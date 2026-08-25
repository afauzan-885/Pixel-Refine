"""
Generic 2D Convolution - Taichi GPU
====================================
OpenCV-compatible 2D filter convolution.
Parity: cv2.filter2D(src, ddepth, kernel)

Usage (JIT):
    from taichi_vision.taichi_algorithm import filter2d
    result = filter2d(src, kernel, border_mode='REFLECT_101')
"""

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
    def _convolve_2d_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        kernel: ti.types.ndarray(dtype=ti.f32, ndim=2),
        k_h: ti.i32,
        k_w: ti.i32,
        h: ti.i32,
        w: ti.i32,
    ):
        """Generic 2D convolution with BORDER_REFLECT_101."""
        half_kh = k_h // 2
        half_kw = k_w // 2
        for y, x in ti.ndrange(h, w):
            acc = 0.0
            for ky in ti.static(range(31)):
                if ky < k_h:
                    for kx in ti.static(range(31)):
                        if kx < k_w:
                            sy = common.reflect_idx(y + ky - half_kh, h)
                            sx = common.reflect_idx(x + kx - half_kw, w)
                            acc += src[sy, sx] * kernel[ky, kx]
            dst[y, x] = acc

    @ti.kernel
    def _convolve_3ch_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        kernel: ti.types.ndarray(dtype=ti.f32, ndim=2),
        k_h: ti.i32,
        k_w: ti.i32,
        h: ti.i32,
        w: ti.i32,
    ):
        """Generic 2D convolution for 3-channel images."""
        half_kh = k_h // 2
        half_kw = k_w // 2
        for y, x, c in ti.ndrange(h, w, src.shape[2]):
            acc = 0.0
            for ky in ti.static(range(31)):
                if ky < k_h:
                    for kx in ti.static(range(31)):
                        if kx < k_w:
                            sy = common.reflect_idx(y + ky - half_kh, h)
                            sx = common.reflect_idx(x + kx - half_kw, w)
                            acc += src[sy, sx, c] * kernel[ky, kx]
            dst[y, x, c] = acc


@ti_thread
def filter2d(src, kernel, border_mode='REFLECT_101'):
    """
    Apply generic 2D convolution filter.
    Parity: cv2.filter2D(src, ddepth=-1, kernel)

    Args:
        src: Input image (H,W) or (H,W,C) float32.
        kernel: 2D convolution kernel (numpy array, float32).
        border_mode: Boundary handling ('REFLECT_101' default, matching OpenCV).

    Returns:
        Filtered image (same shape as src).
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    kernel = np.ascontiguousarray(kernel, dtype=np.float32)
    k_h, k_w = kernel.shape

    # Pad kernel to max 31x31 for static unrolling
    kernel_padded = np.zeros((31, 31), dtype=np.float32)
    kernel_padded[:k_h, :k_w] = kernel

    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32)
    h, w = src_gpu.shape[:2]
    is_3d = len(src_gpu.shape) == 3

    dst_gpu = common.get_temp_buffer(src_gpu.shape, ti.f32)

    kernel_gpu = ti.ndarray(dtype=ti.f32, shape=(31, 31))
    kernel_gpu.from_numpy(kernel_padded)

    if is_3d:
        _convolve_3ch_kernel(src_gpu, dst_gpu, kernel_gpu, k_h, k_w, h, w)
    else:
        _convolve_2d_kernel(src_gpu, dst_gpu, kernel_gpu, k_h, k_w, h, w)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(dst_gpu, not hasattr(src, "to_numpy"))
