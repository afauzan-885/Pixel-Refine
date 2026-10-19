# Marker: GPU_NATIVE_MARKER_V15
"""Box Filter - Taichi GPU (Final Legendary Restoration: Fused 3x3 + Separable Generic)"""

import numpy as np
import os

import os
import importlib

MAX_EXACT_FLOAT_RADIUS = (1 << 24) - 1

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

    @ti.kernel
    def _box_filter_3x3_3ch_f32_unrolled_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int):
        # FUSED 3x3 Pass (Legendary 38 FPS Path)
        # Nested ranges avoid the 2D ndrange signed-div/mod unflatten path on
        # Vulkan/OpenGL while preserving the same row-major output domain.
        for y in range(h):
            for x in range(w):
                acc0, acc1, acc2 = 0.0, 0.0, 0.0
                for i in ti.static(range(-1, 2)):
                    cy = tm.clamp(y + i, 0, h - 1)
                    for j in ti.static(range(-1, 2)):
                        cx = tm.clamp(x + j, 0, w - 1)
                        acc0 += src[cy, cx, 0]
                        acc1 += src[cy, cx, 1]
                        acc2 += src[cy, cx, 2]
                dst[y, x, 0] = acc0 / 9.0
                dst[y, x, 1] = acc1 / 9.0
                dst[y, x, 2] = acc2 / 9.0

    @ti.kernel
    def _box_filter_3x3_vec3_f32_kernel(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), h: int, w: int):
        for y in range(h):
            for x in range(w):
                acc = ti.Vector([0.0, 0.0, 0.0])
                for i in ti.static(range(-1, 2)):
                    cy = tm.clamp(y + i, 0, h - 1)
                    for j in ti.static(range(-1, 2)):
                        cx = tm.clamp(x + j, 0, w - 1)
                        acc += src[cy, cx]
                dst[y, x] = acc / 9.0

    @ti.kernel
    def _box_blur_h_generic_3ch_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int, radius: ti.f32):
        for y in range(h):
            for x in range(w):
                acc0, acc1, acc2 = 0.0, 0.0, 0.0
                q = -radius
                while q <= radius:
                    cx = tm.clamp(x + ti.cast(q, ti.i32), 0, w - 1)
                    acc0 += src[y, cx, 0]
                    acc1 += src[y, cx, 1]
                    acc2 += src[y, cx, 2]
                    q += 1.0
                inv = 1.0 / (radius * 2.0 + 1.0)
                dst[y, x, 0] = acc0 * inv
                dst[y, x, 1] = acc1 * inv
                dst[y, x, 2] = acc2 * inv

    @ti.kernel
    def _box_blur_v_generic_3ch_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int, radius: ti.f32):
        for y in range(h):
            for x in range(w):
                acc0, acc1, acc2 = 0.0, 0.0, 0.0
                q = -radius
                while q <= radius:
                    cy = tm.clamp(y + ti.cast(q, ti.i32), 0, h - 1)
                    acc0 += src[cy, x, 0]
                    acc1 += src[cy, x, 1]
                    acc2 += src[cy, x, 2]
                    q += 1.0
                inv = 1.0 / (radius * 2.0 + 1.0)
                dst[y, x, 0] = acc0 * inv
                dst[y, x, 1] = acc1 * inv
                dst[y, x, 2] = acc2 * inv

    @ti.kernel
    def _box_blur_h_vec3_f32_kernel(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), h: int, w: int, radius: ti.f32):
        for y in range(h):
            for x in range(w):
                acc = ti.Vector([0.0, 0.0, 0.0])
                q = -radius
                while q <= radius:
                    cx = tm.clamp(x + ti.cast(q, ti.i32), 0, w - 1)
                    acc += src[y, cx]
                    q += 1.0
                dst[y, x] = acc * (1.0 / (radius * 2.0 + 1.0))

    @ti.kernel
    def _box_blur_v_vec3_f32_kernel(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), h: int, w: int, radius: ti.f32):
        for y in range(h):
            for x in range(w):
                acc = ti.Vector([0.0, 0.0, 0.0])
                q = -radius
                while q <= radius:
                    cy = tm.clamp(y + ti.cast(q, ti.i32), 0, h - 1)
                    acc += src[cy, x]
                    q += 1.0
                dst[y, x] = acc * (1.0 / (radius * 2.0 + 1.0))

    @ti.kernel
    def _box_filter_3x3_1ch_f32_unrolled_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int):
        for y in range(h):
            for x in range(w):
                acc = 0.0
                for i in ti.static(range(-1, 2)):
                    cy = tm.clamp(y + i, 0, h - 1)
                    for j in ti.static(range(-1, 2)):
                        cx = tm.clamp(x + j, 0, w - 1)
                        acc += src[cy, cx]
                dst[y, x] = acc / 9.0

    @ti.kernel
    def _box_blur_h_generic_1ch_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int, radius: ti.f32):
        for y in range(h):
            for x in range(w):
                acc = 0.0
                q = -radius
                while q <= radius:
                    cx = tm.clamp(x + ti.cast(q, ti.i32), 0, w - 1)
                    acc += src[y, cx]
                    q += 1.0
                dst[y, x] = acc * (1.0 / (radius * 2.0 + 1.0))

    @ti.kernel
    def _box_blur_v_generic_1ch_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int, radius: ti.f32):
        for y in range(h):
            for x in range(w):
                acc = 0.0
                q = -radius
                while q <= radius:
                    cy = tm.clamp(y + ti.cast(q, ti.i32), 0, h - 1)
                    acc += src[cy, x]
                    q += 1.0
                dst[y, x] = acc * (1.0 / (radius * 2.0 + 1.0))


@ti_thread
def box_filter(
    src, dst=None, kernel_size: int = 3, buffer_provider="pool", enable_tiling=True
):
    if kernel_size < 1 or kernel_size % 2 == 0:
        raise ValueError("kernel_size must be a positive odd integer")
    if kernel_size // 2 > MAX_EXACT_FLOAT_RADIUS:
        raise ValueError("kernel_size exceeds the exact float32 radius range")

    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.box_filter(src, kernel_size=kernel_size, return_gpu=True)

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h, w = src.shape[:2]
    radius = kernel_size // 2
    is_3d = len(src.shape) == 3 and src.shape[2] == 3
    
    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32)
    if dst is not None:
        dst_gpu, _ = common.ensure_taichi_field(dst, dtype=ti.f32)
    else:
        dst_gpu = common.get_temp_buffer(src_gpu.shape, ti.f32, buffer_provider)

    if is_3d:
        if kernel_size == 3:
            _box_filter_3x3_3ch_f32_unrolled_kernel(src_gpu, dst_gpu, h, w)
        else:
            tmp_gpu = common.get_temp_buffer(src_gpu.shape, ti.f32, buffer_provider)
            _box_blur_h_generic_3ch_kernel(src_gpu, tmp_gpu, h, w, float(radius))
            _box_blur_v_generic_3ch_kernel(tmp_gpu, dst_gpu, h, w, float(radius))
            common.release_temp_buffer(tmp_gpu)
    else:
        if kernel_size == 3:
            _box_filter_3x3_1ch_f32_unrolled_kernel(src_gpu, dst_gpu, h, w)
        else:
            tmp_gpu = common.get_temp_buffer(src_gpu.shape, ti.f32, buffer_provider)
            _box_blur_h_generic_1ch_kernel(src_gpu, tmp_gpu, h, w, float(radius))
            _box_blur_v_generic_1ch_kernel(tmp_gpu, dst_gpu, h, w, float(radius))
            common.release_temp_buffer(tmp_gpu)

    if src_is_temp: common.release_temp_buffer(src_gpu)
    return common.to_numpy_if_needed(dst_gpu, not hasattr(src, "to_numpy"))

def box_filter_2d(src, dst=None, kernel_size=3, **kwargs):
    return box_filter(src, dst, kernel_size, **kwargs)
