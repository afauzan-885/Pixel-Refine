from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import subprocess
import weakref
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PIL import Image
from PySide6.QtCore import QThread, Signal, QObject
import cv2
import numpy as np
import tifffile
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    save_image,
)
from pixel_refine_desktop.enhance_stack.components.batch_page.thumbnail import (
    ThumbnailLoader,
    make_safe_callback,
    show_thumbnail,
)
from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import (
    BatchImageImportThreading,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from config import SUPPORTED_FORMATS


class BatchDeleteProcess(QThread):
    batch_deleted = Signal()

    def __init__(
        self, database_manager, batch_id, cache_dir, thumbnail_threads, parent=None
    ):
        super().__init__(parent)
        self.database_manager = database_manager
        self.batch_id = batch_id
        self.cache_dir = cache_dir
        self.thumbnail_threads = thumbnail_threads

    def individual_batch_delete(self):
        """
        Menghapus satu batch beserta cache gambarnya.
        """
        # Jeda semua proses pembuatan thumbnail
        for thread in self.thumbnail_threads:
            thread.pause()

        # Hapus cache dari disk untuk batch tertentu
        image_paths = self.database_manager.get_images_by_batch(self.batch_id)
        if image_paths:
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = []
                for path in image_paths:
                    cache_path = os.path.join(self.cache_dir, os.path.basename(path) + ".jpg")
                    futures.append(executor.submit(os.remove, cache_path))
                for future in futures:
                    try:
                        future.result()
                    except FileNotFoundError:
                        pass
                    except Exception as e:
                        print(f"Error deleting cache file: {e}")

        # Hapus batch dari database
        self.database_manager.batch_process_delete_batch(self.batch_id)

        # Emit sinyal untuk memperbarui UI setelah penghapusan selesai
        self.batch_deleted.emit()

        # Lanjutkan kembali proses pembuatan thumbnail
        for thread in self.thumbnail_threads:
            thread.resume()

    def delete_all_batch(self):
        """
        Menghapus semua batch beserta cache gambar yang terkait.
        """
        # Jeda semua proses pembuatan thumbnail
        for thread in self.thumbnail_threads:
            thread.pause()

        # Ambil seluruh path gambar dari semua batch dalam satu query cepat
        all_image_paths = []
        try:
            with self.database_manager._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT i.path
                    FROM images i
                    JOIN batch_process_image bpi ON i.id = bpi.image_id_batch
                """)
                all_image_paths = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching all batch images for deletion: {e}")

        # Hapus cache gambar dari disk secara efisien menggunakan thread pool
        if all_image_paths:
            with ThreadPoolExecutor(max_workers=12) as executor:
                futures = []
                for path in all_image_paths:
                    cache_path = os.path.join(self.cache_dir, os.path.basename(path) + ".jpg")
                    futures.append(executor.submit(os.remove, cache_path))
                for future in futures:
                    try:
                        future.result()
                    except FileNotFoundError:
                        pass
                    except Exception as e:
                        print(f"Error deleting cache file: {e}")

        # Hapus seluruh batch beserta gambar yang terkait dari database
        self.database_manager.delete_all_batches()

        # Emit sinyal untuk memperbarui UI setelah penghapusan selesai
        self.batch_deleted.emit()

        # Lanjutkan kembali proses pembuatan thumbnail
        for thread in self.thumbnail_threads:
            thread.resume()

    def run(self):
        """
        Metode run default akan menjalankan individual_batch_delete.
        Anda dapat memanggil delete_all_batch secara eksplisit jika ingin menghapus semua batch.
        """
        self.individual_batch_delete()


def handle_add_image_to_batch(
    batch_page_layout, database_manager, thumbnail_threads, batch_id, list_layout
):
    if batch_id is None:
        print("Batch ID tidak valid.")
        return

    # Dapatkan path yang sudah ada di batch ini (untuk cek duplikat nanti)
    try:
        existing_image_paths = database_manager.get_images_by_batch(batch_id)
    except Exception as e:
        print(f"Error mendapatkan gambar yang ada untuk batch {batch_id}: {e}")
        QMessageBox.critical(
            None, "Database Error", "Could not retrieve existing images for the batch."
        )
        return

    filter_parts = []
    all_supported_extensions = []
    for ext_list in SUPPORTED_FORMATS.values():
        all_supported_extensions.extend([f"*{ext}" for ext in ext_list])
    all_filter_str = f"All Supported Images ({' '.join(sorted(list(set(all_supported_extensions))))})"
    filter_parts.append(all_filter_str)
    for format_key, extensions in SUPPORTED_FORMATS.items():
        formatted_extensions = " ".join([f"*{ext}" for ext in extensions])
        description = f"{format_key.upper()} Files"
        filter_parts.append(f"{description} ({formatted_extensions})")
    filter_parts.append("All Files (*)")
    file_dialog_filter = ";;".join(filter_parts)
    # --- AKHIR PERBAIKAN FILTER ---

    # Gunakan filter yang sudah dibuat
    file_paths, _ = QFileDialog.getOpenFileNames(
        None,  # Parent bisa None atau widget yang relevan
        language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH,  # Judul dialog
        "",  # Direktori awal
        file_dialog_filter,  # Gunakan filter dari SUPPORTED_FORMATS
    )

    if not file_paths:
        return  # Keluar jika tidak ada file dipilih

    supported_extensions_set = {
        ext.lower() for fmt_list in SUPPORTED_FORMATS.values() for ext in fmt_list
    }
    selected_supported_files = [
        path
        for path in file_paths
        if os.path.splitext(path)[1].lower() in supported_extensions_set
    ]

    # Beri tahu jika ada file dengan format tidak didukung yang dipilih & dibuang
    num_unsupported = len(file_paths) - len(selected_supported_files)
    if num_unsupported > 0:
        QMessageBox.information(
            None,
            "Format Tidak Didukung",
            f"{num_unsupported} file dipilih dengan format yang tidak didukung dan akan diabaikan.",
        )

    if not selected_supported_files:
        print("Tidak ada file dengan format yang didukung yang dipilih.")
        return  # Keluar jika tidak ada file valid tersisa

    # Cek duplikat hanya terhadap file yang formatnya didukung
    existing_set = set(existing_image_paths)
    unique_files = [
        path for path in selected_supported_files if path not in existing_set
    ]
    duplicates = list(existing_set.intersection(selected_supported_files))

    if duplicates:
        message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE.format(
            count=len(duplicates)
        )
        QMessageBox.warning(
            None, language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE, message
        )

    if unique_files:
        try:
            database_manager.batch_process_save_image_path(batch_id, unique_files)
        except Exception as e:
            print(f"Error menyimpan path baru ke batch {batch_id}: {e}")
            QMessageBox.critical(
                None, "Database Error", "Could not save new image paths to the batch."
            )
            return

        newly_added_count = 0
        layout_ref = (
            weakref.ref(list_layout) if isinstance(list_layout, QObject) else None
        )

        for path in unique_files:
            try:
                loader = ThumbnailLoader(path)
                callback = make_safe_callback(path, layout_ref)
                loader.thumbnail_ready.connect(callback)
                loader.start()
                thumbnail_threads.append(loader)
                newly_added_count += 1
            except Exception as e_thumb:
                print(f"Error memulai thumbnail loader untuk {path}: {e_thumb}")

        print(f"Added {newly_added_count} new supported images to batch {batch_id}")
        batch_page_layout.data_changed.emit()


# --- Fungsi Baru yang Dipindahkan ---
def process_and_start_batch_import(batch_page_layout, image_paths: list):
    """
    Memproses dan memulai impor batch dengan pola streaming sejati,
    memperbarui UI secara bertahap saat file siap.
    """
    if not image_paths:
        return

    db_manager = batch_page_layout.database_manager
    CHUNK_SIZE = 2
    try:
        existing_batch_names = db_manager.get_all_batch_names()
        prefix = "batch"
        max_num_found = 0
        for name in existing_batch_names:
            if name.startswith(prefix):
                try:
                    num_part = name[len(prefix) :]
                    if num_part.isdigit():
                        num = int(num_part)
                        if num > max_num_found:
                            max_num_found = num
                except ValueError:
                    continue
        next_batch_num = max_num_found + 1
        target_batch_name = f"{prefix}{next_batch_num}"
        target_batch_id = db_manager.create_new_batch(target_batch_name)
        if target_batch_id is None:
            raise Exception(f"Could not create or find batch '{target_batch_name}'.")
    except Exception as e:
        QMessageBox.critical(
            batch_page_layout, "Batch Error", f"Failed to prepare batch:\n{e}"
        )
        return

    # --- Fungsi Helper untuk Memulai Impor per Chunk ---
    def start_import_for_chunk(files_to_import_chunk):
        if not files_to_import_chunk:
            return

        num_files_this_chunk = len(files_to_import_chunk)
        print(f"Starting import thread for a chunk of {num_files_this_chunk} files...")

        # Update progress bar agregat
        batch_page_layout._total_pending_imports += num_files_this_chunk
        batch_page_layout._update_aggregated_progress_toast()

        try:
            import_thread = BatchImageImportThreading(
                database_manager=db_manager,
                image_paths=files_to_import_chunk,
                batch_id=target_batch_id,
                batch_name=target_batch_name,
                batch_size=CHUNK_SIZE,  # Gunakan CHUNK_SIZE atau nilai lain
                delay_ms=25,
            )
            batch_page_layout._active_import_threads.append(import_thread)
            import_thread.result_signal.connect(batch_page_layout._handle_item_imported)
            import_thread.finished.connect(
                lambda t=import_thread: batch_page_layout._handle_thread_finished(t)
            )
            if hasattr(import_thread, "error_signal"):
                import_thread.error_signal.connect(
                    batch_page_layout.on_batch_import_error
                )
            import_thread.start()
        except Exception as e:
            print(f"Error creating/starting batch import thread: {e}")
            QMessageBox.critical(
                batch_page_layout,
                "Threading Error",
                f"Could not start import process for a chunk:\n{e}",
            )
            # Rollback progress jika thread gagal start
            batch_page_layout._total_pending_imports -= num_files_this_chunk
            if batch_page_layout._total_pending_imports < 0:
                batch_page_layout._total_pending_imports = 0
            batch_page_layout._update_aggregated_progress_toast()
            # Tidak perlu hapus batch di sini karena mungkin chunk lain berhasil

    # --- Pengumpulan dan Pemrosesan Streaming ---
    ready_files_chunk = []
    tiff_errors = []

    # Step 1: Kumpulkan semua file yang tidak butuh konversi
    unique_files = list(set(image_paths))
    all_tiff_files = []

    for path in unique_files:
        lower_path = path.lower()
        if any(lower_path.endswith(ext) for ext in SUPPORTED_FORMATS.get("tiff", [])):
            all_tiff_files.append(path)
        elif any(
            lower_path.endswith(ext)
            for fmt in SUPPORTED_FORMATS
            if fmt != "tiff"
            for ext in SUPPORTED_FORMATS[fmt]
        ):
            ready_files_chunk.append(path)

    # Step 2: Analisis file TIFF
    tiffs_to_convert = []
    if all_tiff_files:
        print(f"Analyzing {len(all_tiff_files)} TIFF files...")
        for tiff_path in all_tiff_files:
            try:
                with Image.open(tiff_path) as img:
                    compression = img.info.get("compression", "none").lower()
                    if compression in [
                        "tiff_lzw",
                        "tiff_zip",
                        "packbits",
                        "jpeg",
                        "lzw",
                    ]:
                        tiffs_to_convert.append(tiff_path)
                    else:
                        # TIFF sudah OK, langsung tambahkan ke chunk
                        ready_files_chunk.append(tiff_path)
            except Exception as e:
                print(
                    f"  TIFF Error reading info: {os.path.basename(tiff_path)}, Error: {e}"
                )
                tiff_errors.append(f"{os.path.basename(tiff_path)} (Read Error)")

    # Step 3: Langsung proses chunk pertama yang berisi file non-TIFF dan TIFF yang sudah OK
    # Ini memberikan feedback instan kepada pengguna
    start_import_for_chunk(list(ready_files_chunk))  # Kirim salinan
    ready_files_chunk.clear()

    # Step 4: Jalankan konversi untuk TIFF yang membutuhkan dan proses hasilnya secara streaming
    total_files_processed = 0
    if tiffs_to_convert:
        output_folder = "database/align/uncompressed_tiff"
        os.makedirs(output_folder, exist_ok=True)

        conversion_generator = convert_tiff_to_uncompressed(
            tiffs_to_convert, output_folder
        )
        for success, path_or_message in conversion_generator:
            if success:
                ready_files_chunk.append(path_or_message)
                # Jika chunk sudah penuh, mulai thread impor dan kosongkan chunk
                if len(ready_files_chunk) >= CHUNK_SIZE:
                    start_import_for_chunk(list(ready_files_chunk))
                    ready_files_chunk.clear()
            else:
                tiff_errors.append(path_or_message)
            total_files_processed += 1

    # Step 5: Proses sisa file di chunk terakhir yang mungkin tidak penuh
    if ready_files_chunk:
        start_import_for_chunk(list(ready_files_chunk))
        ready_files_chunk.clear()

    # Step 6: Tampilkan semua error TIFF yang terkumpul
    if tiff_errors:
        error_message = "\n".join(tiff_errors)
        if len(tiff_errors) > 10:
            error_message = (
                "\n".join(tiff_errors[:10])
                + f"\n... dan {len(tiff_errors) - 10} lainnya."
            )
        QMessageBox.warning(
            batch_page_layout,
            "TIFF Processing Issues",
            f"Could not process some TIFF files:\n{error_message}",
        )

    # Cek jika pada akhirnya tidak ada impor yang dimulai sama sekali
    if (
        not batch_page_layout._active_import_threads
        and not batch_page_layout._total_pending_imports
    ):
        title, message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED
        QMessageBox.information(batch_page_layout, title, message)
        db_manager.batch_process_delete_batch(target_batch_id)
        print(
            "No valid files were found to import after processing. Deleting empty batch."
        )


def convert_tiff_to_uncompressed(input_paths, output_folder):
    """
    Mengonversi daftar gambar input secara paralel dan MENGHASILKAN (yield) setiap hasil
    segera setelah selesai.

    Args:
        input_paths: Sebuah list path file yang akan dikonversi.
        output_folder: Folder tujuan untuk semua file yang dikonversi.

    Yields:
        Tuple (bool, str) yang berisi status keberhasilan dan path hasil atau pesan error.
    """
    max_workers = 4

    print(
        f"Memulai konversi paralel untuk {len(input_paths)} file menggunakan {max_workers} thread (Mode Generator)..."
    )

    def _worker(input_path):
        """Fungsi worker internal, tidak ada perubahan logika di sini."""
        try:
            output_filename = os.path.basename(input_path)
            output_path = os.path.join(output_folder, output_filename)

            numpy_image_rgb = tifffile.imread(input_path)

            if len(numpy_image_rgb.shape) == 3 and numpy_image_rgb.shape[2] >= 3:
                numpy_image = cv2.cvtColor(numpy_image_rgb[:, :, :3], cv2.COLOR_RGB2BGR)
            else:
                numpy_image = numpy_image_rgb

            source_orientation = 1
            try:
                result = subprocess.run(
                    ["exiftool", "-n", "-Orientation", input_path],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                output_str = result.stdout.strip()
                if output_str:
                    source_orientation = int(output_str.split(":")[-1].strip())
            except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
                pass

            image_corrected = numpy_image.copy()
            # if source_orientation == 3: image_corrected = cv2.rotate(numpy_image, cv2.ROTATE_180)
            # elif source_orientation == 6: image_corrected = cv2.rotate(numpy_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            # elif source_orientation == 8: image_corrected = cv2.rotate(numpy_image, cv2.ROTATE_90_CLOCKWISE)

            saved_path = save_image(
                image=image_corrected,
                output_path=output_path,
                reference_image_path=input_path,
            )

            if saved_path:
                return (True, saved_path)
            else:
                return (False, f"{os.path.basename(input_path)} (Save Failed)")

        except Exception as e:
            return (False, f"{os.path.basename(input_path)} (Error: {e})")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {executor.submit(_worker, path): path for path in input_paths}

        # as_completed akan menghasilkan future segera setelah selesai, tidak menunggu semua.
        for future in as_completed(future_to_path):
            input_file = os.path.basename(future_to_path[future])
            try:
                # Ambil hasil dari future yang sudah selesai
                result = future.result()
                # Langsung kirimkan hasilnya keluar dari fungsi menggunakan 'yield'
                yield result
            except Exception as e:
                # Jika future itu sendiri gagal secara kritis, yield pesan error
                yield (False, f"{input_file} (Critical Error: {e})")

    print(f"\nSemua pekerjaan konversi telah dikirim dan diselesaikan.")
