"""GPU-resident burst orchestration.

``run_gpu_resident_pipeline`` selects the RAW or RGB resident lane, prepares the
analysis/weight contracts, drives the three stage workers, and blends the burst
on the main thread.  Sibling implementations are reached through
:func:`pipeline_process.facade.api` so ``monkeypatch.setattr`` on the resident
facade keeps reaching the live call path.
"""

from __future__ import annotations

import os
import queue
import sys
import threading
import time
from pathlib import Path
from typing import Callable, Optional, Sequence, Tuple

import numpy as np

from taichi_vision.taichi_aot import TaichiGPUBuffer, get_engine

from ....pipeline_runtime import (
    PipelineRuntime,
    current_pipeline_runtime,
    resolve_in_processing_depth,
    resolve_prefetch_depth,
    runtime_entrypoint,
)
from ...MFDenoiser import (
    PROGRESS_ALIGN_MIN,
    PROGRESS_LOAD_IMAGES_MIN,
    PROGRESS_MERGE_MIN,
    PROGRESS_FINALIZE_MAX,
    _align_percent,
    _merge_percent,
)
from ..analysis import ANALYSIS_AUTO_ENHANCE_MODE
from ..contracts import ResidentAnalysisContext, ResidentGeometry
from ..facade import api as _facade
from ..telemetry import PipelineTelemetry

__all__ = ["run_gpu_resident_pipeline"]

@runtime_entrypoint
def run_gpu_resident_pipeline(
    image_paths: Sequence[str | Path],
    session=None,
    *,
    source_mode: Optional[str] = None,
    source_descriptor=None,
    telemetry: Optional[bool] = None,
    weight_engine: str = "fusionet",
    alignment_plan: str = "optical_flow",
    alignment_config: Optional[dict] = None,
    spatial_config: Optional[dict] = None,
    analysis_enhance: bool = True,
    analysis_auto_enhance_mode: str = ANALYSIS_AUTO_ENHANCE_MODE,
    work_scale: float = 0.50,
    flownet_work_scale: Optional[float] = None,
    weightnet_work_scale: Optional[float] = None,
    denoising_mode: str = "standard",
    max_neighbor_candidates: int = 4,
    patch_search_radius: int = 5,
    max_work_dimension: Optional[int] = 2048,
    tile_size: int = 512,
    weightnet_input_channels: Optional[int] = None,
    overlap: float = 0.30,
    ghost_penalty: float = 1.0,
    ghost_penalty_min: Optional[float] = None,
    ghost_cutoff: float = 0.05,
    chroma_sensitivity: float = 6.0,
    storage_mode: str = "direct",
    alignment_only: bool = False,
    batch_queue: Optional[int] = None,
    prefetch_depth: Optional[int] = None,
    batch_plan: Optional[Sequence[Tuple[int, int]]] = None,
    auto_params: Optional[dict] = None,
    stop_event: Optional[threading.Event] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> Tuple[Optional[np.ndarray], float]:
    """Execute the full GPU-resident FusionNet / SpatialFusion / Streaming Burst pipeline.

    Modes:
    - Pure VRAM/RAM-resident zero-copy pipeline (0 disk I/O, fastest).

    Engines:
    - weight_engine="fusionet": AI WeightNet inference via DirectML ONNX.
    - weight_engine="spatial_fusion": Native Taichi AOT TCM GPU Similarity Weighting.
    - weight_engine="average": Uniform fast averaging.

    Args:
        image_paths: List of image file paths (burst).
        session: WeightNet ONNX session (optional if alignment_only or spatial_fusion).
        weight_engine: "fusionet" (AI), "spatial_fusion" (AOT TCM), or "average".
        spatial_config: Parameters dict for spatial fusion weighting.
        work_scale: Downscale factor for WeightNet/Spatial weight computation.
        flownet_work_scale: Downscale factor for Optical Flow alignment.
        weightnet_work_scale: Downscale factor for WeightNet ONNX inference.
        max_neighbor_candidates: Deep Analysis top-K neighbor limit per target
            location and frame; ignored by Standard.
        patch_search_radius: Deep Analysis radius in WeightNet-grid pixels;
            ignored by Standard.
        max_work_dimension: Optional safety cap for analysis dimensions. Set
            to ``None`` when the UI-requested scale must be used natively.
        tile_size: Tile size for weight computation.
        weightnet_input_channels: Compatibility parameter; FusionNet currently
            requires the validated 1-channel WeightNet model.
        overlap: Tile overlap ratio.
        ghost_penalty: Ghost artifact suppression exponent (maximum penalty).
        ghost_penalty_min: Minimum ghost penalty for high-noise regions.
        ghost_cutoff: Ghost cutoff threshold.
        chroma_sensitivity: Color deviation protection scale.
        source_descriptor/source_mode: Input-layer classification forwarded to
            the denoising runtime before it selects the RAW or RGB provider.
        storage_mode: "direct" (RAM/VRAM stream).
        alignment_only: If True, executes pure alignment without blending.
        batch_queue: Deprecated compatibility argument retained for existing
            callers. The saved Performance-page setting is authoritative.
        prefetch_depth: Optional per-call override for the RAM Queue (0 disables
            read-ahead; 1-4 bounds unchanged source-file byte payloads in RAM).
        batch_plan: Optional comparison-frame ranges from MFDenoiser. The
            reference frame (index 0) remains resident for the whole call.
        auto_params: Pre-computed auto_enhance params (analyzed on first frame if None).
        analysis_auto_enhance_mode: Compatibility argument. FusionNet and
            SpatialFusion alignment use analysis mode; FusionNet weight input
            retains natural mode and SpatialFusion weight input remains linear.
        stop_event: Cancellation signal.
        progress_callback: Progress reporting callback.

    Returns:
        (result_fp32, mean_alpha): Fused float32 RGB [H, W, 3] and mean alpha.
    """
    if source_descriptor is None:
        source_descriptor = getattr(current_pipeline_runtime(), "source_descriptor", None)
    if source_mode is None and source_descriptor is not None:
        source_mode = source_descriptor.kind
    if source_mode is None:
        source_mode = "rgb"
    source_mode = str(source_mode).strip().lower()
    if source_mode not in {"rgb", "raw", "video_rgb"}:
        raise ValueError(f"Unsupported resident source_mode: {source_mode!r}")
    denoising_mode = str(denoising_mode).strip().lower().replace(" ", "_")
    if denoising_mode not in {"standard", "deep_analysis"}:
        raise ValueError(f"Unsupported FusionNet denoising mode: {denoising_mode!r}")
    if denoising_mode == "deep_analysis" and str(weight_engine).strip().lower() != "fusionet":
        raise ValueError("Deep Analysis mode is available only with FusionNet")
    max_neighbor_candidates = max(1, min(16, int(max_neighbor_candidates)))
    patch_search_radius = max(1, min(16, int(patch_search_radius)))
    # The public parameter remains accepted for source compatibility; each
    # engine stage below chooses its explicit analysis/natural/linear contract.
    analysis_auto_enhance_mode = ANALYSIS_AUTO_ENHANCE_MODE
    runtime = current_pipeline_runtime()
    if runtime is None:
        runtime = PipelineRuntime(
            prefetch_depth=resolve_prefetch_depth(prefetch_depth),
            in_processing_depth=resolve_in_processing_depth(),
            stop_event=stop_event,
            progress_callback=progress_callback,
            source_descriptor=source_descriptor,
        )
    is_raw = source_mode == "raw"

    if source_mode == "raw":
        if any(Path(path).suffix.lower() != ".dng" for path in image_paths):
            raise ValueError(
                "RAW pipeline currently supports DNG input only; "
                "this RAW format cannot be processed without a compatible RAW provider"
            )
        # The provider supplies only the CFA carrier operations.  The shared
        # executor below owns the same frame loop, analysis, alignment, weight
        # generation, telemetry, and cleanup as the RGB path.
        if session is None and str(weight_engine).strip().lower() == "fusionet":
            from ...fusionet_engine.weightnet_inference import (
                DEFAULT_WEIGHTNET_ONNX,
                load_weightnet_onnx,
            )

            session = load_weightnet_onnx(
                DEFAULT_WEIGHTNET_ONNX,
                runtime=os.environ.get("PIXEL_REFINE_WEIGHTNET_RUNTIME", "taichi_aot"),
                patch_size=int(tile_size),
                input_channels=1,
            )

        return _facade()._run_shared_raw_provider_pipeline(
            image_paths,
            session=session,
            telemetry=telemetry,
            weight_engine=weight_engine,
            alignment_plan=alignment_plan,
            alignment_config=alignment_config,
            spatial_config=spatial_config,
            work_scale=work_scale,
            flownet_work_scale=flownet_work_scale,
            weightnet_work_scale=weightnet_work_scale,
            denoising_mode=denoising_mode,
            max_neighbor_candidates=max_neighbor_candidates,
            patch_search_radius=patch_search_radius,
            max_work_dimension=max_work_dimension,
            tile_size=tile_size,
            overlap=overlap,
            ghost_penalty=ghost_penalty,
            ghost_penalty_min=ghost_penalty_min,
            ghost_cutoff=ghost_cutoff,
            chroma_sensitivity=chroma_sensitivity,
            auto_params=auto_params,
            stop_event=stop_event,
            progress_callback=progress_callback,
            source_descriptor=source_descriptor,
            weightnet_input_channels=weightnet_input_channels,
            analysis_enhance=analysis_enhance,
            analysis_auto_enhance_mode=analysis_auto_enhance_mode,
            prefetch_depth=runtime.prefetch_depth,
            _runtime=runtime,
        )

    from taichi_vision import taichi_aot

    taichi_aot = _facade()._managed_api(taichi_aot)
    from taichi_vision.taichi_aot import get_engine
    from ...fusionet_engine.weightnet_inference import (
        DEFAULT_WEIGHTNET_ONNX,
        load_weightnet_onnx,
        infer_single_support_weight_map,
    )

    engine = _facade()._managed_api(get_engine())
    buffer_session = runtime.ensure_session(engine)
    engine = buffer_session.managed_api(engine)
    taichi_aot = buffer_session.managed_api(taichi_aot)
    pipeline_telemetry = PipelineTelemetry(engine, enabled=telemetry)
    pipeline_telemetry.emit("start")
    # Keep Taichi's idle allocation pool below a predictable ceiling.  The
    # pipeline queues are already depth-bounded, but a retained allocator pool
    # can otherwise grow as alignment/weight kernels encounter new size
    # classes.  Allow an explicit override for larger GPUs while using a
    # conservative default on 2 GB-class devices.
    try:
        pool = getattr(engine, "buffer_pool", None)
        if pool is not None and hasattr(pool, "set_budget"):
            status = engine.get_memory_status() if hasattr(engine, "get_memory_status") else {}
            resident_limit = int(status.get("resident_limit", 0) or 0)
            default_pool_mb = 128 if 0 < resident_limit <= 3 * 1024**3 else 384
            pool_mb = max(
                32,
                int(os.environ.get("PIXEL_REFINE_TAICHI_POOL_MB", default_pool_mb)),
            )
            pool.set_budget(pool_mb * 1024**2)
    except Exception:
        # Pool limiting is an optimization; never make the processing route
        # fail when an older engine lacks memory telemetry.
        pass
    if batch_plan:
        batch_plan = tuple((int(start), int(end)) for start, end in batch_plan)
        print(
            f"[GPU Pipeline] Batch plan received: {batch_plan}; "
            "reference remains resident across all batches"
        )
    num_images = len(image_paths)
    if num_images < 2:
        raise ValueError(f"Need at least 2 images, got {num_images}")
    total_supp = num_images - 1

    if session is None and weight_engine == "fusionet" and not alignment_only:
        session = load_weightnet_onnx(
            DEFAULT_WEIGHTNET_ONNX,
            runtime=os.environ.get("PIXEL_REFINE_WEIGHTNET_RUNTIME", "taichi_aot"),
            patch_size=tile_size,
            input_channels=1,
        )
    weightnet_channels = _facade()._resolve_weightnet_input_channels(
        session, weightnet_input_channels
    )

    # ------------------------------------------------------------------
    # PHASE 1: Load reference frame directly to GPU
    # ------------------------------------------------------------------
    if progress_callback:
        progress_callback(
            PROGRESS_LOAD_IMAGES_MIN,
            ui="Memuat gambar referensi...",
            console=f"Memuat gambar referensi ke GPU VRAM ({len(image_paths)} frame)...",
        )

    from ..rgb_pipeline.provider import RGBFrameProvider

    rgb_provider = buffer_session.own(RGBFrameProvider(image_paths))
    ref_gpu = buffer_session.own(rgb_provider.load_reference_gpu())
    target_h, target_w = ref_gpu.shape[:2]

    print(
        f"[GPU Pipeline] Reference loaded to VRAM: "
        f"shape=({target_h}, {target_w}, 3) dtype={ref_gpu.dtype} "
        f"size={ref_gpu.nbytes / (1024*1024):.1f} MB (engine={weight_engine})"
    )
    pipeline_telemetry.emit("reference_loaded")
    # ------------------------------------------------------------------
    # PHASE 2: Resolve independent alignment and weight-analysis transforms.
    # ------------------------------------------------------------------
    alignment_key = str(alignment_plan or "").strip().lower()
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
    needs_analysis = not (weight_engine == "average" and no_alignment)

    # Alignment uses the full analysis mode for FusionNet and SpatialFusion.
    # FusionNet's WeightNet parameters remain separately resolved in natural mode.
    alignment_mode = ANALYSIS_AUTO_ENHANCE_MODE
    analysis_params = _facade()._resolve_engine_analysis_params(
        ref_gpu,
        weight_engine=weight_engine,
        enabled=analysis_enhance,
        supplied=(auto_params if alignment_mode != "analysis" else None),
        needs_analysis=needs_analysis,
        mode=alignment_mode,
    )
    weight_analysis_params = analysis_params if weight_engine == "fusionet" else None
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
            if not analysis_enhance
            else "average + no alignment"
        )
        print(f"[GPU Pipeline] Alignment AutoEnhance skipped ({reason})")
    if weight_engine == "fusionet" and weight_analysis_params is None:
        print("[GPU Pipeline] FusionNet analysis WeightNet AutoEnhance skipped")

    # ------------------------------------------------------------------
    # PHASE 3: Create Analysis Reference & Work-Resolution Copy
    # ------------------------------------------------------------------
    flow_scale = float(flownet_work_scale) if flownet_work_scale is not None else float(work_scale)
    weight_scale = float(weightnet_work_scale) if weightnet_work_scale is not None else float(work_scale)
    geometry = ResidentGeometry.resolve(
        (target_h, target_w),
        align_scale=flow_scale,
        weight_scale=weight_scale,
        max_work_dimension=max_work_dimension,
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
        f"max_work_dimension={('disabled' if max_work_dimension is None else f'{int(max_work_dimension)}px')}"
    )

    # Keep alignment/noise analysis separate from the linear fusion carrier and
    # from FusionNet's natural-mode WeightNet input.
    ref_analysis_flow_gpu = None
    ref_analysis_gpu = None
    ref_noise_score = None
    if needs_analysis:
        ref_analysis_flow_gpu, ref_noise_score, ghost_penalty = (
            _facade().prepare_reference_analysis_and_noise(
                ref_gpu,
                work_shape=geometry.align_shape,
                analysis_params=analysis_params,
                ghost_penalty=ghost_penalty,
                ghost_penalty_min=ghost_penalty_min,
                in_place=False,
                noise_source_gpu=(
                    ref_gpu
                    if weight_engine in ("fusionet", "spatial_fusion")
                    else None
                ),
                noise_analysis_params=(
                    analysis_params if weight_engine == "fusionet" else None
                ),
            )
        )

        ref_analysis_gpu = ref_analysis_flow_gpu
        analysis_context.reference_proxy = ref_analysis_gpu
        analysis_context.alignment_reference = ref_analysis_gpu
        analysis_context.noise_score = ref_noise_score

    ref_work_rgb_np = None
    weightnet_gray_gpu = None
    weightnet_support_workspace = None
    weightnet_support_workspaces = None
    weightnet_upload_workspace = None
    weightnet_upload_workspaces = None
    ref_spatial_gray_gpu = None
    spatial_scratch = None
    spatial_tile_h = 16
    spatial_tile_w = 16
    spatial_overlap = 0.35
    spatial_noise_sigma = 0.01
    spatial_motion_sens = 150.0
    spatial_noise_offset = 0.15
    spatial_rows_gpu = None
    spatial_cols_gpu = None
    spatial_weight_work_gpu = None
    # Compact SpatialFusion writes final weights directly into leased slots;
    # the former full-resolution generation map is no longer needed.
    spatial_weight_post_a_gpu = None
    spatial_weight_post_b_gpu = None
    spatial_weight_slots = None
    average_weight_gpu = None
    spatial_row_starts = []
    spatial_col_starts = []

    if weight_engine == "spatial_fusion" or (
        weight_engine == "fusionet" and weightnet_channels == 1
    ):
        weightnet_gray_gpu = engine.allocate(
            (work_h, work_w), dtype=np.float32, host_accessible=False
        )
    if weight_engine == "fusionet" and getattr(session, "runtime", None) != "taichi_aot":
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

    if weight_engine == "spatial_fusion":
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi import (
            SpatialScratchCache,
            generate_spatial_weights_taichi,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi.compute_spatial import (
            _compute_tile_starts,
        )
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            resolve_spatial_thresholds,
        )

        (
            st_size, spatial_overlap, spatial_motion_sens,
            spatial_noise_offset, spatial_noise_sigma, spatial_sigma_mode,
        ) = _facade()._resolve_spatial_analysis_config(
            spatial_config, tile_size=tile_size, overlap=overlap,
            work_shape=(work_h, work_w), noise_score=ref_noise_score, is_raw=is_raw,
        )
        spatial_tile_h = st_size
        spatial_tile_w = st_size

        # SpatialFusion aligns with the analysis-enhanced proxy but scores its
        # independent linear reference proxy.
        print(
            "[GPU Pipeline] SpatialFusion alignment uses AutoEnhance analysis; "
            "weight scoring uses linear reference/support proxies; "
            "linear fusion carrier unchanged"
        )
        ref_spatial_linear_gpu = _facade().prepare_analysis_proxy_gpu(
            ref_gpu, work_shape=geometry.weight_shape, analysis_params=None
        )
        ref_spatial_gray_source_gpu = taichi_aot.cvtColor(
            ref_spatial_linear_gpu, taichi_aot.COLOR_RGB2GRAY
        )
        if ref_spatial_linear_gpu is not ref_gpu:
            _facade()._destroy_work_item(ref_spatial_linear_gpu)
        ref_spatial_gray_gpu = ref_spatial_gray_source_gpu

        print(
            f"[SpatialFusion] Kernel parameters: tile={spatial_tile_h} "
            f"overlap={spatial_overlap:.3f} "
            f"motion_sensitivity={spatial_motion_sens:.3f} (noise-aware) "
            f"noise_offset_factor={spatial_noise_offset:.3f} "
            f"noise_sigma={spatial_noise_sigma:.6f}"
        )
        print(
            f"[SpatialFusion] Reference noise sigma (Taichi Vision GPU-Native): "
            f"{spatial_noise_sigma:.6f} (mode={spatial_sigma_mode})"
        )
        spatial_row_starts = _compute_tile_starts(
            work_h, spatial_tile_h, overlap=spatial_overlap
        )
        spatial_col_starts = _compute_tile_starts(
            work_w, spatial_tile_w, overlap=spatial_overlap
        )
        spatial_rows_gpu = taichi_aot.upload(
            np.asarray(spatial_row_starts, dtype=np.int32)
        )
        spatial_cols_gpu = taichi_aot.upload(
            np.asarray(spatial_col_starts, dtype=np.int32)
        )
        spatial_weight_post_a_gpu = engine.allocate(
            (work_h, work_w), dtype=np.float32, host_accessible=False
        )
        spatial_weight_post_b_gpu = engine.allocate(
            (work_h, work_w), dtype=np.float32, host_accessible=False
        )
        spatial_weight_slots = queue.Queue(maxsize=2)
        spatial_weight_slots.put_nowait(spatial_weight_post_a_gpu)
        spatial_weight_slots.put_nowait(spatial_weight_post_b_gpu)
        spatial_scratch = _facade()._own_component(SpatialScratchCache(), releaser=lambda cache: cache.clear())
    elif weight_engine == "fusionet":
        if (
            ref_analysis_gpu is not None
            and geometry.weight_shape == geometry.align_shape
        ):
            reference_analysis_gpu = ref_analysis_gpu
        else:
            reference_analysis_gpu = _facade().prepare_analysis_proxy_gpu(
                ref_gpu,
                work_shape=geometry.weight_shape,
                analysis_params=weight_analysis_params,
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
        analysis_context.weight_reference = ref_work_rgb_np
        analysis_context.clahe_transfer_map = None
        if (
            reference_analysis_gpu is not ref_gpu
            and reference_analysis_gpu is not ref_analysis_gpu
        ):
            _facade()._destroy_work_item(reference_analysis_gpu)

    def _is_persistent_weight(buf):
        return (
            weight_engine == "average"
            and buf is average_weight_gpu
        ) or (
            weight_engine == "spatial_fusion"
            and (
                buf is spatial_weight_post_a_gpu
                or buf is spatial_weight_post_b_gpu
            )
        )

    # ------------------------------------------------------------------
    # PHASE 4: Initialize GPU-Resident Aligner
    # ------------------------------------------------------------------
    if progress_callback:
        progress_callback(
            PROGRESS_ALIGN_MIN,
            ui="Menyiapkan Aligner...",
            console=f"Inisialisasi Aligner ({alignment_plan}) di GPU...",
        )

    aligner = _facade().create_resident_aligner(
        alignment_plan,
        ref_analysis_flow_gpu,
        work_scale=flow_capped_scale,
        full_shape=(target_h, target_w),
        alignment_config=alignment_config,
        noise_score=ref_noise_score,
    )

    if ref_analysis_flow_gpu is not None and ref_analysis_flow_gpu is not ref_gpu:
        _facade()._destroy_work_item(ref_analysis_flow_gpu)

    # ------------------------------------------------------------------
    # PHASE 5: Initialize GPU accumulators with 100% True Linear RAW Reference
    # ------------------------------------------------------------------
    # Directly use ref_gpu as sum_img_gpu accumulator to save 144MB VRAM
    sum_img_gpu = ref_gpu
    if weight_engine in ("spatial_fusion", "average") or (
        weight_engine == "fusionet" and weightnet_channels == 1
    ):
        # These engines produce one color-neutral confidence value per pixel.
        # Keep its accumulator scalar and broadcast only while updating RGB;
        # do not retain a redundant full-resolution vec3 weight sum.
        weight_sum_gpu = engine.upload(np.ones((target_h, target_w), dtype=np.float32))
    else:
        # FusionNet/WeightNet outputs a 3-channel (vec3) weightmap [H, W, 3].
        weight_sum_gpu = engine.upload(
            np.ones((target_h, target_w, 3), dtype=np.float32)
        )
    if weight_engine == "average":
        # Uniform weights are invariant across support frames. Keep one
        # resident work-resolution buffer instead of allocating and uploading
        # a full host array for every frame.
        average_weight_gpu = engine.upload(
            np.ones((work_h, work_w), dtype=np.float32),
            is_vector=False,
            vector_dim=1,
        )
    rgb_provider.bind_accumulator(sum_img_gpu, weight_sum_gpu)
    engine_arch = str(getattr(engine, "arch", "")).lower()
    is_cpu_backend = engine_arch == "cpu"
    is_thread_affine = engine_arch in ("opengl", "gles")

    # The RAM Queue controls the host loader queue. The separate in-processing
    # limiter below spans admission through final blend for this support frame.
    q_depth = runtime.prefetch_depth
    in_processing_lock = threading.Lock()
    in_processing_active: dict[int, Any] = {}
    in_processing_peak = 0

    if progress_callback:
        progress_callback(
            PROGRESS_MERGE_MIN,
            ui="Menyiapkan Pipeline...",
            console=(
                "Memulai Pipeline Asynchronous Flow "
                f"(ram_queue={q_depth}, in_processing={runtime.in_processing_depth})..."
            ),
        )

    _SENTINEL = object()
    vram_queue = queue.Queue(maxsize=1)  # One unaligned frame resident in VRAM
    aligned_queue = queue.Queue(maxsize=1)  # One aligned frame in flight
    weighted_queue = queue.Queue(maxsize=1)  # One weighted frame awaiting blending

    print(
        f"[GPU Pipeline] Universal Multi-Stage Queue initialized: "
        f"ram_queue={q_depth}, in_processing_queue={runtime.in_processing_depth}, "
        f"stage_queue_capacity=1, cpu_mode={is_cpu_backend}"
    )

    pipeline_error = None
    pipeline_lock = threading.Lock()
    gpu_hardware_lock = threading.Lock()
    processed_count = 0
    alpha_total = 0.0

    def _is_stopped():
        if stop_event is not None:
            if hasattr(stop_event, "is_set"):
                if stop_event.is_set():
                    return True
            elif callable(stop_event):
                if stop_event():
                    return True
        return False

    def _remap_rgb_rank_carrier(source_gpu, rank_indices, offsets, telemetry):
        """Gather per-location neighbor offsets from an aligned RGB carrier."""
        from ...patch_process.multi_patch import candidate_flow_from_indices

        flow_host = candidate_flow_from_indices(
            rank_indices,
            offsets,
            full_shape=geometry.full_shape,
            flow_shape=geometry.align_shape,
        )
        flow_gpu = engine.upload(flow_host, is_vector=True)
        try:
            started = time.perf_counter()
            result = taichi_aot.remap_with_flow(
                source_gpu,
                flow_gpu,
                int(geometry.full_shape[0]),
                int(geometry.full_shape[1]),
                return_gpu=True,
            )
            telemetry.record("carrier_rank_remap", started)
            return result
        finally:
            _facade()._destroy_work_item(flow_gpu)

    patch_offsets = None
    if weight_engine == "fusionet" and denoising_mode == "deep_analysis":
        from ...patch_process.multi_patch import (
            CandidateTelemetry,
            search_candidate_offsets,
        )

        patch_offsets = search_candidate_offsets(
            geometry.full_shape,
            geometry.weight_shape,
            align_shape=geometry.align_shape,
            search_radius=patch_search_radius,
            patch_stride=2,
            preserve_cfa_phase=False,
        )
        reference_telemetry = CandidateTelemetry()
        for rank_indices, _rank_valid, confidence, _rank_alpha in _facade()._iter_multi_patch_rank_maps(
            session,
            ref_work_rgb_np,
            ref_work_rgb_np,
            patch_offsets,
            max_neighbors=max_neighbor_candidates,
            tile_size=tile_size,
            overlap=overlap,
            ghost_penalty=ghost_penalty,
            ghost_cutoff=ghost_cutoff,
            chroma_sensitivity=chroma_sensitivity,
            stop_event=stop_event,
            telemetry=reference_telemetry,
        ):
            if _is_stopped():
                raise RuntimeError("RGB Deep Analysis cancelled during reference neighbors")
            candidate_carrier_gpu = weight_gpu = None
            try:
                candidate_carrier_gpu = _remap_rgb_rank_carrier(
                    ref_gpu, rank_indices, patch_offsets, reference_telemetry
                )
                weight_gpu = _facade()._upload_weightnet_confidence(engine, confidence)
                accumulate_started = time.perf_counter()
                rgb_provider.accumulate(
                    candidate_carrier_gpu,
                    transform=None,
                    weight_map=weight_gpu,
                )
                reference_telemetry.record("rgb_accumulation_device", accumulate_started)
                if getattr(session, "runtime", None) != "taichi_aot":
                    engine.sync()
            finally:
                if weight_gpu is not None:
                    _facade()._destroy_work_item(weight_gpu)
                if candidate_carrier_gpu is not None:
                    _facade()._destroy_work_item(candidate_carrier_gpu)
        if reference_telemetry.candidate_count == 0:
            raise RuntimeError("RGB Deep Analysis patch search produced no reference neighbors")
        print(
            "[FusionNet MultiPatch][RGB reference] "
            f"backend={getattr(engine, 'arch', 'unknown')} "
            f"shape={geometry.weight_shape} dtype=float32 "
            f"neighbors={reference_telemetry.candidate_count} "
            f"search_candidates={reference_telemetry.search_candidate_count} "
            f"stages={reference_telemetry.summary()}"
        )

    def _workers_stopped():
        return _is_stopped() or runtime.worker_stop_requested

    def _release_in_processing_slot(index):
        with in_processing_lock:
            lease = in_processing_active.pop(int(index), None)
        if lease is not None:
            lease.release()

    def _release_all_in_processing_slots():
        with in_processing_lock:
            leases = tuple(in_processing_active.values())
            in_processing_active.clear()
        for lease in leases:
            lease.release()

    def _iter_in_processing_supports(
        indices, loader, *, disposer=None, prepare=None
    ):
        """Register generic runtime leases until the final blend stage releases them."""
        nonlocal in_processing_peak
        for index, support, support_lease in runtime.iter_admitted_supports(
            indices,
            loader,
            prepare or (lambda _index, value: value),
            stop_when=lambda: _workers_stopped() or pipeline_error is not None,
            source_disposer=disposer,
        ):
            with in_processing_lock:
                in_processing_active[int(index)] = support_lease
                in_processing_peak = max(
                    in_processing_peak, len(in_processing_active)
                )
            yield index, support

    def _put_stage_end(stage_queue):
        # Consumers can exit on cancel/error before reading the sentinel.
        # Never block a producer forever behind an abandoned full queue.
        while not _workers_stopped() and pipeline_error is None:
            try:
                stage_queue.put(_SENTINEL, timeout=0.05)
                return
            except queue.Full:
                continue

    def _take_spatial_weight_slot():
        while not _workers_stopped() and pipeline_error is None:
            try:
                return buffer_session.borrow(spatial_weight_slots.get(timeout=0.05))
            except queue.Empty:
                continue
        return None

    def _release_spatial_weight_slot(buf):
        if (
            spatial_weight_slots is None
            or buf is None
            or (
                buf is not spatial_weight_post_a_gpu
                and buf is not spatial_weight_post_b_gpu
            )
        ):
            return
        try:
            buffer_session.release_borrow(buf)
        except ValueError:
            # Duplicate return: do not add the same writable slot twice.
            return
        try:
            spatial_weight_slots.put_nowait(buf)
        except queue.Full:
            # A full slot queue means the same lease was already returned.
            pass


    def _set_error(exc):
        nonlocal pipeline_error
        import traceback

        traceback.print_exc()
        with pipeline_lock:
            if pipeline_error is None:
                pipeline_error = exc

    def _load_host_support(index):
        """Read original file bytes only; decoding happens after queue admission."""
        return rgb_provider.load_support_bytes_host(index)

    # ------------------------------------------------------------------
    # Worker 1.5: Dedicated VRAM Uploader (PCIe DMA Double-Buffering)
    # ------------------------------------------------------------------
    def _uploader_worker():
        try:
            from taichi_vision.taichi_aot.engine import ensure_cuda_context

            ensure_cuda_context()
        except Exception:
            pass
        try:
            for curr_idx, supp_linear_input in _iter_in_processing_supports(
                range(1, num_images),
                _load_host_support,
                disposer=lambda payload: payload.close(),
                prepare=rgb_provider.decode_support_bytes_host,
            ):
                if _workers_stopped() or pipeline_error is not None:
                    _facade()._destroy_work_item(supp_linear_input)
                    break
                curr_name = Path(image_paths[curr_idx]).name

                with gpu_hardware_lock:
                    if _workers_stopped():
                        _facade()._destroy_work_item(supp_linear_input)
                        break
                    # Keep the host prefetch queue free of resized GPU buffers.
                    # CPU resizing is synchronous here; GPU backends resize only
                    # after the current support has been uploaded.
                    if (
                        is_cpu_backend
                        and tuple(supp_linear_input.shape[:2]) != (target_h, target_w)
                    ):
                        supp_linear_input = np.ascontiguousarray(
                            taichi_aot.resize(
                                supp_linear_input,
                                (target_w, target_h),
                                interpolation=taichi_aot.INTER_LINEAR,
                            ),
                            dtype=np.float32,
                        )

                    # Upload exactly the support currently entering the GPU stages.
                    if isinstance(supp_linear_input, TaichiGPUBuffer):
                        supp_linear_gpu = supp_linear_input
                    else:
                        supp_linear_gpu = engine.upload(supp_linear_input)
                        del supp_linear_input

                    if (
                        not is_cpu_backend
                        and tuple(supp_linear_gpu.shape[:2]) != (target_h, target_w)
                    ):
                        resized_gpu = taichi_aot.resize(
                            supp_linear_gpu,
                            (target_w, target_h),
                            interpolation=taichi_aot.INTER_LINEAR,
                            return_gpu=True,
                        )
                        _facade()._destroy_work_item(supp_linear_gpu)
                        supp_linear_gpu = resized_gpu

                    if not needs_analysis:
                        # Average + no alignment never consumes a work-resolution
                        # analysis frame. Keep the carrier as the pass-through
                        # secondary so the queue/ownership contract stays intact
                        # without two unnecessary GPU resizes.
                        supp_analysis_flow_gpu = supp_linear_gpu
                        supp_analysis_sec_gpu = supp_linear_gpu
                    else:
                        # Keep the alignment proxy independent from the linear
                        # fusion carrier and from the weight-scoring proxy.
                        supp_analysis_flow_gpu = _facade().prepare_analysis_proxy_gpu(
                            supp_linear_gpu,
                            work_shape=geometry.align_shape,
                            analysis_params=analysis_params,
                            in_place=True,
                        )

                        if weight_engine == "fusionet":
                            if geometry.weight_shape == geometry.align_shape:
                                supp_analysis_sec_gpu = supp_analysis_flow_gpu
                            else:
                                supp_analysis_sec_gpu = _facade().prepare_analysis_proxy_gpu(
                                    supp_linear_gpu,
                                    work_shape=geometry.weight_shape,
                                    analysis_params=weight_analysis_params,
                                )
                        elif weight_engine == "spatial_fusion":
                            supp_analysis_sec_gpu = _facade().prepare_analysis_proxy_gpu(
                                supp_linear_gpu,
                                work_shape=geometry.weight_shape,
                                analysis_params=None,
                            )
                        # Other engines keep their prior linear secondary path.
                        elif (weight_work_h, weight_work_w) != (target_h, target_w):
                            supp_analysis_sec_gpu = taichi_aot.resize(
                                supp_linear_gpu,
                                (weight_work_w, weight_work_h),
                                interpolation=taichi_aot.INTER_AREA,
                                return_gpu=True,
                            )
                        else:
                            supp_analysis_sec_gpu = supp_linear_gpu

                while not _workers_stopped():
                    if pipeline_error is not None:
                        _facade()._destroy_work_item(supp_linear_gpu)
                        if supp_analysis_flow_gpu is not supp_linear_gpu:
                            _facade()._destroy_work_item(supp_analysis_flow_gpu)
                        if (
                            supp_analysis_sec_gpu is not supp_linear_gpu
                            and supp_analysis_sec_gpu is not supp_analysis_flow_gpu
                        ):
                            _facade()._destroy_work_item(supp_analysis_sec_gpu)
                        return
                    try:
                        vram_queue.put(
                            (
                                curr_idx,
                                curr_name,
                                supp_linear_gpu,
                                supp_analysis_flow_gpu,
                                supp_analysis_sec_gpu,
                            ),
                            timeout=0.05,
                        )
                        break
                    except queue.Full:
                        continue
        except Exception as exc:
            _set_error(exc)
        finally:
            _put_stage_end(vram_queue)

    # ------------------------------------------------------------------
    # Worker 2: Optical Flow Alignment & Dual-Warp (Taichi GPU)
    # ------------------------------------------------------------------
    def _alignment_worker():
        try:
            from taichi_vision.taichi_aot.engine import ensure_cuda_context

            ensure_cuda_context()
        except Exception:
            pass
        try:
            while not _workers_stopped():
                if pipeline_error is not None:
                    break
                try:
                    item = vram_queue.get(timeout=0.05)
                except queue.Empty:
                    continue

                if item is _SENTINEL:
                    break

                (
                    curr_idx,
                    curr_name,
                    supp_linear_gpu,
                    supp_analysis_flow_gpu,
                    supp_analysis_sec_gpu,
                ) = item

                supp_aligned_linear_gpu = None
                supp_work_item = None
                raw_np = None

                with gpu_hardware_lock:
                    if _workers_stopped():
                        _facade()._destroy_work_item(supp_linear_gpu)
                        if supp_analysis_flow_gpu is not supp_linear_gpu:
                            _facade()._destroy_work_item(supp_analysis_flow_gpu)
                        if (
                            supp_analysis_sec_gpu is not supp_linear_gpu
                            and supp_analysis_sec_gpu is not supp_analysis_flow_gpu
                        ):
                            _facade()._destroy_work_item(supp_analysis_sec_gpu)
                        break

                    # Dual-Warp on GPU (Primary in full-res 12MP, Secondary directly in weight-res)
                    # 100% Taichi Vision GPU-resident, zero OpenCV, zero numpy round-trip.
                    # The average/no-alignment fast path is already a carrier
                    # pass-through; avoid even the no-op aligner call there.
                    if not needs_analysis:
                        if _workers_stopped():
                            raise RuntimeError("Alignment cancelled.")
                        supp_aligned_linear_gpu = supp_linear_gpu
                        supp_aligned_sec_gpu = supp_linear_gpu
                    else:
                        supp_aligned_linear_gpu, supp_aligned_sec_gpu = (
                            aligner.align_frame(
                                supp_linear_gpu,
                                analysis_frame_gpu=supp_analysis_flow_gpu,
                                secondary_frame_to_warp=supp_analysis_sec_gpu,
                                stop_event=stop_event,
                                return_gpu=True,
                            )
                        )
                    if supp_aligned_linear_gpu is not supp_linear_gpu:
                        _facade()._destroy_work_item(supp_linear_gpu)
                    if (
                        supp_analysis_flow_gpu is not supp_linear_gpu
                        and supp_analysis_flow_gpu is not supp_aligned_sec_gpu
                    ):
                        _facade()._destroy_work_item(supp_analysis_flow_gpu)
                    if (
                        supp_analysis_sec_gpu is not supp_linear_gpu
                        and supp_analysis_sec_gpu is not supp_analysis_flow_gpu
                        and supp_analysis_sec_gpu is not supp_aligned_sec_gpu
                    ):
                        _facade()._destroy_work_item(supp_analysis_sec_gpu)

                    if weight_engine == "spatial_fusion":
                        # Queue the disposable enhanced RGB analysis proxy;
                        # grayscale is written into the reusable scratch in the
                        # serial weight worker, with no per-frame allocation.
                        supp_work_item = supp_aligned_sec_gpu
                    elif weight_engine == "average":
                        if (
                            supp_aligned_sec_gpu is not None
                            and supp_aligned_sec_gpu is not supp_aligned_linear_gpu
                        ):
                            _facade()._destroy_work_item(supp_aligned_sec_gpu)
                        supp_work_item = None
                    else:
                        # DirectML ONNX requires CPU array: pull bytes directly
                        # to avoid an extra allocation before transposition.
                        readback_workspace = (
                            weightnet_support_workspaces[curr_idx & 1]
                            if weightnet_support_workspaces is not None
                            else None
                        )
                        weightnet_input_gpu = supp_aligned_sec_gpu
                        if weightnet_channels == 1:
                            taichi_aot.cvtColor(
                                supp_aligned_sec_gpu,
                                taichi_aot.COLOR_RGB2GRAY,
                                dst=weightnet_gray_gpu,
                                return_gpu=True,
                            )
                            weightnet_input_gpu = weightnet_gray_gpu
                        if readback_workspace is not None:
                            raw_np = readback_workspace.readback(weightnet_input_gpu)
                        else:
                            raw_np = weightnet_input_gpu.to_numpy()
                        _facade()._destroy_work_item(supp_aligned_sec_gpu)

                if raw_np is not None:
                    if (
                        weightnet_support_workspaces is not None
                        and readback_workspace is not None
                    ):
                        supp_work_item = readback_workspace.as_chw(raw_np)
                    else:
                        supp_work_item = np.ascontiguousarray(
                            raw_np[None, ...]
                            if raw_np.ndim == 2
                            else np.transpose(raw_np, (2, 0, 1)),
                            dtype=np.float32,
                        )
                    del raw_np

                if alignment_only:
                    _facade()._destroy_work_item(supp_aligned_linear_gpu)
                    _facade()._destroy_work_item_except(supp_work_item, supp_aligned_linear_gpu)
                    _release_in_processing_slot(curr_idx)
                    if progress_callback:
                        progress_callback(
                            _align_percent(curr_idx, total_supp),
                            f"Alignment: {curr_idx}/{total_supp} ({curr_name})...",
                        )
                    continue

                # Apply Precomputed Reference Transfer Map on CPU NumPy OUTSIDE gpu_hardware_lock
                if weight_engine not in ("spatial_fusion", "average") and supp_work_item is not None:
                    if ref_transfer_map is not None:
                        try:
                            supp_work_item = _facade().apply_precomputed_transfer_map(
                                supp_work_item, ref_transfer_map
                            )
                        except Exception:
                            pass

                while not _workers_stopped():
                    if pipeline_error is not None:
                        _facade()._destroy_work_item(supp_aligned_linear_gpu)
                        _facade()._destroy_work_item_except(supp_work_item, supp_aligned_linear_gpu)
                        return
                    try:
                        aligned_queue.put(
                            (
                                curr_idx,
                                curr_name,
                                supp_aligned_linear_gpu,
                                supp_work_item,
                            ),
                            timeout=0.05,
                        )
                        break
                    except queue.Full:
                        continue
        except Exception as exc:
            _set_error(exc)
        finally:
            _put_stage_end(aligned_queue)

    # ------------------------------------------------------------------
    # Worker 3: Weight Inference (DirectML ONNX AI or Native Taichi AOT)
    # ------------------------------------------------------------------
    def _enqueue_deep_candidate(
        curr_idx,
        curr_name,
        carrier_gpu,
        weight_gpu,
        alpha_share,
        candidate_index,
        candidate_count,
        telemetry,
        carrier_owned,
    ):
        while not _workers_stopped() and pipeline_error is None:
            try:
                weighted_queue.put(
                    (
                        curr_idx,
                        curr_name,
                        carrier_gpu,
                        weight_gpu,
                        float(alpha_share),
                        int(candidate_index),
                        int(candidate_count),
                        telemetry,
                        bool(carrier_owned),
                    ),
                    timeout=0.05,
                )
                return True
            except queue.Full:
                continue
        return False

    def _weight_inference_worker():
        weight_slot = None
        try:
            from taichi_vision.taichi_aot.engine import ensure_cuda_context

            ensure_cuda_context()
        except Exception:
            pass
        try:
            while not _workers_stopped():
                if pipeline_error is not None:
                    break
                try:
                    item = aligned_queue.get(timeout=0.05)
                except queue.Empty:
                    continue

                if item is _SENTINEL:
                    break

                curr_idx, curr_name, supp_aligned_linear_gpu, supp_work_item = item

                if _workers_stopped():
                    with gpu_hardware_lock:
                        _facade()._destroy_work_item(supp_aligned_linear_gpu)
                    _facade()._destroy_work_item_except(supp_work_item, supp_aligned_linear_gpu)
                    break

                if (
                    weight_engine == "fusionet"
                    and str(denoising_mode).strip().lower() == "deep_analysis"
                ):
                    from ...patch_process.multi_patch import CandidateTelemetry

                    if patch_offsets is None:
                        raise RuntimeError("Deep Analysis search offsets were not initialized")
                    telemetry = CandidateTelemetry()
                    try:
                        source_proxy_chw = np.asarray(supp_work_item, dtype=np.float32)
                        options = dict(
                            max_neighbors=max_neighbor_candidates,
                            tile_size=tile_size,
                            overlap=overlap,
                            ghost_penalty=ghost_penalty,
                            ghost_cutoff=ghost_cutoff,
                            chroma_sensitivity=chroma_sensitivity,
                            stop_event=stop_event,
                            telemetry=telemetry,
                        )
                        candidate_maps = _facade()._iter_deep_support_candidate_maps(
                            session,
                            ref_work_rgb_np,
                            source_proxy_chw,
                            patch_offsets,
                            **options,
                        )
                        for candidate_index, (
                            rank_indices,
                            _rank_valid,
                            confidence,
                            alpha,
                            candidate_count,
                        ) in enumerate(candidate_maps):
                            if _workers_stopped():
                                raise RuntimeError(
                                    "RGB Deep Analysis cancelled during candidate maps"
                                )
                            carrier_owned = rank_indices is not None
                            candidate_carrier_gpu = weight_work_gpu = None
                            try:
                                if carrier_owned:
                                    with gpu_hardware_lock:
                                        candidate_carrier_gpu = _remap_rgb_rank_carrier(
                                            supp_aligned_linear_gpu,
                                            rank_indices,
                                            patch_offsets,
                                            telemetry,
                                        )
                                else:
                                    candidate_carrier_gpu = supp_aligned_linear_gpu
                                with gpu_hardware_lock:
                                    weight_work_gpu = _facade()._upload_weightnet_confidence(
                                        engine, confidence
                                    )
                                queued = _enqueue_deep_candidate(
                                    curr_idx,
                                    curr_name,
                                    candidate_carrier_gpu,
                                    weight_work_gpu,
                                    alpha / candidate_count,
                                    candidate_index,
                                    candidate_count,
                                    telemetry,
                                    carrier_owned,
                                )
                                if not queued:
                                    raise RuntimeError(
                                        "RGB Deep Analysis stopped before candidate fusion"
                                    )
                                candidate_carrier_gpu = weight_work_gpu = None
                            finally:
                                if carrier_owned and candidate_carrier_gpu is not None:
                                    _facade()._destroy_work_item(candidate_carrier_gpu)
                                if weight_work_gpu is not None:
                                    _facade()._destroy_work_item(weight_work_gpu)
                    finally:
                        with gpu_hardware_lock:
                            _facade()._destroy_work_item(supp_aligned_linear_gpu)
                        _facade()._destroy_work_item_except(
                            supp_work_item,
                            supp_aligned_linear_gpu,
                        )
                    continue
                if weight_engine == "spatial_fusion":
                    weight_slot = _take_spatial_weight_slot()
                    if weight_slot is None:
                        _facade()._destroy_work_item(supp_aligned_linear_gpu)
                        _facade()._destroy_work_item_except(supp_work_item, supp_aligned_linear_gpu)
                        break
                    with gpu_hardware_lock:
                        supp_work_rgb_gpu = supp_work_item
                        try:
                            taichi_aot.cvtColor(
                                supp_work_rgb_gpu,
                                taichi_aot.COLOR_RGB2GRAY,
                                dst=weightnet_gray_gpu,
                                return_gpu=True,
                            )
                            generate_spatial_weights_taichi(
                                current_image=weightnet_gray_gpu,
                                reference_image=ref_spatial_gray_gpu,
                                weight_map_sum=weight_slot,
                                base_window=0,
                                stability_map=None,
                                row_starts=spatial_row_starts,
                                col_starts=spatial_col_starts,
                                tile_h=spatial_tile_h,
                                tile_w=spatial_tile_w,
                                noise_sigma=spatial_noise_sigma,
                                motion_sensitivity=spatial_motion_sens,
                                noise_offset_factor=spatial_noise_offset,
                                equalize_brightness=False,
                                buffer_provider=None,
                                scratch_cache=spatial_scratch,
                                row_starts_gpu=spatial_rows_gpu,
                                col_starts_gpu=spatial_cols_gpu,
                                spatial_stride_h=max(
                                    1,
                                    int(spatial_tile_h * (1.0 - spatial_overlap)),
                                ),
                                spatial_stride_w=max(
                                    1,
                                    int(spatial_tile_w * (1.0 - spatial_overlap)),
                                ),
                                ghost_penalty=ghost_penalty,
                                ghost_cutoff=ghost_cutoff,
                                postprocess_in_place=True,
                            )
                        finally:
                            if (
                                supp_work_rgb_gpu is not None
                                and supp_work_rgb_gpu is not supp_aligned_linear_gpu
                            ):
                                _facade()._destroy_work_item(supp_work_rgb_gpu)
                        weight_work_item = weight_slot
                        alpha_mean = 1.0
                elif weight_engine == "average":
                    weight_work_item = average_weight_gpu
                    alpha_mean = 1.0
                else:
                    # DirectML ONNX AI inference runs asynchronously on dedicated GPU
                    # WITHOUT holding gpu_hardware_lock, fully overlapping with Taichi alignment!
                    supp_work_rgb_np = supp_work_item
                    weight_work_np, alpha_mean = infer_single_support_weight_map(
                        session,
                        ref_work_rgb_np,
                        supp_work_rgb_np,
                        tile_size=tile_size,
                        overlap=overlap,
                        ghost_penalty=ghost_penalty,
                        ghost_cutoff=ghost_cutoff,
                        chroma_sensitivity=chroma_sensitivity,
                        stop_event=stop_event,
                        return_scalar=(weightnet_channels == 1),
                    )
                    upload_workspace = (
                        weightnet_upload_workspaces[curr_idx & 1]
                        if weightnet_upload_workspaces is not None
                        else None
                    )
                    if upload_workspace is not None:
                        weight_work_item = upload_workspace.stage(weight_work_np)
                    else:
                        weight_work_item = np.ascontiguousarray(
                            weight_work_np[0]
                            if weightnet_channels == 1
                            else np.transpose(weight_work_np, (1, 2, 0)),
                            dtype=np.float32,
                        )
                    del weight_work_np

                queued = False
                while not _workers_stopped():
                    if pipeline_error is not None:
                        _facade()._destroy_work_item(supp_aligned_linear_gpu)
                        if (
                            hasattr(weight_work_item, "destroy")
                            and not _is_persistent_weight(weight_work_item)
                        ):
                            _facade()._destroy_work_item(weight_work_item)
                        _release_spatial_weight_slot(weight_work_item)
                        weight_slot = None
                        return
                    try:
                        weighted_queue.put(
                            (
                                curr_idx,
                                curr_name,
                                supp_aligned_linear_gpu,
                                weight_work_item,
                                alpha_mean,
                            ),
                            timeout=0.05,
                        )
                        queued = True
                        weight_slot = None
                        break
                    except queue.Full:
                        continue
                if not queued:
                    _facade()._destroy_work_item(supp_aligned_linear_gpu)
                    if (
                        hasattr(weight_work_item, "destroy")
                        and not _is_persistent_weight(weight_work_item)
                    ):
                        _facade()._destroy_work_item(weight_work_item)
                    _release_spatial_weight_slot(weight_work_item)
                    weight_slot = None
                    return
        except Exception as exc:
            _release_spatial_weight_slot(weight_slot)
            weight_slot = None
            _set_error(exc)
        finally:
            _put_stage_end(weighted_queue)

    is_thread_affine = (str(getattr(engine, "arch", "")).lower() in ("opengl", "gles")
                        or getattr(session, "runtime", None) == "taichi_aot")

    if is_thread_affine:
        # Context-affine backends (OpenGL/GLES) execute all GPU work synchronously on the context-owner thread
        threads = []

        processed_count = 0
        try:
            for curr_idx, supp_linear_np in _iter_in_processing_supports(
                range(1, num_images),
                _load_host_support,
                disposer=lambda payload: payload.close(),
                prepare=rgb_provider.decode_support_bytes_host,
            ):
                if pipeline_error is not None:
                    raise pipeline_error
                curr_name = Path(image_paths[curr_idx]).name
                if _workers_stopped():
                    _facade()._destroy_work_item(supp_linear_np)
                    break

                supp_linear_gpu = engine.upload(supp_linear_np)
                del supp_linear_np

                # OpenGL/GLES owns one native context thread.  Keep any
                # source-size normalization on that owner thread instead of
                # calling a native resize graph from the host preloader.
                if is_thread_affine and tuple(supp_linear_gpu.shape[:2]) != (
                    target_h,
                    target_w,
                ):
                    resized_gpu = taichi_aot.resize(
                        supp_linear_gpu,
                        (target_w, target_h),
                        interpolation=taichi_aot.INTER_LINEAR,
                        return_gpu=True,
                    )
                    _facade()._destroy_work_item(supp_linear_gpu)
                    supp_linear_gpu = resized_gpu

                if not needs_analysis:
                    # Average + no alignment can pass the full-resolution carrier
                    # through the existing context-affine queue directly.
                    supp_analysis_flow_gpu = supp_linear_gpu
                    supp_analysis_sec_gpu = supp_linear_gpu
                else:
                    supp_analysis_flow_gpu = _facade().prepare_analysis_proxy_gpu(
                        supp_linear_gpu,
                        work_shape=geometry.align_shape,
                        analysis_params=analysis_params,
                        in_place=True,
                    )

                    if weight_engine == "fusionet":
                        if geometry.weight_shape == geometry.align_shape:
                            supp_analysis_sec_gpu = supp_analysis_flow_gpu
                        else:
                            supp_analysis_sec_gpu = _facade().prepare_analysis_proxy_gpu(
                                supp_linear_gpu,
                                work_shape=geometry.weight_shape,
                                analysis_params=weight_analysis_params,
                            )
                    elif weight_engine == "spatial_fusion":
                        supp_analysis_sec_gpu = _facade().prepare_analysis_proxy_gpu(
                            supp_linear_gpu,
                            work_shape=geometry.weight_shape,
                            analysis_params=None,
                        )
                    elif (weight_work_h, weight_work_w) != (target_h, target_w):
                        supp_analysis_sec_gpu = taichi_aot.resize(
                            supp_linear_gpu,
                            (weight_work_w, weight_work_h),
                            interpolation=taichi_aot.INTER_AREA,
                            return_gpu=True,
                        )
                    else:
                        supp_analysis_sec_gpu = supp_linear_gpu

                # Dual-Warp on GPU (Primary in full-res 12MP, Secondary directly in weight-res)
                if not needs_analysis:
                    if _workers_stopped():
                        raise RuntimeError("Alignment cancelled.")
                    supp_aligned_linear_gpu = supp_linear_gpu
                    supp_aligned_sec_gpu = supp_linear_gpu
                else:
                    supp_aligned_linear_gpu, supp_aligned_sec_gpu = (
                        aligner.align_frame(
                            supp_linear_gpu,
                            analysis_frame_gpu=supp_analysis_flow_gpu,
                            secondary_frame_to_warp=supp_analysis_sec_gpu,
                            stop_event=stop_event,
                            return_gpu=True,
                        )
                    )
                if supp_aligned_linear_gpu is not supp_linear_gpu:
                    _facade()._destroy_work_item(supp_linear_gpu)
                if (
                    supp_analysis_flow_gpu is not supp_linear_gpu
                    and supp_analysis_flow_gpu is not supp_aligned_sec_gpu
                ):
                    _facade()._destroy_work_item(supp_analysis_flow_gpu)
                if (
                    supp_analysis_sec_gpu is not supp_linear_gpu
                    and supp_analysis_sec_gpu is not supp_analysis_flow_gpu
                    and supp_analysis_sec_gpu is not supp_aligned_sec_gpu
                ):
                    _facade()._destroy_work_item(supp_analysis_sec_gpu)

                if (
                    weight_engine == "fusionet"
                    and str(denoising_mode).strip().lower() == "deep_analysis"
                ):
                    from ...patch_process.multi_patch import CandidateTelemetry

                    if patch_offsets is None:
                        raise RuntimeError("Deep Analysis search offsets were not initialized")
                    telemetry = CandidateTelemetry()
                    proxy_host = (
                        supp_aligned_sec_gpu
                        if getattr(session, "runtime", None) == "taichi_aot"
                        else supp_aligned_sec_gpu.to_numpy()
                        if hasattr(supp_aligned_sec_gpu, "to_numpy")
                        else np.asarray(supp_aligned_sec_gpu)
                    )
                    support_proxy_chw = _facade()._multi_patch_weightnet_input(
                        proxy_host,
                        channels=weightnet_channels,
                        transfer_map=ref_transfer_map,
                    )
                    del proxy_host
                    try:
                        options = dict(
                            max_neighbors=max_neighbor_candidates,
                            tile_size=tile_size,
                            overlap=overlap,
                            ghost_penalty=ghost_penalty,
                            ghost_cutoff=ghost_cutoff,
                            chroma_sensitivity=chroma_sensitivity,
                            stop_event=stop_event,
                            telemetry=telemetry,
                        )
                        for candidate_index, (
                            rank_indices,
                            _rank_valid,
                            confidence,
                            alpha,
                            candidate_count,
                        ) in enumerate(
                            _facade()._iter_deep_support_candidate_maps(
                                session,
                                ref_work_rgb_np,
                                support_proxy_chw,
                                patch_offsets,
                                **options,
                            )
                        ):
                            if _workers_stopped():
                                raise RuntimeError(
                                    "RGB Deep Analysis cancelled during candidate maps"
                                )
                            carrier_owned = rank_indices is not None
                            candidate_carrier_gpu = weight_gpu = None
                            try:
                                if carrier_owned:
                                    candidate_carrier_gpu = _remap_rgb_rank_carrier(
                                        supp_aligned_linear_gpu,
                                        rank_indices,
                                        patch_offsets,
                                        telemetry,
                                    )
                                else:
                                    candidate_carrier_gpu = supp_aligned_linear_gpu
                                weight_gpu = _facade()._upload_weightnet_confidence(
                                    engine, confidence
                                )
                                rgb_provider.accumulate(
                                    candidate_carrier_gpu,
                                    transform=None,
                                    weight_map=weight_gpu,
                                )
                                if getattr(session, "runtime", None) != "taichi_aot":
                                    engine.sync()
                                alpha_total += alpha / candidate_count
                            finally:
                                if carrier_owned and candidate_carrier_gpu is not None:
                                    _facade()._destroy_work_item(candidate_carrier_gpu)
                                if weight_gpu is not None:
                                    _facade()._destroy_work_item(weight_gpu)
                        processed_count += 1
                    finally:
                        released_ids = set()
                        for buffer in (supp_aligned_sec_gpu, supp_aligned_linear_gpu):
                            if buffer is not None and id(buffer) not in released_ids:
                                _facade()._destroy_work_item(buffer)
                                released_ids.add(id(buffer))
                        del support_proxy_chw

                    if telemetry.candidate_count == 0:
                        raise RuntimeError("Deep Analysis produced no RGB candidates")
                    if progress_callback:
                        progress_callback(
                            _merge_percent(processed_count, total_supp),
                            ui=f"Memproses {curr_idx}/{total_supp}...",
                            console=f"Memproses frame {curr_idx}/{total_supp} ({curr_name}) [Deep Analysis]...",
                        )
                    print(
                        "[FusionNet MultiPatch][RGB] "
                        f"backend={getattr(engine, 'arch', 'unknown')} "
                        f"shape={geometry.weight_shape} dtype=float32 "
                        f"maps={telemetry.candidate_count} "
                        f"search_candidates={telemetry.search_candidate_count} "
                        f"stages={telemetry.summary()}"
                    )
                    pipeline_telemetry.emit(f"blend_{curr_idx}")
                    _release_in_processing_slot(curr_idx)
                    if _workers_stopped():
                        break
                    continue
                if weight_engine == "spatial_fusion":
                    taichi_aot.cvtColor(
                        supp_aligned_sec_gpu,
                        taichi_aot.COLOR_RGB2GRAY,
                        dst=weightnet_gray_gpu,
                        return_gpu=True,
                    )

                    weight_work_2d_gpu = spatial_weight_post_a_gpu
                    generate_spatial_weights_taichi(
                        current_image=weightnet_gray_gpu,
                        reference_image=ref_spatial_gray_gpu,
                        weight_map_sum=weight_work_2d_gpu,
                        base_window=0,
                        stability_map=None,
                        row_starts=spatial_row_starts,
                        col_starts=spatial_col_starts,
                        tile_h=spatial_tile_h,
                        tile_w=spatial_tile_w,
                        noise_sigma=spatial_noise_sigma,
                        motion_sensitivity=spatial_motion_sens,
                        noise_offset_factor=spatial_noise_offset,
                        equalize_brightness=False,
                        buffer_provider=None,
                        scratch_cache=spatial_scratch,
                        row_starts_gpu=spatial_rows_gpu,
                        col_starts_gpu=spatial_cols_gpu,
                        spatial_stride_h=max(
                            1, int(spatial_tile_h * (1.0 - spatial_overlap))
                        ),
                        spatial_stride_w=max(
                            1, int(spatial_tile_w * (1.0 - spatial_overlap))
                        ),
                        ghost_penalty=ghost_penalty,
                        ghost_cutoff=ghost_cutoff,
                        postprocess_in_place=True,
                    )
                    if supp_aligned_sec_gpu is not supp_aligned_linear_gpu:
                        _facade()._destroy_work_item(supp_aligned_sec_gpu)
                    weight_work_item = weight_work_2d_gpu
                    alpha_mean = 1.0
                elif weight_engine == "average":
                    if (
                        supp_aligned_sec_gpu is not None
                        and supp_aligned_sec_gpu is not supp_aligned_linear_gpu
                    ):
                        _facade()._destroy_work_item(supp_aligned_sec_gpu)
                    weight_work_item = average_weight_gpu
                    alpha_mean = 1.0
                else:
                    weightnet_input_gpu = supp_aligned_sec_gpu
                    if weightnet_channels == 1 and getattr(session, "runtime", None) != "taichi_aot":
                        taichi_aot.cvtColor(
                            supp_aligned_sec_gpu,
                            taichi_aot.COLOR_RGB2GRAY,
                            dst=weightnet_gray_gpu,
                            return_gpu=True,
                        )
                        weightnet_input_gpu = weightnet_gray_gpu
                    supp_work_rgb_np = _facade().prepare_weightnet_support_input(
                        weightnet_input_gpu,
                        ref_transfer_map,
                        workspace=weightnet_support_workspace,
                    )
                    _facade()._destroy_work_item(supp_aligned_sec_gpu)
                    weight_work_np, alpha_mean = infer_single_support_weight_map(
                        session,
                        ref_work_rgb_np,
                        supp_work_rgb_np,
                        tile_size=tile_size,
                        overlap=overlap,
                        ghost_penalty=ghost_penalty,
                        ghost_cutoff=ghost_cutoff,
                        chroma_sensitivity=chroma_sensitivity,
                        stop_event=stop_event,
                        return_scalar=(weightnet_channels == 1),
                    )
                    weight_work_item = (
                        _facade()._upload_weightnet_confidence(engine, weight_work_np)
                        if getattr(session, "runtime", None) == "taichi_aot"
                        else (
                        weightnet_upload_workspace.stage(weight_work_np)
                        if weightnet_upload_workspace is not None
                        else np.ascontiguousarray(
                            weight_work_np[0]
                            if weightnet_channels == 1
                            else np.transpose(weight_work_np, (1, 2, 0)),
                            dtype=np.float32,
                        ))
                    )
                    del weight_work_np

                processed_count += 1
                alpha_total += alpha_mean

                if progress_callback:
                    align_lbl = (
                        alignment_plan
                        if alignment_plan not in ("none", "off", "")
                        else "No Alignment"
                    )
                    progress_callback(
                        _merge_percent(processed_count, total_supp),
                        ui=f"Memproses {curr_idx}/{total_supp}...",
                        console=f"Memproses frame {curr_idx}/{total_supp} ({curr_name}) [{align_lbl} + Fusion]...",
                    )

                if isinstance(weight_work_item, taichi_aot.TaichiGPUBuffer):
                    weight_work_gpu = weight_work_item
                else:
                    weight_work_gpu = engine.upload(weight_work_item)
                    del weight_work_item

                rgb_provider.accumulate(
                    supp_aligned_linear_gpu,
                    transform=None,
                    weight_map=weight_work_gpu,
                )

                _facade()._destroy_work_item(supp_aligned_linear_gpu)
                if not _is_persistent_weight(weight_work_gpu):
                    _facade()._destroy_work_item(weight_work_gpu)
                if weight_engine != "spatial_fusion" and getattr(session, "runtime", None) != "taichi_aot":
                    engine.sync()
                if processed_count % 2 == 0 or processed_count == total_supp:
                    gc.collect()
                    if sys.platform == "win32":
                        try:
                            import ctypes
                            ctypes.windll.kernel32.SetProcessWorkingSetSize(
                                ctypes.windll.kernel32.GetCurrentProcess(), -1, -1
                            )
                        except Exception:
                            pass

                print(
                    f"[GPU Flow Coordinator] Frame {curr_idx}/{total_supp} ({curr_name}) blended "
                    f"(alpha={alpha_mean:.3f})"
                )
                pipeline_telemetry.emit(f"blend_{curr_idx}")
                _release_in_processing_slot(curr_idx)
        finally:
            runtime.close_streams()
            _release_all_in_processing_slots()
    else:
        # Launch background stages for thread-safe backends (CUDA/Vulkan)
        t_uploader = runtime.start_worker(
            target=_uploader_worker, name="Stage1.5_Uploader"
        )
        t_aligner = runtime.start_worker(
            target=_alignment_worker, name="Stage2_Aligner"
        )
        threads = [t_uploader, t_aligner]

        t_weight = None
        if not alignment_only and (
            session is not None or weight_engine in ("spatial_fusion", "average")
        ):
            t_weight = runtime.start_worker(
                target=_weight_inference_worker, name="Stage3_Weight"
            )
            threads.append(t_weight)

        # If only alignment is requested, wait for stages and return reference image
        if alignment_only:
            t_uploader.join()
            t_aligner.join()
            runtime.stop_workers()
            _release_all_in_processing_slots()
            ref_out = ref_gpu.to_numpy()
            buffer_session.release_all_except()
            return _facade()._export_result(ref_out), 1.0

        processed_count = 0

        try:
            # --------------------------------------------------------------
            # Stage 4: GPU Accumulator Blending (Runs in Main Thread)
            # --------------------------------------------------------------
            while not _is_stopped():
                if pipeline_error is not None:
                    raise pipeline_error

                try:
                    item = weighted_queue.get(timeout=0.05)
                except queue.Empty:
                    continue

                if item is _SENTINEL:
                    if pipeline_error is not None:
                        raise pipeline_error
                    break

                if len(item) == 9:
                    (
                        curr_idx,
                        curr_name,
                        candidate_carrier_gpu,
                        weight_work_gpu,
                        candidate_alpha,
                        candidate_index,
                        candidate_count,
                        candidate_telemetry,
                        carrier_owned,
                    ) = item
                    alpha_total += float(candidate_alpha)
                    is_last_candidate = candidate_index + 1 == candidate_count
                    if is_last_candidate:
                        processed_count += 1
                    if progress_callback and is_last_candidate:
                        align_lbl = (
                            alignment_plan
                            if alignment_plan not in ("none", "off", "")
                            else "No Alignment"
                        )
                        progress_callback(
                            _merge_percent(processed_count, total_supp),
                            ui=f"Memproses {curr_idx}/{total_supp}...",
                            console=(
                                f"Memproses frame {curr_idx}/{total_supp} ({curr_name}) "
                                f"[{align_lbl} + Deep Analysis]..."
                            ),
                        )
                    with gpu_hardware_lock:
                        if _is_stopped():
                            if carrier_owned:
                                _facade()._destroy_work_item(candidate_carrier_gpu)
                            _facade()._destroy_work_item(weight_work_gpu)
                            break
                        accumulate_started = time.perf_counter()
                        try:
                            rgb_provider.accumulate(
                                candidate_carrier_gpu,
                                transform=None,
                                weight_map=weight_work_gpu,
                            )
                            candidate_telemetry.record(
                                "rgb_accumulation_device", accumulate_started
                            )
                            engine.sync()
                        finally:
                            if carrier_owned:
                                _facade()._destroy_work_item(candidate_carrier_gpu)
                            _facade()._destroy_work_item(weight_work_gpu)
                    if is_last_candidate:
                        backend_details = {}
                        try:
                            from taichi_vision.taichi_aot import backend_info

                            backend_details = backend_info()
                        except Exception:
                            backend_details = {
                                "backend": getattr(engine, "arch", "unknown")
                            }
                        print(
                            "[FusionNet MultiPatch][RGB] "
                            f"backend={getattr(engine, 'arch', 'unknown')} device={backend_details} "
                            f"shape={geometry.weight_shape} dtype=float32 "
                            f"weightnet={getattr(session, 'runtime', 'onnx')} "
                            f"stages={candidate_telemetry.summary()}"
                        )
                        print(
                            f"[GPU Flow Coordinator] Frame {curr_idx}/{total_supp} "
                            f"({curr_name}) Deep Analysis blended "
                            f"(candidates={candidate_count}, in_processing={len(in_processing_active)})"
                        )
                        pipeline_telemetry.emit(f"blend_{curr_idx}")
                        _release_in_processing_slot(curr_idx)
                    continue

                (
                    curr_idx,
                    curr_name,
                    supp_aligned_linear_gpu,
                    weight_work_item,
                    alpha_mean,
                ) = item

                processed_count += 1
                alpha_total += alpha_mean

                if progress_callback:
                    align_lbl = (
                        alignment_plan
                        if alignment_plan not in ("none", "off", "")
                        else "No Alignment"
                    )
                    progress_callback(
                        _merge_percent(processed_count, total_supp),
                        ui=f"Memproses {curr_idx}/{total_supp}...",
                        console=f"Memproses frame {curr_idx}/{total_supp} ({curr_name}) [{align_lbl} + Fusion]...",
                    )

                with gpu_hardware_lock:
                    if _is_stopped():
                        _facade()._destroy_work_item(supp_aligned_linear_gpu)
                        if _is_persistent_weight(weight_work_item):
                            _release_spatial_weight_slot(weight_work_item)
                        elif hasattr(weight_work_item, "destroy"):
                            _facade()._destroy_work_item(weight_work_item)
                        break

                    if isinstance(weight_work_item, taichi_aot.TaichiGPUBuffer):
                        weight_work_gpu = weight_work_item
                    else:
                        weight_work_gpu = engine.upload(weight_work_item)
                        del weight_work_item

                    rgb_provider.accumulate(
                        supp_aligned_linear_gpu,
                        transform=None,
                        weight_map=weight_work_gpu,
                    )

                    if weight_engine == "spatial_fusion":
                        _release_spatial_weight_slot(weight_work_gpu)

                    _facade()._destroy_work_item(supp_aligned_linear_gpu)
                    if not _is_persistent_weight(weight_work_gpu):
                        _facade()._destroy_work_item(weight_work_gpu)
                    if processed_count % 2 == 0 or processed_count == total_supp:
                        gc.collect()
                        if sys.platform == "win32":
                            try:
                                import ctypes
                                ctypes.windll.kernel32.SetProcessWorkingSetSize(
                                    ctypes.windll.kernel32.GetCurrentProcess(), -1, -1
                                )
                            except Exception:
                                pass

                print(
                    f"[GPU Flow Coordinator] Frame {curr_idx}/{total_supp} ({curr_name}) blended "
                    f"(alpha={alpha_mean:.3f}, in_processing={len(in_processing_active)})"
                )
                pipeline_telemetry.emit(f"blend_{curr_idx}")
                _release_in_processing_slot(curr_idx)

        finally:
            runtime.stop_workers()
            # Drain and destroy any remaining GPU buffers in queues immediately
            for q in (vram_queue, aligned_queue, weighted_queue):
                while not q.empty():
                    try:
                        val = q.get_nowait()
                        if val is not _SENTINEL and isinstance(val, tuple):
                            for index, el in enumerate(val):
                                if (
                                    len(val) == 9
                                    and index == 2
                                    and not bool(val[8])
                                ):
                                    # The weight worker owns the unshifted
                                    # source carrier across candidate entries.
                                    continue
                                if _is_persistent_weight(el):
                                    _release_spatial_weight_slot(el)
                                    continue
                                if (
                                    el is not None
                                    and hasattr(el, "destroy")
                                    and not _is_persistent_weight(el)
                                ):
                                    try:
                                        _facade()._destroy_work_item(el)
                                    except Exception:
                                        pass
                    except Exception:
                        pass

            _release_all_in_processing_slots()

            if _is_stopped() or pipeline_error is not None:
                try:
                    if pipeline_error is None:
                        # Cancellation retains the partial accumulator for output.
                        buffer_session.release_all_except(ref_gpu, sum_img_gpu, weight_sum_gpu)
                    else:
                        buffer_session.release_all_except()
                    if session is not None and hasattr(session, "clear_cache"):
                        session.clear_cache()
                except Exception:
                    pass

                # If an actual error occurred, destroy accumulation buffers
                if pipeline_error is not None:
                    try:
                        engine.sync()
                        engine.get_device_block_cache().clear()
                    except Exception:
                        pass
                    gc.collect()

    print(
        "[GPU Pipeline] In-Processing Queue peak: "
        f"{in_processing_peak}/{runtime.in_processing_depth} support frames"
    )

    if pipeline_error is not None:
        print(f"[GPU Pipeline] Pipeline aborted due to error: {pipeline_error}")
        return None, 0.0

    if _is_stopped():
        print(
            f"[GPU Pipeline] Graceful stop active. Finalizing partial burst of "
            f"{1 + processed_count}/{total_supp + 1} accumulated frames as valid output..."
        )

    # ------------------------------------------------------------------
    # PHASE 7: Final Linear Normalization (Pure Linear RAW Data)
    # ------------------------------------------------------------------
    if progress_callback:
        progress_callback(
            PROGRESS_FINALIZE_MAX,
            ui="Menyelesaikan proses...",
            console="Finalisasi GPU-resident fusion & normalisasi pembagian bobot...",
        )

    # The phase boundary has three live GPU resources: carrier/accumulator
    # (aliased), scalar/vector weights, and reference. No per-engine cleanup list.
    try:
        buffer_session.release_all_except(ref_gpu, sum_img_gpu, weight_sum_gpu)
        if session is not None and hasattr(session, "clear_cache"):
            session.clear_cache()
    except Exception:
        pass
    if "ref_work_rgb_np" in locals() and ref_work_rgb_np is not None:
        del ref_work_rgb_np
    try:
        engine.sync()
    except Exception:
        pass

    # Normalization with reference fallback
    # Directly passing ref_gpu (already resident in VRAM, 0 overhead!)
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi import (
        mean_division_vec3_weight_taichi,
    )

    if getattr(weight_sum_gpu, "ndim", 2) == 2 or (len(weight_sum_gpu.shape) == 2):
        # SpatialFusion is luma-weighted.  Use the scalar-weight graph
        # directly; broadcasting to HWC3 would add a full-frame readback,
        # host allocation, and upload at the peak-memory point.
        _final_linear_gpu = mean_division_vec3_weight_taichi(
            sum_img=sum_img_gpu,
            sum_weight=weight_sum_gpu,
            ref_img=ref_gpu,
            dst=sum_img_gpu,
        )
        _facade()._destroy_work_item(weight_sum_gpu)
    else:
        _final_linear_gpu = mean_division_vec3_weight_taichi(
            sum_img=sum_img_gpu,
            sum_weight=weight_sum_gpu,
            ref_img=ref_gpu,
            dst=sum_img_gpu,
        )
        _facade()._destroy_work_item(weight_sum_gpu)

    # The resident RGB path intentionally aliases the reference as the
    # accumulator.  With in-place normalization, destroying ref_gpu here
    # would also destroy the final destination before its readback.  Only
    # release it when it is a distinct allocation.
    if getattr(ref_gpu, "handle", None) != getattr(
        _final_linear_gpu, "handle", None
    ):
        _facade()._destroy_work_item(ref_gpu)

    result_hwc = np.ascontiguousarray(_final_linear_gpu.to_numpy(), dtype=np.float32)
    _facade()._destroy_work_item(_final_linear_gpu)

    # Synchronize the retired handles, but retain the engine pools: subsequent
    # bursts can acquire same-shape buffers without another VRAM allocation.
    try:
        engine.sync()
    except Exception:
        pass

    mean_alpha = float(alpha_total / max(1, total_supp))
    _facade()._destroy_work_item(rgb_provider)
    print(
        f"[GPU Pipeline] Complete: shape={result_hwc.shape} "
        f"mean_alpha={mean_alpha:.4f} (reusable VRAM pools retained)"
    )
    pipeline_telemetry.emit("complete")

    return _facade()._export_result(result_hwc), mean_alpha
