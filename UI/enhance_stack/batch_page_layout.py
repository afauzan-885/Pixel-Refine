import os
import shutil
import sqlite3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QMessageBox, QFileDialog,
                              QApplication)
import weakref
from PyQt6.QtCore import (pyqtSignal)
from PIL import Image
from UI.enhance_stack.components.batch_page_layout.batch_layout import refresh_ui, setup_main_panel
from UI.enhance_stack.components.batch_page_layout.combined_panel import CombinedPanel
from UI.enhance_stack.components.batch_page_layout.image_batch_management import BatchDeleteProcess
from UI.enhance_stack.components.batch_page_layout.thumbnail import stop_all_thumbnails
from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.enhance_stack.logic.multi_threading import BatchImageImportThreading
from UI.resources.stylesheet.stylesheet import SCROLL_AREA
from UI.settings.General.Language import language_config
from config import  CACHE_DIR

os.makedirs(CACHE_DIR, exist_ok=True)

class BatchPageLayout(QWidget):
    data_changed = pyqtSignal()
    show_toast_requested = pyqtSignal(str, object, bool)

    def __init__(self):
        super().__init__()
        self.thumbnail_threads = []
        self.thumbnail_placeholders = weakref.WeakValueDictionary()
        self.database_manager = DatabaseManager("pixel_refine_database.db")
        self.database_manager.create_database()
        
        self.active_batch_panels = weakref.WeakValueDictionary()
        self.batch_states = {}
        
        self.combined_panel = CombinedPanel(self.database_manager)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)

        # Gunakan instance layout yang akan diisi oleh setup_main_panel
        self.main_panel_container = QVBoxLayout()
        self.main_panel = setup_main_panel(self.main_panel_container, SCROLL_AREA)

        self.data_changed.connect(self.refresh_ui)
        
        self.refresh_ui()
        self.layout.addWidget(self.main_panel)
        

    def stop_thumbnail(self):
        """Menghentikan semua thread thumbnail yang sedang berjalan."""
        stop_all_thumbnails(self.thumbnail_threads)

    def refresh_ui(self):
        """Memperbarui tampilan UI dengan daftar batch yang tersedia."""

        current_batch_ids_in_ui = list(self.active_batch_panels.keys())
        for batch_id in current_batch_ids_in_ui:
            panel = self.active_batch_panels.get(batch_id)
            if panel: # Pastikan panel masih ada
                try:
                    self.batch_states[batch_id] = panel.get_current_state()
                    # print(f"Saved state for batch {batch_id}: {self.batch_states[batch_id]}") # Debug
                except Exception as e:
                    print(f"Error getting state from panel for batch {batch_id}: {e}")
        # -----------------------------------------------------------

        # Sekarang panggil fungsi refresh asli (atau implementasi di sini)
        refresh_ui(
            self.database_manager,
            self.main_panel_container,
            self.setup_combined_panel # Fungsi callback untuk membuat panel baru
        )
    
    def setup_combined_panel(self, batch_id=None):
        """Membuat dan menyimpan panel gabungan untuk batch tertentu."""

        # --- LANGKAH 4: Ambil state tersimpan ---
        initial_state = self.batch_states.get(batch_id, {}) # Default ke dict kosong
        # print(f"Creating panel for batch {batch_id} with initial state: {initial_state}") # Debug
        # --------------------------------------

        combined_panel = CombinedPanel(
            self.database_manager,
            batch_id,
            self,
            self.thumbnail_threads,
            self.thumbnail_placeholders,
            initial_state=initial_state # <-- Teruskan state awal
        )
        # Simpan referensi panel yang baru dibuat
        self.active_batch_panels[batch_id] = combined_panel
        return combined_panel

    def process_all_batches(self):
        """Menjalankan semua batch dan MEMINTA toast ditampilkan."""
        if not self.active_batch_panels:
            self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_NO_PROCESS, 3000, False)
            return

        target_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not target_folder:
            return

        active_panels = list(self.active_batch_panels.values())
        total_batches = len(active_panels)

        if total_batches == 0:
             self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_NO_PROCESS, 3000, False)
             return

        # Tampilkan toast AWAL
        self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_PROCESS.format(total_batches), None, False)
        QApplication.processEvents() # Import QApplication jika perlu

        # Mulai proses batch
        print(f"Starting processing for {total_batches} batches...")
        for i, batch_panel in enumerate(active_panels, start=1):
            if batch_panel:
                 print(f"Processing batch {batch_panel.batch_id} ({i}/{total_batches})...")
                 try:
                    batch_panel.process_all_batch()
                    # UPDATE toast progress
                    self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_PROGRESS.format(i, total_batches), None, True) # is_progress=True
                    QApplication.processEvents()
                 except Exception as e:
                    print(f"Error processing batch {batch_panel.batch_id}: {e}")
                    QMessageBox.warning(self, "Processing Error", f"An error occurred while processing batch {batch_panel.batch_id}:\n{e}")
            else:
                 print(f"Skipping invalid panel reference at index {i-1}")

        # Setelah SEMUA batch selesai, simpan gambar
        print("All batch processing finished. Saving images...")
        self.save_image(target_folder) # save_image juga bisa emit sinyal toast jika perlu

        # Notifikasi selesai
        self.show_toast_requested.emit(language_config.UI_LABEL_BATCH_SUCCES, 5000, False)

    def save_image(self, target_folder):
        """Memindahkan gambar dan MEMINTA toast ditampilkan."""
        folder_path = "database/stack"

        if not os.path.exists(folder_path):
            # Panggil QMessageBox atau emit sinyal toast error
            self.show_toast_requested.emit(language_config.UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH, 4000, False)
            return

        try:
            image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        except Exception as e:
             self.show_toast_requested.emit(f"Error accessing stack folder: {e}", 4000, False)
             return

        if not image_files:
            self.show_toast_requested.emit(language_config.UI_NO_IMAGE_TO_SAVE_IMAGE_BATCH, 4000, False)
            return

        # Tampilkan toast sebelum memindahkan
        self.show_toast_requested.emit(language_config.UI_LABEL_MOVING_FILES.format(len(image_files), target_folder), None, True) # Progress
        QApplication.processEvents()

        move_errors = []
        for image_file_name in image_files:
             source_path = os.path.join(folder_path, image_file_name)
             destination_path = os.path.join(target_folder, image_file_name)
             try:
                 shutil.move(source_path, destination_path)
             except Exception as e:
                 error_msg = f"Failed to move '{image_file_name}': {e}"
                 print(error_msg)
                 move_errors.append(error_msg)

        # Tampilkan hasil akhir (toast success sudah ditampilkan oleh process_all_batches)
        if move_errors:
             error_details = "\n".join(move_errors)
             QMessageBox.critical(self, "Move Error", f"Some files could not be moved:\n{error_details}")


    # Contoh penggunaan di handle_delete_individual_batch
    def handle_delete_individual_batch(self, batch_id):
        title, message = language_config.BATCH_DELETE_LABEL
        message = message.format(batch_id)

        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # --- LANGKAH 6: Hapus state sebelum memulai delete ---
            if batch_id in self.batch_states:
                del self.batch_states[batch_id]
                # print(f"Removed saved state for batch {batch_id}") # Debug
            
            # Jalankan penghapusan di thread terpisah
            self.deleter_thread = BatchDeleteProcess(self.database_manager, batch_id, CACHE_DIR, self.thumbnail_threads)
            # Hubungkan sinyal SEBELUM memulai thread
            self.deleter_thread.batch_deleted.connect(self.data_changed.emit)
            self.deleter_thread.start()

    def handle_delete_all_batches(self):
        title = language_config.TITLE_BATCH_ALL_DELETE_BUTTON
        conn = None # Inisialisasi
        batch_defined_count = 0
        
        try:
            db_path = self.database_manager.db_path # Asumsi database_manager punya atribut db_path
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;") 
            cursor.execute("SELECT COUNT(*) FROM batch_process") 
            batch_defined_count = cursor.fetchone()[0]
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to check batch status: {e}")
            return 
        finally:
            if conn:
                conn.close()

        if batch_defined_count == 0:
            QMessageBox.information(self, title, language_config.NO_DATA_BATCH_ALL_DELETE_BUTTON, QMessageBox.StandardButton.Ok)
            return 

        message = language_config.CONFIRM_BATCH_ALL_DELETE_BUTTON.format(batch_defined_count)
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.batch_states.clear()
            
            deleter = BatchDeleteProcess(self.database_manager, None, CACHE_DIR, self.thumbnail_threads)
            deleter.batch_deleted.connect(self.data_changed.emit)
            deleter.delete_all_batch() 

    def convert_tiff_to_uncompressed(self, input_path, output_folder):
        """Konversi TIFF terkompresi ke TIFF tanpa kompresi"""
        try:
            with Image.open(input_path) as img:
                output_path = os.path.join(output_folder, os.path.basename(input_path))
                img.save(output_path, format="TIFF", compression="none")  # Simpan tanpa kompresi
                return output_path
        except Exception as e:
            print(f"Error converting TIFF: {e}")
            return None

    def handle_batch_import_button(self):
        """Function to manage batch image import with TIFF decompression"""
        file_dialog_filter = language_config.HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION
        image_paths, _ = QFileDialog.getOpenFileNames(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH, "", file_dialog_filter)

        if not image_paths:
            return

        # Mapping ekstensi alternatif ke dalam tiga kategori utama
        SUPPORTED_FORMATS = {
            "jpg": [".jpg", ".jpeg", ".jiff", ".jli"],
            "tiff": [".tif", ".tiff"],
            "png": [".png"],
        }
        
        # 1. Dapatkan semua nama batch yang ada
        existing_batch_names = self.database_manager.get_all_batch_names()

        # 2. Tentukan nomor batch berikutnya
        next_batch_num = 1
        prefix = "batch" 
        
        max_num_found = 0
        for name in existing_batch_names:
            if name.startswith(prefix):
                try:
                    num_part = name[len(prefix):]
                    if num_part.isdigit(): 
                        num = int(num_part)
                        if num > max_num_found:
                            max_num_found = num
                except ValueError:
                    continue
        
        # Nomor berikutnya adalah nomor maksimum yang ditemukan + 1
        next_batch_num = max_num_found + 1

        # 3. Buat nama batch baru
        target_batch_name = f"{prefix}{next_batch_num}"
        target_batch_id = self.database_manager.create_new_batch(target_batch_name)
        if target_batch_id is None:
            QMessageBox.critical(self, "Error", f"Could not create or find batch '{target_batch_name}'.")
            return

        # Step 1: Validate duplicate files
        existing_batch_paths = self.database_manager.get_batch_process_image_paths(batch_id=target_batch_id)
        duplicates = [path for path in image_paths if path in existing_batch_paths]
        unique_files = [path for path in image_paths if path not in duplicates]

        if duplicates:
            message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE.format(count=len(duplicates))
            QMessageBox.warning(self,
                                language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE,
                                message)

        # Step 2: Group files berdasarkan format utama yang didukung
        format_groups = {key: [] for key in SUPPORTED_FORMATS.keys()}

        for path in unique_files:
            lower_path = path.lower()
            for format_key, extensions in SUPPORTED_FORMATS.items():
                if any(lower_path.endswith(ext) for ext in extensions):
                    format_groups[format_key].append(path)
                    break

        # Jika tidak ada file valid sesuai ketiga kategori, tampilkan pesan garis besar
        if not any(format_groups.values()):
            title, message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED
            QMessageBox.information(self, title, message)
            return

        # Step 3: Konversi TIFF dengan kompresi ke uncompressed
        output_folder = "database/align/uncompressed_tiff"  # Folder penyimpanan hasil konversi
        os.makedirs(output_folder, exist_ok=True)

        uncompressed_tiff_files = []
        if "tiff" in format_groups:
            for tiff_path in format_groups["tiff"]:
                try:
                    with Image.open(tiff_path) as img:
                        compression = img.info.get("compression", "None")
                        if compression.lower() in ["tiff_lzw", "tiff_zip", "packbits"]:
                            new_tiff_path = self.convert_tiff_to_uncompressed(tiff_path, output_folder)
                            if new_tiff_path:
                                uncompressed_tiff_files.append(new_tiff_path)
                        else:
                            uncompressed_tiff_files.append(tiff_path)
                except Exception as e:
                    print(f"Skipping invalid TIFF: {tiff_path}, Error: {e}")

            # Update daftar TIFF dengan versi uncompressed
            format_groups["tiff"] = uncompressed_tiff_files

        # Step 4: Tentukan format dominan (format dengan jumlah file terbanyak)
        dominant_format = max(format_groups, key=lambda key: len(format_groups[key]))

        # Step 5: Seleksi file berdasarkan prioritas atau dominan format
        selected_files = []
        total_unique = sum(len(v) for v in format_groups.values())
        if len(format_groups[dominant_format]) > total_unique / 2:
            selected_files = format_groups[dominant_format]
        else:
            for key in SUPPORTED_FORMATS.keys():
                if format_groups[key]:
                    selected_files = format_groups[key]
                    break

        # Step 6: Proses file terpilih
        if selected_files:
            message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT.format(
                count=len(selected_files),
                format=dominant_format)
            
            QMessageBox.information(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_SELECTED, message)
            
            # Proses import file
            self.multi_thread_import_images = BatchImageImportThreading(
                self.database_manager,
                selected_files,
                batch_id=target_batch_id,
                batch_size=15,
                delay_ms=25
            )

            # Misalnya, jika thread memiliki sinyal completion, sambungkan ke slot untuk refresh UI
            self.multi_thread_import_images.completion_signal.connect(lambda: self.data_changed.emit())
            self.multi_thread_import_images.start()
        else:
            title, message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED
            QMessageBox.information(self, title, message)