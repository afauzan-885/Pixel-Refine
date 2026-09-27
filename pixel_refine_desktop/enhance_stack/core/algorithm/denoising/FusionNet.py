"""FusionNet denoising adapter.

The adapter owns only algorithm configuration and result conversion.  All
execution details (RGB resident, RAW Native, alignment, and WeightNet
lifecycle) are delegated to ``resident_pipeline`` so MFDenoiser and the UI
use the same contract as Similarity.
"""

import gc
from pathlib import Path
import numpy as np

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
    RAW_EXTENSIONS,
    load_weightnet_onnx,
    DEFAULT_WEIGHTNET_ONNX,
)


class FusionNetDenoisingAlgorithm:
    """FusionNet adapter using resident alignment plus WeightNet inference."""

    NAME = "FusionNet"
    KIND = "denoising"
    DESCRIPTION = (
        "Deep burst fusion with resident alignment and 1-channel WeightNet inference."
    )

    # Default Config Parameters (Configurable default parameters)
    DEFAULT_CONFIG = {
        "work_scale": 0.50,  # Scaling factor for resident alignment and analysis
        "tile_size": 512,  # WeightNet model block (256, 512, 1024)
        "input_channels": 1,
        "tile_overlap": 0.20,  # Tile overlap ratio (20% optimal for speed & seamless blend)
        "ghost_penalty": 5.0,  # Maximum ghost penalty for clean/low-noise regions
        "ghost_penalty_min": 0.85,  # Minimum ghost penalty for high-noise regions
    }

    def _load_inputs(self, ctx, frames):
        """Return a concrete frame list from image paths or memory."""
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

    def _resolve_config(self, ctx):
        """Normalize FusionNet settings once, like the SpatialFusion adapter."""
        # Start from the provider defaults/global settings so direct callers
        # that construct a context without MFDenoiser still honor the FusionNet
        # panel.  Batch values carried in ``fusionnet_params`` are applied last
        # and therefore remain authoritative over generic Similarity aliases.
        try:
            from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.fusionnet_parameter_settings import (
                load_fusionnet_config_for_batch,
            )

            params = load_fusionnet_config_for_batch(getattr(ctx, "batch_id", None))
        except Exception:
            params = dict(self.DEFAULT_CONFIG)
        context_params = dict(getattr(ctx, "params", {}) or {})
        params.update(context_params)
        nested = context_params.get("fusionnet_params")
        if isinstance(nested, dict):
            params.update(nested)

        work_scale = float(
            params.get(
                "fusionnet_work_resolution",
                params.get(
                    "work_scale",
                    params.get(
                        "flownet_work_scale",
                        params.get(
                            "weightnet_work_scale",
                            params.get(
                                "work_resolution_scale",
                                params.get(
                                    "proxy_scale", self.DEFAULT_CONFIG["work_scale"]
                                ),
                            ),
                        ),
                    ),
                ),
            )
        )
        work_scale = max(0.05, min(1.0, work_scale))
        requested_tile = int(
            params.get(
                "fusionnet_tile_size",
                params.get(
                    "tile_size",
                    params.get(
                        "weightnet_tile_size",
                        params.get("ai_tile_size", self.DEFAULT_CONFIG["tile_size"]),
                    ),
                ),
            )
        )
        tile_size = min(
            (256, 512, 1024), key=lambda candidate: abs(candidate - requested_tile)
        )
        overlap = params.get(
            "tile_overlap",
            params.get(
                "overlap",
                params.get("ai_overlap_percent", self.DEFAULT_CONFIG["tile_overlap"]),
            ),
        )
        # Similarity's AI overlap field already stores a normalized ratio;
        # accept percentage-style values from older batch snapshots too.
        overlap = float(overlap)
        if overlap > 1.0:
            overlap /= 100.0
        return {
            "work_scale": work_scale,
            "tile_size": tile_size,
            # Keep the model feed on the quality-validated luminance baseline.
            "input_channels": 1,
            "overlap": max(0.0, min(0.95, overlap)),
            "ghost_penalty": float(
                params.get("ghost_penalty", self.DEFAULT_CONFIG["ghost_penalty"])
            ),
            "ghost_penalty_min": float(
                params.get(
                    "ghost_penalty_min", self.DEFAULT_CONFIG["ghost_penalty_min"]
                )
            ),
            "chroma_sensitivity": float(params.get("chroma_sensitivity", 1.0)),
            "alignment_plan": getattr(ctx, "alignment_selection_name", None)
            or params.get("alignment_plan", "No Alignment"),
            "alignment_config": dict(params.get("alignment_params", {}) or {}),
            "batch_queue": max(
                1, min(2, int(params.get("batch_queue", params.get("batch_size", 2))))
            ),
        }

    @staticmethod
    def _is_raw(ctx, inputs):
        if bool(getattr(ctx, "is_linear_mode", False)):
            return True
        paths = getattr(ctx, "image_paths", None)
        return bool(paths) and any(
            Path(p).suffix.lower() in RAW_EXTENSIONS for p in paths
        )

    def _run_resident_paths(self, ctx, inputs, config, batch_plan, is_raw):
        """Run the single resident execution lane for path-based bursts."""
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.resident_pipeline import (
            run_resident_pipeline,
        )

        print(
            f"[FusionNet] Resident route: frames={len(inputs)} is_raw={is_raw} "
            f"tile={config['tile_size']} work_scale={config['work_scale']:.2f}"
        )
        session = load_weightnet_onnx(
            DEFAULT_WEIGHTNET_ONNX,
            runtime="dml",
            patch_size=config["tile_size"],
            input_channels=config["input_channels"],
        )
        config["alignment_config"].setdefault("work_scale", config["work_scale"])
        result, mean_alpha = run_resident_pipeline(
            inputs,
            session,
            weight_engine="fusionet",
            alignment_plan=config["alignment_plan"],
            alignment_config=config["alignment_config"],
            work_scale=config["work_scale"],
            flownet_work_scale=config["work_scale"],
            weightnet_work_scale=config["work_scale"],
            # The UI work-resolution value is authoritative.  Without this,
            # the resident safety cap turns 1.0 into 0.5 on 4096-wide input.
            max_work_dimension=None,
            weightnet_input_channels=config["input_channels"],
            tile_size=config["tile_size"],
            overlap=config["overlap"],
            ghost_penalty=config["ghost_penalty"],
            ghost_penalty_min=config["ghost_penalty_min"],
            ghost_cutoff=0.0,
            chroma_sensitivity=config["chroma_sensitivity"],
            is_raw=is_raw,
            storage_mode="direct",
            batch_queue=config["batch_queue"],
            batch_plan=batch_plan,
            stop_event=getattr(ctx, "stop_requested", None),
            progress_callback=getattr(ctx, "update_progress", None),
            raw_native=bool(getattr(ctx, "is_raw_native", False)),
        )
        if result is None:
            return None
        if bool(getattr(ctx, "is_raw_native", False)):
            ctx.raw_native_result = result
            preview = result.preview_rgb
            print(
                f"[FusionNet][RAW Native] preview shape={preview.shape} "
                f"dtype={preview.dtype}; DNG carrier retained for save"
            )
            return preview
        from taichi_vision import taichi_aot

        output = taichi_aot.cast(result, np.uint16)
        del result
        try:
            taichi_aot.get_engine().buffer_pool.clear()
        except Exception:
            pass
        gc.collect()
        print(
            f"[FusionNet] Resident complete: shape={output.shape} "
            f"dtype={output.dtype} mean_alpha={mean_alpha:.4f}"
        )
        return output

    def run(self, ctx, frames, batch_plan=None):
        """
        Execute resident alignment followed by FusionNet WeightNet fusion.
        """
        inputs, source = self._load_inputs(ctx, frames)
        if not inputs:
            print("[FusionNet] No input images/frames available.")
            return None

        config = self._resolve_config(ctx)
        work_scale = config["work_scale"]
        tile_size = config["tile_size"]
        overlap = config["overlap"]
        ghost_pen = config["ghost_penalty"]
        ghost_pen_min = config["ghost_penalty_min"]
        is_raw = self._is_raw(ctx, inputs)

        print(
            f"[FusionNet] Starting resident alignment + WeightNet pipeline: "
            f"source={source} frames={len(inputs)} is_raw={is_raw} "
            f"tile_size={tile_size} work_scale={work_scale} "
            f"ghost_penalty_range=[{ghost_pen_min:.2f}, {ghost_pen:.2f}]"
        )

        update_prog = getattr(ctx, "update_progress", None)
        stop_req = getattr(ctx, "stop_requested", None)
        stop_ev = stop_req

        if stop_req is not None:
            if callable(stop_req) and stop_req():
                return None
            elif hasattr(stop_req, "is_set") and stop_req.is_set():
                return None

        # ── GPU-Resident Pipeline (zero-copy path for file-based bursts) ──
        if source == "paths":
            return self._run_resident_paths(ctx, inputs, config, batch_plan, is_raw)
        # Compatibility fallback for callers that still provide in-memory or
        # HDF5 frames.  File-based MFDenoiser execution never enters this
        # legacy lane; it uses resident_pipeline's alignment registry above.
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.flownet_inference import (
            AOTOpticalFlowAligner,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
            fuse_support_frame_inplace,
            infer_single_support_weight_map,
            load_rgb_linear_image,
        )

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
                DEFAULT_WEIGHTNET_ONNX,
                runtime="dml",
                patch_size=tile_size,
                input_channels=config["input_channels"],
            )

            with AOTOpticalFlowAligner(
                ref_enhanced,
                work_scale=work_scale,
                tile_size=32,
                smooth=True,
                adaptive=True,
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
                        ghost_cutoff=0.0,
                        chroma_sensitivity=1.0,
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
