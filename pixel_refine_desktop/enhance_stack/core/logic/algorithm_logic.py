"""
Algorithm Logic - Core business logic untuk AlgorithmPanel.
Handles: Algorithm selection, settings management, processing.
Separated dari UI untuk better maintainability dan testability.
"""

from typing import Dict, List, Optional

# Backend logic helper
from pixel_refine_desktop.enhance_stack.models.algorithm_list import (
    get_algorithm_names,
    get_algorithm_descriptions,
    get_algorithm_options,
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
        self.settings = {
            'alignment': None,
            'super_resolution': None,
            'denoising': None,
        }
        self.algorithm_names = {
            'alignment': [],
            'super_resolution': [],
            'denoising': [],
        }
        self.processing_state = {
            'is_processing': False,
            'progress': 0,
            'current_task': None,
        }
        self._load_algorithm_names()

    def _load_algorithm_names(self):
        """Load available algorithm names dari backend."""
        try:
            self.algorithm_names['alignment'] = get_algorithm_names('alignment')
            self.algorithm_names['super_resolution'] = get_algorithm_names('super_resolution')
            self.algorithm_names['denoising'] = get_algorithm_names('denoising')
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

    def get_algorithm_descriptions(self, category: str) -> Dict[str, str]:
        """
        Get algorithm descriptions untuk kategori.
        
        Args:
            category: 'alignment', 'super_resolution', atau 'denoising'
            
        Returns:
            dict: Mapping of algorithm name -> description
        """
        try:
            descriptions = get_algorithm_descriptions(category)
            return descriptions if descriptions else {}
        except Exception:
            return {}

    def get_settings(self) -> Dict[str, str]:
        """
        Get current algorithm settings.
        
        Returns:
            dict: {'alignment': str, 'super_resolution': str, 'denoising': str}
        """
        return self.settings.copy()

    def set_settings(self, settings: Dict[str, str]) -> bool:
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
                    if self._is_valid_algorithm(key, value):
                        self.settings[key] = value
                    else:
                        print(f"Invalid algorithm: {key}={value}")
                        return False
            return True
        except Exception as e:
            print(f"Error setting algorithm settings: {e}")
            return False

    def set_algorithm(self, category: str, algorithm_name: str) -> bool:
        """
        Set single algorithm.
        
        Args:
            category: 'alignment', 'super_resolution', atau 'denoising'
            algorithm_name: Name of algorithm
            
        Returns:
            bool: True jika berhasil
        """
        if category not in self.settings:
            return False

        if not self._is_valid_algorithm(category, algorithm_name):
            return False

        self.settings[category] = algorithm_name
        return True

    def get_algorithm(self, category: str) -> Optional[str]:
        """
        Get current algorithm untuk kategori.
        
        Args:
            category: 'alignment', 'super_resolution', atau 'denoising'
            
        Returns:
            str: Current algorithm name, atau None
        """
        return self.settings.get(category)

    def _is_valid_algorithm(self, category: str, algorithm_name: str) -> bool:
        """
        Validate if algorithm is valid untuk kategori.
        
        Args:
            category: Algorithm category
            algorithm_name: Algorithm name
            
        Returns:
            bool: True jika valid
        """
        if not algorithm_name:
            return False

        available = self.algorithm_names.get(category, [])
        return algorithm_name in available or len(available) == 0  # Allow if list empty

    def start_processing(self) -> bool:
        """
        Mark processing as started.
        
        Returns:
            bool: True jika berhasil start
        """
        if self.processing_state['is_processing']:
            return False  # Already processing

        self.processing_state['is_processing'] = True
        self.processing_state['progress'] = 0
        return True

    def stop_processing(self):
        """Mark processing as stopped."""
        self.processing_state['is_processing'] = False
        self.processing_state['progress'] = 0
        self.processing_state['current_task'] = None

    def is_processing(self) -> bool:
        """
        Check if currently processing.
        
        Returns:
            bool: True jika sedang processing
        """
        return self.processing_state['is_processing']

    def set_progress(self, value: int) -> bool:
        """
        Set progress value.
        
        Args:
            value: Progress value (0-100)
            
        Returns:
            bool: True jika valid
        """
        if 0 <= value <= 100:
            self.processing_state['progress'] = value
            return True
        return False

    def get_progress(self) -> int:
        """
        Get current progress.
        
        Returns:
            int: Progress value (0-100)
        """
        return self.processing_state['progress']

    def set_current_task(self, task_name: str):
        """
        Set current task yang sedang diproses.
        
        Args:
            task_name: Name of current task
        """
        self.processing_state['current_task'] = task_name

    def get_current_task(self) -> Optional[str]:
        """
        Get current task yang sedang diproses.
        
        Returns:
            str: Task name, atau None
        """
        return self.processing_state['current_task']

    def get_processing_state(self) -> Dict:
        """
        Get complete processing state.
        
        Returns:
            dict: Complete processing state
        """
        return self.processing_state.copy()

    def validate_settings(self) -> tuple[bool, str]:
        """
        Validate if all settings are configured.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        for category, value in self.settings.items():
            if not value:
                return False, f"{category} not selected"

            if not self._is_valid_algorithm(category, value):
                return False, f"{category}: {value} is invalid"

        return True, "All settings valid"

    def reset_settings(self):
        """Reset settings ke default (None)."""
        for key in self.settings:
            self.settings[key] = None

    def get_settings_summary(self) -> str:
        """
        Get human-readable summary dari settings.
        
        Returns:
            str: Settings summary
        """
        items = []
        for key, value in self.settings.items():
            display_key = key.replace('_', ' ').title()
            items.append(f"{display_key}: {value or 'Not Selected'}")

        return "\n".join(items)
