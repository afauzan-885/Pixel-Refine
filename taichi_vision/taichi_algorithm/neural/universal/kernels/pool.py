"""Pooling universal kernels."""

import taichi as ti


@ti.kernel
def nu_average_pool2d(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    channels: ti.i32,
    h: ti.i32,
    w: ti.i32,
    oh: ti.i32,
    ow: ti.i32,
    kh: ti.i32,
    kw: ti.i32,
    sh: ti.i32,
    sw: ti.i32,
    ph: ti.i32,
    pw: ti.i32,
    count_include_pad: ti.i32,
):
    for idx in range(n_batch * channels * oh * ow):
        ox = idx % ow
        t = idx // ow
        oy = t % oh
        c = (t // oh) % channels
        n = t // (oh * channels)
        base = (n * channels + c) * h * w
        acc = 0.0
        valid = 0
        for ky in range(kh):
            iy = oy * sh + ky - ph
            if 0 <= iy < h:
                for kx in range(kw):
                    ix = ox * sw + kx - pw
                    if 0 <= ix < w:
                        acc += x[base + iy * w + ix]
                        valid += 1
        if count_include_pad != 0:
            y[idx] = acc / ti.cast(kh * kw, ti.f32)
        else:
            y[idx] = acc / ti.cast(ti.max(valid, 1), ti.f32)


@ti.kernel
def nu_max_pool2d(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    channels: ti.i32,
    h: ti.i32,
    w: ti.i32,
    oh: ti.i32,
    ow: ti.i32,
    kh: ti.i32,
    kw: ti.i32,
    sh: ti.i32,
    sw: ti.i32,
    ph: ti.i32,
    pw: ti.i32,
    dh: ti.i32,
    dw: ti.i32,
):
    for idx in range(n_batch * channels * oh * ow):
        ox = idx % ow
        t = idx // ow
        oy = t % oh
        c = (t // oh) % channels
        n = t // (oh * channels)
        base = (n * channels + c) * h * w
        acc = -3.4028234663852886e38
        for ky in range(kh):
            iy = oy * sh + ky * dh - ph
            if 0 <= iy < h:
                for kx in range(kw):
                    ix = ox * sw + kx * dw - pw
                    if 0 <= ix < w:
                        acc = ti.max(acc, x[base + iy * w + ix])
        y[idx] = acc


@ti.kernel
def nu_global_average_pool2d(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    channels: ti.i32,
    spatial: ti.i32,
):
    inv = 1.0 / ti.cast(spatial, ti.f32)
    for nc in range(n_batch * channels):
        acc = 0.0
        base = nc * spatial
        for s in range(spatial):
            acc += x[base + s]
        y[nc] = acc * inv


ALL_POOL_KERNELS = [
    nu_average_pool2d,
    nu_max_pool2d,
    nu_global_average_pool2d,
]