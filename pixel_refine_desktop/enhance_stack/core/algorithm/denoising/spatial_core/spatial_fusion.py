import os
import numpy as np
import psutil
from .spatial_pipeline import process_in_gpu



def get_ram_usage():
    """Returns the current RAM usage of the process in MiB."""
    process = psutil.Process()
    mem_info = process.memory_info()
    return mem_info.rss / 1024 / 1024


class SpatialFusionProcessor:
    """Handles Spatial Fusion exclusively through the Taichi AOT pipeline."""

    def __init__(self):
        pass

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

        # Tiling. A standard Hanning window is exactly zero at tile edges; when
        # the first/last tile touches the image border, that creates black
        # borders in the final normalization. Keep the feathered shape but clamp
        # it to a small positive floor so every frame edge remains covered.
        win_y = np.maximum(np.hanning(tile_h).astype(np.float32), 1e-4)
        win_x = np.maximum(np.hanning(tile_w).astype(np.float32), 1e-4)
        base_window = np.outer(win_y, win_x).astype(np.float32)
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
