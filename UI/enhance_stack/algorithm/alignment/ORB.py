import json
import concurrent
import cv2
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import QThread, pyqtSignal, Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import compute_images_multithreaded, compute_padding, estimate_transformation, process_with_cropping, process_without_cropping, transform_corners
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.resources.stylesheet.stylesheet import PROGRESS_BAR
from UI.settings.General.Language import language_config

class ORBAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        # Pastikan folder untuk file HDF5 ada
        os.makedirs(os.path.dirname(self.hdf5_path), exist_ok=True)

    def get_all_image_paths(self):
        """Mengambil semua path gambar dari database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]

    def load_images_from_paths(self, image_paths, stop_requested=None):
        """Memuat gambar dari daftar path."""
        images = []
        for image_path in image_paths:
            if stop_requested and stop_requested():
                break
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if image is not None:
                images.append(image)
        return images

    @staticmethod
    def load_orb_config(config_filename=None):
        """Membaca konfigurasi ORB dari file JSON, atau mengembalikan default jika gagal."""
        default_config = {
            "nfeatures": 1000,
            "scaleFactor": 1.1,
            "nlevels": 5,
            "ransacThreshold": 5.0,
            "keep_edges": True,
            "enable_cropping": False  # Ubah nilainya sesuai kebutuhan
        }
        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")
        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("ORB", default_config)
        except Exception as e:
            print("Error loading ORB configuration:", e)
            return default_config

    def calculate_global_motion(self, base_image, target_image, config_filename=None, 
                              num_blocks=(3, 3), overlap=20, stop_requested=None):
        """
        Menghitung keypoints dan deskriptor menggunakan ORB dengan membagi gambar 
        menjadi blok-blok secara paralel.
        """
        if stop_requested and stop_requested():
            print("Proses dihentikan sebelum menghitung gerakan global (parallel ORB).")
            return None, None

        # Ambil konfigurasi ORB
        orb_config = self.load_orb_config(config_filename)

        # Normalisasi gambar ke 8-bit
        base_norm = cv2.normalize(base_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        target_norm = cv2.normalize(target_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

        # Jika gambar berwarna, ubah ke grayscale
        if len(base_norm.shape) == 3:
            base_gray = cv2.cvtColor(base_norm, cv2.COLOR_BGR2GRAY)
        else:
            base_gray = base_norm

        if len(target_norm.shape) == 3:
            target_gray = cv2.cvtColor(target_norm, cv2.COLOR_BGR2GRAY)
        else:
            target_gray = target_norm

        # Definisikan fungsi extractor untuk ORB menggunakan parameter dari konfigurasi
        def orb_extractor(roi):
            orb = cv2.ORB_create(
                nfeatures=orb_config["nfeatures"],
                scaleFactor=orb_config["scaleFactor"],
                nlevels=orb_config["nlevels"]
            )
            return orb.detectAndCompute(roi, None)

        # Panggil fungsi utilitas untuk ekstraksi multi-threaded
        kps_base_all, desc_base_all, kps_target_all, desc_target_all = compute_images_multithreaded(
            base_gray, target_gray, orb_extractor, num_blocks, overlap
        )

        if desc_base_all is None or desc_target_all is None:
            print("Tidak ditemukan deskriptor pada salah satu gambar.")
            return None, None

        # Pencocokan menggunakan BFMatcher dengan crossCheck (sesuai dengan algoritma ORB)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(desc_base_all, desc_target_all)
        matches = sorted(matches, key=lambda x: x.distance)

        base_points = np.float32([kps_base_all[m.queryIdx].pt for m in matches])
        target_points = np.float32([kps_target_all[m.trainIdx].pt for m in matches])

        return base_points, target_points


    def compensate_motion(self, base_image, base_points, target_points,
                          transformation_type='homography',
                          config_filename=None, transformation_matrix=None):
        """
        Apply motion compensation to align an image using the specified transformation.
        Returns the warped image and padding info (pad_top, pad_left, h, w).
        If a transformation_matrix is provided, transformation estimation is skipped.
        """
        config = self.load_orb_config(config_filename)
        keep_edges = config.get("keep_edges", True)
        h, w = base_image.shape[:2]
        corners = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32)

        # Estimate or use the provided transformation matrix.
        if transformation_matrix is None:
            transformation_matrix, transformed_corners = estimate_transformation(
                transformation_type, base_points, target_points, corners
            )
        else:
            transformed_corners = transform_corners(transformation_matrix, corners, transformation_type)

        # Compute required padding to avoid clipping.
        pad_top, pad_left, pad_bottom, pad_right = compute_padding(transformed_corners, h, w)

        # Optionally apply padding to keep image edges.
        padded_image = (cv2.copyMakeBorder(base_image, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_REFLECT)
                        if keep_edges else base_image.copy())
        new_width = w + pad_left + pad_right
        new_height = h + pad_top + pad_bottom

        # Warp the image using the appropriate method.
        if transformation_type in ['affine', 'similarity', 'euclidean']:
            warped = cv2.warpAffine(padded_image, transformation_matrix, (new_width, new_height), borderMode=cv2.BORDER_REFLECT)
        else:
            warped = cv2.warpPerspective(padded_image, transformation_matrix, (new_width, new_height), borderMode=cv2.BORDER_REFLECT)

        return warped, (pad_top, pad_left, h, w)

def main(db_path, update_progress=None, batch_size=5, stop_requested=None):
    processor = ORBAlgorithm(db_path)
    transformation_dir = os.path.join("database", "align", "transformation")
    os.makedirs(transformation_dir, exist_ok=True)

    image_paths = processor.get_all_image_paths()
    if not image_paths:
        print("Gambar tidak ditemukan.")
        return

    # Load dan validasi base image
    base_image_path = image_paths[0]
    base_image = cv2.imread(base_image_path, cv2.IMREAD_UNCHANGED)
    if base_image is None:
        print("Gagal memuat base image.")
        return

    h, w = base_image.shape[:2]
    remaining_paths = image_paths[1:]
    total_images = len(image_paths)
    batch_count = (len(remaining_paths) - 1) // batch_size + 1

    # Ambil konfigurasi dan ambil nilai enable_cropping dari konfigurasi
    config = processor.load_orb_config()
    enable_cropping = config.get("enable_cropping", False)

    if enable_cropping:
        process_with_cropping(
            processor, base_image, remaining_paths, batch_count, batch_size,
            h, w, transformation_dir, update_progress, total_images, stop_requested
        )
    else:
        process_without_cropping(
            processor, base_image, remaining_paths, batch_count, batch_size,
            transformation_dir, update_progress, total_images, stop_requested
        )

        
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
    progress_bar.setStyleSheet(PROGRESS_BAR)
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