"""
Block Matching - Taichi GPU
===========================
Mathematical functions for similarity calculation (1:1 parity with C++ block_matching.cpp).
"""
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

# Keep the names importable in AOT (non-JIT) mode so package imports work
fast_tanh = None
calculate_match_confidence = None
calculate_hybrid_gradient_optimized = None
calculate_hybrid_gradient_optimized_rgb = None

if TAICHI_AVAILABLE:

    @ti.func
    def fast_tanh(x: float) -> float:
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
    def calculate_match_confidence(
        mad_score: float,
        noise_sigma: float,
        motion_sensitivity: float,
        noise_offset_factor: float
    ) -> float:
        """Calculates match confidence using noise-sensitive exponential decay."""
        excess_mad = ti.max(0.0, mad_score - noise_offset_factor * noise_sigma)
        return ti.exp(-excess_mad * motion_sensitivity)

    @ti.func
    def _image_value(image: ti.template(), y: ti.i32, x: ti.i32,
                     channel: ti.i32, is_rgb: ti.template()) -> ti.f32:
        value = 0.0
        if ti.static(is_rgb):
            value = image[y, x, channel]
        else:
            value = image[y, x]
        return value

    @ti.func
    def _calculate_hybrid_gradient_optimized_impl(
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
        channel: ti.i32,
        is_rgb: ti.template(),
    ) -> float:
        """
        Calculates the hybrid gradient similarity score between current and reference blocks.
        Strict 1:1 parity with C++ Internal::calculate_hybrid_gradient_optimized using precomputed gradients.
        """
        weighted_sum = 0.0
        total_weight = 0.0
        
        grad_sensitivity = 202.5
        # Adaptive Vision Boost: increase sensitivity dynamically on low-contrast tiles
        adaptive_grad_sensitivity = grad_sensitivity * (1.0 + 3.0 * flat_weight)
        # Normalized structure threshold squared for [0, 1] float images (150.0 / 255^2)
        structure_min_threshold_sq = 0.002307
        # These values are constant for the complete tile.  Hoisting them
        # avoids repeating the same max/multiply and branch predicate for
        # every sampled pixel while preserving the original arithmetic.
        adaptive_diff_threshold = ti.max(0.005, noise_level * 0.2)
        base_structure_thr_sq = ti.max(structure_min_threshold_sq, 4.0 * noise_level * noise_level) * (1.0 + flat_weight)
        noise_enabled = noise_level > stab_epsilon

        # 1-pixel border skip to prevent out of bounds and match C++
        for y in range((curr_h - 1) // 2):
            img_y = r + 1 + y * 2
            for x in range((curr_w - 1) // 2):
                img_x = c + 1 + x * 2
                
                p1_val = _image_value(current_img, img_y, img_x, channel, is_rgb)
                p2_val = _image_value(reference_img, img_y, img_x, channel, is_rgb)
                pixel_diff = ti.abs(p1_val - p2_val)
                
                # Compute the Sobel-like gradients at the sampled pixel. The
                # old route materialized four full-resolution gradient planes
                # before visiting the tiles. Inlining these few samples keeps
                # gradient scratch bounded to registers while preserving the
                # same stencil and arithmetic order as precompute_gradients.
                gx1_center = _image_value(current_img, img_y, img_x + 1, channel, is_rgb) - _image_value(current_img, img_y, img_x - 1, channel, is_rgb)
                gx1_top = _image_value(current_img, img_y - 1, img_x + 1, channel, is_rgb) - _image_value(current_img, img_y - 1, img_x - 1, channel, is_rgb)
                gx1_bottom = _image_value(current_img, img_y + 1, img_x + 1, channel, is_rgb) - _image_value(current_img, img_y + 1, img_x - 1, channel, is_rgb)
                gx1 = (gx1_center + gx1_top + gx1_bottom) * 0.33333333
                gy1_center = _image_value(current_img, img_y + 1, img_x, channel, is_rgb) - _image_value(current_img, img_y - 1, img_x, channel, is_rgb)
                gy1_left = _image_value(current_img, img_y + 1, img_x - 1, channel, is_rgb) - _image_value(current_img, img_y - 1, img_x - 1, channel, is_rgb)
                gy1_right = _image_value(current_img, img_y + 1, img_x + 1, channel, is_rgb) - _image_value(current_img, img_y - 1, img_x + 1, channel, is_rgb)
                gy1 = (gy1_center + gy1_left + gy1_right) * 0.33333333

                gx2_center = _image_value(reference_img, img_y, img_x + 1, channel, is_rgb) - _image_value(reference_img, img_y, img_x - 1, channel, is_rgb)
                gx2_top = _image_value(reference_img, img_y - 1, img_x + 1, channel, is_rgb) - _image_value(reference_img, img_y - 1, img_x - 1, channel, is_rgb)
                gx2_bottom = _image_value(reference_img, img_y + 1, img_x + 1, channel, is_rgb) - _image_value(reference_img, img_y + 1, img_x - 1, channel, is_rgb)
                gx2 = (gx2_center + gx2_top + gx2_bottom) * 0.33333333
                gy2_center = _image_value(reference_img, img_y + 1, img_x, channel, is_rgb) - _image_value(reference_img, img_y - 1, img_x, channel, is_rgb)
                gy2_left = _image_value(reference_img, img_y + 1, img_x - 1, channel, is_rgb) - _image_value(reference_img, img_y - 1, img_x - 1, channel, is_rgb)
                gy2_right = _image_value(reference_img, img_y + 1, img_x + 1, channel, is_rgb) - _image_value(reference_img, img_y - 1, img_x + 1, channel, is_rgb)
                gy2 = (gy2_center + gy2_left + gy2_right) * 0.33333333
                
                mag1_sq = gx1 * gx1 + gy1 * gy1
                mag2_sq = gx2 * gx2 + gy2 * gy2
                min_mag_sq = ti.min(mag1_sq, mag2_sq)
                
                # Adaptive to local intensity (p2_val): dark areas get higher noise tolerance scale, highlights get stricter.
                # Linear scaling maps p2_val=0 to scale=3.0 and p2_val=1.0 to scale=1.0. Extremely cheap on GPU.
                tolerance_scale = ti.max(1.0, ti.min(3.0, 3.0 - 2.0 * p2_val))
                local_adaptive_diff_threshold = adaptive_diff_threshold * tolerance_scale
                local_structure_min_threshold_sq = base_structure_thr_sq * (tolerance_scale * tolerance_scale)

                # --- continuous noise weight ---
                noise_weight = 1.0
                if noise_enabled:
                    if min_mag_sq < local_structure_min_threshold_sq:
                        # Flat area
                        local_thr = local_adaptive_diff_threshold * 1.5
                        if pixel_diff < local_thr:
                            noise_weight = 0.05 + 0.95 * (pixel_diff / local_thr)
                        else:
                            ratio = (pixel_diff - local_thr) / local_thr
                            if ratio > 1.0:
                                ratio = 1.0
                            noise_weight = 1.0 - 0.2 * ratio
                    else:
                        # Edge area
                        if pixel_diff < local_adaptive_diff_threshold:
                            noise_weight = 1.15 + 0.15 * (1.0 - pixel_diff / local_adaptive_diff_threshold)
                        else:
                            ratio = pixel_diff / (local_adaptive_diff_threshold * 4.0)
                            if ratio > 1.0:
                                ratio = 1.0
                            noise_weight = 0.3 + 0.4 * (1.0 - ratio)
                
                # --- structure weight & deghosting penalty ---
                structure_weight = 1.0
                if min_mag_sq > stab_epsilon and mag1_sq > stab_epsilon and mag2_sq > stab_epsilon:
                    dot = gx1 * gx2 + gy1 * gy2
                    cos_sim = dot / ti.sqrt(mag1_sq * mag2_sq)
                    
                    if min_mag_sq > local_structure_min_threshold_sq and cos_sim < 0.2:
                        # Mismatched structure orientations: scale up pixel_diff to penalize mismatch and prevent ghosting
                        pixel_diff = pixel_diff * (1.5 - cos_sim)
                    else:
                        score = ti.max(0.0, cos_sim) * ti.sqrt(min_mag_sq)
                        structure_weight = 1.0 + grad_weight_factor * fast_tanh(score * adaptive_grad_sensitivity)
                    
                final_weight = structure_weight * noise_weight
                weighted_sum += pixel_diff * final_weight
                total_weight += final_weight

        # Fallback to L1 mean if total weight is very low
        res_val = 0.0
        if total_weight < 1e-4:
            l1_sum = 0.0
            for y in range(curr_h):
                for x in range(curr_w):
                    l1_sum += ti.abs(
                        _image_value(current_img, r + y, c + x, channel, is_rgb)
                        - _image_value(reference_img, r + y, c + x, channel, is_rgb)
                    )
            res_val = l1_sum / float(curr_h * curr_w)
        else:
            res_val = weighted_sum / total_weight

        return res_val

    @ti.func
    def calculate_hybrid_gradient_optimized(
        current_img: ti.template(), reference_img: ti.template(),
        curr_grad_x: ti.template(), curr_grad_y: ti.template(),
        ref_grad_x: ti.template(), ref_grad_y: ti.template(),
        r: int, c: int, curr_h: int, curr_w: int, h: int, w: int,
        noise_level: float, grad_weight_factor: float, stab_epsilon: float,
        flat_weight: float,
    ) -> float:
        return _calculate_hybrid_gradient_optimized_impl(
            current_img, reference_img, curr_grad_x, curr_grad_y,
            ref_grad_x, ref_grad_y, r, c, curr_h, curr_w, h, w,
            noise_level, grad_weight_factor, stab_epsilon, flat_weight,
            0, False,
        )

    @ti.func
    def calculate_hybrid_gradient_optimized_rgb(
        current_img: ti.template(), reference_img: ti.template(),
        r: int, c: int, curr_h: int, curr_w: int, h: int, w: int,
        noise_level: float, grad_weight_factor: float, stab_epsilon: float,
        flat_weight: float, channel: ti.i32,
    ) -> float:
        return _calculate_hybrid_gradient_optimized_impl(
            current_img, reference_img, current_img, current_img,
            reference_img, reference_img, r, c, curr_h, curr_w, h, w,
            noise_level, grad_weight_factor, stab_epsilon, flat_weight,
            channel, True,
        )
