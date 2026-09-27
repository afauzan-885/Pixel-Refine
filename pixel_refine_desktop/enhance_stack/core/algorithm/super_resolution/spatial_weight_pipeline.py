"""Compatibility façade for Splat SR's spatial weight helpers."""

from .splat_sr.spatial_weight_pipeline import *  # noqa: F401,F403


def __getattr__(name):
    from .splat_sr import spatial_weight_pipeline as implementation

    return getattr(implementation, name)
