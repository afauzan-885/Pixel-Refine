import gc
import math
import cv2
import numpy as np
import sqlite3
import os
import json
import concurrent.futures
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
from PyQt6.QtCore import Qt
import h5py

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import compute_global_crop, crop_image, extract_all_metadata, extract_exif, get_all_image_paths_for_single_process, load_images_from_paths, save_align_to_folder, save_to_hdf5
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config
from config import ALGORITHM_PARAMETER_SETTINGS_FILE

class AKAZEAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

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

    @staticmethod
    def load_akaze_config(config_filename=None):
        """
        Membaca konfigurasi AKAZE dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "akaze_threshold": 0.001,
            "akaze_nOctaves": 4,
            "akaze_nOctaveLayers": 4,
            "ratio_threshold": 0.75,
            "ransacThreshold": 5.0,
            "transformation": "homography",
            "keep_edges": False,
            "enable_cropping": False,
            "save_align": False,
            "command_save_to_hd5f": True,
            "use_multi_core": True,
            "tile_sizes_w_h_overlap": [
                (256, 256, 0.25),
                (128, 128, 0.25),

            ],
            "skip_warp_shift_threshold": 1.4,
            "skip_warp_response_threshold": 1.7, 
            "fallback_tile_size_w": 128, 
            "fallback_tile_size_h": 128,
            "overlap_percent": 0.25,  
            "use_multi_core_tile_processing": True,
            "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image")
        }

        if config_filename is None:
            config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE 
        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("TILE_ALIGN", default_config)
        except Exception as e:
            return default_config
            
    @staticmethod
    def load_akaze_config_for_batch(config_filename=None):
        """
        Membaca konfigurasi AKAZE dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "akaze_threshold": 0.001,
            "akaze_nOctaves": 4,
            "akaze_nOctaveLayers": 4,
            "ratio_threshold": 0.75,
            "ransacThreshold": 5.0,
            "transformation": "homography",
            "keep_edges": False,
            "enable_cropping": False,
            "save_align": False,
            "command_save_to_hd5f": True,
            "use_multi_core": False,
            "tile_sizes_w_h_overlap": [ # Default multi-scale, dari besar ke kecil
                (512, 512, 0.25),
                (256, 256, 0.25),
                (128, 128, 0.25)
            ],
            "fallback_tile_size_w": 256, # Fallback jika tile_sizes_w_h_overlap tidak ada/kosong
            "fallback_tile_size_h": 256,
            "overlap_percent": 0.25,  # GANTI overlap_px menjadi overlap_percent (misal 25%)
            "use_multi_core_tile_processing": True,
            "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image")
        }

        if config_filename is None:
            config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE 

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("Tile_Align_BATCH", default_config)
        except Exception as e:
            print("Error loading AKAZE configuration:", e)
            return default_config
        
    def prepare_gray_akaze(self, img):
        if img is None: raise ValueError("Input image is None.")
        # Pastikan gambar adalah contiguous array, terutama setelah slicing atau warping
        if not img.flags['C_CONTIGUOUS']:
            img = np.ascontiguousarray(img)

        if img.ndim == 3:
            if img.shape[2] == 3: gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            elif img.shape[2] == 4: gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            else: raise ValueError(f"Unsupported number of channels for 3D image: {img.shape[2]}")
        elif img.ndim == 2: gray = img.copy() # Salin agar tidak mengubah asli jika sudah grayscale
        else:
            raise ValueError(f"Invalid image dimensions: {img.shape}")

        if gray.dtype != np.uint8:
            if gray.dtype in [np.float32, np.float64]:
                # Jika float, asumsikan rentang 0-1 atau 0-255
                max_val = np.max(gray)
                if max_val <= 1.0 and np.min(gray) >=0.0 : # Asumsi 0-1
                     gray_norm = (gray * 255.0).astype(np.uint8)
                elif max_val <=255.0 and np.min(gray) >=0.0: # Asumsi sudah 0-255 tapi float
                     gray_norm = gray.astype(np.uint8)
                else: # Normalisasi umum jika rentang tidak diketahui
                    gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            elif gray.dtype == np.uint16:
                gray_norm = (gray / 256.0).astype(np.uint8) # Konversi uint16 ke uint8
            else: # Tipe lain, coba normalisasi umum
                gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            return gray_norm
        return gray

    def _create_hanning_window_2d(self, h, w):
        if h <= 0 or w <= 0: # Handle kasus tile sangat kecil atau invalid
            return np.ones((max(1,h), max(1,w)), dtype=np.float32) # Kembalikan array 1 jika ukuran tidak valid
        hann_h = np.hanning(h) if h > 1 else np.array([1.0])
        hann_w = np.hanning(w) if w > 1 else np.array([1.0])
        hann_2d = np.outer(hann_h, hann_w)
        return hann_2d

    def _process_single_tile(self, tile_idx_i, tile_idx_j,
                             base_gray_enhanced, target_gray_enhanced, target_image_to_warp,
                             tile_w, tile_h,
                             overlap_px_w, overlap_px_h,
                             img_h, img_w,
                             akaze_detector,
                             local_align_config): # local_align_config sekarang akan berisi parameter skip_warp

        # ... (Perhitungan koordinat tile dan ekstraksi tile_target_content_to_warp sama) ...
        x_coord_grid = tile_idx_i * (tile_w - overlap_px_w)
        y_coord_grid = tile_idx_j * (tile_h - overlap_px_h)
        current_tile_global_x_start = max(0, int(x_coord_grid))
        current_tile_global_y_start = max(0, int(y_coord_grid))
        current_tile_global_x_end = min(img_w, current_tile_global_x_start + tile_w)
        current_tile_global_y_end = min(img_h, current_tile_global_y_start + tile_h)
        current_tile_processing_w = current_tile_global_x_end - current_tile_global_x_start
        current_tile_processing_h = current_tile_global_y_end - current_tile_global_y_start
        tile_target_content_to_warp = target_image_to_warp[current_tile_global_y_start:current_tile_global_y_end,
                                                           current_tile_global_x_start:current_tile_global_x_end]

        # ... (Logika skip awal jika tile terlalu kecil, sama) ...
        if current_tile_processing_w <= max(1, overlap_px_w // 2) or \
           current_tile_processing_h <= max(1, overlap_px_h // 2) or \
           current_tile_processing_w < 16 or current_tile_processing_h < 16:
            if tile_target_content_to_warp.size == 0: return None, None, None
            hanning_win_skip = self._create_hanning_window_2d(tile_target_content_to_warp.shape[0], tile_target_content_to_warp.shape[1])
            if tile_target_content_to_warp.ndim == 3: hanning_win_skip = np.stack([hanning_win_skip]*tile_target_content_to_warp.shape[2], axis=-1)
            windowed_tile_skip = (tile_target_content_to_warp.astype(np.float32) * hanning_win_skip)
            return windowed_tile_skip, (current_tile_global_y_start, current_tile_global_x_start), np.float32([[1,0,0],[0,1,0]])

        # ... (Ekstraksi tile_base_for_phase dan tile_target_for_phase sama) ...
        tile_base_for_phase = base_gray_enhanced[current_tile_global_y_start:current_tile_global_y_end,
                                                 current_tile_global_x_start:current_tile_global_x_end].astype(np.float32)
        tile_target_for_phase = target_gray_enhanced[current_tile_global_y_start:current_tile_global_y_end,
                                                     current_tile_global_x_start:current_tile_global_x_end].astype(np.float32)
        
        # ... (Pengecekan ukuran tile sama) ...
        if tile_base_for_phase.size == 0 or tile_target_for_phase.size == 0 or tile_target_content_to_warp.size == 0 or \
           tile_base_for_phase.shape != tile_target_for_phase.shape:
            if tile_target_content_to_warp.size > 0:
                # ... (logika skip jika tile target masih ada) ...
                hanning_win_skip = self._create_hanning_window_2d(tile_target_content_to_warp.shape[0], tile_target_content_to_warp.shape[1])
                if tile_target_content_to_warp.ndim == 3: hanning_win_skip = np.stack([hanning_win_skip]*tile_target_content_to_warp.shape[2], axis=-1)
                windowed_tile_skip = (tile_target_content_to_warp.astype(np.float32) * hanning_win_skip)
                return windowed_tile_skip, (current_tile_global_y_start, current_tile_global_x_start), np.float32([[1,0,0],[0,1,0]])
            return None, None, None


        M_local = np.float32([[1, 0, 0], [0, 1, 0]]) # Default ke matriks identitas
        perform_warp = True # Flag untuk menentukan apakah warp perlu dilakukan

        # Ambil parameter skip dari konfigurasi
        skip_warp_enabled = local_align_config.get("skip_warp_enabled", True)
        cfg_skip_shift = local_align_config.get("skip_warp_shift_threshold", 0.5)
        cfg_skip_response = local_align_config.get("skip_warp_response_threshold", 0.8)

        dx, dy, response_val = None, None, 0.0

        try:
            tile_base_for_phase_cont = np.ascontiguousarray(tile_base_for_phase)
            tile_target_for_phase_cont = np.ascontiguousarray(tile_target_for_phase)
            shift, response = cv2.phaseCorrelate(tile_base_for_phase_cont, tile_target_for_phase_cont)

            if shift is not None and shift[0] is not None and shift[1] is not None:
                dx, dy = shift[0], shift[1]
                response_val = response if response is not None else 0.0

                if skip_warp_enabled:
                    magnitude_shift = np.sqrt(dx**2 + dy**2)
                    if magnitude_shift < cfg_skip_shift and response_val > cfg_skip_response:
                        # Pergeseran kecil DAN respons tinggi, maka skip warp
                        perform_warp = False
                        # M_local sudah identitas
                        # print(f"  Tile ({tile_idx_i},{tile_idx_j}) - Skipping warp: shift={magnitude_shift:.2f}, resp={response_val:.2f}")
                    else:
                        # Perlu warp, hitung M_local
                        M_local = np.float32([[1, 0, -dx], [0, 1, -dy]])
                else:
                    # Skip warp tidak diaktifkan, selalu hitung M_local jika shift valid
                    M_local = np.float32([[1, 0, -dx], [0, 1, -dy]])
            else:
                # phaseCorrelate gagal mengembalikan shift yang valid
                # print(f"Warning: phaseCorrelate returned None for shift in tile ({tile_idx_i},{tile_idx_j}). Using identity M_local.")
                perform_warp = False # Tidak ada info pergeseran, jadi jangan warp (atau M_local identitas sudah cukup)
        
        except cv2.error as e:
            # print(f"cv2.error in phaseCorrelate for tile ({tile_idx_i},{tile_idx_j}): {e}. Using identity M_local.")
            perform_warp = False # Error, jangan warp
        except Exception as e_gen:
            # print(f"General error in phaseCorrelate for tile ({tile_idx_i},{tile_idx_j}): {e_gen}. Using identity M_local.")
            perform_warp = False # Error, jangan warp


        output_size_warp = (tile_base_for_phase.shape[1], tile_base_for_phase.shape[0])
        
        if perform_warp:
            try:
                tile_target_content_to_warp_cont = np.ascontiguousarray(tile_target_content_to_warp)
                warped_tile_target_content = cv2.warpAffine(tile_target_content_to_warp_cont, M_local,
                                                            output_size_warp, flags=cv2.INTER_AREA, # Atau INTER_LINEAR
                                                            borderMode=cv2.BORDER_REFLECT_101)
            except cv2.error as e:
                # print(f"cv2.error in warpAffine for tile ({tile_idx_i},{tile_idx_j}): {e}. Using original tile content.")
                warped_tile_target_content = tile_target_content_to_warp.copy() # Fallback ke original
            except Exception as e_gen:
                # print(f"General error in warpAffine for tile ({tile_idx_i},{tile_idx_j}): {e_gen}. Using original tile content.")
                warped_tile_target_content = tile_target_content_to_warp.copy() # Fallback ke original
        else:
            # Jika tidak perlu warp (karena skip atau error di phaseCorrelate),
            # warped_tile_target_content adalah konten asli tile target. M_local adalah identitas.
            warped_tile_target_content = tile_target_content_to_warp.copy()


        if warped_tile_target_content is None or warped_tile_target_content.size == 0:
            # Fallback jika warped_tile_target_content masih None atau kosong
            if tile_target_content_to_warp.size > 0:
                # print(f"Warning: warped_tile_target_content is None/empty, reverting to original for windowing.")
                warped_tile_target_content = tile_target_content_to_warp.copy()
            else: # Jika tile asli juga kosong, tidak ada yang bisa dilakukan
                 return None, None, None

        hanning_win = self._create_hanning_window_2d(warped_tile_target_content.shape[0], warped_tile_target_content.shape[1])
        if warped_tile_target_content.ndim == 3:
            hanning_win = np.stack([hanning_win] * warped_tile_target_content.shape[2], axis=-1)

        windowed_tile = (warped_tile_target_content.astype(np.float32) * hanning_win)
        return windowed_tile, (current_tile_global_y_start, current_tile_global_x_start), M_local

    # --- FUNGSI align_local DIUBAH MENJADI align_local_multiscale ---
    def align_local_multiscale(self, base_image_orig, target_image_orig, config_to_use):
        if base_image_orig is None or target_image_orig is None:
            print("Error: Base or target image is None in align_local_multiscale.")
            return None, None

        # Dapatkan konfigurasi tile dari config_to_use
        tile_configs = config_to_use.get("tile_sizes_w_h_overlap", [])
        if not tile_configs: # Fallback jika tidak ada atau kosong
            fb_w = config_to_use.get("fallback_tile_size_w", 256)
            fb_h = config_to_use.get("fallback_tile_size_h", 256)
            fb_ov = config_to_use.get("fallback_overlap_percent", 0.25)
            tile_configs = [(fb_w, fb_h, fb_ov)]
            print(f"Warning: 'tile_sizes_w_h_overlap' not found or empty in config. Using fallback: {tile_configs}")

        use_multicore_tiles = bool(config_to_use.get("use_multi_core_tile_processing", True))
        dummy_akaze_detector = None # Masih placeholder

        current_target_image_to_align = target_image_orig.copy()
        all_final_local_matrices = {} # Untuk menyimpan matriks dari skala terkecil

        img_h_orig, img_w_orig = base_image_orig.shape[:2]

        # Persiapkan base_gray sekali saja karena tidak berubah antar skala
        base_gray_prepared = self.prepare_gray_akaze(base_image_orig)
        try:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            base_gray_enhanced_const = clahe.apply(base_gray_prepared)
        except Exception as e:
            print(f"Error applying CLAHE to base image: {e}. Using original gray.")
            base_gray_enhanced_const = base_gray_prepared

        final_aligned_image = None # Inisialisasi

        # Loop dari tile terbesar ke terkecil (coarse-to-fine)
        for scale_idx, (tile_w, tile_h, overlap_percent) in enumerate(tile_configs):
            print(f"\nProcessing Scale {scale_idx+1}/{len(tile_configs)}: Tile Size {tile_w}x{tile_h}, Overlap {overlap_percent*100:.1f}%")

            if not (0 <= overlap_percent < 1.0):
                overlap_percent = np.clip(overlap_percent, 0.01, 0.9)
                print(f"  Adjusted overlap_percent to {overlap_percent*100:.1f}%")

            overlap_px_w = int(tile_w * overlap_percent)
            overlap_px_h = int(tile_h * overlap_percent)
            if overlap_px_w >= tile_w : overlap_px_w = max(0, tile_w -1)
            if overlap_px_h >= tile_h : overlap_px_h = max(0, tile_h -1)
            overlap_px_w = max(0, overlap_px_w) # Pastikan tidak negatif
            overlap_px_h = max(0, overlap_px_h) # Pastikan tidak negatif


            # Persiapkan target_gray untuk skala saat ini (dari current_target_image_to_align)
            target_gray_current_scale_prepared = self.prepare_gray_akaze(current_target_image_to_align)
            try:
                target_gray_enhanced_current_scale = clahe.apply(target_gray_current_scale_prepared)
            except Exception as e:
                print(f"  Error applying CLAHE to target image at current scale: {e}. Using original gray.")
                target_gray_enhanced_current_scale = target_gray_current_scale_prepared

            # Ukuran gambar (img_h, img_w) tetap mengacu pada ukuran original
            # Jumlah channel untuk stitching dari current_target_image_to_align
            num_channels_current = current_target_image_to_align.shape[2] if current_target_image_to_align.ndim == 3 else 1

            # Inisialisasi buffer untuk stitching pada skala ini
            # Ukuran buffer harus sesuai dengan dimensi gambar asli
            if num_channels_current > 1:
                aligned_target_stitched_float_scale = np.zeros((img_h_orig, img_w_orig, num_channels_current), dtype=np.float32)
            else:
                aligned_target_stitched_float_scale = np.zeros((img_h_orig, img_w_orig), dtype=np.float32)
            weight_sum_map_scale = np.zeros((img_h_orig, img_w_orig), dtype=np.float32)

            step_w = tile_w - overlap_px_w
            step_h = tile_h - overlap_px_h
            if step_w <= 0 : step_w = 1
            if step_h <= 0 : step_h = 1

            # Jumlah tile berdasarkan dimensi gambar asli
            num_tiles_x = math.ceil(img_w_orig / step_w) if img_w_orig > tile_w else 1
            num_tiles_y = math.ceil(img_h_orig / step_h) if img_h_orig > tile_h else 1
            if img_w_orig <= tile_w: num_tiles_x = 1 # Kasus gambar lebih kecil dari tile
            if img_h_orig <= tile_h: num_tiles_y = 1 # Kasus gambar lebih kecil dari tile

            print(f"  Num tiles (x,y): ({num_tiles_x}, {num_tiles_y}), Step (w,h): ({step_w}, {step_h})")
            print(f"  Tile (w,h): ({tile_w}, {tile_h}), Overlap_px (w,h): ({overlap_px_w}, {overlap_px_h})")


            tile_params_list_scale = []
            for i in range(num_tiles_x):
                for j in range(num_tiles_y):
                    tile_params_list_scale.append((
                        i, j,
                        base_gray_enhanced_const, # Base selalu sama
                        target_gray_enhanced_current_scale, # Target gray dari skala ini
                        current_target_image_to_align, # Gambar warna/asli yang akan di-warp
                        tile_w, tile_h, overlap_px_w, overlap_px_h,
                        img_h_orig, img_w_orig, # Gunakan dimensi original untuk bounds
                        dummy_akaze_detector,
                        config_to_use
                    ))
            if not tile_params_list_scale:
                print("  Warning: No tiles to process for this scale. Skipping scale.")
                if scale_idx == len(tile_configs) -1: # Jika ini skala terakhir dan tidak ada tile
                    final_aligned_image = current_target_image_to_align.copy() # Gunakan hasil dari skala sebelumnya
                continue


            results_scale = []
            if use_multicore_tiles and len(tile_params_list_scale) > 1:
                # print(f"  Using ThreadPoolExecutor with {os.cpu_count()} workers for {len(tile_params_list_scale)} tiles.")
                with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                    future_to_tile = {executor.submit(self._process_single_tile, *params): params for params in tile_params_list_scale}
                    for future_idx, future in enumerate(concurrent.futures.as_completed(future_to_tile)):
                        # print(f"    Processing future {future_idx+1}/{len(tile_params_list_scale)}")
                        try:
                            result_tile = future.result()
                            if result_tile and result_tile[0] is not None: results_scale.append(result_tile)
                        except Exception as exc:
                            params_failed = future_to_tile[future]
                            print(f"  Tile ({params_failed[0]},{params_failed[1]}) processing (scale {tile_w}x{tile_h}) generated an exception: {exc}")
            else:
                # print(f"  Processing {len(tile_params_list_scale)} tiles sequentially.")
                for idx, params_set in enumerate(tile_params_list_scale):
                    # print(f"    Processing tile {idx+1}/{len(tile_params_list_scale)}")
                    try:
                        result_tile = self._process_single_tile(*params_set)
                        if result_tile and result_tile[0] is not None: results_scale.append(result_tile)
                    except Exception as exc:
                        print(f"  Tile {params_set[0]},{params_set[1]} (scale {tile_w}x{tile_h}) generated an exception: {exc}")

            if not results_scale:
                print("  Warning: No valid results from tile processing at this scale. Using previous scale's result.")
                # Jika ini skala terakhir dan tidak ada hasil, maka final_aligned_image akan tetap dari skala sebelumnya atau original target
                if scale_idx == len(tile_configs) -1 :
                     if final_aligned_image is None: # Jika ini juga skala pertama
                         final_aligned_image = current_target_image_to_align.copy()
                # else: # Jika bukan skala terakhir, current_target_image_to_align tidak berubah, lanjut ke skala berikutnya
                continue


            # Stitching untuk skala saat ini
            temp_local_matrices_scale = {}
            for windowed_tile_float, (y_start_global, x_start_global), M_loc in results_scale:
                if windowed_tile_float is None: continue

                h_tile_processed, w_tile_processed = windowed_tile_float.shape[:2]

                # Pastikan ROI tidak keluar batas dari buffer stitching
                y_end_global = min(y_start_global + h_tile_processed, img_h_orig)
                x_end_global = min(x_start_global + w_tile_processed, img_w_orig)

                actual_h_to_place = y_end_global - y_start_global
                actual_w_to_place = x_end_global - x_start_global

                if actual_h_to_place <= 0 or actual_w_to_place <= 0: continue

                current_tile_data_to_place = windowed_tile_float[:actual_h_to_place, :actual_w_to_place]
                target_roi_buffer = aligned_target_stitched_float_scale[y_start_global:y_end_global, x_start_global:x_end_global]

                if target_roi_buffer.shape[:2] != current_tile_data_to_place.shape[:2]:
                    # print(f"  Warning: Shape mismatch during stitching. ROI: {target_roi_buffer.shape}, Tile: {current_tile_data_to_place.shape}. Skipping tile.")
                    # Ini bisa terjadi jika tile diproses dengan ukuran berbeda dari yang diharapkan di buffer
                    # Misalnya, jika tile di tepi dan warped_tile_target_content memiliki ukuran berbeda
                    # Coba resize current_tile_data_to_place agar sesuai jika memungkinkan, atau skip.
                    # Untuk sekarang, kita skip agar tidak error.
                    continue

                # Logika penanganan channel yang sudah ada
                if num_channels_current > 1:
                    if target_roi_buffer.ndim == 3 and current_tile_data_to_place.ndim == 3 and target_roi_buffer.shape[2] == current_tile_data_to_place.shape[2]:
                        target_roi_buffer += current_tile_data_to_place
                    else:
                        # print(f"  Warning: Channel/dim mismatch for color image. ROI: {target_roi_buffer.shape}, Tile: {current_tile_data_to_place.shape}")
                        continue
                elif num_channels_current == 1:
                    # Memastikan current_tile_data_to_place juga 2D jika target_roi_buffer adalah 2D
                    if current_tile_data_to_place.ndim == 3 and current_tile_data_to_place.shape[2] == 1:
                        current_tile_data_to_place = np.squeeze(current_tile_data_to_place, axis=2)

                    if target_roi_buffer.ndim == 2 and current_tile_data_to_place.ndim == 2:
                        target_roi_buffer += current_tile_data_to_place
                    # (kasus lain dari kode asli Anda bisa ditambahkan jika relevan untuk grayscale)
                    else:
                        # print(f"  Warning: Channel/dim mismatch for grayscale image. ROI: {target_roi_buffer.shape}, Tile: {current_tile_data_to_place.shape}")
                        continue

                hanning_for_weight = self._create_hanning_window_2d(current_tile_data_to_place.shape[0], current_tile_data_to_place.shape[1])
                weight_sum_map_scale[y_start_global:y_end_global, x_start_global:x_end_global] += hanning_for_weight

                if M_loc is not None:
                    grid_idx_x = (x_start_global // step_w) if step_w > 0 else 0
                    grid_idx_y = (y_start_global // step_h) if step_h > 0 else 0
                    temp_local_matrices_scale[(grid_idx_x, grid_idx_y)] = M_loc
                    if scale_idx == len(tile_configs) - 1: # Jika ini skala terkecil/terakhir
                        all_final_local_matrices[(grid_idx_x, grid_idx_y)] = M_loc

            # Normalisasi hasil stitching untuk skala ini
            if num_channels_current > 1:
                weight_sum_map_3d_scale = np.stack([weight_sum_map_scale] * num_channels_current, axis=-1)
                denominator_scale = np.where(weight_sum_map_3d_scale < 1e-6, 1.0, weight_sum_map_3d_scale)
            else: # num_channels_current == 1
                # Pastikan weight_sum_map_scale dan aligned_target_stitched_float_scale keduanya 2D atau broadcast-compatible
                if aligned_target_stitched_float_scale.ndim == 3 and num_channels_current == 1: # Jika hasil stitching masih 3D (misal, (H,W,1))
                    aligned_target_stitched_float_scale = np.squeeze(aligned_target_stitched_float_scale, axis=2)
                denominator_scale = np.where(weight_sum_map_scale < 1e-6, 1.0, weight_sum_map_scale)

            # Hindari division by zero jika denominator_scale ada yang nol (meskipun np.where sudah menangani)
            denominator_scale[denominator_scale == 0] = 1.0
            intermediate_aligned_float_scale = aligned_target_stitched_float_scale / denominator_scale

            # Update current_target_image_to_align untuk iterasi skala berikutnya atau sebagai hasil akhir
            # Penting: Konversi kembali ke tipe data asli dari target_image_orig
            if target_image_orig.dtype == np.uint8:
                current_target_image_to_align = np.clip(intermediate_aligned_float_scale, 0, 255).astype(np.uint8)
            elif target_image_orig.dtype == np.uint16:
                current_target_image_to_align = np.clip(intermediate_aligned_float_scale, 0, 65535).astype(np.uint16)
            elif target_image_orig.dtype in [np.float32, np.float64]:
                finfo = np.finfo(target_image_orig.dtype)
                current_target_image_to_align = np.clip(intermediate_aligned_float_scale, finfo.min, finfo.max).astype(target_image_orig.dtype)
            else: # Tipe data lain
                current_target_image_to_align = intermediate_aligned_float_scale.astype(target_image_orig.dtype)

            print(f"  Finished scale {scale_idx+1}. Target image updated for next scale or as final result.")

            if scale_idx == len(tile_configs) - 1: # Jika ini adalah skala terakhir
                final_aligned_image = current_target_image_to_align.copy() # Hasil akhir

        # Jika loop tile_configs tidak pernah berjalan (misal tile_configs kosong dan fallback juga gagal)
        if final_aligned_image is None:
            print("Warning: Multi-scale processing did not complete. Returning original target image.")
            return target_image_orig.copy(), {}


        return final_aligned_image, all_final_local_matrices
    
def main(db_path, update_progress=None, batch_size=8, stop_requested=None, single_process=None, batch_id=None,
         config_filename=None, save_align_flag_arg=None, align_folder_path_arg=None, command_save_to_hd5f_flag_arg=None):

    processor = AKAZEAlgorithm(db_path=db_path) # Berikan db_path ke konstruktor jika diperlukan

    if single_process or batch_id is None:
        current_config = processor.load_akaze_config(config_filename)
    else:
        current_config = processor.load_akaze_config_for_batch(config_filename)

    save_align = save_align_flag_arg if save_align_flag_arg is not None else current_config.get("save_align", False)
    command_save_to_hd5f = command_save_to_hd5f_flag_arg if command_save_to_hd5f_flag_arg is not None else current_config.get("command_save_to_hd5f", True)
    align_folder_default = os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image_local_multiscale")
    align_folder = align_folder_path_arg if align_folder_path_arg is not None else current_config.get("align_folder", align_folder_default)

    image_paths = []
    if single_process:
        image_paths = get_all_image_paths_for_single_process(db_path)
        processor.hdf5_path = current_config.get("hdf5_path_single_local", "database/align/aligned_images.h5")
    else:
        if batch_id is None:
            raise ValueError(language_config.BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS)
        image_paths = processor.get_all_image_paths_for_batch_process(batch_id)
        processor.hdf5_path = current_config.get("hdf5_path_batch_local_template", "database/align/aligned_image_batch_{batch_id}.h5").format(batch_id=batch_id)

    if not image_paths or len(image_paths) < 2 : # Perlu minimal 2 gambar (base + target)
        errmsg = language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED
        if len(image_paths) < 2: errmsg = "Not enough images for alignment (minimum 2 required)."
        print(errmsg)
        if update_progress: update_progress(0, 1, errmsg)
        return

    hdf5_parent_folder = os.path.dirname(processor.hdf5_path)
    if hdf5_parent_folder and not os.path.exists(hdf5_parent_folder):
        os.makedirs(hdf5_parent_folder)
    # (Logika warning HDF5 path Anda sudah baik)

    metadata_folder_name = f"metadata_local_multiscale{'_batch_' + str(batch_id) if not single_process and batch_id else ''}"
    metadata_folder = os.path.join("database", "align", metadata_folder_name)
    os.makedirs(metadata_folder, exist_ok=True)
    metadata_file_local = os.path.join(metadata_folder, "metadata.json")
    extract_all_metadata(image_paths, metadata_file=metadata_file_local) # Ini mungkin perlu path yang benar jika dummy

    base_image_path = image_paths[0]
    print(f"Loading base image: {base_image_path}")
    loaded_base_list = load_images_from_paths([base_image_path], stop_requested=stop_requested)
    if not loaded_base_list or loaded_base_list[0] is None:
        print(f"{language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED} for base image.")
        if update_progress: update_progress(0, 1, language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
        return
    base_image_orig = loaded_base_list[0] # Ganti nama ke base_image_orig agar jelas

    num_target_images = len(image_paths) - 1
    total_steps = num_target_images if num_target_images > 0 else 1 # Hindari total_steps 0
    current_step = 0

    print(f"Will save results to HDF5: {processor.hdf5_path}")

    try:
        with h5py.File(processor.hdf5_path, "w") as h5f:
            if command_save_to_hd5f:
                base_metadata = extract_exif(base_image_path)
                save_to_hdf5(h5f, "image_0", base_image_orig, base_metadata) # Simpan base_image_orig
            if save_align:
                save_align_to_folder(base_image_orig, 0, base_image_path, align_folder) # Simpan base_image_orig

            if num_target_images <= 0:
                print("No target images to align.")
                if update_progress: update_progress(total_steps, total_steps, "Completed, no targets.")
                return

            total_batches_load = (num_target_images + batch_size - 1) // batch_size
            processed_image_idx_global_offset = 0 # Untuk dataset_name yang benar

            for batch_load_idx in range(total_batches_load):
                if stop_requested and stop_requested(): print("Process stopped by user."); break

                start_slice_idx = 1 + batch_load_idx * batch_size # Indeks di image_paths
                end_slice_idx = min(len(image_paths), start_slice_idx + batch_size)
                batch_target_paths = image_paths[start_slice_idx:end_slice_idx]

                if not batch_target_paths: continue
                print(f"\nLoading batch {batch_load_idx+1}/{total_batches_load} of target images ({len(batch_target_paths)} images)...")
                batch_target_images = load_images_from_paths(batch_target_paths, stop_requested=stop_requested)

                if stop_requested and stop_requested(): break
                if not batch_target_images or all(img is None for img in batch_target_images) :
                    print(f"Failed to load any images in batch {batch_load_idx+1}.")
                    current_step += len(batch_target_paths) # Majukan step sejumlah gambar yang gagal dimuat
                    processed_image_idx_global_offset += len(batch_target_paths)
                    if update_progress: update_progress(current_step, total_steps, f"Failed to load batch {batch_load_idx+1}")
                    continue


                for img_idx_in_batch, target_image_orig in enumerate(batch_target_images):
                    if stop_requested and stop_requested(): break

                    # Indeks global dataset dimulai dari 1 untuk target pertama
                    dataset_image_index = processed_image_idx_global_offset + img_idx_in_batch + 1
                    current_original_path = batch_target_paths[img_idx_in_batch]

                    if target_image_orig is None:
                        print(f"Skipping None image: {current_original_path} (index {dataset_image_index})")
                        current_step +=1
                        if update_progress: update_progress(current_step, total_steps, f"Skipped None image {dataset_image_index}")
                        continue


                    info_message = language_config.RUN_IMAGE_PROCESSING.format(i=dataset_image_index, total_images=num_target_images)
                    print(info_message)
                    if update_progress: update_progress(current_step, total_steps, info_message)

                    compensated_image = None # Inisialisasi
                    try:
                        # --- PANGGIL FUNGSI MULTI-SKALA ---
                        compensated_image, _ = processor.align_local_multiscale(base_image_orig, target_image_orig, current_config)

                        if compensated_image is None:
                            fail_msg = f"Failed local multi-scale alignment for image {current_original_path} (index {dataset_image_index})."
                            print(fail_msg)
                            # Sebagai fallback, mungkin simpan gambar target asli? Atau biarkan None.
                            # compensated_image = target_image_orig.copy() # Jika ingin menyimpan original jika gagal
                        else:
                            print(f"Successfully aligned image {current_original_path} (index {dataset_image_index})")
                            if save_align:
                                save_align_to_folder(compensated_image, dataset_image_index, current_original_path, align_folder)
                            if command_save_to_hd5f:
                                target_metadata = extract_exif(current_original_path)
                                dataset_name = f"image_{dataset_image_index}"
                                save_to_hdf5(h5f, dataset_name, compensated_image, target_metadata)

                        progress_msg = f"Image {dataset_image_index}/{num_target_images} processed."
                        if update_progress: update_progress(current_step + 1, total_steps, progress_msg)

                    except Exception as e:
                        error_msg = f"Error processing image {current_original_path} (index {dataset_image_index}): {e}"
                        print(error_msg)
                        # traceback.print_exc() # Untuk debug lebih detail
                        if update_progress: update_progress(current_step + 1, total_steps, f"Error on image {dataset_image_index}")
                    finally:
                        current_step += 1
                        del target_image_orig # Hapus referensi ke gambar target batch saat ini
                        if compensated_image is not None: del compensated_image
                        gc.collect()
                
                processed_image_idx_global_offset += len(batch_target_paths)
                del batch_target_images # Hapus referensi ke daftar gambar batch
                gc.collect()

    except Exception as e:
        print(f"Main error occurred (HDF5 or other): {e}")
        # traceback.print_exc() # Untuk debug lebih detail
        if update_progress: update_progress(current_step, total_steps, f"Main error: {e}")

    if update_progress: update_progress(total_steps, total_steps, "Local multi-scale alignment process completed.")
    print("All local multi-scale alignment processes completed.")
                   
def running_tile_align(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_AKAZE)
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
    progress_bar.setStyleSheet("""
        QProgressBar {
            border: 1px solid #bbb;
            border-radius: 5px;
            background-color: #f0f0f0;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #80C4E9;
            width: 20px;
        }
    """)
    layout.addWidget(progress_bar)

    # Inisialisasi thread worker
    worker = ImageProcessingMultiThreading(main, "pixel_refine_database.db", single_process=single_process, batch_id=batch_id)

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