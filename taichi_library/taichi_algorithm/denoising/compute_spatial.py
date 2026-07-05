"""
Compute Spatial Similarity - Taichi GPU
=========================================
GPU-accelerated spatial similarity weight map computation.
Based on hybrid gradient MAD (Mean Absolute Difference) with coarse-to-fine
tile-based analysis for ghost rejection in multi-frame stacking.

Parity: Identical to compute_spatial.py + block_matching.py original.

Usage (JIT):
    from taichi_library.taichi_algorithm import compute_spatial_weight
    weight_map = compute_spatial_weight(ref_gray, comp_gray, noise_sigma=0.02)

Usage (AOT):
    import taichi_library.taichi_aot as ta
    weight_map = ta.spatial_similarity(ref_img, comp_img)
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
# Inlined Block Matching Device Functions (from block_matching.py)
# =============================================================================

if TAICHI_AVAILABLE:

    @ti.func
    def _fast_tanh(x: float) -> float:
        """Fast Tanh approximation matching C++ Padé approximation."""
        res = 0.0
        if x > 3.0:
            res = 1.0
        elif x < -3.0:
            res = -1.0
        else:
            x2 = x * x
            res = x * (27.0 + x2) / (27.0 + 9.0 * x2)
        return res

    @ti.func
    def _calculate_match_confidence(
        mad_score: float,
        noise_sigma: float,
        motion_sensitivity: float,
        noise_offset_factor: float,
    ) -> float:
        """Noise-sensitive exponential decay confidence."""
        excess_mad = ti.max(0.0, mad_score - noise_offset_factor * noise_sigma)
        return ti.exp(-excess_mad * motion_sensitivity)

    @ti.func
    def _calculate_hybrid_gradient(
        current_img: ti.template(),
        reference_img: ti.template(),
        curr_grad_x: ti.template(),
        curr_grad_y: ti.template(),
        ref_grad_x: ti.template(),
        ref_grad_y: ti.template(),
        r: int,
        c: int,
        curr_h: int,
        curr_w: int,
        h: int,
        w: int,
        noise_level: float,
        grad_weight_factor: float,
        stab_epsilon: float,
        flat_weight: float,
    ) -> float:
        """Hybrid gradient similarity score — strict 1:1 parity with C++."""
        weighted_sum = 0.0
        total_weight = 0.0

        grad_sensitivity = 202.5
        adaptive_grad_sensitivity = grad_sensitivity * (1.0 + 3.0 * flat_weight)
        structure_min_threshold_sq = 150.0

        for y in range((curr_h - 1) // 2):
            img_y = r + 1 + y * 2
            for x in range((curr_w - 1) // 2):
                img_x = c + 1 + x * 2

                p1_val = current_img[img_y, img_x]
                p2_val = reference_img[img_y, img_x]
                pixel_diff = ti.abs(p1_val - p2_val)

                adaptive_diff_threshold = ti.max(0.005, noise_level * 0.2)

                gx1 = curr_grad_x[img_y, img_x]
                gy1 = curr_grad_y[img_y, img_x]
                gx2 = ref_grad_x[img_y, img_x]
                gy2 = ref_grad_y[img_y, img_x]

                mag1_sq = gx1 * gx1 + gy1 * gy1
                mag2_sq = gx2 * gx2 + gy2 * gy2
                min_mag_sq = ti.min(mag1_sq, mag2_sq)

                tolerance_scale = ti.max(1.0, ti.min(3.0, 3.0 - 2.0 * p2_val))
                local_adaptive_diff_threshold = adaptive_diff_threshold * tolerance_scale

                noise_weight = 1.0
                if noise_level > stab_epsilon:
                    if min_mag_sq < structure_min_threshold_sq:
                        local_thr = local_adaptive_diff_threshold * 1.5
                        if pixel_diff < local_thr:
                            noise_weight = 0.05 + 0.95 * (pixel_diff / local_thr)
                        else:
                            ratio = (pixel_diff - local_thr) / local_thr
                            if ratio > 1.0:
                                ratio = 1.0
                            noise_weight = 1.0 - 0.2 * ratio
                    else:
                        if pixel_diff < local_adaptive_diff_threshold:
                            noise_weight = 1.15 + 0.15 * (1.0 - pixel_diff / local_adaptive_diff_threshold)
                        else:
                            ratio = pixel_diff / (local_adaptive_diff_threshold * 4.0)
                            if ratio > 1.0:
                                ratio = 1.0
                            noise_weight = 0.3 + 0.4 * (1.0 - ratio)

                structure_weight = 1.0
                if min_mag_sq > stab_epsilon and mag1_sq > stab_epsilon and mag2_sq > stab_epsilon:
                    dot = gx1 * gx2 + gy1 * gy2
                    cos_sim = dot / ti.sqrt(mag1_sq * mag2_sq)

                    if min_mag_sq > structure_min_threshold_sq and cos_sim < 0.2:
                        pixel_diff = pixel_diff * (1.5 - cos_sim)
                    else:
                        score = ti.max(0.0, cos_sim) * ti.sqrt(min_mag_sq)
                        structure_weight = 1.0 + grad_weight_factor * _fast_tanh(
                            score * adaptive_grad_sensitivity
                        )

                final_weight = structure_weight * noise_weight
                weighted_sum += pixel_diff * final_weight
                total_weight += final_weight

        res_val = 0.0
        if total_weight < 1e-4:
            l1_sum = 0.0
            for y in range(curr_h):
                for x in range(curr_w):
                    l1_sum += ti.abs(current_img[r + y, c + x] - reference_img[r + y, c + x])
            res_val = l1_sum / float(curr_h * curr_w)
        else:
            res_val = weighted_sum / total_weight

        return res_val


# =============================================================================
# GPU Kernels
# =============================================================================

if TAICHI_AVAILABLE:

    @ti.kernel
    def _precompute_gradients_kernel(
        img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        grad_x: ti.types.ndarray(dtype=ti.f32, ndim=2),
        grad_y: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32,
        w: ti.i32,
    ):
        """Sobel-like gradient precomputation (1:1 parity with original)."""
        for y, x in ti.ndrange(h, w):
            if 0 < y < h - 1 and 0 < x < w - 1:
                gx_center = img[y, x + 1] - img[y, x - 1]
                gx_top = img[y - 1, x + 1] - img[y - 1, x - 1]
                gx_bottom = img[y + 1, x + 1] - img[y + 1, x - 1]
                grad_x[y, x] = (gx_center + gx_top + gx_bottom) * 0.333
                grad_y[y, x] = img[y + 1, x] - img[y - 1, x]
            else:
                grad_x[y, x] = 0.0
                grad_y[y, x] = 0.0

    @ti.kernel
    def _equalize_brightness_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        ref: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32,
        w: ti.i32,
    ):
        """Global brightness equalization by mean ratio."""
        sum_ref = 0.0
        sum_src = 0.0
        for i, j in ti.ndrange(h, w):
            sum_ref += ref[i, j]
            sum_src += src[i, j]
        ratio = 1.0
        if sum_src > 1e-5:
            ratio = sum_ref / sum_src
        ratio = ti.max(0.6, ti.min(1.8, ratio))
        for i, j in ti.ndrange(h, w):
            dst[i, j] = src[i, j] * ratio

    @ti.kernel
    def _phase1_coarse_kernel(
        current_coarse: ti.types.ndarray(dtype=ti.f32, ndim=2),
        reference_coarse: ti.types.ndarray(dtype=ti.f32, ndim=2),
        coarse_grad_x: ti.types.ndarray(dtype=ti.f32, ndim=2),
        coarse_grad_y: ti.types.ndarray(dtype=ti.f32, ndim=2),
        ref_coarse_grad_x: ti.types.ndarray(dtype=ti.f32, ndim=2),
        ref_coarse_grad_y: ti.types.ndarray(dtype=ti.f32, ndim=2),
        coarse_confidence: ti.types.ndarray(dtype=ti.f32, ndim=2),
        coarse_tile_h: ti.i32,
        coarse_tile_w: ti.i32,
        h_coarse: ti.i32,
        w_coarse: ti.i32,
        noise_sigma: ti.f32,
        motion_sensitivity: ti.f32,
        noise_offset_factor: ti.f32,
    ):
        """Coarse guidance map generation at 1/4 resolution."""
        for r, c in coarse_confidence:
            tile_y = r * coarse_tile_h
            tile_x = c * coarse_tile_w
            curr_h = ti.min(coarse_tile_h, h_coarse - tile_y)
            curr_w = ti.min(coarse_tile_w, w_coarse - tile_x)
            if curr_h > 0 and curr_w > 0:
                mad_score = _calculate_hybrid_gradient(
                    current_coarse, reference_coarse,
                    coarse_grad_x, coarse_grad_y,
                    ref_coarse_grad_x, ref_coarse_grad_y,
                    tile_y, tile_x,
                    curr_h, curr_w, h_coarse, w_coarse,
                    noise_sigma, 1.0, 1e-6, 0.0,
                )
                diff_ratio = mad_score / ti.max(1e-6, noise_sigma)
                adjusted = ti.max(0.0, diff_ratio - noise_offset_factor)
                exponent = adjusted * motion_sensitivity * 0.5
                conf = 0.0
                if exponent <= 20.0:
                    conf = 1.0 / (1.0 + ti.exp(exponent - 2.0))
                coarse_confidence[r, c] = conf
            else:
                coarse_confidence[r, c] = 0.0

    @ti.kernel
    def _phase2_fine_kernel(
        current: ti.types.ndarray(dtype=ti.f32, ndim=2),
        reference: ti.types.ndarray(dtype=ti.f32, ndim=2),
        curr_grad_x: ti.types.ndarray(dtype=ti.f32, ndim=2),
        curr_grad_y: ti.types.ndarray(dtype=ti.f32, ndim=2),
        ref_grad_x: ti.types.ndarray(dtype=ti.f32, ndim=2),
        ref_grad_y: ti.types.ndarray(dtype=ti.f32, ndim=2),
        guidance_map: ti.types.ndarray(dtype=ti.f32, ndim=2),
        stability_map: ti.types.ndarray(dtype=ti.f32, ndim=2),
        weight_map_sum: ti.types.ndarray(dtype=ti.f32, ndim=2),
        base_window: ti.i32,
        row_starts: ti.types.ndarray(dtype=ti.i32, ndim=1),
        col_starts: ti.types.ndarray(dtype=ti.i32, ndim=1),
        pass_idx: ti.i32,
        tile_h: ti.i32,
        tile_w: ti.i32,
        h: ti.i32,
        w: ti.i32,
        noise_sigma: ti.f32,
        motion_sensitivity: ti.f32,
        noise_offset_factor: ti.f32,
        use_stability: ti.i32,
        use_guidance: ti.i32,
        early_exit_threshold: ti.f32,
    ):
        """Fine 4-pass sliding window weight accumulation."""
        pass_row_mod = pass_idx // 2
        pass_col_mod = pass_idx % 2
        num_rows = row_starts.shape[0]
        num_cols = col_starts.shape[0]
        limit_rows = (num_rows - pass_row_mod + 1) // 2
        limit_cols = (num_cols - pass_col_mod + 1) // 2
        for k, m in ti.ndrange(limit_rows, limit_cols):
            i = pass_row_mod + k * 2
            j = pass_col_mod + m * 2
            r = row_starts[i]
            c = col_starts[j]
            curr_h = ti.min(tile_h, h - r)
            curr_w = ti.min(tile_w, w - c)
            if curr_h > 0 and curr_w > 0:
                center_x = ti.min(c + curr_w // 2, w - 1)
                center_y = ti.min(r + curr_h // 2, h - 1)

                guidance_val = 1.0
                if use_guidance == 1:
                    guidance_val = guidance_map[center_y, center_x]
                stab_val = 1.0
                if use_stability == 1:
                    stab_val = stability_map[center_y, center_x]

                if guidance_val >= early_exit_threshold and stab_val >= early_exit_threshold:
                    # Local contrast estimation (5-point)
                    c_y = curr_h // 2
                    c_x = curr_w // 2
                    v0 = reference[r + c_y, c + c_x]
                    v1 = reference[r, c]
                    v2 = reference[r, c + curr_w - 1]
                    v3 = reference[r + curr_h - 1, c]
                    v4 = reference[r + curr_h - 1, c + curr_w - 1]

                    ref_min = ti.min(v0, ti.min(v1, ti.min(v2, ti.min(v3, v4))))
                    ref_max = ti.max(v0, ti.max(v1, ti.max(v2, ti.max(v3, v4))))
                    contrast = ref_max - ref_min

                    mean_luma = (v0 + v1 + v2 + v3 + v4) * 0.2
                    contrast_limit = 0.12 * ti.max(0.05, mean_luma)
                    contrast_range = 0.08 * ti.max(0.05, mean_luma)
                    flat_weight = ti.max(0.0, ti.min(1.0, (contrast_limit - contrast) / contrast_range))

                    mad_score = _calculate_hybrid_gradient(
                        current, reference,
                        curr_grad_x, curr_grad_y,
                        ref_grad_x, ref_grad_y,
                        r, c, curr_h, curr_w, h, w,
                        noise_sigma, 1.0, 1e-6, flat_weight,
                    )

                    confidence_fine = _calculate_match_confidence(
                        mad_score, noise_sigma, motion_sensitivity, noise_offset_factor,
                    )

                    final_conf = confidence_fine * guidance_val * stab_val

                    if final_conf >= 1e-6:
                        for y, x in ti.ndrange(curr_h, curr_w):
                            wy = 0.5 * (1.0 - ti.cos(2.0 * 3.1415926535 * float(y) / float(tile_h - 1))) if tile_h > 1 else 1.0
                            wx = 0.5 * (1.0 - ti.cos(2.0 * 3.1415926535 * float(x) / float(tile_w - 1))) if tile_w > 1 else 1.0
                            weight_map_sum[r + y, c + x] += wy * wx * final_conf

    @ti.kernel
    def _accumulate_merging_kernel(
        current_image_full: ti.types.ndarray(dtype=ti.f32, ndim=3),
        weight_map_work: ti.types.ndarray(dtype=ti.f32, ndim=2),
        final_image_sum: ti.types.ndarray(dtype=ti.f32, ndim=3),
        weight_map_sum_full: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h_full: ti.i32, w_full: ti.i32,
        h_work: ti.i32, w_work: ti.i32,
        num_channels: ti.i32,
    ):
        """Bilinear upsample work-res weights → full-res and accumulate."""
        for i, j in ti.ndrange(h_full, w_full):
            y_work_f = float(i) * float(h_work) / float(h_full)
            x_work_f = float(j) * float(w_work) / float(w_full)
            y0 = ti.max(0, ti.cast(ti.floor(y_work_f), ti.i32))
            x0 = ti.max(0, ti.cast(ti.floor(x_work_f), ti.i32))
            y1 = ti.min(y0 + 1, h_work - 1)
            x1 = ti.min(x0 + 1, w_work - 1)
            wy = y_work_f - float(y0)
            wx = x_work_f - float(x0)
            w_val = (
                (1.0 - wy) * (1.0 - wx) * weight_map_work[y0, x0] +
                (1.0 - wy) * wx * weight_map_work[y0, x1] +
                wy * (1.0 - wx) * weight_map_work[y1, x0] +
                wy * wx * weight_map_work[y1, x1]
            )
            weight_map_sum_full[i, j] += w_val
            for c in range(num_channels):
                final_image_sum[i, j, c] += current_image_full[i, j, c] * w_val


# =============================================================================
# Utility: Compute tile starts (CPU)
# =============================================================================

def _compute_tile_starts(full_size, tile_size, overlap=0.3):
    """Compute tile start positions for a dimension."""
    if tile_size >= full_size:
        return np.array([0], dtype=np.int32)
    step = max(int(tile_size * (1.0 - overlap)), 1)
    starts = []
    y = 0
    while y + tile_size <= full_size:
        starts.append(y)
        if y + tile_size == full_size:
            break
        y = min(y + step, full_size - tile_size)
    return np.array(starts, dtype=np.int32)


def _estimate_noise_sigma(gray_np):
    """Estimasi noise menggunakan Laplacian MAD.
    Parity 1:1 dengan estimate_noise_in_python() di global_feature.py.
    Formula: sigma = median(|lap - median(lap)|) * 1.4826
    """
    if gray_np is None or gray_np.size == 0:
        return 0.015
    h, w = gray_np.shape
    if h < 3 or w < 3:
        return 0.015
    lap_kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    from . import filter2d
    lap = filter2d(gray_np, lap_kernel)
    if lap is None:
        return 0.015
    median_val = np.median(lap)
    mad_value = np.median(np.abs(lap - median_val))
    estimated_sigma = mad_value * 1.4826
    return float(np.clip(estimated_sigma, 1e-5, 0.99999))


class NoiseEstimator:
    """Noise estimation dengan caching untuk menghindari kalkulasi ulang.

    Mendukung 4 mode penggunaan:
    1. Auto-estimate dari gambar referensi (sekali saja, cache otomatis)
    2. Cache reuse — ambil nilai yang sudah dihitung sebelumnya
    3. Force recalculate — paksa re-estimasi meskipun cache ada
    4. External value — terima nilai noise dari luar untuk fleksibilitas

    Usage:
        estimator = NoiseEstimator()

        # Mode 1: Auto-estimate (cache otomatis)
        sigma = estimator.estimate(ref_gray)

        # Mode 2: Reuse cache
        sigma = estimator.get_cached()  # Returns None jika belum ada

        # Mode 3: Force recalculate
        sigma = estimator.estimate(ref_gray, force=True)

        # Mode 4: External value
        estimator.set_external(0.025)
        sigma = estimator.get()  # Returns 0.025

        # Mode 5: Clear cache
        estimator.clear()
    """

    def __init__(self):
        self._cached_sigma = None
        self._external_sigma = None
        self._ref_hash = None

    def estimate(self, ref_gray, force=False):
        """Estimasi noise dari gambar referensi.

        Args:
            ref_gray: Grayscale image (H,W) float32.
            force: Jika True, paksa re-estimasi meskipun cache ada.

        Returns:
            float: Estimated noise sigma.
        """
        # External value punya prioritas tertinggi
        if self._external_sigma is not None:
            return self._external_sigma

        # Cek cache jika tidak force
        if self._cached_sigma is not None and not force:
            return self._cached_sigma

        # Hitung hash gambar untuk deteksi perubahan
        ref_hash = self._compute_hash(ref_gray)
        if self._ref_hash == ref_hash and self._cached_sigma is not None and not force:
            return self._cached_sigma

        # Estimasi noise
        self._cached_sigma = _estimate_noise_sigma(ref_gray)
        self._ref_hash = ref_hash
        return self._cached_sigma

    def get_cached(self):
        """Ambil nilai cache (None jika belum ada)."""
        return self._cached_sigma

    def get(self):
        """Ambil nilai terbaik yang tersedia (external > cache > None)."""
        if self._external_sigma is not None:
            return self._external_sigma
        return self._cached_sigma

    def set_external(self, sigma):
        """Set nilai noise external (prioritas tertinggi)."""
        self._external_sigma = float(sigma)

    def clear_external(self):
        """Hapus hanya nilai external, cache tetap dipertahankan."""
        self._external_sigma = None

    def clear(self):
        """Hapus semua cache dan external value."""
        self._cached_sigma = None
        self._external_sigma = None
        self._ref_hash = None

    def _compute_hash(self, img):
        """Hitung hash sederhana dari gambar untuk deteksi perubahan."""
        h, w = img.shape[:2]
        step_h = max(1, h // 10)
        step_w = max(1, w // 10)
        samples = img[::step_h, ::step_w].ravel()[:100]
        return hash(samples.tobytes())


# =============================================================================
# Public API (JIT)
# =============================================================================

@ti_thread
def compute_spatial_weight(
    ref_gray,
    comp_gray,
    noise_sigma=None,
    noise_estimator=None,
    noise_threshold=None,
    motion_threshold=None,
    mode='auto',
    motion_sensitivity=150.0,
    noise_offset_factor=0.15,
    tile_h=16,
    tile_w=16,
    overlap=0.3,
    equalize_brightness=True,
    early_exit_threshold=0.05,
):
    """
    Compute spatial similarity weight map between two grayscale images.
    Ghost rejection via hybrid gradient MAD analysis.

    Args:
        ref_gray: Reference image (H,W) float32 [0,1] or [0,255].
        comp_gray: Comparison image (H,W) float32 [0,1] or [0,255].
        noise_sigma: Noise level (float), 'force' string to recalculate, or None for auto.
        noise_estimator: NoiseEstimator instance (opsional, enables caching).
        noise_threshold: Explicit noise floor threshold (float or None).
            If set, overrides noise_offset_factor. Value di mana MAD dianggap noise.
            Auto: noise_sigma * noise_offset_factor (default 0.15).
        motion_threshold: Explicit motion detection threshold (float or None).
            Jika mode='manual', langsung digunakan sebagai motion_sensitivity.
            Jika mode='auto', digunakan sebagai base sensitivity + SSIM-adaptive.
        mode: 'auto' atau 'manual'.
            - 'auto': motion_threshold adaptif berdasarkan SSIM lokal per tile.
                      noise_threshold dihitung dari noise_sigma * noise_offset_factor.
            - 'manual': menggunakan motion_sensitivity dan noise_offset_factor langsung.
        motion_sensitivity: Ghost rejection aggressiveness (default 150.0, mode='manual').
        noise_offset_factor: Noise floor offset multiplier (default 0.15, mode='manual').
        tile_h, tile_w: Tile dimensions (default 16x16).
        overlap: Tile overlap ratio (default 0.3).
        equalize_brightness: Apply brightness equalization before analysis.
        early_exit_threshold: Skip tiles below this confidence.

    Returns:
        weight_map: (H, W) float32 weight map (higher = more similar).
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Ensure float32 numpy
    ref_np = ref_gray.astype(np.float32) if isinstance(ref_gray, np.ndarray) else ref_gray.to_numpy().astype(np.float32)
    comp_np = comp_gray.astype(np.float32) if isinstance(comp_gray, np.ndarray) else comp_gray.to_numpy().astype(np.float32)

    h, w = ref_np.shape[:2]

    # --- Resolusi noise_sigma ---
    if noise_estimator is not None:
        if isinstance(noise_sigma, str) and noise_sigma == 'force':
            actual_sigma = noise_estimator.estimate(ref_np, force=True)
        elif noise_sigma is not None:
            noise_estimator.set_external(float(noise_sigma))
            actual_sigma = float(noise_sigma)
        else:
            actual_sigma = noise_estimator.estimate(ref_np)
    else:
        if noise_sigma is None:
            actual_sigma = _estimate_noise_sigma(ref_np)
        elif isinstance(noise_sigma, str) and noise_sigma == 'force':
            actual_sigma = _estimate_noise_sigma(ref_np)
        else:
            actual_sigma = float(noise_sigma)

    # --- Resolusi noise_threshold dan motion_sensitivity ---
    if mode == 'auto':
        # Auto mode: noise_threshold = noise_sigma * offset_factor
        # motion_threshold digunakan sebagai base, adaptif per tile via SSIM
        actual_noise_offset = noise_threshold / actual_sigma if noise_threshold is not None and actual_sigma > 1e-8 else noise_offset_factor
        actual_motion_sens = motion_threshold if motion_threshold is not None else motion_sensitivity
    else:
        # Manual mode: gunakan parameter langsung
        actual_noise_offset = noise_threshold / actual_sigma if noise_threshold is not None and actual_sigma > 1e-8 else noise_offset_factor
        actual_motion_sens = motion_threshold if motion_threshold is not None else motion_sensitivity

    # Upload to GPU
    ref_gpu, ref_temp = common.ensure_taichi_field(ref_np, dtype=ti.f32)
    comp_gpu, comp_temp = common.ensure_taichi_field(comp_np, dtype=ti.f32)

    # Brightness equalization (optional)
    analysis_input = comp_gpu
    eq_temp = None
    if equalize_brightness:
        eq_temp = common.get_temp_buffer((h, w), ti.f32)
        _equalize_brightness_kernel(comp_gpu, ref_gpu, eq_temp, h, w)
        analysis_input = eq_temp

    # Compute tile starts
    row_starts = _compute_tile_starts(h, tile_h, overlap)
    col_starts = _compute_tile_starts(w, tile_w, overlap)
    rows_gpu = ti.ndarray(dtype=ti.i32, shape=(len(row_starts),))
    rows_gpu.from_numpy(row_starts)
    cols_gpu = ti.ndarray(dtype=ti.i32, shape=(len(col_starts),))
    cols_gpu.from_numpy(col_starts)

    # --- Phase 1: Coarse guidance map (1/4 resolution) ---
    from .interpolation.bilinear_interpolation import bilinear_resize
    from .interpolation.bicubic_interpolation import bicubic_resize

    # Downscale pyramids matching C++ AOT exactly to avoid aliasing: L0 -> L1 -> L2
    ref_l1_np = bilinear_resize(ref_np, h // 2, w // 2)
    ref_l2_np = bilinear_resize(ref_l1_np, h // 4, w // 4)
    
    comp_l1_np = bilinear_resize(analysis_input.to_numpy() if hasattr(analysis_input, "to_numpy") else comp_np, h // 2, w // 2)
    comp_l2_np = bilinear_resize(comp_l1_np, h // 4, w // 4)

    ref_l2_gpu, _ = common.ensure_taichi_field(ref_l2_np, dtype=ti.f32)
    comp_l2_gpu, _ = common.ensure_taichi_field(comp_l2_np, dtype=ti.f32)

    # Coarse gradients
    h_l2, w_l2 = ref_l2_np.shape[:2]
    ref_cgx = common.get_temp_buffer((h_l2, w_l2), ti.f32)
    ref_cgy = common.get_temp_buffer((h_l2, w_l2), ti.f32)
    comp_cgx = common.get_temp_buffer((h_l2, w_l2), ti.f32)
    comp_cgy = common.get_temp_buffer((h_l2, w_l2), ti.f32)
    _precompute_gradients_kernel(ref_l2_gpu, ref_cgx, ref_cgy, h_l2, w_l2)
    _precompute_gradients_kernel(comp_l2_gpu, comp_cgx, comp_cgy, h_l2, w_l2)

    # Coarse analysis parameters
    scale_factor = h_l2 / h
    level_tile_h = max(8, int(tile_h * scale_factor))
    level_tile_w = max(8, int(tile_w * scale_factor))
    num_tiles_h = max(1, h_l2 // level_tile_h)
    num_tiles_w = max(1, w_l2 // level_tile_w)

    coarse_conf = ti.ndarray(dtype=ti.f32, shape=(num_tiles_h, num_tiles_w))
    coarse_conf.from_numpy(np.zeros((num_tiles_h, num_tiles_w), dtype=np.float32))

    _phase1_coarse_kernel(
        comp_l2_gpu, ref_l2_gpu,
        comp_cgx, comp_cgy, ref_cgx, ref_cgy,
        coarse_conf,
        level_tile_h, level_tile_w,
        h_l2, w_l2,
        float(actual_sigma), float(actual_motion_sens), float(actual_noise_offset),
    )

    # Upsample coarse confidence to full resolution using bicubic resize matching C++ AOT
    coarse_conf_np = coarse_conf.to_numpy()
    guidance_l2_np = bicubic_resize(coarse_conf_np, h_l2, w_l2)
    guidance_np = bicubic_resize(guidance_l2_np, h, w)
    guidance_gpu, _ = common.ensure_taichi_field(guidance_np, dtype=ti.f32)

    # Cleanup coarse buffers
    for buf in [ref_l2_gpu, comp_l2_gpu, ref_cgx, ref_cgy, comp_cgx, comp_cgy]:
        common.release_temp_buffer(buf)

    # --- Phase 2: Fine analysis (4-pass sliding window) ---
    ref_grad_x = common.get_temp_buffer((h, w), ti.f32)
    ref_grad_y = common.get_temp_buffer((h, w), ti.f32)
    comp_grad_x = common.get_temp_buffer((h, w), ti.f32)
    comp_grad_y = common.get_temp_buffer((h, w), ti.f32)
    _precompute_gradients_kernel(ref_gpu, ref_grad_x, ref_grad_y, h, w)
    _precompute_gradients_kernel(analysis_input, comp_grad_x, comp_grad_y, h, w)

    weight_map = common.get_temp_buffer((h, w), ti.f32)
    # Clear weight map
    weight_map.from_numpy(np.zeros((h, w), dtype=np.float32))

    # Dummy stability map (all 1.0)
    dummy_stab = ti.ndarray(dtype=ti.f32, shape=(1, 1))
    dummy_stab.from_numpy(np.ones((1, 1), dtype=np.float32))

    # Run 4 passes
    for pass_idx in range(4):
        _phase2_fine_kernel(
            analysis_input, ref_gpu,
            comp_grad_x, comp_grad_y, ref_grad_x, ref_grad_y,
            guidance_gpu, dummy_stab, weight_map,
            0, rows_gpu, cols_gpu, pass_idx,
            tile_h, tile_w, h, w,
            float(actual_sigma), float(actual_motion_sens), float(actual_noise_offset),
            0, 1, float(early_exit_threshold),
        )

    # Cleanup
    for buf in [ref_grad_x, ref_grad_y, comp_grad_x, comp_grad_y, guidance_gpu]:
        common.release_temp_buffer(buf)
    if eq_temp is not None:
        common.release_temp_buffer(eq_temp)
    if ref_temp:
        common.release_temp_buffer(ref_gpu)
    if comp_temp:
        common.release_temp_buffer(comp_gpu)

    result = weight_map.to_numpy()
    common.release_temp_buffer(weight_map)
    return result


@ti_thread
def accumulate_spatial_merging(
    current_image_full,
    weight_map_work,
    final_image_sum,
    weight_map_sum_full,
    h_full, w_full,
    h_work, w_work,
    num_channels,
):
    """
    Accumulate weighted frame into global sum (JIT mode).
    Bilinearly upsamples work-res weights to full-res.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    curr_gpu, _ = common.ensure_taichi_field(current_image_full, dtype=ti.f32)
    weight_gpu, _ = common.ensure_taichi_field(weight_map_work, dtype=ti.f32)
    sum_gpu, _ = common.ensure_taichi_field(final_image_sum, dtype=ti.f32)
    wsum_gpu, _ = common.ensure_taichi_field(weight_map_sum_full, dtype=ti.f32)

    _accumulate_merging_kernel(
        curr_gpu, weight_gpu, sum_gpu, wsum_gpu,
        h_full, w_full, h_work, w_work, num_channels,
    )

    return sum_gpu.to_numpy(), wsum_gpu.to_numpy()
