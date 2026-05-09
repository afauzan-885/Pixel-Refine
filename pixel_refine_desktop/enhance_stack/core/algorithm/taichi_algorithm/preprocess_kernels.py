import taichi as ti
import taichi.math as tm

@ti.func
def get_pixel_safe(src: ti.types.ndarray(), y: int, x: int, h: int, w: int):
    # Robust clamping for any coordinate
    ry = tm.clamp(y, 0, h - 1)
    rx = tm.clamp(x, 0, w - 1)
    return src[ry, rx]

@ti.func
def _fused_apply_postprocess(green: ti.f32, scale_norm: ti.f32, apply_gamma: ti.i32, scale_gamma: ti.f32, gamma_pow: ti.f32, slope: ti.f32, cutoff: ti.f32, use_sharpen: ti.i32) -> ti.f32:
    green = green / scale_norm
    if apply_gamma == 1:
        green = green * scale_gamma
        if green < cutoff: green = green * slope
        else: green = 1.099 * tm.pow(green, 1.0 / gamma_pow) - 0.099
    if use_sharpen == 1: green = (green - 0.5) * 0.7 + 0.5
    return tm.clamp(green, 0.0, 1.0)

@ti.kernel
def _fused_full_pipeline_kernel_u8_aot(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.u8), ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), scale_norm: ti.f32, apply_gamma: ti.i32, scale_gamma: ti.f32, gamma_pow: ti.f32, slope: ti.f32, cutoff: ti.f32, use_sharpen: ti.i32):
    src_h, src_w = src.shape[0], src.shape[1]
    dst_h, dst_w = dst.shape[0], dst.shape[1]
    for y, x in ti.ndrange(dst_h, dst_w):
        u, v = (x + 0.5) / float(dst_w), (y + 0.5) / float(dst_h)
        src_x, src_y = u * float(src_w) - 0.5, v * float(src_h) - 0.5
        x0, y0 = int(ti.floor(src_x)), int(ti.floor(src_y))
        fx, fy = src_x - x0, src_y - y0
        x0, y0 = tm.clamp(x0, 0, src_w - 2), tm.clamp(y0, 0, src_h - 2)
        v00, v10 = ti.cast(src[y0, x0][1], ti.f32), ti.cast(src[y0, x0+1][1], ti.f32)
        v01, v11 = ti.cast(src[y0+1, x0][1], ti.f32), ti.cast(src[y0+1, x0+1][1], ti.f32)
        green = (v00*(1.0-fx) + v10*fx)*(1.0-fy) + (v01*(1.0-fx) + v11*fx)*fy
        dst[y, x] = _fused_apply_postprocess(green, scale_norm, apply_gamma, scale_gamma, gamma_pow, slope, cutoff, use_sharpen)

@ti.kernel
def _fused_full_pipeline_kernel_u16_aot(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.u16), ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), scale_norm: ti.f32, apply_gamma: ti.i32, scale_gamma: ti.f32, gamma_pow: ti.f32, slope: ti.f32, cutoff: ti.f32, use_sharpen: ti.i32):
    src_h, src_w = src.shape[0], src.shape[1]
    dst_h, dst_w = dst.shape[0], dst.shape[1]
    for y, x in ti.ndrange(dst_h, dst_w):
        u, v = (x + 0.5) / float(dst_w), (y + 0.5) / float(dst_h)
        src_x, src_y = u * float(src_w) - 0.5, v * float(src_h) - 0.5
        x0, y0 = int(ti.floor(src_x)), int(ti.floor(src_y))
        fx, fy = src_x - x0, src_y - y0
        x0, y0 = tm.clamp(x0, 0, src_w - 2), tm.clamp(y0, 0, src_h - 2)
        v00, v10 = ti.cast(src[y0, x0][1], ti.f32), ti.cast(src[y0, x0+1][1], ti.f32)
        v01, v11 = ti.cast(src[y0+1, x0][1], ti.f32), ti.cast(src[y0+1, x0+1][1], ti.f32)
        green = (v00*(1.0-fx) + v10*fx)*(1.0-fy) + (v01*(1.0-fx) + v11*fx)*fy
        dst[y, x] = _fused_apply_postprocess(green, scale_norm, apply_gamma, scale_gamma, gamma_pow, slope, cutoff, use_sharpen)

@ti.kernel
def _fused_full_pipeline_kernel_aot(src: ti.types.ndarray(dtype=ti.types.vector(3, ti.i32), ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), scale_norm: ti.f32, apply_gamma: ti.i32, scale_gamma: ti.f32, gamma_pow: ti.f32, slope: ti.f32, cutoff: ti.f32, use_sharpen: ti.i32):
    src_h, src_w = src.shape[0], src.shape[1]
    dst_h, dst_w = dst.shape[0], dst.shape[1]
    for y, x in ti.ndrange(dst_h, dst_w):
        u, v = (x + 0.5) / float(dst_w), (y + 0.5) / float(dst_h)
        src_x, src_y = u * float(src_w) - 0.5, v * float(src_h) - 0.5
        x0, y0 = int(ti.floor(src_x)), int(ti.floor(src_y))
        fx, fy = src_x - x0, src_y - y0
        x0, y0 = tm.clamp(x0, 0, src_w - 2), tm.clamp(y0, 0, src_h - 2)
        v00, v10 = ti.cast(src[y0, x0][1], ti.f32), ti.cast(src[y0, x0+1][1], ti.f32)
        v01, v11 = ti.cast(src[y0+1, x0][1], ti.f32), ti.cast(src[y0+1, x0+1][1], ti.f32)
        green = (v00*(1.0-fx) + v10*fx)*(1.0-fy) + (v01*(1.0-fx) + v11*fx)*fy
        dst[y, x] = _fused_apply_postprocess(green, scale_norm, apply_gamma, scale_gamma, gamma_pow, slope, cutoff, use_sharpen)

@ti.kernel
def _fused_full_pipeline_gray_kernel_aot(src: ti.types.ndarray(dtype=ti.i32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), scale_norm: ti.f32, apply_gamma: ti.i32, scale_gamma: ti.f32, gamma_pow: ti.f32, slope: ti.f32, cutoff: ti.f32, use_sharpen: ti.i32):
    src_h, src_w = src.shape[0], src.shape[1]
    dst_h, dst_w = dst.shape[0], dst.shape[1]
    for y, x in ti.ndrange(dst_h, dst_w):
        u, v = (x + 0.5) / float(dst_w), (y + 0.5) / float(dst_h)
        src_x, src_y = u * float(src_w) - 0.5, v * float(src_h) - 0.5
        x0, y0 = int(ti.floor(src_x)), int(ti.floor(src_y))
        fx, fy = src_x - x0, src_y - y0
        x0, y0 = tm.clamp(x0, 0, src_w - 2), tm.clamp(y0, 0, src_h - 2)
        v00, v10 = ti.cast(src[y0, x0], ti.f32), ti.cast(src[y0, x0+1], ti.f32)
        v01, v11 = ti.cast(src[y0+1, x0], ti.f32), ti.cast(src[y0+1, x0+1], ti.f32)
        green = (v00*(1.0-fx) + v10*fx)*(1.0-fy) + (v01*(1.0-fx) + v11*fx)*fy
        dst[y, x] = _fused_apply_postprocess(green, scale_norm, apply_gamma, scale_gamma, gamma_pow, slope, cutoff, use_sharpen)
