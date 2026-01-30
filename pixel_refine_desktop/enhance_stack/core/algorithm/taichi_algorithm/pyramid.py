"""Image Pyramid - Taichi GPU"""

import numpy as np

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
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        """2x2 Average Pooling downsample (Anti-aliasing)."""
        for r, c in ti.ndrange(h_dst, w_dst):
            y = r * 2
            x = c * 2

            # Simple 2x2 average for stability
            v00 = src[ti.min(y, h_src - 1), ti.min(x, w_src - 1)]
            v01 = src[ti.min(y, h_src - 1), ti.min(x + 1, w_src - 1)]
            v10 = src[ti.min(y + 1, h_src - 1), ti.min(x, w_src - 1)]
            v11 = src[ti.min(y + 1, h_src - 1), ti.min(x + 1, w_src - 1)]

            dst[r, c] = (v00 + v01 + v10 + v11) * 0.25

    @ti.kernel
    def _upsample_flow_kernel(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
        scale_x: float,
        scale_y: float,
    ):
        for r, c in ti.ndrange(h_dst, w_dst):
            u = r * (float(h_src) / float(h_dst))
            v = c * (float(w_src) / float(w_dst))
            y0 = int(ti.floor(u))
            x0 = int(ti.floor(v))
            y0 = tm.clamp(y0, 0, h_src - 1)
            x0 = tm.clamp(x0, 0, w_src - 1)
            y1 = tm.clamp(y0 + 1, 0, h_src - 1)
            x1 = tm.clamp(x0 + 1, 0, w_src - 1)
            wy = u - float(y0)
            wx = v - float(x0)
            f00 = tm.vec2(src[y0, x0, 0], src[y0, x0, 1])
            f01 = tm.vec2(src[y0, x1, 0], src[y0, x1, 1])
            f10 = tm.vec2(src[y1, x0, 0], src[y1, x0, 1])
            f11 = tm.vec2(src[y1, x1, 0], src[y1, x1, 1])
            res = (1.0 - wy) * ((1.0 - wx) * f00 + wx * f01) + wy * (
                (1.0 - wx) * f10 + wx * f11
            )
            dst[r, c, 0] = res[0] * scale_x
            dst[r, c, 1] = res[1] * scale_y


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
    buffer_provider="pool",
) -> list:
    """GPU native interface: Build image pyramid and return list of ti.ndarrays."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    pyramid = [image_gpu]
    for _ in range(n_levels - 1):
        prev = pyramid[-1]
        h_src, w_src = prev.shape
        h_dst, w_dst = h_src // 2, w_src // 2

        if h_dst < min_size or w_dst < min_size:
            break

        dst = common.get_temp_buffer((h_dst, w_dst), ti.f32, buffer_provider)
        _downsample_2x_kernel(prev, dst, h_src, w_src, h_dst, w_dst)
        pyramid.append(dst)

    return pyramid


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
        src_gpu, dst_gpu, h_src, w_src, h_dst, w_dst, float(sx), float(sy)
    )
