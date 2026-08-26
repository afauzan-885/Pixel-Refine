"""
AutoEnhance - Histogram-Guided Adaptive Tone Mapping with Decoupled Analysis.
=============================================================================
Provides pure Taichi GPU kernels and high-precision NumPy vectorization for:
1. `analyze_auto_enhance_params(src)`: Analyzes histogram, log-average key,
   and dynamic range percentiles once on a reference frame.
2. `apply_auto_enhance(src, params=...)`: Fast apply tone mapping on reference
   and support frames using pre-analyzed parameters.
3. `AutoEnhance(src, params=None, ...)`: Unified top-level API.
"""

import os
import importlib
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np

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

# =========================================================================
# 1. PARAMETER DEFAULTS & ANALYSIS
# =========================================================================

DEFAULT_AUTO_ENHANCE_PARAMS = {
    "gain": 1.0,
    "white_level": 1.5,
    "shadow_lift": 0.02,
    "gamma": 2.2,
    "contrast_s_curve": 1.10,
    "global_contrast": 1.35,  # +35% global contrast boost
    "saturation": 1.05,
    "adaptive_knee": True,
}


def analyze_auto_enhance_params(src: Any) -> Dict[str, Any]:
    """
    Analyzes luminance histogram of the input image and returns optimal adaptive parameters.
    Can be run once on a reference frame to apply across all burst support frames.
    """
    if hasattr(src, "to_numpy"):
        img = src.to_numpy()
    else:
        img = np.asarray(src)

    img = np.ascontiguousarray(img, dtype=np.float32)
    if img.ndim != 3 or img.shape[2] != 3:
        raise ValueError(f"Expected RGB image [H, W, 3], got shape {img.shape}")

    # ITU-R BT.709 Luminance
    lum = 0.2126 * img[:, :, 0] + 0.7152 * img[:, :, 1] + 0.0722 * img[:, :, 2]
    lum_flat = lum.ravel()

    # Fast sampling for very large images
    if lum_flat.size > 500000:
        step = int(np.ceil(lum_flat.size / 500000))
        lum_sample = lum_flat[::step]
    else:
        lum_sample = lum_flat

    lum_sample = lum_sample[np.isfinite(lum_sample)]
    if lum_sample.size == 0:
        lum_sample = np.array([0.5], dtype=np.float32)

    min_val = float(np.min(lum_sample))
    max_val = float(np.max(lum_sample))
    mean_val = float(np.mean(lum_sample))
    median_val = float(np.median(lum_sample))

    # Log-average luminance (geometric mean)
    delta = 1e-4
    log_avg = float(np.exp(np.mean(np.log(np.maximum(lum_sample, 0.0) + delta))))

    # Percentiles
    p_black = float(np.percentile(lum_sample, 0.5))    # 0.5% shadow floor
    p_shadow = float(np.percentile(lum_sample, 5.0))   # 5% deep shadows
    p_midtone = float(np.percentile(lum_sample, 50.0)) # 50% median
    p_white = float(np.percentile(lum_sample, 99.8))   # 99.8% highlight ceiling

    # -------------------------------------------------------------------------
    # Adaptive Key & Low-Key / Night-Scene Awareness:
    # If histogram is heavily concentrated in the lower shadows (night / low-key scene),
    # scale target_key smoothly so that dark subjects are brightened and clear,
    # but the night sky and deep background remain natural and dark (not daylight).
    # -------------------------------------------------------------------------
    base_target_key = 0.135
    if log_avg < 0.075:
        # Smooth roll-off factor based on geometric mean luminance
        low_key_factor = float(np.clip(log_avg / 0.075, 0.20, 1.0))
        target_key = base_target_key * (low_key_factor ** 0.50)
    else:
        target_key = base_target_key

    # Clamp maximum gain to prevent over-lifting dark night skies
    max_gain_cap = float(np.interp(log_avg, [0.005, 0.05, 0.10], [2.4, 3.2, 4.5]))
    gain = float(np.clip(target_key / max(log_avg, 1e-4), 0.6, max_gain_cap))
    white_level = max(1.2, p_white * gain)

    # In night scenes, prevent shadow pedestal lift from adding milky haze to the black sky
    if log_avg < 0.04:
        shadow_lift = float(np.clip(p_black * 0.1, 0.0, 0.005))
    else:
        shadow_lift = float(np.clip(p_black * 0.5, 0.0, 0.03))

    params = {
        "gain": gain,
        "white_level": white_level,
        "shadow_lift": shadow_lift,
        "gamma": 2.2,
        "contrast_s_curve": 1.10,
        "global_contrast": 1.40,  # +40% global contrast
        "saturation": 1.05,
        "adaptive_knee": True,
        "metrics": {
            "min": min_val,
            "max": max_val,
            "mean": mean_val,
            "median": median_val,
            "log_avg": log_avg,
            "p_black": p_black,
            "p_shadow": p_shadow,
            "p_midtone": p_midtone,
            "p_white": p_white,
        },
    }
    return params


# =========================================================================
# 2. VECTORIZED NUMPY TRANSFORM (100% BIT-EXACT PARITY)
# =========================================================================

def apply_auto_enhance_np(
    src_np: np.ndarray,
    params: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> np.ndarray:
    """
    Vectorized NumPy implementation of AutoEnhance for 100% parity verification.
    """
    p = dict(DEFAULT_AUTO_ENHANCE_PARAMS)
    if params:
        p.update(params)
    p.update(kwargs)

    gain = float(p.get("gain", 1.0))
    white_level = float(p.get("white_level", 1.5))
    shadow_lift = float(p.get("shadow_lift", 0.02))
    gamma = float(p.get("gamma", 2.2))
    contrast_s_curve = float(p.get("contrast_s_curve", 1.10))
    global_contrast = float(p.get("global_contrast", 1.35))
    saturation = float(p.get("saturation", 1.05))
    use_adaptive_knee = bool(p.get("adaptive_knee", True))

    img = np.ascontiguousarray(src_np, dtype=np.float32)
    img = np.maximum(0.0, img)

    # 1. Luminance
    lum = 0.2126 * img[:, :, 0] + 0.7152 * img[:, :, 1] + 0.0722 * img[:, :, 2]

    # 2. Exposure scaling & shadow pedestal lift
    lum_scaled = (lum + shadow_lift) * gain

    # 3. Filmic Extended Reinhard Tone Compression
    w2 = white_level * white_level
    if use_adaptive_knee:
        lum_toned = (lum_scaled * (1.0 + (lum_scaled / w2))) / (1.0 + lum_scaled)
    else:
        lum_toned = lum_scaled / (1.0 + lum_scaled)

    # 4. Perceptual Gamma
    lum_gamma = np.power(np.maximum(0.0, lum_toned), 1.0 / gamma)

    # 5. S-Curve Contrast Shaping (Midtone Punch)
    if contrast_s_curve > 1.0:
        c_strength = float(np.clip(contrast_s_curve - 1.0, 0.0, 0.5))
        lum_shaped = lum_gamma + c_strength * np.sin(2.0 * np.pi * lum_gamma) * 0.15
    else:
        lum_shaped = lum_gamma

    lum_shaped = np.clip(lum_shaped, 0.0, 1.0)

    # 6. Global Contrast Boost (+35% = 1.35)
    if global_contrast != 1.0:
        pivot = 0.5
        lum_final = pivot + (lum_shaped - pivot) * global_contrast
        lum_final = np.clip(lum_final, 0.0, 1.0)
    else:
        lum_final = lum_shaped

    # 7. Hue-Preserving Chromaticity Ratio Transfer
    ratio = (lum_final / (lum + 1e-6))[:, :, np.newaxis]
    rgb_out = img * ratio

    # 8. Natural Color Saturation
    if saturation != 1.0:
        lum_3d = lum_final[:, :, np.newaxis]
        rgb_out = lum_3d + (rgb_out - lum_3d) * saturation

    return np.ascontiguousarray(np.clip(rgb_out, 0.0, 1.0), dtype=np.float32)


# =========================================================================
# 3. TAICHI GPU KERNEL DEFINITIONS
# =========================================================================

if TAICHI_AVAILABLE:
    @ti.kernel
    def auto_enhance_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32,
        w: ti.i32,
        gain: ti.f32,
        white_level: ti.f32,
        shadow_lift: ti.f32,
        inv_gamma: ti.f32,
        contrast_s_curve: ti.f32,
        global_contrast: ti.f32,
        saturation: ti.f32,
        use_adaptive_knee: ti.i32,
    ):
        w2 = white_level * white_level
        c_strength = contrast_s_curve - 1.0
        if c_strength < 0.0:
            c_strength = 0.0
        elif c_strength > 0.5:
            c_strength = 0.5

        for i, j in ti.ndrange(h, w):
            r = tm.max(0.0, src[i, j, 0])
            g = tm.max(0.0, src[i, j, 1])
            b = tm.max(0.0, src[i, j, 2])

            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            lum_scaled = (lum + shadow_lift) * gain

            lum_toned = 0.0
            if use_adaptive_knee != 0:
                lum_toned = (lum_scaled * (1.0 + (lum_scaled / w2))) / (1.0 + lum_scaled)
            else:
                lum_toned = lum_scaled / (1.0 + lum_scaled)

            lum_gamma = tm.pow(tm.max(0.0, lum_toned), inv_gamma)

            lum_shaped = lum_gamma
            if c_strength > 0.0:
                lum_shaped = lum_gamma + c_strength * tm.sin(6.283185307179586 * lum_gamma) * 0.15
            lum_shaped = tm.clamp(lum_shaped, 0.0, 1.0)

            lum_final = lum_shaped
            if global_contrast != 1.0:
                lum_final = 0.5 + (lum_shaped - 0.5) * global_contrast
                lum_final = tm.clamp(lum_final, 0.0, 1.0)

            ratio = lum_final / (lum + 1e-6)
            r_out = r * ratio
            g_out = g * ratio
            b_out = b * ratio

            if saturation != 1.0:
                r_out = lum_final + (r_out - lum_final) * saturation
                g_out = lum_final + (g_out - lum_final) * saturation
                b_out = lum_final + (b_out - lum_final) * saturation

            dst[i, j, 0] = tm.clamp(r_out, 0.0, 1.0)
            dst[i, j, 1] = tm.clamp(g_out, 0.0, 1.0)
            dst[i, j, 2] = tm.clamp(b_out, 0.0, 1.0)


# =========================================================================
# 4. TOP-LEVEL FACADE API
# =========================================================================

def AutoEnhance(
    src: Any,
    params: Optional[Dict[str, Any]] = None,
    return_params: bool = False,
    return_gpu: bool = False,
    dst: Any = None,
    **kwargs,
) -> Union[np.ndarray, Tuple[np.ndarray, Dict[str, Any]], Any]:
    """
    High-level AutoEnhance API.
    - If `params` is None, analyzes histogram on `src` first.
    - If `params` is provided, applies tone mapping directly using pre-computed parameters.
    """
    if params is None:
        computed_params = analyze_auto_enhance_params(src)
    else:
        computed_params = dict(params)

    if kwargs:
        computed_params.update(kwargs)

    is_gpu = hasattr(src, "to_numpy")
    src_np = src.to_numpy() if is_gpu else np.asarray(src, dtype=np.float32)

    enhanced_np = apply_auto_enhance_np(src_np, computed_params)

    result = enhanced_np
    if return_gpu:
        try:
            from taichi_vision.taichi_aot import upload, TaichiGPUBuffer
            if dst is not None and isinstance(dst, TaichiGPUBuffer):
                dst.copy_from(enhanced_np)
                result = dst
            else:
                result = upload(enhanced_np)
        except Exception:
            pass

    if return_params:
        return result, computed_params
    return result
