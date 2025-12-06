"""
Single Page View (MVC Hybrid).
Reuses legacy UI components while connecting to MVC controllers.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, Signal
from pixel_refine_desktop.ui.components.single_page.single_page_layout import (
    SinglePageLayout,
)


class SinglePageView(SinglePageLayout):
    """
    Single page view with MVC architecture.
    Inherits from legacy SinglePageLayout to reuse all UI and functionality.
    This is a pragmatic hybrid approach for complex refactoring.
    """

    def __init__(self, db_path: str, parent=None):
        # Create database manager first
        from pixel_refine_desktop.core.logic.database_manager import DatabaseManager

        database_manager = DatabaseManager(db_path)

        # Initialize parent (legacy SinglePageLayout)
        super().__init__(database_manager)

        # Store db_path for future use
        self.db_path = db_path

        # Initialize MVC controllers
        from pixel_refine_desktop.controllers.single_page_controller import (
            SinglePageController,
        )
        from pixel_refine_desktop.controllers.import_export_controller import (
            ImportExportController,
        )
        from pixel_refine_desktop.controllers.image_processing_controller import (
            ImageProcessingController,
        )

        self.single_controller = SinglePageController(db_path, self)
        self.import_export_controller = ImportExportController(self)
        self.processing_controller = ImageProcessingController(self)

        # Connect controller signals
        self.connect_controller_signals()

    def connect_controller_signals(self):
        """Connect MVC controller signals to view updates."""
        # These can be used for future enhancements
        # For now, legacy functionality is preserved
        pass
