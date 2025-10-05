from concurrent.futures import ThreadPoolExecutor
import gc
import json
import queue
import threading
import concurrent
import traceback
import cv2
import numpy as np
import os
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PySide6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import (calculate_crop_parameters, do_warp_and_crop, estimate_noise_variance, extract_all_metadata, get_adaptive_bilateral, get_all_image_paths_for_batch_process,
                                                                                    get_all_image_paths_for_single_process, load_images_from_paths, prepare_image,
                                                                                    resize_all_with_padding, run_pipeline_global_crop, run_pipeline_non_crop)
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
    
    def calculate_global_motion(self, base_image, target_image, config_filename=None, num_blocks=(2, 2), overlap=10, stop_requested=None):
        if stop_requested and stop_requested():
            return None, None

        orb_config = self.load_orb_config(config_filename)
        use_multicore = orb_config.get("use_multi_core", True)
        
        # --- PERUBAHAN 1: Definisikan fungsi worker untuk filtering ---
        def filter_worker(job_q, result_q):
            """
            Thread worker yang mengambil gambar mentah, menerapkan bilateral filter,
            dan menaruh hasilnya di antrian hasil.
            """
            while True:
                item = job_q.get()
                if item is None:  # Sinyal untuk berhenti
                    result_q.put(None) # Beri sinyal selesai ke antrian hasil juga
                    break
                
                image_type, image_data = item
                
                try:
                    # 1. Persiapan awal (CLAHE dilewati untuk sementara)
                    enhanced_gray = prepare_image(image_data, grayscale=True, use_clahe=False)
                    
                    # 2. Estimasi noise
                    noise_level = estimate_noise_variance(enhanced_gray)
                    
                    # 3. Logika filter adaptif
                    min_noise_threshold = 200.0
                    max_noise_threshold = 700.0
                    min_d, max_d = 5, 9
                    min_sigma, max_sigma = 20, 75

                    if noise_level > min_noise_threshold:
                        d, sigma_color, sigma_space = get_adaptive_bilateral(
                            noise_level, min_noise_threshold, max_noise_threshold,
                            min_d, max_d, min_sigma, max_sigma
                        )
                        filtered_image = cv2.bilateralFilter(enhanced_gray, d, sigma_color, sigma_space)
                    else:
                        filtered_image = enhanced_gray
                    
                    # 4. Terapkan CLAHE setelah filtering
                    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
                    final_image = clahe.apply(filtered_image)
                    
                    result_q.put((image_type, final_image))

                except Exception as e:
                    result_q.put((image_type, None)) # Kirim sinyal error

        # --- PERUBAHAN 2: Inisialisasi antrian dan thread worker ---
        job_queue = queue.Queue()
        result_queue = queue.Queue(maxsize=4) # Cukup untuk base dan target

        filter_thread = threading.Thread(target=filter_worker, args=(job_queue, result_queue))
        filter_thread.start()

        # --- PERUBAHAN 3: Isi antrian tugas (Produser) ---
        job_queue.put(("base", base_image))
        job_queue.put(("target", target_image))
        job_queue.put(None)  # Sinyal akhir pekerjaan

        # --- PERUBAHAN 4: Loop utama menjadi konsumen hasil filtering ---
        enhanced_base_gray, enhanced_target_gray = None, None
        results_received = 0
        while results_received < 2:
            item = result_queue.get() # Memblokir hingga hasil tersedia
            if item is None: # Sinyal selesai dari worker
                break
            
            image_type, image_data = item
            if image_data is None: # Terjadi error di worker
                filter_thread.join()
                return None, None

            if image_type == "base":
                enhanced_base_gray = image_data
            else: # target
                enhanced_target_gray = image_data
            
            results_received += 1
            
        # Pastikan thread worker selesai sebelum melanjutkan
        filter_thread.join()

        if enhanced_base_gray is None or enhanced_target_gray is None:
            print("Failed to get filtered images.")
            return None, None
            
        # --- DARI SINI, KODE KEMBALI SEPERTI SEMULA, TAPI MENGGUNAKAN HASIL DARI QUEUE ---
        h, w = enhanced_base_gray.shape
        blocks_x, blocks_y = num_blocks
        block_w = max(1, w // blocks_x)
        block_h = max(1, h // blocks_y)
        max_kps_per_block = 300

        try:
            orb = cv2.ORB_create(
                nfeatures=int(orb_config.get("nfeatures", 10000)), 
                scaleFactor=float(orb_config.get("scaleFactor", 1.2)),
                nlevels=int(orb_config.get("nlevels", 8)),
                scoreType=cv2.ORB_HARRIS_SCORE
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
                orb, enhanced_base_gray, enhanced_target_gray,
                x, y, bw, bh, overlap, w, h, max_kps_per_block=max_kps_per_block
            )

        try:
            if use_multicore:
                with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
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
            # descriptor_size = orb.getDescriptorSize()
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
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            matches = bf.knnMatch(descriptors_base_all, descriptors_target_all, k=2)
            ratio_thresh = orb_config.get("ratio_threshold", 0.75)
            good_matches = [m for m, n in matches if m.distance < ratio_thresh * n.distance] if all(len(mn) == 2 for mn in matches) else []

            if len(good_matches) < orb_config.get("min_matches_for_transform", 10):
                return None, None

            good_matches = sorted(good_matches, key=lambda m: m.distance)[:orb_config.get("max_keypoints_used", 500)]
            pts_base = np.float32([keypoints_base_all[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            pts_target = np.float32([keypoints_target_all[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        except Exception as e:
            print(f"Matching error: {e}")
            return None, None

        return pts_base, pts_target
    
    def compensate_motion(self, base_image, base_points, target_points, config_filename=None):
        """
        Menerapkan kompensasi gerakan menggunakan transformasi (dengan USAC_MAGSAC)
        untuk menyelaraskan gambar.
        """
        if base_points is None or target_points is None or base_image is None or base_image.ndim < 2:
             return None

        config = self.load_orb_config(config_filename)
        keep_edges = config.get("keep_edges", False)
        transformation_type = config.get("transformation", "affine")
        ransac_threshold = config.get("ransacThreshold", 5.0)

        h, w = base_image.shape[:2]
        if len(base_points) < 4 or len(target_points) < 4:
             return None
         
        # --- 1. Hitung Matriks Transformasi ---
        matrix = None
        try:
            if transformation_type == 'affine':
                matrix, mask = cv2.estimateAffine2D(target_points.reshape(-1, 2), base_points.reshape(-1, 2),
                                                     method=cv2.USAC_MAGSAC, ransacReprojThreshold=ransac_threshold)
            elif transformation_type == 'homography':
                matrix, mask = cv2.findHomography(target_points, base_points, cv2.USAC_MAGSAC, ransac_threshold)
            else:
                raise ValueError( getattr(language_config.UNRECOGNIZED_TRANSFORMATION))
                
            if matrix is None:
                 print(language_config.FAILED_TO_COMPUTE_TRANSFORMATION)
                 return None
            
        except (cv2.error, Exception) as e:
             return None
        
        # --- 2. Lakukan Warping pada Gambar ---
        try:
            if not keep_edges:
                interpolation_flag = cv2.INTER_CUBIC
                if transformation_type == 'homography':
                    return cv2.warpPerspective(base_image, matrix, (w, h), flags=interpolation_flag, borderMode=cv2.BORDER_CONSTANT)
                else:
                    return cv2.warpAffine(base_image, matrix, (w, h), flags=interpolation_flag, borderMode=cv2.BORDER_CONSTANT)
            else:
                pad = calculate_crop_parameters(matrix, w, h, transformation_type)
                
                if pad is None:
                    return cv2.warpAffine(base_image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
                
                return do_warp_and_crop(base_image, matrix, pad, w, h, transformation_type)

        except (cv2.error, Exception) as e:
            return None 

def main(db_path,
         update_progress=None,
         stop_requested=None,
         single_process=None,
         batch_id=None,
         config_filename=None,
         save_align=None,
         align_folder=None,
         command_save_to_hd5f=None,
         num_workers=None):
    
    # --- Tahap 1: Inisialisasi dan Konfigurasi ---
    processor = ORBAlgorithm(db_path) 
    config = processor.load_orb_config(config_filename)
    
    # Tentukan parameter operasi dari argumen atau file konfigurasi
    save_align = save_align if save_align is not None else config.get("save_align", False)
    command_save_to_hd5f = command_save_to_hd5f if command_save_to_hd5f is not None else config.get("command_save_to_hd5f", True)
    align_folder = align_folder if align_folder is not None else config.get(
        "align_folder",
        os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image")
    )
    enable_cropping = config.get("enable_cropping", False)
    keep_edges = config.get("keep_edges", False)
    transformation_type = config.get("transformation", "affine")
    
    # Tentukan path input dan output
    if single_process:
        image_paths = get_all_image_paths_for_single_process(db_path)
        processor.hdf5_path = "database/align/aligned_images.h5"
    else:
        if batch_id is None:
            raise ValueError("Batch ID harus ada saat proses batch")
        image_paths = get_all_image_paths_for_batch_process(db_path, batch_id)
        processor.hdf5_path = f"database/align/aligned_image_batch_{batch_id}.h5"

    if not image_paths:
        if update_progress:
            update_progress(0, "Failed to load image paths.")
        return

    # Buat direktori output jika belum ada
    if command_save_to_hd5f:
        os.makedirs(os.path.dirname(processor.hdf5_path), exist_ok=True)
    if save_align and align_folder:
        os.makedirs(align_folder, exist_ok=True)
        
    extract_all_metadata(image_paths, metadata_file=os.path.join("database", "align", "metadata.json"))

    # --- Tahap 2: Pemuatan dan Penyiapan Base Image ---
    base_img_list = load_images_from_paths([image_paths[0]], stop_requested=stop_requested)
    if not base_img_list or base_img_list[0] is None:
        raise RuntimeError("Base image failed to load.")
    
    if num_workers is None:
        num_workers = 4
    
    base_image_raw = base_img_list[0]
    base_resized_list, (target_h, target_w) = resize_all_with_padding([base_image_raw], method="median")
    base_image = base_resized_list[0]

    del base_image_raw, base_resized_list, base_img_list
    gc.collect()

    # --- Tahap 3: Manajemen File dan Eksekusi Pipeline ---
    h5f = None
    try:
        if command_save_to_hd5f:
            h5f = h5py.File(processor.hdf5_path, "w")

        if not enable_cropping or keep_edges:
            run_pipeline_non_crop(
                processor=processor,
                image_paths=image_paths,
                base_image=base_image,
                target_dims=(target_h, target_w),
                update_progress=update_progress,
                stop_requested=stop_requested,
                save_align=save_align,
                align_folder=align_folder,
                h5_file_handle=h5f,
                num_workers=num_workers 
            )
        else:
            run_pipeline_global_crop(
                processor=processor,
                image_paths=image_paths,
                base_image=base_image,
                target_dims=(target_h, target_w),
                update_progress=update_progress,
                stop_requested=stop_requested,
                transformation_type=transformation_type,
                save_align=save_align,
                align_folder=align_folder,
                h5_file_handle=h5f,
                num_workers=num_workers 
            )
            
    except Exception as e:
        # Tangkap error apa pun yang mungkin terjadi selama pipeline
        print(f"A critical error occurred during the main pipeline: {e}\n{traceback.format_exc()}")
    finally:
        # --- Tahap 4: Cleanup ---
        if h5f:
            h5f.close()
          
def running_orb(parent=None, single_process=None, batch_id=None, progress_callback=None):
    
    # ==========================================================
    # KONDISI 1: MODE BATCH (TANPA GUI)
    # ==========================================================
    if batch_id is not None and progress_callback is not None:
        try:
            main(
                db_path="pixel_refine_database.db",
                update_progress=progress_callback,
                single_process=False, 
                batch_id=batch_id
            )
        except Exception as e:
            raise e
        return 

    # ==========================================================
    # KONDISI 2: MODE SINGLE (DENGAN GUI DIALOG)
    # ==========================================================
    process_finished = False
    
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_ORB)
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(
        Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint |
        Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint
    )

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

    worker = ImageProcessingMultiThreading(main, "pixel_refine_database.db", single_process=single_process, batch_id=batch_id)
    worker.progress_updated.connect(lambda progress, message: (
        progress_bar.setValue(progress),
        label.setText(message)
    ))

    def finish_handler():
        nonlocal process_finished
        process_finished = True
        dialog.close()
        worker.quit()
        worker.wait()

    worker.finished.connect(finish_handler)

    def error_handler(error):
        QMessageBox.critical(dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=error))
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    def on_dialog_close(event):
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