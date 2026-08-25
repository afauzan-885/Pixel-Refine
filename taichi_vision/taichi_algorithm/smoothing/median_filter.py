# Marker: GPU_NATIVE_MARKER_V2
"""Median Filter - Taichi GPU"""

import numpy as np

import os
import importlib

TAICHI_AVAILABLE = False
ti = None
tm = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        tm = importlib.import_module("taichi.math")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from .. import common
    from ..taichi_worker import ti_thread
except ImportError:
    pass

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
            for i in range(9):
                for j in range(i + 1, 9):
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
                    vals_x[idx] = src[ny, nx][0]
                    vals_y[idx] = src[ny, nx][1]
                    idx += 1
            for i in range(9):
                for j in range(i + 1, 9):
                    if vals_x[j] < vals_x[i]:
                        vals_x[i], vals_x[j] = vals_x[j], vals_x[i]
            for i in range(9):
                for j in range(i + 1, 9):
                    if vals_y[j] < vals_y[i]:
                        vals_y[i], vals_y[j] = vals_y[j], vals_y[i]
            dst[y, x][0] = vals_x[4]
            dst[y, x][1] = vals_y[4]

    @ti.kernel
    def _median_filter_rgb_3x3_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int
    ):

        for y, x in ti.ndrange(h, w):
            for c in ti.static(range(3)):
                vals = ti.Vector([0.0] * 9)
                idx = 0
                for dy in ti.static(range(-1, 2)):
                    for dx in ti.static(range(-1, 2)):
                        ny = tm.clamp(y + dy, 0, h - 1)
                        nx = tm.clamp(x + dx, 0, w - 1)
                        vals[idx] = src[ny, nx, c]
                        idx += 1
                # Simple selection sort
                for i in range(9):
                    for j in range(i + 1, 9):
                        if vals[j] < vals[i]:
                            vals[i], vals[j] = vals[j], vals[i]
                dst[y, x, c] = vals[4]

    @ti.kernel
    def _confidence_weighted_median_flow_kernel(
        src: ti.types.ndarray(),
        conf: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """
        Specialized Median Filter that prioritizes high-confidence neighbors.
        Helps propagate flow from textured areas into flat/ambiguous areas.
        """
        for y, x in ti.ndrange(h, w):
            # We use a 5x5 window for better propagation in flat areas
            # For each pixel, we collect neighbors and their confidence
            vals_x = ti.Vector([0.0] * 25)
            vals_y = ti.Vector([0.0] * 25)
            weights = ti.Vector([0.0] * 25)

            idx = 0
            for dy in ti.static(range(-2, 3)):
                for dx in ti.static(range(-2, 3)):
                    ny, nx = tm.clamp(y + dy, 0, h - 1), tm.clamp(x + dx, 0, w - 1)
                    vals_x[idx] = src[ny, nx][0]
                    vals_y[idx] = src[ny, nx][1]
                    weights[idx] = conf[ny, nx]
                    idx += 1

            # Sort by confidence to find the most 'trusted' neighbors
            # (Simple bubble sort for the small window)
            for i in ti.static(range(25)):
                for j in ti.static(range(i + 1, 25)):
                    if weights[j] > weights[i]:
                        weights[i], weights[j] = weights[j], weights[i]
                        vals_x[i], vals_x[j] = vals_x[j], vals_x[i]
                        vals_y[i], vals_y[j] = vals_y[j], vals_y[i]

            # Result is the median of the top 13 most confident neighbors
            # This ensures we ignore noisy outliers in low-confidence areas
            sum_x = 0.0
            sum_y = 0.0
            for i in ti.static(range(13)):
                sum_x += vals_x[i]
                sum_y += vals_y[i]

            dst[y, x][0] = sum_x / 13.0
            dst[y, x][1] = sum_y / 13.0


@ti_thread
def median_filter(
    src, dst=None, kernel_size: int = 3, buffer_provider="pool", enable_tiling=True
):
    """Supports both NumPy and Taichi ndarrays."""
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.median_filter(src, return_gpu=hasattr(src, "to_numpy"))

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    if kernel_size != 3:
        raise ValueError("Only kernel_size=3 supported")

    # OOM Guard Trigger
    if enable_tiling and isinstance(src, np.ndarray) and src.size > 2048 * 2048 * 3:
        from .. import oom_guard

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


@ti_thread
def median_filter_flow(
    src, dst=None, kernel_size: int = 3, buffer_provider="pool", enable_tiling=True
):
    """Supports both NumPy and Taichi ndarrays."""
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.median_filter(src, return_gpu=hasattr(src, "to_numpy"))

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    if kernel_size != 3:
        raise ValueError("Only kernel_size=3 supported")

    # OOM Guard Trigger
    if enable_tiling and isinstance(src, np.ndarray) and src.size > 2048 * 2048 * 3:
        from .. import oom_guard

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


@ti_thread
def confidence_weighted_median_filter_flow(
    src, confidence, dst=None, buffer_provider="pool"
):
    """
    Apply confidence-weighted regularization to the flow field.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h, w = src.shape[:2]
    src_gpu, src_is_temp = common.ensure_taichi_field(
        src, dtype=ti.f32, buffer_provider=buffer_provider
    )
    conf_gpu, conf_is_temp = common.ensure_taichi_field(
        confidence, dtype=ti.f32, buffer_provider=buffer_provider
    )

    if dst is not None:
        dst_gpu = dst
    else:
        dst_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)

    _confidence_weighted_median_flow_kernel(src_gpu, conf_gpu, dst_gpu, h, w)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)
    if conf_is_temp:
        common.release_temp_buffer(conf_gpu)

    return common.to_numpy_if_needed(dst_gpu, src_is_temp and dst is None)
