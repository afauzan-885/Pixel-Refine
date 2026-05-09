import taichi as ti
import taichi.math as tm
from . import common

@ti.func
def _get_gaussian_weight(dy: int, dx: int) -> ti.f32:
    val = 0.0
    if dy == -2:
        if dx == -2: val = 0.002969
        elif dx == -1: val = 0.013306
        elif dx == 0: val = 0.021938
        elif dx == 1: val = 0.013306
        elif dx == 2: val = 0.002969
    elif dy == -1:
        if dx == -2: val = 0.013306
        elif dx == -1: val = 0.059634
        elif dx == 0: val = 0.098320
        elif dx == 1: val = 0.059634
        elif dx == 2: val = 0.013306
    elif dy == 0:
        if dx == -2: val = 0.021938
        elif dx == -1: val = 0.098320
        elif dx == 0: val = 0.162103
        elif dx == 1: val = 0.098320
        elif dx == 2: val = 0.021938
    elif dy == 1:
        if dx == -2: val = 0.013306
        elif dx == -1: val = 0.059634
        elif dx == 0: val = 0.098320
        elif dx == 1: val = 0.059634
        elif dx == 2: val = 0.013306
    elif dy == 2:
        if dx == -2: val = 0.002969
        elif dx == -1: val = 0.013306
        elif dx == 0: val = 0.021938
        elif dx == 1: val = 0.013306
        elif dx == 2: val = 0.002969
    return val

@ti.func
def _guided_flow_at_i32_ref3d_vec(flow: ti.template(), ref_vec: ti.template(), y: int, x: int) -> ti.types.vector(2, ti.f32):
    h, w = flow.shape[0], flow.shape[1]
    inv_norm = 1.0 / 65535.0
    total_w = 1e-12
    sum_uv = ti.Vector([0.0, 0.0])
    center_val = float(ref_vec[y, x][1]) * inv_norm
    for dy in ti.static(range(-2, 3)):
        ny = common.reflect_idx(y + dy, h)
        for dx in ti.static(range(-2, 3)):
            nx = common.reflect_idx(x + dx, w)
            w_s = _get_gaussian_weight(dy, dx)
            val_neighbor = float(ref_vec[ny, nx][1]) * inv_norm
            diff = val_neighbor - center_val
            w_curr = w_s * ti.exp(-(diff * diff) * 50.0)
            sum_uv += ti.Vector([flow[ny, nx, 0], flow[ny, nx, 1]]) * w_curr
            total_w += w_curr
    return sum_uv / total_w

@ti.kernel
def _warp_guided_i32_rgb_aot(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.i32), ndim=2), flow: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.i32), ndim=2), ref: ti.types.ndarray(dtype=ti.types.vector(3, ti.i32), ndim=2)):
    h, w = src.shape[0], src.shape[1]
    for y, x in ti.ndrange(h, w):
        guided_uv = _guided_flow_at_i32_ref3d_vec(flow, ref, y, x)
        u_final, v_final = float(x) + guided_uv[0], float(y) + guided_uv[1]
        x_int, y_int = int(ti.floor(u_final)), int(ti.floor(v_final))
        dx, dy = u_final - float(x_int), v_final - float(y_int)
        w_x, w_y = common.cubic_hermite_weights(dx), common.cubic_hermite_weights(dy)
        res = ti.Vector([0.0, 0.0, 0.0])
        for m in ti.static(range(-1, 3)):
            yy = common.reflect_idx(y_int + m, h)
            row_res = ti.Vector([0.0, 0.0, 0.0])
            for n in ti.static(range(-1, 3)):
                xx = common.reflect_idx(x_int + n, w)
                row_res += ti.cast(src[yy, xx], ti.f32) * w_x[n + 1]
            res += row_res * w_y[m + 1]
        dst[y, x] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.i32)

@ti.kernel
def _warp_naked_i32_rgb_aot(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.i32), ndim=2), flow: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.i32), ndim=2)):
    h, w = src.shape[0], src.shape[1]
    for y, x in ti.ndrange(h, w):
        u_final, v_final = float(x) + flow[y, x, 0], float(y) + flow[y, x, 1]
        x_int, y_int = int(ti.floor(u_final)), int(ti.floor(v_final))
        dx, dy = u_final - float(x_int), v_final - float(y_int)
        w_x, w_y = common.cubic_hermite_weights(dx), common.cubic_hermite_weights(dy)
        res = ti.Vector([0.0, 0.0, 0.0])
        for m in ti.static(range(-1, 3)):
            yy = common.reflect_idx(y_int + m, h)
            row_res = ti.Vector([0.0, 0.0, 0.0])
            for n in ti.static(range(-1, 3)):
                xx = common.reflect_idx(x_int + n, w)
                row_res += ti.cast(src[yy, xx], ti.f32) * w_x[n + 1]
            res += row_res * w_y[m + 1]
        dst[y, x] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.i32)

@ti.kernel
def _warp_guided_f32_rgb_aot(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), flow: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), ref: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2)):
    h, w = src.shape[0], src.shape[1]
    for y, x in ti.ndrange(h, w):
        guided_uv = _guided_flow_at_i32_ref3d_vec(flow, ref, y, x)
        u_final, v_final = float(x) + guided_uv[0], float(y) + guided_uv[1]
        x_int, y_int = int(ti.floor(u_final)), int(ti.floor(v_final))
        dx, dy = u_final - float(x_int), v_final - float(y_int)
        w_x, w_y = common.cubic_hermite_weights(dx), common.cubic_hermite_weights(dy)
        res = ti.Vector([0.0, 0.0, 0.0])
        for m in ti.static(range(-1, 3)):
            yy = common.reflect_idx(y_int + m, h)
            row_res = ti.Vector([0.0, 0.0, 0.0])
            for n in ti.static(range(-1, 3)):
                xx = common.reflect_idx(x_int + n, w)
                row_res += src[yy, xx] * w_x[n + 1]
            res += row_res * w_y[m + 1]
        dst[y, x] = tm.clamp(res, 0.0, 1.0)

@ti.kernel
def _warp_naked_f32_rgb_aot(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2), flow: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2)):
    h, w = src.shape[0], src.shape[1]
    for y, x in ti.ndrange(h, w):
        u_final, v_final = float(x) + flow[y, x, 0], float(y) + flow[y, x, 1]
        x_int, y_int = int(ti.floor(u_final)), int(ti.floor(v_final))
        dx, dy = u_final - float(x_int), v_final - float(y_int)
        w_x, w_y = common.cubic_hermite_weights(dx), common.cubic_hermite_weights(dy)
        res = ti.Vector([0.0, 0.0, 0.0])
        for m in ti.static(range(-1, 3)):
            yy = common.reflect_idx(y_int + m, h)
            row_res = ti.Vector([0.0, 0.0, 0.0])
            for n in ti.static(range(-1, 3)):
                xx = common.reflect_idx(x_int + n, w)
                row_res += src[yy, xx] * w_x[n + 1]
            res += row_res * w_y[m + 1]
        dst[y, x] = tm.clamp(res, 0.0, 1.0)
