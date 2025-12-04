"""
Application manager module for handling core business logic.
Manages database, folders, and application lifecycle.
"""

import os
import sys
from shutil import rmtree
from PySide6.QtWidgets import QMessageBox

from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.resources.animation.animation_manager import StackedWidgetAnimator


class ApplicationManager:
    """
    Manages core application logic including database, folders, and cleanup.
    """
    
    def __init__(self, main_window):
        """
        Initialize application manager.
        
        Args:
            main_window: Reference to the main window instance
        """
        self.main_window = main_window
        self.database_manager = None
        self.animator = None
        
        # Folder paths
        self.database_folder = "database"
        self.align_folder = os.path.join(self.database_folder, "align")
        self.stack_folder = os.path.join(self.database_folder, "stack")
        self.align_stitch_cache_folder = os.path.join(self.database_folder, "cache", "align_stitch")
        self.render_tiles_folder = os.path.join(self.database_folder, "cache", "render_tiles")
    
    def initialize_database(self, db_path: str = "pixel_refine_database.db") -> DatabaseManager:
        """
        Initialize and create database.
        
        Args:
            db_path: Path to the database file
            
        Returns:
            DatabaseManager instance
        """
        self.database_manager = DatabaseManager(db_path)
        self.database_manager.create_database()
        return self.database_manager
    
    def setup_animator(self) -> StackedWidgetAnimator:
        """
        Initialize animation manager.
        
        Returns:
            StackedWidgetAnimator instance
        """
        self.animator = StackedWidgetAnimator(self.main_window)
        return self.animator
    
    def initialize_folders(self) -> None:
        """
        Create necessary folders if they don't exist.
        
        Raises:
            SystemExit: If folder creation fails
        """
        try:
            os.makedirs(self.database_folder, exist_ok=True)
            os.makedirs(self.align_folder, exist_ok=True)
            os.makedirs(self.stack_folder, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"An error occurred while creating folders: {e}. The application will now close."
            )
            sys.exit(1)
    
    def cleanup_folders(self) -> None:
        """
        Clean up temporary folders and cache.
        Called when application is closing.
        """
        try:
            # Clean align_folder contents
            if os.path.exists(self.align_folder):
                for item in os.listdir(self.align_folder):
                    item_path = os.path.join(self.align_folder, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        rmtree(item_path)
            
            # Clean stack_folder contents
            if os.path.exists(self.stack_folder):
                for item in os.listdir(self.stack_folder):
                    item_path = os.path.join(self.stack_folder, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        rmtree(item_path)
            
            # Remove align_stitch_cache_folder
            if os.path.exists(self.align_stitch_cache_folder):
                rmtree(self.align_stitch_cache_folder)
            
            # Remove render_tiles_folder
            if os.path.exists(self.render_tiles_folder):
                rmtree(self.render_tiles_folder)
                
        except Exception as e:
            QMessageBox.warning(
                self.main_window,
                "Error",
                f"An error occurred while deleting folder contents: {e}"
            )
