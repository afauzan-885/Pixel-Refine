from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)


FARNEBACK_DEFAULTS = {
    "pyr_scale": 0.5,
    "levels": 3,
    "winsize": 15,
    "iterations": 3,
    "poly_n": 5,
    "poly_sigma": 1.2,
    "flags": 0,
    "use_multi_core": True,
    "tile_cols": 4,
    "tile_rows": 3,
    "tile_overlap": 0.20,
}


PARAMETER_SCHEMA = [
    {"key": "pyr_scale", "label": "Pyramid Scale", "type": "slider", "min": 10, "max": 90, "scale": 0.01, "decimals": 2, "value_type": "float", "default": 0.5, "tooltip_key": "FARNEBACK_PYR_SCALE_TOOLTIP"},
    {"key": "levels", "label": "Levels", "type": "slider", "min": 1, "max": 8, "scale": 1, "value_type": "int", "default": 3, "tooltip_key": "FARNEBACK_LEVELS_TOOLTIP"},
    {"key": "winsize", "label": "Window Size", "type": "slider", "min": 5, "max": 61, "scale": 1, "step": 2, "value_type": "int", "default": 15, "tooltip_key": "FARNEBACK_WINSIZE_TOOLTIP"},
    {"key": "iterations", "label": "Iterations", "type": "slider", "min": 1, "max": 10, "scale": 1, "value_type": "int", "default": 3, "tooltip_key": "FARNEBACK_ITERATIONS_TOOLTIP"},
    {"key": "poly_n", "label": "Poly N", "type": "slider", "min": 5, "max": 7, "scale": 1, "step": 2, "value_type": "int", "default": 5, "tooltip_key": "FARNEBACK_POLY_N_TOOLTIP"},
    {"key": "poly_sigma", "label": "Poly Sigma", "type": "slider", "min": 50, "max": 250, "scale": 0.01, "decimals": 2, "value_type": "float", "default": 1.2, "tooltip_key": "FARNEBACK_POLY_SIGMA_TOOLTIP"},
    {"key": "flags", "label": "Flags", "type": "dropdown", "options": [0, 256], "value_type": "int", "default": 0, "tooltip_key": "FARNEBACK_FLAGS_TOOLTIP"},
    {"key": "tile_cols", "label": "Tile Columns", "type": "slider", "min": 1, "max": 8, "scale": 1, "value_type": "int", "default": 4, "tooltip_key": "OPTICAL_FLOW_TILE_COLS_TOOLTIP"},
    {"key": "tile_rows", "label": "Tile Rows", "type": "slider", "min": 1, "max": 6, "scale": 1, "value_type": "int", "default": 3, "tooltip_key": "OPTICAL_FLOW_TILE_ROWS_TOOLTIP"},
    {"key": "tile_overlap", "label": "Tile Overlap %", "type": "slider", "min": 0, "max": 50, "scale": 0.01, "decimals": 2, "value_type": "float", "default": 0.20, "tooltip_key": "OPTICAL_FLOW_TILE_OVERLAP_TOOLTIP"},
    {"key": "use_multi_core", "label": "Use Multi Core", "type": "toggle", "value_type": "bool", "default": True, "tooltip_key": "PARAMETER_USE_MULTI_CORE_TOOLTIP"},
]


def load_farneback_config():
    return load_section("Farneback", FARNEBACK_DEFAULTS)


def save_farneback_config(config):
    save_section("Farneback", config)


def save_farneback_config_for_active_batch(config):
    save_alignment_config_for_active_batch(
        "Farneback",
        "farneback_params",
        config,
    )
