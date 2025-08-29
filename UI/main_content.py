from PySide6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from UI.enhance_stack.logic.database_manager import DatabaseManager
# from UI.panorama.PanoramaPage import PanoramaPage
from UI.resources.stylesheet.stylesheet import BLANK_CONTENT_BACKGROUND, BLANK_CONTENT_LABEL
from UI.settings.General.Language import language_config


from .enhance_stack.EnhanceStackPage import EnhanceStackPage
from .settings.SettingPage import SettingPage
class Pages:
    """
    Satu Sumber Kebenaran (Single Source of Truth) untuk semua halaman aplikasi.
    Setiap entri adalah tuple dengan format: (label, path_ikon, kelas_widget)
    Kelas widget bisa None jika halaman tersebut masih dalam pengembangan.
    """
    
    # Halaman yang muncul di bagian atas sidebar
    MAIN_PAGES = [
        ("Enhance Stack", "UI/resources/icon/enhance_stack.png", EnhanceStackPage),
        # (language_config.PANORAMA_SIDEBAR_LABEL, "UI/resources/icon/panorama.png", PanoramaPage),
        # Tambahkan halaman utama baru di sini
    ]

    # Halaman yang muncul di bagian bawah sidebar (setelah pemisah)
    FOOTER_PAGES = [
        (language_config.SETTINGS_SIDEBAR_LABEL, "UI/resources/icon/setting.png", SettingPage),
        # Tambahkan halaman footer baru di sini
    ]

    # Gabungan semua halaman untuk kemudahan MainContent dalam menjaga urutan.
    ALL_PAGES = MAIN_PAGES + FOOTER_PAGES

class MainContent(QStackedWidget):
    def __init__(self, database_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager

        # Hapus definisi 'self.pages' yang lama.
        # Langsung bangun widget dari sumber kebenaran (Pages.ALL_PAGES).
        # Urutan widget di sini akan SAMA PERSIS dengan urutan tombol di Sidebar.
        for page_config in Pages.ALL_PAGES:
            page_label, _, page_class = page_config # path ikon tidak diperlukan di sini
            
            # Buat dan tambahkan widget ke QStackedWidget
            self.addWidget(self.Contents_page(page_label, page_class, self.database_manager))

    def Contents_page(self, page_name, page_class, database_manager: DatabaseManager):
        if page_class:
            return page_class(database_manager)

        # Halaman default (kode ini tidak perlu diubah, sudah bagus)
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 150, 0, 0)
        layout.setSpacing(0)

        page.setStyleSheet(BLANK_CONTENT_BACKGROUND)

        # Tambahkan ikon
        icon_label = QLabel()
        pixmap = QPixmap("UI/resources/image/system_updates-maintenance.png")
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("background: transparent;")  
            layout.addWidget(icon_label)

        # Tambahkan teks
        label = QLabel(language_config.UNDER_DEVELOPMENT.format(page_name=page_name))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(BLANK_CONTENT_LABEL)
        layout.addWidget(label)

        page.setLayout(layout)
        return page
    