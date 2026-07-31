"""
Enhanced Stack Page View (MVC Refactored).
Main container for single and batch page views with controller integration.
Subclass of WorkspaceView from workplace framework.
"""

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QWidget
from pixel_refine_desktop.workplace.workspace_view import WorkspaceView
from .single_page_view import SinglePageView
from .batch_page_view import BatchPageView


class EnhanceStackView(WorkspaceView):
    """
    Main view for enhance stack feature (MVC Architecture).
    Subclass of WorkspaceView - implementasi spesifik enhance_stack.
    """

    page_changed = Signal(int)  # Forward global navigation

    def __init__(self, db_path: str, parent=None):
        # WorkspaceView.__init__ akan memanggil _create_pages() dan _connect_page_signals()
        self.batch_page_view = None
        self._batch_placeholder = None
        self._batch_signals_connected = False
        super().__init__(db_path, parent)
        QTimer.singleShot(750, self.preload_batch_page)

    def _create_pages(self):
        """Buat halaman-halaman enhance_stack dan tambahkan ke stacked_widget."""
        # Create single page view (hybrid MVC)
        self.single_page_view = SinglePageView(self.db_path, self)
        self.stacked_widget.addWidget(self.single_page_view)

        # Bulk/legacy batch page is heavier than the default page, so startup
        # only reserves its stack slot and loads it after the window is usable.
        self._batch_placeholder = QWidget(self)
        self.stacked_widget.addWidget(self._batch_placeholder)

    def _set_initial_page(self):
        """Set halaman awal ke single page view."""
        self.stacked_widget.setCurrentWidget(self.single_page_view)

    def _connect_page_signals(self):
        """Connect page signals and toast notifications."""
        # Connect Navigation
        self.single_page_view.page_changed.connect(self.page_changed)
        # Connect Bulk Mode toggles between V2 (SinglePageView) and V1 (BatchPageView)
        if hasattr(self.single_page_view, "workspace_panel") and self.single_page_view.workspace_panel:
            dp = self.single_page_view.workspace_panel.display_panel
            if hasattr(dp, "bulk_mode_btn"):
                dp.bulk_mode_btn.clicked.connect(self._on_v2_bulk_clicked)

        self._connect_batch_page_signals()

    def preload_batch_page(self):
        """Warm up the legacy bulk page after the main window becomes usable."""
        self._ensure_batch_page()

    def _ensure_batch_page(self):
        """Create the legacy bulk page once and replace the reserved placeholder."""
        if self.batch_page_view is not None:
            return self.batch_page_view

        self.batch_page_view = BatchPageView(self.db_path, self)
        placeholder_index = self.stacked_widget.indexOf(self._batch_placeholder)
        if placeholder_index >= 0:
            self.stacked_widget.insertWidget(placeholder_index, self.batch_page_view)
            self.stacked_widget.removeWidget(self._batch_placeholder)
            self._batch_placeholder.deleteLater()
            self._batch_placeholder = None
        else:
            self.stacked_widget.addWidget(self.batch_page_view)

        self._connect_batch_page_signals()
        return self.batch_page_view

    def _connect_batch_page_signals(self):
        if self._batch_signals_connected or self.batch_page_view is None:
            return

        self.batch_page_view.page_changed.connect(self.page_changed)
        self.batch_page_view.bulk_mode_toggled.connect(self._on_legacy_bulk_toggled)
        if hasattr(self.batch_page_view, "batch_layout"):
            if hasattr(self.batch_page_view.batch_layout, "show_toast_requested"):
                self.batch_page_view.batch_layout.show_toast_requested.connect(
                    self._handle_legacy_toast
                )
        self._batch_signals_connected = True

    def _on_v2_bulk_clicked(self):
        if hasattr(self.single_page_view, "workspace_panel") and self.single_page_view.workspace_panel:
            dp = self.single_page_view.workspace_panel.display_panel
            dp.is_bulk_mode = not dp.is_bulk_mode
            dp.set_mode_button_state(dp.is_bulk_mode)
            self._on_v2_bulk_toggled(dp.is_bulk_mode)

    def _on_v2_bulk_toggled(self, checked):
        if checked:
            batch_page = self._ensure_batch_page()
            # Direct switch avoids QPainter conflicts while the thumbnail/grid
            # pages are still repainting.
            self.animator.stop_all()
            self.stacked_widget.setCurrentWidget(batch_page)
            # Synchronize batches: refresh V1
            if hasattr(batch_page, "batch_layout"):
                batch_page.batch_layout.data_changed.emit()

    def _on_legacy_bulk_toggled(self, checked):
        if not checked:
            self.animator.stop_all()
            self.stacked_widget.setCurrentWidget(self.single_page_view)
            
            # Defer/stop V1 thumbnail generation and reset lazy load limit immediately (Task 4)
            if self.batch_page_view is not None and hasattr(self.batch_page_view, "batch_layout"):
                self.batch_page_view.batch_layout.stop_thumbnail()
                self.batch_page_view.batch_layout.limit = 10
                
            # Synchronize batches: refresh V2
            if hasattr(self.single_page_view, "batch_panel") and self.single_page_view.batch_panel:
                self.single_page_view.batch_panel._load_batches()
            # Synchronize switch on V2 header
            if hasattr(self.single_page_view, "workspace_panel") and self.single_page_view.workspace_panel:
                dp = self.single_page_view.workspace_panel.display_panel
                dp.is_bulk_mode = False
                dp.set_mode_button_state(False)

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

    def _handle_legacy_toast(self, message, duration_or_category, is_progress):
        """Handle legacy toast notifications from BatchPageLayout V1."""
        if is_progress:
            category = duration_or_category if isinstance(duration_or_category, str) else "legacy_batch_progress"
            self.toast_manager.show_progress(message, category=category)
        else:
            duration = duration_or_category if isinstance(duration_or_category, int) else 3000
            try:
                self.toast_manager.hide_progress()
            except Exception:
                pass
            self.toast_manager.show_message(message, duration=duration)
