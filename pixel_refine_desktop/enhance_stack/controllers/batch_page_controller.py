"""
Batch Page Controller.
Handles business logic for batch processing operations.
"""

from collections import OrderedDict
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

    batch_selected = Signal(int)  # (batch_id) logic event

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

        # LRU cache for BatchModel lookups. Eliminates the SQLite hit
        # when the same batch is re-selected from the right-side list.
        # Keyed by batch_id; entries are evicted at _BATCH_CACHE_LIMIT
        # or when invalidated by signals.
        self._batch_cache: "OrderedDict[int, BatchModel]" = OrderedDict()
        self._batch_cache_limit: int = 64

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
                # New batch invalidates ordering and any cached batch
                # list snapshot.
                self._evict_batch_cache(None)
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

        Uses a single LEFT JOIN query (replaces the prior N+1 pattern
        of one query for batch rows + N queries for image rows).
        Populates the LRU cache as a side effect.

        Returns:
            List of BatchModel instances
        """
        rows = self.batch_repo.get_all_with_images()
        if not rows:
            return []

        batches: List[BatchModel] = []
        for batch_id, batch_name, image_rows in rows:
            images = [
                ImageModel(id=img_id, path=path, is_reference=bool(is_ref))
                for img_id, path, is_ref in image_rows
            ]
            batch = BatchModel(id=batch_id, name=batch_name, images=images)
            self._batch_cache[batch_id] = batch
            self._touch_cache(batch_id)
            batches.append(batch)
        return batches

    def get_batch(self, batch_id: int) -> Optional[BatchModel]:
        """
        Get a specific batch with its images.

        Cache hit returns the previously-fetched BatchModel without
        hitting SQLite. Cache miss falls back to a per-batch query
        and primes the cache.

        Args:
            batch_id: Batch ID

        Returns:
            BatchModel or None if not found
        """
        cached = self._batch_cache.get(batch_id)
        if cached is not None:
            self._touch_cache(batch_id)
            return cached

        batch_row = self.batch_repo.get_by_id(batch_id)
        if not batch_row:
            return None

        b_id, batch_name = batch_row
        image_rows = self.batch_repo.get_batch_images(b_id)
        images = [
            ImageModel(id=img_id, path=path, is_reference=bool(is_ref))
            for img_id, path, is_ref in image_rows
        ]
        batch = BatchModel(id=b_id, name=batch_name, images=images)
        self._batch_cache[b_id] = batch
        self._touch_cache(b_id)
        return batch

    def _touch_cache(self, batch_id: int) -> None:
        """Mark *batch_id* as most-recently-used and enforce the LRU cap."""
        if batch_id in self._batch_cache:
            self._batch_cache.move_to_end(batch_id)
        while len(self._batch_cache) > self._batch_cache_limit:
            self._batch_cache.popitem(last=False)

    def _evict_batch_cache(self, batch_id) -> None:
        """Evict one batch_id (int) or the entire cache (None)."""
        if batch_id is None:
            self._batch_cache.clear()
        else:
            self._batch_cache.pop(batch_id, None)

    def invalidate_batch_cache(self, batch_id=None) -> None:
        """Public alias for :meth:`_evict_batch_cache`.

        Exposed for grid cache wiring in :class:`DisplayPanel` so a
        stale ``BatchModel`` cannot be served after the underlying
        ``batch_process`` / ``batch_process_image`` rows change.
        """
        self._evict_batch_cache(batch_id)

    def delete_batch(self, batch_id: int) -> bool:
        """
        Delete a batch.

        Args:
            batch_id: Batch ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # 1. Get image paths for thumbnail cleanup
            batch = self.get_batch(batch_id)
            image_paths = []
            if batch:
                image_paths = [img.path for img in batch.images]

            # 2. Delete from database
            rows = self.batch_repo.delete(batch_id)

            if rows > 0:
                # 3. Cleanup thumbnails on disk
                if image_paths:
                    try:
                        from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_processor import (
                            get_thumbnail_repo,
                        )

                        thumb_repo = get_thumbnail_repo()
                        thumb_repo.delete_thumbnails(image_paths)
                    except Exception as e:
                        print(f"[BatchController] Thumbnail cleanup warning: {e}")

                self._evict_batch_cache(batch_id)
                self.batch_deleted.emit(batch_id)
                return True
            return False
        except Exception as e:
            self.batch_error.emit(f"Error deleting batch: {e}")
            return False

    def reorder_batches(self, batch_ids: List[int]) -> bool:
        """
        Reorder batches in the database.
        """
        success = self.batch_repo.update_batch_order(batch_ids)
        if success:
            # Ordering change affects the cached list view; drop it
            # so the next ``get_all_batches`` re-reads the new order.
            self._evict_batch_cache(None)
            # No specific signal needed if view reloads, but good for sync
            self.batch_updated.emit(-1)  # Special ID for global update
        return success

    def update_batch_name(self, batch_id: int, new_name: str) -> bool:
        """
        Update the name of a batch.

        Args:
            batch_id: The ID of the batch.
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
                self._evict_batch_cache(batch_id)
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
                self._evict_batch_cache(batch_id)
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
                self._evict_batch_cache(batch_id)
                self.images_removed.emit(batch_id, count)
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

    def handle_batch_selected(self, batch_id: int):
        """
        Notify that a batch has been selected.
        This signal is listened to by the RightPanel/Layout to switch context.
        """
        self.batch_selected.emit(batch_id)
