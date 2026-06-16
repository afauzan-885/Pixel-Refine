from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from pixel_refine_desktop.ui.views.panorama.working_left_panel import WorkingLeftPanel
from pixel_refine_desktop.ui.views.panorama.working_right_panel import WorkingRightPanel
from resources.styles.stylesheet import stylesheet_global_page


class PanoramaPage(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)

        # --- Inisialisasi Panel (Tanpa DB) ---
        self.left_panel = WorkingLeftPanel()
        self.right_panel = WorkingRightPanel()

        # --- Koneksi Antar Panel ---
        # Kanan (List) -> Kiri (Display)
        self.right_panel.project_selection_changed.connect(
            self.left_panel.update_display_for_project
        )
        self.right_panel.project_selection_cleared.connect(
            self.left_panel.clear_display
        )

        # Layouting
        main_layout.addWidget(self.left_panel, 3)
        main_layout.addWidget(self.right_panel, 1)

        # Apply Stylesheet
        self.setStyleSheet(stylesheet_global_page())
