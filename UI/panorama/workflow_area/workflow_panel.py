# workflow_panel.py

from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTabWidget,
    QComboBox,
)


class WorkflowPanel(QFrame):
    # Sinyal yang akan dikirim ke kelas koordinator
    setting_changed = Signal(str, str)  # key, value
    tab_changed = Signal(int)  # index
    preview_button_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("workflowContainer")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # --- Bagian Atas: Panel Tab ---
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.tab_changed.emit)

        alignment_content = self._create_alignment_tab_content()
        projection_content = self._create_projection_tab_content()
        blending_content = self._create_blending_tab_content()

        self.tab_widget.addTab(alignment_content, "Align gambar")
        self.tab_widget.addTab(projection_content, "Projection dan Crop")
        self.tab_widget.addTab(blending_content, "Blending")

        # --- Bagian Bawah: Area Tombol ---
        self.preview_button = QPushButton()
        self.preview_button.setVisible(False)
        self.preview_button.clicked.connect(self.preview_button_clicked.emit)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.preview_button)

        layout.addWidget(self.tab_widget, 3)
        layout.addLayout(button_layout, 1)

    # --- Metode untuk membuat konten tab ---
    def _create_alignment_tab_content(self):
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(QLabel("Alignment Algorithm:"))
        combo_layout = QHBoxLayout()
        self.combo_align = QComboBox()
        self.combo_align.addItems(["AKAZE", "ORB", "SIFT", "BRISK"])
        self.combo_align.currentTextChanged.connect(
            lambda v: self.setting_changed.emit("align_algorithm", v)
        )
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
            lambda v: self.setting_changed.emit("projection_type", v)
        )
        combo_layout.addWidget(self.combo_proj)
        combo_layout.addStretch()
        main_layout.addLayout(combo_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(QLabel("Set Region:"))
        button_layout = QHBoxLayout()
        button_layout.addWidget(QPushButton("Auto"))
        button_layout.addWidget(QPushButton("Manual"))
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
            lambda v: self.setting_changed.emit("blending_method", v)
        )
        combo_layout_1.addWidget(self.combo_blend)
        combo_layout_1.addStretch()
        main_layout.addLayout(combo_layout_1)
        main_layout.addSpacing(10)
        main_layout.addWidget(QLabel("Anti-ghosting:"))
        combo_layout_2 = QHBoxLayout()
        combo_ghost = QComboBox()
        combo_ghost.addItems(["None", "Simple", "Dynamic"])
        combo_layout_2.addWidget(combo_ghost)
        combo_layout_2.addStretch()
        main_layout.addLayout(combo_layout_2)
        main_layout.addStretch()
        return content

    # --- Metode Publik untuk dikontrol oleh WorkingLeftPanel ---
    
    def show_preview_button(self, visible):
        self.preview_button.setVisible(visible)

    def update_preview_button(self, icon_path, tooltip):
        self.preview_button.setText("")
        icon = QIcon(icon_path)
        self.preview_button.setIcon(icon)
        self.preview_button.setIconSize(QSize(32, 32))
        self.preview_button.setToolTip(tooltip)
        
    def get_current_tab_index(self):
        return self.tab_widget.currentIndex()

    def set_current_tab(self, index):
        self.tab_widget.setCurrentIndex(index)

    def update_tab_enabled_states(self, latest_stage):
        self.tab_widget.setTabEnabled(0, True)
        self.tab_widget.setTabEnabled(
            1, latest_stage in ["aligned", "projected", "blended"]
        )
        self.tab_widget.setTabEnabled(
            2, latest_stage in ["projected", "blended"]
        )
        
    def load_settings(self, settings: dict):
        if settings:
            self.combo_align.setCurrentText(settings.get("align_algorithm", "AKAZE"))
            self.combo_proj.setCurrentText(settings.get("projection_type", "Cylindrical"))
            self.combo_blend.setCurrentText(settings.get("blending_method", "Multi-band"))