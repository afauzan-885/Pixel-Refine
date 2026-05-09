"""
Pixel Refine - Main Application Entry Point
============================================
This module initializes and runs the Pixel Refine application.
"""

import sys
import os
import time

# --- Taichi Cache Configuration ---
# Store Taichi kernels in the project root to prevent auto-deletion and speed up JIT.
# Using forward slashes and a standard folder name for maximum compatibility on Windows.
_current_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
_cache_path = f"{_current_dir}/taichi_cache"
if not os.path.exists(_cache_path):
    os.makedirs(_cache_path, exist_ok=True)
os.environ["TI_OFFLINE_CACHE"] = "1"
os.environ["TI_OFFLINE_CACHE_FILE_PATH"] = _cache_path
os.environ["TI_OFFLINE_CACHE_DIR"] = _cache_path

# --- Backend Configuration for AOT/TiRT ---
# Disable CUDA Async Malloc for Taichi stability before any other imports
os.environ["TI_ENABLE_CUDA_MALLOC_ASYNC"] = "0"


# PySide6 imports
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QHBoxLayout,
    QWidget,
    QStackedWidget,
    QLabel,
    QProxyStyle,
    QStyle,
    QToolTip,
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QObject, QEvent

# Project imports
from pixel_refine_desktop.app_core import ApplicationManager, WindowConfig
from pixel_refine_desktop.ui import (
    EnhanceStackView,
    SettingsView,
    Sidebar,
    SplashScreen,
    fade_in,
)

# from pixel_refine_desktop.ui.views.panorama import PanoramaPage
import config

# import taichi as ti

# Initialize Taichi globally
# try:
#     ti.init(arch=ti.gpu, offline_cache=True)
# except Exception as e:
#     print(f"Taichi initialization failed: {e}")


# ============================================================================
# CUSTOM STYLES AND FILTERS
# ============================================================================


class CustomStyle(QProxyStyle):
    """Custom style to set tooltip delay to 200ms."""

    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.StyleHint.SH_ToolTip_WakeUpDelay:
            return 200  # 200ms delay before tooltip appears
        return super().styleHint(hint, option, widget, returnData)


class ToolTipFilter(QObject):
    """
    Event filter to intercept tooltip events and wrap text using HTML
    to ensure adaptive width based on font size (em units).
    """

    def eventFilter(self, obj, event):
        """Filter tooltip events to add HTML formatting for word wrapping."""
        if event.type() == QEvent.Type.ToolTip:
            widget = obj
            tooltip = widget.toolTip()

            # Only process plain text tooltips (not already HTML)
            if (
                tooltip
                and not tooltip.strip().startswith("<html>")
                and not tooltip.strip().startswith("<p")
            ):
                # Escape HTML special characters to prevent injection
                import html

                escaped_tooltip = html.escape(tooltip)

                # Convert newlines to <br> tags to preserve line breaks
                formatted_text = escaped_tooltip.replace("\n", "<br>")

                # Wrap in HTML with width in em units and preserve whitespace
                # 25em ≈ 400px for 16px font, but adapts to font size
                # white-space: pre-wrap preserves spaces and allows wrapping
                formatted_tooltip = (
                    f"<div style='width: 25em; text-align: left; white-space: pre-wrap;'>"
                    f"{formatted_text}</div>"
                )

                # Show the tooltip manually with the formatted text
                QToolTip.showText(event.globalPos(), formatted_tooltip, widget)
                return True  # Event handled

        return super().eventFilter(obj, event)


# ============================================================================
# MAIN WINDOW CLASS
# ============================================================================


class PixelRefineMain(QMainWindow):
    """Main application window for Pixel Refine."""

    def __init__(self):
        """
        Initialize main window.
        Lightweight constructor that only initializes attributes.
        """
        super().__init__()
        self.main_content: QStackedWidget | None = None
        self.sidebar: Sidebar | None = None
        self.app_manager: ApplicationManager | None = None
        self.window_config: WindowConfig | None = None
        self.sidebar_buttons = []

    def setup_ui_and_logic(self, splash: SplashScreen):
        """Setup UI and application logic with progress updates."""
        # Initialize core components
        self._initialize_core_components(splash)

        # Configure window properties
        self._configure_window(splash)

        # Load UI based on architecture
        self._load_ui_components(splash)

        # Assemble final layout
        self._assemble_layout(splash)

        # Finalize
        splash.update_status("Finalizing...", 100)
        self.switch_page(0)

    def _initialize_core_components(self, splash: SplashScreen):
        """Initialize core application components."""
        # Application manager
        splash.update_status("Initializing application...", 10)
        self.app_manager = ApplicationManager(self)

        # Database
        splash.update_status("Loading database...", 20)
        self.app_manager.initialize_database()

        # Animator
        splash.update_status("Initializing animations...", 30)
        self.app_manager.setup_animator()

        # Algorithms
        splash.update_status("Loading algorithms...", 40)
        algo_summary = self.app_manager.load_algorithms()
        print(f"Loaded algorithms: {algo_summary}")

    def _configure_window(self, splash: SplashScreen):
        """Configure window properties and settings."""
        splash.update_status("Setting up main window...", 50)

        # Window icon and title
        self.setWindowIcon(
            QIcon("pixel_refine_desktop/ui/resources/assets/icons/enhance_stack.png")
        )
        self.setWindowTitle(f"Pixel Refine - Version {config.APP_VERSION}")

        # Window configuration
        self.window_config = WindowConfig(
            app_aspect_ratio=1200 / 600,
            min_screen_ratio=0.76,
            abs_min_width=800,
            abs_min_height=400,
        )
        self.window_config.apply_to_window(self)

        # Prepare folders
        splash.update_status("Preparing temporary folders...", 60)
        if self.app_manager:
            self.app_manager.initialize_folders()

    def _load_ui_components(self, splash: SplashScreen):
        """Load UI components."""
        splash.update_status("Loading UI components...", 70)
        self._load_mvc_architecture(splash)

    def _load_mvc_architecture(self, splash: SplashScreen):
        """Load MVC architecture components."""
        # Create main content stack
        self.main_content = QStackedWidget()

        # Enhance Stack View
        splash.update_status("Initializing Enhance Stack View...", 75)
        if self.app_manager is None or self.app_manager.database_manager is None:
            raise RuntimeError("App Manager or Database Manager not initialized")

        enhance_stack_view = EnhanceStackView(
            db_path=self.app_manager.database_manager.db_path,
            parent=self.main_content,
        )
        self.main_content.addWidget(enhance_stack_view)

        # Connect navigation signal from EnhanceStackView
        enhance_stack_view.page_changed.connect(self.switch_page)

        # Panorama Page
        # splash.update_status("Initializing Panorama Page...", 80)
        # panorama_page = PanoramaPage(
        #     database_manager=self.app_manager.database_manager,
        # )
        # self.main_content.addWidget(panorama_page)

        # Settings View
        splash.update_status("Initializing Settings View...", 85)
        if self.app_manager is None or self.app_manager.database_manager is None:
            raise RuntimeError("App Manager or Database Manager not initialized")

        settings_view = SettingsView(
            db_path=self.app_manager.database_manager.db_path,
            parent=self.main_content,
        )
        self.main_content.addWidget(settings_view)

        # Sidebar - REMOVED (Now internal to EnhanceStackView/DisplayPanel)
        # splash.update_status("Initializing Sidebar...", 90)
        # self.sidebar = self._create_sidebar()

        # Print architecture info
        # self._print_info()

    def _assemble_layout(self, splash: SplashScreen):
        """Assemble the final UI layout."""
        splash.update_status("Assembling UI layout...", 95)

        self.main_layout = QHBoxLayout()
        # self.main_layout.addWidget(self.sidebar) # Removed global sidebar
        if self.main_content is None:
            raise RuntimeError("Main content stack not initialized")

        self.main_layout.addWidget(self.main_content, 1)  # Stretch factor
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def closeEvent(self, event):
        """Handle application close event."""
        if self.app_manager:
            self.app_manager.cleanup_folders()
        event.accept()

    def switch_page(self, index):
        """Switch to a different page with fade animation."""
        if self.main_content is None:
            return
        if not (0 <= index < self.main_content.count()):
            return

        # Check if already on the same page
        if (
            index == self.main_content.currentIndex()
            and self.main_content.widget(index) is not None
        ):
            return

        # Switch page
        if self.app_manager and self.app_manager.animator:
            # Note: fade_in parameter order is (animator, target_widget/index, stack_widget, duration)
            fade_in(self.app_manager.animator, index, self.main_content, duration=250)

    def toggle_sidebar(self):
        """Toggle sidebar visibility (placeholder for future implementation)."""
        pass


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================


def main():
    """Main application entry point."""
    # Create application
    app = QApplication(sys.argv)

    # Apply custom styles
    app.setStyle(CustomStyle())

    # Install adaptive tooltip filter
    tooltip_filter = ToolTipFilter()
    app.installEventFilter(tooltip_filter)

    # Configure global tooltip stylesheet
    app.setStyleSheet(
        """
        QToolTip {
            border: 1px solid #333;
            background-color: #2c3e50;
            color: white;
            padding: 5px;
            border-radius: 3px;
        }
    """
    )

    # Setup splash screen
    screen_geometry = app.primaryScreen().geometry()
    original_pixmap = QPixmap(
        "pixel_refine_desktop/ui/resources/assets/images/Logo_Pixel_Refine.png"
    )

    splash_width = int(screen_geometry.width() * 0.25)
    scaled_pixmap = original_pixmap.scaledToWidth(
        splash_width, Qt.TransformationMode.SmoothTransformation
    )

    version_text = f"Version {config.APP_VERSION}"
    splash = SplashScreen(scaled_pixmap, version_text)

    splash.show()
    app.processEvents()

    # Create and setup main window
    window = PixelRefineMain()
    window.setup_ui_and_logic(splash)

    # Show main window and close splash
    window.show()
    splash.finish(window)

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
