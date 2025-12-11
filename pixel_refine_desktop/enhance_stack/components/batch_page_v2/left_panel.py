from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Signal, Slot

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

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.animator = None  # Will be initialized in _setup_ui
        self._setup_ui()

        # Connect internal signal for view switching
        self.previewImageRequested.connect(lambda _: self.display_panel.show_preview())

    def _setup_ui(self):
        """Setup UI dengan DisplayPanel dan AlgorithmPanel menggunakan stacked widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # --- 1. Display Panel (Top) ---
        self.display_panel = DisplayPanel(controller=self.controller)

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

        # Connect currentChanged to updateGeometry
        self.algorithm_stack.currentChanged.connect(
            lambda: self.algorithm_stack.updateGeometry()
        )

        self.algorithm_stack.setCurrentIndex(0)  # Start dengan collapsed

        # Add to main layout
        main_layout.addWidget(self.display_panel, 1)  # Flex 1
        main_layout.addWidget(self.algorithm_stack, 0)  # Fixed height

        # Connect signals
        self.algorithm_panel.process_requested.connect(self._forward_process_requested)
        self.display_panel.images_to_import_selected.connect(self._on_images_imported)

    @Slot()
    def clear_display(self):
        """
        Clear display saat tidak ada batch yang dipilih.
        Forward ke DisplayPanel dan hide AlgorithmPanel dengan SLIDE_DOWN animation.
        """
        self.display_panel.clear_display()

        # Hide algorithm panel dengan slide down animation
        slide(
            self.animator,
            self.algorithm_stack,
            self.empty_algorithm_widget,
            SlideDirection.DOWN,
            duration=400,
        )

    def load_batch(self, batch_id, images):
        """
        Load batch images dan show AlgorithmPanel dengan SLIDE_UP animation.
        Forward ke DisplayPanel dan expand AlgorithmPanel.

        Args:
            batch_id: ID dari batch
            images: List of image objects
        """
        self.display_panel.load_batch(batch_id, images)

        # Show algorithm panel ONLY if there are images
        if images:
            slide(
                self.animator,
                self.algorithm_stack,
                self.algorithm_panel,
                SlideDirection.UP,
                duration=400,
            )
        else:
            # If batch is empty (no images), keep collapsed/collapse it
            slide(
                self.animator,
                self.algorithm_stack,
                self.empty_algorithm_widget,
                SlideDirection.DOWN,
                duration=400,
            )

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
