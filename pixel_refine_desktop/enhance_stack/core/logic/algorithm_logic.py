"""
Algorithm Logic - Core business logic untuk AlgorithmPanel.
Handles: Algorithm selection, settings management, processing.
Separated dari UI untuk better maintainability dan testability.
"""

from typing import Dict, List, Optional
import config

# Backend logic helper
from pixel_refine_desktop.enhance_stack.models.algorithm_list import (
    get_algorithm_names,
)


class AlgorithmLogic:
    """
    Core logic untuk algorithm management dan settings.

    Responsibilities:
    - Manage algorithm selections
    - Handle settings get/set
    - Validate algorithm choices
    - Provide algorithm info
    """

    def __init__(self):
        """Initialize algorithm logic."""
        self.settings: Dict[str, Optional[str]] = {
            config.KEY_ALIGNMENT: None,
            config.KEY_SUPER_RESOLUTION: None,
            config.KEY_DENOISING: None,
            config.KEY_CHECKBOX_ALIGN: False,
            config.KEY_CHECKBOX_SUPER_RES: False,
            config.KEY_CHECKBOX_DENOISING: False,
        }
        self.algorithm_names = {
            "alignment": [],
            "super_resolution": [],
            "denoising": [],
        }
        self.processing_state = {
            "progress": 0,
        }
        self._load_algorithm_names()

    def _load_algorithm_names(self):
        """Load available algorithm names dari backend."""
        try:
            self.algorithm_names["alignment"] = get_algorithm_names("alignment")
            self.algorithm_names["super_resolution"] = get_algorithm_names(
                "super_resolution"
            )
            self.algorithm_names["denoising"] = get_algorithm_names("denoising")
        except Exception as e:
            print(f"Error loading algorithm names: {e}")

    def get_algorithm_names(self, category: str) -> List[str]:
        """
        Get available algorithm names untuk kategori.

        Args:
            category: 'alignment', 'super_resolution', atau 'denoising'

        Returns:
            list: List of algorithm names
        """
        return self.algorithm_names.get(category, [])

    def get_settings(self) -> Dict[str, Optional[str]]:
        """
        Get current algorithm settings.

        Returns:
            dict: {'alignment': str, 'super_resolution': str, 'denoising': str}
        """
        return self.settings.copy()

    def set_settings(self, settings: Dict[str, Optional[str]]) -> bool:
        """
        Set algorithm settings.

        Args:
            settings: dict dengan format:
                {'alignment': str, 'super_resolution': str, 'denoising': str}

        Returns:
            bool: True jika berhasil, False jika ada error
        """
        try:
            for key, value in settings.items():
                if key in self.settings:
                    if key in (
                        config.KEY_CHECKBOX_ALIGN,
                        config.KEY_CHECKBOX_SUPER_RES,
                        config.KEY_CHECKBOX_DENOISING,
                    ):
                        self.settings[key] = bool(value)
                        continue
                    # Robust check: allow None or "None" variants
                    if value is None or str(value).strip().lower() in ["none", ""]:
                        self.settings[key] = None  # Normalize to None
                    elif self._is_valid_algorithm(key, value):
                        self.settings[key] = value
                    else:
                        # If it starts with "No ", it's likely a valid 'None' variant from UI
                        if str(value).startswith("No "):
                            self.settings[key] = value
                        else:
                            print(f"Invalid algorithm: {key}={value}")
                            # Don't fail the whole set, just skip or set to None
                            self.settings[key] = None
            return True
        except Exception as e:
            print(f"Error setting algorithm settings: {e}")
            return False

    def _is_valid_algorithm(self, category: str, algorithm_name: Optional[str]) -> bool:
        """
        Validate if algorithm is valid untuk kategori.
        """
        if algorithm_name is None:
            return True

        str_val = str(algorithm_name).strip()
        if not str_val or str_val.lower() == "none" or str_val.startswith("No "):
            return True

        available = self.algorithm_names.get(category, [])
        return str_val in available or len(available) == 0  # Allow if list empty

    def stop_processing(self):
        """Mark processing as stopped."""
        self.processing_state["progress"] = 0

    def set_progress(self, value: int) -> bool:
        """
        Set progress value.

        Args:
            value: Progress value (0-100)

        Returns:
            bool: True jika valid
        """
        if 0 <= value <= 100:
            self.processing_state["progress"] = value
            return True
        return False
