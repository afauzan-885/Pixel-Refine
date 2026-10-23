"""Compatibility facade for the resident denoising pipeline.

The implementation lives in small, single-purpose modules:

``frames``        host frame loading, orientation, GPU upload
``workspace``     WeightNet readback/upload scratch workspaces
``analysis``      analysis parameters, AutoEnhance, noise, WeightNet inputs
``weightnet``     multi-patch candidate selection and confidence upload
``aligners``      resident aligner implementations and the factory
``raw``/``raw_blend``  RAW CFA accumulation lane
``executor``      GPU-resident burst orchestration
``telemetry``     memory telemetry

Every symbol that used to live in this module is re-exported here, so existing
imports keep working.  Modules extracted from this file reach each other through
:func:`facade.api`, which resolves to this module — that keeps
``monkeypatch.setattr(resident_pipeline, name, fake)`` effective across the
whole pipeline.
"""

from __future__ import annotations

from .aligners.base import NoAlignmentGPUAligner, _ResidentFlowBufferMixin
from .aligners.factory import (
    _buffer_session,
    _component_factory,
    _destroy_work_item,
    _destroy_work_item_except,
    _export_result,
    _managed_api,
    _own_component,
    _track_gpu_result,
    create_resident_aligner,
)
from .aligners.feature import FeatureMatchingGPUAligner
from .aligners.flow import (
    BlockMatchingResidentAligner,
    FarnebackResidentAligner,
    LucasKanadeResidentAligner,
    _parse_bool,
    _scale_f32_scalar_gpu,
)
from .analysis import (
    ANALYSIS_AUTO_ENHANCE_MODE,
    _resolve_apap_fit_grid_size,
    _resolve_engine_analysis_params,
    _resolve_reference_analysis_params,
    _resolve_spatial_analysis_config,
    _resolve_weightnet_input_channels,
    _select_ransac_inlier_correspondences,
    analyze_auto_enhance_on_gpu,
    apply_auto_enhance_on_gpu,
    apply_clahe_16bit_reference,
    apply_precomputed_transfer_map,
    prepare_analysis_proxy_gpu,
    prepare_reference_analysis_and_noise,
    prepare_weightnet_reference_input,
    prepare_weightnet_support_input,
    resolve_noise_adaptive_penalty,
)
from .executor.run import run_gpu_resident_pipeline
from .frames import (
    _RAW_EXTENSIONS,
    _apply_orientation,
    _normalize_rgb_host_frame,
    _read_orientation,
    load_frame_to_gpu,
)
from .raw import _run_shared_raw_provider_pipeline
from .raw_blend import _gpu_blend_frame, _prepare_raw_aligned_analysis
from .telemetry import PipelineTelemetry, get_memory_telemetry_str
from .weightnet import (
    _iter_deep_support_candidate_maps,
    _iter_multi_patch_rank_maps,
    _multi_patch_weightnet_input,
    _select_multi_patch_candidates,
    _upload_weightnet_confidence,
)
from .workspace import _WeightNetReadbackWorkspace, _WeightNetUploadWorkspace

# Canonical alias kept for callers that used the shorter name.
run_resident_pipeline = run_gpu_resident_pipeline

__all__ = [
    "get_memory_telemetry_str",
    "load_frame_to_gpu",
    "analyze_auto_enhance_on_gpu",
    "apply_auto_enhance_on_gpu",
    "prepare_analysis_proxy_gpu",
    "prepare_reference_analysis_and_noise",
    "resolve_noise_adaptive_penalty",
    "apply_clahe_16bit_reference",
    "apply_precomputed_transfer_map",
    "prepare_weightnet_reference_input",
    "prepare_weightnet_support_input",
    "NoAlignmentGPUAligner",
    "BlockMatchingResidentAligner",
    "LucasKanadeResidentAligner",
    "FeatureMatchingGPUAligner",
    "FarnebackResidentAligner",
    "create_resident_aligner",
    "PipelineTelemetry",
    "run_gpu_resident_pipeline",
    "run_resident_pipeline",
]
