"""
Batch Page View (MVC Hybrid).
Wraps legacy BatchPageLayout while connecting to MVC controllers.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot
from pixel_refine_desktop.ui.components.batch_page import BatchPageLayout
from pixel_refine_desktop.controllers.batch_page_controller import BatchPageController
from pixel_refine_desktop.controllers.import_export_controller import (
    ImportExportController,
)
from pixel_refine_desktop.controllers.image_processing_controller import (
    ImageProcessingController,
)


class BatchPageView(QWidget):
    """
    Batch page view with MVC architecture.
    Wraps legacy BatchPageLayout but connects to controllers for business logic.
    """

    def __init__(self, db_path: str, parent=None):
        super().__init__(parent)
        self.db_path = db_path

        # Initialize controllers
        self.batch_controller = BatchPageController(db_path, self)
        self.import_export_controller = ImportExportController(self)
        self.processing_controller = ImageProcessingController(self)

        self.setup_ui()
        self.connect_controller_signals()

    def setup_ui(self):
        """Setup UI using legacy BatchPageLayout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Use legacy BatchPageLayout directly
        # This is a pragmatic approach for complex UI
        self.batch_layout = BatchPageLayout()
        layout.addWidget(self.batch_layout)

    def connect_controller_signals(self):
        """Connect controller signals to view updates."""
        # Batch controller signals
        self.batch_controller.batch_created.connect(self._on_batch_created)
        self.batch_controller.batch_updated.connect(self._on_batch_updated)
        self.batch_controller.batch_deleted.connect(self._on_batch_deleted)
        self.batch_controller.batch_error.connect(self._on_batch_error)

        # Processing signals
        self.processing_controller.workflow_completed.connect(
            self._on_workflow_completed
        )
        self.processing_controller.workflow_error.connect(self._on_workflow_error)

        # Connect legacy signals to controllers
        if hasattr(self.batch_layout, "data_changed"):
            self.batch_layout.data_changed.connect(self._on_data_changed)

    # Delegate methods to legacy layout
    def handle_batch_import_button(self):
        """Handle batch import button."""
        if hasattr(self.batch_layout, "handle_batch_import_button"):
            self.batch_layout.handle_batch_import_button()

    def handle_delete_all_batches(self):
        """Handle delete all batches."""
        if hasattr(self.batch_layout, "handle_delete_all_batches"):
            self.batch_layout.handle_delete_all_batches()

    def process_all_batches(self):
        """Handle process all batches."""
        if hasattr(self.batch_layout, "process_all_batches"):
            self.batch_layout.process_all_batches()

    # Signal handlers from controllers
    def _on_batch_created(self, batch_id: int, batch_name: str):
        """Handle batch creation."""
        print(f"✅ Batch created via controller: {batch_name} (ID: {batch_id})")
        # Refresh legacy UI
        if hasattr(self.batch_layout, "data_changed"):
            self.batch_layout.data_changed.emit()

    def _on_batch_updated(self, batch_id: int):
        """Handle batch update."""
        print(f"✅ Batch updated: ID {batch_id}")
        if hasattr(self.batch_layout, "data_changed"):
            self.batch_layout.data_changed.emit()

    def _on_batch_deleted(self, batch_id: int):
        """Handle batch deletion."""
        print(f"✅ Batch deleted: ID {batch_id}")
        if hasattr(self.batch_layout, "data_changed"):
            self.batch_layout.data_changed.emit()

    def _on_batch_error(self, error: str):
        """Handle batch error."""
        print(f"❌ Batch error: {error}")
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(self, "Batch Error", error)

    def _on_workflow_completed(self, result_path: str):
        """Handle workflow completion."""
        print(f"✅ Workflow completed: {result_path}")
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self, "Processing Complete", f"Result saved to:\n{result_path}"
        )

    def _on_workflow_error(self, error: str):
        """Handle workflow error."""
        print(f"❌ Workflow error: {error}")
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(self, "Processing Error", error)

    def _on_data_changed(self):
        """Handle data changed from legacy layout."""
        print("📊 Batch data changed")
