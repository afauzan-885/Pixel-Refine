import os
import gc
import time
import traceback
import sqlite3
import h5py
import numpy as np
import cv2
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
from PySide6.QtCore import Qt

from pixel_refine_desktop.enhance_stack.core.algorithm.base_worker import (
    BaseAlgorithmWorker,
)
from resources.styles.stylesheet import PROGRESS_BAR
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    extract_all_metadata,
    normalize_image,
    save_image,
    setup_balanced_batching,
    get_all_image_paths_for_single_process,
    load_images_from_paths,
    resize_all_with_padding,
    cleanup_old_hdf5_files,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
import taichi_library.taichi_algorithm as ta
from .weighted_sr import TaichiWSR

class WeightedSRAlgorithm:

    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

    def get_all_image_paths_for_batch_process(self, batch_id):
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

    def compute_spatial_weight_maps(self, lr_frames, noise_std=0.015, sensitivity=120.0):
        """
        Computes Spatial Weight Maps (W_k) relative to reference frame Y_ref (lr_frames[0]).
        Matches the concept of tile rejection / ghosting suppression using Local-MSE window calculation.
        """
        # Handle potential 4D shape: (num_frames, h, w, channels)
        if lr_frames.ndim == 4:
            num_frames, h, w, channels = lr_frames.shape
            # Create a 3D grayscale representation for weight calculation
            lr_gray = np.zeros((num_frames, h, w), dtype=np.float32)
            for k in range(num_frames):
                lr_gray[k] = cv2.cvtColor(lr_frames[k], cv2.COLOR_RGB2GRAY)
            ref_frame = lr_gray[0]
            weight_maps = np.ones((num_frames, h, w), dtype=np.float32)
        else:
            num_frames, h, w = lr_frames.shape
            ref_frame = lr_frames[0]
            weight_maps = np.ones_like(lr_frames)
            lr_gray = lr_frames
        
        # Calculate local window differences
        for k in range(1, num_frames):
            diff = lr_gray[k] - ref_frame

            # Compute Local MSE via Gaussian Blur on GPU
            local_mse = ta.gaussian(diff * diff, (5, 5), sigmaX=1.0)
            if hasattr(local_mse, "to_numpy"):
                local_mse = local_mse.to_numpy()
            
            # Tile rejection mapping formula
            # Areas with high Local-MSE (movement/misalignment) get weights near 0
            w_k = np.exp(-local_mse / (noise_std * noise_std * 2.0))
            # Smooth out and clamp
            w_k = np.clip(w_k * sensitivity, 0.0, 1.0)
            weight_maps[k] = w_k
            
        return weight_maps


    def run_super_resolution(
        self,
        images,
        scale=2,
        num_iterations=120,
        update_progress=None,
        stop_requested=None,
        total_overall_images=None,
        images_processed_so_far=0,
    ):
        if not isinstance(images, list) or not images:
            return None

        import taichi as ti
        from taichi_library.taichi_algorithm.common import generate_hanning_window_2d
        # Reset and initialize Taichi JIT on this background worker thread
        ti.reset()
        use_gpu = True
        try:
            ti.init(arch=ti.vulkan)
        except Exception:
            ti.init(arch=ti.cpu)
            use_gpu = False

        try:
            ref_image = images[0]
            dtype_ref = ref_image.dtype
            h_ref, w_ref = ref_image.shape[:2]
            
            is_color = ref_image.ndim == 3 and ref_image.shape[2] == 3
            if is_color:
                # Convert reference image to YCrCb to extract Cb and Cr channels
                ref_ycbcr = cv2.cvtColor(ref_image, cv2.COLOR_RGB2YCrCb)
                _, cr_ref, cb_ref = cv2.split(ref_ycbcr)
            
            # Normalize to float32 range [0.0, 1.0]
            lr_frames = []
            for img in images:
                if stop_requested and stop_requested():
                    return None
                if is_color:
                    # Convert to YCrCb and extract Y (luminance) channel for super resolution
                    img_yuv = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
                    y_channel = img_yuv[:, :, 0]
                    norm_img = normalize_image(y_channel, dtype_ref)[:, :, 0]
                else:
                    norm_img = normalize_image(img, dtype_ref)
                    if norm_img.ndim == 3:
                        norm_img = norm_img[:, :, 0]
                lr_frames.append(norm_img)
                
            lr_frames = np.array(lr_frames)
            num_frames = len(lr_frames)
            
            # 1. Estimate real sub-pixel shifts using Taichi AOT Phase Correlation
            from taichi_library.taichi_aot import phase_correlation
            if update_progress:
                update_progress(3, "Estimating sub-pixel shifts...")
                
            shifts = np.zeros((num_frames, 2), dtype=np.float32)
            for k in range(1, num_frames):
                if stop_requested and stop_requested():
                    return None
                dx, dy, _ = phase_correlation(lr_frames[0], lr_frames[k], use_hanning=True)
                shifts[k] = [dy * scale, dx * scale]

            # 2. Compute Spatial Weight Maps for Ghosting Rejection
            if update_progress:
                update_progress(5, "Calculating spatial similarity weight maps...")
            weight_maps = self.compute_spatial_weight_maps(lr_frames)

            # 3. Setup Tiling and Accumulators
            lr_h, lr_w = lr_frames[0].shape[:2]
            hr_h, hr_w = lr_h * scale, lr_w * scale
            
            hr_accumulator = np.zeros((hr_h, hr_w), dtype=np.float32)
            weight_accumulator = np.zeros((hr_h, hr_w), dtype=np.float32)
            
            tile_size = 512
            overlap = 0.3
            
            tile_h = min(tile_size, lr_h)
            tile_w = min(tile_size, lr_w)
            
            step_y = int(tile_h * (1.0 - overlap)) if tile_h < lr_h else lr_h
            step_x = int(tile_w * (1.0 - overlap)) if tile_w < lr_w else lr_w
            
            y_starts = []
            y = 0
            while y + tile_h <= lr_h:
                y_starts.append(y)
                if y + tile_h == lr_h:
                    break
                y = min(y + step_y, lr_h - tile_h)
                
            x_starts = []
            x = 0
            while x + tile_w <= lr_w:
                x_starts.append(x)
                if x + tile_w == lr_w:
                    break
                x = min(x + step_x, lr_w - tile_w)
                
            total_tiles = len(y_starts) * len(x_starts)
            processed_tiles = 0

            # 4. Iterate over tiles
            for y_start in y_starts:
                for x_start in x_starts:
                    if stop_requested and stop_requested():
                        return None
                        
                    # Re-initialize Taichi JIT context for this tile
                    ti.reset()
                    if use_gpu:
                        try:
                            ti.init(arch=ti.vulkan)
                        except Exception:
                            ti.init(arch=ti.cpu)
                            use_gpu = False
                    else:
                        ti.init(arch=ti.cpu)
                        
                    tile_lr = lr_frames[:, y_start:y_start+tile_h, x_start:x_start+tile_w]
                    tile_weight = weight_maps[:, y_start:y_start+tile_h, x_start:x_start+tile_w]
                    
                    tile_hr_h = tile_h * scale
                    tile_hr_w = tile_w * scale
                    
                    # Run Solver for current tile
                    try:
                        solver = TaichiWSR(
                            lr_shape=(tile_h, tile_w),
                            hr_shape=(tile_hr_h, tile_hr_w),
                            num_frames=num_frames,
                            scale=scale,
                            alpha=0.7,
                            beta=0.005,
                            btv_window=2
                        )
                        solver.set_lr_data(tile_lr, tile_weight, shifts)
                    except RuntimeError as e:
                        if use_gpu:
                            print("VRAM Allocation failed. Falling back to CPU backend for tiling...", flush=True)
                            ti.reset()
                            ti.init(arch=ti.cpu)
                            use_gpu = False
                            solver = TaichiWSR(
                                lr_shape=(tile_h, tile_w),
                                hr_shape=(tile_hr_h, tile_hr_w),
                                num_frames=num_frames,
                                scale=scale,
                                alpha=0.7,
                                beta=0.005,
                                btv_window=2
                            )
                            solver.set_lr_data(tile_lr, tile_weight, shifts)
                        else:
                            raise e
                            
                    # Set initial estimate via bicubic upsampling
                    init_hr = ta.resize(tile_lr[0], (tile_hr_w, tile_hr_h), interpolation=ta.INTER_CUBIC)
                    if hasattr(init_hr, "to_numpy"):
                        init_hr = init_hr.to_numpy()
                    if init_hr.ndim == 3:
                        init_hr = init_hr[:, :, 0]
                        
                    solver.set_initial_hr(init_hr)
                    
                    # Iterative Optimization Loop for Tile
                    for step_idx in range(num_iterations):
                        if stop_requested and stop_requested():
                            return None
                        if step_idx > 0 and step_idx % 25 == 0:
                            solver.beta *= 0.90
                        solver.step(lam=0.001)
                        
                    tile_hr_res = solver.get_hr_image()
                    
                    # Generate Hanning window for tile stitching
                    win = generate_hanning_window_2d((tile_hr_h, tile_hr_w))
                    if hasattr(win, "to_numpy"):
                        win = win.to_numpy()
                        
                    # Accumulate to global high-resolution buffers
                    y_hr_start = y_start * scale
                    x_hr_start = x_start * scale
                    hr_accumulator[y_hr_start:y_hr_start+tile_hr_h, x_hr_start:x_hr_start+tile_hr_w] += tile_hr_res * win
                    weight_accumulator[y_hr_start:y_hr_start+tile_hr_h, x_hr_start:x_hr_start+tile_hr_w] += win
                    
                    # Release GPU JIT VRAM immediately for this tile
                    del solver
                    del tile_hr_res
                    del win
                    ti.reset()
                    gc.collect()
                    
                    processed_tiles += 1
                    if update_progress:
                        prog_val = 10 + int((processed_tiles / total_tiles) * 85)
                        update_progress(prog_val, f"Processing super-resolution tile {processed_tiles}/{total_tiles}...")

            # 5. Final Stitching normalization and scaling
            if update_progress:
                update_progress(98, "Stitching and normalizing tiles...")
                
            valid_mask = weight_accumulator > 1e-6
            final_hr = np.zeros_like(hr_accumulator)
            final_hr[valid_mask] = hr_accumulator[valid_mask] / weight_accumulator[valid_mask]
            
            max_val = np.iinfo(dtype_ref).max
            final_result = np.clip(final_hr * max_val, 0, max_val).astype(dtype_ref)
            
            if is_color:
                # Upscale chrominance channels to match high-resolution shape
                cb_hr = cv2.resize(cb_ref, (hr_w, hr_h), interpolation=cv2.INTER_CUBIC)
                cr_hr = cv2.resize(cr_ref, (hr_w, hr_h), interpolation=cv2.INTER_CUBIC)
                # Merge back to YCrCb and convert to RGB
                yuv_hr = cv2.merge([final_result, cr_hr, cb_hr])
                final_color = cv2.cvtColor(yuv_hr, cv2.COLOR_YCrCb2RGB)
                return final_color
                
            return final_result

        except Exception as e:
            traceback.print_exc()
            raise e
        finally:
            # Safely release the Taichi runtime from this thread
            try:
                ti.reset()
            except:
                pass


def main(
    db_path,
    update_progress=None,
    stop_requested=None,
    single_process=None,
    batch_id=None,
    progress_bar=None,
):
    try:
        if update_progress:
            update_progress(0, "Initiating Weighted Super-Resolution process...")

        image_processor = WeightedSRAlgorithm(db_path)
        align_dir = os.path.join("database", "align")
        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)

        image_paths = []
        if single_process:
            hdf5_path = os.path.join(align_dir, "aligned_images.h5")
            image_paths = get_all_image_paths_for_single_process(db_path)
            ref_name = os.path.splitext(os.path.basename(image_paths[0]))[0] if image_paths else "single_process"
            data_source = hdf5_path if os.path.exists(hdf5_path) else image_paths
        else:
            if batch_id is None:
                raise ValueError("Batch ID must be provided for batch processing.")
            hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
            image_paths = image_processor.get_all_image_paths_for_batch_process(batch_id)
            ref_name = os.path.splitext(os.path.basename(image_paths[0]))[0] if image_paths else f"batch_{batch_id}"
            data_source = hdf5_path if os.path.exists(hdf5_path) else image_paths

        cleanup_old_hdf5_files(hdf5_path)

        output_name_safe = "".join(c for c in ref_name if c.isalnum() or c in ("_", "-")).rstrip() or "sr_result"
        output_path = os.path.join(output_folder_stack, f"{output_name_safe}_weighted_sr.tif")

        # Load images
        if update_progress:
            update_progress(5, "Loading image files...")
            
        if isinstance(data_source, str) and data_source.endswith(".h5"):
            with h5py.File(data_source, "r") as h5f:
                keys = list(h5f.keys())
                images = [np.array(h5f[key]) for key in keys]
        else:
            images = load_images_from_paths(image_paths, stop_requested)

        # Run process
        final_result = image_processor.run_super_resolution(
            images,
            scale=2,
            num_iterations=120,
            update_progress=update_progress,
            stop_requested=stop_requested
        )

        if final_result is not None:
            save_success = save_image(final_result, output_path, reference_image_path=image_paths[0] if image_paths else None)
            final_message = f"Process finished successfully: {os.path.basename(output_path)}" if save_success else "Failed to save result image."
            if update_progress:
                update_progress(100, final_message)
        else:
            if update_progress:
                update_progress(100, "Failed to run super resolution.")

    except Exception as e:
        traceback.print_exc()
        if update_progress:
            update_progress(0, f"Error: {str(e)}")


def running_weighted_sr(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
):
    if batch_id is not None and progress_callback is not None:
        main(
            db_path="pixel_refine_database.db",
            update_progress=progress_callback,
            stop_requested=stop_callback,
            single_process=False,
            batch_id=batch_id,
        )
        return

    process_finished = False
    dialog = QDialog(parent)
    dialog.setWindowTitle("Weighted Super-Resolution")
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)

    layout = QVBoxLayout(dialog)
    label = QLabel("Starting processing...")
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
    worker.progress_updated.connect(lambda progress, message: (progress_bar.setValue(progress), label.setText(message)))

    def finish_handler():
        nonlocal process_finished
        process_finished = True
        dialog.close()
        worker.quit()
        worker.wait()

    worker.finished.connect(finish_handler)
    worker.error_occurred.connect(lambda err: (QMessageBox.critical(dialog, "Error", f"Error occurred: {err}"), dialog.close(), worker.quit(), worker.wait()))

    dialog.closeEvent = lambda ev: ev.accept() if process_finished else (ev.accept() if not worker.isRunning() else (worker.stop(), worker.quit(), worker.wait(), ev.accept()) if QMessageBox.question(dialog, "Cancel Process", "Do you want to cancel?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes else ev.ignore())
    worker.start()
    dialog.exec()


if __name__ == "__main__":
    db_path = "pixel_refine_database.db"
    main(db_path)
