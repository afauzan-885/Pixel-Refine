"""Spatial fusion denoising adapter with CPU/GPU dispatching."""

import os

# Check architecture to load the correct CPU or GPU version
active_arch = os.environ.get("PIXEL_REFINE_AOT_ARCH", "vulkan").lower()

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
