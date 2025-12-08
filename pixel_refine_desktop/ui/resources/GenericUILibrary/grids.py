"""
Bootstrap-like Grid and Gallery Components for PySide6
Provides grid layouts for displaying items (images, cards, etc.)
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QGridLayout,
    QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QPen, QColor


class GridContainer(QScrollArea):
    """
    Scrollable grid container for displaying items

    Usage:
        grid = GridContainer(columns=4)
        grid.add_item(GridItem("Item 1"))
        grid.add_item(GridItem("Item 2"))
    """

    def __init__(self, columns=4, spacing=10, parent=None):
        super().__init__(parent)

        self.columns = columns
        self.setWidgetResizable(True)
        self.setObjectName("scrollArea")

        # Container widget
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(spacing)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.setWidget(self.container)

        self.item_count = 0

    def add_item(self, widget):
        """Add item to grid"""
        row = self.item_count // self.columns
        col = self.item_count % self.columns

        self.grid_layout.addWidget(widget, row, col)
        self.item_count += 1

    def clear_items(self):
        """Clear all items"""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.item_count = 0

    def get_item_count(self):
        """Get number of items"""
        return self.item_count


class GridItem(QWidget):
    """
    Individual grid item with selection support

    Usage:
        item = GridItem("item_1", "Image 1")
        item.clicked.connect(on_click)
    """

    clicked = Signal(str)  # item_id
    double_clicked = Signal(str)  # item_id

    def __init__(self, item_id, label="", size=110, parent=None):
        super().__init__(parent)

        self.item_id = item_id
        self._is_selected = False

        self.setFixedSize(size, size)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Visual placeholder
        self.visual_box = QLabel(label)
        self.visual_box.setAlignment(Qt.AlignCenter)
        self.visual_box.setWordWrap(True)
        self.visual_box.setStyleSheet(
            """
            background-color: #ddd;
            border: 1px solid #bbb;
            color: #333;
            border-radius: 4px;
        """
        )

        layout.addWidget(self.visual_box)

    def set_selected(self, selected):
        """Set selection state"""
        if self._is_selected != selected:
            self._is_selected = selected
            self.update()

    def is_selected(self):
        """Check if selected"""
        return self._is_selected

    def set_content(self, widget):
        """Replace visual box with custom widget"""
        self.visual_box.setParent(None)
        self.visual_box = widget
        self.layout().addWidget(widget)

    def set_label(self, label):
        """Set label text"""
        if isinstance(self.visual_box, QLabel):
            self.visual_box.setText(label)

    def paintEvent(self, event):
        """Draw selection border"""
        super().paintEvent(event)

        if self._is_selected:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            # Blue highlight border
            border_pen = QPen(QColor(0, 120, 215))
            border_pen.setWidth(3)

            painter.setPen(border_pen)
            painter.setBrush(Qt.NoBrush)

            rect = self.rect().adjusted(2, 2, -2, -2)
            painter.drawRoundedRect(rect, 4, 4)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle click"""
        self.clicked.emit(self.item_id)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double click"""
        self.double_clicked.emit(self.item_id)


class Gallery(QFrame):
    """
    Gallery component with header and grid

    Usage:
        gallery = Gallery(title="Images", columns=5)
        gallery.add_item("img1", "Photo 1")
        gallery.item_clicked.connect(on_click)
    """

    item_clicked = Signal(str, str)  # item_id, label
    item_double_clicked = Signal(str, str)  # item_id, label

    def __init__(self, title="", columns=4, show_header=True, parent=None):
        super().__init__(parent)

        self.setObjectName("displayContainer")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        if show_header:
            header_layout = QHBoxLayout()

            self.title_label = QLabel(title)
            self.title_label.setObjectName("sectionTitle")

            header_layout.addWidget(self.title_label)
            header_layout.addStretch()

            layout.addLayout(header_layout)
        else:
            self.title_label = None

        # Grid container
        self.grid = GridContainer(columns=columns)
        layout.addWidget(self.grid, 1)

        self.items = {}  # item_id -> GridItem

    def set_title(self, title):
        """Set gallery title"""
        if self.title_label:
            self.title_label.setText(title)

    def add_item(self, item_id, label=""):
        """Add item to gallery"""
        item = GridItem(item_id, label)
        item.clicked.connect(lambda id: self.item_clicked.emit(id, label))
        item.double_clicked.connect(lambda id: self.item_double_clicked.emit(id, label))

        self.grid.add_item(item)
        self.items[item_id] = item

    def remove_item(self, item_id):
        """Remove item from gallery"""
        if item_id in self.items:
            item = self.items[item_id]
            item.setParent(None)
            item.deleteLater()
            del self.items[item_id]

    def clear_items(self):
        """Clear all items"""
        self.grid.clear_items()
        self.items.clear()

    def get_item(self, item_id):
        """Get item by ID"""
        return self.items.get(item_id)

    def set_item_selected(self, item_id, selected=True):
        """Set item selection state"""
        if item_id in self.items:
            self.items[item_id].set_selected(selected)


class ThumbnailGrid(GridContainer):
    """
    Grid specifically for thumbnails/images

    Usage:
        grid = ThumbnailGrid(columns=6)
        grid.add_thumbnail("thumb1", "Image 1.jpg")
    """

    thumbnail_clicked = Signal(str)  # item_id

    def __init__(self, columns=5, thumbnail_size=100, parent=None):
        super().__init__(columns=columns, parent=parent)

        self.thumbnail_size = thumbnail_size
        self.thumbnails = {}

    def add_thumbnail(self, item_id, label=""):
        """Add thumbnail"""
        thumb = GridItem(item_id, label, size=self.thumbnail_size)
        thumb.clicked.connect(self.thumbnail_clicked.emit)

        self.add_item(thumb)
        self.thumbnails[item_id] = thumb

    def get_thumbnail(self, item_id):
        """Get thumbnail by ID"""
        return self.thumbnails.get(item_id)

    def clear_thumbnails(self):
        """Clear all thumbnails"""
        self.clear_items()
        self.thumbnails.clear()
