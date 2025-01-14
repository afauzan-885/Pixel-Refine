from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QGraphicsView,
    QGraphicsScene,
    QVBoxLayout,
    QWidget
)
from PyQt6.QtCore import Qt

from UI.enhance_stack.logic.database_manager import DatabaseManager
from .components.left_panel import LeftPanel
from .components.right_panel import RightPanel
from .components.progress_section import ProgressSection
from UI.enhance_stack.logic.workflow_process import process_algorithm
from UI.settings.General.Language import language_config

from .logic.image_handler import handle_import_button, handle_delete_button
from .logic.image_preview import (
    update_preview_panel,
    fit_image_to_panel,
    display_image,
    handle_image_ready,
    handle_image_error,
    image_status_info,
    start_image_processing
)

class SinglePageLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.database_manager = DatabaseManager("pixel_refine_database.db")
        self.database_manager.create_database()

        self.layout = QVBoxLayout()

        # Create panels and layout
        self.single_page_layout = QHBoxLayout()

        self.left_panel = LeftPanel()
        self.right_panel = RightPanel()
        self.single_page_layout.addWidget(self.left_panel, 3)
        self.single_page_layout.addWidget(self.right_panel, 2)
        self.layout.addLayout(self.single_page_layout)

        # Add ProgressSection
        self.progress_section = ProgressSection()
        self.layout.addWidget(self.progress_section)
        self.progress_section.process_clicked.connect(self.process_algorithm)

        # Setup graphics view and scene for preview panel
        self.preview_scene = QGraphicsScene()
        self.preview_view = QGraphicsView(self.preview_scene)
        self.preview_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.preview_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.preview_view.setStyleSheet(
            "background-color: #f0f0f0; margin-left: 5px; border: none"
        )
        self.preview_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.preview_view.viewport().installEventFilter(self)

        # Initialize managers
        self.multi_thread_import_images = None

        # Add the graphics view to the left panel
        self.left_panel.preview_panel_widget.layout().addWidget(self.preview_view)

    def update_preview_panel(self, selected_paths):
        update_preview_panel(self, selected_paths)

    def start_image_processing(self, selected_paths):
        start_image_processing(self, selected_paths)

    def image_status_info(self, proxy):
        image_status_info(self, proxy)

    def handle_image_ready(self, pixmap):
        handle_image_ready(self, pixmap)

    def handle_image_error(self, error_message):
        handle_image_error(self, error_message)

    def display_image(self, pixmap):
        display_image(self, pixmap)

    def pause_preview_update(self):
        """Temporarily disable preview panel updates."""
        self.update_preview_enabled = False

    def resume_preview_update(self):
        """Re-enable preview panel updates."""
        self.update_preview_enabled = True

    def resizeEvent(self, event):
        """Handles window resizing by adjusting the image size to fit the preview panel."""
        super().resizeEvent(event)
        self.fit_image_to_panel()

    def fit_image_to_panel(self):
        fit_image_to_panel(self)

    def eventFilter(self, source, event):
        # Remove zoom handling
        return super().eventFilter(source, event)

    def handle_import_button(self):
        handle_import_button(self)

    def handle_delete_button(self):
        handle_delete_button(self)

    def process_algorithm(self):
        process_algorithm(self)

    def update_progress_bar(self, value, images_left):
        """Updates the progress bar and displays remaining images."""
        self.progress_section.progress_bar.setValue(value)
        self.progress_section.progress_bar.setFormat(
            language_config.UPDATE_PROGRESS_BAR_STATUS.format(value=value, images_left=images_left)
        )

    def on_import_complete(self, successful_images):
        """Called when the import process is complete."""
        self.right_panel.load_image_paths()
        QMessageBox.information(
            self,
            language_config.ON_IMPORT_COMPLETE_STATUS,
            language_config.ON_IMPORT_COMPLETE_MESSAGES.format(successful_images=successful_images)
        )
        self.progress_section.progress_bar.setValue(0)
        self.progress_section.progress_bar.setFormat("0%")
