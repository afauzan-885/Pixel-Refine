from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)

RAFT_DEFAULTS = {
    "mode": "balance",
    "global_scale": 0.75,
    "tile_overlap": 0.25,
    "execution_provider": "auto",
}

PARAMETER_SCHEMA = [
    {
        "key": "mode",
        "label": "Mode",
        "type": "dropdown",
        "options": ["fast", "balance", "high"],
        "default": "balance",
        "tooltip_key": "LUCAS_KANADE_GPU_MODE_TOOLTIP",
    },
    {
        "key": "global_scale",
        "label": "Global Scale",
        "type": "dropdown",
        "options": [1.0, 0.75, 0.5, 0.33, 0.25],
        "default": 0.75,
        "value_type": "float",
        "tooltip_key": "LUCAS_KANADE_GPU_MODE_TOOLTIP",
    },
    {
        "key": "tile_overlap",
        "label": "Tile Overlap",
        "type": "dropdown",
        "options": [0.10, 0.15, 0.20, 0.25, 0.30],
        "default": 0.25,
        "value_type": "float",
        "tooltip_key": "LUCAS_KANADE_GPU_MODE_TOOLTIP",
    },
    {
        "key": "execution_provider",
        "label": "Execution Provider",
        "type": "dropdown",
        "options": ["auto", "cpu"],
        "default": "auto",
        "tooltip_key": "LUCAS_KANADE_GPU_MODE_TOOLTIP",
    },
]


def load_raft_config():
    return load_section("RAFT", RAFT_DEFAULTS)


def save_raft_config(config):
    save_section("RAFT", config)


def save_raft_config_for_active_batch(config):
    save_alignment_config_for_active_batch("RAFT", "raft_params", config)
