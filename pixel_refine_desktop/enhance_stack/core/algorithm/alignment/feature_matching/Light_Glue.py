import gc
import json
import os
import queue
import subprocess
import sys
import threading
import traceback
import urllib.request
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

from config import ALGORITHM_PARAMETER_SETTINGS_FILE


os.environ["ORT_CUDA_MEM_LIMIT_MB"] = "1024"


DEFAULT_LIGHT_GLUE_CONFIG = {
    "transformation": "homography",
    "ransacThreshold": 5.0,
    "keep_edges": False,
    "enable_cropping": False,
    "save_align": False,
    "command_save_to_hd5f": True,
    "align_folder": os.path.join(
        os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image"
    ),
    "use_multi_core": True,
    "use_gpu": False,
    "model_input_size": 448,
    "match_confidence": 0.5,
    "min_matches_for_transform": 8,
}


def load_light_glue_config(config_filename=None):
    config = DEFAULT_LIGHT_GLUE_CONFIG.copy()
    config_filename = config_filename or ALGORITHM_PARAMETER_SETTINGS_FILE
    try:
        if os.path.exists(config_filename):
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            config.update(params.get("Light_Glue", {}))
    except Exception as exc:
        print(f"[LightGlueAlgorithm] Failed to load config: {exc}")
    return config


def is_frozen_app():
    return hasattr(sys, "frozen") or (
        hasattr(sys, "_MEIPASS")
        or (sys.executable.endswith(".exe") and sys.executable != sys.argv[0])
    )


def find_cudnn_dlls():
    dlls = []
    env_vars = ["CUDNN_PATH", "CUDA_PATH"] + [
        key for key in os.environ.keys() if key.startswith("CUDA_PATH_V")
    ]
    for var in env_vars:
        if var not in os.environ:
            continue
        path = Path(os.environ[var])
        if path.exists():
            for pattern in ("cudnn64_*.dll", "cublas64_*.dll", "cufft64_*.dll", "curand64_*.dll"):
                dlls.extend(path.rglob(pattern))

    for base in (
        Path("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA"),
        Path("C:/Program Files/NVIDIA"),
        Path("C:/tools/cuda"),
    ):
        if base.exists():
            for pattern in ("cudnn64_*.dll", "cublas64_*.dll", "cufft64_*.dll", "curand64_*.dll"):
                dlls.extend(base.rglob(pattern))

    if not dlls:
        try:
            result = subprocess.check_output(
                ["where", "cudnn64_*.dll"], shell=True, text=True
            ).strip()
            dlls.extend(Path(line.strip()) for line in result.splitlines() if line.strip())
        except Exception:
            pass

    dlls = list(dict.fromkeys(dll for dll in dlls if dll.exists()))
    cudnn_only = [dll for dll in dlls if "cudnn64_" in dll.name]
    if cudnn_only:
        cudnn_only.sort(key=lambda dll: int(dll.stem.split("cudnn64_")[-1]), reverse=True)
        highest_version = int(cudnn_only[0].stem.split("cudnn64_")[-1])
        dlls = [
            dll
            for dll in dlls
            if f"cudnn64_{highest_version}" in dll.name
            or not dll.name.startswith("cudnn64_")
        ]
    return dlls


def add_dll_to_path():
    if os.name != "nt":
        return
    for dll in find_cudnn_dlls():
        dll_dir = dll.parent
        os.add_dll_directory(str(dll_dir))
        os.environ["PATH"] = str(dll_dir) + os.pathsep + os.environ.get("PATH", "")


add_dll_to_path()


class LightGlueAlgorithm:
    NAME = "Light Glue"
    KIND = "alignment"
    DESCRIPTION = "LightGlue feature alignment adapter."

    def __init__(self):
        self.sess = None
        self.initialized = False
        self.init_thread = None
        self.stop_event = threading.Event()
        self.PIPELINE_ONNX = os.path.join(
            "database", "Learning_Model", "disk_lightglue_pipeline.ort.onnx"
        )
        self.MODEL_URL = (
            "https://github.com/fabio-sim/LightGlue-ONNX/releases/download/v2.0/"
            "disk_lightglue_pipeline.ort.onnx"
        )
        cv2.ocl.setUseOpenCL(True)

    @staticmethod
    def load_config(batch_id=None, config_filename=None):
        config = load_light_glue_config(config_filename)
        if batch_id is None:
            return config
        try:
            from pixel_refine_desktop.enhance_stack.core.logic import (
                batch_parameter_manager,
            )

            batch_params = batch_parameter_manager.load_json_state().get(str(batch_id), {})
            light_glue_params = batch_params.get("light_glue_params", {})
            if isinstance(light_glue_params, dict):
                config.update(light_glue_params)
        except Exception as exc:
            print(f"[LightGlueAlgorithm] Failed to load batch_id config: {exc}")
        return config

    @staticmethod
    def load_light_glue_config_for_batch_id(batch_id):
        return LightGlueAlgorithm.load_config(batch_id=batch_id)

    def _ensure_model_ready(self):
        if self.initialized and self.sess is not None:
            return
        if self.init_thread is None or not self.init_thread.is_alive():
            self.init_thread = threading.Thread(
                target=self._initialize_model_thread, daemon=True
            )
            self.init_thread.start()
        self.init_thread.join()

    def _initialize_model_thread(self):
        try:
            self._download_and_prepare_model()
            self._create_inference_session()
            self.initialized = self.sess is not None
        except Exception:
            traceback.print_exc()
            self.initialized = False
            self._cleanup_gpu()

    def _download_and_prepare_model(self):
        model_path = self.PIPELINE_ONNX
        model_url = self.MODEL_URL
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        if os.path.exists(model_path):
            local_size = os.path.getsize(model_path)
            total_size = 0
            try:
                request = urllib.request.Request(model_url, method="HEAD")
                with urllib.request.urlopen(request) as response:
                    total_size = int(response.getheader("Content-Length", 0))
            except Exception:
                total_size = 0

            if total_size > 0 and local_size < total_size:
                request = urllib.request.Request(model_url)
                request.add_header("Range", f"bytes={local_size}-")
                with urllib.request.urlopen(request) as response, open(model_path, "ab") as file:
                    while chunk := response.read(8192):
                        file.write(chunk)
            else:
                try:
                    ort.InferenceSession(model_path)
                    return
                except Exception:
                    os.remove(model_path)

        with urllib.request.urlopen(model_url) as response, open(model_path, "wb") as file:
            while chunk := response.read(8192):
                file.write(chunk)

    def _create_inference_session(self):
        config = load_light_glue_config()
        use_gpu = bool(config.get("use_gpu", False))
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        providers = ["CPUExecutionProvider"]
        if use_gpu:
            providers = [
                (
                    "CUDAExecutionProvider",
                    {
                        "device_id": 0,
                        "gpu_mem_limit": 1024 * 1024 * 1024,
                        "arena_extend_strategy": "kNextPowerOfTwo",
                    },
                ),
                "CPUExecutionProvider",
            ]

        try:
            self.sess = ort.InferenceSession(
                self.PIPELINE_ONNX,
                sess_options=sess_options,
                providers=providers,
            )
        except Exception as exc:
            if use_gpu:
                print(f"[LightGlueAlgorithm] GPU session failed, falling back to CPU: {exc}")
                self.sess = ort.InferenceSession(
                    self.PIPELINE_ONNX,
                    sess_options=sess_options,
                    providers=["CPUExecutionProvider"],
                )
            else:
                raise

    def _cleanup_gpu(self):
        try:
            if self.sess is not None:
                del self.sess
                self.sess = None
            gc.collect()
        except Exception as exc:
            print(f"[LightGlueAlgorithm] GPU cleanup failed: {exc}")

    @staticmethod
    def _resize_and_pad(image, target_size):
        height, width = image.shape[:2]
        scale = target_size / max(height, width)
        new_width = max(1, int(width * scale))
        new_height = max(1, int(height * scale))
        resized = cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_LINEAR_EXACT,
        )
        pad_top = (target_size - new_height) // 2
        pad_left = (target_size - new_width) // 2
        padded = cv2.copyMakeBorder(
            resized,
            pad_top,
            target_size - new_height - pad_top,
            pad_left,
            target_size - new_width - pad_left,
            cv2.BORDER_CONSTANT,
            value=0,
        )
        return padded, (width / new_width, height / new_height), (pad_left, pad_top)

    @classmethod
    def _prepare_model_input(cls, image, target_size):
        if image.ndim == 2:
            rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        padded, scale_factors, pad_offsets = cls._resize_and_pad(rgb, target_size)
        tensor = padded.astype(np.float32)[None, :, :, :].transpose(0, 3, 1, 2) / 255.0
        return tensor, scale_factors, pad_offsets

    @staticmethod
    def _restore_coords(points, pad_offsets, scale_factors):
        return (points - np.array(pad_offsets)) * np.array(scale_factors)

    @staticmethod
    def _deduplicate_matches(base_points, target_points, scores, image_shape):
        if len(base_points) == 0:
            return base_points, target_points
        height, width = image_shape[:2]
        seen = set()
        selected = []
        order = np.argsort(-scores)
        for idx in order:
            x, y = base_points[idx]
            if not (0 <= x < width and 0 <= y < height):
                continue
            key = (int(round(x)), int(round(y)))
            if key in seen:
                continue
            seen.add(key)
            selected.append(idx)
        if not selected:
            return np.empty((0, 2), dtype=np.float32), np.empty((0, 2), dtype=np.float32)
        selected = np.array(selected, dtype=np.int32)
        return base_points[selected], target_points[selected]

    def calculate_global_motion(self, base_image, target_image, config=None, stop_requested=None):
        if stop_requested and stop_requested():
            return None, None
        if base_image is None or target_image is None:
            return None, None

        config = config or self.load_config()
        self._ensure_model_ready()
        if self.sess is None:
            return None, None

        height_orig, width_orig = base_image.shape[:2]
        megapixels = (height_orig * width_orig) / 1_000_000.0
        grid_size = (1, 1)
        frame_scale = 1.0
        if megapixels > 22.0:
            frame_scale = (22.0 / megapixels) ** 0.5
            new_width = int(width_orig * frame_scale)
            new_height = int(height_orig * frame_scale)
            base_image = cv2.resize(base_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            target_image = cv2.resize(target_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            grid_size = (4, 4)
        elif 17.5 <= megapixels <= 22.0:
            grid_size = (3, 3)
        elif 11.5 <= megapixels <= 13.0:
            grid_size = (2, 2)

        target_size = int(config.get("model_input_size", 448))
        confidence = float(config.get("match_confidence", 0.5))
        min_matches = int(config.get("min_matches_for_transform", 8))
        overlap_percent = 0.10
        height, width = base_image.shape[:2]
        cols, rows = grid_size
        tile_w = max(1, width // cols)
        tile_h = max(1, height // rows)
        overlap_w = int(tile_w * overlap_percent)
        overlap_h = int(tile_h * overlap_percent)

        all_results = []
        for row in range(rows):
            for col in range(cols):
                if stop_requested and stop_requested():
                    return None, None
                x_start = max(0, col * tile_w - overlap_w)
                y_start = max(0, row * tile_h - overlap_h)
                x_end = min(width, (col + 1) * tile_w + overlap_w)
                y_end = min(height, (row + 1) * tile_h + overlap_h)
                base_tile = base_image[y_start:y_end, x_start:x_end]
                target_tile = target_image[y_start:y_end, x_start:x_end]

                img_l, scale_l, offset_l = self._prepare_model_input(base_tile, target_size)
                img_r, scale_r, offset_r = self._prepare_model_input(target_tile, target_size)
                batch = np.concatenate([img_l, img_r], axis=0).astype(np.float32)

                try:
                    input_name = self.sess.get_inputs()[0].name
                    keypoints_b, matches, scores = self.sess.run(None, {input_name: batch})
                except Exception as exc:
                    print(f"[LightGlueAlgorithm] ONNX inference failed: {exc}")
                    continue

                if keypoints_b is None or matches is None or scores is None:
                    continue
                matches = matches.astype(np.int32)
                batch_mask = matches[:, 0] == 0
                idx0 = matches[batch_mask, 1]
                idx1 = matches[batch_mask, 2]
                tile_scores = scores[batch_mask]
                conf_mask = tile_scores > confidence
                if np.sum(conf_mask) < min_matches:
                    continue

                idx0 = idx0[conf_mask]
                idx1 = idx1[conf_mask]
                tile_scores = tile_scores[conf_mask]
                base_padded = keypoints_b[0][idx0].astype(np.float32)
                target_padded = keypoints_b[1][idx1].astype(np.float32)
                base_local = self._restore_coords(base_padded, offset_l, scale_l)
                target_local = self._restore_coords(target_padded, offset_r, scale_r)
                global_offset = np.array([x_start, y_start], dtype=np.float32)
                all_results.append((base_local + global_offset, target_local + global_offset, tile_scores))

        if not all_results:
            return None, None

        base_points = np.vstack([item[0] for item in all_results])
        target_points = np.vstack([item[1] for item in all_results])
        scores = np.concatenate([item[2] for item in all_results])
        base_points, target_points = self._deduplicate_matches(
            base_points,
            target_points,
            scores,
            base_image.shape,
        )
        if len(base_points) < min_matches:
            return None, None
        if frame_scale != 1.0:
            base_points = base_points / frame_scale
            target_points = target_points / frame_scale

        print(f"[LightGlueAlgorithm] motion matches={len(base_points)}")
        return base_points.reshape(-1, 1, 2), target_points.reshape(-1, 1, 2)

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
            print(f"[LightGlueAlgorithm] stage1 motion index={offset} success={success}")
            if ctx.update_progress:
                ctx.update_progress(20 + int((offset / total_targets) * 35), f"LightGlue motion {offset}/{total_targets}")
            del frame
        return plan

    def run(self, ctx, frames, batch_plan=None):
        return list(frames)


def running_light_glue(*args, **kwargs):
    raise RuntimeError(
        "Light Glue is now orchestrated by MFDenoiser. Use MFDenoiser with alignment='Light Glue' instead."
    )
