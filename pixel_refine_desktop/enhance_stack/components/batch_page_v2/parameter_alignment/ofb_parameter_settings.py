from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)

OFB_DEFAULTS = {
    "mode": "fast",
}

PARAMETER_SCHEMA = [
    {
        "key": "mode",
        "label": "Preset",
        "type": "dropdown",
        "options": ["fast", "balance", "high"],
        "default": "fast",
        "tooltip_key": "ORB_NFEATURES_TOOLTIP",
    },
]


def load_ofb_config():
    return load_section("OFB", OFB_DEFAULTS)


def save_ofb_config(config):
    save_section("OFB", config)


def save_ofb_config_for_active_batch(config):
    save_alignment_config_for_active_batch(
        "OFB",
        "ofb_params",
        config,
    )
