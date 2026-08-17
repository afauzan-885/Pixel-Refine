"""Unified high-level workflows for panorama, HDR, focus, and 3D tasks.

The functions exported here are aliases to family-local orchestrators.  No
algorithm kernel is reimplemented and importing this module does not modify
the legacy ``taichi_algorithm`` facade.
"""

from __future__ import annotations

from .domain_catalog import (
    ALGORITHM_CATALOG,
    PENDING_NATIVE_CAPABILITIES,
    AlgorithmSpec,
    audit_catalog,
)
from .focus_stack import FocusStackResult, focus_measure, focus_stack
from .image_processing.hdr_stack import deghost_confidence, hdr_stack
from .image_processing.hdr_response import (
    ResponseCalibration,
    estimate_response_curve,
    estimate_response_curve_robertson,
    merge_radiance,
    merge_radiance_weighted,
    response_weight,
)
from .panorama import (
    AlignmentResult,
    ExposureCompensation,
    PanoramaError,
    ProjectionResult,
    align_pair,
    apply_exposure_compensation,
    blend_with_seam,
    compensate_exposure,
    cylindrical_projection,
    dynamic_programming_seam,
    equirectangular_projection,
    estimate_exposure_compensation,
    graph_cut_maxflow,
    graph_cut_surrogate,
    project_image,
    seam_energy,
    spherical_projection,
    sparse_to_dense_warp,
    stitch_panorama,
)
from .sfm.reconstruction_pipeline import (
    MVSResult,
    PairwiseSfMConfig,
    PairwiseSfMResult,
    PointCloudResult,
    SequenceSfMResult,
    reconstruct_pair,
    reconstruct_sequence,
    run_patchmatch_mvs,
    run_plane_sweep_mvs,
    run_sgm_mvs,
    run_point_cloud_pipeline,
)
from .sfm.registration import (
    ICPResult,
    PnPResult,
    TSDFResult,
    integrate_tsdf,
    point_to_plane_icp,
    project_points,
    solve_pnp_checked,
)
from .sfm.five_point_solver import solve_five_point
from .sfm.cheirality_check import check_cheirality_minimal, check_cheirality_full
from .sfm.triangulation import triangulate_adaptive
from .sfm.feature_matching import bfmatcher_l2, bfmatcher_hamming
from .sfm.bundle_adjustment import bundle_adjust_lm
from .sfm.point_cloud import (
    statistical_outlier_removal,
    radius_outlier_removal,
    voxel_downsample,
    estimate_normals,
    preprocess_point_cloud,
)
from .sfm.poisson_recon import poisson_reconstruct
from .sfm.texture_mapping import TextureAtlasResult, rasterize_texture_atlas

__all__ = [
    "AlignmentResult",
    "AlgorithmSpec",
    "ALGORITHM_CATALOG",
    "PENDING_NATIVE_CAPABILITIES",
    "ExposureCompensation",
    "FocusStackResult",
    "MVSResult",
    "PairwiseSfMConfig",
    "PairwiseSfMResult",
    "SequenceSfMResult",
    "PanoramaError",
    "ProjectionResult",
    "ResponseCalibration",
    "PointCloudResult",
    "ICPResult",
    "PnPResult",
    "TSDFResult",
    "align_pair",
    "apply_exposure_compensation",
    "blend_with_seam",
    "compensate_exposure",
    "cylindrical_projection",
    "deghost_confidence",
    "focus_measure",
    "focus_stack",
    "hdr_stack",
    "estimate_response_curve",
    "estimate_response_curve_robertson",
    "merge_radiance",
    "merge_radiance_weighted",
    "response_weight",
    "estimate_exposure_compensation",
    "dynamic_programming_seam",
    "equirectangular_projection",
    "graph_cut_surrogate",
    "graph_cut_maxflow",
    "project_image",
    "seam_energy",
    "spherical_projection",
    "sparse_to_dense_warp",
    "reconstruct_pair",
    "reconstruct_sequence",
    "run_plane_sweep_mvs",
    "run_sgm_mvs",
    "run_patchmatch_mvs",
    "run_point_cloud_pipeline",
    "stitch_panorama",
    "audit_catalog",
    "integrate_tsdf",
    "point_to_plane_icp",
    "project_points",
    "solve_pnp_checked",
    "solve_five_point",
    "check_cheirality_minimal",
    "check_cheirality_full",
    "triangulate_adaptive",
    "bfmatcher_l2",
    "bfmatcher_hamming",
    "bundle_adjust_lm",
    "statistical_outlier_removal",
    "radius_outlier_removal",
    "voxel_downsample",
    "estimate_normals",
    "preprocess_point_cloud",
    "poisson_reconstruct",
    "TextureAtlasResult",
    "rasterize_texture_atlas",
]
