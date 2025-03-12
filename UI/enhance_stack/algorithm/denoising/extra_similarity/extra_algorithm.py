# import numpy as np
# from numba import njit, prange

# @njit(inline='always')
# def compute_motion_metrics(current_tile, ref_tile, prev_threshold, motion_threshold, noise_threshold, alpha, max_passes=200, epsilon=1e-3):
#     """
#     Menggunakan MSE dengan multi-pass dan perbaikan robustness menggunakan estimasi bertahap.
#     """
#     # Vectorize
#     current_tile_flat = current_tile.ravel()
#     ref_tile_flat = ref_tile.ravel()
    
#     # Hitung MSE awal
#     mse_score = np.mean((current_tile_flat - ref_tile_flat) ** 2)
#     dz = mse_score  

#     # Normalisasi perbedaan dengan estimasi noise
#     sigma_noise = np.std(current_tile_flat - ref_tile_flat)
#     dz_norm = dz / (1 + sigma_noise)

#     # Inisialisasi threshold adaptif
#     new_threshold = motion_threshold + noise_threshold * dz_norm
#     adaptive_threshold = alpha * prev_threshold + (1 - alpha) * new_threshold

#     # Multi-pass refinement
#     for _ in range(max_passes):
#         prev_value = adaptive_threshold
#         adaptive_threshold = alpha * prev_value + (1 - alpha) * (motion_threshold + noise_threshold * (dz / (1 + dz / prev_value)))

#         # Jika perubahan kecil, hentikan iterasi
#         if abs(adaptive_threshold - prev_value) < epsilon:
#             break

#     # Similarity weight menggunakan threshold akhir
#     similarity_weight = np.exp(-dz / (adaptive_threshold + epsilon))

#     return similarity_weight, adaptive_threshold

# @njit (parallel=True, nogil=True)
# def accumulate_tiles_jit(final_image, weight_map, current_image, reference_image,
#                          base_window, row_starts, col_starts,
#                          tile_h, tile_w, motion_threshold, noise_threshold, scale, alpha=0.8, max_passes=200, epsilon=1e-3):
#     h, w, channels = current_image.shape
#     for i in prange(row_starts.shape[0]):  
#         r = row_starts[i]
#         for j in range(col_starts.shape[0]):
#             c = col_starts[j]
#             if r + tile_h > h or c + tile_w > w:
#                 continue
#             current_tile = current_image[r:r+tile_h, c:c+tile_w, :]
#             ref_tile = reference_image[r:r+tile_h, c:c+tile_w, :]

#             # Inisialisasi threshold pertama dengan motion_threshold
#             prev_threshold = motion_threshold

#             # Panggil compute_motion_metrics dengan semua parameter yang diperlukan
#             similarity_weight, _ = compute_motion_metrics(current_tile, ref_tile, prev_threshold, motion_threshold, noise_threshold, alpha, max_passes, epsilon)

#             for a in range(tile_h):
#                 for b in range(tile_w):
#                     for ch in range(channels):
#                         final_image[r + a, c + b, ch] += current_image[r + a, c + b, ch] * base_window[a, b] * similarity_weight * scale
#                     weight_map[r + a, c + b] += base_window[a, b] * similarity_weight

# def accumulate_tiles(final_image, weight_map, current_image, reference_image,
#                      base_window, row_starts, col_starts,
#                      tile_h, tile_w, motion_threshold, noise_threshold, scale, alpha=0.8, max_passes=200, epsilon=1e-3):
#     accumulate_tiles_jit(final_image, weight_map, current_image, reference_image,
#                          base_window, row_starts, col_starts,
#                          tile_h, tile_w, motion_threshold, noise_threshold, scale, alpha, max_passes, epsilon)
import ctypes
import os
import numpy as np


def load_motionmetrics_library(lib_path='UI/enhance_stack/algorithm/denoising/extra_similarity/compute_motion.dll'):
    """
    Memuat shared library C++ yang telah dikompilasi.
    Pastikan lib_path mengarah ke file shared library yang sesuai.
    """
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"Library tidak ditemukan di {lib_path}")
    return ctypes.CDLL(lib_path)

def setup_accumulate_tiles_jit(lib):
    """
    Menetapkan tipe argumen untuk fungsi accumulate_tiles_jit dalam library.
    Fungsi signature di C++ adalah:
      void accumulate_tiles_jit(float* final_image, float* weight_map,
                                const float* current_image, const float* reference_image,
                                const float* base_window,
                                const int* row_starts, const int* col_starts,
                                int num_row_starts, int num_col_starts,
                                int tile_h, int tile_w,
                                int h, int w, int channels,
                                float motion_threshold, float noise_threshold, float scale,
                                float alpha, int max_passes, float epsilon)
    """
    lib.accumulate_tiles_jit.argtypes = [
        np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),  # final_image (h x w x channels)
        np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),  # weight_map (h x w)
        np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),  # current_image (h x w x channels)
        np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),  # reference_image (h x w x channels)
        np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),  # base_window (tile_h x tile_w)
        np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),    # row_starts
        np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),    # col_starts
        ctypes.c_int, ctypes.c_int,      # num_row_starts, num_col_starts
        ctypes.c_int, ctypes.c_int,      # tile_h, tile_w
        ctypes.c_int, ctypes.c_int, ctypes.c_int,  # h, w, channels
        ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,  # motion_threshold, noise_threshold, scale, alpha
        ctypes.c_int, ctypes.c_float     # max_passes, epsilon
    ]
    return lib.accumulate_tiles_jit

def call_accumulate_tiles_compile(lib, final_image, weight_map, current_image, reference_image,
                              base_window, row_starts, col_starts,
                              tile_h, tile_w, h, w, channels,
                              motion_threshold, noise_threshold, scale, alpha,
                              max_passes, epsilon):
    """
    Membungkus pemanggilan fungsi accumulate_tiles_jit dari shared library.
    Parameter:
      - final_image: numpy array float32 dengan shape (h, w, channels)
      - weight_map: numpy array float32 dengan shape (h, w)
      - current_image, reference_image: numpy array float32 dengan shape (h, w, channels)
      - base_window: numpy array float32 dengan shape (tile_h, tile_w)
      - row_starts, col_starts: numpy array int32 berisi indeks awal tiap tile
      - tile_h, tile_w: ukuran tile
      - h, w, channels: dimensi citra penuh
      - motion_threshold, noise_threshold, scale, alpha, max_passes, epsilon: parameter algoritma
    """
    # Pastikan array berurutan (C-contiguous) dan dengan tipe data yang tepat
    final_image = np.ascontiguousarray(final_image, dtype=np.float32)
    weight_map = np.ascontiguousarray(weight_map, dtype=np.float32)
    current_image = np.ascontiguousarray(current_image, dtype=np.float32)
    reference_image = np.ascontiguousarray(reference_image, dtype=np.float32)
    base_window = np.ascontiguousarray(base_window, dtype=np.float32)
    row_starts = np.ascontiguousarray(row_starts, dtype=np.int32)
    col_starts = np.ascontiguousarray(col_starts, dtype=np.int32)
    
    num_row_starts = row_starts.size
    num_col_starts = col_starts.size

    # Panggil fungsi accumulate_tiles_jit dari shared library
    lib.accumulate_tiles_jit(
        final_image, weight_map,
        current_image, reference_image, base_window,
        row_starts, col_starts,
        ctypes.c_int(num_row_starts), ctypes.c_int(num_col_starts),
        ctypes.c_int(tile_h), ctypes.c_int(tile_w),
        ctypes.c_int(h), ctypes.c_int(w), ctypes.c_int(channels),
        ctypes.c_float(motion_threshold), ctypes.c_float(noise_threshold),
        ctypes.c_float(scale), ctypes.c_float(alpha),
        ctypes.c_int(max_passes), ctypes.c_float(epsilon)
    )