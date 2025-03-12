# aot_module_optimized.py
from numba.pycc import CC
from numba import njit
import math

cc = CC("compute_motion_metrics_aot")

@cc.export("compute_motion_metrics", "Tuple((float32, float32))(float32[:,:,:], float32[:,:,:], float32, float32, float32, float32, int32, float32)")
@njit(inline='always', nogil=True, fastmath=True, nonpython=True, cache=True)
def compute_motion_metrics(current_tile, ref_tile, prev_threshold, motion_threshold, noise_threshold, alpha, max_passes, epsilon):
    """
    Menggunakan MSE dengan multi-pass dan perbaikan robustness menggunakan estimasi bertahap.
    Optimasi: menghitung selisih hanya sekali dan menggabungkan perhitungan statistik dalam satu loop.
    """
    # Hitung selisih dan flatten array sekali
    diff = current_tile.ravel() - ref_tile.ravel()
    n = diff.shape[0]

    s: float = 0.0
    sum_diff: float = 0.0
    for i in range(n):
        val: float = diff[i]
        s += val * val
        sum_diff += val
    mse_score: float = s / n
    mean_diff: float = sum_diff / n
    sigma_noise: float = math.sqrt(mse_score - mean_diff * mean_diff)
    
    dz: float = mse_score
    dz_norm: float = dz / (1.0 + sigma_noise)
    new_threshold: float = motion_threshold + noise_threshold * dz_norm
    adaptive_threshold: float = alpha * prev_threshold + (1.0 - alpha) * new_threshold

    for _ in range(max_passes):
        prev_value: float = adaptive_threshold
        adaptive_threshold = alpha * prev_value + (1.0 - alpha) * (motion_threshold + noise_threshold * (dz / (1.0 + dz / prev_value)))
        if abs(adaptive_threshold - prev_value) < epsilon:
            break

    similarity_weight: float = math.exp(-dz / (adaptive_threshold + epsilon))
    return similarity_weight, adaptive_threshold


@cc.export("accumulate_tiles_jit", "void(float32[:,:,:], float32[:,:], float32[:,:,:], float32[:,:,:], float32[:,:], int32[:], int32[:], int32, int32, float32, float32, float32, float32, int32, float32)")
@njit(nogil=True, fastmath=True, nonpython=True, cache=True)
def accumulate_tiles_jit(final_image, weight_map, current_image, reference_image,
                         base_window, row_starts, col_starts,
                         tile_h, tile_w, motion_threshold, noise_threshold, scale, alpha, max_passes, epsilon):
    h: int = current_image.shape[0]
    w: int = current_image.shape[1]
    channels: int = current_image.shape[2]
    for i in range(row_starts.shape[0]):
        r: int = row_starts[i]
        for j in range(col_starts.shape[0]):
            c: int = col_starts[j]
            r_end: int = r + tile_h
            c_end: int = c + tile_w
            if r_end > h or c_end > w:
                continue

            # Slicing sekali dan menyimpan hasilnya dalam variabel lokal
            current_tile = current_image[r:r_end, c:c_end, :]
            ref_tile = reference_image[r:r_end, c:c_end, :]

            prev_threshold: float = motion_threshold
            similarity_weight, _ = compute_motion_metrics(current_tile, ref_tile, prev_threshold,
                                                          motion_threshold, noise_threshold, alpha, max_passes, epsilon)

            for a in range(tile_h):
                for b in range(tile_w):
                    window_factor: float = base_window[a, b] * similarity_weight
                    for ch in range(channels):
                        final_image[r + a, c + b, ch] += current_image[r + a, c + b, ch] * window_factor * scale
                    weight_map[r + a, c + b] += window_factor

if __name__ == '__main__':
    cc.compile()
