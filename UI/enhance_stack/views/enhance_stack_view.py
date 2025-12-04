"""
Enhanced Stack Page View (MVC Refactored).
Main container for single and batch page views with controller integration.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt
from controllers.single_page_controller import SinglePageController
from controllers.batch_page_controller import BatchPageController
from controllers.image_processing_controller import ImageProcessingController
from controllers.import_export_controller import ImportExportController


class EnhanceStackView(QWidget):
    """
    Main view for enhance stack feature.
    Manages single and batch page views with MVC architecture.
    """
    
    def __init__(self, db_path: str, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        
        # Initialize controllers
        self.single_controller = SinglePageController(db_path, self)
        self.batch_controller = BatchPageController(db_path, self)
        self.processing_controller = ImageProcessingController(self)
        self.import_export_controller = ImportExportController(self)
        
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Setup the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget for switching between single and batch views
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # For now, add placeholder widgets
        # These will be replaced with actual SinglePageView and BatchPageView
        from PySide6.QtWidgets import QLabel
        
        single_placeholder = QLabel("Single Page View (MVC)\nControllers initialized and ready")
        single_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        single_placeholder.setStyleSheet("font-size: 16px; padding: 20px;")
        
        batch_placeholder = QLabel("Batch Page View (MVC)\nControllers initialized and ready")
        batch_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        batch_placeholder.setStyleSheet("font-size: 16px; padding: 20px;")
        
        self.stacked_widget.addWidget(single_placeholder)
        self.stacked_widget.addWidget(batch_placeholder)
        
        # Show single page by default
        self.stacked_widget.setCurrentIndex(0)
    
    def connect_signals(self):
        """Connect controller signals to view slots."""
        # Single page controller signals
        self.single_controller.import_completed.connect(self.on_import_completed)
        self.single_controller.import_error.connect(self.on_import_error)
        
        # Batch controller signals
        self.batch_controller.batch_created.connect(self.on_batch_created)
        self.batch_controller.batch_error.connect(self.on_batch_error)
        
        # Processing controller signals
        self.processing_controller.workflow_completed.connect(self.on_workflow_completed)
        self.processing_controller.workflow_error.connect(self.on_workflow_error)
    
    def switch_to_single_page(self):
        """Switch to single page view."""
        self.stacked_widget.setCurrentIndex(0)
    
    def switch_to_batch_page(self):
        """Switch to batch page view."""
        self.stacked_widget.setCurrentIndex(1)
    
    # Signal handlers
    def on_import_completed(self, count: int):
        """Handle import completion."""
        print(f"Import completed: {count} images")
    
    def on_import_error(self, error: str):
        """Handle import error."""
        print(f"Import error: {error}")
    
    def on_batch_created(self, batch_id: int, batch_name: str):
        """Handle batch creation."""
        print(f"Batch created: {batch_name} (ID: {batch_id})")
    
    def on_batch_error(self, error: str):
        """Handle batch error."""
        print(f"Batch error: {error}")
    
    def on_workflow_completed(self, result_path: str):
        """Handle workflow completion."""
        print(f"Workflow completed: {result_path}")
    
    def on_workflow_error(self, error: str):
        """Handle workflow error."""
        print(f"Workflow error: {error}")
