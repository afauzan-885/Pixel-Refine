"""Normalization universal kernels: instance, layer, softmax, log-softmax."""

import taichi as ti

from .common import nu_activate


@ti.kernel
def nu_instance_norm(
    x: ti.types.ndarray(ti.f32, 1),
    scale: ti.types.ndarray(ti.f32, 1),
    bias: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    channels: ti.i32,
    spatial: ti.i32,
    eps: ti.f32,
    has_scale: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    inv = 1.0 / ti.cast(spatial, ti.f32)
    for idx in range(n_batch * channels):
        c = idx % channels
        base = idx * spatial
        acc = 0.0
        for s in range(spatial):
            acc += x[base + s]
        mean = acc * inv
        acc2 = 0.0
        for s in range(spatial):
            d = x[base + s] - mean
            acc2 += d * d
        inv_std = 1.0 / ti.sqrt(acc2 * inv + eps)
        s_scale = scale[c] if has_scale != 0 else 1.0
        s_bias = bias[c] if has_bias != 0 else 0.0
        for s in range(spatial):
            y[base + s] = nu_activate((x[base + s] - mean) * inv_std * s_scale + s_bias, act)


@ti.kernel
def nu_layer_norm(
    x: ti.types.ndarray(ti.f32, 1),
    scale: ti.types.ndarray(ti.f32, 1),
    bias: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    outer_size: ti.i32,
    axis_dim: ti.i32,
    eps: ti.f32,
    has_scale: ti.i32,
    has_bias: ti.i32,
    act: ti.i32,
):
    inv = 1.0 / ti.cast(axis_dim, ti.f32)
    for o in range(outer_size):
        base = o * axis_dim
        acc = 0.0
        for i in range(axis_dim):
            acc += x[base + i]
        mean = acc * inv
        acc2 = 0.0
        for i in range(axis_dim):
            d = x[base + i] - mean
            acc2 += d * d
        inv_std = 1.0 / ti.sqrt(acc2 * inv + eps)
        for i in range(axis_dim):
            s_scale = scale[i] if has_scale != 0 else 1.0
            s_bias = bias[i] if has_bias != 0 else 0.0
            y[base + i] = nu_activate((x[base + i] - mean) * inv_std * s_scale + s_bias, act)


@ti.kernel
def nu_softmax(
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
        peak = x[base]
        for a in range(1, axis_dim):
            peak = ti.max(peak, x[base + a * inner_size])
        total = 0.0
        for a in range(axis_dim):
            total += ti.exp(x[base + a * inner_size] - peak)
        inv = 1.0 / total
        for a in range(axis_dim):
            y[base + a * inner_size] = ti.exp(x[base + a * inner_size] - peak) * inv


@ti.kernel
def nu_log_softmax(
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
        peak = x[base]
        for a in range(1, axis_dim):
            peak = ti.max(peak, x[base + a * inner_size])
        total = 0.0
        for a in range(axis_dim):
            total += ti.exp(x[base + a * inner_size] - peak)
        log_total = ti.log(total)
        for a in range(axis_dim):
            y[base + a * inner_size] = x[base + a * inner_size] - peak - log_total


@ti.kernel
def nu_batch_norm(
    x: ti.types.ndarray(ti.f32, 1),
    scale: ti.types.ndarray(ti.f32, 1),
    bias: ti.types.ndarray(ti.f32, 1),
    mean: ti.types.ndarray(ti.f32, 1),
    var: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    channels: ti.i32,
    spatial: ti.i32,
    eps: ti.f32,
    act: ti.i32,
):
    for idx in range(n_batch * channels * spatial):
        s = idx % spatial
        c = (idx // spatial) % channels
        factor = 1.0 / ti.sqrt(var[c] + eps)
        y[idx] = nu_activate((x[idx] - mean[c]) * factor * scale[c] + bias[c], act)


ALL_NORM_KERNELS = [
    nu_instance_norm,
    nu_layer_norm,
    nu_softmax,
    nu_log_softmax,
    nu_batch_norm,
]