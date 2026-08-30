"""
Taichi AOT Native Optical Flow Alignment Engine (compute_flow.tcm).
Computes dense hierarchical optical flow (dx, dy) between reference and support frames
using Taichi AOT 3-layer coarse-to-fine pyramid alignment (compute_flow.tcm)
and warps support frames with Taichi AOT native remap_with_flow.
"""

import gc
import os
import threading
from pathlib import Path
from typing import Callable, Optional, Tuple, Union

import numpy as np

_MODULE_CACHE = {}


def load_compute_flow_module(engine=None):
    """Loads and caches the compute_flow AOT module on the active Taichi engine."""
    from taichi_vision import taichi_aot

    return taichi_aot.load_tcm("compute_flow")


def _build_gray_pyramid_taichi(
    image_rgb_f32: np.ndarray,
    work_res_h: int,
    work_res_w: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Builds a 3-layer 2D grayscale float32 pyramid (L0, L1, L2) with guaranteed field_dim=2.
    """
    from taichi_vision import taichi_aot

    # 1. RGB to Grayscale Luma (Taichi AOT cvtColor)
    if image_rgb_f32.ndim == 3 and image_rgb_f32.shape[2] == 3:
        try:
            gray = taichi_aot.cvtColor(image_rgb_f32, taichi_aot.COLOR_RGB2GRAY)
        except Exception:
            gray = (
                0.299 * image_rgb_f32[..., 0]
                + 0.587 * image_rgb_f32[..., 1]
                + 0.114 * image_rgb_f32[..., 2]
            ).astype(np.float32)
    elif image_rgb_f32.ndim == 2:
        gray = image_rgb_f32.astype(np.float32)
    else:
        gray = image_rgb_f32[..., 0].astype(np.float32)

    # 2. Contrast normalization for dark linear images
    max_val = float(np.percentile(gray, 99.0)) if gray.size > 0 else 1.0
    if 1e-4 < max_val < 0.8:
        gray = np.clip(gray / max_val, 0.0, 1.0)
    else:
        gray = np.clip(gray, 0.0, 1.0)

    # 3. L0: 2D work resolution (work_res_h, work_res_w)
    if gray.shape[:2] != (work_res_h, work_res_w):
        l0 = taichi_aot.resize(gray, (work_res_w, work_res_h), interpolation=taichi_aot.INTER_AREA)
    else:
        l0 = gray
    l0 = np.ascontiguousarray(l0.reshape(work_res_h, work_res_w), dtype=np.float32)

    # 4. L1: 1/2 scale (h1, w1)
    h1, w1 = max(16, work_res_h // 2), max(16, work_res_w // 2)
    l1 = taichi_aot.resize(l0, (w1, h1), interpolation=taichi_aot.INTER_AREA)
    l1 = np.ascontiguousarray(l1.reshape(h1, w1), dtype=np.float32)

    # 5. L2: 1/4 scale (h2, w2)
    h2, w2 = max(8, work_res_h // 4), max(8, work_res_w // 4)
    l2 = taichi_aot.resize(l1, (w2, h2), interpolation=taichi_aot.INTER_AREA)
    l2 = np.ascontiguousarray(l2.reshape(h2, w2), dtype=np.float32)

    return l0, l1, l2


class AOTOpticalFlowAligner:
    """
    Persistent AOT Optical Flow Alignment Session.
    Pre-computes reference pyramid to minimize redundant computation and executes
    isolated compute_flow.tcm graph seamlessly across all hardware backends.
    """

    def __init__(
        self,
        ref_rgb_f32: np.ndarray,
        *,
        work_scale: float = 0.50,
        tile_size: int = 16,
        search_dist: int = 2,
        max_search_radius: int = 12,
    ):
        from taichi_vision.taichi_aot import get_engine
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import (
            taichi_bridge,
        )

        self.engine = get_engine()
        self.mod = load_compute_flow_module(self.engine)

        self.full_h, self.full_w = ref_rgb_f32.shape[:2]
        self.work_res_h = max(32, int(self.full_h * float(work_scale)))
        self.work_res_w = max(32, int(self.full_w * float(work_scale)))

        self.tile_size = int(tile_size)
        self.search_dist = int(search_dist)
        self.max_search_radius = int(max_search_radius)

        # Pre-compute Reference Pyramid 100% in GPU Dedicated VRAM
        self.ref_pyramid = taichi_bridge.prepare_reference_for_alignment(
            ref_rgb_f32,
            is_linear_mode=False,
            proxy_scale=1.0,
            work_res_h=self.work_res_h,
            work_res_w=self.work_res_w,
            num_layers=3,
        )
        self.ref_l0 = self.ref_pyramid[0]
        self.ref_l1 = self.ref_pyramid[1]
        self.ref_l2 = self.ref_pyramid[2]

        self.h0, self.w0 = self.work_res_h, self.work_res_w
        self.h1, self.w1 = self.h0 // 2, self.w0 // 2
        self.h2, self.w2 = self.h0 // 4, self.w0 // 4

        # Pre-allocate persistent flow buffers to eliminate per-frame VRAM thrashing
        self.flow_l0 = self.engine.allocate((self.h0, self.w0, 2), dtype=np.float32, is_vector=False)
        self.flow_l1 = self.engine.allocate((self.h1, self.w1, 2), dtype=np.float32, is_vector=False)
        self.flow_l2 = self.engine.allocate((self.h2, self.w2, 2), dtype=np.float32, is_vector=False)

    def align_frame(
        self,
        supp_rgb_f32: Union[np.ndarray, "TaichiGPUBuffer"],
        *,
        analysis_frame_gpu: Optional[Union[np.ndarray, "TaichiGPUBuffer"]] = None,
        secondary_frame_to_warp: Optional[Union[np.ndarray, "TaichiGPUBuffer"]] = None,
        stop_event: Optional[threading.Event] = None,
        return_gpu: bool = False,
    ):
        """Aligns a single support frame to the pre-loaded reference frame using pure GPU VRAM buffers.
        
        If `analysis_frame_gpu` is provided, optical flow vectors are calculated from the high-contrast
        analysis frame, and then applied to warp `supp_rgb_f32` (RAW linear) and optionally `secondary_frame_to_warp`.
        If `secondary_frame_to_warp` is given, returns a tuple `(warped_primary, warped_secondary)`.
        """
        from taichi_vision import taichi_aot
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import (
            taichi_bridge,
        )

        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("AOT Optical Flow alignment cancelled.")
            elif callable(stop_event) and stop_event():
                raise RuntimeError("AOT Optical Flow alignment cancelled.")

        # Use analysis frame if provided, otherwise fallback to supp_rgb_f32
        src_for_pyramid = analysis_frame_gpu if analysis_frame_gpu is not None else supp_rgb_f32

        # Build comparison pyramid 100% in GPU Dedicated VRAM
        comp_pyramid = taichi_bridge.prepare_comparison_for_alignment(
            src_for_pyramid,
            ref_dtype=getattr(src_for_pyramid, "dtype", np.float32),
            is_linear_mode=False,
            proxy_scale=1.0,
            work_res_h=self.work_res_h,
            work_res_w=self.work_res_w,
            num_layers=3,
        )
        comp_l0 = comp_pyramid[0]
        comp_l1 = comp_pyramid[1]
        comp_l2 = comp_pyramid[2]

        warped_secondary = None
        try:
            args = {
                "ref_l0": self.ref_l0,
                "ref_l1": self.ref_l1,
                "ref_l2": self.ref_l2,
                "comp_l0": comp_l0,
                "comp_l1": comp_l1,
                "comp_l2": comp_l2,
                "flow_l0": self.flow_l0,
                "flow_l1": self.flow_l1,
                "flow_l2": self.flow_l2,
                "tile_h": self.tile_size,
                "tile_w": self.tile_size,
                "scale": 2.0,
                "search_dist": self.search_dist,
                "downscale": 2,
                "max_search_radius": self.max_search_radius,
            }
            self.mod.run("align_end_to_end_3layer", **args)
            self.engine.sync()

            # Smooth optical flow field once
            smooth_flow_gpu = taichi_aot.smooth_flow_gpu(
                self.flow_l0, sigma=1.0, kernel_size=5
            )

            # Pure GPU remap for primary image
            warped = taichi_aot.remap_with_flow(
                supp_rgb_f32,
                smooth_flow_gpu,
                self.full_h,
                self.full_w,
                return_gpu=return_gpu,
            )

            # Reuse exact same flow field to warp secondary frame if requested
            if secondary_frame_to_warp is not None:
                sec_shape = getattr(secondary_frame_to_warp, "shape", (self.full_h, self.full_w))
                sec_h, sec_w = int(sec_shape[0]), int(sec_shape[1])
                warped_secondary = taichi_aot.remap_with_flow(
                    secondary_frame_to_warp,
                    smooth_flow_gpu,
                    sec_h,
                    sec_w,
                    return_gpu=return_gpu,
                )

            if hasattr(smooth_flow_gpu, "destroy"):
                smooth_flow_gpu.destroy()

        finally:
            for buf in comp_pyramid:
                try:
                    if buf is not None and hasattr(buf, "destroy"):
                        buf.destroy()
                except Exception:
                    pass

        if secondary_frame_to_warp is not None:
            return warped, warped_secondary
        if return_gpu:
            return warped
        return np.ascontiguousarray(np.clip(warped, 0.0, 1.0), dtype=np.float32)

    def close(self):
        """Release all persistent reference and flow GPU buffers."""
        for buf in getattr(self, "ref_pyramid", []):
            try:
                if buf is not None and hasattr(buf, "destroy"):
                    buf.destroy()
            except Exception:
                pass
        for buf in [
            getattr(self, "flow_l0", None),
            getattr(self, "flow_l1", None),
            getattr(self, "flow_l2", None),
            getattr(self, "comp_l1_warped", None),
            getattr(self, "comp_l0_warped", None),
        ]:
            try:
                if buf is not None and hasattr(buf, "destroy"):
                    buf.destroy()
            except Exception:
                pass
        self.engine.sync()
        gc.collect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def align_support_frame(
    ref_rgb_f32: np.ndarray,
    supp_rgb_f32: np.ndarray,
    *,
    work_scale: float = 0.50,
    tile_size: int = 16,
    search_dist: int = 2,
    max_search_radius: int = 12,
    stop_event: Optional[threading.Event] = None,
    progress: Optional[Callable[[int, str], None]] = None,
) -> np.ndarray:
    """Convenience functional wrapper for single pair alignment."""
    with AOTOpticalFlowAligner(
        ref_rgb_f32,
        work_scale=work_scale,
        tile_size=tile_size,
        search_dist=search_dist,
        max_search_radius=max_search_radius,
    ) as aligner:
        return aligner.align_frame(supp_rgb_f32, stop_event=stop_event)
