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

class SimilarityAlgorithm(QThread):
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
    
    def raised_cosine_window(self, tile_size):
        """Membuat raised cosine window untuk blending."""
        y = np.hanning(tile_size[0])
        x = np.hanning(tile_size[1])
        window = np.outer(y, x)
        return window
    
    def similarity_mfnr(self, images, tile_size=(32, 32), overlap=0.25, motion_threshold=0.035):
        if not images:
            raise ValueError(language_config.SIMILARITY_MNFR_LOAD_FAILED)

        dtype = images[0].dtype
        if dtype != np.uint8 and dtype != np.uint16:
            raise TypeError(language_config.SIMILARITY_MNFR_BIT_REQUIRED)

        reference_image = np.array(images[0], dtype=np.float32)
        h, w, _ = reference_image.shape

        print(language_config.SIMILARITY_MNFR_TILE_SLICE.format(height=h, width=w, tile_size=tile_size))

        tile_step_y = int(tile_size[0] * (1 - overlap))
        tile_step_x = int(tile_size[1] * (1 - overlap))
        vertical_offset = tile_size[0] // 2

        final_image = np.zeros_like(reference_image, dtype=np.float32)
        weight_map = np.zeros((h, w), dtype=np.float32)
        cosine_window = self.raised_cosine_window(tile_size)

        for i, image in enumerate(images):
            progress = int((i + 1) / len(images) * 100)
            self.progress_update.emit(progress, language_config.RUN_IMAGE_PROCESSING.format(i=i+1, total_images=len(images)))
            print(language_config.RUN_IMAGE_PROCESSING.format(i=i+1, total_images=len(images)))

            current_image = np.array(image, dtype=np.float32)
            if current_image.shape != reference_image.shape:
                raise ValueError(language_config.SIMILARITY_MNFR_SIZE_FAILED.format(i=i+1))

            # Normalisasi gambar ke rentang 0-1
            current_image_normalized = current_image / np.iinfo(dtype).max
            reference_image_normalized = reference_image / np.iinfo(dtype).max

            processed_tiles = 0

            for y in range(0, h, tile_step_y):
                offset_x = vertical_offset if (y // tile_step_y) % 2 == 1 else 0
                for x in range(-offset_x, w, tile_step_x):
                    y_end = min(y + tile_size[0], h)
                    x_end = min(x + tile_size[1], w)
                    x_start = max(x, 0)

                    tile_height = y_end - y
                    tile_width = x_end - x_start

                    ref_tile = reference_image_normalized[y:y_end, x_start:x_end]
                    current_tile = current_image_normalized[y:y_end, x_start:x_end]

                    window = cosine_window[:tile_height, :tile_width]

                    Dz = np.mean(np.abs(current_tile - ref_tile))
                    similarity_weight = 1.0 if Dz < motion_threshold else np.exp(-Dz / motion_threshold)

                    weighted_tile = current_tile * window[..., np.newaxis] * similarity_weight
                    weight_map[y:y_end, x_start:x_end] += window * similarity_weight
                    final_image[y:y_end, x_start:x_end] += weighted_tile * np.iinfo(dtype).max # Denormalisasi disini

                    processed_tiles += 1
            print(language_config.SIMILARITY_MNFR_PROCESS_SUCCESS.format(i=i+1, count=len(images)))

        final_image = final_image / (weight_map[..., np.newaxis] + 1e-6)
        final_image = np.clip(final_image, np.iinfo(dtype).min, np.iinfo(dtype).max).astype(dtype)

        print(language_config.SIMILARITY_MNFR_PROCESS_FINISHED)
        return final_image

    def save_image(self, image, output_path):
        cv2.imwrite(output_path, image)

    def run(self):
        try:
            db_path = "pixel_refine_database.db"
            image_paths = self.get_all_image_paths()
            if not image_paths:
                self.progress_update.emit(0, language_config.RUN_IMAGE_NOT_FOUND)
                self.finished.emit()
                return
            reference_image_path = image_paths[0]
            reference_image_name = os.path.splitext(os.path.basename(reference_image_path))[0]
            output_path = f"database/stack/{reference_image_name}_similarity_stack.tiff"
            image_processor = SimilarityAlgorithm(db_path)

            self.progress_update.emit(0, language_config.RUN_IMAGE_PROCESS_STARTED)
            global_hdf5_path = "database/align/global/aligned_images.h5"
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
                stacked_image = self.similarity_mfnr(images)
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
        self.setWindowTitle(language_config.WINDOW_TITLE_SIMILARITY)
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
        self.processor_thread = SimilarityAlgorithm(self.db_path)
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
