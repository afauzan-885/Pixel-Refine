"""
Image Thresholding - Taichi GPU
================================
OpenCV-compatible threshold operations.
Parity: cv2.threshold(src, thresh, maxval, type)

Usage (JIT):
    from taichi_vision.taichi_algorithm import threshold, THRESH_BINARY, THRESH_BINARY_INV
    result, thresh_val = threshold(src, 127, 255, 'BINARY')
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
    from .otsu import otsu_threshold
    from ..taichi_worker import ti_thread
except ImportError:
    pass

# Ensure ti_thread is defined in all execution paths (e.g. AOT compiler)
if 'ti_thread' not in globals() and 'ti_thread' not in locals():
    def ti_thread(func):
        return func

# Threshold type constants (matching OpenCV)
THRESH_BINARY = 0
THRESH_BINARY_INV = 1
THRESH_TRUNC = 2
THRESH_TOZERO = 3
THRESH_TOZERO_INV = 4
THRESH_OTSU = 8


if TAICHI_AVAILABLE:

    @ti.kernel
    def _thresh_binary_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32, w: ti.i32,
        thresh: ti.f32, maxval: ti.f32,
    ):
        """dst = (src > thresh) ? maxval : 0"""
        for y, x in ti.ndrange(h, w):
            dst[y, x] = maxval if src[y, x] > thresh else 0.0

    @ti.kernel
    def _thresh_binary_inv_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32, w: ti.i32,
        thresh: ti.f32, maxval: ti.f32,
    ):
        """dst = (src > thresh) ? 0 : maxval"""
        for y, x in ti.ndrange(h, w):
            dst[y, x] = 0.0 if src[y, x] > thresh else maxval

    @ti.kernel
    def _thresh_trunc_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32, w: ti.i32,
        thresh: ti.f32, maxval: ti.f32,
    ):
        """dst = min(src, thresh)"""
        for y, x in ti.ndrange(h, w):
            val = src[y, x]
            dst[y, x] = val if val <= thresh else thresh

    @ti.kernel
    def _thresh_tozero_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32, w: ti.i32,
        thresh: ti.f32, maxval: ti.f32,
    ):
        """dst = (src > thresh) ? src : 0"""
        for y, x in ti.ndrange(h, w):
            val = src[y, x]
            dst[y, x] = val if val > thresh else 0.0

    @ti.kernel
    def _thresh_tozero_inv_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32, w: ti.i32,
        thresh: ti.f32, maxval: ti.f32,
    ):
        """dst = (src > thresh) ? 0 : src"""
        for y, x in ti.ndrange(h, w):
            val = src[y, x]
            dst[y, x] = 0.0 if val > thresh else val


@ti_thread
def threshold(src, thresh=127, maxval=255, thresh_type='BINARY'):
    """
    Apply threshold to image.
    Parity: cv2.threshold(src, thresh, maxval, type)

    Args:
        src: Input image (H,W) float32.
        thresh: Threshold value.
        maxval: Maximum value for BINARY/BINARY_INV.
        thresh_type: 'BINARY', 'BINARY_INV', 'TRUNC', 'TOZERO', 'TOZERO_INV', 'OTSU'
                     or integer constants.

    Returns:
        (retval, thresholded_image) — matching OpenCV return signature.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Map string to integer constant
    if isinstance(thresh_type, str):
        type_map = {
            'BINARY': THRESH_BINARY,
            'BINARY_INV': THRESH_BINARY_INV,
            'TRUNC': THRESH_TRUNC,
            'TOZERO': THRESH_TOZERO,
            'TOZERO_INV': THRESH_TOZERO_INV,
            'OTSU': THRESH_OTSU,
        }
        thresh_type = type_map.get(thresh_type.upper(), THRESH_BINARY)

    # Handle OTSU: compute optimal threshold first
    actual_thresh = float(thresh)
    if thresh_type & THRESH_OTSU:
        # Compute Otsu threshold on CPU (histogram is fast enough)
        src_np = src if isinstance(src, np.ndarray) else src.to_numpy()
        if src_np.dtype == np.uint8:
            hist, _ = np.histogram(src_np.ravel(), bins=256, range=(0, 256))
        else:
            hist, _ = np.histogram(src_np.ravel(), bins=256, range=(float(src_np.min()), float(src_np.max())))
        # Otsu's method
        total = hist.sum()
        sum_total = np.sum(np.arange(len(hist)) * hist)
        sum_bg = 0.0
        weight_bg = 0
        max_variance = 0.0
        best_thresh = 0
        for t in range(len(hist)):
            weight_bg += hist[t]
            if weight_bg == 0:
                continue
            weight_fg = total - weight_bg
            if weight_fg == 0:
                break
            sum_bg += t * hist[t]
            mean_bg = sum_bg / weight_bg
            mean_fg = (sum_total - sum_bg) / weight_fg
            variance = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
            if variance > max_variance:
                max_variance = variance
                best_thresh = t
        if src_np.dtype == np.uint8:
            actual_thresh = float(best_thresh)
        else:
            actual_thresh = float(src_np.min()) + (float(src_np.max()) - float(src_np.min())) * best_thresh / 255.0
        # Remove OTSU flag, keep base type
        thresh_type = thresh_type & 0x07

    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32)
    h, w = src_gpu.shape[:2]
    dst_gpu = common.get_temp_buffer((h, w), ti.f32)

    kernel_map = {
        THRESH_BINARY: _thresh_binary_kernel,
        THRESH_BINARY_INV: _thresh_binary_inv_kernel,
        THRESH_TRUNC: _thresh_trunc_kernel,
        THRESH_TOZERO: _thresh_tozero_kernel,
        THRESH_TOZERO_INV: _thresh_tozero_inv_kernel,
    }
    kernel_func = kernel_map.get(thresh_type, _thresh_binary_kernel)
    kernel_func(src_gpu, dst_gpu, h, w, actual_thresh, float(maxval))

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    result = common.to_numpy_if_needed(dst_gpu, not hasattr(src, "to_numpy"))
    return (actual_thresh, result)
