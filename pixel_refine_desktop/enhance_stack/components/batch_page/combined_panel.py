import json
import os

from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QCheckBox,
    QMessageBox,
)
from PySide6.QtCore import (
    Signal,
    QTimer,
    Slot,
)
import weakref
from PySide6.QtCore import Signal, Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QFont
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.AKAZE import (
    running_akaze,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.Farneback_optical_flow import (
    running_farneback_optical_flow,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.Light_Glue import (
    running_light_glue,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.ORB import running_orb
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Average import (
    running_average,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Median import (
    running_median,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Similarity import (
    running_similarity,
)

# from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Similarity_V2 import (
#     running_similarity_v2,
# )
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.Interpolation import (
    running_interpolation,
)
from pixel_refine_desktop.enhance_stack.models.algorithm_list import (
    get_algorithm_options,
)
from pixel_refine_desktop.enhance_stack.components.batch_page.image_batch_management import (
    handle_add_image_to_batch,
)
from pixel_refine_desktop.enhance_stack.components.batch_page.thumbnail import (
    ThumbnailLoader,
    thumbnail_placeholder,
    show_thumbnail,
)
from pixel_refine_desktop.enhance_stack.core.logic.workflow_process import (
    ImageViewer,
    get_last_image,
)
from pixel_refine_desktop.ui.resources.animations.animation_manager import (
    StackedWidgetAnimator,
)
from pixel_refine_desktop.ui.resources.animations.fade import fade_out
from pixel_refine_desktop.ui.resources.styles.stylesheet import (
    DROPDOWN_BOX,
    SCROLL_AREA,
    CHECKBOX_SWITCH_STYLE,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from config import GENERAL_SETTINGS_FILE


def load_json_state(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def save_json_state(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=4)


class ClickableLabel(QLabel):
    clicked = Signal()

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

    def __init__(
        self,
        database_manager,
        batch_id=None,
        parent=None,
        thumbnail_threads=None,
        thumbnail_placeholders=None,
        initial_state=None,
        sequential_batch_number=None,
    ):
        super().__init__(parent)
        self.database_manager = database_manager
        self.sequential_batch_number = sequential_batch_number
        self.batch_id = batch_id
        self.parent_widget = parent
        self.thumbnail_threads = (
            thumbnail_threads if thumbnail_threads is not None else []
        )
        self.thumbnail_placeholders = (
            thumbnail_placeholders
            if thumbnail_placeholders is not None
            else weakref.WeakValueDictionary()
        )
        self.animator = StackedWidgetAnimator(self)

        _initial_state_passed = initial_state if initial_state is not None else {}

        if self.batch_id is not None and not _initial_state_passed:
            json_path_val = os.path.join("database", "align", "batch_parameter.json")
            all_saved_states = load_json_state(json_path_val)
            self.initial_state = all_saved_states.get(str(self.batch_id), {})

        else:
            self.initial_state = _initial_state_passed

        # Pastikan self.initial_state selalu berupa dictionary
        if not isinstance(self.initial_state, dict):
            self.initial_state = {}
        # --- MODIFIKASI SELESAI DI SINI ---

        self.selected_algorithms = {
            "alignment": self.initial_state.get("alignment_algo"),
            "super_resolution": self.initial_state.get("super_resolution_algo"),
            "denoising": self.initial_state.get("denoising_algo"),
        }

        self.checkboxes = {}
        self.comboboxes = {}

        # Hitung jumlah gambar dalam batch ini sekali
        self.image_paths_in_batch = []
        self.image_count_in_batch = 0
        if self.batch_id is not None:
            try:
                self.image_paths_in_batch = self.database_manager.get_images_by_batch(
                    self.batch_id
                )
                self.image_count_in_batch = len(self.image_paths_in_batch)
            except Exception as e:
                print(f"Error getting images for batch {self.batch_id}: {e}")

        # Flag untuk mengecek apakah overlay masih “alive”
        self._overlay_alive = False
        self.batch_info_label = None

        self.init_ui()

    def update_sequential_number(self, new_number):
        """Memperbarui nomor urut batch yang ditampilkan di UI."""
        self.sequential_batch_number = new_number

        # Temukan label yang menampilkan info batch. Asumsi ia ada di dalam `self.batch_info_label`
        if hasattr(self, "batch_info_label") and self.batch_info_label:
            batch_label_text = language_config.BATCH_LABEL_FORMAT.format(
                self.sequential_batch_number, self.image_count_in_batch
            )
            self.batch_info_label.setText(batch_label_text)

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
        self.list_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
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
        self.progress_overlay.setStyleSheet(
            """
            background-color: rgba(0, 0, 0, 150);
            color: white;
            font-weight: bold;
            font-size: 14px;
            border-radius: 5px;
            padding: 10px;
        """
        )
        self.progress_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_overlay.hide()

        # === Status overlay dan koneksi sinyal destroyed ke handler yang aman
        self._overlay_alive = True
        self.progress_overlay.destroyed.connect(self._on_overlay_destroyed)

        # === Thumbnail generation logic
        if self.batch_id is not None and create_thumbnail:
            QTimer.singleShot(50, self.delay_thumbnails)
        elif self.batch_id is not None:
            self.load_text_labels()

    @Slot(dict)
    def refresh_ui_from_broadcast(self, all_new_states):
        """
        Slot yang dipanggil saat BatchPageLayout menyiarkan perubahan state.
        Slot ini TIDAK MEMBACA FILE. Ia hanya menerima data dan menerapkan perubahan.
        """
        if not self.batch_id:
            return

        # 1. Ambil state yang relevan untuk panel ini dari data yang disiarkan
        new_state = all_new_states.get(str(self.batch_id))

        # Jika tidak ada state untuk batch ini (misalnya baru dihapus), jangan lakukan apa-apa
        if new_state is None:
            return

        self.apply_state(new_state)

    def apply_state(self, state):
        """
        Menerapkan state dari dictionary ke semua aspek panel:
        1. Widget UI (checkboxes, comboboxes).
        2. State internal (self.selected_algorithms).
        3. Tampilan visual (visibilitas, status enabled/disabled).
        """
        # ... (KODE apply_state DARI JAWABAN SEBELUMNYA SUDAH BENAR, GUNAKAN KEMBALI)
        if not isinstance(state, dict):
            print(
                f"[ERROR] apply_state received invalid state for batch {self.batch_id}"
            )
            return

        # LANGKAH 1: PERBARUI STATE INTERNAL (self.selected_algorithms)
        self.selected_algorithms["alignment"] = state.get("alignment_algo", "None")
        self.selected_algorithms["super_resolution"] = state.get(
            "super_resolution_algo", "None"
        )
        self.selected_algorithms["denoising"] = state.get("denoising_algo", "None")

        # LANGKAH 2: PERBARUI WIDGET UI (COMBOBOX & CHECKBOX)
        # Update ComboBox
        for category, key in [
            ("alignment", "alignment_algo"),
            ("super_resolution", "super_resolution_algo"),
            ("denoising", "denoising_algo"),
        ]:
            combobox = self.comboboxes.get(category)
            if combobox:
                algo_name = state.get(key, "None")
                combobox.blockSignals(True)
                combobox.setCurrentText(algo_name)
                combobox.blockSignals(False)

        # Update Checkbox
        if hasattr(self, "label_to_key_map"):
            for label_text, json_key in self.label_to_key_map.items():
                checkbox = self.checkboxes.get(label_text)
                if checkbox:
                    is_checked = state.get(json_key, False)
                    checkbox.blockSignals(True)
                    checkbox.setChecked(is_checked)
                    checkbox.blockSignals(False)

        # LANGKAH 3: SINKRONKAN TAMPILAN VISUAL UI
        self._update_visibility_internal()

        denoising_key = language_config.PARAMETER_BATCH_DENOISING
        superres_key = language_config.PARAMETER_BATCH_SUPER_RESOLUTION
        # ... (sisa logika handler eksklusif)
        if denoising_key in self.checkboxes:
            self._handle_denoising_state_changed(
                self.checkboxes[denoising_key].isChecked()
            )
        if superres_key in self.checkboxes:
            self._handle_superres_state_changed(
                self.checkboxes[superres_key].isChecked()
            )

    def _on_overlay_destroyed(self, *args):
        self._overlay_alive = False

    def delay_thumbnails(self):
        self.pending_thumbnail_paths = self.database_manager.get_images_by_batch(
            self.batch_id
        )
        self.total_images = len(self.pending_thumbnail_paths)
        self.thumbnails_loaded = 0
        self.active_thumbnail_loaders = 0
        self.max_concurrent_loaders = 4
        self.thumbnail_loader_queue = []

        self.progress_overlay.setText("Create thumbnail: 0%")
        self.progress_overlay.resize(self.scroll_list_panel.viewport().size())
        self.progress_overlay.show()
        self.progress_overlay.raise_()

        self._start_next_thumbnail_loaders()

    def _on_thumbnail_loaded(self):
        self.thumbnails_loaded += 1

        if self.thumbnails_loaded >= self.total_images:

            def hide_overlay():
                self.progress_overlay.hide()

            fade_out(
                self.animator,
                self.progress_overlay,
                duration=500,
                on_finished_callback=hide_overlay,
            )

        else:
            percent = int((self.thumbnails_loaded / self.total_images) * 100)
            self.progress_overlay.setText(f"Create thumbnail: {percent}%")

    def _start_next_thumbnail_loaders(self):
        """
        Jalankan loading thumbnail secara asynchronous hingga semua selesai.
        """
        while (
            self.active_thumbnail_loaders < self.max_concurrent_loaders
            and self.pending_thumbnail_paths
        ):
            path = self.pending_thumbnail_paths.pop(0)

            # Buat placeholder dulu (misal thumbnail_placeholder akan menaruh widget kosong)
            placeholder = thumbnail_placeholder(
                self.list_layout, path, self.thumbnail_placeholders
            )

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

        @Slot(object, str)
        def on_ready(image, image_path):
            try:
                show_thumbnail(
                    weakref.ref(self.list_layout), image, image_path, animator_ref
                )
            except Exception as e:
                print(f"Error while loading thumbnail: {e}")
                try:
                    show_thumbnail(
                        weakref.ref(self.list_layout), image, image_path, animator_ref
                    )
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
                    self.progress_overlay.setStyleSheet(
                        """
                        background-color: rgba(0, 0, 0, 150);
                        color: white;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 10px;
                    """
                    )
                    self.progress_overlay.adjustSize()
                except RuntimeError:
                    pass

                if percent >= 100:
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
        for loader in getattr(self, "thumbnail_threads", []):
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

    def get_current_state(self, batch_id=None):
        """
        Mengambil state saat ini dari widget panel parameter.
        Sekarang menggunakan self.label_to_key_map untuk konsistensi kunci.
        """
        state = {}
        if hasattr(self, "label_to_key_map"):
            for text, checkbox in self.checkboxes.items():
                key = self.label_to_key_map.get(text)
                if key:
                    state[key] = checkbox.isChecked()
        else:
            # Fallback jika map belum ada, meskipun seharusnya tidak terjadi dalam alur normal
            print("[WARNING] self.label_to_key_map not found in get_current_state.")
            for text, checkbox in self.checkboxes.items():
                # Ini adalah logika lama yang rentan bug, hanya sebagai fallback
                key = f"checkbox_{text.replace(' ', '_').lower()}"
                state[key] = checkbox.isChecked()

        # Logika untuk ComboBox sudah benar karena menggunakan kunci yang stabil
        if "alignment" in self.comboboxes:
            state["alignment_algo"] = self.comboboxes["alignment"].currentText()
        if "super_resolution" in self.comboboxes:
            state["super_resolution_algo"] = self.comboboxes[
                "super_resolution"
            ].currentText()
        if "denoising" in self.comboboxes:
            state["denoising_algo"] = self.comboboxes["denoising"].currentText()

        return state

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

        # 1. Selalu buat label, tapi teks awalnya bisa kosong atau placeholder.
        #    Ini memastikan self.batch_info_label selalu ada.
        initial_label_text = ""
        if self.sequential_batch_number is not None:
            # Jika nomor sudah ada saat init (meskipun sekarang tidak), gunakan.
            initial_label_text = language_config.BATCH_LABEL_FORMAT.format(
                self.sequential_batch_number, self.image_count_in_batch
            )

        self.batch_info_label = QLabel(initial_label_text)

        # 2. Atur style untuk label ini
        self.batch_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.batch_info_label.setFont(font)
        self.batch_info_label.setStyleSheet(
            """
            QLabel {
                background-color: #607D8B;
                color: white;
                padding: 3px 5px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
        """
        )

        # 3. Tambahkan widget yang benar ke layout
        algorithm_area_v_layout.addWidget(self.batch_info_label)

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
        add_button.setIcon(
            QIcon("pixel_refine_desktop/ui/resources/assets/icons/add-image.png")
        )
        add_button.setIconSize(QSize(25, 25))
        add_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50; 
                border-radius: 5px; 
                color: white; 
                font-weight: semi-bold;
            }
            QPushButton:hover {
                background-color: #347A36;
            }
        """
        )
        add_button.setToolTip(language_config.ADD_IMAGE_BUTTON)
        add_button.clicked.connect(
            lambda: handle_add_image_to_batch(
                self.parent_widget,
                self.database_manager,
                self.thumbnail_threads,
                self.batch_id,
                list_layout,
            )
        )

        # Tombol Preview
        preview_button = QPushButton()
        preview_button.setFixedSize(30, 30)
        preview_button.setIcon(
            QIcon("pixel_refine_desktop/ui/resources/assets/icons/play-preview.png")
        )
        preview_button.setIconSize(QSize(15, 15))
        preview_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FFA500; 
                border-radius: 5px; 
                color: white; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #CC8400;
            }
        """
        )

        preview_button.setToolTip(language_config.PREVIEW_IMAGE_BUTTON)
        preview_button.clicked.connect(self.process_and_preview)

        # Tombol Delete
        delete_button = QPushButton()
        delete_button.setFixedSize(30, 30)
        delete_button.setIcon(
            QIcon("pixel_refine_desktop/ui/resources/assets/icons/delete-image.png")
        )
        delete_button.setStyleSheet(
            """
            QPushButton {
                background-color: #F44336; 
                border-radius: 5px; 
                color: white; 
                font-weight: semi-bold;
            }
            QPushButton:hover {
                background-color: #B9332A;
            }
        """
        )
        delete_button.setToolTip(language_config.DELETE_IMAGE_BUTTON)
        delete_button.clicked.connect(
            lambda: self.parent_widget.handle_delete_individual_batch(self.batch_id)
        )

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
        alignment_options = get_algorithm_options("alignment")
        algorithm_alignment = QComboBox()
        algorithm_alignment.setStyleSheet(DROPDOWN_BOX + override_style)
        for name, _ in alignment_options:
            algorithm_alignment.addItem(name)
        algorithm_alignment.setVisible(False)

        # --- Super Resolution Dropdown ---
        super_res_options = get_algorithm_options("super_resolution")
        super_res_combo = QComboBox()
        super_res_combo.setStyleSheet(DROPDOWN_BOX + override_style)
        for name, _ in super_res_options:
            super_res_combo.addItem(name)
        super_res_combo.setVisible(False)

        # --- Denoising Dropdown ---
        denoising_options = get_algorithm_options("denoising")
        denoising_combox = QComboBox()
        denoising_combox.setStyleSheet(DROPDOWN_BOX + override_style)
        for name, _ in denoising_options:
            denoising_combox.addItem(name)
        denoising_combox.setVisible(False)

        # --- Simpan comboboxes dan atur state awal ---
        self.comboboxes["alignment"] = algorithm_alignment
        self.comboboxes["super_resolution"] = super_res_combo
        self.comboboxes["denoising"] = denoising_combox

        algorithm_alignment.setCurrentText(
            self.initial_state.get("alignment_algo", "None")
        )
        super_res_combo.setCurrentText(
            self.initial_state.get("super_resolution_algo", "None")
        )
        denoising_combox.setCurrentText(
            self.initial_state.get("denoising_algo", "None")
        )

        # --- Hubungkan sinyal ---
        algorithm_alignment.currentIndexChanged.connect(
            lambda index: self.execute_algorithm(
                "alignment", algorithm_alignment.currentText()
            )
        )
        super_res_combo.currentIndexChanged.connect(
            lambda index: self.execute_algorithm(
                "super_resolution", super_res_combo.currentText()
            )
        )
        denoising_combox.currentIndexChanged.connect(
            lambda index: self.execute_algorithm(
                "denoising", denoising_combox.currentText()
            )
        )

        return algorithm_alignment, super_res_combo, denoising_combox

    def execute_algorithm(self, category, selected_algo):
        """Simpan pilihan algoritma dan update JSON secara realtime."""
        self.selected_algorithms[category] = selected_algo
        print(
            language_config.CONSOL_LOG_RUNNING_ALGORITHM.format(category, selected_algo)
        )

        if hasattr(self, "batch_id") and self.batch_id is not None:
            self._save_state_to_json(self.batch_id)

    def _handle_denoising_state_changed(self, is_checked):
        """Logika eksklusif saat state checkbox Denoising berubah."""
        superres_checkbox = self.checkboxes.get(
            language_config.PARAMETER_BATCH_SUPER_RESOLUTION
        )
        if not superres_checkbox:
            return

        if is_checked:
            superres_checkbox.blockSignals(True)
            superres_checkbox.setChecked(False)
            superres_checkbox.blockSignals(False)
        else:
            superres_checkbox.setEnabled(True)

    def _handle_superres_state_changed(self, is_checked):
        """Logika eksklusif saat state checkbox Super Resolution berubah."""
        denoising_checkbox = self.checkboxes.get(
            language_config.PARAMETER_BATCH_DENOISING
        )
        if not denoising_checkbox:
            return

        if is_checked:
            denoising_checkbox.blockSignals(True)
            denoising_checkbox.setChecked(False)
            denoising_checkbox.blockSignals(False)
        else:
            denoising_checkbox.setEnabled(True)

    def _save_state_to_json(self, batch_id):
        """Simpan state checkbox dan combobox untuk batch_id ke dalam file JSON."""
        json_path = os.path.join("database", "align", "batch_parameter.json")
        state = self.get_current_state()

        # Baca data lama jika ada
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                all_batches = json.load(f)
        else:
            all_batches = {}

        all_batches[str(batch_id)] = state

        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w") as f:
            json.dump(all_batches, f, indent=4)

    def _trigger_exclusive_handler(self, checkbox_key):
        """Dipanggil oleh klik label atau toggle checkbox untuk memicu logika eksklusif."""
        checkbox = self.checkboxes.get(checkbox_key)
        if not checkbox:
            return

        is_checked = checkbox.isChecked()

        if checkbox_key == language_config.PARAMETER_BATCH_DENOISING:
            self._handle_denoising_state_changed(is_checked)
        elif checkbox_key == language_config.PARAMETER_BATCH_SUPER_RESOLUTION:
            self._handle_superres_state_changed(is_checked)
        elif checkbox_key == language_config.PARAMETER_BATCH_CROP_EDGE:
            self._handle_crop_keep_edge(
                is_checked, checkbox_key, language_config.PARAMETER_BATCH_KEEP_EDGE
            )
        elif checkbox_key == language_config.PARAMETER_BATCH_KEEP_EDGE:
            self._handle_crop_keep_edge(
                is_checked, checkbox_key, language_config.PARAMETER_BATCH_CROP_EDGE
            )

        self._update_visibility_internal()

        # Simpan state terbaru ke JSON berdasarkan batch_id (pastikan Anda punya self.batch_id)
        if hasattr(self, "batch_id"):
            self._save_state_to_json(self.batch_id)

    def _handle_crop_keep_edge(self, is_checked, changed_cb_key, other_cb_key):
        """Logika eksklusif untuk Crop Edge dan Keep Edge."""
        changed_cb = self.checkboxes.get(changed_cb_key)
        other_cb = self.checkboxes.get(other_cb_key)
        align_cb = self.checkboxes.get(language_config.PARAMETER_BATCH_ALIGNMENT)
        if not changed_cb or not other_cb or not align_cb:
            return

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
        algorithm_alignment = self.comboboxes.get("alignment")
        super_res_combo = self.comboboxes.get("super_resolution")
        denoising_combox = self.comboboxes.get("denoising")

        # Kunci checkbox
        alignment_key = language_config.PARAMETER_BATCH_ALIGNMENT
        denoising_key = language_config.PARAMETER_BATCH_DENOISING
        superres_key = language_config.PARAMETER_BATCH_SUPER_RESOLUTION
        align_folder_key = language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER
        crop_edge_key = language_config.PARAMETER_BATCH_CROP_EDGE
        keep_edge_key = language_config.PARAMETER_BATCH_KEEP_EDGE

        # Dapatkan status checked dengan aman
        is_alignment_checked = self.checkboxes.get(
            alignment_key, QCheckBox()
        ).isChecked()
        is_denoising_checked = self.checkboxes.get(
            denoising_key, QCheckBox()
        ).isChecked()
        is_superres_checked = self.checkboxes.get(superres_key, QCheckBox()).isChecked()
        is_crop_edge_checked = self.checkboxes.get(
            crop_edge_key, QCheckBox()
        ).isChecked()
        is_keep_edge_checked = self.checkboxes.get(
            keep_edge_key, QCheckBox()
        ).isChecked()

        # Atur Visibilitas ComboBox/Tombol
        if algorithm_alignment:
            algorithm_alignment.setVisible(is_alignment_checked)
        if denoising_combox:
            denoising_combox.setVisible(is_denoising_checked)
        if super_res_combo:
            super_res_combo.setVisible(is_superres_checked)

        align_folder_cb = self.checkboxes.get(align_folder_key)
        if align_folder_cb:
            align_folder_cb.setEnabled(is_alignment_checked)

        crop_edge_cb = self.checkboxes.get(crop_edge_key)
        if crop_edge_cb:
            crop_edge_cb.setEnabled(is_alignment_checked and not is_keep_edge_checked)

        keep_edge_cb = self.checkboxes.get(keep_edge_key)
        if keep_edge_cb:
            keep_edge_cb.setEnabled(is_alignment_checked and not is_crop_edge_checked)

    def process_all_batch(self, progress_callback=None):
        """
        Jalankan semua algoritma yang dipilih untuk self.batch_id.
        Fungsi ini sekarang menerima 'progress_callback' untuk melaporkan status
        sub-proses kembali ke thread pemanggil tanpa membuat UI baru.
        """
        # --- Langkah 0: Pemeriksaan Awal ---
        if self.batch_id is None:
            print("[ERROR] process_all_batch called with no batch_id.")
            return

        # --- Langkah 1: Verifikasi Batch ID terhadap Database Manager ---
        try:
            images_in_db = self.database_manager.get_images_by_batch(self.batch_id)
            if not images_in_db:
                print(
                    f"[WARN] No images found in database for batch_id: {self.batch_id}. Skipping."
                )
                return
        except Exception as e:
            print(
                f"[ERROR] Database verification failed for batch_id: {self.batch_id}. Error: {e}"
            )
            return

        # --- Langkah 2: Baca Konfigurasi dari File JSON ---
        json_path = os.path.join("database", "align", "batch_parameter.json")
        config_from_json = {}

        if os.path.exists(json_path):
            all_batches_in_json = load_json_state(json_path)
            config_from_json = all_batches_in_json.get(str(self.batch_id), {})
            if not config_from_json:
                print(
                    f"[WARN] No configuration found in batch_parameter.json for batch_id: {self.batch_id}. Skipping."
                )
                return

        # --- Langkah 3: Definisikan Aksi Algoritma ---
        actions = {
            "alignment": {
                "Farneback Optical Flow": lambda: running_farneback_optical_flow(
                    self,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "AKAZE": lambda: running_akaze(
                    self,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "ORB": lambda: running_orb(
                    self,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "Light Glue": lambda: running_light_glue(
                    self,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "No Alignment": lambda: print(
                    "[INFO] Alignment: 'No Alignment' selected, no action."
                ),
                "None": lambda: print("[INFO] Alignment: 'None' selected, no action."),
            },
            "super_resolution": {
                # "Interpolation": lambda: running_interpolation(self, single_process=False, batch_id=self.batch_id, progress_callback=progress_callback),
                "No Super Resolution": lambda: print(
                    "[INFO] Super Resolution: 'No Super Resolution' selected, no action."
                ),
                "None": lambda: print(
                    "[INFO] Super Resolution: 'None' selected, no action."
                ),
            },
            "denoising": {
                "Average": lambda: running_average(
                    self,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "Median": lambda: running_median(
                    self,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                "Similarity": lambda: running_similarity(
                    self,
                    single_process=False,
                    batch_id=self.batch_id,
                    progress_callback=progress_callback,
                ),
                # "Similarity V2": lambda: running_similarity_v2(self, single_process=False, batch_id=self.batch_id, progress_callback=progress_callback),
                "No Denoising": lambda: print(
                    "[INFO] Denoising: 'No Denoising' selected, no action."
                ),
                "None": lambda: print("[INFO] Denoising: 'None' selected, no action."),
            },
        }

        category_to_json_checkbox_key = {
            "alignment": "checkbox_align_images",
            "super_resolution": "checkbox_super_resolution",
            "denoising": "checkbox_denoising",
        }

        # --- Langkah 4: Jalankan Algoritma Berdasarkan Konfigurasi JSON ---
        any_algorithm_executed = False
        for category, selected_algo_name in self.selected_algorithms.items():
            json_checkbox_key = category_to_json_checkbox_key.get(category)

            if not json_checkbox_key:
                continue

            if config_from_json.get(json_checkbox_key, False):
                # Cek untuk nama algoritma yang valid untuk diproses
                if selected_algo_name and selected_algo_name not in [
                    "None",
                    "No Alignment",
                    "No Super Resolution",
                    "No Denoising",
                ]:

                    if category in actions and selected_algo_name in actions[category]:
                        print(
                            f"[INFO] Executing '{selected_algo_name}' for batch_id: {self.batch_id}"
                        )
                        actions[category][selected_algo_name]()
                        any_algorithm_executed = True
                    else:
                        print(
                            f"[WARN] Algorithm '{selected_algo_name}' for category '{category}' not found in actions."
                        )

        if not any_algorithm_executed:
            print(
                f"[INFO] No algorithms were executed for batch_id: {self.batch_id} based on config."
            )
            pass

    def create_parameter_panel(self):
        """
        Buat panel parameter yang berisi combo box dan checkbox.
        Diperbaiki untuk menggunakan pemetaan kunci yang stabil untuk penyimpanan state.
        """
        algorithm_panel = QWidget()
        algorithm_panel.setStyleSheet("background-color: #EBEAEA")
        algorithm_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        parameter_layout = QHBoxLayout(algorithm_panel)
        parameter_layout.setContentsMargins(10, 10, 10, 10)

        algorithm_layout = QVBoxLayout()
        algorithm_layout.setContentsMargins(5, 5, 5, 5)
        algorithm_layout.setSpacing(5)

        algorithm_alignment, super_res_combo, denoising_combox = (
            self.dropdown_box_control()
        )

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

        # --- PERBAIKAN 1: Definisikan pemetaan dari teks label ke kunci JSON yang stabil ---
        self.label_to_key_map = {
            language_config.PARAMETER_BATCH_ALIGNMENT: "checkbox_align_images",
            language_config.PARAMETER_BATCH_ALIGNMENT_TO_FOLDER: "checkbox_save_alignment_to_folder",
            language_config.PARAMETER_BATCH_DENOISING: "checkbox_denoising",
            language_config.PARAMETER_BATCH_SUPER_RESOLUTION: "checkbox_super_resolution",
            language_config.PARAMETER_BATCH_CROP_EDGE: "checkbox_crop_edges",
            language_config.PARAMETER_BATCH_KEEP_EDGE: "checkbox_keep_edges",
        }

        # Gunakan keys dari map untuk iterasi agar konsisten
        checkbox_texts = list(self.label_to_key_map.keys())

        # Ambil referensi kunci untuk logika selanjutnya
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
            option_checkbox.setStyleSheet(CHECKBOX_SWITCH_STYLE)
            option_label = ClickableLabel(text)
            option_label.setWordWrap(True)
            option_label.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
            )
            option_label.clicked.connect(option_checkbox.toggle)

            self.checkboxes[text] = option_checkbox
            checkbox_widgets[text] = checkbox_widget

            # --- PERBAIKAN 2: Gunakan pemetaan untuk mendapatkan kunci yang benar saat memuat state ---
            key_for_state = self.label_to_key_map.get(
                text
            )  # Mengambil kunci stabil, misal "checkbox_align_images"
            if key_for_state:
                initial_checked = self.initial_state.get(key_for_state, False)
                option_checkbox.setChecked(initial_checked)

            current_key = text
            option_label.clicked.connect(
                lambda key=current_key: self._trigger_exclusive_handler(key)
            )
            option_checkbox.toggled.connect(
                lambda checked, key=current_key: self._trigger_exclusive_handler(key)
            )

            checkbox_layout.addWidget(option_checkbox)
            checkbox_layout.addWidget(option_label, 1)
            option_layout.addWidget(checkbox_widget)

        if crop_edge_key in checkbox_widgets:
            checkbox_widgets[crop_edge_key].setVisible(False)
        if keep_edge_key in checkbox_widgets:
            checkbox_widgets[keep_edge_key].setVisible(False)
        if align_folder_key in checkbox_widgets:
            checkbox_widgets[align_folder_key].setVisible(False)

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
        if alignment_key in self.checkboxes:
            self._update_visibility_internal()
        if align_folder_key in self.checkboxes:
            self._update_visibility_internal()

        return algorithm_panel
