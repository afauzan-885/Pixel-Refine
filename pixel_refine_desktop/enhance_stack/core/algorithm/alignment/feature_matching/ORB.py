"""
ORB Adapter - Redirected to Taichi Vision OFB Algorithm.
========================================================
Maintains backwards compatibility while dispatching to the 100% GPU-native
Taichi Vision Oriented FAST + BRIEF (OFB) alignment engine.
"""

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.OFB import (
    OFBAlgorithm,
)


class ORBAlgorithm(OFBAlgorithm):
    NAME = "ORB"
    DESCRIPTION = "Taichi Vision Oriented FAST and BRIEF Feature Alignment (Legacy ORB Alias)."


def running_orb(*args, **kwargs):
    raise RuntimeError(
        "ORB/OFB is now orchestrated by MFDenoiser. Use MFDenoiser with alignment='OFB' instead."
    )

