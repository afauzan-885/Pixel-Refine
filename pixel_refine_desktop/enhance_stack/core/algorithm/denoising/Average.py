"""
Average denoising adapter (GPU-Resident & CPU Parity).

Matches SpatialFusion and FusioNet pipeline architecture:
- Routes to GPU-resident pipeline (taichi_aot Vulkan) for zero-copy streaming
- Guarantees 100% RGB output in uint16/uint8 format
- Output saved with AutoEnhance v2 tonemapping via save_image
"""

import gc
import os
import threading

import h5py
import numpy as np


def _frame_info(frame):
    if frame is None:
        return "None"
    return f"shape={getattr(frame, 'shape', None)}, dtype={getattr(frame, 'dtype', None)}"


def _active_backend():
    """Resolve the backend selected by Performance Settings at call time."""
    try:
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.backend_arch_helper import (
            get_backend_arch,
        )

        configured = str(get_backend_arch() or "").strip().lower()
        if configured in {"cpu", "cuda", "vulkan", "opengl", "gles"}:
            return configured
    except Exception:
        pass
    try:
        from taichi_vision import taichi_aot

        return str(getattr(taichi_aot.engine, "arch", "cpu")).strip().lower()
    except Exception:
        return "cpu"


def _restore_output_dtype(image, dtype=np.uint16):
    if image is None:
        return None
    image_f32 = np.ascontiguousarray(image, dtype=np.float32)
    if dtype is None or not np.issubdtype(dtype, np.integer):
        dtype = np.uint16
    info = np.iinfo(dtype)
    max_val = float(np.nanmax(image_f32)) if image_f32.size > 0 else 1.0
    if max_val <= 1.5:
        image_f32 = image_f32 * float(info.max)
    image_clipped = np.clip(image_f32 + 0.5, float(info.min), float(info.max))
    return image_clipped.astype(dtype, copy=False)


class AverageDenoisingAlgorithm:
    """Simple average multi-frame denoising adapter."""

    NAME = "Average"
    KIND = "denoising"
    DESCRIPTION = "Average all aligned frames."

    def run(self, ctx, frames=None, batch_plan=None):
        backend = _active_backend()
        image_paths = getattr(ctx, "image_paths", None)

        if image_paths and len(image_paths) >= 2:
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.resident_pipeline import (
                run_resident_pipeline,
            )

            is_raw = bool(getattr(ctx, "is_linear_mode", False))
            storage_mode = "direct"
            work_scale = float(
                getattr(ctx, "params", {}).get("work_resolution_scale", 0.50)
            ) if hasattr(ctx, "params") else 0.50

            stop_req = getattr(ctx, "stop_requested", None)
            if stop_req is not None and callable(stop_req) and stop_req():
                return None

            print(
                f"[Average] Routing to GPU-resident pipeline: backend={backend} "
                f"frames={len(image_paths)} storage_mode={storage_mode}"
            )

            alignment_plan = (
                getattr(ctx, "alignment_selection_name", None)
                or getattr(ctx, "params", {}).get("alignment_plan", "No Alignment")
            )
            alignment_config = getattr(ctx, "params", {}).get(
                "alignment_params", {}
            )
            batch_queue = int(
                getattr(ctx, "params", {}).get(
                    "batch_queue", getattr(ctx, "params", {}).get("batch_size", 3)
                )
            )

            result_fp32, _ = run_resident_pipeline(
                image_paths,
                session=None,
                weight_engine="average",
                alignment_plan=alignment_plan,
                alignment_config=alignment_config,
                work_scale=work_scale,
                is_raw=is_raw,
                storage_mode=storage_mode,
                batch_queue=batch_queue,
                stop_event=stop_req,
                progress_callback=getattr(ctx, "update_progress", None),
            )

            if result_fp32 is None:
                return None

            ref_dtype = getattr(ctx, "ref_dtype", np.uint16 if is_raw else np.uint8)
            result = _restore_output_dtype(result_fp32, ref_dtype)
            print(
                f"[Average] finished backend={backend} "
                f"result shape={result.shape} dtype={result.dtype}"
            )
            return result

        # Legacy in-memory / HDF5 fallback
        if frames:
            print(
                f"[AverageDenoisingAlgorithm] start in-memory frames={len(frames)} "
                f"batch_plan={batch_plan}"
            )
            stack = np.stack(
                [frame.astype(np.float32, copy=False) for frame in frames], axis=0
            )
            averaged = np.mean(stack, axis=0)
            ref_dtype = getattr(ctx, "ref_dtype", frames[0].dtype)
            return _restore_output_dtype(averaged, ref_dtype)

        return None


def average_accumulate(sum_image, count, frame):
    if frame is None:
        return sum_image, count
    if sum_image is None:
        sum_image = np.zeros(frame.shape, dtype=np.float32)
    sum_image += frame.astype(np.float32, copy=False)
    return sum_image, count + 1


def average_finalize(ctx, sum_image, count):
    if sum_image is None or count <= 0:
        return None
    result = sum_image / float(count)
    dtype = getattr(ctx, "ref_dtype", None) or getattr(
        ctx.reference_image, "dtype", result.dtype
    )
    return _restore_output_dtype(result, dtype)


def merge_average_from_hdf5(ctx, progress_callback=None):
    alignment_name = str(
        getattr(ctx, "alignment_selection_name", "No Alignment") or "No Alignment"
    ).strip().casefold()
    if alignment_name == "no alignment":
        return False
    if not getattr(ctx, "hdf5_path", None):
        return False
    if not os.path.exists(ctx.hdf5_path):
        return False

    print(f"[Average] streaming aligned HDF5: {ctx.hdf5_path}")
    sum_image = None
    count = 0
    with h5py.File(ctx.hdf5_path, "r") as h5f:
        image_keys = sorted(
            [key for key in h5f.keys() if key.startswith("image_")],
            key=lambda item: int(item.split("_", 1)[1]),
        )
        for idx, key in enumerate(image_keys):
            if getattr(ctx, "stop_requested", None) and ctx.stop_requested():
                break
            frame = h5f[key][...]
            sum_image, count = average_accumulate(sum_image, count, frame)
            del frame
            gc.collect()
            if progress_callback:
                from pixel_refine_desktop.ui.views.settings.General.Language import (
                    language_config,
                )

                msg = getattr(
                    language_config, "PROGRESS_MERGING", "Merging: {}/{}"
                ).format(idx + 1, len(image_keys))
                progress_callback(
                    60 + int(((idx + 1) / max(1, len(image_keys))) * 30),
                    msg,
                )
    ctx.result_image = average_finalize(ctx, sum_image, count)
    print(
        f"[Average] HDF5 merge count={count} result={_frame_info(ctx.result_image)}"
    )
    del sum_image
    gc.collect()
    return True


def merge_average_from_paths(
    ctx, load_single_frame, progress_callback=None, batch_plan=None
):
    # Delegate directly to the GPU-resident pipeline
    algo = AverageDenoisingAlgorithm()
    ctx.result_image = algo.run(ctx, frames=None, batch_plan=batch_plan)
    return ctx.result_image is not None


# Backward-compatible alias for older imports while the registry migration is in progress.
AverageMerge = AverageDenoisingAlgorithm


def running_average(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
        running_mf_denoiser,
    )

    return running_mf_denoiser(
        parent=parent,
        single_process=single_process,
        batch_id=batch_id,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        merging_mode=AverageDenoisingAlgorithm.NAME,
        output_suffix="average",
    )
