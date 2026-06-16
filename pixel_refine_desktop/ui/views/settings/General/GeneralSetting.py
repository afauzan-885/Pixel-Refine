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

        gpu_label = getattr(language_config, "GPU_ACCELERATION_LABEL", "GPU Acceleration")
        gpu_tip = getattr(language_config, "GPU_ACCELERATION_DESCRIPTION", "")
        self.gpu_cb.checkbox.setText(gpu_label)
        self.gpu_cb.checkbox.setToolTip(gpu_tip)

        cpu_label = getattr(language_config, "MULTI_CORE_CPU", "Multi-Core CPU")
        cpu_tip = getattr(language_config, "MULTI_CORE_CPU_DESCRIPTION", "")
        self.cpu_cb.checkbox.setText(cpu_label)
        self.cpu_cb.checkbox.setToolTip(cpu_tip)

        thumb_label = getattr(language_config, "THUMBNAIL_LABEL", "Enable Thumbnails")
        thumb_tip = getattr(language_config, "THUMBNAIL_DESCRIPTION", "")
        self.thumb_cb.checkbox.setText(thumb_label)
        self.thumb_cb.checkbox.setToolTip(thumb_tip)

        apply_text = getattr(language_config, "APPLY_PARAMETER_BUTTON_TEXT", "Apply Settings")
        self.apply_btn.setText(apply_text)

        # Update window title if possible
        main_win = self.window()
        if main_win:
            from config import APP_VERSION
            main_win.setWindowTitle(f"Pixel Refine - Version {APP_VERSION}")
        
        self.update_theme()

    def update_theme(self):
        """Update checkbox styles and apply button variant styles dynamically on theme changes."""
        from resources.GenericUILibrary.theme import create_checkbox_style, create_button_style
        style = create_checkbox_style()
        for cb in [self.gpu_cb, self.cpu_cb, self.thumb_cb]:
            if hasattr(cb, "checkbox"):
                cb.checkbox.setStyleSheet(style)
        
        # Apply variant styling for apply button dynamically
        if hasattr(self, "apply_btn") and self.apply_btn:
            self.apply_btn.setStyleSheet(create_button_style("success"))

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


def general_page():
    """Entry point for SettingPage.py"""
    return GeneralSettingsPage()


def load_general_settings():
    """
    Backward compatibility wrapper.
    Returns the current general settings from the store.
    """
    return get_general_store().get(None) or {}
