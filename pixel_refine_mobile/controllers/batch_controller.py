"""
pixel_refine_mobile/controllers/batch_controller.py
----------------------------------------------------
Batch operations controller.
Desktop equivalent: BatchPageController.
Same signal contract for API parity.
"""

from PySide6.QtCore import QObject, Signal
from pixel_refine_mobile.core_logic.database_manager import DatabaseManager


class BatchController(QObject):
    """Controller for batch CRUD operations."""

    # Signals — IDENTICAL to desktop
    batch_created = Signal(int, str)    # batch_id, batch_name
    batch_updated = Signal(int)         # batch_id
    batch_deleted = Signal(int)         # batch_id
    batch_error = Signal(str)           # error_message
    images_added = Signal(int, int)     # batch_id, count
    images_removed = Signal(int, int)   # batch_id, count
    batch_selected = Signal(int)        # batch_id

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self._db = db_manager
        self._batch_repo = db_manager.get_batch_repo()

    def create_batch(self, name: str):
        """Create a new batch."""
        try:
            batch_id = self._batch_repo.create(name)
            if batch_id:
                self.batch_created.emit(batch_id, name)
            else:
                self.batch_error.emit(f"Failed to create batch '{name}'")
        except Exception as e:
            self.batch_error.emit(str(e))

    def delete_batch(self, batch_id: int):
        """Delete a batch."""
        try:
            self._batch_repo.delete(batch_id)
            self.batch_deleted.emit(batch_id)
        except Exception as e:
            self.batch_error.emit(str(e))

    def get_all_batches(self):
        """Get all batches."""
        return self._batch_repo.get_all()

    def get_batch_images(self, batch_id: int):
        """Get all images in a batch."""
        return self._batch_repo.get_batch_images(batch_id)

    def add_images_to_batch(self, batch_id: int, image_paths: list):
        """Add images to a batch."""
        try:
            count = self._batch_repo.add_images(batch_id, image_paths)
            if count > 0:
                self.images_added.emit(batch_id, count)
                self.batch_updated.emit(batch_id)
        except Exception as e:
            self.batch_error.emit(str(e))

    def handle_batch_selected(self, batch_id: int):
        """Handle batch selection."""
        self.batch_selected.emit(batch_id)

    def count_images_in_batch(self, batch_id: int) -> int:
        """Get number of images in a batch."""
        return self._batch_repo.count_images_in_batch(batch_id)
