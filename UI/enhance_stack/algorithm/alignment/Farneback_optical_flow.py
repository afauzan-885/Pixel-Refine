import json
import cv2
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py

from PyQt6.QtCore import QThread, pyqtSignal, Qt

from UI.settings.General.Language import language_config

class ThreadWorker(QThread):
    progress_updated = pyqtSignal(int, str)  # Sinyal untuk memperbarui progress
    finished = pyqtSignal()  # Sinyal untuk menandakan selesai
    error_occurred = pyqtSignal(str)  # Sinyal untuk menandakan error

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
        self.stop_requested = True  # Set flag agar thread berhenti

class FarnebackAlgorithm:
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

    def resize_image(self, image, size):
        """
        Resizes the image to match the reference image size.
        """
        return cv2.resize(image, (size[1], size[0]), interpolation=cv2.INTER_LINEAR)

    @staticmethod
    def load_farneback_config(config_filename=None):
        """
        Membaca konfigurasi Farneback Optical Flow dari file JSON.
        Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "pyr_scale": 0.5,
            "levels": 3,
            "winsize": 15,
            "iterations": 3,
            "poly_n": 5,
            "poly_sigma": 1.2,
            "flags": 0,
            "interpolation": "INTER_CUBIC"
        }

        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("Farneback", default_config)
        except Exception as e:
            print("Error loading Farneback configuration:", e)
            return default_config


    def calculate_optical_flow(self, base_image, target_image, config_filename=None):
        device = " GPU" if self.use_gpu else " CPU"
        print(language_config.CALCULATE_OPTICAL_FLOW_STATUS.format(device=device))

        if self.use_gpu:
            base_gray = cv2.UMat(cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY))
            target_gray = cv2.UMat(cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY))
        else:
            base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
            target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

        # Muat parameter Farneback Optical Flow dari file konfigurasi
        fb_config = self.load_farneback_config(config_filename)

        flow = cv2.calcOpticalFlowFarneback(
            base_gray, 
            target_gray, 
            None,
            pyr_scale=fb_config["pyr_scale"],
            levels=fb_config["levels"],
            winsize=fb_config["winsize"],
            iterations=fb_config["iterations"],
            poly_n=fb_config["poly_n"],
            poly_sigma=fb_config["poly_sigma"],
            flags=fb_config["flags"]
        )

        print(language_config.CALCULATE_OPTICAL_FLOW_FINISHED)
        return flow.get() if self.use_gpu else flow


    def compensate_motion(self, base_image_16bit, flow, image_id, config_filename=None):
        print(language_config.COMPENSATE_MOTION_STATUS.format(image_id=image_id))
        h, w = base_image_16bit.shape[:2]
        flow_map = np.stack(np.meshgrid(np.arange(w), np.arange(h)), axis=-1)
        warped_map = flow_map + flow
        remap_x, remap_y = cv2.split(warped_map.astype(np.float32))

        if self.use_gpu:
            base_image_16bit = cv2.UMat(base_image_16bit)
            remap_x = cv2.UMat(remap_x)
            remap_y = cv2.UMat(remap_y)

        # Muat konfigurasi Farneback untuk mendapatkan parameter interpolasi
        fb_config = self.load_farneback_config(config_filename)
        # Konversi nilai string interpolasi ke flag OpenCV (misalnya, "INTER_AREA")
        interpolation_str = fb_config.get("interpolation", "INTER_AREA")
        interp_flag = getattr(cv2, interpolation_str, cv2.INTER_AREA)

        compensated_image = cv2.remap(
            base_image_16bit, 
            remap_x, 
            remap_y, 
            interpolation=interp_flag, 
            borderMode=cv2.BORDER_REFLECT
        )

        if self.use_gpu:
            compensated_image = compensated_image.get()

        print(language_config.COMPENSATE_MOTION_FINISHED.format(image_id=image_id))
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
    processor = FarnebackAlgorithm(db_path)

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

                # Hitung flow gerakan dan kompensasi gerakan
                flow = processor.calculate_optical_flow(base_image, target_image)
                compensated_image = processor.compensate_motion(target_image, flow)

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


def running_farneback_optical_flow(parent=None):
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_FARNEBACK)
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
