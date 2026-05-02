import os
import gc
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
        if not isinstance(images, list) or not images:
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
            return np.zeros(out_shape, dtype=dtype_ref), None, []

        merging_mode = merging_kwargs.get("merging_mode", "smart")
        # merging_mode = merging_kwargs.get("merging_mode", "spatial")

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
            return np.zeros(out_shape, dtype=dtype_ref), None, []

        final_img_norm, final_weight, processed_frames = (
            results[0],
            results[1],
            results[2],
        )

        # Scaling back to original bit-depth
        if processed_frames > 0 and final_img_norm is not None:
            if return_raw:
                return results

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
    try:
        if update_progress:
            update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        general_settings = load_similarity_config()
        processor = SimilarityAlgorithm(db_path)
        data_provider = processor.data_provider

        # Setup parameters
        tile_val = general_settings.get("similarity_spatial_tile_size", 16)
        extra_params = {
            "tile_size": (tile_val, tile_val),
            "overlap": general_settings.get("similarity_spatial_overlap_percent", 0.3),
            "motion_sensitivity": general_settings.get(
                "similarity_spatial_motion_sensitivity", 150.00
            ),
            "noise_offset_factor": general_settings.get(
                "similarity_spatial_noise_mad_offset_factor", 1.0
            ),
            "similarity_spatial_num_workers": general_settings.get(
                "similarity_spatial_num_workers", 1
            ),
            "similarity_smart_noise_alpha": general_settings.get(
                "similarity_smart_noise_alpha", 1.0
            ),
            "enable_linear_mode": general_settings.get("enable_linear_mode", True),
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
        if extra_params.get("enable_linear_mode", True) and image_paths:
            _, ext = os.path.splitext(image_paths[0])
            if ext.lower() in [".dng", ".cr2", ".cr3", ".nef", ".arw", ".orf", ".raf"]:
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
            ref_image_list, ref_proxy_gt = ref_res
            reference_image = ref_image_list[0] if ref_image_list else None
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

        # Batch Processing Loop
        batch_plan = setup_balanced_batching(
            total_images, language_config, max_batch_size=8
        )
        global_sum_img, global_sum_weight, global_total_frames = None, None, 0

        for batch_num, (b_start, b_end) in enumerate(batch_plan, 1):
            if stop_requested and stop_requested():
                break

            current_batch_images = data_provider.load_images_for_batch(
                data_source,
                (b_start, b_end),
                stop_requested,
                linear_mode=is_linear_mode,
            )
            if not current_batch_images:
                continue

            # RUN ALGORITHM
            print(f"[DEBUG] Memulai processing Batch {batch_num}/{len(batch_plan)} (Range: {b_start}-{b_end})...", flush=True)
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
                **extra_params,
            )
            print(f"[DEBUG] Batch {batch_num} selesai diproses.", flush=True)

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

            # [STABILITY] Safe cleanup after batch accumulation
            if 'batch_res' in locals():
                del batch_res
            if 'current_batch_images' in locals():
                del current_batch_images
            if 'b_img' in locals():
                del b_img
            if 'b_weight' in locals():
                del b_weight
                
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

            max_v = np.iinfo(reference_image.dtype).max
            final_img = np.clip(final_normalized * max_v, 0, max_v).astype(
                reference_image.dtype
            )

            # SAVE
            # Always use save_image (TIFF) for consistency and to match UI expectations.
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
