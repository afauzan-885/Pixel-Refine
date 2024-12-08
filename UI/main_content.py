from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

# Import Komponen
from .burst_denoising.BurstDenoisingPage import BurstDenoisingPage


class Pages:
    BURST_DENOSING = "Burst Denoising"
    TONE_MAPPING = "Tone Mapping"
    SETTINGS = "Settings"


class MainContent(QStackedWidget):
    def __init__(self):
        super().__init__()

        # Peta halaman
        self.pages = {
            Pages.BURST_DENOSING: BurstDenoisingPage,
        }

        # halaman berdasarkan peta halaman
        for page_name in Pages.__dict__.keys():
            if not page_name.startswith("_"):
                page_label = getattr(Pages, page_name)
                page_class = self.pages.get(page_label)
                self.addWidget(self.Contents_page(page_label, page_class))

    def Contents_page(self, page_name, page_class):
        if page_class:
            return page_class()

        # Halaman default
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 150, 0, 0)
        layout.setSpacing(0)

        # Atur gaya untuk background dengan gradien warna pastel
        page.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread: pad,
                    x1: 1, y1: 0, x2: 0, y2: 1,
                    stop: 0 #D3D3D3, 
                    stop: 0.3 #A9A9A9, 
                    stop: 0.6 #E6E6E6   
                );
                border: none; 
                padding: 0; 
            }
        """)

        # Tambahkan ikon
        icon_label = QLabel()
        pixmap = QPixmap("UI/resources/image/system_updates-maintenance.png")
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("background: transparent;")  # Pastikan transparan
            layout.addWidget(icon_label)

        # Tambahkan teks
        label = QLabel(f"{page_name} menu under development")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            color: #555555;
            font-size: 22px;
            font-family: Arial, Helvetica, sans-serif;
            background: transparent; 
            margin-top: -200px;
        """)
        layout.addWidget(label)

        page.setLayout(layout)
        return page



