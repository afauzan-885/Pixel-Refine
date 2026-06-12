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
        on_link_activated: Optional[Callable[[str], None]] = None,
    ) -> QWidget:
        """
        Create placeholder widget to display when grid is empty.
        Follows pattern from panorama with flexible layout.

        Args:
            html_text: HTML text to display
            button_text: Text for button (optional)
            on_button_click: Callback for button click (optional)
            on_link_activated: Callback for link click (optional)

        Returns:
            QWidget: Container with layout stretch + label + button (if provided)
        """
        container = QWidget()
        container.setObjectName("PlaceholderWidget")
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        container.setStyleSheet(
            "#PlaceholderWidget { background-color: transparent; }"
        )
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        # Create nested card widget (green box/focused card)
        card = QWidget()
        card.setObjectName("PlaceholderCard")
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card.setStyleSheet(
            "#PlaceholderCard { background-color: #F5F8FA; border: 1px solid #E2E8F0; border-radius: 8px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 35, 35, 35)
        card_layout.setSpacing(15)

        # Text label inside card
        if html_text:
            label = QLabel(html_text)
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            label.setStyleSheet("QLabel { color: #888; font-size: 14px; }")
            if on_link_activated:
                label.linkActivated.connect(on_link_activated)
            card_layout.addWidget(label)

        # Button (if provided) inside card
        if button_text and on_button_click:
            btn = Button(button_text, variant="secondary")
            btn.setFixedWidth(120)
            btn.clicked.connect(on_button_click)

            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(btn)
            btn_layout.addStretch()
            card_layout.addLayout(btn_layout)

        # Top stretch for vertical centering
        layout.addStretch()

        # Let the card stretch horizontally across the screen as requested
        layout.addWidget(card)

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
        placeholder_html = """
        <div style="text-align: center; max-width: 600px; margin: 0 auto; font-family: 'Segoe UI', Arial, sans-serif;">
            <div style="font-size: 64px; color: #cbd5e1; margin-bottom: 10px;">🖼️</div>
            <div style="font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 4px; line-height: 1.25;">This Batch is Empty</div>
            <div style="font-size: 13px; color: #64748b; margin: 0; line-height: 1.3;">
                Drag and drop images here, or use the "Import Images" button in the toolbar to load pictures into this batch.
            </div>
        </div>
        """
        placeholder = self.create_placeholder_widget(html_text=placeholder_html)
        self.set_placeholder(placeholder)

    def show_no_batch_state(self, on_create_batch: Callable, on_import_click: Optional[Callable] = None):
        """
        Show state when no batch is selected.
        Display message with clickable folder icon.

        Args:
            on_create_batch: Callback for creating new batch
            on_import_click: Callback for importing images into a new batch
        """
        placeholder_html = """
        <div style="text-align: center; max-width: 520px; margin: 0 auto; font-family: 'Segoe UI', Arial, sans-serif;">
            <a href="import_no_batch" style="text-decoration: none; outline: none;">
                <div style="font-size: 52px; color: #94a3b8; margin-bottom: 16px;">📁</div>
            </a>
            <div style="font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 8px; letter-spacing: -0.01em;">
                No Batches Yet
            </div>
            <div style="font-size: 12.5px; color: #64748b; line-height: 1.7; margin: 0;">
                Click the <a href="import_no_batch" style="color: #3b82f6; text-decoration: none; font-weight: 500;">folder icon</a> above to select images and create your first batch.
            </div>
        </div>
        """

        def link_handler(link):
            if link == "import_no_batch" and on_import_click:
                on_import_click()

        placeholder = self.create_placeholder_widget(
            html_text=placeholder_html,
            button_text=None,
            on_button_click=None,
            on_link_activated=link_handler,
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
