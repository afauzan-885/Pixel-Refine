"""
Normalized Cross-Correlation (NCC) via FFT - Taichi GPU Implementation
======================================================================
Provides high-performance correlation functions for pattern matching,
feature tracking, and general signal analysis using FFT backend.
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
    def _compute_zncc_map_kernel(
        image: ti.types.ndarray(),
        template: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_img: int,
        w_img: int,
        h_temp: int,
        w_temp: int,
    ):
        """
        Computes a full ZNCC correlation map in spatial domain.
        Formula: sum((I - mean_I) * (T - mean_T)) / (std_I * std_T * N)
        Result is in range [-1.0, 1.0].
        """
        # Pre-compute template stats once
        sum_t = 0.0
        sum_sq_t = 0.0
        n = float(h_temp * w_temp)
        for i, j in ti.ndrange(h_temp, w_temp):
            val = float(template[i, j])
            sum_t += val
            sum_sq_t += val * val
        
        mean_t = sum_t / n
        std_t_n = ti.sqrt(ti.max(0.0, sum_sq_t - (sum_t**2 / n)))

        # Slide over image
        for y, x in ti.ndrange(h_img - h_temp + 1, w_img - w_temp + 1):
            sum_i = 0.0
            sum_sq_i = 0.0
            sum_it = 0.0

            for i, j in ti.ndrange(h_temp, w_temp):
                val_i = float(image[y + i, x + j])
                val_t = float(template[i, j])
                
                sum_i += val_i
                sum_sq_i += val_i * val_i
                sum_it += val_i * val_t

            # ZNCC Numerator: sum(I*T) - (sum_I * sum_T / N)
            numerator = sum_it - (sum_i * sum_t / n)
            
            # Local variance of image window
            var_i_n = ti.max(0.0, sum_sq_i - (sum_i**2 / n))
            denominator = ti.sqrt(var_i_n * std_t_n**2)

            if denominator > 1e-10:
                dst[y, x] = tm.clamp(numerator / denominator, -1.0, 1.0)
            else:
                dst[y, x] = 0.0

    @ti.kernel
    def _compute_global_zncc_surface(
        ref: ti.types.ndarray(dtype=ti.f32, ndim=2),
        comp: ti.types.ndarray(dtype=ti.f32, ndim=2),
        cost_surface: ti.types.ndarray(dtype=ti.f32, ndim=2),
        max_shift: int,
        h: int,
        w: int,
    ):
        """
        Computes the ZNCC (Zero-mean Normalized Cross-Correlation) cost across a shift grid.
        Identical to older implementation for global motion estimation.
        """
        for dy, dx in ti.ndrange(
            (-max_shift, max_shift + 1), (-max_shift, max_shift + 1)
        ):
            # Pass 1: Calculate Means
            sum_ref = 0.0
            sum_comp = 0.0
            count = 0.0

            for y in range(max_shift, h - max_shift):
                for x in range(max_shift, w - max_shift):
                    comp_y = y + dy
                    comp_x = x + dx

                    sum_ref += float(ref[y, x])
                    sum_comp += float(comp[comp_y, comp_x])
                    count += 1.0

            if count > 0.0:
                mean_ref = sum_ref / count
                mean_comp = sum_comp / count

                # Pass 2: Calculate ZNCC
                numerator = 0.0
                sum_sq_ref = 0.0
                sum_sq_comp = 0.0

                for y in range(max_shift, h - max_shift):
                    for x in range(max_shift, w - max_shift):
                        comp_y = y + dy
                        comp_x = x + dx

                        val_ref = float(ref[y, x]) - mean_ref
                        val_comp = float(comp[comp_y, comp_x]) - mean_comp

                        numerator += val_ref * val_comp
                        sum_sq_ref += val_ref * val_ref
                        sum_sq_comp += val_comp * val_comp

                denominator = ti.sqrt(sum_sq_ref * sum_sq_comp)

                if denominator > 1e-6:
                    zncc = numerator / denominator
                    cost_surface[dy + max_shift, dx + max_shift] = 1.0 - zncc
                else:
                    cost_surface[dy + max_shift, dx + max_shift] = 1e10
            else:
                cost_surface[dy + max_shift, dx + max_shift] = 1e10


@ti_thread
def zncc(image, template):
    """
    Zero-mean Normalized Cross-Correlation (ZNCC) - Spatial Version.
    Exact sliding window implementation (Non-FFT).
    """
    if not TAICHI_AVAILABLE:
        raise RuntimeError("Taichi not available")

    img_gpu, img_temp = common.ensure_taichi_field(image, dtype=ti.f32)
    temp_gpu, temp_temp = common.ensure_taichi_field(template, dtype=ti.f32)

    h_img, w_img = img_gpu.shape[:2]
    h_temp, w_temp = temp_gpu.shape[:2]

    # Result size: (H_img - H_temp + 1, W_img - W_temp + 1)
    res_h = h_img - h_temp + 1
    res_w = w_img - w_temp + 1
    
    if res_h <= 0 or res_w <= 0:
        raise ValueError("Template larger than image")

    res_field = common.get_temp_buffer((res_h, res_w), ti.f32)
    res_field.fill(0.0)

    _compute_zncc_map_kernel(
        img_gpu, temp_gpu, res_field, h_img, w_img, h_temp, w_temp
    )

    res_np = res_field.to_numpy()

    # Cleanup
    common.release_temp_buffer(res_field)
    if img_temp: common.release_temp_buffer(img_gpu)
    if temp_temp: common.release_temp_buffer(temp_gpu)

    return res_np


@ti_thread
def global_translate_zncc(ref, comp, max_shift=16):
    """
    Estimates the dominant global translation (dx, dy) between two 2D images.
    Uses spatial ZNCC for extreme robustness on coarsest layers.
    """
    if not TAICHI_AVAILABLE:
        raise RuntimeError("Taichi not available")

    ref_gpu, ref_temp = common.ensure_taichi_field(ref, dtype=ti.f32)
    comp_gpu, comp_temp = common.ensure_taichi_field(comp, dtype=ti.f32)

    h, w = ref_gpu.shape[:2]
    # Prevent empty valid region on very small coarse layers.
    safe_shift = int(
        min(
            int(max_shift),
            max(0, (int(h) - 1) // 2),
            max(0, (int(w) - 1) // 2),
        )
    )
    if safe_shift <= 0:
        if ref_temp:
            common.release_temp_buffer(ref_gpu)
        if comp_temp:
            common.release_temp_buffer(comp_gpu)
        return 0, 0, 1e10

    size = 2 * safe_shift + 1
    cost_surface = common.get_temp_buffer((size, size), ti.f32)
    cost_surface.fill(1e10)

    _compute_global_zncc_surface(ref_gpu, comp_gpu, cost_surface, safe_shift, h, w)

    surface_np = cost_surface.to_numpy()
    min_idx = np.unravel_index(np.argmin(surface_np), surface_np.shape)

    best_dy = int(min_idx[0]) - safe_shift
    best_dx = int(min_idx[1]) - safe_shift
    best_cost = float(surface_np[min_idx[0], min_idx[1]])

    common.release_temp_buffer(cost_surface)
    if ref_temp: common.release_temp_buffer(ref_gpu)
    if comp_temp: common.release_temp_buffer(comp_gpu)

    return best_dx, best_dy, best_cost


def match_template(image, template):
    """
    Standard Template Matching via Spatial ZNCC.
    Replaces older match_template_fft.
    """
    return zncc(image, template)
