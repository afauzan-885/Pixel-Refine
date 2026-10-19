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
    config = load_section("AKAZE", AKAZE_DEFAULTS)
    config.pop("warp_method", None)
    return config


def save_akaze_config(config):
    saved_config = dict(config)
    saved_config.pop("warp_method", None)
    save_section("AKAZE", saved_config)


def save_akaze_config_for_active_batch(config):
    saved_config = dict(config)
    saved_config.pop("warp_method", None)
    save_alignment_config_for_active_batch(
        "AKAZE",
        "akaze_params",
        saved_config,
    )
