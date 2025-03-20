import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy,
                             QSpacerItem, QPushButton, QScrollArea, QMessageBox,
                             QFileDialog, QLabel)
from PyQt6.QtGui import QIcon, QPixmap, QImageReader, QPixmapCache
from functools import partial
import weakref
from PyQt6.QtCore import (QSize, Qt, pyqtSignal, QThread, QSemaphore,
                          QTimer,)
from UI.enhance_stack.components.batch_page_layout.image_batch_management import handle_add_image_to_batch
from UI.enhance_stack.components.batch_page_layout.thumbnail import ThumbnailLoader
from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.enhance_stack.logic.multi_threading import BatchImageImportThreading
from UI.resources.stylesheet.stylesheet import SCROLL_AREA
from UI.settings.General.Language import language_config
from config import CACHE_DIR

os.makedirs(CACHE_DIR, exist_ok=True)

class BatchDeleteProcess(QThread):
    batch_deleted = pyqtSignal()

    def __init__(self, database_manager, batch_id, cache_dir, thumbnail_threads, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.batch_id = batch_id
        self.cache_dir = cache_dir
        self.thumbnail_threads = thumbnail_threads

    def run(self):
        # **Jeda semua proses pembuatan thumbnail**
        for thread in self.thumbnail_threads:
            thread.pause()

        # **Hapus cache dari disk**
        image_paths = self.database_manager.get_images_by_batch(self.batch_id)
        for path in image_paths:
            cache_path = os.path.join(self.cache_dir, os.path.basename(path) + ".jpg")
            if os.path.exists(cache_path):
                os.remove(cache_path)

        # **Hapus batch dari database**
        self.database_manager.batch_process_delete_batch(self.batch_id)

        # **Emit sinyal untuk memperbarui UI setelah penghapusan selesai**
        self.batch_deleted.emit()

        # **Lanjutkan kembali proses pembuatan thumbnail**
        for thread in self.thumbnail_threads:
            thread.resume()


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

        # Membuat panel utama
        self.main_panel = self.setup_main_panel()
        
        # Hubungkan signal dengan slot refresh_ui
        self.data_changed.connect(self.refresh_ui)
        
        self.refresh_ui()
        self.layout.addWidget(self.main_panel)
        
    def refresh_ui(self):
        while self.main_panel_layout.count():
            item = self.main_panel_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        batch_ids = self.database_manager.get_all_batch_ids()
        
        if not batch_ids:
            placeholder = QLabel("Tidak ada batch yang tersedia.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_panel_layout.addWidget(placeholder)
        else:
            for batch_id in batch_ids:
                combined_panel = self.setup_combined_panel(batch_id=batch_id)
                self.main_panel_layout.addWidget(combined_panel)

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_panel_layout.addSpacerItem(spacer)

    def setup_main_panel(self):
        """Membuat panel utama dengan layout vertikal agar UI tersusun dari atas."""
        # Buat widget utama yang akan ditempatkan dalam QScrollArea
        main_panel = QWidget(self)
        main_panel.setStyleSheet("background-color: white;")
        main_panel_layout = QVBoxLayout(main_panel)
        main_panel_layout.setContentsMargins(10, 10, 10, 10)
        main_panel_layout.setSpacing(30)  
        self.main_panel_layout = main_panel_layout

        # Bungkus main_panel dalam QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_panel)
        scroll_area.setStyleSheet(SCROLL_AREA)
        return scroll_area
        
    def thumbnail_placeholder(self, list_layout: QHBoxLayout, image_path: str):
        """Menampilkan placeholder loading sebelum thumbnail selesai diproses."""
        placeholder = QLabel("Loading...")
        placeholder.setFixedSize(80, 80)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("background-color: lightgray; border: 1px solid gray; font-size: 12px; color: gray;")
        list_layout.addWidget(placeholder)

        # Simpan referensi layout sebagai weakref agar tidak menyebabkan crash jika dihapus
        self.thumbnail_placeholders[image_path] = list_layout  
        return placeholder

    def add_thumbnail(self, ref_layout, pixmap: QPixmap, image_path: str):
        """Mengganti placeholder dengan thumbnail saat sudah tersedia."""
        list_layout = ref_layout() if callable(ref_layout) else ref_layout
        
        if list_layout is None:
            return  # Jika layout sudah dihapus, hentikan fungsi agar tidak crash

        for i in range(list_layout.count()):
            item = list_layout.itemAt(i)
            if isinstance(item.widget(), QLabel) and item.widget().text() == "Loading...":
                thumb_label = item.widget()
                break
        else:
            thumb_label = QLabel()
            list_layout.addWidget(thumb_label)

        thumb_label.setPixmap(pixmap)
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        thumb_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
        thumb_label.setFixedSize(80, 80)

        
    def stop_thumbnail(self):
        """Menghentikan semua thread ThumbnailLoader yang sedang berjalan dan membersihkan daftar thread."""
        if not hasattr(self, 'thumbnail_threads'):
            return

        for thread in self.thumbnail_threads:
            if thread.isRunning():
                thread.thumbnail_ready.disconnect()
                thread.quit()

        # Gunakan QTimer untuk menunggu thread berhenti sebelum membersihkannya
        QTimer.singleShot(100, lambda: setattr(self, 'thumbnail_threads', [t for t in self.thumbnail_threads if t.isRunning()]))

        
    def clear_batch_cache(self, batch_id):
        """
        Menghapus thumbnail yang terkait dengan batch yang dihapus.
        
        Args:
            batch_id (int): ID batch yang akan dihapus.
        """
        image_paths = self.database_manager.get_images_by_batch(batch_id)

        for path in image_paths:
            cache_path = os.path.join(CACHE_DIR, os.path.basename(path) + ".png")
            if os.path.exists(cache_path):
                os.remove(cache_path)

    def setup_combined_panel(self, batch_id=None):
        """Membuat panel gabungan yang berisi tombol tambah, tombol delete, parameter_panel, dan list_panel."""
        combined_panel = QWidget()
        combined_panel.setMaximumHeight(120)  # Berikan tinggi maksimum agar UI tetap rapi
        combined_panel_layout = QHBoxLayout(combined_panel)
        combined_panel_layout.setContentsMargins(0, 0, 0, 0)

        # Layout vertikal untuk tombol Add, Delete, dan Play Preview
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tombol "Tambah" (dengan ikon)
        add_button = QPushButton()
        add_button.setFixedSize(30, 30)
        add_button.setIcon(QIcon("UI/resources/icon/add-image.png"))
        add_button.setIconSize(QSize(25, 25))
        add_button.setStyleSheet("""
            QPushButton {
            background-color: #4CAF50; 
            border-radius: 5px; 
            color: white; 
            font-weight: semi-bold;
            }
            QPushButton:hover {
            background-color: #347A36;
            }
        """)
        add_button.setToolTip("Tambah")

        add_button.clicked.connect(lambda: handle_add_image_to_batch(batch_id, list_layout))

        
        # Tombol "Play Preview" (dengan ikon)
        play_preview = QPushButton()
        play_preview.setFixedSize(30, 30)
        play_preview.setIcon(QIcon("UI/resources/icon/play-preview.png"))
        play_preview.setStyleSheet("""
                                   
        QPushButton {
            background-color: #31CBD1;
            border-radius: 5px;
            color: white;
            font-weight: semi-bold
            }
        
        
        QPushButton:hover {
            background-color: #27A1A7;
            }
            
        """)
        play_preview.setToolTip("Pratinjau")

        delete_button = QPushButton()
        delete_button.setFixedSize(30, 30)
        delete_button.setIcon(QIcon("UI/resources/icon/delete-image.png"))
        delete_button.setStyleSheet("""
            QPushButton {
            background-color: #F44336; 
            border-radius: 5px; 
            color: white; 
            font-weight: semi-bold;
            }
            QPushButton:hover {
            background-color: #B9332A;
            }
        """)
        delete_button.setToolTip("Hapus")
        # Hubungkan tombol delete dengan slot handle_delete_batch
        delete_button.clicked.connect(lambda: self.handle_delete_batch(batch_id))

        button_layout.addWidget(add_button)
        button_layout.addWidget(play_preview)
        button_layout.addWidget(delete_button)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        # Layout horizontal untuk button_widget + parameter_panel
        left_layout = QHBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Panel Parameter (bisa berisi informasi batch atau parameter lainnya)
        parameter_panel = QWidget()
        parameter_panel.setStyleSheet("background-color: #EBEAEA")
        parameter_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        left_layout.addWidget(button_widget)
        left_layout.addWidget(parameter_panel, 1)

        # Panel kanan (Panel List gambar) yang menampilkan thumbnail gambar dari batch tertentu
        list_panel = QWidget()
        list_panel.setStyleSheet("background-color: #DBDBDB")
        list_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
         # Buat layout untuk list_panel
        list_layout = QHBoxLayout(list_panel)
        list_layout.setContentsMargins(5, 5, 5, 5)
        list_layout.setSpacing(10)
        
        # List untuk menyimpan thread agar tetap hidup
        self.thumbnail_threads = getattr(self, 'thumbnail_threads', [])
        
        if batch_id is not None:
            image_paths = self.database_manager.get_images_by_batch(batch_id)
            for path in image_paths:
                # Tambahkan placeholder dengan fungsi dari modul utilitas
                placeholder = self.thumbnail_placeholder(list_layout, path)
                
                # Buat instance worker dan hubungkan sinyalnya
                loader = ThumbnailLoader(path)
                loader.thumbnail_ready.connect(lambda pixmap, p, ref_layout=weakref.ref(list_layout): 
                    self.add_thumbnail(ref_layout, pixmap, p) if ref_layout() else None)


                loader.start()
                self.thumbnail_threads.append(loader)  # Simpan referensi agar tidak dihapus GC

        
        # Bungkus list_panel dalam QScrollArea seperti sebelumnya
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(list_panel)
        
        scroll.setStyleSheet(SCROLL_AREA)

        # Bungkus left_layout dalam QWidget
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # Tambahkan ke combined panel layout
        combined_panel_layout.addWidget(left_widget, 1)  # Button + Parameter Panel
        combined_panel_layout.addWidget(scroll, 2)        # List Panel dengan scroll

        # Simpan batch_id dalam panel untuk referensi
        combined_panel.batch_id = batch_id

        return combined_panel
    
    # Contoh penggunaan di handle_delete_batch
    def handle_delete_batch(self, batch_id):
        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus batch {batch_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.deleter_thread = BatchDeleteProcess(self.database_manager, batch_id, CACHE_DIR, self.thumbnail_threads)
            self.deleter_thread.batch_deleted.connect(self.data_changed.emit)  # Refresh UI setelah penghapusan selesai
            self.deleter_thread.start()

    def handle_import_button(self):
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
