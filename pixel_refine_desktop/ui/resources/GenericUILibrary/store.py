from PySide6.QtCore import QObject, Signal, QFileSystemWatcher, QTimer
import json
import os


class DataStore(QObject):
    """
    Centralized data store for GenericUILibrary.
    Emits signals when data changes, allowing UI components to react.
    """

    changed = Signal(str, object)  # emits (key, new_value)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = {}
        self._watcher = None
        self._file_path = None

    def set(self, key, value):
        """Set a value in the store and emit changed signal."""
        if self._data.get(key) != value:
            self._data[key] = value
            self.changed.emit(key, value)

            # If we are backed by a file, save it (optional, usually handled externally or explicitly)
            if self._file_path:
                self.save_to_file()

    def get(self, key, default=None):
        """Get a value from the store."""
        return self._data.get(key, default)

    def update_bulk(self, data_dict):
        """Update multiple keys at once."""
        for k, v in data_dict.items():
            self.set(k, v)

    def bind_to_file(self, file_path):
        """
        Bind this store to a JSON file.
        It will load data initially and watch for external changes.
        """
        self._file_path = file_path
        self.load_from_file()

        if not self._watcher:
            self._watcher = QFileSystemWatcher(self)
            self._watcher.fileChanged.connect(self._on_file_changed)

        self._watcher.addPath(file_path)

    def load_from_file(self):
        """Load data from the bound JSON file."""
        if not self._file_path or not os.path.exists(self._file_path):
            return

        try:
            with open(self._file_path, "r") as f:
                new_data = json.load(f)
                if isinstance(new_data, dict):
                    self.update_bulk(new_data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"DataStore: Error loading file {self._file_path}: {e}")

    def save_to_file(self):
        """Save current data to the bound JSON file."""
        if not self._file_path:
            return

        try:
            os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
            with open(self._file_path, "w") as f:
                json.dump(self._data, f, indent=4)
        except IOError as e:
            print(f"DataStore: Error saving file {self._file_path}: {e}")

    def _on_file_changed(self, path):
        """Handle external file changes."""
        # Simple debounce/delay to ensure file write is complete
        QTimer.singleShot(100, self.load_from_file)

        # Re-add path because some editors delete/re-create files
        if self._watcher:
            QTimer.singleShot(200, lambda: self._watcher.addPath(path))


# Global singleton or context-based instances can be used
_global_store = None


def get_store():
    global _global_store
    if _global_store is None:
        _global_store = DataStore()
    return _global_store
