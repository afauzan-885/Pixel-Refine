import os
import numpy as np
import psutil
from .spatial_pipeline import process_in_gpu


# The outer crop/stitch implementation below is intentionally not enabled by
# the production dispatcher yet.  It normalizes each crop before blending,
# while the native full-frame graph accumulates unnormalised sums and divides
# once at the end.  Those two operations are not mathematically equivalent at
# tile boundaries, so enabling the crop path without a same-backend oracle
# would silently change the denoising result.
SPATIAL_BLOCK_PARITY_CERTIFIED = False
SPATIAL_BLOCK_SIZES = (512, 768, 1024, 2048)
# A block result is only eligible for promotion when both the image and raw
# weight planes agree with the same-backend full-frame result.  Native paths
# accumulate float32 values in a different tile order, so a small one-ulp-scale
# envelope is needed for a useful gate.  This is a numerical validation
# tolerance, not a visual-quality target; ``loss_score`` ranks candidates.
SPATIAL_BLOCK_PARITY_ATOL = 1.5e-6
SPATIAL_BLOCK_PARITY_RTOL = 0.0
# Relative-L1 qualification lets us rank and accept numerically equivalent
# float32 candidates even when tile-order accumulation creates a few extra
# ulps.  This does not promote the block path by itself.
SPATIAL_BLOCK_MAX_RELATIVE_LOSS = 2.0e-6


def _normalize_spatial_block_size(value, default=1024):
    """Return a bounded, aligned block size for diagnostics and telemetry."""

    try:
        size = int(value)
    except (TypeError, ValueError):
        size = int(default)
    size = max(64, size)
    # Keep the same 16-pixel alignment used by the shared runtime policy.
    return max(64, (size // 16) * 16)


def _select_spatial_execution_mode(block_requested, block_size=1024):
    """Select a safe spatial execution mode without pretending parity.

    The helper is deliberately pure so tests can cover the policy without
    initializing Taichi or a native backend.  The tile/halo implementation is
    only eligible after a measured same-backend parity gate is added; until
    then an explicit full-frame fallback is returned.
    """

    normalized_size = _normalize_spatial_block_size(block_size)
    if bool(block_requested) and not SPATIAL_BLOCK_PARITY_CERTIFIED:
        return {
            "requested": True,
            "enabled": False,
            "mode": "full_frame",
            "block_size": normalized_size,
            "reason": "spatial tile/halo stitch parity is not certified",
        }
    return {
        "requested": bool(block_requested),
        "enabled": bool(block_requested),
        "mode": "block" if bool(block_requested) else "full_frame",
        "block_size": normalized_size,
        "reason": "parity-certified" if bool(block_requested) else "not requested",
    }


def _spatial_parity_report(
    full_result,
    block_result,
    *,
    atol=SPATIAL_BLOCK_PARITY_ATOL,
    rtol=SPATIAL_BLOCK_PARITY_RTOL,
):
    """Compare full-frame and block results without changing either result.

    ``SpatialFusionProcessor.process`` returns either ``(image, weight,
    count)`` or ``(image, weight, count, per_image_weights)`` depending on
    the caller.  The helper accepts either that tuple or a mapping containing
    ``image``/``weight``/``count``.  It is deliberately side-effect free so
    an integration harness can run the two candidates on one backend and
    decide whether a block profile is eligible for promotion.

    A report is always returned, including shape/type/non-finite failures.
    ``passed`` is the strict numerical promotion gate; ``quality_passed`` is
    the relative-loss qualification used to rank an otherwise equivalent
    candidate.  Callers must not infer success from finite output alone.
    """

    def _unpack(result):
        if isinstance(result, dict):
            return result.get("image"), result.get("weight"), result.get("count")
        if isinstance(result, (tuple, list)) and len(result) >= 3:
            return result[0], result[1], result[2]
        return None, None, None

    full_image, full_weight, full_count = _unpack(full_result)
    block_image, block_weight, block_count = _unpack(block_result)
    report = {
        "passed": False,
        "reason": None,
        "atol": float(atol),
        "rtol": float(rtol),
        "image": {
            "shape": None,
            "dtype": None,
            "max_abs": None,
            "mean_abs": None,
            "rmse": None,
            "relative_l1": None,
        },
        "weight": {
            "shape": None,
            "dtype": None,
            "max_abs": None,
            "mean_abs": None,
            "rmse": None,
            "relative_l1": None,
        },
        # Worst-plane relative L1 is a useful ranking metric when a candidate
        # does not meet the strict promotion tolerance.  It is deliberately
        # informational for ranking; strict ``passed`` still reports the
        # np.allclose result for both planes, while ``quality_passed`` applies
        # the relative-loss budget plus structural/count checks.
        "loss_score": None,
        "quality_passed": False,
        "count": {
            "full": full_count,
            "block": block_count,
            "equal": False,
            "positive": False,
        },
    }

    if full_image is None or block_image is None:
        report["reason"] = "missing image result"
        return report
    if full_weight is None or block_weight is None:
        report["reason"] = "missing weight result"
        return report

    def _compare(name, left, right):
        lhs = np.asarray(left)
        rhs = np.asarray(right)
        item = report[name]
        item["shape"] = {
            "full": tuple(lhs.shape),
            "block": tuple(rhs.shape),
            "equal": lhs.shape == rhs.shape,
        }
        item["dtype"] = {
            "full": str(lhs.dtype),
            "block": str(rhs.dtype),
            "equal": lhs.dtype == rhs.dtype,
        }
        if lhs.shape != rhs.shape:
            return False
        if lhs.dtype != rhs.dtype:
            return False
        if not (np.all(np.isfinite(lhs)) and np.all(np.isfinite(rhs))):
            item["finite"] = False
            return False
        item["finite"] = True
        diff = np.abs(lhs.astype(np.float64, copy=False) - rhs.astype(np.float64, copy=False))
        item["max_abs"] = float(np.max(diff)) if diff.size else 0.0
        item["mean_abs"] = float(np.mean(diff)) if diff.size else 0.0
        item["rmse"] = float(np.sqrt(np.mean(np.square(diff)))) if diff.size else 0.0
        reference_l1 = float(np.mean(np.abs(lhs.astype(np.float64, copy=False)))) if lhs.size else 0.0
        item["relative_l1"] = float(item["mean_abs"] / max(reference_l1, 1.0e-12))
        item["passed"] = bool(np.allclose(lhs, rhs, atol=atol, rtol=rtol))
        return item["passed"]

    image_ok = _compare("image", full_image, block_image)
    weight_ok = _compare("weight", full_weight, block_weight)
    count_ok = full_count == block_count
    report["count"]["equal"] = count_ok
    if report["image"]["relative_l1"] is not None and report["weight"]["relative_l1"] is not None:
        report["loss_score"] = max(
            float(report["image"]["relative_l1"]),
            float(report["weight"]["relative_l1"]),
        )
    # ``process_in_gpu`` intentionally catches native exceptions and returns
    # an empty raw result with ``count == 0`` so the application can keep its
    # same-backend recovery path alive.  A parity harness must not mistake two
    # identical empty fallbacks for successful native execution.  Require at
    # least one processed frame from both runners before accepting parity.
    try:
        count_positive = int(full_count) > 0 and int(block_count) > 0
    except (TypeError, ValueError, OverflowError):
        count_positive = False
    report["count"]["positive"] = count_positive
    report["quality_passed"] = bool(
        count_ok
        and count_positive
        and report["loss_score"] is not None
        and float(report["loss_score"]) <= SPATIAL_BLOCK_MAX_RELATIVE_LOSS
    )
    if not image_ok or not weight_ok:
        report["reason"] = "image or weight mismatch"
    elif not count_ok:
        report["reason"] = "processed frame count mismatch"
    elif not count_positive:
        report["reason"] = "no processed frames; native runner likely failed"
    else:
        report["reason"] = "parity passed"
        report["passed"] = True
    return report


def run_spatial_block_parity_probe(
    full_frame_runner,
    block_runner,
    *,
    backend="unknown",
    device="unknown",
    block_size=None,
    atol=SPATIAL_BLOCK_PARITY_ATOL,
    rtol=SPATIAL_BLOCK_PARITY_RTOL,
):
    """Run a same-backend full/block comparison for an integration harness.

    The runners are supplied by the caller so this helper never initializes a
    second Taichi context or silently changes backend.  The caller should bind
    both runners to the same engine/device, shape, dtype, and parameters.  A
    successful report is evidence for that exact configuration only; it does
    not mutate :data:`SPATIAL_BLOCK_PARITY_CERTIFIED`.
    """

    report = _spatial_parity_report(
        full_frame_runner(),
        block_runner(),
        atol=atol,
        rtol=rtol,
    )
    report.update(
        {
            "backend": str(backend),
            "device": str(device),
            "block_size": None if block_size is None else int(block_size),
        }
    )
    return report


def get_ram_usage():
    """Returns the current RAM usage of the process in MiB."""
    process = psutil.Process()
    mem_info = process.memory_info()
    return mem_info.rss / 1024 / 1024


class SpatialFusionProcessor:
    """Handles Spatial Fusion exclusively through the Taichi AOT pipeline."""

    def __init__(self):
        pass

    @staticmethod
    def _process_image_blocks(
        images,
        reference_image_float,
        ref_image_h,
        ref_image_w,
        backend_args,
        block_size,
        halo,
        update_progress=None,
        stop_requested=None,
        return_raw=False,
    ):
        """Run AOT on bounded crops and stitch unnormalised sums.

        Each crop requests raw ``sum`` and ``weight`` planes from
        :func:`process_in_gpu`; only its disjoint core is copied into the
        global accumulator.  This avoids blending already-normalised crop
        results.  The dispatcher keeps this helper behind the parity gate.
        """
        if not SPATIAL_BLOCK_PARITY_CERTIFIED:
            raise RuntimeError(
                "[SpatialFusion][Block] crop/stitch execution is disabled: "
                "same-backend parity has not been certified"
            )
        block_size = max(64, int(block_size))
        halo = max(0, int(halo))
        channels = int(reference_image_float.shape[2]) if reference_image_float.ndim == 3 else 1
        full_sum = np.zeros((ref_image_h, ref_image_w, channels), dtype=np.float32)
        full_weight = np.zeros((ref_image_h, ref_image_w), dtype=np.float32)
        processed_total = 0
        blocks = [
            (y0, min(y0 + block_size, ref_image_h), x0, min(x0 + block_size, ref_image_w))
            for y0 in range(0, ref_image_h, block_size)
            for x0 in range(0, ref_image_w, block_size)
        ]

        for block_index, (y0, y1, x0, x1) in enumerate(blocks):
            if stop_requested and stop_requested():
                break
            cy0, cy1 = max(0, y0 - halo), min(ref_image_h, y1 + halo)
            cx0, cx1 = max(0, x0 - halo), min(ref_image_w, x1 + halo)
            crop_h, crop_w = cy1 - cy0, cx1 - cx0
            crop_images = [
                np.ascontiguousarray(frame[cy0:cy1, cx0:cx1])
                for frame in images
            ]
            crop_reference = np.ascontiguousarray(
                reference_image_float[cy0:cy1, cx0:cx1]
            )
            local_args = dict(backend_args)
            tile_h = max(2, min(int(backend_args["tile_h"]), crop_h))
            tile_w = max(2, min(int(backend_args["tile_w"]), crop_w))
            local_args.update(
                images=crop_images,
                reference_image_float=crop_reference,
                ref_image_h=crop_h,
                ref_image_w=crop_w,
                work_res_h=crop_h,
                work_res_w=crop_w,
                tile_h=tile_h,
                tile_w=tile_w,
                update_progress=None,
                return_raw=True,
            )
            global_rows = np.asarray(backend_args.get("row_starts", []), dtype=np.int64)
            global_cols = np.asarray(backend_args.get("col_starts", []), dtype=np.int64)

            def _crop_starts(global_starts, origin, extent, tile):
                if global_starts.size:
                    selected = global_starts[
                        (global_starts >= origin)
                        & (global_starts + tile <= origin + extent)
                    ]
                    if selected.size:
                        return np.ascontiguousarray(selected - origin, dtype=np.int32)
                return np.asarray([0], dtype=np.int32)

            local_args["row_starts"] = _crop_starts(global_rows, cy0, crop_h, tile_h)
            local_args["col_starts"] = _crop_starts(global_cols, cx0, crop_w, tile_w)
            local_args["base_window"] = None

            count, crop_sum, crop_weight, _ = process_in_gpu(**local_args)
            if crop_sum is None or crop_weight is None:
                continue
            # Halo pixels provide context only.  Stitch each block's disjoint
            # core exactly once to avoid double counting at overlaps.
            core_y0, core_y1 = y0 - cy0, y1 - cy0
            core_x0, core_x1 = x0 - cx0, x1 - cx0
            full_sum[y0:y1, x0:x1] += crop_sum[core_y0:core_y1, core_x0:core_x1]
            full_weight[y0:y1, x0:x1] += crop_weight[core_y0:core_y1, core_x0:core_x1]
            processed_total = max(processed_total, int(count))
            if update_progress:
                update_progress(
                    int((block_index + 1) * 100 / max(1, len(blocks))),
                    f"Spatial block {block_index + 1}/{len(blocks)}",
                )
            del crop_images, crop_reference, crop_sum, crop_weight

        if not return_raw:
            np.divide(
                full_sum,
                np.maximum(full_weight[..., None], np.float32(1e-6)),
                out=full_sum,
            )
        return processed_total, full_sum, full_weight, 0.0

    def process(
        self,
        images,
        ref_image_h,
        ref_image_w,
        ref_channels_buffer,
        ref_dtype,
        reference_image_float,
        tile_size,
        overlap,
        motion_sensitivity,
        noise_offset_factor,
        update_progress=None,
        stop_requested=None,
        total_overall_images=None,
        images_processed_so_far=0,
        lib_path=None,
        num_workers=-1,
        weight_of_each_image=False,
        enable_alignment=True,
        scale_down_factor: float = 1.0,
        return_raw=False,
        is_linear_mode=False,
        proxy_scale=1.0,
        process_in="gpu",
        merging_backend="taichi",
        **unused_kwargs,
    ):
        """Executes the Spatial Fusion algorithm on a batch of images."""
        print(f"[RAM] Startup SpatialFusionProcessor: {get_ram_usage():.2f} MB")

        if os.environ.get("AOT_MODE", "1") != "1":
            raise RuntimeError(
                "SpatialFusionProcessor requires AOT_MODE=1; the legacy C++ "
                "spatial-fusion path has been removed."
            )

        # MFDenoiser's shared governor may request 1024-tile processing for
        # this batch.  Keep that request visible, but do not route into the
        # experimental crop/stitch helper: it blends already-normalized crop
        # results and therefore has no proven parity with the native graph.
        # This explicit fallback prevents a log line claiming ``mode=block``
        # from being mistaken for an actually active spatial block kernel.
        spatial_block_policy = _select_spatial_execution_mode(
            unused_kwargs.get("spatial_block_requested", False),
            unused_kwargs.get("spatial_block_size", 1024),
        )
        if spatial_block_policy["requested"]:
            print(
                "[SpatialFusion][Block] requested="
                f"{spatial_block_policy['block_size']}px "
                f"enabled={spatial_block_policy['enabled']} "
                f"fallback={spatial_block_policy['mode']} "
                f"reason={spatial_block_policy['reason']}"
            )

        # 1. Initialization and Work Resolution
        tile_h, tile_w = map(int, tile_size)
        num_images = len(images)
        work_res_h, work_res_w = ref_image_h, ref_image_w
        TARGET_MP = 12.5 * 1e6

        # Progress Calculation logic
        use_overall_progress = total_overall_images and total_overall_images > 0
        if use_overall_progress:
            # Batch processing: Hitung slot global untuk stack ini
            scope_start = (images_processed_so_far / total_overall_images) * 100.0
            scope_end = (
                (images_processed_so_far + num_images) / total_overall_images
            ) * 100.0
        else:
            # Single processing: Full 0-100
            scope_start, scope_end = 0.0, 100.0

        scope_width = scope_end - scope_start
        p_init = int(scope_start + scope_width * 0.05)
        p_align_start = unused_kwargs.get("align_progress_start", p_init)
        p_align_end = unused_kwargs.get(
            "align_progress_end", int(scope_start + scope_width * 0.40)
        )
        p_merge_start = unused_kwargs.get("merge_progress_start", p_align_end)
        p_merge_end = unused_kwargs.get(
            "merge_progress_end", int(scope_start + scope_width * 0.95)
        )
        pass_merge_range = (p_merge_start, p_merge_end)

        # Scale down logic
        if scale_down_factor != 1.0:
            if scale_down_factor < 1.0:
                work_res_h, work_res_w = int(ref_image_h * scale_down_factor), int(
                    ref_image_w * scale_down_factor
                )
                if update_progress:
                    update_progress(p_init, f"Downscale aktif: {scale_down_factor:.2f}")
            else:
                if update_progress:
                    update_progress(p_init, "Menggunakan resolusi asli (scale > 1.0)")
        elif (ref_image_h * ref_image_w) > TARGET_MP:
            scale_factor = np.sqrt(TARGET_MP / (ref_image_h * ref_image_w))
            work_res_h, work_res_w = int(ref_image_h * scale_factor), int(
                ref_image_w * scale_factor
            )
            if update_progress:
                update_progress(p_init, f"Auto-scale ke {scale_factor:.2f}x")

        work_res_h, work_res_w = (work_res_h // 2) * 2, (work_res_w // 2) * 2

        # ``phase2_fine_analysis`` retains ``base_window`` in its historical
        # graph signature, but the maintained AOT kernel derives the window
        # from ``tile_h/tile_w``.  Avoid constructing a redundant host Hanning
        # matrix here; the active pipeline passes ``None`` for this compatibility
        # argument and uses the scalar ABI value internally.
        base_window = None
        step_y, step_x = max(int(tile_h * (1 - overlap)), 1), max(
            int(tile_w * (1 - overlap)), 1
        )

        row_starts = np.arange(0, work_res_h - tile_h + 1, step_y, dtype=np.int32)
        if work_res_h > tile_h and (
            row_starts.size == 0 or row_starts[-1] != work_res_h - tile_h
        ):
            row_starts = np.append(row_starts, work_res_h - tile_h)
        row_starts = np.ascontiguousarray(np.unique(row_starts).astype(np.int32))

        col_starts = np.arange(0, work_res_w - tile_w + 1, step_x, dtype=np.int32)
        if work_res_w > tile_w and (
            col_starts.size == 0 or col_starts[-1] != work_res_w - tile_w
        ):
            col_starts = np.append(col_starts, work_res_w - tile_w)
        col_starts = np.ascontiguousarray(np.unique(col_starts).astype(np.int32))

        # There is deliberately one execution lane now.  ``process_in`` is
        # retained as a compatibility argument, but CPU/C++ dispatch is gone.
        process_in = "gpu"

        # 2. Execute Backend
        backend_args = {
            "images": images,
            "reference_image_float": reference_image_float,
            "ref_image_h": ref_image_h,
            "ref_image_w": ref_image_w,
            "ref_channels_buffer": ref_channels_buffer,
            "ref_dtype": ref_dtype,
            "work_res_h": work_res_h,
            "work_res_w": work_res_w,
            "tile_h": tile_h,
            "tile_w": tile_w,
            "overlap": overlap,
            "row_starts": row_starts,
            "col_starts": col_starts,
            "base_window": base_window,
            "motion_sensitivity": motion_sensitivity,
            "noise_offset_factor": noise_offset_factor,
            "update_progress": update_progress,
            "stop_requested": stop_requested,
            "pass_merge_range": pass_merge_range,
            "p_align_start": p_align_start,
            "p_align_end": p_align_end,
            "p_merge_start": p_merge_start,
            "is_linear_mode": is_linear_mode,
            "proxy_scale": proxy_scale,
            "images_processed_so_far": images_processed_so_far,
            "total_overall_images": total_overall_images,
            "enable_alignment": enable_alignment,
            "num_workers": num_workers,
            "alignment_tile_size": 32,
            "lib_path": lib_path,
            "return_raw": return_raw,
            **unused_kwargs,
        }

        if spatial_block_policy["enabled"]:
            halo = max(
                int(tile_h),
                int(tile_w),
                int(unused_kwargs.get("spatial_block_halo", 16)),
            )
            print(
                "[SpatialFusion][Block] native raw-sum path enabled: "
                f"size={spatial_block_policy['block_size']}px halo={halo}px"
            )
            res = self._process_image_blocks(
                images=images,
                reference_image_float=reference_image_float,
                ref_image_h=ref_image_h,
                ref_image_w=ref_image_w,
                backend_args=backend_args,
                block_size=spatial_block_policy["block_size"],
                halo=halo,
                update_progress=update_progress,
                stop_requested=stop_requested,
                return_raw=return_raw,
            )
        else:
            res = process_in_gpu(**backend_args)

        processed_frames, final_sum_img, sum_weight_full, _ = res
        if final_sum_img is None:
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)

        # 3. Finalization
        if stop_requested and stop_requested():
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)

        if processed_frames > 0 and return_raw:
            return (final_sum_img, sum_weight_full, processed_frames)

        # AOT GPU lane finalizes the normalized image before returning.
        final_image = final_sum_img

        if weight_of_each_image:
            return (final_image, sum_weight_full, processed_frames, [])
        else:
            return (final_image, sum_weight_full, processed_frames)
