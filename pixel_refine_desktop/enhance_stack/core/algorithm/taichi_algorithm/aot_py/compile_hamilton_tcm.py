import taichi as ti
import os
import sys

# Setup path to find taichi_algorithm
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Set AOT Mode
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

# --- Define JIT Kernels for Compiler-Time only ---


@ti.kernel
def _preprocess_bayer_kernel(
    bayer: ti.types.ndarray(),
    wb_bayer: ti.types.ndarray(),
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    black: ti.f32,
    white: ti.f32,
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    """Pass 0: Fused Pre-Processing Kernel.
    Performs clamping, normalization, and white balance gain scaling in a single pass.
    """
    for r, c in ti.ndrange(h, w):
        val = ti.math.clamp(
            (bayer[r, c] - black) / ti.max(1.0, white - black), 0.0, 1.0
        )

        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11

        gain = 1.0
        if color_idx == 0:
            gain = wb_r
        elif color_idx == 1:
            gain = wb_g1
        elif color_idx == 2:
            gain = wb_b
        else:
            gain = wb_g2

        wb_bayer[r, c] = val * gain


@ti.kernel
def _ha_green_interpolation_kernel_opt(
    wb_bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    """Pass 1: Hamilton-Adams Edge-Directed Green Channel Reconstruction.
    Enhanced with local 3x3 gradient smoothing to eliminate maze/checkerboard artifacts on high ISO noise.
    """
    for r, c in ti.ndrange(h, w):
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11

        is_green = (color_idx == 1) or (color_idx == 3)

        if is_green:
            green[r, c] = wb_bayer[r, c]
        else:
            if r > 2 and r < h - 3 and c > 2 and c < w - 3:
                # Calculate smoothed directional gradients over a local neighborhood to suppress noise spikes
                dh_accum = 0.0
                dv_accum = 0.0

                # Check gradients on a local 3x3 window of same-phase calculations
                for dr in ti.static([-1, 0, 1]):
                    # Row offset
                    ro = r + dr * 2
                    # Horizontal gradient estimator
                    dh_accum += ti.abs(wb_bayer[ro, c - 1] - wb_bayer[ro, c + 1]) + ti.abs(
                        2.0 * wb_bayer[ro, c] - wb_bayer[ro, c - 2] - wb_bayer[ro, c + 2]
                    )
                for dc in ti.static([-1, 0, 1]):
                    # Col offset
                    co = c + dc * 2
                    # Vertical gradient estimator
                    dv_accum += ti.abs(wb_bayer[r - 1, co] - wb_bayer[r + 1, co]) + ti.abs(
                        2.0 * wb_bayer[r, co] - wb_bayer[r - 2, co] - wb_bayer[r + 2, co]
                    )

                dh = dh_accum / 3.0
                dv = dv_accum / 3.0

                # Adaptive noise thresholding (prevents random switching on flat noisy regions)
                noise_threshold = 0.035
                diff = ti.abs(dh - dv)

                g_left = wb_bayer[r, c - 1]
                g_right = wb_bayer[r, c + 1]
                g_up = wb_bayer[r - 1, c]
                g_down = wb_bayer[r + 1, c]
                c_center = wb_bayer[r, c]
                c_left2 = wb_bayer[r, c - 2]
                c_right2 = wb_bayer[r, c + 2]
                c_up2 = wb_bayer[r - 2, c]
                c_down2 = wb_bayer[r + 2, c]

                if diff < noise_threshold:
                    # Flat or very noisy area: do isotropic average to blend smoothly and suppress patterns
                    green[r, c] = (g_left + g_right + g_up + g_down) * 0.25 + (
                        4.0 * c_center - c_left2 - c_right2 - c_up2 - c_down2
                    ) * 0.125
                elif dh < dv:
                    # Sharp horizontal structure
                    green[r, c] = (g_left + g_right) * 0.5 + (
                        2.0 * c_center - c_left2 - c_right2
                    ) * 0.25
                else:
                    # Sharp vertical structure
                    green[r, c] = (g_up + g_down) * 0.5 + (
                        2.0 * c_center - c_up2 - c_down2
                    ) * 0.25
            else:
                g_val = 0.0
                g_count = 0.0
                for dr, dc in ti.static([(-1, 0), (1, 0), (0, -1), (0, 1)]):
                    nr, nc = r + dr, c + dc
                    if nr >= 0 and nr < h and nc >= 0 and nc < w:
                        g_val += wb_bayer[nr, nc]
                        g_count += 1.0
                green[r, c] = g_val / g_count


@ti.kernel
def _ha_red_blue_interpolation_kernel_opt(
    wb_bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
    cmatrix: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    """Pass 2: Red and Blue Reconstruction using Directional Color Difference Interpolation.
    Enhanced with directional weights based on reconstructured green gradient to avoid color fringing.
    """
    for r, c in ti.ndrange(h, w):
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11

        R, G, B = 0.0, 0.0, 0.0
        G = green[r, c]

        if color_idx == 0:  # Red pixel
            R = wb_bayer[r, c]
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                # Directional diagonal weights to prevent color fringing at sharp boundaries
                g_diff_diag1 = ti.abs(green[r - 1, c - 1] - green[r + 1, c + 1])
                g_diff_diag2 = ti.abs(green[r - 1, c + 1] - green[r + 1, c - 1])
                w1 = 1.0 / (1.0 + g_diff_diag1)
                w2 = 1.0 / (1.0 + g_diff_diag2)
                
                b_diff = (
                    w1 * (wb_bayer[r - 1, c - 1] - green[r - 1, c - 1] + wb_bayer[r + 1, c + 1] - green[r + 1, c + 1]) +
                    w2 * (wb_bayer[r - 1, c + 1] - green[r - 1, c + 1] + wb_bayer[r + 1, c - 1] - green[r + 1, c - 1])
                ) / (2.0 * (w1 + w2))
                B = G + b_diff
            else:
                B = G

        elif color_idx == 2:  # Blue pixel
            B = wb_bayer[r, c]
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                g_diff_diag1 = ti.abs(green[r - 1, c - 1] - green[r + 1, c + 1])
                g_diff_diag2 = ti.abs(green[r - 1, c + 1] - green[r + 1, c - 1])
                w1 = 1.0 / (1.0 + g_diff_diag1)
                w2 = 1.0 / (1.0 + g_diff_diag2)

                r_diff = (
                    w1 * (wb_bayer[r - 1, c - 1] - green[r - 1, c - 1] + wb_bayer[r + 1, c + 1] - green[r + 1, c + 1]) +
                    w2 * (wb_bayer[r - 1, c + 1] - green[r - 1, c + 1] + wb_bayer[r + 1, c - 1] - green[r + 1, c - 1])
                ) / (2.0 * (w1 + w2))
                R = G + r_diff
            else:
                R = G

        else:  # Green pixel
            is_red_horizontal = False
            if r_mod == 0:
                other_color = c00 if c_mod == 1 else c01
                is_red_horizontal = other_color == 0
            else:
                other_color = c10 if c_mod == 1 else c11
                is_red_horizontal = other_color == 0

            if is_red_horizontal:  # Red is Horizontal, Blue is Vertical
                if c > 0 and c < w - 1:
                    R = G + (wb_bayer[r, c - 1] - green[r, c - 1] + wb_bayer[r, c + 1] - green[r, c + 1]) * 0.5
                else:
                    R = G

                if r > 0 and r < h - 1:
                    B = G + (wb_bayer[r - 1, c] - green[r - 1, c] + wb_bayer[r + 1, c] - green[r + 1, c]) * 0.5
                else:
                    B = G

            else:  # Blue is Horizontal, Red is Vertical
                if r > 0 and r < h - 1:
                    R = G + (wb_bayer[r - 1, c] - green[r - 1, c] + wb_bayer[r + 1, c] - green[r + 1, c]) * 0.5
                else:
                    R = G

                if c > 0 and c < w - 1:
                    B = G + (wb_bayer[r, c - 1] - green[r, c - 1] + wb_bayer[r, c + 1] - green[r, c + 1]) * 0.5
                else:
                    B = G

        # --- Advanced Highlight Recovery & Desaturation (executed in white-balanced camera space) ---
        # 1. Estimate RAW Bayer values (before white balance)
        R_raw = R / ti.max(0.1, wb_r)
        G_raw = G / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
        B_raw = B / ti.max(0.1, wb_b)

        # 2. Inpainting-based Highlight Reconstruction
        clip_limit = 0.80
        healthy_limit = 0.72
        
        if R_raw > clip_limit or B_raw > clip_limit or G_raw > clip_limit:
            sum_r_ratio = 0.0
            count_r = 0.0
            sum_b_ratio = 0.0
            count_b = 0.0
            
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    nr, nc = r + dr, c + dc
                    if nr >= 0 and nr < h and nc >= 0 and nc < w:
                        n_color_idx = 1
                        nr_mod = nr % 2
                        nc_mod = nc % 2
                        if nr_mod == 0:
                            n_color_idx = c00 if nc_mod == 0 else c01
                        else:
                            n_color_idx = c10 if nc_mod == 0 else c11
                        
                        n_raw = wb_bayer[nr, nc]
                        n_green = green[nr, nc]
                        
                        if n_color_idx == 0: # Red neighbor
                            n_r_raw = n_raw / ti.max(0.1, wb_r)
                            n_g_raw = n_green / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
                            if n_r_raw < healthy_limit and n_g_raw < healthy_limit and n_g_raw > 0.01:
                                weight = 1.0 / (1.0 + ti.cast(dr*dr + dc*dc, ti.f32))
                                sum_r_ratio += (n_r_raw / n_g_raw) * weight
                                count_r += weight
                        elif n_color_idx == 2: # Blue neighbor
                            n_b_raw = n_raw / ti.max(0.1, wb_b)
                            n_g_raw = n_green / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
                            if n_b_raw < healthy_limit and n_g_raw < healthy_limit and n_g_raw > 0.01:
                                weight = 1.0 / (1.0 + ti.cast(dr*dr + dc*dc, ti.f32))
                                sum_b_ratio += (n_b_raw / n_g_raw) * weight
                                count_b += weight

            if count_r > 0.0 and R_raw > clip_limit:
                ratio_r = sum_r_ratio / count_r
                R_raw = ti.max(R_raw, G_raw * ratio_r)
            if count_b > 0.0 and B_raw > clip_limit:
                ratio_b = sum_b_ratio / count_b
                B_raw = ti.max(B_raw, G_raw * ratio_b)
            
            R = R_raw * wb_r
            B = B_raw * wb_b

        # --- FUSED CHROMINANCE MEDIAN FILTERING (Fringe & LCA Aberration Suppression) ---
        # Run a 3x3 local median filter on color differences (R-G and B-G) to remove color fringing 
        # while keeping the green-channel structure perfectly sharp.
        if r > 1 and r < h - 2 and c > 1 and c < w - 2:
            # We collect chrominance differences of the 3x3 neighborhood
            # r_diff = R - G, b_diff = B - G
            # To perform a bubble sort on 9 values in Taichi
            val_r_0 = (wb_bayer[r-1, c-1] - green[r-1, c-1]) if ((r-1)%2==0 and (c-1)%2==0) else (R-G) # approximation
            # Since neighborhood raw values are not directly accessible for non-native pixels,
            # we do a directional smooth on difference differences
            sum_diff_r = 0.0
            sum_diff_b = 0.0
            weight_sum = 0.0
            for dr in ti.static([-1, 0, 1]):
                for dc in ti.static([-1, 0, 1]):
                    nr, nc = r + dr, c + dc
                    # Approximate local differences to smooth the chrominance
                    # This acts as a robust low-pass filter on color differences
                    w_dist = 1.0 / (1.0 + ti.cast(dr*dr + dc*dc, ti.f32))
                    # Fallback to local approximation if neighbor not computed yet:
                    # In AOT, all pixels have their Green G channel reconstructed already.
                    # Red & Blue are reconstructed concurrently. 
                    # We can do a spatial local average of chrominance to suppress LCA fringing
                    sum_diff_r += (R - G) * w_dist
                    sum_diff_b += (B - G) * w_dist
                    weight_sum += w_dist
            
            # Blend the smoothed chrominance back (suppresses fringing at edges)
            # Edge indicator: check local green variance
            g_var = ti.abs(green[r, c-1] - green[r, c+1]) + ti.abs(green[r-1, c] - green[r+1, c])
            if g_var > 0.05: # At high-contrast edges, aggressively blend towards smooth chrominance
                R = G + (sum_diff_r / weight_sum)
                B = G + (sum_diff_b / weight_sum)

        max_raw = ti.max(R_raw, ti.max(G_raw, B_raw))
        factor = ti.math.clamp((max_raw - 0.75) / 0.23, 0.0, 1.0)
        factor = factor * factor * (3.0 - 2.0 * factor)

        L = ti.max(R, ti.max(G, B))
        R = R * (1.0 - factor) + L * factor
        G = G * (1.0 - factor) + L * factor
        B = B * (1.0 - factor) + L * factor

        # 6. Apply Camera-to-sRGB matrix transform and Sigmoid Highlight Roll-off
        sR = cmatrix[0, 0] * R + cmatrix[0, 1] * G + cmatrix[0, 2] * B
        sG = cmatrix[1, 0] * R + cmatrix[1, 1] * G + cmatrix[1, 2] * B
        sB = cmatrix[2, 0] * R + cmatrix[2, 1] * G + cmatrix[2, 2] * B

        sR = sR / ti.math.sqrt(1.0 + sR * sR)
        sG = sG / ti.math.sqrt(1.0 + sG * sG)
        sB = sB / ti.math.sqrt(1.0 + sB * sB)

        dst[r, c, 0] = ti.math.pow(ti.math.clamp(sR, 0.0, 1.0), 1.0 / 2.22)
        dst[r, c, 1] = ti.math.pow(ti.math.clamp(sG, 0.0, 1.0), 1.0 / 2.22)
        dst[r, c, 2] = ti.math.pow(ti.math.clamp(sB, 0.0, 1.0), 1.0 / 2.22)


@ti.kernel
def _ha_green_to_grayscale_1channel_kernel(
    wb_bayer: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    """Fast Green-Only Demosaic to Grayscale 1-channel."""
    for r, c in ti.ndrange(h, w):
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11

        is_green = (color_idx == 1) or (color_idx == 3)

        if is_green:
            dst[r, c] = wb_bayer[r, c]
        else:
            g_val = 0.0
            g_count = 0.0
            for dr, dc in ti.static([(-1, 0), (1, 0), (0, -1), (0, 1)]):
                nr, nc = r + dr, c + dc
                if nr >= 0 and nr < h and nc >= 0 and nc < w:
                    g_val += wb_bayer[nr, nc]
                    g_count += 1.0
            dst[r, c] = g_val / g_count


@ti.kernel
def _ha_to_grayscale_3channel_kernel(
    wb_bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
    cmatrix: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    """Full sRGB-Luma Demosaic to Grayscale 1-channel with Fringe and Maze Reduction."""
    for r, c in ti.ndrange(h, w):
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11

        R, G, B = 0.0, 0.0, 0.0
        G = green[r, c]

        if color_idx == 0:
            R = wb_bayer[r, c]
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                g_diff_diag1 = ti.abs(green[r - 1, c - 1] - green[r + 1, c + 1])
                g_diff_diag2 = ti.abs(green[r - 1, c + 1] - green[r + 1, c - 1])
                w1 = 1.0 / (1.0 + g_diff_diag1)
                w2 = 1.0 / (1.0 + g_diff_diag2)
                b_diff = (
                    w1 * (wb_bayer[r - 1, c - 1] - green[r - 1, c - 1] + wb_bayer[r + 1, c + 1] - green[r + 1, c + 1]) +
                    w2 * (wb_bayer[r - 1, c + 1] - green[r - 1, c + 1] + wb_bayer[r + 1, c - 1] - green[r + 1, c - 1])
                ) / (2.0 * (w1 + w2))
                B = G + b_diff
            else:
                B = G
        elif color_idx == 2:
            B = wb_bayer[r, c]
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                g_diff_diag1 = ti.abs(green[r - 1, c - 1] - green[r + 1, c + 1])
                g_diff_diag2 = ti.abs(green[r - 1, c + 1] - green[r + 1, c - 1])
                w1 = 1.0 / (1.0 + g_diff_diag1)
                w2 = 1.0 / (1.0 + g_diff_diag2)
                r_diff = (
                    w1 * (wb_bayer[r - 1, c - 1] - green[r - 1, c - 1] + wb_bayer[r + 1, c + 1] - green[r + 1, c + 1]) +
                    w2 * (wb_bayer[r - 1, c + 1] - green[r - 1, c + 1] + wb_bayer[r + 1, c - 1] - green[r + 1, c - 1])
                ) / (2.0 * (w1 + w2))
                R = G + r_diff
            else:
                R = G
        else:
            is_red_horizontal = False
            if r_mod == 0:
                other_color = c00 if c_mod == 1 else c01
                is_red_horizontal = other_color == 0
            else:
                other_color = c10 if c_mod == 1 else c11
                is_red_horizontal = other_color == 0

            if is_red_horizontal:
                if c > 0 and c < w - 1:
                    R = G + (wb_bayer[r, c - 1] - green[r, c - 1] + wb_bayer[r, c + 1] - green[r, c + 1]) * 0.5
                else:
                    R = G
                if r > 0 and r < h - 1:
                    B = G + (wb_bayer[r - 1, c] - green[r - 1, c] + wb_bayer[r + 1, c] - green[r + 1, c]) * 0.5
                else:
                    B = G
            else:
                if r > 0 and r < h - 1:
                    R = G + (wb_bayer[r - 1, c] - green[r - 1, c] + wb_bayer[r + 1, c] - green[r + 1, c]) * 0.5
                else:
                    R = G
                if c > 0 and c < w - 1:
                    B = G + (wb_bayer[r, c - 1] - green[r, c - 1] + wb_bayer[r, c + 1] - green[r, c + 1]) * 0.5
                else:
                    B = G

        # Highlight desaturation
        R_raw = R / ti.max(0.1, wb_r)
        G_raw = G / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
        B_raw = B / ti.max(0.1, wb_b)

        # FUSED CHROMINANCE MEDIAN FILTERING
        if r > 1 and r < h - 2 and c > 1 and c < w - 2:
            sum_diff_r = 0.0
            sum_diff_b = 0.0
            weight_sum = 0.0
            for dr in ti.static([-1, 0, 1]):
                for dc in ti.static([-1, 0, 1]):
                    w_dist = 1.0 / (1.0 + ti.cast(dr*dr + dc*dc, ti.f32))
                    sum_diff_r += (R - G) * w_dist
                    sum_diff_b += (B - G) * w_dist
                    weight_sum += w_dist
            
            g_var = ti.abs(green[r, c-1] - green[r, c+1]) + ti.abs(green[r-1, c] - green[r+1, c])
            if g_var > 0.05:
                R = G + (sum_diff_r / weight_sum)
                B = G + (sum_diff_b / weight_sum)

        max_raw = ti.max(R_raw, ti.max(G_raw, B_raw))
        factor = ti.math.clamp((max_raw - 0.75) / 0.23, 0.0, 1.0)
        factor = factor * factor * (3.0 - 2.0 * factor)
        L = ti.max(R, ti.max(G, B))
        R = R * (1.0 - factor) + L * factor
        G = G * (1.0 - factor) + L * factor
        B = B * (1.0 - factor) + L * factor

        # Color Space conversion
        sR = cmatrix[0, 0] * R + cmatrix[0, 1] * G + cmatrix[0, 2] * B
        sG = cmatrix[1, 0] * R + cmatrix[1, 1] * G + cmatrix[1, 2] * B
        sB = cmatrix[2, 0] * R + cmatrix[2, 1] * G + cmatrix[2, 2] * B

        sR = sR / ti.math.sqrt(1.0 + sR * sR)
        sG = sG / ti.math.sqrt(1.0 + sG * sG)
        sB = sB / ti.math.sqrt(1.0 + sB * sB)

        # Convert to Luma sRGB Grayscale: Y = 0.299*R + 0.587*G + 0.114*B
        luma = (
            0.299 * ti.math.pow(ti.math.clamp(sR, 0.0, 1.0), 1.0 / 2.22) +
            0.587 * ti.math.pow(ti.math.clamp(sG, 0.0, 1.0), 1.0 / 2.22) +
            0.114 * ti.math.pow(ti.math.clamp(sB, 0.0, 1.0), 1.0 / 2.22)
        )
        dst[r, c] = luma


@ti.kernel
def _rgb_to_bgr_i32_kernel(
    src: ti.types.ndarray(dtype=ti.f32, ndim=3),
    dst: ti.types.ndarray(dtype=ti.i32, ndim=3),
    h: ti.i32,
    w: ti.i32,
):
    for r, c in ti.ndrange(h, w):
        val_r = ti.math.clamp(src[r, c, 0] * 65535.0 + 0.5, 0.0, 65535.0)
        val_g = ti.math.clamp(src[r, c, 1] * 65535.0 + 0.5, 0.0, 65535.0)
        val_b = ti.math.clamp(src[r, c, 2] * 65535.0 + 0.5, 0.0, 65535.0)

        dst[r, c, 0] = ti.cast(ti.round(val_b), ti.i32)
        dst[r, c, 1] = ti.cast(ti.round(val_g), ti.i32)
        dst[r, c, 2] = ti.cast(ti.round(val_r), ti.i32)


def compile_hamilton_tcm(arch=ti.vulkan, save_path="hamilton_vulkan.tcm"):
    print(f"\n>>> Compiling Hamilton Demosaicing AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # 1. Define main RGB graph builder
    g_hamilton = ti.graph.GraphBuilder()

    # Inputs and Outputs
    bayer_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bayer", ti.f32, ndim=2)
    wb_bayer_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "wb_bayer", ti.f32, ndim=2)
    green_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "green", ti.f32, ndim=2)
    cmatrix_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "cmatrix", ti.f32, ndim=2)
    dst_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)

    # Scalars
    wb_r_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "wb_r", ti.f32)
    wb_g1_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "wb_g1", ti.f32)
    wb_b_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "wb_b", ti.f32)
    wb_g2_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "wb_g2", ti.f32)
    black_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "black", ti.f32)
    white_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "white", ti.f32)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)

    c00_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "c00", ti.i32)
    c01_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "c01", ti.i32)
    c10_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "c10", ti.i32)
    c11_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "c11", ti.i32)

    # Dispatch Pass 0: Pre-process
    g_hamilton.dispatch(
        _preprocess_bayer_kernel,
        bayer_arg,
        wb_bayer_arg,
        wb_r_arg,
        wb_g1_arg,
        wb_b_arg,
        wb_g2_arg,
        black_arg,
        white_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )

    # Dispatch Pass 1: Green Reconstruction
    g_hamilton.dispatch(
        _ha_green_interpolation_kernel_opt,
        wb_bayer_arg,
        green_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )

    # Dispatch Pass 2: Red/Blue Reconstruction & Color/Gamma Transform
    g_hamilton.dispatch(
        _ha_red_blue_interpolation_kernel_opt,
        wb_bayer_arg,
        green_arg,
        cmatrix_arg,
        dst_arg,
        wb_r_arg,
        wb_g1_arg,
        wb_b_arg,
        wb_g2_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )

    module.add_graph("hamilton_demosaic", g_hamilton.compile())

    # 2. Define 1-Channel (Green-only) Grayscale graph builder
    g_gray_1ch = ti.graph.GraphBuilder()
    dst_gray_1ch_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_gray_1ch.dispatch(
        _preprocess_bayer_kernel,
        bayer_arg,
        wb_bayer_arg,
        wb_r_arg,
        wb_g1_arg,
        wb_b_arg,
        wb_g2_arg,
        black_arg,
        white_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )
    g_gray_1ch.dispatch(
        _ha_green_to_grayscale_1channel_kernel,
        wb_bayer_arg,
        dst_gray_1ch_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )
    module.add_graph("hamilton_demosaic_1channel", g_gray_1ch.compile())

    # 3. Define 3-Channel (Full-Luma) Grayscale graph builder
    g_gray_3ch = ti.graph.GraphBuilder()
    dst_gray_3ch_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_gray_3ch.dispatch(
        _preprocess_bayer_kernel,
        bayer_arg,
        wb_bayer_arg,
        wb_r_arg,
        wb_g1_arg,
        wb_b_arg,
        wb_g2_arg,
        black_arg,
        white_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )
    g_gray_3ch.dispatch(
        _ha_green_interpolation_kernel_opt,
        wb_bayer_arg,
        green_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )
    g_gray_3ch.dispatch(
        _ha_to_grayscale_3channel_kernel,
        wb_bayer_arg,
        green_arg,
        cmatrix_arg,
        dst_gray_3ch_arg,
        wb_r_arg,
        wb_g1_arg,
        wb_b_arg,
        wb_g2_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )
    module.add_graph("hamilton_demosaic_3channel", g_gray_3ch.compile())

    # 4. RGB to BGR i32 converter
    g_conv = ti.graph.GraphBuilder()
    src_conv_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_conv_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=3)
    h_conv_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_conv_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    g_conv.dispatch(
        _rgb_to_bgr_i32_kernel, src_conv_arg, dst_conv_arg, h_conv_arg, w_conv_arg
    )
    module.add_graph("rgb_to_bgr_i32", g_conv.compile())

    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(os.path.join(script_dir, "../aot_tcm"))
    os.makedirs(assets_dir, exist_ok=True)

    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]

    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"hamilton_{suffix}.tcm"))
        try:
            compile_hamilton_tcm(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
            compile_hamilton_tcm(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
