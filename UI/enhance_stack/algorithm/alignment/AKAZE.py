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

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import compute_global_crop, crop_image, extract_all_metadata, extract_exif, load_images_from_paths, save_align_to_folder, save_to_hdf5
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config

class AKAZEAlgorithm:
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
            return {**default_config, **params.get("AKAZE", {})}
        except Exception as e:
            print("Error loading AKAZE configuration:", e)
            return default_config
        
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
            return {**default_config, **params.get("AKAZE_BATCH", {})}
        except Exception as e:
            print("Error loading AKAZE configuration:", e)
            return default_config

    def calculate_global_motion(self, base_image, target_image, config_filename=None, num_blocks=(3, 3), overlap=20, stop_requested=None):
        """
        Menghitung keypoints dan deskriptor menggunakan AKAZE dengan membagi gambar menjadi blok-blok secara paralel.
        
        Parameter:
          - num_blocks: tuple (blocks_x, blocks_y) untuk pembagian gambar.
          - overlap: jumlah piksel overlap di sekeliling tiap blok.
        """
        if stop_requested and stop_requested():
            print("Proses dihentikan sebelum menghitung gerakan global (parallel).")
            return None, None

        akaze_config = self.load_akaze_config(config_filename)
        # Konversi gambar ke grayscale
        base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
        target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

        h, w = base_gray.shape
        blocks_x, blocks_y = num_blocks
        block_w = w // blocks_x
        block_h = h // blocks_y

        # Himpunan untuk menggabungkan hasil dari tiap blok
        keypoints_base_all = []
        descriptors_base_all = None  # akan berupa numpy array
        keypoints_target_all = []
        descriptors_target_all = None

        def compute_features_block(x, y, bw, bh, overlap):
            # Tentukan ROI dengan tambahan overlap
            roi_x_start = max(0, x - overlap)
            roi_y_start = max(0, y - overlap)
            roi_x_end = min(w, x + bw + overlap)
            roi_y_end = min(h, y + bh + overlap)

            roi_base = base_gray[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
            roi_target = target_gray[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

            # Buat instance AKAZE untuk blok ini
            akaze = cv2.AKAZE_create(
                threshold=akaze_config["akaze_threshold"],
                nOctaves=akaze_config["akaze_nOctaves"],
                nOctaveLayers=akaze_config["akaze_nOctaveLayers"]
            )
            kps_base, desc_base = akaze.detectAndCompute(roi_base, None)
            kps_target, desc_target = akaze.detectAndCompute(roi_target, None)

            # Sesuaikan koordinat keypoints agar sesuai dengan posisi asli pada gambar penuh
            for kp in kps_base:
                kp.pt = (kp.pt[0] + roi_x_start, kp.pt[1] + roi_y_start)
            for kp in kps_target:
                kp.pt = (kp.pt[0] + roi_x_start, kp.pt[1] + roi_y_start)
            return kps_base, desc_base, kps_target, desc_target

        with concurrent.futures.ThreadPoolExecutor(max_workers=blocks_x * blocks_y) as executor:
            futures = []
            for i in range(blocks_x):
                for j in range(blocks_y):
                    x = i * block_w
                    y = j * block_h
                    bw = block_w if i < blocks_x - 1 else w - x
                    bh = block_h if j < blocks_y - 1 else h - y
                    futures.append(executor.submit(compute_features_block, x, y, bw, bh, overlap))
            for future in concurrent.futures.as_completed(futures):
                kps_base, desc_base, kps_target, desc_target = future.result()
                if desc_base is not None and len(kps_base) > 0:
                    keypoints_base_all.extend(kps_base)
                    if descriptors_base_all is None:
                        descriptors_base_all = desc_base
                    else:
                        descriptors_base_all = np.vstack([descriptors_base_all, desc_base])
                if desc_target is not None and len(kps_target) > 0:
                    keypoints_target_all.extend(kps_target)
                    if descriptors_target_all is None:
                        descriptors_target_all = desc_target
                    else:
                        descriptors_target_all = np.vstack([descriptors_target_all, desc_target])

        # Lakukan matching menggunakan BFMatcher pada hasil gabungan dari semua blok
        if descriptors_base_all is None or descriptors_target_all is None:
            print("Tidak ditemukan deskriptor pada salah satu gambar.")
            return None, None

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        matches = bf.knnMatch(descriptors_base_all, descriptors_target_all, k=2)
        good_matches = []
        for m, n in matches:
            if m.distance < akaze_config["ratio_threshold"] * n.distance:
                good_matches.append(m)

        base_points = np.float32([keypoints_base_all[m.queryIdx].pt for m in good_matches])
        target_points = np.float32([keypoints_target_all[m.trainIdx].pt for m in good_matches])

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
        image_paths = processor.get_all_image_paths_for_single_process()
    else:
        if batch_id is None:
            raise ValueError("batch_id harus diberikan untuk batch process")
        image_paths = processor.get_all_image_paths_for_batch_process(batch_id)
    
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