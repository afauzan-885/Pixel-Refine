import gc
import cv2
import numpy as np
import sqlite3
import os
import json
import concurrent.futures
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
from PyQt6.QtCore import Qt
import h5py

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import compute_global_crop, crop_image, extract_all_metadata, extract_exif, load_images_from_paths, save_align_to_folder, save_to_hdf5
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config

class AKAZEAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        # Pastikan folder HDF5 ada
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

    def get_all_image_paths_for_single_process(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT images.path 
                FROM single_process_image
                JOIN images ON single_process_image.image_id_single = images.id
            """)
            return [row[0] for row in cursor.fetchall()]
        
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
            "align_folder": os.path.join(
                os.path.expanduser("~"), 
                "Documents", 
                "Pixel Refine", 
                "align_image"
            )
        }

        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return {**default_config, **params.get("AKAZE", {})}
        except Exception as e:
            print("Error loading AKAZE configuration:", e)
            return default_config
        
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
            "keep_edges": True,
            "enable_cropping": False,
            "save_align": False,  
            "command_save_to_hd5f": True,
            "align_folder": os.path.join(
                os.path.expanduser("~"), 
                "Documents", 
                "Pixel Refine", 
                "align_image"
            )
        }

        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return {**default_config, **params.get("AKAZE_BATCH", {})}
        except Exception as e:
            print("Error loading AKAZE configuration:", e)
            return default_config

    def calculate_global_motion(self, base_image, target_image, config_filename=None, num_blocks=(4, 4), overlap=20, stop_requested=None):
        """
        Menghitung keypoints dan deskriptor menggunakan AKAZE dengan membagi gambar
        menjadi blok-blok secara paralel. Instance AKAZE dibuat sekali.

        Parameter:
          - num_blocks: tuple (blocks_x, blocks_y) untuk pembagian gambar.
          - overlap: jumlah piksel overlap di sekeliling tiap blok.
        """
        if stop_requested and stop_requested():
            print("Proses dihentikan sebelum menghitung gerakan global (parallel).")
            return None, None

        akaze_config = self.load_akaze_config(config_filename)

        # --- Konversi gambar ke grayscale (sekali) ---
        try:
            if base_image.ndim == 3 and base_image.shape[2] == 3:
                 base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
            elif base_image.ndim == 2:
                 base_gray = base_image # Sudah grayscale
            else: raise ValueError("Base image has unsupported channels")

            if target_image.ndim == 3 and target_image.shape[2] == 3:
                 target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
            elif target_image.ndim == 2:
                 target_gray = target_image # Sudah grayscale
            else: raise ValueError("Target image has unsupported channels")
        except Exception as e:
            return None, None
        # --------------------------------------------

        h, w = base_gray.shape
        blocks_x, blocks_y = num_blocks
        block_w = w // blocks_x
        block_h = h // blocks_y

        # --- Buat instance AKAZE SEKALI di sini ---
        try:
            akaze = cv2.AKAZE_create(
                descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB, # Default MLDB, bisa eksplisit
                descriptor_size=0, # Default
                descriptor_channels=3, # Default
                threshold=akaze_config.get("akaze_threshold", 0.001), # Gunakan .get dengan default
                nOctaves=akaze_config.get("akaze_nOctaves", 4),
                nOctaveLayers=akaze_config.get("akaze_nOctaveLayers", 4),
                diffusivity=cv2.KAZE_DIFF_PM_G2 # Default
            )
        except Exception as e:
            return None, None
        # ------------------------------------------

        keypoints_base_all = []
        descriptors_base_list = [] # Gunakan list dulu untuk efisiensi
        keypoints_target_all = []
        descriptors_target_list = []

        # --- Fungsi worker thread (sekarang menerima instance akaze) ---
        def compute_features_block(akaze_instance, x, y, bw, bh, overlap):
            # Tentukan ROI dengan tambahan overlap
            roi_x_start = max(0, x - overlap)
            roi_y_start = max(0, y - overlap)
            roi_x_end = min(w, x + bw + overlap)
            roi_y_end = min(h, y + bh + overlap)

            # Pastikan ROI valid sebelum slicing
            if roi_y_end <= roi_y_start or roi_x_end <= roi_x_start:
                return [], None, [], None # Kembalikan hasil kosong jika ROI tidak valid

            roi_base = base_gray[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
            roi_target = target_gray[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

            # Gunakan instance AKAZE yang sama
            try:
                kps_base, desc_base = akaze_instance.detectAndCompute(roi_base, None)
                kps_target, desc_target = akaze_instance.detectAndCompute(roi_target, None)
            except Exception as e:
                 # Tangani error jika detectAndCompute gagal di satu blok
                 return [], None, [], None # Kembalikan hasil kosong

            # Sesuaikan koordinat keypoints agar sesuai dengan posisi asli
            # Lakukan ini hanya jika keypoints ditemukan
            kps_base_adjusted = []
            if kps_base:
                for kp in kps_base:
                    kp.pt = (kp.pt[0] + roi_x_start, kp.pt[1] + roi_y_start)
                    kps_base_adjusted.append(kp)

            kps_target_adjusted = []
            if kps_target:
                for kp in kps_target:
                    kp.pt = (kp.pt[0] + roi_x_start, kp.pt[1] + roi_y_start)
                    kps_target_adjusted.append(kp)

            return kps_base_adjusted, desc_base, kps_target_adjusted, desc_target
        # -------------------------------------------------------------

        print(f"Submitting {blocks_x * blocks_y} blocks to ThreadPoolExecutor...")
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor: # Gunakan os.cpu_count()
            for i in range(blocks_x):
                for j in range(blocks_y):
                    if stop_requested and stop_requested(): # Cek di dalam loop juga
                        # Batalkan future yang belum selesai jika memungkinkan (opsional)
                        for f in futures: f.cancel()
                        executor.shutdown(wait=False, cancel_futures=True) # Coba hentikan thread
                        return None, None

                    x = i * block_w
                    y = j * block_h
                    bw = block_w # Lebar dasar
                    bh = block_h # Tinggi dasar
                    # Koreksi ukuran untuk blok di tepi kanan dan bawah
                    if i == blocks_x - 1: bw = w - x
                    if j == blocks_y - 1: bh = h - y

                    # Lewatkan instance akaze yang sama
                    futures.append(executor.submit(compute_features_block, akaze, x, y, bw, bh, overlap))

            processed_count = 0
            for future in concurrent.futures.as_completed(futures):
                if stop_requested and stop_requested():
                     # Batalkan future lain jika memungkinkan
                    for f in futures: f.cancel()
                    # Tidak perlu shutdown executor lagi karena sudah di dalam context manager
                    return None, None
                try:
                    kps_base, desc_base, kps_target, desc_target = future.result()
                    processed_count += 1
                    # print(f"Processed block {processed_count}/{len(futures)}") # Log progress per blok

                    # --- Gunakan list.append untuk efisiensi ---
                    if desc_base is not None and len(kps_base) > 0:
                        keypoints_base_all.extend(kps_base)
                        descriptors_base_list.append(desc_base)
                    if desc_target is not None and len(kps_target) > 0:
                        keypoints_target_all.extend(kps_target)
                        descriptors_target_list.append(desc_target)
                    # ------------------------------------------
                except concurrent.futures.CancelledError:
                    print("A task was cancelled.") # Handle jika pembatalan berhasil
                except Exception as exc:
                    print(f'Block processing generated an exception: {exc}')
                    # Putuskan apakah akan melanjutkan atau gagal

        print("Block computations finished. Aggregating descriptors...")
        # --- Gabungkan deskriptor dari list setelah semua selesai ---
        descriptors_base_all = None
        if descriptors_base_list:
            try:
                descriptors_base_all = np.vstack(descriptors_base_list)
            except ValueError as e:
                 return None, None # Gagal jika tidak bisa stack

        descriptors_target_all = None
        if descriptors_target_list:
            try:
                descriptors_target_all = np.vstack(descriptors_target_list)
            except ValueError as e:
                 return None, None # Gagal jika tidak bisa stack
        # ----------------------------------------------------------

        # --- Lakukan matching menggunakan BFMatcher ---
        if descriptors_base_all is None or descriptors_target_all is None or \
           len(descriptors_base_all) == 0 or len(descriptors_target_all) == 0: # Tambah cek panjang > 0
            return None, None

        try:
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False) # NORM_HAMMING untuk AKAZE
            # Pastikan k <= jumlah deskriptor di set target jika jumlahnya < 2
            k_val = min(2, len(descriptors_target_all))
            if k_val < 2:
                 # Lakukan pencocokan tunggal jika k=1
                 matches_single = bf.match(descriptors_base_all, descriptors_target_all)
                 # Konversi ke format list[DMatch] agar ratio test bisa dilewati
                 good_matches = matches_single
            else:
                matches = bf.knnMatch(descriptors_base_all, descriptors_target_all, k=k_val)
                good_matches = []
                ratio_thresh = akaze_config.get("ratio_threshold", 0.75)
                for match_pair in matches:
                    # Pastikan match_pair berisi cukup elemen (k=2)
                    if len(match_pair) == 2:
                        m, n = match_pair
                        if m.distance < ratio_thresh * n.distance:
                            good_matches.append(m)
                    # Jika k=1 (misal karena target desc < 2), tidak bisa lakukan ratio test
                    # Mungkin perlu logika berbeda jika k=1 terjadi, tapi untuk sekarang kita abaikan

        except Exception as e:
            return None, None
        # ---------------------------------------------

        # --- Ekstrak titik-titik yang cocok ---
        if len(good_matches) < 4: # Butuh minimal 4 poin untuk sebagian besar estimasi transformasi
             return None, None

        try:
            base_points = np.float32([keypoints_base_all[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2) # Reshape untuk OpenCV
            target_points = np.float32([keypoints_target_all[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2) # Reshape untuk OpenCV
            
        except IndexError as e:
             # Coba print beberapa indeks untuk debug
             # for i, m in enumerate(good_matches[:5]): print(f"Match {i}: qIdx={m.queryIdx}, tIdx={m.trainIdx}")
             return None, None
        except Exception as e:
             return None, None
        # -----------------------------------

        return base_points, target_points
        
    def compensate_motion(self, base_image, base_points, target_points, config_filename=None):
        """
        Menerapkan kompensasi gerakan menggunakan transformasi untuk menyelaraskan gambar.
        """
        config = self.load_akaze_config(config_filename)
        keep_edges = config["keep_edges"]
        transformation_type = config["transformation"]
        ransac_threshold = config["ransacThreshold"]

        h, w = base_image.shape[:2]

        # Hitung matriks transformasi
        if transformation_type == 'affine':
            matrix, mask = cv2.estimateAffine2D(target_points, base_points, method=cv2.RANSAC, ransacReprojThreshold=ransac_threshold)
        elif transformation_type in ['similarity', 'euclidean']:
            matrix, mask = cv2.estimateAffinePartial2D(target_points, base_points, method=cv2.RANSAC, ransacReprojThreshold=ransac_threshold)
        elif transformation_type == 'homography':
            matrix, mask = cv2.findHomography(target_points, base_points, cv2.RANSAC, ransac_threshold)
        else:
            raise ValueError(language_config.UNRECOGNIZED_TRANSFORMATION)

        # Pastikan matriks valid
        if matrix is None:
            raise ValueError(language_config.FAILED_TO_COMPUTE_TRANSFORMATION)

        # Hitung batas pergeseran (terlepas dari keep_edges)
        corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(-1, 1, 2)

        if transformation_type == 'homography':
            transformed_corners = cv2.perspectiveTransform(corners, matrix)
        else:
            transformed_corners = cv2.transform(corners, matrix)

        transformed_corners = transformed_corners.reshape(-1, 2)
        min_x, min_y = transformed_corners.min(axis=0)
        max_x, max_y = transformed_corners.max(axis=0)

        # print(f"Pergerakan batas: min_x={min_x}, min_y={min_y}, max_x={max_x}, max_y={max_y}")

        # Jika keep_edges = False, langsung terapkan transformasi tanpa padding
        if not keep_edges:
            if transformation_type == 'homography':
                compensated_image = cv2.warpPerspective(base_image, matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            else:
                compensated_image = cv2.warpAffine(base_image, matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            return compensated_image

        # Jika keep_edges = True, tambahkan padding berdasarkan batas pergeseran
        pad_x = max(0, int(np.ceil(max_x - w)))
        pad_y = max(0, int(np.ceil(max_y - h)))
        pad_left = max(0, int(np.ceil(-min_x))) 
        pad_top = max(0, int(np.ceil(-min_y)))  

        pad = max(pad_x, pad_y, pad_left, pad_top)

        padded_image = cv2.copyMakeBorder(base_image, pad, pad, pad, pad, cv2.BORDER_REFLECT)

        if transformation_type == 'homography':
            compensated_padded = cv2.warpPerspective(padded_image, matrix, (padded_image.shape[1], padded_image.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        else:
            compensated_padded = cv2.warpAffine(padded_image, matrix, (padded_image.shape[1], padded_image.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        compensated_image = compensated_padded[pad:pad+h, pad:pad+w] if keep_edges else compensated_padded

        return compensated_image

def main(db_path, update_progress=None, batch_size=8, stop_requested=None, single_process=None, batch_id=None,
         config_filename=None, save_align=None, align_folder=None, command_save_to_hd5f=None):
    
    # Inisialisasi processor dan konfigurasi
    processor = AKAZEAlgorithm(db_path)
    config = processor.load_akaze_config(config_filename)
    
    if save_align is None:
        save_align = config.get("save_align", False)
    
    if command_save_to_hd5f is None:
        command_save_to_hd5f = config.get("command_save_to_hd5f", True)
    
    if align_folder is None:
        align_folder = config.get("align_folder", os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image"))
    
    enable_cropping = config.get("enable_cropping", True)
    transformation_type = config.get("transformation", "affine")
    
    # Dapatkan semua path gambar
    if single_process:
        image_paths = processor.get_all_image_paths_for_single_process()
    else:
        if batch_id is None:
            raise ValueError(language_config.BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS)
        image_paths = processor.get_all_image_paths_for_batch_process(batch_id)
    
    if not image_paths:
        if update_progress:
            update_progress(0, language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
        return
    
    # Ekstrak metadata dari seluruh gambar dan simpan ke file JSON
    metadata_folder = os.path.join("database", "align")
    os.makedirs(metadata_folder, exist_ok=True)
    metadata_file = os.path.join(metadata_folder, "metadata.json")
    extract_all_metadata(image_paths, metadata_file=metadata_file)
    
    # Proses gambar pertama sebagai base_image
    base_image_path = image_paths[0]
    base_image = cv2.imread(base_image_path, cv2.IMREAD_UNCHANGED)
    if base_image is None:
        print(language_config.LOAD_IMAGES_FROM_PATHS_LOAD_FAILED)
        return
    
    total_images = len(image_paths)
    total_batches = (total_images - 1) // batch_size + 1
    total_steps = total_images * 2
    current_step = 0
    
    transform_folder = os.path.join("database", "align", "transformasi")
    os.makedirs(transform_folder, exist_ok=True)
    
    # Phase 1: Estimasi transformasi
    for batch_idx in range(total_batches):
        if stop_requested and stop_requested():
            break
        
        start_idx = batch_idx * batch_size + 1
        end_idx = min((batch_idx + 1) * batch_size + 1, total_images)
        batch_paths = image_paths[start_idx:end_idx]
        batch_images = load_images_from_paths(batch_paths)
        if not batch_images:
            continue
        
        for i, target_image in enumerate(batch_images, start=start_idx):
            if stop_requested and stop_requested():
                break
            
            info_message = language_config.RUN_IMAGE_PROCESSING.format(i=i, total_images=total_images)
            print(info_message)
            
            base_points, target_points = processor.calculate_global_motion(base_image, target_image)
            if base_points is None or target_points is None:
                print(language_config.FAIL_COMPENSATE_MOTION_PROCESS.format(i=i))
                current_step += 1
                if update_progress:
                    update_progress(current_step, total_steps, language_config.FAIL_COMPENSATE_MOTION_PROCESS.format(i))
                continue
            
            transform_file_path = os.path.join(transform_folder, f"transform_{i}.npy")
            np.save(transform_file_path, (base_points, target_points))
            
            current_step += 1
            if update_progress:
                update_progress(current_step, total_steps, info_message)
        
        del batch_images, batch_paths
        gc.collect()
    
    # Hitung crop bounds jika diaktifkan
    crop_bounds = None
    if enable_cropping:
        h, w = base_image.shape[:2]
        crop_bounds = compute_global_crop(transform_folder, total_images, w, h, transformation_type=transformation_type)
        if crop_bounds is None:
            print(language_config.FAILED_TO_COMPUTE_CROP)
            return
        np.save(os.path.join(transform_folder, "crop.npy"), crop_bounds)
    
    # Phase 2: Terapkan transformasi dan simpan ke HDF5 jika diizinkan
    with h5py.File(processor.hdf5_path, "w") as h5f:
        if enable_cropping:
            base_image = crop_image(base_image, crop_bounds)
        
        # Simpan referensi gambar ke HDF5 hanya jika command_save_to_hd5f aktif
        if command_save_to_hd5f:
            h5f.create_dataset("image_0", data=base_image)
        
        if save_align:
            save_align_to_folder(base_image, 0, base_image_path, align_folder)
        
        num_threads = os.cpu_count() or 4
        
        for batch_idx in range(total_batches):
            if stop_requested and stop_requested():
                break
            
            start_idx = batch_idx * batch_size + 1
            end_idx = min((batch_idx + 1) * batch_size + 1, total_images)
            batch_paths = image_paths[start_idx:end_idx]
            batch_images = load_images_from_paths(batch_paths)
            if not batch_images:
                continue
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for i, target_image in enumerate(batch_images, start=start_idx):
                    if stop_requested and stop_requested():
                        break
                    
                    transform_file_path = os.path.join(transform_folder, f"transform_{i}.npy")
                    if not os.path.exists(transform_file_path):
                        print(language_config.FAIL_LOAD_TRANSFORMATION_MATRIX_FILE.format(i))
                        current_step += 1
                        if update_progress:
                            update_progress(current_step, total_steps, language_config.FAIL_LOAD_TRANSFORMATION_MATRIX_FILE.format(i))
                        continue
                    
                    base_points, target_points = np.load(transform_file_path, allow_pickle=True)
                    compensated_image = processor.compensate_motion(target_image, base_points, target_points)
                    
                    if enable_cropping:
                        compensated_image = crop_image(compensated_image, crop_bounds)
                    
                    if save_align:
                        save_align_to_folder(compensated_image, i, batch_paths[i - start_idx], align_folder)
                    
                    # Ekstrak metadata untuk gambar yang sedang diproses (dari path asli)
                    original_path = batch_paths[i - start_idx]
                    metadata = extract_exif(original_path)
                    
                    # Simpan ke HDF5 jika diizinkan, sertakan metadata
                    if command_save_to_hd5f:
                        dataset_name = f"image_{i}"
                        futures.append(executor.submit(save_to_hdf5, h5f, dataset_name, compensated_image, metadata))
                    
                    current_step += 1
                    if update_progress:
                        update_progress(current_step, total_steps,
                                        language_config.PROGRESS_SAVING_CALCULATE_AND_COMPENSATE_MOTION.format(i, total_images))
                    
                    del base_points, target_points, compensated_image
                
                for future in futures:
                    future.result()
            
            del batch_images, batch_paths, futures
            gc.collect()
                
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