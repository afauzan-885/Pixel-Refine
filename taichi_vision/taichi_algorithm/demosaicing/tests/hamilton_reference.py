"""Float64 NumPy model of the Hamilton demosaic graph.

The AOT graph is the source of truth for *runtime behaviour*, but scoring a
candidate parameter set through it costs a TCM compile plus a device round trip.
This module re-implements the same arithmetic in NumPy float64 with the tuning
constants lifted into :class:`HamiltonParams`, so a search can evaluate hundreds
of candidates per second and only the winner is compiled.

It is a *model*, not a second implementation of the product path: the graph
keeps its own kernels, and any parameter that wins here must still be verified
against the graph through ``run_demosaic_quality.py``.

Every formula below mirrors ``compile_hamilton_tcm.py``; keeping the two in step
is the whole point, so the structure and the constant names are deliberately
identical.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

_COLOUR_TO_CHANNEL = {0: 0, 1: 1, 2: 2, 3: 1}


@dataclass(frozen=True)
class HamiltonParams:
    """The tunable constants of the Hamilton graph.

    Defaults mirror the constants compiled into ``compile_hamilton_tcm.py``.
    When a searched value is adopted there, the matching default must change
    here in the same commit, or the model stops predicting the graph.
    """

    # Directional evidence weights in the green pass.
    direction_primary: float = 4.5
    direction_secondary: float = 3.0
    # Soft/hard blend floor for the green decision.
    green_weight_floor: float = 0.01
    # Texture detector that blends the hard decision toward the soft one.
    texture_offset: float = 2.0
    texture_scale: float = 0.25
    # Colour-difference weight floor in the red/blue pass.
    chroma_weight_floor: float = 0.015
    # Opponent-outlier suppression knee and range, plus its texture gate.
    opponent_offset: float = 0.005
    opponent_scale: float = 0.08
    opponent_texture_offset: float = 0.24
    opponent_texture_scale: float = 0.6
    # Highlight recovery knee and neutrality window.
    highlight_knee: float = 0.55
    highlight_scale: float = 0.43
    neutrality_offset: float = 0.40
    neutrality_scale: float = 0.45


def smoothstep(value):
    return value * value * (3.0 - 2.0 * value)


def _t(v):
    """Return a float32 scalar suitable for arithmetic with a NumPy array."""

    return np.float32(v)


def _clamp01(value):
    return np.clip(value, 0.0, 1.0)


def _colour_map(cfa: Sequence[int], shape) -> np.ndarray:
    height, width = shape
    block = ((int(cfa[0]), int(cfa[1])), (int(cfa[2]), int(cfa[3])))
    colours = np.empty((height, width), dtype=np.int32)
    for row in range(2):
        for col in range(2):
            colours[row::2, col::2] = block[row][col]
    return colours


def _sample(field: np.ndarray, ys: np.ndarray, xs: np.ndarray) -> np.ndarray:
    """Clamped nearest-neighbour sampling, matching ``ti.math.clamp`` taps."""

    return field[np.clip(ys, 0, field.shape[0] - 1), np.clip(xs, 0, field.shape[1] - 1)]


def hamilton_model(
    bayer: np.ndarray,
    wb: Sequence[float],
    black_level: float,
    white_level: float,
    cfa: Sequence[int],
    params: HamiltonParams | None = None,
) -> np.ndarray:
    """Demosaic a Bayer frame exactly as the Hamilton graph does.

    Returns the display-compressed RGB output (highlight recovery plus the
    algebraic sigmoid) that the graph's public ``hamilton_demosaic`` graph
    produces.
    """

    params = params or HamiltonParams()
    bayer = np.asarray(bayer, dtype=np.float64)
    height, width = bayer.shape
    rows, cols = np.indices((height, width))
    rows32 = rows.astype(np.float32)
    cols32 = cols.astype(np.float32)

    inv_range = 1.0 / max(1.0, float(white_level) - float(black_level))
    raw = np.clip((bayer - float(black_level)) * inv_range, 0.0, 1.0)

    wb_r, wb_g1, wb_b, wb_g2 = (float(value) for value in wb)
    colours = _colour_map(cfa, bayer.shape)
    gain_table = np.array([wb_r, wb_g1, wb_b, wb_g2], dtype=np.float64)
    gain_map = gain_table[colours]

    # ------------------------------------------------------------------
    # Pass 1: edge-directed green reconstruction
    # ------------------------------------------------------------------
    def raw_wb(dy: int, dx: int) -> np.ndarray:
        ys, xs = rows + dy, cols + dx
        return _sample(raw, ys, xs) * _sample(gain_map, ys, xs)

    g_left = raw_wb(0, -1)
    g_right = raw_wb(0, 1)
    g_up = raw_wb(-1, 0)
    g_down = raw_wb(1, 0)
    g_left3 = raw_wb(0, -3)
    g_right3 = raw_wb(0, 3)
    g_up3 = raw_wb(-3, 0)
    g_down3 = raw_wb(3, 0)

    center_gain = np.where(colours == 0, wb_r, wb_b)
    c_center = _sample(raw, rows, cols)
    c_center_wb = c_center * center_gain
    c_left2 = _sample(raw, rows, cols - 2) * center_gain
    c_right2 = _sample(raw, rows, cols + 2) * center_gain
    c_up2 = _sample(raw, rows - 2, cols) * center_gain
    c_down2 = _sample(raw, rows + 2, cols) * center_gain

    primary = _t(params.direction_primary)
    secondary = _t(params.direction_secondary)

    dh = primary * (
        np.abs(c_left2 - c_center_wb)
        + np.abs(c_right2 - c_center_wb)
        + np.abs(g_left - g_right)
    ) + secondary * (np.abs(g_right3 - g_right) + np.abs(g_left3 - g_left))
    dv = primary * (
        np.abs(c_up2 - c_center_wb)
        + np.abs(c_down2 - c_center_wb)
        + np.abs(g_up - g_down)
    ) + secondary * (np.abs(g_down3 - g_down) + np.abs(g_up3 - g_up))

    g_h = 0.5 * (g_left + g_right) + 0.25 * (2.0 * c_center_wb - c_left2 - c_right2)
    g_v = 0.5 * (g_up + g_down) + 0.25 * (2.0 * c_center_wb - c_up2 - c_down2)
    g_h_bounded = np.clip(g_h, np.minimum(g_left, g_right), np.maximum(g_left, g_right))
    g_v_bounded = np.clip(g_v, np.minimum(g_up, g_down), np.maximum(g_up, g_down))

    g_hard = np.where(
        dh < dv,
        g_h_bounded,
        np.where(dv < dh, g_v_bounded, 0.5 * (g_h_bounded + g_v_bounded)),
    )
    floor = _t(params.green_weight_floor)
    weight_h = 1.0 / (floor + dh)
    weight_v = 1.0 / (floor + dv)
    g_soft = (weight_h * g_h + weight_v * g_v) / (weight_h + weight_v)

    texture = _clamp01(
        (np.minimum(dh, dv) - _t(params.texture_offset)) * _t(params.texture_scale)
    )
    texture = smoothstep(texture)

    is_green = (colours == 1) | (colours == 3)
    green_from_green_site = c_center * np.where(colours == 1, wb_g1, wb_g2)
    green = np.where(
        is_green,
        green_from_green_site,
        g_hard * (1.0 - texture) + g_soft * texture,
    )

    # ------------------------------------------------------------------
    # Pass 2: colour-difference red/blue reconstruction
    # ------------------------------------------------------------------
    def green_at(dy: int, dx: int) -> np.ndarray:
        return _sample(green, rows + dy, cols + dx)

    G = green
    R = np.zeros_like(green)
    B = np.zeros_like(green)

    # Red sites: reconstruct blue from the diagonal colour differences.
    is_red = colours == 0
    is_blue = colours == 2

    r_interior = (rows > 0) & (rows < height - 1) & (cols > 0) & (cols < width - 1)

    b11 = _sample(raw, rows - 1, cols - 1) * wb_b
    b22 = _sample(raw, rows + 1, cols + 1) * wb_b
    b12 = _sample(raw, rows - 1, cols + 1) * wb_b
    b21 = _sample(raw, rows + 1, cols - 1) * wb_b
    g11 = green_at(-1, -1)
    g22 = green_at(1, 1)
    g12 = green_at(-1, 1)
    g21 = green_at(1, -1)

    d1 = 0.5 * ((b11 - g11) + (b22 - g22))
    d2 = 0.5 * ((b12 - g12) + (b21 - g21))
    e1 = np.abs(b11 - b22) + np.abs(g11 - G) + np.abs(g22 - G)
    e2 = np.abs(b12 - b21) + np.abs(g12 - G) + np.abs(g21 - G)
    w1 = 1.0 / (1.0 + np.abs(g11 - g22))
    w2 = 1.0 / (1.0 + np.abs(g12 - g21))
    d_soft = (w1 * d1 + w2 * d2) / (w1 + w2)
    d_hard = np.where(e1 < e2, d1, np.where(e2 < e1, d2, 0.5 * (d1 + d2)))
    simple_edge = smoothstep(_clamp01((0.25 - np.minimum(e1, e2)) * 5.0))
    blue_diff = d_soft * (1.0 - simple_edge) + d_hard * simple_edge

    # Blue sites: the mirror of the red-site reconstruction.
    r11 = _sample(raw, rows - 1, cols - 1) * wb_r
    r22 = _sample(raw, rows + 1, cols + 1) * wb_r
    r12 = _sample(raw, rows - 1, cols + 1) * wb_r
    r21 = _sample(raw, rows + 1, cols - 1) * wb_r

    rd1 = 0.5 * ((r11 - g11) + (r22 - g22))
    rd2 = 0.5 * ((r12 - g12) + (r21 - g21))
    re1 = np.abs(r11 - r22) + np.abs(g11 - G) + np.abs(g22 - G)
    re2 = np.abs(r12 - r21) + np.abs(g12 - G) + np.abs(g21 - G)
    rw1 = 1.0 / (1.0 + np.abs(g11 - g22))
    rw2 = 1.0 / (1.0 + np.abs(g12 - g21))
    rd_soft = (rw1 * rd1 + rw2 * rd2) / (rw1 + rw2)
    rd_hard = np.where(re1 < re2, rd1, np.where(re2 < re1, rd2, 0.5 * (rd1 + rd2)))
    red_edge = smoothstep(_clamp01((0.25 - np.minimum(re1, re2)) * 5.0))
    red_diff = rd_soft * (1.0 - red_edge) + rd_hard * red_edge

    measured_centre = _sample(raw, rows, cols)

    # Green sites: which colour is horizontal follows the CFA neighbour parity.
    # A green site's horizontal neighbour sits at (r, c +/- 1), whose colour is
    # the 2x2 block entry with the opposite column parity; the vertical
    # neighbour sits at (r +/- 1, c), with the opposite row parity.
    block = ((int(cfa[0]), int(cfa[1])), (int(cfa[2]), int(cfa[3])))
    horizontal = np.empty(bayer.shape, dtype=np.int32)
    vertical = np.empty(bayer.shape, dtype=np.int32)
    for row in range(2):
        for col in range(2):
            horizontal[row::2, col::2] = block[row][1 - col]
            vertical[row::2, col::2] = block[1 - row][col]
    red_horizontal = horizontal == 0

    raw_left = _sample(raw, rows, cols - 1)
    raw_right = _sample(raw, rows, cols + 1)
    raw_up = _sample(raw, rows - 1, cols)
    raw_down = _sample(raw, rows + 1, cols)

    # The horizontal axis carries red when the block says so, otherwise blue;
    # the vertical axis carries the other one.
    horizontal_gain = np.where(red_horizontal, wb_r, wb_b)
    vertical_gain = np.where(red_horizontal, wb_b, wb_r)

    g_l = green_at(0, -1)
    g_r = green_at(0, 1)
    g_u = green_at(-1, 0)
    g_d = green_at(1, 0)
    chroma_floor = _t(params.chroma_weight_floor)
    w_l = 1.0 / (chroma_floor + np.abs(g_l - G))
    w_r = 1.0 / (chroma_floor + np.abs(g_r - G))
    w_u = 1.0 / (chroma_floor + np.abs(g_u - G))
    w_d = 1.0 / (chroma_floor + np.abs(g_d - G))
    horizontal_diff = (
        w_l * (raw_left * horizontal_gain - g_l)
        + w_r * (raw_right * horizontal_gain - g_r)
    ) / (w_l + w_r)
    vertical_diff = (
        w_u * (raw_up * vertical_gain - g_u) + w_d * (raw_down * vertical_gain - g_d)
    ) / (w_u + w_d)

    green_site_horizontal_ok = (cols > 0) & (cols < width - 1)
    green_site_vertical_ok = (rows > 0) & (rows < height - 1)

    # Assemble each colour plane from its own reconstruction rule.  The three
    # site masks are disjoint, so the assignment order cannot matter.
    R = np.where(is_red, measured_centre * wb_r, R)
    # Both diagonal reconstructions are gated on an interior site: at the border
    # the kernel falls back to ``R = G`` (or ``B = G``) rather than extrapolating
    # from taps that do not exist.
    R = np.where(is_blue, np.where(r_interior, G + red_diff, G), R)
    R = np.where(
        is_green,
        np.where(
            red_horizontal,
            np.where(green_site_horizontal_ok, G + horizontal_diff, G),
            np.where(green_site_vertical_ok, G + vertical_diff, G),
        ),
        R,
    )
    B = np.where(is_blue, measured_centre * wb_b, B)
    B = np.where(is_red, np.where(r_interior, G + blue_diff, G), B)
    B = np.where(
        is_green,
        np.where(
            red_horizontal,
            np.where(green_site_vertical_ok, G + vertical_diff, G),
            np.where(green_site_horizontal_ok, G + horizontal_diff, G),
        ),
        B,
    )

    # ------------------------------------------------------------------
    # Opponent-outlier suppression plus highlight recovery and compression
    # ------------------------------------------------------------------
    g_up_v = green_at(-1, 0)
    g_down_v = green_at(1, 0)
    g_left_v = green_at(0, -1)
    g_right_v = green_at(0, 1)
    g_min = np.minimum(
        G,
        np.minimum(g_up_v, np.minimum(g_down_v, np.minimum(g_left_v, g_right_v))),
    )
    g_max = np.maximum(
        G,
        np.maximum(g_up_v, np.maximum(g_down_v, np.maximum(g_left_v, g_right_v))),
    )
    texture_strength = smoothstep(
        _clamp01(
            (g_max - g_min - _t(params.opponent_texture_offset))
            / _t(params.opponent_texture_scale)
        )
    )
    rg = R - G
    bg = B - G
    opponent_magnitude = np.minimum(np.abs(rg), np.abs(bg))
    opponent_strength = smoothstep(
        _clamp01(
            (opponent_magnitude - _t(params.opponent_offset)) / _t(params.opponent_scale)
        )
    )
    artifact_blend = texture_strength * opponent_strength
    opposite = rg * bg < 0.0

    keep = 1.0 - artifact_blend
    # The kernel corrects the *interpolated* channel at each site: blue at a red
    # site, red at a blue site, and both at a green site.
    R = np.where(opposite & is_blue, G + rg * keep + bg * artifact_blend, R)
    R = np.where(opposite & is_green, G + rg * keep, R)
    B = np.where(opposite & is_red, G + bg * keep + rg * artifact_blend, B)
    B = np.where(opposite & is_green, G + bg * keep, B)

    inv_wb_r = 1.0 / max(0.1, wb_r)
    inv_wb_g = 1.0 / max(0.1, (wb_g1 + wb_g2) * 0.5)
    inv_wb_b = 1.0 / max(0.1, wb_b)

    max_raw = np.maximum(R * inv_wb_r, np.maximum(G * inv_wb_g, B * inv_wb_b))
    min_raw = np.minimum(R * inv_wb_r, np.minimum(G * inv_wb_g, B * inv_wb_b))

    factor = smoothstep(
        _clamp01((max_raw - _t(params.highlight_knee)) / _t(params.highlight_scale))
    )
    ratio = min_raw / np.maximum(1e-5, max_raw)
    neutrality = smoothstep(
        _clamp01(
            (ratio - _t(params.neutrality_offset)) / _t(params.neutrality_scale)
        )
    )
    final_factor = factor * neutrality

    peak = np.maximum(R, np.maximum(G, B))
    R = R * (1.0 - final_factor) + peak * final_factor
    G = G * (1.0 - final_factor) + peak * final_factor
    B = B * (1.0 - final_factor) + peak * final_factor

    R = np.maximum(0.0, R)
    G = np.maximum(0.0, G)
    B = np.maximum(0.0, B)

    output = np.empty((height, width, 3), dtype=np.float32)
    output[..., 0] = (R / np.sqrt(1.0 + R * R)).astype(np.float32)
    output[..., 1] = (G / np.sqrt(1.0 + G * G)).astype(np.float32)
    output[..., 2] = (B / np.sqrt(1.0 + B * B)).astype(np.float32)
    return output


__all__ = ["HamiltonParams", "hamilton_model", "smoothstep"]
