"""
Average denoising adapter.

This module is standalone. MFDenoiser only calls the public adapter interface.
"""

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
