import os
import sqlite3
from PyQt6.QtWidgets import (QLabel, QSizePolicy, QWidget, QVBoxLayout, QScrollArea,
                             QHBoxLayout, QPushButton, QComboBox, QCheckBox,
                             QMessageBox, QProgressDialog)
import weakref
from PyQt6.QtCore import (pyqtSignal, Qt, QSize)
from PyQt6.QtGui import QIcon
from UI.enhance_stack.algorithm.alignment.AKAZE import running_akaze
from UI.enhance_stack.algorithm.alignment.Farneback_optical_flow import running_farneback_optical_flow
from UI.enhance_stack.algorithm.alignment.ORB import running_orb
from UI.enhance_stack.algorithm.denoising.Average import running_average
from UI.enhance_stack.algorithm.denoising.Median import running_median
from UI.enhance_stack.algorithm.denoising.Similarity import running_similarity
from UI.enhance_stack.algorithm.denoising.Similarity_V2 import running_similarity_v2
from UI.enhance_stack.algorithm.super_resolution.Interpolation import running_interpolation
from UI.enhance_stack.components.batch_page_layout.image_batch_management import handle_add_image_to_batch
from UI.enhance_stack.components.batch_page_layout.thumbnail import ThumbnailLoader, create_thumbnail_placeholder, update_thumbnail
from UI.enhance_stack.logic.workflow_process import ImageViewer, get_last_image
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
                 thumbnail_threads=None, thumbnail_placeholders=None,
                 initial_state=None): 
        super().__init__(parent)
        self.database_manager = database_manager
        self.batch_id = batch_id
        self.parent_widget = parent
        self.thumbnail_threads = thumbnail_threads if thumbnail_threads is not None else []
        self.thumbnail_placeholders = thumbnail_placeholders if thumbnail_placeholders is not None else weakref.WeakValueDictionary()
        
        self.selected_algorithms = {
            'alignment': None,
            'super_resolution': None,
            'denoising': None
        }
        self.initial_state = initial_state if initial_state is not None else {}
        self.checkboxes = {}
        self.comboboxes = {}
        self.init_ui()
    
    def init_ui(self):
        create_thumbnail = CACHE.get("create_thumbnail", False)
        
        # Atur tinggi maksimal panel gabungan
        self.setMaximumHeight(120)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Panel kanan: Thumbnail List Panel tanpa QScrollArea
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
        
        # Buat left widget yang berisi tombol & panel parameter
        parameter_panel_layout = self.create_parameter_panel_layout(list_layout)
        parameter_panel_layout.setMinimumWidth(420)
        
        scroll_list_panel = QScrollArea()
        scroll_list_panel.setWidgetResizable(True)
        scroll_list_panel.setWidget(list_panel)
        scroll_list_panel.setStyleSheet(SCROLL_AREA)
        
        main_layout.addWidget(parameter_panel_layout, 1)
        main_layout.addWidget(scroll_list_panel, 2)
        
    def get_current_state(self):
        """Mengambil state saat ini dari widget panel parameter."""
        state = {}
        # Ambil state checkboxes
        for text, checkbox in self.checkboxes.items():
             # Gunakan kunci yang stabil, mungkin bukan teks bahasa dinamis
             # Misalnya, gunakan konstanta atau nama variabel
             key = f"checkbox_{text.replace(' ', '_').lower()}" # Contoh kunci sederhana
             state[key] = checkbox.isChecked()

        # Ambil state comboboxes (algoritma yang dipilih)
        if 'alignment' in self.comboboxes:
             state['alignment_algo'] = self.comboboxes['alignment'].currentText()
        if 'super_resolution' in self.comboboxes:
             state['super_resolution_algo'] = self.comboboxes['super_resolution'].currentText()
        if 'denoising' in self.comboboxes:
             state['denoising_algo'] = self.comboboxes['denoising'].currentText()

        # Tambahkan state lain jika perlu
        return state
    # --------------------------------------------------
    
    def create_parameter_panel_layout(self, list_layout):
        """Buat widget bagian kiri yang menggabungkan tombol dan panel parameter."""
        button_widget = self.create_button_parameter(list_layout)
        algorithm_panel = self.create_parameter_panel()
        
        parameter_panel = QHBoxLayout()
        parameter_panel.setContentsMargins(0, 0, 0, 0)
        parameter_panel.addWidget(button_widget)
        parameter_panel.addWidget(algorithm_panel, 1)
        
        parameter_panel_layout = QWidget()
        parameter_panel_layout.setLayout(parameter_panel)
        
        return parameter_panel_layout
    
    def create_button_parameter(self, list_layout):
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
        
        # Tombol Preview
        preview_button = QPushButton()
        preview_button.setFixedSize(30, 30)
        preview_button.setIcon(QIcon("UI/resources/icon/play-preview.png"))
        preview_button.setIconSize(QSize(15, 15))
        preview_button.setStyleSheet("""
            QPushButton {
                background-color: #FFA500; 
                border-radius: 5px; 
                color: white; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #CC8400;
            }
        """)
        
        preview_button.setToolTip(language_config.PREVIEW_IMAGE_BUTTON)
        preview_button.clicked.connect(self.process_and_preview) 
        
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
        delete_button.clicked.connect(lambda: self.parent_widget.handle_delete_individual_batch(self.batch_id))
        
        # Tambahkan tombol ke layout
        button_layout.addWidget(add_button)
        button_layout.addWidget(preview_button)  
        button_layout.addWidget(delete_button)
        
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        return button_widget
    
    def process_and_preview(self):
        """Jalankan semua algoritma batch terlebih dahulu, lalu tampilkan preview gambar."""
        self.process_all_batch()  # Jalankan semua algoritma batch
        self.handle_preview_button()  # Setelah selesai, tampilkan preview
    
    def handle_preview_button(self):
        """Menampilkan gambar terbaru setelah batch diproses."""
        latest_image_path = get_last_image("database/stack")
        if latest_image_path:
            dialog = ImageViewer(latest_image_path, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Caution", language_config.NOT_IMAGE_PREVIEW)
    
    def dropdown_box_control(self):
        """Buat combo box untuk algoritma penyelarasan, super resolusi, dan denoising."""
        # Buat combo box beserta item-nya dalam satu baris
        algorithm_alignment = QComboBox()
        alignment_algorithms = [
            ("None", language_config.NONE_ALIGNMENT_DESCRIPTION),
            ("Farneback Optical Flow", language_config.FARNEBACK_DESCRIPTION),
            ("AKAZE", language_config.AKAZE_DESCRIPTION),
            ("ORB", language_config.ORB_DESCRIPTION)
        ]
        for name, _ in alignment_algorithms:
            algorithm_alignment.addItem(name)
        algorithm_alignment.setVisible(False)

        super_res_combo = QComboBox()
        super_res_algorithms = [
            ("None", language_config.NONE_SUPER_RESOLUTION_DESCRIPTION),
            ("Interpolation", language_config.INTERPOLATION_DESCRIPTION)
        ]
        for name, _ in super_res_algorithms:
            super_res_combo.addItem(name)
        super_res_combo.setVisible(False)

        denoising_combox = QComboBox()
        denoising_algorithms = [
            ("None", language_config.NONE_DENOISING_DESCRIPTION),
            ("Average", language_config.AVERAGE_DESCRIPTION),
            ("Median", language_config.MEDIAN_DESCRIPTION),
            ("Similarity", language_config.SIMILARITY_DESCRIPTION),
            ("Similarity V2", language_config.SIMILARITY_MOTION_V2_DESCRIPTION)
        ]
        for name, _ in denoising_algorithms:
            denoising_combox.addItem(name)
        denoising_combox.setVisible(False)
        
        # --- Simpan referensi combobox ---
        self.comboboxes['alignment'] = algorithm_alignment
        self.comboboxes['super_resolution'] = super_res_combo
        self.comboboxes['denoising'] = denoising_combox
        # --------------------------------

        # --- LANGKAH 5: Terapkan state awal ke Combobox ---
        algorithm_alignment.setCurrentText(self.initial_state.get('alignment_algo', "None"))
        super_res_combo.setCurrentText(self.initial_state.get('super_resolution_algo', "None"))
        denoising_combox.setCurrentText(self.initial_state.get('denoising_algo', "None"))
        # ------------------------------------------------

        # Hubungkan sinyal currentIndexChanged menggunakan lambda untuk execute_algorithm
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
        """Simpan pilihan algoritma."""
        self.selected_algorithms[category] = selected_algo
        # Jika Anda perlu memperbarui state global segera, emit sinyal di sini
        # self.state_changed.emit(self.batch_id, self.get_current_state()) # Contoh jika pakai sinyal
        print(language_config.CONSOL_LOG_RUNNING_ALGORITHM.format(category, selected_algo))
    
    def process_all_batch(self):
        """Jalankan semua algoritma yang dipilih."""
        actions = {
            'alignment': {
                "Farneback Optical Flow": lambda: running_farneback_optical_flow(self, single_process=False, batch_id=self.batch_id),
                "AKAZE": lambda: running_akaze(self, single_process=False, batch_id=self.batch_id),
                "ORB": lambda: running_orb(self, single_process=False, batch_id=self.batch_id),
            }, 
            'super_resolution': {
                "Interpolation": lambda: running_interpolation(self, single_process=False, batch_id=self.batch_id),
            },
            'denoising': {
                "Average": lambda: running_average(self, single_process=False, batch_id=self.batch_id),
                "Median": lambda: running_median(self, single_process=False, batch_id=self.batch_id),
                "Similarity": lambda: running_similarity(self, single_process=False, batch_id=self.batch_id),
                "Similarity V2": lambda: running_similarity_v2(self, single_process=False, batch_id=self.batch_id),
            }
        }

        for category, algo in self.selected_algorithms.items():
            if algo and algo in actions.get(category, {}):
                actions[category][algo]()
            
    def create_parameter_panel(self):
        """
        Buat panel parameter yang berisi combo box dan checkbox dengan scroll area.
        Fungsi ini juga memulihkan state (checked/selected) dan mengatur visibilitas/enabled awal.
        """
        algorithm_panel = QWidget()
        algorithm_panel.setStyleSheet("background-color: #EBEAEA")
        algorithm_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        parameter_layout = QHBoxLayout(algorithm_panel)
        parameter_layout.setContentsMargins(10, 10, 10, 10)

        algorithm_layout = QVBoxLayout()
        algorithm_layout.setContentsMargins(5, 5, 5, 5)
        algorithm_layout.setSpacing(5)

        algorithm_alignment, super_res_combo, denoising_combox = self.dropdown_box_control()

        # Tombol folder output (visibilitas awal False, diatur oleh update_visibility)
        folder_button = QPushButton()
        folder_button.setIcon(QIcon("UI/resources/icon/folder-output.png")) 
        folder_button.setFixedSize(24, 24)
        folder_button.setIconSize(QSize(20, 20))
        folder_button.setVisible(False)
        # folder_button.setToolTip(language_config.OUTPUT_FOLDER_BUTTON_TOOLTIP) # Tambahkan tooltip jika perlu
        # folder_button.clicked.connect(self.handle_folder_button_click) # Hubungkan ke fungsi jika perlu

        algorithm_layout.addWidget(algorithm_alignment)
        algorithm_layout.addWidget(super_res_combo)
        algorithm_layout.addWidget(denoising_combox)
        algorithm_layout.addWidget(folder_button)
        algorithm_layout.addStretch() # Tambahkan stretch agar tombol folder tidak terlalu jauh

        # Bagian Kanan: Checkbox dalam scroll area
        option_widget = QWidget()
        option_layout = QVBoxLayout(option_widget)
        option_layout.setContentsMargins(5, 5, 5, 5)
        option_layout.setSpacing(5)

        checkbox_widgets = {} 
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
            option_label = ClickableLabel(text)
            option_label.setWordWrap(True)
            option_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            option_label.clicked.connect(option_checkbox.toggle) 
            
            # Simpan referensi ke instance variable self.checkboxes
            self.checkboxes[text] = option_checkbox
            checkbox_widgets[text] = checkbox_widget 
            
            # Pulihkan state checked
            key_for_state = f"checkbox_{text.replace(' ', '_').lower()}" # Kunci konsisten
            initial_checked = self.initial_state.get(key_for_state, False)
            option_checkbox.setChecked(initial_checked)

            checkbox_layout.addWidget(option_checkbox)
            checkbox_layout.addWidget(option_label, 1) 
            option_layout.addWidget(checkbox_widget)

        # Sembunyikan widget checkbox tertentu secara default
        checkbox_widgets[language_config.PARAMETER_BATCH_ALIGNMENT_TO_PROCESS].setVisible(False)
        checkbox_widgets[language_config.PARAMETER_BATCH_CROP_EDGE].setVisible(False)
        checkbox_widgets[language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER].setVisible(False)
        checkbox_widgets[language_config.PARAMETER_BATCH_KEEP_EDGE].setVisible(False)

        option_layout.addStretch() # Dorong checkbox ke atas

        scroll_option_layout = QScrollArea()
        scroll_option_layout.setWidgetResizable(True)
        scroll_option_layout.setWidget(option_widget)
        scroll_option_layout.setStyleSheet("QScrollArea { border: none; background-color: transparent; } QWidget { background-color: transparent; }") # Style agar menyatu


        parameter_layout.addLayout(algorithm_layout, 1) 
        parameter_layout.addWidget(scroll_option_layout, 1)

        # --- FUNGSI EVENT HANDLER (Nested agar bisa akses variabel lokal & instance) ---
        def update_visibility():
            # Akses status checkbox dari self.checkboxes
            is_alignment_checked = self.checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT].isChecked()
            is_denoising_checked = self.checkboxes[language_config.PARAMETER_BATCH_DENOISING].isChecked()
            is_superres_checked = self.checkboxes[language_config.PARAMETER_BATCH_SUPER_RESOLUTION].isChecked()
            is_align_to_folder_checked = self.checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER].isChecked()

            # Atur visibilitas ComboBox
            # Akses combobox dari variabel lokal yang didefinisikan di awal fungsi ini
            algorithm_alignment.setVisible(is_alignment_checked)
            denoising_combox.setVisible(is_denoising_checked)
            super_res_combo.setVisible(is_superres_checked)
            folder_button.setVisible(is_align_to_folder_checked)

            # Atur status enabled checkbox dependen (tanpa mengubah checked status)
            checkbox_alignment_to_process = self.checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_PROCESS]
            checkbox_alignment_to_process.setEnabled(is_alignment_checked and (is_denoising_checked or is_superres_checked))

            checkbox_align_to_folder = self.checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER]
            checkbox_align_to_folder.setEnabled(is_alignment_checked)

            checkbox_crop_edge = self.checkboxes[language_config.PARAMETER_BATCH_CROP_EDGE]
            checkbox_keep_edge = self.checkboxes[language_config.PARAMETER_BATCH_KEEP_EDGE]
            can_edge_options_be_enabled = is_alignment_checked
            checkbox_crop_edge.setEnabled(can_edge_options_be_enabled)
            checkbox_keep_edge.setEnabled(can_edge_options_be_enabled)


        def toggle_exclusive_checkboxes(state, other_checkbox_text, current_checkbox):
            other_checkbox = self.checkboxes[other_checkbox_text]
            # Hanya nonaktifkan jika yang ini dicentang
            if current_checkbox.isChecked(): # Gunakan isChecked()
                other_checkbox.setEnabled(False)
                
            else:
                is_alignment_checked = self.checkboxes[language_config.PARAMETER_BATCH_ALIGNMENT].isChecked()
                is_denoising_checked = self.checkboxes[language_config.PARAMETER_BATCH_DENOISING].isChecked()
                is_superres_checked = self.checkboxes[language_config.PARAMETER_BATCH_SUPER_RESOLUTION].isChecked()

                if other_checkbox_text == language_config.PARAMETER_BATCH_KEEP_EDGE and is_alignment_checked:
                    other_checkbox.setEnabled(True)
                elif other_checkbox_text == language_config.PARAMETER_BATCH_CROP_EDGE and is_alignment_checked:
                    other_checkbox.setEnabled(True)
                elif other_checkbox_text == language_config.PARAMETER_BATCH_SUPER_RESOLUTION and not is_denoising_checked: # Hanya aktifkan jika Denoising tidak aktif
                    other_checkbox.setEnabled(True)
                elif other_checkbox_text == language_config.PARAMETER_BATCH_DENOISING and not is_superres_checked: # Hanya aktifkan jika Super Res tidak aktif
                    other_checkbox.setEnabled(True)


        # --- Hubungkan sinyal stateChanged ---
        for text, checkbox in self.checkboxes.items():
            checkbox.stateChanged.connect(update_visibility)

        # Koneksi untuk checkbox eksklusif
        checkbox_denoising_text = language_config.PARAMETER_BATCH_DENOISING
        checkbox_superres_text = language_config.PARAMETER_BATCH_SUPER_RESOLUTION
        checkbox_crop_edge_text = language_config.PARAMETER_BATCH_CROP_EDGE
        checkbox_keep_edge_text = language_config.PARAMETER_BATCH_KEEP_EDGE

        # Pastikan checkbox ada sebelum menghubungkan sinyalnya
        if checkbox_denoising_text in self.checkboxes and checkbox_superres_text in self.checkboxes:
            self.checkboxes[checkbox_denoising_text].stateChanged.connect(
                lambda state, cb=self.checkboxes[checkbox_denoising_text], other=checkbox_superres_text: toggle_exclusive_checkboxes(state, other, cb)
            )
            self.checkboxes[checkbox_superres_text].stateChanged.connect(
                lambda state, cb=self.checkboxes[checkbox_superres_text], other=checkbox_denoising_text: toggle_exclusive_checkboxes(state, other, cb)
            )
        if checkbox_crop_edge_text in self.checkboxes and checkbox_keep_edge_text in self.checkboxes:
            self.checkboxes[checkbox_crop_edge_text].stateChanged.connect(
                lambda state, cb=self.checkboxes[checkbox_crop_edge_text], other=checkbox_keep_edge_text: toggle_exclusive_checkboxes(state, other, cb)
            )
            self.checkboxes[checkbox_keep_edge_text].stateChanged.connect(
                lambda state, cb=self.checkboxes[checkbox_keep_edge_text], other=checkbox_crop_edge_text: toggle_exclusive_checkboxes(state, other, cb)
            )
    
        update_visibility()
    
        return algorithm_panel
