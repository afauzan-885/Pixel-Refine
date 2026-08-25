"""
Auto Brightness Enhancement Algorithm.
Inspired by LibRaw/rawpy's auto_bright mechanism with perceptual tone mapping,
exposure scaling, soft-knee highlight preservation, and hue-preserving color contrast.
"""

import numpy as np


def apply_auto_brightness(
    image: np.ndarray,
    clip_percentile: float = 0.002,
    target_white: float = 0.95,
    max_gain: float = 8.0,
    gamma: float = 2.2,
    contrast: float = 1.10,
    shadow_lift: float = 0.02,
    saturation_boost: float = 1.05,
) -> np.ndarray:
    """
    Apply intelligent auto brightness and perceptual tone enhancement.

    Args:
        image: Input RGB image float32 in range [0.0, 1.0], shape [H, W, 3].
        clip_percentile: Fraction of top brightest pixels to ignore when finding white point (default 0.2%).
        target_white: Target luminance value for the non-clipped highlight (default 0.95).
        max_gain: Maximum exposure multiplication factor (default 8.0).
        gamma: Display gamma exponent for perceptual midtone expansion (default 2.2).
        contrast: Subtle S-curve contrast enhancement factor (default 1.10).
        shadow_lift: Toe lift to reveal deep shadow details without clipping blacks (default 0.02).
        saturation_boost: Subtle chroma boost to keep colors vibrant and pleasing (default 1.05).

    Returns:
        Enhanced RGB float32 array in range [0.0, 1.0] with beautiful natural brightness and contrast.
    """
    if not isinstance(image, np.ndarray) or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"Expected RGB image array [H, W, 3], got {getattr(image, 'shape', type(image))}")

    img_f32 = np.ascontiguousarray(image, dtype=np.float32)
    img_f32 = np.clip(img_f32, 0.0, 1.0)

    # 1. Perceptual Luminance (ITU-R BT.709 standard)
    lum = 0.2126 * img_f32[:, :, 0] + 0.7152 * img_f32[:, :, 1] + 0.0722 * img_f32[:, :, 2]

    # Sample a representative subset for fast & accurate percentile calculation
    h, w = lum.shape
    sample_step = max(1, int(np.sqrt(h * w / 250000)))  # ~250k samples
    lum_sample = lum[::sample_step, ::sample_step].ravel()

    # 2. Histogram White Point and Black Point Analysis (rawpy style)
    p_high = float(np.percentile(lum_sample, 100.0 * (1.0 - clip_percentile)))
    p_shadow = float(np.percentile(lum_sample, 0.5))

    # Calculate adaptive exposure gain multiplier
    p_high_safe = max(p_high, 1e-4)
    raw_gain = target_white / p_high_safe
    gain = float(np.clip(raw_gain, 1.0, max_gain))

    # 3. Adaptive Exposure & Black Level Adjustment
    # Slightly subtract pedestal noise and multiply by auto gain
    lum_scaled = np.maximum(0.0, lum - p_shadow * 0.5) * gain

    # 4. Filmic Soft-Knee Highlight Roll-Off (Extended Reinhard Curve)
    # Prevents harsh flat white clipping in bright specular areas
    white_point = float(np.percentile(lum_sample * gain, 99.8))
    white_point = max(1.2, white_point)
    lum_tone = (lum_scaled * (1.0 + (lum_scaled / (white_point * white_point)))) / (1.0 + lum_scaled)

    # 5. Perceptual Gamma Expansion & Shadow Lift
    # Reveals shadow/midtone details naturally
    lum_gamma = np.power(np.maximum(lum_tone + shadow_lift * (1.0 - lum_tone), 0.0), 1.0 / gamma)

    # 6. S-Curve Contrast Enhancement (Midtone Punch)
    # y = x + 0.5 * (contrast - 1.0) * sin(2 * pi * x)
    if contrast > 1.0:
        c_strength = float(np.clip(contrast - 1.0, 0.0, 0.5))
        lum_final = lum_gamma + c_strength * np.sin(2.0 * np.pi * lum_gamma) * 0.15
        lum_final = np.clip(lum_final, 0.0, 1.0)
    else:
        lum_final = np.clip(lum_gamma, 0.0, 1.0)

    # 7. Hue-Preserving Color Ratio Transfer
    # Scale RGB channels by luminance ratio to strictly preserve color balance and avoid hue shifts
    ratio = (lum_final / (lum + 1e-7))[:, :, np.newaxis]
    rgb_bright = img_f32 * ratio

    # 8. Natural Saturation Boost
    # Keeps rich tones from looking washed out
    if saturation_boost != 1.0:
        lum_out = lum_final[:, :, np.newaxis]
        rgb_bright = lum_out + (rgb_bright - lum_out) * saturation_boost

    result = np.ascontiguousarray(np.clip(rgb_bright, 0.0, 1.0), dtype=np.float32)
    return result
