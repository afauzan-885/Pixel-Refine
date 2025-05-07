import gc
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
            "use_multi_core": False,
            "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image")
        }

        if config_filename is None:
            config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE 
        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("AKAZE", default_config)
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
            "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image")
        }

        if config_filename is None:
            config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE 

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("AKAZE_BATCH", default_config)
        except Exception as e:
            print("Error loading AKAZE configuration:", e)
            return default_config
        
    def prepare_gray_akaze(self, img):
        if img is None: raise ValueError("Input image is None.")
        if img.ndim == 3 and img.shape[2] == 3: gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif img.ndim == 3 and img.shape[2] == 4: gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY) # Tambahkan handle BGRA
        elif img.ndim == 2: gray = img
        else:
            raise ValueError(f"Invalid image dimensions/channels: {img.shape}")

        # Normalisasi ke uint8 jika perlu (penting untuk CLAHE dan AKAZE)
        if gray.dtype != np.uint8:
            max_val = np.max(gray)
            if gray.dtype == np.float32 or gray.dtype == np.float64:
                 # Jika rentang sudah 0-1 (umum untuk float), skala ke 0-255
                 if max_val <= 1.0 and np.min(gray) >= 0:
                     gray_norm = (gray * 255.0).astype(np.uint8)
                 # Jika rentang float > 1, coba normalisasi atau konversi langsung
                 # Normalisasi MINMAX mungkin mengubah kontras asli, jadi hati-hati
                 # Mungkin lebih baik konversi langsung jika datanya uint16/int16
                 else:
                     # Jika mungkin int16/uint16, coba scaling hati-hati
                     if gray.dtype == np.uint16:
                         gray_norm = (gray / 256.0).astype(np.uint8) # Asumsi 16-bit ke 8-bit
                     elif gray.dtype == np.int16:
                          gray_norm = ((gray / 256.0) + 128).astype(np.uint8) # Perkiraan kasar
                     else: # Fallback ke normalisasi jika tidak yakin
                         gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            elif gray.dtype == np.uint16:
                 # Konversi umum uint16 ke uint8
                 gray_norm = (gray / 256.0).astype(np.uint8)
            else: # Tipe lain yang tidak umum, coba normalisasi
                 gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            return gray_norm
        return gray

    # Fungsi compute_features_block Anda (dengan modifikasi kecil)
    # Sekarang menerima gambar grayscale *yang sudah ditingkatkan*
    def compute_features_block(self, akaze_instance, enhanced_gray_base, enhanced_gray_target, x, y, bw, bh, overlap_px, img_w, img_h):
        roi_x_start = max(0, x - overlap_px)
        roi_y_start = max(0, y - overlap_px)
        roi_x_end = min(img_w, x + bw + overlap_px)
        roi_y_end = min(img_h, y + bh + overlap_px)

        if roi_y_end <= roi_y_start or roi_x_end <= roi_x_start: return [], None, [], None

        # Gunakan ROI dari gambar yang *sudah ditingkatkan*
        roi_base_enhanced = enhanced_gray_base[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
        roi_target_enhanced = enhanced_gray_target[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

        # Deteksi pada ROI yang ditingkatkan
        kps_base, desc_base = akaze_instance.detectAndCompute(roi_base_enhanced, None)
        kps_target, desc_target = akaze_instance.detectAndCompute(roi_target_enhanced, None)

        # Penyesuaian koordinat dan filtering tetap sama, karena koordinat
        # mengacu pada gambar asli (bukan yang di-enhance secara spasial)
        kps_base_adjusted = []
        valid_desc_indices_base = [] # Kumpulkan indeks deskriptor valid
        if kps_base and desc_base is not None:
            for idx, kp in enumerate(kps_base):
                orig_kp_x = kp.pt[0] + roi_x_start
                orig_kp_y = kp.pt[1] + roi_y_start
                if x <= orig_kp_x < x + bw and y <= orig_kp_y < y + bh:
                    # Pastikan indeks deskriptor valid sebelum menambahkan
                    if idx < len(desc_base):
                        kp.pt = (orig_kp_x, orig_kp_y)
                        kps_base_adjusted.append(kp)
                        valid_desc_indices_base.append(idx) # Simpan indeks yang valid

        kps_target_adjusted = []
        valid_desc_indices_target = [] # Kumpulkan indeks deskriptor valid
        if kps_target and desc_target is not None:
            for idx, kp in enumerate(kps_target):
                orig_kp_x = kp.pt[0] + roi_x_start
                orig_kp_y = kp.pt[1] + roi_y_start
                if x <= orig_kp_x < x + bw and y <= orig_kp_y < y + bh:
                    if idx < len(desc_target):
                        kp.pt = (orig_kp_x, orig_kp_y)
                        kps_target_adjusted.append(kp)
                        valid_desc_indices_target.append(idx) # Simpan indeks yang valid

        # Filter deskriptor berdasarkan indeks yang valid
        final_desc_base = desc_base[valid_desc_indices_base] if desc_base is not None and valid_desc_indices_base else None
        final_desc_target = desc_target[valid_desc_indices_target] if desc_target is not None and valid_desc_indices_target else None

        # Validasi akhir (opsional tapi bagus)
        if final_desc_base is not None and len(kps_base_adjusted) != len(final_desc_base):
             print(f"Warning: Mismatch base keypoints ({len(kps_base_adjusted)}) vs descriptors ({len(final_desc_base)}) after filtering.")
             # Mungkin perlu mengembalikan None jika terjadi mismatch fatal
             # return [], None, kps_target_adjusted, final_desc_target # Atau handle lain

        if final_desc_target is not None and len(kps_target_adjusted) != len(final_desc_target):
             print(f"Warning: Mismatch target keypoints ({len(kps_target_adjusted)}) vs descriptors ({len(final_desc_target)}) after filtering.")
             # return kps_base_adjusted, final_desc_base, [], None # Atau handle lain

        return kps_base_adjusted, final_desc_base, kps_target_adjusted, final_desc_target

    def calculate_global_motion(self, base_image, target_image, config_filename=None, num_blocks=(3, 3), overlap=20, stop_requested=None):
        """
        Menghitung keypoints dan deskriptor menggunakan AKAZE. Gambar grayscale
        ditingkatkan KONTRASTNYA (menggunakan CLAHE) HANYA untuk deteksi fitur
        guna meningkatkan akurasi pada gambar gelap/kontras rendah.
        Pencocokan dan transformasi didasarkan pada fitur dari gambar yang ditingkatkan,
        namun transformasi nantinya diterapkan pada gambar ASLI.
        """
        if stop_requested and stop_requested():
            return None, None

        # 1. Baca Konfigurasi
        akaze_config = self.load_akaze_config(config_filename)
        use_multicore = akaze_config.get("use_multi_core", True)

        # --- 2. Konversi gambar ke grayscale uint8 (sekali) ---
        try:
            # Gunakan fungsi prepare_gray_akaze yang sudah dimodifikasi
            base_gray = self.prepare_gray_akaze(base_image)
            target_gray = self.prepare_gray_akaze(target_image)
        except ValueError as e:
            print(f"Error preparing grayscale images: {e}")
            return None, None
        except Exception as e:
             print(f"Unexpected error preparing grayscale: {e}")
             return None, None

        # --- 3. TINGKATKAN Kontras Grayscale HANYA untuk Deteksi ---
        try:
            # Buat objek CLAHE (parameter bisa disesuaikan)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            # Terapkan CLAHE ke gambar grayscale
            enhanced_base_gray = clahe.apply(base_gray)
            enhanced_target_gray = clahe.apply(target_gray)
            # CATATAN: base_gray dan target_gray ASLI tetap ada jika diperlukan
            #         tetapi deteksi fitur akan menggunakan versi enhanced.
        except Exception as e:
            print(f"Error applying CLAHE enhancement: {e}. Using original grayscale.")
            # Fallback ke grayscale asli jika CLAHE gagal
            enhanced_base_gray = base_gray
            enhanced_target_gray = target_gray
        # -------------------------------------------------------

        h, w = base_gray.shape # Dimensi tetap sama
        blocks_x, blocks_y = num_blocks
        # ... (logika perhitungan block_w, block_h Anda tetap sama) ...
        if blocks_x <= 0 or blocks_y <= 0: blocks_x, blocks_y = 1, 1
        block_w = w // blocks_x if blocks_x > 0 else w
        block_h = h // blocks_y if blocks_y > 0 else h
        if block_w <= 0: block_w = 1
        if block_h <= 0: block_h = 1


        # --- 4. Buat instance AKAZE SEKALI ---
        try:
            akaze = cv2.AKAZE_create(
                descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB,
                threshold=float(akaze_config.get("akaze_threshold", 0.001)),
                nOctaves=int(akaze_config.get("akaze_nOctaves", 4)),
                nOctaveLayers=int(akaze_config.get("akaze_nOctaveLayers", 4)),
                diffusivity=cv2.KAZE_DIFF_PM_G2 # Default yang bagus
            )
        except Exception as e:
            print(f"Error creating AKAZE instance: {e}")
            return None, None

        keypoints_base_all = []
        descriptors_base_list = []
        keypoints_target_all = []
        descriptors_target_list = []

        total_blocks = blocks_x * blocks_y

        # --- 5. Jalankan Deteksi pada Gambar yang DITINGKATKAN (Paralel atau Sekuensial) ---
        if use_multicore:
            futures = []
            try:
                max_workers = os.cpu_count()
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    for i in range(blocks_x):
                        for j in range(blocks_y):
                            if stop_requested and stop_requested():
                                # ... (cancel logic) ...
                                return None, None

                            x = i * block_w
                            y = j * block_h
                            # Perhitungan bw dan bh harus benar
                            current_bw = w - x if i == blocks_x - 1 else block_w
                            current_bh = h - y if j == blocks_y - 1 else block_h
                            # Pastikan tidak negatif atau nol
                            current_bw = max(1, current_bw)
                            current_bh = max(1, current_bh)

                            # Kirim gambar yang sudah DITINGKATKAN ke worker
                            futures.append(executor.submit(self.compute_features_block,
                                                             akaze,
                                                             enhanced_base_gray, # <-- Gunakan Enhanced
                                                             enhanced_target_gray, # <-- Gunakan Enhanced
                                                             x, y, current_bw, current_bh,
                                                             overlap, w, h))

                    # ... (bagian concurrent.futures.as_completed Anda tetap sama) ...
                    processed_count = 0
                    for future in concurrent.futures.as_completed(futures):
                        if stop_requested and stop_requested():
                             for f in futures: f.cancel()
                             return None, None
                        try:
                            kps_base, desc_base, kps_target, desc_target = future.result()
                            processed_count += 1

                            if desc_base is not None and len(kps_base) > 0:
                                keypoints_base_all.extend(kps_base)
                                descriptors_base_list.append(desc_base)
                            if desc_target is not None and len(kps_target) > 0:
                                keypoints_target_all.extend(kps_target)
                                descriptors_target_list.append(desc_target)

                        except concurrent.futures.CancelledError:
                            pass # Proses dibatalkan
                        except Exception as exc:
                             print(f"Error processing block result: {exc}")
                             pass # Lanjut ke blok berikutnya

            except Exception as e:
                 print(f"Error during ThreadPool execution: {e}")
                 return None, None

        else: # --- Mode Sekuensial ---
            processed_count = 0
            for i in range(blocks_x):
                for j in range(blocks_y):
                    if stop_requested and stop_requested(): return None, None

                    x = i * block_w
                    y = j * block_h
                    current_bw = w - x if i == blocks_x - 1 else block_w
                    current_bh = h - y if j == blocks_y - 1 else block_h
                    current_bw = max(1, current_bw)
                    current_bh = max(1, current_bh)

                    try:
                        # Panggil dengan gambar yang sudah DITINGKATKAN
                        kps_base, desc_base, kps_target, desc_target = self.compute_features_block(
                            akaze,
                            enhanced_base_gray, # <-- Gunakan Enhanced
                            enhanced_target_gray, # <-- Gunakan Enhanced
                            x, y, current_bw, current_bh,
                            overlap, w, h
                        )
                        processed_count += 1

                        if desc_base is not None and len(kps_base) > 0:
                            keypoints_base_all.extend(kps_base)
                            descriptors_base_list.append(desc_base)
                        if desc_target is not None and len(kps_target) > 0:
                            keypoints_target_all.extend(kps_target)
                            descriptors_target_list.append(desc_target)

                    except Exception as exc:
                        pass # Lanjut ke blok berikutnya

        # --- 6. Gabungkan Deskriptor ---
        # ... (Logika vstack Anda tetap sama) ...
        if not descriptors_base_list or not descriptors_target_list:
             return None, None
        try:
            # Pastikan list tidak kosong sebelum vstack
            descriptors_base_all = np.vstack(descriptors_base_list) if descriptors_base_list else np.array([], dtype=np.uint8).reshape(0, akaze.getDescriptorSize())
            descriptors_target_all = np.vstack(descriptors_target_list) if descriptors_target_list else np.array([], dtype=np.uint8).reshape(0, akaze.getDescriptorSize())

            # Pengecekan penting: jumlah keypoint harus cocok dengan jumlah deskriptor
            if len(keypoints_base_all) != descriptors_base_all.shape[0]:
                 print(f"CRITICAL: Final mismatch base keypoints ({len(keypoints_base_all)}) vs descriptors ({descriptors_base_all.shape[0]}).")
                 return None, None
            if len(keypoints_target_all) != descriptors_target_all.shape[0]:
                 print(f"CRITICAL: Final mismatch target keypoints ({len(keypoints_target_all)}) vs descriptors ({descriptors_target_all.shape[0]}).")
                 return None, None

        except ValueError as e:
             print(f"Error stacking descriptors: {e}")
             return None, None

        # --- 7. Lakukan Matching (menggunakan deskriptor dari gambar enhanced) ---
        # ... (Logika BFMatcher, knnMatch, ratio test Anda tetap sama) ...
        if descriptors_base_all.shape[0] == 0 or descriptors_target_all.shape[0] == 0:
             print("No descriptors available for matching.")
             return None, None

        base_points = None
        target_points = None
        try:
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False) # NORM_HAMMING untuk AKAZE/ORB/BRISK

            # Cek jika k=2 memungkinkan
            k_val = 0
            if descriptors_base_all.shape[0] >= 2 and descriptors_target_all.shape[0] >= 2:
                k_val = 2
            elif descriptors_base_all.shape[0] >= 1 and descriptors_target_all.shape[0] >= 1:
                 k_val = 1 # Fallback ke match biasa jika knnMatch k=2 tidak bisa

            good_matches = []
            if k_val >= 2:
                matches_raw = bf.knnMatch(descriptors_base_all, descriptors_target_all, k=k_val)
                ratio_thresh = float(akaze_config.get("ratio_threshold", 0.75))
                # Lakukan ratio test dengan hati-hati
                for match_pair in matches_raw:
                    # Pastikan match_pair memiliki 2 elemen sebelum unpacking
                    if len(match_pair) == 2:
                        m, n = match_pair
                        if m.distance < ratio_thresh * n.distance:
                            good_matches.append(m)
            elif k_val == 1:
                 print("Warning: Performing simple matching (k=1) due to insufficient descriptors for knnMatch k=2.")
                 matches_raw = bf.match(descriptors_base_all, descriptors_target_all)
                 good_matches = matches_raw # Ambil semua match jika hanya k=1
            else:
                 print("Error: Not enough descriptors in one or both images for any matching.")
                 return None, None


            min_matches_req = 4
            if len(good_matches) >= min_matches_req:
                try:
                    base_pts_list = []
                    target_pts_list = []
                    for m in good_matches:
                         if m.queryIdx < len(keypoints_base_all) and m.trainIdx < len(keypoints_target_all):
                            base_pts_list.append(keypoints_base_all[m.queryIdx].pt)
                            target_pts_list.append(keypoints_target_all[m.trainIdx].pt)
                    
                    if len(base_pts_list) >= min_matches_req: 
                       base_points = np.float32(base_pts_list).reshape(-1, 1, 2)
                       target_points = np.float32(target_pts_list).reshape(-1, 1, 2)
                    else:
                       base_points = None; target_points = None

                except Exception as e:
                    base_points = None; target_points = None
            else:
                print(f"Not enough good matches found ({len(good_matches)} < {min_matches_req}).")

        except cv2.error as cv_err:
             base_points = None; target_points = None
        except Exception as e:
            base_points = None; target_points = None

        if base_points is not None and target_points is not None:
            pass
        else:
             print("Failed to find sufficient matching points.")

        return base_points, target_points
        
    def compensate_motion(self, target_image, base_points, target_points, config_filename=None):
        """
        Menerapkan kompensasi gerakan menggunakan transformasi untuk menyelaraskan gambar TARGET ke BASE.
        PENTING: Fungsi ini harus menerima gambar TARGET asli, bukan yang di-enhance.
        base_points dan target_points didapatkan dari calculate_global_motion
        (yang mungkin menggunakan gambar enhanced untuk deteksi).
        """
        if target_image is None or base_points is None or target_points is None:
             print("Error: Invalid input to compensate_motion.")
             # Mungkin raise ValueError atau return None tergantung penanganan error Anda
             raise ValueError("Invalid input for motion compensation")

        config = self.load_akaze_config(config_filename)
        keep_edges = config.get("keep_edges", True) # Default ke True jika tidak ada
        transformation_type = config.get("transformation", "affine")
        ransac_threshold = config.get("ransacThreshold", 5.0)

        h, w = target_image.shape[:2] # Gunakan dimensi gambar TARGET yang akan di-warp

        # --- Hitung matriks transformasi ---
        # Perhatikan: Kita memetakan dari target ke base.
        # estimateAffine2D(src, dst) -> src=target_points, dst=base_points
        # findHomography(src, dst) -> src=target_points, dst=base_points
        matrix = None
        mask = None

        # Pastikan jumlah point cukup
        min_req = 4 if transformation_type == 'homography' else 3 # Affine/Similarity butuh 3
        if len(target_points) < min_req or len(base_points) < min_req:
             print(f"Error: Not enough points ({len(target_points)}) for {transformation_type} transform (need {min_req}).")
             raise ValueError(f"Not enough points for {transformation_type}")

        try:
            if transformation_type == 'affine':
                # cv2.estimateAffine2D mengembalikan matriks 2x3
                matrix, mask = cv2.estimateAffine2D(target_points, base_points, method=cv2.USAC_MAGSAC, ransacReprojThreshold=ransac_threshold)
            elif transformation_type in ['similarity', 'euclidean']:
                # cv2.estimateAffinePartial2D juga mengembalikan matriks 2x3
                matrix, mask = cv2.estimateAffinePartial2D(target_points, base_points, method=cv2.USAC_MAGSAC, ransacReprojThreshold=ransac_threshold)
            elif transformation_type == 'homography':
                # cv2.findHomography mengembalikan matriks 3x3
                matrix, mask = cv2.findHomography(target_points, base_points, cv2.USAC_MAGSAC, ransac_threshold)
            else:
                # Gunakan pesan dari language_config jika ada
                # raise ValueError(language_config.UNRECOGNIZED_TRANSFORMATION)
                raise ValueError(f"Unrecognized transformation type: {transformation_type}")

            # Pastikan matriks valid
            if matrix is None:
                # raise ValueError(language_config.FAILED_TO_COMPUTE_TRANSFORMATION)
                raise ValueError("Failed to compute transformation matrix (returned None)")

            # Hitung jumlah inlier (opsional tapi informatif)
            if mask is not None:
                inliers = np.sum(mask)
                print(f"Transformation computed with {inliers} inliers out of {len(target_points)} points.")
                if inliers < min_req:
                    print(f"Warning: Number of inliers ({inliers}) is less than minimum required ({min_req}). Result might be unstable.")
                    # Pertimbangkan raise error jika inlier terlalu sedikit

        except cv2.error as cv_err:
             print(f"OpenCV error during transformation estimation: {cv_err}")
             raise ValueError(f"OpenCV error estimating transform: {cv_err}")
        except Exception as e:
             print(f"General error during transformation estimation: {e}")
             raise ValueError(f"Error estimating transform: {e}")


        # --- Terapkan Transformasi pada Gambar TARGET ASLI ---
        output_size = (w, h) # Default ke ukuran asli target
        compensated_image = None

        # Logika padding jika keep_edges=True
        pad_top, pad_bottom, pad_left, pad_right = 0, 0, 0, 0
        if keep_edges:
            # Hitung transformasi sudut untuk menentukan ukuran output & padding
            corners_target = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(-1, 1, 2)
            if transformation_type == 'homography':
                transformed_corners = cv2.perspectiveTransform(corners_target, matrix)
            else:
                 # Untuk matriks 2x3, kita perlu menambahkan baris [0, 0, 1]
                 # agar bisa digunakan dengan cv2.transform jika shape matriksnya 2x3
                 if matrix.shape == (2, 3):
                     matrix_3x3 = np.vstack([matrix, [0, 0, 1]])
                     # Perlu reshape corners ke (N, 1, 2)
                     corners_target_reshaped = corners_target.reshape(-1, 1, 2)
                     transformed_corners = cv2.transform(corners_target_reshaped, matrix) # matrix 2x3 sudah cukup
                 else: # Jika sudah 3x3 (misal dari partial affine)
                     transformed_corners = cv2.transform(corners_target, matrix)


            if transformed_corners is not None:
                transformed_corners = transformed_corners.reshape(-1, 2)
                min_x, min_y = transformed_corners.min(axis=0)
                max_x, max_y = transformed_corners.max(axis=0)

                # Hitung padding yang dibutuhkan di sekitar *area asli*
                pad_left = max(0, int(np.ceil(-min_x)))
                pad_top = max(0, int(np.ceil(-min_y)))
                # Padding kanan/bawah dihitung dari seberapa jauh sudut bergerak > w atau > h
                pad_right = max(0, int(np.ceil(max_x - w)))
                pad_bottom = max(0, int(np.ceil(max_y - h)))

                # Ukuran output canvas adalah ukuran asli + padding total
                out_w = w + pad_left + pad_right
                out_h = h + pad_top + pad_bottom
                output_size = (out_w, out_h)

                # Kita perlu menggeser transformasi agar sesuai dengan canvas baru
                # Buat matriks translasi M_trans = [[1, 0, pad_left], [0, 1, pad_top]]
                translation_matrix = np.float32([[1, 0, pad_left], [0, 1, pad_top]])

                if transformation_type == 'homography':
                    # Gabungkan translasi dengan homografi: M_final = M_trans * M_homography
                    # Untuk homografi 3x3, matriks translasi juga perlu 3x3
                    translation_matrix_3x3 = np.identity(3, dtype=np.float32)
                    translation_matrix_3x3[0, 2] = pad_left
                    translation_matrix_3x3[1, 2] = pad_top
                    matrix = translation_matrix_3x3 @ matrix # Urutan penting!
                else:
                    # Gabungkan translasi dengan affine: M_final = M_trans * M_affine (secara efektif)
                    # M_affine = [[m11, m12, m13], [m21, m22, m23]]
                    # M_final = [[m11, m12, m13 + pad_left], [m21, m22, m23 + pad_top]]
                    matrix[0, 2] += pad_left
                    matrix[1, 2] += pad_top
            else:
                 print("Warning: Could not transform corners for keep_edges=True. Using original size.")
                 keep_edges = False # Fallback

        # Terapkan warping
        try:
            warp_flags = cv2.INTER_LINEAR # Interpolasi yang baik
            border_mode = cv2.BORDER_CONSTANT # Isi area luar dengan hitam
            if keep_edges: # Jika keep_edges dan padding dihitung
                border_mode = cv2.BORDER_REFLECT # Atau BORDER_REPLICATE lebih baik untuk hindari artefak?

            if transformation_type == 'homography':
                compensated_image = cv2.warpPerspective(target_image, matrix, output_size, flags=warp_flags, borderMode=border_mode)
            else:
                compensated_image = cv2.warpAffine(target_image, matrix, output_size, flags=warp_flags, borderMode=border_mode)

        except cv2.error as cv_err:
             print(f"OpenCV error during warping: {cv_err}")
             raise ValueError(f"OpenCV error during warping: {cv_err}")
        except Exception as e:
             print(f"General error during warping: {e}")
             raise ValueError(f"Error during warping: {e}")


        return compensated_image

def main(db_path, update_progress=None, batch_size=8, stop_requested=None, single_process=None, batch_id=None,
         config_filename=None, save_align=None, align_folder=None, command_save_to_hd5f=None):
    
    # Inisialisasi processor dan konfigurasi
    processor = AKAZEAlgorithm(db_path)
    config = processor.load_akaze_config(config_filename)
    
    if save_align is None:
        save_align = config.get("save_align", False)
    
    if command_save_to_hd5f is None:
        command_save_to_hd5f = config.get("command_save_to_hd5f", True)
    
    if align_folder is None:
        align_folder = config.get("align_folder", os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image"))
    
    enable_cropping = config.get("enable_cropping", True)
    transformation_type = config.get("transformation", "affine")
    
    # Dapatkan semua path gambar
    if single_process:
        image_paths = get_all_image_paths_for_single_process(db_path)
        processor.hdf5_path = "database/align/aligned_images.h5"
    else:
        if batch_id is None:
            raise ValueError(language_config.BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS)
        image_paths = processor.get_all_image_paths_for_batch_process(batch_id)
        processor.hdf5_path = f"database/align/aligned_image_batch_{batch_id}.h5"
    
    if not image_paths:
        if update_progress:
            update_progress(0, language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
        return
    
    # Ekstrak metadata dari seluruh gambar dan simpan ke file JSON
    metadata_folder = os.path.join("database", "align")
    os.makedirs(metadata_folder, exist_ok=True)
    metadata_file = os.path.join(metadata_folder, "metadata.json")
    extract_all_metadata(image_paths, metadata_file=metadata_file)
    
    base_image_path = image_paths[0]
    loaded_base_list = load_images_from_paths([base_image_path], stop_requested=stop_requested) # Tambahkan argumen lain jika perlu

    if not loaded_base_list:
        print(language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
        return
    else:
        base_image = loaded_base_list[0]
    if base_image is None:
        print(language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
        return
    
    total_images = len(image_paths)
    total_batches = (total_images - 1) // batch_size + 1
    total_steps = total_images * 2
    current_step = 0
    
    transform_folder = os.path.join("database", "align", "transformasi")
    os.makedirs(transform_folder, exist_ok=True)
    
    # Phase 1: Estimasi transformasi
    for batch_idx in range(total_batches):
        if stop_requested and stop_requested():
            break
        
        start_idx = batch_idx * batch_size + 1
        end_idx = min((batch_idx + 1) * batch_size + 1, total_images)
        batch_paths = image_paths[start_idx:end_idx]
        batch_images = load_images_from_paths(batch_paths)
        if not batch_images:
            continue
        
        for i, target_image in enumerate(batch_images, start=start_idx):
            if stop_requested and stop_requested():
                break
            
            info_message = language_config.RUN_IMAGE_PROCESSING.format(i=i, total_images=total_images)
            print(info_message)
            
            base_points, target_points = processor.calculate_global_motion(base_image, target_image)
            if base_points is None or target_points is None:
                print(language_config.FAIL_COMPENSATE_MOTION_PROCESS.format(i=i))
                current_step += 1
                if update_progress:
                    update_progress(current_step, total_steps, language_config.FAIL_COMPENSATE_MOTION_PROCESS.format(i))
                continue
            
            transform_file_path = os.path.join(transform_folder, f"transform_{i}.npy")
            np.save(transform_file_path, (base_points, target_points))
            
            current_step += 1
            if update_progress:
                update_progress(current_step, total_steps, info_message)
        
        del batch_images, batch_paths
        gc.collect()
    
    # Hitung crop bounds jika diaktifkan
    crop_bounds = None
    if enable_cropping:
        h, w = base_image.shape[:2]
        crop_bounds = compute_global_crop(transform_folder, total_images, w, h, transformation_type=transformation_type)
        if crop_bounds is None:
            print(language_config.FAILED_TO_COMPUTE_CROP)
            return
        np.save(os.path.join(transform_folder, "crop.npy"), crop_bounds)
    
    # Phase 2: Terapkan transformasi dan simpan ke HDF5 jika diizinkan
    with h5py.File(processor.hdf5_path, "w") as h5f:
        if enable_cropping:
            base_image = crop_image(base_image, crop_bounds)
        
        if command_save_to_hd5f:
            h5f.create_dataset("image_0", data=base_image)
        
        if save_align:
            save_align_to_folder(base_image, 0, base_image_path, align_folder)
        
        num_threads = os.cpu_count() or 4
        
        for batch_idx in range(total_batches):
            if stop_requested and stop_requested():
                break
            
            start_idx = batch_idx * batch_size + 1
            end_idx = min((batch_idx + 1) * batch_size + 1, total_images)
            batch_paths = image_paths[start_idx:end_idx]
            batch_images = load_images_from_paths(batch_paths, stop_requested)
            if stop_requested and stop_requested(): 
                break
            
            if not batch_images:
                continue
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for i, target_image in enumerate(batch_images, start=start_idx):
                    if stop_requested and stop_requested():
                        break
                    
                    transform_file_path = os.path.join(transform_folder, f"transform_{i}.npy")
                    if not os.path.exists(transform_file_path):
                        print(language_config.FAIL_LOAD_TRANSFORMATION_MATRIX_FILE.format(i))
                        current_step += 1
                        if update_progress:
                            update_progress(current_step, total_steps, language_config.FAIL_LOAD_TRANSFORMATION_MATRIX_FILE.format(i))
                        continue
                    
                    base_points, target_points = np.load(transform_file_path, allow_pickle=True)
                    compensated_image = processor.compensate_motion(target_image, base_points, target_points)
                    
                    if enable_cropping:
                        compensated_image = crop_image(compensated_image, crop_bounds)
                    
                    if save_align:
                        save_align_to_folder(compensated_image, i, batch_paths[i - start_idx], align_folder)
                    
                    # Ekstrak metadata untuk gambar yang sedang diproses (dari path asli)
                    original_path = batch_paths[i - start_idx]
                    metadata = extract_exif(original_path)
                    
                    # Simpan ke HDF5 jika diizinkan, sertakan metadata
                    if command_save_to_hd5f:
                        dataset_name = f"image_{i}"
                        futures.append(executor.submit(save_to_hdf5, h5f, dataset_name, compensated_image, metadata))
                    
                    current_step += 1
                    if update_progress:
                        update_progress(current_step, total_steps,
                                        language_config.PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION.format(i, total_images))
                    
                    del base_points, target_points, compensated_image
                
                for future in futures:
                    future.result()
            
            del batch_images, batch_paths, futures
            gc.collect()
                
def running_akaze(parent=None, single_process=None, batch_id=None):
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