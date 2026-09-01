from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)

AKAZE_DEFAULTS = {
    "mode": "fast",
}

PARAMETER_SCHEMA = [
    {
        "key": "mode",
        "label": "Preset",
        "type": "dropdown",
        "options": ["fast", "balance", "high"],
        "default": "fast",
        "tooltip_key": "AKAZE_THRESHOLD_TOOLTIP",
    },
]


def load_akaze_config():
    return load_section("AKAZE", AKAZE_DEFAULTS)


def save_akaze_config(config):
    save_section("AKAZE", config)


def save_akaze_config_for_active_batch(config):
    save_alignment_config_for_active_batch(
        "AKAZE",
        "akaze_params",
        config,
    )
