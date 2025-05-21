import traceback
import cv2
import numpy as np
import numpy.ma as ma
import sqlite3
import concurrent.futures
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import extract_all_metadata, get_all_image_paths_for_single_process, load_images_from_paths, save_image
from UI.resources.stylesheet.stylesheet import PROGRESS_BAR
from UI.settings.General.GeneralSetting import load_general_settings
from UI.settings.General.Language import language_config

class ThreadWorker(QThread):
    progress_updated = pyqtSignal(int, str)  # Sinyal untuk memperbarui progress
    finished = pyqtSignal()  # Sinyal untuk menandakan selesai
    error_occurred = pyqtSignal(str)  # Sinyal untuk menandakan error

    def __init__(self, db_path, single_process=True, batch_id=None):
        super().__init__()
        self.db_path = db_path
        self.single_process = single_process  # Menentukan apakah proses single atau batch
        self.batch_id = batch_id  # ID batch jika batch processing
        self.stop_requested = False  # Flag untuk menghentikan thread

    def run(self):
        try:
            def update_progress(progress, message):
                self.progress_updated.emit(progress, message)

            # Fungsi callback untuk mengecek status stop
            def is_stop_requested():
                return self.stop_requested

            # Panggil main dengan parameter yang sesuai
            main(
                self.db_path, 
                update_progress=update_progress, 
                stop_requested=is_stop_requested, 
                single_process=self.single_process, 
                batch_id=self.batch_id
            )
            
            self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))
            
    def stop(self):
        self.stop_requested = True  
        
class MedianAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5", max_workers=None):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        # Pastikan folder HDF5 ada
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

        # Buat executor sekali saja untuk reuse di setiap pemrosesan
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
    def get_all_image_paths_for_batch_process(self, batch_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT images.path 
                FROM batch_process_image
                JOIN images ON batch_process_image.image_id_batch = images.id
                WHERE batch_process_image.batch_id = ?
            """, (batch_id,))
            return [row[0] for row in cursor.fetchall()]

    def load_images_from_hdf5(self, hdf5_path, stop_requested=None):
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                if stop_requested and stop_requested():
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images

    def stack_sigma_clip_images(self, images, stop_requested=None, block_size=64, overlap=0.3,
                                update_progress=None, total_overall_images=None, images_processed_so_far=0,
                                sigma_low=3.0, sigma_high=3.0, max_iterations=3,
                                use_multi_core=True): # Parameter baru
        """
        Menghitung stack gambar dengan metode Sigma Clipping berbasis blok.
        Mendukung kontrol penggunaan multi-core.
        """
        if stop_requested and stop_requested():
             print(language_config.STACK_SIGMA_CLIP_STOPPED)
             return None

        if not images:
            raise ValueError(language_config.NO_IMAGES_PROCESSED)

        if not isinstance(images[0], np.ndarray):
             raise TypeError(language_config.IMAGE_DATA_MUST_BE_VALID)

        dtype = images[0].dtype
        target_shape = images[0].shape
        num_images_in_this_call = len(images)

        adapted_update_progress = None
        if update_progress:
            overall_progress_cap = 98
            progress_start_percent = 0
            progress_range_for_this_call = overall_progress_cap
            if total_overall_images is not None and total_overall_images > 0:
                 progress_start_percent = (images_processed_so_far / total_overall_images) * 100
                 theoretical_end_percent = ((images_processed_so_far + num_images_in_this_call) / total_overall_images) * 100
                 progress_end_percent_for_this_call = min(theoretical_end_percent, overall_progress_cap)
                 progress_range_for_this_call = max(0, progress_end_percent_for_this_call - progress_start_percent)
            def map_progress(internal_percent, internal_message="process"):
                 overall_progress = int(progress_start_percent + (internal_percent / 100.0) * progress_range_for_this_call)
                 update_progress(overall_progress, f"{internal_message}")
            adapted_update_progress = map_progress
        # --------------------------------

        images_resized = self._resize_images(images, target_shape)
        stacked_image = self._compute_sigma_clip_image(
            images_resized,
            target_shape,
            block_size,
            dtype,
            overlap,
            update_progress=adapted_update_progress,
            stop_requested=stop_requested,
            sigma_low=sigma_low,
            sigma_high=sigma_high,
            max_iterations=max_iterations,
            use_multi_core=use_multi_core 
        )

        if stacked_image is None:
             return None

        if adapted_update_progress:
            adapted_update_progress(100, language_config.ANALYZING_COMPLETE)

        return stacked_image

    def _resize_images(self, images, target_shape):
        resized_images = []
        target_size = (target_shape[1], target_shape[0])
        for i, image in enumerate(images):
            if image.shape[0:2] == target_shape[0:2]:
                 resized_images.append(image)
            else:
                 resized = cv2.resize(image, target_size, interpolation=cv2.INTER_CUBIC)
                 resized_images.append(resized)
        return resized_images

    def _compute_block_sigma_clip(self, block_stack, sigma_low=3.0, sigma_high=3.0, max_iterations=5):
        """
        Menghitung stack blok menggunakan Sigma Clipping (Rejection).

        Args:
            block_stack (np.ndarray): Tumpukan blok gambar (N, H, W, [C]).
            sigma_low (float): Batas bawah sigma untuk penolakan.
            sigma_high (float): Batas atas sigma untuk penolakan.
            max_iterations (int): Jumlah iterasi maksimum untuk clipping.

        Returns:
            np.ndarray: Blok gambar hasil sigma clipping (H, W, [C]), dtype float32.
        """
        num_blocks, H, W = block_stack.shape[:3]
        num_channels = block_stack.shape[3] if block_stack.ndim == 4 else 0

        if num_blocks == 0:
            return np.zeros(block_stack.shape[1:], dtype=np.float32)
        elif num_blocks == 1:
            return block_stack[0].astype(np.float32)

        current_mask = np.ones(num_blocks, dtype=bool)
        clipped_count = 0

        # Iterasi Sigma Clipping
        for _ in range(max_iterations):
            valid_blocks = block_stack[current_mask]
            if valid_blocks.shape[0] < 2: 
                break 

            median_block = np.median(valid_blocks, axis=0)
            std_dev_block = np.std(valid_blocks, axis=0)

            lower_bound = median_block - sigma_low * std_dev_block
            upper_bound = median_block + sigma_high * std_dev_block

            new_mask = np.ones(num_blocks, dtype=bool)
            new_mask[current_mask] = np.all(
                (block_stack[current_mask] >= lower_bound) & (block_stack[current_mask] <= upper_bound),
                axis=tuple(range(1, block_stack.ndim)) 
            )

            if np.all(new_mask == current_mask):
                break

            current_mask = new_mask
            clipped_count = num_blocks - np.sum(current_mask) 

        final_valid_blocks = block_stack[current_mask]
        if final_valid_blocks.shape[0] == 0:
             return np.median(block_stack, axis=0).astype(np.float32)
        else:
            # print(f"Sigma Clip: Kept {final_valid_blocks.shape[0]}/{num_blocks} blocks.")
            return np.mean(final_valid_blocks, axis=0).astype(np.float32)


    def _compute_sigma_clip_image(self, images, target_shape, block_size, dtype, overlap,
                                 update_progress=None, stop_requested=None,
                                 sigma_low=3.0, sigma_high=3.0, max_iterations=3,
                                 use_multi_core=True):
        """
        Menghitung gambar stack menggunakan metode blok dengan Sigma Clipping.
        Mendukung pemrosesan multi-core atau single-core.
        """
        H, W = target_shape[:2]
        num_channels = target_shape[2] if len(target_shape) == 3 else 0

        accumulator = np.zeros(target_shape, dtype=np.float32)
        weight_sum = np.zeros(target_shape[:2], dtype=np.float32)

        step = max(int(block_size * (1 - overlap)), 1)

        # Kalkulasi row_starts dan col_starts (tetap sama)
        row_starts = list(range(0, H - block_size + 1, step))
        if H % block_size != 0 and H > block_size :
             if not row_starts or row_starts[-1] != H - block_size: row_starts.append(H - block_size)
        elif H <= block_size and not row_starts: row_starts = [0]
        col_starts = list(range(0, W - block_size + 1, step))
        if W % block_size != 0 and W > block_size :
             if not col_starts or col_starts[-1] != W - block_size: col_starts.append(W - block_size)
        elif W <= block_size and not col_starts: col_starts = [0]
        if not row_starts or not col_starts: return np.zeros(target_shape, dtype=dtype)

        base_hanning = np.outer(np.hanning(block_size), np.hanning(block_size))

        tasks = []
        for r in row_starts:
            for c in col_starts:
                tasks.append((r, c))

        total_blocks = len(tasks)
        if total_blocks == 0: return np.zeros(target_shape, dtype=dtype)

        blocks_processed_count = 0
        internal_progress_cap = 98 

        def process_block(row_start, col_start, p_sigma_low, p_sigma_high, p_max_iter):
            row_end = min(row_start + block_size, H)
            col_end = min(col_start + block_size, W)
            actual_block_h = row_end - row_start
            actual_block_w = col_end - col_start

            if actual_block_h <= 0 or actual_block_w <= 0: # Cek jika blok tidak valid
                 return row_start, row_end, col_start, col_end, None, None

            if num_channels > 0:
                blocks = np.stack([im[row_start:row_end, col_start:col_end, :] for im in images], axis=0)
            else:
                blocks = np.stack([im[row_start:row_end, col_start:col_end] for im in images], axis=0)

            block_result = self._compute_block_sigma_clip(blocks, p_sigma_low, p_sigma_high, p_max_iter)

            if (actual_block_h, actual_block_w) == (block_size, block_size):
                hanning_win_2d = base_hanning
            else:
                hanning_win_2d = np.outer(np.hanning(actual_block_h), np.hanning(actual_block_w))
            weighted_block_result = block_result * hanning_win_2d[..., np.newaxis if num_channels > 0 else Ellipsis]

            return row_start, row_end, col_start, col_end, weighted_block_result, hanning_win_2d

        if use_multi_core:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_task = {executor.submit(process_block, r, c, sigma_low, sigma_high, max_iterations): (r, c)
                                  for r, c in tasks}

                for future in concurrent.futures.as_completed(future_to_task):
                    if stop_requested and stop_requested():
                        for f in future_to_task: f.cancel()
                        executor.shutdown(wait=False, cancel_futures=True) # Coba batalkan
                        return None # Keluar
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        if result is None or result[4] is None: # Cek jika process_block gagal
                             continue

                        row_start, row_end, col_start, col_end, weighted_block, hanning_win_2d = result

                        accumulator[row_start:row_end, col_start:col_end] += weighted_block
                        weight_sum[row_start:row_end, col_start:col_end] += hanning_win_2d
                        blocks_processed_count += 1

                        if update_progress:
                            progress_percent = int((blocks_processed_count / total_blocks) * internal_progress_cap)
                            update_progress(progress_percent)

                    except concurrent.futures.CancelledError:
                        pass
                    except Exception as exc:
                        pass
        else:
            for r, c in tasks:
                if stop_requested and stop_requested():
                    return None 
                
                try:
                    result = process_block(r, c, sigma_low, sigma_high, max_iterations)
                    if result is None or result[4] is None:
                         continue

                    row_start, row_end, col_start, col_end, weighted_block, hanning_win_2d = result

                    # Akumulasi hasil
                    accumulator[row_start:row_end, col_start:col_end] += weighted_block
                    weight_sum[row_start:row_end, col_start:col_end] += hanning_win_2d
                    blocks_processed_count += 1

                    # Update progress
                    if update_progress:
                        progress_percent = int((blocks_processed_count / total_blocks) * internal_progress_cap)
                        update_progress(progress_percent)

                except Exception as exc:
                    pass
        
        if update_progress:
             update_progress(internal_progress_cap, language_config.FINISHING_ANALYSIS)

        final_weight_sum = weight_sum[..., np.newaxis] if num_channels > 0 else weight_sum
        mask = final_weight_sum > 1e-10
        stacked_image_float = np.zeros_like(accumulator)
        np.divide(accumulator, final_weight_sum, out=stacked_image_float, where=mask)

        if np.issubdtype(dtype, np.integer):
            min_val, max_val = np.iinfo(dtype).min, np.iinfo(dtype).max
            stacked_image_float = np.nan_to_num(stacked_image_float, nan=0.0, posinf=max_val, neginf=min_val)
            final_image = np.clip(stacked_image_float, min_val, max_val).astype(dtype)
        elif np.issubdtype(dtype, np.floating):
            stacked_image_float = np.nan_to_num(stacked_image_float, nan=0.0)
            final_image = stacked_image_float.astype(dtype)
        else:
            final_image = stacked_image_float 

        return final_image

def main(db_path, update_progress=None, stop_requested=None, batch_size=4,
         single_process=None, batch_id=None, progress_bar=None):
    try:
        general_settings, _ = load_general_settings()
        use_multicore_from_settings = general_settings.get('multi_core_cpu', True)
        image_processor = MedianAlgorithm(db_path)

        output_name_base = ""
        image_paths = []
        align_dir = os.path.join("database", "align") 

        if single_process:
            image_paths = get_all_image_paths_for_single_process(db_path)
            if image_paths:
                 if image_paths[0] and isinstance(image_paths[0], str):
                      ref_image_name = os.path.splitext(os.path.basename(image_paths[0]))[0]
                      output_name_base = f"{ref_image_name}"
                 else:
                      output_name_base = "single_process_invalid_path"
            else:
                 output_name_base = "single_process_no_images"
        else:
            if batch_id is None:
                raise ValueError(language_config.BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS)
            else:
                pass

            # Lanjutkan dengan mendapatkan path gambar untuk batch
            image_paths = image_processor.get_all_image_paths_for_batch_process(batch_id)
            if image_paths and isinstance(image_paths[0], str):
                ref_image_name = os.path.splitext(os.path.basename(image_paths[0]))[0]
                output_name_base = f"{ref_image_name}"
            else:
                output_name_base = "batch_no_reference"

           
        if not image_paths:
            print(language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return 

        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)
        output_name_base_safe = "".join(c for c in output_name_base if c.isalnum() or c in ('_', '-')).rstrip()
        if not output_name_base_safe: output_name_base_safe = "stack_result"
        output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_median.tif")
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))
        
        metadata_folder = align_dir 
        os.makedirs(metadata_folder, exist_ok=True) 
        metadata_file = os.path.join(metadata_folder, "metadata.json")

        # Panggil ekstraksi metadata hanya jika ada path gambar
        if image_paths:
             if 'extract_all_metadata' in globals():
                  try:
                       extract_all_metadata(image_paths, metadata_file=metadata_file)
                  except Exception as e_meta:
                       traceback.print_exc()     
             else:
                  pass
        else:
            pass

        # --- Update progress awal ---
        if update_progress: update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        if single_process:
            global_hdf5_path = os.path.join(align_dir, "aligned_images.h5")
        else:
            global_hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
        processed_batches_results = []
        images_processed_count = 0
        total_images = 0

        # --- Logika Pemrosesan Utama (Batching dari HDF5 atau Path) ---
        use_hdf5 = os.path.exists(global_hdf5_path)

        if use_hdf5:
            print(language_config.PROCESSING_IMAGE_FROM_HDF5.format(global_hdf5_path))
            try:
                # Dapatkan total gambar dari HDF5 untuk progress
                with h5py.File(global_hdf5_path, 'r') as h5f_check:
                    total_images = len(h5f_check.keys())
                print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))

                if total_images == 0:
                    if update_progress: update_progress(100, "File HDF5 is empty.")
                    return

                total_batches = (total_images + batch_size - 1) // batch_size
                print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))

                with h5py.File(global_hdf5_path, 'r') as h5f:
                    keys = list(h5f.keys()) # Ambil keys sekali saja
                    for batch_start in range(0, total_images, batch_size):
                        current_batch_num = (batch_start // batch_size) + 1
                        print(f"\n" + language_config.PROCESSING_BATCH.format(current_batch_num, total_batches, batch_start))

                        if stop_requested and stop_requested():
                            print(language_config.PROCESS_TERMINATED_BY_USER)
                            break 
                        
                        batch_keys = keys[batch_start:min(batch_start + batch_size, total_images)]
                        print(language_config.LOAD_IMAGE_FROM_HDF5.format(len(batch_keys)))
                        batch_images = []
                        keys_loaded_in_batch = 0
                        for key in batch_keys:
                            if stop_requested and stop_requested(): break
                            try:
                                batch_images.append(np.array(h5f[key]))
                                keys_loaded_in_batch += 1
                            except Exception as e:
                                print(language_config.ERROR_WHILE_RETRIEVING_KEY_FROM_HD5F.format(key, e))
                        if stop_requested and stop_requested(): break 

                        if not batch_images:
                            print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num))
                            continue 
                        
                        print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images)))
                        try:
                             batch_result = image_processor.stack_sigma_clip_images(
                                 batch_images,
                                 update_progress=update_progress,
                                 stop_requested=stop_requested,
                                 total_overall_images=total_images,
                                 images_processed_so_far=images_processed_count,
                                 use_multi_core=use_multicore_from_settings # <-- LEWATKAN DI SINI
                             )
                        except Exception as e_sim_batch:
                             traceback.print_exc()
                             batch_result = None 
                             
                        if stop_requested and stop_requested():
                            break

                        if batch_result is not None:
                             processed_batches_results.append(batch_result)
                             images_processed_count += len(batch_images)                             
                        else:
                            pass
                            # print(f"Batch {current_batch_num} processing failed or returned None.")
                         
            except Exception as e:
                print(language_config.ERROR_IN_READING_FILE_HDF5.format(e))
                traceback.print_exc()
                if update_progress: update_progress(0, language_config.ERROR_IN_READING_FILE_HDF5.format(e))
                return 

        else: 
            print(language_config.NO_HDF5_FILE_PROCESSING_FROM_PATH)
            total_images = len(image_paths)
            print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))

            if total_images == 0:
                print(language_config.NO_IMAGE_PATH_PROCESSED_IMAGE) # Redundan, sudah dicek di atas, tapi aman
                if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
                return

            total_batches = (total_images + batch_size - 1) // batch_size
            print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))

            for batch_start in range(0, total_images, batch_size):
                current_batch_num = (batch_start // batch_size) + 1
                print(f"\n" + language_config.PROCESSING_BATCH.format(current_batch_num, total_batches, batch_start))

                if stop_requested and stop_requested():
                    print(language_config.PROCESS_TERMINATED_BY_USER)
                    break

                batch_paths = image_paths[batch_start:min(batch_start + batch_size, total_images)]
                batch_images = load_images_from_paths(batch_paths, stop_requested)
                if stop_requested and stop_requested(): break

                if not batch_images:
                    print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num))
                    continue

                print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images)))
                try:
                    batch_result = image_processor.stack_sigma_clip_images(
                        batch_images,
                        update_progress=update_progress,
                        stop_requested=stop_requested,
                        total_overall_images=total_images,
                        images_processed_so_far=images_processed_count,
                        use_multi_core=use_multicore_from_settings # <-- LEWATKAN DI SINI
                    )
                except Exception as e_sim_batch:
                      traceback.print_exc()
                      batch_result = None

                if stop_requested and stop_requested():
                    break

                if batch_result is not None:
                    processed_batches_results.append(batch_result)
                    images_processed_count += len(batch_images)
                else:
                    print(f"Batch {current_batch_num} processing failed or returned None.")


        # --- Fine-Tuning / Pemrosesan Akhir (jika ada hasil batch) ---
        if stop_requested and stop_requested():
            pass
        elif processed_batches_results:
            num_fine_tuning_inputs = len(processed_batches_results)
            print(f"\n--- {language_config.STARTING_ENHANCEMENT} ({num_fine_tuning_inputs} batch results) ---")

            fine_tuning_start_progress = 95
            fine_tuning_end_progress = 99

            def fine_tuning_update_progress(inner_progress, message):
                mapped_progress = fine_tuning_start_progress + int((inner_progress / 100.0) * (fine_tuning_end_progress - fine_tuning_start_progress))
                if update_progress:
                    if not (stop_requested and stop_requested()):
                        update_progress(mapped_progress, language_config.ENHANCEMENT.format(message))

            if update_progress: update_progress(fine_tuning_start_progress, language_config.STARTING_ENHANCEMENT)

            final_result = None
            try:
                 final_result = image_processor.stack_sigma_clip_images(
                     processed_batches_results,
                     update_progress=fine_tuning_update_progress,
                     stop_requested=stop_requested,
                     use_multi_core=use_multicore_from_settings, 
                     total_overall_images=num_fine_tuning_inputs,
                     images_processed_so_far=0
                 )
            except Exception as e_fine_tune:
                  traceback.print_exc()
                  final_result = None 

            if stop_requested and stop_requested():
                pass
            
            elif final_result is not None:
                 ref_path_for_save = image_paths[0] if image_paths and isinstance(image_paths[0], str) else None
                 save_success = save_image(final_result, output_path, reference_image_path=ref_path_for_save)
                 if save_success:
                    final_message = f"{language_config.IMAGE_PROCESS_FINISHED}: {os.path.basename(output_path)}"
                    print(final_message)
                    if update_progress: update_progress(100, final_message)
                    if not single_process and batch_id is not None:
                        batch_hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
                        if os.path.exists(batch_hdf5_path):
                            try:
                                os.remove(batch_hdf5_path)
                            except Exception as e:
                                pass
                        else:
                            pass
                 else:
                      error_msg = language_config.FAILED_TO_SAVE_IMAGE + f": {os.path.basename(output_path)}"
                      print(error_msg)
                      if update_progress: update_progress(100, error_msg) # Tetap 100% tapi pesan error
            else:
                print(language_config.FAILED_IMAGE_ENHANCEMENT)
                if update_progress: update_progress(100, language_config.FAILED_IMAGE_ENHANCEMENT) # 100% tapi pesan gagal

        elif not (stop_requested and stop_requested()): # Jika tidak ada hasil batch DAN tidak dibatalkan
            print(language_config.DATA_FAILED_COMPLETION_CREATED)
            if update_progress:
                update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED)

        if stop_requested and stop_requested():
             if update_progress and progress_bar: update_progress(progress_bar.value(), "Proses dibatalkan.") # Update progress terakhir


    except ValueError as ve:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(ve))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
             update_progress(0, error_message)
    except FileNotFoundError as fnf:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(fnf))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
             update_progress(0, error_message)
    except RuntimeError as rte:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(rte))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)
    except Exception as e: 
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)
    finally:
       pass
       
def running_median(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_MEDIAN)
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(
        Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint |
        Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint
    )

    # Layout untuk progress bar dan label
    layout = QVBoxLayout(dialog)
    label = QLabel(language_config.WINDOW_START_PROCESSING)
    layout.addWidget(label)

    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setStyleSheet(PROGRESS_BAR)
    layout.addWidget(progress_bar)

    # Inisialisasi thread worker
    worker = ThreadWorker("pixel_refine_database.db", single_process=single_process, batch_id=batch_id)
    # Menghubungkan signal worker ke fungsi pembaruan UI
    worker.progress_updated.connect(lambda progress, message: (
        progress_bar.setValue(progress),
        label.setText(message)
    ))

    def finish_handler():
        nonlocal process_finished
        process_finished = True  # set flag ketika proses selesai
        dialog.close()
        worker.quit()  # Berhenti dari thread
        worker.wait()  # Tunggu thread selesai

    worker.finished.connect(finish_handler)

    def error_handler(error):
        QMessageBox.critical(dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=error))
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    def on_dialog_close(event):
        # Jika proses telah selesai, lewati konfirmasi
        if process_finished:
            event.accept()
        elif worker.isRunning():
            reply = QMessageBox.question(dialog, "Cancel Process",
                                        language_config.CANCEL_PROCESSING,
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
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
    db_path = "pixel_refine_database.db"  # Path ke database Anda
    main(db_path)