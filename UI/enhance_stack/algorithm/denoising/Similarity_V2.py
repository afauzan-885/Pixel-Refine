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
from UI.enhance_stack.algorithm.denoising.extra_code.extra_algorithm import SimilarityV2MotionInterface
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

class SimilarityAlgorithmV2:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path
        self.low_global_sigma_thresh = 0.043  # Sigma di bawah ini dianggap "bersih"
        self.high_global_sigma_thresh = 0.28   # Sigma di atas ini dianggap "sangat ber-noise"
        self.high_max_multiplier = 5.5        # Multiplier maks untuk gambar bersih
        self.low_max_multiplier = 15.0        # Multiplier maks untuk gambar sangat ber-noise

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

    def _calculate_dynamic_max_multiplier(self, global_avg_sigma):
        """Menghitung multiplier maksimum dinamis berdasarkan sigma global."""
        clamped_sigma = max(self.low_global_sigma_thresh, min(global_avg_sigma, self.high_global_sigma_thresh))

        if self.high_global_sigma_thresh <= self.low_global_sigma_thresh:
            return self.high_max_multiplier 
        
        if clamped_sigma <= self.low_global_sigma_thresh:
            return self.high_max_multiplier
        elif clamped_sigma >= self.high_global_sigma_thresh:
            return self.low_max_multiplier
        else:
            factor = (clamped_sigma - self.low_global_sigma_thresh) / (self.high_global_sigma_thresh - self.low_global_sigma_thresh)
            dynamic_multiplier = self.high_max_multiplier + factor * (self.low_max_multiplier - self.high_max_multiplier)

            # --- PERBAIKAN LOGIKA CLAMPING ---
            lower_bound = min(self.low_max_multiplier, self.high_max_multiplier)
            upper_bound = max(self.low_max_multiplier, self.high_max_multiplier)

            clamped_multiplier = max(lower_bound, min(upper_bound, dynamic_multiplier))
            return clamped_multiplier
        
    # === FUNGSI untuk Skor Noise ===
    def _calculate_noise_level_score(self, global_avg_sigma):
        """
        Menghitung skor tingkat kebersihan gambar (0-100) berdasarkan sigma global.
        100 = Sangat Bersih (sigma <= low_thresh)
        0   = Sangat Bising (sigma >= high_thresh)
        Linear dazwischen.
        """
        sigma_low = self.low_global_sigma_thresh
        sigma_high = self.high_global_sigma_thresh

        if sigma_high <= sigma_low:
            return 50.0 if global_avg_sigma > sigma_low else 100.0

        if global_avg_sigma <= sigma_low:
            return 100.0
        elif global_avg_sigma >= sigma_high:
            return 0.0
        else:
            # Interpolasi linear terbalik: skor turun dari 100 ke 0 saat sigma naik
            score = 100.0 * (sigma_high - global_avg_sigma) / (sigma_high - sigma_low)
            # Pastikan skor tetap dalam rentang [0, 100] karena floating point error kecil
            return max(0.0, min(score, 100.0))
    
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
        
        gaussian_y = np.exp(-y**2 / (2 * sigma_y**2 + 1e-12))
        gaussian_x = np.exp(-x**2 / (2 * sigma_x**2 + 1e-12))
        window = np.outer(gaussian_y, gaussian_x)
        max_val = window.max()
        if max_val > 1e-6: 
             window = window / max_val
        else:
            window = np.zeros_like(window)
        
        return np.ascontiguousarray(window.astype(np.float32))

    def normalize_image(self, image, dtype):
        """
        Normalisasi gambar ke range [0, 1] float32 berdasarkan tipe data asli.
        Mempertahankan kecerahan relatif antar frame. Menghasilkan C-contiguous array.
        """
        try:
            scale = np.float32(np.iinfo(dtype).max)
        except ValueError:
            if np.issubdtype(dtype, np.floating):
                scale = 1.0
            else:
                raise TypeError(language_config.DATA_TYPE_NOT_SUPPORTED.format(dtype))

        image_float = np.ascontiguousarray(image.astype(np.float32))

        if scale > 1e-6:
            norm_image = image_float / scale
        else:
            norm_image = image_float
              
        if image.ndim == 2:
            norm_image = np.stack((norm_image,) * 3, axis=-1)

        return np.ascontiguousarray(norm_image.astype(np.float32))

    def similarity_mfnr(self, images, tile_size=(16, 16), overlap=0.40,
                        motion_threshold=0.0025, update_progress=None, stop_requested=None,
                        lib_path='UI/data/similarity_motion_v2.dll',
                        save_weight_map_path=None, total_overall_images=None, images_processed_so_far=0):

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
                raise TypeError(language_config.IMAGE_DATA_MUST_BE_VALID)
            h, w = ref_image.shape[:2]
            channels = ref_image.shape[2] if ref_image.ndim == 3 else 1
            dtype = ref_image.dtype
            
            if channels == 1: channels_buffer = 3
            elif channels == 3: channels_buffer = 3
            else:
                 raise ValueError(language_config.IMAGE_CHANNEL_DOES_NOT_SUPPORT.format(channels))

        except (AttributeError, IndexError, ValueError, TypeError) as e:
            raise ValueError(language_config.FIRST_IMAGE_CANNOT_BE_OBTAINED.format(e))

        if dtype not in (np.uint8, np.uint16):
            raise TypeError(language_config.IMAGE_BIT_REQUIRED) # Tambahkan detail

        mbm_block_h = tile_h
        mbm_block_w = tile_w
        mbm_search_radius = 16
        
        try:
            c_interface = SimilarityV2MotionInterface(lib_path)
        except (FileNotFoundError, OSError, AttributeError) as e:
            raise RuntimeError(f"Failed to initialize C++ interface: {e}")

        # --- Load Library C++ & Definisikan Argtypes SEKALI ---
        if not os.path.exists(lib_path):
            raise FileNotFoundError(language_config.LIBRARY_FILE_NOT_FOUND.format(lib_path))
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
                ctypes.c_int,  # 18 mbm_search_radius
                ctypes.c_float 
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
            
            # === DEFINISI UNTUK FUNGSI C++ BARU ===
            clib.estimate_global_noise.argtypes = [
                np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'), # reference_image_ptr
                ctypes.c_int, # h
                ctypes.c_int, # w
                ctypes.c_int, # channels (input, akan jadi gray di C++)
                ctypes.c_int, # tile_h
                ctypes.c_int, # tile_w
                np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'), # row_starts
                ctypes.c_int, # num_row_starts
                np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'), # col_starts
                ctypes.c_int  # num_col_starts
            ]
            clib.estimate_global_noise.restype = ctypes.c_float
            # === AKHIR DEFINISI BARU ===

        except OSError as e:
            raise OSError(language_config.FAILED_TO_CONFIGURE_LIBRARY.format(lib_path, e))
        except AttributeError as e:
             raise AttributeError(f"Function not found in DLL or error setting argtypes. Did you compile C++ correctly? Error: {e}")


         # --- Persiapan Buffer & Variabel (Sama) ---
        reference_image_float = self.normalize_image(ref_image, dtype)
        h_ref, w_ref, channels_ref = reference_image_float.shape
        if channels_ref != channels_buffer: raise RuntimeError(language_config.COLOR_CHANNEL_DOES_NOT_MATCH)
        final_image_sum = np.ascontiguousarray(np.zeros((h_ref, w_ref, channels_buffer), dtype=np.float32))
        weight_map_sum = np.ascontiguousarray(np.zeros((h_ref, w_ref), dtype=np.float32))

        # --- Tile Starts & Base Window (Sama) ---
        step_y = max(int(tile_h * (1 - overlap)), 1); step_x = max(int(tile_w * (1 - overlap)), 1)
        if h_ref >= tile_h:
            row_starts = np.arange(0, h_ref - tile_h + 1, step_y)
            if h_ref > tile_h and (len(row_starts) == 0 or row_starts[-1] != h_ref - tile_h): row_starts = np.append(row_starts, h_ref - tile_h)
            elif h_ref == tile_h: row_starts = np.array([0])
        else: row_starts = np.array([0])
        if w_ref >= tile_w:
            col_starts = np.arange(0, w_ref - tile_w + 1, step_x)
            if w_ref > tile_w and (len(col_starts) == 0 or col_starts[-1] != w_ref - tile_w): col_starts = np.append(col_starts, w_ref - tile_w)
            elif w_ref == tile_w: col_starts = np.array([0])
        else: col_starts = np.array([0])
        row_starts = np.ascontiguousarray(np.unique(row_starts).astype(np.int32))
        col_starts = np.ascontiguousarray(np.unique(col_starts).astype(np.int32))
        base_window = self.gaussian_window(tile_size)

        # --- HITUNG GLOBAL NOISE (PANGGIL C++), MULTIPLIER, DAN SKOR ---
        try:
            global_avg_sigma = clib.estimate_global_noise(
                reference_image_float,
                h_ref, w_ref, channels_buffer,
                tile_h, tile_w,
                row_starts, len(row_starts),
                col_starts, len(col_starts)
            )
        except Exception as e:
            global_avg_sigma = 0.0
            
        # Lanjutkan seperti sebelumnya
        frame_max_multiplier = self._calculate_dynamic_max_multiplier(global_avg_sigma)
        noise_level_score = self._calculate_noise_level_score(global_avg_sigma)
        print(f"  Cleanliness Score (0-100, 100=clean): {noise_level_score:.1f}")
       
        # --- Skala Denormalisasi ---
        scale_value = np.float32(np.iinfo(dtype).max)

        num_images = len(images)
        processed_frames = 0
        progress_cap_percent = 95

        # --- Loop Pemrosesan Gambar ---
        # print(f"Starting MFNR process for {num_images} images...")
        for i, image_orig in enumerate(images):
            if not isinstance(image_orig, np.ndarray):
                # print(f"Warning: Skipping item at index {i} because it's not a NumPy array.")
                continue

            if update_progress:
                if total_overall_images is not None and total_overall_images > 0:
                    overall_processed_count = images_processed_so_far + i + 1
                    progress = int((overall_processed_count / total_overall_images) * progress_cap_percent)
                    message = language_config.IMAGE_PROCESS_IN_PROGRESS.format(overall_processed_count, total_overall_images)
                else:
                    progress = int(((i + 1) / num_images) * progress_cap_percent) # Cap internal
                    message = language_config.ANALYZING_IMAGE.format(i+1,num_images)
                update_progress(progress, message)

            if stop_requested and stop_requested():
                break

            try:
                if image_orig.shape[0] != h or image_orig.shape[1] != w:
                    continue
                if image_orig.dtype != dtype:
                    continue
                num_channels_orig = image_orig.shape[2] if image_orig.ndim == 3 else 1
                if num_channels_orig not in (1, channels_buffer): # Hanya izinkan 1 atau 3 channel input
                     continue

            except Exception as e:
                continue 
            
            current_image_float = self.normalize_image(image_orig, dtype)
            if current_image_float.shape[2] != channels_buffer:
                 continue


            # --- Panggil Fungsi Akumulasi C++ ---
            try:
                c_interface.accumulate_frame(
                    final_image_sum, weight_map_sum, # Target (Writable)
                    current_image_float, reference_image_float, # Input (Read-only)
                    base_window, row_starts, col_starts, # Params
                    tile_h, tile_w, h_ref, w_ref, channels_buffer, # Ukuran & Channel Buffer
                    motion_threshold,
                    mbm_block_h, mbm_block_w, mbm_search_radius, frame_max_multiplier
                )
                processed_frames += 1 # Hanya increment jika pemanggilan berhasil
            except Exception as e:
                #  print(f"ERROR calling C++ accumulate function for frame {i+1}: {e}")
                # Putuskan: Lanjutkan tanpa frame ini atau hentikan?
                raise RuntimeError(f"C++ accumulation failed for frame {i+1}: {e}") # Hentikan

        # --- Normalisasi FINAL (Setelah Loop) ---
        if processed_frames > 0:
            try:
                c_interface.normalize_accumulated(final_image_sum, weight_map_sum, h_ref, w_ref, channels_buffer)
                print("Normalization complete.")
            except Exception as e:
                 raise RuntimeError(language_config.NORMALIZATION_FAILED.format(e))

            # --- PENYIMPANAN PETA BOBOT ---
            if save_weight_map_path:
                print(language_config.OUTPUT_SAVE_WEIGHT_MAP.format(save_weight_map_path))
                try:
                    # --- Normalisasi: Berdasarkan jumlah frame yang diproses ---
                    # Ini menunjukkan 'rata-rata' confidence per frame yang berkontribusi
                    # (sudah termasuk pengaruh base_window)
                    if processed_frames > 0:
                         # Bagi dengan jumlah frame untuk mendapatkan bobot rata-rata per piksel
                         # Nilai maksimum idealnya 1.0 di tengah tile jika confidence selalu 1
                         normalized_weights = weight_map_sum / float(processed_frames)
                    else:
                         normalized_weights = np.zeros_like(weight_map_sum) # Peta hitam jika tidak ada frame

                    # Clamp nilai ke [0, 1] karena pembagian bisa menghasilkan > 1 jika ada overlap tinggi
                    normalized_weights = np.clip(normalized_weights, 0.0, 1.0)

                    # --- Opsional: Tambahkan Blurring pada Visualisasi ---
                    # Jika Anda masih melihat artefak visual antar blok MBM (bukan tile)
                    # atau ingin visualisasi yang lebih mulus secara umum.
                    apply_vis_blur = False
                    if apply_vis_blur:
                        vis_blur_kernel_size = 3
                        normalized_weights = cv2.GaussianBlur(normalized_weights, (vis_blur_kernel_size, vis_blur_kernel_size), 0)
                        normalized_weights = np.clip(normalized_weights, 0.0, 1.0)


                    # Konversi ke uint8 [0, 255]
                    weight_map_vis = (normalized_weights * 255).astype(np.uint8)

                    # Simpan peta bobot sebagai gambar grayscale
                    os.makedirs(os.path.dirname(save_weight_map_path), exist_ok=True)
                    success_save = cv2.imwrite(save_weight_map_path, weight_map_vis)
                    if success_save:
                         print(language_config.SAVING_WEIGHT_MAP)
                    else:
                         print(language_config.FAILED_TO_SAVE_WEIGHT_MAP_TO_PATH.format(save_weight_map_path))

                except Exception as e:
                    traceback.print_exc()


            # --- Denormalisasi, Clipping, Konversi Tipe (di Python) ---
            final_image_normalized = final_image_sum
            final_image_scaled = final_image_normalized * scale_value

            # Konversi kembali ke tipe data asli (uint8/uint16)
            # Jika input asli grayscale, kembalikan grayscale
            if ref_image.ndim == 2 or (ref_image.ndim == 3 and ref_image.shape[2] == 1) :
                final_image_scaled_single_channel = final_image_scaled[:, :, 0]
                min_val = 0
                max_val = np.iinfo(dtype).max
                final_image_output = np.clip(final_image_scaled_single_channel, min_val, max_val).astype(dtype, copy=False)
            elif channels_buffer == 3: # Input asli berwarna
                min_val = 0
                max_val = np.iinfo(dtype).max
                final_image_output = np.clip(final_image_scaled, min_val, max_val).astype(dtype, copy=False)
            
            if stop_requested and stop_requested() and processed_frames < num_images:
                 print(f"WARNING: Returning partially processed image after accumulating {processed_frames} frames.")
            return final_image_output
        else:
            output_shape = (h, w) if ref_image.ndim == 2 else (h, w, ref_image.shape[2])
            return np.zeros(output_shape, dtype=dtype)

def main(db_path, update_progress=None, stop_requested=None, batch_size=10,
         single_process=None, batch_id=None, save_final_weight_map=False, progress_bar=None):
    try:
        image_processor = SimilarityAlgorithmV2(db_path)

        output_name_base = ""
        image_paths = []
        align_dir = os.path.join("database", "align") # Definisikan path folder alignment

        if single_process:
            image_paths = image_processor.get_all_image_paths_for_single_process()
            if image_paths:
                if image_paths[0] and isinstance(image_paths[0], str):
                    ref_image_name = os.path.splitext(os.path.basename(image_paths[0]))[0]
                    output_name_base = f"{ref_image_name}"
                else:
                    output_name_base = "single_process_invalid_path"
            else:
                output_name_base = "single_process_no_images"
        else:
            if batch_id is None:
                raise ValueError(language_config.BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS)
            else:
                pass

            # Lanjutkan dengan mendapatkan path gambar untuk batch
            image_paths = image_processor.get_all_image_paths_for_batch_process(batch_id)
            if image_paths and isinstance(image_paths[0], str):
                ref_image_name = os.path.splitext(os.path.basename(image_paths[0]))[0]
                output_name_base = f"{ref_image_name}"
            else:
                output_name_base = "batch_no_reference"
           
        if not image_paths:
            print(language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return # Keluar jika tidak ada gambar

        # --- Setup Path Output ---
        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)
        output_name_base_safe = "".join(c for c in output_name_base if c.isalnum() or c in ('_', '-')).rstrip()
        if not output_name_base_safe: output_name_base_safe = "stack_result" # Fallback name
        output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_similarityV2.tif")
        weight_map_output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_similarity_weight_map.png")
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))
        if save_final_weight_map:
             print(language_config.OUTPUT_SAVE_WEIGHT_MAP.format(weight_map_output_path))

        # --- Ekstraksi Metadata ---
        metadata_folder = align_dir 
        os.makedirs(metadata_folder, exist_ok=True) 
        metadata_file = os.path.join(metadata_folder, "metadata.json")

        # Panggil ekstraksi metadata hanya jika ada path gambar
        if image_paths:
             if 'extract_all_metadata' in globals():
                  try:
                       extract_all_metadata(image_paths, metadata_file=metadata_file)
                      
                  except Exception as e_meta:
                       traceback.print_exc()
                      
             else:
                  pass
        else:
            pass

        # --- Update progress awal ---
        if update_progress: update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        if single_process:
            global_hdf5_path = os.path.join(align_dir, "aligned_images.h5")
        else:
            global_hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
        processed_batches_results = []
        images_processed_count = 0
        total_images = 0

        # --- Logika Pemrosesan Utama (Batching dari HDF5 atau Path) ---
        use_hdf5 = os.path.exists(global_hdf5_path)

        if use_hdf5:
            print(language_config.PROCESSING_IMAGE_FROM_HDF5.format(global_hdf5_path))
            try:
                # Dapatkan total gambar dari HDF5 untuk progress
                with h5py.File(global_hdf5_path, 'r') as h5f_check:
                    total_images = len(h5f_check.keys())
                print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))

                if total_images == 0:
                    if update_progress: update_progress(100, "File HDF5 is empty.")
                    return

                total_batches = (total_images + batch_size - 1) // batch_size
                print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))

                with h5py.File(global_hdf5_path, 'r') as h5f:
                    keys = list(h5f.keys()) # Ambil keys sekali saja
                    for batch_start in range(0, total_images, batch_size):
                        current_batch_num = (batch_start // batch_size) + 1
                        print(f"\n" + language_config.PROCESSING_BATCH.format(current_batch_num, total_batches, batch_start))

                        if stop_requested and stop_requested():
                            print(language_config.PROCESS_TERMINATED_BY_USER)
                            break 
                        
                        batch_keys = keys[batch_start:min(batch_start + batch_size, total_images)]
                        print(language_config.LOAD_IMAGE_FROM_HDF5.format(len(batch_keys)))
                        batch_images = []
                        keys_loaded_in_batch = 0
                        for key in batch_keys:
                            if stop_requested and stop_requested(): break
                            try:
                                batch_images.append(np.array(h5f[key]))
                                keys_loaded_in_batch += 1
                            except Exception as e:
                                print(language_config.ERROR_WHILE_RETRIEVING_KEY_FROM_HD5F.format(key, e))
                        if stop_requested and stop_requested(): break # Cek lagi setelah loop key

                        if not batch_images:
                            print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num))
                            continue 
                        
                        print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images)))
                        try:
                             batch_result = image_processor.similarity_mfnr(
                                 batch_images,
                                 update_progress=update_progress,
                                 stop_requested=stop_requested,
                                 total_overall_images=total_images,
                                 images_processed_so_far=images_processed_count
                                
                             )
                        except Exception as e_sim_batch:
                             traceback.print_exc()
                             batch_result = None 
                             
                        if stop_requested and stop_requested():
                            break

                        if batch_result is not None:
                             processed_batches_results.append(batch_result)
                             images_processed_count += len(batch_images)                             
                        else:
                            print(f"Batch {current_batch_num} processing failed or returned None.")
                         
            except Exception as e:
                print(language_config.ERROR_IN_READING_FILE_HDF5.format(e))
                traceback.print_exc()
                if update_progress: update_progress(0, language_config.ERROR_IN_READING_FILE_HDF5.format(e))
                return 

        else: 
            print(language_config.NO_HDF5_FILE_PROCESSING_FROM_PATH)
            total_images = len(image_paths)
            print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))

            if total_images == 0:
                print(language_config.NO_IMAGE_PATH_PROCESSED_IMAGE) # Redundan, sudah dicek di atas, tapi aman
                if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
                return

            total_batches = (total_images + batch_size - 1) // batch_size
            print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))

            for batch_start in range(0, total_images, batch_size):
                current_batch_num = (batch_start // batch_size) + 1
                print(f"\n" + language_config.PROCESSING_BATCH.format(current_batch_num, total_batches, batch_start))

                if stop_requested and stop_requested():
                    print(language_config.PROCESS_TERMINATED_BY_USER)
                    break

                batch_paths = image_paths[batch_start:min(batch_start + batch_size, total_images)]
                batch_images = image_processor.load_images_from_paths(batch_paths, stop_requested)
                if stop_requested and stop_requested(): break # Cek setelah loading

                if not batch_images:
                    print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num))
                    continue

                print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images)))
                try:
                    batch_result = image_processor.similarity_mfnr(
                        batch_images,
                        update_progress=update_progress,
                        stop_requested=stop_requested,
                        total_overall_images=total_images,
                        images_processed_so_far=images_processed_count
                    )
                except Exception as e_sim_batch:
                      traceback.print_exc()
                      batch_result = None

                if stop_requested and stop_requested():
                    break

                if batch_result is not None:
                    processed_batches_results.append(batch_result)
                    images_processed_count += len(batch_images)
                else:
                    print(f"Batch {current_batch_num} processing failed or returned None.")


        # --- Fine-Tuning / Pemrosesan Akhir (jika ada hasil batch) ---
        if stop_requested and stop_requested():
            pass
        elif processed_batches_results:
            num_fine_tuning_inputs = len(processed_batches_results)
            print(f"\n--- {language_config.STARTING_ENHANCEMENT} ({num_fine_tuning_inputs} batch results) ---")

            fine_tuning_start_progress = 95
            fine_tuning_end_progress = 99

            # Wrapper untuk progress callback fine-tuning
            def fine_tuning_update_progress(inner_progress, message):
                # Map progress internal [0, 100] ke rentang [start, end]
                mapped_progress = fine_tuning_start_progress + int((inner_progress / 100.0) * (fine_tuning_end_progress - fine_tuning_start_progress))
                if update_progress:
                    # Jangan update jika sudah diminta berhenti
                    if not (stop_requested and stop_requested()):
                        update_progress(mapped_progress, language_config.ENHANCEMENT.format(message))

            if update_progress: update_progress(fine_tuning_start_progress, language_config.STARTING_ENHANCEMENT)

            final_weight_map_path_arg = weight_map_output_path if save_final_weight_map else None
            if final_weight_map_path_arg:
                 print(f"Final weight map saving is ENABLED to: {final_weight_map_path_arg}")
            else:
                 print("Final weight map saving is DISABLED.")

            # Panggil similarity_mfnr untuk fine-tuning
            final_result = None
            try:
                 final_result = image_processor.similarity_mfnr(
                     processed_batches_results, # Input adalah hasil dari batch sebelumnya
                     update_progress=fine_tuning_update_progress, # Wrapper callback
                     stop_requested=stop_requested,
                     save_weight_map_path=final_weight_map_path_arg,
                     
                 )
            except Exception as e_fine_tune:
                  traceback.print_exc()
                  final_result = None 

            if stop_requested and stop_requested():
                pass
            
            elif final_result is not None:
                 ref_path_for_save = image_paths[0] if image_paths and isinstance(image_paths[0], str) else None
                 save_success = save_image(final_result, output_path, reference_image_path=ref_path_for_save)
                 if save_success:
                    final_message = f"{language_config.IMAGE_PROCESS_FINISHED}: {os.path.basename(output_path)}"
                    print(final_message)
                    if update_progress: update_progress(100, final_message)

                    if not single_process and batch_id is not None:
                        batch_hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
                        if os.path.exists(batch_hdf5_path):
                            try:
                                os.remove(batch_hdf5_path)
                            except Exception as e:
                                pass
                        else:
                            pass
            else:
                print(language_config.FAILED_IMAGE_ENHANCEMENT)
                if update_progress: update_progress(100, language_config.FAILED_IMAGE_ENHANCEMENT) # 100% tapi pesan gagal

        elif not (stop_requested and stop_requested()): # Jika tidak ada hasil batch DAN tidak dibatalkan
            print(language_config.DATA_FAILED_COMPLETION_CREATED)
            if update_progress:
                update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED)

        if stop_requested and stop_requested():
             if update_progress and progress_bar: update_progress(progress_bar.value(), "Proses dibatalkan.") # Update progress terakhir


    except ValueError as ve:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(ve))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
             update_progress(0, error_message)
    except FileNotFoundError as fnf:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(fnf))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
             update_progress(0, error_message)
    except RuntimeError as rte:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(rte))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)
    except Exception as e: 
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)
    finally:
       pass


def running_similarity_v2(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_SIMILARITY_V2)
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