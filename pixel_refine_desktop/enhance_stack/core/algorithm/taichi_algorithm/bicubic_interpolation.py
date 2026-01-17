"""Bicubic Interpolation - Taichi GPU"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None

if TAICHI_AVAILABLE:

    @ti.func
    def cubic_hermite(A, B, C, D, t):
        a = -A / 2.0 + (3.0 * B) / 2.0 - (3.0 * C) / 2.0 + D / 2.0
        b = A - (5.0 * B) / 2.0 + 2.0 * C - D / 2.0
        c = -A / 2.0 + C / 2.0
        d = B
        return a * t * t * t + b * t * t + c * t + d

    @ti.kernel
    def _bicubic_resize_kernel(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        for r, c in ti.ndrange(h_dst, w_dst):
            # Bicubic needs careful coordinate mapping typically center-aligned
            y_src = (r + 0.5) * (float(h_src) / float(h_dst)) - 0.5
            x_src = (c + 0.5) * (float(w_src) / float(w_dst)) - 0.5

            x_int = int(ti.floor(x_src))
            y_int = int(ti.floor(y_src))

            dx = x_src - x_int
            dy = y_src - y_int

            # 4x4 Neighborhood
            # Store column results
            col_results = ti.Vector([0.0, 0.0, 0.0, 0.0])

            for m in range(-1, 3):  # y offset
                # Horizontal interpolation

                # Fetch 4 horizontal pixels
                p = ti.Vector([0.0, 0.0, 0.0, 0.0])
                y_idx = tm.clamp(y_int + m, 0, h_src - 1)

                for n in range(-1, 3):  # x offset
                    x_idx = tm.clamp(x_int + n, 0, w_src - 1)
                    p[n + 1] = src[y_idx, x_idx]

                col_results[m + 1] = cubic_hermite(p[0], p[1], p[2], p[3], dx)

            # Vertical interpolation of column results
            val = cubic_hermite(
                col_results[0], col_results[1], col_results[2], col_results[3], dy
            )
            dst[r, c] = val


def bicubic_resize(src: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    h_src, w_src = src.shape[:2]
    src_f32 = np.ascontiguousarray(src, dtype=np.float32)
    dst = np.zeros((target_h, target_w), dtype=np.float32)
    _bicubic_resize_kernel(src_f32, dst, h_src, w_src, target_h, target_w)
    return dst
