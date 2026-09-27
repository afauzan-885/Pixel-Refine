"""Compatibility façade for the optional WeightNet SR confidence provider."""

from .splat_sr.weightnet_confidence import *  # noqa: F401,F403


def __getattr__(name):
    from .splat_sr import weightnet_confidence as implementation

    return getattr(implementation, name)
