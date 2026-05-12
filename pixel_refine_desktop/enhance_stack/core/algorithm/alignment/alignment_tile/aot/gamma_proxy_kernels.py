import taichi as ti
import taichi.math as tm
import numpy as np

@ti.func
def _gamma_proxy_core(val: ti.f32, scale: ti.f32, gamma_pow: ti.f32, slope: ti.f32, cutoff: ti.f32) -> ti.f32:
    # 1. Exposure Scaling & Clip
    x = tm.clamp(val * scale, 0.0, 1.0)
    
    # 2. Gamma Curve (BT.709 Style)
    res = 0.0
    if x < cutoff:
        res = x * slope
    else:
        res = 1.099 * tm.pow(x, 1.0 / gamma_pow) - 0.099
        
    return tm.clamp(res, 0.0, 1.0)

@ti.kernel
def gamma_proxy_rgb_kernel(
    src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    scale: ti.f32,
    gamma_pow: ti.f32,
    slope: ti.f32,
    cutoff: ti.f32
):
    for y, x in src:
        v = src[y, x]
        r = _gamma_proxy_core(v[0], scale, gamma_pow, slope, cutoff)
        g = _gamma_proxy_core(v[1], scale, gamma_pow, slope, cutoff)
        b = _gamma_proxy_core(v[2], scale, gamma_pow, slope, cutoff)
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
