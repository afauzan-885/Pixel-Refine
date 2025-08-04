from concurrent.futures import ThreadPoolExecutor, as_completed
import gc
import json
import queue
import threading
import cv2
import numpy as np
import sqlite3
import os
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PySide6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import (calculate_crop_parameters, do_warp_and_crop, extract_all_metadata, filter_keypoints_spatially,
                                                                                    get_all_image_paths_for_single_process, load_images_from_paths, prepare_image,
                                                                                    resize_all_with_padding, run_pipeline_global_crop, run_pipeline_non_crop, save_align_to_folder)
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

    def calculate_global_motion(self, base_image, target_image, config_filename=None, 
                                stop_requested=None, calib_filename=None):
        """
        Menghitung keypoints ORB pada gambar global, menyaringnya secara spasial
        berdasarkan kualitas, lalu melakukan matching. Mendukung eksekusi multi-core.
        """
        # --- Tahap 1: Pre-processing ---
        if calib_filename:
            try:
                fs = cv2.FileStorage(calib_filename, cv2.FILE_STORAGE_READ)
                mtx = fs.getNode("camera_matrix").mat()
                dist = fs.getNode("dist_coeff").mat()
                fs.release()
                base_image = cv2.undistort(base_image, mtx, dist, None, mtx)
                target_image = cv2.undistort(target_image, mtx, dist, None, mtx)
            except Exception:
                pass

        orb_config = self.load_orb_config(config_filename)
        use_multicore = orb_config.get("use_multi_core", True)
        
        if stop_requested and stop_requested():
            return None, None
        
        try:
            base_gray_enhanced = prepare_image(base_image, grayscale=True, use_clahe=True)
            target_gray_enhanced = prepare_image(target_image, grayscale=True, use_clahe=True)
            
            if base_gray_enhanced is None or target_gray_enhanced is None:
                return None, None

        except Exception:
            return None, None

        # --- Tahap 4: Deteksi Fitur Global ---
        try:
            orb = cv2.ORB_create(
                nfeatures=int(orb_config.get("nfeatures", 10000)), 
                scaleFactor=float(orb_config.get("scaleFactor", 1.2)),
                nlevels=int(orb_config.get("nlevels", 8)),
                scoreType=cv2.ORB_HARRIS_SCORE
            )
        except Exception:
            return None, None

        try:
            if use_multicore:
                def detect_task(image): return orb.detectAndCompute(image, None)
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future_base = executor.submit(detect_task, base_gray_enhanced)
                    future_target = executor.submit(detect_task, target_gray_enhanced)
                    keypoints_base_raw, descriptors_base_raw = future_base.result()
                    keypoints_target_raw, descriptors_target_raw = future_target.result()
            else:
                keypoints_base_raw, descriptors_base_raw = orb.detectAndCompute(base_gray_enhanced, None)
                keypoints_target_raw, descriptors_target_raw = orb.detectAndCompute(target_gray_enhanced, None)
        except Exception:
            return None, None

        # --- Tahap 5: Filtrasi Spasial untuk Keypoint Terbaik & Terdistribusi ---
        try:
            keypoints_base, descriptors_base = filter_keypoints_spatially(
                keypoints_base_raw, descriptors_base_raw, base_gray_enhanced.shape,
                grid_size=tuple(orb_config.get("spatial_grid_size", (4, 4))),
                max_kps_per_cell=int(orb_config.get("max_kps_per_cell", 50))
            )
            keypoints_target, descriptors_target = filter_keypoints_spatially(
                keypoints_target_raw, descriptors_target_raw, target_gray_enhanced.shape,
                grid_size=tuple(orb_config.get("spatial_grid_size", (4, 4))),
                max_kps_per_cell=int(orb_config.get("max_kps_per_cell", 50))
            )
        except Exception:
            return None, None

        # --- Tahap 6: Matching Fitur pada Keypoint Berkualitas Tinggi ---
        if descriptors_base is None or descriptors_target is None or len(descriptors_base) < 2 or len(descriptors_target) < 2:
            return None, None

        try:
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            matches_raw = bf.knnMatch(descriptors_base, descriptors_target, k=2)

            good_matches = []
            ratio_thresh = float(orb_config.get("ratio_threshold", 0.75))
            for match_pair in matches_raw:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < ratio_thresh * n.distance:
                        good_matches.append(m)
            
            min_matches_req = int(orb_config.get("min_matches_for_transform", 10))
            if len(good_matches) < min_matches_req:
                return None, None
                
            good_matches.sort(key=lambda m: m.distance)
            
            base_points = np.float32([keypoints_base[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            target_points = np.float32([keypoints_target[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        except Exception:
            return None, None

        return base_points, target_points
    
    def compensate_motion(self, base_image, base_points, target_points, config_filename=None):
        """
        Menerapkan kompensasi gerakan menggunakan transformasi (dengan USAC_MAGSAC)
        untuk menyelaraskan gambar.
        """
        if base_points is None or target_points is None or base_image is None or base_image.ndim < 2:
             return None

        config = self.load_orb_config(config_filename)
        keep_edges = config.get("keep_edges", False)
        transformation_type = config.get("transformation", "affine")
        ransac_threshold = config.get("ransacThreshold", 5.0)

        h, w = base_image.shape[:2]
        if len(base_points) < 4 or len(target_points) < 4:
             return None
         
        # --- 1. Hitung Matriks Transformasi ---
        matrix = None
        try:
            if transformation_type == 'affine':
                matrix, mask = cv2.estimateAffine2D(target_points.reshape(-1, 2), base_points.reshape(-1, 2),
                                                     method=cv2.USAC_MAGSAC, ransacReprojThreshold=ransac_threshold)
            elif transformation_type == 'homography':
                matrix, mask = cv2.findHomography(target_points, base_points, cv2.USAC_MAGSAC, ransac_threshold)
            else:
                raise ValueError( getattr(language_config.UNRECOGNIZED_TRANSFORMATION))
                
            if matrix is None:
                 print(language_config.FAILED_TO_COMPUTE_TRANSFORMATION)
                 return None
            
        except (cv2.error, Exception) as e:
             return None
        
        # --- 2. Lakukan Warping pada Gambar ---
        try:
            if not keep_edges:
                interpolation_flag = cv2.INTER_CUBIC
                if transformation_type == 'homography':
                    return cv2.warpPerspective(base_image, matrix, (w, h), flags=interpolation_flag, borderMode=cv2.BORDER_CONSTANT)
                else:
                    return cv2.warpAffine(base_image, matrix, (w, h), flags=interpolation_flag, borderMode=cv2.BORDER_CONSTANT)
            else:
                pad = calculate_crop_parameters(matrix, w, h, transformation_type)
                
                if pad is None:
                    return cv2.warpAffine(base_image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
                
                return do_warp_and_crop(base_image, matrix, pad, w, h, transformation_type)

        except (cv2.error, Exception) as e:
            return None 

def main(db_path,
         update_progress=None,
         stop_requested=None,
         single_process=None,
         batch_id=None,
         config_filename=None,
         save_align=None,
         align_folder=None,
         command_save_to_hd5f=None):
    
    processor = ORBAlgorithm(db_path)
    config = processor.load_orb_config(config_filename)
    
    save_align = save_align if save_align is not None else config.get("save_align", False)
    command_save_to_hd5f = command_save_to_hd5f if command_save_to_hd5f is not None else config.get("command_save_to_hd5f", True)
    align_folder = align_folder if align_folder is not None else config.get(
        "align_folder",
        os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image")
    )
    enable_cropping = config.get("enable_cropping", False)
    keep_edges = config.get("keep_edges", False)
    transformation_type = config.get("transformation", "affine")
    
    if single_process:
        image_paths = get_all_image_paths_for_single_process(db_path)
        processor.hdf5_path = "database/align/aligned_images.h5"
    else:
        if batch_id is None:
            raise ValueError("Batch ID harus ada saat proses batch")
        image_paths = processor.get_all_image_paths_for_batch_process(batch_id)
        processor.hdf5_path = f"database/align/aligned_image_batch_{batch_id}.h5"

    if not image_paths:
        if update_progress:
            update_progress(0, "Failed to load image")
        return

    os.makedirs(os.path.dirname(processor.hdf5_path), exist_ok=True)
    if align_folder:
        os.makedirs(align_folder, exist_ok=True)
    extract_all_metadata(image_paths, metadata_file=os.path.join("database", "align", "metadata.json"))

    # --- 3. Pemuatan dan Penyiapan Base Image ---
    total_images = len(image_paths)
    base_img_list = load_images_from_paths([image_paths[0]], stop_requested=stop_requested)
    if not base_img_list or base_img_list[0] is None:
        raise RuntimeError("Base image failed to load.")

    base_image_raw = base_img_list[0]
    # Dapatkan dimensi target dari gambar dasar sebelum diubah
    base_resized_list, (target_h, target_w) = resize_all_with_padding([base_image_raw], method="median")
    base_image = base_resized_list[0]

    del base_image_raw, base_resized_list, base_img_list
    gc.collect()

    # Buat file HDF5 dan simpan gambar dasar pertama
    with h5py.File(processor.hdf5_path, "w") as h5f:
        if command_save_to_hd5f:
            h5f.create_dataset("image_0", data=base_image)
        if save_align:
            save_align_to_folder(base_image, 0, image_paths[0], align_folder)

    # --- 4. Delegasi ke Pipeline yang Sesuai ---
    if not enable_cropping or keep_edges:
        run_pipeline_non_crop(
            processor=processor,
            image_paths=image_paths[1:],
            base_image=base_image,
            target_dims=(target_h, target_w),
            update_progress=update_progress,
            stop_requested=stop_requested,
            save_align=save_align,
            align_folder=align_folder,
            command_save_to_hd5f=command_save_to_hd5f
        )
    else:
        run_pipeline_global_crop(
            processor=processor,
            image_paths=image_paths[1:],
            base_image=base_image,
            target_dims=(target_h, target_w),
            update_progress=update_progress,
            stop_requested=stop_requested,
            transformation_type=transformation_type,
            save_align=save_align,
            align_folder=align_folder,
            command_save_to_hd5f=command_save_to_hd5f
        )  
             
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