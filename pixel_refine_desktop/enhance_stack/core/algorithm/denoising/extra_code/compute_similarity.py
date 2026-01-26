"""
Compute Similarity - Taichi GPU Migration
=========================================
1:1 Migration from similarity_spatial_merging.cpp to Taichi.
Handles brightness equalization, hierarchical motion analysis, and weight map generation.
"""

import numpy as np

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.extra_code.Compiler.similarity_metrics import (
    calculate_hybrid_gradient_mad,
)

try:
    import taichi as ti
    import taichi.math as tm
    from ...taichi_algorithm import (
        common,
        pyramid,
        bicubic_interpolation,
    )
    from ...taichi_algorithm.taichi_worker import (
        ti_thread,
        create_taichi_ndarray,
        download_taichi_ndarray,
    )

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None


if TAICHI_AVAILABLE:

    # --- KERNELS ---

    @ti.kernel
    def _phase1_coarse_analysis(
        current_coarse: ti.types.ndarray(),
        reference_coarse: ti.types.ndarray(),
        coarse_confidence: ti.types.ndarray(),
        coarse_tile_h: int,
        coarse_tile_w: int,
        h_coarse: int,
        w_coarse: int,
        noise_sigma: float,
        motion_sensitivity: float,
        noise_offset_factor: float,
    ):
        """Phase 1: Coarse analysis with simplified confidence estimation."""
        for r, c in ti.ndrange(coarse_confidence.shape[0], coarse_confidence.shape[1]):
            y = r * coarse_tile_h
            x = c * coarse_tile_w

            # Simple MAD for coarse level
            mad_score = calculate_hybrid_gradient_mad(
                current_coarse,
                reference_coarse,
                y,
                x,
                coarse_tile_h,
                coarse_tile_w,
                h_coarse,
                w_coarse,
                noise_sigma,
                1.0,
                1e-6,
            )

            # Simplified confidence formula from C++
            diff_ratio = mad_score / ti.max(1e-6, noise_sigma)
            adjusted = ti.max(0.0, diff_ratio - noise_offset_factor)
            exponent = adjusted * motion_sensitivity * 0.5

            conf = 0.0
            if exponent <= 20.0:
                conf = 1.0 / (1.0 + ti.exp(exponent - 2.0))

            coarse_confidence[r, c] = conf

    @ti.kernel
    def _phase2_fine_analysis(
        current: ti.types.ndarray(),
        reference: ti.types.ndarray(),
        guidance_map: ti.types.ndarray(),
        stability_map: ti.types.ndarray(),
        weight_map_sum: ti.types.ndarray(),
        base_window: ti.types.ndarray(),
        row_starts: ti.types.ndarray(),
        col_starts: ti.types.ndarray(),
        pass_idx: int,
        tile_h: int,
        tile_w: int,
        h: int,
        w: int,
        noise_sigma: float,
        motion_sensitivity: float,
        noise_offset_factor: float,
        use_stability: int,
    ):
        """Phase 2: Fine MAD analysis with 4-pass sliding window and accumulation."""
        pass_row_mod = pass_idx // 2
        pass_col_mod = pass_idx % 2

        num_rows = row_starts.shape[0]
        num_cols = col_starts.shape[0]

        for i, j in ti.ndrange(num_rows, num_cols):
            if i % 2 == pass_row_mod and j % 2 == pass_col_mod:
                r = row_starts[i]
                c = col_starts[j]

                curr_h = ti.min(tile_h, h - r)
                curr_w = ti.min(tile_w, w - c)

                if curr_h > 0 and curr_w > 0:
                    # 1. Calculate Fine MAD
                    mad_score = calculate_hybrid_gradient_mad(
                        current,
                        reference,
                        r,
                        c,
                        curr_h,
                        curr_w,
                        h,
                        w,
                        noise_sigma,
                        1.0,
                        1e-6,
                    )

                    # 2. Calculate Exponential Match Confidence
                    noise_offset = noise_offset_factor * noise_sigma
                    excess_mad = ti.max(0.0, mad_score - noise_offset)
                    conf_fine = ti.exp(-excess_mad * motion_sensitivity)

                    # 3. Guidance and Stability weighting
                    center_y = int(ti.min(r + curr_h // 2, h - 1))
                    center_x = int(ti.min(c + curr_w // 2, w - 1))

                    final_conf = conf_fine * guidance_map[center_y, center_x]

                    if use_stability == 1:
                        final_conf *= stability_map[center_y, center_x]

                    if final_conf >= 1e-6:
                        # 4. Global Accumulation (Equivalent to C++ accumulate_tile)
                        for dr, dc in ti.ndrange(curr_h, curr_w):
                            weight_map_sum[r + dr, c + dc] += (
                                base_window[dr, dc] * final_conf
                            )

    @ti.kernel
    def _equalize_brightness_kernel(
        src: ti.types.ndarray(),
        ref: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """Median-based gain equalization for brightness consistency."""
        sum_src = 0.0
        sum_ref = 0.0
        for r, c in ti.ndrange(h, w):
            sum_src += src[r, c]
            sum_ref += ref[r, c]

        gain = sum_ref / (sum_src + 1e-5)
        gain = tm.clamp(gain, 0.6, 1.8)

        for r, c in ti.ndrange(h, w):
            dst[r, c] = src[r, c] * gain

    return weight_map_sum
