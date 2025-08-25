import ctypes
import os
import numpy as np

class SimilaritySpatialInterface:
    """Membungkus pemanggilan fungsi C++ untuk similarity_mfnr_v2."""

    def __init__(self, lib_path):
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Shared library not found: {lib_path}")
        try:
            self.clib = ctypes.CDLL(lib_path)
            self._define_argtypes()
        except OSError as e:
            raise OSError(f"Error loading shared library {lib_path}: {e}")
        except AttributeError as e:
             raise AttributeError(f"Function not found in DLL or error setting argtypes. Did you compile C++ correctly? Error: {e}")

    def _define_argtypes(self):
        self.clib.accumulate_frame_weighted_jit.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS, WRITEABLE'), # final_image_sum_ptr
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS, WRITEABLE'), # weight_map_sum_ptr
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),          # current_image_ptr
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),          # reference_image_ptr
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),          # base_window_ptr
            ctypes.c_void_p,                                                                  # stability_map_ptr
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),             # row_starts
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),             # col_starts
            ctypes.c_int, # num_row_starts
            ctypes.c_int, # num_col_starts
            ctypes.c_int, # tile_h
            ctypes.c_int, # tile_w
            ctypes.c_int, # h_img
            ctypes.c_int, # w_img
            ctypes.c_int, # channels
            ctypes.c_float, # motion_sensitivity
            ctypes.c_float  # noise_offset_factor
        ]
        # --- AKHIR PERBAIKAN ---

        self.clib.accumulate_frame_weighted_jit.restype = None
        
        self.clib.normalize_accumulated_image_jit.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS, WRITEABLE'),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
            ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        self.clib.normalize_accumulated_image_jit.restype = None

    def call_accumulate_frame_weighted(self, final_image_sum, weight_map_sum, current_image, reference_image,
                                       base_window, stability_map, row_starts, col_starts,
                                       tile_h, tile_w, h, w, channels,
                                       motion_sensitivity, noise_offset_factor):
        
        stability_map_ptr = None
        if stability_map is not None:
            if not stability_map.flags['C_CONTIGUOUS']:
                stability_map = np.ascontiguousarray(stability_map)
            stability_map_ptr = stability_map.ctypes.data_as(ctypes.c_void_p)
        
        self.clib.accumulate_frame_weighted_jit(
            final_image_sum, weight_map_sum, current_image, reference_image, base_window,
            stability_map_ptr, row_starts, col_starts, len(row_starts), len(col_starts),
            tile_h, tile_w, h, w, channels,
            motion_sensitivity, noise_offset_factor
        )
        
    def call_normalize_accumulated(self, final_image_sum, weight_map_sum, h, w, channels):
        self.clib.normalize_accumulated_image_jit(final_image_sum, weight_map_sum, h, w, channels)
        
class SimilarityFrequencyInterface:
    """Membungkus pemanggilan fungsi C++ untuk similarity_mfnr_v2."""

    def __init__(self, lib_path):
        """
        Memuat library C++, mendefinisikan argtypes, dan menyimpan objek clib.
        """
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Shared library not found: {lib_path}")
        try:
            self.clib = ctypes.CDLL(lib_path)
            self._define_argtypes()
        except OSError as e:
            raise OSError(f"Error loading shared library {lib_path}: {e}")
        except AttributeError as e:
             raise AttributeError(f"Function not found in DLL or error setting argtypes. Did you compile C++ correctly? Error: {e}")

    def _define_argtypes(self):
        """Mendefinisikan argtypes untuk semua fungsi C++ yang digunakan."""
      
        self.clib.accumulate_frame_weighted_jit.restype = None # Sesuaikan nama fungsi jika berbeda
        self.clib.accumulate_frame_weighted_jit.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'), # final_image_sum
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), # weight_map_sum
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'), # current_image
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'), # reference_image
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), # base_window
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),   # row_starts
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),   # col_starts
            ctypes.c_int, # num_row_starts
            ctypes.c_int, # num_col_starts
            ctypes.c_int, ctypes.c_int, # tile_h, tile_w
            ctypes.c_int, ctypes.c_int, ctypes.c_int, # h_img, w_img, channels
            ctypes.c_int, ctypes.c_int, # block_h, block_w
            ctypes.c_float  # dft_wiener_c_factor <<--- ARGTYPE BARU
        ]

        self.clib.accumulate_frame_weighted_jit.restype = None
        
        self.clib.normalize_accumulated_image_jit.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS, WRITEABLE'), # 1 final_image_ptr
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),           # 2 weight_map_sum_ptr
            ctypes.c_int, ctypes.c_int, ctypes.c_int # 3-5 h, w, channels_buffer
        ]
        self.clib.normalize_accumulated_image_jit.restype = None

    def call_accumulate_frame_weighted(self, clib_instance, final_image_sum, weight_map_sum,
                                     current_image_float, reference_image_float,
                                     base_window, row_starts, col_starts,
                                     tile_h, tile_w, h_ref, w_ref, channels_buffer,
                                     block_h, block_w, 
                                     dft_wiener_c_factor):
        clib_instance.accumulate_frame_weighted_jit( 
            final_image_sum, weight_map_sum,
            current_image_float, reference_image_float,
            base_window, row_starts, col_starts,
            len(row_starts), len(col_starts), 
            tile_h, tile_w,
            h_ref, w_ref, channels_buffer,
            block_h, block_w,
            ctypes.c_float(dft_wiener_c_factor)
        )

    def call_normalize_accumulated(self, lib, final_image_sum, weight_map_sum, h, w, channels):
        """
        Membungkus pemanggilan normalize_accumulated_image_jit.
        ASUMSI: Semua argumen NumPy sudah C-contiguous.
        ASUMSI: argtypes sudah didefinisikan pada objek 'lib'.
        """
        # Langsung panggil fungsi C dengan argumen yang sudah disiapkan
        lib.normalize_accumulated_image_jit(final_image_sum, weight_map_sum, h, w, channels)
        # Catatan: final_image_sum dimodifikasi secara inplace oleh fungsi C

def call_weighted_average_motion(final_image, weight_map, current_image, reference_image,
                           base_window, row_starts, col_starts,
                           tile_h, tile_w, h, w, channels,
                           motion_threshold, scale, alpha,
                           max_passes, epsilon,
                           lib_path):
    """
    Membungkus pemanggilan fungsi accumulate_tiles_jit dari shared library.
    """
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"Library not found in {lib_path}")
    
    # Memuat library C++
    lib = ctypes.CDLL(lib_path)
    
    # Tetapkan tipe argumen untuk fungsi accumulate_tiles_jit (tanpa noise_threshold)
    lib.accumulate_tiles_jit.argtypes = [
        np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),
        np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
        np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),
        np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),
        np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
        np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),
        np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),
        ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int, ctypes.c_int,
        ctypes.c_float,    # motion_threshold
        ctypes.c_float,    # scale
        ctypes.c_float,    # alpha
        ctypes.c_int,      # max_passes
        ctypes.c_float     # epsilon
    ]
    
    # Pastikan array dalam format C-contiguous
    final_image = np.ascontiguousarray(final_image, dtype=np.float32)
    weight_map = np.ascontiguousarray(weight_map, dtype=np.float32)
    current_image = np.ascontiguousarray(current_image, dtype=np.float32)
    reference_image = np.ascontiguousarray(reference_image, dtype=np.float32)
    base_window = np.ascontiguousarray(base_window, dtype=np.float32)
    row_starts = np.ascontiguousarray(row_starts, dtype=np.int32)
    col_starts = np.ascontiguousarray(col_starts, dtype=np.int32)
    
    num_row_starts = row_starts.size
    num_col_starts = col_starts.size
    
    # Panggil fungsi dari library C++
    lib.accumulate_tiles_jit(
        final_image, weight_map,
        current_image, reference_image, base_window,
        row_starts, col_starts,
        ctypes.c_int(num_row_starts), ctypes.c_int(num_col_starts),
        ctypes.c_int(tile_h), ctypes.c_int(tile_w),
        ctypes.c_int(h), ctypes.c_int(w), ctypes.c_int(channels),
        ctypes.c_float(motion_threshold),
        ctypes.c_float(scale), ctypes.c_float(alpha),
        ctypes.c_int(max_passes), ctypes.c_float(epsilon)
    )



### Fungsi untuk menghitung threshold berdasarkan estimasi noise

def call_accumulate_frame_weighted_flow_motion(lib, final_image_sum, weight_map_sum, current_image, reference_image,
                                   base_window, row_starts, col_starts,
                                   tile_h, tile_w, h, w, channels,
                                   base_motion_threshold, # Ganti nama agar jelas
                                   estimated_noise_sigma, # <-- TAMBAHKAN
                                   block_h, block_w, search_radius, frame_max_adaptive_multiplier):
    """
    Membungkus pemanggilan accumulate_frame_weighted_jit.
    ASUMSI: Argumen NumPy sudah C-contiguous & argtypes sudah di set.
    """
    lib.accumulate_frame_weighted_jit(
        final_image_sum, weight_map_sum, current_image, reference_image, base_window,
        row_starts, col_starts, len(row_starts), len(col_starts),
        tile_h, tile_w, h, w, channels,
        base_motion_threshold, # Teruskan base threshold
        estimated_noise_sigma, # <-- Teruskan sigma noise
        block_h, block_w, search_radius, frame_max_adaptive_multiplier
    )

def call_normalize_accumulated_flow_motion(lib, final_image_sum, weight_map_sum, h, w, channels):
    """
    Membungkus pemanggilan normalize_accumulated_image_jit.
    ASUMSI: Semua argumen NumPy sudah C-contiguous.
    ASUMSI: argtypes sudah didefinisikan pada objek 'lib'.
    """
    # Langsung panggil fungsi C dengan argumen yang sudah disiapkan
    lib.normalize_accumulated_image_jit(final_image_sum, weight_map_sum, h, w, channels)
    # Catatan: final_image_sum dimodifikasi secara inplace oleh fungsi C
    
def estimate_noise_stddev_simple(image_float_gray, block_size=8, percentile=10):
    """
    Estimasi standar deviasi noise Gaussian secara sederhana
    dengan mencari blok paling 'datar'. Input harus grayscale float [0, 1].
    """
    h, w = image_float_gray.shape
    if h < block_size or w < block_size:
        print(f"Warning: Image ({h}x{w}) smaller than block size ({block_size}), using overall stddev.")
        return np.std(image_float_gray).astype(np.float32)

    block_stddevs = []
    block_coords = [] # Simpan koordinat blok

    # Loop over blocks untuk hitung stddev
    for r in range(0, h - block_size + 1, block_size):
        for c in range(0, w - block_size + 1, block_size):
            block = image_float_gray[r:r+block_size, c:c+block_size]
            block_stddevs.append(np.std(block))
            block_coords.append((r, c)) # Simpan posisi blok

    if not block_stddevs:
        print("Warning: No blocks processed for noise estimation. Using overall stddev.")
        return np.std(image_float_gray).astype(np.float32)

    # Ambil stddev pada persentil rendah
    percentile = max(0, min(100, percentile))
    try:
        threshold_stddev = np.percentile(block_stddevs, percentile)
    except IndexError:
         print("Warning: block_stddevs empty. Using overall stddev.")
         return np.std(image_float_gray).astype(np.float32)

    # --- Cara Lebih Sederhana Mengumpulkan Piksel Datar ---
    flat_pixels_list = []
    for i, (r, c) in enumerate(block_coords):
        if block_stddevs[i] <= threshold_stddev:
            block = image_float_gray[r:r+block_size, c:c+block_size]
            flat_pixels_list.append(block.flatten()) # Tambahkan piksel blok datar ke list

    if not flat_pixels_list:
        print(f"Warning: No blocks found below {percentile}th percentile stddev ({threshold_stddev:.4f}). Using overall stddev.")
        estimated_noise_stddev = np.std(image_float_gray).astype(np.float32)
    else:
        # Gabungkan semua piksel dari blok datar menjadi satu array
        all_flat_pixels = np.concatenate(flat_pixels_list)
        # Hitung stddev dari gabungan piksel ini
        estimated_noise_stddev = np.std(all_flat_pixels).astype(np.float32)
    # ------------------------------------------------------

    return estimated_noise_stddev