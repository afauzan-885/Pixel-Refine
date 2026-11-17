"""Central policy for thumbnail creation and display.

The thumbnail setting is an application-wide feature flag. Consumers should
use this policy instead of reading ``app_setting.json`` or starting a
``ThumbnailLoader`` based on local assumptions.
"""

import threading

from PySide6.QtCore import QObject, Signal

_suspension_lock = threading.Lock()
_suspension_reasons = set()


def set_thumbnail_generation_suspended(suspended, reason="default"):
    """Hold new thumbnail work while a reason owns the backend.

    Reasons are independent: releasing ``preview`` must not resume thumbnails
    while ``compute`` is still running. Returns True only when this call
    releases the last active reason, so the UI can restart lazy loading once.
    """

    key = str(reason)
    with _suspension_lock:
        was_suspended = bool(_suspension_reasons)
        if suspended:
            _suspension_reasons.add(key)
        else:
            _suspension_reasons.discard(key)
        now_suspended = bool(_suspension_reasons)
        return was_suspended and not now_suspended


def thumbnail_generation_suspended(exclude_reason=None):
    """Whether thumbnail creation must wait for any active owner."""

    with _suspension_lock:
        if exclude_reason is None:
            return bool(_suspension_reasons)
        return bool(_suspension_reasons - {str(exclude_reason)})


class ThumbnailPolicy(QObject):
    """Single source of truth for the application's thumbnail feature flag."""

    changed = Signal(bool)

    def __init__(self, parent=None, store=None):
        super().__init__(parent)

        if store is None:
            # Keep this import lazy so low-level image services do not create
            # an import cycle with the settings UI.
            from pixel_refine_desktop.ui.views.settings.General.general_store import (
                get_general_store,
            )

            store = get_general_store()

        self._store = store
        self._enabled = self._read_enabled()
        self._store.changed.connect(self._on_store_changed)

    @property
    def enabled(self):
        """Whether thumbnail generation and display are currently allowed."""

        return self._enabled

    def is_enabled(self):
        """Method form for call sites that prefer an explicit predicate."""

        return self.enabled

    def _read_enabled(self):
        try:
            return bool(self._store.get("create_thumbnail", False))
        except Exception:
            return False

    def _on_store_changed(self, key, _value):
        if key not in (None, "create_thumbnail"):
            return

        enabled = self._read_enabled()
        if enabled == self._enabled:
            return

        self._enabled = enabled
        self.changed.emit(enabled)


def thumbnail_creation_enabled(policy=None):
    """Return the current policy value for non-widget service code."""

    if policy is not None:
        return bool(policy.enabled)

    from pixel_refine_desktop.ui.views.settings.General.general_store import (
        get_general_store,
    )

    try:
        return bool(get_general_store().get("create_thumbnail", False))
    except Exception:
        return False
