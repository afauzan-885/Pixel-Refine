"""
Custom splash screen component with progress indicator.
"""

from PySide6.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QApplication
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from UI.resources.animation.loading.circular_progress import CircularProgress


class SplashScreen(QSplashScreen):
    """
    Custom splash screen that displays an image, circular progress indicator,
    and status label.
    """
    
    def __init__(self, pixmap: QPixmap, version_string: str, flags=Qt.WindowType.WindowStaysOnTopHint):
        """
        Initialize splash screen.
        
        Args:
            pixmap: Image to display on splash screen
            version_string: Version text to display
            flags: Window flags
        """
        super().__init__(pixmap, flags)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 15)
        
        main_layout.addStretch()

        # Custom circular progress widget
        self.progress_indicator = CircularProgress(self)
        self.progress_indicator.setFixedSize(120, 120) 
        main_layout.addWidget(self.progress_indicator, alignment=Qt.AlignmentFlag.AlignCenter)

        # Label for "LOADING..."
        self.status_label = QLabel("L O A D I N G . . .", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: white; 
            font-size: 14px;
            font-weight: normal;
            letter-spacing: 4px;
            background-color: transparent;
            padding-top: 5px;
        """)
        main_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Label for detailed messages
        self.detail_label = QLabel("", self)
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setStyleSheet("color: #DDDDDD; font-size: 11px; background-color: transparent;")
        main_layout.addWidget(self.detail_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Small spacer for version number
        main_layout.addSpacing(10)

        # Label for version number
        self.version_label = QLabel(version_string, self)
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Made smaller and dimmer for elegance
        self.version_label.setStyleSheet("""
            color: #AAAAAA; 
            font-size: 9px; 
            background-color: transparent;
        """)
        main_layout.addWidget(self.version_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def update_status(self, message: str, value: int) -> None:
        """
        Update progress indicator and status message.
        
        Args:
            message: Status message to display
            value: Progress value (0-100)
        """
        self.progress_indicator.setValue(value)
        self.detail_label.setText(message) 
        QApplication.processEvents()
