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
from typing import Callable, Optional, Tuple

import numpy as np

_MODULE_CACHE = {}


def _resolve_compute_flow_tcm(engine=None) -> str:
    """Locate the backend-specific compute_flow_<arch>.tcm or fallback."""
    from taichi_vision.taichi_aot import get_engine

    engine = engine or get_engine()
    arch = str(getattr(engine, "arch", "cpu")).strip().lower()

    candidates = [
        Path(__file__).parents[5] / f"ui/data/aot_assets/compute_flow_{arch}.tcm",
        Path(__file__).parents[5] / "ui/data/aot_assets/compute_flow.tcm",
        Path(__file__).parents[5] / f"taichi_vision/taichi_algorithm/aot_tcm/compute_flow_{arch}.tcm",
        Path(__file__).parents[5] / "taichi_vision/taichi_algorithm/aot_tcm/compute_flow.tcm",
    ]

    for p in candidates:
        if p.is_file():
            return str(p.resolve())

    raise FileNotFoundError(
        f"compute_flow.tcm not found for backend '{arch}'. Checked paths: {[str(p) for p in candidates]}"
    )


def load_compute_flow_module(engine=None):
    """Loads and caches the compute_flow AOT module on the active Taichi engine."""
    from taichi_vision.taichi_aot import get_engine

    engine = engine or get_engine()
    arch = str(getattr(engine, "arch", "cpu")).strip().lower()

    if arch in _MODULE_CACHE:
        return _MODULE_CACHE[arch]

    tcm_path = _resolve_compute_flow_tcm(engine)
    mod = engine.load(tcm_path)
    _MODULE_CACHE[arch] = mod
    print(f"[AOT Optical Flow] Loaded '{os.path.basename(tcm_path)}' on backend '{arch}'")
    return mod


def _build_gray_pyramid_np(
    image_rgb_f32: np.ndarray,
    work_res_h: int,
    work_res_w: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Builds a 3-layer grayscale float32 pyramid (L0, L1, L2) in NumPy host memory using fast CPU OpenCV.
    Zero GPU context switching, 100% memory isolation.
    """
    import cv2

    # 1. RGB to Grayscale Luma (0.299 R + 0.587 G + 0.114 B)
    if image_rgb_f32.ndim == 3 and image_rgb_f32.shape[2] == 3:
        gray = cv2.cvtColor(image_rgb_f32, cv2.COLOR_RGB2GRAY)
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

    # 3. L0: work resolution
    if gray.shape[:2] != (work_res_h, work_res_w):
        l0 = cv2.resize(gray, (work_res_w, work_res_h), interpolation=cv2.INTER_AREA)
    else:
        l0 = gray
    l0 = np.ascontiguousarray(l0, dtype=np.float32)

    # 4. L1: 1/2 scale
    h1, w1 = max(16, work_res_h // 2), max(16, work_res_w // 2)
    l1 = np.ascontiguousarray(
        cv2.resize(l0, (w1, h1), interpolation=cv2.INTER_AREA),
        dtype=np.float32,
    )

    # 5. L2: 1/4 scale
    h2, w2 = max(8, work_res_h // 4), max(8, work_res_w // 4)
    l2 = np.ascontiguousarray(
        cv2.resize(l1, (w2, h2), interpolation=cv2.INTER_AREA),
        dtype=np.float32,
    )

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

        self.engine = get_engine()
        self.mod = load_compute_flow_module(self.engine)

        self.full_h, self.full_w = ref_rgb_f32.shape[:2]
        work_res_h = max(32, int(self.full_h * float(work_scale)))
        work_res_w = max(32, int(self.full_w * float(work_scale)))

        # Force even dimensions for clean 3-level pyramid division
        self.work_res_h = (work_res_h // 4) * 4
        self.work_res_w = (work_res_w // 4) * 4

        self.h0, self.w0 = self.work_res_h, self.work_res_w
        self.h1, self.w1 = self.h0 // 2, self.w0 // 2
        self.h2, self.w2 = self.h0 // 4, self.w0 // 4

        self.tile_size = int(tile_size)
        self.search_dist = int(search_dist)
        self.max_search_radius = int(max_search_radius)

        # Pre-compute reference pyramid in host memory and upload to GPU
        ref_l0_np, ref_l1_np, ref_l2_np = _build_gray_pyramid_np(
            ref_rgb_f32, self.work_res_h, self.work_res_w
        )
        self.ref_l0 = self.engine.upload(ref_l0_np)
        self.ref_l1 = self.engine.upload(ref_l1_np)
        self.ref_l2 = self.engine.upload(ref_l2_np)
        del ref_l0_np, ref_l1_np, ref_l2_np

    def align_frame(
        self,
        supp_rgb_f32: np.ndarray,
        *,
        stop_event: Optional[threading.Event] = None,
    ) -> np.ndarray:
        """Aligns a single support frame to the pre-loaded reference frame."""
        from taichi_vision import taichi_aot

        if stop_event is not None and stop_event.is_set():
            raise RuntimeError("AOT Optical Flow alignment cancelled.")

        # Build support comparison pyramid in host CPU (instant)
        comp_l0_np, comp_l1_np, comp_l2_np = _build_gray_pyramid_np(
            supp_rgb_f32, self.work_res_h, self.work_res_w
        )

        comp_l0 = self.engine.upload(comp_l0_np)
        comp_l1 = self.engine.upload(comp_l1_np)
        comp_l2 = self.engine.upload(comp_l2_np)
        del comp_l0_np, comp_l1_np, comp_l2_np

        flow_l0 = self.engine.allocate((self.h0, self.w0, 2), dtype=np.float32, is_vector=False)
        flow_l1 = self.engine.allocate((self.h1, self.w1, 2), dtype=np.float32, is_vector=False)
        flow_l2 = self.engine.allocate((self.h2, self.w2, 2), dtype=np.float32, is_vector=False)

        comp_l1_warped = self.engine.allocate((self.h1, self.w1), dtype=np.float32, is_vector=False)
        comp_l0_warped = self.engine.allocate((self.h0, self.w0), dtype=np.float32, is_vector=False)

        try:
            args = {
                "ref_l0": self.ref_l0,
                "ref_l1": self.ref_l1,
                "ref_l2": self.ref_l2,
                "comp_l0": comp_l0,
                "comp_l1": comp_l1,
                "comp_l2": comp_l2,
                "flow_l0": flow_l0,
                "flow_l1": flow_l1,
                "flow_l2": flow_l2,
                "comp_l1_warped": comp_l1_warped,
                "comp_l0_warped": comp_l0_warped,
                "tile_h": self.tile_size,
                "tile_w": self.tile_size,
                "scale": 2.0,
                "search_dist": self.search_dist,
                "downscale": 2,
                "max_search_radius": self.max_search_radius,
            }
            self.mod.run("align_end_to_end_3layer", **args)
            self.engine.sync()

            # Smooth optical flow field
            smooth_flow_gpu = taichi_aot.smooth_flow_gpu(
                flow_l0, sigma=1.0, kernel_size=5
            )

            # Pure GPU remap
            warped = taichi_aot.remap_with_flow(
                supp_rgb_f32,
                smooth_flow_gpu,
                self.full_h,
                self.full_w,
                return_gpu=False,
            )

        finally:
            for buf in [comp_l0, comp_l1, comp_l2, comp_l1_warped, comp_l0_warped, flow_l1, flow_l2]:
                try:
                    if buf is not None and hasattr(buf, "destroy"):
                        buf.destroy()
                except Exception:
                    pass
            self.engine.sync()

        return np.ascontiguousarray(np.clip(warped, 0.0, 1.0), dtype=np.float32)

    def close(self):
        """Release all reference GPU pyramid buffers."""
        for buf in [self.ref_l0, self.ref_l1, self.ref_l2]:
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
