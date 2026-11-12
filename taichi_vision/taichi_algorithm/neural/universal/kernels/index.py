"""Index and generation universal kernels: range, fill, top-k, prefix helpers."""

import taichi as ti


@ti.kernel
def nu_fill_f32(
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    value: ti.f32,
):
    for i in range(n):
        y[i] = value


@ti.kernel
def nu_fill_i32(
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
    value: ti.i32,
):
    for i in range(n):
        y[i] = value


@ti.kernel
def nu_fill_i64(
    y: ti.types.ndarray(ti.i64, 1),
    n: ti.i32,
    value: ti.i64,
):
    for i in range(n):
        y[i] = value


@ti.kernel
def nu_range_f32(
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    start: ti.f32,
    delta: ti.f32,
):
    for i in range(n):
        y[i] = start + ti.cast(i, ti.f32) * delta


@ti.kernel
def nu_range_i32(
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
    start: ti.i32,
    delta: ti.i32,
):
    for i in range(n):
        y[i] = start + i * delta


@ti.kernel
def nu_range_i64(
    y: ti.types.ndarray(ti.i64, 1),
    n: ti.i32,
    start: ti.i64,
    delta: ti.i64,
):
    for i in range(n):
        y[i] = start + ti.cast(i, ti.i64) * delta


@ti.kernel
def nu_topk_last(
    x: ti.types.ndarray(ti.f32, 1),
    values: ti.types.ndarray(ti.f32, 1),
    indices: ti.types.ndarray(ti.i32, 1),
    taken: ti.types.ndarray(ti.i32, 1),
    rows: ti.i32,
    cols: ti.i32,
    k: ti.i32,
    largest: ti.i32,
):
    """Exact top-k over the last axis using k selection passes.

    ``taken`` is a per-row scratch of length ``cols`` reused between rows; only
    one thread owns a row, so the scratch is not shared concurrently.
    """
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
            indices[r * k + j] = best_i
            if best_i >= 0:
                taken[best_i] = 1


@ti.kernel
def nu_gather_axis0_i32(
    src: ti.types.ndarray(ti.i32, 1),
    indices: ti.types.ndarray(ti.i32, 1),
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = src[indices[i]]


ALL_INDEX_KERNELS = [
    nu_fill_f32,
    nu_fill_i32,
    nu_fill_i64,
    nu_range_f32,
    nu_range_i32,
    nu_range_i64,
    nu_topk_last,
    nu_gather_axis0_i32,
]