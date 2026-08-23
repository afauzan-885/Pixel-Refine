"""Shared Bayer/white-balance helpers for demosaic AOT kernels.

The functions in this module intentionally stay small and Taichi-compatible.
They contain no graph assembly or runtime policy, so other demosaic kernels
can reuse the exact same CFA and RAW/headroom semantics.  Hamilton, ARM, and
future Bayer algorithms can depend on this module without importing a family
specific graph builder.
"""

import taichi as ti


@ti.func
def cfa_color(y, x, c00, c01, c10, c11):
    colour = c00
    if y % 2 == 0:
        colour = c00 if x % 2 == 0 else c01
    else:
        colour = c10 if x % 2 == 0 else c11
    return colour


@ti.func
def channel_gain(colour, wb_r, wb_g1, wb_b, wb_g2):
    result = wb_g1
    if colour == 0:
        result = wb_r
    elif colour == 2:
        result = wb_b
    elif colour == 3:
        result = wb_g2
    return result


@ti.func
def sample_normalized(
    bayer: ti.template(), y, x, black, white,
    wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11,
):
    """Normalize Bayer RAW with Quad-Aware Tint Neutralization (No Magenta, No Halos)."""
    colour = cfa_color(y, x, c00, c01, c10, c11)
    inv_range = 1.0 / ti.max(1.0, white - black)
    raw = ti.math.clamp((bayer[y, x] - black) * inv_range, 0.0, 1.0)
    gain = channel_gain(colour, wb_r, wb_g1, wb_b, wb_g2)
    
    # Quad-Aware Tint Neutralization:
    # Reads 2x2 Bayer cell max so all channels in overexposed quad transition gains together,
    # completely eliminating magenta clouds without creating dark halos around edges.
    y0 = (y // 2) * 2
    x0 = (x // 2) * 2
    v00 = (bayer[y0, x0] - black) * inv_range
    v01 = (bayer[y0, x0 + 1] - black) * inv_range
    v10 = (bayer[y0 + 1, x0] - black) * inv_range
    v11 = (bayer[y0 + 1, x0 + 1] - black) * inv_range
    
    quad_peak = ti.math.clamp(ti.max(v00, ti.max(v01, ti.max(v10, v11))), 0.0, 1.0)
    
    blend = ti.math.clamp((quad_peak - 0.78) / 0.22, 0.0, 1.0)
    blend = blend * blend * (3.0 - 2.0 * blend)
    
    effective_gain = gain * (1.0 - blend) + 1.0 * blend
    return raw * effective_gain


@ti.func
def sample_headroom(
    bayer: ti.template(), y, x, black, white,
    wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11,
):
    """Normalize RAW with Quad-Aware Tint Neutralization for Headroom Mode."""
    colour = cfa_color(y, x, c00, c01, c10, c11)
    inv_range = 1.0 / ti.max(1.0, white - black)
    raw = (bayer[y, x] - black) * inv_range
    gain = channel_gain(colour, wb_r, wb_g1, wb_b, wb_g2)
    
    y0 = (y // 2) * 2
    x0 = (x // 2) * 2
    v00 = (bayer[y0, x0] - black) * inv_range
    v01 = (bayer[y0, x0 + 1] - black) * inv_range
    v10 = (bayer[y0 + 1, x0] - black) * inv_range
    v11 = (bayer[y0 + 1, x0 + 1] - black) * inv_range
    
    quad_peak = ti.math.clamp(ti.max(v00, ti.max(v01, ti.max(v10, v11))), 0.0, 1.0)
    
    blend = ti.math.clamp((quad_peak - 0.78) / 0.22, 0.0, 1.0)
    blend = blend * blend * (3.0 - 2.0 * blend)
    
    effective_gain = gain * (1.0 - blend) + 1.0 * blend
    return ti.max(raw, 0.0) * effective_gain


@ti.func
def fast_gamma(x: ti.f32) -> ti.f32:
    t = ti.math.sqrt(x)
    return t * (1.30547177 + t * (-0.78947190 + t * (0.79064221 - 0.30664208 * t)))


@ti.func
def reflect_index(index: ti.i32, length: ti.i32) -> ti.i32:
    """Mirror an integer coordinate for stencil access at image borders."""
    result = 0
    if length > 1:
        # All current demosaic stencils stay within a few pixels of the
        # border, so a single branch reflection avoids modulo/division in the
        # hot path.  The final clamp keeps tiny test images well-defined.
        result = index
        if result < 0:
            result = -result
        if result >= length:
            result = 2 * length - 2 - result
        if result < 0:
            result = 0
    return result


@ti.func
def select_gain(ym: ti.i32, xm: ti.i32, g00: ti.f32, g01: ti.f32, g10: ti.f32, g11: ti.f32) -> ti.f32:
    return ti.select(ym == 0, ti.select(xm == 0, g00, g01), ti.select(xm == 0, g10, g11))


@ti.func
def green_gain(nr: ti.i32, nc: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32, wb_g1: ti.f32, wb_g2: ti.f32) -> ti.f32:
    colour = c00
    if nr % 2 == 0:
        colour = c00 if nc % 2 == 0 else c01
    else:
        colour = c10 if nc % 2 == 0 else c11
    return wb_g1 if colour == 1 else wb_g2
