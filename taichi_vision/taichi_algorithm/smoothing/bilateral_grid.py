# Marker: GPU_NATIVE_MARKER_V3
"""
Bilateral Grid - Taichi AOT Implementation
==========================================
Fast, edge-preserving smoothing using a bilateral grid.
Refactored for AOT compatibility with split kernels.
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

try:
    from .. import common
    from ..taichi_worker import ti_thread
except ImportError:
    pass

if TAICHI_AVAILABLE:

    @ti.func
    def trilinear_sample(grid: ti.types.ndarray(), u: float, v: float, w: float, 
                         gn: int, gm: int, gl: int) -> ti.types.vector(2, ti.f32):
        """Trilinear interpolation on the 3D bilateral grid."""
        # Spatial floor
        i_int = int(ti.floor(u))
        j_int = int(ti.floor(v))
        k_int = int(ti.floor(w))
        
        # Fractional parts
        fi = u - float(i_int)
        fj = v - float(j_int)
        fk = w - float(k_int)
        
        # 8 neighbors
        res = ti.Vector([0.0, 0.0])
        
        # We use nested mix for trilinear
        # Level 0 (k_int)
        v000 = ti.Vector([grid[tm.clamp(i_int, 0, gn-1), tm.clamp(j_int, 0, gm-1), tm.clamp(k_int, 0, gl-1)][0], grid[tm.clamp(i_int, 0, gn-1), tm.clamp(j_int, 0, gm-1), tm.clamp(k_int, 0, gl-1)][1]])
        v100 = ti.Vector([grid[tm.clamp(i_int+1, 0, gn-1), tm.clamp(j_int, 0, gm-1), tm.clamp(k_int, 0, gl-1)][0], grid[tm.clamp(i_int+1, 0, gn-1), tm.clamp(j_int, 0, gm-1), tm.clamp(k_int, 0, gl-1)][1]])
        v010 = ti.Vector([grid[tm.clamp(i_int, 0, gn-1), tm.clamp(j_int+1, 0, gm-1), tm.clamp(k_int, 0, gl-1)][0], grid[tm.clamp(i_int, 0, gn-1), tm.clamp(j_int+1, 0, gm-1), tm.clamp(k_int, 0, gl-1)][1]])
        v110 = ti.Vector([grid[tm.clamp(i_int+1, 0, gn-1), tm.clamp(j_int+1, 0, gm-1), tm.clamp(k_int, 0, gl-1)][0], grid[tm.clamp(i_int+1, 0, gn-1), tm.clamp(j_int+1, 0, gm-1), tm.clamp(k_int, 0, gl-1)][1]])
        
        # Level 1 (k_int + 1)
        v001 = ti.Vector([grid[tm.clamp(i_int, 0, gn-1), tm.clamp(j_int, 0, gm-1), tm.clamp(k_int+1, 0, gl-1)][0], grid[tm.clamp(i_int, 0, gn-1), tm.clamp(j_int, 0, gm-1), tm.clamp(k_int+1, 0, gl-1)][1]])
        v101 = ti.Vector([grid[tm.clamp(i_int+1, 0, gn-1), tm.clamp(j_int, 0, gm-1), tm.clamp(k_int+1, 0, gl-1)][0], grid[tm.clamp(i_int+1, 0, gn-1), tm.clamp(j_int, 0, gm-1), tm.clamp(k_int+1, 0, gl-1)][1]])
        v011 = ti.Vector([grid[tm.clamp(i_int, 0, gn-1), tm.clamp(j_int+1, 0, gm-1), tm.clamp(k_int+1, 0, gl-1)][0], grid[tm.clamp(i_int, 0, gn-1), tm.clamp(j_int+1, 0, gm-1), tm.clamp(k_int+1, 0, gl-1)][1]])
        v111 = ti.Vector([grid[tm.clamp(i_int+1, 0, gn-1), tm.clamp(j_int+1, 0, gm-1), tm.clamp(k_int+1, 0, gl-1)][0], grid[tm.clamp(i_int+1, 0, gn-1), tm.clamp(j_int+1, 0, gm-1), tm.clamp(k_int+1, 0, gl-1)][1]])
        
        # Interpolate
        # X direction
        m00 = tm.mix(v000, v100, fi)
        m10 = tm.mix(v010, v110, fi)
        m01 = tm.mix(v001, v101, fi)
        m11 = tm.mix(v011, v111, fi)
        
        # Y direction
        n0 = tm.mix(m00, m10, fj)
        n1 = tm.mix(m01, m11, fj)
        
        # Z direction
        return tm.mix(n0, n1, fk)

    # --- AOT KERNELS ---

    @ti.kernel
    def _bg_clear_grid(grid: ti.types.ndarray(), gn: int, gm: int, gl: int):
        for i, j, k in ti.ndrange(gn, gm, gl):
            grid[i, j, k][0] = 0.0
            grid[i, j, k][1] = 0.0

    @ti.kernel
    def _bg_splat(src: ti.types.ndarray(), grid: ti.types.ndarray(), 
                  s_s: int, s_r: int, h: int, w: int, gn: int, gm: int, gl: int):
        for y, x in ti.ndrange(h, w):
            val = float(src[y, x])
            
            # Atomic add to grid (nearest bin)
            gx = int(tm.round(float(y) / float(s_s)))
            gy = int(tm.round(float(x) / float(s_s)))
            gz = int(tm.round(val / float(s_r)))
            
            # Clamp and accumulate
            ix = tm.clamp(gx, 0, gn-1)
            iy = tm.clamp(gy, 0, gm-1)
            iz = tm.clamp(gz, 0, gl-1)
            
            # Update vector lanes independently.  Atomic add on the whole
            # vector is not lowered safely by the LLVM CPU AOT backend for
            # larger grids and can corrupt the allocation under contention.
            ti.atomic_add(grid[ix, iy, iz][0], val)
            ti.atomic_add(grid[ix, iy, iz][1], 1.0)

    @ti.kernel
    def _bg_blur_x(src_grid: ti.types.ndarray(), dst_grid: ti.types.ndarray(), 
                   radius: int, sigma: float, gn: int, gm: int, gl: int):
        inv_2s2 = 1.0 / (2.0 * sigma * sigma)
        for i, j, k in ti.ndrange(gn, gm, gl):
            acc = ti.Vector([0.0, 0.0])
            total_w = 0.0
            for di in range(-radius, radius + 1):
                ni = tm.clamp(i + di, 0, gn - 1)
                wt = ti.exp(-float(di * di) * inv_2s2)
                acc += ti.Vector([src_grid[ni, j, k][0], src_grid[ni, j, k][1]]) * wt
                total_w += wt
            dst_grid[i, j, k][0] = acc[0] / total_w
            dst_grid[i, j, k][1] = acc[1] / total_w

    @ti.kernel
    def _bg_blur_y(src_grid: ti.types.ndarray(), dst_grid: ti.types.ndarray(), 
                   radius: int, sigma: float, gn: int, gm: int, gl: int):
        inv_2s2 = 1.0 / (2.0 * sigma * sigma)
        for i, j, k in ti.ndrange(gn, gm, gl):
            acc = ti.Vector([0.0, 0.0])
            total_w = 0.0
            for dj in range(-radius, radius + 1):
                nj = tm.clamp(j + dj, 0, gm - 1)
                wt = ti.exp(-float(dj * dj) * inv_2s2)
                acc += ti.Vector([src_grid[i, nj, k][0], src_grid[i, nj, k][1]]) * wt
                total_w += wt
            dst_grid[i, j, k][0] = acc[0] / total_w
            dst_grid[i, j, k][1] = acc[1] / total_w

    @ti.kernel
    def _bg_blur_z(src_grid: ti.types.ndarray(), dst_grid: ti.types.ndarray(), 
                   radius: int, sigma: float, gn: int, gm: int, gl: int):
        inv_2s2 = 1.0 / (2.0 * sigma * sigma)
        for i, j, k in ti.ndrange(gn, gm, gl):
            acc = ti.Vector([0.0, 0.0])
            total_w = 0.0
            for dk in range(-radius, radius + 1):
                nk = tm.clamp(k + dk, 0, gl - 1)
                wt = ti.exp(-float(dk * dk) * inv_2s2)
                acc += ti.Vector([src_grid[i, j, nk][0], src_grid[i, j, nk][1]]) * wt
                total_w += wt
            dst_grid[i, j, k][0] = acc[0] / total_w
            dst_grid[i, j, k][1] = acc[1] / total_w

    @ti.kernel
    def _bg_slice(src: ti.types.ndarray(), grid: ti.types.ndarray(), dst: ti.types.ndarray(), 
                   s_s: int, s_r: int, h: int, w: int, gn: int, gm: int, gl: int):
        for y, x in ti.ndrange(h, w):
            val = float(src[y, x])
            
            # Trilinear sampling
            res_vec = trilinear_sample(grid, float(y)/float(s_s), float(x)/float(s_s), val/float(s_r), gn, gm, gl)
            
            # Normalize and output
            out = val
            if res_vec[1] > 1e-6:
                out = res_vec[0] / res_vec[1]
            dst[y, x] = out

@ti_thread
def bilateral_grid_filter(img, dst=None, s_s=16, s_r=16, sigma_s=1.0, sigma_r=1.0):
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        preset = "medium"
        if s_s <= 8: preset = "heavy"
        elif s_s >= 32: preset = "light"
        res_gpu = taichi_aot.bilateral_grid_filter(img, preset=preset, return_gpu=hasattr(img, "to_numpy"))
        if dst is not None:
            if isinstance(dst, np.ndarray) and not isinstance(res_gpu, np.ndarray):
                dst[:] = res_gpu.to_numpy()
            else:
                dst[:] = res_gpu
            return dst
        return res_gpu

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    h, w = img.shape[:2]
    gn, gm, gl = (h + s_s - 1) // s_s + 1, (w + s_s - 1) // s_s + 1, 256 // s_r + 1
    
    grid = ti.Vector.ndarray(2, ti.f32, (gn, gm, gl))
    grid_tmp = ti.Vector.ndarray(2, ti.f32, (gn, gm, gl))
    
    _bg_clear_grid(grid, gn, gm, gl)
    _bg_splat(img, grid, s_s, s_r, h, w, gn, gm, gl)
    
    # Blurs
    rs, rr = int(ti.ceil(sigma_s * 3.0)), int(ti.ceil(sigma_r * 3.0))
    _bg_blur_x(grid, grid_tmp, rs, sigma_s, gn, gm, gl)
    _bg_blur_y(grid_tmp, grid, rs, sigma_s, gn, gm, gl)
    _bg_blur_z(grid, grid_tmp, rr, sigma_r, gn, gm, gl)
    
    if dst is None: dst = np.zeros_like(img)
    _bg_slice(img, grid_tmp, dst, s_s, s_r, h, w, gn, gm, gl)
    return dst
