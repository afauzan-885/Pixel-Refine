"""GPU-resident dense optical-flow aligners for the resident pipeline.

Block Matching, Lucas-Kanade, and Farneback each keep a native reference
pyramid alive for the whole burst and reuse one resident flow destination.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from taichi_vision.taichi_aot import TaichiGPUBuffer, get_engine

from ..facade import api as _facade
from .base import _ResidentFlowBufferMixin

__all__ = [
    "BlockMatchingResidentAligner",
    "LucasKanadeResidentAligner",
    "FarnebackResidentAligner",
]


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
        taichi_aot = _facade()._managed_api(taichi_aot)
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
                session=_facade()._buffer_session(),
            )
        )
        # The native pyramid returns L0 as the caller-owned reference buffer.
        # Keep a single ownership path so close() cannot double-retire it.
        self.ref_gray_gpu = self.reference_pyramid[0]
        from taichi_vision.taichi_algorithm.aot_wrapper import FlowScratchCache
        self._flow_scratch = FlowScratchCache()
        print(
            "[GPU Pipeline] Aligner: Block Matching GPU "
            f"(mode={mode}, window={self.config.get('win_size')}, "
            f"levels={len(self.reference_pyramid)}, resident-reference=true, scratch-cache=true)"
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
        taichi_aot = _facade()._managed_api(taichi_aot)
        from taichi_vision.taichi_algorithm import calcOpticalFlowBlockMatching

        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Block Matching alignment cancelled.")
            if callable(stop_event) and stop_event():
                raise RuntimeError("Block Matching alignment cancelled.")

        source = analysis_frame_gpu if analysis_frame_gpu is not None else supp_linear_gpu
        supp_gray_scratch = getattr(self, "_supp_gray_scratch", None)
        if (
            supp_gray_scratch is None
            or getattr(supp_gray_scratch, "handle", None) is None
            or tuple(int(v) for v in getattr(supp_gray_scratch, "shape", ())) != (self.work_h, self.work_w)
        ):
            if supp_gray_scratch is not None:
                _facade()._destroy_work_item(supp_gray_scratch)
            engine = get_engine()
            self._supp_gray_scratch = _facade()._own_component(
                engine.allocate((self.work_h, self.work_w), dtype=np.float32, host_accessible=False)
            )
            supp_gray_scratch = self._supp_gray_scratch

        supp_gray_gpu = taichi_aot.cvtColor(
            source,
            taichi_aot.COLOR_RGB2GRAY,
            dst=supp_gray_scratch if tuple(source.shape[:2]) == (self.work_h, self.work_w) else None,
            return_gpu=True,
        )
        flow_gpu = None
        try:
            if tuple(supp_gray_gpu.shape[:2]) != (self.work_h, self.work_w):
                resized = taichi_aot.resize(
                    supp_gray_gpu,
                    (self.work_w, self.work_h),
                    interpolation=taichi_aot.INTER_AREA,
                    return_gpu=True,
                    dst=supp_gray_scratch,
                )
                if supp_gray_gpu is not supp_gray_scratch:
                    _facade()._destroy_work_item(supp_gray_gpu)
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
                scratch=getattr(self, "_flow_scratch", None),
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
                _facade()._destroy_work_item(flow_gpu)
            if supp_gray_gpu is not None and supp_gray_gpu is not getattr(self, "_supp_gray_scratch", None) and hasattr(supp_gray_gpu, "destroy"):
                _facade()._destroy_work_item(supp_gray_gpu)

    def close(self):
        # L0 is the same object as ``ref_gray_gpu``; destroy every pyramid
        # level exactly once so the allocator can reuse or retire it safely.
        for buffer in getattr(self, "reference_pyramid", ()):
            try:
                if buffer is not None and hasattr(buffer, "destroy"):
                    _facade()._destroy_work_item(buffer)
            except Exception:
                pass
        self.reference_pyramid = ()
        self.ref_gray_gpu = None
        if hasattr(self, "_supp_gray_scratch") and self._supp_gray_scratch is not None:
            _facade()._destroy_work_item(self._supp_gray_scratch)
            self._supp_gray_scratch = None
        if hasattr(self, "_flow_scratch") and self._flow_scratch is not None:
            self._flow_scratch.clear()
            self._flow_scratch = None
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
        taichi_aot = _facade()._managed_api(taichi_aot)
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
                session=_facade()._buffer_session(),
            )
        )
        self.ref_gray_gpu = self.reference_pyramid[0]
        from taichi_vision.taichi_algorithm.aot_wrapper import FlowScratchCache
        self._flow_scratch = FlowScratchCache()
        print(
            "[GPU Pipeline] Aligner: Lucas Kanade GPU "
            f"(mode={mode}, window={self.config.get('win_size')}, "
            f"levels={len(self.reference_pyramid)}, resident-reference=true, scratch-cache=true)"
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
        taichi_aot = _facade()._managed_api(taichi_aot)
        from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLK

        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Lucas Kanade alignment cancelled.")
            if callable(stop_event) and stop_event():
                raise RuntimeError("Lucas Kanade alignment cancelled.")

        source = analysis_frame_gpu if analysis_frame_gpu is not None else supp_linear_gpu
        supp_gray_scratch = getattr(self, "_supp_gray_scratch", None)
        if (
            supp_gray_scratch is None
            or getattr(supp_gray_scratch, "handle", None) is None
            or tuple(int(v) for v in getattr(supp_gray_scratch, "shape", ())) != (self.work_h, self.work_w)
        ):
            if supp_gray_scratch is not None:
                _facade()._destroy_work_item(supp_gray_scratch)
            engine = get_engine()
            self._supp_gray_scratch = _facade()._own_component(
                engine.allocate((self.work_h, self.work_w), dtype=np.float32, host_accessible=False)
            )
            supp_gray_scratch = self._supp_gray_scratch

        supp_gray_gpu = taichi_aot.cvtColor(
            source,
            taichi_aot.COLOR_RGB2GRAY,
            dst=supp_gray_scratch if tuple(source.shape[:2]) == (self.work_h, self.work_w) else None,
            return_gpu=True,
        )
        flow_gpu = None
        try:
            if tuple(supp_gray_gpu.shape[:2]) != (self.work_h, self.work_w):
                resized = taichi_aot.resize(
                    supp_gray_gpu,
                    (self.work_w, self.work_h),
                    interpolation=taichi_aot.INTER_AREA,
                    return_gpu=True,
                    dst=supp_gray_scratch,
                )
                if supp_gray_gpu is not supp_gray_scratch:
                    _facade()._destroy_work_item(supp_gray_gpu)
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
                scratch=getattr(self, "_flow_scratch", None),
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
                _facade()._destroy_work_item(flow_gpu)
            if supp_gray_gpu is not None and supp_gray_gpu is not getattr(self, "_supp_gray_scratch", None) and hasattr(supp_gray_gpu, "destroy"):
                _facade()._destroy_work_item(supp_gray_gpu)

    def close(self):
        for buffer in getattr(self, "reference_pyramid", ()):
            try:
                if buffer is not None and hasattr(buffer, "destroy"):
                    _facade()._destroy_work_item(buffer)
            except Exception:
                pass
        self.reference_pyramid = ()
        self.ref_gray_gpu = None
        if hasattr(self, "_supp_gray_scratch") and self._supp_gray_scratch is not None:
            _facade()._destroy_work_item(self._supp_gray_scratch)
            self._supp_gray_scratch = None
        if hasattr(self, "_flow_scratch") and self._flow_scratch is not None:
            self._flow_scratch.clear()
            self._flow_scratch = None
        self._close_resident_flow_buffer()


def _scale_f32_scalar_gpu(source_gpu, scale: float):
    """Scale a scalar f32 resident buffer without a host round-trip."""
    from taichi_vision import taichi_aot
    taichi_aot = _facade()._managed_api(taichi_aot)
    from taichi_vision.taichi_algorithm.aot_api import _mod

    output = _facade()._managed_api(taichi_aot.get_engine()).allocate(
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
        taichi_aot = _facade()._managed_api(taichi_aot)
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
            _facade()._destroy_work_item(ref_gray_unit_gpu)
        self.work_h, self.work_w = (int(self.ref_gray_gpu.shape[0]), int(self.ref_gray_gpu.shape[1]))
        levels = max(1, int(self.config.get("levels", 3)))
        self.reference_pyramid = tuple(
            build_image_pyramid_gpu(self.ref_gray_gpu, n_levels=levels, min_size=32, session=_facade()._buffer_session())
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
        taichi_aot = _facade()._managed_api(taichi_aot)

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
            _facade()._destroy_work_item(supp_gray_unit_gpu)
            supp_gray_unit_gpu = None
            if tuple(supp_gray_gpu.shape[:2]) != (self.work_h, self.work_w):
                resized = taichi_aot.resize(
                    supp_gray_gpu, (self.work_w, self.work_h),
                    interpolation=taichi_aot.INTER_AREA, return_gpu=True,
                )
                _facade()._destroy_work_item(supp_gray_gpu)
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
                _facade()._destroy_work_item(flow_gpu)
            if supp_gray_gpu is not None and supp_gray_gpu is not getattr(self, "_supp_gray_scratch", None) and hasattr(supp_gray_gpu, "destroy"):
                _facade()._destroy_work_item(supp_gray_gpu)
            if supp_gray_unit_gpu is not None and hasattr(supp_gray_unit_gpu, "destroy"):
                _facade()._destroy_work_item(supp_gray_unit_gpu)

    def close(self):
        for buffer in getattr(self, "reference_pyramid", ()):
            try:
                if buffer is not None and hasattr(buffer, "destroy"):
                    _facade()._destroy_work_item(buffer)
            except Exception:
                pass
        self.reference_pyramid = ()
        self.ref_gray_gpu = None
        self._close_resident_flow_buffer()
