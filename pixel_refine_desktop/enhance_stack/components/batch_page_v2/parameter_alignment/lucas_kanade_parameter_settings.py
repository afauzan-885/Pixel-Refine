from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)


LUCAS_KANADE_DEFAULTS = {
    "backend": "cpu",
    "mode": "fast",
}

LUCAS_KANADE_GPU_DEFAULTS = {
    "mode": "high",
}


PARAMETER_SCHEMA = [
    {
        "key": "mode",
        "label": "Preset",
        "type": "dropdown",
        "options": ["fast", "medium", "high"],
        "default": "fast",
        "tooltip_key": "LUCAS_KANADE_GRID_STEP_TOOLTIP",
    },
]

GPU_PARAMETER_SCHEMA = [
    {
        "key": "mode",
        "label": "Preset",
        "type": "dropdown",
        "options": ["fast", "medium", "high"],
        "default": "high",
        "tooltip_key": "LUCAS_KANADE_GPU_MODE_TOOLTIP",
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


def save_lucas_kanade_gpu_config_for_active_batch(config):
    save_alignment_config_for_active_batch(
        "Lucas Kanade",
        "lucas_kanade_gpu_params",
        config,
    )


def load_lucas_kanade_gpu_config():
    return load_section("LucasKanadeGPU", LUCAS_KANADE_GPU_DEFAULTS)


def save_lucas_kanade_gpu_config(config):
    save_section("LucasKanadeGPU", config)
