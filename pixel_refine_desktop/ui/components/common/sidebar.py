"""
Reusable Sidebar Component (MVC).
100% identical to legacy UI/sidebar.py with all features, animations, and styling.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot, QEasingCurve, Signal, Qt, QSize
from resources.animations.animation_manager import WidthAnimator
from resources.styles import stylesheet


class Sidebar(QWidget):
    """
    Reusable sidebar component with expand/collapse animation.
    Identical to legacy sidebar but accepts dynamic pages configuration.
    """

    # Constants
    EXPANDED_WIDTH = 60  # Icon-only width
    COLLAPSED_WIDTH = 60  # Same as expanded since we only show icons
    ANIMATION_DURATION = 250
    ANIMATION_CURVE = QEasingCurve.Type.InOutQuad

    # Signals
    page_changed = Signal(int)  # Emitted when page button is clicked
    toggle_requested = Signal()  # Emitted when toggle button is clicked

    def __init__(self, pages: list | None = None, parent=None):
        """
        Initialize sidebar.

        Args:
            pages: List of tuples (name, icon_path) for all pages
                   Settings will automatically be placed at bottom
            parent: Parent widget
        """
        super().__init__(parent)

        self.expanded_width = self.EXPANDED_WIDTH
        self.collapsed_width = self.COLLAPSED_WIDTH
        self.sidebar_expanded = True
        self.pages = pages or []

        # Animation manager
        self.width_animator = WidthAnimator(self)

        # Styling
        self.setStyleSheet(stylesheet.SIDEBAR_STYLE)

        # Layout sidebar
        self.sidebar_layout = QVBoxLayout()
        self.setLayout(self.sidebar_layout)

        # Create UI
        self.side_buttons = []
        self._create_ui()

        # Set initial width
        self.setFixedWidth(self.expanded_width)

    def _create_ui(self):
        """Create sidebar UI elements."""

        # Separate pages into main and footer (settings)
        main_pages = []
        footer_pages = []

        for idx, (name, icon_path) in enumerate(self.pages):
            if name.lower() == "settings":
                footer_pages.append((idx, name, icon_path))
            else:
                main_pages.append((idx, name, icon_path))

        # Create main navigation buttons
        for idx, text, icon_path in main_pages:
            btn = self.create_nav_button(text, icon_path, idx)
            self.sidebar_layout.addWidget(btn)
            self.side_buttons.append(btn)

        # Add stretch to push settings to bottom
        self.sidebar_layout.addStretch()

        # Create footer navigation buttons (Settings)
        for idx, text, icon_path in footer_pages:
            btn = self.create_nav_button(text, icon_path, idx)
            self.sidebar_layout.addWidget(btn)
            self.side_buttons.append(btn)

    def create_nav_button(self, text, icon_path, index):
        """
        Create a navigation button with icon only and tooltip.
        """
        btn = QPushButton("")  # No text, icon only
        icon = QIcon()
        icon.addFile(icon_path, QSize(28, 28), QIcon.Mode.Normal)
        icon.addFile(icon_path, QSize(28, 28), QIcon.Mode.Active)
        icon.addFile(icon_path, QSize(28, 28), QIcon.Mode.Selected)
        btn.setIcon(icon)
        btn.setIconSize(QSize(28, 28))
        btn.setCheckable(True)
        btn.setToolTip(text)  # Set tooltip to show name on hover
        btn.setToolTipDuration(0)  # Tooltip stays until mouse leaves

        btn.setStyleSheet(stylesheet.SIDEBAR_NAV_BUTTON_STYLE)
        # Use lambda with default argument to capture index correctly
        btn.clicked.connect(
            lambda checked=False, idx=index: self._handle_nav_click(idx)
        )
        btn.setProperty("default_text", text)  # Store original text for reference
        return btn

    @Slot(int)
    def _handle_nav_click(self, index):
        """
        Handle navigation button click.
        Updates button states and emits page_changed signal.
        """
        for i, btn in enumerate(self.side_buttons):
            btn.setChecked(i == index)
        self.page_changed.emit(index)

    def toggle_sidebar(self):
        """
        Toggle sidebar expand/collapse with animation.
        Note: Since sidebar is now icon-only, this mainly handles the toggle signal.
        """
        target_expanded = not self.sidebar_expanded
        end_width = self.expanded_width if target_expanded else self.collapsed_width

        # Update state immediately
        self.sidebar_expanded = target_expanded
        # Removed text update as button is external now
        # self.toggle_button.setText("☰" if target_expanded else "➡")

        # Emit toggle signal
        self.toggle_requested.emit()

        # Animate width using WidthAnimator (if needed, though width is same in both states now)
        self.width_animator.animate_width(
            target_widget=self,
            end_width=end_width,
            duration=self.ANIMATION_DURATION,
            curve=self.ANIMATION_CURVE,
        )

    def set_current_page(self, index: int):
        """
        Set the current active page.
        Updates button checked states.
        """
        for i, btn in enumerate(self.side_buttons):
            btn.setChecked(i == index)
