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
        
class EECAlgorithm:
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
    def load_eec_config(config_filename=None):
        """
        Membaca konfigurasi EEC (berbasis ECC) dari file JSON.
        Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "number_of_iterations": 5000,
            "termination_eps": 1e-6,
            "motion_type": "affine"  # Pilihan: "affine", "homography", atau "translation"
        }

        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("EEC", default_config)
        except Exception as e:
            print("Error loading EEC configuration:", e)
            return default_config

    def calculate_global_motion(self, base_image, target_image, config_filename=None, num_blocks=(3, 3), overlap=20, stop_requested=None):
        """
        Menghitung transformasi global dengan metode ECC secara paralel.
        """
        if stop_requested and stop_requested():
            print("Proses dihentikan sebelum menghitung gerakan global (parallel).")
            return None

        # Ambil konfigurasi EEC dari file atau gunakan default
        eec_config = self.load_eec_config(config_filename)

        # Mapping dari string ke motionType OpenCV
        motion_type_mapping = {
            "affine": cv2.MOTION_AFFINE,
            "homography": cv2.MOTION_HOMOGRAPHY,
            "translation": cv2.MOTION_TRANSLATION
        }
        motionType = motion_type_mapping.get(eec_config["motion_type"], cv2.MOTION_AFFINE)

        # Konversi gambar ke grayscale
        base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
        target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

        # Konversi grayscale ke 8-bit
        base_gray_8bit = cv2.normalize(base_gray, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        target_gray_8bit = cv2.normalize(target_gray, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

        h, w = base_gray_8bit.shape
        blocks_x, blocks_y = num_blocks
        block_w, block_h = w // blocks_x, h // blocks_y

        warp_matrices = []

        def compute_ecc_block(x, y, bw, bh, overlap):
            roi_x_start, roi_y_start = max(0, x - overlap), max(0, y - overlap)
            roi_x_end, roi_y_end = min(w, x + bw + overlap), min(h, y + bh + overlap)

            roi_base = base_gray_8bit[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
            roi_target = target_gray_8bit[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

            warp_matrix = np.eye(3, 3, dtype=np.float32) if motionType == cv2.MOTION_HOMOGRAPHY else np.eye(2, 3, dtype=np.float32)

            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                        eec_config["number_of_iterations"],
                        eec_config["termination_eps"])
            try:
                _, warp_matrix = cv2.findTransformECC(roi_base, roi_target, warp_matrix, motionType, criteria)
            except cv2.error as e:
                print("findTransformECC error:", e)
                warp_matrix = np.eye(3, 3, dtype=np.float32) if motionType == cv2.MOTION_HOMOGRAPHY else np.eye(2, 3, dtype=np.float32)

            return warp_matrix

        with concurrent.futures.ThreadPoolExecutor(max_workers=blocks_x * blocks_y) as executor:
            futures = [executor.submit(compute_ecc_block, i * block_w, j * block_h, block_w if i < blocks_x - 1 else w - i * block_w, block_h if j < blocks_y - 1 else h - j * block_h, overlap) for i in range(blocks_x) for j in range(blocks_y)]
            for future in concurrent.futures.as_completed(futures):
                warp_matrices.append(future.result())

        # Hitung rata-rata warp matrix dari semua blok
        global_warp = np.mean(warp_matrices, axis=0)

        print(language_config.CALCULATE_OPTICAL_FLOW_FINISHED + " (EEC parallel)")
        return global_warp

    def compensate_motion(self, base_image, warp_matrix, config_filename=None):
        """
        Menerapkan kompensasi gerakan menggunakan warp matrix untuk menyelaraskan gambar.
        """
        eec_config = self.load_eec_config(config_filename)

        # Mapping motion_type langsung
        motion_type_mapping = {
            "affine": cv2.warpAffine,
            "euclidean": cv2.warpAffine,
            "translation": cv2.warpAffine,
            "homography": cv2.warpPerspective
        }
        warp_function = motion_type_mapping.get(eec_config["motion_type"])

        if warp_function == cv2.warpAffine:
            compensated_image = warp_function(base_image, warp_matrix, (base_image.shape[1], base_image.shape[0]))
        elif warp_function == cv2.warpPerspective:
            compensated_image = warp_function(base_image, warp_matrix, (base_image.shape[1], base_image.shape[0]))
        else:
            raise ValueError("Tipe transformasi tidak dikenali.")

        return compensated_image

    def save_to_hdf5(self, h5f, aligned_images, update_progress=None, start_index=0):
        """
        Menyimpan gambar yang telah disejajarkan ke dalam file HDF5.
        """
        total_images = len(aligned_images) + start_index
        for i, image in enumerate(aligned_images):
            h5f.create_dataset(f"image_{i + start_index}", data=image, compression="gzip")
            progress_message = f"Gambar ke-{i + start_index + 1} disimpan dalam HDF5."
            print(progress_message)
            if update_progress:
                update_progress(i + start_index, total_images - 1, progress_message)


def main(db_path, update_progress=None, batch_size=5, stop_requested=None):
    processor = EECAlgorithm(db_path)

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

                # Hitung transformasi global menggunakan EEC secara paralel
                warp_matrix = processor.calculate_global_motion(base_image, target_image)
                # Gunakan jenis transformasi yang sama dengan yang didefinisikan di konfigurasi EEC
                compensated_image = processor.compensate_motion(target_image, warp_matrix)
                batch_aligned.append(compensated_image)

                if update_progress:
                    update_progress(i - 1, total_images - 1, info_message)

            for j, aligned_image in enumerate(batch_aligned):
                h5f.create_dataset(f"image_{start_idx + j}", data=aligned_image, compression="gzip")

            print(f"Batch {batch_idx + 1}/{total_batches} selesai diproses dan disimpan.")

    if update_progress:
        update_progress(total_images - 1, total_images - 1, language_config.SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED)

    print("Pemrosesan selesai dan semua gambar telah disimpan ke HDF5.")


def running_eec(parent=None):
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_EEC)
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
