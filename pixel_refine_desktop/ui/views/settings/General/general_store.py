import os
from resources.GenericUILibrary import get_store, DataStore
from config import GENERAL_SETTINGS_FILE

DEFAULTS = {
    "language": "English",
    "theme": "Light Theme",
    "gpu_acceleration": False,
    "multi_core_cpu": True,
    "create_thumbnail": False,
    "device_backend": "CPU (Universal)",
}

_general_store = None


def get_general_store():
    """
    Returns a DataStore instance initialized with general settings.
    Binds it to the file path defined in config.
    """
    global _general_store
    if _general_store is None:
        _general_store = DataStore()

        # Ensure file exists or will be created with defaults
        if not os.path.exists(GENERAL_SETTINGS_FILE):
            os.makedirs(os.path.dirname(GENERAL_SETTINGS_FILE), exist_ok=True)
            _general_store.update_bulk(DEFAULTS, save=True)

        # Bind to file to enable auto-sync and persistence
        _general_store.bind_to_file(GENERAL_SETTINGS_FILE)

        # Fill missing keys with defaults if any
        current_data = _general_store.get(None)
        if isinstance(current_data, dict):
            missing = {k: v for k, v in DEFAULTS.items() if k not in current_data}
            if missing:
                _general_store.update_bulk(missing, save=True)

    return _general_store
