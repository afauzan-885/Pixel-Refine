import cv2
import numpy as np
import os
import sqlite3
import h5py

class MedianWeighting:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_all_image_paths(self):
        print("Mengambil path gambar dari database...")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]

    def load_images_from_hdf5(self, hdf5_path):
        print(f"Membaca gambar dari file HDF5: {hdf5_path}")
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                image = np.array(h5f[key])
                images.append(image)
                print(f"Gambar {key} berhasil dimuat.")
        return images

    def load_images_from_folder(self, folder_path):
        print(f"Membaca gambar dari folder: {folder_path}")
        image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        return self.load_images_from_paths(image_paths)

    def load_images_from_paths(self, image_paths):
        print(f"Membaca gambar dari path: {image_paths}")
        images = []
        for image_path in image_paths:
            image = cv2.imread(image_path)
            if image is not None:
                images.append(image)
            else:
                print(f"Peringatan: Gambar {image_path} gagal dimuat.")
        return images

    def apply_mfnr(self, images, tile_size=(64, 64), overlap=0.3, motion_threshold=30.0):
        print("Melakukan pengurangan noise menggunakan MFNR dengan pendekatan tile berbasis similarity...")

        images_float = np.array(images, dtype=np.float32)
        reference_image = images_float[0]
        h, w, _ = reference_image.shape

        print(f"Dimensi gambar: {h}x{w}, Ukuran tile: {tile_size}, Overlap: {overlap*100:.1f}%")

        # Hitung overlap dalam piksel
        tile_step_y = int(tile_size[0] * (1 - overlap))
        tile_step_x = int(tile_size[1] * (1 - overlap))

        print(f"Langkah tile: {tile_step_y} (vertikal), {tile_step_x} (horizontal)")

        final_image = np.zeros_like(reference_image)
        weight_map = np.zeros_like(reference_image[..., 0])

        total_tiles = 0
        processed_tiles = 0

        # Iterasi melalui tile
        for y in range(0, h, tile_step_y):
            for x in range(0, w, tile_step_x):
                total_tiles += 1

        print(f"Jumlah total tile yang akan diproses: {total_tiles}")

        for y in range(0, h, tile_step_y):
            for x in range(0, w, tile_step_x):
                # Ambil tile referensi
                y_end = min(y + tile_size[0], h)
                x_end = min(x + tile_size[1], w)

                ref_tile = reference_image[y:y_end, x:x_end]

                accumulated_tile = np.zeros_like(ref_tile)
                total_weight_tile = np.zeros_like(ref_tile[..., 0])

                # Proses setiap frame pada tile
                for i, image in enumerate(images_float):
                    current_tile = image[y:y_end, x:x_end]

                    # Hitung similarity
                    difference = np.abs(current_tile - ref_tile)
                    similarity = np.exp(-np.sum(difference, axis=-1) / motion_threshold)
                    similarity = np.clip(similarity, 0.01, 1)

                    # Akumulasi tile berbobot
                    accumulated_tile += current_tile * similarity[..., np.newaxis]
                    total_weight_tile += similarity

                # Normalisasi tile hasil
                final_tile = accumulated_tile / (total_weight_tile[..., np.newaxis] + 1e-6)

                # Tempelkan hasil ke posisi tile di gambar akhir
                final_image[y:y_end, x:x_end] += final_tile
                weight_map[y:y_end, x:x_end] += 1

                processed_tiles += 1
                print(f"Tile ke-{processed_tiles}/{total_tiles} (lokasi: y={y}-{y_end}, x={x}-{x_end}) selesai diproses.")

        # Normalisasi gambar akhir untuk area overlap
        final_image = final_image / (weight_map[..., np.newaxis] + 1e-6)

        final_image = np.clip(final_image, 0, 255).astype(np.uint8)
        print("Pengurangan noise selesai dengan pendekatan tile berbasis similarity.")
        return final_image



    def save_image(self, image, output_path, quality=100):
        print(f"Menyimpan gambar ke path: {output_path} dengan kualitas {quality}")
        # Menyimpan gambar dengan kualitas tertentu
        cv2.imwrite(output_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])


def main(db_path, output_path):
    image_processor = MedianWeighting(db_path)

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

    # Perform image stacking with MFNR
    if images:
        mfnr_image = image_processor.apply_mfnr(images)
        image_processor.save_image(mfnr_image, output_path)
        print(f"Pengurangan noise MFNR selesai! Hasil disimpan di: {output_path}")
    else:
        print("Tidak ada gambar yang dapat diproses.")


if __name__ == "__main__":
    db_path = "pixel_refine_database.db"
    output_path = "mfnr_output.jpg"
    main(db_path, output_path)
