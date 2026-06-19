"""
pixel_refine_mobile/models/data_access/image_repository.py
----------------------------------------------------------
Image repository for image-related database operations.
Direct port from desktop — same API, same behavior.
"""

from typing import Optional, List
from .base_repository import BaseRepository


class ImageRepository(BaseRepository):
    """Repository for image data access."""

    def get_or_create(self, path: str) -> int:
        """Get existing image ID or create new image record."""
        existing = self.get_by_path(path)
        if existing:
            return existing[0]
        query = "INSERT INTO images (path) VALUES (?)"
        return self.execute_update(query, (path,))

    def get_by_id(self, image_id: int) -> Optional[tuple]:
        """Get image by ID."""
        query = "SELECT id, path FROM images WHERE id = ?"
        return self.execute_query(query, (image_id,), fetch_one=True)

    def get_by_path(self, path: str) -> Optional[tuple]:
        """Get image by path."""
        query = "SELECT id, path FROM images WHERE path = ?"
        return self.execute_query(query, (path,), fetch_one=True)

    def get_all(self) -> List[tuple]:
        """Get all images."""
        query = "SELECT id, path FROM images"
        return self.execute_query(query)

    def delete(self, image_id: int) -> int:
        """Delete image by ID."""
        query = "DELETE FROM images WHERE id = ?"
        return self.execute_update(query, (image_id,))

    def delete_by_path(self, path: str) -> int:
        """Delete image by path."""
        query = "DELETE FROM images WHERE path = ?"
        return self.execute_update(query, (path,))

    def exists(self, path: str) -> bool:
        """Check if image exists in database."""
        return self.get_by_path(path) is not None

    def count(self) -> int:
        """Get total number of images."""
        query = "SELECT COUNT(*) FROM images"
        result = self.execute_query(query, fetch_one=True)
        return result[0] if result else 0
