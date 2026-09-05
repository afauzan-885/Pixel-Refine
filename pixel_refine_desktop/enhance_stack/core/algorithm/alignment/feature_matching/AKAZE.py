"""
AKAZE Alignment Adapter - Taichi Vision Accelerated Feature Matching.
=====================================================================
Uses Non-linear Diffusion Scale-Space & Sub-pixel Hessian ANMS from Taichi Vision
for robust and fast feature-based global motion estimation.
"""

import json
import os
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
            return gray.astype(np.float32) / 255.0
        if gray.dtype == np.uint16:
            return gray.astype(np.float32) / 65535.0
        return np.clip(gray, 0.0, 1.0).astype(np.float32, copy=False)

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
            from taichi_vision import taichi_aot

            # Taichi Vision owns feature extraction, descriptor matching, and
            # the RANSAC homography.  The point arrays are intentionally the
            # only small host readback; image data stays in the Taichi path.
            matched = taichi_aot.akaze(
                ref_gray,
                tgt_gray,
                ratio_threshold=float(preset["ratio"]),
                grid_size=max(8, int(config.get("grid_size", 32))),
                threshold=float(config.get("threshold", preset["thresh"])),
                margin=max(4, int(config.get("margin", 15))),
                max_keypoints=int(preset["max_kps"]),
                k_contrast=float(config.get("k_contrast", 0.02)),
                num_fed_steps=max(1, int(config.get("num_fed_steps", 8))),
            )
            if matched is None or matched[0] is None or matched[1] is None:
                return None, None

            src_pts, dst_pts = matched[0], matched[1]
            if len(src_pts) < 4 or len(dst_pts) < 4:
                return None, None
            # The warp consumes a support -> reference matrix.
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
                return None, None
            if mask is not None and int(np.asarray(mask).reshape(-1).sum()) < 4:
                return None, None
            return np.asarray(H, dtype=np.float32), mask
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

        from taichi_vision import taichi_aot

        h, w = reference.shape[:2]
        warped = taichi_aot.warp_perspective(
            np.ascontiguousarray(img_to_warp),
            H,
            (w, h),
            return_gpu=False,
        )
        if np.issubdtype(np.asarray(img_to_warp).dtype, np.integer):
            info = np.iinfo(np.asarray(img_to_warp).dtype)
            warped = np.clip(warped + 0.5, info.min, info.max).astype(
                np.asarray(img_to_warp).dtype
            )
        return warped


def running_akaze(*args, **kwargs):
    raise RuntimeError(
        "AKAZE is now orchestrated by MFDenoiser. Use MFDenoiser with alignment='AKAZE' instead."
    )
