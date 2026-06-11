import taichi as ti
import taichi.math as tm
import numpy as np

@ti.func
def _gamma_proxy_core(val: ti.f32, scale: ti.f32, gamma_pow: ti.f32, slope: ti.f32, cutoff: ti.f32) -> ti.f32:
    # 1. Exposure Scaling (No early clamping to allow Sigmoid to compress highlights naturally)
    x = val * scale
    
    # 2. Dynamic Algebraic Sigmoid Highlight Roll-off (Tone Mapping)
    x_mapped = x / tm.sqrt(1.0 + x * x)
    
    # 3. Gamma Correction (clamped to 0.0-1.0 to ensure correct range)
    res = tm.pow(tm.clamp(x_mapped, 0.0, 1.0), 1.0 / gamma_pow)
        
    return res

@ti.kernel
def gamma_proxy_rgb_kernel(
    src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    cmatrix: ti.types.ndarray(dtype=ti.f32, ndim=2),
    scale: ti.f32,
    gamma_pow: ti.f32,
    slope: ti.f32,
    cutoff: ti.f32
):
    for y, x in src:
        v = src[y, x]
        # On-the-fly Camera-to-sRGB matrix multiplication
        r_lin = cmatrix[0, 0] * v[0] + cmatrix[0, 1] * v[1] + cmatrix[0, 2] * v[2]
        g_lin = cmatrix[1, 0] * v[0] + cmatrix[1, 1] * v[1] + cmatrix[1, 2] * v[2]
        b_lin = cmatrix[2, 0] * v[0] + cmatrix[2, 1] * v[1] + cmatrix[2, 2] * v[2]
        
        r = _gamma_proxy_core(r_lin, scale, gamma_pow, slope, cutoff)
        g = _gamma_proxy_core(g_lin, scale, gamma_pow, slope, cutoff)
        b = _gamma_proxy_core(b_lin, scale, gamma_pow, slope, cutoff)
        dst[y, x] = ti.Vector([r, g, b])

@ti.kernel
def gamma_proxy_single_kernel(
    src: ti.types.ndarray(dtype=ti.f32, ndim=2),
    dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
    scale: ti.f32,
    gamma_pow: ti.f32,
    slope: ti.f32,
    cutoff: ti.f32
):
    for y, x in src:
        dst[y, x] = _gamma_proxy_core(src[y, x], scale, gamma_pow, slope, cutoff)
