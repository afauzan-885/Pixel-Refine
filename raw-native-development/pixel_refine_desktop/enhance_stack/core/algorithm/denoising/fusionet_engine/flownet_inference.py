"""
Taichi AOT Native Optical Flow Alignment Engine (compute_flow.tcm).
Computes dense hierarchical optical flow (dx, dy) between reference and support frames
using Taichi AOT 3-layer coarse-to-fine pyramid alignment (compute_flow.tcm)
and warps support frames with Taichi AOT native remap_with_flow.
"""

import gc
import os
import threading
from typing import Callable, Optional, Tuple, Union

import numpy as np

_MODULE_CACHE = {}


def load_compute_flow_module(engine=None):
    """Loads and caches the compute_flow AOT module on the active Taichi engine."""
    from taichi_vision import taichi_aot

    return taichi_aot.load_tcm("compute_flow")


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
        full_shape: Optional[Tuple[int, int]] = None,
        tile_size: int = 16,
        search_dist: int = 2,
        max_search_radius: int = 12,
        noise_score: Optional[float] = None,
    ):
        from taichi_vision.taichi_aot import get_engine
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import (
            taichi_bridge,
        )

        self.engine = get_engine()
        self.mod = load_compute_flow_module(self.engine)

        if full_shape is not None:
            self.full_h, self.full_w = int(full_shape[0]), int(full_shape[1])
            if ref_rgb_f32.shape[:2] != (self.full_h, self.full_w):
                self.work_res_h, self.work_res_w = ref_rgb_f32.shape[:2]
            else:
                self.work_res_h = max(32, int(self.full_h * float(work_scale)))
                self.work_res_w = max(32, int(self.full_w * float(work_scale)))
        else:
            self.full_h, self.full_w = ref_rgb_f32.shape[:2]
            self.work_res_h = max(32, int(self.full_h * float(work_scale)))
            self.work_res_w = max(32, int(self.full_w * float(work_scale)))

        self.tile_size = int(tile_size)
        self.search_dist = int(search_dist)
        self.max_search_radius = int(max_search_radius)

        # Noise-Aware Analysis Pre-Filter on Reference Frame.  The resident
        # pipeline can provide the score computed from the linear reference;
        # reuse it so FlowNet does not re-estimate noise on AutoEnhance output.
        ref_denoised = None
        ref_for_pyramid = ref_rgb_f32
        self.prefilter_kernel_size = 0
        try:
            if noise_score is None:
                from taichi_vision.taichi_algorithm.enhancement.estimate_noise import (
                    estimate_noise,
                )

                ref_noise_score, _ = estimate_noise(ref_rgb_f32)
                ref_noise_score = float(ref_noise_score)
                score_source = "aligner-local"
            else:
                ref_noise_score = float(noise_score)
                score_source = "shared-linear-reference"
            print(
                f"[FlowNet] Reference noise score={ref_noise_score:.6f} "
                f"source={score_source}"
            )
            if ref_noise_score >= 0.60:
                self.prefilter_kernel_size = 5
                ref_denoised = taichi_aot.box_filter(
                    ref_rgb_f32, kernel_size=5, return_gpu=True
                )
                ref_for_pyramid = ref_denoised
            elif ref_noise_score >= 0.30:
                self.prefilter_kernel_size = 3
                ref_denoised = taichi_aot.box_filter(
                    ref_rgb_f32, kernel_size=3, return_gpu=True
                )
                ref_for_pyramid = ref_denoised
        except Exception:
            pass

        # Pre-compute Reference Pyramid 100% in GPU Dedicated VRAM
        try:
            self.ref_pyramid = taichi_bridge.prepare_reference_for_alignment(
                ref_for_pyramid,
                is_linear_mode=False,
                proxy_scale=1.0,
                work_res_h=self.work_res_h,
                work_res_w=self.work_res_w,
                num_layers=3,
            )
        finally:
            if ref_denoised is not None and hasattr(ref_denoised, "destroy"):
                ref_denoised.destroy()

        self.ref_l0 = self.ref_pyramid[0]
        self.ref_l1 = self.ref_pyramid[1]
        self.ref_l2 = self.ref_pyramid[2]

        self.h0, self.w0 = self.work_res_h, self.work_res_w
        self.h1, self.w1 = self.h0 // 2, self.w0 // 2
        self.h2, self.w2 = self.h0 // 4, self.w0 // 4

        # Pre-allocate persistent flow buffers to eliminate per-frame memory allocation overhead across all backends
        self.flow_l0 = self.engine.allocate(
            (self.h0, self.w0, 2), dtype=np.float32, is_vector=False
        )
        self.flow_l1 = self.engine.allocate(
            (self.h1, self.w1, 2), dtype=np.float32, is_vector=False
        )
        self.flow_l2 = self.engine.allocate(
            (self.h2, self.w2, 2), dtype=np.float32, is_vector=False
        )

        # V2 uses ping-pong flow storage so the tile-parallel refinement
        # kernels never read and write a level through the same allocation.
        # It is opt-in at the artifact level: a stale deployment keeps the
        # historical graph and public behavior without an API change.
        self._fast_graph_enabled = False
        self.flow_l1_seed = None
        self.flow_l0_seed = None
        self.flow_l0_raw = None
        self._smooth_weights = None
        self._remap_mod = None
        self.last_flow_gpu = None
        try:
            from taichi_vision import taichi_aot
            from taichi_vision.taichi_algorithm.aot_api import (
                InputArray,
                aot_graph_available,
            )
            from taichi_vision.taichi_algorithm.smoothing.gaussian import (
                compute_gaussian_weights,
            )

            enabled_by_env = os.environ.get(
                "PIXEL_REFINE_COMPUTE_FLOW_FAST_PATH", "1"
            ).strip().lower() not in {"0", "false", "off", "no"}
            if enabled_by_env and aot_graph_available(
                "compute_flow", "align_end_to_end_3layer_v2"
            ):
                self.flow_l1_seed = self.engine.allocate(
                    (self.h1, self.w1, 2), dtype=np.float32, is_vector=False
                )
                self.flow_l0_seed = self.engine.allocate(
                    (self.h0, self.w0, 2), dtype=np.float32, is_vector=False
                )
                self.flow_l0_raw = self.engine.allocate(
                    (self.h0, self.w0, 2), dtype=np.float32, is_vector=False
                )
                self._smooth_weights = InputArray(
                    np.ascontiguousarray(
                        compute_gaussian_weights(1.0, 2), dtype=np.float32
                    )
                )
                self._remap_mod = taichi_aot.load_tcm("remap")
                self._fast_graph_enabled = True
        except Exception:
            # The established graph remains the same-backend recovery route
            # when a target archive has not yet been rebuilt.
            self._fast_graph_enabled = False
            for attr in (
                "flow_l1_seed",
                "flow_l0_seed",
                "flow_l0_raw",
                "_smooth_weights",
            ):
                buf = getattr(self, attr, None)
                try:
                    if buf is not None and hasattr(buf, "destroy"):
                        buf.destroy()
                except Exception:
                    pass
                setattr(self, attr, None)

    def _run_flow_graph(self, args):
        """Run the non-aliasing graph when its target artifact is available."""
        if self._fast_graph_enabled:
            try:
                v2_args = dict(args)
                # V2 produces its unsmoothed final level in ``flow_l0_raw``.
                # Do not marshal the legacy-only output into this graph.
                v2_args.pop("flow_l0", None)
                self.mod.run(
                    "align_end_to_end_3layer_v2",
                    **v2_args,
                    flow_l1_seed=self.flow_l1_seed,
                    flow_l0_seed=self.flow_l0_seed,
                    flow_l0_raw=self.flow_l0_raw,
                )
                return True
            except Exception as exc:
                # Do not fall back to CPU or retain a failed graph state for
                # the rest of a burst.  The legacy graph is the established
                # same-backend compatibility path.
                self._fast_graph_enabled = False
                for attr in (
                    "flow_l1_seed",
                    "flow_l0_seed",
                    "flow_l0_raw",
                    "_smooth_weights",
                ):
                    buf = getattr(self, attr, None)
                    try:
                        if buf is not None and hasattr(buf, "destroy"):
                            buf.destroy()
                    except Exception:
                        pass
                    setattr(self, attr, None)
                self._remap_mod = None
                print(
                    "[FlowNet] compute_flow v2 unavailable at runtime; "
                    f"using legacy graph: {type(exc).__name__}: {exc}"
                )
        self.mod.run("align_end_to_end_3layer", **args)
        return False

    def _smooth_flow_resident(self):
        """Run the existing two-pass Gaussian graph without per-frame pool work."""
        self._remap_mod.run(
            "smooth_flow_x",
            src=self.flow_l0_raw,
            dst=self.flow_l0_seed,
            h=self.h0,
            w=self.w0,
            weights=self._smooth_weights,
            radius=2,
        )
        self._remap_mod.run(
            "smooth_flow_y",
            src=self.flow_l0_seed,
            dst=self.flow_l0,
            h=self.h0,
            w=self.w0,
            weights=self._smooth_weights,
            radius=2,
        )
        return self.flow_l0

    def _retain_flow(self, flow):
        """Copy a transient or reusable flow into caller-owned GPU storage."""
        from taichi_vision.taichi_aot.engine import _LIB

        previous = getattr(self, "last_flow_gpu", None)
        if previous is not None and hasattr(previous, "destroy"):
            previous.destroy()
        retained = self.engine.allocate(
            (self.h0, self.w0, 2), dtype=np.float32, is_vector=False
        )
        try:
            with self.engine._lock:
                _LIB.copy_gpu_buffer(
                    self.engine.runtime,
                    flow.handle,
                    retained.handle,
                    retained.nbytes,
                )
        except Exception:
            retained.destroy()
            raise
        self.last_flow_gpu = retained

    def _remap_resident(self, src, flow, full_h, full_w):
        """Submit an f32 resident remap without the public host-sync boundary."""
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer

        if (
            not isinstance(src, TaichiGPUBuffer)
            or np.dtype(src.dtype) != np.dtype(np.float32)
            or np.dtype(flow.dtype) != np.dtype(np.float32)
            or len(src.shape) not in (2, 3)
        ):
            return None

        is_3d = len(src.shape) == 3
        channels = int(src.shape[2]) if is_3d else 1
        if is_3d and channels != 3:
            return None

        dst_shape = (int(full_h), int(full_w), channels) if is_3d else (
            int(full_h),
            int(full_w),
        )
        dst = self.engine.allocate(
            dst_shape,
            dtype=np.float32,
            is_vector=is_3d,
            vector_dim=channels,
        )
        try:
            src_view = (
                src
                if not is_3d or getattr(src, "is_vector", False)
                else src.view_as_vector(True, channels)
            )
            dst_view = (
                dst
                if not is_3d or getattr(dst, "is_vector", False)
                else dst.view_as_vector(True, channels)
            )
            flow_view = (
                flow.view_as_vector(False)
                if getattr(flow, "is_vector", False)
                else flow
            )
            self._remap_mod.run(
                "remap_with_flow_f32_3d" if is_3d else "remap_with_flow_f32_2d",
                src=src_view,
                flow=flow_view,
                dst=dst_view,
                h_src=int(src.shape[0]),
                w_src=int(src.shape[1]),
                h_dst=int(full_h),
                w_dst=int(full_w),
                h_flow=int(flow.shape[0]),
                w_flow=int(flow.shape[1]),
                scale_x=float(full_w) / float(flow.shape[1]),
                scale_y=float(full_h) / float(flow.shape[0]),
            )
            return dst
        except Exception:
            dst.destroy()
            return None

    def align_frame(
        self,
        supp_rgb_f32: Union[np.ndarray, "TaichiGPUBuffer"],
        *,
        analysis_frame_gpu: Optional[Union[np.ndarray, "TaichiGPUBuffer"]] = None,
        secondary_frame_to_warp: Optional[Union[np.ndarray, "TaichiGPUBuffer"]] = None,
        stop_event: Optional[threading.Event] = None,
        return_gpu: bool = False,
        stream_primary: bool = False,
        keep_flow: bool = False,
    ):
        """Aligns a single support frame to the pre-loaded reference frame using pure GPU VRAM buffers.

        If `analysis_frame_gpu` is provided, optical flow vectors are calculated from the high-contrast
        analysis frame, and then applied to warp `supp_rgb_f32` (RAW linea r) and optionally `secondary_frame_to_warp`.
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
        src_for_pyramid = (
            analysis_frame_gpu if analysis_frame_gpu is not None else supp_rgb_f32
        )

        # Noise-Aware Analysis Pre-Filter for Optical Flow Computation (Reuses burst-wide analysis without per-frame CPU stall)
        src_denoised = None
        if self.prefilter_kernel_size > 0:
            try:
                src_denoised = taichi_aot.box_filter(
                    src_for_pyramid,
                    kernel_size=self.prefilter_kernel_size,
                    return_gpu=True,
                )
                src_for_pyramid = src_denoised
            except Exception:
                pass

        # Build comparison pyramid 100% in GPU Dedicated VRAM
        try:
            comp_pyramid = taichi_bridge.prepare_comparison_for_alignment(
                src_for_pyramid,
                ref_dtype=getattr(src_for_pyramid, "dtype", np.float32),
                is_linear_mode=False,
                proxy_scale=1.0,
                work_res_h=self.work_res_h,
                work_res_w=self.work_res_w,
                num_layers=3,
            )
        finally:
            if src_denoised is not None and hasattr(src_denoised, "destroy"):
                src_denoised.destroy()
        comp_l0 = comp_pyramid[0]
        comp_l1 = comp_pyramid[1]
        comp_l2 = comp_pyramid[2]

        warped_secondary = None
        transient_flow_gpu = None
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
            used_fast_graph = self._run_flow_graph(args)

            # The comparison pyramid is only an input to flow estimation.  Do
            # not keep all three levels alive while remap allocates its full
            # resolution output; on small VRAM devices that temporary overlap
            # is a significant peak.  The outer finally remains as a safety
            # net for exceptions during graph execution.
            for buf in comp_pyramid:
                try:
                    if buf is not None and hasattr(buf, "destroy"):
                        buf.destroy()
                except Exception:
                    pass
            comp_pyramid = ()

            # The resident v2 route keeps the exact same two-pass Gaussian
            # kernels but reuses their temporary/weight buffers and does not
            # impose the public API's host synchronization between stages.
            # Host-return callers retain the established compatibility route.
            if used_fast_graph and return_gpu:
                active_flow_gpu = self._smooth_flow_resident()
                if supp_rgb_f32 is not None:
                    warped = self._remap_resident(
                        supp_rgb_f32,
                        active_flow_gpu,
                        self.full_h,
                        self.full_w,
                    )
                    if warped is None:
                        warped = taichi_aot.remap_with_flow(
                            supp_rgb_f32,
                            active_flow_gpu,
                            self.full_h,
                            self.full_w,
                            return_gpu=True,
                        )
                else:
                    warped = None

                if secondary_frame_to_warp is not None:
                    sec_shape = getattr(
                        secondary_frame_to_warp,
                        "shape",
                        (self.full_h, self.full_w),
                    )
                    sec_h, sec_w = int(sec_shape[0]), int(sec_shape[1])
                    warped_secondary = self._remap_resident(
                        secondary_frame_to_warp,
                        active_flow_gpu,
                        sec_h,
                        sec_w,
                    )
                    if warped_secondary is None:
                        warped_secondary = taichi_aot.remap_with_flow(
                            secondary_frame_to_warp,
                            active_flow_gpu,
                            sec_h,
                            sec_w,
                            return_gpu=True,
                        )
            else:
                flow_source = (
                    self.flow_l0_raw if used_fast_graph else self.flow_l0
                )
                smooth_flow_gpu = taichi_aot.smooth_flow_gpu(
                    flow_source, sigma=1.0, kernel_size=5
                )
                active_flow_gpu = smooth_flow_gpu
                transient_flow_gpu = smooth_flow_gpu
                if supp_rgb_f32 is not None:
                    warped = taichi_aot.remap_with_flow(
                        supp_rgb_f32,
                        active_flow_gpu,
                        self.full_h,
                        self.full_w,
                        return_gpu=return_gpu,
                    )
                else:
                    warped = None

                if secondary_frame_to_warp is not None:
                    sec_shape = getattr(
                        secondary_frame_to_warp,
                        "shape",
                        (self.full_h, self.full_w),
                    )
                    sec_h, sec_w = int(sec_shape[0]), int(sec_shape[1])
                    warped_secondary = taichi_aot.remap_with_flow(
                        secondary_frame_to_warp,
                        active_flow_gpu,
                        sec_h,
                        sec_w,
                        return_gpu=return_gpu,
                    )

            # ``stream_primary`` was historically accepted but did not alter
            # graph submission.  Keep it for API compatibility while the
            # caller-selected GPU return mode remains the streaming contract.
            _ = stream_primary
            if keep_flow:
                self._retain_flow(active_flow_gpu)
            if transient_flow_gpu is not None and hasattr(
                transient_flow_gpu, "destroy"
            ):
                transient_flow_gpu.destroy()

        finally:
            for buf in comp_pyramid:
                try:
                    if buf is not None and hasattr(buf, "destroy"):
                        buf.destroy()
                except Exception:
                    pass

        if secondary_frame_to_warp is not None:
            return warped, warped_secondary
        if return_gpu or warped is None:
            return warped
        return np.ascontiguousarray(np.clip(warped, 0.0, 1.0), dtype=np.float32)

    def take_last_flow(self):
        """Transfer the retained filtered flow to the caller."""
        flow = getattr(self, "last_flow_gpu", None)
        self.last_flow_gpu = None
        if flow is None:
            raise RuntimeError("No retained compute_flow result is available.")
        return flow

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
            getattr(self, "flow_l1_seed", None),
            getattr(self, "flow_l0_seed", None),
            getattr(self, "flow_l0_raw", None),
            getattr(self, "_smooth_weights", None),
            getattr(self, "last_flow_gpu", None),
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
