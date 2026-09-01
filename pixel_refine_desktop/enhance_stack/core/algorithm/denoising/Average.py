"""
Average denoising adapter (GPU-Resident & CPU Parity).

Matches SpatialFusion and FusioNet pipeline architecture:
- Routes to GPU-resident pipeline (taichi_aot Vulkan) for zero-copy streaming
- Guarantees 100% RGB output in uint16/uint8 format
- Output saved with AutoEnhance v2 tonemapping via save_image
"""

import numpy as np

from ._common_helpers import active_backend, restore_output_dtype


class AverageDenoisingAlgorithm:
    """Simple average multi-frame denoising adapter."""

    NAME = "Average"
    KIND = "denoising"
    DESCRIPTION = "Average all aligned frames."

    def run(self, ctx, frames=None, batch_plan=None):
        backend = active_backend()
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
            result = restore_output_dtype(result_fp32, ref_dtype)
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
            return restore_output_dtype(averaged, ref_dtype)

        return None
