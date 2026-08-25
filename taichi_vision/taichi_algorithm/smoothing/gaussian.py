# Marker: GPU_NATIVE_MARKER_V11
"""Gaussian Blur - Taichi GPU (High-Performance Static Unrolled)"""

import numpy as np
import os

import os
import importlib

TAICHI_AVAILABLE = False
ti = None
tm = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        tm = importlib.import_module("taichi.math")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from .. import common
    from ..taichi_worker import ti_thread
except ImportError:
    pass

if TAICHI_AVAILABLE:

    @ti.func
    def _gaussian_blur_x_3ch_body(src: ti.template(), dst: ti.template(), h: int, w: int, weights: ti.template(), radius: int):
        for y, x in ti.ndrange(h, w):
            acc0, acc1, acc2 = 0.0, 0.0, 0.0
            total_weight = 0.0
            w0 = weights[0]
            acc0 += src[y, x, 0] * w0
            acc1 += src[y, x, 1] * w0
            acc2 += src[y, x, 2] * w0
            total_weight += w0
            for k in ti.static(range(1, 17)):
                if k <= radius:
                    wk = weights[k]
                    lx = common.reflect_idx(x - k, w)
                    rx = common.reflect_idx(x + k, w)
                    acc0 += (src[y, lx, 0] + src[y, rx, 0]) * wk
                    acc1 += (src[y, lx, 1] + src[y, rx, 1]) * wk
                    acc2 += (src[y, lx, 2] + src[y, rx, 2]) * wk
                    total_weight += 2.0 * wk
            dst[y, x, 2] = acc2 / total_weight

    @ti.func
    def _gaussian_blur_x_vec3_body(src: ti.template(), dst: ti.template(), h: int, w: int, weights: ti.template(), radius: int):
        for y, x in ti.ndrange(h, w):
            acc = ti.Vector([0.0, 0.0, 0.0])
            total_weight = 0.0
            w0 = weights[0]
            acc += src[y, x] * w0
            total_weight += w0
            for k in ti.static(range(1, 17)):
                if k <= radius:
                    wk = weights[k]
                    lx = common.reflect_idx(x - k, w)
                    rx = common.reflect_idx(x + k, w)
                    acc += (src[y, lx] + src[y, rx]) * wk
                    total_weight += 2.0 * wk
            dst[y, x] = acc / total_weight

    @ti.func
    def _gaussian_blur_y_vec3_body(src: ti.template(), dst: ti.template(), h: int, w: int, weights: ti.template(), radius: int):
        for y, x in ti.ndrange(h, w):
            acc = ti.Vector([0.0, 0.0, 0.0])
            total_weight = 0.0
            w0 = weights[0]
            acc += src[y, x] * w0
            total_weight += w0
            for k in ti.static(range(1, 17)):
                if k <= radius:
                    wk = weights[k]
                    ty = common.reflect_idx(y - k, h)
                    by = common.reflect_idx(y + k, h)
                    acc += (src[ty, x] + src[by, x]) * wk
                    total_weight += 2.0 * wk
            dst[y, x] = acc / total_weight

    @ti.func
    def _gaussian_blur_y_3ch_body(src: ti.template(), dst: ti.template(), h: int, w: int, weights: ti.template(), radius: int):
        for y, x in ti.ndrange(h, w):
            acc0, acc1, acc2 = 0.0, 0.0, 0.0
            total_weight = 0.0
            w0 = weights[0]
            acc0 += src[y, x, 0] * w0
            acc1 += src[y, x, 1] * w0
            acc2 += src[y, x, 2] * w0
            total_weight += w0
            for k in ti.static(range(1, 17)):
                if k <= radius:
                    wk = weights[k]
                    ty = common.reflect_idx(y - k, h)
                    by = common.reflect_idx(y + k, h)
                    acc0 += (src[ty, x, 0] + src[by, x, 0]) * wk
                    acc1 += (src[ty, x, 1] + src[by, x, 1]) * wk
                    acc2 += (src[ty, x, 2] + src[by, x, 2]) * wk
                    total_weight += 2.0 * wk
            dst[y, x, 0] = acc0 / total_weight
            dst[y, x, 1] = acc1 / total_weight
            dst[y, x, 2] = acc2 / total_weight

    @ti.kernel
    def _gaussian_blur_x_3ch_f32_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int, weights: ti.types.ndarray(), radius: int):
        _gaussian_blur_x_3ch_body(src, dst, h, w, weights, radius)

    @ti.kernel
    def _gaussian_blur_y_3ch_f32_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int, weights: ti.types.ndarray(), radius: int):
        _gaussian_blur_y_3ch_body(src, dst, h, w, weights, radius)

    @ti.kernel
    def _gaussian_blur_x_3ch_i32_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int, weights: ti.types.ndarray(), radius: int):
        _gaussian_blur_x_3ch_body(src, dst, h, w, weights, radius)

    @ti.kernel
    def _gaussian_blur_y_3ch_i32_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int, weights: ti.types.ndarray(), radius: int):
        _gaussian_blur_y_3ch_body(src, dst, h, w, weights, radius)

    @ti.kernel
    def _gaussian_blur_x_vec3_f32_kernel(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), h: int, w: int, weights: ti.types.ndarray(), radius: int):
        _gaussian_blur_x_vec3_body(src, dst, h, w, weights, radius)

    @ti.kernel
    def _gaussian_blur_y_vec3_f32_kernel(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), h: int, w: int, weights: ti.types.ndarray(), radius: int):
        _gaussian_blur_y_vec3_body(src, dst, h, w, weights, radius)

    @ti.kernel
    def _gaussian_blur_x_1ch_f32_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int, weights: ti.types.ndarray(), radius: int):
        for y, x in ti.ndrange(h, w):
            acc, total_w = ti.cast(0.0, ti.f32), ti.cast(0.0, ti.f32)
            w0 = weights[0]
            acc += src[y, x] * w0
            total_w += w0
            for k in ti.static(range(1, 17)):
                if k <= radius:
                    wk = weights[k]
                    acc += (src[y, common.reflect_idx(x-k, w)] + src[y, common.reflect_idx(x+k, w)]) * wk
                    total_w += 2.0 * wk
            dst[y, x] = acc / total_w

    @ti.kernel
    def _gaussian_blur_y_1ch_f32_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int, weights: ti.types.ndarray(), radius: int):
        for y, x in ti.ndrange(h, w):
            acc, total_w = 0.0, 0.0
            w0 = weights[0]
            acc += src[y, x] * w0
            total_w += w0
            for k in ti.static(range(1, 17)):
                if k <= radius:
                    wk = weights[k]
                    acc += (src[common.reflect_idx(y-k, h), x] + src[common.reflect_idx(y+k, h), x]) * wk
                    total_w += 2.0 * wk
            dst[y, x] = acc / total_w

def compute_gaussian_weights(sigma, radius):
    weights = []
    total = 0.0
    for i in range(radius + 1):
        w = np.exp(-(i * i) / (2 * sigma * sigma))
        weights.append(w)
        if i == 0: total += w
        else: total += 2 * w
    return np.array(weights) / total

@ti_thread
def gaussian_blur(src, dst=None, sigma=1.0, kernel_size=None, buffer_provider="pool", **kwargs):
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.gaussian_blur(src, sigma=sigma, kernel_size=kernel_size, return_gpu=True)

    if not TAICHI_AVAILABLE: raise ImportError("Taichi not available")

    if kernel_size is None or kernel_size <= 0:
        radius = int(np.ceil(3 * sigma))
        kernel_size = 2 * radius + 1
    else: radius = kernel_size // 2

    h, w = src.shape[:2]
    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32)
    is_3d = len(src_gpu.shape) == 3
    shape = (h, w, 3) if is_3d else (h, w)
    
    temp_gpu = common.get_temp_buffer(shape, ti.f32, buffer_provider)
    if dst is not None: dst_gpu, _ = common.ensure_taichi_field(dst, dtype=ti.f32)
    else: dst_gpu = common.get_temp_buffer(shape, ti.f32, buffer_provider)

    weights_np = compute_gaussian_weights(sigma, radius)
    weights_gpu = ti.ndarray(dtype=ti.f32, shape=(radius + 1,))
    weights_gpu.from_numpy(weights_np.astype(np.float32))

    if is_3d:
        _gaussian_blur_x_3ch_f32_kernel(src_gpu, temp_gpu, h, w, weights_gpu, radius)
        _gaussian_blur_y_3ch_f32_kernel(temp_gpu, dst_gpu, h, w, weights_gpu, radius)
    else:
        _gaussian_blur_x_1ch_f32_kernel(src_gpu, temp_gpu, h, w, weights_gpu, radius)
        _gaussian_blur_y_1ch_f32_kernel(temp_gpu, dst_gpu, h, w, weights_gpu, radius)

    common.release_temp_buffer(temp_gpu)
    if src_is_temp: common.release_temp_buffer(src_gpu)
    return common.to_numpy_if_needed(dst_gpu, not hasattr(src, "to_numpy"))
