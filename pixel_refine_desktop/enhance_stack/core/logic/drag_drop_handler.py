"""
Drag Drop Handler - Handles drag and drop operations for image import.
Manages drag enter, drag leave, and drop events with file validation.
"""

from PySide6.QtCore import QMimeData
from typing import List, Tuple


class DragDropHandler:
    """Handles drag and drop operations for image files."""

    def __init__(self, parent_panel):
        """
        Initialize DragDropHandler.

        Args:
            parent_panel: Reference to DisplayPanel for accessing UI components
        """
        self.panel = parent_panel

    def handle_drag_enter(self, mime_data: QMimeData) -> Tuple[bool, int]:
        """
        Handle drag enter event.

        Args:
            mime_data: MIME data from drag event

        Returns:
            Tuple of (should_accept, file_count)
        """
        if not self.panel.current_batch_id:
            return False, 0

        if mime_data.hasUrls():
            # Count files being hovered
            file_count = len([url for url in mime_data.urls() if url.isLocalFile()])

            if file_count > 0:
                return True, file_count

        return False, 0

    def handle_drag_leave(self):
        """Handle drag leave event."""
        # Logic handled by DisplayPanel's drop_overlay
        pass

    def handle_drop(self, mime_data: QMimeData) -> Tuple[bool, List[str]]:
        """
        Handle drop event and filter valid image files.

        Args:
            mime_data: MIME data from drop event

        Returns:
            Tuple of (should_accept, valid_files_list)
        """
        if not self.panel.current_batch_id:
            return False, []

        if mime_data.hasUrls():
            # Filter valid image files in supported formats
            valid_files = self.filter_valid_files(mime_data.urls())
            if valid_files:
                return True, valid_files

        return False, []

    def filter_valid_files(self, urls) -> List[str]:
        """
        Filter valid image files from URL list.

        Args:
            urls: List of QUrl objects

        Returns:
            List of valid file paths
        """
        # Get supported extensions from UI state manager
        supported_extensions = self.panel.ui_state_manager.get_supported_extensions()

        valid_files = [
            url.toLocalFile()
            for url in urls
            if url.isLocalFile()
            and url.toLocalFile().lower().endswith(supported_extensions)
        ]

        return valid_files
