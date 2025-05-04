import os
import weakref
from PyQt6.QtWidgets import (QMessageBox, QFileDialog)
from PIL import Image, UnidentifiedImageError
from PyQt6.QtCore import QThread, pyqtSignal
from UI.enhance_stack.components.batch_page_layout.thumbnail import ThumbnailLoader, update_thumbnail
from UI.enhance_stack.logic.multi_threading import BatchImageImportThreading
from UI.settings.General.Language import language_config
from config import SUPPORTED_FORMATS

class BatchDeleteProcess(QThread):
    batch_deleted = pyqtSignal()

    def __init__(self, database_manager, batch_id, cache_dir, thumbnail_threads, parent=None):
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
        for path in image_paths:
            cache_path = os.path.join(self.cache_dir, os.path.basename(path) + ".jpg")
            if os.path.exists(cache_path):
                os.remove(cache_path)

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

        # Ambil semua batch ID dan kumpulkan semua image path dari seluruh batch
        batch_ids = self.database_manager.get_all_batch_ids()
        all_image_paths = []
        for batch_id in batch_ids:
            image_paths = self.database_manager.get_images_by_batch(batch_id)
            all_image_paths.extend(image_paths)
        # Hapus duplikat jika ada
        all_image_paths = list(set(all_image_paths))

        # Hapus cache gambar dari disk
        for path in all_image_paths:
            cache_path = os.path.join(self.cache_dir, os.path.basename(path) + ".jpg")
            if os.path.exists(cache_path):
                os.remove(cache_path)

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


def handle_add_image_to_batch(batch_page_layout, database_manager, thumbnail_threads, batch_id, list_layout):
    if batch_id is None:
        print("Batch ID tidak valid.")
        return

    existing_image_paths = database_manager.get_images_by_batch(batch_id)

    file_dialog = QFileDialog()
    file_paths, _ = file_dialog.getOpenFileNames(
        None,
        language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH,
        "",
        language_config.HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION
    )

    if not file_paths:
        return  

    existing_set = set(existing_image_paths)
    unique_files = [path for path in file_paths if path not in existing_set]
    duplicates = list(existing_set.intersection(file_paths))

    if duplicates:
        message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE.format(count=len(duplicates))
        QMessageBox.warning(None, language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE, message)

    if unique_files:
        database_manager.batch_process_save_image_path(batch_id, unique_files)

        ref_layout = weakref.ref(list_layout)

        for path in unique_files:
            loader = ThumbnailLoader(path)
            loader.thumbnail_ready.connect(
                lambda pixmap, p=path, ref_layout=ref_layout: update_thumbnail(ref_layout, pixmap, p) if ref_layout() else None
            )
            loader.start()
            thumbnail_threads.append(loader)  # Simpan referensi agar tidak dihapus GC

        print(f"Added {len(unique_files)} new images to batch {batch_id}")

        # Emit sinyal data_changed dari BatchPageLayout
        batch_page_layout.data_changed.emit()

# --- Fungsi Baru yang Dipindahkan ---
def process_and_start_batch_import(batch_page_layout, image_paths: list):
    """
    Memproses daftar path gambar untuk impor batch: membuat batch baru,
    validasi, konversi, seleksi, dan memulai impor background.

    Args:
        batch_page_layout: Instance dari BatchPageLayout.
        image_paths: List path gambar yang akan diimpor.
    """
    if not image_paths: return

    db_manager = batch_page_layout.database_manager # Akses via argumen

    try:
         existing_batch_names = db_manager.get_all_batch_names()
         next_batch_num = 1
         prefix = "batch"
         max_num_found = 0
         for name in existing_batch_names:
             if name.startswith(prefix):
                 try:
                     num_part = name[len(prefix):]
                     if num_part.isdigit(): num = int(num_part)
                     if num > max_num_found: max_num_found = num
                 except ValueError: continue
         next_batch_num = max_num_found + 1
         target_batch_name = f"{prefix}{next_batch_num}"
         target_batch_id = db_manager.create_new_batch(target_batch_name)
         if target_batch_id is None:
             raise Exception(f"Could not create or find batch '{target_batch_name}'.")
    except Exception as e:
        QMessageBox.critical(batch_page_layout, "Batch Error", f"Failed to prepare batch:\n{e}") # Gunakan batch_page_layout sbg parent
        return
    # ------------------------------------

    # --- Step 1: Validasi Duplikat (dalam batch BARU ini) ---
    unique_files = list(image_paths)

    # --- Step 2: Group File berdasarkan Format ---
    format_groups = {key: [] for key in SUPPORTED_FORMATS.keys()}
    valid_files_grouped = False
    for path in unique_files:
        lower_path = path.lower()
        for format_key, extensions in SUPPORTED_FORMATS.items():
            if any(lower_path.endswith(ext) for ext in extensions):
                format_groups[format_key].append(path)
                valid_files_grouped = True
                break

    if not valid_files_grouped:
        title, message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED
        QMessageBox.information(batch_page_layout, title, message) # Gunakan batch_page_layout sbg parent
        # Penting: Hapus batch kosong yang baru dibuat jika tidak ada file valid
        db_manager.batch_process_delete_batch(target_batch_id)
        return

    # --- Step 3: Konversi TIFF ---
    output_folder = "database/align/uncompressed_tiff"
    try:
        os.makedirs(output_folder, exist_ok=True)
    except OSError as e:
        QMessageBox.critical(batch_page_layout, "Folder Error", f"Could not create folder for TIFF conversion:\n{e}")
        # Hapus batch kosong jika konversi gagal di awal
        db_manager.batch_process_delete_batch(target_batch_id)
        return

    files_to_import = []
    files_to_import.extend(format_groups.get("jpg", []))
    files_to_import.extend(format_groups.get("png", []))

    tiff_files = format_groups.get("tiff", [])
    if tiff_files:
         print(f"Processing {len(tiff_files)} TIFF files for batch {target_batch_id}...")
         converted_or_original_tiffs = []
         tiff_errors = []
         for tiff_path in tiff_files:
              processed_tiff_path = tiff_path
              needs_conversion = False
              try:
                  with Image.open(tiff_path) as img:
                       compression = img.info.get("compression", "none").lower()
                       if compression in ["tiff_lzw", "tiff_zip", "packbits", "jpeg"]: needs_conversion = True
              except (FileNotFoundError, UnidentifiedImageError, Exception) as e:
                   print(f"  TIFF Error reading info/opening: {os.path.basename(tiff_path)}, Error: {e}"); tiff_errors.append(f"{os.path.basename(tiff_path)} (Read Error)"); continue

              if needs_conversion:
                   print(f"  Converting compressed TIFF: {os.path.basename(tiff_path)}")
                   # Panggil metode helper (asumsikan ada atau pindahkan juga)
                   converted = convert_tiff_to_uncompressed_static(tiff_path, output_folder) # Buat versi statis
                   if converted: processed_tiff_path = converted
                   else: print(f"  Skipping TIFF due to conversion error: {os.path.basename(tiff_path)}"); tiff_errors.append(f"{os.path.basename(tiff_path)} (Conversion Failed)"); continue
              converted_or_original_tiffs.append(processed_tiff_path)

         files_to_import.extend(converted_or_original_tiffs)
         if tiff_errors: QMessageBox.warning(batch_page_layout, "TIFF Processing Issues", f"Could not process some TIFF files:\n{', '.join(tiff_errors)}") # Gunakan batch_page_layout sbg parent
    # ---------------------------

    # --- Step 4 & 5: Seleksi File (Logika Dominan/Prioritas) ---
    selected_files = []
    if files_to_import:
        temp_format_groups = {key: [] for key in SUPPORTED_FORMATS.keys()}
        for path in files_to_import:
             lower_path = path.lower()
             for format_key, extensions in SUPPORTED_FORMATS.items():
                 if any(lower_path.endswith(ext) for ext in extensions):
                      temp_format_groups[format_key].append(path)
                      break

        if any(temp_format_groups.values()):
            dominant_format = max(temp_format_groups, key=lambda key: len(temp_format_groups[key]))
            total_to_import = len(files_to_import)
            # Terapkan logika dominan
            if len(temp_format_groups[dominant_format]) > total_to_import / 2:
                 selected_files = temp_format_groups[dominant_format]
                 print(f"Selected dominant format '{dominant_format}' with {len(selected_files)} files.")
            else:
                 for key in SUPPORTED_FORMATS.keys():
                      if temp_format_groups[key]:
                          selected_files = temp_format_groups[key]
                          print(f"Selected first available format '{key}' with {len(selected_files)} files.")
                          dominant_format = key # Update dominant format untuk pesan
                          break
        else:
             print("Warning: No valid format groups found after TIFF conversion.")
             selected_files = []
             dominant_format = "N/A"
    else:
         dominant_format = "N/A"

    # --- Step 6: Proses Impor File Terpilih ---
    if selected_files:
        num_files_this_batch = len(selected_files)

        # Update state di BatchPageLayout
        batch_page_layout._total_pending_imports += num_files_this_batch
        batch_page_layout._update_aggregated_progress_toast() 

        # Mulai impor di background thread
        try:
            import_thread = BatchImageImportThreading(
                database_manager=db_manager,
                image_paths=selected_files,
                batch_id=target_batch_id,
                batch_size=15,
                delay_ms=25
            )
            # Tambahkan thread ke list di BatchPageLayout
            batch_page_layout._active_import_threads.append(import_thread)

            # Hubungkan sinyal thread ke slot/metode di BatchPageLayout
            import_thread.result_signal.connect(batch_page_layout._handle_item_imported)
            import_thread.finished.connect(lambda t=import_thread: batch_page_layout._handle_thread_finished(t))
            if hasattr(import_thread, 'error_signal'):
                 import_thread.error_signal.connect(batch_page_layout.on_batch_import_error)

            import_thread.start()

        except Exception as e:
            print(f"Error creating/starting batch import thread: {e}")
            QMessageBox.critical(batch_page_layout, "Threading Error", f"Could not start import process:\n{e}")
            # Rollback state jika thread gagal start
            batch_page_layout._total_pending_imports -= num_files_this_batch
            if batch_page_layout._total_pending_imports < 0: batch_page_layout._total_pending_imports = 0
            batch_page_layout._update_aggregated_progress_toast()
             # Hapus batch yang gagal
            db_manager.batch_process_delete_batch(target_batch_id)

    else:
        title, message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED
        QMessageBox.information(batch_page_layout, title, message)
        db_manager.batch_process_delete_batch(target_batch_id)

# --- Helper Function (jika `convert_tiff_to_uncompressed` juga perlu dipindah) ---
def convert_tiff_to_uncompressed_static(input_path, output_folder):
    """Konversi TIFF terkompresi ke TIFF tanpa kompresi (versi statis)."""
    try:
        with Image.open(input_path) as img:
            output_filename = os.path.basename(input_path)
            output_path = os.path.join(output_folder, output_filename)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            img.save(output_path, format="TIFF", compression="none")
            print(f"  Successfully converted '{os.path.basename(input_path)}' to uncompressed TIFF at '{output_path}'")
            return output_path
    except UnidentifiedImageError:
        print(f"Error converting TIFF: Cannot identify image file '{input_path}'")
        return None
    except FileNotFoundError:
         print(f"Error converting TIFF: Input file not found '{input_path}'")
         return None
    except Exception as e:
        print(f"Error converting TIFF '{input_path}': {e}")
        return None