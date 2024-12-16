from PyQt6.QtWidgets import QWidget, QHBoxLayout, QProgressBar, QPushButton, QFileDialog
from PyQt6.QtCore import pyqtSignal

class ProgressSection(QWidget):
    process_clicked  = pyqtSignal()
    save_as_clicked = pyqtSignal()
    
    """Progress bar and control buttons."""
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 5px;
                background-color: #f0f0f0;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #80C4E9;
                width: 20px;
            }
        """)

        self.next_button = QPushButton("Next")
        self.process_button = QPushButton("Process")
        self.save_as_button = QPushButton("Save As")
     
        self.layout.addWidget(self.progress_bar, 4)
        self.layout.addWidget(self.next_button, 1)
        self.layout.addWidget(self.process_button, 1)
        self.layout.addWidget(self.save_as_button, 1)
        
        self.process_button.clicked.connect(self.process_clicked)
    