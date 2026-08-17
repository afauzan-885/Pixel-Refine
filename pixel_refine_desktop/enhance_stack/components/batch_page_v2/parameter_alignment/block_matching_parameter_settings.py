from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)

BLOCK_MATCHING_GPU_DEFAULTS = {
    "mode": "fast",
}

GPU_PARAMETER_SCHEMA = [
    {
        "key": "mode",
        "label": "Mode",
        "type": "dropdown",
        "options": ["fast", "balance", "high"],
        "default": "fast",
        "tooltip_key": "LUCAS_KANADE_GPU_MODE_TOOLTIP",
    },
]


def load_block_matching_gpu_config():
    return load_section("BlockMatchingGPU", BLOCK_MATCHING_GPU_DEFAULTS)


def save_block_matching_gpu_config(config):
    save_section("BlockMatchingGPU", config)


def save_block_matching_gpu_config_for_active_batch(config):
    save_alignment_config_for_active_batch(
        "Block Matching GPU",
        "block_matching_gpu_params",
        config,
    )
