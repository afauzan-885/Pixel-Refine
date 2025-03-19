from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy,
                             QSpacerItem, QPushButton, QScrollArea, QMessageBox,
                             QFileDialog, QLabel)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.enhance_stack.logic.multi_threading import BatchImageImportThreading
from UI.resources.stylesheet.stylesheet import SCROLL_AREA
from UI.settings.General.Language import language_config

class BatchPageLayout(QWidget):
    data_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
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
    
    def refresh_ui(self):
        # Merefresh UI agar tetap realtime dalam menampilkan data
        while self.main_panel_layout.count():
            item = self.main_panel_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        # Ambil ulang data batch dari database
        batch_ids = self.database_manager.get_all_batch_ids()
        
        if not batch_ids:
            placeholder = QLabel("Tidak ada batch yang tersedia.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_panel_layout.addWidget(placeholder)
        else:
            for batch_id in batch_ids:
                combined_panel = self.setup_combined_panel(batch_id=batch_id)
                self.main_panel_layout.addWidget(combined_panel)
        
        # Tambahkan spacer agar layout tetap rapi
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_panel_layout.addSpacerItem(spacer)


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

        # Hubungkan tombol "Tambah" ke fungsi handle_add_image_to_batch
        add_button.clicked.connect(lambda: self.handle_add_image_to_batch(batch_id, list_layout))

        
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
        
        # Jika batch_id diberikan, ambil data gambar dari database dan tampilkan
        if batch_id is not None:
            image_paths = self.database_manager.get_images_by_batch(batch_id)
            for path in image_paths:
                thumb_label = QLabel()
                thumb_label.setFixedSize(80, 80)
                thumb_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
                thumb_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                # Misalnya, tampilkan nama file sebagai thumbnail (Anda bisa menggantinya dengan QPixmap)
                thumb_label.setText(path.split("/")[-1])
                list_layout.addWidget(thumb_label)
        
        # Bungkus list_panel dalam QScrollArea agar dapat di-scroll secara horizontal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(list_panel)
        # Jika Anda memiliki stylesheet khusus untuk scroll area, misalnya SCROLL_AREA, aktifkan:
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
    
    def handle_add_image_to_batch(self, batch_id, list_layout):
        """
        Menambahkan gambar ke batch yang sudah ada, dengan pengecekan duplikat dalam batch tersebut.

        Args:
            batch_id (int): ID batch tempat gambar akan ditambahkan.
            list_layout (QHBoxLayout): Layout yang menampilkan daftar gambar.
        """
        if batch_id is None:
            print("Batch ID tidak valid.")
            return

        # Ambil daftar image_id yang sudah ada dalam batch ini
        existing_image_paths = self.database_manager.get_images_by_batch(batch_id)

        # Buka dialog pemilihan file
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(None, "Pilih Gambar", "", language_config.HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION)

        if not file_paths:
            return  # Jika user tidak memilih gambar, keluar dari fungsi

        # Cek duplikat dalam batch ini
        duplicates = [path for path in file_paths if path in existing_image_paths]
        unique_files = [path for path in file_paths if path not in existing_image_paths]

        # Jika ada duplikat, beri peringatan ke user
        if duplicates:
            message = f"{len(duplicates)} gambar sudah ada dalam batch ini dan tidak akan ditambahkan lagi."
            QMessageBox.warning(None, "Gambar Duplikat", message)

        # Simpan hanya gambar yang unik ke database
        if unique_files:
            self.database_manager.batch_process_save_image_path(batch_id, unique_files)

            # Tambahkan thumbnail ke list_layout hanya untuk gambar unik
            for path in unique_files:
                thumb_label = QLabel()
                thumb_label.setFixedSize(80, 80)
                thumb_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
                thumb_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                thumb_label.setText(path.split("/")[-1])  # Menampilkan nama file
                list_layout.addWidget(thumb_label)

            print(f"Added {len(unique_files)} new images to batch {batch_id}")
    
    def handle_delete_batch(self, batch_id):
        # Opsional: Tampilkan konfirmasi sebelum menghapus
        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus batch {batch_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.database_manager.batch_process_delete_batch(batch_id)
            # Emit sinyal untuk merefresh UI setelah penghapusan
            self.data_changed.emit()

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
            QMessageBox.information(self, language_config.HANDLE_IMPORT_BUTTON_IMAGE_NO_VALID_SELECTED)