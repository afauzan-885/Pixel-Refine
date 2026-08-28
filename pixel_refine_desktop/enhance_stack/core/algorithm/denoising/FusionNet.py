import gc
import os
import threading
from pathlib import Path

import h5py
import numpy as np

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.flownet_inference import (
    AOTOpticalFlowAligner,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
    DEFAULT_WEIGHTNET_ONNX,
    RAW_EXTENSIONS,
    fuse_support_frame_inplace,
    infer_single_support_weight_map,
    load_rgb_linear_image,
    load_weightnet_onnx,
)


class FusionNetDenoisingAlgorithm:
    """FusionNet deep multi-frame burst fusion denoising adapter with compute_flow.tcm AOT alignment."""

    NAME = "FusionNet"
    KIND = "denoising"
    DESCRIPTION = "Deep learning multi-frame burst fusion with compute_flow.tcm AOT alignment and FusionNet."

    # Default Config Parameters (Configurable default parameters)
    DEFAULT_CONFIG = {
        "work_scale": 0.50,  # 50% scaling for FlowNet & WeightNet analysis
        "flownet_work_scale": 1.0,  # Optical flow work scale (defaults to work_scale)
        "weightnet_work_scale": 0.50,  # WeightNet ONNX work scale (defaults to work_scale)
        "tile_size": 256,  # ONNX patch size (256, 512, 1024)
        "tile_overlap": 0.30,  # Tile overlap ratio (30%)
        "ghost_penalty": 1.0,  # Exponent penalty for motion/ghost artifacts
        "ghost_cutoff": 0.05,  # Low-weight threshold cutoff
        "chroma_sensitivity": 1.0,  # Color deviation protection sensitivity
    }

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
        if getattr(ctx, "image_paths", None) and len(ctx.image_paths) > 0:
            # Free in-memory burst if present to eliminate host RAM pressure
            if hasattr(ctx, "frames") and ctx.frames is not None:
                ctx.frames = None
            if hasattr(ctx, "aligned_frames") and ctx.aligned_frames is not None:
                ctx.aligned_frames = None
            gc.collect()
            return list(ctx.image_paths), "paths"
        if frames:
            return list(frames), "memory"
        return [], "none"

    def run(self, ctx, frames, batch_plan=None):
        """
        Execute FlowNet streaming alignment followed by FusionNet ONNX fusion.
        """
        inputs, source = self._load_inputs(ctx, frames)
        if not inputs:
            print("[FusionNet] No input images/frames available.")
            return None

        # Resolve parameters with DEFAULT_CONFIG fallbacks
        params_cfg = getattr(ctx, "params", {}) or {}
        work_scale = float(
            params_cfg.get("work_scale", self.DEFAULT_CONFIG["work_scale"])
        )
        tile_size = int(
            params_cfg.get(
                "fusionnet_tile_size",
                params_cfg.get(
                    "tile_size",
                    params_cfg.get(
                        "weightnet_tile_size", self.DEFAULT_CONFIG["tile_size"]
                    ),
                ),
            )
        )
        if tile_size < 256:
            tile_size = 256
        overlap = float(
            params_cfg.get(
                "tile_overlap",
                params_cfg.get("overlap", self.DEFAULT_CONFIG["tile_overlap"]),
            )
        )
        ghost_pen = float(
            params_cfg.get("ghost_penalty", self.DEFAULT_CONFIG["ghost_penalty"])
        )
        ghost_cut = float(
            params_cfg.get("ghost_cutoff", self.DEFAULT_CONFIG["ghost_cutoff"])
        )
        chroma_sens = float(
            params_cfg.get(
                "chroma_sensitivity", self.DEFAULT_CONFIG["chroma_sensitivity"]
            )
        )
        is_raw = bool(getattr(ctx, "is_linear_mode", False))
        if not is_raw and getattr(ctx, "image_paths", None):
            is_raw = any(
                Path(p).suffix.lower() in RAW_EXTENSIONS for p in ctx.image_paths
            )

        print(
            f"[FusionNet] Starting FlowNet + FusionNet pipeline: "
            f"source={source} frames={len(inputs)} is_raw={is_raw} "
            f"tile_size={tile_size}"
        )

        update_prog = getattr(ctx, "update_progress", None)
        stop_req = getattr(ctx, "stop_requested", None)

        stop_ev = None
        if stop_req is not None:
            stop_ev = threading.Event()
            if callable(stop_req) and stop_req():
                return None

        # ── GPU-Resident Pipeline (zero-copy path for file-based bursts) ──
        if source == "paths":
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.gpu_resident_pipeline import (
                run_gpu_resident_pipeline,
            )
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
                load_weightnet_onnx as _load_wn_onnx,
            )

            print("[FusionNet] Routing to GPU-resident zero-copy pipeline...")
            session = _load_wn_onnx(
                DEFAULT_WEIGHTNET_ONNX, runtime="dml", patch_size=tile_size
            )

            result_fp32, mean_alpha = run_gpu_resident_pipeline(
                inputs,
                session,
                work_scale=work_scale,
                tile_size=tile_size,
                overlap=overlap,
                ghost_penalty=ghost_pen,
                ghost_cutoff=ghost_cut,
                chroma_sensitivity=chroma_sens,
                is_raw=is_raw,
                stop_event=stop_ev,
                progress_callback=update_prog,
            )

            if result_fp32 is None:
                return None

            # Always convert float32 to high-precision 16-bit uint16 TIFF [0, 65535]
            result = np.clip(result_fp32 * 65535.0 + 0.5, 0.0, 65535.0).astype(
                np.uint16
            )

            print(
                f"[FusionNet] GPU-resident pipeline complete: "
                f"shape={result.shape} dtype={result.dtype} mean_alpha={mean_alpha:.4f}"
            )
            return result

        # Fallback for memory/HDF5 inputs
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

        if update_prog:
            update_prog(2, "Loading reference linear frame...")

        if source == "paths":
            ref_linear = load_rgb_linear_image(inputs[0])
        else:
            ref_linear = _to_f32(inputs[0])
            inputs[0] = None

        target_h, target_w = ref_linear.shape[:2]
        ref_linear = np.ascontiguousarray(ref_linear, dtype=np.float32)

        auto_params = None
        if is_raw:
            from taichi_vision import taichi_aot
            from taichi_vision.taichi_algorithm.enhancement.auto_enhance import (
                apply_auto_enhance_np,
            )

            auto_params = taichi_aot.analyze_auto_enhance_params(ref_linear)
            ref_enhanced = apply_auto_enhance_np(ref_linear, **auto_params)
            del ref_linear
        else:
            ref_enhanced = ref_linear

        from taichi_vision import taichi_aot

        total_supp = len(inputs) - 1
        work_scale = float(work_scale)
        work_h = max(1, int(target_h * work_scale))
        work_w = max(1, int(target_w * work_scale))

        ref_full_chw = np.ascontiguousarray(
            np.transpose(ref_enhanced, (2, 0, 1)), dtype=np.float32
        )
        sum_img = ref_full_chw.copy()
        weight_sum = np.ones((3, target_h, target_w), dtype=np.float32)

        if (work_h, work_w) != (target_h, target_w):
            ref_work_hwc = taichi_aot.resize(
                ref_enhanced, (work_w, work_h), interpolation=taichi_aot.INTER_AREA
            )
            ref_work = np.ascontiguousarray(
                np.transpose(ref_work_hwc, (2, 0, 1)), dtype=np.float32
            )
            del ref_work_hwc
        else:
            ref_work = ref_full_chw

        alpha_total = 0.0

        if total_supp > 0:
            if update_prog:
                update_prog(
                    5, "Initializing GPU Optical Flow & FusionNet ONNX engine..."
                )

            session = load_weightnet_onnx(
                DEFAULT_WEIGHTNET_ONNX, runtime="dml", patch_size=tile_size
            )

            with AOTOpticalFlowAligner(
                ref_enhanced,
                work_scale=work_scale,
                tile_size=16,
            ) as aligner:
                del ref_enhanced
                gc.collect()

                import psutil

                proc = psutil.Process(os.getpid())

                for idx, item in enumerate(inputs[1:], start=1):
                    if stop_ev and stop_ev.is_set():
                        return None

                    supp_name = Path(item).name if source == "paths" else f"frame_{idx}"
                    if update_prog:
                        base_p = 5 + int((idx - 1) / total_supp * 90)
                        update_prog(
                            base_p,
                            f"Streaming GPU alignment & AI fusion for {supp_name} ({idx}/{total_supp})...",
                        )

                    if source == "paths":
                        supp_linear = load_rgb_linear_image(item)
                    else:
                        supp_linear = _to_f32(item)
                        inputs[idx] = None

                    if is_raw and auto_params is not None:
                        supp_raw = apply_auto_enhance_np(supp_linear, **auto_params)
                        del supp_linear
                    else:
                        supp_raw = supp_linear

                    if supp_raw.shape[:2] != (target_h, target_w):
                        supp_raw = taichi_aot.resize(
                            supp_raw,
                            (target_w, target_h),
                            interpolation=taichi_aot.INTER_LINEAR,
                        )
                    supp_raw = np.ascontiguousarray(supp_raw, dtype=np.float32)

                    supp_aligned = aligner.align_frame(
                        supp_raw,
                        stop_event=stop_ev,
                    )
                    del supp_raw

                    supp_full_chw = np.ascontiguousarray(
                        np.transpose(supp_aligned, (2, 0, 1)), dtype=np.float32
                    )

                    if (work_h, work_w) != (target_h, target_w):
                        supp_work_hwc = taichi_aot.resize(
                            supp_aligned,
                            (work_w, work_h),
                            interpolation=taichi_aot.INTER_AREA,
                        )
                        supp_work = np.ascontiguousarray(
                            np.transpose(supp_work_hwc, (2, 0, 1)), dtype=np.float32
                        )
                        del supp_work_hwc
                    else:
                        supp_work = supp_full_chw
                    del supp_aligned

                    weight_work, alpha_mean = infer_single_support_weight_map(
                        session,
                        ref_work,
                        supp_work,
                        tile_size=tile_size,
                        overlap=overlap,
                        ghost_penalty=ghost_pen,
                        ghost_cutoff=ghost_cut,
                        chroma_sensitivity=chroma_sens,
                        stop_event=stop_ev,
                    )
                    alpha_total += alpha_mean
                    del supp_work

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

        else:
            del ref_enhanced
            gc.collect()

        del ref_work
        gc.collect()

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

        # Always convert float32 to high-precision 16-bit uint16 TIFF [0, 65535]
        result = np.clip(res_fp32 * 65535.0 + 0.5, 0.0, 65535.0).astype(np.uint16)

        print(
            f"[FusionNet] Pipeline finished successfully: shape={result.shape} dtype={result.dtype} mean_alpha={mean_alpha:.4f}"
        )
        return result


def running_fusionnet(
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
        output_suffix=output_suffix or "fusionet",
        batch_size=batch_size,
        alignment_backend=alignment_backend,
        clear_raw=clear_raw,
        db_path=db_path,
    )
