"""
WorkspaceLeftPanel - General Left Panel
=========================================
Clone dari enhance_stack LeftPanel UI shell.
Display panel (atas) + Parameter panel (bawah) dengan adaptive responsive layout.

Layout:
┌──────────────────────────────┐
│  DisplayPanel (flex 1)       │
├──────────────────────────────┤
│  ParameterPanel (collapsible)│
│  - AdaptiveStackedWidget     │
│  - Slide UP/DOWN animation   │
│  - Fixed 230px / Flex 50%    │
└──────────────────────────────┘
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QBoxLayout,
)
from PySide6.QtCore import Signal, Slot, QTimer

from resources.animations.animation_manager import (
    StackedWidgetAnimator,
    SlideDirection,
)
from resources.animations.slide import slide


class AdaptiveStackedWidget(QStackedWidget):
    """QStackedWidget yang menyesuaikan ukuran ke widget aktif."""

    def minimumSizeHint(self):
        if self.currentWidget():
            return self.currentWidget().minimumSizeHint()
        return super().minimumSizeHint()

    def sizeHint(self):
        if self.currentWidget():
            return self.currentWidget().sizeHint()
        return super().sizeHint()


class WorkspaceLeftPanel(QWidget):
    """
    General left panel - UI clone dari enhance_stack LeftPanel.

    Container untuk display panel (atas) dan parameter panel (bawah)
    dengan adaptive responsive sizing.

    Fitur:
    - Adaptive layout: fixed 230px pada layar kecil, flex 50% pada layar besar
    - Panel parameter bisa collapse/expand dengan animasi slide UP/DOWN
    """

    # Signals
    process_requested = Signal(dict)
    previewImageRequested = Signal(list)
    imagesDropped = Signal(list)
    page_changed = Signal(int)

    def __init__(self, display_panel=None, parameter_panel=None,
                 controller=None, store=None):
        super().__init__()
        self.controller = controller
        self.store = store
        self.animator = None
        self._last_visibility = None

        # Panels di-inject dari luar (bukan abstract method)
        self.display_panel = display_panel
        self.algorithm_panel = parameter_panel

        self._setup_ui()
        self._connect_internal_signals()

    def _setup_ui(self):
        """Setup UI dengan display panel dan parameter panel."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. Display Panel (Top) ---
        if self.display_panel:
            self.display_panel.page_changed.connect(self.page_changed)
            main_layout.addWidget(self.display_panel, 1)

        # --- 2. Algorithm Panel (Bottom) dengan Stacked Widget ---
        self.algorithm_stack = AdaptiveStackedWidget()
        self.animator = StackedWidgetAnimator(self.algorithm_stack)

        # Empty widget untuk collapsed state
        self.empty_algorithm_widget = QWidget()
        self.empty_algorithm_widget.setMaximumHeight(0)

        self.algorithm_stack.addWidget(self.empty_algorithm_widget)  # Index 0
        if self.algorithm_panel:
            self.algorithm_stack.addWidget(self.algorithm_panel)     # Index 1
        self.algorithm_stack.currentChanged.connect(
            lambda: QTimer.singleShot(0, self._update_layout_responsive)
        )
        self.algorithm_stack.setCurrentIndex(0)  # Start collapsed

        main_layout.addWidget(self.algorithm_stack, 0)

    def _connect_internal_signals(self):
        """Hubungkan sinyal internal antar panel."""
        if self.algorithm_panel:
            self.algorithm_panel.process_requested.connect(self._forward_process_requested)
            self.algorithm_panel.processing_completed.connect(self._on_algorithm_completed)
            self.algorithm_panel.visibility_state_changed.connect(
                self._handle_algorithm_panel_visibility
            )

        if self.display_panel:
            self.previewImageRequested.connect(
                lambda _: self.display_panel.show_preview()
            )

    # =========================================================================
    # === ADAPTIVE LAYOUT ===
    # =========================================================================

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_layout_responsive()

    def _update_layout_responsive(self):
        """
        Adjust layout berdasarkan threshold height.
        - Height < 850: Parameter Panel fixed 230px
        - Height >= 850: Parameter Panel flex 50%
        """
        if self.algorithm_stack.currentWidget() == self.empty_algorithm_widget:
            self.algorithm_stack.setMaximumHeight(16777215)
            self.algorithm_stack.setFixedHeight(16777215)
            self.algorithm_stack.setMinimumHeight(0)
            self.algorithm_stack.updateGeometry()
            return

        current_height = self.height()
        layout = self.layout()
        if not layout or not isinstance(layout, QBoxLayout):
            return

        # Collapsed state
        if self.algorithm_stack.currentIndex() == 0:
            self.algorithm_stack.setFixedHeight(0)
            layout.setStretch(0, 1)
            layout.setStretch(1, 0)
            return

        LARGE_HEIGHT_THRESHOLD = 850

        if current_height >= LARGE_HEIGHT_THRESHOLD:
            # FLEX MODE (50-50)
            self.algorithm_stack.setMinimumHeight(0)
            self.algorithm_stack.setMaximumHeight(16777215)
            layout.setStretch(0, 1)
            layout.setStretch(1, 1)
        else:
            # FIXED MODE (Small Screen) -> 230px
            self.algorithm_stack.setFixedHeight(230)
            layout.setStretch(0, 1)
            layout.setStretch(1, 0)

    # =========================================================================
    # === PANEL VISIBILITY (Collapse/Expand Animation) ===
    # =========================================================================

    @Slot()
    def clear_display(self):
        """Clear display saat tidak ada item yang dipilih."""
        if self.animator:
            self.animator.stop_all()
        if self.display_panel:
            self.display_panel.clear_display()
        self._handle_algorithm_panel_visibility(False)

    def _handle_algorithm_panel_visibility(self, visible: bool):
        """Handle visibility changes dari parameter panel."""
        if self._last_visibility == visible:
            return
        self._last_visibility = visible

        if not self.animator or not self.algorithm_panel:
            return

        target_widget = self.algorithm_panel if visible else self.empty_algorithm_widget
        direction = SlideDirection.UP if visible else SlideDirection.DOWN

        if self.algorithm_stack.currentWidget() != target_widget:
            slide(
                self.animator,
                self.algorithm_stack,
                target_widget,
                direction,
                duration=400,
            )

    def load_batch(self, batch_id, images, batch_name=None):
        """Load batch/item ke display dan show parameter panel."""
        if self.animator:
            self.animator.stop_all()
        if self.display_panel:
            self.display_panel.load_batch(batch_id, images, batch_name)

        if self.algorithm_panel:
            self.algorithm_panel.set_current_batch(batch_id)
            current_settings = self.algorithm_panel.get_settings()
            self.algorithm_panel.update_settings(current_settings)

    def _forward_process_requested(self, settings):
        """Forward process_requested signal dari parameter panel."""
        self.process_requested.emit(settings)

    def _on_algorithm_completed(self, data):
        """Handle algorithm completion. Subclass BISA override untuk display result."""
        pass

    @Slot(list)
    def _on_images_imported(self, file_paths):
        """Handle imported images. Forward ke parent."""
        self.imagesDropped.emit(file_paths)

    def remove_selected_images(self):
        """Remove selected images. Forward ke display panel."""
        if self.display_panel:
            self.display_panel.remove_selected_images()

    def get_select_image_list(self):
        """Get selected image list. Forward ke display panel."""
        if self.display_panel:
            return self.display_panel.get_selected_image_list()
        return []
