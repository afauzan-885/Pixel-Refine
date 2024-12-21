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
        Optimized global alignment using ORB (OBF) features with pyramid scaling on GPU (OpenCL) or CPU.
        """
        print("Mulai deteksi fitur dengan pendekatan multiskala menggunakan ORB...")

        # Convert images to grayscale if not already
        base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
        target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

        # Check if GPU (OpenCL) is available
        if cv2.ocl.haveOpenCL() and self.use_gpu:
            print("Menggunakan GPU (OpenCL) untuk pemrosesan...")
            base_gray_umat = cv2.UMat(base_gray)  # Convert to UMat for GPU memory (OpenCL)
            target_gray_umat = cv2.UMat(target_gray)
        else:
            print("GPU tidak tersedia, menggunakan CPU untuk pemrosesan...")
            base_gray_umat = base_gray
            target_gray_umat = target_gray

        # Initialize warp matrix
        warp_matrix = (
            np.eye(2, 3, dtype=np.float32) if warp_mode != cv2.MOTION_HOMOGRAPHY else np.eye(3, 3, dtype=np.float32)
        )

        # Multiscale alignment (e.g., 3 levels: 25%, 50%, 100%)
        scales = [0.25, 0.5, 1.0]
        for scale in scales:
            print(f"Memproses pada skala: {scale * 100}%...")

            # Resize images to the current scale
            scaled_base = cv2.resize(base_gray_umat, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
            scaled_target = cv2.resize(target_gray_umat, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

            # Create ORB detector
            orb = cv2.ORB_create()

            # Detect keypoints and descriptors using ORB
            print("Mendeteksi keypoints dan descriptors dengan ORB...")
            kp1, des1 = orb.detectAndCompute(scaled_base, None)
            kp2, des2 = orb.detectAndCompute(scaled_target, None)

            # Match descriptors using BFMatcher
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            print("Mencocokkan descriptors...")
            matches = bf.match(des1, des2)

            # Sort matches by distance
            matches = sorted(matches, key=lambda x: x.distance)

            # Extract matching keypoints
            src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

            # Scale back keypoints to full resolution
            src_pts /= scale
            dst_pts /= scale

            # Compute the homography (warp matrix) using RANSAC
            try:
                print("Menghitung homografi pada skala ini...")
                warp_matrix, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            except cv2.error as e:
                print(f"Gagal menghitung homografi pada skala {scale}: {e}")
                continue

        print("Deteksi fitur multiskala selesai.")
        return warp_matrix


    def compensate_global_motion(self, base_image, warp_matrix, warp_mode=cv2.MOTION_EUCLIDEAN):
        """
        Applies global motion compensation using the warp matrix calculated by AKAZE features.
        """
        h, w = base_image.shape[:2]
        
        print("Menerapkan kompensasi gerakan dengan warp matrix...")

        if self.use_gpu:
            # Convert base image to UMat for OpenCL acceleration (GPU memory)
            base_image_umat = cv2.UMat(base_image)
        else:
            base_image_umat = base_image  # Use CPU array

        try:
            # Check if the warp matrix is a 3x3 matrix (homography)
            if warp_matrix.shape == (3, 3):
                # Use warpPerspective for homography (perspective transformation)
                aligned_image = cv2.warpPerspective(base_image_umat, warp_matrix, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
            else:
                # Use warpAffine for affine transformation (2x3 matrix)
                aligned_image = cv2.warpAffine(base_image_umat, warp_matrix, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        except cv2.error as e:
            print(f"Motion compensation failed: {e}")
            return None

        print("Kompensasi gerakan berhasil diterapkan.")
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

def process_image_alignment(processor, base_image_path, target_image_path, image_id, warp_matrices, save_warp_matrices_dir="warp_matrices"):
    target_image = cv2.imread(target_image_path)
    base_image = cv2.imread(base_image_path)
    
    if base_image is None or target_image is None:
        print(f"Gambar tidak dapat dimuat: {base_image_path} atau {target_image_path}")
        return f"Image {image_id} gagal diproses."

    # Resize both images to a lower resolution
    low_res_base = cv2.resize(base_image, (0, 0), fx=1, fy=1, interpolation=cv2.INTER_LINEAR)
    low_res_target = cv2.resize(target_image, (0, 0), fx=1, fy=1, interpolation=cv2.INTER_LINEAR)

    # Apply global alignment using AKAZE features
    warp_matrix = processor.calculate_global_alignment(low_res_base, low_res_target)

    # Save warp_matrix to disk for future use
    if not os.path.exists(save_warp_matrices_dir):
        os.makedirs(save_warp_matrices_dir)
    
    warp_matrix_file = os.path.join(save_warp_matrices_dir, f"warp_matrix_{image_id}.npz")
    np.savez(warp_matrix_file, warp_matrix)  # Save the warp matrix to a .npz file

    # Store warp_matrix path in a list for later use
    warp_matrices.append(warp_matrix_file)

    # Free memory after processing alignment
    del target_image
    del base_image
    del low_res_base
    del low_res_target
    del warp_matrix
    gc.collect()

    return f"Image {image_id} alignment selesai diproses."


def process_image_compensation(processor, target_image_path, warp_matrix_file, image_id, aligned_images):
    target_image = cv2.imread(target_image_path)
    
    if target_image is None:
        print(f"Gambar tidak dapat dimuat: {target_image_path}")
        return f"Image {image_id} gagal diproses."

    # Load the previously saved warp matrix
    warp_matrix = np.load(warp_matrix_file)['arr_0']

    # Apply warp matrix to the full-resolution target image
    full_res_compensated_image = processor.compensate_global_motion(target_image, warp_matrix)

    # Save the aligned image
    processor.save_individual_image(full_res_compensated_image, f"image_{image_id}")

    # Add the aligned image to the shared list (convert to numpy array to store)
    aligned_images.append(full_res_compensated_image.get() if isinstance(full_res_compensated_image, cv2.UMat) else full_res_compensated_image)

    # Free memory after processing compensation
    del target_image
    del full_res_compensated_image
    gc.collect()

    return f"Image {image_id} compensation selesai diproses."


def main(db_path, use_gpu=True):
    processor = ORBAlgorithm(db_path, use_gpu=use_gpu)

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

    # Gunakan Manager untuk membuat list yang dibagikan antar proses
    with Manager() as manager:
        aligned_images = manager.list([])
        warp_matrices = manager.list([])

        # Step 1: Proses seluruh gambar untuk menghitung global alignment
        with ProcessPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(1, len(image_paths)):
                print(f"Memproses alignment gambar ke-{i + 1} dari {len(image_paths)}...")
                target_image_path = image_paths[i]
                
                futures.append(executor.submit(process_image_alignment, processor, base_image_path, target_image_path, i + 1, warp_matrices))
            
            # Tunggu proses selesai
            for future in futures:
                result = future.result()
                print(result)

        # Step 2: Setelah alignment selesai, proses compensate global motion
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = []
            for i, warp_matrix_file in enumerate(warp_matrices):
                target_image_path = image_paths[i + 1]  # Target images after the base image
                print(f"Memproses kompensasi gerakan gambar ke-{i + 1}...")
                
                futures.append(executor.submit(process_image_compensation, processor, target_image_path, warp_matrix_file, i + 1, aligned_images))

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