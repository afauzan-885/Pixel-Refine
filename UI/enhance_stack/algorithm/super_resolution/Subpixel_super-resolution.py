import cv2
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import QThread, pyqtSignal, Qt
import tensorflow as tf
from tensorflow.keras.layers import Conv2D, Lambda, Input
from tensorflow.keras.models import Model

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

            # Jalankan proses ORB dengan callback
            main(self.db_path, update_progress, stop_requested=is_stop_requested)
            self.finished.emit()
        except Exception as e:
            print(f"Error terjadi: {str(e)}")  # Menampilkan pesan error di konsol
            self.error_occurred.emit(str(e))  # Mengirim pesan error melalui sinyal


    def stop(self):
        self.stop_requested = True  # Set flag agar thread berhenti

class InterpolationAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path
        self.espcn_model = self.build_espcn_model(scale=2)  # Inisialisasi model ESPCN

        # Pastikan folder HDF5 ada
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

    def build_espcn_model(self, scale=2):
        """
        Membangun model ESPCN untuk super-resolution.
        """
        inputs = Input(shape=(None, None, 3))  # Input gambar dengan 3 channel (RGB)
        
        # Lapisan konvolusi untuk ekstraksi fitur
        x = Conv2D(64, (5, 5), padding='same', activation='relu')(inputs)
        x = Conv2D(64, (3, 3), padding='same', activation='relu')(x)
        
        # Lapisan konvolusi untuk menghasilkan channel * scale^2
        x = Conv2D(3 * (scale ** 2), (3, 3), padding='same', activation='relu')(x)
        
        # Subpixel convolution layer untuk meningkatkan resolusi
        x = Lambda(lambda x: tf.nn.depth_to_space(x, scale))(x)
        
        model = Model(inputs, x)
        return model

    def get_all_image_paths(self):
        """
        Mengambil semua path gambar dari database SQLite.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]

    def load_images_from_hdf5(self, hdf5_path, stop_requested=None):
        """
        Memuat gambar dari file HDF5.
        """
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                if stop_requested and stop_requested():  # Cek apakah harus berhenti
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images

    def load_images_from_folder(self, folder_path):
        """
        Memuat gambar dari folder.
        """
        image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        return self.load_images_from_paths(image_paths)

    def load_images_from_paths(self, image_paths, stop_requested=None):
        """
        Memuat gambar dari daftar path.
        """
        images = []
        for image_path in image_paths:
            if stop_requested and stop_requested():  # Cek apakah harus berhenti
                break
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if image is not None:
                images.append(image)
        return images

    def upsample_image(self, image, scale=2):
        """
        Menggantikan upsampling tradisional dengan model ESPCN.
        """
        # Pastikan gambar dalam format yang benar (3 channel, RGB)
        if len(image.shape) == 2:  # Jika gambar grayscale
            image = np.stack((image,) * 3, axis=-1)  # Konversi ke RGB
        elif image.shape[2] == 1:  # Jika gambar single-channel
            image = np.repeat(image, 3, axis=-1)  # Konversi ke RGB

        # Normalisasi gambar ke range [0, 1]
        image = image.astype(np.float32) / 255.0

        # Tambahkan dimensi batch (model membutuhkan input dengan bentuk [batch, height, width, channels])
        image = np.expand_dims(image, axis=0)

        # Lakukan prediksi dengan model ESPCN
        upsampled_image = self.espcn_model.predict(image)

        # Hapus dimensi batch dan kembalikan ke range [0, 255]
        upsampled_image = np.squeeze(upsampled_image, axis=0)
        upsampled_image = (upsampled_image * 255.0).astype(np.uint8)

        return upsampled_image

    def stack_average_images(self, images, accumulated_image, total_weights, reference_image, stop_requested=None):
        """
        Menghasilkan gambar rata-rata dari kumpulan gambar.
        """
        if stop_requested and stop_requested():
            return accumulated_image, total_weights

        if len(images) == 0:
            raise ValueError("Tidak ada gambar yang ditemukan.")

        if accumulated_image is None:
            accumulated_image = np.zeros_like(images[0], dtype=np.float32)  # Gunakan resolusi asli

        for image in images:
            if image is None:
                continue

            if stop_requested and stop_requested():  
                break

            # Proses akumulasi tanpa upsampling
            accumulated_image += image.astype(np.float32)
            total_weights += 1

        return accumulated_image, total_weights

    def process_final_image(self, accumulated_image, total_weights, dtype=np.uint16):
        """
        Memproses gambar akhir dari akumulasi.
        """
        if accumulated_image is None or total_weights <= 0:
            raise ValueError("Accumulated image is None atau total weights tidak valid.")
        
        normalized_image = accumulated_image / total_weights
        
        image_min = np.iinfo(dtype).min
        image_max = np.iinfo(dtype).max
        
        final_image = np.clip(normalized_image, image_min, image_max)
        
        final_image = final_image.astype(dtype)
        
        return final_image

    def save_image(self, image, output_path):
        """
        Menyimpan gambar ke path yang ditentukan.
        """
        cv2.imwrite(output_path, image)

def main(db_path, update_progress=None, stop_requested=None, batch_size=3):
    """
    Fungsi utama untuk memproses gambar.
    """
    try:
        image_processor = InterpolationAlgorithm(db_path)
        image_paths = image_processor.get_all_image_paths()
        if not image_paths:
            if update_progress:
                update_progress(0, language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
            return

        reference_image_path = image_paths[0]
        reference_image_name = os.path.splitext(os.path.basename(reference_image_path))[0]
        output_path = f"database/stack/{reference_image_name}_interpolation_stack.tif"

        if update_progress:
            update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        global_hdf5_path = "database/align/aligned_images.h5"
        accumulated_image = None
        total_weights = 0

        total_images = len(image_paths) if not os.path.exists(global_hdf5_path) else len(h5py.File(global_hdf5_path, 'r').keys())
        processed_images = 0

        if os.path.exists(global_hdf5_path):
            with h5py.File(global_hdf5_path, 'r') as h5f:
                total_batches = (total_images + batch_size - 1) // batch_size

                for batch_idx in range(total_batches):
                    if stop_requested and stop_requested():
                        break

                    batch_keys = list(h5f.keys())[batch_idx * batch_size:(batch_idx + 1) * batch_size]
                    batch_images = [np.array(h5f[key]) for key in batch_keys]

                    if batch_idx == 0:
                        reference_image = batch_images[0]

                    accumulated_image, total_weights = image_processor.stack_average_images(
                        batch_images, accumulated_image, total_weights, reference_image, stop_requested
                    )

                    for i in range(len(batch_images)):
                        processed_images += 1
                        progress = int((processed_images / total_images) * 100)
                        message = language_config.STACK_AVERAGE_IMAGES_PROCESS.format(current=processed_images, total=total_images)
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
                    message = language_config.STACK_AVERAGE_IMAGES_PROCESS.format(current=processed_images, total=total_images)
                    if update_progress:
                        update_progress(progress, message)

        if accumulated_image is not None:
            try:
                final_image = image_processor.process_final_image(accumulated_image, total_weights)

                # Gunakan model ESPCN untuk upsampling
                upsampled_image = image_processor.upsample_image(final_image)

                image_processor.save_image(upsampled_image, output_path)
                if update_progress:
                    update_progress(100, f"Proses selesai, hasil disimpan di {output_path}")
            except ValueError as e:
                if update_progress:
                    update_progress(0, f"Gagal memproses gambar: {str(e)}")
                print(language_config.RUN_ERROR_STATUS.format(error=str(e)))

        else:
            if update_progress:
                update_progress(0, "Gagal melakukan stack gambar.")
    except Exception as e:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        if update_progress:
            update_progress(0, error_message)
        print(language_config.RUN_ERROR_STATUS.format(error=str(e)))

def running_interpolation(parent=None):
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_INTERPOLATION)
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
        worker.quit()
        worker.wait()

    worker.finished.connect(finish_handler)

    def error_handler(error):
        
        # messages: An error occurred
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
