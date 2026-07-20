from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.lucas_kanade_gpu import LucasKanadeGPU
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.optical_flow_utils.flow_blocking import to_flow_gray_u8
import numpy as np
import os
import json

ALGORITHM_PARAMETER_SETTINGS_FILE = "algorithm_parameter_settings.json"

DEFAULT_BLOCK_MATCHING_GPU_CONFIG = {
    "mode": "fast",
}

BLOCK_MATCHING_GPU_PRESETS = {
    "fast": {
        "grid_step": 48,
        "border_margin": 8,
        "win_size": 13,
        "max_level": 2,
        "iterations": 1,
        "epsilon": 0.02,
        "motion_mode": "fast",
        "adaptive": False,
        "adaptive_threshold": 1,
        "use_multi_core": False,
        "tile_cols": 1,
        "tile_rows": 1,
        "tile_overlap": 0.20,
        "max_flow_px": 48.0,
    },
    "balance": {
        "grid_step": 32,
        "border_margin": 8,
        "win_size": 15,
        "max_level": 2,
        "iterations": 1,
        "epsilon": 0.02,
        "motion_mode": "fast",
        "adaptive": False,
        "adaptive_threshold": 1,
        "use_multi_core": False,
        "tile_cols": 2,
        "tile_rows": 2,
        "tile_overlap": 0.20,
        "max_flow_px": 64.0,
    },
    "high": {
        "grid_step": 16,
        "border_margin": 8,
        "win_size": 17,
        "max_level": 3,
        "iterations": 1,
        "epsilon": 0.02,
        "motion_mode": "fast",
        "adaptive": False,
        "adaptive_threshold": 1,
        "use_multi_core": False,
        "tile_cols": 3,
        "tile_rows": 2,
        "tile_overlap": 0.20,
        "max_flow_px": 96.0,
    },
}


class BlockMatchingGPU(LucasKanadeGPU):
    NAME = "Block Matching GPU Optical Flow"
    KIND = "alignment"
    DESCRIPTION = "Tile-based GPU AOT Block Matching + Parabolic Fit optical flow alignment."

    @staticmethod
    def load_config(batch_id=None, config_filename=None):
        visible_config = DEFAULT_BLOCK_MATCHING_GPU_CONFIG.copy()
        config_filename = config_filename or ALGORITHM_PARAMETER_SETTINGS_FILE
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                section = params.get("BlockMatchingGPU", {})
                if isinstance(section, dict):
                    visible_config.update(section)
        except Exception as exc:
            print(f"[BlockMatchingGPU] Failed to load config: {exc}")
        if batch_id is not None:
            try:
                from pixel_refine_desktop.enhance_stack.core.logic import (
                    batch_parameter_manager,
                )

                batch_params = batch_parameter_manager.load_json_state().get(
                    str(batch_id),
                    {},
                )
                section = batch_params.get("block_matching_gpu_params", {})
                if isinstance(section, dict):
                    visible_config.update(section)
            except Exception as exc:
                print(f"[BlockMatchingGPU] Failed to load batch config: {exc}")
        return BlockMatchingGPU._resolve_mode_config(visible_config)

    @staticmethod
    def _normalize_mode(mode):
        value = str(mode or "fast").strip().lower()
        if value in ("balanced", "balance mode"):
            return "balance"
        if value not in BLOCK_MATCHING_GPU_PRESETS:
            return "fast"
        return value

    @staticmethod
    def _resolve_mode_config(config):
        mode = BlockMatchingGPU._normalize_mode(config.get("mode", "fast"))
        resolved = BLOCK_MATCHING_GPU_PRESETS[mode].copy()
        resolved["mode"] = mode
        return resolved

    @staticmethod
    def load_block_matching_gpu_config(config_filename=None):
        return BlockMatchingGPU.load_config(config_filename=config_filename)

    @staticmethod
    def load_block_matching_gpu_config_for_batch(config_filename=None):
        return BlockMatchingGPU.load_config(config_filename=config_filename)

    def calculate_flow(self, reference_gray, target_gray, config, point_executor=None):
        from taichi_library.taichi_algorithm import calcOpticalFlowBlockMatching

        lk_params = self._build_lk_params(config)

        try:
            flow = calcOpticalFlowBlockMatching(
                reference_gray,
                target_gray,
                **lk_params,
            )
            if isinstance(flow, tuple):
                flow = flow[0]
            if flow is not None:
                return np.ascontiguousarray(flow, dtype=np.float32)
        except Exception as exc:
            print(
                f"[BlockMatchingGPU] Dense AOT flow failed: {exc}"
            )
        return np.zeros((reference_gray.shape[0], reference_gray.shape[1], 2), dtype=np.float32)

    def _calculate_flow_gpu_buffer(self, reference_gray, target_gray, config):
        from taichi_library.taichi_algorithm import calcOpticalFlowBlockMatching

        flow = calcOpticalFlowBlockMatching(
            reference_gray,
            target_gray,
            **self._build_lk_params(config),
            return_gpu=True,
        )
        if isinstance(flow, tuple):
            flow = flow[0]
        if flow is None or not hasattr(flow, "shape"):
            raise RuntimeError("Block Matching AOT did not return a GPU flow buffer")
        return flow
