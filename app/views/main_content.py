from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from app.views.import_image.ImportImagesPage import ImportImagesPage  # Mengimpor komponen ImportImagesPage
from app.views.global_alignment.GlobalAlignmentPage import GlobalAlignmentPage  # Mengimpor komponen GlobalAlignmentPage
from app.views.local_alignment.LocalAlignmentPage import LocalAlignmentPage  # Mengimpor komponen LocalAlignmentPage
# Anda dapat mengimpor halaman lainnya dengan cara yang sama


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

    def create_page(self, page_name):
        
        # komponen ImportImagesPage
        if page_name == "Import Images Page":
            return ImportImagesPage()

        # komponen GlobalAlignmentPage
        elif page_name == "Global Alignment Page":
            return GlobalAlignmentPage()

        # komponen LocalAlignmentPage
        elif page_name == "Local Alignment Page":
            return LocalAlignmentPage()

        # Jika halaman lainnya tidak modular, tampilkan halaman default
        page = QWidget()
        layout = QVBoxLayout()
        label = QLabel(f"This is {page_name}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        page.setLayout(layout)
        return page
