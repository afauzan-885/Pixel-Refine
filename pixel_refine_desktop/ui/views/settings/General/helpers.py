import os
import sys
import json
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QProcess, QCoreApplication
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from config import ALGORITHM_PARAMETER_SETTINGS_FILE


def restart_application():
    """Fungsi untuk merestart aplikasi baik saat dev maupun saat dibungkus Nuitka."""
    try:
        print(
            getattr(
                language_config, "TRY_RESTART_APPLICATION", "Attempting to reload..."
            )
        )

        sys_executable_abs = os.path.abspath(sys.executable)
        try:
            initial_launch_path = os.path.abspath(sys.argv[0])
        except Exception:
            initial_launch_path = sys_executable_abs

        working_dir = os.path.dirname(initial_launch_path)

        def is_frozen_app():
            """Cek apakah aplikasi berjalan sebagai executable yang dibekukan."""
            return getattr(sys, "frozen", False)

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

        started = QProcess.startDetached(program_to_run, arguments, working_dir)

        if started:
            inst = QCoreApplication.instance()
            if inst:
                inst.quit()
        else:
            print(
                getattr(
                    language_config,
                    "COMMAND_FAILED_IN_RESTART_APPLICATION",
                    "System failed to restart.",
                )
            )
            _show_restart_error(program_to_run, arguments, working_dir)

    except Exception as e:
        _show_generic_error(e)


def _show_restart_error(program, args, wd):
    error_msg = QMessageBox()
    error_msg.setIcon(QMessageBox.Icon.Critical)
    error_msg.setWindowTitle(
        getattr(language_config, "RESTART_FAILED", "Restart Failed")
    )
    error_msg.setText(f"Failed command:\nProgram: {program}\nArgs: {args}\nWD: {wd}")
    error_msg.exec()


def _show_generic_error(e):
    error_msg = QMessageBox()
    error_msg.setIcon(QMessageBox.Icon.Critical)
    error_msg.setWindowTitle(
        getattr(language_config, "RESTART_FAILED", "Restart Failed")
    )
    error_msg.setText(f"An error occurred while trying to restart:\n{e}")
    error_msg.exec()


def sync_algorithm_settings(gpu_setting, multicore_setting):
    """Sync values to Algorithm Parameter Settings File."""
    try:
        all_specific_params = {}
        if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r") as f:
                all_specific_params = json.load(f)

        needs_writing = False
        algo_keys_cpu = ["Farneback", "ORB", "AKAZE"]
        algo_keys_gpu = ["Farneback"]

        for key in algo_keys_cpu:
            if key not in all_specific_params:
                all_specific_params[key] = {}
                needs_writing = True

            if isinstance(all_specific_params[key], dict):
                if all_specific_params[key].get("use_multi_core") != multicore_setting:
                    all_specific_params[key]["use_multi_core"] = multicore_setting
                    needs_writing = True

        for key in algo_keys_gpu:
            if key in all_specific_params and isinstance(
                all_specific_params[key], dict
            ):
                if all_specific_params[key].get("use_gpu") != gpu_setting:
                    all_specific_params[key]["use_gpu"] = gpu_setting
                    needs_writing = True

        if needs_writing:
            os.makedirs(
                os.path.dirname(ALGORITHM_PARAMETER_SETTINGS_FILE), exist_ok=True
            )
            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "w") as f:
                json.dump(all_specific_params, f, indent=4)

    except Exception as e:
        print(f"Warning: Failed to sync algorithm settings: {e}")
