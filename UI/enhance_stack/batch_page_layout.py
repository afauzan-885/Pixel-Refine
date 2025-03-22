import os
from PyQt6.QtWidgets import (QLabel, QSpacerItem, QSizePolicy, QWidget, QVBoxLayout, QScrollArea,
                             QHBoxLayout, QPushButton, QComboBox, QCheckBox, QLineEdit,
                             QMessageBox, QFileDialog)
import weakref
from PyQt6.QtCore import (pyqtSignal, Qt, QSize)
from PyQt6.QtGui import QIcon
from UI.enhance_stack.components.batch_page_layout.batch_layout import refresh_ui, setup_main_panel
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

        # Menggunakan fungsi dari batch_layout.py
        self.main_panel, self.main_panel_layout = setup_main_panel(self, SCROLL_AREA)
        
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
        """Membuat panel gabungan yang berisi tombol tambah, tombol delete, parameter_panel, dan list_panel."""
        create_thumbnail = CACHE.get("create_thumbnail", False)

        combined_panel = QWidget()
        combined_panel.setMaximumHeight(120)
        combined_panel_layout = QHBoxLayout(combined_panel)
        combined_panel_layout.setContentsMargins(0, 0, 0, 0)

        # Panel kanan (Thumbnail List Panel)
        list_panel = QWidget()
        list_panel.setStyleSheet("background-color: #DBDBDB")
        list_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        list_layout = QHBoxLayout(list_panel)
        list_layout.setContentsMargins(5, 5, 5, 5)
        list_layout.setSpacing(10)

        if batch_id is not None:
            image_paths = self.database_manager.get_images_by_batch(batch_id)
            for path in image_paths:
                if create_thumbnail:
                    placeholder = create_thumbnail_placeholder(list_layout, path, self.thumbnail_placeholders)
                    loader = ThumbnailLoader(path)
                    loader.thumbnail_ready.connect(
                        lambda pixmap, p, ref_layout=weakref.ref(list_layout):
                        update_thumbnail(ref_layout, pixmap, p) if ref_layout() else None
                    )
                    loader.start()
                    self.thumbnail_threads.append(loader)
                else:
                    label = QLabel(os.path.basename(path))
                    label.setFixedSize(80, 80)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setWordWrap(True)
                    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                    file_name = os.path.basename(path).replace("_", "\n")
                    label.setText(file_name)
                    label.setStyleSheet("""
                        background-color: lightgray; 
                        border: 1px solid gray; 
                        font-size: 11px;
                        color: gray;
                        padding: 3px;
                    """)
                    list_layout.addWidget(label)

        scroll_list_panel = QScrollArea()
        scroll_list_panel.setWidgetResizable(True)
        scroll_list_panel.setWidget(list_panel)
        scroll_list_panel.setStyleSheet(SCROLL_AREA)

        # Buat left widget dari fungsi modular
        left_widget = self.create_left_widget(batch_id, list_layout)

        left_widget.setMinimumWidth(420)
        combined_panel_layout.addWidget(left_widget, 1)
        combined_panel_layout.addWidget(scroll_list_panel, 2)

        combined_panel.batch_id = batch_id
        return combined_panel

    def create_left_widget(self, batch_id, list_layout):
        """Buat widget bagian kiri yang menggabungkan tombol dan panel parameter."""
        button_widget = self.create_button_widget(batch_id, list_layout)
        # Panggil method create_parameter_panel dengan self.
        parameter_panel = self.create_parameter_panel()

        left_layout = QHBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(button_widget)
        left_layout.addWidget(parameter_panel, 1)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        return left_widget

    def create_parameter_panel(self):
        """Buat panel parameter yang berisi combo box dan checkbox dengan scroll area."""
        parameter_panel = QWidget()
        parameter_panel.setStyleSheet("background-color: #EBEAEA")
        parameter_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        parameter_layout = QHBoxLayout(parameter_panel)
        parameter_layout.setContentsMargins(10, 10, 10, 10)

        # Bagian Kiri - Layout untuk Algoritma dan Folder Icon
        algorithm_layout = QVBoxLayout()
        algorithm_layout.setContentsMargins(5, 5, 5, 5)
        algorithm_layout.setSpacing(5)

        # Dropdown algoritma penyelarasan
        algorithm_combox = QComboBox()
        algorithm_combox.addItems([
            "Algoritma Penyelarasan 1", 
            "Algoritma Penyelarasan 2", 
            "Algoritma Penyelarasan 3"
        ])
        algorithm_combox.setVisible(False)  # Awalnya disembunyikan

        # Dropdown algoritma denoising/super resolusi
        denoising_combox = QComboBox()
        denoising_combox.addItems([
            "Denoising Algoritma 1", 
            "Denoising Algoritma 2", 
            "Denoising Algoritma 3"
        ])
        denoising_combox.setVisible(False)  # Awalnya disembunyikan

        # Tombol folder output
        folder_button = QPushButton()
        folder_button.setIcon(QIcon("UI/resources/icon/folder-output.png"))  # Ganti dengan path icon yang sesuai
        folder_button.setVisible(False)  # Awalnya disembunyikan

        # Tambahkan ke layout vertikal
        algorithm_layout.addWidget(algorithm_combox)
        algorithm_layout.addWidget(denoising_combox)
        algorithm_layout.addWidget(folder_button)

        # Bagian Kanan - Checkbox dalam Scroll Area
        option_widget = QWidget()
        option_layout = QVBoxLayout(option_widget)
        option_layout.setContentsMargins(5, 5, 5, 5)
        option_layout.setSpacing(5)

        checkboxes = {}
        checkbox_texts = [
            language_config.PARAMETER_BATCH_ALIGNMENT,
            language_config.PARAMETER_BATCH_ALIGNMENT_TO_PROCESS,
            language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER,
            language_config.PARAMETER_BATCH_DENOISING,
            language_config.PARAMETER_BATCH_SUPER_RESOLUTION,
            language_config.PARAMETER_BATCH_CROP_EDGE,
            language_config.PARAMETER_BATCH_KEEP_EDGE
        ]

        for text in checkbox_texts:
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setSpacing(5)

            option_checkbox = QCheckBox()
            option_label = QLabel(text)
            option_label.setWordWrap(True)
            option_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            checkbox_layout.addWidget(option_checkbox)
            checkbox_layout.addWidget(option_label, 1)
            option_layout.addWidget(checkbox_widget)

            checkboxes[text] = option_checkbox  # Simpan checkbox dalam dictionary

        option_layout.addStretch()

        scroll_option_layout = QScrollArea()
        scroll_option_layout.setWidgetResizable(True)
        scroll_option_layout.setWidget(option_widget)
        scroll_option_layout.setStyleSheet("border: none;")

        parameter_layout.addLayout(algorithm_layout, 1)
        parameter_layout.addWidget(scroll_option_layout, 1)

        # EVENT HANDLER
        def update_visibility():
            """Perbarui tampilan dropdown dan ikon folder sesuai dengan checkbox yang aktif."""
            is_alignment_checked = checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT].isChecked()
            is_denoising_checked = checkboxes[language_config.PARAMETER_BATCH_DENOISING].isChecked()
            is_superres_checked = checkboxes[language_config.PARAMETER_BATCH_SUPER_RESOLUTION].isChecked()

            # Tampilkan dropdown penyelarasan jika "Selaraskan Gambar" dicentang
            algorithm_combox.setVisible(is_alignment_checked)

            # Tampilkan dropdown denoising jika "Denoising" atau "Super Resolusi" dicentang
            denoising_combox.setVisible(is_denoising_checked or is_superres_checked)

            # Tampilkan ikon folder jika "Simpan Hasil Penyelarasan ke dalam Folder" dicentang
            folder_button.setVisible(checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER].isChecked())

            # Logika untuk checkbox ALIGNMENT_TO_PROCESS:
            # Aktif hanya jika kondisi terpenuhi:
            # 1. PARAMETER_BATCH_ALIGNMENT dicentang, dan
            # 2. Salah satu dari PARAMETER_BATCH_DENOISING atau PARAMETER_BATCH_SUPER_RESOLUTION dicentang.
            if is_alignment_checked and (is_denoising_checked or is_superres_checked):
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_PROCESS].setEnabled(True)
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_PROCESS].setChecked(True)
            else:
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_PROCESS].setChecked(False)
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_PROCESS].setEnabled(False)

            # Logika untuk checkbox ALIGNMENT_TO_FOLDER:
            # Hanya tersedia (enabled) jika checkbox ALIGNMENT aktif.
            if is_alignment_checked:
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER].setEnabled(True)
            else:
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER].setChecked(False)
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER].setEnabled(False)

            # Logika untuk checkbox CROP_EDGE dan KEEP_EDGE:
            # Hanya aktif jika checkbox ALIGNMENT aktif, jika tidak maka dinonaktifkan.
            if is_alignment_checked:
                checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE].setEnabled(True)
                checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE].setEnabled(True)
            else:
                checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE].setChecked(False)
                checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE].setChecked(False)
                checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE].setEnabled(False)
                checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE].setEnabled(False)


        def toggle_exclusive_checkboxes(state, other_checkbox):
            """
            Jika checkbox diaktifkan, matikan checkbox lainnya.
            Jika checkbox dimatikan, aktifkan kembali pilihan pada checkbox lainnya.
            """
            if state == 2:  # 2 = Qt.Checked
                other_checkbox.setChecked(False)
                other_checkbox.setEnabled(False)
            else:
                other_checkbox.setEnabled(True)

        # Hubungkan semua checkbox ke fungsi update_visibility
        for checkbox in checkboxes.values():
            checkbox.stateChanged.connect(update_visibility)

        # Buat checkbox eksklusif untuk Denoising & Super Resolusi
        checkboxes[language_config.PARAMETER_BATCH_DENOISING].stateChanged.connect(
            lambda state: toggle_exclusive_checkboxes(state, checkboxes[language_config.PARAMETER_BATCH_SUPER_RESOLUTION])
        )
        checkboxes[language_config.PARAMETER_BATCH_SUPER_RESOLUTION].stateChanged.connect(
            lambda state: toggle_exclusive_checkboxes(state, checkboxes[language_config.PARAMETER_BATCH_DENOISING])
        )

        # Buat checkbox eksklusif untuk Potong Tepi & Pertahankan Tepi
        checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE].stateChanged.connect(
            lambda state: toggle_exclusive_checkboxes(state, checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE])
        )
        checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE].stateChanged.connect(
            lambda state: toggle_exclusive_checkboxes(state, checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE])
        )

        return parameter_panel


    def create_button_widget(self, batch_id, list_layout):
        """Buat widget tombol yang berisi tombol add, preview, dan delete."""
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Add button
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
        add_button.setToolTip(language_config.ADD_IMAGE_BUTTON)
        add_button.clicked.connect(lambda: handle_add_image_to_batch(self, self.database_manager, self.thumbnail_threads, 
                                                                    batch_id, list_layout))


        # Preview button
        play_preview = QPushButton()
        play_preview.setFixedSize(30, 30)
        play_preview.setIcon(QIcon("UI/resources/icon/play-preview.png"))
        play_preview.setStyleSheet("""
            QPushButton {
                background-color: #31CBD1;
                border-radius: 5px;
                color: white;
                font-weight: semi-bold;
            }
            QPushButton:hover {
                background-color: #27A1A7;
            }
        """)
        play_preview.setToolTip(language_config.PREVIEW_IMAGE_BUTTON)

        # Delete button
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
        delete_button.setToolTip(language_config.DELETE_IMAGE_BUTTON)
        delete_button.clicked.connect(lambda: self.handle_delete_batch(batch_id))

        button_layout.addWidget(add_button)
        button_layout.addWidget(play_preview)
        button_layout.addWidget(delete_button)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        return button_widget
    
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
