from PySide6.QtWidgets import QWidget, QMessageBox, QComboBox
from PySide6.QtCore import Qt

from pixel_refine_desktop.ui.resources.GenericUILibrary import (
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
            "#GeneralSettingsPage { background-color: #ffffff; border: none; }"
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

        # GPU Acceleration
        gpu_label = getattr(
            language_config, "GPU_ACCELERATION_LABEL", "GPU Acceleration"
        )
        gpu_tip = getattr(language_config, "GPU_ACCELERATION_DESCRIPTION", "")
        self.gpu_cb = Checkbox(gpu_label, auto_sync=True)
        self.gpu_cb.checkbox.setToolTip(gpu_tip)
        self.gpu_cb.bind_store(self.store, "gpu_acceleration")
        form.add_row(self.gpu_cb)

        # CPU Acceleration
        cpu_label = getattr(language_config, "MULTI_CORE_CPU", "Multi-Core CPU")
        cpu_tip = getattr(language_config, "MULTI_CORE_CPU_DESCRIPTION", "")
        self.cpu_cb = Checkbox(cpu_label, auto_sync=True)
        self.cpu_cb.checkbox.setToolTip(cpu_tip)
        self.cpu_cb.bind_store(self.store, "multi_core_cpu")
        form.add_row(self.cpu_cb)

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
        self.apply_btn = Button(apply_text, variant="ghost")
        self.apply_btn.setMinimumHeight(35)
        self.apply_btn.clicked.connect(self._on_apply_clicked)

        actions.add_item(self.apply_btn)
        self.add_widget(actions)

    def _on_apply_clicked(self):
        """
        Final apply logic:
        1. Save language from FormGroup to store.
        2. Trigger restart only if language has changed.
        """

        if isinstance(self.language_group.input, QComboBox):
            new_lang = self.language_group.input.currentText()
            # We compare with initial to see if restart is needed
            needs_restart = str(new_lang).lower() != str(self._initial_language).lower()

            # Save to store (this will update app_setting.json)
            self.store.set("language", new_lang)

            if needs_restart:
                self._prompt_restart()
            else:
                QMessageBox.information(
                    self,
                    "Setting",
                    getattr(
                        language_config,
                        "SETTINGS_SAVED",
                        "Settings saved successfully!",
                    ),
                )
        else:
            # Fallback for unexpected input type
            QMessageBox.information(
                self,
                "Setting",
                getattr(
                    language_config, "SETTINGS_SAVED", "Settings saved successfully!"
                ),
            )

    def _prompt_restart(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(
            getattr(language_config, "RESTART_APPLICATION_REQUIRED", "Restart Required")
        )
        msg_box.setText(
            getattr(
                language_config,
                "RESTART_APPLICATION_DESCRIPTION",
                "Changes require restart.",
            )
        )
        msg_box.setIcon(QMessageBox.Icon.Warning)

        restart_btn = msg_box.addButton(
            getattr(language_config, "ACCEPT_RESTART_APPLICATION", "Restart Now"),
            QMessageBox.ButtonRole.AcceptRole,
        )
        msg_box.addButton(
            getattr(language_config, "REJECT_APPLICATION_DESCRIPTION", "Later"),
            QMessageBox.ButtonRole.RejectRole,
        )

        msg_box.exec()
        if msg_box.clickedButton() == restart_btn:
            restart_application()


def general_page():
    """Entry point for SettingPage.py"""
    return GeneralSettingsPage()


def load_general_settings():
    """
    Backward compatibility wrapper.
    Returns the current general settings from the store.
    """
    return get_general_store().get(None) or {}
