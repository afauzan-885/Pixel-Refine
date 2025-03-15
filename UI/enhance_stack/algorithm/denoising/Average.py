import subprocess
import cv2
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import QThread, pyqtSignal, Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import extract_all_metadata, load_images_from_paths
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.resources.stylesheet.stylesheet import PROGRESS_BAR
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
        return load_images_from_paths(image_paths)

    def stack_average_images(self, images, accumulated_image, total_weights, reference_image, stop_requested=None):
        if stop_requested and stop_requested():  # Cek penghentian
            print("Proses dihentikan sebelum menghitung gerakan global.")
            return accumulated_image, total_weights

        if len(images) == 0:
            raise ValueError("Tidak ada gambar yang ditemukan.")

        dtype = images[0].dtype
        if accumulated_image is None:
            accumulated_image = np.zeros_like(images[0], dtype=np.float32)

        for i, image in enumerate(images):
            if image is None:
                continue

            if stop_requested and stop_requested():  # Cek penghentian
                print("Proses dihentikan saat menghitung stack.")
                break

            # Gunakan gambar referensi untuk perhitungan
            current_image = image.astype(np.float32)
            accumulated_image += current_image
            total_weights += 1

        return accumulated_image, total_weights

    
    def process_final_image(self, accumulated_image, total_weights, dtype=np.uint16):
        if accumulated_image is None or total_weights <= 0:
            raise ValueError("Accumulated image is None atau total weights tidak valid.")
        
        # Normalisasi
        normalized_image = accumulated_image / total_weights
        
        # Mendapatkan rentang nilai untuk tipe data
        image_min = np.iinfo(dtype).min
        image_max = np.iinfo(dtype).max
        
        # Normalisasi ke rentang tipe data yang sesuai
        final_image = np.clip(normalized_image, image_min, image_max)
        
        # Mengonversi ke tipe data yang diinginkan
        final_image = final_image.astype(dtype)
        
        return final_image
    
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
        
def main(db_path, update_progress=None, stop_requested=None, batch_size=10):
    try:
        image_processor = AverageAlgorithm(db_path)
        image_paths = image_processor.get_all_image_paths()
        if not image_paths:
            if update_progress:
                update_progress(0, language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
            return
        
        # Ekstrak metadata dari seluruh gambar dan simpan ke file JSON
        metadata_folder = os.path.join("database", "align")
        os.makedirs(metadata_folder, exist_ok=True)
        metadata_file = os.path.join(metadata_folder, "metadata.json")
        extract_all_metadata(image_paths, metadata_file=metadata_file)

        # Gunakan gambar pertama sebagai gambar referensi
        reference_image_path = image_paths[0]
        reference_image_name = os.path.splitext(os.path.basename(reference_image_path))[0]
        output_path = f"database/stack/{reference_image_name}_average_stack.tif"

        if update_progress:
            update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        global_hdf5_path = "database/align/aligned_images.h5"
        accumulated_image = None
        total_weights = 0

        # Jika file HDF5 sudah ada, hitung jumlah gambar dari sana,
        # jika tidak, gunakan jumlah image_paths
        if os.path.exists(global_hdf5_path):
            with h5py.File(global_hdf5_path, 'r') as h5f:
                total_images = len(list(h5f.keys()))
        else:
            total_images = len(image_paths)
        processed_images = 0  # counter untuk gambar yang diproses

        if os.path.exists(global_hdf5_path):
            with h5py.File(global_hdf5_path, 'r') as h5f:
                total_batches = (total_images + batch_size - 1) // batch_size

                for batch_idx in range(total_batches):
                    if stop_requested and stop_requested():
                        break

                    batch_keys = list(h5f.keys())[batch_idx * batch_size:(batch_idx + 1) * batch_size]
                    batch_images = [np.array(h5f[key]) for key in batch_keys]

                    # Gunakan gambar pertama dari batch pertama sebagai referensi
                    if batch_idx == 0:
                        reference_image = batch_images[0]

                    accumulated_image, total_weights = image_processor.stack_average_images(
                        batch_images, accumulated_image, total_weights, reference_image, stop_requested
                    )

                    # Update progress per gambar
                    for i in range(len(batch_images)):
                        processed_images += 1
                        progress = int((processed_images / total_images) * 100)
                        message = language_config.STACK_IMAGES_PROCESS.format(current=processed_images, total=total_images)
                        if update_progress:
                            update_progress(progress, message)

        else:
            total_batches = (total_images + batch_size - 1) // batch_size
            for batch_idx in range(total_batches):
                if stop_requested and stop_requested():
                    break

                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, total_images)
                batch_paths = image_paths[start_idx:end_idx]

                batch_images = []
                for path in batch_paths:
                    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                    if image is not None:
                        batch_images.append(image)

                if batch_idx == 0:
                    reference_image = batch_images[0]

                accumulated_image, total_weights = image_processor.stack_average_images(
                    batch_images, accumulated_image, total_weights, reference_image, stop_requested
                )

                for i in range(len(batch_images)):
                    processed_images += 1
                    progress = int((processed_images / total_images) * 100)
                    message = language_config.STACK_IMAGES_PROCESS.format(current=processed_images, total=total_images)
                    if update_progress:
                        update_progress(progress, message)

        if accumulated_image is not None:
            try:
                final_result = image_processor.process_final_image(accumulated_image, total_weights)
                # Saat menyimpan gambar akhir, kembalikan metadata dari gambar referensi
                image_processor.save_image(final_result, output_path, reference_image_path=reference_image_path)
                if update_progress:
                    update_progress(100, f"Proses selesai, hasil disimpan di {output_path}")
            except ValueError as e:
                if update_progress:
                    update_progress(0, f"Gagal memproses gambar: {str(e)}")
                print(f"Error: {str(e)}")
        else:
            if update_progress:
                update_progress(0, "Gagal melakukan stack gambar.")
    except Exception as e:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        if update_progress:
            update_progress(0, error_message)
        print(f"Error encountered: {str(e)}")

def running_average(parent=None):
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_AVERAGE)
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
