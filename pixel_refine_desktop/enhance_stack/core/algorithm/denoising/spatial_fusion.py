"""Spatial fusion denoising adapter with CPU/GPU dispatching."""

import os

from taichi_library.backend_config import requested_backend


def _active_backend():
    """Read the same canonical backend contract as the AOT engine.

    Importing the native engine is deferred until automatic mode is actually
    requested, keeping this adapter safe for compiler-only and CPU imports.
    """

    requested, _explicit, _source = requested_backend()
    if requested != "auto":
        return requested
    try:
        from taichi_library.taichi_aot import get_backend_name

        return get_backend_name()
    except Exception:
        return "cpu"


active_arch = _active_backend()

if active_arch == "cpu":
    from .spatial_fusion_cpu import (
        SpatialFusionCPUDenoisingAlgorithm as SpatialFusionDenoisingAlgorithm,
        SimilarityDenoisingAlgorithm,
    )
else:
    from .spatial_fusion_gpu import (
        SpatialFusionDenoisingAlgorithm,
        SimilarityDenoisingAlgorithm,
    )
