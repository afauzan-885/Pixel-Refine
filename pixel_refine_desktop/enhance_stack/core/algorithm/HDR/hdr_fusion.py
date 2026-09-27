"""Compatibility imports for the weighted-average HDR implementation."""

from .weighted_average.core import (
    WeightedHDRFusion,
    estimate_noise_taichi,
    rgb_to_gray,
    srgb_to_linear,
    _LAPLACIAN_4,
)

__all__ = [
    "WeightedHDRFusion",
    "estimate_noise_taichi",
    "rgb_to_gray",
    "srgb_to_linear",
]
