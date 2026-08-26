import gc
import os
import threading
from contextlib import contextmanager
from pathlib import Path

import cv2
import h5py
import numpy as np
from PIL import Image

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.weightnet_engine.flownet_inference import (
    AOTOpticalFlowAligner,
    align_support_frame,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.weightnet_engine.weightnet_inference import (
    DEFAULT_WEIGHTNET_ONNX,
    RAW_EXTENSIONS,
    fuse_support_frame_inplace,
    infer_single_support_weight_map,
    load_rgb_linear_image,
    load_weightnet_onnx,
    run_weightnet_inference,
)


class FusionNetDenoisingAlgorithm:
    """WeightNet ONNX-based deep multi-frame fusion denoising adapter with compute_flow.tcm AOT alignment."""

    NAME = "FusionNet"
    KIND = "denoising"
    DESCRIPTION = "Deep learning multi-frame burst fusion with compute_flow.tcm AOT alignment and WeightNet 512."

    @staticmethod
    def _sorted_image_keys(h5f):
        return sorted(
            (key for key in h5f.keys() if key.startswith("image_")),
            key=lambda item: int(item.split("_", 1)[1]),
        )

    def _load_inputs(self, ctx, frames):
        """Return a concrete frame list from HDF5 or memory, or path list."""
        use_hdf5 = bool(getattr(ctx, "hdf5_path", None)) and os.path.exists(
            ctx.hdf5_path
        )
        if use_hdf5:
            with h5py.File(ctx.hdf5_path, "r") as h5f:
                keys = self._sorted_image_keys(h5f)
                return [h5f[key][:] for key in keys], "hdf5"
        if frames:
            return list(frames), "memory"
        if getattr(ctx, "image_paths", None):
            return list(ctx.image_paths), "paths"
        return [], "none"

    def run(self, ctx, frames, batch_plan=None):
        """
        Execute FlowNet 512 streaming alignment followed by WeightNet 512 ONNX fusion.
        """
        inputs, source = self._load_inputs(ctx, frames)
        if not inputs:
            print("[FusionNet] No input images/frames available.")
            return None

        # Resolve parameters
        params_cfg = getattr(ctx, "params", {}) or {}
        work_scale = float(params_cfg.get("work_scale", 0.50))
        tile_size = int(
            params_cfg.get(
                "fusionnet_tile_size", params_cfg.get("weightnet_tile_size", 512)
            )
        )
        if tile_size < 512:
            tile_size = 512
        overlap = float(params_cfg.get("tile_overlap", params_cfg.get("overlap", 0.30)))

        # Detect RAW mode
        is_raw = bool(getattr(ctx, "is_linear_mode", False))
        if not is_raw and getattr(ctx, "image_paths", None):
            is_raw = any(
                Path(p).suffix.lower() in RAW_EXTENSIONS for p in ctx.image_paths
            )

        print(
            f"[FusionNet] Starting FlowNet 512 + WeightNet 512 pipeline: "
            f"source={source} frames={len(inputs)} is_raw={is_raw} "
            f"tile_size={tile_size} work_scale={work_scale}"
        )

        update_prog = getattr(ctx, "update_progress", None)
        stop_req = getattr(ctx, "stop_requested", None)

        stop_ev = None
        if stop_req is not None:
            stop_ev = threading.Event()
            if callable(stop_req) and stop_req():
                return None

        # Helper to convert array to float32 [0, 1]
        def _to_f32(img):
            img_arr = np.asarray(img)
            if np.issubdtype(img_arr.dtype, np.integer):
                scale = 65535.0 if img_arr.dtype.itemsize > 1 else 255.0
                return np.ascontiguousarray(
                    img_arr.astype(np.float32) / scale, dtype=np.float32
                )
            elif np.issubdtype(img_arr.dtype, np.floating):
                max_v = float(np.max(img_arr)) if img_arr.size > 0 else 1.0
                if max_v > 1.5:
                    scale = 65535.0 if max_v > 255.0 else 255.0
                    return np.ascontiguousarray(
                        img_arr.astype(np.float32) / scale, dtype=np.float32
                    )
                return np.ascontiguousarray(
                    img_arr.astype(np.float32, copy=False), dtype=np.float32
                )
            return np.ascontiguousarray(img_arr.astype(np.float32), dtype=np.float32)

        # -------------------------------------------------------------
        # STEP 1: Process Reference Linear Frame (Anchor) & AutoEnhance Analysis
        # -------------------------------------------------------------
        if update_prog:
            update_prog(2, "Loading reference linear frame...")

        if source == "paths":
            ref_linear = load_rgb_linear_image(inputs[0])
        else:
            ref_linear = _to_f32(inputs[0])
            inputs[0] = None

        target_h, target_w = ref_linear.shape[:2]
        ref_linear = np.ascontiguousarray(ref_linear, dtype=np.float32)

        # Analyze AutoEnhance params from reference anchor once
        auto_params = None
        if is_raw:
            from taichi_vision import taichi_aot

            auto_params = taichi_aot.analyze_auto_enhance_params(ref_linear)
            print(
                f"[FusionNet AutoEnhance] Analyzed linear ref -> "
                f"gain={auto_params['gain']:.4f}, white={auto_params['white_level']:.4f}, "
                f"shadow={auto_params['shadow_lift']:.4f}, contrast={auto_params['global_contrast']:.2f}"
            )
            ref_enhanced = np.ascontiguousarray(
                taichi_aot.AutoEnhance(ref_linear, params=auto_params), dtype=np.float32
            )
        else:
            ref_enhanced = ref_linear

        # Store aligned frames in compact uint16 (75MB per frame) to minimize RAM
        ref_u16 = np.ascontiguousarray(
            np.clip(ref_enhanced * 65535.0 + 0.5, 0.0, 65535.0).astype(np.uint16)
        )
        aligned_burst_u16 = [ref_u16]
        del ref_enhanced

        # -------------------------------------------------------------
        # STEP 2: Persistent AOT Optical Flow Alignment & Direct AutoEnhance
        # -------------------------------------------------------------
        total_supp = len(inputs) - 1

        if total_supp > 0:
            with AOTOpticalFlowAligner(
                ref_linear,
                work_scale=work_scale,
                tile_size=16,
            ) as aligner:
                del ref_linear
                gc.collect()

                for idx, item in enumerate(inputs[1:], start=1):
                    if stop_ev and stop_ev.is_set():
                        return None

                    supp_name = Path(item).name if source == "paths" else f"frame_{idx}"
                    if update_prog:
                        base_p = 5 + int((idx - 1) / total_supp * 40)
                        update_prog(
                            base_p,
                            f"Taichi AOT optical flow alignment for {supp_name} ({idx}/{total_supp})...",
                        )

                    # 1. Load support frame
                    if source == "paths":
                        supp_linear = load_rgb_linear_image(item)
                    else:
                        supp_linear = _to_f32(item)
                        inputs[idx] = None

                    # 2. Resize support if necessary
                    if supp_linear.shape[:2] != (target_h, target_w):
                        from taichi_vision import taichi_aot

                        supp_linear = taichi_aot.resize(
                            supp_linear,
                            (target_w, target_h),
                            interpolation=taichi_aot.INTER_LINEAR,
                        )
                    supp_linear = np.ascontiguousarray(supp_linear, dtype=np.float32)

                    # 3. GPU Optical Flow Alignment (compute_flow.tcm)
                    supp_aligned = aligner.align_frame(
                        supp_linear,
                        stop_event=stop_ev,
                    )
                    del supp_linear

                    # 4. Direct AutoEnhance
                    if is_raw and auto_params is not None:
                        from taichi_vision import taichi_aot

                        supp_enhanced = np.ascontiguousarray(
                            taichi_aot.AutoEnhance(supp_aligned, params=auto_params),
                            dtype=np.float32,
                        )
                        del supp_aligned
                    else:
                        supp_enhanced = supp_aligned

                    # Compact uint16 store
                    supp_u16 = np.ascontiguousarray(
                        np.clip(supp_enhanced * 65535.0 + 0.5, 0.0, 65535.0).astype(np.uint16)
                    )
                    del supp_enhanced
                    aligned_burst_u16.append(supp_u16)
                    gc.collect()

        else:
            del ref_linear
            gc.collect()

        # -------------------------------------------------------------
        # STEP 3: Streaming Pair-by-Pair WeightNet Fusion & Accumulation
        # -------------------------------------------------------------
        from taichi_vision import taichi_aot

        if update_prog:
            update_prog(48, "Loading FusionNet ONNX model & preparing fusion...")

        session = load_weightnet_onnx(
            DEFAULT_WEIGHTNET_ONNX, runtime="dml", patch_size=tile_size
        )
        ghost_pen = 1.30 if is_raw else 1.0
        ghost_cut = 0.05 if is_raw else 0.0

        # Work Resolution Downscale for WeightNet
        work_scale = float(work_scale)
        work_h = max(1, int(target_h * work_scale))
        work_w = max(1, int(target_w * work_scale))

        import cv2

        # Convert Reference to Float32 CHW
        ref_f32_hwc = aligned_burst_u16[0].astype(np.float32) / 65535.0
        ref_full_chw = np.ascontiguousarray(
            np.transpose(ref_f32_hwc, (2, 0, 1)), dtype=np.float32
        )
        sum_img = ref_full_chw.copy()
        weight_sum = np.ones((3, target_h, target_w), dtype=np.float32)

        if (work_h, work_w) != (target_h, target_w):
            ref_work_hwc = cv2.resize(
                ref_f32_hwc, (work_w, work_h), interpolation=cv2.INTER_AREA
            )
            ref_work = np.ascontiguousarray(
                np.transpose(ref_work_hwc, (2, 0, 1)), dtype=np.float32
            )
            del ref_work_hwc
        else:
            ref_work = ref_full_chw
        del ref_f32_hwc

        alpha_total = 0.0
        if total_supp > 0:
            for idx in range(1, total_supp + 1):
                if stop_ev and stop_ev.is_set():
                    return None

                if update_prog:
                    base_p = 50 + int((idx - 1) / total_supp * 45)
                    update_prog(
                        base_p,
                        f"FusionNet tile weighting & blending for frame {idx}/{total_supp}...",
                    )

                # 1. Load support frame from compact uint16
                supp_f32_hwc = aligned_burst_u16[idx].astype(np.float32) / 65535.0
                aligned_burst_u16[idx] = None  # Free uint16 slot immediately

                supp_full_chw = np.ascontiguousarray(
                    np.transpose(supp_f32_hwc, (2, 0, 1)), dtype=np.float32
                )

                # 2. Work Resolution Downscale
                if (work_h, work_w) != (target_h, target_w):
                    supp_work_hwc = cv2.resize(
                        supp_f32_hwc, (work_w, work_h), interpolation=cv2.INTER_AREA
                    )
                    supp_work = np.ascontiguousarray(
                        np.transpose(supp_work_hwc, (2, 0, 1)), dtype=np.float32
                    )
                    del supp_work_hwc
                else:
                    supp_work = supp_full_chw
                del supp_f32_hwc

                # 3. Single-Support WeightNet Tile Inference
                weight_work, alpha_mean = infer_single_support_weight_map(
                    session,
                    ref_work,
                    supp_work,
                    tile_size=tile_size,
                    overlap=overlap,
                    ghost_penalty=ghost_pen,
                    ghost_cutoff=ghost_cut,
                    stop_event=stop_ev,
                )
                alpha_total += alpha_mean
                del supp_work

                # 4. In-Place Blending & Instant Purge
                fuse_support_frame_inplace(
                    sum_img,
                    weight_sum,
                    supp_full_chw,
                    weight_work,
                    target_h,
                    target_w,
                )
                del supp_full_chw, weight_work
                gc.collect()

        del aligned_burst_u16, ref_work
        gc.collect()

        # -------------------------------------------------------------
        # STEP 4: Normalize Final Fused Accumulator
        # -------------------------------------------------------------
        if update_prog:
            update_prog(96, "Finalizing deep fusion output...")

        res_chw = np.clip(sum_img / (weight_sum + 1e-8), 0.0, 1.0)
        del sum_img, weight_sum
        gc.collect()

        res_fp32 = np.ascontiguousarray(
            np.transpose(res_chw, (1, 2, 0)), dtype=np.float32
        )
        del res_chw
        gc.collect()

        mean_alpha = alpha_total / max(1, total_supp)

        if res_fp32 is None:
            return None

        ref_dtype = getattr(ctx, "ref_dtype", np.uint16)
        if np.issubdtype(ref_dtype, np.integer):
            info = np.iinfo(ref_dtype)
            result = np.clip(
                res_fp32 * float(info.max) + 0.5, info.min, info.max
            ).astype(ref_dtype)
        else:
            result = np.ascontiguousarray(res_fp32, dtype=np.float32)

        print(
            f"[FusionNet] Pipeline finished successfully: shape={result.shape} dtype={result.dtype} mean_alpha={mean_alpha:.4f}"
        )
        return result


def save_rgb_result(image_fp32: np.ndarray, output_path: str | Path) -> None:
    """Save uncompressed float32 RGB array [H, W, 3] to 16-bit TIFF or PNG/JPEG."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image = np.ascontiguousarray(np.clip(image_fp32, 0.0, 1.0), dtype=np.float32)

    ext = output_path.suffix.lower()
    if ext in {".jpg", ".jpeg"}:
        Image.fromarray((image * 255.0 + 0.5).astype(np.uint8), mode="RGB").save(
            output_path, quality=95
        )
    elif ext == ".png":
        image_u8 = np.clip(image * 255.0 + 0.5, 0, 255).astype(np.uint8)
        image_bgr = cv2.cvtColor(image_u8, cv2.COLOR_RGB2BGR)
        if not cv2.imwrite(str(output_path), image_bgr):
            raise RuntimeError(f"Failed to save PNG result: {output_path}")
    else:
        # Default: 16-bit TIFF
        image_u16 = np.clip(image * 65535.0 + 0.5, 0, 65535).astype(np.uint16)
        image_bgr = cv2.cvtColor(image_u16, cv2.COLOR_RGB2BGR)
        if not cv2.imwrite(str(output_path), image_bgr):
            raise RuntimeError(f"Failed to save 16-bit RGB result: {output_path}")


def running_weightnet(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
    merging_mode=None,
    output_suffix=None,
    batch_size=None,
    alignment_backend=None,
    clear_raw=None,
    db_path=None,
):
    """Facade delegating to running_mf_denoiser with merging_mode='FusionNet'."""
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
        running_mf_denoiser,
    )

    return running_mf_denoiser(
        parent=parent,
        single_process=single_process,
        batch_id=batch_id,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        merging_mode=merging_mode or "FusionNet",
        output_suffix=output_suffix or "weightnet",
        batch_size=batch_size,
        alignment_backend=alignment_backend,
        clear_raw=clear_raw,
        db_path=db_path,
    )


# Alias
running_fusionnet = running_weightnet
