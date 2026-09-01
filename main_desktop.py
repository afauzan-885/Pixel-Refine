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
import subprocess
import tempfile

# Suppress Vulkan loader registry warnings on Windows
os.environ["VK_LOADER_DEBUG"] = "error"


def _ensure_llvm20_interpreter():
    """Re-exec the desktop entrypoint on the isolated LLVM20 interpreter.

    A legacy system/venv Python can still expose Taichi LLVM15 through
    ``sys.path`` even when the native AOT bridge later resolves the D: release.
    Keep imports and tests untouched, but make direct desktop launches
    deterministic by replacing the process before any application module is
    initialized. ``PIXEL_REFINE_DISABLE_AUTO_REEXEC=1`` is reserved for
    controlled diagnostics.
    """
    if (
        os.name != "nt"
        or os.environ.get("PIXEL_REFINE_DISABLE_AUTO_REEXEC", "0") == "1"
        or getattr(sys, "frozen", False)
    ):
        return

    runtime_root = os.environ.get("PIXEL_REFINE_RUNTIME_ROOT", "").strip()
    project_root = os.path.dirname(os.path.abspath(__file__))
    candidate = os.environ.get(
        "PIXEL_REFINE_PYTHON_INTERPRETER",
        os.path.join(project_root, "venv", "Scripts", "python.exe"),
    )
    if not os.path.isfile(candidate):
        return

    current = os.path.abspath(sys.executable)
    target = os.path.abspath(candidate)
    if os.path.normcase(current) == os.path.normcase(target):
        return

    os.environ["PIXEL_REFINE_LLVM20_REEXEC"] = "1"
    if runtime_root:
        os.environ["PIXEL_REFINE_RUNTIME_ROOT"] = os.path.abspath(runtime_root)
    else:
        os.environ.pop("PIXEL_REFINE_RUNTIME_ROOT", None)
    os.environ["PIXEL_REFINE_CANONICAL_LAUNCH"] = "1"
    extra_python_path = os.environ.get("PIXEL_REFINE_EXTRA_PYTHONPATH", "").strip()
    os.environ["PYTHONPATH"] = os.pathsep.join(
        value for value in (project_root, extra_python_path) if value
    )
    if os.environ.get("PIXEL_REFINE_VERBOSE_BOOTSTRAP", "0") == "1":
        print(
            f"[PixelRefine] Re-executing desktop entrypoint on LLVM20 interpreter: {target}",
            flush=True,
        )
    child = subprocess.run(
        [target, *sys.argv],
        cwd=project_root,
        env=os.environ.copy(),
        close_fds=True,
    )
    raise SystemExit(child.returncode)


if __name__ == "__main__":
    _ensure_llvm20_interpreter()


def _bootstrap_aot_backend_from_settings():
    """Apply saved AOT backend before any module can import taichi_aot."""
    if os.environ.get("AOT_DEVICE") is not None:
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

    from taichi_vision.backend_config import normalize_backend

    arch = normalize_backend(
        settings.get("device_backend_arch") or "cpu",
        allow_auto=False,
    )
    device_id = settings.get("device_backend_id", None)
    if device_id is None:
        return

    # Resolve the persisted GPU fingerprint against the *current* Vulkan
    # enumeration.  A device ordinal is intentionally only a cache: drivers
    # may reorder adapters after an update or a display configuration change.
    selector = settings.get("device_selector")
    if arch in ("vulkan", "opengl") and not isinstance(selector, dict):
        # One-time migration from settings written before stable selectors.
        from taichi_vision.device_selection import make_device_selector

        legacy_name = str(settings.get("device_backend") or "")
        if legacy_name and "cpu" not in legacy_name.lower():
            selector = make_device_selector(legacy_name)
            settings["device_selector"] = selector
    if arch in ("vulkan", "opengl") and isinstance(selector, dict):
        try:
            from taichi_vision.device_selection import (
                resolve_device_selector,
                scan_vulkan_device_records,
            )

            devices = scan_vulkan_device_records()
            resolved_id = resolve_device_selector(selector, devices, device_id)
            if resolved_id is None:
                print(
                    "[PixelRefine Backend] Saved GPU is unavailable; selecting CPU safely."
                )
                arch, device_id = "cpu", -1
            else:
                device_id = resolved_id
                settings["device_backend_id"] = resolved_id
                with open(settings_path, "w", encoding="utf-8") as fh:
                    json.dump(settings, fh, indent=2, ensure_ascii=False)
        except Exception as exc:
            # A failed scan must never reinterpret a stale ordinal as another
            # GPU. Keep startup available using CPU until a later rescan.
            print(
                f"[PixelRefine Backend] GPU fingerprint scan failed; selecting CPU: {exc}"
            )
            arch, device_id = "cpu", -1

    try:
        device_id_int = int(device_id)
    except (TypeError, ValueError):
        return

    from taichi_vision.backend_config import BackendConfig, backend_env

    canonical_config = BackendConfig(
        backend=arch or "cpu",
        device_id=device_id_int,
        vendor=(selector or {}).get("vendor", "") if isinstance(selector, dict) else "",
        device_name=(
            (selector or {}).get("name", "") if isinstance(selector, dict) else ""
        ),
        explicit=True,
        source="app_setting.json",
        strict=True,
    )
    os.environ.update(backend_env(canonical_config))
    os.environ["AOT_STRICT_BACKEND"] = "1"
    if arch == "opengl" and isinstance(selector, dict):
        os.environ["OPENGL_EXPECTED_VENDOR"] = str(selector.get("vendor", "")).lower()
        os.environ["OPENGL_EXPECTED_NAME"] = str(selector.get("name", ""))
    else:
        os.environ.pop("OPENGL_EXPECTED_VENDOR", None)
        os.environ.pop("OPENGL_EXPECTED_NAME", None)
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
                    json.dump(
                        {
                            "selector": selector,
                            "cached_ordinal": device_id_int,
                        },
                        fh,
                        indent=2,
                        ensure_ascii=False,
                    )
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
    QProxyStyle,
    QStyle,
    QToolTip,
    QMessageBox,
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QObject, QEvent, QTimer

# Project imports.  The source tree now keeps the desktop package under
# ``pixel_refine_desktop``; retain the historical ``desktop`` import for
# installed bundles that still expose that compatibility root.
try:
    from desktop.app_core import ApplicationManager, WindowConfig
    from desktop.ui import (
        EnhanceStackView,
        SettingsView,
        Sidebar,
        SplashScreen,
    )
except ModuleNotFoundError as exc:
    if exc.name != "desktop":
        raise
    from pixel_refine_desktop.app_core import ApplicationManager, WindowConfig
    from pixel_refine_desktop.ui import (
        EnhanceStackView,
        SettingsView,
        Sidebar,
        SplashScreen,
    )
from resources.animations.fade import fade_in
from pixel_refine_desktop.app_core.project_file_association import (
    register_project_file_association,
)
from pixel_refine_desktop.enhance_stack.core.logic.project_archive import (
    restore_project_session,
)

# from desktop.ui.views.panorama import PanoramaPage
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
        import taichi_vision.taichi_aot as taichi_aot

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
from resources.GenericUILibrary.modals import modal_confirm


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
        self.enhance_stack_view: EnhanceStackView | None = None
        self.sidebar: Sidebar | None = None
        self.app_manager: ApplicationManager | None = None
        self.window_config: WindowConfig | None = None
        self.sidebar_buttons = []
        self._close_confirmation_accepted = False
        self.setAcceptDrops(True)

    def _project_drop_path(self, event):
        mime_data = event.mimeData() if hasattr(event, "mimeData") else None
        if mime_data is None or not mime_data.hasUrls():
            return None
        for url in mime_data.urls():
            if url.isLocalFile() and url.toLocalFile().lower().endswith(".prf"):
                path = os.path.abspath(url.toLocalFile())
                if os.path.isfile(path):
                    return path
        return None

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.DragEnter:
            if self._project_drop_path(event):
                event.acceptProposedAction()
                return True
        elif event.type() == QEvent.Type.Drop:
            path = self._project_drop_path(event)
            if path and self.enhance_stack_view:
                self.enhance_stack_view._open_project(path)
                event.acceptProposedAction()
                return True
        return super().eventFilter(watched, event)

    def setup_ui_and_logic(self, splash: SplashScreen):
        """Setup UI and application logic with friendly progress updates."""
        # Initialize core components
        self._initialize_core_components(splash)

        # Configure window properties
        self._configure_window(splash)

        # Load UI based on architecture
        self._load_ui_components(splash)

        # Assemble final layout
        self._assemble_layout(splash)

    def setup_ui_and_logic(self, splash: SplashScreen):
        """Setup UI and application logic with friendly progress updates."""
        from pixel_refine_desktop.ui.views.settings.General.Language import (
            language_config,
        )

        # Initialize core components
        self._initialize_core_components(splash)

        # Configure window properties
        self._configure_window(splash)

        # Load UI based on architecture
        self._load_ui_components(splash)

        # Assemble final layout
        self._assemble_layout(splash)

        # Finalize
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_FINALIZING", "Menyiapkan workspace..."),
            100,
        )
        self.switch_page(0)

    def _initialize_core_components(self, splash: SplashScreen):
        """Initialize core application components."""
        from pixel_refine_desktop.ui.views.settings.General.Language import (
            language_config,
        )

        # Application manager
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_CHECKING_APP", "Memeriksa aplikasi..."),
            3,
        )
        self.app_manager = ApplicationManager(self)
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_APP_ACTIVE", "Aplikasi aktif"),
            10,
        )

        # Database
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_CHECKING_PROJECT", "Memeriksa data proyek..."),
            15,
        )
        self.app_manager.initialize_database()
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_PROJECT_READY", "Data proyek siap"),
            20,
        )

        # Animator
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_PREPARING_EFFECTS", "Menyiapkan efek visual..."),
            25,
        )
        self.app_manager.setup_animator()
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_EFFECTS_READY", "Efek visual siap"),
            30,
        )

        # Algorithms
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_PREPARING_MODULES", "Menyiapkan modul proses..."),
            35,
        )
        algo_summary = self.app_manager.load_algorithms()
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_MODULES_READY", "Modul siap"),
            40,
        )
        print(f"Loaded algorithms: {algo_summary}")

    def _configure_window(self, splash: SplashScreen):
        """Configure window properties and settings."""
        from pixel_refine_desktop.ui.views.settings.General.Language import (
            language_config,
        )

        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_LOADING_WINDOW", "Memuat tampilan jendela..."),
            48,
        )

        # Window icon and title
        self.setWindowIcon(QIcon("resources/assets/images/Logo_Pixel_Refine.ico"))
        self.setWindowTitle(f"Pixel Refine - Version {config.APP_VERSION}")

        # Window configuration
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_ADJUSTING_SCREEN", "Menyesuaikan resolusi layar..."),
            52,
        )
        self.window_config = WindowConfig(
            app_aspect_ratio=config.WINDOW_CONFIG["app_aspect_ratio"],
            min_screen_ratio=config.WINDOW_CONFIG["min_screen_ratio"],
            abs_min_width=config.WINDOW_CONFIG["abs_min_width"],
            abs_min_height=config.WINDOW_CONFIG["abs_min_height"],
        )
        self.window_config.apply_to_window(self)
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_SCREEN_READY", "Tampilan siap"),
            56,
        )

        # Prepare folders
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_PREPARING_WORKSPACE", "Menyiapkan ruang kerja..."),
            58,
        )
        if self.app_manager:
            self.app_manager.initialize_folders()
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_WORKSPACE_READY", "Ruang kerja siap"),
            62,
        )

    def _load_ui_components(self, splash: SplashScreen):
        """Load UI components."""
        from pixel_refine_desktop.ui.views.settings.General.Language import (
            language_config,
        )

        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_LOADING_UI", "Memuat UI utama..."),
            65,
        )
        self._load_mvc_architecture(splash)

    def _load_mvc_architecture(self, splash: SplashScreen):
        """Load MVC architecture components."""
        from pixel_refine_desktop.ui.views.settings.General.Language import (
            language_config,
        )

        # Create main content stack
        self.main_content = QStackedWidget()
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_PREPARING_PAGE", "Menyiapkan halaman kerja..."),
            68,
        )

        # Enhance Stack View
        if self.app_manager is None or self.app_manager.database_manager is None:
            raise RuntimeError("App Manager or Database Manager not initialized")

        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_OPENING_MAIN_WORKSPACE", "Membuka workspace utama..."),
            72,
        )
        enhance_stack_view = EnhanceStackView(
            db_path=self.app_manager.database_manager.db_path,
            parent=self.main_content,
        )
        self.enhance_stack_view = enhance_stack_view
        self.main_content.addWidget(enhance_stack_view)
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_MAIN_WORKSPACE_READY", "Workspace siap digunakan"),
            80,
        )

        # Connect navigation signal from EnhanceStackView
        enhance_stack_view.page_changed.connect(self.switch_page)

        # Settings View
        if self.app_manager is None or self.app_manager.database_manager is None:
            raise RuntimeError("App Manager or Database Manager not initialized")

        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_LOADING_SETTINGS", "Memuat panel pengaturan..."),
            82,
        )
        settings_view = SettingsView(
            db_path=self.app_manager.database_manager.db_path,
            parent=self.main_content,
        )
        self.main_content.addWidget(settings_view)
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_SETTINGS_READY", "Pengaturan siap"),
            86,
        )

    def _assemble_layout(self, splash: SplashScreen):
        """Assemble the final UI layout."""
        from pixel_refine_desktop.ui.views.settings.General.Language import (
            language_config,
        )

        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_ASSEMBLING_LAYOUT", "Menyusun tata letak aplikasi..."),
            90,
        )

        self.main_layout = QHBoxLayout()
        if self.main_content is None:
            raise RuntimeError("Main content stack not initialized")

        self.main_layout.addWidget(self.main_content, 1)  # Stretch factor
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        container = QWidget()
        container.setLayout(self.main_layout)
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_FINISHING_SETUP", "Menyelesaikan persiapan awal..."),
            94,
        )
        self.setCentralWidget(container)

    def closeEvent(self, event):
        """Handle application close event."""
        app = QApplication.instance()
        skip_confirmation = bool(
            app and app.property("_pixel_refine_skip_close_confirmation")
        )
        project_exit_decided = False
        if not skip_confirmation and not self._close_confirmation_accepted:
            from pixel_refine_desktop.ui.views.settings.General.Language import (
                language_config,
            )

            project_view = self.enhance_stack_view
            if project_view and project_view.project_has_unsaved_changes():
                save_dialog = QMessageBox(self)
                save_dialog.setIcon(QMessageBox.Icon.Warning)
                save_dialog.setWindowTitle(
                    getattr(
                        language_config, "PROJECT_SAVE_CHANGES_TITLE", "Save Project"
                    )
                )
                save_dialog.setText(
                    getattr(
                        language_config,
                        "PROJECT_SAVE_CHANGES_MESSAGE",
                        "This project has unsaved changes. Save before exiting?",
                    )
                )
                save_button = save_dialog.addButton(
                    getattr(language_config, "PROJECT_SAVE_CHANGES_SAVE", "Save"),
                    QMessageBox.ButtonRole.AcceptRole,
                )
                discard_button = save_dialog.addButton(
                    getattr(
                        language_config, "PROJECT_SAVE_CHANGES_DISCARD", "Don't Save"
                    ),
                    QMessageBox.ButtonRole.DestructiveRole,
                )
                cancel_button = save_dialog.addButton(
                    getattr(language_config, "PROJECT_SAVE_CHANGES_CANCEL", "Cancel"),
                    QMessageBox.ButtonRole.RejectRole,
                )
                save_dialog.exec()
                clicked = save_dialog.clickedButton()
                if clicked is save_button:
                    if not project_view._save_project(blocking=True):
                        event.ignore()
                        return
                    project_exit_decided = True
                elif clicked is cancel_button or clicked is None:
                    event.ignore()
                    return
                elif clicked is not discard_button:
                    event.ignore()
                    return
                else:
                    project_exit_decided = True

            if project_exit_decided:
                # The Save/Don't Save decision already confirms the user's
                # intent to exit; do not ask for a second confirmation.
                self._close_confirmation_accepted = True
            else:
                dialog = modal_confirm(
                    getattr(
                        language_config,
                        "EXIT_APPLICATION_MESSAGE",
                        "Do you want to exit the application?",
                    ),
                    self,
                )
                dialog.title_text.setText(
                    getattr(
                        language_config, "EXIT_APPLICATION_TITLE", "Exit Application"
                    )
                )
                dialog.yes_button.setText(
                    getattr(language_config, "EXIT_APPLICATION_YES", "Yes")
                )
                dialog.no_button.setText(
                    getattr(language_config, "EXIT_APPLICATION_NO", "No")
                )
                if dialog.exec() != dialog.DialogCode.Accepted:
                    event.ignore()
                    return
                self._close_confirmation_accepted = True

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
    app.setWindowIcon(QIcon("resources/assets/images/Logo_Pixel_Refine.ico"))
    register_project_file_association()

    project_argument = next(
        (
            os.path.abspath(argument)
            for argument in sys.argv[1:]
            if argument.lower().endswith(".prf") and os.path.isfile(argument)
        ),
        None,
    )
    session_database = os.path.join(
        tempfile.gettempdir(), f"pixel_refine_session_{os.getpid()}.sqlite"
    )
    try:
        if project_argument:
            restore_project_session(project_argument, session_database)
        else:
            # A new launch starts with an empty, private session.  Persistent
            # batch data now lives only inside an explicit .prf archive.
            for path in (
                session_database,
                session_database + "-wal",
                session_database + "-shm",
            ):
                if os.path.isfile(path):
                    os.remove(path)
            parameter_path = os.path.join("database", "align", "batch_parameter.json")
            os.makedirs(os.path.dirname(parameter_path), exist_ok=True)
            with open(parameter_path, "w", encoding="utf-8") as handle:
                handle.write("{}\n")
        os.environ["PIXEL_REFINE_SESSION_DB"] = session_database
    except Exception as exc:
        QMessageBox.critical(app, "Project Error", str(exc))
        sys.exit(1)
    app.aboutToQuit.connect(lambda: _cleanup_aot_backend("about-to-quit"))

    # Load and apply theme from settings on startup
    try:
        try:
            from desktop.ui.views.settings.General.general_store import (
                get_general_store,
            )
        except ModuleNotFoundError as exc:
            if exc.name != "desktop":
                raise
            from pixel_refine_desktop.ui.views.settings.General.general_store import (
                get_general_store,
            )
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
    original_pixmap = QPixmap("resources/assets/images/Logo_Pixel_Refine.png")

    splash_width = int(screen_geometry.width() * 0.25)
    scaled_pixmap = original_pixmap.scaledToWidth(
        splash_width, Qt.TransformationMode.SmoothTransformation
    )

    from pixel_refine_desktop.ui.views.settings.General.Language import (
        language_config,
    )

    version_text = f"Version {config.APP_VERSION}"
    splash = SplashScreen(scaled_pixmap, version_text)

    splash.show()
    # Show the splash at 0% before any heavy work begins so the user
    # sees the spinner immediately rather than a blank image.
    splash.update_status(
        getattr(language_config, "SPLASH_STATUS_STARTING", "Memulai aplikasi..."), 0
    )
    app.processEvents()

    # Create and setup main window
    window = PixelRefineMain()
    window.setup_ui_and_logic(splash)
    app.installEventFilter(window)

    # Load and apply initial stylesheet & theme triggers at startup
    try:
        splash.update_status(
            getattr(language_config, "SPLASH_STATUS_PREPARING_THEME", "Menyiapkan tema tampilan..."), 97
        )
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

    # A .prf opened from Explorer is passed as a command-line argument.
    if project_argument and window.enhance_stack_view:
        QTimer.singleShot(
            0,
            lambda path=project_argument: window.enhance_stack_view._open_project(path),
        )

    # Run application
    exit_code = 0
    try:
        exit_code = app.exec()
    finally:
        if window.app_manager:
            window.app_manager.cleanup_session_database()
        _cleanup_aot_backend("event-loop-exit")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
