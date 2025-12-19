"""
Batch Page Controller.
Handles business logic for batch processing operations.
"""

from PySide6.QtCore import QObject, Signal
from typing import List, Optional, Dict
from pixel_refine_desktop.enhance_stack.models.data_access.batch_repository import (
    BatchRepository,
)
from pixel_refine_desktop.enhance_stack.models.batch_model import BatchModel
from pixel_refine_desktop.enhance_stack.models.image_model import ImageModel


class BatchPageController(QObject):
    """
    Controller for batch page operations.
    Coordinates between view and model for batch processing.
    """

    # Signals for view communication
    batch_created = Signal(int, str)  # (batch_id, batch_name)
    batch_updated = Signal(int)  # (batch_id)
    batch_deleted = Signal(int)  # (batch_id)
    batch_error = Signal(str)  # (error_message)

    images_added = Signal(int, int)  # (batch_id, count)
    images_removed = Signal(int, int)  # (batch_id, count)

    processing_started = Signal(int)  # (batch_id)
    processing_progress = Signal(int, int, int)  # (batch_id, current, total)
    processing_completed = Signal(int, str)  # (batch_id, result_path)
    processing_error = Signal(int, str)  # (batch_id, error_message)

    reference_changed = Signal(int, str)  # (batch_id, image_path)

    def __init__(self, db_path: str, parent: Optional[QObject] = None):
        """
        Initialize controller.

        Args:
            db_path: Path to database
            parent: Parent QObject
        """
        super().__init__(parent)
        self.batch_repo = BatchRepository(db_path)
        self.db_path = db_path

    def create_batch(self, batch_name: str) -> Optional[int]:
        """
        Create a new batch.

        Args:
            batch_name: Name for the batch

        Returns:
            Batch ID if successful, None otherwise
        """
        try:
            batch_id = self.batch_repo.create(batch_name)
            if batch_id:
                self.batch_created.emit(batch_id, batch_name)
                return batch_id
            else:
                self.batch_error.emit(f"Failed to create batch '{batch_name}'")
                return None
        except Exception as e:
            self.batch_error.emit(f"Error creating batch: {e}")
            return None

    def get_all_batches(self) -> List[BatchModel]:
        """
        Get all batches with their images.

        Returns:
            List of BatchModel instances
        """
        batches = []
        batch_rows = self.batch_repo.get_all()

        for batch_id, batch_name in batch_rows:
            # Get images for this batch
            image_rows = self.batch_repo.get_batch_images(batch_id)
            images = [
                ImageModel(id=img_id, path=path, is_reference=bool(is_ref))
                for img_id, path, is_ref in image_rows
            ]

            batch = BatchModel(id=batch_id, name=batch_name, images=images)
            batches.append(batch)

        return batches

    def get_batch(self, batch_id: int) -> Optional[BatchModel]:
        """
        Get a specific batch with its images.

        Args:
            batch_id: Batch ID

        Returns:
            BatchModel or None if not found
        """
        batch_row = self.batch_repo.get_by_id(batch_id)
        if not batch_row:
            return None

        batch_id, batch_name = batch_row

        # Get images
        image_rows = self.batch_repo.get_batch_images(batch_id)
        images = [
            ImageModel(id=img_id, path=path, is_reference=bool(is_ref))
            for img_id, path, is_ref in image_rows
        ]

        return BatchModel(id=batch_id, name=batch_name, images=images)

    def delete_batch(self, batch_id: int) -> bool:
        """
        Delete a batch.

        Args:
            batch_id: Batch ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            rows = self.batch_repo.delete(batch_id)
            if rows > 0:
                self.batch_deleted.emit(batch_id)
                return True
            return False
        except Exception as e:
            self.batch_error.emit(f"Error deleting batch: {e}")
            return False

    def update_batch_name(self, batch_id: int, new_name: str) -> bool:
        """
        Update the name of a batch.

        Args:
            batch_id: The ID of the batch to update.
            new_name: The new name for the batch.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Basic validation
            if not new_name or not new_name.strip():
                self.batch_error.emit("Batch name cannot be empty.")
                return False
            if len(new_name) > 128:
                self.batch_error.emit("Batch name cannot exceed 128 characters.")
                return False

            rows = self.batch_repo.update_name(batch_id, new_name.strip())
            if rows > 0:
                self.batch_updated.emit(batch_id)
                return True
            return False
        except Exception as e:
            self.batch_error.emit(f"Error updating batch name: {e}")
            return False

    def add_images_to_batch(self, batch_id: int, image_paths: List[str]) -> int:
        """
        Add images to a batch.

        Args:
            batch_id: Batch ID
            image_paths: List of image paths to add

        Returns:
            Number of images added
        """
        try:
            count = self.batch_repo.add_images(batch_id, image_paths)
            if count > 0:
                self.images_added.emit(batch_id, count)
                self.batch_updated.emit(batch_id)
            return count
        except Exception as e:
            self.batch_error.emit(f"Error adding images: {e}")
            return 0

    def remove_images_from_batch(self, batch_id: int, image_paths: List[str]) -> int:
        """
        Remove images from a batch.

        Args:
            batch_id: Batch ID
            image_paths: List of image paths to remove

        Returns:
            Number of images removed
        """
        try:
            count = self.batch_repo.remove_images(batch_id, image_paths)
            if count > 0:
                self.images_removed.emit(batch_id, count)
                self.batch_updated.emit(batch_id)
            return count
        except Exception as e:
            self.batch_error.emit(f"Error removing images: {e}")
            return 0

    def set_reference_image(self, batch_id: int, image_path: str) -> bool:
        """
        Set the reference image for a batch.

        Args:
            batch_id: Batch ID
            image_path: Path of image to set as reference

        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.batch_repo.set_reference_image(batch_id, image_path)
            if success:
                self.reference_changed.emit(batch_id, image_path)
                self.batch_updated.emit(batch_id)
            return success
        except Exception as e:
            self.batch_error.emit(f"Error setting reference: {e}")
            return False

    def get_batch_count(self) -> int:
        """
        Get total number of batches.

        Returns:
            Batch count
        """
        return self.batch_repo.count()

    def get_batch_image_count(self, batch_id: int) -> int:
        """
        Get number of images in a batch.

        Args:
            batch_id: Batch ID

        Returns:
            Image count
        """
        return self.batch_repo.count_images_in_batch(batch_id)
