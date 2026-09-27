"""RAW Bayer-CFA carrier mechanics for the shared resident lifecycle.

The analysis contract is owned by ``resident_pipeline``.  This module keeps
only the RAW-specific carrier work auditable: RGB is used for alignment and
WeightNet/SpatialFusion analysis, while CFA planes receive the final warp and
accumulation for Average, SpatialFusion, or FusionNet.  The compatibility
runner remains temporarily available as a migration oracle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional, Sequence, Tuple

import numpy as np
import os

from .metadata import normalize_cfa_rgb_codes
from .result import RawNativeResult
from ..contracts import (
    FrameMetadata,
    ProviderFrame,
    ResidentAnalysisContext,
    ResidentResult,
    ResidentGeometry,
    scale_homography,
)


_NO_ALIGNMENT = {"", "none", "no alignment", "no_alignment", "off"}


def _release(buffer) -> None:
    if buffer is None:
        return
    from ....pipeline_runtime import current_pipeline_runtime
    runtime = current_pipeline_runtime()
    if runtime is not None and runtime.buffer_session is not None:
        runtime.buffer_session.release_tree(buffer)
        return
    for method_name in ("release", "destroy"):
        method = getattr(buffer, method_name, None)
        if callable(method):
            method()
            return


def _is_cancelled(stop_event) -> bool:
    if stop_event is None:
        return False
    if hasattr(stop_event, "is_set"):
        return bool(stop_event.is_set())
    return bool(stop_event()) if callable(stop_event) else False


def _phase_planes(frame, normalized: np.ndarray) -> tuple[np.ndarray, ...]:
    """Return contiguous, phase-correct Bayer planes in tile order."""
    planes = []
    phase_y, phase_x = (int(frame.phase_origin[0]) & 1, int(frame.phase_origin[1]) & 1)
    for index in range(4):
        plane_y, plane_x = divmod(index, 2)
        row = (plane_y - phase_y) & 1
        col = (plane_x - phase_x) & 1
        planes.append(np.ascontiguousarray(normalized[row::2, col::2], dtype=np.float32))
    return tuple(planes)


def _normalized_for_rgb_parity(frame) -> np.ndarray:
    """Normalize one CFA carrier exactly like ``demosaic(path)`` does.

    The canonical RGB loader currently follows rawpy's scalar RAW contract:
    channel-zero black level, one white level, float32 reciprocal multiply,
    then clamp to the sensor interval.  ``RawMosaicFrame.normalized_headroom``
    intentionally preserves per-plane black levels and highlight headroom,
    which is useful for sensor-native processing but makes even a one-frame
    RAW round-trip differ from the RGB-resident oracle.

    Keep this parity conversion local to the denoising provider.  It does not
    change ``RawMosaicFrame`` or the public demosaic API, and it makes the CFA
    carrier consumed by fusion match the samples seen by the RGB path before
    Hamilton reconstruction.
    """

    samples = np.asarray(frame.samples).astype(np.float32, copy=False)
    black = np.float32(int(float(frame.black_level[0])))
    white = np.float32(int(float(frame.white_level[0])))
    inverse_range = np.float32(1.0) / np.maximum(
        np.float32(1.0), np.float32(white - black)
    )
    normalized = (samples - black) * inverse_range
    return np.ascontiguousarray(
        np.clip(normalized, np.float32(0.0), np.float32(1.0)),
        dtype=np.float32,
    )


def _plane_homography(matrix: np.ndarray, frame, index: int) -> np.ndarray:
    """Conjugate a support-to-reference homography into one Bayer lattice."""
    plane_y, plane_x = divmod(int(index), 2)
    origin_y = (plane_y - int(frame.phase_origin[0])) & 1
    origin_x = (plane_x - int(frame.phase_origin[1])) & 1
    plane_to_sensor = np.asarray(
        ((2.0, 0.0, origin_x), (0.0, 2.0, origin_y), (0.0, 0.0, 1.0)),
        dtype=np.float32,
    )
    return np.ascontiguousarray(
        np.linalg.inv(plane_to_sensor) @ np.asarray(matrix, dtype=np.float32) @ plane_to_sensor,
        dtype=np.float32,
    )


def _analysis_proxy(
    path: str | Path,
    *,
    width: int,
    height: int,
    scale: float,
    source_gpu=None,
    auto_enhance_params: Optional[dict] = None,
):
    """Build the RGB alignment proxy while keeping RAW fusion linear.

    ``auto_enhance_params`` is computed once from the full-resolution
    reference and reused for every support frame, matching the RGB-resident
    alignment contract.  The CFA carrier is never tone-mapped or
    contrast-enhanced.
    """
    from taichi_vision import taichi_aot
    from ..resident_pipeline import _managed_api
    taichi_aot = _managed_api(taichi_aot)

    from ..resident_pipeline import prepare_analysis_proxy_gpu

    proxy = source_gpu
    owns_proxy = proxy is None
    if proxy is None:
        proxy = taichi_aot.demosaic(str(path), method="hamilton", return_gpu=True)
    work_h = max(32, int(height * scale))
    work_w = max(32, int(width * scale))
    work = prepare_analysis_proxy_gpu(
        proxy,
        work_shape=(work_h, work_w),
        analysis_params=auto_enhance_params,
    )
    # A caller-provided source remains caller-owned.  The helper returns a
    # temporary only when resize/enhancement was required.
    if work is not proxy and proxy is not None:
        _release(proxy)
    return work


def _warp_analysis_proxy(proxy_gpu, transform, *, height: int, width: int):
    """Warp an AutoEnhanced work-resolution proxy for SpatialFusion weights."""
    from taichi_vision import taichi_aot
    from ..resident_pipeline import _managed_api
    taichi_aot = _managed_api(taichi_aot)

    if isinstance(transform, np.ndarray) and transform.ndim == 2 and transform.shape == (3, 3):
        return taichi_aot.warp_perspective(
            proxy_gpu,
            transform,
            (int(width), int(height)),
            return_gpu=True,
        )
    return taichi_aot.remap_with_flow(
        proxy_gpu,
        transform,
        int(height),
        int(width),
        return_gpu=True,
    )


def _analysis_transform(transform, *, full_shape, proxy_shape):
    """Return the transform in the proxy coordinate system.

    Feature matching returns a full-resolution homography.  Dense optical
    flow already carries work-resolution vectors, so it must pass through
    unchanged.  Keeping this conversion at the provider boundary prevents a
    full-resolution translation from being magnified when the proxy is
    downscaled.
    """

    if transform is None or not isinstance(transform, np.ndarray):
        return transform
    # Dense flow is already expressed in work-grid pixel units.  Only a
    # 3x3 matrix is a full-resolution feature transform here.
    if transform.ndim != 2 or transform.shape != (3, 3):
        return transform
    return scale_homography(
        transform,
        source_shape=(int(full_shape[0]), int(full_shape[1])),
        destination_shape=(int(proxy_shape[0]), int(proxy_shape[1])),
    )


def _accumulate_homography_cfa(
    source_planes,
    homography,
    *,
    frame,
    zero_flow_gpu,
    weight_map_gpu,
    sum_gpu,
    weight_gpu,
):
    """Warp CFA planes independently, then accumulate them in reference phase."""
    from taichi_vision import taichi_aot
    from ..resident_pipeline import _managed_api
    taichi_aot = _managed_api(taichi_aot)
    from taichi_vision.taichi_algorithm.spatial_fusion import (
        accumulate_cfa_homography_taichi,
        remap_accumulate_cfa_weighted_taichi,
    )

    # Phase-aware direct gather is the production RAW path: the inverse
    # homography is evaluated at each destination CFA site and the source is
    # interpolated only within the matching colour plane.  The historical
    # plane-warp implementation remains available explicitly through
    # ``PIXEL_REFINE_CFA_WARP_MODE=legacy_plane`` for parity/rollback tests.
    # Keeping this switch internal preserves the public alignment API.
    direct_mode = os.environ.get(
        "PIXEL_REFINE_CFA_WARP_MODE", "direct_homography"
    ).strip().lower()
    if direct_mode in {"direct", "direct_homography", "gather"}:
        accumulate_cfa_homography_taichi(
            source_planes,
            homography,
            weight_map_gpu,
            sum_gpu,
            weight_gpu,
            full_shape=frame.shape,
            cfa_pattern=normalize_cfa_rgb_codes(frame.cfa_pattern),
            phase_origin=frame.phase_origin,
        )
        return

    warped_planes = []
    try:
        for index, source_plane in enumerate(source_planes):
            h_plane, w_plane = (int(source_plane.shape[0]), int(source_plane.shape[1]))
            warped_planes.append(
                taichi_aot.warp_perspective(
                    source_plane,
                    _plane_homography(homography, frame, index),
                    (w_plane, h_plane),
                    return_gpu=True,
                )
            )
        remap_accumulate_cfa_weighted_taichi(
            warped_planes,
            zero_flow_gpu,
            weight_map_gpu,
            sum_gpu,
            weight_gpu,
            full_shape=frame.shape,
            cfa_pattern=normalize_cfa_rgb_codes(frame.cfa_pattern),
            phase_origin=frame.phase_origin,
        )
    finally:
        for plane in warped_planes:
            _release(plane)


def _validate_support(reference, support, path: str | Path) -> None:
    """Fail before mixing sensor contracts that cannot be fused safely."""
    checks = {
        "shape": (reference.shape, support.shape),
        "bits_per_sample": (reference.bits_per_sample, support.bits_per_sample),
        "cfa_pattern": (reference.cfa_pattern, support.cfa_pattern),
        "phase_origin": (reference.phase_origin, support.phase_origin),
        "orientation": (reference.orientation, support.orientation),
    }
    mismatches = [name for name, (left, right) in checks.items() if left != right]
    if mismatches:
        raise ValueError(
            f"RAW Native requires an identical DNG sensor contract; {Path(path).name} "
            f"differs in {', '.join(mismatches)}"
        )


def _preview_from_mosaic(
    mosaic,
    frame,
    reference_path: str | Path,
    *,
    return_gpu: bool = False,
):
    """Demosaic once after CFA accumulation, solely for the desktop preview."""
    from taichi_vision import taichi_aot
    from ..resident_pipeline import _managed_api
    taichi_aot = _managed_api(taichi_aot)

    from .metadata import extract_demosaic_parameters

    try:
        params = extract_demosaic_parameters(
            reference_path, frame.cfa_pattern, frame=frame
        )
        print(
            "[RAW Native] Preview colour contract: "
            f"{params.pop('white_balance_source')} WB + ColorMatrix1"
        )
    except Exception as exc:
        # The DNG output still retains its colour metadata.  This fallback is
        # only for a corrupt/unsupported source preview and is deliberately
        # visible in the log, never used for a normal camera DNG.
        c00, c01, c10, c11 = normalize_cfa_rgb_codes(frame.cfa_pattern)
        print(f"[RAW Native] Preview colour metadata unavailable: {exc}; using neutral preview")
        params = {
            "wb_r": 1.0, "wb_g1": 1.0, "wb_b": 1.0, "wb_g2": 1.0,
            "cmatrix": np.eye(3, dtype=np.float32), "black_level": 0.0,
            "white_level": 1.0, "c00": c00, "c01": c01, "c10": c10, "c11": c11,
        }
    source = (
        mosaic
        if hasattr(mosaic, "to_numpy")
        else np.ascontiguousarray(mosaic, dtype=np.float32)
    )
    return taichi_aot.demosaic(
        source,
        **params,
        method="hamilton",
        return_gpu=bool(return_gpu),
    )


def _demosaic_carrier_gpu(carrier):
    """Demosaic an already-decoded carrier without a second file decode.

    The analysis proxy used to call ``taichi_aot.demosaic(path)``, which re-opens
    the DNG through an external RAW reader even though the provider already holds
    the decoded mosaic.  Feeding that mosaic straight to the kernel with the
    carrier's own tag-derived parameters reproduces the same proxy bit for bit.
    """
    from taichi_vision import taichi_aot
    from ..resident_pipeline import _managed_api
    taichi_aot = _managed_api(taichi_aot)

    from .metadata import carrier_demosaic_parameters

    params = carrier_demosaic_parameters(carrier)
    return taichi_aot.demosaic(
        np.ascontiguousarray(carrier.samples),
        **params,
        method="hamilton",
        return_gpu=True,
    )


def _legacy_run_raw_native_resident_pipeline(
    image_paths: Sequence[str | Path],
    *,
    session=None,
    weight_engine: str,
    alignment_plan: str,
    alignment_config: Optional[dict] = None,
    spatial_config: Optional[dict] = None,
    work_scale: float = 0.50,
    flownet_work_scale: Optional[float] = None,
    weightnet_work_scale: Optional[float] = None,
    max_work_dimension: Optional[int] = 2048,
    tile_size: int = 256,
    overlap: float = 0.30,
    ghost_penalty: float = 1.0,
    ghost_penalty_min: Optional[float] = None,
    ghost_cutoff: float = 0.05,
    chroma_sensitivity: float = 6.0,
    stop_event=None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    **_unused,
) -> Tuple[RawNativeResult, float]:
    """Fuse a DNG burst directly in Bayer CFA space.

    RGB is used only to estimate an alignment transform.  The transform is
    then applied to same-colour Bayer lattices; no warped RGB value is ever
    sampled back into the sensor carrier.
    """
    normalized_engine = str(weight_engine).strip().lower()
    normalized_alignment = str(alignment_plan).strip().lower()
    if normalized_engine not in ("average", "spatial_fusion", "fusionet"):
        raise NotImplementedError(
            "RAW Native supports Average, SpatialFusion, and FusionNet."
        )
    if normalized_engine == "fusionet" and session is None:
        raise ValueError("RAW Native FusionNet requires an initialized WeightNet session")
    if len(image_paths) < 2:
        raise ValueError("RAW Native fusion requires at least two DNG frames")
    if any(Path(path).suffix.lower() != ".dng" for path in image_paths):
        raise ValueError("RAW Native is currently restricted to homogeneous DNG bursts")

    from taichi_vision import taichi_aot

    from ..resident_pipeline import _managed_api

    taichi_aot = _managed_api(taichi_aot)
    from taichi_vision.taichi_algorithm.compression import RawMosaicFrame, read_dng_aot
    from taichi_vision.taichi_algorithm.spatial_fusion import (
        SpatialScratchCache,
        generate_spatial_weights_taichi,
        normalize_accumulator_cfa_taichi,
        postprocess_spatial_weight_taichi,
        remap_accumulate_cfa_weighted_taichi,
        resolve_spatial_thresholds,
    )
    from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (
        _compute_tile_starts,
    )
    if normalized_engine == "fusionet":
        from ...fusionet_engine.weightnet_inference import (
            infer_single_support_weight_map,
        )

    engine = taichi_aot.get_engine()
    from ..telemetry import PipelineTelemetry

    pipeline_telemetry = PipelineTelemetry(
        engine,
        enabled=_unused.get("telemetry"),
    )
    pipeline_telemetry.emit("start")
    reference = RawMosaicFrame.from_dng(read_dng_aot(image_paths[0]), source_id=str(image_paths[0]))
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
    analysis_context = ResidentAnalysisContext(geometry=geometry)
    print(
        "[RAW Native] Shared analysis geometry: "
        f"full={geometry.full_shape} "
        f"align={geometry.align_shape} "
        f"weight={geometry.weight_shape} "
        f"requested=({geometry.requested_align_scale:.3f},"
        f"{geometry.requested_weight_scale:.3f})"
    )
    unsupported_codes = sorted(set(int(value) for value in reference.cfa_pattern).difference({0, 1, 2, 3}))
    if unsupported_codes:
        raise ValueError(
            "RAW Native CFA fusion currently requires DNG RGB CFA codes [0, 1, 2]; "
            f"got {reference.cfa_pattern}"
        )

    ref_normalized = reference.normalized_headroom()
    sum_gpu = engine.upload(np.ascontiguousarray(ref_normalized, dtype=np.float32))
    weight_gpu = engine.upload(np.ones(reference.shape, dtype=np.float32))
    zero_flow_gpu = engine.upload(np.zeros((1, 1, 2), dtype=np.float32), is_vector=False)
    one_weight_gpu = engine.upload(np.ones((1, 1, 3), dtype=np.float32), is_vector=False)
    del ref_normalized

    aligner = None
    ref_analysis_gpu = None
    analysis_params = None
    ref_spatial_gray_gpu = None
    spatial_weight_work_gpu = None
    spatial_weight_post_gpu = None
    spatial_rows_gpu = None
    spatial_cols_gpu = None
    spatial_scratch = None
    spatial_row_starts = []
    spatial_col_starts = []
    spatial_cfg = dict(spatial_config or {})
    fusion_ref_work_chw = None
    fusion_weight_transfer_map = None
    fusion_tile_size = max(256, int(tile_size))
    fusion_overlap = float(np.clip(overlap, 0.0, 0.95))
    alpha_total = 0.0
    needs_analysis = (
        normalized_alignment not in _NO_ALIGNMENT
        or normalized_engine in ("spatial_fusion", "fusionet")
    )
    if needs_analysis:
        # Cap the analysis side at 2048 pixels, matching the resident RGB
        # pipeline's bounded alignment footprint.
        capped_scale = geometry.effective_align_scale
        # Match the RGB-resident contract: compute AutoEnhance v1 analysis
        # parameters once from the full-resolution reference, then reuse them
        # on the downscaled reference/support proxies.
        from taichi_vision import taichi_aot
        from ..resident_pipeline import _managed_api
        taichi_aot = _managed_api(taichi_aot)
        from ..resident_pipeline import (
            analyze_auto_enhance_on_gpu,
            prepare_analysis_proxy_gpu,
            resolve_noise_adaptive_penalty,
        )

        ref_proxy_full_gpu = taichi_aot.demosaic(
            str(image_paths[0]), method="hamilton", return_gpu=True
        )
        try:
            analysis_params = analyze_auto_enhance_on_gpu(
                ref_proxy_full_gpu, mode="analysis"
            )
            print(
                "[RAW Native] AutoEnhance v1 alignment analysis: "
                f"Gain={float(analysis_params.get('gain', 1.0)):.2f}x "
                "(reference parameters reused)"
            )
            ref_analysis_gpu = prepare_analysis_proxy_gpu(
                ref_proxy_full_gpu,
                work_shape=geometry.align_shape,
                analysis_params=analysis_params,
            )
            analysis_context.analysis_params = analysis_params or {}
            analysis_context.reference_proxy = ref_analysis_gpu
            analysis_context.alignment_reference = ref_analysis_gpu
            ref_noise_score, ghost_penalty = resolve_noise_adaptive_penalty(
                ref_analysis_gpu,
                ghost_penalty=ghost_penalty,
                ghost_penalty_min=ghost_penalty_min,
            )
            analysis_context.noise_score = ref_noise_score
            print(
                "[RAW Native] Alignment proxy ready: "
                f"shape={tuple(ref_analysis_gpu.shape[:2])} CLAHE=off"
            )
        finally:
            _release(ref_proxy_full_gpu)
        if normalized_alignment not in _NO_ALIGNMENT:
            from ..resident_pipeline import create_resident_aligner
            aligner = create_resident_aligner(
                alignment_plan,
                ref_analysis_gpu,
                work_scale=capped_scale,
                full_shape=reference.shape,
                alignment_config=alignment_config,
            )

        if normalized_engine == "spatial_fusion":
            # SpatialFusion consumes the aligned analysis luminance, while
            # CFA accumulation remains scalar and phase-locked.
            ref_spatial_gray_gpu = taichi_aot.cvtColor(
                ref_analysis_gpu, taichi_aot.COLOR_RGB2GRAY
            )
            analysis_context.weight_reference = ref_spatial_gray_gpu
            spatial_tile = int(
                spatial_cfg.get(
                    "similarity_spatial_tile_size",
                    spatial_cfg.get("tile_size", 12),
                )
            )
            spatial_tile = max(4, spatial_tile)
            spatial_overlap = float(
                spatial_cfg.get(
                    "similarity_spatial_overlap_percent",
                    spatial_cfg.get("overlap_percent", 0.70),
                )
            )
            spatial_motion = float(
                spatial_cfg.get(
                    "similarity_spatial_motion_sensitivity",
                    spatial_cfg.get("motion_sensitivity", 150.0),
                )
            )
            spatial_noise_offset = float(
                spatial_cfg.get(
                    "similarity_spatial_noise_mad_offset_factor",
                    spatial_cfg.get("noise_offset_factor", 0.15),
                )
            )
            noise_sigma = spatial_cfg.get("noise_sigma")
            if noise_sigma in (None, 0, 0.0):
                noise_sigma = (
                    float(ref_noise_score)
                    if ref_noise_score is not None
                    else 0.025
                )
            noise_sigma = float(np.clip(noise_sigma, 1.0e-4, 0.99999))
            spatial_row_starts = _compute_tile_starts(
                int(ref_spatial_gray_gpu.shape[0]), spatial_tile,
                overlap=spatial_overlap,
            )
            spatial_col_starts = _compute_tile_starts(
                int(ref_spatial_gray_gpu.shape[1]), spatial_tile,
                overlap=spatial_overlap,
            )
            spatial_rows_gpu = taichi_aot.upload(
                np.asarray(spatial_row_starts, dtype=np.int32)
            )
            spatial_cols_gpu = taichi_aot.upload(
                np.asarray(spatial_col_starts, dtype=np.int32)
            )
            work_shape = tuple(int(v) for v in ref_spatial_gray_gpu.shape[:2])
            spatial_weight_work_gpu = engine.allocate(work_shape, dtype=np.float32)
            spatial_weight_post_gpu = engine.allocate(work_shape, dtype=np.float32)
            spatial_scratch = SpatialScratchCache()
            spatial_cfg["_tile_size"] = spatial_tile
            spatial_cfg["_overlap"] = spatial_overlap
            spatial_cfg["_motion_sensitivity"] = spatial_motion
            spatial_cfg["_noise_offset_factor"] = spatial_noise_offset
            spatial_cfg["_noise_sigma"] = noise_sigma
            print(
                "[RAW Native][SpatialFusion] weights resident: "
                f"tile={spatial_tile} overlap={spatial_overlap:.3f} "
                f"motion={spatial_motion:.3f} noise_sigma={noise_sigma:.6f}"
            )
        elif normalized_engine == "fusionet":
            # Keep the alignment proxy CLAHE-free, matching RGB Linear.
            # WeightNet receives the same canonical reference tensor and one
            # cached transfer map as the shared RGB resident path.
            from ..resident_pipeline import prepare_weightnet_reference_input

            fusion_ref_work_chw, fusion_weight_transfer_map = (
                prepare_weightnet_reference_input(
                    ref_analysis_gpu,
                    work_shape=geometry.weight_shape,
                    clip_limit=2.0,
                    tile_grid_size=(8, 8),
                )
            )
            analysis_context.weight_reference = fusion_ref_work_chw
            analysis_context.clahe_transfer_map = fusion_weight_transfer_map
            print(
                "[RAW Native][FusionNet] WeightNet proxy cache ready: "
                f"shape={tuple(fusion_ref_work_chw.shape)} tile={fusion_tile_size} "
                f"overlap={fusion_overlap:.3f} CLAHE=reference-cache"
            )

        _release(ref_analysis_gpu)
        ref_analysis_gpu = None

    total_supports = len(image_paths) - 1
    try:
        engine_label = {
            "spatial_fusion": "SpatialFusion",
            "fusionet": "FusionNet",
        }.get(normalized_engine, "Average")
        print(
            f"[RAW Native] CFA {engine_label} start: shape={reference.shape} "
            f"cfa={reference.cfa_pattern} supports={total_supports} "
            f"backend={getattr(engine, 'arch', 'unknown')}"
        )
        pipeline_telemetry.emit("reference_loaded")
        for index, path in enumerate(image_paths[1:], start=1):
            if _is_cancelled(stop_event):
                raise RuntimeError("RAW Native processing cancelled")
            support = RawMosaicFrame.from_dng(read_dng_aot(path), source_id=str(path))
            _validate_support(reference, support, path)
            normalized = support.normalized_headroom()
            cpu_planes = _phase_planes(support, normalized)
            del normalized
            gpu_planes = []
            transform = None
            aligned_proxy = None
            aligned_analysis_gpu = None
            aligned_weight_gray_gpu = None
            supp_analysis_gpu = None
            try:
                gpu_planes = [engine.upload(plane) for plane in cpu_planes]
                if normalized_engine in ("spatial_fusion", "fusionet"):
                    supp_analysis_gpu = _analysis_proxy(
                        path, width=reference.width, height=reference.height,
                        scale=capped_scale,
                        auto_enhance_params=analysis_params,
                    )
                if aligner is None and normalized_engine == "average":
                    remap_accumulate_cfa_weighted_taichi(
                        gpu_planes, zero_flow_gpu, one_weight_gpu, sum_gpu, weight_gpu,
                        full_shape=reference.shape,
                        cfa_pattern=normalize_cfa_rgb_codes(reference.cfa_pattern),
                        phase_origin=reference.phase_origin,
                    )
                elif aligner is not None:
                    if supp_analysis_gpu is None:
                        supp_analysis_gpu = _analysis_proxy(
                            path, width=reference.width, height=reference.height,
                            scale=capped_scale,
                            auto_enhance_params=analysis_params,
                        )
                    if hasattr(aligner, "take_last_flow"):
                        aligned_proxy = aligner.align_frame(
                            supp_analysis_gpu,
                            analysis_frame_gpu=supp_analysis_gpu,
                            stop_event=stop_event,
                            return_gpu=True,
                            keep_flow=True,
                        )
                        transform = aligner.take_last_flow()
                    else:
                        aligned_proxy, _ignored, transform = aligner.align_frame(
                            supp_analysis_gpu,
                            analysis_frame_gpu=supp_analysis_gpu,
                            stop_event=stop_event,
                            return_gpu=True,
                            return_transform=True,
                        )
                if normalized_engine == "spatial_fusion":
                    if transform is None:
                        aligned_analysis_gpu = supp_analysis_gpu
                    else:
                        analysis_transform = _analysis_transform(
                            transform,
                            full_shape=reference.shape,
                            proxy_shape=ref_spatial_gray_gpu.shape[:2],
                        )
                        aligned_analysis_gpu = _warp_analysis_proxy(
                            supp_analysis_gpu,
                            analysis_transform,
                            height=int(ref_spatial_gray_gpu.shape[0]),
                            width=int(ref_spatial_gray_gpu.shape[1]),
                        )
                    aligned_weight_gray_gpu = taichi_aot.cvtColor(
                        aligned_analysis_gpu, taichi_aot.COLOR_RGB2GRAY
                    )
                    generate_spatial_weights_taichi(
                        current_image=aligned_weight_gray_gpu,
                        reference_image=ref_spatial_gray_gpu,
                        weight_map_sum=spatial_weight_work_gpu,
                        base_window=0,
                        stability_map=None,
                        row_starts=spatial_row_starts,
                        col_starts=spatial_col_starts,
                        tile_h=spatial_cfg["_tile_size"],
                        tile_w=spatial_cfg["_tile_size"],
                        noise_sigma=spatial_cfg["_noise_sigma"],
                        motion_sensitivity=spatial_cfg["_motion_sensitivity"],
                        noise_offset_factor=spatial_cfg["_noise_offset_factor"],
                        equalize_brightness=False,
                        buffer_provider=None,
                        scratch_cache=spatial_scratch,
                        row_starts_gpu=spatial_rows_gpu,
                        col_starts_gpu=spatial_cols_gpu,
                    )
                    postprocess_spatial_weight_taichi(
                        spatial_weight_work_gpu,
                        ghost_penalty=float(ghost_penalty),
                        ghost_cutoff=float(ghost_cutoff),
                        dst=spatial_weight_post_gpu,
                    )
                    # SpatialFusion produces a scalar confidence map.  Keep
                    # it scalar all the way into the CFA graph; expanding to
                    # RGB would allocate 3x the weight storage and was never
                    # needed by the phase-safe accumulator.
                    spatial_weight_graph_gpu = spatial_weight_post_gpu
                    if isinstance(transform, np.ndarray):
                        _accumulate_homography_cfa(
                            gpu_planes,
                            transform,
                            frame=reference,
                            zero_flow_gpu=zero_flow_gpu,
                            weight_map_gpu=spatial_weight_graph_gpu,
                            sum_gpu=sum_gpu,
                            weight_gpu=weight_gpu,
                        )
                    else:
                        remap_accumulate_cfa_weighted_taichi(
                            gpu_planes,
                            transform if transform is not None else zero_flow_gpu,
                            spatial_weight_graph_gpu,
                            sum_gpu,
                            weight_gpu,
                            full_shape=reference.shape,
                            cfa_pattern=normalize_cfa_rgb_codes(reference.cfa_pattern),
                            phase_origin=reference.phase_origin,
                        )
                    print(
                        f"[RAW Native][SpatialFusion] Frame {index}: "
                        "weight map -> CFA accumulator"
                    )
                elif normalized_engine == "fusionet":
                    if transform is None:
                        aligned_analysis_gpu = supp_analysis_gpu
                    else:
                        analysis_transform = _analysis_transform(
                            transform,
                            full_shape=reference.shape,
                            proxy_shape=(
                                int(fusion_ref_work_chw.shape[1]),
                                int(fusion_ref_work_chw.shape[2]),
                            ),
                        )
                        aligned_analysis_gpu = _warp_analysis_proxy(
                            supp_analysis_gpu,
                            analysis_transform,
                            height=int(fusion_ref_work_chw.shape[1]),
                            width=int(fusion_ref_work_chw.shape[2]),
                        )
                    from ..resident_pipeline import prepare_weightnet_support_input

                    supp_work_chw = prepare_weightnet_support_input(
                        aligned_analysis_gpu,
                        fusion_weight_transfer_map,
                    )
                    weight_map_chw, alpha_mean = infer_single_support_weight_map(
                        session,
                        fusion_ref_work_chw,
                        supp_work_chw,
                        tile_size=fusion_tile_size,
                        overlap=fusion_overlap,
                        ghost_penalty=float(ghost_penalty),
                        ghost_cutoff=float(ghost_cutoff),
                        chroma_sensitivity=float(chroma_sensitivity),
                        stop_event=stop_event,
                    )
                    alpha_total += float(alpha_mean)
                    weight_map_gpu = engine.upload(
                        np.ascontiguousarray(
                            np.transpose(weight_map_chw, (1, 2, 0)),
                            dtype=np.float32,
                        ),
                        is_vector=False,
                    )
                    try:
                        if isinstance(transform, np.ndarray):
                            _accumulate_homography_cfa(
                                gpu_planes,
                                transform,
                                frame=reference,
                                zero_flow_gpu=zero_flow_gpu,
                                weight_map_gpu=weight_map_gpu,
                                sum_gpu=sum_gpu,
                                weight_gpu=weight_gpu,
                            )
                        else:
                            remap_accumulate_cfa_weighted_taichi(
                                gpu_planes,
                                transform if transform is not None else zero_flow_gpu,
                                weight_map_gpu,
                                sum_gpu,
                                weight_gpu,
                                full_shape=reference.shape,
                                cfa_pattern=normalize_cfa_rgb_codes(reference.cfa_pattern),
                                phase_origin=reference.phase_origin,
                            )
                    finally:
                        _release(weight_map_gpu)
                    del supp_work_chw, weight_map_chw
                    print(
                        f"[RAW Native][FusionNet] Frame {index}: "
                        f"WeightNet alpha={float(alpha_mean):.4f} -> CFA accumulator"
                    )
                elif aligner is not None and isinstance(transform, np.ndarray):
                        print(
                            f"[RAW Native] Alignment {alignment_plan}: "
                            "feature homography -> phase-safe CFA warp"
                        )
                        _accumulate_homography_cfa(
                            gpu_planes, transform, frame=reference,
                            zero_flow_gpu=zero_flow_gpu, weight_map_gpu=one_weight_gpu,
                            sum_gpu=sum_gpu, weight_gpu=weight_gpu,
                        )
                elif aligner is not None and transform is None:
                        # A feature matcher may reject an unreliable H.  The
                        # established RGB route also keeps that support as an
                        # identity warp, so preserve the same fail-closed rule.
                        print(
                            f"[RAW Native] Alignment {alignment_plan}: "
                            "no trusted feature transform; identity CFA warp"
                        )
                        remap_accumulate_cfa_weighted_taichi(
                            gpu_planes, zero_flow_gpu, one_weight_gpu, sum_gpu, weight_gpu,
                            full_shape=reference.shape,
                            cfa_pattern=normalize_cfa_rgb_codes(reference.cfa_pattern),
                            phase_origin=reference.phase_origin,
                        )
                elif aligner is not None:
                        print(
                            f"[RAW Native] Alignment {alignment_plan}: "
                            f"dense flow {tuple(transform.shape)} -> CFA remap"
                        )
                        remap_accumulate_cfa_weighted_taichi(
                            gpu_planes, transform, one_weight_gpu, sum_gpu, weight_gpu,
                            full_shape=reference.shape,
                            cfa_pattern=normalize_cfa_rgb_codes(reference.cfa_pattern),
                            phase_origin=reference.phase_origin,
                        )
                engine.sync()
            finally:
                if aligned_proxy is not None and aligned_proxy is not supp_analysis_gpu:
                    _release(aligned_proxy)
                if aligned_analysis_gpu is not None and aligned_analysis_gpu is not supp_analysis_gpu:
                    _release(aligned_analysis_gpu)
                if aligned_weight_gray_gpu is not None:
                    _release(aligned_weight_gray_gpu)
                _release(supp_analysis_gpu)
                if transform is not None and not isinstance(transform, np.ndarray):
                    _release(transform)
                for plane in gpu_planes:
                    _release(plane)

            if progress_callback:
                progress_callback(
                    int(25 + (65 * index / total_supports)),
                    ui=f"RAW Native CFA {index}/{total_supports}",
                    console=f"RAW Native CFA accumulated {index}/{total_supports}",
                )
            print(f"[RAW Native] Frame {index}/{total_supports} CFA accumulated ({Path(path).name})")
            pipeline_telemetry.emit(f"blend_{index}")

        normalize_accumulator_cfa_taichi(sum_gpu, weight_gpu)
        engine.sync()
        preview_gpu = None
        try:
            preview_gpu = _preview_from_mosaic(
                sum_gpu,
                reference,
                image_paths[0],
                return_gpu=True,
            )
            fused_mosaic = np.empty(sum_gpu.shape, dtype=np.float32)
            sum_gpu.to_numpy(out=fused_mosaic)
            preview = preview_gpu.to_numpy()
        finally:
            _release(preview_gpu)
    finally:
        if aligner is not None:
            try:
                aligner.close()
            except Exception:
                pass
        _release(ref_analysis_gpu)
        _release(ref_spatial_gray_gpu)
        if spatial_scratch is not None:
            try:
                spatial_scratch.clear()
            except Exception:
                pass
        _release(spatial_weight_work_gpu)
        _release(spatial_weight_post_gpu)
        _release(spatial_rows_gpu)
        _release(spatial_cols_gpu)
        _release(zero_flow_gpu)
        _release(one_weight_gpu)
        _release(weight_gpu)
        _release(sum_gpu)
        if fusion_ref_work_chw is not None:
            del fusion_ref_work_chw
        if fusion_weight_transfer_map is not None:
            del fusion_weight_transfer_map

    result_mean_alpha = (
        alpha_total / max(1, total_supports)
        if normalized_engine == "fusionet"
        else 1.0
    )
    result = RawNativeResult(
        normalized_mosaic=fused_mosaic,
        preview_rgb=np.ascontiguousarray(preview, dtype=np.float32),
        reference_frame=reference,
        source_paths=tuple(str(path) for path in image_paths),
        report={
            "mean_alpha": result_mean_alpha,
            "supports": total_supports,
            "mode": (
                f"cfa_{'fusionet' if normalized_engine == 'fusionet' else ('spatial_fusion' if normalized_engine == 'spatial_fusion' else 'average')}_"
                f"{normalized_alignment or 'no_alignment'}"
            ),
        },
    )
    print(
        f"[RAW Native] CFA {'FusionNet' if normalized_engine == 'fusionet' else ('SpatialFusion' if normalized_engine == 'spatial_fusion' else 'Average')} "
        "complete: one final Hamilton preview demosaic"
    )
    pipeline_telemetry.emit("complete")
    return result, float(result_mean_alpha)


class RawNativeProvider:
    """RAW Native carrier boundary used by the resident dispatcher.

    ``run`` is retained as a compatibility entry point, but delegates to the
    shared resident executor.  The former standalone runner remains available
    privately as ``_legacy_run_raw_native_resident_pipeline`` for comparison.
    """

    source_mode = "raw_native"
    carrier_kind = "cfa"

    def __init__(self, image_paths, **options):
        self.image_paths = tuple(str(path) for path in image_paths)
        self.options = dict(options)
        self._engine = None
        self._reference_frame = None
        self._sum_gpu = None
        self._weight_gpu = None
        self._zero_flow_gpu = None
        self._one_weight_gpu = None
        self._finalized = False

    def _read_frame(self, index: int):
        from taichi_vision.taichi_algorithm.compression import RawMosaicFrame, read_dng_aot

        path = self.image_paths[int(index)]
        return RawMosaicFrame.from_dng(
            read_dng_aot(path),
            source_id=path,
        )

    def load_reference(self) -> ProviderFrame:
        if self._reference_frame is None:
            self._reference_frame = self._read_frame(0)
        frame = self._reference_frame
        return ProviderFrame(
            carrier=frame,
            metadata=FrameMetadata(
                source_id=self.image_paths[0],
                shape=tuple(int(value) for value in frame.shape),
                dtype="float32",
                color_model="cfa_linear",
                carrier_kind="cfa",
                orientation=int(frame.orientation),
                extra={
                    "bits_per_sample": int(frame.bits_per_sample),
                    "cfa_pattern": tuple(int(value) for value in frame.cfa_pattern),
                    "phase_origin": tuple(int(value) for value in frame.phase_origin),
                },
            ),
        )

    def load_support(self, index: int) -> ProviderFrame:
        frame = self._read_frame(index)
        return ProviderFrame(
            carrier=frame,
            metadata=FrameMetadata(
                source_id=self.image_paths[int(index)],
                shape=tuple(int(value) for value in frame.shape),
                dtype="float32",
                color_model="cfa_linear",
                carrier_kind="cfa",
                orientation=int(frame.orientation),
                extra={
                    "bits_per_sample": int(frame.bits_per_sample),
                    "cfa_pattern": tuple(int(value) for value in frame.cfa_pattern),
                    "phase_origin": tuple(int(value) for value in frame.phase_origin),
                },
            ),
        )

    def load_analysis_proxy(self, frame: ProviderFrame, *, work_shape, analysis_params=None):
        """Build the shared RGB proxy used only for alignment/weight analysis."""

        from ..resident_pipeline import prepare_analysis_proxy_gpu

        proxy = _demosaic_carrier_gpu(frame.carrier)
        try:
            analysis = prepare_analysis_proxy_gpu(
                proxy,
                work_shape=work_shape,
                analysis_params=analysis_params,
                in_place=True,
            )
            if analysis is not proxy:
                _release(proxy)
            return analysis
        except Exception:
            _release(proxy)
            raise

    def bind_accumulator(self, engine, reference: ProviderFrame | None = None) -> None:
        """Allocate the persistent CFA accumulator for the shared frame loop."""

        if self._sum_gpu is not None:
            raise RuntimeError("RAW Native accumulator is already bound")
        if reference is None:
            reference = self.load_reference()
        frame = reference.carrier
        self._engine = engine
        normalized = _normalized_for_rgb_parity(frame)
        try:
            self._sum_gpu = engine.upload(
                np.ascontiguousarray(normalized, dtype=np.float32)
            )
            self._weight_gpu = engine.upload(
                np.ones(frame.shape, dtype=np.float32)
            )
            self._zero_flow_gpu = engine.upload(
                np.zeros((1, 1, 2), dtype=np.float32),
                is_vector=False,
            )
            self._one_weight_gpu = engine.upload(
                np.ones((1, 1, 3), dtype=np.float32),
                is_vector=False,
            )
        finally:
            del normalized

    def accumulate(self, frame: ProviderFrame, transform=None, weight_map=None) -> None:
        """Warp one CFA carrier and accumulate it with the shared weight map."""

        if self._sum_gpu is None or self._weight_gpu is None or self._engine is None:
            raise RuntimeError("RAW Native accumulator is not bound")
        if frame is None or frame.carrier is None:
            raise ValueError("RAW Native accumulate requires a provider frame")
        reference = self.load_reference().carrier
        support = frame.carrier
        _validate_support(reference, support, frame.metadata.source_id)

        from taichi_vision import taichi_aot

        from ..resident_pipeline import _managed_api

        taichi_aot = _managed_api(taichi_aot)
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            remap_accumulate_cfa_weighted_taichi,
        )

        normalized = _normalized_for_rgb_parity(support)
        planes = _phase_planes(support, normalized)
        gpu_planes = []
        active_weight = weight_map if weight_map is not None else self._one_weight_gpu
        try:
            # Preserve each successful upload if a later plane fails.
            for plane in planes:
                gpu_planes.append(self._engine.upload(plane))
            if isinstance(transform, np.ndarray) and transform.ndim == 2 and transform.shape == (3, 3):
                _accumulate_homography_cfa(
                    gpu_planes,
                    transform,
                    frame=reference,
                    zero_flow_gpu=self._zero_flow_gpu,
                    weight_map_gpu=active_weight,
                    sum_gpu=self._sum_gpu,
                    weight_gpu=self._weight_gpu,
                )
            else:
                remap_accumulate_cfa_weighted_taichi(
                    gpu_planes,
                    transform if transform is not None else self._zero_flow_gpu,
                    active_weight,
                    self._sum_gpu,
                    self._weight_gpu,
                    full_shape=reference.shape,
                    cfa_pattern=normalize_cfa_rgb_codes(reference.cfa_pattern),
                    phase_origin=reference.phase_origin,
                )
        finally:
            del normalized, planes
            for plane in gpu_planes:
                _release(plane)

    def finalize(self, mean_alpha: float = 1.0) -> ResidentResult:
        """Normalize the CFA accumulator and create the one-time RGB preview."""

        if self._sum_gpu is None or self._weight_gpu is None or self._engine is None:
            raise RuntimeError("RAW Native accumulator is not bound")
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            normalize_accumulator_cfa_taichi,
        )

        normalize_accumulator_cfa_taichi(self._sum_gpu, self._weight_gpu)
        self._engine.sync()
        reference = self.load_reference().carrier
        preview = None
        try:
            preview = _preview_from_mosaic(
                self._sum_gpu,
                reference,
                self.image_paths[0],
                return_gpu=True,
            )
            mosaic = np.empty(self._sum_gpu.shape, dtype=np.float32)
            self._sum_gpu.to_numpy(out=mosaic)
            preview_rgb = preview.to_numpy()
        finally:
            _release(preview)
        result = RawNativeResult(
            normalized_mosaic=mosaic,
            preview_rgb=np.ascontiguousarray(preview_rgb, dtype=np.float32),
            reference_frame=reference,
            source_paths=self.image_paths,
            report={
                "mean_alpha": float(mean_alpha),
                "supports": max(0, len(self.image_paths) - 1),
                "mode": "shared_cfa_provider",
            },
        )
        self._finalized = True
        return ResidentResult(
            value=result,
            mean_alpha=float(mean_alpha),
            source_mode="raw_native",
            report=dict(result.report or {}),
        )

    def run(self):
        from ..resident_pipeline import _run_shared_raw_provider_pipeline

        return _run_shared_raw_provider_pipeline(
            self.image_paths,
            **self.options,
        )

    def close(self) -> None:
        for name in (
            "_sum_gpu",
            "_weight_gpu",
            "_zero_flow_gpu",
            "_one_weight_gpu",
        ):
            _release(getattr(self, name, None))
            setattr(self, name, None)
        # The cached RawMosaicFrame owns the decoded host carrier.  Drop it at
        # the same lifecycle boundary as the GPU accumulator so a completed
        # burst cannot retain its reference image in the provider instance.
        self._reference_frame = None
        self._engine = None
        return None


def run_raw_native_resident_pipeline(image_paths, **kwargs):
    """Compatibility entry point delegating to the shared resident executor."""
    from ..resident_pipeline import _run_shared_raw_provider_pipeline

    return _run_shared_raw_provider_pipeline(image_paths, **kwargs)


__all__ = ["RawNativeProvider", "run_raw_native_resident_pipeline"]
