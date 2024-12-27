import tempfile
import cv2
import numpy as np
import os
import sqlite3
import h5py

class SimilarityAlgorithm:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_all_image_paths(self):
        print("Mengambil path gambar dari database...")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]

    def load_images_batch_from_hdf5(self, hdf5_path, batch_size=10, start_index=0):
        print(f"Membaca batch gambar dari file HDF5: {hdf5_path} (batch mulai dari index {start_index})")
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            keys = list(h5f.keys())[start_index:start_index + batch_size]
            for key in keys:
                image = np.array(h5f[key])
                images.append(image)
                print(f"Gambar {key} berhasil dimuat.")
        return images, len(keys)

    def get_images_batch_from_db(self, batch_size=10, start_index=0):
        print(f"Mengambil batch gambar dari database (batch mulai dari index {start_index})...")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images LIMIT ? OFFSET ?", (batch_size, start_index))
            paths = [row[0] for row in cursor.fetchall()]
        return self.load_images_from_paths(paths), len(paths)

    def load_images_from_paths(self, image_paths, batch_size=10):
        print(f"Membaca gambar dari path secara batch: {image_paths}")
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i + batch_size]
            print(f"Memproses batch gambar dari {batch_paths}")
            images = []
            for image_path in batch_paths:
                image = cv2.imread(image_path)
                if image is not None:
                    images.append(image)
                else:
                    print(f"Peringatan: Gambar {image_path} gagal dimuat.")
            yield images

    def calculate_similarity(self, reference_tile, current_tile, motion_threshold):
        difference = np.abs(current_tile - reference_tile)
        similarity = np.exp(-np.sum(difference, axis=-1) / motion_threshold)
        return np.clip(similarity, 0.01, 1)

    def process_tile(self, reference_image, current_image, y, x, tile_size, tile_step_y, tile_step_x, motion_threshold):
        h, w, _ = reference_image.shape

        y_end = min(y + tile_size[0], h)
        x_end = min(x + tile_size[1], w)

        ref_tile = reference_image[y:y_end, x:x_end]
        current_tile = current_image[y:y_end, x:x_end]

        similarity = self.calculate_similarity(ref_tile, current_tile, motion_threshold)

        return (y, x, y_end, x_end, similarity)

    def similarity_process(self, images, tile_size=(64, 64), overlap=0.3, motion_threshold=30.0):
        print("Melakukan pengurangan noise menggunakan MFNR dengan optimalisasi RAM...")

        reference_image = np.array(images[0], dtype=np.float32)
        h, w, _ = reference_image.shape
        print(f"Dimensi gambar: {h}x{w}, Ukuran tile: {tile_size}, Overlap: {overlap*100:.1f}%")

        tile_step_y = int(tile_size[0] * (1 - overlap))
        tile_step_x = int(tile_size[1] * (1 - overlap))

        # Variabel untuk menyimpan hasil sementara untuk setiap gambar
        batch_final_images = []
        batch_weight_maps = []

        for i, current_image in enumerate(images):
            print(f"Memproses gambar ke-{i+1}/{len(images)}...")

            current_image = np.array(current_image, dtype=np.float32)

            # Variabel untuk menyimpan hasil sementara dalam satu gambar
            final_image = np.zeros_like(reference_image)
            weight_map = np.zeros((h, w), dtype=np.float32)

            for y in range(0, h, tile_step_y):
                for x in range(0, w, tile_step_x):
                    y, x, y_end, x_end, similarity = self.process_tile(reference_image, current_image, y, x, tile_size, tile_step_y, tile_step_x, motion_threshold)

                    weight_map[y:y_end, x:x_end] += similarity
                    final_image[y:y_end, x:x_end] += current_image[y:y_end, x:x_end] * similarity[..., np.newaxis]

            print(f"Gambar ke-{i+1}/{len(images)} selesai diproses.")
            batch_final_images.append(final_image)
            batch_weight_maps.append(weight_map)

        # Setelah seluruh gambar diproses, lakukan akumulasi hasil
        print("Mengakumulasi hasil dari setiap gambar...")

        # Final image untuk seluruh batch
        accumulated_final_image = np.zeros_like(final_image)
        accumulated_weight_map = np.zeros_like(weight_map)

        # Mengakumulasi hasil dari setiap gambar
        for final_image, weight_map in zip(batch_final_images, batch_weight_maps):
            accumulated_weight_map += weight_map
            accumulated_final_image += final_image

        # Normalisasi hasil setelah semua gambar diproses
        accumulated_final_image = self.normalize_image(accumulated_final_image, accumulated_weight_map)

        print("Stack selesai.")
        return accumulated_final_image

    def normalize_image(self, final_image, weight_map):
        final_image = final_image / (weight_map[..., np.newaxis] + 1e-6)
        final_image = np.clip(final_image, 0, 255).astype(np.uint8)
        return final_image

    def save_image(self, image, output_path, quality=100):
        print(f"Menyimpan gambar ke path: {output_path} dengan kualitas {quality}")
        cv2.imwrite(output_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])

def main(db_path, output_path):
    image_processor = SimilarityAlgorithm(db_path)

    global_hdf5_path = "database/align/global/aligned_images.h5"
    if os.path.exists(global_hdf5_path):
        print("Data ditemukan di path 'database/align/global'. Memuat data dari HDF5...")
        reference_image = image_processor.load_images_batch_from_hdf5(global_hdf5_path, batch_size=1)[0][0]
        total_images = len(h5py.File(global_hdf5_path, 'r'))
        load_batch = lambda start: image_processor.load_images_batch_from_hdf5(global_hdf5_path, start_index=start)

    elif os.path.exists("database/align/local/aligned_images.h5"):
        print("Data tidak ditemukan di path 'database/align/global'. Memuat dari 'database/align/local'...")
        local_hdf5_path = "database/align/local/aligned_images.h5"
        reference_image = image_processor.load_images_batch_from_hdf5(local_hdf5_path, batch_size=1)[0][0]
        total_images = len(h5py.File(local_hdf5_path, 'r'))
        load_batch = lambda start: image_processor.load_images_batch_from_hdf5(local_hdf5_path, start_index=start)

    else:
        print("Tidak ada data di 'database/align/global' atau 'database/align/local'. Memuat data dari database...")
        image_paths = image_processor.get_all_image_paths()
        if not image_paths:
            print("Tidak ada gambar ditemukan di database.")
            return
        reference_image = image_processor.load_images_from_paths([image_paths[0]])[0]
        total_images = len(image_paths)
        load_batch = lambda start: (next(image_processor.load_images_from_paths(image_paths[start:], batch_size=10)), 10)

    processed_images = 0
    final_image = np.zeros_like(reference_image, dtype=np.float32)
    weight_map = np.zeros(reference_image.shape[:2], dtype=np.float32)

    while processed_images < total_images - 1:
        print(f"Memuat batch ke-{processed_images // 10 + 1}...")
        batch_images, loaded_count = load_batch(processed_images + 1)
        batch_images.insert(0, reference_image)
        batch_result = image_processor.similarity_process(batch_images)

        final_image += batch_result
        weight_map += np.ones_like(weight_map)
        processed_images += loaded_count
        print(f"Batch selesai diproses. {processed_images}/{total_images - 1} gambar diproses.")

    final_image = image_processor.normalize_image(final_image, weight_map)
    image_processor.save_image(final_image, output_path)
    print(f"Pengurangan noise MFNR selesai! Hasil disimpan di: {output_path}")

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"
    output_path = "mfnr_output.jpg"
    main(db_path, output_path)
