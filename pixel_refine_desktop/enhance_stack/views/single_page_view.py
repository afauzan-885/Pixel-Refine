"""
Single Page View (MVC Hybrid).
Reuses legacy UI components while connecting to MVC controllers.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, Signal
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.batch_page_v2_layout import (
    BatchPageV2Layout,
)


class SinglePageView(BatchPageV2Layout):
    """
    Single page view with MVC architecture.
    Inherits from BatchPageV2Layout to reuse all UI and functionality.
    This is a pragmatic hybrid approach for complex refactoring.
    """

    def __init__(self, db_path: str, parent=None):
        # Create database manager first
        from pixel_refine_desktop.enhance_stack.core.logic.database_manager import (
            DatabaseManager,
        )

        database_manager = DatabaseManager(db_path)

        # Initialize parent (BatchPageV2Layout)
        super().__init__(database_manager)

        # Store db_path for future use
        self.db_path = db_path

        # Initialize MVC controllers
        from pixel_refine_desktop.enhance_stack.controllers.single_page_controller import (
            SinglePageController,
        )
        from pixel_refine_desktop.enhance_stack.controllers.import_export_controller import (
            ImportExportController,
        )
        from pixel_refine_desktop.enhance_stack.controllers.image_processing_controller import (
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
