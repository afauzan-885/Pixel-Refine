import cv2
import numpy as np
import sqlite3
import os
import json
import concurrent.futures
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
from PyQt6.QtCore import Qt
import h5py
from PyQt6.QtCore import QThread, pyqtSignal

from UI.settings.General.Language import language_config

class ThreadWorker(QThread):
    progress_updated = pyqtSignal(int, str) 
    finished = pyqtSignal() 
    error_occurred = pyqtSignal(str)

    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.stop_requested = False  # Flag untuk menghentikan thread

    def run(self):
        try:
            def update_progress(current, total, message):
                progress = int((current / total) * 100)
                self.progress_updated.emit(progress, message)

            # Fungsi callback untuk mengecek status stop
            def is_stop_requested():
                return self.stop_requested

            # Jalankan proses ORB dengan callback
            main(self.db_path, update_progress, stop_requested=is_stop_requested)
            self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self.stop_requested = True
        
class AKAZEAlgorithm:
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
            if stop_requested and stop_requested():
                break
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if image is not None:
                images.append(image)
        return images

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
            "keep_edges": True
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
        
    def compensate_motion(self, base_image, base_points, target_points, transformation_type='homography', config_filename=None):
        """
        Menerapkan kompensasi gerakan menggunakan transformasi untuk menyelaraskan gambar.
        transformation_type dapat berupa 'homography', 'affine', 'similarity', atau 'euclidean'.
        """
        akaze_config = self.load_akaze_config(config_filename)
        keep_edges = akaze_config["keep_edges"]

        pad = 50 if keep_edges else 0
        padded_image = cv2.copyMakeBorder(base_image, pad, pad, pad, pad, cv2.BORDER_REFLECT) if keep_edges else base_image.copy()

        if transformation_type == 'affine':
            matrix, mask = cv2.estimateAffine2D(target_points, base_points, method=cv2.RANSAC, ransacReprojThreshold=5.0)
            compensated_padded = cv2.warpAffine(padded_image, matrix, (padded_image.shape[1], padded_image.shape[0]), borderMode=cv2.BORDER_REFLECT)
        elif transformation_type == 'similarity':
            matrix, mask = cv2.estimateAffinePartial2D(target_points, base_points, method=cv2.RANSAC, ransacReprojThreshold=5.0)
            compensated_padded = cv2.warpAffine(padded_image, matrix, (padded_image.shape[1], padded_image.shape[0]), borderMode=cv2.BORDER_REFLECT)
        elif transformation_type == 'euclidean':
            matrix, mask = cv2.estimateAffinePartial2D(target_points, base_points, method=cv2.RANSAC, ransacReprojThreshold=5.0)
            if np.linalg.norm(matrix[:2, 0]) != np.linalg.norm(matrix[:2, 1]):
                raise ValueError("Transformasi ini bukan transformasi Euclidean (terdapat skala).")
            compensated_padded = cv2.warpAffine(padded_image, matrix, (padded_image.shape[1], padded_image.shape[0]), borderMode=cv2.BORDER_REFLECT)
        elif transformation_type == 'homography':
            H, mask = cv2.findHomography(target_points, base_points, cv2.RANSAC, 5.0)
            compensated_padded = cv2.warpPerspective(padded_image, H, (padded_image.shape[1], padded_image.shape[0]), borderMode=cv2.BORDER_REFLECT)
        else:
            raise ValueError("Tipe transformasi tidak dikenali.")

        h, w = base_image.shape[:2]
        compensated_image = compensated_padded[pad:pad+h, pad:pad+w] if keep_edges else compensated_padded
        return compensated_image


def main(db_path, update_progress=None, batch_size=5, stop_requested=None):
    processor = AKAZEAlgorithm(db_path)

    # Ambil path gambar dari database
    image_paths = processor.get_all_image_paths()
    if not image_paths:
        print(language_config.RUN_IMAGE_NOT_FOUND)
        return

    # Gunakan gambar pertama sebagai referensi
    base_image_path = image_paths[0]
    base_image = cv2.imread(base_image_path, cv2.IMREAD_UNCHANGED)
    if base_image is None:
        print(language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
        return

    total_images = len(image_paths)
    total_batches = (total_images - 1) // batch_size + 1

    aligned_images = [base_image]

    with h5py.File(processor.hdf5_path, "w") as h5f:
        h5f.create_dataset("image_0", data=base_image, compression="gzip")

        for batch_idx in range(total_batches):
            if stop_requested and stop_requested():
                break

            start_idx = batch_idx * batch_size + 1
            end_idx = min((batch_idx + 1) * batch_size + 1, total_images)

            batch_paths = image_paths[start_idx:end_idx]
            batch_images = processor.load_images_from_paths(batch_paths, stop_requested)
            if not batch_images:
                continue

            batch_aligned = []
            for i, target_image in enumerate(batch_images, start=start_idx):
                if stop_requested and stop_requested():
                    print("Proses dihentikan oleh pengguna.")
                    break

                info_message = language_config.RUN_IMAGE_PROCESSING.format(i=i, total_images=total_images)
                print(info_message)

                # Gunakan versi paralel untuk menghitung global motion
                base_pts, target_pts = processor.calculate_global_motion(base_image, target_image)
                compensated_image = processor.compensate_motion(target_image, base_pts, target_pts)
                batch_aligned.append(compensated_image)

                if update_progress:
                    update_progress(i - 1, total_images - 1, info_message)

            for j, aligned_image in enumerate(batch_aligned):
                h5f.create_dataset(f"image_{start_idx + j}", data=aligned_image, compression="gzip")

            print(f"Batch {batch_idx + 1}/{total_batches} selesai diproses dan disimpan.")

    if update_progress:
        update_progress(total_images - 1, total_images - 1, language_config.SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED)

    print("Pemrosesan selesai dan semua gambar telah disimpan ke HDF5.")

def running_akaze(parent=None):
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
    worker = ThreadWorker("pixel_refine_database.db")

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
