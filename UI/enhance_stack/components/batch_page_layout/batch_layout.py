import os
import weakref
from PyQt6.QtWidgets import (QLabel, QSpacerItem, QSizePolicy, QWidget, QVBoxLayout, QScrollArea,
                             QHBoxLayout, QPushButton, QComboBox, QCheckBox, QLineEdit)
from PyQt6.QtCore import Qt

from UI.enhance_stack.components.batch_page_layout.combined_panel import CombinedPanel
from UI.enhance_stack.components.batch_page_layout.thumbnail import ThumbnailLoader, create_thumbnail_placeholder, update_thumbnail

def setup_main_panel(layout_instance, scroll_area_style):
    """Membuat panel utama dengan layout yang diberikan."""
    main_panel = QWidget()
    main_panel.setStyleSheet("background-color: white;")

    # Menggunakan layout yang diberikan daripada membuat baru
    layout_instance.setContentsMargins(10, 10, 10, 10)
    layout_instance.setSpacing(30)

    main_panel.setLayout(layout_instance)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(main_panel)
    scroll_area.setStyleSheet(scroll_area_style)

    return scroll_area


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
        placeholder = QLabel("No batches available.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_panel_layout.addWidget(placeholder)
    else:
        for batch_id in batch_ids:
            combined_panel = setup_combined_panel(batch_id=batch_id)
            main_panel_layout.addWidget(combined_panel)

    spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
    main_panel_layout.addSpacerItem(spacer)
    