"""RAW CFA accumulation through the shared resident frame loop.

``_run_shared_raw_provider_pipeline`` drives analysis, alignment, WeightNet
inference, and CFA accumulation for RAW Native.  Sibling implementations are
reached through :func:`pipeline_process.facade.api` so
``monkeypatch.setattr`` on the resident facade keeps reaching the live call
path.
"""

import queue
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Optional, Sequence, Tuple

import numpy as np

from ...pipeline_runtime import (
    PipelineRuntime,
    current_pipeline_runtime,
    resolve_in_processing_depth,
    resolve_prefetch_depth,
    runtime_entrypoint,
)
from .analysis import ANALYSIS_AUTO_ENHANCE_MODE
from .contracts import ResidentGeometry, scale_homography
from .facade import api as _facade
from .telemetry import PipelineTelemetry

__all__ = ["_run_shared_raw_provider_pipeline"]

@runtime_entrypoint
def _run_shared_raw_provider_pipeline(
    image_paths: Sequence[str | Path],
    session=None,
    *,
    telemetry: Optional[bool] = None,
    weight_engine: str,
    alignment_plan: str,
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
    tile_size: int = 256,
    overlap: float = 0.30,
    ghost_penalty: float = 1.0,
    ghost_penalty_min: Optional[float] = None,
    ghost_cutoff: float = 0.05,
    chroma_sensitivity: float = 6.0,
    weightnet_input_channels: Optional[int] = None,
    stop_event=None,
    progress_callback: Optional[Callable[..., None]] = None,
    auto_params: Optional[dict] = None,
    prefetch_depth: Optional[int] = None,
    source_descriptor=None,
    _runtime: Optional[PipelineRuntime] = None,
    **_unused,
) -> Tuple[Any, float]:
    """Run RAW CFA accumulation through the shared resident frame loop.

    The resident executor owns analysis, alignment, weight generation, queue
    lifetime, and cleanup.  ``RawPipelineProvider`` owns only CFA carrier I/O
    and phase-safe accumulation/finalization.
    """

    normalized_engine = str(weight_engine).strip().lower()
    normalized_denoising_mode = str(denoising_mode).strip().lower().replace(" ", "_")
    if normalized_denoising_mode not in {"standard", "deep_analysis"}:
        raise ValueError(f"Unsupported FusionNet denoising mode: {denoising_mode!r}")
    if normalized_denoising_mode == "deep_analysis" and normalized_engine != "fusionet":
        raise ValueError("Deep Analysis mode is available only with FusionNet")
    denoising_mode = normalized_denoising_mode
    # Retain the argument for compatibility. Stages below explicitly use
    # analysis mode for alignment and natural mode for FusionNet weight input.
    analysis_auto_enhance_mode = ANALYSIS_AUTO_ENHANCE_MODE
    if normalized_engine not in ("average", "spatial_fusion", "fusionet"):
        raise NotImplementedError(
            "RAW Native supports Average, SpatialFusion, and FusionNet."
        )
    if len(image_paths) < 2:
        raise ValueError("RAW Native fusion requires at least two DNG frames")

    from .raw_pipeline.provider import RawPipelineProvider
    from taichi_vision import taichi_aot
    taichi_aot = _facade()._managed_api(taichi_aot)
    from taichi_vision.taichi_aot import get_engine
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi import (
        SpatialScratchCache,
        generate_spatial_weights_taichi,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi.compute_spatial import (
        _compute_tile_starts,
    )
    from ..fusionet_engine.weightnet_inference import (
        DEFAULT_WEIGHTNET_ONNX,
        infer_single_support_weight_map,
    )
    from taichi_vision.taichi_algorithm.spatial_fusion import resolve_spatial_thresholds

    engine = _facade()._managed_api(get_engine())
    runtime = _runtime or current_pipeline_runtime()
    owns_runtime = runtime is None
    if runtime is None:
        runtime = PipelineRuntime(
            prefetch_depth=resolve_prefetch_depth(prefetch_depth),
            in_processing_depth=resolve_in_processing_depth(),
            stop_event=stop_event,
            progress_callback=progress_callback,
            source_descriptor=source_descriptor,
        )
    buffer_session = runtime.ensure_session(engine)
    engine = buffer_session.managed_api(engine)
    taichi_aot = buffer_session.managed_api(taichi_aot)
    weightnet_channels = _facade()._resolve_weightnet_input_channels(
        session, weightnet_input_channels
    )
    provider = buffer_session.own(RawPipelineProvider(image_paths, weight_engine=normalized_engine))
    pipeline_telemetry = PipelineTelemetry(engine, enabled=telemetry)
    aligner = None
    ref_proxy_full_gpu = None
    ref_analysis_gpu = None
    ref_weight_analysis_gpu = None
    ref_spatial_gray_gpu = None
    spatial_rows_gpu = None
    spatial_cols_gpu = None
    spatial_weight_work_gpu = None
    spatial_scratch = None
    spatial_rows = None
    spatial_cols = None
    fusion_ref_work_chw = None
    fusion_transfer_map = None
    weightnet_gray_gpu = None
    weightnet_support_workspace = None
    weightnet_upload_workspace = None
    ref_frame = None
    analysis_params = None
    weight_analysis_params = None
    spatial_state = None
    mean_alpha = 1.0

    def _cancelled():
        if stop_event is None:
            return False
        if hasattr(stop_event, "is_set"):
            return bool(stop_event.is_set())
        return bool(stop_event()) if callable(stop_event) else bool(stop_event)

    def _emit(percent, ui, console):
        if progress_callback is None:
            return
        try:
            progress_callback(percent, ui=ui, console=console)
        except TypeError:
            progress_callback(percent, console)

    def _warp_analysis(proxy_gpu, transform, shape):
        if transform is None:
            return proxy_gpu
        if isinstance(transform, np.ndarray) and transform.ndim == 2 and transform.shape == (3, 3):
            work_h, work_w = (int(shape[0]), int(shape[1]))
            scaled = scale_homography(
                transform,
                source_shape=geometry.full_shape,
                destination_shape=(work_h, work_w),
            )
            return taichi_aot.warp_perspective(
                proxy_gpu,
                scaled,
                (work_w, work_h),
                return_gpu=True,
            )
        return taichi_aot.remap_with_flow(
            proxy_gpu,
            transform,
            int(shape[0]),
            int(shape[1]),
            return_gpu=True,
        )

    try:
        buffer_session = runtime.ensure_session(engine)
        pipeline_telemetry.emit("start")
        ref_frame = provider.load_reference()
        reference = ref_frame.carrier
        geometry = ResidentGeometry.resolve(
            reference.shape,
            align_scale=(
                float(flownet_work_scale)
                if flownet_work_scale is not None
                else float(work_scale)
            ),
            weight_scale=(
                float(weightnet_work_scale)
                if weightnet_work_scale is not None
                else float(work_scale)
            ),
            max_work_dimension=max_work_dimension,
        )
        needs_analysis = (
            str(alignment_plan).strip().lower()
            not in {"", "none", "no alignment", "no_alignment", "off"}
            or normalized_engine in ("spatial_fusion", "fusionet")
        )
        if normalized_engine == "spatial_fusion" or (
            normalized_engine == "fusionet" and weightnet_channels == 1
        ):
            weightnet_gray_gpu = buffer_session.own(
                engine.allocate(
                    geometry.weight_shape,
                    dtype=np.float32,
                    host_accessible=False,
                )
            )
        if normalized_engine == "fusionet" and getattr(session, "runtime", None) != "taichi_aot":
            weightnet_support_workspace = _facade()._WeightNetReadbackWorkspace(
                geometry.weight_shape, channels=weightnet_channels
            )
            weightnet_upload_workspace = _facade()._WeightNetUploadWorkspace(
                geometry.weight_shape, channels=weightnet_channels
            )
        ref_noise_score = None
        use_half_res = False
        if needs_analysis:
            from .raw_pipeline.provider import _demosaic_carrier_gpu

            carrier_h, carrier_w = ref_frame.carrier.samples.shape[:2]
            use_half_res = (
                geometry.align_shape[0] <= carrier_h // 2
                and geometry.align_shape[1] <= carrier_w // 2
                and geometry.weight_shape[0] <= carrier_h // 2
                and geometry.weight_shape[1] <= carrier_w // 2
            )
            ref_proxy_full_gpu = _demosaic_carrier_gpu(
                ref_frame.carrier, half_res=use_half_res
            )
            print(
                f"[RAW Native] Analysis demosaic: bilinear, "
                f"{'half-resolution' if use_half_res else 'full-resolution'}; "
                "final preview: Hamilton"
            )
            alignment_mode = ANALYSIS_AUTO_ENHANCE_MODE
            analysis_params = _facade()._resolve_engine_analysis_params(
                ref_proxy_full_gpu,
                weight_engine=normalized_engine,
                enabled=analysis_enhance,
                supplied=(auto_params if alignment_mode != "analysis" else None),
                mode=alignment_mode,
            )
            if normalized_engine == "fusionet":
                weight_analysis_params = analysis_params
            noise_analysis_params = (
                analysis_params if normalized_engine == "fusionet" else None
            )
            share_ref_weight_proxy = (
                normalized_engine == "fusionet"
                and geometry.weight_shape == geometry.align_shape
            )
            if normalized_engine in ("fusionet", "spatial_fusion") and not share_ref_weight_proxy:
                ref_weight_analysis_gpu = _facade().prepare_analysis_proxy_gpu(
                    ref_proxy_full_gpu,
                    work_shape=geometry.weight_shape,
                    analysis_params=(
                        weight_analysis_params
                        if normalized_engine == "fusionet"
                        else None
                    ),
                )
                if ref_weight_analysis_gpu is ref_proxy_full_gpu:
                    ref_weight_analysis_gpu = taichi_aot.copy(
                        ref_weight_analysis_gpu, return_gpu=True
                    )
            if analysis_params is not None:
                print(
                    "[RAW Native] Alignment AutoEnhance "
                    f"({alignment_mode}, uncapped gain): "
                    f"Gain={float(analysis_params.get('gain', 1.0)):.2f}x "
                    "(reference parameters reused for support alignment; "
                    "CFA fusion carrier remains unchanged)"
                )
            else:
                print(
                    "[RAW Native] Alignment AutoEnhance skipped; "
                    "alignment proxy remains linear"
                )
            if weight_analysis_params is not None:
                print(
                    "[RAW Native] FusionNet WeightNet AutoEnhance (analysis): "
                    f"Gain={float(weight_analysis_params.get('gain', 1.0)):.2f}x"
                )

            ref_analysis_gpu, ref_noise_score, ghost_penalty = (
                _facade().prepare_reference_analysis_and_noise(
                    ref_proxy_full_gpu,
                    work_shape=geometry.align_shape,
                    analysis_params=analysis_params,
                    ghost_penalty=ghost_penalty,
                    ghost_penalty_min=ghost_penalty_min,
                    in_place=share_ref_weight_proxy,
                    source_is_disposable=share_ref_weight_proxy,
                    noise_source_gpu=(
                        ref_proxy_full_gpu
                        if normalized_engine in ("fusionet", "spatial_fusion")
                        else None
                    ),
                    noise_analysis_params=noise_analysis_params,
                )
            )
            if share_ref_weight_proxy:
                ref_weight_analysis_gpu = ref_analysis_gpu
            if ref_proxy_full_gpu is not ref_analysis_gpu:
                _facade()._destroy_work_item(ref_proxy_full_gpu)
            ref_proxy_full_gpu = None

            ref_spatial_gray_gpu = None
            if normalized_engine == "spatial_fusion":
                (
                    tile, overlap_value, motion, noise_offset, noise_sigma, sigma_mode
                ) = _facade()._resolve_spatial_analysis_config(
                    spatial_config, tile_size=tile_size, overlap=overlap,
                    work_shape=geometry.weight_shape, noise_score=ref_noise_score,
                    is_raw=True,
                )
                print(
                    f"[RAW Native] SpatialFusion kernel parameters: tile={tile} "
                    f"overlap={overlap_value:.3f} motion_sensitivity={motion:.3f} "
                    f"(noise-aware) noise_sigma={noise_sigma:.6f} (mode={sigma_mode})"
                )
                spatial_rows = _compute_tile_starts(
                    geometry.weight_shape[0], tile, overlap=overlap_value
                )
                spatial_cols = _compute_tile_starts(
                    geometry.weight_shape[1], tile, overlap=overlap_value
                )
                spatial_rows_gpu = buffer_session.own(
                    taichi_aot.upload(np.asarray(spatial_rows, dtype=np.int32))
                )
                spatial_cols_gpu = buffer_session.own(
                    taichi_aot.upload(np.asarray(spatial_cols, dtype=np.int32))
                )
                spatial_weight_work_gpu = buffer_session.own(
                    engine.allocate(
                        geometry.weight_shape, dtype=np.float32, host_accessible=False
                    )
                )
                spatial_scratch = _facade()._own_component(SpatialScratchCache(), releaser=lambda cache: cache.clear())
                spatial_state = (tile, overlap_value, motion, noise_offset, noise_sigma)
            if normalized_engine == "spatial_fusion":
                ref_spatial_gray_gpu = buffer_session.own(
                    taichi_aot.cvtColor(
                        ref_weight_analysis_gpu,
                        taichi_aot.COLOR_RGB2GRAY,
                        return_gpu=True,
                    )
                )
                _facade()._destroy_work_item(ref_weight_analysis_gpu)
                ref_weight_analysis_gpu = None
                print(
                    "[RAW Native] SpatialFusion weight analysis: "
                    "linear proxy -> grayscale scratch; "
                    "CFA carrier unchanged"
                )
            if normalized_engine == "fusionet":
                if weightnet_channels == 1 and getattr(session, "runtime", None) != "taichi_aot":
                    taichi_aot.cvtColor(
                        ref_weight_analysis_gpu,
                        taichi_aot.COLOR_RGB2GRAY,
                        dst=weightnet_gray_gpu,
                        return_gpu=True,
                    )
                    ref_weight_input_gpu = weightnet_gray_gpu
                else:
                    ref_weight_input_gpu = ref_weight_analysis_gpu
                fusion_ref_work_chw, fusion_transfer_map = _facade().prepare_weightnet_reference_input(
                    ref_weight_input_gpu,
                    work_shape=geometry.weight_shape,
                    session=session,
                )
                if ref_weight_analysis_gpu is not ref_analysis_gpu:
                    _facade()._destroy_work_item(ref_weight_analysis_gpu)
                ref_weight_analysis_gpu = None
            print(
                "[GPU Pipeline] Shared RAW analysis: "
                f"full={geometry.full_shape} align={geometry.align_shape} "
                f"weight={geometry.weight_shape}"
            )

            if str(alignment_plan).strip().lower() not in {
                "", "none", "no alignment", "no_alignment", "off"
            }:
                aligner = _facade().create_resident_aligner(
                    alignment_plan,
                    ref_analysis_gpu,
                    work_scale=geometry.effective_align_scale,
                    full_shape=geometry.full_shape,
                    alignment_config=alignment_config,
                    noise_score=ref_noise_score,
                )

            # The aligner has derived its persistent features; weight analysis
            # was prepared from its independent natural/linear proxy above.
        _facade()._destroy_work_item(ref_analysis_gpu)
        ref_analysis_gpu = None

        provider.bind_accumulator(engine, ref_frame)
        pipeline_telemetry.emit("reference_loaded")
        total_supports = len(image_paths) - 1
        alpha_total = 0.0

        if denoising_mode == "deep_analysis":
            from ..patch_process.multi_patch import (
                CandidateTelemetry,
                candidate_flow_from_indices,
                search_candidate_offsets,
            )

            reference_offsets = search_candidate_offsets(
                geometry.full_shape,
                geometry.weight_shape,
                align_shape=geometry.align_shape,
                search_radius=patch_search_radius,
                patch_stride=2,
                preserve_cfa_phase=True,
            )
            # Give each selected local rank an equal share of the bounded
            # local-candidate confidence contribution.
            local_rank_weight_scale = 1.0 / float(
                max(1, int(max_neighbor_candidates)) ** 2
            )
            reference_telemetry = CandidateTelemetry()
            for rank_indices, _rank_valid, confidence, _rank_alpha in _facade()._iter_multi_patch_rank_maps(
                session,
                fusion_ref_work_chw,
                fusion_ref_work_chw,
                reference_offsets,
                max_neighbors=max_neighbor_candidates,
                tile_size=tile_size,
                overlap=overlap,
                ghost_penalty=ghost_penalty,
                ghost_cutoff=ghost_cutoff,
                chroma_sensitivity=chroma_sensitivity,
                stop_event=stop_event,
                telemetry=reference_telemetry,
            ):
                if _cancelled():
                    raise RuntimeError("RAW Deep Analysis cancelled during reference neighbors")
                flow_gpu = weight_gpu = None
                try:
                    flow_host = candidate_flow_from_indices(
                        rank_indices,
                        reference_offsets,
                        full_shape=geometry.full_shape,
                        flow_shape=geometry.align_shape,
                    )
                    flow_gpu = engine.upload(flow_host, is_vector=True)
                    weight_gpu = _facade()._upload_weightnet_confidence(
                        engine,
                        confidence,
                        confidence_scale=local_rank_weight_scale,
                    )
                    accumulate_started = time.perf_counter()
                    provider.accumulate(
                        ref_frame,
                        transform=flow_gpu,
                        weight_map=weight_gpu,
                    )
                    reference_telemetry.record("cfa_accumulation_device", accumulate_started)
                finally:
                    if weight_gpu is not None:
                        _facade()._destroy_work_item(weight_gpu)
                    if flow_gpu is not None:
                        _facade()._destroy_work_item(flow_gpu)
            if reference_telemetry.candidate_count == 0:
                raise RuntimeError(
                    "RAW Deep Analysis patch search produced no reference neighbors"
                )
            print(
                "[FusionNet MultiPatch][RAW reference] "
                f"shape={geometry.weight_shape} dtype=float32 "
                f"neighbors={reference_telemetry.candidate_count} "
                f"search_candidates={reference_telemetry.search_candidate_count} "
                f"stages={reference_telemetry.summary()}"
            )

        # Persistent scratch destination for support demosaic to prevent VRAM churn
        _demosaic_scratch = None
        _work_scratch = None
        if needs_analysis:
            try:
                target_scratch_h = geometry.full_shape[0] // 2 if use_half_res else geometry.full_shape[0]
                target_scratch_w = geometry.full_shape[1] // 2 if use_half_res else geometry.full_shape[1]
                _demosaic_scratch = buffer_session.own(
                    engine.allocate((target_scratch_h, target_scratch_w, 3), dtype=np.float32, host_accessible=False)
                )
            except Exception:
                _demosaic_scratch = None

            # Persistent work scratch for analysis proxy resize & in-place tone-mapping
            try:
                align_h, align_w = geometry.align_shape
                if (align_h, align_w) == (target_scratch_h, target_scratch_w):
                    _work_scratch = _demosaic_scratch
                else:
                    _work_scratch = buffer_session.own(
                        engine.allocate((align_h, align_w, 3), dtype=np.float32, host_accessible=False)
                    )
            except Exception:
                _work_scratch = None

        def _load_support_dng_payload(index):
            return provider.load_support_dng_payload_host(index)

        def _decode_support_payload(ordinal, support_payload):
            dng_bytes = None
            try:
                dng_bytes = support_payload.take()
                return provider.decode_support_dng_bytes_host(ordinal, dng_bytes)
            finally:
                # The in-processing queue owns decoded CFA carriers, not a
                # second copy of the compressed DNG container bytes.
                dng_bytes = None
                support_payload.close()

        for ordinal, support_frame in runtime.iter_prepared_supports(
            range(1, len(image_paths)),
            _load_support_dng_payload,
            _decode_support_payload,
            raise_on_cancel=True,
            source_disposer=lambda payload: payload.close(),
        ):
            if _cancelled():
                raise RuntimeError("RAW Native processing cancelled")

            support_linear_full = None
            support_analysis = None
            support_weight_analysis = None
            alignment_preview = None
            aligned_weight_rgb = None
            aligned_analysis_weight = None
            transform = None
            weight_gpu = None
            deep_analysis_accumulated = False
            try:
                if needs_analysis:
                    from .raw_pipeline.provider import _demosaic_carrier_gpu

                    support_linear_full = _demosaic_carrier_gpu(
                        support_frame.carrier,
                        half_res=use_half_res,
                        dst=_demosaic_scratch,
                    )

                    share_support_weight_proxy = (
                        normalized_engine == "fusionet"
                        and geometry.weight_shape == geometry.align_shape
                    )
                    # Build the independent WeightNet/SpatialFusion proxy only when
                    # it differs from the alignment analysis proxy.
                    if normalized_engine in ("fusionet", "spatial_fusion") and not share_support_weight_proxy:
                        support_weight_analysis = _facade().prepare_analysis_proxy_gpu(
                            support_linear_full,
                            work_shape=geometry.weight_shape,
                            analysis_params=(
                                weight_analysis_params
                                if normalized_engine == "fusionet"
                                else None
                            ),
                        )
                        if support_weight_analysis is support_linear_full:
                            support_weight_analysis = taichi_aot.copy(
                                support_weight_analysis, return_gpu=True
                            )

                    # Alignment uses the reference-derived analysis AutoEnhance proxy.
                    support_analysis = _facade().prepare_analysis_proxy_gpu(
                        support_linear_full,
                        work_shape=geometry.align_shape,
                        analysis_params=analysis_params,
                        in_place=True,
                        source_is_disposable=True,
                        dst=_work_scratch,
                    )
                    if (
                        support_linear_full is not support_analysis
                        and support_linear_full is not _demosaic_scratch
                        and support_linear_full is not _work_scratch
                    ):
                        _facade()._destroy_work_item(support_linear_full)
                    support_linear_full = None
                    if share_support_weight_proxy:
                        support_weight_analysis = support_analysis

                    if aligner is not None:
                        primary_for_preview = (
                            support_analysis if share_support_weight_proxy else None
                        )
                        if hasattr(aligner, "take_last_flow"):
                            alignment_preview = aligner.align_frame(
                                primary_for_preview,
                                analysis_frame_gpu=support_analysis,
                                stop_event=stop_event,
                                return_gpu=True,
                                keep_flow=True,
                            )
                            transform = aligner.take_last_flow()
                        else:
                            alignment_preview, _ignored, transform = aligner.align_frame(
                                primary_for_preview,
                                analysis_frame_gpu=support_analysis,
                                stop_event=stop_event,
                                return_gpu=True,
                                return_transform=True,
                            )
                        if normalized_engine not in ("fusionet", "spatial_fusion") and (
                            alignment_preview is not None
                            and alignment_preview is not support_analysis
                        ):
                            _facade()._destroy_work_item(alignment_preview)
                            alignment_preview = None

                if normalized_engine not in ("fusionet", "spatial_fusion"):
                    if support_analysis is not _demosaic_scratch and support_analysis is not _work_scratch:
                        _facade()._destroy_work_item(support_analysis)
                    support_analysis = None

                if normalized_engine in ("spatial_fusion", "fusionet"):
                    # SpatialFusion scores linear proxies while alignment uses
                    # analysis-mode AutoEnhance; FusionNet shares analysis mode.
                    if not (
                        normalized_engine == "fusionet"
                        and geometry.weight_shape == geometry.align_shape
                    ):
                        if alignment_preview is not None and alignment_preview is not support_analysis:
                            _facade()._destroy_work_item(alignment_preview)
                        alignment_preview = None
                    aligned_weight_proxy, unused_preview = _facade()._prepare_raw_aligned_analysis(
                        support_weight_analysis, alignment_preview, transform,
                        align_shape=geometry.weight_shape, warp_analysis=_warp_analysis
                    )
                    # Transfer the already-aligned preview to the weight stage.
                    # A different analysis grid deliberately retains resize->warp.
                    if (
                        unused_preview is not None
                        and unused_preview is not support_weight_analysis
                    ):
                        _facade()._destroy_work_item(unused_preview)
                    alignment_preview = None
                    if (
                        support_weight_analysis is not support_analysis
                        and support_weight_analysis is not aligned_weight_proxy
                    ):
                        _facade()._destroy_work_item(support_weight_analysis)
                    if normalized_engine == "spatial_fusion":
                        aligned_weight_rgb = aligned_weight_proxy
                    else:
                        aligned_analysis_weight = aligned_weight_proxy
                    if aligned_weight_proxy is not support_analysis:
                        if support_analysis is not _demosaic_scratch and support_analysis is not _work_scratch:
                            _facade()._destroy_work_item(support_analysis)
                        support_analysis = None
                    support_weight_analysis = None

                if normalized_engine == "spatial_fusion":
                    tile, overlap_value, motion, noise_offset, noise_sigma = spatial_state
                    taichi_aot.cvtColor(
                        aligned_weight_rgb,
                        taichi_aot.COLOR_RGB2GRAY,
                        dst=weightnet_gray_gpu,
                        return_gpu=True,
                    )
                    generate_spatial_weights_taichi(
                        current_image=weightnet_gray_gpu,
                        reference_image=ref_spatial_gray_gpu,
                        weight_map_sum=spatial_weight_work_gpu,
                        base_window=0,
                        stability_map=None,
                        row_starts=spatial_rows,
                        col_starts=spatial_cols,
                        tile_h=tile,
                        tile_w=tile,
                        noise_sigma=noise_sigma,
                        motion_sensitivity=motion,
                        noise_offset_factor=noise_offset,
                        equalize_brightness=False,
                        buffer_provider=None,
                        scratch_cache=spatial_scratch,
                        row_starts_gpu=spatial_rows_gpu,
                        col_starts_gpu=spatial_cols_gpu,
                        ghost_penalty=float(ghost_penalty),
                        ghost_cutoff=float(ghost_cutoff),
                        postprocess_in_place=True,
                    )
                    weight_gpu = spatial_weight_work_gpu
                    alpha = 1.0
                    if aligned_weight_rgb is not support_analysis:
                        _facade()._destroy_work_item(aligned_weight_rgb)
                    aligned_weight_rgb = None
                    if support_analysis is not None:
                        if support_analysis is not _demosaic_scratch and support_analysis is not _work_scratch:
                            _facade()._destroy_work_item(support_analysis)
                        support_analysis = None
                elif normalized_engine == "fusionet":
                    if getattr(session, "runtime", None) == "taichi_aot":
                        from ..patch_process.multi_patch import CandidateTelemetry, search_candidate_offsets
                        telemetry = CandidateTelemetry()
                        support_resident = session.prepare(aligned_analysis_weight)
                        native_confidence, alpha = session.infer(
                            fusion_ref_work_chw, support_resident, overlap=overlap,
                            ghost_penalty=ghost_penalty, ghost_cutoff=ghost_cutoff,
                            stop_event=stop_event,
                        )
                        telemetry.candidate()
                        if denoising_mode == "deep_analysis":
                            center_weight = _facade()._upload_weightnet_confidence(engine, native_confidence)
                            try:
                                provider.accumulate(support_frame, transform=transform, weight_map=center_weight)
                            finally:
                                _facade()._destroy_work_item(center_weight)
                            candidates = search_candidate_offsets(
                                geometry.full_shape, geometry.weight_shape,
                                align_shape=geometry.align_shape, search_radius=patch_search_radius,
                                patch_stride=2, preserve_cfa_phase=True,
                            )
                            candidate_alpha_total = alpha
                            for selected, _, confidence, rank_alpha in session.candidates(
                                fusion_ref_work_chw, support_resident, candidates,
                                max_neighbors=max_neighbor_candidates, telemetry=telemetry,
                                overlap=overlap, ghost_penalty=ghost_penalty,
                                ghost_cutoff=ghost_cutoff, stop_event=stop_event,
                            ):
                                flow_gpu = selected.flow(full_shape=geometry.full_shape,
                                                         flow_shape=geometry.align_shape,
                                                         base_transform=transform)
                                local_weight = _facade()._upload_weightnet_confidence(
                                    engine, confidence, confidence_scale=local_rank_weight_scale)
                                try:
                                    provider.accumulate(support_frame, transform=flow_gpu, weight_map=local_weight)
                                finally:
                                    _facade()._destroy_work_item(flow_gpu)
                                    _facade()._destroy_work_item(local_weight)
                                candidate_alpha_total += rank_alpha
                            alpha = candidate_alpha_total / telemetry.candidate_count
                            deep_analysis_accumulated = True
                        else:
                            weight_gpu = _facade()._upload_weightnet_confidence(engine, native_confidence)
                        print(f"[FusionNet Resident][RAW] mode={denoising_mode} "
                              f"shape={geometry.weight_shape} dtype=float32 "
                              f"candidates={telemetry.candidate_count} host_patch_readback=0")
                        del support_resident
                    elif str(denoising_mode).strip().lower() == "deep_analysis":
                        from ..patch_process.multi_patch import (
                            CandidateTelemetry,
                            candidate_flow_from_indices,
                            search_candidate_offsets,
                        )

                        telemetry = CandidateTelemetry()
                        candidate_alpha_total = 0.0
                        candidates = search_candidate_offsets(
                            geometry.full_shape,
                            geometry.weight_shape,
                            align_shape=geometry.align_shape,
                            search_radius=patch_search_radius,
                            patch_stride=2,
                            preserve_cfa_phase=True,
                        )
                        readback_started = time.perf_counter()
                        support_proxy_hwc = (
                            aligned_analysis_weight.to_numpy()
                            if hasattr(aligned_analysis_weight, "to_numpy")
                            else np.asarray(aligned_analysis_weight)
                        )
                        telemetry.record("analysis_candidate_readback", readback_started)
                        support_proxy_chw = _facade()._multi_patch_weightnet_input(
                            support_proxy_hwc,
                            channels=weightnet_channels,
                            transfer_map=fusion_transfer_map,
                        )
                        del support_proxy_hwc

                        # Keep ONNX inference serial, but hand each completed
                        # candidate to a bounded CFA-consumer queue. This lets
                        # the Taichi CFA accumulator consume candidate N while
                        # WeightNet evaluates candidate N+1, matching the
                        # standard route's overlapped inference/merge stages.
                        candidate_queue = queue.Queue(maxsize=1)
                        candidate_errors = []
                        candidate_sentinel = object()
                        deep_taichi_lock = threading.Lock()

                        def _raw_deep_candidate_consumer():
                            nonlocal candidate_alpha_total
                            try:
                                from taichi_vision.taichi_aot.engine import ensure_cuda_context

                                ensure_cuda_context()
                            except Exception:
                                pass
                            while True:
                                candidate = candidate_queue.get()
                                if candidate is candidate_sentinel:
                                    return
                                rank_indices, confidence, rank_alpha = candidate
                                transform_gpu = weight_gpu = None
                                deep_taichi_lock.acquire()
                                try:
                                    if _cancelled():
                                        raise RuntimeError(
                                            "RAW Deep Analysis cancelled during candidate fusion"
                                        )
                                    if rank_indices is None:
                                        transform_gpu = transform
                                    else:
                                        transform_started = time.perf_counter()
                                        if (
                                            transform is not None
                                            and hasattr(transform, "to_numpy")
                                            and len(getattr(transform, "shape", ())) == 3
                                        ):
                                            transform_gpu = taichi_aot.compose_multi_patch_dense_flow(
                                                rank_indices,
                                                np.asarray(
                                                    [(item.dx_full, item.dy_full) for item in candidates],
                                                    dtype=np.int32,
                                                ),
                                                transform,
                                                full_shape=geometry.full_shape,
                                            )
                                        else:
                                            rank_flow_host = candidate_flow_from_indices(
                                                rank_indices,
                                                candidates,
                                                full_shape=geometry.full_shape,
                                                flow_shape=geometry.align_shape,
                                                base_transform=transform,
                                            )
                                            transform_gpu = engine.upload(
                                                rank_flow_host, is_vector=True
                                            )
                                        telemetry.record("candidate_transform", transform_started)
                                    weight_gpu = _facade()._upload_weightnet_confidence(
                                        engine,
                                        confidence,
                                        confidence_scale=(
                                            local_rank_weight_scale
                                            if rank_indices is not None
                                            else 1.0
                                        ),
                                    )
                                    accumulate_started = time.perf_counter()
                                    provider.accumulate(
                                        support_frame,
                                        transform=transform_gpu,
                                        weight_map=weight_gpu,
                                    )
                                    telemetry.record("cfa_accumulation_device", accumulate_started)
                                    candidate_alpha_total += float(rank_alpha)
                                except Exception as exc:
                                    candidate_errors.append(exc)
                                    return
                                finally:
                                    try:
                                        if weight_gpu is not None:
                                            _facade()._destroy_work_item(weight_gpu)
                                        if rank_indices is not None and transform_gpu is not None:
                                            _facade()._destroy_work_item(transform_gpu)
                                    finally:
                                        deep_taichi_lock.release()

                        candidate_consumer = threading.Thread(
                            target=_raw_deep_candidate_consumer,
                            name=f"FusionNet-RAW-candidate-{ordinal}",
                            daemon=True,
                        )
                        candidate_consumer.start()

                        def _queue_raw_deep_candidate(candidate):
                            while candidate_consumer.is_alive():
                                if candidate_errors:
                                    raise RuntimeError(
                                        "RAW Deep Analysis candidate consumer failed"
                                    ) from candidate_errors[0]
                                if _cancelled():
                                    raise RuntimeError(
                                        "RAW Deep Analysis cancelled during candidate queueing"
                                    )
                                try:
                                    candidate_queue.put(candidate, timeout=0.05)
                                    return
                                except queue.Full:
                                    continue
                            if candidate_errors:
                                raise RuntimeError(
                                    "RAW Deep Analysis candidate consumer failed"
                                ) from candidate_errors[0]
                            raise RuntimeError(
                                "RAW Deep Analysis candidate consumer stopped unexpectedly"
                            )

                        try:
                            # ONNX calls stay one-at-a-time. Their results are
                            # consumed on a separate Taichi worker immediately.
                            center_started = time.perf_counter()
                            center_confidence, center_alpha = infer_single_support_weight_map(
                                session,
                                fusion_ref_work_chw,
                                support_proxy_chw,
                                tile_size=tile_size,
                                overlap=overlap,
                                ghost_penalty=float(ghost_penalty),
                                ghost_cutoff=float(ghost_cutoff),
                                chroma_sensitivity=float(chroma_sensitivity),
                                stop_event=stop_event,
                                return_scalar=(weightnet_channels == 1),
                            )
                            telemetry.record("weightnet_center", center_started)
                            telemetry.candidate()
                            _queue_raw_deep_candidate((None, center_confidence, center_alpha))

                            for rank_indices, _rank_valid, confidence, rank_alpha in _facade()._iter_multi_patch_rank_maps(
                                session,
                                fusion_ref_work_chw,
                                support_proxy_chw,
                                candidates,
                                max_neighbors=max_neighbor_candidates,
                                tile_size=tile_size,
                                overlap=overlap,
                                ghost_penalty=float(ghost_penalty),
                                ghost_cutoff=float(ghost_cutoff),
                                chroma_sensitivity=float(chroma_sensitivity),
                                stop_event=stop_event,
                                telemetry=telemetry,
                                device_lock=deep_taichi_lock,
                                prefetch_depth=2,
                            ):
                                if _cancelled():
                                    raise RuntimeError(
                                        "RAW Deep Analysis cancelled during neighbor ranks"
                                    )
                                _queue_raw_deep_candidate(
                                    (rank_indices, confidence, rank_alpha)
                                )
                        finally:
                            if candidate_consumer.is_alive():
                                while candidate_consumer.is_alive():
                                    try:
                                        candidate_queue.put(candidate_sentinel, timeout=0.05)
                                        break
                                    except queue.Full:
                                        if candidate_errors:
                                            break
                            candidate_consumer.join()
                        if candidate_errors:
                            raise RuntimeError(
                                "RAW Deep Analysis candidate consumer failed"
                            ) from candidate_errors[0]
                        del support_proxy_chw
                        if telemetry.candidate_count == 0:
                            raise RuntimeError("RAW Deep Analysis produced no candidates")
                        alpha = candidate_alpha_total / telemetry.candidate_count
                        deep_analysis_accumulated = True
                        backend_details = {}
                        try:
                            from taichi_vision.taichi_aot import backend_info

                            backend_details = backend_info()
                        except Exception:
                            backend_details = {"backend": getattr(engine, "arch", "unknown")}
                        print(
                            "[FusionNet MultiPatch][RAW] "
                            f"backend={getattr(engine, 'arch', 'unknown')} device={backend_details} "
                            f"shape={geometry.weight_shape} dtype=float32 "
                            f"weightnet={getattr(session, 'runtime', 'onnx')} "
                            "candidate_prefetch_depth=2 "
                            f"stages={telemetry.summary()}"
                        )
                    else:
                        if weightnet_channels == 1:
                            taichi_aot.cvtColor(
                                aligned_analysis_weight,
                                taichi_aot.COLOR_RGB2GRAY,
                                dst=weightnet_gray_gpu,
                                return_gpu=True,
                            )
                            weightnet_support_gpu = weightnet_gray_gpu
                        else:
                            weightnet_support_gpu = aligned_analysis_weight
                        support_chw = _facade().prepare_weightnet_support_input(
                            weightnet_support_gpu,
                            fusion_transfer_map,
                            workspace=weightnet_support_workspace,
                        )
                        weight_chw, alpha = infer_single_support_weight_map(
                            session,
                            fusion_ref_work_chw,
                            support_chw,
                            tile_size=tile_size,
                            overlap=overlap,
                            ghost_penalty=float(ghost_penalty),
                            ghost_cutoff=float(ghost_cutoff),
                            chroma_sensitivity=float(chroma_sensitivity),
                            stop_event=stop_event,
                            return_scalar=(weightnet_channels == 1),
                        )
                        weight_upload = (
                            weightnet_upload_workspace.stage(weight_chw)
                            if weightnet_upload_workspace is not None
                            else (
                                np.ascontiguousarray(weight_chw[0], dtype=np.float32)
                                if weightnet_channels == 1
                                else np.ascontiguousarray(
                                    np.transpose(weight_chw, (1, 2, 0)),
                                    dtype=np.float32,
                                )
                            )
                        )
                        weight_gpu = engine.upload(weight_upload, is_vector=False)
                        del weight_upload
                        if aligned_analysis_weight is not None:
                            if support_analysis is aligned_analysis_weight:
                                support_analysis = None
                            _facade()._destroy_work_item(aligned_analysis_weight)
                            aligned_analysis_weight = None
                        del support_chw, weight_chw
                else:
                    alpha = 1.0

                # Release all analysis RGB proxies before CFA accumulation,
                # which is the largest transient allocation of this frame.
                released_ids = {id(_demosaic_scratch), id(_work_scratch)}
                for buffer in (
                    aligned_weight_rgb,
                    support_weight_analysis,
                    support_linear_full,
                ):
                    if buffer is not None and id(buffer) not in released_ids:
                        _facade()._destroy_work_item(buffer)
                        released_ids.add(id(buffer))
                aligned_weight_rgb = None
                support_weight_analysis = None
                support_linear_full = None

                # ``accumulate`` warps the CFA carrier and blends it, which is
                # the largest transient allocation of the per-frame loop.  It
                # only needs the mosaic frame, the transform and the weight map,
                # so both full-resolution RGB proxies can go before it runs.
                if support_analysis is not None:
                    if support_analysis is not _demosaic_scratch and support_analysis is not _work_scratch:
                        _facade()._destroy_work_item(support_analysis)
                    support_analysis = None
                if aligned_analysis_weight is not None:
                    _facade()._destroy_work_item(aligned_analysis_weight)
                    aligned_analysis_weight = None

                if not deep_analysis_accumulated:
                    provider.accumulate(
                        support_frame,
                        transform=transform,
                        weight_map=weight_gpu,
                    )
                alpha_total += alpha if getattr(session, "runtime", None) == "taichi_aot" else float(alpha)
                _emit(
                    int(25 + (65 * ordinal / max(1, total_supports))),
                    f"RAW Native {ordinal}/{total_supports}",
                    f"RAW Native frame {ordinal}/{total_supports} accumulated",
                )
                pipeline_telemetry.emit(f"blend_{ordinal}")
            finally:
                released_ids = {id(_demosaic_scratch), id(_work_scratch)}
                for buffer in (
                    aligned_weight_rgb,
                    support_weight_analysis,
                    support_linear_full,
                    support_analysis,
                    aligned_analysis_weight,
                    alignment_preview,
                ):
                    if buffer is not None and id(buffer) not in released_ids:
                        _facade()._destroy_work_item(buffer)
                        released_ids.add(id(buffer))
                if weight_gpu is not None and weight_gpu is not spatial_weight_work_gpu:
                    _facade()._destroy_work_item(weight_gpu)
                if transform is not None and not isinstance(transform, np.ndarray):
                    _facade()._destroy_work_item(transform)

        mean_alpha = alpha_total / max(1, total_supports)
        result = provider.finalize(mean_alpha)
        pipeline_telemetry.emit("complete")
        return _facade()._export_result(result.value), result.mean_alpha
    finally:
        if aligner is not None:
            try:
                _facade()._destroy_work_item(aligner)
            except Exception:
                pass
        for buffer in (
            ref_proxy_full_gpu,
            ref_analysis_gpu,
            ref_weight_analysis_gpu,
        ):
            _facade()._destroy_work_item(buffer)
        if spatial_scratch is not None:
            try:
                _facade()._destroy_work_item(spatial_scratch)
            except Exception:
                pass
        active_error = sys.exc_info()[1]
        try:
            runtime.stop_workers()
            buffer_session.release_all_except()
            if owns_runtime:
                runtime.close()
        except Exception as cleanup_error:
            if active_error is None:
                raise
            print(f"[GPU Pipeline] Buffer cleanup also failed: {cleanup_error}")
        finally:
            _facade()._destroy_work_item(provider)
        # A finished burst leaves far more resident memory than the engine's own
        # live/pooled counters describe: measured 1446 MiB -> 934 MiB of process
        # Working set once the warm pool, retired queue and native staging
        # caches are drained.  Nothing else in this call still needs them.
        try:
            from taichi_vision import taichi_aot
            taichi_aot = _facade()._managed_api(taichi_aot)

            if hasattr(taichi_aot, "reclaim_resident_buffers"):
                engine.sync()
                taichi_aot.reclaim_resident_buffers("raw_pipeline_burst_complete")
        except Exception as exc:
            print(f"[GPU Pipeline] Post-burst reclaim skipped: {exc}")
