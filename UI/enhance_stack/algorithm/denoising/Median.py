import cv2
import numpy as np
import os
import sqlite3
import h5py
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QProgressBar,
                             QVBoxLayout, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import PyQt6.QtGui as QtGui

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from UI.settings.General.Language import language_config


class MedianAlgorithm(QThread):
    progress_update = pyqtSignal(int, str)
    finished = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path

    def get_all_image_paths(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]

    def load_images_from_hdf5(self, hdf5_path):
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                image = np.array(h5f[key])
                images.append(image)
        return images

    def load_images_from_folder(self, folder_path):
        image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        return self.load_images_from_paths(image_paths)

    def load_images_from_paths(self, image_paths):
        images = []
        for image_path in image_paths:
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if image is not None:
                images.append(image)
        return images

    def stack_median_images(self, images):
        if len(images) == 0:
            raise ValueError(language_config.RUN_IMAGE_NOT_FOUND)

        dtype = images[0].dtype
        stacked_image = np.zeros_like(images[0], dtype=np.float64)

        for i, image in enumerate(images):
            if image is None:
                continue

            current_image = image.astype(np.float64)
            stacked_image += current_image

            progress = int((i + 1) / len(images) * 100)
            self.progress_update.emit(progress, language_config.STACK_AVERAGE_IMAGES_PROCESS.format(current=i+1, total=len(images)))

        stacked_image = np.median(np.array(images), axis=0)
        stacked_image = np.clip(stacked_image, np.iinfo(dtype).min, np.iinfo(dtype).max).astype(dtype)
        return stacked_image

    def save_image(self, image, output_path):
        cv2.imwrite(output_path, image)

    def run(self):
        try:
            db_path = "pixel_refine_database.db"
            image_paths = self.get_all_image_paths()
            if not image_paths:
                self.progress_update.emit(0, language_config.RUN_IMAGE_PROCESS_LOAD_FAILED)
                self.finished.emit()
                return
            reference_image_path = image_paths[0]
            reference_image_name = os.path.splitext(os.path.basename(reference_image_path))[0]
            output_path = f"database/stack/{reference_image_name}_median_stack.tiff"
            image_processor = MedianAlgorithm(db_path)

            self.progress_update.emit(0, language_config.RUN_IMAGE_PROCESS_STARTED)
            global_hdf5_path = "database/align/aligned_images.h5"
            total_images = 0
            if os.path.exists(global_hdf5_path):
                with h5py.File(global_hdf5_path, 'r') as h5f:
                    total_images = len(h5f.keys())
                self.progress_update.emit(0, language_config.RUN_IMAGE_PROCESS_LOAD_HDF5)
                images = []
                with h5py.File(global_hdf5_path, 'r') as h5f:
                    for i, key in enumerate(h5f.keys()):
                        images.append(np.array(h5f[key]))
                        self.progress_update.emit(int((i/total_images)*10), language_config.RUN_IMAGE_PROCESS_LOAD_PROGRESS.format(current=i+1, total=total_images))
            else:
                self.progress_update.emit(0, language_config.RUN_IMAGE_PROCESS_LOAD_PATH)
                image_paths = image_processor.get_all_image_paths()
                if not image_paths:
                    self.progress_update.emit(0, language_config.RUN_IMAGE_PROCESS_LOAD_FAILED)
                    self.finished.emit()
                    return
                total_images = len(image_paths)
                images = []
                for i, path in enumerate(image_paths):
                    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                    if image is not None:
                        images.append(image)
                    self.progress_update.emit(int((i/total_images)*100), language_config.RUN_IMAGE_PROCESS_LOAD_PROGRESS.format(current=i+1, total=total_images))


            if images:
                stacked_image = self.stack_median_images(images)
                image_processor.save_image(stacked_image, output_path)
                self.progress_update.emit(100, language_config.RUN_IMAGE_PROCESS_STACK_SUCCESS.format(output_path=output_path))
            else:
                self.progress_update.emit(0, language_config.STACK_AVERAGE_IMAGES_FAILED)
            self.finished.emit()
        except Exception as e:
            self.error_signal.emit(language_config.RUN_ERROR_STATUS.format(error=str(e)))
            self.finished.emit()

class ProcessWindows(QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.setWindowTitle(language_config.WINDOW_TITLE_MEDIAN)
        self.setFixedSize(300, 90)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        self.db_path = db_path
        self.initUI()
        self.center_window()
        self.processor_thread = None

    def initUI(self):
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
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
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status = QLabel(language_config.WINDOW_INITIATION, self)
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label_status)
        layout.addWidget(self.progress_bar)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

    def start_processing(self):
        self.progress_bar.setValue(0)
        self.label_status.setText(language_config.WINDOW_START_PROCESSING)
        self.processor_thread = MedianAlgorithm(self.db_path)
        self.processor_thread.progress_update.connect(self.update_progress)
        self.processor_thread.error_signal.connect(self.show_error_message)
        self.processor_thread.finished.connect(self.process_finished)
        self.processor_thread.start()

    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.label_status.setText(message)
        QApplication.processEvents()

    def process_finished(self):
        self.label_status.setText(language_config.WINDOW_PROCESSING_COMPLETE)
        QMessageBox.information(self, "Done", language_config.WINDOW_PROCESS_SUCCESS)
        self.close()

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def center_window(self):
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_path = "pixel_refine_database.db"
    window = ProcessWindows(db_path)
    window.show()
    window.start_processing()
    sys.exit(app.exec())
