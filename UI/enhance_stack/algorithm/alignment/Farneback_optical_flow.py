import json
import time
import cv2
import numpy as np
import sqlite3
import os
import concurrent.futures
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py

from PyQt6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import extract_all_metadata, extract_exif, load_images_from_paths, save_to_hdf5
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config
from concurrent.futures import ThreadPoolExecutor

class FarnebackAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        # Pastikan folder HDF5 ada
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

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
            "use_gpu": True
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
    def load_farneback_config_for_batch(config_filename=None):
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
            "interpolation": "INTER_LANCZOS4",
            "use_gpu": False
        }

        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("Farneback_BATCH", default_config)
        except Exception as e:
            print("Error loading Farneback configuration:", e)
            return default_config

    # --- Fungsi Optical Flow (dengan logika CPU/GPU terpisah) ---
    def calculate_optical_flow(self, base_image, target_image, config_filename=None, stop_requested=None):
        """
        Menghitung optical flow Farneback.
        - Mode GPU: Memproses gambar penuh menggunakan UMat.
        - Mode CPU: Memproses secara paralel berbasis blok dengan overlap.
        """
        if stop_requested and stop_requested():
            print("Proses optical flow dihentikan.")
            return None

        start_time = time.time()
        fb_config = self.load_farneback_config(config_filename)
        use_gpu = fb_config.get("use_gpu", False) and cv2.ocl.haveOpenCL()

        print(f"Calculating dense optical flow using Farneback ({'GPU' if use_gpu else 'CPU Parallel Blocks'})...")

        try:
            # --- Persiapan Gambar Grayscale (Selalu uint8) ---
            # (Logika konversi sama seperti sebelumnya)
            if base_image.ndim == 3: base_gray_8bit = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
            elif base_image.ndim == 2 and base_image.dtype != np.uint8: base_gray_8bit = cv2.normalize(base_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            elif base_image.ndim == 2 and base_image.dtype == np.uint8: base_gray_8bit = base_image
            else: raise ValueError("Base image invalid.")

            if target_image.ndim == 3: target_gray_8bit = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
            elif target_image.ndim == 2 and target_image.dtype != np.uint8: target_gray_8bit = cv2.normalize(target_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            elif target_image.ndim == 2 and target_image.dtype == np.uint8: target_gray_8bit = target_image
            else: raise ValueError("Target image invalid.")
            # -------------------------------------------------

            h, w = base_gray_8bit.shape
            flow_full = None # Inisialisasi

            # --- === JALUR EKSEKUSI GPU === ---
            if use_gpu:
                print("GPU Path: Uploading images to UMat...")
                try:
                    base_gray_umat = cv2.UMat(base_gray_8bit)
                    target_gray_umat = cv2.UMat(target_gray_8bit)
                    print("GPU Path: Running Farneback on UMat...")
                    flow_umat = cv2.calcOpticalFlowFarneback(
                        base_gray_umat, target_gray_umat, None,
                        pyr_scale=fb_config["pyr_scale"], levels=fb_config["levels"],
                        winsize=fb_config["winsize"], iterations=fb_config["iterations"],
                        poly_n=fb_config["poly_n"], poly_sigma=fb_config["poly_sigma"],
                        flags=fb_config["flags"]
                    )
                    print("GPU Path: Downloading flow field...")
                    flow_full = flow_umat.get()
                except cv2.error as gpu_err:
                     print(f"GPU Farneback error: {gpu_err}. Will attempt CPU fallback.")
                     use_gpu = False # Set flag untuk fallback
                     # Hapus UMat untuk membebaskan memori GPU
                     try: del base_gray_umat, target_gray_umat, flow_umat
                     except NameError: pass
                except Exception as gpu_exc:
                     print(f"Unexpected GPU error: {gpu_exc}. Will attempt CPU fallback.")
                     use_gpu = False
            # --- === AKHIR JALUR GPU === ---

            # --- === JALUR EKSEKUSI CPU (Paralel Blok atau Fallback GPU) === ---
            if not use_gpu:
                print("CPU Path: Using parallel block processing...")
                # Ambil parameter blok dari config
                num_blocks = fb_config.get("cpu_num_blocks", (2, 2))
                overlap_ratio = fb_config.get("cpu_overlap_ratio", 0.3)
                blocks_x, blocks_y = num_blocks
                block_w = w // blocks_x
                block_h = h // blocks_y

                # Buat array hasil di CPU
                flow_full_cpu = np.zeros((h, w, 2), dtype=np.float32)

                # Fungsi worker untuk CPU (mirip kode lama Anda)
                def compute_block_cpu(x, y, bw, bh, overlap_ratio):
                    overlap_x = int(bw * overlap_ratio)
                    overlap_y = int(bh * overlap_ratio)
                    roi_x_start = max(0, x - overlap_x)
                    roi_y_start = max(0, y - overlap_y)
                    roi_x_end = min(w, x + bw + overlap_x)
                    roi_y_end = min(h, y + bh + overlap_y)

                    if roi_y_end <= roi_y_start or roi_x_end <= roi_x_start: return None

                    # Slicing langsung dari array NumPy CPU
                    roi_base = base_gray_8bit[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
                    roi_target = target_gray_8bit[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

                    try:
                        flow_roi = cv2.calcOpticalFlowFarneback(
                            roi_base, roi_target, None,
                            pyr_scale=fb_config["pyr_scale"], levels=fb_config["levels"],
                            winsize=fb_config["winsize"], iterations=fb_config["iterations"],
                            poly_n=fb_config["poly_n"], poly_sigma=fb_config["poly_sigma"],
                            flags=fb_config["flags"]
                        )
                        # Crop bagian tengah flow_roi yang sesuai dengan blok asli (tanpa overlap)
                        offset_x = x - roi_x_start
                        offset_y = y - roi_y_start
                        # Pastikan dimensi crop valid
                        if offset_y+bh > flow_roi.shape[0] or offset_x+bw > flow_roi.shape[1]:
                             print(f"Warning: Crop dimension error for block ({x},{y}). ROI shape {flow_roi.shape}, offset ({offset_x},{offset_y}), block size ({bw},{bh})")
                             # Ambil bagian yang valid saja
                             bh_valid = min(bh, flow_roi.shape[0] - offset_y)
                             bw_valid = min(bw, flow_roi.shape[1] - offset_x)
                             if bh_valid <= 0 or bw_valid <= 0 : return None # Tidak ada bagian valid
                             flow_block = flow_roi[offset_y:offset_y+bh_valid, offset_x:offset_x+bw_valid, :]
                             # Perlu penanganan khusus saat menempatkan kembali ke flow_full_cpu jika ukuran tidak pas
                             # Untuk sementara, lewati blok ini jika ukuran tidak pas
                             if flow_block.shape[0] != bh or flow_block.shape[1] != bw:
                                 print(f"Warning: Skipping block ({x},{y}) due to size mismatch after cropping.")
                                 return None
                        else:
                            flow_block = flow_roi[offset_y:offset_y+bh, offset_x:offset_x+bw, :]

                        # Kembalikan posisi (x,y) dan hasil flow untuk blok ini
                        return (x, y, flow_block)
                    except cv2.error as cv_err:
                        print(f"OpenCV error in compute_block_cpu ({x},{y}): {cv_err}")
                        return None
                    except Exception as exc:
                        print(f"Unexpected error in compute_block_cpu ({x},{y}): {exc}")
                        return None
                # --- Akhir fungsi worker CPU ---

                futures_cpu = []
                # Gunakan seluruh core yang tersedia pada CPU
                num_workers = max(1, os.cpu_count())  # Gunakan semua core yang tersedia
                print(f"CPU Path: Submitting {blocks_x * blocks_y} blocks to ThreadPoolExecutor (max_workers={num_workers})...")
                with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                    for i in range(blocks_x):
                        for j in range(blocks_y):
                            if stop_requested and stop_requested():
                                print("CPU Path: Stop requested during task submission.")
                                for f in futures_cpu: f.cancel()
                                executor.shutdown(wait=False, cancel_futures=True)
                                return None # Keluar

                            x = i * block_w
                            y = j * block_h
                            bw = block_w if i < blocks_x - 1 else w - x
                            bh = block_h if j < blocks_y - 1 else h - y
                            futures_cpu.append(executor.submit(compute_block_cpu, x, y, bw, bh, overlap_ratio))

                    processed_count_cpu = 0
                    for future in concurrent.futures.as_completed(futures_cpu):
                        if stop_requested and stop_requested():
                            print("CPU Path: Stop requested while processing results.")
                            for f in futures_cpu: f.cancel()
                            return None # Keluar

                        try:
                            result_block = future.result()
                            processed_count_cpu += 1
                            if result_block: # Jika tidak None
                                x, y, flow_block = result_block
                                h_block, w_block, _ = flow_block.shape
                                # Tempatkan hasil blok ke array penuh
                                # Pastikan penempatan tidak keluar batas (meskipun sudah ada cek di worker)
                                y_end = min(y + h_block, h)
                                x_end = min(x + w_block, w)
                                flow_full_cpu[y:y_end, x:x_end, :] = flow_block[0:y_end-y, 0:x_end-x, :] # Slicing defensif
                        except concurrent.futures.CancelledError:
                             print("CPU Path: A block task was cancelled.")
                        except Exception as exc:
                             print(f'CPU Path: Block processing generated an exception: {exc}')
                # Setelah loop, tetapkan hasil CPU ke variabel utama
                flow_full = flow_full_cpu
            # --- === AKHIR JALUR CPU === ---

            end_time = time.time()
            print(f"Optical flow calculation completed in {end_time - start_time:.2f} seconds.")
            return flow_full # Kembalikan hasil (dari GPU atau CPU)

        except ValueError as ve:
             print(f"Error preparing images: {ve}")
             return None
        except Exception as e:
             print(f"Unexpected error in calculate_optical_flow: {e}")
             return None

    # --- Fungsi Kompensasi Gerakan (Sudah Cukup Baik, Sedikit Refinement) ---
    def compensate_motion(self, base_image_input, flow, image_id=0, config_filename=None): # image_id default
        """
        Menerapkan kompensasi gerakan menggunakan cv2.remap berdasarkan flow field.
        Mendukung input CPU (NumPy) atau GPU (UMat) untuk remap jika diaktifkan.
        """
        if flow is None:
             print(f"Error for image {image_id}: Input flow field is None. Cannot compensate motion.")
             return None
        if base_image_input is None:
             print(f"Error for image {image_id}: Input base_image is None. Cannot compensate motion.")
             return None

        # Pesan status bisa dipindah ke pemanggil jika perlu
        # print(language_config.COMPENSATE_MOTION_STATUS.format(image_id=image_id))
        start_time = time.time()

        try:
            # Cek shape flow
            if not (isinstance(flow, np.ndarray) and flow.ndim == 3 and flow.shape[2] == 2):
                 raise ValueError(f"Invalid flow field shape: {flow.shape}. Expected (h, w, 2).")

            h, w = flow.shape[:2]

            # Cek shape base_image (hanya dimensi, tipe data bisa bervariasi)
            if base_image_input.shape[0] != h or base_image_input.shape[1] != w:
                 raise ValueError(f"Base image shape {base_image_input.shape[:2]} mismatch with flow field shape {flow.shape[:2]}.")

            # --- Buat Peta Remap (di CPU, karena flow selalu NumPy) ---
            # Meshgrid menghasilkan HxW, perlu transpose jika ingin WxH atau perhatikan axis
            grid_y, grid_x = np.mgrid[0:h, 0:w] # grid_y shape (h, w), grid_x shape (h, w)
            # Perhitungan map: x_baru = x_lama + flow_x, y_baru = y_lama + flow_y
            # remap membutuhkan map x dan map y terpisah
            remap_x = (grid_x + flow[:, :, 0]).astype(np.float32)
            remap_y = (grid_y + flow[:, :, 1]).astype(np.float32)
            # -----------------------------------------------------------

            fb_config = self.load_farneback_config(config_filename)
            use_gpu = fb_config.get("use_gpu", False) and cv2.ocl.haveOpenCL()
            interpolation_str = fb_config.get("interpolation", "INTER_LINEAR") # Ubah default ke INTER_LINEAR
            # Ambil flag interpolasi dari cv2, fallback ke INTER_LINEAR jika tidak valid
            interp_flag = getattr(cv2, interpolation_str, cv2.INTER_LINEAR)

            print(f"Remapping image {image_id} using {'GPU' if use_gpu else 'CPU'} with interpolation {interpolation_str}...")

            # --- Operasi Remap (CPU atau GPU) ---
            compensated_image = None # Inisialisasi
            if use_gpu:
                try:
                    # Upload data yang diperlukan ke GPU
                    base_image_umat = cv2.UMat(base_image_input) # Tipe data asli (uint8/uint16) dijaga
                    remap_x_umat = cv2.UMat(remap_x)
                    remap_y_umat = cv2.UMat(remap_y)

                    compensated_image_umat = cv2.remap(
                        base_image_umat,
                        remap_x_umat,
                        remap_y_umat,
                        interpolation=interp_flag,
                        borderMode=cv2.BORDER_REFLECT # Atau BORDER_CONSTANT?
                    )
                    compensated_image = compensated_image_umat.get() # Download hasil
                except cv2.error as gpu_remap_err:
                     print(f"OpenCV GPU error during remap: {gpu_remap_err}. Falling back to CPU.")
                     use_gpu = False # Matikan flag jika remap GPU gagal
                     del base_image_umat, remap_x_umat, remap_y_umat, compensated_image_umat # Hapus UMat
                except Exception as gpu_remap_exc:
                     print(f"Unexpected GPU error during remap: {gpu_remap_exc}. Falling back to CPU.")
                     use_gpu = False

            # Jalur CPU (atau fallback dari GPU)
            if not use_gpu:
                compensated_image = cv2.remap(
                    base_image_input, # Gunakan input NumPy asli
                    remap_x,
                    remap_y,
                    interpolation=interp_flag,
                    borderMode=cv2.BORDER_REFLECT # Atau BORDER_CONSTANT?
                )
            # ----------------------------------

            end_time = time.time()
            # Pesan selesai bisa dipindah ke pemanggil
            # print(language_config.COMPENSATE_MOTION_FINISHED.format(image_id=image_id))
            print(f"Compensate motion for image {image_id} finished in {end_time - start_time:.2f} seconds.")
            return compensated_image

        except ValueError as ve:
            print(f"Error in compensate_motion for image {image_id}: {ve}")
            return None
        except cv2.error as cv_err:
             print(f"OpenCV error during compensate_motion for image {image_id}: {cv_err}")
             return None
        except Exception as e:
            print(f"Unexpected error during compensate_motion for image {image_id}: {e}")
            return None

def main(db_path, update_progress=None, batch_size=5, stop_requested=None, single_process=None, 
         batch_id=None,):
    processor = FarnebackAlgorithm(db_path)

    # Dapatkan semua path gambar
    if single_process:
        image_paths = processor.get_all_image_paths_for_single_process()
    else:
        if batch_id is None:
            raise ValueError("batch_id harus diberikan untuk batch process")
        image_paths = processor.get_all_image_paths_for_batch_process(batch_id)
    
    if not image_paths:
        if update_progress:
            update_progress(0, language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
        return
    
    # Ekstrak metadata dari seluruh gambar dan simpan ke file JSON
    metadata_folder = os.path.join("database", "align")
    os.makedirs(metadata_folder, exist_ok=True)
    metadata_file = os.path.join(metadata_folder, "metadata.json")
    extract_all_metadata(image_paths, metadata_file=metadata_file)

    # Gunakan gambar pertama sebagai referensi
    base_image_path = image_paths[0]
    base_image = cv2.imread(base_image_path, cv2.IMREAD_UNCHANGED)
    if base_image is None:
        print(language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
        return

    total_images = len(image_paths)
    total_batches = (total_images - 1) // batch_size + 1

    with h5py.File(processor.hdf5_path, "w") as h5f:
        h5f.create_dataset("image_0", data=base_image)

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []

            num_threads = os.cpu_count() or 4
            
            for batch_idx in range(total_batches):
                if stop_requested and stop_requested():
                    break

                start_idx = batch_idx * batch_size + 1
                end_idx = min((batch_idx + 1) * batch_size + 1, total_images)
                batch_paths = image_paths[start_idx:end_idx]
                batch_images = load_images_from_paths(batch_paths, stop_requested)
                if not batch_images:
                    continue

                for i, target_image in enumerate(batch_images, start=start_idx):
                    if stop_requested and stop_requested():
                        break

                    info_message = language_config.RUN_IMAGE_PROCESSING.format(i=i, total_images=total_images)
                    print(info_message)
                    if update_progress:
                        update_progress(i - 1, total_images - 1, info_message)

                    # Menggunakan metode parallel untuk optical flow pada tiap gambar
                    flow = processor.calculate_optical_flow(base_image, target_image)
                    compensated_image = processor.compensate_motion(target_image, flow, image_id=i)
                    
                    # Ekstrak metadata untuk gambar yang sedang diproses (dari path asli)
                    original_path = batch_paths[i - start_idx]
                    metadata = extract_exif(original_path)

                    if compensated_image is not None:
                        dataset_name = f"image_{i}"
                        futures.append(executor.submit(save_to_hdf5, h5f, dataset_name, compensated_image, metadata))

            for future in futures:
                future.result()

    if update_progress:
        update_progress(total_images - 1, total_images - 1, language_config.SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED)
    if update_progress:
        update_progress(total_images - 1, total_images - 1, language_config.SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED)

    # print("Pemrosesan selesai dan semua gambar telah disimpan ke HDF5.")

def running_farneback_optical_flow(parent=None, single_process=None, batch_id=None):
    process_finished = False
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

    worker = ImageProcessingMultiThreading(main, "pixel_refine_database.db", single_process=single_process, batch_id=batch_id)
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