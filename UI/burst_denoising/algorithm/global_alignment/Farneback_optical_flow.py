import cv2
import numpy as np
import sqlite3, os
import h5py
import glob

class FarnebackAlgorithm:
    def __init__(self, db_path, debug_folder="database/align/global/debug_images", hdf5_path="database/align/global/aligned_images.h5"):
        self.db_path = db_path
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
        Loads images from a list of image paths.
        """
        images = []
        for image_path in image_paths:
            image = cv2.imread(image_path)
            if image is not None:
                images.append(image)
        return images

    def resize_image(self, image, size):
        """
        Resizes the image to match the reference image size.
        """
        return cv2.resize(image, (size[1], size[0]), interpolation=cv2.INTER_LINEAR)

    def calculate_optical_flow(self, base_image, target_image):
        """
        Calculates the optical flow between two images.
        """
        print("Menghitung optical flow...")
        base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
        target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

        # Using Farneback Optical Flow
        flow = cv2.calcOpticalFlowFarneback(base_gray, target_gray, None,
                                            pyr_scale=0.5, levels=3, winsize=15,
                                            iterations=3, poly_n=5, poly_sigma=1.2, flags=0)
        print("Optical flow selesai dihitung.")
        return flow

    def compensate_motion(self, base_image, flow, image_id):
        """
        Applies motion compensation (warp) to the image using optical flow.
        """
        print(f"Melakukan kompensasi gerakan pada gambar {image_id}...")
        h, w = base_image.shape[:2]
        flow_map = np.stack(np.meshgrid(np.arange(w), np.arange(h)), axis=-1)
        warped_map = flow_map + flow
        remap_x, remap_y = cv2.split(warped_map.astype(np.float32))
        compensated_image = cv2.remap(base_image, remap_x, remap_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        
        print(f"Kompensasi gerakan selesai untuk gambar {image_id}.")
        return compensated_image

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

    def save_individual_image(self, image, image_id):
        """
        Save individual aligned image to disk.
        """
        debug_image_path = os.path.join(self.debug_folder, f"aligned_image_{image_id}.png")
        cv2.imwrite(debug_image_path, image)
        print(f"Gambar yang diselaraskan disimpan ke {debug_image_path}.")
        # Hapus gambar dari memori setelah disimpan
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
    processor = FarnebackAlgorithm(db_path)

    # Ambil path gambar dari database
    image_paths = processor.get_all_image_paths()
    if not image_paths:
        print("Tidak ada gambar ditemukan di database.")
        return

    # Muat gambar pertama sebagai referensi
    base_image = cv2.imread(image_paths[0])
    if base_image is None:
        print(f"Gambar referensi tidak dapat dimuat dari {image_paths[0]}.")
        return

    # Ubah ukuran gambar referensi
    print("Menyesuaikan ukuran gambar referensi...")  
    images_resized = [processor.resize_image(base_image, base_image.shape[:2])]

    # Proses gambar dengan optical flow dan kompensasi gerakan satu per satu
    aligned_images = [base_image]  # Simpan gambar referensi sebagai gambar yang telah diselaraskan

    for i in range(1, len(image_paths)):
        # Muat gambar satu per satu
        print(f"Memproses gambar ke-{i + 1} dari {len(image_paths)}...")
        target_image = cv2.imread(image_paths[i])
        if target_image is None:
            print(f"Gambar ke-{i + 1} tidak dapat dimuat dari {image_paths[i]}.")
            continue

        # Ubah ukuran gambar target agar sesuai dengan gambar referensi
        target_image_resized = processor.resize_image(target_image, base_image.shape[:2])

        # Hitung optical flow dan lakukan kompensasi gerakan
        flow = processor.calculate_optical_flow(base_image, target_image_resized)
        compensated_image = processor.compensate_motion(target_image_resized, flow, f"image_{i + 1}")
        
        # Simpan gambar yang diselaraskan secara terpisah
        processor.save_individual_image(compensated_image, f"image_{i + 1}")

        # Simpan gambar yang diselaraskan ke dalam list untuk HDF5 setelah semua selesai
        aligned_images.append(compensated_image)

        # Kosongkan gambar target dari memori untuk mengurangi penggunaan RAM
        del target_image
        del target_image_resized
        del flow
        del compensated_image

    # Setelah seluruh gambar diselaraskan, simpan ke dalam HDF5
    processor.save_to_hdf5(aligned_images)

    # Hapus gambar di folder debug setelah semuanya selesai
    processor.delete_debug_images()

    print("Proses selesai.")

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"  # Path ke database Anda
    main(db_path)
