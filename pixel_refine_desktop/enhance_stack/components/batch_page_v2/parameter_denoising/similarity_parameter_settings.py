"""
Similarity Parameter Settings - Config Provider
================================================

Backend value provider for Similarity parameters.
Only provides config load/save functions - UI is handled by MFDenoiser_parameter_settings.py.
"""

import os
import json
from config import CONFIG_DIR, ALGORITHM_PARAMETER_SETTINGS_FILE


def load_similarity_config():
    """Load Similarity config from JSON file with defaults."""
    defaults = {
        "use_multi_core": True,
        "spatial_params": {
            "similarity_spatial_tile_size": 32,
            "similarity_spatial_motion_sensitivity": 150.00,
            "similarity_spatial_noise_mad_offset_factor": 0.15,
            "similarity_spatial_overlap_percent": 0.40,
            "similarity_spatial_num_workers": 1,
            "similarity_smart_noise_alpha": 1.0,
            "similarity_smart_noise_aware_enable": False,
            "similarity_smart_noise_strength": 100.0,
        },
    }
    final_config = {
        "use_multi_core": defaults["use_multi_core"],
        **defaults["spatial_params"],
    }
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
                    for key, value in defaults["spatial_params"].items():
                        final_config[key] = loaded_similarity_section[
                            "spatial_params"
                        ].get(key, value)
                else:
                    for key, value in defaults["spatial_params"].items():
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


# Default values for UI reference
SIMILARITY_DEFAULTS = {
    "similarity_spatial_tile_size": 24,
    "similarity_spatial_motion_sensitivity": 150.0,
    "similarity_spatial_noise_mad_offset_factor": 0.15,
    "similarity_spatial_overlap_percent": 0.35,
    "similarity_spatial_num_workers": -1,  # -1 = Auto
    "similarity_smart_noise_alpha": 1.8,
    "similarity_smart_noise_aware_enable": True,
    "similarity_smart_noise_strength": 100.0,
}
