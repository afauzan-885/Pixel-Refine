import numpy as np
import taichi as ti
import taichi.math as tm
from .taichi_worker import ti_thread, TAICHI_AVAILABLE

if TAICHI_AVAILABLE:
    # ... (Kernels remain the same but will be executed via @ti_thread)
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
            y_src = (r + 0.5) * (float(h_src) / float(h_dst)) - 0.5
            x_src = (c + 0.5) * (float(w_src) / float(w_dst)) - 0.5

            x_int = int(ti.floor(x_src))
            y_int = int(ti.floor(y_src))

            dx = x_src - x_int
            dy = y_src - y_int

            col_results = ti.Vector([0.0, 0.0, 0.0, 0.0])
            for m in range(-1, 3):
                p = ti.Vector([0.0, 0.0, 0.0, 0.0])
                y_idx = tm.clamp(y_int + m, 0, h_src - 1)
                for n in range(-1, 3):
                    x_idx = tm.clamp(x_int + n, 0, w_src - 1)
                    p[n + 1] = src[y_idx, x_idx]
                col_results[m + 1] = cubic_hermite(p[0], p[1], p[2], p[3], dx)

            val = cubic_hermite(
                col_results[0], col_results[1], col_results[2], col_results[3], dy
            )
            dst[r, c] = val


def bicubic_resize(src, target_h: int, target_w: int, dst=None):
    """
    Smart bicubic resize API that auto-detects input type and returns appropriate output.
    All Taichi operations are synchronized via @ti_thread.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Detect input type
    is_taichi_input = hasattr(src, "to_numpy")

    @ti_thread
    def _run_gpu_bicubic_resize(src_data, h_dst, w_dst, dst_data=None):
        h_src, w_src = src_data.shape[:2]

        # Determine output buffer
        if dst_data is None:
            if is_taichi_input:
                dst_data = ti.ndarray(dtype=ti.f32, shape=(h_dst, w_dst))
            else:
                dst_data = np.zeros((h_dst, w_dst), dtype=np.float32)

        # Ensure contiguous if NumPy
        data_to_pass = src_data
        if not is_taichi_input:
            data_to_pass = np.ascontiguousarray(src_data, dtype=np.float32)

        _bicubic_resize_kernel(data_to_pass, dst_data, h_src, w_src, h_dst, w_dst)
        return dst_data

    return _run_gpu_bicubic_resize(src, target_h, target_w, dst)


# Legacy alias
def bicubic_resize_gpu(src_gpu, target_h: int, target_w: int, dst_gpu=None):
    return bicubic_resize(src_gpu, target_h, target_w, dst_gpu)
