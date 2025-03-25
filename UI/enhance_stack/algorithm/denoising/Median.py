import subprocess
import cv2
import numpy as np
import sqlite3
import concurrent.futures
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import extract_all_metadata, save_image
from UI.resources.stylesheet.stylesheet import PROGRESS_BAR
from UI.settings.General.Language import language_config

class ThreadWorker(QThread):
    progress_updated = pyqtSignal(int, str)  # Sinyal untuk memperbarui progress
    finished = pyqtSignal()  # Sinyal untuk menandakan selesai
    error_occurred = pyqtSignal(str)  # Sinyal untuk menandakan error

    def __init__(self, db_path, single_process=True, batch_id=None):
        super().__init__()
        self.db_path = db_path
        self.single_process = single_process  # Menentukan apakah proses single atau batch
        self.batch_id = batch_id  # ID batch jika batch processing
        self.stop_requested = False  # Flag untuk menghentikan thread

    def run(self):
        try:
            def update_progress(progress, message):
                self.progress_updated.emit(progress, message)

            # Fungsi callback untuk mengecek status stop
            def is_stop_requested():
                return self.stop_requested

            # Panggil main dengan parameter yang sesuai
            main(
                self.db_path, 
                update_progress=update_progress, 
                stop_requested=is_stop_requested, 
                single_process=self.single_process, 
                batch_id=self.batch_id
            )
            
            self.finished.emit()
        except Exception as e:
            print(f"Error terjadi: {str(e)}")  # Menampilkan pesan error di konsol
            self.error_occurred.emit(str(e))  # Mengirim pesan error melalui sinyal

    def stop(self):
        self.stop_requested = True  # Set flag agar thread berhenti

class MedianAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5", max_workers=None):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        # Pastikan folder HDF5 ada
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

        # Buat executor sekali saja untuk reuse di setiap pemrosesan
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def get_all_image_paths_for_single_process(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT images.path 
                FROM single_process_image
                JOIN images ON single_process_image.image_id_single = images.id
            """)
            return [row[0] for row in cursor.fetchall()]
        
    def get_all_image_paths_for_batch_process(self, batch_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT images.path 
                FROM batch_process_image
                JOIN images ON batch_process_image.image_id_batch = images.id
                WHERE batch_process_image.batch_id = ?
            """, (batch_id,))
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
        image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                       if f.endswith(('.png', '.jpg', '.jpeg'))]
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

    def stack_median_images(self, images, previous_medians, stop_requested=None, block_size=64, overlap=0.3):
        if stop_requested and stop_requested():
            print("Proses dihentikan sebelum menghitung stack median.")
            return previous_medians

        if not images:
            raise ValueError("Tidak ada gambar yang ditemukan.")

        dtype = images[0].dtype
        target_shape = images[0].shape

        # Resize gambar agar semua memiliki ukuran yang sama
        images_resized = self._resize_images(images, target_shape)
        # Proses median dengan metode blok yang dioptimasi
        median_image = self._compute_median_image(images_resized, target_shape, block_size, dtype, overlap)
        return median_image, images_resized

    def _resize_images(self, images, target_shape):
        """
        Resize seluruh gambar agar memiliki ukuran yang sama dengan target_shape.
        """
        resized_images = []
        for image in images:
            resized = cv2.resize(image, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_CUBIC)
            resized_images.append(resized)
        return resized_images

    def stack_median_images(self, images, previous_medians, stop_requested=None, block_size=64, overlap=0.3):
        if stop_requested and stop_requested():
            print("Proses dihentikan sebelum menghitung stack median.")
            return previous_medians

        if not images:
            raise ValueError("Tidak ada gambar yang ditemukan.")

        dtype = images[0].dtype
        target_shape = images[0].shape

        # Resize gambar agar semua memiliki ukuran yang sama
        images_resized = self._resize_images(images, target_shape)
        # Proses median dengan metode blok yang dioptimasi
        median_image = self._compute_median_image(images_resized, target_shape, block_size, dtype, overlap)
        return median_image, images_resized

    def _resize_images(self, images, target_shape):
        """
        Resize seluruh gambar agar memiliki ukuran yang sama dengan target_shape.
        """
        resized_images = []
        for image in images:
            resized = cv2.resize(image, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_CUBIC)
            resized_images.append(resized)
        return resized_images

    def _compute_block_median(self, block_stack):
        """
        Menghitung median dari stack blok secara vectorized.
        """
        return np.median(block_stack, axis=0)

    def _compute_median_image(self, images, target_shape, block_size, dtype, overlap):
        H, W = target_shape[:2]
        accumulator = np.zeros(target_shape, dtype=np.float32)
        weight_sum = np.zeros(target_shape, dtype=np.float32)

        step = max(int(block_size * (1 - overlap)), 1)

        row_starts = list(range(0, H - block_size + 1, step)) + ([H - block_size] if H % block_size != 0 else [])
        col_starts = list(range(0, W - block_size + 1, step)) + ([W - block_size] if W % block_size != 0 else [])

        base_hanning = np.outer(np.hanning(block_size), np.hanning(block_size))

        def process_block(row_start, col_start):
            row_end, col_end = row_start + block_size, col_start + block_size
            
            # Gunakan array view untuk menghindari salinan baru
            blocks = np.stack([im[row_start:row_end, col_start:col_end] for im in images], axis=0)

            # Gunakan fungsi _compute_block_median untuk menghitung median
            block_median = self._compute_block_median(blocks)
  

            # Hindari alokasi array baru untuk Hanning window
            hanning_win = base_hanning
            if blocks.shape[1:3] != (block_size, block_size):
                hanning_win = np.outer(np.hanning(row_end - row_start), np.hanning(col_end - col_start))

            if len(target_shape) == 3:
                hanning_win = hanning_win[..., np.newaxis]

            return row_start, row_end, col_start, col_end, block_median * hanning_win, hanning_win

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_block, r, c): (r, c) for r in row_starts for c in col_starts}

            for future in concurrent.futures.as_completed(futures):
                row_start, row_end, col_start, col_end, weighted_block, hanning_win = future.result()
                accumulator[row_start:row_end, col_start:col_end] += weighted_block
                weight_sum[row_start:row_end, col_start:col_end] += hanning_win

        with np.errstate(divide='ignore', invalid='ignore'):
            median_image = np.true_divide(accumulator, weight_sum)
            median_image[weight_sum == 0] = 0

        return np.clip(median_image, np.iinfo(dtype).min, np.iinfo(dtype).max).astype(dtype) if np.issubdtype(dtype, np.integer) else median_image.astype(dtype)
    
def main(db_path, update_progress=None, stop_requested=None, batch_size=4, single_process=None, batch_id=None):
    try:
        image_processor = MedianAlgorithm(db_path)
        
        # Pilih sumber image_paths
        if single_process:
            image_paths = image_processor.get_all_image_paths_for_single_process()
        else:
            if batch_id is None:
                raise ValueError("batch_id harus diberikan untuk batch process")
            image_paths = image_processor.get_all_image_paths_for_batch_process(batch_id)
        
        if not image_paths:
            if update_progress:
                update_progress(0, language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
            return
        
        # Ekstrak metadata dari seluruh gambar dan simpan ke file JSON
        metadata_folder = os.path.join("database", "align")
        os.makedirs(metadata_folder, exist_ok=True)
        metadata_file = os.path.join(metadata_folder, "metadata.json")
        extract_all_metadata(image_paths, metadata_file=metadata_file)

        reference_image_path = image_paths[0]
        reference_image_name = os.path.splitext(os.path.basename(reference_image_path))[0]
        output_path = f"database/stack/{reference_image_name}_median_stack.tiff"

        if update_progress:
            update_progress(0, language_config.WINDOW_START_PROCESSING)

        global_hdf5_path = "database/align/aligned_images.h5"
        total_images = len(image_paths)
        total_batches = (total_images + batch_size - 1) // batch_size
        processed_images = 0

        # List untuk menyimpan hasil median tiap batch
        batch_medians = []

        if os.path.exists(global_hdf5_path):
            with h5py.File(global_hdf5_path, 'r') as h5f:
                for batch_idx in range(total_batches):
                    if stop_requested and stop_requested():
                        # print("Proses dihentikan oleh pengguna.")
                        break

                    batch_keys = list(h5f.keys())[batch_idx * batch_size:(batch_idx + 1) * batch_size]
                    batch_images = [np.array(h5f[key]) for key in batch_keys]

                    # Proses median untuk batch ini
                    batch_median, _ = image_processor.stack_median_images(
                        batch_images, None, stop_requested
                    )
                    batch_medians.append(batch_median)

                    processed_images += len(batch_images)
                    progress = int((processed_images / total_images) * 100)
                    message = language_config.STACK_IMAGES_PROCESS.format(
                        current=processed_images, total=total_images)
                    if update_progress:
                        update_progress(progress, message)
        else:
            for batch_idx in range(total_batches):
                if stop_requested and stop_requested():
                    # print("Proses dihentikan oleh pengguna.")
                    break

                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, total_images)
                batch_paths = image_paths[start_idx:end_idx]

                batch_images = []
                for path in batch_paths:
                    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                    if image is not None:
                        batch_images.append(image)

                # Proses median untuk batch ini
                batch_median, _ = image_processor.stack_median_images(
                    batch_images, None, stop_requested
                )
                batch_medians.append(batch_median)

                processed_images += len(batch_images)
                progress = int((processed_images / total_images) * 100)
                message = language_config.STACK_IMAGES_PROCESS.format(
                    current=processed_images, total=total_images)
                if update_progress:
                    update_progress(progress, message)

        if batch_medians:
            # Proses ulang dengan menggabungkan semua median batch
            final_median, _ = image_processor.stack_median_images(
                batch_medians, None, stop_requested
            )
        else:
            final_median = None

        # Simpan gambar median akhir
        if final_median is not None:
            final_result = final_median.astype(np.uint16)
            save_image(final_result, output_path, reference_image_path=reference_image_path)
            # if update_progress:
            #     update_progress(100, f"Proses selesai, hasil disimpan di {output_path}")
        else:
            if update_progress:
                update_progress(0, language_config.RUN_ERROR_MESSAGE.format(error=str(e)))

    except Exception as e:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        if update_progress:
            update_progress(0, error_message)
        print(language_config.RUN_ERROR_MESSAGE.format(error=str(e)))
       
def running_median(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_MEDIAN)
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
    worker = ThreadWorker("pixel_refine_database.db", single_process=single_process, batch_id=batch_id)
    # Menghubungkan signal worker ke fungsi pembaruan UI
    worker.progress_updated.connect(lambda progress, message: (
        progress_bar.setValue(progress),
        label.setText(message)
    ))

    def finish_handler():
        nonlocal process_finished
        process_finished = True  # set flag ketika proses selesai
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

    def on_dialog_close(event):
        # Jika proses telah selesai, lewati konfirmasi
        if process_finished:
            event.accept()
        elif worker.isRunning():
            reply = QMessageBox.question(dialog, "Cancel Process",
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
        else:
            event.accept()

    dialog.closeEvent = on_dialog_close
    worker.start()
    dialog.exec()

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"  # Path ke database Anda
    main(db_path)
