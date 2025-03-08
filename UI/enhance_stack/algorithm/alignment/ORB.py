from concurrent.futures import ThreadPoolExecutor
import json
import cv2
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import compute_global_crop, crop_image, save_to_hdf5
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

    def get_all_image_paths(self):
        """
        Retrieves all image paths stored in the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]

    def load_images_from_paths(self, image_paths, stop_requested=None):
        """
        Loads images from a list of image paths.
        """
        images = []
        for image_path in image_paths:
            if stop_requested and stop_requested():  # Cek apakah harus berhenti
                break
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if image is not None:
                images.append(image)
        return images

    @staticmethod
    def load_orb_config(config_filename=None):
        """
        Membaca konfigurasi ORB dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "nfeatures": 1000,
            "scaleFactor": 1.1,
            "nlevels": 5,
            "ransacThreshold": 5.0,
            "transformation": "affine",
            "keep_edges": False,
            "enable_cropping": True
        }

        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("ORB", default_config)
        except Exception as e:
            print("Error loading ORB configuration:", e)
            return default_config  # Gunakan default jika file tidak ditemukan atau ada error


    def calculate_global_motion(self, base_image, target_image, stop_requested=None):
        """
        Menghitung keypoints dan deskriptor menggunakan ORB antara dua gambar.
        """
        if stop_requested and stop_requested():
            return None, None

        # Baca konfigurasi ORB
        orb_config = self.load_orb_config()

        # Konversi gambar 16-bit ke 8-bit
        base_image_8bit = cv2.normalize(base_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        target_image_8bit = cv2.normalize(target_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

        # Inisialisasi ORB dengan parameter dari konfigurasi
        orb = cv2.ORB_create(
            nfeatures=orb_config["nfeatures"],
            scaleFactor=orb_config["scaleFactor"],
            nlevels=orb_config["nlevels"]
        )

        keypoints_base, descriptors_base = orb.detectAndCompute(base_image_8bit, None)
        keypoints_target, descriptors_target = orb.detectAndCompute(target_image_8bit, None)

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(descriptors_base, descriptors_target)
        matches = sorted(matches, key=lambda x: x.distance)
        base_points = np.float32([keypoints_base[m.queryIdx].pt for m in matches])
        target_points = np.float32([keypoints_target[m.trainIdx].pt for m in matches])

        return base_points, target_points

    def compensate_motion(self, base_image, base_points, target_points, config_filename=None):
        """
        Menerapkan kompensasi gerakan menggunakan transformasi untuk menyelaraskan gambar.
        """
        config = self.load_orb_config(config_filename)
        keep_edges = config["keep_edges"]
        transformation_type = config["transformation"]
        ransac_threshold = config["ransacThreshold"]

        h, w = base_image.shape[:2]

        # Hitung matriks transformasi
        if transformation_type == 'affine':
            matrix, mask = cv2.estimateAffine2D(target_points, base_points, method=cv2.RANSAC, ransacReprojThreshold=ransac_threshold)
        elif transformation_type in ['similarity', 'euclidean']:
            matrix, mask = cv2.estimateAffinePartial2D(target_points, base_points, method=cv2.RANSAC, ransacReprojThreshold=ransac_threshold)
        elif transformation_type == 'homography':
            matrix, mask = cv2.findHomography(target_points, base_points, cv2.RANSAC, ransac_threshold)
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
                compensated_image = cv2.warpPerspective(base_image, matrix, (w, h), borderMode=cv2.BORDER_CONSTANT)
            else:
                compensated_image = cv2.warpAffine(base_image, matrix, (w, h), borderMode=cv2.BORDER_CONSTANT)
            return compensated_image

        # Jika keep_edges = True, tambahkan padding berdasarkan batas pergeseran
        pad_x = max(0, int(np.ceil(max_x - w)))
        pad_y = max(0, int(np.ceil(max_y - h)))
        pad_left = max(0, int(np.ceil(-min_x))) 
        pad_top = max(0, int(np.ceil(-min_y)))  

        pad = max(pad_x, pad_y, pad_left, pad_top)

        padded_image = cv2.copyMakeBorder(base_image, pad, pad, pad, pad, cv2.BORDER_REFLECT)

        if transformation_type == 'homography':
            compensated_padded = cv2.warpPerspective(padded_image, matrix, (padded_image.shape[1], padded_image.shape[0]), borderMode=cv2.BORDER_REFLECT)
        else:
            compensated_padded = cv2.warpAffine(padded_image, matrix, (padded_image.shape[1], padded_image.shape[0]), borderMode=cv2.BORDER_REFLECT)

        compensated_image = compensated_padded[pad:pad+h, pad:pad+w] if keep_edges else compensated_padded

        return compensated_image

def main(db_path, update_progress=None, batch_size=12, stop_requested=None, config_filename=None):
    # Buat objek processor dan baca konfigurasi ORB
    processor = ORBAlgorithm(db_path)
    config = processor.load_orb_config(config_filename)
    enable_cropping = config.get("enable_cropping", True)
    transformation_type = config.get("transformation", "affine")
    
    image_paths = processor.get_all_image_paths()
    if not image_paths:
        print(language_config.RUN_IMAGE_NOT_FOUND)
        return
    
    base_image_path = image_paths[0]
    base_image = cv2.imread(base_image_path, cv2.IMREAD_UNCHANGED)
    if base_image is None:
        print(language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
        return
    
    total_images = len(image_paths)
    total_batches = (total_images - 1) // batch_size + 1

    # Total progress mencakup phase 1 (estimasi transformasi) dan phase 2 (aplikasi transformasi & penyimpanan)
    total_steps = total_images * 2
    current_step = 0
    
    transform_folder = os.path.join("database", "align", "transformasi")
    os.makedirs(transform_folder, exist_ok=True)
    
    # -----------------------
    # Phase 1: Estimasi transformasi dan simpan ke disk
    # -----------------------
    for batch_idx in range(total_batches):
        if stop_requested and stop_requested():
            break
        
        start_idx = batch_idx * batch_size + 1
        end_idx = min((batch_idx + 1) * batch_size + 1, total_images)
        batch_paths = image_paths[start_idx:end_idx]
        batch_images = processor.load_images_from_paths(batch_paths)
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
                # Tetap naikkan progress walaupun transformasi gagal
                current_step += 1
                if update_progress:
                    update_progress(current_step, total_steps, language_config.FAIL_COMPENSATE_MOTION_PROCESS.format(i))
                continue
            
            transform_file_path = os.path.join(transform_folder, f"transform_{i}.npy")
            np.save(transform_file_path, (base_points, target_points))
            
            current_step += 1
            if update_progress:
                update_progress(current_step, total_steps, info_message)
    
    # -----------------------
    # Hitung crop bounds jika diaktifkan
    crop_bounds = None
    if enable_cropping:
        h, w = base_image.shape[:2]
        # Misalnya, fungsi compute_global_crop() mengembalikan (crop_x, crop_y, crop_w, crop_h)
        crop_bounds = compute_global_crop(transform_folder, total_images, w, h, transformation_type=transformation_type)
        if crop_bounds is None:
            print(language_config.FAILED_TO_COMPUTE_CROP)
            return
        np.save(os.path.join(transform_folder, "crop.npy"), crop_bounds)
        # print(f"Crop bounds dihitung: {crop_bounds}")
    
    # -----------------------
    # Phase 2: Terapkan transformasi dan simpan ke HDF5
    # -----------------------
    with h5py.File(processor.hdf5_path, "w") as h5f:
        # Terapkan cropping pada gambar referensi jika diaktifkan
        if enable_cropping:
            base_image = crop_image(base_image, crop_bounds)
        h5f.create_dataset("image_0", data=base_image)
        
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            for batch_idx in range(total_batches):
                if stop_requested and stop_requested():
                    break
                
                start_idx = batch_idx * batch_size + 1
                end_idx = min((batch_idx + 1) * batch_size + 1, total_images)
                batch_paths = image_paths[start_idx:end_idx]
                batch_images = processor.load_images_from_paths(batch_paths)
                if not batch_images:
                    continue
                
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
                    
                    dataset_name = f"image_{i}"
                    futures.append(executor.submit(save_to_hdf5, h5f, dataset_name, compensated_image))
                    
                    current_step += 1
                    if update_progress:
                        update_progress(current_step, total_steps, language_config.PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION.format(i, total_images))
            
            for future in futures:
                future.result()
    
    # if update_progress:
    #     update_progress(total_steps, total_steps, "Penyimpanan gambar yang telah di-align selesai.")
    # print("Tahap 2 selesai: Semua gambar telah disimpan ke HDF5.")

def running_orb(parent=None):
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
    worker = ImageProcessingMultiThreading(main, "pixel_refine_database.db")
    # Menghubungkan signal worker ke fungsi pembaruan UI
    worker.progress_updated.connect(lambda progress, message: (
        progress_bar.setValue(progress),
        label.setText(message)
    ))

    def finish_handler():
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

    # Mulai worker
    worker.start()

    # Pastikan worker dihentikan jika dialog ditutup
    def on_dialog_close(event):
        if worker.isRunning():
            # Menampilkan konfirmasi sebelum menutup dialog
            reply = QMessageBox.question(dialog, "Cancel Process",
                                        
                                        # message: Are you sure you want to cancel the process?
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

    dialog.closeEvent = on_dialog_close

    dialog.exec()

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"  # Path ke database Anda
    main(db_path)