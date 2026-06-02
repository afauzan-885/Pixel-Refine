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

# Set AOT Mode

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
    Optimized: standard Hamilton-Adams 1-row/col gradient estimation (no redundant loops) for 3x memory bandwidth savings.
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
            if r > 1 and r < h - 2 and c > 1 and c < w - 2:
                dh = ti.abs(wb_bayer[r, c - 1] - wb_bayer[r, c + 1]) + ti.abs(
                    2.0 * wb_bayer[r, c] - wb_bayer[r, c - 2] - wb_bayer[r, c + 2]
                )
                dv = ti.abs(wb_bayer[r - 1, c] - wb_bayer[r + 1, c]) + ti.abs(
                    2.0 * wb_bayer[r, c] - wb_bayer[r - 2, c] - wb_bayer[r + 2, c]
                )

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
                    green[r, c] = (g_left + g_right + g_up + g_down) * 0.25 + (
                        4.0 * c_center - c_left2 - c_right2 - c_up2 - c_down2
                    ) * 0.125
                elif dh < dv:
                    green[r, c] = (g_left + g_right) * 0.5 + (
                        2.0 * c_center - c_left2 - c_right2
                    ) * 0.25
                else:
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
    Uses cached preprocessed wb_bayer for maximum performance.
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

        # --- Advanced Highlight Recovery & Desaturation ---
        R_raw = R / ti.max(0.1, wb_r)
        G_raw = G / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
        B_raw = B / ti.max(0.1, wb_b)

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

        # Highlight desaturation with color neutrality weight (protects saturated primary highlights like fire)
        min_raw = ti.min(R_raw, ti.min(G_raw, B_raw))
        max_raw = ti.max(R_raw, ti.max(G_raw, B_raw))
        
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

        dst[r, c, 0] = ti.math.pow(ti.math.clamp(sR, 0.0, 1.0), 1.0 / 2.22)
        dst[r, c, 1] = ti.math.pow(ti.math.clamp(sG, 0.0, 1.0), 1.0 / 2.22)
        dst[r, c, 2] = ti.math.pow(ti.math.clamp(sB, 0.0, 1.0), 1.0 / 2.22)


@ti.func
def _get_green_gain(nr: ti.i32, nc: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32, wb_g1: ti.f32, wb_g2: ti.f32) -> ti.f32:
    color_idx = 1
    if nr % 2 == 0:
        color_idx = c00 if nc % 2 == 0 else c01
    else:
        color_idx = c10 if nc % 2 == 0 else c11
    return wb_g1 if color_idx == 1 else wb_g2


@ti.kernel
def _ha_green_to_grayscale_1channel_fused_kernel(
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
    """FUSED 1-Channel (Grayscale Full-Res): Fuses preprocessing, normalization, white balance 
    and fast green demosaicing into a single fast GPU pass. Eliminates temporary memory footprint entirely.
    Optimized: static neighborhood fetching and fast WB mapping using hardware-friendly select branches.
    """
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
def _ha_green_half_res_fused_kernel(
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
    """FUSED Bypass Demosaicing: Extract Green Sub-Sampling directly from RAW to 1/2 size grayscale.
    Executes in a single pass without intermediate VRAM buffers (saving VRAM and bandwidth).
    """
    inv_range = 1.0 / ti.max(1.0, white - black)
    
    for r, c in ti.ndrange(h // 2, w // 2):
        r_orig = r * 2
        c_orig = c * 2
        
        g_val = 0.0
        g_count = 0.0
        
        for dr, dc in ti.static([(0, 0), (0, 1), (1, 0), (1, 1)]):
            nr, nc = r_orig + dr, c_orig + dc
            
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
def _ha_rgb_half_res_fused_kernel(
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
    """FUSED Bypass Demosaicing: Extract RGB Directly from Bayer 2x2 blocks to 1/2 size RGB.
    Executes in a single pass without intermediate VRAM buffers.
    """
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
        
        # Zero-overhead highlight desaturation to prevent magenta cast on overexposed regions
        # Protected by color neutrality weight (protects saturated highlights like fire/red lights)
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
        
        dst[r, c, 0] = ti.math.pow(ti.math.clamp(sR, 0.0, 1.0), 1.0 / 2.22)
        dst[r, c, 1] = ti.math.pow(ti.math.clamp(sG, 0.0, 1.0), 1.0 / 2.22)
        dst[r, c, 2] = ti.math.pow(ti.math.clamp(sB, 0.0, 1.0), 1.0 / 2.22)


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

    # 1. Define main RGB graph builder (Preprocessed path restored and optimized)
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

    # Dispatch Pass 1: Green Reconstruction using cached wb_bayer
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

    # Dispatch Pass 2: Red/Blue Reconstruction using cached wb_bayer
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

    # 2. Define 1-Channel (Green-only) Grayscale graph builder (Fused Single-Pass!)
    g_gray_1ch = ti.graph.GraphBuilder()
    dst_gray_1ch_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_gray_1ch.dispatch(
        _ha_green_to_grayscale_1channel_fused_kernel,
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
    module.add_graph("hamilton_demosaic_1channel", g_gray_1ch.compile())

    # 2b. Define Half-Res (Green Sub-sampling) Grayscale graph builder (Fused Single-Pass!)
    g_half_res = ti.graph.GraphBuilder()
    dst_half_res_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_half_res.dispatch(
        _ha_green_half_res_fused_kernel,
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
    module.add_graph("hamilton_demosaic_half_res", g_half_res.compile())

    # 2c. Define Half-Res (RGB Sub-sampling) graph builder (Fused Single-Pass!)
    g_rgb_half_res = ti.graph.GraphBuilder()
    dst_rgb_half_res_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    g_rgb_half_res.dispatch(
        _ha_rgb_half_res_fused_kernel,
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
    module.add_graph("hamilton_demosaic_rgb_half_res", g_rgb_half_res.compile())

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
