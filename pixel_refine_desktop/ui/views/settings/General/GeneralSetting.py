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
from taichi_library.device_selection import (
    make_device_selector,
    resolve_device_selector,
    scan_vulkan_device_records,
)


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
            return 8 if backend == "cpu" else 14
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
            backend = option.get("backend", "cpu")
            device_id = option.get("device_id", -1)
            vendor = str(option.get("vendor", "")).lower()
            success = False
            output = ""
            returncode = -1
            passed = total_tests = 0
            renderer = ""

            environment = os.environ.copy()
            environment.update(
                {
                    "PIXEL_REFINE_AOT_ARCH": backend,
                    "PIXEL_REFINE_AOT_DEVICE": str(device_id),
                    "PIXEL_REFINE_AOT_STRICT_BACKEND": "1",
                    "PIXEL_REFINE_AOT_ALLOW_CPU_FALLBACK": "0",
                    "PIXEL_REFINE_AOT_SKIP_DOZEN": "1",
                    "PIXEL_REFINE_INTEL_VULKAN_AUTO_QUALIFY": "0",
                    "VK_LOADER_DEBUG": "error",
                }
            )
            if backend == "vulkan" and vendor == "intel":
                # Compatibility testing is crash-isolated, so it may probe an
                # unqualified Intel driver without changing production policy.
                environment["PIXEL_REFINE_AOT_INTEL_PROBE"] = "1"
                environment["PIXEL_REFINE_AOT_ALLOW_UNSAFE_INTEL"] = "1"
            else:
                environment.pop("PIXEL_REFINE_AOT_INTEL_PROBE", None)
                environment.pop("PIXEL_REFINE_AOT_ALLOW_UNSAFE_INTEL", None)
                environment.pop("PIXEL_REFINE_AOT_INTEL_UNSAFE", None)
            if backend == "opengl":
                environment["PIXEL_REFINE_OPENGL_EXPECTED_VENDOR"] = vendor
                environment["PIXEL_REFINE_OPENGL_EXPECTED_NAME"] = str(
                    option.get("raw_name", "")
                )
            else:
                environment.pop("PIXEL_REFINE_OPENGL_EXPECTED_VENDOR", None)
                environment.pop("PIXEL_REFINE_OPENGL_EXPECTED_NAME", None)

            test_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../../../../../taichi_library/taichi_algorithm/"
                    "aot_py/test_comprehensif.py",
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
                        "../../../../../taichi_library/vulkan_probe.py",
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
                    environment["PIXEL_REFINE_AOT_CACHE"] = cache_dir
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
                                if elapsed >= 1500:
                                    process.kill()
                                    process.wait(timeout=10)
                                    raise subprocess.TimeoutExpired(command, 1500)

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
                    json_text = output[output.find("{") :]
                    payload = json.loads(json_text)
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
                    match = re.search(r"Results:\s*(\d+)\s*/\s*(\d+)", output)
                    if match:
                        passed, total_tests = map(int, match.groups())
                    renderer_match = re.search(
                        r"Runtime initialized on '[^']+'\s*\((.+)\)\s*$",
                        output,
                        re.MULTILINE,
                    )
                    if renderer_match:
                        renderer = renderer_match.group(1).strip()
                    else:
                        mismatch = re.search(
                            r"Windows created the context on '([^']+)'",
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

    def __init__(self, title="Hardware Backend Analysis", message="", parent=None, on_cancel=None):
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
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #E2E8F0;
                border: 1px solid #CBD5E1;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #2ECC71;
                border-radius: 4px;
            }
        """)

        # Live Scrollable Log Box
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Live testing output logs...")
        self.log_box.setFixedHeight(130)
        self.log_box.setStyleSheet("""
            QTextEdit {
                background-color: #0F172A;
                border: 1px solid #334155;
                border-radius: 6px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                color: #38BDF8;
                padding: 8px;
            }
        """)

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

        # Themes Selection temporarily disabled.
        # theme_label = "Theme:"
        # self.theme_group = FormGroup(label=theme_label, input_type="select")
        # if isinstance(self.theme_group.input, QComboBox):
        #     self.theme_group.input.addItems(["Light Theme", "Dark Theme"])
        # self.theme_group.bind_store(self.store, "theme")
        # form.add_row(self.theme_group)

        hardware_backends = self._scan_hardware_backend_options()
        self._migrate_saved_backend_option(hardware_backends)
        self._initial_device_backend = self.store.get(
            "device_backend", "CPU (Universal)"
        )

        # Device Selection Dropdown
        device_label = getattr(
            language_config,
            "DEVICE_ACCELERATION_LABEL",
            "Accelerated Hardware Backend:",
        )
        self.device_group = FormGroup(
            label=device_label, input_type="select", auto_sync=False
        )
        if isinstance(self.device_group.input, QComboBox):
            for option in hardware_backends:
                self.device_group.input.addItem(option["text"], option)
            self.device_group.input.currentTextChanged.connect(
                self.update_device_dropdown_style
            )
        self.device_group.bind_store(self.store, "device_backend")
        form.add_row(self.device_group)
        self._apply_selected_backend_to_process()

        # Uji Backend Hardware Button
        self.test_btn = Button("Uji Backend Hardware", variant="secondary")
        self.test_btn.setMinimumHeight(35)
        self.test_btn.clicked.connect(self._on_test_backends_clicked)
        form.add_row(self.test_btn)

        # Initial styling update
        self.update_device_dropdown_style()

        # Thumbnails
        thumb_label = getattr(language_config, "THUMBNAIL_LABEL", "Enable Thumbnails")
        thumb_tip = getattr(language_config, "THUMBNAIL_DESCRIPTION", "")
        self.thumb_cb = Checkbox(thumb_label, auto_sync=True)
        self.thumb_cb.checkbox.setToolTip(thumb_tip)
        self.thumb_cb.bind_store(self.store, "create_thumbnail")
        self.thumb_cb.toggled.connect(self._on_thumbnail_toggled)
        form.add_row(self.thumb_cb)

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

        thumb_label = getattr(language_config, "THUMBNAIL_LABEL", "Enable Thumbnails")
        thumb_tip = getattr(language_config, "THUMBNAIL_DESCRIPTION", "")
        self.thumb_cb.checkbox.setText(thumb_label)
        self.thumb_cb.checkbox.setToolTip(thumb_tip)

        apply_text = getattr(
            language_config, "APPLY_PARAMETER_BUTTON_TEXT", "Apply Settings"
        )
        self.apply_btn.setText(apply_text)

        # Translate Test Button
        lang_str = getattr(language_config, "LANGUAGE", "english").lower()
        if lang_str == "indonesian":
            test_text = "Uji Backend Hardware"
        elif lang_str == "melayu":
            test_text = "Uji Backend Perkakasan"
        elif lang_str == "china traditional":
            test_text = "测试硬件后端"
        else:
            test_text = "Test Hardware Backend"
        self.test_btn.setText(test_text)

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
        for cb in [self.thumb_cb]:
            if hasattr(cb, "checkbox"):
                cb.checkbox.setStyleSheet(style)

        # Apply variant styling for buttons dynamically
        if hasattr(self, "apply_btn") and self.apply_btn:
            self.apply_btn.setStyleSheet(create_button_style("success"))
        if hasattr(self, "test_btn") and self.test_btn:
            self.test_btn.setStyleSheet(create_button_style("secondary"))
        self.update_device_dropdown_style()

    def _scan_hardware_backend_options(self):
        options = [
            {
                "key": "cpu",
                "text": "CPU (Universal)",
                "backend": "cpu",
                "device_id": -1,
                "vendor": "cpu",
            }
        ]
        allowed_ids = self.store.get("allowed_backend_ids", [])

        try:
            devices = scan_vulkan_device_records()
            if devices:
                for record in devices:
                    idx = int(record["ordinal"])
                    dev = str(record.get("name") or "")
                    if not dev:
                        continue

                    # Filter by allowed device IDs if the list is not empty
                    if allowed_ids and idx not in allowed_ids:
                        continue

                    # Native Vulkan only: Dozen is Vulkan-on-D3D12 and has a
                    # different descriptor/pipeline ABI from native Intel
                    # Vulkan.  Keep native Intel and NVIDIA ICDs visible.
                    if record.get("translation"):
                        continue

                    selector = make_device_selector(record)
                    fingerprint = str(
                        selector.get("fingerprint")
                        or f"{record.get('vendor_id')}:{record.get('device_id')}"
                    )
                    vendor = str(record.get("vendor") or "unknown").lower()
                    for backend, backend_label in (
                        ("vulkan", "Vulkan"),
                        ("opengl", "OpenGL"),
                    ):
                        if backend == "vulkan" and vendor == "intel":
                            continue
                        if backend == "opengl" and vendor == "nvidia":
                            continue
                        options.append(
                            {
                                "key": f"{fingerprint}|{backend}",
                                "text": f"{dev} — {backend_label}",
                                "backend": backend,
                                "device_id": idx,
                                "vendor": vendor,
                                "raw_name": dev,
                                "device_record": record,
                                "device_selector": selector,
                            }
                        )
        except Exception as e:
            print(f"[Hardware Scan] Failed to scan hardware: {e}")

        return options

    def _migrate_saved_backend_option(self, options):
        """Map legacy GPU-only labels to an explicit GPU/backend pair."""
        saved_text = str(self.store.get("device_backend", "") or "")
        saved_key = str(self.store.get("device_backend_key", "") or "")
        saved_arch = str(self.store.get("device_backend_arch", "cpu") or "cpu").lower()
        exact_text = next(
            (option for option in options if option.get("text") == saved_text),
            None,
        )
        if exact_text is not None:
            self.store.set("device_backend_key", exact_text["key"])
            return
        exact_key = next(
            (option for option in options if option.get("key") == saved_key),
            None,
        )
        if exact_key is not None and (
            saved_key != "cpu" or "cpu" in saved_text.lower()
        ):
            self.store.set("device_backend", exact_key["text"])
            return
        legacy = saved_text.lower()
        preferred_arch = saved_arch
        if preferred_arch not in ("vulkan", "opengl"):
            preferred_arch = (
                "vulkan" if ("nvidia" in legacy or "geforce" in legacy) else "opengl"
            )
        saved_selector = self.store.get("device_selector", {})
        resolved_id = None
        if isinstance(saved_selector, dict):
            records = [
                option.get("device_record")
                for option in options
                if isinstance(option.get("device_record"), dict)
            ]
            unique_records = {int(record["ordinal"]): record for record in records}
            resolved_id = resolve_device_selector(
                saved_selector,
                list(unique_records.values()),
                self.store.get("device_backend_id", None),
            )
        migrated = next(
            (
                option
                for option in options
                if option.get("backend") == preferred_arch
                and (
                    (resolved_id is not None and option.get("device_id") == resolved_id)
                    or str(option.get("raw_name", "")).lower() in legacy
                )
            ),
            options[0],
        )
        self.store.set("device_backend", migrated["text"])
        self.store.set("device_backend_key", migrated["key"])

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
            "backend": "cpu" if text == "CPU (Universal)" else ("opengl" if "intel" in text.lower() else "vulkan"),
            "device_id": idx - 1,
        }

    def _apply_selected_backend_to_process(self):
        option = self._get_selected_backend_option()
        if not option:
            return

        import os

        backend = option.get("backend", "cpu")
        device_id = int(option.get("device_id", -1))
        self.store.set("device_backend", option.get("text", "CPU (Universal)"))
        self.store.set("device_backend_key", option.get("key", "cpu"))
        self.store.set("device_backend_arch", backend)
        self.store.set("device_backend_id", device_id)
        if backend == "cpu":
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

        os.environ["PIXEL_REFINE_AOT_ARCH"] = backend
        os.environ["PIXEL_REFINE_AOT_DEVICE"] = str(device_id)
        os.environ["PIXEL_REFINE_AOT_STRICT_BACKEND"] = "1"
        if backend == "opengl":
            os.environ["PIXEL_REFINE_OPENGL_EXPECTED_VENDOR"] = str(
                option.get("vendor", "")
            ).lower()
            os.environ["PIXEL_REFINE_OPENGL_EXPECTED_NAME"] = str(
                option.get("raw_name", "")
            )
        else:
            os.environ.pop("PIXEL_REFINE_OPENGL_EXPECTED_VENDOR", None)
            os.environ.pop("PIXEL_REFINE_OPENGL_EXPECTED_NAME", None)
        # This is a selection policy for the Vulkan loader/runtime; it does
        # not uninstall or modify any Windows display driver.  The native ICD
        # remains selectable while Dozen/D3D12 devices are excluded above.
        os.environ["PIXEL_REFINE_AOT_NATIVE_VULKAN_ONLY"] = "1"
        os.environ["PIXEL_REFINE_AOT_SKIP_DOZEN"] = "1"

    def _get_backend_test_options(self):
        if not hasattr(self, "device_group") or not isinstance(
            self.device_group.input, QComboBox
        ):
            return []
        options = []
        for i in range(self.device_group.input.count()):
            data = self.device_group.input.itemData(i)
            if isinstance(data, dict):
                options.append(data)
            else:
                text = self.device_group.input.itemText(i)
                options.append(
                    {
                        "text": text,
                        "backend": "cpu" if text == "CPU (Universal)" else ("opengl" if "intel" in text.lower() else "vulkan"),
                        "device_id": i - 1,
                    }
                )
        return options

    def _on_thumbnail_toggled(self, checked):
        self.store.set("create_thumbnail", bool(checked))
        if hasattr(self.store, "save_to_file"):
            self.store.save_to_file()
        from resources.GenericUILibrary import trigger_live_update
        trigger_live_update()

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
            if isinstance(self.device_group.input, QComboBox)
            else self.store.get("device_backend", "CPU (Universal)")
        )
        backend_changed = selected_backend_text != self._initial_device_backend

        self.store.set("language", new_lang)

        if hasattr(self, "thumb_cb"):
            new_thumb = bool(self.thumb_cb.is_checked())
            self.store.set("create_thumbnail", new_thumb)

        if isinstance(self.device_group.input, QComboBox):
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

        if backend_changed:
            confirm_message = (
                "Perubahan Accelerated Hardware Backend memerlukan restart aplikasi.\n\n"
                "Restart sekarang?"
            )
            if getattr(language_config, "LANGUAGE", "english").lower() != "indonesian":
                confirm_message = (
                    "Changes to Accelerated Hardware Backend require an application restart.\n\n"
                    "Restart now?"
                )

            dialog = modal_confirm(confirm_message, self.window())
            dialog.title_text.setText("Restart Required")
            dialog.yes_button.setText("Yes")
            dialog.no_button.setText("No")

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

        python_bin = (
            PYTHON_INTERPRETER if os.path.exists(PYTHON_INTERPRETER) else sys.executable
        )
        options = self._get_backend_test_options()
        if not options:
            return

        lang_str = getattr(language_config, "LANGUAGE", "english").lower()
        is_indonesian = lang_str == "indonesian"

        msg = (
            "Pilih kedalaman pengujian backend hardware:\n\n"
            "• Fast: pemeriksaan native inti (~1 menit).\n"
            "• Deep: 29 pengujian & stress pipeline 24.1 MP."
            if is_indonesian
            else (
                "Choose hardware-backend test depth:\n\n"
                "• Fast: core native smoke checks (~1 min).\n"
                "• Deep: 29 checks & 24.1 MP stress pipeline."
            )
        )
        chooser = modal_confirm(msg, self.window())
        chooser.title_text.setText(
            "Pilih Mode Analisis" if is_indonesian else "Choose Analysis Mode"
        )
        chooser.yes_button.setText("Fast")
        chooser.yes_button.setFixedWidth(60)
        chooser.no_button.setText("Deep")
        chooser.no_button.setFixedWidth(60)

        chosen_mode = [None]

        def choose_fast():
            chosen_mode[0] = "fast"
            chooser.accept()

        def choose_deep():
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
        self.test_btn.setText(
            "Menguji... ETA menghitung"
            if is_indonesian
            else "Testing... calculating ETA"
        )
        dialog_title = (
            "Analisis Backend Hardware"
            if is_indonesian
            else "Hardware Backend Analysis"
        )
        initial_msg = (
            f"{analysis_mode.title()} Analysis\nMenyiapkan...\n0% · ETA --:--"
            if is_indonesian
            else f"{analysis_mode.title()} Analysis\nPreparing...\n0% · ETA --:--"
        )
        self._backend_test_progress_dialog = HardwareProgressModal(
            title=dialog_title,
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
        if hasattr(self, "_backend_test_progress_dialog") and self._backend_test_progress_dialog:
            try:
                self._backend_test_progress_dialog.reject()
            except Exception:
                pass
            self._backend_test_progress_dialog = None

        self.test_btn.setEnabled(True)
        lang_str = getattr(language_config, "LANGUAGE", "english").lower()
        self.test_btn.setText(
            "Uji Backend Hardware" if lang_str == "indonesian" else "Test Hardware Backend"
        )
        self.test_btn.setToolTip("")

        from resources.GenericUILibrary import Toast
        toast = Toast(
            "Pengujian backend dibatalkan." if lang_str == "indonesian" else "Backend testing cancelled.",
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
        lang_str = getattr(language_config, "LANGUAGE", "english").lower()
        prefix = "Menguji" if lang_str == "indonesian" else "Testing"
        mode = str(getattr(self, "_backend_test_mode", "fast")).title()
        eta = self._format_backend_eta(eta_seconds)
        self.test_btn.setText(f"{prefix} {mode}... {progress}% · ETA {eta}")
        self.test_btn.setToolTip(f"{backend_text}\nETA {eta}")
        dialog = getattr(self, "_backend_test_progress_dialog", None)
        if dialog is not None:
            dialog.setValue(int(progress))
            dialog.setLabelText(
                f"{mode} Analysis\n{backend_text}\n" f"{progress}% · ETA {eta}"
            )

    def _on_backend_test_finished(self, test_results):
        self.store.set("backend_test_results", test_results)
        if hasattr(self.store, "save_to_file"):
            self.store.save_to_file()

        self.update_device_dropdown_style()

        # Restore button text
        lang_str = getattr(language_config, "LANGUAGE", "english").lower()
        if lang_str == "indonesian":
            test_text = "Uji Backend Hardware"
        elif lang_str == "melayu":
            test_text = "Uji Backend Perkakasan"
        elif lang_str == "china traditional":
            test_text = "测试硬件后端"
        else:
            test_text = "Test Hardware Backend"

        self.test_btn.setEnabled(True)
        self.test_btn.setText(test_text)
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
        fully_compatible = True
        for result in test_results.values():
            if isinstance(result, dict):
                supported = result.get("status") == "support"
                fully_compatible = fully_compatible and supported
                score = (
                    f"{result.get('passed', 0)}/{result.get('total', 0)}"
                    if result.get("total", 0)
                    else "initialization failed"
                )
                renderer = result.get("renderer") or "renderer unavailable"
                analysis_mode = str(result.get("analysis_mode", "deep")).upper()
                summary.append(
                    f"{'✓' if supported else '✗'} "
                    f"{result.get('text', 'Unknown')}: "
                    f"{analysis_mode} {score} "
                    f"[{renderer}]"
                )
                if not supported and result.get("diagnostic"):
                    details.append(
                        f"{result.get('text', 'Unknown')}:\n"
                        f"{result.get('diagnostic')}"
                    )

        dialog_title = (
            "Hasil Kompatibilitas Backend"
            if lang_str == "indonesian"
            else "Backend Compatibility Results"
        )
        summary_text = "\n".join(summary) or "No backend results."

        dialog = modal_confirm(
            summary_text,
            self.window(),
            width=620,
            height=350 if details else 240,
        )
        dialog.title_text.setText(dialog_title)

        content_widget = dialog.message_label.parentWidget()
        if content_widget and content_widget.layout():
            content_widget.layout().setDirection(QBoxLayout.Direction.TopToBottom)
            content_widget.layout().setContentsMargins(18, 14, 18, 12)
            content_widget.layout().setSpacing(10)

        if details:
            from PySide6.QtWidgets import QTextEdit

            log_box = QTextEdit()
            log_box.setReadOnly(True)
            log_box.setPlainText("Diagnostic Logs:\n\n" + "\n\n".join(details))
            log_box.setFixedHeight(125)
            log_box.setStyleSheet("""
                QTextEdit {
                    background-color: #F8FAFC;
                    border: 1px solid #CBD5E1;
                    border-radius: 6px;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 11px;
                    color: #334155;
                    padding: 8px;
                }
            """)
            if content_widget and content_widget.layout():
                content_widget.layout().addWidget(log_box)

        dialog.yes_button.setText("OK")
        dialog.yes_button.setFixedWidth(60)
        dialog.no_button.hide()
        dialog.exec()

        # Toast result
        from resources.GenericUILibrary import Toast

        toast_msg = (
            "Pengujian backend selesai! Hasil disimpan."
            if lang_str == "indonesian"
            else "Backend testing finished! Results saved."
        )
        toast = Toast(toast_msg, variant="success", parent=self.window())
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
