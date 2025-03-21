
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

TOGGLE_BUTTON = """
    QToolButton {
        background-color: #FF0000; /* Merah untuk state false */
        color: white;
        border-radius: 5px;
        padding: 6px 6px;
        font-size: 12px;
    }
    QToolButton:checked {
        background-color: #4893C1; /* Biru untuk state true */
    }
    QToolButton:hover:!checked {
        background-color: #FF6666; /* Hover pada state false */
    }
    QToolButton:hover:checked {
        background-color: #2F7AA8; /* Hover pada state true */
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
    QScrollBar:horizontal { background: #F0F0F0; height: 10px; border-radius: 5px; }
    QScrollBar::handle:horizontal { background: #A0A0A0; min-width: 20px; border-radius: 5px; }
    QScrollBar::handle:horizontal:hover { background: #808080; }
"""

DROPDOWN_BOX = """
            QComboBox {
                background-color: #F0EEEE;
                padding: 5px;
                border-radius: 5px;
                min-width: 200px;
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

BLANK_CONTENT_BACKGROUND = """
            QWidget {
                background: qlineargradient(
                    spread: pad,
                    x1: 1, y1: 0, x2: 0, y2: 1,
                    stop: 0 #D3D3D3, 
                    stop: 0.3 #A9A9A9, 
                    stop: 0.6 #E6E6E6   
                );
                border: none; 
                padding: 0; 
            }
        """
        
BLANK_CONTENT_LABEL = """
            color: #555555;
            font-size: 22px;
            font-family: Arial, Helvetica, sans-serif;
            background: transparent; 
            margin-top: -200px;
        """
        
PROGRESS_BAR = """
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 5px;
                background-color: #f0f0f0;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #80C4E9;
                width: 20px;
            }
        """
        
SWITCH_BUTTON ="""
            QPushButton {
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                background-color: #95a5a6;
                color: black;
                border: none;
            }
            QPushButton:first-child {
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
            QPushButton:last-child {
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QPushButton:checked {
                background-color: #2ecc71; 
                color: white;
            }
        """

PROCESS_BUTTON = """
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #B2F2A0, stop:1 #66D966
                );
                color: #3C3939;
                font-weight: bold;
                border-radius: 10px;
                font-size: 14px;
                padding: 4px 8px;
                border: 1px solid #66D966;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #C7F3B8, stop:1 #82E582
                );
            }
            QPushButton:pressed {
                background-color: #56B856;
            }
        """
SAVE_AS_BUTTON = """
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #D3D3D3, stop:1 #A9A9A9
                );
                color: #3C3939;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                padding: 4px 8px;
                border: 1px solid #A9A9A9;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #E0E0E0, stop:1 #B8B8B8
                );
            }
            QPushButton:pressed {
                background-color: #808080;
            }
        """
        
DELETE_BUTTON = """
            QPushButton {
                padding: 8px 16px;
                font-size: 14px;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """

IMPORT_BUTTON = """
            QPushButton {
                padding: 8px 16px;
                font-size: 14px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """