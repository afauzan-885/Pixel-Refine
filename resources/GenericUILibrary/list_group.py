from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QWidget,
    QVBoxLayout,
    QAbstractItemView,
    QLabel,
)
from PySide6.QtCore import QEvent, Qt, Signal, Slot, QTimer, QRect
from resources.animations.animation_manager import (
    StackedWidgetAnimator,
)

from .theme import get_theme
from .mixins import RealtimeMixin


class ListGroup(QWidget, RealtimeMixin):
    """
    A friendly list component for displaying and managing lists of items.
    Wraps QListWidget with a simpler API and modern styling.
    Supports real-time updates via RealtimeMixin.

    Usage:
        list_group = ListGroup()
        list_group.add_item("Item 1", value=1)
        list_group.selection_changed.connect(my_handler)

        # Real-time binding
        list_group.bind_store(my_store, "project_list")
    """

    # Signals
    selection_changed = Signal(list)  # Emits list of selected values (data)
    item_double_clicked = Signal(object)  # Emits value (data) of double clicked item
    item_renamed = Signal(object, str)  # Emits value (data) and new text
    delete_key_pressed = Signal()  # Emits when delete key is pressed
    items_reordered = Signal(
        list, str, int, int
    )  # Emits (values, direction, start_idx, target_idx)

    def __init__(self, parent=None, reordering=False):
        super().__init__(parent)

        # Setup Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Configuration
        self._multi_mode = False
        self._reordering_animation = False
        self._animator = None
        self._pre_move_snapshot = None
        self._snapshot_overlay = None

        if reordering:
            self.reordering_animation = True
        self._move_mode = False
        self._last_move_direction = None  # Track 'up' or 'down' for animation
        self._last_move_start = -1
        self._last_move_target = -1
        self._list_widget = QListWidget()
        self._list_widget.setAlternatingRowColors(True)
        self._list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self._list_widget.setDragEnabled(True)
        self._list_widget.setAcceptDrops(True)
        self._list_widget.setDropIndicatorShown(True)
        self._list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._list_widget.setSpacing(2)

        # Styling
        self._apply_styles()

        layout.addWidget(self._list_widget)

        # Forward signals
        self._list_widget.itemSelectionChanged.connect(self._on_selection_change)
        self._list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._list_widget.itemChanged.connect(
            self._on_item_changed
        )  # Signal for when item text is changed
        self._list_widget.model().rowsAboutToBeMoved.connect(
            self._on_rows_about_to_be_moved
        )
        self._list_widget.model().rowsMoved.connect(self._on_rows_moved)
        self._list_widget.installEventFilter(self)

    def _apply_styles(self):
        """Apply modern styling to the list."""
        theme = get_theme()
        self._list_widget.setStyleSheet(
            f"""
            QListWidget {{
                background-color: {theme.bg_primary};
                border: 1px solid {theme.border_color};
                border-radius: {theme.radius_md}px;
                outline: none;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: {theme.radius_sm}px;
                color: {theme.text_primary};
                margin-bottom: 2px;
            }}
            QListWidget::item:alternate {{
                background-color: {theme.bg_secondary};
            }}
            QListWidget::item:hover {{
                background-color: {theme.bg_secondary};
            }}
            QListWidget::item:selected {{
                background-color: {theme.primary};
                color: {theme.text_white};
                font-weight: bold;
            }}
            QListWidget::item:selected:!active {{
                background-color: {theme.bg_secondary};
                color: {theme.text_primary};
            }}
        """
        )

    # --- RealtimeMixin Implementation ---

    def on_store_changed(self, key, value):
        """Handle real-time updates from DataStore."""
        if isinstance(value, list):
            # Expecting list of dicts like [{"text": "Item 1", "value": 1}, ...]
            # or list of strings ["Item 1", "Item 2"]
            self.sync_items(value)

    def sync_items(self, new_data_list):
        """
        Smart-update list items without clearing everything.
        Preserves selection for items that still exist.
        """
        # Store current selection
        selected_values = set(self.get_selected_values())

        # Map current items by value
        current_items = {}
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            val = item.data(Qt.ItemDataRole.UserRole)
            current_items[val] = item

        # New set of values
        new_values = []
        processed_data = []
        for item_data in new_data_list:
            if isinstance(item_data, dict):
                text = item_data.get("text", "")
                val = item_data.get("value", text)
            else:
                text = str(item_data)
                val = item_data
            new_values.append(val)
            processed_data.append((text, val))

        # 1. Remove items no longer in new data
        for val in list(current_items.keys()):
            if val not in new_values:
                item = current_items.pop(val)
                self._list_widget.takeItem(self._list_widget.row(item))

        # 2. Add or reorder items
        for i, (text, val) in enumerate(processed_data):
            if val in current_items:
                item = current_items[val]
                # Update text if changed
                if item.text() != text:
                    item.setText(text)
                # Ensure correct order
                if self._list_widget.row(item) != i:
                    self._list_widget.takeItem(self._list_widget.row(item))
                    self._list_widget.insertItem(i, item)
            else:
                # Add new item
                item = self.add_item(text, value=val)
                # If newly added item is not at target index, move it
                if self._list_widget.row(item) != i:
                    self._list_widget.takeItem(self._list_widget.row(item))
                    self._list_widget.insertItem(i, item)

            # 3. Restore selection
            if val in selected_values:
                item.setSelected(True)

    # --- Friendly API ---

    def add_item(self, text: str, value=None):
        """
        Add an item to the list.

        Args:
            text: The display text for the item.
            value: Hidden data associated with the item (defaults to text).
        """
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, value if value is not None else text)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)  # Make item editable
        self._list_widget.addItem(item)
        return item

    def clear(self):
        """Remove all items."""
        self._list_widget.clear()

    def clear_selection(self):
        """Clear all selected items."""
        self._list_widget.clearSelection()

    def get_selected_values(self):
        """Return a list of values (data) of currently selected items."""
        return [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self._list_widget.selectedItems()
        ]

    @property
    def reordering_animation(self):
        """Toggle cascading reorder animation."""
        return self._reordering_animation

    @reordering_animation.setter
    def reordering_animation(self, enabled: bool):
        self._reordering_animation = enabled
        if enabled and not self._animator:
            self._animator = StackedWidgetAnimator(self)
        elif not enabled and self._animator:
            self._animator = None

    def get_selected_labels(self):
        """Return a list of text labels of currently selected items."""
        return [item.text() for item in self._list_widget.selectedItems()]

    def remove_selected_items(self):
        """Remove currently selected items from the list."""
        for item in self._list_widget.selectedItems():
            self._list_widget.takeItem(self._list_widget.row(item))

    def select_first(self):
        """Select the first item if available."""
        if self._list_widget.count() > 0:
            self._list_widget.setCurrentRow(0)

    def select_item_by_value(self, value):
        """
        Select an item by its data value.
        Clears any existing selection first.

        Args:
            value: The data value (UserRole) to search for.
        Returns:
            True if item was found and selected, False otherwise.
        """
        self._list_widget.clearSelection()
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == value:
                item.setSelected(True)
                self._list_widget.setCurrentItem(item)
                return True
        return False

    def set_move_mode(self, enabled: bool):
        """Enable or disable keyboard move mode."""
        self._move_mode = enabled
        if enabled:
            theme = get_theme()
            self._list_widget.setStyleSheet(
                self._list_widget.styleSheet()
                + f"QListWidget {{ border: 2px solid {theme.primary}; }}"
            )
        else:
            self._apply_styles()

    def _move_item_keyboard(self, key):
        """
        Handle internal keyboard move for multiple selected items.
        Moves items as a group if possible.
        """
        lw = self._list_widget
        selected_items = lw.selectedItems()
        if not selected_items:
            return

        # Get rows and sort them
        rows = sorted([lw.row(item) for item in selected_items])

        moved = False
        if key == Qt.Key.Key_Up:
            # Move up: start from top-most, check if first can move
            if rows[0] > 0:
                for row in rows:
                    item = lw.takeItem(row)
                    lw.insertItem(row - 1, item)
                    item.setSelected(True)
                lw.setCurrentRow(rows[0] - 1)
                moved = True
                self._last_move_direction = "up"
                self._last_move_start = rows[0]
                self._last_move_target = rows[0] - 1
        elif key == Qt.Key.Key_Down:
            # Move down: start from bottom-most
            if rows[-1] < lw.count() - 1:
                # Reverse for downward move to maintain order during take/insert
                for row in reversed(rows):
                    item = lw.takeItem(row)
                    lw.insertItem(row + 1, item)
                    item.setSelected(True)
                lw.setCurrentRow(rows[-1] + 1)
                moved = True
                self._last_move_direction = "down"
                self._last_move_start = rows[-1]
                self._last_move_target = rows[-1] + 1

        if moved:
            self._emit_reordered()
            # "One-shot" logic: disable move mode after one operation
            self.set_move_mode(False)

    # --- Internals ---

    def _on_selection_change(self):
        values = self.get_selected_values()
        self.selection_changed.emit(values)

    def _on_item_double_clicked(self, item):
        """Enter edit mode on double click."""
        self.item_double_clicked.emit(item.data(Qt.ItemDataRole.UserRole))
        self._list_widget.editItem(item)

    def _on_item_changed(self, item):
        """Emit a signal when an item's text has been changed."""
        self.item_renamed.emit(item.data(Qt.ItemDataRole.UserRole), item.text())

    def _on_rows_about_to_be_moved(self, parent, start, end, destination, row):
        """Capture a snapshot of the list BEFORE the move happens."""
        if self._reordering_animation:
            # Clear previous overlay if any (safety)
            if self._snapshot_overlay:
                self._snapshot_overlay.deleteLater()
                self._snapshot_overlay = None

            # Capture current visual state
            self._pre_move_snapshot = self._list_widget.grab()

    def _on_rows_moved(self, parent, start, end, destination, row):
        """Handle internal move of items (Drag & Drop)."""
        # If row > start, it's moving DOWN
        if row > start:
            self._last_move_direction = "down"
            self._last_move_target = row - 1  # Item lands at row-1 when moving forward
        else:
            self._last_move_direction = "up"
            self._last_move_target = row

        self._last_move_start = start

        # 1. Overlay the snapshot IMMEDIATELY to mask the jump
        if self._reordering_animation and self._pre_move_snapshot:
            self._snapshot_overlay = QLabel(self)
            self._snapshot_overlay.setPixmap(self._pre_move_snapshot)
            self._snapshot_overlay.setFixedSize(self._list_widget.size())
            self._snapshot_overlay.move(self._list_widget.pos())
            self._snapshot_overlay.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents
            )
            self._snapshot_overlay.show()
            self._snapshot_overlay.raise_()

        # Delay slightly to allow the model to finish updating
        QTimer.singleShot(10, self._emit_reordered)

    def get_all_values(self):
        """Helper to get all item values in current order."""
        return [
            self._list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self._list_widget.count())
        ]

    def _emit_reordered(self):
        """Emit notification after a small delay to ensure model consistency."""
        all_values = self.get_all_values()

        # Trigger native animation if enabled
        if self._reordering_animation and self._animator:
            self._animator.animate_list_reorder(
                self._list_widget,
                self._last_move_start,
                self._last_move_target,
                start_delay=150,
                overlay_to_remove=self._snapshot_overlay,
            )
            # Clear internal references
            self._snapshot_overlay = None
            self._pre_move_snapshot = None

        self.items_reordered.emit(
            all_values,
            self._last_move_direction,
            self._last_move_start,
            self._last_move_target,
        )
        self._last_move_direction = None  # Reset after emit
        self._last_move_start = -1
        self._last_move_target = -1

    def eventFilter(self, source, event):
        if source is self._list_widget and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Delete:
                self.delete_key_pressed.emit()
                return True
            if self._move_mode and event.key() in [Qt.Key.Key_Up, Qt.Key.Key_Down]:
                self._move_item_keyboard(event.key())
                return True
        return super().eventFilter(source, event)

    @property
    def count(self):
        return self._list_widget.count()

    # Access raw widget if needed
    @property
    def widget(self):
        return self._list_widget

    def to_qml(self, indent=0):
        tab = "    " * indent
        reordering = getattr(self, "_reordering_animation", False) or \
                     getattr(self, "reordering_animation", False)
        qml = f"{tab}ListView {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    height: {max(200, self._list_widget.count() * 40)}\n"
        qml += f"{tab}    clip: true\n"
        qml += f"{tab}    spacing: 2\n"
        # reordering=True -> aktifkan drag handle di QML
        if reordering:
            qml += f"{tab}    // reordering enabled — items bisa di-drag untuk diurutkan ulang\n"
        qml += f"{tab}    model: ListModel {{\n"
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            text = item.text().replace("'", "\\'")
            qml += f"{tab}        ListElement {{ text: '{text}' }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}    delegate: Rectangle {{\n"
        qml += f"{tab}        width: ListView.view.width\n"
        qml += f"{tab}        height: 36\n"
        qml += f"{tab}        radius: genericTheme.radiusSm\n"
        qml += f"{tab}        color: genericTheme.bgPrimary\n"
        qml += f"{tab}        border.color: genericTheme.borderColor\n"
        qml += f"{tab}        border.width: 1\n"
        qml += f"{tab}        Row {{\n"
        qml += f"{tab}            anchors.fill: parent\n"
        qml += f"{tab}            anchors.leftMargin: 12\n"
        qml += f"{tab}            spacing: 8\n"
        if reordering:
            # Tambahkan drag handle visual jika reordering aktif
            qml += f"{tab}            Text {{ text: '⠿'; color: genericTheme.textMuted; anchors.verticalCenter: parent.verticalCenter; font.pixelSize: 14 }}\n"
        qml += f"{tab}            Text {{ text: model.text; anchors.verticalCenter: parent.verticalCenter; color: genericTheme.textPrimary; elide: Text.ElideRight }}\n"
        qml += f"{tab}        }}\n"
        qml += f"{tab}        MouseArea {{ anchors.fill: parent; onClicked: appBridge.openTool(model.text) }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml
