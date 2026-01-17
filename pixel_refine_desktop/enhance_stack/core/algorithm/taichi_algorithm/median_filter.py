# Marker: GPU_NATIVE_MARKER_V2
"""Median Filter - Taichi GPU"""

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
    def _median_filter_3x3_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int
    ):
        for y, x in ti.ndrange(h, w):
            vals = ti.Vector([0.0] * 9)
            idx = 0
            for dy in ti.static(range(-1, 2)):
                for dx in ti.static(range(-1, 2)):
                    ny = tm.clamp(y + dy, 0, h - 1)
                    nx = tm.clamp(x + dx, 0, w - 1)
                    vals[idx] = src[ny, nx]
                    idx += 1
            for i in ti.static(range(9)):
                for j in ti.static(range(i + 1, 9)):
                    if vals[j] < vals[i]:
                        vals[i], vals[j] = vals[j], vals[i]
            dst[y, x] = vals[4]

    @ti.kernel
    def _median_filter_flow_3x3_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int
    ):
        for y, x in ti.ndrange(h, w):
            vals_x = ti.Vector([0.0] * 9)
            vals_y = ti.Vector([0.0] * 9)
            idx = 0
            for dy in ti.static(range(-1, 2)):
                for dx in ti.static(range(-1, 2)):
                    ny = tm.clamp(y + dy, 0, h - 1)
                    nx = tm.clamp(x + dx, 0, w - 1)
                    vals_x[idx] = src[ny, nx, 0]
                    vals_y[idx] = src[ny, nx, 1]
                    idx += 1
            for i in ti.static(range(9)):
                for j in ti.static(range(i + 1, 9)):
                    if vals_x[j] < vals_x[i]:
                        vals_x[i], vals_x[j] = vals_x[j], vals_x[i]
            for i in ti.static(range(9)):
                for j in ti.static(range(i + 1, 9)):
                    if vals_y[j] < vals_y[i]:
                        vals_y[i], vals_y[j] = vals_y[j], vals_y[i]
            dst[y, x, 0] = vals_x[4]
            dst[y, x, 1] = vals_y[4]


def median_filter(
    src, dst=None, kernel_size: int = 3, buffer_provider="pool", enable_tiling=True
):
    """Supports both NumPy and Taichi ndarrays."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    if kernel_size != 3:
        raise ValueError("Only kernel_size=3 supported")

    # OOM Guard Trigger
    if enable_tiling and isinstance(src, np.ndarray) and src.size > 2048 * 2048 * 3:
        from . import oom_guard

        return oom_guard.execute_tiled(
            median_filter,
            src,
            overlap=kernel_size * 2,
            dst=dst,
            kernel_size=kernel_size,
            buffer_provider=buffer_provider,
            enable_tiling=False,
        )

    h, w = src.shape[:2]

    src_gpu, src_is_temp = common.ensure_taichi_field(
        src, dtype=ti.f32, buffer_provider=buffer_provider
    )

    if dst is not None:
        dst_gpu = dst
    else:
        dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

    _median_filter_3x3_kernel(src_gpu, dst_gpu, h, w)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(dst_gpu, src_is_temp and dst is None)


def median_filter_flow(
    src, dst=None, kernel_size: int = 3, buffer_provider="pool", enable_tiling=True
):
    """Supports both NumPy and Taichi ndarrays."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    if kernel_size != 3:
        raise ValueError("Only kernel_size=3 supported")

    # OOM Guard Trigger
    if enable_tiling and isinstance(src, np.ndarray) and src.size > 2048 * 2048 * 3:
        from . import oom_guard

        return oom_guard.execute_tiled(
            median_filter_flow,
            src,
            overlap=kernel_size * 2,
            dst=dst,
            kernel_size=kernel_size,
            buffer_provider=buffer_provider,
            enable_tiling=False,
        )

    h, w = src.shape[:2]

    src_gpu, src_is_temp = common.ensure_taichi_field(
        src, dtype=ti.f32, buffer_provider=buffer_provider
    )

    if dst is not None:
        dst_gpu = dst
    else:
        dst_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)

    _median_filter_flow_3x3_kernel(src_gpu, dst_gpu, h, w)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(dst_gpu, src_is_temp and dst is None)
