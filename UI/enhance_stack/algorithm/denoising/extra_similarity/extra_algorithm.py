import numpy as np
from numba import njit, prange

@njit(inline='always')
def compute_motion_metrics(current_tile, ref_tile, prev_threshold, motion_threshold, noise_threshold, alpha, max_passes=200, epsilon=1e-3):
    """
    Menggunakan MSE dengan multi-pass dan perbaikan robustness menggunakan estimasi bertahap.
    """
    # Vectorize
    current_tile_flat = current_tile.ravel()
    ref_tile_flat = ref_tile.ravel()
    
    # Hitung MSE awal
    mse_score = np.mean((current_tile_flat - ref_tile_flat) ** 2)
    dz = mse_score  

    # Normalisasi perbedaan dengan estimasi noise
    sigma_noise = np.std(current_tile_flat - ref_tile_flat)
    dz_norm = dz / (1 + sigma_noise)

    # Inisialisasi threshold adaptif
    new_threshold = motion_threshold + noise_threshold * dz_norm
    adaptive_threshold = alpha * prev_threshold + (1 - alpha) * new_threshold

    # Multi-pass refinement
    for _ in range(max_passes):
        prev_value = adaptive_threshold
        adaptive_threshold = alpha * prev_value + (1 - alpha) * (motion_threshold + noise_threshold * (dz / (1 + dz / prev_value)))

        # Jika perubahan kecil, hentikan iterasi
        if abs(adaptive_threshold - prev_value) < epsilon:
            break

    # Similarity weight menggunakan threshold akhir
    similarity_weight = np.exp(-dz / (adaptive_threshold + epsilon))

    return similarity_weight, adaptive_threshold

@njit (parallel=True, nogil=True)
def accumulate_tiles_jit(final_image, weight_map, current_image, reference_image,
                         base_window, row_starts, col_starts,
                         tile_h, tile_w, motion_threshold, noise_threshold, scale, alpha=0.8, max_passes=200, epsilon=1e-3):
    h, w, channels = current_image.shape
    for i in prange(row_starts.shape[0]):  
        r = row_starts[i]
        for j in range(col_starts.shape[0]):
            c = col_starts[j]
            if r + tile_h > h or c + tile_w > w:
                continue
            current_tile = current_image[r:r+tile_h, c:c+tile_w, :]
            ref_tile = reference_image[r:r+tile_h, c:c+tile_w, :]

            # Inisialisasi threshold pertama dengan motion_threshold
            prev_threshold = motion_threshold

            # Panggil compute_motion_metrics dengan semua parameter yang diperlukan
            similarity_weight, _ = compute_motion_metrics(current_tile, ref_tile, prev_threshold, motion_threshold, noise_threshold, alpha, max_passes, epsilon)

            for a in range(tile_h):
                for b in range(tile_w):
                    for ch in range(channels):
                        final_image[r + a, c + b, ch] += current_image[r + a, c + b, ch] * base_window[a, b] * similarity_weight * scale
                    weight_map[r + a, c + b] += base_window[a, b] * similarity_weight

def accumulate_tiles(final_image, weight_map, current_image, reference_image,
                     base_window, row_starts, col_starts,
                     tile_h, tile_w, motion_threshold, noise_threshold, scale, alpha=0.8, max_passes=200, epsilon=1e-3):
    accumulate_tiles_jit(final_image, weight_map, current_image, reference_image,
                         base_window, row_starts, col_starts,
                         tile_h, tile_w, motion_threshold, noise_threshold, scale, alpha, max_passes, epsilon)
