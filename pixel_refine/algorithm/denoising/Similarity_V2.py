import ctypes
from functools import lru_cache
import traceback
import cv2
import numpy as np
import sqlite3
import os
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PySide6.QtCore import QThread, Signal, Qt
from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import extract_all_metadata, gaussian_window, get_all_image_paths_for_single_process, load_images_from_paths, normalize_image, resize_all_with_padding, save_image
from UI.enhance_stack.components.single_page_layout.parameter_denoising.similarity_v2_parameter_settings import load_similarity_v2_config
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
            print(f"Error terjadi: {str(e)}")  # Menampilkan pesan error di konsol
            self.error_occurred.emit(str(e))  # Mengirim pesan error melalui sinyal

    def stop(self):
        self.stop_requested = True  # Set flag agar thread berhenti

class SimilarityAlgorithmV2:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path
        self.low_global_sigma_thresh = 0.043  # Sigma di bawah ini dianggap "bersih"
        self.high_global_sigma_thresh = 0.28   # Sigma di atas ini dianggap "sangat ber-noise"
        self.high_max_multiplier = 5.5        # Multiplier maks untuk gambar bersih
        self.low_max_multiplier = 15.0        # Multiplier maks untuk gambar sangat ber-noise

        # Pastikan folder HDF5 ada
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

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
                if stop_requested and stop_requested():  # Cek apakah harus berhenti
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images

    def load_images_from_hdf5(self, hdf5_path, stop_requested=None):
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                if stop_requested and stop_requested():  # Cek apakah harus berhenti
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images

    def _calculate_dynamic_max_multiplier(self, global_avg_sigma):
        """Menghitung multiplier maksimum dinamis berdasarkan sigma global."""
        clamped_sigma = max(self.low_global_sigma_thresh, min(global_avg_sigma, self.high_global_sigma_thresh))

        if self.high_global_sigma_thresh <= self.low_global_sigma_thresh:
            return self.high_max_multiplier 
        
        if clamped_sigma <= self.low_global_sigma_thresh:
            return self.high_max_multiplier
        elif clamped_sigma >= self.high_global_sigma_thresh:
            return self.low_max_multiplier
        else:
            factor = (clamped_sigma - self.low_global_sigma_thresh) / (self.high_global_sigma_thresh - self.low_global_sigma_thresh)
            dynamic_multiplier = self.high_max_multiplier + factor * (self.low_max_multiplier - self.high_max_multiplier)

            # --- PERBAIKAN LOGIKA CLAMPING ---
            lower_bound = min(self.low_max_multiplier, self.high_max_multiplier)
            upper_bound = max(self.low_max_multiplier, self.high_max_multiplier)

            clamped_multiplier = max(lower_bound, min(upper_bound, dynamic_multiplier))
            return clamped_multiplier
        
    # === FUNGSI untuk Skor Noise ===
    def _calculate_noise_level_score(self, global_avg_sigma):
        """
        Menghitung skor tingkat kebersihan gambar (0-100) berdasarkan sigma global.
        100 = Sangat Bersih (sigma <= low_thresh)
        0   = Sangat Bising (sigma >= high_thresh)
        Linear dazwischen.
        """
        sigma_low = self.low_global_sigma_thresh
        sigma_high = self.high_global_sigma_thresh

        if sigma_high <= sigma_low:
            return 50.0 if global_avg_sigma > sigma_low else 100.0

        if global_avg_sigma <= sigma_low:
            return 100.0
        elif global_avg_sigma >= sigma_high:
            return 0.0
        else:
            score = 100.0 * (sigma_high - global_avg_sigma) / (sigma_high - sigma_low)
            return max(0.0, min(score, 100.0))
    

    def similarity_mfnr(self, images, tile_size, overlap,
                        mbm_mad_sensitivity=20.0,
                        mbm_noise_mad_offset_factor=0.5,
                        mbm_confidence_skip_dft_threshold=0.9,
                        coarse_alignment_search_margin=12,
                        freq_merge_wiener_c_factor=2.0,
                        update_progress=None, stop_requested=None,
                        lib_path='UI/data/similarity_motion_v2.dll',
                        save_weight_map_path=None,
                        total_overall_images=None, images_processed_so_far=0):

        if not isinstance(images, list) or not images:
           raise ValueError("Input 'images' must be a non-empty list.")

        val_tile_h, val_tile_w = map(int, tile_size)
        if not (val_tile_h > 0 and val_tile_w > 0):
            raise ValueError("tile_size must be a tuple or list of two positive integers.")

        try:
            ref_image_orig = images[0]
            if not isinstance(ref_image_orig, np.ndarray):
                raise TypeError(language_config.IMAGE_DATA_MUST_BE_VALID)

            h_orig, w_orig = ref_image_orig.shape[:2]
            channels_orig = ref_image_orig.shape[2] if ref_image_orig.ndim == 3 else 1
            dtype_orig = ref_image_orig.dtype

            channels_buffer_cpp = 3

        except (AttributeError, IndexError, TypeError) as e:
            raise ValueError(language_config.FIRST_IMAGE_CANNOT_BE_OBTAINED.format(e))

        if dtype_orig not in (np.uint8, np.uint16):
            raise TypeError(language_config.IMAGE_BIT_REQUIRED)

        block_h = val_tile_h
        block_w = val_tile_w
        search_radius = 0 
        
        try:
            c_interface = SimilarityV2MotionInterface(lib_path)
        except (FileNotFoundError, OSError, AttributeError) as e:
           raise RuntimeError(f"Failed to initialize C++ interface: {e}")

        reference_image_float32_3ch = normalize_image(ref_image_orig, dtype_orig)
        h_ref, w_ref, channels_ref_check = reference_image_float32_3ch.shape

        if channels_ref_check != channels_buffer_cpp:
             raise RuntimeError(language_config.COLOR_CHANNEL_DOES_NOT_MATCH +
                                f" Expected {channels_buffer_cpp}, got {channels_ref_check} from normalized ref.")

        final_image_sum = np.ascontiguousarray(np.zeros((h_ref, w_ref, channels_buffer_cpp), dtype=np.float32))
        weight_map_sum = np.ascontiguousarray(np.zeros((h_ref, w_ref), dtype=np.float32)) # Weight map selalu 1 channel

        tile_h_proc = min(val_tile_h, h_ref)
        tile_w_proc = min(val_tile_w, w_ref)

        step_y = max(int(tile_h_proc * (1 - overlap)), 1)
        step_x = max(int(tile_w_proc * (1 - overlap)), 1)

        if h_ref > tile_h_proc:
            row_starts = np.arange(0, h_ref - tile_h_proc + 1, step_y, dtype=np.int32)
            if not row_starts.size or row_starts[-1] != h_ref - tile_h_proc :
                row_starts = np.append(row_starts, h_ref - tile_h_proc).astype(np.int32)
        else: 
            row_starts = np.array([0], dtype=np.int32)

        if w_ref > tile_w_proc:
            col_starts = np.arange(0, w_ref - tile_w_proc + 1, step_x, dtype=np.int32)
            if not col_starts.size or col_starts[-1] != w_ref - tile_w_proc:
                col_starts = np.append(col_starts, w_ref - tile_w_proc).astype(np.int32)
        else:
            col_starts = np.array([0], dtype=np.int32)

        row_starts = np.ascontiguousarray(np.unique(row_starts))
        col_starts = np.ascontiguousarray(np.unique(col_starts))

        base_window = gaussian_window((tile_h_proc, tile_w_proc))

        try:
            global_avg_sigma = c_interface.estimate_noise(
                reference_image_float32_3ch, h_ref, w_ref, channels_buffer_cpp,
                tile_h_proc, tile_w_proc,
                row_starts, col_starts 
            )
        except Exception as e:
            global_avg_sigma = 0.03 
            
        frame_max_multiplier = self._calculate_dynamic_max_multiplier(global_avg_sigma)
        noise_level_score = self._calculate_noise_level_score(global_avg_sigma)
        print(f"  Cleanliness Score (0-100, 100=clean): {noise_level_score:.1f}")

        scale_value = np.float32(np.iinfo(dtype_orig).max)
        num_images_total = len(images)
        processed_frames_count = 0
        progress_cap_percent = 95 
        
        for i, current_image_orig in enumerate(images):
            if not isinstance(current_image_orig, np.ndarray):
                continue

            if update_progress:
                current_progress_val = 0
                if total_overall_images is not None and total_overall_images > 0:
                    overall_processed_count = images_processed_so_far + i + 1
                    current_progress_val = int((overall_processed_count / total_overall_images) * progress_cap_percent)
                    progress_message = language_config.IMAGE_PROCESS_IN_PROGRESS.format(overall_processed_count, total_overall_images)
                else:
                    current_progress_val = int(((i + 1) / num_images_total) * progress_cap_percent)
                    progress_message = language_config.ANALYZING_IMAGE.format(i + 1, num_images_total)
                update_progress(current_progress_val, progress_message)

            if stop_requested and stop_requested():
                break

            try:
                if current_image_orig.shape[0] != h_orig or current_image_orig.shape[1] != w_orig:
                    continue
                if current_image_orig.dtype != dtype_orig:
                    continue
            except Exception as e:
                continue

            current_image_float32_3ch = normalize_image(current_image_orig, dtype_orig)
            if current_image_float32_3ch.shape[2] != channels_buffer_cpp:
                continue

            try:
                c_interface.accumulate_frame(
                    final_image_sum, weight_map_sum,
                    current_image_float32_3ch, reference_image_float32_3ch,
                    base_window, row_starts, col_starts,
                    tile_h_proc, tile_w_proc, h_ref, w_ref, channels_buffer_cpp,
                    block_h, block_w, search_radius, 
                    frame_max_multiplier, 
                    mbm_mad_sensitivity, mbm_noise_mad_offset_factor,
                    mbm_confidence_skip_dft_threshold, coarse_alignment_search_margin,
                    freq_merge_wiener_c_factor
                )
                processed_frames_count += 1
            except RuntimeError as e: 
               pass
            except Exception as e:
                pass
        if processed_frames_count == 0:
            if channels_orig == 1 and ref_image_orig.ndim == 2: # input asli grayscale
                 return ref_image_orig.astype(dtype_orig, copy=False)
            elif channels_orig == 3 and ref_image_orig.ndim == 3: # input asli berwarna
                 return ref_image_orig.astype(dtype_orig, copy=False)
            else:
                 output_shape = (h_orig, w_orig) if channels_orig == 1 else (h_orig, w_orig, channels_orig)
                 return np.zeros(output_shape, dtype=dtype_orig)


        try:
            c_interface.normalize_accumulated(final_image_sum, weight_map_sum, h_ref, w_ref, channels_buffer_cpp)
        except Exception as e:
            raise RuntimeError(language_config.NORMALIZATION_FAILED.format(e))

        if save_weight_map_path:
            print(language_config.OUTPUT_SAVE_WEIGHT_MAP.format(save_weight_map_path))
            try:
                if processed_frames_count > 0:
                    normalized_weights_vis = weight_map_sum / float(processed_frames_count)
                else:
                    normalized_weights_vis = np.zeros_like(weight_map_sum)

                normalized_weights_vis = np.clip(normalized_weights_vis, 0.0, 1.0)
                weight_map_to_save = (normalized_weights_vis * 255).astype(np.uint8)

                os.makedirs(os.path.dirname(save_weight_map_path), exist_ok=True)
                success_save = cv2.imwrite(save_weight_map_path, weight_map_to_save)
                if success_save:
                    print(language_config.SAVING_WEIGHT_MAP)
                else:
                    print(language_config.FAILED_TO_SAVE_WEIGHT_MAP_TO_PATH.format(save_weight_map_path))
            except Exception as e:
                traceback.print_exc()

        final_image_scaled = final_image_sum * scale_value

        final_image_output = None
        if channels_orig == 1:
            final_image_gray_float = final_image_scaled[:, :, 0]
            final_image_output = np.clip(final_image_gray_float, 0, np.iinfo(dtype_orig).max).astype(dtype_orig, copy=False)
        elif channels_orig == 3: 
            final_image_output = np.clip(final_image_scaled, 0, np.iinfo(dtype_orig).max).astype(dtype_orig, copy=False)
        elif channels_orig == 4:
            final_image_output = np.clip(final_image_scaled, 0, np.iinfo(dtype_orig).max).astype(dtype_orig, copy=False)
        else:
            pass

        if stop_requested and stop_requested() and processed_frames_count < num_images_total:
            pass
        return final_image_output

def main(db_path, update_progress=None, stop_requested=None, batch_size=10,
         single_process=None, batch_id=None, save_final_weight_map=False, progress_bar=None):
    try:
        general_settings= load_similarity_v2_config()
        image_processor = SimilarityAlgorithmV2(db_path)
        
        sim_tile_size_int = general_settings.get("similarity_v2_tile_size", 16)
        sim_overlap_percent = general_settings.get("similarity_v2_overlap_percent", 40.0)
        sim_v2_mbm_noise_mad_offset_factor = general_settings.get("similarity_v2_mbm_noise_mad_offset_factor", 0.5)
        sim_v2_mbm_mad_sensitivity = general_settings.get("similarity_v2_mbm_mad_sensitivity", 20.0)
        sim_v2_mbm_confidence_skip_dft_threshold = general_settings.get("similarity_v2_mbm_confidence_skip_dft_threshold", 0.9)
        sim_v2_freq_merge_wiener_c_factor = general_settings.get("similarity_v2_freq_merge_wiener_c_factor", 2.0)
        sim_v2_coarse_alignment_search_margin = general_settings.get("similarity_v2_coarse_alignment_search_margin", 12)
       
        tile_size_tuple = (sim_tile_size_int, sim_tile_size_int)
        overlap_ratio = sim_overlap_percent / 100.0

        output_name_base = ""
        image_paths = []
        align_dir = os.path.join("database", "align")
        os.makedirs(align_dir, exist_ok=True) # Pastikan align_dir dibuat

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
            return # Keluar jika tidak ada gambar

        # --- Setup Path Output ---
        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)
        output_name_base_safe = "".join(c for c in output_name_base if c.isalnum() or c in ('_', '-')).rstrip()
        if not output_name_base_safe: output_name_base_safe = "stack_result" # Fallback name
        output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_similarityV2.tif")
        weight_map_output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_similarity_weight_map.png")
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))
        if save_final_weight_map:
             print(language_config.OUTPUT_SAVE_WEIGHT_MAP.format(weight_map_output_path))

        # --- Ekstraksi Metadata ---
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
                        if stop_requested and stop_requested(): break # Cek lagi setelah loop key

                        if not batch_images:
                            print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num))
                            continue 
                        batch_images, new_size = resize_all_with_padding(batch_images, method="preserve")
                        print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images)))
                        try:
                            batch_result = image_processor.similarity_mfnr(
                                batch_images,
                                tile_size=tile_size_tuple,
                                overlap=overlap_ratio,
                                mbm_noise_mad_offset_factor=sim_v2_mbm_noise_mad_offset_factor,
                                mbm_mad_sensitivity=sim_v2_mbm_mad_sensitivity,
                                mbm_confidence_skip_dft_threshold=sim_v2_mbm_confidence_skip_dft_threshold,
                                freq_merge_wiener_c_factor=sim_v2_freq_merge_wiener_c_factor,
                                coarse_alignment_search_margin=sim_v2_coarse_alignment_search_margin,
                                update_progress=update_progress,
                                stop_requested=stop_requested,
                                total_overall_images=total_images,
                                images_processed_so_far=images_processed_count
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
                if stop_requested and stop_requested(): 
                    break
                batch_images, new_size = resize_all_with_padding(batch_images, method="preserve")
                        
                if not batch_images:
                    print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num))
                    continue

                print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images)))
                try:
                    batch_result = image_processor.similarity_mfnr(
                    batch_images,
                    tile_size=tile_size_tuple,
                    overlap=overlap_ratio,
                    mbm_noise_mad_offset_factor=sim_v2_mbm_noise_mad_offset_factor,
                    mbm_mad_sensitivity=sim_v2_mbm_mad_sensitivity,
                    mbm_confidence_skip_dft_threshold=sim_v2_mbm_confidence_skip_dft_threshold,
                    freq_merge_wiener_c_factor=sim_v2_freq_merge_wiener_c_factor,
                    coarse_alignment_search_margin=sim_v2_coarse_alignment_search_margin,
                    update_progress=update_progress,
                    stop_requested=stop_requested,
                    total_overall_images=total_images,
                    images_processed_so_far=images_processed_count
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

            # Wrapper untuk progress callback fine-tuning
            def fine_tuning_update_progress(inner_progress, message):
                # Map progress internal [0, 100] ke rentang [start, end]
                mapped_progress = fine_tuning_start_progress + int((inner_progress / 100.0) * (fine_tuning_end_progress - fine_tuning_start_progress))
                if update_progress:
                    # Jangan update jika sudah diminta berhenti
                    if not (stop_requested and stop_requested()):
                        update_progress(mapped_progress, language_config.ENHANCEMENT.format(message))

            if update_progress: update_progress(fine_tuning_start_progress, language_config.STARTING_ENHANCEMENT)

            final_weight_map_path_arg = weight_map_output_path if save_final_weight_map else None
            if final_weight_map_path_arg:
                 print(f"Final weight map saving is ENABLED to: {final_weight_map_path_arg}")
            else:
                 print("Final weight map saving is DISABLED.")

            final_result = None
            try:
                 final_result = image_processor.similarity_mfnr(
                 processed_batches_results,
                 tile_size=tile_size_tuple,
                 overlap=overlap_ratio,
                 mbm_noise_mad_offset_factor=sim_v2_mbm_noise_mad_offset_factor,
                 mbm_mad_sensitivity=sim_v2_mbm_mad_sensitivity,
                 mbm_confidence_skip_dft_threshold=sim_v2_mbm_confidence_skip_dft_threshold,
                 freq_merge_wiener_c_factor=sim_v2_freq_merge_wiener_c_factor,
                 coarse_alignment_search_margin=sim_v2_coarse_alignment_search_margin,
                 update_progress=fine_tuning_update_progress,
                 stop_requested=stop_requested,
                 save_weight_map_path=final_weight_map_path_arg,
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
                print(language_config.FAILED_IMAGE_ENHANCEMENT)
                if update_progress: update_progress(100, language_config.FAILED_IMAGE_ENHANCEMENT)

        elif not (stop_requested and stop_requested()):
            print(language_config.DATA_FAILED_COMPLETION_CREATED)
            if update_progress:
                update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED)

        if stop_requested and stop_requested():
             if update_progress and progress_bar:
                 update_progress(progress_bar.value())


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


def running_similarity_v2(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_SIMILARITY_V2)
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