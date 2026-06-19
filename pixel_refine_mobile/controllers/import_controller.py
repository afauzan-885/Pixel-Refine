"""
pixel_refine_mobile/controllers/import_controller.py
----------------------------------------------------
Import controller for image import operations.
Desktop equivalent: ImportExportController + ImportManager.
Mobile uses platform file picker instead of QFileDialog.
"""

from PySide6.QtCore import QObject, Signal
from pixel_refine_mobile.core_logic.database_manager import DatabaseManager


class ImportController(QObject):
    """Controller for image import operations."""

    import_started = Signal()
    import_progress = Signal(int, int)    # current, total
    import_completed = Signal(int)        # total imported count
    import_error = Signal(str)            # error message

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self._db = db_manager
        self._batch_repo = db_manager.get_batch_repo()

    def import_images(self, batch_id: int, image_paths: list):
        """
        Import images into a batch.
        On mobile, image_paths come from platform file picker.
        """
        if not image_paths:
            return

        self.import_started.emit()
        try:
            count = self._batch_repo.add_images(batch_id, image_paths)
            self.import_completed.emit(count)
        except Exception as e:
            self.import_error.emit(str(e))

    def validate_image_paths(self, paths: list) -> list:
        """Validate and filter image paths."""
        import os
        from pixel_refine_mobile.core.config import SUPPORTED_FORMATS

        valid = []
        all_extensions = []
        for exts in SUPPORTED_FORMATS.values():
            all_extensions.extend(exts)

        for path in paths:
            ext = os.path.splitext(path)[1].lower()
            if ext in all_extensions:
                valid.append(path)

        return valid
