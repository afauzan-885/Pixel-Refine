import cv2
import numpy as np
import sqlite3
import os
import json
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
            if stop_requested and stop_requested():  # Cek apakah harus berhenti
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
            "ratio_threshold": 0.75
        }

        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
                
            # Ambil parameter AKAZE jika ada, jika tidak gunakan default_config
            return params.get("AKAZE", default_config)
        except Exception as e:
            print("Error loading AKAZE configuration:", e)
            return default_config
    
    def calculate_global_motion(self, base_image, target_image, stop_requested=None):
        """
        Menghitung keypoints dan deskriptor menggunakan AKAZE antara dua gambar.
        Konfigurasi parameter dimuat dari file JSON.
        """
        if stop_requested and stop_requested():
            print("Proses dihentikan sebelum menghitung gerakan global.")
            return None, None

        # Muat konfigurasi AKAZE dari file konfigurasi
        akaze_config = self.load_akaze_config()

        # Membuat AKAZE dengan parameter dari konfigurasi
        akaze = cv2.AKAZE_create(
            threshold=akaze_config["akaze_threshold"],
            nOctaves=akaze_config["akaze_nOctaves"],
            nOctaveLayers=akaze_config["akaze_nOctaveLayers"]
        )

        keypoints_base, descriptors_base = akaze.detectAndCompute(base_image, None)
        keypoints_target, descriptors_target = akaze.detectAndCompute(target_image, None)

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        matches = bf.knnMatch(descriptors_base, descriptors_target, k=2)

        good_matches = []
        for m, n in matches:
            if m.distance < akaze_config["ratio_threshold"] * n.distance:
                good_matches.append(m)

        base_points = np.float32([keypoints_base[m.queryIdx].pt for m in good_matches])
        target_points = np.float32([keypoints_target[m.trainIdx].pt for m in good_matches])

        return base_points, target_points

    def compensate_motion(self, base_image, base_points, target_points, transformation_type='homography'):
        """
        Menerapkan kompensasi gerakan menggunakan berbagai jenis transformasi untuk menyelaraskan gambar.
        
        transformation_type:
            - 'homography'   : Menggunakan homografi (perspektif)
            - 'affine'       : Menggunakan transformasi affine
            - 'similarity'   : Menggunakan transformasi similarity
            - 'euclidean'    : Menggunakan transformasi Euclidean (rotasi dan translasi)
        """
        if transformation_type == 'affine':
            # Menghitung matriks affine menggunakan pasangan titik yang dicocokkan
            matrix, mask = cv2.estimateAffine2D(target_points, base_points, method=cv2.RANSAC, ransacReprojThreshold=5.0)
            # Menyaring pasangan titik berdasarkan mask
            valid_points = mask.ravel() == 1
            compensated_image = cv2.warpAffine(base_image, matrix, (base_image.shape[1], base_image.shape[0]))
            
        elif transformation_type == 'similarity':
            # Menghitung matriks similarity (translasi, rotasi, skala)
            matrix, mask = cv2.estimateAffinePartial2D(target_points, base_points, method=cv2.RANSAC, ransacReprojThreshold=5.0)
            # Menyaring pasangan titik berdasarkan mask
            valid_points = mask.ravel() == 1
            compensated_image = cv2.warpAffine(base_image, matrix, (base_image.shape[1], base_image.shape[0]))
            
        elif transformation_type == 'euclidean':
            # Menghitung matriks Euclidean (rotasi dan translasi)
            matrix, mask = cv2.estimateAffinePartial2D(target_points, base_points, method=cv2.RANSAC, ransacReprojThreshold=5.0)
            
            # Jika matriks memiliki skala, maka tidak sesuai dengan Euclidean
            # Matriks Euclidean hanya dapat mencakup rotasi dan translasi
            if np.linalg.norm(matrix[:2, 0]) != np.linalg.norm(matrix[:2, 1]):
                raise ValueError("Transformasi ini bukan transformasi Euclidean (terdapat skala).")
            
            # Menyaring pasangan titik berdasarkan mask
            valid_points = mask.ravel() == 1
            compensated_image = cv2.warpAffine(base_image, matrix, (base_image.shape[1], base_image.shape[0]))
            
        elif transformation_type == 'homography':
            # Menghitung matriks homografi menggunakan pasangan titik yang dicocokkan
            H, mask = cv2.findHomography(target_points, base_points, cv2.RANSAC, 5.0)
            # Menyaring pasangan titik berdasarkan mask
            valid_points = mask.ravel() == 1
            compensated_image = cv2.warpPerspective(base_image, H, (base_image.shape[1], base_image.shape[0]))

        else:
            raise ValueError("Tipe transformasi tidak dikenali. Pilih dari 'homography', 'affine', 'similarity', atau 'euclidean'.")
        
        return compensated_image

    def save_to_hdf5(self, h5f, aligned_images, update_progress=None, start_index=0):
        """
        Saves aligned images to an open HDF5 file.
        """
        total_images = len(aligned_images) + start_index
        for i, image in enumerate(aligned_images):
            # Simpan dataset ke dalam file HDF5
            h5f.create_dataset(f"image_{i + start_index}", data=image, compression="gzip")
            
            # Buat pesan progres
            progress_message = f"Gambar ke-{i + start_index + 1} disimpan dalam HDF5."
            print(progress_message)  # Log ke konsol
            
            # Perbarui progress bar jika `update_progress` tersedia
            if update_progress:
                update_progress(i + start_index, total_images - 1, progress_message)



def main(db_path, update_progress=None, batch_size=3, stop_requested=None):
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

    # Total gambar untuk keseluruhan proses
    total_images = len(image_paths)
    total_batches = (total_images - 1) // batch_size + 1  # Hitung jumlah batch

    # Simpan gambar referensi ke dalam HDF5
    aligned_images = [base_image]

    with h5py.File(processor.hdf5_path, "w") as h5f:
        h5f.create_dataset("image_0", data=base_image, compression="gzip")

        # Mulai pemrosesan batch
        for batch_idx in range(total_batches):
            if stop_requested and stop_requested():
                break

            start_idx = batch_idx * batch_size + 1
            end_idx = min((batch_idx + 1) * batch_size + 1, total_images)

            # Muat batch gambar
            batch_paths = image_paths[start_idx:end_idx]
            batch_images = processor.load_images_from_paths(batch_paths)
            if not batch_images:
                continue

            # Proses setiap gambar dalam batch
            batch_aligned = []
            for i, target_image in enumerate(batch_images, start=start_idx):
                if stop_requested and stop_requested():  # Cek penghentian
                    print("Proses dihentikan oleh pengguna.")
                    break

                info_message = language_config.RUN_IMAGE_PROCESSING.format(i=i, total_images=total_images)
                print(info_message)

                # Hitung keypoints dan kompensasi gerakan
                base_points, target_points = processor.calculate_global_motion(base_image, target_image)
                compensated_image = processor.compensate_motion(target_image, base_points, target_points)
                batch_aligned.append(compensated_image)

                # Perbarui progress bar
                if update_progress:
                    update_progress(i - 1, total_images - 1, info_message)

            # Simpan batch ke HDF5
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
