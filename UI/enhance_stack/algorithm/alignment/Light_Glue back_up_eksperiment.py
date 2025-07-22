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
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModel


from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import compute_global_crop, crop_image, extract_all_metadata, extract_exif, get_all_image_paths_for_single_process, load_images_from_paths, process_and_crop, resize_all_with_padding, resize_with_padding, save_align_to_folder, save_to_hdf5
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config
from config import ALGORITHM_PARAMETER_SETTINGS_FILE

# 1. Tentukan path dan ID model
DEVICE = torch.device("cuda")
MODEL_ID = "ETH-CVG/lightglue_superpoint"
LOCAL_MODEL_PATH = os.path.join("database", "Learning_Model", "lightglue_superpoint")

processor = None
model = None

try:
    # 2. Coba muat dari path lokal terlebih dahulu
    if os.path.exists(os.path.join(LOCAL_MODEL_PATH, "config.json")):
        print(f"Loading model from local path: {LOCAL_MODEL_PATH}")
        # --- TAMBAHKAN use_fast=True DI SINI ---
        processor = AutoImageProcessor.from_pretrained(LOCAL_MODEL_PATH, use_fast=True)
        model = AutoModel.from_pretrained(LOCAL_MODEL_PATH).eval().to(DEVICE)
    else:
        # 3. Jika path lokal tidak ada, unduh dari Hugging Face
        print(f"Local model not found. Downloading from '{MODEL_ID}'...")
        os.makedirs(LOCAL_MODEL_PATH, exist_ok=True)

        # --- TAMBAHKAN use_fast=True DI SINI JUGA ---
        processor = AutoImageProcessor.from_pretrained(MODEL_ID, use_fast=True)
        model = AutoModel.from_pretrained(MODEL_ID).eval().to(DEVICE)
        
        # 4. Simpan ke path lokal untuk penggunaan berikutnya
        print(f"Saving model to {LOCAL_MODEL_PATH} for future use...")
        processor.save_pretrained(LOCAL_MODEL_PATH)
        model.save_pretrained(LOCAL_MODEL_PATH)

    print("Model and processor loaded successfully.")

except Exception as e:
    print(f"FATAL: Could not load or download the alignment model. Error: {e}")
    processor = None
    model = None


class LightGlueAlgorithm:
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
        Membaca konfigurasi dari file JSON. 
        UNTUK PENGUJIAN: Saat ini dimodifikasi untuk selalu mengembalikan
        parameter default yang dioptimalkan untuk LightGlue.
        """
        # --- LANGKAH 1: Optimalkan nilai default untuk LightGlue ---
        default_config = {
            # Parameter utama untuk alignment
            "transformation": "homography",     # Gunakan model yang lebih kuat
            "ransacThreshold": 4.0,             # Ambang batas yang lebih ketat untuk presisi LightGlue

            # Parameter lain yang masih relevan untuk proses penyimpanan/cropping
            "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image"),
            "keep_edges": False,
            "enable_cropping": False,
            "save_align": False,
            "command_save_to_hd5f": True,
            
            # Parameter di bawah ini tidak lagi relevan untuk LightGlue, tetapi biarkan saja
            # untuk menjaga kompatibilitas jika file config dibaca lagi nanti.
            "nfeatures": 1500, "scaleFactor": 1.1, "nlevels": 5,
            "clahe_clipLimit": 2.0, "clahe_tileGridSize": [8, 8],
            "ratio_threshold": 0.75, "min_matches_for_transform": 10,
            "use_multi_core": True
        } 
        config_data = default_config.copy()

        # --- LANGKAH 2: Nonaktifkan sementara pembacaan dari file JSON ---
        # Dengan menonaktifkan blok di bawah, `config_data` tidak akan pernah
        # diperbarui dengan nilai dari file, sehingga fungsi ini akan
        # selalu mengembalikan `default_config` di atas.

        """
        ### BAGIAN INI DINONAKTIFKAN SEMENTARA UNTUK PENGUJIAN ###
        
        if config_filename is None:
            config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE 

        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                loaded_orb_config = params.get("ORB", {})
                config_data.update(loaded_orb_config)
            else:
                 print(f"Info: Config file '{config_filename}' not found. Using defaults.")

        except Exception as e:
            print(f"Error loading configuration from '{config_filename}': {e}. Using defaults.")
            config_data = default_config.copy() # Kembali ke default jika error
        
        ### AKHIR DARI BAGIAN YANG DINONAKTIFKAN ###
        """
        
        # Bagian ini tidak perlu diubah
        if isinstance(config_data.get("clahe_tileGridSize"), list):
             config_data["clahe_tileGridSize"] = tuple(config_data["clahe_tileGridSize"])
        elif not isinstance(config_data.get("clahe_tileGridSize"), tuple):
             config_data["clahe_tileGridSize"] = (8, 8)

        # Cetak pesan agar Anda tahu mode pengujian aktif
        print("--- Using LightGlue Test Configuration ---")
        print(f"   Transformation: {config_data['transformation']}")
        print(f"   RANSAC Threshold: {config_data['ransacThreshold']}")
        print("----------------------------------------")
        
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
        Menghitung keypoints menggunakan LightGlue. Secara internal akan mengonversi
        gambar 16-bit ke 8-bit hanya untuk deteksi fitur.
        """
        if stop_requested and stop_requested(): return None, None
        if model is None or processor is None:
            print("Hugging Face models are not available. Aborting.")
            return None, None

        # --- LANGKAH BARU: Konversi internal ke uint8 ---
        def convert_to_uint8_if_needed(img):
            """Konversi gambar ke uint8, menangani uint16 dengan benar."""
            if img.dtype == np.uint16:
                # Turunkan skala dari 0-65535 ke 0-255
                return (img / 257.0).astype(np.uint8)
            elif img.dtype == np.uint8:
                # Tidak perlu melakukan apa-apa
                return img
            else:
                # Untuk tipe lain seperti float, normalisasi terlebih dahulu
                norm_img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
                return norm_img.astype(np.uint8)

        try:
            # Buat salinan 8-bit untuk deteksi fitur
            base_image_8bit = convert_to_uint8_if_needed(base_image)
            target_image_8bit = convert_to_uint8_if_needed(target_image)
        except Exception as e:
            print(f"Error converting images to 8-bit for feature detection: {e}")
            return None, None

        # --- 1. Persiapan Gambar (menggunakan versi 8-bit) ---
        # Gambar asli (base_image, target_image) tidak diubah
        base_pil = Image.fromarray(cv2.cvtColor(base_image_8bit, cv2.COLOR_BGR2RGB))
        target_pil = Image.fromarray(cv2.cvtColor(target_image_8bit, cv2.COLOR_BGR2RGB))
        
        try:
            inputs = processor(images=[base_pil, target_pil], return_tensors="pt").to(DEVICE)
        except Exception as e:
            print(f"Error during HF processing: {e}")
            return None, None

        # --- 2. Lakukan Matching & Ekstrak Output Mentah ---
        try:
            with torch.no_grad():
                outputs = model(**inputs)

            # --- 3. Lakukan Post-Processing (PERUBAHAN FINAL DI SINI) ---
            image_sizes = [[(img.height, img.width) for img in [base_pil, target_pil]]]
            
            # HAPUS nama keyword "original_images_sizes="
            # Teruskan `image_sizes` sebagai argumen posisional kedua.
            processed_outputs = processor.post_process_keypoint_matching(
                outputs, image_sizes, threshold=0.1
            )
            # --- AKHIR PERUBAHAN ---

            result = processed_outputs[0]
            mkpts0 = result["keypoints0"].cpu().numpy()
            mkpts1 = result["keypoints1"].cpu().numpy()

            if len(mkpts0) < 8:
                print(f"DEBUG: Alignment failed. Found only {len(mkpts0)} matches, which is less than 8. Aborting for this image.")
                return None, None

            # --- 4. Format output agar sesuai ---
            base_points = np.float32(mkpts0).reshape(-1, 1, 2)
            target_points = np.float32(mkpts1).reshape(-1, 1, 2)

            if torch.cuda.is_available(): torch.cuda.empty_cache()
            return base_points, target_points

        except Exception as e:
            if torch.cuda.is_available(): torch.cuda.empty_cache()
            import traceback
            print(f"An error occurred during Hugging Face model inference: {e}")
            traceback.print_exc()
            return None, None
    
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
    
    # --- Inisialisasi (Tidak ada perubahan di sini) ---
    processor = LightGlueAlgorithm(db_path)
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
    
    progress_counter = {"count": 1 if not enable_cropping or keep_edges else 0}
    progress_lock = threading.Lock() # Lock tetap ada, tidak masalah

    if single_process:
        image_paths = get_all_image_paths_for_single_process(db_path)
        processor.hdf5_path = "database/align/aligned_images.h5"
    else:
        if batch_id is None:
            raise ValueError("Batch ID harus ada saat proses batch") # Ganti dengan variabel bahasa Anda
        image_paths = processor.get_all_image_paths_for_batch_process(batch_id)
        processor.hdf5_path = f"database/align/aligned_image_batch_{batch_id}.h5"

    if not image_paths:
        if update_progress:
            update_progress(0, "Gagal memuat gambar") # Ganti dengan variabel bahasa Anda
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

    lock = threading.Lock() # Lock tetap ada, tidak masalah
    with h5py.File(processor.hdf5_path, "w") as h5f:
        if command_save_to_hd5f:
            h5f.create_dataset("image_0", data=base_image)
        if save_align:
            save_align_to_folder(base_image, 0, image_paths[0], align_folder)

    # --- Definisi Fungsi Helper (Tidak ada perubahan) ---
    def process_image(i, path, return_transform=False):
        # Fungsi ini tetap sama, debug print masih sangat berguna
        print(f"\n--- DEBUG: Worker starting for image index {i} ---")
        if stop_requested and stop_requested():
            print(f"DEBUG [{i}]: Stop requested. Exiting worker.")
            return None
        img_list = load_images_from_paths([path], stop_requested=stop_requested)
        if not img_list or img_list[0] is None:
            print(f"DEBUG [{i}]: Failed to load image from path: {path}")
            return None
        print(f"DEBUG [{i}]: Image loaded successfully.")
        target_image = resize_with_padding(img_list[0], (target_h, target_w))
        print(f"DEBUG [{i}]: Base image shape: {base_image.shape}, Target image shape: {target_image.shape}")
        print(f"DEBUG [{i}]: Calling calculate_global_motion...")
        base_pts, target_pts = processor.calculate_global_motion(base_image, target_image)
        if base_pts is None or target_pts is None:
            print(f"DEBUG [{i}]: calculate_global_motion returned None. Worker finishing for this image.")
            return None
        print(f"DEBUG [{i}]: calculate_global_motion SUCCEEDED. Found {len(base_pts)} points.")
        print(f"DEBUG [{i}]: Calling compensate_motion...")
        compensated = processor.compensate_motion(target_image, base_pts, target_pts)
        if compensated is None:
            print(f"DEBUG [{i}]: compensate_motion returned None. Worker finishing for this image.")
            return None
        print(f"DEBUG [{i}]: compensate_motion SUCCEEDED.")
        if enable_cropping and not keep_edges and return_transform:
            return (i, path, base_pts, target_pts)
        if enable_cropping and not keep_edges:
            return None
        print(f"DEBUG [{i}]: Proceeding to save results...")
        if save_align:
            save_align_to_folder(compensated, i, path, align_folder)
        if command_save_to_hd5f:
            with lock:
                with h5py.File(processor.hdf5_path, "a") as h5f:
                    save_to_hdf5(h5f, f"image_{i}", compensated, extract_exif(path))
        print(f"--- DEBUG: Worker finished successfully for image index {i} ---")
        return None

    # Variabel num_threads tidak lagi diperlukan
    # num_threads = 1
    
    # --- BLOK PEMROSESAN UTAMA (PERUBAHAN DI SINI) ---
    if not enable_cropping or keep_edges:
        # === Streaming tanpa cropping (Mode Sekuensial) ===
        print("\n--- INFO: Running alignment in sequential mode (No ThreadPoolExecutor) ---\n")
        for i, path in enumerate(image_paths[1:], start=1):
            if stop_requested and stop_requested(): break
            # Panggil fungsi secara langsung
            process_image(i, path)
            # Update progress bar
            with progress_lock:
                progress_counter["count"] += 1
                if update_progress:
                    update_progress(
                        progress_counter["count"], total_images,
                        f"Processing image {progress_counter['count']}/{total_images}" # Ganti dengan variabel bahasa Anda
                    )
    else:
        # === Global cropping (Mode Sekuensial) ===
        # --- Tahap 1: Hitung transformasi ---
        print("\n--- INFO: Cropping Stage 1: Calculating transforms sequentially ---\n")
        all_transforms = []
        for i, path in enumerate(image_paths[1:], start=1):
            if stop_requested and stop_requested(): break
            result = process_image(i, path, return_transform=True)
            if result is not None:
                all_transforms.append(result)
            with progress_lock:
                progress_counter["count"] += 1
                if update_progress:
                    update_progress(
                        progress_counter["count"], 2 * (total_images - 1),
                        f"Calculating transform {progress_counter['count']}/{total_images - 1}" # Ganti dengan variabel bahasa Anda
                    )
        
        # --- Tahap 2: Hitung dan terapkan crop global (Tidak ada perubahan) ---
        print("\n--- INFO: Cropping Stage 2: Computing global crop bounds ---\n")
        crop_bounds = compute_global_crop(
            [(i, b, t) for i, _, b, t in all_transforms],
            total_images, base_image.shape[1], base_image.shape[0],
            transformation_type=transformation_type
        )
        if crop_bounds is None:
            print("Failed to compute crop bounds.") # Ganti dengan variabel bahasa Anda
            return
        base_image_cropped = crop_image(base_image, crop_bounds)
        del base_image
        gc.collect()
        with h5py.File(processor.hdf5_path, "a") as h5f:
            del h5f["image_0"]
            h5f.create_dataset("image_0", data=base_image_cropped)
            if save_align:
                save_align_to_folder(base_image_cropped, 0, image_paths[0], align_folder)

        # --- Tahap 3: Streaming ulang, align dan simpan hasil crop ---
        def apply_transform_and_save(i, path, base_pts, target_pts):
            # Fungsi helper ini tetap sama
            img_list = load_images_from_paths([path], stop_requested=stop_requested)
            if not img_list or img_list[0] is None: return
            target_image = resize_with_padding(img_list[0], (target_h, target_w))
            compensated = processor.compensate_motion(target_image, base_pts, target_pts)
            if compensated is None: return
            cropped = crop_image(compensated, crop_bounds)
            if save_align:
                save_align_to_folder(cropped, i, path, align_folder)
            if command_save_to_hd5f:
                with lock:
                    with h5py.File(processor.hdf5_path, "a") as h5f:
                        save_to_hdf5(h5f, f"image_{i}", cropped, extract_exif(path))
            del img_list, target_image, compensated, cropped
            gc.collect()

        print("\n--- INFO: Cropping Stage 3: Applying transforms and saving sequentially ---\n")
        stage3_counter = {"count": 0}
        for i, path, b, t in all_transforms:
            if stop_requested and stop_requested(): break
            apply_transform_and_save(i, path, b, t)
            with progress_lock:
                stage3_counter["count"] += 1
                if update_progress:
                    update_progress(
                        (total_images - 1) + stage3_counter["count"],
                        2 * (total_images - 1),
                        f"Applying transform {stage3_counter['count']}/{len(all_transforms)}" # Ganti dengan variabel bahasa Anda
                    )
             
def running_light_glue(parent=None, single_process=None, batch_id=None):
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