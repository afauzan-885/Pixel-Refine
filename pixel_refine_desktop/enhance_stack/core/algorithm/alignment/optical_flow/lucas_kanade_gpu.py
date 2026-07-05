import json
import os

import numpy as np
import cv2

from config import ALGORITHM_PARAMETER_SETTINGS_FILE

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.lucas_kanade_cpu import (
    LucasKanadeCPU,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.optical_flow_utils.flow_blocking import (
    _restore_dtype,
    align_with_tiled_flow,
    iter_flow_tiles,
)


DEFAULT_LUCAS_KANADE_GPU_CONFIG = {
    "mode": "fast",
}

LUCAS_KANADE_GPU_PRESETS = {
    "fast": {
        "grid_step": 32,
        "border_margin": 8,
        "win_size": 13,
        "max_level": 2,
        "iterations": 8,
        "epsilon": 0.03,
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
        "grid_step": 20,
        "border_margin": 8,
        "win_size": 15,
        "max_level": 2,
        "iterations": 12,
        "epsilon": 0.02,
        "motion_mode": "fast",
        "adaptive": False,
        "adaptive_threshold": 1,
        "use_multi_core": False,
        "tile_cols": 1,
        "tile_rows": 1,
        "tile_overlap": 0.25,
        "max_flow_px": 64.0,
    },
    "auto": {
        "grid_step": 24,
        "border_margin": 8,
        "win_size": 15,
        "max_level": 2,
        "iterations": 12,
        "epsilon": 0.02,
        "motion_mode": "auto",
        "adaptive": False,
        "adaptive_threshold": 1,
        "use_multi_core": False,
        "tile_cols": 1,
        "tile_rows": 1,
        "tile_overlap": 0.20,
        "max_flow_px": 96.0,
    },
}


class LucasKanadeGPU(LucasKanadeCPU):
    NAME = "Lucas Kanade GPU Optical Flow"
    KIND = "alignment"
    DESCRIPTION = "Tile-based GPU AOT Lucas-Kanade optical flow alignment."
    _gpu_remap_disabled = False
    _reported_gpu_remap_disabled = False

    @staticmethod
    def load_config(batch_id=None, config_filename=None):
        visible_config = DEFAULT_LUCAS_KANADE_GPU_CONFIG.copy()
        config_filename = config_filename or ALGORITHM_PARAMETER_SETTINGS_FILE
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                section = params.get("LucasKanadeGPU", {})
                if isinstance(section, dict):
                    visible_config.update(section)
        except Exception as exc:
            print(f"[LucasKanadeGPU] Failed to load config: {exc}")
        if batch_id is not None:
            try:
                from pixel_refine_desktop.enhance_stack.core.logic import (
                    batch_parameter_manager,
                )

                batch_params = batch_parameter_manager.load_json_state().get(
                    str(batch_id),
                    {},
                )
                section = batch_params.get("lucas_kanade_gpu_params", {})
                if isinstance(section, dict):
                    visible_config.update(section)
            except Exception as exc:
                print(f"[LucasKanadeGPU] Failed to load batch config: {exc}")
        return LucasKanadeGPU._resolve_mode_config(visible_config)

    @staticmethod
    def _normalize_mode(mode):
        value = str(mode or "fast").strip().lower()
        if value in ("balanced", "balance mode"):
            return "balance"
        if value not in LUCAS_KANADE_GPU_PRESETS:
            return "fast"
        return value

    @staticmethod
    def _resolve_mode_config(config):
        mode = LucasKanadeGPU._normalize_mode(config.get("mode", "fast"))
        resolved = LUCAS_KANADE_GPU_PRESETS[mode].copy()
        resolved["mode"] = mode
        return resolved

    @staticmethod
    def load_lucas_kanade_gpu_config(config_filename=None):
        return LucasKanadeGPU.load_config(config_filename=config_filename)

    @staticmethod
    def load_lucas_kanade_gpu_config_for_batch(config_filename=None):
        return LucasKanadeGPU.load_config(config_filename=config_filename)

    def _build_lk_params(self, config):
        win_size = max(5, int(config.get("win_size", 13)))
        if win_size % 2 == 0:
            win_size += 1

        return {
            "winSize": (win_size, win_size),
            "maxLevel": max(0, int(config.get("max_level", 2))),
            "criteria": (
                3,
                max(1, int(config.get("iterations", 8))),
                float(config.get("epsilon", 0.03)),
            ),
            "grid_step": max(4, int(config.get("grid_step", 48))),
            "border_margin": max(0, int(config.get("border_margin", 8))),
            "motion_mode": str(config.get("motion_mode", "fast")),
            "dense_mode": "blocky_clamped",
            "max_flow_px": float(config.get("max_flow_px", 64.0)),
        }

    def calculate_flow(self, reference_gray, target_gray, config, point_executor=None):
        from taichi_library.taichi_algorithm import calcOpticalFlowPyrLK

        lk_params = self._build_lk_params(config)

        try:
            flow = calcOpticalFlowPyrLK(
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
                f"[LucasKanadeGPU] Dense AOT flow failed, falling back to grid flow: {exc}"
            )

        return self._calculate_flow_grid_fallback(
            reference_gray,
            target_gray,
            config,
            lk_params,
        )

    def _calculate_flow_gpu_buffer(self, reference_gray, target_gray, config):
        from taichi_library.taichi_algorithm import calcOpticalFlowPyrLK

        flow = calcOpticalFlowPyrLK(
            reference_gray,
            target_gray,
            **self._build_lk_params(config),
            return_gpu=True,
        )
        if isinstance(flow, tuple):
            flow = flow[0]
        if flow is None or not hasattr(flow, "shape"):
            raise RuntimeError("Lucas Kanade AOT did not return a GPU flow buffer")
        return flow

    def align_frame(
        self,
        reference,
        target,
        config=None,
        stop_requested=None,
        tile_executor=None,
        point_executor=None,
    ):
        config = config or self.load_config()
        if reference is None or target is None:
            return None

        if LucasKanadeGPU._gpu_remap_disabled:
            if not LucasKanadeGPU._reported_gpu_remap_disabled:
                print(
                    "[LucasKanadeGPU] GPU remap path disabled after previous failure; "
                    "using CPU/OpenCV fallback."
                )
                LucasKanadeGPU._reported_gpu_remap_disabled = True
            return self._align_frame_cpu_fallback(
                reference,
                target,
                config=config,
                stop_requested=stop_requested,
                tile_executor=tile_executor,
                point_executor=point_executor,
            )

        try:
            return self._align_frame_gpu_flow_remap(
                reference,
                target,
                config,
                stop_requested=stop_requested,
            )
        except Exception as exc:
            LucasKanadeGPU._gpu_remap_disabled = True
            print(
                f"[LucasKanadeGPU] GPU remap path failed, falling back to CPU remap: {exc}"
            )
            return self._align_frame_cpu_fallback(
                reference,
                target,
                config=config,
                stop_requested=stop_requested,
                tile_executor=tile_executor,
                point_executor=point_executor,
            )

    def _align_frame_cpu_fallback(
        self,
        reference,
        target,
        config,
        stop_requested=None,
        tile_executor=None,
        point_executor=None,
    ):
        fallback_config = dict(config)
        fallback_config["use_multi_core"] = True
        fallback_config["tile_cols"] = max(2, int(fallback_config.get("tile_cols", 1)))
        fallback_config["tile_rows"] = max(2, int(fallback_config.get("tile_rows", 1)))
        fallback_config["point_workers"] = max(
            2,
            int(fallback_config.get("point_workers", 2)),
        )

        def flow_func(reference_gray, target_gray):
            return LucasKanadeCPU.calculate_flow(
                self,
                reference_gray,
                target_gray,
                fallback_config,
                point_executor=point_executor,
            )

        return align_with_tiled_flow(
            reference,
            target,
            flow_func,
            cols=int(fallback_config.get("tile_cols", 3)),
            rows=int(fallback_config.get("tile_rows", 2)),
            overlap=float(fallback_config.get("tile_overlap", 0.20)),
            use_multi_core=True,
            stop_requested=stop_requested,
            executor=tile_executor,
        )

    def build_flow_alignment(self, ctx, reference, target_dims, orchestrator, config):
        fallback_config = dict(config)
        fallback_config["use_multi_core"] = True
        fallback_config["tile_cols"] = max(2, int(fallback_config.get("tile_cols", 1)))
        fallback_config["tile_rows"] = max(2, int(fallback_config.get("tile_rows", 1)))
        fallback_config["point_workers"] = max(
            2,
            int(fallback_config.get("point_workers", 2)),
        )
        return super().build_flow_alignment(
            ctx,
            reference,
            target_dims,
            orchestrator,
            fallback_config,
        )

    def _align_frame_gpu_flow_remap(
        self,
        reference,
        target,
        config,
        stop_requested=None,
    ):
        from taichi_library import taichi_aot

        height, width = reference.shape[:2]
        tiles = self._build_tiles(width, height, config)
        accumulator, weights, target_ref = self._create_gpu_accumulators(target)
        buffers = [accumulator, weights, target_ref]

        try:
            for tile in tiles:
                if stop_requested and stop_requested():
                    return None

                warped_gpu = self._warp_tile_gpu(
                    tile,
                    reference,
                    target,
                    config,
                )
                if warped_gpu is None:
                    continue
                try:
                    self._accumulate_tile_gpu(
                        taichi_aot,
                        accumulator,
                        weights,
                        tile,
                        warped_gpu,
                    )
                finally:
                    warped_gpu.release()

            result_gpu = taichi_aot.mean_division(accumulator, weights, target_ref)
            buffers.append(result_gpu)
            return _restore_dtype(result_gpu.to_numpy(), target.dtype)
        finally:
            for buffer in buffers:
                if buffer is not None and hasattr(buffer, "release"):
                    buffer.release()

    @staticmethod
    def _build_tiles(width, height, config):
        return list(
            iter_flow_tiles(
                width,
                height,
                cols=int(config.get("tile_cols", 2)),
                rows=int(config.get("tile_rows", 2)),
                overlap=float(config.get("tile_overlap", 0.20)),
            )
        )

    @staticmethod
    def _create_gpu_accumulators(target):
        from taichi_library import taichi_aot

        is_color = target.ndim == 3
        accumulator = taichi_aot.upload(
            np.zeros(target.shape, dtype=np.float32),
            is_vector=is_color,
        )
        weights = taichi_aot.upload(
            np.zeros(target.shape[:2], dtype=np.float32),
            is_vector=False,
        )
        target_ref = taichi_aot.upload(
            target.astype(np.float32, copy=False),
            is_vector=is_color,
        )
        return accumulator, weights, target_ref

    def _warp_tile_gpu(self, tile, reference, target, config):
        from taichi_library import taichi_aot

        rx0, ry0, rx1, ry1 = tile["roi"]
        ref_roi = reference[ry0:ry1, rx0:rx1]
        target_roi_original = target[ry0:ry1, rx0:rx1]
        ref_gpu = None
        target_gpu = None
        ref_gray_gpu = None
        target_gray_gpu = None
        flow_gpu = None

        try:
            ref_gpu = taichi_aot.upload(
                ref_roi.astype(np.float32, copy=False),
                is_vector=ref_roi.ndim == 3,
            )
            target_gpu = taichi_aot.upload(
                target_roi_original.astype(np.float32, copy=False),
                is_vector=target_roi_original.ndim == 3,
            )
            ref_gray_gpu = self._to_gpu_gray(taichi_aot, ref_gpu)
            target_gray_gpu = self._to_gpu_gray(taichi_aot, target_gpu)
            flow_gpu = self._calculate_flow_gpu_buffer(
                ref_gray_gpu,
                target_gray_gpu,
                config,
            )
            roi_h, roi_w = ref_gray_gpu.shape[:2]
            warped_roi = taichi_aot.remap_with_flow(
                target_gpu,
                flow_gpu,
                roi_h,
                roi_w,
                return_gpu=True,
            )
        finally:
            if flow_gpu is not None and hasattr(flow_gpu, "release"):
                flow_gpu.release()
            if ref_gray_gpu is not None and hasattr(ref_gray_gpu, "release"):
                ref_gray_gpu.release()
            if target_gray_gpu is not None and hasattr(target_gray_gpu, "release"):
                target_gray_gpu.release()
            if ref_gpu is not None and hasattr(ref_gpu, "release"):
                ref_gpu.release()
            if target_gpu is not None and hasattr(target_gpu, "release"):
                target_gpu.release()

        return warped_roi

    @staticmethod
    def _to_gpu_gray(taichi_aot, image_gpu):
        from taichi_library.taichi_algorithm import ta

        if len(image_gpu.shape) == 2:
            return ta.clip(image_gpu, 0.0, 255.0)

        gray_gpu = taichi_aot.rgb2gray(image_gpu)
        try:
            return ta.clip(gray_gpu, 0.0, 255.0)
        finally:
            if gray_gpu is not None and hasattr(gray_gpu, "release"):
                gray_gpu.release()

    @staticmethod
    def _accumulate_tile_gpu(taichi_aot, accumulator, weights, tile, warped_gpu):
        rx0, ry0, _rx1, _ry1 = tile["roi"]
        tile_h, tile_w = warped_gpu.shape[:2]
        hanning_gpu = None
        tile_weight_gpu = None

        try:
            hanning_gpu = taichi_aot.generate_hanning_window_2d(
                (tile_h, tile_w),
                exclude_boundary=True,
            )
            tile_weight_gpu = taichi_aot.upload(
                np.ones((tile_h, tile_w), dtype=np.float32),
                is_vector=False,
            )
            taichi_aot.stitch_tile(
                warped_gpu,
                tile_weight_gpu,
                hanning_gpu,
                accumulator,
                weights,
                ry0,
                rx0,
            )
        finally:
            if hanning_gpu is not None:
                hanning_gpu.release()
            if tile_weight_gpu is not None:
                tile_weight_gpu.release()

    def _calculate_flow_grid_fallback(
        self, reference_gray, target_gray, config, lk_params
    ):
        from taichi_library.taichi_algorithm import calcOpticalFlowPyrLKGrid

        grid_result = calcOpticalFlowPyrLKGrid(
            reference_gray,
            target_gray,
            winSize=lk_params["winSize"],
            maxLevel=lk_params["maxLevel"],
            criteria=lk_params["criteria"],
            grid_step=max(4, int(config.get("grid_step", 48))),
            border_margin=max(0, int(config.get("border_margin", 8))),
            motion_mode=str(config.get("motion_mode", "fast")),
        )
        if isinstance(grid_result, tuple):
            grid_result = grid_result[0]
        if not grid_result or "grid_flow" not in grid_result:
            height, width = reference_gray.shape[:2]
            return np.zeros((height, width, 2), dtype=np.float32)
        return self._dense_from_aot_grid(reference_gray.shape[:2], grid_result)

    def _dense_from_aot_grid(self, shape, grid_result):
        height, width = shape
        grid_flow = np.asarray(grid_result["grid_flow"], dtype=np.float32)
        grid_h, grid_w = grid_flow.shape[:2]
        if grid_h <= 0 or grid_w <= 0:
            return np.zeros((height, width, 2), dtype=np.float32)

        valid = grid_flow[..., 2] > 0.5
        compact = np.zeros((grid_h, grid_w, 2), dtype=np.float32)
        compact[..., 0] = np.where(valid, grid_flow[..., 0], 0.0)
        compact[..., 1] = np.where(valid, grid_flow[..., 1], 0.0)

        if not np.any(valid):
            return np.zeros((height, width, 2), dtype=np.float32)

        # CPU-like but fast: repair invalid grid cells on the compact grid, not
        # on the full tile. This avoids the old 64-pass full-resolution blur.
        valid_f = valid.astype(np.float32)
        for _ in range(3):
            missing = valid_f <= 0
            if not np.any(missing):
                break
            blurred_weight = cv2.blur(valid_f, (3, 3))
            can_fill = missing & (blurred_weight > 1e-6)
            if not np.any(can_fill):
                break
            for channel in (0, 1):
                blurred_flow = cv2.blur(compact[..., channel] * valid_f, (3, 3))
                compact[..., channel][can_fill] = (
                    blurred_flow[can_fill] / blurred_weight[can_fill]
                )
            valid_f[can_fill] = 1.0

        flow = cv2.resize(compact, (width, height), interpolation=cv2.INTER_NEAREST)
        return np.ascontiguousarray(flow, dtype=np.float32)
