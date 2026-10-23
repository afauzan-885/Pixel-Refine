"""Resident alignment, WeightNet confidence, and RGB/CFA burst accumulation.

Standard uses DirectML. Deep Analysis uses Taichi AOT by default and retains
candidate selection, WeightNet confidence, and fusion buffers in the same device
runtime. Initial calibration samples and final outputs still cross the host
boundary. RAW output consists of a CFA mosaic and a separate RGB preview.
Neither route applies CLAHE.
"""

import gc
import os
import queue
import sys
import threading
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, Sequence, Tuple
import numpy as np

from taichi_vision.taichi_aot import TaichiGPUBuffer, get_engine
from .telemetry import PipelineTelemetry
from .contracts import ResidentAnalysisContext, ResidentGeometry, scale_homography
from ...pipeline_runtime import (
    PipelineRuntime,
    current_pipeline_runtime,
    resolve_in_processing_depth,
    resolve_prefetch_depth,
    runtime_entrypoint,
)

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
    PROGRESS_ALIGN_MIN,
    PROGRESS_ALIGN_MAX,
    PROGRESS_LOAD_IMAGES_MIN,
    PROGRESS_LOAD_IMAGES_MAX,
    PROGRESS_MERGE_MIN,
    PROGRESS_MERGE_MAX,
    PROGRESS_FINALIZE_MIN,
    PROGRESS_FINALIZE_MAX,
    PROGRESS_SAVE,
    _align_percent,
    _merge_percent,
)

ANALYSIS_AUTO_ENHANCE_MODE = "natural"


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
            apply_precomputed_transfer_map(chw, transfer_map)
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
        apply_precomputed_transfer_map(chw, transfer_map)
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
            selection = _select_multi_patch_candidates(
                reference_chw,
                candidate_source_chw,
                offsets,
                max_neighbors=max_neighbors,
                stop_event=stop_event,
                telemetry=telemetry,
            )
        else:
            with device_lock:
                selection = _select_multi_patch_candidates(
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
    selection = _select_multi_patch_candidates(
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
    for result in _iter_multi_patch_rank_maps(
        session, reference_chw, support_chw, offsets,
        max_neighbors=max_neighbors,
        tile_size=options["tile_size"], overlap=options["overlap"],
        ghost_penalty=options["ghost_penalty"], ghost_cutoff=options["ghost_cutoff"],
        chroma_sensitivity=options["chroma_sensitivity"],
        stop_event=stop_event, telemetry=telemetry, selection=selection,
    ):
        rank_indices, valid, confidence, rank_alpha = result
        yield rank_indices, valid, confidence, rank_alpha, count


def _resolve_apap_fit_grid_size(config):
    """Choose a local-model grid independently from the fixed 33x33 warp grid."""
    settings = config or {}
    preset = str(settings.get("mode", "fast")).strip().lower()
    default_size = {"fast": 13, "balance": 17, "high": 25}.get(preset, 17)
    return max(4, min(33, int(settings.get("apap_fit_grid_size", default_size))))


def _select_ransac_inlier_correspondences(source, target, inlier_mask):
    """Apply one RANSAC mask while preserving the selected rows' input order."""
    src = np.ascontiguousarray(source)
    dst = np.ascontiguousarray(target)
    if src.ndim != 2 or src.shape[1:] != (2,) or dst.shape != src.shape:
        raise ValueError(
            f"RANSAC correspondences must be matching Nx2 arrays, got {src.shape} and {dst.shape}"
        )
    if inlier_mask is None:
        selected = np.ones((len(src),), dtype=bool)
    else:
        if isinstance(inlier_mask, TaichiGPUBuffer):
            get_engine().sync()
            mask_values = inlier_mask.to_numpy()
        else:
            mask_values = np.asarray(inlier_mask)
        mask_values = np.asarray(mask_values).reshape(-1)
        if len(mask_values) != len(src):
            raise ValueError(
                f"RANSAC inlier mask has {len(mask_values)} rows for {len(src)} correspondences"
            )
        selected = mask_values.astype(bool, copy=False)
    if int(selected.sum()) < 4:
        raise RuntimeError(
            f"RANSAC selected only {int(selected.sum())} APAP correspondences; at least four are required"
        )
    return (
        np.ascontiguousarray(src[selected]),
        np.ascontiguousarray(dst[selected]),
    )


def _resolve_spatial_analysis_config(
    config, *, tile_size, overlap, work_shape, noise_score, is_raw
):
    """Resolve one identical spatial-weight policy for RGB and CFA carriers."""
    from taichi_vision.taichi_algorithm.spatial_fusion import auto_motion_sensitivity

    cfg = config or {}
    tile = max(
        8, min(int(cfg.get("similarity_spatial_tile_size", tile_size)), min(work_shape))
    )
    ratio = float(cfg.get("similarity_spatial_overlap_percent", overlap))
    base_motion = float(
        cfg.get("similarity_spatial_motion_sensitivity",
                cfg.get("motion_sensitivity", cfg.get("motion_sensivity", 150.0)))
    )
    offset = float(
        cfg.get("similarity_spatial_noise_mad_offset_factor",
                cfg.get("noise_offset_factor",
                        cfg.get("noise_mad_offset_factor", cfg.get("noise_offset", 0.15))))
    )
    explicit_sigma = cfg.get("similarity_spatial_noise_sigma", cfg.get("noise_sigma"))
    if explicit_sigma is not None and float(explicit_sigma) > 0:
        sigma, mode = float(explicit_sigma), "explicit_ui"
    elif noise_score is not None:
        sigma, mode = (
            float(np.clip(noise_score, 1e-4, 0.99999)),
            "linear_reference_score",
        )
    else:
        sigma, mode = 0.025, "fallback"
    motion = auto_motion_sensitivity(is_raw=is_raw, base=base_motion, noise_sigma=sigma)
    return tile, ratio, motion, offset, sigma, mode


def _resolve_reference_analysis_params(
    reference,
    *,
    enabled,
    supplied=None,
    needs_analysis=True,
    mode=ANALYSIS_AUTO_ENHANCE_MODE,
):
    """Analyze a reference once so its stage-specific RGB parameters are reused."""
    override = os.environ.get("PIXEL_REFINE_ANALYSIS_ENHANCE")
    if override is not None:
        enabled = override.strip().lower() not in ("0", "false", "off", "no")
    if not enabled or not needs_analysis:
        return None
    normalized_mode = str(mode).strip().lower()
    if normalized_mode not in {"analysis", "natural"}:
        raise ValueError(f"Unsupported AutoEnhance mode: {mode!r}")
    return supplied or analyze_auto_enhance_on_gpu(reference, mode=normalized_mode)


def _resolve_engine_analysis_params(
    reference,
    *,
    weight_engine,
    enabled,
    supplied=None,
    needs_analysis=True,
    mode=ANALYSIS_AUTO_ENHANCE_MODE,
):
    """Resolve the reference-driven transform for a requested pipeline stage."""
    if (
        str(weight_engine).strip().lower() == "spatial_fusion"
        and str(mode).strip().lower() != "analysis"
    ):
        return None
    return _resolve_reference_analysis_params(
        reference,
        enabled=enabled,
        supplied=supplied,
        needs_analysis=needs_analysis,
        mode=mode,
    )


def _resolve_weightnet_input_channels(session, requested: Optional[int]) -> int:
    requested_channels = None if requested is None else int(requested)
    if requested_channels not in (None, 1):
        raise ValueError(f"FusionNet baseline requires 1 input channel, got {requested_channels}")
    active_session = getattr(session, "encoder_session", session)
    try:
        shape = active_session.get_inputs()[0].shape
        model_channels = shape[1] if len(shape) >= 2 else None
        if isinstance(model_channels, int) and model_channels != 1:
            raise ValueError(
                "FusionNet baseline requires a 1-channel ONNX model, "
                f"got model input channels={model_channels}"
            )
    except AttributeError:
        pass
    return requested_channels or 1


# ---------------------------------------------------------------------------
# Memory Telemetry Helper (Dedicated VRAM, Shared VRAM, Host RAM)
# ---------------------------------------------------------------------------


def get_memory_telemetry_str(engine=None) -> str:
    """Format Dedicated VRAM, Shared VRAM, and Process RAM metrics."""
    parts = []
    # 1. Process Host RAM
    try:
        import psutil

        proc = psutil.Process(os.getpid())
        ram_mb = proc.memory_info().rss / (1024 * 1024)
        parts.append(f"RAM={ram_mb:.0f}MB")
    except Exception:
        pass

    # 2. Engine Memory Governor / Vulkan Budget
    try:
        from taichi_vision.device_selection import query_vulkan_memory_budget

        eng = engine or get_engine()
        dev_id = getattr(eng, "device_id", 0)
        arch = getattr(eng, "arch", "vulkan").lower()
        if arch in ("vulkan", "opengl", "cuda"):
            budget = query_vulkan_memory_budget(dev_id)
            if budget.get("supported"):
                heaps = budget.get("heaps", [])
                vram_used_mb = 0.0
                shared_used_mb = 0.0
                for h in heaps:
                    u_mb = h.get("usage", 0) / (1024 * 1024)
                    if h.get("device_local"):
                        vram_used_mb += u_mb
                    else:
                        shared_used_mb += u_mb
                if vram_used_mb > 0 or budget.get("device_local_usage", 0) > 0:
                    vram_mb = (
                        vram_used_mb
                        if vram_used_mb > 0
                        else (budget.get("device_local_usage", 0) / (1024 * 1024))
                    )
                    parts.append(f"VRAM={vram_mb:.0f}MB")
                if shared_used_mb > 0:
                    parts.append(f"SharedVRAM={shared_used_mb:.0f}MB")
    except Exception:
        pass

    return " | ".join(parts) if parts else "RAM=N/A"


# ---------------------------------------------------------------------------
# GPU-Resident Image Loading
# ---------------------------------------------------------------------------

_RAW_EXTENSIONS = frozenset(
    {
        ".dng",
        ".cr2",
        ".cr3",
        ".nef",
        ".arw",
        ".rw2",
        ".orf",
        ".raf",
        ".pef",
        ".srw",
    }
)


def _read_orientation(path: Path) -> int:
    from PIL import Image

    try:
        with Image.open(path) as img:
            exif = img.getexif()
            return int(exif.get(0x0112, 1))
    except Exception:
        return 1


def _apply_orientation(image: np.ndarray, orientation: int) -> np.ndarray:
    if orientation == 2:
        return np.fliplr(image)
    if orientation == 3:
        return np.rot90(image, 2)
    if orientation == 4:
        return np.flipud(image)
    if orientation == 5:
        return np.rot90(np.fliplr(image), -1)
    if orientation == 6:
        return np.rot90(image, -1)
    if orientation == 7:
        return np.rot90(np.fliplr(image), 1)
    if orientation == 8:
        return np.rot90(image, 1)
    return image


def _normalize_rgb_host_frame(image: np.ndarray) -> np.ndarray:
    """Convert one decoded RGB frame with one reusable float32 allocation."""
    source_dtype = image.dtype
    normalized = np.array(image, dtype=np.float32, copy=True, order="C")
    if np.issubdtype(source_dtype, np.integer):
        scale = np.float32(65535.0 if source_dtype == np.uint16 else 255.0)
        np.divide(normalized, scale, out=normalized)
    np.clip(normalized, 0.0, 1.0, out=normalized)
    return normalized


def load_frame_to_gpu(
    path: str | Path,
    is_raw: bool = False,
) -> TaichiGPUBuffer:
    """Load a single image directly to GPU VRAM as float32 [0,1] RGB.

    RAW/DNG:  demosaic (Hamilton) -> GPU float32 RGB
    Standard: imread -> GPU uint8 BGR -> cvtColor BGR->RGB -> GPU float32
    """
    from taichi_vision import taichi_aot
    taichi_aot = _managed_api(taichi_aot)

    path = Path(path)
    is_raw_file = is_raw or path.suffix.lower() in _RAW_EXTENSIONS

    if is_raw_file:
        rgb_gpu = taichi_aot.demosaic(
            str(path),
            method="hamilton",
            return_gpu=True,
        )
        if rgb_gpu.dtype in (np.uint8, np.uint16):
            # Keep the conversion in the Taichi Vision/native cast boundary.
            # Hamilton currently emits f32, but this compatibility branch is
            # still needed for older uint8/uint16 demosaic artifacts.
            converted_gpu = taichi_aot.cast(
                rgb_gpu, np.float32, host_accessible=True
            )
            if converted_gpu is not rgb_gpu:
                _destroy_work_item(rgb_gpu)
            return converted_gpu
        return rgb_gpu

    from PIL import Image, ImageOps

    try:
        with Image.open(path) as img:
            img = ImageOps.exif_transpose(img)
            if img.mode in ("RGBA", "LA", "P", "L"):
                img = img.convert("RGB")
            img_rgb = np.array(img)
    except Exception as e_pil:
        raise ValueError(f"Failed to read image '{path}' with PIL: {e_pil}")

    rgb_f32 = _normalize_rgb_host_frame(img_rgb)
    del img_rgb

    return taichi_aot.upload(rgb_f32)


# ---------------------------------------------------------------------------
# GPU-Resident AutoEnhance
# ---------------------------------------------------------------------------


def analyze_auto_enhance_on_gpu(
    ref_gpu: TaichiGPUBuffer, mode: str = "natural"
) -> dict:
    from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
        analyze_auto_enhance_params_gpu,
    )

    return analyze_auto_enhance_params_gpu(ref_gpu, mode=mode)


def apply_auto_enhance_on_gpu(
    src_gpu: TaichiGPUBuffer,
    params: dict,
    dst: Optional[TaichiGPUBuffer] = None,
) -> TaichiGPUBuffer:
    from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
        apply_auto_enhance_gpu,
    )

    return _track_gpu_result(apply_auto_enhance_gpu(src_gpu, params, dst=dst, return_gpu=True))


def prepare_analysis_proxy_gpu(
    source_gpu: TaichiGPUBuffer,
    *,
    work_shape: tuple[int, int],
    analysis_params: Optional[dict] = None,
    in_place: bool = False,
    source_is_disposable: bool = False,
) -> TaichiGPUBuffer:
    """Create the canonical work-resolution RGB analysis proxy.

    This helper is deliberately shared by RGB and RAW Native.  By default it
    never modifies or destroys ``source_gpu``: callers retain ownership of the
    source carrier and release the returned temporary when finished.

    ``in_place`` opts into writing the tone-mapped result back into
    ``source_gpu``.  The enhance kernel is per-pixel with an explicit
    destination, so when the caller already owns a throwaway carrier (RAW
    Native analysis proxies) the second full-resolution buffer is pure waste:
    at 12.6 MP one proxy is 144 MiB, and both the reference and every support
    frame allocate one.
    """

    from taichi_vision import taichi_aot

    taichi_aot = _managed_api(taichi_aot)

    work_h, work_w = (max(1, int(work_shape[0])), max(1, int(work_shape[1])))
    if tuple(int(value) for value in source_gpu.shape[:2]) != (work_h, work_w):
        proxy = taichi_aot.resize(
            source_gpu,
            (work_w, work_h),
            interpolation=taichi_aot.INTER_AREA,
            return_gpu=True,
        )
    else:
        proxy = source_gpu
        if (
            in_place
            and analysis_params is not None
            and not source_is_disposable
        ):
            # Keep the full-resolution linear carrier untouched when the
            # requested analysis geometry happens to match its dimensions.
            # A same-size resize does extra filtering work; an exact device
            # copy is sufficient to create the disposable in-place proxy.
            proxy = taichi_aot.copy(source_gpu, return_gpu=True)
    if analysis_params is None:
        return proxy
    enhanced = apply_auto_enhance_on_gpu(
        proxy, analysis_params, dst=proxy if in_place else None
    )
    if enhanced is not proxy and proxy is not source_gpu:
        _destroy_work_item(proxy)
    return enhanced


def resolve_noise_adaptive_penalty(
    analysis_proxy_gpu: TaichiGPUBuffer,
    *,
    ghost_penalty: float,
    ghost_penalty_min: Optional[float] = None,
) -> tuple[Optional[float], float]:
    """Estimate reference noise once and derive the shared ghost penalty."""

    score: Optional[float] = None
    try:
        from taichi_vision.taichi_algorithm.enhancement.estimate_noise import (
            estimate_noise,
        )

        score, _ = estimate_noise(analysis_proxy_gpu, session=_buffer_session())
        score = float(score)
    except Exception as exc:
        print(f"[GPU Pipeline] Noise estimation note: {exc}")

    if score is None:
        return None, float(ghost_penalty)

    maximum = float(ghost_penalty)
    minimum = float(
        ghost_penalty_min
        if ghost_penalty_min is not None
        else min(maximum, 0.65)
    )
    if minimum > maximum:
        minimum, maximum = maximum, minimum
    if score <= 0.50:
        active = maximum
    elif score < 0.90:
        t = (score - 0.50) / 0.40
        factor = 0.5 * (1.0 + np.cos(np.pi * t))
        active = float(minimum + (maximum - minimum) * factor)
    else:
        active = minimum
    print(
        f"[GPU Pipeline] Noise-Adaptive Ghost Penalty: score={score:.4f} "
        f"-> penalty={active:.2f} (range=[{minimum:.2f}, {maximum:.2f}])"
    )
    return score, float(active)


def prepare_reference_analysis_and_noise(
    source_gpu: TaichiGPUBuffer,
    *,
    work_shape: tuple[int, int],
    analysis_params: Optional[dict],
    ghost_penalty: float,
    ghost_penalty_min: Optional[float] = None,
    in_place: bool = False,
    source_is_disposable: bool = False,
    noise_source_gpu: Optional[TaichiGPUBuffer] = None,
    noise_analysis_params: Optional[dict] = None,
) -> tuple[TaichiGPUBuffer, Optional[float], float]:
    """Prepare the reference analysis proxy, then estimate its noise once.

    Keep RGB Linear and RAW Native on the same ordering: work-resolution
    analysis proxy -> reference AutoEnhance -> noise estimate by default.
    FusionNet may provide an independent reference and AutoEnhance parameter
    set for noise estimation while its natural-mode WeightNet proxy remains
    separate from the alignment proxy. SpatialFusion can use an independent
    linear source for noise and weight scoring.
    """

    # If the same linear source is needed for noise estimation, do not let an
    # in-place AutoEnhance consume/mutate it, even when the caller considers
    # that proxy disposable.
    preserve_noise_source = noise_source_gpu is source_gpu
    analysis_gpu = prepare_analysis_proxy_gpu(
        source_gpu,
        work_shape=work_shape,
        analysis_params=analysis_params,
        in_place=in_place,
        source_is_disposable=(source_is_disposable and not preserve_noise_source),
    )
    noise_gpu = analysis_gpu
    owns_noise_gpu = False
    can_reuse_analysis_for_noise = (
        noise_source_gpu is source_gpu
        and noise_analysis_params == analysis_params
    )
    if noise_source_gpu is not None and not can_reuse_analysis_for_noise:
        noise_gpu = prepare_analysis_proxy_gpu(
            noise_source_gpu,
            work_shape=work_shape,
            analysis_params=noise_analysis_params,
        )
        owns_noise_gpu = noise_gpu is not noise_source_gpu and noise_gpu is not analysis_gpu
    try:
        score, active_penalty = resolve_noise_adaptive_penalty(
            noise_gpu,
            ghost_penalty=ghost_penalty,
            ghost_penalty_min=ghost_penalty_min,
        )
    finally:
        if owns_noise_gpu:
            _destroy_work_item(noise_gpu)
    if score is not None:
        source = (
            "autoenhanced_analysis"
            if noise_source_gpu is not None and noise_analysis_params is not None
            else "linear_unenhanced"
            if noise_source_gpu is not None
            else (
            "autoenhanced_natural"
            if analysis_params is not None
            else "linear_proxy_enhance_disabled"
            )
        )
        print(
            "[GPU Pipeline] Reference noise estimate (Taichi Vision): "
            f"score={score:.6f} source={source} "
            f"shape={tuple(int(v) for v in analysis_gpu.shape[:2])}"
        )
    return analysis_gpu, score, active_penalty


def apply_clahe_16bit_reference(
    rgb_chw: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8),
    backend: str = "auto",
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Compatibility alias: CLAHE was removed from FusionNet preprocessing.

    Preserve the historical callable and tuple contract for external callers;
    return the supplied CHW analysis tensor with no transfer map.
    """
    img = np.ascontiguousarray(rgb_chw, dtype=np.float32)
    if img.ndim != 3 or img.shape[0] not in (1, 3):
        raise ValueError(f"WeightNet reference must be CHW with 1 or 3 channels, got {img.shape}")
    return img, None


def apply_precomputed_transfer_map(
    rgb_chw: np.ndarray,
    transfer_map: np.ndarray,
) -> np.ndarray:
    """Compatibility helper for callers supplying an explicit transfer map."""
    img = np.asarray(rgb_chw)
    if img.dtype != np.float32 or not img.flags.c_contiguous:
        img = np.ascontiguousarray(img, dtype=np.float32)
    np.multiply(img, transfer_map[None, :, :], out=img)
    np.clip(img, 0.0, 1.0, out=img)
    return img


def prepare_weightnet_reference_input(
    analysis_gpu: TaichiGPUBuffer,
    *,
    work_shape: tuple[int, int],
    clip_limit: float = 2.0,
    tile_grid_size: tuple[int, int] = (8, 8),
    session=None,
) -> tuple[np.ndarray, Optional[np.ndarray]]:
    """Build the WeightNet reference tensor directly from the analysis proxy."""

    if getattr(session, "runtime", None) == "taichi_aot":
        return session.prepare_reference(analysis_gpu)
    from taichi_vision import taichi_aot

    taichi_aot = _managed_api(taichi_aot)

    work_h, work_w = (int(work_shape[0]), int(work_shape[1]))
    if tuple(int(value) for value in analysis_gpu.shape[:2]) != (work_h, work_w):
        work_gpu = taichi_aot.resize(
            analysis_gpu,
            (work_w, work_h),
            interpolation=taichi_aot.INTER_AREA,
            return_gpu=True,
        )
    else:
        work_gpu = analysis_gpu
    try:
        reference_array = work_gpu.to_numpy()
        if reference_array.ndim == 2:
            reference_chw = np.ascontiguousarray(reference_array[None, ...], dtype=np.float32)
        else:
            reference_chw = np.ascontiguousarray(
                np.transpose(reference_array, (2, 0, 1)), dtype=np.float32
            )
    finally:
        if work_gpu is not analysis_gpu:
            _destroy_work_item(work_gpu)
    return reference_chw, None


def prepare_weightnet_support_input(
    aligned_analysis_gpu: TaichiGPUBuffer,
    transfer_map: Optional[np.ndarray] = None,
    workspace=None,
) -> np.ndarray:
    """Build one canonical CHW support tensor for the ONNX bridge.

    ``workspace`` is an internal reusable host readback pair.  The default
    path remains allocation-compatible for external callers, while resident
    pipelines can reuse the HWC readback and CHW bridge arrays per worker.
    """

    if getattr(transfer_map, "runtime", None) == "taichi_aot":
        return transfer_map.prepare(aligned_analysis_gpu)
    if workspace is not None:
        return workspace.read(aligned_analysis_gpu, transfer_map=transfer_map)

    support_chw = np.ascontiguousarray(
        np.transpose(aligned_analysis_gpu.to_numpy(), (2, 0, 1)),
        dtype=np.float32,
    )
    if transfer_map is not None:
        support_chw = apply_precomputed_transfer_map(support_chw, transfer_map)
    return support_chw


class _WeightNetReadbackWorkspace:
    """Reuse host arrays across the serialized WeightNet support loop."""

    def __init__(self, shape: tuple[int, int], *, channels: int = 3):
        height, width = (max(1, int(shape[0])), max(1, int(shape[1])))
        self.channels = int(channels)
        if self.channels not in (1, 3):
            raise ValueError(f"WeightNet staging supports 1 or 3 channels, got {channels}")
        self.hwc = np.empty(
            (height, width) if self.channels == 1 else (height, width, self.channels),
            dtype=np.float32,
        )
        self.chw = np.empty((self.channels, height, width), dtype=np.float32)
        _own_component(self)

    def close(self):
        self.hwc = None
        self.chw = None

    def read(
        self,
        gpu_buffer: TaichiGPUBuffer,
        *,
        transfer_map: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        expected_shape = self.hwc.shape
        if (
            tuple(int(value) for value in getattr(gpu_buffer, "shape", ()))
            != expected_shape
            or np.dtype(getattr(gpu_buffer, "dtype", np.float32))
            != np.dtype(np.float32)
        ):
            raw = gpu_buffer.to_numpy()
            support_chw = np.ascontiguousarray(
                raw[None, ...] if raw.ndim == 2 else np.transpose(raw, (2, 0, 1)),
                dtype=np.float32,
            )
        else:
            gpu_buffer.to_numpy(out=self.hwc)
            if self.channels == 1:
                np.copyto(self.chw[0], self.hwc)
            else:
                np.copyto(self.chw, np.transpose(self.hwc, (2, 0, 1)))
            support_chw = self.chw
        if transfer_map is not None:
            support_chw = apply_precomputed_transfer_map(
                support_chw, transfer_map
            )
        return support_chw

    def readback(self, gpu_buffer: TaichiGPUBuffer) -> np.ndarray:
        """Read HWC data into the reusable host slot without transposing."""
        expected_shape = self.hwc.shape
        if (
            tuple(int(value) for value in getattr(gpu_buffer, "shape", ()))
            == expected_shape
            and np.dtype(getattr(gpu_buffer, "dtype", np.float32))
            == np.dtype(np.float32)
        ):
            gpu_buffer.to_numpy(out=self.hwc)
            return self.hwc
        return gpu_buffer.to_numpy()

    def as_chw(self, hwc: np.ndarray) -> np.ndarray:
        """Copy one HWC readback into the reusable CHW bridge slot."""
        if hwc is not self.hwc:
            chw = hwc[None, ...] if hwc.ndim == 2 else np.transpose(hwc, (2, 0, 1))
            return np.ascontiguousarray(chw, dtype=np.float32)
        if self.channels == 1:
            np.copyto(self.chw[0], self.hwc)
        else:
            np.copyto(self.chw, np.transpose(self.hwc, (2, 0, 1)))
        return self.chw


class _WeightNetUploadWorkspace:
    """Reuse the HWC host staging array used to upload each weight map."""

    def __init__(self, shape: tuple[int, int], *, channels: int = 3):
        height, width = (max(1, int(shape[0])), max(1, int(shape[1])))
        self.shape = (height, width)
        self.channels = int(channels)
        if self.channels not in (1, 3):
            raise ValueError(f"WeightNet upload staging supports 1 or 3 channels, got {channels}")
        self.hwc = (
            None
            if self.channels == 1
            else np.empty((height, width, 3), dtype=np.float32)
        )
        _own_component(self)

    def close(self):
        self.hwc = None

    def stage(self, weight_chw: np.ndarray) -> np.ndarray:
        array = np.asarray(weight_chw, dtype=np.float32)
        if self.channels == 1:
            if array.ndim == 3 and array.shape[0] == 1:
                array = array[0]
            if array.ndim != 2 or tuple(array.shape) != self.shape:
                raise ValueError(
                    f"Scalar weight map shape {array.shape} does not match "
                    f"workspace {self.shape}"
                )
            # The scalar inference result is already contiguous and upload()
            # consumes it immediately; pass a view instead of staging a second
            # full-resolution host copy.
            return array
        if array.ndim == 3 and array.shape[0] == 3:
            if tuple(array.shape[1:]) != self.hwc.shape[:2]:
                raise ValueError(
                    f"Weight map shape {array.shape} does not match "
                    f"workspace {self.hwc.shape[:2]}"
                )
            np.copyto(self.hwc, np.transpose(array, (1, 2, 0)))
            return self.hwc
        if array.ndim == 3 and array.shape[0] == 1:
            if tuple(array.shape[1:]) != self.hwc.shape[:2]:
                raise ValueError(
                    f"Weight map shape {array.shape} does not match "
                    f"workspace {self.hwc.shape[:2]}"
                )
            np.copyto(self.hwc, array[0, :, :, None])
            return self.hwc
        if array.ndim == 2 and tuple(array.shape) == self.hwc.shape[:2]:
            np.copyto(self.hwc, array[:, :, None])
            return self.hwc
        return np.ascontiguousarray(np.transpose(array, (1, 2, 0)), dtype=np.float32)


# ---------------------------------------------------------------------------
class NoAlignmentGPUAligner:
    """Pass-through aligner when no alignment is requested."""

    def __init__(self, ref_frame, **kwargs):
        pass

    def align_frame(
        self,
        supp_linear_gpu,
        *,
        analysis_frame_gpu=None,
        secondary_frame_to_warp=None,
        stop_event=None,
        return_gpu=True,
        return_transform: bool = False,
    ):
        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Alignment cancelled.")
            elif callable(stop_event) and stop_event():
                raise RuntimeError("Alignment cancelled.")
        if return_transform:
            return supp_linear_gpu, secondary_frame_to_warp, None
        return supp_linear_gpu, secondary_frame_to_warp

    def close(self):
        pass


class _ResidentFlowBufferMixin:
    """Own one reusable dense-flow destination for a resident aligner."""

    def _init_resident_flow_buffer(self):
        self._resident_flow_buffer = None
        self._resident_quantized_flow_buffer = None

    def _ensure_resident_flow_buffer(self, shape):
        expected = tuple(int(value) for value in shape)
        current = getattr(self, "_resident_flow_buffer", None)
        if (
            current is not None
            and getattr(current, "handle", None) is not None
            and tuple(int(value) for value in getattr(current, "shape", ()))
            == expected
            and np.dtype(getattr(current, "dtype", np.float32))
            == np.dtype(np.float32)
        ):
            return current
        if current is not None and hasattr(current, "destroy"):
            _destroy_work_item(current)
        self._resident_flow_buffer = _managed_api(get_engine()).allocate(
            expected,
            dtype=np.float32,
            is_vector=False,
        )
        return self._resident_flow_buffer

    @staticmethod
    def _normalize_resident_flow(result, destination):
        if isinstance(result, tuple):
            result = result[0]
        if result is None:
            raise RuntimeError("Optical-flow backend returned no resident flow")
        if getattr(result, "handle", None) != getattr(destination, "handle", None):
            from taichi_vision.taichi_algorithm.common import copy_field

            copy_field(result, destination)
            if hasattr(result, "destroy"):
                _destroy_work_item(result)
        return destination

    def _resident_flow_view(self, owner=None):
        if owner is None:
            owner = getattr(self, "_resident_flow_buffer", None)
        if owner is None or getattr(owner, "handle", None) is None:
            return None
        view = TaichiGPUBuffer(
            owner.size_bytes,
            owner.handle,
            owner.shape,
            dtype=owner.dtype,
            is_vector=owner.is_vector,
            engine=owner.engine,
            is_owner=False,
            host_accessible=owner.host_accessible,
            vector_dim=owner.vector_dim,
        )
        view._parent_ref = owner
        return view

    def _close_resident_flow_buffer(self):
        owners = (
            getattr(self, "_resident_flow_buffer", None),
            getattr(self, "_resident_quantized_flow_buffer", None),
        )
        self._resident_flow_buffer = None
        self._resident_quantized_flow_buffer = None
        for owner in owners:
            if owner is not None and hasattr(owner, "destroy"):
                _destroy_work_item(owner)

    def _store_quantized_flow(self, taichi_aot, flow_quant):
        """Keep quantized remap flow separate from the AOT ndarray destination."""
        quantized = taichi_aot.upload(flow_quant, is_vector=True)
        previous = getattr(self, "_resident_quantized_flow_buffer", None)
        if previous is not None and previous is not quantized:
            # The previous flow may still be consumed by resident accumulation.
            taichi_aot.engine.sync()
            _destroy_work_item(previous)
        self._resident_quantized_flow_buffer = quantized
        return quantized


def _parse_bool(value, default=True):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("false", "0", "no", "off", "none", ""):
            return False
        if v in ("true", "1", "yes", "on"):
            return True
    return bool(value)


class BlockMatchingResidentAligner(_ResidentFlowBufferMixin):
    """Persistent native Block-Matching session for the resident pipeline.

    ``Block Matching GPU`` used to fall through to ``compute_flow`` in the
    resident factory.  Besides selecting the wrong algorithm, that discarded
    Block Matching's reusable reference pyramid.  This adapter keeps the BM
    reference gray/pyramid alive for the entire burst and owns only the
    per-support gray and flow buffers.
    """

    def __init__(
        self,
        ref_analysis_gpu: TaichiGPUBuffer,
        *,
        work_scale: float = 0.50,
        full_shape: Optional[Tuple[int, int]] = None,
        alignment_config: Optional[dict] = None,
    ):
        from taichi_vision import taichi_aot
        taichi_aot = _managed_api(taichi_aot)
        from taichi_vision.taichi_algorithm.pyramid.pyramid import (
            build_image_pyramid_gpu,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.block_matching import (
            BLOCK_MATCHING_PRESETS as BLOCK_MATCHING_GPU_PRESETS,
        )

        requested = dict(alignment_config or {})
        mode = str(requested.get("mode", "fast")).strip().lower()
        if mode in ("balanced", "balance mode"):
            mode = "balance"
        if mode not in BLOCK_MATCHING_GPU_PRESETS:
            mode = "fast"
        self.config = dict(BLOCK_MATCHING_GPU_PRESETS[mode])
        self.config.update(requested)
        self.config["mode"] = mode
        self.full_h, self.full_w = (
            (int(full_shape[0]), int(full_shape[1]))
            if full_shape is not None
            else tuple(int(v) for v in ref_analysis_gpu.shape[:2])
        )
        self._init_resident_flow_buffer()

        self.ref_gray_gpu = taichi_aot.cvtColor(
            ref_analysis_gpu, taichi_aot.COLOR_RGB2GRAY
        )
        self.work_h, self.work_w = (
            int(self.ref_gray_gpu.shape[0]), int(self.ref_gray_gpu.shape[1])
        )
        levels = max(1, int(self.config.get("max_level", 2)) + 1)
        self.reference_pyramid = tuple(
            build_image_pyramid_gpu(
                self.ref_gray_gpu,
                n_levels=levels,
                min_size=32,
                session=_buffer_session(),
            )
        )
        # The native pyramid returns L0 as the caller-owned reference buffer.
        # Keep a single ownership path so close() cannot double-retire it.
        self.ref_gray_gpu = self.reference_pyramid[0]
        print(
            "[GPU Pipeline] Aligner: Block Matching GPU "
            f"(mode={mode}, window={self.config.get('win_size')}, "
            f"levels={len(self.reference_pyramid)}, resident-reference=true)"
        )

    def _flow_params(self):
        win_size = max(5, int(self.config.get("win_size", 13)))
        if win_size % 2 == 0:
            win_size += 1
        smooth_val = self.config.get("smooth", None)
        if smooth_val is not None:
            smooth = _parse_bool(smooth_val, default=False)
            dense_mode = "smooth" if smooth else "blocky_clamped"
            overlap = 0.50 if smooth else 0.0
        else:
            dense_mode = str(self.config.get("dense_mode", "blocky_clamped"))
            if "overlap" in self.config:
                overlap = float(self.config["overlap"])
            else:
                overlap = 0.50 if dense_mode == "smooth" else 0.0
        return {
            "winSize": (win_size, win_size),
            "maxLevel": max(0, int(self.config.get("max_level", 2))),
            "criteria": (
                3,
                max(1, int(self.config.get("iterations", 1))),
                float(self.config.get("epsilon", 0.02)),
            ),
            "grid_step": max(4, int(self.config.get("grid_step", 32))),
            "border_margin": max(0, int(self.config.get("border_margin", 8))),
            "motion_mode": str(self.config.get("motion_mode", "fast")),
            "dense_mode": dense_mode,
            "overlap": overlap,
            "max_flow_px": float(self.config.get("max_flow_px", 48.0)),
            "adaptive": bool(self.config.get("adaptive", False)),
            "adaptive_threshold": max(1, int(self.config.get("adaptive_threshold", 1))),
            "decoupled_scale": max(0, int(self.config.get("decoupled_scale", 0))),
        }

    def align_frame(
        self,
        supp_linear_gpu,
        *,
        analysis_frame_gpu=None,
        secondary_frame_to_warp=None,
        stop_event=None,
        return_gpu=True,
        return_transform: bool = False,
    ):
        from taichi_vision import taichi_aot
        taichi_aot = _managed_api(taichi_aot)
        from taichi_vision.taichi_algorithm import calcOpticalFlowBlockMatching

        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Block Matching alignment cancelled.")
            if callable(stop_event) and stop_event():
                raise RuntimeError("Block Matching alignment cancelled.")

        source = analysis_frame_gpu if analysis_frame_gpu is not None else supp_linear_gpu
        supp_gray_gpu = taichi_aot.cvtColor(source, taichi_aot.COLOR_RGB2GRAY)
        flow_gpu = None
        try:
            if tuple(supp_gray_gpu.shape[:2]) != (self.work_h, self.work_w):
                resized = taichi_aot.resize(
                    supp_gray_gpu,
                    (self.work_w, self.work_h),
                    interpolation=taichi_aot.INTER_AREA,
                    return_gpu=True,
                )
                _destroy_work_item(supp_gray_gpu)
                supp_gray_gpu = resized
            flow_destination = self._ensure_resident_flow_buffer(
                (self.work_h, self.work_w, 2)
            )
            flow_gpu = calcOpticalFlowBlockMatching(
                self.ref_gray_gpu,
                supp_gray_gpu,
                **self._flow_params(),
                return_gpu=True,
                reference_pyramid=self.reference_pyramid,
                dst=flow_destination,
            )
            flow_gpu = self._normalize_resident_flow(flow_gpu, flow_destination)
            warped_primary = None
            if supp_linear_gpu is not None:
                prim_h, prim_w = (int(v) for v in supp_linear_gpu.shape[:2])
                warped_primary = taichi_aot.remap_with_flow(
                    supp_linear_gpu,
                    flow_gpu,
                    prim_h,
                    prim_w,
                    return_gpu=True,
                )
            warped_secondary = None
            if secondary_frame_to_warp is not None:
                sec_h, sec_w = (int(v) for v in secondary_frame_to_warp.shape[:2])
                warped_secondary = taichi_aot.remap_with_flow(
                    secondary_frame_to_warp,
                    flow_gpu,
                    sec_h,
                    sec_w,
                    return_gpu=True,
                )
            if return_transform:
                retained_flow = self._resident_flow_view()
                flow_gpu = None
                return warped_primary, warped_secondary, retained_flow
            return warped_primary, warped_secondary
        finally:
            if (
                flow_gpu is not None
                and flow_gpu is not getattr(self, "_resident_flow_buffer", None)
                and hasattr(flow_gpu, "destroy")
            ):
                _destroy_work_item(flow_gpu)
            if supp_gray_gpu is not None and hasattr(supp_gray_gpu, "destroy"):
                _destroy_work_item(supp_gray_gpu)

    def close(self):
        # L0 is the same object as ``ref_gray_gpu``; destroy every pyramid
        # level exactly once so the allocator can reuse or retire it safely.
        for buffer in getattr(self, "reference_pyramid", ()):
            try:
                if buffer is not None and hasattr(buffer, "destroy"):
                    _destroy_work_item(buffer)
            except Exception:
                pass
        self.reference_pyramid = ()
        self.ref_gray_gpu = None
        self._close_resident_flow_buffer()


class LucasKanadeResidentAligner(_ResidentFlowBufferMixin):
    """Persistent native Lucas-Kanade session for the resident pipeline.

    Provides smooth continuous optical flow using Taichi AOT Lucas-Kanade
    pyramid tracking with anisotropic dense interpolation, eliminating
    blocky mosaicing artifacts.
    """

    def __init__(
        self,
        ref_analysis_gpu: TaichiGPUBuffer,
        *,
        work_scale: float = 0.50,
        full_shape: Optional[Tuple[int, int]] = None,
        alignment_config: Optional[dict] = None,
    ):
        from taichi_vision import taichi_aot
        taichi_aot = _managed_api(taichi_aot)
        from taichi_vision.taichi_algorithm.pyramid.pyramid import (
            build_image_pyramid_gpu,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.lucas_kanade import (
            LUCAS_KANADE_PRESETS as LUCAS_KANADE_GPU_PRESETS,
        )

        requested = dict(alignment_config or {})
        mode = str(requested.get("mode", "balance")).strip().lower()
        if mode in ("balanced", "balance mode", "medium", "normal"):
            mode = "balance"
        if mode not in LUCAS_KANADE_GPU_PRESETS:
            mode = "balance"
        self.config = dict(LUCAS_KANADE_GPU_PRESETS[mode])
        self.config.update(requested)
        self.config["mode"] = mode
        self.full_h, self.full_w = (
            (int(full_shape[0]), int(full_shape[1]))
            if full_shape is not None
            else tuple(int(v) for v in ref_analysis_gpu.shape[:2])
        )
        self._init_resident_flow_buffer()

        self.ref_gray_gpu = taichi_aot.cvtColor(
            ref_analysis_gpu, taichi_aot.COLOR_RGB2GRAY
        )
        self.work_h, self.work_w = (
            int(self.ref_gray_gpu.shape[0]), int(self.ref_gray_gpu.shape[1])
        )
        levels = max(1, int(self.config.get("max_level", 2)) + 1)
        self.reference_pyramid = tuple(
            build_image_pyramid_gpu(
                self.ref_gray_gpu,
                n_levels=levels,
                min_size=32,
                session=_buffer_session(),
            )
        )
        self.ref_gray_gpu = self.reference_pyramid[0]
        print(
            "[GPU Pipeline] Aligner: Lucas Kanade GPU "
            f"(mode={mode}, window={self.config.get('win_size')}, "
            f"levels={len(self.reference_pyramid)}, resident-reference=true)"
        )

    def _flow_params(self):
        win_size = max(5, int(self.config.get("win_size", 17)))
        if win_size % 2 == 0:
            win_size += 1
        smooth_val = self.config.get("smooth", None)
        if smooth_val is not None:
            smooth = _parse_bool(smooth_val, default=True)
            dense_mode = "smooth" if smooth else "blocky_clamped"
            overlap = 0.50 if smooth else 0.0
        else:
            dense_mode = str(self.config.get("dense_mode", "smooth"))
            overlap = float(
                self.config.get("overlap", self.config.get("tile_overlap", 0.50 if dense_mode == "smooth" else 0.0))
            )
        return {
            "winSize": (win_size, win_size),
            "maxLevel": max(0, int(self.config.get("max_level", 2))),
            "criteria": (
                3,
                max(1, int(self.config.get("iterations", 16))),
                float(self.config.get("epsilon", 0.015)),
            ),
            "grid_step": max(1, int(self.config.get("grid_step", 16))),
            "border_margin": max(0, int(self.config.get("border_margin", 8))),
            "overlap": overlap,
            "motion_mode": str(self.config.get("motion_mode", "fast")),
            "dense_mode": dense_mode,
            "max_flow_px": float(self.config.get("max_flow_px", 64.0)),
            "adaptive": bool(self.config.get("adaptive", False)),
            "adaptive_threshold": max(1, int(self.config.get("adaptive_threshold", 1))),
        }

    def align_frame(
        self,
        supp_linear_gpu,
        *,
        analysis_frame_gpu=None,
        secondary_frame_to_warp=None,
        stop_event=None,
        return_gpu=True,
        return_transform: bool = False,
    ):
        from taichi_vision import taichi_aot
        taichi_aot = _managed_api(taichi_aot)
        from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLK

        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Lucas Kanade alignment cancelled.")
            if callable(stop_event) and stop_event():
                raise RuntimeError("Lucas Kanade alignment cancelled.")

        source = analysis_frame_gpu if analysis_frame_gpu is not None else supp_linear_gpu
        supp_gray_gpu = taichi_aot.cvtColor(source, taichi_aot.COLOR_RGB2GRAY)
        flow_gpu = None
        try:
            if tuple(supp_gray_gpu.shape[:2]) != (self.work_h, self.work_w):
                resized = taichi_aot.resize(
                    supp_gray_gpu,
                    (self.work_w, self.work_h),
                    interpolation=taichi_aot.INTER_AREA,
                    return_gpu=True,
                )
                _destroy_work_item(supp_gray_gpu)
                supp_gray_gpu = resized
            flow_destination = self._ensure_resident_flow_buffer(
                (self.work_h, self.work_w, 2)
            )
            flow_gpu = calcOpticalFlowPyrLK(
                self.ref_gray_gpu,
                supp_gray_gpu,
                **self._flow_params(),
                return_gpu=True,
                reference_pyramid=self.reference_pyramid,
                dst=flow_destination,
            )
            flow_gpu = self._normalize_resident_flow(flow_gpu, flow_destination)
            warped_primary = None
            if supp_linear_gpu is not None:
                prim_h, prim_w = (int(v) for v in supp_linear_gpu.shape[:2])
                warped_primary = taichi_aot.remap_with_flow(
                    supp_linear_gpu,
                    flow_gpu,
                    prim_h,
                    prim_w,
                    return_gpu=True,
                )
            warped_secondary = None
            if secondary_frame_to_warp is not None:
                sec_h, sec_w = (int(v) for v in secondary_frame_to_warp.shape[:2])
                warped_secondary = taichi_aot.remap_with_flow(
                    secondary_frame_to_warp,
                    flow_gpu,
                    sec_h,
                    sec_w,
                    return_gpu=True,
                )
            if return_transform:
                retained_flow = self._resident_flow_view(flow_gpu)
                flow_gpu = None
                return warped_primary, warped_secondary, retained_flow
            return warped_primary, warped_secondary
        finally:
            if (
                flow_gpu is not None
                and flow_gpu is not getattr(self, "_resident_flow_buffer", None)
                and flow_gpu
                is not getattr(self, "_resident_quantized_flow_buffer", None)
                and hasattr(flow_gpu, "destroy")
            ):
                _destroy_work_item(flow_gpu)
            if supp_gray_gpu is not None and hasattr(supp_gray_gpu, "destroy"):
                _destroy_work_item(supp_gray_gpu)

    def close(self):
        for buffer in getattr(self, "reference_pyramid", ()):
            try:
                if buffer is not None and hasattr(buffer, "destroy"):
                    _destroy_work_item(buffer)
            except Exception:
                pass
        self.reference_pyramid = ()
        self.ref_gray_gpu = None
        self._close_resident_flow_buffer()


class FeatureMatchingGPUAligner:
    """Taichi Vision OFB/AKAZE feature aligner with native descriptors."""

    @staticmethod
    def _validate_homography(
        homography,
        src_points,
        dst_points,
        inlier_mask,
        *,
        width: int,
        height: int,
        reproj_threshold: float = 5.0,
    ):
        """Return a safe support->reference transform or a robust translation.

        Feature matching can occasionally produce a numerically valid but
        geometrically nonsensical projective matrix (especially on repeated
        texture/blurred burst frames).  Applying such a matrix is worse than
        skipping alignment: it creates the long streaks/ghosting visible in
        Average output.  Keep this check on the small host-side point arrays;
        image buffers remain resident on the active backend.
        """

        try:
            src = np.asarray(src_points, dtype=np.float64)
            dst = np.asarray(dst_points, dtype=np.float64)
            if src.ndim != 2 or dst.ndim != 2 or src.shape[1] != 2 or dst.shape[1] != 2:
                return None
            n = min(len(src), len(dst))
            if n < 4:
                return None
            src = src[:n]
            dst = dst[:n]
            if inlier_mask is None:
                inliers = np.ones(n, dtype=bool)
            else:
                inliers = np.asarray(inlier_mask).reshape(-1)[:n].astype(bool, copy=False)
            inlier_count = int(inliers.sum())
            min_inliers = max(8, min(32, int(np.ceil(0.08 * n))))

            def _translation_fallback():
                if inlier_count < max(6, min(24, int(np.ceil(0.06 * n)))):
                    return None
                delta = dst[inliers] - src[inliers]
                if delta.size == 0 or not np.isfinite(delta).all():
                    return None
                median = np.median(delta, axis=0)
                mad = np.median(np.abs(delta - median), axis=0)
                spread = float(np.max(mad))
                max_shift = 0.5 * max(float(width), float(height))
                if (
                    not np.isfinite(median).all()
                    or spread > max(3.0, 1.5 * float(reproj_threshold))
                    or float(np.max(np.abs(median))) > max_shift
                ):
                    return None
                return np.asarray(
                    [[1.0, 0.0, median[0]], [0.0, 1.0, median[1]], [0.0, 0.0, 1.0]],
                    dtype=np.float32,
                )

            if inlier_count < min_inliers:
                return _translation_fallback()

            H = np.asarray(homography, dtype=np.float64)
            if H.shape != (3, 3) or not np.isfinite(H).all():
                return _translation_fallback()
            if abs(float(H[2, 2])) < 1e-10:
                return _translation_fallback()
            H = H / H[2, 2]

            src_h = np.concatenate((src[inliers], np.ones((inlier_count, 1))), axis=1)
            projected_h = src_h @ H.T
            denom = projected_h[:, 2]
            if not np.isfinite(projected_h).all() or np.any(np.abs(denom) < 1e-8):
                return _translation_fallback()
            projected = projected_h[:, :2] / denom[:, None]
            errors = np.linalg.norm(projected - dst[inliers], axis=1)
            p90 = float(np.percentile(errors, 90)) if errors.size else float("inf")
            if not np.isfinite(errors).all() or p90 > max(10.0, 2.5 * float(reproj_threshold)):
                return _translation_fallback()

            affine = H[:2, :2]
            det = float(np.linalg.det(affine))
            if not np.isfinite(det) or det <= 0.0:
                return _translation_fallback()
            singular = np.linalg.svd(affine, compute_uv=False)
            if (
                not np.isfinite(singular).all()
                or float(singular.min()) < 0.10
                or float(singular.max()) > 10.0
            ):
                return _translation_fallback()

            corners = np.asarray(
                [[0.0, 0.0], [float(width), 0.0], [0.0, float(height)], [float(width), float(height)]],
                dtype=np.float64,
            )
            corners_h = np.concatenate((corners, np.ones((4, 1))), axis=1) @ H.T
            cden = corners_h[:, 2]
            if not np.isfinite(corners_h).all() or np.any(np.abs(cden) < 1e-8):
                return _translation_fallback()
            corners_xy = corners_h[:, :2] / cden[:, None]
            margin_x = 0.75 * float(width)
            margin_y = 0.75 * float(height)
            if (
                float(corners_xy[:, 0].min()) < -margin_x
                or float(corners_xy[:, 0].max()) > float(width) + margin_x
                or float(corners_xy[:, 1].min()) < -margin_y
                or float(corners_xy[:, 1].max()) > float(height) + margin_y
            ):
                return _translation_fallback()
            return np.asarray(H, dtype=np.float32)
        except Exception:
            return None

    def __init__(
        self,
        ref_analysis_gpu: TaichiGPUBuffer,
        *,
        feature_type: str = "orb",
        work_scale: float = 0.50,
        full_shape: Optional[Tuple[int, int]] = None,
        feature_config: Optional[dict] = None,
    ):
        from taichi_vision import taichi_aot
        taichi_aot = _managed_api(taichi_aot)

        self.feature_type = str(feature_type).lower().strip()
        self.work_scale = work_scale
        self.config = feature_config or {}
        self.apap_fit_grid_size = _resolve_apap_fit_grid_size(self.config)
        requested_warp_method = str(
            self.config.get("warp_method", "homography")
        ).strip().lower()
        self.warp_method = "homography"
        if requested_warp_method != "homography":
            print(
                f"[GPU Pipeline][Align] {self.feature_type.upper()} requested "
                f"warp={requested_warp_method.upper()} is disabled; using HOMOGRAPHY"
            )
        print(
            f"[GPU Pipeline][Align] feature={self.feature_type.upper()} "
            f"warp={self.warp_method.upper()}"
        )

        ref_gray_gpu = taichi_aot.cvtColor(ref_analysis_gpu, taichi_aot.COLOR_RGB2GRAY)
        h, w = ref_gray_gpu.shape[:2]
        if full_shape is not None:
            self.target_h, self.target_w = int(full_shape[0]), int(full_shape[1])
        else:
            self.target_h, self.target_w = h, w

        if ref_analysis_gpu.shape[:2] != (self.target_h, self.target_w):
            self.work_h, self.work_w = ref_analysis_gpu.shape[:2]
        else:
            self.work_h = max(32, int(self.target_h * work_scale))
            self.work_w = max(32, int(self.target_w * work_scale))

        if (self.work_h, self.work_w) != (h, w):
            ref_gray_work = taichi_aot.resize(
                ref_gray_gpu,
                (self.work_w, self.work_h),
                interpolation=taichi_aot.INTER_AREA,
                return_gpu=True,
            )
            _destroy_work_item(ref_gray_gpu)
            ref_gray_gpu = ref_gray_work

        self.ref_gray_gpu = ref_gray_gpu
        self.feature_type = "akaze" if "akaze" in self.feature_type else "ofb"
        self._feature_reference_cache = None
        self._feature_resident_matches = False
        # Reuse the reference on all resident graphics backends.  CUDA,
        # Vulkan, and OpenGL have target-qualified feature graphs; CPU keeps
        # the established stateless path as a compatibility fallback.
        try:
            feature_arch = str(getattr(taichi_aot.engine, "arch", "")).lower()
            if (
                feature_arch in {"cuda", "vulkan", "opengl"}
                and os.environ.get("TAICHI_CUDA_FEATURE_CACHE", "1") != "0"
            ):
                self._feature_reference_cache = taichi_aot.create_feature_reference_cache(
                    self.feature_type,
                    self.ref_gray_gpu,
                    ratio_threshold=float(self.config.get("ratio", 0.75)),
                    grid_size=max(8, int(self.config.get("grid_size", 32))),
                    threshold=float(
                        self.config.get(
                            "threshold", 0.001 if self.feature_type == "akaze" else 0.015
                        )
                    ),
                    margin=max(4, int(self.config.get("margin", 15))),
                    max_keypoints=int(self.config.get("max_keypoints", 1200)),
                    k_contrast=float(self.config.get("k_contrast", 0.02)),
                    num_fed_steps=max(1, int(self.config.get("num_fed_steps", 8))),
                )
                resident_algorithm_allowed = (
                    self.warp_method == "homography"
                    and (
                        self.feature_type == "ofb"
                        or (
                            self.feature_type == "akaze"
                            and os.environ.get("TAICHI_FEATURE_RESIDENT_AKAZE", "0")
                            == "1"
                        )
                    )
                )
                # CUDA's resident correspondence pack path can corrupt the
                # native heap after matching completes. Keep CUDA on the
                # cache-backed compatibility readback path until that graph
                # is validated there; feature extraction and RANSAC still run
                # on the selected backend / host respectively.
                resident_match_backend_allowed = feature_arch != "cuda"
                self._feature_resident_matches = (
                    resident_algorithm_allowed
                    and resident_match_backend_allowed
                    and os.environ.get("TAICHI_FEATURE_RESIDENT_MATCHES", "1") != "0"
                    and taichi_aot.aot_graph_available(
                        self.feature_type, "compact_matches_to_points"
                    )
                    and taichi_aot.aot_graph_available(
                        self.feature_type, "pack_compacted_points"
                    )
                )
                # The cache owns only derived keypoints/descriptors.  The
                # grayscale reference itself is no longer needed per frame.
                _destroy_work_item(self.ref_gray_gpu)
                self.ref_gray_gpu = None
                print(
                    f"[GPU Pipeline] {feature_arch.upper()} {self.feature_type.upper()} "
                    f"reference cache ready "
                    f"(levels={self._feature_reference_cache.num_levels}, "
                    f"resident_matches={self._feature_resident_matches})"
                )
        except Exception as exc:
            self._feature_reference_cache = None
            self._feature_resident_matches = False
            print(
                f"[GPU Pipeline] {feature_arch.upper()} reference cache unavailable; "
                f"using legacy path: {exc}"
            )

    def align_frame(
        self,
        supp_linear_gpu,
        *,
        analysis_frame_gpu=None,
        secondary_frame_to_warp=None,
        stop_event=None,
        return_gpu=True,
        return_transform: bool = False,
    ):
        from taichi_vision import taichi_aot
        taichi_aot = _managed_api(taichi_aot)

        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Alignment cancelled.")
            elif callable(stop_event) and stop_event():
                raise RuntimeError("Alignment cancelled.")

        src_for_analysis = (
            analysis_frame_gpu if analysis_frame_gpu is not None else supp_linear_gpu
        )
        supp_gray_gpu = taichi_aot.cvtColor(src_for_analysis, taichi_aot.COLOR_RGB2GRAY)
        if tuple(int(v) for v in supp_gray_gpu.shape[:2]) != (self.work_h, self.work_w):
            supp_gray_work = taichi_aot.resize(
                supp_gray_gpu,
                (self.work_w, self.work_h),
                interpolation=taichi_aot.INTER_AREA,
                return_gpu=True,
            )
            _destroy_work_item(supp_gray_gpu)
            supp_gray_gpu = supp_gray_work

        resident_matches = None
        try:
            if self._feature_reference_cache is not None:
                if self._feature_resident_matches:
                    resident_matches = taichi_aot.match_feature_reference_resident(
                        self._feature_reference_cache, supp_gray_gpu
                    )
                    matched = None
                else:
                    matched = taichi_aot.match_feature_reference(
                        self._feature_reference_cache, supp_gray_gpu
                    )
            elif self.feature_type == "akaze":
                matched = taichi_aot.akaze(
                    self.ref_gray_gpu,
                    supp_gray_gpu,
                    ratio_threshold=float(self.config.get("ratio", 0.75)),
                    grid_size=max(8, int(self.config.get("grid_size", 32))),
                    threshold=float(self.config.get("threshold", 0.001)),
                    margin=max(4, int(self.config.get("margin", 15))),
                    max_keypoints=int(self.config.get("max_keypoints", 1200)),
                    k_contrast=float(self.config.get("k_contrast", 0.02)),
                    num_fed_steps=max(1, int(self.config.get("num_fed_steps", 8))),
                )
            else:
                matched = taichi_aot.ofb(
                    self.ref_gray_gpu,
                    supp_gray_gpu,
                    ratio_threshold=float(self.config.get("ratio", 0.75)),
                    grid_size=max(8, int(self.config.get("grid_size", 24))),
                    threshold=float(self.config.get("threshold", 0.03)),
                    margin=max(4, int(self.config.get("margin", 15))),
                    max_keypoints=int(self.config.get("max_keypoints", 1200)),
                )
        finally:
            _destroy_work_item(supp_gray_gpu)

        H_matrix = None
        apap_ref_points = None
        apap_support_points = None
        matched_pair_count = 0
        if resident_matches is not None:
            matched_pair_count = int(resident_matches.count)
        elif matched is not None and len(matched) >= 2:
            matched_pair_count = min(len(matched[0]), len(matched[1]))
        scale_x = self.target_w / float(self.work_w)
        scale_y = self.target_h / float(self.work_h)
        if resident_matches is not None:
            try:
                if resident_matches.count >= 4:
                    pts_ref_gpu, pts_supp_gpu = resident_matches.point_views()
                    reproj_threshold = max(
                        0.5, float(self.config.get("ransac_threshold", 5.0))
                    )
                    ransac_hypotheses = max(
                        64, int(self.config.get("ransac_hypotheses", 256))
                    )
                    ransac_iters = max(1, int(self.config.get("ransac_iters", 2)))
                    if self.feature_type == "ofb":
                        from ...alignment.feature_matching.OFB import OFBAlgorithm

                        H_candidate, inlier_mask = OFBAlgorithm._find_homography(
                            pts_supp_gpu.to_numpy(),
                            pts_ref_gpu.to_numpy(),
                            threshold=reproj_threshold,
                            hypotheses=ransac_hypotheses,
                            refinements=ransac_iters,
                        )
                    else:
                        H_candidate, inlier_mask = taichi_aot.find_homography(
                            pts_supp_gpu,
                            pts_ref_gpu,
                            method="RANSAC",
                            ransacReprojThreshold=reproj_threshold,
                            n_hypotheses=ransac_hypotheses,
                            max_iters=ransac_iters,
                            return_gpu=True,
                        )
                    if H_candidate is not None:
                        if self.feature_type == "ofb":
                            H_matrix = scale_homography(
                                np.asarray(H_candidate, dtype=np.float32),
                                source_shape=(self.work_h, self.work_w),
                                destination_shape=(self.target_h, self.target_w),
                            )
                        else:
                            H_matrix = scale_homography(
                                H_candidate,
                                source_shape=(self.work_h, self.work_w),
                                destination_shape=(self.target_h, self.target_w),
                            )
                    if self.warp_method == "apap":
                        if H_matrix is not None:
                            pts_ref = np.ascontiguousarray(
                                pts_ref_gpu.to_numpy(), dtype=np.float32
                            )
                            pts_supp = np.ascontiguousarray(
                                pts_supp_gpu.to_numpy(), dtype=np.float32
                            )
                            apap_ref_points, apap_support_points = (
                                _select_ransac_inlier_correspondences(
                                    pts_ref, pts_supp, inlier_mask
                                )
                            )
                            scale = np.array([scale_x, scale_y], dtype=np.float32)
                            apap_ref_points *= scale
                            apap_support_points *= scale
                    if isinstance(inlier_mask, TaichiGPUBuffer):
                        get_engine().sync()
                        _destroy_work_item(inlier_mask)
            finally:
                resident_matches.close()
        elif matched is not None and len(matched) >= 2:
            pts_ref = np.ascontiguousarray(matched[0], dtype=np.float32)
            pts_supp = np.ascontiguousarray(matched[1], dtype=np.float32)
            if len(pts_ref) >= 4 and len(pts_supp) >= 4:
                pts_ref *= np.array([scale_x, scale_y], dtype=np.float32)
                pts_supp *= np.array([scale_x, scale_y], dtype=np.float32)
                # Spend extra RANSAC work only when there are enough
                # correspondences for it to improve model selection.  Sparse
                # AKAZE matches already fail closed via the geometry gate.
                akaze_ransac_quality = len(pts_ref) >= 64
                ransac_hypotheses = max(
                    64,
                    int(
                        self.config.get(
                            "ransac_hypotheses",
                            1024
                            if self.feature_type == "akaze" and akaze_ransac_quality
                            else 256,
                        )
                    ),
                )
                ransac_iters = max(
                    1,
                    int(
                        self.config.get(
                            "ransac_iters",
                            3
                            if self.feature_type == "akaze" and akaze_ransac_quality
                            else 2,
                        )
                    ),
                )
                reproj_threshold = max(
                    0.5, float(self.config.get("ransac_threshold", 5.0))
                )
                if self.feature_type == "ofb":
                    from ...alignment.feature_matching.OFB import OFBAlgorithm

                    H_candidate, inlier_mask = OFBAlgorithm._find_homography(
                        pts_supp,
                        pts_ref,
                        threshold=reproj_threshold,
                        hypotheses=ransac_hypotheses,
                        refinements=ransac_iters,
                    )
                    H_matrix = (
                        None
                        if H_candidate is None
                        else np.asarray(H_candidate, dtype=np.float32)
                    )
                else:
                    H_candidate, inlier_mask = taichi_aot.find_homography(
                        pts_supp,
                        pts_ref,
                        method="RANSAC",
                        ransacReprojThreshold=reproj_threshold,
                        n_hypotheses=ransac_hypotheses,
                        max_iters=ransac_iters,
                        return_gpu=False,
                    )
                    # AKAZE's binary matches are more vulnerable to repeated
                    # texture producing a plausible-looking but wrong H.
                    H_matrix = self._validate_homography(
                        H_candidate,
                        pts_supp,
                        pts_ref,
                        inlier_mask,
                        width=self.target_w,
                        height=self.target_h,
                        reproj_threshold=reproj_threshold,
                    )
                if self.warp_method == "apap" and H_matrix is not None:
                    apap_ref_points, apap_support_points = (
                        _select_ransac_inlier_correspondences(
                            pts_ref, pts_supp, inlier_mask
                        )
                    )

        if H_matrix is not None:
            if self.warp_method == "apap":
                if apap_ref_points is None or apap_support_points is None:
                    raise RuntimeError(
                        f"{self.feature_type.upper()} APAP warp needs at least four matched point pairs"
                    )
                from taichi_vision.taichi_algorithm.alignment.apap import fit_apap

                print(
                    "[GPU Pipeline][Align] APAP RANSAC inliers="
                    f"{len(apap_ref_points)} (no second correspondence filter)"
                )
                # RANSAC's H maps support -> reference. APAP's inverse map
                # consumes reference coordinates and returns support
                # coordinates, so reuse the validated transform in reverse
                # instead of estimating the same global control a second time.
                apap_global_h = np.linalg.inv(
                    np.asarray(H_matrix, dtype=np.float64)
                )
                if return_transform:
                    # RAW merges the CFA carrier, not this RGB proxy. Return
                    # the local inverse field instead of losing APAP here by
                    # returning only its global RANSAC homography.
                    apap_warp = fit_apap(
                        apap_ref_points,
                        apap_support_points,
                        global_homography=apap_global_h,
                        grid_shape=(self.apap_fit_grid_size,) * 2,
                    )
                    flow = apap_warp.to_flow(
                        (33, 33), full_shape=(self.target_h, self.target_w)
                    )
                    flow_gpu = taichi_aot.upload(flow, is_vector=False)
                    warped_primary = None
                    warped_secondary = None
                    try:
                        if supp_linear_gpu is not None:
                            warped_primary = taichi_aot.remap_with_flow(
                                supp_linear_gpu, flow_gpu,
                                int(supp_linear_gpu.shape[0]), int(supp_linear_gpu.shape[1]),
                                return_gpu=True,
                            )
                        if secondary_frame_to_warp is not None:
                            warped_secondary = taichi_aot.remap_with_flow(
                                secondary_frame_to_warp, flow_gpu,
                                int(secondary_frame_to_warp.shape[0]),
                                int(secondary_frame_to_warp.shape[1]),
                                return_gpu=True,
                            )
                    except BaseException:
                        for buffer in (warped_primary, warped_secondary, flow_gpu):
                            if buffer is not None:
                                _destroy_work_item(buffer)
                        raise
                    print(
                        "[GPU Pipeline][Align] APAP carrier transform=local_flow "
                        f"grid={flow.shape[:2]} model_grid="
                        f"{self.apap_fit_grid_size}x{self.apap_fit_grid_size} "
                        "warp=AOT-flow units=flow_pixels"
                    )
                    return warped_primary, warped_secondary, flow_gpu

                from taichi_vision.taichi_algorithm.alignment.mesh_warp import (
                    warp_apap,
                )

                warped_primary = None
                if supp_linear_gpu is not None:
                    warped_primary = _track_gpu_result(
                        warp_apap(
                            supp_linear_gpu,
                            apap_ref_points,
                            apap_support_points,
                            dsize=(self.target_w, self.target_h),
                            global_homography=apap_global_h,
                            fit_grid_shape=(self.apap_fit_grid_size,) * 2,
                            return_gpu=True,
                        )
                    )
            elif supp_linear_gpu is None:
                warped_primary = None
            elif self.feature_type == "ofb":
                from ...alignment.feature_matching.OFB import OFBAlgorithm

                prim_h, prim_w = (int(v) for v in supp_linear_gpu.shape[:2])
                H_prim = (
                    scale_homography(
                        H_matrix,
                        source_shape=(self.target_h, self.target_w),
                        destination_shape=(prim_h, prim_w),
                    )
                    if (prim_h, prim_w) != (self.target_h, self.target_w)
                    else H_matrix
                )
                primary_np = np.ascontiguousarray(supp_linear_gpu.to_numpy())
                warped_primary_np = OFBAlgorithm._warp_perspective(
                    primary_np, H_prim, (prim_w, prim_h)
                )
                warped_primary = taichi_aot.upload(
                    np.ascontiguousarray(warped_primary_np), is_vector=False
                )
            else:
                prim_h, prim_w = (int(v) for v in supp_linear_gpu.shape[:2])
                H_prim = (
                    scale_homography(
                        H_matrix,
                        source_shape=(self.target_h, self.target_w),
                        destination_shape=(prim_h, prim_w),
                    )
                    if (prim_h, prim_w) != (self.target_h, self.target_w)
                    else H_matrix
                )
                warped_primary = taichi_aot.warp_perspective(
                    supp_linear_gpu,
                    H_prim,
                    (prim_w, prim_h),
                    return_gpu=True,
                )
            warped_secondary = None
            if secondary_frame_to_warp is not None:
                scale_mat = np.array(
                    [[1.0 / scale_x, 0, 0], [0, 1.0 / scale_y, 0], [0, 0, 1.0]],
                    dtype=np.float32,
                )
                scale_mat_inv = np.array(
                    [[scale_x, 0, 0], [0, scale_y, 0], [0, 0, 1.0]],
                    dtype=np.float32,
                )
                H_work = scale_mat @ H_matrix @ scale_mat_inv
                if self.warp_method == "apap":
                    scale = np.array([scale_x, scale_y], dtype=np.float32)
                    work_ref_points = apap_ref_points / scale
                    work_support_points = apap_support_points / scale
                    warped_secondary = _track_gpu_result(
                        warp_apap(
                            secondary_frame_to_warp,
                            work_ref_points,
                            work_support_points,
                            dsize=(self.work_w, self.work_h),
                            global_homography=np.linalg.inv(
                                np.asarray(H_work, dtype=np.float64)
                            ),
                            return_gpu=True,
                        )
                    )
                elif self.feature_type == "ofb":
                    secondary_np = np.ascontiguousarray(
                        secondary_frame_to_warp.to_numpy()
                    )
                    warped_secondary_np = OFBAlgorithm._warp_perspective(
                        secondary_np, H_work, (self.work_w, self.work_h)
                    )
                    warped_secondary = taichi_aot.upload(
                        np.ascontiguousarray(warped_secondary_np), is_vector=False
                    )
                else:
                    warped_secondary = taichi_aot.warp_perspective(
                        secondary_frame_to_warp,
                        H_work,
                        (self.work_w, self.work_h),
                        return_gpu=True,
                    )
            if return_transform:
                return warped_primary, warped_secondary, np.ascontiguousarray(
                    H_matrix, dtype=np.float32
                )
            return warped_primary, warped_secondary
        else:
            print(
                f"[GPU Pipeline][Align] feature={self.feature_type.upper()} "
                f"warp={self.warp_method.upper()} not_applied=no_trusted_transform "
                f"matched_pairs={matched_pair_count}; support remains unaligned"
            )
            if return_transform:
                return supp_linear_gpu, secondary_frame_to_warp, None
            return supp_linear_gpu, secondary_frame_to_warp

    def close(self):
        cache = getattr(self, "_feature_reference_cache", None)
        if cache is not None:
            try:
                cache.close()
            except Exception:
                pass
        self._feature_reference_cache = None
        self._feature_resident_matches = False
        ref_gray_gpu = getattr(self, "ref_gray_gpu", None)
        if ref_gray_gpu is not None and hasattr(ref_gray_gpu, "destroy"):
            _destroy_work_item(ref_gray_gpu)
        self.ref_gray_gpu = None


def _scale_f32_scalar_gpu(source_gpu, scale: float):
    """Scale a scalar f32 resident buffer without a host round-trip."""
    from taichi_vision import taichi_aot
    taichi_aot = _managed_api(taichi_aot)
    from taichi_vision.taichi_algorithm.aot_api import _mod

    output = _managed_api(taichi_aot.get_engine()).allocate(
        tuple(int(value) for value in source_gpu.shape), dtype=np.float32
    )
    _mod("common").run(
        "scale_f32_2d", src=source_gpu, dst=output, scale=float(scale)
    )
    return output


class FarnebackResidentAligner(_ResidentFlowBufferMixin):
    """Persistent native Farneback session for the resident pipeline."""

    def __init__(
        self,
        ref_analysis_gpu: TaichiGPUBuffer,
        *,
        full_shape: Optional[Tuple[int, int]] = None,
        alignment_config: Optional[dict] = None,
        **_unused,
    ):
        from taichi_vision import taichi_aot
        taichi_aot = _managed_api(taichi_aot)
        from taichi_vision.taichi_algorithm.pyramid.pyramid import build_image_pyramid_gpu
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.farneback_flow import (
            FarnebackFlow as FarnebackFlowCPU,
        )

        requested = dict(alignment_config or {})
        mode = str(requested.get("mode", "balance")).strip().lower()
        if mode in ("balanced", "medium", "normal"):
            mode = "balance"
        if mode not in FarnebackFlowCPU.PRESETS:
            mode = "balance"
        self.config = dict(FarnebackFlowCPU.PRESETS[mode])
        self.config.update(requested)
        self.config["mode"] = mode
        self.full_h, self.full_w = (
            (int(full_shape[0]), int(full_shape[1]))
            if full_shape is not None
            else tuple(int(v) for v in ref_analysis_gpu.shape[:2])
        )
        self._init_resident_flow_buffer()
        ref_gray_unit_gpu = taichi_aot.cvtColor(
            ref_analysis_gpu, taichi_aot.COLOR_RGB2GRAY
        )
        try:
            # Farneback's polynomial-expansion constants are calibrated for
            # OpenCV-style luminance [0, 255].  Resident RAW analysis uses
            # linear float [0, 1]; feeding that range directly produced a
            # near-zero flow field even though remap/CFA accumulation ran.
            self.ref_gray_gpu = _scale_f32_scalar_gpu(ref_gray_unit_gpu, 255.0)
        finally:
            _destroy_work_item(ref_gray_unit_gpu)
        self.work_h, self.work_w = (int(self.ref_gray_gpu.shape[0]), int(self.ref_gray_gpu.shape[1]))
        levels = max(1, int(self.config.get("levels", 3)))
        self.reference_pyramid = tuple(
            build_image_pyramid_gpu(self.ref_gray_gpu, n_levels=levels, min_size=32, session=_buffer_session())
        )
        self.ref_gray_gpu = self.reference_pyramid[0]
        print(
            "[GPU Pipeline] Aligner: Farneback GPU "
            f"(mode={mode}, levels={levels}, input_range=0..255, resident-reference=true)"
        )

    def align_frame(
        self,
        supp_linear_gpu,
        *,
        analysis_frame_gpu=None,
        secondary_frame_to_warp=None,
        stop_event=None,
        return_gpu=True,
        return_transform: bool = False,
    ):
        from taichi_vision import taichi_aot
        taichi_aot = _managed_api(taichi_aot)

        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Farneback alignment cancelled.")
            if callable(stop_event) and stop_event():
                raise RuntimeError("Farneback alignment cancelled.")
        source = analysis_frame_gpu if analysis_frame_gpu is not None else supp_linear_gpu
        supp_gray_unit_gpu = taichi_aot.cvtColor(source, taichi_aot.COLOR_RGB2GRAY)
        supp_gray_gpu = None
        flow_gpu = None
        try:
            supp_gray_gpu = _scale_f32_scalar_gpu(supp_gray_unit_gpu, 255.0)
            _destroy_work_item(supp_gray_unit_gpu)
            supp_gray_unit_gpu = None
            if tuple(supp_gray_gpu.shape[:2]) != (self.work_h, self.work_w):
                resized = taichi_aot.resize(
                    supp_gray_gpu, (self.work_w, self.work_h),
                    interpolation=taichi_aot.INTER_AREA, return_gpu=True,
                )
                _destroy_work_item(supp_gray_gpu)
                supp_gray_gpu = resized
            flow_destination = self._ensure_resident_flow_buffer(
                (self.work_h, self.work_w, 2)
            )
            flow_gpu = taichi_aot.farneback_flow(
                self.ref_gray_gpu,
                supp_gray_gpu,
                pyr_scale=float(self.config.get("pyr_scale", 0.5)),
                num_levels=max(1, int(self.config.get("levels", 3))),
                win_size=max(5, int(self.config.get("winsize", 17))),
                num_iters=max(1, int(self.config.get("iterations", 3))),
                poly_n=max(5, int(self.config.get("poly_n", 5))),
                poly_sigma=float(self.config.get("poly_sigma", 1.2)),
                return_gpu=True,
                reference_pyramid=self.reference_pyramid,
                dst=flow_destination,
            )
            flow_gpu = self._normalize_resident_flow(flow_gpu, flow_destination)
            smooth = _parse_bool(self.config.get("smooth", True), default=True)
            if not smooth:
                from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.farneback_flow import (
                    FarnebackFlow as FarnebackFlowCPU,
                )
                step = max(2, int(self.config.get("grid_step", 16)))
                flow_np = flow_gpu.to_numpy()
                flow_quant = FarnebackFlowCPU._quantize_to_blocks(flow_np, step)
                flow_gpu = self._store_quantized_flow(taichi_aot, flow_quant)
            warped_primary = None
            if supp_linear_gpu is not None:
                prim_h, prim_w = (int(v) for v in supp_linear_gpu.shape[:2])
                warped_primary = taichi_aot.remap_with_flow(
                    supp_linear_gpu,
                    flow_gpu,
                    prim_h,
                    prim_w,
                    return_gpu=True,
                )
            warped_secondary = None
            if secondary_frame_to_warp is not None:
                sec_h, sec_w = (int(v) for v in secondary_frame_to_warp.shape[:2])
                warped_secondary = taichi_aot.remap_with_flow(
                    secondary_frame_to_warp,
                    flow_gpu,
                    sec_h,
                    sec_w,
                    return_gpu=True,
                )
            if return_transform:
                retained_flow = self._resident_flow_view(flow_gpu)
                flow_gpu = None
                return warped_primary, warped_secondary, retained_flow
            return warped_primary, warped_secondary
        finally:
            if (
                flow_gpu is not None
                and flow_gpu is not getattr(self, "_resident_flow_buffer", None)
                and flow_gpu
                is not getattr(self, "_resident_quantized_flow_buffer", None)
                and hasattr(flow_gpu, "destroy")
            ):
                _destroy_work_item(flow_gpu)
            if supp_gray_gpu is not None and hasattr(supp_gray_gpu, "destroy"):
                _destroy_work_item(supp_gray_gpu)
            if supp_gray_unit_gpu is not None and hasattr(supp_gray_unit_gpu, "destroy"):
                _destroy_work_item(supp_gray_unit_gpu)

    def close(self):
        for buffer in getattr(self, "reference_pyramid", ()):
            try:
                if buffer is not None and hasattr(buffer, "destroy"):
                    _destroy_work_item(buffer)
            except Exception:
                pass
        self.reference_pyramid = ()
        self.ref_gray_gpu = None
        self._close_resident_flow_buffer()


def _component_factory(factory):
    @wraps(factory)
    def build(*args, **kwargs):
        return _own_component(factory(*args, **kwargs))
    return build


@_component_factory
def create_resident_aligner(
    alignment_plan: str,
    ref_analysis_gpu: TaichiGPUBuffer,
    *,
    work_scale: float = 0.50,
    full_shape: Optional[Tuple[int, int]] = None,
    alignment_config: Optional[dict] = None,
    noise_score: Optional[float] = None,
):
    """Factory creating the appropriate GPU-resident aligner instance."""
    from ...catalog import get_spec

    spec = get_spec("alignment", alignment_plan or "none", context="resident")
    route = spec.resident_route
    if route == "none":
        print("[GPU Pipeline] Aligner: No Alignment (Bypass)")
        return NoAlignmentGPUAligner(ref_analysis_gpu)
    elif route in ("ofb", "akaze"):
        print(f"[GPU Pipeline] Aligner: Feature Matching ({spec.name})")
        return FeatureMatchingGPUAligner(
            ref_analysis_gpu,
            feature_type=route,
            work_scale=work_scale,
            full_shape=full_shape,
            feature_config=alignment_config,
        )
    elif route == "block_matching":
        print("[GPU Pipeline] Aligner: Block Matching GPU")
        return BlockMatchingResidentAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            alignment_config=alignment_config,
        )
    elif route == "lucas_kanade":
        print("[GPU Pipeline] Aligner: Lucas Kanade GPU")
        return LucasKanadeResidentAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            alignment_config=alignment_config,
        )
    elif route == "farneback":
        return FarnebackResidentAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            alignment_config=alignment_config,
        )
    elif route == "block_flow":
        print(f"[GPU Pipeline] Aligner: Dense Optical Flow Adaptive Multi-Tile ({spec.name})")
        from ..fusionet_engine.flownet_inference import AOTOpticalFlowAligner

        smooth = _parse_bool((alignment_config or {}).get("smooth", True), default=True)

        return AOTOpticalFlowAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            tile_size=32,
            noise_score=noise_score,
            smooth=smooth,
            adaptive=True,
        )

    raise ValueError(f"No resident aligner registered for '{spec.name}'")


# ---------------------------------------------------------------------------
# GPU-Resident Weight + Blend Bridge
# ---------------------------------------------------------------------------


def _buffer_session():
    runtime = current_pipeline_runtime()
    return runtime.buffer_session if runtime is not None else None


def _managed_api(api):
    session = _buffer_session()
    return session.managed_api(api) if session is not None else api


def _track_gpu_result(result):
    session = _buffer_session()
    return session.track_result(result) if session is not None else result


def _own_component(component, *, releaser=None):
    session = _buffer_session()
    return session.own(component, releaser=releaser) if session is not None else component


def _export_result(result):
    session = _buffer_session()
    return session.detach(session.own(result)) if session is not None else result


def _destroy_work_item(item):
    """Safely destroy GPU buffers or nested tuples of GPU buffers."""
    if item is None:
        return
    if isinstance(item, tuple):
        for el in item:
            if el is not None and hasattr(el, "destroy"):
                try:
                    el.destroy()
                except Exception:
                    pass
    elif hasattr(item, "destroy"):
        try:
            item.destroy()
        except Exception:
            pass


def _destroy_work_item_except(item, protected):
    """Destroy queued work buffers without releasing a shared carrier."""
    if item is None:
        return
    session = _buffer_session()
    if session is not None:
        session.release_tree(item)
        return
    values = item if isinstance(item, tuple) else (item,)
    seen = set()
    for value in values:
        if value is None or value is protected or id(value) in seen:
            continue
        seen.add(id(value))
        _destroy_work_item(value)


def _prepare_raw_aligned_analysis(
    support_analysis,
    alignment_preview,
    transform,
    *,
    align_shape,
    warp_analysis,
):
    """Resolve exactly one support->reference warp for RAW weight analysis.

    Resident aligners return both an already-warped primary image and the
    transform used to create it.  RAW Native needs the transform again for the
    CFA carrier, but must not apply it a second time to that aligned RGB proxy.

    The aligner preview can be reused only when it is a distinct buffer on the
    canonical analysis grid.  A smaller RAW proxy may otherwise have been
    expanded to the full carrier grid by an aligner whose primary-image
    contract targets ``full_shape``.  In that case, discard the preview and
    warp the original proxy once on its own grid.

    Returns ``(analysis_for_weight, preview_to_destroy)``.  Ownership of a
    reusable preview transfers to ``analysis_for_weight``.
    """

    target_shape = (int(align_shape[0]), int(align_shape[1]))
    if transform is None:
        return support_analysis, alignment_preview

    preview_shape = getattr(alignment_preview, "shape", ())
    preview_matches = (
        alignment_preview is not None
        and alignment_preview is not support_analysis
        and len(preview_shape) >= 2
        and tuple(int(value) for value in preview_shape[:2]) == target_shape
    )
    if preview_matches:
        return alignment_preview, None

    aligned = warp_analysis(support_analysis, transform, target_shape)
    return aligned, alignment_preview


def _gpu_blend_frame(sum_img_gpu, weight_sum_gpu, supp_aligned_gpu, weight_work_gpu):
    """Blend one support frame into the GPU-resident accumulator.

    Uses the shared Taichi accumulator. Scalar WeightNet maps stay 2D and
    dispatch to scalar-to-RGB accumulation; SpatialFusion and legacy RGB maps
    retain their existing scalar/vec3 dispatch.
    """
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi import (
        accumulate_spatial_merging_taichi,
    )

    accumulate_spatial_merging_taichi(
        current_image_full=supp_aligned_gpu.view_as_vector(False),
        weight_map_work=(
            weight_work_gpu.view_as_vector(False)
            if len(weight_work_gpu.shape) > 2
            else weight_work_gpu
        ),
        final_image_sum=sum_img_gpu.view_as_vector(False),
        weight_map_sum_full=weight_sum_gpu.view_as_vector(False),
    )


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
    taichi_aot = _managed_api(taichi_aot)
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

    engine = _managed_api(get_engine())
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
    weightnet_channels = _resolve_weightnet_input_channels(
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
            weightnet_support_workspace = _WeightNetReadbackWorkspace(
                geometry.weight_shape, channels=weightnet_channels
            )
            weightnet_upload_workspace = _WeightNetUploadWorkspace(
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
            alignment_mode = (
                "analysis"
                if normalized_engine in ("fusionet", "spatial_fusion")
                else ANALYSIS_AUTO_ENHANCE_MODE
            )
            analysis_params = _resolve_engine_analysis_params(
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
                ref_weight_analysis_gpu = prepare_analysis_proxy_gpu(
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
                prepare_reference_analysis_and_noise(
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
                _destroy_work_item(ref_proxy_full_gpu)
            ref_proxy_full_gpu = None

            ref_spatial_gray_gpu = None
            if normalized_engine == "spatial_fusion":
                (
                    tile, overlap_value, motion, noise_offset, noise_sigma, sigma_mode
                ) = _resolve_spatial_analysis_config(
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
                spatial_scratch = _own_component(SpatialScratchCache(), releaser=lambda cache: cache.clear())
                spatial_state = (tile, overlap_value, motion, noise_offset, noise_sigma)
            if normalized_engine == "spatial_fusion":
                ref_spatial_gray_gpu = buffer_session.own(
                    taichi_aot.cvtColor(
                        ref_weight_analysis_gpu,
                        taichi_aot.COLOR_RGB2GRAY,
                        return_gpu=True,
                    )
                )
                _destroy_work_item(ref_weight_analysis_gpu)
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
                fusion_ref_work_chw, fusion_transfer_map = prepare_weightnet_reference_input(
                    ref_weight_input_gpu,
                    work_shape=geometry.weight_shape,
                    session=session,
                )
                if ref_weight_analysis_gpu is not ref_analysis_gpu:
                    _destroy_work_item(ref_weight_analysis_gpu)
                ref_weight_analysis_gpu = None
            print(
                "[GPU Pipeline] Shared RAW analysis: "
                f"full={geometry.full_shape} align={geometry.align_shape} "
                f"weight={geometry.weight_shape}"
            )

            if str(alignment_plan).strip().lower() not in {
                "", "none", "no alignment", "no_alignment", "off"
            }:
                aligner = create_resident_aligner(
                    alignment_plan,
                    ref_analysis_gpu,
                    work_scale=geometry.effective_align_scale,
                    full_shape=geometry.full_shape,
                    alignment_config=alignment_config,
                    noise_score=ref_noise_score,
                )

            # The aligner has derived its persistent features; weight analysis
            # was prepared from its independent natural/linear proxy above.
        _destroy_work_item(ref_analysis_gpu)
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
            for rank_indices, _rank_valid, confidence, _rank_alpha in _iter_multi_patch_rank_maps(
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
                    weight_gpu = _upload_weightnet_confidence(
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
                        _destroy_work_item(weight_gpu)
                    if flow_gpu is not None:
                        _destroy_work_item(flow_gpu)
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
                        support_frame.carrier, half_res=use_half_res
                    )

                    share_support_weight_proxy = (
                        normalized_engine == "fusionet"
                        and geometry.weight_shape == geometry.align_shape
                    )
                    # Build the independent WeightNet/SpatialFusion proxy only when
                    # it differs from the alignment analysis proxy.
                    if normalized_engine in ("fusionet", "spatial_fusion") and not share_support_weight_proxy:
                        support_weight_analysis = prepare_analysis_proxy_gpu(
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
                    support_analysis = prepare_analysis_proxy_gpu(
                        support_linear_full,
                        work_shape=geometry.align_shape,
                        analysis_params=analysis_params,
                        in_place=True,
                        source_is_disposable=True,
                    )
                    if support_linear_full is not support_analysis:
                        _destroy_work_item(support_linear_full)
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
                            _destroy_work_item(alignment_preview)
                            alignment_preview = None

                if normalized_engine not in ("fusionet", "spatial_fusion"):
                    _destroy_work_item(support_analysis)
                    support_analysis = None

                if normalized_engine in ("spatial_fusion", "fusionet"):
                    # SpatialFusion scores linear proxies while alignment uses
                    # analysis-mode AutoEnhance; FusionNet shares analysis mode.
                    if not (
                        normalized_engine == "fusionet"
                        and geometry.weight_shape == geometry.align_shape
                    ):
                        if alignment_preview is not None and alignment_preview is not support_analysis:
                            _destroy_work_item(alignment_preview)
                        alignment_preview = None
                    aligned_weight_proxy, unused_preview = _prepare_raw_aligned_analysis(
                        support_weight_analysis, alignment_preview, transform,
                        align_shape=geometry.weight_shape, warp_analysis=_warp_analysis
                    )
                    # Transfer the already-aligned preview to the weight stage.
                    # A different analysis grid deliberately retains resize->warp.
                    if (
                        unused_preview is not None
                        and unused_preview is not support_weight_analysis
                    ):
                        _destroy_work_item(unused_preview)
                    alignment_preview = None
                    if (
                        support_weight_analysis is not support_analysis
                        and support_weight_analysis is not aligned_weight_proxy
                    ):
                        _destroy_work_item(support_weight_analysis)
                    if normalized_engine == "spatial_fusion":
                        aligned_weight_rgb = aligned_weight_proxy
                    else:
                        aligned_analysis_weight = aligned_weight_proxy
                    if aligned_weight_proxy is not support_analysis:
                        _destroy_work_item(support_analysis)
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
                        _destroy_work_item(aligned_weight_rgb)
                    aligned_weight_rgb = None
                    if support_analysis is not None:
                        _destroy_work_item(support_analysis)
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
                            center_weight = _upload_weightnet_confidence(engine, native_confidence)
                            try:
                                provider.accumulate(support_frame, transform=transform, weight_map=center_weight)
                            finally:
                                _destroy_work_item(center_weight)
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
                                local_weight = _upload_weightnet_confidence(
                                    engine, confidence, confidence_scale=local_rank_weight_scale)
                                try:
                                    provider.accumulate(support_frame, transform=flow_gpu, weight_map=local_weight)
                                finally:
                                    _destroy_work_item(flow_gpu)
                                    _destroy_work_item(local_weight)
                                candidate_alpha_total += rank_alpha
                            alpha = candidate_alpha_total / telemetry.candidate_count
                            deep_analysis_accumulated = True
                        else:
                            weight_gpu = _upload_weightnet_confidence(engine, native_confidence)
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
                        support_proxy_chw = _multi_patch_weightnet_input(
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
                                    weight_gpu = _upload_weightnet_confidence(
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
                                            _destroy_work_item(weight_gpu)
                                        if rank_indices is not None and transform_gpu is not None:
                                            _destroy_work_item(transform_gpu)
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

                            for rank_indices, _rank_valid, confidence, rank_alpha in _iter_multi_patch_rank_maps(
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
                        support_chw = prepare_weightnet_support_input(
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
                            _destroy_work_item(aligned_analysis_weight)
                            aligned_analysis_weight = None
                        del support_chw, weight_chw
                else:
                    alpha = 1.0

                # Release all analysis RGB proxies before CFA accumulation,
                # which is the largest transient allocation of this frame.
                released_ids = set()
                for buffer in (
                    aligned_weight_rgb,
                    support_weight_analysis,
                    support_linear_full,
                ):
                    if buffer is not None and id(buffer) not in released_ids:
                        _destroy_work_item(buffer)
                        released_ids.add(id(buffer))
                aligned_weight_rgb = None
                support_weight_analysis = None
                support_linear_full = None

                # ``accumulate`` warps the CFA carrier and blends it, which is
                # the largest transient allocation of the per-frame loop.  It
                # only needs the mosaic frame, the transform and the weight map,
                # so both full-resolution RGB proxies can go before it runs.
                if support_analysis is not None:
                    _destroy_work_item(support_analysis)
                    support_analysis = None
                if aligned_analysis_weight is not None:
                    _destroy_work_item(aligned_analysis_weight)
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
                released_ids = set()
                for buffer in (
                    aligned_weight_rgb,
                    support_weight_analysis,
                    support_linear_full,
                    support_analysis,
                    aligned_analysis_weight,
                    alignment_preview,
                ):
                    if buffer is not None and id(buffer) not in released_ids:
                        _destroy_work_item(buffer)
                        released_ids.add(id(buffer))
                if weight_gpu is not None and weight_gpu is not spatial_weight_work_gpu:
                    _destroy_work_item(weight_gpu)
                if transform is not None and not isinstance(transform, np.ndarray):
                    _destroy_work_item(transform)

        mean_alpha = alpha_total / max(1, total_supports)
        result = provider.finalize(mean_alpha)
        pipeline_telemetry.emit("complete")
        return _export_result(result.value), result.mean_alpha
    finally:
        if aligner is not None:
            try:
                _destroy_work_item(aligner)
            except Exception:
                pass
        for buffer in (
            ref_proxy_full_gpu,
            ref_analysis_gpu,
            ref_weight_analysis_gpu,
        ):
            _destroy_work_item(buffer)
        if spatial_scratch is not None:
            try:
                _destroy_work_item(spatial_scratch)
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
            _destroy_work_item(provider)
        # A finished burst leaves far more resident memory than the engine's own
        # live/pooled counters describe: measured 1446 MiB -> 934 MiB of process
        # Working set once the warm pool, retired queue and native staging
        # caches are drained.  Nothing else in this call still needs them.
        try:
            from taichi_vision import taichi_aot
            taichi_aot = _managed_api(taichi_aot)

            if hasattr(taichi_aot, "reclaim_resident_buffers"):
                engine.sync()
                taichi_aot.reclaim_resident_buffers("raw_pipeline_burst_complete")
        except Exception as exc:
            print(f"[GPU Pipeline] Post-burst reclaim skipped: {exc}")


# ---------------------------------------------------------------------------
# Main GPU-Resident Pipeline
# ---------------------------------------------------------------------------


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
            from ..fusionet_engine.weightnet_inference import (
                DEFAULT_WEIGHTNET_ONNX,
                load_weightnet_onnx,
            )

            session = load_weightnet_onnx(
                DEFAULT_WEIGHTNET_ONNX,
                runtime=os.environ.get("PIXEL_REFINE_WEIGHTNET_RUNTIME", "taichi_aot"),
                patch_size=int(tile_size),
                input_channels=1,
            )

        return _run_shared_raw_provider_pipeline(
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

    taichi_aot = _managed_api(taichi_aot)
    from taichi_vision.taichi_aot import get_engine
    from ..fusionet_engine.weightnet_inference import (
        DEFAULT_WEIGHTNET_ONNX,
        load_weightnet_onnx,
        infer_single_support_weight_map,
    )

    engine = _managed_api(get_engine())
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
    weightnet_channels = _resolve_weightnet_input_channels(
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

    from .rgb_pipeline.provider import RGBFrameProvider

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
    alignment_mode = (
        "analysis"
        if weight_engine in ("fusionet", "spatial_fusion")
        else ANALYSIS_AUTO_ENHANCE_MODE
    )
    analysis_params = _resolve_engine_analysis_params(
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
            prepare_reference_analysis_and_noise(
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
        weightnet_support_workspace = _WeightNetReadbackWorkspace(
            (work_h, work_w), channels=weightnet_channels
        )
        weightnet_support_workspaces = (weightnet_support_workspace,) + tuple(
            _WeightNetReadbackWorkspace(
                (work_h, work_w), channels=weightnet_channels
            )
            for _ in range(1)
        )
        weightnet_upload_workspace = _WeightNetUploadWorkspace(
            (work_h, work_w), channels=weightnet_channels
        )
        weightnet_upload_workspaces = (weightnet_upload_workspace,) + tuple(
            _WeightNetUploadWorkspace((work_h, work_w), channels=weightnet_channels)
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
        ) = _resolve_spatial_analysis_config(
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
        ref_spatial_linear_gpu = prepare_analysis_proxy_gpu(
            ref_gpu, work_shape=geometry.weight_shape, analysis_params=None
        )
        ref_spatial_gray_source_gpu = taichi_aot.cvtColor(
            ref_spatial_linear_gpu, taichi_aot.COLOR_RGB2GRAY
        )
        if ref_spatial_linear_gpu is not ref_gpu:
            _destroy_work_item(ref_spatial_linear_gpu)
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
        spatial_scratch = _own_component(SpatialScratchCache(), releaser=lambda cache: cache.clear())
    elif weight_engine == "fusionet":
        if (
            ref_analysis_gpu is not None
            and geometry.weight_shape == geometry.align_shape
        ):
            reference_analysis_gpu = ref_analysis_gpu
        else:
            reference_analysis_gpu = prepare_analysis_proxy_gpu(
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
        ref_work_rgb_np, ref_transfer_map = prepare_weightnet_reference_input(
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
            _destroy_work_item(reference_analysis_gpu)

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

    aligner = create_resident_aligner(
        alignment_plan,
        ref_analysis_flow_gpu,
        work_scale=flow_capped_scale,
        full_shape=(target_h, target_w),
        alignment_config=alignment_config,
        noise_score=ref_noise_score,
    )

    if ref_analysis_flow_gpu is not None and ref_analysis_flow_gpu is not ref_gpu:
        _destroy_work_item(ref_analysis_flow_gpu)

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
        from ..patch_process.multi_patch import candidate_flow_from_indices

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
            _destroy_work_item(flow_gpu)

    patch_offsets = None
    if weight_engine == "fusionet" and denoising_mode == "deep_analysis":
        from ..patch_process.multi_patch import (
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
        for rank_indices, _rank_valid, confidence, _rank_alpha in _iter_multi_patch_rank_maps(
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
                weight_gpu = _upload_weightnet_confidence(engine, confidence)
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
                    _destroy_work_item(weight_gpu)
                if candidate_carrier_gpu is not None:
                    _destroy_work_item(candidate_carrier_gpu)
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
                    _destroy_work_item(supp_linear_input)
                    break
                curr_name = Path(image_paths[curr_idx]).name

                with gpu_hardware_lock:
                    if _workers_stopped():
                        _destroy_work_item(supp_linear_input)
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
                        _destroy_work_item(supp_linear_gpu)
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
                        supp_analysis_flow_gpu = prepare_analysis_proxy_gpu(
                            supp_linear_gpu,
                            work_shape=geometry.align_shape,
                            analysis_params=analysis_params,
                            in_place=True,
                        )

                        if weight_engine == "fusionet":
                            if geometry.weight_shape == geometry.align_shape:
                                supp_analysis_sec_gpu = supp_analysis_flow_gpu
                            else:
                                supp_analysis_sec_gpu = prepare_analysis_proxy_gpu(
                                    supp_linear_gpu,
                                    work_shape=geometry.weight_shape,
                                    analysis_params=weight_analysis_params,
                                )
                        elif weight_engine == "spatial_fusion":
                            supp_analysis_sec_gpu = prepare_analysis_proxy_gpu(
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
                        _destroy_work_item(supp_linear_gpu)
                        if supp_analysis_flow_gpu is not supp_linear_gpu:
                            _destroy_work_item(supp_analysis_flow_gpu)
                        if (
                            supp_analysis_sec_gpu is not supp_linear_gpu
                            and supp_analysis_sec_gpu is not supp_analysis_flow_gpu
                        ):
                            _destroy_work_item(supp_analysis_sec_gpu)
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
                        _destroy_work_item(supp_linear_gpu)
                        if supp_analysis_flow_gpu is not supp_linear_gpu:
                            _destroy_work_item(supp_analysis_flow_gpu)
                        if (
                            supp_analysis_sec_gpu is not supp_linear_gpu
                            and supp_analysis_sec_gpu is not supp_analysis_flow_gpu
                        ):
                            _destroy_work_item(supp_analysis_sec_gpu)
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
                        _destroy_work_item(supp_linear_gpu)
                    if (
                        supp_analysis_flow_gpu is not supp_linear_gpu
                        and supp_analysis_flow_gpu is not supp_aligned_sec_gpu
                    ):
                        _destroy_work_item(supp_analysis_flow_gpu)
                    if (
                        supp_analysis_sec_gpu is not supp_linear_gpu
                        and supp_analysis_sec_gpu is not supp_analysis_flow_gpu
                        and supp_analysis_sec_gpu is not supp_aligned_sec_gpu
                    ):
                        _destroy_work_item(supp_analysis_sec_gpu)

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
                            _destroy_work_item(supp_aligned_sec_gpu)
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
                        _destroy_work_item(supp_aligned_sec_gpu)

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
                    _destroy_work_item(supp_aligned_linear_gpu)
                    _destroy_work_item_except(supp_work_item, supp_aligned_linear_gpu)
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
                            supp_work_item = apply_precomputed_transfer_map(
                                supp_work_item, ref_transfer_map
                            )
                        except Exception:
                            pass

                while not _workers_stopped():
                    if pipeline_error is not None:
                        _destroy_work_item(supp_aligned_linear_gpu)
                        _destroy_work_item_except(supp_work_item, supp_aligned_linear_gpu)
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
                        _destroy_work_item(supp_aligned_linear_gpu)
                    _destroy_work_item_except(supp_work_item, supp_aligned_linear_gpu)
                    break

                if (
                    weight_engine == "fusionet"
                    and str(denoising_mode).strip().lower() == "deep_analysis"
                ):
                    from ..patch_process.multi_patch import CandidateTelemetry

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
                        candidate_maps = _iter_deep_support_candidate_maps(
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
                                    weight_work_gpu = _upload_weightnet_confidence(
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
                                    _destroy_work_item(candidate_carrier_gpu)
                                if weight_work_gpu is not None:
                                    _destroy_work_item(weight_work_gpu)
                    finally:
                        with gpu_hardware_lock:
                            _destroy_work_item(supp_aligned_linear_gpu)
                        _destroy_work_item_except(
                            supp_work_item,
                            supp_aligned_linear_gpu,
                        )
                    continue
                if weight_engine == "spatial_fusion":
                    weight_slot = _take_spatial_weight_slot()
                    if weight_slot is None:
                        _destroy_work_item(supp_aligned_linear_gpu)
                        _destroy_work_item_except(supp_work_item, supp_aligned_linear_gpu)
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
                                _destroy_work_item(supp_work_rgb_gpu)
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
                        _destroy_work_item(supp_aligned_linear_gpu)
                        if (
                            hasattr(weight_work_item, "destroy")
                            and not _is_persistent_weight(weight_work_item)
                        ):
                            _destroy_work_item(weight_work_item)
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
                    _destroy_work_item(supp_aligned_linear_gpu)
                    if (
                        hasattr(weight_work_item, "destroy")
                        and not _is_persistent_weight(weight_work_item)
                    ):
                        _destroy_work_item(weight_work_item)
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
                    _destroy_work_item(supp_linear_np)
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
                    _destroy_work_item(supp_linear_gpu)
                    supp_linear_gpu = resized_gpu

                if not needs_analysis:
                    # Average + no alignment can pass the full-resolution carrier
                    # through the existing context-affine queue directly.
                    supp_analysis_flow_gpu = supp_linear_gpu
                    supp_analysis_sec_gpu = supp_linear_gpu
                else:
                    supp_analysis_flow_gpu = prepare_analysis_proxy_gpu(
                        supp_linear_gpu,
                        work_shape=geometry.align_shape,
                        analysis_params=analysis_params,
                        in_place=True,
                    )

                    if weight_engine == "fusionet":
                        if geometry.weight_shape == geometry.align_shape:
                            supp_analysis_sec_gpu = supp_analysis_flow_gpu
                        else:
                            supp_analysis_sec_gpu = prepare_analysis_proxy_gpu(
                                supp_linear_gpu,
                                work_shape=geometry.weight_shape,
                                analysis_params=weight_analysis_params,
                            )
                    elif weight_engine == "spatial_fusion":
                        supp_analysis_sec_gpu = prepare_analysis_proxy_gpu(
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
                    _destroy_work_item(supp_linear_gpu)
                if (
                    supp_analysis_flow_gpu is not supp_linear_gpu
                    and supp_analysis_flow_gpu is not supp_aligned_sec_gpu
                ):
                    _destroy_work_item(supp_analysis_flow_gpu)
                if (
                    supp_analysis_sec_gpu is not supp_linear_gpu
                    and supp_analysis_sec_gpu is not supp_analysis_flow_gpu
                    and supp_analysis_sec_gpu is not supp_aligned_sec_gpu
                ):
                    _destroy_work_item(supp_analysis_sec_gpu)

                if (
                    weight_engine == "fusionet"
                    and str(denoising_mode).strip().lower() == "deep_analysis"
                ):
                    from ..patch_process.multi_patch import CandidateTelemetry

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
                    support_proxy_chw = _multi_patch_weightnet_input(
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
                            _iter_deep_support_candidate_maps(
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
                                weight_gpu = _upload_weightnet_confidence(
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
                                    _destroy_work_item(candidate_carrier_gpu)
                                if weight_gpu is not None:
                                    _destroy_work_item(weight_gpu)
                        processed_count += 1
                    finally:
                        released_ids = set()
                        for buffer in (supp_aligned_sec_gpu, supp_aligned_linear_gpu):
                            if buffer is not None and id(buffer) not in released_ids:
                                _destroy_work_item(buffer)
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
                        _destroy_work_item(supp_aligned_sec_gpu)
                    weight_work_item = weight_work_2d_gpu
                    alpha_mean = 1.0
                elif weight_engine == "average":
                    if (
                        supp_aligned_sec_gpu is not None
                        and supp_aligned_sec_gpu is not supp_aligned_linear_gpu
                    ):
                        _destroy_work_item(supp_aligned_sec_gpu)
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
                    supp_work_rgb_np = prepare_weightnet_support_input(
                        weightnet_input_gpu,
                        ref_transfer_map,
                        workspace=weightnet_support_workspace,
                    )
                    _destroy_work_item(supp_aligned_sec_gpu)
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
                        _upload_weightnet_confidence(engine, weight_work_np)
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

                _destroy_work_item(supp_aligned_linear_gpu)
                if not _is_persistent_weight(weight_work_gpu):
                    _destroy_work_item(weight_work_gpu)
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
            return _export_result(ref_out), 1.0

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
                                _destroy_work_item(candidate_carrier_gpu)
                            _destroy_work_item(weight_work_gpu)
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
                                _destroy_work_item(candidate_carrier_gpu)
                            _destroy_work_item(weight_work_gpu)
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
                        _destroy_work_item(supp_aligned_linear_gpu)
                        if _is_persistent_weight(weight_work_item):
                            _release_spatial_weight_slot(weight_work_item)
                        elif hasattr(weight_work_item, "destroy"):
                            _destroy_work_item(weight_work_item)
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

                    _destroy_work_item(supp_aligned_linear_gpu)
                    if not _is_persistent_weight(weight_work_gpu):
                        _destroy_work_item(weight_work_gpu)
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
                                        _destroy_work_item(el)
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
        _destroy_work_item(weight_sum_gpu)
    else:
        _final_linear_gpu = mean_division_vec3_weight_taichi(
            sum_img=sum_img_gpu,
            sum_weight=weight_sum_gpu,
            ref_img=ref_gpu,
            dst=sum_img_gpu,
        )
        _destroy_work_item(weight_sum_gpu)

    # The resident RGB path intentionally aliases the reference as the
    # accumulator.  With in-place normalization, destroying ref_gpu here
    # would also destroy the final destination before its readback.  Only
    # release it when it is a distinct allocation.
    if getattr(ref_gpu, "handle", None) != getattr(
        _final_linear_gpu, "handle", None
    ):
        _destroy_work_item(ref_gpu)

    result_hwc = np.ascontiguousarray(_final_linear_gpu.to_numpy(), dtype=np.float32)
    _destroy_work_item(_final_linear_gpu)

    # Synchronize the retired handles, but retain the engine pools: subsequent
    # bursts can acquire same-shape buffers without another VRAM allocation.
    try:
        engine.sync()
    except Exception:
        pass

    mean_alpha = float(alpha_total / max(1, total_supp))
    _destroy_work_item(rgb_provider)
    print(
        f"[GPU Pipeline] Complete: shape={result_hwc.shape} "
        f"mean_alpha={mean_alpha:.4f} (reusable VRAM pools retained)"
    )
    pipeline_telemetry.emit("complete")

    return _export_result(result_hwc), mean_alpha


# Canonical alias
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
