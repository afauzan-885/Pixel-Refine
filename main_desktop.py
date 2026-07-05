"""
Pixel Refine - Main Application Entry Point
============================================
This module initializes and runs the Pixel Refine application.
"""

import sys
import os
import time
import atexit
import signal
import threading
import json

# Suppress Vulkan loader registry warnings on Windows
os.environ["VK_LOADER_DEBUG"] = "error"

def _bootstrap_aot_backend_from_settings():
    """Apply saved AOT backend before any module can import taichi_aot."""
    if os.environ.get("PIXEL_REFINE_AOT_DEVICE") is not None:
        return

    settings_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "database",
        "setting",
        "app_setting.json",
    )
    try:
        with open(settings_path, "r", encoding="utf-8") as fh:
            settings = json.load(fh)
    except Exception:
        return

    arch = str(settings.get("device_backend_arch") or "").strip().lower()
    device_id = settings.get("device_backend_id", None)
    if arch:
        os.environ.setdefault("PIXEL_REFINE_AOT_ARCH", arch)
    if device_id is None:
        return

    try:
        device_id_int = int(device_id)
    except (TypeError, ValueError):
        return

    os.environ["PIXEL_REFINE_AOT_DEVICE"] = str(device_id_int)
    if arch == "vulkan" and device_id_int >= 0:
        try:
            cache_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "PixelRefine")
            if cache_dir:
                os.makedirs(cache_dir, exist_ok=True)
                with open(
                    os.path.join(cache_dir, "aot_device_cache.txt"),
                    "w",
                    encoding="utf-8",
                ) as fh:
                    fh.write(str(device_id_int))
        except Exception:
            pass


_bootstrap_aot_backend_from_settings()

# --- Taichi Cache Configuration ---
# Offline cache disabled per request.
os.environ["TI_OFFLINE_CACHE"] = "0"

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
)
from resources.animations.fade import fade_in

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


_SHUTDOWN_LOCK = threading.Lock()
_SHUTDOWN_DONE = False


def _cleanup_aot_backend(reason="app-shutdown"):
    """Best-effort GPU/AOT cleanup for app close, crash, and signal exits."""
    global _SHUTDOWN_DONE
    with _SHUTDOWN_LOCK:
        if _SHUTDOWN_DONE:
            return
        _SHUTDOWN_DONE = True

    try:
        print(f"[PixelRefine Shutdown] AOT cleanup start reason={reason}", flush=True)
    except Exception:
        pass

    try:
        import gc
        import taichi_library.taichi_aot as taichi_aot

        try:
            taichi_aot.unload_all_modules()
        except Exception:
            pass
        try:
            taichi_aot.engine.destroy()
        except Exception:
            pass
        try:
            gc.collect()
        except Exception:
            pass
    except Exception as exc:
        try:
            print(f"[PixelRefine Shutdown] AOT cleanup skipped: {exc}", flush=True)
        except Exception:
            pass


def _install_shutdown_guards():
    """Install process-level hooks that release GPU resources before exit."""
    atexit.register(_cleanup_aot_backend, "atexit")

    def _handle_exception(exc_type, exc, tb):
        _cleanup_aot_backend("unhandled-exception")
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = _handle_exception

    def _handle_signal(signum, frame):
        _cleanup_aot_backend(f"signal-{signum}")
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)

    for sig_name in ("SIGTERM", "SIGINT"):
        if hasattr(signal, sig_name):
            try:
                signal.signal(getattr(signal, sig_name), _handle_signal)
            except (OSError, ValueError):
                pass
    if hasattr(signal, "SIGBREAK"):
        try:
            signal.signal(signal.SIGBREAK, _handle_signal)
        except (OSError, ValueError):
            pass


class CustomStyle(QProxyStyle):
    """Custom style to set tooltip delay to 100ms."""

    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.StyleHint.SH_ToolTip_WakeUpDelay:
            return 100  # 100ms delay before tooltip appears
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


from resources.GenericUILibrary import live_update


@live_update
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
            QIcon("resources/assets/icons/enhance_stack.png")
        )
        self.setWindowTitle(f"Pixel Refine - Version {config.APP_VERSION}")

        # Window configuration
        self.window_config = WindowConfig(
            app_aspect_ratio=config.WINDOW_CONFIG["app_aspect_ratio"],
            min_screen_ratio=config.WINDOW_CONFIG["min_screen_ratio"],
            abs_min_width=config.WINDOW_CONFIG["abs_min_width"],
            abs_min_height=config.WINDOW_CONFIG["abs_min_height"],
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
        _cleanup_aot_backend("window-close")
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

    def retranslate_ui(self):
        """Update window title dynamically when language changes."""
        self.setWindowTitle(f"Pixel Refine - Version {config.APP_VERSION}")



# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================


def main():
    """Main application entry point."""
    _install_shutdown_guards()

    # Suppress native Vulkan loader registry warnings by wrapping stderr
    class VulkanWarningFilter:
        def __init__(self, target):
            self.target = target
        def write(self, message):
            if "windows_read_data_files_in_registry" not in message:
                self.target.write(message)
        def flush(self):
            self.target.flush()

    sys.stderr = VulkanWarningFilter(sys.stderr)

    # Create application
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(lambda: _cleanup_aot_backend("about-to-quit"))

    # Load and apply theme from settings on startup
    try:
        from pixel_refine_desktop.ui.views.settings.General.general_store import get_general_store
        from resources.GenericUILibrary.theme import set_theme, DarkTheme, LightTheme
        store = get_general_store()
        saved_theme = store.get("theme", "Light Theme")
        if saved_theme == "Dark Theme":
            set_theme(DarkTheme())
        else:
            set_theme(LightTheme())
    except Exception as e:
        print(f"Error loading initial theme: {e}")

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
        "resources/assets/images/Logo_Pixel_Refine.png"
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

    # Load and apply initial stylesheet & theme triggers at startup
    try:
        from resources.styles.stylesheet import stylesheet_global_page
        from resources.GenericUILibrary import trigger_live_update
        window.setStyleSheet(stylesheet_global_page())
        trigger_live_update()
        trigger_live_update("update_theme")
    except Exception as e:
        print(f"Error applying startup stylesheet/theme updates: {e}")

    # Show main window and close splash
    window.show()
    splash.finish(window)

    # Run application
    exit_code = 0
    try:
        exit_code = app.exec()
    finally:
        _cleanup_aot_backend("event-loop-exit")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
