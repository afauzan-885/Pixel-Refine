"""
OFB Alignment Algorithm - 100% Taichi Vision GPU-Native Feature Matching.
========================================================================
Uses Oriented FAST + ANMS Grid Keypoint Extraction & Oriented BRIEF (256-bit)
descriptor matching compiled with Taichi AOT for zero-copy GPU execution.
"""

from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import get_spec
import json
import os
import numpy as np

from config import ALGORITHM_PARAMETER_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.ofb_parameter_settings import (
    OFB_DEFAULTS,
    load_ofb_config,
)




class OFBAlgorithm:
    SPEC = get_spec("alignment", "ofb")
    NAME = SPEC.implementation_name
    KIND = SPEC.category
    DESCRIPTION = SPEC.description

    PRESETS = {
        "fast": {"max_kps": 600, "grid_size": 32, "threshold": 0.05, "ratio": 0.75},
        "balance": {"max_kps": 1200, "grid_size": 24, "threshold": 0.03, "ratio": 0.75},
        "high": {"max_kps": 2000, "grid_size": 16, "threshold": 0.02, "ratio": 0.80},
    }

    def __init__(self):
        self._runtime_config = None

    @classmethod
    def load_config(cls, batch_id=None, config_filename=None):
        config = OFB_DEFAULTS.copy()
        try:
            cfg = load_ofb_config()
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
                ofb_params = batch_parameter_manager.get_batch_algorithm_params(
                    batch_id, "alignment", "OFB", batch_entry=batch_params
                )
                if isinstance(ofb_params, dict):
                    config.update(ofb_params)
            except Exception:
                pass
        # Ignore legacy global and per-batch APAP selections.
        config["warp_method"] = "homography"
        return config

    def _get_config(self, batch_id=None):
        return self._runtime_config or self.load_config(batch_id=batch_id)

    @staticmethod
    def _find_homography(
        src_points, dst_points, *, threshold=5.0, hypotheses=256, refinements=2
    ):
        """Estimate support-to-reference motion through the public AOT API."""
        from taichi_vision import taichi_aot

        return taichi_aot.find_homography(
            np.ascontiguousarray(src_points, dtype=np.float32),
            np.ascontiguousarray(dst_points, dtype=np.float32),
            method="RANSAC",
            ransacReprojThreshold=float(threshold),
            n_hypotheses=max(64, int(hypotheses)),
            max_iters=max(1, int(refinements)),
            return_gpu=False,
        )

    @staticmethod
    def _warp_perspective(image, homography, dsize):
        """Warp an array through the backend-neutral AOT route used by OFB."""
        from taichi_vision import taichi_aot

        return taichi_aot.warp_perspective(
            np.ascontiguousarray(image, dtype=np.float32),
            np.ascontiguousarray(homography, dtype=np.float32),
            (int(dsize[0]), int(dsize[1])),
            return_gpu=False,
        )

    @staticmethod
    def _to_gray_f32(image):
        if image is None:
            return None
        img = np.ascontiguousarray(image)
        if img.ndim == 3:
            if img.shape[2] == 3:
                # ITU-R BT.709 Luminance
                gray = 0.2126 * img[:, :, 0] + 0.7152 * img[:, :, 1] + 0.0722 * img[:, :, 2]
            else:
                gray = img[:, :, 0]
        else:
            gray = img
        if gray.dtype == np.uint8:
            return gray.astype(np.float32) / 255.0
        if gray.dtype == np.uint16:
            return gray.astype(np.float32) / 65535.0
        return np.clip(gray, 0.0, 1.0).astype(np.float32)

    def calculate_global_motion(
        self, reference, target, config=None, stop_requested=None
    ):
        H, mask, _, _ = self._estimate_motion(
            reference, target, config=config, stop_requested=stop_requested
        )
        return H, mask

    def _estimate_motion(self, reference, target, config=None, stop_requested=None):
        if stop_requested and stop_requested():
            return None, None, None, None

        config = config or self._get_config()
        mode = str(config.get("mode", "fast")).strip().lower()
        preset = self.PRESETS.get(mode, self.PRESETS["fast"])

        ref_gray = self._to_gray_f32(reference)
        tgt_gray = self._to_gray_f32(target)
        if ref_gray is None or tgt_gray is None:
            return None, None, None, None

        try:
            from taichi_vision import taichi_aot

            matched = taichi_aot.ofb(
                ref_gray,
                tgt_gray,
                ratio_threshold=float(preset["ratio"]),
                grid_size=int(preset["grid_size"]),
                threshold=float(preset["threshold"]),
                margin=max(4, int(config.get("margin", 15))),
                max_keypoints=int(preset["max_kps"]),
            )
            if matched is None or matched[0] is None or matched[1] is None:
                return None, None, None, None
            src_pts, dst_pts = matched[0], matched[1]
            if len(src_pts) < 4 or len(dst_pts) < 4:
                return None, None, None, None

            H, mask = taichi_aot.find_homography(
                np.ascontiguousarray(dst_pts, dtype=np.float32),
                np.ascontiguousarray(src_pts, dtype=np.float32),
                method="RANSAC",
                ransacReprojThreshold=float(config.get("ransac_threshold", 5.0)),
                n_hypotheses=max(64, int(config.get("ransac_hypotheses", 1024))),
                max_iters=max(1, int(config.get("ransac_iters", 1))),
                return_gpu=False,
            )
            if H is None:
                return None, None, None, None
            keep = np.ones(len(src_pts), dtype=bool)
            if mask is not None:
                keep = np.asarray(mask).reshape(-1).astype(bool)
                if int(keep.sum()) < 4:
                    return None, mask, None, None
            return (
                np.asarray(H, dtype=np.float32),
                mask,
                np.ascontiguousarray(src_pts[keep], dtype=np.float32),
                np.ascontiguousarray(dst_pts[keep], dtype=np.float32),
            )
        except Exception as exc:
            print(f"[OFB] Motion estimation error: {exc}")
            return None, None, None, None

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

        effective_config = config or self._get_config()
        H, _, _, _ = self._estimate_motion(
            reference,
            target,
            config=effective_config,
            stop_requested=stop_requested,
        )
        img_to_warp = target if target_for_warping is None else target_for_warping
        if H is None:
            return img_to_warp

        h, w = reference.shape[:2]
        warped = self._warp_perspective(
            np.ascontiguousarray(img_to_warp), H, (w, h)
        )
        if np.issubdtype(np.asarray(img_to_warp).dtype, np.integer):
            info = np.iinfo(np.asarray(img_to_warp).dtype)
            warped = np.clip(warped + 0.5, info.min, info.max).astype(
                np.asarray(img_to_warp).dtype
            )
        else:
            warped = np.asarray(warped, dtype=np.asarray(img_to_warp).dtype)
        return warped
