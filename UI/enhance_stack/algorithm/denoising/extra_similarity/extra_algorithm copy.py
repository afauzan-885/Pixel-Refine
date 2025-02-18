import cv2
import numpy as np
from functools import lru_cache
import concurrent.futures

@lru_cache(maxsize=1)
def raised_cosine_window(tile_size):
    """Membuat raised cosine window untuk blending."""
    y = np.hanning(tile_size[0])
    x = np.hanning(tile_size[1])
    window = np.outer(y, x)
    return window

def compute_sliding_window(image, tile_size, stride):
    """Menggunakan sliding window dengan strided tricks untuk ekstraksi tile."""
    h, w, _ = image.shape
    view = np.lib.stride_tricks.sliding_window_view(image, tile_size + (3,))
    return view[::stride[0], ::stride[1], :, :, :]

def compute_motion_metrics(current_tile, ref_tile, motion_threshold):
    """Hitung similarity weight menggunakan perhitungan vektorisasi."""
    diff = current_tile.astype(np.float32) - ref_tile.astype(np.float32)
    norm = np.linalg.norm(diff, axis=-1)
    norm_median = np.median(norm)
    mad = np.median(np.abs(norm - norm_median))
    return np.exp(-mad / motion_threshold)

def update_final_image(final_image, weight_map, current_tile, window, similarity_weight, y, x, dtype):
    """Optimalkan pembaruan final_image dan weight_map secara vektorisasi."""
    weighted_tile = current_tile * window[..., np.newaxis] * similarity_weight
    np.add.at(weight_map, (slice(y, y + window.shape[0]), slice(x, x + window.shape[1])), window * similarity_weight)
    np.add.at(final_image, (slice(y, y + window.shape[0]), slice(x, x + window.shape[1])), weighted_tile * np.iinfo(dtype).max)

def process_tiles(current_image, reference_image, tile_size, overlap, motion_threshold, dtype, method='roi'):
    """Proses perhitungan similarity menggunakan ROI atau strided tricks."""
    final_image = np.zeros_like(current_image, dtype=np.float32)
    weight_map = np.zeros(current_image.shape[:2], dtype=np.float32)
    cosine_window = raised_cosine_window(tile_size)
    
    if method == 'roi':
        # ROI-based tiling
        tile_positions = generate_tile_coordinates(current_image.shape, tile_size, overlap)
        precomputed_tiles = precompute_reference_tiles(reference_image, tile_size, overlap)
    else:
        # Strided tricks
        stride = (int(tile_size[0] * (1 - overlap)), int(tile_size[1] * (1 - overlap)))
        current_tiles = compute_sliding_window(current_image, tile_size, stride)
        ref_tiles = compute_sliding_window(reference_image, tile_size, stride)
    
    def process_batch(y, x, current_tile, ref_tile):
        similarity_weight = compute_motion_metrics(current_tile, ref_tile, motion_threshold)
        update_final_image(final_image, weight_map, current_tile, cosine_window, similarity_weight, y, x, dtype)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        if method == 'roi':
            for (y, x), (ref_tile, window) in precomputed_tiles.items():
                current_tile = current_image[y:y+tile_size[0], x:x+tile_size[1]]
                futures.append(executor.submit(process_batch, y, x, current_tile, ref_tile))
        else:
            for i in range(current_tiles.shape[0]):
                for j in range(current_tiles.shape[1]):
                    y, x = i * stride[0], j * stride[1]
                    futures.append(executor.submit(process_batch, y, x, current_tiles[i, j], ref_tiles[i, j]))
        
        for future in concurrent.futures.as_completed(futures):
            future.result()
    
    final_image = np.divide(final_image, weight_map[..., np.newaxis], where=weight_map[..., np.newaxis] != 0)
    return final_image.astype(dtype)
