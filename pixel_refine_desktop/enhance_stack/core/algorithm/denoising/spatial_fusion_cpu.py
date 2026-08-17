"""Compatibility import for the unified :mod:`spatial_fusion` adapter."""

from .spatial_fusion import SpatialFusionDenoisingAlgorithm

SpatialFusionCPUDenoisingAlgorithm = SpatialFusionDenoisingAlgorithm
SimilarityDenoisingAlgorithm = SpatialFusionDenoisingAlgorithm

__all__ = ["SpatialFusionCPUDenoisingAlgorithm", "SimilarityDenoisingAlgorithm"]
