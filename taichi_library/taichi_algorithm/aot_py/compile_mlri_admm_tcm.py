import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import os
import sys

# Setup path to find taichi_algorithm
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

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
    """Pass 0: Clamp, normalize, and apply white balance gains."""
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
def _bayer_bilateral_denoise_kernel(
    wb_bayer: ti.types.ndarray(),
    denoised_bayer: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
    sigma_r_base: ti.f32,
):
    """Pass 0B: Adaptive Bayer Denoising using stride-2 noise-aware Bilateral Filter."""
    for r, c in ti.ndrange(h, w):
        val_center = wb_bayer[r, c]
        
        if sigma_r_base <= 0.0:
            denoised_bayer[r, c] = val_center
        else:
            # Poisson-like shot noise model: range sigma scales with pixel intensity
            sigma_r = sigma_r_base * ti.math.sqrt(val_center + 1e-4)
            
            sum_val = 0.0
            sum_w = 0.0
            
            # 3x3 same-channel neighborhood (stride-2 over 5x5 window on Bayer grid)
            for dr, dc in ti.static(ti.ndrange((-1, 2), (-1, 2))):
                nr = ti.math.clamp(r + 2 * dr, 0, h - 1)
                nc = ti.math.clamp(c + 2 * dc, 0, w - 1)
                
                val_neighbor = wb_bayer[nr, nc]
                
                # Spatial weight: sigma_s = 1.0
                w_s = ti.math.exp(-ti.cast(dr*dr + dc*dc, ti.f32) / 2.0)
                
                # Range weight (edge-preserving)
                diff = val_center - val_neighbor
                w_r = ti.math.exp(-(diff * diff) / ti.max(1e-6, 2.0 * sigma_r * sigma_r))
                
                w_total = w_s * w_r
                sum_val += val_neighbor * w_total
                sum_w += w_total
                
            denoised_bayer[r, c] = sum_val / ti.max(1e-5, sum_w)

@ti.func
def _fast_gamma(x: ti.f32) -> ti.f32:
    t = ti.math.sqrt(x)
    return t * (1.30547177 + t * (-0.78947190 + t * (0.79064221 - 0.30664208 * t)))

@ti.kernel
def _gbtf_green_interpolation_kernel(
    wb_bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    """Pass 1: GBTF (Gradient-Based Threshold-Free) Green Channel Interpolation."""
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
            # Clamp indices
            r_u3 = ti.math.clamp(r - 3, 0, h - 1)
            r_u2 = ti.math.clamp(r - 2, 0, h - 1)
            r_u1 = ti.math.clamp(r - 1, 0, h - 1)
            r_d1 = ti.math.clamp(r + 1, 0, h - 1)
            r_d2 = ti.math.clamp(r + 2, 0, h - 1)
            r_d3 = ti.math.clamp(r + 3, 0, h - 1)

            c_l3 = ti.math.clamp(c - 3, 0, w - 1)
            c_l2 = ti.math.clamp(c - 2, 0, w - 1)
            c_l1 = ti.math.clamp(c - 1, 0, w - 1)
            c_r1 = ti.math.clamp(c + 1, 0, w - 1)
            c_r2 = ti.math.clamp(c + 2, 0, w - 1)
            c_r3 = ti.math.clamp(c + 3, 0, w - 1)

            # GBTF interpolation at Red/Blue sites using N, S, E, W gradients
            g_E = ti.abs(wb_bayer[r, c_r1] - wb_bayer[r, c_r3]) + ti.abs(wb_bayer[r, c] - wb_bayer[r, c_r2])
            g_W = ti.abs(wb_bayer[r, c_l1] - wb_bayer[r, c_l3]) + ti.abs(wb_bayer[r, c] - wb_bayer[r, c_l2])
            g_N = ti.abs(wb_bayer[r_u1, c] - wb_bayer[r_u3, c]) + ti.abs(wb_bayer[r, c] - wb_bayer[r_u2, c])
            g_S = ti.abs(wb_bayer[r_d1, c] - wb_bayer[r_d3, c]) + ti.abs(wb_bayer[r, c] - wb_bayer[r_d2, c])

            w_E = 1.0 / ti.max(1e-5, (1.0 + g_E) * (1.0 + g_E))
            w_W = 1.0 / ti.max(1e-5, (1.0 + g_W) * (1.0 + g_W))
            w_N = 1.0 / ti.max(1e-5, (1.0 + g_N) * (1.0 + g_N))
            w_S = 1.0 / ti.max(1e-5, (1.0 + g_S) * (1.0 + g_S))

            val_E = wb_bayer[r, c_r1] + (wb_bayer[r, c] - wb_bayer[r, c_r2]) * 0.5
            val_W = wb_bayer[r, c_l1] + (wb_bayer[r, c] - wb_bayer[r, c_l2]) * 0.5
            val_N = wb_bayer[r_u1, c] + (wb_bayer[r, c] - wb_bayer[r_u2, c]) * 0.5
            val_S = wb_bayer[r_d1, c] + (wb_bayer[r, c] - wb_bayer[r_d2, c]) * 0.5

            green[r, c] = (w_E*val_E + w_W*val_W + w_N*val_N + w_S*val_S) / (w_E + w_W + w_N + w_S)

@ti.kernel
def _initial_color_difference_kernel(
    wb_bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
    r_diff: ti.types.ndarray(),
    b_diff: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    """Pass 2A: Dense Color Difference Initialization using bilinear interpolation of R-G and B-G."""
    r_red, c_red = 0, 0
    r_blue, c_blue = 0, 0
    if c00 == 0: r_red, c_red = 0, 0
    elif c01 == 0: r_red, c_red = 0, 1
    elif c10 == 0: r_red, c_red = 1, 0
    elif c11 == 0: r_red, c_red = 1, 1

    if c00 == 2: r_blue, c_blue = 0, 0
    elif c01 == 2: r_blue, c_blue = 0, 1
    elif c10 == 2: r_blue, c_blue = 1, 0
    elif c11 == 2: r_blue, c_blue = 1, 1

    for r, c in ti.ndrange(h, w):
        # --- Red Difference Interpolation ---
        r_mod = (r - r_red) % 2
        c_mod = (c - c_red) % 2
        val_r = 0.0
        if r_mod == 0 and c_mod == 0:
            val_r = wb_bayer[r, c] - green[r, c]
        elif r_mod == 0 and c_mod != 0:
            c_l = ti.math.clamp(c - 1, 0, w - 1)
            c_r = ti.math.clamp(c + 1, 0, w - 1)
            val_r = ((wb_bayer[r, c_l] - green[r, c_l]) + (wb_bayer[r, c_r] - green[r, c_r])) * 0.5
        elif r_mod != 0 and c_mod == 0:
            r_u = ti.math.clamp(r - 1, 0, h - 1)
            r_d = ti.math.clamp(r + 1, 0, h - 1)
            val_r = ((wb_bayer[r_u, c] - green[r_u, c]) + (wb_bayer[r_d, c] - green[r_d, c])) * 0.5
        else:
            r_u = ti.math.clamp(r - 1, 0, h - 1)
            r_d = ti.math.clamp(r + 1, 0, h - 1)
            c_l = ti.math.clamp(c - 1, 0, w - 1)
            c_r = ti.math.clamp(c + 1, 0, w - 1)
            val_r = (
                (wb_bayer[r_u, c_l] - green[r_u, c_l]) +
                (wb_bayer[r_u, c_r] - green[r_u, c_r]) +
                (wb_bayer[r_d, c_l] - green[r_d, c_l]) +
                (wb_bayer[r_d, c_r] - green[r_d, c_r])
            ) * 0.25
        r_diff[r, c] = val_r

        # --- Blue Difference Interpolation ---
        rb_mod = (r - r_blue) % 2
        cb_mod = (c - c_blue) % 2
        val_b = 0.0
        if rb_mod == 0 and cb_mod == 0:
            val_b = wb_bayer[r, c] - green[r, c]
        elif rb_mod == 0 and cb_mod != 0:
            c_l = ti.math.clamp(c - 1, 0, w - 1)
            c_r = ti.math.clamp(c + 1, 0, w - 1)
            val_b = ((wb_bayer[r, c_l] - green[r, c_l]) + (wb_bayer[r, c_r] - green[r, c_r])) * 0.5
        elif rb_mod != 0 and cb_mod == 0:
            r_u = ti.math.clamp(r - 1, 0, h - 1)
            r_d = ti.math.clamp(r + 1, 0, h - 1)
            val_b = ((wb_bayer[r_u, c] - green[r_u, c]) + (wb_bayer[r_d, c] - green[r_d, c])) * 0.5
        else:
            r_u = ti.math.clamp(r - 1, 0, h - 1)
            r_d = ti.math.clamp(r + 1, 0, h - 1)
            c_l = ti.math.clamp(c - 1, 0, w - 1)
            c_r = ti.math.clamp(c + 1, 0, w - 1)
            val_b = (
                (wb_bayer[r_u, c_l] - green[r_u, c_l]) +
                (wb_bayer[r_u, c_r] - green[r_u, c_r]) +
                (wb_bayer[r_d, c_l] - green[r_d, c_l]) +
                (wb_bayer[r_d, c_r] - green[r_d, c_r])
            ) * 0.25
        b_diff[r, c] = val_b

@ti.kernel
def _mlri_laplacian_coeff_kernel(
    guidance: ti.types.ndarray(),
    filt_input: ti.types.ndarray(),
    coeff_a: ti.types.ndarray(),
    coeff_b: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
    eps: ti.f32,
):
    """Pass 2B: MLRI (Minimized-Laplacian Residual Interpolation) coefficients calculation (5x5 local window)."""
    for r, c in ti.ndrange(h, w):
        sum_lap_GG = 0.0
        sum_lap_GT = 0.0
        sum_G = 0.0
        sum_diff = 0.0
        count = 0.0
        
        for dr, dc in ti.static(ti.ndrange((-2, 3), (-2, 3))):
            nr = r + dr
            nc = c + dc
            if 0 <= nr < h and 0 <= nc < w:
                # Clamp coordinates for discrete Laplacian stencil (North, South, West, East)
                nr_u = ti.math.clamp(nr - 1, 0, h - 1)
                nr_d = ti.math.clamp(nr + 1, 0, h - 1)
                nc_l = ti.math.clamp(nc - 1, 0, w - 1)
                nc_r = ti.math.clamp(nc + 1, 0, w - 1)
                
                # Guidance (Green) Laplacian at neighbor
                lap_G = (
                    guidance[nr_u, nc] + guidance[nr_d, nc] +
                    guidance[nr, nc_l] + guidance[nr, nc_r] -
                    4.0 * guidance[nr, nc]
                )
                
                # Difference Laplacian at neighbor
                lap_diff = (
                    filt_input[nr_u, nc] + filt_input[nr_d, nc] +
                    filt_input[nr, nc_l] + filt_input[nr, nc_r] -
                    4.0 * filt_input[nr, nc]
                )
                
                # Reconstructed target Laplacian (lap_diff is the Laplacian of the color difference R-G)
                lap_target = lap_diff
                
                sum_lap_GG += lap_G * lap_G
                sum_lap_GT += lap_G * lap_target
                
                sum_G += guidance[nr, nc]
                sum_diff += filt_input[nr, nc]
                count += 1.0
                
        mean_G = sum_G / count
        mean_diff = sum_diff / count
        mean_target = mean_diff
        
        coeff_a[r, c] = sum_lap_GT / ti.max(1e-6, sum_lap_GG + eps)
        coeff_b[r, c] = mean_target - coeff_a[r, c] * mean_G

@ti.kernel
def _guided_filter_apply_and_reconstruct_kernel(
    guidance: ti.types.ndarray(),
    coeff_a: ti.types.ndarray(),
    coeff_b: ti.types.ndarray(),
    output_channel: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
):
    """Pass 2C: Guided filter coefficients smoothing (5x5 local window) and channel reconstruction."""
    for r, c in ti.ndrange(h, w):
        sum_a = 0.0
        sum_b = 0.0
        count = 0.0
        
        for dr, dc in ti.static(ti.ndrange((-2, 3), (-2, 3))):
            nr = r + dr
            nc = c + dc
            if 0 <= nr < h and 0 <= nc < w:
                sum_a += coeff_a[nr, nc]
                sum_b += coeff_b[nr, nc]
                count += 1.0
                
        mean_a = sum_a / count
        mean_b = sum_b / count
        
        output_channel[r, c] = guidance[r, c] + (mean_a * guidance[r, c] + mean_b)

@ti.kernel
def _admm_step1_kernel(
    green: ti.types.ndarray(),
    red: ti.types.ndarray(),
    blue: ti.types.ndarray(),
    temp_r: ti.types.ndarray(),
    temp_b: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
):
    """Pass 3A: ADMM iteration Step 1 (Calculates cross-channel gradient updates to temp buffers)."""
    for r, c in ti.ndrange(h, w):
        sum_diff_R = 0.0
        sum_diff_B = 0.0
        count = 0.0
        
        for dr, dc in ti.static(ti.ndrange((-1, 2), (-1, 2))):
            nr = r + dr
            nc = c + dc
            if 0 <= nr < h and 0 <= nc < w:
                sum_diff_R += (red[nr, nc] - green[nr, nc])
                sum_diff_B += (blue[nr, nc] - green[nr, nc])
                count += 1.0
                
        temp_r[r, c] = green[r, c] + (sum_diff_R / count)
        temp_b[r, c] = green[r, c] + (sum_diff_B / count)

@ti.kernel
def _admm_step2_kernel(
    wb_bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
    red: ti.types.ndarray(),
    blue: ti.types.ndarray(),
    temp_r: ti.types.ndarray(),
    temp_b: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    """Pass 3B: ADMM iteration Step 2 (Stabilizing blend and enforcing sensor data fidelity)."""
    for r, c in ti.ndrange(h, w):
        R_new = temp_r[r, c] * 0.5 + red[r, c] * 0.5
        B_new = temp_b[r, c] * 0.5 + blue[r, c] * 0.5
        
        color_idx = 1
        r_mod = r % 2
        c_mod = c % 2
        if r_mod == 0:
            color_idx = c00 if c_mod == 0 else c01
        else:
            color_idx = c10 if c_mod == 0 else c11

        if color_idx == 0:
            red[r, c] = wb_bayer[r, c]
            blue[r, c] = B_new
        elif color_idx == 2:
            red[r, c] = R_new
            blue[r, c] = wb_bayer[r, c]
        else:
            green[r, c] = wb_bayer[r, c]
            red[r, c] = R_new
            blue[r, c] = B_new

@ti.kernel
def _mlri_admm_reconstruct_and_postprocess_kernel(
    green: ti.types.ndarray(),
    red: ti.types.ndarray(),
    blue: ti.types.ndarray(),
    cmatrix: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    h: ti.i32,
    w: ti.i32,
):
    """Pass 4: Final RGB Reconstruction and Color/Gamma transformations."""
    inv_wb_r = 1.0 / ti.max(0.1, wb_r)
    inv_wb_g = 1.0 / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
    inv_wb_b = 1.0 / ti.max(0.1, wb_b)

    for r, c in ti.ndrange(h, w):
        R = red[r, c]
        G = green[r, c]
        B = blue[r, c]

        # --- Advanced Highlight Recovery & Desaturation ---
        R_raw = R * inv_wb_r
        G_raw = G * inv_wb_g
        B_raw = B * inv_wb_b

        max_raw = ti.max(R_raw, ti.max(G_raw, B_raw))
        min_raw = ti.min(R_raw, ti.min(G_raw, B_raw))

        factor = ti.math.clamp((max_raw - 0.55) / 0.43, 0.0, 1.0)
        factor = factor * factor * (3.0 - 2.0 * factor)

        ratio = min_raw / ti.max(1e-5, max_raw)
        neutrality = ti.math.clamp((ratio - 0.40) / 0.45, 0.0, 1.0)
        neutrality = neutrality * neutrality * (3.0 - 2.0 * neutrality)

        final_factor = factor * neutrality

        L = ti.max(R, ti.max(G, B))
        R = R * (1.0 - final_factor) + L * final_factor
        G = G * (1.0 - final_factor) + L * final_factor
        B = B * (1.0 - final_factor) + L * final_factor

        # sRGB conversion & Gamma curve
        sR = cmatrix[0, 0] * R + cmatrix[0, 1] * G + cmatrix[0, 2] * B
        sG = cmatrix[1, 0] * R + cmatrix[1, 1] * G + cmatrix[1, 2] * B
        sB = cmatrix[2, 0] * R + cmatrix[2, 1] * G + cmatrix[2, 2] * B

        sR = sR / ti.math.sqrt(1.0 + sR * sR)
        sG = sG / ti.math.sqrt(1.0 + sG * sG)
        sB = sB / ti.math.sqrt(1.0 + sB * sB)

        dst[r, c, 0] = _fast_gamma(ti.math.clamp(sR, 0.0, 1.0))
        dst[r, c, 1] = _fast_gamma(ti.math.clamp(sG, 0.0, 1.0))
        dst[r, c, 2] = _fast_gamma(ti.math.clamp(sB, 0.0, 1.0))

@ti.func
def _get_green_gain(nr: ti.i32, nc: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32, wb_g1: ti.f32, wb_g2: ti.f32) -> ti.f32:
    color_idx = 1
    if nr % 2 == 0:
        color_idx = c00 if nc % 2 == 0 else c01
    else:
        color_idx = c10 if nc % 2 == 0 else c11
    return wb_g1 if color_idx == 1 else wb_g2

@ti.kernel
def _mlri_admm_green_to_grayscale_1channel_fused_kernel(
    bayer: ti.types.ndarray(),
    dst: ti.types.ndarray(),
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
    """FUSED 1-Channel (Grayscale Full-Res): Preprocessing and GBTF green interpolation only."""
    inv_range = 1.0 / ti.max(1.0, white - black)
    
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
            raw_val = ti.math.clamp((bayer[r, c] - black) * inv_range, 0.0, 1.0)
            gain = wb_g1 if color_idx == 1 else wb_g2
            dst[r, c] = raw_val * gain
        else:
            # Simple average for fast grayscale green interpolation
            c_left = ti.max(0, c - 1)
            c_right = ti.min(w - 1, c + 1)
            r_up = ti.max(0, r - 1)
            r_down = ti.min(h - 1, r + 1)
            
            raw_l = ti.math.clamp((bayer[r, c_left] - black) * inv_range, 0.0, 1.0)
            raw_r = ti.math.clamp((bayer[r, c_right] - black) * inv_range, 0.0, 1.0)
            raw_u = ti.math.clamp((bayer[r_up, c] - black) * inv_range, 0.0, 1.0)
            raw_d = ti.math.clamp((bayer[r_down, c] - black) * inv_range, 0.0, 1.0)
            
            gain_l = _get_green_gain(r, c_left, c00, c01, c10, c11, wb_g1, wb_g2)
            gain_r = _get_green_gain(r, c_right, c00, c01, c10, c11, wb_g1, wb_g2)
            gain_u = _get_green_gain(r_up, c, c00, c01, c10, c11, wb_g1, wb_g2)
            gain_d = _get_green_gain(r_down, c, c00, c01, c10, c11, wb_g1, wb_g2)
            
            dst[r, c] = (raw_l * gain_l + raw_r * gain_r + raw_u * gain_u + raw_d * gain_d) * 0.25

@ti.kernel
def _mlri_admm_green_half_res_fused_kernel(
    bayer: ti.types.ndarray(),
    dst: ti.types.ndarray(),
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
    """FUSED Bypass Demosaicing: Extract Green Sub-Sampling directly from RAW to 1/2 size grayscale."""
    inv_range = 1.0 / ti.max(1.0, white - black)
    
    for r, c in ti.ndrange(h // 2, w // 2):
        r_orig = r * 2
        c_orig = c * 2
        
        g_val = 0.0
        g_count = 0.0
        
        for dr, dc in ti.static([(0, 0), (0, 1), (1, 0), (1, 1)]):
            nr = r_orig + dr
            nc = c_orig + dc
            
            color_idx = 1
            nr_mod = nr % 2
            nc_mod = nc % 2
            if nr_mod == 0:
                color_idx = c00 if nc_mod == 0 else c01
            else:
                color_idx = c10 if nc_mod == 0 else c11
                
            is_green = (color_idx == 1) or (color_idx == 3)
            if is_green:
                raw_val = ti.math.clamp((bayer[nr, nc] - black) * inv_range, 0.0, 1.0)
                gain = wb_g1 if color_idx == 1 else wb_g2
                g_val += raw_val * gain
                g_count += 1.0
                
        if g_count > 0.0:
            dst[r, c] = g_val / g_count
        else:
            dst[r, c] = ti.math.clamp((bayer[r_orig, c_orig] - black) * inv_range, 0.0, 1.0)

@ti.kernel
def _mlri_admm_rgb_half_res_fused_kernel(
    bayer: ti.types.ndarray(),
    cmatrix: ti.types.ndarray(),
    dst: ti.types.ndarray(),
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
    """FUSED Bypass Demosaicing: Extract RGB Directly from Bayer 2x2 blocks to 1/2 size RGB."""
    inv_range = 1.0 / ti.max(1.0, white - black)
    
    for r, c in ti.ndrange(h // 2, w // 2):
        r_orig = r * 2
        c_orig = c * 2
        
        val_00 = ti.math.clamp((bayer[r_orig, c_orig] - black) * inv_range, 0.0, 1.0)
        val_01 = ti.math.clamp((bayer[r_orig, c_orig + 1] - black) * inv_range, 0.0, 1.0)
        val_10 = ti.math.clamp((bayer[r_orig + 1, c_orig] - black) * inv_range, 0.0, 1.0)
        val_11 = ti.math.clamp((bayer[r_orig + 1, c_orig + 1] - black) * inv_range, 0.0, 1.0)
        
        R, G1, B, G2 = 0.0, 0.0, 0.0, 0.0
        
        if c00 == 0: R = val_00
        elif c00 == 1: G1 = val_00
        elif c00 == 2: B = val_00
        else: G2 = val_00
        
        if c01 == 0: R = val_01
        elif c01 == 1: G1 = val_01
        elif c01 == 2: B = val_01
        else: G2 = val_01
        
        if c10 == 0: R = val_10
        elif c10 == 1: G1 = val_10
        elif c10 == 2: B = val_10
        else: G2 = val_10
        
        if c11 == 0: R = val_11
        elif c11 == 1: G1 = val_11
        elif c11 == 2: B = val_11
        else: G2 = val_11
        
        G_raw = (G1 + G2) * 0.5
        min_raw = ti.min(R, ti.min(G_raw, B))
        max_raw = ti.max(R, ti.max(G_raw, B))
        
        factor = ti.math.clamp((max_raw - 0.55) / 0.43, 0.0, 1.0)
        factor = factor * factor * (3.0 - 2.0 * factor)

        ratio = min_raw / ti.max(1e-5, max_raw)
        neutrality = ti.math.clamp((ratio - 0.40) / 0.45, 0.0, 1.0)
        neutrality = neutrality * neutrality * (3.0 - 2.0 * neutrality)

        final_factor = factor * neutrality

        R = R * wb_r
        G = (G1 * wb_g1 + G2 * wb_g2) * 0.5
        B = B * wb_b

        L = ti.max(R, ti.max(G, B))
        R = R * (1.0 - final_factor) + L * final_factor
        G = G * (1.0 - final_factor) + L * final_factor
        B = B * (1.0 - final_factor) + L * final_factor
        
        sR = cmatrix[0, 0] * R + cmatrix[0, 1] * G + cmatrix[0, 2] * B
        sG = cmatrix[1, 0] * R + cmatrix[1, 1] * G + cmatrix[1, 2] * B
        sB = cmatrix[2, 0] * R + cmatrix[2, 1] * G + cmatrix[2, 2] * B
        
        sR = sR / ti.math.sqrt(1.0 + sR * sR)
        sG = sG / ti.math.sqrt(1.0 + sG * sG)
        sB = sB / ti.math.sqrt(1.0 + sB * sB)
        
        dst[r, c, 0] = _fast_gamma(ti.math.clamp(sR, 0.0, 1.0))
        dst[r, c, 1] = _fast_gamma(ti.math.clamp(sG, 0.0, 1.0))
        dst[r, c, 2] = _fast_gamma(ti.math.clamp(sB, 0.0, 1.0))

@ti.kernel
def _mlri_admm_to_grayscale_3channel_kernel(
    green: ti.types.ndarray(),
    red: ti.types.ndarray(),
    blue: ti.types.ndarray(),
    cmatrix: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    h: ti.i32,
    w: ti.i32,
):
    """Full sRGB-Luma Demosaic to Grayscale 1-channel."""
    for r, c in ti.ndrange(h, w):
        R = red[r, c]
        G = green[r, c]
        B = blue[r, c]

        # Highlight desaturation
        R_raw = R / ti.max(0.1, wb_r)
        G_raw = G / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
        B_raw = B / ti.max(0.1, wb_b)

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

        luma = (
            0.299 * _fast_gamma(ti.math.clamp(sR, 0.0, 1.0)) +
            0.587 * _fast_gamma(ti.math.clamp(sG, 0.0, 1.0)) +
            0.114 * _fast_gamma(ti.math.clamp(sB, 0.0, 1.0))
        )
        dst[r, c] = luma

def compile_mlri_admm_tcm(arch, save_path):
    """Build and save the MLRI-ADMM AOT module."""
    ti.init(arch=arch)
    module = ti.aot.Module(arch)

    # Arguments definition
    bayer_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bayer", ti.f32, ndim=2)
    wb_bayer_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "wb_bayer", ti.f32, ndim=2)
    green_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "green", ti.f32, ndim=2)
    r_diff_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "r_diff", ti.f32, ndim=2)
    b_diff_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "b_diff", ti.f32, ndim=2)
    
    # 2 temporary arrays allocated by host for guided filter coefficients and ADMM double-buffering
    temp_a_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "temp_a", ti.f32, ndim=2)
    temp_b_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "temp_b", ti.f32, ndim=2)
    
    cmatrix_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "cmatrix", ti.f32, ndim=2)
    dst_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)

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
    
    denoise_strength_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "denoise_strength", ti.f32)

    # 1. Full RGB demosaic
    g_mlri_admm = ti.graph.GraphBuilder()
    g_mlri_admm.dispatch(
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
    # Stride-2 Bayer Bilateral Denoising: reads wb_bayer -> writes denoised to temp_a
    g_mlri_admm.dispatch(
        _bayer_bilateral_denoise_kernel,
        wb_bayer_arg,
        temp_a_arg,
        h_arg,
        w_arg,
        denoise_strength_arg,
    )
    # GBTF green interpolation reads denoised bayer (temp_a) -> writes to green
    g_mlri_admm.dispatch(
        _gbtf_green_interpolation_kernel,
        temp_a_arg,
        green_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )
    # Dense difference initialization: reads denoised bayer (temp_a) & green -> writes to r_diff, b_diff
    g_mlri_admm.dispatch(
        _initial_color_difference_kernel,
        temp_a_arg,
        green_arg,
        r_diff_arg,
        b_diff_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )
    # Guided filter for Red: inputs green (guidance) & r_diff (input), outputs to temp_a and temp_b
    eps_val = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "eps", ti.f32)
    g_mlri_admm.dispatch(
        _mlri_laplacian_coeff_kernel,
        green_arg,
        r_diff_arg,
        temp_a_arg,
        temp_b_arg,
        h_arg,
        w_arg,
        eps_val,
    )
    # Apply GF and reconstruct Red channel directly to r_diff
    g_mlri_admm.dispatch(
        _guided_filter_apply_and_reconstruct_kernel,
        green_arg,
        temp_a_arg,
        temp_b_arg,
        r_diff_arg,
        h_arg,
        w_arg,
    )
    # Guided filter for Blue: inputs green & b_diff, outputs to temp_a and temp_b
    g_mlri_admm.dispatch(
        _mlri_laplacian_coeff_kernel,
        green_arg,
        b_diff_arg,
        temp_a_arg,
        temp_b_arg,
        h_arg,
        w_arg,
        eps_val,
    )
    # Apply GF and reconstruct Blue channel directly to b_diff
    g_mlri_admm.dispatch(
        _guided_filter_apply_and_reconstruct_kernel,
        green_arg,
        temp_a_arg,
        temp_b_arg,
        b_diff_arg,
        h_arg,
        w_arg,
    )
    # Run 3 ADMM iterations (Double-Buffered)
    for _ in range(3):
        # Step 1: Reads r_diff, b_diff -> writes updates to temp_a, temp_b
        g_mlri_admm.dispatch(
            _admm_step1_kernel,
            green_arg,
            r_diff_arg,
            b_diff_arg,
            temp_a_arg,
            temp_b_arg,
            h_arg,
            w_arg,
        )
        # Step 2: Reads temp_a, temp_b -> writes stabilized & fidelity-enforced output back to r_diff, b_diff
        g_mlri_admm.dispatch(
            _admm_step2_kernel,
            wb_bayer_arg,
            green_arg,
            r_diff_arg,
            b_diff_arg,
            temp_a_arg,
            temp_b_arg,
            h_arg,
            w_arg,
            c00_arg,
            c01_arg,
            c10_arg,
            c11_arg,
        )
    g_mlri_admm.dispatch(
        _mlri_admm_reconstruct_and_postprocess_kernel,
        green_arg,
        r_diff_arg,
        b_diff_arg,
        cmatrix_arg,
        dst_arg,
        wb_r_arg,
        wb_g1_arg,
        wb_b_arg,
        wb_g2_arg,
        h_arg,
        w_arg,
    )
    module.add_graph("mlri_admm_demosaic", g_mlri_admm.compile())

    # 2. Fast 1-channel grayscale
    g_gray_1ch = ti.graph.GraphBuilder()
    dst_gray_1ch_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_gray_1ch.dispatch(
        _mlri_admm_green_to_grayscale_1channel_fused_kernel,
        bayer_arg,
        dst_gray_1ch_arg,
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
    module.add_graph("mlri_admm_demosaic_1channel", g_gray_1ch.compile())

    # 3. Half res green
    g_half_res = ti.graph.GraphBuilder()
    dst_half_res_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_half_res.dispatch(
        _mlri_admm_green_half_res_fused_kernel,
        bayer_arg,
        dst_half_res_arg,
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
    module.add_graph("mlri_admm_demosaic_half_res", g_half_res.compile())

    # 4. Half res RGB
    g_rgb_half_res = ti.graph.GraphBuilder()
    dst_rgb_half_res_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    g_rgb_half_res.dispatch(
        _mlri_admm_rgb_half_res_fused_kernel,
        bayer_arg,
        cmatrix_arg,
        dst_rgb_half_res_arg,
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
    module.add_graph("mlri_admm_demosaic_rgb_half_res", g_rgb_half_res.compile())

    # 5. Full 3-channel grayscale
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
        _bayer_bilateral_denoise_kernel,
        wb_bayer_arg,
        temp_a_arg,
        h_arg,
        w_arg,
        denoise_strength_arg,
    )
    g_gray_3ch.dispatch(
        _gbtf_green_interpolation_kernel,
        temp_a_arg,
        green_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )
    g_gray_3ch.dispatch(
        _initial_color_difference_kernel,
        temp_a_arg,
        green_arg,
        r_diff_arg,
        b_diff_arg,
        h_arg,
        w_arg,
        c00_arg,
        c01_arg,
        c10_arg,
        c11_arg,
    )
    g_gray_3ch.dispatch(
        _mlri_laplacian_coeff_kernel,
        green_arg,
        r_diff_arg,
        temp_a_arg,
        temp_b_arg,
        h_arg,
        w_arg,
        eps_val,
    )
    g_gray_3ch.dispatch(
        _guided_filter_apply_and_reconstruct_kernel,
        green_arg,
        temp_a_arg,
        temp_b_arg,
        r_diff_arg,
        h_arg,
        w_arg,
    )
    g_gray_3ch.dispatch(
        _mlri_laplacian_coeff_kernel,
        green_arg,
        b_diff_arg,
        temp_a_arg,
        temp_b_arg,
        h_arg,
        w_arg,
        eps_val,
    )
    g_gray_3ch.dispatch(
        _guided_filter_apply_and_reconstruct_kernel,
        green_arg,
        temp_a_arg,
        temp_b_arg,
        b_diff_arg,
        h_arg,
        w_arg,
    )
    for _ in range(3):
        g_gray_3ch.dispatch(
            _admm_step1_kernel,
            green_arg,
            r_diff_arg,
            b_diff_arg,
            temp_a_arg,
            temp_b_arg,
            h_arg,
            w_arg,
        )
        g_gray_3ch.dispatch(
            _admm_step2_kernel,
            wb_bayer_arg,
            green_arg,
            r_diff_arg,
            b_diff_arg,
            temp_a_arg,
            temp_b_arg,
            h_arg,
            w_arg,
            c00_arg,
            c01_arg,
            c10_arg,
            c11_arg,
        )
    g_gray_3ch.dispatch(
        _mlri_admm_to_grayscale_3channel_kernel,
        green_arg,
        r_diff_arg,
        b_diff_arg,
        cmatrix_arg,
        dst_gray_3ch_arg,
        wb_r_arg,
        wb_g1_arg,
        wb_b_arg,
        wb_g2_arg,
        h_arg,
        w_arg,
    )
    module.add_graph("mlri_admm_demosaic_3channel", g_gray_3ch.compile())

    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(os.path.join(script_dir, "../aot_tcm"))
    os.makedirs(assets_dir, exist_ok=True)

    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]

    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"mlri_admm_{suffix}.tcm"))
        try:
            compile_mlri_admm_tcm(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")