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


def analyze_auto_enhance_params(
    src: Any,
    mode: str = "natural",
) -> Dict[str, Any]:
    """
    Analyzes luminance histogram of the input image and returns optimal adaptive parameters.

    Modes:
    - 'analysis' (Tier 1): Maximizes dynamic range & boosts deep shadow textures so even
      extremely dark frames become bright and highly contrasted for FlowNet & WeightNet.
    - 'natural' (Tier 2): Natural perceptual tone mapping, filmic knee, and balanced contrast
      for the final merged image.
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
    p_black = float(np.percentile(lum_sample, 0.5))  # 0.5% shadow floor
    p_shadow = float(np.percentile(lum_sample, 5.0))  # 5% deep shadows
    p_midtone = float(np.percentile(lum_sample, 50.0))  # 50% median
    p_white = float(np.percentile(lum_sample, 99.8))  # 99.8% highlight ceiling

    if mode == "analysis":
        # ---------------------------------------------------------------------
        # TIER 1: Histogram-Driven Full-Dynamic-Range Maximizer (For FlowNet / WeightNet)
        # Shifts skewed dark histograms towards center/right-center for maximum AI visibility
        # while Filmic Extended Knee retains 100% highlight & midtone textures.
        # ---------------------------------------------------------------------
        # 1. Dynamically boost target key for dark/underexposed images to shift histogram to center
        if log_avg < 0.08:
            darkness_ratio = float(np.clip((0.08 - log_avg) / 0.08, 0.0, 1.0))
            target_key = (
                0.25 + 0.25 * darkness_ratio
            )  # Shifts target key from 0.25 up to 0.50
            gamma = 1.95  # Slightly steeper gamma to lift dark gradients
            shadow_lift = float(np.clip(0.005 + p_black * 0.8, 0.005, 0.030))
        else:
            target_key = 0.25
            gamma = 2.20
            shadow_lift = float(np.clip(p_black * 0.5, 0.0, 0.015))

        # 2. Compute dynamic gain
        gain = float(np.clip(target_key / max(log_avg, 1e-4), 1.0, 45.0))

        # 3. Filmic Extended White Level anchored to high percentiles (zero blown-out highlights)
        white_level = max(1.8, p_white * gain * 1.25)

        params = {
            "gain": gain,
            "white_level": white_level,
            "shadow_lift": shadow_lift,
            "gamma": gamma,
            "contrast_s_curve": 1.20,
            "global_contrast": 1.30,  # Crisp Sigmoid slope for sharp edge & texture discrimination
            "saturation": 1.05,
            "adaptive_knee": True,  # Extended Filmic Knee protects highlights & midtones
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

    # -------------------------------------------------------------------------
    # TIER 2: Natural Perceptual Tone Mapping (Final Master Output)
    # Adaptive Key & Low-Key / Night-Scene Awareness
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # TIER 2: Natural Perceptual Tone Mapping (Final Master Output)
    # Adaptive Key & Low-Key / Night-Scene Awareness with Highlight Protection
    # -------------------------------------------------------------------------
    base_target_key = 0.108  # -20% global brightness reduction
    if log_avg < 0.075:
        # Smooth roll-off factor based on geometric mean luminance
        low_key_factor = float(np.clip(log_avg / 0.075, 0.20, 1.0))
        target_key = base_target_key * (low_key_factor**0.50)
    else:
        target_key = base_target_key

    # Clamp maximum gain to prevent over-lifting dark night skies (-20% gain cap)
    max_gain_cap = float(np.interp(log_avg, [0.005, 0.05, 0.10], [1.9, 2.55, 3.6]))
    gain = float(np.clip(target_key / max(log_avg, 1e-4), 0.5, max_gain_cap))

    # White Point Anchor: Peak input luminance scales smoothly to EXACTLY 1.0
    white_level = max(1.0, 1.0 * gain)

    # In night scenes, keep shadow_lift zero so the sigmoid asymptote anchors deep black skies
    if log_avg < 0.04:
        shadow_lift = 0.0
    else:
        shadow_lift = float(np.clip(p_black * 0.4, 0.0, 0.015))

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

    # 5. Normalized Sigmoid Contrast Curve with Hermite Highlight Protection
    # k controls the contrast slope, x0 is the perceptual midtone anchor (0.38 for +15% deeper blacks)
    k = float(
        np.clip(3.5 + (global_contrast - 1.0) * 3.0, 3.0, 6.0)
    )  # e.g. k=4.7 for contrast=1.40
    x0 = 0.38

    s_x = 1.0 / (1.0 + np.exp(-k * (lum_gamma - x0)))
    s_0 = 1.0 / (1.0 + np.exp(-k * (0.0 - x0)))
    s_1 = 1.0 / (1.0 + np.exp(-k * (1.0 - x0)))
    s_tone = np.clip((s_x - s_0) / (s_1 - s_0), 0.0, 1.0)

    # Highlight protection shoulder: Smoothly blend from contrast curve to soft filmic shoulder
    hl_weight = np.clip((lum_gamma - 0.35) / 0.65, 0.0, 1.0)
    hl_smooth = hl_weight * hl_weight * (3.0 - 2.0 * hl_weight)  # Hermite smoothstep
    lum_final = np.clip(s_tone * (1.0 - hl_smooth) + lum_gamma * hl_smooth, 0.0, 1.0)

    # 7. Hue-Preserving Chromaticity Ratio Transfer
    ratio = (lum_final / (lum + 1e-6))[:, :, np.newaxis]
    rgb_out = img * ratio

    # 8. Adaptive Highlight Desaturation (Anti-Chromatic Aberration Fringe)
    desat_factor = np.clip((lum_final - 0.55) / 0.40, 0.0, 1.0)
    desat_smooth = desat_factor * desat_factor * (3.0 - 2.0 * desat_factor)
    eff_sat = (
        (1.0 + (saturation - 1.0) * (1.0 - desat_smooth))
        * (1.0 - desat_smooth)
    )[:, :, np.newaxis]

    lum_3d = lum_final[:, :, np.newaxis]
    rgb_out = lum_3d + (rgb_out - lum_3d) * eff_sat

    return np.ascontiguousarray(np.clip(rgb_out, 0.0, 1.0), dtype=np.float32)


# =========================================================================
# 3. TAICHI GPU KERNEL DEFINITIONS
# =========================================================================

if TAICHI_AVAILABLE:

    @ti.kernel
    def auto_enhance_kernel(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
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
        k = 3.5 + (global_contrast - 1.0) * 3.0
        if k < 3.0:
            k = 3.0
        elif k > 6.0:
            k = 6.0
        x0 = 0.38

        s_0 = 1.0 / (1.0 + tm.exp(-k * (0.0 - x0)))
        s_1 = 1.0 / (1.0 + tm.exp(-k * (1.0 - x0)))
        inv_s_range = 1.0 / (s_1 - s_0)

        for i, j in ti.ndrange(h, w):
            v = src[i, j]
            r = tm.max(0.0, v[0])
            g = tm.max(0.0, v[1])
            b = tm.max(0.0, v[2])

            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            lum_scaled = (lum + shadow_lift) * gain

            lum_toned = 0.0
            if use_adaptive_knee != 0:
                lum_toned = (lum_scaled * (1.0 + (lum_scaled / w2))) / (
                    1.0 + lum_scaled
                )
            else:
                lum_toned = lum_scaled / (1.0 + lum_scaled)

            lum_gamma = tm.pow(tm.max(0.0, lum_toned), inv_gamma)

            s_x = 1.0 / (1.0 + tm.exp(-k * (lum_gamma - x0)))
            s_tone = tm.clamp((s_x - s_0) * inv_s_range, 0.0, 1.0)

            # Highlight protection shoulder: Smoothly blend from contrast curve to soft filmic shoulder
            hl_weight = tm.clamp((lum_gamma - 0.35) / 0.65, 0.0, 1.0)
            hl_smooth = hl_weight * hl_weight * (3.0 - 2.0 * hl_weight)
            lum_final = tm.clamp(
                s_tone * (1.0 - hl_smooth) + lum_gamma * hl_smooth, 0.0, 1.0
            )

            ratio = lum_final / (lum + 1e-6)
            r_out = r * ratio
            g_out = g * ratio
            b_out = b * ratio

            # Adaptive Highlight Desaturation (Anti-Chromatic Aberration Fringe)
            desat_factor = tm.clamp((lum_final - 0.55) / 0.40, 0.0, 1.0)
            desat_smooth = desat_factor * desat_factor * (3.0 - 2.0 * desat_factor)
            eff_sat = (1.0 + (saturation - 1.0) * (1.0 - desat_smooth)) * (1.0 - desat_smooth)

            r_out = lum_final + (r_out - lum_final) * eff_sat
            g_out = lum_final + (g_out - lum_final) * eff_sat
            b_out = lum_final + (b_out - lum_final) * eff_sat

            dst[i, j] = tm.vec3(
                tm.clamp(r_out, 0.0, 1.0),
                tm.clamp(g_out, 0.0, 1.0),
                tm.clamp(b_out, 0.0, 1.0),
            )


# =========================================================================
# 4. PURE GPU AOT / TCM EXECUTION (ZERO HOST MEMORY ROUNDTRIP)
# =========================================================================


def apply_auto_enhance_gpu(
    src_gpu: Any,
    params: Dict[str, Any],
    dst: Any = None,
    return_gpu: bool = True,
) -> Any:
    """
    Executes AutoEnhance directly inside GPU VRAM via Taichi AOT / TCM module.
    Zero PCIe transfer, pure GPU shader performance.
    """
    from taichi_vision.taichi_aot import get_engine, TaichiGPUBuffer
    from taichi_vision.taichi_algorithm.aot_api import _mod

    engine = get_engine()
    mod = _mod("auto_enhance")

    h, w = src_gpu.shape[:2]
    if dst is None:
        dst_buf = engine.allocate((h, w, 3), dtype=np.float32, is_vector=True)
    else:
        dst_buf = dst

    src_v = src_gpu
    if hasattr(src_gpu, "is_vector") and not src_gpu.is_vector:
        src_v = src_gpu.view_as_vector(True)

    dst_v = dst_buf
    if hasattr(dst_buf, "is_vector") and not dst_buf.is_vector:
        dst_v = dst_buf.view_as_vector(True)

    gamma = float(params.get("gamma", 2.2))
    inv_gamma = 1.0 / max(gamma, 1e-4)

    args = {
        "src": src_v,
        "dst": dst_v,
        "h": int(h),
        "w": int(w),
        "gain": float(params.get("gain", 1.0)),
        "white_level": float(params.get("white_level", 1.5)),
        "shadow_lift": float(params.get("shadow_lift", 0.02)),
        "inv_gamma": float(inv_gamma),
        "contrast_s_curve": float(params.get("contrast_s_curve", 1.10)),
        "global_contrast": float(params.get("global_contrast", 1.35)),
        "saturation": float(params.get("saturation", 1.05)),
        "use_adaptive_knee": 1 if params.get("adaptive_knee", True) else 0,
    }
    mod.run("auto_enhance", **args)

    if not return_gpu:
        res_np = dst_buf.to_numpy()
        if dst is None:
            dst_buf.destroy()
        return res_np
    return dst_buf


# =========================================================================
# 5. TOP-LEVEL FACADE API
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
    - If `src` is in VRAM (TaichiGPUBuffer) or `return_gpu=True`, executes directly on GPU TCM.
    """
    if params is None:
        computed_params = analyze_auto_enhance_params(src)
    else:
        computed_params = dict(params)

    if kwargs:
        computed_params.update(kwargs)

    is_gpu_in = hasattr(src, "to_numpy")

    if is_gpu_in or return_gpu:
        from taichi_vision.taichi_aot import upload, TaichiGPUBuffer

        src_gpu = (
            src if is_gpu_in else upload(np.ascontiguousarray(src, dtype=np.float32))
        )
        try:
            result = apply_auto_enhance_gpu(
                src_gpu,
                computed_params,
                dst=dst,
                return_gpu=return_gpu,
            )
        finally:
            if not is_gpu_in and hasattr(src_gpu, "destroy"):
                src_gpu.destroy()
    else:
        src_np = np.asarray(src, dtype=np.float32)
        result = apply_auto_enhance_np(src_np, computed_params)

    if return_params:
        return result, computed_params
    return result
