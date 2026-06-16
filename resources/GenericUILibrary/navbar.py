"""
Bootstrap-like Navbar Components for PySide6
Provides navigation bar components
"""

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PySide6.QtCore import Signal, Qt


class Navbar(QFrame):
    """
    Bootstrap-like navigation bar

    Usage:
        navbar = Navbar(brand="My App")
        navbar.add_nav_item("Home", callback=on_home)
        navbar.add_nav_item("Settings", callback=on_settings)
    """

    nav_clicked = Signal(str)  # item_name

    def __init__(self, brand="", height=50, parent=None):
        super().__init__(parent)

        self.setFixedHeight(height)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #2c3e50;
                border-bottom: 2px solid #34495e;
            }
        """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(10)

        # Brand/Logo
        if brand:
            self.brand_label = QLabel(brand)
            self.brand_label.setStyleSheet(
                """
                font-size: 16pt;
                font-weight: bold;
                color: white;
                padding: 5px;
            """
            )
            layout.addWidget(self.brand_label)
        else:
            self.brand_label = None

        # Nav items container
        self.nav_container = QWidget()
        self.nav_layout = QHBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(5)

        layout.addWidget(self.nav_container, 1)

        # Right actions container
        self.actions_container = QWidget()
        self.actions_layout = QHBoxLayout(self.actions_container)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_layout.setSpacing(5)

        layout.addWidget(self.actions_container)

        self.nav_items = []

    def set_brand(self, brand):
        """Set brand text"""
        if self.brand_label:
            self.brand_label.setText(brand)

    def add_nav_item(self, text, callback=None):
        """Add navigation item"""
        item = NavItem(text)

        if callback:
            item.clicked.connect(callback)

        item.clicked.connect(lambda: self.nav_clicked.emit(text))

        self.nav_layout.addWidget(item)
        self.nav_items.append(item)

        return item

    def add_action(self, widget):
        """Add action widget to right side"""
        self.actions_layout.addWidget(widget)

    def set_active_item(self, index):
        """Set active navigation item"""
        for i, item in enumerate(self.nav_items):
            item.set_active(i == index)


class NavItem(QPushButton):
    """
    Navigation item button

    Usage:
        item = NavItem("Home")
        item.clicked.connect(on_click)
    """

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self.is_active = False

        self.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 11pt;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """
        )

    def set_active(self, active):
        """Set active state"""
        self.is_active = active

        if active:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.15);
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    font-size: 11pt;
                    border-radius: 4px;
                    border-bottom: 3px solid #3498db;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """
            )
        else:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    font-size: 11pt;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """
            )


class Sidebar(QFrame):
    """
    Vertical sidebar navigation

    Usage:
        sidebar = Sidebar(width=200)
        sidebar.add_item("Dashboard", icon_path="...")
        sidebar.add_item("Settings")
        sidebar.item_clicked.connect(on_item_click)
    """

    item_clicked = Signal(int, str)  # index, text

    def __init__(self, width=200, parent=None):
        super().__init__(parent)

        self.setFixedWidth(width)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.items = []
        self.current_index = -1

    def add_item(self, text, icon_path=None):
        """Add sidebar item"""
        item = SidebarItem(text, icon_path)

        index = len(self.items)
        item.clicked.connect(lambda: self._on_item_clicked(index, text))

        self.layout().addWidget(item)
        self.items.append(item)

        return item

    def add_separator(self):
        """Add separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #34495e;")
        separator.setFixedHeight(1)
        self.layout().addWidget(separator)

    def add_stretch(self):
        """Add stretch to push items to top"""
        self.layout().addStretch()

    def set_active_item(self, index):
        """Set active item"""
        for i, item in enumerate(self.items):
            item.set_active(i == index)
        self.current_index = index

    def _on_item_clicked(self, index, text):
        """Handle item click"""
        self.set_active_item(index)
        self.item_clicked.emit(index, text)


class SidebarItem(QPushButton):
    """
    Sidebar navigation item

    Usage:
        item = SidebarItem("Dashboard", icon_path="...")
        item.clicked.connect(on_click)
    """

    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)

        if icon_path:
            from PySide6.QtGui import QIcon

            self.setIcon(QIcon(icon_path))

        self.is_active = False

        self.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 15px 20px;
                text-align: left;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """
        )

    def set_active(self, active):
        """Set active state"""
        self.is_active = active

        if active:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 15px 20px;
                    text-align: left;
                    font-size: 11pt;
                    border-left: 4px solid #2980b9;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """
            )
        else:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 15px 20px;
                    text-align: left;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """
            )
