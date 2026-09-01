from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)

FARNEBACK_DEFAULTS = {
    "mode": "fast",
}

PARAMETER_SCHEMA = [
    {
        "key": "mode",
        "label": "Preset",
        "type": "dropdown",
        "options": ["fast", "balance", "high"],
        "default": "fast",
        "tooltip_key": "FARNEBACK_LEVELS_TOOLTIP",
    },
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
