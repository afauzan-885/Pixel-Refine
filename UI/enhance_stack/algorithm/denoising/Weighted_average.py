import cProfile
import subprocess
import cv2
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import QThread, pyqtSignal, Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import extract_all_metadata, load_images_from_paths
from UI.enhance_stack.algorithm.denoising.extra_similarity.extra_algorithm import call_weighted_average_motion
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

class WeightedAverageAlgorithm:
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
        return load_images_from_paths(image_paths)

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
        return window
    
    def weighted_average(self, images, tile_size=(64, 64), overlap=0.3,
                     motion_threshold=0.0001, update_progress=None, stop_requested=None,
                     lib_path='UI/data/weighted_average_motion.dll'):
        """
        Fungsi untuk menghitung multi-frame noise reduction dengan referensi citra pertama.
        """
        if not images:
            raise ValueError("Gagal memuat citra referensi.")

        dtype = images[0].dtype
        if dtype not in (np.uint8, np.uint16):
            raise TypeError("Tipe citra harus uint8 atau uint16.")

        # Normalisasi citra referensi
        reference_image = self.normalize_image(images[0], dtype)
        h, w, channels = reference_image.shape

        # Menghitung step berdasarkan overlap dan ukuran tile
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
                message = f"Processing image {i+1} of {num_images}"
                update_progress(progress, message)

            if stop_requested and stop_requested():
                break

            current_image = self.normalize_image(image, dtype)
            if current_image.shape != reference_image.shape:
                raise ValueError(f"Image size {i+1} does not match.")

            # Konversi row dan col starts ke numpy array
            row_starts_arr = np.array(row_starts, dtype=np.int32)
            col_starts_arr = np.array(col_starts, dtype=np.int32)

            # Panggil fungsi dari library C++ (tanpa noise_threshold)
            call_weighted_average_motion(
                final_image, weight_map,
                current_image, reference_image,
                base_window,
                row_starts_arr, col_starts_arr,
                tile_size[0], tile_size[1],
                h, w, channels,
                motion_threshold, scale, 0.8, 50, 1e-3,
                lib_path
            )

        # Normalisasi dan kliping hasil akhir
        final_image /= (weight_map[..., np.newaxis] + 1e-3)
        final_image = np.clip(final_image, np.iinfo(dtype).min, np.iinfo(dtype).max).astype(dtype, copy=False)

        return final_image

    def normalize_image(self, image, dtype):
        # Konversi ke float32 dan pastikan array contiguous
        image_float = np.ascontiguousarray(image.astype(np.float32))
        norm_image = (image_float - image_float.min()) / (image_float.max() - image_float.min() + 1e-6)
        if len(image.shape) == 2:
            norm_image = np.stack((norm_image,)*3, axis=-1)
        return norm_image.astype(np.float32)


    def save_image(self, image, output_path, reference_image_path=None):
        """
        Menyimpan gambar ke output_path dengan cv2.imwrite, lalu 
        mengembalikan metadata dari gambar referensi (reference_image_path) ke file yang disimpan.
        
        Parameter:
        - image: array gambar yang akan disimpan
        - output_path: path file output (misalnya, TIFF)
        - reference_image_path: path gambar referensi untuk penyalinan metadata
        """
        # Simpan gambar menggunakan OpenCV
        cv2.imwrite(output_path, image)
        
        # Jika reference_image_path disediakan, gunakan exiftool untuk mengembalikan metadata
        if reference_image_path is not None and os.path.exists(reference_image_path):
            try:
                subprocess.run(
                    ["exiftool", "-overwrite_original", "-TagsFromFile", reference_image_path, output_path],
                    check=True
                )
                print(f"Metadata berhasil dikembalikan dari {reference_image_path} ke {output_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error saat mengembalikan metadata ke {output_path}: {e}")
        return output_path
        
def main(db_path, update_progress=None, stop_requested=None, batch_size=8):
    try:
        image_processor = WeightedAverageAlgorithm(db_path)
        image_paths = image_processor.get_all_image_paths()
        if not image_paths:
            if update_progress:
                update_progress(0, language_config.RUN_IMAGE_PROCESS_LOAD_FAILED)
            return
        
        # Ekstrak metadata dari seluruh gambar dan simpan ke file JSON
        metadata_folder = os.path.join("database", "align")
        os.makedirs(metadata_folder, exist_ok=True)
        metadata_file = os.path.join(metadata_folder, "metadata.json")
        extract_all_metadata(image_paths, metadata_file=metadata_file)

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
                    batch_result = image_processor.weighted_average(batch_images, update_progress=update_progress, stop_requested=stop_requested)
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
                batch_result = image_processor.weighted_average(batch_images, update_progress=update_progress, stop_requested=stop_requested)
                processed_batches.append(batch_result)

                progress = int(((batch_start + len(batch_paths)) / total_images) * 100)
                if update_progress:
                    update_progress(progress, language_config.RUN_IMAGE_PROCESS_BATCH_PROGRESS.format(
                        current=batch_start + len(batch_paths), total=total_images
                    ))

        if processed_batches:
            # Proses fine-tuning dari semua hasil batch
            final_result = image_processor.weighted_average(processed_batches, update_progress=update_progress, stop_requested=stop_requested)

            # Simpan hasil akhir
            image_processor.save_image(final_result, output_path, reference_image_path=reference_image_path)

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


def running_weighted_average(parent=None):
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_WEIGHTED_AVERAGE)
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