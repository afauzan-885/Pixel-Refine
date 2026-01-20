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
        use_sharpen: int,
        gamma_pow: float,
        slope: float,
        cutoff: float,
    ):
        """
        Fused Kernel: Normalize -> Gamma -> Resize (Bilinear) -> Gray -> Sharpen
        Matches OpenCV mapping: (i + 0.5) * scale - 0.5
        """
        # Grid Stride Loop over Destination
        for i, j in ti.ndrange(dst_h, dst_w):
            # 1. Coordinate Mapping (Dst -> Src) - Centered Mapping
            # Avoids precision issues with integers (i * scale)
            u = (float(i) + 0.5) * (float(src_h) / float(dst_h)) - 0.5
            v = (float(j) + 0.5) * (float(src_w) / float(dst_w)) - 0.5

            # Epsilon to handle extreme edges
            u = tm.clamp(u, 0.0, float(src_h - 1))
            v = tm.clamp(v, 0.0, float(src_w - 1))

            y0 = int(ti.floor(u))
            x0 = int(ti.floor(v))
            y1 = tm.clamp(y0 + 1, 0, src_h - 1)
            x1 = tm.clamp(x0 + 1, 0, src_w - 1)

            wy = u - float(y0)
            wx = v - float(x0)

            # 2. Fetch & Interpolate on Raw Data
            pixel_00 = tm.vec3(src[y0, x0, 0], src[y0, x0, 1], src[y0, x0, 2])
            pixel_01 = tm.vec3(src[y0, x1, 0], src[y0, x1, 1], src[y0, x1, 2])
            pixel_10 = tm.vec3(src[y1, x0, 0], src[y1, x0, 1], src[y1, x0, 2])
            pixel_11 = tm.vec3(src[y1, x1, 0], src[y1, x1, 1], src[y1, x1, 2])

            val_interp = (
                pixel_00 * (1.0 - wx) * (1.0 - wy)
                + pixel_01 * wx * (1.0 - wy)
                + pixel_10 * (1.0 - wx) * wy
                + pixel_11 * wx * wy
            )

            # 3. Normalize & Apply Gamma/Scale
            val_norm = val_interp
            if input_bits > 0:
                MAX_VAL = float((1 << input_bits) - 1)
                val_norm = val_interp / MAX_VAL

            # Exposure Scale
            res_rgb = val_norm * scale_factor

            if apply_gamma:
                # 100% Consistent with to_gamma_proxy: Clip BEFORE Gamma
                for c in ti.static(range(3)):
                    v_val = tm.clamp(res_rgb[c], 0.0, 1.0)
                    if v_val < cutoff:
                        res_rgb[c] = v_val * slope
                    else:
                        res_rgb[c] = 1.099 * tm.pow(v_val, 1.0 / gamma_pow) - 0.099

            # 4. Grayscale (Green Channel Priority for Alignment)
            gray = res_rgb[1]  # Green only

            # 5. Logika Penajaman & Kontras (Consistent with preprocess_in_python)
            if use_sharpen:
                # 30% contrast reduction: (pixel - 0.5) * 0.7 + 0.5
                gray = (gray - 0.5) * 0.7 + 0.5

            dst_gray[i, j] = tm.clamp(gray, 0.0, 1.0)


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
    use_sharpen=False,
):
    """
    End-to-end GPU preprocessing with Fusion.
    Supported steps: Normalization, Gamma-Proxy, Bilinear Resize, Green Extraction, Sharpening.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h, w = image.shape[:2]

    # Default Target
    th = target_h if target_h is not None else h
    tw = target_w if target_w is not None else w

    # OOM Guard Trigger (Adaptive)
    from . import oom_guard

    if enable_tiling and isinstance(image, np.ndarray) and oom_guard.should_tile(image):
        return oom_guard.execute_tiled(
            preprocess_gpu,
            image,
            overlap=32,
            scale=scale,
            apply_gamma=apply_gamma,
            target_h=target_h,
            target_w=target_w,
            input_bits=input_bits,
            buffer_provider=buffer_provider,
            enable_tiling=False,  # PREVENT RECURSION
            gamma_pow=gamma_pow,
            slope=slope,
            cutoff=cutoff,
            use_sharpen=use_sharpen,
        )

    # Upload/Ensure field
    src_gpu, src_is_temp = common.ensure_taichi_field(
        image, dtype=ti.f32, buffer_provider=buffer_provider
    )

    # Destination Buffer
    gray_gpu = common.get_temp_buffer((th, tw), ti.f32, buffer_provider)

    # Run Fused Kernel
    _fused_preprocess_kernel(
        src_gpu,
        gray_gpu,
        h,
        w,
        th,
        tw,
        scale,
        int(apply_gamma),
        input_bits,
        int(use_sharpen),
        float(gamma_pow),
        float(slope),
        float(cutoff),
    )

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return gray_gpu
