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
    from ..taichi_worker import ti_thread
except ImportError:
    pass

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
            y_src = (r + 0.5) * (float(h_src) / float(h_dst))
            x_src = (c + 0.5) * (float(w_src) / float(w_dst))

            y = int(ti.floor(y_src))
            x = int(ti.floor(x_src))

            y = tm.clamp(y, 0, h_src - 1)
            x = tm.clamp(x, 0, w_src - 1)

            dst[r, c] = src[y, x]


def nearest_resize(src, target_h: int, target_w: int, dst=None):
    """
    Smart nearest resize API that auto-detects input type and returns appropriate output.
    All Taichi operations are synchronized via @ti_thread.
    """
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.resize(src, (target_w, target_h), interpolation=taichi_aot.INTER_NEAREST, return_gpu=hasattr(src, "to_numpy"), dst=dst)

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Detect input type
    is_taichi_input = hasattr(src, "to_numpy")

    @ti_thread
    def _run_gpu_nearest_resize(src_data, h_dst, w_dst, dst_data=None):
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

        _nearest_resize_kernel(data_to_pass, dst_data, h_src, w_src, h_dst, w_dst)
        return dst_data

    return _run_gpu_nearest_resize(src, target_h, target_w, dst)


# Legacy alias
def nearest_resize_gpu(src_gpu, target_h: int, target_w: int, dst_gpu=None):
    return nearest_resize(src_gpu, target_h, target_w, dst_gpu)
