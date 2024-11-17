from PyQt6.QtWidgets import QListWidget
from PyQt6.QtCore import Qt


class Sidebar(QListWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.addItems([
            "Import Images",
            "G. Alignment",
            "L. Alignment",
            "Stacking",
            "Tone Mapping",
            "Output",
            "Setting"
        ])
        self.setMaximumWidth(150)
        self.setStyleSheet("background-color: #f0f0f0; font-size: 14px;")
