import json
import os
import sys
import time
from PySide6.QtWidgets import (QWidget, QLabel, QComboBox, QFormLayout,
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QMessageBox, QCheckBox,
                             )
from PySide6.QtCore import QProcess, QCoreApplication, Qt
from UI.resources.stylesheet.stylesheet import APPLY_BUTTON, DROPDOWN_BOX, CHECKBOX_SWITCH_STYLE
from UI.settings.General.Language import language_config
from config import ALGORITHM_PARAMETER_SETTINGS_FILE, GENERAL_SETTINGS_FILE

SETTINGS_DIR = "database/setting"
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "app_setting.json")

# --- Fungsi Helper Load Settings (General) ---
def load_general_settings():
    """Memuat pengaturan dari app_setting.json."""
    defaults = {
        "language": "English",
        "gpu_acceleration": False,
        "multi_core_cpu": True,
        "create_thumbnail": False,

    }
    if not os.path.exists(GENERAL_SETTINGS_FILE):
        try:
            os.makedirs(os.path.dirname(GENERAL_SETTINGS_FILE), exist_ok=True)
        except OSError:
            pass
        return defaults.copy(), defaults
    try:
        with open(GENERAL_SETTINGS_FILE, "r") as f:
            loaded_settings_from_file = json.load(f)

        settings_to_use = loaded_settings_from_file.copy()
        for key, default_value in defaults.items():
            settings_to_use.setdefault(key, default_value)

        return settings_to_use, defaults

    except (json.JSONDecodeError, IOError):
        print(f"Warning: Could not read settings file '{GENERAL_SETTINGS_FILE}'. Using defaults.")
        return defaults.copy(), defaults

# --- Fungsi Pembuatan Komponen UI ---

def _create_language_settings(parent_layout, current_settings):
    """Membuat dan menambahkan pengaturan bahasa ke layout."""
    initial_language = current_settings.get("language", "English")
    language_label_text = getattr(language_config, 'LANGUAGE_LABEL', "Language:")
    language_label = QLabel(language_label_text)
    language_dropdown = QComboBox()
    languages = ["English", "Indonesian", "China Traditional", "Melayu"]
    
    current_lang_lower = initial_language.lower()
    selected_lang = next((lang for lang in languages if lang.lower() == current_lang_lower), None)
    if selected_lang:
        languages.remove(selected_lang)
        languages.insert(0, selected_lang)
    language_dropdown.addItems(languages)
    language_dropdown.setCurrentText(initial_language)
    language_dropdown.setStyleSheet(DROPDOWN_BOX)
    language_dropdown.setMinimumWidth(150)
    parent_layout.addRow(language_label, language_dropdown)
    return language_dropdown 

def _create_acceleration_settings(parent_layout, current_settings):
    """Membuat dan menambahkan pengaturan akselerasi GPU & CPU ke layout."""
    # GPU
    gpu_label_text = getattr(language_config, 'GPU_ACCELERATION_LABEL', "GPU Acceleration")
    gpu_checkbox = QCheckBox(gpu_label_text)
    gpu_checkbox.setChecked(current_settings.get("gpu_acceleration", False))
    gpu_checkbox.setToolTip(getattr(language_config, 'GPU_ACCELERATION_DESCRIPTION', ''))
    gpu_checkbox.setStyleSheet(CHECKBOX_SWITCH_STYLE)
    parent_layout.addRow(gpu_checkbox)

    # CPU
    cpu_label_text = getattr(language_config, 'MULTI_CORE_CPU', "Multi-Core CPU") # Atau 'MULTI_CORE_CPU' ?
    cpu_checkbox = QCheckBox(cpu_label_text)
    cpu_checkbox.setToolTip(getattr(language_config, 'MULTI_CORE_CPU_DESCRIPTION', ''))
    cpu_checkbox.setChecked(current_settings.get("multi_core_cpu", True))
    cpu_checkbox.setStyleSheet(CHECKBOX_SWITCH_STYLE)
    parent_layout.addRow(cpu_checkbox)
    
    # Thumbnail
    thumbnail_label_text = getattr(language_config, 'THUMBNAIL_LABEL', "Enable Thumbnails")
    thumbnail_checkbox = QCheckBox(thumbnail_label_text)
    thumbnail_checkbox.setToolTip(getattr(language_config, 'THUMBNAIL_DESCRIPTION', ''))
    thumbnail_checkbox.setChecked(current_settings.get("create_thumbnail", False))
    thumbnail_checkbox.setStyleSheet(CHECKBOX_SWITCH_STYLE)
    parent_layout.addRow(thumbnail_checkbox)


    return {
        "gpu": gpu_checkbox,
        "cpu": cpu_checkbox,
        "thumbnail": thumbnail_checkbox
    }


def _create_apply_button():
    """Membuat layout dan tombol Apply."""
    button_layout = QHBoxLayout()
    button_layout.addStretch()
    apply_button_text = getattr(language_config, 'APPLY_PARAMETER_BUTTON_TEXT', "Apply Settings")
    apply_button = QPushButton(apply_button_text)
    button_layout.addWidget(apply_button)
    apply_button.setStyleSheet(APPLY_BUTTON)
    apply_button.setMinimumHeight(30)
    return button_layout, apply_button

# --- Fungsi Utama (Orchestrator) ---
def general_page():
    """Creates the general settings tab by composing smaller functions."""
    general_tab = QWidget()
    general_tab.setStyleSheet(
        """
        QWidget { background-color: #ffffff; border: none; }
        QGroupBox {
            font-weight: bold; border: 1px solid gray; border-radius: 5px;
            margin-top: 10px; padding-top: 15px; padding-left: 5px;
            padding-right: 5px; padding-bottom: 5px;
            max-width: 350px; /* MODIFIED: increased max-width for more params */
            min-width: 100px;
        }
        QGroupBox::title {
            subcontrol-origin: margin; subcontrol-position: top left;
            padding: 0 3px; left: 10px;
        }
        """
    )

    current_settings, original_defaults_for_reset = load_general_settings()
    initial_language = current_settings.get("language", "English")
    initial_thumbnail_setting = current_settings.get(False)

    main_layout = QVBoxLayout(general_tab)
    top_form_layout = QFormLayout()
    top_form_layout.setContentsMargins(15, 15, 15, 15)
    top_form_layout.setSpacing(12)
    top_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    top_form_layout.setHorizontalSpacing(20)

    language_dropdown = _create_language_settings(top_form_layout, current_settings)
    accel_widgets = _create_acceleration_settings(top_form_layout, current_settings)
    gpu_checkbox = accel_widgets['gpu']
    cpu_checkbox = accel_widgets['cpu']
    main_layout.addLayout(top_form_layout)

    main_layout.addStretch()

    apply_button_layout, apply_button = _create_apply_button()
    main_layout.addLayout(apply_button_layout)

    # MODIFIED: save_settings
    def save_settings():
        new_language = language_dropdown.currentText()
        new_gpu_setting = gpu_checkbox.isChecked()
        new_multicore_setting = cpu_checkbox.isChecked()
        new_thumbnail_setting = accel_widgets['thumbnail'].isChecked()



        settings_to_save_general = {
            "language": new_language,
            "gpu_acceleration": new_gpu_setting,
            "multi_core_cpu": new_multicore_setting,
            "create_thumbnail": new_thumbnail_setting
        }


        general_save_successful = False
        try:
            os.makedirs(os.path.dirname(GENERAL_SETTINGS_FILE), exist_ok=True)
            with open(GENERAL_SETTINGS_FILE, "w") as f:
                json.dump(settings_to_save_general, f, indent=4)
            general_save_successful = True
        except Exception as e:
             QMessageBox.critical(general_tab, "Error Saving Settings", f"Could not save general settings... Error: {e}")
             return

        if general_save_successful:
            specific_file_needs_writing = False
            try:
                all_specific_params = {}
                if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
                    try:
                        with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r") as f_specific:
                            all_specific_params = json.load(f_specific)
                    except Exception as e_read:
                         QMessageBox.warning(general_tab, "Update Warning", f"General settings saved, but failed to read algorithm settings... Error: {e_read}")
                         all_specific_params = None 
                else:
                    all_specific_params = {}

                if all_specific_params is not None:
                    algo_keys_cpu = ["Farneback", "ORB", "AKAZE"]
                    algo_keys_gpu = ["Farneback"]

                    for key in algo_keys_cpu:
                         if key not in all_specific_params: all_specific_params[key] = {}; specific_file_needs_writing = True
                         if isinstance(all_specific_params.get(key), dict):
                             if all_specific_params[key].get("use_multi_core") != new_multicore_setting:
                                 all_specific_params[key]["use_multi_core"] = new_multicore_setting; specific_file_needs_writing = True

                    for key in algo_keys_gpu:
                         if isinstance(all_specific_params.get(key), dict): # Farneback sudah ada dari loop CPU
                              if all_specific_params[key].get("use_gpu") != new_gpu_setting:
                                  all_specific_params[key]["use_gpu"] = new_gpu_setting; specific_file_needs_writing = True
                        
                    if specific_file_needs_writing:
                        try:
                            os.makedirs(os.path.dirname(ALGORITHM_PARAMETER_SETTINGS_FILE), exist_ok=True)
                            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "w") as f_specific_write:
                                json.dump(all_specific_params, f_specific_write, indent=4)
                        except Exception as e_write: QMessageBox.warning(general_tab, "Update Warning", f"General settings saved, but failed to write algorithm settings... Error: {e_write}")

            except Exception as e_update:
                 QMessageBox.warning(general_tab, "Update Warning", f"General settings saved, but an error occurred during algorithm settings update... Error: {e_update}")

        # Cek perubahan yang butuh restart
        language_changed = (new_language.lower() != initial_language.lower())
        thumbnail_setting_changed = (new_thumbnail_setting != initial_thumbnail_setting)

        needs_restart = language_changed or thumbnail_setting_changed

        if needs_restart:
            msg_box = QMessageBox()
            restart_title = getattr(language_config, 'RESTART_APPLICATION_REQUIRED', "Restart Required")
            restart_desc = getattr(language_config, 'RESTART_APPLICATION_DESCRIPTION', "Changes require application restart.")
            accept_text = getattr(language_config, 'ACCEPT_RESTART_APPLICATION', "Restart Now")
            reject_text = getattr(language_config, 'REJECT_APPLICATION_DESCRIPTION', "Later")

            msg_box.setWindowTitle(restart_title)
            msg_box.setText(restart_desc)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            restart_button = msg_box.addButton(accept_text, QMessageBox.ButtonRole.AcceptRole)
            later_button = msg_box.addButton(reject_text, QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()

            if msg_box.clickedButton() == restart_button:
                restart_application()
        else:
            if general_save_successful:
                QMessageBox.information(
                    general_tab,
                    "Setting",
                    getattr(language_config, 'SETTINGS_SAVED', "Settings saved successfully!")
                )

    def restart_application():
        """Fungsi untuk merestart aplikasi baik saat dev maupun saat dibungkus Nuitka."""
        try:
            print(language_config.TRY_RESTART_APPLICATION)

            sys_executable_abs = os.path.abspath(sys.executable)
            try:
                initial_launch_path = os.path.abspath(sys.argv[0])
            except Exception:
                initial_launch_path = sys_executable_abs

            working_dir = os.path.dirname(initial_launch_path)

            def is_frozen_app():
                return hasattr(sys, 'frozen') or (sys.executable != sys.argv[0] and sys.executable.endswith(".exe"))

            frozen = is_frozen_app()

            arguments = []
            program_to_run = ""

            if frozen:
                program_to_run = sys_executable_abs  # Nuitka .exe
                arguments = sys.argv[1:]
            else:
                program_to_run = sys_executable_abs  # python
                arguments = [initial_launch_path] + sys.argv[1:]

            if not os.path.exists(program_to_run):
                raise FileNotFoundError(f"Program to run not found: {program_to_run}")
            if not frozen and not os.path.exists(arguments[0]):
                raise FileNotFoundError(f"Script to run not found: {arguments[0]}")
            if not os.path.isdir(working_dir):
                raise NotADirectoryError(f"Working directory is not a valid directory: {working_dir}")

            started = QProcess.startDetached(program_to_run, arguments, working_dir)

            if started:
                QCoreApplication.instance().quit()
            else:
                print(language_config.COMMAND_FAILED_IN_RESTART_APPLICATION)
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Icon.Critical)
                error_msg.setWindowTitle(language_config.RESTART_FAILED)
                error_msg.setText(f"{language_config.COMMAND_TO_RESTART_MANUALLY}\n\nFailed command:\nProgram: {program_to_run}\nArgs: {arguments}\nWD: {working_dir}")
                error_msg.exec()

        except Exception as e:
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Icon.Critical)
            error_msg.setWindowTitle(language_config.RESTART_FAILED)
            error_msg.setText(f"An error occurred while trying to restart:\n{e}\n\nPlease restart the application manually.")
            error_msg.exec()

    apply_button.clicked.connect(save_settings)
    general_tab.setLayout(main_layout)
    
    return general_tab
