from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout
)
from pixel_refine_desktop.core.logic.database_manager import DatabaseManager
from pixel_refine_desktop.ui.views.panorama.working_left_panel import WorkingLeftPanel
from pixel_refine_desktop.ui.views.panorama.working_right_panel import WorkingRightPanel
from pixel_refine_desktop.ui.resources.styles.stylesheet import stylesheet_global_page

class PanoramaPage(QMainWindow):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.database_manager = database_manager
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_content = self._create_main_content()
        main_layout.addWidget(main_content)
        
        self.setStyleSheet(stylesheet_global_page())

    def _create_main_content(self):
        """
        Menghubungkan komponen modular dan mengatur komunikasi antar mereka.
        """
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)

        left_panel = WorkingLeftPanel(database_manager=self.database_manager)
        right_panel = WorkingRightPanel(database_manager=self.database_manager)
        
        right_panel.project_selection_changed.connect(left_panel.update_display_for_project)
        right_panel.project_selection_cleared.connect(left_panel.clear_display)
        left_panel.rename_project_requested.connect(right_panel.handle_rename_request)
        right_panel.project_list_updated.connect(left_panel.on_project_existence_changed)
        
        main_layout.addWidget(left_panel, 3)
        main_layout.addWidget(right_panel, 1)

        right_panel.load_projects_from_db()

        return content_widget