"""
Custom splash screen component with progress indicator.
"""

from PySide6.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QApplication
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from resources.animations.loading.circular_progress import CircularProgress


class SplashScreen(QSplashScreen):
    """
    Custom splash screen that displays an image, circular progress indicator,
    and status label.
    """

    def __init__(
        self,
        pixmap: QPixmap,
        version_string: str,
        flags=Qt.WindowType.WindowStaysOnTopHint,
    ):
        """
        Initialize splash screen.

        Args:
            pixmap: Image to display on splash screen
            version_string: Version text to display
            flags: Window flags
        """
        super().__init__(pixmap, flags)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        # Clip splash window to exact circle matching the logo
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMask(pixmap.mask())

        main_layout = QVBoxLayout(self)
        side = min(pixmap.width(), pixmap.height())
        # Safe horizontal margins so layout uses the wide middle-lower region of circle
        main_layout.setContentsMargins(12, 10, 12, int(side * 0.09))
        main_layout.setSpacing(2)

        main_layout.addStretch()

        # Custom circular progress widget
        self.progress_indicator = CircularProgress(self)
        self.progress_indicator.setFixedSize(110, 110)
        main_layout.addWidget(
            self.progress_indicator, alignment=Qt.AlignmentFlag.AlignCenter
        )

        from pixel_refine_desktop.ui.views.settings.General.Language import (
            language_config,
        )

        # Label for "MEMUAT..." / "LOADING..."
        loading_text = getattr(language_config, "UI_SPLASH_LOADING", "MEMUAT...").upper()
        self.status_label = QLabel(loading_text, self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            """
            color: rgba(255, 255, 255, 0.95); 
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 3px;
            background-color: transparent;
            padding-top: 4px;
            padding-bottom: 2px;
        """
        )
        main_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Label for detailed friendly messages (comfortably spanning the chord width)
        self.detail_label = QLabel("", self)
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setWordWrap(True)
        self.detail_label.setMinimumWidth(int(side * 0.78))
        self.detail_label.setMaximumWidth(int(side * 0.86))
        self.detail_label.setStyleSheet(
            """
            color: #E2E8F0;
            font-size: 11px;
            font-weight: 500;
            background-color: transparent;
            padding: 0px 4px;
        """
        )
        main_layout.addWidget(self.detail_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Small spacer for version number
        main_layout.addSpacing(6)

        # Label for version number
        self.version_label = QLabel(version_string, self)
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Made smaller and dimmer for elegance
        self.version_label.setStyleSheet(
            """
            color: #94A3B8; 
            font-size: 9px; 
            background-color: transparent;
        """
        )
        main_layout.addWidget(
            self.version_label, alignment=Qt.AlignmentFlag.AlignCenter
        )

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
