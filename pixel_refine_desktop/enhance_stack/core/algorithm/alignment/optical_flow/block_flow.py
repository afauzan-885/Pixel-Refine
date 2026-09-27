"""
Block Flow Optical Flow Alignment Module
========================================

Canonical Block Flow implementation unifying Taichi AOT native hierarchical
block matching and optical flow (compute_flow.tcm) with memory-bounded
streaming compositor for CPU and GPU fallback.
"""

import json
import os
import numpy as np

from config import ALGORITHM_PARAMETER_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.lucas_kanade import (
    LucasKanade,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.optical_flow_utils.flow_blocking import (
    align_with_block_flow,
    to_flow_gray_u8,
)


DEFAULT_BLOCK_FLOW_CONFIG = {
    "backend": "auto",
    "mode": "balance",
    "smooth": True,
    "adaptive": True,
    "conservative_vram": True,
}

BLOCK_FLOW_PRESETS = {
    "fast": {
        "grid_step": 32,
        "border_margin": 8,
        "win_size": 13,
        "max_level": 1,
        "iterations": 8,
        "epsilon": 0.05,
        "overlap": 0.50,
        "smooth": True,
        "adaptive": False,
        "tile_overlap": 0.20,
        "max_flow_px": 48.0,
    },
    "balance": {
        "grid_step": 16,
        "border_margin": 8,
        "win_size": 17,
        "max_level": 2,
        "iterations": 16,
        "epsilon": 0.015,
        "overlap": 0.50,
        "smooth": True,
        "adaptive": True,
        "tile_overlap": 0.35,
        "max_flow_px": 64.0,
    },
    "high": {
        "grid_step": 8,
        "border_margin": 8,
        "win_size": 21,
        "max_level": 3,
        "iterations": 24,
        "epsilon": 0.01,
        "overlap": 0.50,
        "smooth": True,
        "adaptive": True,
        "tile_overlap": 0.50,
        "max_flow_px": 96.0,
    },
}


class BlockFlow(LucasKanade):
    """Canonical Block Flow alignment algorithm."""

    NAME = "Block Flow"
    CATEGORY = "optical_flow"
    PRESETS = BLOCK_FLOW_PRESETS

    @staticmethod
    def load_config(config_filename=None):
        target_file = config_filename or ALGORITHM_PARAMETER_SETTINGS_FILE
        loaded_config = dict(DEFAULT_BLOCK_FLOW_CONFIG)
        if os.path.exists(target_file):
            try:
                with open(target_file, "r") as f:
                    data = json.load(f)
                section = data.get("BlockFlow") or data.get("block_flow_params") or {}
                loaded_config.update(section)
            except Exception:
                pass
        return loaded_config

    load_block_flow_config = load_config
    load_block_flow_config_for_batch = load_config

    def calculate_flow(
        self,
        reference_gray,
        target_gray,
        config,
        point_executor=None,
        return_gpu=False,
    ):
        """Calculate dense block flow using Taichi AOT TCM block matching."""
        ref_u8 = to_flow_gray_u8(reference_gray)
        tgt_u8 = to_flow_gray_u8(target_gray)

        from taichi_vision.taichi_algorithm import calcOpticalFlowBlockMatching

        lk_params = self._build_lk_params(config)
        if return_gpu:
            lk_params["return_gpu"] = True

        try:
            flow = calcOpticalFlowBlockMatching(
                ref_u8,
                tgt_u8,
                **lk_params,
            )
            if isinstance(flow, tuple):
                flow = flow[0]
            if flow is not None:
                if return_gpu:
                    return flow
                return np.ascontiguousarray(flow, dtype=np.float32)
        except Exception as exc:
            if bool(config.get("strict", False)):
                raise RuntimeError("Block Flow AOT failed") from exc

        return np.zeros((ref_u8.shape[0], ref_u8.shape[1], 2), dtype=np.float32)

    def align_frame(
        self,
        reference,
        target,
        config=None,
        point_executor=None,
        tile_executor=None,
        stop_requested=None,
        matching_reference=None,
        matching_target=None,
        target_for_warping=None,
        return_gpu=False,
    ):
        """Align a frame using memory-bounded Block Flow."""
        active_config = self.load_config() if config is None else dict(config)

        # 1. GPU Resident Native Alignment (Zero CPU RAM)
        if not bool(active_config.get("use_multi_core", False)):
            try:
                return self._align_frame_gpu_flow_remap(
                    reference=reference,
                    target=target,
                    config=active_config,
                    stop_requested=stop_requested,
                    matching_reference=matching_reference,
                    matching_target=matching_target,
                    return_gpu=return_gpu,
                )
            except Exception:
                pass

        # 2. Host streaming fallback with bounded peak RAM
        def flow_func(r_gray, t_gray):
            return self.calculate_flow(
                r_gray,
                t_gray,
                active_config,
                point_executor=point_executor,
                return_gpu=False,
            )

        halo = int(active_config.get("win_size", 17)) + int(
            active_config.get("max_flow_px", 64.0)
        )
        return align_with_block_flow(
            reference,
            target,
            flow_func,
            halo=halo,
            use_multi_core=bool(active_config.get("use_multi_core", True)),
            stop_requested=stop_requested,
            executor=tile_executor,
            target_for_warping=target_for_warping,
        )

    def close(self):
        """Release allocated tile buffers and resources."""
        self._cleanup_tile_buffers()
