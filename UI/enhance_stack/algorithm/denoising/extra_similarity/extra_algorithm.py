from numba import njit
@njit
def accumulate_tile(final_tile, weight_tile, current_tile, base_window, similarity_weight, scale):
    """
    Mengakumulasi hasil blending untuk satu tile.
    
    Parameter:
      final_tile      : sub-array final_image untuk tile (tile_h, tile_w, channels)
      weight_tile     : sub-array weight_map untuk tile (tile_h, tile_w)
      current_tile    : tile dari current_image (tile_h, tile_w, channels)
      base_window     : raised cosine window (tile_h, tile_w)
      similarity_weight: nilai bobot similarity untuk tile ini (float)
      scale           : faktor skala, biasanya np.iinfo(dtype).max (misal, 255 atau 65535)
    """
    tile_h, tile_w = base_window.shape
    channels = final_tile.shape[2]
    for i in range(tile_h):
        for j in range(tile_w):
            for k in range(channels):
                final_tile[i, j, k] += current_tile[i, j, k] * base_window[i, j] * similarity_weight * scale
            weight_tile[i, j] += base_window[i, j] * similarity_weight
