from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.resources.stylesheet.stylesheet import BLANK_CONTENT_BACKGROUND, BLANK_CONTENT_LABEL
from UI.settings.General.Language import language_config


from .enhance_stack.EnhanceStackPage import EnhanceStackPage
from .settings.SettingPage import SettingPage

class Pages:
    ENHANCE_STACK = "Enhance Stack"
    HDR_RECONTRUCTION = language_config.HDR_SIDEBAR_LABEL
    SETTINGS = language_config.SETTINGS_SIDEBAR_LABEL


class MainContent(QStackedWidget):
    def __init__(self, database_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager # Simpan referensi
        self.pages = {
            Pages.ENHANCE_STACK: EnhanceStackPage,
            Pages.SETTINGS: SettingPage,
        }

        # halaman berdasarkan peta halaman
        for page_name in Pages.__dict__.keys():
            if not page_name.startswith("_"):
                page_label = getattr(Pages, page_name)
                page_class = self.pages.get(page_label)
                self.addWidget(self.Contents_page(page_label, page_class, self.database_manager))

    def Contents_page(self, page_name, page_class, database_manager: DatabaseManager):
        if page_class:
            return page_class(database_manager)

        # Halaman default
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
            icon_label.setStyleSheet("background: transparent;")  # Pastikan transparan
            layout.addWidget(icon_label)

        # Tambahkan teks
        label = QLabel(language_config.UNDER_DEVELOPMENT.format(page_name=page_name))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(BLANK_CONTENT_LABEL)
        layout.addWidget(label)

        page.setLayout(layout)
        return page



