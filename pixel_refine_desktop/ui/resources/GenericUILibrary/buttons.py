"""
Bootstrap-like Button Components for PySide6
Provides reusable button components with variants and customization
"""

from PySide6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QIcon
from . import theme


class Button(QPushButton):
    """
    Bootstrap-like button with variant support

    Variants:
    - primary: Main action button (green)
    - secondary: Secondary action (gray)
    - danger: Destructive action (red)
    - success: Success action (green)
    - warning: Warning action (yellow/orange)
    - info: Information action (blue)
    - light: Light background
    - dark: Dark background

    Usage:
        btn = Button("Click Me", variant="primary")
        btn.clicked.connect(on_click)
    """

    def __init__(
        self,
        text="",
        variant="secondary",
        object_name=None,
        bg_color=None,
        text_color=None,
        hover_color=None,
        parent=None,
    ):
        super().__init__(text, parent)
        self.variant = variant

        # Set object name for styling
        if object_name:
            self.setObjectName(object_name)
        else:
            # Auto-assign based on variant
            variant_names = {
                "primary": "processButton",
                "success": "addButton",
                "danger": "deleteButton",
                "info": "importButton",
            }
            if variant in variant_names:
                self.setObjectName(variant_names[variant])

        # Apply custom colors if provided (overrides stylesheet)
        if bg_color or text_color or hover_color:
            self._apply_custom_colors(bg_color, text_color, hover_color)

    def _apply_custom_colors(self, bg_color=None, text_color=None, hover_color=None):
        """Apply custom colors via inline stylesheet"""

        theme_obj = theme.get_theme()

        # Use provided colors or fall back to variant defaults
        if not bg_color:
            bg_color = theme_obj.get_variant_color(self.variant)
        if not text_color:
            if self.variant in ["primary", "success", "danger", "info", "dark"]:
                text_color = theme_obj.text_white
            elif self.variant == "ghost":
                text_color = theme_obj.primary
            else:
                text_color = theme_obj.text_primary

        if not hover_color:
            hover_color = theme_obj.get_variant_hover_color(self.variant)

        # Border logic for outline
        border = (
            f"2px solid {theme_obj.primary}" if self.variant == "outline" else "none"
        )

        style = f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: {border};
                border-radius: {theme_obj.radius_md}px;
                padding: 8px 16px;
                font-size: {theme_obj.font_md};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                padding: 9px 15px 7px 17px;
            }}
            QPushButton:disabled {{
                background-color: {theme_obj.bg_secondary};
                color: {theme_obj.text_muted};
            }}
        """
        self.setStyleSheet(style)

    def set_variant(self, variant):
        """Change button variant dynamically"""
        self.variant = variant
        # Update object name if needed
        variant_names = {
            "primary": "processButton",
            "success": "addButton",
            "danger": "deleteButton",
            "info": "importButton",
        }
        if variant in variant_names:
            self.setObjectName(variant_names[variant])
        self.style().unpolish(self)
        self.style().polish(self)


class IconButton(Button):
    """
    Button with icon support

    Usage:
        btn = IconButton(icon_path="path/to/icon.png", text="Save")
        btn = IconButton(icon=QIcon(...), text="Save")
    """

    def __init__(
        self,
        text="",
        icon=None,
        icon_path=None,
        variant="secondary",
        text_tooltip=None,
        square_size=None,
        parent=None,
    ):
        super().__init__(text=text, variant=variant, parent=parent)

        if icon:
            self.setIcon(icon)
        elif icon_path:
            from PySide6.QtGui import QIcon

            self.setIcon(QIcon(icon_path))

        if square_size:

            self.setFixedSize(square_size, square_size)
            # 2px padding each side = 4px total reduction
            self.setIconSize(QSize(square_size - 4, square_size - 4))
            # Override default button padding to allow icon to fill space
            self.setStyleSheet(self.styleSheet() + "QPushButton { padding: 0px; }")

        if text_tooltip:
            # Overriding the global QToolTip style for this specific button
            tooltip_style = (
                "QToolTip { "
                "background-color: transparent; "
                "color: transparent; "
                "border: 1px solid #D4C489; "
                "padding: 0px; "
                "}"
            )
            self.setStyleSheet(self.styleSheet() + tooltip_style)

            # 2px margin as requested by user
            self.setToolTip(
                f"<html><div style='width: 25em; text-align: left; white-space: pre-wrap; margin: 2px;'>"
                f"{text_tooltip}</div></html>"
            )

        # Re-apply variant styling to ensure it's used
        self._apply_custom_colors()


class ButtonGroup(QWidget):
    """
    Group of buttons arranged horizontally or vertically

    Usage:
        group = ButtonGroup(orientation="horizontal")
        group.add_button("Option 1")
        group.add_button("Option 2")
        group.button_clicked.connect(on_button_click)
    """

    button_clicked = Signal(int, str)  # index, text

    def __init__(self, orientation="horizontal", parent=None):
        super().__init__(parent)

        self.buttons = []
        self.orientation = orientation

        if orientation == "horizontal":
            self.layout = QHBoxLayout(self)
        else:
            self.layout = QVBoxLayout(self)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def add_button(self, text, variant="secondary", checkable=False):
        """Add a button to the group"""
        btn = QPushButton(text)
        btn.setCheckable(checkable)

        # Apply variant
        if variant == "primary":
            btn.setObjectName("processButton")
        elif variant == "danger":
            btn.setObjectName("deleteButton")

        index = len(self.buttons)
        btn.clicked.connect(lambda: self.button_clicked.emit(index, text))

        self.buttons.append(btn)
        self.layout.addWidget(btn)

        return btn

    def get_button(self, index):
        """Get button by index"""
        if 0 <= index < len(self.buttons):
            return self.buttons[index]
        return None

    def set_active(self, index):
        """Set active button (for checkable buttons)"""
        for i, btn in enumerate(self.buttons):
            if btn.isCheckable():
                btn.setChecked(i == index)


class ToggleButton(QPushButton):
    """
    Toggle button with on/off states

    Usage:
        toggle = ToggleButton("Enable Feature")
        toggle.toggled.connect(on_toggle)
    """

    def __init__(self, text="", checked=False, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setChecked(checked)

        # Update text based on state
        self.toggled.connect(self._update_appearance)
        self._update_appearance(checked)

    def _update_appearance(self, checked):
        """Update button appearance based on state"""
        # You can customize this behavior
        pass
