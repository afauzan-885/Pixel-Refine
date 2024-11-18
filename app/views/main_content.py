from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class MainContent(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.pages = [
            "Import Images Page",
            "Global Alignment Page",
            "Local Alignment Page",
            "Stacking Page",
            "Tone Mapping Page",
            "Settings Page",
        ]

        for page_name in self.pages:
            self.addWidget(self.create_page(page_name))

    def create_page(self, text):
        """Create a placeholder page."""
        page = QWidget()
        layout = QVBoxLayout()
        label = QLabel(f"This is {text}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        page.setLayout(layout)
        return page
