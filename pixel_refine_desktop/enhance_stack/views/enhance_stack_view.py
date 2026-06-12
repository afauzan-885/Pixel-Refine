"""
Enhanced Stack Page View (MVC Refactored).
Main container for single and batch page views with controller integration.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Signal
from .top_bar import TopBar
from .single_page_view import SinglePageView
from .batch_page_view import BatchPageView
from pixel_refine_desktop.ui.resources.animations.animation_manager import (
    SlideDirection,
    StackedWidgetAnimator,
)
from pixel_refine_desktop.ui.resources.animations.slide import slide
from pixel_refine_desktop.ui.resources.animations.fade import fade_in
from pixel_refine_desktop.ui.resources.animations.toast.toast_manager import (
    ToastManager,
)


class EnhanceStackView(QWidget):
    """
    Main view for enhance stack feature (MVC Architecture).
    Manages single and batch page views with controllers.
    """

    page_changed = Signal(int)  # Forward global navigation

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
        # self.top_bar = TopBar()
        # layout.addWidget(self.top_bar)

        # Stacked widget for single/batch pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget, 1)

        # Create single page view (hybrid MVC)
        self.single_page_view = SinglePageView(self.db_path, self)
        self.stacked_widget.addWidget(self.single_page_view)

        # Create batch page view (hybrid MVC)
        self.batch_page_view = BatchPageView(self.db_path, self)
        self.stacked_widget.addWidget(self.batch_page_view)

        # Connect Navigation
        self.batch_page_view.page_changed.connect(self.page_changed)
        self.single_page_view.page_changed.connect(self.page_changed)

        # Set initial page
        self.stacked_widget.setCurrentWidget(self.single_page_view)
        # self.top_bar.left_stack.setCurrentIndex(0)
        # self.top_bar.right_stack.setCurrentIndex(0)

    def connect_signals(self):
        """Connect top bar signals and toast notifications."""
        # Connect Bulk Mode toggles between V2 (SinglePageView) and V1 (BatchPageView)
        if hasattr(self.single_page_view, "workspace_panel") and self.single_page_view.workspace_panel:
            dp = self.single_page_view.workspace_panel.display_panel
            if hasattr(dp, "bulk_mode_switch"):
                dp.bulk_mode_switch.toggled.connect(self._on_v2_bulk_toggled)

        self.batch_page_view.bulk_mode_toggled.connect(self._on_legacy_bulk_toggled)

    def _on_v2_bulk_toggled(self, checked):
        if checked:
            # Switch to Legacy V1 Batch Page with fade transition
            fade_in(self.animator, self.batch_page_view, self.stacked_widget, duration=300)
            # Synchronize batches: refresh V1
            if hasattr(self.batch_page_view, "batch_layout"):
                self.batch_page_view.batch_layout.data_changed.emit()
            # Synchronize switch on legacy header
            self.batch_page_view.legacy_bulk_switch.blockSignals(True)
            self.batch_page_view.legacy_bulk_switch.setChecked(True)
            self.batch_page_view.legacy_bulk_switch.blockSignals(False)

    def _on_legacy_bulk_toggled(self, checked):
        if not checked:
            # Switch back to V2 Layout with fade transition
            fade_in(self.animator, self.single_page_view, self.stacked_widget, duration=300)
            
            # Defer/stop V1 thumbnail generation and reset lazy load limit immediately (Task 4)
            if hasattr(self.batch_page_view, "batch_layout"):
                self.batch_page_view.batch_layout.stop_thumbnail()
                self.batch_page_view.batch_layout.limit = 10
                
            # Synchronize batches: refresh V2
            if hasattr(self.single_page_view, "batch_panel") and self.single_page_view.batch_panel:
                self.single_page_view.batch_panel._load_batches()
            # Synchronize switch on V2 header
            if hasattr(self.single_page_view, "workspace_panel") and self.single_page_view.workspace_panel:
                dp = self.single_page_view.workspace_panel.display_panel
                if hasattr(dp, "bulk_mode_switch"):
                    dp.bulk_mode_switch.blockSignals(True)
                    dp.bulk_mode_switch.setChecked(False)
                    dp.bulk_mode_switch.blockSignals(False)

        # Single page buttons
        # self.top_bar.single_page_import_button.clicked.connect(
        #     self.single_page_view.handle_import_button
        # )
        # self.top_bar.single_page_delete_button.clicked.connect(
        #     self.single_page_view.handle_delete_button
        # )

        # Batch page buttons
        # self.top_bar.batch_page_import_button.clicked.connect(
        #     self.batch_page_view.handle_batch_import_button
        # )
        # self.top_bar.batch_page_delete_button.clicked.connect(
        #     self.batch_page_view.handle_delete_all_batches
        # )
        # self.top_bar.start_process_batch.clicked.connect(
        #     self.batch_page_view.process_all_batches
        # )

        # Connect batch layout toast to main toast manager
        if hasattr(self.batch_page_view, "batch_layout"):
            if hasattr(self.batch_page_view.batch_layout, "show_toast_requested"):
                self.batch_page_view.batch_layout.show_toast_requested.connect(
                    self._handle_legacy_toast
                )

    def _handle_legacy_toast(self, message, duration_or_category, is_progress):
        """Handle legacy toast notifications from BatchPageLayout V1."""
        if is_progress:
            category = duration_or_category if isinstance(duration_or_category, str) else "legacy_batch_progress"
            self.toast_manager.show_progress(message, category=category)
        else:
            duration = duration_or_category if isinstance(duration_or_category, int) else 3000
            self.toast_manager.show_message(message, duration=duration)

    def _handle_switch_request(self):
        """Handle switch between single and batch pages."""
        # if self.top_bar.single_button.isChecked():
        #     target_widget = self.single_page_view
        #     target_index = 0
        #     slide_direction = SlideDirection.RIGHT
        # elif self.top_bar.batch_button.isChecked():
        #     target_widget = self.batch_page_view
        #     target_index = 1
        #     slide_direction = SlideDirection.LEFT
        # else:
        #     return
        return  # Disable switching via TopBar for now

        # Animate transition
        # slide(
        #     self.animator,
        #     self.stacked_widget,
        #     target_widget,
        #     slide_direction,
        #     duration=400,
        # )

        # Switch top bar stacks
        # Switch top bar stacks
        # self.top_bar.left_stack.setCurrentIndex(target_index)
        # self.top_bar.right_stack.setCurrentIndex(target_index)
