# Marker: GPU_NATIVE_MARKER_V2
"""
Efficient 2D FFT Implementation in Taichi
=========================================
"""

import numpy as np
import math
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
except ImportError:
    pass

if TAICHI_AVAILABLE:
    from ..taichi_worker import ti_thread
else:
    ti_thread = lambda f: f

if TAICHI_AVAILABLE:
    # Use explicit vector NDArray type for AOT compatibility
    vec2_array = ti.types.ndarray(dtype=ti.math.vec2, ndim=2)
    f32_array = ti.types.ndarray(dtype=ti.f32, ndim=2)

    @ti.func
    def reverse_bits(n: int, bits: int) -> int:
        res = 0
        for i in range(bits):
            res = (res << 1) | (n & 1)
            n >>= 1
        return res

    @ti.kernel
    def _bit_reverse_kernel(
        src: vec2_array, dst: vec2_array, bits: int, is_col: int
    ):
        for i, j in ti.ndrange(src.shape[0], src.shape[1]):
            if is_col == 0:
                target_j = reverse_bits(j, bits)
                dst[i, target_j] = src[i, j]
            else:
                target_i = reverse_bits(i, bits)
                dst[target_i, j] = src[i, j]

    @ti.kernel
    def _fft_stage_kernel(
        data: vec2_array, n: int, stage_len: int, is_inverse: int, is_col: int
    ):
        half_len = stage_len // 2
        angle_sign = 1.0 if is_inverse == 1 else -1.0

        for i, j in ti.ndrange(data.shape[0], data.shape[1]):
            idx = j if is_col == 0 else i
            if (idx % stage_len) < half_len:
                idx0 = idx
                idx1 = idx + half_len
                angle = 2.0 * math.pi * (idx % half_len) / stage_len
                w = tm.vec2(ti.cos(angle), angle_sign * ti.sin(angle))

                v0 = tm.vec2(0.0, 0.0)
                v1 = tm.vec2(0.0, 0.0)

                if is_col == 0:
                    v0 = data[i, idx0]
                    v1 = data[i, idx1]
                    v1_twiddled = tm.vec2(v1.x * w.x - v1.y * w.y, v1.x * w.y + v1.y * w.x)
                    data[i, idx0] = v0 + v1_twiddled
                    data[i, idx1] = v0 - v1_twiddled
                else:
                    v0 = data[idx0, j]
                    v1 = data[idx1, j]
                    v1_twiddled = tm.vec2(v1.x * w.x - v1.y * w.y, v1.x * w.y + v1.y * w.x)
                    data[idx0, j] = v0 + v1_twiddled
                    data[idx1, j] = v0 - v1_twiddled

    @ti.kernel
    def _normalize_kernel(data: vec2_array, scale: float):
        for i, j in ti.ndrange(data.shape[0], data.shape[1]):
            data[i, j] *= scale

    @ti.kernel
    def _real_to_complex_kernel(
        src: f32_array, dst: vec2_array, src_h: int, src_w: int
    ):
        for i, j in ti.ndrange(dst.shape[0], dst.shape[1]):
            if i < src_h and j < src_w:
                dst[i, j] = tm.vec2(src[i, j], 0.0)
            else:
                dst[i, j] = tm.vec2(0.0, 0.0)

    @ti.kernel
    def _complex_to_real_kernel(
        src: vec2_array, dst: f32_array, dst_h: int, dst_w: int
    ):
        for i, j in ti.ndrange(src.shape[0], src.shape[1]):
            if i < dst_h and j < dst_w:
                dst[i, j] = src[i, j].x

    @ti.kernel
    def _complex_mul_kernel(
        a: vec2_array, b: vec2_array, dst: vec2_array, conj_b: int
    ):
        for i, j in ti.ndrange(a.shape[0], a.shape[1]):
            va = a[i, j]
            vb = b[i, j]
            if conj_b == 1:
                vb = tm.vec2(vb.x, -vb.y)
            dst[i, j] = tm.vec2(va.x * vb.x - va.y * vb.y, va.x * vb.y + va.y * vb.x)
    @ti.kernel
    def _complex_to_mag_kernel(src: vec2_array, dst: f32_array):
        for i, j in ti.ndrange(src.shape[0], src.shape[1]):
            dst[i, j] = tm.length(src[i, j])

    @ti.kernel
    def _phase_normalize_kernel(data: vec2_array):
        for i, j in ti.ndrange(data.shape[0], data.shape[1]):
            m = tm.length(data[i, j])
            if m > 1e-12:
                data[i, j] /= m
            else:
                data[i, j] = tm.vec2(0.0, 0.0)

    @ti.kernel
    def _hanning_window_kernel(dst: f32_array, h: int, w: int):
        for i, j in ti.ndrange(h, w):
            wy = 0.5 * (1.0 - ti.cos(2.0 * math.pi * float(i) / float(h - 1)))
            wx = 0.5 * (1.0 - ti.cos(2.0 * math.pi * float(j) / float(w - 1)))
            dst[i, j] *= (wy * wx)

    @ti.kernel
    def _complex_hanning_kernel(data: vec2_array, h: int, w: int):
        for i, j in ti.ndrange(h, w):
            wy = 0.5 * (1.0 - ti.cos(2.0 * math.pi * float(i) / float(h - 1)))
            wx = 0.5 * (1.0 - ti.cos(2.0 * math.pi * float(j) / float(w - 1)))
            data[i, j] *= (wy * wx)

def _is_power_of_two(n):
    return (n > 0) and (n & (n - 1) == 0)

def _next_power_of_two(n):
    return 1 << (n - 1).bit_length()

@ti_thread
def fft_1d_gpu(data_gpu, is_inverse=False, is_col=False):
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi is not available")
    h, w = data_gpu.shape
    n = h if is_col else w
    bits = int(math.log2(n))
    temp_gpu = common.get_temp_buffer((h, w), ti.types.vector(2, ti.f32))
    _bit_reverse_kernel(data_gpu, temp_gpu, bits, 1 if is_col else 0)
    common.copy_field(temp_gpu, data_gpu)
    common.release_temp_buffer(temp_gpu)
    for stage in range(1, bits + 1):
        _fft_stage_kernel(data_gpu, n, 1 << stage, 1 if is_inverse else 0, 1 if is_col else 0)
    if is_inverse:
        _normalize_kernel(data_gpu, 1.0 / n)

@ti_thread
def fft2(src):
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.fft2(src)
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi is not available")
    src_gpu, is_temp = common.ensure_taichi_field(src, dtype=ti.f32)
    h, w = src_gpu.shape[:2]
    target_h, target_w = _next_power_of_two(h), _next_power_of_two(w)
    complex_gpu = common.get_temp_buffer((target_h, target_w), ti.types.vector(2, ti.f32))
    _real_to_complex_kernel(src_gpu, complex_gpu, h, w)
    fft_1d_gpu(complex_gpu, is_inverse=False, is_col=False)
    fft_1d_gpu(complex_gpu, is_inverse=False, is_col=True)
    if is_temp: common.release_temp_buffer(src_gpu)
    return complex_gpu

@ti_thread
def ifft2(complex_gpu, target_shape=None):
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.ifft2(complex_gpu, target_shape=target_shape)
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi is not available")
    fft_1d_gpu(complex_gpu, is_inverse=True, is_col=True)
    fft_1d_gpu(complex_gpu, is_inverse=True, is_col=False)
    h, w = complex_gpu.shape
    out_h, out_w = target_shape if target_shape else (h, w)
    res_gpu = common.get_temp_buffer((out_h, out_w), ti.f32)
    _complex_to_real_kernel(complex_gpu, res_gpu, out_h, out_w)
    return res_gpu
