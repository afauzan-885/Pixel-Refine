"""
Image Normalization - Taichi GPU
=================================
OpenCV-compatible normalization operations.
Parity: cv2.normalize(src, dst, alpha, beta, norm_type)

Usage (JIT):
    from taichi_vision.taichi_algorithm import normalize
    result = normalize(src, alpha=0, beta=255, norm_type='MINMAX')
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

# Norm type constants (matching OpenCV)
NORM_INF = 0
NORM_L1 = 1
NORM_L2 = 2
NORM_MINMAX = 32


if TAICHI_AVAILABLE:

    @ti.kernel
    def _find_min_max_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        min_val: ti.types.ndarray(dtype=ti.f32, ndim=1),
        max_val: ti.types.ndarray(dtype=ti.f32, ndim=1),
        h: ti.i32,
        w: ti.i32,
    ):
        """Find global min and max of a 2D array."""
        local_min = 1e30
        local_max = -1e30
        for y, x in ti.ndrange(h, w):
            val = src[y, x]
            if val < local_min:
                local_min = val
            if val > local_max:
                local_max = val
        min_val[0] = local_min
        max_val[0] = local_max

    @ti.kernel
    def _normalize_minmax_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32,
        w: ti.i32,
        alpha: ti.f32,
        beta: ti.f32,
        src_min: ti.f32,
        src_max: ti.f32,
    ):
        """MIN-MAX normalization: dst = (src - src_min) / (src_max - src_min) * (beta - alpha) + alpha."""
        denom = src_max - src_min
        if ti.abs(denom) < 1e-10:
            denom = 1.0
        for y, x in ti.ndrange(h, w):
            dst[y, x] = (src[y, x] - src_min) / denom * (beta - alpha) + alpha

    @ti.kernel
    def _compute_norm_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        norm_val: ti.types.ndarray(dtype=ti.f32, ndim=1),
        h: ti.i32,
        w: ti.i32,
        norm_type: ti.i32,
    ):
        """Compute L1, L2, or INF norm."""
        acc = 0.0
        max_val = 0.0
        for y, x in ti.ndrange(h, w):
            val = ti.abs(src[y, x])
            if norm_type == 0:  # INF
                if val > max_val:
                    max_val = val
            elif norm_type == 1:  # L1
                acc += val
            else:  # L2
                acc += val * val
        if norm_type == 0:
            norm_val[0] = max_val
        elif norm_type == 1:
            norm_val[0] = acc
        else:
            norm_val[0] = ti.sqrt(acc)

    @ti.kernel
    def _normalize_norm_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32,
        w: ti.i32,
        alpha: ti.f32,
        norm_factor: ti.f32,
    ):
        """Scale: dst = src * (alpha / norm_factor)."""
        scale = alpha / norm_factor if ti.abs(norm_factor) > 1e-10 else 1.0
        for y, x in ti.ndrange(h, w):
            dst[y, x] = src[y, x] * scale


@ti_thread
def normalize(src, alpha=0, beta=255, norm_type='MINMAX'):
    """
    Normalize image values.
    Parity: cv2.normalize(src, dst, alpha, beta, norm_type)

    Args:
        src: Input image (H,W) float32.
        alpha: Lower bound (for MINMAX) or target norm value.
        beta: Upper bound (for MINMAX only).
        norm_type: 'MINMAX', 'L1', 'L2', 'INF' or integer constants.

    Returns:
        Normalized image (same shape as src).
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32)
    h, w = src_gpu.shape[:2]
    dst_gpu = common.get_temp_buffer((h, w), ti.f32)

    # Map string to integer constant
    if isinstance(norm_type, str):
        norm_map = {'INF': 0, 'L1': 1, 'L2': 2, 'MINMAX': 32}
        norm_type = norm_map.get(norm_type.upper(), 32)

    if norm_type == NORM_MINMAX:
        # Find min/max on GPU
        min_buf = ti.ndarray(dtype=ti.f32, shape=(1,))
        max_buf = ti.ndarray(dtype=ti.f32, shape=(1,))
        _find_min_max_kernel(src_gpu, min_buf, max_buf, h, w)
        src_min = min_buf.to_numpy()[0]
        src_max = max_buf.to_numpy()[0]
        _normalize_minmax_kernel(src_gpu, dst_gpu, h, w, float(alpha), float(beta), src_min, src_max)
    else:
        # L1, L2, INF normalization
        norm_buf = ti.ndarray(dtype=ti.f32, shape=(1,))
        _compute_norm_kernel(src_gpu, norm_buf, h, w, norm_type)
        norm_val = norm_buf.to_numpy()[0]
        _normalize_norm_kernel(src_gpu, dst_gpu, h, w, float(alpha), norm_val)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(dst_gpu, not hasattr(src, "to_numpy"))
