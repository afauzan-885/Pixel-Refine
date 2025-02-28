import ctypes
import numpy as np
import os

# Menentukan path ke DLL (asumsikan berada pada direktori yang sama)
dll_path = os.path.join(os.path.dirname(__file__), "accumulate_tiles.dll")
lib = ctypes.CDLL(dll_path)

# Tentukan tipe argumen dan nilai kembali untuk fungsi accumulate_tiles di DLL
lib.accumulate_tiles.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.double, flags="C_CONTIGUOUS"),  # final_image
    np.ctypeslib.ndpointer(dtype=np.double, flags="C_CONTIGUOUS"),  # weight_map
    np.ctypeslib.ndpointer(dtype=np.double, flags="C_CONTIGUOUS"),  # current_image
    np.ctypeslib.ndpointer(dtype=np.double, flags="C_CONTIGUOUS"),  # reference_image
    np.ctypeslib.ndpointer(dtype=np.double, flags="C_CONTIGUOUS"),  # base_window
    np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS"),   # row_starts
    np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS"),   # col_starts
    ctypes.c_int,   # num_rows
    ctypes.c_int,   # num_cols
    ctypes.c_int,   # h
    ctypes.c_int,   # w
    ctypes.c_int,   # channels
    ctypes.c_int,   # tile_h
    ctypes.c_int,   # tile_w
    ctypes.c_double,# motion_threshold
    ctypes.c_double,# noise_threshold
    ctypes.c_double # scale
]
lib.accumulate_tiles.restype = None

def accumulate_tiles_py(final_image, weight_map, current_image, reference_image, base_window,
                        row_starts, col_starts, tile_h, tile_w, motion_threshold, noise_threshold, scale):
    """
    Fungsi wrapper untuk memanggil fungsi accumulate_tiles dari DLL.
    Semua array diharapkan merupakan numpy array dengan tipe data dan layout yang benar.
    """
    h, w, channels = current_image.shape
    num_rows = row_starts.shape[0]
    num_cols = col_starts.shape[0]

    # Pastikan array bersifat contiguous dan memiliki tipe data yang sesuai
    final_image = np.ascontiguousarray(final_image, dtype=np.double)
    weight_map = np.ascontiguousarray(weight_map, dtype=np.double)
    current_image = np.ascontiguousarray(current_image, dtype=np.double)
    reference_image = np.ascontiguousarray(reference_image, dtype=np.double)
    base_window = np.ascontiguousarray(base_window, dtype=np.double)
    row_starts = np.ascontiguousarray(row_starts, dtype=np.int32)
    col_starts = np.ascontiguousarray(col_starts, dtype=np.int32)

    # Panggil fungsi dari DLL
    lib.accumulate_tiles(final_image, weight_map, current_image, reference_image, base_window,
                         row_starts, col_starts,
                         num_rows, num_cols, h, w, channels,
                         tile_h, tile_w, motion_threshold, noise_threshold, scale)

# --- Contoh Penggunaan ---
if __name__ == "__main__":
    # Definisikan dimensi gambar dan tile
    h, w, channels = 100, 100, 3
    tile_h, tile_w = 10, 10

    # Buat contoh data (misalnya, gambar acak)
    current_image = np.random.rand(h, w, channels)
    reference_image = np.random.rand(h, w, channels)
    final_image = np.zeros((h, w, channels), dtype=np.double)
    weight_map = np.zeros((h, w), dtype=np.double)
    base_window = np.ones((tile_h, tile_w), dtype=np.double)

    # Misal, pilih beberapa titik mulai untuk tiles
    row_starts = np.array([0, 10, 20, 30], dtype=np.int32)
    col_starts = np.array([0, 10, 20, 30], dtype=np.int32)

    # Parameter threshold dan scale
    motion_threshold = 0.1
    noise_threshold = 0.01
    scale = 1.0

    # Panggil fungsi accumulate_tiles
    accumulate_tiles_py(final_image, weight_map, current_image, reference_image, base_window,
                        row_starts, col_starts, tile_h, tile_w, motion_threshold, noise_threshold, scale)

    # Cetak hasil (atau lakukan proses selanjutnya)
    print("Final image:\n", final_image)
    print("Weight map:\n", weight_map)
