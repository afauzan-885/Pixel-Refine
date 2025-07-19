from concurrent.futures import ThreadPoolExecutor, as_completed
import gc
import json
import threading
import cv2
import numpy as np
import sqlite3
import os
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PySide6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import compute_global_crop, crop_image, extract_all_metadata, extract_exif, get_all_image_paths_for_single_process, load_images_from_paths, process_and_crop, resize_all_with_padding, resize_with_padding, save_align_to_folder, save_to_hdf5
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config
from config import ALGORITHM_PARAMETER_SETTINGS_FILE

class ORBAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        # Pastikan folder HDF5 ada
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)
        
    def get_all_image_paths_for_batch_process(self, batch_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT images.path 
                FROM batch_process_image
                JOIN images ON batch_process_image.image_id_batch = images.id
                WHERE batch_process_image.batch_id = ?
            """, (batch_id,))
            return [row[0] for row in cursor.fetchall()]
        
    @staticmethod
    def load_orb_config(config_filename=None):
        """
        Membaca konfigurasi ORB dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "nfeatures": 1500, "scaleFactor": 1.1, "nlevels": 5,
            "ransacThreshold": 5.0, "transformation": "homography",
            "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image"),
            "clahe_clipLimit": 2.0, "clahe_tileGridSize": [8, 8],
            "ratio_threshold": 0.75, "min_matches_for_transform": 10,
            "keep_edges": False, "enable_cropping": False,
            "save_align": False, "command_save_to_hd5f": True,
            "use_multi_core": True
        }

        if config_filename is None:
            config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE 

        config_data = default_config.copy()
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                loaded_orb_config = params.get("ORB", {})
                # Gabungkan default dengan yang dimuat (yang dimuat menimpa default)
                config_data.update(loaded_orb_config)
            else:
                 print(f"Info: ORB config file '{config_filename}' not found. Using defaults.")

        except Exception as e:
            print(f"Error loading ORB configuration from '{config_filename}': {e}. Using defaults.")
            config_data = default_config # Kembali ke default jika error

        # Pastikan clahe_tileGridSize adalah tuple
        if isinstance(config_data.get("clahe_tileGridSize"), list):
             config_data["clahe_tileGridSize"] = tuple(config_data["clahe_tileGridSize"])
        elif not isinstance(config_data.get("clahe_tileGridSize"), tuple):
             config_data["clahe_tileGridSize"] = (8, 8) # Fallback jika tipe salah

        return config_data

    @staticmethod
    def load_orb_config_for_batch(config_filename=None):
        """
        Membaca konfigurasi ORB BATCH dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "nfeatures": 1500, "scaleFactor": 1.1, "nlevels": 5,
            "ransacThreshold": 5.0, "transformation": "homography",
            "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image"),
            "clahe_clipLimit": 2.0, "clahe_tileGridSize": [8, 8],
            "ratio_threshold": 0.75, "min_matches_for_transform": 10,
            "keep_edges": False, "enable_cropping": False,
            "save_align": False, "command_save_to_hd5f": True,
            "use_multi_core": True
        }
        if config_filename is None:
            config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE 

        config_data = default_config.copy()
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                loaded_batch_config = params.get("ORB_BATCH", {})
                config_data.update(loaded_batch_config)
            else:
                pass
        except Exception as e:
            print(f"Error loading ORB BATCH configuration from '{config_filename}': {e}. Using defaults.")
            config_data = default_config

        if isinstance(config_data.get("clahe_tileGridSize"), list):
             config_data["clahe_tileGridSize"] = tuple(config_data["clahe_tileGridSize"])
        elif not isinstance(config_data.get("clahe_tileGridSize"), tuple):
             config_data["clahe_tileGridSize"] = (8, 8)

        return config_data

    def calculate_global_motion(self, base_image, target_image, config_filename=None, stop_requested=None):
        """
        Menghitung keypoints/deskriptor menggunakan ORB dengan preprocessing CLAHE,
        dan matching KNN + Ratio Test. Deteksi fitur bisa multi-core.
        """
        if stop_requested and stop_requested():
            return None, None

        # 1. Baca konfigurasi ORB
        orb_config = self.load_orb_config(config_filename)
        use_multicore = orb_config.get("use_multi_core", True)
        
        # --- 2. Konversi gambar ke grayscale 8-bit ---
        try:
            def prepare_gray_orb(img):
                if img is None: raise ValueError("Input image is None.")
                if img.ndim == 3 and img.shape[2] == 3: gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                elif img.ndim == 2: gray = img
                else: raise ValueError(f"Invalid image dimensions/channels: {img.shape}")
                if gray.dtype != np.uint8:
                    gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
                    return gray_norm.astype(np.uint8)
                return gray

            base_gray_8bit = prepare_gray_orb(base_image)
            target_gray_8bit = prepare_gray_orb(target_image)
        except ValueError as e:
            print(f"Error preparing images: {e}")
            return None, None
        except Exception as e:
             print(f"Unexpected error during image preparation: {e}")
             return None, None

        # --- 3. Terapkan CLAHE (opsional, tetap sekuensial) ---
        try:
            clip_limit = orb_config.get("clahe_clipLimit", 6.0)
            grid_size = tuple(orb_config.get("clahe_tileGridSize", (4, 4))) # Pastikan tuple
        
            # Hanya buat dan terapkan jika clip_limit > 0 (atau flag lain jika ada)
            if clip_limit > 0:
                clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
                base_gray_enhanced = clahe.apply(base_gray_8bit)
                target_gray_enhanced = clahe.apply(target_gray_8bit)
            else:
                base_gray_enhanced = base_gray_8bit
                target_gray_enhanced = target_gray_8bit
        except Exception as e:
            base_gray_enhanced = base_gray_8bit
            target_gray_enhanced = target_gray_8bit

        # --- 4. Buat instance ORB ---
        try:
            nfeatures = int(orb_config.get("nfeatures", 1000))
            scaleFactor = float(orb_config.get("scaleFactor", 1.2))
            nlevels = int(orb_config.get("nlevels", 8))
            if nfeatures <=0 or scaleFactor <= 1.0 or nlevels <= 0:
                raise ValueError("Invalid ORB parameters in config.")

            orb = cv2.ORB_create(
                nfeatures=nfeatures,
                scaleFactor=scaleFactor,
                nlevels=nlevels,
                scoreType=cv2.ORB_HARRIS_SCORE 
            )
        except ValueError as e:
             return None, None
        except Exception as e:
            return None, None

        # --- 5. Deteksi Fitur (Sekuensial atau Paralel) ---
        keypoints_base, descriptors_base = None, None
        keypoints_target, descriptors_target = None, None

        try:
            if use_multicore:
                def detect_task(image_to_process):
                    return orb.detectAndCompute(image_to_process, None)

                with ThreadPoolExecutor(max_workers=3) as executor:
                    future_base = executor.submit(detect_task, base_gray_enhanced)
                    future_target = executor.submit(detect_task, target_gray_enhanced)

                    keypoints_base, descriptors_base = future_base.result()
                    keypoints_target, descriptors_target = future_target.result()

            else: 
                keypoints_base, descriptors_base = orb.detectAndCompute(base_gray_enhanced, None)
                keypoints_target, descriptors_target = orb.detectAndCompute(target_gray_enhanced, None)

        except Exception as e:
             return None, None 

        # --- 6. Matching Fitur (Tetap Sekuensial) ---
        base_points = None
        target_points = None
        if descriptors_base is not None and descriptors_target is not None and \
           len(descriptors_base) > 0 and len(descriptors_target) > 0:
            try:
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

                k_val = 2
                if len(descriptors_base) < k_val or len(descriptors_target) < k_val:
                    print(f"Warning: Not enough descriptors for KNN k={k_val}. Falling back to simple matching.")
                    # Lakukan match biasa (lebih sedikit match tapi lebih aman)
                    matches_raw = bf.match(descriptors_base, descriptors_target)
                    good_matches = matches_raw
                else:
                    matches_raw = bf.knnMatch(descriptors_base, descriptors_target, k=k_val)

                    # Terapkan Ratio Test Lowe
                    good_matches = []
                    ratio_thresh = float(orb_config.get("ratio_threshold", 0.75)) # Ambil dari config
                    for match_pair in matches_raw:
                        if len(match_pair) == k_val:
                            m, n = match_pair
                            if m.distance < ratio_thresh * n.distance:
                                good_matches.append(m)
                    
                # --- 7. Ekstrak titik-titik yang cocok, maksimum 500 keypoint terbaik ---
                min_matches_req = int(orb_config.get("min_matches_for_transform", 10))
                max_keypoints_used = 500

                if len(good_matches) >= min_matches_req:
                    try:
                        # Urutkan berdasarkan jarak (semakin kecil = semakin bagus)
                        good_matches_sorted = sorted(good_matches, key=lambda m: m.distance)

                        # Ambil hanya maksimum 500 terbaik
                        limited_matches = good_matches_sorted[:min(len(good_matches_sorted), max_keypoints_used)]

                        base_points_list = [keypoints_base[m.queryIdx].pt for m in limited_matches]
                        target_points_list = [keypoints_target[m.trainIdx].pt for m in limited_matches]

                        # Konversi ke format NumPy (N, 1, 2)
                        base_points_np = np.float32(base_points_list).reshape(-1, 1, 2)
                        target_points_np = np.float32(target_points_list).reshape(-1, 1, 2)

                        # --- Refinement menggunakan Optical Flow LK ---
                        try:
                            refined_target_points, status, err = cv2.calcOpticalFlowPyrLK(
                                base_gray_enhanced, target_gray_enhanced,
                                base_points_np, target_points_np,
                                winSize=(15, 15),
                                maxLevel=3,
                                criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01)
                            )

                            # Filter hanya yang berhasil (status == 1)
                            status = status.reshape(-1)
                            base_points = base_points_np[status == 1]
                            target_points = refined_target_points[status == 1]

                            base_points = base_points.reshape(-1, 1, 2)
                            target_points = target_points.reshape(-1, 1, 2)
                        except Exception as e:
                            print(f"Refinement with optical flow failed: {e}")
                            base_points = base_points_np
                            target_points = target_points_np

                    except IndexError as e:
                        base_points = None
                        target_points = None
                    except Exception as e:
                        base_points = None
                        target_points = None
                else:
                    print(f"Not enough good matches found ({len(good_matches)} < {min_matches_req}) to estimate transform.")


            except cv2.error as cv_err:
                 base_points = None; target_points = None
            except Exception as e:
                import traceback
                base_points = None; target_points = None
        else:
            print("Not enough descriptors found in one or both images to perform matching.")
      
        return base_points, target_points

    def compensate_motion(self, base_image, base_points, target_points, config_filename=None):
        """
        Menerapkan kompensasi gerakan menggunakan transformasi (dengan USAC_MAGSAC)
        untuk menyelaraskan gambar.
        """
        if base_points is None or target_points is None:
             return None

        config = self.load_orb_config(config_filename)
        keep_edges = config.get("keep_edges", False)
        transformation_type = config.get("transformation", "affine")
        ransac_threshold = config.get("ransacThreshold", 5.0)

        # --- Cek input shape ---
        if base_image is None or base_image.ndim < 2:
             return None
         
        h, w = base_image.shape[:2]
        if len(base_points) < 4 or len(target_points) < 4:
             return None
         
        matrix = None
        mask = None
        try:
            if transformation_type == 'affine':
                matrix, mask = cv2.estimateAffine2D(target_points.reshape(-1, 2), base_points.reshape(-1, 2),
                                                     method=cv2.USAC_MAGSAC, ransacReprojThreshold=ransac_threshold)
            elif transformation_type in ['similarity', 'euclidean']:
                matrix, mask = cv2.estimateAffinePartial2D(target_points.reshape(-1, 2), base_points.reshape(-1, 2),
                                                             method=cv2.USAC_MAGSAC, ransacReprojThreshold=ransac_threshold)
            elif transformation_type == 'homography':
                matrix, mask = cv2.findHomography(target_points, base_points, cv2.USAC_MAGSAC, ransac_threshold)
            else:
                error_msg = getattr(language_config.UNRECOGNIZED_TRANSFORMATION)
                raise ValueError(error_msg)

            if matrix is None:
                 error_msg = getattr(language_config.FAILED_TO_COMPUTE_TRANSFORMATION)
                 print(error_msg)
                 return None

            num_inliers = np.sum(mask) if mask is not None else len(base_points) 
            
        except cv2.error as cv_err:
             return None
        except Exception as e:
             return None
        # -------------------------------------------------

        # --- Hitung batas pergeseran (sama) ---
        corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(-1, 1, 2)
        try:
            if transformation_type == 'homography':
                # Cek matrix adalah 3x3
                if matrix.shape != (3, 3):
                     return None
                transformed_corners = cv2.perspectiveTransform(corners, matrix)
            else:
                 # Cek matrix adalah 2x3
                 if matrix.shape != (2, 3):
                     return None
                 transformed_corners = cv2.transform(corners, matrix)

            if transformed_corners is None:
                 return None

            transformed_corners = transformed_corners.reshape(-1, 2)
            min_x, min_y = transformed_corners.min(axis=0)
            max_x, max_y = transformed_corners.max(axis=0)
        except Exception as e:
             return None
        # ------------------------------------

        # --- Warping ---
        try:
            if not keep_edges:
                interpolation_flag = cv2.INTER_CUBIC 
                if transformation_type == 'homography':
                    compensated_image = cv2.warpPerspective(base_image, matrix, (w, h), flags=interpolation_flag, borderMode=cv2.BORDER_CONSTANT)
                else:
                    compensated_image = cv2.warpAffine(base_image, matrix, (w, h), flags=interpolation_flag, borderMode=cv2.BORDER_CONSTANT)
                return compensated_image

            pad_x = max(0, int(np.ceil(max_x - w)))
            pad_y = max(0, int(np.ceil(max_y - h)))
            pad_left = max(0, int(np.ceil(-min_x)))
            pad_top = max(0, int(np.ceil(-min_y)))

            pad = max(pad_x, pad_y, pad_left, pad_top)
            padded_image = cv2.copyMakeBorder(base_image, pad, pad, pad, pad, cv2.BORDER_REFLECT)
            
            interpolation_flag_padded = cv2.INTER_LANCZOS4

            target_w_padded = padded_image.shape[1]
            target_h_padded = padded_image.shape[0]

            if transformation_type == 'homography':
                compensated_padded = cv2.warpPerspective(padded_image, matrix, (target_w_padded, target_h_padded), flags=interpolation_flag_padded, borderMode=cv2.BORDER_REFLECT)
            else:
                compensated_padded = cv2.warpAffine(padded_image, matrix, (target_w_padded, target_h_padded), flags=interpolation_flag_padded, borderMode=cv2.BORDER_REFLECT)

            # Crop kembali ke ukuran asli
            if pad + h > compensated_padded.shape[0] or pad + w > compensated_padded.shape[1]:
                 if transformation_type == 'homography':
                     compensated_image = cv2.warpPerspective(base_image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
                 else:
                     compensated_image = cv2.warpAffine(base_image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
                 return compensated_image
            else:
                 compensated_image = compensated_padded[pad:pad+h, pad:pad+w]
                 return compensated_image

        except cv2.error as cv_err:
             return None
        except Exception as e:
             return None   

def main(db_path,
         update_progress=None,
         stop_requested=None,
         single_process=None,
         batch_id=None,
         config_filename=None,
         save_align=None,
         align_folder=None,
         command_save_to_hd5f=None):
    
    processor = ORBAlgorithm(db_path)
    config = processor.load_orb_config(config_filename)
    
    save_align = save_align if save_align is not None else config.get("save_align", False)
    command_save_to_hd5f = command_save_to_hd5f if command_save_to_hd5f is not None else config.get("command_save_to_hd5f", True)
    align_folder = align_folder if align_folder is not None else config.get(
        "align_folder",
        os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image")
    )
    enable_cropping = config.get("enable_cropping", False)
    keep_edges = config.get("keep_edges", False)
    transformation_type = config.get("transformation", "affine")
    
    progress_counter = {"count": 1 if not enable_cropping or keep_edges else 0}  # 1 untuk image_0 jika no cropping
    progress_lock = threading.Lock()

    if single_process:
        image_paths = get_all_image_paths_for_single_process(db_path)
        processor.hdf5_path = "database/align/aligned_images.h5"
    else:
        if batch_id is None:
            raise ValueError(language_config.BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS)
        image_paths = processor.get_all_image_paths_for_batch_process(batch_id)
        processor.hdf5_path = "database/align/aligned_image_batch_{batch_id}.h5"

    if not image_paths:
        if update_progress:
            update_progress(0, language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
        return

    os.makedirs(os.path.dirname(processor.hdf5_path), exist_ok=True)
    os.makedirs(align_folder, exist_ok=True)
    extract_all_metadata(image_paths, metadata_file=os.path.join("database", "align", "metadata.json"))

    total_images = len(image_paths)
    base_img_list = load_images_from_paths([image_paths[0]], stop_requested=stop_requested)
    if not base_img_list or base_img_list[0] is None:
        raise RuntimeError("Base image gagal dimuat.")

    base_image_raw = base_img_list[0]
    base_resized_list, (target_h, target_w) = resize_all_with_padding([base_image_raw], method="median")
    base_image = base_resized_list[0]

    lock = threading.Lock()
    with h5py.File(processor.hdf5_path, "w") as h5f:
        if command_save_to_hd5f:
            h5f.create_dataset("image_0", data=base_image)
        if save_align:
            save_align_to_folder(base_image, 0, image_paths[0], align_folder)

    def process_image(i, path, return_transform=False):
        if stop_requested and stop_requested():
            return None

        img_list = load_images_from_paths([path], stop_requested=stop_requested)
        if not img_list or img_list[0] is None:
            return None

        target_image = resize_with_padding(img_list[0], (target_h, target_w))
        base_pts, target_pts = processor.calculate_global_motion(base_image, target_image)
        if base_pts is None or target_pts is None:
            return None

        compensated = processor.compensate_motion(target_image, base_pts, target_pts)
        if compensated is None:
            return None

        if enable_cropping and not keep_edges and return_transform:
            return (i, path, base_pts, target_pts)

        if enable_cropping and not keep_edges:
            return None

        if save_align:
            save_align_to_folder(compensated, i, path, align_folder)

        if command_save_to_hd5f:
            with lock:
                with h5py.File(processor.hdf5_path, "a") as h5f:
                    save_to_hdf5(h5f, f"image_{i}", compensated, extract_exif(path))

        return None
    num_threads = 4 # os.cpu_count() or 
    if not enable_cropping or keep_edges:
        # === Streaming tanpa cropping ===
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {executor.submit(process_image, i, path): (i, path) for i, path in enumerate(image_paths[1:], start=1)}
            for future in as_completed(futures):
                i, path = futures[future]
                with progress_lock:
                    progress_counter["count"] += 1
                    if update_progress:
                        update_progress(
                            progress_counter["count"],
                            total_images,
                            language_config.RUN_IMAGE_PROCESSING.format(
                                i=progress_counter["count"],
                                total_images=total_images
                            )
                        )
    else:
        # === Global cropping (tahap 1 - hitung transformasi) ===
        all_transforms = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {executor.submit(process_image, i, path, return_transform=True): (i, path)
                       for i, path in enumerate(image_paths[1:], start=1)}
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    all_transforms.append(result)
                with progress_lock:
                    progress_counter["count"] += 1
                    if update_progress:
                        update_progress(
                            progress_counter["count"],
                            2 * (total_images - 1),
                            language_config.RUN_PROCESS_TRANSFORMATION.format(
                                progress_counter["count"],
                                total_images - 1
                            )
                        )



        # === Tahap 2: Hitung dan terapkan crop global ===
        crop_bounds = compute_global_crop(
            [(i, b, t) for i, _, b, t in all_transforms],
            total_images,
            base_image.shape[1], base_image.shape[0],
            transformation_type=transformation_type
        )

        if crop_bounds is None:
            print(language_config.FAILED_TO_COMPUTE_CROP)
            return

        base_image_cropped = crop_image(base_image, crop_bounds)
        del base_image
        gc.collect()

        with h5py.File(processor.hdf5_path, "a") as h5f:
            del h5f["image_0"]
            h5f.create_dataset("image_0", data=base_image_cropped)
            if save_align:
                save_align_to_folder(base_image_cropped, 0, image_paths[0], align_folder)

        # === Tahap 3: streaming ulang, align dan simpan hasil crop ===
        def apply_transform_and_save(i, path, base_pts, target_pts):
            img_list = load_images_from_paths([path], stop_requested=stop_requested)
            if not img_list or img_list[0] is None:
                return

            target_image = resize_with_padding(img_list[0], (target_h, target_w))
            compensated = processor.compensate_motion(target_image, base_pts, target_pts)
            if compensated is None:
                return

            cropped = crop_image(compensated, crop_bounds)

            if save_align:
                save_align_to_folder(cropped, i, path, align_folder)

            if command_save_to_hd5f:
                with lock:
                    with h5py.File(processor.hdf5_path, "a") as h5f:
                        save_to_hdf5(h5f, f"image_{i}", cropped, extract_exif(path))

            del img_list, target_image, compensated, cropped
            gc.collect()

        stage3_counter = {"count": 0}
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(apply_transform_and_save, i, path, b, t): (i, path)
                    for i, path, b, t in all_transforms}
            for future in as_completed(futures):
                future.result()
                with progress_lock:
                    stage3_counter["count"] += 1
                    if update_progress:
                        update_progress(
                        (total_images - 1) + stage3_counter["count"],
                        2 * (total_images - 1),
                        language_config.RUN_SAVING_TRANSFORMATION.format(
                                stage3_counter["count"],
                                total_images - 1
                            )
                    )
             
def running_orb(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_ORB)
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(
        Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint |
        Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint
    )

    # Layout untuk progress bar dan label
    layout = QVBoxLayout(dialog)
    label = QLabel(language_config.WINDOW_START_PROCESSING)
    layout.addWidget(label)

    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setStyleSheet("""
        QProgressBar {
            border: 1px solid #bbb;
            border-radius: 5px;
            background-color: #f0f0f0;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #80C4E9;
            width: 20px;
        }
    """)
    layout.addWidget(progress_bar)

    # Inisialisasi thread worker
    worker = ImageProcessingMultiThreading(main, "pixel_refine_database.db", single_process=single_process, batch_id=batch_id)
    # Menghubungkan signal worker ke fungsi pembaruan UI
    worker.progress_updated.connect(lambda progress, message: (
        progress_bar.setValue(progress),
        label.setText(message)
    ))

    def finish_handler():
        nonlocal process_finished
        process_finished = True  # set flag ketika proses selesai
        dialog.close()
        worker.quit()  # Berhenti dari thread
        worker.wait()  # Tunggu thread selesai

    worker.finished.connect(finish_handler)

    def error_handler(error):
        QMessageBox.critical(dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=error))
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    def on_dialog_close(event):
        # Jika proses telah selesai, lewati konfirmasi
        if process_finished:
            event.accept()
        elif worker.isRunning():
            reply = QMessageBox.question(dialog, "Cancel Process",
                                        language_config.CANCEL_PROCESSING,
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                worker.stop()
                worker.quit() 
                worker.wait() 
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    dialog.closeEvent = on_dialog_close
    worker.start()
    dialog.exec()

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"  # Path ke database Anda
    main(db_path)