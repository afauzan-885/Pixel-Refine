"""Clean-room, DCB-style Bayer demosaicing graphs for Taichi AOT.

The implementation follows the public DCB pipeline shape (edge-aware green,
colour-difference reconstruction, iterative chroma correction), but does not
contain or derive from LibRaw source code.
"""

import os
import sys

import taichi as ti

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
except ImportError:
    from aot_artifact import archive_module

try:
    from taichi_vision.taichi_algorithm.demosaicing.demosaic_aot_builder import (
        register_dcb_graphs,
    )
    from taichi_vision.taichi_algorithm.demosaicing.reduced_kernels import (
        rgb_to_luma,
        rgb_to_luma_half_res,
    )
except ImportError:
    from demosaic_aot_builder import register_dcb_graphs
    from reduced_kernels import rgb_to_luma, rgb_to_luma_half_res


@ti.func
def _cfa_color(y, x, c00, c01, c10, c11):
    colour = c00
    if y % 2 == 0:
        colour = c00 if x % 2 == 0 else c01
    else:
        colour = c10 if x % 2 == 0 else c11
    return colour


@ti.func
def _gain(colour, wb_r, wb_g1, wb_b, wb_g2):
    result = wb_g1
    if colour == 0:
        result = wb_r
    elif colour == 2:
        result = wb_b
    elif colour == 3:
        result = wb_g2
    return result


@ti.func
def _sample(bayer: ti.template(), y, x, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11):
    colour = _cfa_color(y, x, c00, c01, c10, c11)
    raw = ti.math.clamp((bayer[y, x] - black) / ti.max(1.0, white - black), 0.0, 1.0)
    return raw * _gain(colour, wb_r, wb_g1, wb_b, wb_g2)


@ti.func
def _sample_headroom(bayer: ti.template(), y, x, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11):
    """Normalize RAW without clipping it before white balance/recovery."""
    colour = _cfa_color(y, x, c00, c01, c10, c11)
    raw = (bayer[y, x] - black) / ti.max(1.0, white - black)
    return ti.max(raw, 0.0) * _gain(colour, wb_r, wb_g1, wb_b, wb_g2)


@ti.kernel
def _dcb_preprocess(
    bayer: ti.types.ndarray(), mosaic: ti.types.ndarray(),
    wb_r: ti.f32, wb_g1: ti.f32, wb_b: ti.f32, wb_g2: ti.f32,
    black: ti.f32, white: ti.f32, h: ti.i32, w: ti.i32,
    c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        mosaic[y, x] = _sample(bayer, y, x, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11)


@ti.kernel
def _dcb_preprocess_headroom(
    bayer: ti.types.ndarray(), mosaic: ti.types.ndarray(),
    wb_r: ti.f32, wb_g1: ti.f32, wb_b: ti.f32, wb_g2: ti.f32,
    black: ti.f32, white: ti.f32, h: ti.i32, w: ti.i32,
    c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        mosaic[y, x] = _sample_headroom(
            bayer, y, x, black, white, wb_r, wb_g1, wb_b, wb_g2,
            c00, c01, c10, c11,
        )


@ti.kernel
def _dcb_green(
    mosaic: ti.types.ndarray(), green: ti.types.ndarray(), h: ti.i32, w: ti.i32,
    c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        colour = _cfa_color(y, x, c00, c01, c10, c11)
        if colour == 1 or colour == 3:
            green[y, x] = mosaic[y, x]
        else:
            yl = ti.max(0, y - 1)
            yr = ti.min(h - 1, y + 1)
            xl = ti.max(0, x - 1)
            xr = ti.min(w - 1, x + 1)
            gh = (mosaic[y, xl] + mosaic[y, xr]) * 0.5
            gv = (mosaic[yl, x] + mosaic[yr, x]) * 0.5
            dh = ti.abs(mosaic[y, xl] - mosaic[y, xr])
            dv = ti.abs(mosaic[yl, x] - mosaic[yr, x])
            weight_h = 1.0 / (1e-4 + dh)
            weight_v = 1.0 / (1e-4 + dv)
            green[y, x] = (gh * weight_h + gv * weight_v) / (weight_h + weight_v)


@ti.kernel
def _dcb_initial_rgb(
    mosaic: ti.types.ndarray(), green: ti.types.ndarray(), rgb: ti.types.ndarray(),
    h: ti.i32, w: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        colour = _cfa_color(y, x, c00, c01, c10, c11)
        yl = ti.max(0, y - 1)
        yr = ti.min(h - 1, y + 1)
        xl = ti.max(0, x - 1)
        xr = ti.min(w - 1, x + 1)
        r = green[y, x]
        g = green[y, x]
        b = green[y, x]
        if colour == 0:
            r = mosaic[y, x]
            b = g + (
                (mosaic[yl, xl] - green[yl, xl]) +
                (mosaic[yl, xr] - green[yl, xr]) +
                (mosaic[yr, xl] - green[yr, xl]) +
                (mosaic[yr, xr] - green[yr, xr])
            ) * 0.25
        elif colour == 2:
            b = mosaic[y, x]
            r = g + (
                (mosaic[yl, xl] - green[yl, xl]) +
                (mosaic[yl, xr] - green[yl, xr]) +
                (mosaic[yr, xl] - green[yr, xl]) +
                (mosaic[yr, xr] - green[yr, xr])
            ) * 0.25
        else:
            left_colour = _cfa_color(y, xl, c00, c01, c10, c11)
            if left_colour == 0:
                r = g + ((mosaic[y, xl] - green[y, xl]) + (mosaic[y, xr] - green[y, xr])) * 0.5
                b = g + ((mosaic[yl, x] - green[yl, x]) + (mosaic[yr, x] - green[yr, x])) * 0.5
            else:
                b = g + ((mosaic[y, xl] - green[y, xl]) + (mosaic[y, xr] - green[y, xr])) * 0.5
                r = g + ((mosaic[yl, x] - green[yl, x]) + (mosaic[yr, x] - green[yr, x])) * 0.5
        rgb[y, x, 0] = r
        rgb[y, x, 1] = g
        rgb[y, x, 2] = b


@ti.kernel
def _dcb_refine_chroma(
    src: ti.types.ndarray(), mosaic: ti.types.ndarray(), dst: ti.types.ndarray(),
    h: ti.i32, w: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        g = src[y, x, 1]
        r_diff = 0.0
        b_diff = 0.0
        count = 0.0
        for dy, dx in ti.static(ti.ndrange(3, 3)):
            ny = ti.math.clamp(y + dy - 1, 0, h - 1)
            nx = ti.math.clamp(x + dx - 1, 0, w - 1)
            r_diff += src[ny, nx, 0] - src[ny, nx, 1]
            b_diff += src[ny, nx, 2] - src[ny, nx, 1]
            count += 1.0
        r = g + r_diff / count
        b = g + b_diff / count
        colour = _cfa_color(y, x, c00, c01, c10, c11)
        if colour == 0:
            r = mosaic[y, x]
        elif colour == 2:
            b = mosaic[y, x]
        dst[y, x, 0] = ti.max(r, 0.0)
        dst[y, x, 1] = ti.max(g, 0.0)
        dst[y, x, 2] = ti.max(b, 0.0)


@ti.kernel
def _dcb_copy_rgb(
    src: ti.types.ndarray(), dst: ti.types.ndarray(),
    wb_r: ti.f32, wb_g1: ti.f32, wb_b: ti.f32, wb_g2: ti.f32,
    h: ti.i32, w: ti.i32,
):
    inv_wb_r = 1.0 / ti.max(0.1, wb_r)
    inv_wb_g = 1.0 / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
    inv_wb_b = 1.0 / ti.max(0.1, wb_b)

    for y, x in ti.ndrange(h, w):
        R = src[y, x, 0]
        G = src[y, x, 1]
        B = src[y, x, 2]

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

        dst[y, x, 0] = R / ti.math.sqrt(1.0 + R * R)
        dst[y, x, 1] = G / ti.math.sqrt(1.0 + G * G)
        dst[y, x, 2] = B / ti.math.sqrt(1.0 + B * B)


@ti.kernel
def _dcb_copy_rgb_headroom(
    src: ti.types.ndarray(), dst: ti.types.ndarray(),
    wb_r: ti.f32, wb_g1: ti.f32, wb_b: ti.f32, wb_g2: ti.f32,
    h: ti.i32, w: ti.i32,
):
    inv_wb_r = 1.0 / ti.max(0.1, wb_r)
    inv_wb_g = 1.0 / ti.max(0.1, (wb_g1 + wb_g2) * 0.5)
    inv_wb_b = 1.0 / ti.max(0.1, wb_b)

    for y, x in ti.ndrange(h, w):
        R = src[y, x, 0]
        G = src[y, x, 1]
        B = src[y, x, 2]

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

        dst[y, x, 0] = R / ti.math.sqrt(1.0 + R * R)
        dst[y, x, 1] = G / ti.math.sqrt(1.0 + G * G)
        dst[y, x, 2] = B / ti.math.sqrt(1.0 + B * B)


@ti.kernel
def _dcb_srgb_tonemap(
    src_linear: ti.types.ndarray(),
    cmatrix: ti.types.ndarray(),
    dst_srgb: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32,
):
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


@ti.kernel
def _dcb_recover_highlights_local(
    src: ti.types.ndarray(), dst: ti.types.ndarray(),
    wb_r: ti.f32, wb_g: ti.f32, wb_b: ti.f32, h: ti.i32, w: ti.i32,
):
    """Recover clipped channels from nearby unclipped camera-space ratios."""
    for y, x in ti.ndrange(h, w):
        r = src[y, x, 0]
        g = src[y, x, 1]
        b = src[y, x, 2]
        raw_r = r / ti.max(wb_r, 1e-4)
        raw_g = g / ti.max(wb_g, 1e-4)
        raw_b = b / ti.max(wb_b, 1e-4)
        raw_peak = ti.max(raw_r, ti.max(raw_g, raw_b))

        rg_sum = 0.0
        bg_sum = 0.0
        weight_sum = 0.0
        for dy, dx in ti.ndrange(11, 11):
            ny = ti.math.clamp(y + dy - 5, 0, h - 1)
            nx = ti.math.clamp(x + dx - 5, 0, w - 1)
            nr = src[ny, nx, 0]
            ng = src[ny, nx, 1]
            nb = src[ny, nx, 2]
            neighbour_peak = ti.max(nr / ti.max(wb_r, 1e-4), ti.max(ng / ti.max(wb_g, 1e-4), nb / ti.max(wb_b, 1e-4)))
            if ng > 1e-5:
                distance = ti.cast(ti.abs(dy - 5) + ti.abs(dx - 5), ti.f32)
                valid = ti.math.clamp((1.0 - neighbour_peak) / 0.12, 0.0, 1.0)
                valid = valid * valid * (3.0 - 2.0 * valid)
                weight = valid / (1.0 + distance)
                rg_sum += ti.math.clamp(nr / ng, 0.05, 8.0) * weight
                bg_sum += ti.math.clamp(nb / ng, 0.05, 8.0) * weight
                weight_sum += weight

        rg = ti.select(weight_sum > 0.0, rg_sum / ti.max(weight_sum, 1e-5), 1.0)
        bg = ti.select(weight_sum > 0.0, bg_sum / ti.max(weight_sum, 1e-5), 1.0)
        # Preprocessing already applied white balance. Neutral highlights are
        # therefore R=G=B in this space; applying WB ratios here a second time
        # produces the familiar magenta clipping artifact.
        neutral = ti.math.clamp((raw_peak - 0.80) / 0.20, 0.0, 1.0)
        neutral = neutral * neutral * (3.0 - 2.0 * neutral)
        # Keep part of the propagated boundary chroma at sensor white. This
        # creates a gradual blue-to-neutral transition instead of a hard cut.
        neutral *= 0.70
        rg = ti.math.clamp(rg, 0.70, 1.30) * (1.0 - neutral) + neutral
        bg = ti.math.clamp(bg, 0.70, 1.30) * (1.0 - neutral) + neutral
        rel_r = ti.math.clamp((1.0 - raw_r) / 0.12, 0.0, 1.0)
        rel_g = ti.math.clamp((1.0 - raw_g) / 0.12, 0.0, 1.0)
        rel_b = ti.math.clamp((1.0 - raw_b) / 0.12, 0.0, 1.0)
        rel_r = rel_r * rel_r * (3.0 - 2.0 * rel_r)
        rel_g = rel_g * rel_g * (3.0 - 2.0 * rel_g)
        rel_b = rel_b * rel_b * (3.0 - 2.0 * rel_b)
        reliable_sum = r * rel_r + g * rel_g + b * rel_b
        reliable_weight = rel_r + rel_g + rel_b
        intensity = ti.select(
            reliable_weight > 1e-4,
            reliable_sum / ti.max(reliable_weight, 1e-4),
            ti.min(r, ti.min(g, b)),
        )
        recovered_r = r * rel_r + intensity * rg * (1.0 - rel_r)
        recovered_g = g * rel_g + intensity * (1.0 - rel_g)
        recovered_b = b * rel_b + intensity * bg * (1.0 - rel_b)

        blend = ti.math.clamp((raw_peak - 0.80) / 0.20, 0.0, 1.0)
        blend = blend * blend * (3.0 - 2.0 * blend)
        dst[y, x, 0] = r * (1.0 - blend) + recovered_r * blend
        dst[y, x, 1] = g * (1.0 - blend) + recovered_g * blend
        dst[y, x, 2] = b * (1.0 - blend) + recovered_b * blend


@ti.kernel
def _dcb_chroma_inpaint_seed(
    src: ti.types.ndarray(), ratios: ti.types.ndarray(),
    wb_r: ti.f32, wb_g: ti.f32, wb_b: ti.f32, h: ti.i32, w: ti.i32,
):
    """Seed chroma ratios and a continuous confidence from unclipped samples."""
    for y, x in ti.ndrange(h, w):
        r = src[y, x, 0]
        g = src[y, x, 1]
        b = src[y, x, 2]
        peak = ti.max(r / ti.max(wb_r, 1e-4), ti.max(g / ti.max(wb_g, 1e-4), b / ti.max(wb_b, 1e-4)))
        confidence = ti.math.clamp((0.98 - peak) / 0.16, 0.0, 1.0)
        confidence = confidence * confidence * (3.0 - 2.0 * confidence)
        ratios[y, x, 0] = ti.math.clamp(r / ti.max(g, 1e-4), 0.65, 1.45)
        ratios[y, x, 1] = ti.math.clamp(b / ti.max(g, 1e-4), 0.65, 1.45)
        ratios[y, x, 2] = confidence


@ti.kernel
def _dcb_chroma_inpaint_diffuse(
    guide: ti.types.ndarray(), src: ti.types.ndarray(), dst: ti.types.ndarray(),
    h: ti.i32, w: ti.i32,
):
    """One Jacobi iteration of edge-aware chroma-ratio inpainting."""
    for y, x in ti.ndrange(h, w):
        own_confidence = src[y, x, 2]
        if own_confidence >= 0.995:
            dst[y, x, 0] = src[y, x, 0]
            dst[y, x, 1] = src[y, x, 1]
            dst[y, x, 2] = own_confidence
        else:
            luma = guide[y, x, 0] * 0.25 + guide[y, x, 1] * 0.5 + guide[y, x, 2] * 0.25
            rg_sum = 0.0
            bg_sum = 0.0
            confidence_sum = 0.0
            weight_sum = 0.0
            for dy, dx in ti.static(ti.ndrange(3, 3)):
                if dy != 1 or dx != 1:
                    ny = ti.math.clamp(y + dy - 1, 0, h - 1)
                    nx = ti.math.clamp(x + dx - 1, 0, w - 1)
                    neighbour_luma = guide[ny, nx, 0] * 0.25 + guide[ny, nx, 1] * 0.5 + guide[ny, nx, 2] * 0.25
                    edge_weight = 1.0 / (1.0 + 24.0 * ti.abs(neighbour_luma - luma))
                    support = 0.08 + src[ny, nx, 2]
                    weight = edge_weight * support
                    rg_sum += src[ny, nx, 0] * weight
                    bg_sum += src[ny, nx, 1] * weight
                    confidence_sum += src[ny, nx, 2] * edge_weight
                    weight_sum += weight
            neighbour_rg = ti.select(weight_sum > 1e-5, rg_sum / weight_sum, 1.0)
            neighbour_bg = ti.select(weight_sum > 1e-5, bg_sum / weight_sum, 1.0)
            mix = ti.math.clamp(0.38 + (1.0 - own_confidence) * 0.44, 0.0, 0.82)
            dst[y, x, 0] = src[y, x, 0] * (1.0 - mix) + neighbour_rg * mix
            dst[y, x, 1] = src[y, x, 1] * (1.0 - mix) + neighbour_bg * mix
            propagated = ti.select(weight_sum > 1e-5, confidence_sum / ti.max(weight_sum, 1e-5), 0.0)
            dst[y, x, 2] = ti.math.clamp(own_confidence * 0.90 + propagated * 0.22, 0.0, 1.0)


@ti.kernel
def _dcb_recover_highlights_inpainted(
    src: ti.types.ndarray(), ratios: ti.types.ndarray(), dst: ti.types.ndarray(),
    wb_r: ti.f32, wb_g: ti.f32, wb_b: ti.f32, h: ti.i32, w: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        r = src[y, x, 0]
        g = src[y, x, 1]
        b = src[y, x, 2]
        raw_r = r / ti.max(wb_r, 1e-4)
        raw_g = g / ti.max(wb_g, 1e-4)
        raw_b = b / ti.max(wb_b, 1e-4)
        peak = ti.max(raw_r, ti.max(raw_g, raw_b))
        rel_r = ti.math.clamp((1.0 - raw_r) / 0.16, 0.0, 1.0)
        rel_g = ti.math.clamp((1.0 - raw_g) / 0.16, 0.0, 1.0)
        rel_b = ti.math.clamp((1.0 - raw_b) / 0.16, 0.0, 1.0)
        rel_r = rel_r * rel_r * (3.0 - 2.0 * rel_r)
        rel_g = rel_g * rel_g * (3.0 - 2.0 * rel_g)
        rel_b = rel_b * rel_b * (3.0 - 2.0 * rel_b)
        reliable_sum = r * rel_r + g * rel_g + b * rel_b
        reliable_weight = rel_r + rel_g + rel_b
        intensity = ti.select(reliable_weight > 1e-4, reliable_sum / reliable_weight, ti.min(r, ti.min(g, b)))
        fade = ti.math.clamp((peak - 0.80) / 0.20, 0.0, 1.0)
        fade = fade * fade * (3.0 - 2.0 * fade) * 0.35
        rg = ti.math.clamp(ratios[y, x, 0], 0.70, 1.30)
        bg = ti.math.clamp(ratios[y, x, 1], 0.70, 1.30)
        rg = rg * (1.0 - fade) + fade
        bg = bg * (1.0 - fade) + fade
        recovered_r = r * rel_r + intensity * rg * (1.0 - rel_r)
        recovered_g = g * rel_g + intensity * (1.0 - rel_g)
        recovered_b = b * rel_b + intensity * bg * (1.0 - rel_b)
        blend = ti.math.clamp((peak - 0.78) / 0.22, 0.0, 1.0)
        blend = blend * blend * (3.0 - 2.0 * blend)
        dst[y, x, 0] = ti.math.clamp(r * (1.0 - blend) + recovered_r * blend, 0.0, 1.0)
        dst[y, x, 1] = ti.math.clamp(g * (1.0 - blend) + recovered_g * blend, 0.0, 1.0)
        dst[y, x, 2] = ti.math.clamp(b * (1.0 - blend) + recovered_b * blend, 0.0, 1.0)


@ti.kernel
def _dcb_highlight_ratio_seed(
    src: ti.types.ndarray(), ratio_map: ti.types.ndarray(),
    wb_r: ti.f32, wb_g: ti.f32, wb_b: ti.f32,
    h: ti.i32, w: ti.i32, map_h: ti.i32, map_w: ti.i32,
):
    """Collect camera-space chroma ratios only from confidently unclipped pixels."""
    for my, mx in ti.ndrange(map_h, map_w):
        rg_sum = 0.0
        bg_sum = 0.0
        count = 0.0
        for dy, dx in ti.static(ti.ndrange(8, 8)):
            y = my * 8 + dy
            x = mx * 8 + dx
            if y < h and x < w:
                r = src[y, x, 0]
                g = src[y, x, 1]
                b = src[y, x, 2]
                raw_peak = ti.max(r / ti.max(wb_r, 1e-4), ti.max(g / ti.max(wb_g, 1e-4), b / ti.max(wb_b, 1e-4)))
                if raw_peak < 0.92 and g > 1e-5:
                    rg_sum += ti.math.clamp(r / g, 0.05, 8.0)
                    bg_sum += ti.math.clamp(b / g, 0.05, 8.0)
                    count += 1.0
        ratio_map[my, mx, 0] = ti.select(count > 0.0, rg_sum / ti.max(count, 1.0), 0.0)
        ratio_map[my, mx, 1] = ti.select(count > 0.0, bg_sum / ti.max(count, 1.0), 0.0)
        ratio_map[my, mx, 2] = ti.select(count > 0.0, 1.0, 0.0)


@ti.kernel
def _dcb_highlight_ratio_propagate(
    src: ti.types.ndarray(), dst: ti.types.ndarray(), map_h: ti.i32, map_w: ti.i32,
):
    for y, x in ti.ndrange(map_h, map_w):
        valid = src[y, x, 2]
        if valid > 0.0:
            for channel in ti.static(range(3)):
                dst[y, x, channel] = src[y, x, channel]
        else:
            rg_sum = 0.0
            bg_sum = 0.0
            weight_sum = 0.0
            for dy, dx in ti.static(ti.ndrange(3, 3)):
                ny = y + dy - 1
                nx = x + dx - 1
                if (dy != 1 or dx != 1) and ny >= 0 and ny < map_h and nx >= 0 and nx < map_w:
                    if src[ny, nx, 2] > 0.0:
                        weight = ti.select(dy == 1 or dx == 1, 1.0, 0.70710678)
                        rg_sum += src[ny, nx, 0] * weight
                        bg_sum += src[ny, nx, 1] * weight
                        weight_sum += weight
            dst[y, x, 0] = ti.select(weight_sum > 0.0, rg_sum / ti.max(weight_sum, 1e-5), 1.0)
            dst[y, x, 1] = ti.select(weight_sum > 0.0, bg_sum / ti.max(weight_sum, 1e-5), 1.0)
            dst[y, x, 2] = ti.select(weight_sum > 0.0, 1.0, 0.0)


@ti.kernel
def _dcb_highlight_apply(
    src: ti.types.ndarray(), ratio_map: ti.types.ndarray(), dst: ti.types.ndarray(),
    wb_r: ti.f32, wb_g: ti.f32, wb_b: ti.f32,
    h: ti.i32, w: ti.i32, map_h: ti.i32, map_w: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        r = src[y, x, 0]
        g = src[y, x, 1]
        b = src[y, x, 2]
        raw_r = r / ti.max(wb_r, 1e-4)
        raw_g = g / ti.max(wb_g, 1e-4)
        raw_b = b / ti.max(wb_b, 1e-4)
        raw_peak = ti.max(raw_r, ti.max(raw_g, raw_b))
        blend = ti.math.clamp((raw_peak - 0.84) / 0.14, 0.0, 1.0)
        my = ti.min(y // 8, map_h - 1)
        mx = ti.min(x // 8, map_w - 1)
        rg = ti.max(ratio_map[my, mx, 0], 0.05)
        bg = ti.max(ratio_map[my, mx, 1], 0.05)

        recovered_r = r
        recovered_g = g
        recovered_b = b
        if raw_g >= 0.96:
            from_r = r / rg
            from_b = b / bg
            recovered_g = ti.min(from_r, from_b)
        if raw_r >= 0.96:
            recovered_r = recovered_g * rg
        if raw_b >= 0.96:
            recovered_b = recovered_g * bg

        dst[y, x, 0] = r * (1.0 - blend) + recovered_r * blend
        dst[y, x, 1] = g * (1.0 - blend) + recovered_g * blend
        dst[y, x, 2] = b * (1.0 - blend) + recovered_b * blend


@ti.kernel
def _dcb_green_1ch(
    bayer: ti.types.ndarray(), dst: ti.types.ndarray(), wb_r: ti.f32, wb_g1: ti.f32, wb_b: ti.f32, wb_g2: ti.f32,
    black: ti.f32, white: ti.f32, h: ti.i32, w: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        colour = _cfa_color(y, x, c00, c01, c10, c11)
        if colour == 1 or colour == 3:
            dst[y, x] = _sample(bayer, y, x, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11)
        else:
            yl = ti.max(0, y - 1)
            yr = ti.min(h - 1, y + 1)
            xl = ti.max(0, x - 1)
            xr = ti.min(w - 1, x + 1)
            dst[y, x] = (_sample(bayer, y, xl, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11) + _sample(bayer, y, xr, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11) + _sample(bayer, yl, x, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11) + _sample(bayer, yr, x, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11)) * 0.25


@ti.kernel
def _dcb_rgb_half(
    bayer: ti.types.ndarray(), dst: ti.types.ndarray(), wb_r: ti.f32, wb_g1: ti.f32, wb_b: ti.f32, wb_g2: ti.f32,
    black: ti.f32, white: ti.f32, h: ti.i32, w: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h // 2, w // 2):
        oy = y * 2
        ox = x * 2
        r = 0.0
        g = 0.0
        b = 0.0
        g_count = 0.0
        for dy, dx in ti.static(ti.ndrange(2, 2)):
            yy = oy + dy
            xx = ox + dx
            value = _sample(bayer, yy, xx, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11)
            colour = _cfa_color(yy, xx, c00, c01, c10, c11)
            if colour == 0:
                r = value
            elif colour == 2:
                b = value
            else:
                g += value
                g_count += 1.0
        dst[y, x, 0] = r
        dst[y, x, 1] = g / ti.max(g_count, 1.0)
        dst[y, x, 2] = b


@ti.kernel
def _rgb_luma(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: ti.i32, w: ti.i32):
    for y, x in ti.ndrange(h, w):
        dst[y, x] = src[y, x, 0] * 0.2126 + src[y, x, 1] * 0.7152 + src[y, x, 2] * 0.0722


@ti.kernel
def _rgb_luma_half(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: ti.i32, w: ti.i32):
    for y, x in ti.ndrange(h // 2, w // 2):
        dst[y, x] = src[y, x, 0] * 0.2126 + src[y, x, 1] * 0.7152 + src[y, x, 2] * 0.0722


def compile_dcb_tcm(arch=ti.vulkan, save_path="dcb_vulkan.tcm"):
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    register_dcb_graphs(
        module,
        kernels={
            "preprocess": _dcb_preprocess,
            "preprocess_headroom": _dcb_preprocess_headroom,
            "green": _dcb_green,
            "initial_rgb": _dcb_initial_rgb,
            "refine_chroma": _dcb_refine_chroma,
            "copy_rgb": _dcb_copy_rgb,
            "copy_rgb_headroom": _dcb_copy_rgb_headroom,
            "srgb_tonemap": _dcb_srgb_tonemap,
            "highlight_ratio_seed": _dcb_highlight_ratio_seed,
            "highlight_ratio_propagate": _dcb_highlight_ratio_propagate,
            "highlight_apply": _dcb_highlight_apply,
            "green_1ch": _dcb_green_1ch,
            "rgb_half": _dcb_rgb_half,
            # These two kernels are ABI- and semantics-identical to the
            # reusable reduced-resolution implementations.  Keep the local
            # names above for compatibility with older direct imports, but
            # register the shared implementation as the single graph source.
            "rgb_luma": rgb_to_luma,
            "rgb_luma_half": rgb_to_luma_half_res,
        },
    )

    archive_module(module, save_path)
    ti.reset()


if __name__ == "__main__":
    target_id = os.environ.get("PIXEL_REFINE_TARGET_VARIANT", "").strip() or "vulkan_x86_64_windows"
    output = os.path.abspath(
        os.path.join(file_dir, f"../aot_tcm/{target_id}/dcb_{target_id}.tcm")
    )
    os.makedirs(os.path.dirname(output), exist_ok=True)
    compile_dcb_tcm(ti.vulkan, output)
