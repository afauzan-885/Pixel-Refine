from functools import lru_cache
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

class TILEAlgorithm:
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
    def load_tile_config(config_filename=None):
        """
        Membaca konfigurasi AKAZE dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "tile_size_w": 48,
            "tile_size_h": 48,
            "overlap_percent": 0.30, 
            "num_pyramid_levels_coarse_to_fine": 3, 
            "use_multi_core": True,
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
    def load_tile_config_for_batch(config_filename=None):
        """
        Membaca konfigurasi AKAZE dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "tile_size_w": 128,
            "tile_size_h": 128,
            "overlap_percent": 0.30,
            "num_pyramid_levels_coarse_to_fine": 4, 
            "use_multi_core": True,
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
        
    def prepare_gray_image(self, img):
        if img is None: raise ValueError("Input image is None.")
        if not img.flags['C_CONTIGUOUS']:
            img = np.ascontiguousarray(img)

        if img.ndim == 3:
            if img.shape[2] == 3: gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            elif img.shape[2] == 4: gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            else: raise ValueError(f"Unsupported number of channels for 3D image: {img.shape[2]}")
        elif img.ndim == 2: gray = img.copy() 
        else:
            raise ValueError(f"Invalid image dimensions: {img.shape}")

        if gray.dtype != np.uint8:
            if gray.dtype in [np.float32, np.float64]:
                max_val = np.max(gray)
                if max_val <= 1.0 and np.min(gray) >=0.0 : 
                     gray_norm = (gray * 255.0).astype(np.uint8)
                elif max_val <=255.0 and np.min(gray) >=0.0: 
                     gray_norm = gray.astype(np.uint8)
                else: 
                    gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            elif gray.dtype == np.uint16:
                gray_norm = (gray / 256.0).astype(np.uint8) 
            else: 
                gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            return gray_norm
        return gray
    
    @lru_cache(maxsize=128)
    def _create_hanning_window_2d(self, h, w):
        if h <= 0 or w <= 0: 
            return np.ones((max(1,h), max(1,w)), dtype=np.float32) 
        hann_h = np.hanning(h) if h > 1 else np.array([1.0])
        hann_w = np.hanning(w) if w > 1 else np.array([1.0])
        hann_2d = np.outer(hann_h, hann_w)
        return hann_2d
    
    def _build_gaussian_pyramid(self, image_gray, num_levels=4):
        pyramid = [image_gray]
        for _ in range(1, num_levels):
            image_gray = cv2.pyrDown(image_gray)
            pyramid.append(image_gray)
        return pyramid[::-1]
    
    def _compute_tile_displacements_multiscale(self, base_gray_full_res, target_gray_full_res, config, num_levels=4):
        base_gray_uint8 = self.prepare_gray_image(base_gray_full_res)
        target_gray_uint8 = self.prepare_gray_image(target_gray_full_res)

        base_pyr = self._build_gaussian_pyramid(base_gray_uint8, num_levels)
        target_pyr = self._build_gaussian_pyramid(target_gray_uint8, num_levels)

        if not base_pyr or not target_pyr or len(base_pyr) != len(target_pyr):
            print("Warning: Could not build consistent pyramids. Skipping multiscale displacement computation.")
            return {}, {}

        actual_num_levels = len(base_pyr)
        tile_w_orig = config["tile_size_w"]
        tile_h_orig = config["tile_size_h"]
        overlap_percent = config["overlap_percent"]
        use_multi_core = config.get("use_multi_core", True)

        current_level_displacement_field = {}
        final_response_map = {}

        for level_idx in range(actual_num_levels):
            base_level_img = base_pyr[level_idx]
            target_level_img = target_pyr[level_idx]

            scale_to_original = (2**(actual_num_levels - 1 - level_idx))
            current_tile_w = max(16, int(round(tile_w_orig / scale_to_original)))
            current_tile_h = max(16, int(round(tile_h_orig / scale_to_original)))
            current_overlap_px_w = min(int(round(current_tile_w * overlap_percent)), current_tile_w - 1)
            current_overlap_px_h = min(int(round(current_tile_h * overlap_percent)), current_tile_h - 1)

            img_h_level, img_w_level = base_level_img.shape[:2]

            if img_h_level < current_tile_h // 2 or img_w_level < current_tile_w // 2:
                # propagate from previous level
                propagated_field = {}
                if level_idx > 0:
                    for key, (prev_dx, prev_dy) in current_level_displacement_field.items():
                        propagated_field[key] = (prev_dx * 2.0, prev_dy * 2.0)
                current_level_displacement_field = propagated_field
                continue

            step_w_level = max(1, current_tile_w - current_overlap_px_w)
            step_h_level = max(1, current_tile_h - current_overlap_px_h)
            num_tiles_x_level = max(1, math.ceil(img_w_level / step_w_level))
            num_tiles_y_level = max(1, math.ceil(img_h_level / step_h_level))

            tile_params_for_level = []
            for i in range(num_tiles_x_level):
                for j in range(num_tiles_y_level):
                    tile_key = (i, j)
                    init_dx_level, init_dy_level = 0.0, 0.0
                    if level_idx > 0:
                        prev_dx, prev_dy = current_level_displacement_field.get(tile_key, (0.0, 0.0))
                        init_dx_level, init_dy_level = prev_dx * 2.0, prev_dy * 2.0

                    tile_params_for_level.append((
                        i, j,
                        base_level_img, target_level_img, None,
                        current_tile_w, current_tile_h,
                        current_overlap_px_w, current_overlap_px_h,
                        img_h_level, img_w_level,
                        None,
                        config,
                        init_dx_level, init_dy_level,
                        True  # is_for_displacement_estimation_only
                    ))

            level_results_matrices = {}
            response_map_level = {}

            if use_multi_core and len(tile_params_for_level) > 1:
                with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                    future_to_tile_key = {
                        executor.submit(self._process_single_tile, *params): (params[0], params[1])
                        for params in tile_params_for_level
                    }
                    for future in concurrent.futures.as_completed(future_to_tile_key):
                        tile_key_processed = future_to_tile_key[future]
                        try:
                            _, _, M_level, response_val = future.result()  # ⬅️ Perbaikan: 4 nilai
                            level_results_matrices[tile_key_processed] = M_level
                            response_map_level[tile_key_processed] = response_val
                        except Exception as exc:
                            print(f"  Tile {tile_key_processed} (level {level_idx}) estimation error: {exc}")
                            level_results_matrices[tile_key_processed] = None
                            response_map_level[tile_key_processed] = 0.0
            else:
                for params in tile_params_for_level:
                    tile_key_processed = (params[0], params[1])
                    try:
                        _, _, M_level, response_val = self._process_single_tile(*params)  # ⬅️ Perbaikan: 4 nilai
                        level_results_matrices[tile_key_processed] = M_level
                        response_map_level[tile_key_processed] = response_val
                    except Exception as exc:
                        print(f"  Tile {tile_key_processed} (level {level_idx}) estimation error: {exc}")
                        level_results_matrices[tile_key_processed] = None
                        response_map_level[tile_key_processed] = 0.0

            next_level_displacement_field_temp = {}
            for i in range(num_tiles_x_level):
                for j in range(num_tiles_y_level):
                    tile_key = (i, j)
                    M_level = level_results_matrices.get(tile_key)
                    init_dx_fallback, init_dy_fallback = 0.0, 0.0
                    if level_idx > 0:
                        prev_dx, prev_dy = current_level_displacement_field.get(tile_key, (0.0, 0.0))
                        init_dx_fallback, init_dy_fallback = prev_dx * 2.0, prev_dy * 2.0

                    current_dx_total, current_dy_total = init_dx_fallback, init_dy_fallback
                    if M_level is not None:
                        current_dx_total = -M_level[0, 2]
                        current_dy_total = -M_level[1, 2]

                    next_level_displacement_field_temp[tile_key] = (current_dx_total, current_dy_total)

            current_level_displacement_field = next_level_displacement_field_temp

            # Simpan response map dari level terhalus (paling akhir)
            if level_idx == actual_num_levels - 1:
                final_response_map = response_map_level

        return current_level_displacement_field, final_response_map


    def refine_bad_tiles_from_neighbors(self, displacement_field, response_map, response_thresh=0.03):
        refined_field = displacement_field.copy()

        for (i, j), resp in response_map.items():
            if resp >= response_thresh:
                continue

            neighbor_shifts = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (i + dx, j + dy)
                if neighbor in displacement_field and response_map.get(neighbor, 0.0) >= response_thresh:
                    neighbor_shifts.append(displacement_field[neighbor])

            if neighbor_shifts:
                mean_dx = sum(d[0] for d in neighbor_shifts) / len(neighbor_shifts)
                mean_dy = sum(d[1] for d in neighbor_shifts) / len(neighbor_shifts)
                refined_field[(i, j)] = (mean_dx, mean_dy)

        return refined_field


    def _process_single_tile(self, tile_idx_i, tile_idx_j,
                         base_gray_enhanced, target_gray_enhanced, target_image_to_warp,
                         tile_w, tile_h,
                         overlap_px_w, overlap_px_h,
                         img_h, img_w,
                         akaze_detector,
                         local_align_config,
                         init_dx=0.0, init_dy=0.0,
                         is_for_displacement_estimation_only=False):

        x_coord_grid = tile_idx_i * (tile_w - overlap_px_w)
        y_coord_grid = tile_idx_j * (tile_h - overlap_px_h)
        current_tile_global_x_start = max(0, int(x_coord_grid))
        current_tile_global_y_start = max(0, int(y_coord_grid))
        current_tile_global_x_end = min(img_w, current_tile_global_x_start + tile_w)
        current_tile_global_y_end = min(img_h, current_tile_global_y_start + tile_h)

        current_tile_processing_w = current_tile_global_x_end - current_tile_global_x_start
        current_tile_processing_h = current_tile_global_y_end - current_tile_global_y_start

        if current_tile_processing_w <= 0 or current_tile_processing_h <= 0:
            return None, None, None, 0.0

        tile_target_content_to_warp_current = None
        if not is_for_displacement_estimation_only and target_image_to_warp is not None:
            tile_target_content_to_warp_current = target_image_to_warp[
                current_tile_global_y_start:current_tile_global_y_end,
                current_tile_global_x_start:current_tile_global_x_end
            ]
            if tile_target_content_to_warp_current.size == 0:
                return None, None, None, 0.0
        elif is_for_displacement_estimation_only and target_image_to_warp is None:
            if current_tile_processing_w < 16 or current_tile_processing_h < 16:
                M_init_guess = np.float32([[1, 0, -init_dx], [0, 1, -init_dy]])
                return None, (current_tile_global_y_start, current_tile_global_x_start), M_init_guess, 0.0

        if not is_for_displacement_estimation_only and \
        (current_tile_processing_w <= max(1, overlap_px_w // 2) or
            current_tile_processing_h <= max(1, overlap_px_h // 2) or
            current_tile_processing_w < 16 or current_tile_processing_h < 16):
            if tile_target_content_to_warp_current is None or tile_target_content_to_warp_current.size == 0:
                return None, None, None, 0.0

            hanning_win_skip = self._create_hanning_window_2d(tile_target_content_to_warp_current.shape[0], tile_target_content_to_warp_current.shape[1])
            if tile_target_content_to_warp_current.ndim == 3:
                hanning_win_skip = np.stack([hanning_win_skip]*tile_target_content_to_warp_current.shape[2], axis=-1)
            windowed_tile_skip = (tile_target_content_to_warp_current.astype(np.float32) * hanning_win_skip)

            M_final = np.float32([[1, 0, -init_dx], [0, 1, -init_dy]]) if (init_dx != 0 or init_dy != 0) else np.float32([[1, 0, 0], [0, 1, 0]])
            try:
                if init_dx != 0 or init_dy != 0:
                    output_size = (tile_target_content_to_warp_current.shape[1], tile_target_content_to_warp_current.shape[0])
                    warped = cv2.warpPerspective(np.ascontiguousarray(tile_target_content_to_warp_current), M_final,
                                            output_size, flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT_101)
                    windowed_tile_skip = (warped.astype(np.float32) * hanning_win_skip)
            except:
                pass

            return windowed_tile_skip, (current_tile_global_y_start, current_tile_global_x_start), M_final, 0.0

        tile_base = base_gray_enhanced[
            current_tile_global_y_start:current_tile_global_y_end,
            current_tile_global_x_start:current_tile_global_x_end
        ].astype(np.float32)

        tile_target_original = target_gray_enhanced[
            current_tile_global_y_start:current_tile_global_y_end,
            current_tile_global_x_start:current_tile_global_x_end
        ].astype(np.float32)

        if tile_base.size == 0 or tile_target_original.size == 0 or tile_base.shape != tile_target_original.shape:
            M_fallback = np.float32([[1, 0, -init_dx], [0, 1, -init_dy]])
            if not is_for_displacement_estimation_only:
                if tile_target_content_to_warp_current is not None and tile_target_content_to_warp_current.size > 0:
                    hanning_win = self._create_hanning_window_2d(tile_target_content_to_warp_current.shape[0], tile_target_content_to_warp_current.shape[1])
                    if tile_target_content_to_warp_current.ndim == 3:
                        hanning_win = np.stack([hanning_win]*tile_target_content_to_warp_current.shape[2], axis=-1)
                    windowed = (tile_target_content_to_warp_current.astype(np.float32) * hanning_win)
                    return windowed, (current_tile_global_y_start, current_tile_global_x_start), M_fallback, 0.0
            else:
                return None, (current_tile_global_y_start, current_tile_global_x_start), M_fallback, 0.0

            return None, None, None, 0.0

        # Pre-warp untuk phase correlation
        tile_target = tile_target_original
        if init_dx != 0.0 or init_dy != 0.0:
            try:
                M_guess = np.float32([[1, 0, -init_dx], [0, 1, -init_dy]])
                tile_target = cv2.warpAffine(tile_target_original, M_guess, (tile_target_original.shape[1], tile_target_original.shape[0]),
                                            flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
            except:
                tile_target = tile_target_original

        refined_dx, refined_dy = 0.0, 0.0
        response = 0.0
        try:
            if tile_base.shape[0] >= 8 and tile_base.shape[1] >= 8:
                shift, response = cv2.phaseCorrelate(np.ascontiguousarray(tile_base), np.ascontiguousarray(tile_target))
                if shift is not None and shift[0] is not None and shift[1] is not None:
                    refined_dx, refined_dy = shift[0], shift[1]
        except:
            response = 0.0

        total_dx = init_dx + refined_dx
        total_dy = init_dy + refined_dy
        M_total = np.float32([[1, 0, -total_dx], [0, 1, -total_dy]])

        if is_for_displacement_estimation_only:
            return None, (current_tile_global_y_start, current_tile_global_x_start), M_total, response

        warped_tile = tile_target_content_to_warp_current.copy()
        try:
            if tile_target_content_to_warp_current is not None:
                warped_tile = cv2.warpAffine(np.ascontiguousarray(tile_target_content_to_warp_current), M_total,
                                            (tile_base.shape[1], tile_base.shape[0]),
                                            flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT_101)
        except:
            warped_tile = tile_target_content_to_warp_current.copy()

        if warped_tile is None or warped_tile.size == 0:
            return None, None, None, 0.0

        hanning_win = self._create_hanning_window_2d(warped_tile.shape[0], warped_tile.shape[1])
        if warped_tile.ndim == 3:
            hanning_win = np.stack([hanning_win] * warped_tile.shape[2], axis=-1)

        windowed_tile = warped_tile.astype(np.float32) * hanning_win
        return windowed_tile, (current_tile_global_y_start, current_tile_global_x_start), M_total, response

    def align_local(self, base_image_orig, target_image_orig, config_to_use):
        if base_image_orig is None or target_image_orig is None:
            return None, None

        tile_w = config_to_use.get("tile_size_w")
        tile_h = config_to_use.get("tile_size_h")
        overlap_percent = config_to_use.get("overlap_percent")
        num_pyr_levels = config_to_use.get("num_pyramid_levels_coarse_to_fine", 4)

        if tile_w is None or tile_h is None or overlap_percent is None:
            return target_image_orig.copy(), {}

        use_multicore_tiles = bool(config_to_use.get("use_multi_core", True))
        dummy_akaze_detector = None

        current_target_image_to_align = target_image_orig.copy()
        all_final_local_matrices = {}
        img_h_orig, img_w_orig = base_image_orig.shape[:2]

        base_gray_prepared = self.prepare_gray_image(base_image_orig)
        try:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            base_gray_enhanced_const = clahe.apply(base_gray_prepared)
        except Exception as e:
            print(f"Error applying CLAHE to base image: {e}. Using original gray.")
            base_gray_enhanced_const = base_gray_prepared

        target_gray_prepared = self.prepare_gray_image(current_target_image_to_align)
        try:
            target_gray_enhanced = clahe.apply(target_gray_prepared)
        except Exception as e:
            print(f"Error applying CLAHE to target image: {e}. Using original gray.")
            target_gray_enhanced = target_gray_prepared

        # --- Coarse-to-fine displacement estimation ---
        print(f"  Starting coarse-to-fine displacement estimation with {num_pyr_levels} levels...")
        displacement_field, response_map = self._compute_tile_displacements_multiscale(
            base_gray_enhanced_const, target_gray_enhanced, config_to_use, num_levels=num_pyr_levels)
        print("  Refining low-confidence tiles using neighboring displacements...")
        displacement_field = self.refine_bad_tiles_from_neighbors(displacement_field, response_map)

        if not (0 <= overlap_percent < 1.0):
            overlap_percent = np.clip(overlap_percent, 0.01, 0.9)

        overlap_px_w = int(tile_w * overlap_percent)
        overlap_px_h = int(tile_h * overlap_percent)
        overlap_px_w = min(overlap_px_w, tile_w - 1)
        overlap_px_h = min(overlap_px_h, tile_h - 1)

        num_channels = current_target_image_to_align.shape[2] if current_target_image_to_align.ndim == 3 else 1
        aligned_image_float = np.zeros((img_h_orig, img_w_orig, num_channels), dtype=np.float32) \
                            if num_channels > 1 else np.zeros((img_h_orig, img_w_orig), dtype=np.float32)
        weight_map = np.zeros((img_h_orig, img_w_orig), dtype=np.float32)

        step_w = tile_w - overlap_px_w
        step_h = tile_h - overlap_px_h
        num_tiles_x = max(1, math.ceil(img_w_orig / step_w))
        num_tiles_y = max(1, math.ceil(img_h_orig / step_h))

        tile_params = []
        for i in range(num_tiles_x):
            for j in range(num_tiles_y):
                init_dx, init_dy = displacement_field.get((i, j), (0.0, 0.0))
                tile_params.append((
                    i, j,
                    base_gray_enhanced_const,
                    target_gray_enhanced,
                    current_target_image_to_align,
                    tile_w, tile_h,
                    overlap_px_w, overlap_px_h,
                    img_h_orig, img_w_orig,
                    dummy_akaze_detector,
                    config_to_use,
                    init_dx, init_dy,
                    False  # is_for_displacement_estimation_only
                ))

        results = []
        if use_multicore_tiles and len(tile_params) > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                futures = {
                    executor.submit(self._process_single_tile, *params): (params[0], params[1])
                    for params in tile_params
                }
                for future in concurrent.futures.as_completed(futures):
                    try:
                        win_tile, coord, M_loc, _ = future.result()
                        if win_tile is not None:
                            results.append((win_tile, coord, M_loc))
                    except Exception as exc:
                        i, j = futures[future]
                        print(f"  Tile ({i},{j}) processing exception: {exc}")
        else:
            for params in tile_params:
                try:
                    win_tile, coord, M_loc, _ = self._process_single_tile(*params)
                    if win_tile is not None:
                        results.append((win_tile, coord, M_loc))
                except Exception as exc:
                    print(f"  Tile ({params[0]},{params[1]}) processing exception: {exc}")

        if not results:
            return current_target_image_to_align.copy(), {}

        for win_tile, (y0, x0), M_loc in results:
            h, w = win_tile.shape[:2]
            y1, x1 = min(y0 + h, img_h_orig), min(x0 + w, img_w_orig)
            actual_h, actual_w = y1 - y0, x1 - x0
            if actual_h <= 0 or actual_w <= 0:
                continue

            win_crop = win_tile[:actual_h, :actual_w]
            target_crop = aligned_image_float[y0:y1, x0:x1]

            if num_channels > 1:
                if win_crop.shape == target_crop.shape:
                    target_crop += win_crop
            else:
                if win_crop.ndim == 3:
                    win_crop = np.squeeze(win_crop, axis=2)
                if target_crop.ndim == 3:
                    target_crop = np.squeeze(target_crop, axis=2)
                if win_crop.shape == target_crop.shape:
                    target_crop += win_crop

            hanning_win = self._create_hanning_window_2d(actual_h, actual_w)
            weight_map[y0:y1, x0:x1] += hanning_win

            if M_loc is not None:
                gx = int(round(x0 / step_w)) if step_w > 0 else 0
                gy = int(round(y0 / step_h)) if step_h > 0 else 0
                all_final_local_matrices[(gx, gy)] = M_loc

        if num_channels > 1:
            weight_map_3d = np.stack([weight_map] * num_channels, axis=-1)
            denom = np.where(weight_map_3d < 1e-6, 1.0, weight_map_3d)
        else:
            denom = np.where(weight_map < 1e-6, 1.0, weight_map)

        aligned_image_float /= denom

        if target_image_orig.dtype == np.uint8:
            final_aligned_image = np.clip(aligned_image_float, 0, 255).astype(np.uint8)
        elif target_image_orig.dtype == np.uint16:
            final_aligned_image = np.clip(aligned_image_float, 0, 65535).astype(np.uint16)
        elif target_image_orig.dtype in [np.float32, np.float64]:
            info = np.finfo(target_image_orig.dtype)
            final_aligned_image = np.clip(aligned_image_float, info.min, info.max).astype(target_image_orig.dtype)
        else:
            final_aligned_image = aligned_image_float.astype(target_image_orig.dtype)

        print(f"  Finished full-resolution alignment. Final image generated.")
        return final_aligned_image, all_final_local_matrices
    
def main(db_path, update_progress=None, batch_size=20, stop_requested=None, single_process=None, batch_id=None,
         config_filename=None, save_align_flag_arg=None, align_folder_path_arg=None, command_save_to_hd5f_flag_arg=None):

    processor = TILEAlgorithm(db_path=db_path)

    if single_process or batch_id is None:
        current_config = processor.load_tile_config(config_filename)
    else:
        current_config = processor.load_tile_config_for_batch(config_filename)

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
                        compensated_image, _ = processor.align_local(base_image_orig, target_image_orig, current_config)

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
        if update_progress: update_progress(current_step, total_steps, f"Main error: {e}")

    if update_progress: update_progress(total_steps, total_steps, "Local multi-scale alignment process completed.")
                   
def running_tile_align(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle("Tile Alignment")
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