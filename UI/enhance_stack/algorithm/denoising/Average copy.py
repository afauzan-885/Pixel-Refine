
import traceback
import cv2
import numpy as np
import sqlite3
import os
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PySide6.QtCore import QThread, Signal, Qt
from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import batch_image_generator, extract_all_metadata, get_all_image_paths_for_single_process, load_images_from_paths, resize_all_with_padding, save_image
from UI.resources.stylesheet.stylesheet import PROGRESS_BAR
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
            print(f"Error terjadi: {str(e)}")  # Menampilkan pesan error di konsol
            self.error_occurred.emit(str(e))  # Mengirim pesan error melalui sinyal

    def stop(self):
        self.stop_requested = True  

class AverageAlgorithm:
    def __init__(self, db_path, hdf5_path=None):
        self.db_path = db_path
        if hdf5_path is None:
            self.hdf5_path = "database/align/aligned_images.h5"
        else:
            self.hdf5_path = hdf5_path
            
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

    def load_images_from_hdf5(self, hdf5_path, stop_requested=None):
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                if stop_requested and stop_requested():
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images

    def average_stack(self, images, update_progress=None, stop_requested=None,
                      total_overall_images=None, images_processed_so_far=0):
        """
        Melakukan stacking gambar dengan metode rata-rata sederhana (simple average).
        (Docstring lainnya tetap sama)
        """
        # 1. Guard clause (tidak berubah, sudah optimal)
        if not isinstance(images, list) or not images:
            return None

        # 2. Validasi gambar referensi (tidak berubah, sudah robust)
        try:
            ref_image = images[0]
            if not isinstance(ref_image, np.ndarray):
                raise TypeError(language_config.IMAGE_DATA_MUST_BE_VALID)
            if ref_image.dtype not in (np.uint8, np.uint16):
                raise TypeError(language_config.IMAGE_BIT_REQUIRED)
        except (AttributeError, IndexError, ValueError, TypeError) as e:
            raise ValueError(language_config.FIRST_IMAGE_CANNOT_BE_OBTAINED.format(e))

        # --- PERUBAHAN 1: Inisialisasi Accumulator lebih ringkas ---
        sum_image = np.zeros_like(ref_image, dtype=np.float32)

        num_images_averaged = 0
        num_images_in_list = len(images)

        for i, current_image in enumerate(images):
            if stop_requested and stop_requested():
                break

            # Logika Progress Bar (tidak berubah, karena spesifik untuk UI)
            if update_progress:
                progress_cap_percent = 95
                if total_overall_images is not None and total_overall_images > 0:
                    current_overall_image_index = images_processed_so_far + i + 1
                    progress = int((current_overall_image_index / total_overall_images) * progress_cap_percent)
                    message = language_config.IMAGE_PROCESS_IN_PROGRESS.format(current_overall_image_index, total_overall_images)
                else:
                    progress = int(((i + 1) / num_images_in_list) * progress_cap_percent)
                    message = language_config.ANALYZING_IMAGE.format(i+1, num_images_in_list)
                update_progress(progress, message)

            # --- PERUBAHAN 2: Validasi per gambar digabung menjadi satu ---
            is_valid = (
                isinstance(current_image, np.ndarray) and
                current_image.shape == ref_image.shape and
                current_image.dtype == ref_image.dtype
            )
            if not is_valid:
                continue

            # Akumulasi (tidak berubah)
            sum_image += current_image.astype(np.float32)
            num_images_averaged += 1

        if num_images_averaged == 0:
            # --- PERUBAHAN 3: Return untuk kasus gagal lebih ringkas ---
            return np.zeros_like(ref_image) # Mengembalikan tipe data asli

        # Finalisasi (tidak berubah, sudah optimal)
        average_image_float = sum_image / num_images_averaged
        
        # Mendapatkan nilai max yang aman (tidak berubah)
        max_val = np.iinfo(ref_image.dtype).max
        
        final_image = np.clip(average_image_float, 0, max_val).astype(ref_image.dtype)

        # --- PERUBAHAN 4: Menghapus blok pass yang tidak perlu ---
        return final_image

def main(db_path, update_progress=None, stop_requested=None, batch_size=10,
         single_process=None, batch_id=None, progress_bar=None):
    try:
        # --- 1. Setup & Konfigurasi (Bagian ini tetap diperlukan) ---
        if update_progress: update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        image_processor = AverageAlgorithm(db_path)
        align_dir = os.path.join("database", "align")
        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)

        data_source = None
        output_path = ""
        total_images = 0

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
        output_path = os.path.join(output_folder_stack, f"{output_name_safe}_average.tif")
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))
        
        # Dapatkan total gambar untuk progress bar
        if isinstance(data_source, str) and data_source.endswith('.h5'):
            with h5py.File(data_source, 'r') as f: total_images = len(f.keys())
        elif isinstance(data_source, list):
            total_images = len(data_source)

        if not total_images:
            if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return

        # --- 2. Proses Batch Utama (Menggunakan generator baru kita) ---
        print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))
        processed_batches_results = []
        images_processed_count = 0
        
        batch_generator = batch_image_generator(data_source, batch_size, stop_requested)

        for batch_images in batch_generator:
            if not batch_images or (stop_requested and stop_requested()):
                break
            
            print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images)))
            
            batch_result = image_processor.average_stack(
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

        # Panggil average_stack dengan callback progress yang sudah disesuaikan
        final_result = image_processor.average_stack(
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

def running_average(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_AVERAGE)
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