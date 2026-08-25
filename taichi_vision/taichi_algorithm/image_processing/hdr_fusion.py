"""
HDR Exposure Fusion - Taichi GPU
=================================
Noise-aware exposure fusion with multi-resolution Laplacian pyramid blending.

Algorithm (Mertens et al. + Noise-Aware Enhancement):
  1. Compute per-pixel weight maps: W_noise × W_exposure × W_detail
  2. Build Laplacian pyramids for each frame
  3. Build Gaussian pyramids for each weight map
  4. Blend Laplacian levels weighted by Gaussian weight levels
  5. Reconstruct fused image from blended Laplacian pyramid

Priority: Noise > Exposure > Detail

Usage (JIT):
    from taichi_vision.taichi_algorithm import hdr_fuse
    result = hdr_fuse(frames, noise_sigmas=None)

Usage (AOT):
    import taichi_vision.taichi_aot as ta
    result = ta.hdr_fusion(frames)
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


# =============================================================================
# GPU Kernels
# =============================================================================

if TAICHI_AVAILABLE:

    @ti.kernel
    def _compute_weight_kernel(
        img_rgb: ti.types.ndarray(dtype=ti.f32, ndim=3),
        lap_gray: ti.types.ndarray(dtype=ti.f32, ndim=2),
        weight: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32, w: ti.i32,
        noise_sigma: ti.f32,
        noise_power: ti.f32,
        exposure_sigma: ti.f32,
        exposure_power: ti.f32,
        detail_power: ti.f32,
        saturation_power: ti.f32,
    ):
        """Compute combined weight: W_noise^p × W_exposure^q × W_detail^r."""
        for y, x in ti.ndrange(h, w):
            r_val = img_rgb[y, x, 0]
            g_val = img_rgb[y, x, 1]
            b_val = img_rgb[y, x, 2]

            # --- Noise weight (SNR-based) ---
            # SNR = signal / noise_sigma
            # W_noise = SNR / (SNR + k)  where k is smoothing factor
            luma = 0.299 * r_val + 0.587 * g_val + 0.114 * b_val
            snr = luma / ti.max(noise_sigma, 1e-6)
            w_noise = ti.pow(snr / (snr + 0.5), noise_power)

            # --- Well-exposedness weight ---
            # Gaussian centered at 0.5 (optimal mid-tone)
            # Per-channel then combined
            w_exp_r = ti.exp(-ti.pow(r_val - 0.5, 2) / (2.0 * exposure_sigma * exposure_sigma))
            w_exp_g = ti.exp(-ti.pow(g_val - 0.5, 2) / (2.0 * exposure_sigma * exposure_sigma))
            w_exp_b = ti.exp(-ti.pow(b_val - 0.5, 2) / (2.0 * exposure_sigma * exposure_sigma))
            w_exposure = ti.pow(w_exp_r * w_exp_g * w_exp_b, exposure_power / 3.0)

            # --- Detail weight (contrast + saturation) ---
            # Contrast: absolute Laplacian of grayscale
            contrast = ti.abs(lap_gray[y, x])
            w_contrast = ti.pow(contrast + 1e-6, detail_power)

            # Saturation: std dev of RGB channels
            mean_rgb = (r_val + g_val + b_val) / 3.0
            sat = ti.sqrt(
                (r_val - mean_rgb) ** 2 +
                (g_val - mean_rgb) ** 2 +
                (b_val - mean_rgb) ** 2
            ) / 3.0
            w_sat = ti.pow(sat + 1e-6, saturation_power)

            # Combined weight
            weight[y, x] = w_noise * w_exposure * w_contrast * w_sat

    @ti.kernel
    def _normalize_weights_kernel(
        weights: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32, w: ti.i32, n_frames: ti.i32,
    ):
        """Normalize weight maps so they sum to 1 at each pixel."""
        for y, x in ti.ndrange(h, w):
            total = 0.0
            for i in range(n_frames):
                total += weights[i, y, x]
            if total > 1e-8:
                for i in range(n_frames):
                    weights[i, y, x] /= total
            else:
                # Equal weight fallback
                inv_n = 1.0 / float(n_frames)
                for i in range(n_frames):
                    weights[i, y, x] = inv_n

    @ti.kernel
    def _downsample_2x_3ch_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
    ):
        """Gaussian 2x downsampling for 3-channel images."""
        h_src, w_src = src.shape[0], src.shape[1]
        h_dst, w_dst = dst.shape[0], dst.shape[1]
        weights = ti.static([1.0, 4.0, 6.0, 4.0, 1.0])
        total_weight = 256.0
        for r, c in ti.ndrange(h_dst, w_dst):
            y_src = r * 2
            x_src = c * 2
            val0, val1, val2 = 0.0, 0.0, 0.0
            for j in ti.static(range(-2, 3)):
                for i in ti.static(range(-2, 3)):
                    sy = ti.min(ti.max(y_src + j, 0), h_src - 1)
                    sx = ti.min(ti.max(x_src + i, 0), w_src - 1)
                    w = weights[j + 2] * weights[i + 2]
                    val0 += src[sy, sx, 0] * w
                    val1 += src[sy, sx, 1] * w
                    val2 += src[sy, sx, 2] * w
            dst[r, c, 0] = val0 / total_weight
            dst[r, c, 1] = val1 / total_weight
            dst[r, c, 2] = val2 / total_weight

    @ti.kernel
    def _downsample_2x_1ch_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
    ):
        """Gaussian 2x downsampling for single-channel images."""
        h_src, w_src = src.shape[0], src.shape[1]
        h_dst, w_dst = dst.shape[0], dst.shape[1]
        weights = ti.static([1.0, 4.0, 6.0, 4.0, 1.0])
        total_weight = 256.0
        for r, c in ti.ndrange(h_dst, w_dst):
            y_src = r * 2
            x_src = c * 2
            val = 0.0
            for j in ti.static(range(-2, 3)):
                for i in ti.static(range(-2, 3)):
                    sy = ti.min(ti.max(y_src + j, 0), h_src - 1)
                    sx = ti.min(ti.max(x_src + i, 0), w_src - 1)
                    val += src[sy, sx] * weights[j + 2] * weights[i + 2]
            dst[r, c] = val / total_weight

    @ti.kernel
    def _upsample_2x_3ch_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
    ):
        """Bilinear 2x upsampling for 3-channel images (for Laplacian reconstruction)."""
        h_src, w_src = src.shape[0], src.shape[1]
        h_dst, w_dst = dst.shape[0], dst.shape[1]
        for r, c in ti.ndrange(h_dst, w_dst):
            y_f = float(r) * 0.5
            x_f = float(c) * 0.5
            y0 = ti.min(int(y_f), h_src - 1)
            x0 = ti.min(int(x_f), w_src - 1)
            y1 = ti.min(y0 + 1, h_src - 1)
            x1 = ti.min(x0 + 1, w_src - 1)
            fy = y_f - float(y0)
            fx = x_f - float(x0)
            for ch in ti.static(range(3)):
                val = (
                    src[y0, x0, ch] * (1 - fy) * (1 - fx) +
                    src[y0, x1, ch] * (1 - fy) * fx +
                    src[y1, x0, ch] * fy * (1 - fx) +
                    src[y1, x1, ch] * fy * fx
                )
                dst[r, c, ch] = val * 4.0  # Scale factor for Laplacian reconstruction

    @ti.kernel
    def _upsample_2x_1ch_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
    ):
        """Bilinear 2x upsampling for single-channel images."""
        h_src, w_src = src.shape[0], src.shape[1]
        h_dst, w_dst = dst.shape[0], dst.shape[1]
        for r, c in ti.ndrange(h_dst, w_dst):
            y_f = float(r) * 0.5
            x_f = float(c) * 0.5
            y0 = ti.min(int(y_f), h_src - 1)
            x0 = ti.min(int(x_f), w_src - 1)
            y1 = ti.min(y0 + 1, h_src - 1)
            x1 = ti.min(x0 + 1, w_src - 1)
            fy = y_f - float(y0)
            fx = x_f - float(x0)
            dst[r, c] = (
                src[y0, x0] * (1 - fy) * (1 - fx) +
                src[y0, x1] * (1 - fy) * fx +
                src[y1, x0] * fy * (1 - fx) +
                src[y1, x1] * fy * fx
            ) * 4.0

    @ti.kernel
    def _subtract_kernel(
        img: ti.types.ndarray(dtype=ti.f32, ndim=3),
        upsampled: ti.types.ndarray(dtype=ti.f32, ndim=3),
        lap: ti.types.ndarray(dtype=ti.f32, ndim=3),
    ):
        """Laplacian level = image - upsampled(coarser_level)."""
        for y, x, ch in ti.ndrange(img.shape[0], img.shape[1], img.shape[2]):
            lap[y, x, ch] = img[y, x, ch] - upsampled[y, x, ch]

    @ti.kernel
    def _add_weighted_laplacian_kernel(
        lap: ti.types.ndarray(dtype=ti.f32, ndim=3),
        weight: ti.types.ndarray(dtype=ti.f32, ndim=2),
        result: ti.types.ndarray(dtype=ti.f32, ndim=3),
    ):
        """Add weighted Laplacian to result accumulator."""
        for y, x, ch in ti.ndrange(lap.shape[0], lap.shape[1], lap.shape[2]):
            result[y, x, ch] += lap[y, x, ch] * weight[y, x]

    @ti.kernel
    def _add_3ch_kernel(
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
    ):
        """Add src to dst element-wise."""
        for y, x, ch in ti.ndrange(dst.shape[0], dst.shape[1], dst.shape[2]):
            dst[y, x, ch] += src[y, x, ch]


# =============================================================================
# Utility Functions
# =============================================================================

def _compute_laplacian(gray_np):
    """Compute absolute Laplacian for contrast measure."""
    h, w = gray_np.shape
    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    from . import filter2d
    lap = filter2d(gray_np, kernel)
    return np.abs(lap).astype(np.float32)


def _estimate_noise_sigma(gray_np):
    """Estimate sensor noise locally without depending on spatial-weight."""

    gray = np.asarray(gray_np, dtype=np.float32)
    if gray.size == 0 or gray.ndim != 2 or min(gray.shape) < 3:
        return 0.015
    padded = np.pad(gray, 1, mode="reflect")
    lap = (
        padded[:-2, 1:-1] + padded[1:-1, :-2]
        - 4.0 * padded[1:-1, 1:-1]
        + padded[1:-1, 2:] + padded[2:, 1:-1]
    )
    median = np.median(lap)
    sigma = np.median(np.abs(lap - median)) * 1.4826
    return float(np.clip(sigma, 1e-5, 0.99999))


def _build_gaussian_pyramid_3ch(img_gpu, n_levels):
    """Build Gaussian pyramid for 3-channel image. Returns list of GPU buffers."""
    pyramid = [img_gpu]
    for lvl in range(n_levels - 1):
        src = pyramid[-1]
        h, w = src.shape[0], src.shape[1]
        nh, nw = h // 2, w // 2
        if nh < 2 or nw < 2:
            break
        dst = common.get_temp_buffer((nh, nw, 3), ti.f32)
        _downsample_2x_3ch_kernel(src, dst)
        pyramid.append(dst)
    return pyramid


def _build_gaussian_pyramid_1ch(img_gpu, n_levels):
    """Build Gaussian pyramid for single-channel image. Returns list of GPU buffers."""
    pyramid = [img_gpu]
    for lvl in range(n_levels - 1):
        src = pyramid[-1]
        h, w = src.shape[0], src.shape[1]
        nh, nw = h // 2, w // 2
        if nh < 2 or nw < 2:
            break
        dst = common.get_temp_buffer((nh, nw), ti.f32)
        _downsample_2x_1ch_kernel(src, dst)
        pyramid.append(dst)
    return pyramid


def _build_laplacian_pyramid_3ch(img_gpu, n_levels):
    """Build Laplacian pyramid for 3-channel image."""
    gauss_pyr = _build_gaussian_pyramid_3ch(img_gpu, n_levels)
    lap_pyr = []
    for lvl in range(len(gauss_pyr) - 1):
        src = gauss_pyr[lvl]
        h, w = src.shape[0], src.shape[1]
        # Upsample coarser level to current size
        upsampled = common.get_temp_buffer((h, w, 3), ti.f32)
        _upsample_2x_3ch_kernel(gauss_pyr[lvl + 1], upsampled)
        # Laplacian = current - upsampled
        lap = common.get_temp_buffer((h, w, 3), ti.f32)
        _subtract_kernel(src, upsampled, lap)
        common.release_temp_buffer(upsampled)
        lap_pyr.append(lap)
    # Last level is the coarsest Gaussian (residual)
    lap_pyr.append(gauss_pyr[-1])
    return lap_pyr


def _reconstruct_from_laplacian(lap_pyr):
    """Reconstruct image from Laplacian pyramid."""
    result = lap_pyr[-1]
    for lvl in range(len(lap_pyr) - 2, -1, -1):
        h, w = lap_pyr[lvl].shape[0], lap_pyr[lvl].shape[1]
        upsampled = common.get_temp_buffer((h, w, 3), ti.f32)
        _upsample_2x_3ch_kernel(result, upsampled)
        _add_3ch_kernel(upsampled, lap_pyr[lvl])
        if lvl < len(lap_pyr) - 1:
            common.release_temp_buffer(result)
        result = upsampled
    return result


# =============================================================================
# Public API (JIT)
# =============================================================================

@ti_thread
def hdr_fuse(
    frames,
    noise_sigmas=None,
    noise_power=2.0,
    exposure_sigma=0.2,
    exposure_power=1.0,
    detail_power=1.0,
    saturation_power=1.0,
    n_levels=None,
    noise_estimator=None,
):
    """
    HDR Exposure Fusion with noise-aware pixel selection.

    Merges multiple differently-exposed frames into a single well-exposed,
    noise-suppressed, detail-preserved image using Laplacian pyramid blending
    with noise-aware weight maps.

    Args:
        frames: List of (H, W, 3) float32 images in [0, 1] range.
            Or list of (H, W) grayscale float32 images.
        noise_sigmas: List of noise sigma per frame (auto-estimated if None).
        noise_power: Power for noise weight (higher = stronger noise priority).
            Default 2.0 — noise is the dominant factor.
        exposure_sigma: Gaussian width for well-exposedness (default 0.2).
        exposure_power: Power for exposure weight (default 1.0).
        detail_power: Power for contrast/detail weight (default 1.0).
        saturation_power: Power for saturation weight (default 1.0).
        n_levels: Number of pyramid levels (auto-calculated if None).
        noise_estimator: Optional external estimator with an ``estimate`` method.

    Returns:
        Fused image (H, W, 3) or (H, W) float32 in [0, 1].
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    n_frames = len(frames)
    if n_frames == 0:
        raise ValueError("No frames provided")
    if n_frames == 1:
        return frames[0].copy()

    is_grayscale = frames[0].ndim == 2
    h, w = frames[0].shape[:2]

    # Auto pyramid levels
    if n_levels is None:
        n_levels = max(2, min(6, int(np.log2(min(h, w))) - 3))

    # --- Step 1: Estimate noise per frame ---
    if noise_sigmas is None:
        noise_sigmas = []
        for frame in frames:
            if is_grayscale:
                gray = frame.astype(np.float32)
            else:
                gray = (0.299 * frame[:, :, 0] + 0.587 * frame[:, :, 1] + 0.114 * frame[:, :, 2]).astype(np.float32)
            if noise_estimator is not None:
                sigma = noise_estimator.estimate(gray)
            else:
                sigma = _estimate_noise_sigma(gray)
            noise_sigmas.append(sigma)

    # --- Step 2: Compute weight maps ---
    weight_maps = []
    for i, frame in enumerate(frames):
        frame_f32 = frame.astype(np.float32)
        if is_grayscale:
            # Convert to 3ch for uniform processing
            frame_rgb = np.stack([frame_f32, frame_f32, frame_f32], axis=-1)
            gray = frame_f32
        else:
            frame_rgb = frame_f32
            gray = (0.299 * frame_f32[:, :, 0] + 0.587 * frame_f32[:, :, 1] + 0.114 * frame_f32[:, :, 2]).astype(np.float32)

        # Laplacian for contrast
        lap_gray = _compute_laplacian(gray)

        # Upload to GPU
        rgb_gpu, _ = common.ensure_taichi_field(frame_rgb, dtype=ti.f32)
        lap_gpu, _ = common.ensure_taichi_field(lap_gray, dtype=ti.f32)
        w_gpu = common.get_temp_buffer((h, w), ti.f32)

        _compute_weight_kernel(
            rgb_gpu, lap_gpu, w_gpu, h, w,
            float(noise_sigmas[i]), float(noise_power),
            float(exposure_sigma), float(exposure_power),
            float(detail_power), float(saturation_power),
        )

        w_np = w_gpu.to_numpy()
        common.release_temp_buffer(w_gpu)
        weight_maps.append(w_np)

    # --- Step 3: Normalize weights ---
    weights_stack = np.stack(weight_maps, axis=0).astype(np.float32)  # (N, H, W)
    weights_gpu, _ = common.ensure_taichi_field(weights_stack, dtype=ti.f32)
    _normalize_weights_kernel(weights_gpu, h, w, n_frames)
    weights_normalized = weights_gpu.to_numpy()

    # Build Gaussian pyramids for weight maps
    weight_gauss_pyrs = []
    for i in range(n_frames):
        w_i_gpu, _ = common.ensure_taichi_field(weights_normalized[i], dtype=ti.f32)
        w_pyr = _build_gaussian_pyramid_1ch(w_i_gpu, n_levels)
        weight_gauss_pyrs.append(w_pyr)

    # --- Step 4: Build Laplacian pyramids for each frame ---
    frame_lap_pyrs = []
    for frame in frames:
        frame_f32 = frame.astype(np.float32)
        if is_grayscale:
            frame_rgb = np.stack([frame_f32, frame_f32, frame_f32], axis=-1)
        else:
            frame_rgb = frame_f32
        frame_gpu, _ = common.ensure_taichi_field(frame_rgb, dtype=ti.f32)
        lap_pyr = _build_laplacian_pyramid_3ch(frame_gpu, n_levels)
        frame_lap_pyrs.append(lap_pyr)

    # --- Step 5: Blend Laplacian pyramids ---
    actual_levels = len(frame_lap_pyrs[0])
    blended_pyr = []
    for lvl in range(actual_levels):
        h_lvl = frame_lap_pyrs[0][lvl].shape[0]
        w_lvl = frame_lap_pyrs[0][lvl].shape[1]
        result_lvl = common.get_temp_buffer((h_lvl, w_lvl, 3), ti.f32)
        # Zero initialize
        result_lvl.from_numpy(np.zeros((h_lvl, w_lvl, 3), dtype=np.float32))

        for i in range(n_frames):
            w_lvl_gpu = weight_gauss_pyrs[i][min(lvl, len(weight_gauss_pyrs[i]) - 1)]
            _add_weighted_laplacian_kernel(frame_lap_pyrs[i][lvl], w_lvl_gpu, result_lvl)
        blended_pyr.append(result_lvl)

    # --- Step 6: Reconstruct ---
    result_gpu = _reconstruct_from_laplacian(blended_pyr)
    result_np = result_gpu.to_numpy()

    # --- Cleanup ---
    for pyr in frame_lap_pyrs:
        for buf in pyr:
            common.release_temp_buffer(buf)
    for pyr in weight_gauss_pyrs:
        for buf in pyr:
            common.release_temp_buffer(buf)
    for buf in blended_pyr:
        common.release_temp_buffer(buf)
    common.release_temp_buffer(result_gpu)

    # Clamp to [0, 1]
    result_np = np.clip(result_np, 0.0, 1.0)

    if is_grayscale:
        return result_np[:, :, 0]
    return result_np


@ti_thread
def hdr_fuse_simple(
    frames,
    noise_sigmas=None,
    noise_power=2.0,
    exposure_sigma=0.2,
    n_levels=None,
):
    """
    Simplified HDR Fusion API with sensible defaults.

    Args:
        frames: List of (H, W, 3) float32 images in [0, 1].
        noise_sigmas: Optional list of noise levels per frame.
        noise_power: Noise priority (default 2.0 = high priority).
        exposure_sigma: Well-exposedness width (default 0.2).
        n_levels: Pyramid levels (auto if None).

    Returns:
        Fused image (H, W, 3) float32 in [0, 1].
    """
    return hdr_fuse(
        frames,
        noise_sigmas=noise_sigmas,
        noise_power=noise_power,
        exposure_sigma=exposure_sigma,
        n_levels=n_levels,
    )
