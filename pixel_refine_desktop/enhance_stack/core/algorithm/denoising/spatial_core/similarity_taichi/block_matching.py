"""
Block Matching - Taichi GPU
===========================
Mathematical functions for similarity calculation (1:1 parity with C++ block_matching.cpp).
"""
import taichi as ti
import taichi.math as tm

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
def calculate_hybrid_gradient_optimized(
    current_img: ti.template(),
    reference_img: ti.template(),
    r: int,
    c: int,
    curr_h: int,
    curr_w: int,
    h: int,
    w: int,
    noise_level: float,
    grad_weight_factor: float,
    stab_epsilon: float
) -> float:
    """
    Calculates the hybrid gradient similarity score between current and reference blocks.
    Strict 1:1 parity with C++ Internal::calculate_hybrid_gradient_optimized.
    """
    weighted_sum = 0.0
    total_weight = 0.0
    
    grad_sensitivity = 202.5
    structure_min_threshold_sq = 150.0

    # 1-pixel border skip to prevent out of bounds and match C++
    for y in range(1, curr_h - 1):
        for x in range(1, curr_w - 1):
            img_y = r + y
            img_x = c + x
            
            p1_val = current_img[img_y, img_x]
            p2_val = reference_img[img_y, img_x]
            pixel_diff = ti.abs(p1_val - p2_val)
            
            adaptive_diff_threshold = ti.max(0.005, noise_level * 0.2)
            
            # --- Diagonal Averaging Gradients (3 rows) ---
            # Current Image gradients
            gx1_center = current_img[img_y, img_x + 1] - current_img[img_y, img_x - 1]
            gx1_top = current_img[img_y - 1, img_x + 1] - current_img[img_y - 1, img_x - 1]
            gx1_bottom = current_img[img_y + 1, img_x + 1] - current_img[img_y + 1, img_x - 1]
            gx1 = (gx1_center + gx1_top + gx1_bottom) * 0.333
            
            gy1 = current_img[img_y + 1, img_x] - current_img[img_y - 1, img_x]
            
            # Reference Image gradients
            gx2_center = reference_img[img_y, img_x + 1] - reference_img[img_y, img_x - 1]
            gx2_top = reference_img[img_y - 1, img_x + 1] - reference_img[img_y - 1, img_x - 1]
            gx2_bottom = reference_img[img_y + 1, img_x + 1] - reference_img[img_y + 1, img_x - 1]
            gx2 = (gx2_center + gx2_top + gx2_bottom) * 0.333
            
            gy2 = reference_img[img_y + 1, img_x] - reference_img[img_y - 1, img_x]
            
            mag1_sq = gx1 * gx1 + gy1 * gy1
            mag2_sq = gx2 * gx2 + gy2 * gy2
            min_mag_sq = ti.min(mag1_sq, mag2_sq)
            
            # --- continuous noise weight ---
            noise_weight = 1.0
            if noise_level > stab_epsilon:
                if min_mag_sq < structure_min_threshold_sq:
                    # Flat area
                    local_thr = adaptive_diff_threshold * 1.5
                    if pixel_diff < local_thr:
                        noise_weight = 0.05 + 0.95 * (pixel_diff / local_thr)
                    else:
                        ratio = (pixel_diff - local_thr) / local_thr
                        if ratio > 1.0:
                            ratio = 1.0
                        noise_weight = 1.0 - 0.2 * ratio
                else:
                    # Edge area
                    if pixel_diff < adaptive_diff_threshold:
                        noise_weight = 1.15 + 0.15 * (1.0 - pixel_diff / adaptive_diff_threshold)
                    else:
                        ratio = pixel_diff / (adaptive_diff_threshold * 4.0)
                        if ratio > 1.0:
                            ratio = 1.0
                        noise_weight = 0.3 + 0.4 * (1.0 - ratio)
            
            # --- structure weight ---
            structure_weight = 1.0
            if min_mag_sq > stab_epsilon and mag1_sq > stab_epsilon and mag2_sq > stab_epsilon:
                dot = gx1 * gx2 + gy1 * gy2
                cos_sim = dot / ti.sqrt(mag1_sq * mag2_sq)
                score = ti.max(0.0, cos_sim) * ti.sqrt(min_mag_sq)
                
                structure_weight = 1.0 + grad_weight_factor * fast_tanh(score * grad_sensitivity)
                
            final_weight = structure_weight * noise_weight
            weighted_sum += pixel_diff * final_weight
            total_weight += final_weight

    # Fallback to L1 mean if total weight is very low
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
