"""Reusable output kernels shared by Bayer demosaic families.

The demosaic algorithms produce linear RGB ``f32`` values.  This module owns
the common conversion to clamped, rounded BGR ``i32`` output used by the
family-specific AOT graphs.  Graph assembly and graph identifiers remain in
the individual compiler entrypoints.
"""

import taichi as ti


@ti.kernel
def median_filter_3x3_clamp(
    src: ti.types.ndarray(), dst: ti.types.ndarray(), h: ti.i32, w: ti.i32,
):
    """Single-plane 3x3 median with edge-clamp borders.

    ARM's residual filtering historically clamps out-of-range neighbors to
    the nearest edge pixel.  Keep that boundary policy explicit instead of
    silently reusing :func:`median_filter_pair_3x3`, whose reflected border
    policy is intentionally different.
    """
    for y, x in ti.ndrange(h, w):
        p0 = src[ti.math.clamp(y - 1, 0, h - 1), ti.math.clamp(x - 1, 0, w - 1)]
        p1 = src[ti.math.clamp(y - 1, 0, h - 1), x]
        p2 = src[ti.math.clamp(y - 1, 0, h - 1), ti.math.clamp(x + 1, 0, w - 1)]
        p3 = src[y, ti.math.clamp(x - 1, 0, w - 1)]
        p4 = src[y, x]
        p5 = src[y, ti.math.clamp(x + 1, 0, w - 1)]
        p6 = src[ti.math.clamp(y + 1, 0, h - 1), ti.math.clamp(x - 1, 0, w - 1)]
        p7 = src[ti.math.clamp(y + 1, 0, h - 1), x]
        p8 = src[ti.math.clamp(y + 1, 0, h - 1), ti.math.clamp(x + 1, 0, w - 1)]

        p1, p2 = ti.min(p1, p2), ti.max(p1, p2)
        p4, p5 = ti.min(p4, p5), ti.max(p4, p5)
        p7, p8 = ti.min(p7, p8), ti.max(p7, p8)
        p0, p1 = ti.min(p0, p1), ti.max(p0, p1)
        p3, p4 = ti.min(p3, p4), ti.max(p3, p4)
        p6, p7 = ti.min(p6, p7), ti.max(p6, p7)
        p1, p2 = ti.min(p1, p2), ti.max(p1, p2)
        p4, p5 = ti.min(p4, p5), ti.max(p4, p5)
        p7, p8 = ti.min(p7, p8), ti.max(p7, p8)
        p0, p3 = ti.min(p0, p3), ti.max(p0, p3)
        p5, p8 = ti.min(p5, p8), ti.max(p5, p8)
        p4, p7 = ti.min(p4, p7), ti.max(p4, p7)
        p1, p4 = ti.min(p1, p4), ti.max(p1, p4)
        p2, p5 = ti.min(p2, p5), ti.max(p2, p5)
        p3, p6 = ti.min(p3, p6), ti.max(p3, p6)
        p2, p3 = ti.min(p2, p3), ti.max(p2, p3)
        p4, p5 = ti.min(p4, p5), ti.max(p4, p5)
        p3, p4 = ti.min(p3, p4), ti.max(p3, p4)
        dst[y, x] = p4


@ti.kernel
def median_filter_pair_3x3(
    src_r: ti.types.ndarray(), src_b: ti.types.ndarray(),
    dst_r: ti.types.ndarray(), dst_b: ti.types.ndarray(),
    h: ti.i32, w: ti.i32,
):
    """Apply an exact 3x3 median to two scalar planes in one dispatch.

    The fixed network is shared by demosaic families that reconstruct red and
    blue colour differences.  Outputs are separate so callers can safely
    reuse no input buffer until this kernel has finished.
    """
    for y, x in ti.ndrange(h, w):
        vals_r = ti.Vector([0.0] * 9)
        vals_b = ti.Vector([0.0] * 9)
        idx = 0
        for dy in ti.static(range(-1, 2)):
            for dx in ti.static(range(-1, 2)):
                ny = y + dy
                nx = x + dx
                if ny < 0:
                    ny = 1
                elif ny >= h:
                    ny = h - 2
                if nx < 0:
                    nx = 1
                elif nx >= w:
                    nx = w - 2
                vals_r[idx] = src_r[ny, nx]
                vals_b[idx] = src_b[ny, nx]
                idx += 1
        # 19-comparator median-of-nine network.  It produces the same exact
        # median as the previous 25-comparator network with fewer ALU ops.
        for i, j in ti.static((
            (0, 1), (3, 4), (6, 7), (1, 2), (4, 5),
            (7, 8), (0, 1), (3, 4), (6, 7), (0, 3),
            (5, 8), (4, 7), (3, 6), (1, 4), (2, 5),
            (4, 7), (4, 2), (6, 4), (4, 2),
        )):
            if vals_r[i] > vals_r[j]:
                tmp = vals_r[i]
                vals_r[i] = vals_r[j]
                vals_r[j] = tmp
            if vals_b[i] > vals_b[j]:
                tmp = vals_b[i]
                vals_b[i] = vals_b[j]
                vals_b[j] = tmp
        dst_r[y, x] = vals_r[4]
        dst_b[y, x] = vals_b[4]


@ti.kernel
def median_filter_pair_cross(
    src_r: ti.types.ndarray(), src_b: ti.types.ndarray(),
    dst_r: ti.types.ndarray(), dst_b: ti.types.ndarray(),
    h: ti.i32, w: ti.i32,
):
    """Lower-cost 5-sample median for realtime demosaic experiments."""
    for y, x in ti.ndrange(h, w):
        yu = 1 if y == 0 else y - 1
        yd = h - 2 if y == h - 1 else y + 1
        xl = 1 if x == 0 else x - 1
        xr = w - 2 if x == w - 1 else x + 1
        vals_r = ti.Vector([
            src_r[y, x], src_r[yu, x], src_r[yd, x], src_r[y, xl], src_r[y, xr]
        ])
        vals_b = ti.Vector([
            src_b[y, x], src_b[yu, x], src_b[yd, x], src_b[y, xl], src_b[y, xr]
        ])
        for i, j in ti.static((
            (0, 1), (3, 4), (0, 3), (1, 4), (1, 3),
            (2, 4), (2, 3), (1, 2), (2, 3),
        )):
            if vals_r[i] > vals_r[j]:
                tmp = vals_r[i]
                vals_r[i] = vals_r[j]
                vals_r[j] = tmp
            if vals_b[i] > vals_b[j]:
                tmp = vals_b[i]
                vals_b[i] = vals_b[j]
                vals_b[j] = tmp
        dst_r[y, x] = vals_r[2]
        dst_b[y, x] = vals_b[2]


@ti.kernel
def rgb_to_bgr_i32(
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
