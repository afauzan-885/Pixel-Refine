"""Utility to check the device backend arch from app_setting.json.

Reads directly from the JSON file to avoid circular imports with the UI layer.
Falls back to reading the general_store if the JSON is unavailable.
"""

import os
import json


def _get_app_setting_path() -> str:
    """Return the path to app_setting.json."""
    # Try to use the config module if importable
    try:
        from config import GENERAL_SETTINGS_FILE  # type: ignore
        return GENERAL_SETTINGS_FILE
    except ImportError:
        pass

    # Fallback: search relative to this file (3 levels up to project root)
    here = os.path.dirname(os.path.abspath(__file__))
    root = here
    for _ in range(8):
        candidate = os.path.join(root, "database", "setting", "app_setting.json")
        if os.path.exists(candidate):
            return candidate
        root = os.path.dirname(root)
    return ""


def is_cpu_backend() -> bool:
    """Return True when device_backend_arch is 'cpu'."""
    path = _get_app_setting_path()
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            arch = str(data.get("device_backend_arch", "vulkan")).lower()
            return arch == "cpu"
        except Exception:
            pass

    # Fallback to general_store (may cause circular import in some contexts,
    # wrapped in try/except so it degrades gracefully)
    try:
        from pixel_refine_desktop.ui.views.settings.General.general_store import (
            get_general_store,
        )

        store = get_general_store()
        arch = store.get("device_backend_arch") or "vulkan"
        return str(arch).lower() == "cpu"
    except Exception:
        pass

    return False
