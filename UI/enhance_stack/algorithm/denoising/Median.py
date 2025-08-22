import traceback
import cv2
import numpy as np
import numpy.ma as ma
import sqlite3
import concurrent.futures
import os
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PySide6.QtCore import Qt, QThread, Signal

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import batch_image_generator, extract_all_metadata, get_all_image_paths_for_single_process, load_images_from_paths, resize_all_with_padding, save_image, setup_balanced_batching
from UI.resources.stylesheet.stylesheet import PROGRESS_BAR
from UI.settings.General.GeneralSetting import load_general_settings
from UI.settings.General.Language import language_config

class ThreadWorker(QThread):
    progress_updated = Signal(int, str)  # Sinyal untuk memperbarui progress
    finished = Signal()  # Sinyal untuk menandakan selesai
    error_occurred = Signal(str)  # Sinyal untuk menandakan error

    def __init__(self, db_path, single_process=True, batch_id=None):
        super().__init__()
        self.db_path = db_path
        self.single_process = single_process  # Menentukan apakah proses single atau batch
        self.batch_id = batch_id  # ID batch jika batch processing
        self.stop_requested = False  # Flag untuk menghentikan thread

    def run(self):
        try:
            def update_progress(progress, message):
                self.progress_updated.emit(progress, message)

            # Fungsi callback untuk mengecek status stop
            def is_stop_requested():
                return self.stop_requested

            # Panggil main dengan parameter yang sesuai
            main(
                self.db_path, 
                update_progress=update_progress, 
                stop_requested=is_stop_requested, 
                single_process=self.single_process, 
                batch_id=self.batch_id
            )
            
            self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))
            
    def stop(self):
        self.stop_requested = True  
        
class MedianAlgorithm:
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5", max_workers=None):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        # Pastikan folder HDF5 ada
        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

        # Buat executor sekali saja untuk reuse di setiap pemrosesan
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
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

    def load_images_from_hdf5(self, hdf5_path, stop_requested=None):
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                if stop_requested and stop_requested():
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images

    def stack_median_images(self, images, stop_requested=None, block_size=1024, overlap=0.2,
                            update_progress=None, total_overall_images=None, images_processed_so_far=0,
                            use_multi_core=True):
        """
        Menghitung stack gambar dengan metode Median berbasis blok.
        Mendukung kontrol penggunaan multi-core.
        """
        if stop_requested and stop_requested():
             return None

        if not images:
            raise ValueError(language_config.NO_IMAGES_PROCESSED)

        if not isinstance(images[0], np.ndarray):
             raise TypeError(language_config.IMAGE_DATA_MUST_BE_VALID)

        dtype = images[0].dtype
        target_shape = images[0].shape
        num_images_in_this_call = len(images)

        adapted_update_progress = None
        if update_progress:
            overall_progress_cap = 98 # Persentase maksimal sebelum finalisasi
            progress_start_percent = 0
            progress_range_for_this_call = overall_progress_cap

            if total_overall_images is not None and total_overall_images > 0:
                 progress_start_percent = (images_processed_so_far / total_overall_images) * 100
                 theoretical_end_percent = ((images_processed_so_far + num_images_in_this_call) / total_overall_images) * 100
                 progress_end_percent_for_this_call = min(theoretical_end_percent, overall_progress_cap)
                 progress_range_for_this_call = max(0, progress_end_percent_for_this_call - progress_start_percent)

            def map_progress(internal_percent, internal_message="process"):
                 overall_progress = int(progress_start_percent + (internal_percent / 100.0) * progress_range_for_this_call)
                 update_progress(overall_progress, f"{internal_message}")
            adapted_update_progress = map_progress
        # --------------------------------

        target_images = images

        stacked_image = self._compute_median_image( 
            target_images,
            target_shape,
            block_size,
            dtype,
            overlap,
            update_progress=adapted_update_progress,
            stop_requested=stop_requested,
            use_multi_core=use_multi_core
            # Parameter sigma_low, sigma_high, max_iterations dihapus dari pemanggilan
        )

        if stacked_image is None: # Jika proses dibatalkan atau gagal
             return None

        if adapted_update_progress:
            # Panggil progress 100% dengan pesan selesai dari language_config
            adapted_update_progress(100, language_config.ANALYZING_COMPLETE)

        return stacked_image

    def _compute_block_median(self, block_stack):
        """
        Menghitung stack blok menggunakan Median.

        Args:
            block_stack (np.ndarray): Tumpukan blok gambar (N, H, W, [C]).

        Returns:
            np.ndarray: Blok gambar hasil median (H, W, [C]), dtype float32.
        """
        num_blocks = block_stack.shape[0]
        
        if num_blocks == 0:
            return np.zeros(block_stack.shape[1:], dtype=np.float32)
        
        median_block = np.median(block_stack, axis=0)

        return median_block.astype(np.float32)

    def _compute_median_image(self, images, target_shape, block_size, dtype, overlap,
                          update_progress=None, stop_requested=None,
                          use_multi_core=True):
        """
        Menghitung gambar stack menggunakan metode blok dengan Median.
        (Versi yang dirampingkan tanpa duplikasi kode).
        """
        H, W = target_shape[:2]
        num_channels = target_shape[2] if len(target_shape) == 3 else 0

        accumulator = np.zeros(target_shape, dtype=np.float32)
        weight_sum = np.zeros((H, W), dtype=np.float32)
        step = max(int(block_size * (1 - overlap)), 1)

        # --- PERUBAHAN 1: Logika perhitungan tile/blok yang sedikit lebih ringkas ---
        def get_starts(dim_size):
            starts = list(range(0, dim_size, step))
            if not starts or (starts[-1] + block_size) < dim_size:
                starts.append(max(0, dim_size - block_size))
            return sorted(list(set(starts))) 

        row_starts = get_starts(H)
        col_starts = get_starts(W)

        tasks = [(r, c) for r in row_starts for c in col_starts]
        total_blocks = len(tasks)
        if total_blocks == 0:
            return np.zeros(target_shape, dtype=dtype)

        base_hanning = np.outer(np.hanning(block_size), np.hanning(block_size))

        # Fungsi process_block (nested function) tetap sama
        def process_block(row_start, col_start):
            # ... (TIDAK ADA PERUBAHAN DI SINI, LOGIKA INI SUDAH BENAR) ...
            row_end, col_end = min(row_start + block_size, H), min(col_start + block_size, W)
            actual_h, actual_w = row_end - row_start, col_end - col_start
            if actual_h <= 0 or actual_w <= 0: return None
            
            if num_channels > 0:
                block_stack = np.stack([im[row_start:row_end, col_start:col_end, :] for im in images])
            else:
                block_stack = np.stack([im[row_start:row_end, col_start:col_end] for im in images])
                
            block_result = self._compute_block_median(block_stack)
            
            h_win = base_hanning if (actual_h, actual_w) == (block_size, block_size) \
                else np.outer(np.hanning(actual_h), np.hanning(actual_w))
                
            weighted_block = block_result * (h_win[..., np.newaxis] if num_channels > 0 else h_win)
            
            return row_start, row_end, col_start, col_end, weighted_block, h_win

        # --- PERUBAHAN 2 (UTAMA): Menyatukan loop multi-core dan single-core ---
        results_iterator = None
        executor = None

        if use_multi_core:
            executor = concurrent.futures.ThreadPoolExecutor()
            future_to_task = {executor.submit(process_block, r, c): (r, c) for r, c in tasks}
            results_iterator = concurrent.futures.as_completed(future_to_task)
        else:
            # Buat iterator sederhana yang langsung memanggil fungsi
            results_iterator = (process_block(r, c) for r, c in tasks)

        blocks_processed_count = 0
        internal_progress_cap = 98

        # Sekarang kita hanya punya SATU loop pemrosesan yang bersih
        for item in results_iterator:
            if stop_requested and stop_requested():
                if executor: executor.shutdown(wait=False, cancel_futures=True)
                return None

            try:
                # Dapatkan hasil, baik dari future (multi-core) atau langsung (single-core)
                result = item.result() if use_multi_core else item
                
                if result is None: continue

                row_s, row_e, col_s, col_e, weighted_block, h_win_2d = result

                # Logika akumulasi dan progress (sekarang berada di satu tempat)
                accumulator[row_s:row_e, col_s:col_e] += weighted_block
                weight_sum[row_s:row_e, col_s:col_e] += h_win_2d
                blocks_processed_count += 1

                if update_progress:
                    progress_percent = int((blocks_processed_count / total_blocks) * internal_progress_cap)
                    update_progress(progress_percent)

            except (concurrent.futures.CancelledError, Exception):
                traceback.print_exc()
                pass
                
        if executor: executor.shutdown() # Pastikan executor ditutup dengan baik

        # --- Bagian Finalisasi (TIDAK BERUBAH) ---
        if stop_requested and stop_requested(): return None
        if update_progress: update_progress(internal_progress_cap, language_config.FINISHING_ANALYSIS)
        
        final_weight_sum = weight_sum[..., np.newaxis] if num_channels > 0 else weight_sum
        mask = final_weight_sum > 1e-10
        stacked_image_float = np.zeros_like(accumulator)
        np.divide(accumulator, final_weight_sum, out=stacked_image_float, where=mask)
        
        if np.issubdtype(dtype, np.integer):
            min_val, max_val = np.iinfo(dtype).min, np.iinfo(dtype).max
            stacked_image_float = np.nan_to_num(stacked_image_float, nan=0.0, posinf=max_val, neginf=min_val)
            final_image = np.clip(stacked_image_float, min_val, max_val).astype(dtype)
        else:
            final_image = np.nan_to_num(stacked_image_float, nan=0.0).astype(dtype)

        return final_image
    
def main(db_path, update_progress=None, stop_requested=None, batch_size=8,
         single_process=None, batch_id=None, progress_bar=None):
    try:
        if update_progress: update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        image_processor = MedianAlgorithm(db_path)
        align_dir = os.path.join("database", "align")
        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)

        data_source = None
        output_path = ""
        total_images = 0
        image_paths = [] # Inisialisasi di sini

        # Tentukan sumber data (HDF5 atau list path) dan path output
        if single_process:
            hdf5_path = os.path.join(align_dir, "aligned_images.h5")
            image_paths = get_all_image_paths_for_single_process(db_path)
            ref_name = os.path.splitext(os.path.basename(image_paths[0]))[0] if image_paths else "single_process"
            data_source = hdf5_path if os.path.exists(hdf5_path) else image_paths
        else: # Batch process
            if batch_id is None: raise ValueError(language_config.BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS)
            hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
            image_paths = image_processor.get_all_image_paths_for_batch_process(batch_id)
            ref_name = os.path.splitext(os.path.basename(image_paths[0]))[0] if image_paths else f"batch_{batch_id}"
            data_source = hdf5_path if os.path.exists(hdf5_path) else image_paths

        # Buat nama output yang aman
        output_name_safe = "".join(c for c in ref_name if c.isalnum() or c in ('_', '-')).rstrip() or "stack_result"
        output_path = os.path.join(output_folder_stack, f"{output_name_safe}_median.tif")
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))
        
        # Dapatkan total gambar untuk progress bar
        if isinstance(data_source, str) and data_source.endswith('.h5'):
            with h5py.File(data_source, 'r') as f: total_images = len(f.keys())
        elif isinstance(data_source, list):
            total_images = len(data_source)

        if not total_images:
            if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return

        # --- PERUBAHAN UTAMA 1: Menggunakan setup_balanced_batching ---
        batch_plan = setup_balanced_batching(total_images, language_config)
        
        if not batch_plan:
            if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return
            
        total_batches = len(batch_plan)
        print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))
        print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))
        
        processed_batches_results = []
        images_processed_count = 0
        
        # --- PERUBAHAN UTAMA 2: Mengganti loop generator dengan loop berbasis rencana (plan) ---
        for batch_num, (batch_start, batch_end) in enumerate(batch_plan, 1):
            if stop_requested and stop_requested():
                print(language_config.PROCESS_TERMINATED_BY_USER)
                break
                
            print(f"\n{language_config.PROCESSING_BATCH.format(batch_num, total_batches, batch_start)}")

            # Pemuatan data manual di dalam loop, berdasarkan rencana
            batch_images = []
            if isinstance(data_source, str) and data_source.endswith('.h5'):
                with h5py.File(data_source, 'r') as h5f:
                    keys = list(h5f.keys())[batch_start:batch_end]
                    batch_images = [np.array(h5f[key]) for key in keys]
            else: # Sumbernya adalah list path
                batch_paths = data_source[batch_start:batch_end]
                batch_images = load_images_from_paths(batch_paths, stop_requested)
                # Terapkan pra-pemrosesan jika perlu
                if 'resize_all_with_padding' in globals():
                    batch_images, _ = resize_all_with_padding(batch_images, method="median")

            if stop_requested and stop_requested(): break
            if not batch_images:
                print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(batch_num))
                continue
            
            print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images)))
            
            batch_result = image_processor.stack_median_images(
                batch_images,
                update_progress=update_progress,
                stop_requested=stop_requested,
                total_overall_images=total_images,
                images_processed_so_far=images_processed_count
            )

            if batch_result is not None:
                processed_batches_results.append(batch_result)
                images_processed_count += len(batch_images)
            else:
                print("Batch processing failed or returned None.")

        if stop_requested and stop_requested():
            if update_progress and progress_bar: update_progress(progress_bar.value(), "Proses dibatalkan.")
            return

        # --- 3. Proses Finalisasi (Fine-Tuning) ---
        if not processed_batches_results:
            if update_progress: update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED)
            return

        print(f"\n--- {language_config.STARTING_ENHANCEMENT} ({len(processed_batches_results)} batch results) ---")
        
        # --- KODE YANG DIPERBAIKI ADA DI SINI ---
        fine_tuning_start_progress = 95
        fine_tuning_end_progress = 99

        def fine_tuning_update_progress(inner_progress, message):
            """Callback untuk memetakan progress 0-100 dari stacking final ke rentang 95-99%."""
            mapped_progress = fine_tuning_start_progress + int((inner_progress / 100.0) * (fine_tuning_end_progress - fine_tuning_start_progress))
            if update_progress:
                if not (stop_requested and stop_requested()):
                    update_progress(mapped_progress, language_config.ENHANCEMENT.format(message))

        # Update progress awal untuk fase fine-tuning
        if update_progress: update_progress(fine_tuning_start_progress, language_config.STARTING_ENHANCEMENT)

        # Panggil stack_median_images dengan callback progress yang sudah disesuaikan
        final_result = image_processor.stack_median_images(
            processed_batches_results,
            update_progress=fine_tuning_update_progress,
            stop_requested=stop_requested,
        )
        # --- AKHIR DARI KODE YANG DIPERBAIKI ---

        # --- 4. Simpan Hasil dan Cleanup ---
        if stop_requested and stop_requested():
            # Jika proses dibatalkan selama fine-tuning, jangan simpan dan keluar dengan baik
            if update_progress and progress_bar: update_progress(progress_bar.value(), "Proses dibatalkan.")
            return

        if final_result is not None:
            ref_path_for_save = image_paths[0] if image_paths else None
            save_success = save_image(final_result, output_path, reference_image_path=ref_path_for_save)
            
            final_message = f"{language_config.IMAGE_PROCESS_FINISHED}: {os.path.basename(output_path)}" if save_success \
                else f"{language_config.FAILED_TO_SAVE_IMAGE}: {os.path.basename(output_path)}"
            
            if update_progress: update_progress(100, final_message)
            
            # Cleanup
            if not single_process and batch_id is not None:
                batch_hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
                if os.path.exists(batch_hdf5_path):
                    try: os.remove(batch_hdf5_path)
                    except OSError as e: print(f"Error removing temp file: {e}")
        else:
            if update_progress: update_progress(100, language_config.FAILED_IMAGE_ENHANCEMENT)

    # --- 5. Penanganan Error (Tetap sama, karena sudah bagus) ---
    except Exception as e: 
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)
   
def running_median(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_MEDIAN)
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
    progress_bar.setStyleSheet(PROGRESS_BAR)
    layout.addWidget(progress_bar)

    # Inisialisasi thread worker
    worker = ThreadWorker("pixel_refine_database.db", single_process=single_process, batch_id=batch_id)
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