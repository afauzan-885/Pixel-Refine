"""
Batch parameter management utilities.
Handles loading and saving batch algorithm parameters from JSON.
"""

import json
import os
from typing import Dict, Any, Optional


# Centralized JSON path for batch parameters
BATCH_PARAMETER_PATH = os.path.join("database", "align", "batch_parameter.json")


def get_json_path() -> str:
    """Return the centralized path to batch_parameter.json."""
    return BATCH_PARAMETER_PATH


def load_json_state(path: Optional[str] = None, default: Optional[Dict] = None) -> Dict:
    """
    Load JSON state from file.

    Args:
        path: Path to JSON file (defaults to BATCH_PARAMETER_PATH)
        default: Default value if file doesn't exist or is invalid

    Returns:
        Dictionary with loaded state or default
    """
    if path is None:
        path = BATCH_PARAMETER_PATH

    if default is None:
        default = {}

    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default
    return default


def save_json_state(
    path: Optional[str] = None, data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Save JSON state to file.

    Args:
        path: Path to JSON file (defaults to BATCH_PARAMETER_PATH)
        data: Dictionary to save
    """
    if path is None:
        path = BATCH_PARAMETER_PATH

    if data is None:
        return

    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"[batch_parameter_manager] Error saving JSON: {e}")


def update_batch_settings(store: Any, batch_id: int, settings: Dict[str, Any]) -> None:
    """
    Update batch settings in the store and save to persistence.

    Args:
        store: SyncStore instance
        batch_id: Batch ID
        settings: Dictionary containing algorithm settings
    """
    str_id = str(batch_id)

    # Map high-level settings to store keys
    bulk_data = {
        f"{str_id}.alignment_algo": settings.get("alignment_algo"),
        f"{str_id}.super_resolution_algo": settings.get("super_resolution_algo"),
        f"{str_id}.denoising_algo": settings.get("denoising_algo"),
        f"{str_id}.checkbox_align_images": settings.get("checkbox_align_images"),
        f"{str_id}.checkbox_super_resolution": settings.get(
            "checkbox_super_resolution"
        ),
        f"{str_id}.checkbox_denoising": settings.get("checkbox_denoising"),
    }

    # Filter out None values to avoid overwriting with nulls if some keys are missing
    bulk_data = {k: v for k, v in bulk_data.items() if v is not None}

    if bulk_data:
        store.update_bulk(bulk_data, save=True)


def get_batch_algorithm_summary(batch_id: int) -> str:
    """
    Get algorithm summary for a batch.

    Args:
        batch_id: Batch ID

    Returns:
        Comma-separated string of active algorithms or "Not Set"
    """
    from pixel_refine_desktop.ui.views.settings.General.Language import language_config

    all_params = load_json_state()
    batch_params = all_params.get(str(batch_id), {})

    active_algos = []

    # Check alignment
    if batch_params.get("checkbox_align_images", False):
        algo = batch_params.get("alignment_algo", "None")
        if algo not in ["None", "No Alignment"]:
            active_algos.append(algo)

    # Check super resolution
    if batch_params.get("checkbox_super_resolution", False):
        algo = batch_params.get("super_resolution_algo", "None")
        if algo not in ["None", "No Super Resolution"]:
            active_algos.append(algo)

    # Check denoising
    if batch_params.get("checkbox_denoising", False):
        algo = batch_params.get("denoising_algo", "None")
        if algo not in ["None", "No Denoising"]:
            active_algos.append(algo)

    return (
        ", ".join(active_algos)
        if active_algos
        else language_config.UI_ALGORITHM_NOT_SET
    )


def get_batch_algorithm_settings(batch_id: int) -> Dict[str, str]:
    """
    Get algorithm settings for a batch in the format expected by AlgorithmProcessorThread.

    Args:
        batch_id: Batch ID

    Returns:
        Dictionary with keys: alignment, super_resolution, denoising
    """
    all_params = load_json_state()
    batch_params = all_params.get(str(batch_id), {})

    settings = {
        "alignment": "No Alignment",
        "super_resolution": "No Super Resolution",
        "denoising": "No Denoising",
    }

    # Check alignment
    if batch_params.get("checkbox_align_images", False):
        algo = batch_params.get("alignment_algo", "No Alignment")
        if algo and algo not in ["None"]:
            settings["alignment"] = algo

    # Check super resolution
    if batch_params.get("checkbox_super_resolution", False):
        algo = batch_params.get("super_resolution_algo", "No Super Resolution")
        if algo and algo not in ["None"]:
            settings["super_resolution"] = algo

    # Check denoising
    if batch_params.get("checkbox_denoising", False):
        algo = batch_params.get("denoising_algo", "No Denoising")
        if algo and algo not in ["None"]:
            settings["denoising"] = algo

    return settings
