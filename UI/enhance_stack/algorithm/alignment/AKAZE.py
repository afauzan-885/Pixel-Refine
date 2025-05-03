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

    def calculate_global_motion(self, base_image, target_image, config_filename=None, num_blocks=(4, 4), overlap=20, stop_requested=None):
        """
        Menghitung keypoints dan deskriptor menggunakan AKAZE dengan membagi gambar
        menjadi blok-blok secara paralel. Instance AKAZE dibuat sekali.

        Parameter:
          - num_blocks: tuple (blocks_x, blocks_y) untuk pembagian gambar.
          - overlap: jumlah piksel overlap di sekeliling tiap blok.
        """
        if stop_requested and stop_requested():
            return None, None

        # 1. Baca Konfigurasi
        akaze_config = self.load_akaze_config(config_filename)
        use_multicore = akaze_config.get("use_multi_core", True) # Ambil flag dari config

        # --- 2. Konversi gambar ke grayscale (sekali) ---
        try:
            def prepare_gray_akaze(img):
                if img is None: raise ValueError("Input image is None.")
                if img.ndim == 3 and img.shape[2] == 3: gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                elif img.ndim == 2: gray = img
                else: raise ValueError(f"Invalid image dimensions/channels: {img.shape}")
                if gray.dtype != np.uint8:
                    if gray.dtype == np.float32 or gray.dtype == np.float64:
                        if gray.max() <= 1.0:
                             gray_norm = (gray * 255).astype(np.uint8)
                        else:
                             gray_norm = gray.astype(np.uint8)
                    else: 
                         gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
                         gray_norm = gray_norm.astype(np.uint8)
                    return gray_norm
                return gray

            base_gray = prepare_gray_akaze(base_image)
            target_gray = prepare_gray_akaze(target_image)
        except ValueError as e:
            return None, None
        except Exception as e:
             return None, None
        # --------------------------------------------

        h, w = base_gray.shape
        blocks_x, blocks_y = num_blocks
        if blocks_x <= 0 or blocks_y <= 0:
            return None, None
        block_w = w // blocks_x
        block_h = h // blocks_y
        if block_w == 0 or block_h == 0:
             print(f"Warning: Image size ({w}x{h}) too small for {num_blocks} blocks. Adjusting blocks.")
             blocks_x = max(1, w)
             blocks_y = max(1, h)
             block_w = 1
             block_h = 1
             num_blocks = (blocks_x, blocks_y) 

        # --- 3. Buat instance AKAZE SEKALI di sini ---
        try:
            akaze = cv2.AKAZE_create(
                descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB,
                threshold=float(akaze_config.get("akaze_threshold", 0.001)),
                nOctaves=int(akaze_config.get("akaze_nOctaves", 4)),
                nOctaveLayers=int(akaze_config.get("akaze_nOctaveLayers", 4)),
                diffusivity=cv2.KAZE_DIFF_PM_G2
            )
        except Exception as e:
            print(f"Error creating AKAZE instance: {e}")
            return None, None
     
        keypoints_base_all = []
        descriptors_base_list = []
        keypoints_target_all = []
        descriptors_target_list = []

        total_blocks = blocks_x * blocks_y

        def compute_features_block(akaze_instance, img_base, img_target, x, y, bw, bh, overlap_px, img_w, img_h):
            roi_x_start = max(0, x - overlap_px)
            roi_y_start = max(0, y - overlap_px)
            roi_x_end = min(img_w, x + bw + overlap_px)
            roi_y_end = min(img_h, y + bh + overlap_px)

            if roi_y_end <= roi_y_start or roi_x_end <= roi_x_start: return [], None, [], None

            roi_base = img_base[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
            roi_target = img_target[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

            kps_base, desc_base = akaze_instance.detectAndCompute(roi_base, None)
            kps_target, desc_target = akaze_instance.detectAndCompute(roi_target, None)

            kps_base_adjusted = []
            if kps_base:
                for kp in kps_base:
                    # Hanya proses keypoint jika deskriptornya valid (ada)
                    # Cek apakah koordinat berada di dalam blok asli (tanpa overlap)
                    # untuk menghindari duplikasi di batas overlap
                    orig_kp_x = kp.pt[0] + roi_x_start
                    orig_kp_y = kp.pt[1] + roi_y_start
                    if x <= orig_kp_x < x + bw and y <= orig_kp_y < y + bh:
                        kp.pt = (orig_kp_x, orig_kp_y)
                        kps_base_adjusted.append(kp)
                    # Note: Filter overlap ini mungkin mengurangi jumlah keypoint total,
                    # tapi mencegah satu keypoint dideteksi & ditambahkan berkali-kali
                    # dari blok-blok yang overlap. Alternatifnya adalah membiarkan duplikasi
                    # dan melakukan non-maximal suppression *setelah* semua keypoint terkumpul.
                    # Untuk kesederhanaan, filter di sini dulu.

            kps_target_adjusted = []
            # Pastikan desc_target tidak None sebelum mengaksesnya
            if kps_target and desc_target is not None:
                for idx, kp in enumerate(kps_target):
                    orig_kp_x = kp.pt[0] + roi_x_start
                    orig_kp_y = kp.pt[1] + roi_y_start
                    if x <= orig_kp_x < x + bw and y <= orig_kp_y < y + bh:
                         if idx < len(desc_target):
                            kp.pt = (orig_kp_x, orig_kp_y)
                            kps_target_adjusted.append(kp)
                         else: # Jarang terjadi, tapi jaga-jaga
                            print(f"Warning: Keypoint index {idx} out of bounds for target descriptors (len={len(desc_target)}) in block.")


            # Penting: Filter deskriptor agar sesuai dengan keypoint yang sudah difilter
            valid_desc_indices_base = [i for i, kp in enumerate(kps_base) if kp in kps_base_adjusted] if kps_base else []
            valid_desc_indices_target = [i for i, kp in enumerate(kps_target) if kp in kps_target_adjusted] if kps_target else []

            final_desc_base = desc_base[valid_desc_indices_base] if desc_base is not None and valid_desc_indices_base else None
            final_desc_target = desc_target[valid_desc_indices_target] if desc_target is not None and valid_desc_indices_target else None

            # Pastikan jumlah keypoint dan deskriptor cocok setelah filter
            if final_desc_base is not None and len(kps_base_adjusted) != len(final_desc_base):
                 print(f"Warning: Mismatch base keypoints ({len(kps_base_adjusted)}) and descriptors ({len(final_desc_base)}) after filtering.")
              
            if final_desc_target is not None and len(kps_target_adjusted) != len(final_desc_target):
                 print(f"Warning: Mismatch target keypoints ({len(kps_target_adjusted)}) and descriptors ({len(final_desc_target)}) after filtering.")
              
            return kps_base_adjusted, final_desc_base, kps_target_adjusted, final_desc_target

        # --- 5. Jalankan Deteksi (Paralel atau Sekuensial) ---
        if use_multicore:
            print(f"Using Multi-Core AKAZE block processing ({total_blocks} blocks)...")
            futures = []
            try:
                # Gunakan max_workers dari os.cpu_count() atau batasi jika perlu
                max_workers = os.cpu_count()
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    for i in range(blocks_x):
                        for j in range(blocks_y):
                            
                            if stop_requested and stop_requested():
                                for f in futures: f.cancel()
                                executor.shutdown(wait=False, cancel_futures=True)
                                return None, None # Keluar secepatnya

                            x = i * block_w
                            y = j * block_h
                            bw = w - x if i == blocks_x - 1 else block_w
                            bh = h - y if j == blocks_y - 1 else block_h

                            # Submit tugas ke executor
                            futures.append(executor.submit(compute_features_block, akaze, base_gray, target_gray, x, y, bw, bh, overlap, w, h))

                    processed_count = 0
                    for future in concurrent.futures.as_completed(futures):
                        if stop_requested and stop_requested():
                             for f in futures: f.cancel()
                             return None, None
                        try:
                            kps_base, desc_base, kps_target, desc_target = future.result()
                            processed_count += 1

                            # Tambahkan hasil valid ke list
                            if desc_base is not None and len(kps_base) > 0:
                                keypoints_base_all.extend(kps_base)
                                descriptors_base_list.append(desc_base)
                            if desc_target is not None and len(kps_target) > 0:
                                keypoints_target_all.extend(kps_target)
                                descriptors_target_list.append(desc_target)

                        except concurrent.futures.CancelledError:
                            pass
                        except Exception as exc:
                            pass
            except Exception as e:
                 print(f"Error during ThreadPool execution: {e}")
                 return None, None # Gagal jika executor error

        else: # --- Mode Sekuensial ---
            print(f"Using Single-Core AKAZE block processing ({total_blocks} blocks)...")
            processed_count = 0
            for i in range(blocks_x):
                for j in range(blocks_y):
                    if stop_requested and stop_requested():
                        return None, None # Keluar

                    x = i * block_w
                    y = j * block_h
                    bw = w - x if i == blocks_x - 1 else block_w
                    bh = h - y if j == blocks_y - 1 else block_h

                    try:
                        # Panggil fungsi worker secara langsung
                        kps_base, desc_base, kps_target, desc_target = compute_features_block(
                            akaze, base_gray, target_gray, x, y, bw, bh, overlap, w, h
                        )
                        processed_count += 1
                        
                        # Tambahkan hasil valid ke list
                        if desc_base is not None and len(kps_base) > 0:
                            keypoints_base_all.extend(kps_base)
                            descriptors_base_list.append(desc_base)
                        if desc_target is not None and len(kps_target) > 0:
                            keypoints_target_all.extend(kps_target)
                            descriptors_target_list.append(desc_target)

                    except Exception as exc:
                        pass
      
        # --- 6. Gabungkan Deskriptor ---
        if not descriptors_base_list or not descriptors_target_list:
             return None, None

        try:
            descriptors_base_all = np.vstack(descriptors_base_list) if descriptors_base_list else None
            descriptors_target_all = np.vstack(descriptors_target_list) if descriptors_target_list else None
        except ValueError as e:
             return None, None

        # --- 7. Lakukan Matching ---
        if descriptors_base_all is None or descriptors_target_all is None or \
           len(keypoints_base_all) == 0 or len(keypoints_target_all) == 0 or \
           len(descriptors_base_all) == 0 or len(descriptors_target_all) == 0:
            print("Not enough keypoints or descriptors found for matching.")
            return None, None

        # Pastikan jumlah keypoint sesuai dengan jumlah deskriptor sebelum matching
        if len(keypoints_base_all) != len(descriptors_base_all):
            return None, None
        if len(keypoints_target_all) != len(descriptors_target_all):
            return None, None


        base_points = None
        target_points = None
        try:
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            k_val = min(2, len(descriptors_target_all), len(descriptors_base_all)) # Juga cek base

            good_matches = []
            if k_val < 2:
                 matches_raw = bf.match(descriptors_base_all, descriptors_target_all)
                 good_matches = matches_raw
            else:
                # Lakukan KNN Match
                matches_raw = bf.knnMatch(descriptors_base_all, descriptors_target_all, k=k_val)

                # Terapkan Ratio Test Lowe
                ratio_thresh = float(akaze_config.get("ratio_threshold", 0.75))
                for match_pair in matches_raw:
                    if len(match_pair) == k_val:
                        m, n = match_pair
                        if m.distance < ratio_thresh * n.distance:
                            good_matches.append(m)
                
            # --- 8. Ekstrak titik-titik yang cocok ---
            min_matches_req = 4
            if len(good_matches) >= min_matches_req:
                try:
                    base_points_list = []
                    target_points_list = []
                    valid_good_matches = []
                    for m in good_matches:
                        if m.queryIdx < len(keypoints_base_all) and m.trainIdx < len(keypoints_target_all):
                            base_points_list.append(keypoints_base_all[m.queryIdx].pt)
                            target_points_list.append(keypoints_target_all[m.trainIdx].pt)
                            valid_good_matches.append(m)
                        else:
                            pass

                    if len(valid_good_matches) >= min_matches_req:
                        base_points = np.float32(base_points_list).reshape(-1, 1, 2)
                        target_points = np.float32(target_points_list).reshape(-1, 1, 2)
                    else:
                         print(f"Not enough valid matches remaining ({len(valid_good_matches)} < {min_matches_req}) after index check.")


                except IndexError as e: # Seharusnya sudah ditangani oleh cek di atas, tapi jaga-jaga
                    print(f"Error extracting points (IndexError): {e}. Match indices might be invalid.")
                    base_points = None; target_points = None
                except Exception as e:
                     print(f"Error extracting points: {e}")
                     base_points = None; target_points = None
            else:
                print(f"Not enough good matches found ({len(good_matches)} < {min_matches_req}) to estimate transform.")


        except cv2.error as cv_err:
             print(f"OpenCV Error during matching or point extraction: {cv_err}")
             base_points = None; target_points = None
        except Exception as e:
            import traceback
            print(f"Unexpected error during matching/point extraction: {e}\n{traceback.format_exc()}")
            base_points = None; target_points = None


        return base_points, target_points
        
    def compensate_motion(self, base_image, base_points, target_points, config_filename=None):
        """
        Menerapkan kompensasi gerakan menggunakan transformasi untuk menyelaraskan gambar.
        """
        config = self.load_akaze_config(config_filename)
        keep_edges = config["keep_edges"]
        transformation_type = config["transformation"]
        ransac_threshold = config["ransacThreshold"]

        h, w = base_image.shape[:2]

        # Hitung matriks transformasi
        if transformation_type == 'affine':
            matrix, mask = cv2.estimateAffine2D(target_points, base_points, method=cv2.USAC_MAGSAC, ransacReprojThreshold=ransac_threshold)
        elif transformation_type in ['similarity', 'euclidean']:
            matrix, mask = cv2.estimateAffinePartial2D(target_points, base_points, method=cv2.USAC_MAGSAC, ransacReprojThreshold=ransac_threshold)
        elif transformation_type == 'homography':
            matrix, mask = cv2.findHomography(target_points, base_points, cv2.USAC_MAGSAC, ransac_threshold)
        else:
            raise ValueError(language_config.UNRECOGNIZED_TRANSFORMATION)

        # Pastikan matriks valid
        if matrix is None:
            raise ValueError(language_config.FAILED_TO_COMPUTE_TRANSFORMATION)

        # Hitung batas pergeseran (terlepas dari keep_edges)
        corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(-1, 1, 2)

        if transformation_type == 'homography':
            transformed_corners = cv2.perspectiveTransform(corners, matrix)
        else:
            transformed_corners = cv2.transform(corners, matrix)

        transformed_corners = transformed_corners.reshape(-1, 2)
        min_x, min_y = transformed_corners.min(axis=0)
        max_x, max_y = transformed_corners.max(axis=0)

        # print(f"Pergerakan batas: min_x={min_x}, min_y={min_y}, max_x={max_x}, max_y={max_y}")

        # Jika keep_edges = False, langsung terapkan transformasi tanpa padding
        if not keep_edges:
            if transformation_type == 'homography':
                compensated_image = cv2.warpPerspective(base_image, matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            else:
                compensated_image = cv2.warpAffine(base_image, matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            return compensated_image

        # Jika keep_edges = True, tambahkan padding berdasarkan batas pergeseran
        pad_x = max(0, int(np.ceil(max_x - w)))
        pad_y = max(0, int(np.ceil(max_y - h)))
        pad_left = max(0, int(np.ceil(-min_x))) 
        pad_top = max(0, int(np.ceil(-min_y)))  

        pad = max(pad_x, pad_y, pad_left, pad_top)

        padded_image = cv2.copyMakeBorder(base_image, pad, pad, pad, pad, cv2.BORDER_REFLECT)

        if transformation_type == 'homography':
            compensated_padded = cv2.warpPerspective(padded_image, matrix, (padded_image.shape[1], padded_image.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        else:
            compensated_padded = cv2.warpAffine(padded_image, matrix, (padded_image.shape[1], padded_image.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        compensated_image = compensated_padded[pad:pad+h, pad:pad+w] if keep_edges else compensated_padded

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
    
    # Proses gambar pertama sebagai base_image
    base_image_path = image_paths[0]
    base_image = cv2.imread(base_image_path, cv2.IMREAD_UNCHANGED)
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
        
        # Simpan referensi gambar ke HDF5 hanya jika command_save_to_hd5f aktif
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
            batch_images = load_images_from_paths(batch_paths)
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