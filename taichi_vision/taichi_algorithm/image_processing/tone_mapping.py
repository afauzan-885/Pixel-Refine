"""
Tone Mapping & Gamma Correction - Taichi GPU
===============================================
Implements tone mapping operators inspired by Google Camera HDR+ pipeline.

Algorithms:
  1. Reinhard Global Tone Mapping (2002)
  2. sRGB Gamma Curve (IEC 61966-2-1)
  3. Local Laplacian Tone Mapping (Google HDR+ inspired)
     - Simulates brighter exposure
     - Gaussian-weighted blending with Laplacian pyramid
     - Iterative application for high-contrast scenes
  4. Global Contrast Adjustment

Google HDR+ Tone Mapping Approach:
  "To apply tone mapping, we simulate a more brightly exposed image and
  weight the pixels of the brighter and darker images according to a normal
  distribution -- here the normal distribution represents the ideal pixel
  value distribution of a well-exposed image. The weights are then applied
  to the two images using a Laplacian pyramid, which prevents hard edges
  and haloing around transitions between dark and bright portions of the
  scene. We apply this algorithm iteratively on high-contrast scenes."

References:
  - Reinhard et al., "Photographic Tone Reproduction for Digital Images", 2002
  - Hasinoff et al., "Burst Photography for High Dynamic Range and Low-Light
    Imaging on Mobile Cameras", Google 2016
  - Paris et al., "Local Laplacian Filters: Edge-aware Image Processing
    with a Laplacian Pyramid", 2011

Usage (JIT):
    from taichi_vision.taichi_algorithm import reinhard_tone_map, srgb_gamma
    from taichi_vision.taichi_algorithm import local_tone_map
    result = reinhard_tone_map(hdr_image, key=0.18)
    result = srgb_gamma(result)
    result = local_tone_map(hdr_image)

Usage (AOT):
    import taichi_vision.taichi_aot as ta
    result = ta.tone_map(hdr_image, method='local')
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
    def _compute_luminance_kernel(
        img: ti.types.ndarray(dtype=ti.f32, ndim=3),
        lum: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32, w: ti.i32,
    ):
        """Compute luminance from RGB: L = 0.2126R + 0.7152G + 0.0722B (ITU-R BT.709)."""
        for y, x in ti.ndrange(h, w):
            lum[y, x] = (
                0.2126 * img[y, x, 0] +
                0.7152 * img[y, x, 1] +
                0.0722 * img[y, x, 2]
            )

    @ti.kernel
    def _reinhard_global_kernel(
        img: ti.types.ndarray(dtype=ti.f32, ndim=3),
        lum: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32, w: ti.i32,
        key: ti.f32,
        lum_white: ti.f32,
        epsilon: ti.f32,
    ):
        """Reinhard global tone mapping.
        Formula: L_mapped = (key / L_avg) * L / (1 + (key / L_avg) * L)
        With burn-out protection: L_final = L_mapped * (1 + L_mapped/L_white²) / (1 + L_mapped)
        """
        # Compute log-average luminance
        log_sum = 0.0
        for y, x in ti.ndrange(h, w):
            log_sum += ti.log(lum[y, x] + epsilon)
        log_avg = ti.exp(log_sum / float(h * w))

        scale = key / (log_avg + epsilon)
        white_sq = lum_white * lum_white

        for y, x in ti.ndrange(h, w):
            L = lum[y, x]
            L_mapped = (scale * L) / (1.0 + scale * L)
            # Burn-out protection (soft highlight compression)
            L_final = L_mapped * (1.0 + L_mapped / white_sq) / (1.0 + L_mapped)

            # Preserve color ratios
            if L > epsilon:
                ratio = L_final / L
                dst[y, x, 0] = ti.max(0.0, ti.min(1.0, img[y, x, 0] * ratio))
                dst[y, x, 1] = ti.max(0.0, ti.min(1.0, img[y, x, 1] * ratio))
                dst[y, x, 2] = ti.max(0.0, ti.min(1.0, img[y, x, 2] * ratio))
            else:
                dst[y, x, 0] = 0.0
                dst[y, x, 1] = 0.0
                dst[y, x, 2] = 0.0

    @ti.kernel
    def _srgb_gamma_kernel(
        img: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32, w: ti.i32,
        gamma: ti.f32,
    ):
        """Apply gamma correction (sRGB-like curve).
        Linear → sRGB: if x <= 0.0031308: 12.92*x else: 1.055*x^(1/2.4) - 0.055
        Simplified: x^(1/gamma) where gamma ≈ 2.2
        """
        inv_gamma = 1.0 / gamma
        for y, x, c in ti.ndrange(h, w, 3):
            val = img[y, x, c]
            val = ti.max(0.0, ti.min(1.0, val))
            # sRGB transfer function
            if val <= 0.0031308:
                dst[y, x, c] = 12.92 * val
            else:
                dst[y, x, c] = 1.055 * ti.pow(val, inv_gamma) - 0.055

    @ti.kernel
    def _srgb_gamma_simple_kernel(
        img: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32, w: ti.i32,
        gamma: ti.f32,
    ):
        """Simple gamma correction: x^(1/gamma)."""
        inv_gamma = 1.0 / gamma
        for y, x, c in ti.ndrange(h, w, 3):
            val = img[y, x, c]
            dst[y, x, c] = ti.pow(ti.max(0.0, ti.min(1.0, val)), inv_gamma)

    @ti.kernel
    def _simulate_exposure_kernel(
        img: ti.types.ndarray(dtype=ti.f32, ndim=3),
        bright: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32, w: ti.i32,
        gain: ti.f32,
    ):
        """Simulate brighter exposure by multiplying with gain factor."""
        for y, x, c in ti.ndrange(h, w, 3):
            bright[y, x, c] = ti.min(1.0, img[y, x, c] * gain)

    @ti.kernel
    def _compute_blend_weight_kernel(
        lum: ti.types.ndarray(dtype=ti.f32, ndim=2),
        weight: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32, w: ti.i32,
        target_lum: ti.f32,
        sigma: ti.f32,
    ):
        """Compute Gaussian weight based on closeness to target luminance.
        Weight = exp(-(L - target)² / (2σ²))
        """
        for y, x in ti.ndrange(h, w):
            L = lum[y, x]
            weight[y, x] = ti.exp(-(L - target_lum) * (L - target_lum) / (2.0 * sigma * sigma))

    @ti.kernel
    def _weighted_blend_kernel(
        img_dark: ti.types.ndarray(dtype=ti.f32, ndim=3),
        img_bright: ti.types.ndarray(dtype=ti.f32, ndim=3),
        w_dark: ti.types.ndarray(dtype=ti.f32, ndim=2),
        w_bright: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32, w: ti.i32,
    ):
        """Blend two images using per-pixel weights: dst = (w_d*dark + w_b*bright) / (w_d + w_b)."""
        for y, x, c in ti.ndrange(h, w, 3):
            wd = w_dark[y, x]
            wb = w_bright[y, x]
            total = wd + wb
            if total > 1e-8:
                dst[y, x, c] = (wd * img_dark[y, x, c] + wb * img_bright[y, x, c]) / total
            else:
                dst[y, x, c] = img_dark[y, x, c]

    @ti.kernel
    def _contrast_adjust_kernel(
        img: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32, w: ti.i32,
        contrast: ti.f32,
        brightness: ti.f32,
    ):
        """Global contrast and brightness adjustment.
        dst = clamp(contrast * (img - 0.5) + 0.5 + brightness, 0, 1)
        """
        for y, x, c in ti.ndrange(h, w, 3):
            val = img[y, x, c]
            dst[y, x, c] = ti.max(0.0, ti.min(1.0, contrast * (val - 0.5) + 0.5 + brightness))

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
        """Gaussian 2x downsampling for single-channel."""
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
        """Bilinear 2x upsampling for 3-channel images."""
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
                dst[r, c, ch] = (
                    src[y0, x0, ch] * (1 - fy) * (1 - fx) +
                    src[y0, x1, ch] * (1 - fy) * fx +
                    src[y1, x0, ch] * fy * (1 - fx) +
                    src[y1, x1, ch] * fy * fx
                ) * 4.0

    @ti.kernel
    def _upsample_2x_1ch_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
    ):
        """Bilinear 2x upsampling for single-channel."""
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
    def _subtract_3ch_kernel(
        img: ti.types.ndarray(dtype=ti.f32, ndim=3),
        upsampled: ti.types.ndarray(dtype=ti.f32, ndim=3),
        lap: ti.types.ndarray(dtype=ti.f32, ndim=3),
    ):
        """Laplacian = image - upsampled(coarser)."""
        for y, x, c in ti.ndrange(img.shape[0], img.shape[1], img.shape[2]):
            lap[y, x, c] = img[y, x, c] - upsampled[y, x, c]

    @ti.kernel
    def _add_3ch_kernel(
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
    ):
        """Add src to dst element-wise."""
        for y, x, c in ti.ndrange(dst.shape[0], dst.shape[1], dst.shape[2]):
            dst[y, x, c] += src[y, x, c]


# =============================================================================
# Helper Functions
# =============================================================================

def _build_laplacian_pyramid_3ch(img_gpu, n_levels):
    """Build Laplacian pyramid for 3-channel image."""
    gauss_pyr = [img_gpu]
    for _ in range(n_levels - 1):
        src = gauss_pyr[-1]
        h, w = src.shape[0], src.shape[1]
        nh, nw = h // 2, w // 2
        if nh < 2 or nw < 2:
            break
        dst = common.get_temp_buffer((nh, nw, 3), ti.f32)
        _downsample_2x_3ch_kernel(src, dst)
        gauss_pyr.append(dst)

    lap_pyr = []
    for lvl in range(len(gauss_pyr) - 1):
        src = gauss_pyr[lvl]
        h, w = src.shape[0], src.shape[1]
        upsampled = common.get_temp_buffer((h, w, 3), ti.f32)
        _upsample_2x_3ch_kernel(gauss_pyr[lvl + 1], upsampled)
        lap = common.get_temp_buffer((h, w, 3), ti.f32)
        _subtract_3ch_kernel(src, upsampled, lap)
        common.release_temp_buffer(upsampled)
        lap_pyr.append(lap)
    lap_pyr.append(gauss_pyr[-1])
    return lap_pyr


def _build_gaussian_pyramid_1ch(img_gpu, n_levels):
    """Build Gaussian pyramid for single-channel image."""
    pyramid = [img_gpu]
    for _ in range(n_levels - 1):
        src = pyramid[-1]
        h, w = src.shape[0], src.shape[1]
        nh, nw = h // 2, w // 2
        if nh < 2 or nw < 2:
            break
        dst = common.get_temp_buffer((nh, nw), ti.f32)
        _downsample_2x_1ch_kernel(src, dst)
        pyramid.append(dst)
    return pyramid


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
def reinhard_tone_map(img, key=0.18, lum_white=1.0, epsilon=1e-6):
    """
    Reinhard global tone mapping operator.

    Based on: "Photographic Tone Reproduction for Digital Images" (Reinhard et al., 2002)

    Args:
        img: Input image (H, W, 3) float32 in [0, 1] or higher dynamic range.
        key: Key value controlling overall brightness (default 0.18 = middle gray).
             Higher = brighter result.
        lum_white: Minimum luminance that maps to pure white (default 1.0).
                   Lower values compress highlights more.
        epsilon: Small value to avoid log(0).

    Returns:
        Tone-mapped image (H, W, 3) float32 in [0, 1].
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    img_np = img.astype(np.float32) if isinstance(img, np.ndarray) else img
    h, w = img_np.shape[:2]

    img_gpu, _ = common.ensure_taichi_field(img_np, dtype=ti.f32)
    lum_gpu = common.get_temp_buffer((h, w), ti.f32)
    dst_gpu = common.get_temp_buffer((h, w, 3), ti.f32)

    _compute_luminance_kernel(img_gpu, lum_gpu, h, w)
    _reinhard_global_kernel(img_gpu, lum_gpu, dst_gpu, h, w,
                            float(key), float(lum_white), float(epsilon))

    result = dst_gpu.to_numpy()
    common.release_temp_buffer(lum_gpu)
    common.release_temp_buffer(dst_gpu)
    return np.clip(result, 0.0, 1.0)


@ti_thread
def srgb_gamma(img, gamma=2.2, use_srgb_curve=True):
    """
    Apply gamma correction (sRGB transfer function).

    Args:
        img: Input image (H, W, 3) float32 in [0, 1].
        gamma: Gamma value (default 2.2 for sRGB).
        use_srgb_curve: If True, use exact sRGB transfer function.
                        If False, use simple x^(1/gamma).

    Returns:
        Gamma-corrected image (H, W, 3) float32 in [0, 1].
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    img_np = img.astype(np.float32) if isinstance(img, np.ndarray) else img
    h, w = img_np.shape[:2]

    img_gpu, _ = common.ensure_taichi_field(img_np, dtype=ti.f32)
    dst_gpu = common.get_temp_buffer((h, w, 3), ti.f32)

    if use_srgb_curve:
        _srgb_gamma_kernel(img_gpu, dst_gpu, h, w, float(gamma))
    else:
        _srgb_gamma_simple_kernel(img_gpu, dst_gpu, h, w, float(gamma))

    result = dst_gpu.to_numpy()
    common.release_temp_buffer(dst_gpu)
    return np.clip(result, 0.0, 1.0)


@ti_thread
def local_tone_map(
    img,
    gain=2.0,
    target_lum=0.5,
    sigma=0.3,
    n_levels=None,
    n_iterations=2,
    apply_gamma=True,
    gamma=2.2,
):
    """
    Local Laplacian Tone Mapping (Google HDR+ inspired).

    Simulates a brighter exposure and blends with the original using
    Laplacian pyramid blending with Gaussian luminance weights.
    Iteratively applied for high-contrast scenes.

    Google HDR+ approach:
    "We simulate a more brightly exposed image and weight the pixels
    of the brighter and darker images according to a normal distribution.
    The weights are applied using a Laplacian pyramid, which prevents
    hard edges and haloing."

    Args:
        img: Input image (H, W, 3) float32 in [0, 1].
        gain: Exposure gain for simulated brighter image (default 2.0 = +1 EV).
        target_lum: Target luminance for Gaussian weight (default 0.5 = mid-gray).
        sigma: Width of Gaussian weight function (default 0.3).
        n_levels: Number of pyramid levels (auto-calculated if None).
        n_iterations: Number of iterative applications (default 2).
            More iterations = stronger compression for high-contrast scenes.
        apply_gamma: Apply sRGB gamma correction after tone mapping.
        gamma: Gamma value for sRGB correction.

    Returns:
        Tone-mapped image (H, W, 3) float32 in [0, 1].
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    img_np = img.astype(np.float32) if isinstance(img, np.ndarray) else img
    h, w = img_np.shape[:2]

    if n_levels is None:
        n_levels = max(2, min(6, int(np.log2(min(h, w))) - 3))

    result_np = img_np.copy()

    for iteration in range(n_iterations):
        result_gpu, _ = common.ensure_taichi_field(result_np, dtype=ti.f32)

        # Step 1: Simulate brighter exposure
        bright_gpu = common.get_temp_buffer((h, w, 3), ti.f32)
        _simulate_exposure_kernel(result_gpu, bright_gpu, h, w, float(gain))

        # Step 2: Compute luminance for both versions
        lum_dark_gpu = common.get_temp_buffer((h, w), ti.f32)
        lum_bright_gpu = common.get_temp_buffer((h, w), ti.f32)
        _compute_luminance_kernel(result_gpu, lum_dark_gpu, h, w)
        _compute_luminance_kernel(bright_gpu, lum_bright_gpu, h, w)

        # Step 3: Compute blend weights (Gaussian on luminance)
        w_dark_gpu = common.get_temp_buffer((h, w), ti.f32)
        w_bright_gpu = common.get_temp_buffer((h, w), ti.f32)
        _compute_blend_weight_kernel(lum_dark_gpu, w_dark_gpu, h, w,
                                     float(target_lum), float(sigma))
        _compute_blend_weight_kernel(lum_bright_gpu, w_bright_gpu, h, w,
                                     float(target_lum), float(sigma))

        # Step 4: Build Laplacian pyramids for both images
        lap_dark = _build_laplacian_pyramid_3ch(result_gpu, n_levels)
        lap_bright = _build_laplacian_pyramid_3ch(bright_gpu, n_levels)

        # Step 5: Build Gaussian pyramids for weights
        gauss_w_dark = _build_gaussian_pyramid_1ch(w_dark_gpu, n_levels)
        gauss_w_bright = _build_gaussian_pyramid_1ch(w_bright_gpu, n_levels)

        # Step 6: Blend at each Laplacian level
        actual_levels = len(lap_dark)
        blended_pyr = []
        for lvl in range(actual_levels):
            h_lvl = lap_dark[lvl].shape[0]
            w_lvl = lap_dark[lvl].shape[1]
            result_lvl = common.get_temp_buffer((h_lvl, w_lvl, 3), ti.f32)
            result_lvl.from_numpy(np.zeros((h_lvl, w_lvl, 3), dtype=np.float32))

            # Weighted blend of Laplacian levels
            wd = gauss_w_dark[min(lvl, len(gauss_w_dark) - 1)]
            wb = gauss_w_bright[min(lvl, len(gauss_w_bright) - 1)]
            _weighted_blend_kernel(lap_dark[lvl], lap_bright[lvl], wd, wb,
                                   result_lvl, h_lvl, w_lvl)
            blended_pyr.append(result_lvl)

        # Step 7: Reconstruct
        result_gpu_new = _reconstruct_from_laplacian(blended_pyr)
        result_np = result_gpu_new.to_numpy()
        result_np = np.clip(result_np, 0.0, 1.0)

        # Cleanup
        for buf in [result_gpu, bright_gpu, lum_dark_gpu, lum_bright_gpu,
                    w_dark_gpu, w_bright_gpu, result_gpu_new]:
            common.release_temp_buffer(buf)
        for pyr in [lap_dark, lap_bright, gauss_w_dark, gauss_w_bright]:
            for buf in pyr:
                common.release_temp_buffer(buf)
        for buf in blended_pyr:
            common.release_temp_buffer(buf)

    # Optional gamma correction
    if apply_gamma:
        result_np = srgb_gamma(result_np, gamma=gamma)

    return result_np


@ti_thread
def contrast_adjust(img, contrast=1.0, brightness=0.0):
    """
    Global contrast and brightness adjustment.

    Args:
        img: Input image (H, W, 3) float32 in [0, 1].
        contrast: Contrast multiplier (default 1.0 = no change). >1 = more contrast.
        brightness: Brightness offset (default 0.0 = no change). Positive = brighter.

    Returns:
        Adjusted image (H, W, 3) float32 in [0, 1].
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    img_np = img.astype(np.float32) if isinstance(img, np.ndarray) else img
    h, w = img_np.shape[:2]

    img_gpu, _ = common.ensure_taichi_field(img_np, dtype=ti.f32)
    dst_gpu = common.get_temp_buffer((h, w, 3), ti.f32)

    _contrast_adjust_kernel(img_gpu, dst_gpu, h, w, float(contrast), float(brightness))

    result = dst_gpu.to_numpy()
    common.release_temp_buffer(dst_gpu)
    return np.clip(result, 0.0, 1.0)


@ti_thread
def tone_map(
    img,
    method='local',
    key=0.18,
    lum_white=1.0,
    gain=2.0,
    target_lum=0.5,
    sigma=0.3,
    n_iterations=2,
    apply_gamma=True,
    gamma=2.2,
    contrast=1.0,
    brightness=0.0,
):
    """
    Unified tone mapping API.

    Args:
        img: Input image (H, W, 3) float32 in [0, 1].
        method: 'reinhard' (global), 'local' (Laplacian pyramid, default),
                or 'simple' (gamma only).
        key: Reinhard key value (default 0.18).
        lum_white: Reinhard white point (default 1.0).
        gain: Exposure gain for local tone mapping (default 2.0).
        target_lum: Target luminance for local blending (default 0.5).
        sigma: Gaussian weight width for local blending (default 0.3).
        n_iterations: Iterative applications for local mode (default 2).
        apply_gamma: Apply sRGB gamma correction (default True).
        gamma: Gamma value (default 2.2).
        contrast: Global contrast adjustment (default 1.0 = no change).
        brightness: Global brightness offset (default 0.0).

    Returns:
        Tone-mapped image (H, W, 3) float32 in [0, 1].
    """
    if method == 'reinhard':
        result = reinhard_tone_map(img, key=key, lum_white=lum_white)
        if apply_gamma:
            result = srgb_gamma(result, gamma=gamma)
    elif method == 'local':
        result = local_tone_map(
            img, gain=gain, target_lum=target_lum, sigma=sigma,
            n_iterations=n_iterations, apply_gamma=apply_gamma, gamma=gamma,
        )
    else:  # simple
        result = img.astype(np.float32) if isinstance(img, np.ndarray) else img
        result = np.clip(result, 0.0, 1.0)
        if apply_gamma:
            result = srgb_gamma(result, gamma=gamma)

    if contrast != 1.0 or brightness != 0.0:
        result = contrast_adjust(result, contrast=contrast, brightness=brightness)

    return result
