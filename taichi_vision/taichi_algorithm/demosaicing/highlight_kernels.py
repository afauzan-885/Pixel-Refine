"""Reusable Bayer highlight-ratio kernels."""

import taichi as ti


@ti.kernel
def highlight_ratio_seed(
    src: ti.types.ndarray(), ratio_map: ti.types.ndarray(),
    wb_r: ti.f32, wb_g: ti.f32, wb_b: ti.f32,
    h: ti.i32, w: ti.i32, map_h: ti.i32, map_w: ti.i32,
):
    for my, mx in ti.ndrange(map_h, map_w):
        ratio_map[my, mx, 0] = 1.0
        ratio_map[my, mx, 1] = 1.0


@ti.kernel
def highlight_ratio_propagate(
    src_map: ti.types.ndarray(), dst_map: ti.types.ndarray(),
    map_h: ti.i32, map_w: ti.i32,
):
    for my, mx in ti.ndrange(map_h, map_w):
        dst_map[my, mx, 0] = src_map[my, mx, 0]
        dst_map[my, mx, 1] = src_map[my, mx, 1]


@ti.kernel
def highlight_apply(
    src: ti.types.ndarray(), ratio_src: ti.types.ndarray(), dst: ti.types.ndarray(),
    wb_r: ti.f32, wb_g: ti.f32, wb_b: ti.f32,
    h: ti.i32, w: ti.i32, map_h: ti.i32, map_w: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        dst[y, x, 0] = src[y, x, 0]
        dst[y, x, 1] = src[y, x, 1]
        dst[y, x, 2] = src[y, x, 2]


@ti.kernel
def libraw_neutral_highlight_blend(
    src: ti.types.ndarray(), dst: ti.types.ndarray(),
    wb_r: ti.f32, wb_g: ti.f32, wb_b: ti.f32,
    threshold: ti.f32, strength: ti.f32,
    h: ti.i32, w: ti.i32,
):
    for y, x in ti.ndrange(h, w):
        dst[y, x, 0] = ti.math.clamp(src[y, x, 0], 0.0, 1.0)
        dst[y, x, 1] = ti.math.clamp(src[y, x, 1], 0.0, 1.0)
        dst[y, x, 2] = ti.math.clamp(src[y, x, 2], 0.0, 1.0)
