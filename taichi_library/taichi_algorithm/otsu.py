# Marker: GPU_NATIVE_MARKER_V3
"""
Otsu's Thresholding - Taichi GPU Implementation
================================================
Automatic global thresholding via between-class variance maximization.

Reference:
  - Otsu, N. (1979). "A Threshold Selection Method from Gray-Level Histograms."
    IEEE Transactions on Systems, Man, and Cybernetics, SMC-9(1), pp. 62-66.

Pipeline:
  1. Parallel histogram (shared-memory atomics on GPU)
  2. Threshold search over 256 bins (trivial, CPU-side)
  3. Parallel binary thresholding (one thread per pixel)
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
    from . import common
    from .taichi_worker import ti_thread
except ImportError:
    pass

# Threshold types (OpenCV-compatible)
THRESH_BINARY = 0
THRESH_BINARY_INV = 1
THRESH_OTSU = 8  # Flag to combine with THRESH_BINARY


def _otsu_threshold_cpu(hist):
    """
    Compute optimal Otsu threshold from a 256-bin histogram on CPU.
    Maximizes between-class variance: sigma_B^2 = w0 * w1 * (mu0 - mu1)^2

    Args:
        hist: numpy array of shape (256,) with bin counts.

    Returns:
        Optimal threshold value (int, 0-255).
    """
    total = hist.sum()
    if total == 0:
        return 0

    # Compute total mean
    mu_T = 0.0
    for i in range(256):
        mu_T += i * hist[i]
    mu_T /= total

    # Incremental search
    w0 = 0.0
    sum_0 = 0.0
    max_sigma_B = -1.0
    best_t = 0

    for t in range(256):
        w0 += hist[t]
        if w0 == 0:
            continue
        w1 = total - w0
        if w1 == 0:
            break

        sum_0 += t * hist[t]
        mu0 = sum_0 / w0
        mu1 = (mu_T * total - sum_0) / w1

        sigma_B = w0 * w1 * (mu0 - mu1) * (mu0 - mu1)
        if sigma_B > max_sigma_B:
            max_sigma_B = sigma_B
            best_t = t

    return best_t


if TAICHI_AVAILABLE:

    # =========================================================================
    # Kernel 1: Parallel Histogram (one thread per pixel row, atomics to bins)
    # =========================================================================
    @ti.kernel
    def _compute_histogram_kernel(src: ti.types.ndarray(), hist: ti.types.ndarray(),
                                   h: int, w: int):
        """Compute 256-bin histogram using atomic operations."""
        for y, x in ti.ndrange(h, w):
            val = ti.cast(tm.clamp(src[y, x], 0.0, 255.0), ti.i32)
            ti.atomic_add(hist[val], 1)

    # =========================================================================
    # Kernel 2: Parallel Binary Thresholding
    # =========================================================================
    @ti.kernel
    def _threshold_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                           threshold: float, max_val: float, thresh_type: int,
                           h: int, w: int):
        """Apply binary threshold. thresh_type: 0=normal, 1=inverted."""
        for y, x in ti.ndrange(h, w):
            val = src[y, x]
            if thresh_type == 0:
                # THRESH_BINARY
                dst[y, x] = max_val if val > threshold else 0.0
            else:
                # THRESH_BINARY_INV
                dst[y, x] = 0.0 if val > threshold else max_val

    # =========================================================================
    # Kernel 3: Parallel Threshold + Convert to uint8 range
    # =========================================================================
    @ti.kernel
    def _threshold_to_u8_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                                 threshold: float, max_val: float, thresh_type: int,
                                 h: int, w: int):
        """Apply threshold and output in [0, max_val] range."""
        for y, x in ti.ndrange(h, w):
            val = src[y, x]
            if thresh_type == 0:
                dst[y, x] = max_val if val > threshold else 0.0
            else:
                dst[y, x] = 0.0 if val > threshold else max_val


@ti_thread
def otsu_threshold(src, dst=None, thresh_type=THRESH_BINARY, max_val=255.0,
                    buffer_provider="pool"):
    """
    Otsu's automatic thresholding (GPU-accelerated).
    OpenCV-compatible: Similar to cv2.threshold(src, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    Args:
        src: Input grayscale image (H, W), uint8 or float32 [0, 255].
        dst: Optional output buffer (H, W).
        thresh_type: THRESH_BINARY (0) or THRESH_BINARY_INV (1).
        max_val: Maximum value for thresholded output (default 255).
        buffer_provider: Buffer pool provider.

    Returns:
        Tuple of (threshold_value, thresholded_image).
        - threshold_value: The optimal Otsu threshold (float).
        - thresholded_image: Binary image with values in {0, max_val}.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_numpy = isinstance(src, np.ndarray)
    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32,
                                                       buffer_provider=buffer_provider)
    h, w = src_gpu.shape[:2]

    # Step 1: Compute histogram on GPU
    hist_gpu = ti.ndarray(dtype=ti.i32, shape=(256,))
    hist_gpu.fill(0)
    _compute_histogram_kernel(src_gpu, hist_gpu, h, w)

    # Step 2: Download histogram and find optimal threshold (CPU-side, trivial)
    hist_np = hist_gpu.to_numpy()
    threshold_val = _otsu_threshold_cpu(hist_np)

    # Step 3: Apply threshold on GPU
    if dst is not None:
        dst_gpu, _ = common.ensure_taichi_field(dst, dtype=ti.f32,
                                                 buffer_provider=buffer_provider)
    else:
        dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

    _threshold_kernel(src_gpu, dst_gpu, float(threshold_val), float(max_val),
                       thresh_type, h, w)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    result = common.to_numpy_if_needed(dst_gpu, is_numpy)
    return float(threshold_val), result
