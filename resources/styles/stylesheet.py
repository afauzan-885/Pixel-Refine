# stylesheet.py

# Initialize global style constants placeholders. They will be populated by update_stylesheet_constants.
SLIDER_STYLE = ""
SLIDER_VALUE_LABEL = ""
VALUE_EDIT_LABEL = ""
TOGGLE_BUTTON = ""
APPLY_BUTTON = ""
SCROLL_AREA = ""
CHECKBOX_SWITCH_STYLE = ""
DROPDOWN_BOX = ""
BLANK_CONTENT_BACKGROUND = ""
BLANK_CONTENT_LABEL = ""
PROGRESS_BAR = ""
SWITCH_BUTTON = ""
PROCESS_BUTTON = ""
SAVE_AS_BUTTON = ""
DELETE_BUTTON = ""
IMPORT_BUTTON = ""
LIST_IMAGE_DATA_SINGLE_MODE = ""
LIST_IMAGE_DATA_SPECIFIC_ITEM = ""
SWITCH_BUTTON_DEFAULT_STYLE = ""
SWITCH_BUTTON_ACTIVE_STYLE = ""
PLACEHOLDER_LABEL_STYLE = ""
PREVIEW_VIEW_STYLE = ""
PANEL_BACKGROUND_STYLE = ""
LABEL_BOLD_STYLE = ""
TRANSPARENT_BACKGROUND_STYLE = ""
SIDEBAR_STYLE = ""
SIDEBAR_TOGGLE_BUTTON_STYLE = ""
SIDEBAR_NAV_BUTTON_STYLE = ""


def update_stylesheet_constants(theme=None):
    if theme is None:
        from resources.GenericUILibrary.theme import get_theme
        theme = get_theme()

    global SLIDER_STYLE, SLIDER_VALUE_LABEL, VALUE_EDIT_LABEL, TOGGLE_BUTTON
    global APPLY_BUTTON, SCROLL_AREA, CHECKBOX_SWITCH_STYLE, DROPDOWN_BOX
    global BLANK_CONTENT_BACKGROUND, BLANK_CONTENT_LABEL, PROGRESS_BAR
    global SWITCH_BUTTON, PROCESS_BUTTON, SAVE_AS_BUTTON, DELETE_BUTTON, IMPORT_BUTTON
    global LIST_IMAGE_DATA_SINGLE_MODE, LIST_IMAGE_DATA_SPECIFIC_ITEM
    global SWITCH_BUTTON_DEFAULT_STYLE, SWITCH_BUTTON_ACTIVE_STYLE
    global PLACEHOLDER_LABEL_STYLE, PREVIEW_VIEW_STYLE, PANEL_BACKGROUND_STYLE
    global LABEL_BOLD_STYLE, TRANSPARENT_BACKGROUND_STYLE
    global SIDEBAR_STYLE, SIDEBAR_TOGGLE_BUTTON_STYLE, SIDEBAR_NAV_BUTTON_STYLE

    SLIDER_STYLE = f"""
        QSlider::groove:horizontal {{
            border: {theme.slider_groove_border};
            background: {theme.slider_groove_bg};
            height: 6px;
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: {theme.slider_handle_bg};
            border: {theme.slider_handle_border};
            width: 14px;
            height: 14px;
            margin: -4px 0;
            border-radius: 7px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {theme.slider_handle_hover_bg};
        }}
    """

    SLIDER_VALUE_LABEL = f"""
        QLabel {{
            background-color: {theme.value_label_bg};
            border: {theme.value_label_border};
            border-radius: 4px;
            padding: 3px 8px;
            font-weight: bold;
            font-size: 11px;
            color: {theme.value_label_text};
            min-width: 40px;
            text-align: center;
        }}
    """

    VALUE_EDIT_LABEL = f"""
        QLineEdit {{
            background-color: {theme.value_label_bg};
            border: {theme.value_label_border};
            border-radius: 4px;
            padding: 3px 8px;
            font-weight: bold;
            font-size: 11px;
            color: {theme.value_label_text};
            min-width: 40px;
            text-align: center;
        }}
        QLineEdit:focus {{
            border: {theme.value_label_focus_border};
            background-color: {theme.value_label_focus_bg};
        }}
    """

    TOGGLE_BUTTON = f"""
        QToolButton {{
            background-color: {theme.toggle_btn_unchecked_bg};
            color: {theme.toggle_btn_unchecked_text};
            border-radius: 5px;
            padding: 6px 6px;
            font-size: 12px;
        }}
        QToolButton:checked {{
            background-color: {theme.toggle_btn_checked_bg};
            color: {theme.toggle_btn_checked_text};
        }}
        QToolButton:hover:!checked {{
            background-color: {theme.toggle_btn_hover_unchecked_bg};
        }}
        QToolButton:hover:checked {{
            background-color: {theme.toggle_btn_hover_checked_bg}; 
        }}
    """

    APPLY_BUTTON = f"""
        QPushButton {{
            background-color: {theme.btn_success_bg};
            color: {theme.btn_success_text};
            border: {theme.btn_success_border};
            border-radius: 5px;
            padding: 4px 10px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{ background-color: {theme.get_variant_hover_color("success")}; }}
        QPushButton:pressed {{ background-color: {theme.get_variant_hover_color("success")}; }}
    """

    SCROLL_AREA = f"""
        QScrollArea {{ border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 10px; }}
        QScrollBar::handle:vertical {{ background-color: {theme.border_dark}; min-height: 20px; border-radius: 5px; }}
        QScrollBar::handle:vertical:hover {{ background-color: {theme.text_secondary}; }}
        QScrollBar:horizontal {{ background: transparent; height: 10px; }}
        QScrollBar::handle:horizontal {{ background-color: {theme.border_dark}; min-width: 20px; border-radius: 5px; }}
        QScrollBar::handle:horizontal:hover {{ background-color: {theme.text_secondary}; }}
    """

    CHECKBOX_SWITCH_STYLE = f"""
        QCheckBox {{
            spacing: 8px;
            color: {theme.text_checkbox};
        }}
        QCheckBox::indicator {{
            width: 12px;
            height: 12px;
            border-radius: 6px;
            border: 1px solid {theme.border_color};
            background: {theme.bg_primary};
        }}
        QCheckBox::indicator:checked {{
            background-color: {theme.primary};
            border-color: {theme.primary};
        }}
        QCheckBox::indicator:unchecked:hover {{
            border-color: {theme.focus_color};
        }}
        QCheckBox::indicator:checked:hover {{
            background-color: {theme.get_variant_hover_color("primary")};
            border-color: {theme.get_variant_hover_color("primary")};
        }}
    """

    DROPDOWN_BOX = f"""
        QComboBox {{
            background-color: {theme.bg_primary};
            color: {theme.text_primary};
            border: 1px solid {theme.border_color};
            padding: 5px;
            border-radius: 5px;
            max-width: 200px;
        }}
        QComboBox::drop-down {{
            background-color: {theme.bg_secondary};
            border-radius: 5px;
            border: 1px solid {theme.border_color};
        }}
        QComboBox::down-arrow {{
            image: url('resources/assets/icons/menu-options.png');
            width: 24px;
            height: 24px;
        }}
        QComboBox:hover {{
            border-color: {theme.focus_color};
        }}
        QComboBox QAbstractItemView {{
            background-color: {theme.bg_primary};
            color: {theme.text_primary};
            border: 1px solid {theme.border_color};
            selection-background-color: {theme.primary};
            selection-color: {theme.text_white};
            padding: 5px;
        }}
    """

    BLANK_CONTENT_BACKGROUND = f"""
        QWidget {{
            background-color: {theme.bg_secondary};
            border: none; 
            padding: 0; 
        }}
    """

    BLANK_CONTENT_LABEL = f"""
        color: {theme.text_muted};
        font-size: 22px;
        font-family: Arial, Helvetica, sans-serif;
        background: transparent; 
        margin-top: -200px;
    """

    PROGRESS_BAR = f"""
        QProgressBar {{
            border: {theme.progress_bar_border};
            border-radius: 5px;
            background-color: {theme.progress_bar_bg};
            text-align: center;
            color: {theme.progress_text_color};
        }}
        QProgressBar::chunk {{
            background-color: {theme.progress_chunk_bg};
            width: 20px;
        }}
    """

    SWITCH_BUTTON = f"""
        QPushButton {{
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
            background-color: {theme.switch_btn_unchecked_bg};
            color: {theme.switch_btn_unchecked_text};
            border: none;
        }}
        QPushButton:first-child {{
            border-top-left-radius: 10px;
            border-bottom-left-radius: 10px;
        }}
        QPushButton:last-child {{
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
        }}
        QPushButton:checked {{
            background-color: {theme.switch_btn_checked_bg}; 
            color: {theme.switch_btn_checked_text};
        }}
    """

    PROCESS_BUTTON = f"""
        QPushButton {{
            background-color: {theme.btn_success_bg};
            color: {theme.btn_success_text};
            font-weight: bold;
            border-radius: 10px;
            font-size: 14px;
            padding: 4px 8px;
            border: {theme.btn_success_border};
        }}
        QPushButton:hover {{
            background-color: {theme.get_variant_hover_color("success")};
        }}
        QPushButton:pressed {{
            background-color: {theme.get_variant_hover_color("success")};
        }}
    """

    SAVE_AS_BUTTON = f"""
        QPushButton {{
            background-color: {theme.get_variant_color("secondary")};
            color: {theme.text_primary};
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
            padding: 4px 8px;
            border: 1px solid {theme.border_color};
        }}
        QPushButton:hover {{
            background-color: {theme.get_variant_hover_color("secondary")};
        }}
    """

    DELETE_BUTTON = f"""
        QPushButton {{
            padding: 8px 16px;
            font-size: 14px;
            background-color: {theme.btn_danger_bg};
            color: {theme.btn_danger_text};
            border: {theme.btn_danger_border};
            border-radius: 5px;
        }}
        QPushButton:hover {{
            background-color: {theme.get_variant_hover_color("danger")};
        }}
    """

    IMPORT_BUTTON = f"""
        QPushButton {{
            padding: 8px 16px;
            font-size: 14px;
            background-color: {theme.btn_primary_bg};
            color: {theme.btn_primary_text};
            border: {theme.btn_primary_border};
            border-radius: 5px;
        }}
        QPushButton:hover {{
            background-color: {theme.get_variant_hover_color("primary")};
        }}
    """

    LIST_IMAGE_DATA_SINGLE_MODE = f"""
        RightPanel {{
            background-color: transparent;
            border: none;
        }}
        RightPanel[acceptingDrop="false"] {{
             border: none;
        }}
        RightPanel[acceptingDrop="true"] {{
             border: {theme.drop_active_border};
        }}
        QListWidget#ImageList {{
            background-color: {theme.bg_primary};
            border: 1px solid {theme.border_color};
            font-size: 14px; padding: 4px; outline: none;
            color: {theme.text_primary};
        }}
        RightPanel[acceptingDrop="true"] QListWidget#ImageList {{
            background-color: {theme.drop_active_bg};
        }}
        QWidget#PlaceholderWidget {{
            background-color: {theme.bg_primary};
            border: 1px dashed {theme.border_color};
            border-radius: 3px;
        }}
        RightPanel[acceptingDrop="true"] QWidget#PlaceholderWidget {{
             background-color: {theme.drop_active_bg};
        }}
        QListWidget#ImageList::item {{
            padding: 2px 3px; color: {theme.text_primary};
        }}
        QListWidget#ImageList::item:hover {{
            background-color: {theme.list_item_hover_bg};
        }}
        QListWidget#ImageList::item:selected {{
            background-color: {theme.list_item_selected_bg};
            color: {theme.list_item_selected_text};
        }}
    """

    LIST_IMAGE_DATA_SPECIFIC_ITEM = f"""
        QListWidget#ImageList::item {{
            border: 1px solid {theme.border_color};
            border-radius: 4px;       
            padding: 2px 4px;         
            margin: 2px 4px 2px 0px;  
            background-color: transparent;
            color: {theme.text_primary};
        }}
        QListWidget#ImageList::item:hover {{
            background-color: {theme.list_item_hover_bg};             
            border-color: {theme.border_dark};
        }}
        QListWidget#ImageList::item:selected {{
            background-color: {theme.list_item_selected_bg};
            color: {theme.list_item_selected_text};
            border-color: {theme.primary};
        }}
    """

    SWITCH_BUTTON_DEFAULT_STYLE = f"""
        QPushButton {{
            background-color: {theme.switch_btn_unchecked_bg};
            color: {theme.switch_btn_unchecked_text};
            border-radius: 5px;
            padding: 2px 5px;
            min-height: 10px; 
            min-width: 40px; 
        }}
        QPushButton:hover {{
            background-color: {theme.switch_btn_hover_unchecked_bg};
        }}
    """

    SWITCH_BUTTON_ACTIVE_STYLE = f"""
        QPushButton {{
            background-color: {theme.switch_btn_checked_bg}; 
            color: {theme.switch_btn_checked_text};
            border: {theme.btn_success_border};
            border-radius: 5px;
            padding: 2px 5px;  
            min-height: 20px;  
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {theme.get_variant_hover_color("success")};
        }}
    """

    PLACEHOLDER_LABEL_STYLE = f"""
        QLabel {{
            color: {theme.text_muted}; 
            font-size: 21px; 
            border: none;
            background-color: transparent; 
            padding: 20px;
        }}
    """

    PREVIEW_VIEW_STYLE = f"""
        background-color: {theme.bg_secondary}; 
        margin-left: 5px; 
        border: none;
    """

    PANEL_BACKGROUND_STYLE = f"""
        QWidget {{ 
            background-color: {theme.bg_card}; 
        }}
    """

    LABEL_BOLD_STYLE = f"""
        font-weight: bold; 
        margin-bottom: 0px;
        color: {theme.text_primary};
    """

    TRANSPARENT_BACKGROUND_STYLE = f"""
        background-color: transparent;
    """

    SIDEBAR_STYLE = f"""
        QWidget {{
            background-color: {theme.sidebar_bg};
            color: {theme.sidebar_text};
        }}
    """

    SIDEBAR_TOGGLE_BUTTON_STYLE = f"""
        QPushButton {{
            background-color: {theme.sidebar_toggle_bg};
            border: none;
            color: {theme.sidebar_text};
            font-size: 18px;
            padding: 5px;
        }}
        QPushButton:hover {{
            background-color: {theme.sidebar_toggle_hover_bg};
        }}
    """

    SIDEBAR_NAV_BUTTON_STYLE = f"""
        QPushButton {{
            qproperty-iconSize: 28px;
            padding: 12px;
            border: none;
            background-color: {theme.sidebar_nav_bg};
        }}
        QPushButton:hover {{
            background-color: {theme.sidebar_nav_hover_bg};
        }}
        QPushButton:checked {{
            background-color: {theme.sidebar_nav_checked_bg};
        }}
    """


# Call once initially to bind default theme
update_stylesheet_constants()


def stylesheet_global_page(theme=None):
    """Mengembalikan QSS untuk styling aplikasi berdasarkan tema aktif"""
    if theme is None:
        from resources.GenericUILibrary.theme import get_theme
        theme = get_theme()

    return f"""
            /* === Latar Belakang dan Font Dasar === */
            QMainWindow, QWidget {{
                background-color: {theme.bg_secondary};
                color: {theme.text_primary};
            }}
            * {{
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 10pt;
                border: none;
            }}
            QCheckBox, ClickableLabel {{
                color: {theme.text_checkbox};
            }}
            #BatchTitleLabel {{
                color: {theme.text_header};
                font-weight: bold;
            }}
            #DisplayHeaderTitle {{
                color: {theme.text_header};
                font-weight: bold;
                padding: 5px 10px;
            }}
            #SidebarToggleBtn {{
                background-color: {theme.bg_secondary};
                color: {theme.text_secondary};
                border: 1px solid {theme.border_color};
                border-radius: 5px;
                padding: 6px 8px;
                font-size: 14px;
            }}
            #SidebarToggleBtn:hover {{
                background-color: {theme.border_dark};
            }}
            #ImportImageBtn {{
                background-color: transparent;
                color: {theme.text_secondary};
                border: 1px solid {theme.border_dark};
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 10pt;
            }}
            #ImportImageBtn:hover {{
                background-color: {theme.bg_secondary};
                border-color: {theme.text_secondary};
            }}
            
            /* === Judul dan Kontainer Utama === */
            #sectionTitle {{
                font-size: 14pt;
                font-weight: bold;
                color: {theme.text_primary};
                margin-bottom: 5px;
            }}
            #displayContainer, #projectPanel, QTabWidget::pane, #SettingsViewDialog {{
                background-color: {theme.bg_card};
                border: 1px solid {theme.border_color};
                border-radius: 8px;
            }}
            #DisplayContainerBase {{
                background-color: {theme.bg_card};
                border: 1px solid {theme.border_color};
                border-radius: 6px;
            }}
            #CombinedPanel {{
                background-color: {theme.bg_card};
                border: 1px solid {theme.border_color};
                border-radius: 8px;
                padding: 5px;
            }}
            #BulkMainPanel {{
                background-color: {theme.bg_secondary};
            }}
            #BulkAlgorithmPanel {{
                background-color: {theme.bg_primary};
                border: 1px solid {theme.border_color};
                border-radius: 6px;
            }}
            #BulkListPanel {{
                background-color: {theme.bg_primary};
                border: 1px solid {theme.border_color};
                border-radius: 6px;
            }}
            #BulkBatchInfoLabel {{
                background-color: {theme.primary};
                color: {theme.text_white};
                padding: 3px 5px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }}
            QTabWidget::pane {{
                border-top-left-radius: 0;
            }}
            #scrollArea {{
                background-color: transparent;
            }}
            #imageThumbnail {{
                border: 1px solid {theme.border_color};
                background-color: Transparent;
                border-radius: 4px;
                font-size: 14pt;
                font-weight: bold;
                color: {theme.text_muted};
            }}
            
            #thumbnailWidget {{
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                background-color: {theme.bg_secondary};
            }}
            
            /* === Panel Proyek (Kanan) === */
            #projectPanel {{
                padding: 5px;
            }}
            QListWidget {{
                border: 1px solid {theme.border_color};
                border-radius: 5px;
                outline: 0;
                background-color: {theme.bg_primary};
                color: {theme.text_primary};
            }}
            QListWidget::item {{
                padding: 8px;
                color: {theme.text_primary};
            }}
            QListWidget::item:selected {{
                background-color: {theme.primary}2D; /* Semi-transparent accent */
                color: {theme.primary};
                border-radius: 4px;
                border: 1px solid {theme.primary};
            }}
            QListWidget:!focus QListWidget::item:selected {{
                background-color: {theme.border_dark};
                color: {theme.text_primary};
                border-color: {theme.border_color};
            }}
            
            /* === Tombol-tombol === */
            .QPushButton {{
                padding: 4px 6px;
                border: 1px solid {theme.border_color};
                border-radius: 5px;
                background-color: {theme.bg_primary};
                color: {theme.text_primary};
            }}
            .QPushButton:hover {{
                background-color: {theme.bg_secondary};
                border-color: {theme.border_dark};
            }}
            .QPushButton#addButton, .QPushButton#processButton, .QPushButton#ApplySettingsBtn {{
                background-color: {theme.btn_success_bg};
                color: {theme.btn_success_text};
                font-weight: bold;
                border: {theme.btn_success_border};
            }}
            .QPushButton#addButton:hover, .QPushButton#processButton:hover, .QPushButton#ApplySettingsBtn:hover {{
                background-color: {theme.get_variant_hover_color("success")};
            }}
            .QPushButton#deleteButton, .QPushButton#DeleteBatchBtn {{
                background-color: {theme.btn_danger_bg};
                color: {theme.btn_danger_text};
                font-weight: bold;
                border: {theme.btn_danger_border};
            }}
            .QPushButton#deleteButton:hover, .QPushButton#DeleteBatchBtn:hover {{
                background-color: {theme.get_variant_hover_color("danger")};
            }}
            .QPushButton#importButton, .QPushButton#NewBatchBtn {{
                background-color: {theme.btn_primary_bg};
                color: {theme.btn_primary_text};
                font-weight: bold;
                border: {theme.btn_primary_border};
            }}
            .QPushButton#importButton:hover, .QPushButton#NewBatchBtn:hover {{
                background-color: {theme.get_variant_hover_color("primary")};
            }}
            
            /* === Panel Tab Workflow === */
            QTabBar::tab {{
                background: transparent;
                border-bottom: 3px solid transparent; 
                padding: 6px 10px;
                margin-right: 5px;
                color: {theme.text_secondary};
            }}
            QTabBar::tab:selected {{
                font-weight: bold;
                color: {theme.focus_color};
                border-bottom: 3px solid {theme.focus_color};
            }}
            QTabBar::tab:!selected:hover {{
                color: {theme.text_primary};
            }}
            QMenu {{
                background-color: {theme.bg_primary};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                padding: 5px;
                border-radius: 4px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                background-color: transparent;
                border-radius: 3px;
                color: {theme.text_primary};
            }}
            QMenu::item:disabled {{
                color: {theme.text_muted};
            }}
            QMenu::item:selected {{
                background-color: {theme.primary}; 
                color: {theme.text_white};
            }}
            QMenu::separator {{
                height: 1px;
                background: {theme.border_color};
                margin: 4px 0px;
            }}
            
            /* === Widget di dalam Tab (Dropdown, Slider) === */
            QComboBox {{
                padding: 6px 5px;
                border: none; 
                background-color: {theme.bg_primary};
                color: {theme.text_primary};
                border-bottom: 4px solid {theme.border_color}; 
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}

            QComboBox:hover {{
                border-bottom-color: {theme.focus_color}; 
            }}

            QComboBox::drop-down {{
                border: none;
            }}
            QSlider::groove:horizontal {{
                border: {theme.slider_groove_border};
                background: {theme.slider_groove_bg};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {theme.slider_handle_bg};
                border: {theme.slider_handle_border};
                width: 16px;
                margin: -6px 0; 
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {theme.slider_handle_hover_bg};
            }}

            /* === Desain Scrollbar Modern === */
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

            /* === Custom Widgets & Containers === */
            #paramAlignWidget, #paramAlgoWidget {{
                background-color: {theme.bg_card};
            }}
            #progressContainer {{
                background-color: {theme.bg_secondary};
            }}

            /* === ConfigPanel === */
            #workflowContainer {{
                background-color: {theme.bg_card};
                border: 1px solid {theme.border_color};
                border-radius: 8px;
            }}

            /* === modal_confirm Dialog === */
            #ConfirmContainer {{
                background-color: {theme.bg_card};
                border: 1px solid {theme.border_color};
                border-radius: 6px;
            }}
            #TitleBar {{
                background-color: {theme.bg_primary};
                border-bottom: 1px solid {theme.border_color};
            }}

            /* === Global Tooltip === */
            QToolTip {{
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #DDE5EC;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 10pt;
            }}
        """


PLACEHOLDER_LABEL_STYLE = """
    QLabel {
        color: #777777; 
        font-size: 21px; 
        border: none;
        background-color: transparent; 
        padding: 20px;
    }
"""

PREVIEW_VIEW_STYLE = """
    background-color: #f0f0f0; 
    margin-left: 5px; 
    border: none;
"""

PANEL_BACKGROUND_STYLE = """
    QWidget { 
        background-color: white; 
    }
"""

LABEL_BOLD_STYLE = """
    font-weight: bold; 
    margin-bottom: 0px;
"""

TRANSPARENT_BACKGROUND_STYLE = """
    background-color: transparent;
"""

# NOTE: SIDEBAR_STYLE, SIDEBAR_TOGGLE_BUTTON_STYLE, SIDEBAR_NAV_BUTTON_STYLE
# are set by update_stylesheet_constants() using theme-aware values.
# Do NOT reassign them here with hardcoded colors.
