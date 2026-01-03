"""
UI State Manager - Handles UI state management and placeholder widgets.
Manages header titles, placeholders, and supported file extensions.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional, Callable
from config import SUPPORTED_FORMATS
from pixel_refine_desktop.ui.resources.GenericUILibrary import Button
from pixel_refine_desktop.ui.resources.animations.slide import slide
from pixel_refine_desktop.ui.resources.animations.animation_manager import (
    SlideDirection,
)


class UIStateManager:
    """Manages UI state, placeholders, and header information."""

    def __init__(self, parent_panel):
        """
        Initialize UIStateManager.

        Args:
            parent_panel: Reference to DisplayPanel for accessing UI components
        """
        self.panel = parent_panel
        self.supported_extensions = self._build_supported_extensions()

    def _build_supported_extensions(self) -> tuple:
        """
        Build tuple of supported file extensions from config.

        Returns:
            Tuple of supported extensions
        """
        extensions = []
        for format_name, ext_list in SUPPORTED_FORMATS.items():
            extensions.extend(ext_list)
        return tuple(extensions)

    def create_placeholder_widget(
        self,
        html_text: str = "",
        button_text: Optional[str] = None,
        on_button_click: Optional[Callable] = None,
    ) -> QWidget:
        """
        Create placeholder widget to display when grid is empty.
        Follows pattern from panorama with flexible layout.

        Args:
            html_text: HTML text to display
            button_text: Text for button (optional)
            on_button_click: Callback for button click (optional)

        Returns:
            QWidget: Container with layout stretch + label + button (if provided)
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Top stretch for vertical centering
        layout.addStretch()

        # Text label
        if html_text:
            label = QLabel(html_text)
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            label.setStyleSheet("QLabel { color: #888; font-size: 14px; }")
            layout.addWidget(label)

        # Button (if provided)
        if button_text and on_button_click:
            btn = Button(button_text, variant="secondary")
            btn.setFixedWidth(120)
            btn.clicked.connect(on_button_click)

            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(btn)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)

        # Bottom stretch for vertical centering
        layout.addStretch()

        return container

    def set_placeholder(self, widget: Optional[QWidget]):
        """
        Set placeholder widget in stack.
        Safely removes previous placeholder if exists.

        Args:
            widget: Generic widget/container to show, or None to show grid
        """
        # Remove old placeholder if exists and is different from new widget
        if self.panel.placeholder_widget and self.panel.placeholder_widget != widget:
            try:
                self.panel.grid_content_stack.removeWidget(
                    self.panel.placeholder_widget
                )
                self.panel.placeholder_widget.deleteLater()
            except RuntimeError:
                pass  # Widget already deleted
            self.panel.placeholder_widget = None

        # Add and show new placeholder
        if widget:
            self.panel.placeholder_widget = widget
            self.panel.grid_content_stack.addWidget(widget)
            # Slide DOWN for showing placeholder (content leaves)
            slide(
                self.panel.grid_animator,
                self.panel.grid_content_stack,
                widget,
                SlideDirection.DOWN,
                duration=300,
            )
        else:
            # Placeholder -> Grid = Slide UP (Content arrives)
            slide(
                self.panel.grid_animator,
                self.panel.grid_content_stack,
                self.panel.grid_container,
                SlideDirection.UP,
                duration=300,
            )

    def show_empty_batch_state(self):
        """
        Show empty state when batch is selected but has no images.
        Display informative message + button to import images directly.
        """
        placeholder_html = "<p>Drag and drop images ke sini,<br>atau gunakan tombol di atas untuk memilih dari folder.</p>"
        placeholder = self.create_placeholder_widget(html_text=placeholder_html)
        self.set_placeholder(placeholder)

    def show_no_batch_state(self, on_create_batch: Callable):
        """
        Show state when no batch is selected.
        Display message with "New Batch" button.

        Args:
            on_create_batch: Callback for creating new batch
        """
        placeholder_html = "<p>Create a new batch to get started.</p>"
        placeholder = self.create_placeholder_widget(
            html_text=placeholder_html,
            button_text="New Batch",
            on_button_click=on_create_batch,
        )
        self.set_placeholder(placeholder)

    def update_header_title(
        self,
        batch_id: Optional[int] = None,
        batch_name: Optional[str] = None,
        count: Optional[int] = None,
    ):
        """
        Update header title with batch name and image count.

        Args:
            batch_id: Current batch ID
            batch_name: Current batch name
            count: Image count to display
        """
        if not batch_id:
            self.panel.header_title.setText("No batch selected")
            return

        display_name = batch_name if batch_name else str(batch_id)

        # Use provided count or fall back to panel's total_image_count
        actual_count = count if count is not None else self.panel.total_image_count
        self.panel.header_title.setText(f"{display_name}: ({actual_count} image)")

    def get_supported_extensions(self) -> tuple:
        """
        Get tuple of supported file extensions.

        Returns:
            Tuple of supported extensions
        """
        return self.supported_extensions
