# Marker: GPU_NATIVE_MARKER_V3
"""
Area Interpolation (INTER_AREA) - Taichi AOT Implementation
===========================================================
High-quality downscaling using pixel area relation.
Prevents aliasing by integrating contribution of source pixels.
"""

import numpy as np

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

if TAICHI_AVAILABLE:

    @ti.kernel
    def _inter_area_1ch_kernel(
        src: ti.types.ndarray(), 
        dst: ti.types.ndarray(), 
        sh: int, sw: int, dh: int, dw: int
    ):
        scale_x = float(sw) / float(dw)
        scale_y = float(sh) / float(dh)
        
        # Norm factor is the area of one destination pixel in source coordinates
        inv_norm = 1.0 / (scale_x * scale_y)
        
        for y, x in dst:
            x_start = float(x) * scale_x
            x_end = float(x + 1) * scale_x
            y_start = float(y) * scale_y
            y_end = float(y + 1) * scale_y
            
            acc = 0.0
            sum_w = 0.0
            
            y_min = int(ti.floor(y_start))
            y_max = int(ti.ceil(y_end))
            x_min = int(ti.floor(x_start))
            x_max = int(ti.ceil(x_end))
            
            for iy in range(y_min, y_max):
                for ix in range(x_min, x_max):
                    iy_c = tm.clamp(iy, 0, sh - 1)
                    ix_c = tm.clamp(ix, 0, sw - 1)
                    
                    w_x = ti.max(0.0, ti.min(float(ix + 1), x_end) - ti.max(float(ix), x_start))
                    w_y = ti.max(0.0, ti.min(float(iy + 1), y_end) - ti.max(float(iy), y_start))
                    w = w_x * w_y
                    
                    acc += float(src[iy_c, ix_c]) * w
                    sum_w += w
            
            dst[y, x] = acc / ti.max(sum_w, 1e-9)

    @ti.kernel
    def _inter_area_vec3_kernel(
        src: ti.types.ndarray(), 
        dst: ti.types.ndarray(), 
        sh: int, sw: int, dh: int, dw: int
    ):
        scale_x = float(sw) / float(dw)
        scale_y = float(sh) / float(dh)
        
        for y, x in dst:
            x_start = float(x) * scale_x
            x_end = float(x + 1) * scale_x
            y_start = float(y) * scale_y
            y_end = float(y + 1) * scale_y
            
            acc = ti.Vector([0.0, 0.0, 0.0])
            sum_w = 0.0
            
            y_min = int(ti.floor(y_start))
            y_max = int(ti.ceil(y_end))
            x_min = int(ti.floor(x_start))
            x_max = int(ti.ceil(x_end))
            
            for iy in range(y_min, y_max):
                for ix in range(x_min, x_max):
                    iy_c = tm.clamp(iy, 0, sh - 1)
                    ix_c = tm.clamp(ix, 0, sw - 1)
                    
                    w_x = ti.max(0.0, ti.min(float(ix + 1), x_end) - ti.max(float(ix), x_start))
                    w_y = ti.max(0.0, ti.min(float(iy + 1), y_end) - ti.max(float(iy), y_start))
                    w = w_x * w_y
                    
                    acc += src[iy_c, ix_c] * w
                    sum_w += w
            
            dst[y, x] = acc / ti.max(sum_w, 1e-9)

    @ti.kernel
    def _inter_area_offset_1ch_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(),
        sh: int, sw: int, dh: int, dw: int, offset_y: int, offset_x: int,
    ):
        scale_x, scale_y = float(sw) / float(dw), float(sh) / float(dh)
        for y, x in ti.ndrange(dst.shape[0], dst.shape[1]):
            gy, gx = y + offset_y, x + offset_x
            xs, xe = float(gx) * scale_x, float(gx + 1) * scale_x
            ys, ye = float(gy) * scale_y, float(gy + 1) * scale_y
            acc, sum_w = 0.0, 0.0
            for iy in range(int(ti.floor(ys)), int(ti.ceil(ye))):
                for ix in range(int(ti.floor(xs)), int(ti.ceil(xe))):
                    wx = ti.max(0.0, ti.min(float(ix + 1), xe) - ti.max(float(ix), xs))
                    wy = ti.max(0.0, ti.min(float(iy + 1), ye) - ti.max(float(iy), ys))
                    weight = wx * wy
                    acc += float(src[tm.clamp(iy, 0, sh - 1), tm.clamp(ix, 0, sw - 1)]) * weight
                    sum_w += weight
            dst[y, x] = acc / ti.max(sum_w, 1e-9)

    @ti.kernel
    def _inter_area_offset_vec3_kernel(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        sh: int, sw: int, dh: int, dw: int, offset_y: int, offset_x: int,
    ):
        scale_x, scale_y = float(sw) / float(dw), float(sh) / float(dh)
        for y, x in ti.ndrange(dst.shape[0], dst.shape[1]):
            gy, gx = y + offset_y, x + offset_x
            xs, xe = float(gx) * scale_x, float(gx + 1) * scale_x
            ys, ye = float(gy) * scale_y, float(gy + 1) * scale_y
            acc, sum_w = ti.Vector([0.0, 0.0, 0.0]), 0.0
            for iy in range(int(ti.floor(ys)), int(ti.ceil(ye))):
                for ix in range(int(ti.floor(xs)), int(ti.ceil(xe))):
                    wx = ti.max(0.0, ti.min(float(ix + 1), xe) - ti.max(float(ix), xs))
                    wy = ti.max(0.0, ti.min(float(iy + 1), ye) - ti.max(float(iy), ys))
                    weight = wx * wy
                    acc += src[tm.clamp(iy, 0, sh - 1), tm.clamp(ix, 0, sw - 1)] * weight
                    sum_w += weight
            dst[y, x] = acc / ti.max(sum_w, 1e-9)
