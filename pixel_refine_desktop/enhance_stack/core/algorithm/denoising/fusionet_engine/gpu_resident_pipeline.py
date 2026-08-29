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
    │    c. Grayscale on GPU (rgb2gray)                      │
    │    d. Download work-res for ONNX (~2 MB)               │
    │    e. Upload weight map back to GPU                     │
    │    f. Upsample weight to full-res on GPU               │
    │    g. Blend: multiply-add on CPU bridge                 │
    └────────────────────┬────────────────────────────────────┘
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │  Download final fused result (one frame)                │
    └─────────────────────────────────────────────────────────┘
"""

import gc
import os
import threading
from pathlib import Path
from typing import Callable, Optional, Sequence, Tuple

import numpy as np

from taichi_vision.taichi_aot import TaichiGPUBuffer, get_engine


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


def load_frame_to_gpu(
    path: str | Path,
    is_raw: bool = False,
) -> TaichiGPUBuffer:
    """Load a single image directly to GPU VRAM as float32 [0,1] RGB.

    RAW/DNG:  demosaic (Hamilton) -> GPU float32 RGB
    Standard: imread -> GPU uint8 BGR -> cvtColor BGR->RGB -> GPU float32
    """
    from taichi_vision import taichi_aot

    path = Path(path)
    is_raw_file = is_raw or path.suffix.lower() in _RAW_EXTENSIONS

    if is_raw_file:
        rgb_gpu = taichi_aot.demosaic(
            str(path),
            method="hamilton",
            return_gpu=True,
        )
        if rgb_gpu.dtype in (np.uint8, np.uint16):
            scale = 255.0 if rgb_gpu.dtype == np.uint8 else 65535.0
            rgb_np = rgb_gpu.to_numpy().astype(np.float32) / scale
            rgb_gpu.destroy()
            return taichi_aot.upload(
                np.ascontiguousarray(np.clip(rgb_np, 0.0, 1.0), dtype=np.float32)
            )
        return rgb_gpu

    import cv2

    img_bgr = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img_bgr is None:
        raise ValueError(f"Failed to read image: {path}")

    orientation = _read_orientation(path)
    if orientation != 1:
        img_bgr = _apply_orientation(img_bgr, orientation)

    if img_bgr.ndim == 2:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2RGB)
    else:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    del img_bgr

    if np.issubdtype(img_rgb.dtype, np.integer):
        scale = 65535.0 if img_rgb.dtype == np.uint16 else 255.0
        rgb_f32 = img_rgb.astype(np.float32) / scale
    else:
        rgb_f32 = img_rgb.astype(np.float32)
    del img_rgb

    return taichi_aot.upload(
        np.ascontiguousarray(np.clip(rgb_f32, 0.0, 1.0), dtype=np.float32)
    )


# ---------------------------------------------------------------------------
# GPU-Resident AutoEnhance
# ---------------------------------------------------------------------------


def analyze_auto_enhance_on_gpu(
    ref_gpu: TaichiGPUBuffer, mode: str = "natural"
) -> dict:
    from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
        analyze_auto_enhance_params,
    )

    ref_np = ref_gpu.to_numpy()
    params = analyze_auto_enhance_params(ref_np, mode=mode)
    del ref_np
    return params


def apply_auto_enhance_on_gpu(
    src_gpu: TaichiGPUBuffer,
    params: dict,
) -> TaichiGPUBuffer:
    from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
        apply_auto_enhance_gpu,
    )

    return apply_auto_enhance_gpu(src_gpu, params, return_gpu=True)


# ---------------------------------------------------------------------------
# GPU-Resident Alignment Wrapper
# ---------------------------------------------------------------------------


class GPUResidentAligner:
    """Wraps AOTOpticalFlowAligner for GPU-resident frame flow."""

    def __init__(
        self,
        ref_rgb_np,
        *,
        work_scale=0.50,
        tile_size=16,
        search_dist=2,
        max_search_radius=12,
    ):
        from .flownet_inference import AOTOpticalFlowAligner

        self._aligner = AOTOpticalFlowAligner(
            ref_rgb_np,
            work_scale=work_scale,
            tile_size=tile_size,
            search_dist=search_dist,
            max_search_radius=max_search_radius,
        )

    def align_frame_gpu(self, supp_gpu, *, stop_event=None):
        if isinstance(supp_gpu, TaichiGPUBuffer):
            supp_np = supp_gpu.to_numpy()
        else:
            supp_np = supp_gpu
        return self._aligner.align_frame(
            supp_np, stop_event=stop_event, return_gpu=True
        )

    def close(self):
        self._aligner.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ---------------------------------------------------------------------------
# GPU-Resident Weight + Blend Bridge
# ---------------------------------------------------------------------------


def _compute_weight_onnx(
    session,
    ref_work_rgb_np,
    supp_work_rgb_np,
    *,
    tile_size=512,
    overlap=0.30,
    ghost_penalty=1.0,
    ghost_cutoff=0.05,
    chroma_sensitivity=6.0,
    stop_event=None,
):
    from .weightnet_inference import infer_single_support_weight_map

    return infer_single_support_weight_map(
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


def _gpu_blend_frame(
    sum_img_gpu, weight_sum_gpu, supp_aligned_gpu, weight_work_gpu
):
    """Blend one support frame into the GPU-resident accumulator.

    Uses accumulate_spatial_merging_taichi from SpatialFusion which
    auto-dispatches to the vec3 kernel when given a 3D weight map.

    The vec3 kernel performs per-channel bilinear upsample + multiply + accumulate
    entirely on GPU on-the-fly — saving 144 MB VRAM per frame.
    """
    from taichi_vision.taichi_algorithm.spatial_fusion import (
        accumulate_spatial_merging_taichi,
    )

    accumulate_spatial_merging_taichi(
        current_image_full=supp_aligned_gpu.view_as_vector(False),
        weight_map_work=weight_work_gpu.view_as_vector(False),
        final_image_sum=sum_img_gpu.view_as_vector(False),
        weight_map_sum_full=weight_sum_gpu.view_as_vector(False),
    )


# ---------------------------------------------------------------------------
# Main GPU-Resident Pipeline
# ---------------------------------------------------------------------------


def run_gpu_resident_pipeline(
    image_paths: Sequence[str | Path],
    session,
    *,
    work_scale: float = 0.50,
    tile_size: int = 512,
    overlap: float = 0.30,
    ghost_penalty: float = 1.0,
    ghost_cutoff: float = 0.05,
    chroma_sensitivity: float = 6.0,
    is_raw: bool = False,
    auto_params: Optional[dict] = None,
    stop_event: Optional[threading.Event] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> Tuple[Optional[np.ndarray], float]:
    """Execute the full GPU-resident FusionNet pipeline.

    All full-resolution data stays in VRAM. The only CPU touches are:
    1. ONNX weight inference at work-resolution (~2 MB/frame)
    2. auto_enhance analysis on reference (once, tiny)
    3. Final result download (1 frame)

    Args:
        image_paths: List of image file paths (burst).
        session: WeightNet ONNX session.
        work_scale: Downscale factor for WeightNet weight computation.
        tile_size: WeightNet tile size (model input).
        overlap: Tile overlap ratio.
        ghost_penalty: Ghost artifact suppression exponent.
        ghost_cutoff: Ghost cutoff threshold.
        chroma_sensitivity: Color deviation protection scale.
        is_raw: Whether images are RAW/DNG.
        auto_params: Pre-computed auto_enhance params (analyzed on first frame if None).
        stop_event: Cancellation signal.
        progress_callback: Progress reporting callback.

    Returns:
        (result_fp32, mean_alpha): Fused float32 RGB [H, W, 3] and mean alpha.
    """
    from taichi_vision import taichi_aot
    from taichi_vision.taichi_aot import get_engine
    from .flownet_inference import AOTOpticalFlowAligner, load_compute_flow_module
    from .weightnet_inference import (
        load_weightnet_onnx,
        infer_single_support_weight_map,
        load_rgb_linear_image,
    )

    engine = get_engine()
    num_images = len(image_paths)
    if num_images < 2:
        raise ValueError(f"Need at least 2 images, got {num_images}")

    # ------------------------------------------------------------------
    # PHASE 1: Load reference frame directly to GPU
    # ------------------------------------------------------------------
    if progress_callback:
        progress_callback(2, "Loading reference frame to GPU VRAM...")

    ref_gpu = load_frame_to_gpu(image_paths[0], is_raw=is_raw)
    target_h, target_w = ref_gpu.shape[:2]

    print(
        f"[GPU Pipeline] Reference loaded to VRAM: "
        f"shape=({target_h}, {target_w}, 3) dtype={ref_gpu.dtype} "
        f"size={ref_gpu.nbytes / (1024*1024):.1f} MB"
    )

    # ------------------------------------------------------------------
    # PHASE 2: Two-Tier Decoupled AutoEnhance Analysis
    # ------------------------------------------------------------------
    # Versi 1 (Analysis / High-Key): Used for FlowNet Alignment (Native Res) & ONNX WeightNet
    # Versi 2 (Natural Tone-Mapping): Used for Master Final Post-Process Output
    analysis_params = None
    natural_params = None

    if is_raw:
        analysis_params = analyze_auto_enhance_on_gpu(ref_gpu, mode="analysis")
        natural_params = analyze_auto_enhance_on_gpu(ref_gpu, mode="natural")
        print(
            f"[GPU Pipeline] AutoEnhance: Analysis Gain (v1)={analysis_params['gain']:.2f}x | "
            f"Final Natural Gain (v2)={natural_params['gain']:.2f}x"
        )

    # ------------------------------------------------------------------
    # PHASE 3: Create Analysis Reference & Work-Resolution Copy for ONNX
    # ------------------------------------------------------------------
    work_h = max(32, int(target_h * work_scale))
    work_w = max(32, int(target_w * work_scale))

    # Create high-contrast analysis copy (Versi 1) on-the-fly
    if is_raw and analysis_params is not None:
        ref_analysis_gpu = apply_auto_enhance_on_gpu(ref_gpu, analysis_params)
    else:
        ref_analysis_gpu = ref_gpu

    # Work-resolution copy for ONNX WeightNet inference
    if (work_h, work_w) != (target_h, target_w):
        ref_work_rgb_hwc_gpu = taichi_aot.resize(
            ref_analysis_gpu,
            (work_w, work_h),
            interpolation=taichi_aot.INTER_AREA,
            return_gpu=True,
        )
    else:
        ref_work_rgb_hwc_gpu = ref_analysis_gpu

    ref_work_rgb_np = np.transpose(ref_work_rgb_hwc_gpu.to_numpy(), (2, 0, 1)).astype(
        np.float32
    )  # [3, work_h, work_w]

    if ref_work_rgb_hwc_gpu is not ref_analysis_gpu:
        ref_work_rgb_hwc_gpu.destroy()

    # ------------------------------------------------------------------
    # PHASE 4: Build GPU pyramid for FlowNet Alignment (Native Res 1.0)
    # ------------------------------------------------------------------
    if progress_callback:
        progress_callback(
            5, "Building reference pyramid on GPU (v1 Analysis Native Res)..."
        )

    aligner = AOTOpticalFlowAligner(
        ref_analysis_gpu,
        work_scale=work_scale,
        tile_size=16,
    )

    if ref_analysis_gpu is not ref_gpu:
        ref_analysis_gpu.destroy()

    # ------------------------------------------------------------------
    # PHASE 5: Initialize GPU accumulators with 100% True Linear RAW Reference
    # ------------------------------------------------------------------
    # sum_img: (H, W, 3) HWC — Accumulates true linear raw data
    sum_img_gpu = engine.upload(ref_gpu.to_numpy())
    weight_sum_gpu = engine.upload(np.ones((target_h, target_w, 3), dtype=np.float32))

    alpha_total = 0.0
    total_supp = num_images - 1

    # ------------------------------------------------------------------
    # PHASE 6: Sliding Window Staged VRAM Queue + Async Pre-loader
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # PHASE 6: Asynchronous Multi-Stage Flow Coordinator Pipeline
    # ------------------------------------------------------------------
    # Stage 1: Preloader Thread   -> preloaded_queue (maxsize=2)
    # Stage 2: Alignment Thread   -> aligned_queue   (maxsize=2)
    # Stage 3: ONNX Inference     -> weighted_queue  (maxsize=2)
    # Stage 4: GPU Blending (Main Thread) consumes weighted_queue
    # ------------------------------------------------------------------
    if progress_callback:
        progress_callback(8, "Starting Asynchronous Flow Coordinator Pipeline...")

    import queue

    _SENTINEL = object()
    preloaded_queue = queue.Queue(maxsize=2)  # Host RAM queue (0 MB VRAM)
    aligned_queue = queue.Queue(
        maxsize=1
    )  # GPU VRAM queue (strictly 1 frame in flight)
    weighted_queue = queue.Queue(
        maxsize=1
    )  # GPU VRAM queue (strictly 1 frame in flight)

    pipeline_error = None
    pipeline_lock = threading.Lock()
    gpu_hardware_lock = threading.Lock()

    def _set_error(exc):
        nonlocal pipeline_error
        with pipeline_lock:
            if pipeline_error is None:
                pipeline_error = exc

    # ------------------------------------------------------------------
    # Worker 1: Disk Preloader (loads RAW to CPU Host RAM - 0 MB VRAM)
    # ------------------------------------------------------------------
    def _preloader_worker():
        try:
            for idx in range(1, num_images):
                if stop_event is not None and stop_event.is_set():
                    break
                if pipeline_error is not None:
                    break
                f_path = image_paths[idx]
                f_name = Path(f_path).name
                s_np = load_rgb_linear_image(f_path, is_raw=is_raw)
                if s_np.shape[:2] != (target_h, target_w):
                    s_np = cv2.resize(
                        s_np, (target_w, target_h), interpolation=cv2.INTER_LINEAR
                    )

                while not (stop_event is not None and stop_event.is_set()):
                    if pipeline_error is not None:
                        del s_np
                        return
                    try:
                        preloaded_queue.put((idx, f_name, s_np), timeout=0.1)
                        break
                    except queue.Full:
                        continue
        except Exception as exc:
            _set_error(exc)
        finally:
            preloaded_queue.put(_SENTINEL)

    # ------------------------------------------------------------------
    # Worker 2: Optical Flow Alignment & Dual-Warp (Taichi Vulkan GPU)
    # ------------------------------------------------------------------
    def _alignment_worker():
        try:
            while True:
                if stop_event is not None and stop_event.is_set():
                    break
                if pipeline_error is not None:
                    break
                try:
                    item = preloaded_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                if item is _SENTINEL:
                    break

                curr_idx, curr_name, supp_linear_np = item

                with gpu_hardware_lock:
                    # Upload single frame to VRAM on demand
                    supp_linear_gpu = engine.upload(supp_linear_np)
                    del supp_linear_np

                    # Generate on-the-fly Versi 1 (Analysis High-Key) for FlowNet
                    if is_raw and analysis_params is not None:
                        supp_analysis_gpu = apply_auto_enhance_on_gpu(
                            supp_linear_gpu, analysis_params
                        )
                    else:
                        supp_analysis_gpu = supp_linear_gpu

                    # Downscale analysis frame to work-res directly before warping
                    if (work_h, work_w) != (target_h, target_w):
                        supp_analysis_work_gpu = taichi_aot.resize(
                            supp_analysis_gpu,
                            (work_w, work_h),
                            interpolation=taichi_aot.INTER_AREA,
                            return_gpu=True,
                        )
                    else:
                        supp_analysis_work_gpu = supp_analysis_gpu

                    # Dual-Warp on GPU (Primary in full-res 12MP, Secondary directly in work-res ~36MB!)
                    supp_aligned_linear_gpu, supp_aligned_analysis_work_gpu = (
                        aligner.align_frame(
                            supp_linear_gpu,
                            analysis_frame_gpu=supp_analysis_gpu,
                            secondary_frame_to_warp=supp_analysis_work_gpu,
                            stop_event=stop_event,
                            return_gpu=True,
                        )
                    )
                    supp_linear_gpu.destroy()
                    if supp_analysis_gpu is not supp_linear_gpu:
                        supp_analysis_gpu.destroy()
                    if supp_analysis_work_gpu is not supp_analysis_gpu:
                        supp_analysis_work_gpu.destroy()

                    supp_work_rgb_np = np.transpose(
                        supp_aligned_analysis_work_gpu.to_numpy(), (2, 0, 1)
                    ).astype(np.float32)

                    supp_aligned_analysis_work_gpu.destroy()
                    engine.sync()

                while not (stop_event is not None and stop_event.is_set()):
                    if pipeline_error is not None:
                        supp_aligned_linear_gpu.destroy()
                        return
                    try:
                        aligned_queue.put(
                            (
                                curr_idx,
                                curr_name,
                                supp_aligned_linear_gpu,
                                supp_work_rgb_np,
                            ),
                            timeout=0.1,
                        )
                        break
                    except queue.Full:
                        continue
        except Exception as exc:
            _set_error(exc)
        finally:
            aligned_queue.put(_SENTINEL)

    # ------------------------------------------------------------------
    # Worker 3: DirectML ONNX AI Weight Inference
    # ------------------------------------------------------------------
    def _onnx_inference_worker():
        try:
            while True:
                if stop_event is not None and stop_event.is_set():
                    break
                if pipeline_error is not None:
                    break
                try:
                    item = aligned_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                if item is _SENTINEL:
                    break

                curr_idx, curr_name, supp_aligned_linear_gpu, supp_work_rgb_np = item

                with gpu_hardware_lock:
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
                    engine.sync()

                while not (stop_event is not None and stop_event.is_set()):
                    if pipeline_error is not None:
                        supp_aligned_linear_gpu.destroy()
                        return
                    try:
                        weighted_queue.put(
                            (
                                curr_idx,
                                curr_name,
                                supp_aligned_linear_gpu,
                                weight_work_np,
                                alpha_mean,
                            ),
                            timeout=0.1,
                        )
                        break
                    except queue.Full:
                        continue
        except Exception as exc:
            _set_error(exc)
        finally:
            weighted_queue.put(_SENTINEL)

    # Launch background stages
    t_preloader = threading.Thread(
        target=_preloader_worker, name="Stage1_Preloader", daemon=True
    )
    t_aligner = threading.Thread(
        target=_alignment_worker, name="Stage2_Aligner", daemon=True
    )
    t_onnx = threading.Thread(
        target=_onnx_inference_worker, name="Stage3_ONNX", daemon=True
    )

    t_preloader.start()
    t_aligner.start()
    t_onnx.start()

    processed_count = 0

    try:
        # --------------------------------------------------------------
        # Stage 4: GPU Accumulator Blending (Runs in Main Thread)
        # --------------------------------------------------------------
        while True:
            if stop_event is not None and stop_event.is_set():
                break
            if pipeline_error is not None:
                raise pipeline_error

            try:
                item = weighted_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if item is _SENTINEL:
                break

            (
                curr_idx,
                curr_name,
                supp_aligned_linear_gpu,
                weight_work_np,
                alpha_mean,
            ) = item

            processed_count += 1
            alpha_total += alpha_mean

            if progress_callback:
                base_p = 8 + int(processed_count / total_supp * 85)
                progress_callback(
                    base_p,
                    f"Pipelined GPU Fusion frame {curr_idx}/{total_supp}: {curr_name}...",
                )

            with gpu_hardware_lock:
                weight_work_hwc = np.ascontiguousarray(
                    np.transpose(weight_work_np, (1, 2, 0)), dtype=np.float32
                )
                del weight_work_np
                weight_work_gpu = engine.upload(weight_work_hwc)

                _gpu_blend_frame(
                    sum_img_gpu,
                    weight_sum_gpu,
                    supp_aligned_linear_gpu,
                    weight_work_gpu,
                )

                supp_aligned_linear_gpu.destroy()
                weight_work_gpu.destroy()
                engine.sync()

            print(
                f"[GPU Flow Coordinator] Frame {curr_idx}/{total_supp} ({curr_name}) blended "
                f"(alpha={alpha_mean:.3f}, in_flight={weighted_queue.qsize()})"
            )

    finally:
        # Drain and destroy any remaining GPU buffers in queues if aborted
        for q in (preloaded_queue, aligned_queue, weighted_queue):
            while not q.empty():
                try:
                    val = q.get_nowait()
                    if val is not _SENTINEL and isinstance(val, tuple):
                        for el in val:
                            if el is not None and hasattr(el, "destroy"):
                                try:
                                    el.destroy()
                                except Exception:
                                    pass
                except Exception:
                    pass

        t_preloader.join(timeout=1.0)
        t_aligner.join(timeout=1.0)
        t_onnx.join(timeout=1.0)

    # ------------------------------------------------------------------
    # PHASE 7: Final Linear Normalization & Tier 2 Natural AutoEnhance
    # ------------------------------------------------------------------
    if progress_callback:
        progress_callback(96, "Finalizing GPU-resident fusion...")

    # Use mean_division_vec3_weight_taichi — per-channel GPU normalization
    # Directly passing ref_gpu (already resident in VRAM, 0 overhead!)
    from taichi_vision.taichi_algorithm.spatial_fusion import (
        mean_division_vec3_weight_taichi,
    )

    _final_linear_gpu = mean_division_vec3_weight_taichi(
        sum_img=sum_img_gpu,
        sum_weight=weight_sum_gpu,
        ref_img=ref_gpu,
    )

    # Apply Tier 2: Final Natural AutoEnhance on the clean merged linear image
    if is_raw and natural_params is not None:
        if progress_callback:
            progress_callback(98, "Applying master natural tone-mapping...")
        _final_enhanced_gpu = apply_auto_enhance_on_gpu(
            _final_linear_gpu, natural_params
        )
        _final_linear_gpu.destroy()
        result_hwc = np.ascontiguousarray(
            _final_enhanced_gpu.to_numpy(), dtype=np.float32
        )
        _final_enhanced_gpu.destroy()
    else:
        result_hwc = np.ascontiguousarray(
            _final_linear_gpu.to_numpy(), dtype=np.float32
        )
        _final_linear_gpu.destroy()

    # Cleanup GPU resources
    try:
        sum_img_gpu.destroy()
        weight_sum_gpu.destroy()
        ref_gpu.destroy()
        aligner.close()
    except Exception:
        pass
    del ref_work_rgb_np
    try:
        engine.sync()
        engine.get_device_block_cache().clear()
    except Exception:
        pass
    gc.collect()

    mean_alpha = alpha_total / max(1, total_supp)
    print(
        f"[GPU Pipeline] Complete: shape={result_hwc.shape} "
        f"mean_alpha={mean_alpha:.4f}"
    )

    return result_hwc, mean_alpha
