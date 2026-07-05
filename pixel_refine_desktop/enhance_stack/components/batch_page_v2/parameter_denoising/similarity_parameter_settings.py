"""
Similarity Parameter Settings - Config Provider
================================================

Backend value provider for Similarity parameters.
Only provides config load/save functions - UI is handled by MFDenoiser_parameter_settings.py.
"""

import os
import json
from config import CONFIG_DIR, ALGORITHM_PARAMETER_SETTINGS_FILE


SIMILARITY_DEFAULTS = {
    "use_multi_core": True,
    "similarity_spatial_tile_size": 24,
    "similarity_spatial_motion_sensitivity": 150.0,
    "similarity_spatial_noise_mad_offset_factor": 0.15,
    "similarity_spatial_overlap_percent": 0.35,
    "similarity_spatial_num_workers": -1,
    "similarity_smart_noise_alpha": 1.8,
    "similarity_smart_noise_aware_enable": True,
    "similarity_smart_noise_strength": 100.0,
    "equalize_brightness": False,
    "early_exit_threshold": 0.05,
    "work_resolution_scale": 1.0,
}


PARAMETER_SCHEMA = [
    {
        "key": "similarity_spatial_tile_size",
        "label": "Tile Size",
        "type": "dropdown",
        "default": 24,
        "options": [8, 12, 16, 24, 32, 48, 64],
        "value_type": "int",
    },
    {
        "key": "similarity_spatial_overlap_percent",
        "label": "Overlap",
        "type": "slider",
        "default": 0.35,
        "min": 0,
        "max": 70,
        "scale": 0.01,
        "value_type": "float",
    },
    {
        "key": "similarity_spatial_motion_sensitivity",
        "label": "Motion Sensitivity",
        "type": "slider",
        "default": 150.0,
        "min": 10,
        "max": 3000,
        "scale": 0.1,
        "value_type": "float",
    },
    {
        "key": "similarity_spatial_noise_mad_offset_factor",
        "label": "Noise Offset",
        "type": "slider",
        "default": 0.15,
        "min": 0,
        "max": 100,
        "scale": 0.01,
        "value_type": "float",
    },
    {
        "key": "early_exit_threshold",
        "label": "Early Exit",
        "type": "slider",
        "default": 0.05,
        "min": 0,
        "max": 100,
        "scale": 0.01,
        "value_type": "float",
    },
    {
        "key": "work_resolution_scale",
        "label": "Work Scale",
        "type": "dropdown",
        "default": 1.0,
        "options": [1.0, 0.75, 0.5, 0.33, 0.25],
        "value_type": "float",
    },
    {
        "key": "equalize_brightness",
        "label": "Equalize Brightness",
        "type": "toggle",
        "default": False,
        "value_type": "bool",
    },
    {
        "key": "use_multi_core",
        "label": "Use Multi Core",
        "type": "toggle",
        "default": True,
        "value_type": "bool",
    },
]


def load_similarity_config():
    """Load Similarity config from JSON file with defaults."""
    final_config = SIMILARITY_DEFAULTS.copy()
    try:
        if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r") as f:
                all_params_file = json.load(f)
            if "Similarity" in all_params_file and isinstance(
                all_params_file.get("Similarity"), dict
            ):
                loaded_similarity_section = all_params_file["Similarity"]
                if "use_multi_core" in loaded_similarity_section:
                    final_config["use_multi_core"] = loaded_similarity_section[
                        "use_multi_core"
                    ]
                if "spatial_params" in loaded_similarity_section and isinstance(
                    loaded_similarity_section["spatial_params"], dict
                ):
                    for key, value in SIMILARITY_DEFAULTS.items():
                        final_config[key] = loaded_similarity_section[
                            "spatial_params"
                        ].get(key, value)
                else:
                    for key, value in SIMILARITY_DEFAULTS.items():
                        final_config[key] = loaded_similarity_section.get(key, value)
                return final_config
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading Similarity config: {e}. Using defaults.")
    return final_config


def save_similarity_v1_config(config_to_save):
    """Save Similarity config to JSON file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_filename = ALGORITHM_PARAMETER_SETTINGS_FILE
    all_params_file = {}
    try:
        if os.path.exists(config_filename):
            with open(config_filename, "r") as f:
                all_params_file = json.load(f)
    except Exception:
        pass
    if "Similarity" not in all_params_file or not isinstance(
        all_params_file.get("Similarity"), dict
    ):
        all_params_file["Similarity"] = {}
    similarity_section_to_save = {
        "use_multi_core": config_to_save.get("use_multi_core", True),
        "spatial_params": {},
    }
    spatial_keys = [
        "similarity_spatial_tile_size",
        "similarity_spatial_motion_sensitivity",
        "similarity_spatial_noise_mad_offset_factor",
        "similarity_spatial_overlap_percent",
        "similarity_spatial_num_workers",
        "similarity_smart_noise_alpha",
        "similarity_smart_noise_aware_enable",
        "similarity_smart_noise_strength",
        "equalize_brightness",
        "early_exit_threshold",
        "work_resolution_scale",
    ]

    for key in spatial_keys:
        if key in config_to_save:
            similarity_section_to_save["spatial_params"][key] = config_to_save[key]
    all_params_file["Similarity"] = similarity_section_to_save
    try:
        with open(config_filename, "w") as f:
            json.dump(all_params_file, f, indent=4)
    except Exception as e:
        print(f"Error saving Similarity config: {e}")


def save_similarity_config(config_to_save):
    save_similarity_v1_config(config_to_save)


def save_similarity_config_for_active_batch(config_to_save):
    try:
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
            find_active_right_panel,
        )
        from pixel_refine_desktop.enhance_stack.core.logic import batch_parameter_manager

        right_panel = find_active_right_panel()
        if not right_panel or not getattr(right_panel, "current_batch_id", None):
            return

        batch_id = right_panel.current_batch_id
        str_id = str(batch_id)
        settings = {
            "denoising_algo": "Similarity",
            "checkbox_denoising": True,
        }

        if hasattr(right_panel, "_store") and right_panel._store:
            bulk_data = {f"{str_id}.{key}": value for key, value in settings.items()}
            bulk_data[f"{str_id}.similarity_params"] = config_to_save
            right_panel._store.update_bulk(bulk_data, save=True)
        else:
            data = batch_parameter_manager.load_json_state()
            data.setdefault(str_id, {})
            data[str_id].update(settings)
            data[str_id]["similarity_params"] = config_to_save
            batch_parameter_manager.save_json_state(data=data)
    except Exception as exc:
        print(f"Error saving Similarity config for active batch: {exc}")
