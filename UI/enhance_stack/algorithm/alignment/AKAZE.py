import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import cv2
import numpy as np
import sqlite3
import os
import json
import concurrent.futures
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
from PySide6.QtCore import Qt
import h5py

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import (compute_global_crop, crop_image, extract_all_metadata, extract_exif,
                                                                                    get_all_image_paths_for_single_process, load_images_from_paths, process_and_crop,
                                                                                    resize_all_with_padding, resize_with_padding, save_align_to_folder, save_to_hdf5)
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config
from config import ALGORITHM_PARAMETER_SETTINGS_FILE

class AKAZEAlgorithm:
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
    def load_akaze_config(config_filename=None):
        """
        Membaca konfigurasi AKAZE dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "akaze_threshold": 0.001,
            "akaze_nOctaves": 4,
            "akaze_nOctaveLayers": 4,
            "ratio_threshold": 0.75,
            "ransacThreshold": 5.0,
            "transformation": "homography",
            "keep_edges": False,
            "enable_cropping": False,
            "save_align": False,  
            "command_save_to_hd5f": True,
            "use_multi_core": False,
            "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image")
        }

        if config_filename is None:
            config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE 
        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("AKAZE", default_config)
        except Exception as e:
            return default_config
        
        
    @staticmethod
    def load_akaze_config_for_batch(config_filename=None):
        """
        Membaca konfigurasi AKAZE dari file JSON. Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "akaze_threshold": 0.001,
            "akaze_nOctaves": 4,
            "akaze_nOctaveLayers": 4,
            "ratio_threshold": 0.75,
            "ransacThreshold": 5.0,
            "transformation": "homography",
            "keep_edges": False,
            "enable_cropping": False,
            "save_align": False,  
            "command_save_to_hd5f": True,
            "use_multi_core": False,
            "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image")
        }

        if config_filename is None:
            config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE 

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("AKAZE_BATCH", default_config)
        except Exception as e:
            print("Error loading AKAZE configuration:", e)
            return default_config
        
    def prepare_gray_akaze(self, img):
        if img is None: raise ValueError("Input image is None.")
        if img.ndim == 3 and img.shape[2] == 3: gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif img.ndim == 3 and img.shape[2] == 4: gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY) # Tambahkan handle BGRA
        elif img.ndim == 2: gray = img
        else:
            raise ValueError(f"Invalid image dimensions/channels: {img.shape}")

        if gray.dtype != np.uint8:
            max_val = np.max(gray)
            if gray.dtype == np.float32 or gray.dtype == np.float64:
                 if max_val <= 1.0 and np.min(gray) >= 0:
                     gray_norm = (gray * 255.0).astype(np.uint8)
                 else:
                     if gray.dtype == np.uint16:
                         gray_norm = (gray / 256.0).astype(np.uint8) # Asumsi 16-bit ke 8-bit
                     elif gray.dtype == np.int16:
                          gray_norm = ((gray / 256.0) + 128).astype(np.uint8) # Perkiraan kasar
                     else:
                         gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            elif gray.dtype == np.uint16:
                 gray_norm = (gray / 256.0).astype(np.uint8)
            else:
                 gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            return gray_norm
        return gray

    def compute_features_block(self, akaze_instance, enhanced_gray_base, enhanced_gray_target, x, y, bw, bh, overlap_px, img_w, img_h, max_kps_per_block=300):
        roi_x_start = max(0, x - overlap_px)
        roi_y_start = max(0, y - overlap_px)
        roi_x_end = min(img_w, x + bw + overlap_px)
        roi_y_end = min(img_h, y + bh + overlap_px)

        if roi_y_end <= roi_y_start or roi_x_end <= roi_x_start:
            return [], None, [], None

        roi_base_enhanced = enhanced_gray_base[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
        roi_target_enhanced = enhanced_gray_target[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

        kps_base, desc_base = akaze_instance.detectAndCompute(roi_base_enhanced, None)
        kps_target, desc_target = akaze_instance.detectAndCompute(roi_target_enhanced, None)

        def adjust_and_filter_kps(kps, descs):
            adjusted_kps = []
            valid_desc_indices = []
            if kps and descs is not None:
                for idx, kp in enumerate(kps):
                    orig_x = kp.pt[0] + roi_x_start
                    orig_y = kp.pt[1] + roi_y_start
                    if x <= orig_x < x + bw and y <= orig_y < y + bh:
                        if idx < len(descs):
                            kp.pt = (orig_x, orig_y)
                            adjusted_kps.append(kp)
                            valid_desc_indices.append(idx)
            if descs is not None and valid_desc_indices:
                filtered_descs = descs[np.array(valid_desc_indices)]
            else:
                filtered_descs = None
            return adjusted_kps, filtered_descs

        kps_base_adjusted, final_desc_base = adjust_and_filter_kps(kps_base, desc_base)
        kps_target_adjusted, final_desc_target = adjust_and_filter_kps(kps_target, desc_target)

        def select_top_k(kps, descs, k):
            if descs is None or len(kps) == 0:
                return [], None
            if len(kps) <= k:
                return kps, descs
            sorted_idx = np.argsort([-kp.response for kp in kps])[:k]
            return [kps[i] for i in sorted_idx], descs[sorted_idx]

        kps_base_adjusted, final_desc_base = select_top_k(kps_base_adjusted, final_desc_base, max_kps_per_block)
        kps_target_adjusted, final_desc_target = select_top_k(kps_target_adjusted, final_desc_target, max_kps_per_block)

        return kps_base_adjusted, final_desc_base, kps_target_adjusted, final_desc_target
    
    def calculate_global_motion(self, base_image, target_image, config_filename=None, num_blocks=(3, 3), overlap=20, stop_requested=None):
        if stop_requested and stop_requested():
            return None, None

        akaze_config = self.load_akaze_config(config_filename)
        use_multicore = akaze_config.get("use_multi_core", True)
        max_kps_per_block = 300

        try:
            base_gray = self.prepare_gray_akaze(base_image)
            target_gray = self.prepare_gray_akaze(target_image)
        except Exception:
            return None, None

        try:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced_base_gray = clahe.apply(base_gray)
            enhanced_target_gray = clahe.apply(target_gray)
        except Exception:
            enhanced_base_gray = base_gray
            enhanced_target_gray = target_gray

        h, w = base_gray.shape
        blocks_x, blocks_y = num_blocks
        block_w = max(1, w // blocks_x)
        block_h = max(1, h // blocks_y)

        try:
            akaze = cv2.AKAZE_create(
                descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB,
                threshold=float(akaze_config.get("akaze_threshold", 0.001)),
                nOctaves=int(akaze_config.get("akaze_nOctaves", 4)),
                nOctaveLayers=int(akaze_config.get("akaze_nOctaveLayers", 4)),
                diffusivity=cv2.KAZE_DIFF_PM_G2
            )
        except Exception:
            return None, None

        keypoints_base_all = []
        descriptors_base_list = []
        keypoints_target_all = []
        descriptors_target_list = []

        def process_block(i, j):
            x = i * block_w
            y = j * block_h
            bw = w - x if i == blocks_x - 1 else block_w
            bh = h - y if j == blocks_y - 1 else block_h
            return self.compute_features_block(
                akaze, enhanced_base_gray, enhanced_target_gray,
                x, y, bw, bh, overlap, w, h, max_kps_per_block=max_kps_per_block
            )

        try:
            if use_multicore:
                with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
                    futures = [executor.submit(process_block, i, j)
                            for i in range(blocks_x) for j in range(blocks_y)]
                    for future in concurrent.futures.as_completed(futures):
                        if stop_requested and stop_requested():
                            return None, None
                        try:
                            kpb, db, kpt, dt = future.result()
                            if db is not None and len(kpb) > 0:
                                keypoints_base_all.extend(kpb)
                                descriptors_base_list.append(db)
                            if dt is not None and len(kpt) > 0:
                                keypoints_target_all.extend(kpt)
                                descriptors_target_list.append(dt)
                        except Exception as e:
                            print(f"Error in block processing: {e}")
            else:
                for i in range(blocks_x):
                    for j in range(blocks_y):
                        if stop_requested and stop_requested():
                            return None, None
                        kpb, db, kpt, dt = process_block(i, j)
                        if db is not None and len(kpb) > 0:
                            keypoints_base_all.extend(kpb)
                            descriptors_base_list.append(db)
                        if dt is not None and len(kpt) > 0:
                            keypoints_target_all.extend(kpt)
                            descriptors_target_list.append(dt)
        except Exception as e:
            print(f"ThreadPool execution error: {e}")
            return None, None

        if not descriptors_base_list or not descriptors_target_list:
            return None, None

        try:
            descriptor_size = akaze.getDescriptorSize()
            descriptors_base_all = np.vstack(descriptors_base_list)
            descriptors_target_all = np.vstack(descriptors_target_list)

            if len(keypoints_base_all) != descriptors_base_all.shape[0] or \
            len(keypoints_target_all) != descriptors_target_all.shape[0]:
                print("CRITICAL: Mismatch between keypoints and descriptors after filtering.")
                return None, None
        except Exception as e:
            print(f"Descriptor stack error: {e}")
            return None, None

        if descriptors_base_all.shape[0] == 0 or descriptors_target_all.shape[0] == 0:
            return None, None

        def select_top_k(kps, descs, k):
            if len(kps) <= k:
                return kps, descs
            idx = np.argsort([-kp.response for kp in kps])[:k]
            return [kps[i] for i in idx], descs[idx]

        keypoints_base_all, descriptors_base_all = select_top_k(keypoints_base_all, descriptors_base_all, 500)
        keypoints_target_all, descriptors_target_all = select_top_k(keypoints_target_all, descriptors_target_all, 500)

        try:
            flann = cv2.FlannBasedMatcher(
                dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1),
                dict(checks=50)
            )
            matches = flann.knnMatch(descriptors_base_all, descriptors_target_all, k=2)
            ratio_thresh = 0.75
            good_matches = [m for m, n in matches if m.distance < ratio_thresh * n.distance] if all(len(mn) == 2 for mn in matches) else []

            if len(good_matches) < akaze_config.get("min_matches_for_transform", 10):
                return None, None

            good_matches = sorted(good_matches, key=lambda m: m.distance)[:akaze_config.get("max_keypoints_used", 500)]
            pts_base = np.float32([keypoints_base_all[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            pts_target = np.float32([keypoints_target_all[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            try:
                refined_pts_target, status, _ = cv2.calcOpticalFlowPyrLK(
                    enhanced_base_gray, enhanced_target_gray, pts_base, pts_target,
                    winSize=(15, 15), maxLevel=3,
                    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01)
                )
                status = status.reshape(-1)
                pts_base = pts_base[status == 1].reshape(-1, 2)
                pts_target = refined_pts_target[status == 1].reshape(-1, 2)
                if len(pts_base) < akaze_config.get("min_matches_for_transform", 10):
                    return None, None
            except Exception:
                pts_base = pts_base.reshape(-1, 2)
                pts_target = pts_target.reshape(-1, 2)

        except Exception as e:
            print(f"Matching error: {e}")
            return None, None

        return pts_base, pts_target

    
    def compensate_motion(self, base_image, base_points, target_points, config_filename=None):
        """
        Menerapkan kompensasi gerakan menggunakan transformasi (dengan USAC_MAGSAC)
        untuk menyelaraskan gambar.
        """
        if base_points is None or target_points is None:
             return None

        config = self.load_akaze_config(config_filename)
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

        # --- Hitung batas pergeseran---
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
    
    processor = AKAZEAlgorithm(db_path)
    config = processor.load_akaze_config(config_filename)
    
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
        processor.hdf5_path = f"database/align/aligned_image_batch_{batch_id}.h5"

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
    num_threads = 2  # Default to 4 if os.cpu_count() returns None
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
             

def running_akaze(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_AKAZE)
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