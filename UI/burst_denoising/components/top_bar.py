from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton

class TopBar(QWidget):
    """Top bar with Import and Delete buttons."""
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.import_button = QPushButton("Import Image")
        self.import_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                font-size: 14px;
                background-color: #3498db;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                font-size: 14px;
                background-color: #e74c3c;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        self.layout.addWidget(self.import_button)
        self.layout.addStretch()
        self.layout.addWidget(self.delete_button)
