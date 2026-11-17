from PySide6.QtCore import Slot

_MISS = object()


class RealtimeMixin:
    """Store binding for widgets and panels, exposed through three APIs.

    The surface follows the same shape as ``Button(text, variant=..., ...)`` and
    ``taichi.buffer_session.BufferSession``: a few verbs, with advanced needs
    expressed as explicit keyword arguments instead of extra methods.

    ``bind``   attach a store, declare bindings, optionally apply them.
    ``sync``   pull, switch context, write, or peek — depending on the keywords.
    ``on_sync`` reactive hook invoked after bindings were applied.

    Single-key widgets bind with ``key=``; panels that follow a selected entity
    bind with ``scope=`` plus a ``bindings`` mapping. Without either, the
    component reacts to global invalidation (broadcast mode).
    """

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------
    def bind(
        self,
        store,
        *,
        key=None,
        scope=None,
        bindings=None,
        fallback=None,
        apply=True,
        follow=True,
    ):
        """Attach ``store`` and declare bindings for one key or one scope.

        Args:
            store: DataStore-like object exposing ``get``/``set``/``changed``.
            key: Single-key mode (e.g. ``"language"``). Exclusive with ``scope``.
            scope: Scoped mode (e.g. a batch id). Exclusive with ``key``.
            bindings: Scoped bindings; ``{rel_key: widget | (widget, prop) |
                (widget, prop, fallback)}``. Requires ``scope``.
            fallback: Default fallback for bindings that omit their own.
            apply: Apply the current store values immediately.
            follow: Subscribe to ``store.changed`` for automatic updates.
        """

        self._ensure_state()
        if store is None:
            raise ValueError("bind(store=...) requires a store instance")
        if key is not None and scope is not None:
            raise ValueError("bind() accepts key= or scope=, not both")
        if bindings is not None and key is not None:
            raise ValueError("bind(bindings=...) cannot be combined with key=")
        if bindings is not None and scope is not None and not str(scope):
            raise ValueError("bind(bindings=...) requires a non-empty scope=")

        follow = bool(follow)
        if self._store is not store or self._follow != follow:
            self._detach()
            self._store = store
            self._follow = follow
            if follow:
                store.changed.connect(self._handle_store_change)

        self._store_key = key
        if scope is not None:
            self._scope_prefix = self._normalize_scope(scope)
        elif key is not None:
            self._scope_prefix = ""
        if fallback is not None:
            self._default_fallback = fallback
        if bindings:
            self._register_bindings(bindings, fallback)

        if apply:
            self.sync()

    def sync(
        self,
        *,
        scope=None,
        key=None,
        keys=None,
        values=None,
        notify=True,
        persist=False,
        peek=False,
    ):
        """Synchronize widgets with the store, in either direction.

        Args:
            scope: Switch scope and apply it.
            key: Switch to single-key mode and apply that key.
            keys: Restrict pulling to these relative keys.
            values: Write ``{rel_key: value}`` to the store, then apply.
                ``None`` values are skipped.
            notify: With ``values``, ``False`` writes without emitting
                ``store.changed`` (replaces a temporary signal blocker).
            persist: With ``values``, save the store to disk synchronously.
            peek: Return the current payload without touching any widget.

        Returns:
            Mapping for the active scope, a scalar in single-key mode, or
            ``None`` when the component has no payload (broadcast mode).
        """

        self._ensure_state()
        if scope is not None and key is not None:
            raise ValueError("sync() accepts scope= or key=, not both")
        if values is not None and peek:
            raise ValueError("sync() cannot combine values=... with peek=True")
        if values is not None and keys is not None:
            raise ValueError("sync() cannot combine values=... with keys=...")
        if not notify and values is None:
            raise ValueError("sync(notify=False) only applies with values=...")
        if persist and values is None:
            raise ValueError("sync(persist=True) only applies with values=...")

        if scope is not None:
            self._scope_prefix = self._normalize_scope(scope)
            self._store_key = None
        if key is not None:
            self._store_key = key
            self._scope_prefix = ""

        if values is not None:
            written = self._write(values, notify=bool(notify), persist=bool(persist))
            self._apply(None)
            self.on_sync(self._sync_payload(), key=None, origin="self")
            return written

        if peek:
            return self._snapshot(keys)
        self._apply(keys)
        result = self._snapshot(keys)
        self.on_sync(self._sync_payload(keys), key=None, origin="store")
        return result

    def on_sync(self, payload, *, key=None, origin=None):
        """React after ``sync`` applied bindings.

        Args:
            payload: Shallow mapping of the active scope, ``{bound_key: value}``
                in single-key mode, or ``None`` for global invalidation.
            key: Relative key that triggered this call, or ``None`` for a
                scope-wide/bulk update.
            origin: ``"store"`` or ``"self"`` (the component's own write).
        """

    # ------------------------------------------------------------------
    # EVENT NORMALIZATION
    # ------------------------------------------------------------------
    @Slot(object, object)
    def _handle_store_change(self, key, value):
        if not self._follow or self._is_syncing:
            return

        relative = self._match_event(key)
        if relative is _MISS:
            return

        replaced = (
            relative is None
            and self._store_key is None
            and isinstance(key, str)
            and isinstance(value, dict)
            and key == self._scope_prefix.rstrip(".")
        )
        if replaced:
            # The whole scope object was replaced by this event payload.
            self._apply_values(value)
            payload = dict(value)
        else:
            self._apply([relative] if relative else None)
            payload = self._event_payload(key, value)
        self.on_sync(payload, key=relative, origin="store")

    def _match_event(self, key):
        """Return the relative key, ``None`` (bulk), or ``_MISS`` (unrelated)."""
        if key is None:
            return None
        if not isinstance(key, str):
            return _MISS
        if self._store_key is not None:
            if key == self._store_key or key.startswith(f"{self._store_key}."):
                return key
            return _MISS
        prefix = self._scope_prefix
        if not prefix:
            # Broadcast mode: every keyed change is relevant.
            return key
        if key == prefix.rstrip("."):
            return None
        if key.startswith(prefix):
            return key[len(prefix):]
        return _MISS

    def _event_payload(self, key, value):
        if self._store_key is not None:
            return {self._store_key: self._bound_value(self._store_key)}
        if not self._scope_prefix:
            return {key: value} if isinstance(key, str) else None
        payload = self._snapshot()
        return payload if payload is not None else {}

    def _sync_payload(self, keys=None):
        """Mapping handed to ``on_sync`` for a manual sync (never a live store dict)."""
        if self._store_key is not None:
            return {self._store_key: self._bound_value(self._store_key)}
        if keys is not None:
            return {rel_key: self._bound_value(rel_key) for rel_key in keys}
        payload = self._snapshot()
        return payload if payload is not None else {}

    # ------------------------------------------------------------------
    # INTERNALS
    # ------------------------------------------------------------------
    def _ensure_state(self):
        if not hasattr(self, "_bindings"):
            self._bindings = {}
        if not hasattr(self, "_fallbacks"):
            self._fallbacks = {}
        if not hasattr(self, "_scope_prefix"):
            self._scope_prefix = ""
        if not hasattr(self, "_store_key"):
            self._store_key = None
        if not hasattr(self, "_store"):
            self._store = None
        if not hasattr(self, "_is_syncing"):
            self._is_syncing = False
        if not hasattr(self, "_follow"):
            self._follow = False
        if not hasattr(self, "_default_fallback"):
            self._default_fallback = None
        if not hasattr(self, "_applying"):
            self._applying = False

    @staticmethod
    def _normalize_scope(scope):
        text = str(scope or "")
        if text and not text.endswith("."):
            text = f"{text}."
        return text

    def _detach(self):
        store = getattr(self, "_store", None)
        if store is None:
            return
        try:
            store.changed.disconnect(self._handle_store_change)
        except (RuntimeError, TypeError, AttributeError):
            pass

    def _register_bindings(self, bindings, default_fallback):
        if not isinstance(bindings, dict):
            raise TypeError(
                "bind(bindings=...) expects a mapping of "
                "{key: widget | (widget, prop) | (widget, prop, fallback)}"
            )
        for rel_key, spec in bindings.items():
            if isinstance(spec, (tuple, list)):
                if len(spec) == 2:
                    widget, prop = spec
                    key_fallback = default_fallback
                elif len(spec) == 3:
                    widget, prop, key_fallback = spec
                else:
                    raise TypeError(
                        f"bind(bindings['{rel_key}']): expected widget or a "
                        "2-3 item tuple (widget, prop[, fallback])"
                    )
            else:
                widget, prop = spec, "value"
                key_fallback = default_fallback
            self._bindings.setdefault(str(rel_key), []).append((widget, prop))
            self._fallbacks[str(rel_key)] = key_fallback

    def _apply(self, keys):
        if self._applying:
            return
        target_keys = list(keys) if keys is not None else list(self._bindings)
        if not target_keys:
            return
        self._applying = True
        previous = self._is_syncing
        self._is_syncing = True
        try:
            for rel_key in target_keys:
                self._apply_binding(rel_key, self._bound_value(rel_key))
        finally:
            self._is_syncing = previous
            self._applying = False

    def _apply_values(self, values):
        """Apply bindings from an explicit payload (scope object replaced)."""
        if self._applying:
            return
        self._applying = True
        previous = self._is_syncing
        self._is_syncing = True
        try:
            for rel_key in list(self._bindings):
                self._apply_binding(
                    rel_key, self._value_or_fallback(rel_key, values.get(rel_key))
                )
        finally:
            self._is_syncing = previous
            self._applying = False

    def _bound_value(self, rel_key):
        store = getattr(self, "_store", None)
        value = None
        if store is not None:
            try:
                value = store.get(f"{self._scope_prefix}{rel_key}")
            except (AttributeError, TypeError):
                value = None
        return self._value_or_fallback(rel_key, value)

    def _value_or_fallback(self, rel_key, value):
        if value is not None:
            return value
        if rel_key in self._fallbacks:
            return self._fallbacks.get(rel_key)
        return self._default_fallback

    def _snapshot(self, keys=None):
        store = getattr(self, "_store", None)
        if store is None:
            return None
        if keys is not None:
            return {
                rel_key: store.get(f"{self._scope_prefix}{rel_key}")
                for rel_key in keys
            }
        if self._store_key is not None:
            return store.get(self._store_key)
        scope_key = self._scope_prefix.rstrip(".")
        if not scope_key:
            return None
        value = store.get(scope_key)
        return dict(value) if isinstance(value, dict) else value

    def _write(self, values, notify, persist):
        if not isinstance(values, dict):
            raise TypeError("sync(values=...) expects a mapping of {key: value}")
        updates = {}
        for rel_key, value in values.items():
            if value is None:
                continue
            updates[f"{self._scope_prefix}{rel_key}"] = value
        if not updates:
            return {}
        self._is_syncing = True
        try:
            if notify:
                self._store.update_bulk(updates, save=False)
            else:
                for full_key, value in updates.items():
                    self._store.silent_set(full_key, value)
        finally:
            self._is_syncing = False
        if persist:
            save = getattr(self._store, "save_to_file", None)
            if callable(save):
                save()
        return {key: value for key, value in values.items() if value is not None}

    def _apply_binding(self, rel_key, value):
        for widget, prop in list(self._bindings.get(rel_key, ())):
            self._apply_binding_value(widget, prop, value)

    def _apply_binding_value(self, widget, property_name, value):
        """Call the widget setter, isolating one broken widget from the rest."""
        setter_name = f"set_{property_name}"
        try:
            if hasattr(widget, setter_name):
                widget.blockSignals(True)
                try:
                    getattr(widget, setter_name)(value)
                finally:
                    widget.blockSignals(False)
            elif hasattr(widget, property_name):
                setattr(widget, property_name, value)
        except (RuntimeError, TypeError, ValueError) as error:
            print(
                f"[SyncMixin] Could not apply '{property_name}' to "
                f"{type(widget).__name__}: {error}"
            )


class SyncMixin(RealtimeMixin):
    """Scoped declarative bindings for panels that follow a selected entity.

    These three APIs are inherited unchanged from ``RealtimeMixin``; the class
    stays separate so panel code reads as "this component follows a scope"
    while a plain widget uses single-key mode.
    """


class AdaptiveSizingMixin:
    """
    A reusable mixin for PySide widgets to enable general adaptive layout features:
    - Dynamic font size calculation based on widget width
    - Word wrapping for target labels
    - Size policy constraints based on allowed expansion directions (e.g., bottom, right)
    """
    def init_adaptive_sizing(self, allowed_directions=None):
        """
        Initializes the size policy based on allowed expansion directions.
        allowed_directions: list of strings (e.g., ['bottom', 'right'])
        """
        from PySide6.QtWidgets import QSizePolicy
        
        self._allowed_directions = allowed_directions if allowed_directions is not None else ["bottom"]
        
        h_policy = (
            QSizePolicy.Policy.Expanding
            if "right" in self._allowed_directions
            else QSizePolicy.Policy.Preferred
        )
        v_policy = (
            QSizePolicy.Policy.Expanding
            if "bottom" in self._allowed_directions
            else QSizePolicy.Policy.Preferred
        )
        if hasattr(self, "setSizePolicy"):
            self.setSizePolicy(h_policy, v_policy)

    def calculate_adaptive_font_size(self, current_width, ranges=None):
        """
        Helper method to map the current widget width to font sizes.
        ranges: list of tuples (width_threshold, font_size) ordered by width ascending.
        Returns the appropriate font size.
        """
        if ranges is None:
            # Default scaling ranges matching FeatureCard
            ranges = [
                (180, 8.5),
                (230, 9.5),
                (99999, 11)
            ]
        for threshold, size in ranges:
            if current_width < threshold:
                return size
        return ranges[-1][1]

    def apply_word_wrap(self, *labels):
        """
        Ensures word wrapping is enabled on the target QLabels.
        """
        for label in labels:
            if hasattr(label, "setWordWrap"):
                label.setWordWrap(True)
                label.setMinimumWidth(0)
