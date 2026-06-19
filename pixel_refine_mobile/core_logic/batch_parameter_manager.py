"""
pixel_refine_mobile/core_logic/batch_parameter_manager.py
---------------------------------------------------------
Manages per-batch algorithm parameter settings.
Direct port from desktop — same JSON persistence format.
"""

import json
import os
from typing import Dict, Any, Optional


class BatchParameterManager:
    """
    Manages algorithm parameter settings per batch.
    Settings are persisted in a JSON file.
    """

    def __init__(self, config_path: str):
        self._config_path = config_path
        self._settings: Dict[int, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        """Load settings from JSON file."""
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r") as f:
                    data = json.load(f)
                    # Convert string keys back to int
                    self._settings = {int(k): v for k, v in data.items()}
            except Exception as e:
                print(f"[BatchParameterManager] Error loading: {e}")
                self._settings = {}

    def _save(self):
        """Save settings to JSON file."""
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, "w") as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            print(f"[BatchParameterManager] Error saving: {e}")

    def get_settings(self, batch_id: int) -> Dict[str, Any]:
        """Get settings for a batch."""
        return self._settings.get(batch_id, {})

    def set_settings(self, batch_id: int, settings: Dict[str, Any]):
        """Set settings for a batch."""
        self._settings[batch_id] = settings
        self._save()

    def get_algorithm(self, batch_id: int, category: str) -> Optional[str]:
        """Get a specific algorithm setting for a batch."""
        settings = self.get_settings(batch_id)
        return settings.get(category)

    def set_algorithm(self, batch_id: int, category: str, algorithm: str):
        """Set a specific algorithm setting for a batch."""
        settings = self.get_settings(batch_id)
        settings[category] = algorithm
        self.set_settings(batch_id, settings)

    def delete_batch_settings(self, batch_id: int):
        """Delete settings for a batch."""
        if batch_id in self._settings:
            del self._settings[batch_id]
            self._save()
