import ctypes
import os
import numpy as np

def call_similarity_motion(final_image, weight_map, current_image, reference_image,
                                  base_window, row_starts, col_starts,
                                  tile_h, tile_w, h, w, channels,
                                  motion_threshold, noise_threshold, scale, alpha,
                                  max_passes, epsilon,
                                  lib_path):
    """
    Membungkus pemanggilan fungsi accumulate_tiles_jit dari shared library.
    """
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"Library not found in {lib_path}")
    
    # Memuat library C++
    lib = ctypes.CDLL(lib_path)
    
    # Tetapkan tipe argumen untuk fungsi accumulate_tiles_jit
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
        ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
        ctypes.c_int, ctypes.c_float
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
        ctypes.c_float(motion_threshold), ctypes.c_float(noise_threshold),
        ctypes.c_float(scale), ctypes.c_float(alpha),
        ctypes.c_int(max_passes), ctypes.c_float(epsilon)
    )
    
    
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