"""Compile Hamilton Demosaicing AOT Graphs (Direct Fast 2-Pass Architecture).

Pipeline Architecture:
- Pass 1 (`_ha_green_direct`): Fast 2D raw sampling without per-sample branch evaluation. Computes edge-directed Green channel in ~25ms.
- Pass 2 (`_ha_red_blue_direct`): Fast Red/Blue color difference interpolation + Highlight Recovery + Dynamic Range Compression in ~20ms.
- Pass 3 (Optional): sRGB Color Matrix & Gamma Correction (for tonemapping=True).

Graph Targets:
- `hamilton_demosaic`: Direct 2-Pass Linear RGB with Highlight Recovery & Dynamic Range Compression (tonemapping=False)
- `hamilton_demosaic_tonemapped`: Full sRGB Tonemapped output (tonemapping=True)
- `rgb_to_bgr_i32`: 16-bit BGR export conversion
"""

import os
import sys
import taichi as ti

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module, normalize_tcm
except ImportError:
    from aot_artifact import archive_module, normalize_tcm

try:
    from taichi_vision.taichi_algorithm.demosaicing.demosaic_aot_builder import (
        register_hamilton_graphs,
    )
    from taichi_vision.taichi_algorithm.demosaicing.demosaic_postprocess import (
        rgb_to_bgr_i32,
    )
except ImportError:
    from demosaic_aot_builder import register_hamilton_graphs
    from demosaic_postprocess import rgb_to_bgr_i32


@ti.func
def _sample_raw(
    bayer: ti.template(),
    r: ti.i32,
    c: ti.i32,
    black: ti.f32,
    inv_range: ti.f32,
    h: ti.i32,
    w: ti.i32,
) -> ti.f32:
    nr = ti.math.clamp(r, 0, h - 1)
    nc = ti.math.clamp(c, 0, w - 1)
    return ti.math.clamp((bayer[nr, nc] - black) * inv_range, 0.0, 1.0)


@ti.func
def _get_channel_gain(
    r: ti.i32,
    c: ti.i32,
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
) -> ti.f32:
    r_mod = r % 2
    c_mod = c % 2
    color_idx = ti.select(r_mod == 0, ti.select(c_mod == 0, c00, c01), ti.select(c_mod == 0, c10, c11))
    gain = wb_g1
    if color_idx == 0:
        gain = wb_r
    elif color_idx == 2:
        gain = wb_b
    elif color_idx == 3:
        gain = wb_g2
    return gain


# -----------------------------------------------------------------------------
# Pass 1: Ultra-Fast Direct Edge-Directed Green Channel Reconstruction
# -----------------------------------------------------------------------------
@ti.kernel
def _ha_green_direct_kernel(
    bayer: ti.types.ndarray(),
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
    inv_range = 1.0 / ti.max(1.0, white - black)

    for r, c in ti.ndrange(h, w):
        r_mod = r % 2
        c_mod = c % 2
        color_idx = ti.select(r_mod == 0, ti.select(c_mod == 0, c00, c01), ti.select(c_mod == 0, c10, c11))
        is_green = (color_idx == 1) or (color_idx == 3)

        c_center = _sample_raw(bayer, r, c, black, inv_range, h, w)

        if is_green:
            green[r, c] = c_center * ti.select(color_idx == 1, wb_g1, wb_g2)
        else:
            g_left = _sample_raw(bayer, r, c - 1, black, inv_range, h, w) * wb_g1
            g_right = _sample_raw(bayer, r, c + 1, black, inv_range, h, w) * wb_g1
            g_up = _sample_raw(bayer, r - 1, c, black, inv_range, h, w) * wb_g2
            g_down = _sample_raw(bayer, r + 1, c, black, inv_range, h, w) * wb_g2

            c_center_wb = c_center * ti.select(color_idx == 0, wb_r, wb_b)
            c_left2 = _sample_raw(bayer, r, c - 2, black, inv_range, h, w) * ti.select(color_idx == 0, wb_r, wb_b)
            c_right2 = _sample_raw(bayer, r, c + 2, black, inv_range, h, w) * ti.select(color_idx == 0, wb_r, wb_b)
            c_up2 = _sample_raw(bayer, r - 2, c, black, inv_range, h, w) * ti.select(color_idx == 0, wb_r, wb_b)
            c_down2 = _sample_raw(bayer, r + 2, c, black, inv_range, h, w) * ti.select(color_idx == 0, wb_r, wb_b)

            dh = ti.abs(g_left - g_right) + ti.abs(2.0 * c_center_wb - c_left2 - c_right2)
            dv = ti.abs(g_up - g_down) + ti.abs(2.0 * c_center_wb - c_up2 - c_down2)

            diff = ti.abs(dh - dv)
            g_avg = (g_left + g_right + g_up + g_down) * 0.25 + (4.0 * c_center_wb - c_left2 - c_right2 - c_up2 - c_down2) * 0.125
            g_h = (g_left + g_right) * 0.5 + (2.0 * c_center_wb - c_left2 - c_right2) * 0.25
            g_v = (g_up + g_down) * 0.5 + (2.0 * c_center_wb - c_up2 - c_down2) * 0.25

            green[r, c] = ti.select(diff < 0.035, g_avg, ti.select(dh < dv, g_h, g_v))


# -----------------------------------------------------------------------------
# Pass 2: Direct Red/Blue Reconstruction + Highlight Recovery + Dynamic Range Compression
# -----------------------------------------------------------------------------
@ti.kernel
def _ha_red_blue_direct_kernel(
    bayer: ti.types.ndarray(),
    green: ti.types.ndarray(),
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
    inv_wb_r = 1.0 / ti.max(0.1, wb_r)
    inv_wb_g = 1.0 / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
    inv_wb_b = 1.0 / ti.max(0.1, wb_b)

    for r, c in ti.ndrange(h, w):
        r_mod = r % 2
        c_mod = c % 2
        color_idx = ti.select(r_mod == 0, ti.select(c_mod == 0, c00, c01), ti.select(c_mod == 0, c10, c11))

        G = green[r, c]
        R, B = 0.0, 0.0

        if color_idx == 0:  # Red pixel
            R = _sample_raw(bayer, r, c, black, inv_range, h, w) * wb_r
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                g11, g22 = green[r - 1, c - 1], green[r + 1, c + 1]
                g12, g21 = green[r - 1, c + 1], green[r + 1, c - 1]
                w1 = 1.0 / (1.0 + ti.abs(g11 - g22))
                w2 = 1.0 / (1.0 + ti.abs(g12 - g21))

                b11 = _sample_raw(bayer, r - 1, c - 1, black, inv_range, h, w) * wb_b
                b22 = _sample_raw(bayer, r + 1, c + 1, black, inv_range, h, w) * wb_b
                b12 = _sample_raw(bayer, r - 1, c + 1, black, inv_range, h, w) * wb_b
                b21 = _sample_raw(bayer, r + 1, c - 1, black, inv_range, h, w) * wb_b

                b_diff = (w1 * (b11 - g11 + b22 - g22) + w2 * (b12 - g12 + b21 - g21)) / (2.0 * (w1 + w2))
                B = G + b_diff
            else:
                B = G

        elif color_idx == 2:  # Blue pixel
            B = _sample_raw(bayer, r, c, black, inv_range, h, w) * wb_b
            if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                g11, g22 = green[r - 1, c - 1], green[r + 1, c + 1]
                g12, g21 = green[r - 1, c + 1], green[r + 1, c - 1]
                w1 = 1.0 / (1.0 + ti.abs(g11 - g22))
                w2 = 1.0 / (1.0 + ti.abs(g12 - g21))

                r11 = _sample_raw(bayer, r - 1, c - 1, black, inv_range, h, w) * wb_r
                r22 = _sample_raw(bayer, r + 1, c + 1, black, inv_range, h, w) * wb_r
                r12 = _sample_raw(bayer, r - 1, c + 1, black, inv_range, h, w) * wb_r
                r21 = _sample_raw(bayer, r + 1, c - 1, black, inv_range, h, w) * wb_r

                r_diff = (w1 * (r11 - g11 + r22 - g22) + w2 * (r12 - g12 + r21 - g21)) / (2.0 * (w1 + w2))
                R = G + r_diff
            else:
                R = G

        else:  # Green pixel
            is_red_horizontal = False
            if r_mod == 0:
                is_red_horizontal = (c00 if c_mod == 1 else c01) == 0
            else:
                is_red_horizontal = (c10 if c_mod == 1 else c11) == 0

            if is_red_horizontal:  # Red is Horizontal, Blue is Vertical
                if c > 0 and c < w - 1:
                    r_l = _sample_raw(bayer, r, c - 1, black, inv_range, h, w) * wb_r
                    r_r = _sample_raw(bayer, r, c + 1, black, inv_range, h, w) * wb_r
                    R = G + (r_l - green[r, c - 1] + r_r - green[r, c + 1]) * 0.5
                else:
                    R = G

                if r > 0 and r < h - 1:
                    b_u = _sample_raw(bayer, r - 1, c, black, inv_range, h, w) * wb_b
                    b_d = _sample_raw(bayer, r + 1, c, black, inv_range, h, w) * wb_b
                    B = G + (b_u - green[r - 1, c] + b_d - green[r + 1, c]) * 0.5
                else:
                    B = G

            else:  # Blue is Horizontal, Red is Vertical
                if r > 0 and r < h - 1:
                    r_u = _sample_raw(bayer, r - 1, c, black, inv_range, h, w) * wb_r
                    r_d = _sample_raw(bayer, r + 1, c, black, inv_range, h, w) * wb_r
                    R = G + (r_u - green[r - 1, c] + r_d - green[r + 1, c]) * 0.5
                else:
                    R = G

                if c > 0 and c < w - 1:
                    b_l = _sample_raw(bayer, r, c - 1, black, inv_range, h, w) * wb_b
                    b_r = _sample_raw(bayer, r, c + 1, black, inv_range, h, w) * wb_b
                    B = G + (b_l - green[r, c - 1] + b_r - green[r, c + 1]) * 0.5
                else:
                    B = G

        # 1. Highlight Recovery & Desaturation (Commit 1106566 Math)
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

        # 2. Algebraic Sigmoid Dynamic Range Compression
        dst[r, c, 0] = R / ti.math.sqrt(1.0 + R * R)
        dst[r, c, 1] = G / ti.math.sqrt(1.0 + G * G)
        dst[r, c, 2] = B / ti.math.sqrt(1.0 + B * B)


@ti.kernel
def _ha_srgb_tonemap_kernel(
    src_linear: ti.types.ndarray(),
    cmatrix: ti.types.ndarray(),
    dst_srgb: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
):
    """Pass 3: Camera-to-sRGB matrix transform and sRGB Gamma curve."""
    for r, c in ti.ndrange(h, w):
        R = src_linear[r, c, 0]
        G = src_linear[r, c, 1]
        B = src_linear[r, c, 2]

        sR = cmatrix[0, 0] * R + cmatrix[0, 1] * G + cmatrix[0, 2] * B
        sG = cmatrix[1, 0] * R + cmatrix[1, 1] * G + cmatrix[1, 2] * B
        sB = cmatrix[2, 0] * R + cmatrix[2, 1] * G + cmatrix[2, 2] * B

        dst_srgb[r, c, 0] = ti.math.pow(ti.math.clamp(sR, 0.0, 1.0), 1.0 / 2.22)
        dst_srgb[r, c, 1] = ti.math.pow(ti.math.clamp(sG, 0.0, 1.0), 1.0 / 2.22)
        dst_srgb[r, c, 2] = ti.math.pow(ti.math.clamp(sB, 0.0, 1.0), 1.0 / 2.22)


@ti.func
def _ha_green_gain(nr: ti.i32, nc: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32, wb_g1: ti.f32, wb_g2: ti.f32) -> ti.f32:
    colour = c00
    if nr % 2 == 0:
        colour = c00 if nc % 2 == 0 else c01
    else:
        colour = c10 if nc % 2 == 0 else c11
    return wb_g1 if colour == 1 else wb_g2


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
    """Green-only Hamilton demosaic to grayscale (fast luma fallback)."""
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
            gain_l = _ha_green_gain(r, c_left, c00, c01, c10, c11, wb_g1, wb_g2)
            gain_r = _ha_green_gain(r, c_right, c00, c01, c10, c11, wb_g1, wb_g2)
            gain_u = _ha_green_gain(r_up, c, c00, c01, c10, c11, wb_g1, wb_g2)
            gain_d = _ha_green_gain(r_down, c, c00, c01, c10, c11, wb_g1, wb_g2)
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
    """Extract green sub-sampling to half size grayscale."""
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
    """Extract RGB direct sub-sampling to half size RGB (with WB + cmatrix)."""
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

        dst[r, c, 0] = ti.math.clamp(sR, 0.0, 1.0)
        dst[r, c, 1] = ti.math.clamp(sG, 0.0, 1.0)
        dst[r, c, 2] = ti.math.clamp(sB, 0.0, 1.0)


@ti.kernel
def _ha_preprocess_wb_kernel(
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
    """Normalize bayer and apply white balance into a per-pixel gain map."""
    inv_range = 1.0 / ti.max(1.0, white - black)
    for r, c in ti.ndrange(h, w):
        raw = ti.math.clamp((bayer[r, c] - black) * inv_range, 0.0, 1.0)
        gain = _get_channel_gain(r, c, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11)
        wb_bayer[r, c] = raw * gain


@ti.kernel
def _ha_grayscale_from_green_kernel(
    green: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
):
    """Output a single-channel luma from the reconstructed green plane."""
    for r, c in ti.ndrange(h, w):
        dst[r, c] = green[r, c]


# -----------------------------------------------------------------------------
# Modular AOT Module Compiler
# -----------------------------------------------------------------------------
def compile_hamilton_tcm(arch=ti.vulkan, save_path=None, target_variant=None):
    print(f"\n>>> Compiling Direct Fast 2-Pass Hamilton Demosaicing AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    register_hamilton_graphs(
        module,
        kernels={
            "green_direct": _ha_green_direct_kernel,
            "red_blue_direct": _ha_red_blue_direct_kernel,
            "srgb_tonemap": _ha_srgb_tonemap_kernel,
            "green_1ch": _ha_green_to_grayscale_1channel_fused_kernel,
            "green_half_res": _ha_green_half_res_fused_kernel,
            "rgb_half_res": _ha_rgb_half_res_fused_kernel,
            "preprocess_wb": _ha_preprocess_wb_kernel,
            "grayscale": _ha_grayscale_from_green_kernel,
            "rgb_to_bgr_i32": rgb_to_bgr_i32,
        },
    )

    # Archive the module using the target selected by the caller.  Never
    # hard-code the OpenGL target here: Vulkan/OpenGL archives have distinct
    # bridge and shader contracts, and CUDA/CPU archives use LLVM payloads.
    if target_variant is None:
        arch_name = "cuda" if arch == ti.cuda else "cpu" if arch == ti.cpu else "opengl" if arch == ti.opengl else "vulkan"
        target_variant = {
            "cpu": "cpu_x86_64_windows",
            "cuda": "cuda_x86_64_windows_nvidia",
            "opengl": "opengl_x86_64_windows",
            "vulkan": "vulkan_x86_64_windows",
        }[arch_name]
    if save_path is None:
        save_path = os.path.abspath(
            os.path.join(file_dir, f"../aot_tcm/{target_variant}/hamilton_{target_variant}.tcm")
        )
    archive_module(module, save_path)
    print(f"Successfully compiled and archived to: {save_path}")

    ti.reset()


if __name__ == "__main__":
    requested = os.environ.get("PIXEL_REFINE_AOT_ARCH", "vulkan").strip().lower()
    arch = {
        "cpu": ti.cpu,
        "cuda": ti.cuda,
        "opengl": ti.opengl,
        "vulkan": ti.vulkan,
    }.get(requested)
    if arch is None:
        raise ValueError("PIXEL_REFINE_AOT_ARCH must be cpu, cuda, opengl, or vulkan")
    compile_hamilton_tcm(arch=arch)
