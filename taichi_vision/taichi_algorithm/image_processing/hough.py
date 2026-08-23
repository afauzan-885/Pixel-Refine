# Marker: GPU_NATIVE_MARKER_V3
"""
Hough Line Transform - Taichi GPU Implementation
=================================================
Detect lines in binary edge maps using the polar parameter space.

Reference:
  - Duda, R.O., Hart, P.E. (1972). "Use of the Hough Transformation to Detect
    Lines and Curves in Pictures." Communications of the ACM, 15(1), pp. 11-15.
  - Galambos, C., Matas, J. "Progressive Probabilistic Hough Transform."

Algorithm:
  Parameterize lines as: rho = x*cos(theta) + y*sin(theta)
  Each edge pixel votes for all (rho, theta) bins in an accumulator array.
  Peaks in the accumulator correspond to detected lines.

GPU Strategy:
  - Voting: one thread per edge pixel, atomicAdd for each theta bin
  - Peak detection: parallel NMS on the accumulator array
"""

import numpy as np
import os
import importlib
import math

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
    from .canny import canny as _canny_impl
except ImportError:
    pass

if TAICHI_AVAILABLE:

    # =========================================================================
    # Stage 1: Voting Kernel
    # =========================================================================
    @ti.kernel
    def _hough_vote_kernel(edges: ti.types.ndarray(),
                            accumulator: ti.types.ndarray(),
                            cos_table: ti.types.ndarray(),
                            sin_table: ti.types.ndarray(),
                            h: int, w: int,
                            num_theta: int, rho_offset: int,
                            edge_threshold: float):
        """
        Each edge pixel votes for all theta bins.
        accumulator shape: (num_rho, num_theta) flattened as (rho_bins, theta_bins).
        """
        for y, x in ti.ndrange(h, w):
            if edges[y, x] >= edge_threshold:
                for t in range(num_theta):
                    rho = float(x) * cos_table[t] + float(y) * sin_table[t]
                    rho_bin = ti.cast(ti.round(rho) + float(rho_offset), ti.i32)
                    # Clamp to valid range
                    rho_bin = tm.clamp(rho_bin, 0, 2 * rho_offset)
                    ti.atomic_add(accumulator[rho_bin, t], 1)

    # =========================================================================
    # Stage 2: Peak Detection (NMS on accumulator)
    # =========================================================================
    @ti.kernel
    def _hough_peaks_kernel(accumulator: ti.types.ndarray(),
                              peaks: ti.types.ndarray(),
                              peak_count: ti.types.ndarray(),
                              num_rho: int, num_theta: int,
                              threshold: int, nms_radius: int,
                              max_peaks: int):
        """
        Find peaks in accumulator with non-maximum suppression.
        peaks: output array of (rho_bin, theta_bin, votes) tuples.
        peak_count: single element tracking number of peaks found.
        """
        for r, t in ti.ndrange(num_rho, num_theta):
            if accumulator[r, t] < threshold:
                continue

            # NMS: check neighborhood
            is_max = True
            for dr in range(-nms_radius, nms_radius + 1):
                for dt in range(-nms_radius, nms_radius + 1):
                    if dr == 0 and dt == 0:
                        continue
                    nr = r + dr
                    nt = t + dt
                    if 0 <= nr < num_rho and 0 <= nt < num_theta:
                        if accumulator[nr, nt] > accumulator[r, t]:
                            is_max = False

            if is_max:
                idx = ti.atomic_add(peak_count[0], 1)
                if idx < max_peaks:
                    peaks[idx, 0] = float(r)
                    peaks[idx, 1] = float(t)
                    peaks[idx, 2] = float(accumulator[r, t])


@ti_thread
def hough_lines(edge_image, rho_resolution=1.0, theta_resolution=1.0,
                threshold=80, buffer_provider="pool"):
    """
    Standard Hough Line Transform (GPU-accelerated).
    OpenCV-compatible: Similar to cv2.HoughLines()

    Args:
        edge_image: Binary edge map (H, W) from Canny, values {0, 255}.
        rho_resolution: Distance resolution in pixels (default 1.0).
        theta_resolution: Angle resolution in degrees (default 1.0).
        threshold: Minimum votes to detect a line.

    Returns:
        List of (rho, theta) tuples for detected lines.
        rho: distance from origin in pixels.
        theta: angle in radians.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_numpy = isinstance(edge_image, np.ndarray)
    edges_gpu, edges_is_temp = common.ensure_taichi_field(edge_image, dtype=ti.f32,
                                                            buffer_provider=buffer_provider)
    h, w = edges_gpu.shape[:2]

    # Compute accumulator dimensions
    rho_max = int(math.sqrt(h * h + w * w)) + 1
    num_rho = int(2 * rho_max / rho_resolution) + 1
    num_theta = int(180.0 / theta_resolution)
    rho_offset = int(rho_max / rho_resolution)

    # Pre-compute sin/cos tables
    theta_values = np.deg2rad(np.arange(0, 180, theta_resolution)).astype(np.float32)
    cos_table = np.cos(theta_values)
    sin_table = np.sin(theta_values)

    cos_gpu = ti.ndarray(dtype=ti.f32, shape=(num_theta,))
    sin_gpu = ti.ndarray(dtype=ti.f32, shape=(num_theta,))
    cos_gpu.from_numpy(cos_table)
    sin_gpu.from_numpy(sin_table)

    # Allocate accumulator
    acc = ti.ndarray(dtype=ti.i32, shape=(num_rho, num_theta))
    acc.fill(0)

    # Stage 1: Voting
    _hough_vote_kernel(edges_gpu, acc, cos_gpu, sin_gpu, h, w,
                        num_theta, rho_offset, 128.0)

    if edges_is_temp:
        common.release_temp_buffer(edges_gpu)

    # Stage 2: Peak detection
    max_peaks = 1000
    peaks = ti.ndarray(dtype=ti.f32, shape=(max_peaks, 3))
    peak_count = ti.ndarray(dtype=ti.i32, shape=(1,))
    peak_count.fill(0)

    _hough_peaks_kernel(acc, peaks, peak_count, num_rho, num_theta,
                          threshold, nms_radius=3, max_peaks=max_peaks)

    # Download results
    n_peaks = peak_count.to_numpy()[0]
    peaks_np = peaks.to_numpy()

    # Convert bins to (rho, theta)
    lines = []
    for i in range(min(n_peaks, max_peaks)):
        rho_bin = int(peaks_np[i, 0])
        theta_bin = int(peaks_np[i, 1])
        rho = (rho_bin - rho_offset) * rho_resolution
        theta = theta_bin * theta_resolution * math.pi / 180.0
        lines.append((rho, theta))

    return lines


@ti_thread
def hough_lines_with_canny(src, low_threshold=50.0, high_threshold=150.0,
                             rho_resolution=1.0, theta_resolution=1.0,
                             vote_threshold=80, buffer_provider="pool"):
    """
    Convenience: Canny edge detection + Hough line detection in one call.

    Args:
        src: Input grayscale image (H, W).
        low_threshold: Canny low threshold.
        high_threshold: Canny high threshold.
        rho_resolution: Distance resolution in pixels.
        theta_resolution: Angle resolution in degrees.
        vote_threshold: Minimum votes for Hough lines.

    Returns:
        Tuple of (lines, edge_map) where lines is list of (rho, theta).
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Run Canny first
    edges = _canny_impl(src, low_threshold=low_threshold,
                          high_threshold=high_threshold,
                          buffer_provider=buffer_provider)

    # Run Hough on edges
    # Need to call without @ti_thread since we're already inside one
    # Re-upload edges and run hough
    is_numpy = isinstance(src, np.ndarray)
    edges_gpu, edges_is_temp = common.ensure_taichi_field(edges, dtype=ti.f32,
                                                            buffer_provider=buffer_provider)
    h, w = edges_gpu.shape[:2]

    rho_max = int(math.sqrt(h * h + w * w)) + 1
    num_rho = int(2 * rho_max / rho_resolution) + 1
    num_theta = int(180.0 / theta_resolution)
    rho_offset = int(rho_max / rho_resolution)

    theta_values = np.deg2rad(np.arange(0, 180, theta_resolution)).astype(np.float32)
    cos_table = np.cos(theta_values)
    sin_table = np.sin(theta_values)

    cos_gpu = ti.ndarray(dtype=ti.f32, shape=(num_theta,))
    sin_gpu = ti.ndarray(dtype=ti.f32, shape=(num_theta,))
    cos_gpu.from_numpy(cos_table)
    sin_gpu.from_numpy(sin_table)

    acc = ti.ndarray(dtype=ti.i32, shape=(num_rho, num_theta))
    acc.fill(0)

    _hough_vote_kernel(edges_gpu, acc, cos_gpu, sin_gpu, h, w,
                        num_theta, rho_offset, 128.0)

    if edges_is_temp:
        common.release_temp_buffer(edges_gpu)

    max_peaks = 1000
    peaks = ti.ndarray(dtype=ti.f32, shape=(max_peaks, 3))
    peak_count = ti.ndarray(dtype=ti.i32, shape=(1,))
    peak_count.fill(0)

    _hough_peaks_kernel(acc, peaks, peak_count, num_rho, num_theta,
                          vote_threshold, nms_radius=3, max_peaks=max_peaks)

    n_peaks = peak_count.to_numpy()[0]
    peaks_np = peaks.to_numpy()

    lines = []
    for i in range(min(n_peaks, max_peaks)):
        rho_bin = int(peaks_np[i, 0])
        theta_bin = int(peaks_np[i, 1])
        rho = (rho_bin - rho_offset) * rho_resolution
        theta = theta_bin * theta_resolution * math.pi / 180.0
        lines.append((rho, theta))

    return lines, edges
