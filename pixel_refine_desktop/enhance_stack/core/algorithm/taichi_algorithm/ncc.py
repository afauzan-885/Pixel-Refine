"""
Normalized Cross-Correlation (NCC) - Taichi GPU Implementation
==============================================================
Provides high-performance correlation functions using Hybrid Integral + Spatial.
"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm
    from .taichi_worker import ti_thread, TAICHI_AVAILABLE
    from . import common
except ImportError:
    TAICHI_AVAILABLE = False

if TAICHI_AVAILABLE:
    @ti.kernel
    def _integral_image_row_scan_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sum_h: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sq_sum_h: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: int, w: int
    ):
        for y in ti.ndrange(h):
            row_sum = 0.0
            row_sq_sum = 0.0
            for x in range(w):
                val = src[y, x]
                row_sum += val
                row_sq_sum += val * val
                sum_h[y, x] = row_sum
                sq_sum_h[y, x] = row_sq_sum

    @ti.kernel
    def _integral_image_col_scan_kernel(
        sum_h: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sq_sum_h: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sum_2d: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sq_sum_2d: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: int, w: int
    ):
        for x in ti.ndrange(w):
            col_sum = 0.0
            col_sq_sum = 0.0
            for y in range(h):
                col_sum += sum_h[y, x]
                col_sq_sum += sq_sum_h[y, x]
                sum_2d[y, x] = col_sum
                sq_sum_2d[y, x] = col_sq_sum

    @ti.kernel
    def _compute_correlation_kernel(
        image: ti.types.ndarray(dtype=ti.f32, ndim=2),
        template: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h_img: int, w_img: int,
        h_temp: int, w_temp: int,
        stride: int
    ):
        """Pure Cross-Correlation with Stride support."""
        for y, x in ti.ndrange((h_img - h_temp) // stride + 1, (w_img - w_temp) // stride + 1):
            acc = 0.0
            iy, ix = y * stride, x * stride
            for i, j in ti.ndrange(h_temp, w_temp):
                acc += image[iy + i, ix + j] * template[i, j]
            dst[y, x] = acc

    @ti.kernel
    def _assemble_zncc_kernel(
        corr: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sum_img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sq_sum_img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sum_t: float,
        var_t_n: float,
        n: float,
        h_temp: int,
        w_temp: int,
        stride: int
    ):
        """Combine correlation and stats with Stride support."""
        for y, x in ti.ndrange(corr.shape[0], corr.shape[1]):
            iy, ix = y * stride, x * stride
            y1, x1 = iy - 1, ix - 1
            y2, x2 = iy + h_temp - 1, ix + w_temp - 1
            
            s_a = sum_img[y2, x2]
            s_b = sum_img[y1, x2] if y1 >= 0 else 0.0
            s_c = sum_img[y2, x1] if x1 >= 0 else 0.0
            s_d = sum_img[y1, x1] if (y1 >= 0 and x1 >= 0) else 0.0
            s_i = s_a - s_b - s_c + s_d

            sq_a = sq_sum_img[y2, x2]
            sq_b = sq_sum_img[y1, x2] if y1 >= 0 else 0.0
            sq_c = sq_sum_img[y2, x1] if x1 >= 0 else 0.0
            sq_d = sq_sum_img[y1, x1] if (y1 >= 0 and x1 >= 0) else 0.0
            s_sq_i = sq_a - sq_b - sq_c + sq_d
            
            numerator = corr[y, x] - (s_i * sum_t / n)
            v_i_n = ti.max(0.0, s_sq_i - (s_i**2 / n))
            denominator = ti.sqrt(ti.max(1e-12, v_i_n * var_t_n))
            
            dst[y, x] = tm.clamp(numerator / denominator, -1.0, 1.0)

    @ti.kernel
    def _compute_global_zncc_surface(
        ref: ti.types.ndarray(dtype=ti.f32, ndim=2),
        comp: ti.types.ndarray(dtype=ti.f32, ndim=2),
        cost_surface: ti.types.ndarray(dtype=ti.f32, ndim=2),
        max_shift: int,
    ):
        h, w = ref.shape[0], ref.shape[1]
        for dy, dx in ti.ndrange(2 * max_shift + 1, 2 * max_shift + 1):
            shift_y = dy - max_shift
            shift_x = dx - max_shift

            sum_ref = 0.0
            sum_comp = 0.0
            sum_ref2 = 0.0
            sum_comp2 = 0.0
            sum_ref_comp = 0.0
            count = 0.0

            for y, x in ti.ndrange(h, w):
                comp_y = y + shift_y
                comp_x = x + shift_x
                if 0 <= comp_y < h and 0 <= comp_x < w:
                    v_r = ref[y, x]
                    v_c = comp[comp_y, comp_x]
                    sum_ref += v_r
                    sum_comp += v_c
                    sum_ref2 += v_r * v_r
                    sum_comp2 += v_c * v_c
                    sum_ref_comp += v_r * v_c
                    count += 1.0

            if count > 0:
                mean_r = sum_ref / count
                mean_c = sum_comp / count
                var_r = sum_ref2 - (sum_ref * sum_ref / count)
                var_c = sum_comp2 - (sum_comp * sum_comp / count)
                cov = sum_ref_comp - (sum_ref * sum_comp / count)

                numerator = cov
                denominator = ti.sqrt(ti.max(1e-12, var_r * var_c))

                if denominator > 1e-6:
                    zncc = numerator / denominator
                    cost_surface[dy, dx] = 1.0 - zncc
                else:
                    cost_surface[dy, dx] = 1e10
            else:
                cost_surface[dy, dx] = 1e10


@ti_thread
def zncc(image, template, stride=1):
    """JIT Version of NCC with Stride."""
    img_gpu, img_temp = common.ensure_taichi_field(image, dtype=ti.f32)
    temp_gpu, temp_temp = common.ensure_taichi_field(template, dtype=ti.f32)
    
    h_img, w_img = img_gpu.shape[:2]
    h_temp, w_temp = temp_gpu.shape[:2]
    
    res_h = (h_img - h_temp) // stride + 1
    res_w = (w_img - w_temp) // stride + 1
    
    res_field = common.get_temp_buffer((res_h, res_w), ti.f32)
    corr_field = common.get_temp_buffer((res_h, res_w), ti.f32)
    sum_h = common.get_temp_buffer((h_img, w_img), ti.f32)
    sq_sum_h = common.get_temp_buffer((h_img, w_img), ti.f32)
    sum_2d = common.get_temp_buffer((h_img, w_img), ti.f32)
    sq_sum_2d = common.get_temp_buffer((h_img, w_img), ti.f32)

    temp_np = template if isinstance(template, np.ndarray) else template.to_numpy()
    sum_t = float(np.sum(temp_np))
    var_t_n = float(np.sum(temp_np**2) - (sum_t**2 / (h_temp * w_temp)))

    _integral_image_row_scan_kernel(img_gpu, sum_h, sq_sum_h, h_img, w_img)
    _integral_image_col_scan_kernel(sum_h, sq_sum_h, sum_2d, sq_sum_2d, h_img, w_img)
    _compute_correlation_kernel(img_gpu, temp_gpu, corr_field, h_img, w_img, h_temp, w_temp, stride)
    _assemble_zncc_kernel(corr_field, sum_2d, sq_sum_2d, res_field, sum_t, var_t_n, float(h_temp * w_temp), h_temp, w_temp, stride)

    res_np = res_field.to_numpy()

    for f in [res_field, corr_field, sum_h, sq_sum_h, sum_2d, sq_sum_2d]:
        common.release_temp_buffer(f)
    if img_temp: common.release_temp_buffer(img_gpu)
    if temp_temp: common.release_temp_buffer(temp_gpu)

    return res_np

def global_translate_zncc(ref, comp, max_shift=16):
    """Fallback JIT translate."""
    ref_gpu, _ = common.ensure_taichi_field(ref, ti.f32)
    comp_gpu, _ = common.ensure_taichi_field(comp, ti.f32)
    surface = common.get_temp_buffer((2*max_shift+1, 2*max_shift+1), ti.f32)
    _compute_global_zncc_surface(ref_gpu, comp_gpu, surface, max_shift)
    res = surface.to_numpy()
    min_idx = np.unravel_index(np.argmin(res), res.shape)
    return int(min_idx[1] - max_shift), int(min_idx[0] - max_shift), float(res[min_idx])

def match_template(image, template):
    """Alias for zncc."""
    return zncc(image, template)
