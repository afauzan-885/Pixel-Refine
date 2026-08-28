"""
Spatial Fusion — Noise & Motion Threshold Estimation.

``generate_spatial_weights_taichi`` requires a noise sigma and a motion
sensitivity.  This module provides self-contained estimation so the public
``spatial_merging`` API can auto-tune these thresholds from the reference
frame without forcing the caller to compute them manually.

- noise_sigma:           Laplacian MAD (median absolute deviation) estimator,
                         matching the application's historical
                         ``estimate_noise_in_python`` convention.
- motion_sensitivity:    Higher = more aggressive ghost rejection.  When
                         None, defaults to the established 150.0 value.
- noise_offset_factor:   Fraction of noise_sigma subtracted before the
                         exponential confidence decay.  Default 0.15.
"""

from typing import Any, Optional, Tuple

import numpy as np


def estimate_noise_sigma(
    ref_image: np.ndarray,
    fallback: float = 0.015,
) -> float:
    """Estimate image noise sigma via Taichi Multi-Subband Wavelet & Patch Subspace.
    100% Texture Invariant.

    Args:
        ref_image: Reference image (H, W) or (H, W, C) float32 [0, 1].
        fallback:  Value returned when the image is empty or degenerate.

    Returns:
        Estimated sigma in [1e-5, 0.99999].
    """
    if ref_image is None or (isinstance(ref_image, np.ndarray) and ref_image.size == 0):
        return float(fallback)

    try:
        from taichi_vision.taichi_algorithm.enhancement.estimate_noise import (
            estimate_noise,
        )

        return float(np.clip(estimate_noise(ref_image), 1e-5, 0.99999))
    except Exception:
        pass

    gray = np.asarray(ref_image, dtype=np.float32)
    if gray.ndim == 3:
        if gray.shape[2] == 3:
            gray = (
                0.299 * gray[..., 0]
                + 0.587 * gray[..., 1]
                + 0.114 * gray[..., 2]
            )
        elif gray.shape[2] == 1:
            gray = gray[..., 0]

    gray = np.ascontiguousarray(gray, dtype=np.float32)

    # Pure-NumPy 3x3 Laplacian fallback: [[0,1,0],[1,-4,1],[0,1,0]]
    lap = np.zeros_like(gray, dtype=np.float32)
    lap[1:-1, 1:-1] = (
        gray[1:-1, 0:-2]
        + gray[1:-1, 2:]
        + gray[0:-2, 1:-1]
        + gray[2:, 1:-1]
        - 4.0 * gray[1:-1, 1:-1]
    )

    if lap is None or lap.size == 0:
        return float(fallback)

    median_val = float(np.median(lap))
    mad_value = float(np.median(np.abs(lap - median_val)))
    estimated_sigma = mad_value * 1.4826

    return float(np.clip(estimated_sigma, 1e-5, 0.99999))


def auto_motion_sensitivity(
    is_raw: bool = False,
    base: float = 150.0,
) -> float:
    """Return a sensible default motion sensitivity.

    Higher values reject ghosts more aggressively.  RAW/linear bursts are
    typically noisier, so a slightly lower default keeps fine detail while
    still suppressing ghosts.
    """
    return base * (0.9 if is_raw else 1.0)


def resolve_spatial_thresholds(
    reference_work_gray: Any,
    *,
    noise_sigma: Optional[float] = None,
    motion_sensitivity: Optional[float] = None,
    noise_offset_factor: Optional[float] = None,
    is_raw: bool = False,
) -> Tuple[float, float, float]:
    """Resolve spatial-merging thresholds, auto-estimating missing values via Taichi GPU.

    Args:
        reference_work_gray: Work-resolution grayscale reference (GPU buffer or NumPy array).
        noise_sigma:         Explicit noise sigma [0.0 - 1.0]; None -> auto-estimate on GPU.
        motion_sensitivity:  Explicit motion sensitivity; None -> default.
        noise_offset_factor: Explicit noise offset; None -> default 0.15.
        is_raw:              Whether the burst is RAW/linear (affects default).

    Returns:
        (noise_sigma, motion_sensitivity, noise_offset_factor)
    """
    if noise_sigma is None or (isinstance(noise_sigma, (int, float)) and noise_sigma <= 0.0):
        from taichi_vision.taichi_algorithm.enhancement.estimate_noise import (
            estimate_noise,
        )

        noise_sigma = float(estimate_noise(reference_work_gray))
    else:
        noise_sigma = float(np.clip(noise_sigma, 1e-5, 0.99999))

    if motion_sensitivity is None:
        motion_sensitivity = auto_motion_sensitivity(is_raw=is_raw)
    if noise_offset_factor is None:
        noise_offset_factor = 0.15
    return (
        float(noise_sigma),
        float(motion_sensitivity),
        float(noise_offset_factor),
    )
