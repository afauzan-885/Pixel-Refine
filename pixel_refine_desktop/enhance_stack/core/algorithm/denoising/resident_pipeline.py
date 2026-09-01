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
import queue
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Optional, Sequence, Tuple, Union
import numpy as np

from taichi_vision.taichi_aot import TaichiGPUBuffer, get_engine

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
    ):
        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Alignment cancelled.")
            elif callable(stop_event) and stop_event():
                raise RuntimeError("Alignment cancelled.")
        return supp_linear_gpu, secondary_frame_to_warp

    def close(self):
        pass


class FeatureMatchingGPUAligner:
    """Pluggable GPU-Resident Feature Matching Aligner (ORB, AKAZE, SIFT, LightGlue)."""

    def __init__(
        self,
        ref_analysis_gpu: TaichiGPUBuffer,
        *,
        feature_type: str = "orb",
        work_scale: float = 0.50,
        full_shape: Optional[Tuple[int, int]] = None,
        feature_config: Optional[dict] = None,
    ):
        import cv2
        from taichi_vision import taichi_aot

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
            ref_gray_gpu.destroy()
            ref_gray_gpu = ref_gray_work

        ref_gray_np = (
            np.clip(ref_gray_gpu.to_numpy(), 0.0, 1.0) * 255.0
        ).astype(np.uint8)
        ref_gray_gpu.destroy()

        if "akaze" in self.feature_type:
            thresh = float(self.config.get("akaze_threshold", 0.001))
            self.detector = cv2.AKAZE_create(threshold=thresh)
            self.norm_type = cv2.NORM_HAMMING
        elif "sift" in self.feature_type:
            nfeatures = int(self.config.get("nfeatures", 2000))
            self.detector = cv2.SIFT_create(nfeatures=nfeatures)
            self.norm_type = cv2.NORM_L2
        else:
            nfeatures = int(self.config.get("nfeatures", 2000))
            scale_factor = float(self.config.get("scaleFactor", 1.2))
            nlevels = int(self.config.get("nlevels", 8))
            self.detector = cv2.ORB_create(
                nfeatures=nfeatures, scaleFactor=scale_factor, nlevels=nlevels
            )
            self.norm_type = cv2.NORM_HAMMING

        self.kp_ref, self.des_ref = self.detector.detectAndCompute(ref_gray_np, None)
        self.matcher = cv2.BFMatcher(self.norm_type, crossCheck=True)

    def align_frame(
        self,
        supp_linear_gpu,
        *,
        analysis_frame_gpu=None,
        secondary_frame_to_warp=None,
        stop_event=None,
        return_gpu=True,
    ):
        import cv2
        from taichi_vision import taichi_aot

        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Alignment cancelled.")
            elif callable(stop_event) and stop_event():
                raise RuntimeError("Alignment cancelled.")

        src_for_analysis = (
            analysis_frame_gpu
            if analysis_frame_gpu is not None
            else supp_linear_gpu
        )
        supp_gray_gpu = taichi_aot.cvtColor(
            src_for_analysis, taichi_aot.COLOR_RGB2GRAY
        )
        if (self.work_h, self.work_w) != (self.target_h, self.target_w):
            supp_gray_work = taichi_aot.resize(
                supp_gray_gpu,
                (self.work_w, self.work_h),
                interpolation=taichi_aot.INTER_AREA,
                return_gpu=True,
            )
            supp_gray_gpu.destroy()
            supp_gray_gpu = supp_gray_work

        supp_gray_np = (
            np.clip(supp_gray_gpu.to_numpy(), 0.0, 1.0) * 255.0
        ).astype(np.uint8)
        supp_gray_gpu.destroy()

        kp_supp, des_supp = self.detector.detectAndCompute(supp_gray_np, None)
        H_matrix = None
        scale_x = self.target_w / float(self.work_w)
        scale_y = self.target_h / float(self.work_h)

        if (
            self.des_ref is not None
            and des_supp is not None
            and len(self.kp_ref) >= 4
            and len(kp_supp) >= 4
        ):
            matches = self.matcher.match(self.des_ref, des_supp)
            if len(matches) >= 4:
                matches = sorted(matches, key=lambda m: m.distance)[:100]
                pts_ref = np.float32([self.kp_ref[m.queryIdx].pt for m in matches])
                pts_supp = np.float32([kp_supp[m.trainIdx].pt for m in matches])

                pts_ref_full = pts_ref * np.array([scale_x, scale_y], dtype=np.float32)
                pts_supp_full = pts_supp * np.array([scale_x, scale_y], dtype=np.float32)

                H_matrix, _ = cv2.findHomography(
                    pts_supp_full, pts_ref_full, cv2.RANSAC, 5.0
                )

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
            return warped_primary, warped_secondary
        else:
            return supp_linear_gpu, secondary_frame_to_warp

    def close(self):
        pass


def create_resident_aligner(
    alignment_plan: str,
    ref_analysis_gpu: TaichiGPUBuffer,
    *,
    work_scale: float = 0.50,
    full_shape: Optional[Tuple[int, int]] = None,
    alignment_config: Optional[dict] = None,
):
    """Factory creating the appropriate GPU-resident aligner instance."""
    plan_clean = str(alignment_plan or "").strip().lower()
    if plan_clean in ("no alignment", "none", "off", ""):
        print("[GPU Pipeline] Aligner: No Alignment (Bypass)")
        return NoAlignmentGPUAligner(ref_analysis_gpu)
    elif plan_clean in ("ofb", "orb", "akaze", "sift", "lightglue", "feature matching"):
        print(f"[GPU Pipeline] Aligner: Feature Matching ({plan_clean.upper()})")
        return FeatureMatchingGPUAligner(
            ref_analysis_gpu,
            feature_type=plan_clean,
            work_scale=work_scale,
            full_shape=full_shape,
            feature_config=alignment_config,
        )
    else:
        print(f"[GPU Pipeline] Aligner: Dense Optical Flow ({plan_clean})")
        from .fusionet_engine.flownet_inference import AOTOpticalFlowAligner

        return AOTOpticalFlowAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            tile_size=16,
        )


# ---------------------------------------------------------------------------
# GPU-Resident Weight + Blend Bridge
# ---------------------------------------------------------------------------


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
    session=None,
    *,
    weight_engine: str = "fusionet",
    alignment_plan: str = "optical_flow",
    alignment_config: Optional[dict] = None,
    spatial_config: Optional[dict] = None,
    work_scale: float = 0.50,
    tile_size: int = 512,
    overlap: float = 0.30,
    ghost_penalty: float = 1.0,
    ghost_cutoff: float = 0.05,
    chroma_sensitivity: float = 6.0,
    is_raw: bool = False,
    storage_mode: str = "direct",
    alignment_only: bool = False,
    batch_queue: int = 3,
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
        tile_size: Tile size for weight computation.
        overlap: Tile overlap ratio.
        ghost_penalty: Ghost artifact suppression exponent.
        ghost_cutoff: Ghost cutoff threshold.
        chroma_sensitivity: Color deviation protection scale.
        is_raw: Whether images are RAW/DNG.
        storage_mode: "direct" (RAM/VRAM stream).
        alignment_only: If True, executes pure alignment without blending.
        auto_params: Pre-computed auto_enhance params (analyzed on first frame if None).
        stop_event: Cancellation signal.
        progress_callback: Progress reporting callback.

    Returns:
        (result_fp32, mean_alpha): Fused float32 RGB [H, W, 3] and mean alpha.
    """
    from taichi_vision import taichi_aot
    from taichi_vision.taichi_aot import get_engine
    from .fusionet_engine.flownet_inference import (
        AOTOpticalFlowAligner,
        load_compute_flow_module,
    )
    from .fusionet_engine.weightnet_inference import (
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

    import gc
    try:
        from taichi_vision import taichi_aot
        taichi_aot.engine.buffer_pool.clear()
    except Exception:
        pass
    gc.collect()

    ref_gpu = load_frame_to_gpu(image_paths[0], is_raw=is_raw)
    target_h, target_w = ref_gpu.shape[:2]

    print(
        f"[GPU Pipeline] Reference loaded to VRAM: "
        f"shape=({target_h}, {target_w}, 3) dtype={ref_gpu.dtype} "
        f"size={ref_gpu.nbytes / (1024*1024):.1f} MB (engine={weight_engine})"
    )

    # ------------------------------------------------------------------
    # PHASE 2: Tier 1 Analysis AutoEnhance for Feature Extraction
    # ------------------------------------------------------------------
    # AutoEnhance analysis on reference frame:
    # - Versi 1 (Analysis / High-Key): For Alignment & ONNX WeightNet (Used for BOTH RAW & Non-RAW)
    # - Versi 2 (Natural Tone Map): For SpatialFusion Perceptual Analysis (RAW only)
    analysis_params = analyze_auto_enhance_on_gpu(ref_gpu, mode="analysis")
    natural_params = analyze_auto_enhance_on_gpu(ref_gpu, mode="natural") if is_raw else None
    if is_raw and natural_params is not None:
        print(
            f"[GPU Pipeline] AutoEnhance: Analysis Gain (v1)={analysis_params['gain']:.2f}x | "
            f"Natural Gain (v2)={natural_params['gain']:.2f}x"
        )
    else:
        print(
            f"[GPU Pipeline] AutoEnhance (Non-RAW): Analysis Gain (v1)={analysis_params['gain']:.2f}x "
            f"(Applied only to analysis/flow/weightnet computation)"
        )

    # ------------------------------------------------------------------
    # PHASE 3: Create Analysis Reference & Work-Resolution Copy
    # ------------------------------------------------------------------
    # Adaptive Work Resolution: ensure work resolution never exceeds 2048px on large sensors (>12MP)
    max_dimension = max(target_h, target_w)
    if max_dimension > 2048:
        capped_scale = min(work_scale, 2048.0 / float(max_dimension))
    else:
        capped_scale = work_scale

    work_h = max(32, int(target_h * capped_scale))
    work_w = max(32, int(target_w * capped_scale))

    # Create high-contrast analysis copy (Versi 1) on-the-fly for feature alignment & weight computation
    if analysis_params is not None:
        ref_analysis_gpu = apply_auto_enhance_on_gpu(ref_gpu, analysis_params)
    else:
        ref_analysis_gpu = ref_gpu

    # Downscale analysis frame to work-res directly FIRST to minimize VRAM footprint (144MB -> 36MB or less)
    if (work_h, work_w) != (target_h, target_w):
        ref_analysis_work_gpu = taichi_aot.resize(
            ref_analysis_gpu,
            (work_w, work_h),
            interpolation=taichi_aot.INTER_AREA,
            return_gpu=True,
        )
        if ref_analysis_gpu is not ref_gpu:
            ref_analysis_gpu.destroy()
        ref_analysis_gpu = ref_analysis_work_gpu

    # Noise-Aware Analysis Pre-Filter on work-res:
    # - Noise Score >= 0.60: Aggressive pre-denoising (5x5 Box Filter)
    # - 0.30 <= Noise Score < 0.60: Light pre-denoising (3x3 Box Filter)
    # - Noise Score < 0.30: Clean image, pre-denoising bypassed
    analysis_box_kernel_size = 0
    try:
        from taichi_vision.taichi_algorithm.enhancement.estimate_noise import (
            estimate_noise,
        )

        ref_noise_score = float(estimate_noise(ref_analysis_gpu))
        if ref_noise_score >= 0.60:
            analysis_box_kernel_size = 5
            ref_analysis_denoised = taichi_aot.box_filter(
                ref_analysis_gpu, kernel_size=5, return_gpu=True
            )
            if ref_analysis_gpu is not ref_gpu:
                ref_analysis_gpu.destroy()
            ref_analysis_gpu = ref_analysis_denoised
            print(
                f"[GPU Pipeline] High/Extreme noise detected for analysis (score={ref_noise_score:.4f} >= 0.60). "
                f"Enabled aggressive Box Filter (5x5) pre-denoising."
            )
        elif ref_noise_score >= 0.30:
            analysis_box_kernel_size = 3
            ref_analysis_denoised = taichi_aot.box_filter(
                ref_analysis_gpu, kernel_size=3, return_gpu=True
            )
            if ref_analysis_gpu is not ref_gpu:
                ref_analysis_gpu.destroy()
            ref_analysis_gpu = ref_analysis_denoised
            print(
                f"[GPU Pipeline] Moderate noise detected for analysis (score={ref_noise_score:.4f} >= 0.30). "
                f"Enabled light Box Filter (3x3) pre-denoising."
            )
        else:
            print(
                f"[GPU Pipeline] Low noise detected for analysis (score={ref_noise_score:.4f} < 0.30). "
                f"Bypassed analysis pre-denoising."
            )
    except Exception as e_noise:
        print(f"[GPU Pipeline] Noise estimation note: {e_noise}")

    ref_work_rgb_np = None
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
    spatial_row_starts = []
    spatial_col_starts = []

    if weight_engine == "spatial_fusion":
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            SpatialScratchCache,
            generate_spatial_weights_taichi,
            resolve_spatial_thresholds,
        )
        from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (
            _compute_tile_starts,
        )

        cfg = spatial_config or {}
        st_size = int(
            cfg.get(
                "similarity_spatial_tile_size",
                tile_size if tile_size <= 64 else 16,
            )
        )
        spatial_tile_h = st_size
        spatial_tile_w = st_size
        spatial_overlap = float(cfg.get("similarity_spatial_overlap_percent", overlap))
        spatial_motion_sens = float(
            cfg.get("similarity_spatial_motion_sensitivity", 150.0)
        )
        spatial_noise_offset = float(
            cfg.get("similarity_spatial_noise_mad_offset_factor", 0.15)
        )

        # SpatialFusion analyzes via AutoEnhance v1 (High-Key Analysis Mode)
        if (work_h, work_w) != (target_h, target_w):
            ref_work_v1_gpu = taichi_aot.resize(
                ref_analysis_gpu,
                (work_w, work_h),
                interpolation=taichi_aot.INTER_AREA,
                return_gpu=True,
            )
        else:
            ref_work_v1_gpu = ref_analysis_gpu

        ref_spatial_gray_gpu = taichi_aot.cvtColor(
            ref_work_v1_gpu, taichi_aot.COLOR_RGB2GRAY
        )
        ref_work_rgb_np = np.transpose(
            ref_work_v1_gpu.to_numpy(), (2, 0, 1)
        ).astype(np.float32)  # [3, work_h, work_w]

        if ref_work_v1_gpu is not ref_analysis_gpu:
            ref_work_v1_gpu.destroy()

        # Estimasi noise 100% GPU-Native Taichi Vision (Wavelet Subband Minima & Patch Subspace)
        # Terkalibrasi ke noise sigma spatial domain: score * 0.032 * 1.25
        if 'ref_noise_score' in locals() and ref_noise_score is not None:
            auto_noise_sigma = float(np.clip(ref_noise_score * 0.040, 1e-4, 0.99999))
        else:
            try:
                from taichi_vision.taichi_algorithm.enhancement.estimate_noise import estimate_noise
                gpu_score = float(estimate_noise(ref_work_v1_gpu))
                auto_noise_sigma = float(np.clip(gpu_score * 0.040, 1e-4, 0.99999))
            except Exception:
                auto_noise_sigma = 0.025

        explicit_noise_sigma = cfg.get("noise_sigma")
        if explicit_noise_sigma is not None and float(explicit_noise_sigma) > 0.0:
            spatial_noise_sigma = float(explicit_noise_sigma)
        else:
            spatial_noise_sigma = auto_noise_sigma

        print(
            f"[SpatialFusion] Reference noise sigma (Taichi Vision GPU-Native): {spatial_noise_sigma:.6f}"
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
        spatial_scratch = SpatialScratchCache()
    else:
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

        ref_work_rgb_np = np.transpose(
            ref_work_rgb_hwc_gpu.to_numpy(), (2, 0, 1)
        ).astype(
            np.float32
        )  # [3, work_h, work_w]

        if ref_work_rgb_hwc_gpu is not ref_analysis_gpu:
            ref_work_rgb_hwc_gpu.destroy()

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
        ref_analysis_gpu,
        work_scale=work_scale,
        full_shape=(target_h, target_w),
        alignment_config=alignment_config,
    )

    if ref_analysis_gpu is not ref_gpu:
        ref_analysis_gpu.destroy()

    # ------------------------------------------------------------------
    # PHASE 5: Initialize GPU accumulators with 100% True Linear RAW Reference
    # ------------------------------------------------------------------
    # Directly use ref_gpu as sum_img_gpu accumulator to save 144MB VRAM
    sum_img_gpu = ref_gpu
    if weight_engine == "spatial_fusion":
        weight_sum_gpu = engine.upload(np.ones((target_h, target_w), dtype=np.float32))
    else:
        # FusionNet/WeightNet outputs a 3-channel (vec3) weightmap [H, W, 3]
        weight_sum_gpu = engine.upload(np.ones((target_h, target_w, 3), dtype=np.float32))

    alpha_total = 0.0
    total_supp = num_images - 1

    # ------------------------------------------------------------------
    # PHASE 6: Asynchronous Multi-Stage Flow Coordinator Pipeline
    # ------------------------------------------------------------------
    # Stage 1: Preloader Thread   -> preloaded_queue (maxsize=batch_queue, Host RAM)
    # Stage 2: Alignment Thread   -> aligned_queue   (maxsize=1, 1 GPU Frame in-flight)
    # Stage 3: Weight Inference   -> weighted_queue  (maxsize=1, 1 GPU Frame in-flight)
    # Stage 4: GPU Blending (Main Thread) consumes weighted_queue
    # ------------------------------------------------------------------
    q_depth = max(1, int(batch_queue))
    if progress_callback:
        progress_callback(
            PROGRESS_MERGE_MIN,
            ui="Menyiapkan Pipeline...",
            console=f"Memulai Pipeline Asynchronous Flow (host_queue={q_depth}, gpu_in_flight=1)...",
        )

    _SENTINEL = object()
    preloaded_queue = queue.Queue(maxsize=q_depth)  # Host RAM queue (0 MB VRAM)
    aligned_queue = queue.Queue(maxsize=1)          # Aligned queue (strictly 1 GPU frame in-flight max)
    weighted_queue = queue.Queue(maxsize=1)         # Weighted queue (strictly 1 GPU frame in-flight max)

    print(
        f"[GPU Pipeline] Universal Multi-Stage Queue initialized: "
        f"host_queue={q_depth}, gpu_in_flight=1 (Safe VRAM footprint active)"
    )

    pipeline_error = None
    pipeline_lock = threading.Lock()
    gpu_hardware_lock = threading.Lock()

    def _is_stopped():
        if stop_event is not None:
            if hasattr(stop_event, "is_set"):
                if stop_event.is_set():
                    return True
            elif callable(stop_event):
                if stop_event():
                    return True
        return False

    def _set_error(exc):
        nonlocal pipeline_error
        import traceback
        traceback.print_exc()
        with pipeline_lock:
            if pipeline_error is None:
                pipeline_error = exc

    # ------------------------------------------------------------------
    # Worker 1: Disk Preloader (loads RAW to CPU Host RAM - 0 MB VRAM)
    # ------------------------------------------------------------------
    def _preloader_worker():
        try:
            for idx in range(1, num_images):
                if _is_stopped() or pipeline_error is not None:
                    break
                f_path = image_paths[idx]
                f_name = Path(f_path).name
                s_np = load_rgb_linear_image(f_path, is_raw=is_raw)
                if s_np.shape[:2] != (target_h, target_w):
                    s_np = np.ascontiguousarray(
                        taichi_aot.resize(
                            s_np, (target_w, target_h), interpolation=taichi_aot.INTER_LINEAR
                        ),
                        dtype=np.float32,
                    )

                while not _is_stopped():
                    if pipeline_error is not None:
                        del s_np
                        return
                    try:
                        preloaded_queue.put((idx, f_name, s_np), timeout=0.05)
                        break
                    except queue.Full:
                        continue
        except Exception as exc:
            _set_error(exc)
        finally:
            preloaded_queue.put(_SENTINEL)

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
            while not _is_stopped():
                if pipeline_error is not None:
                    break
                try:
                    item = preloaded_queue.get(timeout=0.05)
                except queue.Empty:
                    continue

                if item is _SENTINEL:
                    break

                curr_idx, curr_name, supp_linear_np = item

                with gpu_hardware_lock:
                    if _is_stopped():
                        del supp_linear_np
                        break
                    # Upload single frame to VRAM on demand
                    supp_linear_gpu = engine.upload(supp_linear_np)
                    del supp_linear_np

                    # Generate on-the-fly Versi 1 (Analysis High-Key) for FlowNet / WeightNet
                    if analysis_params is not None:
                        supp_analysis_gpu = apply_auto_enhance_on_gpu(
                            supp_linear_gpu, analysis_params
                        )
                    else:
                        supp_analysis_gpu = supp_linear_gpu

                    # Downscale analysis frame to work-res directly first (144MB -> 36MB or less)
                    if (work_h, work_w) != (target_h, target_w):
                        supp_analysis_work_gpu = taichi_aot.resize(
                            supp_analysis_gpu,
                            (work_w, work_h),
                            interpolation=taichi_aot.INTER_AREA,
                            return_gpu=True,
                        )
                        if supp_analysis_gpu is not supp_linear_gpu:
                            supp_analysis_gpu.destroy()
                    else:
                        supp_analysis_work_gpu = supp_analysis_gpu

                    # Apply Box Filter directly on work-res analysis frame (drastically saves VRAM)
                    if analysis_box_kernel_size > 0:
                        supp_analysis_denoised = taichi_aot.box_filter(
                            supp_analysis_work_gpu,
                            kernel_size=analysis_box_kernel_size,
                            return_gpu=True,
                        )
                        if supp_analysis_work_gpu is not supp_linear_gpu:
                            supp_analysis_work_gpu.destroy()
                        supp_analysis_work_gpu = supp_analysis_denoised

                    # Dual-Warp on GPU (Primary in full-res 12MP, Secondary directly in work-res ~36MB!)
                    supp_aligned_linear_gpu, supp_aligned_analysis_work_gpu = (
                        aligner.align_frame(
                            supp_linear_gpu,
                            analysis_frame_gpu=supp_analysis_work_gpu,
                            secondary_frame_to_warp=supp_analysis_work_gpu,
                            stop_event=stop_event,
                            return_gpu=True,
                        )
                    )
                    if supp_aligned_linear_gpu is not supp_linear_gpu:
                        supp_linear_gpu.destroy()
                    if (
                        supp_analysis_gpu is not supp_linear_gpu
                        and supp_analysis_gpu is not supp_aligned_analysis_work_gpu
                    ):
                        supp_analysis_gpu.destroy()
                    if (
                        supp_analysis_work_gpu is not supp_analysis_gpu
                        and supp_analysis_work_gpu is not supp_aligned_analysis_work_gpu
                    ):
                        supp_analysis_work_gpu.destroy()

                    if weight_engine == "spatial_fusion":
                        # SpatialFusion analyzes via AutoEnhance v1 (High-Key Analysis Mode)
                        supp_work_gray_gpu = taichi_aot.cvtColor(
                            supp_aligned_analysis_work_gpu, taichi_aot.COLOR_RGB2GRAY
                        )
                        supp_work_rgb_np = np.transpose(
                            supp_aligned_analysis_work_gpu.to_numpy(), (2, 0, 1)
                        ).astype(np.float32)
                        supp_aligned_analysis_work_gpu.destroy()
                        supp_work_item = (supp_work_gray_gpu, supp_work_rgb_np)
                    elif weight_engine == "average":
                        if supp_aligned_analysis_work_gpu is not None:
                            supp_aligned_analysis_work_gpu.destroy()
                        supp_work_item = None
                    else:
                        supp_work_item = np.transpose(
                            supp_aligned_analysis_work_gpu.to_numpy(), (2, 0, 1)
                        ).astype(np.float32)
                        supp_aligned_analysis_work_gpu.destroy()
                        engine.sync()

                    if alignment_only:
                        supp_aligned_linear_gpu.destroy()
                        _destroy_work_item(supp_work_item)
                        if progress_callback:
                            progress_callback(
                                _align_percent(curr_idx, total_supp),
                                f"Alignment: {curr_idx}/{total_supp} ({curr_name})...",
                            )
                        continue

                while not _is_stopped():
                    if pipeline_error is not None:
                        supp_aligned_linear_gpu.destroy()
                        _destroy_work_item(supp_work_item)
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
            aligned_queue.put(_SENTINEL)

    # ------------------------------------------------------------------
    # Worker 3: Weight Inference (DirectML ONNX AI or Native Taichi AOT)
    # ------------------------------------------------------------------
    def _weight_inference_worker():
        try:
            from taichi_vision.taichi_aot.engine import ensure_cuda_context
            ensure_cuda_context()
        except Exception:
            pass
        try:
            while not _is_stopped():
                if pipeline_error is not None:
                    break
                try:
                    item = aligned_queue.get(timeout=0.05)
                except queue.Empty:
                    continue

                if item is _SENTINEL:
                    break

                curr_idx, curr_name, supp_aligned_linear_gpu, supp_work_item = item

                with gpu_hardware_lock:
                    if _is_stopped():
                        supp_aligned_linear_gpu.destroy()
                        _destroy_work_item(supp_work_item)
                        break

                    if weight_engine == "spatial_fusion":
                        supp_work_gray_gpu, supp_work_rgb_np = supp_work_item
                        weight_work_2d_gpu = engine.allocate(
                            (work_h, work_w), dtype=np.float32, host_accessible=True
                        )
                        generate_spatial_weights_taichi(
                            current_image=supp_work_gray_gpu,
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
                        )
                        supp_work_gray_gpu.destroy()
                        w_2d_np = weight_work_2d_gpu.to_numpy()
                        weight_work_2d_gpu.destroy()

                        # Apply ghost penalty & cutoff on 2D weightmap
                        if ghost_penalty != 1.0:
                            w_2d_np = np.power(w_2d_np, float(ghost_penalty))
                        if ghost_cutoff > 0.0:
                            w_2d_np = np.clip(
                                (w_2d_np - float(ghost_cutoff))
                                / (1.0 - float(ghost_cutoff)),
                                0.0,
                                1.0,
                            )

                        # Pure 1-Channel (2D) Spatial Weightmap
                        w_2d_np = np.ascontiguousarray(w_2d_np, dtype=np.float32)
                        del supp_work_rgb_np
                        weight_work_item = w_2d_np
                        alpha_mean = 1.0
                    elif weight_engine == "average":
                        weight_work_item = np.ones((work_h, work_w, 3), dtype=np.float32)
                        alpha_mean = 1.0
                    else:
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
                        weight_work_item = np.ascontiguousarray(
                            np.transpose(weight_work_np, (1, 2, 0)), dtype=np.float32
                        )
                        del weight_work_np
                        engine.sync()

                while not _is_stopped():
                    if pipeline_error is not None:
                        supp_aligned_linear_gpu.destroy()
                        if hasattr(weight_work_item, "destroy"):
                            weight_work_item.destroy()
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
                        break
                    except queue.Full:
                        continue
        except Exception as exc:
            _set_error(exc)
        finally:
            weighted_queue.put(_SENTINEL)

    is_thread_affine = str(getattr(engine, "arch", "")).lower() in ("opengl", "gles")

    if is_thread_affine:
        # Context-affine backends (OpenGL/GLES) execute all GPU work synchronously on the context-owner thread
        t_preloader = threading.Thread(
            target=_preloader_worker, name="Stage1_Preloader", daemon=True
        )
        t_preloader.start()
        threads = [t_preloader]

        processed_count = 0
        try:
            while not _is_stopped():
                if pipeline_error is not None:
                    raise pipeline_error

                try:
                    item = preloaded_queue.get(timeout=0.05)
                except queue.Empty:
                    continue

                if item is _SENTINEL:
                    if pipeline_error is not None:
                        raise pipeline_error
                    break

                curr_idx, curr_name, supp_linear_np = item
                if _is_stopped():
                    del supp_linear_np
                    break

                supp_linear_gpu = engine.upload(supp_linear_np)
                del supp_linear_np

                if is_raw and analysis_params is not None:
                    supp_analysis_gpu = apply_auto_enhance_on_gpu(
                        supp_linear_gpu, analysis_params
                    )
                else:
                    supp_analysis_gpu = supp_linear_gpu

                # Downscale analysis frame to work-res directly first (144MB -> 36MB or less)
                if (work_h, work_w) != (target_h, target_w):
                    supp_analysis_work_gpu = taichi_aot.resize(
                        supp_analysis_gpu,
                        (work_w, work_h),
                        interpolation=taichi_aot.INTER_AREA,
                        return_gpu=True,
                    )
                    if supp_analysis_gpu is not supp_linear_gpu:
                        supp_analysis_gpu.destroy()
                else:
                    supp_analysis_work_gpu = supp_analysis_gpu

                # Apply Box Filter directly on work-res analysis frame (drastically saves VRAM)
                if analysis_box_kernel_size > 0:
                    supp_analysis_denoised = taichi_aot.box_filter(
                        supp_analysis_work_gpu,
                        kernel_size=analysis_box_kernel_size,
                        return_gpu=True,
                    )
                    if supp_analysis_work_gpu is not supp_linear_gpu:
                        supp_analysis_work_gpu.destroy()
                    supp_analysis_work_gpu = supp_analysis_denoised

                supp_aligned_linear_gpu, supp_aligned_analysis_work_gpu = (
                    aligner.align_frame(
                        supp_linear_gpu,
                        analysis_frame_gpu=supp_analysis_work_gpu,
                        secondary_frame_to_warp=supp_analysis_work_gpu,
                        stop_event=stop_event,
                        return_gpu=True,
                    )
                )
                if supp_aligned_linear_gpu is not supp_linear_gpu:
                    supp_linear_gpu.destroy()
                if (
                    supp_analysis_gpu is not supp_linear_gpu
                    and supp_analysis_gpu is not supp_aligned_analysis_work_gpu
                ):
                    supp_analysis_gpu.destroy()
                if (
                    supp_analysis_work_gpu is not supp_analysis_gpu
                    and supp_analysis_work_gpu is not supp_aligned_analysis_work_gpu
                ):
                    supp_analysis_work_gpu.destroy()

                if weight_engine == "spatial_fusion":
                    supp_work_gray_gpu = taichi_aot.cvtColor(
                        supp_aligned_analysis_work_gpu, taichi_aot.COLOR_RGB2GRAY
                    )
                    supp_work_rgb_np = np.transpose(
                        supp_aligned_analysis_work_gpu.to_numpy(), (2, 0, 1)
                    ).astype(np.float32)
                    supp_aligned_analysis_work_gpu.destroy()

                    weight_work_2d_gpu = engine.allocate(
                        (work_h, work_w), dtype=np.float32, host_accessible=True
                    )
                    generate_spatial_weights_taichi(
                        current_image=supp_work_gray_gpu,
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
                    )
                    supp_work_gray_gpu.destroy()
                    w_2d_np = weight_work_2d_gpu.to_numpy()
                    weight_work_2d_gpu.destroy()

                    # Apply ghost penalty & cutoff on 2D weightmap
                    if ghost_penalty != 1.0:
                        w_2d_np = np.power(w_2d_np, float(ghost_penalty))
                    if ghost_cutoff > 0.0:
                        w_2d_np = np.clip(
                            (w_2d_np - float(ghost_cutoff))
                            / max(1e-5, (1.0 - float(ghost_cutoff))),
                            0.0,
                            1.0,
                        )

                    # Pure 1-Channel (2D) Spatial Weightmap
                    w_2d_np = np.ascontiguousarray(w_2d_np, dtype=np.float32)
                    del supp_work_rgb_np
                    weight_work_item = w_2d_np
                    alpha_mean = 1.0
                elif weight_engine == "average":
                    if supp_aligned_analysis_work_gpu is not None:
                        supp_aligned_analysis_work_gpu.destroy()
                    weight_work_item = np.ones((work_h, work_w, 3), dtype=np.float32)
                    alpha_mean = 1.0
                else:
                    supp_work_rgb_np = np.transpose(
                        supp_aligned_analysis_work_gpu.to_numpy(), (2, 0, 1)
                    ).astype(np.float32)
                    supp_aligned_analysis_work_gpu.destroy()
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
                    weight_work_item = np.ascontiguousarray(
                        np.transpose(weight_work_np, (1, 2, 0)), dtype=np.float32
                    )
                    del weight_work_np

                processed_count += 1
                alpha_total += alpha_mean

                if progress_callback:
                    align_lbl = alignment_plan if alignment_plan not in ("none", "off", "") else "No Alignment"
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

                _gpu_blend_frame(
                    sum_img_gpu,
                    weight_sum_gpu,
                    supp_aligned_linear_gpu,
                    weight_work_gpu,
                )

                supp_aligned_linear_gpu.destroy()
                weight_work_gpu.destroy()
                if weight_engine != "spatial_fusion":
                    engine.sync()

                print(
                    f"[GPU Flow Coordinator] Frame {curr_idx}/{total_supp} ({curr_name}) blended "
                    f"(alpha={alpha_mean:.3f})"
                )
        finally:
            t_preloader.join(timeout=1.0)
    else:
        # Launch background stages for thread-safe backends (CUDA/Vulkan)
        t_preloader = threading.Thread(
            target=_preloader_worker, name="Stage1_Preloader", daemon=True
        )
        t_aligner = threading.Thread(
            target=_alignment_worker, name="Stage2_Aligner", daemon=True
        )
        threads = [t_preloader, t_aligner]

        t_weight = None
        if not alignment_only and (
            session is not None or weight_engine in ("spatial_fusion", "average")
        ):
            t_weight = threading.Thread(
                target=_weight_inference_worker, name="Stage3_Weight", daemon=True
            )
            t_weight.start()
            threads.append(t_weight)

        t_preloader.start()
        t_aligner.start()

        # If only alignment is requested, wait for stages and return reference image
        if alignment_only:
            t_preloader.join()
            t_aligner.join()
            ref_out = ref_gpu.to_numpy()
            aligner.close()
            ref_gpu.destroy()
            sum_img_gpu.destroy()
            weight_sum_gpu.destroy()
            if ref_spatial_gray_gpu is not None:
                ref_spatial_gray_gpu.destroy()
            if spatial_rows_gpu is not None:
                spatial_rows_gpu.destroy()
            if spatial_cols_gpu is not None:
                spatial_cols_gpu.destroy()
            return ref_out, 1.0

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
                    align_lbl = alignment_plan if alignment_plan not in ("none", "off", "") else "No Alignment"
                    progress_callback(
                        _merge_percent(processed_count, total_supp),
                        ui=f"Memproses {curr_idx}/{total_supp}...",
                        console=f"Memproses frame {curr_idx}/{total_supp} ({curr_name}) [{align_lbl} + Fusion]...",
                    )

                with gpu_hardware_lock:
                    if _is_stopped():
                        supp_aligned_linear_gpu.destroy()
                        if hasattr(weight_work_item, "destroy"):
                            weight_work_item.destroy()
                        break

                    if isinstance(weight_work_item, taichi_aot.TaichiGPUBuffer):
                        weight_work_gpu = weight_work_item
                    else:
                        weight_work_gpu = engine.upload(weight_work_item)
                        del weight_work_item

                    _gpu_blend_frame(
                        sum_img_gpu,
                        weight_sum_gpu,
                        supp_aligned_linear_gpu,
                        weight_work_gpu,
                    )

                    supp_aligned_linear_gpu.destroy()
                    weight_work_gpu.destroy()
                    if weight_engine != "spatial_fusion":
                        engine.sync()

                print(
                    f"[GPU Flow Coordinator] Frame {curr_idx}/{total_supp} ({curr_name}) blended "
                    f"(alpha={alpha_mean:.3f}, in_flight={weighted_queue.qsize()})"
                )

        finally:
            # Drain and destroy any remaining GPU buffers in queues immediately
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

            t_preloader.join(timeout=0.2)
            t_aligner.join(timeout=0.2)
            if t_weight is not None:
                t_weight.join(timeout=0.2)

            if _is_stopped():
                try:
                    sum_img_gpu.destroy()
                    weight_sum_gpu.destroy()
                    ref_gpu.destroy()
                    aligner.close()
                    if ref_spatial_gray_gpu is not None:
                        ref_spatial_gray_gpu.destroy()
                    if spatial_rows_gpu is not None:
                        spatial_rows_gpu.destroy()
                    if spatial_cols_gpu is not None:
                        spatial_cols_gpu.destroy()
                except Exception:
                    pass
                try:
                    engine.sync()
                    engine.get_device_block_cache().clear()
                except Exception:
                    pass
                gc.collect()

    if _is_stopped():
        print("[GPU Pipeline] Process cancelled by user. Discarded in-flight computation & released GPU memory.")
        return None, 0.0

    # ------------------------------------------------------------------
    # PHASE 7: Final Linear Normalization (Pure Linear RAW Data)
    # ------------------------------------------------------------------
    if progress_callback:
        progress_callback(
            PROGRESS_FINALIZE_MAX,
            ui="Menyelesaikan proses...",
            console="Finalisasi GPU-resident fusion & normalisasi pembagian bobot...",
        )

    # Normalization with reference fallback
    # Directly passing ref_gpu (already resident in VRAM, 0 overhead!)
    from taichi_vision.taichi_algorithm.spatial_fusion import (
        mean_division_vec3_weight_taichi,
    )

    if getattr(weight_sum_gpu, "ndim", 2) == 2 or (len(weight_sum_gpu.shape) == 2):
        # Broadcast 2D weight sum to 3D for vector division kernel
        weight_sum_3d = taichi_aot.upload(
            np.ascontiguousarray(
                np.repeat(weight_sum_gpu.to_numpy()[:, :, None], 3, axis=2),
                dtype=np.float32,
            )
        )
        _final_linear_gpu = mean_division_vec3_weight_taichi(
            sum_img=sum_img_gpu,
            sum_weight=weight_sum_3d,
            ref_img=ref_gpu,
        )
        weight_sum_3d.destroy()
    else:
        _final_linear_gpu = mean_division_vec3_weight_taichi(
            sum_img=sum_img_gpu,
            sum_weight=weight_sum_gpu,
            ref_img=ref_gpu,
        )

    result_hwc = np.ascontiguousarray(
        _final_linear_gpu.to_numpy(), dtype=np.float32
    )
    _final_linear_gpu.destroy()

    # Cleanup GPU resources and flush buffer pool back to baseline
    try:
        sum_img_gpu.destroy()
        weight_sum_gpu.destroy()
        ref_gpu.destroy()
        aligner.close()
        if ref_spatial_gray_gpu is not None:
            ref_spatial_gray_gpu.destroy()
        if spatial_rows_gpu is not None:
            spatial_rows_gpu.destroy()
        if spatial_cols_gpu is not None:
            spatial_cols_gpu.destroy()
    except Exception:
        pass
    del ref_work_rgb_np
    try:
        engine.sync()
        if hasattr(engine, "buffer_pool") and engine.buffer_pool is not None:
            engine.buffer_pool.clear()
        if hasattr(engine, "_staging_pool") and engine._staging_pool is not None:
            engine._staging_pool.clear()
        engine.get_device_block_cache().clear()
    except Exception:
        pass
    gc.collect()

    mean_alpha = alpha_total / max(1, total_supp)
    print(
        f"[GPU Pipeline] Complete: shape={result_hwc.shape} "
        f"mean_alpha={mean_alpha:.4f} (VRAM drained to baseline)"
    )

    return result_hwc, mean_alpha


# Canonical alias
run_resident_pipeline = run_gpu_resident_pipeline

