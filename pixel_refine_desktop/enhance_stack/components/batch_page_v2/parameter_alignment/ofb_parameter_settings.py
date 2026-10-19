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
    config = load_section("OFB", OFB_DEFAULTS)
    config.pop("warp_method", None)
    return config


def save_ofb_config(config):
    saved_config = dict(config)
    saved_config.pop("warp_method", None)
    save_section("OFB", saved_config)


def save_ofb_config_for_active_batch(config):
    saved_config = dict(config)
    saved_config.pop("warp_method", None)
    save_alignment_config_for_active_batch(
        "OFB",
        "ofb_params",
        saved_config,
    )
