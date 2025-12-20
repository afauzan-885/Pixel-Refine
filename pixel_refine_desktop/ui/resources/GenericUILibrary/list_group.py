from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QWidget,
    QVBoxLayout,
    QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal, QEvent

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
    selection_changed = Signal(list)  # emits list of selected values (data)
    item_double_clicked = Signal(object)  # emits value (data) of double clicked item
    item_renamed = Signal(object, str)  # emits value (data) and new text
    delete_key_pressed = Signal()  # emits when delete key is pressed

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Internal List Widget
        self._list_widget = QListWidget()
        self._list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
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
            val = item.data(Qt.UserRole)
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
        """Add an item to the list. 'value' is hidden data associated with the item."""
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, value if value is not None else text)
        item.setFlags(item.flags() | Qt.ItemIsEditable)  # Make item editable
        self._list_widget.addItem(item)
        return item

    def clear(self):
        """Remove all items."""
        self._list_widget.clear()

    def get_selected_values(self):
        """Return a list of values (data) of currently selected items."""
        return [item.data(Qt.UserRole) for item in self._list_widget.selectedItems()]

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
        """Select item by its data value."""
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            if item.data(Qt.UserRole) == value:
                item.setSelected(True)
                self._list_widget.setCurrentItem(item)
                return True
        return False

    # --- Internals ---

    def _on_selection_change(self):
        values = self.get_selected_values()
        self.selection_changed.emit(values)

    def _on_item_double_clicked(self, item):
        """Enter edit mode on double click."""
        self.item_double_clicked.emit(item.data(Qt.UserRole))
        self._list_widget.editItem(item)

    def _on_item_changed(self, item):
        """Emit a signal when an item's text has been changed."""
        self.item_renamed.emit(item.data(Qt.UserRole), item.text())

    def eventFilter(self, source, event):
        if source is self._list_widget and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Delete:
                self.delete_key_pressed.emit()
                return True
        return super().eventFilter(source, event)

    @property
    def count(self):
        return self._list_widget.count()

    # Access raw widget if needed
    @property
    def widget(self):
        return self._list_widget
