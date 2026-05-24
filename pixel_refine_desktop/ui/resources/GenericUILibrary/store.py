from PySide6.QtCore import QObject, Signal, QFileSystemWatcher, QTimer
import json
import os


class DataStore(QObject):
    """
    Centralized data store for GenericUILibrary.
    Emits signals when data changes, allowing UI components to react.
    """

    changed = Signal(
        object, object
    )  # emits (key, new_value). key can be None for bulk updates.

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = {}
        self._watcher = None
        self._file_path = None
        self._in_transaction = False
        self._pending_notifications = set()  # Track keys changed during transaction

    def set(self, key, value, notify=True):
        """
        Set a value in the store and emit changed signal.
        Supports nested keys using dot notation.
        """
        keys = key.split(".")
        target = self._data

        # Traverse for nested keys
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]

        last_key = keys[-1]
        if target.get(last_key) != value:
            target[last_key] = value

            if notify:
                if self._in_transaction:
                    self._pending_notifications.add(key)
                else:
                    self.changed.emit(key, value)

            # If we are backed by a file, save it (unless in transaction)
            if self._file_path and not self._in_transaction:
                self.save_to_file()

    def silent_set(self, key, value):
        """Set value without emitting signals or saving to file."""
        self.set(key, value, notify=False)

    def get(self, key, default=None):
        """
        Get a value from the store.
        Supports nested keys using dot notation.
        """
        if key is None:
            return self._data

        if not isinstance(key, str):
            return (
                self._data.get(key, default)
                if isinstance(self._data, dict)
                else default
            )

        keys = key.split(".")
        current = self._data
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current

    def update_bulk(self, data_dict, deep=True, save=True):
        """
        Update multiple keys at once.
        Supports dotted keys (e.g., {"625.algo": "X"}) by expanding them into nested dicts.
        If deep=True, merges dictionaries instead of replacing.
        """
        processed_data = {}
        for key, value in data_dict.items():
            if "." in key:
                # Expand "a.b.c" into {"a": {"b": {"c": value}}}
                keys = key.split(".")
                curr = processed_data
                for k in keys[:-1]:
                    if k not in curr or not isinstance(curr[k], dict):
                        curr[k] = {}
                    curr = curr[k]
                curr[keys[-1]] = value
            else:
                processed_data[key] = value

        if not deep:
            self._data.update(processed_data)
        else:
            self._deep_merge(self._data, processed_data)

        if self._in_transaction:
            self._pending_notifications.add(None)  # Mark for global refresh
        else:
            self.changed.emit(None, self._data)  # Notify all listeners of major change
            if save and self._file_path:
                self.save_to_file()

    def transaction(self):
        """Context manager for batching multiple updates into a single notification."""

        class Transaction:
            def __init__(self, store):
                self.store = store

            def __enter__(self):
                self.store._in_transaction = True
                return self.store

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.store._in_transaction = False
                # If there was an error, we might still have pending changes
                if exc_type is None:
                    # Notify for all changed keys
                    for key in self.store._pending_notifications:
                        val = self.store.get(key) if key else self.store._data
                        self.store.changed.emit(key, val)

                    if self.store._file_path and self.store._pending_notifications:
                        self.store.save_to_file()

                self.store._pending_notifications.clear()

        return Transaction(self)

    def _deep_merge(self, base, source):
        """Internal helper for recursive dict merging."""
        for k, v in source.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._deep_merge(base[k], v)
            else:
                base[k] = v

    def bind_to_file(self, file_path):
        """
        Bind this store to a JSON file.
        It will load data initially and watch for external changes.
        """
        self._file_path = os.path.abspath(file_path)
        self.load_from_file()

        if not self._watcher:
            self._watcher = QFileSystemWatcher(self)
            self._watcher.fileChanged.connect(self._on_file_changed)
            # Also watch directory for atomic saves/deletions
            self._watcher.directoryChanged.connect(self._on_file_changed)

        # Watch both the file and its parent directory
        self._watcher.addPath(self._file_path)
        parent_dir = os.path.dirname(self._file_path)
        if os.path.exists(parent_dir):
            self._watcher.addPath(parent_dir)

    def load_from_file(self):
        """Load data from the bound JSON file. Replaces current data."""
        if not self._file_path or not os.path.exists(self._file_path):
            return

        try:
            with open(self._file_path, "r") as f:
                new_data = json.load(f)
                if isinstance(new_data, dict):
                    # Direct assignment to reflect EXACT state from file (including deletions)
                    self._data = new_data
                    self.changed.emit(None, self._data)
                    print(
                        f"[OK] DataStore: Sync success from {os.path.basename(self._file_path)}"
                    )
        except (json.JSONDecodeError, IOError) as e:
            print(f"[ERROR] DataStore: Error loading file {self._file_path}: {e}")

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
        """Handle external file changes with robust path re-registration."""
        # Use absolute target file path
        target = self._file_path
        if not target:
            return

        # If file is temporarily missing (atomic save), retry
        if not os.path.exists(target):
            # Wait a bit for editor to finish rename/re-create
            QTimer.singleShot(100, lambda: self._on_file_changed(target))
            return

        # Load data (this emits changed signal)
        self.load_from_file()

        # Re-add file to watcher if it was dropped
        if self._watcher:
            # Re-ensure we are watching the file
            if target not in self._watcher.files():
                self._watcher.addPath(target)
                print(
                    f"[WATCH] DataStore: Re-attached watcher to {os.path.basename(target)}"
                )


# Global singleton or context-based instances can be used
_global_store = None


def get_store():
    global _global_store
    if _global_store is None:
        _global_store = DataStore()
    return _global_store
