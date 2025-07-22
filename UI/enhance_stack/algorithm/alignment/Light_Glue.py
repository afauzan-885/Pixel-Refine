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
import requests
import onnxruntime as ort

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import compute_global_crop, crop_image, enhance_contrast_clahe, extract_all_metadata, extract_exif, get_all_image_paths_for_single_process, calculate_crop_parameters, do_warp_and_crop, load_images_from_paths, process_and_crop, resize_all_with_padding, resize_with_padding, save_align_to_folder, save_to_hdf5
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config
from config import ALGORITHM_PARAMETER_SETTINGS_FILE

class LightGlueAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

        PIPELINE_ONNX = os.path.join("database", "Learning_Model", "disk_lightglue_pipeline.ort.onnx")
        if not os.path.exists(PIPELINE_ONNX):
            os.makedirs(os.path.dirname(PIPELINE_ONNX), exist_ok=True)
            print("📥 Download Model ONNX…")
            url = "https://github.com/fabio-sim/LightGlue-ONNX/releases/download/v2.0/disk_lightglue_pipeline.ort.onnx"
            with open(PIPELINE_ONNX, "wb") as f:
                f.write(requests.get(url).content)

        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = os.cpu_count()
        sess_options.inter_op_num_threads = 1
        sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        self.sess = ort.InferenceSession(
            PIPELINE_ONNX,
            sess_options=sess_options,
            providers=["CPUExecutionProvider"]
        )
        
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
            "transformation": "homography",
            "ransacThreshold": 4.0,        

            "align_folder": os.path.join(os.path.expanduser("~"), "Documents", "Pixel Refine", "align_image"),
            "keep_edges": False,
            "enable_cropping": False,
            "save_align": False,
            "command_save_to_hd5f": True,
            
            "nfeatures": 1500, "scaleFactor": 1.1, "nlevels": 5,
            "clahe_clipLimit": 2.0, "clahe_tileGridSize": [8, 8],
            "ratio_threshold": 0.75, "min_matches_for_transform": 10,
            "use_multi_core": True
        } 
        config_data = default_config.copy()

        # --- LANGKAH 2: Nonaktifkan sementara pembacaan dari file JSON ---
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

    def calculate_global_motion(self, base_image, target_image,
                                      config_filename=None, stop_requested=None):
        if stop_requested and stop_requested():
            return None, None

        def resize_and_pad(image, target_size=640):
            """Mengubah ukuran dan memberi padding agar gambar menjadi persegi."""
            h, w = image.shape[:2]
            scale = target_size / max(h, w)
            new_h, new_w = int(h * scale), int(w * scale)
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            
            pad_top = (target_size - new_h) // 2
            pad_left = (target_size - new_w) // 2
            
            padded = cv2.copyMakeBorder(
                resized, pad_top, target_size - new_h - pad_top,
                pad_left, target_size - new_w - pad_left,
                borderType=cv2.BORDER_CONSTANT, value=0
            )
            return padded, (w / new_w, h / new_h), (pad_left, pad_top)

        def prep_for_onnx(img):
            """
            Fungsi lengkap untuk pra-pemrosesan: CLAHE -> RGB -> Resize/Pad -> Tensor.
            """
            # <<< PERUBAHAN DI SINI: Terapkan CLAHE sebagai langkah pertama
            enhanced_img = enhance_contrast_clahe(img)
            
            # Lanjutkan dengan konversi warna pada gambar yang sudah ditingkatkan
            rgb = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2RGB)
            
            # Lanjutkan dengan resize dan padding
            padded, scale_factors, pad_offsets = resize_and_pad(rgb)
            
            # Konversi ke float32 dan normalisasi untuk ONNX
            return (padded.astype(np.float32)[None, :, :, :].transpose(0, 3, 1, 2) / 255.0, 
                    scale_factors, pad_offsets)

        # --- ALUR UTAMA FUNGSI ---
        
        # Mempersiapkan gambar (sekarang sudah termasuk CLAHE)
        imgL, scaleL, offsetL = prep_for_onnx(base_image)
        imgR, scaleR, offsetR = prep_for_onnx(target_image)

        # BLOK KRITIS UNTUK MANAJEMEN MEMORI (Tidak Berubah)
        keypoints_b, matches, mscores = None, None, None
        try:
            batch = np.concatenate([imgL, imgR], axis=0).astype(np.float32)
            del imgL, imgR
            
            inp_name = self.sess.get_inputs()[0].name
            keypoints_b, matches, mscores = self.sess.run(None, {inp_name: batch})

        except Exception as e:
            return None, None
        finally:
            del batch
            gc.collect()

        if keypoints_b is None:
            return None, None

        # Ekstraksi Keypoint (Tidak Berubah)
        matches = matches.astype(np.int32)
        batch_mask = matches[:, 0] == 0
        idx0 = matches[batch_mask, 1]
        idx1 = matches[batch_mask, 2]
        scores = mscores[batch_mask]

        conf_mask = scores > 0.5
        if np.sum(conf_mask) < 8:
            print("[INFO] Not enough confident matches found after filtering.")
            return None, None

        idx0, idx1 = idx0[conf_mask], idx1[conf_mask]
        
        mkptsL = keypoints_b[0][idx0].astype(np.float32)
        mkptsR = keypoints_b[1][idx1].astype(np.float32)

        del keypoints_b, matches, mscores, scores, batch_mask, conf_mask
        gc.collect()

        # Mengembalikan Koordinat ke Skala Asli (Tidak Berubah)
        def restore_coords(pts, pad, scale):
            pts -= np.array(pad)
            pts *= np.array(scale)
            return pts

        mkptsL = restore_coords(mkptsL, offsetL, scaleL)
        mkptsR = restore_coords(mkptsR, offsetR, scaleR)

        return mkptsL.reshape(-1, 1, 2), mkptsR.reshape(-1, 1, 2)
    
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
            elif transformation_type in ['similarity', 'euclidean']:
                matrix, mask = cv2.estimateAffinePartial2D(target_points.reshape(-1, 2), base_points.reshape(-1, 2),
                                                             method=cv2.USAC_MAGSAC, ransacReprojThreshold=ransac_threshold)
            elif transformation_type == 'homography':
                matrix, mask = cv2.findHomography(target_points, base_points, cv2.USAC_MAGSAC, ransac_threshold)
            else:
                # error_msg = getattr(language_config.UNRECOGNIZED_TRANSFORMATION)
                # raise ValueError(error_msg)
                raise ValueError("Tipe transformasi tidak dikenali")

            if matrix is None:
                 # error_msg = getattr(language_config.FAILED_TO_COMPUTE_TRANSFORMATION)
                 # print(error_msg)
                 print("Gagal menghitung matriks transformasi")
                 return None
            
        except (cv2.error, Exception) as e:
             # print(f"Error saat estimasi transformasi: {e}")
             return None
        
        # --- 2. Lakukan Warping pada Gambar ---
        try:
            if not keep_edges:
                # Kasus sederhana: warp tanpa menjaga tepi yang keluar
                interpolation_flag = cv2.INTER_CUBIC
                if transformation_type == 'homography':
                    return cv2.warpPerspective(base_image, matrix, (w, h), flags=interpolation_flag, borderMode=cv2.BORDER_CONSTANT)
                else:
                    return cv2.warpAffine(base_image, matrix, (w, h), flags=interpolation_flag, borderMode=cv2.BORDER_CONSTANT)
            else:
                # Kasus kompleks: hitung padding, lalu warp dan crop
                # Panggil fungsi statis untuk menghitung parameter
                pad = calculate_crop_parameters(matrix, w, h, transformation_type)
                
                if pad is None:
                    # Gagal menghitung parameter, kembali ke warp standar
                    return cv2.warpAffine(base_image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
                
                # Panggil fungsi bantuan untuk melakukan prosesnya
                return do_warp_and_crop(base_image, matrix, pad, w, h, transformation_type)

        except (cv2.error, Exception) as e:
            # print(f"Error saat warping gambar: {e}")
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

    # --- Inisialisasi (Sama seperti kode original Anda) ---
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
    progress_lock = threading.Lock()

    if single_process:
        image_paths = get_all_image_paths_for_single_process(db_path)
        processor.hdf5_path = "database/align/aligned_images.h5"
    else:
        if batch_id is None:
            raise ValueError("Batch ID harus ada saat proses batch")
        image_paths = processor.get_all_image_paths_for_batch_process(batch_id)
        processor.hdf5_path = f"database/align/aligned_image_batch_{batch_id}.h5"

    if not image_paths:
        if update_progress: update_progress(0, "Failed to load image")
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
    
    # Hapus referensi awal yang tidak perlu
    del base_image_raw, base_resized_list, base_img_list
    gc.collect()

    lock = threading.Lock()
    with h5py.File(processor.hdf5_path, "w") as h5f:
        if command_save_to_hd5f:
            h5f.create_dataset("image_0", data=base_image)
        if save_align:
            save_align_to_folder(base_image, 0, image_paths[0], align_folder)

    if not enable_cropping or keep_edges:
        for i, path in enumerate(image_paths[1:], start=1):
            if stop_requested and stop_requested(): break
            
            # Mendefinisikan variabel untuk dibersihkan nanti
            img_list, target_image, base_pts, target_pts, compensated = None, None, None, None, None
            
            try:
                # 1. Muat dan proses gambar
                img_list = load_images_from_paths([path], stop_requested=stop_requested)
                if not img_list or img_list[0] is None: continue
                
                target_image = resize_with_padding(img_list[0], (target_h, target_w))
                
                # 2. Hitung motion (sumber utama penggunaan memori)
                base_pts, target_pts = processor.calculate_global_motion(base_image, target_image)
                if base_pts is None or target_pts is None: continue
                
                # 3. Kompensasi motion
                compensated = processor.compensate_motion(target_image, base_pts, target_pts)
                if compensated is None: continue
                
                # 4. Simpan hasil
                if save_align:
                    save_align_to_folder(compensated, i, path, align_folder)
                if command_save_to_hd5f:
                    with lock:
                        with h5py.File(processor.hdf5_path, "a") as h5f:
                            save_to_hdf5(h5f, f"image_{i}", compensated, extract_exif(path))
            
            finally:
                del img_list
                del target_image
                del base_pts
                del target_pts
                del compensated
                
                gc.collect()

            with progress_lock:
                progress_counter["count"] += 1
                if update_progress:
                    update_progress(
                        progress_counter["count"], total_images,
                        f"Processing image {progress_counter['count']}/{total_images}"
                    )
    else:
        all_transforms = []
        
        # --- Tahap 1: Hitung transformasi ---
        for i, path in enumerate(image_paths[1:], start=1):
            if stop_requested and stop_requested(): break

            # Variabel untuk dibersihkan
            img_list, target_image, base_pts, target_pts = None, None, None, None
            try:
                img_list = load_images_from_paths([path], stop_requested=stop_requested)
                if not img_list or img_list[0] is None: continue
                
                target_image = resize_with_padding(img_list[0], (target_h, target_w))
                base_pts, target_pts = processor.calculate_global_motion(base_image, target_image)
                
                if base_pts is not None and target_pts is not None:
                    all_transforms.append((i, path, base_pts, target_pts))

            finally:
                del img_list
                del target_image
                gc.collect()

            with progress_lock:
                progress_counter["count"] += 1
                if update_progress:
                    update_progress(
                        progress_counter["count"], 2 * (total_images - 1),
                        f"Calculating transform {progress_counter['count']}/{total_images - 1}"
                    )

        # --- Tahap 2: Hitung dan terapkan crop global ---
        if not all_transforms:
             return

        crop_bounds = compute_global_crop(
            [(i, b, t) for i, _, b, t in all_transforms],
            total_images, base_image.shape[1], base_image.shape[0],
            transformation_type=transformation_type
        )
        if crop_bounds is None:
            return
            
        base_image_cropped = crop_image(base_image, crop_bounds)
        del base_image
        gc.collect()
        
        with h5py.File(processor.hdf5_path, "a") as h5f:
            del h5f["image_0"]
            h5f.create_dataset("image_0", data=base_image_cropped)
        if save_align:
            save_align_to_folder(base_image_cropped, 0, image_paths[0], align_folder)
        
        del base_image_cropped
        gc.collect()

        # --- Tahap 3: Streaming ulang, align dan simpan hasil crop ---
        stage3_counter = {"count": 0}
        
        temp_transforms = all_transforms
        all_transforms = [] 
        gc.collect()

        for i, path, base_pts, target_pts in temp_transforms:
            if stop_requested and stop_requested(): break

            img_list, target_image, compensated, cropped = None, None, None, None
            try:
                img_list = load_images_from_paths([path], stop_requested=stop_requested)
                if not img_list or img_list[0] is None: continue
                
                target_image = resize_with_padding(img_list[0], (target_h, target_w))
                compensated = processor.compensate_motion(target_image, base_pts, target_pts)
                if compensated is None: continue
                
                cropped = crop_image(compensated, crop_bounds)
                if save_align:
                    save_align_to_folder(cropped, i, path, align_folder)
                if command_save_to_hd5f:
                    with lock:
                        with h5py.File(processor.hdf5_path, "a") as h5f:
                            save_to_hdf5(h5f, f"image_{i}", cropped, extract_exif(path))
            finally:
                del img_list
                del target_image
                del compensated
                del cropped
                gc.collect()

            with progress_lock:
                stage3_counter["count"] += 1
                if update_progress:
                    update_progress(
                        (total_images - 1) + stage3_counter["count"],
                        2 * (total_images - 1),
                        f"Applying transform {stage3_counter['count']}/{len(temp_transforms)}"
                    )
                                
def running_light_glue(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_LIGHT_GLUE)
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