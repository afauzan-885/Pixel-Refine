import numpy as np
from numba import njit, prange

@njit(inline='always')
def compute_motion_metrics(current_tile, ref_tile, motion_threshold, noise_threshold):
    """
    Menghitung metrik gerakan secara sederhana menggunakan perulangan.
    Fungsi ini mengembalikan similarity_weight dan adaptive_threshold.
    Implementasi ini hanya menggunakan operasi yang didukung Numba.
    """
    h, w, channels = current_tile.shape
    total_diff = 0.0
    count = 0
    for i in range(h):
        for j in range(w):
            for ch in range(channels):
                total_diff += abs(current_tile[i, j, ch] - ref_tile[i, j, ch])
                count += 1
    dz = total_diff / count

    # Versi sederhana adaptive threshold
    adaptive_threshold = motion_threshold + noise_threshold * dz
    similarity_weight = 1.0 if dz < adaptive_threshold else np.exp(-dz / adaptive_threshold)
    return similarity_weight, adaptive_threshold

@njit(parallel=True)
def accumulate_tiles(final_image, weight_map, current_image, reference_image,
                     base_window, row_starts, col_starts,
                     tile_h, tile_w, motion_threshold, noise_threshold, scale):
    h, w, channels = current_image.shape
    # Looping parallel untuk tiap tile
    for i in prange(row_starts.shape[0]):
        r = row_starts[i]
        for j in range(col_starts.shape[0]):
            c = col_starts[j]
            # Pastikan indeks tidak keluar batas
            if r + tile_h > h or c + tile_w > w:
                continue

            # Mengambil tile dengan slicing (pastikan arraynya contiguous)
            current_tile = current_image[r:r+tile_h, c:c+tile_w, :]
            ref_tile = reference_image[r:r+tile_h, c:c+tile_w, :]
            
            # Panggil fungsi perhitungan metrik yang sudah dipisah
            similarity_weight, _ = compute_motion_metrics(current_tile, ref_tile, motion_threshold, noise_threshold)
            
            # Akumulasi nilai untuk tiap piksel pada tile
            for a in range(tile_h):
                for b in range(tile_w):
                    for ch in range(channels):
                        final_image[r + a, c + b, ch] += current_image[r + a, c + b, ch] * base_window[a, b] * similarity_weight * scale
                    weight_map[r + a, c + b] += base_window[a, b] * similarity_weight
