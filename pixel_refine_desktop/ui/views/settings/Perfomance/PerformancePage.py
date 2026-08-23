"""Performance settings, including target backend selection and validation."""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QComboBox, QSizePolicy

from resources.GenericUILibrary import Button, Checkbox, FormGroup, FormRow, Stack
from pixel_refine_desktop.ui.views.settings.General.GeneralSetting import (
    GeneralSettingsPage,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from resources.GenericUILibrary.modals import modal_confirm
from pixel_refine_desktop.ui.views.settings.General.helpers import restart_application


class PerformanceSettingsPage(GeneralSettingsPage):
    """Backend controls sharing the General page's discovery/test pipeline.

    The implementation deliberately inherits the established backend resolver
    and hardware test worker. Only the presentation and apply surface move to
    the Performance tab, so persisted keys and runtime selection stay stable.
    """

    def _setup_ui(self):
        form = FormRow()

        hardware_backends = self._scan_hardware_backend_options()
        self._migrate_saved_backend_option(hardware_backends)

        device_label = getattr(
            language_config,
            "DEVICE_ACCELERATION_LABEL",
            "GPU Acceleration",
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
        self._restore_saved_backend_selection(hardware_backends)
        form.add_row(self.device_group)
        self._apply_selected_backend_to_process()

        auto_fb_label = getattr(language_config, "LBL_AUTO_FALLBACK", "Auto Fallback")
        auto_fb_tip = getattr(
            language_config,
            "LBL_AUTO_FALLBACK_TIP",
            "When enabled, automatically fall back through CUDA, Vulkan, OpenGL, "
            "then CPU if the selected backend is unavailable.",
        )
        self.auto_fallback_cb = Checkbox(auto_fb_label, auto_sync=True)
        self.auto_fallback_cb.checkbox.setToolTip(auto_fb_tip)
        self.auto_fallback_cb.bind_store(self.store, "auto_fallback")
        form.add_row(self.auto_fallback_cb)

        self.test_btn = Button(
            language_config.BTN_TEST_BACKEND_HARDWARE, variant="secondary"
        )
        self.test_btn.setMinimumHeight(35)
        self.test_btn.clicked.connect(self._on_test_backends_clicked)
        form.add_row(self.test_btn)

        # Large-image residency policy.  Keep these controls directly below
        # the backend test: they are live performance controls and do not
        # require a backend restart or an Apply action.
        self.compute_block_cb = Checkbox("Enable Compute Blocks", auto_sync=True)
        self.compute_block_cb.checkbox.setToolTip(
            "Process large images in bounded blocks to reduce VRAM/RAM pressure."
        )
        self.compute_block_cb.bind_store(self.store, "compute_block_enabled")
        form.add_row(self.compute_block_cb)

        self.compute_block_size_group = FormGroup(
            label="Compute Block Size", input_type="select", auto_sync=True
        )
        self.compute_block_size_group.input.addItems(["512", "768", "1024", "2048"])
        self.compute_block_size_group.bind_store(self.store, "compute_block_size")
        form.add_row(self.compute_block_size_group)

        # FormGroup's decimal editor is the GenericUILibrary component as
        # well; auto_sync makes threshold edits immediately available to the
        # runtime without restarting the application.
        self.compute_block_threshold_group = FormGroup(
            label="Enable Above Megapixels", input_type="decimal", auto_sync=True
        )
        self.compute_block_threshold_group.input.setRange(0.1, 1000.0)
        self.compute_block_threshold_group.input.setSingleStep(0.5)
        self.compute_block_threshold_group.input.setDecimals(1)
        self.compute_block_threshold_group.bind_store(
            self.store, "compute_block_threshold_mp"
        )
        form.add_row(self.compute_block_threshold_group)

        self.compute_block_mode_group = FormGroup(
            label="Block Processing Rule", input_type="select", auto_sync=True
        )
        self.compute_block_mode_group.input.addItems(
            ["Automatic (by megapixels)", "Always", "Disabled"]
        )
        # Persist a compact canonical value while displaying friendly labels.
        mode_value = str(self.store.get("compute_block_mode", "auto")).lower()
        mode_text = {
            "block": "Always",
            "auto": "Automatic (by megapixels)",
            "full": "Disabled",
        }.get(mode_value, "Automatic (by megapixels)")
        self.compute_block_mode_group.input.setCurrentText(mode_text)
        self.compute_block_mode_group.input.currentTextChanged.connect(
            lambda text: self.store.set(
                "compute_block_mode",
                {
                    "Always": "block",
                    "Automatic (by megapixels)": "auto",
                    "Disabled": "full",
                }.get(text, "auto"),
            )
        )
        form.add_row(self.compute_block_mode_group)
        self.update_device_dropdown_style()

        self.add_widget(form)
        QTimer.singleShot(0, self._compact_performance_inputs)
        self.add_stretch()

        actions = Stack(orientation="horizontal")
        actions.add_stretch()
        self.apply_btn = Button(
            getattr(language_config, "APPLY_PARAMETER_BUTTON_TEXT", "Apply Settings"),
            variant="success",
        )
        self.apply_btn.setObjectName("ApplyPerformanceSettingsBtn")
        self.apply_btn.setMinimumHeight(35)
        self.apply_btn.clicked.connect(self._on_apply_clicked)
        actions.add_item(self.apply_btn)
        self.add_widget(actions)

    def _compact_performance_inputs(self):
        """Keep settings editors compact while allowing long options to fit."""
        inputs = (
            getattr(getattr(self, "device_group", None), "input", None),
            getattr(getattr(self, "compute_block_size_group", None), "input", None),
            getattr(getattr(self, "compute_block_threshold_group", None), "input", None),
            getattr(getattr(self, "compute_block_mode_group", None), "input", None),
        )
        compact_width = max(180, int(max(1, self.width()) * 0.5))
        for editor in inputs:
            if editor is None:
                continue
            required_width = editor.sizeHint().width() + 24
            width = max(compact_width, required_width)
            editor.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            editor.setMinimumWidth(width)
            editor.setFixedWidth(width)
            if isinstance(editor, QComboBox):
                editor.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._compact_performance_inputs()

    def _restore_saved_backend_selection(self, options):
        """Select the persisted backend by key, identity, or architecture.

        The display text can be stale after a device rename or migration. The
        canonical architecture/device selector is therefore preferred so the
        combo box reflects the backend actually loaded at startup.
        """
        if not isinstance(getattr(self.device_group, "input", None), QComboBox):
            return
        saved_key = str(self.store.get("device_backend_key", "") or "")
        saved_arch = str(self.store.get("device_backend_arch", "cpu") or "cpu").lower()
        saved_id = self.store.get("device_backend_id", None)
        try:
            saved_id = int(saved_id)
        except (TypeError, ValueError):
            saved_id = None
        selector = self.store.get("device_selector", {})
        saved_name = str(selector.get("name", "") if isinstance(selector, dict) else "").lower()
        saved_text = str(self.store.get("device_backend", "") or "")

        def matches(option):
            if saved_key and option.get("key") == saved_key:
                return True
            if option.get("backend") != saved_arch:
                return False
            if saved_id is not None and option.get("device_id") == saved_id:
                return True
            if saved_name and saved_name in str(option.get("raw_name", "")).lower():
                return True
            return option.get("text") == saved_text

        selected = next((option for option in options if matches(option)), None)
        if selected is None:
            return
        index = self.device_group.input.findData(selected)
        if index < 0:
            index = self.device_group.input.findText(selected.get("text", ""))
        if index >= 0:
            self.device_group.input.setCurrentIndex(index)

    def retranslate_ui(self):
        language_config.reload_language()
        parent_tab = self.parentWidget()
        if parent_tab and hasattr(parent_tab, "parentWidget"):
            from PySide6.QtWidgets import QTabWidget

            tabs = parent_tab.parentWidget()
            if isinstance(tabs, QTabWidget):
                index = tabs.indexOf(parent_tab)
                if index >= 0:
                    tabs.setTabText(
                        index,
                        getattr(language_config, "SETTING_PERFORMANCE_LABEL", "Performance"),
                    )
        self.device_group.label.setText(
            getattr(language_config, "DEVICE_ACCELERATION_LABEL", "GPU Acceleration")
        )
        if hasattr(self, "compute_block_cb"):
            self.compute_block_cb.checkbox.setText("Enable Compute Blocks")
        self.auto_fallback_cb.checkbox.setText(
            getattr(language_config, "LBL_AUTO_FALLBACK", "Auto Fallback")
        )
        self.auto_fallback_cb.checkbox.setToolTip(
            getattr(language_config, "LBL_AUTO_FALLBACK_TIP", "")
        )
        self.test_btn.setText(language_config.BTN_TEST_BACKEND_HARDWARE)
        self.apply_btn.setText(
            getattr(language_config, "APPLY_PARAMETER_BUTTON_TEXT", "Apply Settings")
        )
        self.update_theme()
        self.update_device_dropdown_style()

    def _on_apply_clicked(self):
        selected_backend_text = self.device_group.input.currentText()
        backend_changed = selected_backend_text != self._initial_device_backend
        self._apply_selected_backend_to_process()
        if hasattr(self.store, "save_to_file"):
            self.store.save_to_file()

        from resources.GenericUILibrary import Toast, trigger_live_update

        trigger_live_update()
        self._initial_device_backend = selected_backend_text
        Toast(
            getattr(language_config, "SETTINGS_SAVED", "Settings saved successfully!"),
            variant="success",
            parent=self.window(),
        ).show_toast(duration=3000)

        if backend_changed:
            dialog = modal_confirm(
                language_config.MSG_BACKEND_EXIT_REQUIRED, self.window()
            )
            dialog.title_text.setText(language_config.EXIT_APPLICATION_APPLY_BACKEND_TITLE)
            dialog.yes_button.setText(language_config.EXIT_APPLICATION_YES)
            dialog.no_button.setText(language_config.EXIT_APPLICATION_NO)
            if dialog.exec() == dialog.DialogCode.Accepted:
                restart_application()


def performance_page():
    return PerformanceSettingsPage()
