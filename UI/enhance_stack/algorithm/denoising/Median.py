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
            def update_progress(progress, message):
                self.progress_updated.emit(progress, message)

            # Fungsi callback untuk mengecek status stop
            def is_stop_requested():
                return self.stop_requested

            # Panggil main untuk menjalankan proses dengan parameter yang benar
            main(self.db_path, update_progress=update_progress, stop_requested=is_stop_requested)
            self.finished.emit()
        except Exception as e:
            print(f"Error terjadi: {str(e)}")  # Menampilkan pesan error di konsol
            self.error_occurred.emit(str(e))  # Mengirim pesan error melalui sinyal

    def stop(self):
        self.stop_requested = True  # Set flag agar thread berhenti

class MedianAlgorithm:
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
    
    def raised_cosine_window(self, tile_size):
        """Membuat raised cosine window untuk blending."""
        y = np.hanning(tile_size[0])
        x = np.hanning(tile_size[1])
        window = np.outer(y, x)
        return window

    def median_stack(self, images, tile_size=(128, 128), overlap=0.20, sub_sampling_factor=4, update_progress=None, stop_requested=None):
        """
        Multi-frame Noise Reduction (MFNR) dengan optimasi tile processing dan menggunakan MAD untuk pembobotan.
        """
        if not images:
            raise ValueError(language_config.SIMILARITY_MNFR_LOAD_FAILED)

        dtype = images[0].dtype
        if dtype != np.uint8 and dtype != np.uint16:
            raise TypeError(language_config.SIMILARITY_MNFR_BIT_REQUIRED)

        # Ambil gambar referensi
        reference_image = np.array(images[0], dtype=np.float32)
        h, w, _ = reference_image.shape

        # Langkah tile
        tile_step_y = int(tile_size[0] * (1 - overlap))
        tile_step_x = int(tile_size[1] * (1 - overlap))
        vertical_offset = tile_size[0] // 2

        # Hasil akhir dan peta bobot
        final_image = np.zeros_like(reference_image, dtype=np.float32)
        weight_map = np.zeros((h, w), dtype=np.float32)

        # Precompute cosine window untuk caching sekali
        cosine_window = self.raised_cosine_window(tile_size)

        for i, image in enumerate(images):
            progress = int((i + 1) / len(images) * 100)
            message = language_config.RUN_IMAGE_PROCESSING.format(i=i+1, total_images=len(images))
            print(message)

            if update_progress:
                update_progress(progress, message)
                
            if stop_requested and stop_requested():
                print("Process stopped by user.")
                break
                
            current_image = np.array(image, dtype=np.float32)
            if current_image.shape != reference_image.shape:
                raise ValueError(language_config.SIMILARITY_MNFR_SIZE_FAILED.format(i=i+1))

            # Normalisasi gambar ke rentang 0-1
            current_image_normalized = current_image / np.iinfo(dtype).max
            reference_image_normalized = reference_image / np.iinfo(dtype).max

            # Proses tile satu per satu dengan optimasi akses memori
            for y in range(0, h, tile_step_y):
                offset_x = vertical_offset if (y // tile_step_y) % 2 == 1 else 0
                for x in range(-offset_x, w, tile_step_x):
                    # Tentukan batas tile
                    y_end = min(y + tile_size[0], h)
                    x_end = min(x + tile_size[1], w)
                    x_start = max(x, 0)

                    tile_height = y_end - y
                    tile_width = x_end - x_start

                    # Ambil tile referensi dan saat ini tanpa sub-sampling
                    ref_tile = reference_image_normalized[y:y_end, x_start:x_end]
                    current_tile = current_image_normalized[y:y_end, x_start:x_end]

                    # Sub-sampling gambar untuk mempercepat perhitungan
                    subsampled_ref_tile = ref_tile[::sub_sampling_factor, ::sub_sampling_factor]
                    subsampled_current_tile = current_tile[::sub_sampling_factor, ::sub_sampling_factor]

                    # Gunakan cosine window yang sudah di-cache
                    window = cosine_window[:tile_height, :tile_width]

                    # Estimasi MAD untuk tile referensi dan tile saat ini
                    mad_ref = np.median(np.abs(subsampled_ref_tile - np.median(subsampled_ref_tile)))
                    mad_current = np.median(np.abs(subsampled_current_tile - np.median(subsampled_current_tile)))

                    # Bobot berdasarkan MAD (lebih kecil MAD -> lebih tinggi bobot)
                    similarity_weight = 1.0  # Menetapkan bobot tile tetap 1

                    # Perbarui final_image dan weight_map
                    weighted_tile = current_tile * window[..., np.newaxis] * similarity_weight
                    weight_map[y:y_end, x_start:x_end] += window * similarity_weight
                    final_image[y:y_end, x_start:x_end] += weighted_tile * np.iinfo(dtype).max  # Denormalisasi

            print(language_config.SIMILARITY_MNFR_PROCESS_SUCCESS.format(i=i+1, count=len(images)))

        # Normalisasi akhir
        final_image = final_image / (weight_map[..., np.newaxis] + 1e-6)
        final_image = np.clip(final_image, np.iinfo(dtype).min, np.iinfo(dtype).max).astype(dtype)

        print(language_config.SIMILARITY_MNFR_PROCESS_FINISHED)
        return final_image


    def save_image(self, image, output_path):
        cv2.imwrite(output_path, image)
        
def main(db_path, update_progress=None, stop_requested=None):
    try:
        image_processor = MedianAlgorithm(db_path)
        image_paths = image_processor.get_all_image_paths()
        if not image_paths:
            if update_progress:
                update_progress(0, language_config.RUN_IMAGE_PROCESS_LOAD_FAILED)
            return

        reference_image_path = image_paths[0]
        reference_image_name = os.path.splitext(os.path.basename(reference_image_path))[0]
        output_path = f"database/stack/{reference_image_name}_median_stack.tiff"

        if update_progress:
            update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        global_hdf5_path = "database/align/aligned_images.h5"
        images = []

        if os.path.exists(global_hdf5_path):
            with h5py.File(global_hdf5_path, 'r') as h5f:
                total_images = len(h5f.keys())
                for i, key in enumerate(h5f.keys()):
                    if stop_requested and stop_requested():
                        break
                    images.append(np.array(h5f[key]))
                    progress = int((i / total_images) * 10)
                    message = language_config.RUN_IMAGE_PROCESS_LOAD_PROGRESS.format(
                        current=i + 1, total=total_images)
                    if update_progress:
                        update_progress(progress, message)
        else:
            total_images = len(image_paths)
            for i, path in enumerate(image_paths):
                if stop_requested and stop_requested():
                    break
                image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if image is not None:
                    images.append(image)
                progress = int((i / total_images) * 100)
                message = language_config.RUN_IMAGE_PROCESS_LOAD_PROGRESS.format(
                    current=i + 1, total=total_images)
                if update_progress:
                    update_progress(progress, message)

        if images:
            # Tidak perlu mendefinisikan tile_size di sini
            stacked_image = image_processor.median_stack(images, update_progress=update_progress, stop_requested=stop_requested)
            image_processor.save_image(stacked_image, output_path)
            if update_progress:
                update_progress(100, language_config.RUN_IMAGE_PROCESS_STACK_SUCCESS.format(output_path=output_path))
        else:
            if update_progress:
                update_progress(0, language_config.STACK_IMAGES_FAILED)
    except Exception as e:
        error_message = language_config.RUN_ERROR_STATUS.format(error=str(e))
        if update_progress:
            update_progress(0, error_message)
        print(f"Error encountered: {str(e)}")

            
def running_median(parent=None):
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_SIMILARITY)
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
        QMessageBox.critical(dialog, "Error", f"An error occurred: {error}")
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
                                        "Are you sure you want to cancel the process?",
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
