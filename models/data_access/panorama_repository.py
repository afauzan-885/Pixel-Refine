"""
Panorama repository for panorama project database operations.
Handles CRUD operations for panorama_projects and panorama_project_images tables.
"""

from typing import Optional, List, Dict
from .base_repository import BaseRepository
from .image_repository import ImageRepository


class PanoramaRepository(BaseRepository):
    """
    Repository for panorama project data access.
    Handles all database operations related to panorama projects.
    """
    
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.image_repo = ImageRepository(db_path)
    
    def create_project(self, name: str) -> Optional[int]:
        """
        Create a new panorama project.
        
        Args:
            name: Project name
            
        Returns:
            Project ID if successful, None if name already exists
        """
        try:
            query = "INSERT INTO panorama_projects (name) VALUES (?)"
            project_id = self.execute_update(query, (name,))
            print(f"Panorama project '{name}' created with ID: {project_id}")
            return project_id
        except Exception as e:
            print(f"Error creating panorama project '{name}': {e}")
            return None
    
    def get_project(self, project_id: int) -> Optional[tuple]:
        """
        Get panorama project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Tuple of (id, name, created_at) or None
        """
        query = "SELECT id, name, created_at FROM panorama_projects WHERE id = ?"
        return self.execute_query(query, (project_id,), fetch_one=True)
    
    def get_all_projects(self) -> List[tuple]:
        """
        Get all panorama projects.
        
        Returns:
            List of tuples (id, name, created_at)
        """
        query = "SELECT id, name, created_at FROM panorama_projects ORDER BY name"
        return self.execute_query(query)
    
    def delete_project(self, project_id: int) -> bool:
        """
        Delete panorama project.
        Associated images will be unlinked automatically (CASCADE).
        
        Args:
            project_id: Project ID
            
        Returns:
            True if successful, False otherwise
        """
        query = "DELETE FROM panorama_projects WHERE id = ?"
        rows = self.execute_update(query, (project_id,))
        if rows > 0:
            print(f"Panorama project ID {project_id} deleted")
            return True
        return False
    
    def rename_project(self, project_id: int, new_name: str) -> bool:
        """
        Rename a panorama project.
        
        Args:
            project_id: Project ID
            new_name: New project name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = "UPDATE panorama_projects SET name = ? WHERE id = ?"
            rows = self.execute_update(query, (new_name, project_id))
            if rows > 0:
                print(f"Project ID {project_id} renamed to '{new_name}'")
                return True
            return False
        except Exception as e:
            print(f"Error renaming project {project_id}: {e}")
            return False
    
    def add_images(self, project_id: int, image_paths: List[str]) -> bool:
        """
        Add images to a panorama project.
        
        Args:
            project_id: Project ID
            image_paths: List of image file paths
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for path in image_paths:
                # Get or create image ID
                image_id = self.image_repo.get_or_create(path)
                
                # Link to project (OR IGNORE prevents duplicates)
                query = """
                    INSERT OR IGNORE INTO panorama_project_images (project_id, image_id)
                    VALUES (?, ?)
                """
                self.execute_update(query, (project_id, image_id))
            
            print(f"Added {len(image_paths)} images to project ID {project_id}")
            return True
        except Exception as e:
            print(f"Error adding images to project {project_id}: {e}")
            return False
    
    def remove_images(self, project_id: int, image_paths: List[str]) -> bool:
        """
        Remove images from a panorama project.
        
        Args:
            project_id: Project ID
            image_paths: List of image file paths to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for path in image_paths:
                image = self.image_repo.get_by_path(path)
                if not image:
                    continue
                
                image_id = image[0]
                query = "DELETE FROM panorama_project_images WHERE project_id = ? AND image_id = ?"
                self.execute_update(query, (project_id, image_id))
            
            return True
        except Exception as e:
            print(f"Error removing images from project {project_id}: {e}")
            return False
    
    def get_project_images(self, project_id: int) -> List[str]:
        """
        Get all image paths for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of image file paths
        """
        query = """
            SELECT i.path
            FROM panorama_project_images ppi
            JOIN images i ON ppi.image_id = i.id
            WHERE ppi.project_id = ?
            ORDER BY ppi.image_order, ppi.id
        """
        results = self.execute_query(query, (project_id,))
        return [row[0] for row in results]
    
    def get_workflow_settings(self, project_id: int) -> Optional[Dict[str, str]]:
        """
        Get workflow settings for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary of settings or None if project not found
        """
        query = """
            SELECT align_algorithm, feature_detector, projection_type, blending_method
            FROM panorama_projects
            WHERE id = ?
        """
        result = self.execute_query(query, (project_id,), fetch_one=True)
        
        if result:
            return {
                'align_algorithm': result[0],
                'feature_detector': result[1],
                'projection_type': result[2],
                'blending_method': result[3]
            }
        return None
    
    def save_workflow_setting(self, project_id: int, setting_key: str, setting_value: str) -> bool:
        """
        Save a single workflow setting for a project.
        
        Args:
            project_id: Project ID
            setting_key: Setting name (must be in allowed list)
            setting_value: Setting value
            
        Returns:
            True if successful, False otherwise
        """
        allowed_keys = ['align_algorithm', 'feature_detector', 'projection_type', 'blending_method']
        
        if setting_key not in allowed_keys:
            print(f"Invalid setting key: {setting_key}")
            return False
        
        try:
            query = f"UPDATE panorama_projects SET {setting_key} = ? WHERE id = ?"
            rows = self.execute_update(query, (setting_value, project_id))
            return rows > 0
        except Exception as e:
            print(f"Error saving setting '{setting_key}' for project {project_id}: {e}")
            return False
