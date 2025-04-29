from concurrent.futures import ThreadPoolExecutor
import gc
import time
import exifread
import json
import subprocess
import cv2
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import compute_global_crop, crop_image, extract_all_metadata, extract_exif, load_images_from_paths, save_align_to_folder, save_to_hdf5
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config

class ORBAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        # Pastikan folder HDF5 ada
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

    def get_all_image_paths_for_single_process(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT images.path 
                FROM single_process_image
                JOIN images ON single_process_image.image_id_single = images.id
            """)
            return [row[0] for row in cursor.fetchall()]
        
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
    def load_orb_config(config_filename=None):
        """
        Membaca konfigurasi ORB dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "nfeatures": 1500,
            "scaleFactor": 1.1,
            "nlevels": 5,
            "ransacThreshold": 5.0,
            "transformation": "homography",
            "keep_edges": False,
            "enable_cropping": False,
            "save_align": False,  
            "command_save_to_hd5f": True,
            "align_folder": os.path.join(
                os.path.expanduser("~"), 
                "Documents", 
                "Pixel Refine", 
                "align_image"
            )
        }

        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return {**default_config, **params.get("ORB", {})}
        except Exception as e:
            print("Error loading ORB configuration:", e)
            return default_config  # Gunakan default jika file tidak ditemukan atau ada error
        
    def load_orb_config_for_batch(config_filename=None):
        """
        Membaca konfigurasi ORB dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "nfeatures": 1500,
            "scaleFactor": 1.1,
            "nlevels": 5,
            "ransacThreshold": 5.0,
            "transformation": "homography",
            "keep_edges": True,
            "enable_cropping": False,
            "save_align": False,  
            "command_save_to_hd5f": True,
            "align_folder": os.path.join(
                os.path.expanduser("~"), 
                "Documents", 
                "Pixel Refine", 
                "align_image"
            )
        }

        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return {**default_config, **params.get("ORB_BATCH", {})}
        except Exception as e:
            print("Error loading ORB configuration:", e)
            return default_config  # Gunakan default jika file tidak ditemukan atau ada error


    def calculate_global_motion(self, base_image, target_image, config_filename=None, stop_requested=None):
        """
        Menghitung keypoints/deskriptor menggunakan ORB dengan preprocessing CLAHE,
        dan matching KNN + Ratio Test. Tidak menggunakan paralelisasi blok.
        """
        if stop_requested and stop_requested():
            return None, None

        # Baca konfigurasi ORB (termasuk parameter CLAHE & ratio test)
        orb_config = self.load_orb_config(config_filename)

        # --- Konversi gambar ke grayscale 8-bit (penting untuk ORB & CLAHE) ---
        try:
            if base_image.ndim == 3 and base_image.shape[2] == 3:
                base_gray_8bit = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
            elif base_image.ndim == 2:
                base_gray_8bit = base_image
            else:
                raise ValueError("Base image has unsupported channels")
            # Konversi tipe ke uint8 jika belum
            if base_gray_8bit.dtype != np.uint8:
                 # Normalisasi MINMAX adalah cara umum untuk konversi 16bit->8bit
                 base_gray_8bit = cv2.normalize(base_gray_8bit, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)


            if target_image.ndim == 3 and target_image.shape[2] == 3:
                target_gray_8bit = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
            elif target_image.ndim == 2:
                target_gray_8bit = target_image
            else:
                 raise ValueError("Target image has unsupported channels")
            if target_gray_8bit.dtype != np.uint8:
                 target_gray_8bit = cv2.normalize(target_gray_8bit, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

        except Exception as e:
            return None, None
        # -----------------------------------------------------------------

        # --- Preprocessing: Terapkan CLAHE ---
        try:
            clip_limit = orb_config.get("clahe_clipLimit", 2.0)
            grid_size = tuple(orb_config.get("clahe_tileGridSize", (8, 8)))
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
            base_gray_enhanced = clahe.apply(base_gray_8bit)
            target_gray_enhanced = clahe.apply(target_gray_8bit)
        except Exception as e:
            base_gray_enhanced = base_gray_8bit # Fallback
            target_gray_enhanced = target_gray_8bit
        # -------------------------------------

        # --- Inisialisasi ORB ---
        try:
            orb = cv2.ORB_create(
                nfeatures=orb_config.get("nfeatures", 1000), # Default lebih tinggi
                scaleFactor=orb_config.get("scaleFactor", 1.2),
                nlevels=orb_config.get("nlevels", 8),
                # Parameter lain bisa ditambahkan jika perlu (edgeThreshold, patchSize, dll)
                scoreType=cv2.ORB_HARRIS_SCORE # Coba HARRIS score untuk kualitas keypoint lebih baik
            )
        except Exception as e:
            return None, None
        # ------------------------

        # --- Deteksi dan Komputasi Fitur ---
        try:
            keypoints_base, descriptors_base = orb.detectAndCompute(base_gray_enhanced, None)
            keypoints_target, descriptors_target = orb.detectAndCompute(target_gray_enhanced, None)
        except Exception as e:
             return None, None
        # ---------------------------------

        # --- Matching: KNN + Ratio Test ---
        base_points = None
        target_points = None
        if descriptors_base is not None and descriptors_target is not None and \
           len(descriptors_base) > 0 and len(descriptors_target) > 0:
            try:
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False) # crossCheck=False untuk knnMatch
                # Pastikan k <= jumlah deskriptor target
                k_val = min(2, len(descriptors_target))

                if k_val < 2:
                     print("Warning: Less than 2 target descriptors, cannot perform KNN ratio test. Falling back to simple match.")
                     # Lakukan pencocokan tunggal jika k=1
                     matches_raw = bf.match(descriptors_base, descriptors_target)
                     # Anggap semua match ini 'good' dalam kasus ini
                     good_matches = matches_raw
                else:
                    matches_raw = bf.knnMatch(descriptors_base, descriptors_target, k=k_val)
                    good_matches = []
                    ratio_thresh = orb_config.get("ratio_threshold", 0.75)
                    for match_pair in matches_raw:
                        # Harus selalu cek len karena knnMatch bisa mengembalikan < k hasil dekat batas gambar
                        if len(match_pair) == 2:
                            m, n = match_pair
                            if m.distance < ratio_thresh * n.distance:
                                good_matches.append(m)

                
                # --- Ekstrak titik-titik yang cocok ---
                min_matches_req = orb_config.get("min_matches_for_transform", 10) # Ambil dari config
                if len(good_matches) >= min_matches_req: # Gunakan threshold dari config
                    try:
                        base_points = np.float32([keypoints_base[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                        target_points = np.float32([keypoints_target[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                    except IndexError as e:
                        # Set points ke None jika gagal
                        base_points = None
                        target_points = None
                    except Exception as e:
                        base_points = None
                        target_points = None
                else:
                    print(f"Not enough good matches found ({len(good_matches)} < {min_matches_req}).")
                    # points tetap None

            except Exception as e:
                # Pastikan points None jika error
                base_points = None
                target_points = None
        else:
            print("Not enough descriptors found in one or both images to perform matching.")
        # ----------------------------------
        # Kembalikan None, None jika points tidak berhasil diekstrak
        if base_points is None or target_points is None:
            return None, None
        else:
            return base_points, target_points

    def compensate_motion(self, base_image, base_points, target_points, config_filename=None):
        """
        Menerapkan kompensasi gerakan menggunakan transformasi (dengan USAC_MAGSAC)
        untuk menyelaraskan gambar.
        """
        # Pastikan base_points dan target_points tidak None sebelum melanjutkan
        if base_points is None or target_points is None:
             # Mungkin kembalikan base_image asli atau raise error?
             # Mengembalikan None agar pemanggil tahu proses gagal.
             return None

        config = self.load_orb_config(config_filename) # Gunakan config ORB
        keep_edges = config.get("keep_edges", False)
        transformation_type = config.get("transformation", "affine")
        ransac_threshold = config.get("ransacThreshold", 5.0)

        # --- Cek input shape ---
        if base_image is None or base_image.ndim < 2:
             print("Error: Invalid base_image for compensation.")
             return None
        h, w = base_image.shape[:2]
        if len(base_points) < 4 or len(target_points) < 4:
             print(f"Error: Not enough points for transformation ({len(base_points)} base, {len(target_points)} target). Need at least 4.")
             return None # Tidak bisa estimasi
        # -----------------------

        # --- Hitung matriks transformasi dengan USAC_MAGSAC ---
        matrix = None
        mask = None
        try:
            if transformation_type == 'affine':
                # estimateAffine2D membutuhkan format (N, 2), bukan (N, 1, 2)
                matrix, mask = cv2.estimateAffine2D(target_points.reshape(-1, 2), base_points.reshape(-1, 2),
                                                     method=cv2.USAC_MAGSAC, ransacReprojThreshold=ransac_threshold)
            elif transformation_type in ['similarity', 'euclidean']:
                # estimateAffinePartial2D juga butuh (N, 2)
                matrix, mask = cv2.estimateAffinePartial2D(target_points.reshape(-1, 2), base_points.reshape(-1, 2),
                                                             method=cv2.USAC_MAGSAC, ransacReprojThreshold=ransac_threshold)
            elif transformation_type == 'homography':
                # findHomography butuh (N, 1, 2) atau (N, 2) - otomatis handle
                matrix, mask = cv2.findHomography(target_points, base_points, cv2.USAC_MAGSAC, ransac_threshold)
            else:
                # Gunakan language_config jika tersedia
                error_msg = getattr(language_config.UNRECOGNIZED_TRANSFORMATION)
                raise ValueError(error_msg)

            if matrix is None:
                # Gunakan language_config jika tersedia
                 error_msg = getattr(language_config.FAILED_TO_COMPUTE_TRANSFORMATION)
                 print(error_msg) # Print sebagai warning/info
                 return None # Gagal jika matrix None

            # Hitung jumlah inlier (opsional, untuk logging)
            num_inliers = np.sum(mask) if mask is not None else len(base_points) # Asumsikan semua inlier jika mask None
            
        except cv2.error as cv_err: # Tangkap error spesifik OpenCV (misal tidak cukup poin)
             return None
        except Exception as e:
             return None
        # -------------------------------------------------

        # --- Hitung batas pergeseran (sama) ---
        corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(-1, 1, 2)
        try:
            if transformation_type == 'homography':
                # Cek matrix adalah 3x3
                if matrix.shape != (3, 3):
                     return None
                transformed_corners = cv2.perspectiveTransform(corners, matrix)
            else:
                 # Cek matrix adalah 2x3
                 if matrix.shape != (2, 3):
                     return None
                 transformed_corners = cv2.transform(corners, matrix)

            if transformed_corners is None: # Cek hasil transform
                 return None

            transformed_corners = transformed_corners.reshape(-1, 2)
            min_x, min_y = transformed_corners.min(axis=0)
            max_x, max_y = transformed_corners.max(axis=0)
        except Exception as e:
             return None
        # ------------------------------------

        # --- Warping ---
        try:
            # Jika keep_edges = False, langsung terapkan transformasi tanpa padding
            if not keep_edges:
                interpolation_flag = cv2.INTER_CUBIC # Pilihan Anda
                if transformation_type == 'homography':
                    compensated_image = cv2.warpPerspective(base_image, matrix, (w, h), flags=interpolation_flag, borderMode=cv2.BORDER_CONSTANT)
                else:
                    compensated_image = cv2.warpAffine(base_image, matrix, (w, h), flags=interpolation_flag, borderMode=cv2.BORDER_CONSTANT)
                return compensated_image

            # Jika keep_edges = True, tambahkan padding berdasarkan batas pergeseran
            pad_x = max(0, int(np.ceil(max_x - w)))
            pad_y = max(0, int(np.ceil(max_y - h)))
            pad_left = max(0, int(np.ceil(-min_x)))
            pad_top = max(0, int(np.ceil(-min_y)))

            # Tentukan padding maksimum untuk semua sisi agar konsisten
            pad = max(pad_x, pad_y, pad_left, pad_top)
            
            padded_image = cv2.copyMakeBorder(base_image, pad, pad, pad, pad, cv2.BORDER_REFLECT)
            
            # Gunakan interpolasi Lanczos4 untuk kualitas terbaik saat keep_edges=True
            interpolation_flag_padded = cv2.INTER_LANCZOS4 # Pilihan Anda

            target_w_padded = padded_image.shape[1]
            target_h_padded = padded_image.shape[0]

            if transformation_type == 'homography':
                compensated_padded = cv2.warpPerspective(padded_image, matrix, (target_w_padded, target_h_padded), flags=interpolation_flag_padded, borderMode=cv2.BORDER_REFLECT)
            else:
                compensated_padded = cv2.warpAffine(padded_image, matrix, (target_w_padded, target_h_padded), flags=interpolation_flag_padded, borderMode=cv2.BORDER_REFLECT)

            # Crop kembali ke ukuran asli
            # Pastikan hasil crop valid
            if pad + h > compensated_padded.shape[0] or pad + w > compensated_padded.shape[1]:
                 # Fallback: Kembalikan hasil warp tanpa padding jika crop gagal? Atau None?
                 # Coba kembalikan warp tanpa padding sebagai fallback
                 if transformation_type == 'homography':
                     compensated_image = cv2.warpPerspective(base_image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
                 else:
                     compensated_image = cv2.warpAffine(base_image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
                 return compensated_image
            else:
                 compensated_image = compensated_padded[pad:pad+h, pad:pad+w]
                 return compensated_image

        except cv2.error as cv_err:
             return None
        except Exception as e:
             return None
        # -------------
    
def main(db_path, update_progress=None, batch_size=12, stop_requested=None, single_process=None, batch_id=None,
         config_filename=None, save_align=None, align_folder=None, command_save_to_hd5f=None):
    
    # Inisialisasi processor dan konfigurasi
    processor = ORBAlgorithm(db_path)
    config = processor.load_orb_config(config_filename)
    
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
        image_paths = processor.get_all_image_paths_for_single_process()
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
            
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
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

def running_orb(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_ORB)
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