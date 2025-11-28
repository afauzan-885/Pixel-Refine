from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QComboBox, QFrame
)

from UI.panorama.logic.DynamicPanel import DynamicFlowPanel

class WorkflowPanel(QWidget):
    """
    Panel Bawah: Form Pengaturan.
    Murni Layout Widget. Semua Tab diaktifkan untuk demo UI.
    """
    setting_changed = Signal(str, str)  
    preview_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # --- Preview Button ---
        self.preview_button = QPushButton("Run Process (UI Only)")
        self.preview_button.clicked.connect(self._on_preview_clicked)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.preview_button)

        # --- Tab Widget ---
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_align_ui(), "Align")
        self.tab_widget.addTab(self._create_proj_ui(), "Projection")
        self.tab_widget.addTab(self._create_blend_ui(), "Blending")

        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(btn_layout)

    def _create_align_ui(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignLeft)
        
        # Group 1
        g1 = QVBoxLayout()
        g1.addWidget(QLabel("Feature Detector:"))
        cb1 = QComboBox()
        cb1.addItems(["AKAZE", "ORB", "SIFT"])
        g1.addWidget(cb1)
        layout.addLayout(g1)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Group 2
        g2 = QVBoxLayout()
        g2.addWidget(QLabel("Warping:"))
        cb2 = QComboBox()
        cb2.addItems(["Homography", "Affine"])
        g2.addWidget(cb2)
        layout.addLayout(g2)
        
        return widget

    def _create_proj_ui(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        panel = DynamicFlowPanel()
        panel.addWidget(QLabel("Projection Type:"))
        cb = QComboBox()
        cb.addItems(["Spherical", "Cylindrical", "Planar"])
        panel.addWidget(cb)
        
        layout.addWidget(panel)
        layout.addStretch()
        return widget

    def _create_blend_ui(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        panel = DynamicFlowPanel()
        panel.addWidget(QLabel("Blending Method:"))
        cb = QComboBox()
        cb.addItems(["Multi-band", "Feathering"])
        panel.addWidget(cb)
        
        layout.addWidget(panel)
        layout.addStretch()
        return widget

    def _on_preview_clicked(self):
        # Kirim nama tab yang sedang aktif
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        self.preview_requested.emit(current_tab)