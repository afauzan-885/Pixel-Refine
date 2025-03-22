import os
import sqlite3
from PyQt6.QtWidgets import (QLabel, QSpacerItem, QSizePolicy, QWidget, QVBoxLayout, QScrollArea,
                             QHBoxLayout, QPushButton, QComboBox, QCheckBox, QLineEdit,
                             QMessageBox, QFileDialog)
import weakref
from PyQt6.QtCore import (pyqtSignal, Qt, QSize)
from PyQt6.QtGui import QIcon
from UI.enhance_stack.components.batch_page_layout.batch_layout import refresh_ui, setup_main_panel
from UI.enhance_stack.components.batch_page_layout.combined_panel import CombinedPanel
from UI.enhance_stack.components.batch_page_layout.image_batch_management import BatchDeleteProcess, handle_add_image_to_batch
from UI.enhance_stack.components.batch_page_layout.thumbnail import ThumbnailLoader, create_thumbnail_placeholder, stop_all_thumbnails, update_thumbnail
from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.enhance_stack.logic.multi_threading import BatchImageImportThreading
from UI.resources.stylesheet.stylesheet import SCROLL_AREA
from UI.settings.General.Language import language_config
from config import CACHE, CACHE_DIR

os.makedirs(CACHE_DIR, exist_ok=True)

class BatchPageLayout(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.thumbnail_threads = []
        self.thumbnail_placeholders = weakref.WeakValueDictionary()
        self.database_manager = DatabaseManager("pixel_refine_database.db")
        self.database_manager.create_database()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)

        # Gunakan instance layout yang akan diisi oleh setup_main_panel
        self.main_panel_layout = QVBoxLayout()
        self.main_panel = setup_main_panel(self.main_panel_layout, SCROLL_AREA)

        self.data_changed.connect(self.refresh_ui)

        self.refresh_ui()
        self.layout.addWidget(self.main_panel)

    def stop_thumbnail(self):
        """Menghentikan semua thread thumbnail yang sedang berjalan."""
        stop_all_thumbnails(self.thumbnail_threads)

    def refresh_ui(self):
        """Memperbarui tampilan UI dengan daftar batch yang tersedia."""
        refresh_ui(self.database_manager, self.main_panel_layout, self.setup_combined_panel)
    
    def setup_combined_panel(self, batch_id=None):
        """Menggunakan kelas CombinedPanel untuk membuat panel gabungan."""
        return CombinedPanel(
            self.database_manager,
            batch_id,
            self,
            self.thumbnail_threads,
            self.thumbnail_placeholders
        )
    
    # Contoh penggunaan di handle_delete_batch
    def handle_delete_batch(self, batch_id):
        title, message = language_config.BATCH_DELETE_LABEL 
        message = message.format(batch_id)

        reply = QMessageBox.question(
            self,
            title,  # Judul dialog
            message,  # Isi pesan
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.deleter_thread = BatchDeleteProcess(self.database_manager, batch_id, CACHE_DIR, self.thumbnail_threads)
            self.deleter_thread.batch_deleted.connect(self.data_changed.emit)
            self.deleter_thread.start()  # Akan memanggil run() -> individual_batch_delete()

    def handle_delete_all_batches(self):
        title = language_config.TITLE_BATCH_ALL_DELETE_BUTTON

        # Mengecek jumlah batch unik dalam batch_process_image
        conn = sqlite3.connect("pixel_refine_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT batch_id) FROM batch_process_image")
        batch_count = cursor.fetchone()[0]
        conn.close()

        if batch_count == 0:
            QMessageBox.information(self, title, language_config.NO_DATA_BATCH_ALL_DELETE_BUTTON, QMessageBox.StandardButton.Ok)
            return  # Keluar dari fungsi jika tidak ada batch

        # Jika ada batch, lanjutkan dengan konfirmasi penghapusan
        message = language_config.CONFIRM_BATCH_ALL_DELETE_BUTTON.format(batch_count)
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            deleter = BatchDeleteProcess(self.database_manager, None, CACHE_DIR, self.thumbnail_threads)
            deleter.batch_deleted.connect(self.data_changed.emit)
            deleter.delete_all_batch()  # Jalankan fungsi penghapusan batch


    def handle_batch_import_button(self):
        """Function to manage images import"""
        # Open file dialog and get image paths with filter
        file_dialog_filter = language_config.HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION
        image_paths, _ = QFileDialog.getOpenFileNames(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH, "", file_dialog_filter)
        
        if not image_paths:
            return

        # Extract file extensions from the filter string
        filter_extensions = [ext.strip().lower() for ext in file_dialog_filter.split("*") if ext.strip().startswith(".")]

        # Step 1: Validate duplicate files
        existing_paths = self.database_manager.get_all_image_paths()
        duplicates = [path for path in image_paths if path in existing_paths]
        unique_files = [path for path in image_paths if path not in duplicates]

        if duplicates:
            message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE.format(count=len(duplicates))
            QMessageBox.warning(self,
                                language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE,
                                message)

        # Step 2: Group files by format based on selected file extensions
        format_groups = {ext: [] for ext in filter_extensions}

        for path in unique_files:
            for ext in filter_extensions:
                if path.lower().endswith(ext):
                    format_groups[ext].append(path)
                    break

        # Step 3: Determine dominant format
        dominant_format = max(format_groups, key=lambda ext: len(format_groups[ext]))

        # Step 4: Select files based on priority or dominant format
        selected_files = []
        if len(format_groups[dominant_format]) > len(unique_files) / 2:
            # If dominant format is more than half, prioritize it
            selected_files = format_groups[dominant_format]
        else:
            # Otherwise, follow the original priority order based on filter
            for ext in filter_extensions:
                if format_groups[ext]:
                    selected_files = format_groups[ext]
                    break

        # Step 5: Proceed with selected files
        if selected_files:
            # Inform user about the selected format and number of files to import
            message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DOMINANT.format(
            
            count=len(selected_files),
            format=dominant_format)
            
            QMessageBox.information(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_SELECTED, message)
            
            # Proceed with importing the selected files
            self.multi_thread_import_images = BatchImageImportThreading(
                self.database_manager,
                selected_files,
                batch_size=15,
                delay_ms=25
            )
            
            # Misalnya, jika thread memiliki sinyal completion, sambungkan ke slot untuk refresh UI
            self.multi_thread_import_images.completion_signal.connect(lambda: self.data_changed.emit())
            self.multi_thread_import_images.start()

            # Connect signals to update progress and completion
            # self.multi_thread_import_images.progress_signal.connect(self.update_progress_bar)
            # self.multi_thread_import_images.completion_signal.connect(self.on_import_complete)

            # Start the thread
            self.multi_thread_import_images.start()
        else:
            title, message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED
            QMessageBox.information(self, title, message)
