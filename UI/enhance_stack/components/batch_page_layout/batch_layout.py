from PySide6.QtWidgets import (QWidget,  QScrollArea)

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