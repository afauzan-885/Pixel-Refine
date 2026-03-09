"""
Compute Spatial Merging - Taichi GPU Migration
=============================================
1:1 Migration from similarity_spatial_merging.cpp to Taichi.
Handles brightness equalization, hierarchical motion analysis, and spatial weight map generation.
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
        bilinear_resize,
        bicubic_resize,
    )
    from ...taichi_algorithm.taichi_worker import (
        ti_thread,
        TAICHI_AVAILABLE,
        release_taichi_ndarray,
    )

except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None
    ti_thread = lambda f: f  # No-op in case of no Taichi

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
        weight_method: int,
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
            if weight_method == 0:
                if exponent <= 20.0:
                    conf = 1.0 / (1.0 + _ti.exp(exponent - 2.0))
            else:
                # Linear / Reciprocal weighting (More forgiving)
                conf = 1.0 / (1.0 + exponent)

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
        weight_method: int,
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

                    # 2. Calculate Match Confidence
                    noise_offset = noise_offset_factor * noise_sigma
                    excess_mad = _ti.max(0.0, mad_score - noise_offset)

                    conf_fine = 0.0
                    if weight_method == 0:
                        # Exponential fall-off
                        conf_fine = _ti.exp(-excess_mad * motion_sensitivity)
                    else:
                        # Linear / Reciprocal (Inspired by HDR+ paper L1 Reciprocal)
                        conf_fine = 1.0 / (1.0 + excess_mad * motion_sensitivity)

                    # 3. Guidance, Stability and Confidence Weighting
                    # Dalam C++, guidance dan stability diambil dari center tile saja
                    center_y = int(_ti.min(r + curr_h // 2, h - 1))
                    center_x = int(_ti.min(c + curr_w // 2, w - 1))

                    guidance_val = 1.0
                    if use_guidance == 1:
                        guidance_val = guidance_map[center_y, center_x]

                    final_conf = conf_fine * guidance_val

                    if use_stability == 1:
                        stab_val = stability_map[center_y, center_x]
                        final_conf *= stab_val

                    if final_conf >= 1e-6:
                        # 4. Global Accumulation (Tile-level, persis seperti C++)
                        # Tidak ada lagi per-pixel veto atau per-pixel guidance
                        for dr, dc in _ti.ndrange(curr_h, curr_w):
                            yy, xx = r + dr, c + dc

                            # Kombinasi bobot base window dengan final_conf dari tile
                            pixel_weight = base_window[dr, dc] * final_conf

                            weight_map_sum[yy, xx] += pixel_weight

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

    @ti_thread
    def generate_spatial_weights_taichi(
        current_image,
        reference_image,
        weight_map_sum,
        base_window,
        stability_map,
        row_starts,
        col_starts,
        tile_h,
        tile_w,
        noise_sigma,
        motion_sensitivity,
        noise_offset_factor,
        equalize_brightness,
        buffer_provider,
        weight_method=0,
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

            # 4. Phase 1: Multi-Level Pyramid Analysis for Guidance Map
            use_guidance = 1

            # Build pyramids for hierarchical analysis (auto-stop at 32px minimum)
            curr_pyramid = pyramid.build_image_pyramid_gpu(
                analysis_input,
                n_levels=3,  # Will auto-stop at min_size
                min_size=32,
                buffer_provider=buffer_provider,
            )
            ref_pyramid = pyramid.build_image_pyramid_gpu(
                ref_gpu, n_levels=3, min_size=32, buffer_provider=buffer_provider
            )

            # Debug: Print pyramid levels
            print(f"[Pyramid] Built {len(curr_pyramid)} levels:")
            for idx, level in enumerate(curr_pyramid):
                print(f"  Level {idx}: {level.shape[0]}x{level.shape[1]}")

            # Hierarchical confidence propagation: coarse to fine
            guidance_gpu = None
            pyramid_confidences = []  # Track for cleanup

            try:
                # Process from coarsest to finest level
                for level_idx in range(len(curr_pyramid) - 1, -1, -1):
                    curr_level = curr_pyramid[level_idx]
                    ref_level = ref_pyramid[level_idx]

                    h_level, w_level = curr_level.shape[0], curr_level.shape[1]

                    # Calculate adaptive tile size for this pyramid level
                    # Maintain consistent analysis granularity across scales
                    scale_factor = h_level / h  # Relative to full resolution
                    level_tile_h = max(8, int(tile_h * scale_factor))
                    level_tile_w = max(8, int(tile_w * scale_factor))

                    num_tiles_h = max(1, h_level // level_tile_h)
                    num_tiles_w = max(1, w_level // level_tile_w)

                    # Calculate confidence at this level
                    level_conf_gpu = common.get_temp_buffer(
                        (num_tiles_h, num_tiles_w), _ti.f32, buffer_provider
                    )

                    _phase1_coarse_analysis(
                        curr_level,
                        ref_level,
                        level_conf_gpu,
                        level_tile_h,
                        level_tile_w,
                        h_level,
                        w_level,
                        noise_sigma,
                        motion_sensitivity,
                        noise_offset_factor,
                        weight_method,
                    )

                    # Upsample to current level resolution for blending
                    level_conf_upsampled = bicubic_resize(
                        level_conf_gpu,
                        h_level,
                        w_level,
                        buffer_provider=buffer_provider,
                    )

                    # Blend with previous guidance if exists (hierarchical refinement)
                    if guidance_gpu is not None:
                        # Release old guidance dan langsung gunakan level upsampled yang baru ini
                        # (mengikuti gaya C++ yang murni tidak ada pembobotan historis level resolusi halus)
                        common.release_temp_buffer(guidance_gpu)
                        guidance_gpu = level_conf_upsampled
                    else:
                        # First level (coarsest), use as-is
                        guidance_gpu = level_conf_upsampled

                    # Track for cleanup
                    pyramid_confidences.append(level_conf_gpu)

                # Final upsample to full resolution if needed
                if guidance_gpu is not None and (
                    guidance_gpu.shape[0] != h or guidance_gpu.shape[1] != w
                ):
                    final_guidance = bicubic_resize(
                        guidance_gpu, h, w, buffer_provider=buffer_provider
                    )
                    common.release_temp_buffer(guidance_gpu)
                    guidance_gpu = final_guidance

            finally:
                # Cleanup pyramid levels and intermediate confidence maps
                for level in curr_pyramid[1:]:  # Skip first (original image)
                    common.release_temp_buffer(level)
                for level in ref_pyramid[1:]:
                    common.release_temp_buffer(level)
                for conf in pyramid_confidences:
                    common.release_temp_buffer(conf)

            # 5. Phase 2: Fine Analysis (Sliding Window MAD)
            use_stability = 1 if stability_map is not None else 0

            # Dummy buffer for stability if None
            if stability_map is None:
                dummy_gpu = common.get_temp_buffer((1, 1), _ti.f32, buffer_provider)
                stability_map = dummy_gpu

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
                    weight_method,
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

    @ti_thread
    def accumulate_spatial_merging_taichi(
        current_image_full,
        weight_map_work,
        final_image_sum,
        weight_map_sum_full,
        buffer_provider,
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
    def generate_spatial_weights_taichi(*args, **kwargs):
        return None

    def accumulate_spatial_merging_taichi(*args, **kwargs):
        return None
