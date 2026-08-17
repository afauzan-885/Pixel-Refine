"""
Batch parameter management utilities.
Handles loading and saving batch algorithm parameters from JSON.
"""

import json
import os
from typing import Dict, Any, Optional
import config


# Centralized JSON path for batch parameters
BATCH_PARAMETER_PATH = os.path.join("database", "align", "batch_parameter.json")


def _normalize_alignment_name(name: str) -> str:
    mapping = {
        "Farneback Optical Flow": "Farneback",
        "Lucas Kanade Optical Flow": "Lucas Kanade",
        "Lucas Kanade GPU Optical Flow": "Lucas Kanade",
        "Block Matching GPU Optical Flow": "Block Matching GPU",
        "RAFT Optical Flow": "RAFT",
    }
    return mapping.get(str(name or "").strip(), str(name or ""))


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
        f"{str_id}.{config.KEY_ALIGNMENT_ALGO}": settings.get(config.KEY_ALIGNMENT_ALGO),
        f"{str_id}.{config.KEY_SUPER_RESOLUTION_ALGO}": settings.get(config.KEY_SUPER_RESOLUTION_ALGO),
        f"{str_id}.{config.KEY_DENOISING_ALGO}": settings.get(config.KEY_DENOISING_ALGO),
        f"{str_id}.{config.KEY_CHECKBOX_ALIGN}": settings.get(config.KEY_CHECKBOX_ALIGN),
        f"{str_id}.{config.KEY_CHECKBOX_SUPER_RES}": settings.get(
            config.KEY_CHECKBOX_SUPER_RES
        ),
        f"{str_id}.{config.KEY_CHECKBOX_DENOISING}": settings.get(config.KEY_CHECKBOX_DENOISING),
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
    if batch_params.get(config.KEY_CHECKBOX_ALIGN, False):
        algo = batch_params.get(config.KEY_ALIGNMENT_ALGO, "None")
        if algo not in ["None", "No Alignment"]:
            active_algos.append(_normalize_alignment_name(algo))

    # Check super resolution
    if batch_params.get(config.KEY_CHECKBOX_SUPER_RES, False):
        algo = batch_params.get(config.KEY_SUPER_RESOLUTION_ALGO, "None")
        if algo not in ["None", "No Super Resolution"]:
            active_algos.append(algo)

    # Check denoising
    if batch_params.get(config.KEY_CHECKBOX_DENOISING, False):
        algo = batch_params.get(config.KEY_DENOISING_ALGO, "None")
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
        config.KEY_ALIGNMENT: "No Alignment",
        config.KEY_SUPER_RESOLUTION: "No Super Resolution",
        config.KEY_DENOISING: "No Denoising",
    }

    # Check alignment
    if batch_params.get(config.KEY_CHECKBOX_ALIGN, False):
        algo = batch_params.get(config.KEY_ALIGNMENT_ALGO, "No Alignment")
        if algo and algo not in ["None"]:
            settings[config.KEY_ALIGNMENT] = _normalize_alignment_name(algo)

    # Check super resolution
    if batch_params.get(config.KEY_CHECKBOX_SUPER_RES, False):
        algo = batch_params.get(config.KEY_SUPER_RESOLUTION_ALGO, "No Super Resolution")
        if algo and algo not in ["None"]:
            settings[config.KEY_SUPER_RESOLUTION] = algo

    # Check denoising
    if batch_params.get(config.KEY_CHECKBOX_DENOISING, False):
        algo = batch_params.get(config.KEY_DENOISING_ALGO, "No Denoising")
        if algo and algo not in ["None"]:
            settings[config.KEY_DENOISING] = algo

    return settings


def get_batch_alignment_runtime_snapshot(batch_id: Optional[int]) -> Dict[str, Any]:
    """
    Build a normalized in-memory snapshot of alignment state for a batch.

    This snapshot is intended to be captured once at process start and reused
    throughout the whole alignment pipeline so cache validity and runtime
    execution both read from the same source of truth.
    """
    if batch_id is None:
        return {
            "batch_id": None,
            config.KEY_ALIGNMENT_ALGO: "No Alignment",
            "alignment_active": False,
            "reference_path": "",
            "params_key": "",
            "params": {},
            "raw_batch_entry": {},
        }

    all_params = load_json_state()
    batch_entry = dict(all_params.get(str(batch_id), {}) or {})
    alignment_algo = _normalize_alignment_name(
        batch_entry.get(config.KEY_ALIGNMENT_ALGO, "No Alignment")
    )
    alignment_active = bool(batch_entry.get(config.KEY_CHECKBOX_ALIGN, False))
    if not alignment_active:
        alignment_algo = "No Alignment"

    params_key_map = {
        "AKAZE": "akaze_params",
        "ORB": "orb_params",
        "Light Glue": "light_glue_params",
        "Farneback": "farneback_params",
        "Lucas Kanade": "lucas_kanade_params",
        "Block Matching GPU": "block_matching_gpu_params",
        "RAFT": "raft_params",
    }
    params_key = params_key_map.get(alignment_algo, "")
    params = batch_entry.get(params_key, {}) if params_key else {}
    if not isinstance(params, dict):
        params = {}
    if alignment_algo == "Lucas Kanade":
        gpu_params = batch_entry.get("lucas_kanade_gpu_params", {})
        if not isinstance(gpu_params, dict):
            gpu_params = {}
        params = {
            **dict(params),
            "gpu_params": dict(gpu_params),
        }

    reference_path = str(batch_entry.get("reference_image_path", "") or "")
    return {
        "batch_id": batch_id,
        config.KEY_ALIGNMENT_ALGO: alignment_algo,
        "alignment_active": alignment_active,
        "reference_path": reference_path,
        "params_key": params_key,
        "params": dict(params),
        "raw_batch_entry": batch_entry,
    }
