"""
Structural Similarity Index (SSIM) - Taichi GPU
=================================================
GPU-accelerated SSIM computation.
Parity: skimage.metrics.structural_similarity

Usage (JIT):
    from taichi_vision.taichi_algorithm import ssim
    score = ssim(img1, img2, window_size=11)
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
    def _ssim_channel_kernel(
        img1: ti.types.ndarray(dtype=ti.f32, ndim=2),
        img2: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32, w: ti.i32,
        win_radius: ti.i32,
        C1: ti.f32, C2: ti.f32,
        ssim_sum: ti.types.ndarray(dtype=ti.f32, ndim=1),
    ):
        """Compute SSIM sum over all valid pixels using window-based approach."""
        total_ssim = 0.0
        valid_count = 0
        for y, x in ti.ndrange(h, w):
            # Compute local statistics within window
            mu1 = 0.0
            mu2 = 0.0
            sigma1_sq = 0.0
            sigma2_sq = 0.0
            sigma12 = 0.0
            count = 0
            for dy in ti.static(range(21)):
                if dy <= 2 * win_radius:
                    for dx in ti.static(range(21)):
                        if dx <= 2 * win_radius:
                            sy = y + dy - win_radius
                            sx = x + dx - win_radius
                            if sy >= 0 and sy < h and sx >= 0 and sx < w:
                                v1 = img1[sy, sx]
                                v2 = img2[sy, sx]
                                mu1 += v1
                                mu2 += v2
                                sigma1_sq += v1 * v1
                                sigma2_sq += v2 * v2
                                sigma12 += v1 * v2
                                count += 1
            if count > 0:
                inv_n = 1.0 / float(count)
                mu1 *= inv_n
                mu2 *= inv_n
                sigma1_sq = sigma1_sq * inv_n - mu1 * mu1
                sigma2_sq = sigma2_sq * inv_n - mu2 * mu2
                sigma12 = sigma12 * inv_n - mu1 * mu2

                numerator = (2.0 * mu1 * mu2 + C1) * (2.0 * sigma12 + C2)
                denominator = (mu1 * mu1 + mu2 * mu2 + C1) * (sigma1_sq + sigma2_sq + C2)
                total_ssim += numerator / denominator
                valid_count += 1

        ssim_sum[0] = total_ssim
        ssim_sum[1] = float(valid_count)


@ti_thread
def ssim(img1, img2, window_size=11, data_range=None, k1=0.01, k2=0.03):
    """
    Compute Structural Similarity Index between two images.
    Parity: skimage.metrics.structural_similarity(img1, img2)

    Args:
        img1, img2: Input images (H,W) float32 or uint8.
        window_size: Size of the sliding window (must be odd, default 11).
        data_range: Dynamic range of images (default: auto-detect from dtype).
        k1, k2: SSIM stability constants (default: 0.01, 0.03).

    Returns:
        SSIM score (float, higher is better, max 1.0).
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Ensure float32
    if isinstance(img1, np.ndarray):
        img1_f32 = img1.astype(np.float32)
        img2_f32 = img2.astype(np.float32)
    else:
        img1_f32 = img1
        img2_f32 = img2

    # Auto-detect data range
    if data_range is None:
        if isinstance(img1, np.ndarray):
            if img1.dtype == np.uint8:
                data_range = 255.0
            elif img1.dtype == np.uint16:
                data_range = 65535.0
            else:
                data_range = float(img1.max() - img1.min())
        else:
            data_range = 255.0

    C1 = (k1 * data_range) ** 2
    C2 = (k2 * data_range) ** 2
    win_radius = window_size // 2

    # Handle multi-channel: compute SSIM per channel and average
    if img1_f32.ndim == 3:
        channels = img1_f32.shape[2]
        total_ssim = 0.0
        for c in range(channels):
            ch1 = np.ascontiguousarray(img1_f32[:, :, c])
            ch2 = np.ascontiguousarray(img2_f32[:, :, c])
            total_ssim += _compute_ssim_2d(ch1, ch2, win_radius, C1, C2)
        return total_ssim / channels
    else:
        return _compute_ssim_2d(img1_f32, img2_f32, win_radius, C1, C2)


def _compute_ssim_2d(img1_np, img2_np, win_radius, C1, C2):
    """Compute SSIM for a single 2D channel."""
    h, w = img1_np.shape[:2]
    img1_gpu, is_temp1 = common.ensure_taichi_field(img1_np, dtype=ti.f32)
    img2_gpu, is_temp2 = common.ensure_taichi_field(img2_np, dtype=ti.f32)

    result_buf = ti.ndarray(dtype=ti.f32, shape=(2,))
    _ssim_channel_kernel(img1_gpu, img2_gpu, h, w, win_radius, C1, C2, result_buf)

    result = result_buf.to_numpy()
    total_ssim = result[0]
    valid_count = result[1]

    if is_temp1:
        common.release_temp_buffer(img1_gpu)
    if is_temp2:
        common.release_temp_buffer(img2_gpu)

    if valid_count > 0:
        return float(total_ssim / valid_count)
    return 0.0
