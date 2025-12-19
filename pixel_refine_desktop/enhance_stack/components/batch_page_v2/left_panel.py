from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QSizePolicy,
    QLayout,
    QBoxLayout,
)
from PySide6.QtWidgets import (
    QApplication,
    QWidget as QWIDGETSIZE_MAX_SOURCE,
)  # Hack to access constant if not direct


from PySide6.QtCore import Signal, Slot, QTimer

# Panel components
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.display_panel import (
    DisplayPanel,
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.algorithm_panel import (
    AlgorithmPanel,
)

# Animation support
from pixel_refine_desktop.ui.resources.animations.animation_manager import (
    StackedWidgetAnimator,
    SlideDirection,
)
from pixel_refine_desktop.ui.resources.animations.slide import slide


class AdaptiveStackedWidget(QStackedWidget):
    """
    QStackedWidget that resizes to fit its current widget.
    """

    def minimumSizeHint(self):
        if self.currentWidget():
            return self.currentWidget().minimumSizeHint()
        return super().minimumSizeHint()

    def sizeHint(self):
        if self.currentWidget():
            return self.currentWidget().sizeHint()
        return super().sizeHint()


class LeftPanel(QWidget):
    """
    Main Workspace Panel untuk Enhance Stack.
    Orchestrator yang mengelola DisplayPanel dan AlgorithmPanel.

    Structure:
    1. DisplayPanel (Top) - Grid images dan full resolution preview
    2. AlgorithmPanel (Bottom) - Workflow settings dan processing
    """

    # Signals
    process_requested = Signal(dict)  # Emit settings dict
    previewImageRequested = Signal(list)  # Emit list of image paths
    imagesDropped = Signal(list)  # Drag and drop support
    page_changed = Signal(int)  # Forward global navigation

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.animator = None  # Will be initialized in _setup_ui
        self._last_visibility = None  # Guard for redundant animations
        self._setup_ui()

        # Connect internal signal for view switching
        self.previewImageRequested.connect(lambda _: self.display_panel.show_preview())

    def _setup_ui(self):
        """Setup UI dengan DisplayPanel dan AlgorithmPanel menggunakan stacked widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. Display Panel (Top) ---
        self.display_panel = DisplayPanel(controller=self.controller)
        # Forward page changed signal from sidebar in display panel
        self.display_panel.page_changed.connect(self.page_changed)

        # --- 2. Algorithm Panel (Bottom) dengan Stacked Widget untuk collapse/expand ---
        # Create stacked widget untuk algorithm panel animation
        self.algorithm_stack = AdaptiveStackedWidget()
        self.animator = StackedWidgetAnimator(self.algorithm_stack)

        self.algorithm_panel = AlgorithmPanel(controller=self.controller)

        # Empty widget sebagai default (untuk initial collapsed state)
        self.empty_algorithm_widget = QWidget()
        self.empty_algorithm_widget.setMaximumHeight(0)  # Collapsed state

        self.algorithm_stack.addWidget(
            self.empty_algorithm_widget
        )  # Index 0 - collapsed
        self.algorithm_stack.addWidget(self.algorithm_panel)  # Index 1 - expanded
        # Connect signals for adaptivity
        self.algorithm_stack.currentChanged.connect(
            lambda: QTimer.singleShot(0, self._update_layout_responsive)
        )

        self.algorithm_stack.setCurrentIndex(0)  # Start dengan collapsed

        # Add to main layout
        main_layout.addWidget(self.display_panel, 1)  # Flex 1
        main_layout.addWidget(self.algorithm_stack, 0)  # Fixed height

        # Connect signals
        self.algorithm_panel.process_requested.connect(self._forward_process_requested)
        self.algorithm_panel.processing_completed.connect(self._on_algorithm_completed)
        self.display_panel.images_to_import_selected.connect(self._on_images_imported)
        self.algorithm_panel.visibility_state_changed.connect(
            self._handle_algorithm_panel_visibility
        )

        # The connection is already made above with QTimer for safety

    def resizeEvent(self, event):
        """Handle resize to switch between fixed height and flex ratio for algorithm panel."""
        super().resizeEvent(event)
        self._update_layout_responsive()

    def _update_layout_responsive(self):
        """
        Adjust layout based on height threshold.
        - Height < 850px: Algorithm Panel fixed 230px (approx 30%)
        - Height >= 850px: Algorithm Panel flex 50%
        Only applies if Algo Panel is visible (not collapsed).
        """
        # If collapsed (showing empty widget), let stack handle height (0)
        if self.algorithm_stack.currentWidget() == self.empty_algorithm_widget:
            self.algorithm_stack.setMaximumHeight(16777215)  # Reset max
            # Actually, standard stack behavior handles it if empty widget has max height 0
            # But we might need to reset fixed height constraints from previous state
            self.algorithm_stack.setFixedHeight(16777215)
            self.algorithm_stack.setMinimumHeight(0)
            self.algorithm_stack.updateGeometry()
            return

        current_height = self.height()
        LARGE_HEIGHT_THRESHOLD = 850

        # Access layout to change stretch
        layout = self.layout()
        if not layout or not isinstance(layout, QBoxLayout):
            return

        # COLLAPSED state logic
        if self.algorithm_stack.currentIndex() == 0:
            self.algorithm_stack.setFixedHeight(0)
            layout.setStretch(0, 1)
            layout.setStretch(1, 0)
            return

        if current_height >= LARGE_HEIGHT_THRESHOLD:
            # FLEX MODE (50-50)
            # Reset fixed height constraint
            self.algorithm_stack.setMinimumHeight(0)
            self.algorithm_stack.setMaximumHeight(16777215)

            # Set stretch factors: Display 1, Algo 1 (Equals 50/50 if spacing ignored)
            # Note: addWidget(widget, stretch)
            # We can't easily change stretch of existing items without remove/add or internal layout API
            # But QVBoxLayout has setStretch(index, stretch)

            layout.setStretch(0, 1)  # DisplayPanel
            layout.setStretch(1, 1)  # AlgorithmStack

        else:
            # FIXED MODE (Small Screen) -> 230px
            # Enforce fixed height
            self.algorithm_stack.setFixedHeight(230)

            # Set stretch so DisplayPanel takes all remaining space
            layout.setStretch(0, 1)  # DisplayPanel
            layout.setStretch(1, 0)  # AlgorithmStack (Fixed size)

    @Slot()
    def clear_display(self):
        """
        Clear display saat tidak ada batch yang dipilih.
        Forward ke DisplayPanel dan hide AlgorithmPanel dengan SLIDE_DOWN animation.
        """
        self.display_panel.clear_display()
        self._handle_algorithm_panel_visibility(False)

    def _handle_algorithm_panel_visibility(self, visible):
        """
        Handle visibility changes from AlgorithmPanel.
        Expand or collapse the panel with animation.
        """
        if self._last_visibility == visible:
            return
        self._last_visibility = visible

        if not self.animator:
            return

        target_widget = self.algorithm_panel if visible else self.empty_algorithm_widget
        direction = SlideDirection.UP if visible else SlideDirection.DOWN

        # Only slide if the current widget is different
        if self.algorithm_stack.currentWidget() != target_widget:
            slide(
                self.animator,
                self.algorithm_stack,
                target_widget,
                direction,
                duration=400,
            )

    def load_batch(self, batch_id, images, batch_name=None):
        """
        Load batch images dan show AlgorithmPanel dengan SLIDE_UP animation.
        Forward ke DisplayPanel dan expand AlgorithmPanel.

        Args:
            batch_id: ID dari batch
            images: List of image objects
            batch_name: Nama dari batch (optional)
        """
        self.display_panel.load_batch(batch_id, images, batch_name)

        # Set current batch in algorithm panel for processing
        self.algorithm_panel.set_current_batch(batch_id)

        # The visibility is now handled by _handle_algorithm_panel_visibility
        # which will be triggered if the RightPanel emits settings or if we manually refresh.
        # Check initial state:
        current_settings = self.algorithm_panel.get_settings()
        self.algorithm_panel._update_adaptive_ui(current_settings)

    def _forward_process_requested(self, settings):
        """Forward process_requested signal dari AlgorithmPanel."""
        self.process_requested.emit(settings)

    @Slot(list)
    def _on_images_imported(self, file_paths):
        """
        Handle imported images dari drag & drop.
        Forward ke parent untuk database processing.

        Args:
            file_paths: List of image file paths
        """
        self.imagesDropped.emit(file_paths)

    def remove_selected_images(self):
        """Remove selected images. Forward ke DisplayPanel."""
        self.display_panel.remove_selected_images()

    def get_select_image_list(self):
        """Get selected image list. Forward ke DisplayPanel."""
        return self.display_panel.get_selected_image_list()

    def load_image_paths(self):
        """Refresh grid. Stub untuk compatibility."""
        pass

    def _on_algorithm_completed(self, data):
        """
        Handle algorithm completion to display result.

        Args:
            data: dict containing 'batch_id' and 'settings'
        """
        import os
        import glob

        batch_id = data.get("batch_id")
        settings = data.get("settings", {})

        if not batch_id or not self.controller:
            return

        # Determine process type (Average, Median, Similarity)
        # Check based on priority or what was likely run
        denoising = settings.get("denoising")

        process_suffix = None
        if denoising in ["Average", "Median", "Similarity"]:
            process_suffix = denoising.lower()

        # If no relevant process found that produces a stack result, possibly skip
        # Add others if needed (e.g. if Alignment produces a visualization?)
        if not process_suffix:
            return

        # Get batch images to determine filename pattern
        batch = self.controller.get_batch(batch_id)
        if not batch or not batch.images:
            return

        first_image_path = batch.images[0].path
        first_image_name = os.path.splitext(os.path.basename(first_image_path))[0]

        # Safe name logic from Average.py:
        # "".join(c for c in ref_name if c.isalnum() or c in ("_", "-")).rstrip()
        output_name_safe = "".join(
            c for c in first_image_name if c.isalnum() or c in ("_", "-")
        ).rstrip()

        # Construct expected path
        # Pattern: database/stack/[safe_name]_[process].tif
        # Note: We need absolute path. Assuming database is relative to CWD (root of execution)
        # Or using self.controller.db_path's directory as base?
        # Standard app runs from root, so 'database/stack' should work relative to CWD.

        stack_dir = os.path.abspath("database/stack")
        expected_filename = f"{output_name_safe}_{process_suffix}.tif"
        expected_path = os.path.join(stack_dir, expected_filename)

        # Fallback/Loose search if exact match fails (e.g. timestamp differences?)
        # But try exact first.

        if os.path.exists(expected_path):
            self.display_panel.display_processed_result(expected_path)
        else:
            print(f"[LeftPanel] Result file not found: {expected_path}")

            # Additional fallback: Check if ANY result exists and show that instead
            # This helps if naming conventions drift
            results = self.display_panel.logic.detect_processed_results(
                first_image_path
            )
            if results:
                print(f"[LeftPanel] Falling back to found result: {results[0]['path']}")
                self.display_panel.display_processed_result(results[0]["path"])
