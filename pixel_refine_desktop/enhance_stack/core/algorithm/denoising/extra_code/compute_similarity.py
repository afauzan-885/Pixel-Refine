"""
Compute Similarity - Taichi GPU Migration
=========================================
1:1 Migration from similarity_spatial_merging.cpp to Taichi.
Handles brightness equalization, hierarchical motion analysis, and weight map generation.
"""

import numpy as np
from typing import Any

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

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None

# To satisfy type checkers when TAICHI_AVAILABLE is False
_ti: Any = ti
_tm: Any = tm

if TAICHI_AVAILABLE and _ti is not None:

    # --- KERNELS ---

    @_ti.kernel
    def _phase1_coarse_analysis(
        current_coarse: _ti.types.ndarray(),
        reference_coarse: _ti.types.ndarray(),
        coarse_confidence: _ti.types.ndarray(),
        coarse_tile_h: int,
        coarse_tile_w: int,
        h_coarse: int,
        w_coarse: int,
        noise_sigma: float,
        motion_sensitivity: float,
        noise_offset_factor: float,
    ):
        """Phase 1: Coarse analysis with simplified confidence estimation."""
        for r, c in _ti.ndrange(coarse_confidence.shape[0], coarse_confidence.shape[1]):
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
            diff_ratio = mad_score / _ti.max(1e-6, noise_sigma)
            adjusted = _ti.max(0.0, diff_ratio - noise_offset_factor)
            exponent = adjusted * motion_sensitivity * 0.5

            conf = 0.0
            if exponent <= 20.0:
                conf = 1.0 / (1.0 + _ti.exp(exponent - 2.0))

            coarse_confidence[r, c] = conf

    @_ti.kernel
    def _phase2_fine_analysis(
        current: _ti.types.ndarray(),
        reference: _ti.types.ndarray(),
        guidance_map: _ti.types.ndarray(),
        stability_map: _ti.types.ndarray(),
        weight_map_sum: _ti.types.ndarray(),
        base_window: _ti.types.ndarray(),
        row_starts: _ti.types.ndarray(),
        col_starts: _ti.types.ndarray(),
        pass_idx: int,
        tile_h: int,
        tile_w: int,
        h: int,
        w: int,
        noise_sigma: float,
        motion_sensitivity: float,
        noise_offset_factor: float,
        use_stability: int,
        use_guidance: int,
    ):
        """Phase 2: Fine MAD analysis with 4-pass sliding window and accumulation."""
        pass_row_mod = pass_idx // 2
        pass_col_mod = pass_idx % 2

        num_rows = row_starts.shape[0]
        num_cols = col_starts.shape[0]

        for i, j in _ti.ndrange(num_rows, num_cols):
            if i % 2 == pass_row_mod and j % 2 == pass_col_mod:
                r = row_starts[i]
                c = col_starts[j]

                curr_h = _ti.min(tile_h, h - r)
                curr_w = _ti.min(tile_w, w - c)

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
                    excess_mad = _ti.max(0.0, mad_score - noise_offset)
                    conf_fine = _ti.exp(-excess_mad * motion_sensitivity)

                    # 3. Guidance and Stability weighting
                    center_y = int(_ti.min(r + curr_h // 2, h - 1))
                    center_x = int(_ti.min(c + curr_w // 2, w - 1))

                    final_conf = conf_fine
                    if use_guidance == 1:
                        final_conf *= guidance_map[center_y, center_x]

                    if use_stability == 1:
                        final_conf *= stability_map[center_y, center_x]

                    if final_conf >= 1e-6:
                        # 4. Global Accumulation (Equivalent to C++ accumulate_tile)
                        for dr, dc in _ti.ndrange(curr_h, curr_w):
                            weight_map_sum[r + dr, c + dc] += (
                                base_window[dr, dc] * final_conf
                            )

    @_ti.kernel
    def _equalize_brightness_kernel(
        src: _ti.types.ndarray(),
        ref: _ti.types.ndarray(),
        dst: _ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """Median-based gain equalization for brightness consistency."""
        sum_src = 0.0
        sum_ref = 0.0
        for r, c in _ti.ndrange(h, w):
            sum_src += src[r, c]
            sum_ref += ref[r, c]

        gain = sum_ref / (sum_src + 1e-5)
        gain = _tm.clamp(gain, 0.6, 1.8)

        for r, c in _ti.ndrange(h, w):
            dst[r, c] = src[r, c] * gain

    @_ti.kernel
    def _accumulate_spatial_merging_kernel(
        current_image_full: _ti.types.ndarray(),
        weight_map_work: _ti.types.ndarray(),
        final_image_sum: _ti.types.ndarray(),
        weight_map_sum_full: _ti.types.ndarray(),
        h_full: int,
        w_full: int,
        h_work: int,
        w_work: int,
        num_channels: int,
    ):
        """Upsample weight map and accumulate into global buffers."""
        for r, c in _ti.ndrange(h_full, w_full):
            # Bilinear upsampling of weight map
            fy = (float(r) + 0.5) * (float(h_work) / float(h_full)) - 0.5
            fx = (float(c) + 0.5) * (float(w_work) / float(w_full)) - 0.5

            w_val = common.bilinear_at(weight_map_work, fx, fy)

            # Accumulate
            weight_map_sum_full[r, c] += w_val
            for ch in range(num_channels):
                final_image_sum[r, c, ch] += current_image_full[r, c, ch] * w_val

    # --- INTERFACE FUNCTIONS ---

    def generate_weight_map_taichi(
        current_image,
        reference_image,
        weight_map_sum,
        base_window,
        stability_map=None,
        row_starts=None,
        col_starts=None,
        tile_h=64,
        tile_w=64,
        noise_sigma=0.01,
        motion_sensitivity=10.0,
        noise_offset_factor=1.5,
        equalize_brightness=False,
        buffer_provider="pool",
        **kwargs,
    ):
        """
        Calculates the weight map for a single frame relative to the reference.
        """
        if not TAICHI_AVAILABLE or _ti is None:
            return None

        # 1. Prepare buffers
        curr_gpu, curr_is_temp = common.ensure_taichi_field(
            current_image, dtype=_ti.f32, buffer_provider=buffer_provider
        )
        ref_gpu = reference_image  # Assumed already on GPU

        h, w = curr_gpu.shape[0], curr_gpu.shape[1]

        # 2. Reset weight map sum
        weight_map_sum.fill(0.0)

        analysis_input = None
        dummy_gpu = None
        guidance_gpu = None

        try:
            # 3. Brightness Equalization (Optional)
            analysis_input = curr_gpu
            if equalize_brightness:
                analysis_input = common.get_temp_buffer(
                    (h, w), _ti.f32, buffer_provider
                )
                _equalize_brightness_kernel(curr_gpu, ref_gpu, analysis_input, h, w)

            # 4. Hierarchical / Pass-based Analysis
            use_stability = 1 if stability_map is not None else 0
            use_guidance = 0  # Can be enabled if guidance map is provided

            # Dummy buffers for optional ndarrays (Taichi kernels require valid objects)
            if stability_map is None:
                dummy_gpu = common.get_temp_buffer((1, 1), _ti.f32, buffer_provider)
                stability_map = dummy_gpu

            guidance_gpu = dummy_gpu
            if guidance_gpu is stability_map and use_guidance == 0:
                pass  # Already using dummy
            elif guidance_gpu is None:
                guidance_gpu = common.get_temp_buffer((1, 1), _ti.f32, buffer_provider)

            for pass_idx in range(4):
                _phase2_fine_analysis(
                    analysis_input,
                    ref_gpu,
                    guidance_gpu,
                    stability_map,
                    weight_map_sum,
                    base_window,
                    row_starts,
                    col_starts,
                    pass_idx,
                    tile_h,
                    tile_w,
                    h,
                    w,
                    noise_sigma,
                    motion_sensitivity,
                    noise_offset_factor,
                    use_stability,
                    use_guidance,
                )

        finally:
            # Cleanup
            if dummy_gpu is not None:
                common.release_temp_buffer(dummy_gpu)
            if (guidance_gpu is not None) and (guidance_gpu is not dummy_gpu):
                common.release_temp_buffer(guidance_gpu)
            if equalize_brightness and analysis_input is not None:
                common.release_temp_buffer(analysis_input)
            if curr_is_temp:
                common.release_temp_buffer(curr_gpu)

    def accumulate_spatial_merging_taichi(
        current_image_full,
        weight_map_work,
        final_image_sum,
        weight_map_sum_full,
        buffer_provider="pool",
    ):
        """
        Accumulates a frame into the global sum using its processed weight map.
        Handles the resolution difference between analysis (work_res) and accumulation (full_res).
        """
        if not TAICHI_AVAILABLE or _ti is None:
            return

        h_full, w_full = final_image_sum.shape[0], final_image_sum.shape[1]
        h_work, w_work = weight_map_work.shape[0], weight_map_work.shape[1]
        num_channels = final_image_sum.shape[2]

        if h_full == 0 or w_full == 0:
            return

        # Ensure current image is on GPU
        curr_full_gpu, curr_is_temp = common.ensure_taichi_field(
            current_image_full, dtype=_ti.f32, buffer_provider=buffer_provider
        )

        try:
            _accumulate_spatial_merging_kernel(
                curr_full_gpu,
                weight_map_work,
                final_image_sum,
                weight_map_sum_full,
                h_full,
                w_full,
                h_work,
                w_work,
                num_channels,
            )
        finally:
            if curr_is_temp:
                common.release_temp_buffer(curr_full_gpu)

else:
    # Dummy interface functions for when Taichi is not available
    def generate_weight_map_taichi(*args, **kwargs):
        return None

    def accumulate_spatial_merging_taichi(*args, **kwargs):
        return None
