from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout
)
from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.panorama.working_left_panel import WorkingLeftPanel
from UI.panorama.working_right_panel import WorkingRightPanel
from UI.resources.stylesheet.stylesheet import stylesheet_panorama_page

class PanoramaPage(QMainWindow):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.database_manager = database_manager
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Fungsi _create_main_content sekarang hanya merakit komponen
        main_content = self._create_main_content()
        main_layout.addWidget(main_content)
        
        # Stylesheet tetap di sini karena berlaku global untuk halaman ini
        self.setStyleSheet(stylesheet_panorama_page())

    def _create_main_content(self):
        """
        Menghubungkan komponen modular dan mengatur komunikasi antar mereka.
        """
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)

        # === PERUBAHAN: Berikan database_manager ke KEDUA panel ===
        left_panel = WorkingLeftPanel(database_manager=self.database_manager)
        right_panel = WorkingRightPanel(database_manager=self.database_manager)
        
        # === Hubungkan komunikasi antar panel ===
        # 1. Saat pilihan proyek berubah di kanan, perbarui kiri.
        right_panel.project_selection_changed.connect(left_panel.update_display_for_project)
        right_panel.project_selection_cleared.connect(left_panel.clear_display)
        
        # 2. Saat judul di kiri di-double-click, minta kanan untuk me-rename.
        left_panel.rename_project_requested.connect(right_panel.handle_rename_request)
        
        main_layout.addWidget(left_panel, 3)
        main_layout.addWidget(right_panel, 1)

        return content_widget