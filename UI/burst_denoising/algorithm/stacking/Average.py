import cv2
import numpy as np
import os
import sqlite3
import h5py

class AverageAlgorithm:
    def __init__(self, db_path):
        self.db_path = db_path

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

    def stack_images(self, images):
        """
        Stacks images by averaging them.
        """
        stacked_image = np.zeros_like(images[0], dtype=np.float32)
        for image in images:
            stacked_image += image.astype(np.float32)
        stacked_image /= len(images)
        stacked_image = np.clip(stacked_image, 0, 255).astype(np.uint8)
        return stacked_image

    def save_image(self, image, output_path):
        """
        Saves the stacked image to the specified output path.
        """
        cv2.imwrite(output_path, image)


def main(db_path, output_path):
    image_processor = AverageAlgorithm(db_path)

    # Step 1: Check "database/align/global" folder for HDF5 file
    global_hdf5_path = "database/align/global/aligned_images.h5"
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

        # Save processed images to "database/stack"
        stack_folder = "database/stack"
        os.makedirs(stack_folder, exist_ok=True)
        for i, img in enumerate(images):
            output_path_stack = os.path.join(stack_folder, f"stack_image_{i}.jpg")
            image_processor.save_image(img, output_path_stack)

    # Perform image stacking
    if images:
        print("Melakukan penumpukan gambar...")
        stacked_image = image_processor.stack_images(images)
        image_processor.save_image(stacked_image, output_path)
        print(f"Penumpukan gambar selesai! Hasil disimpan di: {output_path}")
    else:
        print("Tidak ada gambar yang dapat diproses.")


if __name__ == "__main__":
    db_path = "pixel_refine_database.db"
    output_path = "stacked_output.jpg"
    main(db_path, output_path)
