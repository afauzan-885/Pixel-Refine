"""
pixel_refine_mobile/models/data_access/batch_repository.py
----------------------------------------------------------
Batch repository for batch-related database operations.
Direct port from desktop — same API, same behavior.
"""

from typing import Optional, List, Tuple
from .base_repository import BaseRepository
from .image_repository import ImageRepository


class BatchRepository(BaseRepository):
    """Repository for batch data access."""

    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.image_repo = ImageRepository(db_path)
        self.add_column_if_not_exists("batch_process", "order_index", "INTEGER DEFAULT 0")

    def create(self, batch_name: str) -> Optional[int]:
        """Create a new batch."""
        try:
            max_order_query = "SELECT MAX(order_index) FROM batch_process"
            max_order_res = self.execute_query(max_order_query, fetch_one=True)
            next_order = (max_order_res[0] or 0) + 1 if max_order_res else 1
            query = "INSERT INTO batch_process (batch_name, order_index) VALUES (?, ?)"
            batch_id = self.execute_update(query, (batch_name, next_order))
            print(f"Batch '{batch_name}' created with ID: {batch_id}")
            return batch_id
        except Exception as e:
            print(f"Batch name '{batch_name}' already exists or error: {e}")
            return self.get_id_by_name(batch_name)

    def get_by_id(self, batch_id: int) -> Optional[tuple]:
        """Get batch by ID."""
        query = "SELECT id, batch_name FROM batch_process WHERE id = ?"
        return self.execute_query(query, (batch_id,), fetch_one=True)

    def get_id_by_name(self, batch_name: str) -> Optional[int]:
        """Get batch ID by name."""
        query = "SELECT id FROM batch_process WHERE batch_name = ?"
        result = self.execute_query(query, (batch_name,), fetch_one=True)
        return result[0] if result else None

    def get_all(self) -> List[tuple]:
        """Get all batches ordered by order_index."""
        query = "SELECT id, batch_name FROM batch_process ORDER BY order_index ASC, id ASC"
        return self.execute_query(query, fetch_one=False)

    def delete(self, batch_id: int) -> int:
        """Delete batch by ID (CASCADE deletes associated images)."""
        query = "DELETE FROM batch_process WHERE id = ?"
        return self.execute_update(query, (batch_id,))

    def add_images(self, batch_id: int, image_paths: List[str]) -> int:
        """Add multiple images to a batch."""
        if not image_paths:
            return 0
        added_count = 0
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM batch_process_image WHERE batch_id = ? AND is_reference_batch = 1 LIMIT 1",
                    (batch_id,),
                )
                has_reference = cursor.fetchone() is not None

                for image_path in image_paths:
                    image_id = self.image_repo.get_or_create(image_path)
                    cursor.execute(
                        "SELECT 1 FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ? LIMIT 1",
                        (batch_id, image_id),
                    )
                    if cursor.fetchone():
                        continue
                    is_reference = 0 if has_reference else 1
                    if not has_reference:
                        has_reference = True
                    cursor.execute(
                        "INSERT INTO batch_process_image (batch_id, image_id_batch, is_reference_batch) VALUES (?, ?, ?)",
                        (batch_id, image_id, is_reference),
                    )
                    added_count += 1
            return added_count
        except Exception as e:
            print(f"Error in add_images: {e}")
            return 0

    def get_batch_images(self, batch_id: int) -> List[Tuple[int, str, bool]]:
        """Get all images in a batch."""
        query = """
            SELECT i.id, i.path, bpi.is_reference_batch
            FROM batch_process_image bpi
            JOIN images i ON bpi.image_id_batch = i.id
            WHERE bpi.batch_id = ?
            ORDER BY bpi.is_reference_batch DESC, bpi.id ASC
        """
        return self.execute_query(query, (batch_id,), fetch_one=False)

    def count(self) -> int:
        """Get total number of batches."""
        query = "SELECT COUNT(*) FROM batch_process"
        result = self.execute_query(query, fetch_one=True)
        return result[0] if result else 0

    def count_images_in_batch(self, batch_id: int) -> int:
        """Get number of images in a batch."""
        query = "SELECT COUNT(*) FROM batch_process_image WHERE batch_id = ?"
        result = self.execute_query(query, (batch_id,), fetch_one=True)
        return result[0] if result else 0
