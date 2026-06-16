import traceback
import cv2
import gc
from pixel_refine_desktop.enhance_stack.core.algorithm.base_worker import (
    BaseAlgorithmWorker,
)
import numpy as np
import sqlite3
import os
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PySide6.QtCore import QThread, Signal, Qt
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    extract_all_metadata,
    get_all_image_paths_for_single_process,
    load_images_from_paths,
    resize_all_with_padding,
    resize_with_padding,
    save_image,
    setup_balanced_batching,
    cleanup_old_hdf5_files,
)
from resources.styles.stylesheet import PROGRESS_BAR
from pixel_refine_desktop.ui.views.settings.General.Language import language_config


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
            cursor.execute(
                """
                SELECT images.path
                FROM batch_process_image
                JOIN images ON batch_process_image.image_id_batch = images.id
                WHERE batch_process_image.batch_id = ?
                ORDER BY batch_process_image.is_reference_batch DESC, images.path ASC
            """,
                (batch_id,),
            )
            return [row[0] for row in cursor.fetchall()]

    def load_images_from_hdf5(self, hdf5_path, stop_requested=None):
        images = []
        with h5py.File(hdf5_path, "r") as h5f:
            for key in h5f.keys():
                if stop_requested and stop_requested():
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images

    def average_stack(
        self,
        images,
        update_progress=None,
        stop_requested=None,
        total_overall_images=None,
        images_processed_so_far=0,
    ):
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
                    progress = int(
                        (current_overall_image_index / total_overall_images)
                        * progress_cap_percent
                    )
                    message = language_config.IMAGE_PROCESS_IN_PROGRESS.format(
                        current_overall_image_index, total_overall_images
                    )
                else:
                    progress = int(
                        ((i + 1) / num_images_in_list) * progress_cap_percent
                    )
                    message = language_config.ANALYZING_IMAGE.format(
                        i + 1, num_images_in_list
                    )
                update_progress(progress, message)

            # --- PERUBAHAN 2: Validasi per gambar digabung menjadi satu ---
            is_valid = (
                isinstance(current_image, np.ndarray)
                and current_image.shape == ref_image.shape
                and current_image.dtype == ref_image.dtype
            )
            if not is_valid:
                continue

            # Akumulasi (tidak berubah)
            sum_image += current_image.astype(np.float32)
            num_images_averaged += 1

        if num_images_averaged == 0:
            # --- PERUBAHAN 3: Return untuk kasus gagal lebih ringkas ---
            return np.zeros_like(ref_image)  # Mengembalikan tipe data asli

        # Finalisasi (tidak berubah, sudah optimal)
        average_image_float = sum_image / num_images_averaged

        # Mendapatkan nilai max yang aman (tidak berubah)
        max_val = np.iinfo(ref_image.dtype).max

        final_image = np.clip(average_image_float, 0, max_val).astype(ref_image.dtype)

        # --- PERUBAHAN 4: Menghapus blok pass yang tidak perlu ---
        return final_image


def main(
    db_path,
    update_progress=None,
    stop_requested=None,
    single_process=None,
    batch_id=None,
    progress_bar=None,
):
    try:
        if update_progress:
            update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        image_processor = AverageAlgorithm(db_path)
        align_dir = os.path.join("database", "align")
        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)

        data_source = None
        output_path = ""
        total_images = 0
        image_paths = []

        if single_process:
            hdf5_path = os.path.join(align_dir, "aligned_images.h5")
            image_paths = get_all_image_paths_for_single_process(db_path)
            ref_name = (
                os.path.splitext(os.path.basename(image_paths[0]))[0]
                if image_paths
                else "single_process"
            )
            data_source = hdf5_path if os.path.exists(hdf5_path) else image_paths
        else:
            if batch_id is None:
                raise ValueError(
                    language_config.BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS
                )
            hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
            image_paths = image_processor.get_all_image_paths_for_batch_process(
                batch_id
            )
            ref_name = (
                os.path.splitext(os.path.basename(image_paths[0]))[0]
                if image_paths
                else f"batch_{batch_id}"
            )
            data_source = hdf5_path if os.path.exists(hdf5_path) else image_paths

        # Hapus file HDF5 lama selain file target saat ini untuk menghemat ruang HDD
        cleanup_old_hdf5_files(hdf5_path)


        metadata_output_path = os.path.join("database", "align", "metadata.json")
        try:
            extract_all_metadata(image_paths, metadata_file=metadata_output_path)
        except Exception as e:
            pass

        output_name_safe = (
            "".join(c for c in ref_name if c.isalnum() or c in ("_", "-")).rstrip()
            or "stack_result"
        )
        output_path = os.path.join(
            output_folder_stack, f"{output_name_safe}_average.tif"
        )
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))

        if isinstance(data_source, str) and data_source.endswith(".h5"):
            with h5py.File(data_source, "r") as f:
                total_images = len(f.keys())
        elif isinstance(data_source, list):
            total_images = len(data_source)

        if not total_images:
            if update_progress:
                update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return

        batch_plan = setup_balanced_batching(total_images, language_config)

        if not batch_plan:
            if update_progress:
                update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return

        total_batches = len(batch_plan)
        # print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))

        sum_accumulator = None
        total_count_processed = 0

        # Penanda ukuran target dan bit-depth untuk konsistensi data
        target_shape = None
        reference_dtype = None

        for batch_num, (batch_start, batch_end) in enumerate(batch_plan, 1):
            if stop_requested and stop_requested():
                print(language_config.PROCESS_TERMINATED_BY_USER)
                break

            print(
                f"\n{language_config.PROCESSING_BATCH.format(batch_num, total_batches, batch_start)}"
            )

            batch_images = []
            if isinstance(data_source, str) and data_source.endswith(".h5"):
                with h5py.File(data_source, "r") as h5f:
                    keys = list(h5f.keys())[batch_start:batch_end]
                    batch_images = [np.array(h5f[key]) for key in keys]
            else:  # Sumbernya adalah list path
                batch_paths = data_source[batch_start:batch_end]
                # Gunakan load_images_from_paths karena lebih tangguh untuk berbagai format
                batch_images = load_images_from_paths(batch_paths, stop_requested)

            # Setup awal dari gambar pertama (referensi)
            if batch_images and target_shape is None:
                first_img = batch_images[0]
                target_shape = (first_img.shape[1], first_img.shape[0])  # (w, h)
                reference_dtype = first_img.dtype
                print(
                    f"  -> Reference detect: {target_shape[0]}x{target_shape[1]}, Depth: {reference_dtype}"
                )

            if stop_requested and stop_requested():
                break
            if not batch_images:
                print(
                    language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(
                        batch_num
                    )
                )
                continue

            # --- PROSES AKUMULASI KUMULATIF SATU-TAHAP ---
            num_in_batch = len(batch_images)
            gc_threshold = max(1, int(num_in_batch * 0.7))

            for i in range(num_in_batch):
                if stop_requested and stop_requested():
                    break

                current_img = batch_images[i]
                if current_img is None:
                    continue

                # Validasi dimensi dan resize jika perlu
                if (current_img.shape[1], current_img.shape[0]) != target_shape:
                    current_img = resize_with_padding(current_img, target_shape)

                # Inisialisasi accumulator hny sekali
                if sum_accumulator is None:
                    sum_accumulator = current_img.astype(np.float32)
                else:
                    # Akumulasi langsung ke float32 (Single Stage)
                    sum_accumulator += current_img.astype(np.float32)

                total_count_processed += 1

                # Update progress UI
                if update_progress:
                    progress_val = int((total_count_processed / total_images) * 98)
                    msg = language_config.IMAGE_PROCESS_IN_PROGRESS.format(
                        total_count_processed, total_images
                    )
                    update_progress(progress_val, msg)

                # --- STRATEGI GC ELEGAN (Refill Memory) ---
                # Hapus referensi gambar dari list segera setelah variabel accumulator memegangnya
                batch_images[i] = None

                # GC setiap 70% proses batch atau di akhir batch
                if (i + 1) >= gc_threshold or (i + 1) == num_in_batch:
                    gc.collect()

            # Cleanup total untuk batch ini
            del batch_images
            gc.collect()

        if stop_requested and stop_requested():
            if update_progress and progress_bar:
                update_progress(progress_bar.value(), "Proses dibatalkan.")
            return

        if sum_accumulator is None or total_count_processed == 0:
            if update_progress:
                update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED)
            return

        # --- FINALISASI RATA-RATA & PRESERVASI BIT-DEPTH ---
        if update_progress:
            update_progress(99, "Finalisasi...")

        average_image_float = sum_accumulator / total_count_processed

        # Gunakan bit-depth asli dari referensi untuk clipping yang akurat
        if reference_dtype is None:
            # Fallback jika gagal deteksi di awal
            reference_dtype = np.uint8

        max_val = np.iinfo(reference_dtype).max
        final_result = np.clip(average_image_float, 0, max_val).astype(reference_dtype)

        # Bebaskan memori accumulator
        del sum_accumulator
        gc.collect()

        if final_result is not None:
            ref_path_for_save = image_paths[0] if image_paths else None
            save_success = save_image(
                final_result, output_path, reference_image_path=ref_path_for_save
            )

            final_message = (
                f"{language_config.IMAGE_PROCESS_FINISHED}: {os.path.basename(output_path)}"
                if save_success
                else f"{language_config.FAILED_TO_SAVE_IMAGE}: {os.path.basename(output_path)}"
            )

            if update_progress:
                update_progress(100, final_message)

            # Cleanup temp files jika ada
            if not single_process and batch_id is not None:
                align_dir = os.path.join("database", "align")
                batch_hdf5_path = os.path.join(
                    align_dir, f"aligned_image_batch_{batch_id}.h5"
                )
                if os.path.exists(batch_hdf5_path):
                    try:
                        os.remove(batch_hdf5_path)
                    except OSError as e:
                        print(f"Error removing temp file: {e}")
        else:
            if update_progress:
                update_progress(100, language_config.FAILED_IMAGE_ENHANCEMENT)

    # --- 5. Penanganan Error (Tetap sama, karena sudah bagus) ---
    except Exception as e:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)


def running_average(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
):
    # ==========================================================
    # KONDISI 1: MODE BATCH (TANPA GUI)
    # ==========================================================
    if batch_id is not None and progress_callback is not None:
        try:
            main(
                db_path="pixel_refine_database.db",
                update_progress=progress_callback,
                stop_requested=stop_callback,
                single_process=False,
                batch_id=batch_id,
            )
        except Exception as e:
            raise e
        return

    # ==========================================================
    # KONDISI 2: MODE SINGLE (DENGAN GUI DIALOG)
    # ==========================================================
    process_finished = False
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_AVERAGE)
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.CustomizeWindowHint
        | Qt.WindowType.WindowTitleHint
        | Qt.WindowType.WindowCloseButtonHint
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
    worker = BaseAlgorithmWorker(
        main,
        "pixel_refine_database.db",
        single_process=single_process,
        batch_id=batch_id,
    )
    # Menghubungkan signal worker ke fungsi pembaruan UI
    worker.progress_updated.connect(
        lambda progress, message: (
            progress_bar.setValue(progress),
            label.setText(message),
        )
    )

    def finish_handler():
        nonlocal process_finished
        process_finished = True  # set flag ketika proses selesai
        dialog.close()
        worker.quit()  # Berhenti dari thread
        worker.wait()  # Tunggu thread selesai

    worker.finished.connect(finish_handler)

    def error_handler(error):
        QMessageBox.critical(
            dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=error)
        )
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    def on_dialog_close(event):
        # Jika proses telah selesai, lewati konfirmasi
        if process_finished:
            event.accept()
        elif worker.isRunning():
            reply = QMessageBox.question(
                dialog,
                "Cancel Process",
                language_config.CANCEL_PROCESSING,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
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
