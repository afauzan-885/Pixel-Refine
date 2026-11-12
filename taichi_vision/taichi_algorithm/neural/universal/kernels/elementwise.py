"""Elementwise universal kernels: unary, binary, compare, where, cast."""

import taichi as ti

from .common import MAX_RANK, nu_binop, nu_pad_list, nu_unary


@ti.kernel
def nu_unary_f32(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    code: ti.i32,
    lo: ti.f32,
    hi: ti.f32,
):
    for i in range(n):
        y[i] = nu_unary(x[i], code, lo, hi)


@ti.kernel
def nu_clip_f32(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    lo: ti.f32,
    hi: ti.f32,
):
    for i in range(n):
        y[i] = ti.max(lo, ti.min(hi, x[i]))


@ti.kernel
def nu_binary_flat(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    code: ti.i32,
):
    for i in range(n):
        y[i] = nu_binop(a[i], b[i], code)


@ti.kernel
def nu_binary_scalar_rhs(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    code: ti.i32,
):
    bv = b[0]
    for i in range(n):
        y[i] = nu_binop(a[i], bv, code)


@ti.kernel
def nu_binary_scalar_lhs(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    code: ti.i32,
):
    av = a[0]
    for i in range(n):
        y[i] = nu_binop(av, b[i], code)


@ti.kernel
def nu_binary_broadcast(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    code: ti.i32,
    o0: ti.i32, o1: ti.i32, o2: ti.i32, o3: ti.i32,
    o4: ti.i32, o5: ti.i32, o6: ti.i32, o7: ti.i32,
    a0: ti.i32, a1: ti.i32, a2: ti.i32, a3: ti.i32,
    a4: ti.i32, a5: ti.i32, a6: ti.i32, a7: ti.i32,
    b0: ti.i32, b1: ti.i32, b2: ti.i32, b3: ti.i32,
    b4: ti.i32, b5: ti.i32, b6: ti.i32, b7: ti.i32,
):
    for i in range(n):
        rem = i
        ai = 0
        bi = 0
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = nu_pad_list(o0, o1, o2, o3, o4, o5, o6, o7, d)
            coord = rem % dim
            rem = rem // dim
            ai += coord * nu_pad_list(a0, a1, a2, a3, a4, a5, a6, a7, d)
            bi += coord * nu_pad_list(b0, b1, b2, b3, b4, b5, b6, b7, d)
        y[i] = nu_binop(a[ai], b[bi], code)


@ti.kernel
def nu_binary_unary_broadcast(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    binary_code: ti.i32,
    unary_code: ti.i32,
    lo: ti.f32,
    hi: ti.f32,
    o0: ti.i32, o1: ti.i32, o2: ti.i32, o3: ti.i32,
    o4: ti.i32, o5: ti.i32, o6: ti.i32, o7: ti.i32,
    a0: ti.i32, a1: ti.i32, a2: ti.i32, a3: ti.i32,
    a4: ti.i32, a5: ti.i32, a6: ti.i32, a7: ti.i32,
    b0: ti.i32, b1: ti.i32, b2: ti.i32, b3: ti.i32,
    b4: ti.i32, b5: ti.i32, b6: ti.i32, b7: ti.i32,
):
    for i in range(n):
        rem = i
        ai = 0
        bi = 0
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = nu_pad_list(o0, o1, o2, o3, o4, o5, o6, o7, d)
            coord = rem % dim
            rem = rem // dim
            ai += coord * nu_pad_list(a0, a1, a2, a3, a4, a5, a6, a7, d)
            bi += coord * nu_pad_list(b0, b1, b2, b3, b4, b5, b6, b7, d)
        value = nu_binop(a[ai], b[bi], binary_code)
        y[i] = nu_unary(value, unary_code, lo, hi)


@ti.kernel
def nu_fused_unary_binary(
    x: ti.types.ndarray(ti.f32, 1),
    other: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    unary_code: ti.i32,
    binary_code: ti.i32,
    unary_is_left: ti.i32,
    lo: ti.f32,
    hi: ti.f32,
    o0: ti.i32, o1: ti.i32, o2: ti.i32, o3: ti.i32,
    o4: ti.i32, o5: ti.i32, o6: ti.i32, o7: ti.i32,
    x0: ti.i32, x1: ti.i32, x2: ti.i32, x3: ti.i32,
    x4: ti.i32, x5: ti.i32, x6: ti.i32, x7: ti.i32,
    b0: ti.i32, b1: ti.i32, b2: ti.i32, b3: ti.i32,
    b4: ti.i32, b5: ti.i32, b6: ti.i32, b7: ti.i32,
):
    """Apply one unary op then one binary op in a single broadcast pass."""
    for i in range(n):
        rem = i
        xi = 0
        bi = 0
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = nu_pad_list(o0, o1, o2, o3, o4, o5, o6, o7, d)
            coord = rem % dim
            rem = rem // dim
            xi += coord * nu_pad_list(x0, x1, x2, x3, x4, x5, x6, x7, d)
            bi += coord * nu_pad_list(b0, b1, b2, b3, b4, b5, b6, b7, d)
        unary_value = ti.cast(nu_unary(x[xi], unary_code, lo, hi), ti.f32)
        other_value = other[bi]
        if unary_is_left != 0:
            y[i] = nu_binop(unary_value, other_value, binary_code)
        else:
            y[i] = nu_binop(other_value, unary_value, binary_code)


@ti.kernel
def nu_fused_sub_sub_div(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    c: ti.types.ndarray(ti.f32, 1),
    d: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    first_tmp: ti.types.ndarray(ti.f32, 1),
    second_tmp: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
):
    """Evaluate ``((a - b) - c) / d`` with FP32 materialized intermediates."""
    for i in range(n):
        first_tmp[i] = ti.cast(nu_binop(a[i], b[i], 1), ti.f32)
        second_tmp[i] = ti.cast(nu_binop(first_tmp[i], c[i], 1), ti.f32)
        y[i] = nu_binop(second_tmp[i], d[i], 3)


@ti.kernel
def nu_add_sqrt_clip_broadcast(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    clip_lo: ti.f32,
    clip_hi: ti.f32,
    o0: ti.i32, o1: ti.i32, o2: ti.i32, o3: ti.i32,
    o4: ti.i32, o5: ti.i32, o6: ti.i32, o7: ti.i32,
    a0: ti.i32, a1: ti.i32, a2: ti.i32, a3: ti.i32,
    a4: ti.i32, a5: ti.i32, a6: ti.i32, a7: ti.i32,
    b0: ti.i32, b1: ti.i32, b2: ti.i32, b3: ti.i32,
    b4: ti.i32, b5: ti.i32, b6: ti.i32, b7: ti.i32,
):
    for i in range(n):
        rem = i
        ai = 0
        bi = 0
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = nu_pad_list(o0, o1, o2, o3, o4, o5, o6, o7, d)
            coord = rem % dim
            rem = rem // dim
            ai += coord * nu_pad_list(a0, a1, a2, a3, a4, a5, a6, a7, d)
            bi += coord * nu_pad_list(b0, b1, b2, b3, b4, b5, b6, b7, d)
        value = nu_binop(a[ai], b[bi], 0)
        value = nu_unary(value, 6, 0.0, 0.0)
        # ONNX Clip propagates NaN; Taichi min/max may select the finite bound.
        if ti.math.isnan(value):
            y[i] = value
        else:
            y[i] = nu_unary(value, 21, clip_lo, clip_hi)


@ti.kernel
def nu_sub_clip_sqrt_broadcast(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    clip_lo: ti.f32,
    clip_hi: ti.f32,
    o0: ti.i32, o1: ti.i32, o2: ti.i32, o3: ti.i32,
    o4: ti.i32, o5: ti.i32, o6: ti.i32, o7: ti.i32,
    a0: ti.i32, a1: ti.i32, a2: ti.i32, a3: ti.i32,
    a4: ti.i32, a5: ti.i32, a6: ti.i32, a7: ti.i32,
    b0: ti.i32, b1: ti.i32, b2: ti.i32, b3: ti.i32,
    b4: ti.i32, b5: ti.i32, b6: ti.i32, b7: ti.i32,
):
    for i in range(n):
        rem = i
        ai = 0
        bi = 0
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = nu_pad_list(o0, o1, o2, o3, o4, o5, o6, o7, d)
            coord = rem % dim
            rem = rem // dim
            ai += coord * nu_pad_list(a0, a1, a2, a3, a4, a5, a6, a7, d)
            bi += coord * nu_pad_list(b0, b1, b2, b3, b4, b5, b6, b7, d)
        value = nu_binop(a[ai], b[bi], 1)
        if ti.math.isnan(value):
            y[i] = value
        else:
            value = nu_unary(value, 21, clip_lo, clip_hi)
            y[i] = nu_unary(value, 6, 0.0, 0.0)


@ti.kernel
def nu_prelu(
    x: ti.types.ndarray(ti.f32, 1),
    slope: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    o0: ti.i32, o1: ti.i32, o2: ti.i32, o3: ti.i32,
    o4: ti.i32, o5: ti.i32, o6: ti.i32, o7: ti.i32,
    s0: ti.i32, s1: ti.i32, s2: ti.i32, s3: ti.i32,
    s4: ti.i32, s5: ti.i32, s6: ti.i32, s7: ti.i32,
):
    for i in range(n):
        rem = i
        si = 0
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = nu_pad_list(o0, o1, o2, o3, o4, o5, o6, o7, d)
            coord = rem % dim
            rem = rem // dim
            si += coord * nu_pad_list(s0, s1, s2, s3, s4, s5, s6, s7, d)
        value = x[i]
        y[i] = value if value >= 0.0 else value * slope[si]


@ti.kernel
def nu_binary_cmp_flat(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
    code: ti.i32,
):
    for i in range(n):
        y[i] = ti.cast(nu_binop(a[i], b[i], code), ti.i32)


@ti.kernel
def nu_binary_cmp_scalar_rhs(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
    code: ti.i32,
):
    bv = b[0]
    for i in range(n):
        y[i] = ti.cast(nu_binop(a[i], bv, code), ti.i32)


@ti.kernel
def nu_binary_cmp_scalar_lhs(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
    code: ti.i32,
):
    av = a[0]
    for i in range(n):
        y[i] = ti.cast(nu_binop(av, b[i], code), ti.i32)


@ti.kernel
def nu_binary_cmp_broadcast(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
    code: ti.i32,
    o0: ti.i32, o1: ti.i32, o2: ti.i32, o3: ti.i32,
    o4: ti.i32, o5: ti.i32, o6: ti.i32, o7: ti.i32,
    a0: ti.i32, a1: ti.i32, a2: ti.i32, a3: ti.i32,
    a4: ti.i32, a5: ti.i32, a6: ti.i32, a7: ti.i32,
    b0: ti.i32, b1: ti.i32, b2: ti.i32, b3: ti.i32,
    b4: ti.i32, b5: ti.i32, b6: ti.i32, b7: ti.i32,
):
    for i in range(n):
        rem = i
        ai = 0
        bi = 0
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = nu_pad_list(o0, o1, o2, o3, o4, o5, o6, o7, d)
            coord = rem % dim
            rem = rem // dim
            ai += coord * nu_pad_list(a0, a1, a2, a3, a4, a5, a6, a7, d)
            bi += coord * nu_pad_list(b0, b1, b2, b3, b4, b5, b6, b7, d)
        y[i] = ti.cast(nu_binop(a[ai], b[bi], code), ti.i32)


@ti.kernel
def nu_and_i32(
    a: ti.types.ndarray(ti.i32, 1),
    b: ti.types.ndarray(ti.i32, 1),
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = 1 if (a[i] != 0 and b[i] != 0) else 0


@ti.kernel
def nu_or_i32(
    a: ti.types.ndarray(ti.i32, 1),
    b: ti.types.ndarray(ti.i32, 1),
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = 1 if (a[i] != 0 or b[i] != 0) else 0


@ti.kernel
def nu_xor_i32(
    a: ti.types.ndarray(ti.i32, 1),
    b: ti.types.ndarray(ti.i32, 1),
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = 1 if ((a[i] != 0) != (b[i] != 0)) else 0


@ti.kernel
def nu_not_i32(
    a: ti.types.ndarray(ti.i32, 1),
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = 0 if a[i] != 0 else 1


@ti.kernel
def nu_where_flat(
    cond: ti.types.ndarray(ti.i32, 1),
    x: ti.types.ndarray(ti.f32, 1),
    y_in: ti.types.ndarray(ti.f32, 1),
    out: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
):
    for i in range(n):
        out[i] = x[i] if cond[i] != 0 else y_in[i]


@ti.kernel
def nu_where_broadcast(
    cond: ti.types.ndarray(ti.i32, 1),
    x: ti.types.ndarray(ti.f32, 1),
    y_in: ti.types.ndarray(ti.f32, 1),
    out: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    o0: ti.i32, o1: ti.i32, o2: ti.i32, o3: ti.i32,
    o4: ti.i32, o5: ti.i32, o6: ti.i32, o7: ti.i32,
    c0: ti.i32, c1: ti.i32, c2: ti.i32, c3: ti.i32,
    c4: ti.i32, c5: ti.i32, c6: ti.i32, c7: ti.i32,
    x0: ti.i32, x1: ti.i32, x2: ti.i32, x3: ti.i32,
    x4: ti.i32, x5: ti.i32, x6: ti.i32, x7: ti.i32,
    y0: ti.i32, y1: ti.i32, y2: ti.i32, y3: ti.i32,
    y4: ti.i32, y5: ti.i32, y6: ti.i32, y7: ti.i32,
):
    for i in range(n):
        rem = i
        ci = 0
        xi = 0
        yi = 0
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = nu_pad_list(o0, o1, o2, o3, o4, o5, o6, o7, d)
            coord = rem % dim
            rem = rem // dim
            ci += coord * nu_pad_list(c0, c1, c2, c3, c4, c5, c6, c7, d)
            xi += coord * nu_pad_list(x0, x1, x2, x3, x4, x5, x6, x7, d)
            yi += coord * nu_pad_list(y0, y1, y2, y3, y4, y5, y6, y7, d)
        out[i] = x[xi] if cond[ci] != 0 else y_in[yi]


@ti.kernel
def nu_where_scalar_rhs(
    cond: ti.types.ndarray(ti.i32, 1),
    x: ti.types.ndarray(ti.f32, 1),
    y_in: ti.types.ndarray(ti.f32, 1),
    out: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
):
    yv = y_in[0]
    for i in range(n):
        out[i] = x[i] if cond[i] != 0 else yv


@ti.kernel
def nu_where_scalar_lhs(
    cond: ti.types.ndarray(ti.i32, 1),
    x: ti.types.ndarray(ti.f32, 1),
    y_in: ti.types.ndarray(ti.f32, 1),
    out: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
):
    xv = x[0]
    for i in range(n):
        out[i] = xv if cond[i] != 0 else y_in[i]


# ---------------------------------------------------------------- casts


@ti.kernel
def nu_cast_f32_i32(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = ti.cast(x[i], ti.i32)


@ti.kernel
def nu_cast_f32_i64(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.i64, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = ti.cast(ti.cast(x[i], ti.i32), ti.i64)


@ti.kernel
def nu_cast_i32_f32(
    x: ti.types.ndarray(ti.i32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = ti.cast(x[i], ti.f32)


@ti.kernel
def nu_cast_i64_f32(
    x: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = ti.cast(x[i], ti.f32)


@ti.kernel
def nu_cast_i64_i32(
    x: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = ti.cast(x[i], ti.i32)


@ti.kernel
def nu_cast_i32_i64(
    x: ti.types.ndarray(ti.i32, 1),
    y: ti.types.ndarray(ti.i64, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = ti.cast(x[i], ti.i64)


@ti.kernel
def nu_copy_f32(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = x[i]


@ti.kernel
def nu_copy_i32(
    x: ti.types.ndarray(ti.i32, 1),
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = x[i]


@ti.kernel
def nu_copy_i64(
    x: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.i64, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = x[i]


ALL_ELEMENTWISE_KERNELS = [
    nu_unary_f32,
    nu_clip_f32,
    nu_binary_flat,
    nu_binary_scalar_rhs,
    nu_binary_scalar_lhs,
    nu_binary_broadcast,
    nu_binary_unary_broadcast,
    nu_add_sqrt_clip_broadcast,
    nu_sub_clip_sqrt_broadcast,
    nu_prelu,
    nu_binary_cmp_flat,
    nu_binary_cmp_scalar_rhs,
    nu_binary_cmp_scalar_lhs,
    nu_binary_cmp_broadcast,
    nu_and_i32,
    nu_or_i32,
        nu_xor_i32,
        nu_not_i32,
    nu_where_flat,
    nu_where_broadcast,
    nu_where_scalar_rhs,
    nu_where_scalar_lhs,
    nu_cast_f32_i32,
    nu_cast_f32_i64,
    nu_cast_i32_f32,
    nu_cast_i64_f32,
    nu_cast_i64_i32,
    nu_cast_i32_i64,
    nu_copy_f32,
    nu_copy_i32,
    nu_copy_i64,
]
