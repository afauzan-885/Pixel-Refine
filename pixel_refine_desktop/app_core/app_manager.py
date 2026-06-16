"""
Application manager module for handling core business logic.
Manages database, folders, and application lifecycle.
"""

import os
import sys
from shutil import rmtree
from PySide6.QtWidgets import QMessageBox

from pixel_refine_desktop.enhance_stack.core.logic.database_manager import (
    DatabaseManager,
)
from resources.animations.animation_manager import (
    StackedWidgetAnimator,
)
from pixel_refine_desktop.enhance_stack.models.algorithm_list import ALGORITHM_DATA
import config


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

        # Auto-apply GenericUILibrary stylesheet
        try:
            from resources.GenericUILibrary import (
                apply_stylesheet,
            )

            apply_stylesheet()
        except Exception as e:
            print(f"Note: Could not auto-apply GenericUILibrary stylesheet - {e}")

        self.main_window = main_window
        self.database_manager = None
        self.animator = None

        # Folder paths
        self.database_folder = "database"
        self.align_folder = os.path.join(self.database_folder, "align")
        self.stack_folder = os.path.join(self.database_folder, "stack")
        self.align_stitch_cache_folder = os.path.join(
            self.database_folder, "cache", "align_stitch"
        )
        self.render_tiles_folder = os.path.join(
            self.database_folder, "cache", "render_tiles"
        )
        self.comparison_cache_folder = config.COMPARISON_CACHE_DIR

    def initialize_database(
        self, db_path: str = "pixel_refine_database.db"
    ) -> DatabaseManager:
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
        self.animator = StackedWidgetAnimator(self.main_window)
        return self.animator

    def load_algorithms(self) -> dict:
        """
        Load and validate available algorithms.

        Returns:
            dict: Summary of loaded algorithms count by category.
        """
        summary = {}
        for category, data in ALGORITHM_DATA.items():
            count = len(data.get("options", []))
            summary[category] = count
            # Here you could add more complex validation logic if needed
            # For example, checking if model files exist for each algorithm

        return summary

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
            os.makedirs(self.comparison_cache_folder, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"An error occurred while creating folders: {e}. The application will now close.",
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

            # Remove comparison_cache contents
            if os.path.exists(self.comparison_cache_folder):
                for item in os.listdir(self.comparison_cache_folder):
                    item_path = os.path.join(self.comparison_cache_folder, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        rmtree(item_path)

        except Exception as e:
            QMessageBox.warning(
                self.main_window,
                "Error",
                f"An error occurred while deleting folder contents: {e}",
            )
