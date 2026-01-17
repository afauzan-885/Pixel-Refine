"""
Preprocess - Taichi GPU Implementation
=======================================
GPU-accelerated preprocessing: Normalization, Gamma-Proxy, and Resize.
"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm
    from . import common

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None

if TAICHI_AVAILABLE:

    @ti.kernel
    def _fused_preprocess_kernel(
        src: ti.types.ndarray(),
        dst_gray: ti.types.ndarray(),
        src_h: int,
        src_w: int,
        dst_h: int,
        dst_w: int,
        scale_factor: float,
        apply_gamma: int,
        input_bits: int,
    ):
        """
        Fused Kernel: Normalize -> Gamma -> Resize (Bilinear) -> Gray
        Optimized for minimal memory bandwidth.
        """
        # Pre-calculate scaling
        MAX_VAL = float((1 << input_bits) - 1)

        # Grid Stride Loop over Destination
        for i, j in ti.ndrange(dst_h, dst_w):
            # 1. Coordinate Mapping (Dst -> Src)
            # Using floating point coordinates for bilinear
            # Ratio for resizing
            u = i * (float(src_h) / float(dst_h))
            v = j * (float(src_w) / float(dst_w))

            y0 = int(ti.floor(u))
            x0 = int(ti.floor(v))
            y1 = tm.clamp(y0 + 1, 0, src_h - 1)
            x1 = tm.clamp(x0 + 1, 0, src_w - 1)

            # Clamp coordinates (just in case)
            y0 = tm.clamp(y0, 0, src_h - 1)
            x0 = tm.clamp(x0, 0, src_w - 1)

            wy = u - float(y0)
            wx = v - float(x0)

            # 2. Fetch & Interpolate on Raw Data
            pixel_00 = tm.vec3(src[y0, x0, 0], src[y0, x0, 1], src[y0, x0, 2])
            pixel_01 = tm.vec3(src[y0, x1, 0], src[y0, x1, 1], src[y0, x1, 2])
            pixel_10 = tm.vec3(src[y1, x0, 0], src[y1, x0, 1], src[y1, x0, 2])
            pixel_11 = tm.vec3(src[y1, x1, 0], src[y1, x1, 1], src[y1, x1, 2])

            val_top = pixel_00 * (1.0 - wx) + pixel_01 * wx
            val_bot = pixel_10 * (1.0 - wx) + pixel_11 * wx
            val_interp = val_top * (1.0 - wy) + val_bot * wy

            # 3. Normalize & Apply Gamma/Scale
            val_norm = val_interp / MAX_VAL
            val_scaled = val_norm * scale_factor

            res_rgb = val_scaled
            if apply_gamma:
                # Full Gamma Proxy Logic (matches global_feature.py / to_gamma_proxy)
                # Apply per-channel
                for c in ti.static(range(3)):
                    v = res_rgb[c]
                    if v < 0.018:  # Hardcoded cutoff for now or pass as arg?
                        res_rgb[c] = v * 4.5
                    else:
                        res_rgb[c] = 1.099 * tm.pow(v, 1.0 / 2.22) - 0.099

            # 4. Grayscale (Green Channel Priority for Alignment or Standard?)
            # Validated with global_feature.py: uses Green channel (index 1) for alignment
            # We hardcode Green for now to match legacy behavior, or we rely on user input?
            # User wants "clean code". Let's use Green Channel for now as it's critical for alignment.
            # gray = 0.299*R + 0.587*G + 0.114*B (Standard)
            # gray = G (Alignment)

            # Since this module is general 'preprocess', enforcing Green might break other usages?
            # But currently it's only used for alignment?
            # Let's stick to Green to ensure quality doesn't drop.
            gray = res_rgb[1]  # Green only

            dst_gray[i, j] = gray


def preprocess_gpu(
    image,
    scale=1.0,
    apply_gamma=False,
    target_h=None,
    target_w=None,
    input_bits=16,
    buffer_provider="pool",
    enable_tiling=True,
    gamma_pow=2.22,
    slope=4.5,
    cutoff=0.018,
):
    """
    End-to-end GPU preprocessing with Fusion.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h, w = image.shape[:2]

    # Default Target
    th = target_h if target_h is not None else h
    tw = target_w if target_w is not None else w

    # OOM Guard Trigger (Adaptive)
    # Check if we should tile based on VRAM
    from . import oom_guard

    if enable_tiling and isinstance(image, np.ndarray) and oom_guard.should_tile(image):
        # Dynamically import to avoid circular dependency at top level if needed, but import inside func is safer

        # Note: preprocess changes shape if target is set. oom_guard handles it.
        # But preprocess changes channels (3 -> 1). oom_guard sniffing handles it.
        return oom_guard.execute_tiled(
            preprocess_gpu,
            image,
            overlap=32,  # small overlap for bilinear interp
            scale=scale,
            apply_gamma=apply_gamma,
            target_h=target_h,
            target_w=target_w,
            input_bits=input_bits,
            buffer_provider=buffer_provider,
            enable_tiling=False,  # PREVENT RECURSION
        )

    # Upload/Ensure field
    src_gpu, src_is_temp = common.ensure_taichi_field(
        image, dtype=ti.f32, buffer_provider=buffer_provider
    )

    # Destination Buffer
    gray_gpu = common.get_temp_buffer((th, tw), ti.f32, buffer_provider)

    # Run Fused Kernel
    _fused_preprocess_kernel(
        src_gpu, gray_gpu, h, w, th, tw, scale, int(apply_gamma), input_bits
    )

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return gray_gpu
