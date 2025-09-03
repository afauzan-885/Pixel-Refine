import gc
import queue
import subprocess
import sys
import threading
import traceback
import cv2
import numpy as np
import os
from pathlib import Path
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
from PySide6.QtCore import Qt
import h5py
import onnxruntime as ort
import urllib

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import (calculate_crop_parameters, deduplicate_keypoints, do_warp_and_crop, estimate_noise_variance, 
                                                                                    extract_all_metadata, get_adaptive_bilateral, get_all_image_paths_for_batch_process,
                                                                                    get_all_image_paths_for_single_process, load_images_from_paths, prepare_image,
                                                                                    resize_all_with_padding, run_pipeline_global_crop, run_pipeline_non_crop)
from UI.enhance_stack.components.single_page_layout.parameter_alignment.light_glue_parameter_settings import load_light_glue_config
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config

os.environ["ORT_CUDA_MEM_LIMIT_MB"] = "1024"

def is_frozen_app():
    """
    Memeriksa apakah aplikasi berjalan sebagai biner yang dibekukan (misalnya, Nuitka, PyInstaller).
    """
    return hasattr(sys, 'frozen') or (hasattr(sys, '_MEIPASS') or (sys.executable.endswith(".exe") and sys.executable != sys.argv[0]))

def find_cudnn_dlls():
    """
    Cari semua file cuDNN (cudnn64_*.dll) + CUDA core (cublas, cufft, curand) 
    hanya dari instalasi sistem, bukan dari venv.
    """
    dlls = []

    # --- 1. Cari di environment variable (prioritas utama: sistem) ---
    env_vars = ["CUDNN_PATH", "CUDA_PATH"] + [k for k in os.environ.keys() if k.startswith("CUDA_PATH_V")]
    for var in env_vars:
        if var in os.environ:
            p = Path(os.environ[var])
            if p.exists():
                # ambil cuDNN
                for dll in p.rglob("cudnn64_*.dll"):
                    dlls.append(dll)
                for dll in p.rglob("cublas64_*.dll"):
                    dlls.append(dll)
                for dll in p.rglob("cufft64_*.dll"):
                    dlls.append(dll)
                for dll in p.rglob("curand64_*.dll"):
                    dlls.append(dll)

    # --- 2. Cari di folder umum (misalnya instalasi CUDA di Program Files) ---
    common_dirs = [
        Path("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA"),
        Path("C:/Program Files/NVIDIA"),
        Path("C:/tools/cuda"),
    ]
    for base in common_dirs:
        if base.exists():
            for dll in base.rglob("cudnn64_*.dll"):
                dlls.append(dll)
            for dll in base.rglob("cublas64_*.dll"):
                dlls.append(dll)
            for dll in base.rglob("cufft64_*.dll"):
                dlls.append(dll)
            for dll in base.rglob("curand64_*.dll"):
                dlls.append(dll)

    # --- 3. (Opsional) Gunakan perintah `where` (Windows only) ---
    if not dlls:
        try:
            result = subprocess.check_output(["where", "cudnn64_*.dll"], shell=True, text=True).strip()
            if result:
                for line in result.splitlines():
                    path = Path(line.strip())
                    if path.exists():
                        dlls.append(path)
        except Exception:
            pass

    # Hilangkan duplikat
    dlls = list(dict.fromkeys(dlls))

    # --- Pilih versi cuDNN tertinggi saja ---
    if dlls:
        cudnn_only = [d for d in dlls if "cudnn64_" in d.name]
        if cudnn_only:
            cudnn_only.sort(key=lambda d: int(d.stem.split("cudnn64_")[-1]), reverse=True)
            highest_version = int(cudnn_only[0].stem.split("cudnn64_")[-1])
            dlls = [dll for dll in dlls if f"cudnn64_{highest_version}" in dll.name or not dll.name.startswith("cudnn64_")]

    return dlls

def add_dll_to_path():
    """
    Menambahkan direktori yang berisi DLL ONNX Runtime dan CuDNN ke PATH
    menggunakan variabel lingkungan atau pencarian global.
    """
    cudnn_dlls = find_cudnn_dlls()

    if not cudnn_dlls:
        print("[WARNING] Could not find cuDNN DLL on the system!")
    else:
        for dll in cudnn_dlls:
            dll_dir = dll.parent
            os.add_dll_directory(str(dll_dir))
            os.environ["PATH"] = str(dll_dir) + os.pathsep + os.environ.get("PATH", "")
        print(f"[INFO] Adding cuDNN from folder: {cudnn_dlls[0].parent}")

    # Check if the CUDA provider can be loaded after adding the path
    try:
        if "CUDAExecutionProvider" in ort.get_available_providers():
            print("[INFO] GPU support successfully enabled.")
        else:
            print("[WARNING] CUDAExecutionProvider tidak tersedia.")
    except Exception as e:
        print(f"[WARNING] Failed to enable GPU support. {e}")


# --- Panggil fungsi ini di awal skrip Anda ---
if os.name == 'nt':
    add_dll_to_path()
        
class LightGlueAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path
        cv2.ocl.setUseOpenCL(True)

        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

        PIPELINE_ONNX = os.path.join(
            "database", "Learning_Model", "disk_lightglue_pipeline.ort.onnx"
        )
        url = "https://github.com/fabio-sim/LightGlue-ONNX/releases/download/v2.0/disk_lightglue_pipeline.ort.onnx"

        # --- Hybrid download check ---
        need_download = False
        if os.path.exists(PIPELINE_ONNX):
            local_size = os.path.getsize(PIPELINE_ONNX)
            total_size = 0
            try:
                # HEAD request dengan urllib
                req = urllib.request.Request(url, method="HEAD")
                with urllib.request.urlopen(req) as resp:
                    if resp.getheader("Content-Length"):
                        total_size = int(resp.getheader("Content-Length"))
            except Exception:
                total_size = 0

            if total_size > 0 and local_size < total_size:
                print("📥 Resume download LightGlue model…")
                req = urllib.request.Request(url)
                req.add_header("Range", f"bytes={local_size}-")
                with urllib.request.urlopen(req) as resp, open(PIPELINE_ONNX, "ab") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                print("✅ Download Complete.")
            else:
                try:
                    _ = ort.InferenceSession(PIPELINE_ONNX)
                except Exception:
                    print("⚠️ Model file corrupt, delete and re-download…")
                    os.remove(PIPELINE_ONNX)
                    need_download = True
        else:
            need_download = True

        if need_download:
            print("📥 Download Model ONNX…")
            os.makedirs(os.path.dirname(PIPELINE_ONNX), exist_ok=True)
            with urllib.request.urlopen(url) as resp, open(PIPELINE_ONNX, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
            print("✅ Download selesai.")

        # --- Config ---
        config = load_light_glue_config()
        use_gpu = config.get("use_gpu", False)

        providers = ["CPUExecutionProvider"]
        if use_gpu:
            try:
                available_providers = ort.get_available_providers()
                if "CUDAExecutionProvider" in available_providers:
                    providers.insert(0, "CUDAExecutionProvider")
            except Exception as e:
                print(f"[ERROR] An error occurred while checking the CUDA provider: {e}. Falling back to using the CPU.")
        else:
            print("[INFO] Sesi inferensi akan menggunakan CPU (sesuai konfigurasi).")

        # --- ONNX Runtime session ---
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = os.cpu_count()
        sess_options.inter_op_num_threads = 1
        sess_options.execution_mode = ort.ExecutionMode.ORT_PARALLEL
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.add_session_config_entry("arena_extend_strategy", "kSameAsRequested")
        sess_options.add_session_config_entry("session.disable_prepacking", "0")
        sess_options.log_severity_level = 3

        self.sess = ort.InferenceSession(
            PIPELINE_ONNX, sess_options=sess_options, providers=providers
        )


    def calculate_global_motion(self, base_image, target_image, stop_requested=None):
        if stop_requested and stop_requested():
            return None, None

        h_orig, w_orig = base_image.shape[:2]
        megapixels = (h_orig * w_orig) / 1_000_000.0
        
        GRID_SIZE = (1, 1)
        if megapixels > 22.0:
            target_mp = 18.0
            scale_factor = (target_mp / megapixels) ** 0.5
            new_width = int(w_orig * scale_factor)
            new_height = int(h_orig * scale_factor)
            base_image = cv2.resize(base_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            target_image = cv2.resize(target_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            GRID_SIZE = (3, 3)
        elif 17.5 <= megapixels <= 22.0: GRID_SIZE = (2, 3)
        elif 11.5 <= megapixels <= 13.0: GRID_SIZE = (1, 2)
        elif megapixels <= 8.5: GRID_SIZE = (1, 1)

        OVERLAP_PERCENT = 0.10
        h, w = base_image.shape[:2]
        cols, rows = GRID_SIZE
        if cols <= 0 or rows <= 0: return None, None
        tile_w, tile_h = w // cols, h // rows
        if tile_w == 0 or tile_h == 0: return None, None
        overlap_w_px, overlap_h_px = int(tile_w * OVERLAP_PERCENT), int(tile_h * OVERLAP_PERCENT)

        def resize_and_pad(image, target_size=448):
            h_tile, w_tile = image.shape[:2]
            scale = target_size / max(h_tile, w_tile)
            new_h, new_w = int(h_tile * scale), int(w_tile * scale)
            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR_EXACT)
            pad_top, pad_left = (target_size - new_h) // 2, (target_size - new_w) // 2
            padded = cv2.copyMakeBorder(resized, pad_top, target_size - new_h - pad_top, pad_left, target_size - new_w - pad_left, cv2.BORDER_CONSTANT, value=0)
            return padded, (w_tile / new_w, h_tile / new_h), (pad_left, pad_top)

        def prep_for_onnx(img):
            enhanced_img = prepare_image(img, grayscale=False, use_clahe=True)
            enhanced_gray = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2GRAY)
            noise_level = estimate_noise_variance(enhanced_gray)
            if noise_level > 200.0:
                d, sigma_color, sigma_space = get_adaptive_bilateral(noise_level, 200.0, 700.0, 5, 9, 20, 75)
                enhanced_img = cv2.bilateralFilter(enhanced_img, d, sigma_color, sigma_space)
            rgb = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2RGB)
            padded, scale_factors, pad_offsets = resize_and_pad(rgb)
            return padded.astype(np.float32)[None, :, :, :].transpose(0, 3, 1, 2) / 255.0, scale_factors, pad_offsets

        def preprocessor_worker(job_q, result_q):
            while True:
                # Periksa sinyal berhenti di dalam worker juga, untuk keluar lebih cepat
                if stop_requested and stop_requested(): break
                try:
                    item = job_q.get(timeout=0.1)
                except queue.Empty:
                    continue # Jika tidak ada kerjaan, coba lagi
                    
                if item is None: break
                r, c = item
                x_start = max(0, c * tile_w - overlap_w_px)
                y_start = max(0, r * tile_h - overlap_h_px)
                x_end = min(w, (c + 1) * tile_w + overlap_w_px)
                y_end = min(h, (r + 1) * tile_h + overlap_h_px)
                base_tile = base_image[y_start:y_end, x_start:x_end]
                target_tile = target_image[y_start:y_end, x_start:x_end]
                imgL, scaleL, offsetL = prep_for_onnx(base_tile)
                imgR, scaleR, offsetR = prep_for_onnx(target_tile)
                result_q.put((r, c, imgL, imgR, scaleL, offsetL, scaleR, offsetR, x_start, y_start))

        num_tiles = rows * cols
        job_queue = queue.Queue()
        result_queue = queue.Queue(maxsize=num_tiles)
        
        preprocessor_thread = threading.Thread(target=preprocessor_worker, args=(job_queue, result_queue))
        preprocessor_thread.start()

        for r in range(rows):
            for c in range(cols):
                job_queue.put((r, c))
        job_queue.put(None)

        all_results = []
        processed_tiles = 0

        while processed_tiles < num_tiles:
            # 1. Selalu periksa sinyal berhenti di setiap iterasi
            if stop_requested and stop_requested():
                break

            try:
                # 2. Ambil hasil dengan timeout singkat, ini kuncinya
                item = result_queue.get(timeout=0.1)
                processed_tiles += 1
                r, c, imgL, imgR, scaleL, offsetL, scaleR, offsetR, x_start, y_start = item
            
            except queue.Empty:
                # 3. Jika antrian kosong, berarti worker sedang sibuk.
                # Cek apakah worker masih hidup. Jika sudah mati, tidak akan ada hasil lagi.
                if not preprocessor_thread.is_alive() and result_queue.empty():
                    break
                # Jika masih hidup, lanjutkan loop untuk mencoba lagi dan memeriksa stop_requested
                continue

            # --- Blok inferensi dan post-processing (TIDAK BERUBAH) ---
            try:
                batch = np.concatenate([imgL, imgR], axis=0).astype(np.float32)
                inp_name = self.sess.get_inputs()[0].name
                keypoints_b, matches, mscores = self.sess.run(None, {inp_name: batch})
            except Exception as e:
                print(f"ERROR: Gagal saat inferensi ONNX: {e}")
                continue

            if keypoints_b is None: continue
            
            matches = matches.astype(np.int32)
            batch_mask = matches[:, 0] == 0
            idx0, idx1, scores = matches[batch_mask, 1], matches[batch_mask, 2], mscores[batch_mask]
            
            conf_mask = scores > 0.5
            if np.sum(conf_mask) < 8: continue
            
            idx0, idx1 = idx0[conf_mask], idx1[conf_mask]
            mkptsL_padded = keypoints_b[0][idx0].astype(np.float32)
            mkptsR_padded = keypoints_b[1][idx1].astype(np.float32)

            def restore_coords(pts, pad, scale):
                return (pts - np.array(pad)) * np.array(scale)

            mkptsL_tile_local = restore_coords(mkptsL_padded, offsetL, scaleL)
            mkptsR_tile_local = restore_coords(mkptsR_padded, offsetR, scaleR)
            
            offset_global = np.array([x_start, y_start])
            mkptsL_global = mkptsL_tile_local + offset_global
            mkptsR_global = mkptsR_tile_local + offset_global
            
            all_results.append((mkptsL_global, mkptsR_global, scores[conf_mask]))
        
        preprocessor_thread.join()

        if not all_results:
            return None, None

        final_mkptsL = np.vstack([res[0] for res in all_results])
        final_mkptsR = np.vstack([res[1] for res in all_results])
        final_scores = np.concatenate([res[2] for res in all_results])

        dedup_mkptsL, dedup_mkptsR, _ = deduplicate_keypoints(
            final_mkptsL, final_mkptsR, final_scores, base_image.shape
        )
        
        if len(dedup_mkptsL) < 8:
            return None, None

        return dedup_mkptsL.reshape(-1, 1, 2), dedup_mkptsR.reshape(-1, 1, 2)
    
    def compensate_motion(
        self, base_image, base_points, target_points, config_filename=None
    ):
        """
        Menerapkan kompensasi gerakan menggunakan transformasi (dengan USAC_MAGSAC)
        untuk menyelaraskan gambar.
        """
        if (
            base_points is None
            or target_points is None
            or base_image is None
            or base_image.ndim < 2
        ):
            return None

        config = load_light_glue_config(config_filename)
        keep_edges = config.get("keep_edges", False)
        transformation_type = config.get("transformation", "affine")
        ransac_threshold = config.get("ransacThreshold", 5.0)

        h, w = base_image.shape[:2]
        if len(base_points) < 4 or len(target_points) < 4:
            return None

        # --- 1. Hitung Matriks Transformasi ---
        matrix = None
        try:
            if transformation_type == "affine":
                matrix, mask = cv2.estimateAffine2D(
                    target_points.reshape(-1, 2),
                    base_points.reshape(-1, 2),
                    method=cv2.USAC_MAGSAC,
                    ransacReprojThreshold=ransac_threshold,
                )
            elif transformation_type == "homography":
                matrix, mask = cv2.findHomography(
                    target_points, base_points, cv2.USAC_MAGSAC, ransac_threshold
                )
            else:
                raise ValueError("Tipe transformasi tidak dikenali")

            if matrix is None:
                return None

        except (cv2.error, Exception) as e:
            return None

        # --- 2. Lakukan Warping pada Gambar ---
        try:
            if not keep_edges:
                interpolation_flag = cv2.INTER_CUBIC
                if transformation_type == "homography":
                    return cv2.warpPerspective(
                        base_image,
                        matrix,
                        (w, h),
                        flags=interpolation_flag,
                        borderMode=cv2.BORDER_CONSTANT,
                    )
                else:
                    return cv2.warpAffine(
                        base_image,
                        matrix,
                        (w, h),
                        flags=interpolation_flag,
                        borderMode=cv2.BORDER_CONSTANT,
                    )
            else:
                pad = calculate_crop_parameters(matrix, w, h, transformation_type)

                if pad is None:
                    return cv2.warpAffine(
                        base_image,
                        matrix,
                        (w, h),
                        flags=cv2.INTER_CUBIC,
                        borderMode=cv2.BORDER_CONSTANT,
                    )

                # Panggil fungsi bantuan untuk melakukan prosesnya
                return do_warp_and_crop(
                    base_image, matrix, pad, w, h, transformation_type
                )

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
    processor = LightGlueAlgorithm(db_path) 
    config = load_light_glue_config(config_filename)
    
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
        num_workers = 2
    
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
            
def running_light_glue(parent=None, single_process=None, batch_id=None, progress_callback=None):
    
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
    dialog.setWindowTitle(language_config.WINDOW_TITLE_LIGHT_GLUE)
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