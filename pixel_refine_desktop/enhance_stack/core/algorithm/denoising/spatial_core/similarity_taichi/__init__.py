"""
similarity_taichi package
=========================
Standalone Taichi GPU implementation for Spatial Fusion / Similarity weight map generation.
"""

from .block_matching import (
    calculate_hybrid_gradient_optimized,
    calculate_match_confidence,
    fast_tanh,
)
from .compute_spatial import (
    compile_spatial_tcm,
    generate_spatial_weights_taichi,
    accumulate_spatial_merging_taichi,
    postprocess_spatial_weight_taichi,
    mean_division_vec3_weight_taichi,
    SpatialScratchCache,
    precompute_gradients_kernel,
    clear_f32_2d_kernel,
    equalize_brightness_kernel,
    phase1_coarse_analysis_kernel,
    phase2_fine_analysis_kernel,
)

__all__ = [
    "calculate_hybrid_gradient_optimized",
    "calculate_match_confidence",
    "fast_tanh",
    "compile_spatial_tcm",
    "generate_spatial_weights_taichi",
    "accumulate_spatial_merging_taichi",
    "postprocess_spatial_weight_taichi",
    "mean_division_vec3_weight_taichi",
    "SpatialScratchCache",
    "precompute_gradients_kernel",
    "clear_f32_2d_kernel",
    "equalize_brightness_kernel",
    "phase1_coarse_analysis_kernel",
    "phase2_fine_analysis_kernel",
]
