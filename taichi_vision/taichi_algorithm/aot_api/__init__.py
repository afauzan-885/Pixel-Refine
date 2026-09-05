from concurrent.futures.thread import ThreadPoolExecutor
import os
import functools
import time
import zipfile

# Suppress Vulkan loader registry warnings on Windows
os.environ["VK_LOADER_DEBUG"] = "error"
import sys
import numpy as np

# Path resolution to find the bridge
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Legacy JIT imports removed as we now use AOT (TCM) exclusively


# Import the Generic AOT Engine and Buffer Pool
from taichi_vision.taichi_aot.engine import (
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
)
from taichi_vision.taichi_aot.backend_config import (
    BackendConfig,
    CANONICAL_BACKENDS,
    GPU_BACKENDS,
    normalize_backend,
    normalize_vendor,
    backend_env,
)
from taichi_vision.taichi_aot.capabilities import (
    BackendCapabilities,
    classify_device,
    backend_candidates,
)
from taichi_vision.taichi_aot.backend_manager import (
    BackendManager,
    BackendDecision,
    preflight_backend,
)
from taichi_vision.taichi_aot.artifact_targets import (
    TargetSpec,
    detect_target,
    resolve_artifact,
    load_target_manifest,
)
from taichi_vision.taichi_aot.engine import enable_experiment_mode, is_experiment_mode
from taichi_vision.taichi_algorithm.demosaicing.demosaic_runtime import (
    DemosaicBufferSet,
)
from taichi_vision.taichi_algorithm.demosaicing.demosaic_graph_manifest import (
    resolve_graph_name,
    registered_graph_names,
)
from taichi_vision.taichi_aot.engine import (
    INTER_CUBIC,
    INTER_LINEAR,
    INTER_NEAREST,
    INTER_AREA,
)
from taichi_vision.taichi_aot.engine import (
    COLOR_BGR2GRAY,
    COLOR_RGB2GRAY,
    COLOR_GRAY2BGR,
)
from taichi_vision.taichi_aot.block import (
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
from taichi_vision.taichi_aot.block_adapters import (
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
    optical_flow_partition_gap_report,
)
from taichi_vision.taichi_aot.native_evidence import (
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
from taichi_vision.taichi_aot.generic_block import (
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
from taichi_vision.taichi_aot.compute_block import (
    ComputeBlockAnalysis,
    ComputeBlockMetadata,
    analyze_compute_block_source,
    compute_block,
    current_compute_block_scope,
    get_compute_block_registry,
)
from taichi_vision.taichi_aot.pipeline_scheduler import (
    PipelineStage,
    run_block_pipeline,
)
from taichi_vision.taichi_aot.auto_pipeline import (
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
from taichi_vision.taichi_algorithm.taichi_worker import ti_thread

# Bridge to specialized AOT functions
# Moved to lazy imports in wrapper functions below to avoid circular imports


def get_engine():
    """Return the canonical engine handle used by all public AOT operations."""

    return engine


# --- Lazy-Load TCM Module Cache ---
# Modules are NOT loaded at startup. Loaded on first use, cached permanently.
# Saves ~200MB of idle VRAM compared to eager loading all 15 modules.
# An explicit root remains authoritative.  Otherwise `_mod` resolves the
# target-qualified LLVM20 bundle automatically when the isolated release root
# exists, with the checked-in tree retained only as a rollback/source fallback.
_tcm_dir = os.path.abspath(
    os.environ.get("PIXEL_REFINE_AOT_TCM_ROOT", os.path.join(file_dir, "../aot_tcm"))
)
_module_cache = {}  # name -> AOTModuleWrapper (loaded on demand)


def set_block_mode(
    enabled=False,
    size=512,
    threshold_bytes=512 * 1024 * 1024,
    cache_entries=64,
    cache_bytes=None,
    adaptive_memory=True,
    device_cache_enabled=True,
    device_cache_bytes=128 * 1024 * 1024,
):
    """Configure block execution.

    Local parity-safe operations are planned adaptively under memory pressure
    even when ``enabled`` is False. Setting ``enabled`` opts additional
    block-classified operations into the explicit policy.
    """
    return engine.configure_blocks(
        enabled=enabled,
        size=size,
        threshold_bytes=threshold_bytes,
        cache_entries=cache_entries,
        cache_bytes=cache_bytes,
        adaptive_memory=adaptive_memory,
        device_cache_enabled=device_cache_enabled,
        device_cache_bytes=device_cache_bytes,
    )


def get_block_config():
    """Return the active block runtime policy."""
    return engine.get_block_config()


def get_block_cache_stats():
    """Return cache hit, admission, eviction, and byte-usage counters."""
    return engine.get_block_cache_stats()


def get_last_block_execution():
    """Return host-side dispatch/sync/readback telemetry for the last block call."""
    return engine.get_last_block_execution()


def clear_block_quarantine(operation=None):
    """Clear a block-operation quarantine after a controlled retest."""
    return engine.clear_block_quarantine(operation)


def get_memory_status(force=False):
    """Return the current realtime RAM pressure and cache-admission policy."""
    return engine.get_memory_status(force=force)


def trim_memory_pool():
    """Synchronize and release idle native GPU buffers.

    This is intentionally explicit: normal calls retain buffers for
    throughput, while constrained streaming callers can trim between tiles
    to lower the VRAM floor.
    """
    engine.sync()
    pool = getattr(engine, "buffer_pool", None)
    if pool is not None and hasattr(pool, "clear"):
        pool.clear()
    return engine.get_memory_status(force=True)


def reclaim_resident_buffers(reason: str = "manual"):
    """Phase 4 D3: drain warm pool + retired queue + staging pool.

    Public alias for ``engine.reclaim_resident_buffers`` with a
    user-supplied ``reason`` string.  Returns a counter dict with
    before/after ``get_memory_status`` snapshots and the delta in
    live / pooled / staging / retired bytes.  Safe to call from
    any thread that does not already hold ``engine._lock`` for
    another purpose.
    """
    fn = getattr(engine, "reclaim_resident_buffers", None)
    if not callable(fn):
        # Fallback for engines that pre-date Phase 4 D3: at least clear
        # the warm pool, then report a structured dict.
        trim_memory_pool()
        return {
            "reason": str(reason),
            "before": engine.get_memory_status(force=True),
            "after": engine.get_memory_status(force=True),
            "reclaimed_live_bytes": 0,
            "reclaimed_pooled_bytes": 0,
            "reclaimed_staging_bytes": 0,
            "reclaimed_retired_bytes": 0,
            "fallback": "trim_memory_pool",
        }
    return fn(reason)


def set_force_host_accessible(value):
    """Phase 4 D1: force every subsequent allocation to use
    host-accessible (shared) memory.  Pass ``True`` to force, ``False``
    to force device-local, or ``None`` to clear the override and let
    the engine apply the default policy.  Returns the new effective
    override (``True`` / ``False`` / ``None``).
    """
    fn = getattr(engine, "set_force_host_accessible", None)
    if not callable(fn):
        return None
    return fn(value)


def set_max_pixel_count(max_pixels):
    """Phase 4 D4: cap the per-call pixel count.  Pass ``0`` to clear
    the limit.  Returns the new effective cap.
    """
    fn = getattr(engine, "set_max_pixel_count", None)
    if not callable(fn):
        return 0
    return fn(max_pixels)


def get_auto_promote_decision(size_bytes=1 * 1024 * 1024):
    """Phase 4 D1: return True if the next ``size_bytes`` allocation
    would be auto-promoted to host-accessible (shared) memory.

    The default probe size is 1 MiB.  Returns ``None`` if the engine
    pre-dates Phase 4 D1.
    """
    fn = getattr(engine, "_decide_memory_domain", None)
    if not callable(fn):
        return None
    return bool(fn(int(size_bytes)))


def auto_pipeline(graphs, *, name=None):
    """Return an automatic pipeline scope for multi-stage algorithms.

    The scope chooses direct, recorded, or segmented execution from current
    memory telemetry.  Existing ``module.run`` calls inside the scope do not
    need backend-specific changes.
    """
    return engine.auto_pipeline(graphs, name=name)


def configure_block_reservation(operation, soft_bytes=0, hard_bytes=None, weight=1.0):
    """Set an elastic reservation for one algorithm's future VRAM-resident blocks."""
    return engine.configure_block_reservation(operation, soft_bytes, hard_bytes, weight)


def _mod(name: str):
    """Lazy-load and cache a TCM module by name. Thread-safe via GIL."""
    cached = _module_cache.get(name)
    if cached is not None and (
        getattr(cached, "module_ptr", None)
        and getattr(cached, "engine_generation", None)
        == getattr(engine, "_generation", 0)
    ):
        # CPU AOT artifacts are sometimes materialized under a content hash,
        # so their path stem cannot identify the logical family (``canny``,
        # ``gradients``, ``hough``).  Keep the public module key on the
        # wrapper; the runtime's segmented recorder uses it to bind each
        # graph group to the correct ModuleContext without changing the
        # historical cache key or loading behavior.
        try:
            setattr(cached, "logical_key", str(name))
        except Exception:
            pass
        return cached
    if name in _module_cache:
        _module_cache.pop(name, None)

    if name not in _module_cache:
        # Resolve the target before choosing the root so an installed LLVM20
        # bundle can be selected automatically without changing any public
        # algorithm call.  An explicit root remains authoritative.
        target = detect_target(
            backend=getattr(engine, "arch", "cpu"),
            device=getattr(engine, "gpu_name", ""),
        )
        active_tcm_dir = _tcm_dir
        if not os.environ.get("PIXEL_REFINE_AOT_TCM_ROOT", "").strip():
            try:
                from taichi_vision.llvm20_runtime_paths import tcm_root as staged_tcm_root

                staged_root = staged_tcm_root(target.target_id)
            except (ImportError, OSError, ValueError):
                staged_root = None
            if staged_root is not None:
                active_tcm_dir = os.path.abspath(str(staged_root))
        path_dir = os.path.join(active_tcm_dir, name)
        if os.path.isdir(path_dir):
            _module_cache[name] = engine.load(path_dir)
        else:
            # Prefer an architecture/backend-qualified artifact.  Legacy
            # names remain available for the existing x86 desktop tree while
            # ARM/mobile targets fail clearly instead of loading x86 by
            # accident.
            allow_legacy = (
                # Target-qualified artifacts are the production contract;
                # legacy root files require an explicit opt-in for migration.
                os.environ.get("PIXEL_REFINE_AOT_ALLOW_LEGACY_ARTIFACTS", "0") == "1"
                and not target.is_arm
                and not target.is_mobile
            )
            resolved = resolve_artifact(
                active_tcm_dir,
                name,
                target,
                allow_legacy=allow_legacy,
            )
            if resolved is None:
                raise FileNotFoundError(
                    f"No AOT artifact for target {target.target_id}: "
                    f"algorithm={name!r}, root={active_tcm_dir!r}. "
                    "Compile the target-qualified TCM before dispatch."
                )
            _module_cache[name] = engine.load(str(resolved))
        try:
            setattr(_module_cache[name], "logical_key", str(name))
        except Exception:
            pass
    return _module_cache[name]


def aot_graph_available(module_name: str, graph_name: str) -> bool:
    """Return whether the active target artifact contains a graph.

    This is a preflight helper for optional streaming paths.  It reads the
    packaged graph index only; it does not load or execute a module.  A caller
    can therefore select a validated same-backend full-frame route when an
    older artifact is still installed.
    """
    try:
        target = detect_target(
            backend=getattr(engine, "arch", "cpu"),
            device=getattr(engine, "gpu_name", ""),
        )
        active_tcm_dir = _tcm_dir
        if not os.environ.get("PIXEL_REFINE_AOT_TCM_ROOT", "").strip():
            try:
                from taichi_vision.llvm20_runtime_paths import tcm_root as staged_tcm_root

                staged_root = staged_tcm_root(target.target_id)
            except (ImportError, OSError, ValueError):
                staged_root = None
            if staged_root is not None:
                active_tcm_dir = os.path.abspath(str(staged_root))
        module_dir = os.path.join(active_tcm_dir, str(module_name))
        if os.path.isdir(module_dir):
            # Directory-form modules expose their graph files directly.  Use
            # the same marker scan as ZIP artifacts where possible.
            candidates = [
                os.path.join(module_dir, "graphs.tcb"),
                os.path.join(module_dir, "graphs.json"),
            ]
        else:
            allow_legacy = (
                os.environ.get("PIXEL_REFINE_AOT_ALLOW_LEGACY_ARTIFACTS", "0") == "1"
                and not target.is_arm
                and not target.is_mobile
            )
            resolved = resolve_artifact(
                active_tcm_dir,
                str(module_name),
                target,
                allow_legacy=allow_legacy,
            )
            if resolved is None:
                return False
            candidates = [os.fspath(resolved)]

        marker = str(graph_name).encode("utf-8")
        for candidate in candidates:
            if not os.path.isfile(candidate):
                continue
            if os.path.basename(candidate) in {"graphs.tcb", "graphs.json"}:
                with open(candidate, "rb") as graph_file:
                    data = graph_file.read()
                if marker in data:
                    return True
                continue
            with zipfile.ZipFile(candidate, "r") as archive:
                for index_name in ("graphs.tcb", "graphs.json"):
                    if index_name in archive.namelist() and marker in archive.read(index_name):
                        return True
    except (OSError, RuntimeError, ValueError, zipfile.BadZipFile):
        return False
    return False


def load_tcm(name):
    """Public helper for external callers (backward compat). Uses lazy cache."""
    return _mod(name)


def unload_all_modules():
    """Release all cached TCM modules. Call after heavy processing to free VRAM."""
    _module_cache.clear()
    engine.modules.clear()
    engine.clear_pipelines()


# --- OpenCV-style Constants ---
INTER_NEAREST = 0
INTER_LINEAR = 1
INTER_CUBIC = 2
INTER_AREA = 3
INTER_LANCZOS4 = 4

# --- Core API ---


def upload(arr: np.ndarray, is_vector=False, force_8bit=False) -> TaichiGPUBuffer:
    """Upload a NumPy array to GPU VRAM, optionally forcing 16-bit to 8-bit to optimize memory."""
    if force_8bit and isinstance(arr, np.ndarray) and arr.dtype == np.uint16:
        arr = (arr >> 8).astype(np.uint8)
    return engine.upload(arr, is_vector=is_vector)


# -------------------------------------------------------------------------
# Helper Functions (AOT-Optimized Utility)
# -------------------------------------------------------------------------


def copy_field(src, dst):
    """Zero-overhead AOT copy."""
    is_3ch = len(src.shape) == 3
    is_1d = len(src.shape) == 1
    graph = "copy_i32_1d" if is_1d else "copy_i32_2d"
    dtype_suffix = {
        np.dtype(np.float32): "f32",
        np.dtype(np.int32): "i32",
        np.dtype(np.uint8): "u8",
        np.dtype(np.uint16): "u16",
        np.dtype(np.int16): "i16",
        np.dtype(np.float16): "f16",
    }.get(np.dtype(src.dtype))
    if is_1d and src.dtype == np.float32:
        graph = "copy_f32_1d"
    elif is_3ch and dtype_suffix == "f32":
        graph = "copy_vec3_2d"
    elif is_3ch and dtype_suffix == "i32":
        graph = "copy_vec3_i32_2d"
    elif is_3ch and dtype_suffix:
        graph = f"copy_vec3_{dtype_suffix}_2d"
    elif not is_1d and dtype_suffix == "f32":
        graph = "copy_f32_2d"
    elif not is_1d and dtype_suffix == "i32":
        graph = "copy_i32_2d"
    elif not is_1d and dtype_suffix:
        graph = f"copy_{dtype_suffix}_2d"

    src_v, dst_v = src, dst
    if is_3ch:
        if not getattr(src, "is_vector", False):
            src_v = src.view_as_vector(True)
        if not getattr(dst, "is_vector", False):
            dst_v = dst.view_as_vector(True)

    _mod("common").run(graph, src=src_v, dst=dst_v)


def _common_native_suffix(dtype):
    """Return a compact common-graph suffix for the CPU target only."""

    if str(getattr(engine, "arch", "")).lower() != "cpu":
        return None
    return {
        np.dtype(np.uint8): "u8",
        np.dtype(np.uint16): "u16",
        np.dtype(np.int16): "i16",
        np.dtype(np.float16): "f16",
    }.get(np.dtype(dtype))


def _common_graph_dtype(dtype, *, ndim=None, native_copy=False):
    """Return the dtype currently implemented by the common AOT graphs.

    ``common.tcm`` has portable ``f32``/``i32`` graphs and CPU-only native
    compact data-movement graphs.  Graphics buffers may still be allocated as
    u8/u16/i16/f16, but dispatching those directly to an i32 graph is an ABI
    error.  Keep this policy in one place so backend capability additions do
    not change the public API.
    """

    dtype = np.dtype(dtype)
    if dtype in (np.dtype(np.float32), np.dtype(np.int32)):
        return dtype
    # Native compact copy graphs are currently compiled for CPU 2D/3D
    # arrays only.  Keep 1D and all graphics backends on the portable graph
    # policy until their own capability-qualified archives exist.
    if (
        native_copy
        and str(getattr(engine, "arch", "")).lower() == "cpu"
        and ndim != 1
        and dtype
        in {
            np.dtype(np.uint8),
            np.dtype(np.uint16),
            np.dtype(np.int16),
            np.dtype(np.float16),
        }
    ):
        return dtype
    if np.issubdtype(dtype, np.integer):
        return np.dtype(np.int32)
    if np.issubdtype(dtype, np.floating):
        return np.dtype(np.float32)
    raise TypeError(f"common AOT graphs do not support dtype {dtype}")


def _restore_common_dtype(value, dtype):
    """Restore a common-graph result to the caller's dtype safely."""

    dtype = np.dtype(dtype)
    result = np.asarray(value)
    if np.issubdtype(dtype, np.integer):
        info = np.iinfo(dtype)
        result = np.clip(result, info.min, info.max)
    return result.astype(dtype, copy=False)


def _copy_tile(tile):
    """Run the existing native common-copy graph for one contiguous tile."""
    original_dtype = np.dtype(tile.dtype)
    graph_dtype = _common_graph_dtype(original_dtype, ndim=tile.ndim, native_copy=True)
    graph_tile = np.ascontiguousarray(tile, dtype=graph_dtype)
    src_tile = upload(graph_tile)
    dst_tile = engine.allocate(
        graph_tile.shape,
        dtype=graph_dtype,
        is_vector=tile.ndim == 3,
    )
    try:
        copy_field(src_tile, dst_tile)
        return _restore_common_dtype(dst_tile.to_numpy(), original_dtype)
    finally:
        src_tile.destroy()
        dst_tile.destroy()


def _cached_block_record(block_id, source_checksum, validate_data=None):
    """Resolve RAM first, then the native VRAM tier with integrity checks."""
    cache = engine.get_block_cache()
    record = cache.get(block_id)
    if record is not None:
        # Treat cache metadata as untrusted.  A partially-written tuple
        # checksum (or a scalar checksum attached to a multi-output record)
        # must invalidate the entry rather than raising from ``zip`` or
        # silently validating only the shortest side.  This is important when
        # a process is interrupted while a block result is being promoted to
        # the resident tier.
        try:
            payload = record.data
            if isinstance(payload, (tuple, list)):
                checksums = record.checksum
                checksum_shape_ok = isinstance(checksums, (tuple, list)) and len(
                    checksums
                ) == len(payload)
                checksum_ok = checksum_shape_ok and all(
                    checksum(data) == expected
                    for data, expected in zip(payload, checksums)
                )
            else:
                checksum_ok = (
                    record.checksum is not None and checksum(payload) == record.checksum
                )
            valid = bool(
                record.is_valid()
                and record.source_checksum == source_checksum
                and checksum_ok
            )
        except Exception:
            valid = False
        if valid and validate_data is not None:
            try:
                valid = bool(validate_data(record.data))
            except Exception:
                valid = False
        if valid:
            return record
        cache.invalidate(block_id)

    record = engine.restore_resident_block(block_id, source_checksum)
    if record is not None:
        valid = True
        if validate_data is not None:
            try:
                valid = bool(validate_data(record.data))
            except Exception:
                valid = False
        if valid:
            engine.put_block_record(record)
        else:
            try:
                engine.get_device_block_cache().invalidate(block_id)
            except Exception:
                pass
            record = None
    return record


def _run_blockwise(
    operation,
    arrays,
    output_shape,
    output_dtype,
    run_tile,
    *,
    halo=0,
    params=None,
    validate_output=None,
    cache_outputs=True,
):
    """Run a local operation per tile with optional checksum-backed caching.

    Demosaic callers can disable output-tile caching for constrained-memory
    jobs.  The tile result is still copied into the caller-owned output, but
    no second host/device cache copy is retained after the tile completes.
    The default remains cached for compatibility with existing block users.
    """
    if not arrays or any(array.shape[:2] != arrays[0].shape[:2] for array in arrays):
        raise ValueError("blockwise inputs must share their first two dimensions")

    total_nbytes = sum(array.nbytes for array in arrays)
    grid = engine.plan_blocks(operation, arrays[0].shape, total_nbytes, halo=halo)
    if grid is None:
        return None

    # Large blockwise demosaic outputs can dominate host RSS even though the
    # actual AOT work is tile-bounded.  An explicit path enables a disk-backed
    # result for constrained deployments without changing the default API.
    memmap_path = os.environ.get("PIXEL_REFINE_DEMOSAIC_MEMMAP_PATH", "").strip()
    if memmap_path:
        parent = os.path.dirname(os.path.abspath(memmap_path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        result = np.memmap(
            memmap_path,
            mode="w+",
            dtype=np.dtype(output_dtype),
            shape=output_shape,
        )
    else:
        result = np.empty(output_shape, dtype=output_dtype)
    cache = engine.get_block_cache() if cache_outputs else None
    source_id = "|".join(str(id(array)) for array in arrays)
    # A tile-local checksum used to rescan every input tile before the cache
    # lookup and then rescan the output again.  Compute one fingerprint per
    # source frame instead.  It is conservative (a change anywhere invalidates
    # all tiles) but correct, and reduces checksum work from O(number_of_tiles
    # * frame_bytes) to O(number_of_inputs * frame_bytes).
    source_checksum = (
        tuple(checksum(array) for array in arrays) if cache_outputs else None
    )
    params = {
        "shape": tuple(output_shape),
        "dtype": np.dtype(output_dtype).str,
        **(params or {}),
    }

    blocks = list(grid)
    if cache_outputs:
        blocks.sort(
            key=lambda block: (
                cache.peek(block.make_id(source_id, operation, params)) is None,
                block.index,
            )
        )
    else:
        blocks.sort(key=lambda block: block.index)
    tracker = _BlockExecutionTracker(operation, "host_tile", len(blocks))
    try:
        # Pre-slice tile inputs asynchronously to overlap CPU slicing with GPU dispatch
        next_tile_future = None

        def _fetch_tiles(block):
            return tuple(
                np.ascontiguousarray(array[block.read_slice]) for array in arrays
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            if len(blocks) > 0:
                next_tile_future = executor.submit(_fetch_tiles, blocks[0])

            for idx, block in enumerate(blocks):
                block_id = (
                    block.make_id(source_id, operation, params)
                    if cache_outputs
                    else None
                )
                if cache_outputs:
                    cached = _cached_block_record(
                        block_id,
                        source_checksum,
                        validate_data=lambda data, block=block: (
                            np.asarray(data)[block.core_slice].shape
                            == result[block.write_slice].shape
                        ),
                    )
                    if cached is not None:
                        tracker.cache_hits += 1
                        result[block.write_slice] = cached.data[block.core_slice]
                        if idx + 1 < len(blocks):
                            next_tile_future = executor.submit(
                                _fetch_tiles, blocks[idx + 1]
                            )
                        continue
                    tracker.cache_misses += 1

                # Retrieve pre-fetched input tile
                tiles = (
                    next_tile_future.result()
                    if next_tile_future is not None
                    else _fetch_tiles(block)
                )

                # Immediately pre-fetch the next block's tile inputs
                if idx + 1 < len(blocks):
                    next_tile_future = executor.submit(_fetch_tiles, blocks[idx + 1])

                tracker.input_bytes += sum(int(tile.nbytes) for tile in tiles)

                last_error = None
                for _ in range(2):
                    try:
                        dispatch_started = time.perf_counter()
                        copied = np.ascontiguousarray(run_tile(*tiles))
                        tracker.dispatch_seconds += (
                            time.perf_counter() - dispatch_started
                        )
                        tracker.dispatches += 1
                        if copied.shape[:2] != block.read_shape:
                            raise RuntimeError(
                                "block operation returned an unexpected tile shape"
                            )
                        if validate_output is not None and not validate_output(
                            copied, tiles
                        ):
                            raise RuntimeError(f"{operation} tile validation failed")
                        tracker.output_bytes += int(copied.nbytes)
                        if cache_outputs:
                            engine.put_block_record(
                                BlockRecord(
                                    block_id,
                                    state=BlockState.READY,
                                    data=copied,
                                    checksum=checksum(copied),
                                    source_checksum=source_checksum,
                                    owner=operation,
                                )
                            )
                        result[block.write_slice] = copied[block.core_slice]
                        break
                    except Exception as exc:
                        last_error = exc
                else:
                    engine.quarantine_block_operation(
                        operation,
                        f"block {block.index} failed after retry: {last_error}",
                    )
                    tracker.finish(status="quarantined", error=last_error)
                    return None

        if isinstance(result, np.memmap):
            result.flush()
        tracker.finish()
        return result
    except Exception as exc:
        tracker.finish(status="failed", error=exc)
        raise


def _run_blockwise_gpu(
    operation,
    arrays,
    output_shape,
    output_dtype,
    run_tile,
    *,
    halo=0,
    params=None,
    validate_output=None,
    resident_multiplier=8,
    batch_cap=4,
):
    """Run GPU-returning tiles with bounded deferred synchronization.

    ``run_tile`` must return a live :class:`TaichiGPUBuffer`.  This executor
    deliberately keeps the public NumPy API unchanged: tiles stay resident
    until the batch fence, then are read back and stitched.  The operation's
    intermediate buffers are therefore bounded by the adaptive batch size
    instead of accumulating for the entire image.
    """
    if not arrays or any(array.shape[:2] != arrays[0].shape[:2] for array in arrays):
        raise ValueError("blockwise inputs must share their first two dimensions")

    total_nbytes = sum(array.nbytes for array in arrays)
    grid = engine.plan_blocks(operation, arrays[0].shape, total_nbytes, halo=halo)
    if grid is None:
        return None

    result = np.empty(output_shape, dtype=output_dtype)
    cache = engine.get_block_cache()
    source_id = "|".join(str(id(array)) for array in arrays)
    source_checksum = tuple(checksum(array) for array in arrays)
    params = {
        "shape": tuple(output_shape),
        "dtype": np.dtype(output_dtype).str,
        **(params or {}),
    }
    blocks = list(grid)
    blocks.sort(
        key=lambda block: (
            cache.peek(block.make_id(source_id, operation, params)) is None,
            block.index,
        )
    )
    tracker = _BlockExecutionTracker(operation, "gpu_tile", len(blocks))

    # Generic GPU-tile users (Block Matching, Farneback, and Horn--Schunck)
    # can share the same pre-communication sink as the native LK batch path.
    # The source tile remains algorithm-owned; only its core is scattered into
    # one bounded resident output atlas before a single host readback.
    atlas_enabled = False
    atlas_flow = None
    common_mod = None
    if (
        str(getattr(engine, "arch", "")).lower() in {"vulkan", "cuda"}
        and len(output_shape) == 3
        and np.dtype(output_dtype) == np.dtype(np.float32)
        and os.environ.get("PIXEL_REFINE_AOT_DISABLE_BLOCK_ATLAS") != "1"
    ):
        try:
            common_mod = _mod("common")
            memory = engine.get_memory_status()
            limit = int(memory.get("resident_limit", 0) or 0)
            headroom = int(memory.get("resident_headroom_bytes", 0) or 0)
            atlas_bytes = int(np.prod(output_shape) * np.dtype(output_dtype).itemsize)
            reserve = max(64 * 1024 * 1024, atlas_bytes // 4)
            atlas_cap = 256 * 1024 * 1024
            if limit > 0:
                atlas_cap = min(atlas_cap, max(64 * 1024 * 1024, limit // 4))
            atlas_enabled = atlas_bytes <= atlas_cap and (
                limit <= 0 or atlas_bytes + reserve <= headroom
            )
            if atlas_enabled:
                atlas_flow = engine.allocate(output_shape, dtype=output_dtype)
                tracker.readback_strategy = "atlas"
                tracker.resident_output_bytes = atlas_bytes
        except Exception as atlas_error:
            if atlas_flow is not None:
                try:
                    atlas_flow.destroy()
                except Exception:
                    pass
            atlas_flow = None
            atlas_enabled = False
            common_mod = None
            print(
                f"[{operation}] generic atlas admission failed; "
                f"using tile readback: {atlas_error}"
            )

    pending = []
    atlas_cold_blocks = []
    batch_size = 1
    try:
        # A flow/demosaic tile owns several intermediate buffers in addition
        # to its output.  Reserve a conservative multiplier so batching does
        # not defeat the low-VRAM purpose of block mode.
        block_h, block_w = grid.block_height, grid.block_width
        trailing = tuple(int(value) for value in output_shape[2:])
        tile_bytes = (
            int(block_h * block_w * max(1, int(np.prod(trailing) or 1)))
            * np.dtype(output_dtype).itemsize
        )
        batch_size = engine.recommend_block_batch_size(
            tile_bytes * max(1, int(resident_multiplier)),
            cap=max(1, int(batch_cap)),
        )
    except Exception:
        batch_size = 1

    def flush():
        if not pending:
            return
        if atlas_enabled and atlas_flow is not None and common_mod is not None:
            for block, gpu_tile in pending:
                common_mod.run(
                    "scatter_core_f32_3d",
                    src=gpu_tile,
                    dst=atlas_flow,
                    src_y=int(block.core_slice[0].start),
                    src_x=int(block.core_slice[1].start),
                    dst_y=int(block.y0),
                    dst_x=int(block.x0),
                    core_h=int(block.shape[0]),
                    core_w=int(block.shape[1]),
                )
        sync_started = time.perf_counter()
        engine.sync()
        tracker.sync_seconds += time.perf_counter() - sync_started
        tracker.syncs += 1
        tracker.batches += 1
        if atlas_enabled and atlas_flow is not None:
            atlas_cold_blocks.extend(block for block, _gpu_tile in pending)
            for block, gpu_tile in pending:
                try:
                    gpu_tile.release()
                except Exception:
                    try:
                        gpu_tile.destroy()
                    except Exception:
                        pass
            pending.clear()
            return
        for block, gpu_tile in pending:
            readback_started = time.perf_counter()
            copied = np.ascontiguousarray(gpu_tile.to_numpy())
            tracker.readback_seconds += time.perf_counter() - readback_started
            tracker.output_bytes += int(copied.nbytes)
            if copied.shape[:2] != block.read_shape:
                raise RuntimeError(f"{operation} returned an unexpected GPU tile shape")
            if validate_output is not None and not validate_output(copied, ()):
                raise RuntimeError(f"{operation} tile validation failed")
            block_id = block.make_id(source_id, operation, params)
            engine.put_block_record(
                BlockRecord(
                    block_id,
                    state=BlockState.READY,
                    data=copied,
                    checksum=checksum(copied),
                    source_checksum=source_checksum,
                    owner=operation,
                )
            )
            result[block.write_slice] = copied[block.core_slice]
            try:
                gpu_tile.release()
            except Exception:
                try:
                    gpu_tile.destroy()
                except Exception:
                    pass
        pending.clear()

    try:
        for block in blocks:
            block_id = block.make_id(source_id, operation, params)
            cached = _cached_block_record(
                block_id,
                source_checksum,
                validate_data=lambda data, block=block: (
                    np.asarray(data).shape[:2]
                    in {tuple(block.read_shape), tuple(block.shape)}
                    and np.asarray(data).shape[-1:] == tuple(output_shape[2:])
                ),
            )
            if cached is not None:
                tracker.cache_hits += 1
                if tuple(np.asarray(cached.data).shape[:2]) == tuple(block.shape):
                    result[block.write_slice] = cached.data
                else:
                    result[block.write_slice] = cached.data[block.core_slice]
                continue
            tracker.cache_misses += 1

            tiles = tuple(
                np.ascontiguousarray(array[block.read_slice]) for array in arrays
            )
            tracker.input_bytes += sum(int(tile.nbytes) for tile in tiles)
            last_error = None
            for _ in range(2):
                gpu_tile = None
                try:
                    dispatch_started = time.perf_counter()
                    previous_tracker = getattr(
                        getattr(engine, "_local", None),
                        "block_execution_tracker",
                        None,
                    )
                    if getattr(engine, "_local", None) is not None:
                        engine._local.block_execution_tracker = tracker
                    try:
                        gpu_tile = run_tile(*tiles)
                    finally:
                        if getattr(engine, "_local", None) is not None:
                            engine._local.block_execution_tracker = previous_tracker
                    tracker.dispatch_seconds += time.perf_counter() - dispatch_started
                    tracker.dispatches += 1
                    if not hasattr(gpu_tile, "to_numpy"):
                        raise TypeError(
                            f"{operation} GPU tile runner must return a GPU buffer"
                        )
                    if tuple(gpu_tile.shape[:2]) != tuple(block.read_shape):
                        raise RuntimeError(
                            f"{operation} returned an unexpected GPU tile shape"
                        )
                    pending.append((block, gpu_tile))
                    break
                except Exception as exc:
                    last_error = exc
                    if gpu_tile is not None:
                        try:
                            gpu_tile.destroy()
                        except Exception:
                            pass
            else:
                engine.quarantine_block_operation(
                    operation,
                    f"block {block.index} failed after retry: {last_error}",
                )
                tracker.finish(status="quarantined", error=last_error)
                return None

            if len(pending) >= batch_size:
                flush()
        flush()
        if atlas_enabled and atlas_flow is not None and atlas_cold_blocks:
            readback_started = time.perf_counter()
            atlas_np = np.ascontiguousarray(atlas_flow.to_numpy())
            tracker.readback_seconds += time.perf_counter() - readback_started
            tracker.output_bytes += int(atlas_np.nbytes)
            if atlas_np.shape != output_shape or not np.isfinite(atlas_np).all():
                raise RuntimeError(f"{operation} atlas returned invalid data")
            for block in atlas_cold_blocks:
                core = np.ascontiguousarray(atlas_np[block.write_slice])
                block_id = block.make_id(source_id, operation, params)
                engine.put_block_record(
                    BlockRecord(
                        block_id,
                        state=BlockState.READY,
                        data=core,
                        checksum=checksum(core),
                        source_checksum=source_checksum,
                        owner=operation,
                    )
                )
                result[block.write_slice] = core
        tracker.finish()
        return result
    except Exception as exc:
        tracker.finish(status="failed", error=exc)
        raise
    finally:
        if atlas_flow is not None:
            try:
                atlas_flow.destroy()
            except Exception:
                pass
        if pending:
            try:
                sync_started = time.perf_counter()
                engine.sync()
                tracker.sync_seconds += time.perf_counter() - sync_started
                tracker.syncs += 1
            except Exception:
                pass
            for _block, gpu_tile in pending:
                try:
                    gpu_tile.destroy()
                except Exception:
                    pass
            pending.clear()


def _block_recovery(operation):
    """Retry a specialized block loop once through same-backend full-frame.

    Generic block helpers already return ``None`` after quarantining a failed
    tile.  Specialized loops (resize/remap/pyramid/demosaic-half) contain
    their own dispatch loops, so this decorator gives them the same recovery
    contract without duplicating large loop bodies.
    """
    operation = str(operation)

    def decorate(function):
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            recovering = getattr(engine._local, "block_recovery", None)
            if recovering is None:
                recovering = set()
                engine._local.block_recovery = recovering
            if operation in recovering:
                return function(*args, **kwargs)
            try:
                return function(*args, **kwargs)
            except (RuntimeError, MemoryError) as exc:
                marker = getattr(engine._local, "last_block_plan", None)
                selected = bool(
                    marker
                    and marker.get("operation") == operation
                    and marker.get("selected")
                )
                if not selected:
                    raise
                engine.quarantine_block_operation(operation, str(exc))
                recovering.add(operation)
                try:
                    return function(*args, **kwargs)
                finally:
                    recovering.discard(operation)

        return wrapped

    return decorate


def _vulkan_host_accessible(function):
    """Use host-visible allocations for Vulkan remap graph buffers.

    The Vulkan remap TCM maps its input/output buffers through the native
    bridge.  Device-local allocations are valid for most kernels but are not
    mappable on the affected driver, so remap must temporarily opt into the
    engine's shared-memory policy.  Restore the caller's policy afterwards.
    """
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        if str(getattr(engine, "arch", "")).lower() != "vulkan":
            return function(*args, **kwargs)
        previous = getattr(engine, "_force_host_accessible", None)
        engine.set_force_host_accessible(True)
        try:
            return function(*args, **kwargs)
        finally:
            engine.set_force_host_accessible(previous)

    return wrapped


def _get_cached_output_tile(
    operation, block, source_checksum, params, expected_shape=None
):
    cache = engine.get_block_cache()
    block_id = block.make_id(str(source_checksum), operation, params)
    validator = None
    if expected_shape is not None:
        expected_shape = tuple(int(value) for value in expected_shape)
        validator = lambda data: np.asarray(data).shape == expected_shape
    record = _cached_block_record(block_id, source_checksum, validator)
    if record is not None:
        return record.data
    return None


def _put_cached_output_tile(operation, block, source_checksum, params, data):
    copied = np.ascontiguousarray(data)
    block_id = block.make_id(str(source_checksum), operation, params)
    engine.put_block_record(
        BlockRecord(
            block_id,
            state=BlockState.READY,
            data=copied,
            checksum=checksum(copied),
            source_checksum=source_checksum,
            owner=operation,
        )
    )


def _ordered_cached_output_blocks(operation, grid, source_checksum, params):
    """Visit resident output tiles before cold tiles to prevent scan thrashing."""
    cache = engine.get_block_cache()
    blocks = list(grid)
    blocks.sort(
        key=lambda block: (
            cache.peek(block.make_id(str(source_checksum), operation, params)) is None,
            block.index,
        )
    )
    return blocks


class _BlockExecutionTracker:
    """Low-overhead host-side telemetry for one block invocation.

    The tracker intentionally measures orchestration rather than pretending
    to be a GPU profiler. It separates dispatch, queue waits, and readback
    time so a later atlas/offset implementation can be compared against the
    current tile contract without changing any public algorithm API.
    """

    __slots__ = (
        "operation",
        "mode",
        "block_count",
        "cache_hits",
        "cache_misses",
        "dispatches",
        "batches",
        "syncs",
        "input_bytes",
        "output_bytes",
        "dispatch_seconds",
        "sync_seconds",
        "readback_seconds",
        "started",
        "pipeline_submissions",
        "pipeline_graphs",
        "readback_strategy",
        "resident_output_bytes",
        "finished",
    )

    def __init__(self, operation, mode, block_count):
        self.operation = str(operation)
        self.mode = str(mode)
        self.block_count = int(block_count)
        self.cache_hits = 0
        self.cache_misses = 0
        self.dispatches = 0
        self.batches = 0
        self.syncs = 0
        self.input_bytes = 0
        self.output_bytes = 0
        self.dispatch_seconds = 0.0
        self.sync_seconds = 0.0
        self.readback_seconds = 0.0
        self.pipeline_submissions = 0
        self.pipeline_graphs = 0
        self.readback_strategy = "tile"
        self.resident_output_bytes = 0
        self.started = time.perf_counter()
        self.finished = False

    def finish(self, *, status="ok", error=None):
        if self.finished:
            return
        self.finished = True
        payload = {
            "operation": self.operation,
            "mode": self.mode,
            "status": str(status),
            "block_count": self.block_count,
            "cache_hits": int(self.cache_hits),
            "cache_misses": int(self.cache_misses),
            "dispatches": int(self.dispatches),
            "batches": int(self.batches),
            "syncs": int(self.syncs),
            "input_bytes": int(self.input_bytes),
            "output_bytes": int(self.output_bytes),
            "elapsed_seconds": float(time.perf_counter() - self.started),
            "dispatch_seconds": float(self.dispatch_seconds),
            "sync_seconds": float(self.sync_seconds),
            "readback_seconds": float(self.readback_seconds),
            "readback_strategy": str(self.readback_strategy),
            "resident_output_bytes": int(self.resident_output_bytes),
            "pipeline_submissions": int(self.pipeline_submissions),
            "pipeline_graphs": int(self.pipeline_graphs),
        }
        if error is not None:
            payload["error"] = str(error)[:512]
        try:
            engine.set_last_block_execution(payload)
        except Exception:
            pass


def _run_blockwise_pair(
    operation,
    array,
    run_tile,
    *,
    halo=0,
    params=None,
):
    """Run a local operation that produces two same-sized output tiles."""
    grid = engine.plan_blocks(operation, array.shape, array.nbytes, halo=halo)
    if grid is None:
        return None

    first_result = np.empty(array.shape[:2], dtype=np.float32)
    second_result = np.empty(array.shape[:2], dtype=np.float32)
    cache = engine.get_block_cache()
    source_id = str(id(array))
    source_checksum = checksum(array)
    params = {"shape": tuple(array.shape), "dtype": array.dtype.str, **(params or {})}

    blocks = list(grid)
    blocks.sort(
        key=lambda block: (
            cache.peek(block.make_id(source_id, operation, params)) is None,
            block.index,
        )
    )

    for block in blocks:
        block_id = block.make_id(source_id, operation, params)
        cached = _cached_block_record(
            block_id,
            source_checksum,
            validate_data=lambda data, block=block: (
                isinstance(data, tuple)
                and len(data) == 2
                and all(
                    np.asarray(item)[block.core_slice].shape
                    == first_result[block.write_slice].shape
                    for item in data
                )
            ),
        )
        if (
            cached is not None
            and isinstance(cached.data, tuple)
            and len(cached.data) == 2
        ):
            first_result[block.write_slice] = cached.data[0][block.core_slice]
            second_result[block.write_slice] = cached.data[1][block.core_slice]
            continue

        tile = np.ascontiguousarray(array[block.read_slice])

        last_error = None
        for _ in range(2):
            try:
                outputs = tuple(
                    np.ascontiguousarray(output) for output in run_tile(tile)
                )
                if len(outputs) != 2 or any(
                    output.shape[:2] != block.read_shape for output in outputs
                ):
                    raise RuntimeError(
                        "block operation returned unexpected output tiles"
                    )
                engine.put_block_record(
                    BlockRecord(
                        block_id,
                        state=BlockState.READY,
                        data=outputs,
                        checksum=tuple(checksum(output) for output in outputs),
                        source_checksum=source_checksum,
                        owner=operation,
                    )
                )
                first_result[block.write_slice] = outputs[0][block.core_slice]
                second_result[block.write_slice] = outputs[1][block.core_slice]
                break
            except Exception as exc:
                last_error = exc
        else:
            engine.quarantine_block_operation(
                operation,
                f"block {block.index} failed after retry: {last_error}",
            )
            return None

    return first_result, second_result


def _run_blockwise_triplet(operation, array, run_tile, *, params=None):
    """Run a local operation that produces three same-sized output tiles."""
    grid = engine.plan_blocks(operation, array.shape, array.nbytes)
    if grid is None:
        return None

    results = tuple(np.empty(array.shape[:2], dtype=array.dtype) for _ in range(3))
    cache = engine.get_block_cache()
    source_id = str(id(array))
    source_checksum = checksum(array)
    params = {"shape": tuple(array.shape), "dtype": array.dtype.str, **(params or {})}

    blocks = list(grid)
    blocks.sort(
        key=lambda block: (
            cache.peek(block.make_id(source_id, operation, params)) is None,
            block.index,
        )
    )
    for block in blocks:
        block_id = block.make_id(source_id, operation, params)
        cached = _cached_block_record(
            block_id,
            source_checksum,
            validate_data=lambda data, block=block: (
                isinstance(data, tuple)
                and len(data) == 3
                and all(
                    np.asarray(item)[block.core_slice].shape
                    == results[0][block.write_slice].shape
                    for item in data
                )
            ),
        )
        if (
            cached is not None
            and isinstance(cached.data, tuple)
            and len(cached.data) == 3
        ):
            for result, output in zip(results, cached.data):
                result[block.write_slice] = output[block.core_slice]
            continue

        tile = np.ascontiguousarray(array[block.read_slice])

        last_error = None
        for _ in range(2):
            try:
                outputs = tuple(
                    np.ascontiguousarray(output) for output in run_tile(tile)
                )
                if len(outputs) != 3 or any(
                    output.shape[:2] != block.read_shape for output in outputs
                ):
                    raise RuntimeError(
                        "block operation returned unexpected output tiles"
                    )
                engine.put_block_record(
                    BlockRecord(
                        block_id,
                        state=BlockState.READY,
                        data=outputs,
                        checksum=tuple(checksum(output) for output in outputs),
                        source_checksum=source_checksum,
                        owner=operation,
                    )
                )
                for result, output in zip(results, outputs):
                    result[block.write_slice] = output[block.core_slice]
                break
            except Exception as exc:
                last_error = exc
        else:
            engine.quarantine_block_operation(
                operation,
                f"block {block.index} failed after retry: {last_error}",
            )
            return None

    return results


def copy(src, return_gpu=False):
    """Copy an array, dispatching large NumPy inputs through AOT tiles."""
    if isinstance(src, TaichiGPUBuffer):
        dst = engine.allocate(
            src.shape,
            dtype=src.dtype,
            is_vector=getattr(src, "is_vector", False),
            vector_dim=getattr(src, "vector_dim", None),
        )
        copy_field(src, dst)
        return dst

    array = np.ascontiguousarray(src)
    grid = engine.plan_blocks("copy", array.shape, array.nbytes)
    if grid is None:
        result = _copy_tile(array)
        return upload(result, is_vector=array.ndim == 3) if return_gpu else result

    result = _run_blockwise(
        "copy",
        (array,),
        array.shape,
        array.dtype,
        _copy_tile,
        validate_output=lambda copied, tiles: checksum(copied) == checksum(tiles[0]),
    )

    return upload(result) if return_gpu else result


def _extract_channel_tile(tile, ch):
    original_dtype = np.dtype(tile.dtype)
    graph_dtype = _common_graph_dtype(original_dtype, ndim=tile.ndim, native_copy=True)
    src_tile = upload(np.ascontiguousarray(tile, dtype=graph_dtype))
    try:
        dst_tile = extract_channel(src_tile, ch)
        try:
            return _restore_common_dtype(dst_tile.to_numpy(), original_dtype)
        finally:
            dst_tile.destroy()
    finally:
        src_tile.destroy()


def extract_channel(src, ch):
    """AOT Optimized channel extraction."""
    if not isinstance(src, TaichiGPUBuffer):
        array = np.ascontiguousarray(src)
        if array.ndim != 3 or array.shape[2] != 3:
            raise ValueError("extract_channel expects an HxWx3 array")
        if not 0 <= int(ch) < 3:
            raise ValueError("channel index must be in [0, 2]")
        result = _run_blockwise(
            "extract_channel",
            (array,),
            array.shape[:2],
            array.dtype,
            lambda tile: _extract_channel_tile(tile, ch),
            params={"ch": int(ch)},
        )
        if result is not None:
            return result
        original_dtype = np.dtype(array.dtype)
        graph_dtype = _common_graph_dtype(
            original_dtype, ndim=array.ndim, native_copy=True
        )
        src_buf = upload(np.ascontiguousarray(array, dtype=graph_dtype))
        try:
            dst_buf = extract_channel(src_buf, ch)
            try:
                return _restore_common_dtype(dst_buf.to_numpy(), original_dtype)
            finally:
                dst_buf.destroy()
        finally:
            src_buf.destroy()

    h, w = src.shape[0], src.shape[1]
    dst = engine.allocate((h, w), dtype=src.dtype)
    src_v = src
    if len(src.shape) == 3 and not getattr(src, "is_vector", False):
        src_v = src.view_as_vector(True)

    suffix = _common_native_suffix(src.dtype)
    graph = (
        f"extract_channel_{suffix}"
        if suffix
        else (
            "extract_channel_f32" if src.dtype == np.float32 else "extract_channel_i32"
        )
    )
    _mod("common").run(graph, src=src_v, dst=dst, ch=int(ch))
    return dst


def _split_3ch_tile(tile):
    original_dtype = np.dtype(tile.dtype)
    graph_dtype = _common_graph_dtype(original_dtype, ndim=tile.ndim, native_copy=True)
    src_tile = upload(np.ascontiguousarray(tile, dtype=graph_dtype))
    try:
        channels = split_3ch(src_tile)
        try:
            return tuple(
                _restore_common_dtype(channel.to_numpy(), original_dtype)
                for channel in channels
            )
        finally:
            for channel in channels:
                channel.destroy()
    finally:
        src_tile.destroy()


def split_3ch(src):
    """Fused 3-channel split."""
    if not isinstance(src, TaichiGPUBuffer):
        array = np.ascontiguousarray(src)
        if array.ndim != 3 or array.shape[2] != 3:
            raise ValueError("split_3ch expects an HxWx3 array")
        result = _run_blockwise_triplet("split_3ch", array, _split_3ch_tile)
        if result is not None:
            return list(result)
        original_dtype = np.dtype(array.dtype)
        graph_dtype = _common_graph_dtype(
            original_dtype, ndim=array.ndim, native_copy=True
        )
        src_buf = upload(np.ascontiguousarray(array, dtype=graph_dtype))
        try:
            channels = split_3ch(src_buf)
            try:
                return [
                    _restore_common_dtype(channel.to_numpy(), original_dtype)
                    for channel in channels
                ]
            finally:
                for channel in channels:
                    channel.destroy()
        finally:
            src_buf.destroy()

    h, w = src.shape[0], src.shape[1]
    dst_dtype = src.dtype
    c0 = engine.allocate((h, w), dtype=dst_dtype)
    c1 = engine.allocate((h, w), dtype=dst_dtype)
    c2 = engine.allocate((h, w), dtype=dst_dtype)
    src_v = src
    if not getattr(src, "is_vector", False):
        src_v = src.view_as_vector(True)

    suffix = _common_native_suffix(dst_dtype)
    graph = (
        f"split_3ch_{suffix}"
        if suffix
        else ("split_3ch_f32" if dst_dtype == np.float32 else "split_3ch_i32")
    )
    _mod("common").run(graph, src=src_v, c0=c0, c1=c1, c2=c2)
    return [c0, c1, c2]


def _merge_3ch_tile(c0_tile, c1_tile, c2_tile):
    original_dtype = np.dtype(c0_tile.dtype)
    graph_dtype = _common_graph_dtype(
        original_dtype, ndim=c0_tile.ndim, native_copy=True
    )
    channels = [
        upload(np.ascontiguousarray(tile, dtype=graph_dtype))
        for tile in (c0_tile, c1_tile, c2_tile)
    ]
    try:
        dst_tile = merge_3ch(*channels)
        try:
            return _restore_common_dtype(dst_tile.to_numpy(), original_dtype)
        finally:
            dst_tile.destroy()
    finally:
        for channel in channels:
            channel.destroy()


def merge_3ch(c0, c1, c2):
    """Fused 3-channel merge."""
    if not isinstance(c0, TaichiGPUBuffer):
        channels = tuple(np.ascontiguousarray(channel) for channel in (c0, c1, c2))
        if any(channel.ndim != 2 for channel in channels):
            raise ValueError("merge_3ch expects three 2D arrays")
        if any(
            channel.shape != channels[0].shape or channel.dtype != channels[0].dtype
            for channel in channels[1:]
        ):
            raise ValueError("merge_3ch channels must have matching shape and dtype")
        result = _run_blockwise(
            "merge_3ch",
            channels,
            (*channels[0].shape, 3),
            channels[0].dtype,
            _merge_3ch_tile,
        )
        if result is not None:
            return result
        original_dtype = np.dtype(channels[0].dtype)
        graph_dtype = _common_graph_dtype(
            original_dtype, ndim=channels[0].ndim, native_copy=True
        )
        buffers = [
            upload(np.ascontiguousarray(channel, dtype=graph_dtype))
            for channel in channels
        ]
        try:
            dst_buf = merge_3ch(*buffers)
            try:
                return _restore_common_dtype(dst_buf.to_numpy(), original_dtype)
            finally:
                dst_buf.destroy()
        finally:
            for buffer in buffers:
                buffer.destroy()

    h, w = c0.shape[0], c0.shape[1]
    dst_dtype = c0.dtype
    dst = engine.allocate((h, w, 3), dtype=dst_dtype, is_vector=True, vector_dim=3)

    suffix = _common_native_suffix(dst_dtype)
    graph = (
        f"merge_3ch_{suffix}"
        if suffix
        else ("merge_3ch_f32" if dst_dtype == np.float32 else "merge_3ch_i32")
    )
    _mod("common").run(graph, c0=c0, c1=c1, c2=c2, dst=dst.view_as_vector(True, 3))
    return dst


def _rgb2gray_tile(tile):
    original_dtype = np.dtype(tile.dtype)
    graph_dtype = _common_graph_dtype(original_dtype)
    graph_tile = np.ascontiguousarray(tile, dtype=graph_dtype)
    src_tile = upload(graph_tile)
    dst_tile = engine.allocate(tile.shape[:2], dtype=graph_dtype)
    try:
        src_vector = src_tile.view_as_vector(True, 3)
        graph = (
            "rgb2gray_f32" if graph_dtype == np.dtype(np.float32) else "rgb2gray_i32"
        )
        _mod("common").run(graph, src=src_vector, dst=dst_tile)
        return _restore_common_dtype(dst_tile.to_numpy(), original_dtype)
    finally:
        src_tile.destroy()
        dst_tile.destroy()


def _insert_channel_tile(src_tile, dst_tile, ch):
    original_dtype = np.dtype(src_tile.dtype)
    graph_dtype = _common_graph_dtype(
        original_dtype, ndim=src_tile.ndim, native_copy=True
    )
    src_buf = upload(np.ascontiguousarray(src_tile, dtype=graph_dtype))
    dst_buf = upload(np.ascontiguousarray(dst_tile, dtype=graph_dtype))
    try:
        insert_channel(src_buf, dst_buf, ch)
        return _restore_common_dtype(dst_buf.to_numpy(), original_dtype)
    finally:
        src_buf.destroy()
        dst_buf.destroy()


def insert_channel(src, dst, ch):
    """AOT Optimized channel insertion (in-place on GPU)."""
    if not isinstance(src, TaichiGPUBuffer):
        source = np.ascontiguousarray(src)
        if not isinstance(dst, np.ndarray) or dst.ndim != 3 or dst.shape[2] != 3:
            raise ValueError("insert_channel destination must be an HxWx3 NumPy array")
        if source.shape != dst.shape[:2] or source.dtype != dst.dtype:
            raise ValueError(
                "insert_channel source must match destination size and dtype"
            )
        if not 0 <= int(ch) < 3:
            raise ValueError("channel index must be in [0, 2]")
        destination = np.ascontiguousarray(dst)
        result = _run_blockwise(
            "insert_channel",
            (source, destination),
            destination.shape,
            destination.dtype,
            lambda source_tile, destination_tile: _insert_channel_tile(
                source_tile, destination_tile, ch
            ),
            params={"ch": int(ch)},
        )
        if result is None:
            original_dtype = np.dtype(source.dtype)
            graph_dtype = _common_graph_dtype(
                original_dtype, ndim=source.ndim, native_copy=True
            )
            src_buf = upload(np.ascontiguousarray(source, dtype=graph_dtype))
            dst_buf = upload(np.ascontiguousarray(destination, dtype=graph_dtype))
            try:
                insert_channel(src_buf, dst_buf, ch)
                result = _restore_common_dtype(dst_buf.to_numpy(), original_dtype)
            finally:
                src_buf.destroy()
                dst_buf.destroy()
        dst[...] = result
        return dst

    src_v = src
    dst_v = dst
    if len(dst.shape) == 3 and not getattr(dst, "is_vector", False):
        dst_v = dst.view_as_vector(True)

    suffix = _common_native_suffix(src.dtype)
    graph = (
        f"insert_channel_{suffix}"
        if suffix
        else ("insert_channel_f32" if src.dtype == np.float32 else "insert_channel_i32")
    )
    _mod("common").run(graph, src=src_v, dst=dst_v, ch=int(ch))


def generate_hanning_window_2d(
    shape, exclude_boundary=False, dtype=np.float32
) -> TaichiGPUBuffer:
    """AOT Optimized 2D Hanning window generation."""
    h, w = shape
    dst = engine.allocate((h, w), dtype=dtype)
    _mod("common").run(
        "generate_hanning_window_2d",
        dst=dst,
        H=int(h),
        W=int(w),
        exclude_boundary=int(exclude_boundary),
    )
    return dst


def mean_division(
    sum_img: TaichiGPUBuffer,
    sum_weight: TaichiGPUBuffer,
    ref_img: TaichiGPUBuffer,
    dst: TaichiGPUBuffer = None,
) -> TaichiGPUBuffer:
    """AOT Optimized final mean division and fallback."""
    if dst is None:
        dst = engine.allocate(
            sum_img.shape,
            dtype=sum_img.dtype,
            is_vector=getattr(sum_img, "is_vector", False),
            vector_dim=getattr(sum_img, "vector_dim", 1),
        )

    is_vec = len(sum_img.shape) == 3 or getattr(sum_img, "is_vector", False)
    graph = "mean_division_vec3_f32" if is_vec else "mean_division_f32"

    sum_img_v = sum_img
    ref_img_v = ref_img
    dst_v = dst

    if is_vec:
        if not getattr(sum_img, "is_vector", False):
            sum_img_v = sum_img.view_as_vector(True)
        if not getattr(ref_img, "is_vector", False):
            ref_img_v = ref_img.view_as_vector(True)
        if not getattr(dst, "is_vector", False):
            dst_v = dst.view_as_vector(True)

    _mod("common").run(
        graph, sum_img=sum_img_v, sum_weight=sum_weight, ref_img=ref_img_v, dst=dst_v
    )
    return dst


def normalize_accumulator(
    sum_img: TaichiGPUBuffer, sum_weight: TaichiGPUBuffer, dst: TaichiGPUBuffer = None
) -> TaichiGPUBuffer:
    """Fast normalize for fully-covered tiled accumulators."""
    if dst is None:
        dst = engine.allocate(
            sum_img.shape,
            dtype=sum_img.dtype,
            is_vector=getattr(sum_img, "is_vector", False),
            vector_dim=getattr(sum_img, "vector_dim", 1),
        )

    is_vec = len(sum_img.shape) == 3 or getattr(sum_img, "is_vector", False)
    graph = "normalize_accum_vec3_f32" if is_vec else "normalize_accum_f32"

    sum_img_v = sum_img
    dst_v = dst
    if is_vec:
        if not getattr(sum_img, "is_vector", False):
            sum_img_v = sum_img.view_as_vector(True)
        if not getattr(dst, "is_vector", False):
            dst_v = dst.view_as_vector(True)

    try:
        _mod("common").run(graph, sum_img=sum_img_v, sum_weight=sum_weight, dst=dst_v)
    except Exception:
        return mean_division(sum_img, sum_weight, sum_img, dst=dst)
    return dst


# ---------------------------------------------------------------------------
# Spatial Merging — Ghost Reduction & Multi-Frame Fusion
# ---------------------------------------------------------------------------
# Canonical implementation lives in taichi_vision.taichi_algorithm.spatial_fusion.
# These wrappers expose the public API as ``taichi_aot.spatial_merging`` and
# related low-level helpers.


def spatial_merging(*args, **kwargs):
    """Ghost-reduction spatial merging for multi-frame burst fusion.

    Exposed as ``taichi_aot.spatial_merging``.  See
    ``taichi_vision.taichi_algorithm.spatial_fusion.spatial_merging`` for the
    full signature.  Two modes:

        mode="weights"  → frame-by-frame: one weight map per support frame
                          (ghost rejection baked in).
        mode="fuse"     → batch: fused RGB result from all support frames.

    Noise & motion thresholds auto-estimate from the reference when not given.
    """
    from taichi_vision.taichi_algorithm.spatial_fusion.spatial_merging import (
        spatial_merging as _spatial_merging,
    )

    return _spatial_merging(*args, **kwargs)


def generate_spatial_weights(*args, **kwargs):
    """Generate a ghost-rejection weight map for one frame (low-level)."""
    from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (
        generate_spatial_weights_taichi,
    )

    return generate_spatial_weights_taichi(*args, **kwargs)


def accumulate_spatial_merging(*args, **kwargs):
    """Accumulate one frame into a fusion sum with its weight map (low-level).

    Auto-dispatches to the vec3 per-channel kernel when the weight map is 3D.
    """
    from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (
        accumulate_spatial_merging_taichi,
    )

    return accumulate_spatial_merging_taichi(*args, **kwargs)


def mean_division_vec3_weight(*args, **kwargs):
    """Per-channel GPU mean division with reference fallback (low-level)."""
    from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (
        mean_division_vec3_weight_taichi,
    )

    return mean_division_vec3_weight_taichi(*args, **kwargs)


def SpatialScratchCache(*args, **kwargs):
    """Reusable per-batch GPU scratch buffers for spatial analysis (low-level)."""
    from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (
        SpatialScratchCache as _SpatialScratchCache,
    )

    return _SpatialScratchCache(*args, **kwargs)


def estimate_spatial_noise_sigma(*args, **kwargs):
    """Estimate image noise sigma via Laplacian MAD (low-level)."""
    from taichi_vision.taichi_algorithm.spatial_fusion.noise_estimation import (
        estimate_noise_sigma,
    )

    return estimate_noise_sigma(*args, **kwargs)


def compile_spatial_merging_tcm(*args, **kwargs):
    """Compile and package the spatial-merging AOT TCM (build-time helper)."""
    from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (
        compile_spatial_tcm,
    )

    return compile_spatial_tcm(*args, **kwargs)


def stitch_tile(
    tile: TaichiGPUBuffer,
    tile_weight: TaichiGPUBuffer,
    hanning: TaichiGPUBuffer,
    accum: TaichiGPUBuffer,
    weight_accum: TaichiGPUBuffer,
    y0: int,
    x0: int,
) -> None:
    """AOT Optimized tile stitching."""
    h, w = tile.shape[:2]
    is_vec = len(tile.shape) == 3 or getattr(tile, "is_vector", False)
    graph = "stitch_tile_vec3" if is_vec else "stitch_tile_f32"

    tile_v = tile
    accum_v = accum
    if is_vec:
        if not getattr(tile, "is_vector", False):
            tile_v = tile.view_as_vector(True)
        if not getattr(accum, "is_vector", False):
            accum_v = accum.view_as_vector(True)

    _mod("common").run(
        graph,
        tile=tile_v,
        tile_weight=tile_weight,
        hanning=hanning,
        accum=accum_v,
        weight_accum=weight_accum,
        y0=int(y0),
        x0=int(x0),
        h=int(h),
        w=int(w),
    )


def stitch_tile_normalized(
    tile: TaichiGPUBuffer,
    tile_weight: TaichiGPUBuffer,
    hanning: TaichiGPUBuffer,
    accum: TaichiGPUBuffer,
    weight_accum: TaichiGPUBuffer,
    y0: int,
    x0: int,
) -> None:
    """Tile stitching with running weighted-average normalization."""
    h, w = tile.shape[:2]
    is_vec = len(tile.shape) == 3 or getattr(tile, "is_vector", False)
    graph = "stitch_tile_normalized_vec3" if is_vec else "stitch_tile_normalized_f32"

    tile_v = tile
    accum_v = accum
    if is_vec:
        if not getattr(tile, "is_vector", False):
            tile_v = tile.view_as_vector(True)
        if not getattr(accum, "is_vector", False):
            accum_v = accum.view_as_vector(True)

    _mod("common").run(
        graph,
        tile=tile_v,
        tile_weight=tile_weight,
        hanning=hanning,
        accum=accum_v,
        weight_accum=weight_accum,
        y0=int(y0),
        x0=int(x0),
        h=int(h),
        w=int(w),
    )


# NumPy-like aliases for JIT/AOT consistency
hanning = generate_hanning_window_2d
divide = mean_division


def rgb2gray(src, dst=None):
    """AOT Optimized RGB to Gray conversion."""
    if not isinstance(src, TaichiGPUBuffer):
        array = np.ascontiguousarray(src)
        if array.ndim != 3 or array.shape[2] != 3:
            raise ValueError("rgb2gray requires an HxWx3 array")
        result = _run_blockwise(
            "rgb2gray",
            (array,),
            array.shape[:2],
            array.dtype,
            _rgb2gray_tile,
        )
        if result is not None:
            return result

        original_dtype = np.dtype(array.dtype)
        graph_dtype = _common_graph_dtype(original_dtype)
        source_for_aot = np.ascontiguousarray(array, dtype=graph_dtype)
        src_buffer = upload(source_for_aot)
        output = rgb2gray(src_buffer, dst=None)
        try:
            return _restore_common_dtype(output.to_numpy(), original_dtype)
        finally:
            src_buffer.destroy()
            if dst is None:
                output.destroy()

    h, w = src.shape[0], src.shape[1]
    if dst is None:
        dst = engine.allocate((h, w), dtype=src.dtype)
    src_v = src
    if len(src.shape) == 3 and not getattr(src, "is_vector", False):
        src_v = src.view_as_vector(True)

    graph = "rgb2gray_f32" if src.dtype == np.float32 else "rgb2gray_i32"
    _mod("common").run(graph, src=src_v, dst=dst)
    return dst


def _absdiff_tile(first, second):
    first_tile = upload(first)
    second_tile = upload(second)
    try:
        output = absdiff(first_tile, second_tile)
        try:
            return output.to_numpy()
        finally:
            output.destroy()
    finally:
        first_tile.destroy()
        second_tile.destroy()


def absdiff(src1, src2):
    """AOT Optimized absolute difference."""
    inputs_are_gpu = isinstance(src1, TaichiGPUBuffer) and isinstance(
        src2, TaichiGPUBuffer
    )
    if not inputs_are_gpu:
        if isinstance(src1, TaichiGPUBuffer) or isinstance(src2, TaichiGPUBuffer):
            raise TypeError("absdiff inputs must both be NumPy arrays or GPU buffers")
        first = np.ascontiguousarray(src1)
        second = np.ascontiguousarray(src2)
        if first.shape != second.shape or first.dtype != second.dtype:
            raise ValueError("absdiff inputs must have matching shape and dtype")
        result = _run_blockwise(
            "absdiff",
            (first, second),
            first.shape,
            first.dtype,
            _absdiff_tile,
        )
        if result is not None:
            return result

        first_buffer = upload(first)
        second_buffer = upload(second)
        output = absdiff(first_buffer, second_buffer)
        try:
            return output.to_numpy()
        finally:
            first_buffer.destroy()
            second_buffer.destroy()
            output.destroy()

    is_3d = len(src1.shape) == 3
    dst = engine.allocate(src1.shape, dtype=src1.dtype, is_vector=is_3d)

    src1_v, src2_v, dst_v = src1, src2, dst
    if is_3d:
        if not getattr(src1, "is_vector", False):
            src1_v = src1.view_as_vector(True, 3)
        if not getattr(src2, "is_vector", False):
            src2_v = src2.view_as_vector(True, 3)
        if not getattr(dst, "is_vector", False):
            dst_v = dst.view_as_vector(True, 3)
        graph = "absdiff_vec3_f32"
    else:
        graph = "absdiff_f32_2d" if src1.dtype == np.float32 else "absdiff_i32_2d"

    _mod("common").run(graph, src1=src1_v, src2=src2_v, dst=dst_v)
    return dst


def _cvt_gray_tile(tile, code):
    """Run one BGR/RGB-to-gray tile through the common AOT graph."""
    owner = engine.upload(np.ascontiguousarray(tile, dtype=np.float32))
    source = owner.view_as_vector(True, 3)
    dst = engine.allocate(tile.shape[:2], dtype=np.float32)
    try:
        graph = "rgb2gray_f32" if int(code) == COLOR_RGB2GRAY else "bgr2gray_f32"
        _mod("common").run(graph, src=source, dst=dst)
        return dst.to_numpy()
    finally:
        dst.destroy()
        owner.destroy()


def cvtColor(src, code):
    """AOT Optimized color conversion (OpenCV Parity)."""
    # OpenCV Constants
    COLOR_BGR2GRAY = 6
    COLOR_RGB2GRAY = 7

    is_host = isinstance(src, np.ndarray)
    if isinstance(src, TaichiGPUBuffer) and np.dtype(src.dtype) != np.dtype(np.float32):
        import cv2

        result = cv2.cvtColor(src.to_numpy(), code)
        return upload(np.ascontiguousarray(result))
    # Common grayscale graphs are compiled for f32. Normalize integer host
    # inputs before dispatch so u8/int16 images work on every backend.
    if isinstance(src, np.ndarray) and np.issubdtype(src.dtype, np.integer):
        src_buf = InputArray(np.ascontiguousarray(src, dtype=np.float32))
    else:
        src_buf = InputArray(src)
    owned_src_f32 = False
    if np.dtype(src_buf.dtype) != np.dtype(np.float32):
        src_buf = engine.upload(
            np.ascontiguousarray(src_buf.to_numpy(), dtype=np.float32)
        )
        owned_src_f32 = True

    if code in [COLOR_BGR2GRAY, COLOR_RGB2GRAY]:
        if is_host:
            source_array = np.ascontiguousarray(src, dtype=np.float32)
            if source_array.ndim != 3 or source_array.shape[2] != 3:
                raise ValueError("cvtColor grayscale conversion expects HxWx3 input")
            result = _run_blockwise(
                "cvtColor",
                (source_array,),
                source_array.shape[:2],
                np.float32,
                lambda tile: _cvt_gray_tile(tile, code),
                params={"code": int(code)},
            )
            if result is not None:
                # ``src_buf`` was prepared before the block decision for the
                # legacy full-frame path.  Retire it explicitly when the
                # block path succeeds so the cache does not retain an extra
                # full-frame upload.
                src_buf.destroy()
                return result
        h, w = src_buf.shape[0], src_buf.shape[1]
        dst = OutputArray((h, w), dtype=src_buf.dtype)
        src_v = src_buf
        if len(src_buf.shape) == 3 and not getattr(src_buf, "is_vector", False):
            src_v = src_buf.view_as_vector(True, 3)

        graph = "rgb2gray_f32" if code == COLOR_RGB2GRAY else "bgr2gray_f32"
        _mod("common").run(graph, src=src_v, dst=dst)
        if is_host:
            try:
                return dst.to_numpy()
            finally:
                src_buf.destroy()
                dst.destroy()
        if owned_src_f32:
            src_buf.destroy()
        return dst

    return src


# -------------------------------------------------------------------------
# Algorithm APIs
# -------------------------------------------------------------------------


def normalize_image(
    src: InputArray, dtype: np.dtype, out: OutputArray = None
) -> TaichiGPUBuffer:
    """High-level normalization [0, 1] using AOT."""
    from taichi_vision.taichi_algorithm.alignment.taichi_bridge import (
        normalize_image_gpu,
    )

    src_gpu = upload(src) if not isinstance(src, TaichiGPUBuffer) else src
    return normalize_image_gpu(src_gpu, dtype, out_gpu=out)


def to_gamma_proxy(
    src: InputArray, scale: float = 1.0, out: OutputArray = None
) -> TaichiGPUBuffer:
    """High-level Gamma Proxy transformation using AOT."""
    from taichi_vision.taichi_algorithm.alignment.taichi_bridge import (
        to_gamma_proxy_gpu,
    )

    src_gpu = upload(src) if not isinstance(src, TaichiGPUBuffer) else src
    return to_gamma_proxy_gpu(src_gpu, scale=scale, dst_gpu=out)


class _BlockTileArena:
    """Reuse a bounded set of GPU tile buffers during one block operation.

    The previous tiled paths allocated and destroyed the output buffer for
    every block.  The engine's pool can reuse the native handle eventually,
    but the Python wrapper and lifecycle bookkeeping still happened once per
    tile.  This operation-local arena keeps those wrappers alive and returns
    them only after a batch has been synchronized and read back.
    """

    def __init__(self, runtime):
        self.runtime = runtime
        self._free = {}
        self._all = []

    @staticmethod
    def _key(shape, dtype, is_vector, vector_dim):
        return (
            tuple(int(value) for value in shape),
            np.dtype(dtype).str,
            bool(is_vector),
            int(vector_dim),
        )

    def acquire(self, shape, *, dtype=np.float32, is_vector=False, vector_dim=3):
        key = self._key(shape, dtype, is_vector, vector_dim)
        slots = self._free.setdefault(key, [])
        if slots:
            return slots.pop()
        buffer = self.runtime.allocate(
            shape,
            dtype=dtype,
            is_vector=is_vector,
            vector_dim=vector_dim,
        )
        self._all.append(buffer)
        return buffer

    def release(self, buffer):
        if buffer is None:
            return
        key = self._key(
            buffer.shape,
            buffer.dtype,
            getattr(buffer, "is_vector", False),
            getattr(buffer, "vector_dim", 3),
        )
        self._free.setdefault(key, []).append(buffer)

    def close(self):
        for buffer in self._all:
            try:
                buffer.destroy()
            except Exception:
                pass
        self._all.clear()
        self._free.clear()


def _flush_offset_batch(
    operation,
    pending,
    result,
    source_crc,
    cache_params,
    arena,
    *,
    validate_output=None,
    tracker=None,
):
    """Synchronize and merge one group of offset-dispatched output tiles.

    Resize and fused remap use the same contract: the source buffers remain
    resident, each graph writes one output tile at an offset, and the host
    only waits once for the whole bounded batch.  Keeping this lifecycle in a
    single helper avoids subtly different release/sync behaviour between
    algorithms.
    """
    if not pending:
        return
    # One queue wait for all dispatches in the batch. Each readback below is
    # then a host copy, not a separate GPU completion point.
    sync_started = time.perf_counter()
    engine.sync()
    if tracker is not None:
        tracker.sync_seconds += time.perf_counter() - sync_started
        tracker.syncs += 1
        tracker.batches += 1
    for block, tile_buf in pending:
        readback_started = time.perf_counter()
        tile_result = tile_buf.to_numpy()
        if tracker is not None:
            tracker.readback_seconds += time.perf_counter() - readback_started
            tracker.output_bytes += int(np.asarray(tile_result).nbytes)
        if validate_output is not None and not validate_output(tile_result, block):
            raise RuntimeError(f"{operation} tile validation failed")
        result[block.write_slice] = tile_result
        _put_cached_output_tile(operation, block, source_crc, cache_params, tile_result)
        arena.release(tile_buf)
    pending.clear()


def _flush_resize_batch(
    pending, result, source_crc, cache_params, arena, *, tracker=None
):
    """Compatibility wrapper for the existing resize call sites."""
    return _flush_offset_batch(
        "resize",
        pending,
        result,
        source_crc,
        cache_params,
        arena,
        tracker=tracker,
    )


def _resize_bilinear_batch_offset(
    source,
    source_f32,
    src_view,
    grid,
    target_h,
    target_w,
    output_shape,
    source_crc,
    cache_params,
):
    """Evaluate linear-resize tiles in bounded batched offset graphs.

    The graph consumes one resident source frame and an ``(N, 2)`` offset
    table.  It writes ``N`` output tiles in one dispatch, eliminating one
    graph launch per tile while retaining the existing cache and stitch
    contract.  ``None`` means the optional batch artifact is unavailable;
    callers then use the established offset executor.
    """
    try:
        batch_mod = _mod("bilinear_batch")
    except FileNotFoundError:
        return None

    source_ndim = int(source.ndim)
    is_vector = source_ndim == 3
    batch_graph = (
        "bilinear_resize_batch_offset_f32_3d"
        if is_vector
        else "bilinear_resize_batch_offset_f32_2d"
    )
    cache = engine.get_block_cache()
    blocks = list(
        _ordered_cached_output_blocks("resize", grid, source_crc, cache_params)
    )
    result = np.empty(output_shape, dtype=np.float32)
    tracker = _BlockExecutionTracker("resize", "batch_offset", len(blocks))
    tracker.input_bytes = int(source_f32.nbytes)

    # Resolve cache entries first.  Only cold blocks need a batch buffer, so
    # cache-heavy repeated frames do not allocate or upload an offset table.
    cold = []
    for block in blocks:
        tile_shape = (*block.shape, source.shape[2]) if is_vector else block.shape
        cached = _get_cached_output_tile(
            "resize", block, source_crc, cache_params, tile_shape
        )
        if cached is not None:
            tracker.cache_hits += 1
            result[block.write_slice] = cached
        else:
            tracker.cache_misses += 1
            cold.append(block)

    if cold:
        tile_h = max(int(block.shape[0]) for block in cold)
        tile_w = max(int(block.shape[1]) for block in cold)
        # Grouping by exact shape avoids padding edge blocks.  Most frames
        # have one dominant group and at most two thin edge groups.
        groups = {}
        for block in cold:
            groups.setdefault(tuple(block.shape), []).append(block)
        sample_tile_shape = (
            (tile_h, tile_w, source.shape[2]) if is_vector else (tile_h, tile_w)
        )
        sample_tile_bytes = (
            int(np.prod(sample_tile_shape)) * np.dtype(np.float32).itemsize
        )
        batch_size = engine.recommend_block_batch_size(sample_tile_bytes * 2, cap=4)
        for shape, shape_blocks in groups.items():
            tile_h, tile_w = (int(shape[0]), int(shape[1]))
            for start in range(0, len(shape_blocks), batch_size):
                chunk = shape_blocks[start : start + batch_size]
                offsets_np = np.asarray(
                    [[block.y0, block.x0] for block in chunk], dtype=np.int32
                )
                offset_buf = None
                batch_buf = None
                try:
                    offset_buf = upload(offsets_np)
                    batch_shape = (
                        (len(chunk), tile_h, tile_w, source.shape[2])
                        if is_vector
                        else (len(chunk), tile_h, tile_w)
                    )
                    batch_buf = engine.allocate(
                        batch_shape,
                        dtype=np.float32,
                        is_vector=is_vector,
                        vector_dim=3,
                    )
                    dispatch_started = time.perf_counter()
                    batch_mod.run(
                        batch_graph,
                        src=src_view,
                        dst=batch_buf,
                        offsets=offset_buf,
                        h_src=int(source.shape[0]),
                        w_src=int(source.shape[1]),
                        h_dst=int(target_h),
                        w_dst=int(target_w),
                    )
                    tracker.dispatch_seconds += time.perf_counter() - dispatch_started
                    tracker.dispatches += 1
                    sync_started = time.perf_counter()
                    engine.sync()
                    tracker.sync_seconds += time.perf_counter() - sync_started
                    tracker.syncs += 1
                    tracker.batches += 1
                    readback_started = time.perf_counter()
                    batch_np = np.ascontiguousarray(batch_buf.to_numpy())
                    tracker.readback_seconds += time.perf_counter() - readback_started
                    tracker.output_bytes += int(batch_np.nbytes)
                    for index, block in enumerate(chunk):
                        tile_result = np.ascontiguousarray(batch_np[index])
                        if (
                            tuple(tile_result.shape[:2]) != tuple(block.shape)
                            or not np.isfinite(tile_result).all()
                        ):
                            raise RuntimeError(
                                "bilinear batch graph returned an invalid tile"
                            )
                        result[block.write_slice] = tile_result
                        _put_cached_output_tile(
                            "resize", block, source_crc, cache_params, tile_result
                        )
                finally:
                    if offset_buf is not None:
                        offset_buf.destroy()
                    if batch_buf is not None:
                        batch_buf.destroy()

    tracker.finish()
    return result


@_block_recovery("resize")
def resize(src, dsize, interpolation=INTER_CUBIC, return_gpu=False, dst=None):
    """Taichi AOT Resize (OpenCV Parity API)"""
    target_w, target_h = dsize
    if isinstance(src, TaichiGPUBuffer) and np.dtype(src.dtype) != np.dtype(np.float32):
        import cv2

        source = src.to_numpy()
        cv_interp = {
            INTER_NEAREST: cv2.INTER_NEAREST,
            INTER_LINEAR: cv2.INTER_LINEAR,
            INTER_CUBIC: cv2.INTER_CUBIC,
            INTER_AREA: cv2.INTER_AREA,
        }.get(interpolation)
        if cv_interp is None:
            raise NotImplementedError(
                f"Interpolation mode {interpolation} is not supported"
            )
        result = cv2.resize(
            source, (int(target_w), int(target_h)), interpolation=cv_interp
        )
        if dst is not None:
            uploaded = upload(result)
            try:
                copy_field(uploaded, dst)
            finally:
                uploaded.destroy()
            return dst
        return upload(np.ascontiguousarray(result)) if return_gpu else result
    if (
        isinstance(src, np.ndarray)
        and dst is None
        and interpolation in (INTER_LINEAR, INTER_CUBIC, INTER_AREA)
    ):
        source = np.ascontiguousarray(src)
        output_nbytes = (
            target_h
            * target_w
            * (source.shape[2] if source.ndim == 3 else 1)
            * np.dtype(np.float32).itemsize
        )
        grid = engine.plan_blocks(
            "resize", (target_h, target_w), source.nbytes + output_nbytes
        )
        if grid is not None:
            source_f32 = np.ascontiguousarray(source, dtype=np.float32)
            src_buf = upload(source_f32)
            output_shape = (
                (target_h, target_w, source.shape[2])
                if source.ndim == 3
                else (target_h, target_w)
            )
            result = np.empty(output_shape, dtype=np.float32)
            if interpolation == INTER_AREA:
                module = "area"
                graph = (
                    "inter_area_offset_vec3_f32"
                    if source.ndim == 3
                    else "inter_area_offset_f32"
                )
            else:
                module = "bicubic" if interpolation == INTER_CUBIC else "bilinear"
                prefix = "bicubic" if interpolation == INTER_CUBIC else "bilinear"
                graph = (
                    f"{prefix}_resize_offset_f32_{'3d' if source.ndim == 3 else '2d'}"
                )
            src_view = src_buf.view_as_vector(True, 3) if source.ndim == 3 else src_buf
            source_crc = checksum(source_f32)
            cache_params = {
                "dsize": dsize,
                "interpolation": interpolation,
                "dtype": source.dtype.str,
            }
            if interpolation == INTER_LINEAR:
                try:
                    batched_result = _resize_bilinear_batch_offset(
                        source,
                        source_f32,
                        src_view,
                        grid,
                        target_h,
                        target_w,
                        output_shape,
                        source_crc,
                        cache_params,
                    )
                except Exception:
                    src_buf.destroy()
                    raise
                if batched_result is not None:
                    src_buf.destroy()
                    result = batched_result
                    if source.dtype != np.float32:
                        if np.issubdtype(source.dtype, np.integer):
                            result = np.clip(
                                result,
                                np.iinfo(source.dtype).min,
                                np.iinfo(source.dtype).max,
                            )
                        result = result.astype(source.dtype)
                    return upload(result) if return_gpu else result
            arena = _BlockTileArena(engine)
            pending = []
            # Keep the batch deliberately small.  The governor reduces this
            # to one under pressure, while healthy systems can overlap a few
            # dispatches without turning the block path into a full-frame
            # resident allocation.
            grid_tile_shape = (grid.block_height, grid.block_width)
            sample_tile_shape = (
                (*grid_tile_shape, source.shape[2])
                if source.ndim == 3
                else grid_tile_shape
            )
            sample_tile_bytes = (
                int(np.prod(sample_tile_shape)) * np.dtype(np.float32).itemsize
            )
            batch_size = engine.recommend_block_batch_size(sample_tile_bytes, cap=4)
            tracker = _BlockExecutionTracker("resize", "offset", len(grid))
            tracker.input_bytes = int(source_f32.nbytes)
            try:
                for block in _ordered_cached_output_blocks(
                    "resize", grid, source_crc, cache_params
                ):
                    tile_shape = (
                        (*block.shape, source.shape[2])
                        if source.ndim == 3
                        else block.shape
                    )
                    cached = _get_cached_output_tile(
                        "resize", block, source_crc, cache_params, tile_shape
                    )
                    if cached is not None:
                        tracker.cache_hits += 1
                        result[block.write_slice] = cached
                        continue
                    tracker.cache_misses += 1
                    tile_buf = arena.acquire(
                        tile_shape,
                        dtype=np.float32,
                        is_vector=source.ndim == 3,
                        vector_dim=3,
                    )
                    tile_view = (
                        tile_buf.view_as_vector(True, 3)
                        if source.ndim == 3
                        else tile_buf
                    )
                    dispatch_started = time.perf_counter()
                    if interpolation == INTER_AREA:
                        _mod(module).run(
                            graph,
                            src=src_view,
                            dst=tile_view,
                            sh=source.shape[0],
                            sw=source.shape[1],
                            dh=target_h,
                            dw=target_w,
                            offset_y=block.y0,
                            offset_x=block.x0,
                        )
                    else:
                        _mod(module).run(
                            graph,
                            src=src_view,
                            dst=tile_view,
                            h_src=source.shape[0],
                            w_src=source.shape[1],
                            h_dst=target_h,
                            w_dst=target_w,
                            offset_y=block.y0,
                            offset_x=block.x0,
                        )
                    tracker.dispatch_seconds += time.perf_counter() - dispatch_started
                    tracker.dispatches += 1
                    pending.append((block, tile_buf))
                    if len(pending) >= batch_size:
                        _flush_resize_batch(
                            pending,
                            result,
                            source_crc,
                            cache_params,
                            arena,
                            tracker=tracker,
                        )
                _flush_resize_batch(
                    pending,
                    result,
                    source_crc,
                    cache_params,
                    arena,
                    tracker=tracker,
                )
                tracker.finish()
            except Exception as exc:
                tracker.finish(status="failed", error=exc)
                raise
            finally:
                # A failed batch may still own slots; synchronize before
                # returning them to the engine's retired-buffer pool.
                if pending:
                    try:
                        sync_started = time.perf_counter()
                        engine.sync()
                        tracker.sync_seconds += time.perf_counter() - sync_started
                        tracker.syncs += 1
                    except Exception:
                        pass
                arena.close()
                src_buf.destroy()
            if source.dtype != np.float32:
                if np.issubdtype(source.dtype, np.integer):
                    result = np.clip(
                        result, np.iinfo(source.dtype).min, np.iinfo(source.dtype).max
                    )
                result = result.astype(source.dtype)
            return upload(result) if return_gpu else result

    # Maintained resize graphs are float32. Normalize the non-tiled path too;
    # small images bypass block planning and otherwise reach an f32 graph with
    # their original uint8/int32 dtype.
    if isinstance(src, np.ndarray) and src.dtype != np.float32:
        src_buf = InputArray(np.ascontiguousarray(src, dtype=np.float32))
    else:
        src_buf = InputArray(src)
    owned_f32_src = False
    if np.dtype(src_buf.dtype) != np.dtype(np.float32):
        src_buf = engine.upload(
            np.ascontiguousarray(src_buf.to_numpy(), dtype=np.float32)
        )
        owned_f32_src = True

    if isinstance(src, TaichiGPUBuffer) and len(src_buf.shape) == 3:
        # Force vector for any 3D arrays (RGB or Flow)
        src_buf = src_buf.view_as_vector(True)

    h_src, w_src = src_buf.shape[0], src_buf.shape[1]
    is_vec = getattr(src_buf, "is_vector", False)
    is_3d = (len(src_buf.shape) == 3) or is_vec

    # If it's a vector field but shape is 2D (like placeholders), we need to ensure dst_shape has the vector dim
    v_dim = (
        src_buf.vector_dim
        if is_vec
        else (src_buf.shape[2] if len(src_buf.shape) == 3 else 1)
    )

    if dst is None:
        if is_3d:
            dst_shape = (target_h, target_w, v_dim)
        else:
            dst_shape = (target_h, target_w)

        dst_buf = OutputArray(
            dst_shape, dtype=src_buf.dtype, is_vector=is_vec, vector_dim=v_dim
        )
    else:
        dst_buf = dst

    is_vec = getattr(src_buf, "is_vector", False)

    if interpolation == INTER_CUBIC:
        graph_name = "bicubic_resize_f32_3d" if is_vec else "bicubic_resize_f32_2d"
        if src_buf.dtype != np.float32:
            graph_name = graph_name.replace("f32", "i32")
        _mod("bicubic").run(
            graph_name,
            src=src_buf,
            dst=dst_buf,
            h_src=h_src,
            w_src=w_src,
            h_dst=target_h,
            w_dst=target_w,
        )
    elif interpolation == INTER_LINEAR:
        graph_name = "bilinear_resize_f32_3d" if is_vec else "bilinear_resize_f32_2d"
        try:
            _mod("bilinear").run(
                graph_name,
                src=src_buf,
                dst=dst_buf,
                h_src=h_src,
                w_src=w_src,
                h_dst=target_h,
                w_dst=target_w,
            )
        except RuntimeError as exc:
            # Intel Vulkan may quarantine bilinear when its staging mapping is
            # not host-visible. Resize is an infrastructure operation: keep
            # the RGB spatial pipeline alive with a CPU fallback.
            message = str(exc).lower()
            if "quarantined" not in message and "map memory" not in message:
                raise
            import cv2

            if dst is None:
                dst_buf.destroy()
            source_np = np.ascontiguousarray(src_buf.to_numpy())
            result_np = cv2.resize(
                source_np,
                (int(target_w), int(target_h)),
                interpolation=cv2.INTER_LINEAR,
            )
            uploaded = upload(np.ascontiguousarray(result_np, dtype=np.float32))
            try:
                if dst is not None:
                    copy_field(uploaded, dst)
                    return dst
                if return_gpu:
                    return uploaded
                return uploaded.to_numpy()
            finally:
                if dst is not None or not return_gpu:
                    uploaded.destroy()
    elif interpolation == INTER_AREA:
        graph_name = "inter_area_vec3_f32" if is_vec else "inter_area_f32"
        _mod("area").run(
            graph_name,
            src=src_buf,
            dst=dst_buf,
            sh=h_src,
            sw=w_src,
            dh=target_h,
            dw=target_w,
        )
    elif interpolation == INTER_NEAREST:
        if is_vec:
            raise NotImplementedError(
                "AOT nearest-neighbor currently has a scalar graph only"
            )
        _mod("nearest").run(
            "nearest_resize_f32",
            src=src_buf,
            dst=dst_buf,
            h_src=h_src,
            w_src=w_src,
            h_dst=target_h,
            w_dst=target_w,
        )
    else:
        raise NotImplementedError(
            f"Interpolation mode {interpolation} is not supported in AOT currently."
        )

    return dst_buf if return_gpu else dst_buf.to_numpy()


# ---------------------------------------------------------------------------
# Point interpolation adapters
# ---------------------------------------------------------------------------
#
# ``bicubic_interpolation.py`` has always contained the point-sampling kernels
# and ``compile_bicubic_tcm.py`` archives them as ``bicubic_sample_*`` graphs.
# The old public facade did not expose a wrapper for those graphs, however,
# and consequently AOT mode used a fail-closed placeholder.  Keep the
# implementation here next to the other AOT leaves so both scalar and vector
# samples use the target-qualified artifact; no second interpolation kernel is
# introduced.


def _sample_coords(x, y):
    """Return broadcasted ``(x, y)`` coordinates as contiguous f32 pairs."""

    x_arr, y_arr = np.broadcast_arrays(
        np.asarray(x, dtype=np.float32), np.asarray(y, dtype=np.float32)
    )
    if not np.isfinite(x_arr).all() or not np.isfinite(y_arr).all():
        raise ValueError("sample coordinates must be finite")
    return (
        np.ascontiguousarray(
            np.column_stack((x_arr.reshape(-1), y_arr.reshape(-1))), dtype=np.float32
        ),
        x_arr.shape,
    )


def _sample_point_aot(src, x, y, *, mode="bicubic", channel=None):
    """Dispatch the existing bicubic graph (or remap graph for bilinear).

    The legacy API is scalar, but accepting broadcastable coordinate arrays is
    harmless and useful for sparse-to-dense alignment callers.  AOT supports
    grayscale and the existing three-component vector ABI.  A requested
    channel is extracted through the common AOT graph before sampling, so no
    host/JIT implementation is silently substituted.
    """

    if not isinstance(src, (np.ndarray, TaichiGPUBuffer)):
        src = np.asarray(src)
    shape = tuple(getattr(src, "shape", ()))
    if len(shape) not in (2, 3):
        raise ValueError("sample source must have shape (H, W) or (H, W, C)")
    if len(shape) == 3 and int(shape[2]) != 3:
        raise ValueError("AOT point sampling supports only three-channel images")
    if channel is not None:
        channel = int(channel)
        if len(shape) != 3 or channel < 0 or channel >= 3:
            raise ValueError("channel must be 0, 1, or 2 for an HxWx3 source")
        # ``extract_channel`` is itself an AOT graph and returns a scalar
        # buffer for GPU input or a host array for host input.
        src = extract_channel(src, channel)
        shape = tuple(src.shape)

    coords, out_shape = _sample_coords(x, y)
    n_samples = int(coords.shape[0])

    if mode == "bilinear":
        # The remap graph is the canonical bilinear sampler.  A one-row map
        # keeps the result compact while preserving the graph's x/y contract.
        map_x = np.ascontiguousarray(coords[:, 0].reshape(1, n_samples))
        map_y = np.ascontiguousarray(coords[:, 1].reshape(1, n_samples))
        result = remap(src, map_x, map_y, return_gpu=False)
        result = np.asarray(result)
        if result.ndim == 3:
            result = result.reshape(n_samples, 3)
        else:
            result = result.reshape(n_samples)
    else:
        source_is_vector = len(shape) == 3
        source_owner = src
        owned_source = False
        if isinstance(src, np.ndarray):
            source_owner = InputArray(np.ascontiguousarray(src, dtype=np.float32))
            owned_source = True
        elif np.dtype(src.dtype) != np.dtype(np.float32):
            source_owner = src.cast(np.float32)
            owned_source = source_owner is not src

        source_arg = source_owner
        if source_is_vector and not getattr(source_owner, "is_vector", False):
            source_arg = source_owner.view_as_vector(True, 3)
        coords_buf = InputArray(coords)
        # Keep the physical RGB shape in the owner allocation.  A vector
        # view with shape ``(n_samples,)`` would read back only the first
        # component through the bridge; the graph receives the view while
        # callers retain the ordinary ``(n_samples, 3)`` ndarray contract.
        result_owner = OutputArray(
            (n_samples, 3) if source_is_vector else (n_samples,),
            dtype=np.float32,
            is_vector=False,
        )
        result_buf = (
            result_owner.view_as_vector(True, 3) if source_is_vector else result_owner
        )
        try:
            graph = (
                "bicubic_sample_f32_3d" if source_is_vector else "bicubic_sample_f32_2d"
            )
            _mod("bicubic").run(
                graph,
                src=source_arg,
                coords=coords_buf,
                results=result_buf,
                n_samples=n_samples,
                h_src=int(shape[0]),
                w_src=int(shape[1]),
            )
            result = result_owner.to_numpy()
        finally:
            result_owner.destroy()
            coords_buf.destroy()
            if owned_source:
                source_owner.destroy()

    # Point-wise callers historically receive a scalar/one-dimensional
    # channel vector.  Preserve that convention for scalar x/y while keeping
    # the natural broadcast shape for array coordinates.
    if out_shape == ():
        if np.asarray(result).ndim == 2:
            return np.asarray(result[0], dtype=np.float32)
        return np.asarray(result).reshape(-1)[0].item()
    result_array = np.asarray(result)
    if result_array.ndim == 2:
        return result_array.reshape((*out_shape, 3)).astype(np.float32, copy=False)
    return result_array.reshape(out_shape).astype(np.float32, copy=False)


def sample_at_bicubic(img, x, y, channel=None):
    """Sample an image at fractional coordinates using the bicubic AOT graph."""

    return _sample_point_aot(img, x, y, mode="bicubic", channel=channel)


def sample_at(img, x, y, channel=None):
    """Backward-compatible alias for :func:`sample_at_bicubic`."""

    return sample_at_bicubic(img, x, y, channel=channel)


def sample_at_bilinear(img, x, y, channel=None):
    """Sample an image at fractional coordinates using the remap AOT graph."""

    return _sample_point_aot(img, x, y, mode="bilinear", channel=channel)


def _box_filter_tile(tile, kernel_size):
    src_tile = upload(tile)
    try:
        output = box_filter(src_tile, kernel_size=kernel_size, return_gpu=True)
        try:
            return output.to_numpy()
        finally:
            output.destroy()
    finally:
        src_tile.destroy()


def box_filter(src, kernel_size=3, return_gpu=False, dst=None):
    """AOT Implementation of Box Filter."""
    if kernel_size < 1 or kernel_size % 2 == 0:
        raise ValueError("kernel_size must be a positive odd integer")

    # The rebuilt artifact is stable for scalar and small RGB fp32 frames.
    # Intel OpenGL still rejects large RGB SSBO bindings; retain the validated
    # reference path unless the caller explicitly opts into that experiment.
    source_shape = getattr(src, "shape", ())
    source_dtype = src.dtype if hasattr(src, "dtype") else np.asarray(src).dtype
    native_box_requested = (
        os.environ.get("PIXEL_REFINE_AOT_NATIVE_BOX_FILTER", "1") == "1"
    )
    if (
        np.dtype(source_dtype) != np.dtype(np.float32)
        or (engine.arch.lower() in ("opengl", "gles") and not native_box_requested)
        or (
            engine.arch.lower() in ("opengl", "gles")
            and len(source_shape) == 3
            and os.environ.get("PIXEL_REFINE_AOT_UNSAFE_LARGE_BOX") != "1"
        )
    ):
        import cv2

        source = (
            src.to_numpy()
            if isinstance(src, TaichiGPUBuffer)
            else np.ascontiguousarray(src)
        )
        result = cv2.boxFilter(
            source,
            ddepth=-1,
            ksize=(kernel_size, kernel_size),
            normalize=True,
            borderType=cv2.BORDER_REPLICATE,
        ).astype(source.dtype, copy=False)
        if dst is not None:
            uploaded = upload(result)
            try:
                copy_field(uploaded, dst)
            finally:
                uploaded.destroy()
            return dst
        return upload(result) if return_gpu else result

    if not isinstance(src, TaichiGPUBuffer):
        if dst is not None:
            raise ValueError(
                "blockwise box filter does not support a destination buffer"
            )
        array = np.ascontiguousarray(src)
        result = _run_blockwise(
            "box_filter",
            (array,),
            array.shape,
            array.dtype,
            lambda tile: _box_filter_tile(tile, kernel_size),
            halo=kernel_size // 2,
            params={"kernel_size": kernel_size},
        )
        if result is not None:
            return upload(result) if return_gpu else result

        src_buffer = upload(array)
        output = box_filter(src_buffer, kernel_size=kernel_size, return_gpu=True)
        if return_gpu:
            src_buffer.destroy()
            return output
        try:
            return output.to_numpy()
        finally:
            src_buffer.destroy()
            output.destroy()

    src_buf = InputArray(src)
    h, w = src_buf.shape[:2]
    radius = kernel_size // 2
    is_3d = len(src_buf.shape) == 3

    if dst is None:
        dst_buf = OutputArray(src_buf.shape, dtype=src_buf.dtype, is_vector=is_3d)
    else:
        dst_buf = dst

    is_vec = getattr(src_buf, "is_vector", False)

    if kernel_size == 3:
        target = "box_filter_fused_3x3_1ch_f32"
        if is_3d:
            target = (
                "box_filter_fused_3x3_vec3_f32"
                if is_vec
                else "box_filter_fused_3x3_3ch_f32"
            )
        _mod("box_filter").run(target, src=src_buf, dst=dst_buf, h=h, w=w)
    else:
        tmp_buf = engine.allocate(src_buf.shape, dtype=src_buf.dtype, is_vector=is_vec)
        target = "box_filter_separable_generic_1ch_f32"
        if is_3d:
            target = (
                "box_filter_separable_generic_vec3_f32"
                if is_vec
                else "box_filter_separable_generic_3ch_f32"
            )
        _mod("box_filter").run(
            target, src=src_buf, tmp=tmp_buf, dst=dst_buf, h=h, w=w, radius=radius
        )
        del tmp_buf

    return dst_buf if return_gpu else dst_buf.to_numpy()


def _gaussian_blur_tile(tile, sigma, kernel_size):
    src_tile = upload(tile)
    try:
        output = gaussian_blur(
            src_tile,
            sigma=sigma,
            kernel_size=kernel_size,
            return_gpu=True,
        )
        try:
            return output.to_numpy()
        finally:
            output.destroy()
    finally:
        src_tile.destroy()


def gaussian_blur(src, sigma=1.0, kernel_size=None, return_gpu=False, dst=None):
    """AOT Implementation of Gaussian Blur.

    Supports:
      - 2D single-channel (H, W)              -> uses gaussian_blur_x/y_1ch_f32
      - 3D scalar (H, W, 3)                   -> uses gaussian_blur_x/y_3ch_f32
      - 3D vector field (H, W) is_vector=True -> uses gaussian_blur_x/y_vec3_f32

    Args:
        src:         Input buffer (TaichiGPUBuffer or np.ndarray).
        sigma:       Gaussian standard deviation.
        kernel_size: Kernel size (must be odd). Auto-computed from sigma if None.
        return_gpu:  If True, returns TaichiGPUBuffer; otherwise returns np.ndarray.
        dst:         Optional pre-allocated TaichiGPUBuffer to reuse (same shape as src).
                     When provided, output is written directly into this buffer
                     and the same buffer is returned, saving a VRAM allocation.
    """
    if kernel_size is None or kernel_size <= 0:
        kernel_size = int(np.ceil(3 * sigma)) * 2 + 1
    radius = kernel_size // 2

    if not isinstance(src, TaichiGPUBuffer):
        if dst is not None:
            raise ValueError(
                "blockwise Gaussian blur does not support a destination buffer"
            )
        array = np.ascontiguousarray(src)
        result = _run_blockwise(
            "gaussian_blur",
            (array,),
            array.shape,
            array.dtype,
            lambda tile: _gaussian_blur_tile(tile, sigma, kernel_size),
            halo=radius,
            params={"sigma": float(sigma), "kernel_size": kernel_size},
        )
        if result is not None:
            return upload(result) if return_gpu else result

        # Gaussian AOT graphs are float32. Normalize integer inputs before
        # entering the non-blockwise recursive path.
        src_buffer = upload(
            np.ascontiguousarray(array, dtype=np.float32)
            if array.dtype != np.float32
            else array
        )
        output = gaussian_blur(
            src_buffer,
            sigma=sigma,
            kernel_size=kernel_size,
            return_gpu=True,
        )
        if return_gpu:
            src_buffer.destroy()
            return output
        try:
            return output.to_numpy()
        finally:
            src_buffer.destroy()
            output.destroy()

    src_buf = src
    owned_f32_src = False
    if np.dtype(src_buf.dtype) != np.dtype(np.float32):
        src_buf = engine.upload(
            np.ascontiguousarray(src_buf.to_numpy(), dtype=np.float32)
        )
        owned_f32_src = True
    h, w = src_buf.shape[:2]
    is_vec = getattr(src_buf, "is_vector", False)
    is_2d = (len(src_buf.shape) == 2) and not is_vec

    from taichi_vision.taichi_algorithm.smoothing.gaussian import (
        compute_gaussian_weights,
    )

    weights_np = compute_gaussian_weights(sigma, radius).astype(np.float32)
    weights_buf = InputArray(weights_np)

    # Intermediate buffer (always freshly allocated — must be separate from src)
    tmp_buf = OutputArray(src_buf.shape, dtype=src_buf.dtype, is_vector=is_vec)

    # Output: reuse caller-supplied dst if shape and dtype match, otherwise allocate
    if dst is not None and dst.shape == src_buf.shape and dst.dtype == src_buf.dtype:
        dst_buf = dst
    else:
        dst_buf = OutputArray(src_buf.shape, dtype=src_buf.dtype, is_vector=is_vec)

    if is_2d:
        # Single-channel 2D path
        target_x = "gaussian_blur_x_1ch_f32"
        target_y = "gaussian_blur_y_1ch_f32"
    elif is_vec:
        target_x = "gaussian_blur_x_vec3_f32"
        target_y = "gaussian_blur_y_vec3_f32"
    else:
        target_x = "gaussian_blur_x_3ch_f32"
        target_y = "gaussian_blur_y_3ch_f32"

    _mod("gaussian").run(
        target_x, src=src_buf, dst=tmp_buf, h=h, w=w, weights=weights_buf, radius=radius
    )
    _mod("gaussian").run(
        target_y, src=tmp_buf, dst=dst_buf, h=h, w=w, weights=weights_buf, radius=radius
    )

    engine.sync()
    tmp_buf.release()
    if hasattr(weights_buf, "release"):
        weights_buf.release()
    elif hasattr(weights_buf, "destroy"):
        weights_buf.destroy()
    if owned_f32_src:
        src_buf.destroy()
    output = dst_buf if return_gpu else dst_buf.to_numpy()
    return output


@_block_recovery("image_pyramid")
def image_pyramid(src, levels=4, return_gpu=False):
    """AOT Implementation of Image Pyramid (Downsampling)"""
    if isinstance(src, np.ndarray):
        current = np.ascontiguousarray(src, dtype=np.float32)
        first_grid = engine.plan_blocks("image_pyramid", current.shape, current.nbytes)
        if first_grid is not None:
            for _ in range(levels):
                next_h, next_w = current.shape[0] // 2, current.shape[1] // 2
                if next_h < 1 or next_w < 1:
                    break
                grid = BlockGrid(
                    (next_h, next_w),
                    size=engine.get_block_config().normalized_size(),
                )
                output_shape = (
                    (next_h, next_w, current.shape[2])
                    if current.ndim == 3
                    else (next_h, next_w)
                )
                next_level = np.empty(output_shape, dtype=np.float32)
                src_buf = upload(current)
                src_view = (
                    src_buf.view_as_vector(False) if current.ndim == 3 else src_buf
                )
                graph = (
                    "downsample_2x_offset_3ch_f32"
                    if current.ndim == 3
                    else "downsample_2x_offset_f32"
                )
                source_crc = checksum(current)
                cache_params = {"shape": output_shape, "graph": graph}
                try:
                    for block in _ordered_cached_output_blocks(
                        "image_pyramid", grid, source_crc, cache_params
                    ):
                        tile_shape = (
                            (*block.shape, current.shape[2])
                            if current.ndim == 3
                            else block.shape
                        )
                        cached = _get_cached_output_tile(
                            "image_pyramid", block, source_crc, cache_params, tile_shape
                        )
                        if cached is not None:
                            next_level[block.write_slice] = cached
                            continue
                        tile_buf = engine.allocate(tile_shape, dtype=np.float32)
                        try:
                            _mod("pyramid").run(
                                graph,
                                src=src_view,
                                dst=tile_buf,
                                offset_y=block.y0,
                                offset_x=block.x0,
                            )
                            tile_result = tile_buf.to_numpy()
                            next_level[block.write_slice] = tile_result
                            _put_cached_output_tile(
                                "image_pyramid",
                                block,
                                source_crc,
                                cache_params,
                                tile_result,
                            )
                        finally:
                            tile_buf.destroy()
                finally:
                    src_buf.destroy()
                current = next_level
            return upload(current) if return_gpu else current

    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    is_3d = len(src_buf.shape) == 3

    curr_buf = src_buf
    graph = "downsample_2x_3ch_f32" if is_3d else "downsample_2x_f32"

    for _ in range(levels):
        h, w = curr_buf.shape[0], curr_buf.shape[1]
        next_h, next_w = h // 2, w // 2
        if next_h < 1 or next_w < 1:
            break

        dst_shape = (next_h, next_w, src_buf.shape[2]) if is_3d else (next_h, next_w)
        dst_buf = engine.allocate(dst_shape, dtype=src_buf.dtype)
        curr_view = (
            curr_buf.view_as_vector(False)
            if is_3d and getattr(curr_buf, "is_vector", False)
            else curr_buf
        )
        _mod("pyramid").run(graph, src=curr_view, dst=dst_buf)

        if curr_buf is not src_buf:
            del curr_buf

        curr_buf = dst_buf

    return curr_buf if return_gpu else curr_buf.to_numpy()


def _median_filter_tile(tile):
    src_tile = upload(tile)
    try:
        output = median_filter(src_tile, return_gpu=True)
        try:
            return output.to_numpy()
        finally:
            output.destroy()
    finally:
        src_tile.destroy()


def median_filter(src, return_gpu=False, **kwargs):
    """AOT Median Filter 3x3."""
    # The deployed OpenGL artifact currently exposes a validated scalar graph;
    # RGB/flow remain on the reference path until the vector artifact is rebuilt.
    median_shape = getattr(src, "shape", ())
    median_dtype = src.dtype if hasattr(src, "dtype") else np.asarray(src).dtype
    native_median_requested = (
        os.environ.get("PIXEL_REFINE_AOT_NATIVE_MEDIAN", "1") == "1"
    )
    native_median_supported = len(median_shape) == 2 and not getattr(
        src, "is_vector", False
    )
    if (
        engine.arch.lower() in ("opengl", "gles")
        and len(median_shape) == 3
        and median_shape[2] == 3
        and not getattr(src, "is_vector", False)
    ):
        # RGB graph is enabled only after an isolated child-process probe.  A
        # crashing Intel driver therefore cannot take down the application.
        from taichi_vision.taichi_aot.capabilities import opengl_native_probe

        native_median_supported = opengl_native_probe("median")
    if np.dtype(median_dtype) != np.dtype(np.float32) or (
        engine.arch.lower() in ("opengl", "gles")
        and (not native_median_requested or not native_median_supported)
    ):
        import cv2

        source = (
            src.to_numpy()
            if isinstance(src, TaichiGPUBuffer)
            else np.ascontiguousarray(src)
        )
        result = cv2.medianBlur(source, 3)
        if return_gpu:
            return upload(np.ascontiguousarray(result))
        return result

    if not isinstance(src, TaichiGPUBuffer):
        array = np.ascontiguousarray(src)
        result = _run_blockwise(
            "median_filter",
            (array,),
            array.shape,
            array.dtype,
            _median_filter_tile,
            halo=1,
            params={"kernel_size": 3},
        )
        if result is not None:
            return upload(result) if return_gpu else result

        src_buffer = upload(array)
        output = median_filter(src_buffer, return_gpu=True, **kwargs)
        if return_gpu:
            src_buffer.destroy()
            return output
        try:
            return output.to_numpy()
        finally:
            src_buffer.destroy()
            output.destroy()

    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]

    is_flow = len(src_buf.shape) == 3 and src_buf.shape[2] == 2
    is_3ch = len(src_buf.shape) == 3 and src_buf.shape[2] == 3

    # Use vector for flow, but scalar 3D for RGB to avoid field_dim warnings in Taichi AOT
    src_v = src_buf.view_as_vector(True) if is_flow else src_buf.view_as_vector(False)

    dst_buf = engine.allocate(src_buf.shape, dtype=src_buf.dtype, is_vector=is_flow)
    dst_v = dst_buf.view_as_vector(True) if is_flow else dst_buf.view_as_vector(False)

    if is_flow:
        graph = "median_flow_3x3_f32"
    elif is_3ch:
        graph = "median_3ch_3x3_f32"
    else:
        graph = "median_3x3_f32" if src_buf.dtype == np.float32 else "median_3x3"

    _mod("median_filter").run(graph, src=src_v, dst=dst_v, h=h, w=w)
    return dst_buf if return_gpu else dst_buf.to_numpy()


def fft2(src, use_hanning=False):
    """AOT Implementation of 2D FFT."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h_src, w_src = src_buf.shape[:2]

    # FFT requires power-of-two dimensions
    h = 1 << (h_src - 1).bit_length()
    w = 1 << (w_src - 1).bit_length()

    complex_buf = engine.allocate((h, w, 2), is_vector=True)
    _mod("fft").run(
        "fft_real_to_complex_f32", src=src_buf, dst=complex_buf, h=h_src, w=w_src
    )

    if use_hanning:
        # Hanning window works on real part (complex_buf.x)
        # We need a temp real buffer to apply it before R2C or after R2C
        # Actually our fft_hanning_window_f32 takes a real ndarray.
        # Let's apply it to src_buf if it's already on GPU, or a copy.
        src_padded = engine.allocate((h, w), dtype=np.float32)
        # Copy src to padded and apply window
        # For simplicity, we can use a kernel that does both,
        # but let's just use existing graphs.
        _mod("common").run(
            "copy_f32_2d", src=src_buf, dst=src_padded
        )  # This might fail if shapes differ
        # Wait, copy_f32_2d needs same shape.
        # Better: use fft_real_to_complex first, then apply window to the complex x-channel.
        # But our hanning graph takes f32 ndarray.
        # Let's just create a quick hanning window on the src_buf if we can.

    # Actually, let's just apply Hanning to the complex_buf.x after R2C
    if use_hanning:
        _mod("fft").run("fft_complex_hanning_f32", data=complex_buf, h=h_src, w=w_src)

    def run_fft_1d(buf, h, w, is_inverse, is_col):
        n = h if is_col else w
        bits = (n - 1).bit_length()
        temp_buf = engine.allocate((h, w, 2), is_vector=True)
        _mod("fft").run(
            "fft_bit_reverse_f32",
            src=buf,
            dst=temp_buf,
            bits=bits,
            is_col=1 if is_col else 0,
        )
        buf.handle, temp_buf.handle = temp_buf.handle, buf.handle
        for stage in range(1, bits + 1):
            _mod("fft").run(
                "fft_stage_f32",
                data=buf,
                n=n,
                stage_len=1 << stage,
                is_inverse=1 if is_inverse else 0,
                is_col=1 if is_col else 0,
            )
        if is_inverse:
            _mod("fft").run("fft_normalize_f32", data=buf, scale=1.0 / n)
        del temp_buf

    run_fft_1d(complex_buf, h, w, False, False)
    run_fft_1d(complex_buf, h, w, False, True)
    return complex_buf


def ifft2(complex_buf, target_shape=None):
    """AOT Implementation of 2D IFFT."""
    h, w = complex_buf.shape[:2]

    def run_fft_1d(buf, h, w, is_inverse, is_col):
        n = h if is_col else w
        bits = (n - 1).bit_length()
        temp_buf = engine.allocate((h, w, 2), is_vector=True)
        _mod("fft").run(
            "fft_bit_reverse_f32",
            src=buf,
            dst=temp_buf,
            bits=bits,
            is_col=1 if is_col else 0,
        )
        buf.handle, temp_buf.handle = temp_buf.handle, buf.handle
        for stage in range(1, bits + 1):
            _mod("fft").run(
                "fft_stage_f32",
                data=buf,
                n=n,
                stage_len=1 << stage,
                is_inverse=1 if is_inverse else 0,
                is_col=1 if is_col else 0,
            )
        if is_inverse:
            _mod("fft").run("fft_normalize_f32", data=buf, scale=1.0 / n)
        del temp_buf

    run_fft_1d(complex_buf, h, w, True, True)
    run_fft_1d(complex_buf, h, w, True, False)

    out_h, out_w = target_shape if target_shape else (h, w)
    dst_buf = engine.allocate((out_h, out_w))
    _mod("fft").run(
        "fft_complex_to_real_f32", src=complex_buf, dst=dst_buf, h=out_h, w=out_w
    )
    return dst_buf


def _sobel_tile(tile):
    src_tile = upload(tile)
    try:
        dx, dy = sobel(src_tile, return_gpu=True)
        try:
            return dx.to_numpy(), dy.to_numpy()
        finally:
            dx.destroy()
            dy.destroy()
    finally:
        src_tile.destroy()


def sobel(src, return_gpu=False):
    """AOT Sobel."""
    if not isinstance(src, TaichiGPUBuffer):
        array = np.ascontiguousarray(src, dtype=np.float32)
        result = _run_blockwise_pair("sobel", array, _sobel_tile, halo=1)
        if result is not None:
            return (upload(result[0]), upload(result[1])) if return_gpu else result

        src_buffer = upload(array)
        outputs = sobel(src_buffer, return_gpu=True)
        if return_gpu:
            src_buffer.destroy()
            return outputs
        try:
            return outputs[0].to_numpy(), outputs[1].to_numpy()
        finally:
            src_buffer.destroy()
            outputs[0].destroy()
            outputs[1].destroy()

    if np.dtype(src.dtype) != np.dtype(np.float32):
        import cv2

        source = src.to_numpy()
        dx = cv2.Sobel(source, cv2.CV_32F, 1, 0, ksize=3)
        dy = cv2.Sobel(source, cv2.CV_32F, 0, 1, ksize=3)
        return (upload(dx), upload(dy)) if return_gpu else (dx, dy)

    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3

    src_v = src_buf if not is_3d else src_buf.view_as_vector(True)

    dx = engine.allocate((h, w))
    dy = engine.allocate((h, w))

    # Use 3ch graph if 3d
    graph = "sobel_vec3_f32" if is_3d else "sobel_f32"

    _mod("gradients").run(graph, src=src_v, dst_dx=dx, dst_dy=dy, h=h, w=w)
    return (dx, dy) if return_gpu else (dx.to_numpy(), dy.to_numpy())


def _laplacian_tile(tile):
    src_tile = upload(tile)
    try:
        output = laplacian(src_tile, return_gpu=True)
        try:
            return output.to_numpy()
        finally:
            output.destroy()
    finally:
        src_tile.destroy()


def laplacian(src, return_gpu=False):
    """AOT Laplacian."""
    if not isinstance(src, TaichiGPUBuffer):
        array = np.ascontiguousarray(src)
        result = _run_blockwise(
            "laplacian",
            (array,),
            array.shape,
            np.float32,
            _laplacian_tile,
            halo=1,
        )
        if result is not None:
            return upload(result) if return_gpu else result

        src_buffer = upload(array)
        output = laplacian(src_buffer, return_gpu=True)
        if return_gpu:
            src_buffer.destroy()
            return output
        try:
            return output.to_numpy()
        finally:
            src_buffer.destroy()
            output.destroy()

    if np.dtype(src.dtype) != np.dtype(np.float32):
        import cv2

        source = src.to_numpy()
        result = cv2.Laplacian(source, cv2.CV_32F, ksize=3)
        return upload(result) if return_gpu else result

    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]
    dst = engine.allocate((h, w))
    _mod("gradients").run("laplacian_f32", src=src_buf, dst=dst, h=h, w=w)
    return dst if return_gpu else dst.to_numpy()


def ransac_flow_cleanup(flow, threshold=1.0, return_gpu=False):
    """AOT RANSAC Flow Cleanup."""
    return ransac_flow_cleanup_aot(flow, threshold=threshold, return_gpu=return_gpu)


def ransac_flow_cleanup_aot(flow, threshold=1.0, return_gpu=False):
    """Internal AOT RANSAC implementation."""
    if (
        engine.arch.lower() in ("opengl", "gles")
        and os.environ.get("PIXEL_REFINE_AOT_NATIVE_RANSAC", "1") != "1"
    ):
        source = (
            flow.to_numpy()
            if isinstance(flow, TaichiGPUBuffer)
            else np.ascontiguousarray(flow)
        )
        result = np.array(source, copy=True)
        model = np.median(result.reshape(-1, 2), axis=0)
        distance = np.linalg.norm(result - model, axis=2)
        result[distance > float(threshold)] = model
        return upload(result) if return_gpu else result

    is_gpu = isinstance(flow, TaichiGPUBuffer)
    # The LLVM20 RANSAC graph uses the canonical scalar rank-3 ABI
    # ``(H, W, 2)``.  A vector2 rank-2 buffer has the same bytes but a
    # different graph shape contract, which Taichi rejects at dispatch time.
    # Normalize host input without an extra NumPy round-trip; an already
    # imported vector buffer is materialized only for this legacy ABI boundary
    # until a native vector-to-scalar external-memory view is available.
    from taichi_vision.taichi_algorithm.aot_wrapper import _InputArray

    flow_owned = False
    if is_gpu and getattr(flow, "is_vector", False):
        flow_buf = _InputArray(flow.to_numpy(), force_vector=False)
        flow_owned = True
    elif is_gpu:
        flow_buf = flow
    else:
        flow_buf = _InputArray(np.ascontiguousarray(flow, dtype=np.float32), force_vector=False)
        flow_owned = True
    h, w = flow_buf.shape[:2]

    dst = engine.allocate(
        flow_buf.shape,
        dtype=np.float32,
        is_vector=False,
        vector_dim=1,
        host_accessible=not return_gpu,
    )
    mask = engine.allocate((h, w), dtype=np.int32)
    model = engine.allocate((2,), dtype=np.float32)  # [mean_u, mean_v]

    _mod("ransac").run(
        "ransac_flow_cleanup_f32",
        flow=flow_buf,
        inlier_mask=mask,
        model=model,
        output=dst,
        h=h,
        w=w,
        threshold=float(threshold),
        stride_refine=1,  # Full-frame reduction for deterministic parity
        stride_final=1,
    )  # Full resolution

    # OpenGL dispatch is asynchronous.  Do not let reduction buffers be
    # recycled immediately after the graph call: the driver may still be
    # binding them while the final output is produced.  Keeping these
    # dependencies owned by the output fixes the GL_INVALID_OPERATION seen
    # during native RANSAC without changing the public API.
    if return_gpu:
        result = dst.view_as_vector(True, 2)
        result._ransac_dependencies = (mask, model, flow_buf if flow_owned else None)
        return result
    engine.sync()
    result = dst.to_numpy()
    dst.destroy()
    mask.destroy()
    model.destroy()
    if flow_owned:
        flow_buf.destroy()
    return result


def ncc_alignment(image, template, stride=1, return_gpu=False):
    """
    Taichi AOT ZNCC Alignment.
    Returns: (dx, dy, confidence)
    """
    res_map = zncc(
        image, template, stride=stride, return_gpu=False
    )  # Always need peak-finding on CPU for now

    idx = np.unravel_index(np.argmax(res_map), res_map.shape)
    dy, dx = idx[0] * stride, idx[1] * stride
    conf = float(res_map[idx])

    return float(dx), float(dy), conf


def zncc(image, template, stride=1, return_gpu=False):
    """AOT Optimized Spatial ZNCC."""
    is_gpu_img = isinstance(image, TaichiGPUBuffer)
    is_gpu_temp = isinstance(template, TaichiGPUBuffer)
    img_buf = image if is_gpu_img else engine.upload(image)
    temp_buf = template if is_gpu_temp else engine.upload(template)

    h_img, w_img = img_buf.shape[:2]
    h_temp, w_temp = temp_buf.shape[:2]

    s_h = engine.allocate((h_img, w_img))
    sq_h = engine.allocate((h_img, w_img))
    s_2d = engine.allocate((h_img, w_img))
    sq_2d = engine.allocate((h_img, w_img))

    _mod("ncc").run(
        "integral_row_scan", src=img_buf, sum_h=s_h, sq_sum_h=sq_h, h=h_img, w=w_img
    )
    _mod("ncc").run(
        "integral_col_scan",
        sum_h=s_h,
        sq_sum_h=sq_h,
        sum_2d=s_2d,
        sq_sum_2d=sq_2d,
        h=h_img,
        w=w_img,
    )

    del s_h, sq_h

    temp_np = temp_buf.to_numpy() if is_gpu_temp else template
    sum_t = float(np.sum(temp_np))
    n = float(h_temp * w_temp)
    var_t_n = float(max(0.0, np.sum(temp_np**2) - (sum_t**2 / n)))

    res_h, res_w = (h_img - h_temp) // stride + 1, (w_img - w_temp) // stride + 1
    dst = engine.allocate((res_h, res_w))

    _mod("ncc").run(
        "zncc_spatial",
        src=img_buf,
        template=temp_buf,
        sum_2d=s_2d,
        sq_sum_2d=sq_2d,
        dst=dst,
        sum_t=sum_t,
        var_t_n=var_t_n,
        n_float=n,
        stride=stride,
    )

    res = dst if return_gpu else dst.to_numpy()
    del s_2d, sq_2d, dst
    return res


# -------------------------------------------------------------------------
# SIGMA PRESETS (shared with JBF python-side)
# -------------------------------------------------------------------------
_JBF_SIGMA_PRESETS = {
    "high": (0.8, 0.05),
    "medium": (1.5, 0.10),
    "low": (2.5, 0.20),
}


def _jbf_sigma(preset):
    ss, sr = _JBF_SIGMA_PRESETS.get(preset, _JBF_SIGMA_PRESETS["medium"])
    return 1.0 / (2.0 * ss * ss), 1.0 / (2.0 * sr * sr)


def _prepare_guide_aot(guide_raw):
    """Ensure guide is a 2D f32 GPU buffer, normalized [0,1]."""
    is_gpu = isinstance(guide_raw, TaichiGPUBuffer)
    if is_gpu:
        g = guide_raw
        if len(g.shape) == 3:
            # Auto-convert 3ch → gray using common AOT
            g = cvtColor(g, 6)  # BGR2GRAY
        return g, False
    else:
        import numpy as _np

        arr = _np.array(guide_raw, dtype=_np.float32)
        if arr.ndim == 3:
            arr = 0.299 * arr[:, :, 2] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 0]
        if arr.max() > 1.0:
            arr = arr / (255.0 if arr.max() <= 255.0 else 65535.0)
        return engine.upload(arr.astype(_np.float32)), True


def _prepare_guide_array(guide_raw):
    """Match the AOT guide normalization path without allocating a full GPU buffer."""
    guide = np.asarray(guide_raw, dtype=np.float32)
    if guide.ndim == 3:
        guide = 0.299 * guide[:, :, 2] + 0.587 * guide[:, :, 1] + 0.114 * guide[:, :, 0]
    if guide.ndim != 2:
        raise ValueError("joint bilateral guide must be a 2D or 3-channel image")
    peak = float(np.max(guide)) if guide.size else 0.0
    if peak > 1.0:
        guide = guide / (255.0 if peak <= 255.0 else 65535.0)
    return np.ascontiguousarray(guide)


def _joint_bilateral_tile(tile, guide_tile, preset, radius):
    src_tile = upload(tile)
    guide_buffer = upload(guide_tile)
    try:
        output = joint_bilateral_filter(
            src_tile, guide_buffer, preset=preset, radius=radius, return_gpu=True
        )
        try:
            return output.to_numpy()
        finally:
            output.destroy()
    finally:
        src_tile.destroy()
        guide_buffer.destroy()


def joint_bilateral_filter(src, guide, preset="medium", radius=2, return_gpu=False):
    """
    AOT Joint Bilateral Filter — General post-processor.

    Args:
        src    : (H,W), (H,W,3) vec, or (H,W,2) vec — grayscale/RGB/flow GPU buffer
        guide  : (H,W) or (H,W,3) — guidance image (auto-converted to gray)
        preset : "low" | "medium" | "high"
        radius : 1=3x3 | 2=5x5 (default) | 3=7x7

    Example:
        # Post-process median result with original image as guide
        clean = taichi_aot.joint_bilateral_filter(median_out, original_img, preset="medium")

        # Refine flow field
        smooth_flow = taichi_aot.joint_bilateral_filter(flow_gpu, ref_gray, preset="low")
    """
    if not isinstance(src, TaichiGPUBuffer) and not isinstance(guide, TaichiGPUBuffer):
        source = np.ascontiguousarray(src, dtype=np.float32)
        guide_array = _prepare_guide_array(guide)
        if source.shape[:2] != guide_array.shape:
            raise ValueError(
                "joint bilateral source and guide must have matching dimensions"
            )
        effective_radius = radius if radius in (1, 2, 3) else 2
        result = _run_blockwise(
            "joint_bilateral_filter",
            (source, guide_array),
            source.shape,
            np.float32,
            lambda tile, guide_tile: _joint_bilateral_tile(
                tile, guide_tile, preset, effective_radius
            ),
            halo=effective_radius,
            params={"preset": preset, "radius": effective_radius},
        )
        if result is not None:
            return upload(result) if return_gpu else result

        src_buffer = upload(source)
        guide_buffer = upload(guide_array)
        output = joint_bilateral_filter(
            src_buffer,
            guide_buffer,
            preset=preset,
            radius=effective_radius,
            return_gpu=True,
        )
        if return_gpu:
            src_buffer.destroy()
            guide_buffer.destroy()
            return output
        try:
            return output.to_numpy()
        finally:
            src_buffer.destroy()
            guide_buffer.destroy()
            output.destroy()

    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    guide_buf, guide_is_temp = _prepare_guide_aot(guide)

    h, w = src_buf.shape[:2]
    inv_2ss2, inv_2sr2 = _jbf_sigma(preset)
    r = radius if radius in (1, 2, 3) else 2

    # Determine src type
    is_vec = getattr(src_buf, "is_vector", False)
    ndim = len(src_buf.shape)

    if ndim == 2 and not is_vec:
        # 1ch scalar
        dst = engine.allocate((h, w))
        _mod("jbf").run(
            f"jbf_1ch_r{r}",
            src=src_buf,
            guide=guide_buf,
            dst=dst,
            h=h,
            w=w,
            inv_2ss2=inv_2ss2,
            inv_2sr2=inv_2sr2,
        )
    elif (
        ndim == 3
        and src_buf.shape[2] == 2
        or (is_vec and src_buf.shape[-1] == 2 if hasattr(src_buf, "shape") else False)
    ):
        # flow 2ch
        src_v = src_buf if is_vec else src_buf.view_as_vector(True)
        dst = engine.allocate(src_buf.shape, is_vector=True)
        dst_v = dst.view_as_vector(True)
        _mod("jbf").run(
            f"jbf_flow_r{r}",
            src=src_v,
            guide=guide_buf,
            dst=dst_v,
            h=h,
            w=w,
            inv_2ss2=inv_2ss2,
            inv_2sr2=inv_2sr2,
        )
    else:
        # 3ch
        src_v = src_buf if is_vec else src_buf.view_as_vector(True)
        dst = engine.allocate(src_buf.shape, is_vector=True)
        dst_v = dst.view_as_vector(True)
        _mod("jbf").run(
            f"jbf_3ch_r{r}",
            src=src_v,
            guide=guide_buf,
            dst=dst_v,
            h=h,
            w=w,
            inv_2ss2=inv_2ss2,
            inv_2sr2=inv_2sr2,
        )

    if guide_is_temp:
        del guide_buf
    return dst if return_gpu else dst.to_numpy()


def joint_bilateral_upsample(src_low, guide_hi, preset="medium", return_gpu=False):
    jblu_src_shape = getattr(src_low, "shape", ())
    jblu_guide_shape = getattr(guide_hi, "shape", ())
    jblu_src_dtype = (
        src_low.dtype if hasattr(src_low, "dtype") else np.asarray(src_low).dtype
    )
    jblu_guide_dtype = (
        guide_hi.dtype if hasattr(guide_hi, "dtype") else np.asarray(guide_hi).dtype
    )
    native_jblu_requested = os.environ.get("PIXEL_REFINE_AOT_NATIVE_JBLU", "1") == "1"
    native_jblu_supported = (
        len(jblu_src_shape) == 2
        and len(jblu_guide_shape) == 2
        and int(jblu_guide_shape[0]) * int(jblu_guide_shape[1]) <= 256 * 256
    )
    if (
        np.dtype(jblu_src_dtype) != np.dtype(np.float32)
        or np.dtype(jblu_guide_dtype) != np.dtype(np.float32)
        or (
            engine.arch.lower() in ("opengl", "gles")
            and (not native_jblu_requested or not native_jblu_supported)
        )
    ):
        import cv2

        low = (
            src_low.to_numpy()
            if isinstance(src_low, TaichiGPUBuffer)
            else np.asarray(src_low)
        )
        guide = (
            guide_hi.to_numpy()
            if isinstance(guide_hi, TaichiGPUBuffer)
            else np.asarray(guide_hi)
        )
        result = cv2.resize(
            np.ascontiguousarray(low, dtype=np.float32),
            (guide.shape[1], guide.shape[0]),
            interpolation=cv2.INTER_LINEAR,
        )
        return upload(np.ascontiguousarray(result)) if return_gpu else result

    """
    AOT Joint Bilateral Upsampling (JBLU).
    Upscales src_low to resolution of guide_hi with edge-aware interpolation.

    Args:
        src_low  : (h,w), (h,w,3) vec, or (h,w,2) vec — LOW-RES source
        guide_hi : (H,W) or (H,W,3) — HIGH-RES guide (auto-converted to gray)
        preset   : "low" | "medium" | "high"

    Example:
        # Upsample pyramid flow with full-res image as guide
        flow_full = taichi_aot.joint_bilateral_upsample(flow_low, full_res_img)

        # Upsample low-res mask
        mask_full = taichi_aot.joint_bilateral_upsample(mask_low, full_res_gray)
    """
    is_gpu = isinstance(src_low, TaichiGPUBuffer)
    src_buf = src_low if is_gpu else engine.upload(src_low)
    guide_buf, guide_is_temp = _prepare_guide_aot(guide_hi)

    h_low, w_low = src_buf.shape[:2]
    H, W = guide_buf.shape[:2]
    scale_y = float(H) / float(h_low)
    scale_x = float(W) / float(w_low)
    inv_2ss2, inv_2sr2 = _jbf_sigma(preset)

    is_vec = getattr(src_buf, "is_vector", False)
    ndim = len(src_buf.shape)

    if ndim == 2 and not is_vec:
        # 1ch
        dst = engine.allocate((H, W))
        _mod("jbf").run(
            "jblu_1ch_r2",
            src_low=src_buf,
            guide_hi=guide_buf,
            dst=dst,
            h_low=h_low,
            w_low=w_low,
            H=H,
            W=W,
            inv_2ss2=inv_2ss2,
            inv_2sr2=inv_2sr2,
        )
    elif (ndim == 3 and src_buf.shape[2] == 2) or (
        is_vec and ndim == 2 and len(src_buf.shape) == 2
    ):
        # flow 2ch — check by is_vector and shape
        src_v = src_buf if is_vec else src_buf.view_as_vector(True)
        dst = engine.allocate((H, W, 2), is_vector=True)
        dst_v = dst.view_as_vector(True)
        _mod("jbf").run(
            "jblu_flow_r2",
            src_low=src_v,
            guide_hi=guide_buf,
            dst=dst_v,
            h_low=h_low,
            w_low=w_low,
            H=H,
            W=W,
            inv_2ss2=inv_2ss2,
            inv_2sr2=inv_2sr2,
            scale_y=scale_y,
            scale_x=scale_x,
        )
    else:
        # 3ch
        src_v = src_buf if is_vec else src_buf.view_as_vector(True)
        dst = engine.allocate((H, W, 3), is_vector=True)
        dst_v = dst.view_as_vector(True)
        _mod("jbf").run(
            "jblu_3ch_r2",
            src_low=src_v,
            guide_hi=guide_buf,
            dst=dst_v,
            h_low=h_low,
            w_low=w_low,
            H=H,
            W=W,
            inv_2ss2=inv_2ss2,
            inv_2sr2=inv_2sr2,
        )

    if guide_is_temp:
        del guide_buf
    return dst if return_gpu else dst.to_numpy()


# --- Bilateral Grid ---

BILATERAL_GRID_PRESETS = {
    # Tier: (s_s, s_r, sigma_s, sigma_r)
    "light": (32, 32, 1.0, 1.0),
    "medium": (16, 16, 1.0, 1.0),
    "heavy": (8, 8, 2.0, 1.5),
}


def bilateral_grid_filter(src, preset="medium", return_gpu=False):
    """
    AOT Bilateral Grid Filter.
    Edge-preserving smoothing in O(1) time per pixel.
    """
    # The checked-in OpenGL grid artifact has been rebuilt with matching 4D
    # shape metadata and passed the isolated runtime smoke test. Keep an
    # explicit host escape hatch for older driver/artifact deployments.
    if (
        engine.arch.lower() in ("opengl", "gles")
        and os.environ.get("PIXEL_REFINE_AOT_NATIVE_BILATERAL_GRID", "1") != "1"
    ):
        import cv2

        source = (
            src.to_numpy()
            if isinstance(src, TaichiGPUBuffer)
            else np.ascontiguousarray(src)
        )
        _, _, sigma_s, sigma_r = BILATERAL_GRID_PRESETS.get(
            preset, BILATERAL_GRID_PRESETS["medium"]
        )
        result = cv2.bilateralFilter(
            source.astype(np.float32, copy=False),
            d=0,
            sigmaColor=float(sigma_r),
            sigmaSpace=float(sigma_s),
        )
        if return_gpu:
            return upload(np.ascontiguousarray(result))
        return result

    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]

    # Handle multichannel by looping
    is_3ch = len(src_buf.shape) == 3 and src_buf.shape[2] == 3

    s_s, s_r, sigma_s, sigma_r = BILATERAL_GRID_PRESETS.get(
        preset, BILATERAL_GRID_PRESETS["medium"]
    )
    gn, gm, gl = (h + s_s - 1) // s_s + 2, (w + s_s - 1) // s_s + 2, 256 // s_r + 2

    # Allocate grids (pooled) - 3D spatial field of 2D vectors
    # Keep the channel lane explicit in the ndarray shape.  Vector ndarray
    # metadata is not ABI-stable for CPU AOT modules on larger allocations.
    grid_a = engine.allocate((gn, gm, gl, 2))
    grid_b = engine.allocate((gn, gm, gl, 2))
    # The bilateral-grid TCM ABI declares these as vector2 rank-3 ndarrays,
    # while the storage owner is kept as an explicit HxWxLx2 rank-4 buffer.
    # Passing the owner directly makes the native graph reject the runtime
    # shape metadata before dispatch (notably on Vulkan).  Use a vector2 view
    # so the public storage layout and the compiled graph ABI agree.
    grid_a_v = grid_a.view_as_vector(True, 2)
    grid_b_v = grid_b.view_as_vector(True, 2)

    rs, rr = int(np.ceil(sigma_s * 3.0)), int(np.ceil(sigma_r * 3.0))

    if not is_3ch:
        dst = engine.allocate((h, w))
        # Clear, Splat, Blur X, Y, Z, Slice
        _mod("bilateral_grid").run("bg_clear", grid=grid_a_v, gn=gn, gm=gm, gl=gl)
        _mod("bilateral_grid").run(
            "bg_splat",
            src=src_buf,
            grid=grid_a_v,
            s_s=s_s,
            s_r=s_r,
            h=h,
            w=w,
            gn=gn,
            gm=gm,
            gl=gl,
        )
        _mod("bilateral_grid").run(
            "bg_blur_x",
            grid=grid_a_v,
            dst_grid=grid_b_v,
            radius=rs,
            sigma=sigma_s,
            gn=gn,
            gm=gm,
            gl=gl,
        )
        _mod("bilateral_grid").run(
            "bg_blur_y",
            grid=grid_b_v,
            dst_grid=grid_a_v,
            radius=rs,
            sigma=sigma_s,
            gn=gn,
            gm=gm,
            gl=gl,
        )
        _mod("bilateral_grid").run(
            "bg_blur_z",
            grid=grid_a_v,
            dst_grid=grid_b_v,
            radius=rr,
            sigma=sigma_r,
            gn=gn,
            gm=gm,
            gl=gl,
        )
        _mod("bilateral_grid").run(
            "bg_slice",
            src=src_buf,
            grid=grid_b_v,
            dst=dst,
            s_s=s_s,
            s_r=s_r,
            h=h,
            w=w,
            gn=gn,
            gm=gm,
            gl=gl,
        )
    else:
        # RGB loop
        dst = engine.allocate((h, w, 3), is_vector=True)
        dst_v = dst.view_as_vector(True)
        src_v = (
            src_buf
            if getattr(src_buf, "is_vector", False)
            else src_buf.view_as_vector(True)
        )

        temp_ch = engine.allocate((h, w))
        temp_out = engine.allocate((h, w))

        for c in range(3):
            # 1. Extract channel
            _mod("common").run("extract_channel_f32", src=src_v, dst=temp_ch, ch=c)

            # 2. Filter
            _mod("bilateral_grid").run("bg_clear", grid=grid_a_v, gn=gn, gm=gm, gl=gl)
            _mod("bilateral_grid").run(
                "bg_splat",
                src=temp_ch,
                grid=grid_a_v,
                s_s=s_s,
                s_r=s_r,
                h=h,
                w=w,
                gn=gn,
                gm=gm,
                gl=gl,
            )
            _mod("bilateral_grid").run(
                "bg_blur_x",
                grid=grid_a_v,
                dst_grid=grid_b_v,
                radius=rs,
                sigma=sigma_s,
                gn=gn,
                gm=gm,
                gl=gl,
            )
            _mod("bilateral_grid").run(
                "bg_blur_y",
                grid=grid_b_v,
                dst_grid=grid_a_v,
                radius=rs,
                sigma=sigma_s,
                gn=gn,
                gm=gm,
                gl=gl,
            )
            _mod("bilateral_grid").run(
                "bg_blur_z",
                grid=grid_a_v,
                dst_grid=grid_b_v,
                radius=rr,
                sigma=sigma_r,
                gn=gn,
                gm=gm,
                gl=gl,
            )
            _mod("bilateral_grid").run(
                "bg_slice",
                src=temp_ch,
                grid=grid_b_v,
                dst=temp_out,
                s_s=s_s,
                s_r=s_r,
                h=h,
                w=w,
                gn=gn,
                gm=gm,
                gl=gl,
            )
            # Promote the filtered scalar plane back into the persistent RGB
            # destination before the next channel iteration.  Without this
            # graph call the RGB branch returned an uninitialized destination
            # even though each bilateral-grid slice completed successfully.
            insert_channel(temp_out, dst_v, c)

        engine.sync()
        temp_ch.release()
        temp_out.release()
        del temp_ch, temp_out

    engine.sync()
    grid_a.release()
    grid_b.release()
    del grid_a, grid_b
    return dst if return_gpu else dst.to_numpy()


def phase_correlation(ref, comp, use_hanning=True):
    """
    Taichi AOT Phase Correlation for global shift estimation.
    Returns: (dx, dy, response)
    """
    native_phase_requested = (
        os.environ.get("PIXEL_REFINE_AOT_NATIVE_PHASE_CORR", "1") == "1"
    )
    # The OpenGL FFT graph is not reliable for tiny transforms and its
    # Hanning-window path is not yet numerically equivalent to OpenCV.  Keep
    # the explicit native switch safe by routing those cases to the reference
    # implementation instead of returning a plausible but incorrect shift.
    phase_shape = ref.shape if hasattr(ref, "shape") else np.asarray(ref).shape
    native_phase_safe = (
        native_phase_requested
        and not use_hanning
        and len(phase_shape) >= 2
        and min(int(phase_shape[0]), int(phase_shape[1])) >= 48
    )
    if engine.arch.lower() in ("opengl", "gles") and not native_phase_safe:
        import cv2

        ref_np = (
            ref.to_numpy()
            if isinstance(ref, TaichiGPUBuffer)
            else np.ascontiguousarray(ref)
        )
        comp_np = (
            comp.to_numpy()
            if isinstance(comp, TaichiGPUBuffer)
            else np.ascontiguousarray(comp)
        )
        hann = (
            cv2.createHanningWindow((ref_np.shape[1], ref_np.shape[0]), cv2.CV_32F)
            if use_hanning
            else None
        )
        shift, response = cv2.phaseCorrelate(
            ref_np.astype(np.float32, copy=False),
            comp_np.astype(np.float32, copy=False),
            hann,
        )
        return float(shift[0]), float(shift[1]), float(response)

    is_gpu = isinstance(ref, TaichiGPUBuffer)
    ref_buf = ref if is_gpu else engine.upload(ref)
    comp_buf = comp if is_gpu else engine.upload(comp)

    h, w = ref_buf.shape[:2]
    # 1. FFT
    f_complex = fft2(ref_buf, use_hanning=use_hanning)
    g_complex = fft2(comp_buf, use_hanning=use_hanning)

    th, tw = f_complex.shape[:2]
    r_complex = OutputArray((th, tw, 2), is_vector=True)

    # 2. Cross-power spectrum: G * conj(F)
    # Graph Arg: src (a), b, dst, conj_b
    _mod("fft").run(
        "fft_complex_mul_f32", src=g_complex, b=f_complex, dst=r_complex, conj_b=1
    )

    # 3. Phase Normalize: R = R / |R|
    _mod("fft").run("fft_phase_normalize_f32", data=r_complex)

    # 4. IFFT
    corr_buf = ifft2(r_complex, target_shape=(h, w))
    corr_np = corr_buf.to_numpy()

    # 5. Peak finding
    idx = np.unravel_index(np.argmax(corr_np), corr_np.shape)
    dy, dx = idx[0], idx[1]
    peak_val = corr_np[idx]

    # Shift wrapping
    if dy > h // 2:
        dy -= h
    if dx > w // 2:
        dx -= w

    # Some Intel OpenGL drivers produce an all-zero correlation surface for
    # sparse or highly structured inputs. Recover through the reference path
    # instead of returning a plausible-looking but incorrect shift.
    if (
        engine.arch.lower() in ("opengl", "gles")
        and native_phase_safe
        and (not np.isfinite(peak_val) or float(peak_val) <= 1e-6)
    ):
        ref_np = (
            ref.to_numpy()
            if isinstance(ref, TaichiGPUBuffer)
            else np.ascontiguousarray(ref)
        )
        comp_np = (
            comp.to_numpy()
            if isinstance(comp, TaichiGPUBuffer)
            else np.ascontiguousarray(comp)
        )
        import cv2

        shift, response = cv2.phaseCorrelate(
            ref_np.astype(np.float32, copy=False),
            comp_np.astype(np.float32, copy=False),
            None,
        )
        del f_complex, g_complex, r_complex, corr_buf
        return float(shift[0]), float(shift[1]), float(response)

    del f_complex, g_complex, r_complex, corr_buf
    return float(dx), float(dy), float(peak_val)


@_block_recovery("remap")
def remap(src, map_x, map_y, return_gpu=False):
    """Taichi AOT Remap (OpenCV Parity API)"""
    if (
        isinstance(src, np.ndarray)
        and isinstance(map_x, np.ndarray)
        and isinstance(map_y, np.ndarray)
    ):
        source = np.ascontiguousarray(src)
        map_x_array = np.ascontiguousarray(map_x, dtype=np.float32)
        map_y_array = np.ascontiguousarray(map_y, dtype=np.float32)
        if map_x_array.shape != map_y_array.shape or map_x_array.ndim != 2:
            raise ValueError("map_x and map_y must be matching 2D arrays")
        output_nbytes = (
            map_x_array.size
            * (source.shape[2] if source.ndim == 3 else 1)
            * np.dtype(np.float32).itemsize
        )
        grid = engine.plan_blocks(
            "remap",
            map_x_array.shape,
            source.nbytes + map_x_array.nbytes + map_y_array.nbytes + output_nbytes,
        )
        if grid is not None:
            # The source stays global on GPU; map and destination are tiled.
            # This preserves map coordinates exactly at tile boundaries.
            source_f32 = np.ascontiguousarray(source, dtype=np.float32)
            source_buffer = upload(source_f32)
            output_shape = (
                (*map_x_array.shape, source.shape[2])
                if source.ndim == 3
                else map_x_array.shape
            )
            result = np.empty(output_shape, dtype=np.float32)
            source_crc = checksum(source_f32)
            cache_params = {"shape": output_shape, "dtype": source.dtype.str}
            cache = engine.get_block_cache()
            scheduled = []
            for block in grid:
                map_x_tile = np.ascontiguousarray(map_x_array[block.write_slice])
                map_y_tile = np.ascontiguousarray(map_y_array[block.write_slice])
                block_source_crc = (
                    source_crc,
                    checksum(map_x_tile),
                    checksum(map_y_tile),
                )
                block_id = block.make_id(str(block_source_crc), "remap", cache_params)
                scheduled.append(
                    (
                        cache.peek(block_id) is None,
                        block.index,
                        block,
                        block_source_crc,
                        map_x_tile,
                        map_y_tile,
                    )
                )
            scheduled.sort(key=lambda item: (item[0], item[1]))
            try:
                for (
                    _cold,
                    _index,
                    block,
                    block_source_crc,
                    map_x_tile,
                    map_y_tile,
                ) in scheduled:
                    tile_shape = (
                        (*block.shape, source.shape[2])
                        if source.ndim == 3
                        else block.shape
                    )
                    cached = _get_cached_output_tile(
                        "remap", block, block_source_crc, cache_params, tile_shape
                    )
                    if cached is not None:
                        result[block.write_slice] = cached
                        continue
                    tile = remap(
                        source_buffer,
                        map_x_tile,
                        map_y_tile,
                    )
                    result[block.write_slice] = tile
                    _put_cached_output_tile(
                        "remap", block, block_source_crc, cache_params, tile
                    )
            finally:
                source_buffer.destroy()
            if src.dtype != np.float32:
                if np.issubdtype(src.dtype, np.integer):
                    result = np.clip(
                        result, np.iinfo(src.dtype).min, np.iinfo(src.dtype).max
                    )
                result = result.astype(src.dtype)
            return upload(result) if return_gpu else result

    orig_dtype = None
    if isinstance(src, np.ndarray) and src.dtype != np.float32:
        orig_dtype = src.dtype
        src_cast = src.astype(np.float32)
    elif hasattr(src, "dtype") and src.dtype != np.float32:
        orig_dtype = src.dtype
        src_cast = src.cast(np.float32)
    else:
        src_cast = src

    src_buf = InputArray(src_cast)
    mx_buf = InputArray(map_x)
    my_buf = InputArray(map_y)

    h_src, w_src = src_buf.shape[:2]
    h_dst, w_dst = mx_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3

    if is_3d:
        src_v = (
            src_buf
            if getattr(src_buf, "is_vector", False)
            else src_buf.view_as_vector(True)
        )
        v_dim = src_v.vector_dim
        dst_shape = (h_dst, w_dst, v_dim)
        is_vec = True
    else:
        src_v = src_buf
        v_dim = 1
        dst_shape = (h_dst, w_dst)
        is_vec = False

    dst_buf = OutputArray(
        dst_shape, dtype=src_buf.dtype, is_vector=is_vec, vector_dim=v_dim
    )

    graph_name = "remap_f32_3d" if is_vec else "remap_f32_2d"
    _mod("remap").run(
        graph_name,
        src=src_v,
        map_x=mx_buf,
        map_y=my_buf,
        dst=dst_buf,
        h_src=h_src,
        w_src=w_src,
        h_dst=h_dst,
        w_dst=w_dst,
    )

    if src_cast is not src and hasattr(src_cast, "release"):
        engine.sync()
        src_cast.release()
    elif src_cast is not src and hasattr(src_cast, "destroy"):
        engine.sync()
        src_cast.destroy()

    if not return_gpu:
        res = dst_buf.to_numpy()
    else:
        engine.sync()
        res = dst_buf

    if orig_dtype is not None:
        if return_gpu:
            res_cast = res.cast(orig_dtype)
            res.release()
            res = res_cast
        else:
            if np.issubdtype(orig_dtype, np.integer):
                res = np.clip(res, np.iinfo(orig_dtype).min, np.iinfo(orig_dtype).max)
            res = res.astype(orig_dtype)

    return res


@_vulkan_host_accessible
@_block_recovery("remap_with_flow")
def remap_with_flow(src, flow, full_h, full_w, return_gpu=False, dst=None):
    """
    Fused remap with flow: bilinear interpolate flow on-the-fly + warp src image.
    Eliminates need for map_x, map_y full-res buffers (~91.6 MB VRAM saved).
    """
    active_arch = str(getattr(engine, "arch", "")).lower()
    # A common mixed API call uses a host image with a small GPU flow grid.
    # Route it through the fused path as well; downloading the low-resolution
    # flow grid avoids the broken legacy layout path while keeping full-
    # resolution coordinate maps off-device.
    if (
        isinstance(src, np.ndarray)
        and isinstance(flow, TaichiGPUBuffer)
        and dst is None
    ):
        return remap_with_flow(
            src,
            np.ascontiguousarray(flow.to_numpy(), dtype=np.float32),
            full_h,
            full_w,
            return_gpu=return_gpu,
            dst=dst,
        )

    if isinstance(src, np.ndarray) and isinstance(flow, np.ndarray) and dst is None:
        source = np.ascontiguousarray(src)
        flow_array = np.ascontiguousarray(flow, dtype=np.float32)
        output_nbytes = (
            full_h
            * full_w
            * (source.shape[2] if source.ndim == 3 else 1)
            * np.dtype(np.float32).itemsize
        )
        grid = engine.plan_blocks(
            "remap_with_flow",
            (full_h, full_w),
            source.nbytes + flow_array.nbytes + output_nbytes,
        )
        # Prefer tiled AOT for safe float32 workloads. Large frames and
        # integer sources use the full-frame AOT graph below until their tiled
        # numerical parity is proven.
        use_tiled = (
            grid is not None
            and source.dtype == np.float32
            and full_h * full_w < 8_000_000
        )
        if use_tiled:
            source_f32 = np.ascontiguousarray(source, dtype=np.float32)
            src_buf = upload(source_f32)
            flow_buf = engine.allocate(
                flow_array.shape,
                dtype=np.float32,
                is_vector=False,
                host_accessible=True,
            )
            from taichi_vision.taichi_aot.engine import _LIB, _RUNTIME

            _LIB.write_to_gpu_buffer(
                _RUNTIME, flow_buf.handle, flow_array.ctypes.data, flow_buf.nbytes
            )
            output_shape = (
                (full_h, full_w, source.shape[2])
                if source.ndim == 3
                else (full_h, full_w)
            )
            result = np.empty(output_shape, dtype=np.float32)
            h_src, w_src = source.shape[:2]
            h_flow, w_flow = flow_array.shape[:2]
            graph = (
                "remap_with_flow_offset_f32_3d"
                if source.ndim == 3
                else "remap_with_flow_offset_f32_2d"
            )
            src_view = src_buf.view_as_vector(True, 3) if source.ndim == 3 else src_buf
            source_crc = (checksum(source_f32), checksum(flow_array))
            cache_params = {"shape": output_shape, "scale": (full_h, full_w)}
            arena = _BlockTileArena(engine)
            pending = []
            block_tile_size = (grid.block_height, grid.block_width)
            sample_tile_shape = (
                (*block_tile_size, source.shape[2])
                if source.ndim == 3
                else block_tile_size
            )
            sample_tile_bytes = (
                int(np.prod(sample_tile_shape)) * np.dtype(np.float32).itemsize
            )
            # One output slot plus one staging/driver slot per queued tile.
            # The governor may reduce this to one when shared VRAM is tight.
            batch_size = engine.recommend_block_batch_size(sample_tile_bytes * 2, cap=4)
            tracker = _BlockExecutionTracker("remap_with_flow", "offset", len(grid))
            tracker.input_bytes = int(source_f32.nbytes + flow_array.nbytes)
            try:
                for block in _ordered_cached_output_blocks(
                    "remap_with_flow", grid, source_crc, cache_params
                ):
                    tile_shape = (
                        (*block.shape, source.shape[2])
                        if source.ndim == 3
                        else block.shape
                    )
                    cached = _get_cached_output_tile(
                        "remap_with_flow", block, source_crc, cache_params, tile_shape
                    )
                    if cached is not None:
                        tracker.cache_hits += 1
                        result[block.write_slice] = cached
                        continue
                    tracker.cache_misses += 1
                    tile_buf = arena.acquire(
                        tile_shape,
                        dtype=np.float32,
                        is_vector=source.ndim == 3,
                        vector_dim=3,
                    )
                    tile_view = (
                        tile_buf.view_as_vector(True, 3)
                        if source.ndim == 3
                        else tile_buf
                    )
                    try:
                        dispatch_started = time.perf_counter()
                        _mod("remap").run(
                            graph,
                            src=src_view,
                            flow=flow_buf,
                            dst=tile_view,
                            h_src=h_src,
                            w_src=w_src,
                            h_dst=full_h,
                            w_dst=full_w,
                            h_flow=h_flow,
                            w_flow=w_flow,
                            scale_x=float(full_w) / w_flow,
                            scale_y=float(full_h) / h_flow,
                            offset_y=block.y0,
                            offset_x=block.x0,
                        )
                        tracker.dispatch_seconds += (
                            time.perf_counter() - dispatch_started
                        )
                        tracker.dispatches += 1
                        pending.append((block, tile_buf))
                        if len(pending) >= batch_size:
                            _flush_offset_batch(
                                "remap_with_flow",
                                pending,
                                result,
                                source_crc,
                                cache_params,
                                arena,
                                validate_output=lambda tile, block: (
                                    tuple(np.asarray(tile).shape[:2])
                                    == tuple(block.shape)
                                    and bool(np.isfinite(tile).all())
                                ),
                                tracker=tracker,
                            )
                    except Exception:
                        # The arena owns the slot; keep it alive until the
                        # queue is fenced in the outer finally block.
                        raise
                _flush_offset_batch(
                    "remap_with_flow",
                    pending,
                    result,
                    source_crc,
                    cache_params,
                    arena,
                    validate_output=lambda tile, block: (
                        tuple(np.asarray(tile).shape[:2]) == tuple(block.shape)
                        and bool(np.isfinite(tile).all())
                    ),
                    tracker=tracker,
                )
                tracker.finish()
            except Exception as exc:
                tracker.finish(status="failed", error=exc)
                raise
            finally:
                if pending:
                    try:
                        sync_started = time.perf_counter()
                        engine.sync()
                        tracker.sync_seconds += time.perf_counter() - sync_started
                        tracker.syncs += 1
                    except Exception:
                        pass
                    pending.clear()
                arena.close()
                src_buf.destroy()
                flow_buf.destroy()
            if source.dtype != np.float32:
                if np.issubdtype(source.dtype, np.integer):
                    result = np.clip(
                        result, np.iinfo(source.dtype).min, np.iinfo(source.dtype).max
                    )
                result = result.astype(source.dtype)
            return upload(result) if return_gpu else result

    # Cast src to float32 on CPU if it is not float32 (matches legacy remap behavior)
    orig_dtype = None
    if isinstance(src, np.ndarray) and src.dtype != np.float32:
        orig_dtype = src.dtype
        src_cpu = src.astype(np.float32)
    elif hasattr(src, "dtype") and src.dtype != np.float32:
        orig_dtype = src.dtype
        src_cpu = src.cast(np.float32)
    else:
        src_cpu = src
        if hasattr(src, "dtype"):
            orig_dtype = src.dtype
        else:
            orig_dtype = np.float32

    is_gpu_src = isinstance(src_cpu, TaichiGPUBuffer)
    is_gpu_flow = isinstance(flow, TaichiGPUBuffer)
    src_buf = src_cpu if is_gpu_src else engine.upload(src_cpu)
    if is_gpu_flow:
        flow_buf = flow
    else:
        # Bypass engine.upload auto-detect bug for (H, W, 2) flow array by using direct allocation
        flow_buf = engine.allocate(
            flow.shape, dtype=np.float32, is_vector=False, host_accessible=True
        )
        from taichi_vision.taichi_aot.engine import _LIB, _RUNTIME

        _LIB.write_to_gpu_buffer(
            _RUNTIME,
            flow_buf.handle,
            np.ascontiguousarray(flow, dtype=np.float32).ctypes.data,
            flow_buf.nbytes,
        )

    h_src, w_src = src_buf.shape[:2]
    h_flow, w_flow = flow_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3
    c_count = src_buf.shape[2] if is_3d else 1

    src_cast = src_buf
    target_dtype = np.float32
    graph_name = "remap_with_flow_f32_3d" if is_3d else "remap_with_flow_f32_2d"

    # Output buffer determination (allocate intermediate float32 buffer)
    if dst is None:
        dst_shape = (full_h, full_w, c_count) if is_3d else (full_h, full_w)
        dst_buf = engine.allocate(dst_shape, dtype=np.float32, is_vector=is_3d)
    else:
        if dst.dtype == np.float32:
            dst_buf = dst
        else:
            dst_buf = engine.allocate(dst.shape, dtype=np.float32, is_vector=is_3d)

    # Input view for 3d vector graphs
    src_v = src_cast
    dst_v = dst_buf
    if is_3d:
        src_v = (
            src_cast
            if getattr(src_cast, "is_vector", False)
            else src_cast.view_as_vector(True)
        )
        dst_v = (
            dst_buf
            if getattr(dst_buf, "is_vector", False)
            else dst_buf.view_as_vector(True)
        )
    flow_v = flow_buf
    if getattr(flow_v, "is_vector", False):
        flow_v = flow_v.view_as_vector(False)

    scale_x = float(full_w) / float(w_flow)
    scale_y = float(full_h) / float(h_flow)

    # Run AOT Graph (always float32 for interpolation precision)
    _mod("remap").run(
        graph_name,
        src=src_v,
        flow=flow_v,
        dst=dst_v,
        h_src=int(h_src),
        w_src=int(w_src),
        h_dst=int(full_h),
        w_dst=int(full_w),
        h_flow=int(h_flow),
        w_flow=int(w_flow),
        scale_x=float(scale_x),
        scale_y=float(scale_y),
    )

    # Sync
    engine.sync()

    # Clean up intermediate casts and uploads
    if src_cast is not src_buf:
        src_cast.release()
    if not is_gpu_src:
        src_buf.release()
    if not is_gpu_flow:
        flow_buf.release()

    # Cast back to original dtype or download with CPU fallback
    if return_gpu:
        if dst is not None and dst is not dst_buf:
            from taichi_vision.taichi_algorithm.common import copy_field

            copy_field(dst_buf, dst)
            dst_buf.release()
            return dst
        return dst_buf
    else:
        # Download f32 from GPU first, then cast on CPU to avoid Vulkan u16/i16 host-mapping restrictions or .cast failures
        res_f32 = dst_buf.to_numpy()
        dst_buf.release()

        if orig_dtype != np.float32:
            if np.issubdtype(orig_dtype, np.integer):
                res_np = np.clip(
                    res_f32, np.iinfo(orig_dtype).min, np.iinfo(orig_dtype).max
                ).astype(orig_dtype)
            else:
                res_np = res_f32.astype(orig_dtype)
        else:
            res_np = res_f32

        if dst is not None:
            dst[:] = res_np
            return dst
        return res_np


def remap_with_flow_tile(
    src,
    flow,
    full_h,
    full_w,
    offset_y,
    offset_x,
    tile_h,
    tile_w,
    dst=None,
):
    """Warp one output tile directly from GPU-resident source and flow.

    Unlike :func:`remap_with_flow`, this low-level helper never allocates a
    full-resolution destination and never synchronizes.  It is intended for a
    same-stream producer/consumer pair where the returned tile is immediately
    consumed by another AOT graph.  Source and flow ownership stays with the
    caller.
    """
    if not isinstance(src, TaichiGPUBuffer) or not isinstance(flow, TaichiGPUBuffer):
        raise TypeError("remap_with_flow_tile requires GPU source and flow buffers")
    if np.dtype(src.dtype) != np.dtype(np.float32) or np.dtype(flow.dtype) != np.dtype(np.float32):
        raise TypeError("remap_with_flow_tile requires float32 source and flow buffers")

    full_h, full_w = int(full_h), int(full_w)
    offset_y, offset_x = int(offset_y), int(offset_x)
    tile_h, tile_w = int(tile_h), int(tile_w)
    if full_h <= 0 or full_w <= 0 or tile_h <= 0 or tile_w <= 0:
        raise ValueError("full and tile dimensions must be positive")
    if offset_y < 0 or offset_x < 0 or offset_y >= full_h or offset_x >= full_w:
        raise ValueError("tile offset is outside the full output")
    if offset_y + tile_h > full_h or offset_x + tile_w > full_w:
        raise ValueError("tile extends beyond the full output")

    is_3d = len(src.shape) == 3
    if is_3d and int(src.shape[2]) != 3:
        raise ValueError("remap_with_flow_tile only supports RGB 3D source buffers")
    if not is_3d and len(src.shape) != 2:
        raise ValueError("source buffer must be 2D or RGB 3D")
    if len(flow.shape) != 3 or int(flow.shape[2]) != 2:
        raise ValueError("flow buffer must have shape (H, W, 2)")

    graph_name = (
        "remap_with_flow_offset_f32_3d"
        if is_3d
        else "remap_with_flow_offset_f32_2d"
    )
    if not aot_graph_available("remap", graph_name):
        raise RuntimeError(
            f"{graph_name} is unavailable in the active remap TCM; "
            "recompile the target-qualified remap artifact."
        )

    h_src, w_src = int(src.shape[0]), int(src.shape[1])
    h_flow, w_flow = int(flow.shape[0]), int(flow.shape[1])
    if dst is None:
        dst = engine.allocate(
            (tile_h, tile_w, 3) if is_3d else (tile_h, tile_w),
            dtype=np.float32,
            is_vector=is_3d,
            vector_dim=3,
        )
    elif tuple(int(v) for v in dst.shape[:2]) != (tile_h, tile_w):
        raise ValueError("destination tile shape does not match tile dimensions")

    src_v = src if getattr(src, "is_vector", False) else src.view_as_vector(True, 3)
    dst_v = dst if getattr(dst, "is_vector", False) else dst.view_as_vector(True, 3)
    flow_v = flow.view_as_vector(False) if getattr(flow, "is_vector", False) else flow
    _mod("remap").run(
        graph_name,
        src=src_v if is_3d else src,
        flow=flow_v,
        dst=dst_v if is_3d else dst,
        h_src=h_src,
        w_src=w_src,
        h_dst=full_h,
        w_dst=full_w,
        h_flow=h_flow,
        w_flow=w_flow,
        scale_x=float(full_w) / float(w_flow),
        scale_y=float(full_h) / float(h_flow),
        offset_y=offset_y,
        offset_x=offset_x,
    )
    return dst


def _smooth_flow_tile(tile, sigma, kernel_size):
    flow_tile = upload(tile)
    try:
        output = smooth_flow_gpu(flow_tile, sigma=sigma, kernel_size=kernel_size)
        try:
            return output.to_numpy()
        finally:
            output.destroy()
    finally:
        flow_tile.destroy()


def smooth_flow_gpu(flow, sigma=1.0, kernel_size=5, dst=None):
    """Gaussian blur a 2-channel flow field (H, W, 2) entirely on GPU.

    Uses the fused smooth_flow_x / smooth_flow_y graphs compiled into remap.tcm.
    Both channels are processed simultaneously in a single kernel launch per pass,
    making this significantly faster than calling gaussian_blur twice on separate channels.

    Args:
        flow:        TaichiGPUBuffer (H, W, 2) — the raw flow field.
        sigma:       Gaussian standard deviation.
        kernel_size: Filter kernel size (must be odd). Auto-computed from sigma if <= 0.
        dst:         Optional pre-allocated TaichiGPUBuffer (H, W, 2) to reuse as output.
                     If None or incompatible, a new buffer is allocated.

    Returns:
        TaichiGPUBuffer (H, W, 2) — smoothed flow. Caller must destroy when done.
    """
    from taichi_vision.taichi_algorithm.smoothing.gaussian import (
        compute_gaussian_weights,
    )

    if kernel_size is None or kernel_size <= 0:
        kernel_size = int(np.ceil(3 * sigma)) * 2 + 1
    radius = kernel_size // 2

    if not isinstance(flow, TaichiGPUBuffer):
        if dst is not None:
            raise ValueError(
                "blockwise flow smoothing does not support a destination buffer"
            )
        flow_array = np.ascontiguousarray(flow, dtype=np.float32)
        if flow_array.ndim != 3 or flow_array.shape[2] != 2:
            raise ValueError("flow must have shape (H, W, 2)")
        result = _run_blockwise(
            "smooth_flow",
            (flow_array,),
            flow_array.shape,
            np.float32,
            lambda tile: _smooth_flow_tile(tile, sigma, kernel_size),
            halo=radius,
            params={"sigma": float(sigma), "kernel_size": kernel_size},
        )
        if result is not None:
            return result

        flow_buffer = upload(flow_array)
        output = smooth_flow_gpu(flow_buffer, sigma=sigma, kernel_size=kernel_size)
        try:
            return output.to_numpy()
        finally:
            flow_buffer.destroy()
            output.destroy()

    weights_np = compute_gaussian_weights(sigma, radius).astype(np.float32)
    weights_buf = InputArray(weights_np)

    h, w = int(flow.shape[0]), int(flow.shape[1])

    # Intermediate buffer for x-pass output (always new — cannot alias src)
    tmp_buf = engine.allocate((h, w, 2), dtype=np.float32)

    # Output buffer: reuse if compatible
    if dst is not None and dst.shape == (h, w, 2) and dst.dtype == np.float32:
        out_buf = dst
    else:
        out_buf = engine.allocate((h, w, 2), dtype=np.float32)

    # smooth_flow graphs were compiled as plain ndim=3 arrays, not vec2 fields.
    flow_src = flow.view_as_vector(False) if getattr(flow, "is_vector", False) else flow

    def _dispatch_smooth_flow_passes():
        _mod("remap").run(
            "smooth_flow_x",
            src=flow_src,
            dst=tmp_buf,
            h=h,
            w=w,
            weights=weights_buf,
            radius=radius,
        )
        _mod("remap").run(
            "smooth_flow_y",
            src=tmp_buf,
            dst=out_buf,
            h=h,
            w=w,
            weights=weights_buf,
            radius=radius,
        )

    # Resolve the producer module before recording.  The bridge can associate
    # a cross-module graph sequence with an already-loaded native module;
    # loading lazily from inside the recorder is driver-dependent.
    _mod("remap")
    _run_auto_graph_sequence(
        ("smooth_flow_x", "smooth_flow_y"),
        (h, w, 2),
        _dispatch_smooth_flow_passes,
        operation="smooth_flow",
        source="smooth_flow_gpu",
        resident_multiplier=8,
        reads=("flow", "weights"),
        writes=("smoothed_flow",),
        metadata={
            "sequence_kind": "two_pass_local_stencil",
            # The remap wrapper owns both passes and validates their serial
            # resource lifetime; keep this explicit so the planner's generic
            # read/write hazard guard does not over-split this known chain.
            "hazard_policy": "ordered",
        },
        module_keys=("remap", "remap"),
        retain_buffers=(out_buf, flow, flow_src),
    )

    engine.sync()
    tmp_buf.release()
    if hasattr(weights_buf, "release"):
        weights_buf.release()
    elif hasattr(weights_buf, "destroy"):
        weights_buf.destroy()
    del weights_buf
    return out_buf


def build_flow_maps(
    flow_or_dx,
    flow_or_dy_or_h,
    full_h_or_w=None,
    full_w=None,
    scale_x=None,
    scale_y=None,
    map_x_buf=None,
    map_y_buf=None,
):
    """Build remap coordinate maps from a flow field — fully on GPU.

    Two calling conventions:
      1. 2-channel flow tensor:
         build_flow_maps(flow_2ch, full_h, full_w, ...)
         where flow_2ch is TaichiGPUBuffer (H_flow, W_flow, 2).

      2. Separate dx/dy tensors (legacy):
         build_flow_maps(dx, dy, full_h, full_w, ...)
         where dx and dy are TaichiGPUBuffer (H_flow, W_flow).

    Args:
        flow_or_dx:         2-channel flow buffer OR dx buffer.
        flow_or_dy_or_h:    full_h (int) if 2ch convention, OR dy buffer if separate.
        full_h_or_w:        full_w (int) if 2ch convention, OR full_h (int) if separate.
        full_w:             full_w (int) only when using separate dx/dy convention.
        scale_x:            Horizontal scale factor. Auto-computed if None.
        scale_y:            Vertical scale factor. Auto-computed if None.
        map_x_buf:          Optional pre-allocated output buffer (full_h, full_w) to reuse.
        map_y_buf:          Optional pre-allocated output buffer (full_h, full_w) to reuse.

    Returns:
        (map_x_buf, map_y_buf): TaichiGPUBuffer (full_h, full_w) each.
    """
    # Detect calling convention
    if isinstance(flow_or_dy_or_h, int):
        # Convention 1: build_flow_maps(flow_2ch, full_h, full_w, ...)
        flow_buf = InputArray(flow_or_dx)
        _full_h = int(flow_or_dy_or_h)
        _full_w = int(full_h_or_w)
        h_flow = int(flow_buf.shape[0])
        w_flow = int(flow_buf.shape[1])

        if scale_x is None:
            scale_x = float(_full_w) / float(w_flow)
        if scale_y is None:
            scale_y = float(_full_h) / float(h_flow)

        out_shape = (_full_h, _full_w)
        if (
            map_x_buf is None
            or map_x_buf.shape != out_shape
            or map_x_buf.dtype != np.float32
        ):
            map_x_buf = engine.allocate(out_shape, dtype=np.float32)
        if (
            map_y_buf is None
            or map_y_buf.shape != out_shape
            or map_y_buf.dtype != np.float32
        ):
            map_y_buf = engine.allocate(out_shape, dtype=np.float32)

        _mod("remap").run(
            "build_flow_maps_from_2ch",
            flow=flow_buf,
            map_x=map_x_buf,
            map_y=map_y_buf,
            h_flow=h_flow,
            w_flow=w_flow,
            h_dst=_full_h,
            w_dst=_full_w,
            scale_x=float(scale_x),
            scale_y=float(scale_y),
        )
    else:
        # Convention 2: build_flow_maps(dx, dy, full_h, full_w, ...)
        dx_buf = InputArray(flow_or_dx)
        dy_buf = InputArray(flow_or_dy_or_h)
        _full_h = int(full_h_or_w)
        _full_w = int(full_w)
        h_flow = int(dx_buf.shape[0])
        w_flow = int(dx_buf.shape[1])

        if scale_x is None:
            scale_x = float(_full_w) / float(w_flow)
        if scale_y is None:
            scale_y = float(_full_h) / float(h_flow)

        out_shape = (_full_h, _full_w)
        if (
            map_x_buf is None
            or map_x_buf.shape != out_shape
            or map_x_buf.dtype != np.float32
        ):
            map_x_buf = engine.allocate(out_shape, dtype=np.float32)
        if (
            map_y_buf is None
            or map_y_buf.shape != out_shape
            or map_y_buf.dtype != np.float32
        ):
            map_y_buf = engine.allocate(out_shape, dtype=np.float32)

        _mod("remap").run(
            "build_flow_maps",
            dx=dx_buf,
            dy=dy_buf,
            map_x=map_x_buf,
            map_y=map_y_buf,
            h_flow=h_flow,
            w_flow=w_flow,
            h_dst=_full_h,
            w_dst=_full_w,
            scale_x=float(scale_x),
            scale_y=float(scale_y),
        )

    return map_x_buf, map_y_buf


def _enhance_grayscale_tile(
    src_tile, blur_tile, lut, micro_contrast, clarity, noise_coring
):
    src_buf, blur_buf, lut_buf = upload(src_tile), upload(blur_tile), upload(lut)
    dst_buf = engine.allocate(src_tile.shape, dtype=np.float32)
    try:
        h, w = src_tile.shape
        _mod("remap").run(
            "enhance_grayscale",
            src=src_buf,
            blur=blur_buf,
            lut=lut_buf,
            dst=dst_buf,
            micro_contrast=float(micro_contrast),
            clarity=float(clarity),
            noise_coring=float(noise_coring),
            h=h,
            w=w,
        )
        return dst_buf.to_numpy()
    finally:
        src_buf.destroy()
        blur_buf.destroy()
        lut_buf.destroy()
        dst_buf.destroy()


def enhance_grayscale(
    src,
    blur,
    lut,
    micro_contrast=2.93,
    clarity=0.0,
    noise_coring=0.0,
    return_gpu=False,
    dst=None,
):
    """Taichi AOT Grayscale Image Enhancement (1D LUT & Micro-Contrast) API"""
    if not isinstance(src, TaichiGPUBuffer) and not isinstance(blur, TaichiGPUBuffer):
        if dst is not None:
            raise ValueError(
                "blockwise enhance_grayscale does not support a destination buffer"
            )
        source = np.ascontiguousarray(src, dtype=np.float32)
        blurred = np.ascontiguousarray(blur, dtype=np.float32)
        table = np.ascontiguousarray(lut, dtype=np.float32)
        if source.ndim != 2 or blurred.shape != source.shape:
            raise ValueError("src and blur must be matching 2D arrays")
        result = _run_blockwise(
            "enhance_grayscale",
            (source, blurred),
            source.shape,
            np.float32,
            lambda src_tile, blur_tile: _enhance_grayscale_tile(
                src_tile, blur_tile, table, micro_contrast, clarity, noise_coring
            ),
            params={
                "lut_checksum": checksum(table),
                "micro_contrast": float(micro_contrast),
                "clarity": float(clarity),
                "noise_coring": float(noise_coring),
            },
        )
        if result is not None:
            return upload(result) if return_gpu else result

    src_buf = InputArray(src)
    blur_buf = InputArray(blur)
    lut_buf = InputArray(lut)

    h, w = src_buf.shape[:2]

    if dst is not None and dst.shape == (h, w) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w), dtype=np.float32)

    _mod("remap").run(
        "enhance_grayscale",
        src=src_buf,
        blur=blur_buf,
        lut=lut_buf,
        dst=dst_buf,
        micro_contrast=float(micro_contrast),
        clarity=float(clarity),
        noise_coring=float(noise_coring),
        h=h,
        w=w,
    )

    return dst_buf if return_gpu else dst_buf.to_numpy()


def _demosaic_blockwise(
    operation,
    bayer,
    run_tile,
    params,
    channels=3,
    halo=8,
):
    """Dispatch a Bayer-phase-safe local demosaic over cached halo tiles."""
    if not isinstance(bayer, np.ndarray) or bayer.ndim != 2:
        return None
    block_h, block_w = engine.get_block_config().normalized_size()
    if block_h % 2 or block_w % 2:
        return None
    source = np.ascontiguousarray(bayer)
    cache_mode = os.environ.get("PIXEL_REFINE_DEMOSAIC_BLOCK_CACHE", "auto")
    cache_outputs = cache_mode.strip().lower() not in {
        "0",
        "false",
        "off",
        "none",
        "disabled",
    }
    return _run_blockwise(
        operation,
        (source,),
        source.shape if channels == 1 else (*source.shape, channels),
        np.float32,
        run_tile,
        halo=halo,
        params=params,
        cache_outputs=cache_outputs,
        validate_output=lambda output, _tiles: (
            output.ndim == (2 if channels == 1 else 3)
            and (channels == 1 or output.shape[2] == channels)
            and np.isfinite(output).all()
        ),
    )


def _demosaic_half_blockwise(operation, bayer, run_tile, params, channels=1):
    """Evaluate a fused Bayer 2x2-to-one output graph per cached output tile."""
    if not isinstance(bayer, np.ndarray) or bayer.ndim != 2:
        return None
    source = np.ascontiguousarray(bayer)
    out_h, out_w = source.shape[0] // 2, source.shape[1] // 2
    grid = engine.plan_blocks(operation, (out_h, out_w), source.nbytes)
    if grid is None:
        return None
    output_shape = (out_h, out_w) if channels == 1 else (out_h, out_w, channels)
    result = np.empty(output_shape, dtype=np.float32)
    params = {"shape": output_shape, **params}
    cache = engine.get_block_cache()
    source_crc = checksum(source)
    scheduled = []
    for block in grid:
        raw_slice = (
            slice(block.y0 * 2, block.y1 * 2),
            slice(block.x0 * 2, block.x1 * 2),
        )
        block_id = block.make_id(str(source_crc), operation, params)
        scheduled.append(
            (cache.peek(block_id) is None, block.index, block, raw_slice, source_crc)
        )
    scheduled.sort(key=lambda item: (item[0], item[1]))
    for _cold, _index, block, raw_slice, source_crc in scheduled:
        raw_tile = np.ascontiguousarray(source[raw_slice])
        expected_shape = block.shape if channels == 1 else (*block.shape, channels)
        cached = _get_cached_output_tile(
            operation, block, source_crc, params, expected_shape
        )
        if cached is not None:
            result[block.write_slice] = cached
            continue
        last_error = None
        for _ in range(2):
            try:
                tile_result = np.ascontiguousarray(run_tile(raw_tile))
                if (
                    tile_result.shape != expected_shape
                    or not np.isfinite(tile_result).all()
                ):
                    raise RuntimeError(
                        f"{operation} returned an invalid half-resolution tile"
                    )
                result[block.write_slice] = tile_result
                _put_cached_output_tile(
                    operation, block, source_crc, params, tile_result
                )
                break
            except Exception as exc:
                last_error = exc
        else:
            raise RuntimeError(
                f"Unable to recover {operation} block {block.index}"
            ) from last_error
    return result


def _demosaic_params(wb, levels, cfa, cmatrix=None):
    params = {
        "wb": tuple(float(value) for value in wb),
        "levels": tuple(float(value) for value in levels),
        "cfa": tuple(int(value) for value in cfa),
    }
    if cmatrix is not None:
        params["cmatrix"] = checksum(np.ascontiguousarray(cmatrix))
    return params


def _release_owned_aot_buffer(buffer, original=None):
    if buffer is original:
        return
    if hasattr(buffer, "release"):
        buffer.release()
    elif hasattr(buffer, "destroy"):
        buffer.destroy()


def _mlri_common_scalars(
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    h,
    w,
):
    return {
        "wb_r": float(wb_r),
        "wb_g1": float(wb_g1),
        "wb_b": float(wb_b),
        "wb_g2": float(wb_g2),
        "black": float(black_level),
        "white": float(white_level),
        "h": int(h),
        "w": int(w),
        "c00": int(c00),
        "c01": int(c01),
        "c10": int(c10),
        "c11": int(c11),
    }


def _mlri_full_dispatch(
    graph_name,
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    output_channels,
    return_gpu=False,
    dst=None,
):
    if graph_name not in registered_graph_names("mlri"):
        raise ValueError(
            f"MLRI graph {graph_name!r} is not registered in the canonical "
            f"manifest; available={registered_graph_names('mlri')}"
        )

    vulkan_portable = engine.arch.lower() == "vulkan"
    separable = graph_name in {
        "mlri_admm_demosaic_separable",
        "mlri_admm_demosaic_guided",
    }
    output_shape = None
    with DemosaicBufferSet() as buffers:
        bayer_buf = buffers.input("bayer", bayer)
        h, w = bayer_buf.shape[:2]
        output_shape = (h, w, 3) if output_channels == 3 else (h, w)

        cmatrix_buf = None if vulkan_portable else buffers.input("cmatrix", cmatrix)
        scratch_names = (
            "wb_bayer", "green", "r_diff", "b_diff", "temp_a", "temp_b",
        )
        scratch = {
            name: buffers.scratch(name, (h, w), dtype=np.float32)
            for name in scratch_names
        }
        if separable:
            scratch["box_a"] = buffers.scratch("box_a", (h, w), dtype=np.float32)
            scratch["box_b"] = buffers.scratch("box_b", (h, w), dtype=np.float32)

        host_dst = None
        if dst is None:
            dst_buf = buffers.output("dst", output_shape, dtype=np.float32)
        elif isinstance(dst, TaichiGPUBuffer):
            if tuple(dst.shape) != output_shape or np.dtype(dst.dtype) != np.dtype(np.float32):
                raise ValueError(
                    f"MLRI dst must have shape={output_shape} dtype=float32; "
                    f"got shape={dst.shape} dtype={dst.dtype}"
                )
            dst_buf = buffers.register("dst", dst)
        else:
            host_dst = np.asarray(dst)
            if host_dst.shape != output_shape or np.dtype(host_dst.dtype) != np.dtype(np.float32):
                raise ValueError(
                    f"MLRI dst must have shape={output_shape} dtype=float32; "
                    f"got shape={host_dst.shape} dtype={host_dst.dtype}"
                )
            dst_buf = buffers.output("dst", output_shape, dtype=np.float32)

        arguments = {
            "bayer": bayer_buf,
            **scratch,
            "dst": dst_buf,
            "denoise_strength": 0.0,
            "eps": 1e-4,
            **_mlri_common_scalars(
                wb_r, wb_g1, wb_b, wb_g2, black_level, white_level,
                c00, c01, c10, c11, h, w,
            ),
        }
        if vulkan_portable:
            matrix = cmatrix.to_numpy() if hasattr(cmatrix, "to_numpy") else np.asarray(cmatrix)
            matrix = np.asarray(matrix, dtype=np.float32)
            if matrix.shape != (3, 3):
                raise ValueError(
                    f"MLRI color matrix must have shape (3, 3), got {matrix.shape}"
                )
            arguments.update({
                f"m{row}{col}": float(matrix[row, col])
                for row in range(3) for col in range(3)
            })
        else:
            arguments["cmatrix"] = cmatrix_buf

        try:
            _mod("mlri_admm").run(graph_name, **arguments)
            engine.sync()
            if return_gpu:
                return buffers.detach("dst")
            result = dst_buf.to_numpy()
            if host_dst is not None:
                np.copyto(host_dst, result)
                return host_dst
            return result
        except Exception as exc:
            raise RuntimeError(
                f"MLRI AOT graph '{graph_name}' failed for shape={(h, w)} "
                f"backend={getattr(engine, 'arch', 'unknown')}"
            ) from exc


@ti_thread
def mlri_admm(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Native full-resolution MLRI-ADMM RGB demosaic."""
    # The public API uses zero denoise strength today.  Resolve only graph
    # variants that are actually registered by the canonical builder.  Older
    # environment selectors are rejected instead of dispatching a stale ABI.
    if os.environ.get("PIXEL_REFINE_MLRI_BILATERAL", "0").strip() == "1":
        graph_name = "mlri_admm_demosaic"
    else:
        window_mode = (
            os.environ.get("PIXEL_REFINE_MLRI_WINDOW", "separable").strip().lower()
        )
        if window_mode == "auto" and isinstance(bayer, np.ndarray) and bayer.ndim == 2:
            # The current canonical builder exposes one full MLRI graph.  The
            # old reduced ``window3`` selector is not registered, so auto mode
            # resolves to the canonical graph instead of dispatching a stale
            # ABI.  Keep the public ``auto`` setting backward compatible.
            window_mode = "separable"
        if window_mode in {"separable", "sep", "default", "canonical"}:
            graph_name = resolve_graph_name("mlri", "default")
        else:
            # ``window3`` and ``guided`` were wrapper-only selectors; they
            # have no corresponding graph in the current manifest.
            graph_name = resolve_graph_name("mlri", window_mode)
    return _mlri_full_dispatch(
        graph_name,
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        output_channels=3,
        return_gpu=return_gpu,
        dst=dst,
    )


def _should_use_demosaic_blockwise(operation, bayer) -> bool:
    """Choose the safe demosaic execution mode without hiding overrides.

    OpenGL's host-tile path serializes every tile through the native bridge
    and retains host cache copies. Measurements on the supported desktop
    renderer show it slower *and* larger in RSS than the full graph, so
    ``auto`` uses full-frame on OpenGL. Users can force either behavior with
    ``PIXEL_REFINE_DEMOSAIC_EXECUTION``; the threshold remains available for
    explicitly constrained deployments.
    """
    mode = os.environ.get("PIXEL_REFINE_DEMOSAIC_EXECUTION", "auto").strip().lower()
    if mode in {"full", "frame", "full-frame", "full_frame"}:
        return False
    if mode in {"block", "blockwise", "tile", "tiled"}:
        return True
    if not isinstance(bayer, np.ndarray) or bayer.ndim != 2:
        return False
    arch = str(getattr(engine, "arch", "")).lower()
    if arch in {"opengl", "gles"}:
        try:
            # The pipeline planner may have enabled bounded block mode from
            # the current resident-memory budget. Honour that decision even
            # when no explicit demosaic environment override is present.
            if bool(getattr(engine.get_block_config(), "enabled", False)):
                return True
        except Exception:
            pass
        threshold_mp = float(
            os.environ.get("PIXEL_REFINE_DEMOSAIC_AUTO_FULL_MP", "inf")
        )
        return (bayer.size / 1_000_000.0) > max(0.0, threshold_mp)
    if arch in {"vulkan", "cuda"}:
        # A full graph avoids a host round-trip for every halo tile and is
        # substantially faster when the intermediate planes fit.  Estimate
        # the peak from the graph's simultaneous float32 planes, then keep a
        # conservative margin for the input/output transport and the runtime
        # pool.  Larger frames remain on the bounded tile path.
        bytes_per_pixel = {
            "dcb": 36,  # bayer + mosaic + green + rgb_a + dst
            "arm": 40,  # bayer + six scalar planes + RGB dst
            "hamilton": 40,
            "mlri_admm": 52,  # bayer + guided/filter scratch + RGB dst
        }.get(str(operation).lower(), 48)
        try:
            status = engine.get_memory_status(force=True)
            limit = int(status.get("pipeline_resident_limit", 0) or 0)
            available = int(status.get("device_heap_available", 0) or 0)
            if limit <= 0:
                limit = int(available * 0.65) if available > 0 else 0
            resident = int(status.get("resident_bytes", 0) or 0)
        except Exception:
            limit = 0
            resident = 0
        estimated = int(bayer.size) * int(bytes_per_pixel)
        safety = float(os.environ.get("PIXEL_REFINE_DEMOSAIC_FULL_SAFETY", "1.10"))
        usable = int(max(0, limit - resident) * 0.95)
        if usable > 0:
            return int(estimated * max(1.0, safety)) > usable
    return True


def mlri_admm_demosaic(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Backward-compatible name for :func:`mlri_admm`."""
    return mlri_admm(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
    )


def _mlri_fused_dispatch(
    graph_name,
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    output_shape,
    cmatrix=None,
    return_gpu=False,
    dst=None,
):
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]
    matrix_buf = InputArray(cmatrix) if cmatrix is not None else None
    if (
        dst is not None
        and tuple(dst.shape) == tuple(output_shape)
        and dst.dtype == np.float32
    ):
        dst_buf = dst
    else:
        dst_buf = OutputArray(output_shape, dtype=np.float32)
    arguments = {
        "bayer": bayer_buf,
        "dst": dst_buf,
        **_mlri_common_scalars(
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            h,
            w,
        ),
    }
    if matrix_buf is not None:
        arguments["cmatrix"] = matrix_buf
    _mod("mlri_admm").run(graph_name, **arguments)
    engine.sync()
    _release_owned_aot_buffer(bayer_buf, bayer)
    if matrix_buf is not None:
        _release_owned_aot_buffer(matrix_buf, cmatrix)
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def mlri_admm_demosaic_1channel(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    bayer_shape = tuple(bayer.shape)
    return _mlri_fused_dispatch(
        "mlri_admm_demosaic_1channel",
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        bayer_shape[:2],
        return_gpu=return_gpu,
        dst=dst,
    )


@ti_thread
def mlri_admm_demosaic_half_res(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    h, w = tuple(bayer.shape)[:2]
    return _mlri_fused_dispatch(
        "mlri_admm_demosaic_half_res",
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        (h // 2, w // 2),
        return_gpu=return_gpu,
        dst=dst,
    )


@ti_thread
def mlri_admm_demosaic_rgb_half_res(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    h, w = tuple(bayer.shape)[:2]
    return _mlri_fused_dispatch(
        "mlri_admm_demosaic_rgb_half_res",
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        (h // 2, w // 2, 3),
        cmatrix=cmatrix,
        return_gpu=return_gpu,
        dst=dst,
    )


@ti_thread
def mlri_admm_demosaic_3channel(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Native full MLRI reconstruction reduced to luminance."""
    return _mlri_full_dispatch(
        "mlri_admm_demosaic_3channel",
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        output_channels=1,
        return_gpu=return_gpu,
        dst=dst,
    )


def _dispatch_hamilton_buffers(
    bayer_buf,
    cmatrix_buf,
    wb_bayer_buf,
    green_buf,
    r_diff_buf,
    b_diff_buf,
    r_diff_f_buf,
    b_diff_f_buf,
    dst_buf,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    h,
    w,
):
    _mod("hamilton").run(
        "hamilton_demosaic",
        bayer=bayer_buf,
        cmatrix=cmatrix_buf,
        wb_bayer=wb_bayer_buf,
        green=green_buf,
        dst=dst_buf,
        r_diff=r_diff_buf,
        b_diff=b_diff_buf,
        r_diff_filtered=r_diff_f_buf,
        b_diff_filtered=b_diff_f_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )


@ti_thread
def hamilton(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
    tonemapping=False,
):
    if (
        not return_gpu
        and dst is None
        and _should_use_demosaic_blockwise("hamilton", bayer)
    ):
        params = {
            "wb": (float(wb_r), float(wb_g1), float(wb_b), float(wb_g2)),
            "levels": (float(black_level), float(white_level)),
            "cfa": (int(c00), int(c01), int(c10), int(c11)),
            "cmatrix": checksum(np.ascontiguousarray(cmatrix)),
        }
        result = _demosaic_blockwise(
            "hamilton_demosaic",
            bayer,
            lambda tile: _hamilton_demosaic_full(
                tile,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                cmatrix,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
                tonemapping=tonemapping,
            ),
            params,
        )
        if result is not None:
            return result
    return _hamilton_demosaic_full(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
        tonemapping=tonemapping,
    )


def hamilton_demosaic(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Backward-compatible name for :func:`hamilton`."""
    return hamilton(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
    )


def _hamilton_demosaic_full(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
    tonemapping=False,
):
    """Run the direct Hamilton graph with a Bilinear-style buffer lifecycle.

    The current Hamilton graph performs its edge-directed green pass and
    red/blue reconstruction directly from the Bayer input.  It therefore only
    needs one green scratch plane and the destination.  The former wrapper
    allocated six additional full-resolution planes for an older graph ABI;
    on CUDA those allocations could exhaust the resident budget before the
    first host-to-device copy.  ``cmatrix`` is uploaded only for the optional
    tonemapping graph, exactly as Bilinear uploads the matrix it actually uses.
    """
    bayer_dtype = np.dtype(getattr(bayer, "dtype", np.float32))
    use_u16_graph = (
        bayer_dtype == np.dtype(np.uint16)
        and aot_graph_available("hamilton", "hamilton_demosaic_u16")
    )
    if bayer_dtype == np.dtype(np.uint16) and not use_u16_graph:
        # Compatibility with older Hamilton TCMs: preserve the old f32 graph
        # contract instead of dispatching a u16 buffer into an f32 ABI.
        if isinstance(bayer, TaichiGPUBuffer):
            bayer = np.ascontiguousarray(bayer.to_numpy(), dtype=np.float32)
        else:
            bayer = np.ascontiguousarray(bayer, dtype=np.float32)

    with DemosaicBufferSet() as buffers:
        bayer_buf = buffers.input("bayer", bayer)
        h, w = bayer_buf.shape[:2]
        cmatrix_buf = (
            buffers.input("cmatrix", cmatrix) if tonemapping else None
        )
        host_dst = None

        if dst is None:
            dst_buf = buffers.output("dst", (h, w, 3), dtype=np.float32)
        elif isinstance(dst, TaichiGPUBuffer):
            if tuple(dst.shape) != (h, w, 3) or np.dtype(dst.dtype) != np.dtype(np.float32):
                raise ValueError(
                    f"Hamilton dst must have shape={(h, w, 3)} dtype=float32; "
                    f"got shape={dst.shape} dtype={dst.dtype}"
                )
            dst_buf = buffers.register("dst", dst)
        else:
            dst_array = np.asarray(dst)
            if dst_array.shape != (h, w, 3) or np.dtype(dst_array.dtype) != np.dtype(np.float32):
                raise ValueError(
                    f"Hamilton dst must have shape={(h, w, 3)} dtype=float32; "
                    f"got shape={dst_array.shape} dtype={dst_array.dtype}"
                )
            host_dst = dst_array
            dst_buf = buffers.output("dst", (h, w, 3), dtype=np.float32)

        green_buf = buffers.scratch("green", (h, w), dtype=np.float32)
        graph_name = resolve_graph_name(
            "hamilton", "tonemapped" if tonemapping else "default"
        )
        if use_u16_graph and not tonemapping:
            graph_name = "hamilton_demosaic_u16"
        run_kwargs = {
            "bayer": bayer_buf,
            "green": green_buf,
            "dst": dst_buf,
            "wb_r": float(wb_r),
            "wb_g1": float(wb_g1),
            "wb_b": float(wb_b),
            "wb_g2": float(wb_g2),
            "black": float(black_level),
            "white": float(white_level),
            "h": int(h),
            "w": int(w),
            "c00": int(c00),
            "c01": int(c01),
            "c10": int(c10),
            "c11": int(c11),
        }
        if cmatrix_buf is not None:
            run_kwargs["cmatrix"] = cmatrix_buf

        try:
            _mod("hamilton").run(graph_name, **run_kwargs)
            engine.sync()
            if return_gpu:
                result = buffers.detach("dst")
            else:
                result = dst_buf.to_numpy()
                if host_dst is not None:
                    np.copyto(host_dst, result)
                    result = host_dst
            return result
        except Exception as exc:
            raise RuntimeError(
                f"Hamilton AOT graph '{graph_name}' failed for shape={(h, w)} "
                f"backend={getattr(engine, 'arch', 'unknown')}. "
                "Recompile the Hamilton target-qualified TCM if its graph ABI is stale."
            ) from exc


def _dcb_parameters(
    wb_r, wb_g1, wb_b, wb_g2, black_level, white_level, c00, c01, c10, c11
):
    return {
        "algorithm": "dcb_cleanroom_v1",
        "wb": (float(wb_r), float(wb_g1), float(wb_b), float(wb_g2)),
        "levels": (float(black_level), float(white_level)),
        "cfa": (int(c00), int(c01), int(c10), int(c11)),
    }


@ti_thread
def dcb(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
    preserve_headroom=False,
):
    """Return normalized linear, white-balanced camera RGB in ``0..1``.

    The default path normalizes white-balance gains and clamps the final DCB
    result to ``0..1``. ``preserve_headroom=True`` remains available only as
    an explicit opt-in compatibility path.

    ``cmatrix`` is retained for API compatibility but deliberately not applied.
    """
    if not return_gpu and dst is None and _should_use_demosaic_blockwise("dcb", bayer):
        result = _demosaic_blockwise(
            "dcb_demosaic",
            bayer,
            lambda tile: _dcb_demosaic_full(
                tile,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                cmatrix,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
                preserve_headroom=preserve_headroom,
            ),
            _dcb_parameters(
                wb_r, wb_g1, wb_b, wb_g2, black_level, white_level, c00, c01, c10, c11
            ),
            halo=16,
        )
        if result is not None:
            return result
    return _dcb_demosaic_full(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
        preserve_headroom=preserve_headroom,
    )


def dcb_demosaic(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
    preserve_headroom=False,
):
    """Backward-compatible name for :func:`dcb`."""
    return dcb(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
        preserve_headroom=preserve_headroom,
    )


@ti_thread
def bilinear(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
    half_res=False,
):
    """Fast Ultra-Low-Latency Bilinear Bayer Demosaicing (<25ms target).

    ``half_res=True`` returns a half-resolution RGB image (like rawpy
    ``half_size=True``).  Output is linear RGB (white balance + color matrix
    applied, no gamma) so callers can run ``naturalTonemapping`` after, in the
    same pipeline order as the other demosaic families.
    """
    # InputArray returns caller-owned GPU buffers unchanged. Host inputs are
    # uploaded here and released by this wrapper after dispatch. Initializing
    # the handles before entering the try block also makes partial setup safe:
    # a failed cmatrix upload or invalid destination still releases bayer.
    bayer_buf = cmatrix_buf = dst_buf = None
    owns_bayer = owns_cmatrix = owns_dst = False
    host_dst = None
    dispatch_synced = False
    try:
        bayer_buf = InputArray(bayer)
        owns_bayer = bayer_buf is not bayer
        cmatrix_buf = InputArray(cmatrix)
        owns_cmatrix = cmatrix_buf is not cmatrix
        h, w = bayer_buf.shape[:2]
        out_h, out_w = (h // 2, w // 2) if half_res else (h, w)

        if dst is None:
            dst_buf = OutputArray((out_h, out_w, 3), dtype=np.float32)
            owns_dst = True
        elif isinstance(dst, TaichiGPUBuffer):
            if tuple(dst.shape) != (out_h, out_w, 3) or np.dtype(dst.dtype) != np.dtype(np.float32):
                raise ValueError(
                    f"Bilinear dst must have shape={(out_h, out_w, 3)} dtype=float32; "
                    f"got shape={dst.shape} dtype={dst.dtype}"
                )
            dst_buf = dst
        else:
            dst_array = np.asarray(dst)
            if dst_array.shape != (out_h, out_w, 3) or np.dtype(dst_array.dtype) != np.dtype(np.float32):
                raise ValueError(
                    f"Bilinear dst must have shape={(out_h, out_w, 3)} dtype=float32; "
                    f"got shape={dst_array.shape} dtype={dst_array.dtype}"
                )
            # The demosaic graphs declare ``dst`` as a plain 3-D ndarray,
            # whereas generic upload auto-promotes RGB arrays to vector
            # fields. Allocate the matching plain ndarray descriptor and copy
            # the result back to the caller's host array after readback.
            dst_buf = OutputArray((out_h, out_w, 3), dtype=np.float32)
            host_dst = dst_array
            owns_dst = True

        graph_name = resolve_graph_name(
            "bilinear", "rgb_half_res" if half_res else "default"
        )
        _mod("bilinear_demosaice").run(
            graph_name,
            bayer=bayer_buf,
            cmatrix=cmatrix_buf,
            dst=dst_buf,
            wb_r=float(wb_r),
            wb_g1=float(wb_g1),
            wb_b=float(wb_b),
            wb_g2=float(wb_g2),
            black=float(black_level),
            white=float(white_level),
            h=int(h),
            w=int(w),
            c00=int(c00),
            c01=int(c01),
            c10=int(c10),
            c11=int(c11),
            linear=1,
        )
        engine.sync()
        dispatch_synced = True
        if return_gpu:
            return dst_buf
        result = dst_buf.to_numpy()
        if host_dst is not None:
            np.copyto(host_dst, result)
            return host_dst
        return result
    finally:
        # If dispatch or readback fails, synchronize before returning buffers
        # to the pool so the native graph cannot still reference them.
        if not dispatch_synced:
            try:
                engine.sync()
            except Exception:
                pass
        if owns_bayer and bayer_buf is not None:
            _release_owned_aot_buffer(bayer_buf, bayer)
        if owns_cmatrix and cmatrix_buf is not None:
            _release_owned_aot_buffer(cmatrix_buf, cmatrix)
        # A caller-provided GPU destination remains caller-owned.  An owned
        # destination is retained only when return_gpu=True transfers it out.
        if owns_dst and not return_gpu and dst_buf is not None:
            _release_owned_aot_buffer(dst_buf)


def bilinear_demosaic(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
    half_res=False,
):
    """Backward-compatible name for :func:`bilinear`."""
    return bilinear(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
        half_res=half_res,
    )


def _dcb_demosaic_full(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
    preserve_headroom=False,
):
    if not preserve_headroom:
        wb_scale = max(float(wb_r), float(wb_g1), float(wb_b), float(wb_g2), 1e-6)
        wb_r = float(wb_r) / wb_scale
        wb_g1 = float(wb_g1) / wb_scale
        wb_b = float(wb_b) / wb_scale
        wb_g2 = float(wb_g2) / wb_scale
    dcb_mode = os.environ.get("PIXEL_REFINE_DCB_MODE", "canonical").strip().lower()
    fast_mode = not preserve_headroom and (
        dcb_mode in {"fast", "realtime", "low_latency"}
        or os.environ.get("PIXEL_REFINE_DCB_FAST", "0").strip().lower()
        in {"1", "true", "yes", "on"}
    )

    cross_mode = not preserve_headroom and dcb_mode in {"cross", "refined_cross"}
    if fast_mode or cross_mode:
        raise ValueError(
            "The requested DCB mode is not registered in the canonical AOT "
            "graph manifest. Use the canonical DCB graph or compile/register "
            "a dedicated variant before enabling this selector."
        )

    with DemosaicBufferSet() as buffers:
        bayer_buf = buffers.input("bayer", bayer)
        h, w = bayer_buf.shape[:2]
        host_dst = None
        if dst is None:
            dst_buf = buffers.output("dst", (h, w, 3), dtype=np.float32)
        elif isinstance(dst, TaichiGPUBuffer):
            if tuple(dst.shape) != (h, w, 3) or np.dtype(dst.dtype) != np.dtype(np.float32):
                raise ValueError(
                    f"DCB dst must have shape={(h, w, 3)} dtype=float32; "
                    f"got shape={dst.shape} dtype={dst.dtype}"
                )
            dst_buf = buffers.register("dst", dst)
        else:
            host_dst = np.asarray(dst)
            if host_dst.shape != (h, w, 3) or np.dtype(host_dst.dtype) != np.dtype(np.float32):
                raise ValueError(
                    f"DCB dst must have shape={(h, w, 3)} dtype=float32; "
                    f"got shape={host_dst.shape} dtype={host_dst.dtype}"
                )
            dst_buf = buffers.output("dst", (h, w, 3), dtype=np.float32)

        mosaic = buffers.scratch("mosaic", (h, w), dtype=np.float32)
        green = buffers.scratch("green", (h, w), dtype=np.float32)
        rgb_a = dst_buf if fast_mode else buffers.scratch(
            "rgb_a", (h, w, 3), dtype=np.float32
        )
        rgb_b = dst_buf if (fast_mode or cross_mode or not preserve_headroom) else buffers.scratch(
            "rgb_b", (h, w, 3), dtype=np.float32
        )
        graph_name = resolve_graph_name(
            "dcb", "headroom" if preserve_headroom else "default"
        )
        try:
            _mod("dcb").run(
                graph_name,
                bayer=bayer_buf,
                mosaic=mosaic,
                green=green,
                rgb_a=rgb_a,
                rgb_b=rgb_b,
                dst=dst_buf,
                wb_r=float(wb_r),
                wb_g1=float(wb_g1),
                wb_b=float(wb_b),
                wb_g2=float(wb_g2),
                black=float(black_level),
                white=float(white_level),
                h=int(h),
                w=int(w),
                c00=int(c00),
                c01=int(c01),
                c10=int(c10),
                c11=int(c11),
            )
            engine.sync()
            if return_gpu:
                return buffers.detach("dst")
            result = dst_buf.to_numpy()
            if host_dst is not None:
                np.copyto(host_dst, result)
                return host_dst
            return result
        except Exception as exc:
            raise RuntimeError(
                f"DCB AOT graph '{graph_name}' failed for shape={(h, w)} "
                f"backend={getattr(engine, 'arch', 'unknown')}"
            ) from exc


def _demosaic_blockwise_u16(
    operation,
    bayer,
    run_tile,
    params,
    *,
    channels=3,
    halo=8,
):
    """Run native demosaic tiles and stitch directly into an integer output.

    The RAW application route requests ``output_bgr_u16=True``.  That route
    historically asked the full-frame wrapper for a live GPU buffer, which
    bypassed the block planner even when the residency governor had selected
    bounded tiles.  This adapter keeps the public API unchanged while making
    the conversion tile-local: the demosaic graph still executes on the
    selected backend, and only the small integer tile is retained for the
    host-side stitch.  The ``+0.5`` rule matches the canonical
    ``rgb_to_bgr_i32`` graph's round-to-nearest conversion.
    """
    if channels != 3:
        return None
    if not isinstance(bayer, np.ndarray) or bayer.ndim != 2:
        return None
    block_h, block_w = engine.get_block_config().normalized_size()
    if block_h % 2 or block_w % 2:
        return None
    source = np.ascontiguousarray(bayer)
    cache_mode = os.environ.get("PIXEL_REFINE_DEMOSAIC_BLOCK_CACHE", "auto")
    cache_outputs = cache_mode.strip().lower() not in {
        "0",
        "false",
        "off",
        "none",
        "disabled",
    }

    def _run_u16_tile(tile):
        rgb = np.asarray(run_tile(tile), dtype=np.float32)
        if rgb.ndim != 3 or rgb.shape[2] != 3 or not np.isfinite(rgb).all():
            raise RuntimeError(f"{operation} returned an invalid RGB tile")
        scaled = np.clip(rgb * np.float32(65535.0) + np.float32(0.5), 0.0, 65535.0)
        out = np.empty(scaled.shape, dtype=np.uint16)
        out[..., 0] = scaled[..., 2].astype(np.uint16, copy=False)
        out[..., 1] = scaled[..., 1].astype(np.uint16, copy=False)
        out[..., 2] = scaled[..., 0].astype(np.uint16, copy=False)
        return out

    return _run_blockwise(
        operation,
        (source,),
        (*source.shape, 3),
        np.uint16,
        _run_u16_tile,
        halo=halo,
        params={**(params or {}), "output_dtype": np.dtype(np.uint16).str},
        cache_outputs=cache_outputs,
        validate_output=lambda output, _tiles: (
            output.ndim == 3
            and output.shape[2] == 3
            and np.isfinite(output.astype(np.float32)).all()
        ),
    )


@ti_thread
def dcb_demosaic_1channel(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]
    dst_buf = (
        dst
        if dst is not None and dst.shape == (h, w) and dst.dtype == np.float32
        else OutputArray((h, w), dtype=np.float32)
    )
    _mod("dcb").run(
        "dcb_demosaic_1channel",
        bayer=bayer_buf,
        gray=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )
    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
@_block_recovery("dcb_demosaic_rgb_half_res")
def dcb_demosaic_rgb_half_res(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]
    shape = (h // 2, w // 2, 3)
    dst_buf = (
        dst
        if dst is not None and dst.shape == shape and dst.dtype == np.float32
        else OutputArray(shape, dtype=np.float32)
    )
    _mod("dcb").run(
        "dcb_demosaic_rgb_half_res",
        bayer=bayer_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )
    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
@_block_recovery("dcb_demosaic_half_res")
def dcb_demosaic_half_res(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]
    rgb_half = engine.allocate((h // 2, w // 2, 3), dtype=np.float32, is_vector=False)
    shape = (h // 2, w // 2)
    dst_buf = (
        dst
        if dst is not None and dst.shape == shape and dst.dtype == np.float32
        else OutputArray(shape, dtype=np.float32)
    )
    _mod("dcb").run(
        "dcb_demosaic_half_res",
        bayer=bayer_buf,
        dst=rgb_half,
        gray=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )
    engine.sync()
    rgb_half.release()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def dcb_demosaic_3channel(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """DCB camera-RGB demosaic reduced to linear luminance."""
    rgb = dcb_demosaic(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=True,
    )
    h, w = rgb.shape[:2]
    dst_buf = (
        dst
        if dst is not None and dst.shape == (h, w) and dst.dtype == np.float32
        else OutputArray((h, w), dtype=np.float32)
    )
    _mod("dcb").run("dcb_rgb_to_luma", rgb_a=rgb, gray=dst_buf, h=int(h), w=int(w))
    engine.sync()
    rgb.release()
    return dst_buf if return_gpu else dst_buf.to_numpy()


def _highlight_recovery_tile(tile, wb_r, wb_g, wb_b, strength):
    """Run one 11x11-neighbour highlight-recovery tile."""
    owner = engine.upload(np.ascontiguousarray(tile, dtype=np.float32))
    source = owner.view_as_vector(False)
    dst = engine.allocate(tile.shape, dtype=np.float32, is_vector=False)
    try:
        _mod("highlight_recovery").run(
            "highlight_recover_rgb",
            src=source,
            dst=dst,
            wb_r=float(wb_r),
            wb_g=float(wb_g),
            wb_b=float(wb_b),
            strength=float(np.clip(strength, 0.0, 1.0)),
            h=int(tile.shape[0]),
            w=int(tile.shape[1]),
        )
        return dst.to_numpy()
    finally:
        dst.destroy()
        owner.destroy()


def highlight_recovery(
    rgb, wb_r=1.0, wb_g=1.0, wb_b=1.0, strength=1.0, return_gpu=False, dst=None
):
    """Recover highlights and map linear camera RGB to the ``0..1`` range.

    The input may contain white-balance headroom above ``1.0`` but must not
    have a tone curve, display gamma, or colour matrix applied. ``wb_*`` must
    use the same gains used by demosaic. The recovery graph clamps its output
    to ``0..1``.
    """
    # The recovery kernel reads an 11x11 neighbourhood.  Host inputs can be
    # safely decomposed with a five-pixel halo; GPU-buffer callers keep the
    # existing zero-copy full-frame contract, especially when a caller
    # supplied an output buffer.
    if not isinstance(rgb, TaichiGPUBuffer) and dst is None:
        array = np.ascontiguousarray(rgb, dtype=np.float32)
        if array.ndim != 3 or array.shape[2] != 3:
            raise ValueError(
                "highlight_recovery expects an HxWx3 float32 linear RGB image"
            )
        result = _run_blockwise(
            "highlight_recovery",
            (array,),
            array.shape,
            np.float32,
            lambda tile: _highlight_recovery_tile(tile, wb_r, wb_g, wb_b, strength),
            halo=5,
            params={
                "wb_r": float(wb_r),
                "wb_g": float(wb_g),
                "wb_b": float(wb_b),
                "strength": float(np.clip(strength, 0.0, 1.0)),
            },
        )
        if result is not None:
            return upload(result) if return_gpu else result

    src_buf = (
        rgb
        if isinstance(rgb, TaichiGPUBuffer)
        else upload(np.ascontiguousarray(rgb, dtype=np.float32), is_vector=False)
    )
    if len(src_buf.shape) != 3 or src_buf.shape[2] != 3:
        if not isinstance(rgb, TaichiGPUBuffer):
            src_buf.release()
        raise ValueError("highlight_recovery expects an HxWx3 float32 linear RGB image")
    h, w = src_buf.shape[:2]
    src_view = (
        src_buf.view_as_vector(False)
        if getattr(src_buf, "is_vector", False)
        else src_buf
    )
    if dst is not None and dst.shape == (h, w, 3) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = engine.allocate((h, w, 3), dtype=np.float32, is_vector=False)
    dst_view = (
        dst_buf.view_as_vector(False)
        if getattr(dst_buf, "is_vector", False)
        else dst_buf
    )
    _mod("highlight_recovery").run(
        "highlight_recover_rgb",
        src=src_view,
        dst=dst_view,
        wb_r=float(wb_r),
        wb_g=float(wb_g),
        wb_b=float(wb_b),
        strength=float(np.clip(strength, 0.0, 1.0)),
        h=int(h),
        w=int(w),
    )
    engine.sync()
    if not isinstance(rgb, TaichiGPUBuffer):
        src_buf.release()
    return dst_buf if return_gpu else dst_buf.to_numpy()


_TONE_MAPPING_LUT_CACHE = {}


def get_natural_tone_mapping_lut(
    exposure=1.43,
    shoulder=2.99,
    gamma=1.50,
    shadow_offset=0.01,
    lut_size=65536,
):
    key = (exposure, shoulder, gamma, shadow_offset, lut_size)
    if key in _TONE_MAPPING_LUT_CACHE:
        return _TONE_MAPPING_LUT_CACHE[key]

    raw_indices = np.linspace(0.0, 1.0, lut_size, dtype=np.float32)
    x = np.maximum(0.0, raw_indices - shadow_offset)
    x = x * exposure
    if abs(shoulder - 1.0) > 1e-4:
        denom = np.power(1.0 + np.power(x, shoulder), 1.0 / shoulder)
        x = x / np.maximum(denom, 1e-8)
    else:
        x = x / np.sqrt(1.0 + x * x)
    x = np.clip(x, 0.0, 1.0)
    if abs(gamma - 1.0) > 1e-4:
        x = np.power(x, 1.0 / gamma)

    lut = np.clip(x, 0.0, 1.0).astype(np.float32)
    _TONE_MAPPING_LUT_CACHE[key] = lut
    return lut


def apply_coarse_texture_boost(img_float, texture_amount=0.0, radius=10):
    """Boost coarse textures (mid-frequency details/clarity) without amplifying fine noise.

    Args:
        img_float: float32 image [0, 1]
        texture_amount: boost intensity [0.0, 2.0]
        radius: Gaussian kernel radius for coarse scale (default 10)
    """
    if abs(texture_amount) < 1e-4:
        return img_float

    # Pure Taichi AOT Gaussian Blur on GPU/Engine (No OpenCV cv2 dependency)
    blurred = gaussian_blur(img_float, sigma=float(radius), return_gpu=False)

    # Extract mid-frequency coarse texture layer
    coarse_texture = img_float - blurred

    # Soft saturation curve to prevent halo artifacts around high-contrast edges
    soft_texture = coarse_texture / np.sqrt(1.0 + np.square(coarse_texture * 4.0))

    enhanced = img_float + texture_amount * soft_texture
    return np.clip(enhanced, 0.0, 1.0)


_COARSE_TEXTURE_IDENTITY_LUT = np.linspace(0.0, 1.0, 256, dtype=np.float32)


def coarse_texture_boost_gpu(src, texture_amount=0.30, radius=10, dst=None):
    """Boost coarse/mid-frequency texture entirely through the AOT GPU path.

    This is intentionally separate from :func:`apply_coarse_texture_boost`,
    whose legacy API returns a NumPy array.  The spatial matcher needs a
    temporary analysis image and must not read the image back to the CPU.

    ``enhance_grayscale`` performs the pointwise detail shaping in one AOT
    dispatch after the Gaussian low-pass.  The identity LUT preserves the
    original tone response; only the detail residual is scaled.
    """
    if not isinstance(src, TaichiGPUBuffer):
        raise TypeError("coarse_texture_boost_gpu requires a TaichiGPUBuffer")
    if len(src.shape) != 2 or getattr(src, "dtype", None) != np.float32:
        raise ValueError("coarse_texture_boost_gpu requires a float32 2D buffer")

    amount = float(texture_amount)
    if abs(amount) < 1e-6:
        return src if dst is None else copy_field(src, dst) or dst

    blur = engine.allocate(src.shape, dtype=np.float32)
    try:
        gaussian_blur(
            src,
            sigma=float(radius),
            return_gpu=True,
            dst=blur,
        )
        return enhance_grayscale(
            src,
            blur,
            _COARSE_TEXTURE_IDENTITY_LUT,
            micro_contrast=amount,
            clarity=0.0,
            noise_coring=0.0,
            return_gpu=True,
            dst=dst,
        )
    finally:
        blur.destroy()


def apply_natural_tone_mapping_np(
    src_np,
    exposure=1.43,
    shoulder=2.99,
    gamma=1.50,
    shadow_offset=0.01,
    saturation=1.00,
    texture_amount=0.0,
    texture_radius=10,
):
    # Pre-cached 1D LUT lookup for 100x speedup
    if src_np.dtype == np.uint16:
        lut = get_natural_tone_mapping_lut(
            exposure=exposure,
            shoulder=shoulder,
            gamma=gamma,
            shadow_offset=shadow_offset,
            lut_size=65536,
        )
        x = lut[src_np]
    elif src_np.dtype in (np.float32, np.float64):
        lut = get_natural_tone_mapping_lut(
            exposure=exposure,
            shoulder=shoulder,
            gamma=gamma,
            shadow_offset=shadow_offset,
            lut_size=65536,
        )
        idx = np.clip((src_np * 65535.0).astype(np.int32, copy=False), 0, 65535)
        x = lut[idx]
    else:
        x = np.maximum(0.0, src_np.astype(np.float32) - shadow_offset)
        x = x * exposure
        if abs(shoulder - 1.0) > 1e-4:
            denom = np.power(1.0 + np.power(x, shoulder), 1.0 / shoulder)
            x = x / np.maximum(denom, 1e-8)
        else:
            x = x / np.sqrt(1.0 + x * x)
        x = np.clip(x, 0.0, 1.0)
        if abs(gamma - 1.0) > 1e-4:
            x = np.power(x, 1.0 / gamma)

    if abs(saturation - 1.0) > 1e-4 and x.ndim == 3 and x.shape[2] == 3:
        luma = 0.299 * x[:, :, 0] + 0.587 * x[:, :, 1] + 0.114 * x[:, :, 2]
        luma_3ch = np.stack([luma, luma, luma], axis=-1)
        x = luma_3ch + saturation * (x - luma_3ch)
        x = np.clip(x, 0.0, 1.0)

    if abs(texture_amount) > 1e-4:
        x = apply_coarse_texture_boost(
            x, texture_amount=texture_amount, radius=texture_radius
        )

    return x.astype(np.float32, copy=False)


def naturalTonemapping(
    src,
    return_gpu=False,
    dst=None,
    exposure=None,
    shoulder=None,
    gamma=None,
    shadow_offset=None,
    saturation=None,
    texture_amount=None,
    texture_radius=None,
):
    """Parametric natural display transform with default tuned parameters loaded from config.py."""
    try:
        from config import DEFAULT_TONE_MAPPING_PARAMS

        defaults = DEFAULT_TONE_MAPPING_PARAMS
    except Exception:
        defaults = {
            "exposure": 1.43,
            "shoulder": 2.99,
            "gamma": 1.50,
            "shadow_offset": 0.01,
            "saturation": 1.00,
            "texture_amount": 0.0,
            "texture_radius": 10,
        }

    exposure = defaults["exposure"] if exposure is None else exposure
    shoulder = defaults["shoulder"] if shoulder is None else shoulder
    gamma = defaults["gamma"] if gamma is None else gamma
    shadow_offset = (
        defaults["shadow_offset"] if shadow_offset is None else shadow_offset
    )
    saturation = defaults["saturation"] if saturation is None else saturation
    texture_amount = (
        defaults["texture_amount"] if texture_amount is None else texture_amount
    )
    texture_radius = (
        defaults["texture_radius"] if texture_radius is None else texture_radius
    )
    if isinstance(src, TaichiGPUBuffer):
        src_np = src.to_numpy()
        was_gpu_in = True
    else:
        src_np = src
        was_gpu_in = False

    toned_np = apply_natural_tone_mapping_np(
        src_np,
        exposure=exposure,
        shoulder=shoulder,
        gamma=gamma,
        shadow_offset=shadow_offset,
        saturation=saturation,
        texture_amount=texture_amount,
        texture_radius=texture_radius,
    )

    if return_gpu:
        if dst is not None and isinstance(dst, TaichiGPUBuffer):
            dst_buf = dst
            dst_buf.copy_from(toned_np)
        else:
            dst_buf = upload(toned_np)
        return dst_buf

    return toned_np


def tone_map_srgb(src, return_gpu=False, dst=None):
    """Compatibility alias for :func:`naturalTonemapping`."""
    return naturalTonemapping(src, return_gpu=return_gpu, dst=dst)


def AutoEnhance(
    src,
    params=None,
    return_params=False,
    return_gpu=False,
    dst=None,
    **kwargs,
):
    """
    Histogram-Guided Adaptive Natural Tone Mapping with Decoupled Analysis.
    - If `params` is None: Analyzes histogram on `src` first.
    - If `params` is provided: Applies tone mapping directly without re-computing analysis.
    """
    from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
        AutoEnhance as _AutoEnhance,
    )

    return _AutoEnhance(
        src,
        params=params,
        return_params=return_params,
        return_gpu=return_gpu,
        dst=dst,
        **kwargs,
    )


def analyze_auto_enhance_params(src, mode: str = "natural"):
    """Analyze luminance histogram metrics and return adaptive tone mapping parameters."""
    from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
        analyze_auto_enhance_params as _analyze,
    )

    return _analyze(src, mode=mode)


@ti_thread
def hamilton_demosaic_1channel(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    if not return_gpu and dst is None:
        result = _demosaic_blockwise(
            "hamilton_demosaic_1channel",
            bayer,
            lambda tile: _hamilton_demosaic_1channel_full(
                tile,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
            ),
            _demosaic_params(
                (wb_r, wb_g1, wb_b, wb_g2),
                (black_level, white_level),
                (c00, c01, c10, c11),
            ),
            channels=1,
            halo=4,
        )
        if result is not None:
            return result
    return _hamilton_demosaic_1channel_full(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
    )


def _hamilton_demosaic_1channel_full(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Fast Green-Only Demosaic to Grayscale 1-channel (Fused Single-Pass)."""
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]

    if dst is not None and dst.shape == (h, w) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w), dtype=np.float32)

    _mod("hamilton").run(
        "hamilton_demosaic_1channel",
        bayer=bayer_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )

    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()

    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
@_block_recovery("hamilton_demosaic_half_res")
def hamilton_demosaic_half_res(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    if not return_gpu and dst is None:
        result = _demosaic_half_blockwise(
            "hamilton_demosaic_half_res",
            bayer,
            lambda tile: _hamilton_demosaic_half_res_full(
                tile,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
            ),
            _demosaic_params(
                (wb_r, wb_g1, wb_b, wb_g2),
                (black_level, white_level),
                (c00, c01, c10, c11),
            ),
        )
        if result is not None:
            return result
    return _hamilton_demosaic_half_res_full(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
    )


def _hamilton_demosaic_half_res_full(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Bypass Demosaicing: Extract Green Sub-Sampling to 1/2 size (half_res) grayscale (Fused Single-Pass)."""
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]

    if dst is not None and dst.shape == (h // 2, w // 2) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h // 2, w // 2), dtype=np.float32)

    _mod("hamilton").run(
        "hamilton_demosaic_half_res",
        bayer=bayer_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )

    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
@_block_recovery("hamilton_demosaic_rgb_half_res")
def hamilton_demosaic_rgb_half_res(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    if not return_gpu and dst is None:
        result = _demosaic_half_blockwise(
            "hamilton_demosaic_rgb_half_res",
            bayer,
            lambda tile: _hamilton_demosaic_rgb_half_res_full(
                tile,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                cmatrix,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
            ),
            _demosaic_params(
                (wb_r, wb_g1, wb_b, wb_g2),
                (black_level, white_level),
                (c00, c01, c10, c11),
                cmatrix,
            ),
            channels=3,
        )
        if result is not None:
            return result
    return _hamilton_demosaic_rgb_half_res_full(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
    )


def _hamilton_demosaic_rgb_half_res_full(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Bypass Demosaicing: Extract RGB Direct Sub-Sampling to 1/2 size (half_res) RGB (Fused Single-Pass)."""
    bayer_buf = InputArray(bayer)
    cmatrix_buf = InputArray(cmatrix)
    h, w = bayer_buf.shape[:2]

    if dst is not None and dst.shape == (h // 2, w // 2, 3) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h // 2, w // 2, 3), dtype=np.float32)

    _mod("hamilton").run(
        "hamilton_demosaic_rgb_half_res",
        bayer=bayer_buf,
        cmatrix=cmatrix_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )

    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
    if cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "release"):
        cmatrix_buf.release()
    elif cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "destroy"):
        cmatrix_buf.destroy()
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def hamilton_demosaic_3channel(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    if not return_gpu and dst is None:
        result = _demosaic_blockwise(
            "hamilton_demosaic_3channel",
            bayer,
            lambda tile: _hamilton_demosaic_3channel_full(
                tile,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                cmatrix,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
            ),
            _demosaic_params(
                (wb_r, wb_g1, wb_b, wb_g2),
                (black_level, white_level),
                (c00, c01, c10, c11),
                cmatrix,
            ),
            channels=1,
            halo=4,
        )
        if result is not None:
            return result
    return _hamilton_demosaic_3channel_full(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
    )


def _hamilton_demosaic_3channel_full(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Full-Luma Demosaic directly to Grayscale 1-channel."""
    bayer_buf = InputArray(bayer)
    cmatrix_buf = InputArray(cmatrix)
    h, w = bayer_buf.shape[:2]
    wb_bayer_buf = engine.allocate((h, w), dtype=np.float32)
    green_buf = engine.allocate((h, w), dtype=np.float32)

    if dst is not None and dst.shape == (h, w) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w), dtype=np.float32)

    _mod("hamilton").run(
        "hamilton_demosaic_3channel",
        bayer=bayer_buf,
        wb_bayer=wb_bayer_buf,
        green=green_buf,
        cmatrix=cmatrix_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )

    engine.sync()
    wb_bayer_buf.release()
    green_buf.release()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
    if cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "release"):
        cmatrix_buf.release()
    elif cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "destroy"):
        cmatrix_buf.destroy()

    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def arm(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    if not return_gpu and dst is None and _should_use_demosaic_blockwise("arm", bayer):
        params = {
            "wb": (float(wb_r), float(wb_g1), float(wb_b), float(wb_g2)),
            "levels": (float(black_level), float(white_level)),
            "cfa": (int(c00), int(c01), int(c10), int(c11)),
            "cmatrix": checksum(np.ascontiguousarray(cmatrix)),
        }
        result = _demosaic_blockwise(
            "arm_demosaic",
            bayer,
            lambda tile: _arm_demosaic_full(
                tile,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                cmatrix,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
            ),
            params,
        )
        if result is not None:
            return result
    return _arm_demosaic_full(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
    )


def arm_demosaic(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Backward-compatible name for :func:`arm`."""
    return arm(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
    )


def _arm_demosaic_full(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Taichi AOT ARM Demosaicing & sRGB / Gamma transform API"""
    with DemosaicBufferSet() as buffers:
        bayer_buf = buffers.input("bayer", bayer)
        cmatrix_buf = buffers.input("cmatrix", cmatrix)
        h, w = bayer_buf.shape[:2]
        scratch = {
            name: buffers.scratch(name, (h, w), dtype=np.float32)
            for name in (
                "wb_bayer", "green", "r_diff", "b_diff",
                "r_diff_filtered", "b_diff_filtered",
            )
        }
        host_dst = None
        if dst is None:
            dst_buf = buffers.output("dst", (h, w, 3), dtype=np.float32)
        elif isinstance(dst, TaichiGPUBuffer):
            if tuple(dst.shape) != (h, w, 3) or np.dtype(dst.dtype) != np.dtype(np.float32):
                raise ValueError(
                    f"ARM dst must have shape={(h, w, 3)} dtype=float32; "
                    f"got shape={dst.shape} dtype={dst.dtype}"
                )
            dst_buf = buffers.register("dst", dst)
        else:
            host_dst = np.asarray(dst)
            if host_dst.shape != (h, w, 3) or np.dtype(host_dst.dtype) != np.dtype(np.float32):
                raise ValueError(
                    f"ARM dst must have shape={(h, w, 3)} dtype=float32; "
                    f"got shape={host_dst.shape} dtype={host_dst.dtype}"
                )
            dst_buf = buffers.output("dst", (h, w, 3), dtype=np.float32)

        try:
            _mod("arm").run(
                resolve_graph_name("arm", "default"),
                bayer=bayer_buf,
                **scratch,
                cmatrix=cmatrix_buf,
                dst=dst_buf,
                wb_r=float(wb_r), wb_g1=float(wb_g1), wb_b=float(wb_b),
                wb_g2=float(wb_g2), black=float(black_level),
                white=float(white_level), h=int(h), w=int(w),
                c00=int(c00), c01=int(c01), c10=int(c10), c11=int(c11),
            )
            engine.sync()
            if return_gpu:
                return buffers.detach("dst")
            result = dst_buf.to_numpy()
            if host_dst is not None:
                np.copyto(host_dst, result)
                return host_dst
            return result
        except Exception as exc:
            raise RuntimeError(
                f"ARM AOT graph failed for shape={(h, w)} "
                f"backend={getattr(engine, 'arch', 'unknown')}"
            ) from exc


@ti_thread
def arm_demosaic_1channel(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    if not return_gpu and dst is None:
        result = _demosaic_blockwise(
            "arm_demosaic_1channel",
            bayer,
            lambda tile: _arm_demosaic_1channel_full(
                tile,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
            ),
            _demosaic_params(
                (wb_r, wb_g1, wb_b, wb_g2),
                (black_level, white_level),
                (c00, c01, c10, c11),
            ),
            channels=1,
            halo=4,
        )
        if result is not None:
            return result
    return _arm_demosaic_1channel_full(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
    )


def _arm_demosaic_1channel_full(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Fast Green-Only ARM Demosaic to Grayscale 1-channel."""
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]

    if dst is not None and dst.shape == (h, w) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w), dtype=np.float32)

    _mod("arm").run(
        "arm_demosaic_1channel",
        bayer=bayer_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )

    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()

    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
@_block_recovery("arm_demosaic_half_res")
def arm_demosaic_half_res(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    if not return_gpu and dst is None:
        result = _demosaic_half_blockwise(
            "arm_demosaic_half_res",
            bayer,
            lambda tile: _arm_demosaic_half_res_full(
                tile,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
            ),
            _demosaic_params(
                (wb_r, wb_g1, wb_b, wb_g2),
                (black_level, white_level),
                (c00, c01, c10, c11),
            ),
        )
        if result is not None:
            return result
    return _arm_demosaic_half_res_full(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
    )


def _arm_demosaic_half_res_full(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Bypass Demosaicing: Extract Green Sub-Sampling to 1/2 size (half_res) grayscale (ARM)."""
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]

    if dst is not None and dst.shape == (h // 2, w // 2) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h // 2, w // 2), dtype=np.float32)

    _mod("arm").run(
        "arm_demosaic_half_res",
        bayer=bayer_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )

    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
@_block_recovery("arm_demosaic_rgb_half_res")
def arm_demosaic_rgb_half_res(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    if not return_gpu and dst is None:
        result = _demosaic_half_blockwise(
            "arm_demosaic_rgb_half_res",
            bayer,
            lambda tile: _arm_demosaic_rgb_half_res_full(
                tile,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                cmatrix,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
            ),
            _demosaic_params(
                (wb_r, wb_g1, wb_b, wb_g2),
                (black_level, white_level),
                (c00, c01, c10, c11),
                cmatrix,
            ),
            channels=3,
        )
        if result is not None:
            return result
    return _arm_demosaic_rgb_half_res_full(
        bayer,
        wb_r,
        wb_g1,
        wb_b,
        wb_g2,
        cmatrix,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
    )


def _arm_demosaic_rgb_half_res_full(
    bayer,
    wb_r,
    wb_g1,
    wb_b,
    wb_g2,
    cmatrix,
    black_level,
    white_level,
    c00,
    c01,
    c10,
    c11,
    return_gpu=False,
    dst=None,
):
    """Bypass Demosaicing: Extract RGB Direct Sub-Sampling to 1/2 size (half_res) RGB (ARM)."""
    bayer_buf = InputArray(bayer)
    cmatrix_buf = InputArray(cmatrix)
    h, w = bayer_buf.shape[:2]

    if dst is not None and dst.shape == (h // 2, w // 2, 3) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h // 2, w // 2, 3), dtype=np.float32)

    _mod("arm").run(
        "arm_demosaic_rgb_half_res",
        bayer=bayer_buf,
        cmatrix=cmatrix_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )

    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()
    if cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "release"):
        cmatrix_buf.release()
    elif cmatrix_buf is not cmatrix and hasattr(cmatrix_buf, "destroy"):
        cmatrix_buf.destroy()
    return dst_buf if return_gpu else dst_buf.to_numpy()


@ti_thread
def pure_arm_demosaic(
    bayer, black_level, white_level, c00, c01, c10, c11, return_gpu=False, dst=None
):
    if not return_gpu and dst is None:
        result = _demosaic_blockwise(
            "pure_arm_demosaic",
            bayer,
            lambda tile: _pure_arm_demosaic_full(
                tile,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
            ),
            _demosaic_params((), (black_level, white_level), (c00, c01, c10, c11)),
            channels=3,
            halo=4,
        )
        if result is not None:
            return result
    return _pure_arm_demosaic_full(
        bayer,
        black_level,
        white_level,
        c00,
        c01,
        c10,
        c11,
        return_gpu=return_gpu,
        dst=dst,
    )


def _pure_arm_demosaic_full(
    bayer, black_level, white_level, c00, c01, c10, c11, return_gpu=False, dst=None
):
    """Taichi AOT Pure ARM Demosaicing (no color space or gamma)"""
    bayer_buf = InputArray(bayer)
    h, w = bayer_buf.shape[:2]

    if dst is not None and dst.shape == (h, w, 3) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w, 3), dtype=np.float32)

    _mod("arm").run(
        "pure_arm_demosaic",
        bayer=bayer_buf,
        dst=dst_buf,
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )

    engine.sync()
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        bayer_buf.release()
    elif bayer_buf is not bayer and hasattr(bayer_buf, "destroy"):
        bayer_buf.destroy()

    return dst_buf if return_gpu else dst_buf.to_numpy()


def rotate_by_flip(img: np.ndarray, flip: int) -> np.ndarray:
    """Rotates a numpy array according to the LibRaw/rawpy sizes.flip value."""
    if flip == 0:
        return img
    elif flip == 1:
        return np.fliplr(img)
    elif flip == 2:
        return np.rot90(img, 2)
    elif flip == 3:
        return np.rot90(img, 2)
    elif flip == 4:
        return np.fliplr(np.rot90(img, 1))
    elif flip == 5:
        return np.rot90(img, 1)
    elif flip == 6:
        return np.rot90(img, 3)
    elif flip == 7:
        return np.fliplr(np.rot90(img, 3))
    return img


def demosaic(
    raw_input,
    wb_r=None,
    wb_g1=None,
    wb_b=None,
    wb_g2=None,
    cmatrix=None,
    black_level=None,
    white_level=None,
    c00=None,
    c01=None,
    c10=None,
    c11=None,
    method="hamilton",
    return_gpu=False,
    dst=None,
    output_bgr_u16=False,
    preserve_headroom=False,
    half_res=False,
):
    """
    Unified, Ultra-Simplified GPU-Accelerated RAW Demosaicing API.

    This function acts as the single entry-point for all GPU-accelerated demosaicing algorithms.
    It automatically routes the raw sensor Bayer array to the appropriate pre-compiled AOT shader.

    Smart Metadata Auto-Extraction:
    -------------------------------
    To make integration extremely simple and prevent intimidating signatures, you can pass a
    `rawpy` object or a file path string directly as the first argument. All sensor metadata
    (Bayer array, WB gains, color matrix, black/white levels, layout indices) will be extracted
    automatically under the hood!

    Usage Examples:
    ---------------
    1. Pass rawpy object directly (Recommended):
       >>> rgb = ta_aot.demosaic(raw, method="hamilton")

    2. Pass DNG filepath directly:
       >>> rgb = ta_aot.demosaic("path/to/image.dng", method="hamilton")

    3. Pass parameters manually (For advanced JIT/AOT parity checks):
       >>> rgb = ta_aot.demosaic(bayer_np, wb_r, wb_g1, wb_b, wb_g2, cmatrix, ...)

    Supported Methods:
    -----------------
    1. 'hamilton' (or 'ha'):
       - Real Name: Hamilton-Adams Edge-Directed Demosaicing (equivalent to PPG / Patterned Pixel Grouping).
       - Features: High-speed edge-directed green interpolation, color difference gradient restoration,
                   and fused sRGB + Dynamic Algebraic Sigmoid contrast roll-off.

    Canonical method selectors are ``hamilton`` (or ``ha``), ``dcb``,
    ``bilinear``, ``arm``, and ``mlri-admm``.  Set ``half_res=True`` to use
    the RGB half-resolution graph for any of these families; do not encode
    resolution in the method name.

    Parameters:
    -----------
    raw_input : rawpy.RawPy, str, or np.ndarray
        Either a loaded rawpy object, a file path to a DNG/RAW image, or a raw Bayer NumPy array.
    """
    bayer = raw_input
    flip = 0

    # Check if raw_input is a filepath string or rawpy object
    is_rawpy_obj = hasattr(raw_input, "raw_image")
    is_filepath = isinstance(raw_input, str) and os.path.exists(raw_input)

    if is_rawpy_obj or is_filepath:
        import rawpy

        def _extract_from_raw(raw):
            # Keep the sensor mosaic compact through the upload boundary.
            # Hamilton has a u16-specialized graph that promotes samples to
            # f32 at the same arithmetic sites as the established f32 graph;
            # retaining u16 here avoids a temporary 48 MiB host expansion on
            # a 12 MP Bayer frame. Non-Hamilton variants convert at their
            # dispatch boundary when their TCM only exposes f32 input.
            raw_image = np.asarray(raw.raw_image)
            if raw_image.dtype in (np.dtype(np.uint8), np.dtype(np.uint16)):
                b_np = np.array(raw_image, copy=True)
            else:
                b_np = raw_image.astype(np.float32)
            bl = float(raw.black_level_per_channel[0])
            wl = float(raw.white_level)

            wb_np = np.array(raw.camera_whitebalance, dtype=np.float32)
            if len(wb_np) == 4:
                if wb_np[3] <= 0.01:
                    wb_np[3] = wb_np[1]
                g_gain = (wb_np[1] + wb_np[3]) / 2.0
                wb_np /= g_gain
            else:
                wb_np = np.array([1.5, 1.0, 2.0, 1.0], dtype=np.float32)

            c_00 = int(raw.raw_colors[0, 0])
            c_01 = int(raw.raw_colors[0, 1])
            c_10 = int(raw.raw_colors[1, 0])
            c_11 = int(raw.raw_colors[1, 1])
            cm = raw.color_matrix[:, :3].astype(np.float32)
            return (
                b_np,
                wb_np[0],
                wb_np[1],
                wb_np[2],
                wb_np[3],
                cm,
                bl,
                wl,
                c_00,
                c_01,
                c_10,
                c_11,
            )

        if is_rawpy_obj:
            flip = getattr(raw_input.sizes, "flip", 0)
            (
                bayer,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                cmatrix,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
            ) = _extract_from_raw(raw_input)
        else:
            with rawpy.imread(raw_input) as raw:
                flip = getattr(raw.sizes, "flip", 0)
                (
                    bayer,
                    wb_r,
                    wb_g1,
                    wb_b,
                    wb_g2,
                    cmatrix,
                    black_level,
                    white_level,
                    c00,
                    c01,
                    c10,
                    c11,
                ) = _extract_from_raw(raw)

        # Store active cmatrix in engine singleton for downstream gamma proxy color space alignment transformations
        engine.active_cmatrix = cmatrix
        engine.active_wb_r = wb_r
        engine.active_wb_g1 = wb_g1
        engine.active_wb_b = wb_b
        engine.active_wb_g2 = wb_g2
        engine.active_black_level = black_level
        engine.active_white_level = white_level
        engine.active_c00 = c00
        engine.active_c01 = c01
        engine.active_c10 = c10
        engine.active_c11 = c11

    # Canonical selectors only.  ``half_res`` is a universal resolution
    # switch; legacy ``*-half-res`` method spellings are not dispatch keys.
    method_lower = str(method).strip().lower()
    _legacy_method_aliases = {
        "hamilton-adams", "ppg", "hamilton-half-res", "hamilton-half",
        "ha-half-res", "ha-half", "half-res", "hamilton-rgb-half-res",
        "hamilton-rgb-half", "ha-rgb-half-res", "rgb-half-res",
        "mlri-half-res", "mlri-half", "mlri-rgb-half-res", "mlri-rgb-half",
        "dcb-demosaic", "dcb-half-res", "dcb-half", "dcb-rgb-half-res",
        "dcb-rgb-half", "arm-demosaic", "arm-half-res", "arm-half",
        "arm-rgb-half-res", "arm-rgb-half", "bilinear-rgb-half-res",
        "bilinear-rgb-half", "bi-rgb-half-res",
    }
    if method_lower in _legacy_method_aliases:
        raise ValueError(
            f"Unsupported demosaic method alias {method!r}; use a canonical "
            "method (hamilton, dcb, bilinear, arm, or mlri-admm) with "
            "half_res=True/False."
        )
    if half_res and output_bgr_u16:
        raise ValueError(
            "half_res=True is currently defined for the canonical RGB output; "
            "combine it with output_bgr_u16=False."
        )

    # The compact-input graph is currently specific to the full-resolution
    # Hamilton path. Keep the established f32 ABI for other families and
    # Hamilton half-resolution/auxiliary variants.
    if not (
        method_lower in ("hamilton", "ha")
        and not half_res
    ) and isinstance(bayer, np.ndarray) and bayer.dtype in (
        np.dtype(np.uint8),
        np.dtype(np.uint16),
    ):
        bayer = np.ascontiguousarray(bayer, dtype=np.float32)
    if method_lower in ("hamilton", "ha"):
        if half_res and not output_bgr_u16:
            res = hamilton_demosaic_rgb_half_res(
                bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
                black_level, white_level, c00, c01, c10, c11,
                return_gpu=return_gpu, dst=dst,
            )
            if not return_gpu and flip != 0:
                res = rotate_by_flip(res, flip)
            return res
        if output_bgr_u16:
            # The block planner must be consulted before requesting a live
            # full-frame GPU buffer.  The latter path is appropriate when the
            # graph fits, but on constrained OpenGL residency it can fail
            # before the existing tile executor gets a chance to run.
            if (
                not return_gpu
                and dst is None
                and _should_use_demosaic_blockwise("hamilton", bayer)
            ):
                params = _demosaic_params(
                    (wb_r, wb_g1, wb_b, wb_g2),
                    (black_level, white_level),
                    (c00, c01, c10, c11),
                    cmatrix,
                )
                tiled = _demosaic_blockwise_u16(
                    "hamilton_demosaic",
                    bayer,
                    lambda tile: _hamilton_demosaic_full(
                        tile,
                        wb_r,
                        wb_g1,
                        wb_b,
                        wb_g2,
                        cmatrix,
                        black_level,
                        white_level,
                        c00,
                        c01,
                        c10,
                        c11,
                        return_gpu=False,
                        tonemapping=False,
                    ),
                    params,
                )
                if tiled is not None:
                    if flip != 0:
                        tiled = rotate_by_flip(tiled, flip)
                    return tiled
            # Step 1: Run the demosaic JIT/AOT to produce float32 RGB on GPU
            rgb_f32_gpu = hamilton(
                bayer,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                cmatrix,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
                return_gpu=True,
                dst=None,
            )
            h, w = rgb_f32_gpu.shape[:2]

            # Step 2: Allocate host-accessible intermediate i32 BGR buffer in VRAM
            bgr_i32_gpu = engine.allocate(
                (h, w, 3), dtype=np.int32, host_accessible=True
            )

            # Step 3: Run the conversion/channel-swapping graph on GPU
            _mod("hamilton").run(
                "rgb_to_bgr_i32", src=rgb_f32_gpu, dst=bgr_i32_gpu, h=int(h), w=int(w)
            )

            # Step 4: Clean up GPU intermediate float32 buffer immediately
            engine.sync()
            rgb_f32_gpu.release()

            # Step 5: Convert and return
            if not return_gpu:
                engine.sync()
                bgr_u16_gpu = bgr_i32_gpu.cast(np.uint16, host_accessible=True)
                bgr_u16_cpu = bgr_u16_gpu.to_numpy()
                bgr_u16_gpu.release()
                bgr_i32_gpu.release()
                if flip != 0:
                    bgr_u16_cpu = rotate_by_flip(bgr_u16_cpu, flip)
                return bgr_u16_cpu
            else:
                engine.sync()
                bgr_u16_gpu = bgr_i32_gpu.cast(np.uint16, host_accessible=True)
                bgr_i32_gpu.release()
                return bgr_u16_gpu
        else:
            res = hamilton(
                bayer,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                cmatrix,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
                return_gpu=return_gpu,
                dst=dst,
            )
            if not return_gpu and flip != 0:
                res = rotate_by_flip(res, flip)
            return res
    elif method_lower in ("hamilton-1channel", "hamilton-1ch", "ha-1ch"):
        res = hamilton_demosaic_1channel(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in (
        "hamilton-half-res",
        "hamilton-half",
        "ha-half-res",
        "ha-half",
        "half-res",
    ):
        res = hamilton_demosaic_half_res(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in (
        "hamilton-rgb-half-res",
        "hamilton-rgb-half",
        "ha-rgb-half-res",
        "rgb-half-res",
    ):
        res = hamilton_demosaic_rgb_half_res(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("hamilton-3channel", "hamilton-3ch", "ha-3ch"):
        res = hamilton_demosaic_3channel(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower == "mlri-admm":
        if half_res:
            res = mlri_admm_demosaic_rgb_half_res(
                bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
                black_level, white_level, c00, c01, c10, c11,
                return_gpu=return_gpu, dst=dst,
            )
            if not return_gpu and flip != 0:
                res = rotate_by_flip(res, flip)
            return res
        res = mlri_admm(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower == "bilinear":
        res = bilinear(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
            half_res=half_res,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in (
        "bilinear-rgb-half-res",
        "bilinear-rgb-half",
        "bi-rgb-half-res",
    ):
        res = bilinear(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
            half_res=True,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("mlri-1channel", "mlri-1ch", "mlri_admm_demosaic_1channel"):
        res = mlri_admm_demosaic_1channel(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("mlri-half-res", "mlri-half", "mlri_admm_demosaic_half_res"):
        res = mlri_admm_demosaic_half_res(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in (
        "mlri-rgb-half-res",
        "mlri-rgb-half",
        "mlri_admm_demosaic_rgb_half_res",
    ):
        res = mlri_admm_demosaic_rgb_half_res(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("mlri-3channel", "mlri-3ch", "mlri_admm_demosaic_3channel"):
        res = mlri_admm_demosaic_3channel(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower == "dcb":
        if half_res:
            res = dcb_demosaic_rgb_half_res(
                bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
                black_level, white_level, c00, c01, c10, c11,
                return_gpu=return_gpu, dst=dst,
            )
            if not return_gpu and flip != 0:
                res = rotate_by_flip(res, flip)
            return res
        res = dcb(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
            preserve_headroom=preserve_headroom,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("dcb-1channel", "dcb-1ch"):
        res = dcb_demosaic_1channel(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("dcb-half-res", "dcb-half"):
        res = dcb_demosaic_half_res(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("dcb-rgb-half-res", "dcb-rgb-half"):
        res = dcb_demosaic_rgb_half_res(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("dcb-3channel", "dcb-3ch"):
        res = dcb_demosaic_3channel(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower == "arm":
        if half_res and not output_bgr_u16:
            res = arm_demosaic_rgb_half_res(
                bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
                black_level, white_level, c00, c01, c10, c11,
                return_gpu=return_gpu, dst=dst,
            )
            if not return_gpu and flip != 0:
                res = rotate_by_flip(res, flip)
            return res
        if output_bgr_u16:
            rgb_f32_gpu = arm(
                bayer,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                cmatrix,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
                return_gpu=True,
                dst=None,
            )
            h, w = rgb_f32_gpu.shape[:2]
            bgr_i32_gpu = engine.allocate(
                (h, w, 3), dtype=np.int32, host_accessible=True
            )
            _mod("arm").run(
                "rgb_to_bgr_i32", src=rgb_f32_gpu, dst=bgr_i32_gpu, h=int(h), w=int(w)
            )
            engine.sync()
            rgb_f32_gpu.release()
            if not return_gpu:
                engine.sync()
                bgr_u16_gpu = bgr_i32_gpu.cast(np.uint16, host_accessible=True)
                bgr_u16_cpu = bgr_u16_gpu.to_numpy()
                bgr_u16_gpu.release()
                bgr_i32_gpu.release()
                if flip != 0:
                    bgr_u16_cpu = rotate_by_flip(bgr_u16_cpu, flip)
                return bgr_u16_cpu
            else:
                engine.sync()
                bgr_u16_gpu = bgr_i32_gpu.cast(np.uint16, host_accessible=True)
                bgr_i32_gpu.release()
                return bgr_u16_gpu
        else:
            res = arm(
                bayer,
                wb_r,
                wb_g1,
                wb_b,
                wb_g2,
                cmatrix,
                black_level,
                white_level,
                c00,
                c01,
                c10,
                c11,
                return_gpu=return_gpu,
                dst=dst,
            )
            if not return_gpu and flip != 0:
                res = rotate_by_flip(res, flip)
            return res
    elif method_lower in ("arm-1channel", "arm-1ch", "arm_demosaic_1channel"):
        res = arm_demosaic_1channel(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("arm-half-res", "arm-half", "arm_demosaic_half_res"):
        res = arm_demosaic_half_res(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in (
        "arm-rgb-half-res",
        "arm-rgb-half",
        "arm_demosaic_rgb_half_res",
    ):
        res = arm_demosaic_rgb_half_res(
            bayer,
            wb_r,
            wb_g1,
            wb_b,
            wb_g2,
            cmatrix,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    elif method_lower in ("pure-arm", "pure-arm-demosaic", "pure_arm_demosaic"):
        res = pure_arm_demosaic(
            bayer,
            black_level,
            white_level,
            c00,
            c01,
            c10,
            c11,
            return_gpu=return_gpu,
            dst=dst,
        )
        if not return_gpu and flip != 0:
            res = rotate_by_flip(res, flip)
        return res
    else:
        supported = [
            "'hamilton' (aliases: 'hamilton-adams', 'ha', 'ppg')",
            "'hamilton-1channel' (aliases: 'hamilton-1ch', 'ha-1ch')",
            "'hamilton-half-res' (aliases: 'hamilton-half', 'ha-half-res', 'half-res')",
            "'hamilton-rgb-half-res' (aliases: 'hamilton-rgb-half', 'ha-rgb-half-res', 'rgb-half-res')",
            "'hamilton-3channel' (aliases: 'hamilton-3ch', 'ha-3ch')",
            "'arm' (aliases: 'arm-demosaic', 'arm_demosaic')",
            "'arm-1channel' (aliases: 'arm-1ch')",
            "'arm-half-res' (aliases: 'arm-half')",
            "'arm-rgb-half-res' (aliases: 'arm-rgb-half')",
            "'pure-arm'",
            "'mlri' (aliases: 'mlri-admm', 'mlri-admm-demosaic')",
            "'mlri-1channel' (aliases: 'mlri-1ch')",
            "'mlri-half-res' (aliases: 'mlri-half')",
            "'mlri-rgb-half-res' (aliases: 'mlri-rgb-half')",
            "'mlri-3channel' (aliases: 'mlri-3ch')",
        ]
        raise ValueError(
            f"\n[Taichi AOT] Unsupported demosaicing method: '{method}'.\n"
            f"  SUPPORTED METHODS: {', '.join(supported)}"
        )


def generate_brief_pattern(num_pairs=256, patch_size=31, seed=42):
    """Generate BRIEF descriptor pattern coordinates."""
    np.random.seed(seed)
    sigma = patch_size / 5.0
    x1 = np.random.normal(0, sigma, num_pairs)
    y1 = np.random.normal(0, sigma, num_pairs)
    x2 = np.random.normal(0, sigma, num_pairs)
    y2 = np.random.normal(0, sigma, num_pairs)

    radius = patch_size // 2
    x1 = np.clip(np.round(x1), -radius, radius)
    y1 = np.clip(np.round(y1), -radius, radius)
    x2 = np.clip(np.round(x2), -radius, radius)
    y2 = np.clip(np.round(y2), -radius, radius)

    pattern = np.stack([x1, y1, x2, y2], axis=1).astype(np.float32)
    return pattern


def ofb(
    src1,
    src2,
    ratio_threshold=0.8,
    grid_size=32,
    threshold=0.015,
    margin=15,
    max_keypoints=1500,
):
    """
    Scale-Invariant Multi-Scale O-FAST-BRIEF Feature Matching on GPU.
    Automatically handles super low resolution images (< 240px) using adaptive parameters.

    Args:
        src1, src2: Grayscale input images (np.ndarray or TaichiGPUBuffer) [H, W] normalized to [0, 1].
        ratio_threshold: Lowe's ratio test threshold (default 0.8).
        grid_size: ANMS grid size (default 32).
        threshold: FAST score threshold (default 0.015).
        margin: Sensor margin to avoid border keypoints (default 15).
        max_keypoints: Maximum number of keypoints to extract (default 1500).

    Returns:
        pts1: Matched points from src1 (N, 2) in (x, y) coordinates.
        pts2: Matched points from src2 (N, 2) in (x, y) coordinates.
        scores: Matching scores / Hamming distances (N,).
    """
    img1_gpu = upload(src1) if not isinstance(src1, TaichiGPUBuffer) else src1
    img2_gpu = upload(src2) if not isinstance(src2, TaichiGPUBuffer) else src2

    h_orig, w_orig = img1_gpu.shape[:2]
    min_dim = min(h_orig, w_orig)

    # 1. Determine number of scale pyramid levels dynamically
    if min_dim < 240:
        num_levels = 1
    elif min_dim < 512:
        num_levels = 2
    else:
        num_levels = 3

    pattern_np = generate_brief_pattern(num_pairs=256, patch_size=31, seed=42)
    pattern_gpu = engine.upload(pattern_np)

    kps1_list = []
    kps2_list = []
    desc1_list = []

    for level in range(num_levels):
        if level > 0:
            dh, dw = h_orig // (2**level), w_orig // (2**level)
            curr1 = resize(
                img1_gpu, (dw, dh), interpolation=INTER_AREA, return_gpu=True
            )
            curr2 = resize(
                img2_gpu, (dw, dh), interpolation=INTER_AREA, return_gpu=True
            )
        else:
            curr1 = img1_gpu
            curr2 = img2_gpu

        h_l, w_l = curr1.shape[:2]

        # Adaptive parameters for this scale level
        grid_size_l = max(8, grid_size // (2**level))
        margin_l = max(4, margin // (2**level))
        threshold_l = threshold * (0.8**level)

        # Apply Median Filter to remove hot pixels
        img1_med = median_filter(curr1, return_gpu=True)
        img2_med = median_filter(curr2, return_gpu=True)

        # Apply Gaussian Blur to smooth noise for BRIEF descriptor
        img1_blur = gaussian_blur(curr1, sigma=2.0, return_gpu=True)
        img2_blur = gaussian_blur(curr2, sigma=2.0, return_gpu=True)

        # Allocate keypoint and descriptor buffers for this scale
        max_kps_l = max(100, max_keypoints // (2**level))

        kps1_gpu = engine.allocate((max_kps_l, 2), dtype=np.float32)
        kps2_gpu = engine.allocate((max_kps_l, 2), dtype=np.float32)

        score_map1 = engine.allocate((h_l, w_l), dtype=np.float32)
        score_map2 = engine.allocate((h_l, w_l), dtype=np.float32)

        counter1 = upload(np.zeros(1, dtype=np.int32))
        counter2 = upload(np.zeros(1, dtype=np.int32))

        # Detect keypoints
        _mod("ofb").run(
            "detect_keypoints",
            src=img1_med,
            score_map=score_map1,
            keypoints=kps1_gpu,
            counter=counter1,
            h=h_l,
            w=w_l,
            grid_size=grid_size_l,
            margin=margin_l,
            threshold=threshold_l,
        )
        _mod("ofb").run(
            "detect_keypoints",
            src=img2_med,
            score_map=score_map2,
            keypoints=kps2_gpu,
            counter=counter2,
            h=h_l,
            w=w_l,
            grid_size=grid_size_l,
            margin=margin_l,
            threshold=threshold_l,
        )

        desc1_gpu = engine.allocate((max_kps_l, 8), dtype=np.int32)
        desc2_gpu = engine.allocate((max_kps_l, 8), dtype=np.int32)
        matches_gpu = engine.allocate((max_kps_l, 2), dtype=np.int32)

        # Compute descriptors on GPU (fully async)
        _mod("ofb").run(
            "compute_descriptors",
            src=img1_blur,
            kps=kps1_gpu,
            pattern=pattern_gpu,
            desc=desc1_gpu,
            counter=counter1,
            h=h_l,
            w=w_l,
        )
        _mod("ofb").run(
            "compute_descriptors",
            src=img2_blur,
            kps=kps2_gpu,
            pattern=pattern_gpu,
            desc=desc2_gpu,
            counter=counter2,
            h=h_l,
            w=w_l,
        )

        # Match descriptors on GPU (fully async)
        _mod("ofb").run(
            "match_descriptors",
            desc1=desc1_gpu,
            desc2=desc2_gpu,
            matches=matches_gpu,
            counter1=counter1,
            counter2=counter2,
            ratio_threshold=ratio_threshold,
        )

        results_gpu = engine.allocate((max_kps_l, 6), dtype=np.float32)

        # Pack matches on GPU (fully async)
        _mod("ofb").run(
            "pack_matches",
            kps1=kps1_gpu,
            kps2=kps2_gpu,
            matches=matches_gpu,
            counter1=counter1,
            counter2=counter2,
            results=results_gpu,
        )

        # Download results (causes exactly one sync step per level)
        results_np = results_gpu.to_numpy()

        valid_mask = results_np[:, 5] == 1.0
        if np.any(valid_mask):
            pts1_level = results_np[valid_mask, 0:2]
            pts2_level = results_np[valid_mask, 2:4]
            dists_level = results_np[valid_mask, 4]

            scale_factor = float(2**level)
            for idx in range(len(pts1_level)):
                kps1_list.append(
                    [
                        pts1_level[idx, 0] * scale_factor,
                        pts1_level[idx, 1] * scale_factor,
                    ]
                )
                kps2_list.append(
                    [
                        pts2_level[idx, 0] * scale_factor,
                        pts2_level[idx, 1] * scale_factor,
                    ]
                )
                desc1_list.append(dists_level[idx])

        # Clean up this scale's temporary buffers
        results_gpu.release()
        desc1_gpu.release()
        desc2_gpu.release()
        matches_gpu.release()
        score_map1.release()
        score_map2.release()
        kps1_gpu.release()
        kps2_gpu.release()
        counter1.release()
        counter2.release()
        img1_med.release()
        img2_med.release()
        img1_blur.release()
        img2_blur.release()

        # Release downsampled images if allocated
        if level > 0:
            curr1.release()
            curr2.release()

    pattern_gpu.release()

    if len(kps1_list) == 0:
        return None, None, None

    return (
        np.array(kps1_list, dtype=np.float32),
        np.array(kps2_list, dtype=np.float32),
        np.array(desc1_list, dtype=np.float32),
    )


def get_fed_step_sizes(n=8):
    """Generate cycle of step sizes for Fast Explicit Diffusion (FED)."""
    tau_max = 0.25
    steps = []
    for j in range(n):
        tau = tau_max / (np.cos((2 * j + 1) * np.pi / (4 * n + 2)) ** 2)
        steps.append(float(tau))
    return steps


def akaze(
    src1,
    src2,
    ratio_threshold=0.8,
    grid_size=32,
    threshold=0.008,
    margin=15,
    max_keypoints=1500,
    k_contrast=0.02,
    num_fed_steps=8,
):
    """
    Scale-Invariant Multi-Scale A-KAZE (Accelerated KAZE) Feature Matching on GPU.
    Uses Non-Linear Scale Space via FED (Fast Explicit Diffusion) for superior keypoint quality
    under extreme noise, low contrast, and medical/microscopic images.

    Args:
        src1, src2: Grayscale input images (np.ndarray or TaichiGPUBuffer) [H, W] normalized to [0, 1].
        ratio_threshold: Lowe's ratio test threshold (default 0.8).
        grid_size: ANMS grid size (default 32).
        threshold: Hessian determinant score threshold (default 0.008).
        margin: Sensor margin to avoid border keypoints (default 15).
        max_keypoints: Maximum number of keypoints to extract (default 1500).
        k_contrast: Contrast threshold for non-linear conductivity (default 0.02).
        num_fed_steps: Number of FED steps per pyramid level (default 8).

    Returns:
        pts1: Matched points from src1 (N, 2) in (x, y) coordinates.
        pts2: Matched points from src2 (N, 2) in (x, y) coordinates.
        scores: Matching scores / Hamming distances (N,).
    """
    img1_gpu = upload(src1) if not isinstance(src1, TaichiGPUBuffer) else src1
    img2_gpu = upload(src2) if not isinstance(src2, TaichiGPUBuffer) else src2

    h_orig, w_orig = img1_gpu.shape[:2]
    min_dim = min(h_orig, w_orig)

    # Determine scale levels dynamically
    if min_dim < 240:
        num_levels = 1
    elif min_dim < 512:
        num_levels = 2
    else:
        num_levels = 3

    pattern_np = generate_brief_pattern(num_pairs=256, patch_size=31, seed=42)
    pattern_gpu = engine.upload(pattern_np)

    kps1_list = []
    kps2_list = []
    desc1_list = []

    fed_taus = get_fed_step_sizes(num_fed_steps)

    for level in range(num_levels):
        if level > 0:
            dh, dw = h_orig // (2**level), w_orig // (2**level)
            curr1 = resize(
                img1_gpu, (dw, dh), interpolation=INTER_AREA, return_gpu=True
            )
            curr2 = resize(
                img2_gpu, (dw, dh), interpolation=INTER_AREA, return_gpu=True
            )
        else:
            # We must copy to avoid modifying original inputs during diffusion
            curr1 = engine.allocate((h_orig, w_orig), dtype=np.float32)
            curr2 = engine.allocate((h_orig, w_orig), dtype=np.float32)
            copy_field(img1_gpu, curr1)
            copy_field(img2_gpu, curr2)

        h_l, w_l = curr1.shape[:2]

        # Allocate temporary buffers for Non-Linear Scale Space Diffusion
        temp1 = engine.allocate((h_l, w_l), dtype=np.float32)
        temp2 = engine.allocate((h_l, w_l), dtype=np.float32)
        cond1 = engine.allocate((h_l, w_l), dtype=np.float32)
        cond2 = engine.allocate((h_l, w_l), dtype=np.float32)

        # 1. Compute conductivity map at this scale level
        _mod("akaze").run(
            "compute_conductivity_map",
            src=curr1,
            conductivity=cond1,
            h=h_l,
            w=w_l,
            k=float(k_contrast),
        )
        _mod("akaze").run(
            "compute_conductivity_map",
            src=curr2,
            conductivity=cond2,
            h=h_l,
            w=w_l,
            k=float(k_contrast),
        )

        # 2. Run FED explicit diffusion iterations on GPU
        for tau in fed_taus:
            # Step on image 1
            _mod("akaze").run(
                "fed_diffusion_step",
                src=curr1,
                dst=temp1,
                conductivity=cond1,
                h=h_l,
                w=w_l,
                tau=tau,
            )
            curr1, temp1 = temp1, curr1  # zero-cost swap

            # Step on image 2
            _mod("akaze").run(
                "fed_diffusion_step",
                src=curr2,
                dst=temp2,
                conductivity=cond2,
                h=h_l,
                w=w_l,
                tau=tau,
            )
            curr2, temp2 = temp2, curr2  # zero-cost swap

        # 3. Compute Hessian Determinant Map
        score_map1 = engine.allocate((h_l, w_l), dtype=np.float32)
        score_map2 = engine.allocate((h_l, w_l), dtype=np.float32)

        _mod("akaze").run(
            "compute_hessian_determinant",
            src=curr1,
            hessian_map=score_map1,
            h=h_l,
            w=w_l,
        )
        _mod("akaze").run(
            "compute_hessian_determinant",
            src=curr2,
            hessian_map=score_map2,
            h=h_l,
            w=w_l,
        )

        # Adaptive parameters for this scale level
        grid_size_l = max(8, grid_size // (2**level))
        margin_l = max(4, margin // (2**level))
        threshold_l = threshold * (0.8**level)

        max_kps_l = max(100, max_keypoints // (2**level))

        kps1_gpu = engine.allocate((max_kps_l, 2), dtype=np.float32)
        kps2_gpu = engine.allocate((max_kps_l, 2), dtype=np.float32)

        counter1 = upload(np.zeros(1, dtype=np.int32))
        counter2 = upload(np.zeros(1, dtype=np.int32))

        # Detect keypoints (ANMS)
        _mod("akaze").run(
            "detect_keypoints",
            hessian_map=score_map1,
            keypoints=kps1_gpu,
            counter=counter1,
            h=h_l,
            w=w_l,
            grid_size=grid_size_l,
            threshold=threshold_l,
        )
        _mod("akaze").run(
            "detect_keypoints",
            hessian_map=score_map2,
            keypoints=kps2_gpu,
            counter=counter2,
            h=h_l,
            w=w_l,
            grid_size=grid_size_l,
            threshold=threshold_l,
        )

        desc1_gpu = engine.allocate((max_kps_l, 16), dtype=np.int32)
        desc2_gpu = engine.allocate((max_kps_l, 16), dtype=np.int32)
        matches_gpu = engine.allocate((max_kps_l, 2), dtype=np.int32)

        # Compute descriptors on GPU (fully async)
        _mod("akaze").run(
            "compute_descriptors",
            src=curr1,
            kps=kps1_gpu,
            pattern=pattern_gpu,
            desc=desc1_gpu,
            counter=counter1,
            h=h_l,
            w=w_l,
        )
        _mod("akaze").run(
            "compute_descriptors",
            src=curr2,
            kps=kps2_gpu,
            pattern=pattern_gpu,
            desc=desc2_gpu,
            counter=counter2,
            h=h_l,
            w=w_l,
        )

        # Match descriptors on GPU (fully async)
        _mod("akaze").run(
            "match_descriptors",
            desc1=desc1_gpu,
            desc2=desc2_gpu,
            matches=matches_gpu,
            counter1=counter1,
            counter2=counter2,
            ratio_threshold=ratio_threshold,
        )

        results_gpu = engine.allocate((max_kps_l, 6), dtype=np.float32)

        # Pack matches on GPU (fully async)
        _mod("akaze").run(
            "pack_matches",
            kps1=kps1_gpu,
            kps2=kps2_gpu,
            matches=matches_gpu,
            counter1=counter1,
            counter2=counter2,
            results=results_gpu,
        )

        # Download results (causes exactly one sync step per level)
        results_np = results_gpu.to_numpy()

        valid_mask = results_np[:, 5] == 1.0
        if np.any(valid_mask):
            pts1_level = results_np[valid_mask, 0:2]
            pts2_level = results_np[valid_mask, 2:4]
            dists_level = results_np[valid_mask, 4]

            scale_factor = float(2**level)
            for idx in range(len(pts1_level)):
                kps1_list.append(
                    [
                        pts1_level[idx, 0] * scale_factor,
                        pts1_level[idx, 1] * scale_factor,
                    ]
                )
                kps2_list.append(
                    [
                        pts2_level[idx, 0] * scale_factor,
                        pts2_level[idx, 1] * scale_factor,
                    ]
                )
                desc1_list.append(dists_level[idx])

        # Clean up temporary buffers
        results_gpu.release()
        desc1_gpu.release()
        desc2_gpu.release()
        matches_gpu.release()
        score_map1.release()
        score_map2.release()
        kps1_gpu.release()
        kps2_gpu.release()
        counter1.release()
        counter2.release()

        temp1.release()
        temp2.release()
        cond1.release()
        cond2.release()
        curr1.release()
        curr2.release()

    pattern_gpu.release()

    if len(kps1_list) == 0:
        return None, None, None

    return (
        np.array(kps1_list, dtype=np.float32),
        np.array(kps2_list, dtype=np.float32),
        np.array(desc1_list, dtype=np.float32),
    )


def find_homography(
    pts1,
    pts2,
    method: str = "MAGSAC++",
    ransacReprojThreshold: float = 3.0,
    n_hypotheses: int = 1024,
    max_iters: int = 1,
    return_gpu: bool = False,
) -> tuple:
    """
    Estimasi matriks Homografi 3x3 menggunakan GPU RANSAC / MAGSAC++.
    API menyerupai implementasi homography standar (RANSAC).

    Args:
        pts1  (np.ndarray | TaichiGPUBuffer): Array titik sumber, shape (N, 2) float32 [x, y].
        pts2  (np.ndarray | TaichiGPUBuffer): Array titik tujuan, shape (N, 2) float32 [x, y].
        method (str)      : 'RANSAC' atau 'MAGSAC++' (default MAGSAC++).
        ransacReprojThreshold (float): Jarak re-proyeksi maksimum inlier (piksel).
        n_hypotheses (int): Jumlah iterasi RANSAC paralel di GPU (default 1024).
        max_iters (int)   : Jumlah putaran pencarian ulang untuk memperbaiki akurasi.
        return_gpu (bool) : Jika True, mengembalikan mask dalam TaichiGPUBuffer (zero-copy VRAM).

    Returns:
        H    (np.ndarray | None): Matriks Homografi 3x3 float64, atau None jika gagal.
        mask (np.ndarray | TaichiGPUBuffer | None): Mask biner inlier shape (N, 1) uint8 atau TaichiGPUBuffer.
    """
    if pts1 is None or pts2 is None:
        return None, None

    # Deteksi input dari GPU Buffer atau NumPy
    is_pts1_gpu = isinstance(pts1, TaichiGPUBuffer)
    is_pts2_gpu = isinstance(pts2, TaichiGPUBuffer)

    n_pts = pts1.shape[0]
    if n_pts < 4:
        return None, None

    # Handle Upload ke GPU jika input berupa numpy array
    pts1_gpu = (
        pts1
        if is_pts1_gpu
        else upload(np.ascontiguousarray(pts1.reshape(-1, 2), dtype=np.float32))
    )
    pts2_gpu = (
        pts2
        if is_pts2_gpu
        else upload(np.ascontiguousarray(pts2.reshape(-1, 2), dtype=np.float32))
    )

    H_cand_gpu = engine.allocate((n_hypotheses, 9), dtype=np.float32)
    inlier_cnt_gpu = engine.allocate((n_hypotheses,), dtype=np.int32)

    best_H_flat = None
    best_inliers = -1

    import time

    seed_base = int(time.time() * 1000) & 0x7FFFFFFF

    for iteration in range(max_iters):
        seed_offset = (seed_base + iteration * 31337) & 0x7FFFFFFF

        # Jalankan 1024 hipotesis RANSAC secara paralel di GPU (dari modul ransac)
        _mod("ransac").run(
            "ransac_homography",
            pts1=pts1_gpu,
            pts2=pts2_gpu,
            n_pts=n_pts,
            n_hypotheses=n_hypotheses,
            reproj_threshold=float(ransacReprojThreshold),
            H_candidates=H_cand_gpu,
            inlier_counts=inlier_cnt_gpu,
            seed_offset=seed_offset,
        )

        # Download hanya vektor inlier count kecil (1024 int) — sangat cepat
        inlier_counts_np = inlier_cnt_gpu.to_numpy()
        best_idx = int(np.argmax(inlier_counts_np))
        best_count = int(inlier_counts_np[best_idx])

        if best_count > best_inliers:
            best_inliers = best_count
            H_cand_np = H_cand_gpu.to_numpy()
            best_H_flat = H_cand_np[best_idx]  # 9-element flat

    H_cand_gpu.release()
    inlier_cnt_gpu.release()

    if best_H_flat is None:
        if not is_pts1_gpu:
            pts1_gpu.release()
        if not is_pts2_gpu:
            pts2_gpu.release()
        return None, None

    # Hasilkan mask inlier pada GPU menggunakan matriks RANSAC terbaik
    H_flat_gpu = upload(best_H_flat)
    mask_gpu = engine.allocate((n_pts,), dtype=np.int32)

    _mod("ransac").run(
        "generate_inlier_mask",
        pts1=pts1_gpu,
        pts2=pts2_gpu,
        H_best=H_flat_gpu,
        n_pts=n_pts,
        reproj_threshold=float(ransacReprojThreshold),
        mask_out=mask_gpu,
    )

    # ── Least-Squares refinement (Weighted Least Squares) ───────────
    ATA_gpu = engine.allocate((8, 8), dtype=np.float32)
    ATb_gpu = engine.allocate((8,), dtype=np.float32)

    _mod("ransac").run(
        "refine_homography",
        pts1=pts1_gpu,
        pts2=pts2_gpu,
        mask=mask_gpu,
        n_pts=n_pts,
        reproj_threshold=float(ransacReprojThreshold),
        ATA_out=ATA_gpu,
        ATb_out=ATb_gpu,
    )

    ATA_np = ATA_gpu.to_numpy().astype(np.float64)
    ATb_np = ATb_gpu.to_numpy().astype(np.float64)

    ATA_gpu.release()
    ATb_gpu.release()

    H = best_H_flat.reshape(3, 3).astype(np.float64)

    # Selesaikan ATA*h = ATb di CPU
    try:
        h_refined = np.linalg.solve(ATA_np, ATb_np)
        H_refined = np.array(
            [
                [h_refined[0], h_refined[1], h_refined[2]],
                [h_refined[3], h_refined[4], h_refined[5]],
                [h_refined[6], h_refined[7], 1.0],
            ],
            dtype=np.float64,
        )
        H = H_refined
    except np.linalg.LinAlgError:
        pass  # Gunakan H dari RANSAC jika LS singular

    # Re-generate mask final menggunakan H yang sudah di-refine
    H_flat_refined = H.ravel().astype(np.float32)
    H_flat_gpu2 = upload(H_flat_refined)
    mask_gpu2 = engine.allocate((n_pts,), dtype=np.int32)

    _mod("ransac").run(
        "generate_inlier_mask",
        pts1=pts1_gpu,
        pts2=pts2_gpu,
        H_best=H_flat_gpu2,
        n_pts=n_pts,
        reproj_threshold=float(ransacReprojThreshold),
        mask_out=mask_gpu2,
    )

    # Bersihkan input GPU Buffer jika kita yang mengalokasikannya secara lokal
    if not is_pts1_gpu:
        pts1_gpu.release()
    if not is_pts2_gpu:
        pts2_gpu.release()
    H_flat_gpu.release()
    mask_gpu.release()
    H_flat_gpu2.release()

    if return_gpu:
        return H, mask_gpu2
    else:
        mask_np = mask_gpu2.to_numpy().astype(np.uint8).reshape(-1, 1)
        mask_gpu2.release()
        return H, mask_np


@_block_recovery("warp_perspective")
def warp_perspective(src, M, dsize, return_gpu=False, dst=None):
    """
    GPU-accelerated Warp Perspective menggunakan Taichi AOT.
    API menyerupai warp perspective standar.
    """
    if isinstance(src, np.ndarray) and dst is None:
        source = np.ascontiguousarray(src, dtype=np.float32)
        w_dst, h_dst = dsize
        output_nbytes = (
            h_dst
            * w_dst
            * (source.shape[2] if source.ndim == 3 else 1)
            * np.dtype(np.float32).itemsize
        )
        grid = engine.plan_blocks(
            "warp_perspective", (h_dst, w_dst), source.nbytes + output_nbytes
        )
        if grid is not None:
            try:
                inverse = np.linalg.inv(np.asarray(M, dtype=np.float32)).astype(
                    np.float32
                )
            except np.linalg.LinAlgError:
                inverse = np.eye(3, dtype=np.float32)
            src_buf, matrix_buf = upload(source), upload(inverse)
            output_shape = (
                (h_dst, w_dst, source.shape[2]) if source.ndim == 3 else (h_dst, w_dst)
            )
            result = np.empty(output_shape, dtype=np.float32)
            graph = (
                "warp_perspective_offset_f32_3d"
                if source.ndim == 3
                else "warp_perspective_offset_f32_2d"
            )
            src_view = src_buf.view_as_vector(True, 3) if source.ndim == 3 else src_buf
            source_crc = checksum(source)
            cache_params = {"dsize": dsize, "matrix": tuple(inverse.ravel())}
            try:
                for block in _ordered_cached_output_blocks(
                    "warp_perspective", grid, source_crc, cache_params
                ):
                    tile_shape = (
                        (*block.shape, source.shape[2])
                        if source.ndim == 3
                        else block.shape
                    )
                    cached = _get_cached_output_tile(
                        "warp_perspective", block, source_crc, cache_params, tile_shape
                    )
                    if cached is not None:
                        result[block.write_slice] = cached
                        continue
                    tile_buf = engine.allocate(
                        tile_shape, dtype=np.float32, is_vector=source.ndim == 3
                    )
                    tile_view = (
                        tile_buf.view_as_vector(True, 3)
                        if source.ndim == 3
                        else tile_buf
                    )
                    try:
                        _mod("remap").run(
                            graph,
                            src=src_view,
                            M_inv=matrix_buf,
                            dst=tile_view,
                            h_src=source.shape[0],
                            w_src=source.shape[1],
                            offset_y=block.y0,
                            offset_x=block.x0,
                        )
                        tile_result = tile_buf.to_numpy()
                        result[block.write_slice] = tile_result
                        _put_cached_output_tile(
                            "warp_perspective",
                            block,
                            source_crc,
                            cache_params,
                            tile_result,
                        )
                    finally:
                        tile_buf.destroy()
            finally:
                src_buf.destroy()
                matrix_buf.destroy()
            return upload(result) if return_gpu else result

    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else upload(src)

    h_src, w_src = src_buf.shape[:2]
    w_dst, h_dst = dsize

    # Hitung inverse matriks di CPU menggunakan NumPy
    M_np = np.asarray(M, dtype=np.float32)
    try:
        M_inv = np.linalg.inv(M_np)
    except np.linalg.LinAlgError:
        M_inv = np.eye(3, dtype=np.float32)

    M_inv_gpu = upload(M_inv)

    is_vec = getattr(src_buf, "is_vector", False)
    is_3d = len(src_buf.shape) == 3 or is_vec
    v_dim = (
        src_buf.vector_dim
        if is_vec
        else (src_buf.shape[2] if len(src_buf.shape) == 3 else 1)
    )

    if dst is None:
        if is_3d:
            dst_buf = OutputArray(
                (h_dst, w_dst, v_dim),
                dtype=src_buf.dtype,
                is_vector=is_vec,
                vector_dim=v_dim,
            )
        else:
            dst_buf = OutputArray((h_dst, w_dst), dtype=src_buf.dtype)
    else:
        dst_buf = dst

    src_v = src_buf
    dst_v = dst_buf
    if is_3d:
        if not getattr(src_buf, "is_vector", False):
            src_v = src_buf.view_as_vector(True)
        if not getattr(dst_buf, "is_vector", False):
            dst_v = dst_buf.view_as_vector(True)

    graph = (
        "warp_perspective_offset_f32_3d" if is_3d else "warp_perspective_offset_f32_2d"
    )

    _mod("remap").run(
        graph,
        src=src_v,
        M_inv=M_inv_gpu,
        dst=dst_v,
        h_src=h_src,
        w_src=w_src,
        offset_y=0,
        offset_x=0,
    )

    M_inv_gpu.release()
    if not is_gpu:
        src_buf.release()

    return dst_buf if return_gpu else dst_buf.to_numpy()


# ===========================================================================
# AOT Dispatch: Non-Local Means Denoising
# ===========================================================================
def _nlm_variant(search_window, patch_size):
    """Map requested NLM parameters to a compiled AOT variant."""
    variants = ((3, 1), (5, 2), (7, 3))
    return min(
        variants,
        key=lambda variant: abs(variant[0] - search_window)
        + abs(variant[1] - patch_size),
    )


def _non_local_means_tile(
    tile,
    h_param,
    search_radius,
    patch_radius,
    refinement_strength,
    shrinkage_strength,
):
    src_tile = upload(tile)
    try:
        output = non_local_means_aot(
            src_tile,
            h_param=h_param,
            search_window=search_radius,
            patch_size=patch_radius,
            refinement_strength=refinement_strength,
            shrinkage_strength=shrinkage_strength,
            return_gpu=True,
        )
        try:
            return output.to_numpy()
        finally:
            output.destroy()
    finally:
        src_tile.destroy()


def non_local_means(
    src,
    h_param=10.0,
    search_window=7,
    patch_size=5,
    refinement_strength=1.0,
    shrinkage_strength=1.0,
    return_gpu=False,
):
    """
    Taichi AOT Non-Local Means Denoising.
    Dispatches to pre-compiled fixed-parameter kernel variants.
    Supports: search_window in {3,5,7}, patch_size in {1,2,3}.
    Auto-cast: uint8/uint16 input is normalized to [0,1] float32,
    processed, then cast back to original dtype.
    """
    is_numpy = isinstance(src, np.ndarray)
    if not is_numpy:
        return non_local_means_aot(
            src,
            h_param=h_param,
            search_window=search_window,
            patch_size=patch_size,
            refinement_strength=refinement_strength,
            shrinkage_strength=shrinkage_strength,
            return_gpu=return_gpu,
        )

    # --- Auto-cast: normalize integer types to float32 [0,1] ---
    orig_dtype = src.dtype
    if src.dtype == np.uint8:
        src = src.astype(np.float32) / 255.0
    elif src.dtype == np.uint16:
        src = src.astype(np.float32) / 65535.0

    src_np = np.ascontiguousarray(src, dtype=np.float32)
    search_radius, patch_radius = _nlm_variant(search_window, patch_size)
    result = _run_blockwise(
        "non_local_means",
        (src_np,),
        src_np.shape,
        np.float32,
        lambda tile: _non_local_means_tile(
            tile,
            h_param,
            search_radius,
            patch_radius,
            refinement_strength,
            shrinkage_strength,
        ),
        halo=search_radius + patch_radius,
        params={
            "h_param": float(h_param),
            "search_radius": search_radius,
            "patch_radius": patch_radius,
            "refinement_strength": float(refinement_strength),
            "shrinkage_strength": float(shrinkage_strength),
        },
    )
    if result is None:
        result = non_local_means_aot(
            src_np,
            h_param=h_param,
            search_window=search_radius,
            patch_size=patch_radius,
            refinement_strength=refinement_strength,
            shrinkage_strength=shrinkage_strength,
            return_gpu=False,
        )

    if return_gpu:
        return upload(result)

    # --- Auto-cast back to original dtype ---
    if orig_dtype == np.uint8:
        return np.clip(result * 255.0, 0, 255).astype(np.uint8)
    elif orig_dtype == np.uint16:
        return np.clip(result * 65535.0, 0, 65535).astype(np.uint16)
    return result


# ===========================================================================
# AOT Dispatch: Inpainting
# ===========================================================================
def inpaint(src, mask, inpaint_radius=3, flags=0, return_gpu=False):
    """
    Taichi AOT Inpainting.
    Dispatches individual kernels in sequence (distance transform, dilate, fill).
    """
    from taichi_vision.taichi_aot.capabilities import opengl_native_probe

    src_shape = getattr(src, "shape", ())
    src_dtype = getattr(src, "dtype", np.float32)
    # The native graph is validated for scalar fp32 only.  RGB and integer
    # inputs stay on the reference path until dedicated parity probes exist.
    native_inpaint_shape_safe = len(src_shape) == 2 and np.dtype(src_dtype) == np.dtype(
        np.float32
    )
    if engine.arch.lower() in ("opengl", "gles") and (
        not native_inpaint_shape_safe
        or os.environ.get("PIXEL_REFINE_AOT_NATIVE_INPAINT", "0") != "1"
        or not opengl_native_probe("inpaint")
    ):
        import cv2

        source = (
            src.to_numpy()
            if isinstance(src, TaichiGPUBuffer)
            else np.ascontiguousarray(src)
        )
        source = np.ascontiguousarray(source)
        mask_np = (
            mask.to_numpy() if isinstance(mask, TaichiGPUBuffer) else np.asarray(mask)
        )
        mask_u8 = (mask_np > 0).astype(np.uint8)
        scale = (
            255.0
            if np.issubdtype(source.dtype, np.floating) and np.max(source) <= 1.0
            else 1.0
        )
        work = (
            np.clip(source * scale, 0, 255).astype(np.uint8)
            if scale != 1.0 or source.dtype != np.uint8
            else source
        )
        result = cv2.inpaint(work, mask_u8, float(inpaint_radius), cv2.INPAINT_TELEA)
        if np.issubdtype(source.dtype, np.floating):
            result = result.astype(np.float32) / scale
        else:
            result = result.astype(source.dtype, copy=False)
        return upload(np.ascontiguousarray(result)) if return_gpu else result

    is_numpy = isinstance(src, np.ndarray)
    is_3d = len(src.shape) == 3 and src.shape[2] == 3

    src_buf, src_is_temp2 = _ensure_upload(src)
    mask_buf = InputArray(
        mask.astype(np.float32) if isinstance(mask, np.ndarray) else mask
    )

    h, w = src_buf.shape[:2]
    max_dist = max(h, w) // 2 + 1

    # Allocate intermediate buffers
    dist_buf = OutputArray((h, w), dtype=np.float32)
    dist_tmp = OutputArray((h, w), dtype=np.float32)
    boundary_buf = OutputArray((h, w), dtype=np.float32)
    filled_buf = OutputArray((h, w), dtype=np.float32)

    # Stage 1: Init distance
    _mod("inpaint").run(
        "inpaint_init_distance_f32",
        mask=mask_buf,
        dist=dist_buf,
        boundary=boundary_buf,
        h=h,
        w=w,
    )

    # Iterative dilation to compute distance map
    for level in range(max_dist):
        _mod("inpaint").run(
            "inpaint_dilate_distance_f32",
            dist_in=dist_buf,
            dist_out=dist_tmp,
            h=h,
            w=w,
            current_level=float(level),
        )
        dist_buf, dist_tmp = dist_tmp, dist_buf

    # Stage 2: Init filled mask
    _mod("inpaint").run(
        "inpaint_init_distance_f32",
        mask=mask_buf,
        dist=filled_buf,
        boundary=boundary_buf,
        h=h,
        w=w,
    )
    _mod("inpaint").run(
        "inpaint_set_filled_f32", mask=mask_buf, filled=filled_buf, h=h, w=w
    )

    # Stage 3: Iterative inpainting
    if is_3d:
        for level in range(1, max_dist + 1):
            _mod("inpaint").run(
                "inpaint_level_3ch_f32",
                src=src_buf,
                dist=dist_buf,
                filled=filled_buf,
                h=h,
                w=w,
                target_level=float(level),
                inpaint_radius=float(inpaint_radius),
            )
            _mod("inpaint").run(
                "inpaint_mark_filled_f32",
                dist=dist_buf,
                filled=filled_buf,
                h=h,
                w=w,
                target_level=float(level),
            )
    else:
        for level in range(1, max_dist + 1):
            _mod("inpaint").run(
                "inpaint_level_1ch_f32",
                src=src_buf,
                dist=dist_buf,
                filled=filled_buf,
                h=h,
                w=w,
                target_level=float(level),
                inpaint_radius=float(inpaint_radius),
            )
            _mod("inpaint").run(
                "inpaint_mark_filled_f32",
                dist=dist_buf,
                filled=filled_buf,
                h=h,
                w=w,
                target_level=float(level),
            )

    return src_buf if return_gpu else src_buf.to_numpy()


# ===========================================================================
# AOT Dispatch: Seamless Clone (Poisson Image Editing)
# ===========================================================================
def seamless_clone(
    src, dst, mask, center=(0, 0), flags=1, max_iterations=200, return_gpu=False
):
    """
    Taichi AOT Seamless Clone.
    Dispatches Jacobi iterations for Poisson blending.
    """
    is_numpy = isinstance(dst, np.ndarray)

    src_buf = InputArray(src)
    dst_buf = InputArray(dst)
    mask_buf = InputArray(
        mask.astype(np.float32) if isinstance(mask, np.ndarray) else mask
    )

    src_buf = src_buf.view_as_vector(True) if len(src_buf.shape) == 3 else src_buf
    dst_buf_v = dst_buf.view_as_vector(True) if len(dst_buf.shape) == 3 else dst_buf

    h, w = dst_buf.shape[:2]

    # Output = copy of dst
    out_buf = OutputArray((h, w, 3), dtype=np.float32, is_vector=True, vector_dim=3)
    _mod("seamless_clone").run("seamless_copy_f32", s=dst_buf_v, d=out_buf, h=h, w=w)

    # Intermediate buffers
    div_x = OutputArray((h, w), dtype=np.float32)
    div_y = OutputArray((h, w), dtype=np.float32)
    lap_buf = OutputArray((h, w), dtype=np.float32)
    f_in_buf = OutputArray((h, w), dtype=np.float32)
    f_out_buf = OutputArray((h, w), dtype=np.float32)

    num_channels = 3 if flags != 3 else 1  # MONOCHROME_TRANSFER = 3

    for ch in range(num_channels):
        # Compute guidance gradient
        if flags == 1 or flags == 3:  # NORMAL_CLONE or MONOCHROME_TRANSFER
            _mod("seamless_clone").run(
                "seamless_divergence_normal_f32",
                src=src_buf,
                div_x=div_x,
                div_y=div_y,
                h=h,
                w=w,
                ch=ch,
            )
        elif flags == 2:  # MIXED_CLONE
            _mod("seamless_clone").run(
                "seamless_divergence_mixed_f32",
                src=src_buf,
                dst=dst_buf_v,
                div_x=div_x,
                div_y=div_y,
                h=h,
                w=w,
                ch=ch,
            )

        # Compute Laplacian
        _mod("seamless_clone").run(
            "seamless_laplacian_f32", div_x=div_x, div_y=div_y, lap=lap_buf, h=h, w=w
        )

        # Init f from destination channel
        _mod("seamless_clone").run(
            "seamless_init_f_channel_f32", dst_arr=out_buf, f=f_in_buf, h=h, w=w, c=ch
        )

        # Jacobi iterations
        for _ in range(max_iterations):
            _mod("seamless_clone").run(
                "seamless_jacobi_step_f32",
                f_in=f_in_buf,
                f_out=f_out_buf,
                lap=lap_buf,
                mask=mask_buf,
                h=h,
                w=w,
            )
            f_in_buf, f_out_buf = f_out_buf, f_in_buf

        # Composite
        _mod("seamless_clone").run(
            "seamless_composite_f32",
            f=f_in_buf,
            dst_out=out_buf,
            mask=mask_buf,
            h=h,
            w=w,
            ch=ch,
        )

    return out_buf if return_gpu else out_buf.to_numpy()


# ===========================================================================
# AOT Dispatch: MTB (Median Threshold Bitmap) Alignment
# ===========================================================================
def align_mtb(ref_img, target_img, max_levels=6, tolerance=4.0 / 255.0):
    """
    Taichi AOT MTB Alignment.
    Returns: (dx, dy) integer shift.
    Uses pre-compiled histogram, bitmap, and error kernels.
    """

    # Keep the entire alignment pipeline in Taichi AOT.  Grayscale conversion
    # and pyramid construction use the same compiled graphs as the rest of the
    # library; no host image-processing dependency is required.
    def _gray(img):
        array = np.ascontiguousarray(img)
        if array.ndim == 3:
            array = rgb2gray(array)
        return array.astype(np.float32, copy=False) / 255.0

    def _build_pyr(img, levels):
        pyr = [img]
        for _ in range(levels - 1):
            nxt = image_pyramid(pyr[-1], levels=1, return_gpu=False)
            if nxt.shape[:2] == pyr[-1].shape[:2]:
                break
            pyr.append(nxt)
        return pyr

    ref_gray = _gray(ref_img)
    tgt_gray = _gray(target_img)

    ref_pyr = _build_pyr(ref_gray, max_levels)
    tgt_pyr = _build_pyr(tgt_gray, max_levels)

    current_dx, current_dy = 0, 0

    for level in reversed(range(len(ref_pyr))):
        ref_level = ref_pyr[level]
        tgt_level = tgt_pyr[level]
        h, w = ref_level.shape

        current_dx *= 2
        current_dy *= 2

        ref_buf = InputArray(ref_level)
        tgt_buf = InputArray(tgt_level)

        # Compute histograms
        ref_hist = OutputArray((256,), dtype=np.int32)
        tgt_hist = OutputArray((256,), dtype=np.int32)
        _mod("mtb").run("mtb_histogram_f32", img=ref_buf, hist=ref_hist)
        _mod("mtb").run("mtb_histogram_f32", img=tgt_buf, hist=tgt_hist)

        # Find medians (CPU)
        def _find_median(hist_np):
            total = h * w
            cum = 0
            for i in range(256):
                cum += int(hist_np[i])
                if cum >= total // 2:
                    return i / 255.0
            return 0.5

        ref_med = _find_median(ref_hist.to_numpy())
        tgt_med = _find_median(tgt_hist.to_numpy())

        # Compute bitmaps and exclusion maps
        ref_bitmap = OutputArray((h, w), dtype=np.int32)
        ref_excl = OutputArray((h, w), dtype=np.int32)
        tgt_bitmap = OutputArray((h, w), dtype=np.int32)
        tgt_excl = OutputArray((h, w), dtype=np.int32)

        _mod("mtb").run(
            "mtb_bitmaps_f32",
            img=ref_buf,
            bitmap=ref_bitmap,
            exclusion=ref_excl,
            median_val=float(ref_med),
            tolerance=float(tolerance),
        )
        _mod("mtb").run(
            "mtb_bitmaps_f32",
            img=tgt_buf,
            bitmap=tgt_bitmap,
            exclusion=tgt_excl,
            median_val=float(tgt_med),
            tolerance=float(tolerance),
        )

        # Search 3x3 neighborhood
        best_err = 2**31 - 1
        best_ox, best_oy = 0, 0
        err_buf = OutputArray((1,), dtype=np.int32)

        for oy in [-1, 0, 1]:
            for ox in [-1, 0, 1]:
                test_dx = current_dx + ox
                test_dy = current_dy + oy
                _mod("mtb").run(
                    "mtb_error_f32",
                    bitmap1=ref_bitmap,
                    exclusion1=ref_excl,
                    bitmap2=tgt_bitmap,
                    exclusion2=tgt_excl,
                    error_buf=err_buf,
                    dx=test_dx,
                    dy=test_dy,
                )
                err_val = int(err_buf.to_numpy()[0])
                if err_val < best_err:
                    best_err = err_val
                    best_ox, best_oy = ox, oy

        current_dx += best_ox
        current_dy += best_oy

    return current_dx, current_dy


def _ensure_upload(arr):
    """Helper: upload ndarray to InputArray if needed."""
    if isinstance(arr, TaichiGPUBuffer):
        return arr, False
    return InputArray(arr), True


# =========================================================================
# NEW ALGORITHMS — AOT Bridge Wrappers
# =========================================================================

# --- Color Space Conversion Constants ---
COLOR_BGR2HSV = 40
COLOR_HSV2BGR = 54
COLOR_BGR2YCrCb = 36
COLOR_YCrCb2BGR = 38
COLOR_BGR2LAB = 44
COLOR_LAB2BGR = 55


# --- Inpainting Flags ---
INPAINT_TELEA = 0
INPAINT_NS = 1

# --- Seamless Clone Flags ---
NORMAL_CLONE = 1
MIXED_CLONE = 2
MONOCHROME_TRANSFER = 3


_CVT_COLOR_EXTENDED_GRAPHS = {
    COLOR_BGR2HSV: "bgr2hsv_f32",
    COLOR_HSV2BGR: "hsv2bgr_f32",
    COLOR_BGR2YCrCb: "bgr2ycrcb_f32",
    COLOR_YCrCb2BGR: "ycrcb2bgr_f32",
    COLOR_BGR2LAB: "bgr2lab_f32",
    COLOR_LAB2BGR: "lab2bgr_f32",
}


def _cvt_color_extended_tile(tile, code):
    """Run one plain HxWx3 tile without the vector-field view."""
    owner = engine.upload(np.ascontiguousarray(tile, dtype=np.float32))
    source = owner.view_as_vector(False)
    dst = engine.allocate(tile.shape, dtype=np.float32, is_vector=False)
    try:
        graph_name = _CVT_COLOR_EXTENDED_GRAPHS[code]
        _mod("color_convert").run(
            graph_name,
            src=source,
            dst=dst,
            h=int(tile.shape[0]),
            w=int(tile.shape[1]),
        )
        return dst.to_numpy()
    finally:
        dst.destroy()
        owner.destroy()


def cvtColor_extended(src, code, return_gpu=False):
    """AOT Color Space Conversion (BGR<->HSV, BGR<->YCrCb, BGR<->LAB)."""
    is_gpu = isinstance(src, TaichiGPUBuffer)

    # All supported conversions are pointwise over HxWx3 pixels.  Use the
    # normal tile cache under memory pressure; the full-frame dispatch below
    # remains the exact fallback for small inputs or a quarantined operation.
    if not is_gpu:
        array = np.ascontiguousarray(src, dtype=np.float32)
        if array.ndim != 3 or array.shape[2] != 3:
            raise ValueError("cvtColor_extended expects an HxWx3 array")
        if code not in _CVT_COLOR_EXTENDED_GRAPHS:
            raise ValueError(f"Unsupported color conversion code: {code}")
        result = _run_blockwise(
            "cvtColor_extended",
            (array,),
            array.shape,
            np.float32,
            lambda tile: _cvt_color_extended_tile(tile, code),
            params={"code": int(code)},
        )
        if result is not None:
            return upload(result) if return_gpu else result

    src_buf = src if is_gpu else engine.upload(src)
    # Override auto-detected is_vector for ndim=3 graphs:
    # engine.upload auto-sets is_vector=True for (H,W,3) arrays,
    # but the TCM graph expects plain ndim=3 (not vector field).
    if getattr(src_buf, "is_vector", False):
        src_buf = src_buf.view_as_vector(False)
    h, w = src_buf.shape[:2]
    # Allocate dst as plain ndarray (is_vector=False) to match ndim=3 graph
    dst = engine.allocate((h, w, 3))

    graph_name = _CVT_COLOR_EXTENDED_GRAPHS.get(code)
    if graph_name is None:
        raise ValueError(f"Unsupported color conversion code: {code}")

    _mod("color_convert").run(graph_name, src=src_buf, dst=dst, h=h, w=w)
    return dst if return_gpu else dst.to_numpy()


def otsu_threshold_aot(src, thresh_type=0, max_val=255.0, return_gpu=False):
    """AOT Otsu's Thresholding. Returns (threshold_value, binary_image)."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    if not is_gpu:
        array = np.ascontiguousarray(src, dtype=np.float32)
        # Otsu itself is global, but its histogram reduction can still use
        # the same native grid geometry as a block-safe operation.
        grid = engine.plan_blocks("copy", array.shape, array.nbytes)
        if grid is not None:
            # Otsu is a global reduction: calculate one exact threshold from
            # per-block histograms, then apply it to each block.
            hist_np = np.zeros(256, dtype=np.int64)
            for block in grid:
                tile = np.ascontiguousarray(array[block.read_slice])
                tile_buf = upload(tile)
                hist_buf = upload(np.zeros(256, dtype=np.int32))
                try:
                    _mod("otsu").run(
                        "otsu_histogram_f32",
                        src=tile_buf,
                        hist=hist_buf,
                        h=tile.shape[0],
                        w=tile.shape[1],
                        max_val=float(max_val),
                        num_bins=256,
                    )
                    hist_np += hist_buf.to_numpy().astype(np.int64)
                finally:
                    hist_buf.release()
                    tile_buf.release()

            total = float(hist_np.sum())
            if total == 0:
                threshold_val = 0.0
            else:
                mu_t = float(np.dot(np.arange(256, dtype=np.float64), hist_np)) / total
                w0 = sum0 = max_sigma = 0.0
                best_t = 0
                for t in range(256):
                    w0 += float(hist_np[t])
                    if w0 == 0:
                        continue
                    w1 = total - w0
                    if w1 == 0:
                        break
                    sum0 += float(t * hist_np[t])
                    sigma = w0 * w1 * ((sum0 / w0) - ((mu_t * total - sum0) / w1)) ** 2
                    if sigma > max_sigma:
                        max_sigma, best_t = sigma, t
                threshold_val = float(best_t)

            result = np.empty(array.shape, dtype=np.float32)
            for block in grid:
                tile = array[block.read_slice]
                if thresh_type == 0:
                    out = np.where(tile > threshold_val, max_val, 0.0)
                elif thresh_type == 1:
                    out = np.where(tile > threshold_val, 0.0, max_val)
                else:
                    out = np.where(tile > threshold_val, tile, 0.0)
                result[block.write_slice] = out[block.core_slice]
            return threshold_val, upload(result) if return_gpu else result

    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]
    dst = engine.allocate((h, w))

    # Histogram — zero-initialize to avoid garbage data from buffer pool reuse
    num_bins = 256
    hist = engine.allocate((num_bins,), dtype=np.int32)
    zero_np = np.zeros(num_bins, dtype=np.int32)
    zero_buf = engine.upload(zero_np)
    copy_field(zero_buf, hist)
    zero_buf.destroy()

    _mod("otsu").run(
        "otsu_histogram_f32",
        src=src_buf,
        hist=hist,
        h=h,
        w=w,
        max_val=float(max_val),
        num_bins=num_bins,
    )

    # Find threshold on CPU — use float64 to avoid int32 overflow
    hist_np = hist.to_numpy().astype(np.float64)
    total = float(hist_np.sum())
    if total == 0:
        threshold_val = 0.0
    else:
        mu_T = sum(float(i) * hist_np[i] for i in range(256)) / total
        w0, sum_0, max_sigma, best_t = 0.0, 0.0, -1.0, 0
        for t in range(256):
            w0 += hist_np[t]
            if w0 == 0:
                continue
            w1 = total - w0
            if w1 == 0:
                break
            sum_0 += float(t) * hist_np[t]
            mu0 = sum_0 / w0
            mu1 = (mu_T * total - sum_0) / w1
            sigma_B = w0 * w1 * (mu0 - mu1) ** 2
            if sigma_B > max_sigma:
                max_sigma = sigma_B
                best_t = t
        threshold_val = float(best_t)

    # Apply threshold
    _mod("otsu").run(
        "otsu_threshold_f32",
        src=src_buf,
        dst=dst,
        threshold=threshold_val,
        max_val=float(max_val),
        thresh_type=thresh_type,
        h=h,
        w=w,
    )
    result = dst if return_gpu else dst.to_numpy()
    return threshold_val, result


def _clahe_full(src, clip_limit=2.0, tile_grid_size=(8, 8), return_gpu=False):
    """AOT CLAHE - Contrast Limited Adaptive Histogram Equalization."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]
    tiles_x, tiles_y = tile_grid_size
    total_tiles = tiles_x * tiles_y
    num_bins = 256
    tile_h = (h + tiles_y - 1) // tiles_y
    tile_w = (w + tiles_x - 1) // tiles_x
    tile_pixels = tile_h * tile_w
    beta = max(int(clip_limit * tile_pixels / num_bins), 1)

    hist = engine.allocate((total_tiles, num_bins), dtype=np.int32)
    lut = engine.allocate((total_tiles, num_bins))
    dst = engine.allocate((h, w))

    # Zero-initialize hist and lut to avoid garbage from buffer pool reuse
    zero_hist = engine.upload(np.zeros((total_tiles, num_bins), dtype=np.int32))
    copy_field(zero_hist, hist)
    zero_hist.destroy()
    zero_lut = engine.upload(np.zeros((total_tiles, num_bins), dtype=np.float32))
    copy_field(zero_lut, lut)
    zero_lut.destroy()

    _mod("clahe").run(
        "clahe_pipeline_f32",
        src=src_buf,
        hist=hist,
        lut=lut,
        dst=dst,
        h=h,
        w=w,
        tile_h=tile_h,
        tile_w=tile_w,
        tiles_x=tiles_x,
        tiles_y=tiles_y,
        total_tiles=total_tiles,
        num_bins=num_bins,
        clip_limit=beta,
        tile_pixels=tile_pixels,
        max_val=255.0,
    )
    return dst if return_gpu else np.rint(dst.to_numpy()).astype(np.float32)


def clahe_aot(src, clip_limit=2.0, tile_grid_size=(8, 8), return_gpu=False):
    """CLAHE with automatic block execution for CPU-backed large images.

    The existing CLAHE kernel remains the authority for each tile. A halo of
    one semantic histogram tile keeps interpolation near block boundaries
    stable while the public API and GPU path remain unchanged.
    """
    # CLAHE's tile histograms form one interpolation field. Running a separate
    # CLAHE instance per compute block changes that field and creates seams;
    # retain the single global LUT while the runtime manages its residency.
    return _clahe_full(src, clip_limit, tile_grid_size, return_gpu)


def _canny_full(src, low_threshold=50.0, high_threshold=150.0, return_gpu=False):
    """AOT Canny Edge Detector."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    h, w = src_buf.shape[:2]

    # OpenCV's Canny API applies Sobel directly to the supplied image; it does
    # not implicitly apply a Gaussian blur.  Keeping the same contract here is
    # important for backend parity (the caller can blur explicitly when
    # desired).  The previous implicit blur caused large edge-topology drift
    # on textured frames.
    blurred_buf = src_buf

    # Internal buffers
    gx = engine.allocate((h, w))
    gy = engine.allocate((h, w))
    mag = engine.allocate((h, w))
    nms = engine.allocate((h, w))
    edges = engine.allocate((h, w))
    dst = engine.allocate((h, w))

    def _dispatch_canny_pre_hysteresis():
        # Step 1: Sobel gradients on pre-smoothed image
        _mod("gradients").run(
            "sobel_f32", src=blurred_buf, dst_dx=gx, dst_dy=gy, h=h, w=w
        )

        # Step 2: magnitude and NMS require separate GPU dispatches. NMS reads
        # neighbour magnitudes, which are not coherent inside a fused dispatch.
        _mod("canny").run("canny_magnitude_f32", gx=gx, gy=gy, mag=mag, h=h, w=w)
        _mod("canny").run("canny_nms_f32", gx=gx, gy=gy, mag=mag, nms=nms, h=h, w=w)

        # Step 3: Double threshold
        _mod("canny").run(
            "canny_threshold_f32",
            nms=nms,
            edges=edges,
            low_thresh=low_threshold,
            high_thresh=high_threshold,
            h=h,
            w=w,
        )

    _mod("gradients")
    _mod("canny")

    # Record only the deterministic local prefix.  Hysteresis is an iterative
    # convergence loop and remains direct so its dynamic pass count, status
    # buffers, and synchronization boundaries cannot be misrepresented as a
    # static one-big-graph sequence.
    _run_auto_graph_sequence(
        ("sobel_f32", "canny_magnitude_f32", "canny_nms_f32", "canny_threshold_f32"),
        (h, w),
        _dispatch_canny_pre_hysteresis,
        operation="canny",
        source="canny_pre_hysteresis",
        resident_multiplier=8,
        reads=("source",),
        writes=("gx", "gy", "magnitude", "nms", "edges"),
        metadata={
            "sequence_kind": "deterministic_local_prefix",
            "hazard_policy": "ordered",
        },
        module_keys=("gradients", "canny", "canny", "canny"),
        retain_buffers=(edges,),
    )

    # Step 4: Iterative hysteresis
    # Do not read back a synchronization flag per pass: on Vulkan that creates
    # a host/device race around a pool-backed scalar. A bounded fixed pass
    # count is deterministic and keeps hysteresis entirely on the device.
    # One persistent status buffer is sufficient: dispatches are ordered and
    # the host never reads this value in the fixed-pass AOT path. The previous
    # implementation allocated and retained 256 SSBOs, which can exhaust or
    # wedge older Intel OpenGL drivers even though the Canny kernels are valid.
    changed_buf = engine.allocate((1,), dtype=np.int32)
    try:
        for _ in range(min(h + w, 256)):
            _mod("canny").run(
                "canny_hysteresis_f32", edges=edges, changed=changed_buf, h=h, w=w
            )

        # Step 5: Finalize while the status buffer is still alive.
        _mod("canny").run("canny_finalize_f32", edges=edges, dst=dst, h=h, w=w)
        result = dst if return_gpu else dst.to_numpy()
    finally:
        changed_buf.release()

    return result


def canny_aot(src, low_threshold=50.0, high_threshold=150.0, return_gpu=False):
    """Pure Taichi AOT Canny implementation for host and GPU inputs."""
    # The current OpenGL Canny graph is numerically stable but does not yet
    # reproduce OpenCV's non-maximum suppression/hysteresis topology closely
    # enough for production image quality.  Preserve the public API and exact
    # reference semantics until a parity-qualified graph is available.
    if (
        engine.arch.lower() in ("opengl", "gles")
        and os.environ.get("PIXEL_REFINE_AOT_NATIVE_CANNY", "1") != "1"
    ):
        import cv2

        source = (
            src.to_numpy()
            if isinstance(src, TaichiGPUBuffer)
            else np.ascontiguousarray(src)
        )
        source_u8 = np.clip(source, 0, 255).astype(np.uint8)
        result = cv2.Canny(
            source_u8, float(low_threshold), float(high_threshold)
        ).astype(np.float32)
        return upload(result) if return_gpu else result
    # The native Canny graphs operate in normalized fp32 space. Preserve the
    # public OpenCV-style 0..255 API by normalizing host integer/range inputs
    # before dispatch and scaling thresholds accordingly.
    if not isinstance(src, TaichiGPUBuffer):
        src_arr = np.ascontiguousarray(src, dtype=np.float32)
        scale = 255.0 if (src_arr.size and float(np.nanmax(src_arr)) > 1.0) else 1.0
        if scale != 1.0:
            # Match the public OpenCV-style 8-bit contract. Quantizing before
            # upload avoids backend-dependent edge flips when callers provide
            # float values that represent integer image samples.
            src = np.floor(np.clip(src_arr, 0.0, scale)) / scale
            low_threshold = float(low_threshold) / scale
            high_threshold = float(high_threshold) / scale
    return _canny_full(src, low_threshold, high_threshold, return_gpu)


def hough_lines_aot(
    edge_image, rho_resolution=1.0, theta_resolution=1.0, threshold=80, return_gpu=False
):
    """AOT Hough Line Transform. Returns list of (rho, theta) pairs."""
    is_gpu = isinstance(edge_image, TaichiGPUBuffer)
    src_buf = edge_image if is_gpu else engine.upload(edge_image)
    h, w = src_buf.shape[:2]

    import math

    num_theta = int(180.0 / theta_resolution)
    diag = int(math.sqrt(h * h + w * w))
    num_rho = int(2 * diag / rho_resolution) + 1
    rho_offset = diag

    acc = engine.allocate((num_rho, num_theta), dtype=np.int32)
    cos_table = engine.allocate((num_theta,))
    sin_table = engine.allocate((num_theta,))
    peaks_buf = engine.allocate((500, 3))  # max 500 peaks
    peak_count = engine.allocate((1,), dtype=np.int32)

    # Fill trig tables
    cos_np = np.array(
        [math.cos(math.radians(t * theta_resolution)) for t in range(num_theta)],
        dtype=np.float32,
    )
    sin_np = np.array(
        [math.sin(math.radians(t * theta_resolution)) for t in range(num_theta)],
        dtype=np.float32,
    )
    cos_table_buf = engine.upload(cos_np)
    sin_table_buf = engine.upload(sin_np)

    # The vote kernel uses atomic adds, so initialize the accumulator before
    # the first dispatch and again if an attempted recording has to be retried
    # directly.  This makes the automatic optimization idempotent instead of
    # allowing a partially recorded vote pass to be counted twice.
    zero_acc = engine.upload(np.zeros((num_rho, num_theta), dtype=np.int32))

    def _reset_accumulator():
        copy_field(zero_acc, acc)

    _reset_accumulator()

    def _dispatch_hough_stages():
        # Vote
        _mod("hough").run(
            "hough_vote_f32",
            edges=src_buf,
            accumulator=acc,
            cos_table=cos_table_buf,
            sin_table=sin_table_buf,
            h=h,
            w=w,
            num_theta=num_theta,
            rho_offset=rho_offset,
            edge_threshold=128.0,
        )

        # Find peaks
        _mod("hough").run(
            "hough_peaks_f32",
            accumulator=acc,
            peaks=peaks_buf,
            peak_count=peak_count,
            num_rho=num_rho,
            num_theta=num_theta,
            threshold=threshold,
            nms_radius=10,
            max_peaks=500,
        )

    _mod("hough")
    _run_auto_graph_sequence(
        ("hough_vote_f32", "hough_peaks_f32"),
        (h, w),
        _dispatch_hough_stages,
        operation="hough_lines",
        source="hough_vote_peaks",
        resident_multiplier=4,
        reads=("edges", "trig_tables"),
        writes=("accumulator", "peaks", "peak_count"),
        metadata={
            "sequence_kind": "vote_then_peak",
            "hazard_policy": "ordered",
        },
        module_keys=("hough", "hough"),
        retry_prepare=_reset_accumulator,
        retain_buffers=(peaks_buf, peak_count),
    )

    peaks_np = peaks_buf.to_numpy()
    count = min(int(peak_count.to_numpy()[0]), 500)  # Clamp to buffer size
    lines = []
    for i in range(count):
        rho = (peaks_np[i, 0] - rho_offset) * rho_resolution
        theta = peaks_np[i, 1] * theta_resolution * math.pi / 180.0
        lines.append((rho, theta))

    # These buffers are private to this call.  Release them after the readback
    # so the new recording scope cannot retain a stale pipeline lease.
    for buffer in (
        zero_acc,
        cos_table_buf,
        sin_table_buf,
        acc,
        cos_table,
        sin_table,
        peaks_buf,
        peak_count,
    ):
        try:
            buffer.release()
        except Exception:
            try:
                buffer.destroy()
            except Exception:
                pass
    if not is_gpu:
        try:
            src_buf.release()
        except Exception:
            try:
                src_buf.destroy()
            except Exception:
                pass
    return lines


def _guided_filter_tile(guide_tile, src_tile, radius, epsilon):
    guide_buffer = upload(guide_tile)
    src_buffer = upload(src_tile)
    try:
        output = guided_filter_aot(
            guide_buffer, src_buffer, radius=radius, epsilon=epsilon, return_gpu=True
        )
        try:
            return output.to_numpy()
        finally:
            output.destroy()
    finally:
        guide_buffer.destroy()
        src_buffer.destroy()


def guided_filter_aot(guide, src, radius=8, epsilon=1e-4, return_gpu=False):
    """AOT Guided Filter (edge-preserving smoothing).
    Uses box_filter module for box averaging and guided_filter module for element-wise ops.
    """
    from taichi_vision.taichi_aot.capabilities import opengl_native_probe

    if engine.arch.lower() in ("opengl", "gles") and (
        os.environ.get("PIXEL_REFINE_AOT_NATIVE_GUIDED", "1") != "1"
        or not opengl_native_probe("guided")
    ):
        import cv2

        I = (
            guide.to_numpy()
            if isinstance(guide, TaichiGPUBuffer)
            else np.asarray(guide, dtype=np.float32)
        )
        p = (
            src.to_numpy()
            if isinstance(src, TaichiGPUBuffer)
            else np.asarray(src, dtype=np.float32)
        )
        I = np.ascontiguousarray(I, dtype=np.float32)
        p = np.ascontiguousarray(p, dtype=np.float32)
        if I.ndim != 2 or p.ndim != 2 or I.shape != p.shape:
            raise ValueError(
                "guided_filter_aot requires matching 2D guide and source arrays"
            )
        ksize = (2 * int(radius) + 1, 2 * int(radius) + 1)
        mean_I = cv2.boxFilter(
            I, -1, ksize, normalize=True, borderType=cv2.BORDER_REPLICATE
        )
        mean_p = cv2.boxFilter(
            p, -1, ksize, normalize=True, borderType=cv2.BORDER_REPLICATE
        )
        corr_I = cv2.boxFilter(
            I * I, -1, ksize, normalize=True, borderType=cv2.BORDER_REPLICATE
        )
        corr_Ip = cv2.boxFilter(
            I * p, -1, ksize, normalize=True, borderType=cv2.BORDER_REPLICATE
        )
        a = (corr_Ip - mean_I * mean_p) / (corr_I - mean_I * mean_I + float(epsilon))
        b = mean_p - a * mean_I
        mean_a = cv2.boxFilter(
            a, -1, ksize, normalize=True, borderType=cv2.BORDER_REPLICATE
        )
        mean_b = cv2.boxFilter(
            b, -1, ksize, normalize=True, borderType=cv2.BORDER_REPLICATE
        )
        result = mean_a * I + mean_b
        return upload(np.ascontiguousarray(result)) if return_gpu else result

    if not isinstance(guide, TaichiGPUBuffer) and not isinstance(src, TaichiGPUBuffer):
        guide_array = np.ascontiguousarray(guide, dtype=np.float32)
        source = np.ascontiguousarray(src, dtype=np.float32)
        if (
            guide_array.ndim != 2
            or source.ndim != 2
            or guide_array.shape != source.shape
        ):
            raise ValueError(
                "guided_filter_aot requires matching 2D guide and source arrays"
            )
        result = _run_blockwise(
            "guided_filter",
            (guide_array, source),
            source.shape,
            np.float32,
            lambda guide_tile, src_tile: _guided_filter_tile(
                guide_tile, src_tile, radius, epsilon
            ),
            halo=2 * int(radius),
            params={"radius": int(radius), "epsilon": float(epsilon)},
        )
        if result is not None:
            return upload(result) if return_gpu else result

        guide_buffer = upload(guide_array)
        src_buffer = upload(source)
        output = guided_filter_aot(
            guide_buffer, src_buffer, radius=radius, epsilon=epsilon, return_gpu=True
        )
        if return_gpu:
            guide_buffer.destroy()
            src_buffer.destroy()
            return output
        try:
            return output.to_numpy()
        finally:
            guide_buffer.destroy()
            src_buffer.destroy()
            output.destroy()

    is_gpu_src = isinstance(src, TaichiGPUBuffer)
    is_gpu_guide = isinstance(guide, TaichiGPUBuffer)
    src_buf = src if is_gpu_src else engine.upload(src)
    guide_buf = guide if is_gpu_guide else engine.upload(guide)
    h, w = src_buf.shape[:2]

    # Box filter helper (separable) — use 1ch generic graph
    ks = 2 * radius + 1
    radius_bf = ks // 2

    def _box_filter_1ch(input_buf):
        """Apply separable box filter on a single-channel buffer using box_filter module."""
        out = engine.allocate((h, w))
        tmp = engine.allocate((h, w))
        _mod("box_filter").run(
            "box_filter_separable_generic_1ch_f32",
            src=input_buf,
            tmp=tmp,
            dst=out,
            h=h,
            w=w,
            radius=radius_bf,
        )
        # Graphics dispatch is asynchronous; do not recycle the temporary
        # allocation until the command that consumed it has completed.
        engine.sync()
        tmp.destroy()
        return out

    # Step 1: Compute means via box filter
    mean_I = _box_filter_1ch(guide_buf)
    mean_p = _box_filter_1ch(src_buf)

    # Element-wise products
    II = engine.allocate((h, w))
    Ip = engine.allocate((h, w))
    _mod("guided_filter").run("gf_mul_f32", a=guide_buf, b=guide_buf, dst=II, h=h, w=w)
    _mod("guided_filter").run("gf_mul_f32", a=guide_buf, b=src_buf, dst=Ip, h=h, w=w)
    mean_II = _box_filter_1ch(II)
    mean_Ip = _box_filter_1ch(Ip)
    engine.sync()
    II.destroy()
    Ip.destroy()

    # Step 2: Compute var and cov
    var_I = engine.allocate((h, w))
    cov_Ip = engine.allocate((h, w))
    if engine.arch.lower() == "vulkan":
        _mod("guided_filter").run(
            "gf_var_portable_f32",
            mean_I=mean_I,
            mean_II=mean_II,
            var_I=var_I,
            h=h,
            w=w,
        )
        _mod("guided_filter").run(
            "gf_cov_portable_f32",
            mean_I=mean_I,
            mean_p=mean_p,
            mean_Ip=mean_Ip,
            cov_Ip=cov_Ip,
            h=h,
            w=w,
        )
    else:
        _mod("guided_filter").run(
            "gf_var_cov_f32",
            mean_I=mean_I,
            mean_p=mean_p,
            mean_II=mean_II,
            mean_Ip=mean_Ip,
            var_I=var_I,
            cov_Ip=cov_Ip,
            h=h,
            w=w,
        )

    # Step 3: Compute a, b coefficients
    a = engine.allocate((h, w))
    b = engine.allocate((h, w))
    if engine.arch.lower() == "vulkan":
        _mod("guided_filter").run(
            "gf_a_portable_f32",
            var_I=var_I,
            cov_Ip=cov_Ip,
            a=a,
            epsilon=float(epsilon),
            h=h,
            w=w,
        )
        _mod("guided_filter").run(
            "gf_b_portable_f32",
            mean_I=mean_I,
            mean_p=mean_p,
            a=a,
            b=b,
            h=h,
            w=w,
        )
    else:
        _mod("guided_filter").run(
            "gf_ab_f32",
            var_I=var_I,
            cov_Ip=cov_Ip,
            mean_I=mean_I,
            mean_p=mean_p,
            a=a,
            b=b,
            epsilon=float(epsilon),
            h=h,
            w=w,
        )

    # Step 4: Average a, b via box filter
    mean_a = _box_filter_1ch(a)
    mean_b = _box_filter_1ch(b)
    engine.sync()
    a.destroy()
    b.destroy()

    # Step 5: Compute output
    dst = engine.allocate((h, w))
    _mod("guided_filter").run(
        "gf_output_f32", mean_a=mean_a, mean_b=mean_b, I=guide_buf, dst=dst, h=h, w=w
    )

    # Cleanup
    engine.sync()
    mean_I.destroy()
    mean_p.destroy()
    mean_II.destroy()
    mean_Ip.destroy()
    var_I.destroy()
    cov_Ip.destroy()
    mean_a.destroy()
    mean_b.destroy()

    return dst if return_gpu else dst.to_numpy()


def non_local_means_aot(
    src,
    h_param=10.0,
    search_window=7,
    patch_size=5,
    refinement_strength=1.0,
    shrinkage_strength=1.0,
    return_gpu=False,
):
    """AOT Non-Local Means Denoising (fixed-parameter variants)."""
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)

    # View as 3D scalar array if uploaded as 2D vector array
    if getattr(src_buf, "is_vector", False):
        src_buf = src_buf.view_as_vector(False)

    h, w = src_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3

    # Select AOT variant based on search_window and patch_size
    sr = search_window
    pr = patch_size
    valid_configs = [(3, 1), (5, 2), (7, 3)]
    # Find closest valid config
    best = min(valid_configs, key=lambda c: abs(c[0] - sr) + abs(c[1] - pr))
    sr, pr = best

    if is_3d:
        dst = engine.allocate((h, w, 3), is_vector=False)
        yuv = engine.allocate((h, w, 3), is_vector=False)
        graph = f"nlm_3ch_s{sr}_p{pr}_f32"
        _mod("nlm").run(
            graph,
            src=src_buf,
            yuv=yuv,
            dst=dst,
            h=h,
            w=w,
            h_param=float(h_param),
            refinement_strength=float(refinement_strength),
            shrinkage_strength=float(shrinkage_strength),
        )
        yuv.destroy()
    else:
        dst = engine.allocate((h, w))
        graph = f"nlm_1ch_s{sr}_p{pr}_f32"
        _mod("nlm").run(
            graph,
            src=src_buf,
            dst=dst,
            h=h,
            w=w,
            h_param=float(h_param),
            refinement_strength=float(refinement_strength),
            shrinkage_strength=float(shrinkage_strength),
        )
    return dst if return_gpu else dst.to_numpy()


def inpaint_aot(src, mask, inpaint_radius=3, return_gpu=False):
    """AOT Image Inpainting (iterative diffusion)."""
    if (
        engine.arch.lower() in ("opengl", "gles")
        and os.environ.get("PIXEL_REFINE_AOT_NATIVE_INPAINT", "0") != "1"
    ):
        return inpaint(src, mask, inpaint_radius=inpaint_radius, return_gpu=return_gpu)

    is_gpu_src = isinstance(src, TaichiGPUBuffer)
    is_gpu_mask = isinstance(mask, TaichiGPUBuffer)
    src_buf = src if is_gpu_src else engine.upload(src)
    # The shipped inpaint graphs are f32-only.  Do the conversion at the
    # public AOT boundary instead of allowing a late graph-argument dtype
    # error (particularly common for the usual uint8 OpenCV mask).
    owned_src_upload = not is_gpu_src
    if np.dtype(src_buf.dtype) != np.dtype(np.float32):
        src_f32 = engine.upload(
            np.ascontiguousarray(src_buf.to_numpy(), dtype=np.float32)
        )
        if owned_src_upload:
            src_buf.destroy()
        src_buf = src_f32
        owned_src_upload = True
    # Override auto-detected is_vector for ndim=3 graphs (3ch inpaint)
    if getattr(src_buf, "is_vector", False):
        src_buf = src_buf.view_as_vector(False)
    mask_buf = mask if is_gpu_mask else engine.upload(mask)
    owned_mask_upload = not is_gpu_mask
    if np.dtype(mask_buf.dtype) != np.dtype(np.float32):
        mask_f32 = engine.upload(
            np.ascontiguousarray(mask_buf.to_numpy(), dtype=np.float32)
        )
        if owned_mask_upload:
            mask_buf.destroy()
        mask_buf = mask_f32
        owned_mask_upload = True
    h, w = src_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3

    # Working buffers
    dist = engine.allocate((h, w))
    boundary = engine.allocate((h, w))
    filled = engine.allocate((h, w))

    # Step 1: Initialize
    _mod("inpaint").run(
        "inpaint_init_distance_f32",
        mask=mask_buf,
        dist=dist,
        boundary=boundary,
        h=h,
        w=w,
    )
    _mod("inpaint").run(
        "inpaint_set_filled_f32", mask=mask_buf, filled=filled, h=h, w=w
    )

    # Step 2: Iterative dilation + inpainting
    max_level = int(max(h, w))
    for level in range(1, max_level + 1):
        dist2 = engine.allocate((h, w))
        _mod("inpaint").run(
            "inpaint_dilate_distance_f32",
            dist_in=dist,
            dist_out=dist2,
            h=h,
            w=w,
            current_level=float(level - 1),
        )
        copy_field(dist2, dist)
        dist2.destroy()

        if is_3d:
            _mod("inpaint").run(
                "inpaint_level_3ch_f32",
                src=src_buf,
                dist=dist,
                filled=filled,
                h=h,
                w=w,
                target_level=float(level),
                inpaint_radius=float(inpaint_radius),
            )
        else:
            _mod("inpaint").run(
                "inpaint_level_1ch_f32",
                src=src_buf,
                dist=dist,
                filled=filled,
                h=h,
                w=w,
                target_level=float(level),
                inpaint_radius=float(inpaint_radius),
            )

        _mod("inpaint").run(
            "inpaint_mark_filled_f32",
            dist=dist,
            filled=filled,
            h=h,
            w=w,
            target_level=float(level),
        )

    result = src_buf if return_gpu else src_buf.to_numpy()
    if owned_mask_upload:
        mask_buf.destroy()
    if owned_src_upload and not return_gpu:
        src_buf.destroy()
    return result


def seamless_clone_aot(
    src,
    dst_img,
    mask,
    center=(0, 0),
    flags=NORMAL_CLONE,
    max_iterations=200,
    return_gpu=False,
):
    """AOT Seamless Cloning (Poisson Image Editing)."""
    from taichi_vision.taichi_aot.capabilities import opengl_native_probe

    src_shape = getattr(src, "shape", ())
    dst_shape = getattr(dst_img, "shape", ())
    native_seamless_shape_safe = (
        len(src_shape) == 3
        and len(dst_shape) == 3
        and src_shape[-1] == 3
        and dst_shape[-1] == 3
    )
    if engine.arch.lower() in ("opengl", "gles") and (
        not native_seamless_shape_safe
        or os.environ.get("PIXEL_REFINE_AOT_NATIVE_SEAMLESS", "1") != "1"
        or not opengl_native_probe("seamless")
    ):
        import cv2

        source = src.to_numpy() if isinstance(src, TaichiGPUBuffer) else np.asarray(src)
        destination = (
            dst_img.to_numpy()
            if isinstance(dst_img, TaichiGPUBuffer)
            else np.asarray(dst_img)
        )
        source = np.ascontiguousarray(source)
        destination = np.ascontiguousarray(destination)
        if tuple(center) == (0, 0):
            center = (destination.shape[1] // 2, destination.shape[0] // 2)
        scale = (
            255.0
            if np.issubdtype(source.dtype, np.floating) and np.max(destination) <= 1.0
            else 1.0
        )
        src_u8 = (
            np.clip(source * scale, 0, 255).astype(np.uint8)
            if scale != 1.0 or source.dtype != np.uint8
            else source
        )
        dst_u8 = (
            np.clip(destination * scale, 0, 255).astype(np.uint8)
            if scale != 1.0 or destination.dtype != np.uint8
            else destination
        )
        mask_u8 = (
            mask.to_numpy()
            if isinstance(mask, TaichiGPUBuffer)
            else np.asarray(mask) > 0
        ).astype(np.uint8) * 255
        try:
            result = cv2.seamlessClone(
                src_u8, dst_u8, mask_u8, tuple(map(int, center)), int(flags)
            )
        except cv2.error:
            # OpenCV rejects degenerate/constant Poisson systems on some
            # versions. Preserve the documented image shape and semantics by
            # treating the operation as a no-op instead of leaking a backend
            # exception through the otherwise stable AOT API.
            result = dst_u8.copy()
        if np.issubdtype(destination.dtype, np.floating):
            result = result.astype(np.float32) / scale
        else:
            result = result.astype(destination.dtype, copy=False)
        return upload(np.ascontiguousarray(result)) if return_gpu else result

    is_gpu_src = isinstance(src, TaichiGPUBuffer)
    is_gpu_dst = isinstance(dst_img, TaichiGPUBuffer)
    src_buf = src if is_gpu_src else engine.upload(src)
    dst_buf = dst_img if is_gpu_dst else engine.upload(dst_img)
    # Override auto-detected is_vector for ndim=3 graphs
    if getattr(src_buf, "is_vector", False):
        src_buf = src_buf.view_as_vector(False)
    if getattr(dst_buf, "is_vector", False):
        dst_buf = dst_buf.view_as_vector(False)
    mask_buf = mask if isinstance(mask, TaichiGPUBuffer) else engine.upload(mask)
    owned_mask_buf = not isinstance(mask, TaichiGPUBuffer)
    # Seamless-clone graphs consume a normalized f32 mask.  Normalize common
    # OpenCV uint8 masks at the boundary so native dispatch does not fail on a
    # late graph-argument dtype mismatch.
    if np.dtype(mask_buf.dtype) != np.dtype(np.float32):
        mask_f32 = engine.upload(
            np.ascontiguousarray(mask_buf.to_numpy(), dtype=np.float32)
        )
        if owned_mask_buf:
            mask_buf.destroy()
        mask_buf = mask_f32
        owned_mask_buf = True
    h, w = dst_buf.shape[:2]

    # Copy destination to output (plain ndim=3, not vector)
    result = engine.allocate((h, w, 3))
    _mod("seamless_clone").run("seamless_copy_f32", s=dst_buf, d=result, h=h, w=w)

    # Grayscale source for MONOCHROME_TRANSFER
    if flags == MONOCHROME_TRANSFER:
        src_buf_copy = engine.allocate((h, w, 3))
        _mod("seamless_clone").run(
            "seamless_copy_f32", s=src_buf, d=src_buf_copy, h=h, w=w
        )
        gray = engine.allocate((h, w))
        _mod("seamless_clone").run(
            "seamless_to_grayscale_f32", s=src_buf_copy, g=gray, h=h, w=w
        )
        # Create 3ch grayscale source
        src_buf = engine.allocate((h, w, 3))
        for c in range(3):
            _mod("seamless_clone").run(
                "seamless_init_f_channel_f32",
                dst_arr=src_buf,
                f_arr=gray,
                h=h,
                w=w,
                c=c,
            )
        engine.sync()
        gray.destroy()
        src_buf_copy.destroy()

    # Solve per channel
    for ch in range(3):
        div_x = engine.allocate((h, w))
        div_y = engine.allocate((h, w))
        lap = engine.allocate((h, w))

        # Compute divergence
        if flags == MIXED_CLONE:
            _mod("seamless_clone").run(
                "seamless_divergence_mixed_f32",
                src=src_buf,
                dst=result,
                div_x=div_x,
                div_y=div_y,
                h=h,
                w=w,
                ch=ch,
            )
        else:
            _mod("seamless_clone").run(
                "seamless_divergence_normal_f32",
                src=src_buf,
                div_x=div_x,
                div_y=div_y,
                h=h,
                w=w,
                ch=ch,
            )

        # Compute Laplacian of divergence
        _mod("seamless_clone").run(
            "seamless_laplacian_f32", div_x=div_x, div_y=div_y, lap=lap, h=h, w=w
        )

        # Initialize f from destination channel
        f_in = engine.allocate((h, w))
        f_out = engine.allocate((h, w))
        _mod("seamless_clone").run(
            "seamless_init_f_channel_f32", dst_arr=result, f_arr=f_in, h=h, w=w, ch=ch
        )

        # Jacobi iteration
        for _ in range(max_iterations):
            _mod("seamless_clone").run(
                "seamless_jacobi_step_f32",
                f_in=f_in,
                f_out=f_out,
                lap=lap,
                mask=mask_buf,
                h=h,
                w=w,
            )
            copy_field(f_out, f_in)

        # Composite
        _mod("seamless_clone").run(
            "seamless_composite_f32",
            f=f_in,
            dst_out=result,
            mask=mask_buf,
            h=h,
            w=w,
            ch=ch,
        )

        # Cleanup
        engine.sync()
        div_x.destroy()
        div_y.destroy()
        lap.destroy()
        f_in.destroy()
        f_out.destroy()

    output = result if return_gpu else result.to_numpy()
    if owned_mask_buf:
        mask_buf.destroy()
    return output


# ---------------------------------------------------------------------------
# Farneback Optical Flow (AOT)
# ---------------------------------------------------------------------------


@_vulkan_host_accessible
def farneback_flow(
    ref_gray,
    comp_gray,
    pyr_scale=0.5,
    num_levels=3,
    win_size=15,
    num_iters=3,
    poly_n=5,
    poly_sigma=1.2,
    flags=0,
    flow_init=None,
    return_gpu=False,
):
    if str(getattr(engine, "arch", "")).lower() in ("opengl", "gles"):
        from taichi_vision.taichi_algorithm import aot_wrapper as _flow_wrapper

        _flow_wrapper._prepare_opengl_flow_family("farneback")
    # Strategy A + C: Decoupling for High-Res (>= 8MP, e.g. 12MP) to prevent OOM
    h, w = ref_gray.shape[:2]
    if h * w >= 8_000_000 and flow_init is None and h >= 64 and w >= 64:
        try:
            from taichi_vision.taichi_algorithm.aot_wrapper import _get_module, _InputArray, _OutputArray
            pyramid_mod = _get_module("pyramid")
            prev_dev = _InputArray(ref_gray if hasattr(ref_gray, "handle") else ref_gray.astype(np.float32))
            next_dev = _InputArray(comp_gray if hasattr(comp_gray, "handle") else comp_gray.astype(np.float32))
            half_h, half_w = h // 2, w // 2
            ref_half = _OutputArray((half_h, half_w), np.float32)
            supp_half = _OutputArray((half_h, half_w), np.float32)
            pyramid_mod.run("downsample_2x_f32", src=prev_dev, dst=ref_half)
            pyramid_mod.run("downsample_2x_f32", src=next_dev, dst=supp_half)
            flow_half = farneback_flow(
                ref_half.to_numpy(),
                supp_half.to_numpy(),
                pyr_scale=pyr_scale,
                num_levels=max(1, int(num_levels) - 1),
                win_size=win_size,
                num_iters=num_iters,
                poly_n=poly_n,
                poly_sigma=poly_sigma,
                flags=flags,
                return_gpu=True,
            )
            flow_full = _OutputArray((h, w, 2), np.float32)
            pyramid_mod.run("upsample_flow_f32", src=flow_half, dst=flow_full, scale=2.0)
            return flow_full if return_gpu else flow_full.to_numpy()
        except Exception:
            pass # fallback to tiled execution

    if (
        not return_gpu
        and flow_init is None
        and isinstance(ref_gray, np.ndarray)
        and isinstance(comp_gray, np.ndarray)
    ):
        scale = max(1.0, 1.0 / max(float(pyr_scale), 1e-6))
        local_radius = poly_n // 2 + win_size // 2 * max(1, int(num_iters)) + 4
        halo = int(np.ceil(local_radius * scale ** max(0, int(num_levels) - 1)))
        backend = str(getattr(engine, "arch", "")).lower()
        if backend in {"vulkan", "cuda"}:
            gpu_result = _run_blockwise_gpu(
                "farneback_flow",
                (np.ascontiguousarray(ref_gray), np.ascontiguousarray(comp_gray)),
                (*ref_gray.shape[:2], 2),
                np.float32,
                lambda ref_tile, comp_tile: _farneback_flow_full(
                    ref_tile,
                    comp_tile,
                    pyr_scale,
                    num_levels,
                    win_size,
                    num_iters,
                    poly_n,
                    poly_sigma,
                    flags,
                    return_gpu=True,
                ),
                halo=halo,
                params={
                    "pyr_scale": float(pyr_scale),
                    "levels": int(num_levels),
                    "win_size": int(win_size),
                    "iters": int(num_iters),
                    "poly_n": int(poly_n),
                    "poly_sigma": float(poly_sigma),
                    "flags": int(flags),
                    "gpu_tile": True,
                },
                validate_output=lambda output, _tiles: (
                    output.ndim == 3
                    and output.shape[2] == 2
                    and np.isfinite(output).all()
                ),
                resident_multiplier=16,
                batch_cap=2,
            )
            if gpu_result is not None:
                return gpu_result
        result = _run_blockwise(
            "farneback_flow",
            (np.ascontiguousarray(ref_gray), np.ascontiguousarray(comp_gray)),
            (*ref_gray.shape[:2], 2),
            np.float32,
            lambda ref_tile, comp_tile: _farneback_flow_full(
                ref_tile,
                comp_tile,
                pyr_scale,
                num_levels,
                win_size,
                num_iters,
                poly_n,
                poly_sigma,
                flags,
            ),
            halo=halo,
            params={
                "pyr_scale": float(pyr_scale),
                "levels": int(num_levels),
                "win_size": int(win_size),
                "iters": int(num_iters),
                "poly_n": int(poly_n),
                "poly_sigma": float(poly_sigma),
                "flags": int(flags),
            },
            validate_output=lambda output, _tiles: (
                output.ndim == 3 and output.shape[2] == 2 and np.isfinite(output).all()
            ),
        )
        if result is not None:
            return result
    result = _farneback_flow_full(
        ref_gray,
        comp_gray,
        pyr_scale,
        num_levels,
        win_size,
        num_iters,
        poly_n,
        poly_sigma,
        flags,
        flow_init,
        return_gpu,
    )
    if return_gpu and str(getattr(engine, "arch", "")).lower() in ("opengl", "gles"):
        from taichi_vision.taichi_algorithm import aot_wrapper as _flow_wrapper

        _flow_wrapper._register_opengl_flow_output(result)
    return result


def _farneback_flow_full(
    ref_gray,
    comp_gray,
    pyr_scale=0.5,
    num_levels=3,
    win_size=15,
    num_iters=3,
    poly_n=5,
    poly_sigma=1.2,
    flags=0,
    flow_init=None,
    return_gpu=False,
):
    """
    AOT Farneback Dense Optical Flow (OpenCV-compatible).

    Computes a dense flow field from ref_gray to comp_gray.

    Parameters
    ----------
    ref_gray  : ndarray (H, W) float32 – reference frame [0, 255].
    comp_gray : ndarray (H, W) float32 – comparison frame [0, 255].
    pyr_scale : float – pyramid scale factor (default 0.5).
    num_levels: int   – number of pyramid levels (default 3).
    win_size  : int   – smoothing window size (default 15).
    num_iters : int   – iterations per pyramid level (default 3).
    poly_n    : int   – polynomial expansion neighborhood (default 5).
    poly_sigma: float – polynomial expansion sigma (default 1.2).
    flags     : int   – reserved.
    flow_init : ndarray (H,W,2) or TaichiGPUBuffer – optional initial flow.
    return_gpu: bool  – if True, return TaichiGPUBuffer; else np.ndarray.

    Returns
    -------
    flow : (H, W, 2) float32 – flow field where flow[:,:,0]=dx, flow[:,:,1]=dy.
    """
    from taichi_vision.taichi_algorithm.optical_flow.farneback_flow import (
        prepare_gaussian_constants,
        compute_smoothing_weights,
    )

    # Upload images
    ref_buf = InputArray(ref_gray)
    comp_buf = InputArray(comp_gray)
    h_orig, w_orig = ref_buf.shape[:2]

    # Build pyramids
    downscale_factor = 1.0 / pyr_scale
    if not np.isclose(downscale_factor, 2.0):
        raise ValueError("AOT Farneback currently requires pyr_scale=0.5")

    def _build_flow_pyramid(source):
        pyramid = [source]
        for _ in range(max(0, int(num_levels) - 1)):
            h_prev, w_prev = pyramid[-1].shape[:2]
            h_next, w_next = h_prev // 2, w_prev // 2
            if h_next < 32 or w_next < 32:
                break
            level = engine.allocate((h_next, w_next), dtype=np.float32)
            _mod("pyramid").run("downsample_2x_f32", src=pyramid[-1], dst=level)
            pyramid.append(level)
        return pyramid

    ref_pyr = _build_flow_pyramid(ref_buf)
    comp_pyr = _build_flow_pyramid(comp_buf)
    actual_levels = len(ref_pyr)

    # Pre-compute constants on CPU, upload to GPU
    g_w, xg_w, xxg_w, ig11, ig03, ig33, ig55 = prepare_gaussian_constants(
        poly_n, poly_sigma
    )
    smooth_w, smooth_radius = compute_smoothing_weights(win_size)
    poly_radius = poly_n // 2

    poly_weights_gpu = InputArray(
        np.ascontiguousarray(np.stack((g_w, xg_w, xxg_w), axis=1), dtype=np.float32)
    )
    # The compiled graph ABI uses one ``poly_weights`` matrix on every
    # backend (the three columns are g, x*g, and x*x*g).  Older host code
    # passed separate g/xg/xxg buffers on CPU/OpenGL, which left the required
    # poly_weights argument unset and caused ``Missing runtime value`` at
    # graph initialization.  Keep one descriptor layout for CPU, CUDA,
    # Vulkan, and OpenGL; it also reduces three uploads to one.
    smooth_gpu = InputArray(smooth_w[: smooth_radius + 1])

    mod = _mod("farneback_flow")
    if mod is None:
        raise RuntimeError("farneback_flow TCM not found in aot_tcm/")

    # Coarse-to-fine
    prev_flow = None
    for lvl in range(actual_levels - 1, -1, -1):
        ref_lvl = ref_pyr[lvl]
        comp_lvl = comp_pyr[lvl]
        hl, wl = ref_lvl.shape[0], ref_lvl.shape[1]

        flow_buf = engine.allocate((hl, wl, 2), dtype=np.float32)

        # Scratch buffers are also valid for the fused level graph because
        # every graph dispatch in the sequence is ordered by the runtime.
        vert_buf = engine.allocate((hl, wl, 3), dtype=np.float32)
        R0 = engine.allocate((hl, wl, 5), dtype=np.float32)
        R1 = engine.allocate((hl, wl, 5), dtype=np.float32)
        M = engine.allocate((hl, wl, 5), dtype=np.float32)
        M_smooth = engine.allocate((hl, wl, 5), dtype=np.float32)

        # A/B qualification on the current desktop showed a small gain on
        # CPU/CUDA but a regression on OpenGL/Vulkan, so graph fusion is
        # selected per backend rather than applied unconditionally.
        fused_level = int(num_iters) == 3 and str(
            getattr(engine, "arch", "")
        ).lower() in {"cpu", "cuda"}
        fused_level_name = (
            "farneback_level_clear_3"
            if prev_flow is None
            else "farneback_level_upsample_3"
        )
        fused_args = dict(
            ref=ref_lvl,
            comp=comp_lvl,
            vert=vert_buf,
            R0=R0,
            R1=R1,
            M=M,
            M_smooth=M_smooth,
            h=hl,
            w=wl,
            poly_weights=poly_weights_gpu,
            ig11=float(ig11),
            ig03=float(ig03),
            ig33=float(ig33),
            ig55=float(ig55),
            poly_radius=poly_radius,
            smooth_weights=smooth_gpu,
            smooth_radius=smooth_radius,
        )
        if prev_flow is None:
            fused_args["flow"] = flow_buf
        else:
            fused_args.update(
                {
                    "flow": flow_buf,
                    "flow_coarse": prev_flow,
                    "flow_fine": flow_buf,
                    "scale": float(ref_lvl.shape[0]) / float(prev_flow.shape[0]),
                }
            )

        fused_used = False
        if fused_level:
            try:
                mod.run(fused_level_name, **fused_args)
                fused_used = True
            except Exception as exc:
                # Older artifacts remain usable through the exact direct
                # sequence below; this is a same-backend recovery path.
                print(
                    f"[AOT Farneback] {fused_level_name} unavailable; "
                    f"using direct dispatch: {exc}"
                )

        if not fused_used:
            if prev_flow is not None:
                mod.run(
                    "farneback_upsample_flow",
                    flow_coarse=prev_flow,
                    flow_fine=flow_buf,
                    scale=fused_args.get("scale", 1.0),
                )
            else:
                mod.run("farneback_clear_flow", flow=flow_buf)

            poly_args = dict(
                vert=vert_buf,
                h=hl,
                w=wl,
                poly_weights=poly_weights_gpu,
                ig11=float(ig11),
                ig03=float(ig03),
                ig33=float(ig33),
                ig55=float(ig55),
                poly_radius=poly_radius,
            )
            mod.run(
                "poly_expansion_f32",
                src=ref_lvl,
                poly=R0,
                **poly_args,
            )
            mod.run(
                "poly_expansion_f32",
                src=comp_lvl,
                poly=R1,
                **poly_args,
            )

            # Choose batched multi-iteration graph for efficiency.
            iter_args = dict(
                R0=R0,
                R1=R1,
                flow=flow_buf,
                M=M,
                M_smooth=M_smooth,
                h=hl,
                w=wl,
                smooth_weights=smooth_gpu,
                smooth_radius=smooth_radius,
            )
            remaining = num_iters
            while remaining > 0:
                if remaining >= 5:
                    batch_key = "farneback_multi_5"
                    batch_size = 5
                elif remaining >= 3:
                    batch_key = "farneback_multi_3"
                    batch_size = 3
                elif remaining >= 2:
                    batch_key = "farneback_multi_2"
                    batch_size = 2
                else:
                    batch_key = "farneback_iteration"
                    batch_size = 1
                try:
                    mod.run(batch_key, **iter_args)
                except Exception:
                    # Fallback to single iteration if batch graph not found.
                    mod.run("farneback_iteration", **iter_args)
                remaining -= batch_size

        if str(getattr(engine, "arch", "")).lower() in ("opengl", "gles"):
            engine.sync()

        R0.destroy()
        R1.destroy()
        M.destroy()
        M_smooth.destroy()

        if prev_flow is not None and lvl < actual_levels - 1:
            prev_flow.destroy()
        prev_flow = flow_buf

    engine.sync()
    result = prev_flow

    # Cleanup pyramid buffers (except level 0 which shares ref/comp_buf)
    for lvl_buf in ref_pyr[1:]:
        lvl_buf.destroy()
    for lvl_buf in comp_pyr[1:]:
        lvl_buf.destroy()
    for buf in (poly_weights_gpu, smooth_gpu):
        if buf is not None:
            try:
                buf.destroy()
            except Exception:
                pass

    return result if return_gpu else result.to_numpy()


# ===========================================================================
# AOT Dispatch: BM3D (Hybrid Fast Collaborative Denoising)
# ===========================================================================
def bm3d(
    src,
    sigma,
    block_size=8,
    search_radius=15,
    max_matches=16,
    lambda_3d=2.7,
    cycle_spins=1,
    return_gpu=False,
):
    """
    Taichi AOT BM3D Denoising (Hybrid Fast Collaborative Denoising).

    Self-contained — no external fallback. Handles edge cases internally.
    Supports: uint8, uint16, float32 | grayscale (H,W), RGB (H,W,3).

    Pipeline per spin:
      1. Zero output + weight_sum buffers
      2. Block matching (brute-force L2 + Top-K)
      3. 2D DCT hard thresholding per group
      4. Weighted overlap-add aggregation
      5. Normalize output
    """
    is_numpy = isinstance(src, np.ndarray)
    orig_dtype = src.dtype if is_numpy else np.float32

    # --- Auto-cast dtype ---
    if is_numpy and src.dtype == np.uint8:
        src = src.astype(np.float32) / 255.0
        sigma = float(sigma) / 255.0
    elif is_numpy and src.dtype == np.uint16:
        src = src.astype(np.float32) / 65535.0
        sigma = float(sigma) / 65535.0
    else:
        sigma = float(sigma)

    # --- Auto-repair: sanitize ---
    if is_numpy and src.dtype in (np.float32, np.float64):
        if np.any(np.isnan(src)) or np.any(np.isinf(src)):
            src = np.nan_to_num(src, nan=0.0, posinf=1.0, neginf=0.0).astype(np.float32)
    if is_numpy:
        src = np.ascontiguousarray(src, dtype=np.float32)
        src = np.clip(src, 0.0, 1.0)

    # --- Validate sigma ---
    if not np.isfinite(sigma) or sigma <= 0:
        if return_gpu:
            return InputArray(src) if is_numpy else src
        return src.copy() if is_numpy else src.to_numpy()

    # --- Handle multi-channel (RGB) ---
    if len(src.shape) == 3 and src.shape[2] == 3:
        h, w = src.shape[:2]
        result_np = np.zeros((h, w, 3), dtype=np.float32)
        for c in range(3):
            ch_np = np.ascontiguousarray(src[:, :, c], dtype=np.float32)
            result_np[:, :, c] = bm3d(
                ch_np,
                sigma,
                block_size=block_size,
                search_radius=search_radius,
                max_matches=max_matches,
                lambda_3d=lambda_3d,
                cycle_spins=cycle_spins,
                return_gpu=False,
            )
        if orig_dtype == np.uint8:
            return np.clip(result_np * 255.0, 0, 255).astype(np.uint8)
        elif orig_dtype == np.uint16:
            return np.clip(result_np * 65535.0, 0, 65535).astype(np.uint16)
        return result_np

    # --- Single channel processing ---
    H, W = src.shape[:2]
    N = min(block_size, H, W)
    search_radius = min(search_radius, max(1, min(H, W) // 2))
    max_area = (2 * search_radius + 1) ** 2
    K = min(max_matches, max(1, max_area), 32)

    step = N
    ref_positions_list = []
    for ry in range(0, H - N + 1, step):
        for rx in range(0, W - N + 1, step):
            ref_positions_list.append((ry, rx))
    num_refs = len(ref_positions_list)

    if num_refs == 0:
        if return_gpu:
            return InputArray(src) if is_numpy else src
        return src.copy() if is_numpy else src.to_numpy()

    src_np = np.ascontiguousarray(src, dtype=np.float32)
    src_buf = InputArray(src_np)
    ref_pos_np = np.array(ref_positions_list, dtype=np.int32)
    ref_pos_buf = InputArray(ref_pos_np)

    from taichi_vision.taichi_algorithm.denoising.bm3d import _get_dct_matrix

    T_np = _get_dct_matrix(N)
    T_buf = InputArray(T_np)

    groups_buf = OutputArray((num_refs, K, N, N), dtype=np.float32)
    match_y_buf = OutputArray((num_refs, K), dtype=np.int32)
    match_x_buf = OutputArray((num_refs, K), dtype=np.int32)
    valid_buf = (
        None
        if engine.arch.lower() == "vulkan"
        else OutputArray((num_refs, K), dtype=np.int32)
    )
    filtered_buf = OutputArray((num_refs, K, N, N), dtype=np.float32)
    weights_buf = OutputArray((num_refs,), dtype=np.float32)
    temp_buf = OutputArray((num_refs, K, N, N), dtype=np.float32)
    output_buf = OutputArray((H, W), dtype=np.float32)
    wsum_buf = OutputArray((H, W), dtype=np.float32)
    final_buf = OutputArray((H, W), dtype=np.float32)

    mod = _mod("bm3d")
    mod.run("bm3d_zero_f32", dst=final_buf, H=H, W=W)

    for spin in range(cycle_spins):
        shift_x = (spin * N // 2) % W if spin > 0 else 0
        shift_y = (spin * N // 2) % H if spin > 0 else 0

        mod.run("bm3d_zero_f32", dst=output_buf, H=H, W=W)
        mod.run("bm3d_zero_f32", dst=wsum_buf, H=H, W=W)

        if shift_x != 0 or shift_y != 0:
            shifted_buf = OutputArray((H, W), dtype=np.float32)
            mod.run(
                "bm3d_shift_f32",
                src=src_buf,
                dst=shifted_buf,
                H=H,
                W=W,
                sy=shift_y,
                sx=shift_x,
            )
            work_buf = shifted_buf
        else:
            work_buf = src_buf

        block_args = {
            "src": work_buf,
            "groups": groups_buf,
            "match_y": match_y_buf,
            "match_x": match_x_buf,
            "ref_positions": ref_pos_buf,
            "num_refs": num_refs,
            "K": K,
            "N": N,
            "search_r": search_radius,
            "H": H,
            "W": W,
        }
        if valid_buf is not None:
            block_args["valid_mask"] = valid_buf
        mod.run("bm3d_block_match_f32", **block_args)

        mod.run(
            "bm3d_dct_filter_f32",
            groups=groups_buf,
            filtered=filtered_buf,
            group_weights=weights_buf,
            T_dct=T_buf,
            temp_buf=temp_buf,
            num_refs=num_refs,
            K=K,
            N=N,
            sigma=sigma,
            lambda_3d=lambda_3d,
        )

        aggregate_args = {
            "filtered": filtered_buf,
            "group_weights": weights_buf,
            "match_y": match_y_buf,
            "match_x": match_x_buf,
            "output": output_buf,
            "weight_sum": wsum_buf,
            "num_refs": num_refs,
            "K": K,
            "N": N,
            "H": H,
            "W": W,
        }
        if valid_buf is not None:
            aggregate_args["valid_mask"] = valid_buf
        mod.run("bm3d_aggregate_f32", **aggregate_args)

        mod.run(
            "bm3d_normalize_f32",
            output=output_buf,
            weight_sum=wsum_buf,
            src=work_buf,
            H=H,
            W=W,
        )

        if shift_x != 0 or shift_y != 0:
            unshifted_buf = OutputArray((H, W), dtype=np.float32)
            mod.run(
                "bm3d_shift_f32",
                src=output_buf,
                dst=unshifted_buf,
                H=H,
                W=W,
                sy=-shift_y,
                sx=-shift_x,
            )
            mod.run("bm3d_accumulate_f32", dst=final_buf, src=unshifted_buf, H=H, W=W)
            shifted_buf.destroy()
            unshifted_buf.destroy()
        else:
            mod.run("bm3d_accumulate_f32", dst=final_buf, src=output_buf, H=H, W=W)

    if cycle_spins > 1:
        mod.run("bm3d_scale_f32", data=final_buf, scale=1.0 / cycle_spins, H=H, W=W)

    for buf in [
        groups_buf,
        match_y_buf,
        match_x_buf,
        valid_buf,
        filtered_buf,
        weights_buf,
        temp_buf,
        output_buf,
        wsum_buf,
    ]:
        if buf is not None:
            buf.destroy()

    if return_gpu:
        return final_buf

    result = final_buf.to_numpy()
    if orig_dtype == np.uint8:
        return np.clip(result * 255.0, 0, 255).astype(np.uint8)
    elif orig_dtype == np.uint16:
        return np.clip(result * 65535.0, 0, 65535).astype(np.uint16)
    return result


def _dense_flow_blockwise(
    operation,
    prev,
    next,
    run_tile,
    halo,
    params,
    gpu_run_tile=None,
):
    if not isinstance(prev, np.ndarray) or not isinstance(next, np.ndarray):
        return None
    if prev.shape[:2] != next.shape[:2]:
        raise ValueError("optical-flow frames must have matching dimensions")
    if gpu_run_tile is not None and str(getattr(engine, "arch", "")).lower() in {
        "vulkan",
        "cuda",
        "cpu",
    }:
        result = _run_blockwise_gpu(
            operation,
            (np.ascontiguousarray(prev), np.ascontiguousarray(next)),
            (*prev.shape[:2], 2),
            np.float32,
            gpu_run_tile,
            halo=halo,
            params=params,
            validate_output=lambda output, _tiles: (
                output.ndim == 3 and output.shape[2] == 2 and np.isfinite(output).all()
            ),
            resident_multiplier=16,
            batch_cap=2,
        )
        if result is not None:
            return result
    return _run_blockwise(
        operation,
        (np.ascontiguousarray(prev), np.ascontiguousarray(next)),
        (*prev.shape[:2], 2),
        np.float32,
        run_tile,
        halo=halo,
        params=params,
        validate_output=lambda output, _tiles: (
            output.ndim == 3 and output.shape[2] == 2 and np.isfinite(output).all()
        ),
    )


def _pipeline_graph_specs(
    names,
    shape,
    *,
    operation="lucas_kanade",
    source="aot_pipeline",
    resident_multiplier=16,
    reads=(),
    writes=(),
    force_boundary_indices=(),
    backend_safe=True,
    metadata=None,
    module_key=None,
    module_keys=None,
):
    """Attach a conservative resident estimate to a native graph sequence.

    The bridge still receives the original graph names.  ``GraphSpec`` is only
    planner metadata; it prevents the automatic recorder from treating an
    unqualified string as a zero-byte graph while retaining a direct fallback
    whenever the estimate or runtime allocation does not fit.
    """
    names = tuple(str(name) for name in names)
    try:
        from taichi_vision.taichi_aot.auto_pipeline import GraphSpec

        shape_tuple = tuple(max(1, int(value)) for value in shape)
        pixels = max(1, int(np.prod(shape_tuple, dtype=np.int64)))
        # Estimate a bounded number of resident f32 planes per graph.  This is
        # deliberately a budget hint rather than a claim about exact native
        # allocations: the engine performs a second admission check against
        # actual live buffers before recording each graph.  ``resident_multiplier``
        # is kept conservative for the existing LK path and can be lowered for
        # a small, well-understood map chain.
        multiplier = max(1, int(resident_multiplier))
        per_graph_bytes = max(4096, pixels * 4 * multiplier)
        boundary_indices = {int(index) for index in force_boundary_indices}
        common_metadata = {
            "source": source,
            "shape": shape_tuple,
            "estimate_kind": "conservative_per_graph",
            # Planner telemetry is not device queue/fence evidence. Keep this
            # marker next to the metadata so diagnostics cannot accidentally
            # promote an automatic recording into an overlap claim.
            "overlap_verified": False,
        }
        if metadata:
            common_metadata.update(dict(metadata))
        if module_keys is not None:
            resolved_modules = tuple(module_keys)
            if len(resolved_modules) != len(names):
                raise ValueError("module_keys must match graph names length")
        else:
            resolved_modules = tuple(module_key for _ in names)
        return tuple(
            GraphSpec(
                name=str(name),
                resident_bytes=per_graph_bytes,
                reads=tuple(reads),
                writes=tuple(writes),
                backend_safe=bool(backend_safe),
                force_boundary=index in boundary_indices,
                operation=operation,
                module_key=resolved_modules[index],
                metadata=dict(common_metadata, graph_index=index),
            )
            for index, name in enumerate(names)
        )
    except Exception:
        return tuple(str(name) for name in names)


def _run_auto_graph_sequence(
    names,
    shape,
    runner,
    *,
    operation,
    source,
    resident_multiplier=16,
    reads=(),
    writes=(),
    force_boundary_indices=(),
    metadata=None,
    module_key=None,
    module_keys=None,
    retry_prepare=None,
    retain_buffers=(),
):
    """Run a deterministic native graph sequence through the auto planner.

    ``runner`` is intentionally called once in the normal case.  If command
    recording is rejected by a driver or the adaptive resident admission gate,
    the failed scope is dropped by :meth:`AOTEngine.auto_pipeline` and the same
    runner is called again directly on the same backend.  This keeps recording
    an optimization rather than a correctness dependency, without changing
    any public algorithm signature.  No overlap is inferred from this helper;
    the planner decision used inside the scope retains the canonical
    ``overlap_verified=False`` value.
    """
    names = tuple(str(name) for name in names)
    specs = _pipeline_graph_specs(
        names,
        shape,
        operation=operation,
        source=source,
        resident_multiplier=resident_multiplier,
        reads=reads,
        writes=writes,
        force_boundary_indices=force_boundary_indices,
        metadata=metadata,
        module_key=module_key,
        module_keys=module_keys,
    )
    # Give this one-shot scope a stable private name so that buffers needed by
    # the caller can be detached before the recorder tears down its private
    # intermediates.  The graph order remains the only native contract.
    scope_name = "__auto_api_{}_{}".format(
        str(operation).replace(" ", "_"),
        abs(hash((source, names, tuple(shape)))) & 0xFFFFFFFF,
    )
    plan = None
    try:
        with engine.auto_pipeline(specs, name=scope_name) as plan:
            result = runner()
            if getattr(plan, "is_recorded", False) and retain_buffers:
                with engine._lock:
                    intermediates = engine._pipeline_intermediates.get(scope_name, [])
                    for buffer in tuple(retain_buffers):
                        if buffer is None:
                            continue
                        try:
                            intermediates.remove(buffer)
                        except ValueError:
                            pass
                        try:
                            buffer.associated_pipelines.discard(scope_name)
                            buffer.is_pipeline_intermediate = False
                        except Exception:
                            pass
            return_value = result
        # These are one-shot recordings, unlike the legacy public pipeline
        # API.  Clear their native graph after the single submission while
        # retaining only the explicitly detached result buffers.
        if getattr(plan, "is_recorded", False):
            try:
                engine.clear_pipeline_by_name(scope_name)
            except Exception as cleanup_error:
                # Cleanup must not turn a completed native result into a
                # second computation.  The engine's normal teardown path will
                # retry the bounded native clear if needed.
                print(
                    f"[AOTEngine Pipeline] unable to clear one-shot scope "
                    f"{scope_name}: {cleanup_error}"
                )
        return return_value
    except Exception as exc:
        # The native graph sequence is still the established full-frame path;
        # retry it directly after the recorder has torn down its state.  Do not
        # substitute a CPU implementation or hide the original error if the
        # direct same-backend retry also fails.
        error_name = type(exc).__name__.strip().lower().lstrip("_")
        error_message = str(exc).strip().lower()
        if (
            "cancel" in error_name
            or "cancel" in error_message
            or "runtime generation" in error_message
            or "was invalidated" in error_message
        ):
            # Cancellation and stale-generation failures are lifecycle
            # decisions, not recorder capability failures.  Retrying here
            # would undo cancellation or submit old handles a second time.
            raise
        print(
            f"[AOTEngine Pipeline] {operation} automatic recording failed; "
            f"using direct same-backend dispatch: {exc}"
        )
        if retry_prepare is not None:
            retry_prepare()
        return runner()


def _lucas_kanade_pipeline_graphs(shape, kwargs):
    """Return the static LK graph order for one block-sized invocation.

    A tile call normally submits several independent AOT graphs (pyramid,
    tracking, and interpolation).  When the graph order is deterministic we
    can record that sequence and submit it once.  Diagnostic/``auto`` mode is
    intentionally left on the direct path because it may insert a stats pass
    and a high-motion rerun after inspecting device output.
    """
    if kwargs.get("return_diagnostics", False):
        return None
    motion_mode = str(kwargs.get("motion_mode", "fast") or "fast").lower()
    if motion_mode == "auto":
        return None
    if kwargs.get("prevPts") is not None:
        return None

    height, width = (int(shape[0]), int(shape[1]))
    max_level = max(0, int(kwargs.get("maxLevel", 2)))
    level_shapes = [(height, width)]
    for _level in range(1, max_level + 1):
        src_h, src_w = level_shapes[-1]
        dst_h, dst_w = src_h // 2, src_w // 2
        if dst_h < 32 or dst_w < 32:
            break
        level_shapes.append((dst_h, dst_w))

    dense_mode = str(kwargs.get("dense_mode", "smooth") or "smooth").lower()
    if dense_mode in {
        "blocky_clamped",
        "clamped",
        "cpu_like_clamped",
        "cpu-like-clamped",
    }:
        dense_graph = "flow_lk_dense_blocky_clamped"
    elif dense_mode in {"blocky", "nearest", "cpu_like", "cpu-like"}:
        dense_graph = "flow_lk_dense_blocky"
    else:
        dense_graph = "flow_lk_dense_interpolate"

    graphs = []
    # Pyramid construction is performed from finest to coarsest before the
    # coarse-to-fine tracking loop, exactly matching aot_wrapper.py.
    graphs.extend("downsample_2x_f32" for _ in range(2 * (len(level_shapes) - 1)))
    for level in range(len(level_shapes) - 1, -1, -1):
        if level == len(level_shapes) - 1:
            graphs.append("flow_lk_zero")
        else:
            graphs.append("upsample_flow_f32")
        graphs.append("flow_lk_grid_track")
        if bool(kwargs.get("adaptive", False)) and level == 0:
            graphs.append("flow_lk_adaptive_refine")
        graphs.append(dense_graph)
    # Bare graph names do not carry a footprint, so the automatic planner
    # deliberately refuses to record them.  Attach a conservative per-graph
    # resident estimate here instead of reintroducing a hand-written
    # ``rec_pipeline`` decision.  The estimate is only a budget hint: the
    # runtime still aborts recording if actual allocations exceed the
    # adaptive resident limit and continues through the same-backend direct
    # path.  Keeping this conversion local preserves the public API and lets
    # all graph names remain unchanged for the native bridge.
    module_keys = tuple(
        (
            "pyramid"
            if str(graph).startswith(("downsample", "upsample"))
            else "lucas_kanade"
        )
        for graph in graphs
    )
    return _pipeline_graph_specs(
        graphs,
        (height, width),
        operation="lucas_kanade",
        source="lucas_kanade_tile",
        module_keys=module_keys,
    )


def _run_lucas_kanade_gpu_tile(prev_tile, next_tile, kwargs):
    """Execute one LK block through a recorded graph sequence when safe."""
    from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLK

    pipeline_graphs = _lucas_kanade_pipeline_graphs(prev_tile.shape, kwargs)
    if os.environ.get("PIXEL_REFINE_AOT_DISABLE_BLOCK_PIPELINE") == "1":
        pipeline_graphs = None
    if pipeline_graphs:
        # Load the producer modules before the recorder is entered.  This lets
        # the native bridge clear/associate the pipeline with a real module
        # even on a cold tile, while keeping all buffers owned by the normal
        # AOT wrapper and its retirement pool.
        _mod("lucas_kanade")
        _mod("pyramid")
        tracker = getattr(
            getattr(engine, "_local", None),
            "block_execution_tracker",
            None,
        )
        try:
            with engine.auto_pipeline(pipeline_graphs) as pipeline_plan:
                if tracker is not None and getattr(pipeline_plan, "is_recorded", False):
                    tracker.pipeline_submissions += 1
                    tracker.pipeline_graphs += len(pipeline_graphs)
                output = calcOpticalFlowPyrLK(
                    prev_tile, next_tile, **dict(kwargs, return_gpu=True)
                )
                # ``calcOpticalFlowPyrLK`` owns several temporary buffers
                # whose destructors clear the recorded pipeline. Detach the
                # returned flow before those destructors run; otherwise the
                # final flow handle is reclaimed with the intermediates.
                pipeline_name = engine.current_pipeline
                if pipeline_name and hasattr(output, "handle"):
                    with engine._lock:
                        intermediates = engine._pipeline_intermediates.get(
                            pipeline_name, []
                        )
                        try:
                            intermediates.remove(output)
                        except ValueError:
                            pass
                        output.associated_pipelines.discard(pipeline_name)
                        output.is_pipeline_intermediate = False
                return output
        except Exception as pipeline_error:
            # Recording is an optimization, never a correctness requirement.
            # A driver that rejects command recording must still receive the
            # established direct graph sequence for this tile.
            print(
                "[LucasKanadeGPU] recorded block pipeline failed; "
                f"using direct graph dispatch: {pipeline_error}"
            )
    return calcOpticalFlowPyrLK(prev_tile, next_tile, **dict(kwargs, return_gpu=True))


def _run_lucas_kanade_batch_blocks(prev, next, kwargs, halo):
    """Process same-shaped LK tiles as one native batch.

    This is intentionally a separate executor from ``_run_blockwise_gpu``:
    the latter preserves the one-tile callback contract for every algorithm,
    while this path packs a bounded number of tiles into ``(N,H,W)`` and
    ``(N,H,W,2)`` buffers.  The batch size remains governor-controlled, so
    reducing dispatch count cannot turn into an unbounded VRAM reservation.
    """
    backend = str(getattr(engine, "arch", "")).lower()
    if os.environ.get("PIXEL_REFINE_AOT_DISABLE_LK_BATCH") == "1":
        return None
    if backend not in {"cpu", "vulkan", "cuda"}:
        return None
    if not isinstance(prev, np.ndarray) or not isinstance(next, np.ndarray):
        return None
    if prev.ndim != 2 or next.ndim != 2 or prev.shape != next.shape:
        return None
    if kwargs.get("return_gpu", False) or kwargs.get("return_diagnostics", False):
        return None
    if kwargs.get("prevPts") is not None or bool(kwargs.get("adaptive", False)):
        return None
    if str(kwargs.get("motion_mode", "fast") or "fast").lower() == "auto":
        return None
    dense_mode = str(kwargs.get("dense_mode", "smooth") or "smooth").lower()
    if dense_mode not in {"smooth", "interpolate", "default"}:
        return None
    if float(kwargs.get("max_flow_px", 0.0) or 0.0) > 0.0:
        return None

    try:
        batch_mod = _mod("lucas_kanade_batch")
    except FileNotFoundError:
        return None

    source_prev = np.ascontiguousarray(prev, dtype=np.float32)
    source_next = np.ascontiguousarray(next, dtype=np.float32)
    grid = engine.plan_blocks(
        "lucas_kanade",
        source_prev.shape,
        source_prev.nbytes + source_next.nbytes,
        halo=halo,
    )
    if grid is None:
        return None

    result = np.empty((*source_prev.shape[:2], 2), dtype=np.float32)
    source_id = "|".join((str(id(prev)), str(id(next))))
    source_checksum = (checksum(source_prev), checksum(source_next))
    params = {
        "shape": tuple(result.shape),
        "dtype": np.dtype(np.float32).str,
        "kwargs": repr(sorted(kwargs.items())),
        "batch_graph": "v1",
    }
    tracker = _BlockExecutionTracker("lucas_kanade", "batch_flow", len(grid))

    # A batch can publish its valid cores into one resident frame.  This is
    # admitted only when the output atlas fits beside the governor's working
    # set; large iGPU frames keep the existing bounded readback path instead
    # of trading low VRAM for a second full-frame allocation.
    atlas_enabled = False
    atlas_flow = None
    if (
        backend in {"vulkan", "cuda"}
        and os.environ.get("PIXEL_REFINE_AOT_DISABLE_LK_ATLAS") != "1"
    ):
        try:
            memory = engine.get_memory_status()
            limit = int(memory.get("resident_limit", 0) or 0)
            headroom = int(memory.get("resident_headroom_bytes", 0) or 0)
            atlas_bytes = int(result.nbytes)
            # Reserve enough space for one two-tile multilevel batch plus a
            # conservative 25% guard.  A zero limit means the backend does
            # not expose a resident budget and is safe to try.
            reserve = max(64 * 1024 * 1024, atlas_bytes // 4)
            atlas_cap = 256 * 1024 * 1024
            if limit > 0:
                atlas_cap = min(atlas_cap, max(64 * 1024 * 1024, limit // 4))
            atlas_enabled = atlas_bytes <= atlas_cap and (
                limit <= 0 or atlas_bytes + reserve <= headroom
            )
        except Exception:
            atlas_enabled = False

    ordered = _ordered_cached_output_blocks(
        "lucas_kanade", grid, source_checksum, params
    )
    cold_groups = {}
    for block in ordered:
        block_id = block.make_id(source_id, "lucas_kanade", params)
        cached = _cached_block_record(
            block_id,
            source_checksum,
            validate_data=lambda data, block=block: (
                np.asarray(data).shape[:2]
                in {tuple(block.read_shape), tuple(block.shape)}
                and np.asarray(data).shape[-1:] == (2,)
            ),
        )
        if cached is not None:
            tracker.cache_hits += 1
            cached_shape = tuple(np.asarray(cached.data).shape[:2])
            if cached_shape == tuple(block.shape):
                result[block.write_slice] = cached.data
            else:
                result[block.write_slice] = cached.data[block.core_slice]
            continue
        tracker.cache_misses += 1
        cold_groups.setdefault(tuple(block.read_shape), []).append(block)

    cold_blocks = [block for group in cold_groups.values() for block in group]

    if not cold_groups:
        tracker.finish()
        return result

    if atlas_enabled:
        try:
            atlas_flow = engine.allocate(source_prev.shape[:2] + (2,), dtype=np.float32)
            tracker.readback_strategy = "atlas"
            tracker.resident_output_bytes = int(result.nbytes)
            # The scatter graph writes every core; zeroing is unnecessary and
            # would add another full-frame dispatch.  Keep the handle alive
            # across all shape groups until the single final readback.
        except Exception as atlas_error:
            print(
                "[LucasKanadeGPU] LK atlas admission failed; "
                f"using bounded tile readback: {atlas_error}"
            )
            atlas_enabled = False
            atlas_flow = None

    grid_step = max(4, int(kwargs.get("grid_step", 48)))
    border_margin = max(0, int(kwargs.get("border_margin", 8)))
    win_size = kwargs.get("winSize", (13, 13))
    win_size = win_size[0] if isinstance(win_size, tuple) else int(win_size)
    win_radius = max(2, int(win_size) // 2)
    criteria = kwargs.get("criteria")
    if criteria is None:
        iterations, epsilon = 8, 0.03
    else:
        iterations, epsilon = int(criteria[1]), float(criteria[2])
    overlap = float(kwargs.get("overlap", 0.35))
    max_level = max(0, int(kwargs.get("maxLevel", 2)))

    # Match the established wrapper's minimum pyramid level rule exactly.
    # The batch graph operates on the packed read tile, not the full source
    # dimensions. Every group below has one exact ``(tile_h, tile_w)`` shape.
    # Using the full-frame shape here would allocate a larger final flow and
    # silently break the block core slicing contract.
    level_shapes = []  # filled independently for each exact tile shape below

    def run_graph(name, **values):
        started = time.perf_counter()
        batch_mod.run(name, **values)
        tracker.dispatch_seconds += time.perf_counter() - started
        tracker.dispatches += 1

    for tile_shape, group in cold_groups.items():
        tile_h, tile_w = (int(tile_shape[0]), int(tile_shape[1]))
        group_level_shapes = [(tile_h, tile_w)]
        for _level in range(1, max_level + 1):
            src_h, src_w = group_level_shapes[-1]
            dst_h, dst_w = src_h // 2, src_w // 2
            if dst_h < 32 or dst_w < 32:
                break
            group_level_shapes.append((dst_h, dst_w))
        level_shapes = group_level_shapes
        tile_bytes = tile_h * tile_w * np.dtype(np.float32).itemsize
        # Batch LK retains both pyramid levels plus grid/meta/output buffers.
        # Keep the cap at two so the atlas never consumes the memory headroom
        # that the scalar tile executor previously reserved for the same
        # operation. The governor may reduce this to one under pressure.
        resident_multiplier = 24 if len(level_shapes) > 1 else 12
        batch_size = engine.recommend_block_batch_size(
            tile_bytes * resident_multiplier,
            cap=2,
        )
        inflight_cap = 1
        if atlas_enabled:
            try:
                memory = engine.get_memory_status()
                headroom = int(memory.get("resident_headroom_bytes", 0) or 0)
                pool_budget = int(memory.get("device_pool_budget", 0) or 0)
                per_batch = tile_bytes * resident_multiplier * max(1, batch_size)
                atlas_bytes = int(result.nbytes)
                pool_safe = pool_budget <= 0 or atlas_bytes + per_batch * 2 <= int(
                    pool_budget * 0.75
                )
                if pool_safe and (headroom <= 0 or headroom >= per_batch * 2):
                    inflight_cap = 2
            except Exception:
                inflight_cap = 1
        pending_buffers = []

        def flush_deferred_batches():
            if not pending_buffers:
                return
            sync_started = time.perf_counter()
            engine.sync()
            tracker.sync_seconds += time.perf_counter() - sync_started
            tracker.syncs += 1
            tracker.batches += len(pending_buffers)
            while pending_buffers:
                resident_buffers = pending_buffers.pop()
                for resident_buffer in reversed(resident_buffers):
                    try:
                        resident_buffer.destroy()
                    except Exception:
                        pass

        for start in range(0, len(group), batch_size):
            batch_blocks = group[start : start + batch_size]
            batch_count = len(batch_blocks)
            prev_batch = np.ascontiguousarray(
                np.stack(
                    [source_prev[block.read_slice] for block in batch_blocks],
                    axis=0,
                ),
                dtype=np.float32,
            )
            next_batch = np.ascontiguousarray(
                np.stack(
                    [source_next[block.read_slice] for block in batch_blocks],
                    axis=0,
                ),
                dtype=np.float32,
            )
            tracker.input_bytes += int(prev_batch.nbytes + next_batch.nbytes)
            offset_buf = None
            if atlas_enabled:
                offsets_np = np.ascontiguousarray(
                    np.asarray(
                        [
                            (
                                int(block.core_slice[0].start),
                                int(block.core_slice[1].start),
                                int(block.y0),
                                int(block.x0),
                                int(block.shape[0]),
                                int(block.shape[1]),
                            )
                            for block in batch_blocks
                        ],
                        dtype=np.int32,
                    )
                )
                tracker.input_bytes += int(offsets_np.nbytes)
            buffers = []
            current_flow = None
            final_flow = None
            pipeline_graphs = []
            for _ in range(2 * (len(level_shapes) - 1)):
                pipeline_graphs.append("flow_lk_batch_downsample_2x_f32")
            for level in range(len(level_shapes) - 1, -1, -1):
                pipeline_graphs.append(
                    "flow_lk_batch_zero"
                    if level == len(level_shapes) - 1
                    else "flow_lk_batch_upsample_f32"
                )
                pipeline_graphs.extend(
                    ("flow_lk_batch_grid_track", "flow_lk_batch_dense_interpolate")
                )
            if atlas_enabled:
                pipeline_graphs.append("flow_lk_batch_scatter_core")
            pipeline_graphs = _pipeline_graph_specs(
                pipeline_graphs,
                (batch_count, level_shapes[0][0], level_shapes[0][1]),
                operation="lucas_kanade",
                source="lucas_kanade_batch",
                module_keys=tuple(
                    (
                        "pyramid"
                        if str(graph).startswith(
                            ("flow_lk_batch_downsample", "flow_lk_batch_upsample")
                        )
                        else "lucas_kanade_batch"
                    )
                    for graph in pipeline_graphs
                ),
            )
            pipeline_context = None
            pipeline_plan = None
            batch_synced = False
            batch_deferred = False
            try:
                if (
                    backend in {"vulkan", "cuda"}
                    and os.environ.get("PIXEL_REFINE_AOT_DISABLE_LK_BATCH_PIPELINE")
                    != "1"
                ):
                    pipeline_context = engine.auto_pipeline(pipeline_graphs)
                    pipeline_plan = pipeline_context.__enter__()
                prev_buf = engine.upload(prev_batch)
                next_buf = engine.upload(next_batch)
                buffers.extend((prev_buf, next_buf))
                if atlas_enabled:
                    offset_buf = engine.upload(offsets_np)
                    buffers.append(offset_buf)
                prev_levels = [prev_buf]
                next_levels = [next_buf]

                for level in range(1, len(level_shapes)):
                    level_h, level_w = level_shapes[level]
                    prev_dst = engine.allocate(
                        (batch_count, level_h, level_w), dtype=np.float32
                    )
                    next_dst = engine.allocate(
                        (batch_count, level_h, level_w), dtype=np.float32
                    )
                    buffers.extend((prev_dst, next_dst))
                    run_graph(
                        "flow_lk_batch_downsample_2x_f32",
                        src=prev_levels[-1],
                        dst=prev_dst,
                    )
                    run_graph(
                        "flow_lk_batch_downsample_2x_f32",
                        src=next_levels[-1],
                        dst=next_dst,
                    )
                    prev_levels.append(prev_dst)
                    next_levels.append(next_dst)

                for level in range(len(level_shapes) - 1, -1, -1):
                    level_h, level_w = level_shapes[level]
                    if current_flow is None:
                        init_flow = engine.allocate(
                            (batch_count, level_h, level_w, 2),
                            dtype=np.float32,
                        )
                        buffers.append(init_flow)
                        run_graph("flow_lk_batch_zero", flow=init_flow)
                    else:
                        init_flow = engine.allocate(
                            (batch_count, level_h, level_w, 2),
                            dtype=np.float32,
                        )
                        buffers.append(init_flow)
                        previous_h = level_shapes[level + 1][0]
                        run_graph(
                            "flow_lk_batch_upsample_f32",
                            src=current_flow,
                            dst=init_flow,
                            scale=float(level_h) / float(previous_h),
                        )

                    level_step = max(4, grid_step >> level)
                    level_margin = max(0, border_margin >> level)
                    grid_h = max(
                        1,
                        (level_h - 2 * level_margin + level_step - 1) // level_step,
                    )
                    grid_w = max(
                        1,
                        (level_w - 2 * level_margin + level_step - 1) // level_step,
                    )
                    grid_flow = engine.allocate(
                        (batch_count, grid_h, grid_w, 3), dtype=np.float32
                    )
                    grid_meta = engine.allocate(
                        (batch_count, grid_h, grid_w, 4), dtype=np.float32
                    )
                    flow_out = engine.allocate(
                        (batch_count, level_h, level_w, 2), dtype=np.float32
                    )
                    buffers.extend((grid_flow, grid_meta, flow_out))
                    run_graph(
                        "flow_lk_batch_grid_track",
                        prev=prev_levels[level],
                        next=next_levels[level],
                        init_flow=init_flow,
                        grid_flow=grid_flow,
                        grid_meta=grid_meta,
                        grid_step=level_step,
                        border_margin=level_margin,
                        win_radius=win_radius,
                        iterations=max(1, int(iterations)),
                        epsilon=float(epsilon),
                    )
                    run_graph(
                        "flow_lk_batch_dense_interpolate",
                        grid_flow=grid_flow,
                        flow_out=flow_out,
                        grid_step=level_step,
                        border_margin=level_margin,
                        overlap=overlap,
                    )
                    current_flow = flow_out
                    final_flow = flow_out

                if atlas_enabled:
                    run_graph(
                        "flow_lk_batch_scatter_core",
                        flow_batch=final_flow,
                        flow_out=atlas_flow,
                        offsets=offset_buf,
                    )

                if pipeline_context is not None:
                    # Preserve the final output while temporary level buffers
                    # are retired after the recorded submission.
                    pipeline_name = engine.current_pipeline
                    if pipeline_name and final_flow is not None:
                        with engine._lock:
                            intermediates = engine._pipeline_intermediates.get(
                                pipeline_name, []
                            )
                            try:
                                intermediates.remove(final_flow)
                            except ValueError:
                                pass
                            final_flow.associated_pipelines.discard(pipeline_name)
                            final_flow.is_pipeline_intermediate = False
                            if atlas_flow is not None:
                                try:
                                    intermediates.remove(atlas_flow)
                                except ValueError:
                                    pass
                                atlas_flow.associated_pipelines.discard(pipeline_name)
                                atlas_flow.is_pipeline_intermediate = False
                    pipeline_context.__exit__(None, None, None)
                    pipeline_context = None
                    if pipeline_plan is not None and pipeline_plan.is_recorded:
                        tracker.pipeline_submissions += 1
                        tracker.pipeline_graphs += len(pipeline_graphs)

                can_defer = bool(
                    atlas_enabled
                    and pipeline_plan is not None
                    and pipeline_plan.is_recorded
                )
                if can_defer:
                    pending_buffers.append(buffers)
                    buffers = []
                    batch_deferred = True
                    if len(pending_buffers) >= inflight_cap:
                        flush_deferred_batches()
                else:
                    sync_started = time.perf_counter()
                    engine.sync()
                    tracker.sync_seconds += time.perf_counter() - sync_started
                    tracker.syncs += 1
                    tracker.batches += 1
                    batch_synced = True
                if not atlas_enabled:
                    readback_started = time.perf_counter()
                    flow_batch = np.ascontiguousarray(final_flow.to_numpy())
                    tracker.readback_seconds += time.perf_counter() - readback_started
                    tracker.output_bytes += int(flow_batch.nbytes)
                    if flow_batch.shape != (batch_count, tile_h, tile_w, 2):
                        raise RuntimeError(
                            "lucas_kanade batch graph returned an unexpected shape: "
                            f"{flow_batch.shape}, expected "
                            f"{(batch_count, tile_h, tile_w, 2)}"
                        )
                    if not np.isfinite(flow_batch).all():
                        raise RuntimeError(
                            "lucas_kanade batch graph returned non-finite data"
                        )

                    for index, block in enumerate(batch_blocks):
                        copied = np.ascontiguousarray(flow_batch[index])
                        block_id = block.make_id(source_id, "lucas_kanade", params)
                        engine.put_block_record(
                            BlockRecord(
                                block_id,
                                state=BlockState.READY,
                                data=copied,
                                checksum=checksum(copied),
                                source_checksum=source_checksum,
                                owner="lucas_kanade",
                            )
                        )
                        result[block.write_slice] = copied[block.core_slice]
            finally:
                if pipeline_context is not None:
                    try:
                        pipeline_context.__exit__(*sys.exc_info())
                    except Exception:
                        pass
                # Non-deferred batches are fenced before their buffers are
                # retired.  Recorded atlas batches keep their buffers in the
                # small in-flight queue and are fenced by
                # ``flush_deferred_batches`` instead.
                if not batch_synced and not batch_deferred:
                    try:
                        engine.sync()
                    except Exception:
                        pass
                for buffer in reversed(buffers):
                    try:
                        buffer.destroy()
                    except Exception:
                        pass
                if sys.exc_info()[0] is not None and atlas_flow is not None:
                    try:
                        atlas_flow.destroy()
                    except Exception:
                        pass
                    atlas_flow = None

        flush_deferred_batches()

    if atlas_enabled and atlas_flow is not None:
        try:
            readback_started = time.perf_counter()
            atlas_np = np.ascontiguousarray(atlas_flow.to_numpy())
            tracker.readback_seconds += time.perf_counter() - readback_started
            tracker.output_bytes += int(atlas_np.nbytes)
            if atlas_np.shape != result.shape or not np.isfinite(atlas_np).all():
                raise RuntimeError(
                    "lucas_kanade atlas graph returned an unexpected or non-finite frame"
                )
            for block in cold_blocks:
                core = np.ascontiguousarray(atlas_np[block.write_slice])
                block_id = block.make_id(source_id, "lucas_kanade", params)
                engine.put_block_record(
                    BlockRecord(
                        block_id,
                        state=BlockState.READY,
                        data=core,
                        checksum=checksum(core),
                        source_checksum=source_checksum,
                        owner="lucas_kanade",
                    )
                )
                result[block.write_slice] = core
        finally:
            try:
                atlas_flow.destroy()
            except Exception:
                pass
            atlas_flow = None

    tracker.finish()
    return result


def lucasKanade(prev, next, **kwargs):
    """Dense grid Lucas-Kanade optical flow."""
    from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLK

    if (
        engine.get_block_config().enabled
        and kwargs.get("prevPts") is None
        and not kwargs.get("return_diagnostics", False)
    ):
        step = max(4, int(kwargs.get("grid_step", 16)))
        block_h, block_w = engine.get_block_config().normalized_size()
        if block_h % step == 0 and block_w % step == 0:
            win = kwargs.get("winSize", (13, 13))
            win = win[0] if isinstance(win, tuple) else int(win)
            levels = max(0, int(kwargs.get("maxLevel", 2)))
            radius = int(np.ceil((win // 2 + step * 2) * (2**levels) / step) * step)
            try:
                batch_result = _run_lucas_kanade_batch_blocks(
                    prev, next, kwargs, radius
                )
            except (RuntimeError, MemoryError) as batch_error:
                print(
                    "[LucasKanadeGPU] native multi-tile batch failed; "
                    f"using established tile path: {batch_error}"
                )
                batch_result = None
            if batch_result is not None:
                return batch_result
            result = _dense_flow_blockwise(
                "lucas_kanade",
                prev,
                next,
                lambda p, n: calcOpticalFlowPyrLK(p, n, **kwargs),
                radius,
                {"kwargs": repr(sorted(kwargs.items()))},
                gpu_run_tile=(
                    None
                    if kwargs.get("return_gpu", False)
                    else lambda p, n: _run_lucas_kanade_gpu_tile(p, n, kwargs)
                ),
            )
            if result is not None:
                return result
    return calcOpticalFlowPyrLK(prev, next, **kwargs)


def blockMatching(prev, next, **kwargs):
    """Dense block matching optical flow with parabolic fit."""
    from taichi_vision.taichi_algorithm import calcOpticalFlowBlockMatching

    step = max(4, int(kwargs.get("grid_step", 16)))
    block_h, block_w = engine.get_block_config().normalized_size()
    if (
        engine.get_block_config().enabled
        and block_h % step == 0
        and block_w % step == 0
    ):
        win = kwargs.get("winSize", (17, 17))
        win = win[0] if isinstance(win, tuple) else int(win)
        levels = max(0, int(kwargs.get("maxLevel", 2)))
        radius = int(np.ceil((win // 2 + step * 3) * (2**levels) / step) * step)
        result = _dense_flow_blockwise(
            "block_matching",
            prev,
            next,
            lambda p, n: calcOpticalFlowBlockMatching(p, n, **kwargs),
            radius,
            {"kwargs": repr(sorted(kwargs.items()))},
            gpu_run_tile=(
                None
                if kwargs.get("return_gpu", False)
                else lambda p, n: calcOpticalFlowBlockMatching(
                    p, n, **dict(kwargs, return_gpu=True)
                )
            ),
        )
        if result is not None:
            return result
    return calcOpticalFlowBlockMatching(prev, next, **kwargs)


# Research-stage modular AOT leaf APIs.  Imported at the end so the research
# module can safely reuse the canonical lazy ``_mod`` loader above.
from .research import *  # noqa: E402,F401,F403

from .research_pipeline import (  # noqa: E402,F401
    hdr_fuse_aot,
    hdr_fusion_aot,
    local_tone_map_aot,
    tone_map_aot,
    plane_sweep_stereo_aot,
    multi_view_plane_sweep_aot,
    point_cloud_preprocess_aot,
    bundle_adjust_lm_aot,
    poisson_reconstruct_aot,
)

from taichi_vision.taichi_algorithm.image_processing.extended_aot import (  # noqa: E402,F401
    dilate_aot,
    erode_aot,
    histogram_aot,
    ssim_aot,
    warp_affine_aot,
    filter2d_aot,
    copy_make_border_aot,
    normalize_aot,
    threshold_aot,
    gaussian_window_aot,
    joint_bilateral_guidance_aot,
    enhance_image_aot,
)

def encode_grayscale_aot(*args, **kwargs):
    """Lazy compatibility wrapper for the optional JPEG implementation."""
    from taichi_vision.taichi_algorithm.compression.jpeg_aot import (
        encode_grayscale_aot as _encode_grayscale_aot,
    )

    return _encode_grayscale_aot(*args, **kwargs)


def encode_rgb_aot(*args, **kwargs):
    """Lazy compatibility wrapper for the optional JPEG implementation."""
    from taichi_vision.taichi_algorithm.compression.jpeg_aot import (
        encode_rgb_aot as _encode_rgb_aot,
    )

    return _encode_rgb_aot(*args, **kwargs)


def jpeg_encode_aot(*args, **kwargs):
    """Lazy compatibility wrapper for the optional JPEG implementation."""
    from taichi_vision.taichi_algorithm.compression.jpeg_aot import (
        jpeg_encode_aot as _jpeg_encode_aot,
    )

    return _jpeg_encode_aot(*args, **kwargs)

# Pre-demosaic RAW semantic/native stages.  These imports are additive to the
# historical API; the native functions load ``compression_raw`` lazily on
# first execution and never route a missing artifact to another backend.
from taichi_vision.taichi_algorithm.compression.raw_frame import (  # noqa: E402,F401
    RawMosaicFrame,
    raw_frame_from_dng,
)
from taichi_vision.taichi_algorithm.compression.dng_aot import (  # noqa: E402,F401
    DNGCapabilityError,
    DNGCapabilityReport,
    dng_capability_report,
)
from taichi_vision.taichi_algorithm.compression.raw_pipeline import (  # noqa: E402,F401
    RawFusionReport,
    RawFlowTileContract,
    raw_flow_tile_contract,
    raw_alignment_guide,
    raw_alignment_guide_dng,
    raw_alignment_guide_native,
    raw_normalize_headroom_native,
    raw_weight_map,
    raw_weight_map_native,
    fuse_raw_pair_native,
    fuse_raw_accumulate_native,
    fuse_raw_frames_blockwise,
    fuse_dng_frames_blockwise,
    phase_safe_integer_warp,
    raw_optical_flow,
    raw_optical_flow_dng,
)
