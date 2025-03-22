import os
import sqlite3
from PyQt6.QtWidgets import (QLabel, QSizePolicy, QWidget, QVBoxLayout, QScrollArea,
                             QHBoxLayout, QPushButton, QComboBox, QCheckBox)
import weakref
from PyQt6.QtCore import (pyqtSignal, Qt, QSize)
from PyQt6.QtGui import QIcon
from UI.enhance_stack.components.batch_page_layout.image_batch_management import handle_add_image_to_batch
from UI.enhance_stack.components.batch_page_layout.thumbnail import ThumbnailLoader, create_thumbnail_placeholder, update_thumbnail
from UI.resources.stylesheet.stylesheet import SCROLL_AREA
from UI.settings.General.Language import language_config
from config import CACHE

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class CombinedPanel(QWidget):
    """
    Kelas untuk membuat panel gabungan yang memuat:
    - Tombol (add & delete)
    - Panel parameter (combo box & checkbox)
    - Panel list thumbnail
    """
    def __init__(self, database_manager, batch_id=None, parent=None,
                 thumbnail_threads=None, thumbnail_placeholders=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.batch_id = batch_id
        self.parent_widget = parent
        self.thumbnail_threads = thumbnail_threads if thumbnail_threads is not None else []
        self.thumbnail_placeholders = thumbnail_placeholders if thumbnail_placeholders is not None else weakref.WeakValueDictionary()
        self.init_ui()
    
    def init_ui(self):
        create_thumbnail = CACHE.get("create_thumbnail", False)
        
        # Atur tinggi maksimal panel gabungan
        self.setMaximumHeight(120)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Panel kanan: Thumbnail List Panel
        list_panel = QWidget()
        list_panel.setStyleSheet("background-color: #DBDBDB")
        list_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        list_layout = QHBoxLayout(list_panel)
        list_layout.setContentsMargins(5, 5, 5, 5)
        list_layout.setSpacing(10)
        
        if self.batch_id is not None:
            image_paths = self.database_manager.get_images_by_batch(self.batch_id)
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
                    label.setStyleSheet(
                        "background-color: lightgray; border: 1px solid gray; font-size: 11px; color: gray; padding: 3px;"
                    )
                    list_layout.addWidget(label)
        
        scroll_list_panel = QScrollArea()
        scroll_list_panel.setWidgetResizable(True)
        scroll_list_panel.setWidget(list_panel)
        scroll_list_panel.setStyleSheet(SCROLL_AREA)
        
        # Buat left widget yang berisi tombol & panel parameter
        left_widget = self.create_left_widget(list_layout)
        left_widget.setMinimumWidth(420)
        
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(scroll_list_panel, 2)
    
    def create_left_widget(self, list_layout):
        """Buat widget bagian kiri yang menggabungkan tombol dan panel parameter."""
        button_widget = self.create_button_widget(list_layout)
        parameter_panel = self.create_parameter_panel()
        
        left_layout = QHBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(button_widget)
        left_layout.addWidget(parameter_panel, 1)
        
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        return left_widget
    
    def create_button_widget(self, list_layout):
        """Buat widget tombol yang berisi tombol add dan delete."""
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tombol Add
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
        add_button.clicked.connect(lambda: handle_add_image_to_batch(
            self.parent_widget,
            self.database_manager,
            self.thumbnail_threads,
            self.batch_id,
            list_layout
        ))
        
        # Tombol Delete
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
        delete_button.clicked.connect(lambda: self.parent_widget.handle_delete_batch(self.batch_id))
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        return button_widget
    
    def dropdown_box_control(self):
        """Buat combo box untuk algoritma penyelarasan, super resolusi, dan denoising."""
        # Combo box untuk algoritma penyelarasan
        algorithm_alignment = QComboBox()
        algorithm_alignment.addItems([
            "Algoritma Penyelarasan 1", 
            "Algoritma Penyelarasan 2", 
            "Algoritma Penyelarasan 3"
        ])
        algorithm_alignment.setVisible(False)
        
        # Combo box untuk super resolusi
        super_res_combo = QComboBox()
        super_res_combo.addItems([
            "Super Resolusi Algoritma 1",
            "Super Resolusi Algoritma 2",
            "Super Resolusi Algoritma 3"
        ])
        super_res_combo.setVisible(False)
        
        # Combo box untuk denoising
        denoising_combox = QComboBox()
        denoising_combox.addItems([
            "Denoising Algoritma 1", 
            "Denoising Algoritma 2", 
            "Denoising Algoritma 3"
        ])
        denoising_combox.setVisible(False)
        
        # Hubungkan sinyal currentIndexChanged untuk masing-masing dropdown
        algorithm_alignment.currentIndexChanged.connect(
            lambda index: self.execute_algorithm('alignment', algorithm_alignment.currentText())
        )
        super_res_combo.currentIndexChanged.connect(
            lambda index: self.execute_algorithm('super_resolution', super_res_combo.currentText())
        )
        denoising_combox.currentIndexChanged.connect(
            lambda index: self.execute_algorithm('denoising', denoising_combox.currentText())
        )
        
        return algorithm_alignment, super_res_combo, denoising_combox
    
    def execute_algorithm(self, category, selected_algo):
        """
        Eksekusi algoritma berdasarkan kategori dan pilihan dropdown.
        """
        if category == 'alignment':
            if selected_algo == "Algoritma Penyelarasan 1":
                print("Menjalankan Algoritma Penyelarasan 1")
            elif selected_algo == "Algoritma Penyelarasan 2":
                print("Menjalankan Algoritma Penyelarasan 2")
            elif selected_algo == "Algoritma Penyelarasan 3":
                print("Menjalankan Algoritma Penyelarasan 3")
        elif category == 'super_resolution':
            if selected_algo == "Super Resolusi Algoritma 1":
                print("Menjalankan Super Resolusi Algoritma 1")
            elif selected_algo == "Super Resolusi Algoritma 2":
                print("Menjalankan Super Resolusi Algoritma 2")
            elif selected_algo == "Super Resolusi Algoritma 3":
                print("Menjalankan Super Resolusi Algoritma 3")
        elif category == 'denoising':
            if selected_algo == "Denoising Algoritma 1":
                print("Menjalankan Denoising Algoritma 1")
            elif selected_algo == "Denoising Algoritma 2":
                print("Menjalankan Denoising Algoritma 2")
            elif selected_algo == "Denoising Algoritma 3":
                print("Menjalankan Denoising Algoritma 3")
    
    def create_parameter_panel(self):
        """Buat panel parameter yang berisi combo box dan checkbox dengan scroll area."""
        parameter_panel = QWidget()
        parameter_panel.setStyleSheet("background-color: #EBEAEA")
        parameter_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        parameter_layout = QHBoxLayout(parameter_panel)
        parameter_layout.setContentsMargins(10, 10, 10, 10)
        
        # Bagian Kiri: Layout untuk combo box dan folder icon
        algorithm_layout = QVBoxLayout()
        algorithm_layout.setContentsMargins(5, 5, 5, 5)
        algorithm_layout.setSpacing(5)
        
        # Buat combo box dari fungsi dropdown_box_control
        algorithm_alignment, super_res_combo, denoising_combox = self.dropdown_box_control()
        
        # Tombol folder output
        folder_button = QPushButton()
        folder_button.setIcon(QIcon("UI/resources/icon/folder-output.png"))
        folder_button.setVisible(False)
        
        algorithm_layout.addWidget(algorithm_alignment)
        algorithm_layout.addWidget(super_res_combo)
        algorithm_layout.addWidget(denoising_combox)
        algorithm_layout.addWidget(folder_button)
        
        # Bagian Kanan: Checkbox dalam scroll area
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
            # Gunakan ClickableLabel sebagai label yang dapat diklik
            option_label = ClickableLabel(text)
            option_label.setWordWrap(True)
            option_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            option_label.clicked.connect(option_checkbox.toggle)
            
            checkbox_layout.addWidget(option_checkbox)
            checkbox_layout.addWidget(option_label, 1)
            option_layout.addWidget(checkbox_widget)
            
            checkboxes[text] = option_checkbox
        
        option_layout.addStretch()
        
        scroll_option_layout = QScrollArea()
        scroll_option_layout.setWidgetResizable(True)
        scroll_option_layout.setWidget(option_widget)
        scroll_option_layout.setStyleSheet("border: none;")
        
        parameter_layout.addLayout(algorithm_layout, 1)
        parameter_layout.addWidget(scroll_option_layout, 1)
        
        # EVENT HANDLER: Update tampilan dropdown dan ikon folder berdasarkan checkbox
        def update_visibility():
            is_alignment_checked = checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT].isChecked()
            is_denoising_checked = checkboxes[language_config.PARAMETER_BATCH_DENOISING].isChecked()
            is_superres_checked = checkboxes[language_config.PARAMETER_BATCH_SUPER_RESOLUTION].isChecked()
            
            algorithm_alignment.setVisible(is_alignment_checked)
            denoising_combox.setVisible(is_denoising_checked)
            super_res_combo.setVisible(is_superres_checked)
            folder_button.setVisible(checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER].isChecked())
            
            if is_alignment_checked and (is_denoising_checked or is_superres_checked):
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_PROCESS].setEnabled(True)
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_PROCESS].setChecked(True)
            else:
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_PROCESS].setChecked(False)
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_PROCESS].setEnabled(False)
            
            if is_alignment_checked:
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER].setEnabled(True)
            else:
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER].setChecked(False)
                checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER].setEnabled(False)
            
            if is_alignment_checked:
                checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE].setEnabled(True)
                checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE].setEnabled(True)
            else:
                checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE].setChecked(False)
                checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE].setChecked(False)
                checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE].setEnabled(False)
                checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE].setEnabled(False)
        
        def toggle_exclusive_checkboxes(state, other_checkbox):
            if state == 2:  # Qt.Checked
                other_checkbox.setChecked(False)
                other_checkbox.setEnabled(False)
            else:
                other_checkbox.setEnabled(True)
        
        for checkbox in checkboxes.values():
            checkbox.stateChanged.connect(update_visibility)
        
        # Checkbox eksklusif untuk Denoising & Super Resolusi
        checkboxes[language_config.PARAMETER_BATCH_DENOISING].stateChanged.connect(
            lambda state: toggle_exclusive_checkboxes(state, checkboxes[language_config.PARAMETER_BATCH_SUPER_RESOLUTION])
        )
        checkboxes[language_config.PARAMETER_BATCH_SUPER_RESOLUTION].stateChanged.connect(
            lambda state: toggle_exclusive_checkboxes(state, checkboxes[language_config.PARAMETER_BATCH_DENOISING])
        )
        
        # Checkbox eksklusif untuk Crop Edge & Keep Edge
        checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE].stateChanged.connect(
            lambda state: toggle_exclusive_checkboxes(state, checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE])
        )
        checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE].stateChanged.connect(
            lambda state: toggle_exclusive_checkboxes(state, checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE])
        )
        
        return parameter_panel

