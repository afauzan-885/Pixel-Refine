"""Data movement universal kernels: gather, concat, slice, pad, transpose, tile,
space-to-depth, resize, and non-zero index extraction."""

import taichi as ti

MAX_RANK = 8


@ti.func
def _nth(v0: ti.i32, v1: ti.i32, v2: ti.i32, v3: ti.i32,
         v4: ti.i32, v5: ti.i32, v6: ti.i32, v7: ti.i32, axis: ti.i32) -> ti.i32:
    out = 1
    if axis == 0:
        out = v0
    elif axis == 1:
        out = v1
    elif axis == 2:
        out = v2
    elif axis == 3:
        out = v3
    elif axis == 4:
        out = v4
    elif axis == 5:
        out = v5
    elif axis == 6:
        out = v6
    elif axis == 7:
        out = v7
    return out


# --------------------------------------------------------------- gather


@ti.kernel
def nu_gather(
    data: ti.types.ndarray(ti.f32, 1),
    indices: ti.types.ndarray(ti.i32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    outer_size: ti.i32,
    indices_size: ti.i32,
    axis_dim: ti.i32,
    inner_size: ti.i32,
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
def nu_gather_elements(
    data: ti.types.ndarray(ti.f32, 1),
    indices: ti.types.ndarray(ti.i32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    outer_size: ti.i32,
    axis_dim_data: ti.i32,
    axis_dim_idx: ti.i32,
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
        y[idx] = data[(outer * axis_dim_data + src) * inner_size + inner]


# --------------------------------------------------------------- concat/split


@ti.kernel
def nu_concat2(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    outer_size: ti.i32,
    dim_a: ti.i32,
    dim_b: ti.i32,
    inner_size: ti.i32,
):
    total = dim_a + dim_b
    for idx in range(outer_size * total * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        a_pos = t % total
        outer = t // total
        if a_pos < dim_a:
            y[idx] = a[(outer * dim_a + a_pos) * inner_size + inner]
        else:
            y[idx] = b[(outer * dim_b + (a_pos - dim_a)) * inner_size + inner]


@ti.kernel
def nu_copy_concat_axis(
    src: ti.types.ndarray(ti.f32, 1),
    dst: ti.types.ndarray(ti.f32, 1),
    outer_size: ti.i32,
    src_axis_dim: ti.i32,
    dst_axis_dim: ti.i32,
    axis_offset: ti.i32,
    inner_size: ti.i32,
):
    for idx in range(outer_size * src_axis_dim * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        a = t % src_axis_dim
        outer = t // src_axis_dim
        dst[(outer * dst_axis_dim + axis_offset + a) * inner_size + inner] = (
            src[(outer * src_axis_dim + a) * inner_size + inner]
        )


@ti.kernel
def nu_copy_split_axis(
    src: ti.types.ndarray(ti.f32, 1),
    dst: ti.types.ndarray(ti.f32, 1),
    outer_size: ti.i32,
    src_axis_dim: ti.i32,
    dst_axis_dim: ti.i32,
    axis_offset: ti.i32,
    inner_size: ti.i32,
):
    for idx in range(outer_size * dst_axis_dim * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        a = t % dst_axis_dim
        outer = t // dst_axis_dim
        dst[(outer * dst_axis_dim + a) * inner_size + inner] = (
            src[(outer * src_axis_dim + axis_offset + a) * inner_size + inner]
        )


@ti.kernel
def nu_slice_axis(
    src: ti.types.ndarray(ti.f32, 1),
    dst: ti.types.ndarray(ti.f32, 1),
    outer_size: ti.i32,
    src_axis_dim: ti.i32,
    dst_axis_dim: ti.i32,
    start: ti.i32,
    step: ti.i32,
    inner_size: ti.i32,
):
    for idx in range(outer_size * dst_axis_dim * inner_size):
        inner = idx % inner_size
        t = idx // inner_size
        a = t % dst_axis_dim
        outer = t // dst_axis_dim
        src_pos = start + a * step
        dst[(outer * dst_axis_dim + a) * inner_size + inner] = (
            src[(outer * src_axis_dim + src_pos) * inner_size + inner]
        )


# --------------------------------------------------------------- pad


@ti.kernel
def nu_pad_4d_constant(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    nc: ti.i32,
    h_in: ti.i32,
    w_in: ti.i32,
    h_out: ti.i32,
    w_out: ti.i32,
    pad_top: ti.i32,
    pad_left: ti.i32,
    value: ti.f32,
):
    for idx in range(nc * h_out * w_out):
        w = idx % w_out
        t = idx // w_out
        h = t % h_out
        c = t // h_out
        ih = h - pad_top
        iw = w - pad_left
        if 0 <= ih < h_in and 0 <= iw < w_in:
            y[idx] = x[(c * h_in + ih) * w_in + iw]
        else:
            y[idx] = value


# --------------------------------------------------------------- transpose


@ti.kernel
def nu_transpose_general(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    total: ti.i32,
    d0: ti.i32, d1: ti.i32, d2: ti.i32, d3: ti.i32,
    d4: ti.i32, d5: ti.i32, d6: ti.i32, d7: ti.i32,
    s0: ti.i32, s1: ti.i32, s2: ti.i32, s3: ti.i32,
    s4: ti.i32, s5: ti.i32, s6: ti.i32, s7: ti.i32,
):
    for idx in range(total):
        rem = idx
        src = 0
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = _nth(d0, d1, d2, d3, d4, d5, d6, d7, d)
            coord = rem % dim
            rem = rem // dim
            src += coord * _nth(s0, s1, s2, s3, s4, s5, s6, s7, d)
        y[idx] = x[src]


# --------------------------------------------------------------- expand / tile


@ti.kernel
def nu_tile_general(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    total: ti.i32,
    d0: ti.i32, d1: ti.i32, d2: ti.i32, d3: ti.i32,
    d4: ti.i32, d5: ti.i32, d6: ti.i32, d7: ti.i32,
    i0: ti.i32, i1: ti.i32, i2: ti.i32, i3: ti.i32,
    i4: ti.i32, i5: ti.i32, i6: ti.i32, i7: ti.i32,
    t0: ti.i32, t1: ti.i32, t2: ti.i32, t3: ti.i32,
    t4: ti.i32, t5: ti.i32, t6: ti.i32, t7: ti.i32,
):
    """Out[d] = In[d % tile_dim] where tile_dim is the pre-tile input extent."""
    for idx in range(total):
        rem = idx
        src = 0
        stride = 1
        for d in ti.static(range(MAX_RANK - 1, -1, -1)):
            dim = _nth(d0, d1, d2, d3, d4, d5, d6, d7, d)
            coord = rem % dim
            rem = rem // dim
            inner_dim = _nth(i0, i1, i2, i3, i4, i5, i6, i7, d)
            src += (coord % inner_dim) * stride
            stride *= inner_dim
        y[idx] = x[src]


# --------------------------------------------------------------- space to depth


@ti.kernel
def nu_space_to_depth(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    channels: ti.i32,
    h: ti.i32,
    w: ti.i32,
    block: ti.i32,
):
    """ONNX layout: out channel = (row * block + col) * C + channel."""
    out_h = h // block
    out_w = w // block
    out_c = channels * block * block
    for idx in range(n_batch * out_c * out_h * out_w):
        ow = idx % out_w
        rem = idx // out_w
        oh = rem % out_h
        oc = (rem // out_h) % out_c
        n = rem // (out_h * out_c)
        c_in = oc % channels
        rem_c = oc // channels
        r = rem_c // block
        c = rem_c % block
        ih = oh * block + r
        iw = ow * block + c
        y[idx] = x[((n * channels + c_in) * h + ih) * w + iw]


@ti.kernel
def nu_depth_to_space(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    channels: ti.i32,
    h: ti.i32,
    w: ti.i32,
    block: ti.i32,
):
    in_c = channels // (block * block)
    for idx in range(n_batch * channels * h * w):
        iw = idx % w
        rem = idx // w
        ih = rem % h
        oc = (rem // h) % channels
        n = rem // (h * channels)
        c_in = oc % in_c
        rem_c = oc // in_c
        r = rem_c // block
        c = rem_c % block
        oh = ih * block + r
        ow = iw * block + c
        y[idx] = x[((n * in_c + c_in) * (h * block) + oh) * (w * block) + ow]




# --------------------------------------------------------------- resize
@ti.kernel
def nu_resize_2d(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    channels: ti.i32,
    h_in: ti.i32,
    w_in: ti.i32,
    h_out: ti.i32,
    w_out: ti.i32,
    scale_h: ti.f32,
    scale_w: ti.f32,
    mode: ti.i32,          # 0 linear, 1 nearest
    half_pixel: ti.i32,    # 0 asymmetric, 1 half_pixel, 2 align_corners
):
    for idx in range(n_batch * channels * h_out * w_out):
        ow = idx % w_out
        rem = idx // w_out
        oh = rem % h_out
        c = (rem // h_out) % channels
        n = rem // (h_out * channels)
        base = (n * channels + c) * h_in * w_in
        sy = ti.cast(oh, ti.f32) / scale_h
        sx = ti.cast(ow, ti.f32) / scale_w
        if half_pixel == 1:
            sy = (ti.cast(oh, ti.f32) + 0.5) / scale_h - 0.5
            sx = (ti.cast(ow, ti.f32) + 0.5) / scale_w - 0.5
        elif half_pixel == 2:
            if h_out > 1:
                sy = ti.cast(oh, ti.f32) * ti.cast(h_in - 1, ti.f32) / ti.cast(h_out - 1, ti.f32)
            if w_out > 1:
                sx = ti.cast(ow, ti.f32) * ti.cast(w_in - 1, ti.f32) / ti.cast(w_out - 1, ti.f32)
        if mode == 1:
            iy = ti.cast(ti.floor(sy + 0.5), ti.i32)
            ix = ti.cast(ti.floor(sx + 0.5), ti.i32)
            iy = ti.max(0, ti.min(h_in - 1, iy))
            ix = ti.max(0, ti.min(w_in - 1, ix))
            y[idx] = x[base + iy * w_in + ix]
        else:
            sy = ti.max(0.0, sy)
            sx = ti.max(0.0, sx)
            y0 = ti.min(ti.cast(ti.floor(sy), ti.i32), h_in - 1)
            x0 = ti.min(ti.cast(ti.floor(sx), ti.i32), w_in - 1)
            y1 = ti.min(y0 + 1, h_in - 1)
            x1 = ti.min(x0 + 1, w_in - 1)
            dy = sy - ti.cast(y0, ti.f32)
            dx = sx - ti.cast(x0, ti.f32)
            v00 = x[base + y0 * w_in + x0]
            v01 = x[base + y0 * w_in + x1]
            v10 = x[base + y1 * w_in + x0]
            v11 = x[base + y1 * w_in + x1]
            top = v00 * (1.0 - dx) + v01 * dx
            bottom = v10 * (1.0 - dx) + v11 * dx
            y[idx] = top * (1.0 - dy) + bottom * dy


# --------------------------------------------------------------- nonzero


@ti.kernel
def nu_nonzero_count(
    x: ti.types.ndarray(ti.f32, 1),
    counter: ti.types.ndarray(ti.i32, 1),
    total: ti.i32,
):
    for i in range(total):
        if x[i] != 0.0:
            ti.atomic_add(counter[0], 1)


@ti.kernel
def nu_nonzero_scatter(
    x: ti.types.ndarray(ti.f32, 1),
    out: ti.types.ndarray(ti.i32, 1),
    counter: ti.types.ndarray(ti.i32, 1),
    total: ti.i32,
    capacity: ti.i32,
    rank: ti.i32,
    d0: ti.i32, d1: ti.i32, d2: ti.i32, d3: ti.i32,
    d4: ti.i32, d5: ti.i32, d6: ti.i32, d7: ti.i32,
):
    """Scatter row-major coordinates into an ``[rank, capacity]`` buffer."""
    for i in range(total):
        if x[i] != 0.0:
            slot = ti.atomic_add(counter[0], 1)
            if slot < capacity:
                rem = i
                for d in ti.static(range(MAX_RANK - 1, -1, -1)):
                    if d < rank:
                        dim = _nth(d0, d1, d2, d3, d4, d5, d6, d7, d)
                        out[d * capacity + slot] = rem % dim
                        rem = rem // dim


@ti.kernel
def nu_iota_i32(
    y: ti.types.ndarray(ti.i32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = i


ALL_MOVEMENT_KERNELS = [
    nu_gather,
    nu_gather_elements,
    nu_concat2,
    nu_copy_concat_axis,
    nu_copy_split_axis,
    nu_slice_axis,
    nu_pad_4d_constant,
    nu_transpose_general,
        nu_tile_general,
    nu_space_to_depth,
    nu_depth_to_space,
    nu_resize_2d,
    nu_nonzero_count,
    nu_nonzero_scatter,
    nu_iota_i32,
]
