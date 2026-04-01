"""Image Pyramid - Taichi GPU"""

import numpy as np
import os

try:
    import taichi as ti
    import taichi.math as tm
    from . import common
    from .taichi_worker import ti_thread, TAICHI_AVAILABLE

except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None
    ti_thread = lambda f: f  # No-op in case of no Taichi

MIN_PYRAMID_SIZE = 32

if TAICHI_AVAILABLE:

    @ti.kernel
    def _downsample_2x_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
    ):
        """Standard 2x downsampling (box filter). AOT-compatible."""
        h_src, w_src = src.shape[0], src.shape[1]
        h_dst, w_dst = dst.shape[0], dst.shape[1]
        # Gaussian weights [1, 4, 6, 4, 1] / 16
        weights = ti.static([1.0, 4.0, 6.0, 4.0, 1.0])
        total_weight = 256.0  # (1+4+6+4+1)^2

        for r, c in ti.ndrange(h_dst, w_dst):
            y_src = r * 2
            x_src = c * 2

            val = 0.0
            for j in ti.static(range(-2, 3)):
                for i in ti.static(range(-2, 3)):
                    sy = tm.clamp(y_src + j, 0, h_src - 1)
                    sx = tm.clamp(x_src + i, 0, w_src - 1)
                    val += src[sy, sx] * weights[j + 2] * weights[i + 2]

            dst[r, c] = val / total_weight

    @ti.kernel
    def _upsample_flow_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        scale: float,
    ):
        """Bicubic upsampling for flow fields. AOT-compatible."""
        h_src, w_src = src.shape[0], src.shape[1]
        h_dst, w_dst = dst.shape[0], dst.shape[1]
        for r, c in ti.ndrange(h_dst, w_dst):
            # Coordinates in source domain
            v = float(c) * (float(w_src) / float(w_dst))
            u = float(r) * (float(h_src) / float(h_dst))

            # Sample each channel using bicubic interpolation from common.py
            val0 = common.bicubic_at_channel(src, v, u, h_src, w_src, 0)
            val1 = common.bicubic_at_channel(src, v, u, h_src, w_src, 1)

            dst[r, c, 0] = val0 * scale
            dst[r, c, 1] = val1 * scale





@ti_thread
def build_image_pyramid(
    image: np.ndarray, n_levels: int = 4, min_size: int = MIN_PYRAMID_SIZE
) -> list:
    """CPU interface: Build image pyramid and return list of NumPy arrays."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Upload once using common
    image_gpu, _ = common.ensure_taichi_field(image, dtype=ti.f32)

    # Build on GPU
    pyramid_gpu = build_image_pyramid_gpu(image_gpu, n_levels, min_size)

    # Download all (for backward compatibility)
    return [level.to_numpy() for level in pyramid_gpu]


@ti_thread
def build_image_pyramid_gpu(
    image_gpu,
    n_levels: int = 4,
    min_size: int = MIN_PYRAMID_SIZE,
    downscale_factor: float = 2.0,
    buffer_provider="pool",
) -> list:
    """
    GPU native interface: Build image pyramid with dynamic downsampling.

    Args:
        image_gpu: Source image ti.ndarray.
        n_levels: Total number of levels (including full res).
        min_size: Minimum width or height to stop downsampling.
        downscale_factor: Scale factor between levels (e.g., 2, 4, 1.5).
            - Powers of 2: Uses high-quality cascaded 5x5 Gaussian downsampling.
            - Others: Uses Bilinear interpolation.
        buffer_provider: "pool" or "new".
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    pyramid = [image_gpu]

    # Check if downscale_factor is a power of 2
    is_power_of_2 = False
    steps_per_level = 0
    if downscale_factor > 0:
        log2_val = np.log2(downscale_factor)
        if np.isclose(log2_val, np.round(log2_val)):
            is_power_of_2 = True
            steps_per_level = int(np.round(log2_val))

    for _ in range(n_levels - 1):
        prev = pyramid[-1]
        h_src_prev, w_src_prev = prev.shape

        # Calculate target size
        h_dst_curr = int(np.round(h_src_prev / downscale_factor))
        w_dst_curr = int(np.round(w_src_prev / downscale_factor))

        if h_dst_curr < min_size or w_dst_curr < min_size:
            break

        if is_power_of_2 and steps_per_level > 0:
            # High-quality Gaussian cascaded downsampling
            current_lvl_input = prev
            h_s_curr, w_s_curr = h_src_prev, w_src_prev
            for step in range(steps_per_level):
                h_d_step, w_d_step = h_s_curr // 2, w_s_curr // 2

                # Should not reach here if h_dst/w_dst check above is correct,
                # but adding safety for internal steps
                if h_d_step < 1 or w_d_step < 1:
                    break

                dst = common.get_temp_buffer(
                    (h_d_step, w_d_step), ti.f32, buffer_provider
                )
<<<<<<< HEAD
                _downsample_2x_kernel(
                    current_lvl_input, dst, h_s_curr, w_s_curr, h_d_step, w_d_step
=======
                _AotKernelProvider.get("_downsample_2x_kernel", _downsample_2x_kernel)(
                    current_lvl_input, dst
>>>>>>> f0a7eaf58c12ba5408d95e3002d92aff14af32a4
                )

                if step < steps_per_level - 1:
                    if current_lvl_input is not prev:
                        common.release_temp_buffer(current_lvl_input)
                    current_lvl_input = dst
                    h_s_curr, w_s_curr = h_d_step, w_d_step
                else:
                    pyramid.append(dst)
                    if current_lvl_input is not prev:
                        common.release_temp_buffer(current_lvl_input)
        else:
            # Fallback to Bilinear Resize for arbitrary scales
            from .bilinear_interpolation import bilinear_resize

            dst = bilinear_resize(
                prev, h_dst_curr, w_dst_curr, buffer_provider=buffer_provider
            )
            pyramid.append(dst)

    return pyramid


@ti_thread
def build_image_pyramid_gpu_4x(
    image_gpu,
    n_levels: int = 4,
    min_size: int = MIN_PYRAMID_SIZE,
    buffer_provider="pool",
) -> list:
    """
    Backward compatibility wrapper for 4x downsampling pyramid.
    """
    return build_image_pyramid_gpu(
        image_gpu,
        n_levels,
        min_size,
        downscale_factor=4,
        buffer_provider=buffer_provider,
    )


@ti_thread
def upsample_flow(
    flow: np.ndarray,
    target_h: int,
    target_w: int,
    scale: float = 2.0,
    buffer_provider="pool",
) -> np.ndarray:
    """CPU interface: Upsample flow using NumPy input/output."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    src_gpu, src_is_temp = common.ensure_taichi_field(
        flow, dtype=ti.f32, buffer_provider=buffer_provider
    )
    dst_gpu = common.get_temp_buffer((target_h, target_w, 2), ti.f32, buffer_provider)
    upsample_flow_gpu(src_gpu, dst_gpu, scale)

    res = dst_gpu.to_numpy()

    if src_is_temp:
        common.release_temp_buffer(src_gpu)
    common.release_temp_buffer(dst_gpu)

    return res


@ti_thread
def upsample_flow_gpu(
    src_gpu,
    dst_gpu,
    scale: float | tuple[float, float] = 2.0,
):
    """GPU native interface: Upsample flow from one ti.ndarray to another."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h_src, w_src = src_gpu.shape[:2]
    h_dst, w_dst = dst_gpu.shape[:2]

    if isinstance(scale, (tuple, list)):
        sx, sy = scale
    else:
        sx, sy = scale, scale

    _upsample_flow_kernel(
        src_gpu, dst_gpu,
        float(sx),
    )
