import ctypes
from functools import lru_cache
import traceback
import cv2
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import QThread, pyqtSignal, Qt
# from UI.enhance_stack.algorithm.denoising.extra_similarity.compute_motion_metrics_aot import accumulate_tiles_jit
from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import extract_all_metadata, save_image
from UI.enhance_stack.algorithm.denoising.extra_code.extra_algorithm import SimilarityV1MotionInterface
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

class SimilarityAlgorithm:
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

    def similarity_mfnr(self, images, tile_size=(12, 12), overlap=0.50,
                        motion_threshold=0.030, update_progress=None, stop_requested=None,
                        lib_path='UI/data/similarity_motion.dll',
                        save_weight_map_path=None): # Tambahkan parameter opsional

        if not isinstance(images, list) or not images: # Pastikan images adalah list dan tidak kosong
             raise ValueError("Input 'images' must be a non-empty list.")

        # Validasi tile_size
        if not (isinstance(tile_size, (tuple, list)) and len(tile_size) == 2 and
                tile_size[0] > 0 and tile_size[1] > 0):
            raise ValueError("tile_size must be a tuple or list of two positive integers.")
        tile_h, tile_w = map(int, tile_size)

        # Ambil properti dari gambar pertama dan validasi tipe
        try:
            ref_image = images[0]
            if not isinstance(ref_image, np.ndarray):
                 raise TypeError("Images in the list must be NumPy arrays.")
            h, w = ref_image.shape[:2] # Ambil H, W
            channels = ref_image.shape[2] if ref_image.ndim == 3 else 1 # Cek channel
            dtype = ref_image.dtype

            # Paksa channels jadi 3 jika input grayscale untuk konsistensi buffer C++
            if channels == 1:
                channels_buffer = 3 # Buffer C++ akan selalu 3 channel
            elif channels == 3:
                 channels_buffer = 3
            # elif channels == 4: # Handle 4 channel jika perlu (misal RGBA)
            #     channels_buffer = 4 # Sesuaikan tipe C++ jika perlu
            else:
                 raise ValueError(f"Unsupported number of channels: {channels}")

        except (AttributeError, IndexError, ValueError, TypeError) as e:
            raise ValueError(f"Could not get valid shape/dtype/channels from the first image: {e}")

        if dtype not in (np.uint8, np.uint16):
             raise TypeError("Input image dtype must be uint8 or uint16.")

        # --- Parameter MBM ---
        mbm_block_h = min(tile_h, 16)
        mbm_block_w = min(tile_w, 16)
        mbm_search_radius = 24
        
        # --- BUAT INSTANCE INTERFACE C++ ---
        try:
            # Ini menggantikan blok pemuatan DLL dan definisi argtypes
            c_interface = SimilarityV1MotionInterface(lib_path)
        except (FileNotFoundError, OSError, AttributeError) as e:
            # Tangani error saat memuat/menginisialisasi interface
            raise RuntimeError(f"Failed to initialize C++ interface: {e}")

        # --- Load Library C++ & Definisikan Argtypes SEKALI ---
        # ... (kode load clib dan definisi argtypes Anda sebelumnya, pastikan channels_buffer sesuai) ...
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Shared library not found: {lib_path}")
        try:
            clib = ctypes.CDLL(lib_path)

            # Definisikan argtypes untuk accumulate_frame_weighted_jit
            clib.accumulate_frame_weighted_jit.argtypes = [
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS, WRITEABLE'), # 1 final_image_sum_ptr (selalu 3 channel)
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS, WRITEABLE'), # 2 weight_map_sum_ptr
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),           # 3 current_image_ptr (selalu 3 channel)
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),           # 4 reference_image_ptr (selalu 3 channel)
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),           # 5 base_window_ptr
                np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),             # 6 row_starts
                np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),             # 7 col_starts
                ctypes.c_int, # 8 num_row_starts
                ctypes.c_int, # 9 num_col_starts
                ctypes.c_int, # 10 tile_h
                ctypes.c_int, # 11 tile_w
                ctypes.c_int, # 12 h
                ctypes.c_int, # 13 w
                ctypes.c_int, # 14 channels (jumlah channel buffer C++, yaitu 3)
                ctypes.c_float, # 15 motion_threshold
                ctypes.c_int, # 16 mbm_block_h
                ctypes.c_int, # 17 mbm_block_w
                ctypes.c_int  # 18 mbm_search_radius
            ]
            clib.accumulate_frame_weighted_jit.restype = None

            # Definisikan argtypes untuk normalize_accumulated_image_jit
            clib.normalize_accumulated_image_jit.argtypes = [
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS, WRITEABLE'), # 1 final_image_ptr (selalu 3 channel)
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),           # 2 weight_map_sum_ptr
                ctypes.c_int, # 3 h
                ctypes.c_int, # 4 w
                ctypes.c_int  # 5 channels (jumlah channel buffer C++, yaitu 3)
            ]
            clib.normalize_accumulated_image_jit.restype = None

        except OSError as e:
            raise OSError(f"Error loading shared library {lib_path}: {e}")
        except AttributeError as e:
             raise AttributeError(f"Function not found in DLL or error setting argtypes. Did you compile C++ correctly? Error: {e}")


        # --- Persiapan Buffer & Variabel (Pastikan Contiguous) ---
        # Normalisasi gambar referensi (akan jadi 3 channel jika input gray)
        reference_image_float = self.normalize_image(ref_image, dtype)
        h_ref, w_ref, channels_ref = reference_image_float.shape # Ambil shape setelah normalisasi
        if channels_ref != channels_buffer: # Double check konsistensi channel
            raise RuntimeError(f"Internal Error: Normalized reference image channels ({channels_ref}) mismatch buffer channels ({channels_buffer})")

        # Buat buffer sum dengan ukuran H, W, dan channels_buffer (3)
        final_image_sum = np.ascontiguousarray(np.zeros((h_ref, w_ref, channels_buffer), dtype=np.float32))
        weight_map_sum = np.ascontiguousarray(np.zeros((h_ref, w_ref), dtype=np.float32))

        # --- Tile Starts & Base Window (Pastikan Contiguous) ---
        # ... (kode tile starts dan base_window Anda sebelumnya) ...
        step_y = max(int(tile_h * (1 - overlap)), 1)
        step_x = max(int(tile_w * (1 - overlap)), 1)
        if h_ref >= tile_h:
            row_starts = np.arange(0, h_ref - tile_h + 1, step_y)
            if h_ref > tile_h and (len(row_starts) == 0 or row_starts[-1] != h_ref - tile_h):
                 row_starts = np.append(row_starts, h_ref - tile_h)
            elif h_ref == tile_h:
                 row_starts = np.array([0])
        else:
             row_starts = np.array([0])

        if w_ref >= tile_w:
            col_starts = np.arange(0, w_ref - tile_w + 1, step_x)
            if w_ref > tile_w and (len(col_starts) == 0 or col_starts[-1] != w_ref - tile_w):
                 col_starts = np.append(col_starts, w_ref - tile_w)
            elif w_ref == tile_w:
                 col_starts = np.array([0])
        else:
             col_starts = np.array([0])

        row_starts = np.ascontiguousarray(np.unique(row_starts).astype(np.int32))
        col_starts = np.ascontiguousarray(np.unique(col_starts).astype(np.int32))
        base_window = self.gaussian_window(tile_size)

        # --- Skala Denormalisasi ---
        scale_value = np.float32(np.iinfo(dtype).max)

        num_images = len(images)
        processed_frames = 0

        # --- Loop Pemrosesan Gambar ---
        print(f"Starting MFNR process for {num_images} images...")
        for i, image_orig in enumerate(images):
            if not isinstance(image_orig, np.ndarray):
                print(f"Warning: Skipping item at index {i} because it's not a NumPy array.")
                continue

            if update_progress:
                # Hitung progress berdasarkan frame yang *dicoba* diproses
                progress = int(((i + 1) / num_images) * 99) # Cap di 99% sebelum normalisasi
                message = f"Accumulating frame {i+1} of {num_images}"
                update_progress(progress, message)

            if stop_requested and stop_requested():
                print("Stop requested during accumulation.")
                break

            # --- Validasi Input Frame ---
            try:
                if image_orig.shape[0] != h or image_orig.shape[1] != w:
                    print(f"Warning: Skipping image {i+1} due to size mismatch ({image_orig.shape[:2]} vs {h}x{w}).")
                    continue
                if image_orig.dtype != dtype:
                    print(f"Warning: Skipping image {i+1} due to dtype mismatch ({image_orig.dtype} vs {dtype}).")
                    continue
                # Cek channel asli (sebelum normalisasi)
                num_channels_orig = image_orig.shape[2] if image_orig.ndim == 3 else 1
                if num_channels_orig not in (1, channels_buffer): # Hanya izinkan 1 atau 3 channel input
                     print(f"Warning: Skipping image {i+1} due to unsupported original channels ({num_channels_orig}).")
                     continue

            except Exception as e:
                print(f"Error validating image {i+1}: {e}. Skipping.")
                continue # Lewati frame bermasalah

            # --- Normalisasi Frame Saat Ini (akan jadi 3 channel jika input gray) ---
            current_image_float = self.normalize_image(image_orig, dtype)
            if current_image_float.shape[2] != channels_buffer:
                 print(f"Error: Normalized image {i+1} has unexpected channels ({current_image_float.shape[2]}). Skipping.")
                 continue


            # --- Panggil Fungsi Akumulasi C++ ---
            try:
                c_interface.call_accumulate_frame_weighted(
                    clib, final_image_sum, weight_map_sum, # Target (Writable)
                    current_image_float, reference_image_float, # Input (Read-only)
                    base_window, row_starts, col_starts, # Params
                    tile_h, tile_w, h_ref, w_ref, channels_buffer, # Ukuran & Channel Buffer
                    motion_threshold,
                    mbm_block_h, mbm_block_w, mbm_search_radius
                )
                processed_frames += 1 # Hanya increment jika pemanggilan berhasil
            except Exception as e:
                 print(f"ERROR calling C++ accumulate function for frame {i+1}: {e}")
                 # Putuskan: Lanjutkan tanpa frame ini atau hentikan?
                 # continue # Coba lanjutkan tanpa frame ini
                 raise RuntimeError(f"C++ accumulation failed for frame {i+1}: {e}") # Hentikan

        # --- Normalisasi FINAL (Setelah Loop) ---
        if processed_frames > 0:
            if update_progress: update_progress(99, "Normalizing final image...")
            print(f"Accumulated {processed_frames} frames. Normalizing...")

            try:
                c_interface.call_normalize_accumulated(clib, final_image_sum, weight_map_sum, h_ref, w_ref, channels_buffer)
                print("Normalization complete.")
            except Exception as e:
                 print(f"ERROR calling C++ normalize function: {e}")
                 raise RuntimeError(f"C++ normalization failed: {e}")

            # --- PENYIMPANAN PETA BOBOT (BARU) ---
            if save_weight_map_path:
                print(f"Generating and saving weight map to {save_weight_map_path}...")
                try:
                    # Normalisasi weight_map_sum ke [0, 1] untuk visualisasi
                    max_weight = np.max(weight_map_sum)
                    if max_weight > 1e-6: # Hindari pembagian dengan nol
                        normalized_weights = weight_map_sum / max_weight
                    else:
                        normalized_weights = np.zeros_like(weight_map_sum) # Peta hitam jika tidak ada bobot

                    # Konversi ke uint8 [0, 255]
                    weight_map_vis = (np.clip(normalized_weights, 0, 1) * 255).astype(np.uint8)

                    # Simpan peta bobot sebagai gambar grayscale
                    cv2.imwrite(save_weight_map_path, weight_map_vis)
                    print("Weight map saved successfully.")
                except Exception as e:
                    print(f"ERROR: Could not save weight map: {e}")
            # --- AKHIR BAGIAN PETA BOBOT ---


            # --- Denormalisasi, Clipping, Konversi Tipe (di Python) ---
            final_image_normalized = final_image_sum # Hasil normalisasi dari C++
            final_image_scaled = final_image_normalized * scale_value

            # Konversi kembali ke tipe data asli (uint8/uint16)
            # Jika input asli grayscale, kembalikan grayscale
            if ref_image.ndim == 2 or (ref_image.ndim == 3 and ref_image.shape[2] == 1) :
                 # Ambil satu channel (misal channel 0) karena C++ memproses 3 channel
                 # Mungkin lebih baik merata-ratakan 3 channel? (tergantung C++)
                 # Jika C++ hanya mengisi 3 channel identik untuk input gray, ambil 1 saja cukup.
                 final_image_scaled_single_channel = final_image_scaled[:, :, 0]
                 min_val = 0
                 max_val = np.iinfo(dtype).max
                 final_image_output = np.clip(final_image_scaled_single_channel, min_val, max_val).astype(dtype, copy=False)
            elif channels_buffer == 3: # Input asli berwarna
                 min_val = 0
                 max_val = np.iinfo(dtype).max
                 final_image_output = np.clip(final_image_scaled, min_val, max_val).astype(dtype, copy=False)
            # Tambahkan handler untuk channel lain jika perlu

            if stop_requested and stop_requested() and processed_frames < num_images:
                 print(f"WARNING: Returning partially processed image after accumulating {processed_frames} frames.")

            if update_progress: update_progress(100, "MFNR process finished.")
            print("MFNR process finished successfully.")
            return final_image_output
        else:
            print("No frames were processed successfully.")
            if update_progress: update_progress(100, "MFNR process failed: No frames processed.")
            # Kembalikan gambar hitam dengan dimensi dan tipe yang benar
            output_shape = (h, w) if ref_image.ndim == 2 else (h, w, ref_image.shape[2])
            return np.zeros(output_shape, dtype=dtype)

def main(db_path, update_progress=None, stop_requested=None, batch_size=10,
         single_process=None, batch_id=None, save_final_weight_map=False): # Parameter baru ditambahkan
    try:
        print("Initializing SimilarityAlgorithm...")
        image_processor = SimilarityAlgorithm(db_path)
        print("Initialization complete.")

        # Tentukan nama dasar untuk file output
        output_name_base = "" # Inisialisasi
        image_paths = []      # Inisialisasi

        if single_process:
            print("Processing mode: Single Process")
            image_paths = image_processor.get_all_image_paths_for_single_process()
            if image_paths:
                 ref_image_name = os.path.splitext(os.path.basename(image_paths[0]))[0]
                 output_name_base = f"{ref_image_name}_single"
            else:
                 output_name_base = "single_process_no_images" # Default jika tidak ada gambar
        else:
            print(f"Processing mode: Batch Process (Batch ID: {batch_id})")
            if batch_id is None:
                raise ValueError("batch_id must be provided for batch process")
            image_paths = image_processor.get_all_image_paths_for_batch_process(batch_id)
            output_name_base = f"batch_{batch_id}"

        if not image_paths:
            print("No image paths found for processing.")
            if update_progress: update_progress(100, "No images found for processing.")
            return # Keluar jika tidak ada path

        # Tentukan path output utama dan path peta bobot
        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)
        # Pastikan output_name_base valid untuk nama file
        output_name_base_safe = "".join(c for c in output_name_base if c.isalnum() or c in ('_', '-')).rstrip()
        if not output_name_base_safe: output_name_base_safe = "stack_result" # Fallback name
        output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_similarity_stack.tif")
        weight_map_output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_similarity_weight_map.png")
        print(f"Output image path: {output_path}")
        print(f"Weight map path: {weight_map_output_path}")


        # --- Ekstraksi Metadata ---
        metadata_folder = os.path.join("database", "align")
        os.makedirs(metadata_folder, exist_ok=True)
        metadata_file = os.path.join(metadata_folder, "metadata.json")
        # Panggil fungsi extract_all_metadata jika sudah didefinisikan
        if 'extract_all_metadata' in globals():
            extract_all_metadata(image_paths, metadata_file=metadata_file)
            print("Metadata extraction called.")
        else:
             print("Metadata extraction step skipped (function not defined).")


        if update_progress: update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        global_hdf5_path = "database/align/aligned_images.h5"
        processed_batches = []

        # --- Logika Batching ---
        if os.path.exists(global_hdf5_path):
            print(f"Processing images from HDF5: {global_hdf5_path}")
            with h5py.File(global_hdf5_path, 'r') as h5f:
                keys = list(h5f.keys())
                total_images = len(keys)
                print(f"Total images in HDF5: {total_images}")
                if total_images == 0:
                     print("HDF5 file is empty. Cannot process.")
                     if update_progress: update_progress(100, "HDF5 file is empty.")
                     return

                for batch_start in range(0, total_images, batch_size):
                    current_batch_num = (batch_start // batch_size) + 1
                    total_batches = (total_images + batch_size - 1) // batch_size
                    print(f"\n--- Processing HDF5 Batch {current_batch_num}/{total_batches} ---")
                    if stop_requested and stop_requested(): break

                    batch_keys = keys[batch_start:min(batch_start + batch_size, total_images)]
                    print(f"Loading {len(batch_keys)} images for batch {current_batch_num}...")
                    batch_images = []
                    for key in batch_keys:
                        try: batch_images.append(np.array(h5f[key]))
                        except Exception as e: print(f"Error loading key {key}: {e}")
                    print(f"Loaded {len(batch_images)} images.")

                    if not batch_images:
                        print(f"Skipping empty batch {current_batch_num}.")
                        continue

                    print(f"Running similarity_mfnr for batch {current_batch_num}...")
                    batch_result = image_processor.similarity_mfnr(
                        batch_images, update_progress=update_progress, stop_requested=stop_requested
                        # JANGAN sertakan save_weight_map_path di sini
                    )
                    if batch_result is not None:
                         processed_batches.append(batch_result)
                         print(f"Batch {current_batch_num} processed successfully.")
                    else: print(f"Batch {current_batch_num} processing failed or returned None.")

                    processed_count_so_far = batch_start + len(batch_keys)
                    progress = int((processed_count_so_far / total_images) * 90)
                    if update_progress: update_progress(progress, language_config.RUN_IMAGE_PROCESS_BATCH_PROGRESS.format(current=processed_count_so_far, total=total_images))

        else: # Proses dari path jika HDF5 tidak ada
            print("HDF5 file not found. Processing images from original paths...")
            total_images = len(image_paths)
            print(f"Total image paths found: {total_images}")
            if total_images == 0:
                 print("No image paths to process.")
                 if update_progress: update_progress(100, "No image paths found.")
                 return

            for batch_start in range(0, total_images, batch_size):
                current_batch_num = (batch_start // batch_size) + 1
                total_batches = (total_images + batch_size - 1) // batch_size
                print(f"\n--- Processing Path Batch {current_batch_num}/{total_batches} ---")
                if stop_requested and stop_requested(): break

                batch_paths = image_paths[batch_start:min(batch_start + batch_size, total_images)]
                print(f"Loading {len(batch_paths)} images for batch {current_batch_num}...")
                batch_images = image_processor.load_images_from_paths(batch_paths, stop_requested)
                print(f"Loaded {len(batch_images)} images.")

                if not batch_images:
                    print(f"Skipping empty batch {current_batch_num}.")
                    continue

                print(f"Running similarity_mfnr for batch {current_batch_num}...")
                batch_result = image_processor.similarity_mfnr(
                    batch_images, update_progress=update_progress, stop_requested=stop_requested
                    # JANGAN sertakan save_weight_map_path di sini
                )
                if batch_result is not None:
                    processed_batches.append(batch_result)
                    print(f"Batch {current_batch_num} processed successfully.")
                else: print(f"Batch {current_batch_num} processing failed or returned None.")

                processed_count_so_far = batch_start + len(batch_paths)
                progress = int((processed_count_so_far / total_images) * 90)
                if update_progress: update_progress(progress, language_config.RUN_IMAGE_PROCESS_BATCH_PROGRESS.format(current=processed_count_so_far, total=total_images))

        # --- Fine-Tuning / Pemrosesan Akhir ---
        if processed_batches:
            print(f"\n--- Starting Final Fine-Tuning Process on {len(processed_batches)} Batch Results ---")
            if update_progress: update_progress(95, "Starting final fine-tuning...")

            # Tentukan path argumen untuk peta bobot berdasarkan flag input main
            final_weight_map_path_arg = weight_map_output_path if save_final_weight_map else None

            if final_weight_map_path_arg:
                print("Final weight map saving is ENABLED.")
            else:
                print("Final weight map saving is DISABLED.")

            # Proses fine-tuning dari semua hasil batch
            final_result = image_processor.similarity_mfnr(
                processed_batches, # Gunakan hasil batch sebagai input
                update_progress=update_progress,
                stop_requested=stop_requested,
                save_weight_map_path=final_weight_map_path_arg # <<-- Gunakan argumen kondisional
            )

            if final_result is not None:
                 # Simpan hasil akhir
                 print(f"Saving final fine-tuned image to {output_path}...")
                 # Gunakan fungsi save_image Anda atau cv2.imwrite langsung
                 save_success = save_image(final_result, output_path, reference_image_path=image_paths[0] if image_paths else None)
                 # save_success = cv2.imwrite(output_path, final_result) # Alternatif

                 if save_success:
                      print("Final fine-tuned image saved successfully.")
                      if update_progress: update_progress(100, language_config.RUN_IMAGE_PROCESS_STACK_SUCCESS.format(output_path=output_path))
                 else:
                      print(f"ERROR: Failed to save final image to {output_path}")
                      if update_progress: update_progress(100, "Failed to save final image.")
            else:
                print("Final fine-tuning process failed or returned None.")
                if update_progress: update_progress(100, "Final processing failed.")

        else: # Jika tidak ada batch yang berhasil diproses
            print("No batches were processed successfully. Cannot perform fine-tuning.")
            if update_progress:
                update_progress(100, language_config.STACK_IMAGES_FAILED)

    except ValueError as ve: # Tangkap ValueError spesifik (misal batch_id hilang)
         error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(ve))
         print(f"\n!!! CONFIGURATION ERROR in main function: {error_message} !!!")
         traceback.print_exc()
         if update_progress: update_progress(0, error_message)

    except FileNotFoundError as fnf: # Tangkap FileNotFoundError (misal DB atau DLL)
         error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(fnf))
         print(f"\n!!! FILE NOT FOUND ERROR in main function: {error_message} !!!")
         traceback.print_exc()
         if update_progress: update_progress(0, error_message)

    except Exception as e: # Tangkap semua error lain
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        print(f"\n!!! UNEXPECTED ERROR in main function: {error_message} !!!")
        traceback.print_exc() # Print traceback untuk debug
        if update_progress:
            update_progress(0, error_message) # Set progress ke 0 dan tampilkan error


def running_similarity(parent=None, single_process=None, batch_id=None):
    process_finished = False
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