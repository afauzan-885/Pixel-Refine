from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)


LUCAS_KANADE_DEFAULTS = {
    "grid_step": 16,
    "border_margin": 8,
    "point_workers": 2,
    "win_size": 17,
    "max_level": 2,
    "iterations": 18,
    "epsilon": 0.015,
    "use_multi_core": True,
    "tile_cols": 3,
    "tile_rows": 2,
    "tile_overlap": 0.20,
}

LUCAS_KANADE_GPU_DEFAULTS = {
    "mode": "fast",
}


PARAMETER_SCHEMA = [
    {"key": "grid_step", "label": "Grid Step", "type": "slider", "min": 6, "max": 48, "scale": 1, "value_type": "int", "default": 16, "tooltip_key": "LUCAS_KANADE_GRID_STEP_TOOLTIP"},
    {"key": "border_margin", "label": "Border Margin", "type": "slider", "min": 0, "max": 32, "scale": 1, "value_type": "int", "default": 8, "tooltip_key": "LUCAS_KANADE_BORDER_MARGIN_TOOLTIP"},
    {"key": "point_workers", "label": "Point Workers", "type": "slider", "min": 1, "max": 8, "scale": 1, "value_type": "int", "default": 2, "tooltip_key": "LUCAS_KANADE_POINT_WORKERS_TOOLTIP"},
    {"key": "win_size", "label": "Window Size", "type": "slider", "min": 5, "max": 61, "scale": 1, "step": 2, "value_type": "int", "default": 17, "tooltip_key": "LUCAS_KANADE_WIN_SIZE_TOOLTIP"},
    {"key": "max_level", "label": "Pyramid Levels", "type": "slider", "min": 0, "max": 8, "scale": 1, "value_type": "int", "default": 2, "tooltip_key": "LUCAS_KANADE_MAX_LEVEL_TOOLTIP"},
    {"key": "iterations", "label": "Iterations", "type": "slider", "min": 5, "max": 100, "scale": 1, "value_type": "int", "default": 18, "tooltip_key": "LUCAS_KANADE_ITERATIONS_TOOLTIP"},
    {"key": "epsilon", "label": "Epsilon", "type": "slider", "min": 1, "max": 100, "scale": 0.001, "decimals": 3, "value_type": "float", "default": 0.015, "tooltip_key": "LUCAS_KANADE_EPSILON_TOOLTIP"},
    {"key": "tile_cols", "label": "Tile Columns", "type": "slider", "min": 1, "max": 8, "scale": 1, "value_type": "int", "default": 3, "tooltip_key": "OPTICAL_FLOW_TILE_COLS_TOOLTIP"},
    {"key": "tile_rows", "label": "Tile Rows", "type": "slider", "min": 1, "max": 6, "scale": 1, "value_type": "int", "default": 2, "tooltip_key": "OPTICAL_FLOW_TILE_ROWS_TOOLTIP"},
    {"key": "tile_overlap", "label": "Tile Overlap %", "type": "slider", "min": 0, "max": 50, "scale": 0.01, "decimals": 2, "value_type": "float", "default": 0.20, "tooltip_key": "OPTICAL_FLOW_TILE_OVERLAP_TOOLTIP"},
    {"key": "use_multi_core", "label": "Use Multi Core", "type": "toggle", "value_type": "bool", "default": True, "tooltip_key": "PARAMETER_USE_MULTI_CORE_TOOLTIP"},
]

GPU_PARAMETER_SCHEMA = [
    {
        "key": "mode",
        "label": "Mode",
        "type": "dropdown",
        "options": ["fast", "balance", "auto"],
        "default": "fast",
        "tooltip_key": "LUCAS_KANADE_GPU_MODE_TOOLTIP",
    },
]


def load_lucas_kanade_config():
    return load_section("LucasKanade", LUCAS_KANADE_DEFAULTS)


def save_lucas_kanade_config(config):
    save_section("LucasKanade", config)


def save_lucas_kanade_config_for_active_batch(config):
    save_alignment_config_for_active_batch(
        "Lucas Kanade Optical Flow",
        "lucas_kanade_params",
        config,
    )


def save_lucas_kanade_gpu_config_for_active_batch(config):
    save_alignment_config_for_active_batch(
        "Lucas Kanade GPU Optical Flow",
        "lucas_kanade_gpu_params",
        config,
    )


def load_lucas_kanade_gpu_config():
    return load_section("LucasKanadeGPU", LUCAS_KANADE_GPU_DEFAULTS)


def save_lucas_kanade_gpu_config(config):
    save_section("LucasKanadeGPU", config)
