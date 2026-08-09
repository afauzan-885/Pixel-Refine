"""Runtime compatibility facade for the Taichi AOT library.

The runtime (engine, memory policy, backend selection, and artifact loading)
stays in this package.  Algorithm implementations live in
``taichi_library.taichi_algorithm.aot_api`` so there is one maintained source
tree.  Importing this module keeps the historical public API unchanged:

    import taichi_library.taichi_aot as ta
    ta.resize(image, (1024, 768))

The explicit runtime imports below also preserve ``ta.engine`` and the
backend-management helpers used by the application.
"""

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
from .block import BlockGrid, BlockRecord, BlockState, checksum
from .generic_block import (
    BlockComputeSpec,
    BlockTileContext,
    BlockPlanUnavailable,
    BlockExecutionError,
    GenericBlockExecutor,
    GenericBlockReport,
    GenericBlockResult,
    run_generic_blocks,
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
from .auto_pipeline import AutoPipelinePlanner, GraphSpec, PipelinePlan

# Keep the complete historical algorithm surface available at the old import
# path.  The implementation is now maintained only in ``taichi_algorithm``.
from taichi_library.taichi_algorithm.aot_api import *  # noqa: F401,F403,E402
from taichi_library.taichi_algorithm.aot_api import (  # noqa: E402
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
    from taichi_library.taichi_algorithm.taichi_worker import ti_thread
except Exception:  # pragma: no cover - compiler-only environments
    ti_thread = None


__all__ = [
    name
    for name in globals()
    if not name.startswith("_")
]
