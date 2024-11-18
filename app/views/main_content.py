from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

# Import Komponen
from app.views.import_image.ImportImagesPage import ImportImagesPage
from app.views.global_alignment.GlobalAlignmentPage import GlobalAlignmentPage
from app.views.local_alignment.LocalAlignmentPage import LocalAlignmentPage


class Pages:
    IMPORT_IMAGES = "Import Images Page"
    GLOBAL_ALIGNMENT = "Global Alignment Page"
    LOCAL_ALIGNMENT = "Local Alignment Page"
    STACKING = "Stacking Page"
    TONE_MAPPING = "Tone Mapping Page"
    SETTINGS = "Settings Page"


class MainContent(QStackedWidget):
    def __init__(self):
        super().__init__()

        # Peta halaman
        self.pages = {
            Pages.IMPORT_IMAGES: ImportImagesPage,
            Pages.GLOBAL_ALIGNMENT: GlobalAlignmentPage,
            Pages.LOCAL_ALIGNMENT: LocalAlignmentPage,
        }

        for page_name, page_class in self.pages.items():
            self.addWidget(self.create_page(page_name, page_class))

    def create_page(self, page_name, page_class):

        # Cek apakah halaman ada di peta halaman
        if page_class:
            return page_class()

        # Jika halaman tidak ditemukan, tampilkan halaman default
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        label = QLabel(f"This is {page_name}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        page.setLayout(layout)
        return page
