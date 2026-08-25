"""
GPU Histogram - Taichi GPU
============================
GPU-accelerated histogram computation.
Parity: np.histogram(src, bins, range)

Usage (JIT):
    from taichi_vision.taichi_algorithm import histogram
    hist, bin_edges = histogram(src, bins=256, range=(0, 256))
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
    def _histogram_2d_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        hist: ti.types.ndarray(dtype=ti.i32, ndim=1),
        h: ti.i32, w: ti.i32,
        num_bins: ti.i32,
        range_min: ti.f32, range_max: ti.f32,
    ):
        """Compute histogram for 2D array using atomic operations."""
        scale = float(num_bins) / (range_max - range_min) if (range_max - range_min) > 1e-10 else 1.0
        for y, x in ti.ndrange(h, w):
            val = src[y, x]
            bin_idx = int((val - range_min) * scale)
            bin_idx = tm.clamp(bin_idx, 0, num_bins - 1)
            ti.atomic_add(hist[bin_idx], 1)

    @ti.kernel
    def _histogram_2d_f32_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        hist: ti.types.ndarray(dtype=ti.f32, ndim=1),
        h: ti.i32, w: ti.i32,
        num_bins: ti.i32,
        range_min: ti.f32, range_max: ti.f32,
    ):
        """Compute histogram for 2D array, f32 output."""
        scale = float(num_bins) / (range_max - range_min) if (range_max - range_min) > 1e-10 else 1.0
        for y, x in ti.ndrange(h, w):
            val = src[y, x]
            bin_idx = int((val - range_min) * scale)
            bin_idx = tm.clamp(bin_idx, 0, num_bins - 1)
            ti.atomic_add(hist[bin_idx], 1.0)


@ti_thread
def histogram(src, bins=256, range=(0, 256)):
    """
    Compute histogram of image values.
    Parity: np.histogram(src, bins=bins, range=range)

    Args:
        src: Input image (H,W) or (H,W,C) float32.
        bins: Number of histogram bins (default 256).
        range: Tuple (min_val, max_val) for histogram range.

    Returns:
        (hist, bin_edges) — matching np.histogram return signature.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    range_min, range_max = float(range[0]), float(range[1])
    src_np = src if isinstance(src, np.ndarray) else src.to_numpy()

    # Flatten for multi-channel
    if src_np.ndim == 3:
        src_flat = src_np.reshape(-1).astype(np.float32)
    else:
        src_flat = src_np.ravel().astype(np.float32)

    # GPU histogram
    h_img, w_img = src_np.shape[:2] if src_np.ndim >= 2 else (src_np.size, 1)
    src_gpu, is_temp = common.ensure_taichi_field(src_np.astype(np.float32), dtype=ti.f32)

    hist_gpu = ti.ndarray(dtype=ti.f32, shape=(bins,))
    # Clear histogram
    hist_np = np.zeros(bins, dtype=np.float32)
    hist_gpu.from_numpy(hist_np)

    if src_np.ndim >= 2:
        _histogram_2d_f32_kernel(src_gpu, hist_gpu, h_img, w_img, bins, range_min, range_max)
    else:
        # For 1D arrays, reshape to 2D
        src_2d = src_np.reshape(1, -1).astype(np.float32)
        src_gpu2, _ = common.ensure_taichi_field(src_2d, dtype=ti.f32)
        _histogram_2d_f32_kernel(src_gpu2, hist_gpu, 1, src_np.size, bins, range_min, range_max)
        common.release_temp_buffer(src_gpu2)

    if is_temp:
        common.release_temp_buffer(src_gpu)

    hist_result = hist_gpu.to_numpy()
    bin_edges = np.linspace(range_min, range_max, bins + 1)

    return hist_result, bin_edges
