from PySide6.QtCore import Slot


class RealtimeMixin:
    """
    Mixin class to provide real-time data binding capabilities to UI components.
    """

    def bind_store(self, store, key=None):
        self._store = store
        self._store_key = key
        self._is_syncing = False  # Loop prevention flag
        self._store.changed.connect(self._handle_store_change)

        # Initial sync
        if key:
            initial_val = self._store.get(key)
            if initial_val is not None:
                self.on_store_changed(key, initial_val)

    @Slot(object, object)
    def _handle_store_change(self, key, value):
        if self._is_syncing:
            return

        # key is None means a bulk update (e.g., from file load)
        if key is None:
            if self._store_key:
                # Targeted update: extract our specific value from the new data
                val = self._store.get(self._store_key)
                self.on_store_changed(self._store_key, val)
            else:
                # Global update: notify component of the whole data change
                self.on_store_changed(None, value)
            return

        # Specific key check
        if (
            self._store_key is None
            or self._store_key == key
            or (isinstance(key, str) and key.startswith(f"{self._store_key}."))
        ):
            self.on_store_changed(key, value)

    def on_store_changed(self, key, value):
        pass

    def get_data(self, key=None):
        if hasattr(self, "_store"):
            return self._store.get(key or self._store_key)
        return None

    def set_data(self, value, key=None, notify=True):
        if hasattr(self, "_store"):
            self._is_syncing = True
            try:
                self._store.set(key or self._store_key, value, notify=notify)
            finally:
                self._is_syncing = False

    def signal_blocker(self):
        """Context manager to block store signals temporarily."""

        class Blocker:
            def __init__(self, mixin):
                self.mixin = mixin

            def __enter__(self):
                self.mixin._is_syncing = True

            def __exit__(self, *args):
                self.mixin._is_syncing = False

        return Blocker(self)


class SyncMixin(RealtimeMixin):
    """
    Advanced mixin for declarative data binding.
    Allows linking Store keys directly to widget properties.
    """

    def bind_store(self, store, key=None):
        """Override to initialize bindings dictionary."""
        super().bind_store(store, key)
        if not hasattr(self, "_bindings"):
            self._bindings = {}
        if not hasattr(self, "_scope_prefix"):
            self._scope_prefix = ""

    def set_scope(self, prefix):
        """Set a prefix for all subsequent bindings (e.g., 'batch.625')."""
        self._scope_prefix = (
            prefix if prefix.endswith(".") or not prefix else f"{prefix}."
        )

    def add_binding(self, key, widget, property_name="value", fallback=None):
        """
        Bind a relative store key to a widget property with optional fallback.
        Example: add_binding("alignment_algo", self.align_form, fallback="No Alignment")
        """
        if not hasattr(self, "_bindings"):
            self._bindings = {}
        if not hasattr(self, "_fallbacks"):
            self._fallbacks = {}
        if not hasattr(self, "_scope_prefix"):
            self._scope_prefix = ""

        if key not in self._bindings:
            self._bindings[key] = []
        self._bindings[key].append((widget, property_name))

        # Store fallback for this key
        self._fallbacks[key] = fallback

        # Initial sync
        if hasattr(self, "_store"):
            full_key = f"{self._scope_prefix}{key}"
            val = self._store.get(full_key)
            # Use fallback if value is None
            val_to_apply = val if val is not None else fallback
            self._apply_binding_value(widget, property_name, val_to_apply)

    def on_store_changed(self, key, value):
        """Handle automatic binding updates with scope resolution and fallbacks."""
        if not hasattr(self, "_bindings"):
            return
        if not hasattr(self, "_scope_prefix"):
            self._scope_prefix = ""
        if not hasattr(self, "_fallbacks"):
            self._fallbacks = {}

        # 1. Handle specific key (string)
        if isinstance(key, str):
            # Case A: External update for exact scope (e.g., '625' changed)
            scope_key = self._scope_prefix.rstrip(".")
            if key == scope_key and isinstance(value, dict):
                for rel_key, b_list in self._bindings.items():
                    # Use value from dict or fallback
                    val = value.get(rel_key, self._fallbacks.get(rel_key))
                    for widget, prop in b_list:
                        self._apply_binding_value(widget, prop, val)
                return

            # Case B: Child key changed (e.g., '625.alignment_algo')
            if key.startswith(self._scope_prefix):
                relative_key = key[len(self._scope_prefix) :]
                if relative_key in self._bindings:
                    # Use fallback if value is None
                    val_to_apply = (
                        value
                        if value is not None
                        else self._fallbacks.get(relative_key)
                    )
                    for widget, prop in self._bindings[relative_key]:
                        self._apply_binding_value(widget, prop, val_to_apply)

        # 2. Handle generic bulk updates (key is None)
        if key is None:
            for rel_key, b_list in self._bindings.items():
                full_key = f"{self._scope_prefix}{rel_key}"
                val = self._store.get(full_key)

                # IMPORTANT: Use fallback if store value is None
                val_to_apply = val if val is not None else self._fallbacks.get(rel_key)

                for widget, prop in b_list:
                    self._apply_binding_value(widget, prop, val_to_apply)

    def _apply_binding_value(self, widget, property_name, value):
        """Helper to call setter on widget (e.g., set_value)."""
        setter_name = f"set_{property_name}"
        if hasattr(widget, setter_name):
            # Block signals to prevent feedback loops if the widget has its own sync
            widget.blockSignals(True)
            try:
                getattr(widget, setter_name)(value)
            finally:
                widget.blockSignals(False)
        elif hasattr(widget, property_name):
            # Fallback for direct attribute access (non-Qt property style)
            setattr(widget, property_name, value)
