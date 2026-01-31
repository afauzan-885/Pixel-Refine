# Marker: GPU_NATIVE_MARKER_V2
"""Box Filter - Taichi GPU"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm
    from . import common
    from .taichi_worker import ti_thread

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
    def _box_filter_3d_kernel(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h: int,
        w: int,
        radius: int,
        c: int,
    ):
        for y, x, ch in ti.ndrange(h, w, c):
            sum_val = 0.0
            count = 0.0
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    ny = tm.clamp(y + dy, 0, h - 1)
                    nx = tm.clamp(x + dx, 0, w - 1)
                    sum_val += src[ny, nx, ch]
                    count += 1.0
            dst[y, x, ch] = sum_val / count

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


@ti_thread
def box_filter(
    src, dst=None, kernel_size: int = 3, buffer_provider="pool", enable_tiling=True
):
    """
    Box filter (mean blur) with full GPU pipeline support.

    **Full GPU Pipeline Support:**
    - If input is Taichi field → stays on GPU, returns Taichi field
    - If input is NumPy array → uploads to GPU, processes, downloads to NumPy

    Args:
        src: Input image (NumPy array or Taichi field)
        dst: Optional pre-allocated output buffer
        kernel_size: Filter kernel size (e.g., 3, 5, 7)
        buffer_provider: Buffer management strategy
        enable_tiling: Enable tiling for large images (OOM protection)

    Returns:
        Filtered image (same type as input unless dst is provided)

    Example:
        >>> # NumPy workflow
        >>> img_np = np.random.rand(512, 512).astype(np.float32)
        >>> blurred_np = box_filter(img_np, kernel_size=5)

        >>> # GPU workflow (ZERO COPY!)
        >>> img_gpu = ti.ndarray(dtype=ti.f32, shape=(512, 512))
        >>> blurred_gpu = box_filter(img_gpu, kernel_size=5)  # Stays on GPU!
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Detect input type for GPU pipeline
    is_taichi_input = hasattr(src, "to_numpy")

    # OOM Guard Trigger
    if enable_tiling and isinstance(src, np.ndarray) and src.size > 2048 * 2048 * 3:
        from . import oom_guard

        return oom_guard.execute_tiled(
            box_filter,
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

    is_3d = len(src_gpu.shape) == 3
    c_count = src_gpu.shape[2] if is_3d else 1
    shape_out = (h, w, c_count) if is_3d else (h, w)

    if dst is not None:
        dst_gpu, _ = common.ensure_taichi_field(dst, dtype=ti.f32)
    else:
        dst_gpu = common.get_temp_buffer(shape_out, ti.f32, buffer_provider)

    if is_3d:
        # We need a 3ch kernel for box filter too if we want native GPU.
        # For now, if 3D, we can use the generic wrapper or add a kernel.
        # Let's add a fast 3D kernel to box_filter.py to avoid loops.
        _box_filter_3d_kernel(src_gpu, dst_gpu, h, w, radius, c_count)
    else:
        _box_filter_2d_kernel(src_gpu, dst_gpu, h, w, radius)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    # Return appropriate type
    if not is_taichi_input:
        res = dst_gpu.to_numpy()
        common.release_temp_buffer(dst_gpu)
        if dst is not None:
            dst[:] = res
            return dst
        return res

    return dst_gpu


# Legacy alias for backward compatibility
def box_filter_2d(
    src, dst=None, kernel_size: int = 3, buffer_provider="pool", enable_tiling=True
):
    """
    DEPRECATED: Use box_filter() instead.
    This function is kept for backward compatibility only.
    """
    return box_filter(src, dst, kernel_size, buffer_provider, enable_tiling)


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
