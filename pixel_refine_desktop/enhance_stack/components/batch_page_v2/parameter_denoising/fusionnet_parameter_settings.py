"""FusionNet parameter provider.

The FusionNet panel deliberately contains only model/runtime controls.  Burst
alignment is owned by the resident alignment registry and is persisted by
MFDenoiser, so it must not be duplicated in this provider.
"""

import json
import os

from config import ALGORITHM_PARAMETER_SETTINGS_FILE, CONFIG_DIR


FUSIONNET_DEFAULTS = {
    "fusionnet_tile_size": 512,
    "fusionnet_work_resolution": 0.50,
}


def _normalize_fusionnet_config(config):
    """Return only the canonical FusionNet runtime settings.

    The UI persists a small FusionNet payload per batch, while older global
    settings may still use ``tile_size``/``work_scale`` aliases.  Keeping the
    normalization here gives both the UI and the worker the same contract and
    prevents Similarity's generic ``work_resolution_scale`` from winning.
    """
    source = dict(config or {})
    normalized = dict(FUSIONNET_DEFAULTS)
    aliases = {
        "fusionnet_tile_size": ("fusionnet_tile_size", "tile_size", "ai_tile_size"),
        "fusionnet_work_resolution": (
            "fusionnet_work_resolution",
            "work_resolution_scale",
            "work_scale",
        ),
    }
    for canonical, names in aliases.items():
        for name in names:
            if name in source and source[name] is not None:
                normalized[canonical] = source[name]
                break
    try:
        normalized["fusionnet_tile_size"] = int(float(normalized["fusionnet_tile_size"]))
    except (TypeError, ValueError):
        normalized["fusionnet_tile_size"] = FUSIONNET_DEFAULTS["fusionnet_tile_size"]
    try:
        normalized["fusionnet_work_resolution"] = max(
            0.05, min(1.0, float(normalized["fusionnet_work_resolution"]))
        )
    except (TypeError, ValueError):
        normalized["fusionnet_work_resolution"] = FUSIONNET_DEFAULTS[
            "fusionnet_work_resolution"
        ]
    return normalized


PARAMETER_SCHEMA = [
    {
        "key": "fusionnet_tile_size",
        "label": "Model Block",
        "type": "dropdown",
        "default": 512,
        "options": [256, 512, 1024],
        "value_type": "int",
        "tooltip": "WeightNet model block size.",
    },
    {
        "key": "fusionnet_work_resolution",
        "label": "Work Resolution",
        "type": "dropdown",
        "default": 0.50,
        "options": [1.0, 0.75, 0.50, 0.33, 0.25],
        "value_type": "float",
        "tooltip": "Resolution scale used for resident alignment and WeightNet analysis.",
    },
]


def load_fusionnet_config():
    config = dict(FUSIONNET_DEFAULTS)
    try:
        if not os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
            return config
        with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        section = data.get("FusionNet", {})
        if not isinstance(section, dict):
            return config
        # Accept the nested form used by batch snapshots as well as the
        # flattened section written by this provider.
        nested = section.get("fusionnet_params")
        if isinstance(nested, dict):
            section = {**section, **nested}
        config.update(_normalize_fusionnet_config(section))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"[FusionNetSettings] Failed to load config: {exc}; using defaults")
    return config


def load_fusionnet_config_for_batch(batch_id=None):
    """Load global FusionNet settings plus the active batch override.

    Batch-specific settings are authoritative.  This reads the same JSON
    snapshot that ``DataStore.update_bulk`` writes, so worker processes do not
    depend on a live Qt object or on the UI process still being alive.
    """
    config = load_fusionnet_config()
    if batch_id is None:
        return config
    try:
        from pixel_refine_desktop.enhance_stack.core.logic import batch_parameter_manager

        state = batch_parameter_manager.load_json_state()
        batch = state.get(str(batch_id), {}) if isinstance(state, dict) else {}
        if isinstance(batch, dict):
            nested = batch.get("fusionnet_params")
            if isinstance(nested, dict):
                # Do not let a partial batch payload reset the other global
                # value to its default; override only keys present in the
                # snapshot.
                normalized_nested = _normalize_fusionnet_config(nested)
                if any(
                    key in nested
                    for key in ("fusionnet_tile_size", "tile_size", "ai_tile_size")
                ):
                    config["fusionnet_tile_size"] = normalized_nested[
                        "fusionnet_tile_size"
                    ]
                if any(
                    key in nested
                    for key in (
                        "fusionnet_work_resolution",
                        "work_resolution_scale",
                        "work_scale",
                    )
                ):
                    config["fusionnet_work_resolution"] = normalized_nested[
                        "fusionnet_work_resolution"
                    ]
            else:
                # Accept a flattened legacy snapshot if one is encountered.
                normalized_batch = _normalize_fusionnet_config(batch)
                for key in ("fusionnet_tile_size", "fusionnet_work_resolution"):
                    if key in batch:
                        config[key] = normalized_batch[key]
    except Exception as exc:
        print(f"[FusionNetSettings] Batch override unavailable: {exc}")
    return _normalize_fusionnet_config(config)


def save_fusionnet_config(config_to_save):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = {}
    try:
        if os.path.exists(ALGORITHM_PARAMETER_SETTINGS_FILE):
            with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "r", encoding="utf-8") as handle:
                data = json.load(handle)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        data = {}
    section = data.get("FusionNet", {})
    if not isinstance(section, dict):
        section = {}
    section.update(
        {
            "fusionnet_tile_size": int(float(config_to_save.get("fusionnet_tile_size", FUSIONNET_DEFAULTS["fusionnet_tile_size"]))),
            "fusionnet_work_resolution": float(config_to_save.get("fusionnet_work_resolution", FUSIONNET_DEFAULTS["fusionnet_work_resolution"])),
        }
    )
    data["FusionNet"] = section
    with open(ALGORITHM_PARAMETER_SETTINGS_FILE, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=4)


def save_fusionnet_config_for_active_batch(config_to_save):
    """Persist only FusionNet settings for the active batch."""
    try:
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
            find_active_right_panel,
        )
        from pixel_refine_desktop.enhance_stack.core.logic import batch_parameter_manager

        right_panel = find_active_right_panel()
        if not right_panel or not getattr(right_panel, "current_batch_id", None):
            return
        batch_id = str(right_panel.current_batch_id)
        settings = {"denoising_algo": "FusionNet", "checkbox_denoising": True}
        if hasattr(right_panel, "_store") and right_panel._store:
            bulk = {f"{batch_id}.{key}": value for key, value in settings.items()}
            bulk[f"{batch_id}.fusionnet_params"] = dict(config_to_save)
            right_panel._store.update_bulk(bulk, save=True)
        else:
            data = batch_parameter_manager.load_json_state()
            data.setdefault(batch_id, {}).update(settings)
            data[batch_id]["fusionnet_params"] = dict(config_to_save)
            batch_parameter_manager.save_json_state(data=data)
    except Exception as exc:
        print(f"[FusionNetSettings] Failed to save active batch config: {exc}")
