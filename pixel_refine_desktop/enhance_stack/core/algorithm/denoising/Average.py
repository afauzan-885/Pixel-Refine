"""
Average denoising adapter.

This module is standalone. MFDenoiser only calls the public adapter interface.
"""

import gc
import os

import h5py
import numpy as np


def _frame_info(frame):
    if frame is None:
        return "None"
    return f"shape={getattr(frame, 'shape', None)}, dtype={getattr(frame, 'dtype', None)}"


class AverageDenoisingAlgorithm:
    """Simple average multi-frame denoising adapter."""

    NAME = "Average"
    KIND = "denoising"
    DESCRIPTION = "Average all aligned frames."

    def run(self, ctx, frames, batch_plan=None):
        print(
            f"[AverageDenoisingAlgorithm] start frames={len(frames)} "
            f"batch_plan={batch_plan}"
        )
        if not frames:
            print("[AverageDenoisingAlgorithm] no frames received")
            return None
        for idx, frame in enumerate(frames):
            print(f"[AverageDenoisingAlgorithm] input_frame_{idx}: {_frame_info(frame)}")
        stack = np.stack([frame.astype(np.float32, copy=False) for frame in frames], axis=0)
        print(f"[AverageDenoisingAlgorithm] stack shape={stack.shape}, dtype={stack.dtype}")
        averaged = np.mean(stack, axis=0)
        ref_dtype = getattr(ctx, "ref_dtype", frames[0].dtype)
        if np.issubdtype(ref_dtype, np.integer):
            max_val = np.iinfo(ref_dtype).max
        else:
            max_val = 1.0
        result = np.clip(averaged, 0, max_val).astype(ref_dtype)
        print(f"[AverageDenoisingAlgorithm] result: {_frame_info(result)}")
        return result


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
    dtype = getattr(ctx, "ref_dtype", None) or getattr(ctx.reference_image, "dtype", result.dtype)
    if np.issubdtype(dtype, np.integer):
        info = np.iinfo(dtype)
        result = np.clip(result, info.min, info.max)
    return result.astype(dtype, copy=False)


def merge_average_from_hdf5(ctx, progress_callback=None):
    alignment_name = str(getattr(ctx, "alignment_selection_name", "No Alignment") or "No Alignment").strip().casefold()
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
                from pixel_refine_desktop.ui.views.settings.General.Language import language_config
                msg = getattr(language_config, "PROGRESS_MERGING", "Merging: {}/{}").format(
                    idx + 1, len(image_keys)
                )
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


def merge_average_from_paths(ctx, load_single_frame, progress_callback=None, batch_plan=None):
    alignment_name = str(getattr(ctx, "alignment_selection_name", "No Alignment") or "No Alignment").strip().casefold()
    if alignment_name != "no alignment":
        return False
    if not getattr(ctx, "image_paths", None):
        return False

    print(
        f"[Average] streaming input paths: frames={len(ctx.image_paths)} batch_plan={batch_plan}"
    )
    sum_image = None
    count = 0
    target_dims = None
    for idx, path in enumerate(ctx.image_paths):
        if getattr(ctx, "stop_requested", None) and ctx.stop_requested():
            break
        frame = load_single_frame(ctx, path, target_dims=target_dims)
        if frame is None:
            continue
        if target_dims is None:
            target_dims = frame.shape[:2]
            ctx.reference_image = frame
            ctx.ref_dtype = frame.dtype
            ctx.ref_h, ctx.ref_w = frame.shape[:2]
        sum_image, count = average_accumulate(sum_image, count, frame)
        if idx > 0 or ctx.reference_image is not frame:
            del frame
        gc.collect()
        if progress_callback:
            from pixel_refine_desktop.ui.views.settings.General.Language import language_config
            msg = getattr(language_config, "PROGRESS_MERGING", "Merging: {}/{}").format(
                idx + 1, len(ctx.image_paths)
            )
            progress_callback(
                60 + int(((idx + 1) / max(1, len(ctx.image_paths))) * 30),
                msg,
            )
    ctx.result_image = average_finalize(ctx, sum_image, count)
    print(
        f"[Average] path merge count={count} result={_frame_info(ctx.result_image)}"
    )
    del sum_image
    gc.collect()
    return True


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
