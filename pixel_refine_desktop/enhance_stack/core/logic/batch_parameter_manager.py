"""
Batch parameter management utilities.
Handles loading and saving batch algorithm parameters from JSON.
"""

import json
import os
from typing import Dict, Any, Optional


def load_json_state(path: str, default: Optional[Dict] = None) -> Dict:
    """
    Load JSON state from file.

    Args:
        path: Path to JSON file
        default: Default value if file doesn't exist or is invalid

    Returns:
        Dictionary with loaded state or default
    """
    if default is None:
        default = {}

    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default
    return default


def save_json_state(path: str, data: Dict[str, Any]) -> None:
    """
    Save JSON state to file.

    Args:
        path: Path to JSON file
        data: Dictionary to save
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def get_batch_algorithm_summary(batch_id: int) -> str:
    """
    Get algorithm summary for a batch.

    Args:
        batch_id: Batch ID

    Returns:
        Comma-separated string of active algorithms or "Not Set"
    """
    from pixel_refine_desktop.ui.views.settings.General.Language import language_config

    json_path = os.path.join("database", "align", "batch_parameter.json")
    all_params = load_json_state(json_path)
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
    json_path = os.path.join("database", "align", "batch_parameter.json")
    all_params = load_json_state(json_path)
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
