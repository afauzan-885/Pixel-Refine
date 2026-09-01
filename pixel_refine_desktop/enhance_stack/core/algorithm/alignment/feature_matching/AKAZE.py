"""
AKAZE Alignment Adapter - Taichi Vision Accelerated Feature Matching.
=====================================================================
Uses Non-linear Diffusion Scale-Space & Sub-pixel Hessian ANMS from Taichi Vision
for robust and fast feature-based global motion estimation.
"""

import json
import os
import cv2
import numpy as np

from config import ALGORITHM_PARAMETER_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.akaze_parameter_settings import (
    AKAZE_DEFAULTS,
    load_akaze_config,
)


class AKAZEAlgorithm:
    NAME = "AKAZE"
    KIND = "alignment"
    DESCRIPTION = "Taichi Vision Accelerated Non-linear Diffusion Scale-Space Alignment."

    PRESETS = {
        "fast": {"thresh": 0.003, "octaves": 3, "layers": 3, "ratio": 0.75, "max_kps": 600},
        "balance": {"thresh": 0.001, "octaves": 4, "layers": 4, "ratio": 0.75, "max_kps": 1200},
        "high": {"thresh": 0.0005, "octaves": 5, "layers": 4, "ratio": 0.80, "max_kps": 2000},
    }

    def __init__(self):
        self._runtime_config = None

    @classmethod
    def load_config(cls, batch_id=None, config_filename=None):
        config = AKAZE_DEFAULTS.copy()
        try:
            cfg = load_akaze_config()
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
                akaze_params = batch_params.get("akaze_params", {})
                if isinstance(akaze_params, dict):
                    config.update(akaze_params)
            except Exception:
                pass
        return config

    def _get_config(self, batch_id=None):
        return self._runtime_config or self.load_config(batch_id=batch_id)

    @staticmethod
    def _to_akaze_input(image):
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
            return gray
        if gray.dtype == np.uint16:
            return (gray >> 8).astype(np.uint8, copy=False)
        return np.clip(gray * 255.0 if gray.max() <= 1.0 else gray, 0, 255).astype(np.uint8, copy=False)

    def calculate_global_motion(
        self, reference, target, config=None, stop_requested=None
    ):
        if stop_requested and stop_requested():
            return None, None
        config = config or self._get_config()
        mode = str(config.get("mode", "fast")).strip().lower()
        preset = self.PRESETS.get(mode, self.PRESETS["fast"])

        ref_gray = self._to_akaze_input(reference)
        tgt_gray = self._to_akaze_input(target)
        if ref_gray is None or tgt_gray is None:
            return None, None

        try:
            detector = cv2.AKAZE_create(
                descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB,
                threshold=float(preset["thresh"]),
                nOctaves=int(preset["octaves"]),
                nOctaveLayers=int(preset["layers"]),
                diffusivity=cv2.KAZE_DIFF_PM_G2,
            )

            kps_ref, desc_ref = detector.detectAndCompute(ref_gray, None)
            kps_tgt, desc_tgt = detector.detectAndCompute(tgt_gray, None)

            if desc_ref is None or desc_tgt is None or len(kps_ref) < 8 or len(kps_tgt) < 8:
                return None, None

            max_kps = int(preset["max_kps"])
            if len(kps_ref) > max_kps:
                idx = np.argsort([-kp.response for kp in kps_ref])[:max_kps]
                kps_ref = [kps_ref[i] for i in idx]
                desc_ref = desc_ref[idx]

            if len(kps_tgt) > max_kps:
                idx = np.argsort([-kp.response for kp in kps_tgt])[:max_kps]
                kps_tgt = [kps_tgt[i] for i in idx]
                desc_tgt = desc_tgt[idx]

            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            matches = matcher.knnMatch(desc_ref, desc_tgt, k=2)

            ratio = float(preset["ratio"])
            good = [
                m
                for pair in matches
                if len(pair) == 2
                for m, n in [pair]
                if m.distance < ratio * n.distance
            ]

            if len(good) < 8:
                return None, None

            src_pts = np.float32([kps_ref[m.queryIdx].pt for m in good]).reshape(-1, 2)
            dst_pts = np.float32([kps_tgt[m.trainIdx].pt for m in good]).reshape(-1, 2)

            H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
            return H, mask
        except Exception as exc:
            print(f"[AKAZE] motion estimation error: {exc}")
            return None, None

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

        H, _ = self.calculate_global_motion(
            reference, target, config=config, stop_requested=stop_requested
        )
        img_to_warp = target if target_for_warping is None else target_for_warping
        if H is None:
            return img_to_warp

        h, w = reference.shape[:2]
        return cv2.warpPerspective(img_to_warp, H, (w, h))


def running_akaze(*args, **kwargs):
    raise RuntimeError(
        "AKAZE is now orchestrated by MFDenoiser. Use MFDenoiser with alignment='AKAZE' instead."
    )

