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

import numpy as np
try:
    from .. import common
    from ..common import ti_thread
except ImportError:
    pass

if TAICHI_AVAILABLE:
    @ti.kernel
    def _integral_image_row_scan_kernel(src: ti.types.ndarray(), sum_h: ti.types.ndarray(), sq_sum_h: ti.types.ndarray(), h: int, w: int):
        for i in range(h):
            row_sum = 0.0
            row_sq_sum = 0.0
            for j in range(w):
                val = src[i, j]
                row_sum += val
                row_sq_sum += val * val
                sum_h[i, j] = row_sum
                sq_sum_h[i, j] = row_sq_sum

    @ti.kernel
    def _integral_image_col_scan_kernel(sum_h: ti.types.ndarray(), sq_sum_h: ti.types.ndarray(), sum_2d: ti.types.ndarray(), sq_sum_2d: ti.types.ndarray(), h: int, w: int):
        for j in range(w):
            col_sum = 0.0
            col_sq_sum = 0.0
            for i in range(h):
                col_sum += sum_h[i, j]
                col_sq_sum += sq_sum_h[i, j]
                sum_2d[i, j] = col_sum
                sq_sum_2d[i, j] = col_sq_sum

    @ti.kernel
    def _zncc_spatial_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        template: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sum_img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sq_sum_img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sum_t: float,
        var_t_n: float,
        n: float,
        stride: int
    ):
        """Standard Spatial ZNCC with O(1) local stats via Integral Images."""
        h_t, w_t = template.shape[0], template.shape[1]
        for y, x in ti.ndrange(dst.shape[0], dst.shape[1]):
            base_y = y * stride
            base_x = x * stride
            
            # Local Sum and Square Sum from Integral Image
            y2, x2 = base_y + h_t - 1, base_x + w_t - 1
            y1, x1 = base_y - 1, base_x - 1
            
            s_i = sum_img[y2, x2]
            if y1 >= 0: s_i -= sum_img[y1, x2]
            if x1 >= 0: s_i -= sum_img[y2, x1]
            if y1 >= 0 and x1 >= 0: s_i += sum_img[y1, x1]

            s_sq_i = sq_sum_img[y2, x2]
            if y1 >= 0: s_sq_i -= sq_sum_img[y1, x2]
            if x1 >= 0: s_sq_i -= sq_sum_img[y2, x1]
            if y1 >= 0 and x1 >= 0: s_sq_i += sq_sum_img[y1, x1]

            # Correlation
            corr = 0.0
            for i, j in ti.ndrange(h_t, w_t):
                corr += src[base_y + i, base_x + j] * template[i, j]
            
            # ZNCC Formula (OpenCV TM_CCOEFF_NORMED equivalent)
            numerator = corr - (s_i * sum_t / n)
            v_i_n = ti.max(0.0, s_sq_i - (s_i**2 / n))
            denominator = ti.sqrt(ti.max(1e-12, v_i_n * var_t_n))
            
            dst[y, x] = tm.clamp(numerator / denominator, -1.0, 1.0)

    @ti.kernel
    def _reduce_row_max_kernel(res: ti.types.ndarray(), row_max: ti.types.ndarray()):
        for i in range(res.shape[0]):
            max_val = -1e10
            max_idx = 0
            for j in range(res.shape[1]):
                val = res[i, j]
                if val > max_val:
                    max_val = val
                    max_idx = j
            row_max[i, 0] = max_val
            row_max[i, 1] = ti.cast(max_idx, ti.f32)

    @ti.kernel
    def _reduce_global_max_kernel(row_max: ti.types.ndarray(), final_peak: ti.types.ndarray()):
        max_val = -1e10
        max_y = 0
        max_x = 0
        for i in range(row_max.shape[0]):
            val = row_max[i, 0]
            if val > max_val:
                max_val = val
                max_y = i
                max_x = ti.cast(row_max[i, 1], ti.i32)
        
        final_peak[0, 0] = max_val
        final_peak[0, 1] = ti.cast(max_y, ti.f32)
        final_peak[0, 2] = ti.cast(max_x, ti.f32)

@ti_thread
def zncc(image, template):
    """Entry point for ZNCC alignment."""
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.zncc(image, template, return_gpu=True)
    return None

def match_template(image, template, method="zncc"):
    """Compatibility wrapper for OpenCV-style template matching."""
    if method == "zncc":
        return zncc(image, template)
    return None

def global_translate_zncc(image, template):
    """Compatibility wrapper for global translation."""
    return zncc(image, template)

if TAICHI_AVAILABLE:
    class NCC:
        """Wrapper class for AOT compiler."""
        _integral_image_row_scan_kernel = _integral_image_row_scan_kernel
        _integral_image_col_scan_kernel = _integral_image_col_scan_kernel
        _zncc_spatial_kernel = _zncc_spatial_kernel
        _reduce_row_max_kernel = _reduce_row_max_kernel
        _reduce_global_max_kernel = _reduce_global_max_kernel
