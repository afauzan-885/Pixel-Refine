"""
Theme and Color System for GenericUILibrary
Provides default colors and styling that can be customized
"""


class Theme:
    """
    Default theme colors (Bootstrap-inspired)
    Can be customized by creating a new Theme instance
    """

    def __init__(self):
        # Primary colors
        self.primary = "#2ECC71"  # Green
        self.secondary = "#95A5A6"  # Gray
        self.success = "#2ECC71"  # Green
        self.danger = "#E74C3C"  # Red
        self.warning = "#F39C12"  # Orange
        self.info = "#3498DB"  # Blue
        self.light = "#ECF0F1"  # Light gray
        self.dark = "#2C3E50"  # Dark blue-gray

        # Background colors
        self.bg_primary = "#FFFFFF"  # White
        self.bg_secondary = "#F5F8FA"  # Light gray
        self.bg_dark = "#2C3E50"  # Dark

        # Text colors
        self.text_primary = "#333333"
        self.text_secondary = "#666666"
        self.text_muted = "#999999"
        self.text_white = "#FFFFFF"

        # Border colors
        self.border_color = "#E8EDF2"
        self.border_dark = "#DCDCDC"

        # Interactive states
        self.hover_overlay = "rgba(0, 0, 0, 0.05)"
        self.active_overlay = "rgba(0, 0, 0, 0.1)"
        self.focus_color = "#0078D4"

        # Shadows
        self.shadow_sm = "0 1px 2px rgba(0, 0, 0, 0.05)"
        self.shadow_md = "0 2px 4px rgba(0, 0, 0, 0.1)"
        self.shadow_lg = "0 4px 8px rgba(0, 0, 0, 0.15)"

        # Spacing
        self.spacing_xs = 5
        self.spacing_sm = 10
        self.spacing_md = 15
        self.spacing_lg = 20
        self.spacing_xl = 30

        # Border radius
        self.radius_sm = 4
        self.radius_md = 5
        self.radius_lg = 8
        self.radius_xl = 10

        # Font sizes
        self.font_xs = "9pt"
        self.font_sm = "10pt"
        self.font_md = "11pt"
        self.font_lg = "14pt"
        self.font_xl = "18pt"

    def get_variant_color(self, variant):
        """Get color for a variant"""
        variant_map = {
            "primary": self.primary,
            "secondary": self.secondary,
            "success": self.success,
            "danger": self.danger,
            "warning": self.warning,
            "info": self.info,
            "light": self.light,
            "dark": self.dark,
        }
        return variant_map.get(variant, self.secondary)

    def get_variant_hover_color(self, variant):
        """Get hover color for a variant (slightly darker)"""
        # Simplified: just return a darker version
        color_map = {
            "primary": "#28B463",
            "secondary": "#7F8C8D",
            "success": "#28B463",
            "danger": "#C0392B",
            "warning": "#E67E22",
            "info": "#2980B9",
            "light": "#D5DBDB",
            "dark": "#1C2833",
        }
        return color_map.get(variant, "#7F8C8D")


# Global default theme
_default_theme = Theme()


def get_theme():
    """Get the current default theme"""
    return _default_theme


def set_theme(theme):
    """Set a custom theme globally"""
    global _default_theme
    _default_theme = theme


def create_button_style(variant="secondary", theme=None):
    """
    Create button stylesheet for a given variant

    Usage:
        btn.setStyleSheet(create_button_style("primary"))
    """
    if theme is None:
        theme = get_theme()

    bg_color = theme.get_variant_color(variant)
    hover_color = theme.get_variant_hover_color(variant)

    # Determine text color based on variant
    if variant in ["primary", "success", "danger", "info", "dark"]:
        text_color = theme.text_white
    else:
        text_color = theme.text_primary

    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: none;
            border-radius: {theme.radius_md}px;
            padding: 8px 16px;
            font-size: {theme.font_md};
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
            background-color: {theme.bg_secondary};
            color: {theme.text_muted};
        }}
    """


def create_card_style(theme=None):
    """Create card stylesheet"""
    if theme is None:
        theme = get_theme()

    return f"""
        QFrame {{
            background-color: {theme.bg_primary};
            border: 1px solid {theme.border_color};
            border-radius: {theme.radius_lg}px;
        }}
    """


def create_input_style(theme=None):
    """Create input field stylesheet"""
    if theme is None:
        theme = get_theme()

    return f"""
        QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {theme.bg_primary};
            border: 1px solid {theme.border_color};
            border-radius: {theme.radius_sm}px;
            padding: 6px 10px;
            font-size: {theme.font_md};
            color: {theme.text_primary};
        }}
        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {theme.focus_color};
            border-width: 2px;
        }}
        QLineEdit:disabled, QTextEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
            background-color: {theme.bg_secondary};
            color: {theme.text_muted};
        }}
    """


def create_select_style(theme=None):
    """Create select/combobox stylesheet"""
    if theme is None:
        theme = get_theme()

    return f"""
        QComboBox {{
            background-color: {theme.bg_primary};
            border: 1px solid {theme.border_color};
            border-radius: {theme.radius_sm}px;
            padding: 6px 10px;
            font-size: {theme.font_md};
            color: {theme.text_primary};
        }}
        QComboBox:hover {{
            border-color: {theme.focus_color};
        }}
        QComboBox::drop-down {{
            border: none;
            padding-right: 5px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {theme.bg_primary};
            border: 1px solid {theme.border_color};
            selection-background-color: {theme.primary};
            selection-color: {theme.text_white};
        }}
    """


def create_list_style(theme=None):
    """Create list widget stylesheet"""
    if theme is None:
        theme = get_theme()

    return f"""
        QListWidget {{
            background-color: {theme.bg_primary};
            border: 1px solid {theme.border_color};
            border-radius: {theme.radius_md}px;
            outline: none;
        }}
        QListWidget::item {{
            padding: 8px;
            border-radius: {theme.radius_sm}px;
        }}
        QListWidget::item:hover {{
            background-color: {theme.bg_secondary};
        }}
        QListWidget::item:selected {{
            background-color: {theme.primary};
            color: {theme.text_white};
        }}
    """


def create_scrollbar_style(theme=None):
    """Create scrollbar stylesheet"""
    if theme is None:
        theme = get_theme()

    return f"""
        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 0px;
        }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 10px;
            margin: 0px;
        }}
        QScrollBar::handle {{
            background-color: {theme.border_dark};
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            min-height: 25px;
        }}
        QScrollBar::handle:horizontal {{
            min-width: 25px;
        }}
        QScrollBar::handle:hover {{
            background-color: {theme.text_secondary};
        }}
        QScrollBar::add-line, QScrollBar::sub-line {{
            height: 0px;
            width: 0px;
            background: none;
        }}
        QScrollBar::add-page, QScrollBar::sub-page {{
            background: none;
        }}
    """
