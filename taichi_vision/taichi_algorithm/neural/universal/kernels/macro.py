"""Fused-node universal kernels.

Each kernel here replaces a short chain of ONNX nodes that appears in the target
model families (WeightNet, RAFT, LightGlue). They exist because the fused form
removes one full read/write pass per replaced node.
"""

import taichi as ti

from .common import nu_stable_sigmoid


@ti.kernel
def nu_mul_clip(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    lo: ti.f32,
    hi: ti.f32,
):
    for i in range(n):
        y[i] = ti.max(lo, ti.min(hi, a[i] * b[i]))


@ti.kernel
def nu_mul_scalar_clip(
    a: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    b: ti.f32,
    lo: ti.f32,
    hi: ti.f32,
):
    for i in range(n):
        y[i] = ti.max(lo, ti.min(hi, a[i] * b))


@ti.kernel
def nu_sigmoid_mul_clip(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    lo: ti.f32,
    hi: ti.f32,
):
    for i in range(n):
        y[i] = ti.max(lo, ti.min(hi, nu_stable_sigmoid(a[i]) * b[i]))


@ti.kernel
def nu_add_relu(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
):
    for i in range(n):
        y[i] = ti.max(0.0, a[i] + b[i])


@ti.kernel
def nu_sub_square(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
):
    for i in range(n):
        d = a[i] - b[i]
        y[i] = d * d


@ti.kernel
def nu_pow2_sub_clip_sqrt(
    a: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    sub: ti.f32,
    lo: ti.f32,
):
    for i in range(n):
        v = a[i] * a[i] - sub
        y[i] = ti.sqrt(ti.max(lo, v))


@ti.kernel
def nu_mean_abs_clip(
    a: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
    lo: ti.f32,
    hi: ti.f32,
):
    total = 0.0
    for i in range(n):
        total += ti.abs(a[i])
    ti.atomic_add(y[0], ti.max(lo, ti.min(hi, total / ti.cast(n, ti.f32))))


@ti.kernel
def nu_gate_mix(
    h1: ti.types.ndarray(ti.f32, 1),
    h2: ti.types.ndarray(ti.f32, 1),
    gate: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n: ti.i32,
):
    """WeightNet head gate: ``y = h1 * s + h2 * (1 - s)`` with ``s = sigmoid(gate)``."""
    for i in range(n):
        s = nu_stable_sigmoid(gate[i])
        y[i] = h1[i] * s + h2[i] * (1.0 - s)


@ti.kernel
def nu_rms_pool_tanh(
    x: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    channels: ti.i32,
    h: ti.i32,
    ow: ti.i32,
):
    """WeightNet statistics head: 4-channel RMS over a 4x4 pool, summed, then tanh."""
    for idx in range(ow * ow):
        ox = idx % ow
        oy = idx // ow
        pool_total = 0.0
        for ky in ti.static(range(4)):
            for kx in ti.static(range(4)):
                iy = oy * 2 + ky
                ix = ox * 2 + kx
                channel_total = 0.0
                for channel in ti.static(range(4)):
                    if channel < channels:
                        value = x[(channel * h + iy) * h + ix]
                        channel_total += value * value
                pool_total += ti.sqrt(channel_total * 0.25)
        y[idx] = ti.tanh(pool_total * 0.5)


@ti.kernel
def nu_sep_conv_1x5(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    channels: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    pad_left: ti.i32,
):
    plane = h * w_in
    for idx in range(n_batch * channels * plane):
        p = idx % plane
        c = (idx // plane) % channels
        n = idx // (plane * channels)
        yy = p // w_in
        xx = p % w_in
        acc = 0.0
        for kx in ti.static(range(5)):
            ix = xx + kx - pad_left
            if 0 <= ix < w_in:
                acc += x[(n * channels + c) * plane + yy * w_in + ix] * w[c * 5 + kx]
        y[idx] = acc


@ti.kernel
def nu_sep_conv_5x1(
    x: ti.types.ndarray(ti.f32, 1),
    w: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    channels: ti.i32,
    h: ti.i32,
    w_in: ti.i32,
    pad_top: ti.i32,
):
    plane = h * w_in
    for idx in range(n_batch * channels * plane):
        p = idx % plane
        c = (idx // plane) % channels
        n = idx // (plane * channels)
        yy = p // w_in
        xx = p % w_in
        acc = 0.0
        for ky in ti.static(range(5)):
            iy = yy + ky - pad_top
            if 0 <= iy < h:
                acc += x[(n * channels + c) * plane + iy * w_in + xx] * w[c * 5 + ky]
        y[idx] = acc


ALL_MACRO_KERNELS = [
    nu_mul_clip,
    nu_mul_scalar_clip,
    nu_sigmoid_mul_clip,
    nu_add_relu,
    nu_sub_square,
    nu_pow2_sub_clip_sqrt,
    nu_mean_abs_clip,
    nu_gate_mix,
    nu_rms_pool_tanh,
    nu_sep_conv_1x5,
    nu_sep_conv_5x1,
]