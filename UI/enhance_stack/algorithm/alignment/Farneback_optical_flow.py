import gc
import json
import threading
import time
import traceback
import cv2
import numpy as np
import sqlite3
import os
import concurrent.futures
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py

from PySide6.QtCore import Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import extract_all_metadata, extract_exif, get_all_image_paths_for_single_process, load_images_from_paths, resize_all_with_padding, resize_with_padding,  save_to_hdf5
# from UI.enhance_stack.algorithm.custom_gpu.grayscale_conversion import bgr_to_gray_gpu
from UI.enhance_stack.logic.multi_threading import ImageProcessingMultiThreading
from UI.settings.General.Language import language_config
from concurrent.futures import ThreadPoolExecutor

class FarnebackAlgorithm:
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
    def load_farneback_config(config_filename=None):
        """
        Membaca konfigurasi Farneback Optical Flow dari file JSON.
        Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "pyr_scale": 0.5,
            "levels": 3,
            "winsize": 15,
            "iterations": 3,
            "poly_n": 5,
            "poly_sigma": 1.2,
            "flags": 0,
            "interpolation": "INTER_CUBIC",
            "use_gpu": False,
            "use_multi_core": True
        }

        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("Farneback", default_config)
        except Exception as e:
            print("Error loading Farneback configuration:", e)
            return default_config
    
    def load_farneback_config_for_batch(config_filename=None):
        """
        Membaca konfigurasi Farneback Optical Flow dari file JSON.
        Jika gagal, mengembalikan nilai default.
        """
        default_config = {
            "pyr_scale": 0.5,
            "levels": 3,
            "winsize": 15,
            "iterations": 3,
            "poly_n": 5,
            "poly_sigma": 1.2,
            "flags": 0,
            "interpolation": "INTER_LINEAR",
            "use_gpu": False,
            "use_multi_core": True
        }

        if config_filename is None:
            config_filename = os.path.join("database", "setting", "Parameter_Stack_Enhance.json")

        try:
            with open(config_filename, "r") as config_file:
                params = json.load(config_file)
            return params.get("Farneback_BATCH", default_config)
        except Exception as e:
            # print("Error loading Farneback configuration:", e)
            return default_config
        
    def _filter_flow_by_magnitude(self, flow, min_thresh=0.1, max_thresh=10.0):
        mag = np.linalg.norm(flow, axis=2)
        mask = (mag >= min_thresh) & (mag <= max_thresh)
        filtered = np.zeros_like(flow)
        filtered[mask] = flow[mask]
        return filtered

    # def _refine_flow_median(self, flow, size=3):
    #     refined = np.zeros_like(flow)
    #     for i in range(2):  # x dan y component
    #         refined[..., i] = scipy.ndimage.median_filter(flow[..., i], size=size)
    #     return refined

    def _compute_block_cpu_internal(self, x, y, bw, bh, overlap_ratio, base_gray_8bit, target_gray_8bit, fb_config, w, h):
        overlap_x = int(bw * overlap_ratio)
        overlap_y = int(bh * overlap_ratio)
        roi_x_start = max(0, x - overlap_x)
        roi_y_start = max(0, y - overlap_y)
        roi_x_end = min(w, x + bw + overlap_x)
        roi_y_end = min(h, y + bh + overlap_y)
        if roi_y_end <= roi_y_start or roi_x_end <= roi_x_start:
            return None

        roi_base = base_gray_8bit[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
        roi_target = target_gray_8bit[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

        try:
            flow_roi = cv2.calcOpticalFlowFarneback(
                roi_base, roi_target, None,
                pyr_scale=fb_config["pyr_scale"], levels=fb_config["levels"],
                winsize=fb_config["winsize"], iterations=fb_config["iterations"],
                poly_n=fb_config["poly_n"], poly_sigma=fb_config["poly_sigma"],
                flags=fb_config["flags"]
            )
            offset_x = x - roi_x_start
            offset_y = y - roi_y_start
            bh_valid = min(bh, flow_roi.shape[0] - offset_y)
            bw_valid = min(bw, flow_roi.shape[1] - offset_x)
            if bh_valid <= 0 or bw_valid <= 0:
                return None
            flow_block = flow_roi[offset_y:offset_y + bh_valid, offset_x:offset_x + bw_valid, :]

            # Filter magnitude outliers (flow quality filtering)
            flow_block = self._filter_flow_by_magnitude(flow_block)

            return (x, y, flow_block)
        except cv2.error: return None
        except Exception: return None

    def calculate_optical_flow(self, base_image, target_image, config_filename=None, stop_requested=None):
        if stop_requested and stop_requested():
            return None

        fb_config = self.load_farneback_config(config_filename)
        opencl_available = cv2.ocl.haveOpenCL()
        use_gpu = fb_config.get("use_gpu", False) and opencl_available
        use_multicore = fb_config.get("use_multi_core", True)

        try:
            # def prepare_gray(img):
            #     if img is None:
            #         raise ValueError("Input image is None.")
            #     if img.ndim == 3:
            #         if use_gpu:
            #             return bgr_to_gray_gpu(img)
            #         else:
            #             img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #     return img.astype(np.uint8, copy=False)
            def prepare_gray(img):
                if img is None:
                    raise ValueError("Input image is None.")
                if img.ndim == 3:
                    # Tidak melakukan konversi GPU
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                return img.astype(np.uint8, copy=False)

            base_gray_8bit = prepare_gray(base_image)
            target_gray_8bit = prepare_gray(target_image)
            h, w = base_gray_8bit.shape
            flow_full = None

            if use_gpu:
                try:
                    base_gray_umat = cv2.UMat(base_gray_8bit)
                    target_gray_umat = cv2.UMat(target_gray_8bit)
                    flow_umat = cv2.calcOpticalFlowFarneback(
                        base_gray_umat, target_gray_umat, None,
                        pyr_scale=fb_config["pyr_scale"], levels=fb_config["levels"],
                        winsize=fb_config["winsize"], iterations=fb_config["iterations"],
                        poly_n=fb_config["poly_n"], poly_sigma=fb_config["poly_sigma"],
                        flags=fb_config["flags"]
                    )
                    flow_full = flow_umat.get()
                except Exception as e:
                    print(f"GPU error: {e}, falling back to CPU")
                    use_gpu = False

            if not use_gpu:
                num_blocks_config = fb_config.get("cpu_num_blocks", [10, 8])
                overlap_ratio = fb_config.get("cpu_overlap_ratio", 0.3)
                if isinstance(num_blocks_config, (list, tuple)) and len(num_blocks_config) == 2:
                    blocks_x, blocks_y = num_blocks_config
                else:
                    blocks_x, blocks_y = 2, 2

                try:
                    overlap_ratio = float(overlap_ratio)
                    assert 0.0 <= overlap_ratio < 1.0
                except:
                    overlap_ratio = 0.3

                block_w = w // blocks_x
                block_h = h // blocks_y
                if block_w == 0 or block_h == 0:
                    blocks_x, blocks_y = 1, 1
                    block_w, block_h = w, h

                flow_full_cpu = np.empty((h, w, 2), dtype=np.float32)
                compute_block_cpu = lambda x, y, bw, bh, ovr: self._compute_block_cpu_internal(
                    x, y, bw, bh, ovr, base_gray_8bit, target_gray_8bit, fb_config, w, h
                )

                if use_multicore:
                    futures_cpu = []
                    num_workers = max(1, os.cpu_count())
                    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                        for i in range(blocks_x):
                            for j in range(blocks_y):
                                if stop_requested and stop_requested():
                                    break
                                x = i * block_w
                                y = j * block_h
                                bw = block_w if i < blocks_x - 1 else w - x
                                bh = block_h if j < blocks_y - 1 else h - y
                                futures_cpu.append(executor.submit(compute_block_cpu, x, y, bw, bh, overlap_ratio))
                            if stop_requested and stop_requested():
                                break
                        if stop_requested and stop_requested():
                            for f in futures_cpu:
                                f.cancel()
                            return None
                        for future in concurrent.futures.as_completed(futures_cpu):
                            if stop_requested and stop_requested():
                                return None
                            try:
                                result_block = future.result()
                                if result_block:
                                    x, y, flow_block = result_block
                                    h_block, w_block, _ = flow_block.shape
                                    y_end = min(y + h_block, h)
                                    x_end = min(x + w_block, w)
                                    flow_full_cpu[y:y_end, x:x_end, :] = flow_block[0:y_end - y, 0:x_end - x, :]
                            except Exception as exc:
                                print(f'Block processing generated an exception: {exc}')
                else:
                    for i in range(blocks_x):
                        for j in range(blocks_y):
                            if stop_requested and stop_requested():
                                return None
                            x = i * block_w
                            y = j * block_h
                            bw = block_w if i < blocks_x - 1 else w - x
                            bh = block_h if j < blocks_y - 1 else h - y
                            result_block = compute_block_cpu(x, y, bw, bh, overlap_ratio)
                            if result_block:
                                x, y, flow_block = result_block
                                h_block, w_block, _ = flow_block.shape
                                y_end = min(y + h_block, h)
                                x_end = min(x + w_block, w)
                                flow_full_cpu[y:y_end, x:x_end, :] = flow_block[0:y_end - y, 0:x_end - x, :]
                        if stop_requested and stop_requested():
                            break

                # flow_full_cpu = self._refine_flow_median(flow_full_cpu, size=3)
                flow_full = flow_full_cpu

            return flow_full

        except ValueError as ve:
            print(f"Gagal menyiapkan gambar: {ve}")
            return None
        except Exception as e:
            print(f"Unexpected error in calculate_optical_flow: {e}\n{traceback.format_exc()}")
            return None
    
    def compensate_motion(self, base_image_input, flow, image_id=0, config_filename=None):
        if flow is None:
            print(language_config.ERROR_IN_FLOW_FIELD.format(image_id))
            return None
        if base_image_input is None:
            print(language_config.ERROR_IN_BASE_IMAGE.format(image_id))
            return None

        try:
            if isinstance(flow, cv2.UMat):
                flow_np = flow.get()
                h, w = flow_np.shape[:2]
            elif isinstance(flow, np.ndarray):
                if flow.ndim != 3 or flow.shape[2] != 2:
                    raise ValueError(f"Invalid flow field shape: {flow.shape}. Expected (h, w, 2).")
                h, w = flow.shape[:2]
            else:
                raise ValueError("Flow harus berupa numpy array atau UMat.")

            h, w = flow.shape[:2]
            if base_image_input.shape[:2] != (h, w):
                raise ValueError(f"Base image shape {base_image_input.shape[:2]} mismatch with flow field shape {flow.shape[:2]}.")

            grid_y, grid_x = np.mgrid[0:h, 0:w]
            remap_x = (grid_x + flow[:, :, 0]).astype(np.float32)
            remap_y = (grid_y + flow[:, :, 1]).astype(np.float32)

            fb_config = self.load_farneback_config(config_filename)
            use_gpu = fb_config.get("use_gpu", False) and cv2.ocl.haveOpenCL()
            interpolation_str = fb_config.get("interpolation", "INTER_LINEAR")
            use_multicore = fb_config.get("use_multi_core", True)
            interp_flag = getattr(cv2, interpolation_str, cv2.INTER_LINEAR)

            if use_gpu:
                try:
                    base_image_umat = cv2.UMat(base_image_input)
                    remap_x_umat = cv2.UMat(remap_x)
                    remap_y_umat = cv2.UMat(remap_y)

                    compensated_image_umat = cv2.remap(
                        base_image_umat,
                        remap_x_umat,
                        remap_y_umat,
                        interpolation=interp_flag,
                        borderMode=cv2.BORDER_REFLECT
                    )
                    return compensated_image_umat.get()
                except cv2.error as gpu_remap_err:
                    print(f"[GPU REMAP ERROR] Fallback to CPU. Reason: {gpu_remap_err}")
                    use_gpu = False
                    del base_image_umat, remap_x_umat, remap_y_umat
                except Exception as gpu_remap_exc:
                    print(f"[GPU FALLBACK] Exception: {gpu_remap_exc}")
                    use_gpu = False

            # ===== CPU MULTICORE WITH OVERLAP =====
            if use_multicore:
                num_chunks = 4
                h_chunk = h // num_chunks
                overlap = int(0.2 * h_chunk)

                def remap_chunk(y_start, y_end):
                    base_chunk = base_image_input[y_start:y_end]
                    rx_chunk = remap_x[y_start:y_end]
                    ry_chunk = remap_y[y_start:y_end]
                    return cv2.remap(base_chunk, rx_chunk, ry_chunk, interpolation=interp_flag, borderMode=cv2.BORDER_REFLECT)

                chunks = []
                with ThreadPoolExecutor(max_workers=num_chunks) as executor:
                    futures = []
                    for i in range(num_chunks):
                        y1 = max(0, i * h_chunk - overlap)
                        y2 = min(h, (i + 1) * h_chunk + overlap)
                        futures.append(executor.submit(remap_chunk, y1, y2))
                    chunks = [f.result() for f in futures]

                # Pangkas overlap dan gabungkan hasil
                trimmed_chunks = []
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        trimmed = chunk[:h_chunk]
                    elif i == num_chunks - 1:
                        trimmed = chunk[overlap:]
                    else:
                        trimmed = chunk[overlap:overlap + h_chunk]
                    trimmed_chunks.append(trimmed)

                compensated_image = np.vstack(trimmed_chunks)
                return compensated_image

            # ===== Fallback Single Thread =====
            else:
                return cv2.remap(
                    base_image_input,
                    remap_x,
                    remap_y,
                    interpolation=interp_flag,
                    borderMode=cv2.BORDER_REFLECT
                )

        except ValueError as ve:
            print(f"[VALUE ERROR] {ve}")
            return None
        except cv2.error as cv_err:
            print(f"[OpenCV ERROR] {cv_err}")
            return None
        except Exception as e:
            print(f"[EXCEPTION] {e}")
            return None

def main(
    db_path,
    update_progress=None,
    stop_requested=None,
    single_process=None,
    batch_id=None
):
    processor = FarnebackAlgorithm(db_path)

    # 1) Ambil daftar image_paths & set hdf5_path
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

    # 2) Ekstrak metadata seluruh gambar
    os.makedirs("database/align", exist_ok=True)
    extract_all_metadata(image_paths, metadata_file=os.path.join("database", "align", "metadata.json"))

    total_images = len(image_paths)

    # 3) Load & resize base image
    base_img_list = load_images_from_paths([image_paths[0]], stop_requested=stop_requested)
    if not base_img_list or base_img_list[0] is None:
        raise RuntimeError("Base image gagal dimuat.")
    base_image_raw = base_img_list[0]
    base_resized_list, (target_h, target_w) = resize_all_with_padding([base_image_raw], method="median")
    base_image = base_resized_list[0]

    # 4) Simpan base image ke HDF5
    with h5py.File(processor.hdf5_path, "w") as h5f:
        h5f.create_dataset("image_0", data=base_image)
        
    # Lock untuk penulisan HDF5 secara aman
    lock = threading.Lock()
    progress_lock = threading.Lock()
    progress_counter = {"count": 1}  # Sudah simpan image_0

    # 5) Streaming image satu per satu
    with h5py.File(processor.hdf5_path, "a") as h5f:
        for i, path in enumerate(image_paths[1:], start=1):
            if stop_requested and stop_requested():
                break

            if update_progress:
                update_progress(i, total_images, language_config.RUN_IMAGE_PROCESSING.format(i=i, total_images=total_images))

            img_list = load_images_from_paths([path], stop_requested=stop_requested)
            if not img_list or img_list[0] is None:
                continue

            target_image = resize_with_padding(img_list[0], (target_h, target_w))
            flow = processor.calculate_optical_flow(base_image, target_image)
            compensated = processor.compensate_motion(target_image, flow, image_id=i)

            if compensated is not None:
                save_to_hdf5(h5f, f"image_{i}", compensated, extract_exif(path))

            del img_list, target_image, flow, compensated
            gc.collect()

    if update_progress:
        update_progress(total_images, total_images, language_config.SAVE_TO_HDF5_IMAGE_ALIGNED_SAVING_FINISHED)

def running_farneback_optical_flow(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_FARNEBACK)
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