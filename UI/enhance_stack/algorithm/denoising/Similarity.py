import cv2
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from UI.enhance_stack.algorithm.denoising.extra_similarity.extra_algorithm import precompute_reference_tiles, process_tile_similarity, update_final_image
from concurrent.futures import ThreadPoolExecutor
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
        with h5py.File(hdf5_path, 'r', swmr=True, libver='latest') as h5f:
            keys = list(h5f.keys())  # Ambil semua dataset di HDF5
            
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(lambda k: np.array(h5f[k]), key): key for key in keys}

                for future in futures:
                    if stop_requested and stop_requested():  # Cek apakah harus berhenti
                        break
                    images.append(future.result())  # Ambil hasil pembacaan

        return images
    
    def add_part_with_blending(final_image, weight_map, part, weight_map_part, y_start, y_end, x_start, x_end):
            final_image[y_start:y_end, x_start:x_end] += part
            weight_map[y_start:y_end, x_start:x_end] += weight_map_part[..., np.newaxis]

    def similarity_mfnr(self, images, tile_size=(50, 50), overlap=0.30, motion_threshold=0.02, update_progress=None, stop_requested=None):
        if not images:
            raise ValueError(language_config.SIMILARITY_MNFR_LOAD_FAILED)

        dtype = images[0].dtype
        if dtype not in (np.uint8, np.uint16):
            raise TypeError(language_config.SIMILARITY_MNFR_BIT_REQUIRED)

        reference_image = self.normalize_image(images[0], dtype)
        h, w, _ = reference_image.shape

        overlap_pixels_y = int(tile_size[0] * overlap)
        overlap_pixels_x = int(tile_size[1] * overlap)

        h_mid = h // 2
        w_mid = w // 2
        reference_parts = [
            reference_image[:h_mid + overlap_pixels_y, :w_mid + overlap_pixels_x],
            reference_image[:h_mid + overlap_pixels_y, w_mid - overlap_pixels_x:],
            reference_image[h_mid - overlap_pixels_y:, :w_mid + overlap_pixels_x],
            reference_image[h_mid - overlap_pixels_y:, w_mid - overlap_pixels_x:]
        ]

        precomputed_reference_tiles = [precompute_reference_tiles(part, tile_size, overlap) for part in reference_parts]
        final_image_parts = [np.zeros_like(part, dtype=np.float32) for part in reference_parts]
        weight_map_parts = [np.zeros(part.shape[:2], dtype=np.float32) for part in reference_parts]

        for i, image in enumerate(images):
            if update_progress:
                progress = int((i + 1) / len(images) * 100)
                message = language_config.RUN_IMAGE_PROCESSING.format(i=i + 1, total_images=len(images))
                update_progress(progress, message)

            if stop_requested and stop_requested():
                print("Process stopped by user.")
                break

            current_image = self.normalize_image(image, dtype)
            if current_image.shape != reference_image.shape:
                raise ValueError(language_config.SIMILARITY_MNFR_SIZE_FAILED.format(i=i + 1))

            current_image_parts = [
                current_image[:h_mid + overlap_pixels_y, :w_mid + overlap_pixels_x],
                current_image[:h_mid + overlap_pixels_y, w_mid - overlap_pixels_x:],
                current_image[h_mid - overlap_pixels_y:, :w_mid + overlap_pixels_x],
                current_image[h_mid - overlap_pixels_y:, w_mid - overlap_pixels_x:]
            ]

            # Panggil fungsi baru untuk memproses setiap tile
            process_tile_similarity(current_image_parts, precomputed_reference_tiles, final_image_parts, weight_map_parts,
                                    tile_size, h, w, h_mid, w_mid, overlap_pixels_y, overlap_pixels_x, motion_threshold, dtype)

        final_image = np.zeros_like(reference_image, dtype=np.float32)
        weight_map = np.zeros_like(reference_image, dtype=np.float32)

        def add_part_with_blending(final_image, weight_map, part, weight_map_part, y_start, y_end, x_start, x_end):
            final_image[y_start:y_end, x_start:x_end] += part
            weight_map[y_start:y_end, x_start:x_end] += weight_map_part[..., np.newaxis]

        add_part_with_blending(final_image, weight_map, final_image_parts[0], weight_map_parts[0], 0, h_mid + overlap_pixels_y, 0, w_mid + overlap_pixels_x)
        add_part_with_blending(final_image, weight_map, final_image_parts[1], weight_map_parts[1], 0, h_mid + overlap_pixels_y, w_mid - overlap_pixels_x, w)
        add_part_with_blending(final_image, weight_map, final_image_parts[2], weight_map_parts[2], h_mid - overlap_pixels_y, h, 0, w_mid + overlap_pixels_x)
        add_part_with_blending(final_image, weight_map, final_image_parts[3], weight_map_parts[3], h_mid - overlap_pixels_y, h, w_mid - overlap_pixels_x, w)

        final_image /= (weight_map + 1e-6)
        final_image = np.clip(final_image, np.iinfo(dtype).min, np.iinfo(dtype).max).astype(dtype)

        print(language_config.SIMILARITY_MNFR_PROCESS_FINISHED)
        return final_image

    
    def normalize_image(self, image, dtype):
        return image.astype(np.float32) / np.iinfo(dtype).max

    def save_image(self, image, output_path):
        cv2.imwrite(output_path, image)
        
def main(db_path, update_progress=None, stop_requested=None, batch_size=5):
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