"""Reusable core Bayer demosaic kernels.

Graph construction remains in the family compiler entrypoints; this module
owns native kernels that can be reused by multiple Bayer demosaic families.
Graph identifiers belong to the compiler ABI, while the Python kernel
definitions expose only native, algorithm-neutral names shared by DCB,
Hamilton, ARM, MLRI, and future Bayer families.
"""

import taichi as ti

from .demosaic_common import cfa_color, sample_normalized, sample_headroom


@ti.kernel
def preprocess_bayer(
    bayer: ti.types.ndarray(), mosaic: ti.types.ndarray(),
    wb_r: ti.f32, wb_g1: ti.f32, wb_b: ti.f32, wb_g2: ti.f32,
    black: ti.f32, white: ti.f32, h: ti.i32, w: ti.i32,
    c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        mosaic[y, x] = sample_normalized(
            bayer, y, x, black, white, wb_r, wb_g1, wb_b, wb_g2,
            c00, c01, c10, c11,
        )


@ti.kernel
def preprocess_bayer_headroom(
    bayer: ti.types.ndarray(), mosaic: ti.types.ndarray(),
    wb_r: ti.f32, wb_g1: ti.f32, wb_b: ti.f32, wb_g2: ti.f32,
    black: ti.f32, white: ti.f32, h: ti.i32, w: ti.i32,
    c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        mosaic[y, x] = sample_headroom(
            bayer, y, x, black, white, wb_r, wb_g1, wb_b, wb_g2,
            c00, c01, c10, c11,
        )


@ti.kernel
def preprocess_and_interpolate_green(
    bayer: ti.types.ndarray(), mosaic: ti.types.ndarray(), green: ti.types.ndarray(),
    wb_r: ti.f32, wb_g1: ti.f32, wb_b: ti.f32, wb_g2: ti.f32,
    black: ti.f32, white: ti.f32, h: ti.i32, w: ti.i32,
    c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    """Normalize Bayer data and reconstruct green in one memory pass.

    The normalized mosaic is still written for later RGB reconstruction, but
    green interpolation reads the source Bayer samples directly.  This avoids
    a separate full-frame read/write pass without changing the interpolation
    equations or CFA boundary policy.
    """
    for y, x in ti.ndrange(h, w):
        current = sample_normalized(
            bayer, y, x, black, white, wb_r, wb_g1, wb_b, wb_g2,
            c00, c01, c10, c11,
        )
        mosaic[y, x] = current
        colour = cfa_color(y, x, c00, c01, c10, c11)
        if colour == 1 or colour == 3:
            green[y, x] = current
        else:
            yl = y - 1
            yr = y + 1
            xl = x - 1
            xr = x + 1
            if y == 0:
                yl = 1
            elif y == h - 1:
                yr = h - 2
            if x == 0:
                xl = 1
            elif x == w - 1:
                xr = w - 2
            left = sample_normalized(
                bayer, y, xl, black, white, wb_r, wb_g1, wb_b, wb_g2,
                c00, c01, c10, c11,
            )
            right = sample_normalized(
                bayer, y, xr, black, white, wb_r, wb_g1, wb_b, wb_g2,
                c00, c01, c10, c11,
            )
            up = sample_normalized(
                bayer, yl, x, black, white, wb_r, wb_g1, wb_b, wb_g2,
                c00, c01, c10, c11,
            )
            down = sample_normalized(
                bayer, yr, x, black, white, wb_r, wb_g1, wb_b, wb_g2,
                c00, c01, c10, c11,
            )
            gh = (left + right) * 0.5
            gv = (up + down) * 0.5
            dh = ti.abs(left - right)
            dv = ti.abs(up - down)
            weight_h = 1.0 / (1e-4 + dh)
            weight_v = 1.0 / (1e-4 + dv)
            green[y, x] = (gh * weight_h + gv * weight_v) / (weight_h + weight_v)


@ti.kernel
def preprocess_and_interpolate_green_headroom(
    bayer: ti.types.ndarray(), mosaic: ti.types.ndarray(), green: ti.types.ndarray(),
    wb_r: ti.f32, wb_g1: ti.f32, wb_b: ti.f32, wb_g2: ti.f32,
    black: ti.f32, white: ti.f32, h: ti.i32, w: ti.i32,
    c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    """Headroom-preserving variant of :func:`preprocess_and_interpolate_green`."""
    for y, x in ti.ndrange(h, w):
        current = sample_headroom(
            bayer, y, x, black, white, wb_r, wb_g1, wb_b, wb_g2,
            c00, c01, c10, c11,
        )
        mosaic[y, x] = current
        colour = cfa_color(y, x, c00, c01, c10, c11)
        if colour == 1 or colour == 3:
            green[y, x] = current
        else:
            yl = y - 1
            yr = y + 1
            xl = x - 1
            xr = x + 1
            if y == 0:
                yl = 1
            elif y == h - 1:
                yr = h - 2
            if x == 0:
                xl = 1
            elif x == w - 1:
                xr = w - 2
            left = sample_headroom(
                bayer, y, xl, black, white, wb_r, wb_g1, wb_b, wb_g2,
                c00, c01, c10, c11,
            )
            right = sample_headroom(
                bayer, y, xr, black, white, wb_r, wb_g1, wb_b, wb_g2,
                c00, c01, c10, c11,
            )
            up = sample_headroom(
                bayer, yl, x, black, white, wb_r, wb_g1, wb_b, wb_g2,
                c00, c01, c10, c11,
            )
            down = sample_headroom(
                bayer, yr, x, black, white, wb_r, wb_g1, wb_b, wb_g2,
                c00, c01, c10, c11,
            )
            gh = (left + right) * 0.5
            gv = (up + down) * 0.5
            dh = ti.abs(left - right)
            dv = ti.abs(up - down)
            weight_h = 1.0 / (1e-4 + dh)
            weight_v = 1.0 / (1e-4 + dv)
            green[y, x] = (gh * weight_h + gv * weight_v) / (weight_h + weight_v)


@ti.kernel
def interpolate_green(
    mosaic: ti.types.ndarray(), green: ti.types.ndarray(), h: ti.i32, w: ti.i32,
    c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        colour = cfa_color(y, x, c00, c01, c10, c11)
        if colour == 1 or colour == 3:
            green[y, x] = mosaic[y, x]
        else:
            yl = y - 1
            yr = y + 1
            xl = x - 1
            xr = x + 1
            if y == 0:
                yl = 1
            elif y == h - 1:
                yr = h - 2
            if x == 0:
                xl = 1
            elif x == w - 1:
                xr = w - 2
            gh = (mosaic[y, xl] + mosaic[y, xr]) * 0.5
            gv = (mosaic[yl, x] + mosaic[yr, x]) * 0.5
            dh = ti.abs(mosaic[y, xl] - mosaic[y, xr])
            dv = ti.abs(mosaic[yl, x] - mosaic[yr, x])
            weight_h = 1.0 / (1e-4 + dh)
            weight_v = 1.0 / (1e-4 + dv)
            green[y, x] = (gh * weight_h + gv * weight_v) / (weight_h + weight_v)


@ti.kernel
def reconstruct_rgb(
    mosaic: ti.types.ndarray(), green: ti.types.ndarray(), rgb: ti.types.ndarray(),
    h: ti.i32, w: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        colour = cfa_color(y, x, c00, c01, c10, c11)
        yl = y - 1
        yr = y + 1
        xl = x - 1
        xr = x + 1
        if y == 0:
            yl = 1
        elif y == h - 1:
            yr = h - 2
        if x == 0:
            xl = 1
        elif x == w - 1:
            xr = w - 2
        r = green[y, x]
        g = green[y, x]
        b = green[y, x]
        if colour == 0:
            r = mosaic[y, x]
            b = g + (
                (mosaic[yl, xl] - green[yl, xl])
                + (mosaic[yl, xr] - green[yl, xr])
                + (mosaic[yr, xl] - green[yr, xl])
                + (mosaic[yr, xr] - green[yr, xr])
            ) * 0.25
        elif colour == 2:
            b = mosaic[y, x]
            r = g + (
                (mosaic[yl, xl] - green[yl, xl])
                + (mosaic[yl, xr] - green[yl, xr])
                + (mosaic[yr, xl] - green[yr, xl])
                + (mosaic[yr, xr] - green[yr, xr])
            ) * 0.25
        else:
            left_colour = cfa_color(y, xl, c00, c01, c10, c11)
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
def reconstruct_rgb_clamped(
    mosaic: ti.types.ndarray(), green: ti.types.ndarray(), dst: ti.types.ndarray(),
    h: ti.i32, w: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    """Reconstruct RGB and clamp directly into the final normalized output."""
    for y, x in ti.ndrange(h, w):
        colour = cfa_color(y, x, c00, c01, c10, c11)
        yl = y - 1
        yr = y + 1
        xl = x - 1
        xr = x + 1
        if y == 0:
            yl = 1
        elif y == h - 1:
            yr = h - 2
        if x == 0:
            xl = 1
        elif x == w - 1:
            xr = w - 2
        r = green[y, x]
        g = green[y, x]
        b = green[y, x]
        if colour == 0:
            r = mosaic[y, x]
            b = g + (
                (mosaic[yl, xl] - green[yl, xl])
                + (mosaic[yl, xr] - green[yl, xr])
                + (mosaic[yr, xl] - green[yr, xl])
                + (mosaic[yr, xr] - green[yr, xr])
            ) * 0.25
        elif colour == 2:
            b = mosaic[y, x]
            r = g + (
                (mosaic[yl, xl] - green[yl, xl])
                + (mosaic[yl, xr] - green[yl, xr])
                + (mosaic[yr, xl] - green[yr, xl])
                + (mosaic[yr, xr] - green[yr, xr])
            ) * 0.25
        else:
            left_colour = cfa_color(y, xl, c00, c01, c10, c11)
            if left_colour == 0:
                r = g + ((mosaic[y, xl] - green[y, xl]) + (mosaic[y, xr] - green[y, xr])) * 0.5
                b = g + ((mosaic[yl, x] - green[yl, x]) + (mosaic[yr, x] - green[yr, x])) * 0.5
            else:
                b = g + ((mosaic[y, xl] - green[y, xl]) + (mosaic[y, xr] - green[y, xr])) * 0.5
                r = g + ((mosaic[yl, x] - green[yl, x]) + (mosaic[yr, x] - green[yr, x])) * 0.5
        dst[y, x, 0] = ti.math.clamp(r, 0.0, 1.0)
        dst[y, x, 1] = ti.math.clamp(g, 0.0, 1.0)
        dst[y, x, 2] = ti.math.clamp(b, 0.0, 1.0)


@ti.kernel
def refine_chroma(
    src: ti.types.ndarray(), mosaic: ti.types.ndarray(), dst: ti.types.ndarray(),
    h: ti.i32, w: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        g = src[y, x, 1]
        r_diff = 0.0
        b_diff = 0.0
        count = 0.0
        for dy, dx in ti.static(ti.ndrange(3, 3)):
            ny = y + dy - 1
            nx = x + dx - 1
            if ny < 0:
                ny = 1
            elif ny >= h:
                ny = h - 2
            if nx < 0:
                nx = 1
            elif nx >= w:
                nx = w - 2
            r_diff += src[ny, nx, 0] - src[ny, nx, 1]
            b_diff += src[ny, nx, 2] - src[ny, nx, 1]
            count += 1.0
        r = g + r_diff / count
        b = g + b_diff / count
        colour = cfa_color(y, x, c00, c01, c10, c11)
        if colour == 0:
            r = mosaic[y, x]
        elif colour == 2:
            b = mosaic[y, x]
        dst[y, x, 0] = ti.max(r, 0.0)
        dst[y, x, 1] = ti.max(g, 0.0)
        dst[y, x, 2] = ti.max(b, 0.0)


@ti.kernel
def refine_chroma_clamped(
    src: ti.types.ndarray(), mosaic: ti.types.ndarray(), dst: ti.types.ndarray(),
    h: ti.i32, w: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    """Final chroma refinement that writes directly to a normalized output."""
    for y, x in ti.ndrange(h, w):
        g = src[y, x, 1]
        r_diff = 0.0
        b_diff = 0.0
        count = 0.0
        for dy, dx in ti.static(ti.ndrange(3, 3)):
            ny = y + dy - 1
            nx = x + dx - 1
            if ny < 0:
                ny = 1
            elif ny >= h:
                ny = h - 2
            if nx < 0:
                nx = 1
            elif nx >= w:
                nx = w - 2
            r_diff += src[ny, nx, 0] - src[ny, nx, 1]
            b_diff += src[ny, nx, 2] - src[ny, nx, 1]
            count += 1.0
        r = g + r_diff / count
        b = g + b_diff / count
        colour = cfa_color(y, x, c00, c01, c10, c11)
        if colour == 0:
            r = mosaic[y, x]
        elif colour == 2:
            b = mosaic[y, x]
        dst[y, x, 0] = ti.math.clamp(r, 0.0, 1.0)
        dst[y, x, 1] = ti.math.clamp(g, 0.0, 1.0)
        dst[y, x, 2] = ti.math.clamp(b, 0.0, 1.0)


@ti.kernel
def refine_chroma_cross_clamped(
    src: ti.types.ndarray(), mosaic: ti.types.ndarray(), dst: ti.types.ndarray(),
    h: ti.i32, w: ti.i32, c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    """Lower-cost chroma refinement using the cardinal cross neighbourhood."""
    for y, x in ti.ndrange(h, w):
        yu = 1 if y == 0 else y - 1
        yd = h - 2 if y == h - 1 else y + 1
        xl = 1 if x == 0 else x - 1
        xr = w - 2 if x == w - 1 else x + 1
        r_diff = (
            src[y, x, 0] - src[y, x, 1]
            + src[yu, x, 0] - src[yu, x, 1]
            + src[yd, x, 0] - src[yd, x, 1]
            + src[y, xl, 0] - src[y, xl, 1]
            + src[y, xr, 0] - src[y, xr, 1]
        ) * 0.2
        b_diff = (
            src[y, x, 2] - src[y, x, 1]
            + src[yu, x, 2] - src[yu, x, 1]
            + src[yd, x, 2] - src[yd, x, 1]
            + src[y, xl, 2] - src[y, xl, 1]
            + src[y, xr, 2] - src[y, xr, 1]
        ) * 0.2
        g = src[y, x, 1]
        r = g + r_diff
        b = g + b_diff
        colour = cfa_color(y, x, c00, c01, c10, c11)
        if colour == 0:
            r = mosaic[y, x]
        elif colour == 2:
            b = mosaic[y, x]
        dst[y, x, 0] = ti.math.clamp(r, 0.0, 1.0)
        dst[y, x, 1] = ti.math.clamp(g, 0.0, 1.0)
        dst[y, x, 2] = ti.math.clamp(b, 0.0, 1.0)


@ti.kernel
def copy_rgb(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: ti.i32, w: ti.i32):
    for y, x in ti.ndrange(h, w):
        for channel in ti.static(range(3)):
            dst[y, x, channel] = ti.math.clamp(src[y, x, channel], 0.0, 1.0)


@ti.kernel
def copy_rgb_headroom(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: ti.i32, w: ti.i32):
    """Copy linear camera RGB without discarding white-balance headroom."""
    for y, x in ti.ndrange(h, w):
        for channel in ti.static(range(3)):
            dst[y, x, channel] = ti.max(src[y, x, channel], 0.0)
