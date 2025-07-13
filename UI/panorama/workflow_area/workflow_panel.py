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

from UI.panorama.logic.DynamicFlowPanel import DynamicFlowPanel

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

        self.preview_button = QPushButton()
        self.preview_button.setVisible(False)
        
        self.preview_button.clicked.connect(self._on_preview_button_clicked)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.preview_button)
        
        # Panel Tab
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self._update_preview_button_state)
        self.tab_widget.addTab(self._create_alignment_tab_content(), "Align gambar")
        self.tab_widget.addTab(
            self._create_projection_tab_content(), "Projection dan Crop"
        )
        self.tab_widget.addTab(self._create_blending_tab_content(), "Blending")

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
            lambda value: self.setting_changed.emit("align_algorithm", value) # BENAR: Memancarkan sinyal
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
        
        # --- GRUP 1: Projection Type ---
        # Gunakan panel dinamis kita
        proj_panel = DynamicFlowPanel(horizontal_threshold=220)
        proj_panel.addWidget(QLabel("Projection Type:"))
        self.combo_proj = QComboBox()
        self.combo_proj.addItems(["Planar", "Cylindrical", "Spherical", "Fisheye"])
        self.combo_proj.currentTextChanged.connect(
            lambda value: self.setting_changed.emit("projection_type", value)
        )
        proj_panel.addWidget(self.combo_proj)
        main_layout.addWidget(proj_panel)

        main_layout.addSpacing(5)

        # --- GRUP 2: Set Region ---
        # Gunakan panel dinamis lagi
        region_panel = DynamicFlowPanel(horizontal_threshold=200)
        region_panel.addWidget(QLabel("Set Region:"))
        btn_auto = QPushButton("Auto")
        btn_manual = QPushButton("Manual")
        region_panel.addWidget(btn_auto)
        region_panel.addWidget(btn_manual)
        main_layout.addWidget(region_panel)

        main_layout.addStretch()
        return content

    def _create_blending_tab_content(self):
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- GRUP 1: Blending Method ---
        blend_panel = DynamicFlowPanel(horizontal_threshold=220)
        blend_panel.addWidget(QLabel("Blending Method:"))
        self.combo_blend = QComboBox()
        self.combo_blend.addItems(["Multi-band", "Feathering", "No Blending"])
        self.combo_blend.currentTextChanged.connect(
            lambda value: self.setting_changed.emit("blending_method", value)
        )
        blend_panel.addWidget(self.combo_blend)
        main_layout.addWidget(blend_panel)
        
        main_layout.addSpacing(10)

        # --- GRUP 2: Anti-ghosting ---
        ghost_panel = DynamicFlowPanel(horizontal_threshold=220)
        ghost_panel.addWidget(QLabel("Anti-ghosting:"))
        combo_ghost = QComboBox()
        combo_ghost.addItems(["None", "Simple", "Dynamic"])
        ghost_panel.addWidget(combo_ghost)
        main_layout.addWidget(ghost_panel)

        main_layout.addStretch()
        return content

    @Slot(dict)
    def load_settings(self, settings: dict):
        """Menerapkan pengaturan yang ada ke UI."""
        if settings:
            
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
            
    @Slot()
    def _on_preview_button_clicked(self):
        """Satu slot untuk menangani semua klik tombol preview."""
        current_index = self.tab_widget.currentIndex()
        
        if current_index == 0:
            stage_name = "alignment"
        elif current_index == 1:
            stage_name = "projection"
        elif current_index == 2:
            stage_name = "blending"
        else:
            return 
        
        self.preview_requested.emit(stage_name)

    @Slot(str)
    def update_workflow_stage(self, stage: str, has_images: bool):
        """Memperbarui state UI berdasarkan progres."""
        self.latest_successful_stage = stage
        self._update_tab_states()
        self.preview_button.setVisible(has_images)
        self._update_preview_button_state()

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
        """Mengubah HANYA ikon dan tooltip tombol preview."""
        actions = {
            0: {"icon": "UI/resources/icon/Align_Images.png", "tip": "Generate Alignment Preview"},
            1: {"icon": "UI/resources/icon/Projection_crop.png", "tip": "Update Projection Preview"},
            2: {"icon": "UI/resources/icon/Blending.png", "tip": "Update Blending Preview"},
        }
        action_info = actions.get(self.tab_widget.currentIndex())

        if action_info:
            self.preview_button.setText("")
            self.preview_button.setIcon(QIcon(action_info["icon"]))
            self.preview_button.setIconSize(QSize(32, 32))
            self.preview_button.setToolTip(action_info["tip"])
