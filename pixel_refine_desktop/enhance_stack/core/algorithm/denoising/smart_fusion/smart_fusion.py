"""Smart Fusion denoising adapter using AI weight maps from ONNX.

This adapter processes aligned HDF5 frames in tiles using an ONNX weight-map model,
performing robust stacking fusion to eliminate noise while preventing ghosting.
"""

import os
import h5py
import numpy as np
import onnxruntime as ort
from pathlib import Path
from taichi_library.backend_config import normalize_backend
from ...shared_utils import (
    resolve_batch_config,
    restore_output_dtype as _restore_output_dtype,
    sorted_image_keys as _sorted_image_keys,
)


_SESSION_CACHE = {}


def get_tile_window(h, w, overlap):
    def axis_window(length, edge):
        length = int(length)
        edge = max(0, min(int(edge), max(0, length // 2)))
        weights = np.ones(length, dtype=np.float32)
        if edge <= 0 or length <= 1:
            return weights

        hann = np.hanning(edge * 2).astype(np.float32)
        weights[:edge] = np.maximum(hann[:edge], 1e-4)
        weights[-edge:] = np.maximum(hann[-edge:], 1e-4)
        return weights

    win_y = axis_window(h, overlap)
    win_x = axis_window(w, overlap)
    win = np.outer(win_y, win_x)
    return np.expand_dims(win, axis=-1)


def resolve_smart_fusion_backend():
    """Resolves execution providers and target hardware mode (cpu or gpu) directly from app_setting.json."""
    arch = "cpu"
    try:
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.backend_arch_helper import (
            get_backend_arch,
        )

        arch = str(get_backend_arch()).lower()
    except Exception:
        arch = normalize_backend(
            os.environ.get("AOT_ARCH", "cpu"),
            allow_auto=True,
        )
        if arch == "auto":
            arch = "cpu"

    setting_path = ""
    try:
        from config import GENERAL_SETTINGS_FILE

        setting_path = GENERAL_SETTINGS_FILE
    except ImportError:
        pass

    if not setting_path or not os.path.exists(setting_path):
        root = os.path.dirname(os.path.abspath(__file__))
        for _ in range(8):
            candidate = os.path.join(root, "database", "setting", "app_setting.json")
            if os.path.exists(candidate):
                setting_path = candidate
                break
            root = os.path.dirname(root)

    backend_key = arch
    vendor = ""
    if setting_path and os.path.exists(setting_path):
        try:
            with open(setting_path, "r", encoding="utf-8") as fh:
                import json

                data = json.load(fh)
            backend_key = str(data.get("device_backend_key", arch)).lower()
            backend_arch = str(data.get("device_backend_arch", arch)).lower()
            if backend_arch:
                arch = backend_arch
            selector = data.get("device_selector", {})
            if isinstance(selector, dict):
                vendor = str(selector.get("vendor", "")).lower()
        except Exception:
            pass

    available = ort.get_available_providers()

    if arch == "cpu" or backend_key == "cpu" or vendor == "cpu":
        return ["CPUExecutionProvider"], "cpu"

    if "nvidia" in backend_key or "nvidia" in vendor or "cuda" in arch:
        providers = [
            p
            for p in [
                "CUDAExecutionProvider",
                "DmlExecutionProvider",
                "CPUExecutionProvider",
            ]
            if p in available
        ]
        return (
            (providers, "gpu")
            if len(providers) > 1 or providers[0] != "CPUExecutionProvider"
            else (providers, "cpu")
        )

    providers = [
        p for p in ["DmlExecutionProvider", "CPUExecutionProvider"] if p in available
    ]
    return (
        (providers, "gpu")
        if len(providers) > 1 or providers[0] != "CPUExecutionProvider"
        else (providers, "cpu")
    )


class SmartFusionDenoisingAlgorithm:
    NAME = "Smart Fusion"
    KIND = "denoising"
    DESCRIPTION = "AI-powered robust Smart Fusion on CPU/GPU using ONNX weight maps."

    @staticmethod
    def load_config():
        try:
            from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.similarity_parameter_settings import (
                load_similarity_config,
            )

            return load_similarity_config()
        except (ImportError, Exception):
            return {
                "work_resolution_scale": 1.0,
                "ai_tile_size": 1024,
                "ai_overlap_percent": 0.10,
                "ai_batch_size": 4,
                "ai_model_type": "nano fusion v1",
            }

    def _resolve_config(self, ctx):
        return resolve_batch_config(ctx, self.load_config)

    def run(self, ctx, frames, batch_plan=None):
        config = self._resolve_config(ctx)

        # 1. Read scale and tile parameters
        scale = float(config.get("work_resolution_scale", 1.0))
        tile_size = int(config.get("ai_tile_size", 1024))
        overlap_percent = float(config.get("ai_overlap_percent", 0.10))
        overlap = int(tile_size * overlap_percent)
        overlap = max(0, min(overlap, tile_size // 2 - 1))
        batch_size = int(config.get("ai_batch_size", 4))

        # Resolve execution providers and hardware target from app_setting.json
        providers, target_device = resolve_smart_fusion_backend()

        model_type = str(config.get("ai_model_type", "nano fusion v1")).strip().lower()
        if model_type in ("fusion v1", "smart fusion"):
            model_subfolder = "regular"
            file_prefix = "regular_v2_hanning_weightmap"
        else:
            model_subfolder = "nano"
            file_prefix = "nano_v2_hanning_weightmap"

        model_dir = (
            Path("database") / "Learning_Model" / "smart_fusion" / model_subfolder
        )

        model_suffix = "cpu" if target_device == "cpu" else "gpu"
        model_name = (
            f"{file_prefix}_{tile_size}x{tile_size}_fp32_ort_{model_suffix}.onnx"
        )

        onnx_path = model_dir / model_name
        if not onnx_path.exists():
            print(
                f"[SmartFusion] Warning: {onnx_path} not found. Falling back to default CPU model."
            )
            onnx_path = (
                model_dir / f"{file_prefix}_{tile_size}x{tile_size}_fp32_ort_cpu.onnx"
            )
            providers = ["CPUExecutionProvider"]
            if not onnx_path.exists():
                # Fallback to 1024 if the requested block size model doesn't exist
                tile_size = 1024
                onnx_path = model_dir / f"{file_prefix}_1024x1024_fp32_ort_cpu.onnx"
                providers = ["CPUExecutionProvider"]

        global _SESSION_CACHE
        cache_key = (str(onnx_path), tuple(providers))
        if cache_key in _SESSION_CACHE:
            session = _SESSION_CACHE[cache_key]
            print(f"[SmartFusion] Reusing cached ONNX session for {onnx_path}")
        else:
            print(
                f"[SmartFusion] Loading ONNX model from: {onnx_path} with providers={providers}"
            )
            options = ort.SessionOptions()
            options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            session = ort.InferenceSession(
                str(onnx_path), sess_options=options, providers=providers
            )
            _SESSION_CACHE[cache_key] = session

        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            normalize_image,
        )
        import cv2

        use_hdf5 = bool(ctx.hdf5_path) and os.path.exists(ctx.hdf5_path)

        if use_hdf5:
            with h5py.File(ctx.hdf5_path, "r") as h5f:
                image_keys = _sorted_image_keys(h5f)
                if not image_keys:
                    print("[SmartFusion] no aligned images in HDF5.")
                    return None

                reference_raw = h5f[image_keys[0]][:]
                orig_h, orig_w = reference_raw.shape[:2]
                ref_dtype = getattr(ctx, "ref_dtype", reference_raw.dtype)

                # Load and normalize only reference frame
                reference_normalized = normalize_image(reference_raw, ref_dtype)
                del reference_raw
                total_frames = len(image_keys)
        else:
            if not frames:
                print(
                    "[SmartFusion] aligned HDF5 and in-memory frames are both unavailable."
                )
                return None
            reference_raw = frames[0]
            orig_h, orig_w = reference_raw.shape[:2]
            ref_dtype = getattr(ctx, "ref_dtype", reference_raw.dtype)
            reference_normalized = normalize_image(reference_raw, ref_dtype)
            total_frames = len(frames)

        reference_full = reference_normalized

        # Tone mapping is used only as a visibility/preprocessing transform for
        # the AI weight-map model. The original normalized frame remains the
        # only source used by the final fusion accumulator below.
        try:
            from taichi_library.taichi_aot import naturalTonemapping
            from config import CALCULATION_TONE_MAPPING_PARAMS

            reference_weight_source = naturalTonemapping(
                reference_full, return_gpu=False, **CALCULATION_TONE_MAPPING_PARAMS
            )
            print(
                "[SmartFusion] naturalTonemapping enabled for weight-map inference; "
                "original pixels retained for fusion"
            )
        except Exception as exc:
            print(
                f"[SmartFusion] Tone mapping unavailable for weight maps, "
                f"using original frames: {exc}"
            )
            reference_weight_source = reference_full

        # Prepare work scale only for luma/weight-map inference. Pixel fusion stays
        # in original resolution to preserve aligned RAW detail.
        if abs(scale - 1.0) > 1e-3:
            target_w = int(orig_w * scale)
            target_h = int(orig_h * scale)
            target_w = max(4, target_w)
            target_h = max(4, target_h)
            print(
                f"[SmartFusion] Weight-map work scale: {orig_w}x{orig_h} -> {target_w}x{target_h} (scale={scale})"
            )
            reference_work = cv2.resize(
                reference_weight_source,
                (target_w, target_h),
                interpolation=cv2.INTER_LINEAR,
            )
            ref_h, ref_w = target_h, target_w
        else:
            reference_work = reference_weight_source
            ref_h, ref_w = orig_h, orig_w

        # Dynamically detect ONNX model input node names and expected channel count
        inputs_meta = session.get_inputs()
        ref_input_name = (
            inputs_meta[0].name if len(inputs_meta) > 0 else "reference_luma"
        )
        curr_input_name = (
            inputs_meta[1].name if len(inputs_meta) > 1 else "current_luma"
        )

        first_shape = inputs_meta[0].shape if len(inputs_meta) > 0 else []
        is_rgb_model = False
        if len(first_shape) == 4:
            if (
                first_shape[1] == 3
                or first_shape[-1] == 3
                or "rgb" in ref_input_name.lower()
            ):
                is_rgb_model = True
        elif "rgb" in ref_input_name.lower():
            is_rgb_model = True

        if is_rgb_model:
            ref_feat_full = reference_work  # RGB (H, W, 3)
        else:
            # Compute luma map for 1-channel model
            ref_feat_full = (
                0.299 * reference_work[:, :, 0]
                + 0.587 * reference_work[:, :, 1]
                + 0.114 * reference_work[:, :, 2]
            )

        # Tiling parameters
        step = tile_size - overlap

        print(
            f"[SmartFusion] Weight maps: {ref_w}x{ref_h} in {tile_size}x{tile_size} tiles, "
            f"overlap={overlap}px, batch_size={batch_size}, format={'RGB (3-ch)' if is_rgb_model else 'Luma (1-ch)'}"
        )

        # 1. Collect all tile coordinates to process
        tiles_to_process = []
        for y in range(0, ref_h, step):
            for x in range(0, ref_w, step):
                h_tile = min(tile_size, ref_h - y)
                w_tile = min(tile_size, ref_w - x)
                if h_tile < 4 or w_tile < 4:
                    continue
                tiles_to_process.append((y, x, h_tile, w_tile))

        # Handle Full Frame batch size (value >= 16)
        if batch_size >= 16:
            batch_size = max(1, len(tiles_to_process))

        # Final fusion accumulators stay at original resolution. The reference
        # contributes with weight 1.0, then every support frame contributes via
        # an upscaled global weight map.
        accum_final_img = reference_full.copy()
        accum_final_weight = np.ones((orig_h, orig_w, 1), dtype=np.float32)

        # 2. Process each target frame frame-by-frame streamingly
        for frame_idx in range(1, total_frames):
            if ctx.update_progress:
                from pixel_refine_desktop.ui.views.settings.General.Language import (
                    language_config,
                )

                msg = getattr(
                    language_config, "PROGRESS_MERGING", "Merging: {}/{}"
                ).format(frame_idx, total_frames - 1)
                ctx.update_progress(
                    60 + int((frame_idx / total_frames) * 30),
                    msg,
                )

            # Load frame
            if use_hdf5:
                with h5py.File(ctx.hdf5_path, "r") as h5f:
                    frame_raw = h5f[image_keys[frame_idx]][:]
            else:
                frame_raw = frames[frame_idx]

            # Normalize
            frame_normalized = normalize_image(frame_raw, ref_dtype)

            # Resize only for weight-map inference. Keep frame_normalized
            # untouched for the final original-resolution fusion.
            try:
                from config import CALCULATION_TONE_MAPPING_PARAMS

                frame_weight_source = naturalTonemapping(
                    frame_normalized,
                    return_gpu=False,
                    **CALCULATION_TONE_MAPPING_PARAMS,
                )
            except Exception as exc:
                print(
                    f"[SmartFusion] Tone mapping failed for frame {frame_idx}; "
                    f"using original frame for weight map: {exc}"
                )
                frame_weight_source = frame_normalized
            if abs(scale - 1.0) > 1e-3:
                frame_work = cv2.resize(
                    frame_weight_source,
                    (target_w, target_h),
                    interpolation=cv2.INTER_LINEAR,
                )
            else:
                frame_work = frame_weight_source

            if is_rgb_model:
                curr_feat_full = frame_work  # RGB (H, W, 3)
            else:
                # Compute luma for current frame
                curr_feat_full = (
                    0.299 * frame_work[:, :, 0]
                    + 0.587 * frame_work[:, :, 1]
                    + 0.114 * frame_work[:, :, 2]
                )

            weight_work_sum = np.zeros((ref_h, ref_w), dtype=np.float32)
            weight_work_norm = np.zeros((ref_h, ref_w), dtype=np.float32)

            # Process tiles in chunks of size 'batch_size'
            for i in range(0, len(tiles_to_process), batch_size):
                chunk = tiles_to_process[i : i + batch_size]
                ref_batch = []
                curr_batch = []

                for y, x, h_tile, w_tile in chunk:
                    if is_rgb_model:
                        ref_tile = ref_feat_full[y : y + h_tile, x : x + w_tile, :]
                        curr_tile = curr_feat_full[y : y + h_tile, x : x + w_tile, :]
                        pad_h = tile_size - h_tile
                        pad_w = tile_size - w_tile
                        if pad_h > 0 or pad_w > 0:
                            ref_tile_pad = np.pad(
                                ref_tile, ((0, pad_h), (0, pad_w), (0, 0)), mode="edge"
                            )
                            curr_tile_pad = np.pad(
                                curr_tile, ((0, pad_h), (0, pad_w), (0, 0)), mode="edge"
                            )
                        else:
                            ref_tile_pad = ref_tile
                            curr_tile_pad = curr_tile
                        # Transpose to NCHW [3, H, W] if needed
                        if len(first_shape) == 4 and first_shape[1] == 3:
                            ref_tile_in = np.transpose(ref_tile_pad, (2, 0, 1))
                            curr_tile_in = np.transpose(curr_tile_pad, (2, 0, 1))
                        else:
                            ref_tile_in = ref_tile_pad
                            curr_tile_in = curr_tile_pad
                    else:
                        ref_tile = ref_feat_full[y : y + h_tile, x : x + w_tile]
                        curr_tile = curr_feat_full[y : y + h_tile, x : x + w_tile]
                        pad_h = tile_size - h_tile
                        pad_w = tile_size - w_tile
                        if pad_h > 0 or pad_w > 0:
                            ref_tile_pad = np.pad(
                                ref_tile, ((0, pad_h), (0, pad_w)), mode="edge"
                            )
                            curr_tile_pad = np.pad(
                                curr_tile, ((0, pad_h), (0, pad_w)), mode="edge"
                            )
                        else:
                            ref_tile_pad = ref_tile
                            curr_tile_pad = curr_tile
                        ref_tile_in = np.expand_dims(ref_tile_pad, axis=0)  # [1, H, W]
                        curr_tile_in = np.expand_dims(
                            curr_tile_pad, axis=0
                        )  # [1, H, W]

                    ref_batch.append(ref_tile_in)
                    curr_batch.append(curr_tile_in)

                # Stack along batch axis -> [B, C, H, W] or [B, H, W, C]
                ref_tensor = np.array(ref_batch, dtype=np.float32)
                curr_tensor = np.array(curr_batch, dtype=np.float32)
                if not is_rgb_model and ref_tensor.ndim == 3:
                    ref_tensor = np.expand_dims(ref_tensor, axis=1)
                    curr_tensor = np.expand_dims(curr_tensor, axis=1)

                # Execute ONNX session run with dynamic node names
                output_names = [o.name for o in session.get_outputs()]
                outputs = session.run(
                    output_names,
                    {
                        ref_input_name: ref_tensor,
                        curr_input_name: curr_tensor,
                    },
                )
                out_weights = outputs[0]

                # De-batch, crop padded outputs, and accumulate directly
                for j, (y, x, h_tile, w_tile) in enumerate(chunk):
                    if out_weights.ndim == 4:
                        weight_map_pad = out_weights[j, 0, :, :]
                    else:
                        weight_map_pad = out_weights[j, :, :]
                    pad_h = tile_size - h_tile
                    pad_w = tile_size - w_tile
                    if pad_h > 0 or pad_w > 0:
                        weight_map = weight_map_pad[:h_tile, :w_tile]
                    else:
                        weight_map = weight_map_pad

                    win = get_tile_window(h_tile, w_tile, overlap)[:, :, 0]
                    weight_work_sum[y : y + h_tile, x : x + w_tile] += weight_map * win
                    weight_work_norm[y : y + h_tile, x : x + w_tile] += win

            weight_work_norm = np.maximum(weight_work_norm, 1e-12)
            weight_work = weight_work_sum / weight_work_norm
            if (ref_h, ref_w) != (orig_h, orig_w):
                weight_full = cv2.resize(
                    weight_work,
                    (orig_w, orig_h),
                    interpolation=cv2.INTER_LINEAR,
                )
            else:
                weight_full = weight_work

            weight_full = np.expand_dims(
                np.ascontiguousarray(weight_full, dtype=np.float32),
                axis=-1,
            )
            accum_final_img += weight_full * frame_normalized
            accum_final_weight += weight_full

            # Cleanup this frame's work pixels and feature to reclaim memory immediately
            del frame_work
            del frame_weight_source
            del frame_normalized
            del curr_feat_full
            del weight_work_sum
            del weight_work_norm
            del weight_work
            del weight_full
            import gc

            gc.collect()

        # Cleanup reference work image
        del reference_work
        del reference_weight_source
        del ref_feat_full
        import gc

        gc.collect()

        # 3. Finalize original-resolution fusion
        accum_final_weight = np.maximum(accum_final_weight, 1e-12)
        result = accum_final_img / accum_final_weight

        # Restore original data type
        result = _restore_output_dtype(result, ref_dtype)
        print(
            f"[SmartFusion] Finished fusion successfully. Result shape={result.shape}"
        )
        return result
