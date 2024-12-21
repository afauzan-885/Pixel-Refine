import cv2
import numpy as np
import time
import sqlite3, os, h5py, glob, gc
from multiprocessing import Manager
from concurrent.futures import ProcessPoolExecutor

class SIFTAlgorithm:
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

    def resize_image(self, image, size):
        """
        Resizes the image to match the reference image size using OpenCL or CPU.
        """
        if self.use_gpu:
            image_umat = cv2.UMat(image)  # Convert to UMat for OpenCL acceleration
            resized_image = cv2.resize(image_umat, (size[1], size[0]), interpolation=cv2.INTER_LINEAR)
        else:
            resized_image = cv2.resize(image, (size[1], size[0]), interpolation=cv2.INTER_LINEAR)  # CPU implementation
        return resized_image

    def calculate_global_alignment(self, base_image, target_image, warp_mode=cv2.MOTION_EUCLIDEAN):
        """
        Optimized global alignment using ECC with multiscale approach, GPU or CPU.
        """
        if self.use_gpu:
            # Convert base and target images to UMat for GPU processing
            base_image_umat = cv2.UMat(base_image)
            target_image_umat = cv2.UMat(target_image)
        else:
            base_image_umat = base_image  # Use CPU arrays
            target_image_umat = target_image

        # Convert images to grayscale if not already
        if len(base_image_umat.get().shape) == 3:  # Use get() to access the image data
            base_image_umat = cv2.cvtColor(base_image_umat, cv2.COLOR_BGR2GRAY)
        if len(target_image_umat.get().shape) == 3:  # Use get() to access the image data
            target_image_umat = cv2.cvtColor(target_image_umat, cv2.COLOR_BGR2GRAY)

        # Initialize warp matrix
        warp_matrix = (
            np.eye(2, 3, dtype=np.float32) if warp_mode != cv2.MOTION_HOMOGRAPHY else np.eye(3, 3, dtype=np.float32)
        )

        # Multiscale alignment (e.g., 3 levels: 25%, 50%, 100%)
        scales = [0.25, 0.5, 1.0]
        for scale in scales:
            # Resize images to a lower resolution
            scaled_base = cv2.resize(base_image_umat, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
            scaled_target = cv2.resize(target_image_umat, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 500, 1e-6)
            try:
                _, warp_matrix = cv2.findTransformECC(
                    scaled_base, scaled_target, warp_matrix, warp_mode, criteria
                )
            except cv2.error as e:
                print(f"ECC alignment failed at scale {scale}: {e}")
                break

        return warp_matrix


    def compensate_global_motion(self, base_image, warp_matrix, warp_mode=cv2.MOTION_EUCLIDEAN):
        """
        Applies global motion compensation using the warp matrix calculated by ECC using GPU or CPU.
        """
        h, w = base_image.shape[:2]

        if self.use_gpu:
            # Convert base image to UMat for OpenCL acceleration (GPU memory)
            base_image_umat = cv2.UMat(base_image)
        else:
            base_image_umat = base_image  # Use CPU array

        try:
            # Apply warpAffine or warpPerspective using OpenCL (via UMat)
            if warp_mode == cv2.MOTION_HOMOGRAPHY:
                aligned_image = cv2.warpPerspective(base_image_umat, warp_matrix, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
            else:
                aligned_image = cv2.warpAffine(base_image_umat, warp_matrix, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        except cv2.error as e:
            print(f"Motion compensation failed: {e}")
            return None

        return aligned_image

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

    def delete_debug_images(self):
        """
        Delete all images in the debug folder to free up space.
        """
        print("Menghapus gambar di folder debug...")
        for image_file in glob.glob(os.path.join(self.debug_folder, "*.png")):
            os.remove(image_file)
            print(f"Gambar {image_file} dihapus.")
        print("Semua gambar debug berhasil dihapus.")

def process_image(processor, base_image_path, target_image_path, image_id, aligned_images, scale_factor=1):
    target_image = cv2.imread(target_image_path)
    base_image = cv2.imread(base_image_path)
    
    if base_image is None or target_image is None:
        print(f"Gambar tidak dapat dimuat: {base_image_path} atau {target_image_path}")
        return f"Image {image_id} gagal diproses."

    # Resize both images to a lower resolution
    low_res_base = cv2.resize(base_image, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
    low_res_target = cv2.resize(target_image, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)

    # Convert to grayscale for alignment
    low_res_base_gray = cv2.cvtColor(low_res_base, cv2.COLOR_BGR2GRAY)
    low_res_target_gray = cv2.cvtColor(low_res_target, cv2.COLOR_BGR2GRAY)

    # Calculate alignment warp matrix on low-resolution images
    warp_matrix = processor.calculate_global_alignment(low_res_base_gray, low_res_target_gray)

    # Apply warp matrix to the full-resolution target image
    full_res_compensated_image = processor.compensate_global_motion(target_image, warp_matrix)

    # Save the aligned image
    processor.save_individual_image(full_res_compensated_image, f"image_{image_id}")

    # Add the aligned image to the shared list (convert to numpy array to store)
    aligned_images.append(full_res_compensated_image.get() if isinstance(full_res_compensated_image, cv2.UMat) else full_res_compensated_image)

    # Free memory after processing
    del target_image
    del base_image
    del low_res_base
    del low_res_target
    del warp_matrix
    del full_res_compensated_image

    # Call garbage collection to clean memory
    gc.collect()

    return f"Image {image_id} selesai diproses."



def main(db_path, use_gpu=True):
    processor = SIFTAlgorithm(db_path, use_gpu=use_gpu)

    # Ambil path gambar dari database
    image_paths = processor.get_all_image_paths()
    if not image_paths:
        print("Tidak ada gambar ditemukan di database.")
        return

    # Muat gambar pertama sebagai referensi
    base_image_path = image_paths[0]  # Gunakan path gambar sebagai referensi
    if base_image_path is None:
        print(f"Gambar referensi tidak dapat dimuat dari {base_image_path}.")
        return

    # Muat gambar referensi
    base_image = cv2.imread(base_image_path)
    if base_image is None:
        print(f"Gambar referensi gagal dimuat dari {base_image_path}.")
        return

    # Simpan gambar referensi ke folder debug
    processor.save_individual_image(base_image, "reference_image")

    # Gunakan Manager untuk membuat list yang dibagikan antar proses
    with Manager() as manager:
        aligned_images = manager.list([])  # Daftar untuk menyimpan gambar yang diselaraskan

        # Proses gambar dengan multiprocessing, 3 gambar dalam satu waktu
        with ProcessPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(1, len(image_paths)):
                print(f"Memproses gambar ke-{i + 1} dari {len(image_paths)}...")
                target_image_path = image_paths[i]

                # Submit image processing to the executor
                futures.append(executor.submit(process_image, processor, base_image_path, target_image_path, i + 1, aligned_images))

            # Tunggu proses selesai
            for future in futures:
                result = future.result()
                print(result)

        # Setelah semuanya selesai, simpan ke dalam HDF5
        processor.save_to_hdf5(list(aligned_images))  # Convert manager.list to regular list before saving

        # Hapus gambar di folder debug setelah semuanya selesai
        processor.delete_debug_images()

    print("Proses selesai.")

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"  # Path ke database Anda
    main(db_path, use_gpu=True)