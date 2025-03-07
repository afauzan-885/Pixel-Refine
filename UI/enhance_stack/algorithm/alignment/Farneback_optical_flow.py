import json
import cv2
import numpy as np
import sqlite3
import os
import concurrent.futures
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py

from PyQt6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import load_images_from_paths
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config

class FarnebackAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        # Pastikan folder HDF5 ada
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

    def get_all_image_paths(self):
        """
        Retrieves all image paths stored in the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]

    # def resize_image(self, image, size):
    #     """
    #     Resizes the image to match the reference image size.
    #     """
    #     return cv2.resize(image, (size[1], size[0]), interpolation=cv2.INTER_LINEAR)

    @staticmethod
    def load_farneback_config(config_filename=None):
        """
        Membaca konfigurasi Farneback Optical Flow dari file JSON.
        Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "pyr_scale": 0.5,
            "levels": 3,
            "winsize": 15,
            "iterations": 3,
            "poly_n": 5,
            "poly_sigma": 1.2,
            "flags": 0,
            "interpolation": "INTER_CUBIC",
            "use_gpu": False
        }

        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("Farneback", default_config)
        except Exception as e:
            print("Error loading Farneback configuration:", e)
            return default_config

    def calculate_optical_flow(self, base_image, target_image, config_filename=None, num_blocks=(2, 2), overlap_ratio=0.3):
        """
        Menghitung optical flow dengan metode paralel berbasis blok, dengan overlap sebagai persentase dari ukuran blok.
        
        Parameter:
        - num_blocks: tuple (blocks_x, blocks_y) -> Jumlah blok dalam sumbu X dan Y.
        - overlap_ratio: Persentase overlap relatif terhadap ukuran blok (contoh: 0.3 untuk 30%).
        """
        fb_config = self.load_farneback_config(config_filename)
        use_gpu = fb_config.get("use_gpu", False)

        # print("Calculating optical flow using" + (" GPU" if use_gpu else " CPU"))

        if use_gpu:
            base_gray = cv2.UMat(cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY))
            target_gray = cv2.UMat(cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY))
        else:
            base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
            target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

        h, w = base_gray.get().shape if use_gpu else base_gray.shape
        blocks_x, blocks_y = num_blocks
        block_w = w // blocks_x
        block_h = h // blocks_y

        flow_full = np.zeros((h, w, 2), dtype=np.float32)

        def compute_block(x, y, bw, bh, overlap_ratio):
            overlap_x = int(bw * overlap_ratio)
            overlap_y = int(bh * overlap_ratio)

            roi_x_start = max(0, x - overlap_x)
            roi_y_start = max(0, y - overlap_y)
            roi_x_end = min(w, x + bw + overlap_x)
            roi_y_end = min(h, y + bh + overlap_y)

            if use_gpu:
                roi_base = base_gray.get()[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
                roi_target = target_gray.get()[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
            else:
                roi_base = base_gray[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
                roi_target = target_gray[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

            flow_roi = cv2.calcOpticalFlowFarneback(
                roi_base, roi_target, None,
                pyr_scale=fb_config["pyr_scale"],
                levels=fb_config["levels"],
                winsize=fb_config["winsize"],
                iterations=fb_config["iterations"],
                poly_n=fb_config["poly_n"],
                poly_sigma=fb_config["poly_sigma"],
                flags=fb_config["flags"]
            )

            offset_x = x - roi_x_start
            offset_y = y - roi_y_start
            flow_block = flow_roi[offset_y:offset_y+bh, offset_x:offset_x+bw, :]

            return (x, y, flow_block)

        with concurrent.futures.ThreadPoolExecutor(max_workers=blocks_x * blocks_y) as executor:
            futures = []
            for i in range(blocks_x):
                for j in range(blocks_y):
                    x = i * block_w
                    y = j * block_h
                    bw = block_w if i < blocks_x - 1 else w - x
                    bh = block_h if j < blocks_y - 1 else h - y
                    futures.append(executor.submit(compute_block, x, y, bw, bh, overlap_ratio))

            for future in concurrent.futures.as_completed(futures):
                x, y, flow_block = future.result()
                h_block, w_block, _ = flow_block.shape
                flow_full[y:y+h_block, x:x+w_block, :] = flow_block

        # print("Optical flow calculation completed." + (" (GPU enabled)" if use_gpu else " (CPU mode)"))
        
        return flow_full

    def compensate_motion(self, base_image_16bit, flow, image_id, config_filename=None):
        print(language_config.COMPENSATE_MOTION_STATUS.format(image_id=image_id))
        h, w = base_image_16bit.shape[:2]
        flow_map = np.stack(np.meshgrid(np.arange(w), np.arange(h)), axis=-1)
        warped_map = flow_map + flow
        remap_x, remap_y = cv2.split(warped_map.astype(np.float32))

        fb_config = self.load_farneback_config(config_filename)
        use_gpu = fb_config.get("use_gpu", False)

        if use_gpu:
            base_image_16bit = cv2.UMat(base_image_16bit)
            remap_x = cv2.UMat(remap_x)
            remap_y = cv2.UMat(remap_y)

        interpolation_str = fb_config.get("interpolation", "INTER_AREA")
        interp_flag = getattr(cv2, interpolation_str, cv2.INTER_AREA)

        compensated_image = cv2.remap(
            base_image_16bit, 
            remap_x, 
            remap_y, 
            interpolation=interp_flag, 
            borderMode=cv2.BORDER_REFLECT
        )

        if use_gpu:
            compensated_image = compensated_image.get()

        print(language_config.COMPENSATE_MOTION_FINISHED.format(image_id=image_id))
        return compensated_image

def main(db_path, update_progress=None, batch_size=5, stop_requested=None):
    processor = FarnebackAlgorithm(db_path)

    # Ambil path gambar dari database
    image_paths = processor.get_all_image_paths()
    if not image_paths:
        print(language_config.RUN_IMAGE_NOT_FOUND)
        return

    # Gunakan gambar pertama sebagai referensi
    base_image_path = image_paths[0]
    base_image = cv2.imread(base_image_path, cv2.IMREAD_UNCHANGED)
    if base_image is None:
        print(language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
        return

    total_images = len(image_paths)
    total_batches = (total_images - 1) // batch_size + 1

    with h5py.File(processor.hdf5_path, "w") as h5f:
        h5f.create_dataset("image_0", data=base_image, compression="gzip")

        for batch_idx in range(total_batches):
            if stop_requested and stop_requested():
                break

            start_idx = batch_idx * batch_size + 1
            end_idx = min((batch_idx + 1) * batch_size + 1, total_images)
            batch_paths = image_paths[start_idx:end_idx]
            batch_images = load_images_from_paths(batch_paths, stop_requested)
            if not batch_images:
                continue

            batch_aligned = []
            for i, target_image in enumerate(batch_images, start=start_idx):
                if stop_requested and stop_requested():
                    # print("Proses dihentikan oleh pengguna.")
                    break

                info_message = language_config.RUN_IMAGE_PROCESSING.format(i=i, total_images=total_images)
                print(info_message)
                if update_progress:
                    update_progress(i - 1, total_images - 1, info_message)

                # Menggunakan metode parallel untuk optical flow pada tiap gambar
                flow = processor.calculate_optical_flow(base_image, target_image)
                compensated_image = processor.compensate_motion(target_image, flow, image_id=i)
                batch_aligned.append(compensated_image)

            for j, aligned_image in enumerate(batch_aligned):
                if aligned_image is not None:
                    h5f.create_dataset(f"image_{start_idx + j}", data=aligned_image)

            # print(f"Batch {batch_idx + 1}/{total_batches} selesai diproses dan disimpan.")
    
    if update_progress:
        update_progress(total_images - 1, total_images - 1, language_config.SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED)

    # print("Pemrosesan selesai dan semua gambar telah disimpan ke HDF5.")

def running_farneback_optical_flow(parent=None):
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_FARNEBACK)
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(
        Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint |
        Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint
    )

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

    worker = ImageProcessingMultiThreading(main, "pixel_refine_database.db")
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
        QMessageBox.critical(dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=error))
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    worker.start()

    def on_dialog_close(event):
        if worker.isRunning():
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

    dialog.closeEvent = on_dialog_close

    dialog.exec()

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"  # Path ke database Anda
    main(db_path)