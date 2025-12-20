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
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QMouseEvent, QPainter, QPen, QColor

from .mixins import RealtimeMixin


class GridContainer(QScrollArea, RealtimeMixin):
    """
    Scrollable grid container for displaying items with wrap and responsive column support

    Modes:
        - 'vertical': Items wrap to next row (vertical scroll)
        - 'horizontal': Items wrap to next column (horizontal scroll)

    Column Modes:
        - 'fixed': Use specified columns parameter (default)
        - 'responsive': Auto-calculate columns based on container width and item size

    Usage - Fixed Columns:
        grid = GridContainer(columns=4, wrap_mode='vertical')
        grid.add_item(GridItem("Item 1"))

    Usage - Responsive Columns:
        grid = GridContainer(item_width=120, spacing=10, column_mode='responsive')
        grid.add_item(GridItem("Item 1"))
        # Columns auto-adjust based on available width
    """

    def __init__(
        self,
        columns=4,
        spacing=10,
        wrap_mode="vertical",
        column_mode="fixed",
        item_width=120,
        parent=None,
    ):
        super().__init__(parent)

        self.columns = columns
        self.wrap_mode = wrap_mode  # 'vertical' or 'horizontal'
        self.column_mode = column_mode  # 'fixed' or 'responsive'
        self.item_width = item_width  # For responsive mode calculation
        self.spacing = spacing
        self.setWidgetResizable(True)
        self.setObjectName("scrollArea")

        # Set scrollbar policy based on wrap mode
        if wrap_mode == "vertical":
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        elif wrap_mode == "horizontal":
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Container widget
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(spacing)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.setWidget(self.container)

        self.item_count = 0

        # For responsive mode: store widgets for rebuild on resize
        self._stored_widgets = []

        # ID-based mapping for smart updates
        self._items_map = {}  # item_id -> widget
        self.item_factory = None  # Function: (item_data) -> QWidget

    def add_item(self, widget):
        """Add item to grid based on wrap mode and column mode"""
        # Store widget for responsive mode
        if self.column_mode == "responsive":
            self._stored_widgets.append(widget)

        # Calculate columns if responsive mode
        if self.column_mode == "responsive":
            self.columns = self._calculate_responsive_columns()

        if self.wrap_mode == "vertical":
            # Vertical wrap: fill columns first, then rows
            row = self.item_count // self.columns
            col = self.item_count % self.columns
        elif self.wrap_mode == "horizontal":
            # Horizontal wrap: fill rows first, then columns
            col = self.item_count // self.columns
            row = self.item_count % self.columns
        else:
            # Default to vertical
            row = self.item_count // self.columns
            col = self.item_count % self.columns

        self.grid_layout.addWidget(widget, row, col)
        self.item_count += 1

    def _calculate_responsive_columns(self):
        """
        Calculate number of columns based on available width and item size.

        Formula: (available_width - padding) / (item_width + spacing)
        """
        # Get available width dari scroll area
        available_width = self.viewport().width()

        # Minimum width check
        if available_width <= 0:
            available_width = 800  # Default fallback

        # Calculate: (width - left_margin - right_margin) / (item_width + spacing)
        padding = 10 + 10  # left + right margins
        usable_width = available_width - padding

        # Columns = usable_width / (item_width + spacing)
        # But ensure minimum 1 column
        item_width_with_spacing = self.item_width + self.spacing
        columns = max(1, int(usable_width / item_width_with_spacing))

        return columns

    def clear_items(self):
        """Clear all items"""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.item_count = 0
        self._stored_widgets.clear()
        self._items_map.clear()

    # --- Realtime System ---

    def on_store_changed(self, key, value):
        """Handle real-time updates from DataStore."""
        if isinstance(value, list):
            # Expecting list of dicts like [{"id": "1", "label": "Image 1"}, ...]
            self.sync_items(value)

    def sync_items(self, new_data_list):
        """
        Smart-update grid items based on ID.
        new_data_list: list of dicts with 'id' key.
        """
        new_ids = [str(item.get("id")) for item in new_data_list if "id" in item]

        # 1. Remove items no longer in list
        ids_to_remove = set(self._items_map.keys()) - set(new_ids)
        for item_id in ids_to_remove:
            widget = self._items_map.pop(item_id)
            if widget in self._stored_widgets:
                self._stored_widgets.remove(widget)
            self.grid_layout.removeWidget(widget)
            widget.deleteLater()

        # 2. Add or Reorder
        # Since QGridLayout is row/col based, it's easier to just re-layout everything
        # if the order or set of items changed, but we keep the widget instances.

        old_item_count = self.item_count
        self.item_count = 0

        # Temporary list of all widgets in new order
        ordered_widgets = []

        for item_data in new_data_list:
            item_id = str(item_data.get("id"))
            label = item_data.get("label", item_data.get("name", ""))

            if item_id in self._items_map:
                widget = self._items_map[item_id]
                # Update label if it's a GridItem
                if hasattr(widget, "set_label"):
                    widget.set_label(label)
            else:
                # Use factory if available, else default to GridItem
                if self.item_factory:
                    widget = self.item_factory(item_data)
                else:
                    from .grids import GridItem  # Local import to avoid circular

                    widget = GridItem(item_id, label)

                self._items_map[item_id] = widget

            ordered_widgets.append(widget)

        # Clear layout (remove but don't delete)
        while self.grid_layout.count():
            self.grid_layout.takeAt(0)

        # Reset stored widgets for responsive mode if needed
        if self.column_mode == "responsive":
            self._stored_widgets = ordered_widgets.copy()
            self.columns = self._calculate_responsive_columns()

        # Re-add in order
        for widget in ordered_widgets:
            if self.wrap_mode == "vertical":
                row = self.item_count // self.columns
                col = self.item_count % self.columns
            else:
                col = self.item_count // self.columns
                row = self.item_count % self.columns

            self.grid_layout.addWidget(widget, row, col)
            self.item_count += 1

    def get_item_count(self):
        """Get number of items"""
        return self.item_count

    def set_wrap_mode(self, mode):
        """
        Change wrap mode dynamically.

        Args:
            mode: 'vertical' or 'horizontal'
        """
        if mode in ("vertical", "horizontal"):
            self.wrap_mode = mode
            self._rebuild_grid()

    def set_column_mode(self, mode, item_width=None):
        """
        Change column mode dynamically.

        Args:
            mode: 'fixed' or 'responsive'
            item_width: Item width for responsive calculation (if changing to responsive)
        """
        if mode in ("fixed", "responsive"):
            self.column_mode = mode
            if item_width is not None:
                self.item_width = item_width
            self._rebuild_grid()

    def _rebuild_grid(self):
        """Rebuild grid layout with current settings"""
        # Store all widgets
        widgets = []
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                widgets.append(item.widget())

        # Also include any stored widgets from responsive mode
        if self.column_mode == "responsive" and self._stored_widgets:
            widgets = self._stored_widgets.copy()

        # Reset counter
        self.item_count = 0

        # Re-add all widgets with new layout
        for widget in widgets:
            self.add_item(widget)

    def resizeEvent(self, event):
        """Handle resize event to recalculate responsive columns"""
        super().resizeEvent(event)

        # If responsive mode, rebuild grid on resize
        if self.column_mode == "responsive" and self._stored_widgets:
            new_columns = self._calculate_responsive_columns()
            if new_columns != self.columns:
                self._rebuild_grid()


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
    Grid specifically for thumbnails/images with wrap support

    Usage:
        grid = ThumbnailGrid(columns=6, wrap_mode='vertical')
        grid.add_thumbnail("thumb1", "Image 1.jpg")
    """

    thumbnail_clicked = Signal(str)  # item_id

    def __init__(
        self, columns=5, thumbnail_size=100, wrap_mode="vertical", parent=None
    ):
        super().__init__(columns=columns, wrap_mode=wrap_mode, parent=parent)

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
