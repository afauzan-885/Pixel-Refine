"""Reduction universal kernels over an arbitrary single axis."""

import taichi as ti

@ti.kernel
def nu_reduce_sum(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    outer_size: ti.i32,
    axis_dim: ti.i32,
    inner_size: ti.i32,
):
    """Kahan-compensated sum.

    A plain sequential float32 accumulation over a long axis drifts far from
    the reference implementation (which sums in blocks); compensation keeps the
    relative error near one ulp regardless of ``axis_dim``.
    """
    for idx in range(outer_size * inner_size):
        inner = idx % inner_size
        outer = idx // inner_size
        acc = 0.0
        comp = 0.0
        base = outer * axis_dim * inner_size + inner
        for a in range(axis_dim):
            value = x[base + a * inner_size]
            corrected = value - comp
            total = acc + corrected
            comp = (total - acc) - corrected
            acc = total
        y[idx] = acc


@ti.kernel
def nu_reduce_mean(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    outer_size: ti.i32,
    axis_dim: ti.i32,
    inner_size: ti.i32,
):
    """Kahan-compensated mean; see :func:`nu_reduce_sum` for the rationale."""
    inv = 1.0 / ti.cast(axis_dim, ti.f32)
    for idx in range(outer_size * inner_size):
        inner = idx % inner_size
        outer = idx // inner_size
        acc = 0.0
        comp = 0.0
        base = outer * axis_dim * inner_size + inner
        for a in range(axis_dim):
            value = x[base + a * inner_size]
            corrected = value - comp
            total = acc + corrected
            comp = (total - acc) - corrected
            acc = total
        y[idx] = acc * inv
@ti.kernel
def nu_reduce_max(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    outer_size: ti.i32,
    axis_dim: ti.i32,
    inner_size: ti.i32,
):
    for idx in range(outer_size * inner_size):
        inner = idx % inner_size
        outer = idx // inner_size
        base = outer * axis_dim * inner_size + inner
        acc = x[base]
        for a in range(1, axis_dim):
            acc = ti.max(acc, x[base + a * inner_size])
        y[idx] = acc


@ti.kernel
def nu_reduce_min(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    outer_size: ti.i32,
    axis_dim: ti.i32,
    inner_size: ti.i32,
):
    for idx in range(outer_size * inner_size):
        inner = idx % inner_size
        outer = idx // inner_size
        base = outer * axis_dim * inner_size + inner
        acc = x[base]
        for a in range(1, axis_dim):
            acc = ti.min(acc, x[base + a * inner_size])
        y[idx] = acc


@ti.kernel
def nu_reduce_l2(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    outer_size: ti.i32,
    axis_dim: ti.i32,
    inner_size: ti.i32,
):
    for idx in range(outer_size * inner_size):
        inner = idx % inner_size
        outer = idx // inner_size
        acc = 0.0
        base = outer * axis_dim * inner_size + inner
        for a in range(axis_dim):
            v = x[base + a * inner_size]
            acc += v * v
        y[idx] = ti.sqrt(acc)


@ti.kernel
def nu_zero_f32(
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = 0.0


@ti.kernel
def nu_reduce_all_sum(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    total: ti.i32,
):
    """Full reduction. ``y[0]`` must be zeroed first; accumulation is atomic."""
    acc = 0.0
    for i in range(total):
        acc += x[i]
    ti.atomic_add(y[0], acc)


@ti.kernel
def nu_reduce_all_mean(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    total: ti.i32,
):
    acc = 0.0
    for i in range(total):
        acc += x[i]
    ti.atomic_add(y[0], acc / ti.cast(total, ti.f32))


@ti.kernel
def nu_argmax_last(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.i32, 1),
    rows: ti.i32,
    cols: ti.i32,
):
    for r in range(rows):
        best = x[r * cols]
        best_i = 0
        for c in range(1, cols):
            v = x[r * cols + c]
            if v > best:
                best = v
                best_i = c
        y[r] = best_i


ALL_REDUCE_KERNELS = [
    nu_reduce_sum,
    nu_reduce_mean,
    nu_reduce_max,
    nu_reduce_min,
    nu_reduce_l2,
    nu_zero_f32,
    nu_reduce_all_sum,
    nu_reduce_all_mean,
    nu_argmax_last,
]
