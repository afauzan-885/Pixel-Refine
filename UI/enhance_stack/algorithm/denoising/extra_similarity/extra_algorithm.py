from concurrent.futures import ThreadPoolExecutor
import numpy as np
from numba import njit
from multiprocessing import Pool
    
def raised_cosine_window(tile_size):
        """Membuat raised cosine window untuk blending."""
        y = np.hanning(tile_size[0])
        x = np.hanning(tile_size[1])
        window = np.outer(y, x)
        return window

def precompute_reference_tiles(reference_image, tile_size, overlap):
    h, w, _ = reference_image.shape
    tile_step_y = int(tile_size[0] * (1 - overlap))
    tile_step_x = int(tile_size[1] * (1 - overlap))
    vertical_offset = tile_size[0] // 2
    precomputed_tiles = {}
    cosine_window = raised_cosine_window(tile_size)
    for y in range(0, h, tile_step_y):
        offset_x = vertical_offset if (y // tile_step_y) % 2 == 1 else 0
        for x in range(-offset_x, w, tile_step_x):
            y_end = min(y + tile_size[0], h)
            x_end = min(x + tile_size[1], w)
            x_start = max(x, 0)
            tile_height = y_end - y
            tile_width = x_end - x_start
            ref_tile = reference_image[y:y_end, x_start:x_end]
            window = cosine_window[:tile_height, :tile_width]
            precomputed_tiles[(y, x)] = (ref_tile, window)
    return precomputed_tiles

def process_part(part_idx, current_image_parts, precomputed_reference_tiles, final_image_parts, weight_map_parts,
                 tile_size, h, w, h_mid, w_mid, overlap_pixels_y, overlap_pixels_x, motion_threshold, dtype):
    """
    Fungsi ini memproses satu bagian (part) dari image untuk dijalankan dalam proses paralel.
    """
    for (y, x), (ref_tile, window) in precomputed_reference_tiles[part_idx].items():
        y_end = min(y + tile_size[0], h_mid + overlap_pixels_y if part_idx < 2 else h - (h_mid - overlap_pixels_y))
        x_end = min(x + tile_size[1], w_mid + overlap_pixels_x if part_idx % 2 == 0 else w - (w_mid - overlap_pixels_x))
        x_start = max(x, 0)

        current_tile = current_image_parts[part_idx][y:y_end, x_start:x_end]

        similarity_weight, _ = computing_motion_metrics(current_tile, ref_tile, motion_threshold)

        update_final_image(final_image_parts[part_idx], weight_map_parts[part_idx],
                           current_tile, window, similarity_weight,
                           y, x_start, y_end, x_end, dtype)

def process_tile_similarity(current_image_parts, precomputed_reference_tiles, final_image_parts, weight_map_parts,
                                            tile_size, h, w, h_mid, w_mid, overlap_pixels_y, overlap_pixels_x, 
                                            motion_threshold, dtype, num_workers=4):
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        executor.map(process_part, range(4), 
                     [current_image_parts] * 4, [precomputed_reference_tiles] * 4, 
                     [final_image_parts] * 4, [weight_map_parts] * 4, 
                     [tile_size] * 4, [h] * 4, [w] * 4, [h_mid] * 4, [w_mid] * 4, 
                     [overlap_pixels_y] * 4, [overlap_pixels_x] * 4, 
                     [motion_threshold] * 4, [dtype] * 4)
        
def update_final_image(final_image, weight_map, current_tile, window, similarity_weight, y, x_start, y_end, x_end, dtype):
        weighted_tile = current_tile * window[..., np.newaxis] * similarity_weight
        weight_map[y:y_end, x_start:x_end] += window * similarity_weight
        final_image[y:y_end, x_start:x_end] += weighted_tile * np.iinfo(dtype).max
        

def computing_motion_metrics(current_tile, ref_tile, motion_threshold):
    difference = current_tile.astype(np.float32) - ref_tile.astype(np.float32)
    squared_diff = difference ** 2
    norm = np.sqrt(np.sum(squared_diff, axis=-1))  # L2 norm per piksel
    
    mad = np.median(np.abs(norm - np.median(norm)))
    similarity_weight = np.exp(-mad / motion_threshold)

    return similarity_weight, motion_threshold
