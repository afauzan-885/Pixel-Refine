"""Reusable reduced-resolution and preview demosaic kernels."""

import taichi as ti

from .demosaic_common import cfa_color, sample_normalized


@ti.kernel
def demosaic_green_1channel(
    bayer: ti.types.ndarray(), dst: ti.types.ndarray(),
    wb_r: ti.f32, wb_g1: ti.f32, wb_b: ti.f32, wb_g2: ti.f32,
    black: ti.f32, white: ti.f32, h: ti.i32, w: ti.i32,
    c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        colour = cfa_color(y, x, c00, c01, c10, c11)
        if colour == 1 or colour == 3:
            dst[y, x] = sample_normalized(
                bayer, y, x, black, white, wb_r, wb_g1, wb_b, wb_g2,
                c00, c01, c10, c11,
            )
        else:
            yl = ti.max(0, y - 1)
            yr = ti.min(h - 1, y + 1)
            xl = ti.max(0, x - 1)
            xr = ti.min(w - 1, x + 1)
            dst[y, x] = (
                sample_normalized(bayer, y, xl, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11)
                + sample_normalized(bayer, y, xr, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11)
                + sample_normalized(bayer, yl, x, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11)
                + sample_normalized(bayer, yr, x, black, white, wb_r, wb_g1, wb_b, wb_g2, c00, c01, c10, c11)
            ) * 0.25


@ti.kernel
def demosaic_rgb_half_res(
    bayer: ti.types.ndarray(), dst: ti.types.ndarray(),
    wb_r: ti.f32, wb_g1: ti.f32, wb_b: ti.f32, wb_g2: ti.f32,
    black: ti.f32, white: ti.f32, h: ti.i32, w: ti.i32,
    c00: ti.i32, c01: ti.i32, c10: ti.i32, c11: ti.i32,
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
            value = sample_normalized(
                bayer, yy, xx, black, white, wb_r, wb_g1, wb_b, wb_g2,
                c00, c01, c10, c11,
            )
            colour = cfa_color(yy, xx, c00, c01, c10, c11)
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
def rgb_to_luma(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: ti.i32, w: ti.i32):
    for y, x in ti.ndrange(h, w):
        dst[y, x] = src[y, x, 0] * 0.2126 + src[y, x, 1] * 0.7152 + src[y, x, 2] * 0.0722


@ti.kernel
def rgb_to_luma_half_res(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: ti.i32, w: ti.i32):
    for y, x in ti.ndrange(h // 2, w // 2):
        dst[y, x] = src[y, x, 0] * 0.2126 + src[y, x, 1] * 0.7152 + src[y, x, 2] * 0.0722

