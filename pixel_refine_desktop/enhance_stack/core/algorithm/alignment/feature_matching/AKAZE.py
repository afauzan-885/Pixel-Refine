import concurrent.futures
import json
import os

import cv2
import numpy as np

from config import ALGORITHM_PARAMETER_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.feature_matching_utils.feature_block_compute import (
    compute_features_block,
    select_top_keypoints,
)


DEFAULT_AKAZE_CONFIG = {
    "akaze_threshold": 0.001,
    "akaze_nOctaves": 4,
    "akaze_nOctaveLayers": 4,
    "ratio_threshold": 0.75,
    "ransacThreshold": 5.0,
    "transformation": "homography",
    "keep_edges": False,
    "enable_cropping": False,
    "save_align": False,
    "command_save_to_hd5f": True,
    "use_multi_core": True,
    "align_folder": os.path.join(
        os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image"
    ),
    "min_matches_for_transform": 10,
    "max_keypoints_used": 500,
}


class AKAZEAlgorithm:
    NAME = "AKAZE"
    KIND = "alignment"
    DESCRIPTION = "Block-based AKAZE alignment adapter."

    def __init__(self):
        self._runtime_config = None

    @staticmethod
    def load_config(batch_id=None, config_filename=None):
        config = DEFAULT_AKAZE_CONFIG.copy()
        config_filename = config_filename or ALGORITHM_PARAMETER_SETTINGS_FILE
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                config.update(params.get("AKAZE", {}))
                config.update(params.get("AKAZE_BATCH", {}))
        except Exception as exc:
            print(f"[AKAZE] Failed to load global config: {exc}")

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
            except Exception as exc:
                print(f"[AKAZE] Failed to load batch config: {exc}")
        return config

    def _get_config(self, batch_id=None):
        return self._runtime_config or self.load_config(batch_id=batch_id)

    @staticmethod
    def _as_bool(value, default=False):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        if value is None:
            return default
        return bool(value)

    @staticmethod
    def _to_akaze_input(image):
        if image is None:
            return None
        if image.ndim == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if image.dtype == np.uint8:
            return image
        if image.dtype == np.uint16:
            return (image >> 8).astype(np.uint8, copy=False)
        return np.clip(image, 0, 255).astype(np.uint8, copy=False)

    def calculate_global_motion(
        self, reference, target, config=None, stop_requested=None
    ):
        if stop_requested and stop_requested():
            return None, None
        config = config or self._get_config()
        reference_gray = self._to_akaze_input(reference)
        target_gray = self._to_akaze_input(target)
        if reference_gray is None or target_gray is None:
            return None, None

        height, width = reference_gray.shape
        blocks_x, blocks_y = (1, 2)
        block_w = max(1, width // blocks_x)
        block_h = max(1, height // blocks_y)

        def create_detector():
            return cv2.AKAZE_create(
                descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB,
                threshold=float(config.get("akaze_threshold", 0.001)),
                nOctaves=int(config.get("akaze_nOctaves", 4)),
                nOctaveLayers=int(config.get("akaze_nOctaveLayers", 4)),
                diffusivity=cv2.KAZE_DIFF_PM_G2,
            )

        try:
            create_detector()
        except cv2.error:
            return None, None

        ref_kps, ref_descs, target_kps, target_descs = [], [], [], []

        def block_task(i, j):
            x = i * block_w
            y = j * block_h
            bw = width - x if i == blocks_x - 1 else block_w
            bh = height - y if j == blocks_y - 1 else block_h
            detector = create_detector()
            return compute_features_block(
                detector, reference_gray, target_gray, x, y, bw, bh, 0
            )

        jobs = [(i, j) for i in range(blocks_x) for j in range(blocks_y)]
        use_multi_core = self._as_bool(config.get("use_multi_core"), default=True)
        worker_count = max(1, min(len(jobs), os.cpu_count() or 4))
        print(
            f"[AKAZE] block feature extraction blocks={blocks_x}x{blocks_y} "
            f"use_multi_core={use_multi_core} workers={worker_count if use_multi_core else 1}"
        )
        if use_multi_core and len(jobs) > 1:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=worker_count
            ) as executor:
                futures = [executor.submit(block_task, i, j) for i, j in jobs]
                for future in concurrent.futures.as_completed(futures):
                    if stop_requested and stop_requested():
                        return None, None
                    kpr, dr, kpt, dt = future.result()
                    if dr is not None and kpr:
                        ref_kps.extend(kpr)
                        ref_descs.append(dr)
                    if dt is not None and kpt:
                        target_kps.extend(kpt)
                        target_descs.append(dt)
        else:
            for i, j in jobs:
                kpr, dr, kpt, dt = block_task(i, j)
                if dr is not None and kpr:
                    ref_kps.extend(kpr)
                    ref_descs.append(dr)
                if dt is not None and kpt:
                    target_kps.extend(kpt)
                    target_descs.append(dt)

        if not ref_descs or not target_descs:
            return None, None

        ref_desc = np.vstack(ref_descs)
        target_desc = np.vstack(target_descs)

        ref_kps, ref_desc = select_top_keypoints(
            ref_kps, ref_desc, int(config.get("max_keypoints_used", 500))
        )
        target_kps, target_desc = select_top_keypoints(
            target_kps, target_desc, int(config.get("max_keypoints_used", 500))
        )

        try:
            matcher = cv2.FlannBasedMatcher(
                dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1),
                dict(checks=50),
            )
            matches = matcher.knnMatch(ref_desc, target_desc, k=2)
            ratio = float(config.get("ratio_threshold", 0.75))
            good = [
                m
                for pair in matches
                if len(pair) == 2
                for m, n in [pair]
                if m.distance < ratio * n.distance
            ]
        except cv2.error as exc:
            print(f"[AKAZE] matching failed: {exc}")
            return None, None

        if len(good) < int(config.get("min_matches_for_transform", 10)):
            print(f"[AKAZE] insufficient matches: {len(good)}")
            return None, None

        good = sorted(good, key=lambda item: item.distance)[
            : int(config.get("max_keypoints_used", 500))
        ]
        base_points = np.float32([ref_kps[m.queryIdx].pt for m in good]).reshape(
            -1, 1, 2
        )
        target_points = np.float32([target_kps[m.trainIdx].pt for m in good]).reshape(
            -1, 1, 2
        )
        print(f"[AKAZE] motion matches={len(good)}")
        return base_points, target_points

    def build_motion_plan(self, ctx, reference, target_dims, orchestrator, config):
        plan = [
            {
                "index": 0,
                "path": ctx.image_paths[0],
                "success": True,
                "base_points": None,
                "target_points": None,
            }
        ]
        total_targets = max(1, ctx.total_images - 1)
        for offset, path in enumerate(ctx.image_paths[1:], start=1):
            if ctx.stop_requested and ctx.stop_requested():
                break
            frame = orchestrator._load_single_frame(ctx, path, target_dims=target_dims)
            base_points, target_points = (None, None)
            if frame is not None:
                base_points, target_points = self.calculate_global_motion(
                    reference, frame, config=config, stop_requested=ctx.stop_requested
                )
            success = base_points is not None and target_points is not None
            plan.append(
                {
                    "index": offset,
                    "path": path,
                    "success": success,
                    "base_points": base_points,
                    "target_points": target_points,
                }
            )
            print(f"[AKAZE] stage1 motion index={offset} success={success}")
            if ctx.update_progress:
                ctx.update_progress(
                    20 + int((offset / total_targets) * 35),
                    f"AKAZE motion {offset}/{total_targets}",
                )
            del frame
        return plan

    @staticmethod
    def load_akaze_config(config_filename=None):
        return AKAZEAlgorithm.load_config(config_filename=config_filename)

    @staticmethod
    def load_akaze_config_for_batch(config_filename=None):
        return AKAZEAlgorithm.load_config(config_filename=config_filename)


def running_akaze(*args, **kwargs):
    raise RuntimeError(
        "AKAZE is now orchestrated by MFDenoiser. Use MFDenoiser with alignment='AKAZE' instead."
    )
