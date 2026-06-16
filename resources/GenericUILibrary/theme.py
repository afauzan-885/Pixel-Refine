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
        self.info = "#0DCAF0"  # Bright Blue (Bootstrap 5 Info)
        self.light = "#ECF0F1"  # Light gray
        self.dark = "#2C3E50"  # Dark blue-gray
        self.ghost = "transparent"
        self.outline = "transparent"

        # Background colors
        self.bg_primary = "#FFFFFF"  # White
        self.bg_secondary = "#F5F8FA"  # Light gray
        self.bg_dark = "#2C3E50"  # Dark
        self.bg_card = "#FFFFFF"  # Card/dialog background

        # Text colors
        self.text_primary = "#333333"
        self.text_secondary = "#666666"
        self.text_muted = "#999999"
        self.text_white = "#FFFFFF"
        self.text_checkbox = "#333333"
        self.text_header = "#333333"

        # Softer button colors (light background, dark text, colored border)
        self.btn_success_bg = "#E8F5E9"
        self.btn_success_text = "#2E7D32"
        self.btn_success_border = "1px solid #A9DFBF"
        
        self.btn_danger_bg = "#FFEBEE"
        self.btn_danger_text = "#C62828"
        self.btn_danger_border = "1px solid #F5B7B1"

        self.btn_primary_bg = "#E8F5E9"
        self.btn_primary_text = "#2E7D32"
        self.btn_primary_border = "1px solid #A9DFBF"

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

        # Slider styling
        self.slider_groove_bg = "#ddd"
        self.slider_groove_border = "1px solid #bbb"
        self.slider_handle_bg = "#50A2D5"
        self.slider_handle_border = "1px solid #3B89C2"
        self.slider_handle_hover_bg = "#428BB8"

        # Slider Value & Value Edit Label
        self.value_label_bg = "#E0E0E0"
        self.value_label_text = "#333333"
        self.value_label_border = "none"
        self.value_label_focus_bg = "#F0F8FF"
        self.value_label_focus_border = "1px solid #0078D7"

        # Toggle Button
        self.toggle_btn_checked_bg = "#4893C1"
        self.toggle_btn_checked_text = "#FFFFFF"
        self.toggle_btn_unchecked_bg = "#FF0000"
        self.toggle_btn_unchecked_text = "#FFFFFF"
        self.toggle_btn_hover_checked_bg = "#2F7AA8"
        self.toggle_btn_hover_unchecked_bg = "#FF6666"

        # Progress Bar
        self.progress_bar_bg = "#F0F0F0"
        self.progress_bar_border = "1px solid #BBB"
        self.progress_chunk_bg = "#80C4E9"
        self.progress_text_color = "#333333"

        # Switch Buttons
        self.switch_btn_checked_bg = "#2ECC71"
        self.switch_btn_checked_text = "#FFFFFF"
        self.switch_btn_unchecked_bg = "#95A5A6"
        self.switch_btn_unchecked_text = "#000000"
        self.switch_btn_hover_checked_bg = "#28B463"
        self.switch_btn_hover_unchecked_bg = "#7F8C8D"

        # Image list items & drag status
        self.list_item_hover_bg = "#C0F1E9"
        self.list_item_selected_bg = "#C5CFD8"
        self.list_item_selected_text = "#000000"
        self.drop_active_bg = "#C0F1E9"
        self.drop_active_border = "2px dashed #74B9FF"

        # Sidebar nav styling
        self.sidebar_bg = "#E0E0E0"
        self.sidebar_text = "#333333"
        self.sidebar_toggle_bg = "#C8D6E5"
        self.sidebar_toggle_hover_bg = "#B2BEC3"
        self.sidebar_nav_bg = "#E0E0E0"
        self.sidebar_nav_hover_bg = "#DFE6E9"
        self.sidebar_nav_checked_bg = "#74B9FF"

        # FeatureCard styling
        self.card_checked_bg = "#F0FDF4"
        self.card_checked_border = "#2ECC71"
        self.card_unchecked_bg = "#FFFFFF"
        self.card_unchecked_border = "#E8EDF2"
        self.card_disabled_bg = "#F8F9FA"
        self.card_disabled_border = "#E8EDF2"
        self.card_text_title = "#2C3E50"
        self.card_text_desc = "#7F8C8D"

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
            "ghost": self.ghost,
            "outline": self.outline,
        }
        return variant_map.get(variant, self.secondary)

    def get_variant_hover_color(self, variant):
        """Get hover color for a variant (slightly darker)"""
        # Simplified: just return a darker version
        color_map = {
            "primary": "#C8E6C9",
            "secondary": "#7F8C8D",
            "success": "#C8E6C9",
            "danger": "#FFCDD2",
            "warning": "#E67E22",
            "info": "#31D2F2",
            "light": "#D5DBDB",
            "dark": "#1C2833",
            "ghost": "rgba(0, 0, 0, 0.05)",
            "outline": "rgba(0, 0, 0, 0.05)",
        }
        return color_map.get(variant, "#7F8C8D")


class DarkTheme(Theme):
    """
    Sleek Premium Dark Theme
    Inherits from Theme but overrides background, border, and text colors.
    """

    def __init__(self):
        super().__init__()
        # Primary colors
        self.primary = "#2ECC71"  # Emerald Green
        self.secondary = "#78909C"  # Blue-Gray
        self.success = "#2ECC71"
        self.danger = "#E74C3C"
        self.warning = "#F39C12"
        self.info = "#0DCAF0"
        self.light = "#263238"  # Dark gray-blue for light containers in dark mode
        self.dark = "#CFD8DC"   # Light gray for dark elements in dark mode
        self.ghost = "transparent"
        self.outline = "transparent"

        # Background colors
        self.bg_primary = "#1E272C"    # Slate/Dark Gray
        self.bg_secondary = "#263238"  # Light Slate
        self.bg_dark = "#11171A"       # Deep Dark
        self.bg_card = "#1E272C"       # Dark Card

        # Text colors
        self.text_primary = "#ECEFF1"
        self.text_secondary = "#B0BEC5"
        self.text_muted = "#78909C"
        self.text_white = "#FFFFFF"
        self.text_checkbox = "#ECEFF1"
        self.text_header = "#F5F5F5"

        # Softer button colors
        self.btn_success_bg = "#1B5E20"
        self.btn_success_text = "#A3E2B8"
        self.btn_success_border = "1px solid #2E7D32"

        self.btn_danger_bg = "#B71C1C"
        self.btn_danger_text = "#FFCDD2"
        self.btn_danger_border = "1px solid #C62828"

        self.btn_primary_bg = "#1C5A35"
        self.btn_primary_text = "#A3E2B8"
        self.btn_primary_border = "1px solid #206E3F"

        # Border colors
        self.border_color = "#37474F"
        self.border_dark = "#263238"

        # Interactive states
        self.hover_overlay = "rgba(255, 255, 255, 0.08)"
        self.active_overlay = "rgba(255, 255, 255, 0.15)"
        self.focus_color = "#2BC7BD"

        # Slider styling (Dark Theme)
        self.slider_groove_bg = "#263238"
        self.slider_groove_border = "1px solid #37474F"
        self.slider_handle_bg = "#2BC7BD"
        self.slider_handle_border = "1px solid #208E88"
        self.slider_handle_hover_bg = "#208E88"

        # Slider Value & Value Edit Label (Dark Theme)
        self.value_label_bg = "#263238"
        self.value_label_text = "#ECEFF1"
        self.value_label_border = "1px solid #37474F"
        self.value_label_focus_bg = "#1E272C"
        self.value_label_focus_border = "1px solid #2BC7BD"

        # Toggle Button (Dark Theme)
        self.toggle_btn_checked_bg = "#1C5A35"
        self.toggle_btn_checked_text = "#A3E2B8"
        self.toggle_btn_unchecked_bg = "#B71C1C"
        self.toggle_btn_unchecked_text = "#FFCDD2"
        self.toggle_btn_hover_checked_bg = "#206E3F"
        self.toggle_btn_hover_unchecked_bg = "#C62828"

        # Progress Bar (Dark Theme)
        self.progress_bar_bg = "#263238"
        self.progress_bar_border = "1px solid #37474F"
        self.progress_chunk_bg = "#2BC7BD"
        self.progress_text_color = "#ECEFF1"

        # Switch Buttons (Dark Theme)
        self.switch_btn_checked_bg = "#1C5A35"
        self.switch_btn_checked_text = "#A3E2B8"
        self.switch_btn_unchecked_bg = "#263238"
        self.switch_btn_unchecked_text = "#B0BEC5"
        self.switch_btn_hover_checked_bg = "#206E3F"
        self.switch_btn_hover_unchecked_bg = "#37474F"

        # Image list items & drag status (Dark Mode)
        self.list_item_hover_bg = "#263238"
        self.list_item_selected_bg = "#37474F"
        self.list_item_selected_text = "#FFFFFF"
        self.drop_active_bg = "#263238"
        self.drop_active_border = "2px dashed #2BC7BD"

        # Sidebar nav styling (Dark Mode)
        self.sidebar_bg = "#11171A"
        self.sidebar_text = "#ECEFF1"
        self.sidebar_toggle_bg = "#1E272C"
        self.sidebar_toggle_hover_bg = "#263238"
        self.sidebar_nav_bg = "#11171A"
        self.sidebar_nav_hover_bg = "#1E272C"
        self.sidebar_nav_checked_bg = "#2BC7BD"

        # FeatureCard styling (Dark Theme)
        self.card_checked_bg = "#183D26"
        self.card_checked_border = "#2ECC71"
        self.card_unchecked_bg = "#1E272C"
        self.card_unchecked_border = "#37474F"
        self.card_disabled_bg = "#263238"
        self.card_disabled_border = "#37474F"
        self.card_text_title = "#ECEFF1"
        self.card_text_desc = "#78909C"

    def get_variant_hover_color(self, variant):
        """Get hover color for a variant in dark mode"""
        color_map = {
            "primary": "#27AE60",
            "secondary": "#90A4AE",
            "success": "#27AE60",
            "danger": "#C0392B",
            "warning": "#D35400",
            "info": "#31D2F2",
            "light": "#37474F",
            "dark": "#ECEFF1",
            "ghost": "rgba(255, 255, 255, 0.08)",
            "outline": "rgba(255, 255, 255, 0.08)",
        }
        return color_map.get(variant, "#90A4AE")


LightTheme = Theme

# Global default theme
_default_theme = Theme()


def get_theme():
    """Get the current default theme"""
    return _default_theme


def set_theme(theme):
    """Set a custom theme globally"""
    global _default_theme
    _default_theme = theme
    try:
        from resources.styles.stylesheet import update_stylesheet_constants
        update_stylesheet_constants(theme)
    except Exception as e:
        print(f"Error updating stylesheet constants: {e}")



def create_button_style(variant="secondary", theme=None):
    """
    Create button stylesheet for a given variant

    Usage:
        btn.setStyleSheet(create_button_style("primary"))
    """
    if theme is None:
        theme = get_theme()

    border_style = "border: none;"
    
    if variant == "primary":
        bg_color = theme.btn_primary_bg
        text_color = theme.btn_primary_text
        border_style = f"border: {theme.btn_primary_border};"
        hover_color = theme.get_variant_hover_color("primary")
    elif variant == "success":
        bg_color = theme.btn_success_bg
        text_color = theme.btn_success_text
        border_style = f"border: {theme.btn_success_border};"
        hover_color = theme.get_variant_hover_color("success")
    elif variant == "danger":
        bg_color = theme.btn_danger_bg
        text_color = theme.btn_danger_text
        border_style = f"border: {theme.btn_danger_border};"
        hover_color = theme.get_variant_hover_color("danger")
    else:
        bg_color = theme.get_variant_color(variant)
        hover_color = theme.get_variant_hover_color(variant)
        if variant in ["info", "dark"]:
            text_color = theme.text_white
        else:
            text_color = theme.text_primary

    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            {border_style}
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


def create_checkbox_style(theme=None):
    """Create a premium checkbox stylesheet (Smaller, Blue, Circular)"""
    if theme is None:
        theme = get_theme()

    # Blue color from user reference
    brand_blue = theme.focus_color
    border_color = theme.border_color

    return f"""
        QCheckBox {{
            spacing: 12px;
            font-size: 11pt;
            color: {theme.text_checkbox};
        }}
        QCheckBox::indicator {{
            width: 15px;
            height: 15px;
            border-radius: 8px; /* Circular */
            border: 1px solid {border_color};
            background-color: {theme.bg_primary};
        }}
        QCheckBox::indicator:hover {{
            border-color: {brand_blue};
            background-color: {theme.bg_secondary};
        }}
        QCheckBox::indicator:checked {{
            background-color: {brand_blue};
            border-color: {brand_blue};
            /* Center dot SVG */
            image: url(data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjQgMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iNSIgZmlsbD0id2hpdGUiLz48L3N2Zz4=);
        }}
        QCheckBox::indicator:checked:hover {{
            background-color: {theme.get_variant_hover_color("primary")};
            border-color: {theme.get_variant_hover_color("primary")};
        }}
        QCheckBox:focus {{
            color: {brand_blue};
        }}
        QCheckBox:disabled {{
            color: {theme.text_muted};
        }}
        QCheckBox::indicator:disabled {{
            background-color: {theme.bg_secondary};
            border-color: {border_color};
        }}
    """


# ==============================================================================
# QML Theme Bridge (Dapat di-reuse oleh proyek QML Mobile)
# ==============================================================================
try:
    from PySide6.QtCore import QObject, Property, Signal, Slot

    class QmlThemeBridge(QObject):
        """
        Bridge class to expose PySide6 Theme properties to QML Engine.

        PENTING: Setiap Property WAJIB memiliki notify=<Signal> agar QML bisa
        melakukan property binding secara reaktif. Tanpa notify, QML akan
        mengeluarkan warning: "depends on non-bindable properties".
        """

        # ── Signal perubahan tema (master) ────────────────────────────────────
        themeChanged = Signal()

        # ── Signal individual per properti ────────────────────────────────────
        primaryChanged         = Signal()
        secondaryChanged       = Signal()
        successChanged         = Signal()
        dangerChanged          = Signal()
        warningChanged         = Signal()
        infoChanged            = Signal()
        bgPrimaryChanged       = Signal()
        bgSecondaryChanged     = Signal()
        textPrimaryChanged     = Signal()
        textSecondaryChanged   = Signal()
        textMutedChanged       = Signal()
        textWhiteChanged       = Signal()
        borderColorChanged     = Signal()
        radiusSmChanged        = Signal()
        radiusMdChanged        = Signal()
        radiusLgChanged        = Signal()
        radiusXlChanged        = Signal()

        def __init__(self, parent=None):
            super().__init__(parent)
            self._theme = get_theme()

        def _emit_all(self):
            """Emit semua signal sekaligus (dipakai saat tema berganti)."""
            self.primaryChanged.emit()
            self.secondaryChanged.emit()
            self.successChanged.emit()
            self.dangerChanged.emit()
            self.warningChanged.emit()
            self.infoChanged.emit()
            self.bgPrimaryChanged.emit()
            self.bgSecondaryChanged.emit()
            self.textPrimaryChanged.emit()
            self.textSecondaryChanged.emit()
            self.textMutedChanged.emit()
            self.textWhiteChanged.emit()
            self.borderColorChanged.emit()
            self.radiusSmChanged.emit()
            self.radiusMdChanged.emit()
            self.radiusLgChanged.emit()
            self.radiusXlChanged.emit()
            self.themeChanged.emit()

        @Slot(object)
        def applyTheme(self, new_theme):
            """Ganti tema secara runtime — QML akan merefleksikan perubahan."""
            self._theme = new_theme
            self._emit_all()

        # ── Properties dengan notify signal ───────────────────────────────────

        def _get_primary(self):         return self._theme.primary
        def _get_secondary(self):       return self._theme.secondary
        def _get_success(self):         return self._theme.success
        def _get_danger(self):          return self._theme.danger
        def _get_warning(self):         return self._theme.warning
        def _get_info(self):            return self._theme.info
        def _get_bgPrimary(self):       return self._theme.bg_primary
        def _get_bgSecondary(self):     return self._theme.bg_secondary
        def _get_textPrimary(self):     return self._theme.text_primary
        def _get_textSecondary(self):   return self._theme.text_secondary
        def _get_textMuted(self):       return self._theme.text_muted
        def _get_textWhite(self):       return self._theme.text_white
        def _get_borderColor(self):     return self._theme.border_color
        def _get_radiusSm(self):        return self._theme.radius_sm
        def _get_radiusMd(self):        return self._theme.radius_md
        def _get_radiusLg(self):        return self._theme.radius_lg
        def _get_radiusXl(self):        return self._theme.radius_xl

        primary       = Property(str, _get_primary,       notify=primaryChanged)
        secondary     = Property(str, _get_secondary,     notify=secondaryChanged)
        success       = Property(str, _get_success,       notify=successChanged)
        danger        = Property(str, _get_danger,        notify=dangerChanged)
        warning       = Property(str, _get_warning,       notify=warningChanged)
        info          = Property(str, _get_info,          notify=infoChanged)
        bgPrimary     = Property(str, _get_bgPrimary,     notify=bgPrimaryChanged)
        bgSecondary   = Property(str, _get_bgSecondary,   notify=bgSecondaryChanged)
        textPrimary   = Property(str, _get_textPrimary,   notify=textPrimaryChanged)
        textSecondary = Property(str, _get_textSecondary, notify=textSecondaryChanged)
        textMuted     = Property(str, _get_textMuted,     notify=textMutedChanged)
        textWhite     = Property(str, _get_textWhite,     notify=textWhiteChanged)
        borderColor   = Property(str, _get_borderColor,   notify=borderColorChanged)
        radiusSm      = Property(int, _get_radiusSm,      notify=radiusSmChanged)
        radiusMd      = Property(int, _get_radiusMd,      notify=radiusMdChanged)
        radiusLg      = Property(int, _get_radiusLg,      notify=radiusLgChanged)
        radiusXl      = Property(int, _get_radiusXl,      notify=radiusXlChanged)

except ImportError:
    # Fallback jika dijalankan di environment non-PySide6 (misalnya unit test luar)
    pass
