from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox,
    QGraphicsView,
    QGraphicsScene,
    QVBoxLayout,
)

import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter

from .logic.workflow_process import process_algorithm
from .logic.image_handler import handle_import_button, handle_delete_button

from .logic.image_preview import (
    handler_zoom,
    update_preview_panel,
    fit_image_to_panel,
    scale_image,
    display_image,
    handle_image_ready,
    handle_image_error,
    image_status_info,
    start_image_processing
)
from .components.top_bar import TopBar
from .components.left_panel import LeftPanel
from .components.right_panel import RightPanel
from .components.progress_section import ProgressSection
from .logic.database_manager import DatabaseManager


class BurstDenoisingPage(QWidget):
    """Main Burst Denoising Page with modular components."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.database_manager = DatabaseManager("pixel_refine_database.db")
        self.database_manager.create_database()
        self.update_preview_enabled = True

        # Add TopBar
        self.top_bar = TopBar()
        self.layout.addWidget(self.top_bar)
        self.top_bar.import_button.clicked.connect(self.handle_import_button)
        self.top_bar.delete_button.clicked.connect(self.handle_delete_button)

        # Main Content
        self.main_layout = QHBoxLayout()
        
        self.left_panel = LeftPanel()
        self.right_panel = RightPanel()
        self.right_panel.setParent(self)
        self.main_layout.addWidget(self.left_panel, 2)
        self.main_layout.addWidget(self.right_panel, 2)
        self.layout.addLayout(self.main_layout)

        # Add ProgressSection
        self.progress_section = ProgressSection()
        self.layout.addWidget(self.progress_section)
        self.progress_section.process_clicked.connect(self.process_algorithm)

        # Setup graphics view and scene for preview panel
        self.preview_scene = QGraphicsScene()
        self.preview_view = QGraphicsView(self.preview_scene)
        self.preview_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_view.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.preview_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.preview_view.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.preview_view.setStyleSheet(
            "background-color: #f0f0f0; margin-left: 5px; border: none"
        )  # Optional for visual distinction
        self.preview_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.preview_view.viewport().installEventFilter(self)

        # Zoom-related attributes
        self.zoom_scale = 1.0
        self.original_pixmap = None
        self.drag_start_pos = None

        # Initialize managers
        self.multi_thread_import_images = None

        # Add the graphics view to the left panel
        self.left_panel.preview_panel_widget.layout().addWidget(self.preview_view)

    def update_preview_panel(self, selected_paths):
        update_preview_panel(self, selected_paths)
   
    def start_image_processing(self, selected_paths):
        start_image_processing(self, selected_paths)
        
    def handle_image_ready(self, pixmap):
        handle_image_ready(self, pixmap)
        
    def handle_image_error(self, error_message):
        handle_image_error(self, error_message)
    
    def image_status_info(self, proxy):
        image_status_info(self, proxy)

    def pause_preview_update(self):
        """Temporarily disable preview panel updates."""
        self.update_preview_enabled = False

    def resume_preview_update(self):
        """Re-enable preview panel updates."""
        self.update_preview_enabled = True

    def fit_image_to_panel(self):
        fit_image_to_panel(self)

    def resizeEvent(self, event):
        """Handles window resizing by adjusting the image size to fit the preview panel.
            This method ensures the image remains scaled according to the new window size."""
        super().resizeEvent(event)
        self.fit_image_to_panel()

    def scale_image(self):
        scale_image(self)

    def display_image(self, pixmap):
        display_image(self, pixmap)

    def eventFilter(self, source, event):
        return handler_zoom(self, source, event) or super().eventFilter(source, event)

    def handle_import_button(self):
        handle_import_button(self)

    def handle_delete_button(self):
        handle_delete_button(self)
        
    def process_algorithm(self):
        process_algorithm(self)
     
    def update_progress_bar(self, value, images_left):
        """
        Updates the progress bar and displays remaining images.
        """
        self.progress_section.progress_bar.setValue(value)
        self.progress_section.progress_bar.setFormat(
            f"{value}% ({images_left} images left)"
        )

    def on_import_complete(self, successful_images):
        """
        Called when the import process is complete.
        """
        self.right_panel.load_image_paths()
        QMessageBox.information(
            self,
            "Import Complete",
            f"{successful_images} images have been successfully imported.",
        )

        # Reset progress bar to 0%
        self.progress_section.progress_bar.setValue(0)
        self.progress_section.progress_bar.setFormat("0%")
