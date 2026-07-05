"""
ORB alignment adapter.

The ORB algorithm is intentionally standalone. MFDenoiser only calls its public
adapter interface and does not depend on the internal implementation details.
"""

import json
import os

import cv2
import numpy as np

from config import ALGORITHM_PARAMETER_SETTINGS_FILE


def _frame_info(frame):
    if frame is None:
        return "None"
    return f"shape={getattr(frame, 'shape', None)}, dtype={getattr(frame, 'dtype', None)}"


class ORBAlgorithm:
    """Standalone ORB alignment adapter for MFDenoiser orchestration."""

    NAME = "ORB"
    KIND = "alignment"
    DESCRIPTION = "ORB feature alignment adapter."

    DEFAULT_CONFIG = {
        "nfeatures": 1500,
        "scaleFactor": 1.1,
        "nlevels": 5,
        "ransacThreshold": 5.0,
        "transformation": "homography",
        "keep_edges": False,
        "enable_cropping": False,
        "save_align": False,
        "command_save_to_hd5f": True,
        "align_folder": "",
        "use_multi_core": True,
        "min_matches_for_transform": 10,
        "max_keypoints_used": 500,
    }

    @staticmethod
    def load_config(batch_id=None, config_filename=None):
        config = ORBAlgorithm.load_orb_config_for_batch(config_filename)
        if batch_id is None:
            return config
        try:
            from pixel_refine_desktop.enhance_stack.core.logic import (
                batch_parameter_manager,
            )

            batch_params = batch_parameter_manager.load_json_state().get(str(batch_id), {})
            orb_params = batch_params.get("orb_params", {})
            if isinstance(orb_params, dict):
                config.update(orb_params)
        except Exception as exc:
            print(f"[ORBAlgorithm] Failed to load batch_id ORB config: {exc}")
        return config

    @staticmethod
    def load_orb_config(config_filename=None):
        """Load ORB settings for UI compatibility."""
        config_filename = config_filename or ALGORITHM_PARAMETER_SETTINGS_FILE
        config = ORBAlgorithm.DEFAULT_CONFIG.copy()
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as f:
                    all_params = json.load(f)
                config.update(all_params.get("ORB", {}))
        except Exception as exc:
            print(f"[ORBAlgorithm] Failed to load config, using defaults: {exc}")
        return config

    @staticmethod
    def load_orb_config_for_batch(config_filename=None):
        """Load ORB batch settings for legacy callers."""
        config_filename = config_filename or ALGORITHM_PARAMETER_SETTINGS_FILE
        config = ORBAlgorithm.DEFAULT_CONFIG.copy()
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as f:
                    all_params = json.load(f)
                config.update(all_params.get("ORB_BATCH", all_params.get("ORB", {})))
        except Exception as exc:
            print(f"[ORBAlgorithm] Failed to load batch config, using defaults: {exc}")
        return config

    @staticmethod
    def load_orb_config_for_batch_id(batch_id, config_filename=None):
        config = ORBAlgorithm.load_orb_config_for_batch(config_filename)
        if batch_id is None:
            return config
        try:
            from pixel_refine_desktop.enhance_stack.core.logic import (
                batch_parameter_manager,
            )

            batch_params = batch_parameter_manager.load_json_state().get(str(batch_id), {})
            orb_params = batch_params.get("orb_params", {})
            if isinstance(orb_params, dict):
                config.update(orb_params)
        except Exception as exc:
            print(f"[ORBAlgorithm] Failed to load batch_id ORB config: {exc}")
        return config

    def run(self, ctx, frames, batch_plan=None):
        """Align frames to the first frame using ORB feature matching."""
        print(
            f"[ORBAlgorithm] ORB alignment called. "
            f"frames={len(frames)} batch_plan={batch_plan}"
        )
        if not frames:
            return []

        reference = frames[0]
        aligned = [np.array(reference, copy=True)]
        for idx, frame in enumerate(frames[1:], start=1):
            aligned_frame = self.align_frame(reference, frame, batch_id=getattr(ctx, "batch_id", None))
            aligned.append(aligned_frame)
            print(f"[ORBAlgorithm] aligned_frame_{idx}: {_frame_info(aligned_frame)}")
        return aligned

    def align_frame(self, reference, target, batch_id=None):
        """Align one target frame to reference; return target unchanged on failure."""
        if reference is None or target is None:
            return target

        config = self.load_config(batch_id=batch_id)
        base_points, target_points = self.calculate_global_motion(reference, target, config=config)
        if base_points is None or target_points is None:
            return np.array(target, copy=True)

        transformation = str(config.get("transformation", "homography")).lower()
        ransac_threshold = float(config.get("ransacThreshold", 5.0))
        h, w = reference.shape[:2]

        try:
            if transformation == "affine":
                matrix, _ = cv2.estimateAffinePartial2D(
                    target_points.reshape(-1, 2),
                    base_points.reshape(-1, 2),
                    method=cv2.RANSAC,
                    ransacReprojThreshold=ransac_threshold,
                )
                if matrix is None:
                    print("[ORBAlgorithm] affine matrix failed, using original frame.")
                    return np.array(target, copy=True)
                return cv2.warpAffine(
                    target,
                    matrix,
                    (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_CONSTANT,
                )

            matrix, _ = cv2.findHomography(
                target_points,
                base_points,
                cv2.RANSAC,
                ransac_threshold,
            )
            if matrix is None:
                print("[ORBAlgorithm] homography matrix failed, using original frame.")
                return np.array(target, copy=True)
            return cv2.warpPerspective(
                target,
                matrix,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_CONSTANT,
            )
        except cv2.error as exc:
            print(f"[ORBAlgorithm] OpenCV alignment failed: {exc}")
            return np.array(target, copy=True)

    def calculate_global_motion(self, reference, target, config=None, stop_requested=None):
        if stop_requested and stop_requested():
            return None, None
        if reference is None or target is None:
            return None, None

        config = config or self.load_config()
        ref_gray = self._to_u8_gray(reference)
        target_gray = self._to_u8_gray(target)
        if ref_gray is None or target_gray is None:
            print("[ORBAlgorithm] grayscale conversion failed.")
            return None, None

        nfeatures = int(config.get("nfeatures", 1500))
        scale_factor = float(config.get("scaleFactor", 1.1))
        nlevels = int(config.get("nlevels", 5))
        min_matches = int(config.get("min_matches_for_transform", 10))
        max_keypoints = int(config.get("max_keypoints_used", 500))

        try:
            detector = cv2.ORB_create(
                nfeatures=max(100, nfeatures),
                scaleFactor=max(1.01, scale_factor),
                nlevels=max(1, nlevels),
            )
            kp_ref, des_ref = detector.detectAndCompute(ref_gray, None)
            kp_target, des_target = detector.detectAndCompute(target_gray, None)
            print(
                f"[ORBAlgorithm] keypoints ref={len(kp_ref)} target={len(kp_target)} "
                f"config={config}"
            )
            if des_ref is None or des_target is None or len(kp_ref) < 4 or len(kp_target) < 4:
                print("[ORBAlgorithm] not enough descriptors/keypoints.")
                return None, None

            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = matcher.match(des_ref, des_target)
            matches = sorted(matches, key=lambda m: m.distance)
            keep = max(4, int(len(matches) * 0.65))
            matches = matches[: min(keep, max_keypoints)]
            print(f"[ORBAlgorithm] matches kept={len(matches)}")
            if len(matches) < min_matches:
                print(f"[ORBAlgorithm] insufficient matches: {len(matches)}")
                return None, None

            base_points = np.float32([kp_ref[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            target_points = np.float32([kp_target[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
            return base_points, target_points
        except cv2.error as exc:
            print(f"[ORBAlgorithm] motion calculation failed: {exc}")
            return None, None

    def build_motion_plan(self, ctx, reference, target_dims, orchestrator, config):
        plan = [{"index": 0, "path": ctx.image_paths[0], "success": True, "base_points": None, "target_points": None}]
        total_targets = max(1, ctx.total_images - 1)
        for offset, path in enumerate(ctx.image_paths[1:], start=1):
            if ctx.stop_requested and ctx.stop_requested():
                break
            frame = orchestrator._load_single_frame(ctx, path, target_dims=target_dims)
            base_points, target_points = (None, None)
            if frame is not None:
                base_points, target_points = self.calculate_global_motion(
                    reference,
                    frame,
                    config=config,
                    stop_requested=ctx.stop_requested,
                )
            success = base_points is not None and target_points is not None
            plan.append({"index": offset, "path": path, "success": success, "base_points": base_points, "target_points": target_points})
            print(f"[ORBAlgorithm] stage1 motion index={offset} success={success}")
            if ctx.update_progress:
                ctx.update_progress(20 + int((offset / total_targets) * 35), f"ORB motion {offset}/{total_targets}")
            del frame
        return plan

    @staticmethod
    def _to_u8_gray(image):
        if image is None:
            return None
        arr = image
        if arr.ndim == 3:
            arr = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
        if arr.dtype == np.uint8:
            return arr
        if arr.dtype == np.uint16:
            return (arr >> 8).astype(np.uint8, copy=False)
        return np.clip(arr, 0, 255).astype(np.uint8, copy=False)


def running_orb(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
):
    """Legacy entrypoint routed through MFDenoiser orchestration."""
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
        running_mf_denoiser,
    )

    return running_mf_denoiser(
        parent=parent,
        single_process=single_process,
        batch_id=batch_id,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        alignment_backend=ORBAlgorithm.NAME,
        merging_mode="No Denoising",
        output_suffix="orb_alignment",
    )
