"""Taichi kernels for weighted HDR using scalar flat RGB buffers."""

import taichi as ti


@ti.kernel
def hdr_weight_rgb_flat_f32(
    img_rgb: ti.types.ndarray(ti.f32, ndim=1),
    lap_gray: ti.types.ndarray(ti.f32, ndim=2),
    weight: ti.types.ndarray(ti.f32, ndim=2),
    h: ti.i32,
    w: ti.i32,
    noise_sigma: ti.f32,
    noise_power: ti.f32,
    exposure_sigma: ti.f32,
    exposure_power: ti.f32,
    detail_power: ti.f32,
    saturation_power: ti.f32,
):
    """Compute exposure, SNR, detail and saturation weights per pixel."""
    for y, x in ti.ndrange(h, w):
        base = (y * w + x) * 3
        r_val = img_rgb[base]
        g_val = img_rgb[base + 1]
        b_val = img_rgb[base + 2]
        luma = 0.299 * r_val + 0.587 * g_val + 0.114 * b_val
        snr = luma / ti.max(noise_sigma, 1e-6)
        w_noise = ti.pow(snr / (snr + 0.5), noise_power)
        denom = 2.0 * exposure_sigma * exposure_sigma
        w_exp_r = ti.exp(-ti.pow(r_val - 0.5, 2) / denom)
        w_exp_g = ti.exp(-ti.pow(g_val - 0.5, 2) / denom)
        w_exp_b = ti.exp(-ti.pow(b_val - 0.5, 2) / denom)
        w_exposure = ti.pow(w_exp_r * w_exp_g * w_exp_b, exposure_power / 3.0)
        w_contrast = ti.pow(ti.abs(lap_gray[y, x]) + 1e-6, detail_power)
        mean_rgb = (r_val + g_val + b_val) / 3.0
        sat = ti.sqrt(
            (r_val - mean_rgb) ** 2
            + (g_val - mean_rgb) ** 2
            + (b_val - mean_rgb) ** 2
        ) / 3.0
        w_sat = ti.pow(sat + 1e-6, saturation_power)
        weight[y, x] = w_noise * w_exposure * w_contrast * w_sat


@ti.kernel
def accumulate_weighted_rgb_flat_f32(
    lap_rgb: ti.types.ndarray(ti.f32, ndim=1),
    weight: ti.types.ndarray(ti.f32, ndim=2),
    result: ti.types.ndarray(ti.f32, ndim=1),
    h: ti.i32,
    w: ti.i32,
):
    """Accumulate an RGB frame without vector-field shape metadata."""
    for y, x, channel in ti.ndrange(h, w, 3):
        index = (y * w + x) * 3 + channel
        result[index] += lap_rgb[index] * weight[y, x]


__all__ = ["hdr_weight_rgb_flat_f32", "accumulate_weighted_rgb_flat_f32"]
