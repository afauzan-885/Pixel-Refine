"""
GPU-Resident Zero-Copy Pipeline for FusionNet.

Minimizes CPU↔GPU data transfers by keeping all full-resolution data in VRAM
throughout the align → weight → fuse lifecycle. The only unavoidable CPU
touches are:

    1. ONNX WeightNet inference at work-resolution (~2 MB/frame vs ~50 MB full-res)
    2. auto_enhance histogram analysis (once on reference, tiny)
    3. Final result download (one frame)
    4. Per-frame blend bridge (accumulator multiply-add — no dedicated AOT kernel yet)

Architecture:
    ┌─────────────────────────────────────────────────────────┐
    │  Load frames directly to GPU VRAM (demosaic/imread)    │
    └────────────────────┬────────────────────────────────────┘
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │  Reference: build pyramid on GPU (taichi_bridge)       │
    │  Accumulator: sum_img, weight_sum — VRAM-resident      │
    └────────────────────┬────────────────────────────────────┘
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │  Per support frame (all in VRAM until ONNX bridge):    │
    │    a. GPU alignment → aligned frame stays in VRAM      │
    │    b. Downsample to work-res on GPU (resize)           │
    │    c. Download enhanced RGB work-res for ONNX          │
    │    d. Upload weight map back to GPU                     │
    │    e. Upsample weight to full-res on GPU               │
    │    f. Blend: multiply-add on CPU bridge                 │
    └────────────────────┬────────────────────────────────────┘
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │  Download final fused result (one frame)                │
    └─────────────────────────────────────────────────────────┘
"""

import gc
import os
import queue
import sys
import threading
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


def apply_clahe_16bit_reference(
    rgb_chw: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8),
    backend: str = "auto",
) -> Tuple[np.ndarray, np.ndarray]:
    """Apply CLAHE to Reference Luminance and precompute 2D transfer ratio map.
    Uses Taichi Vision GPU-accelerated CLAHE primarily, falling back to OpenCV
    if needed.  ``backend='opencv'`` forces the OpenCV implementation while
    retaining the same cached transfer-map contract.

    Returns:
        enhanced_chw: np.ndarray [1|3, H, W] float32 enhanced reference frame.
        transfer_map: np.ndarray [H, W] float32 precomputed luminance boost ratio map.
    """
    img = np.ascontiguousarray(rgb_chw, dtype=np.float32)
    if img.ndim != 3 or img.shape[0] not in (1, 3):
        raise ValueError(f"WeightNet reference must be CHW with 1 or 3 channels, got {img.shape}")
    lum = (
        img[0]
        if img.shape[0] == 1
        else 0.2126 * img[0] + 0.7152 * img[1] + 0.0722 * img[2]
    )

    lum_clahe = None
    force_opencv = str(backend).strip().lower() == "opencv"
    if not force_opencv:
        try:
            from taichi_vision import taichi_aot
            taichi_aot = _managed_api(taichi_aot)

            res = taichi_aot.clahe(
                lum,
                clip_limit=float(clip_limit),
                tile_grid_size=tile_grid_size,
            )
            if hasattr(res, "to_numpy"):
                res = res.to_numpy()
            lum_clahe = np.asarray(res, dtype=np.float32)
            if lum_clahe.size > 0 and float(np.max(lum_clahe)) > 1.5:
                lum_clahe = lum_clahe / 255.0
        except Exception:
            pass

    if lum_clahe is None:
        try:
            import cv2

            # Discretize to 16-bit uint16 [0..65535]
            lum_u16 = np.clip(lum * 65535.0 + 0.5, 0.0, 65535.0).astype(np.uint16)
            clahe = cv2.createCLAHE(clipLimit=float(clip_limit), tileGridSize=tile_grid_size)
            lum_clahe_u16 = clahe.apply(lum_u16)
            lum_clahe = lum_clahe_u16.astype(np.float32) / 65535.0
        except Exception:
            lum_clahe = lum

    # Transfer ratio map: ratio(y, x) = Y'_clahe / Y
    transfer_map = ((lum_clahe + 1e-6) / (lum + 1e-6)).astype(np.float32)
    # ``img`` is the one CHW staging array that will be passed to ONNX.  Keep
    # it as the enhanced reference instead of allocating a second full RGB
    # work image solely for the elementwise transfer-map application.
    np.multiply(img, transfer_map[None, :, :], out=img)
    np.clip(img, 0.0, 1.0, out=img)
    return img, transfer_map


def apply_precomputed_transfer_map(
    rgb_chw: np.ndarray,
    transfer_map: np.ndarray,
) -> np.ndarray:
    """Apply the one reference CLAHE map in-place to one ONNX work buffer."""
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
) -> tuple[np.ndarray, np.ndarray]:
    """Build the canonical WeightNet reference tensor and CLAHE cache."""

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
    return apply_clahe_16bit_reference(
        reference_chw,
        clip_limit=clip_limit,
        tile_grid_size=tile_grid_size,
    )


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

    def __init__(self, shape: tuple[int, int]):
        height, width = (max(1, int(shape[0])), max(1, int(shape[1])))
        self.hwc = np.empty((height, width, 3), dtype=np.float32)
        _own_component(self)

    def close(self):
        self.hwc = None

    def stage(self, weight_chw: np.ndarray) -> np.ndarray:
        array = np.asarray(weight_chw, dtype=np.float32)
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

    def _resident_flow_view(self):
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
        owner = getattr(self, "_resident_flow_buffer", None)
        self._resident_flow_buffer = None
        if owner is not None and hasattr(owner, "destroy"):
            _destroy_work_item(owner)


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
        smooth = self.config.get("smooth", None)
        if smooth is not None:
            dense_mode = "smooth" if bool(smooth) else "blocky_clamped"
            overlap = 0.50 if bool(smooth) else 0.0
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
            warped_primary = taichi_aot.remap_with_flow(
                supp_linear_gpu,
                flow_gpu,
                self.full_h,
                self.full_w,
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
        smooth = self.config.get("smooth", None)
        if smooth is not None:
            dense_mode = "smooth" if bool(smooth) else "blocky_clamped"
            overlap = 0.50 if bool(smooth) else 0.0
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
            warped_primary = taichi_aot.remap_with_flow(
                supp_linear_gpu,
                flow_gpu,
                self.full_h,
                self.full_w,
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
                resident_algorithm_allowed = self.feature_type == "ofb" or (
                    self.feature_type == "akaze"
                    and os.environ.get("TAICHI_FEATURE_RESIDENT_AKAZE", "0") == "1"
                )
                self._feature_resident_matches = (
                    resident_algorithm_allowed
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
        if (self.work_h, self.work_w) != (self.target_h, self.target_w):
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
                        H_matrix = scale_homography(
                            H_candidate,
                            source_shape=(self.work_h, self.work_w),
                            destination_shape=(self.target_h, self.target_w),
                        )
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
                # OFB consumes only the refined homography.  Its inlier mask
                # is not used by the established OFB route, so keep that
                # mask resident and release it without forcing a host
                # readback.  AKAZE still needs the mask for its defensive
                # geometry validation and therefore keeps the host result.
                homography_mask_on_gpu = self.feature_type == "ofb"
                H_candidate, inlier_mask = taichi_aot.find_homography(
                    pts_supp,
                    pts_ref,
                    method="RANSAC",
                    ransacReprojThreshold=reproj_threshold,
                    n_hypotheses=ransac_hypotheses,
                    max_iters=ransac_iters,
                    return_gpu=homography_mask_on_gpu,
                )
                if self.feature_type == "akaze":
                    # AKAZE's binary matches are more vulnerable to repeated
                    # texture producing a plausible-looking but wrong H.
                    # Keep the established OFB route unchanged while making
                    # the AKAZE path fail closed (or use robust translation).
                    H_matrix = self._validate_homography(
                        H_candidate,
                        pts_supp,
                        pts_ref,
                        inlier_mask,
                        width=self.target_w,
                        height=self.target_h,
                        reproj_threshold=reproj_threshold,
                    )
                else:
                    H_matrix = H_candidate
                    if isinstance(inlier_mask, TaichiGPUBuffer):
                        # ``find_homography(return_gpu=True)`` leaves the
                        # final inlier-mask dispatch asynchronous.  Establish
                        # the same lifecycle barrier that the old host
                        # readback provided before returning its buffer to
                        # the pool; otherwise the next warp can observe a
                        # recycled allocation on graphics backends.
                        get_engine().sync()
                        _destroy_work_item(inlier_mask)

        if H_matrix is not None:
            # Warp primary linear frame directly on GPU
            warped_primary = taichi_aot.warp_perspective(
                supp_linear_gpu,
                H_matrix,
                (self.target_w, self.target_h),
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
            warped_primary = taichi_aot.remap_with_flow(
                supp_linear_gpu, flow_gpu, self.full_h, self.full_w, return_gpu=True
            )
            warped_secondary = None
            if secondary_frame_to_warp is not None:
                sec_h, sec_w = (int(v) for v in secondary_frame_to_warp.shape[:2])
                warped_secondary = taichi_aot.remap_with_flow(
                    secondary_frame_to_warp, flow_gpu, sec_h, sec_w, return_gpu=True
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
    plan_clean = str(alignment_plan or "").strip().lower()
    if plan_clean in ("no alignment", "none", "off", ""):
        print("[GPU Pipeline] Aligner: No Alignment (Bypass)")
        return NoAlignmentGPUAligner(ref_analysis_gpu)
    elif plan_clean in ("ofb", "orb", "akaze", "feature matching"):
        print(f"[GPU Pipeline] Aligner: Feature Matching ({plan_clean.upper()})")
        return FeatureMatchingGPUAligner(
            ref_analysis_gpu,
            feature_type=plan_clean,
            work_scale=work_scale,
            full_shape=full_shape,
            feature_config=alignment_config,
        )
    elif plan_clean in (
        "block matching", "block_matching", "block matching gpu", "blockmatching", "block align", "bm"
    ):
        print("[GPU Pipeline] Aligner: Block Matching GPU")
        return BlockMatchingResidentAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            alignment_config=alignment_config,
        )
    elif "lucas" in plan_clean or "lk" in plan_clean:
        print("[GPU Pipeline] Aligner: Lucas Kanade GPU")
        return LucasKanadeResidentAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            alignment_config=alignment_config,
        )
    elif "farneback" in plan_clean:
        return FarnebackResidentAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            alignment_config=alignment_config,
        )
    elif plan_clean in ("sift", "lightglue", "light glue"):
        raise ValueError(
            f"Unsupported resident feature aligner '{alignment_plan}'. "
            "Use OFB/ORB or AKAZE; SIFT and LightGlue were removed from the native path."
        )
    else:
        print(f"[GPU Pipeline] Aligner: Dense Optical Flow Adaptive Multi-Tile ({plan_clean})")
        from ..fusionet_engine.flownet_inference import AOTOpticalFlowAligner

        smooth = True
        if alignment_config:
            if "smooth" in alignment_config:
                smooth = bool(alignment_config["smooth"])

        return AOTOpticalFlowAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            tile_size=32,
            noise_score=noise_score,
            smooth=smooth,
            adaptive=True,
        )


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

    Uses accumulate_spatial_merging_taichi from SpatialFusion which
    auto-dispatches to the vec3 kernel when given a 3D weight map.

    The vec3 kernel performs per-channel bilinear upsample + multiply + accumulate
    entirely on GPU on-the-fly — saving 144 MB VRAM per frame.
    """
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi import (
        accumulate_spatial_merging_taichi,
    )

    accumulate_spatial_merging_taichi(
        current_image_full=supp_aligned_gpu.view_as_vector(False),
        weight_map_work=weight_work_gpu.view_as_vector(False),
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
    weightnet_input_channels: Optional[int] = None,
    stop_event=None,
    progress_callback: Optional[Callable[..., None]] = None,
    auto_params: Optional[dict] = None,
    prefetch_depth: Optional[int] = None,
    _runtime: Optional[PipelineRuntime] = None,
    **_unused,
) -> Tuple[Any, float]:
    """Run RAW CFA accumulation through the shared resident frame loop.

    The resident executor owns analysis, alignment, weight generation, queue
    lifetime, and cleanup.  ``RawNativeProvider`` owns only CFA carrier I/O
    and phase-safe accumulation/finalization.
    """

    normalized_engine = str(weight_engine).strip().lower()
    if normalized_engine not in ("average", "spatial_fusion", "fusionet"):
        raise NotImplementedError(
            "RAW Native supports Average, SpatialFusion, and FusionNet."
        )
    if len(image_paths) < 2:
        raise ValueError("RAW Native fusion requires at least two DNG frames")

    from .raw_pipeline.provider import RawNativeProvider
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
            stop_event=stop_event,
            progress_callback=progress_callback,
        )
    buffer_session = runtime.ensure_session(engine)
    engine = buffer_session.managed_api(engine)
    taichi_aot = buffer_session.managed_api(taichi_aot)
    weightnet_channels = _resolve_weightnet_input_channels(
        session, weightnet_input_channels
    )
    provider = buffer_session.own(RawNativeProvider(image_paths, weight_engine=normalized_engine))
    pipeline_telemetry = PipelineTelemetry(engine, enabled=telemetry)
    aligner = None
    ref_proxy_full_gpu = None
    ref_analysis_gpu = None
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
    analysis_params = auto_params or {}
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
        if normalized_engine == "fusionet":
            weightnet_support_workspace = _WeightNetReadbackWorkspace(
                geometry.weight_shape, channels=weightnet_channels
            )
            weightnet_upload_workspace = _WeightNetUploadWorkspace(
                geometry.weight_shape
            )
        ref_noise_score = None
        if needs_analysis:
            from .raw_pipeline.provider import _demosaic_carrier_gpu

            ref_proxy_full_gpu = _demosaic_carrier_gpu(ref_frame.carrier)
            env_override = os.environ.get("PIXEL_REFINE_ANALYSIS_ENHANCE")
            if env_override is not None:
                analysis_enhance = env_override.strip().lower() not in ("0", "false", "off", "no")
            analysis_params = auto_params or None
            if analysis_enhance:
                if not analysis_params:
                    analysis_params = analyze_auto_enhance_on_gpu(
                        ref_proxy_full_gpu, mode="analysis"
                    )
            else:
                analysis_params = None

            # Estimasi noise murni dari versi RAW yang belum di-autoenhance sama sekali
            ref_noise_score, ghost_penalty = resolve_noise_adaptive_penalty(
                ref_proxy_full_gpu,
                ghost_penalty=ghost_penalty,
                ghost_penalty_min=ghost_penalty_min,
            )

            # Noise analysis stays on the unenhanced reference. Weight analysis
            # uses the disposable AutoEnhanced proxy created below.
            ref_spatial_gray_gpu = None
            if normalized_engine == "spatial_fusion":
                cfg = dict(spatial_config or {})
                tile = max(4, int(cfg.get("similarity_spatial_tile_size", 12)))
                overlap_value = float(
                    cfg.get("similarity_spatial_overlap_percent", overlap)
                )
                motion = float(
                    cfg.get("similarity_spatial_motion_sensitivity", 150.0)
                )
                noise_offset = float(
                    cfg.get("similarity_spatial_noise_mad_offset_factor", 0.15)
                )
                noise_sigma = float(
                    cfg.get("noise_sigma")
                    or (ref_noise_score if ref_noise_score is not None else 0.025)
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
            # Kalkulasi alignment KHUSUS menggunakan proxy AutoEnhance analisis
            ref_analysis_gpu = prepare_analysis_proxy_gpu(
                ref_proxy_full_gpu,
                work_shape=geometry.align_shape,
                analysis_params=analysis_params,
                in_place=True,
                source_is_disposable=True,
            )
            if ref_proxy_full_gpu is not ref_analysis_gpu:
                _destroy_work_item(ref_proxy_full_gpu)
            ref_proxy_full_gpu = None
            if normalized_engine == "spatial_fusion":
                ref_analysis_gray_gpu = taichi_aot.cvtColor(
                    ref_analysis_gpu, taichi_aot.COLOR_RGB2GRAY
                )
                if tuple(ref_analysis_gray_gpu.shape[:2]) != geometry.weight_shape:
                    ref_spatial_gray_gpu = buffer_session.own(
                        taichi_aot.resize(
                            ref_analysis_gray_gpu,
                            (geometry.weight_shape[1], geometry.weight_shape[0]),
                            interpolation=taichi_aot.INTER_AREA,
                            return_gpu=True,
                        )
                    )
                    _destroy_work_item(ref_analysis_gray_gpu)
                else:
                    ref_spatial_gray_gpu = buffer_session.own(ref_analysis_gray_gpu)
                print(
                    "[RAW Native] SpatialFusion weight analysis: "
                    "reference AutoEnhance params -> in-place analysis proxy -> "
                    "reused grayscale scratch; CFA carrier unchanged"
                )
            if normalized_engine == "fusionet":
                if tuple(ref_analysis_gpu.shape[:2]) != geometry.weight_shape:
                    ref_weight_analysis_gpu = taichi_aot.resize(
                        ref_analysis_gpu,
                        (geometry.weight_shape[1], geometry.weight_shape[0]),
                        interpolation=taichi_aot.INTER_AREA,
                        return_gpu=True,
                    )
                else:
                    ref_weight_analysis_gpu = ref_analysis_gpu
                if weightnet_channels == 1:
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
                )
                if ref_weight_analysis_gpu is not ref_analysis_gpu:
                    _destroy_work_item(ref_weight_analysis_gpu)
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

        # All consumers of the reference RGB proxy are done: every resident
        # aligner derives its own gray/pyramid buffers inside its constructor.
        _destroy_work_item(ref_analysis_gpu)
        ref_analysis_gpu = None

        provider.bind_accumulator(engine, ref_frame)
        pipeline_telemetry.emit("reference_loaded")
        total_supports = len(image_paths) - 1
        alpha_total = 0.0
        for ordinal, support_frame in runtime.iter_supports(
            range(1, len(image_paths)),
            provider.load_support,
            raise_on_cancel=True,
        ):
            if _cancelled():
                raise RuntimeError("RAW Native processing cancelled")
            support_linear_full = None
            support_analysis = None
            alignment_preview = None
            aligned_weight_rgb = None
            aligned_analysis_weight = None
            transform = None
            weight_gpu = None
            try:
                if needs_analysis:
                    from .raw_pipeline.provider import _demosaic_carrier_gpu

                    support_linear_full = _demosaic_carrier_gpu(support_frame.carrier)

                    # 1. Alignment: proxy AutoEnhance analisis khusus alignment
                    if normalized_engine in ("fusionet", "spatial_fusion"):
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
                    else:
                        support_analysis = prepare_analysis_proxy_gpu(
                            support_linear_full,
                            work_shape=geometry.align_shape,
                            analysis_params=analysis_params,
                            in_place=True,
                        )
                        if support_linear_full is not support_analysis:
                            _destroy_work_item(support_linear_full)
                        support_linear_full = None

                    if aligner is not None:
                        if hasattr(aligner, "take_last_flow"):
                            alignment_preview = aligner.align_frame(
                                support_analysis,
                                analysis_frame_gpu=support_analysis,
                                stop_event=stop_event,
                                return_gpu=True,
                                keep_flow=True,
                            )
                            transform = aligner.take_last_flow()
                        else:
                            alignment_preview, _ignored, transform = aligner.align_frame(
                                support_analysis,
                                analysis_frame_gpu=support_analysis,
                                stop_event=stop_event,
                                return_gpu=True,
                                return_transform=True,
                            )
                        if (
                            alignment_preview is not None
                            and alignment_preview is not support_analysis
                        ):
                            _destroy_work_item(alignment_preview)
                        alignment_preview = None

                if normalized_engine not in ("fusionet", "spatial_fusion"):
                    _destroy_work_item(support_analysis)
                    support_analysis = None

                # Both weight engines score the same AutoEnhanced analysis proxy;
                # the original CFA carrier remains untouched for accumulation.
                if normalized_engine == "spatial_fusion":
                    support_weight_analysis = support_analysis
                    if tuple(support_analysis.shape[:2]) != geometry.weight_shape:
                        support_weight_analysis = taichi_aot.resize(
                            support_analysis,
                            (geometry.weight_shape[1], geometry.weight_shape[0]),
                            interpolation=taichi_aot.INTER_AREA,
                            return_gpu=True,
                        )
                    aligned_weight_rgb = _warp_analysis(
                        support_weight_analysis, transform, geometry.weight_shape
                    )
                    if (
                        support_weight_analysis is not support_analysis
                        and support_weight_analysis is not aligned_weight_rgb
                    ):
                        _destroy_work_item(support_weight_analysis)
                    if (
                        support_linear_full is not None
                        and support_linear_full is not support_analysis
                    ):
                        _destroy_work_item(support_linear_full)
                    support_linear_full = None
                    if support_analysis is None:
                        raise RuntimeError("SpatialFusion analysis proxy was not prepared")
                elif normalized_engine == "fusionet":
                    if tuple(support_analysis.shape[:2]) != geometry.weight_shape:
                        support_weight_analysis = taichi_aot.resize(
                            support_analysis,
                            (geometry.weight_shape[1], geometry.weight_shape[0]),
                            interpolation=taichi_aot.INTER_AREA,
                            return_gpu=True,
                        )
                    else:
                        support_weight_analysis = support_analysis
                    aligned_analysis_weight = _warp_analysis(
                        support_weight_analysis, transform, geometry.weight_shape
                    )
                    if (
                        support_weight_analysis is not support_analysis
                        and support_weight_analysis is not aligned_analysis_weight
                    ):
                        _destroy_work_item(support_weight_analysis)
                    if aligned_analysis_weight is not support_analysis:
                        _destroy_work_item(support_analysis)
                        support_analysis = None
    
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
                    )
                    weight_hwc = (
                        weightnet_upload_workspace.stage(weight_chw)
                        if weightnet_upload_workspace is not None
                        else np.ascontiguousarray(
                            np.transpose(weight_chw, (1, 2, 0)),
                            dtype=np.float32,
                        )
                    )
                    weight_gpu = engine.upload(weight_hwc, is_vector=False)
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
                    support_linear_full,
                ):
                    if buffer is not None and id(buffer) not in released_ids:
                        _destroy_work_item(buffer)
                        released_ids.add(id(buffer))
                aligned_weight_rgb = None
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

                provider.accumulate(support_frame, transform=transform, weight_map=weight_gpu)
                alpha_total += float(alpha)
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
                taichi_aot.reclaim_resident_buffers("raw_native_burst_complete")
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
    telemetry: Optional[bool] = None,
    weight_engine: str = "fusionet",
    alignment_plan: str = "optical_flow",
    alignment_config: Optional[dict] = None,
    spatial_config: Optional[dict] = None,
    analysis_enhance: bool = True,
    work_scale: float = 0.50,
    flownet_work_scale: Optional[float] = None,
    weightnet_work_scale: Optional[float] = None,
    max_work_dimension: Optional[int] = 2048,
    tile_size: int = 512,
    weightnet_input_channels: Optional[int] = None,
    overlap: float = 0.30,
    ghost_penalty: float = 1.0,
    ghost_penalty_min: Optional[float] = None,
    ghost_cutoff: float = 0.05,
    chroma_sensitivity: float = 6.0,
    is_raw: bool = False,
    storage_mode: str = "direct",
    alignment_only: bool = False,
    batch_queue: Optional[int] = None,
    prefetch_depth: Optional[int] = None,
    batch_plan: Optional[Sequence[Tuple[int, int]]] = None,
    auto_params: Optional[dict] = None,
    stop_event: Optional[threading.Event] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    raw_native: bool = False,
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
        is_raw: Whether images are RAW/DNG.
        storage_mode: "direct" (RAM/VRAM stream).
        alignment_only: If True, executes pure alignment without blending.
        batch_queue: Deprecated compatibility argument retained for existing
            callers. The saved Performance-page setting is authoritative.
        prefetch_depth: Optional per-call override for the host support queue
            depth (0 disables prefetch; 1-4 bounds decoded frames in RAM).
        batch_plan: Optional comparison-frame ranges from MFDenoiser. The
            reference frame (index 0) remains resident for the whole call.
        auto_params: Pre-computed auto_enhance params (analyzed on first frame if None).
        stop_event: Cancellation signal.
        progress_callback: Progress reporting callback.

    Returns:
        (result_fp32, mean_alpha): Fused float32 RGB [H, W, 3] and mean alpha.
    """
    if source_mode is None:
        source_mode = "raw_native" if raw_native else ("raw_rgb" if is_raw else "rgb")
    source_mode = str(source_mode).strip().lower()
    if source_mode not in {"rgb", "raw_rgb", "raw_native", "video_rgb"}:
        raise ValueError(f"Unsupported resident source_mode: {source_mode!r}")
    runtime = current_pipeline_runtime()
    if runtime is None:
        runtime = PipelineRuntime(
            prefetch_depth=resolve_prefetch_depth(prefetch_depth),
            stop_event=stop_event,
            progress_callback=progress_callback,
        )
    raw_native = source_mode == "raw_native"
    is_raw = source_mode in {"raw_rgb", "raw_native"}

    if raw_native:
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
                runtime="dml",
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
            weightnet_input_channels=weightnet_input_channels,
            analysis_enhance=analysis_enhance,
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
            runtime="dml",
            patch_size=tile_size,
            input_channels=1,
        )
    weightnet_channels = _resolve_weightnet_input_channels(
        session, weightnet_input_channels
    )

    # ------------------------------------------------------------------
    # PHASE 1: Load reference frame directly to GPU
    # ------------------------------------------------------------------
    RAW_EXTS = {".dng", ".cr2", ".cr3", ".nef", ".arw", ".orf", ".rw2", ".pef", ".raf"}
    first_ext = os.path.splitext(str(image_paths[0]))[1].lower() if image_paths else ""
    if not is_raw and first_ext in RAW_EXTS:
        is_raw = True

    if progress_callback:
        progress_callback(
            PROGRESS_LOAD_IMAGES_MIN,
            ui="Memuat gambar referensi...",
            console=f"Memuat gambar referensi ke GPU VRAM ({len(image_paths)} frame)...",
        )

    from .rgb_pipeline.provider import RGBFrameProvider

    rgb_provider = buffer_session.own(RGBFrameProvider(image_paths, is_raw=is_raw))
    ref_gpu = buffer_session.own(rgb_provider.load_reference_gpu())
    target_h, target_w = ref_gpu.shape[:2]

    print(
        f"[GPU Pipeline] Reference loaded to VRAM: "
        f"shape=({target_h}, {target_w}, 3) dtype={ref_gpu.dtype} "
        f"size={ref_gpu.nbytes / (1024*1024):.1f} MB (engine={weight_engine})"
    )
    pipeline_telemetry.emit("reference_loaded")
    # ------------------------------------------------------------------
    # PHASE 2: Tier 1 Analysis AutoEnhance for Feature Extraction
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

    # AutoEnhance analysis on reference frame:
    # - Versi 1 (Analysis / High-Key): For Alignment & ONNX WeightNet (Used for BOTH RAW & Non-RAW)
    # Parameters are computed once from the reference and reused for every
    # support frame.  The linear fusion buffers themselves remain untouched.
    env_override = os.environ.get("PIXEL_REFINE_ANALYSIS_ENHANCE")
    if env_override is not None:
        analysis_enhance = env_override.strip().lower() not in ("0", "false", "off", "no")

    analysis_params = auto_params or None
    if needs_analysis and analysis_enhance:
        if not analysis_params:
            analysis_params = analyze_auto_enhance_on_gpu(ref_gpu, mode="analysis")
        print(
            f"[GPU Pipeline] AutoEnhance (analysis): Gain={analysis_params['gain']:.2f}x "
            "(reference parameters reused for alignment/WeightNet analysis)"
        )
    else:
        analysis_params = None
        reason = "disabled via analysis_enhance=False" if not analysis_enhance else "average + no alignment"
        print(f"[GPU Pipeline] AutoEnhance (analysis): skipped ({reason})")

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

    # Create the canonical high-contrast analysis proxy through the shared
    # helper.  RAW Native uses this same function for its demosaic-only proxy;
    # the carrier itself remains linear and untouched.
    ref_analysis_flow_gpu = None
    ref_analysis_gpu = None
    ref_noise_score = None
    if needs_analysis:
        ref_analysis_flow_gpu = prepare_analysis_proxy_gpu(
            ref_gpu,
            work_shape=geometry.align_shape,
            analysis_params=analysis_params,
            in_place=(
                weight_engine in ("fusionet", "spatial_fusion")
                and analysis_params is not None
            ),
        )

        ref_analysis_gpu = ref_analysis_flow_gpu
        analysis_context.reference_proxy = ref_analysis_gpu
        analysis_context.alignment_reference = ref_analysis_gpu

        # Estimasi noise murni dari versi RAW/linear yang belum di-autoenhance sama sekali.
        ref_noise_score, ghost_penalty = resolve_noise_adaptive_penalty(
            ref_gpu,
            ghost_penalty=ghost_penalty,
            ghost_penalty_min=ghost_penalty_min,
        )
        analysis_context.noise_score = ref_noise_score
        if ref_noise_score is not None:
            print(
                f"[GPU Pipeline] Reference noise estimate (Taichi Vision): "
                f"score={ref_noise_score:.6f} source=raw_linear_unenhanced"
            )

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
    if weight_engine == "fusionet":
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
            (work_h, work_w)
        )
        weightnet_upload_workspaces = (weightnet_upload_workspace,) + tuple(
            _WeightNetUploadWorkspace((work_h, work_w)) for _ in range(1)
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

        cfg = spatial_config or {}
        st_size = int(
            cfg.get(
                "similarity_spatial_tile_size",
                tile_size,
            )
        )
        st_size = max(8, min(st_size, min(work_h, work_w)))
        spatial_tile_h = st_size
        spatial_tile_w = st_size
        spatial_overlap = float(cfg.get("similarity_spatial_overlap_percent", overlap))
        spatial_motion_sens = float(
            cfg.get(
                "similarity_spatial_motion_sensitivity",
                cfg.get("motion_sensitivity", cfg.get("motion_sensivity", 150.0)),
            )
        )
        spatial_noise_offset = float(
            cfg.get(
                "similarity_spatial_noise_mad_offset_factor",
                cfg.get(
                    "noise_offset_factor",
                    cfg.get("noise_mad_offset_factor", cfg.get("noise_offset", 0.15)),
                ),
            )
        )

        # SpatialFusion scores the same AutoEnhanced analysis proxy as
        # FusionNet, reduced directly to its persistent grayscale reference.
        print(
            "[GPU Pipeline] SpatialFusion weight analysis: reference AutoEnhance "
            "params -> in-place analysis proxy -> reused grayscale scratch; "
            "linear fusion carrier unchanged"
        )
        ref_spatial_gray_source_gpu = taichi_aot.cvtColor(
            ref_analysis_flow_gpu, taichi_aot.COLOR_RGB2GRAY
        )
        if tuple(ref_spatial_gray_source_gpu.shape[:2]) != geometry.weight_shape:
            ref_spatial_gray_gpu = taichi_aot.resize(
                ref_spatial_gray_source_gpu,
                (weight_work_w, weight_work_h),
                interpolation=taichi_aot.INTER_AREA,
                return_gpu=True,
            )
            _destroy_work_item(ref_spatial_gray_source_gpu)
        else:
            ref_spatial_gray_gpu = ref_spatial_gray_source_gpu

        # Estimasi noise fisik sensor murni dari versi RAW yang belum di-autoenhance
        if ref_noise_score is not None:
            auto_noise_sigma = float(np.clip(ref_noise_score, 1e-4, 0.99999))
            spatial_sigma_mode = "raw_linear_score"
        else:
            auto_noise_sigma = 0.025
            spatial_sigma_mode = "fallback"

        from taichi_vision.taichi_algorithm.spatial_fusion import auto_motion_sensitivity

        explicit_noise_sigma = cfg.get("similarity_spatial_noise_sigma", cfg.get("noise_sigma"))
        if explicit_noise_sigma is not None and float(explicit_noise_sigma) > 0.0:
            spatial_noise_sigma = float(explicit_noise_sigma)
            spatial_sigma_mode = "explicit_ui"
        else:
            spatial_noise_sigma = auto_noise_sigma

        # Noise-aware motion sensitivity modulation
        spatial_motion_sens = auto_motion_sensitivity(
            is_raw=is_raw,
            base=spatial_motion_sens,
            noise_sigma=spatial_noise_sigma,
        )

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
        # Reuse the AutoEnhanced alignment proxy as the RGB WeightNet input.
        reference_analysis_gpu = (
            ref_analysis_flow_gpu
            if ref_analysis_flow_gpu is not None
            else ref_gpu
        )
        if weightnet_channels == 1:
            reference_gray_source_gpu = reference_analysis_gpu
            if tuple(
                int(value) for value in reference_analysis_gpu.shape[:2]
            ) != geometry.weight_shape:
                reference_gray_source_gpu = taichi_aot.resize(
                    reference_analysis_gpu,
                    (weight_work_w, weight_work_h),
                    interpolation=taichi_aot.INTER_AREA,
                    return_gpu=True,
                )
            taichi_aot.cvtColor(
                reference_gray_source_gpu,
                taichi_aot.COLOR_RGB2GRAY,
                dst=weightnet_gray_gpu,
                return_gpu=True,
            )
            if reference_gray_source_gpu is not reference_analysis_gpu:
                _destroy_work_item(reference_gray_source_gpu)
            reference_weight_input_gpu = weightnet_gray_gpu
        else:
            reference_weight_input_gpu = reference_analysis_gpu
        ref_work_rgb_np, ref_transfer_map = prepare_weightnet_reference_input(
            reference_weight_input_gpu,
            work_shape=geometry.weight_shape,
            clip_limit=2.0,
            tile_grid_size=(8, 8),
        )
        analysis_context.weight_reference = ref_work_rgb_np
        analysis_context.clahe_transfer_map = ref_transfer_map

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
    if weight_engine in ("spatial_fusion", "average"):
        # Average weights are uniform across channels. Keep the accumulator
        # scalar just like SpatialFusion; the common AOT graph broadcasts it
        # into the RGB sum and avoids a redundant full-resolution vec3 map.
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

    # One runtime-owned producer stages only decoded host frames.  The setting
    # is a strict queue capacity: zero performs synchronous loading.
    q_depth = runtime.prefetch_depth

    if progress_callback:
        progress_callback(
            PROGRESS_MERGE_MIN,
            ui="Menyiapkan Pipeline...",
            console=f"Memulai Pipeline Asynchronous Flow (host_queue={q_depth}, gpu_in_flight=1)...",
        )

    _SENTINEL = object()
    vram_queue = queue.Queue(maxsize=1)  # One unaligned frame resident in VRAM
    aligned_queue = queue.Queue(maxsize=1)  # One aligned frame in flight
    weighted_queue = queue.Queue(maxsize=1)  # One weighted frame awaiting blending

    print(
        f"[GPU Pipeline] Universal Multi-Stage Queue initialized: "
        f"host_queue={q_depth}, vram_input_in_flight=1, gpu_in_flight=1 (bounded VRAM footprint, cpu_mode={is_cpu_backend})"
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

    def _workers_stopped():
        return _is_stopped() or runtime.worker_stop_requested

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
        """Decode only; resizing and all Taichi work stay out of prefetch."""
        return rgb_provider.load_support_host(index)

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
            for curr_idx, supp_linear_input in runtime.iter_supports(
                range(1, num_images),
                _load_host_support,
                stop_when=lambda: _workers_stopped() or pipeline_error is not None,
                disposer=_destroy_work_item,
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
                        # Resize to work resolution, then apply the reference's
                        # AutoEnhance parameters in-place on that disposable
                        # proxy. At native resolution the helper makes one exact
                        # copy so the linear fusion carrier remains untouched.
                        supp_analysis_flow_gpu = prepare_analysis_proxy_gpu(
                            supp_linear_gpu,
                            work_shape=geometry.align_shape,
                            analysis_params=analysis_params,
                            in_place=True,
                        )

                        # Both weight engines reuse the same AutoEnhanced
                        # analysis proxy; only the linear carrier stays separate.
                        if weight_engine in ("fusionet", "spatial_fusion") and tuple(
                            int(value) for value in supp_analysis_flow_gpu.shape[:2]
                        ) == geometry.weight_shape:
                            supp_analysis_sec_gpu = supp_analysis_flow_gpu
                        elif weight_engine in ("fusionet", "spatial_fusion"):
                            supp_analysis_sec_gpu = taichi_aot.resize(
                                supp_analysis_flow_gpu,
                                (weight_work_w, weight_work_h),
                                interpolation=taichi_aot.INTER_AREA,
                                return_gpu=True,
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
                            np.transpose(weight_work_np, (1, 2, 0)),
                            dtype=np.float32,
                        )
                    if weight_work_item.ndim == 3 and weight_work_item.shape[2] == 1:
                        weight_work_item = np.repeat(weight_work_item, 3, axis=2)
                    elif weight_work_item.ndim == 2:
                        weight_work_item = np.repeat(weight_work_item[:, :, None], 3, axis=2)
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

    is_thread_affine = str(getattr(engine, "arch", "")).lower() in ("opengl", "gles")

    if is_thread_affine:
        # Context-affine backends (OpenGL/GLES) execute all GPU work synchronously on the context-owner thread
        threads = []

        processed_count = 0
        try:
            for curr_idx, supp_linear_np in runtime.iter_supports(
                range(1, num_images),
                _load_host_support,
                stop_when=lambda: _workers_stopped() or pipeline_error is not None,
                disposer=_destroy_work_item,
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
                    # Downscale linear frame to resident alignment work-res directly FIRST across all backends
                    if (flow_work_h, flow_work_w) != (target_h, target_w):
                        supp_linear_flow_gpu = taichi_aot.resize(
                            supp_linear_gpu,
                            (flow_work_w, flow_work_h),
                            interpolation=taichi_aot.INTER_AREA,
                            return_gpu=True,
                        )
                    else:
                        supp_linear_flow_gpu = supp_linear_gpu

                    # Generate on-the-fly Versi 1 (Analysis High-Key) on work-res directly
                    if analysis_params is not None:
                        supp_analysis_flow_gpu = apply_auto_enhance_on_gpu(
                            supp_linear_flow_gpu,
                            analysis_params,
                            dst=(
                                supp_linear_flow_gpu
                                if (
                                    weight_engine == "fusionet"
                                    and supp_linear_flow_gpu is not supp_linear_gpu
                                )
                                else None
                            ),
                        )
                        if (
                            supp_linear_flow_gpu is not supp_linear_gpu
                            and supp_analysis_flow_gpu is not supp_linear_flow_gpu
                        ):
                            _destroy_work_item(supp_linear_flow_gpu)
                    else:
                        supp_analysis_flow_gpu = supp_linear_flow_gpu

                    if weight_engine == "fusionet" and tuple(
                        int(value) for value in supp_analysis_flow_gpu.shape[:2]
                    ) == geometry.weight_shape:
                        supp_analysis_sec_gpu = supp_analysis_flow_gpu
                    elif weight_engine == "fusionet":
                        supp_analysis_sec_gpu = taichi_aot.resize(
                            supp_analysis_flow_gpu,
                            (weight_work_w, weight_work_h),
                            interpolation=taichi_aot.INTER_AREA,
                            return_gpu=True,
                        )
                    # Prepare linear secondary for other consumers.
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
                    if weightnet_channels == 1:
                        taichi_aot.cvtColor(
                            supp_aligned_sec_gpu,
                            taichi_aot.COLOR_RGB2GRAY,
                            dst=weightnet_gray_gpu,
                            return_gpu=True,
                        )
                        weightnet_input_gpu = weightnet_gray_gpu
                    _destroy_work_item(supp_aligned_sec_gpu)
                    supp_work_rgb_np = prepare_weightnet_support_input(
                        weightnet_input_gpu,
                        ref_transfer_map,
                        workspace=weightnet_support_workspace,
                    )
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
                    )
                    weight_work_item = (
                        weightnet_upload_workspace.stage(weight_work_np)
                        if weightnet_upload_workspace is not None
                        else np.ascontiguousarray(
                            np.transpose(weight_work_np, (1, 2, 0)),
                            dtype=np.float32,
                        )
                    )
                    if weight_work_item.ndim == 3 and weight_work_item.shape[2] == 1:
                        weight_work_item = np.repeat(weight_work_item, 3, axis=2)
                    elif weight_work_item.ndim == 2:
                        weight_work_item = np.repeat(weight_work_item[:, :, None], 3, axis=2)
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
                if weight_engine != "spatial_fusion":
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
        finally:
            runtime.close_streams()
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
                    f"(alpha={alpha_mean:.3f}, in_flight={weighted_queue.qsize()})"
                )
                pipeline_telemetry.emit(f"blend_{curr_idx}")

        finally:
            runtime.stop_workers()
            # Drain and destroy any remaining GPU buffers in queues immediately
            for q in (vram_queue, aligned_queue, weighted_queue):
                while not q.empty():
                    try:
                        val = q.get_nowait()
                        if val is not _SENTINEL and isinstance(val, tuple):
                            for el in val:
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

    mean_alpha = alpha_total / max(1, total_supp)
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
