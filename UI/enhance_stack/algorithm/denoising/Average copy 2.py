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



class AverageAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        # Pastikan folder HDF5 ada
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

    def get_all_image_paths(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]

    def load_images_from_hdf5(self, hdf5_path, stop_requested=None):
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                if stop_requested and stop_requested():  # Cek apakah harus berhenti
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images

    def load_images_from_folder(self, folder_path):
        image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        return self.load_images_from_paths(image_paths)

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

    def stack_average_images(self, images, update_progress=None, stop_requested=None):
        if stop_requested and stop_requested():  # Cek penghentian
            print("Proses dihentikan sebelum menghitung gerakan global.")
            return None, None
        
        if len(images) == 0:
            raise ValueError(language_config.RUN_IMAGE_NOT_FOUND)

        dtype = images[0].dtype
        stacked_image = np.zeros_like(images[0], dtype=np.float32)

        for i, image in enumerate(images):
            if image is None:
                continue

            current_image = image.astype(np.float32)
            stacked_image += current_image

            progress = int((i + 1) / len(images) * 100)
            message = language_config.STACK_AVERAGE_IMAGES_PROCESS.format(current=i + 1, total=len(images))
            
            if update_progress:
                update_progress(progress, message)

        stacked_image /= len(images)
        stacked_image = np.clip(stacked_image, np.iinfo(dtype).min, np.iinfo(dtype).max).astype(dtype)
        return stacked_image

    def save_image(self, image, output_path):
        cv2.imwrite(output_path, image)
        
def main(db_path, update_progress=None):
    try:
        image_processor = AverageAlgorithm(db_path)
        image_paths = image_processor.get_all_image_paths()
        if not image_paths:
            if update_progress:
                update_progress(0, language_config.RUN_IMAGE_PROCESS_LOAD_FAILED)
            return

        reference_image_path = image_paths[0]
        reference_image_name = os.path.splitext(os.path.basename(reference_image_path))[0]
        output_path = f"database/stack/{reference_image_name}_average_stack.tiff"

        if update_progress:
            update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        global_hdf5_path = "database/align/aligned_images.h5"
        images = []

        if os.path.exists(global_hdf5_path):
            with h5py.File(global_hdf5_path, 'r') as h5f:
                total_images = len(h5f.keys())
                for i, key in enumerate(h5f.keys()):
                    images.append(np.array(h5f[key]))
                    progress = int((i / total_images) * 10)
                    message = language_config.RUN_IMAGE_PROCESS_LOAD_PROGRESS.format(
                        current=i + 1, total=total_images)
                    if update_progress:
                        update_progress(progress, message)
        else:
            total_images = len(image_paths)
            for i, path in enumerate(image_paths):
                image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if image is not None:
                    images.append(image)
                progress = int((i / total_images) * 100)
                message = language_config.RUN_IMAGE_PROCESS_LOAD_PROGRESS.format(
                    current=i + 1, total=total_images)
                if update_progress:
                    update_progress(progress, message)

        if images:
            stacked_image = image_processor.stack_average_images(images, update_progress)
            image_processor.save_image(stacked_image, output_path)
            if update_progress:
                update_progress(100, language_config.RUN_IMAGE_PROCESS_STACK_SUCCESS.format(output_path=output_path))
        else:
            if update_progress:
                update_progress(0, language_config.STACK_AVERAGE_IMAGES_FAILED)
    except Exception as e:
        error_message = language_config.RUN_ERROR_STATUS.format(error=str(e))
        if update_progress:
            update_progress(0, error_message)
            
def running_average(parent=None):
    """
    Menampilkan progress bar dengan gaya kustom dan pesan proses utama.
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_AVERAGE)
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)

    # Membuat layout untuk progress bar dan label
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

    dialog.show()

    try:
        def update_progress(progress, message):
            # Perbarui progress bar dan label
            progress_bar.setValue(progress)
            label.setText(message)

            # Menampilkan progres pada konsol
            print(f"Progress: {progress}%, Message: {message}")

        db_path = "pixel_refine_database.db"
        main(db_path, update_progress)

        progress_bar.setValue(100)
        label.setText(language_config.WINDOW_PROCESSING_COMPLETE)
        print("Pemrosesan selesai!")  # Menampilkan pesan selesai di konsol
        QMessageBox.information(dialog, "Done", language_config.WINDOW_PROCESS_SUCCESS)
    except Exception as e:
        print(language_config.RUN_ERROR_STATUS.format(error=str(e)))  # Menampilkan pesan kesalahan di konsol
        QMessageBox.critical(dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=str(e)))
    finally:
        dialog.close()

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"  # Path ke database Anda
    main(db_path)
