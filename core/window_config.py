"""
Window configuration module for adaptive window sizing and positioning.
"""

from PySide6.QtWidgets import QApplication, QMainWindow


class WindowConfig:
    """
    Handles window size calculation and configuration.
    Provides adaptive window sizing based on screen dimensions.
    """
    
    def __init__(self, 
                 app_aspect_ratio: float = 2.0,
                 min_screen_ratio: float = 0.76,
                 abs_min_width: int = 800,
                 abs_min_height: int = 400):
        """
        Initialize window configuration.
        
        Args:
            app_aspect_ratio: Desired aspect ratio for the application (width / height)
            min_screen_ratio: Percentage of screen that will be the minimum size
            abs_min_width: Absolute minimum width (fallback for very low resolution screens)
            abs_min_height: Absolute minimum height (fallback for very low resolution screens)
        """
        self.app_aspect_ratio = app_aspect_ratio
        self.min_screen_ratio = min_screen_ratio
        self.abs_min_width = abs_min_width
        self.abs_min_height = abs_min_height
        
        self.final_min_width = 0
        self.final_min_height = 0
        self.center_x = 0
        self.center_y = 0
        
    def calculate_adaptive_size(self) -> tuple[int, int, int, int]:
        """
        Calculate adaptive window size based on screen dimensions.
        
        Returns:
            Tuple of (min_width, min_height, center_x, center_y)
        """
        # Get available screen geometry
        screen_geom = QApplication.primaryScreen().availableGeometry()
        
        # Determine minimum safe area on screen
        min_safe_width = int(screen_geom.width() * self.min_screen_ratio)
        min_safe_height = int(screen_geom.height() * self.min_screen_ratio)
        
        # Calculate aspect ratio of minimum area on screen
        screen_aspect_ratio = min_safe_width / min_safe_height
        
        # "Fit Inside a Box" logic to determine adaptive minimum size
        if screen_aspect_ratio > self.app_aspect_ratio:
            # Screen is WIDER than app -> Height is the constraint
            adaptive_min_height = min_safe_height
            adaptive_min_width = int(adaptive_min_height * self.app_aspect_ratio)
        else:
            # Screen is TALLER (or equal) than app -> Width is the constraint
            adaptive_min_width = min_safe_width
            adaptive_min_height = int(adaptive_min_width / self.app_aspect_ratio)
        
        # Determine final minimum size: take the larger between
        # adaptive result and absolute limits
        self.final_min_width = max(self.abs_min_width, adaptive_min_width)
        self.final_min_height = max(self.abs_min_height, adaptive_min_height)
        
        # Calculate center position
        self.center_x = int(screen_geom.x() + (screen_geom.width() - self.final_min_width) / 2)
        self.center_y = int(screen_geom.y() + (screen_geom.height() - self.final_min_height) / 2)
        
        return self.final_min_width, self.final_min_height, self.center_x, self.center_y
    
    def apply_to_window(self, window: QMainWindow) -> None:
        """
        Apply calculated configuration to a QMainWindow.
        
        Args:
            window: The QMainWindow to configure
        """
        # Calculate if not already done
        if self.final_min_width == 0:
            self.calculate_adaptive_size()
        
        # Set minimum size
        window.setMinimumSize(self.final_min_width, self.final_min_height)
        
        # Set initial size same as minimum
        window.resize(self.final_min_width, self.final_min_height)
        
        # Center window on screen
        window.move(self.center_x, self.center_y)
