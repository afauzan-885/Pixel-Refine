# Marker: GPU_NATIVE_MARKER_V2
"""Box Filter - Taichi GPU"""

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
    def _box_filter_2d_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int, radius: int
    ):
        for y, x in ti.ndrange(h, w):
            sum_val = 0.0
            count = 0.0
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    ny = tm.clamp(y + dy, 0, h - 1)
                    nx = tm.clamp(x + dx, 0, w - 1)
                    sum_val += src[ny, nx]
                    count += 1.0
            dst[y, x] = sum_val / count

    @ti.kernel
    def _box_filter_flow_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int, radius: int
    ):
        for y, x in ti.ndrange(h, w):
            sum_x, sum_y = 0.0, 0.0
            count = 0.0
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    ny = tm.clamp(y + dy, 0, h - 1)
                    nx = tm.clamp(x + dx, 0, w - 1)
                    sum_x += src[ny, nx, 0]
                    sum_y += src[ny, nx, 1]
                    count += 1.0
            dst[y, x, 0] = sum_x / count
            dst[y, x, 1] = sum_y / count


def box_filter_2d(
    src, dst=None, kernel_size: int = 3, buffer_provider="pool", enable_tiling=True
):
    """Supports both NumPy and Taichi ndarrays."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # OOM Guard Trigger
    if enable_tiling and isinstance(src, np.ndarray) and src.size > 2048 * 2048 * 3:
        from . import oom_guard

        return oom_guard.execute_tiled(
            box_filter_2d,
            src,
            overlap=kernel_size * 2,
            dst=dst,
            kernel_size=kernel_size,
            buffer_provider=buffer_provider,
            enable_tiling=False,
        )

    h, w = src.shape[:2]
    radius = kernel_size // 2

    src_gpu, src_is_temp = common.ensure_taichi_field(
        src, dtype=ti.f32, buffer_provider=buffer_provider
    )

    if dst is not None:
        dst_gpu = dst
    else:
        dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

    _box_filter_2d_kernel(src_gpu, dst_gpu, h, w, radius)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(dst_gpu, src_is_temp and dst is None)


def box_filter_flow(
    src, dst=None, kernel_size=3, buffer_provider="pool", enable_tiling=True
):
    """Supports both NumPy and Taichi ndarrays."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # OOM Guard Trigger
    if enable_tiling and isinstance(src, np.ndarray) and src.size > 2048 * 2048 * 3:
        from . import oom_guard

        return oom_guard.execute_tiled(
            box_filter_flow,
            src,
            overlap=kernel_size * 2,
            dst=dst,
            kernel_size=kernel_size,
            buffer_provider=buffer_provider,
            enable_tiling=False,
        )

    h, w = src.shape[:2]
    radius = kernel_size // 2

    src_gpu, src_is_temp = common.ensure_taichi_field(
        src, dtype=ti.f32, buffer_provider=buffer_provider
    )

    if dst is not None:
        dst_gpu = dst
    else:
        dst_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)

    _box_filter_flow_kernel(src_gpu, dst_gpu, h, w, radius)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(dst_gpu, src_is_temp and dst is None)
