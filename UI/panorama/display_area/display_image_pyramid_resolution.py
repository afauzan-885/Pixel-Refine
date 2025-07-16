import cv2
import numpy as np
import os
import shutil

def create_image_pyramid(image: np.ndarray, base_path: str, tile_size: int = 256):
    """
    Membuat piramida gambar multi-resolusi yang dipotong menjadi ubin.

    Args:
        image (np.ndarray): Gambar input resolusi penuh (BGR).
        base_path (str): Direktori dasar untuk menyimpan piramida ubin.
        tile_size (int): Ukuran ubin dalam piksel (misal, 256).

    Returns:
        dict: Metadata tentang piramida, termasuk level dan dimensi.
    """
    if os.path.exists(base_path):
        shutil.rmtree(base_path)  # Hapus piramida lama jika ada
    os.makedirs(base_path)

    full_height, full_width = image.shape[:2]
    pyramid_info = {
        "base_path": base_path,
        "tile_size": tile_size,
        "full_width": full_width,
        "full_height": full_height,
        "levels": {}
    }

    current_image = image
    level = 0
    while True:
        h, w = current_image.shape[:2]
        print(f"Memproses level {level} dengan dimensi {w}x{h}...")

        level_path = os.path.join(base_path, str(level))
        os.makedirs(level_path)
        
        pyramid_info["levels"][level] = {"width": w, "height": h, "cols": 0, "rows": 0}

        num_cols = (w + tile_size - 1) // tile_size
        num_rows = (h + tile_size - 1) // tile_size
        pyramid_info["levels"][level]["cols"] = num_cols
        pyramid_info["levels"][level]["rows"] = num_rows

        for r in range(num_rows):
            for c in range(num_cols):
                y_start = r * tile_size
                y_end = min(y_start + tile_size, h)
                x_start = c * tile_size
                x_end = min(x_start + tile_size, w)

                tile = current_image[y_start:y_end, x_start:x_end]
                
                # Buat padding jika tile tidak berukuran penuh agar semua file sama
                padded_tile = cv2.copyMakeBorder(
                    tile, 0, tile_size - (y_end - y_start), 
                    0, tile_size - (x_end - x_start), 
                    cv2.BORDER_CONSTANT, value=[0, 0, 0]
                )

                tile_filename = os.path.join(level_path, f"{r}_{c}.jpg")
                cv2.imwrite(tile_filename, padded_tile, [cv2.IMWRITE_JPEG_QUALITY, 90])

        if max(w, h) <= tile_size:
            break  # Berhenti jika gambar sudah lebih kecil dari ukuran ubin

        current_image = cv2.pyrDown(current_image, dstsize=(w // 2, h // 2))
        level += 1
    
    # Simpan metadata
    import json
    with open(os.path.join(base_path, 'info.json'), 'w') as f:
        json.dump(pyramid_info, f)

    return pyramid_info