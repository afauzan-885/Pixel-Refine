import traceback
import cv2
import numpy as np
import numpy.ma as ma
import sqlite3
import concurrent.futures
import os
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PySide6.QtCore import Qt, QThread, Signal

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import extract_all_metadata, get_all_image_paths_for_single_process, load_images_from_paths, resize_all_with_padding, save_image
from UI.resources.stylesheet.stylesheet import PROGRESS_BAR
from UI.settings.General.GeneralSetting import load_general_settings
from UI.settings.General.Language import language_config

class ThreadWorker(QThread):
    progress_updated = Signal(int, str)  # Sinyal untuk memperbarui progress
    finished = Signal()  # Sinyal untuk menandakan selesai
    error_occurred = Signal(str)  # Sinyal untuk menandakan error

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

    def stack_median_images(self, images, stop_requested=None, block_size=128, overlap=0.2,
                            update_progress=None, total_overall_images=None, images_processed_so_far=0,
                            use_multi_core=True):
        """
        Menghitung stack gambar dengan metode Median berbasis blok.
        Mendukung kontrol penggunaan multi-core.
        """
        if stop_requested and stop_requested():
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
            overall_progress_cap = 98 # Persentase maksimal sebelum finalisasi
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

        stacked_image = self._compute_median_image( 
            images_resized,
            target_shape,
            block_size,
            dtype,
            overlap,
            update_progress=adapted_update_progress,
            stop_requested=stop_requested,
            use_multi_core=use_multi_core
            # Parameter sigma_low, sigma_high, max_iterations dihapus dari pemanggilan
        )

        if stacked_image is None: # Jika proses dibatalkan atau gagal
             return None

        if adapted_update_progress:
            # Panggil progress 100% dengan pesan selesai dari language_config
            adapted_update_progress(100, language_config.ANALYZING_COMPLETE)

        return stacked_image

    def _resize_images(self, images, target_shape):
        """Resize images to target_shape if they are not already."""
        resized_images = []
        # Target size untuk cv2.resize adalah (W, H)
        target_size = (target_shape[1], target_shape[0]) # (kolom, baris)

        for i, image in enumerate(images):
            if image.shape[0:2] == target_shape[0:2]:
                 resized_images.append(image)
            else:
                 interpolation_method = cv2.INTER_AREA if image.shape[0] > target_shape[0] else cv2.INTER_CUBIC
                 resized = cv2.resize(image, target_size, interpolation=interpolation_method)
                 if image.ndim == 2 and resized.ndim == 3 and resized.shape[2] == 1:
                     resized = resized[:, :, 0] # Ambil channel pertama jika grayscale
                 elif image.ndim == 3 and resized.ndim == 2 and target_shape.ndim == 3 : # Jika target 3 channel
                     resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR)


                 if resized.shape != target_shape:
                     if resized.ndim == 2 and len(target_shape) == 3 and target_shape[2] == 1:
                         resized = np.expand_dims(resized, axis=2)
                     elif resized.ndim == 3 and resized.shape[2] == 1 and len(target_shape) == 2:
                         resized = resized[:,:,0]
                 resized_images.append(resized)
        return resized_images

    def _compute_block_median(self, block_stack):
        """
        Menghitung stack blok menggunakan Median.

        Args:
            block_stack (np.ndarray): Tumpukan blok gambar (N, H, W, [C]).

        Returns:
            np.ndarray: Blok gambar hasil median (H, W, [C]), dtype float32.
        """
        num_blocks = block_stack.shape[0]
        
        if num_blocks == 0:
            return np.zeros(block_stack.shape[1:], dtype=np.float32)
        
        median_block = np.median(block_stack, axis=0)

        return median_block.astype(np.float32)


    def _compute_median_image(self, images, target_shape, block_size, dtype, overlap,
                                 update_progress=None, stop_requested=None,
                                 use_multi_core=True): 
        """
        Menghitung gambar stack menggunakan metode blok dengan Median.
        Mendukung pemrosesan multi-core atau single-core.
        """
        H, W = target_shape[:2]
        num_channels = target_shape[2] if len(target_shape) == 3 else 0

        accumulator = np.zeros(target_shape, dtype=np.float32)
        weight_sum = np.zeros(target_shape[:2], dtype=np.float32) # Bobot hanya 2D

        step = max(int(block_size * (1 - overlap)), 1) 

        row_starts = list(range(0, H - block_size + 1, step))
        if H % block_size != 0 and H > block_size : 
             if not row_starts or row_starts[-1] != H - block_size: row_starts.append(H - block_size)
        elif H <= block_size and not row_starts: 
            row_starts = [0]

        col_starts = list(range(0, W - block_size + 1, step))
        if W % block_size != 0 and W > block_size :
             if not col_starts or col_starts[-1] != W - block_size: col_starts.append(W - block_size)
        elif W <= block_size and not col_starts:
            col_starts = [0]

        if not row_starts or not col_starts: 
            return np.zeros(target_shape, dtype=dtype)

        base_hanning = np.outer(np.hanning(block_size), np.hanning(block_size))

        tasks = []
        for r in row_starts:
            for c in col_starts:
                tasks.append((r, c))

        total_blocks = len(tasks)
        if total_blocks == 0: return np.zeros(target_shape, dtype=dtype) # Tidak ada tugas

        blocks_processed_count = 0
        internal_progress_cap = 98 

        def process_block(row_start, col_start): 
            row_end = min(row_start + block_size, H)
            col_end = min(col_start + block_size, W)
            actual_block_h = row_end - row_start
            actual_block_w = col_end - col_start

            if actual_block_h <= 0 or actual_block_w <= 0:
                 return row_start, row_end, col_start, col_end, None, None

            if num_channels > 0:
                blocks_stack = np.stack([im[row_start:row_end, col_start:col_end, :] for im in images], axis=0)
            else:
                blocks_stack = np.stack([im[row_start:row_end, col_start:col_end] for im in images], axis=0)

            block_result = self._compute_block_median(blocks_stack)

            if (actual_block_h, actual_block_w) == (block_size, block_size):
                hanning_win_2d = base_hanning
            else:
                hanning_win_2d = np.outer(np.hanning(actual_block_h), np.hanning(actual_block_w))

            if num_channels > 0:
                weighted_block_result = block_result * hanning_win_2d[..., np.newaxis]
            else:
                weighted_block_result = block_result * hanning_win_2d

            return row_start, row_end, col_start, col_end, weighted_block_result, hanning_win_2d

        if use_multi_core:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_task = {executor.submit(process_block, r, c): (r, c)
                                  for r, c in tasks}

                for future in concurrent.futures.as_completed(future_to_task):
                    if stop_requested and stop_requested():
                        for f_cancel in future_to_task: f_cancel.cancel()
                        executor.shutdown(wait=False, cancel_futures=True)
                        return None 

                    try:
                        result = future.result()
                        if result is None or result[4] is None: # Cek jika process_block mengembalikan None untuk weighted_block
                             continue

                        row_s, row_e, col_s, col_e, weighted_block, h_win_2d = result

                        accumulator[row_s:row_e, col_s:col_e] += weighted_block
                        weight_sum[row_s:row_e, col_s:col_e] += h_win_2d
                        blocks_processed_count += 1

                        if update_progress:
                            progress_percent = int((blocks_processed_count / total_blocks) * internal_progress_cap)
                            update_progress(progress_percent) # Pesan default "process"

                    except concurrent.futures.CancelledError:
                        pass
                    except Exception as exc:
                        traceback.print_exc() # Cetak traceback untuk debugging
                        pass
        else: 
            for r_task, c_task in tasks:
                if stop_requested and stop_requested():
                    return None 

                try:
                    result = process_block(r_task, c_task)
                    if result is None or result[4] is None:
                         continue

                    row_s, row_e, col_s, col_e, weighted_block, h_win_2d = result

                    accumulator[row_s:row_e, col_s:col_e] += weighted_block
                    weight_sum[row_s:row_e, col_s:col_e] += h_win_2d
                    blocks_processed_count += 1

                    if update_progress:
                        progress_percent = int((blocks_processed_count / total_blocks) * internal_progress_cap)
                        update_progress(progress_percent)

                except Exception as exc:
                    traceback.print_exc()
                    pass

        if stop_requested and stop_requested():
            return None

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
    
def main(db_path, update_progress=None, stop_requested=None, batch_size=10,
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
            if hasattr(image_processor, 'get_all_image_paths_for_batch_process'):
                 image_paths = image_processor.get_all_image_paths_for_batch_process(batch_id)
            else:
                 image_paths = []


            if image_paths and isinstance(image_paths[0], str):
                ref_image_name = os.path.splitext(os.path.basename(image_paths[0]))[0]
                output_name_base = f"{ref_image_name}"
            else:
                output_name_base = f"batch_{batch_id}_no_ref" # Nama file jika tidak ada referensi


        if not image_paths:
            if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return

        output_folder_stack = os.path.join("database", "stack") # Pastikan path ini sesuai
        os.makedirs(output_folder_stack, exist_ok=True)
        output_name_base_safe = "".join(c for c in output_name_base if c.isalnum() or c in ('_', '-')).rstrip()
        if not output_name_base_safe: output_name_base_safe = "stack_result" # Default jika nama kosong setelah sanitasi
        output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_median.tif") # Nama tetap _median
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))

        metadata_folder = align_dir
        os.makedirs(metadata_folder, exist_ok=True)
        metadata_file = os.path.join(metadata_folder, "metadata.json") # Nama file metadata

        if image_paths:
             if 'extract_all_metadata' in globals() and callable(globals()['extract_all_metadata']):
                  try:
                       extract_all_metadata(image_paths, metadata_file=metadata_file)
                  except Exception as e_meta:
                       print(f"Error during metadata extraction: {e_meta}")
                       traceback.print_exc()
             else:
                  print("extract_all_metadata function not found globally.")
        else:
            print("No image paths provided, skipping metadata extraction.")


        # --- Update progress awal ---
        if update_progress: update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        if single_process:
            global_hdf5_path = os.path.join(align_dir, "aligned_images.h5")
        else:
            global_hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")

        processed_batches_results = []
        images_processed_count = 0
        total_images = 0

        use_hdf5 = os.path.exists(global_hdf5_path)

        if use_hdf5:
            print(language_config.PROCESSING_IMAGE_FROM_HDF5.format(global_hdf5_path))
            try:
                with h5py.File(global_hdf5_path, 'r') as h5f_check:
                    total_images = len(h5f_check.keys())
                print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))

                if total_images == 0:
                    if update_progress: update_progress(100, "File HDF5 kosong atau tidak ada dataset yang valid.")
                    return

                total_batches = (total_images + batch_size - 1) // batch_size
                print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))

                with h5py.File(global_hdf5_path, 'r') as h5f:
                    keys = list(h5f.keys())
                    for batch_start in range(0, total_images, batch_size):
                        current_batch_num = (batch_start // batch_size) + 1
                        print(f"\n" + language_config.PROCESSING_BATCH.format(current_batch_num, total_batches, batch_start))

                        if stop_requested and stop_requested():
                            print(language_config.PROCESS_TERMINATED_BY_USER)
                            break

                        batch_keys = keys[batch_start:min(batch_start + batch_size, total_images)]
                        print(language_config.LOAD_IMAGE_FROM_HDF5.format(len(batch_keys)))
                        batch_images = []
                        for key in batch_keys:
                            if stop_requested and stop_requested(): break
                            try:
                                data = h5f[key]
                                if isinstance(data, h5py.Dataset):
                                    batch_images.append(np.array(data))
                                else:
                                    print(f"Peringatan: Kunci '{key}' dalam HDF5 bukan dataset, dilewati.")
                            except Exception as e:
                                print(language_config.ERROR_WHILE_RETRIEVING_KEY_FROM_HD5F.format(key, e))
                        if stop_requested and stop_requested(): break

                        if not batch_images:
                            print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num))
                            continue

                        print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images)))
                        try:
                             batch_result = image_processor.stack_median_images(
                                 batch_images,
                                 update_progress=update_progress,
                                 stop_requested=stop_requested,
                                 total_overall_images=total_images,
                                 images_processed_so_far=images_processed_count,
                                 use_multi_core=use_multicore_from_settings
                             )
                        except Exception as e_sim_batch:
                             print(f"Error saat memproses batch {current_batch_num} dengan stack_median_images: {e_sim_batch}")
                             traceback.print_exc()
                             batch_result = None

                        if stop_requested and stop_requested(): break # Cek lagi setelah pemrosesan batch

                        if batch_result is not None:
                             processed_batches_results.append(batch_result)
                             images_processed_count += len(batch_images)
                        else:
                            print(f"Batch {current_batch_num} processing returned None or failed.")

            except Exception as e:
                print(language_config.ERROR_IN_READING_FILE_HDF5.format(e))
                traceback.print_exc()
                if update_progress: update_progress(0, language_config.ERROR_IN_READING_FILE_HDF5.format(e))
                return

        else: # Process from image paths if HDF5 not found
            print(language_config.NO_HDF5_FILE_PROCESSING_FROM_PATH)
            total_images = len(image_paths)
            print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))

            if total_images == 0:
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
                # Fungsi load_images_from_paths dan resize_all_with_padding perlu ada
                batch_images_raw = load_images_from_paths(batch_paths, stop_requested)

                if stop_requested and stop_requested(): break
                if not batch_images_raw:
                    print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num))
                    continue

                # Pastikan semua gambar dalam batch_images_raw memiliki shape yang sama sebelum stacking
                # Fungsi resize_all_with_padding idealnya menangani ini.
                # Jika tidak, Anda perlu logika tambahan di sini.
                # Untuk contoh, kita asumsikan resize_all_with_padding mengembalikan list gambar yang sudah siap.
                batch_images, _ = resize_all_with_padding(batch_images_raw, method="median") # atau method lain yang sesuai


                if not batch_images: # Jika setelah resize tidak ada gambar (misal, error)
                    print(f"Skipping batch {current_batch_num} due to issues in resizing/padding.")
                    continue

                print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images)))
                try:
                    # Panggil fungsi stack_median_images
                    batch_result = image_processor.stack_median_images(
                        batch_images,
                        update_progress=update_progress,
                        stop_requested=stop_requested,
                        total_overall_images=total_images,
                        images_processed_so_far=images_processed_count,
                        use_multi_core=use_multicore_from_settings
                    )
                except Exception as e_sim_batch:
                      print(f"Error saat memproses batch {current_batch_num} (dari path) dengan stack_median_images: {e_sim_batch}")
                      traceback.print_exc()
                      batch_result = None

                if stop_requested and stop_requested(): break

                if batch_result is not None:
                    processed_batches_results.append(batch_result)
                    images_processed_count += len(batch_images)
                else:
                    print(f"Batch {current_batch_num} (dari path) processing returned None or failed.")


        # --- Fine-Tuning / Pemrosesan Akhir (jika ada hasil batch) ---
        if stop_requested and stop_requested():
            # Jangan lakukan apa-apa jika proses sudah diminta berhenti
            pass
        elif processed_batches_results:
            num_fine_tuning_inputs = len(processed_batches_results)
            print(f"\n--- {language_config.STARTING_ENHANCEMENT} ({num_fine_tuning_inputs} batch results) ---")

            # Tentukan rentang progress untuk tahap "fine-tuning" (stacking hasil batch)
            # Misal, dari 95% ke 99%
            fine_tuning_start_progress = 95 # Atau ambil dari progress terakhir sebelum ini
            fine_tuning_end_progress = 99

            def fine_tuning_update_progress(inner_progress, message):
                # Map progress internal (0-100) dari stacking hasil batch ke rentang global
                mapped_progress = fine_tuning_start_progress + int((inner_progress / 100.0) * (fine_tuning_end_progress - fine_tuning_start_progress))
                if update_progress:
                    if not (stop_requested and stop_requested()): # Hanya update jika tidak dibatalkan
                        update_progress(mapped_progress, language_config.ENHANCEMENT.format(message))

            if update_progress: update_progress(fine_tuning_start_progress, language_config.STARTING_ENHANCEMENT)

            final_result = None
            try:
                 # Panggil stack_median_images lagi untuk menggabungkan hasil batch
                 final_result = image_processor.stack_median_images(
                     processed_batches_results,
                     update_progress=fine_tuning_update_progress, # Gunakan progress mapper khusus
                     stop_requested=stop_requested,
                     use_multi_core=use_multicore_from_settings,
                     # Untuk progress mapping di dalam stack_median_images:
                     total_overall_images=num_fine_tuning_inputs, # Total item adalah jumlah hasil batch
                     images_processed_so_far=0 # Mulai dari 0 untuk panggilan ini
                 )
            except Exception as e_fine_tune:
                  print(f"Error during final stacking of batch results: {e_fine_tune}")
                  traceback.print_exc()
                  final_result = None

            if stop_requested and stop_requested():
                pass # Proses dibatalkan

            elif final_result is not None:
                 # Ambil path gambar pertama sebagai referensi untuk penyimpanan (misal, metadata)
                 ref_path_for_save = image_paths[0] if image_paths and isinstance(image_paths[0], str) else None
                 # Fungsi save_image perlu didefinisikan
                 save_success = save_image(final_result, output_path, reference_image_path=ref_path_for_save)

                 if save_success:
                    final_message = f"{language_config.IMAGE_PROCESS_FINISHED}: {os.path.basename(output_path)}"
                    print(final_message)
                    if update_progress: update_progress(100, final_message) # Selesai dengan sukses

                    # Hapus file HDF5 batch jika bukan single process dan batch_id ada
                    if not single_process and batch_id is not None:
                        batch_hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
                        if os.path.exists(batch_hdf5_path):
                            try:
                                os.remove(batch_hdf5_path)
                                print(f"Batch HDF5 file {batch_hdf5_path} removed.")
                            except Exception as e_remove:
                                print(f"Failed to remove batch HDF5 file {batch_hdf5_path}: {e_remove}")
                        # else:
                        #     print(f"Batch HDF5 file {batch_hdf5_path} not found, no removal needed.")
                 else:
                      error_msg = language_config.FAILED_TO_SAVE_IMAGE + f": {os.path.basename(output_path)}"
                      print(error_msg)
                      if update_progress: update_progress(100, error_msg) # Selesai tapi gagal simpan
            else: # final_result is None (dan tidak dibatalkan)
                print(language_config.FAILED_IMAGE_ENHANCEMENT)
                if update_progress: update_progress(100, language_config.FAILED_IMAGE_ENHANCEMENT) # Selesai tapi gagal stacking akhir

        elif not (stop_requested and stop_requested()): # Tidak ada hasil batch DAN tidak dibatalkan
            print(language_config.DATA_FAILED_COMPLETION_CREATED)
            if update_progress:
                update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED)

        # Jika proses dibatalkan, update progress terakhir dengan pesan pembatalan
        if stop_requested and stop_requested():
             # Dapatkan nilai progress terakhir jika progress_bar ada dan bisa diakses
             # Ini asumsi, progress_bar mungkin perlu dilewatkan secara berbeda
             current_progress_val = progress_bar.value() if progress_bar and hasattr(progress_bar, 'value') else 0
             if update_progress: update_progress(current_progress_val, "Proses dibatalkan oleh pengguna.")


    except ValueError as ve:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(ve))
        print(error_message)
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
             update_progress(0, error_message) # Reset progress ke 0 dengan pesan error
    except FileNotFoundError as fnf:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(fnf))
        print(error_message)
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
             update_progress(0, error_message)
    except RuntimeError as rte: # Misal, dari concurrent.futures jika ada masalah executor
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(rte))
        print(error_message)
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)
    except Exception as e: # Tangkap semua exception lain
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        print(error_message)
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)
    finally:
       # Kode cleanup jika ada, akan selalu dijalankan
       # print("Proses utama selesai atau dihentikan.")
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