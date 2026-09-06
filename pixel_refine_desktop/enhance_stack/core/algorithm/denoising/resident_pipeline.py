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


def _normalise_alignment_plan(value: str) -> str:
    return str(value or "").strip().casefold().replace("-", " ").replace("_", " ")


def preflight_resident_dependencies(
    *,
    alignment_plan: str,
    weight_engine: str,
    is_raw: bool,
    engine=None,
) -> dict:
    """Validate the target-qualified graph contract before frame allocation.

    This is intentionally a graph-index check, not a compile/provider claim:
    the subsequent smoke test must still execute each selected backend.
    """
    from taichi_vision import taichi_aot

    plan = _normalise_alignment_plan(alignment_plan)
    requires_analysis = str(
        weight_engine or ""
    ).casefold() != "average" or plan not in {
        "",
        "none",
        "no alignment",
        "off",
    }
    requirements = []

    if is_raw:
        requirements.append(
            (
                "hamilton",
                "hamilton_demosaic|hamilton_demosaic_u16",
                lambda: any(
                    taichi_aot.aot_graph_available("hamilton", graph)
                    for graph in ("hamilton_demosaic", "hamilton_demosaic_u16")
                ),
            )
        )
    if requires_analysis:
        requirements.extend(
            [
                ("auto_enhance", "auto_enhance", None),
                ("estimate_noise", "estimate_noise", None),
            ]
        )

    if plan in {"ofb", "orb", "feature matching"}:
        requirements.extend(
            [
                ("ofb", "detect_keypoints", None),
                ("ransac", "ransac_homography", None),
                ("remap", "warp_perspective_f32_3d", None),
            ]
        )
    elif plan == "akaze":
        requirements.extend(
            [
                ("akaze", "detect_keypoints", None),
                ("ransac", "ransac_homography", None),
                ("remap", "warp_perspective_f32_3d", None),
            ]
        )
    elif plan in {"farneback", "farneback optical flow"}:
        requirements.extend(
            [
                ("farneback_flow", "farneback_multi_3", None),
                ("remap", "remap_with_flow_f32_3d", None),
            ]
        )
    elif plan in {
        "lucas kanade",
        "lucas kanade optical flow",
        "lucas kanade gpu optical flow",
    }:
        requirements.extend(
            [
                ("lucas_kanade", "flow_lk_grid_track", None),
                ("remap", "remap_with_flow_f32_3d", None),
            ]
        )
    elif plan in {
        "block matching",
        "block matching gpu",
        "blockmatching",
        "bm",
        "block align",
    }:
        requirements.extend(
            [
                ("lucas_kanade", "flow_lk_grid_track", None),
                ("remap", "remap_with_flow_f32_3d", None),
            ]
        )
    elif plan in {"optical flow", "dense optical flow"}:
        requirements.extend(
            [
                ("compute_flow", "align_end_to_end_3layer", None),
                ("remap", "remap_with_flow_f32_3d", None),
            ]
        )

    missing = []
    checked = []
    for module_name, graph_name, custom_check in requirements:
        available = (
            bool(custom_check())
            if custom_check is not None
            else taichi_aot.aot_graph_available(module_name, graph_name)
        )
        checked.append(
            {
                "module": module_name,
                "graph": graph_name,
                "available": bool(available),
            }
        )
        if not available:
            missing.append(f"{module_name}:{graph_name}")

    result = {
        "backend": str(getattr(engine or taichi_aot.engine, "arch", "unknown")),
        "alignment_plan": alignment_plan,
        "weight_engine": weight_engine,
        "is_raw": bool(is_raw),
        "checked": checked,
        "missing": missing,
    }
    if missing:
        raise RuntimeError(
            "Resident dependency preflight failed before frame allocation: "
            + ", ".join(missing)
            + ". Compile the target-qualified TCM suite for backend "
            + result["backend"]
            + "."
        )
    print(
        f"[GPU Pipeline] Dependency preflight OK: backend={result['backend']} "
        f"alignment={alignment_plan!r} checked={len(checked)}"
    )
    return result


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
        # The canonical demosaic API returns float32 [0, 1] when
        # return_gpu=True. Keep that buffer in VRAM; a GPU->CPU->GPU
        # normalization round-trip defeats the resident pipeline.
        if np.dtype(rgb_gpu.dtype) != np.dtype(np.float32):
            raise RuntimeError(
                "Resident RAW demosaic returned a non-float32 GPU buffer "
                f"({rgb_gpu.dtype}); refusing an implicit CPU round-trip."
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
    ref_gpu: TaichiGPUBuffer,
    mode: str = "natural",
    max_analysis_pixels: int = 500_000,
) -> dict:
    """Analyze AutoEnhance parameters from a bounded GPU downsample.

    AutoEnhance only consumes luminance statistics and already samples at most
    500k values internally. Downsampling before ``to_numpy`` avoids reading a
    complete 12 MP RGB frame back to host memory just to compute those stats.
    """
    from taichi_vision import taichi_aot
    from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
        analyze_auto_enhance_params,
    )

    source_gpu = ref_gpu
    analysis_gpu = None
    source_pixels = int(ref_gpu.shape[0]) * int(ref_gpu.shape[1])
    limit = max(1, int(max_analysis_pixels))
    if source_pixels > limit:
        scale = (float(limit) / float(source_pixels)) ** 0.5
        sample_h = max(32, int(round(ref_gpu.shape[0] * scale)))
        sample_w = max(32, int(round(ref_gpu.shape[1] * scale)))
        analysis_gpu = taichi_aot.resize(
            ref_gpu,
            (sample_w, sample_h),
            interpolation=taichi_aot.INTER_AREA,
            return_gpu=True,
        )
        source_gpu = analysis_gpu
    analysis_pixels = int(source_gpu.shape[0]) * int(source_gpu.shape[1])
    ref_np = source_gpu.to_numpy()
    try:
        params = analyze_auto_enhance_params(ref_np, mode=mode)
    finally:
        del ref_np
        if analysis_gpu is not None:
            analysis_gpu.destroy()
    params["analysis_pixels"] = analysis_pixels
    params["analysis_source_pixels"] = source_pixels
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
        stream_primary: bool = False,
    ):
        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Alignment cancelled.")
            elif callable(stop_event) and stop_event():
                raise RuntimeError("Alignment cancelled.")
        if secondary_frame_to_warp is None:
            return supp_linear_gpu
        return supp_linear_gpu, secondary_frame_to_warp

    def close(self):
        pass


class BlockMatchingGPUResidentAligner:
    """GPU-resident block matching with dual-domain remapping.

    The reference and support analysis buffers are matched at work resolution,
    while the resulting flow is reused to warp both the full-resolution linear
    frame and the smaller analysis frame.  No CPU flow fallback is allowed in
    this adapter; a native failure is surfaced to the resident pipeline.
    """

    def __init__(
        self,
        ref_analysis_gpu: TaichiGPUBuffer,
        *,
        full_shape: Optional[Tuple[int, int]] = None,
        alignment_config: Optional[dict] = None,
    ):
        from taichi_vision import taichi_aot
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.block_matching_gpu import (
            BlockMatchingGPU,
        )

        self.engine = get_engine()
        self.matcher = BlockMatchingGPU()
        config = dict(self.matcher.load_config())
        overrides = alignment_config if isinstance(alignment_config, dict) else {}
        nested = overrides.get("block_matching_gpu_params")
        if isinstance(nested, dict):
            overrides = nested
        if "mode" in overrides:
            config = dict(
                BlockMatchingGPU._resolve_mode_config({"mode": overrides["mode"]})
            )
        for key in (
            "grid_step",
            "border_margin",
            "win_size",
            "max_level",
            "iterations",
            "epsilon",
            "motion_mode",
            "adaptive",
            "adaptive_threshold",
            "tile_overlap",
            "max_flow_px",
            "decoupled_scale",
        ):
            if key in overrides and overrides[key] is not None:
                config[key] = overrides[key]
        config["strict"] = True
        config["conservative_vram"] = True
        self.config = config
        self.ref_shape = tuple(int(value) for value in ref_analysis_gpu.shape[:2])
        if full_shape is None:
            self.full_h, self.full_w = self.ref_shape
        else:
            self.full_h, self.full_w = int(full_shape[0]), int(full_shape[1])
        self.ref_gray_gpu = taichi_aot.cvtColor(
            ref_analysis_gpu, taichi_aot.COLOR_RGB2GRAY
        )
        self.reference_pyramid = self._build_reference_pyramid_cache()
        print(
            f"[GPU Pipeline] Aligner: Block Matching GPU ({self.config.get('mode', 'fast')}, step={self.config.get('grid_step', 32)})"
        )

    def _build_reference_pyramid_cache(self):
        """Build caller-owned reference pyramid levels once per burst.

        ``calcOpticalFlowBlockMatching`` is called for every support frame,
        while the reference image is invariant. Cache only the pyramid levels
        needed by the selected native path; target levels remain per-frame
        allocations. Failure to build this optional performance cache is
        non-fatal and leaves the established native construction path in
        place.
        """
        from taichi_vision import taichi_aot

        levels = [self.ref_gray_gpu]
        height, width = self.ref_shape
        max_level = max(0, int(self.config.get("max_level", 2)))
        requested_decouple = max(0, int(self.config.get("decoupled_scale", 0) or 0))
        if requested_decouple in (2, 4):
            decouple_factor = requested_decouple
        elif requested_decouple == 0 and height * width >= 8_000_000:
            decouple_factor = 2
        else:
            decouple_factor = 0
        decouple_levels = {2: 1, 4: 2}.get(decouple_factor, 0)
        backend = str(getattr(self.engine, "arch", "")).lower()
        use_decoupled = backend in {"cuda", "cpu"} and decouple_levels > 0
        if use_decoupled:
            # The outer wrapper starts at the selected coarse level, then
            # invokes the native path with the remaining pyramid levels.
            # Cache both the coarse base and all descendants so the invariant
            # reference is never downsampled again for each support frame.
            levels_to_build = decouple_levels + max(1, max_level - decouple_levels)
        else:
            levels_to_build = max_level

        try:
            pyramid_mod = taichi_aot._mod("pyramid")
            with self.engine._lock:
                for _ in range(levels_to_build):
                    next_height = height // 2
                    next_width = width // 2
                    if next_height < 32 or next_width < 32:
                        break
                    next_level = self.engine.allocate(
                        (next_height, next_width),
                        dtype=np.float32,
                        is_vector=False,
                        host_accessible=False,
                        vector_dim=1,
                    )
                    pyramid_mod.run(
                        "downsample_2x_f32",
                        src=levels[-1],
                        dst=next_level,
                    )
                    levels.append(next_level)
                    height, width = next_height, next_width
            if len(levels) <= 1:
                return None
            pass
            return levels
        except Exception as exc:
            for level in levels[1:]:
                if level is not None and hasattr(level, "destroy"):
                    try:
                        level.destroy()
                    except Exception:
                        pass
            pass
            return None

    def align_frame(
        self,
        supp_linear_gpu: TaichiGPUBuffer,
        *,
        analysis_frame_gpu: Optional[TaichiGPUBuffer] = None,
        secondary_frame_to_warp: Optional[TaichiGPUBuffer] = None,
        stop_event=None,
        return_gpu: bool = False,
        stream_primary: bool = False,
    ):
        from taichi_vision import taichi_aot

        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Block-matching alignment cancelled.")
            if callable(stop_event) and stop_event():
                raise RuntimeError("Block-matching alignment cancelled.")

        analysis_gpu = (
            analysis_frame_gpu if analysis_frame_gpu is not None else supp_linear_gpu
        )
        owned_analysis = False
        analysis_gray_gpu = None
        flow_gpu = None
        warped_linear = None
        warped_secondary = None
        try:
            if tuple(int(value) for value in analysis_gpu.shape[:2]) != self.ref_shape:
                analysis_gpu = taichi_aot.resize(
                    analysis_gpu,
                    (self.ref_shape[1], self.ref_shape[0]),
                    interpolation=taichi_aot.INTER_AREA,
                    return_gpu=True,
                )
                owned_analysis = True

            analysis_gray_gpu = taichi_aot.cvtColor(
                analysis_gpu, taichi_aot.COLOR_RGB2GRAY
            )
            flow_gpu = self.matcher._calculate_flow_gpu_buffer(
                self.ref_gray_gpu,
                analysis_gray_gpu,
                self.config,
                reference_pyramid=self.reference_pyramid,
            )
            if secondary_frame_to_warp is not None:
                sec_h, sec_w = (
                    int(secondary_frame_to_warp.shape[0]),
                    int(secondary_frame_to_warp.shape[1]),
                )
                warped_secondary = taichi_aot.remap_with_flow(
                    secondary_frame_to_warp,
                    flow_gpu,
                    sec_h,
                    sec_w,
                    return_gpu=return_gpu,
                )
            if stream_primary:
                # Transfer ownership of the source and low-resolution flow to
                # the descriptor.  The primary full-resolution warp is then
                # produced one output tile at a time by the blend stage.
                warped_linear = ResidentWarpedFrame(
                    supp_linear_gpu,
                    flow_gpu,
                    full_shape=(self.full_h, self.full_w),
                )
                flow_gpu = None
            else:
                warped_linear = taichi_aot.remap_with_flow(
                    supp_linear_gpu,
                    flow_gpu,
                    self.full_h,
                    self.full_w,
                    return_gpu=return_gpu,
                )
        except Exception as exc:
            raise RuntimeError(
                "Native Block Matching GPU alignment failed; no CPU fallback is "
                f"permitted in the resident pipeline: {exc}"
            ) from exc
        finally:
            if flow_gpu is not None and hasattr(flow_gpu, "release"):
                flow_gpu.release()
            if analysis_gray_gpu is not None and hasattr(analysis_gray_gpu, "destroy"):
                analysis_gray_gpu.destroy()
            if owned_analysis and hasattr(analysis_gpu, "destroy"):
                analysis_gpu.destroy()

        if secondary_frame_to_warp is not None:
            return warped_linear, warped_secondary
        return warped_linear

    def close(self):
        if self.reference_pyramid is not None:
            for level in self.reference_pyramid[1:]:
                if level is not None and hasattr(level, "destroy"):
                    try:
                        level.destroy()
                    except Exception:
                        pass
            self.reference_pyramid = None
        if self.ref_gray_gpu is not None and hasattr(self.ref_gray_gpu, "destroy"):
            self.ref_gray_gpu.destroy()
            self.ref_gray_gpu = None
        try:
            self.engine.sync()
        except Exception:
            pass


class TaichiDenseFlowResidentAligner:
    """Resident Farneback/Lucas-Kanade adapter backed only by Taichi Vision.

    The optical-flow kernels accept the work-resolution GPU buffers directly.
    The only output materialized at full resolution is the requested remap;
    no OpenCV tracker or CPU flow fallback is part of this route.
    """

    _PRESETS = {
        "farneback": {
            "pyr_scale": 0.5,
            "num_levels": 3,
            "win_size": 15,
            "num_iters": 3,
            "poly_n": 5,
            "poly_sigma": 1.2,
        },
        "lucas_kanade": {
            "grid_step": 32,
            "border_margin": 8,
            "win_size": 15,
            "max_level": 2,
            "iterations": 8,
            "epsilon": 0.02,
            "motion_mode": "fast",
            "max_flow_px": 64.0,
        },
    }

    def __init__(
        self,
        ref_analysis_gpu: TaichiGPUBuffer,
        *,
        flow_type: str,
        full_shape: Optional[Tuple[int, int]] = None,
        alignment_config: Optional[dict] = None,
    ):
        from taichi_vision import taichi_aot

        flow_type = str(flow_type).strip().lower().replace("-", "_")
        if flow_type not in self._PRESETS:
            raise ValueError(f"Unsupported Taichi dense flow: {flow_type}")
        self.flow_type = flow_type
        self.engine = get_engine()
        self.config = self._resolve_config(alignment_config)
        self.ref_h, self.ref_w = (
            int(ref_analysis_gpu.shape[0]),
            int(ref_analysis_gpu.shape[1]),
        )
        if full_shape is None:
            self.full_h, self.full_w = self.ref_h, self.ref_w
        else:
            self.full_h, self.full_w = int(full_shape[0]), int(full_shape[1])
        self.ref_gray_gpu = self._to_gray(ref_analysis_gpu)
        print(
            f"[GPU Pipeline] Aligner: Taichi Vision {flow_type} "
            f"(work={self.ref_w}x{self.ref_h}, engine={getattr(self.engine, 'arch', 'unknown')})"
        )

    def _resolve_config(self, alignment_config):
        config = self._PRESETS[self.flow_type].copy()
        overrides = alignment_config if isinstance(alignment_config, dict) else {}
        nested_names = (
            ("farneback_params", "Farneback", "farneback")
            if self.flow_type == "farneback"
            else ("lucas_kanade_params", "lucas_kanade_gpu_params", "LucasKanade")
        )
        for key in nested_names:
            nested = overrides.get(key)
            if isinstance(nested, dict):
                overrides = nested
                break
        mode = str(overrides.get("mode", "")).strip().lower()
        if mode:
            try:
                from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.farneback_flow_cpu import (
                    FarnebackFlowCPU,
                )
                from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.lucas_kanade_gpu import (
                    LUCAS_KANADE_GPU_PRESETS,
                )

                preset_table = (
                    FarnebackFlowCPU.PRESETS
                    if self.flow_type == "farneback"
                    else LUCAS_KANADE_GPU_PRESETS
                )
                selected = preset_table.get(mode) or preset_table.get("fast")
                if isinstance(selected, dict):
                    config.update(selected)
            except Exception as exc:
                print(f"[GPU Pipeline] Dense-flow preset lookup skipped: {exc}")
        for key, value in overrides.items():
            if key in config and value is not None:
                config[key] = value
        return config

    @staticmethod
    def _to_gray(buffer):
        from taichi_vision import taichi_aot

        if len(buffer.shape) == 2:
            return buffer
        return taichi_aot.cvtColor(buffer, taichi_aot.COLOR_RGB2GRAY)

    def _calculate_flow(self, target_gray_gpu):
        from taichi_vision import taichi_aot

        if self.flow_type == "farneback":
            return taichi_aot.farneback_flow(
                self.ref_gray_gpu,
                target_gray_gpu,
                pyr_scale=float(self.config["pyr_scale"]),
                num_levels=max(1, int(self.config["num_levels"])),
                win_size=max(5, int(self.config["win_size"])),
                num_iters=max(1, int(self.config["num_iters"])),
                poly_n=max(3, int(self.config["poly_n"])),
                poly_sigma=float(self.config["poly_sigma"]),
                return_gpu=True,
            )

        from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLK

        win_size = max(5, int(self.config["win_size"]))
        if win_size % 2 == 0:
            win_size += 1
        return calcOpticalFlowPyrLK(
            self.ref_gray_gpu,
            target_gray_gpu,
            winSize=(win_size, win_size),
            maxLevel=max(0, int(self.config["max_level"])),
            grid_step=max(4, int(self.config["grid_step"])),
            border_margin=max(0, int(self.config["border_margin"])),
            motion_mode=str(self.config.get("motion_mode", "fast")),
            max_flow_px=float(self.config.get("max_flow_px", 0.0)),
            return_gpu=True,
        )

    def align_frame(
        self,
        supp_linear_gpu,
        *,
        analysis_frame_gpu=None,
        secondary_frame_to_warp=None,
        stop_event=None,
        return_gpu=True,
        stream_primary: bool = False,
    ):
        from taichi_vision import taichi_aot

        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Dense-flow alignment cancelled.")
            if callable(stop_event) and stop_event():
                raise RuntimeError("Dense-flow alignment cancelled.")

        analysis_gpu = (
            analysis_frame_gpu if analysis_frame_gpu is not None else supp_linear_gpu
        )
        owned_analysis = False
        target_gray_gpu = None
        owned_gray = False
        flow_gpu = None
        warped_secondary = None
        try:
            if tuple(int(value) for value in analysis_gpu.shape[:2]) != (
                self.ref_h,
                self.ref_w,
            ):
                analysis_gpu = taichi_aot.resize(
                    analysis_gpu,
                    (self.ref_w, self.ref_h),
                    interpolation=taichi_aot.INTER_AREA,
                    return_gpu=True,
                )
                owned_analysis = True
            target_gray_gpu = self._to_gray(analysis_gpu)
            owned_gray = target_gray_gpu is not analysis_gpu
            flow_gpu = self._calculate_flow(target_gray_gpu)
            if isinstance(flow_gpu, tuple):
                flow_gpu = flow_gpu[0]
            if not hasattr(flow_gpu, "shape"):
                flow_gpu = taichi_aot.upload(
                    np.ascontiguousarray(flow_gpu, dtype=np.float32),
                    is_vector=True,
                    vector_dim=2,
                )
            expected = (self.ref_h, self.ref_w, 2)
            if tuple(int(value) for value in flow_gpu.shape) != expected:
                raise RuntimeError(
                    f"Taichi {self.flow_type} returned flow shape {flow_gpu.shape}; "
                    f"expected {expected}"
                )

            if secondary_frame_to_warp is not None:
                sec_h, sec_w = map(int, secondary_frame_to_warp.shape[:2])
                warped_secondary = taichi_aot.remap_with_flow(
                    secondary_frame_to_warp,
                    flow_gpu,
                    sec_h,
                    sec_w,
                    return_gpu=return_gpu,
                )

            if stream_primary:
                warped_primary = ResidentWarpedFrame(
                    supp_linear_gpu,
                    flow_gpu,
                    full_shape=(self.full_h, self.full_w),
                )
                flow_gpu = None
            else:
                warped_primary = taichi_aot.remap_with_flow(
                    supp_linear_gpu,
                    flow_gpu,
                    self.full_h,
                    self.full_w,
                    return_gpu=return_gpu,
                )
        except Exception as exc:
            raise RuntimeError(
                f"Native Taichi {self.flow_type} alignment failed; "
                f"no OpenCV fallback is permitted: {exc}"
            ) from exc
        finally:
            if flow_gpu is not None and hasattr(flow_gpu, "destroy"):
                flow_gpu.destroy()
            if (
                owned_gray
                and target_gray_gpu is not None
                and hasattr(target_gray_gpu, "destroy")
            ):
                target_gray_gpu.destroy()
            if owned_analysis and hasattr(analysis_gpu, "destroy"):
                analysis_gpu.destroy()

        if secondary_frame_to_warp is not None:
            return warped_primary, warped_secondary
        return warped_primary

    def close(self):
        if self.ref_gray_gpu is not None and hasattr(self.ref_gray_gpu, "destroy"):
            self.ref_gray_gpu.destroy()
            self.ref_gray_gpu = None


class ResidentWarpedFrame:
    """Ownership descriptor for a lazily warped full-resolution support frame.

    Keeping the source and its work-resolution flow resident avoids allocating
    a second full RGB frame.  ``_gpu_blend_frame`` asks the descriptor for
    output tiles and consumes each tile immediately through the offset spatial
    accumulation graph.
    """

    def __init__(self, source_gpu, flow_gpu, *, full_shape):
        self.source_gpu = source_gpu
        self.flow_gpu = flow_gpu
        self.full_h, self.full_w = int(full_shape[0]), int(full_shape[1])
        self._destroyed = False

    @property
    def shape(self):
        return (self.full_h, self.full_w, 3)

    @property
    def dtype(self):
        return getattr(self.source_gpu, "dtype", np.float32)

    @property
    def nbytes(self):
        return int(self.full_h * self.full_w * 3 * np.dtype(np.float32).itemsize)

    def destroy(self):
        if self._destroyed:
            return
        self._destroyed = True
        for name in ("source_gpu", "flow_gpu"):
            buffer = getattr(self, name, None)
            if buffer is not None and hasattr(buffer, "destroy"):
                try:
                    buffer.destroy()
                except Exception:
                    pass
            setattr(self, name, None)

    def release(self):
        self.destroy()


def _postprocess_spatial_weight_gpu(
    weight_gpu: TaichiGPUBuffer,
    *,
    ghost_penalty: float,
    ghost_cutoff: float,
):
    """Shape a SpatialFusion weight map without a CPU round-trip when able.

    The returned value is either a GPU buffer (new graph path) or a NumPy
    array (compatibility path for older spatial TCMs). Keeping the fallback
    here preserves the established output contract while making the optimized
    path fail closed on graph availability.
    """
    if float(ghost_penalty) == 1.0 and float(ghost_cutoff) <= 0.0:
        return weight_gpu

    processed_gpu = None
    try:
        from taichi_vision.taichi_algorithm.aot_api import aot_graph_available

        if aot_graph_available("spatial", "postprocess_spatial_weight"):
            from taichi_vision.taichi_algorithm.spatial_fusion import (
                postprocess_spatial_weight_taichi,
            )

            processed_gpu = postprocess_spatial_weight_taichi(
                weight_gpu,
                ghost_penalty=float(ghost_penalty),
                ghost_cutoff=float(ghost_cutoff),
            )
            weight_gpu.destroy()
            return processed_gpu
    except Exception as exc:
        if processed_gpu is not None:
            try:
                processed_gpu.destroy()
            except Exception:
                pass
        print(
            f"[GPU Pipeline] Spatial weight GPU postprocess unavailable; "
            f"using compatibility readback: {exc}"
        )

    # Compatibility path for an older artifact. This is numerically the same
    # transform used before the resident GPU postprocess graph was introduced.
    weights = weight_gpu.to_numpy()
    weight_gpu.destroy()
    if float(ghost_penalty) != 1.0:
        weights = np.power(weights, float(ghost_penalty))
    if float(ghost_cutoff) > 0.0:
        cutoff = float(ghost_cutoff)
        weights = np.clip(
            (weights - cutoff) / max(1e-5, 1.0 - cutoff),
            0.0,
            1.0,
        )
    return np.ascontiguousarray(weights, dtype=np.float32)


class FeatureMatchingGPUAligner:
    """Taichi Vision feature matcher for both CPU and GPU engine targets.

    ``ofb`` is the maintained Taichi Vision ORB-compatible FAST/BRIEF path;
    ``akaze`` is the maintained Taichi Vision nonlinear diffusion path.  Both
    return matched points to the Taichi Vision RANSAC wrapper, so this adapter
    never imports or calls OpenCV.
    """

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
        self.config = feature_config if isinstance(feature_config, dict) else {}
        for nested_name in ("ofb_params", "orb_params", "akaze_params"):
            nested = self.config.get(nested_name)
            if isinstance(nested, dict):
                self.config = nested
                break
        if self.feature_type in {"orb", "ofb"}:
            self.matcher_name = "ofb"
        elif self.feature_type == "akaze":
            self.matcher_name = "akaze"
        else:
            raise ValueError(
                "Taichi feature aligner supports only ORB/OFB and AKAZE; "
                f"received {feature_type!r}"
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
            ref_gray_gpu.destroy()
            ref_gray_gpu = ref_gray_work

        self.ref_gray_gpu = ref_gray_gpu
        print(
            f"[GPU Pipeline] Aligner: Taichi Vision {self.matcher_name.upper()} "
            f"(work={self.work_w}x{self.work_h}, engine={getattr(taichi_aot.engine, 'arch', 'unknown')})"
        )

    def _matcher_parameters(self):
        if self.matcher_name == "akaze":
            return {
                "ratio_threshold": float(self.config.get("ratio", 0.75)),
                "grid_size": max(8, int(self.config.get("grid_size", 32))),
                "threshold": float(
                    self.config.get("akaze_threshold", self.config.get("thresh", 0.008))
                ),
                "margin": max(4, int(self.config.get("margin", 15))),
                "max_keypoints": max(
                    100,
                    int(
                        self.config.get(
                            "max_kps", self.config.get("max_keypoints", 1500)
                        )
                    ),
                ),
                "k_contrast": float(self.config.get("k_contrast", 0.02)),
                "num_fed_steps": max(1, int(self.config.get("num_fed_steps", 8))),
            }
        return {
            "ratio_threshold": float(self.config.get("ratio", 0.75)),
            "grid_size": max(8, int(self.config.get("grid_size", 32))),
            "threshold": float(self.config.get("threshold", 0.015)),
            "margin": max(4, int(self.config.get("margin", 15))),
            "max_keypoints": max(
                100,
                int(self.config.get("max_kps", self.config.get("max_keypoints", 1500))),
            ),
        }

    def _estimate_homography(self, supp_gray_gpu):
        from taichi_vision import taichi_aot

        parameters = self._matcher_parameters()
        if self.matcher_name == "akaze":
            matched = taichi_aot.akaze(self.ref_gray_gpu, supp_gray_gpu, **parameters)
        else:
            matched = taichi_aot.ofb(self.ref_gray_gpu, supp_gray_gpu, **parameters)
        if matched is None or matched[0] is None or matched[1] is None:
            return None
        pts_ref, pts_supp = matched[0], matched[1]
        if len(pts_ref) < 4 or len(pts_supp) < 4:
            return None
        homography, mask = taichi_aot.find_homography(
            np.ascontiguousarray(pts_supp, dtype=np.float32),
            np.ascontiguousarray(pts_ref, dtype=np.float32),
            method="RANSAC",
            ransacReprojThreshold=float(self.config.get("ransac_threshold", 5.0)),
            n_hypotheses=max(64, int(self.config.get("ransac_hypotheses", 1024))),
            max_iters=max(1, int(self.config.get("ransac_iters", 1))),
            return_gpu=False,
        )
        if homography is None:
            return None
        if mask is not None and int(np.asarray(mask).reshape(-1).sum()) < 4:
            return None
        return np.asarray(homography, dtype=np.float32)

    def align_frame(
        self,
        supp_linear_gpu,
        *,
        analysis_frame_gpu=None,
        secondary_frame_to_warp=None,
        stop_event=None,
        return_gpu=True,
        stream_primary: bool = False,
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
            H_work = self._estimate_homography(supp_gray_gpu)
        finally:
            supp_gray_gpu.destroy()

        if H_work is not None:
            scale_x = self.target_w / float(self.work_w)
            scale_y = self.target_h / float(self.work_h)
            scale_to_full = np.array(
                [[scale_x, 0, 0], [0, scale_y, 0], [0, 0, 1.0]],
                dtype=np.float32,
            )
            scale_to_work = np.array(
                [[1.0 / scale_x, 0, 0], [0, 1.0 / scale_y, 0], [0, 0, 1.0]],
                dtype=np.float32,
            )
            H_full = scale_to_full @ H_work @ scale_to_work
            warped_primary = taichi_aot.warp_perspective(
                supp_linear_gpu,
                H_full,
                (self.target_w, self.target_h),
                return_gpu=True,
            )
            warped_secondary = None
            if secondary_frame_to_warp is not None:
                warped_secondary = taichi_aot.warp_perspective(
                    secondary_frame_to_warp,
                    H_work,
                    (self.work_w, self.work_h),
                    return_gpu=return_gpu,
                )
            if secondary_frame_to_warp is not None:
                return warped_primary, warped_secondary
            return warped_primary

        if secondary_frame_to_warp is not None:
            return supp_linear_gpu, secondary_frame_to_warp
        return supp_linear_gpu

    def close(self):
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
):
    """Factory creating the appropriate GPU-resident aligner instance."""
    plan_clean = (
        str(alignment_plan or "").strip().lower().replace("-", " ").replace("_", " ")
    )
    if plan_clean in ("no alignment", "none", "off", ""):
        print("[GPU Pipeline] Aligner: No Alignment (Bypass)")
        return NoAlignmentGPUAligner(ref_analysis_gpu)
    elif plan_clean in (
        "block matching gpu",
        "block matching",
        "blockmatching",
        "block_align",
        "bm",
    ):
        return BlockMatchingGPUResidentAligner(
            ref_analysis_gpu,
            full_shape=full_shape,
            alignment_config=alignment_config,
        )
    elif plan_clean in (
        "farneback",
        "farneback optical flow",
    ):
        return TaichiDenseFlowResidentAligner(
            ref_analysis_gpu,
            flow_type="farneback",
            full_shape=full_shape,
            alignment_config=alignment_config,
        )
    elif plan_clean in (
        "lucas kanade",
        "lucas kanade optical flow",
        "lucas kanade gpu optical flow",
    ):
        return TaichiDenseFlowResidentAligner(
            ref_analysis_gpu,
            flow_type="lucas_kanade",
            full_shape=full_shape,
            alignment_config=alignment_config,
        )
    elif plan_clean in ("ofb", "orb", "akaze", "feature matching"):
        print(f"[GPU Pipeline] Aligner: Feature Matching ({plan_clean.upper()})")
        return FeatureMatchingGPUAligner(
            ref_analysis_gpu,
            feature_type="ofb" if plan_clean == "feature matching" else plan_clean,
            work_scale=work_scale,
            full_shape=full_shape,
            feature_config=alignment_config,
        )
    elif plan_clean in ("light glue", "lightglue"):
        raise RuntimeError(
            "Light Glue has no validated resident adapter. "
            "Use OFB/ORB, AKAZE, Farneback, Lucas-Kanade, or Block Matching GPU."
        )
    elif plan_clean == "raft":
        raise RuntimeError(
            "RAFT has no validated resident adapter; refusing to route it to "
            "the generic dense-flow graph."
        )
    elif plan_clean not in ("optical flow", "dense optical flow"):
        raise ValueError(
            f"Unsupported resident alignment plan {alignment_plan!r}; "
            "select a validated Taichi alignment route."
        )
    else:
        print(
            f"[GPU Pipeline] Aligner: Generic Taichi Dense Optical Flow ({plan_clean})"
        )
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


def _primary_descriptor_owns_source(aligned_item, source_gpu):
    return (
        isinstance(aligned_item, ResidentWarpedFrame)
        and getattr(aligned_item, "source_gpu", None) is source_gpu
    )


def _prepare_support_frame(
    supp_path,
    *,
    is_raw,
    target_h,
    target_w,
    analysis_box_kernel_size,
    weight_engine,
    prepare_work_analysis_fn,
):
    """Load a support frame to GPU, resize to target, create analysis copy, apply box filter.

    Returns (supp_linear_gpu, secondary_frame_to_warp).
    Caller owns both buffers and must destroy them when done.
    """
    from taichi_vision import taichi_aot

    supp_linear_gpu = load_frame_to_gpu(supp_path, is_raw=is_raw)
    if tuple(int(v) for v in supp_linear_gpu.shape[:2]) != (target_h, target_w):
        supp_resized_gpu = taichi_aot.resize(
            supp_linear_gpu,
            (target_w, target_h),
            interpolation=taichi_aot.INTER_LINEAR,
            return_gpu=True,
        )
        supp_linear_gpu.destroy()
        supp_linear_gpu = supp_resized_gpu

    supp_analysis_work_gpu = prepare_work_analysis_fn(supp_linear_gpu)

    if analysis_box_kernel_size > 0:
        supp_analysis_denoised = taichi_aot.box_filter(
            supp_analysis_work_gpu,
            kernel_size=analysis_box_kernel_size,
            return_gpu=True,
        )
        if supp_analysis_work_gpu is not supp_linear_gpu:
            supp_analysis_work_gpu.destroy()
        supp_analysis_work_gpu = supp_analysis_denoised

    secondary_frame_to_warp = (
        supp_analysis_work_gpu if weight_engine != "average" else None
    )
    return supp_linear_gpu, supp_analysis_work_gpu, secondary_frame_to_warp


def _unpack_aligned_result(
    aligned_result,
    *,
    secondary_frame_to_warp,
    supp_linear_gpu,
    supp_analysis_gpu,
    supp_analysis_work_gpu,
):
    """Unpack aligner output and destroy intermediate buffers no longer needed.

    Returns (supp_aligned_linear_gpu, supp_aligned_analysis_work_gpu).
    """
    if secondary_frame_to_warp is None:
        supp_aligned_linear_gpu = aligned_result
        supp_aligned_analysis_work_gpu = None
    else:
        supp_aligned_linear_gpu, supp_aligned_analysis_work_gpu = aligned_result

    if (
        supp_aligned_linear_gpu is not supp_linear_gpu
        and not _primary_descriptor_owns_source(
            supp_aligned_linear_gpu, supp_linear_gpu
        )
    ):
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

    return supp_aligned_linear_gpu, supp_aligned_analysis_work_gpu


def _compute_support_weight(
    supp_aligned_analysis_work_gpu,
    supp_aligned_linear_gpu,
    *,
    weight_engine,
    engine,
    session,
    ref_work_rgb_np,
    spatial_work_h,
    spatial_work_w,
    ref_spatial_gray_gpu,
    spatial_row_starts,
    spatial_col_starts,
    spatial_rows_gpu,
    spatial_cols_gpu,
    spatial_tile_h,
    spatial_tile_w,
    spatial_noise_sigma,
    spatial_motion_sens,
    spatial_noise_offset,
    spatial_texture_boost,
    spatial_texture_radius,
    spatial_single_coarse,
    spatial_scratch,
    ghost_penalty,
    ghost_cutoff,
    tile_size,
    overlap,
    chroma_sensitivity,
    stop_event,
):
    """Compute the weight map for one support frame based on weight_engine.

    Returns (weight_work_item, alpha_mean).  The caller owns weight_work_item.
    """
    if weight_engine == "spatial_fusion":
        supp_work_gray_gpu = taichi_aot.cvtColor(
            supp_aligned_analysis_work_gpu, taichi_aot.COLOR_RGB2GRAY
        )
        supp_aligned_analysis_work_gpu.destroy()
        spatial_weight_input_gpu = _prepare_spatial_weight_gray_gpu(supp_work_gray_gpu)
        weight_work_2d_gpu = engine.allocate(
            (spatial_work_h, spatial_work_w),
            dtype=np.float32,
            host_accessible=False,
        )
        generate_spatial_weights_taichi(
            current_image=spatial_weight_input_gpu,
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
            coarse_texture_boost=spatial_texture_boost,
            coarse_texture_radius=spatial_texture_radius,
            coarse_pyramid_single_pass=spatial_single_coarse,
        )
        spatial_weight_input_gpu.destroy()
        if spatial_weight_input_gpu is not supp_work_gray_gpu:
            supp_work_gray_gpu.destroy()
        weight_work_item = _postprocess_spatial_weight_gpu(
            weight_work_2d_gpu,
            ghost_penalty=ghost_penalty,
            ghost_cutoff=ghost_cutoff,
        )
        return weight_work_item, 1.0

    if weight_engine == "average":
        if (
            supp_aligned_analysis_work_gpu is not None
            and supp_aligned_analysis_work_gpu is not supp_aligned_linear_gpu
        ):
            supp_aligned_analysis_work_gpu.destroy()
        return None, 1.0

    # FusionNet / ONNX path
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
    return weight_work_item, alpha_mean


def _gpu_blend_frame(
    sum_img_gpu,
    weight_sum_gpu,
    supp_aligned_gpu,
    weight_work_gpu,
    *,
    splat_tile_size: Optional[int] = None,
    uniform_weights: bool = False,
    block_accumulation: bool = False,
    finalize: bool = False,
    uniform_denominator: Optional[float] = None,
):
    """Blend one support frame into the GPU-resident accumulator.

    The streaming path uses one native fused remap+accumulate graph, so the
    full-resolution source and low-resolution flow are sampled directly into
    the global sums without materializing an aligned tile.  The full-frame
    path retains the established accumulation graphs for compatibility.

    Final block accumulation can normalize in place, removing a separate
    full-resolution dispatch while preserving the established frame order.
    """
    from taichi_vision.taichi_algorithm.spatial_fusion import (
        accumulate_spatial_merging_taichi,
    )

    if isinstance(supp_aligned_gpu, ResidentWarpedFrame):
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            remap_accumulate_average_sum_tile_taichi,
            remap_accumulate_tile_taichi,
        )

        tile_size = max(32, int(splat_tile_size))
        for y0 in range(0, supp_aligned_gpu.full_h, tile_size):
            for x0 in range(0, supp_aligned_gpu.full_w, tile_size):
                tile_h = min(tile_size, supp_aligned_gpu.full_h - y0)
                tile_w = min(tile_size, supp_aligned_gpu.full_w - x0)
                if uniform_weights and block_accumulation:
                    remap_accumulate_average_sum_tile_taichi(
                        source_full=supp_aligned_gpu.source_gpu,
                        flow_work=supp_aligned_gpu.flow_gpu,
                        final_image_sum=sum_img_gpu,
                        full_shape=(supp_aligned_gpu.full_h, supp_aligned_gpu.full_w),
                        offset=(y0, x0),
                        tile_shape=(tile_h, tile_w),
                        finalize=finalize,
                        denominator=uniform_denominator,
                    )
                else:
                    remap_accumulate_tile_taichi(
                        source_full=supp_aligned_gpu.source_gpu,
                        flow_work=supp_aligned_gpu.flow_gpu,
                        final_image_sum=sum_img_gpu,
                        weight_map_sum_full=weight_sum_gpu,
                        full_shape=(supp_aligned_gpu.full_h, supp_aligned_gpu.full_w),
                        offset=(y0, x0),
                        tile_shape=(tile_h, tile_w),
                        weight_map_work=None if uniform_weights else weight_work_gpu,
                    )
        return bool(finalize and uniform_weights and block_accumulation)

    if block_accumulation:
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            accumulate_average_sum_region_taichi,
            accumulate_spatial_merging_region_taichi,
        )

        tile_size = max(32, int(splat_tile_size))
        full_h, full_w = (int(sum_img_gpu.shape[0]), int(sum_img_gpu.shape[1]))
        for y0 in range(0, full_h, tile_size):
            for x0 in range(0, full_w, tile_size):
                tile_shape = (
                    min(tile_size, full_h - y0),
                    min(tile_size, full_w - x0),
                )
                if uniform_weights:
                    accumulate_average_sum_region_taichi(
                        current_image_full=supp_aligned_gpu,
                        final_image_sum=sum_img_gpu,
                        offset=(y0, x0),
                        tile_shape=tile_shape,
                        finalize=finalize,
                        denominator=uniform_denominator,
                    )
                else:
                    accumulate_spatial_merging_region_taichi(
                        current_image_full=supp_aligned_gpu,
                        weight_map_work=weight_work_gpu,
                        final_image_sum=sum_img_gpu,
                        weight_map_sum_full=weight_sum_gpu,
                        offset=(y0, x0),
                        tile_shape=tile_shape,
                        finalize=finalize,
                    )
        return bool(finalize)

    if uniform_weights:
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            accumulate_average_taichi,
        )

        accumulate_average_taichi(
            current_image_full=supp_aligned_gpu,
            final_image_sum=sum_img_gpu,
            weight_map_sum_full=weight_sum_gpu,
        )
    else:
        accumulate_spatial_merging_taichi(
            current_image_full=supp_aligned_gpu.view_as_vector(False),
            weight_map_work=weight_work_gpu.view_as_vector(False),
            final_image_sum=sum_img_gpu.view_as_vector(False),
            weight_map_sum_full=weight_sum_gpu.view_as_vector(False),
        )
    return False


def _resolve_resident_accumulation_plan(
    engine,
    *,
    mode,
    weight_engine,
    shape,
    requested_tile_size,
    performance_block_size=None,
    performance_threshold_mp=None,
):
    """Resolve block accumulation against engine policy and TCM capability."""
    from taichi_vision.taichi_algorithm.aot_api import aot_graph_available

    clean_mode = str(mode or "auto").strip().casefold().replace("-", "_")
    if clean_mode in {"full", "full_frame", "off", "disabled", "none"}:
        return {"enabled": False, "reason": "full-frame mode requested"}

    block_config = engine.get_block_config()
    memory = engine.get_memory_status(force=True)
    configured_size = block_config.normalized_size()
    if isinstance(configured_size, (tuple, list)):
        configured_size = max(int(configured_size[0]), int(configured_size[1]))
    recommended = int(memory.get("recommended_block_size", 0) or 0)
    if performance_block_size is not None:
        selected_size = performance_block_size
    elif block_config.enabled:
        selected_size = configured_size
    elif clean_mode == "auto" and recommended:
        selected_size = recommended
    else:
        selected_size = requested_tile_size or recommended or configured_size
    tile_size = max(32, int(selected_size))

    force_block = clean_mode in {"block", "tile", "tiled", "force"}
    backend = str(getattr(engine, "arch", "")).strip().casefold()
    # Current measured speed qualification is deliberately narrow.  Average
    # removes an entire RGB weight accumulator, while weighted engines retain
    # their scalar/vec3 sums and therefore do not yet offset region-dispatch
    # overhead under healthy memory conditions.
    performance_qualified = (
        backend in {"cpu", "cuda"} and weight_engine == "average"
    )
    pixel_count = int(shape[0]) * int(shape[1])
    if performance_threshold_mp is not None:
        threshold_pixels = int(max(0.1, float(performance_threshold_mp)) * 1_000_000)
    else:
        threshold_pixels = int(
            os.environ.get("PIXEL_REFINE_RESIDENT_BLOCK_PIXELS", "4000000")
        )
    large_frame = pixel_count >= threshold_pixels
    memory_pressure = str(memory.get("pressure", "healthy")).lower()
    automatic = bool(
        force_block
        or memory_pressure != "healthy"
        or (performance_qualified and (block_config.enabled or large_frame))
    )
    if not automatic:
        reason = (
            f"block speed is not qualified on {backend or 'this backend'}"
            if large_frame
            else "frame is below the block threshold"
        )
        return {"enabled": False, "reason": reason}

    if weight_engine == "average":
        required = (
            "accumulate_average_sum_region",
            "remap_accumulate_average_sum_tile",
            "normalize_accumulator_uniform_region",
        )
    elif weight_engine == "spatial_fusion":
        required = (
            "accumulate_spatial_merging_region",
            "normalize_accumulator_scalar_region",
        )
    else:
        required = (
            "accumulate_spatial_merging_vec3_region",
            "normalize_accumulator_vec3_region",
        )
    missing = tuple(
        graph
        for graph in required
        if not aot_graph_available("spatial_fusion", graph)
    )
    if missing:
        return {
            "enabled": False,
            "reason": "target TCM lacks block graph(s): " + ", ".join(missing),
        }
    return {
        "enabled": True,
        "tile_size": tile_size,
        "required_graphs": required,
        "memory_pressure": memory_pressure,
        "performance_qualified": performance_qualified,
    }


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
    accumulation_mode: str = "auto",
    alignment_only: bool = False,
    batch_queue: int = 3,
    auto_params: Optional[dict] = None,
    stop_event: Optional[threading.Event] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    accumulation_block_size: Optional[int] = None,
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
        accumulation_mode: "auto", "block", or "full" accumulation policy.
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
    )

    engine = get_engine()
    try:
        from config import get_compute_block_settings

        performance_block_settings = get_compute_block_settings()
    except Exception:
        # Headless/legacy callers still retain the runtime defaults below.
        performance_block_settings = {}
    if accumulation_block_size is not None:
        performance_block_settings = dict(performance_block_settings)
        performance_block_settings["block_size"] = int(accumulation_block_size)
    requested_accumulation_mode = str(accumulation_mode or "auto").strip().casefold()
    if requested_accumulation_mode in {"auto", "automatic"}:
        configured_mode = performance_block_settings.get("mode")
        if configured_mode:
            accumulation_mode = configured_mode
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

    preflight_resident_dependencies(
        alignment_plan=alignment_plan,
        weight_engine=weight_engine,
        is_raw=is_raw,
        engine=engine,
    )

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
        f"[GPU Pipeline] Reference Frame: ({target_w}x{target_h}, {ref_gpu.dtype}) | Engine: {weight_engine}"
    )

    # ------------------------------------------------------------------
    # PHASE 2: Tier 1 Analysis AutoEnhance for Feature Extraction
    # ------------------------------------------------------------------
    # AutoEnhance analysis on reference frame:
    # - Versi 1 (Analysis / High-Key): For Alignment & ONNX WeightNet (Used for BOTH RAW & Non-RAW)
    # - Versi 2 (Natural Tone Map): For SpatialFusion Perceptual Analysis (RAW only)
    # Average without alignment has no analysis consumer, so avoid a needless
    # GPU resize + host histogram readback.  Every other path keeps the same
    # analysis contract, including Block Matching's optical domain.
    plan_clean = str(alignment_plan or "").strip().lower()
    alignment_requires_analysis = plan_clean not in (
        "no alignment",
        "none",
        "off",
        "",
    )
    analysis_required = weight_engine != "average" or alignment_requires_analysis
    if analysis_required:
        analysis_params = analyze_auto_enhance_on_gpu(ref_gpu, mode="analysis")
        natural_params = (
            analyze_auto_enhance_on_gpu(ref_gpu, mode="natural") if is_raw else None
        )
        if is_raw and natural_params is not None:
            pass
        else:
            pass
    else:
        analysis_params = None
        natural_params = None
        pass

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

    def _prepare_work_analysis_gpu(linear_gpu):
        """Create only the work-resolution analysis buffer when needed."""
        if not analysis_required:
            return linear_gpu

        analysis_input_gpu = linear_gpu
        if (work_h, work_w) != (target_h, target_w):
            analysis_input_gpu = taichi_aot.resize(
                linear_gpu,
                (work_w, work_h),
                interpolation=taichi_aot.INTER_AREA,
                return_gpu=True,
            )

        # AutoEnhance is analysis preprocessing, not the linear fusion
        # signal. Applying it after downsampling avoids a full-resolution
        # temporary for every support frame.
        if analysis_params is not None:
            analysis_gpu = apply_auto_enhance_on_gpu(
                analysis_input_gpu, analysis_params
            )
            if analysis_input_gpu is not linear_gpu:
                analysis_input_gpu.destroy()
            return analysis_gpu
        return analysis_input_gpu

    # Create high-contrast analysis copy (Versi 1) directly at work
    # resolution. The fusion reference remains the original linear buffer.
    ref_analysis_gpu = _prepare_work_analysis_gpu(ref_gpu)

    # Noise-Aware Analysis Pre-Filter on work-res:
    # - Noise Score >= 0.60: Aggressive pre-denoising (5x5 Box Filter)
    # - 0.30 <= Noise Score < 0.60: Light pre-denoising (3x3 Box Filter)
    # - Noise Score < 0.30: Clean image, pre-denoising bypassed
    analysis_box_kernel_size = 0
    ref_noise_score = None
    if analysis_required:
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
                pass
            elif ref_noise_score >= 0.30:
                analysis_box_kernel_size = 3
                ref_analysis_denoised = taichi_aot.box_filter(
                    ref_analysis_gpu, kernel_size=3, return_gpu=True
                )
                if ref_analysis_gpu is not ref_gpu:
                    ref_analysis_gpu.destroy()
                ref_analysis_gpu = ref_analysis_denoised
                pass
            else:
                pass
        except Exception as e_noise:
            raise RuntimeError(
                "Taichi estimate_noise failed during resident analysis; "
                "the result cannot be classified safely: "
                f"{e_noise}"
            ) from e_noise
    else:
        pass

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
    spatial_work_h = work_h
    spatial_work_w = work_w

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
        default_spatial_tile = (
            # Larger spatial tiles reduce the number of serialized AOT
            # dispatches on large frames.  Tile 24 was checked against tile
            # 16 on the 12 MP Block Matching + SpatialFusion path.
            24
            if target_h * target_w >= 8_000_000
            else (tile_size if tile_size <= 64 else 16)
        )
        st_size = int(
            cfg.get(
                "similarity_spatial_tile_size",
                default_spatial_tile,
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
        default_spatial_scale = min(
            capped_scale,
            # SpatialFusion is only a confidence-analysis map.  Keep optical
            # alignment at ``capped_scale``; the lower map resolution avoids
            # quadratic work on large sensors while preserving the full-res
            # linear fusion signal.  0.25 was measured against 0.375 on the
            # 12 MP RAW path before becoming the large-frame default.
            0.25 if target_h * target_w >= 8_000_000 else capped_scale,
        )
        try:
            spatial_scale = float(
                cfg.get("similarity_spatial_work_scale", default_spatial_scale)
            )
        except (TypeError, ValueError):
            spatial_scale = default_spatial_scale
        spatial_scale = min(capped_scale, max(0.125, spatial_scale))
        spatial_work_h = max(32, int(target_h * spatial_scale))
        spatial_work_w = max(32, int(target_w * spatial_scale))
        # Texture boosting is analysis-only.  Keep it configurable at the
        # resident-pipeline boundary so large-frame profiles can disable the
        # extra full-resolution Gaussian pass without changing the linear
        # fusion buffer or the public SpatialFusion API.
        default_texture_boost = 0.0 if target_h * target_w >= 8_000_000 else 0.30
        spatial_texture_boost = float(
            cfg.get("similarity_coarse_texture_boost", default_texture_boost)
        )
        spatial_texture_radius = float(
            cfg.get("similarity_coarse_texture_radius", 10.0)
        )
        spatial_single_coarse = bool(
            cfg.get(
                "similarity_coarse_pyramid_single_pass",
                target_h * target_w >= 8_000_000,
            )
        )
        pass

        # SpatialFusion analyzes via AutoEnhance v1 (High-Key Analysis Mode)
        if tuple(int(value) for value in ref_analysis_gpu.shape[:2]) != (
            spatial_work_h,
            spatial_work_w,
        ):
            ref_spatial_v1_gpu = taichi_aot.resize(
                ref_analysis_gpu,
                (spatial_work_w, spatial_work_h),
                interpolation=taichi_aot.INTER_AREA,
                return_gpu=True,
            )
        else:
            ref_spatial_v1_gpu = ref_analysis_gpu

        ref_spatial_gray_gpu = taichi_aot.cvtColor(
            ref_spatial_v1_gpu, taichi_aot.COLOR_RGB2GRAY
        )

        # Estimasi noise 100% GPU-Native Taichi Vision (Wavelet Subband Minima & Patch Subspace)
        # Terkalibrasi ke noise sigma spatial domain: score * 0.032 * 1.25
        if "ref_noise_score" in locals() and ref_noise_score is not None:
            auto_noise_sigma = float(np.clip(ref_noise_score * 0.040, 1e-4, 0.99999))
        else:
            try:
                from taichi_vision.taichi_algorithm.enhancement.estimate_noise import (
                    estimate_noise,
                )

                gpu_score = float(estimate_noise(ref_spatial_v1_gpu))
                auto_noise_sigma = float(np.clip(gpu_score * 0.040, 1e-4, 0.99999))
            except Exception as exc:
                raise RuntimeError(
                    "Taichi estimate_noise failed for SpatialFusion: " f"{exc}"
                ) from exc

        if ref_spatial_v1_gpu is not ref_analysis_gpu:
            ref_spatial_v1_gpu.destroy()

        explicit_noise_sigma = cfg.get("noise_sigma")
        if explicit_noise_sigma is not None and float(explicit_noise_sigma) > 0.0:
            spatial_noise_sigma = float(explicit_noise_sigma)
        else:
            spatial_noise_sigma = auto_noise_sigma

        pass
        spatial_row_starts = _compute_tile_starts(
            spatial_work_h, spatial_tile_h, overlap=spatial_overlap
        )
        spatial_col_starts = _compute_tile_starts(
            spatial_work_w, spatial_tile_w, overlap=spatial_overlap
        )
        spatial_rows_gpu = taichi_aot.upload(
            np.asarray(spatial_row_starts, dtype=np.int32)
        )
        spatial_cols_gpu = taichi_aot.upload(
            np.asarray(spatial_col_starts, dtype=np.int32)
        )
        spatial_scratch = SpatialScratchCache()

    elif weight_engine == "average":
        # Average does not cross an ONNX analysis boundary.  Keep the
        # reference entirely GPU-resident and avoid a work-resolution host
        # copy that would otherwise be discarded by the worker.
        ref_work_rgb_np = None
    else:
        # Work-resolution copy for ONNX WeightNet inference
        if tuple(int(value) for value in ref_analysis_gpu.shape[:2]) != (
            work_h,
            work_w,
        ):
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

    def _prepare_spatial_weight_gray_gpu(source_gray_gpu):
        """Downsample only the already-aligned analysis luma for SpatialFusion.

        Alignment keeps the higher ``work_h x work_w`` domain.  Spatial
        weights are confidence metadata, so they can use the bounded lower
        analysis domain while the linear RGB fusion remains full resolution.
        """
        if tuple(int(value) for value in source_gray_gpu.shape[:2]) == (
            spatial_work_h,
            spatial_work_w,
        ):
            return source_gray_gpu
        return taichi_aot.resize(
            source_gray_gpu,
            (spatial_work_w, spatial_work_h),
            interpolation=taichi_aot.INTER_AREA,
            return_gpu=True,
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
        ref_analysis_gpu,
        work_scale=work_scale,
        full_shape=(target_h, target_w),
        alignment_config=alignment_config,
    )

    # The streaming primary path is deliberately opt-in by capability, not
    # by assumption.  If the fused remap/accumulation graph is missing from
    # the active target artifact, the aligner keeps the established
    # same-backend full-frame route.
    splat_tile_size = None
    stream_root_cfg = alignment_config if isinstance(alignment_config, dict) else {}
    stream_cfg = stream_root_cfg
    try:
        if isinstance(stream_cfg.get("block_matching_gpu_params"), dict):
            block_matching_cfg = stream_cfg["block_matching_gpu_params"]
        else:
            block_matching_cfg = stream_cfg
        splat_tile_size = max(
            32,
            int(
                block_matching_cfg.get(
                    "splat_tile_size",
                    stream_root_cfg.get(
                        "splat_tile_size",
                        os.environ.get("PIXEL_REFINE_RESIDENT_SPLAT_TILE_SIZE", ""),
                    ),
                )
            ),
        )
    except (TypeError, ValueError):
        splat_tile_size = None
    if splat_tile_size is None:
        configured_size = performance_block_settings.get("block_size")
        if configured_size is None:
            configured_size = max(
                int(value) for value in engine.get_block_config().normalized_size()
            )
        splat_tile_size = max(32, int(configured_size))

    stream_primary = False
    if isinstance(aligner, BlockMatchingGPUResidentAligner):
        try:
            from taichi_vision.taichi_algorithm.aot_api import aot_graph_available

            stream_requested = stream_root_cfg.get(
                "stream_primary",
                stream_root_cfg.get(
                    "resident_tile_streaming",
                    block_matching_cfg.get(
                        "stream_primary",
                        block_matching_cfg.get("resident_tile_streaming", True),
                    ),
                ),
            )
            if isinstance(stream_requested, str):
                stream_requested = stream_requested.strip().lower() not in {
                    "0",
                    "false",
                    "off",
                    "no",
                    "disabled",
                }
            fused_splat_graph = (
                "remap_accumulate_average_tile"
                if weight_engine == "average"
                else (
                    "remap_accumulate_spatial_tile"
                    if weight_engine == "spatial_fusion"
                    else "remap_accumulate_spatial_vec3_tile"
                )
            )
            stream_primary = bool(
                stream_requested
                and int(target_h) * int(target_w) >= 4_000_000
                and aot_graph_available("spatial_fusion", fused_splat_graph)
            )
        except Exception as exc:
            pass
            stream_primary = False

    if stream_primary:
        pass
    elif isinstance(aligner, BlockMatchingGPUResidentAligner):
        pass

    accumulation_plan = _resolve_resident_accumulation_plan(
        engine,
        mode=accumulation_mode,
        weight_engine=weight_engine,
        shape=(target_h, target_w),
        requested_tile_size=splat_tile_size,
        performance_block_size=performance_block_settings.get("block_size"),
        performance_threshold_mp=performance_block_settings.get("threshold_mp"),
    )
    block_accumulation = bool(accumulation_plan.get("enabled"))
    if block_accumulation:
        splat_tile_size = int(accumulation_plan["tile_size"])
        print(
            f"[GPU Pipeline] Block accumulation active: tile={splat_tile_size} "
            f"source=Performance Settings "
            f"pressure={accumulation_plan.get('memory_pressure', 'healthy')}"
        )
    else:
        print(
            "[GPU Pipeline] Full-frame accumulation retained: "
            f"{accumulation_plan.get('reason', 'block path unavailable')}"
        )

    if ref_analysis_gpu is not ref_gpu:
        ref_analysis_gpu.destroy()

    # ------------------------------------------------------------------
    # PHASE 5: Initialize GPU accumulators with 100% True Linear RAW Reference
    # ------------------------------------------------------------------
    # Directly use ref_gpu as sum_img_gpu accumulator to save 144MB VRAM
    sum_img_gpu = ref_gpu
    if use_uniform_weight_accumulation := weight_engine == "average":
        # Uniform averaging only needs the scalar number of accepted frames.
        # The block path therefore avoids a full RGB all-ones weight buffer.
        weight_sum_gpu = None if block_accumulation else engine.upload(
            np.ones((target_h, target_w, 3), dtype=np.float32)
        )
    elif weight_engine == "spatial_fusion":
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
    # A full-resolution float32 RGB frame is expensive on both sides of the
    # pipeline.  The old value came directly from ``batch_size`` and could
    # therefore retain several decoded 12-24 MP frames in the preloader queue
    # while the GPU still held the reference, aligned frame, and accumulators.
    # Keep at most the amount that fits in a small host staging budget.  The
    # environment override is intentionally explicit for controlled
    # benchmarking; production defaults to one large frame in flight.
    requested_q_depth = max(1, int(batch_queue))
    try:
        host_queue_budget_mb = max(
            64,
            int(os.environ.get("PIXEL_REFINE_RESIDENT_HOST_QUEUE_MB", "256")),
        )
    except (TypeError, ValueError):
        host_queue_budget_mb = 256
    frame_host_bytes = max(
        1, int(target_h) * int(target_w) * 3 * np.dtype(np.float32).itemsize
    )
    host_queue_capacity = max(
        1,
        int((host_queue_budget_mb * 1024 * 1024) // frame_host_bytes),
    )
    q_depth = min(requested_q_depth, host_queue_capacity)

    pass

    if progress_callback:
        progress_callback(
            PROGRESS_MERGE_MIN,
            ui="Menyiapkan Pipeline...",
            console=f"Memulai Pipeline Asynchronous Flow (host_queue={q_depth}, gpu_in_flight=1)...",
        )

    _SENTINEL = object()
    preloaded_queue = queue.Queue(maxsize=q_depth)  # Host RAM queue (0 MB VRAM)
    aligned_queue = queue.Queue(
        maxsize=1
    )  # Aligned queue (strictly 1 GPU frame in-flight max)
    weighted_queue = queue.Queue(
        maxsize=1
    )  # Weighted queue (strictly 1 GPU frame in-flight max)
    average_direct_to_blend = weight_engine == "average" and not alignment_only
    alignment_output_queue = (
        weighted_queue if average_direct_to_blend else aligned_queue
    )

    pass

    pipeline_error = None
    pipeline_lock = threading.Lock()
    gpu_hardware_lock = threading.Lock()

    # ``destroy()`` is deliberately asynchronous in the AOT engine.  Reclaim
    # only at a safe point and only when lifecycle buffers are accumulating;
    # clearing the pool for every frame would trade the memory fix for costly
    # repeated allocations.  Live accumulators remain resident throughout.
    reclaim_threshold = max(
        64 * 1024 * 1024,
        min(256 * 1024 * 1024, frame_host_bytes),
    )

    def _reclaim_idle_buffers(stage):
        try:
            status = engine.get_memory_status(force=True)
            lifecycle_bytes = (
                int(status.get("pooled_bytes", 0) or 0)
                + int(status.get("retired_bytes", 0) or 0)
                + int(status.get("staging_bytes", 0) or 0)
            )
            pressure = str(status.get("pressure", "healthy")).lower()
            if lifecycle_bytes < reclaim_threshold and pressure not in (
                "critical",
                "emergency",
            ):
                return

            # The reclaim contract requires a synchronization safe-point.
            engine.sync()
            reclaimed = engine.reclaim_resident_buffers(reason=str(stage))
            after = reclaimed.get("after", {})
            pass
        except Exception as exc:
            # Reclaim is an optimization/safety valve.  Never hide the main
            # pipeline error when a backend does not expose the optional API.
            pass

    _reclaim_idle_buffers("reference_analysis")

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
    # Worker 1: Disk Preloader (queues paths; decode/upload stays bounded)
    # ------------------------------------------------------------------
    def _preloader_worker():
        try:
            for idx in range(1, num_images):
                if _is_stopped() or pipeline_error is not None:
                    break
                f_path = image_paths[idx]
                f_name = Path(f_path).name
                while not _is_stopped():
                    if pipeline_error is not None:
                        return
                    try:
                        # Queue only a path.  Keeping decoded 12 MP float32
                        # frames in the host queue duplicates the resident
                        # upload and can grow RSS by hundreds of MiB.  The
                        # alignment worker decodes directly through the same
                        # Hamilton/standard loader used by this pipeline.
                        preloaded_queue.put((idx, f_name, f_path), timeout=0.05)
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

                curr_idx, curr_name, supp_path = item

                with gpu_hardware_lock:
                    if _is_stopped():
                        break
                    supp_linear_gpu, supp_analysis_work_gpu, secondary_frame_to_warp = (
                        _prepare_support_frame(
                            supp_path,
                            is_raw=is_raw,
                            target_h=target_h,
                            target_w=target_w,
                            analysis_box_kernel_size=analysis_box_kernel_size,
                            weight_engine=weight_engine,
                            prepare_work_analysis_fn=_prepare_work_analysis_gpu,
                        )
                    )
                    supp_analysis_gpu = supp_analysis_work_gpu

                    aligned_result = aligner.align_frame(
                        supp_linear_gpu,
                        analysis_frame_gpu=supp_analysis_work_gpu,
                        secondary_frame_to_warp=secondary_frame_to_warp,
                        stop_event=stop_event,
                        return_gpu=True,
                        stream_primary=stream_primary,
                    )
                    supp_aligned_linear_gpu, supp_aligned_analysis_work_gpu = (
                        _unpack_aligned_result(
                            aligned_result,
                            secondary_frame_to_warp=secondary_frame_to_warp,
                            supp_linear_gpu=supp_linear_gpu,
                            supp_analysis_gpu=supp_analysis_gpu,
                            supp_analysis_work_gpu=supp_analysis_work_gpu,
                        )
                    )

                    if weight_engine == "spatial_fusion":
                        # SpatialFusion analyzes via AutoEnhance v1 (High-Key Analysis Mode)
                        supp_work_gray_gpu = taichi_aot.cvtColor(
                            supp_aligned_analysis_work_gpu, taichi_aot.COLOR_RGB2GRAY
                        )
                        supp_aligned_analysis_work_gpu.destroy()
                        supp_work_item = supp_work_gray_gpu
                    elif weight_engine == "average":
                        if (
                            supp_aligned_analysis_work_gpu is not None
                            and supp_aligned_analysis_work_gpu
                            is not supp_aligned_linear_gpu
                        ):
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
                        if average_direct_to_blend:
                            alignment_output_queue.put(
                                (
                                    curr_idx,
                                    curr_name,
                                    supp_aligned_linear_gpu,
                                    None,
                                    1.0,
                                ),
                                timeout=0.05,
                            )
                        else:
                            alignment_output_queue.put(
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
            alignment_output_queue.put(_SENTINEL)

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
                        supp_work_gray_gpu = supp_work_item
                        spatial_weight_input_gpu = _prepare_spatial_weight_gray_gpu(
                            supp_work_gray_gpu
                        )
                        weight_work_2d_gpu = engine.allocate(
                            (spatial_work_h, spatial_work_w),
                            dtype=np.float32,
                            host_accessible=False,
                        )
                        generate_spatial_weights_taichi(
                            current_image=spatial_weight_input_gpu,
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
                            coarse_texture_boost=spatial_texture_boost,
                            coarse_texture_radius=spatial_texture_radius,
                            coarse_pyramid_single_pass=spatial_single_coarse,
                        )
                        spatial_weight_input_gpu.destroy()
                        if spatial_weight_input_gpu is not supp_work_gray_gpu:
                            supp_work_gray_gpu.destroy()
                        weight_work_item = _postprocess_spatial_weight_gpu(
                            weight_work_2d_gpu,
                            ghost_penalty=ghost_penalty,
                            ghost_cutoff=ghost_cutoff,
                        )
                        alpha_mean = 1.0
                    elif weight_engine == "average":
                        # Uniform averaging uses the dedicated native graph;
                        # no work-resolution all-ones map is required.
                        weight_work_item = None
                        alpha_mean = 1.0

                # WeightNet consumes the already downloaded work-resolution
                # NumPy pair. Do not hold the AOT lock during ONNX inference;
                # this allows the alignment worker to prepare the next frame.
                if weight_engine not in ("spatial_fusion", "average"):
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

    accumulator_normalized = False
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

                curr_idx, curr_name, supp_path = item
                if _is_stopped():
                    break

                supp_linear_gpu, supp_analysis_work_gpu, secondary_frame_to_warp = (
                    _prepare_support_frame(
                        supp_path,
                        is_raw=is_raw,
                        target_h=target_h,
                        target_w=target_w,
                        analysis_box_kernel_size=analysis_box_kernel_size,
                        weight_engine=weight_engine,
                        prepare_work_analysis_fn=_prepare_work_analysis_gpu,
                    )
                )
                supp_analysis_gpu = supp_analysis_work_gpu

                aligned_result = aligner.align_frame(
                    supp_linear_gpu,
                    analysis_frame_gpu=supp_analysis_work_gpu,
                    secondary_frame_to_warp=secondary_frame_to_warp,
                    stop_event=stop_event,
                    return_gpu=True,
                    stream_primary=stream_primary,
                )
                supp_aligned_linear_gpu, supp_aligned_analysis_work_gpu = (
                    _unpack_aligned_result(
                        aligned_result,
                        secondary_frame_to_warp=secondary_frame_to_warp,
                        supp_linear_gpu=supp_linear_gpu,
                        supp_analysis_gpu=supp_analysis_gpu,
                        supp_analysis_work_gpu=supp_analysis_work_gpu,
                    )
                )

                weight_work_item, alpha_mean = _compute_support_weight(
                    supp_aligned_analysis_work_gpu,
                    supp_aligned_linear_gpu,
                    weight_engine=weight_engine,
                    engine=engine,
                    session=session,
                    ref_work_rgb_np=ref_work_rgb_np,
                    spatial_work_h=spatial_work_h,
                    spatial_work_w=spatial_work_w,
                    ref_spatial_gray_gpu=ref_spatial_gray_gpu,
                    spatial_row_starts=spatial_row_starts,
                    spatial_col_starts=spatial_col_starts,
                    spatial_rows_gpu=spatial_rows_gpu,
                    spatial_cols_gpu=spatial_cols_gpu,
                    spatial_tile_h=spatial_tile_h,
                    spatial_tile_w=spatial_tile_w,
                    spatial_noise_sigma=spatial_noise_sigma,
                    spatial_motion_sens=spatial_motion_sens,
                    spatial_noise_offset=spatial_noise_offset,
                    spatial_texture_boost=spatial_texture_boost,
                    spatial_texture_radius=spatial_texture_radius,
                    spatial_single_coarse=spatial_single_coarse,
                    spatial_scratch=spatial_scratch,
                    ghost_penalty=ghost_penalty,
                    ghost_cutoff=ghost_cutoff,
                    tile_size=tile_size,
                    overlap=overlap,
                    chroma_sensitivity=chroma_sensitivity,
                    stop_event=stop_event,
                )

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

                if use_uniform_weight_accumulation:
                    weight_work_gpu = None
                elif isinstance(weight_work_item, taichi_aot.TaichiGPUBuffer):
                    weight_work_gpu = weight_work_item
                else:
                    weight_work_gpu = engine.upload(weight_work_item)
                    del weight_work_item

                accumulator_normalized = _gpu_blend_frame(
                    sum_img_gpu,
                    weight_sum_gpu,
                    supp_aligned_linear_gpu,
                    weight_work_gpu,
                    splat_tile_size=splat_tile_size,
                    uniform_weights=use_uniform_weight_accumulation,
                    block_accumulation=block_accumulation,
                    finalize=processed_count == total_supp,
                    uniform_denominator=float(processed_count + 1),
                ) or accumulator_normalized

                supp_aligned_linear_gpu.destroy()
                if weight_work_gpu is not None:
                    weight_work_gpu.destroy()
                # ``_reclaim_idle_buffers`` below provides the synchronization
                # safe-point when lifecycle pressure requires it.  Avoid an
                # unconditional barrier after every frame.
                _reclaim_idle_buffers(f"frame_{curr_idx}")

                print(
                    f"[GPU Pipeline] Frame {curr_idx}/{total_supp} ({curr_name}) blended (alpha={alpha_mean:.3f})"
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
        if (
            not alignment_only
            and weight_engine != "average"
            and (session is not None or weight_engine == "spatial_fusion")
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
            if weight_sum_gpu is not None:
                weight_sum_gpu.destroy()
            if ref_spatial_gray_gpu is not None:
                ref_spatial_gray_gpu.destroy()
            if spatial_rows_gpu is not None:
                spatial_rows_gpu.destroy()
            if spatial_cols_gpu is not None:
                spatial_cols_gpu.destroy()
            if spatial_scratch is not None:
                spatial_scratch.clear()
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

                    if use_uniform_weight_accumulation:
                        weight_work_gpu = None
                    elif isinstance(weight_work_item, taichi_aot.TaichiGPUBuffer):
                        weight_work_gpu = weight_work_item
                    else:
                        weight_work_gpu = engine.upload(weight_work_item)
                        del weight_work_item

                    accumulator_normalized = _gpu_blend_frame(
                        sum_img_gpu,
                        weight_sum_gpu,
                        supp_aligned_linear_gpu,
                        weight_work_gpu,
                        splat_tile_size=splat_tile_size,
                        uniform_weights=use_uniform_weight_accumulation,
                        block_accumulation=block_accumulation,
                        finalize=processed_count == total_supp,
                        uniform_denominator=float(processed_count + 1),
                    ) or accumulator_normalized

                    supp_aligned_linear_gpu.destroy()
                if weight_work_gpu is not None:
                    weight_work_gpu.destroy()
                # Memory reclamation owns the conditional synchronization
                # safe-point; do not serialize every support frame here.
                _reclaim_idle_buffers(f"frame_{curr_idx}")

                print(
                    f"[GPU Pipeline] Frame {curr_idx}/{total_supp} ({curr_name}) blended (alpha={alpha_mean:.3f})"
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
                    if weight_sum_gpu is not None:
                        weight_sum_gpu.destroy()
                    ref_gpu.destroy()
                    aligner.close()
                    if ref_spatial_gray_gpu is not None:
                        ref_spatial_gray_gpu.destroy()
                    if spatial_rows_gpu is not None:
                        spatial_rows_gpu.destroy()
                    if spatial_cols_gpu is not None:
                        spatial_cols_gpu.destroy()
                    if spatial_scratch is not None:
                        spatial_scratch.clear()
                except Exception:
                    pass
                try:
                    engine.sync()
                    engine.get_device_block_cache().clear()
                except Exception:
                    pass
                gc.collect()

    if _is_stopped():
        print(
            "[GPU Pipeline] Process cancelled by user. Discarded in-flight computation & released GPU memory."
        )
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

    _final_linear_gpu = None
    normalization_report = None
    if block_accumulation and accumulator_normalized:
        _final_linear_gpu = sum_img_gpu
        normalization_report = {
            "tile_shape": (splat_tile_size, splat_tile_size),
            "dispatches": (
                ((target_h + splat_tile_size - 1) // splat_tile_size)
                * ((target_w + splat_tile_size - 1) // splat_tile_size)
            ),
        }
        engine.set_last_block_execution(
            {
                "operation": "resident_accumulate_normalize",
                "selected": True,
                "backend": str(getattr(engine, "arch", "")),
                "shape": (target_h, target_w, 3),
                "tile_shape": normalization_report["tile_shape"],
                "computed": normalization_report["dispatches"],
                "fallback": "none",
                "normalization": "fused_last_frame",
            }
        )
    elif block_accumulation:
        try:
            from taichi_vision.taichi_algorithm.spatial_fusion import (
                normalize_accumulator_regions_taichi,
            )

            with taichi_aot.compute_block(
                block_size=(splat_tile_size, splat_tile_size),
                halo=0,
                mode="force",
                fallback="error",
                cache=False,
            ):
                normalization_report = normalize_accumulator_regions_taichi(
                    sum_img_gpu,
                    weight_sum_gpu,
                    uniform_weight=(processed_count + 1)
                    if use_uniform_weight_accumulation
                    else None,
                )
            _final_linear_gpu = sum_img_gpu
            engine.set_last_block_execution(
                {
                    "operation": "resident_accumulate_normalize",
                    "selected": True,
                    "backend": str(getattr(engine, "arch", "")),
                    "shape": (target_h, target_w, 3),
                    "tile_shape": normalization_report["tile_shape"],
                    "computed": normalization_report["dispatches"],
                    "fallback": "none",
                }
            )
        except Exception as exc:
            # Keep recovery on the active backend.  For Average, reconstruct
            # the uniform denominator only on this exceptional path.
            print(
                "[GPU Pipeline] Block normalization unavailable; "
                f"using same-backend full-frame recovery ({exc})."
            )
            if weight_sum_gpu is None:
                weight_sum_gpu = engine.upload(
                    np.full(
                        (target_h, target_w, 3),
                        float(processed_count + 1),
                        dtype=np.float32,
                    )
                )
            engine.set_last_block_execution(
                {
                    "operation": "resident_accumulate_normalize",
                    "selected": False,
                    "backend": str(getattr(engine, "arch", "")),
                    "shape": (target_h, target_w, 3),
                    "fallback": "same_backend_full_frame",
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )

    if _final_linear_gpu is None:
        if len(weight_sum_gpu.shape) == 2:
            _final_linear_gpu = taichi_aot.mean_division(
                sum_img=sum_img_gpu,
                sum_weight=weight_sum_gpu,
                ref_img=ref_gpu,
            )
        else:
            from taichi_vision.taichi_algorithm.spatial_fusion import (
                mean_division_vec3_weight_taichi,
            )

            _final_linear_gpu = mean_division_vec3_weight_taichi(
                sum_img=sum_img_gpu,
                sum_weight=weight_sum_gpu,
                ref_img=ref_gpu,
            )

    result_hwc = np.ascontiguousarray(_final_linear_gpu.to_numpy(), dtype=np.float32)
    if _final_linear_gpu is not sum_img_gpu:
        _final_linear_gpu.destroy()

    # Cleanup GPU resources and flush buffer pool back to baseline
    try:
        sum_img_gpu.destroy()
        if weight_sum_gpu is not None:
            weight_sum_gpu.destroy()
        ref_gpu.destroy()
        aligner.close()
        if ref_spatial_gray_gpu is not None:
            ref_spatial_gray_gpu.destroy()
        if spatial_rows_gpu is not None:
            spatial_rows_gpu.destroy()
        if spatial_cols_gpu is not None:
            spatial_cols_gpu.destroy()
        if spatial_scratch is not None:
            spatial_scratch.clear()
    except Exception:
        pass
    del ref_work_rgb_np
    try:
        engine.sync()
        if hasattr(engine, "reclaim_resident_buffers"):
            engine.reclaim_resident_buffers(reason="pipeline_complete")
        else:
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
        f"[GPU Pipeline] Complete: {result_hwc.shape[1]}x{result_hwc.shape[0]} | Mean Alpha: {mean_alpha:.4f}"
    )

    return result_hwc, mean_alpha


# Canonical alias
run_resident_pipeline = run_gpu_resident_pipeline
