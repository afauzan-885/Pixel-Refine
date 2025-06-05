import json
import os

from PyQt6.QtWidgets import (QLabel, QSizePolicy, QWidget, QVBoxLayout, QScrollArea,
                             QHBoxLayout, QPushButton, QComboBox, QCheckBox,
                             QMessageBox)
from PyQt6.QtCore import (pyqtSignal, QPropertyAnimation, QEasingCurve, QEvent,
                          QTimer, pyqtSlot, QThread)
import weakref
from PyQt6.QtCore import (pyqtSignal, Qt, QSize, QTimer)
from PyQt6.QtGui import QIcon, QFont
from UI.enhance_stack.algorithm.alignment.AKAZE import running_akaze
from UI.enhance_stack.algorithm.alignment.Farneback_optical_flow import running_farneback_optical_flow
from UI.enhance_stack.algorithm.alignment.ORB import running_orb
from UI.enhance_stack.algorithm.denoising.Average import running_average
from UI.enhance_stack.algorithm.denoising.Median import running_median
from UI.enhance_stack.algorithm.denoising.Similarity import running_similarity
from UI.enhance_stack.algorithm.denoising.Similarity_V2 import running_similarity_v2
from UI.enhance_stack.algorithm.super_resolution.Interpolation import running_interpolation
from UI.enhance_stack.components.algorithm_list import get_algorithm_options
from UI.enhance_stack.components.batch_page_layout.image_batch_management import handle_add_image_to_batch
from UI.enhance_stack.components.batch_page_layout.thumbnail import ThumbnailLoader, thumbnail_placeholder, show_thumbnail
from UI.enhance_stack.logic.workflow_process import ImageViewer, get_last_image
from UI.resources.animation.animation_manager import StackedWidgetAnimator
from UI.resources.stylesheet.stylesheet import DROPDOWN_BOX, SCROLL_AREA, TOGGLE_SWITCH_STYLE
from UI.settings.General.Language import language_config
from config import GENERAL_SETTINGS_FILE

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
                 initial_state=None, sequential_batch_number=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.sequential_batch_number = sequential_batch_number
        self.batch_id = batch_id
        self.parent_widget = parent
        self.thumbnail_threads = thumbnail_threads if thumbnail_threads is not None else []
        self.thumbnail_placeholders = thumbnail_placeholders if thumbnail_placeholders is not None else weakref.WeakValueDictionary()
        self.animator = StackedWidgetAnimator(self)

        self.selected_algorithms = {
            'alignment': None,
            'super_resolution': None,
            'denoising': None
        }
        self.initial_state = initial_state if initial_state is not None else {}
        self.checkboxes = {}
        self.comboboxes = {}

        # Hitung jumlah gambar dalam batch ini sekali
        self.image_paths_in_batch = []
        self.image_count_in_batch = 0
        if self.batch_id is not None:
            try:
                self.image_paths_in_batch = self.database_manager.get_images_by_batch(self.batch_id)
                self.image_count_in_batch = len(self.image_paths_in_batch)
            except Exception as e:
                print(f"Error getting images for batch {self.batch_id}: {e}")

        # Flag untuk mengecek apakah overlay masih “alive”
        self._overlay_alive = False

        self.init_ui()

    def get_thumbnail_setting(self):
        if os.path.exists(GENERAL_SETTINGS_FILE):
            try:
                with open(GENERAL_SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                    return settings.get("create_thumbnail", False)
            except Exception as e:
                print(f"Error reading thumbnail setting: {e}")
        return False

    def init_ui(self):
        create_thumbnail = self.get_thumbnail_setting()
        self.setFixedHeight(115)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # === Thumbnail list panel (kanan)
        self.list_panel = QWidget()
        self.list_panel.setStyleSheet("background-color: #DBDBDB")
        self.list_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.list_layout = QHBoxLayout(self.list_panel)
        self.list_layout.setContentsMargins(5, 5, 5, 5)
        self.list_layout.setSpacing(10)

        # === Parameter panel (kiri)
        parameter_section_widget = self.layout_panel_parameter(self.list_layout)
        parameter_section_widget.setMinimumWidth(430)

        # === Scroll area untuk thumbnails
        self.scroll_list_panel = QScrollArea()
        self.scroll_list_panel.setWidgetResizable(True)
        self.scroll_list_panel.setWidget(self.list_panel)
        self.scroll_list_panel.setStyleSheet(SCROLL_AREA)
        self.scroll_list_panel.setMinimumHeight(100)

        # Tambahkan ke layout utama
        main_layout.addWidget(parameter_section_widget, 1)
        main_layout.addWidget(self.scroll_list_panel, 2)

        # === Overlay progress label (di atas viewport scroll area)
        self.progress_overlay = QLabel(self.scroll_list_panel.viewport())
        self.progress_overlay.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
            color: white;
            font-weight: bold;
            font-size: 14px;
            border-radius: 5px;
            padding: 10px;
        """)
        self.progress_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_overlay.hide()

        # === Status overlay dan koneksi sinyal destroyed ke handler yang aman
        self._overlay_alive = True
        self.progress_overlay.destroyed.connect(self._on_overlay_destroyed)

        # === Thumbnail generation logic
        if self.batch_id is not None and create_thumbnail:
            QTimer.singleShot(500, self.delay_thumbnails)
        elif self.batch_id is not None:
            self.load_text_labels()

    def _on_overlay_destroyed(self, *args):
        # Dipanggil otomatis ketika overlay QLabel dihancurkan oleh PyQt
        self._overlay_alive = False
        print(f"[DEBUG] Overlay progress di batch {self.batch_id} telah dihancurkan.")

    def delay_thumbnails(self):
        # Ambil semua path gambar di batch
        self.pending_thumbnail_paths = self.database_manager.get_images_by_batch(self.batch_id)
        self.total_images = len(self.pending_thumbnail_paths)
        self.thumbnails_loaded = 0
        self.active_thumbnail_loaders = 0
        self.max_concurrent_loaders = 4
        self.thumbnail_loader_queue = []

        # Tampilkan progress overlay, langsung atur ukurannya
        self.progress_overlay.setText("Create thumbnail: 0%")
        self.progress_overlay.resize(self.scroll_list_panel.viewport().size())
        self.progress_overlay.show()
        self.progress_overlay.raise_()

        # Mulai load batch thumbnail
        self._start_next_thumbnail_loaders()

    def _start_next_thumbnail_loaders(self):
        """
        Jalankan loading thumbnail secara asynchronous hingga semua selesai.
        """
        while self.active_thumbnail_loaders < self.max_concurrent_loaders and self.pending_thumbnail_paths:
            path = self.pending_thumbnail_paths.pop(0)

            # Buat placeholder dulu (misal thumbnail_placeholder akan menaruh widget kosong)
            placeholder = thumbnail_placeholder(self.list_layout, path, self.thumbnail_placeholders)

            # Buat loader baru
            loader = ThumbnailLoader(path)
            animator = self.animator
            self.active_thumbnail_loaders += 1

            # Hubungkan signal thumbnail_ready ke callback on_ready
            loader.thumbnail_ready.connect(self._make_loader_callback(animator))
            loader.start()
            self.thumbnail_threads.append(loader)

    def _make_loader_callback(self, animator_ref):
        """
        Mengembalikan fungsi on_ready(image, image_path) yang sudah mengecek
        apakah overlay masih 'alive' sebelum setText(...).
        """
        @pyqtSlot(object, str)
        def on_ready(image, image_path):
            try:
                show_thumbnail(weakref.ref(self.list_layout), image, image_path, animator_ref)
            except Exception as e:
                print(f"Error while loading thumbnail: {e}")
                try:
                    show_thumbnail(weakref.ref(self.list_layout), image, image_path, animator_ref)
                except:
                    pass

            # 2) Update counters
            self.active_thumbnail_loaders -= 1
            self.thumbnails_loaded += 1

            # 3) Sebelum memanggil setText, cek dulu apakah overlay masih alive
            if not getattr(self, "_overlay_alive", False):
                self._start_next_thumbnail_loaders()
                return

            # 4) Jika overlay masih hidup, update persentase dan sembunyikan jika sudah 100%
            if self.total_images > 0:
                percent = int((self.thumbnails_loaded / self.total_images) * 100)
                try:
                    self.progress_overlay.setText(f"Create thumbnail: {percent}%")
                    self.progress_overlay.setStyleSheet("""
                        background-color: rgba(0, 0, 0, 150);
                        color: white;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 10px;
                    """)
                    self.progress_overlay.adjustSize()
                except RuntimeError:
                    # Kalau tiba-tiba QLabel sudah dihapus, abaikan saja
                    pass

                if percent >= 100:
                    # Setelah 100%, langsung sembunyikan overlay
                    try:
                        self.progress_overlay.hide()
                    except:
                        pass

            # 5) Lanjutkan loading thumbnail berikutnya
            self._start_next_thumbnail_loaders()

        return on_ready

    def closeEvent(self, event):
        """
        Override closeEvent agar kita bisa disconnect semua ThumbnailLoader
        sebelum widget ini benar-benar di-destroy.
        """
        # 1) Abort semua thread/loader yang masih berjalan dan disconnect signal
        for loader in getattr(self, 'thumbnail_threads', []):
            try:
                loader.thumbnail_ready.disconnect()
            except Exception:
                pass
            try:
                # Jika ThumbnailLoader punya method untuk menghentikan thread, panggil
                loader.requestInterruption()
            except Exception:
                pass
        self.thumbnail_threads.clear()

        # 2) Terakhir, biarkan Qt memproses close seperti biasa
        super().closeEvent(event)


    def load_text_labels(self):
        image_paths = self.database_manager.get_images_by_batch(self.batch_id)
        for path in image_paths:
            label = QLabel(os.path.basename(path))
            label.setFixedSize(80, 80)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            file_name = os.path.basename(path).replace("_", "\n")
            label.setText(file_name)
            label.setStyleSheet(
                "background-color: lightgray; border: 1px solid gray; font-size: 11px; color: gray; padding: 3px;"
            )
            self.list_layout.addWidget(label)
        
    def get_current_state(self):
        """Mengambil state saat ini dari widget panel parameter."""
        state = {}
        for text, checkbox in self.checkboxes.items():
             key = f"checkbox_{text.replace(' ', '_').lower()}"
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
    
    def layout_panel_parameter(self, list_layout):
        left_section_widget = QWidget()
        left_section_h_layout = QHBoxLayout(left_section_widget)
        left_section_h_layout.setContentsMargins(0, 0, 0, 0)
        left_section_h_layout.setSpacing(5)

        button_widget = self.create_button_parameter(list_layout)
        left_section_h_layout.addWidget(button_widget)

        algorithm_area_with_tag = QWidget()
        algorithm_area_v_layout = QVBoxLayout(algorithm_area_with_tag)
        algorithm_area_v_layout.setContentsMargins(0, 0, 0, 0)
        algorithm_area_v_layout.setSpacing(0)

        # --- Label Batch ---
        if self.sequential_batch_number is not None:
            batch_label_text = language_config.BATCH_LABEL_FORMAT.format(self.sequential_batch_number, self.image_count_in_batch)
            batch_info_label = QLabel(batch_label_text)
            batch_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(8)
            font.setBold(True)
            batch_info_label.setFont(font)
            batch_info_label.setStyleSheet("""
                QLabel {
                    background-color: #607D8B;
                    color: white;
                    padding: 3px 5px;
                    border-top-left-radius: 3px;
                    border-top-right-radius: 3px;
                }
            """)
            algorithm_area_v_layout.addWidget(batch_info_label)
        else: 
            if self.batch_id is not None:
                fallback_label = QLabel(f"ID: {self.batch_id} - {self.image_count_in_batch} images")
                fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                fallback_label.setStyleSheet("background-color: #78909C; color: white; padding: 2px;")
                algorithm_area_v_layout.addWidget(fallback_label)


        algorithm_panel = self.create_parameter_panel()
        algorithm_area_v_layout.addWidget(algorithm_panel)

        left_section_h_layout.addWidget(algorithm_area_with_tag, 1)
        return left_section_widget

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
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(preview_button)  
        button_layout.addWidget(delete_button)
        
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        return button_widget
    
    def process_and_preview(self):
        """Jalankan semua algoritma batch terlebih dahulu, lalu tampilkan preview gambar."""
        self.process_all_batch()  
        self.handle_preview_button()
    
    def handle_preview_button(self):
        """Menampilkan gambar terbaru setelah batch diproses."""
        latest_image_path = get_last_image("database/stack")
        if latest_image_path:
            dialog = ImageViewer(latest_image_path, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Caution", language_config.NOT_IMAGE_PREVIEW)
    
    def dropdown_box_control(self):
        override_style = """
                        QComboBox {
                            background-color: white;
                            min-height: 10px;
                            min-width: 100px;
                        }
                        """

        # --- Alignment Dropdown ---
        alignment_options = get_algorithm_options("alignment") # Ambil data
        algorithm_alignment = QComboBox()
        algorithm_alignment.setStyleSheet(DROPDOWN_BOX + override_style)
        for name, _ in alignment_options:
            algorithm_alignment.addItem(name)
        algorithm_alignment.setVisible(False)

        # --- Super Resolution Dropdown ---
        super_res_options = get_algorithm_options("super_resolution") # Ambil data
        super_res_combo = QComboBox()
        super_res_combo.setStyleSheet(DROPDOWN_BOX + override_style)
        for name, _ in super_res_options:
            super_res_combo.addItem(name)
        super_res_combo.setVisible(False)

        # --- Denoising Dropdown ---
        denoising_options = get_algorithm_options("denoising") # Ambil data
        denoising_combox = QComboBox()
        denoising_combox.setStyleSheet(DROPDOWN_BOX + override_style)
        for name, _ in denoising_options:
            denoising_combox.addItem(name)
        denoising_combox.setVisible(False)

        # --- Simpan comboboxes dan atur state awal ---
        self.comboboxes['alignment'] = algorithm_alignment
        self.comboboxes['super_resolution'] = super_res_combo
        self.comboboxes['denoising'] = denoising_combox

        algorithm_alignment.setCurrentText(self.initial_state.get('alignment_algo', "None"))
        super_res_combo.setCurrentText(self.initial_state.get('super_resolution_algo', "None"))
        denoising_combox.setCurrentText(self.initial_state.get('denoising_algo', "None"))

        # --- Hubungkan sinyal ---
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
        print(language_config.CONSOL_LOG_RUNNING_ALGORITHM.format(category, selected_algo))
        
    def _handle_denoising_state_changed(self, is_checked):
        """Logika eksklusif saat state checkbox Denoising berubah."""
        superres_checkbox = self.checkboxes.get(language_config.PARAMETER_BATCH_SUPER_RESOLUTION)
        if not superres_checkbox: return

        if is_checked:
            superres_checkbox.blockSignals(True)
            superres_checkbox.setChecked(False)
            superres_checkbox.blockSignals(False)
        else:
            superres_checkbox.setEnabled(True)
    
    def _handle_superres_state_changed(self, is_checked):
        """Logika eksklusif saat state checkbox Super Resolution berubah."""
        denoising_checkbox = self.checkboxes.get(language_config.PARAMETER_BATCH_DENOISING)
        if not denoising_checkbox: return

        if is_checked:
            denoising_checkbox.blockSignals(True)
            denoising_checkbox.setChecked(False)
            denoising_checkbox.blockSignals(False)
        else: 
            denoising_checkbox.setEnabled(True)
        
    def _trigger_exclusive_handler(self, checkbox_key):
        """Dipanggil oleh klik label atau toggle checkbox untuk memicu logika eksklusif."""
        checkbox = self.checkboxes.get(checkbox_key)
        if not checkbox: return

        is_checked = checkbox.isChecked()
        
        if checkbox_key == language_config.PARAMETER_BATCH_DENOISING:
            self._handle_denoising_state_changed(is_checked)
        elif checkbox_key == language_config.PARAMETER_BATCH_SUPER_RESOLUTION:
            self._handle_superres_state_changed(is_checked)
        elif checkbox_key == language_config.PARAMETER_BATCH_CROP_EDGE:
             self._handle_crop_keep_edge(is_checked, checkbox_key, language_config.PARAMETER_BATCH_KEEP_EDGE)
        elif checkbox_key == language_config.PARAMETER_BATCH_KEEP_EDGE:
             self._handle_crop_keep_edge(is_checked, checkbox_key, language_config.PARAMETER_BATCH_CROP_EDGE)

        self._update_visibility_internal()
        
    def _handle_crop_keep_edge(self, is_checked, changed_cb_key, other_cb_key):
         """Logika eksklusif untuk Crop Edge dan Keep Edge."""
         changed_cb = self.checkboxes.get(changed_cb_key)
         other_cb = self.checkboxes.get(other_cb_key)
         align_cb = self.checkboxes.get(language_config.PARAMETER_BATCH_ALIGNMENT)
         if not changed_cb or not other_cb or not align_cb: return

         is_alignment_checked = align_cb.isChecked()

         if is_checked:
             other_cb.blockSignals(True)
             other_cb.setChecked(False)
             other_cb.setEnabled(False)
             other_cb.blockSignals(False)
         else:
             other_cb.setEnabled(is_alignment_checked)
        
    def _update_visibility_internal(self):
        """Memperbarui visibilitas/enabled widget berdasarkan state checkbox."""
        algorithm_alignment = self.comboboxes.get('alignment')
        super_res_combo = self.comboboxes.get('super_resolution')
        denoising_combox = self.comboboxes.get('denoising')
       
        # Kunci checkbox
        alignment_key = language_config.PARAMETER_BATCH_ALIGNMENT
        denoising_key = language_config.PARAMETER_BATCH_DENOISING
        superres_key = language_config.PARAMETER_BATCH_SUPER_RESOLUTION
        align_folder_key = language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER
        crop_edge_key = language_config.PARAMETER_BATCH_CROP_EDGE
        keep_edge_key = language_config.PARAMETER_BATCH_KEEP_EDGE

        # Dapatkan status checked dengan aman
        is_alignment_checked = self.checkboxes.get(alignment_key, QCheckBox()).isChecked()
        is_denoising_checked = self.checkboxes.get(denoising_key, QCheckBox()).isChecked()
        is_superres_checked = self.checkboxes.get(superres_key, QCheckBox()).isChecked()
        is_crop_edge_checked = self.checkboxes.get(crop_edge_key, QCheckBox()).isChecked()
        is_keep_edge_checked = self.checkboxes.get(keep_edge_key, QCheckBox()).isChecked()


        # Atur Visibilitas ComboBox/Tombol
        if algorithm_alignment: algorithm_alignment.setVisible(is_alignment_checked)
        if denoising_combox: denoising_combox.setVisible(is_denoising_checked)
        if super_res_combo: super_res_combo.setVisible(is_superres_checked)
       
        align_folder_cb = self.checkboxes.get(align_folder_key)
        if align_folder_cb: align_folder_cb.setEnabled(is_alignment_checked)

        crop_edge_cb = self.checkboxes.get(crop_edge_key)
        if crop_edge_cb: crop_edge_cb.setEnabled(is_alignment_checked and not is_keep_edge_checked) 

        keep_edge_cb = self.checkboxes.get(keep_edge_key)
        if keep_edge_cb: keep_edge_cb.setEnabled(is_alignment_checked and not is_crop_edge_checked) 

    def process_all_batch(self):
        """Jalankan semua algoritma yang dipilih HANYA JIKA checkbox terkait dicentang."""
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
                "Average": lambda:  running_average(self, single_process=False, batch_id=self.batch_id),
                "Median": lambda: running_median(self, single_process=False, batch_id=self.batch_id),
                "Similarity": lambda: running_similarity(self, single_process=False, batch_id=self.batch_id),
                "Similarity V2": lambda: running_similarity_v2(self, single_process=False, batch_id=self.batch_id),
            }
        }

        # --- Tambahkan pemetaan dari kategori ke kunci checkbox ---
        category_to_checkbox_key = {
            'alignment': language_config.PARAMETER_BATCH_ALIGNMENT,
            'super_resolution': language_config.PARAMETER_BATCH_SUPER_RESOLUTION,
            'denoising': language_config.PARAMETER_BATCH_DENOISING
        }
        # -------------------------------------------------------

        for category, algo in self.selected_algorithms.items():
            if algo and algo != "None" and category in actions and algo in actions[category]:
                checkbox_key = category_to_checkbox_key.get(category)
                if checkbox_key:
                    checkbox = self.checkboxes.get(checkbox_key)
                    if checkbox and checkbox.isChecked():
                        actions[category][algo]() 
    
    def create_parameter_panel(self):
        """
        Buat panel parameter yang berisi combo box dan checkbox.
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

        folder_button = QPushButton()
        folder_button.setVisible(False)

        algorithm_layout.addWidget(algorithm_alignment)
        algorithm_layout.addWidget(super_res_combo)
        algorithm_layout.addWidget(denoising_combox)
        algorithm_layout.addWidget(folder_button)
        algorithm_layout.addStretch()

        option_widget = QWidget()
        option_layout = QVBoxLayout(option_widget)
        option_layout.setContentsMargins(5, 5, 5, 5)
        option_layout.setSpacing(5)

        checkbox_widgets = {}
        checkbox_texts = [
            language_config.PARAMETER_BATCH_ALIGNMENT,
            language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER,
            language_config.PARAMETER_BATCH_DENOISING, # Checkbox Denoising
            language_config.PARAMETER_BATCH_SUPER_RESOLUTION, # Checkbox Super Resolution
            language_config.PARAMETER_BATCH_CROP_EDGE,
            language_config.PARAMETER_BATCH_KEEP_EDGE
        ]

        # Key yang pasti untuk Denoising dan Super Resolution
        denoising_key = language_config.PARAMETER_BATCH_DENOISING
        superres_key = language_config.PARAMETER_BATCH_SUPER_RESOLUTION
        crop_edge_key = language_config.PARAMETER_BATCH_CROP_EDGE
        keep_edge_key = language_config.PARAMETER_BATCH_KEEP_EDGE
        alignment_key = language_config.PARAMETER_BATCH_ALIGNMENT
        align_folder_key = language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER

        for text in checkbox_texts:
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setSpacing(5)

            option_checkbox = QCheckBox()
            option_checkbox.setStyleSheet(TOGGLE_SWITCH_STYLE)
            option_label = ClickableLabel(text)
            option_label.setWordWrap(True)
            option_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            option_label.clicked.connect(option_checkbox.toggle)

            self.checkboxes[text] = option_checkbox
            checkbox_widgets[text] = checkbox_widget

            key_for_state = f"checkbox_{text.replace(' ', '_').lower()}"
            initial_checked = self.initial_state.get(key_for_state, False)
            option_checkbox.setChecked(initial_checked)

            # --- PERUBAHAN KONEKSI SINYAL ---
            current_key = text
            option_label.clicked.connect(lambda key=current_key: self._trigger_exclusive_handler(key))
            # Hubungkan toggle checkbox ke fungsi perantara
            option_checkbox.toggled.connect(lambda checked, key=current_key: self._trigger_exclusive_handler(key))

            checkbox_layout.addWidget(option_checkbox)
            checkbox_layout.addWidget(option_label, 1)
            option_layout.addWidget(checkbox_widget)

        if crop_edge_key in checkbox_widgets: checkbox_widgets[crop_edge_key].setVisible(False)
        if keep_edge_key in checkbox_widgets: checkbox_widgets[keep_edge_key].setVisible(False)
        if align_folder_key in checkbox_widgets: checkbox_widgets[align_folder_key].setVisible(False)

        option_layout.addStretch()

        scroll_option_layout = QScrollArea()
        scroll_option_layout.setWidgetResizable(True)
        scroll_option_layout.setWidget(option_widget)
        scroll_option_layout.setStyleSheet(SCROLL_AREA)

        parameter_layout.addLayout(algorithm_layout, 1)
        parameter_layout.addWidget(scroll_option_layout, 1)

        # --- Panggil handler dan visibility sekali di awal ---
        self._update_visibility_internal()
        if denoising_key in self.checkboxes:
             self._trigger_exclusive_handler(denoising_key)
        if superres_key in self.checkboxes:
             self._trigger_exclusive_handler(superres_key)
        if crop_edge_key in self.checkboxes:
             self._trigger_exclusive_handler(crop_edge_key)
        if keep_edge_key in self.checkboxes:
             self._trigger_exclusive_handler(keep_edge_key)
        # Panggil juga untuk alignment & align_folder jika mereka mempengaruhi enabled state lain
        if alignment_key in self.checkboxes:
            self._update_visibility_internal() # Cukup panggil visibility
        if align_folder_key in self.checkboxes:
            self._update_visibility_internal() # Cukup panggil visibility


        return algorithm_panel
