"""Nearest Interpolation - Taichi GPU"""

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
    def _nearest_resize_kernel(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        for r, c in ti.ndrange(h_dst, w_dst):
            # Nearest neighbor logic: center of pixel projection
            y_src = (r + 0.5) * (float(h_src) / float(h_dst))
            x_src = (c + 0.5) * (float(w_src) / float(w_dst))

            y = int(ti.floor(y_src))
            x = int(ti.floor(x_src))

            y = tm.clamp(y, 0, h_src - 1)
            x = tm.clamp(x, 0, w_src - 1)

            dst[r, c] = src[y, x]


def nearest_resize(src: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    _ensure_init()
    h_src, w_src = src.shape[:2]
    src_f32 = np.ascontiguousarray(src, dtype=np.float32)
    dst = np.zeros((target_h, target_w), dtype=np.float32)
    _nearest_resize_kernel(src_f32, dst, h_src, w_src, target_h, target_w)
    return dst
