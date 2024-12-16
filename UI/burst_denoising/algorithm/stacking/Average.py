import cv2
import numpy as np
import os
import sqlite3

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

    def save_image_data(self, image_id, image_file):
        """
        Saves image file data as BLOB in the 'data_images' table.
        """
        with open(image_file, 'rb') as file:
            image_data = file.read()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO data_images (image_id, image_data) VALUES (?, ?)",
                (image_id, image_data)
            )
            conn.commit()
            print(f"Image data saved for image_id: {image_id}")

    def delete_image_data(self, image_id):
        """
        Deletes image data (BLOB) from the 'data_images' table.
        
        Args:
            image_id: The ID of the image whose data should be deleted.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Menghapus data gambar berdasarkan image_id
            cursor.execute("DELETE FROM data_images WHERE image_id = ?", (image_id,))
            
            # Melakukan commit untuk memastikan perubahan disimpan
            conn.commit()
            
            # Menjalankan VACUUM untuk mengurangi ukuran file database
            cursor.execute("VACUUM")
            conn.commit()
            
            print(f"Deleted image data for image_id: {image_id} and performed VACUUM to reclaim space.")

    def get_image_data(self, image_id):
        """
        Retrieves image data (BLOB) from the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT image_data FROM data_images WHERE image_id = ?", (image_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                print(f"No image data found for image_id: {image_id}")
                return None

    def is_image_data_empty(self):
        """
        Checks if the 'data_images' table is empty.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM data_images")
            count = cursor.fetchone()[0]
            return count == 0


def main(image_folder, output_path, db_path):
    image_processor = AverageAlgorithm(db_path)

    # Cek apakah tabel 'data_images' kosong
    if image_processor.is_image_data_empty():
        print("Tidak ada data gambar di database, memuat gambar dari folder...")
        
        # Ambil semua path gambar dari folder
        image_paths = image_processor.get_all_image_paths()
        
        if not image_paths:
            print("Tidak ada gambar ditemukan di folder!")
            return
        
        # Muat gambar dari path yang ditemukan
        images = image_processor.load_images_from_paths(image_paths)
        
        if not images:
            print("Tidak ada gambar berhasil dimuat!")
            return
    else:
        # Jika ada data gambar, ambil dari database
        print("Mengambil gambar dari database...")
        image_paths = image_processor.get_all_image_paths()
        images = image_processor.load_images_from_paths(image_paths)
    
    # Lakukan penumpukan gambar
    stacked_image = image_processor.stack_images(images)
    
    # Simpan gambar hasil penumpukan
    image_processor.save_image(stacked_image, output_path)
    print(f"Penumpukan gambar selesai! Hasil disimpan di: {output_path}")

    # Setelah gambar selesai diproses, hapus data gambar dari database
    for i, image_path in enumerate(image_paths):
        image_id = f"image_{i}"
        image_processor.delete_image_data(image_id)

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"
    output_path = "stacked_output.jpg" 
    main(None, output_path, db_path)
