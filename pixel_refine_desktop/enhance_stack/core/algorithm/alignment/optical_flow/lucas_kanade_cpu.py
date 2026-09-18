import json
import os

import numpy as np

from config import ALGORITHM_PARAMETER_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.optical_flow_utils.flow_blocking import (
    align_with_block_flow,
)


DEFAULT_LUCAS_KANADE_CONFIG = {
    "backend": "cpu",
    "mode": "fast",
}

LUCAS_KANADE_CPU_PRESETS = {
    "fast": {
        # 32x32 grid step for fast processing.
        "grid_step": 32,
        "border_margin": 8,
        "point_workers": 2,
        "win_size": 13,
        "max_level": 1,
        "iterations": 8,
        "epsilon": 0.04,
        "overlap": 0.50,
        "adaptive": False,
        "adaptive_threshold": 1,
        "max_flow_px": 32.0,
        "use_multi_core": True,
        "tile_overlap": 0.50,
        "dense_mode": "smooth",
        "smooth": True,
    },
    "balance": {
        # 16x16 grid step for standard quality.
        "grid_step": 16,
        "border_margin": 8,
        "point_workers": 2,
        "win_size": 17,
        "max_level": 2,
        "iterations": 16,
        "epsilon": 0.015,
        "overlap": 0.50,
        "adaptive": False,
        "adaptive_threshold": 1,
        "max_flow_px": 64.0,
        "use_multi_core": True,
        "tile_overlap": 0.50,
        "dense_mode": "smooth",
        "smooth": True,
    },
    "high": {
        # 2x2 ultra-dense micro-grid for highest spatial accuracy.
        "grid_step": 2,
        "border_margin": 8,
        "point_workers": 4,
        "win_size": 25,
        "max_level": 3,
        "iterations": 32,
        "epsilon": 0.005,
        "overlap": 0.50,
        "adaptive": True,
        "adaptive_threshold": 1,
        "max_flow_px": 128.0,
        "use_multi_core": True,
        "tile_overlap": 0.50,
        "dense_mode": "smooth",
        "smooth": True,
    },
}

# Historical configurations may still contain ``medium``; keep it as an
# alias while exposing fast/balance/high as the canonical UI choices.
LUCAS_KANADE_CPU_PRESETS["medium"] = LUCAS_KANADE_CPU_PRESETS["balance"]


class LucasKanadeCPU:
    NAME = "Lucas Kanade Optical Flow"
    KIND = "alignment"
    DESCRIPTION = "Tile-based CPU Lucas-Kanade optical flow alignment."

    @staticmethod
    def _normalize_mode(mode):
        value = str(mode or "fast").strip().lower()
        if value in ("balanced", "balance", "normal", "medium"):
            return "balance"
        if value not in LUCAS_KANADE_CPU_PRESETS:
            return "fast"
        return value

    @staticmethod
    def _resolve_mode_config(config):
        mode = LucasKanadeCPU._normalize_mode(config.get("mode", "fast"))
        resolved = LUCAS_KANADE_CPU_PRESETS[mode].copy()
        resolved["mode"] = mode
        resolved["backend"] = str(config.get("backend", "cpu") or "cpu")
        return resolved

    @staticmethod
    def load_config(batch_id=None, config_filename=None):
        config = DEFAULT_LUCAS_KANADE_CONFIG.copy()
        config_filename = config_filename or ALGORITHM_PARAMETER_SETTINGS_FILE
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                config.update(params.get("LucasKanade", {}))
                config.update(params.get("LucasKanade_BATCH", {}))
        except Exception as exc:
            print(f"[LucasKanadeCPU] Failed to load config: {exc}")
        if batch_id is not None:
            try:
                from pixel_refine_desktop.enhance_stack.core.logic import (
                    batch_parameter_manager,
                )

                batch_params = batch_parameter_manager.load_json_state().get(
                    str(batch_id), {}
                )
                section = batch_params.get("lucas_kanade_params", {})
                if isinstance(section, dict):
                    config.update(section)
            except Exception as exc:
                print(f"[LucasKanadeCPU] Failed to load batch config: {exc}")
        return LucasKanadeCPU._resolve_mode_config(config)

    @staticmethod
    def load_lucas_kanade_config(config_filename=None):
        return LucasKanadeCPU.load_config(config_filename=config_filename)

    @staticmethod
    def load_lucas_kanade_config_for_batch(config_filename=None):
        return LucasKanadeCPU.load_config(config_filename=config_filename)

    def calculate_flow(self, reference_gray, target_gray, config, point_executor=None):
        """Run the full-frame Taichi AOT Lucas-Kanade implementation."""
        from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLK

        win_size = max(5, int(config.get("win_size", 17)))
        if win_size % 2 == 0:
            win_size += 1

        smooth = config.get("smooth", None)
        if smooth is not None:
            dense_mode = "smooth" if bool(smooth) else "blocky_clamped"
            overlap = 0.50 if bool(smooth) else 0.0
        else:
            dense_mode = str(config.get("dense_mode") or "smooth")
            overlap = float(config.get("overlap", 0.50))

        flow = calcOpticalFlowPyrLK(
            np.ascontiguousarray(reference_gray),
            np.ascontiguousarray(target_gray),
            winSize=(win_size, win_size),
            maxLevel=max(0, int(config.get("max_level", 2))),
            criteria=(
                3,
                max(1, int(config.get("iterations", 8))),
                float(config.get("epsilon", 0.03)),
            ),
            grid_step=max(1, int(config.get("grid_step", 16))),
            border_margin=max(0, int(config.get("border_margin", 8))),
            overlap=overlap,
            adaptive=bool(config.get("adaptive", False)),
            adaptive_threshold=max(1, int(config.get("adaptive_threshold", 1))),
            motion_mode=str(config.get("motion_mode") or "fast"),
            dense_mode=dense_mode,
            max_flow_px=float(config.get("max_flow_px", 0.0)),
        )
        if isinstance(flow, tuple):
            flow = flow[0]
        flow = np.asarray(flow, dtype=np.float32)
        expected = (*reference_gray.shape[:2], 2)
        if flow.shape != expected or not np.isfinite(flow).all():
            raise RuntimeError(
                f"Taichi Lucas-Kanade returned invalid flow: {flow.shape}, expected {expected}"
            )
        return np.ascontiguousarray(flow)

    def _make_grid_points(self, width, height, config):
        step = max(1, int(config.get("grid_step", 16)))
        margin = max(0, int(config.get("border_margin", 8)))
        x_start = min(margin, max(0, width - 1))
        y_start = min(margin, max(0, height - 1))
        x_stop = max(x_start + 1, width - margin)
        y_stop = max(y_start + 1, height - margin)

        xs = np.arange(x_start, x_stop, step, dtype=np.float32)
        ys = np.arange(y_start, y_stop, step, dtype=np.float32)
        if xs.size == 0 or ys.size == 0:
            return None
        grid_x, grid_y = np.meshgrid(xs, ys)
        return np.column_stack((grid_x.ravel(), grid_y.ravel())).reshape(-1, 1, 2)

    def _track_grid_points(
        self,
        reference_gray,
        target_gray,
        points,
        config,
        win_size,
        point_executor=None,
    ):
        # This compatibility helper now samples the canonical dense Taichi
        # result. It deliberately cannot fall back to a second tracker.
        dense_flow = self.calculate_flow(reference_gray, target_gray, config)
        points_xy = np.asarray(points, dtype=np.float32).reshape(-1, 2)
        height, width = dense_flow.shape[:2]
        x = np.clip(np.rint(points_xy[:, 0]).astype(np.int32), 0, width - 1)
        y = np.clip(np.rint(points_xy[:, 1]).astype(np.int32), 0, height - 1)
        next_points = (points_xy + dense_flow[y, x]).reshape(-1, 1, 2)
        status = np.isfinite(next_points).all(axis=2).astype(np.uint8).reshape(-1, 1)
        return next_points, status

    def _densify_sparse_flow(self, sparse_flow, known):
        if not np.any(known):
            return sparse_flow

        dense = sparse_flow.astype(np.float32, copy=True)
        valid = known.astype(np.float32)

        def box_blur(array):
            padded = np.pad(array, ((1, 1), (1, 1)), mode="edge")
            return (
                sum(
                    padded[dy : dy + array.shape[0], dx : dx + array.shape[1]]
                    for dy in range(3)
                    for dx in range(3)
                )
                / 9.0
            )

        for _ in range(64):
            missing = valid <= 0
            if not np.any(missing):
                break
            weighted = dense * valid[..., None]
            blur_flow = np.stack(
                [box_blur(weighted[..., channel]) for channel in range(2)], axis=-1
            )
            blur_weight = box_blur(valid)
            can_fill = missing & (blur_weight > 1e-6)
            dense[can_fill] = blur_flow[can_fill] / blur_weight[can_fill, None]
            valid[can_fill] = 1.0
        return dense

    def align_frame(
        self,
        reference,
        target,
        config=None,
        stop_requested=None,
        tile_executor=None,
        point_executor=None,
        target_for_warping=None,
    ):
        config = config or self.load_config()

        def flow_func(reference_gray, target_gray):
            return self.calculate_flow(
                reference_gray,
                target_gray,
                config,
                point_executor=point_executor,
            )

        halo = int(config.get("win_size", 15)) * (
            2 ** max(0, int(config.get("max_level", 2)) - 1)
        )
        return align_with_block_flow(
            reference,
            target,
            flow_func,
            halo=halo,
            use_multi_core=bool(config.get("use_multi_core", True)),
            stop_requested=stop_requested,
            executor=tile_executor,
            target_for_warping=target_for_warping,
        )

    def build_flow_alignment(self, ctx, reference, target_dims, orchestrator, config):
        raise RuntimeError(
            "HDF5 storage is deprecated and has been completely removed. "
            "Use the resident memory pipeline instead."
        )

    def run(self, ctx, frames, batch_plan=None):
        return list(frames)
