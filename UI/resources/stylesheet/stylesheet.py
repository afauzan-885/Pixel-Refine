
# stylesheet.py
SLIDER_STYLE = """
    QSlider::groove:horizontal {
        border: 1px solid #bbb;
        background: #ddd;
        height: 6px;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #50A2D5;
        border: 1px solid #3B89C2;
        width: 14px;
        height: 14px;
        margin: -4px 0;
        border-radius: 7px;
    }
    QSlider::handle:horizontal:hover {
        background: #428BB8;
    }
"""

SLIDER_VALUE_LABEL = """
    QLabel {
        background-color: #E0E0E0;
        border-radius: 4px;
        padding: 3px 8px;
        font-weight: bold;
        font-size: 11px;
        color: #333;
        min-width: 40px;
        text-align: center;
    }
"""

KEEP_EDGES_BUTTON = """
    QToolButton {
        background-color: #50A2D5;
        color: white;
        border-radius: 5px;
        padding: 6px 6px;
    }
    QToolButton:checked {
        background-color: #428BB8;
    }
    QToolButton:hover {
        background-color: #598DAE;
    }
"""

APPLY_BUTTON = """
    QPushButton {
        background-color: #5cb85c;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #4cae4c; }
    QPushButton:pressed { background-color: #449d44; }
"""

SCROLL_AREA = """
    QScrollArea { border: none; }
    QScrollBar:vertical { background: #F0F0F0; width: 10px; border-radius: 5px; }
    QScrollBar::handle:vertical { background: #A0A0A0; min-height: 20px; border-radius: 5px; }
    QScrollBar::handle:vertical:hover { background: #808080; }
"""

DROPDOWN_BOX = """
            QComboBox {
                background-color: #F0EEEE;
                padding: 5px;
                border-radius: 5px;
                max-width: 200px;
            }
            QComboBox::drop-down {
                background-color: #ffffff;
                border-radius: 5px;
                border: 1px solid #d1d1d1;
            }
            QComboBox::down-arrow {
                image: url('UI/resources/icon/menu-options.png');
                width: 24px;
                height: 24px;
            }
            QComboBox:hover {
                background-color: #9EFFE2;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #d1d1d1;
                selection-background-color: #7B9AC8;
                selection-color: white;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item {
                margin-bottom: 5px;
            }
        """
