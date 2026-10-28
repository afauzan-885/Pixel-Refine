"""CPU candidate movement kernels for dynamic INT64 values."""

import taichi as ti

from .movement import _nth


@ti.kernel
def nu_transpose_general_i64_candidate(
    x: ti.types.ndarray(ti.i64, 1), y: ti.types.ndarray(ti.i64, 1), total: ti.i32,
    d0: ti.i32, d1: ti.i32, d2: ti.i32, d3: ti.i32,
    d4: ti.i32, d5: ti.i32, d6: ti.i32, d7: ti.i32,
    s0: ti.i32, s1: ti.i32, s2: ti.i32, s3: ti.i32,
    s4: ti.i32, s5: ti.i32, s6: ti.i32, s7: ti.i32,
):
    for idx in range(total):
        rem, src = idx, 0
        for d in ti.static(range(7, -1, -1)):
            dim = _nth(d0, d1, d2, d3, d4, d5, d6, d7, d)
            coord = rem % dim
            rem = rem // dim
            src += coord * _nth(s0, s1, s2, s3, s4, s5, s6, s7, d)
        y[idx] = x[src]


@ti.kernel
def nu_slice_axis_i64_candidate(
    src: ti.types.ndarray(ti.i64, 1), dst: ti.types.ndarray(ti.i64, 1),
    outer_size: ti.i32, src_axis_dim: ti.i32, dst_axis_dim: ti.i32,
    start: ti.i32, step: ti.i32, inner_size: ti.i32,
):
    for idx in range(outer_size * dst_axis_dim * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        a = t % dst_axis_dim
        outer = t // dst_axis_dim
        src_pos = start + a * step
        dst[idx] = src[(outer * src_axis_dim + src_pos) * inner_size + inner]


@ti.kernel
def nu_concat2_i64_candidate(
    a: ti.types.ndarray(ti.i64, 1), b: ti.types.ndarray(ti.i64, 1),
    y: ti.types.ndarray(ti.i64, 1), outer_size: ti.i32, dim_a: ti.i32,
    dim_b: ti.i32, inner_size: ti.i32,
):
    total = dim_a + dim_b
    for idx in range(outer_size * total * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        pos = t % total
        outer = t // total
        if pos < dim_a:
            y[idx] = a[(outer * dim_a + pos) * inner_size + inner]
        else:
            y[idx] = b[(outer * dim_b + pos - dim_a) * inner_size + inner]


@ti.kernel
def nu_copy_concat_axis_i64_candidate(
    src: ti.types.ndarray(ti.i64, 1), dst: ti.types.ndarray(ti.i64, 1),
    outer_size: ti.i32, src_axis_dim: ti.i32, dst_axis_dim: ti.i32,
    axis_offset: ti.i32, inner_size: ti.i32,
):
    for idx in range(outer_size * src_axis_dim * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        a = t % src_axis_dim
        outer = t // src_axis_dim
        dst[(outer * dst_axis_dim + axis_offset + a) * inner_size + inner] = src[idx]


@ti.kernel
def nu_copy_split_axis_i64_candidate(
    src: ti.types.ndarray(ti.i64, 1), dst: ti.types.ndarray(ti.i64, 1),
    outer_size: ti.i32, src_axis_dim: ti.i32, dst_axis_dim: ti.i32,
    axis_offset: ti.i32, inner_size: ti.i32,
):
    for idx in range(outer_size * dst_axis_dim * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        a = t % dst_axis_dim
        outer = t // dst_axis_dim
        dst[idx] = src[(outer * src_axis_dim + axis_offset + a) * inner_size + inner]


@ti.kernel
def nu_nonzero_scatter_serial_i64_candidate(
    x: ti.types.ndarray(ti.f32, 1), out: ti.types.ndarray(ti.i64, 1),
    counter: ti.types.ndarray(ti.i32, 1), total: ti.i32, capacity: ti.i32,
    rank: ti.i32,
    d0: ti.i32, d1: ti.i32, d2: ti.i32, d3: ti.i32,
    d4: ti.i32, d5: ti.i32, d6: ti.i32, d7: ti.i32,
):
    """Deterministic row-major scatter; isolated CPU candidate for AOT atomic bug."""
    slot = 0
    ti.loop_config(serialize=True)
    for i in range(total):
        if x[i] != 0.0:
            if slot < capacity:
                rem = i
                for d in ti.static(range(7, -1, -1)):
                    if d >= 8 - rank:
                        dim = _nth(d0, d1, d2, d3, d4, d5, d6, d7, d)
                        axis = d - (8 - rank)
                        out[axis * capacity + slot] = rem % dim
                        rem = rem // dim
            slot += 1
    counter[0] = slot


@ti.kernel
def nu_nonzero_scatter_serial_i32_i64_candidate(
    x: ti.types.ndarray(ti.i32, 1), out: ti.types.ndarray(ti.i64, 1),
    counter: ti.types.ndarray(ti.i32, 1), total: ti.i32, capacity: ti.i32,
    rank: ti.i32,
    d0: ti.i32, d1: ti.i32, d2: ti.i32, d3: ti.i32,
    d4: ti.i32, d5: ti.i32, d6: ti.i32, d7: ti.i32,
):
    """Deterministic row-major scatter for ONNX bool/I32 masks to I64 coords."""
    slot = 0
    ti.loop_config(serialize=True)
    for i in range(total):
        if x[i] != 0:
            if slot < capacity:
                rem = i
                for d in ti.static(range(7, -1, -1)):
                    if d >= 8 - rank:
                        dim = _nth(d0, d1, d2, d3, d4, d5, d6, d7, d)
                        axis = d - (8 - rank)
                        out[axis * capacity + slot] = rem % dim
                        rem = rem // dim
            slot += 1
    counter[0] = slot


ALL_I64_MOVEMENT_CANDIDATE_KERNELS = [
    nu_transpose_general_i64_candidate,
    nu_slice_axis_i64_candidate,
    nu_concat2_i64_candidate,
    nu_copy_concat_axis_i64_candidate,
    nu_copy_split_axis_i64_candidate,
    nu_nonzero_scatter_serial_i64_candidate,
    nu_nonzero_scatter_serial_i32_i64_candidate,
]
