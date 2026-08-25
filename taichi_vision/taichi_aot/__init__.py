"""Runtime compatibility facade for the Taichi AOT library.

The runtime (engine, memory policy, backend selection, and artifact loading)
stays in this package.  Algorithm implementations live in
``taichi_vision.taichi_algorithm.aot_api`` so there is one maintained source
tree.  Importing this module keeps the historical public API unchanged:

    import taichi_vision.taichi_aot as ta
    ta.resize(image, (1024, 768))

The explicit runtime imports below also preserve ``ta.engine`` and the
backend-management helpers used by the application.
"""

import os
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_canonical_engine_source():
    """Load the maintained Python engine instead of a stale compiled sibling.

    Python gives ``engine.cp*.pyd`` precedence over ``engine.py``.  The
    checked-in binary was built against the retired package namespace, while
    ``engine.py`` is the maintained lifecycle/runtime source.  Loading the
    source module explicitly keeps backend initialization canonical and makes
    the package independent from that stale build artifact.
    """
    module_name = f"{__name__}.engine"
    loaded = sys.modules.get(module_name)
    if loaded is not None:
        return loaded

    source_path = Path(__file__).with_name("engine.py")
    spec = spec_from_file_location(module_name, source_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load canonical engine source: {source_path}")
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    return module


_load_canonical_engine_source()

# Jalur Dynamic Loading: Utamakan Binary Native DLL (.pyd/.so) di Mode Production,
# dan fallback ke source code .py di Mode Development.
_USE_NATIVE = os.getenv("PIXEL_REFINE_USE_NATIVE_ENGINE", "1") == "1"

try:
    if _USE_NATIVE:
        # Coba import native binary engine terlebih dahulu
        from .engine import (
            AOTEngine,
            TaichiGPUBuffer,
            InputArray,
            OutputArray,
            select_backend,
            resolve_backend_config,
            get_backend_config,
            get_backend_name,
            backend_info,
            engine,
            enable_experiment_mode,
            is_experiment_mode,
            INTER_CUBIC,
            INTER_LINEAR,
            INTER_NEAREST,
            INTER_AREA,
            COLOR_BGR2GRAY,
            COLOR_RGB2GRAY,
            COLOR_GRAY2BGR,
        )
        print("[AOT Native] Production Engine Active (C++ Compiled)")
    else:
        raise ImportError("Development mode forced")
except Exception:
    # Jalur Development / Fallback
    from .engine import (
        AOTEngine,
        TaichiGPUBuffer,
        InputArray,
        OutputArray,
        select_backend,
        resolve_backend_config,
        get_backend_config,
        get_backend_name,
        backend_info,
        engine,
        enable_experiment_mode,
        is_experiment_mode,
        INTER_CUBIC,
        INTER_LINEAR,
        INTER_NEAREST,
        INTER_AREA,
        COLOR_BGR2GRAY,
        COLOR_RGB2GRAY,
        COLOR_GRAY2BGR,
    )

from .backend_config import (
    BackendConfig,
    CANONICAL_BACKENDS,
    GPU_BACKENDS,
    normalize_backend,
    normalize_vendor,
    backend_env,
)
from .capabilities import BackendCapabilities, classify_device, backend_candidates
from .backend_manager import BackendManager, BackendDecision, preflight_backend
from .artifact_targets import (
    TargetSpec,
    detect_target,
    resolve_artifact,
    load_target_manifest,
)
from .block import (
    BlockGrid,
    BlockRecord,
    BlockState,
    BlockPath,
    BlockCapability,
    OperationContract,
    BlockOperationContract,
    PartitionStrategy,
    BlockPartitionStrategy,
    BackendCapability,
    ShapeTransform,
    HaloPolicy,
    BorderPolicy,
    ReductionPolicy,
    MergePolicy,
    BlockAdapter,
    BlockOperationAdapter,
    LegacyPartitionEvidence,
    CANONICAL_OPERATION_ALIASES,
    OPERATION_ALIASES,
    canonical_operation_name,
    operation_contract,
    get_operation_contract,
    operation_contracts,
    register_operation_contract,
    can_auto_block,
    can_partition_block,
    is_partition_block_safe,
    operation_allows_partition_block,
    LEGACY_PARTITION_EVIDENCE,
    legacy_partition_evidence,
    can_auto_partition_dispatch,
    is_legacy_partition_dispatch_safe,
    register_block_adapter,
    lookup_block_adapter,
    get_block_adapter,
    registered_block_adapters,
    block_coverage_report,
    checksum,
)
from .block_adapters import (
    PartitionContext,
    LOW_RISK_ADAPTER_OPERATIONS,
    LOCAL_STENCIL_ADAPTER_OPERATIONS,
    LEGACY_LOCAL_ADAPTER_OPERATIONS,
    MAP_REDUCE_ADAPTER_OPERATIONS,
    NCC_ADAPTER_OPERATIONS,
    STITCH_ADAPTER_OPERATIONS,
    ACCUMULATOR_ADAPTER_OPERATIONS,
    COORDINATE_ADAPTER_OPERATIONS,
    COORDINATE_DOMAIN_ADAPTER_OPERATIONS,
    COORDINATE_WARP_ADAPTER_OPERATIONS,
    OUTPUT_DOMAIN_ADAPTER_OPERATIONS,
    FLOW_MAP_ADAPTER_OPERATIONS,
    NORMALIZATION_ADAPTER_OPERATIONS,
    BRIEF_PATTERN_ADAPTER_OPERATIONS,
    ANALYSIS_ADAPTER_OPERATIONS,
    GLOBAL_PARTITION_ADAPTER_OPERATIONS,
    MTB_PARTITION_ADAPTER_OPERATIONS,
    JBLU_PARTITION_ADAPTER_OPERATIONS,
    BILATERAL_GRID_PARTITION_ADAPTER_OPERATIONS,
    INPAINT_PARTITION_ADAPTER_OPERATIONS,
    FFT_ADAPTER_OPERATIONS,
    PHASE_CORRELATION_ADAPTER_OPERATIONS,
    AKAZE_ADAPTER_OPERATIONS,
    DEMOSAIC_HALF_ADAPTER_OPERATIONS,
    DEMOSAIC_HALF_GAP_OPERATIONS,
    DEMOSAIC_FULL_ADAPTER_OPERATIONS,
    BM3D_ADAPTER_OPERATIONS,
    OPTICAL_FLOW_CONTRACT_OPERATIONS,
    OPTICAL_FLOW_ADAPTER_OPERATIONS,
    OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS,
    OPTICAL_FLOW_IDENTITY_OPERATIONS,
    register_low_risk_block_adapters,
    register_local_stencil_block_adapters,
    register_legacy_local_block_adapters,
    register_analysis_block_adapters,
    register_fft_block_adapters,
    register_phase_correlation_block_adapters,
    register_akaze_block_adapters,
    register_optical_flow_identity_adapters,
    register_demosaic_half_adapters,
    register_demosaic_full_adapters,
    register_bounded_semantic_adapters,
    register_global_partition_adapters,
    register_mtb_partition_adapters,
    register_jblu_partition_adapters,
    register_bilateral_grid_partition_adapters,
    register_inpaint_partition_adapters,
    register_map_reduce_block_adapters,
    register_accumulator_block_adapters,
    register_coordinate_block_adapters,
    register_coordinate_domain_adapters,
    register_coordinate_warp_adapters,
    register_output_domain_adapters,
    register_flow_map_adapters,
    register_normalization_adapters,
    register_brief_pattern_adapters,
    register_specialized_block_adapters,
    ensure_default_block_adapters,
    default_block_adapter_registration_errors,
    run_adapter_tiled,
    run_analysis_tiled,
    run_fft_partition_tiled,
    run_phase_correlation_partition_tiled,
    run_akaze_keypoints_partition_tiled,
    run_optical_flow_identity_partition_tiled,
    run_global_partition_tiled,
    run_mtb_partition_tiled,
    run_jblu_partition_tiled,
    run_bilateral_grid_partition_tiled,
    run_inpaint_partition_tiled,
    verify_analysis_parity,
    verify_fft_parity,
    verify_phase_correlation_parity,
    verify_akaze_keypoint_parity,
    verify_optical_flow_identity_parity,
    run_demosaic_half_tiled,
    run_demosaic_full_tiled,
    verify_demosaic_half_parity,
    demosaic_half_partition_gap_report,
    verify_demosaic_full_parity,
    demosaic_full_partition_gap_report,
    verify_global_partition_parity,
    verify_mtb_partition_parity,
    verify_jblu_partition_parity,
    verify_bilateral_grid_partition_parity,
    verify_inpaint_partition_parity,
    run_coordinate_tiled,
    run_output_domain_tiled,
    run_adapter_map_reduce,
    verify_adapter_parity,
    verify_coordinate_parity,
    verify_coordinate_warp_parity,
    run_coordinate_warp_tiled,
    verify_flow_maps_parity,
    verify_normalize_image_parity,
    verify_output_domain_parity,
    verify_map_reduce_parity,
    GLOBAL_REDUCTION_CONTRACT_OPERATIONS,
    global_reduction_partition_gap_report,
    ITERATIVE_FEATURE_GAP_OPERATIONS,
    iterative_feature_gap_report,
    optical_flow_partition_gap_report,
    FEATURE_GEOMETRY_CONTRACT_OPERATIONS,
    feature_geometry_partition_gap_report,
    validate_homography_correspondence_contract,
    bm3d_partition_gap_report,
    moving_optical_flow_partition_gap_report,
    verify_moving_flow_translation_contract,
    aggregate_moving_flow_candidate_evidence,
    aggregate_native_moving_flow_candidates,
    qualify_native_moving_flow_candidates,
    local_stencil_contract_report,
)
from .native_evidence import (
    NativePartitionEvidence,
    register_native_partition_evidence,
    lookup_native_partition_evidence,
    get_native_partition_evidence,
    native_partition_evidence_supported,
    native_partition_evidence_report,
    native_partition_evidence_snapshot,
    clear_native_partition_evidence,
    register_probe_result,
    register_verified_native_partition_evidence,
    register_verified_native_stencil_evidence,
    register_verified_native_local_stencil_evidence,
    register_verified_native_opengl_stencil_evidence,
    register_verified_native_opengl_partition_evidence,
    register_verified_native_opengl_intel_evidence,
)
from .descriptor_parity import (
    match_binary_descriptors_reference,
    verify_binary_descriptor_partition_parity,
    ratio_test_binary_descriptors_reference,
    cross_check_binary_descriptors_reference,
    ratio_cross_check_binary_descriptors_reference,
    verify_binary_descriptor_matching_partition_parity,
)
from .generic_block import (
    BlockComputeSpec,
    BlockTileContext,
    BlockPlanUnavailable,
    BlockExecutionError,
    GenericBlockExecutor,
    GenericBlockReport,
    GenericBlockResult,
    run_generic_blocks,
    run_registered_block_adapter,
)
from .compute_block import (
    ComputeBlockAnalysis,
    ComputeBlockMetadata,
    analyze_compute_block_source,
    compute_block,
    current_compute_block_scope,
    get_compute_block_registry,
)
from .pipeline_scheduler import PipelineStage, run_block_pipeline
from .auto_pipeline import (
    AutoPipelinePlanner,
    GraphSpec,
    PipelinePlan,
    EWMA,
    PlannerTelemetry,
    PipelineTelemetry,
    AutoTuneConfig,
    AutoTuneRecommendation,
    ConservativeAutoTuner,
    AutoPipelineAutotuner,
)
from taichi_vision.taichi_algorithm.compression.raw_frame import (
    RawMosaicFrame,
    raw_frame_from_dng,
)
from taichi_vision.taichi_algorithm.compression.dng_aot import (
    DNGCapabilityError,
    DNGCapabilityReport,
    dng_capability_report,
)
from taichi_vision.taichi_algorithm.compression.raw_pipeline import (
    RawFusionReport,
    RawFlowTileContract,
    raw_flow_tile_contract,
    fuse_raw_frames_blockwise,
    fuse_dng_frames_blockwise,
    raw_alignment_guide,
    raw_alignment_guide_dng,
    raw_alignment_guide_native,
    raw_normalize_headroom_native,
    raw_weight_map,
    raw_weight_map_native,
    fuse_raw_pair_native,
    fuse_raw_accumulate_native,
    phase_safe_integer_warp,
    raw_optical_flow,
    raw_optical_flow_dng,
)

# Keep the complete historical algorithm surface available at the old import
# path.  The implementation is now maintained only in ``taichi_algorithm``.
from taichi_vision.taichi_algorithm.aot_api import *  # noqa: F401,F403,E402
from taichi_vision.taichi_algorithm.aot_api import (  # noqa: E402
    _mod,
    _module_cache,
    load_tcm,
    unload_all_modules,
    get_engine,
    set_block_mode,
    get_block_config,
    get_block_cache_stats,
    clear_block_quarantine,
    get_memory_status,
    auto_pipeline,
    configure_block_reservation,
)

try:
    from taichi_vision.taichi_algorithm.taichi_worker import ti_thread
except Exception:  # pragma: no cover - compiler-only environments
    ti_thread = None


__all__ = [
    name
    for name in globals()
    if not name.startswith("_")
]
