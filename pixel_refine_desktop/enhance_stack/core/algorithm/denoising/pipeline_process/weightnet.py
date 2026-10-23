"""WeightNet candidate ranking and confidence helpers for the resident pipeline.

Local top-K candidate selection, per-rank WeightNet confidence inference, and
device upload of confidence maps.  Sibling implementations are reached through
:func:`pipeline_process.facade.api` so ``monkeypatch.setattr`` on the resident
facade keeps reaching the live call path.
"""

import queue
import threading
import time

import numpy as np

from .facade import api as _facade

__all__ = [
    "_multi_patch_weightnet_input",
    "_select_multi_patch_candidates",
    "_iter_multi_patch_rank_maps",
    "_upload_weightnet_confidence",
    "_iter_deep_support_candidate_maps",
]

def _multi_patch_weightnet_input(candidate_hwc, *, channels, transfer_map=None):
    """Convert one RGB candidate readback to the existing WeightNet CHW contract."""

    if getattr(transfer_map, "runtime", None) == "taichi_aot":
        return transfer_map.prepare(candidate_hwc)
    candidate = np.asarray(candidate_hwc, dtype=np.float32)
    if (
        candidate.ndim == 3
        and candidate.shape[0] in (1, 3)
        and candidate.shape[-1] not in (1, 3)
    ):
        if channels == candidate.shape[0]:
            chw = np.ascontiguousarray(candidate, dtype=np.float32)
        elif channels == 1 and candidate.shape[0] == 3:
            gray = (
                candidate[0] * np.float32(0.299)
                + candidate[1] * np.float32(0.587)
                + candidate[2] * np.float32(0.114)
            )
            chw = np.ascontiguousarray(gray[None, ...], dtype=np.float32)
        else:
            raise ValueError(
                f"multi-patch CHW proxy has {candidate.shape[0]} channels; expected {channels}"
            )
        if transfer_map is not None:
            _facade().apply_precomputed_transfer_map(chw, transfer_map)
        return chw
    if candidate.ndim == 2:
        candidate = candidate[..., None]
    if candidate.ndim != 3 or candidate.shape[2] not in (1, 3):
        raise ValueError(f"multi-patch proxy must be HWC 1/3-channel, got {candidate.shape}")
    if channels == 1:
        if candidate.shape[2] == 3:
            gray = (
                candidate[..., 0] * np.float32(0.299)
                + candidate[..., 1] * np.float32(0.587)
                + candidate[..., 2] * np.float32(0.114)
            )
        else:
            gray = candidate[..., 0]
        chw = np.ascontiguousarray(gray[None, ...], dtype=np.float32)
    else:
        if candidate.shape[2] != 3:
            raise ValueError("RGB WeightNet requires a 3-channel analysis proxy")
        chw = np.ascontiguousarray(np.transpose(candidate, (2, 0, 1)), dtype=np.float32)
    if transfer_map is not None:
        _facade().apply_precomputed_transfer_map(chw, transfer_map)
    return chw


def _select_multi_patch_candidates(
    reference_chw,
    candidate_source_chw,
    offsets,
    *,
    max_neighbors,
    stop_event,
    telemetry,
):
    from ..patch_process.multi_patch import (
        CandidateSelection,
        cohere_candidate_selection,
    )

    started = time.perf_counter()
    if stop_event is not None and (
        bool(stop_event())
        if callable(stop_event)
        else bool(stop_event.is_set())
        if hasattr(stop_event, "is_set")
        else False
    ):
        return CandidateSelection(
            indices=np.empty((0, *np.asarray(reference_chw).shape[-2:]), dtype=np.int32),
            valid=np.empty((0, *np.asarray(reference_chw).shape[-2:]), dtype=bool),
            search_candidate_count=0,
        )

    from taichi_vision import taichi_aot

    offset_array = np.ascontiguousarray(
        [(int(offset.dx_proxy), int(offset.dy_proxy)) for offset in offsets],
        dtype=np.int32,
    )
    indices_gpu = taichi_aot.select_multi_patch_topk(
        np.ascontiguousarray(reference_chw, dtype=np.float32),
        np.ascontiguousarray(candidate_source_chw, dtype=np.float32),
        offset_array,
        max_neighbors=max_neighbors,
    )
    try:
        indices = np.ascontiguousarray(indices_gpu.to_numpy(), dtype=np.int32)
    finally:
        indices_gpu.destroy()
    valid = indices >= 0
    selection = CandidateSelection(
        indices=indices,
        valid=valid,
        search_candidate_count=len(offsets),
    )
    # The AOT graph ranks every pixel independently. Use one rank decision per
    # 10-pixel patch cell before assembling candidate carriers so flat-field
    # noise cannot create pixel-frequency offset mosaics.
    selection = cohere_candidate_selection(
        selection,
        offsets,
        cell_size=10,
        patch_size=5,
    )
    telemetry.record("local_patch_search", started)
    telemetry.searched(selection.search_candidate_count)
    return selection


def _iter_multi_patch_rank_maps(
    session,
    reference_chw,
    candidate_source_chw,
    offsets,
    *,
    max_neighbors,
    tile_size,
    overlap,
    ghost_penalty,
    ghost_cutoff,
    chroma_sensitivity,
    stop_event,
    telemetry,
    selection=None,
    device_lock=None,
    prefetch_depth=0,
):
    """Yield one local top-K candidate confidence map at a time.

    Patch distance is used only inside ``select_topk_candidates`` to choose
    source offsets. The returned WeightNet map is masked only by geometric
    rank validity and is the sole candidate confidence passed to fusion.
    """

    from ..fusionet_engine.weightnet_inference import infer_single_support_weight_map
    from ..patch_process.multi_patch import gather_rank_candidate

    if getattr(session, "runtime", None) == "taichi_aot":
        yield from session.candidates(reference_chw, candidate_source_chw, offsets,
                                      max_neighbors=max_neighbors, telemetry=telemetry,
                                      overlap=overlap, ghost_penalty=ghost_penalty,
                                      ghost_cutoff=ghost_cutoff, stop_event=stop_event)
        return

    if selection is None:
        if device_lock is None:
            selection = _facade()._select_multi_patch_candidates(
                reference_chw,
                candidate_source_chw,
                offsets,
                max_neighbors=max_neighbors,
                stop_event=stop_event,
                telemetry=telemetry,
            )
        else:
            with device_lock:
                selection = _facade()._select_multi_patch_candidates(
                    reference_chw,
                    candidate_source_chw,
                    offsets,
                    max_neighbors=max_neighbors,
                    stop_event=stop_event,
                    telemetry=telemetry,
                )

    def _is_cancelled():
        return stop_event is not None and (
            bool(stop_event())
            if callable(stop_event)
            else bool(stop_event.is_set())
            if hasattr(stop_event, "is_set")
            else False
        )

    if int(prefetch_depth) > 0:
        input_queue = queue.Queue(maxsize=max(1, int(prefetch_depth)))
        input_sentinel = object()
        producer_stop = threading.Event()
        producer_errors = []

        def _queue_input(candidate):
            while not producer_stop.is_set():
                if _is_cancelled():
                    producer_stop.set()
                    return False
                try:
                    input_queue.put(candidate, timeout=0.05)
                    return True
                except queue.Full:
                    continue
            return False

        def _candidate_input_producer():
            try:
                for rank in range(selection.indices.shape[0]):
                    if producer_stop.is_set() or _is_cancelled():
                        break
                    rank_indices = selection.indices[rank]
                    valid = selection.valid[rank].copy()
                    if not np.any(valid):
                        continue
                    candidate_chw, gathered_valid = gather_rank_candidate(
                        candidate_source_chw, offsets, rank_indices
                    )
                    valid &= gathered_valid
                    if not np.any(valid):
                        del candidate_chw
                        continue
                    if not _queue_input((rank_indices, valid, candidate_chw)):
                        del candidate_chw
                        break
            except Exception as exc:
                producer_errors.append(exc)
            finally:
                if not producer_stop.is_set():
                    _queue_input(input_sentinel)

        producer = threading.Thread(
            target=_candidate_input_producer,
            name="FusionNet-DeepAnalysis-prefetch",
            daemon=True,
        )
        producer.start()
        try:
            while True:
                if _is_cancelled():
                    producer_stop.set()
                    return
                try:
                    item = input_queue.get(timeout=0.05)
                except queue.Empty:
                    if not producer.is_alive():
                        break
                    continue
                if item is input_sentinel:
                    break
                rank_indices, valid, candidate_chw = item
                inference_started = time.perf_counter()
                try:
                    confidence, alpha = infer_single_support_weight_map(
                        session,
                        reference_chw,
                        candidate_chw,
                        tile_size=tile_size,
                        overlap=overlap,
                        ghost_penalty=ghost_penalty,
                        ghost_cutoff=ghost_cutoff,
                        chroma_sensitivity=chroma_sensitivity,
                        stop_event=stop_event,
                        return_scalar=(reference_chw.shape[0] == 1),
                    )
                    telemetry.record("weightnet", inference_started)
                    confidence = np.asarray(confidence, dtype=np.float32)
                    if confidence.ndim != 3 or confidence.shape[1:] != valid.shape:
                        raise ValueError(
                            f"WeightNet confidence must be CHW on {valid.shape}, got {confidence.shape}"
                        )
                    confidence[:, ~valid] = 0.0
                    telemetry.candidate()
                    yield rank_indices, valid, confidence, float(alpha)
                finally:
                    del candidate_chw
            if producer_errors:
                raise RuntimeError(
                    "Deep Analysis candidate prefetch failed"
                ) from producer_errors[0]
        finally:
            producer_stop.set()
            producer.join()
        if producer_errors:
            raise RuntimeError("Deep Analysis candidate prefetch failed") from producer_errors[0]
        return

    for rank in range(selection.indices.shape[0]):
        if _is_cancelled():
            return
        rank_indices = selection.indices[rank]
        valid = selection.valid[rank]
        if not np.any(valid):
            continue
        candidate_chw, gathered_valid = gather_rank_candidate(
            candidate_source_chw, offsets, rank_indices
        )
        valid &= gathered_valid
        inference_started = time.perf_counter()
        confidence, alpha = infer_single_support_weight_map(
            session,
            reference_chw,
            candidate_chw,
            tile_size=tile_size,
            overlap=overlap,
            ghost_penalty=ghost_penalty,
            ghost_cutoff=ghost_cutoff,
            chroma_sensitivity=chroma_sensitivity,
            stop_event=stop_event,
            return_scalar=(reference_chw.shape[0] == 1),
        )
        telemetry.record("weightnet", inference_started)
        confidence = np.asarray(confidence, dtype=np.float32)
        if confidence.ndim != 3 or confidence.shape[1:] != valid.shape:
            raise ValueError(
                f"WeightNet confidence must be CHW on {valid.shape}, got {confidence.shape}"
            )
        confidence[:, ~valid] = 0.0
        telemetry.candidate()
        del candidate_chw
        yield rank_indices, valid, confidence, float(alpha)


def _upload_weightnet_confidence(engine, confidence_chw, *, confidence_scale=1.0):
    """Upload WeightNet CHW confidence as a scalar map or HWC vector map."""

    from taichi_vision.taichi_algorithm.denoising.resident_weightnet import ResidentConfidence
    if isinstance(confidence_chw, ResidentConfidence):
        return confidence_chw.device(float(confidence_scale))
    confidence = np.asarray(confidence_chw, dtype=np.float32)
    if confidence.ndim != 3 or confidence.shape[0] not in (1, 3):
        raise ValueError(f"WeightNet confidence must be 1/3-channel CHW, got {confidence.shape}")
    confidence_scale = float(confidence_scale)
    if not np.isfinite(confidence_scale) or confidence_scale < 0.0:
        raise ValueError("confidence_scale must be finite and non-negative")
    if confidence_scale != 1.0:
        # Each local rank comes from the same sensor frame and its CFA samples
        # overlap spatially with neighboring output locations.  Discount only
        # these extra spatial ranks; the temporal center candidate stays at its
        # original WeightNet confidence.
        confidence = np.ascontiguousarray(confidence * np.float32(confidence_scale))
    if confidence.shape[0] == 1:
        host = np.ascontiguousarray(confidence[0], dtype=np.float32)
        return engine.upload(host, is_vector=False)
    host = np.ascontiguousarray(np.transpose(confidence, (1, 2, 0)), dtype=np.float32)
    return engine.upload(host, is_vector=True)


def _iter_deep_support_candidate_maps(session, reference_chw, support_chw, offsets, **options):
    """Yield same-location and selected local top-K candidate maps."""
    from ..fusionet_engine.weightnet_inference import infer_single_support_weight_map

    max_neighbors = int(options["max_neighbors"])
    stop_event = options["stop_event"]
    telemetry = options["telemetry"]
    if getattr(session, "runtime", None) == "taichi_aot":
        count = 1 + min(max_neighbors, len(offsets))
        center, alpha = session.infer(reference_chw, support_chw, **options)
        telemetry.candidate()
        yield None, None, center, alpha, count
        for rank, valid, confidence, alpha in session.candidates(
            reference_chw, support_chw, offsets, **options
        ):
            yield rank, valid, confidence, alpha, count
        return
    selection = _facade()._select_multi_patch_candidates(
        reference_chw, support_chw, offsets,
        max_neighbors=max_neighbors, stop_event=stop_event, telemetry=telemetry,
    )
    active_ranks = [r for r in range(selection.indices.shape[0]) if np.any(selection.valid[r])]
    if not active_ranks:
        raise RuntimeError("Deep Analysis produced no valid neighbor ranks")
    count = 1 + len(active_ranks)
    started = time.perf_counter()
    center, alpha = infer_single_support_weight_map(
        session, reference_chw, support_chw,
        tile_size=options["tile_size"], overlap=options["overlap"],
        ghost_penalty=options["ghost_penalty"], ghost_cutoff=options["ghost_cutoff"],
        chroma_sensitivity=options["chroma_sensitivity"], stop_event=stop_event,
        return_scalar=(reference_chw.shape[0] == 1),
    )
    telemetry.record("weightnet_center", started)
    telemetry.candidate()
    yield None, None, center, float(alpha), count
    for result in _facade()._iter_multi_patch_rank_maps(
        session, reference_chw, support_chw, offsets,
        max_neighbors=max_neighbors,
        tile_size=options["tile_size"], overlap=options["overlap"],
        ghost_penalty=options["ghost_penalty"], ghost_cutoff=options["ghost_cutoff"],
        chroma_sensitivity=options["chroma_sensitivity"],
        stop_event=stop_event, telemetry=telemetry, selection=selection,
    ):
        rank_indices, valid, confidence, rank_alpha = result
        yield rank_indices, valid, confidence, rank_alpha, count
