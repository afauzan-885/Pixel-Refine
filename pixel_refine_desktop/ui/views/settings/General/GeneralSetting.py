import os
from contextlib import contextmanager

from PySide6.QtWidgets import QWidget, QMessageBox, QComboBox, QVBoxLayout, QBoxLayout
from PySide6.QtCore import Qt, QObject, QThread, Signal

from resources.GenericUILibrary import (
    Container,
    Stack,
    FormRow,
    FormGroup,
    Checkbox,
    Button,
    SyncMixin,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from resources.GenericUILibrary.modals import modal_confirm
from .general_store import get_general_store
from .helpers import restart_application
from taichi_vision.device_selection import (
    is_translation_device,
    make_device_selector,
    resolve_device_selector,
    scan_cuda_device_records,
    scan_vulkan_device_records,
)


def _hardware_test_timeout_seconds(analysis_mode: str) -> float:
    """Return a bounded timeout for one disposable backend test child.

    The interactive fast test must not leave the settings modal waiting for
    the native driver for the 25-minute deep-analysis limit.  The override is
    intentionally process-local so qualification scripts can choose a longer
    limit without changing the UI default.
    """
    default = 120.0 if str(analysis_mode).lower() == "fast" else 1500.0
    raw = os.environ.get("PIXEL_REFINE_HARDWARE_TEST_TIMEOUT_S")
    try:
        value = float(raw) if raw else default
    except (TypeError, ValueError):
        value = default
    return max(10.0, min(value, 3600.0))


@contextmanager
def _temporary_windows_gpu_preference(executable, vendor):
    """Select the intended hybrid-GPU class for an isolated OpenGL test.

    OpenGL has no Vulkan-style adapter ordinal on Optimus laptops. Windows
    chooses the renderer before Taichi starts, based on its per-executable
    graphics preference. Apply that preference only while launching the test
    subprocess and restore the user's previous value afterwards.
    """
    normalized_vendor = str(vendor or "").strip().lower()
    if os.name != "nt" or normalized_vendor not in {"intel", "nvidia", "amd"}:
        yield
        return

    try:
        import winreg

        executable = os.path.abspath(str(executable))
        key = winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\DirectX\UserGpuPreferences",
            0,
            winreg.KEY_QUERY_VALUE | winreg.KEY_SET_VALUE,
        )
    except OSError:
        # The renderer mismatch check still prevents a false-positive result
        # when policy/registry access is unavailable.
        yield
        return

    had_value = False
    previous_value = None
    previous_kind = winreg.REG_SZ
    try:
        try:
            previous_value, previous_kind = winreg.QueryValueEx(key, executable)
            had_value = True
        except FileNotFoundError:
            pass
        preference = 1 if normalized_vendor == "intel" else 2
        winreg.SetValueEx(
            key,
            executable,
            0,
            winreg.REG_SZ,
            f"GpuPreference={preference};",
        )
        winreg.FlushKey(key)
        yield
    finally:
        try:
            if had_value:
                winreg.SetValueEx(
                    key,
                    executable,
                    0,
                    previous_kind,
                    previous_value,
                )
            else:
                try:
                    winreg.DeleteValue(key, executable)
                except FileNotFoundError:
                    pass
            winreg.FlushKey(key)
        finally:
            winreg.CloseKey(key)


class HardwareBackendTestWorker(QObject):
    finished = Signal(dict)
    progress = Signal(int, str, int)
    log_line = Signal(str)

    def __init__(self, options, python_bin, analysis_mode="fast"):
        super().__init__()
        self.options = options
        self.python_bin = python_bin
        self.analysis_mode = "deep" if str(analysis_mode).lower() == "deep" else "fast"
        self._is_cancelled = False
        self._current_process = None

    def cancel(self):
        self._is_cancelled = True
        if self._current_process:
            try:
                self._current_process.kill()
            except Exception:
                pass

    def _estimated_seconds(self, option):
        backend = str(option.get("backend", "cpu")).lower()
        vendor = str(option.get("vendor", "")).lower()
        if self.analysis_mode == "fast":
            return 20 if backend == "cpu" else 35
        if backend == "vulkan" and vendor == "intel":
            return 240
        if backend == "opengl" and vendor == "intel":
            return 110
        if backend == "opengl":
            return 60
        return 50

    def run(self):
        import json
        import math
        import re
        import subprocess
        import tempfile
        import time

        test_results = {}
        total = max(len(self.options), 1)
        base_estimates = [self._estimated_seconds(option) for option in self.options]
        for index, option in enumerate(self.options, start=1):
            text = option.get("text", "")
            result_key = option.get("key", text)
            from taichi_vision.backend_config import normalize_backend, parse_device_id

            backend = normalize_backend(option.get("backend", "cpu"), allow_auto=False)
            device_id = parse_device_id(option.get("device_id"), 0) or 0
            if backend in ("cpu", "opengl"):
                device_id = 0
            vendor = str(option.get("vendor", "")).lower()
            success = False
            output = ""
            returncode = -1
            passed = total_tests = 0
            renderer = ""
            benchmark_width = 1024
            benchmark_height = 1024
            benchmark_elapsed_ms = None
            benchmark_runs = 4
            benchmark_warmup_runs = 1
            benchmark_gpu_only = False
            benchmark_metrics = {}
            benchmark_skipped = 0

            environment = os.environ.copy()
            # A parent process may have pinned an explicit bridge while
            # running an earlier backend (for example the OpenGL NVIDIA
            # renderer).  Keeping that override here defeats the requested
            # backend and can make a Vulkan probe initialize the old bridge.
            # Backend tests must resolve the bridge from the requested
            # AOT_ARCH/target contract; production callers can still provide
            # AOT_ENGINE_DLL outside this isolated test worker.
            environment.pop("AOT_ENGINE_DLL", None)
            environment.update(
                {
                    # AOT_ARCH selects the native bridge DLL; PIXEL_REFINE_AOT_ARCH
                    # selects the engine's runtime backend (canonical env from
                    # backend_config.backend_env).  Both must match so a "Vulkan"
                    # test does not silently run on an auto-selected CUDA device.
                    "AOT_ARCH": backend,
                    "PIXEL_REFINE_AOT_ARCH": backend,
                    "AOT_DEVICE": str(device_id),
                    "PIXEL_REFINE_AOT_DEVICE": str(device_id),
                    "AOT_STRICT_BACKEND": "1",
                    "AOT_ALLOW_CPU_FALLBACK": "0",
                    "AOT_SKIP_DOZEN": "1",
                    "INTEL_VULKAN_AUTO_QUALIFY": "0",
                    "VK_LOADER_DEBUG": "error",
                    # Every backend test is disposable. Prevent a native
                    # MSVC assertion from opening a modal dialog over the
                    # settings window; the child exit/log remains evidence.
                    "AOT_SUPPRESS_NATIVE_DIALOGS": "1",
                }
            )
            if backend == "vulkan" and vendor == "intel":
                # Compatibility testing is crash-isolated, so it may probe an
                # unqualified Intel driver without changing production policy.
                environment["AOT_INTEL_PROBE"] = "1"
                environment["AOT_ALLOW_UNSAFE_INTEL"] = "1"
            else:
                environment.pop("AOT_INTEL_PROBE", None)
                environment.pop("AOT_ALLOW_UNSAFE_INTEL", None)
                environment.pop("AOT_INTEL_UNSAFE", None)
            if backend == "cuda":
                environment["TARGET_VENDOR"] = "nvidia"
                environment["CUDA_EXPECTED_NAME"] = str(option.get("raw_name", ""))
            else:
                environment.pop("CUDA_EXPECTED_NAME", None)
            if backend == "opengl":
                environment["OPENGL_EXPECTED_VENDOR"] = vendor
                environment["OPENGL_EXPECTED_NAME"] = str(option.get("raw_name", ""))
                # The native bridge reads the PIXEL_REFINE-prefixed form;
                # retain the historical unprefixed aliases for Python-side
                # checks and older bridge builds.
                environment["PIXEL_REFINE_OPENGL_EXPECTED_VENDOR"] = vendor
                environment["PIXEL_REFINE_OPENGL_EXPECTED_NAME"] = str(
                    option.get("raw_name", "")
                )
                # Qualification must exercise the vendor ICD directly.  This
                # avoids WGL's adapter selection and also works on older
                # Windows drivers that ship no EGL provider.
                environment["OPENGL_CONTEXT"] = "icd"
                environment["OPENGL_ICD_ONLY"] = "1"
                # Deep probes intentionally run in a disposable child.  A
                # vendor CRT assertion must terminate that child quietly so
                # Windows does not put a modal Visual C++ dialog over the
                # settings window; the parent will still record the failure.
                environment["AOT_SUPPRESS_NATIVE_DIALOGS"] = "1"
                environment.pop("OPENGL_EGL_ONLY", None)
            else:
                environment.pop("OPENGL_EXPECTED_VENDOR", None)
                environment.pop("OPENGL_EXPECTED_NAME", None)
                environment.pop("PIXEL_REFINE_OPENGL_EXPECTED_VENDOR", None)
                environment.pop("PIXEL_REFINE_OPENGL_EXPECTED_NAME", None)
                environment.pop("OPENGL_CONTEXT", None)
                environment.pop("OPENGL_EGL_ONLY", None)

            test_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../Perfomance/test_comprehensif.py",
                )
            )
            command = [
                self.python_bin,
                "-u",
                test_path,
                "--run-logic",
            ]
            if self.analysis_mode == "fast":
                command.append("--fast")
            intel_vulkan_gate = (
                self.analysis_mode == "deep"
                and backend == "vulkan"
                and vendor == "intel"
            )
            if intel_vulkan_gate:
                probe_path = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../../../../../taichi_vision/vulkan_probe.py",
                    )
                )
                command = [
                    self.python_bin,
                    "-u",
                    probe_path,
                    "--comprehensive",
                    "--persist",
                    "--device",
                    str(device_id),
                    "--repeat",
                    "3",
                    "--timeout",
                    "1200",
                ]
            try:
                with tempfile.TemporaryDirectory(
                    prefix="pixel_refine_backend_test_"
                ) as cache_dir:
                    environment["AOT_CACHE"] = cache_dir
                    log_path = os.path.join(cache_dir, "backend_test.log")
                    with _temporary_windows_gpu_preference(
                        self.python_bin,
                        vendor if backend == "opengl" else "",
                    ):
                        started = time.monotonic()
                        estimate = float(base_estimates[index - 1])
                        with open(
                            log_path,
                            "w+",
                            encoding="utf-8",
                            errors="replace",
                        ) as log_file:
                            process = subprocess.Popen(
                                command,
                                stdout=log_file,
                                stderr=subprocess.STDOUT,
                                text=True,
                                env=environment,
                                creationflags=getattr(
                                    subprocess, "CREATE_NO_WINDOW", 0
                                ),
                            )
                            self._current_process = process
                            last_log_pos = 0

                            while process.poll() is None:
                                if self._is_cancelled:
                                    try:
                                        process.kill()
                                    except Exception:
                                        pass
                                    return

                                try:
                                    log_file.flush()
                                    curr_pos = log_file.tell()
                                    if curr_pos > last_log_pos:
                                        log_file.seek(last_log_pos)
                                        new_text = log_file.read()
                                        last_log_pos = curr_pos
                                        if new_text:
                                            for line in new_text.splitlines():
                                                if line.strip():
                                                    self.log_line.emit(line.strip())
                                except Exception:
                                    pass

                                elapsed = time.monotonic() - started
                                process_timeout = _hardware_test_timeout_seconds(
                                    self.analysis_mode
                                )
                                if elapsed >= process_timeout:
                                    process.kill()
                                    process.wait(timeout=10)
                                    self.log_line.emit(
                                        f"[Hardware Test] Timeout setelah "
                                        f"{process_timeout:.0f}s: {text}"
                                    )
                                    raise subprocess.TimeoutExpired(
                                        command, process_timeout
                                    )

                                effective_estimate = max(
                                    estimate,
                                    elapsed / 0.90 if elapsed else estimate,
                                )
                                local_fraction = min(
                                    0.95,
                                    elapsed / max(effective_estimate, 0.1),
                                )
                                overall = int(
                                    ((index - 1) + local_fraction) * 100 / total
                                )
                                remaining = max(
                                    0.0, effective_estimate - elapsed
                                ) + sum(base_estimates[index:])
                                self.progress.emit(
                                    overall,
                                    text,
                                    int(math.ceil(remaining)),
                                )
                                time.sleep(0.5)
                            returncode = int(process.returncode)
                            log_file.flush()
                            log_file.seek(0)
                            output = log_file.read()
                self.progress.emit(
                    int(index * 100 / total),
                    text,
                    int(sum(base_estimates[index:])),
                )
                if intel_vulkan_gate:
                    # The Vulkan probe writes human-readable diagnostics
                    # around its final JSON object.  A native driver crash can
                    # also truncate that object, so parse it defensively and
                    # report an ordinary backend failure instead of aborting
                    # the whole settings dialog with JSONDecodeError.
                    payload = None
                    decoder = json.JSONDecoder()
                    for brace in (i for i, char in enumerate(output) if char == "{"):
                        try:
                            candidate, _ = decoder.raw_decode(output[brace:])
                        except (ValueError, json.JSONDecodeError):
                            continue
                        if isinstance(candidate, dict):
                            payload = candidate
                    if payload is not None:
                        passed = int(payload.get("passed", 0))
                        total_tests = int(payload.get("total", 0))
                        renderer = str(payload.get("device", {}).get("name", ""))
                        success = bool(
                            returncode == 0
                            and payload.get("ok")
                            and passed == total_tests
                            and payload.get("pipeline_passed")
                            and payload.get("artifact_loaded")
                            == payload.get("artifact_total")
                        )
                    else:
                        # Keep the raw tail in the diagnostic log; do not
                        # fabricate a pass result for an incomplete probe.
                        passed = total_tests = 0
                        success = False
                        if output:
                            print(
                                f"[Test Subprocess Backend] {text} produced "
                                "no complete JSON result (likely native crash)\n"
                                f"{output[-4000:]}"
                            )
                else:
                    match = re.search(r"Results:\s*(\d+)\s*/\s*(\d+)", output)
                    if match:
                        passed, total_tests = map(int, match.groups())
                    benchmark_match = re.search(
                        r"Benchmark:\s*(\d+)x(\d+)\s*\|\s*"
                        r"elapsed_ms=([0-9]+(?:\.[0-9]+)?)",
                        output,
                    )
                    if benchmark_match:
                        benchmark_width = int(benchmark_match.group(1))
                        benchmark_height = int(benchmark_match.group(2))
                        benchmark_elapsed_ms = float(benchmark_match.group(3))
                    benchmark_config_match = re.search(
                        r"Benchmark:.*?\|\s*runs=(\d+)\s*\|\s*"
                        r"warmup=(\d+)\s*\|\s*gpu_only=(\d+)",
                        output,
                    )
                    if benchmark_config_match:
                        benchmark_runs = int(benchmark_config_match.group(1))
                        benchmark_warmup_runs = int(benchmark_config_match.group(2))
                        benchmark_gpu_only = bool(int(benchmark_config_match.group(3)))
                    metrics_match = re.search(
                        r"Benchmark Metrics:\s*(\{.*\})\s*$",
                        output,
                        re.MULTILINE,
                    )
                    if metrics_match:
                        try:
                            parsed_metrics = json.loads(metrics_match.group(1))
                            if isinstance(parsed_metrics, dict):
                                benchmark_metrics = parsed_metrics
                        except json.JSONDecodeError:
                            benchmark_metrics = {}
                    skipped_match = re.search(r"Skipped:\s*(\d+)", output)
                    if skipped_match:
                        benchmark_skipped = int(skipped_match.group(1))
                    renderer_match = re.search(
                        r"(?:Runtime initialized on '[^']+'\s*\((.+)\)|"
                        r"\[Taichi Vision\] Backend siap:\s*[^\n(]+\((.+)\))\s*$",
                        output,
                        re.MULTILINE,
                    )
                    if renderer_match:
                        renderer = next(
                            group.strip()
                            for group in renderer_match.groups()
                            if group
                        )
                    else:
                        mismatch = re.search(
                            r"(?:Windows created the context on|context provider selected) '([^']+)'",
                            output,
                        )
                        if mismatch:
                            renderer = mismatch.group(1).strip()
                    success = (
                        returncode == 0 and total_tests > 0 and passed == total_tests
                    )
                if not success:
                    print(
                        f"[Test Subprocess Backend] {text} failed "
                        f"({passed}/{total_tests}, code={returncode})\n"
                        f"{output[-4000:]}"
                    )
            except subprocess.TimeoutExpired as exc:
                output = f"Timed out after {exc.timeout} seconds"
            except Exception as exc:
                output = f"{type(exc).__name__}: {exc}"
                print(f"[Test Backend] {text} worker exception: {output}")

            diagnostic_lines = [
                line.strip() for line in output.splitlines() if line.strip()
            ]
            test_results[result_key] = {
                "status": "support" if success else "disable",
                "text": text,
                "backend": backend,
                "device_id": device_id,
                "vendor": vendor,
                "renderer": renderer,
                "passed": passed,
                "total": total_tests,
                "returncode": returncode,
                "analysis_mode": self.analysis_mode,
                "benchmark_width": benchmark_width,
                "benchmark_height": benchmark_height,
                "benchmark_elapsed_ms": benchmark_elapsed_ms,
                "benchmark_runs": benchmark_runs,
                "benchmark_warmup_runs": benchmark_warmup_runs,
                "benchmark_gpu_only": benchmark_gpu_only,
                "benchmark_skipped": benchmark_skipped,
                "benchmark_metrics": benchmark_metrics,
                "diagnostic": "\n".join(diagnostic_lines[-12:]),
            }

        self.finished.emit(test_results)


class HardwareProgressModal(modal_confirm):
    """
    Testing progress modal extending modal_confirm from GenericUILibrary.
    Wide, elegant layout:
    - Mode & Device title on wide horizontal lines
    - Live progress %, ETA
    - Full-width green progress bar (#2ECC71)
    - Full-width dark scrollable terminal log box
    - Top-right '✕' button for cancellation
    - Click-outside-to-cancel support
    """

    def __init__(
        self, title="Hardware Backend Analysis", message="", parent=None, on_cancel=None
    ):
        super().__init__(
            message=message,
            parent=parent,
            title=title,
            close_on_click_outside=True,
            on_close_callback=on_cancel,
            width=580,
            height=320,
        )
        self.query_icon.hide()  # Hide blue question icon

        # Hide default Yes/No buttons since this is a progress dialog
        self.yes_button.hide()
        self.no_button.hide()

        content_widget = self.message_label.parentWidget()
        if content_widget and content_widget.layout():
            content_widget.layout().setDirection(QBoxLayout.Direction.TopToBottom)
            content_widget.layout().setContentsMargins(18, 12, 18, 14)
            content_widget.layout().setSpacing(10)

        from PySide6.QtWidgets import QProgressBar, QTextEdit

        # Sleek progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                background-color: #E2E8F0;
                border: 1px solid #CBD5E1;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #2ECC71;
                border-radius: 4px;
            }
        """
        )

        # Live Scrollable Log Box
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Live testing output logs...")
        self.log_box.setFixedHeight(130)
        self.log_box.setStyleSheet(
            """
            QTextEdit {
                background-color: #0F172A;
                border: 1px solid #334155;
                border-radius: 6px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                color: #38BDF8;
                padding: 8px;
            }
        """
        )

        if content_widget and content_widget.layout():
            content_widget.layout().addWidget(self.progress_bar)
            content_widget.layout().addWidget(self.log_box)

    def setLabelText(self, text):
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        mode_str = lines[0] if len(lines) > 0 else ""
        backend_str = lines[1] if len(lines) > 1 else ""
        eta_str = lines[2] if len(lines) > 2 else ""
        self.message_label.setText(
            f"<div style='font-family: \"Segoe UI\", Arial; font-size: 13px; color: #1E293B; font-weight: 600; text-align: left;'>"
            f"<span>{mode_str} &nbsp;—&nbsp; {backend_str}</span>"
            f"<span style='float: right; color: #0EA5E9; font-weight: 600;'>{eta_str}</span>"
            f"</div>"
        )

    def setValue(self, val):
        self.progress_bar.setValue(int(val))

    def append_log(self, text):
        if text and text.strip():
            self.log_box.append(text.strip())
            sb = self.log_box.verticalScrollBar()
            if sb:
                sb.setValue(sb.maximum())


class GeneralSettingsPage(Container, SyncMixin):
    """
    General settings page refactored using GenericUILibrary.
    Supports real-time auto-sync for most parameters.
    """

    def __init__(self, parent=None):
        super().__init__(padding=20, parent=parent)
        self.setObjectName("GeneralSettingsPage")
        self.setStyleSheet(
            "#GeneralSettingsPage { background-color: transparent; border: none; }"
        )

        self.store = get_general_store()
        self.bind_store(self.store)

        # Track initial values for restart check
        self._initial_language = self.store.get("language", "English")
        self._initial_thumbnail = self.store.get("create_thumbnail", False)
        self._initial_device_backend = self.store.get(
            "device_backend", "CPU (Universal)"
        )

        self._setup_ui()

    def _setup_ui(self):
        # 1. Main Form Layout
        form = FormRow()

        # Languages
        languages = ["English", "Indonesian", "China Traditional", "Melayu"]
        lang_label = getattr(language_config, "LANGUAGE_LABEL", "Language:")

        # Use FormGroup as requested
        self.language_group = FormGroup(label=lang_label, input_type="select")

        if isinstance(self.language_group.input, QComboBox):
            self.language_group.input.addItems(languages)

        # We don't use auto_sync for language because we want to control the restart prompt
        self.language_group.bind_store(self.store, "language")
        form.add_row(self.language_group)

        # Processing-domain selection is persisted now so the resident
        # pipeline can opt into RAW-native fusion in a later change.  RGB
        # Linear remains the current production-compatible route.
        process_format_label = getattr(
            language_config, "PROCESS_FORMAT_LABEL", "Process Format"
        )
        process_format_tip = getattr(
            language_config,
            "PROCESS_FORMAT_DESCRIPTION",
            "Choose the image domain used by multi-frame processing.",
        )
        self.processing_format_group = FormGroup(
            label=process_format_label,
            input_type="select",
            auto_sync=True,
        )
        if isinstance(self.processing_format_group.input, QComboBox):
            self.processing_format_group.input.addItems(["RGB Linear", "RAW Native"])
            self.processing_format_group.input.setToolTip(process_format_tip)
        self.processing_format_group.bind_store(self.store, "processing_format")
        form.add_row(self.processing_format_group)

        # Themes Selection temporarily disabled.
        # theme_label = "Theme:"
        # self.theme_group = FormGroup(label=theme_label, input_type="select")
        # if isinstance(self.theme_group.input, QComboBox):
        #     self.theme_group.input.addItems(["Light Theme", "Dark Theme"])
        # self.theme_group.bind_store(self.store, "theme")
        # form.add_row(self.theme_group)

        # Thumbnails
        thumb_label = getattr(language_config, "THUMBNAIL_LABEL", "Enable Thumbnails")
        thumb_tip = getattr(language_config, "THUMBNAIL_DESCRIPTION", "")
        self.thumb_cb = Checkbox(thumb_label, auto_sync=True)
        self.thumb_cb.checkbox.setToolTip(thumb_tip)
        self.thumb_cb.bind_store(self.store, "create_thumbnail")
        self.thumb_cb.toggled.connect(self._on_thumbnail_toggled)
        form.add_row(self.thumb_cb)

        # Inactivity shutdown is deliberately opt-in.  The timer is owned by
        # main_desktop.py and observes these existing general settings.
        auto_shutdown_label = getattr(
            language_config, "AUTO_SHUTDOWN_LABEL", "Enable Auto Shutdown"
        )
        auto_shutdown_tip = getattr(
            language_config,
            "AUTO_SHUTDOWN_DESCRIPTION",
            "Close the application after the configured period without user activity.",
        )
        self.auto_shutdown_cb = Checkbox(auto_shutdown_label, auto_sync=True)
        self.auto_shutdown_cb.checkbox.setToolTip(auto_shutdown_tip)
        self.auto_shutdown_cb.bind_store(self.store, "auto_shutdown_enabled")
        self.auto_shutdown_cb.toggled.connect(self._on_auto_shutdown_toggled)
        form.add_row(self.auto_shutdown_cb)

        timeout_label = getattr(
            language_config,
            "AUTO_SHUTDOWN_TIMEOUT_LABEL",
            "Idle timeout (minutes)",
        )
        self.auto_shutdown_minutes_group = FormGroup(
            label=timeout_label,
            input_type="number",
            auto_sync=True,
        )
        self.auto_shutdown_minutes_group.input.setRange(1, 24 * 60)
        self.auto_shutdown_minutes_group.bind_store(
            self.store, "auto_shutdown_minutes"
        )
        form.add_row(self.auto_shutdown_minutes_group)
        self._update_auto_shutdown_timeout_state(
            self.auto_shutdown_cb.is_checked()
        )

        self.add_widget(form)
        self.add_stretch()

        # 2. Bottom Actions
        actions = Stack(orientation="horizontal")
        actions.add_stretch()

        apply_text = getattr(
            language_config, "APPLY_PARAMETER_BUTTON_TEXT", "Apply Settings"
        )
        self.apply_btn = Button(apply_text, variant="success")
        self.apply_btn.setObjectName("ApplySettingsBtn")
        self.apply_btn.setMinimumHeight(35)
        self.apply_btn.clicked.connect(self._on_apply_clicked)

        actions.add_item(self.apply_btn)
        self.add_widget(actions)

    def retranslate_ui(self):
        """Dynamically update all UI labels when the language is changed."""
        language_config.reload_language()

        # Try to update parent tab text
        parent_tab = self.parentWidget()
        if parent_tab:
            parent_tab_parent = parent_tab.parentWidget()
            from PySide6.QtWidgets import QTabWidget

            if isinstance(parent_tab_parent, QTabWidget):
                idx = parent_tab_parent.indexOf(parent_tab)
                if idx != -1:
                    parent_tab_parent.setTabText(
                        idx,
                        getattr(language_config, "SETTING_GENERAL_LABEL", "General"),
                    )
            elif isinstance(parent_tab, QTabWidget):
                idx = parent_tab.indexOf(self)
                if idx != -1:
                    parent_tab.setTabText(
                        idx,
                        getattr(language_config, "SETTING_GENERAL_LABEL", "General"),
                    )

        # Update labels and tooltips
        lang_label = getattr(language_config, "LANGUAGE_LABEL", "Language:")
        self.language_group.label.setText(lang_label)

        self.processing_format_group.label.setText(
            getattr(language_config, "PROCESS_FORMAT_LABEL", "Process Format")
        )
        self.processing_format_group.input.setToolTip(
            getattr(
                language_config,
                "PROCESS_FORMAT_DESCRIPTION",
                "Choose the image domain used by multi-frame processing.",
            )
        )

        thumb_label = getattr(language_config, "THUMBNAIL_LABEL", "Enable Thumbnails")
        thumb_tip = getattr(language_config, "THUMBNAIL_DESCRIPTION", "")
        self.thumb_cb.checkbox.setText(thumb_label)
        self.thumb_cb.checkbox.setToolTip(thumb_tip)

        auto_shutdown_label = getattr(
            language_config, "AUTO_SHUTDOWN_LABEL", "Enable Auto Shutdown"
        )
        auto_shutdown_tip = getattr(
            language_config,
            "AUTO_SHUTDOWN_DESCRIPTION",
            "Close the application after the configured period without user activity.",
        )
        self.auto_shutdown_cb.checkbox.setText(auto_shutdown_label)
        self.auto_shutdown_cb.checkbox.setToolTip(auto_shutdown_tip)
        self.auto_shutdown_minutes_group.label.setText(
            getattr(
                language_config,
                "AUTO_SHUTDOWN_TIMEOUT_LABEL",
                "Idle timeout (minutes)",
            )
        )

        apply_text = getattr(
            language_config, "APPLY_PARAMETER_BUTTON_TEXT", "Apply Settings"
        )
        self.apply_btn.setText(apply_text)

        # Translate Test Button when this page owns backend controls.
        if hasattr(self, "test_btn"):
            self.test_btn.setText(language_config.BTN_TEST_BACKEND_HARDWARE)

        # Update window title if possible
        main_win = self.window()
        if main_win:
            from config import APP_VERSION

            main_win.setWindowTitle(f"Pixel Refine - Version {APP_VERSION}")

        self.update_theme()
        self.update_device_dropdown_style()

    def update_theme(self):
        """Update checkbox styles and apply button variant styles dynamically on theme changes."""
        from resources.GenericUILibrary.theme import (
            create_checkbox_style,
            create_button_style,
        )

        style = create_checkbox_style()
        for cb in [
            getattr(self, "thumb_cb", None),
            getattr(self, "auto_shutdown_cb", None),
        ]:
            if cb is None:
                continue
            if hasattr(cb, "checkbox"):
                cb.checkbox.setStyleSheet(style)

        # Apply variant styling for buttons dynamically
        if hasattr(self, "apply_btn") and self.apply_btn:
            self.apply_btn.setStyleSheet(create_button_style("success"))

    def _scan_hardware_backend_options(self):
        """Enumerate physical hardware devices (CPU, iGPU, Dedicated GPU) without exposing API names."""
        options = [
            {
                "key": "cpu",
                "text": "CPU (Universal)",
                "device_type": "cpu",
                "backend": "cpu",
                "device_id": -1,
                "vendor": "cpu",
                "raw_name": "CPU (Universal)",
                "fallback_chain": ["cpu"],
            }
        ]

        try:
            try:
                vk_records = scan_vulkan_device_records()
            except Exception as e:
                print(f"[Hardware Scan] Failed to scan Vulkan devices: {e}")
                vk_records = []

            try:
                cuda_records = scan_cuda_device_records()
            except Exception as e:
                print(f"[Hardware Scan] Failed to scan CUDA devices: {e}")
                cuda_records = []

            # Filter out translation adapters (Dozen/D3D12)
            native_vk = [
                r for r in vk_records
                if not r.get("translation") and not is_translation_device(r)
            ]

            for record in native_vk:
                if record.get("device_type") == "PHYSICAL_DEVICE_TYPE_CPU":
                    continue

                dev_name = str(record.get("name", "")).strip()
                if not dev_name:
                    continue

                vendor = str(record.get("vendor") or "unknown").lower()
                vk_ordinal = int(record.get("ordinal", 0))
                dev_type = str(record.get("device_type", ""))

                is_igpu = (
                    dev_type == "PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU"
                    or vendor == "intel"
                    or "uhd" in dev_name.lower()
                    or "iris" in dev_name.lower()
                )

                selector = make_device_selector(record)
                fingerprint = str(
                    selector.get("fingerprint")
                    or f"{record.get('vendor_id')}:{record.get('device_id')}"
                )

                if is_igpu:
                    label = f"{dev_name} (iGPU)"
                    options.append(
                        {
                            "key": f"{fingerprint}|igpu",
                            "text": label,
                            "device_type": "igpu",
                            "backend": "vulkan",
                            "device_id": vk_ordinal,
                            "vulkan_device_id": vk_ordinal,
                            "vendor": vendor,
                            "raw_name": dev_name,
                            "fallback_chain": ["vulkan", "opengl", "cpu"],
                            "device_record": record,
                            "device_selector": selector,
                        }
                    )
                else:
                    # Discrete / Dedicated GPU
                    label = f"{dev_name} (Dedicated GPU)"
                    matching_cuda = None
                    if vendor == "nvidia" and cuda_records:
                        matching_cuda = next(
                            (
                                c for c in cuda_records
                                if c.get("name", "").lower() in dev_name.lower()
                                or dev_name.lower() in c.get("name", "").lower()
                            ),
                            cuda_records[0] if len(cuda_records) == 1 else None,
                        )

                    if vendor == "nvidia" and matching_cuda:
                        cuda_id = int(matching_cuda.get("ordinal", 0))
                        primary_backend = "cuda"
                        primary_id = cuda_id
                        fallback_chain = ["cuda", "vulkan", "opengl", "cpu"]
                    else:
                        cuda_id = None
                        primary_backend = "vulkan"
                        primary_id = vk_ordinal
                        fallback_chain = ["vulkan", "opengl", "cpu"]

                    options.append(
                        {
                            "key": f"{fingerprint}|dgpu",
                            "text": label,
                            "device_type": "dgpu",
                            "backend": primary_backend,
                            "device_id": primary_id,
                            "vulkan_device_id": vk_ordinal,
                            "cuda_device_id": cuda_id,
                            "vendor": vendor,
                            "raw_name": dev_name,
                            "fallback_chain": fallback_chain,
                            "device_record": record,
                            "device_selector": selector,
                        }
                    )

        except Exception as e:
            print(f"[Hardware Scan] Failed to scan hardware: {e}")

        return options

    def _migrate_saved_backend_option(self, options):
        """Map legacy backend-name labels to a physical hardware option."""
        saved_text = str(self.store.get("device_backend", "") or "")
        saved_key = str(self.store.get("device_backend_key", "") or "")

        # 1. Exact text match
        exact_text = next(
            (opt for opt in options if opt.get("text") == saved_text),
            None,
        )
        if exact_text is not None:
            self.store.set("device_backend_key", exact_text["key"])
            self.store.set("device_backend_arch", exact_text.get("backend", "cpu"))
            self.store.set("device_backend_id", exact_text.get("device_id", -1))
            self.store.set("device_fallback_chain", exact_text.get("fallback_chain", ["cpu"]))
            return

        # 2. Key match
        exact_key = next(
            (opt for opt in options if opt.get("key") == saved_key),
            None,
        )
        if exact_key is not None:
            self.store.set("device_backend", exact_key["text"])
            self.store.set("device_backend_arch", exact_key.get("backend", "cpu"))
            self.store.set("device_backend_id", exact_key.get("device_id", -1))
            self.store.set("device_fallback_chain", exact_key.get("fallback_chain", ["cpu"]))
            return

        # 3. Fuzzy migration from legacy strings (e.g. "Intel(R) UHD Graphics 620 — Vulkan")
        legacy = saved_text.lower()
        if "intel" in legacy or "uhd" in legacy or "iris" in legacy:
            target_opt = next((opt for opt in options if opt.get("vendor") == "intel"), None)
        elif "nvidia" in legacy or "geforce" in legacy or "mx150" in legacy:
            target_opt = next((opt for opt in options if opt.get("vendor") == "nvidia"), None)
        elif "cpu" in legacy:
            target_opt = options[0]
        else:
            target_opt = options[0]

        if target_opt is None:
            target_opt = options[0]

        self.store.set("device_backend", target_opt["text"])
        self.store.set("device_backend_key", target_opt["key"])
        self.store.set("device_backend_arch", target_opt.get("backend", "cpu"))
        self.store.set("device_backend_id", target_opt.get("device_id", -1))
        self.store.set("device_fallback_chain", target_opt.get("fallback_chain", ["cpu"]))
        if "device_selector" in target_opt:
            self.store.set("device_selector", target_opt["device_selector"])

    def _get_selected_backend_option(self):
        if not hasattr(self, "device_group") or not isinstance(
            self.device_group.input, QComboBox
        ):
            return None
        idx = self.device_group.input.currentIndex()
        data = self.device_group.input.itemData(idx)
        if isinstance(data, dict):
            return data
        text = self.device_group.input.currentText()
        return {
            "text": text,
            "backend": "cpu" if "cpu" in text.lower() else ("cuda" if "nvidia" in text.lower() else "vulkan"),
            "device_id": -1 if "cpu" in text.lower() else 0,
        }

    def _apply_selected_backend_to_process(self, option=None):
        if option is None:
            option = self._get_selected_backend_option()
        if not option:
            return

        import os
        from taichi_vision.backend_config import normalize_backend, BackendConfig, backend_env

        backend = normalize_backend(option.get("backend", "cpu"), allow_auto=False)
        device_id = int(option.get("device_id", -1))
        fallback_chain = option.get("fallback_chain", [backend])
        auto_fallback = bool(self.store.get("auto_fallback", True))

        active_backend = backend
        active_device_id = device_id
        if auto_fallback and fallback_chain:
            from taichi_vision.taichi_aot.capabilities import classify_device

            raw_name = option.get("raw_name", "") or option.get("text", "")
            for cand in fallback_chain:
                caps = classify_device(raw_name, cand)
                if caps.safe:
                    active_backend = cand
                    if cand in ("opengl", "cpu"):
                        active_device_id = 0 if cand == "opengl" else -1
                    elif cand == "vulkan":
                        active_device_id = option.get("vulkan_device_id", device_id)
                    elif cand == "cuda":
                        active_device_id = option.get("cuda_device_id", 0)
                    break

        vendor = str(option.get("vendor", "")).lower()
        self.store.set("device_backend", option.get("text", "CPU (Universal)"))
        self.store.set("device_backend_key", option.get("key", "cpu"))
        self.store.set("device_backend_arch", active_backend)
        self.store.set("device_backend_id", active_device_id)
        self.store.set("device_fallback_chain", fallback_chain)
        self.store.set("device_vendor", vendor)

        if active_backend == "cpu":
            self.store.set(
                "device_selector", {"vendor": "cpu", "name": "cpu universal"}
            )
        else:
            selector = option.get("device_selector")
            if not isinstance(selector, dict):
                selector = make_device_selector(
                    option.get("raw_name") or option.get("text")
                )
            self.store.set("device_selector", selector)

        canonical_config = BackendConfig(
            backend=active_backend,
            device_id=active_device_id if active_device_id >= 0 else 0,
            vendor=option.get("vendor", ""),
            device_name=option.get("raw_name", "") or option.get("text", ""),
            explicit=True,
            source="general_settings",
            strict=not auto_fallback,
        )
        os.environ.update(backend_env(canonical_config))
        os.environ["AOT_ARCH"] = active_backend
        os.environ["AOT_DEVICE"] = str(active_device_id if active_device_id >= 0 else 0)
        os.environ["PIXEL_REFINE_AOT_AUTO_FALLBACK"] = "1" if auto_fallback else "0"
        os.environ["PIXEL_REFINE_AOT_ALLOW_CPU_FALLBACK"] = "1" if auto_fallback else "0"
        if not auto_fallback:
            os.environ["AOT_STRICT_BACKEND"] = "1"
        else:
            os.environ.pop("AOT_STRICT_BACKEND", None)

        if vendor != "cpu" and vendor:
            os.environ["TARGET_VENDOR"] = vendor
            os.environ["ONNX_TARGET_VENDOR"] = vendor
        else:
            os.environ.pop("TARGET_VENDOR", None)
            os.environ.pop("ONNX_TARGET_VENDOR", None)

        if active_backend == "cuda":
            os.environ["CUDA_EXPECTED_NAME"] = str(option.get("raw_name", ""))
            os.environ["CUDA_DEVICE"] = str(active_device_id)
            os.environ["PIXEL_REFINE_CUDA_DEVICE"] = str(active_device_id)
        else:
            os.environ.pop("CUDA_EXPECTED_NAME", None)

        # Set up OpenGL ICD detection in environment if Intel device is selected or in chain
        if vendor == "intel" or "opengl" in fallback_chain:
            try:
                import glob
                base_repo = r"C:\WINDOWS\system32\DriverStore\FileRepository"
                for icd_cand in glob.glob(os.path.join(base_repo, "*iigd_dch*", "ig9icd64.dll")):
                    if os.path.exists(icd_cand):
                        os.environ["PIXEL_REFINE_OPENGL_ICD_LIBRARY"] = icd_cand
                        break
            except Exception:
                pass
            if vendor == "intel":
                os.environ["OPENGL_EXPECTED_VENDOR"] = "intel"
                os.environ["PIXEL_REFINE_OPENGL_EXPECTED_VENDOR"] = "intel"
                os.environ.pop("OPENGL_EXPECTED_NAME", None)
                os.environ.pop("PIXEL_REFINE_OPENGL_EXPECTED_NAME", None)

        os.environ["AOT_NATIVE_VULKAN_ONLY"] = "1"
        os.environ["AOT_SKIP_DOZEN"] = "1"

    def _get_backend_test_options(self):
        """Expand physical devices into individual backend candidates for testing."""
        if not hasattr(self, "device_group") or not isinstance(
            self.device_group.input, QComboBox
        ):
            return []
        options = []
        for i in range(self.device_group.input.count()):
            data = self.device_group.input.itemData(i)
            if not isinstance(data, dict):
                continue
            vendor = str(data.get("vendor", "")).lower()
            raw_name = str(data.get("raw_name", "") or data.get("text", ""))
            fingerprint = str((data.get("device_selector") or {}).get("fingerprint") or data.get("key", ""))
            vk_id = data.get("vulkan_device_id", data.get("device_id", 0))
            cuda_id = data.get("cuda_device_id", 0)

            if vendor == "cpu" or data.get("device_type") == "cpu":
                options.append(
                    {
                        "key": "cpu",
                        "text": "CPU (Universal)",
                        "backend": "cpu",
                        "device_id": -1,
                        "vendor": "cpu",
                        "raw_name": raw_name,
                    }
                )
            elif vendor == "nvidia":
                options.append(
                    {
                        "key": f"{fingerprint}|cuda",
                        "text": f"{raw_name} — CUDA",
                        "backend": "cuda",
                        "device_id": cuda_id,
                        "vendor": "nvidia",
                        "raw_name": raw_name,
                    }
                )
                options.append(
                    {
                        "key": f"{fingerprint}|vulkan",
                        "text": f"{raw_name} — Vulkan",
                        "backend": "vulkan",
                        "device_id": vk_id,
                        "vendor": "nvidia",
                        "raw_name": raw_name,
                    }
                )
                options.append(
                    {
                        "key": f"{fingerprint}|opengl",
                        "text": f"{raw_name} — OpenGL",
                        "backend": "opengl",
                        "device_id": 0,
                        "vendor": "nvidia",
                        "raw_name": raw_name,
                    }
                )
            elif vendor == "intel":
                options.append(
                    {
                        "key": f"{fingerprint}|vulkan",
                        "text": f"{raw_name} — Vulkan",
                        "backend": "vulkan",
                        "device_id": vk_id,
                        "vendor": "intel",
                        "raw_name": raw_name,
                    }
                )
                options.append(
                    {
                        "key": f"{fingerprint}|opengl",
                        "text": f"{raw_name} — OpenGL",
                        "backend": "opengl",
                        "device_id": 0,
                        "vendor": "intel",
                        "raw_name": raw_name,
                    }
                )
            else:
                # Generic GPU
                options.append(
                    {
                        "key": f"{fingerprint}|vulkan",
                        "text": f"{raw_name} — Vulkan",
                        "backend": "vulkan",
                        "device_id": vk_id,
                        "vendor": vendor,
                        "raw_name": raw_name,
                    }
                )
                options.append(
                    {
                        "key": f"{fingerprint}|opengl",
                        "text": f"{raw_name} — OpenGL",
                        "backend": "opengl",
                        "device_id": 0,
                        "vendor": vendor,
                        "raw_name": raw_name,
                    }
                )
        return options

    def _on_thumbnail_toggled(self, checked):
        self.store.set("create_thumbnail", bool(checked))
        if hasattr(self.store, "save_to_file"):
            self.store.save_to_file()
        from resources.GenericUILibrary import trigger_live_update

        trigger_live_update()

    def _update_auto_shutdown_timeout_state(self, checked):
        if hasattr(self, "auto_shutdown_minutes_group"):
            self.auto_shutdown_minutes_group.setEnabled(bool(checked))

    def _on_auto_shutdown_toggled(self, checked):
        self.store.set("auto_shutdown_enabled", bool(checked))
        self._update_auto_shutdown_timeout_state(checked)
        if hasattr(self.store, "save_to_file"):
            self.store.save_to_file()

    def _on_apply_clicked(self):
        """
        Final apply logic:
        1. Save language from FormGroup to store.
        2. Apply changes immediately in real-time.
        """
        new_lang = (
            self.language_group.input.currentText()
            if isinstance(self.language_group.input, QComboBox)
            else self.store.get("language", "English")
        )
        selected_backend_text = (
            self.device_group.input.currentText()
            if hasattr(self, "device_group")
            and isinstance(self.device_group.input, QComboBox)
            else self.store.get("device_backend", "CPU (Universal)")
        )
        backend_changed = selected_backend_text != self._initial_device_backend

        self.store.set("language", new_lang)

        if hasattr(self, "thumb_cb"):
            new_thumb = bool(self.thumb_cb.is_checked())
            self.store.set("create_thumbnail", new_thumb)

        if hasattr(self, "auto_shutdown_cb"):
            self.store.set(
                "auto_shutdown_enabled",
                bool(self.auto_shutdown_cb.is_checked()),
            )
        if hasattr(self, "auto_shutdown_minutes_group"):
            self.store.set(
                "auto_shutdown_minutes",
                int(self.auto_shutdown_minutes_group.get_value()),
            )

        if hasattr(self, "device_group") and isinstance(self.device_group.input, QComboBox):
            self._apply_selected_backend_to_process()

        if hasattr(self.store, "save_to_file"):
            self.store.save_to_file()

        language_config.reload_language(new_lang)
        self.retranslate_ui()

        main_win = self.window()
        if main_win:

            def broadcast_retranslate(widget):
                for child in widget.findChildren(QWidget):
                    if hasattr(child, "retranslate_ui") and child != self:
                        try:
                            child.retranslate_ui()
                        except Exception as e:
                            print(f"Error retranslating {child}: {e}")

            broadcast_retranslate(main_win)

        from resources.GenericUILibrary import Toast, trigger_live_update

        trigger_live_update()

        self._initial_language = new_lang
        self._initial_device_backend = selected_backend_text

        toast = Toast(
            getattr(language_config, "SETTINGS_SAVED", "Settings saved successfully!"),
            variant="success",
            parent=self.window(),
        )
        toast.show_toast(duration=3000)

        if backend_changed and hasattr(self, "device_group"):
            dialog = modal_confirm(
                language_config.MSG_BACKEND_EXIT_REQUIRED, self.window()
            )
            dialog.title_text.setText(language_config.EXIT_APPLICATION_APPLY_BACKEND_TITLE)
            dialog.yes_button.setText(language_config.EXIT_APPLICATION_YES)
            dialog.no_button.setText(language_config.EXIT_APPLICATION_NO)

            if dialog.exec() == dialog.DialogCode.Accepted:
                restart_application()

    def update_device_dropdown_style(self):
        """Update dropdown select style based on test support status."""
        if not hasattr(self, "device_group") or not isinstance(
            self.device_group.input, QComboBox
        ):
            return
        selected_text = self.device_group.input.currentText()
        test_results = self.store.get("backend_test_results", {})
        selected = self._get_selected_backend_option() or {}
        selected_key = selected.get("key", selected_text)

        status_record = test_results.get(
            selected_key, test_results.get(selected_text, "support")
        )
        status = (
            status_record.get("status", "support")
            if isinstance(status_record, dict)
            else status_record
        )

        from resources.GenericUILibrary.theme import get_theme, create_select_style

        theme = get_theme()

        if status == "disable":
            calm_red_bg = "rgba(220, 53, 69, 0.15)"
            calm_red_border = "rgba(220, 53, 69, 0.4)"
            style = f"""
                QComboBox {{
                    background-color: {calm_red_bg};
                    border: 1px solid {calm_red_border};
                    border-radius: {theme.radius_sm}px;
                    padding: 6px 10px;
                    font-size: {theme.font_md};
                    color: {theme.text_primary};
                }}
                QComboBox:hover {{
                    border-color: rgba(220, 53, 69, 0.8);
                }}
                QComboBox::drop-down {{
                    border: none;
                    padding-right: 5px;
                }}
                QComboBox QAbstractItemView {{
                    background-color: {theme.bg_primary};
                    border: 1px solid {theme.border_color};
                    selection-background-color: {theme.primary};
                    selection-color: {theme.text_white};
                }}
            """
            self.device_group.input.setStyleSheet(style)
        else:
            self.device_group.input.setStyleSheet(create_select_style())

        # Update popup list items (disable and style unsupported items)
        model = self.device_group.input.model()
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QColor, QBrush

        if model:
            is_standard_model = hasattr(model, "item")
            for i in range(self.device_group.input.count()):
                text = self.device_group.input.itemText(i)
                data = self.device_group.input.itemData(i)
                item_key = data.get("key", text) if isinstance(data, dict) else text
                item_record = test_results.get(
                    item_key, test_results.get(text, "support")
                )
                item_status = (
                    item_record.get("status", "support")
                    if isinstance(item_record, dict)
                    else item_record
                )

                if is_standard_model:
                    item = model.item(i)
                    if item:
                        if item_status == "disable":
                            item.setEnabled(False)
                            item.setBackground(
                                QBrush(QColor(220, 53, 69, 38))
                            )  # ~0.15 alpha calm pinkish-red
                            item.setForeground(
                                QBrush(QColor(220, 53, 69, 150))
                            )  # semi-transparent red text
                        else:
                            item.setEnabled(True)
                            item.setData(None, Qt.BackgroundRole)
                            item.setData(None, Qt.ForegroundRole)

    def _on_test_backends_clicked(self):
        """Test all available backend options using isolated subprocesses to prevent driver state corruption."""
        if not hasattr(self, "device_group") or not isinstance(
            self.device_group.input, QComboBox
        ):
            return

        import sys
        import os
        from config import PYTHON_INTERPRETER
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
        llvm20_python = os.path.join(project_root, "venv", "Scripts", "python.exe")
        if os.path.isfile(llvm20_python):
            # Hardware probes must use the same LLVM20 interpreter as the
            # production runtime; otherwise a system/legacy venv can import
            # Taichi LLVM15 before the target-qualified AOT bundle is tested.
            python_bin = llvm20_python
        else:
            configured_python = os.path.abspath(str(PYTHON_INTERPRETER))
            python_bin = (
                configured_python if os.path.exists(configured_python) else sys.executable
            )
        options = self._get_backend_test_options()
        if not options:
            return

        msg = (
            f"{language_config.MSG_HARDWARE_TEST_DEPTH}\n\n"
            f"• {language_config.LBL_FAST}: {language_config.MSG_HARDWARE_TEST_FAST}\n"
            f"• {language_config.LBL_DEEP}: {language_config.MSG_HARDWARE_TEST_DEEP}"
        )
        chooser = modal_confirm(msg, self.window())
        chooser.title_text.setText(language_config.LBL_ANALYSIS_MODE)
        chooser.yes_button.setText(language_config.LBL_FAST)
        chooser.yes_button.setFixedWidth(60)
        chooser.no_button.setText(language_config.LBL_DEEP)
        chooser.no_button.setFixedWidth(60)
        # Deep analysis is temporarily disabled while the native-driver
        # qualification matrix is being repaired.  Keep the choice visible
        # (rather than hiding it) so users understand that it is intentional.
        chooser.no_button.setEnabled(False)
        chooser.no_button.setToolTip(
            "Deep analysis is temporarily disabled while backend stability is being improved."
        )

        chosen_mode = [None]

        def choose_fast():
            chosen_mode[0] = "fast"
            chooser.accept()

        def choose_deep():
            if not chooser.no_button.isEnabled():
                return
            chosen_mode[0] = "deep"
            chooser.accept()

        try:
            chooser.yes_button.clicked.disconnect()
            chooser.no_button.clicked.disconnect()
        except Exception:
            pass
        chooser.yes_button.clicked.connect(choose_fast)
        chooser.no_button.clicked.connect(choose_deep)
        chooser.exec()

        if not chosen_mode[0]:
            return
        analysis_mode = chosen_mode[0]
        self._backend_test_mode = analysis_mode

        self.test_btn.setEnabled(False)
        mode_label = (
            language_config.LBL_FAST
            if analysis_mode == "fast"
            else language_config.LBL_DEEP
        )
        eta_placeholder = language_config.LBL_ETA.format("--:--")
        self.test_btn.setText(f"{language_config.LBL_TESTING}... {eta_placeholder}")
        initial_msg = (
            f"{mode_label}\n{language_config.LBL_HARDWARE_PREPARING}\n"
            f"0% · {eta_placeholder}"
        )
        self._backend_test_progress_dialog = HardwareProgressModal(
            title=language_config.LBL_HARDWARE_BACKEND_ANALYSIS,
            message=initial_msg,
            parent=self.window(),
            on_cancel=self._cancel_backend_testing,
        )
        self._backend_test_progress_dialog.show()

        self._backend_test_thread = QThread(self)
        self._backend_test_worker = HardwareBackendTestWorker(
            options,
            python_bin,
            analysis_mode=analysis_mode,
        )
        self._backend_test_worker.moveToThread(self._backend_test_thread)
        self._backend_test_thread.started.connect(self._backend_test_worker.run)
        self._backend_test_worker.progress.connect(self._on_backend_test_progress)
        self._backend_test_worker.log_line.connect(self._on_backend_test_log)
        self._backend_test_worker.finished.connect(self._on_backend_test_finished)
        self._backend_test_worker.finished.connect(self._backend_test_thread.quit)
        self._backend_test_worker.finished.connect(
            self._backend_test_worker.deleteLater
        )
        self._backend_test_thread.finished.connect(self._cleanup_backend_test_worker)
        self._backend_test_thread.finished.connect(
            self._backend_test_thread.deleteLater
        )
        self._backend_test_thread.start()

    def _cancel_backend_testing(self):
        if hasattr(self, "_backend_test_worker") and self._backend_test_worker:
            self._backend_test_worker.cancel()
        if (
            hasattr(self, "_backend_test_progress_dialog")
            and self._backend_test_progress_dialog
        ):
            try:
                self._backend_test_progress_dialog.reject()
            except Exception:
                pass
            self._backend_test_progress_dialog = None

        self.test_btn.setEnabled(True)
        self.test_btn.setText(language_config.BTN_TEST_BACKEND_HARDWARE)
        self.test_btn.setToolTip("")

        from resources.GenericUILibrary import Toast

        toast = Toast(
            language_config.MSG_BACKEND_TEST_CANCELLED,
            variant="secondary",
            parent=self.window(),
        )
        toast.show_toast(duration=2500)

    def _on_backend_test_log(self, line_text):
        dialog = getattr(self, "_backend_test_progress_dialog", None)
        if dialog is not None and hasattr(dialog, "append_log"):
            dialog.append_log(line_text)

    @staticmethod
    def _format_backend_eta(seconds):
        seconds = max(0, int(seconds))
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def _on_backend_test_progress(self, progress, backend_text, eta_seconds):
        mode = str(getattr(self, "_backend_test_mode", "fast")).lower()
        mode_label = (
            language_config.LBL_FAST if mode == "fast" else language_config.LBL_DEEP
        )
        eta = self._format_backend_eta(eta_seconds)
        eta_text = language_config.LBL_ETA.format(eta)
        self.test_btn.setText(
            f"{language_config.LBL_TESTING} {mode_label}... {progress}% · {eta_text}"
        )
        self.test_btn.setToolTip(f"{backend_text}\n{eta_text}")
        dialog = getattr(self, "_backend_test_progress_dialog", None)
        if dialog is not None:
            dialog.setValue(int(progress))
            dialog.setLabelText(
                f"{mode_label}\n{backend_text}\n{progress}% · {eta_text}"
            )

    def _on_backend_test_finished(self, test_results):
        self.store.set("backend_test_results", test_results)
        if hasattr(self.store, "save_to_file"):
            self.store.save_to_file()

        self.update_device_dropdown_style()

        self.test_btn.setEnabled(True)
        self.test_btn.setText(language_config.BTN_TEST_BACKEND_HARDWARE)
        self.test_btn.setToolTip("")
        progress_dialog = getattr(self, "_backend_test_progress_dialog", None)
        if progress_dialog is not None:
            progress_dialog.setValue(100)
            progress_dialog.close()
            progress_dialog.deleteLater()
            self._backend_test_progress_dialog = None

        # Show a per-GPU/per-backend compatibility matrix.
        summary = []
        details = []
        for result in test_results.values():
            if isinstance(result, dict):
                supported = result.get("status") == "support"
                score = (
                    f"{result.get('passed', 0)}/{result.get('total', 0)}"
                    if result.get("total", 0)
                    else language_config.LBL_INITIALIZATION_FAILED
                )
                renderer = (
                    result.get("renderer") or language_config.LBL_RENDERER_UNAVAILABLE
                )
                analysis_mode = str(result.get("analysis_mode", "deep")).lower()
                analysis_label = (
                    language_config.LBL_FAST
                    if analysis_mode == "fast"
                    else language_config.LBL_DEEP
                )
                summary.append(
                    f"{'✓' if supported else '✗'} "
                    f"{result.get('text', language_config.LBL_UNKNOWN)}: "
                    f"{analysis_label} {score} "
                    f"[{renderer}]"
                )
                if not supported and result.get("diagnostic"):
                    details.append(
                        f"{result.get('text', language_config.LBL_UNKNOWN)}:\n"
                        f"{result.get('diagnostic')}"
                    )

        summary_text = "\n".join(summary) or language_config.LBL_NO_BACKEND_RESULTS

        dialog = modal_confirm(
            summary_text,
            self.window(),
            width=620,
            height=350 if details else 240,
        )
        dialog.title_text.setText(language_config.LBL_BACKEND_COMPATIBILITY_RESULTS)

        content_widget = dialog.message_label.parentWidget()
        if content_widget and content_widget.layout():
            content_widget.layout().setDirection(QBoxLayout.Direction.TopToBottom)
            content_widget.layout().setContentsMargins(18, 14, 18, 12)
            content_widget.layout().setSpacing(10)

        if details:
            from PySide6.QtWidgets import QTextEdit

            log_box = QTextEdit()
            log_box.setReadOnly(True)
            log_box.setPlainText(
                f"{language_config.LBL_DIAGNOSTIC_LOGS}:\n\n" + "\n\n".join(details)
            )
            log_box.setFixedHeight(125)
            log_box.setStyleSheet(
                """
                QTextEdit {
                    background-color: #F8FAFC;
                    border: 1px solid #CBD5E1;
                    border-radius: 6px;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 11px;
                    color: #334155;
                    padding: 8px;
                }
            """
            )
            if content_widget and content_widget.layout():
                content_widget.layout().addWidget(log_box)

        dialog.yes_button.setText(language_config.BTN_OK)
        dialog.yes_button.setFixedWidth(60)
        dialog.no_button.hide()
        dialog.exec()

        # Toast result
        from resources.GenericUILibrary import Toast

        toast = Toast(
            language_config.MSG_BACKEND_TEST_FINISHED,
            variant="success",
            parent=self.window(),
        )
        toast.show_toast(duration=3000)

    def _cleanup_backend_test_worker(self):
        self._backend_test_worker = None
        self._backend_test_thread = None


def general_page():
    """Entry point for SettingPage.py"""
    return GeneralSettingsPage()


def load_general_settings():
    """
    Backward compatibility wrapper.
    Returns the current general settings from the store.
    """
    return get_general_store().get(None) or {}
