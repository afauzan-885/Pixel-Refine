"""
Image repository for image-related database operations.
Handles CRUD operations for images table.
"""

from typing import Optional, List
from .base_repository import BaseRepository


class ImageRepository(BaseRepository):
    """
    Repository for image data access.
    Handles all database operations related to images.
    """
    
    def get_or_create(self, path: str) -> int:
        """
        Get existing image ID or create new image record.
        
        Args:
            path: Image file path
            
        Returns:
            Image ID
        """
        # Try to get existing
        existing = self.get_by_path(path)
        if existing:
            return existing[0]  # Return ID
        
        # Create new
        query = "INSERT INTO images (path) VALUES (?)"
        return self.execute_update(query, (path,))
    
    def get_by_id(self, image_id: int) -> Optional[tuple]:
        """
        Get image by ID.
        
        Args:
            image_id: Image ID
            
        Returns:
            Tuple of (id, path) or None if not found
        """
        query = "SELECT id, path FROM images WHERE id = ?"
        return self.execute_query(query, (image_id,), fetch_one=True)
    
    def get_by_path(self, path: str) -> Optional[tuple]:
        """
        Get image by path.
        
        Args:
            path: Image file path
            
        Returns:
            Tuple of (id, path) or None if not found
        """
        query = "SELECT id, path FROM images WHERE path = ?"
        return self.execute_query(query, (path,), fetch_one=True)
    
    def get_all(self) -> List[tuple]:
        """
        Get all images.
        
        Returns:
            List of tuples (id, path)
        """
        query = "SELECT id, path FROM images"
        return self.execute_query(query)
    
    def delete(self, image_id: int) -> int:
        """
        Delete image by ID.
        
        Args:
            image_id: Image ID to delete
            
        Returns:
            Number of rows deleted
        """
        query = "DELETE FROM images WHERE id = ?"
        return self.execute_update(query, (image_id,))
    
    def delete_by_path(self, path: str) -> int:
        """
        Delete image by path.
        
        Args:
            path: Image file path
            
        Returns:
            Number of rows deleted
        """
        query = "DELETE FROM images WHERE path = ?"
        return self.execute_update(query, (path,))
    
    def exists(self, path: str) -> bool:
        """
        Check if image exists in database.
        
        Args:
            path: Image file path
            
        Returns:
            True if exists, False otherwise
        """
        return self.get_by_path(path) is not None
    
    def count(self) -> int:
        """
        Get total number of images.
        
        Returns:
            Number of images in database
        """
        query = "SELECT COUNT(*) FROM images"
        result = self.execute_query(query, fetch_one=True)
        return result[0] if result else 0
