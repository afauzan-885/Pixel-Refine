from concurrent.futures import ThreadPoolExecutor
import gc
import json
import queue
import threading
import concurrent
import traceback
import cv2
import numpy as np
import os
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PySide6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import (calculate_crop_parameters, do_warp_and_crop, estimate_noise_variance, extract_all_metadata, get_adaptive_bilateral, get_all_image_paths_for_batch_process,
                                                                                    get_all_image_paths_for_single_process, load_images_from_paths, prepare_image,
                                                                                    resize_all_with_padding, run_pipeline_global_crop, run_pipeline_non_crop)
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config
from config import ALGORITHM_PARAMETER_SETTINGS_FILE


class ORBAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        # Pastikan folder HDF5 ada
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)
        
    @staticmethod
    def load_orb_config(config_filename=None):
        """
        Membaca konfigurasi ORB dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "nfeatures": 1500, "scaleFactor": 1.1, "nlevels": 5,
            "ransacThreshold": 5.0, "transformation": "homography",
            "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image"),
            "clahe_clipLimit": 2.0, "clahe_tileGridSize": [8, 8],
            "ratio_threshold": 0.75, "min_matches_for_transform": 10,
            "keep_edges": False, "enable_cropping": False,
            "save_align": False, "command_save_to_hd5f": True,
            "use_multi_core": True
        }

        if config_filename is None:
            config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE 

        config_data = default_config.copy()
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                loaded_orb_config = params.get("ORB", {})
                # Gabungkan default dengan yang dimuat (yang dimuat menimpa default)
                config_data.update(loaded_orb_config)
            else:
                 print(f"Info: ORB config file '{config_filename}' not found. Using defaults.")

        except Exception as e:
            print(f"Error loading ORB configuration from '{config_filename}': {e}. Using defaults.")
            config_data = default_config # Kembali ke default jika error

        # Pastikan clahe_tileGridSize adalah tuple
        if isinstance(config_data.get("clahe_tileGridSize"), list):
             config_data["clahe_tileGridSize"] = tuple(config_data["clahe_tileGridSize"])
        elif not isinstance(config_data.get("clahe_tileGridSize"), tuple):
             config_data["clahe_tileGridSize"] = (8, 8) # Fallback jika tipe salah

        return config_data

    @staticmethod
    def load_orb_config_for_batch(config_filename=None):
        """
        Membaca konfigurasi ORB BATCH dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "nfeatures": 1500, "scaleFactor": 1.1, "nlevels": 5,
            "ransacThreshold": 5.0, "transformation": "homography",
            "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image"),
            "clahe_clipLimit": 2.0, "clahe_tileGridSize": [8, 8],
            "ratio_threshold": 0.75, "min_matches_for_transform": 10,
            "keep_edges": False, "enable_cropping": False,
            "save_align": False, "command_save_to_hd5f": True,
            "use_multi_core": True
        }
        if config_filename is None:
            config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE 

        config_data = default_config.copy()
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                loaded_batch_config = params.get("ORB_BATCH", {})
                config_data.update(loaded_batch_config)
            else:
                pass
        except Exception as e:
            print(f"Error loading ORB BATCH configuration from '{config_filename}': {e}. Using defaults.")
            config_data = default_config

        if isinstance(config_data.get("clahe_tileGridSize"), list):
             config_data["clahe_tileGridSize"] = tuple(config_data["clahe_tileGridSize"])
        elif not isinstance(config_data.get("clahe_tileGridSize"), tuple):
             config_data["clahe_tileGridSize"] = (8, 8)

        return config_data
    
    def compute_features_block(self, akaze_instance, enhanced_gray_base, enhanced_gray_target, x, y, bw, bh, overlap_px, img_w, img_h, max_kps_per_block=300):
        roi_x_start = max(0, x - overlap_px)
        roi_y_start = max(0, y - overlap_px)
        roi_x_end = min(img_w, x + bw + overlap_px)
        roi_y_end = min(img_h, y + bh + overlap_px)

        if roi_y_end <= roi_y_start or roi_x_end <= roi_x_start:
            return [], None, [], None

        roi_base_enhanced = enhanced_gray_base[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
        roi_target_enhanced = enhanced_gray_target[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

        kps_base, desc_base = akaze_instance.detectAndCompute(roi_base_enhanced, None)
        kps_target, desc_target = akaze_instance.detectAndCompute(roi_target_enhanced, None)

        def adjust_and_filter_kps(kps, descs):
            adjusted_kps = []
            valid_desc_indices = []
            if kps and descs is not None:
                for idx, kp in enumerate(kps):
                    orig_x = kp.pt[0] + roi_x_start
                    orig_y = kp.pt[1] + roi_y_start
                    if x <= orig_x < x + bw and y <= orig_y < y + bh:
                        if idx < len(descs):
                            kp.pt = (orig_x, orig_y)
                            adjusted_kps.append(kp)
                            valid_desc_indices.append(idx)
            if descs is not None and valid_desc_indices:
                filtered_descs = descs[np.array(valid_desc_indices)]
            else:
                filtered_descs = None
            return adjusted_kps, filtered_descs

        kps_base_adjusted, final_desc_base = adjust_and_filter_kps(kps_base, desc_base)
        kps_target_adjusted, final_desc_target = adjust_and_filter_kps(kps_target, desc_target)

        def select_top_k(kps, descs, k):
            if descs is None or len(kps) == 0:
                return [], None
            if len(kps) <= k:
                return kps, descs
            sorted_idx = np.argsort([-kp.response for kp in kps])[:k]
            return [kps[i] for i in sorted_idx], descs[sorted_idx]

        kps_base_adjusted, final_desc_base = select_top_k(kps_base_adjusted, final_desc_base, max_kps_per_block)
        kps_target_adjusted, final_desc_target = select_top_k(kps_target_adjusted, final_desc_target, max_kps_per_block)

        return kps_base_adjusted, final_desc_base, kps_target_adjusted, final_desc_target
    
    def calculate_global_motion(self, base_image, target_image, config_filename=None, num_blocks=(2, 2), overlap=10, stop_requested=None):
        if stop_requested and stop_requested():
            return None, None

        orb_config = self.load_orb_config(config_filename)
        use_multicore = orb_config.get("use_multi_core", True)
        
        # --- PERUBAHAN 1: Definisikan fungsi worker untuk filtering ---
        def filter_worker(job_q, result_q):
            """
            Thread worker yang mengambil gambar mentah, menerapkan bilateral filter,
            dan menaruh hasilnya di antrian hasil.
            """
            while True:
                item = job_q.get()
                if item is None:  # Sinyal untuk berhenti
                    result_q.put(None) # Beri sinyal selesai ke antrian hasil juga
                    break
                
                image_type, image_data = item
                
                try:
                    # 1. Persiapan awal (CLAHE dilewati untuk sementara)
                    enhanced_gray = prepare_image(image_data, grayscale=True, use_clahe=True)
                    
                    # 2. Estimasi noise
                    noise_level = estimate_noise_variance(enhanced_gray)
                    
                    # 3. Logika filter adaptif
                    min_noise_threshold = 200.0
                    max_noise_threshold = 700.0
                    min_d, max_d = 5, 9
                    min_sigma, max_sigma = 20, 75

                    if noise_level > min_noise_threshold:
                        d, sigma_color, sigma_space = get_adaptive_bilateral(
                            noise_level, min_noise_threshold, max_noise_threshold,
                            min_d, max_d, min_sigma, max_sigma
                        )
                        filtered_image = cv2.bilateralFilter(enhanced_gray, d, sigma_color, sigma_space)
                    else:
                        filtered_image = enhanced_gray
                    
                    # 4. Terapkan CLAHE setelah filtering
                    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                    final_image = clahe.apply(filtered_image)
                    
                    result_q.put((image_type, final_image))

                except Exception as e:
                    result_q.put((image_type, None)) # Kirim sinyal error

        # --- PERUBAHAN 2: Inisialisasi antrian dan thread worker ---
        job_queue = queue.Queue()
        result_queue = queue.Queue(maxsize=4) # Cukup untuk base dan target

        filter_thread = threading.Thread(target=filter_worker, args=(job_queue, result_queue))
        filter_thread.start()

        # --- PERUBAHAN 3: Isi antrian tugas (Produser) ---
        job_queue.put(("base", base_image))
        job_queue.put(("target", target_image))
        job_queue.put(None)  # Sinyal akhir pekerjaan

        # --- PERUBAHAN 4: Loop utama menjadi konsumen hasil filtering ---
        enhanced_base_gray, enhanced_target_gray = None, None
        results_received = 0
        while results_received < 2:
            item = result_queue.get() # Memblokir hingga hasil tersedia
            if item is None: # Sinyal selesai dari worker
                break
            
            image_type, image_data = item
            if image_data is None: # Terjadi error di worker
                filter_thread.join()
                return None, None

            if image_type == "base":
                enhanced_base_gray = image_data
            else: # target
                enhanced_target_gray = image_data
            
            results_received += 1
            
        # Pastikan thread worker selesai sebelum melanjutkan
        filter_thread.join()

        if enhanced_base_gray is None or enhanced_target_gray is None:
            print("Failed to get filtered images.")
            return None, None
            
        # --- DARI SINI, KODE KEMBALI SEPERTI SEMULA, TAPI MENGGUNAKAN HASIL DARI QUEUE ---
        h, w = enhanced_base_gray.shape
        blocks_x, blocks_y = num_blocks
        block_w = max(1, w // blocks_x)
        block_h = max(1, h // blocks_y)
        max_kps_per_block = 1000

        try:
            orb = cv2.ORB_create(
                nfeatures=int(orb_config.get("nfeatures", 10000)), 
                scaleFactor=float(orb_config.get("scaleFactor", 1.2)),
                nlevels=int(orb_config.get("nlevels", 8)),
                scoreType=cv2.ORB_HARRIS_SCORE
            )
        except Exception:
            return None, None

        keypoints_base_all = []
        descriptors_base_list = []
        keypoints_target_all = []
        descriptors_target_list = []

        def process_block(i, j):
            x = i * block_w
            y = j * block_h
            bw = w - x if i == blocks_x - 1 else block_w
            bh = h - y if j == blocks_y - 1 else block_h
            return self.compute_features_block(
                orb, enhanced_base_gray, enhanced_target_gray,
                x, y, bw, bh, overlap, w, h, max_kps_per_block=max_kps_per_block
            )

        try:
            if use_multicore:
                with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
                    futures = [executor.submit(process_block, i, j)
                            for i in range(blocks_x) for j in range(blocks_y)]
                    for future in concurrent.futures.as_completed(futures):
                        if stop_requested and stop_requested():
                            return None, None
                        try:
                            kpb, db, kpt, dt = future.result()
                            if db is not None and len(kpb) > 0:
                                keypoints_base_all.extend(kpb)
                                descriptors_base_list.append(db)
                            if dt is not None and len(kpt) > 0:
                                keypoints_target_all.extend(kpt)
                                descriptors_target_list.append(dt)
                        except Exception as e:
                            print(f"Error in block processing: {e}")
            else:
                for i in range(blocks_x):
                    for j in range(blocks_y):
                        if stop_requested and stop_requested():
                            return None, None
                        kpb, db, kpt, dt = process_block(i, j)
                        if db is not None and len(kpb) > 0:
                            keypoints_base_all.extend(kpb)
                            descriptors_base_list.append(db)
                        if dt is not None and len(kpt) > 0:
                            keypoints_target_all.extend(kpt)
                            descriptors_target_list.append(dt)
        except Exception as e:
            print(f"ThreadPool execution error: {e}")
            return None, None

        if not descriptors_base_list or not descriptors_target_list:
            return None, None

        try:
            # descriptor_size = orb.getDescriptorSize()
            descriptors_base_all = np.vstack(descriptors_base_list)
            descriptors_target_all = np.vstack(descriptors_target_list)

            if len(keypoints_base_all) != descriptors_base_all.shape[0] or \
            len(keypoints_target_all) != descriptors_target_all.shape[0]:
                print("CRITICAL: Mismatch between keypoints and descriptors after filtering.")
                return None, None
        except Exception as e:
            print(f"Descriptor stack error: {e}")
            return None, None

        if descriptors_base_all.shape[0] == 0 or descriptors_target_all.shape[0] == 0:
            return None, None

        def select_top_k(kps, descs, k):
            if len(kps) <= k:
                return kps, descs
            idx = np.argsort([-kp.response for kp in kps])[:k]
            return [kps[i] for i in idx], descs[idx]

        keypoints_base_all, descriptors_base_all = select_top_k(keypoints_base_all, descriptors_base_all, 500)
        keypoints_target_all, descriptors_target_all = select_top_k(keypoints_target_all, descriptors_target_all, 500)

        try:
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            matches = bf.knnMatch(descriptors_base_all, descriptors_target_all, k=2)
            ratio_thresh = orb_config.get("ratio_threshold", 0.75)
            good_matches = [m for m, n in matches if m.distance < ratio_thresh * n.distance] if all(len(mn) == 2 for mn in matches) else []

            if len(good_matches) < orb_config.get("min_matches_for_transform", 10):
                return None, None

            good_matches = sorted(good_matches, key=lambda m: m.distance)[:orb_config.get("max_keypoints_used", 500)]
            pts_base = np.float32([keypoints_base_all[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            pts_target = np.float32([keypoints_target_all[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        except Exception as e:
            print(f"Matching error: {e}")
            return None, None

        return pts_base, pts_target
    
    def _create_feathered_mask(self, i, j, grid_size, h, w, feather_pixels):
        """
        Membuat maska bobot dengan inti solid dan tepi yang lembut (feathered)
        untuk blending yang mulus di sepanjang jahitan.
        """
        grid_w, grid_h = grid_size
        
        # Tentukan batas sel
        x_start, x_end = i * w // grid_w, (i + 1) * w // grid_w
        y_start, y_end = j * h // grid_h, (j + 1) * h // grid_h
        
        # Buat maska dasar dengan nilai 1.0 di dalam sel
        mask = np.zeros((h, w), dtype=np.float32)
        mask[y_start:y_end, x_start:x_end] = 1.0
        
        # Jika feathering diminta, lakukan blur hanya pada maska ini
        if feather_pixels > 0:
            # Kernel size untuk blur harus ganjil
            ksize = feather_pixels * 2 + 1
            
            # Erosi sedikit untuk memastikan tepi benar-benar mencapai nol setelah blur
            # Ini mencegah bleeding tipis di tepi gambar
            eroded_mask = cv2.erode(mask, np.ones((3,3), np.uint8), iterations=1)

            # Terapkan Gaussian blur untuk menciptakan tepi yang lembut
            blurred_mask = cv2.GaussianBlur(eroded_mask, (ksize, ksize), 0)
            
            # Normalisasi kembali maska agar nilai maksimumnya tepat 1.0
            # Ini penting agar pusat sel tidak menjadi redup
            max_val = blurred_mask.max()
            if max_val > 0:
                blurred_mask /= max_val
            return blurred_mask
            
        return mask

    # Letakkan fungsi helper ini di dalam kelas Anda
    def _create_bilinear_weight_mask(self, i, j, grid_size, h, w):
        grid_w, grid_h = grid_size
        x_ramp = np.linspace(0, 1, w)
        y_ramp = np.linspace(0, 1, h)
        x_weight = 1 - np.abs(x_ramp - (i + 0.5) / grid_w) * grid_w
        x_weight = np.clip(x_weight, 0, 1)
        y_weight = 1 - np.abs(y_ramp - (j + 0.5) / grid_h) * grid_h
        y_weight = np.clip(y_weight, 0, 1)
        weight_mask_y, weight_mask_x = np.meshgrid(y_weight, x_weight, indexing='ij')
        return weight_mask_x * weight_mask_y

    # =================================================================
    # === FUNGSI HELPER BARU UNTUK MEMERIKSA KEWARASAN HOMOGRAFI ===
    # =================================================================
    def _is_homography_sane(self, H_local, H_global, max_translation_diff=50, max_scale_diff=0.2, max_perspective_val=0.001):
        """
        Memeriksa apakah H_local tidak terlalu menyimpang dari H_global.
        Ini mencegah "denyutan" atau "jitter" akibat homografi lokal yang tidak stabil.
        """
        # 1. Periksa perbedaan translasi (pergeseran)
        if np.abs(H_local[0, 2] - H_global[0, 2]) > max_translation_diff: return False
        if np.abs(H_local[1, 2] - H_global[1, 2]) > max_translation_diff: return False

        # 2. Periksa perbedaan skala (zoom)
        if np.abs(H_local[0, 0] - H_global[0, 0]) > max_scale_diff: return False
        if np.abs(H_local[1, 1] - H_global[1, 1]) > max_scale_diff: return False
        
        # 3. Periksa nilai perspektif yang ekstrem
        if np.abs(H_local[2, 0]) > max_perspective_val: return False
        if np.abs(H_local[2, 1]) > max_perspective_val: return False
        
        return True
    
    def _calculate_warping_residuals(self, base_points, target_points, homographies):
        """Menghitung warping residual vector untuk setiap pasangan titik."""
        num_points = len(base_points)
        if num_points == 0 or not homographies:
            return np.array([])
            
        num_homographies = len(homographies)
        residual_matrix = np.zeros((num_points, num_homographies))
        base_points_hom = np.hstack([base_points, np.ones((num_points, 1))])

        for h_idx, H in enumerate(homographies):
            warped_points_hom = (H @ base_points_hom.T).T
            w_prime = warped_points_hom[:, 2, np.newaxis]
            w_prime[w_prime == 0] = 1e-6
            warped_points_2d = warped_points_hom[:, :2] / w_prime
            
            errors = np.linalg.norm(warped_points_2d - target_points, axis=1)
            residual_matrix[:, h_idx] = errors
        return residual_matrix

    def _estimate_multiple_homographies(self, base_points, target_points, min_points, 
                                        ransac_threshold, max_homographies=5):
        """
        Menemukan beberapa homografi berbeda menggunakan strategi "Dominant Plane + Residual Analysis".
        [NEW] Jauh lebih sensitif terhadap parallax.
        """
        homographies = []
        
        # --- Langkah 1: Temukan bidang paling dominan dengan presisi tinggi ---
        print("  > Mencari bidang gerak dominan...")
        H_dominant, mask = cv2.findHomography(target_points, base_points, cv2.USAC_MAGSAC, ransac_threshold)
        
        if H_dominant is None:
            print("  > Gagal menemukan homografi dominan.")
            return []
            
        num_inliers = np.sum(mask)
        print(f"  > Bidang dominan ditemukan dengan {num_inliers} inlier.")
        homographies.append(H_dominant)
        
        # Sisa titik untuk diproses adalah outlier dari model dominan
        remaining_indices = np.where(mask.ravel() == 0)[0]

        # --- Langkah 2 & 3: Secara iteratif temukan bidang parallax dari sisa titik ---
        for i in range(1, max_homographies):
            if len(remaining_indices) < min_points:
                print(f"  > Menghentikan pencarian: hanya tersisa {len(remaining_indices)} titik.")
                break
                
            current_base_pts = base_points[remaining_indices]
            current_target_pts = target_points[remaining_indices]
            
            # Gunakan metode yang lebih toleran (LMEDS) untuk menemukan model dari sisa titik yang "berisik"
            print(f"  > Mencari bidang sekunder ke-{i} dari {len(current_base_pts)} sisa titik...")
            try:
                # Kita bisa sedikit melonggarkan threshold di sini
                H_secondary, mask_secondary = cv2.findHomography(current_target_pts, current_base_pts, cv2.LMEDS, ransac_threshold * 2)
                
                if H_secondary is None or mask_secondary is None:
                    print("  > Tidak ada model sekunder yang valid ditemukan.")
                    break # Tidak ada lagi model yang bisa ditemukan

                num_inliers_secondary = np.sum(mask_secondary)
                if num_inliers_secondary < min_points:
                    print(f"  > Model sekunder ditolak: hanya {num_inliers_secondary} inlier.")
                    break

                print(f"  > Bidang sekunder ditemukan dengan {num_inliers_secondary} inlier.")
                homographies.append(H_secondary)
                
                # Perbarui sisa titik untuk iterasi berikutnya
                outlier_indices_secondary = np.where(mask_secondary.ravel() == 0)[0]
                remaining_indices = remaining_indices[outlier_indices_secondary]
                
            except Exception as e:
                print(f"  > Error saat mencari model sekunder: {e}")
                break

        return homographies

    def _process_grid_cell(self, i, j, h, w, actual_grid_w, actual_grid_h, min_points_per_cell, ransac_threshold, feather_pixels, base_image_float, base_points_flat, target_points_flat, H_global):
        """
        Memproses satu sel grid: hitung H_local, warp, dan kembalikan hasil warp
        dan maska bobot untuk sel ini.
        """
        # Batas asli sel
        x_start, x_end = i * w // actual_grid_w, (i + 1) * w // actual_grid_w
        y_start, y_end = j * h // actual_grid_h, (j + 1) * h // actual_grid_h
        cell_w, cell_h = x_end - x_start, y_end - y_start
        overlap_x, overlap_y = int(cell_w * 0.05), int(cell_h * 0.05)
        exp_x_start, exp_x_end = max(0, x_start - overlap_x), min(w, x_end + overlap_x)
        exp_y_start, exp_y_end = max(0, y_start - overlap_y), min(h, y_end + overlap_y)
        
        indices = np.where(
            (base_points_flat[:, 0] >= exp_x_start) & (base_points_flat[:, 0] < exp_x_end) &
            (base_points_flat[:, 1] >= exp_y_start) & (base_points_flat[:, 1] < exp_y_end)
        )[0]
        
        H_to_use = H_global
        if len(indices) >= min_points_per_cell:
            try:
                H_local, _ = cv2.findHomography(target_points_flat[indices], base_points_flat[indices], cv2.USAC_MAGSAC, ransac_threshold)
                
                if H_local is not None and self._is_homography_sane(H_local, H_global):
                    H_to_use = H_local
            except Exception:
                pass
        
        # Lakukan warping pada seluruh gambar
        warped_for_cell = cv2.warpPerspective(base_image_float, H_to_use, (w, h),
                                            flags=cv2.INTER_CUBIC,
                                            borderMode=cv2.BORDER_CONSTANT)
        
        # Buat maska bobot untuk sel ini
        actual_grid_size = (actual_grid_w, actual_grid_h)
        weight_mask = self._create_feathered_mask(i, j, actual_grid_size, h, w, feather_pixels)

        return warped_for_cell, weight_mask

    # =================================================================
    # === FUNGSI UTAMA DENGAN PARALELISASI GRID ===
    # =================================================================
    def compensate_motion(self, base_image, base_points, target_points, config_filename=None, grid_size=(3, 3), feather_pixels=20):
        actual_grid_w = grid_size[0] + 1
        actual_grid_h = grid_size[1] + 1

        print(f"\n[Warp-Refine] Memulai kompensasi dengan grid {actual_grid_w}x{actual_grid_h}, feathering {feather_pixels}px...")
        if base_points is None or target_points is None or base_image is None: return None
        
        # --- LANGKAH 0 & 1: Persiapan dan H_global ---
        original_dtype = base_image.dtype
        try: max_val = np.iinfo(original_dtype).max
        except ValueError: max_val = 1.0
        config = self.load_orb_config(config_filename)
        ransac_threshold = config.get("ransacThreshold", 5.0)
        h, w = base_image.shape[:2]

        try:
            H_global, _ = cv2.findHomography(target_points, base_points, cv2.USAC_MAGSAC, ransac_threshold)
            if H_global is None: return None
        except Exception: return None

        if grid_size == (0, 0):
            return cv2.warpPerspective(base_image, H_global, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)

        min_points_per_cell = 8
        base_image_float = base_image.astype(np.float32) / max_val
        base_points_flat = base_points.reshape(-1, 2)
        target_points_flat = target_points.reshape(-1, 2)
        
        # --- LANGKAH 2: Daftar Tugas Paralel ---
        tasks = []
        for j in range(actual_grid_h):
            for i in range(actual_grid_w):
                tasks.append((i, j))

        num_threads = os.cpu_count() or 4
        
        # --- LANGKAH 3: Jalankan Tugas Paralel dan Kumpulkan Hasil ---
        all_results = []
        print(f"[Warp-Refine] Memproses {len(tasks)} sel grid menggunakan {num_threads} thread...")
        
        # ThreadPoolExecutor secara otomatis mengelola dan memparalelkan tugas
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_results = [
                executor.submit(
                    self._process_grid_cell,
                    i, j, h, w, actual_grid_w, actual_grid_h, 
                    min_points_per_cell, ransac_threshold, feather_pixels, 
                    base_image_float, base_points_flat, target_points_flat, H_global
                ) 
                for i, j in tasks
            ]
            # Ambil hasil dari setiap future
            for future in future_results:
                all_results.append(future.result())

        # --- LANGKAH 4: Akumulasi Hasil ---
        final_warped_image = np.zeros_like(base_image_float)
        weight_accumulator = np.zeros(base_image.shape[:2], dtype=np.float32)

        for warped_for_cell, weight_mask in all_results:
            if final_warped_image.ndim == 3:
                final_warped_image += warped_for_cell * weight_mask[:, :, np.newaxis]
            else:
                final_warped_image += warped_for_cell * weight_mask
            
            weight_accumulator += weight_mask

        # --- LANGKAH 5: FINALISASI ---
        try:
            weight_accumulator[weight_accumulator < 1e-6] = 1e-6 
            normalized_image = final_warped_image / (weight_accumulator[..., np.newaxis] if final_warped_image.ndim == 3 else weight_accumulator)
            output_image_float = normalized_image * max_val
            final_image = np.clip(output_image_float, 0, max_val).astype(original_dtype)
            
            print("[Warp] Proses kompensasi SELESAI dengan sukses.")
            return final_image
        except Exception as e:
            print(f"[Warp] ERROR saat finalisasi: {e}. Mengembalikan hasil warp global sebagai fallback.")
            return cv2.warpPerspective(base_image, H_global, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
                
def main(db_path,
         update_progress=None,
         stop_requested=None,
         single_process=None,
         batch_id=None,
         config_filename=None,
         save_align=None,
         align_folder=None,
         command_save_to_hd5f=None,
         num_workers=None):
    
    # --- Tahap 1: Inisialisasi dan Konfigurasi ---
    processor = ORBAlgorithm(db_path) 
    config = processor.load_orb_config(config_filename)
    
    # Tentukan parameter operasi dari argumen atau file konfigurasi
    save_align = save_align if save_align is not None else config.get("save_align", False)
    command_save_to_hd5f = command_save_to_hd5f if command_save_to_hd5f is not None else config.get("command_save_to_hd5f", True)
    align_folder = align_folder if align_folder is not None else config.get(
        "align_folder",
        os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image")
    )
    enable_cropping = config.get("enable_cropping", False)
    keep_edges = config.get("keep_edges", False)
    transformation_type = config.get("transformation", "affine")
    
    # Tentukan path input dan output
    if single_process:
        image_paths = get_all_image_paths_for_single_process(db_path)
        processor.hdf5_path = "database/align/aligned_images.h5"
    else:
        if batch_id is None:
            raise ValueError("Batch ID harus ada saat proses batch")
        image_paths = get_all_image_paths_for_batch_process(db_path, batch_id)
        processor.hdf5_path = f"database/align/aligned_image_batch_{batch_id}.h5"

    if not image_paths:
        if update_progress:
            update_progress(0, "Failed to load image paths.")
        return

    # Buat direktori output jika belum ada
    if command_save_to_hd5f:
        os.makedirs(os.path.dirname(processor.hdf5_path), exist_ok=True)
    if save_align and align_folder:
        os.makedirs(align_folder, exist_ok=True)
        
    extract_all_metadata(image_paths, metadata_file=os.path.join("database", "align", "metadata.json"))

    # --- Tahap 2: Pemuatan dan Penyiapan Base Image ---
    base_img_list = load_images_from_paths([image_paths[0]], stop_requested=stop_requested)
    if not base_img_list or base_img_list[0] is None:
        raise RuntimeError("Base image failed to load.")
    
    if num_workers is None:
        num_workers = 1
    
    base_image_raw = base_img_list[0]
    base_resized_list, (target_h, target_w) = resize_all_with_padding([base_image_raw], method="preserve")
    base_image = base_resized_list[0]

    del base_image_raw, base_resized_list, base_img_list
    gc.collect()

    # --- Tahap 3: Manajemen File dan Eksekusi Pipeline ---
    h5f = None
    try:
        if command_save_to_hd5f:
            h5f = h5py.File(processor.hdf5_path, "w")

        if not enable_cropping or keep_edges:
            run_pipeline_non_crop(
                processor=processor,
                image_paths=image_paths,
                base_image=base_image,
                target_dims=(target_h, target_w),
                update_progress=update_progress,
                stop_requested=stop_requested,
                save_align=save_align,
                align_folder=align_folder,
                h5_file_handle=h5f,
                num_workers=num_workers 
            )
        else:
            run_pipeline_global_crop(
                processor=processor,
                image_paths=image_paths,
                base_image=base_image,
                target_dims=(target_h, target_w),
                update_progress=update_progress,
                stop_requested=stop_requested,
                transformation_type=transformation_type,
                save_align=save_align,
                align_folder=align_folder,
                h5_file_handle=h5f,
                num_workers=num_workers 
            )
            
    except Exception as e:
        # Tangkap error apa pun yang mungkin terjadi selama pipeline
        print(f"A critical error occurred during the main pipeline: {e}\n{traceback.format_exc()}")
    finally:
        # --- Tahap 4: Cleanup ---
        if h5f:
            h5f.close()
          
def running_orb(parent=None, single_process=None, batch_id=None, progress_callback=None):
    
    # ==========================================================
    # KONDISI 1: MODE BATCH (TANPA GUI)
    # ==========================================================
    if batch_id is not None and progress_callback is not None:
        try:
            main(
                db_path="pixel_refine_database.db",
                update_progress=progress_callback,
                single_process=False, 
                batch_id=batch_id
            )
        except Exception as e:
            raise e
        return 

    # ==========================================================
    # KONDISI 2: MODE SINGLE (DENGAN GUI DIALOG)
    # ==========================================================
    process_finished = False
    
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_ORB)
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(
        Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint |
        Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint
    )

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

    worker = ImageProcessingMultiThreading(main, "pixel_refine_database.db", single_process=single_process, batch_id=batch_id)
    worker.progress_updated.connect(lambda progress, message: (
        progress_bar.setValue(progress),
        label.setText(message)
    ))

    def finish_handler():
        nonlocal process_finished
        process_finished = True
        dialog.close()
        worker.quit()
        worker.wait()

    worker.finished.connect(finish_handler)

    def error_handler(error):
        QMessageBox.critical(dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=error))
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    def on_dialog_close(event):
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