from PySide6.QtCore import Slot


class RealtimeMixin:
    """
    Mixin class to provide real-time data binding capabilities to UI components.

    Usage:
        class MyComponent(QWidget, RealtimeMixin):
            def __init__(self):
                super().__init__()
                self.bind_store(my_store, "user_config")

            def on_store_changed(self, key, value):
                # Update UI based on data
                pass
    """

    def bind_store(self, store, key=None):
        """
        Bind this component to a DataStore.
        If key is provided, on_store_changed will only trigger for that key or if it's None.
        """
        self._store = store
        self._store_key = key
        self._store.changed.connect(self._handle_store_change)

        # Initial sync
        if key:
            initial_val = self._store.get(key)
            if initial_val is not None:
                self.on_store_changed(key, initial_val)

    @Slot(str, object)
    def _handle_store_change(self, key, value):
        if self._store_key is None or self._store_key == key:
            self.on_store_changed(key, value)

    def on_store_changed(self, key, value):
        """
        Override this method in the inheriting class to handle UI updates.
        """
        pass

    def get_data(self, key=None):
        """Helper to get data from bound store."""
        if hasattr(self, "_store"):
            return self._store.get(key or self._store_key)
        return None

    def set_data(self, value, key=None):
        """Helper to set data in bound store."""
        if hasattr(self, "_store"):
            self._store.set(key or self._store_key, value)
