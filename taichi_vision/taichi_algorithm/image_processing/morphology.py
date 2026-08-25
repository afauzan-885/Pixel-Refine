"""
Morphological Operations - Taichi GPU
======================================
Dilate and Erode operations with configurable structuring elements.
Equivalent to cv2.dilate() and cv2.erode().

Usage (JIT):
    from taichi_vision.taichi_algorithm import dilate, erode
    result = dilate(src, kernel=None, iterations=1)
    result = erode(src, kernel=None, iterations=1)
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
    def _dilate_2d_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        kh: ti.types.ndarray(dtype=ti.i32, ndim=1),
        kw: ti.types.ndarray(dtype=ti.i32, ndim=1),
        kernel_data: ti.types.ndarray(dtype=ti.i32, ndim=2),
        kh_size: ti.i32,
        kw_size: ti.i32,
        h: ti.i32,
        w: ti.i32,
    ):
        """Dilate (max filter) with arbitrary structuring element. 2D grayscale."""
        for y, x in ti.ndrange(h, w):
            max_val = -1e30
            for ky in ti.static(range(21)):
                if ky < kh_size:
                    for kx in ti.static(range(21)):
                        if kx < kw_size:
                            if kernel_data[ky, kx] != 0:
                                sy = common.reflect_idx(y + kh[ky], h)
                                sx = common.reflect_idx(x + kw[kx], w)
                                val = src[sy, sx]
                                if val > max_val:
                                    max_val = val
            dst[y, x] = max_val

    @ti.kernel
    def _erode_2d_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        kh: ti.types.ndarray(dtype=ti.i32, ndim=1),
        kw: ti.types.ndarray(dtype=ti.i32, ndim=1),
        kernel_data: ti.types.ndarray(dtype=ti.i32, ndim=2),
        kh_size: ti.i32,
        kw_size: ti.i32,
        h: ti.i32,
        w: ti.i32,
    ):
        """Erode (min filter) with arbitrary structuring element. 2D grayscale."""
        for y, x in ti.ndrange(h, w):
            min_val = 1e30
            for ky in ti.static(range(21)):
                if ky < kh_size:
                    for kx in ti.static(range(21)):
                        if kx < kw_size:
                            if kernel_data[ky, kx] != 0:
                                sy = common.reflect_idx(y + kh[ky], h)
                                sx = common.reflect_idx(x + kw[kx], w)
                                val = src[sy, sx]
                                if val < min_val:
                                    min_val = val
            dst[y, x] = min_val

    @ti.kernel
    def _dilate_3d_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        kh: ti.types.ndarray(dtype=ti.i32, ndim=1),
        kw: ti.types.ndarray(dtype=ti.i32, ndim=1),
        kernel_data: ti.types.ndarray(dtype=ti.i32, ndim=2),
        kh_size: ti.i32,
        kw_size: ti.i32,
        h: ti.i32,
        w: ti.i32,
    ):
        """Dilate (max filter) with arbitrary structuring element. 3D (H,W,C)."""
        for y, x, c in ti.ndrange(h, w, src.shape[2]):
            max_val = -1e30
            for ky in ti.static(range(21)):
                if ky < kh_size:
                    for kx in ti.static(range(21)):
                        if kx < kw_size:
                            if kernel_data[ky, kx] != 0:
                                sy = common.reflect_idx(y + kh[ky], h)
                                sx = common.reflect_idx(x + kw[kx], w)
                                val = src[sy, sx, c]
                                if val > max_val:
                                    max_val = val
            dst[y, x, c] = max_val

    @ti.kernel
    def _erode_3d_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        kh: ti.types.ndarray(dtype=ti.i32, ndim=1),
        kw: ti.types.ndarray(dtype=ti.i32, ndim=1),
        kernel_data: ti.types.ndarray(dtype=ti.i32, ndim=2),
        kh_size: ti.i32,
        kw_size: ti.i32,
        h: ti.i32,
        w: ti.i32,
    ):
        """Erode (min filter) with arbitrary structuring element. 3D (H,W,C)."""
        for y, x, c in ti.ndrange(h, w, src.shape[2]):
            min_val = 1e30
            for ky in ti.static(range(21)):
                if ky < kh_size:
                    for kx in ti.static(range(21)):
                        if kx < kw_size:
                            if kernel_data[ky, kx] != 0:
                                sy = common.reflect_idx(y + kh[ky], h)
                                sx = common.reflect_idx(x + kw[kx], w)
                                val = src[sy, sx, c]
                                if val < min_val:
                                    min_val = val
            dst[y, x, c] = min_val


def _prepare_kernel(kernel, ksize):
    """Convert kernel to offset arrays and kernel data for GPU upload."""
    if kernel is None:
        ks = ksize if ksize % 2 == 1 else ksize + 1
        kernel = np.ones((ks, ks), dtype=np.int32)
    else:
        kernel = np.asarray(kernel, dtype=np.int32)
        if kernel.ndim == 1:
            ks = int(np.sqrt(kernel.size))
            kernel = kernel.reshape(ks, ks)

    kh_size, kw_size = kernel.shape
    kh_np = np.arange(-(kh_size // 2), kh_size // 2 + 1, dtype=np.int32)
    kw_np = np.arange(-(kw_size // 2), kw_size // 2 + 1, dtype=np.int32)

    # Pad kernel_data to max 21x21
    kernel_padded = np.zeros((21, 21), dtype=np.int32)
    kh_padded = np.zeros(21, dtype=np.int32)
    kw_padded = np.zeros(21, dtype=np.int32)

    kernel_padded[:kh_size, :kw_size] = kernel
    kh_padded[:kh_size] = kh_np
    kw_padded[:kw_size] = kw_np

    return kernel_padded, kh_padded, kw_padded, kh_size, kw_size


@ti_thread
def dilate(src, kernel=None, ksize=3, iterations=1):
    """
    Dilate image (max filter) with structuring element.
    Equivalent to cv2.dilate(src, kernel, iterations=iterations).

    Args:
        src: Input image (H,W) or (H,W,C) float32.
        kernel: Structuring element (numpy array). None = rectangular ksize x ksize.
        ksize: Kernel size if kernel is None (default 3).
        iterations: Number of dilation iterations (default 1).

    Returns:
        Dilated image (same shape as src).
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32)
    h, w = src_gpu.shape[:2]
    is_3d = len(src_gpu.shape) == 3

    kernel_data, kh, kw, kh_size, kw_size = _prepare_kernel(kernel, ksize)
    kernel_gpu = ti.ndarray(dtype=ti.i32, shape=(21, 21))
    kernel_gpu.from_numpy(kernel_data)
    kh_gpu = ti.ndarray(dtype=ti.i32, shape=(21,))
    kh_gpu.from_numpy(kh)
    kw_gpu = ti.ndarray(dtype=ti.i32, shape=(21,))
    kw_gpu.from_numpy(kw)

    dst_gpu = common.get_temp_buffer(src_gpu.shape, ti.f32)

    for _ in range(iterations):
        if is_3d:
            _dilate_3d_kernel(src_gpu, dst_gpu, kh_gpu, kw_gpu, kernel_gpu,
                              kh_size, kw_size, h, w)
        else:
            _dilate_2d_kernel(src_gpu, dst_gpu, kh_gpu, kw_gpu, kernel_gpu,
                              kh_size, kw_size, h, w)
        if iterations > 1:
            src_gpu, dst_gpu = dst_gpu, src_gpu

    if iterations % 2 == 0:
        result = src_gpu
    else:
        result = dst_gpu

    common.release_temp_buffer(dst_gpu if result is not dst_gpu else src_gpu)
    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(result, not hasattr(src, "to_numpy"))


@ti_thread
def erode(src, kernel=None, ksize=3, iterations=1):
    """
    Erode image (min filter) with structuring element.
    Equivalent to cv2.erode(src, kernel, iterations=iterations).

    Args:
        src: Input image (H,W) or (H,W,C) float32.
        kernel: Structuring element (numpy array). None = rectangular ksize x ksize.
        ksize: Kernel size if kernel is None (default 3).
        iterations: Number of erosion iterations (default 1).

    Returns:
        Eroded image (same shape as src).
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32)
    h, w = src_gpu.shape[:2]
    is_3d = len(src_gpu.shape) == 3

    kernel_data, kh, kw, kh_size, kw_size = _prepare_kernel(kernel, ksize)
    kernel_gpu = ti.ndarray(dtype=ti.i32, shape=(21, 21))
    kernel_gpu.from_numpy(kernel_data)
    kh_gpu = ti.ndarray(dtype=ti.i32, shape=(21,))
    kh_gpu.from_numpy(kh)
    kw_gpu = ti.ndarray(dtype=ti.i32, shape=(21,))
    kw_gpu.from_numpy(kw)

    dst_gpu = common.get_temp_buffer(src_gpu.shape, ti.f32)

    for _ in range(iterations):
        if is_3d:
            _erode_3d_kernel(src_gpu, dst_gpu, kh_gpu, kw_gpu, kernel_gpu,
                             kh_size, kw_size, h, w)
        else:
            _erode_2d_kernel(src_gpu, dst_gpu, kh_gpu, kw_gpu, kernel_gpu,
                             kh_size, kw_size, h, w)
        if iterations > 1:
            src_gpu, dst_gpu = dst_gpu, src_gpu

    if iterations % 2 == 0:
        result = src_gpu
    else:
        result = dst_gpu

    common.release_temp_buffer(dst_gpu if result is not dst_gpu else src_gpu)
    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(result, not hasattr(src, "to_numpy"))
