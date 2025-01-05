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

class BM4DAlgorithm(QThread):
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

    def block_matching(self, images, block_size=(8, 8)):
        """Memecah gambar menjadi blok-blok kecil dan melakukan pencocokan blok antara gambar."""
        blocks = []
        for image in images:
            h, w = image.shape
            for y in range(0, h - block_size[0], block_size[0]):
                for x in range(0, w - block_size[1], block_size[1]):
                    block = image[y:y+block_size[0], x:x+block_size[1]]
                    blocks.append(block)
        return blocks

    def apply_bm4d_filter(self, blocks, block_size=(8, 8), sigma=0.1):
        """Menerapkan filter BM4D untuk setiap blok."""
        filtered_blocks = []
        for block in blocks:
            # Terapkan filter BM4D pada setiap blok (contoh dengan filter Gaussian sederhana untuk ilustrasi)
            filtered_block = cv2.GaussianBlur(block, (5, 5), sigma)
            filtered_blocks.append(filtered_block)
        return filtered_blocks

    def reconstruct_image_from_blocks(self, blocks, image_shape, block_size=(8, 8)):
        """Merepresentasikan kembali gambar dari blok-blok yang telah diproses."""
        h, w = image_shape
        reconstructed_image = np.zeros((h, w), dtype=np.float32)
        idx = 0
        for y in range(0, h - block_size[0], block_size[0]):
            for x in range(0, w - block_size[1], block_size[1]):
                block = blocks[idx]
                reconstructed_image[y:y+block_size[0], x:x+block_size[1]] = block
                idx += 1
        return np.clip(reconstructed_image, 0, 255).astype(np.uint8)

    def bm4d(self, images, block_size=(8, 8), sigma=0.1):
        if not images:
            raise ValueError(language_config.SIMILARITY_MNFR_LOAD_FAILED)

        # Pencocokan blok antar gambar
        blocks = self.block_matching(images, block_size)

        # Terapkan BM4D Filter pada blok-blok
        filtered_blocks = self.apply_bm4d_filter(blocks, block_size, sigma)

        # Rekonstruksi gambar dari blok-blok yang telah difilter
        h, w = images[0].shape
        filtered_image = self.reconstruct_image_from_blocks(filtered_blocks, (h, w), block_size)

        return filtered_image

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

            output_path = "database/stack/bm4d_filtered_image.tiff"
            image_processor = BM4DAlgorithm(db_path)

            self.progress_update.emit(0, language_config.RUN_IMAGE_PROCESS_STARTED)

            image_paths = image_processor.get_all_image_paths()
            if not image_paths:
                self.progress_update.emit(0, language_config.RUN_IMAGE_PROCESS_LOAD_FAILED)
                self.finished.emit()
                return

            images = []
            for i, path in enumerate(image_paths):
                image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if image is not None:
                    images.append(image)
                self.progress_update.emit(int((i/len(image_paths))*100), language_config.RUN_IMAGE_PROCESS_LOAD_PROGRESS.format(current=i+1, total=len(image_paths)))

            if images:
                filtered_image = self.bm4d(images)
                image_processor.save_image(filtered_image, output_path)
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
        self.processor_thread = BM4DAlgorithm(self.db_path)
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
