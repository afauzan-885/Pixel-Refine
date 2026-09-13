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
        # Latency profile: half the grid density of balance and a 9px window.
        # Keep the native pyramid path disabled here: on low-end CUDA devices
        # its extra staging dominates the sparse-search savings.
        "grid_step": 48,
        "border_margin": 8,
        "win_size": 9,
        "max_level": 2,
        "iterations": 1,
        "epsilon": 0.02,
        "motion_mode": "fast",
        "adaptive": False,
        "adaptive_threshold": 1,
        "use_multi_core": False,
        "tile_overlap": 0.20,
        "max_flow_px": 48.0,
        "decoupled_scale": 0,
        "dense_mode": "blocky_clamped",
    },
    "balance": {
        # Denser grid and smooth interpolation preserve detail; one adaptive
        # residual pass keeps balance mode accuracy-oriented as requested.
        "grid_step": 24,
        "border_margin": 8,
        "win_size": 17,
        "max_level": 3,
        "iterations": 2,
        "epsilon": 0.02,
        "motion_mode": "fast",
        "adaptive": True,
        "adaptive_threshold": 1,
        "use_multi_core": False,
        "tile_overlap": 0.20,
        "max_flow_px": 64.0,
        "dense_mode": "smooth",
        "decoupled_scale": 0,
        "cache_reference_pyramid": True,
    },
    "high": {
        # Accuracy profile: finest grid, extra pyramid level, smooth dense
        # interpolation, and adaptive residual refinement.
        "grid_step": 16,
        "border_margin": 8,
        "win_size": 17,
        "max_level": 3,
        "iterations": 3,
        "epsilon": 0.02,
        "motion_mode": "fast",
        "adaptive": True,
        "adaptive_threshold": 1,
        "use_multi_core": False,
        "tile_overlap": 0.20,
        "max_flow_px": 96.0,
        "dense_mode": "smooth",
        "decoupled_scale": 0,
        "cache_reference_pyramid": True,
    },
}


class BlockMatchingGPU(LucasKanadeGPU):
    NAME = "Block Matching GPU Optical Flow"
    KIND = "alignment"
    DESCRIPTION = "Native AOT Block Matching optical flow for CPU, Vulkan, and OpenGL."
    GPU_MODULES = ("common", "block_matching", "pyramid", "remap")
    DEVICE_RESERVATION = "block_matching_frame"

    def _calculate_flow_host_native(self, reference_gray, target_gray, config):
        from taichi_vision.taichi_algorithm import calcOpticalFlowBlockMatching
        flow = calcOpticalFlowBlockMatching(
            np.ascontiguousarray(reference_gray, dtype=np.float32),
            np.ascontiguousarray(target_gray, dtype=np.float32),
            **self._build_opengl_safe_params(reference_gray, config), return_gpu=False,
        )
        if isinstance(flow, tuple):
            flow = flow[0]
        return np.ascontiguousarray(flow, dtype=np.float32)

    def _build_opengl_safe_params(self, reference_gray, config):
        params = self._build_lk_params(config)
        from taichi_vision import taichi_aot
        if str(getattr(taichi_aot.engine, "arch", "")).lower() == "opengl":
            # Keep Block Matching at level-zero on Intel OpenGL. Its graph
            # shares SSBO bindings with the Lucas pyramid and some drivers
            # reject the combined binding set when algorithms are switched
            # in the same process.
            params["maxLevel"] = 0
            if max(reference_gray.shape[:2]) > 768:
                params["grid_step"] = max(64, int(params["grid_step"]))
        return params

    def _build_lk_params(self, config):
        """Build block-matching parameters, including optional decoupling."""
        params = super()._build_lk_params(config)
        params["dense_mode"] = str(config.get("dense_mode", "blocky_clamped"))
        params["adaptive"] = bool(config.get("adaptive", False))
        params["adaptive_threshold"] = max(
            1, int(config.get("adaptive_threshold", 1))
        )
        params["decoupled_scale"] = max(
            0, int(config.get("decoupled_scale", 0) or 0)
        )
        return params

    def align_frame(
        self,
        reference,
        target,
        config=None,
        stop_requested=None,
        tile_executor=None,
        point_executor=None,
        matching_reference=None,
        matching_target=None,
    ):
        # Resolve the selected preset here as well as in load_config().  UI
        # callers commonly pass only {"mode": "fast"}; forwarding that
        # partial mapping used to silently fall back to base defaults.
        cfg = self._resolve_mode_config(dict(config or self.load_config()))
        cfg.setdefault("cache_reference_pyramid", True)
        cfg.setdefault("retain_native_pool", True)
        cfg.setdefault("conservative_vram", True)
        cfg.setdefault("_reference_cache_key", id(reference))
        try:
            from taichi_vision import taichi_aot

            pool = getattr(taichi_aot.engine, "buffer_pool", None)
            if pool is not None and hasattr(pool, "set_budget"):
                pool.set_budget(128 * 1024 * 1024)
        except Exception:
            pass
        try:
            from taichi_vision.taichi_aot import naturalTonemapping
            from config import CALCULATION_TONE_MAPPING_PARAMS
            matching_reference = naturalTonemapping(
                reference, return_gpu=False, **CALCULATION_TONE_MAPPING_PARAMS
            )
            matching_target = naturalTonemapping(
                target, return_gpu=False, **CALCULATION_TONE_MAPPING_PARAMS
            )
            print("[BlockMatchingGPU] naturalTonemapping enabled for flow matching; original frame retained for warping")
        except Exception as exc:
            print(f"[BlockMatchingGPU] Tone mapping unavailable, using original frames: {exc}")
            matching_reference, matching_target = reference, target
        return super().align_frame(
            reference,
            target,
            config=cfg,
            stop_requested=stop_requested,
            tile_executor=tile_executor,
            point_executor=point_executor,
            matching_reference=matching_reference,
            matching_target=matching_target,
        )

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
        resolved = BlockMatchingGPU._resolve_mode_config(visible_config)
        # Keep the reference pyramid and released per-frame temporaries
        # reusable.  The base GPU aligner used to clear the pool on every
        # frame, which turned Block Matching into an allocation benchmark.
        resolved.setdefault("cache_reference_pyramid", True)
        resolved.setdefault("retain_native_pool", True)
        resolved.setdefault("conservative_vram", True)
        return resolved

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
        for key, value in config.items():
            if key != "mode":
                resolved[key] = value
        resolved["mode"] = mode
        return resolved

    @staticmethod
    def load_block_matching_gpu_config(config_filename=None):
        return BlockMatchingGPU.load_config(config_filename=config_filename)

    @staticmethod
    def load_block_matching_gpu_config_for_batch(config_filename=None):
        return BlockMatchingGPU.load_config(config_filename=config_filename)

    def calculate_flow(self, reference_gray, target_gray, config, point_executor=None):
        from taichi_vision.taichi_algorithm import calcOpticalFlowBlockMatching

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
            if bool(config.get("strict", False)):
                raise RuntimeError("strict block-matching AOT flow failed") from exc
        if bool(config.get("strict", False)):
            raise RuntimeError("Block Matching AOT returned no flow")
        return np.zeros((reference_gray.shape[0], reference_gray.shape[1], 2), dtype=np.float32)

    def _calculate_flow_gpu_buffer(
        self,
        reference_gray,
        target_gray,
        config,
        reference_pyramid=None,
    ):
        from taichi_vision.taichi_algorithm import calcOpticalFlowBlockMatching

        flow_kwargs = {
            "prev": reference_gray,
            "next": target_gray,
            **self._build_lk_params(config),
            "return_gpu": True,
        }
        if reference_pyramid is not None:
            flow_kwargs["reference_pyramid"] = reference_pyramid
        flow = calcOpticalFlowBlockMatching(**flow_kwargs)
        if isinstance(flow, tuple):
            flow = flow[0]
        if flow is None or not hasattr(flow, "shape"):
            raise RuntimeError("Block Matching AOT did not return a GPU flow buffer")
        return flow
