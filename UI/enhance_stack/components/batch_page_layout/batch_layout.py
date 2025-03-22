import os
from PyQt6.QtWidgets import (QLabel, QSpacerItem, QSizePolicy, QWidget, QVBoxLayout, QScrollArea,
                             QHBoxLayout, QPushButton, QComboBox, QCheckBox, QLineEdit)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
import weakref

from UI.enhance_stack.components.batch_page_layout.thumbnail import ThumbnailLoader, create_thumbnail_placeholder, update_thumbnail
from config import CACHE
from UI.settings.General.Language import language_config

def setup_main_panel(parent, scroll_area_style):
    """Membuat panel utama dengan layout vertikal agar UI tersusun dari atas."""
    main_panel = QWidget(parent)
    main_panel.setStyleSheet("background-color: white;")
    
    main_panel_layout = QVBoxLayout(main_panel)
    main_panel_layout.setContentsMargins(10, 10, 10, 10)
    main_panel_layout.setSpacing(30)  
    
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(main_panel)
    scroll_area.setStyleSheet(scroll_area_style)

    return scroll_area, main_panel_layout

def refresh_ui(database_manager, main_panel_layout, setup_combined_panel):
    """Memperbarui UI dengan daftar batch yang tersedia."""
    # Bersihkan layout yang ada
    while main_panel_layout.count():
        item = main_panel_layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    batch_ids = database_manager.get_all_batch_ids()

    if not batch_ids:
        placeholder = QLabel("Tidak ada batch yang tersedia.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_panel_layout.addWidget(placeholder)
    else:
        for batch_id in batch_ids:
            combined_panel = setup_combined_panel(batch_id=batch_id)
            main_panel_layout.addWidget(combined_panel)

    spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
    main_panel_layout.addSpacerItem(spacer)