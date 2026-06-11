import os
import gc
import time
import traceback
import sqlite3
import psutil
import h5py
import numpy as np
import cv2
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
from PySide6.QtCore import Qt

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.smart_fusion.smart_fusion_core import (
    SmartFusionProcessor,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_fusion import (
    SpatialFusionProcessor,
)

# --- EXTERNAL ALGORITHM UTILS ---
from pixel_refine_desktop.enhance_stack.core.algorithm.base_worker import (
    BaseAlgorithmWorker,
)
from pixel_refine_desktop.ui.resources.styles.stylesheet import PROGRESS_BAR
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    extract_all_metadata,
    normalize_image,
    preprocess_in_python,
    save_image,
    setup_balanced_batching,
    calculate_auto_scale,
    calculate_scale_from_gt_proxy,
    save_linear_dng,
    get_all_image_paths_for_single_process,
    load_images_from_paths,
    resize_all_with_padding,
    cleanup_old_hdf5_files,
    is_hdf5_cache_valid,
)

from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.similarity_parameter_settings import (
    load_similarity_config,
)


def get_ram_usage():
    """Returns the current RAM usage of the process in MiB."""
    process = psutil.Process()
    mem_info = process.memory_info()
    return mem_info.rss / 1024 / 1024


class DataProvider:
    """Handles data sourcing, batching, and image loading for the Similarity algorithm."""

    def __init__(self, db_path):
        self.db_path = db_path

    def get_all_image_paths_for_batch_process(self, batch_id):
        """Fetches all image paths for a specific batch from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT images.path 
                FROM batch_process_image
                JOIN images ON batch_process_image.image_id_batch = images.id
                WHERE batch_process_image.batch_id = ?
                ORDER BY batch_process_image.is_reference_batch DESC, images.path ASC
            """,
                (batch_id,),
            )
            return [row[0] for row in cursor.fetchall()]

    def setup_data_source_and_paths(self, single_process, batch_id):
        """Determines the data source (HDF5 or Raw paths) and prepares output metadata."""
        align_dir = os.path.join("database", "align")
        image_paths = []
        output_name_base = ""
        hdf5_path = ""

        if single_process:
            hdf5_path = os.path.join(align_dir, "aligned_images.h5")
            image_paths = get_all_image_paths_for_single_process(self.db_path)
            ref_name = (
                os.path.splitext(os.path.basename(image_paths[0]))[0]
                if image_paths
                else "single_process"
            )
            output_name_base = ref_name
        else:
            hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
            image_paths = self.get_all_image_paths_for_batch_process(batch_id)
            ref_name = (
                os.path.splitext(os.path.basename(image_paths[0]))[0]
                if image_paths
                else f"batch_{batch_id}"
            )
            output_name_base = ref_name

        # Hapus file HDF5 lama selain file target saat ini untuk menghemat ruang HDD
        cleanup_old_hdf5_files(hdf5_path)

        # --- Validasi cache HDF5 berdasarkan referensi image ---
        # Jika HDF5 ada tapi referensi image berubah (misal batch diisi ulang dengan
        # gambar berbeda), hapus cache lama agar alignment dijalankan ulang.
        ref_image_path_current = image_paths[0] if image_paths else ""
        if os.path.exists(hdf5_path) and ref_image_path_current:
            if not is_hdf5_cache_valid(hdf5_path, ref_image_path_current):
                try:
                    os.remove(hdf5_path)
                    print(
                        f"[CacheValidation] Cache HDF5 dihapus karena referensi berubah: {hdf5_path}"
                    )
                except Exception as e_del:
                    print(f"[CacheValidation] Gagal menghapus cache HDF5: {e_del}")

        data_source = hdf5_path if os.path.exists(hdf5_path) else image_paths

        total_images = 0
        if isinstance(data_source, str) and data_source.endswith(".h5"):
            print(language_config.PROCESSING_IMAGE_FROM_HDF5.format(data_source))
            try:
                with h5py.File(data_source, "r") as f:
                    total_images = len(f.keys())
            except Exception as e_h5:
                raise IOError(f"Gagal membaca file HDF5: {e_h5}")
        elif isinstance(data_source, list):
            total_images = len(data_source)

        return data_source, image_paths, output_name_base, total_images

    @staticmethod
    def load_images_for_batch(
        data_source,
        batch_indices,
        stop_requested=None,
        linear_mode=True,
        capture_ref_proxy=False,
        alignment_mode=False,
        update_progress=None,
        progress_start=0,
        progress_end=100,
    ):
        """Loads a specific batch of images from HDF5 or filesystem."""
        batch_start, batch_end = batch_indices
        batch_images = []
        ref_proxy = None

        if isinstance(data_source, str) and data_source.endswith(".h5"):
            with h5py.File(data_source, "r") as h5f:
                keys = list(h5f.keys())[batch_start:batch_end]
                batch_images = [
                    np.array(h5f[key])
                    for key in keys
                    if not (stop_requested and stop_requested())
                ]
        elif isinstance(data_source, list):
            batch_paths = data_source[batch_start:batch_end]
            load_res = load_images_from_paths(
                batch_paths,
                stop_requested,
                linear_mode=linear_mode,
                capture_ref_proxy=capture_ref_proxy,
                alignment_mode=alignment_mode,
                update_progress=update_progress,
                progress_start=progress_start,
                progress_end=progress_end,
            )

            if capture_ref_proxy and isinstance(load_res, tuple):
                batch_images, ref_proxy = load_res
            else:
                batch_images = load_res

            # Automatic resizing for consistency
            resize_res = resize_all_with_padding(
                batch_images,
                method="preserve",
                stop_requested=stop_requested,
                force_even=True,
            )
            if resize_res and resize_res[0]:
                batch_images = resize_res[0]

        if capture_ref_proxy:
            return batch_images, ref_proxy

        return batch_images


class SimilarityAlgorithm:
    """
    Main Orchestrator for the Similarity Merging algorithm.
    Coordinates between Smart Fusion (AI) and Spatial Fusion (C++/Taichi).
    """

    def __init__(self, db_path, hdf5_path=None):
        self.db_path = db_path
        self.data_provider = DataProvider(db_path)
        self.smart_processor = SmartFusionProcessor()
        self.spatial_processor = SpatialFusionProcessor()

    def close(self):
        """Cleanup resources and close AI sessions."""
        if self.smart_processor:
            self.smart_processor.release_sessions()
        self.smart_processor = None
        gc.collect()

    def get_all_image_paths_for_batch_process(self, batch_id):
        """Legacy wrapper for DataProvider."""
        return self.data_provider.get_all_image_paths_for_batch_process(batch_id)

    def similarity_mnfr(
        self,
        images,
        tile_size=None,
        overlap=None,
        motion_sensitivity=None,
        noise_offset_factor=None,
        update_progress=None,
        stop_requested=None,
        save_weight_map_path=None,
        num_workers=None,
        total_overall_images=None,
        images_processed_so_far=0,
        save_temporal_std_path=None,
        weight_of_each_image=False,
        ref_image_override=None,
        return_raw=False,
        is_linear_mode=False,
        proxy_scale=1.0,
        **merging_kwargs,
    ):
        """Entry point for the merging algorithm."""
        if not isinstance(images, list) or (
            not images and merging_kwargs.get("data_source") is None
        ):
            raise ValueError(language_config.IMAGE_DATA_MUST_BE_VALID)

        ref_image = ref_image_override if ref_image_override is not None else images[0]
        dtype_ref = ref_image.dtype
        h_ref, w_ref = ref_image.shape[:2]
        channels_ref_orig = ref_image.shape[2] if ref_image.ndim == 3 else 1

        reference_image_float = normalize_image(ref_image, dtype_ref)
        h_ref_norm, w_ref_norm, _ = reference_image_float.shape

        # Common arguments for booth backends
        common_args = {
            "images": images,
            "ref_image_h": h_ref_norm,
            "ref_image_w": w_ref_norm,
            "ref_channels_buffer": 3,
            "ref_dtype": dtype_ref,
            "reference_image_float": reference_image_float,
            "update_progress": update_progress,
            "stop_requested": stop_requested,
            "total_overall_images": total_overall_images,
            "images_processed_so_far": images_processed_so_far,
            "weight_of_each_image": weight_of_each_image,
            "return_raw": return_raw,
            "is_linear_mode": is_linear_mode,
            "proxy_scale": proxy_scale,
        }
        common_args.update(merging_kwargs)

        if stop_requested and stop_requested():
            out_shape = (
                (h_ref, w_ref)
                if channels_ref_orig == 1
                else (h_ref, w_ref, channels_ref_orig)
            )
            return np.zeros(out_shape, dtype=dtype_ref), None, 0

        # merging_mode = merging_kwargs.get("merging_mode", "smart")
        merging_mode = merging_kwargs.get("merging_mode", "spatial")

        # Determine Backend
        if merging_mode == "smart":
            results = self.smart_processor.process(
                tile_size=(320, 320),
                overlap=0.10,
                num_workers=(
                    num_workers
                    if num_workers is not None
                    else merging_kwargs.get("similarity_spatial_num_workers", 1)
                ),
                noise_alpha=merging_kwargs.get("similarity_smart_noise_alpha", 1.0),
                **common_args,
            )
        else:
            results = self.spatial_processor.process(
                tile_size=(
                    tile_size
                    if tile_size is not None
                    else merging_kwargs.get("tile_size")
                ),
                overlap=(
                    overlap if overlap is not None else merging_kwargs.get("overlap")
                ),
                motion_sensitivity=(
                    motion_sensitivity
                    if motion_sensitivity is not None
                    else merging_kwargs.get("motion_sensitivity")
                ),
                noise_offset_factor=(
                    noise_offset_factor
                    if noise_offset_factor is not None
                    else merging_kwargs.get("noise_offset_factor")
                ),
                num_workers=(
                    num_workers
                    if num_workers is not None
                    else merging_kwargs.get("similarity_spatial_num_workers", 1)
                ),
                **common_args,
            )

        if results is None:
            out_shape = (
                (h_ref, w_ref)
                if channels_ref_orig == 1
                else (h_ref, w_ref, channels_ref_orig)
            )
            return np.zeros(out_shape, dtype=dtype_ref), None, 0

        final_img_norm, final_weight, processed_frames = (
            results[0],
            results[1],
            results[2],
        )

        # Scaling back to original bit-depth
        if processed_frames > 0 and final_img_norm is not None:
            if return_raw:
                return results

            # Perform normalization if not returning raw (since processor now returns raw sums)
            if final_weight is not None:
                valid_mask = final_weight > 1e-6
                normalized = np.zeros_like(final_img_norm)
                np.divide(
                    final_img_norm,
                    final_weight[:, :, np.newaxis],
                    out=normalized,
                    where=valid_mask[:, :, np.newaxis],
                )
                final_img_norm = normalized

            scale_val = np.float32(np.iinfo(dtype_ref).max)
            final_img_scaled = final_img_norm * scale_val
            if channels_ref_orig == 1:
                final_img_out = np.mean(final_img_scaled, axis=2)
            else:
                final_img_out = final_img_scaled

            final_img_output = np.clip(
                final_img_out, 0, np.iinfo(dtype_ref).max
            ).astype(dtype_ref)
            return final_img_output, final_weight, processed_frames

        return np.zeros((h_ref, w_ref, channels_ref_orig), dtype=dtype_ref), None, 0


def main(
    db_path,
    update_progress=None,
    stop_requested=None,
    single_process=None,
    batch_id=None,
    save_final_weight_map=False,
    progress_bar=None,
):
    """Main execution block."""
    start_time = time.perf_counter()
    try:
        if update_progress:
            update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        general_settings = load_similarity_config()
        processor = SimilarityAlgorithm(db_path)
        data_provider = processor.data_provider

        # Setup parameters
        tile_val = general_settings.get("similarity_spatial_tile_size", 12)
        extra_params = {
            "tile_size": (tile_val, tile_val),
            "overlap": general_settings.get("similarity_spatial_overlap_percent", 0.28),
            "motion_sensitivity": general_settings.get(
                "similarity_spatial_motion_sensitivity", 150.00
            ),
            "noise_offset_factor": general_settings.get(
                "similarity_spatial_noise_mad_offset_factor", 0.15
            ),
            "similarity_spatial_num_workers": general_settings.get(
                "similarity_spatial_num_workers", 1
            ),
            "similarity_smart_noise_alpha": general_settings.get(
                "similarity_smart_noise_alpha", 1.0
            ),
            "enable_linear_mode": general_settings.get("enable_linear_mode", False),
        }

        # Calculate effective alpha for Smart Noise Awareness
        extra_params["similarity_smart_noise_aware_enable"] = general_settings.get(
            "similarity_smart_noise_aware_enable", True
        )
        extra_params["similarity_smart_noise_strength"] = general_settings.get(
            "similarity_smart_noise_strength", 100.0
        )

        custom_lib = general_settings.get("similarity_lib_path")
        if custom_lib:
            extra_params["lib_path"] = custom_lib

        # Setup data
        data_source, image_paths, output_name_base, total_images = (
            data_provider.setup_data_source_and_paths(single_process, batch_id)
        )
        if not total_images:
            if update_progress:
                update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return

        # Output paths
        output_folder = "database/stack"
        os.makedirs(output_folder, exist_ok=True)
        safe_name = (
            "".join(
                c for c in output_name_base if c.isalnum() or c in ("_", "-")
            ).rstrip()
            or "stack"
        )
        output_path = os.path.join(output_folder, f"{safe_name}_similarity.tif")

        # Linear mode detection
        is_linear_mode = False
        if extra_params["enable_linear_mode"] and image_paths:
            _, ext = os.path.splitext(image_paths[0])
            if ext.lower() in [
                ".dng",
                ".cr2",
                ".cr3",
                ".nef",
                ".arw",
            ]:  # Simplified raw check
                is_linear_mode = True

        # Load reference
        ref_res = data_provider.load_images_for_batch(
            data_source,
            (0, 1),
            stop_requested,
            linear_mode=is_linear_mode,
            capture_ref_proxy=is_linear_mode,
        )
        if is_linear_mode and isinstance(ref_res, tuple):
            reference_image, ref_proxy_gt = ref_res
        elif isinstance(ref_res, list) and len(ref_res) > 0:
            reference_image = ref_res[0]
            ref_proxy_gt = None
        else:
            reference_image = None
            ref_proxy_gt = None

        # Auto-scale for Linear Mode
        proxy_scale = 1.0
        if (
            is_linear_mode
            and reference_image is not None
            and hasattr(reference_image, "dtype")
        ):
            if ref_proxy_gt is not None:
                proxy_scale = calculate_scale_from_gt_proxy(
                    reference_image, ref_proxy_gt, reference_image.dtype
                )
            else:
                proxy_scale = calculate_auto_scale(
                    normalize_image(reference_image, reference_image.dtype),
                    target_mean=0.25,
                )

        # Generate unique session ID for this stack run
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        stack_session_id = f"{output_name_base}_{timestamp}"

        reference_image_float = normalize_image(reference_image, reference_image.dtype)
        h_ref_norm, w_ref_norm = reference_image_float.shape[:2]

        # Check if we can stream from H5 with zero-allocation buffer reuse
        is_hdf5 = isinstance(data_source, str) and data_source.endswith(".h5")

        just_aligned = False
        if not is_hdf5:
            just_aligned = True
            if update_progress:
                update_progress(
                    0,
                    "Menjalankan alignment awal (Taichi GPU) untuk membuat file HDF5...",
                )

            hdf5_path = (
                "database/align/aligned_images.h5"
                if single_process
                else f"database/align/aligned_image_batch_{batch_id}.h5"
            )
            os.makedirs(os.path.dirname(hdf5_path), exist_ok=True)

            # Load and resize images for alignment in full-res RGB (Progress: 0% to 25%)
            images_for_align = data_provider.load_images_for_batch(
                image_paths,
                (0, len(image_paths)),
                stop_requested,
                linear_mode=is_linear_mode,
                alignment_mode=False,
                update_progress=update_progress,
                progress_start=0,
                progress_end=25,
            )

            with h5py.File(hdf5_path, "w") as h5f:
                from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
                    save_to_hdf5,
                    extract_exif,
                )

                # Simpan path referensi image ke root attrs HDF5 untuk validasi cache di masa depan
                h5f.attrs["ref_image_path"] = image_paths[0] if image_paths else ""

                save_to_hdf5(
                    h5f, "image_0", reference_image, extract_exif(image_paths[0])
                )

                from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_pipeline import (
                    process_in_gpu,
                )

                process_in_gpu(
                    images=images_for_align,
                    reference_image_float=reference_image_float,
                    ref_image_h=h_ref_norm,
                    ref_image_w=w_ref_norm,
                    ref_dtype=reference_image.dtype,
                    work_res_h=h_ref_norm,
                    work_res_w=w_ref_norm,
                    tile_h=extra_params.get("tile_size", (16, 16))[0],
                    tile_w=extra_params.get("tile_size", (16, 16))[1],
                    update_progress=update_progress,
                    stop_requested=stop_requested,
                    p_align_start=25,
                    p_align_end=50,
                    is_linear_mode=is_linear_mode,
                    proxy_scale=proxy_scale,
                    h5_file_handle=h5f,
                    image_paths=image_paths,
                    reference_image=reference_image,
                    alignment_only=True,
                    optical_flow_type="alignment_tile",
                )

            del images_for_align
            gc.collect()

            # Re-check data source to load the newly created H5 file
            data_source, image_paths, output_name_base, total_images = (
                data_provider.setup_data_source_and_paths(single_process, batch_id)
            )
            is_hdf5 = isinstance(data_source, str) and data_source.endswith(".h5")

        global_sum_img, global_sum_weight, global_total_frames = None, None, 0

        if is_hdf5:
            # Disable internal alignment since images are already aligned in HDF5
            extra_params["enable_alignment"] = False

            # Pass custom progress range for merging (50-95% if aligned just now, 0-95% if already aligned)
            extra_params["merge_progress_start"] = 50 if just_aligned else 0
            extra_params["merge_progress_end"] = 95

            # RUN ALGORITHM once on the entire HDF5 data source using GPU Streaming!
            batch_res = processor.similarity_mnfr(
                images=[],  # Empty list since we stream directly from H5 on GPU
                ref_image_override=reference_image,
                total_overall_images=total_images,
                images_processed_so_far=0,
                is_linear_mode=is_linear_mode,
                proxy_scale=proxy_scale,
                update_progress=update_progress,
                stop_requested=stop_requested,
                return_raw=True,
                save_prefix=stack_session_id,
                harvest_alignment=extra_params.get("harvest_alignment", False),
                data_source=data_source,  # Pass H5 path for streaming
                **extra_params,
            )

            if batch_res is not None and len(batch_res) >= 3:
                global_sum_img = batch_res[0]
                global_sum_weight = batch_res[1]
                global_total_frames = batch_res[2]
        else:
            # Fallback for CPU / non-H5 paths
            batch_plan = setup_balanced_batching(
                total_images, language_config, max_batch_size=15
            )
            num_batches = len(batch_plan)
            batch_share = 95.0 / num_batches

            for batch_idx, (b_start, b_end) in enumerate(batch_plan):
                if stop_requested and stop_requested():
                    break

                b_start_prog = batch_idx * batch_share
                b_end_prog = (batch_idx + 1) * batch_share
                load_end_prog = b_start_prog + batch_share * 0.15

                current_batch_images = data_provider.load_images_for_batch(
                    data_source,
                    (b_start, b_end),
                    stop_requested,
                    linear_mode=is_linear_mode,
                    update_progress=update_progress,
                    progress_start=int(b_start_prog),
                    progress_end=int(load_end_prog),
                )
                if not current_batch_images:
                    continue

                # Pass custom progress range for merging this batch
                extra_params["merge_progress_start"] = int(load_end_prog)
                extra_params["merge_progress_end"] = int(b_end_prog)

                # RUN ALGORITHM
                batch_res = processor.similarity_mnfr(
                    current_batch_images,
                    ref_image_override=reference_image,
                    total_overall_images=total_images,
                    images_processed_so_far=b_start,
                    is_linear_mode=is_linear_mode,
                    proxy_scale=proxy_scale,
                    update_progress=update_progress,
                    stop_requested=stop_requested,
                    return_raw=True,
                    save_prefix=stack_session_id,  # [UNIQUE] Session-based prefix
                    harvest_alignment=extra_params.get(
                        "harvest_alignment", False
                    ),  # [NEW] Pass from params
                    **extra_params,
                )

                if batch_res is not None and len(batch_res) >= 3:
                    b_img, b_weight, b_frames = batch_res[0], batch_res[1], batch_res[2]
                    if global_sum_img is None:
                        global_sum_img = b_img if b_img is not None else None
                        global_sum_weight = b_weight if b_weight is not None else None
                    else:
                        if b_img is not None:
                            global_sum_img += b_img
                        if b_weight is not None:
                            global_sum_weight += b_weight
                    global_total_frames += b_frames

                # Explicit cleanup after batch accumulation
                del batch_res
                if "b_img" in locals():
                    del b_img
                if "b_weight" in locals():
                    del b_weight

                del current_batch_images
                gc.collect()

        # FINAL FUSION
        if global_sum_img is not None and global_total_frames > 0:
            if update_progress:
                update_progress(95, "Finalizing fusion...")

            valid_mask = global_sum_weight > 1e-6
            final_normalized = np.zeros_like(global_sum_img)
            np.divide(
                global_sum_img,
                global_sum_weight[:, :, np.newaxis],
                out=final_normalized,
                where=valid_mask[:, :, np.newaxis],
            )

            ref_float = normalize_image(reference_image, reference_image.dtype)
            final_normalized[~valid_mask] = ref_float[~valid_mask]

            # Adaptive Box-Filter High-Frequency Denoise
            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
                estimate_noise_in_python,
            )

            ref_gray_for_noise = cv2.cvtColor(ref_float, cv2.COLOR_BGR2GRAY)
            est_noise = estimate_noise_in_python(ref_gray_for_noise)

            if est_noise >= 0.20:
                print(
                    f"[Denoise] Moderate/High noise detected (sigma={est_noise:.4f}). Applying Adaptive High-Frequency Box-Filter Denoise..."
                )
                # 1. Low-frequency part (LF) via box filter
                lf = cv2.boxFilter(
                    final_normalized,
                    ddepth=-1,
                    ksize=(3, 3),
                    borderType=cv2.BORDER_REFLECT,
                )
                # 2. High-frequency part (HF)
                hf = final_normalized - lf
                # 3. Suppress noise in HF based on noise strength (higher noise = more suppression)
                # Map est_noise range [0.20, 0.80] to alpha range [0.15, 0.45]
                alpha = np.clip(0.15 + (est_noise - 0.20) * 0.5, 0.15, 0.45)
                hf_clean = hf * (1.0 - alpha)
                # 4. Reconstruct
                final_normalized = lf + hf_clean
                print(
                    f"  [Denoise] Damped high-frequency noise by {alpha*100:.1f}% without affecting structures."
                )

            max_v = np.iinfo(reference_image.dtype).max
            final_img = np.clip(final_normalized * max_v, 0, max_v).astype(
                reference_image.dtype
            )

            # SAVE
            if is_linear_mode:
                output_path = save_linear_dng(
                    final_img,
                    os.path.splitext(output_path)[0] + ".dng",
                    reference_image_path=image_paths[0],
                )
            else:
                save_image(final_img, output_path, reference_image_path=image_paths[0])

            if update_progress:
                update_progress(
                    100, f"Process Finished: {os.path.basename(output_path)}"
                )

    except Exception as e:
        print(f"Error in Similarity main loop: {e}")
        traceback.print_exc()
        if update_progress:
            update_progress(0, f"Error: {str(e)}")
    finally:
        if "start_time" in locals():
            elapsed = time.perf_counter() - start_time
            print(f"\n[Benchmark] Seluruh proses selesai dalam {elapsed:.2f} detik.\n")
        # --- FINAL CLEANUP: Ensure RAM is returned to OS ---
        print("[Similarity] Final cleanup...")

        # Explicitly clear AI sessions and processor
        if "processor" in locals():
            processor.close()
            del processor

        # Delete large buffers
        if "global_sum_img" in locals():
            del global_sum_img
        if "global_sum_weight" in locals():
            del global_sum_weight
        if "reference_image" in locals():
            del reference_image

        gc.collect()


def running_similarity(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
):
    """UI Entry point."""

    # ==========================================================
    # KONDISI 1: MODE BATCH (TANPA GUI)
    # ==========================================================
    if batch_id is not None and progress_callback is not None:
        try:
            main(
                db_path="pixel_refine_database.db",
                update_progress=progress_callback,
                stop_requested=stop_callback,
                single_process=False,
                batch_id=batch_id,
            )
        except Exception as e:
            raise e
        return

    # ==========================================================
    # KONDISI 2: MODE SINGLE (DENGAN GUI DIALOG)
    # ==========================================================
    process_finished = False
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_SIMILARITY)
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.CustomizeWindowHint
        | Qt.WindowType.WindowTitleHint
        | Qt.WindowType.WindowCloseButtonHint
    )

    layout = QVBoxLayout(dialog)
    label = QLabel(language_config.WINDOW_START_PROCESSING)
    layout.addWidget(label)

    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setStyleSheet(PROGRESS_BAR)
    layout.addWidget(progress_bar)

    worker = BaseAlgorithmWorker(
        main,
        "pixel_refine_database.db",
        single_process=single_process,
        batch_id=batch_id,
    )

    worker.progress_updated.connect(
        lambda progress, message: (
            progress_bar.setValue(progress),
            label.setText(message),
        )
    )

    def finish_handler():
        nonlocal process_finished
        process_finished = True
        dialog.close()
        worker.quit()
        worker.wait()

    worker.finished.connect(finish_handler)

    def error_handler(error):
        QMessageBox.critical(
            dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=error)
        )
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    def on_dialog_close(event):
        if process_finished:
            event.accept()
        elif worker.isRunning():
            reply = QMessageBox.question(
                dialog,
                "Cancel Process",
                language_config.CANCEL_PROCESSING,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                worker.stop()
                worker.quit()
                worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    dialog.closeEvent = on_dialog_close
    worker.start()
    dialog.exec()


if __name__ == "__main__":
    main("pixel_refine_database.db")
