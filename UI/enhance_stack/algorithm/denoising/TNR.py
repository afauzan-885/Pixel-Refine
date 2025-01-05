import multiprocessing
from multiprocessing.pool import Pool
import time
import cv2
import numpy as np
import os
import sqlite3
import h5py

class Median:
    def __init__(self, db_path):
        self.db_path = db_path
        self.tile_size = 64
        self.overlap = 32
        self.height = 0
        self.width = 0
        self.channels = 0
        self.images = []

    def get_all_image_paths(self):
        """
        Retrieves all image paths stored in the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]

    def load_images_from_hdf5(self, hdf5_path):
        """
        Loads images stored in an HDF5 file.
        """
        images = []
        print(f"Membaca gambar dari file HDF5: {hdf5_path}")
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                image = np.array(h5f[key])
                images.append(image)
                print(f"Gambar {key} berhasil dimuat.")
        return images

    def load_images_from_folder(self, folder_path):
        """
        Loads images from a specified folder.
        """
        image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        return self.load_images_from_paths(image_paths)

    def load_images_from_paths(self, image_paths):
        """
        Loads images from a list of image paths.
        """
        images = []
        for image_path in image_paths:
            image = cv2.imread(image_path)
            if image is not None:
                images.append(image)
        return images

    def blend_tiles(self, tile1, tile2, overlap_x, overlap_y):
        """Blends two overlapping tiles using a raised cosine window."""
        h1, w1, c1 = tile1.shape
        h2, w2, c2 = tile2.shape

        h = max(h1, h2)
        w = max(w1, w2)

        new_tile1 = np.zeros((h, w, c1), dtype=tile1.dtype)
        new_tile2 = np.zeros((h, w, c2), dtype=tile2.dtype)

        new_tile1[:h1, :w1] = tile1
        new_tile2[:h2, :w2] = tile2

        blend = np.zeros_like(new_tile1, dtype=np.float64)

        window_x = np.hanning(overlap_x * 2) if overlap_x > 0 else np.array([1.0])
        window_y = np.hanning(overlap_y * 2) if overlap_y > 0 else np.array([1.0])

        for y in range(h):
            for x in range(w):
                weight1 = 1.0
                weight2 = 1.0

                if x < overlap_x and overlap_x > 0:
                    weight1 = window_x[overlap_x - 1 - x]
                    weight2 = window_x[x]
                if y < overlap_y and overlap_y > 0:
                    weight1 *= window_y[overlap_y - 1 - y]
                    weight2 *= window_y[y]
                blend[y, x] = (new_tile1[y, x] * weight1 + new_tile2[y, x] * weight2) / (weight1 + weight2) if (weight1+weight2)>0 else new_tile1[y,x]
        return blend.astype(np.uint8)
    
    def process_row(self, y):  # Dipindahkan ke luar stack_images_tile_merging
        row_stacked = np.zeros((min(self.tile_size, self.height - y), self.width, self.channels), dtype=np.uint8)
        for x in range(0, self.width, self.tile_size - self.overlap):
            # Define tile boundaries with overlap handling
            y_start = y
            y_end = min(y + self.tile_size, self.height)
            x_start = x
            x_end = min(x + self.tile_size, self.width)

            base_tile = self.images[0][y_start:y_end, x_start:x_end]
            tile_height, tile_width = base_tile.shape[:2]

            if tile_height == 0 or tile_width == 0:
                continue

            weighted_tiles = []
            for i, image in enumerate(self.images):
                tile = image[y_start:y_end, x_start:x_end]
                if tile.shape != base_tile.shape:
                    print(f"Tile {i} tidak memiliki ukuran yang sama dengan base tile pada posisi x: {x}, y: {y}. Melewati tile ini.")
                    continue
                ssd = np.sum((base_tile.astype(float) - tile.astype(float))**2)
                weight = np.exp(-ssd / (2 * 100000.0))
                weighted_tiles.append((tile, weight))

            if weighted_tiles:
                sum_weights = sum(weight for _, weight in weighted_tiles)
                merged_tile = np.zeros_like(base_tile, dtype=np.float64)
                for tile, weight in weighted_tiles:
                    merged_tile += tile * (weight / sum_weights)
                merged_tile = merged_tile.astype(np.uint8)

                overlap_x = min(self.overlap, tile_width)

                if x > 0:
                    left_tile = row_stacked[:, x_start-overlap_x:x_start]
                    left_overlap = self.blend_tiles(left_tile, merged_tile[:, :overlap_x], overlap_x, tile_height)
                    row_stacked[:, x_start:x_end] = merged_tile
                    row_stacked[:, x_start-overlap_x:x_start] = left_overlap
                else:
                    row_stacked[:, x_start:x_end] = merged_tile
        return row_stacked, y

    def stack_images_tile_merging(self, images, tile_size=64, overlap=32):
        start_time = time.time()
        print("Memulai penumpukan gambar dengan tile merging...")

        if not images:
            print("Tidak ada gambar untuk diproses.")
            return None

        self.images = images
        base_image = images[0]
        self.height, self.width, self.channels = base_image.shape
        self.tile_size = tile_size
        self.overlap = overlap
        stacked_image = np.zeros_like(base_image)

        num_tiles_y = (self.height + self.tile_size - self.overlap - 1) // (self.tile_size - self.overlap)
        num_tiles_x = (self.width + self.tile_size - self.overlap - 1) // (self.tile_size - self.overlap)
        total_tiles = num_tiles_y * num_tiles_x

        with Pool(multiprocessing.cpu_count()) as p:
            results = p.map(self.process_row, range(0, self.height, self.tile_size - self.overlap))

        processed_tiles = 0
        for row_stacked, y in results:
            stacked_image[y:y+row_stacked.shape[0], :] = row_stacked
            for x in range(0, self.width, self.tile_size - self.overlap):
                processed_tiles += 1
                print(f"Memproses tile {processed_tiles}/{total_tiles} ({int((processed_tiles/total_tiles)*100)}%)", end='\r')

        end_time = time.time()
        print(f"\nPenumpukan gambar selesai dalam {end_time - start_time:.2f} detik.")
        return stacked_image
    
    def save_image(self, image, output_path):
        """
        Saves the stacked image to the specified output path.
        """
        cv2.imwrite(output_path, image)


def main(db_path, output_path):
    image_processor = Median(db_path)

    # Step 1: Check "database/align/global" folder for HDF5 file
    global_hdf5_path = "database/align/aligned_images.h5"
    if os.path.exists(global_hdf5_path):
        print("Data ditemukan di path 'database/align/global'. Memuat data dari HDF5...")
        images = image_processor.load_images_from_hdf5(global_hdf5_path)

    # Step 2: Check "database/align/local" folder for HDF5 file
    elif os.path.exists("database/align/local/aligned_images.h5"):
        print("Data tidak ditemukan di path 'database/align/global'. Memuat dari 'database/align/local'...")
        local_hdf5_path = "database/align/local/aligned_images.h5"
        images = image_processor.load_images_from_hdf5(local_hdf5_path)

    # Step 3: Load from database if no local or global alignment data is found
    else:
        print("Tidak ada data di 'database/align/global' atau 'database/align/local'. Memuat data dari database...")
        image_paths = image_processor.get_all_image_paths()
        if not image_paths:
            print("Tidak ada gambar ditemukan di database.")
            return
        images = image_processor.load_images_from_paths(image_paths)

    if images:
        stacked_image = image_processor.stack_images_tile_merging(images)
        if stacked_image is not None:
            image_processor.save_image(stacked_image, output_path)
        else:
            print("Gagal melakukan stacking, kemungkinan gambar kosong")
    else:
        print("Tidak ada gambar yang dapat diproses.")


if __name__ == "__main__":
    db_path = "pixel_refine_database.db"
    output_path = "stacked_output.jpg"
    main(db_path, output_path)
