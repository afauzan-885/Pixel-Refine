import concurrent
from concurrent.futures import ThreadPoolExecutor
import os
import cv2
import numpy as np

from UI.panorama.Algorithm.stitching import stitching_utils


class MultiRowPlanarStitcher:
    def __init__(self, settings, progress_callback):
        self.settings = settings
        self.progress_callback = progress_callback
        # Anda bisa menentukan algoritma di sini
        self.algorithm = self.settings.get("algorithm", "akaze").lower()

    def load_images(self, paths):
        # Fungsi ini tetap di dalam kelas karena spesifik untuk alur kerja ini
        images = []
        for path in paths:
            img = cv2.imread(path)
            if img is None:
                return f"Failed to load image: {path}"
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            images.append(img)
        return images

    def stitch(self, image_paths):
        n_images = len(image_paths)
        if n_images < 2:
            return {"stitched_image": None, "error": "Need at least 2 images."}

        self.progress_callback(0, "Loading images...")
        images = self.load_images(image_paths)
        if isinstance(images, str):
            return {"stitched_image": None, "error": images}

        # --- LANGKAH 1: Pilih Algoritma Deteksi Fitur ---
        self.progress_callback(3, f"Using {self.algorithm.upper()} algorithm for feature matching.")
        
        if self.algorithm == "akaze":
            detector = cv2.AKAZE_create()
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        elif self.algorithm == "orb":
            detector = cv2.ORB_create(nfeatures=2000) # Contoh parameter untuk ORB
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        # Tambahkan algoritma lain (SIFT, dll.) di sini jika perlu
        # elif self.algorithm == "sift":
        #     detector = cv2.SIFT_create()
        #     matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        else:
            return {"stitched_image": None, "error": f"Unsupported algorithm: {self.algorithm}"}

        # Buat "pembungkus" (wrapper) untuk fungsi matcher kita agar mudah dipanggil
        matcher_function = lambda im1, im2: stitching_utils.match_features(im1, im2, detector, matcher)

        # --- LANGKAH 2: Hitung Homografi Global ---
        anchor_idx = n_images // 2
        homographies = stitching_utils.calculate_global_homographies(
            images, 
            matcher_function, 
            anchor_idx, 
            self.progress_callback
        )
        
        if homographies is None:
            return {"stitched_image": None, "error": "Failed to create a connected graph of all images."}

        # --- LANGKAH 3: Buat Kanvas dan Gabungkan Gambar ---
        self.progress_callback(70, "Creating final panorama canvas...")
        output_size, translation = stitching_utils.create_panorama_canvas(images, homographies)
        panorama = np.zeros((output_size[1], output_size[0], 3), dtype=np.uint8)

        self.progress_callback(75, "Warping and merging images...")
        for idx, (img, H) in enumerate(zip(images, homographies)):
            self.progress_callback(75 + idx * (24 // n_images), f"Warping image {idx+1}...")
            panorama = stitching_utils.warp_and_merge_image(panorama, img, H, translation, output_size)

        self.progress_callback(99, "Finalizing panorama...")
        return {"stitched_image": panorama}

def run_standart_homography(image_paths, settings, progress_callback):
    try:
        stitcher = MultiRowPlanarStitcher(settings, progress_callback)
        result = stitcher.stitch(image_paths)
        return result
    except Exception as e:
        import traceback
        print(f"FATAL ERROR in stitching: {e}")
        traceback.print_exc()
        return {"stitched_image": None, "error": str(e)}