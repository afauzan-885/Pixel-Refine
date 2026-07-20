import json
import os

import cv2
import numpy as np

from config import ALGORITHM_PARAMETER_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.lucas_kanade_gpu import (
    LucasKanadeGPU,
)


DEFAULT_RAFT_CONFIG = {
    "mode": "balance",
    "tile_overlap": 0.25,
    "execution_provider": "auto",
}

RAFT_PRESETS = {
    "fast": {
        "global_scale": 0.5,
        "tile_overlap": 0.25,
        "model_height": 360,
        "model_width": 480,
    },
    "balance": {
        "global_scale": 0.75,
        "tile_overlap": 0.25,
        "model_height": 360,
        "model_width": 480,
    },
    "high": {
        "global_scale": 1.0,
        "tile_overlap": 0.25,
        "model_height": 360,
        "model_width": 480,
    },
}


class RAFTFlow(LucasKanadeGPU):
    NAME = "RAFT Optical Flow"
    KIND = "alignment"
    DESCRIPTION = "ONNX RAFT optical flow alignment with dynamic 360x480 model tiles."

    def __init__(self):
        super().__init__()
        self._raft_session = None

    @staticmethod
    def load_config(batch_id=None, config_filename=None):
        visible_config = DEFAULT_RAFT_CONFIG.copy()
        config_filename = config_filename or ALGORITHM_PARAMETER_SETTINGS_FILE
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                section = params.get("RAFT", {})
                if isinstance(section, dict):
                    visible_config.update(section)
        except Exception as exc:
            print(f"[RAFTFlow] Failed to load config: {exc}")

        if batch_id is not None:
            try:
                from pixel_refine_desktop.enhance_stack.core.logic import (
                    batch_parameter_manager,
                )

                batch_params = batch_parameter_manager.load_json_state().get(
                    str(batch_id),
                    {},
                )
                section = batch_params.get("raft_params", {})
                if isinstance(section, dict):
                    visible_config.update(section)
            except Exception as exc:
                print(f"[RAFTFlow] Failed to load batch config: {exc}")
        return RAFTFlow._resolve_mode_config(visible_config)

    @staticmethod
    def _normalize_mode(mode):
        value = str(mode or "balance").strip().lower()
        if value in ("balanced", "normal", "medium"):
            return "balance"
        if value not in RAFT_PRESETS:
            return "balance"
        return value

    @staticmethod
    def _resolve_mode_config(config):
        mode = RAFTFlow._normalize_mode(config.get("mode", "balance"))
        resolved = RAFT_PRESETS[mode].copy()
        resolved.update({k: v for k, v in config.items() if k != "mode"})
        resolved["mode"] = mode
        return resolved

    @staticmethod
    def load_raft_config(config_filename=None):
        return RAFTFlow.load_config(config_filename=config_filename)

    @staticmethod
    def load_raft_config_for_batch(config_filename=None):
        return RAFTFlow.load_config(config_filename=config_filename)

    def _get_session(self, provider_preference=None):
        if self._raft_session is None:
            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.alignment_core import (
                FLOW_MODEL_PATH,
                ONNXSessionManager,
            )

            self._raft_session = ONNXSessionManager(
                FLOW_MODEL_PATH,
                provider_preference=provider_preference,
            ).__enter__()
        return self._raft_session

    def _reset_session(self, provider_preference=None):
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.alignment_core import (
            FLOW_MODEL_PATH,
            ONNXSessionManager,
        )

        self._raft_session = None
        self._raft_session = ONNXSessionManager(
            FLOW_MODEL_PATH,
            provider_preference=provider_preference,
        ).__enter__()
        return self._raft_session

    @staticmethod
    def _uses_directml(session):
        try:
            return "DmlExecutionProvider" in session.get_providers()
        except Exception:
            return False

    @staticmethod
    def _to_raft_uint8(image):
        arr = np.asarray(image)
        if arr.ndim == 2:
            arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
        elif arr.shape[2] == 4:
            arr = arr[:, :, :3]

        if arr.dtype == np.uint8:
            return np.ascontiguousarray(arr)
        if np.issubdtype(arr.dtype, np.floating):
            scale = 255.0 if float(np.nanmax(arr)) <= 1.5 else 1.0
            return np.ascontiguousarray(np.clip(arr * scale, 0, 255).astype(np.uint8))
        if np.issubdtype(arr.dtype, np.integer):
            info = np.iinfo(arr.dtype)
            scale = 255.0 / float(max(1, info.max))
            return np.ascontiguousarray(np.clip(arr.astype(np.float32) * scale, 0, 255).astype(np.uint8))
        return np.ascontiguousarray(np.clip(arr, 0, 255).astype(np.uint8))

    @staticmethod
    def _restore_output_dtype(image, dtype):
        if np.issubdtype(dtype, np.integer):
            info = np.iinfo(dtype)
            if image.dtype.kind == "f" and float(np.nanmax(image)) <= 1.5:
                image = image * float(info.max)
            image = np.clip(image, info.min, info.max)
        return image.astype(dtype, copy=False)

    @staticmethod
    def _warp_with_flow_cpu(image, flow):
        h, w = image.shape[:2]
        y_coords, x_coords = np.mgrid[0:h, 0:w].astype(np.float32)
        map_x = x_coords + flow[:, :, 0]
        map_y = y_coords + flow[:, :, 1]
        return cv2.remap(
            image,
            map_x,
            map_y,
            interpolation=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REFLECT_101,
        )

    def _calculate_global_raft_flow(self, reference, target, config, stop_requested=None):
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.alignment_core import (
            compute_flow_raft,
            scale_flow_to_full_res,
        )

        model_h = max(16, int(config.get("model_height", 360)))
        model_w = max(16, int(config.get("model_width", 480)))
        overlap = max(0.0, min(float(config.get("tile_overlap", 0.25)), 0.45))
        global_scale = max(0.1, min(float(config.get("global_scale", 0.75)), 1.0))
        provider_mode = str(config.get("execution_provider", "auto")).strip().lower()
        provider_preference = (
            ["CPUExecutionProvider"] if provider_mode == "cpu" else None
        )
        session = self._get_session(provider_preference=provider_preference)

        ref_u8 = self._to_raft_uint8(reference)
        target_u8 = self._to_raft_uint8(target)
        full_h, full_w = ref_u8.shape[:2]

        if global_scale < 0.999:
            scaled_w = max(model_w, int(round(full_w * global_scale)))
            scaled_h = max(model_h, int(round(full_h * global_scale)))
            ref_work = cv2.resize(
                ref_u8,
                (scaled_w, scaled_h),
                interpolation=cv2.INTER_AREA,
            )
            target_work = cv2.resize(
                target_u8,
                (scaled_w, scaled_h),
                interpolation=cv2.INTER_AREA,
            )
        else:
            ref_work = ref_u8
            target_work = target_u8
            scaled_h, scaled_w = full_h, full_w

        grid_rows = max(1, int(np.ceil(scaled_h / float(model_h))))
        grid_cols = max(1, int(np.ceil(scaled_w / float(model_w))))
        print(
            "[RAFTFlow] "
            f"global_scale={global_scale:.2f} work={scaled_w}x{scaled_h} "
            f"model_tile={model_w}x{model_h} grid={grid_cols}x{grid_rows} "
            f"overlap={overlap:.2f}"
        )

        def run_flow(active_session):
            return compute_flow_raft(
                ref_work,
                target_work,
                active_session,
                grid_rows=grid_rows,
                grid_cols=grid_cols,
                model_input_size=(model_h, model_w),
                overlap_ratio=overlap,
                stop_requested=stop_requested,
            )

        flow_work = run_flow(session)
        if flow_work is None and self._uses_directml(session):
            print(
                "[RAFTFlow] DirectML RAFT failed or device was suspended; retrying once on CPU."
            )
            cpu_session = self._reset_session(["CPUExecutionProvider"])
            flow_work = run_flow(cpu_session)
        if flow_work is None:
            return None

        if (scaled_h, scaled_w) != (full_h, full_w):
            flow_full = scale_flow_to_full_res(
                flow_work,
                scaled_h,
                scaled_w,
                full_h,
                full_w,
            )
        else:
            flow_full = flow_work
        return np.ascontiguousarray(flow_full, dtype=np.float32)

    def calculate_flow(self, reference_gray, target_gray, config, point_executor=None):
        flow = self._calculate_global_raft_flow(reference_gray, target_gray, config)
        if flow is None:
            return np.zeros((*reference_gray.shape[:2], 2), dtype=np.float32)
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
        if reference is None or target is None:
            return None
        config = config or self.load_config()
        flow = self._calculate_global_raft_flow(
            reference,
            target,
            config,
            stop_requested=stop_requested,
        )
        if flow is None:
            return None

        try:
            from taichi_library import taichi_aot

            target_gpu = taichi_aot.upload(
                target.astype(np.float32, copy=False),
                is_vector=target.ndim == 3,
            )
            full_h, full_w = target.shape[:2]
            warped_gpu = taichi_aot.remap_with_flow(
                target_gpu,
                flow,
                full_h,
                full_w,
                return_gpu=True,
            )
            taichi_aot.engine.sync()
            warped = warped_gpu.to_numpy()
            return self._restore_output_dtype(warped, target.dtype)
        except Exception as exc:
            print(f"[RAFTFlow] GPU remap failed, falling back to CPU remap: {exc}")
            warped = self._warp_with_flow_cpu(target, flow)
            return self._restore_output_dtype(warped, target.dtype)
