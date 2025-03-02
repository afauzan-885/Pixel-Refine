import concurrent.futures
import cv2
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# from UI.enhance_stack.algorithm.denoising.extra_similarity.extra_algorithm import accumulate_tiles

from UI.enhance_stack.algorithm.denoising.extra_similarity import extra_algorithm
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.resources.stylesheet.stylesheet import PROGRESS_BAR
from UI.settings.General.Language import language_config

class SimilarityAlgorithm:
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

    def load_images_from_hdf5(self, hdf5_path, stop_requested=None):
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                if stop_requested and stop_requested():  # Cek apakah harus berhenti
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images
    
    def raised_cosine_window(self, tile_size):
        """Membuat raised cosine window untuk blending."""
        y = np.hanning(tile_size[0])
        x = np.hanning(tile_size[1])
        window = np.outer(y, x)
        return window.astype(np.float32)


    def similarity_mfnr(self, images, tile_size=(12, 12), overlap=0.30,
                      motion_threshold=0.0025, noise_threshold=0.0025,
                      update_progress=None, stop_requested=None):
        # Validasi input
        if not images:
            raise ValueError("Gagal memuat gambar referensi.")

        dtype = images[0].dtype
        if dtype not in (np.uint8, np.uint16):
            raise TypeError("Tipe bit gambar harus uint8 atau uint16.")

        reference_image = self.normalize_image(images[0], dtype)
        h, w, _ = reference_image.shape

        step_y = max(int(tile_size[0] * (1 - overlap)), 1)
        step_x = max(int(tile_size[1] * (1 - overlap)), 1)

        row_starts = list(range(0, h - tile_size[0] + 1, step_y))
        if row_starts[-1] != h - tile_size[0]:
            row_starts.append(h - tile_size[0])
        col_starts = list(range(0, w - tile_size[1] + 1, step_x))
        if col_starts[-1] != w - tile_size[1]:
            col_starts.append(w - tile_size[1])

        base_window = self.raised_cosine_window(tile_size)
        
        final_image = np.zeros_like(reference_image, dtype=np.float32)
        weight_map = np.zeros((h, w), dtype=np.float32)

        # Konversi scale ke float32
        scale = np.float32(np.iinfo(dtype).max)
        num_images = len(images)
        
        for i, image in enumerate(images):
            if update_progress:
                progress = int((i + 1) / num_images * 100)
                message = f"Memproses gambar {i+1} dari {num_images}"
                update_progress(progress, message)

            if stop_requested and stop_requested():
                break

            current_image = self.normalize_image(image, dtype)
            if current_image.shape != reference_image.shape:
                raise ValueError(f"Ukuran gambar ke-{i+1} tidak sesuai.")

            row_starts_arr = np.array(row_starts, dtype=np.int32)
            col_starts_arr = np.array(col_starts, dtype=np.int32)

            # Panggil fungsi AOT yang sudah dikompilasi
            extra_algorithm.accumulate_tiles(final_image, weight_map, current_image, reference_image,
                                 base_window, row_starts_arr, col_starts_arr,
                                 tile_size[0], tile_size[1],
                                 motion_threshold, noise_threshold, scale)


        final_image /= (weight_map[..., np.newaxis] + 1e-3)
        final_image = np.clip(final_image, np.iinfo(dtype).min, np.iinfo(dtype).max).astype(dtype)

        print("Proses similarity_mfnr selesai.")
        return final_image

    def normalize_image(self, image, dtype):
        # Konversi ke float32 dan pastikan array contiguous
        image_float = np.ascontiguousarray(image.astype(np.float32))
        norm_image = (image_float - image_float.min()) / (image_float.max() - image_float.min() + 1e-6)
        if len(image.shape) == 2:
            norm_image = np.stack((norm_image,)*3, axis=-1)
        return norm_image.astype(np.float32)

    def save_image(self, image, output_path):
        cv2.imwrite(output_path, image)
        
def main(db_path, update_progress=None, stop_requested=None, batch_size=8):
    try:
        image_processor = SimilarityAlgorithm(db_path)
        image_paths = image_processor.get_all_image_paths()
        if not image_paths:
            if update_progress:
                update_progress(0, language_config.RUN_IMAGE_PROCESS_LOAD_FAILED)
            return

        reference_image_path = image_paths[0]
        reference_image_name = os.path.splitext(os.path.basename(reference_image_path))[0]
        output_path = f"database/stack/{reference_image_name}_similarity_stack.tif"

        if update_progress:
            update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        global_hdf5_path = "database/align/aligned_images.h5"
        processed_batches = []  # Menyimpan hasil sementara dari batch

        if os.path.exists(global_hdf5_path):
            with h5py.File(global_hdf5_path, 'r') as h5f:
                keys = list(h5f.keys())
                total_images = len(keys)

                for batch_start in range(0, total_images, batch_size):
                    if stop_requested and stop_requested():
                        break

                    batch_keys = keys[batch_start:batch_start + batch_size]
                    batch_images = [np.array(h5f[key]) for key in batch_keys]

                    # Proses batch
                    batch_result = image_processor.similarity_mfnr(batch_images, update_progress=update_progress, stop_requested=stop_requested)
                    processed_batches.append(batch_result)

                    progress = int(((batch_start + len(batch_keys)) / total_images) * 100)
                    if update_progress:
                        update_progress(progress, language_config.RUN_IMAGE_PROCESS_BATCH_PROGRESS.format(
                            current=batch_start + len(batch_keys), total=total_images
                        ))
        else:
            total_images = len(image_paths)

            for batch_start in range(0, total_images, batch_size):
                if stop_requested and stop_requested():
                    break

                batch_paths = image_paths[batch_start:batch_start + batch_size]
                batch_images = [cv2.imread(path, cv2.IMREAD_UNCHANGED) for path in batch_paths if cv2.imread(path, cv2.IMREAD_UNCHANGED) is not None]

                # Proses batch
                batch_result = image_processor.similarity_mfnr(batch_images, update_progress=update_progress, stop_requested=stop_requested)
                processed_batches.append(batch_result)

                progress = int(((batch_start + len(batch_paths)) / total_images) * 100)
                if update_progress:
                    update_progress(progress, language_config.RUN_IMAGE_PROCESS_BATCH_PROGRESS.format(
                        current=batch_start + len(batch_paths), total=total_images
                    ))

        if processed_batches:
            # Proses fine-tuning dari semua hasil batch
            final_result = image_processor.similarity_mfnr(processed_batches, update_progress=update_progress, stop_requested=stop_requested)

            # Simpan hasil akhir
            image_processor.save_image(final_result, output_path)

            if update_progress:
                update_progress(100, language_config.RUN_IMAGE_PROCESS_STACK_SUCCESS.format(output_path=output_path))
        else:
            if update_progress:
                update_progress(0, language_config.STACK_IMAGES_FAILED)

    except Exception as error:
        error_message = f"Error encountered: {str(error)}"
        print(error_message)  # Menampilkan error untuk debugging
        if update_progress:
            update_progress(0, error_message)
        raise


def running_similarity(parent=None):
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