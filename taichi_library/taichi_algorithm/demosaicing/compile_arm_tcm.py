import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import sys

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from taichi_library.taichi_algorithm.aot_py.aot_artifact import archive_module
except ImportError:
    from aot_artifact import archive_module

@ti.func
def _fast_gamma(x: ti.f32) -> ti.f32:
    t = ti.math.sqrt(x)
    return t * (1.30547177 + t * (-0.78947190 + t * (0.79064221 - 0.30664208 * t)))

@ti.func
def _get_gain_fast(ym: ti.i32, xm: ti.i32, g00: ti.f32, g01: ti.f32, g10: ti.f32, g11: ti.f32) -> ti.f32:
    return ti.select(ym == 0, ti.select(xm == 0, g00, g01), ti.select(xm == 0, g10, g11))

@ti.func
def _get_green_gain(nr: ti.i32, nc: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32, wb_g1: ti.f32, wb_g2: ti.f32) -> ti.f32:
    color_idx = 1
    if nr % 2 == 0:
        color_idx = c00 if nc % 2 == 0 else c01
    else:
        color_idx = c10 if nc % 2 == 0 else c11
    return wb_g1 if color_idx == 1 else wb_g2

@ti.kernel
def _arm_preprocess_and_green_interpolation_kernel(
    bayer: ti.types.ndarray(),
    wb_bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
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
    """Pass 1: ARM Demosaice Green Channel Reconstruction.
    Preprocesses, normalizes, applies white balance, and interpolates Green using soft-decision weights.
    """
    inv_range = 1.0 / ti.max(1.0, white - black)
    gain_c00 = wb_r if c00==0 else (wb_g1 if c00==1 else (wb_b if c00==2 else wb_g2))
    gain_c01 = wb_r if c01==0 else (wb_g1 if c01==1 else (wb_b if c01==2 else wb_g2))
    gain_c10 = wb_r if c10==0 else (wb_g1 if c10==1 else (wb_b if c10==2 else wb_g2))
    gain_c11 = wb_r if c11==0 else (wb_g1 if c11==1 else (wb_b if c11==2 else wb_g2))

    for r, c in ti.ndrange(h, w):
        r_mod = r % 2
        c_mod = c % 2
        color_idx = ti.select(r_mod == 0, ti.select(c_mod == 0, c00, c01), ti.select(c_mod == 0, c10, c11))
        
        # Preprocess and Apply WB
        val = ti.math.clamp((bayer[r, c] - black) * inv_range, 0.0, 1.0)
        gain = _get_gain_fast(r_mod, c_mod, gain_c00, gain_c01, gain_c10, gain_c11)
        wb_bayer[r, c] = val * gain

    # Interpolate Green channel using Laplacian soft-decision edge weights
    for r, c in ti.ndrange(h, w):
        r_mod = r % 2
        c_mod = c % 2
        color_idx = ti.select(r_mod == 0, ti.select(c_mod == 0, c00, c01), ti.select(c_mod == 0, c10, c11))
        is_green = (color_idx == 1) or (color_idx == 3)

        if is_green:
            green[r, c] = wb_bayer[r, c]
        else:
            if r > 1 and r < h - 2 and c > 1 and c < w - 2:
                # ARM Multi-scale directional gradients
                dh = ti.abs(wb_bayer[r, c - 1] - wb_bayer[r, c + 1]) + ti.abs(2.0 * wb_bayer[r, c] - wb_bayer[r, c - 2] - wb_bayer[r, c + 2])
                dv = ti.abs(wb_bayer[r - 1, c] - wb_bayer[r + 1, c]) + ti.abs(2.0 * wb_bayer[r, c] - wb_bayer[r - 2, c] - wb_bayer[r + 2, c])

                # Soft decision weights
                eps = 1e-6
                dh_sq = dh * dh
                dv_sq = dv * dv
                w_h = dv_sq / (dh_sq + dv_sq + eps)
                w_v = 1.0 - w_h

                # Edge-directed interpolations
                g_h = (wb_bayer[r, c - 1] + wb_bayer[r, c + 1]) * 0.5 + (2.0 * wb_bayer[r, c] - wb_bayer[r, c - 2] - wb_bayer[r, c + 2]) * 0.25
                g_v = (wb_bayer[r - 1, c] + wb_bayer[r + 1, c]) * 0.5 + (2.0 * wb_bayer[r, c] - wb_bayer[r - 2, c] - wb_bayer[r + 2, c]) * 0.25
                green[r, c] = w_h * g_h + w_v * g_v
            else:
                # Boundary pixels fallback
                g_val = 0.0
                g_count = 0.0
                for dr, dc in ti.static([(-1, 0), (1, 0), (0, -1), (0, 1)]):
                    nr, nc = r + dr, c + dc
                    if nr >= 0 and nr < h and nc >= 0 and nc < w:
                        g_val += wb_bayer[nr, nc]
                        g_count += 1.0
                green[r, c] = g_val / g_count

@ti.kernel
def _arm_red_blue_residual_kernel(
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
    """Pass 2: Reconstruct R and B channels into residual differences (R - G and B - G)"""
    for r, c in ti.ndrange(h, w):
        r_mod = r % 2
        c_mod = c % 2
        color_idx = ti.select(r_mod == 0, ti.select(c_mod == 0, c00, c01), ti.select(c_mod == 0, c10, c11))
        
        R, B = 0.0, 0.0
        G = green[r, c]

        if color_idx == 0:  # Red pixel
            R = wb_bayer[r, c]
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                # Diagonal Laplacian weights
                g_diff_diag1 = ti.abs(green[r - 1, c - 1] - green[r + 1, c + 1])
                g_diff_diag2 = ti.abs(green[r - 1, c + 1] - green[r + 1, c - 1])
                w1 = 1.0 / (1.0 + g_diff_diag1)
                w2 = 1.0 / (1.0 + g_diff_diag2)
                
                b_diff_val = (
                    w1 * (wb_bayer[r - 1, c - 1] - green[r - 1, c - 1] + wb_bayer[r + 1, c + 1] - green[r + 1, c + 1]) +
                    w2 * (wb_bayer[r - 1, c + 1] - green[r - 1, c + 1] + wb_bayer[r + 1, c - 1] - green[r + 1, c - 1])
                ) / (2.0 * (w1 + w2))
                B = G + b_diff_val
            else:
                B = G
        elif color_idx == 2:  # Blue pixel
            B = wb_bayer[r, c]
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                g_diff_diag1 = ti.abs(green[r - 1, c - 1] - green[r + 1, c + 1])
                g_diff_diag2 = ti.abs(green[r - 1, c + 1] - green[r + 1, c - 1])
                w1 = 1.0 / (1.0 + g_diff_diag1)
                w2 = 1.0 / (1.0 + g_diff_diag2)

                r_diff_val = (
                    w1 * (wb_bayer[r - 1, c - 1] - green[r - 1, c - 1] + wb_bayer[r + 1, c + 1] - green[r + 1, c + 1]) +
                    w2 * (wb_bayer[r - 1, c + 1] - green[r - 1, c + 1] + wb_bayer[r + 1, c - 1] - green[r + 1, c - 1])
                ) / (2.0 * (w1 + w2))
                R = G + r_diff_val
            else:
                R = G
        else:  # Green pixel
            is_red_horizontal = False
            if r_mod == 0:
                is_red_horizontal = (c00 if c_mod == 1 else c01) == 0
            else:
                is_red_horizontal = (c10 if c_mod == 1 else c11) == 0

            if is_red_horizontal:
                R = G + (wb_bayer[r, ti.max(0, c - 1)] - green[r, ti.max(0, c - 1)] + wb_bayer[r, ti.min(w - 1, c + 1)] - green[r, ti.min(w - 1, c + 1)]) * 0.5
                B = G + (wb_bayer[ti.max(0, r - 1), c] - green[ti.max(0, r - 1), c] + wb_bayer[ti.min(h - 1, r + 1), c] - green[ti.min(h - 1, r + 1), c]) * 0.5
            else:
                B = G + (wb_bayer[r, ti.max(0, c - 1)] - green[r, ti.max(0, c - 1)] + wb_bayer[r, ti.min(w - 1, c + 1)] - green[r, ti.min(w - 1, c + 1)]) * 0.5
                R = G + (wb_bayer[ti.max(0, r - 1), c] - green[ti.max(0, r - 1), c] + wb_bayer[ti.min(h - 1, r + 1), c] - green[ti.min(h - 1, r + 1), c]) * 0.5

        r_diff[r, c] = R - G
        b_diff[r, c] = B - G

@ti.kernel
def _arm_median_filter_3x3_kernel(
    src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int
):
    """Highly optimized 3x3 Median Filter on difference residual channels"""
    for y, x in ti.ndrange(h, w):
        vals = ti.Vector([0.0] * 9)
        idx = 0
        for dy in ti.static(range(-1, 2)):
            for dx in ti.static(range(-1, 2)):
                ny = ti.math.clamp(y + dy, 0, h - 1)
                nx = ti.math.clamp(x + dx, 0, w - 1)
                vals[idx] = src[ny, nx]
                idx += 1
        # In-register sort
        for i in range(9):
            for j in range(i + 1, 9):
                if vals[j] < vals[i]:
                    vals[i], vals[j] = vals[j], vals[i]
        dst[y, x] = vals[4]

@ti.kernel
def _arm_reconstruct_and_postprocess_kernel(
    green: ti.types.ndarray(),
    r_diff_filtered: ti.types.ndarray(),
    b_diff_filtered: ti.types.ndarray(),
    cmatrix: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    h: ti.i32,
    w: ti.i32,
):
    """Pass 3: Reconstruct camera RGB and recover highlights."""
    inv_wb_r = 1.0 / ti.max(0.1, wb_r)
    inv_wb_g = 1.0 / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
    inv_wb_b = 1.0 / ti.max(0.1, wb_b)

    for r, c in ti.ndrange(h, w):
        G = green[r, c]
        R = G + r_diff_filtered[r, c]
        B = G + b_diff_filtered[r, c]

        # Highlight Recovery & Neutral Desaturation
        R_raw = R * inv_wb_r
        G_raw = G * inv_wb_g
        B_raw = B * inv_wb_b

        max_raw = ti.max(R_raw, ti.max(G_raw, B_raw))
        min_raw = ti.min(R_raw, ti.min(G_raw, B_raw))

        # Sensor-channel ratios near clipping are unreliable. Neutralize them
        # before the camera matrix to prevent magenta highlight fringes.
        factor = ti.math.clamp((max_raw - 0.45) / 0.35, 0.0, 1.0)
        factor = factor * factor * (3.0 - 2.0 * factor)

        ratio = min_raw / ti.max(1e-5, max_raw)
        chroma_damage = ti.math.clamp((0.82 - ratio) / 0.52, 0.0, 1.0)
        chroma_damage = chroma_damage * chroma_damage * (3.0 - 2.0 * chroma_damage)

        final_factor = factor * chroma_damage

        neutral = (R + G + B) / 3.0
        R = R * (1.0 - final_factor) + neutral * final_factor
        G = G * (1.0 - final_factor) + neutral * final_factor
        B = B * (1.0 - final_factor) + neutral * final_factor

        # Return white-balanced camera RGB. Color conversion and display tone
        # mapping are separate downstream modules.
        dst[r, c, 0] = ti.max(R, 0.0)
        dst[r, c, 1] = ti.max(G, 0.0)
        dst[r, c, 2] = ti.max(B, 0.0)

@ti.kernel
def _pure_arm_demosaic_kernel(
    bayer: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    black: ti.f32,
    white: ti.f32,
    h: ti.i32,
    w: ti.i32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
):
    """Pure ARM demosaicing (Fast Bilinear fallback for pure metrics check, no WB/Color space mapping)"""
    inv_range = 1.0 / ti.max(1.0, white - black)
    for r, c in ti.ndrange(h, w):
        r_mod = r % 2
        c_mod = c % 2
        color_idx = ti.select(r_mod == 0, ti.select(c_mod == 0, c00, c01), ti.select(c_mod == 0, c10, c11))
            
        r_up = ti.max(0, r - 1)
        r_down = ti.min(h - 1, r + 1)
        c_left = ti.max(0, c - 1)
        c_right = ti.min(w - 1, c + 1)
        
        v11 = ti.math.clamp((bayer[r, c] - black) * inv_range, 0.0, 1.0)
        v01 = ti.math.clamp((bayer[r_up, c] - black) * inv_range, 0.0, 1.0)
        v21 = ti.math.clamp((bayer[r_down, c] - black) * inv_range, 0.0, 1.0)
        v10 = ti.math.clamp((bayer[r, c_left] - black) * inv_range, 0.0, 1.0)
        v12 = ti.math.clamp((bayer[r, c_right] - black) * inv_range, 0.0, 1.0)
        
        R, G, B = 0.0, 0.0, 0.0
        
        if color_idx == 0:  # Red center
            v00 = ti.math.clamp((bayer[r_up, c_left] - black) * inv_range, 0.0, 1.0)
            v02 = ti.math.clamp((bayer[r_up, c_right] - black) * inv_range, 0.0, 1.0)
            v20 = ti.math.clamp((bayer[r_down, c_left] - black) * inv_range, 0.0, 1.0)
            v22 = ti.math.clamp((bayer[r_down, c_right] - black) * inv_range, 0.0, 1.0)
            
            R = v11
            G = (v01 + v10 + v12 + v21) * 0.25
            B = (v00 + v02 + v20 + v22) * 0.25
        elif color_idx == 2:  # Blue center
            v00 = ti.math.clamp((bayer[r_up, c_left] - black) * inv_range, 0.0, 1.0)
            v02 = ti.math.clamp((bayer[r_up, c_right] - black) * inv_range, 0.0, 1.0)
            v20 = ti.math.clamp((bayer[r_down, c_left] - black) * inv_range, 0.0, 1.0)
            v22 = ti.math.clamp((bayer[r_down, c_right] - black) * inv_range, 0.0, 1.0)
            
            B = v11
            G = (v01 + v10 + v12 + v21) * 0.25
            R = (v00 + v02 + v20 + v22) * 0.25
        else:  # Green center
            G = v11
            horiz_idx = c00 if r_mod == 0 else c10
            if (c_left % 2) != 0:
                horiz_idx = c01 if r_mod == 0 else c11
                
            if horiz_idx == 0:
                R = (v10 + v12) * 0.5
                B = (v01 + v21) * 0.5
            else:
                B = (v10 + v12) * 0.5
                R = (v01 + v21) * 0.5
                
        dst[r, c, 0] = R
        dst[r, c, 1] = G
        dst[r, c, 2] = B

@ti.kernel
def _arm_green_to_grayscale_1channel_fused_kernel(
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
    """Green only ARM demosaic (Fast luma fallback)"""
    inv_range = 1.0 / ti.max(1.0, white - black)
    
    for r, c in ti.ndrange(h, w):
        r_mod = r % 2
        c_mod = c % 2
        color_idx = ti.select(r_mod == 0, ti.select(c_mod == 0, c00, c01), ti.select(c_mod == 0, c10, c11))
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
def _arm_green_half_res_fused_kernel(
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
    inv_range = 1.0 / ti.max(1.0, white - black)
    
    for r, c in ti.ndrange(h // 2, w // 2):
        r_orig = r * 2
        c_orig = c * 2
        g_val = 0.0
        g_count = 0.0
        
        for dr, dc in ti.static([(0, 0), (0, 1), (1, 0), (1, 1)]):
            nr, nc = r_orig + dr, c_orig + dc
            nr_mod = nr % 2
            nc_mod = nc % 2
            color_idx = ti.select(nr_mod == 0, ti.select(nc_mod == 0, c00, c01), ti.select(nc_mod == 0, c10, c11))
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
def _arm_rgb_half_res_fused_kernel(
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

def compile_arm_tcm(arch=ti.vulkan, save_path="arm_vulkan.tcm"):
    print(f"\n>>> Compiling ARM Demosaice AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)
    
    # Graphs argument declarations
    bayer_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bayer", ti.f32, ndim=2)
    cmatrix_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "cmatrix", ti.f32, ndim=2)
    dst_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    
    wb_bayer_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "wb_bayer", ti.f32, ndim=2)
    green_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "green", ti.f32, ndim=2)
    r_diff_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "r_diff", ti.f32, ndim=2)
    b_diff_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "b_diff", ti.f32, ndim=2)
    r_diff_f_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "r_diff_filtered", ti.f32, ndim=2)
    b_diff_f_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "b_diff_filtered", ti.f32, ndim=2)

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

    # 1. arm_demosaic Graph (3-Pass Fused)
    g_arm = ti.graph.GraphBuilder()
    g_arm.dispatch(
        _arm_preprocess_and_green_interpolation_kernel,
        bayer_arg, wb_bayer_arg, green_arg,
        wb_r_arg, wb_g1_arg, wb_b_arg, wb_g2_arg,
        black_arg, white_arg, h_arg, w_arg,
        c00_arg, c01_arg, c10_arg, c11_arg
    )
    g_arm.dispatch(
        _arm_red_blue_residual_kernel,
        wb_bayer_arg, green_arg, r_diff_arg, b_diff_arg,
        h_arg, w_arg, c00_arg, c01_arg, c10_arg, c11_arg
    )
    g_arm.dispatch(
        _arm_median_filter_3x3_kernel,
        r_diff_arg, r_diff_f_arg, h_arg, w_arg
    )
    g_arm.dispatch(
        _arm_median_filter_3x3_kernel,
        b_diff_arg, b_diff_f_arg, h_arg, w_arg
    )
    g_arm.dispatch(
        _arm_reconstruct_and_postprocess_kernel,
        green_arg, r_diff_f_arg, b_diff_f_arg, cmatrix_arg, dst_arg,
        wb_r_arg, wb_g1_arg, wb_b_arg, wb_g2_arg, h_arg, w_arg
    )
    module.add_graph("arm_demosaic", g_arm.compile())
    
    # 2. pure_arm_demosaic Graph
    g_pure = ti.graph.GraphBuilder()
    g_pure.dispatch(
        _pure_arm_demosaic_kernel,
        bayer_arg, dst_arg, black_arg, white_arg,
        h_arg, w_arg, c00_arg, c01_arg, c10_arg, c11_arg
    )
    module.add_graph("pure_arm_demosaic", g_pure.compile())
    
    # 3. arm_demosaic_1channel Graph
    g_gray_1ch = ti.graph.GraphBuilder()
    dst_gray_1ch_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_gray_1ch.dispatch(
        _arm_green_to_grayscale_1channel_fused_kernel,
        bayer_arg, dst_gray_1ch_arg,
        wb_r_arg, wb_g1_arg, wb_b_arg, wb_g2_arg,
        black_arg, white_arg, h_arg, w_arg,
        c00_arg, c01_arg, c10_arg, c11_arg
    )
    module.add_graph("arm_demosaic_1channel", g_gray_1ch.compile())

    # 4. arm_demosaic_half_res Graph
    g_half_res = ti.graph.GraphBuilder()
    dst_half_res_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_half_res.dispatch(
        _arm_green_half_res_fused_kernel,
        bayer_arg, dst_half_res_arg,
        wb_r_arg, wb_g1_arg, wb_b_arg, wb_g2_arg,
        black_arg, white_arg, h_arg, w_arg,
        c00_arg, c01_arg, c10_arg, c11_arg
    )
    module.add_graph("arm_demosaic_half_res", g_half_res.compile())

    # 5. arm_demosaic_rgb_half_res Graph
    g_rgb_half_res = ti.graph.GraphBuilder()
    dst_rgb_half_res_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    g_rgb_half_res.dispatch(
        _arm_rgb_half_res_fused_kernel,
        bayer_arg, cmatrix_arg, dst_rgb_half_res_arg,
        wb_r_arg, wb_g1_arg, wb_b_arg, wb_g2_arg,
        black_arg, white_arg, h_arg, w_arg,
        c00_arg, c01_arg, c10_arg, c11_arg
    )
    module.add_graph("arm_demosaic_rgb_half_res", g_rgb_half_res.compile())

    # 6. rgb_to_bgr_i32 Graph
    g_conv = ti.graph.GraphBuilder()
    src_conv_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_conv_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=3)
    h_conv_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_conv_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    g_conv.dispatch(
        _rgb_to_bgr_i32_kernel, src_conv_arg, dst_conv_arg, h_conv_arg, w_conv_arg
    )
    module.add_graph("rgb_to_bgr_i32", g_conv.compile())

    archive_module(module, save_path)
    print(f"Successfully compiled ARM and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = file_dir
    assets_dir = os.path.abspath(os.path.join(script_dir, "../aot_tcm"))
    os.makedirs(assets_dir, exist_ok=True)
    
    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]
    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"arm_{suffix}.tcm"))
        try:
            compile_arm_tcm(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
