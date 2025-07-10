import traceback
import cv2
import numpy as np
import sqlite3
import os
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PySide6.QtCore import QThread, Signal, Qt

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import extract_all_metadata, save_image
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
        
class InterpolationAlgorithm:
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

    def load_images_from_hdf5(self, hdf5_path, stop_requested=None):
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                if stop_requested and stop_requested():  # Cek apakah harus berhenti
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images

    def load_images_from_folder(self, folder_path):
        image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        return self.load_images_from_paths(image_paths)

    def load_images_from_paths(self, image_paths, stop_requested=None):
        """
        Loads images from a list of image paths.
        """
        images = []
        for image_path in image_paths:
            if stop_requested and stop_requested():  # Cek apakah harus berhenti
                break
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if image is not None:
                images.append(image)
        return images
    
    def average_stack(self, images, update_progress=None, stop_requested=None,
                             total_overall_images=None, images_processed_so_far=0):
        """
        Melakukan stacking gambar dengan metode rata-rata sederhana (simple average).

        Args:
            images (list): List berisi NumPy array gambar yang akan di-stack.
            update_progress (callable, optional): Callback untuk update progress bar.
                                                  Dipanggil dengan (persentase, pesan).
            stop_requested (callable, optional): Callback untuk mengecek apakah proses
                                                 harus dihentikan. Harus return True jika berhenti.
            total_overall_images (int, optional): Jumlah total gambar dalam keseluruhan proses
                                                 (untuk kalkulasi progress yang lebih akurat).
            images_processed_so_far (int, optional): Jumlah gambar yang sudah diproses
                                                     sebelum batch ini (untuk progress).

        Returns:
            np.ndarray: Gambar hasil stacking (rata-rata), atau array nol jika tidak ada gambar valid.
        """
        if not isinstance(images, list) or not images:
            return None # Atau raise error, tergantung penanganan yang diinginkan

        # Validasi gambar pertama dan dapatkan propertinya
        try:
            ref_image = images[0]
            if not isinstance(ref_image, np.ndarray):
                raise TypeError(language_config.IMAGE_DATA_MUST_BE_VALID)

            h, w = ref_image.shape[:2]
            dtype = ref_image.dtype
            num_channels = ref_image.shape[2] if ref_image.ndim == 3 else 0 # 0 untuk grayscale

            if dtype not in (np.uint8, np.uint16):
                raise TypeError(language_config.IMAGE_BIT_REQUIRED)

        except (AttributeError, IndexError, ValueError, TypeError) as e:
            raise ValueError(language_config.FIRST_IMAGE_CANNOT_BE_OBTAINED.format(e))

        # --- Inisialisasi Accumulator ---
        if num_channels > 0:
            sum_image = np.zeros((h, w, num_channels), dtype=np.float32)
        else:
            sum_image = np.zeros((h, w), dtype=np.float32)

        num_images_averaged = 0
        num_images_in_list = len(images)
        progress_cap_percent = 95

        for i, current_image in enumerate(images):
            if stop_requested and stop_requested():
                break

            if update_progress:
                current_overall_image_index = images_processed_so_far + i + 1
                if total_overall_images is not None and total_overall_images > 0:
                    progress = int((current_overall_image_index / total_overall_images) * progress_cap_percent)
                    message = language_config.IMAGE_PROCESS_IN_PROGRESS.format(current_overall_image_index, total_overall_images) \
    
                else:
                    progress = int(((i + 1) / num_images_in_list) * progress_cap_percent) # Cap internal
                    message = language_config.ANALYZING_IMAGE.format(i+1, num_images_in_list)
                update_progress(progress, message)

            if not isinstance(current_image, np.ndarray):
                continue
            if current_image.shape[:2] != (h, w):
                continue
        
            if current_image.dtype != dtype:
                continue
        
            current_num_channels = current_image.shape[2] if current_image.ndim == 3 else 0
            if current_num_channels != num_channels:
                 continue

            # --- AKUMULASI ---
            sum_image += current_image.astype(np.float32)
            num_images_averaged += 1

        if num_images_averaged > 0:
            average_image_float = sum_image / num_images_averaged

            min_val = 0
            try:
                max_val = np.iinfo(dtype).max
            except ValueError:
                 max_val = 1.0 if np.issubdtype(dtype, np.floating) else 255 # Default fallback

            final_image = np.clip(average_image_float, min_val, max_val).astype(dtype)

            if stop_requested and stop_requested() and num_images_averaged < num_images_in_list:
                 pass
            return final_image
        else:
            output_shape = (h, w, num_channels) if num_channels > 0 else (h, w)
            return np.zeros(output_shape, dtype=dtype)

def main(db_path, update_progress=None, stop_requested=None, batch_size=10,
         single_process=None, batch_id=None, progress_bar=None):
    try:
        image_processor = InterpolationAlgorithm(db_path)

        output_name_base = ""
        image_paths = []
        align_dir = os.path.join("database", "align") # Definisikan path folder alignment

        if single_process:
            image_paths = get_all_image_paths_for_single_process(db_path)
            if image_paths:
                 if image_paths[0] and isinstance(image_paths[0], str):
                      ref_image_name = os.path.splitext(os.path.basename(image_paths[0]))[0]
                      output_name_base = f"{ref_image_name}"
                 else:
                      output_name_base = "single_process_invalid_path"
            else:
                 output_name_base = "single_process_no_images"
        else:
            if batch_id is None:
                raise ValueError(language_config.BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS)
            else:
                pass

            # Lanjutkan dengan mendapatkan path gambar untuk batch
            image_paths = image_processor.get_all_image_paths_for_batch_process(batch_id)
            if image_paths and isinstance(image_paths[0], str):
                ref_image_name = os.path.splitext(os.path.basename(image_paths[0]))[0]
                output_name_base = f"{ref_image_name}"
            else:
                output_name_base = "batch_no_reference"

           
        if not image_paths:
            print(language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return # Keluar jika tidak ada gambar

        # --- Setup Path Output ---
        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)
        output_name_base_safe = "".join(c for c in output_name_base if c.isalnum() or c in ('_', '-')).rstrip()
        if not output_name_base_safe: output_name_base_safe = "stack_result"
        output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_average.tif")
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))
        
        # --- Ekstraksi Metadata ---
        metadata_folder = align_dir 
        os.makedirs(metadata_folder, exist_ok=True) 
        metadata_file = os.path.join(metadata_folder, "metadata.json")

        # Panggil ekstraksi metadata hanya jika ada path gambar
        if image_paths:
             if 'extract_all_metadata' in globals():
                  try:
                       extract_all_metadata(image_paths, metadata_file=metadata_file)
                      
                  except Exception as e_meta:
                       traceback.print_exc()
                      
             else:
                  pass
        else:
            pass

        # --- Update progress awal ---
        if update_progress: update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        if single_process:
            global_hdf5_path = os.path.join(align_dir, "aligned_images.h5")
        else:
            global_hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
        processed_batches_results = []
        images_processed_count = 0
        total_images = 0

        # --- Logika Pemrosesan Utama (Batching dari HDF5 atau Path) ---
        use_hdf5 = os.path.exists(global_hdf5_path)

        if use_hdf5:
            print(language_config.PROCESSING_IMAGE_FROM_HDF5.format(global_hdf5_path))
            try:
                # Dapatkan total gambar dari HDF5 untuk progress
                with h5py.File(global_hdf5_path, 'r') as h5f_check:
                    total_images = len(h5f_check.keys())
                print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))

                if total_images == 0:
                    if update_progress: update_progress(100, "File HDF5 is empty.")
                    return

                total_batches = (total_images + batch_size - 1) // batch_size
                print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))

                with h5py.File(global_hdf5_path, 'r') as h5f:
                    keys = list(h5f.keys()) # Ambil keys sekali saja
                    for batch_start in range(0, total_images, batch_size):
                        current_batch_num = (batch_start // batch_size) + 1
                        print(f"\n" + language_config.PROCESSING_BATCH.format(current_batch_num, total_batches, batch_start))

                        if stop_requested and stop_requested():
                            print(language_config.PROCESS_TERMINATED_BY_USER)
                            break 
                        
                        batch_keys = keys[batch_start:min(batch_start + batch_size, total_images)]
                        print(language_config.LOAD_IMAGE_FROM_HDF5.format(len(batch_keys)))
                        batch_images = []
                        keys_loaded_in_batch = 0
                        for key in batch_keys:
                            if stop_requested and stop_requested(): break
                            try:
                                batch_images.append(np.array(h5f[key]))
                                keys_loaded_in_batch += 1
                            except Exception as e:
                                print(language_config.ERROR_WHILE_RETRIEVING_KEY_FROM_HD5F.format(key, e))
                        if stop_requested and stop_requested(): break # Cek lagi setelah loop key

                        if not batch_images:
                            print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num))
                            continue 
                        
                        print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images)))
                        try:
                             batch_result = image_processor.average_stack(
                                 batch_images,
                                 update_progress=update_progress,
                                 stop_requested=stop_requested,
                                 total_overall_images=total_images,
                                 images_processed_so_far=images_processed_count
                                
                             )
                        except Exception as e_sim_batch:
                             traceback.print_exc()
                             batch_result = None 
                             
                        if stop_requested and stop_requested():
                            break

                        if batch_result is not None:
                             processed_batches_results.append(batch_result)
                             images_processed_count += len(batch_images)                             
                        else:
                            print(f"Batch {current_batch_num} processing failed or returned None.")
                         
            except Exception as e:
                print(language_config.ERROR_IN_READING_FILE_HDF5.format(e))
                traceback.print_exc()
                if update_progress: update_progress(0, language_config.ERROR_IN_READING_FILE_HDF5.format(e))
                return 

        else: 
            print(language_config.NO_HDF5_FILE_PROCESSING_FROM_PATH)
            total_images = len(image_paths)
            print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))

            if total_images == 0:
                print(language_config.NO_IMAGE_PATH_PROCESSED_IMAGE) # Redundan, sudah dicek di atas, tapi aman
                if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
                return

            total_batches = (total_images + batch_size - 1) // batch_size
            print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))

            for batch_start in range(0, total_images, batch_size):
                current_batch_num = (batch_start // batch_size) + 1
                print(f"\n" + language_config.PROCESSING_BATCH.format(current_batch_num, total_batches, batch_start))

                if stop_requested and stop_requested():
                    print(language_config.PROCESS_TERMINATED_BY_USER)
                    break

                batch_paths = image_paths[batch_start:min(batch_start + batch_size, total_images)]
                batch_images = image_processor.load_images_from_paths(batch_paths, stop_requested)
                if stop_requested and stop_requested(): break # Cek setelah loading

                if not batch_images:
                    print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num))
                    continue

                print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images)))
                try:
                    batch_result = image_processor.average_stack(
                        batch_images,
                        update_progress=update_progress,
                        stop_requested=stop_requested,
                        total_overall_images=total_images,
                        images_processed_so_far=images_processed_count
                    )
                except Exception as e_sim_batch:
                      traceback.print_exc()
                      batch_result = None

                if stop_requested and stop_requested():
                    break

                if batch_result is not None:
                    processed_batches_results.append(batch_result)
                    images_processed_count += len(batch_images)
                else:
                    print(f"Batch {current_batch_num} processing failed or returned None.")


        # --- Fine-Tuning / Pemrosesan Akhir (jika ada hasil batch) ---
        if stop_requested and stop_requested():
            pass
        elif processed_batches_results:
            num_fine_tuning_inputs = len(processed_batches_results)
            print(f"\n--- {language_config.STARTING_ENHANCEMENT} ({num_fine_tuning_inputs} batch results) ---")

            fine_tuning_start_progress = 95
            fine_tuning_end_progress = 99

            def fine_tuning_update_progress(inner_progress, message):
                mapped_progress = fine_tuning_start_progress + int((inner_progress / 100.0) * (fine_tuning_end_progress - fine_tuning_start_progress))
                if update_progress:
                    if not (stop_requested and stop_requested()):
                        update_progress(mapped_progress, language_config.ENHANCEMENT.format(message))

            if update_progress: update_progress(fine_tuning_start_progress, language_config.STARTING_ENHANCEMENT)

            final_result = None
            try:
                 final_result = image_processor.average_stack(
                     processed_batches_results,
                     update_progress=fine_tuning_update_progress,
                     stop_requested=stop_requested,
                 )
            except Exception as e_fine_tune:
                  traceback.print_exc()
                  final_result = None 

            if stop_requested and stop_requested():
                pass
            
            elif final_result is not None:
                 ref_path_for_save = image_paths[0] if image_paths and isinstance(image_paths[0], str) else None
                 save_success = save_image(final_result, output_path, reference_image_path=ref_path_for_save)
                 if save_success:
                    final_message = f"{language_config.IMAGE_PROCESS_FINISHED}: {os.path.basename(output_path)}"
                    print(final_message)
                    if update_progress: update_progress(100, final_message)
                    if not single_process and batch_id is not None:
                        batch_hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
                        if os.path.exists(batch_hdf5_path):
                            try:
                                os.remove(batch_hdf5_path)
                            except Exception as e:
                                pass
                        else:
                            pass
                 else:
                      error_msg = language_config.FAILED_TO_SAVE_IMAGE + f": {os.path.basename(output_path)}"
                      print(error_msg)
                      if update_progress: update_progress(100, error_msg) # Tetap 100% tapi pesan error
            else:
                print(language_config.FAILED_IMAGE_ENHANCEMENT)
                if update_progress: update_progress(100, language_config.FAILED_IMAGE_ENHANCEMENT) # 100% tapi pesan gagal

        elif not (stop_requested and stop_requested()): # Jika tidak ada hasil batch DAN tidak dibatalkan
            print(language_config.DATA_FAILED_COMPLETION_CREATED)
            if update_progress:
                update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED)

        if stop_requested and stop_requested():
             if update_progress and progress_bar: update_progress(progress_bar.value(), "Proses dibatalkan.") # Update progress terakhir


    except ValueError as ve:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(ve))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
             update_progress(0, error_message)
    except FileNotFoundError as fnf:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(fnf))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
             update_progress(0, error_message)
    except RuntimeError as rte:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(rte))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)
    except Exception as e: 
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)
    finally:
       pass

def running_interpolation(parent=None, single_process=None, batch_id=None):
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_INTERPOLATION)
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
        dialog.close()
        worker.quit()
        worker.wait()

    worker.finished.connect(finish_handler)

    def error_handler(error):
        
        # messages: An error occurred
        QMessageBox.critical(dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=error))
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    # Mulai worker
    worker.start()

    # Pastikan worker dihentikan jika dialog ditutup
    def on_dialog_close(event):
        if worker.isRunning():
            # Menampilkan konfirmasi sebelum menutup dialog
            reply = QMessageBox.question(dialog, "Cancel Process",
                                        
                                        # message: Are you sure you want to cancel the process?
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

    dialog.closeEvent = on_dialog_close

    dialog.exec()

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"  # Path ke database Anda
    main(db_path)
