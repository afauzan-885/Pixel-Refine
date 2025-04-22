import ctypes
from functools import lru_cache
import cv2
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import QThread, pyqtSignal, Qt
# from UI.enhance_stack.algorithm.denoising.extra_similarity.compute_motion_metrics_aot import accumulate_tiles_jit
from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import extract_all_metadata, save_image  
from UI.enhance_stack.algorithm.denoising.extra_code.extra_algorithm import call_accumulate_frame_weighted_flow_motion, call_normalize_accumulated_flow_motion, estimate_noise_stddev_simple 
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

class FlowMotionAlgorithm:
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
    
    @lru_cache(maxsize=None) # Tambahkan cache jika jendela sering sama
    def gaussian_window(self, size, sigma_scale=1/6):
        # Implementasi gaussian_window Anda (sudah benar)
        rows, cols = size
        sigma_y = rows * sigma_scale
        sigma_x = cols * sigma_scale
        y = np.arange(0, rows, 1, float) - (rows - 1) / 2
        x = np.arange(0, cols, 1, float) - (cols - 1) / 2
        gaussian_y = np.exp(-(y**2 / (2 * sigma_y**2)))
        gaussian_x = np.exp(-(x**2 / (2 * sigma_x**2)))
        window = np.outer(gaussian_y, gaussian_x)
        window = window / window.max() # Normalisasi window ke [0, 1]
        return window.astype(np.float32)

    def normalize_image(self, image, dtype):
        # Implementasi Anda sudah benar
        image_float = np.ascontiguousarray(image.astype(np.float32))
        scale = np.float32(np.iinfo(dtype).max)
        norm_image = image_float / scale
        if image.ndim == 2:
            norm_image = np.stack((norm_image,) * 3, axis=-1)
        return norm_image.astype(np.float32)

    @lru_cache(maxsize=None)
    def gaussian_window(self, size, sigma_scale=1/6):
        """Menghasilkan jendela Gaussian 2D [0, 1] float32 C-contiguous."""
        rows, cols = size
        if rows <= 0 or cols <= 0:
            return np.zeros((0, 0), dtype=np.float32) # Handle edge case
        sigma_y = max(rows * sigma_scale, 1e-6) # Hindari sigma nol
        sigma_x = max(cols * sigma_scale, 1e-6) # Hindari sigma nol
        y = np.arange(0, rows, 1, float) - (rows - 1) / 2
        x = np.arange(0, cols, 1, float) - (cols - 1) / 2
        # Hindari pembagian dengan nol jika sigma sangat kecil (meskipun sudah dicegah)
        gaussian_y = np.exp(-y**2 / (2 * sigma_y**2 + 1e-12))
        gaussian_x = np.exp(-x**2 / (2 * sigma_x**2 + 1e-12))
        window = np.outer(gaussian_y, gaussian_x)
        max_val = window.max()
        if max_val > 1e-6: # Hindari pembagian dengan nol jika window hampir nol
             window = window / max_val
        else:
             window = np.zeros_like(window) # Jika window nol, kembalikan nol
        # Pastikan tipe dan contiguity
        return np.ascontiguousarray(window.astype(np.float32))

    def normalize_image(self, image, dtype):
        """
        Normalisasi gambar ke range [0, 1] float32 berdasarkan tipe data asli.
        Mempertahankan kecerahan relatif antar frame. Menghasilkan C-contiguous array.
        """
        # Dapatkan nilai maksimum dari tipe data asli
        try:
            scale = np.float32(np.iinfo(dtype).max)
        except ValueError:
            # Jika dtype sudah float, skala adalah 1.0 (asumsi input float sudah [0,1])
            if np.issubdtype(dtype, np.floating):
                scale = 1.0
            else:
                raise TypeError(f"Unsupported dtype for normalization: {dtype}")

        # Konversi ke float32 dan pastikan array contiguous
        image_float = np.ascontiguousarray(image.astype(np.float32))

        # Bagi dengan scale untuk mendapatkan range [0, 1] jika scale > 0
        if scale > 1e-6:
            norm_image = image_float / scale
        else:
             norm_image = image_float # Jika scale 0 atau negatif, jangan dibagi

        # Handle grayscale jika perlu
        if image.ndim == 2:
            norm_image = np.stack((norm_image,) * 3, axis=-1)

        # Pastikan output float32 dan C-contiguous
        return np.ascontiguousarray(norm_image.astype(np.float32))

    def flow_mnfr(self, images, tile_size=(12, 12), overlap=0.45,
                        motion_threshold=0.3, update_progress=None, stop_requested=None,
                        lib_path='UI/data/flow_motion.dll'): # Pastikan path benar

        if not images:
             raise ValueError("Input images list is empty.")

        # Validasi tile_size
        if not (isinstance(tile_size, (tuple, list)) and len(tile_size) == 2 and
                tile_size[0] > 0 and tile_size[1] > 0):
            raise ValueError("tile_size must be a tuple or list of two positive integers.")
        tile_h, tile_w = map(int, tile_size) # Pastikan integer

        # Ambil properti dari gambar pertama
        try:
            h, w, channels = images[0].shape
            dtype = images[0].dtype
        except (AttributeError, IndexError, ValueError) as e:
            raise ValueError(f"Could not get shape/dtype from the first image: {e}")

        if dtype not in (np.uint8, np.uint16):
             raise TypeError("Input image dtype must be uint8 or uint16.")

        # --- Parameter MBM ---
        mbm_block_h = min(tile_h, 16) # Contoh, sesuaikan jika perlu
        mbm_block_w = min(tile_w, 16) # Contoh, sesuaikan jika perlu
        mbm_search_radius = 7       # Contoh, sesuaikan jika perlu

         # --- Estimasi Noise Profile (Sekali di Awal) ---
        print("Estimating noise profile from the first frame...")
        ref_img_for_noise = self.normalize_image(images[0], dtype) # [0,1] float
        if ref_img_for_noise.shape[2] == 3:
             gray_ref_for_noise = cv2.cvtColor(ref_img_for_noise, cv2.COLOR_BGR2GRAY)
        else:
             gray_ref_for_noise = ref_img_for_noise[:,:,0]
        estimated_noise_sigma = estimate_noise_stddev_simple(gray_ref_for_noise, block_size=8, percentile=10) # Gunakan fungsi estimasi
        print(f"Estimated Noise Sigma: {estimated_noise_sigma:.4f}")
        # ---------------------------------------------

        # --- Load Library & Definisikan Argtypes (Tambahkan noise sigma) ---
        if not os.path.exists(lib_path): raise FileNotFoundError(f"Shared library not found: {lib_path}")
        try:
            clib = ctypes.CDLL(lib_path)

            clib.accumulate_frame_weighted_jit.argtypes = [
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS, WRITEABLE'), # 1
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS, WRITEABLE'), # 2
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),           # 3
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),           # 4
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),           # 5
                np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),             # 6
                np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),             # 7
                ctypes.c_int, ctypes.c_int, # 8, 9
                ctypes.c_int, ctypes.c_int, # 10, 11
                ctypes.c_int, ctypes.c_int, ctypes.c_int, # 12, 13, 14
                ctypes.c_float, # 15 base_motion_threshold
                ctypes.c_float, # 16 estimated_noise_sigma <<--- TAMBAHAN
                ctypes.c_int,   # 17 mbm_block_h
                ctypes.c_int,   # 18 mbm_block_w
                ctypes.c_int    # 19 mbm_search_radius <<--- Indeks jadi 19
            ]
            clib.accumulate_frame_weighted_jit.restype = None

            clib.normalize_accumulated_image_jit.argtypes = [
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS, WRITEABLE'), # 1
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),           # 2
                ctypes.c_int, ctypes.c_int, ctypes.c_int  # 3, 4, 5
            ]
            clib.normalize_accumulated_image_jit.restype = None

        except Exception as e: # Tangkap error lebih umum
            raise RuntimeError(f"Error loading library or setting argtypes from {lib_path}: {e}")
        except AttributeError as e:
             # Tangkap error jika fungsi tidak ditemukan di DLL
             raise AttributeError(f"Function not found in DLL or error setting argtypes. Did you compile C++ correctly? Error: {e}")

        # --- Persiapan Buffer & Variabel (Pastikan Contiguous) ---
        reference_image_float = self.normalize_image(images[0], dtype) # normalize_image sudah memastikan contiguous
        # Buat buffer sum, pastikan contiguous secara eksplisit
        final_image_sum = np.ascontiguousarray(np.zeros_like(reference_image_float, dtype=np.float32))
        weight_map_sum = np.ascontiguousarray(np.zeros((h, w), dtype=np.float32))

        # --- Tile Starts & Base Window (Pastikan Contiguous) ---
        step_y = max(int(tile_h * (1 - overlap)), 1)
        step_x = max(int(tile_w * (1 - overlap)), 1)
        # Pastikan h >= tile_h dan w >= tile_w sebelum menggunakan arange
        if h >= tile_h:
            row_starts = np.arange(0, h - tile_h + 1, step_y)
            # Tambahkan start terakhir jika belum ada dan jika ada > 1 tile
            if h > tile_h and (len(row_starts) == 0 or row_starts[-1] != h - tile_h):
                 row_starts = np.append(row_starts, h - tile_h)
            elif h == tile_h: # Hanya satu tile mungkin
                 row_starts = np.array([0])
        else: # Gambar lebih kecil dari tile
             row_starts = np.array([0])

        if w >= tile_w:
            col_starts = np.arange(0, w - tile_w + 1, step_x)
            if w > tile_w and (len(col_starts) == 0 or col_starts[-1] != w - tile_w):
                 col_starts = np.append(col_starts, w - tile_w)
            elif w == tile_w:
                 col_starts = np.array([0])
        else: # Gambar lebih kecil dari tile
             col_starts = np.array([0])

        # Pastikan tipe dan contiguity untuk starts
        row_starts = np.ascontiguousarray(np.unique(row_starts).astype(np.int32)) # unique handles potential duplicates if step is small
        col_starts = np.ascontiguousarray(np.unique(col_starts).astype(np.int32))

        # Dapatkan base_window (gaussian_window sudah memastikan contiguous)
        base_window = self.gaussian_window(tile_size)

        # --- Skala Denormalisasi ---
        scale_value = np.float32(np.iinfo(dtype).max)

        num_images = len(images)
        processed_frames = 0

        # --- Loop Pemrosesan Gambar (Panggil Wrapper dengan Noise Sigma) ---
        print(f"Starting MFNR accumulation for {num_images} images...")
        base_motion_threshold = motion_threshold # Ambil nilai dari argumen fungsi

        # --- Loop Pemrosesan Gambar ---
        print(f"Starting MFNR process for {num_images} images...") # Debug print
        for i, image_orig in enumerate(images):
            if update_progress:
                progress = int((processed_frames / num_images) * 100) # Progress berdasarkan yg sudah diproses
                message = f"Accumulating frame {i+1} of {num_images}"
                update_progress(progress, message)

            if stop_requested and stop_requested():
                print("Stop requested during accumulation.")
                break

            # --- Validasi Input Frame ---
            try:
                # Cek dimensi spasial
                if image_orig.shape[0] != h or image_orig.shape[1] != w:
                    raise ValueError(f"Image {i+1} size ({image_orig.shape[0]}x{image_orig.shape[1]}) does not match reference ({h}x{w}).")
                # Cek tipe data
                if image_orig.dtype != dtype:
                    raise ValueError(f"Image {i+1} dtype ({image_orig.dtype}) does not match reference ({dtype}).")
                # Cek jumlah channel (setelah normalisasi akan jadi 3 jika input gray)
                num_channels_orig = image_orig.shape[2] if image_orig.ndim == 3 else 1
                if num_channels_orig != channels and not (image_orig.ndim == 2 and channels == 3): # Allow gray input -> 3ch output
                     raise ValueError(f"Image {i+1} channels ({num_channels_orig}) inconsistent with reference ({channels}).")

            except Exception as e:
                print(f"Error validating image {i}: {e}")
                # Putuskan: lewati frame ini atau hentikan proses?
                # continue # Lewati frame bermasalah
                raise ValueError(f"Validation failed for image {i}: {e}") # Hentikan

            # --- Normalisasi Frame Saat Ini ---
            current_image_float = self.normalize_image(image_orig, dtype) # normalize_image memastikan contiguous

            # --- Panggil Fungsi Akumulasi C++ ---
            try:
                # print(f"Calling accumulate for frame {i+1}...") # Debug print
                call_accumulate_frame_weighted_flow_motion(
                    clib, final_image_sum, weight_map_sum,
                    current_image_float, reference_image_float,
                    base_window, row_starts, col_starts,
                    tile_h, tile_w, h, w, channels,
                    base_motion_threshold, # <-- Kirim base threshold
                    estimated_noise_sigma, # <-- Kirim sigma noise
                    mbm_block_h, mbm_block_w, mbm_search_radius
                )
                processed_frames += 1 # Hanya increment jika pemanggilan berhasil
                # print(f"Frame {i+1} accumulated.") # Debug print
            except Exception as e:
                 print(f"ERROR calling C++ accumulate function for frame {i+1}: {e}")
                 # Putuskan: Lanjutkan tanpa frame ini atau hentikan?
                 # continue # Coba lanjutkan tanpa frame ini
                 raise RuntimeError(f"C++ accumulation failed for frame {i+1}: {e}") # Hentikan

        # --- Normalisasi FINAL (Setelah Loop) ---
        if processed_frames > 0:
            if update_progress: update_progress(99, "Normalizing final image...") # Hampir selesai
            print(f"Accumulated {processed_frames} frames. Normalizing...") # Debug print

            try:
                # Panggil fungsi NORMALISASI C++
                call_normalize_accumulated_flow_motion(clib, final_image_sum, weight_map_sum, h, w, channels)
                # `final_image_sum` sekarang berisi hasil ternormalisasi [0,1]
                print("Normalization complete.") # Debug print
            except Exception as e:
                 print(f"ERROR calling C++ normalize function: {e}")
                 raise RuntimeError(f"C++ normalization failed: {e}") # Hentikan jika normalisasi gagal

            # --- Denormalisasi, Clipping, Konversi Tipe (di Python) ---
            final_image_normalized = final_image_sum # Ganti nama agar lebih jelas
            final_image_scaled = final_image_normalized * scale_value

            if dtype in (np.uint8, np.uint16):
                min_val = 0
                max_val = np.iinfo(dtype).max
                final_image_output = np.clip(final_image_scaled, min_val, max_val).astype(dtype, copy=False)
            else:
                # Handle kasus jika tipe data asli float (meskipun validasi di awal mencegahnya)
                final_image_output = np.clip(final_image_normalized, 0.0, 1.0).astype(dtype, copy=False)

            if stop_requested and stop_requested() and processed_frames < num_images:
                 print(f"WARNING: Returning partially processed image after accumulating {processed_frames} frames.")

            if update_progress: update_progress(100, "MFNR process finished.")
            print("MFNR process finished successfully.")
            return final_image_output
        else:
            # Jika tidak ada frame yang diproses
            print("No frames were processed successfully.")
            if update_progress: update_progress(100, "MFNR process failed: No frames processed.")
            # Kembalikan gambar hitam atau referensi, sesuai spesifikasi
            return np.zeros_like(images[0]) # Contoh: kembalikan gambar hitam

def main(db_path, update_progress=None, stop_requested=None, batch_size=8, single_process=None, batch_id=None):
    try:
        image_processor = FlowMotionAlgorithm(db_path)
        
        # Pilih sumber image_paths berdasarkan parameter single_process
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
                    batch_result = image_processor.flow_mnfr(batch_images, update_progress=update_progress, stop_requested=stop_requested)
                    processed_batches.append(batch_result)

                    progress = int(((batch_start + len(batch_keys)) / total_images) * 100)
                    if update_progress:
                        update_progress(progress, language_config.RUN_IMAGE_PROCESS_BATCH_PROGRESS.format(
                            current=batch_start + len(batch_keys), total=total_images
                        ))
        else:
            total_images = len(image_paths)
            processed_count = 0 

            for batch_start in range(0, total_images, batch_size):
                if stop_requested and stop_requested():
                    break

                batch_paths = image_paths[batch_start:batch_start + batch_size]
                batch_images = [cv2.imread(path, cv2.IMREAD_UNCHANGED) for path in batch_paths if cv2.imread(path, cv2.IMREAD_UNCHANGED) is not None]

                # Proses batch
                batch_result = image_processor.flow_mnfr(batch_images, update_progress=update_progress, stop_requested=stop_requested)
                processed_batches.append(batch_result)

                progress = int(((batch_start + len(batch_paths)) / total_images) * 100)
                if update_progress:
                    update_progress(progress, language_config.RUN_IMAGE_PROCESS_BATCH_PROGRESS.format(
                        current=batch_start + len(batch_paths), total=total_images
                    ))

        if processed_batches:
            # Proses fine-tuning dari semua hasil batch
            final_result = image_processor.flow_mnfr(processed_batches, update_progress=update_progress, stop_requested=stop_requested)

            # Simpan hasil akhir
            save_image(final_result, output_path, reference_image_path=reference_image_path)

            if update_progress:
                update_progress(100, language_config.RUN_IMAGE_PROCESS_STACK_SUCCESS.format(output_path=output_path))
        else:
            if update_progress:
                update_progress(0, language_config.STACK_IMAGES_FAILED)

    except Exception as e:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        print(error_message)  # Menampilkan error untuk debugging
        if update_progress:
            update_progress(0, error_message)
        raise

def running_motion_flow(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle("Motion Flow Stacking")
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(
        Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint |
        Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint
    )

    # Layout untuk progress bar dan label
    layout = QVBoxLayout(dialog)
    label = QLabel("Starting process...")
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