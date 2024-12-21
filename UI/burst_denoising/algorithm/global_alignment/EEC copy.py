import os
import sys
import cv2
import numpy as np
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from logic.multi_threading import ImageAlignmentThreading  # Mengimpor ImageAlignmentThreading

class EECAlgorithm:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_all_image_paths(self):
        """
        Retrieves all image paths stored in the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, path FROM images")
            return [(row[0], row[1]) for row in cursor.fetchall()]

    def load_image(self, image_path):
        """
        Loads a single image from a given path.
        """
        image = cv2.imread(image_path)
        if image is not None:
            return image
        else:
            print(f"Error: Failed to load image from path: {image_path}")
            return None

    def save_image_data(self, image_id, image_data):
        """
        Saves image file data as BLOB in the 'data_images' table.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO data_images (image_id, image_data) VALUES (?, ?)",
                (image_id, image_data)
            )
            conn.commit()
            print(f"Image data saved for image_id: {image_id}")

    def eccAlign(self, image_path_1, image_path_2, iterations=5000, termination_eps=1e-8):
        """
        Aligns two images using ECC algorithm.
        """
        im1 = self.load_image(image_path_1)
        im2 = self.load_image(image_path_2)

        if im1 is None or im2 is None:
            print("Failed to load images for alignment.")
            return None

        im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

        sz = im1.shape
        warp_mode = cv2.MOTION_EUCLIDEAN
        warp_matrix = np.eye(2, 3, dtype=np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, iterations, termination_eps)

        try:
            _, warp_matrix = cv2.findTransformECC(im1_gray, im2_gray, warp_matrix, warp_mode, criteria)
            im2_aligned = cv2.warpAffine(im2, warp_matrix, (sz[1], sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

            _, im2_aligned_encoded = cv2.imencode('.jpg', im2_aligned)
            return im2_aligned_encoded.tobytes()
        except cv2.error as e:
            print(f"ECC alignment failed: {e}")
            return None

def align_images_multithreaded(db_path):
    """
    Processes image alignment using multithreading.
    """
    algorithm = EECAlgorithm(db_path)
    image_paths = algorithm.get_all_image_paths()

    if len(image_paths) < 2:
        print("Not enough images to align!")
        return

    # Create pairs of consecutive images
    image_pairs = [
        (image_paths[i][0], image_paths[i][1], image_paths[i + 1][1])
        for i in range(len(image_paths) - 1)
    ]

    def task_callback(result):
        print(f"Task completed: {result}")

    def progress_callback(progress, items_left):
        print(f"Progress: {progress}% - Items left: {items_left}")

    def error_callback(error):
        print(f"Error: {error}")

    alignment_thread = ImageAlignmentThreading(
        database_manager=algorithm,
        image_pairs=image_pairs,
        batch_size=2,
        delay_ms=50
    )

    alignment_thread.result_signal.connect(task_callback)
    alignment_thread.progress_signal.connect(progress_callback)
    alignment_thread.error_signal.connect(error_callback)

    # Start the thread
    alignment_thread.start()
    alignment_thread.wait()  # Wait for completion

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"
    align_images_multithreaded(db_path)
