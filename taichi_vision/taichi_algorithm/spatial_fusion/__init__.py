"""
Spatial Fusion — Ghost Reduction & Multi-Frame Merging.

Multi-frame burst fusion weight computation with ghost rejection.
Produces per-frame weight maps (frame-by-frame) or a fully fused result
(batch mode). This package is the canonical home of the spatial-merging
kernels and runtime wrappers; the application's historical
``spatial_core/similarity_taichi`` module re-exports from here so there is
one maintained implementation.

Public entry point (also exposed as ``taichi_aot.spatial_merging``):
    from taichi_vision.taichi_algorithm.spatial_fusion import spatial_merging
"""

from .block_matching import (
    calculate_hybrid_gradient_optimized,
    calculate_match_confidence,
    fast_tanh,
)
from .compute_spatial import (
    accumulate_spatial_merging_taichi,
    accumulate_spatial_merging_tile_taichi,
    accumulate_average_taichi,
    accumulate_average_tile_taichi,
    remap_accumulate_tile_taichi,
    clear_f32_2d_kernel,
    compile_spatial_tcm,
    equalize_brightness_kernel,
    generate_spatial_weights_taichi,
    mean_division_vec3_weight_taichi,
    postprocess_spatial_weight_taichi,
    phase1_coarse_analysis_kernel,
    phase2_fine_analysis_kernel,
    precompute_gradients_kernel,
    SpatialScratchCache,
)
from .noise_estimation import (
    auto_motion_sensitivity,
    estimate_noise_sigma,
    resolve_spatial_thresholds,
)
from .spatial_merging import spatial_merging

__all__ = [
    # kernels
    "precompute_gradients_kernel",
    "clear_f32_2d_kernel",
    "equalize_brightness_kernel",
    "phase1_coarse_analysis_kernel",
    "phase2_fine_analysis_kernel",
    # runtime wrappers
    "SpatialScratchCache",
    "generate_spatial_weights_taichi",
    "accumulate_spatial_merging_taichi",
    "accumulate_spatial_merging_tile_taichi",
    "accumulate_average_taichi",
    "accumulate_average_tile_taichi",
    "remap_accumulate_tile_taichi",
    "mean_division_vec3_weight_taichi",
    "postprocess_spatial_weight_taichi",
    "compile_spatial_tcm",
    # thresholds
    "estimate_noise_sigma",
    "auto_motion_sensitivity",
    "resolve_spatial_thresholds",
    # public API
    "spatial_merging",
]
