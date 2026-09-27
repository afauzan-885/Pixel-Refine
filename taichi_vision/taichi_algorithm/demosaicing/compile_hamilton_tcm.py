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
    from taichi_vision.taichi_algorithm.demosaicing.demosaic_common import (
        cfa_color,
        channel_gain,
        green_gain,
    )
    from taichi_vision.taichi_algorithm.demosaicing.demosaic_postprocess import (
        rgb_to_bgr_i32,
        rgb_to_bgr_u16,
    )
except ImportError:
    from demosaic_aot_builder import register_hamilton_graphs
    from demosaic_common import cfa_color, channel_gain, green_gain
    from demosaic_postprocess import rgb_to_bgr_i32, rgb_to_bgr_u16


# -----------------------------------------------------------------------------
# Tuning constants
# -----------------------------------------------------------------------------
# These mirror ``HamiltonParams`` in ``tests/hamilton_reference.py``, the float64
# model that is used to search them (``tests/search_hamilton_params.py``), and
# the identical names are what let a searched value be applied in one obvious
# place.  Taichi captures module-level Python values at compile time, so these
# are true compile-time constants inside the kernels.
#
# Structural coefficients (the 0.5/0.25 interpolation weights, the 5.0 edge
# ramp, the algebraic sigmoid) are deliberately *not* parameterised: they define
# the algorithm rather than a tuning choice.
# Values marked "searched" come from ``tests/search_hamilton_params.py``, which
# was run against the float64 model.  Only changes with a measured effect above
# the search's own noise floor were adopted: the search also proposed
# ``green_weight_floor=0.1`` (zero measured effect) and a ``neutrality_*`` pair
# (effect ~2e-5, and it would alter highlight recovery on synthetic evidence
# only), and those were rejected deliberately.
HA_DIRECTION_PRIMARY = 4.5  # searched (was 3.0)
HA_DIRECTION_SECONDARY = 3.0  # searched (was 2.0)
HA_GREEN_WEIGHT_FLOOR = 0.01
HA_TEXTURE_OFFSET = 2.0  # searched (was 4.0)
HA_TEXTURE_SCALE = 0.25
HA_CHROMA_WEIGHT_FLOOR = 0.015  # searched (was 0.005)
HA_OPPONENT_TEXTURE_OFFSET = 0.24  # searched (was 0.16)
HA_OPPONENT_TEXTURE_SCALE = 0.6  # searched (was 0.39)
HA_OPPONENT_OFFSET = 0.005  # searched (was 0.015)
HA_OPPONENT_SCALE = 0.08  # searched (was 0.155)
HA_HIGHLIGHT_KNEE = 0.55
HA_HIGHLIGHT_SCALE = 0.43
HA_NEUTRALITY_OFFSET = 0.40
HA_NEUTRALITY_SCALE = 0.45


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
    """The gain of the CFA colour at a coordinate.

    Delegates to the shared ``demosaic_common`` helpers so the CFA phase and
    gain semantics have exactly one definition across the demosaic families.
    """
    return channel_gain(cfa_color(r, c, c00, c01, c10, c11), wb_r, wb_g1, wb_b, wb_g2)


@ti.func
def _sample_raw_wb(
    bayer: ti.template(),
    r: ti.i32,
    c: ti.i32,
    black: ti.f32,
    inv_range: ti.f32,
    h: ti.i32,
    w: ti.i32,
    wb_r: ti.f32,
    wb_g1: ti.f32,
    wb_b: ti.f32,
    wb_g2: ti.f32,
    c00: ti.i32,
    c01: ti.i32,
    c10: ti.i32,
    c11: ti.i32,
) -> ti.f32:
    """Sample with the gain of the clamped CFA position.

    G1/G2 orientation swaps between red and blue sites.  Looking the gain up
    from the actual coordinate avoids a subtle tint discontinuity when the two
    sensor green gains differ.
    """
    nr = ti.math.clamp(r, 0, h - 1)
    nc = ti.math.clamp(c, 0, w - 1)
    gain = _get_channel_gain(
        nr, nc, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11
    )
    return _sample_raw(bayer, nr, nc, black, inv_range, h, w) * gain


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

    # CFA-phase specialisation.  The 2x2 block is unrolled at compile time, so
    # every pixel parity is a constant: the row/column modulo, the parity selects
    # that derived the CFA colour, and the per-sample gain lookups all disappear.
    # Only the 4x4-block borders keep the clamped sampler, so for the interior
    # (>99% of a real frame) this is bit-identical to the clamped formulation.
    for r2, c2 in ti.ndrange((h + 1) // 2, (w + 1) // 2):
        for i in ti.static(range(2)):
            for j in ti.static(range(2)):
                r = r2 * 2 + i
                c = c2 * 2 + j
                if r < h and c < w:
                    # Colours of this phase, its horizontal neighbour, and its
                    # vertical neighbour, chosen at compile time.  All three are
                    # green for a green centre, which is harmless: those values are
                    # unused on that path.
                    colour_self = c00
                    colour_h = c01
                    colour_v = c10
                    if ti.static(i == 0 and j == 1):
                        colour_self = c01
                        colour_h = c00
                        colour_v = c11
                    if ti.static(i == 1 and j == 0):
                        colour_self = c10
                        colour_h = c11
                        colour_v = c00
                    if ti.static(i == 1 and j == 1):
                        colour_self = c11
                        colour_h = c10
                        colour_v = c01

                    c_center = _sample_raw(bayer, r, c, black, inv_range, h, w)

                    if (colour_self == 1) or (colour_self == 3):
                        green[r, c] = c_center * ti.select(colour_self == 1, wb_g1, wb_g2)
                    else:
                        center_gain = ti.select(colour_self == 0, wb_r, wb_b)
                        # Declared before the branch: Taichi scopes a variable to
                        # the block that first assigns it, so the shared tail below
                        # needs these to exist outside the interior/border split.
                        g_left = 0.0
                        g_right = 0.0
                        g_up = 0.0
                        g_down = 0.0
                        g_left3 = 0.0
                        g_right3 = 0.0
                        g_up3 = 0.0
                        g_down3 = 0.0
                        c_center_wb = 0.0
                        c_left2 = 0.0
                        c_right2 = 0.0
                        c_up2 = 0.0
                        c_down2 = 0.0
                        if r >= 3 and r < h - 3 and c >= 3 and c < w - 3:
                            # Interior: neither the indices nor the gains need
                            # clamping, and the two neighbour gains are hoisted out
                            # of what used to be eight separate lookups.
                            gain_h = ti.select(colour_h == 1, wb_g1, wb_g2)
                            gain_v = ti.select(colour_v == 1, wb_g1, wb_g2)

                            g_left = ti.math.clamp(
                                (bayer[r, c - 1] - black) * inv_range, 0.0, 1.0
                            ) * gain_h
                            g_right = ti.math.clamp(
                                (bayer[r, c + 1] - black) * inv_range, 0.0, 1.0
                            ) * gain_h
                            g_up = ti.math.clamp(
                                (bayer[r - 1, c] - black) * inv_range, 0.0, 1.0
                            ) * gain_v
                            g_down = ti.math.clamp(
                                (bayer[r + 1, c] - black) * inv_range, 0.0, 1.0
                            ) * gain_v
                            g_left3 = ti.math.clamp(
                                (bayer[r, c - 3] - black) * inv_range, 0.0, 1.0
                            ) * gain_h
                            g_right3 = ti.math.clamp(
                                (bayer[r, c + 3] - black) * inv_range, 0.0, 1.0
                            ) * gain_h
                            g_up3 = ti.math.clamp(
                                (bayer[r - 3, c] - black) * inv_range, 0.0, 1.0
                            ) * gain_v
                            g_down3 = ti.math.clamp(
                                (bayer[r + 3, c] - black) * inv_range, 0.0, 1.0
                            ) * gain_v

                            c_center_wb = c_center * center_gain
                            c_left2 = ti.math.clamp(
                                (bayer[r, c - 2] - black) * inv_range, 0.0, 1.0
                            ) * center_gain
                            c_right2 = ti.math.clamp(
                                (bayer[r, c + 2] - black) * inv_range, 0.0, 1.0
                            ) * center_gain
                            c_up2 = ti.math.clamp(
                                (bayer[r - 2, c] - black) * inv_range, 0.0, 1.0
                            ) * center_gain
                            c_down2 = ti.math.clamp(
                                (bayer[r + 2, c] - black) * inv_range, 0.0, 1.0
                            ) * center_gain
                        else:
                            # Border ring: keep the clamped sampler so the result is
                            # unchanged where the stencil would run off the frame.
                            g_left = _sample_raw_wb(
                                bayer, r, c - 1, black, inv_range, h, w,
                                wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11,
                            )
                            g_right = _sample_raw_wb(
                                bayer, r, c + 1, black, inv_range, h, w,
                                wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11,
                            )
                            g_up = _sample_raw_wb(
                                bayer, r - 1, c, black, inv_range, h, w,
                                wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11,
                            )
                            g_down = _sample_raw_wb(
                                bayer, r + 1, c, black, inv_range, h, w,
                                wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11,
                            )
                            g_left3 = _sample_raw_wb(
                                bayer, r, c - 3, black, inv_range, h, w,
                                wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11,
                            )
                            g_right3 = _sample_raw_wb(
                                bayer, r, c + 3, black, inv_range, h, w,
                                wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11,
                            )
                            g_up3 = _sample_raw_wb(
                                bayer, r - 3, c, black, inv_range, h, w,
                                wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11,
                            )
                            g_down3 = _sample_raw_wb(
                                bayer, r + 3, c, black, inv_range, h, w,
                                wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11,
                            )

                            c_center_wb = c_center * center_gain
                            c_left2 = _sample_raw(bayer, r, c - 2, black, inv_range, h, w) * center_gain
                            c_right2 = _sample_raw(bayer, r, c + 2, black, inv_range, h, w) * center_gain
                            c_up2 = _sample_raw(bayer, r - 2, c, black, inv_range, h, w) * center_gain
                            c_down2 = _sample_raw(bayer, r + 2, c, black, inv_range, h, w) * center_gain

                        # Hamilton/PPG directional evidence.  The +/-3 green terms
                        # reject a one-pixel false edge, while the two
                        # center-to-same-colour terms retain the original
                        # second-order Hamilton correction.
                        dh = HA_DIRECTION_PRIMARY * (
                            ti.abs(c_left2 - c_center_wb)
                            + ti.abs(c_right2 - c_center_wb)
                            + ti.abs(g_left - g_right)
                        ) + HA_DIRECTION_SECONDARY * (
                            ti.abs(g_right3 - g_right) + ti.abs(g_left3 - g_left)
                        )
                        dv = HA_DIRECTION_PRIMARY * (
                            ti.abs(c_up2 - c_center_wb)
                            + ti.abs(c_down2 - c_center_wb)
                            + ti.abs(g_up - g_down)
                        ) + HA_DIRECTION_SECONDARY * (
                            ti.abs(g_down3 - g_down) + ti.abs(g_up3 - g_up)
                        )

                        g_h = (g_left + g_right) * 0.5 + (2.0 * c_center_wb - c_left2 - c_right2) * 0.25
                        g_v = (g_up + g_down) * 0.5 + (2.0 * c_center_wb - c_up2 - c_down2) * 0.25
                        g_h_bounded = ti.math.clamp(
                            g_h, ti.min(g_left, g_right), ti.max(g_left, g_right)
                        )
                        g_v_bounded = ti.math.clamp(
                            g_v, ti.min(g_up, g_down), ti.max(g_up, g_down)
                        )
                        g_hard = ti.select(
                            dh < dv,
                            g_h_bounded,
                            ti.select(dv < dh, g_v_bounded, (g_h_bounded + g_v_bounded) * 0.5),
                        )
                        # (weight_h*g_h + weight_v*g_v)/(weight_h + weight_v) with
                        # weight = 1/(floor + d) collapses to one division, removing
                        # the two reciprocal weights.  Algebraically identical.
                        g_soft = (g_h * (HA_GREEN_WEIGHT_FLOOR + dv) + g_v * (HA_GREEN_WEIGHT_FLOOR + dh)) / (
                            2.0 * HA_GREEN_WEIGHT_FLOOR + dh + dv
                        )

                        # Sparse/ordinary edges benefit from the bounded hard
                        # decision.  At dense near-Nyquist texture both directional
                        # gradients become large, so blend toward a soft decision to
                        # avoid zipper/moire.
                        texture = ti.math.clamp(
                            (ti.min(dh, dv) - HA_TEXTURE_OFFSET) * HA_TEXTURE_SCALE, 0.0, 1.0
                        )
                        texture = texture * texture * (3.0 - 2.0 * texture)
                        green[r, c] = g_hard * (1.0 - texture) + g_soft * texture


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

    for r2, c2 in ti.ndrange((h + 1) // 2, (w + 1) // 2):
        for i in ti.static(range(2)):
            for j in ti.static(range(2)):
                r = r2 * 2 + i
                c = c2 * 2 + j
                if r < h and c < w:
                    # Compile-time CFA phase, as in pass 1: the parity modulo and
                    # the nested selects that derived the colour are gone, and the
                    # neighbour colours needed below are resolved statically.
                    colour_self = c00
                    colour_h = c01
                    colour_v = c10
                    if ti.static(i == 0 and j == 1):
                        colour_self = c01
                        colour_h = c00
                        colour_v = c11
                    if ti.static(i == 1 and j == 0):
                        colour_self = c10
                        colour_h = c11
                        colour_v = c00
                    if ti.static(i == 1 and j == 1):
                        colour_self = c11
                        colour_h = c10
                        colour_v = c01

                    G = green[r, c]
                    R, B = 0.0, 0.0

                    if colour_self == 0:  # Red pixel
                        R = _sample_raw(bayer, r, c, black, inv_range, h, w) * wb_r
                        if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                            g11, g22 = green[r - 1, c - 1], green[r + 1, c + 1]
                            g12, g21 = green[r - 1, c + 1], green[r + 1, c - 1]
                            b11 = _sample_raw(bayer, r - 1, c - 1, black, inv_range, h, w) * wb_b
                            b22 = _sample_raw(bayer, r + 1, c + 1, black, inv_range, h, w) * wb_b
                            b12 = _sample_raw(bayer, r - 1, c + 1, black, inv_range, h, w) * wb_b
                            b21 = _sample_raw(bayer, r + 1, c - 1, black, inv_range, h, w) * wb_b

                            d1 = ((b11 - g11) + (b22 - g22)) * 0.5
                            d2 = ((b12 - g12) + (b21 - g21)) * 0.5
                            e1 = ti.abs(b11 - b22) + ti.abs(g11 - G) + ti.abs(g22 - G)
                            e2 = ti.abs(b12 - b21) + ti.abs(g12 - G) + ti.abs(g21 - G)
                            a1 = ti.abs(g11 - g22)
                            a2 = ti.abs(g12 - g21)
                            # (w1*d1 + w2*d2)/(w1 + w2) with w = 1/(1+a) collapses to one
                            # division: (d1*(1+a2) + d2*(1+a1))/((1+a1) + (1+a2)).  The two
                            # reciprocal weights then never need materialising, and division
                            # is the most expensive operation in this kernel.
                            d_soft = (d1 * (1.0 + a2) + d2 * (1.0 + a1)) / (2.0 + a1 + a2)
                            d_hard = ti.select(e1 < e2, d1, ti.select(e2 < e1, d2, (d1 + d2) * 0.5))
                            simple_edge = ti.math.clamp((0.25 - ti.min(e1, e2)) * 5.0, 0.0, 1.0)
                            simple_edge = simple_edge * simple_edge * (3.0 - 2.0 * simple_edge)
                            b_diff = d_soft * (1.0 - simple_edge) + d_hard * simple_edge
                            B = G + b_diff
                        else:
                            B = G

                    elif colour_self == 2:  # Blue pixel
                        B = _sample_raw(bayer, r, c, black, inv_range, h, w) * wb_b
                        if r > 0 and r < h - 1 and c > 0 and c < w - 1:
                            g11, g22 = green[r - 1, c - 1], green[r + 1, c + 1]
                            g12, g21 = green[r - 1, c + 1], green[r + 1, c - 1]
                            r11 = _sample_raw(bayer, r - 1, c - 1, black, inv_range, h, w) * wb_r
                            r22 = _sample_raw(bayer, r + 1, c + 1, black, inv_range, h, w) * wb_r
                            r12 = _sample_raw(bayer, r - 1, c + 1, black, inv_range, h, w) * wb_r
                            r21 = _sample_raw(bayer, r + 1, c - 1, black, inv_range, h, w) * wb_r

                            d1 = ((r11 - g11) + (r22 - g22)) * 0.5
                            d2 = ((r12 - g12) + (r21 - g21)) * 0.5
                            e1 = ti.abs(r11 - r22) + ti.abs(g11 - G) + ti.abs(g22 - G)
                            e2 = ti.abs(r12 - r21) + ti.abs(g12 - G) + ti.abs(g21 - G)
                            a1 = ti.abs(g11 - g22)
                            a2 = ti.abs(g12 - g21)
                            # (w1*d1 + w2*d2)/(w1 + w2) with w = 1/(1+a) collapses to one
                            # division: (d1*(1+a2) + d2*(1+a1))/((1+a1) + (1+a2)).  The two
                            # reciprocal weights then never need materialising, and division
                            # is the most expensive operation in this kernel.
                            d_soft = (d1 * (1.0 + a2) + d2 * (1.0 + a1)) / (2.0 + a1 + a2)
                            d_hard = ti.select(e1 < e2, d1, ti.select(e2 < e1, d2, (d1 + d2) * 0.5))
                            simple_edge = ti.math.clamp((0.25 - ti.min(e1, e2)) * 5.0, 0.0, 1.0)
                            simple_edge = simple_edge * simple_edge * (3.0 - 2.0 * simple_edge)
                            r_diff = d_soft * (1.0 - simple_edge) + d_hard * simple_edge
                            R = G + r_diff
                        else:
                            R = G

                    else:  # Green pixel
                        # Whether red is the horizontal neighbour was previously
                        # derived from the parity; the compile-time phase already
                        # resolved that neighbour's colour above.
                        is_red_horizontal = colour_h == 0

                        if is_red_horizontal:  # Red is Horizontal, Blue is Vertical
                            if c > 0 and c < w - 1:
                                r_l = _sample_raw(bayer, r, c - 1, black, inv_range, h, w) * wb_r
                                r_r = _sample_raw(bayer, r, c + 1, black, inv_range, h, w) * wb_r
                                g_l, g_r = green[r, c - 1], green[r, c + 1]
                                a_l = ti.abs(g_l - G)
                                a_r = ti.abs(g_r - G)
                                R = G + (
                                    (r_l - g_l) * (HA_CHROMA_WEIGHT_FLOOR + a_r)
                                    + (r_r - g_r) * (HA_CHROMA_WEIGHT_FLOOR + a_l)
                                ) / (2.0 * HA_CHROMA_WEIGHT_FLOOR + a_l + a_r)
                            else:
                                R = G

                            if r > 0 and r < h - 1:
                                b_u = _sample_raw(bayer, r - 1, c, black, inv_range, h, w) * wb_b
                                b_d = _sample_raw(bayer, r + 1, c, black, inv_range, h, w) * wb_b
                                g_u, g_d = green[r - 1, c], green[r + 1, c]
                                a_u = ti.abs(g_u - G)
                                a_d = ti.abs(g_d - G)
                                B = G + (
                                    (b_u - g_u) * (HA_CHROMA_WEIGHT_FLOOR + a_d)
                                    + (b_d - g_d) * (HA_CHROMA_WEIGHT_FLOOR + a_u)
                                ) / (2.0 * HA_CHROMA_WEIGHT_FLOOR + a_u + a_d)
                            else:
                                B = G

                        else:  # Blue is Horizontal, Red is Vertical
                            if r > 0 and r < h - 1:
                                r_u = _sample_raw(bayer, r - 1, c, black, inv_range, h, w) * wb_r
                                r_d = _sample_raw(bayer, r + 1, c, black, inv_range, h, w) * wb_r
                                g_u, g_d = green[r - 1, c], green[r + 1, c]
                                a_u = ti.abs(g_u - G)
                                a_d = ti.abs(g_d - G)
                                R = G + (
                                    (r_u - g_u) * (HA_CHROMA_WEIGHT_FLOOR + a_d)
                                    + (r_d - g_d) * (HA_CHROMA_WEIGHT_FLOOR + a_u)
                                ) / (2.0 * HA_CHROMA_WEIGHT_FLOOR + a_u + a_d)
                            else:
                                R = G

                            if c > 0 and c < w - 1:
                                b_l = _sample_raw(bayer, r, c - 1, black, inv_range, h, w) * wb_b
                                b_r = _sample_raw(bayer, r, c + 1, black, inv_range, h, w) * wb_b
                                g_l, g_r = green[r, c - 1], green[r, c + 1]
                                a_l = ti.abs(g_l - G)
                                a_r = ti.abs(g_r - G)
                                B = G + (
                                    (b_l - g_l) * (HA_CHROMA_WEIGHT_FLOOR + a_r)
                                    + (b_r - g_r) * (HA_CHROMA_WEIGHT_FLOOR + a_l)
                                ) / (2.0 * HA_CHROMA_WEIGHT_FLOOR + a_l + a_r)
                            else:
                                B = G

                    # Suppress Bayer opponent-colour outliers without blurring luminance.
                    # On dense detail an alias commonly appears as large R-G and B-G
                    # differences with opposite signs.  Preserve the measured channel at
                    # R/B sites and only correct channels reconstructed by interpolation.
                    r_up = ti.max(0, r - 1)
                    r_down = ti.min(h - 1, r + 1)
                    c_left = ti.max(0, c - 1)
                    c_right = ti.min(w - 1, c + 1)
                    g_min = ti.min(
                        G,
                        ti.min(
                            green[r_up, c],
                            ti.min(
                                green[r_down, c],
                                ti.min(green[r, c_left], green[r, c_right]),
                            ),
                        ),
                    )
                    g_max = ti.max(
                        G,
                        ti.max(
                            green[r_up, c],
                            ti.max(
                                green[r_down, c],
                                ti.max(green[r, c_left], green[r, c_right]),
                            ),
                        ),
                    )
                    texture_strength = ti.math.clamp(
                        (g_max - g_min - HA_OPPONENT_TEXTURE_OFFSET) / HA_OPPONENT_TEXTURE_SCALE,
                        0.0,
                        1.0,
                    )
                    texture_strength = texture_strength * texture_strength * (
                        3.0 - 2.0 * texture_strength
                    )
                    rg = R - G
                    bg = B - G
                    opponent_magnitude = ti.min(ti.abs(rg), ti.abs(bg))
                    opponent_strength = ti.math.clamp(
                        (opponent_magnitude - HA_OPPONENT_OFFSET) / HA_OPPONENT_SCALE, 0.0, 1.0
                    )
                    opponent_strength = opponent_strength * opponent_strength * (
                        3.0 - 2.0 * opponent_strength
                    )
                    artifact_blend = texture_strength * opponent_strength
                    if rg * bg < 0.0:
                        if colour_self == 0:
                            B = G + bg * (1.0 - artifact_blend) + rg * artifact_blend
                        elif colour_self == 2:
                            R = G + rg * (1.0 - artifact_blend) + bg * artifact_blend
                        else:
                            R = G + rg * (1.0 - artifact_blend)
                            B = G + bg * (1.0 - artifact_blend)

                    # 1. Highlight Recovery & Desaturation (Commit 1106566 Math)
                    R_raw = R * inv_wb_r
                    G_raw = G * inv_wb_g
                    B_raw = B * inv_wb_b

                    max_raw = ti.max(R_raw, ti.max(G_raw, B_raw))
                    min_raw = ti.min(R_raw, ti.min(G_raw, B_raw))

                    factor = ti.math.clamp((max_raw - HA_HIGHLIGHT_KNEE) / HA_HIGHLIGHT_SCALE, 0.0, 1.0)
                    factor = factor * factor * (3.0 - 2.0 * factor)

                    ratio = min_raw / ti.max(1e-5, max_raw)
                    neutrality = ti.math.clamp((ratio - HA_NEUTRALITY_OFFSET) / HA_NEUTRALITY_SCALE, 0.0, 1.0)
                    neutrality = neutrality * neutrality * (3.0 - 2.0 * neutrality)

                    final_factor = factor * neutrality

                    L = ti.max(R, ti.max(G, B))
                    R = R * (1.0 - final_factor) + L * final_factor
                    G = G * (1.0 - final_factor) + L * final_factor
                    B = B * (1.0 - final_factor) + L * final_factor

                    # 2. Algebraic Sigmoid Dynamic Range Compression
                    # Reconstruction near a black/high-contrast boundary can undershoot
                    # zero by a few code values.  The graph's public output is display
                    # compressed RGB, so reject that non-physical tail before compression.
                    R = ti.max(0.0, R)
                    G = ti.max(0.0, G)
                    B = ti.max(0.0, B)
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
    """The green gain at a coordinate, from the shared CFA definition."""
    return green_gain(nr, nc, c00, c01, c10, c11, wb_g1, wb_g2)


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
        factor = ti.math.clamp((max_raw - HA_HIGHLIGHT_KNEE) / HA_HIGHLIGHT_SCALE, 0.0, 1.0)
        factor = factor * factor * (3.0 - 2.0 * factor)
        ratio = min_raw / ti.max(1e-5, max_raw)
        neutrality = ti.math.clamp((ratio - HA_NEUTRALITY_OFFSET) / HA_NEUTRALITY_SCALE, 0.0, 1.0)
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
            "grayscale": _ha_grayscale_from_green_kernel,
            "rgb_to_bgr_i32": rgb_to_bgr_i32,
            "rgb_to_bgr_u16": rgb_to_bgr_u16,
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
