"""
Batch repository for batch-related database operations.
Handles CRUD operations for batch_process and batch_process_image tables.
"""

from typing import Optional, List, Tuple
from .base_repository import BaseRepository
from .image_repository import ImageRepository


class BatchRepository(BaseRepository):
    """
    Repository for batch data access.
    Handles all database operations related to batches.
    """
    
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.image_repo = ImageRepository(db_path)
    
    def create(self, batch_name: str) -> Optional[int]:
        """
        Create a new batch.
        
        Args:
            batch_name: Unique name for the batch
            
        Returns:
            Batch ID if successful, None if batch name already exists
        """
        try:
            query = "INSERT INTO batch_process (batch_name) VALUES (?)"
            batch_id = self.execute_update(query, (batch_name,))
            print(f"Batch '{batch_name}' created with ID: {batch_id}")
            return batch_id
        except Exception as e:
            # Batch name already exists
            print(f"Batch name '{batch_name}' already exists or error: {e}")
            # Try to get existing batch ID
            return self.get_id_by_name(batch_name)
    
    def get_by_id(self, batch_id: int) -> Optional[tuple]:
        """
        Get batch by ID.
        
        Args:
            batch_id: Batch ID
            
        Returns:
            Tuple of (id, batch_name) or None
        """
        query = "SELECT id, batch_name FROM batch_process WHERE id = ?"
        return self.execute_query(query, (batch_id,), fetch_one=True)
    
    def get_id_by_name(self, batch_name: str) -> Optional[int]:
        """
        Get batch ID by name.
        
        Args:
            batch_name: Batch name
            
        Returns:
            Batch ID or None if not found
        """
        query = "SELECT id FROM batch_process WHERE batch_name = ?"
        result = self.execute_query(query, (batch_name,), fetch_one=True)
        return result[0] if result else None
    
    def get_all(self) -> List[tuple]:
        """
        Get all batches.
        
        Returns:
            List of tuples (id, batch_name)
        """
        query = "SELECT id, batch_name FROM batch_process ORDER BY id"
        return self.execute_query(query)
    
    def delete(self, batch_id: int) -> int:
        """
        Delete batch by ID.
        Associated images in batch_process_image will be deleted automatically (CASCADE).
        
        Args:
            batch_id: Batch ID to delete
            
        Returns:
            Number of rows deleted
        """
        query = "DELETE FROM batch_process WHERE id = ?"
        rows = self.execute_update(query, (batch_id,))
        if rows > 0:
            print(f"Batch ID {batch_id} deleted successfully")
        return rows

    def update_name(self, batch_id: int, new_name: str) -> int:
        """
        Update the name of a batch.

        Args:
            batch_id: The ID of the batch to update.
            new_name: The new name for the batch.

        Returns:
            Number of rows updated (should be 1 on success).
        """
        query = "UPDATE batch_process SET batch_name = ? WHERE id = ?"
        try:
            rows = self.execute_update(query, (new_name, batch_id))
            if rows > 0:
                print(f"Batch ID {batch_id} renamed to '{new_name}'")
            return rows
        except Exception as e:
            print(f"Error updating batch name for ID {batch_id}: {e}")
            return 0
    
    def add_images(self, batch_id: int, image_paths: List[str]) -> int:
        """
        Add images to a batch.
        
        Args:
            batch_id: Batch ID
            image_paths: List of image file paths
            
        Returns:
            Number of images successfully added
        """
        added_count = 0
        
        # Check if batch has reference image
        has_reference = self.has_reference_image(batch_id)
        
        for image_path in image_paths:
            # Get or create image ID
            image_id = self.image_repo.get_or_create(image_path)
            
            # Check if already linked
            if self.is_image_in_batch(batch_id, image_id):
                continue
            
            # Determine if this should be reference
            is_reference = 0
            if not has_reference:
                is_reference = 1
                has_reference = True
            
            # Add to batch
            query = """
                INSERT INTO batch_process_image (batch_id, image_id_batch, is_reference_batch)
                VALUES (?, ?, ?)
            """
            try:
                self.execute_update(query, (batch_id, image_id, is_reference))
                added_count += 1
            except Exception as e:
                print(f"Error adding image {image_path} to batch {batch_id}: {e}")
        
        if added_count > 0:
            print(f"Added {added_count} images to batch ID {batch_id}")
        
        return added_count
    
    def remove_images(self, batch_id: int, image_paths: List[str]) -> int:
        """
        Remove images from a batch.
        
        Args:
            batch_id: Batch ID
            image_paths: List of image file paths to remove
            
        Returns:
            Number of images removed
        """
        removed_count = 0
        
        for image_path in image_paths:
            image = self.image_repo.get_by_path(image_path)
            if not image:
                continue
            
            image_id = image[0]
            
            # Check if this was the reference image
            was_reference = self.is_reference_image(batch_id, image_id)
            
            # Remove from batch
            query = "DELETE FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ?"
            rows = self.execute_update(query, (batch_id, image_id))
            removed_count += rows
            
            # If reference was removed, set new reference
            if was_reference and rows > 0:
                self._set_new_reference(batch_id)
        
        return removed_count
    
    def get_batch_images(self, batch_id: int) -> List[Tuple[int, str, bool]]:
        """
        Get all images in a batch.
        
        Args:
            batch_id: Batch ID
            
        Returns:
            List of tuples (image_id, path, is_reference)
        """
        query = """
            SELECT i.id, i.path, bpi.is_reference_batch
            FROM batch_process_image bpi
            JOIN images i ON bpi.image_id_batch = i.id
            WHERE bpi.batch_id = ?
            ORDER BY bpi.id
        """
        return self.execute_query(query, (batch_id,))
    
    def set_reference_image(self, batch_id: int, image_path: str) -> bool:
        """
        Set an image as the reference for a batch.
        
        Args:
            batch_id: Batch ID
            image_path: Path of image to set as reference
            
        Returns:
            True if successful, False otherwise
        """
        image = self.image_repo.get_by_path(image_path)
        if not image:
            print(f"Image '{image_path}' not found in database")
            return False
        
        image_id = image[0]
        
        # Check if image is in batch
        if not self.is_image_in_batch(batch_id, image_id):
            print(f"Image ID {image_id} is not in batch ID {batch_id}")
            return False
        
        # Reset all references for this batch
        query1 = "UPDATE batch_process_image SET is_reference_batch = 0 WHERE batch_id = ?"
        self.execute_update(query1, (batch_id,))
        
        # Set new reference
        query2 = """
            UPDATE batch_process_image 
            SET is_reference_batch = 1 
            WHERE batch_id = ? AND image_id_batch = ?
        """
        rows = self.execute_update(query2, (batch_id, image_id))
        
        if rows > 0:
            print(f"Image '{image_path}' set as reference for batch ID {batch_id}")
            return True
        
        return False
    
    def get_reference_image(self, batch_id: int) -> Optional[Tuple[int, str]]:
        """
        Get the reference image for a batch.
        
        Args:
            batch_id: Batch ID
            
        Returns:
            Tuple of (image_id, path) or None if no reference set
        """
        query = """
            SELECT i.id, i.path
            FROM batch_process_image bpi
            JOIN images i ON bpi.image_id_batch = i.id
            WHERE bpi.batch_id = ? AND bpi.is_reference_batch = 1
        """
        return self.execute_query(query, (batch_id,), fetch_one=True)
    
    def is_image_in_batch(self, batch_id: int, image_id: int) -> bool:
        """
        Check if an image is in a batch.
        
        Args:
            batch_id: Batch ID
            image_id: Image ID
            
        Returns:
            True if image is in batch, False otherwise
        """
        query = "SELECT 1 FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ?"
        result = self.execute_query(query, (batch_id, image_id), fetch_one=True)
        return result is not None
    
    def is_reference_image(self, batch_id: int, image_id: int) -> bool:
        """
        Check if an image is the reference for a batch.
        
        Args:
            batch_id: Batch ID
            image_id: Image ID
            
        Returns:
            True if image is reference, False otherwise
        """
        query = """
            SELECT is_reference_batch 
            FROM batch_process_image 
            WHERE batch_id = ? AND image_id_batch = ?
        """
        result = self.execute_query(query, (batch_id, image_id), fetch_one=True)
        return result and result[0] == 1
    
    def has_reference_image(self, batch_id: int) -> bool:
        """
        Check if a batch has a reference image set.
        
        Args:
            batch_id: Batch ID
            
        Returns:
            True if batch has reference, False otherwise
        """
        query = "SELECT 1 FROM batch_process_image WHERE batch_id = ? AND is_reference_batch = 1"
        result = self.execute_query(query, (batch_id,), fetch_one=True)
        return result is not None
    
    def _set_new_reference(self, batch_id: int) -> None:
        """
        Set a new reference image for a batch (internal method).
        Called when the current reference is removed.
        
        Args:
            batch_id: Batch ID
        """
        # Get first image in batch
        query = "SELECT id FROM batch_process_image WHERE batch_id = ? ORDER BY id LIMIT 1"
        result = self.execute_query(query, (batch_id,), fetch_one=True)
        
        if result:
            bpi_id = result[0]
            update_query = "UPDATE batch_process_image SET is_reference_batch = 1 WHERE id = ?"
            self.execute_update(update_query, (bpi_id,))
            print(f"New reference set for batch ID {batch_id}")
    
    def count(self) -> int:
        """
        Get total number of batches.
        
        Returns:
            Number of batches in database
        """
        query = "SELECT COUNT(*) FROM batch_process"
        result = self.execute_query(query, fetch_one=True)
        return result[0] if result else 0
    
    def count_images_in_batch(self, batch_id: int) -> int:
        """
        Get number of images in a batch.
        
        Args:
            batch_id: Batch ID
            
        Returns:
            Number of images in the batch
        """
        query = "SELECT COUNT(*) FROM batch_process_image WHERE batch_id = ?"
        result = self.execute_query(query, (batch_id,), fetch_one=True)
        return result[0] if result else 0
