"""
Single Page Controller.
Handles business logic for single page image processing operations.
"""

from PySide6.QtCore import QObject, Signal
from typing import List, Optional
from pixel_refine_desktop.models.data_access.image_repository import ImageRepository
from pixel_refine_desktop.models.image_model import ImageModel


class SinglePageController(QObject):
    """
    Controller for single page operations.
    Coordinates between view and model for single image processing.
    """

    # Signals for view communication
    progress_updated = Signal(int, int)  # (value, images_remaining)
    import_completed = Signal(int)  # (successful_count)
    import_error = Signal(str)  # (error_message)
    delete_completed = Signal(int)  # (deleted_count)
    processing_started = Signal()
    processing_completed = Signal(str)  # (result_path)
    processing_error = Signal(str)  # (error_message)
    save_completed = Signal(str)  # (saved_path)
    save_error = Signal(str)  # (error_message)

    def __init__(self, db_path: str, parent: Optional[QObject] = None):
        """
        Initialize controller.

        Args:
            db_path: Path to database
            parent: Parent QObject
        """
        super().__init__(parent)
        self.image_repo = ImageRepository(db_path)
        self.db_path = db_path

    def get_all_image_paths(self) -> List[str]:
        """
        Get all image paths from database.

        Returns:
            List of image file paths
        """
        images = self.image_repo.get_all()
        return [img[1] for img in images]  # Extract paths from tuples

    def validate_import_paths(self, paths: List[str]) -> tuple[List[str], List[str]]:
        """
        Validate import paths and check for duplicates.

        Args:
            paths: List of image paths to validate

        Returns:
            Tuple of (valid_unique_paths, duplicate_paths)
        """
        existing_paths = set(self.get_all_image_paths())
        duplicates = [p for p in paths if p in existing_paths]
        unique_paths = [p for p in paths if p not in existing_paths]

        return unique_paths, duplicates

    def delete_images(self, paths: List[str]) -> int:
        """
        Delete images from database.

        Args:
            paths: List of image paths to delete

        Returns:
            Number of images deleted
        """
        deleted_count = 0
        for path in paths:
            try:
                rows = self.image_repo.delete_by_path(path)
                deleted_count += rows
            except Exception as e:
                print(f"Error deleting image {path}: {e}")

        if deleted_count > 0:
            self.delete_completed.emit(deleted_count)

        return deleted_count

    def get_image_count(self) -> int:
        """
        Get total number of images.

        Returns:
            Image count
        """
        return self.image_repo.count()
