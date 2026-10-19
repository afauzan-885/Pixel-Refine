"""
Batch parameter management utilities.
Handles loading and saving batch algorithm parameters from JSON.
"""

import json
import os
from typing import Dict, Any, Optional
import config
from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import (
    get_spec,
    get_specs,
    normalize_name,
)


# Centralized JSON path for batch parameters
BATCH_PARAMETER_PATH = os.path.join("database", "align", "batch_parameter.json")
ALGORITHM_PARAMETER_CONTAINER = "algorithm_params"


def _legacy_parameter_keys(spec):
    """Return legacy payload names accepted while batches migrate in place."""
    keys = list(spec.parameter_keys)
    if spec.category == "alignment" and spec.key == "ofb":
        keys.append("orb_params")
    if spec.category == "alignment" and spec.key == "block_matching":
        keys.append("block_matching_params")
    if spec.category == "alignment" and spec.key == "lucas_kanade":
        keys.append("lucas_kanade_gpu_params")
    if spec.category == "denoising" and spec.key == "similarity":
        keys.extend(
            ("spatial_params", "similarity_spatial_params", "similarity_fusion_params")
        )
    return tuple(dict.fromkeys(keys))


def normalize_batch_algorithm_params(batch_entry: Dict[str, Any]) -> Dict[str, Any]:
    """Build the canonical nested parameter container from legacy batch keys.

    ``algorithm_params`` is the single runtime source of truth. Existing
    algorithm-specific top-level keys remain readable as migration inputs.
    """
    if not isinstance(batch_entry, dict):
        return {}
    existing = batch_entry.get(ALGORITHM_PARAMETER_CONTAINER)
    normalized = {
        category: dict(values)
        for category, values in existing.items()
        if category in ("alignment", "denoising", "super_resolution", "hdr")
        and isinstance(values, dict)
    } if isinstance(existing, dict) else {}
    for category in ("alignment", "denoising", "super_resolution", "hdr"):
        normalized.setdefault(category, {})
        for spec in get_specs(category):
            if spec.key in normalized[category]:
                continue
            legacy = next(
                (
                    batch_entry[key]
                    for key in _legacy_parameter_keys(spec)
                    if isinstance(batch_entry.get(key), dict)
                ),
                None,
            )
            if legacy is not None:
                normalized[category][spec.key] = dict(legacy)
    return normalized


def get_batch_algorithm_params(
    batch_id: Optional[int],
    category: str,
    algorithm: str,
    *,
    batch_entry: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Resolve settings for one algorithm, preferring the canonical container."""
    if batch_entry is None:
        if batch_id is None:
            return {}
        state = load_json_state()
        batch_entry = state.get(str(batch_id), {}) if isinstance(state, dict) else {}
    if not isinstance(batch_entry, dict):
        return {}
    spec = get_spec(category, algorithm)
    container = batch_entry.get(ALGORITHM_PARAMETER_CONTAINER)
    if isinstance(container, dict):
        section = container.get(spec.category)
        if isinstance(section, dict) and isinstance(section.get(spec.key), dict):
            return dict(section[spec.key])
    for key in _legacy_parameter_keys(spec):
        value = batch_entry.get(key)
        if isinstance(value, dict):
            return dict(value)
    return {}


def set_batch_algorithm_params(
    batch_entry: Dict[str, Any], category: str, algorithm: str, params: Dict[str, Any]
) -> Dict[str, Any]:
    """Update the canonical container and return it; no disk/store I/O occurs."""
    if not isinstance(batch_entry, dict):
        raise TypeError("batch_entry must be a dictionary")
    spec = get_spec(category, algorithm)
    container = normalize_batch_algorithm_params(batch_entry)
    container.setdefault(spec.category, {})[spec.key] = dict(params or {})
    batch_entry[ALGORITHM_PARAMETER_CONTAINER] = container
    return container


def save_batch_algorithm_params(
    batch_id: Optional[int],
    category: str,
    algorithm: str,
    params: Dict[str, Any],
    *,
    store: Any = None,
) -> bool:
    """Persist one algorithm payload through the shared canonical container."""
    if batch_id is None:
        return False
    batch_key = str(batch_id)
    state = load_json_state()
    entry = dict(state.get(batch_key, {}) or {})
    container = set_batch_algorithm_params(entry, category, algorithm, params)
    spec = get_spec(category, algorithm)
    updates = {
        f"{batch_key}.{ALGORITHM_PARAMETER_CONTAINER}": container,
    }
    # Keep legacy readers compatible during migration. Runtime reads prefer
    # the canonical container above.
    for legacy_key in spec.parameter_keys:
        updates[f"{batch_key}.{legacy_key}"] = dict(params or {})
    if store is not None:
        store.update_bulk(updates, save=True)
        return True
    entry[ALGORITHM_PARAMETER_CONTAINER] = container
    for legacy_key in spec.parameter_keys:
        entry[legacy_key] = dict(params or {})
    state[batch_key] = entry
    save_json_state(data=state)
    return True


def _normalize_alignment_name(name: str) -> str:
    return normalize_name("alignment", name)


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
        f"{str_id}.{config.KEY_HDR_ALGO}": settings.get(config.KEY_HDR_ALGO),
        f"{str_id}.{config.KEY_CHECKBOX_ALIGN}": settings.get(config.KEY_CHECKBOX_ALIGN),
        f"{str_id}.{config.KEY_CHECKBOX_SUPER_RES}": settings.get(
            config.KEY_CHECKBOX_SUPER_RES
        ),
        f"{str_id}.{config.KEY_CHECKBOX_DENOISING}": settings.get(config.KEY_CHECKBOX_DENOISING),
        f"{str_id}.{config.KEY_CHECKBOX_HDR}": settings.get(config.KEY_CHECKBOX_HDR),
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

    if batch_params.get(config.KEY_CHECKBOX_HDR, False):
        algo = batch_params.get(config.KEY_HDR_ALGO, "None")
        if algo not in ["None", "No HDR"]:
            active_algos.append(algo)

    return (
        ", ".join(active_algos)
        if active_algos
        else language_config.UI_ALGORITHM_NOT_SET
    )


def get_batch_algorithm_settings(batch_id: int) -> Dict[str, Any]:
    """
    Get algorithm settings for a batch in the format expected by AlgorithmProcessorThread.

    Args:
        batch_id: Batch ID

    Returns:
        Dictionary with algorithm selections and their enabled state
    """
    all_params = load_json_state()
    batch_params = all_params.get(str(batch_id), {})

    settings = {
        config.KEY_ALIGNMENT: "No Alignment",
        config.KEY_SUPER_RESOLUTION: "No Super Resolution",
        config.KEY_DENOISING: "No Denoising",
        config.KEY_HDR: "No HDR",
        config.KEY_CHECKBOX_ALIGN: bool(
            batch_params.get(config.KEY_CHECKBOX_ALIGN, False)
        ),
        config.KEY_CHECKBOX_SUPER_RES: bool(
            batch_params.get(config.KEY_CHECKBOX_SUPER_RES, False)
        ),
        config.KEY_CHECKBOX_DENOISING: bool(
            batch_params.get(config.KEY_CHECKBOX_DENOISING, False)
        ),
        config.KEY_CHECKBOX_HDR: bool(
            batch_params.get(config.KEY_CHECKBOX_HDR, False)
        ),
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

    if batch_params.get(config.KEY_CHECKBOX_HDR, False):
        algo = batch_params.get(config.KEY_HDR_ALGO, "No HDR")
        if algo and algo not in ["None"]:
            settings[config.KEY_HDR] = algo

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

    spec = get_spec("alignment", alignment_algo)
    params_key = spec.parameter_keys[0] if spec.parameter_keys else ""
    params = get_batch_algorithm_params(
        batch_id, "alignment", alignment_algo, batch_entry=batch_entry
    )
    if alignment_algo.strip().lower() in {"ofb", "akaze"}:
        # Homography is the only enabled warp for these feature aligners.
        # Normalize legacy per-batch APAP values at the runtime boundary.
        params = dict(params)
        params["warp_method"] = "homography"
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
