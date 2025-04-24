import os
import shutil
import sqlite3
from PyQt6.QtWidgets import (QLabel, QWidget, QVBoxLayout, QMessageBox, QFileDialog)
import weakref
from PyQt6.QtCore import (pyqtSignal, Qt, QTimer)
from PyQt6.QtGui import QFont
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

    def __init__(self):
        super().__init__()
        self.thumbnail_threads = []
        self.thumbnail_placeholders = weakref.WeakValueDictionary()
        self.database_manager = DatabaseManager("pixel_refine_database.db")
        self.database_manager.create_database()
        
        self.active_batch_panels = weakref.WeakValueDictionary()
        self.batch_states = {} # Menyimpan state {batch_id: {param1: value1, ...}}
        
        self.combined_panel = CombinedPanel(self.database_manager)

        self.batch_panels = []
        
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

        # --- LANGKAH 3: Simpan state panel yang ada SEBELUM refresh ---
        # Iterasi melalui panel yang masih ada di WeakValueDictionary
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
    
    def show_toast(self, message, duration=None):
        """Menampilkan toast yang tetap aktif selama proses berlangsung"""
        if hasattr(self, 'toast') and self.toast:  # Hapus toast lama jika ada
            self.toast.deleteLater()

        self.toast = QLabel(message, self)
        self.toast.setStyleSheet("""
            background-color: #858686;
            color: white;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
        """)
        self.toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toast.setFont(QFont("Arial", 10))
        
        # Set lokasi di bagian bawah tengah UI
        self.toast.setGeometry(
            (self.width() - 300) // 2,  # Tengah horizontal
            self.height() - 60,  # Bawah layar
            300, 40  # Ukuran toast
        )
        
        self.toast.show()

        # Jika durasi diberikan, otomatis hilang setelah waktu selesai
        if duration:
            QTimer.singleShot(duration, self.toast.hide)
    
    def process_all_batches(self):
        """Menjalankan semua batch dengan toast yang terus diperbarui"""
        if not self.batch_panels:
            self.show_toast(language_config.UI_LABEL_BATCH_NO_PROCESS, duration=3000)
            return

        # 1. User memilih folder tujuan untuk menyimpan gambar
        target_folder = QFileDialog.getExistingDirectory(self)
        if not target_folder:
            self.show_toast(language_config.UI_LABEL_BATCH_NO_PROCESS, duration=3000)
            return

        total_batches = len(self.batch_panels)
        self.show_toast(language_config.UI_LABEL_BATCH_PROCESS.format(total_batches))

        # 2. Mulai proses batch
        for i, batch_panel in enumerate(self.batch_panels, start=1):
            batch_panel.process_all_batch()
            self.show_toast(language_config. UI_LABEL_BATCH_PROGRESS.format(i, total_batches))

        # 3. Setelah proses batch selesai, pindahkan gambar ke folder tujuan
        self.save_image(target_folder)

        # 4. Setelah semua selesai, tampilkan notifikasi
        self.show_toast(language_config.UI_LABEL_BATCH_SUCCES, duration=3000)

    def save_image(self, target_folder):
        """Memindahkan semua gambar dari 'database/stack' ke folder tujuan"""
        folder_path = "database/stack"

        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "Error", language_config.UI_SYSTEM_FOLDER_WRONG_TO_SAVE_IMAGE_BATCH)
            return

        image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        if not image_files:
            QMessageBox.warning(self, "No Images", language_config.UI_NO_IMAGE_TO_SAVE_IMAGE_BATCH)
            return

        try:
            for image_file in image_files:
                shutil.move(image_file, os.path.join(target_folder, os.path.basename(image_file)))

            QMessageBox.information(self, "Success", language_config.UI_SUCCES_TO_SAVE_IMAGE_BATCH.format(target_folder))
        except Exception as e:
            QMessageBox.critical(self, "Error", language_config.UI_FAILED_TO_SAVE_IMAGE_BATCH.format(e))


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
                print(f"Removed saved state for batch {batch_id}") # Debug
            # ----------------------------------------------------

            # Jalankan penghapusan di thread terpisah
            self.deleter_thread = BatchDeleteProcess(self.database_manager, batch_id, CACHE_DIR, self.thumbnail_threads)
            # Hubungkan sinyal SEBELUM memulai thread
            self.deleter_thread.batch_deleted.connect(self.data_changed.emit)
            self.deleter_thread.start()

    def handle_delete_all_batches(self):
        title = language_config.TITLE_BATCH_ALL_DELETE_BUTTON
        conn = None # Inisialisasi
        batch_defined_count = 0
        
        # Mengecek jumlah batch unik dalam batch_process_image
        try:
            # Gunakan path database yang konsisten (misalnya dari self.database_manager jika tersedia)
            # Jika tidak, pastikan path "pixel_refine_database.db" sudah benar
            db_path = self.database_manager.db_path # Asumsi database_manager punya atribut db_path
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Aktifkan foreign keys untuk konsistensi (meskipun tidak wajib untuk SELECT)
            cursor.execute("PRAGMA foreign_keys = ON;") 
            cursor.execute("SELECT COUNT(*) FROM batch_process") 
            batch_defined_count = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error checking batch count: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to check batch status: {e}")
            return # Keluar jika tidak bisa cek database
        finally:
            if conn:
                conn.close()

        if batch_defined_count == 0:
            QMessageBox.information(self, title, language_config.NO_DATA_BATCH_ALL_DELETE_BUTTON, QMessageBox.StandardButton.Ok)
            return  # Keluar dari fungsi jika tidak ada batch yang terdefinisi

        # Jika ada batch, lanjutkan dengan konfirmasi penghapusan
        message = language_config.CONFIRM_BATCH_ALL_DELETE_BUTTON.format(batch_defined_count)
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # --- LANGKAH 6: Hapus semua state sebelum memulai delete ---
            self.batch_states.clear()
            print("Cleared all saved batch states") # Debug

            # Gunakan instance deleter baru jika perlu atau pastikan state internalnya benar
            deleter = BatchDeleteProcess(self.database_manager, None, CACHE_DIR, self.thumbnail_threads)
             # Hubungkan sinyal SEBELUM memulai delete
            deleter.batch_deleted.connect(self.data_changed.emit)
            deleter.delete_all_batch() # Jalankan fungsi penghapusan batch


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
        # Open file dialog and get image paths with filter
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
        prefix = "batch" # Anda bisa ganti prefix jika mau, misal "Sesi"

        max_num_found = 0
        for name in existing_batch_names:
            if name.startswith(prefix):
                # Coba ekstrak nomor dari nama batch
                try:
                    num_part = name[len(prefix):] # Ambil bagian setelah prefix
                    if num_part.isdigit(): # Pastikan itu angka
                        num = int(num_part)
                        if num > max_num_found:
                            max_num_found = num
                except ValueError:
                    # Abaikan nama yang tidak sesuai format (misal "batch_lama")
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