from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)

LUCAS_KANADE_DEFAULTS = {
    "mode": "fast",
}

PARAMETER_SCHEMA = [
    {
        "key": "mode",
        "label": "Preset",
        "type": "dropdown",
        "options": ["fast", "balance", "high"],
        "default": "fast",
        "tooltip_key": "LUCAS_KANADE_GRID_STEP_TOOLTIP",
    },
]


def load_lucas_kanade_config():
    return load_section("LucasKanade", LUCAS_KANADE_DEFAULTS)


def save_lucas_kanade_config(config):
    save_section("LucasKanade", config)


def save_lucas_kanade_config_for_active_batch(config):
    save_alignment_config_for_active_batch(
        "Lucas Kanade",
        "lucas_kanade_params",
        config,
    )
