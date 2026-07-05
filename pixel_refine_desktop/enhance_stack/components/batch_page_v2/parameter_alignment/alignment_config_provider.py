import json
import os

from PySide6.QtWidgets import QApplication, QWidget

from config import ALGORITHM_PARAMETER_SETTINGS_FILE, CONFIG_DIR
from pixel_refine_desktop.enhance_stack.core.logic import batch_parameter_manager


def load_section(section_name, defaults):
    config = defaults.copy()
    try:
        if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r") as file:
                params = json.load(file)
            section = params.get(section_name, {})
            if isinstance(section, dict):
                config.update(section)
    except Exception as exc:
        print(f"[{section_name}Settings] Failed to load config: {exc}")
    return config


def save_section(section_name, config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    params = {}
    try:
        if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r") as file:
                params = json.load(file)
    except Exception:
        params = {}
    params[section_name] = config
    try:
        with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "w") as file:
            json.dump(params, file, indent=4)
    except Exception as exc:
        print(f"[{section_name}Settings] Failed to save config: {exc}")


def iter_widgets(widget):
    yield widget
    for child in widget.findChildren(QWidget):
        yield child


def find_active_right_panel():
    app = QApplication.instance()
    if not app:
        return None
    for top_level in app.topLevelWidgets():
        for widget in iter_widgets(top_level):
            if (
                hasattr(widget, "current_batch_id")
                and hasattr(widget, "align_form")
                and hasattr(widget, "denoise_card")
            ):
                return widget
    return None


def save_alignment_config_for_active_batch(algorithm_name, params_key, config):
    right_panel = find_active_right_panel()
    if not right_panel or not getattr(right_panel, "current_batch_id", None):
        return

    batch_id = right_panel.current_batch_id
    str_id = str(batch_id)
    denoising_algo = (
        right_panel.denoise_card.get_value()
        if hasattr(right_panel, "denoise_card")
        else "Average"
    )
    super_resolution_algo = (
        right_panel.sr_card.get_value()
        if hasattr(right_panel, "sr_card")
        else "No Super Resolution"
    )

    settings = {
        "alignment_algo": algorithm_name,
        "super_resolution_algo": super_resolution_algo or "No Super Resolution",
        "denoising_algo": denoising_algo or "No Denoising",
        "checkbox_align_images": algorithm_name not in ("", "None", "No Alignment"),
        "checkbox_super_resolution": bool(getattr(right_panel.sr_card, "is_checked", False))
        if hasattr(right_panel, "sr_card")
        else False,
        "checkbox_denoising": bool(getattr(right_panel.denoise_card, "is_checked", False))
        if hasattr(right_panel, "denoise_card")
        else denoising_algo not in ("", "None", "No Denoising"),
    }

    if hasattr(right_panel, "align_form"):
        right_panel.align_form.set_value(algorithm_name)

    if hasattr(right_panel, "_store") and right_panel._store:
        bulk_data = {
            f"{str_id}.{key}": value
            for key, value in settings.items()
        }
        bulk_data[f"{str_id}.{params_key}"] = config
        right_panel._store.update_bulk(bulk_data, save=True)
    else:
        data = batch_parameter_manager.load_json_state()
        data.setdefault(str_id, {})
        data[str_id].update(settings)
        data[str_id][params_key] = config
        batch_parameter_manager.save_json_state(data=data)

    if hasattr(right_panel, "logic"):
        right_panel.logic.set_settings(
            {
                "alignment": algorithm_name,
                "super_resolution": settings["super_resolution_algo"],
                "denoising": settings["denoising_algo"],
            }
        )
    print(f"[{algorithm_name}Settings] Saved params for batch_id={batch_id}")
