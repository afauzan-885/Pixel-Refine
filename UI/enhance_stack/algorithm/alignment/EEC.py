import cv2
import numpy as np
import sqlite3, os
import h5py
import glob
import concurrent.futures

class EECAlgorithm:
    def __init__(self, db_path, use_gpu=False, debug_folder="database/align/global/debug_images", hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.use_gpu = use_gpu
        self.debug_folder = debug_folder
        self.hdf5_path = hdf5_path

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

    def load_images_from_paths(self, image_paths):
        """
        Loads images from a list of image paths, preserving bit depth.
        """
        images = []
        for image_path in image_paths:
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if image is not None:
                images.append(image)
            else:
                print(f"Gagal memuat gambar: {image_path}")
        return images

    def resize_image(self, image, size):
        """
        Resizes the image to match the reference image size using GPU if enabled.
        """
        if self.use_gpu:
            # Konversi gambar ke UMat untuk akselerasi GPU
            image = cv2.UMat(image)
        resized_image = cv2.resize(image, (size[1], size[0]), interpolation=cv2.INTER_LINEAR)
        return resized_image.get() if self.use_gpu else resized_image


    def calculate_global_alignment(self, base_image, target_image, warp_mode=cv2.MOTION_AFFINE):
        """Penyelarasan global menggunakan ECC dengan dukungan 16-bit, multiscale, dan pemrosesan paralel."""

        def process_block(base_block, target_block, warp_mode, criteria):
            warp_matrix = np.eye(2, 3, dtype=np.float32) if warp_mode != cv2.MOTION_HOMOGRAPHY else np.eye(3, 3, dtype=np.float32)
            scales = [0.5, 0.9]  # Multiscale
            for scale in scales:
                scaled_base = cv2.resize(base_block, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
                scaled_target = cv2.resize(target_block, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
                try:
                    _, warp_matrix = cv2.findTransformECC(scaled_target, scaled_base, warp_matrix, warp_mode, criteria)
                except cv2.error as e:
                    print(f"ECC alignment failed at scale {scale}: {e}")
                    break
            return warp_matrix

        base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY) if len(base_image.shape) == 3 else base_image
        target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY) if len(target_image.shape) == 3 else target_image

        base_gray = base_gray.astype(np.float32)
        target_gray = target_gray.astype(np.float32)

        if self.use_gpu:
            base_gray = cv2.UMat(base_gray)
            target_gray = cv2.UMat(target_gray)

        h, w = base_gray.get().shape if self.use_gpu else base_gray.shape
        block_size_h = h // 4
        block_size_w = w // 4
        overlap_h = int(block_size_h * 0.4)
        overlap_w = int(block_size_w * 0.4)

        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 5000, 1e-6)

        warp_matrices = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in range(4):
                for j in range(4):
                    y_start = max(i * block_size_h - overlap_h, 0)
                    y_end = min((i + 1) * block_size_h + overlap_h, h)
                    x_start = max(j * block_size_w - overlap_w, 0)
                    x_end = min((j + 1) * block_size_w + overlap_w, w)

                    base_block = base_gray[y_start:y_end, x_start:x_end]
                    target_block = target_gray[y_start:y_end, x_start:x_end]

                    futures.append(executor.submit(process_block, base_block, target_block, warp_mode, criteria))

            for future in concurrent.futures.as_completed(futures):
                warp_matrices.append(future.result())

        # Combine warp matrices (this is a simplified approach, you may need a more sophisticated method)
        final_warp_matrix = np.mean(warp_matrices, axis=0)

        return final_warp_matrix

    def compensate_global_motion(self, target_image, warp_matrix, warp_mode=cv2.MOTION_AFFINE):
        h, w = target_image.shape[:2]

        if warp_matrix is None:
            print("Matriks warp kosong, tidak dapat melakukan kompensasi.")
            return None
        
        if self.use_gpu:
            target_image = cv2.UMat(target_image)

        if warp_mode == cv2.MOTION_HOMOGRAPHY:
            aligned_image = cv2.warpPerspective(target_image, warp_matrix, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        else:
            aligned_image = cv2.warpAffine(target_image, warp_matrix, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

        return aligned_image.get() if self.use_gpu else aligned_image

    def save_to_hdf5(self, aligned_images):
        """
        Saves aligned images to an HDF5 file after all images are processed.
        """
        print(f"Menyimpan gambar yang diselaraskan ke HDF5: {self.hdf5_path}")
        with h5py.File(self.hdf5_path, "w") as h5f:
            for i, image in enumerate(aligned_images):
                h5f.create_dataset(f"image_{i}", data=image, compression="gzip")
                print(f"Gambar ke-{i} disimpan dalam HDF5.")
        print(f"Semua gambar berhasil disimpan ke HDF5.")

    def save_individual_image(self, image, image_id, use_tiff=True):
        """
        Save individual aligned image to disk, handling 16-bit images.
        """
        if use_tiff:
            debug_image_path = os.path.join(self.debug_folder, f"aligned_image_{image_id}.tiff")
            cv2.imwrite(debug_image_path, image)
        else:
            debug_image_path = os.path.join(self.debug_folder, f"aligned_image_{image_id}.png")
            cv2.imwrite(debug_image_path, image)
        print(f"Gambar yang diselaraskan disimpan ke {debug_image_path} dengan tipe data {image.dtype}.")
        del image

    def delete_debug_images(self):
        """
        Delete all images in the debug folder to free up space.
        """
        print("Menghapus gambar di folder debug...")
        for image_file in glob.glob(os.path.join(self.debug_folder, "*.png")):
            os.remove(image_file)
            print(f"Gambar {image_file} dihapus.")
        print("Semua gambar debug berhasil dihapus.")

def main(db_path):
    use_gpu = False  # Ubah ke False jika ingin menggunakan CPU
    processor = EECAlgorithm(db_path, use_gpu=use_gpu)

    image_paths = processor.get_all_image_paths()
    if not image_paths:
        print("Tidak ada gambar ditemukan di database.")
        return

    base_image = cv2.imread(image_paths[0], cv2.IMREAD_UNCHANGED)
    if base_image is None:
        print(f"Gambar referensi tidak dapat dimuat dari {image_paths[0]}.")
        return

    print("Memproses gambar...")

    with h5py.File(processor.hdf5_path, "w") as h5f:
        h5f.create_dataset(f"image_0", data=base_image, compression="gzip")
        print(f"Gambar ke-0 (referensi) disimpan dalam HDF5.")

        for i in range(1, len(image_paths)):
            print(f"Memproses gambar ke-{i} dari {len(image_paths)}...")

            target_image = cv2.imread(image_paths[i], cv2.IMREAD_UNCHANGED)
            if target_image is None:
                print(f"Gambar ke-{i} tidak dapat dimuat dari {image_paths[i]}.")
                continue

            warp_matrix = processor.calculate_global_alignment(base_image, target_image)
            compensated_image = processor.compensate_global_motion(target_image, warp_matrix)

            if compensated_image is not None: #pengecekan jika kompensasi berhasil
                h5f.create_dataset(f"image_{i}", data=compensated_image, compression="gzip")
                print(f"Gambar ke-{i} disimpan dalam HDF5.")
                processor.save_individual_image(compensated_image, i)
                del target_image, warp_matrix, compensated_image
            else:
                print(f"Gagal melakukan kompensasi gerakan pada gambar ke-{i}")
                continue


    processor.delete_debug_images()
    print("Proses selesai.")

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"  # Path ke database Anda
    main(db_path)
