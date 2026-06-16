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
from PySide6.QtCore import QTimer, Qt, Signal, Slot
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
        self.grid_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self.setWidget(self.container)

        self.item_count = 0

        # For responsive mode: store widgets for rebuild on resize
        self._stored_widgets = []

        # ID-based mapping for smart updates
        self._items_map = {}  # item_id -> widget
        self.item_factory = None  # Function: (item_data) -> QWidget
        self._is_batch_updating = False

    def add_item(self, widget):
        """Add item to grid based on wrap mode and column mode"""
        # Store widget for responsive mode
        if self.column_mode == "responsive":
            self._stored_widgets.append(widget)

        # Calculate columns if responsive mode AND not in batch update
        if self.column_mode == "responsive" and not self._is_batch_updating:
            old_cols = self.columns
            self.columns = self._calculate_responsive_columns()
            if old_cols != self.columns and self.item_count > 0:
                # If columns changed, we MUST rebuild to avoid overlapping items
                self._rebuild_grid()
                return  # Rebuild managed the addition

        # Reinforced addition
        if self._is_widget_alive(widget):
            self._add_to_layout_grid(widget)

    def _calculate_responsive_columns(self):
        """
        Calculate number of columns based on available width and item size.
        """
        viewport = self.viewport()
        if not viewport:
            return self.columns

        available_width = viewport.width()

        # Debounce/Init handling
        if available_width <= 100:
            parent_scroll = self.parentWidget()
            if isinstance(parent_scroll, QWidget) and parent_scroll.width() > 100:
                available_width = parent_scroll.width()
            else:
                available_width = 800

        # Ambil margin dari layout secara dinamis
        m = self.grid_layout.contentsMargins()
        padding = m.left() + m.right()
        usable_width = available_width - padding

        spacing = self.spacing or 0
        item_width_with_spacing = self.item_width + spacing

        # Formula cerdas: (Width_tersedia + satu_spacing) / (Lebar_item + satu_spacing)
        # Ini karena item terakhir tidak butuh spacing di kanannya.
        if item_width_with_spacing <= 0:
            return 4

        columns = max(1, int((usable_width + spacing) / item_width_with_spacing))
        return columns

    def _is_widget_alive(self, widget):
        """Reinforced check for PySide6 C++ objects."""
        if widget is None:
            return False
        try:
            _ = widget.parent()
            return True
        except (RuntimeError, AttributeError):
            return False

    def remove_item(self, widget, rebuild=True):
        """Safe removal of tracking widget."""
        if widget in self._stored_widgets:
            self._stored_widgets.remove(widget)
        try:
            self.grid_layout.removeWidget(widget)
        except (RuntimeError, AttributeError):
            pass
        if rebuild and not self._is_batch_updating:
            self._rebuild_grid()

    def clear_items(self):
        """Clear all items and reset state safely."""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                try:
                    item.widget().deleteLater()
                except RuntimeError:
                    pass
        self.item_count = 0
        self._stored_widgets.clear()
        self._items_map.clear()

        # Jika responsive, hitung ulang kolom segera agar tidak stuck di default lama
        if self.column_mode == "responsive":
            self.columns = self._calculate_responsive_columns()
        else:
            self.columns = 4  # Fallback for fixed mode if not specified

    def set_batch_update(self, active: bool):
        """Enable or disable batch update mode to optimize bulk additions."""
        self._is_batch_updating = active
        if not active:
            self._rebuild_grid()

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
        """Rebuild grid layout with current settings (Full Width Reinforced)"""
        # 1. Pastikan jumlah kolom terbaru sebelum mengisi ulang
        if self.column_mode == "responsive":
            self.columns = self._calculate_responsive_columns()

        # 2. Filter widget yang masih hidup
        self._stored_widgets = [
            w for w in self._stored_widgets if self._is_widget_alive(w)
        ]
        valid_widgets = self._stored_widgets.copy()

        # 3. Kosongkan layout tanpa menghapus widget nya
        while self.grid_layout.count():
            self.grid_layout.takeAt(0)

        # 4. Susun ulang
        self.item_count = 0
        for widget in valid_widgets:
            if self._is_widget_alive(widget):
                try:
                    self._add_to_layout_grid(widget)
                except RuntimeError:
                    continue

    def _add_to_layout_grid(self, widget):
        """Helper internal untuk addWidget dengan penghitungan row/col (Heavy-Duty)."""
        if not self._is_widget_alive(widget):
            return

        if self.wrap_mode == "vertical":
            # Cegah pembagian dengan nol
            cols = max(1, self.columns)
            row = self.item_count // cols
            col = self.item_count % cols
        else:
            rows = max(1, self.columns)
            col = self.item_count // rows
            row = self.item_count % rows

        try:
            self.grid_layout.addWidget(widget, row, col)
            self.item_count += 1
        except RuntimeError:
            # Proteksi terakhir jika widget mati tepat saat ditambahkan
            pass

    def resizeEvent(self, event):
        """Handle resize event to recalculate responsive columns"""
        super().resizeEvent(event)

        # If responsive mode AND not in batch update, check if rebuild needed
        if (
            self.column_mode == "responsive"
            and self._stored_widgets
            and not self._is_batch_updating
        ):
            new_columns = self._calculate_responsive_columns()
            if new_columns != self.columns:
                # Debounce: Hanya rebuild setelah resize selesai
                if not hasattr(self, "_resize_timer"):

                    self._resize_timer = QTimer(self)
                    self._resize_timer.setSingleShot(True)
                    self._resize_timer.setInterval(150)  # 150ms debounce
                    self._resize_timer.timeout.connect(self._rebuild_grid)

                if not self._resize_timer.isActive():
                    self._resize_timer.start()

    def to_qml(self, indent=0):
        tab = "    " * indent
        # wrap_mode='vertical' -> vertical scroll (default)
        # wrap_mode='horizontal' -> horizontal scroll
        scroll_orient = "vertical" if self.wrap_mode == "vertical" else "horizontal"

        # column_mode='responsive' -> columns dihitung otomatis dari item_width
        # column_mode='fixed'      -> gunakan self.columns langsung
        if self.column_mode == "responsive" and self.item_width and self.item_width > 0:
            # Estimasi kolom untuk preview QML (parent.width / item_width)
            col_expr = f"Math.max(1, Math.floor(parent.width / {self.item_width}))"
        else:
            col_expr = str(self.columns)

        qml = f"{tab}ScrollView {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    height: parent.height\n"
        qml += f"{tab}    clip: true\n"
        if scroll_orient == "horizontal":
            qml += f"{tab}    contentHeight: parent.height\n"
        else:
            qml += f"{tab}    contentWidth: parent.width\n"
        qml += f"{tab}    Grid {{\n"
        qml += f"{tab}        columns: {col_expr}  // column_mode='{self.column_mode}', item_width={self.item_width}\n"
        qml += f"{tab}        spacing: {self.spacing}\n"
        qml += f"{tab}        width: parent.width\n"
        for w in self._stored_widgets:
            if hasattr(w, "to_qml"):
                qml += w.to_qml(indent + 2) + "\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml


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

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        # Visual placeholder
        self.visual_box = QLabel(label)
        self.visual_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.visual_box.setWordWrap(True)
        self.visual_box.setStyleSheet(
            """
            background-color: #ddd;
            border: 1px solid #bbb;
            color: #333;
            border-radius: 4px;
        """
        )

        self.main_layout.addWidget(self.visual_box)

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
        if self.visual_box:
            try:
                self.visual_box.setParent(None)
            except RuntimeError:
                pass

        self.visual_box = widget
        if self.main_layout and widget:
            self.main_layout.addWidget(widget)

    def set_label(self, label):
        """Set label text"""
        if self.visual_box and isinstance(self.visual_box, QLabel):
            try:
                self.visual_box.setText(label)
            except RuntimeError:
                pass

    def paintEvent(self, event):
        """Draw selection border"""
        super().paintEvent(event)

        if self._is_selected:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Blue highlight border
            border_pen = QPen(QColor(0, 120, 215))
            border_pen.setWidth(3)

            painter.setPen(border_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            rect = self.rect().adjusted(2, 2, -2, -2)
            painter.drawRoundedRect(rect, 4, 4)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle click"""
        self.clicked.emit(self.item_id)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double click"""
        self.double_clicked.emit(self.item_id)

    def to_qml(self, indent=0):
        tab = "    " * indent
        label = self.visual_box.text() if isinstance(self.visual_box, QLabel) else ""
        label_escaped = label.replace("'", "\\'")
        item_id_escaped = str(self.item_id).replace("'", "\\'")
        selected = self._is_selected
        size = self.width() if self.width() > 0 else 110
        border_color = "genericTheme.primary" if selected else "'#bbb'"
        border_width = 2 if selected else 1
        qml = f"{tab}Rectangle {{\n"
        qml += f"{tab}    // item_id: '{item_id_escaped}'\n"
        qml += f"{tab}    width: {size}\n"
        qml += f"{tab}    height: {size}\n"
        qml += f"{tab}    radius: genericTheme.radiusSm\n"
        qml += f"{tab}    color: genericTheme.bgSecondary\n"
        qml += f"{tab}    border.color: {border_color}\n"
        qml += f"{tab}    border.width: {border_width}\n"
        qml += f"{tab}    Text {{ text: '{label_escaped}'; anchors.centerIn: parent; color: genericTheme.textPrimary; wrapMode: Text.WordWrap; width: parent.width - 10; horizontalAlignment: Text.AlignHCenter }}\n"
        qml += f"{tab}    MouseArea {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        # Gunakan item_id sebagai identifier — identik dengan signal clicked(item_id) di desktop
        qml += f"{tab}        onClicked: appBridge.openTool('{item_id_escaped}')\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml


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
        # Simpan show_header untuk digunakan oleh to_qml()
        self._show_header = show_header

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

    def to_qml(self, indent=0):
        tab = "    " * indent
        title = self.title_label.text() if self.title_label else ""
        title_escaped = title.replace("'", "\'")
        show_header = getattr(self, "_show_header", True)
        qml = f"{tab}Rectangle {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    height: 300\n"
        qml += f"{tab}    color: genericTheme.bgPrimary\n"
        qml += f"{tab}    radius: genericTheme.radiusLg\n"
        qml += f"{tab}    border.color: genericTheme.borderColor\n"
        qml += f"{tab}    border.width: 1\n"
        qml += f"{tab}    Column {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        anchors.margins: 10\n"
        qml += f"{tab}        spacing: 10\n"
        # Render header hanya jika show_header=True — selaras dengan desktop
        if show_header and title_escaped:
            qml += f"{tab}        Text {{ text: '{title_escaped}'; font.bold: true; font.pixelSize: 16; color: genericTheme.textPrimary }}\n"
        qml += f"{tab}        Grid {{\n"
        qml += f"{tab}            columns: {self.grid.columns}\n"
        qml += f"{tab}            spacing: {self.grid.spacing}\n"
        qml += f"{tab}            width: parent.width\n"
        for item_id, item in self.items.items():
            if hasattr(item, "to_qml"):
                qml += item.to_qml(indent + 3) + "\n"
        qml += f"{tab}        }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml



class ThumbnailGrid(GridContainer):
    """
    Grid specifically for thumbnails/images with wrap support

    Usage:
        grid = ThumbnailGrid(columns=6, wrap_mode='vertical')
        grid.add_thumbnail("thumb1", "Image 1.jpg")
    """

    thumbnail_clicked = Signal(str)  # item_id

    def __init__(
        self, columns=5, thumbnail_size=110, wrap_mode="vertical", parent=None
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

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}ScrollView {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    height: parent.height\n"
        qml += f"{tab}    clip: true\n"
        qml += f"{tab}    Grid {{\n"
        qml += f"{tab}        columns: {self.columns}\n"
        qml += f"{tab}        spacing: {self.spacing}\n"
        qml += f"{tab}        width: parent.width\n"
        for w in self._stored_widgets:
            if hasattr(w, "to_qml"):
                qml += w.to_qml(indent + 2) + "\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml
