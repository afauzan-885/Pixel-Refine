"""FusionNet parameter provider.

The FusionNet panel deliberately contains only model/runtime controls.  Burst
alignment is owned by the resident alignment registry and is persisted by
MFDenoiser, so it must not be duplicated in this provider.
"""

import json
import os

from config import ALGORITHM_PARAMETER_SETTINGS_FILE, CONFIG_DIR


FUSIONNET_DEFAULTS = {
    "fusionnet_denoising_mode": "standard",
    "fusionnet_tile_size": 512,
    "fusionnet_work_pixel_fraction": 0.50,
    "fusionnet_max_neighbor_candidates": 4,
    "fusionnet_patch_search_radius": 5,
    "fusionnet_max_safety": 0.30,
    "fusionnet_ghost_penalty": 1.5,
}

FUSIONNET_DENOISING_MODES = ("standard", "deep_analysis")

_LEGACY_LINEAR_RESOLUTION_KEYS = (
    "fusionnet_work_resolution",
    "work_resolution_scale",
    "work_scale",
)


def _normalize_fusionnet_config(config):
    """Return only the canonical FusionNet runtime settings.

    The UI persists a small FusionNet payload per batch, while older global
    settings may still use ``tile_size``/``work_scale`` aliases.  Keeping the
    normalization here gives both the UI and the worker the same contract and
    prevents Similarity's generic ``work_resolution_scale`` from winning.
    """
    source = dict(config or {})
    normalized = dict(FUSIONNET_DEFAULTS)
    requested_mode = str(
        source.get("fusionnet_denoising_mode", normalized["fusionnet_denoising_mode"])
    ).strip().lower().replace(" ", "_")
    normalized["fusionnet_denoising_mode"] = (
        requested_mode
        if requested_mode in FUSIONNET_DENOISING_MODES
        else FUSIONNET_DEFAULTS["fusionnet_denoising_mode"]
    )
    for name in ("fusionnet_tile_size", "tile_size", "ai_tile_size"):
        if name in source and source[name] is not None:
            normalized["fusionnet_tile_size"] = source[name]
            break
    try:
        normalized["fusionnet_tile_size"] = int(float(normalized["fusionnet_tile_size"]))
    except (TypeError, ValueError):
        normalized["fusionnet_tile_size"] = FUSIONNET_DEFAULTS["fusionnet_tile_size"]
    for key, lower, upper in (
        ("fusionnet_max_neighbor_candidates", 1, 16),
        ("fusionnet_patch_search_radius", 1, 16),
    ):
        try:
            normalized[key] = max(
                lower,
                min(upper, int(round(float(source.get(key, normalized[key]))))),
            )
        except (TypeError, ValueError):
            normalized[key] = FUSIONNET_DEFAULTS[key]
    try:
        pixel_fraction = source.get("fusionnet_work_pixel_fraction")
        if pixel_fraction is not None:
            pixel_fraction = max(0.0025, min(1.0, float(pixel_fraction)))
        else:
            # Existing settings stored a per-dimension scale. Squaring it
            # preserves the same effective width/height after the UI switches
            # to a percentage of total working pixels.
            legacy_scale = next(
                (
                    source[name]
                    for name in _LEGACY_LINEAR_RESOLUTION_KEYS
                    if name in source and source[name] is not None
                ),
                None,
            )
            if legacy_scale is None:
                pixel_fraction = FUSIONNET_DEFAULTS[
                    "fusionnet_work_pixel_fraction"
                ]
            else:
                legacy_scale = max(0.05, min(1.0, float(legacy_scale)))
                pixel_fraction = legacy_scale * legacy_scale
        normalized["fusionnet_work_pixel_fraction"] = pixel_fraction
    except (TypeError, ValueError):
        normalized["fusionnet_work_pixel_fraction"] = FUSIONNET_DEFAULTS[
            "fusionnet_work_pixel_fraction"
        ]
    try:
        raw_safety = source.get(
            "fusionnet_max_safety",
            source.get("max_safety", normalized.get("fusionnet_max_safety", 0.30)),
        )
        normalized["fusionnet_max_safety"] = max(0.01, min(2.0, float(raw_safety)))
    except (TypeError, ValueError):
        normalized["fusionnet_max_safety"] = FUSIONNET_DEFAULTS["fusionnet_max_safety"]

    try:
        raw_penalty = source.get(
            "fusionnet_ghost_penalty",
            source.get("ghost_penalty", normalized.get("fusionnet_ghost_penalty", 1.5)),
        )
        normalized["fusionnet_ghost_penalty"] = max(0.1, min(5.0, float(raw_penalty)))
    except (TypeError, ValueError):
        normalized["fusionnet_ghost_penalty"] = FUSIONNET_DEFAULTS["fusionnet_ghost_penalty"]

    return normalized


PARAMETER_SCHEMA = [
    {
        "key": "fusionnet_denoising_mode",
        "label": "Denoising Mode",
        "type": "dropdown",
        "default": "standard",
        "options": ["standard", "deep_analysis"],
        "option_labels": {
            "standard": "Standard",
            "deep_analysis": "Deep Analysis",
        },
        "value_type": "str",
        "tooltip": (
            "Standard runs the existing temporal FusionNet pipeline. Deep Analysis "
            "selects similar local patches and uses WeightNet confidence for fusion."
        ),
    },
    {
        "key": "fusionnet_max_neighbor_candidates",
        "label": "Max Neighbor Patches",
        "type": "slider",
        "default": 4,
        "min": 1,
        "max": 16,
        "value_type": "int",
        "visible_if": {"fusionnet_denoising_mode": "deep_analysis"},
        "tooltip": "Maximum top-ranked neighbor patches per location and frame in Deep Analysis.",
    },
    {
        "key": "fusionnet_patch_search_radius",
        "label": "Patch Search Distance",
        "type": "slider",
        "default": 5,
        "min": 1,
        "max": 16,
        "value_type": "int",
        "visible_if": {"fusionnet_denoising_mode": "deep_analysis"},
        "tooltip": "Patch search radius in WeightNet analysis-grid pixels; larger values inspect farther neighbors.",
    },
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
        "key": "fusionnet_work_pixel_fraction",
        "label": "Pixel Resolution",
        "type": "dropdown",
        "default": 0.50,
        "options": [1.0, 0.75, 0.50, 0.33, 0.25],
        "option_labels": {
            "1.0": "100%",
            "0.75": "75%",
            "0.5": "50%",
            "0.33": "33%",
            "0.25": "25%",
        },
        "value_type": "float",
        "tooltip": (
            "Percentage of total working pixels. For example, 25% uses about "
            "half the width and half the height; output remains full resolution."
        ),
    },
    {
        "key": "fusionnet_max_safety",
        "label": "Max Safety",
        "type": "slider",
        "default": 0.30,
        "min": 1,
        "max": 200,
        "scale": 0.01,
        "value_type": "float",
        "tooltip": "Maximum additive WeightNet safety-head bias (0.01 to 2.00, default 0.30).",
    },
    {
        "key": "fusionnet_ghost_penalty",
        "label": "Ghost Penalty",
        "type": "slider",
        "default": 1.5,
        "min": 10,
        "max": 500,
        "scale": 0.01,
        "value_type": "float",
        "tooltip": "Noise-adaptive ghost penalty multiplier (0.1 to 5.0, default 1.5).",
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
            nested = batch_parameter_manager.get_batch_algorithm_params(
                batch_id, "denoising", "FusionNet", batch_entry=batch
            )
            if not nested:
                nested = batch.get("fusionnet_params")
            if isinstance(nested, dict):
                # Do not let a partial batch payload reset the other global
                # value to its default; override only keys present in the
                # snapshot.
                normalized_nested = _normalize_fusionnet_config(nested)
                if "fusionnet_denoising_mode" in nested:
                    config["fusionnet_denoising_mode"] = normalized_nested[
                        "fusionnet_denoising_mode"
                    ]
                for key in (
                    "fusionnet_max_neighbor_candidates",
                    "fusionnet_patch_search_radius",
                ):
                    if key in nested:
                        config[key] = normalized_nested[key]
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
                        "fusionnet_work_pixel_fraction",
                        *_LEGACY_LINEAR_RESOLUTION_KEYS,
                    )
                ):
                    config["fusionnet_work_pixel_fraction"] = normalized_nested[
                        "fusionnet_work_pixel_fraction"
                    ]
            else:
                # Accept a flattened legacy snapshot if one is encountered.
                normalized_batch = _normalize_fusionnet_config(batch)
                if "fusionnet_denoising_mode" in batch:
                    config["fusionnet_denoising_mode"] = normalized_batch[
                        "fusionnet_denoising_mode"
                    ]
                for key in (
                    "fusionnet_max_neighbor_candidates",
                    "fusionnet_patch_search_radius",
                ):
                    if key in batch:
                        config[key] = normalized_batch[key]
                if any(
                    key in batch
                    for key in (
                        "fusionnet_work_pixel_fraction",
                        *_LEGACY_LINEAR_RESOLUTION_KEYS,
                    )
                ):
                    config["fusionnet_work_pixel_fraction"] = normalized_batch[
                        "fusionnet_work_pixel_fraction"
                    ]
                if any(key in batch for key in ("fusionnet_tile_size", "tile_size", "ai_tile_size")):
                    config["fusionnet_tile_size"] = normalized_batch[
                        "fusionnet_tile_size"
                    ]
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
    normalized = _normalize_fusionnet_config(config_to_save)
    linear_scale = normalized["fusionnet_work_pixel_fraction"] ** 0.5
    section.update(
        {
            "fusionnet_denoising_mode": normalized["fusionnet_denoising_mode"],
            "fusionnet_tile_size": normalized["fusionnet_tile_size"],
            "fusionnet_max_neighbor_candidates": normalized[
                "fusionnet_max_neighbor_candidates"
            ],
            "fusionnet_patch_search_radius": normalized[
                "fusionnet_patch_search_radius"
            ],
            "fusionnet_work_pixel_fraction": normalized[
                "fusionnet_work_pixel_fraction"
            ],
            # Keep equivalent linear scale for older app versions.
            "fusionnet_work_resolution": linear_scale,
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
        normalized = _normalize_fusionnet_config(config_to_save)
        batch_config = {
            **normalized,
            # Compatibility for older versions that still interpret this as a
            # per-dimension scale.
            "fusionnet_work_resolution": normalized[
                "fusionnet_work_pixel_fraction"
            ] ** 0.5,
        }
        settings = {"denoising_algo": "FusionNet", "checkbox_denoising": True}
        if hasattr(right_panel, "_store") and right_panel._store:
            batch_parameter_manager.save_batch_algorithm_params(
                batch_id,
                "denoising",
                "FusionNet",
                batch_config,
                store=right_panel._store,
            )
            bulk = {f"{batch_id}.{key}": value for key, value in settings.items()}
            right_panel._store.update_bulk(bulk, save=True)
        else:
            batch_parameter_manager.save_batch_algorithm_params(
                batch_id, "denoising", "FusionNet", batch_config
            )
            data = batch_parameter_manager.load_json_state()
            data.setdefault(batch_id, {}).update(settings)
            batch_parameter_manager.save_json_state(data=data)
    except Exception as exc:
        print(f"[FusionNetSettings] Failed to save active batch config: {exc}")
