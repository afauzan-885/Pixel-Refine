import cv2
import numpy as np
import sqlite3, os
import h5py
import glob
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QProgressBar,
                             QVBoxLayout, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import PyQt6.QtGui as QtGui

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from UI.settings.General.Language import language_config

class AKAZEAlgorithm(QThread):
    progress_update = pyqtSignal(int, str)
    finished = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, db_path, debug_folder="database/align/global/debug_images", hdf5_path="database/align/global/aligned_images.h5"):
        super().__init__()
        self.db_path = db_path
        self.debug_folder = debug_folder
        self.hdf5_path = hdf5_path
        self.stop_requested = False
        self.orb = cv2.AKAZE_create()

        if not os.path.exists(self.debug_folder):
            os.makedirs(self.debug_folder)
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

    def get_all_image_paths(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]

    def load_images_from_paths(self, image_paths):
        images = []
        for image_path in image_paths:
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if image is not None:
                images.append(image)
            else:
                print(language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED.format(image_path=image_path))
        return images

    def align_images(self, base_image, target_image, image_id):
        print(language_config.ALIGN_IMAGES_STATUS.format(image_id=image_id))

        kp1, des1 = self.orb.detectAndCompute(base_image, None)
        kp2, des2 = self.orb.detectAndCompute(target_image, None)

        if des1 is None or des2 is None or len(kp1) < 2 or len(kp2) < 2 :
            print(language_config.ALIGN_IMAGES_CALCULATE_FAILED.format(image_id=image_id))
            return target_image

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        matches = sorted(matches, key=lambda x: x.distance)
        good_matches = matches[:int(len(matches) * 0.1)] if matches else []

        if len(good_matches) > 4:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

            if M is not None:
                h, w = base_image.shape[:2]
                aligned_image = cv2.warpPerspective(target_image, M, (w, h))
                print(language_config.ALIGN_IMAGES_CALCULATE_FINISHED.format(image_id=image_id))
                return aligned_image
            else:
                print(language_config.ALIGN_IMAGES_COMPENSATE_FAILED.format(image_id=image_id))
                return target_image
        else:
            print(language_config.ALIGN_IMAGES_MATCHING_FAILED.format(image_id=image_id))
            return target_image

    def save_to_hdf5(self, aligned_images):
        print(language_config.SAVE_TO_HDF5_ALIGNED_SAVING.format(self.hdf5_path))
        with h5py.File(self.hdf5_path, "w") as h5f:
            for i, image in enumerate(aligned_images):
                h5f.create_dataset(f"image_{i}", data=image, compression="gzip")
                print(language_config.SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING.format(i=i))
        print(language_config.SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED)

    def save_individual_image(self, image, image_id, use_tiff=True):
        if use_tiff:
            debug_image_path = os.path.join(self.debug_folder, f"aligned_image_{image_id}.tiff")
            cv2.imwrite(debug_image_path, image)
        else:
            debug_image_path = os.path.join(self.debug_folder, f"aligned_image_{image_id}.png")
            cv2.imwrite(debug_image_path, image)
        print(f"Gambar yang diselaraskan disimpan ke {debug_image_path} dengan tipe data {image.dtype}.")
        del image

    def delete_debug_images(self):
        print("Menghapus gambar di folder debug...")
        for image_file in glob.glob(os.path.join(self.debug_folder, "*.png")):
            os.remove(image_file)
            print(f"Gambar {image_file} dihapus.")
        print("Semua gambar debug berhasil dihapus.")

    def run(self):
        try:
            image_paths = self.get_all_image_paths()
            if not image_paths:
                self.progress_update.emit(0, language_config.RUN_IMAGE_NOT_FOUND)
                self.finished.emit()
                return

            base_image = cv2.imread(image_paths[0], cv2.IMREAD_UNCHANGED)
            if base_image is None:
                self.progress_update.emit(0, language_config.RUN_REFERENCE_IMAGE_NOT_FOUND.format(image_paths=image_paths[0]))
                self.finished.emit()
                return

            total_images = len(image_paths)
            with h5py.File(self.hdf5_path, "w") as h5f:
                h5f.create_dataset(f"image_0", data=base_image, compression="gzip")
                self.progress_update.emit(int((1/total_images)*100), language_config.RUN_SAVING_REFERENCE_IMAGE)

                for i in range(1, total_images):
                    if self.stop_requested:
                        break

                    self.progress_update.emit(int((i/total_images)*100), language_config.RUN_IMAGE_PROCESSING.format(i=i, total_images=total_images))

                    target_image = cv2.imread(image_paths[i], cv2.IMREAD_UNCHANGED)
                    if target_image is None:
                        self.progress_update.emit(int((i/total_images)*100), language_config.RUN_IMAGE_PROCESSING_FAILED.format(i=i))
                        continue

                    aligned_image = self.align_images(base_image, target_image, f"image_{i}")

                    h5f.create_dataset(f"image_{i}", data=aligned_image, compression="gzip")
                    self.progress_update.emit(int((i/total_images)*100), language_config.RUN_IMAGE_PROCESSING_SAVING.format(i=i))
                    self.save_individual_image(aligned_image, i)

                    del target_image, aligned_image

            self.delete_debug_images()
            self.progress_update.emit(100, language_config.RUN_IMAGE_PROCESSING_FINISHED)
            self.finished.emit()
        except Exception as e:
            self.error_signal.emit(language_config.RUN_ERROR_STATUS.format(error=str(e)))
            QMessageBox.critical(None, "Error", language_config.RUN_ERROR_MESSAGE.format(error=str(e)))
            self.finished.emit()

class ProcessWindows(QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.setWindowTitle(language_config.WINDOW_TITLE_AKAZE)
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
        self.processor_thread = AKAZEAlgorithm(self.db_path)
        self.processor_thread.progress_update.connect(self.update_progress)
        self.processor_thread.error_signal.connect(self.show_error_message)
        self.processor_thread.finished.connect(self.process_finished)  # Sambungkan ke process_finished
        self.processor_thread.start()


    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.label_status.setText(message)
        QApplication.processEvents() # VERY IMPORTANT

    def process_finished(self):
        self.label_status.setText(language_config.WINDOW_PROCESSING_COMPLETE)
        self.close()  # Menutup jendela setelah proses selesai
    
    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def center_window(self):
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_path = "pixel_refine_database.db" # Replace with your database path
    window = ProcessWindows(db_path)
    window.show()
    window.start_processing()
    sys.exit(app.exec())