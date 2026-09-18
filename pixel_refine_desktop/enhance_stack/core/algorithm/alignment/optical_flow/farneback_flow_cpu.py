"""
Farneback Optical Flow Algorithm - 100% Taichi Vision GPU-Native Optical Flow.
==============================================================================
Uses Polynomial Expansion and Cramer's Rule Flow Solver compiled with Taichi AOT
for pure GPU/native execution without OpenCV dependencies.
"""

import json
import os
import numpy as np

from config import ALGORITHM_PARAMETER_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.farneback_parameter_settings import (
    FARNEBACK_DEFAULTS,
    load_farneback_config,
)


class FarnebackFlowCPU:
    NAME = "Farneback Optical Flow"
    KIND = "alignment"
    DESCRIPTION = "100% Taichi Vision GPU-Native Farneback Optical Flow Alignment."

    PRESETS = {
        "fast": {
            "pyr_scale": 0.5,
            # Fast profile: ~32x32 window (33px) for low-latency fast search.
            "levels": 1,
            "winsize": 33,
            "iterations": 1,
            "poly_n": 5,
            "poly_sigma": 1.1,
            "grid_step": 32,
            "tile_size": 32,
        },
        "balance": {
            "pyr_scale": 0.5,
            # Balance profile: ~16x16 window (17px) for balanced trade-off.
            "levels": 3,
            "winsize": 17,
            "iterations": 3,
            "poly_n": 5,
            "poly_sigma": 1.2,
            "grid_step": 16,
            "tile_size": 16,
        },
        "high": {
            "pyr_scale": 0.5,
            # High accuracy profile: ~2x2 micro window with deep 5-level refinement for highest accuracy.
            "levels": 5,
            "winsize": 5,
            "iterations": 7,
            "poly_n": 7,
            "poly_sigma": 1.5,
            "grid_step": 2,
            "tile_size": 2,
        },
    }

    def __init__(self):
        # The reference is invariant across a burst.  Keep its native pyramid
        # resident and replace it only when the reference identity/configuration
        # changes.  This cache is optional and does not alter the public flow
        # result or its dtype.
        self._reference_cache = None

    def _release_reference_cache(self):
        cached = self._reference_cache
        self._reference_cache = None
        if not cached:
            return
        try:
            from taichi_vision.taichi_aot import get_engine

            get_engine().sync()
        except Exception:
            pass
        for buffer in cached.get("pyramid", ()):
            try:
                buffer.destroy()
            except Exception:
                try:
                    buffer.release()
                except Exception:
                    pass

    def close(self):
        """Release the optional resident reference pyramid."""
        self._release_reference_cache()

    def __del__(self):
        try:
            self._release_reference_cache()
        except Exception:
            pass

    def _get_reference_pyramid(self, ref_gray, reference_token, levels):
        try:
            from taichi_vision import taichi_algorithm

            build_pyramid = getattr(taichi_algorithm, "build_image_pyramid_gpu", None)
            if build_pyramid is None:
                return None
            key = (reference_token, tuple(ref_gray.shape), int(levels))
            cached = self._reference_cache
            if cached is not None and cached.get("key") == key:
                pyramid = cached.get("pyramid") or ()
                if pyramid and all(getattr(buf, "handle", None) is not None for buf in pyramid):
                    return pyramid

            self._release_reference_cache()
            pyramid = build_pyramid(
                np.ascontiguousarray(ref_gray, dtype=np.float32), levels=int(levels)
            )
            if not pyramid or not all(hasattr(buf, "handle") for buf in pyramid):
                return None
            self._reference_cache = {"key": key, "pyramid": tuple(pyramid)}
            return self._reference_cache["pyramid"]
        except Exception:
            # The normal full-frame call remains the same-backend recovery
            # path when an optional resident cache cannot be prepared.
            return None

    @classmethod
    def load_config(cls, batch_id=None, config_filename=None):
        config = FARNEBACK_DEFAULTS.copy()
        try:
            cfg = load_farneback_config()
            if isinstance(cfg, dict):
                config.update(cfg)
        except Exception:
            pass

        if batch_id is not None:
            try:
                from pixel_refine_desktop.enhance_stack.core.logic import (
                    batch_parameter_manager,
                )
                batch_params = batch_parameter_manager.load_json_state().get(
                    str(batch_id), {}
                )
                fb_params = batch_params.get("farneback_params", {})
                if isinstance(fb_params, dict):
                    config.update(fb_params)
            except Exception:
                pass
        return config

    @staticmethod
    def load_farneback_config(config_filename=None):
        return FarnebackFlowCPU.load_config(config_filename=config_filename)

    @staticmethod
    def load_farneback_config_for_batch(config_filename=None):
        return FarnebackFlowCPU.load_config(config_filename=config_filename)

    @staticmethod
    def _to_flow_gray(image):
        if image is None:
            return None
        img = np.ascontiguousarray(image)
        if img.ndim == 3:
            if img.shape[2] == 3:
                gray = 0.2126 * img[:, :, 0] + 0.7152 * img[:, :, 1] + 0.0722 * img[:, :, 2]
            else:
                gray = img[:, :, 0]
        else:
            gray = img
        if gray.dtype == np.uint8:
            return gray.astype(np.float32)
        if gray.dtype == np.uint16:
            return (gray >> 8).astype(np.float32)
        return (np.clip(gray, 0.0, 1.0) * 255.0).astype(np.float32)

    def calculate_flow(
        self,
        reference_gray,
        target_gray,
        config=None,
        reference_pyramid=None,
        return_gpu=False,
    ):
        """Run Taichi Vision Farneback optical flow."""
        config = config or self.load_config()
        mode = str(config.get("mode", "fast")).strip().lower()
        preset = self.PRESETS.get(mode, self.PRESETS["fast"])

        from taichi_vision.taichi_algorithm import calcOpticalFlowFarneback

        ref_f32 = np.ascontiguousarray(reference_gray, dtype=np.float32)
        tgt_f32 = np.ascontiguousarray(target_gray, dtype=np.float32)

        flow = calcOpticalFlowFarneback(
            ref_f32,
            tgt_f32,
            None,
            pyr_scale=float(preset["pyr_scale"]),
            levels=int(preset["levels"]),
            winsize=int(preset["winsize"]),
            iterations=int(preset["iterations"]),
            poly_n=int(preset["poly_n"]),
            poly_sigma=float(preset["poly_sigma"]),
            flags=0,
            reference_pyramid=reference_pyramid,
            return_gpu=bool(return_gpu),
        )
        if return_gpu:
            return flow
        if isinstance(flow, tuple):
            flow = flow[0]
        flow = np.asarray(flow, dtype=np.float32)
        expected = (*ref_f32.shape[:2], 2)
        if flow.shape != expected or not np.isfinite(flow).all():
            raise RuntimeError(f"Taichi Farneback returned invalid flow: {flow.shape}, expected {expected}")
        return np.ascontiguousarray(flow)

    def align_frame(
        self,
        reference,
        target,
        config=None,
        stop_requested=None,
        target_for_warping=None,
    ):
        if stop_requested and stop_requested():
            return None

        config = config or self.load_config()
        ref_gray = self._to_flow_gray(reference)
        tgt_gray = self._to_flow_gray(target)
        tgt_warp = target if target_for_warping is None else target_for_warping

        mode = str(config.get("mode", "fast")).strip().lower()
        preset = self.PRESETS.get(mode, self.PRESETS["fast"])
        reference_pyramid = self._get_reference_pyramid(
            ref_gray,
            id(reference),
            int(preset["levels"]),
        )
        flow_gpu = self.calculate_flow(
            ref_gray,
            tgt_gray,
            config,
            reference_pyramid=reference_pyramid,
            return_gpu=True,
        )

        from taichi_vision import taichi_aot
        try:
            return taichi_aot.remap_with_flow(
                np.ascontiguousarray(tgt_warp),
                flow_gpu,
                int(reference.shape[0]),
                int(reference.shape[1]),
                return_gpu=False,
            )
        finally:
            try:
                flow_gpu.destroy()
            except Exception:
                try:
                    flow_gpu.release()
                except Exception:
                    pass


def running_farneback_flow(*args, **kwargs):
    raise RuntimeError(
        "Farneback is now orchestrated by MFDenoiser. Use MFDenoiser with alignment='Farneback' instead."
    )
