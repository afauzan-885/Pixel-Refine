from PySide6.QtWidgets import QWidget, QMessageBox, QComboBox
from PySide6.QtCore import Qt

from resources.GenericUILibrary import (
    Container,
    Stack,
    FormRow,
    FormGroup,
    Select,
    Checkbox,
    Button,
    SyncMixin,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from .general_store import get_general_store
from .helpers import restart_application, sync_algorithm_settings


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

        # Themes Selection
        theme_label = "Theme:"
        self.theme_group = FormGroup(label=theme_label, input_type="select")
        if isinstance(self.theme_group.input, QComboBox):
            self.theme_group.input.addItems(["Light Theme", "Dark Theme"])
        self.theme_group.bind_store(self.store, "theme")
        form.add_row(self.theme_group)

        # Dynamic Hardware Scan for Dropdown
        hardware_backends = ["CPU (Universal)"]
        try:
            from taichi_library.taichi_aot.engine import AOTEngine
            engine = AOTEngine()
            scanned = engine.backend.scan_devices()
            if scanned:
                devices = [d.strip() for d in scanned.split(";")]
                for dev in devices:
                    if not dev:
                        continue
                    # Parse device backend capabilities
                    if "nvidia" in dev.lower() or "geforce" in dev.lower():
                        # Dedicate GPU: Vulkan & D3D12/OpenGL/CUDA
                        hardware_backends.append(f"{dev} (CUDA)")
                        hardware_backends.append(f"{dev} (Vulkan)")
                        hardware_backends.append(f"{dev} (OpenGL)")
                    elif "intel" in dev.lower():
                        # Integrated GPU: Vulkan & D3D12/OpenGL
                        hardware_backends.append(f"{dev} (Vulkan)")
                        hardware_backends.append(f"{dev} (OpenGL)")
                    else:
                        hardware_backends.append(f"{dev} (Vulkan)")
        except Exception as e:
            print(f"[Hardware Scan] Failed to scan hardware: {e}")

        # Device Selection Dropdown
        device_label = getattr(language_config, "DEVICE_ACCELERATION_LABEL", "Accelerated Hardware Backend:")
        self.device_group = FormGroup(label=device_label, input_type="select", auto_sync=False)
        if isinstance(self.device_group.input, QComboBox):
            self.device_group.input.addItems(hardware_backends)
            self.device_group.input.currentTextChanged.connect(self.update_device_dropdown_style)
        self.device_group.bind_store(self.store, "device_backend")
        form.add_row(self.device_group)

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
                    parent_tab_parent.setTabText(idx, getattr(language_config, "SETTING_GENERAL_LABEL", "General"))
            elif isinstance(parent_tab, QTabWidget):
                idx = parent_tab.indexOf(self)
                if idx != -1:
                    parent_tab.setTabText(idx, getattr(language_config, "SETTING_GENERAL_LABEL", "General"))

        # Update labels and tooltips
        lang_label = getattr(language_config, "LANGUAGE_LABEL", "Language:")
        self.language_group.label.setText(lang_label)

        thumb_label = getattr(language_config, "THUMBNAIL_LABEL", "Enable Thumbnails")
        thumb_tip = getattr(language_config, "THUMBNAIL_DESCRIPTION", "")
        self.thumb_cb.checkbox.setText(thumb_label)
        self.thumb_cb.checkbox.setToolTip(thumb_tip)

        apply_text = getattr(language_config, "APPLY_PARAMETER_BUTTON_TEXT", "Apply Settings")
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
        from resources.GenericUILibrary.theme import create_checkbox_style, create_button_style
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

    def _on_apply_clicked(self):
        """
        Final apply logic:
        1. Save language from FormGroup to store.
        2. Apply changes immediately in real-time.
        """
        if isinstance(self.language_group.input, QComboBox):
            new_lang = self.language_group.input.currentText()
            self.store.set("language", new_lang)
            
            # Apply Theme
            if isinstance(self.theme_group.input, QComboBox):
                new_theme_str = self.theme_group.input.currentText()
                self.store.set("theme", new_theme_str)
                from resources.GenericUILibrary.theme import set_theme, DarkTheme, LightTheme
                if new_theme_str == "Dark Theme":
                    set_theme(DarkTheme())
                else:
                    set_theme(LightTheme())

            # Apply Device Selection on Apply Settings Click
            if isinstance(self.device_group.input, QComboBox):
                new_device = self.device_group.input.currentText()
                self.store.set("device_backend", new_device)

            # Explicitly force save general store to disk
            if hasattr(self.store, "save_to_file"):
                self.store.save_to_file()

            # Dynamically reload language config and translate this view
            language_config.reload_language(new_lang)
            self.retranslate_ui()
            
            # Broadcast translation to the entire application hierarchy
            main_win = self.window()
            if main_win:
                # Re-apply global stylesheet with new theme colors
                from resources.styles.stylesheet import stylesheet_global_page
                main_win.setStyleSheet(stylesheet_global_page())

                # Recursively call retranslate_ui on all child widgets
                def broadcast_retranslate(widget):
                    for child in widget.findChildren(QWidget):
                        if hasattr(child, "retranslate_ui") and child != self:
                            try:
                                child.retranslate_ui()
                            except Exception as e:
                                print(f"Error retranslating {child}: {e}")
                broadcast_retranslate(main_win)
            
            # Trigger dedicated live decorator updates
            from resources.GenericUILibrary import trigger_live_update
            trigger_live_update()
            trigger_live_update("update_theme")
            
            self._initial_language = new_lang
            
            from resources.GenericUILibrary import Toast
            toast = Toast(
                getattr(language_config, "SETTINGS_SAVED", "Settings saved successfully!"),
                variant="success",
                parent=self.window()
            )
            toast.show_toast(duration=3000)
        else:
            from resources.GenericUILibrary import Toast
            toast = Toast(
                getattr(language_config, "SETTINGS_SAVED", "Settings saved successfully!"),
                variant="success",
                parent=self.window()
            )
            toast.show_toast(duration=3000)

    def update_device_dropdown_style(self):
        """Update dropdown select style based on test support status."""
        if not hasattr(self, "device_group") or not isinstance(self.device_group.input, QComboBox):
            return
        selected_text = self.device_group.input.currentText()
        test_results = self.store.get("backend_test_results", {})
        
        status = test_results.get(selected_text, "support")
        
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
                item_status = test_results.get(text, "support")
                
                if is_standard_model:
                    item = model.item(i)
                    if item:
                        if item_status == "disable":
                            item.setEnabled(False)
                            item.setBackground(QBrush(QColor(220, 53, 69, 38)))  # ~0.15 alpha calm pinkish-red
                            item.setForeground(QBrush(QColor(220, 53, 69, 150))) # semi-transparent red text
                        else:
                            item.setEnabled(True)
                            item.setData(None, Qt.BackgroundRole)
                            item.setData(None, Qt.ForegroundRole)

    def _on_test_backends_clicked(self):
        """Test all available backend options using isolated subprocesses to prevent driver state corruption."""
        if not hasattr(self, "device_group") or not isinstance(self.device_group.input, QComboBox):
            return
            
        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing..." if getattr(language_config, "LANGUAGE", "english").lower() != "indonesian" else "Menguji...")
        
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
        test_results = {}
        count = self.device_group.input.count()
        options = [self.device_group.input.itemText(i) for i in range(count)]
        
        import subprocess
        import sys
        import os
        from config import PYTHON_INTERPRETER
        
        python_bin = PYTHON_INTERPRETER if os.path.exists(PYTHON_INTERPRETER) else sys.executable
        
        for option in options:
            success = False
            if option == "CPU (Universal)":
                success = True
            elif "(opengl)" in option.lower():
                success = False
            else:
                try:
                    from taichi_library.taichi_aot.engine import AOTEngine
                    engine = AOTEngine()
                    scanned = engine.backend.scan_devices()
                    devices = [d.strip() for d in scanned.split(";")]
                    
                    device_idx = -1
                    for idx, dev in enumerate(devices):
                        if dev and dev.lower() in option.lower():
                            device_idx = idx
                            break
                    
                    if device_idx != -1:
                        arch = "vulkan"
                        if "(cuda)" in option.lower():
                            arch = "cuda"
                        
                        # Run testing logic in an isolated python subprocess
                        test_script = f"""
import sys
try:
    from taichi_library.taichi_aot.engine import AOTEngine
    import numpy as np
    test_inst = AOTEngine(arch='{arch}', device_id={device_idx})
    buf = test_inst.allocate((1,), dtype=np.int32)
    buf.destroy()
    sys.exit(0)
except Exception as e:
    sys.exit(1)
"""
                        # Execute python process
                        res = subprocess.run(
                            [python_bin, "-c", test_script],
                            capture_output=True,
                            text=True,
                            timeout=15
                        )
                        if res.returncode == 0:
                            success = True
                        else:
                            print(f"[Test Subprocess Backend] {option} failed with stdout: {res.stdout}, stderr: {res.stderr}")
                except Exception as e:
                    print(f"[Test Backend] {option} main thread exception: {e}")
                    success = False
            
            test_results[option] = "support" if success else "disable"
            
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
        
        # Toast result
        from resources.GenericUILibrary import Toast
        toast_msg = "Pengujian backend selesai! Hasil disimpan." if lang_str == "indonesian" else "Backend testing finished! Results saved."
        toast = Toast(
            toast_msg,
            variant="success",
            parent=self.window()
        )
        toast.show_toast(duration=3000)


def general_page():
    """Entry point for SettingPage.py"""
    return GeneralSettingsPage()


def load_general_settings():
    """
    Backward compatibility wrapper.
    Returns the current general settings from the store.
    """
    return get_general_store().get(None) or {}
