"""
Similarity Metrics - Taichi GPU
==============================
Modular similarity measurement functions (MAD, Hybrid Gradient, etc.)
Used for denoising weight map generation.
"""

try:
    import taichi as ti
    import taichi.math as tm

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None


# --- CONFIGURATION (1:1 with C++) ---
class SimilarityConfig:
    STABILITY_EPSILON = 1e-6
    CONFIDENCE_EPSILON = 1e-6
    GRADIENT_WEIGHT_FACTOR = 1.0
    MAD_TO_SIGMA_FACTOR = 1.4826
    STRUCTURE_THRESH_SQ = 150.0
    GRAD_SENSITIVITY = 202.5


if TAICHI_AVAILABLE:

    @ti.func
    def fast_tanh(x: float) -> float:
        x2 = x * x
        res = x * (27.0 + x2) / (27.0 + 9.0 * x2)
        return res

    @ti.func
    def calculate_hybrid_gradient_mad(
        current_img: ti.template(),
        reference_img: ti.template(),
        y: int,
        x: int,
        tile_h: int,
        tile_w: int,
        h: int,
        w: int,
        noise_level: float,
        grad_weight_factor: float,
        stab_epsilon: float,
    ) -> float:
        """
        Taichi implementation of Hybrid Gradient MAD.
        Computes gradients on-the-fly and applies structure-aware weighting.
        Identical logic to internal::calculate_hybrid_gradient_optimized in C++.
        """
        weighted_sum = 0.0
        total_weight = 0.0

        # Boundary constraints for gradient calculation (skip 1px border)
        for r in range(1, tile_h - 1):
            curr_y = y + r
            if curr_y < 1 or curr_y >= h - 1:
                continue

            for c in range(1, tile_w - 1):
                curr_x = x + c
                if curr_x < 1 or curr_x >= w - 1:
                    continue

                pixel_diff = ti.abs(
                    current_img[curr_y, curr_x] - reference_img[curr_y, curr_x]
                )

                # Optimization Constants
                adaptive_diff_threshold = ti.max(0.005, noise_level * 0.2)
                structure_min_threshold_sq = 150.0

                # --- 1:1 Gradient Calculation ---
                # ... gradients (stay 1:1 with C++ logic for base component) ...
                gx1 = (
                    (current_img[curr_y, curr_x + 1] - current_img[curr_y, curr_x - 1])
                    + (
                        current_img[curr_y - 1, curr_x + 1]
                        - current_img[curr_y - 1, curr_x - 1]
                    )
                    + (
                        current_img[curr_y + 1, curr_x + 1]
                        - current_img[curr_y + 1, curr_x - 1]
                    )
                ) * 0.333
                gx2 = (
                    (
                        reference_img[curr_y, curr_x + 1]
                        - reference_img[curr_y, curr_x - 1]
                    )
                    + (
                        reference_img[curr_y - 1, curr_x + 1]
                        - reference_img[curr_y - 1, curr_x - 1]
                    )
                    + (
                        reference_img[curr_y + 1, curr_x + 1]
                        - reference_img[curr_y + 1, curr_x - 1]
                    )
                ) * 0.333
                gy1 = current_img[curr_y + 1, curr_x] - current_img[curr_y - 1, curr_x]
                gy2 = (
                    reference_img[curr_y + 1, curr_x]
                    - reference_img[curr_y - 1, curr_x]
                )

                mag1_sq = gx1 * gx1 + gy1 * gy1
                mag2_sq = gx2 * gx2 + gy2 * gy2
                min_mag_sq = ti.min(mag1_sq, mag2_sq)

                # --- NOISE WEIGHTING (1:1 Branching Logic) ---
                noise_weight = 1.0
                if noise_level > stab_epsilon:
                    if min_mag_sq < structure_min_threshold_sq:
                        # Flat area
                        local_thr = adaptive_diff_threshold * 1.5
                        if pixel_diff < local_thr:
                            noise_weight = 0.05 + 0.95 * (pixel_diff / local_thr)
                        else:
                            ratio = (pixel_diff - local_thr) / local_thr
                            noise_weight = 1.0 - 0.2 * ti.min(ratio, 1.0)
                    else:
                        # Edge area
                        if pixel_diff < adaptive_diff_threshold:
                            noise_weight = 1.15 + 0.15 * (
                                1.0 - pixel_diff / adaptive_diff_threshold
                            )
                        else:
                            ratio = pixel_diff / (adaptive_diff_threshold * 4.0)
                            noise_weight = 0.3 + 0.4 * (1.0 - ti.min(ratio, 1.0))

                # --- STRUCTURE WEIGHTING ---
                structure_weight = 1.0
                if (
                    min_mag_sq > stab_epsilon
                    and mag1_sq > stab_epsilon
                    and mag2_sq > stab_epsilon
                ):
                    dot = gx1 * gx2 + gy1 * gy2
                    cos_sim = ti.max(0.0, dot / ti.sqrt(mag1_sq * mag2_sq))
                    score = cos_sim * ti.sqrt(min_mag_sq)
                    structure_weight = 1.0 + grad_weight_factor * fast_tanh(
                        score * SimilarityConfig.GRAD_SENSITIVITY
                    )

                final_weight = structure_weight * noise_weight
                weighted_sum += pixel_diff * final_weight
                total_weight += final_weight

        res = 0.0
        if total_weight > 1e-4:
            res = weighted_sum / total_weight
        else:
            # Fallback to simple L1
            l1_sum = 0.0
            count = 0.0
            for r, c in ti.ndrange(tile_h, tile_w):
                curr_y, curr_x = y + r, x + c
                if curr_y < h and curr_x < w:
                    l1_sum += ti.abs(
                        current_img[curr_y, curr_x] - reference_img[curr_y, curr_x]
                    )
                    count += 1.0
            res = l1_sum / ti.max(count, 1e-6)

        return res
