from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QPushButton, QHBoxLayout, 
     QComboBox,  QFormLayout
)
from PySide6.QtCore import Signal

class ConfigPanel(QWidget):
    apply_clicked = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # ID PENTING untuk styling container bawah
        self.setObjectName("workflowContainer") 
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- Tab Widget ---
        self.tabs = QTabWidget()
        
        # Contoh Tab Align
        self.tab1 = QWidget()
        f1 = QFormLayout(self.tab1)
        self.cmb_method = QComboBox()
        self.cmb_method.addItems(["AKAZE", "SIFT", "ORB"])
        f1.addRow("Feature Matching:", self.cmb_method)
        self.tabs.addTab(self.tab1, "Alignment")
        
        # Contoh Tab Projection
        self.tab2 = QWidget()
        f2 = QFormLayout(self.tab2)
        f2.addRow("Projection Type:", QComboBox())
        self.tabs.addTab(self.tab2, "Projection")

        layout.addWidget(self.tabs)

        # --- Action Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # Tombol aksi kecil di panel bawah (biasanya ikon)
        self.btn_apply = QPushButton("Run Process")
        self.btn_apply.clicked.connect(self._on_apply)
        
        btn_layout.addWidget(self.btn_apply)
        layout.addLayout(btn_layout)

    def _on_apply(self):
        self.apply_clicked.emit({"method": self.cmb_method.currentText()})