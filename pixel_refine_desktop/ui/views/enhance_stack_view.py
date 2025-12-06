"""
Enhanced Stack Page View (MVC Refactored).
Main container for single and batch page views with controller integration.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from pixel_refine_desktop.ui.views.top_bar import TopBar
from pixel_refine_desktop.ui.views.single_page_view import SinglePageView
from pixel_refine_desktop.ui.views.batch_page_view import BatchPageView
from pixel_refine_desktop.ui.resources.animations.animation_manager import (
    SlideDirection,
    StackedWidgetAnimator,
)
from pixel_refine_desktop.ui.resources.animations.slide import slide
from pixel_refine_desktop.ui.resources.animations.toast.toast_manager import (
    ToastManager,
)


class EnhanceStackView(QWidget):
    """
    Main view for enhance stack feature (MVC Architecture).
    Manages single and batch page views with controllers.
    """

    def __init__(self, db_path: str, parent=None):
        super().__init__(parent)
        self.db_path = db_path

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Animation and toast managers
        self.animator = StackedWidgetAnimator(self)
        self.toast_manager = ToastManager(self)

        # Top bar with switch buttons
        self.top_bar = TopBar()
        layout.addWidget(self.top_bar)

        # Stacked widget for single/batch pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget, 1)

        # Create single page view (hybrid MVC)
        self.single_page_view = SinglePageView(self.db_path, self)
        self.stacked_widget.addWidget(self.single_page_view)

        # Create batch page view (hybrid MVC)
        self.batch_page_view = BatchPageView(self.db_path, self)
        self.stacked_widget.addWidget(self.batch_page_view)

        # Set initial page
        self.stacked_widget.setCurrentWidget(self.single_page_view)
        self.top_bar.left_stack.setCurrentIndex(0)
        self.top_bar.right_stack.setCurrentIndex(0)

    def connect_signals(self):
        """Connect top bar signals and toast notifications."""
        # Top bar switch buttons
        self.top_bar.single_button.toggled.connect(self._handle_switch_request)
        self.top_bar.batch_button.toggled.connect(self._handle_switch_request)

        # Single page buttons
        self.top_bar.single_page_import_button.clicked.connect(
            self.single_page_view.handle_import_button
        )
        self.top_bar.single_page_delete_button.clicked.connect(
            self.single_page_view.handle_delete_button
        )

        # Batch page buttons
        self.top_bar.batch_page_import_button.clicked.connect(
            self.batch_page_view.handle_batch_import_button
        )
        self.top_bar.batch_page_delete_button.clicked.connect(
            self.batch_page_view.handle_delete_all_batches
        )
        self.top_bar.start_process_batch.clicked.connect(
            self.batch_page_view.process_all_batches
        )

        # Connect batch layout toast to main toast manager
        if hasattr(self.batch_page_view, "batch_layout"):
            if hasattr(self.batch_page_view.batch_layout, "show_toast_requested"):
                self.batch_page_view.batch_layout.show_toast_requested.connect(
                    self.toast_manager.show
                )

    def _handle_switch_request(self):
        """Handle switch between single and batch pages."""
        if self.top_bar.single_button.isChecked():
            target_widget = self.single_page_view
            target_index = 0
            slide_direction = SlideDirection.RIGHT
        elif self.top_bar.batch_button.isChecked():
            target_widget = self.batch_page_view
            target_index = 1
            slide_direction = SlideDirection.LEFT
        else:
            return

        # Animate transition
        slide(
            self.animator,
            self.stacked_widget,
            target_widget,
            slide_direction,
            duration=400,
        )

        # Switch top bar stacks
        self.top_bar.left_stack.setCurrentIndex(target_index)
        self.top_bar.right_stack.setCurrentIndex(target_index)
