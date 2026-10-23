"""Normalised run plan and stage resolution for the resident burst pipeline.

The orchestrator in :mod:`.run` used to normalise its arguments, resolve the
analysis/weight contracts, and allocate the weight carriers inline.  Those
three steps live here so the orchestrator only has to sequence them.

Every cross-module call goes through :func:`pipeline_process.facade.api` so
``monkeypatch.setattr(resident_pipeline, "<name>", fake)`` keeps reaching the
live execution path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence, Tuple

import numpy as np

from ....pipeline_runtime import (
    PipelineRuntime,
    current_pipeline_runtime,
    resolve_in_processing_depth,
    resolve_prefetch_depth,
)
from ..analysis import ANALYSIS_AUTO_ENHANCE_MODE
from ..contracts import ResidentAnalysisContext, ResidentGeometry
from ..facade import api as _facade

__all__ = [
    "AnalysisStage",
    "RunPlan",
    "WeightCarriers",
    "build_run_plan",
    "prepare_weight_carriers",
    "resolve_analysis_stage",
]


@dataclass
class RunPlan:
    """Normalised call arguments plus the runtime every later stage shares."""

    image_paths: Sequence[Any]
    session: Any = None
    source_mode: Optional[str] = None
    source_descriptor: Any = None
    telemetry: Optional[bool] = None
    weight_engine: str = "fusionet"
    alignment_plan: str = "optical_flow"
    alignment_config: Optional[dict] = None
    spatial_config: Optional[dict] = None
    analysis_enhance: bool = True
    analysis_auto_enhance_mode: str = ANALYSIS_AUTO_ENHANCE_MODE
    work_scale: float = 0.50
    flownet_work_scale: Optional[float] = None
    weightnet_work_scale: Optional[float] = None
    denoising_mode: str = "standard"
    max_neighbor_candidates: int = 4
    patch_search_radius: int = 5
    max_work_dimension: Optional[int] = 2048
    tile_size: int = 512
    weightnet_input_channels: Optional[int] = None
    overlap: float = 0.30
    ghost_penalty: float = 1.0
    ghost_penalty_min: Optional[float] = None
    ghost_cutoff: float = 0.05
    chroma_sensitivity: float = 6.0
    alignment_only: bool = False
    prefetch_depth: Optional[int] = None
    batch_plan: Optional[Sequence[Tuple[int, int]]] = None
    auto_params: Optional[dict] = None
    stop_event: Any = None
    progress_callback: Optional[Callable[[int, str], None]] = None
    runtime: Any = None
    is_raw: bool = False


def build_run_plan(plan: RunPlan) -> RunPlan:
    """Normalise the incoming arguments in the baseline order and attach a runtime."""
    if plan.source_descriptor is None:
        plan.source_descriptor = getattr(
            current_pipeline_runtime(), "source_descriptor", None
        )
    source_mode = plan.source_mode
    if source_mode is None and plan.source_descriptor is not None:
        source_mode = plan.source_descriptor.kind
    if source_mode is None:
        source_mode = "rgb"
    source_mode = str(source_mode).strip().lower()
    if source_mode not in {"rgb", "raw", "video_rgb"}:
        raise ValueError(f"Unsupported resident source_mode: {source_mode!r}")

    denoising_mode = str(plan.denoising_mode).strip().lower().replace(" ", "_")
    if denoising_mode not in {"standard", "deep_analysis"}:
        raise ValueError(f"Unsupported FusionNet denoising mode: {denoising_mode!r}")
    if (
        denoising_mode == "deep_analysis"
        and str(plan.weight_engine).strip().lower() != "fusionet"
    ):
        raise ValueError("Deep Analysis mode is available only with FusionNet")

    plan.source_mode = source_mode
    plan.denoising_mode = denoising_mode
    plan.max_neighbor_candidates = max(1, min(16, int(plan.max_neighbor_candidates)))
    plan.patch_search_radius = max(1, min(16, int(plan.patch_search_radius)))
    # The public parameter remains accepted for source compatibility; each
    # engine stage below chooses its explicit analysis/natural/linear contract.
    plan.analysis_auto_enhance_mode = ANALYSIS_AUTO_ENHANCE_MODE

    runtime = current_pipeline_runtime()
    if runtime is None:
        runtime = PipelineRuntime(
            prefetch_depth=resolve_prefetch_depth(plan.prefetch_depth),
            in_processing_depth=resolve_in_processing_depth(),
            stop_event=plan.stop_event,
            progress_callback=plan.progress_callback,
            source_descriptor=plan.source_descriptor,
        )
    plan.runtime = runtime
    plan.is_raw = source_mode == "raw"
    return plan


@dataclass
class AnalysisStage:
    """Resolved alignment/weight transforms and the reference analysis proxy."""

    needs_analysis: bool
    analysis_params: Optional[dict]
    weight_analysis_params: Optional[dict]
    geometry: ResidentGeometry
    analysis_context: ResidentAnalysisContext
    ref_analysis_gpu: Any
    ref_noise_score: Optional[float]
    ghost_penalty: float
    flow_capped_scale: float
    weight_capped_scale: float
    flow_work_h: int
    flow_work_w: int
    weight_work_h: int
    weight_work_w: int


def resolve_analysis_stage(
    plan: RunPlan,
    ref_gpu: Any,
    target_h: int,
    target_w: int,
) -> AnalysisStage:
    """PHASE 2/3: resolve analysis parameters, geometry, and the reference proxy."""
    alignment_key = str(plan.alignment_plan or "").strip().lower()
    no_alignment = alignment_key in {
        "",
        "none",
        "no alignment",
        "no_alignment",
        "off",
    }
    # Uniform averaging without alignment has no consumer for the analysis
    # proxy, auto-enhance parameters, or noise estimate.  Keeping this gate
    # explicit avoids changing any public mode while removing a full-frame GPU
    # analysis pass from the simplest and most common fast path.
    needs_analysis = not (plan.weight_engine == "average" and no_alignment)

    # Alignment uses the full analysis mode for FusionNet and SpatialFusion.
    # FusionNet's WeightNet parameters remain separately resolved in natural mode.
    alignment_mode = ANALYSIS_AUTO_ENHANCE_MODE
    analysis_params = _facade()._resolve_engine_analysis_params(
        ref_gpu,
        weight_engine=plan.weight_engine,
        enabled=plan.analysis_enhance,
        supplied=(plan.auto_params if alignment_mode != "analysis" else None),
        needs_analysis=needs_analysis,
        mode=alignment_mode,
    )
    weight_analysis_params = analysis_params if plan.weight_engine == "fusionet" else None
    if analysis_params is not None:
        print(
            f"[GPU Pipeline] Alignment AutoEnhance "
            f"({alignment_mode}): "
            f"Gain={analysis_params['gain']:.2f}x "
            "(uncapped reference-derived gain; reused on support alignment proxies)"
        )
    if weight_analysis_params is not None:
        print(
            "[GPU Pipeline] FusionNet WeightNet AutoEnhance (analysis): "
            f"Gain={weight_analysis_params['gain']:.2f}x "
            "(reference-derived parameters reused for weight inference)"
        )
    if analysis_params is None:
        reason = (
            "disabled via analysis_enhance=False"
            if not plan.analysis_enhance
            else "average + no alignment"
        )
        print(f"[GPU Pipeline] Alignment AutoEnhance skipped ({reason})")
    if plan.weight_engine == "fusionet" and weight_analysis_params is None:
        print("[GPU Pipeline] FusionNet analysis WeightNet AutoEnhance skipped")

    flow_scale = (
        float(plan.flownet_work_scale)
        if plan.flownet_work_scale is not None
        else float(plan.work_scale)
    )
    weight_scale = (
        float(plan.weightnet_work_scale)
        if plan.weightnet_work_scale is not None
        else float(plan.work_scale)
    )
    geometry = ResidentGeometry.resolve(
        (target_h, target_w),
        align_scale=flow_scale,
        weight_scale=weight_scale,
        max_work_dimension=plan.max_work_dimension,
    )
    flow_capped_scale = geometry.effective_align_scale
    weight_capped_scale = geometry.effective_weight_scale
    flow_work_h, flow_work_w = geometry.align_shape
    weight_work_h, weight_work_w = geometry.weight_shape
    analysis_context = ResidentAnalysisContext(
        geometry=geometry,
        analysis_params=analysis_params or {},
    )

    work_h, work_w = weight_work_h, weight_work_w

    print(
        f"[GPU Pipeline] Multi-Scale Setup: "
        f"Align Res=({flow_work_h}, {flow_work_w}, "
        f"requested={flow_scale:.2f}, effective={flow_capped_scale:.2f}) | "
        f"WeightNet Res=({weight_work_h}, {weight_work_w}, "
        f"requested={weight_scale:.2f}, effective={weight_capped_scale:.2f}) "
        f"max_work_dimension={('disabled' if plan.max_work_dimension is None else f'{int(plan.max_work_dimension)}px')}"
    )

    # Keep alignment/noise analysis separate from the linear fusion carrier and
    # from FusionNet's natural-mode WeightNet input.
    ref_analysis_flow_gpu = None
    ref_analysis_gpu = None
    ref_noise_score = None
    ghost_penalty = plan.ghost_penalty
    if needs_analysis:
        ref_analysis_flow_gpu, ref_noise_score, ghost_penalty = (
            _facade().prepare_reference_analysis_and_noise(
                ref_gpu,
                work_shape=geometry.align_shape,
                analysis_params=analysis_params,
                ghost_penalty=ghost_penalty,
                ghost_penalty_min=plan.ghost_penalty_min,
                in_place=False,
                noise_source_gpu=(
                    ref_gpu
                    if plan.weight_engine in ("fusionet", "spatial_fusion")
                    else None
                ),
                noise_analysis_params=(
                    analysis_params if plan.weight_engine == "fusionet" else None
                ),
            )
        )

        ref_analysis_gpu = ref_analysis_flow_gpu
        analysis_context.reference_proxy = ref_analysis_gpu
        analysis_context.alignment_reference = ref_analysis_gpu
        analysis_context.noise_score = ref_noise_score

    return AnalysisStage(
        needs_analysis=needs_analysis,
        analysis_params=analysis_params,
        weight_analysis_params=weight_analysis_params,
        geometry=geometry,
        analysis_context=analysis_context,
        ref_analysis_gpu=ref_analysis_gpu,
        ref_noise_score=ref_noise_score,
        ghost_penalty=ghost_penalty,
        flow_capped_scale=flow_capped_scale,
        weight_capped_scale=weight_capped_scale,
        flow_work_h=flow_work_h,
        flow_work_w=flow_work_w,
        weight_work_h=weight_work_h,
        weight_work_w=weight_work_w,
    )


@dataclass
class WeightCarriers:
    """WeightNet buffers, readback workspaces, and the reference weight input."""

    weightnet_gray_gpu: Any
    weightnet_support_workspace: Any
    weightnet_support_workspaces: Any
    weightnet_upload_workspace: Any
    weightnet_upload_workspaces: Any
    ref_work_rgb_np: Any
    ref_transfer_map: Any
    ref_spatial_gray_gpu: Any = None
    spatial_scratch: Any = None
    spatial_tile_h: int = 16
    spatial_tile_w: int = 16
    spatial_overlap: float = 0.35
    spatial_noise_sigma: float = 0.01
    spatial_motion_sens: float = 150.0
    spatial_noise_offset: float = 0.15
    spatial_rows_gpu: Any = None
    spatial_cols_gpu: Any = None
    spatial_row_starts: Any = None
    spatial_col_starts: Any = None
    spatial_weight_post_a_gpu: Any = None
    spatial_weight_post_b_gpu: Any = None
    spatial_weight_slots: Any = None
    generate_spatial_weights_taichi: Any = None


def prepare_weight_carriers(
    plan: RunPlan,
    stage: AnalysisStage,
    ref_gpu: Any,
    *,
    engine: Any,
    taichi_aot: Any,
    session: Any,
    weightnet_channels: int,
) -> WeightCarriers:
    """Allocate the WeightNet carriers and resolve the reference weight input."""
    geometry = stage.geometry
    work_h, work_w = stage.weight_work_h, stage.weight_work_w

    ref_work_rgb_np = None
    ref_transfer_map = None
    weightnet_gray_gpu = None
    weightnet_support_workspace = None
    weightnet_support_workspaces = None
    weightnet_upload_workspace = None
    weightnet_upload_workspaces = None

    if plan.weight_engine == "spatial_fusion" or (
        plan.weight_engine == "fusionet" and weightnet_channels == 1
    ):
        weightnet_gray_gpu = engine.allocate(
            (work_h, work_w), dtype=np.float32, host_accessible=False
        )
    if plan.weight_engine == "fusionet" and getattr(session, "runtime", None) != "taichi_aot":
        weightnet_support_workspace = _facade()._WeightNetReadbackWorkspace(
            (work_h, work_w), channels=weightnet_channels
        )
        weightnet_support_workspaces = (weightnet_support_workspace,) + tuple(
            _facade()._WeightNetReadbackWorkspace(
                (work_h, work_w), channels=weightnet_channels
            )
            for _ in range(1)
        )
        weightnet_upload_workspace = _facade()._WeightNetUploadWorkspace(
            (work_h, work_w), channels=weightnet_channels
        )
        weightnet_upload_workspaces = (weightnet_upload_workspace,) + tuple(
            _facade()._WeightNetUploadWorkspace((work_h, work_w), channels=weightnet_channels)
            for _ in range(1)
        )

    if plan.weight_engine == "fusionet":
        if (
            stage.ref_analysis_gpu is not None
            and geometry.weight_shape == geometry.align_shape
        ):
            reference_analysis_gpu = stage.ref_analysis_gpu
        else:
            reference_analysis_gpu = _facade().prepare_analysis_proxy_gpu(
                ref_gpu,
                work_shape=geometry.weight_shape,
                analysis_params=stage.weight_analysis_params,
            )
        if weightnet_channels == 1 and getattr(session, "runtime", None) != "taichi_aot":
            reference_gray_source_gpu = reference_analysis_gpu
            taichi_aot.cvtColor(
                reference_gray_source_gpu,
                taichi_aot.COLOR_RGB2GRAY,
                dst=weightnet_gray_gpu,
                return_gpu=True,
            )
            reference_weight_input_gpu = weightnet_gray_gpu
        else:
            reference_weight_input_gpu = reference_analysis_gpu
        ref_work_rgb_np, ref_transfer_map = _facade().prepare_weightnet_reference_input(
            reference_weight_input_gpu,
            work_shape=geometry.weight_shape,
            clip_limit=2.0,
            tile_grid_size=(8, 8),
            session=session,
        )
        stage.analysis_context.weight_reference = ref_work_rgb_np
        stage.analysis_context.clahe_transfer_map = None
        if (
            reference_analysis_gpu is not ref_gpu
            and reference_analysis_gpu is not stage.ref_analysis_gpu
        ):
            _facade()._destroy_work_item(reference_analysis_gpu)

    return WeightCarriers(
        weightnet_gray_gpu=weightnet_gray_gpu,
        weightnet_support_workspace=weightnet_support_workspace,
        weightnet_support_workspaces=weightnet_support_workspaces,
        weightnet_upload_workspace=weightnet_upload_workspace,
        weightnet_upload_workspaces=weightnet_upload_workspaces,
        ref_work_rgb_np=ref_work_rgb_np,
        ref_transfer_map=ref_transfer_map,
    )
