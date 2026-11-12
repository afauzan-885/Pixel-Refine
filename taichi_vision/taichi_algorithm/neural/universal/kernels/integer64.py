"""Experimental CPU-only ONNX int64 data-plane kernels.

These kernels are compiled only into isolated candidate pools. The default
universal pool deliberately does not register them.
"""

import taichi as ti
from .common import MAX_RANK, nu_pad_list


@ti.func
def _nu_i64_apply(a, b, code: ti.i32, fmod: ti.i32,
                  status: ti.types.ndarray(ti.i32, 1)) -> ti.i64:
    result = ti.cast(0, ti.i64)
    if code == 0:
        result = a + b
    elif code == 1:
        result = a - b
    elif code == 2:
        result = a * b
    elif code == 3:
        if b == 0:
            ti.atomic_or(status[0], 1)
        elif b == -1:
            result = 0
        else:
            result = a % b
            if result != 0 and ((result < 0) != (b < 0)):
                result += b
            if fmod != 0 and result != 0 and ((result < 0) != (a < 0)):
                result -= b
    elif code == 4:
        if b == 0:
            ti.atomic_or(status[0], 1)
        elif b == -1 and ti.cast(a, ti.u64) == ti.u64(0x8000000000000000):
            ti.atomic_or(status[0], 2)
        else:
            result = a // b
            remainder = a % b
            if remainder != 0 and ((a < 0) != (b < 0)):
                result += 1
    return result


@ti.kernel
def nu_i64_binary_flat(
    a: ti.types.ndarray(ti.i64, 1), b: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.i64, 1), n: ti.i32, code: ti.i32,
    fmod: ti.i32, status: ti.types.ndarray(ti.i32, 1),
):
    """code: 0 Add, 1 Sub, 2 Mul, 3 Mod, 4 Div. Mod matches ONNX fmod."""
    for i in range(n):
        av, bv = a[i], b[i]
        if code == 0:
            y[i] = av + bv
        elif code == 1:
            y[i] = av - bv
        elif code == 2:
            y[i] = av * bv
        elif code == 4 and bv == 0:
            y[i] = 0
            ti.atomic_or(status[0], 1)
        elif code == 4 and bv == -1 and ti.cast(av, ti.u64) == ti.u64(0x8000000000000000):
            y[i] = 0
            ti.atomic_or(status[0], 2)
        elif code == 4:
            quotient = av // bv
            remainder = av % bv
            if remainder != 0 and ((av < 0) != (bv < 0)):
                quotient += 1
            y[i] = quotient
        elif bv == 0:
            y[i] = 0
            ti.atomic_or(status[0], 1)
        elif fmod != 0:
            # Truncating remainder (ONNX fmod=1); signed-min / -1 is defined
            # as zero for the remainder, without evaluating an overflowing div.
            if bv == -1:
                y[i] = 0
            else:
                y[i] = av % bv
                if y[i] != 0 and ((y[i] < 0) != (av < 0)):
                    y[i] = y[i] - bv
        else:
            # Floor modulo: result has divisor's sign. Avoid min/-1 overflow.
            if bv == -1:
                y[i] = 0
            else:
                y[i] = av % bv
                if y[i] != 0 and ((y[i] < 0) != (bv < 0)):
                    y[i] = y[i] + bv


@ti.kernel
def nu_i64_binary_scalar_rhs(
    a: ti.types.ndarray(ti.i64, 1), b: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.i64, 1), n: ti.i32, code: ti.i32,
    fmod: ti.i32, status: ti.types.ndarray(ti.i32, 1),
):
    bv = b[0]
    for i in range(n):
        av = a[i]
        if code == 0:
            y[i] = av + bv
        elif code == 1:
            y[i] = av - bv
        elif code == 2:
            y[i] = av * bv
        elif code == 4 and bv == 0:
            y[i] = 0
            ti.atomic_or(status[0], 1)
        elif code == 4 and bv == -1 and ti.cast(av, ti.u64) == ti.u64(0x8000000000000000):
            y[i] = 0
            ti.atomic_or(status[0], 2)
        elif code == 4:
            quotient = av // bv
            remainder = av % bv
            if remainder != 0 and ((av < 0) != (bv < 0)):
                quotient += 1
            y[i] = quotient
        elif bv == 0:
            y[i] = 0
            ti.atomic_or(status[0], 1)
        elif bv == -1:
            y[i] = 0
        else:
            rem = av % bv
            if rem != 0:
                if fmod == 0 and ((rem < 0) != (bv < 0)):
                    rem += bv
                elif fmod != 0 and ((rem < 0) != (av < 0)):
                    rem -= bv
            y[i] = rem


@ti.kernel
def nu_i64_cmp_flat(
    a: ti.types.ndarray(ti.i64, 1), b: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.i32, 1), n: ti.i32, code: ti.i32,
):
    for i in range(n):
        if code == 0:
            y[i] = 1 if a[i] < b[i] else 0
        elif code == 1:
            y[i] = 1 if a[i] > b[i] else 0
        else:
            y[i] = 1 if a[i] == b[i] else 0


@ti.kernel
def nu_i64_cmp_broadcast_candidate(
    a: ti.types.ndarray(ti.i64, 1), b: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.i32, 1), n: ti.i32, code: ti.i32,
    o0: ti.i32, o1: ti.i32, o2: ti.i32, o3: ti.i32,
    o4: ti.i32, o5: ti.i32, o6: ti.i32, o7: ti.i32,
    a0: ti.i32, a1: ti.i32, a2: ti.i32, a3: ti.i32,
    a4: ti.i32, a5: ti.i32, a6: ti.i32, a7: ti.i32,
    b0: ti.i32, b1: ti.i32, b2: ti.i32, b3: ti.i32,
    b4: ti.i32, b5: ti.i32, b6: ti.i32, b7: ti.i32,
):
    for i in range(n):
        rem = i
        ai, bi = 0, 0
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = nu_pad_list(o0, o1, o2, o3, o4, o5, o6, o7, d)
            coord = rem % dim
            rem = rem // dim
            ai += coord * nu_pad_list(a0, a1, a2, a3, a4, a5, a6, a7, d)
            bi += coord * nu_pad_list(b0, b1, b2, b3, b4, b5, b6, b7, d)
        if code == 0:
            y[i] = 1 if a[ai] < b[bi] else 0
        elif code == 1:
            y[i] = 1 if a[ai] > b[bi] else 0
        else:
            y[i] = 1 if a[ai] == b[bi] else 0


@ti.kernel
def nu_i64_binary_broadcast_candidate(
    a: ti.types.ndarray(ti.i64, 1), b: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.i64, 1), n: ti.i32, code: ti.i32, fmod: ti.i32,
    status: ti.types.ndarray(ti.i32, 1),
    o0: ti.i32, o1: ti.i32, o2: ti.i32, o3: ti.i32,
    o4: ti.i32, o5: ti.i32, o6: ti.i32, o7: ti.i32,
    a0: ti.i32, a1: ti.i32, a2: ti.i32, a3: ti.i32,
    a4: ti.i32, a5: ti.i32, a6: ti.i32, a7: ti.i32,
    b0: ti.i32, b1: ti.i32, b2: ti.i32, b3: ti.i32,
    b4: ti.i32, b5: ti.i32, b6: ti.i32, b7: ti.i32,
):
    for i in range(n):
        rem = i
        ai, bi = 0, 0
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = nu_pad_list(o0, o1, o2, o3, o4, o5, o6, o7, d)
            coord = rem % dim
            rem = rem // dim
            ai += coord * nu_pad_list(a0, a1, a2, a3, a4, a5, a6, a7, d)
            bi += coord * nu_pad_list(b0, b1, b2, b3, b4, b5, b6, b7, d)
        y[i] = _nu_i64_apply(a[ai], b[bi], code, fmod, status)


@ti.kernel
def nu_where_i64_flat(
    cond: ti.types.ndarray(ti.i32, 1), x: ti.types.ndarray(ti.i64, 1),
    other: ti.types.ndarray(ti.i64, 1), out: ti.types.ndarray(ti.i64, 1),
    n: ti.i32,
):
    for i in range(n):
        out[i] = x[i] if cond[i] != 0 else other[i]


@ti.kernel
def nu_where_i64_broadcast_candidate(
    cond: ti.types.ndarray(ti.i32, 1), x: ti.types.ndarray(ti.i64, 1),
    other: ti.types.ndarray(ti.i64, 1), out: ti.types.ndarray(ti.i64, 1), n: ti.i32,
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
        ci, xi, yi = 0, 0, 0
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = nu_pad_list(o0, o1, o2, o3, o4, o5, o6, o7, d)
            coord = rem % dim
            rem = rem // dim
            ci += coord * nu_pad_list(c0, c1, c2, c3, c4, c5, c6, c7, d)
            xi += coord * nu_pad_list(x0, x1, x2, x3, x4, x5, x6, x7, d)
            yi += coord * nu_pad_list(y0, y1, y2, y3, y4, y5, y6, y7, d)
        out[i] = x[xi] if cond[ci] != 0 else other[yi]


@ti.kernel
def nu_copy_i64_candidate(
    x: ti.types.ndarray(ti.i64, 1), y: ti.types.ndarray(ti.i64, 1), n: ti.i32,
):
    for i in range(n):
        y[i] = x[i]


@ti.kernel
def nu_gather_i64_candidate(
    data: ti.types.ndarray(ti.i64, 1), indices: ti.types.ndarray(ti.i32, 1),
    y: ti.types.ndarray(ti.i64, 1), outer_size: ti.i32, indices_size: ti.i32,
    axis_dim: ti.i32, inner_size: ti.i32,
):
    for idx in range(outer_size * indices_size * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        ii = t % indices_size
        outer = t // indices_size
        src = indices[ii]
        if src < 0:
            src += axis_dim
        y[idx] = data[(outer * axis_dim + src) * inner_size + inner]


@ti.kernel
def nu_gather_elements_i64_indices_candidate(
    data: ti.types.ndarray(ti.f32, 1), indices: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.f32, 1), status: ti.types.ndarray(ti.i32, 1),
    outer_size: ti.i32, axis_dim_data: ti.i32, axis_dim_idx: ti.i32,
    inner_size: ti.i32,
):
    for idx in range(outer_size * axis_dim_idx * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        a = t % axis_dim_idx
        outer = t // axis_dim_idx
        src = indices[(outer * axis_dim_idx + a) * inner_size + inner]
        if src < 0:
            src += axis_dim_data
        if src < 0 or src >= axis_dim_data:
            y[idx] = 0.0
            ti.atomic_or(status[0], 1)
        else:
            y[idx] = data[(outer * axis_dim_data + ti.cast(src, ti.i32)) * inner_size + inner]


@ti.kernel
def nu_gather_elements_i64_data_i64_indices_candidate(
    data: ti.types.ndarray(ti.i64, 1), indices: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.i64, 1), status: ti.types.ndarray(ti.i32, 1),
    outer_size: ti.i32, axis_dim_data: ti.i32, axis_dim_idx: ti.i32,
    inner_size: ti.i32,
):
    for idx in range(outer_size * axis_dim_idx * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        a = t % axis_dim_idx
        outer = t // axis_dim_idx
        src = indices[(outer * axis_dim_idx + a) * inner_size + inner]
        if src < 0:
            src += axis_dim_data
        if src < 0 or src >= axis_dim_data:
            y[idx] = 0
            ti.atomic_or(status[0], 1)
        else:
            y[idx] = data[(outer * axis_dim_data + ti.cast(src, ti.i32)) * inner_size + inner]


@ti.kernel
def nu_gather_i64_indices_f32_candidate(
    data: ti.types.ndarray(ti.f32, 1), indices: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.f32, 1), status: ti.types.ndarray(ti.i32, 1),
    outer_size: ti.i32, indices_size: ti.i32, axis_dim: ti.i32, inner_size: ti.i32,
):
    for idx in range(outer_size * indices_size * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        ii = t % indices_size
        outer = t // indices_size
        src = indices[ii]
        if src < 0:
            src += axis_dim
        if src < 0 or src >= axis_dim:
            y[idx] = 0.0
            ti.atomic_or(status[0], 1)
        else:
            y[idx] = data[(outer * axis_dim + ti.cast(src, ti.i32)) * inner_size + inner]


@ti.kernel
def nu_gather_i64_indices_i64_candidate(
    data: ti.types.ndarray(ti.i64, 1), indices: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.i64, 1), status: ti.types.ndarray(ti.i32, 1),
    outer_size: ti.i32, indices_size: ti.i32, axis_dim: ti.i32, inner_size: ti.i32,
):
    for idx in range(outer_size * indices_size * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        ii = t % indices_size
        outer = t // indices_size
        src = indices[ii]
        if src < 0:
            src += axis_dim
        if src < 0 or src >= axis_dim:
            y[idx] = 0
            ti.atomic_or(status[0], 1)
        else:
            y[idx] = data[(outer * axis_dim + ti.cast(src, ti.i32)) * inner_size + inner]


@ti.kernel
def nu_topk_last_i64_indices_candidate(
    x: ti.types.ndarray(ti.f32, 1), values: ti.types.ndarray(ti.f32, 1),
    indices: ti.types.ndarray(ti.i64, 1), taken: ti.types.ndarray(ti.i32, 1),
    rows: ti.i32, cols: ti.i32, k: ti.i32, largest: ti.i32,
):
    """TopK values plus ONNX INT64 indices, matching the pool's stable scan."""
    for r in range(rows):
        for c in range(cols):
            taken[c] = 0
        row_base = r * cols
        for j in range(k):
            best = 0.0
            best_i = -1
            for c in range(cols):
                if taken[c] == 0:
                    v = x[row_base + c]
                    if best_i < 0:
                        best = v
                        best_i = c
                    elif largest != 0:
                        if v > best:
                            best = v
                            best_i = c
                    else:
                        if v < best:
                            best = v
                            best_i = c
            values[r * k + j] = best
            indices[r * k + j] = ti.cast(best_i, ti.i64)
            if best_i >= 0:
                taken[best_i] = 1


@ti.kernel
def nu_topk_axis_i64_indices_candidate(
    x: ti.types.ndarray(ti.f32, 1), values: ti.types.ndarray(ti.f32, 1),
    indices: ti.types.ndarray(ti.i64, 1), taken: ti.types.ndarray(ti.i32, 1),
    outer_size: ti.i32, axis_dim: ti.i32, inner_size: ti.i32,
    k: ti.i32, largest: ti.i32,
):
    """TopK over any axis, output values and ONNX INT64 axis indices."""
    rows = outer_size * inner_size
    for row in range(rows):
        for c in range(axis_dim):
            taken[row * axis_dim + c] = 0
        outer = row // inner_size
        inner = row % inner_size
        for j in range(k):
            best = 0.0
            best_i = -1
            for c in range(axis_dim):
                if taken[row * axis_dim + c] == 0:
                    v = x[(outer * axis_dim + c) * inner_size + inner]
                    if best_i < 0:
                        best, best_i = v, c
                    elif largest != 0:
                        if v > best:
                            best, best_i = v, c
                    else:
                        if v < best:
                            best, best_i = v, c
            values[(outer * k + j) * inner_size + inner] = best
            indices[(outer * k + j) * inner_size + inner] = ti.cast(best_i, ti.i64)
            if best_i >= 0:
                taken[row * axis_dim + best_i] = 1


ALL_I64_CANDIDATE_KERNELS = [
    nu_i64_binary_flat,
    nu_i64_binary_scalar_rhs,
    nu_i64_cmp_flat,
    nu_i64_cmp_broadcast_candidate,
    nu_i64_binary_broadcast_candidate,
    nu_where_i64_flat,
    nu_where_i64_broadcast_candidate,
    nu_copy_i64_candidate,
    nu_gather_i64_candidate,
    nu_gather_elements_i64_indices_candidate,
    nu_gather_elements_i64_data_i64_indices_candidate,
    nu_gather_i64_indices_f32_candidate,
    nu_gather_i64_indices_i64_candidate,
    nu_topk_last_i64_indices_candidate,
    nu_topk_axis_i64_indices_candidate,
]
