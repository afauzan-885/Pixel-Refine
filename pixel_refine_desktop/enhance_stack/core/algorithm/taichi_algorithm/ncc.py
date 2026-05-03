# Marker: GPU_NATIVE_MARKER_V3
"""
Normalized Cross-Correlation (NCC) - Taichi GPU Implementation
==============================================================
Provides high-performance correlation functions using FFT + Integral Image.
"""

import numpy as np
import os

try:
    import taichi as ti
    import taichi.math as tm
    from .taichi_worker import ti_thread, TAICHI_AVAILABLE
    from . import common
    from . import fft
    from . import box_filter
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
    def _assemble_zncc_fft_kernel(
        corr_fft: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sum_img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sq_sum_img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sum_t: float,
        var_t_n: float,
        n: float,
        h_temp: int,
        w_temp: int
    ):
        """
        Final ZNCC Assembly from FFT Correlation and Integral Image Stats.
        Handles the normalization: (Corr - MeanI*MeanT) / (StdI * StdT)
        """
        for y, x in ti.ndrange(dst.shape[0], dst.shape[1]):
            # Region coordinates for local stats
            y1, x1 = y - 1, x - 1
            y2, x2 = y + h_temp - 1, x + w_temp - 1
            
            # Local Sum and Sum Squares from Integral Image
            s_i = sum_img[y2, x2]
            if y1 >= 0: s_i -= sum_img[y1, x2]
            if x1 >= 0: s_i -= sum_img[y2, x1]
            if y1 >= 0 and x1 >= 0: s_i += sum_img[y1, x1]

            s_sq_i = sq_sum_img[y2, x2]
            if y1 >= 0: s_sq_i -= sq_sum_img[y1, x2]
            if x1 >= 0: s_sq_i -= sq_sum_img[y2, x1]
            if y1 >= 0 and x1 >= 0: s_sq_i += sq_sum_img[y1, x1]
            
            # Numerator: Raw Correlation - Mean Correction
            # The FFT correlation at (y,x) corresponds to the sum of products
            raw_corr = corr_fft[y + h_temp - 1, x + w_temp - 1]
            numerator = raw_corr - (s_i * sum_t / n)
            
            # Denominator: Local Standard Deviation product
            v_i_n = ti.max(0.0, s_sq_i - (s_i**2 / n))
            denominator = ti.sqrt(ti.max(1e-12, v_i_n * var_t_n))
            
            dst[y, x] = tm.clamp(numerator / denominator, -1.0, 1.0)
            
    @ti.kernel
    def _zncc_spatial_kernel(
        img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        template: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sum_img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sq_sum_img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sum_t: float,
        var_t_n: float,
        n: float,
        offset_y: int,
        offset_x: int,
        stride: int
    ):
        """
        Spatial ZNCC with ROI and Stride support.
        Used for fast multi-scale / coarse-to-fine searching.
        """
        h_t, w_t = template.shape[0], template.shape[1]
        for y, x in ti.ndrange(dst.shape[0], dst.shape[1]):
            # 1. Coordinate Mapping
            base_y = offset_y + y * stride
            base_x = offset_x + x * stride
            
            # 2. Local Denominator (O(1))
            y1, x1 = base_y - 1, base_x - 1
            y2, x2 = base_y + h_t - 1, base_x + w_t - 1
            
            s_i = sum_img[y2, x2]
            if y1 >= 0: s_i -= sum_img[y1, x2]
            if x1 >= 0: s_i -= sum_img[y2, x1]
            if y1 >= 0 and x1 >= 0: s_i += sum_img[y1, x1]

            s_sq_i = sq_sum_img[y2, x2]
            if y1 >= 0: s_sq_i -= sq_sum_img[y1, x2]
            if x1 >= 0: s_sq_i -= sq_sum_img[y2, x1]
            if y1 >= 0 and x1 >= 0: s_sq_i += sq_sum_img[y1, x1]

            # 3. Local Numerator (O(M))
            corr = 0.0
            for i, j in ti.ndrange(h_t, w_t):
                corr += img[base_y + i, base_x + j] * template[i, j]
            
            numerator = corr - (s_i * sum_t / n)
            v_i_n = ti.max(0.0, s_sq_i - (s_i**2 / n))
            denominator = ti.sqrt(ti.max(1e-12, v_i_n * var_t_n))
            
            dst[y, x] = tm.clamp(numerator / denominator, -1.0, 1.0)

    @ti.kernel
    def _reduce_row_max_kernel(
        res: ti.types.ndarray(dtype=ti.f32, ndim=2),
        row_max: ti.types.ndarray(dtype=ti.f32, ndim=2), # (H, 2) [val, x]
    ):
        """Pass 1: Find max of each row in parallel."""
        for i in range(res.shape[0]):
            max_val = -1e10
            max_x = 0
            for j in range(res.shape[1]):
                val = res[i, j]
                if val > max_val:
                    max_val = val
                    max_x = j
            row_max[i, 0] = max_val
            row_max[i, 1] = ti.cast(max_x, ti.f32)

    @ti.kernel
    def _reduce_global_max_kernel(
        row_max: ti.types.ndarray(dtype=ti.f32, ndim=2),
        final_peak: ti.types.ndarray(dtype=ti.f32, ndim=2), # (1, 3) [val, y, x]
    ):
        """Pass 2: Find global max from row results."""
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

    @ti.kernel
    def _zncc_spatial_refine_kernel(
        img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        template: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sum_img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        sq_sum_img: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        peak_info: ti.types.ndarray(dtype=ti.f32, ndim=2), # (1, 3) [val, y, x]
        sum_t: float,
        var_t_n: float,
        n: float,
        stride: int
    ):
        """Refinement pass: Reads coarse peak from peak_info and searches locally."""
        h_t, w_t = template.shape[0], template.shape[1]
        py_c = ti.cast(peak_info[0, 1], ti.i32)
        px_c = ti.cast(peak_info[0, 2], ti.i32)
        
        # Calculate ROI start (same logic as Python version)
        refine_radius = stride
        py_start = ti.max(0, py_c * stride - refine_radius)
        px_start = ti.max(0, px_c * stride - refine_radius)
        
        for y, x in ti.ndrange(dst.shape[0], dst.shape[1]):
            base_y = py_start + y
            base_x = px_start + x
            
            # Local Denominator (O(1))
            y1, x1 = base_y - 1, base_x - 1
            y2, x2 = base_y + h_t - 1, base_x + w_t - 1
            
            s_i = sum_img[y2, x2]
            if y1 >= 0: s_i -= sum_img[y1, x2]
            if x1 >= 0: s_i -= sum_img[y2, x1]
            if y1 >= 0 and x1 >= 0: s_i += sum_img[y1, x1]

            s_sq_i = sq_sum_img[y2, x2]
            if y1 >= 0: s_sq_i -= sq_sum_img[y1, x2]
            if x1 >= 0: s_sq_i -= sq_sum_img[y2, x1]
            if y1 >= 0 and x1 >= 0: s_sq_i += sq_sum_img[y1, x1]

            # Local Numerator (O(M))
            corr = 0.0
            for i, j in ti.ndrange(h_t, w_t):
                corr += img[base_y + i, base_x + j] * template[i, j]
            
            numerator = corr - (s_i * sum_t / n)
            v_i_n = ti.max(0.0, s_sq_i - (s_i**2 / n))
            denominator = ti.sqrt(ti.max(1e-12, v_i_n * var_t_n))
            
            dst[y, x] = tm.clamp(numerator / denominator, -1.0, 1.0)



@ti_thread
def zncc(image, template):
    """
    True NCC via Hybrid FFT + Integral Image.
    Complexity: O(N log N) - independent of template size.
    """
    # --- AOT ROUTING ---
    if os.environ.get("PIXEL_REFINE_AOT_MODE") == "1":
        from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot
        return taichi_aot.zncc(image, template, return_gpu=True)

    img_gpu, img_temp = common.ensure_taichi_field(image, dtype=ti.f32)
    temp_gpu, temp_temp = common.ensure_taichi_field(template, dtype=ti.f32)
    
    h_img, w_img = img_gpu.shape[:2]
    h_temp, w_temp = temp_gpu.shape[:2]
    
    # 1. FFT Correlation (Numerator part)
    # Pad to power of 2 for Stockham FFT
    target_h = fft._next_power_of_two(h_img + h_temp - 1)
    target_w = fft._next_power_of_two(w_img + w_temp - 1)
    
    # FFT of Image
    img_complex = common.get_temp_buffer((target_h, target_w), ti.types.vector(2, ti.f32))
    fft._real_to_complex_kernel(img_gpu, img_complex, h_img, w_img)
    fft.fft_1d_gpu(img_complex, is_inverse=False, is_col=False)
    fft.fft_1d_gpu(img_complex, is_inverse=False, is_col=True)
    
    # FFT of Template (Padded to same size)
    temp_complex = common.get_temp_buffer((target_h, target_w), ti.types.vector(2, ti.f32))
    fft._real_to_complex_kernel(temp_gpu, temp_complex, h_temp, w_temp)
    fft.fft_1d_gpu(temp_complex, is_inverse=False, is_col=False)
    fft.fft_1d_gpu(temp_complex, is_inverse=False, is_col=True)
    
    # Pointwise Multiply (Complex Conjugate for Correlation)
    corr_complex = common.get_temp_buffer((target_h, target_w), ti.types.vector(2, ti.f32))
    fft._complex_mul_kernel(img_complex, temp_complex, corr_complex, conj_b=1)
    
    # Inverse FFT
    fft.fft_1d_gpu(corr_complex, is_inverse=True, is_col=True)
    fft.fft_1d_gpu(corr_complex, is_inverse=True, is_col=False)
    
    # Convert to Real Correlation Surface
    corr_real = common.get_temp_buffer((target_h, target_w), ti.f32)
    fft._complex_to_real_kernel(corr_complex, corr_real, target_h, target_w)
    
    # 2. Integral Image (Denominator part)
    sum_h = common.get_temp_buffer((h_img, w_img), ti.f32)
    sq_sum_h = common.get_temp_buffer((h_img, w_img), ti.f32)
    sum_2d = common.get_temp_buffer((h_img, w_img), ti.f32)
    sq_sum_2d = common.get_temp_buffer((h_img, w_img), ti.f32)
    
    _integral_image_row_scan_kernel(img_gpu, sum_h, sq_sum_h, h_img, w_img)
    _integral_image_col_scan_kernel(sum_h, sq_sum_h, sum_2d, sq_sum_2d, h_img, w_img)
    
    # 3. Final Assembly
    res_h, res_w = h_img - h_temp + 1, w_img - w_temp + 1
    res_field = common.get_temp_buffer((res_h, res_w), ti.f32)
    
    temp_np = template if isinstance(template, np.ndarray) else template.to_numpy()
    sum_t = float(np.sum(temp_np))
    n = float(h_temp * w_temp)
    var_t_n = float(np.sum(temp_np**2) - (sum_t**2 / n))
    
    _assemble_zncc_fft_kernel(corr_real, sum_2d, sq_sum_2d, res_field, sum_t, var_t_n, n, h_temp, w_temp)
    
    # Cleanup
    for f in [img_complex, temp_complex, corr_complex, corr_real, sum_h, sq_sum_h, sum_2d, sq_sum_2d]:
        common.release_temp_buffer(f)
    if img_temp: common.release_temp_buffer(img_gpu)
    if temp_temp: common.release_temp_buffer(temp_gpu)
    
    return common.to_numpy_if_needed(res_field, True)

def match_template(image, template):
    """Alias for zncc."""
    return zncc(image, template)

@ti_thread
def global_translate_zncc(image, template):
    """Computes the global translation vector using ZNCC surface peak."""
    res = zncc(image, template)
    h_res, w_res = res.shape
    
    # Simple argmax in Python for now (peak finding)
    idx = np.argmax(res)
    py, px = np.unravel_index(idx, res.shape)
    
    return float(px), float(py), float(res[py, px])
