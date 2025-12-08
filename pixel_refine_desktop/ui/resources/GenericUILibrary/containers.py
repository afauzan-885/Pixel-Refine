"""
Bootstrap-like Container and Layout Components for PySide6
Provides reusable layout containers
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
)
from PySide6.QtCore import Qt


class Container(QWidget):
    """
    Main container with padding (like Bootstrap container)

    Usage:
        container = Container(padding=15)
        container.add_widget(my_widget)
    """

    def __init__(self, padding=10, fluid=False, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)

        if fluid:
            # Fluid container - full width with minimal padding
            self.main_layout.setContentsMargins(5, 5, 5, 5)
        else:
            # Fixed container with padding
            self.main_layout.setContentsMargins(padding, padding, padding, padding)

        self.main_layout.setSpacing(10)

    def add_widget(self, widget, stretch=0):
        """Add widget to container"""
        self.main_layout.addWidget(widget, stretch)

    def add_layout(self, layout, stretch=0):
        """Add layout to container"""
        self.main_layout.addLayout(layout, stretch)

    def add_stretch(self, stretch=1):
        """Add stretch space"""
        self.main_layout.addStretch(stretch)


class Row(QWidget):
    """
    Horizontal row layout (like Bootstrap row)

    Usage:
        row = Row(spacing=10)
        row.add_column(widget1, stretch=1)
        row.add_column(widget2, stretch=2)
    """

    def __init__(self, spacing=10, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(spacing)

    def add_column(self, widget, stretch=0):
        """Add a column (widget) to the row"""
        self.layout.addWidget(widget, stretch)

    def add_stretch(self, stretch=1):
        """Add stretch space"""
        self.layout.addStretch(stretch)


class Col(QWidget):
    """
    Column widget (like Bootstrap col)

    Usage:
        col = Col(span=6)  # Half width (out of 12)
        col.add_widget(my_widget)
    """

    def __init__(self, span=12, parent=None):
        super().__init__(parent)

        self.span = span  # For future grid implementation
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

    def add_widget(self, widget, stretch=0):
        """Add widget to column"""
        self.layout.addWidget(widget, stretch)

    def add_stretch(self, stretch=1):
        """Add stretch space"""
        self.layout.addStretch(stretch)


class Stack(QWidget):
    """
    Vertical or horizontal stack layout

    Usage:
        stack = Stack(orientation="vertical", spacing=5)
        stack.add_item(widget1)
        stack.add_item(widget2)
    """

    def __init__(self, orientation="vertical", spacing=5, parent=None):
        super().__init__(parent)

        self.orientation = orientation

        if orientation == "vertical":
            self.layout = QVBoxLayout(self)
        else:
            self.layout = QHBoxLayout(self)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(spacing)

    def add_item(self, widget, stretch=0):
        """Add item to stack"""
        self.layout.addWidget(widget, stretch)

    def add_stretch(self, stretch=1):
        """Add stretch space"""
        self.layout.addStretch(stretch)

    def insert_item(self, index, widget):
        """Insert item at specific position"""
        self.layout.insertWidget(index, widget)

    def remove_item(self, widget):
        """Remove item from stack"""
        self.layout.removeWidget(widget)
        widget.setParent(None)

    def clear(self):
        """Remove all items"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class ScrollContainer(QScrollArea):
    """
    Scrollable container

    Usage:
        scroll = ScrollContainer()
        scroll.set_widget(my_large_widget)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setObjectName("scrollArea")

        # Create inner container
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)

        self.setWidget(self.container)

    def set_widget(self, widget):
        """Set the scrollable widget"""
        # Clear existing
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Add new widget
        self.container_layout.addWidget(widget)

    def add_widget(self, widget, stretch=0):
        """Add widget to scrollable area"""
        self.container_layout.addWidget(widget, stretch)


class GridLayout(QWidget):
    """
    Grid layout container

    Usage:
        grid = GridLayout(columns=3, spacing=10)
        grid.add_item(widget1)
        grid.add_item(widget2)
    """

    def __init__(self, columns=3, spacing=10, parent=None):
        super().__init__(parent)

        self.columns = columns
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(spacing)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.item_count = 0

    def add_item(self, widget):
        """Add item to grid"""
        row = self.item_count // self.columns
        col = self.item_count % self.columns

        self.grid_layout.addWidget(widget, row, col)
        self.item_count += 1

    def add_item_at(self, widget, row, col, row_span=1, col_span=1):
        """Add item at specific position"""
        self.grid_layout.addWidget(widget, row, col, row_span, col_span)

    def clear(self):
        """Clear all items"""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.item_count = 0


class Spacer(QWidget):
    """
    Spacer widget for adding space between elements

    Usage:
        spacer = Spacer(height=20)
        spacer = Spacer(width=20)
    """

    def __init__(self, width=None, height=None, parent=None):
        super().__init__(parent)

        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)

        self.setStyleSheet("background-color: transparent;")
