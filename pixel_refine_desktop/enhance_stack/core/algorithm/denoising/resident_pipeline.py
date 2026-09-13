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
from typing import Any, Callable, Optional, Sequence, Tuple, Union
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
            # Keep the conversion in the Taichi Vision/native cast boundary.
            # Hamilton currently emits f32, but this compatibility branch is
            # still needed for older uint8/uint16 demosaic artifacts.
            converted_gpu = taichi_aot.cast(
                rgb_gpu, np.float32, host_accessible=True
            )
            if converted_gpu is not rgb_gpu:
                rgb_gpu.destroy()
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


def apply_clahe_16bit_reference(
    rgb_chw: np.ndarray,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8),
) -> Tuple[np.ndarray, np.ndarray]:
    """Apply CLAHE to Reference Luminance and precompute 2D transfer ratio map.
    Uses Taichi Vision GPU-accelerated CLAHE primarily, falling back to OpenCV if needed.

    Returns:
        enhanced_chw: np.ndarray [3, H, W] float32 enhanced reference frame.
        transfer_map: np.ndarray [H, W] float32 precomputed luminance boost ratio map.
    """
    img = np.ascontiguousarray(rgb_chw, dtype=np.float32)
    lum = 0.2126 * img[0] + 0.7152 * img[1] + 0.0722 * img[2]

    lum_clahe = None
    try:
        from taichi_vision import taichi_aot

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


class BlockMatchingResidentAligner:
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
        from taichi_vision.taichi_algorithm.pyramid.pyramid import (
            build_image_pyramid_gpu,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.block_matching_gpu import (
            BLOCK_MATCHING_GPU_PRESETS,
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
        return {
            "winSize": (win_size, win_size),
            "maxLevel": max(0, int(self.config.get("max_level", 2))),
            "criteria": (
                3,
                max(1, int(self.config.get("iterations", 1))),
                float(self.config.get("epsilon", 0.02)),
            ),
            "grid_step": max(4, int(self.config.get("grid_step", 48))),
            "border_margin": max(0, int(self.config.get("border_margin", 8))),
            "motion_mode": str(self.config.get("motion_mode", "fast")),
            "dense_mode": "blocky_clamped",
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
    ):
        from taichi_vision import taichi_aot
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
                supp_gray_gpu.destroy()
                supp_gray_gpu = resized
            flow_gpu = calcOpticalFlowBlockMatching(
                self.ref_gray_gpu,
                supp_gray_gpu,
                **self._flow_params(),
                return_gpu=True,
                reference_pyramid=self.reference_pyramid,
            )
            if isinstance(flow_gpu, tuple):
                flow_gpu = flow_gpu[0]
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
            return warped_primary, warped_secondary
        finally:
            if flow_gpu is not None and hasattr(flow_gpu, "destroy"):
                flow_gpu.destroy()
            if supp_gray_gpu is not None and hasattr(supp_gray_gpu, "destroy"):
                supp_gray_gpu.destroy()

    def close(self):
        # L0 is the same object as ``ref_gray_gpu``; destroy every pyramid
        # level exactly once so the allocator can reuse or retire it safely.
        for buffer in getattr(self, "reference_pyramid", ()):
            try:
                if buffer is not None and hasattr(buffer, "destroy"):
                    buffer.destroy()
            except Exception:
                pass
        self.reference_pyramid = ()
        self.ref_gray_gpu = None


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

        self.ref_gray_gpu = ref_gray_gpu
        self.feature_type = "akaze" if "akaze" in self.feature_type else "ofb"
        self._feature_reference_cache = None
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
                # The cache owns only derived keypoints/descriptors.  The
                # grayscale reference itself is no longer needed per frame.
                self.ref_gray_gpu.destroy()
                self.ref_gray_gpu = None
                print(
                    f"[GPU Pipeline] {feature_arch.upper()} {self.feature_type.upper()} "
                    f"reference cache ready "
                    f"(levels={self._feature_reference_cache.num_levels}, one-readback)"
                )
        except Exception as exc:
            self._feature_reference_cache = None
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
    ):
        from taichi_vision import taichi_aot

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
            supp_gray_gpu.destroy()
            supp_gray_gpu = supp_gray_work

        try:
            if self._feature_reference_cache is not None:
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
            supp_gray_gpu.destroy()

        H_matrix = None
        scale_x = self.target_w / float(self.work_w)
        scale_y = self.target_h / float(self.work_h)
        if matched is not None and len(matched) >= 2:
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
                H_candidate, inlier_mask = taichi_aot.find_homography(
                    pts_supp,
                    pts_ref,
                    method="RANSAC",
                    ransacReprojThreshold=reproj_threshold,
                    n_hypotheses=ransac_hypotheses,
                    max_iters=ransac_iters,
                    return_gpu=False,
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
        cache = getattr(self, "_feature_reference_cache", None)
        if cache is not None:
            try:
                cache.close()
            except Exception:
                pass
        self._feature_reference_cache = None
        ref_gray_gpu = getattr(self, "ref_gray_gpu", None)
        if ref_gray_gpu is not None and hasattr(ref_gray_gpu, "destroy"):
            ref_gray_gpu.destroy()
        self.ref_gray_gpu = None


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
    elif plan_clean in ("sift", "lightglue", "light glue"):
        raise ValueError(
            f"Unsupported resident feature aligner '{alignment_plan}'. "
            "Use OFB/ORB or AKAZE; SIFT and LightGlue were removed from the native path."
        )
    else:
        print(f"[GPU Pipeline] Aligner: Dense Optical Flow ({plan_clean})")
        from .fusionet_engine.flownet_inference import AOTOpticalFlowAligner

        return AOTOpticalFlowAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            tile_size=16,
            noise_score=noise_score,
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


def _gpu_blend_frame(sum_img_gpu, weight_sum_gpu, supp_aligned_gpu, weight_work_gpu):
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
    flownet_work_scale: Optional[float] = None,
    weightnet_work_scale: Optional[float] = None,
    tile_size: int = 512,
    overlap: float = 0.30,
    ghost_penalty: float = 1.0,
    ghost_cutoff: float = 0.05,
    chroma_sensitivity: float = 6.0,
    is_raw: bool = False,
    storage_mode: str = "direct",
    alignment_only: bool = False,
    batch_queue: int = 4,
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
        tile_size: Tile size for weight computation.
        overlap: Tile overlap ratio.
        ghost_penalty: Ghost artifact suppression exponent.
        ghost_cutoff: Ghost cutoff threshold.
        chroma_sensitivity: Color deviation protection scale.
        is_raw: Whether images are RAW/DNG.
        storage_mode: "direct" (RAM/VRAM stream).
        alignment_only: If True, executes pure alignment without blending.
        batch_queue: Number of preloaded frames in Host RAM (default 4).
        batch_plan: Optional comparison-frame ranges from MFDenoiser. The
            reference frame (index 0) remains resident for the whole call.
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
    from taichi_vision.taichi_algorithm.spatial_fusion import (
        postprocess_spatial_weight_taichi,
    )

    engine = get_engine()
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

    if session is None and weight_engine == "fusionet" and not alignment_only:
        from .fusionet_engine.weightnet_inference import DEFAULT_WEIGHTNET_ONNX, load_weightnet_onnx
        session = load_weightnet_onnx(DEFAULT_WEIGHTNET_ONNX, runtime="dml", patch_size=tile_size)

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
    # Parameters are computed once from the reference and reused for every
    # support frame.  The linear fusion buffers themselves remain untouched.
    analysis_params = analyze_auto_enhance_on_gpu(ref_gpu, mode="analysis")
    print(
        f"[GPU Pipeline] AutoEnhance (analysis): Gain={analysis_params['gain']:.2f}x "
        "(reference parameters reused for alignment/WeightNet analysis)"
    )

    # ------------------------------------------------------------------
    # PHASE 3: Create Analysis Reference & Work-Resolution Copy
    # ------------------------------------------------------------------
    flow_scale = float(flownet_work_scale) if flownet_work_scale is not None else float(work_scale)
    weight_scale = float(weightnet_work_scale) if weightnet_work_scale is not None else float(work_scale)

    max_dimension = max(target_h, target_w)
    if max_dimension > 2048:
        flow_capped_scale = min(flow_scale, 2048.0 / float(max_dimension))
        weight_capped_scale = min(weight_scale, 2048.0 / float(max_dimension))
    else:
        flow_capped_scale = flow_scale
        weight_capped_scale = weight_scale

    flow_work_h = max(32, int(target_h * flow_capped_scale))
    flow_work_w = max(32, int(target_w * flow_capped_scale))
    weight_work_h = max(32, int(target_h * weight_capped_scale))
    weight_work_w = max(32, int(target_w * weight_capped_scale))

    work_h, work_w = weight_work_h, weight_work_w

    print(
        f"[GPU Pipeline] Multi-Scale Setup: FlowNet Res=({flow_work_h}, {flow_work_w}, scale={flow_capped_scale:.2f}) | "
        f"WeightNet Res=({weight_work_h}, {weight_work_w}, scale={weight_capped_scale:.2f})"
    )

    # Downscale linear reference frame to flow-work-res directly FIRST across all backends (144MB -> 9-36MB)
    # This avoids running heavy 12MP auto-enhance on any backend!
    if (flow_work_h, flow_work_w) != (target_h, target_w):
        ref_flow_linear_gpu = taichi_aot.resize(
            ref_gpu,
            (flow_work_w, flow_work_h),
            interpolation=taichi_aot.INTER_AREA,
            return_gpu=True,
        )
    else:
        ref_flow_linear_gpu = ref_gpu

    # Create high-contrast analysis copy (Versi 1) on work-res for feature alignment & weight computation
    if analysis_params is not None:
        ref_analysis_flow_gpu = apply_auto_enhance_on_gpu(
            ref_flow_linear_gpu, analysis_params
        )
        if ref_flow_linear_gpu is not ref_gpu:
            ref_flow_linear_gpu.destroy()
    else:
        ref_analysis_flow_gpu = ref_flow_linear_gpu

    ref_analysis_gpu = ref_analysis_flow_gpu

    # Estimate noise from the same AutoEnhance analysis reference used by
    # FusionNet/FlowNet and SpatialFusion.  The public estimator returns a
    # tuple; only the normalized score drives the pipeline.
    ref_noise_score = None
    noise_estimation_source = "autoenhanced_analysis"
    try:
        from taichi_vision.taichi_algorithm.enhancement.estimate_noise import (
            estimate_noise,
        )

        ref_noise_score, _ = estimate_noise(ref_analysis_gpu)
        ref_noise_score = float(ref_noise_score)
        print(
            f"[GPU Pipeline] Reference noise estimate (Taichi Vision): "
            f"score={ref_noise_score:.6f} "
            f"source={noise_estimation_source}"
        )
    except Exception as e_noise:
        print(f"[GPU Pipeline] Noise estimation note: {e_noise}")

    # Noise-Adaptive Ghost Penalty (reuses the single analysis score):
    # - Score <= 0.50 (low-to-moderate noise): crisp ghost penalty = 2.5
    # - Score in (0.50, 0.90): smooth cosine transition dropping from 2.5 down to 1.0
    # - Score >= 0.90 (extreme noise): generous ghost penalty = 1.0
    try:
        if ref_noise_score is None:
            raise RuntimeError("analysis reference noise score unavailable")
        if ref_noise_score <= 0.50:
            active_ghost_penalty = 2.5
        elif ref_noise_score < 0.90:
            t = (ref_noise_score - 0.50) / 0.40  # Normalized progress [0, 1]
            factor = 0.5 * (1.0 + np.cos(np.pi * t))  # Cosine ease-in-out
            active_ghost_penalty = float(1.0 + (2.5 - 1.0) * factor)
        else:
            active_ghost_penalty = 1.0

        print(
            f"[GPU Pipeline] Noise-Adaptive Ghost Penalty: score={ref_noise_score:.4f} -> "
            f"penalty={active_ghost_penalty:.2f} (source={noise_estimation_source}, "
            f"configured base={ghost_penalty})"
        )
        ghost_penalty = active_ghost_penalty
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
    spatial_weight_work_gpu = None
    # Spatial weight generation writes one work map; postprocessing writes to
    # one of these two persistent destinations.  The weighted queue has depth
    # one, so ping-pong destinations prevent the producer from overwriting the
    # map that the blend stage is still consuming.
    spatial_weight_post_a_gpu = None
    spatial_weight_post_b_gpu = None
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
        if ref_work_v1_gpu is not ref_analysis_gpu:
            ref_work_v1_gpu.destroy()

        # Estimasi noise 100% GPU-Native Taichi Vision (Wavelet Subband Minima & Patch Subspace)
        # The canonical value passed to SpatialFusion is the normalized
        # estimator score [0, 1], matching both CPU and GPU public APIs.
        if ref_noise_score is not None:
            auto_noise_sigma = ref_noise_score
            spatial_sigma_mode = "score"
            auto_noise_sigma = float(
                np.clip(
                    auto_noise_sigma,
                    1e-4,
                    0.99999,
                )
            )
        else:
            # Do not run a second estimate at another resolution.  A failed
            # reference estimate uses the conservative existing default.
            auto_noise_sigma = 0.025
            spatial_sigma_mode = "fallback"

        explicit_noise_sigma = cfg.get("noise_sigma")
        if explicit_noise_sigma is not None and float(explicit_noise_sigma) > 0.0:
            spatial_noise_sigma = float(explicit_noise_sigma)
            spatial_sigma_mode = "explicit"
        else:
            spatial_noise_sigma = auto_noise_sigma

        print(
            f"[SpatialFusion] Kernel parameters: tile={spatial_tile_h} "
            f"overlap={spatial_overlap:.3f} "
            f"motion_sensitivity={spatial_motion_sens:.3f} "
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
        # One reusable output for spatial weights.  Allocating this per frame
        # creates a new allocator request/bucket even though the shape never
        # changes during a burst.
        spatial_weight_work_gpu = engine.allocate(
            (work_h, work_w), dtype=np.float32, host_accessible=False
        )
        spatial_weight_post_a_gpu = engine.allocate(
            (work_h, work_w), dtype=np.float32, host_accessible=False
        )
        spatial_weight_post_b_gpu = engine.allocate(
            (work_h, work_w), dtype=np.float32, host_accessible=False
        )
        spatial_scratch = SpatialScratchCache()
    else:
        # Work-resolution copy for ONNX WeightNet inference
        if (weight_work_h, weight_work_w) != (flow_work_h, flow_work_w):
            ref_work_rgb_hwc_gpu = taichi_aot.resize(
                ref_analysis_flow_gpu,
                (weight_work_w, weight_work_h),
                interpolation=taichi_aot.INTER_AREA,
                return_gpu=True,
            )
        else:
            ref_work_rgb_hwc_gpu = ref_analysis_flow_gpu

        ref_work_rgb_np = np.transpose(
            ref_work_rgb_hwc_gpu.to_numpy(), (2, 0, 1)
        ).astype(
            np.float32
        )  # [3, weight_work_h, weight_work_w]

        # 16-bit Luminance CLAHE on Reference: Precompute 2D transfer ratio map for Support frames
        ref_transfer_map = None
        try:
            ref_work_rgb_np, ref_transfer_map = apply_clahe_16bit_reference(
                ref_work_rgb_np, clip_limit=2.0, tile_grid_size=(8, 8)
            )
        except Exception as e_clahe:
            print(f"[GPU Pipeline] WeightNet Ref CLAHE note: {e_clahe}")

        if ref_work_rgb_hwc_gpu is not ref_analysis_flow_gpu:
            ref_work_rgb_hwc_gpu.destroy()

    def _is_persistent_spatial_weight(buf):
        return weight_engine == "spatial_fusion" and (
            buf is spatial_weight_work_gpu
            or buf is spatial_weight_post_a_gpu
            or buf is spatial_weight_post_b_gpu
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

    if ref_analysis_flow_gpu is not ref_gpu:
        ref_analysis_flow_gpu.destroy()

    # ------------------------------------------------------------------
    # PHASE 5: Initialize GPU accumulators with 100% True Linear RAW Reference
    # ------------------------------------------------------------------
    # Directly use ref_gpu as sum_img_gpu accumulator to save 144MB VRAM
    sum_img_gpu = ref_gpu
    if weight_engine == "spatial_fusion":
        weight_sum_gpu = engine.upload(np.ones((target_h, target_w), dtype=np.float32))
    else:
        # FusionNet/WeightNet outputs a 3-channel (vec3) weightmap [H, W, 3]
        weight_sum_gpu = engine.upload(
            np.ones((target_h, target_w, 3), dtype=np.float32)
        )

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
    is_cpu_backend = str(getattr(engine, "arch", "")).lower() == "cpu"
    is_thread_affine = str(getattr(engine, "arch", "")).lower() in ("opengl", "gles")
    # When MFDenoiser provides a balanced plan, derive staging depth from the
    # actual plan instead of treating ``batch_queue`` as a second batching
    # policy.  The legacy argument remains accepted for API compatibility.
    planned_batch_size = max(
        (int(end) - int(start) for start, end in (batch_plan or ())),
        default=max(1, int(batch_queue)),
    )
    if is_cpu_backend or is_thread_affine:
        q_depth = 1
    elif is_raw:
        # RAW support frames are CPU-staged before the single GPU uploader;
        # use the generated batch size as the sole staging policy.
        q_depth = max(1, planned_batch_size)
    else:
        q_depth = max(1, planned_batch_size)

    if progress_callback:
        progress_callback(
            PROGRESS_MERGE_MIN,
            ui="Menyiapkan Pipeline...",
            console=f"Memulai Pipeline Asynchronous Flow (host_queue={q_depth}, gpu_in_flight=1)...",
        )

    _SENTINEL = object()
    preloaded_queue = queue.Queue(maxsize=q_depth)  # Host RAM queue (0 MB VRAM)
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
                if is_raw:
                    # Stage support RAW frames on the host while another frame
                    # is being aligned.  GPU demosaic allocates a temporary
                    # Bayer/input buffer plus the RGB output; doing that in
                    # this producer can overlap the active remap and exceed
                    # the 2 GB device heap even with a queue depth of one.
                    # The uploader promotes exactly one staged frame to VRAM.
                    s_input = load_rgb_linear_image(f_path, is_raw=True)
                    if s_input.shape[:2] != (target_h, target_w):
                        s_resized = taichi_aot.resize(
                            s_input,
                            (target_w, target_h),
                            interpolation=taichi_aot.INTER_LINEAR,
                        )
                        s_input = np.ascontiguousarray(s_resized, dtype=np.float32)
                else:
                    s_input = load_rgb_linear_image(f_path, is_raw=False)
                    if s_input.shape[:2] != (target_h, target_w):
                        s_input = np.ascontiguousarray(
                            taichi_aot.resize(
                                s_input,
                                (target_w, target_h),
                                interpolation=taichi_aot.INTER_LINEAR,
                            ),
                            dtype=np.float32,
                        )

                queued = False
                while not _is_stopped():
                    if pipeline_error is not None:
                        _destroy_work_item(s_input)
                        return
                    try:
                        preloaded_queue.put((idx, f_name, s_input), timeout=0.05)
                        queued = True
                        break
                    except queue.Full:
                        continue
                if not queued:
                    _destroy_work_item(s_input)
        except Exception as exc:
            _set_error(exc)
        finally:
            preloaded_queue.put(_SENTINEL)

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
            while not _is_stopped():
                if pipeline_error is not None:
                    break
                try:
                    item = preloaded_queue.get(timeout=0.05)
                except queue.Empty:
                    continue

                if item is _SENTINEL:
                    break

                curr_idx, curr_name, supp_linear_input = item

                with gpu_hardware_lock:
                    if _is_stopped():
                        _destroy_work_item(supp_linear_input)
                        break
                    # Upload single frame to VRAM in background (PCIe DMA transfer)
                    if isinstance(supp_linear_input, TaichiGPUBuffer):
                        supp_linear_gpu = supp_linear_input
                    else:
                        supp_linear_gpu = engine.upload(supp_linear_input)
                        del supp_linear_input

                    # Pre-downscale linear frame to FlowNet work-res directly in VRAM (144MB -> 9-36MB)
                    if (flow_work_h, flow_work_w) != (target_h, target_w):
                        supp_linear_flow_gpu = taichi_aot.resize(
                            supp_linear_gpu,
                            (flow_work_w, flow_work_h),
                            interpolation=taichi_aot.INTER_AREA,
                            return_gpu=True,
                        )
                    else:
                        supp_linear_flow_gpu = supp_linear_gpu

                    # Generate on-the-fly Versi 1 (Analysis High-Key) on work-res directly in VRAM
                    if analysis_params is not None:
                        supp_analysis_flow_gpu = apply_auto_enhance_on_gpu(
                            supp_linear_flow_gpu, analysis_params
                        )
                        if supp_linear_flow_gpu is not supp_linear_gpu:
                            supp_linear_flow_gpu.destroy()
                    else:
                        supp_analysis_flow_gpu = supp_linear_flow_gpu

                    # Prepare secondary frame to warp at WeightNet work-res in VRAM
                    if (weight_work_h, weight_work_w) != (flow_work_h, flow_work_w):
                        supp_analysis_sec_gpu = taichi_aot.resize(
                            supp_analysis_flow_gpu,
                            (weight_work_w, weight_work_h),
                            interpolation=taichi_aot.INTER_AREA,
                            return_gpu=True,
                        )
                    else:
                        supp_analysis_sec_gpu = supp_analysis_flow_gpu

                while not _is_stopped():
                    if pipeline_error is not None:
                        supp_linear_gpu.destroy()
                        if (
                            supp_analysis_flow_gpu is not supp_analysis_sec_gpu
                            and supp_analysis_flow_gpu is not supp_linear_gpu
                        ):
                            supp_analysis_flow_gpu.destroy()
                        if supp_analysis_sec_gpu is not supp_linear_gpu:
                            supp_analysis_sec_gpu.destroy()
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
            vram_queue.put(_SENTINEL)

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
                    if _is_stopped():
                        supp_linear_gpu.destroy()
                        if (
                            supp_analysis_flow_gpu is not supp_analysis_sec_gpu
                            and supp_analysis_flow_gpu is not supp_linear_gpu
                        ):
                            supp_analysis_flow_gpu.destroy()
                        if supp_analysis_sec_gpu is not supp_linear_gpu:
                            supp_analysis_sec_gpu.destroy()
                        break

                    # Dual-Warp on GPU (Primary in full-res 12MP, Secondary directly in weight-res)
                    # 100% Taichi Vision GPU-resident, zero OpenCV, zero numpy round-trip
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
                        supp_linear_gpu.destroy()
                    if (
                        supp_analysis_flow_gpu is not supp_analysis_sec_gpu
                        and supp_analysis_flow_gpu is not supp_aligned_sec_gpu
                    ):
                        supp_analysis_flow_gpu.destroy()
                    if supp_analysis_sec_gpu is not supp_aligned_sec_gpu:
                        supp_analysis_sec_gpu.destroy()

                    if weight_engine == "spatial_fusion":
                        # SpatialFusion analyzes via AutoEnhance v1 (High-Key Analysis Mode)
                        supp_work_gray_gpu = taichi_aot.cvtColor(
                            supp_aligned_sec_gpu, taichi_aot.COLOR_RGB2GRAY
                        )
                        supp_aligned_sec_gpu.destroy()
                        supp_work_item = (supp_work_gray_gpu, None)
                    elif weight_engine == "average":
                        if supp_aligned_sec_gpu is not None:
                            supp_aligned_sec_gpu.destroy()
                        supp_work_item = None
                    else:
                        # DirectML ONNX requires CPU array: pull bytes directly to avoid holding GPU lock during transposition
                        raw_np = supp_aligned_sec_gpu.to_numpy()
                        supp_aligned_sec_gpu.destroy()

                if raw_np is not None:
                    supp_work_item = np.transpose(raw_np, (2, 0, 1)).astype(np.float32)
                    del raw_np

                if alignment_only:
                    supp_aligned_linear_gpu.destroy()
                    _destroy_work_item(supp_work_item)
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

                if _is_stopped():
                    with gpu_hardware_lock:
                        supp_aligned_linear_gpu.destroy()
                    _destroy_work_item(supp_work_item)
                    break

                if weight_engine == "spatial_fusion":
                    with gpu_hardware_lock:
                        supp_work_gray_gpu, _ = supp_work_item
                        weight_work_2d_gpu = spatial_weight_work_gpu
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
                        # Keep the exact historical power/clip semantics on
                        # the active backend.  The two persistent destinations
                        # are alternated because weighted_queue has one slot.
                        weight_work_gpu = (
                            spatial_weight_post_a_gpu
                            if (curr_idx & 1) == 0
                            else spatial_weight_post_b_gpu
                        )
                        postprocess_spatial_weight_taichi(
                            weight_work_2d_gpu,
                            ghost_penalty=ghost_penalty,
                            ghost_cutoff=ghost_cutoff,
                            dst=weight_work_gpu,
                        )
                        weight_work_item = weight_work_gpu
                        alpha_mean = 1.0
                elif weight_engine == "average":
                    weight_work_item = np.ones(
                        (work_h, work_w, 3), dtype=np.float32
                    )
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
                    weight_work_item = np.ascontiguousarray(
                        np.transpose(weight_work_np, (1, 2, 0)), dtype=np.float32
                    )
                    del weight_work_np

                while not _is_stopped():
                    if pipeline_error is not None:
                        supp_aligned_linear_gpu.destroy()
                        if (
                            hasattr(weight_work_item, "destroy")
                            and not _is_persistent_spatial_weight(weight_work_item)
                        ):
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

                # Downscale linear frame to FlowNet work-res directly FIRST across all backends
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
                        supp_linear_flow_gpu, analysis_params
                    )
                    if supp_linear_flow_gpu is not supp_linear_gpu:
                        supp_linear_flow_gpu.destroy()
                else:
                    supp_analysis_flow_gpu = supp_linear_flow_gpu

                # Prepare secondary frame to warp at WeightNet work-res
                if (weight_work_h, weight_work_w) != (flow_work_h, flow_work_w):
                    supp_analysis_sec_gpu = taichi_aot.resize(
                        supp_analysis_flow_gpu,
                        (weight_work_w, weight_work_h),
                        interpolation=taichi_aot.INTER_AREA,
                        return_gpu=True,
                    )
                else:
                    supp_analysis_sec_gpu = supp_analysis_flow_gpu

                # Dual-Warp on GPU (Primary in full-res 12MP, Secondary directly in weight-res)
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
                    supp_linear_gpu.destroy()
                if (
                    supp_analysis_flow_gpu is not supp_analysis_sec_gpu
                    and supp_analysis_flow_gpu is not supp_aligned_sec_gpu
                ):
                    supp_analysis_flow_gpu.destroy()
                if supp_analysis_sec_gpu is not supp_aligned_sec_gpu:
                    supp_analysis_sec_gpu.destroy()

                if weight_engine == "spatial_fusion":
                    supp_work_gray_gpu = taichi_aot.cvtColor(
                        supp_aligned_sec_gpu, taichi_aot.COLOR_RGB2GRAY
                    )
                    supp_aligned_sec_gpu.destroy()

                    weight_work_2d_gpu = spatial_weight_work_gpu
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
                    weight_work_item = spatial_weight_post_a_gpu
                    postprocess_spatial_weight_taichi(
                        weight_work_2d_gpu,
                        ghost_penalty=ghost_penalty,
                        ghost_cutoff=ghost_cutoff,
                        dst=weight_work_item,
                    )
                    alpha_mean = 1.0
                elif weight_engine == "average":
                    if supp_aligned_sec_gpu is not None:
                        supp_aligned_sec_gpu.destroy()
                    weight_work_item = np.ones((work_h, work_w, 3), dtype=np.float32)
                    alpha_mean = 1.0
                else:
                    supp_work_rgb_np = np.transpose(
                        supp_aligned_sec_gpu.to_numpy(), (2, 0, 1)
                    ).astype(np.float32)
                    supp_aligned_sec_gpu.destroy()
                    if ref_transfer_map is not None:
                        try:
                            supp_work_rgb_np = apply_precomputed_transfer_map(
                                supp_work_rgb_np, ref_transfer_map
                            )
                        except Exception:
                            pass
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

                _gpu_blend_frame(
                    sum_img_gpu,
                    weight_sum_gpu,
                    supp_aligned_linear_gpu,
                    weight_work_gpu,
                )

                supp_aligned_linear_gpu.destroy()
                if not _is_persistent_spatial_weight(weight_work_gpu):
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
        t_uploader = threading.Thread(
            target=_uploader_worker, name="Stage1.5_Uploader", daemon=True
        )
        t_aligner = threading.Thread(
            target=_alignment_worker, name="Stage2_Aligner", daemon=True
        )
        threads = [t_preloader, t_uploader, t_aligner]

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
        t_uploader.start()
        t_aligner.start()

        # If only alignment is requested, wait for stages and return reference image
        if alignment_only:
            t_preloader.join()
            t_uploader.join()
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
            if spatial_weight_work_gpu is not None:
                spatial_weight_work_gpu.destroy()
            if spatial_weight_post_a_gpu is not None:
                spatial_weight_post_a_gpu.destroy()
            if spatial_weight_post_b_gpu is not None:
                spatial_weight_post_b_gpu.destroy()
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
                    if not _is_persistent_spatial_weight(weight_work_gpu):
                        weight_work_gpu.destroy()
                    if is_cpu_backend and (
                        processed_count % 3 == 0 or processed_count == total_supp
                    ):
                        gc.collect()

                print(
                    f"[GPU Flow Coordinator] Frame {curr_idx}/{total_supp} ({curr_name}) blended "
                    f"(alpha={alpha_mean:.3f}, in_flight={weighted_queue.qsize()})"
                )

        finally:
            # Drain and destroy any remaining GPU buffers in queues immediately
            for q in (preloaded_queue, vram_queue, aligned_queue, weighted_queue):
                while not q.empty():
                    try:
                        val = q.get_nowait()
                        if val is not _SENTINEL and isinstance(val, tuple):
                            for el in val:
                                if (
                                    el is not None
                                    and hasattr(el, "destroy")
                                    and not _is_persistent_spatial_weight(el)
                                ):
                                    try:
                                        el.destroy()
                                    except Exception:
                                        pass
                    except Exception:
                        pass

            t_preloader.join(timeout=0.2)
            t_uploader.join(timeout=0.2)
            t_aligner.join(timeout=0.2)
            if t_weight is not None:
                t_weight.join(timeout=0.2)

            if _is_stopped() or pipeline_error is not None:
                try:
                    aligner.close()
                    if ref_spatial_gray_gpu is not None:
                        ref_spatial_gray_gpu.destroy()
                        ref_spatial_gray_gpu = None
                    if spatial_rows_gpu is not None:
                        spatial_rows_gpu.destroy()
                        spatial_rows_gpu = None
                    if spatial_cols_gpu is not None:
                        spatial_cols_gpu.destroy()
                        spatial_cols_gpu = None
                    if spatial_weight_work_gpu is not None:
                        spatial_weight_work_gpu.destroy()
                        spatial_weight_work_gpu = None
                    if spatial_weight_post_a_gpu is not None:
                        spatial_weight_post_a_gpu.destroy()
                        spatial_weight_post_a_gpu = None
                    if spatial_weight_post_b_gpu is not None:
                        spatial_weight_post_b_gpu.destroy()
                        spatial_weight_post_b_gpu = None
                    if spatial_scratch is not None:
                        spatial_scratch.clear()
                        spatial_scratch = None
                    if session is not None and hasattr(session, "clear_cache"):
                        session.clear_cache()
                except Exception:
                    pass

                # If an actual error occurred, destroy accumulation buffers
                if pipeline_error is not None:
                    try:
                        if sum_img_gpu is not None:
                            sum_img_gpu.destroy()
                        if weight_sum_gpu is not None:
                            weight_sum_gpu.destroy()
                        if ref_gpu is not None:
                            ref_gpu.destroy()
                    except Exception:
                        pass
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

    # Proactively release intermediate alignment & analysis buffers before final normalization
    try:
        aligner.close()
        if ref_spatial_gray_gpu is not None:
            ref_spatial_gray_gpu.destroy()
            ref_spatial_gray_gpu = None
        if spatial_rows_gpu is not None:
            spatial_rows_gpu.destroy()
            spatial_rows_gpu = None
        if spatial_cols_gpu is not None:
            spatial_cols_gpu.destroy()
            spatial_cols_gpu = None
        if spatial_weight_work_gpu is not None:
            spatial_weight_work_gpu.destroy()
            spatial_weight_work_gpu = None
        if spatial_weight_post_a_gpu is not None:
            spatial_weight_post_a_gpu.destroy()
            spatial_weight_post_a_gpu = None
        if spatial_weight_post_b_gpu is not None:
            spatial_weight_post_b_gpu.destroy()
            spatial_weight_post_b_gpu = None
        if spatial_scratch is not None:
            spatial_scratch.clear()
            spatial_scratch = None
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
    from taichi_vision.taichi_algorithm.spatial_fusion import (
        mean_division_vec3_weight_taichi,
    )

    if getattr(weight_sum_gpu, "ndim", 2) == 2 or (len(weight_sum_gpu.shape) == 2):
        # SpatialFusion is luma-weighted.  Use the scalar-weight graph
        # directly; broadcasting to HWC3 would add a full-frame readback,
        # host allocation, and upload at the peak-memory point.
        _final_linear_gpu = mean_division_vec3_weight_taichi(
            sum_img=sum_img_gpu, sum_weight=weight_sum_gpu, ref_img=ref_gpu
        )
        weight_sum_gpu.destroy()
    else:
        _final_linear_gpu = mean_division_vec3_weight_taichi(
            sum_img=sum_img_gpu,
            sum_weight=weight_sum_gpu,
            ref_img=ref_gpu,
        )
        weight_sum_gpu.destroy()

    sum_img_gpu.destroy()
    ref_gpu.destroy()

    result_hwc = np.ascontiguousarray(_final_linear_gpu.to_numpy(), dtype=np.float32)
    _final_linear_gpu.destroy()

    # Synchronize the retired handles, but retain the engine pools: subsequent
    # bursts can acquire same-shape buffers without another VRAM allocation.
    try:
        engine.sync()
    except Exception:
        pass

    mean_alpha = alpha_total / max(1, total_supp)
    print(
        f"[GPU Pipeline] Complete: shape={result_hwc.shape} "
        f"mean_alpha={mean_alpha:.4f} (reusable VRAM pools retained)"
    )

    return result_hwc, mean_alpha


# Canonical alias
run_resident_pipeline = run_gpu_resident_pipeline
