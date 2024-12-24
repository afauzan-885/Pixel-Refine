import cv2
import numpy as np
import time
import sqlite3, os, h5py, glob, gc
from multiprocessing import Manager
from concurrent.futures import ProcessPoolExecutor

class ORBAlgorithm:
    def __init__(self, db_path, debug_folder="database/align/global/debug_images", hdf5_path="database/align/global/aligned_images.h5", use_gpu=True):
        self.db_path = db_path
        self.debug_folder = debug_folder
        self.hdf5_path = hdf5_path
        self.use_gpu = use_gpu

        # Pastikan folder debug dan HDF5 ada
        if not os.path.exists(self.debug_folder):
            os.makedirs(self.debug_folder)
        hdf5_folder = os.path.dirname(self.hdf5_path)
        
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

    def get_all_image_paths(self):
        """
        Retrieves all image paths stored in the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]

    def save_individual_image(self, image, image_id):
        """
        Save individual aligned image to disk.
        """
        debug_image_path = os.path.join(self.debug_folder, f"aligned_image_{image_id}.png")
        cv2.imwrite(debug_image_path, image)
        print(f"Gambar yang diselaraskan disimpan ke {debug_image_path}.")
        # Hapus gambar dari memori setelah disimpan
        del image

    def save_to_hdf5(self, aligned_images):
        """
        Save images in debug folder to HDF5 file.
        """
        print(f"Menyimpan gambar yang diselaraskan ke HDF5: {self.hdf5_path}")
        with h5py.File(self.hdf5_path, "w") as h5f:
            for i, image in enumerate(aligned_images):
                h5f.create_dataset(f"image_{i}", data=image, compression="gzip")
                print(f"Gambar ke-{i} disimpan dalam HDF5.")
        print(f"Semua gambar berhasil disimpan ke HDF5.")

def main(db_path, use_gpu=True):
    processor = ORBAlgorithm(db_path, use_gpu=use_gpu)

    # Ambil path gambar dari database
    image_paths = processor.get_all_image_paths()
    if not image_paths:
        print("Tidak ada gambar ditemukan di database.")
        return

    print("Proses selesai.")


if __name__ == "__main__":
    db_path = "pixel_refine_database.db"  # Path ke database Anda
    main(db_path, use_gpu=True)