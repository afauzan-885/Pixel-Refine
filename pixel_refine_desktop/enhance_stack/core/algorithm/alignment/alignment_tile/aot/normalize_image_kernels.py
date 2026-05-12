import taichi as ti
import taichi.math as tm

@ti.kernel
def normalize_f32_to_vec3_kernel(
    src: ti.types.ndarray(dtype=ti.f32, ndim=2),
    dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    inv_scale: ti.f32
):
    for y, x in src:
        v = src[y, x] * inv_scale
        dst[y, x] = ti.Vector([v, v, v], dt=ti.f32)

@ti.kernel
def normalize_vec3_f32_to_vec3_f32_kernel(
    src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    inv_scale: ti.f32
):
    for y, x in src:
        v = src[y, x] * inv_scale
        dst[y, x] = v
