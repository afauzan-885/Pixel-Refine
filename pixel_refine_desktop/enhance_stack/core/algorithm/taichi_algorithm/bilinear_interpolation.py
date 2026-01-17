"""Bilinear Interpolation - Taichi GPU"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None

_initialized = False


def _ensure_init():
    global _initialized
    if not _initialized and TAICHI_AVAILABLE:
        try:
            ti.init(arch=ti.gpu, offline_cache=True)
        except:
            ti.init(arch=ti.cpu)
        _initialized = True


if TAICHI_AVAILABLE:

    @ti.kernel
    def _bilinear_resize_kernel(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        for r, c in ti.ndrange(h_dst, w_dst):
            y_src = r * (float(h_src) / float(h_dst))
            x_src = c * (float(w_src) / float(w_dst))

            y0 = int(ti.floor(y_src))
            x0 = int(ti.floor(x_src))
            y1 = ti.min(y0 + 1, h_src - 1)
            x1 = ti.min(x0 + 1, w_src - 1)

            wy = y_src - float(y0)
            wx = x_src - float(x0)

            q00, q01 = src[y0, x0], src[y0, x1]
            q10, q11 = src[y1, x0], src[y1, x1]

            r1 = tm.mix(q00, q01, wx)
            r2 = tm.mix(q10, q11, wx)
            dst[r, c] = tm.mix(r1, r2, wy)


def bilinear_resize(src: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    _ensure_init()
    h_src, w_src = src.shape[:2]
    src_f32 = np.ascontiguousarray(src, dtype=np.float32)
    dst = np.zeros((target_h, target_w), dtype=np.float32)
    _bilinear_resize_kernel(src_f32, dst, h_src, w_src, target_h, target_w)
    return dst


def bilinear_upsample_2x(src: np.ndarray) -> np.ndarray:
    h, w = src.shape[:2]
    return bilinear_resize(src, h * 2, w * 2)


def bilinear_downsample_2x(src: np.ndarray) -> np.ndarray:
    h, w = src.shape[:2]
    return bilinear_resize(src, h // 2, w // 2)
