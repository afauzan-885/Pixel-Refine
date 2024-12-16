import cv2
import numpy as np
import sqlite3


class FarnebackAlgorithm:
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

    def save_image_data(self, image_id, image_data):
        """
        Saves image data (as BLOB) in the 'data_images' table in the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO data_images (image_id, image_data) VALUES (?, ?)",
                (image_id, image_data),
            )
            conn.commit()
            print(f"Image data saved for image_id: {image_id}")

    def calculate_optical_flow(self, base_image, target_image):
        """
        Calculates the optical flow between two images.
        """
        base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
        target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(
            base_gray,
            target_gray,
            None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0,
        )
        return flow

    def compensate_motion(self, base_image, flow):
        """
        Applies motion compensation (warp) to the image using optical flow.
        """
        h, w = base_image.shape[:2]
        flow_map = np.stack(np.meshgrid(np.arange(w), np.arange(h)), axis=-1)
        warped_map = flow_map + flow
        remap_x, remap_y = cv2.split(warped_map.astype(np.float32))
        compensated_image = cv2.remap(
            base_image,
            remap_x,
            remap_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT,
        )
        return compensated_image


def main(db_path):
    processor = FarnebackAlgorithm(db_path)

    # Ambil path gambar dari database
    image_paths = processor.get_all_image_paths()
    if not image_paths:
        print("Tidak ada gambar ditemukan di database.")
        return

    # Muat gambar berdasarkan path yang diambil dari database
    images = processor.load_images_from_paths(image_paths)
    if not images:
        print("Tidak ada gambar berhasil dimuat.")
        return

    # Gunakan gambar pertama sebagai referensi
    base_image = images[0]

    # Simpan gambar referensi (base_image) ke dalam database
    image_id = "reference_image"  # ID untuk gambar referensi
    _, encoded_image = cv2.imencode(".jpg", base_image)  # Encoding image as JPEG to store as BLOB
    image_data = encoded_image.tobytes()  # Convert to bytes for BLOB storage
    processor.save_image_data(image_id, image_data)
    print(f"Gambar referensi telah diselaraskan dan disimpan di database.")

    # Proses gambar dengan optical flow dan kompensasi gerakan
    for i in range(1, len(images)):
        flow = processor.calculate_optical_flow(base_image, images[i])
        compensated_image = processor.compensate_motion(images[i], flow)

        # Simpan gambar hasil penyelarasan KE DATABASE
        image_id = f"image_{i}"  # ID gambar berdasarkan urutan
        _, encoded_image = cv2.imencode(".jpg", compensated_image)  # Encoding image as JPEG to store as BLOB
        image_data = encoded_image.tobytes()  # Convert to bytes for BLOB storage
        processor.save_image_data(image_id, image_data)

        print(f"Gambar ke-{i} telah diselaraskan dan disimpan di database.")

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"  # Path ke database Anda
    main(db_path)
