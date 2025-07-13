from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QComboBox,
)


class WorkflowPanel(QWidget):
    setting_changed = Signal(str, str)  
    preview_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.latest_successful_stage = "grid"
        self._setup_ui()
        self.setVisible(False)

    def _setup_ui(self):
        """Membangun semua elemen UI statis untuk panel workflow."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        self.setObjectName("workflowContainer")

        # Panel Tab
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self._update_preview_button_state)
        self.tab_widget.addTab(self._create_alignment_tab_content(), "Align gambar")
        self.tab_widget.addTab(
            self._create_projection_tab_content(), "Projection dan Crop"
        )
        self.tab_widget.addTab(self._create_blending_tab_content(), "Blending")

        # Tombol Aksi (Preview)
        self.preview_button = QPushButton()
        self.preview_button.setVisible(False)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.preview_button)

        main_layout.addWidget(self.tab_widget, 3)
        main_layout.addLayout(button_layout, 1)

    def _create_alignment_tab_content(self):
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(QLabel("Alignment Algorithm:"))
        self.combo_align = QComboBox()
        self.combo_align.addItems(["AKAZE", "ORB", "SIFT", "BRISK"])
        self.combo_align.currentTextChanged.connect(
            lambda v: self._on_workflow_setting_changed(v, "align_algorithm")
        )
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(self.combo_align)
        combo_layout.addStretch()
        main_layout.addLayout(combo_layout)
        return content

    def _create_projection_tab_content(self):
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(QLabel("Projection Type:"))
        combo_layout = QHBoxLayout()
        self.combo_proj = QComboBox()
        self.combo_proj.addItems(["Planar", "Cylindrical", "Spherical", "Fisheye"])
        self.combo_proj.currentTextChanged.connect(
            lambda v: self._on_workflow_setting_changed(v, "projection_type")
        )
        combo_layout.addWidget(self.combo_proj)
        combo_layout.addStretch()
        main_layout.addLayout(combo_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(QLabel("Set Region:"))
        button_layout = QHBoxLayout()
        btn_auto = QPushButton("Auto")
        btn_manual = QPushButton("Manual")
        button_layout.addWidget(btn_auto)
        button_layout.addWidget(btn_manual)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        return content

    def _create_blending_tab_content(self):
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(QLabel("Blending Method:"))
        combo_layout_1 = QHBoxLayout()
        self.combo_blend = QComboBox()
        self.combo_blend.addItems(["Multi-band", "Feathering", "No Blending"])
        self.combo_blend.currentTextChanged.connect(
            lambda v: self._on_workflow_setting_changed(v, "blending_method")
        )
        combo_layout_1.addWidget(self.combo_blend)
        combo_layout_1.addStretch()
        main_layout.addLayout(combo_layout_1)
        main_layout.addSpacing(10)
        main_layout.addWidget(QLabel("Anti-ghosting:"))
        combo_layout_2 = QHBoxLayout()
        combo_ghost = QComboBox()
        combo_ghost.addItems(
            ["None", "Simple", "Dynamic"]
        )  # Anda mungkin ingin menyimpan referensi ini juga
        combo_layout_2.addWidget(combo_ghost)
        combo_layout_2.addStretch()
        main_layout.addLayout(combo_layout_2)
        main_layout.addStretch()
        return content

    @Slot(dict)
    def load_settings(self, settings: dict):
        """Menerapkan pengaturan yang ada ke UI."""
        if settings:
            # Gunakan blok .blockSignals() agar tidak memicu sinyal `setting_changed` saat memuat
            self.combo_align.blockSignals(True)
            self.combo_proj.blockSignals(True)
            self.combo_blend.blockSignals(True)

            self.combo_align.setCurrentText(settings.get("align_algorithm", "AKAZE"))
            self.combo_proj.setCurrentText(
                settings.get("projection_type", "Cylindrical")
            )
            self.combo_blend.setCurrentText(
                settings.get("blending_method", "Multi-band")
            )

            self.combo_align.blockSignals(False)
            self.combo_proj.blockSignals(False)
            self.combo_blend.blockSignals(False)

    @Slot(str)
    def update_workflow_stage(self, stage: str, has_images: bool):
        """Memperbarui state UI berdasarkan progres."""
        self.latest_successful_stage = stage
        self._update_tab_states()
        self.preview_button.setVisible(has_images)
        self._update_preview_button_state()

    # --- Logika Internal ---

    def _update_tab_states(self):
        """Mengaktifkan/menonaktifkan tab berdasarkan progres workflow."""
        self.tab_widget.setTabEnabled(0, True)
        self.tab_widget.setTabEnabled(
            1, self.latest_successful_stage in ["aligned", "projected", "blended"]
        )
        self.tab_widget.setTabEnabled(
            2, self.latest_successful_stage in ["projected", "blended"]
        )

    def _update_preview_button_state(self):
        """Mengubah ikon dan fungsi tombol preview."""
        actions = {
            0: {
                "name": "alignment",
                "icon": "UI/resources/icon/Align_Images.png",
                "tip": "Generate Alignment Preview",
            },
            1: {
                "name": "projection",
                "icon": "UI/resources/icon/Projection_crop.png",
                "tip": "Update Projection Preview",
            },
            2: {
                "name": "blending",
                "icon": "UI/resources/icon/Blending.png",
                "tip": "Update Blending Preview",
            },
        }
        action_info = actions.get(self.tab_widget.currentIndex())

        if action_info:
            self.preview_button.setText("")
            self.preview_button.setIcon(QIcon(action_info["icon"]))
            self.preview_button.setIconSize(QSize(32, 32))
            self.preview_button.setToolTip(action_info["tip"])

            try:
                self.preview_button.clicked.disconnect()
            except RuntimeError:
                pass

            # Hubungkan ke lambda yang memancarkan sinyal dengan nama tahap
            self.preview_button.clicked.connect(
                lambda: self.preview_requested.emit(action_info["name"])
            )
