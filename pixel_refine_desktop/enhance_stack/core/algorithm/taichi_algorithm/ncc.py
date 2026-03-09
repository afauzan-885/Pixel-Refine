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
    from . import fft
except ImportError:
    TAICHI_AVAILABLE = False


if TAICHI_AVAILABLE:

    @ti.kernel
    def _subtract_mean_kernel(data: ti.types.ndarray(), mean: float):
        for I in ti.grouped(data):
            data[I] -= mean

    @ti.kernel
    def _compute_stats_kernel(data: ti.types.ndarray()) -> tm.vec2:
        """Returns [sum, sum_sq]"""
        s = 0.0
        sq = 0.0
        for I in ti.grouped(data):
            v = data[I]
            s += v
            sq += v * v
        return tm.vec2(s, sq)

    @ti.kernel
    def _complex_mul_conj_kernel(
        a: ti.types.ndarray(), b: ti.types.ndarray(), dst: ti.types.ndarray()
    ):
        for I in ti.grouped(a):
            va = a[I]
            vb = b[I]
            # a * conj(b)
            dst[I] = tm.vec2(va.x * vb.x + va.y * vb.y, va.y * vb.x - va.x * vb.y)

    @ti.kernel
    def _fill_ones_kernel(data: ti.types.ndarray()):
        for I in ti.grouped(data):
            data[I] = 1.0

    @ti.kernel
    def _sq_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
        for I in ti.grouped(src):
            dst[I] = src[I] ** 2

    @ti.kernel
    def _finalize_ncc_kernel(
        num: ti.types.ndarray(),
        sum_i: ti.types.ndarray(),
        sum_sq_i: ti.types.ndarray(),
        std_t_n: float,
        n_comp: float,
        dst: ti.types.ndarray(),
    ):
        for I in ti.grouped(dst):
            s_i = sum_i[I]
            sq_i = sum_sq_i[I]
            # Local variance of image * n_comp
            var_i_n = ti.math.max(0.0, sq_i - (s_i**2 / n_comp))
            std_i_n = ti.math.sqrt(var_i_n)

            denom = std_i_n * std_t_n
            if denom > 1e-10:
                val = num[I] / denom
                dst[I] = tm.clamp(val, -1.0, 1.0)
            else:
                dst[I] = 0.0


@ti_thread
def zncc_fft(ref, comp):
    """
    Local Zero-mean Normalized Cross-Correlation (ZNCC) using FFT.
    Provides robust template matching by normalizing the correlation
    locally at each window position.
    Returns correlation map in range [-1.0, 1.0].
    """
    if not TAICHI_AVAILABLE:
        raise RuntimeError("Taichi not available")

    ref_gpu, ref_temp = common.ensure_taichi_field(ref, dtype=ti.f32)
    comp_gpu, comp_temp = common.ensure_taichi_field(comp, dtype=ti.f32)

    h_ref, w_ref = ref_gpu.shape
    h_comp, w_comp = comp_gpu.shape
    n_comp = float(h_comp * w_comp)

    # 1. Prepare Template (comp): Zero-mean and Unit-norm stats
    stats_comp = _compute_stats_kernel(comp_gpu)
    mean_comp = stats_comp[0] / n_comp
    sum_sq_comp = stats_comp[1]

    # Variance of template * n_comp
    sum_sq_zm_comp = max(0.0, sum_sq_comp - (stats_comp[0] ** 2 / n_comp))
    std_t_n = np.sqrt(sum_sq_zm_comp)

    # Pad zero-mean template to ref size
    comp_zm_padded = common.get_temp_buffer((h_ref, w_ref), ti.f32)
    comp_zm_local = common.get_temp_buffer((h_comp, w_comp), ti.f32)
    common.copy_field(comp_gpu, comp_zm_local)
    _subtract_mean_kernel(comp_zm_local, mean_comp)
    common.copy_field(comp_zm_local, comp_zm_padded)
    common.release_temp_buffer(comp_zm_local)

    # 2. Compute Numerator: I * T_zm (FFT Correlation)
    F_ref = fft.fft2(ref_gpu)
    F_comp_zm = fft.fft2(comp_zm_padded)
    common.release_temp_buffer(comp_zm_padded)

    pad_h, pad_w = F_ref.shape
    R_num = common.get_temp_buffer((pad_h, pad_w), ti.types.vector(2, ti.f32))
    _complex_mul_conj_kernel(F_ref, F_comp_zm, R_num)
    common.release_temp_buffer(F_comp_zm)

    num_field = fft.ifft2(R_num, target_shape=(h_ref, w_ref))
    common.release_temp_buffer(R_num)

    # 3. Compute Local Image Normalization (Denominator) via FFT Box Sums
    # 3a. FFT of Ones
    ones_padded = common.get_temp_buffer((h_ref, w_ref), ti.f32)
    ones_local = common.get_temp_buffer((h_comp, w_comp), ti.f32)
    _fill_ones_kernel(ones_local)
    common.copy_field(ones_local, ones_padded)
    common.release_temp_buffer(ones_local)

    F_ones = fft.fft2(ones_padded)
    common.release_temp_buffer(ones_padded)

    # 3b. Local Sum(I): I * Ones
    R_sum = common.get_temp_buffer((pad_h, pad_w), ti.types.vector(2, ti.f32))
    _complex_mul_conj_kernel(F_ref, F_ones, R_sum)
    sum_i_field = fft.ifft2(R_sum, target_shape=(h_ref, w_ref))
    common.release_temp_buffer(R_sum)
    common.release_temp_buffer(F_ref)

    # 3c. Local Sum(I^2): I^2 * Ones
    img_sq = common.get_temp_buffer((h_ref, w_ref), ti.f32)
    _sq_kernel(ref_gpu, img_sq)
    F_ref_sq = fft.fft2(img_sq)
    common.release_temp_buffer(img_sq)

    R_sum_sq = common.get_temp_buffer((pad_h, pad_w), ti.types.vector(2, ti.f32))
    _complex_mul_conj_kernel(F_ref_sq, F_ones, R_sum_sq)
    sum_sq_i_field = fft.ifft2(R_sum_sq, target_shape=(h_ref, w_ref))

    common.release_temp_buffer(R_sum_sq)
    common.release_temp_buffer(F_ones)
    common.release_temp_buffer(F_ref_sq)

    # 4. Final Normalization Kernel
    res_field = common.get_temp_buffer((h_ref, w_ref), ti.f32)
    _finalize_ncc_kernel(
        num_field, sum_i_field, sum_sq_i_field, float(std_t_n), n_comp, res_field
    )

    res_np = res_field.to_numpy()

    # Cleanup
    common.release_temp_buffer(num_field)
    common.release_temp_buffer(sum_i_field)
    common.release_temp_buffer(sum_sq_i_field)
    common.release_temp_buffer(res_field)

    if ref_temp:
        common.release_temp_buffer(ref_gpu)
    if comp_temp:
        common.release_temp_buffer(comp_gpu)

    return res_np


@ti_thread
def match_template_fft(image, template):
    """
    Standard Template Matching via FFT.
    Returns a correlation map of the same size as 'image'.
    Optimized for wide-range pattern searching.
    """
    return zncc_fft(image, template)
