import numpy as np
from numba import njit, prange
# Fungsi helper ini hanya digunakan secara internal, jadi kita tidak perlu meng-export-nya.
@njit(inline='always')
def compute_motion_metrics(current_tile, ref_tile, motion_threshold, noise_threshold, max_passes=10, epsilon=1e-4):
    """
    Menggunakan Mean Squared Error (MSE) dengan multi-pass untuk memperbaiki threshold adaptif.
    """
    # Vectorize
    current_tile_flat = current_tile.ravel()
    ref_tile_flat = ref_tile.ravel()
    
    # Hitung MSE awal
    mse_score = np.mean((current_tile_flat - ref_tile_flat) ** 2)
    dz = mse_score  

    # Inisialisasi threshold adaptif
    adaptive_threshold = motion_threshold + noise_threshold * dz

    # Multi-pass refinement
    for _ in range(max_passes):
        prev_threshold = adaptive_threshold
        
        # Perbaikan threshold adaptif berdasarkan perbedaan sebelumnya
        adaptive_threshold = motion_threshold + noise_threshold * (dz / (1 + dz / adaptive_threshold))

        # Jika perubahan kecil, hentikan iterasi
        if abs(adaptive_threshold - prev_threshold) < epsilon:
            break

    # Similarity weight menggunakan threshold akhir
    similarity_weight = np.exp(-dz / adaptive_threshold)

    return similarity_weight, adaptive_threshold


@njit (parallel=True, nogil=True)
def accumulate_tiles_jit(final_image, weight_map, current_image, reference_image,
                         base_window, row_starts, col_starts,
                         tile_h, tile_w, motion_threshold, noise_threshold, scale):
    h, w, channels = current_image.shape
    for i in prange(row_starts.shape[0]):  # Gunakan prange untuk paralelisasi
        r = row_starts[i]
        for j in range(col_starts.shape[0]):
            c = col_starts[j]
            if r + tile_h > h or c + tile_w > w:
                continue
            current_tile = current_image[r:r+tile_h, c:c+tile_w, :]
            ref_tile = reference_image[r:r+tile_h, c:c+tile_w, :]
            similarity_weight, _ = compute_motion_metrics(current_tile, ref_tile, motion_threshold, noise_threshold)
            for a in range(tile_h):
                for b in range(tile_w):
                    for ch in range(channels):
                        final_image[r + a, c + b, ch] += current_image[r + a, c + b, ch] * base_window[a, b] * similarity_weight * scale
                    weight_map[r + a, c + b] += base_window[a, b] * similarity_weight

def accumulate_tiles(final_image, weight_map, current_image, reference_image,
                     base_window, row_starts, col_starts,
                     tile_h, tile_w, motion_threshold, noise_threshold, scale):
    accumulate_tiles_jit(final_image, weight_map, current_image, reference_image,
                         base_window, row_starts, col_starts,
                         tile_h, tile_w, motion_threshold, noise_threshold, scale)
