import json
import os
import sys
import time
from PyQt6.QtWidgets import (QWidget, QLabel, QComboBox, QFormLayout,
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QMessageBox, QCheckBox)
from PyQt6.QtCore import QProcess, QCoreApplication, Qt
from UI.resources.stylesheet.stylesheet import APPLY_BUTTON, DROPDOWN_BOX, TOGGLE_SWITCH_STYLE
from UI.settings.General.Language import language_config
from config import ALGORITHM_PARAMETER_SETTINGS_FILE, GENERAL_SETTINGS_FILE

SETTINGS_DIR = "database/setting"
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "app_setting.json")

# --- Fungsi Helper Load Settings (General) ---
def load_settings():
    """Memuat pengaturan dari app_setting.json."""
    defaults = {
        "language": "English",
        "gpu_acceleration": False,
        "multi_core_cpu": True,
        "enable_thumbnails": False
    }
    if not os.path.exists(GENERAL_SETTINGS_FILE):
        try: os.makedirs(os.path.dirname(GENERAL_SETTINGS_FILE), exist_ok=True)
        except OSError: pass
        return defaults
    try:
        with open(GENERAL_SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        # Pastikan semua kunci default ada
        for key, value in defaults.items():
            settings.setdefault(key, value)
        return settings
    except (json.JSONDecodeError, IOError):
        print(f"Warning: Could not read settings file '{GENERAL_SETTINGS_FILE}'. Using defaults.")
        return defaults

# --- Fungsi Utama Halaman Pengaturan General ---
def general_page():
    """Creates a general settings tab with QFormLayout and a styled apply button."""
    general_tab = QWidget()

    general_tab.setStyleSheet(
        """
        QWidget { background-color: #ffffff; border: none; }
        """
    )

    current_settings = load_settings()
    initial_language = current_settings.get("language", "English")

    main_layout = QVBoxLayout()
    form_layout = QFormLayout()
    form_layout.setContentsMargins(15, 15, 15, 15)
    form_layout.setSpacing(12)
    form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    form_layout.setHorizontalSpacing(20)

    # --- Pengaturan Bahasa ---
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
    form_layout.addRow(language_label, language_dropdown)

    # --- Checkbox / Toggle Switches ---
    # Akselerasi GPU
    gpu_label_text = getattr(language_config, 'GPU_ACCELERATION_LABEL', "Akselerasi GPU")
    gpu_checkbox = QCheckBox(gpu_label_text)
    gpu_checkbox.setChecked(current_settings.get("gpu_acceleration", False))
    gpu_checkbox.setStyleSheet(TOGGLE_SWITCH_STYLE)
    form_layout.addRow(gpu_checkbox)

    # Akselerasi Multi-Core CPU
    cpu_label_text = getattr(language_config, 'MULTI_CORE_CPU', "Akselerasi Multi-Core CPU")
    cpu_checkbox = QCheckBox(cpu_label_text)
    cpu_checkbox.setChecked(current_settings.get("multi_core_cpu", True))
    cpu_checkbox.setStyleSheet(TOGGLE_SWITCH_STYLE)
    form_layout.addRow(cpu_checkbox)

    # Aktifkan Thumbnail
    # thumbnail_label_text = getattr(language_config, 'ENABLE_THUMBNAILS_LABEL', "Thumbnail Proses Batch")
    # thumbnail_checkbox = QCheckBox(thumbnail_label_text)
    # thumbnail_checkbox.setChecked(current_settings.get("enable_thumbnails", False))
    # thumbnail_checkbox.setStyleSheet(TOGGLE_SWITCH_STYLE)
    # form_layout.addRow(thumbnail_checkbox)
    # --------------------------------

    main_layout.addLayout(form_layout)
    main_layout.addStretch()

    # --- Tombol Apply ---
    button_layout = QHBoxLayout()
    button_layout.addStretch()
    apply_button_text = getattr(language_config, 'APPLY_PARAMETER_BUTTON_TEXT', "Apply Settings")
    apply_button = QPushButton(apply_button_text)
    button_layout.addWidget(apply_button)
    main_layout.addLayout(button_layout)
    main_layout.setContentsMargins(10, 10, 10, 15)
    apply_button.setStyleSheet(APPLY_BUTTON)
    apply_button.setMinimumHeight(30)
    # ------------------

    def save_settings():
        new_language = language_dropdown.currentText()
        new_gpu_setting = gpu_checkbox.isChecked()
        new_multicore_setting = cpu_checkbox.isChecked()
        # new_thumbnail_setting = thumbnail_checkbox.isChecked()

        settings_to_save_general = {
            "language": new_language,
            "gpu_acceleration": new_gpu_setting,
            "multi_core_cpu": new_multicore_setting,
            # "enable_thumbnails": new_thumbnail_setting
        }

        # 2. Simpan ke app_setting.json (File General)
        general_save_successful = False
        try:
            os.makedirs(os.path.dirname(GENERAL_SETTINGS_FILE), exist_ok=True)
            with open(GENERAL_SETTINGS_FILE, "w") as f:
                json.dump(settings_to_save_general, f, indent=4)
            general_save_successful = True
        except IOError as e:
             QMessageBox.critical(general_tab, "Error Saving Settings", f"Could not save general settings to '{GENERAL_SETTINGS_FILE}'.\nError: {e}")
             return 
        if general_save_successful:
            specific_file_needs_writing = False
            try:
                # 3. Baca file Parameter_Stack_Enhance.json yang ada
                all_specific_params = {}
                if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
                    try:
                        with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r") as f_specific:
                            all_specific_params = json.load(f_specific)
                    except json.JSONDecodeError as e_json:
                         QMessageBox.warning(general_tab, "Update Warning", f"General settings saved, but failed to read '{ALGORITHM_PARAMETER_SETTINGS_FILE}' for automatic update due to format error.\nPlease check the file.\nError: {e_json}")
                         all_specific_params = None
                    except IOError as e_read:
                         QMessageBox.warning(general_tab, "Update Warning", f"General settings saved, but failed to read '{ALGORITHM_PARAMETER_SETTINGS_FILE}' for automatic update.\nError: {e_read}")
                         all_specific_params = None 
                else:
                    print(f"Info: Specific settings file '{ALGORITHM_PARAMETER_SETTINGS_FILE}' not found. Will create if updates are needed.")
                    all_specific_params = {}

                # Hanya lanjutkan jika pembacaan berhasil atau file tidak ada (dict kosong dibuat)
                if all_specific_params is not None:

                    #Faneback
                    if "Farneback" not in all_specific_params:
                        all_specific_params["Farneback"] = {}
                        specific_file_needs_writing = True 
                        
                    if isinstance(all_specific_params.get("Farneback"), dict):
                        if all_specific_params["Farneback"].get("use_gpu") != new_gpu_setting:
                            all_specific_params["Farneback"]["use_gpu"] = new_gpu_setting
                            specific_file_needs_writing = True
                        if all_specific_params["Farneback"].get("use_multi_core") != new_multicore_setting:
                            all_specific_params["Farneback"]["use_multi_core"] = new_multicore_setting
                            specific_file_needs_writing = True
                    else:
                         pass

                    #ORB 
                    if "ORB" not in all_specific_params:
                        all_specific_params["ORB"] = {}
                        specific_file_needs_writing = True
                        
                    if isinstance(all_specific_params.get("ORB"), dict):
                        if all_specific_params["ORB"].get("use_multi_core") != new_multicore_setting:
                            all_specific_params["ORB"]["use_multi_core"] = new_multicore_setting
                            specific_file_needs_writing = True
                    
                    
                    #AKAZE
                    if "AKAZE" not in all_specific_params:
                        all_specific_params["AKAZE"] = {}
                        specific_file_needs_writing = True
                        
                    if isinstance(all_specific_params.get("AKAZE"), dict):
                        if all_specific_params["AKAZE"].get("use_multi_core") != new_multicore_setting:
                            all_specific_params["AKAZE"]["use_multi_core"] = new_multicore_setting
                            specific_file_needs_writing = True
                    else:
                        pass

                    # --- 5. Tulis kembali HANYA JIKA ADA PERUBAHAN ---
                    if specific_file_needs_writing:
                        try:
                            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "w") as f_specific_write:
                                json.dump(all_specific_params, f_specific_write, indent=4)
                        except IOError as e_write:
                            QMessageBox.warning(general_tab, "Update Warning", f"General settings saved, but failed to automatically update algorithm settings in '{ALGORITHM_PARAMETER_SETTINGS_FILE}'.\nError: {e_write}")
                    else:
                        pass

            except Exception as e_general:
                 QMessageBox.warning(general_tab, "Update Warning", f"General settings saved, but an unexpected error occurred during automatic update of algorithm settings.\nError: {e_general}")
        
        # 6. Cek perubahan bahasa dan tampilkan dialog restart jika perlu
        language_changed = (new_language.lower() != initial_language.lower())
        if language_changed:
            msg_box = QMessageBox(); restart_title = getattr(language_config, 'RESTART_APPLICATION_REQUIRED', "Restart Required")
            restart_desc = getattr(language_config, 'RESTART_APPLICATION_DESCRIPTION', "Language change requires restart.")
            accept_text = getattr(language_config, 'ACCEPT_RESTART_APPLICATION', "Restart Now"); reject_text = getattr(language_config, 'REJECT_APPLICATION_DESCRIPTION', "Later")
            msg_box.setWindowTitle(restart_title); msg_box.setText(restart_desc); msg_box.setIcon(QMessageBox.Icon.Warning)
            restart_button = msg_box.addButton(accept_text, QMessageBox.ButtonRole.AcceptRole); later_button = msg_box.addButton(reject_text, QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()
            if msg_box.clickedButton() == restart_button: restart_application()
        else:
             if general_save_successful:
                 QMessageBox.information(general_tab, "Setting", language_config.SETTINGS_SAVED)
            
    def restart_application():
        """Fungsi untuk merestart aplikasi menggunakan QProcess."""
        try:
            print(language_config.TRY_RESTART_APPLICATION)

            sys_executable_abs = os.path.abspath(sys.executable)
            try:
                initial_launch_path = os.path.abspath(sys.argv[0])
            except Exception:
                initial_launch_path = sys_executable_abs # Fallback
            
            working_dir = os.path.dirname(initial_launch_path)

            is_frozen = getattr(sys, 'frozen', False)
            
            arguments = []
            program_to_run = "" 

            if is_frozen:
                program_to_run = initial_launch_path 
                arguments = sys.argv[1:]
            else:
                program_to_run = sys_executable_abs # Path ke python.exe
                arguments = [initial_launch_path] + sys.argv[1:] # initial_launch_path adalah main.py
            
            if not os.path.exists(program_to_run):
                raise FileNotFoundError(f"Program to run not found: {program_to_run}")
            if not is_frozen and not os.path.exists(arguments[0]): # Cek script path di mode dev
                raise FileNotFoundError(f"Script to run not found: {arguments[0]}")
            if not os.path.isdir(working_dir):
                raise NotADirectoryError(f"Working directory is not a valid directory: {working_dir}")

            started = QProcess.startDetached(program_to_run, arguments, working_dir)

            if started:
                time.sleep(0.2) 
                QCoreApplication.instance().quit() 
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
