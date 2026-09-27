from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)

BLOCK_MATCHING_DEFAULTS = {
    "mode": "fast",
    "smooth": False,
}
BLOCK_MATCHING_GPU_DEFAULTS = BLOCK_MATCHING_DEFAULTS

PARAMETER_SCHEMA = [
    {
        "key": "mode",
        "label": "Mode",
        "type": "dropdown",
        "options": ["fast", "balance", "high"],
        "default": "fast",
        "tooltip_key": "LUCAS_KANADE_GPU_MODE_TOOLTIP",
    },
    {
        "key": "smooth",
        "label": "Smooth Blending",
        "type": "checkbox",
        "default": False,
    },
]
GPU_PARAMETER_SCHEMA = PARAMETER_SCHEMA


def load_block_matching_config():
    # Load from canonical section first, then fallback to GPU section
    cfg = load_section("BlockMatching", BLOCK_MATCHING_DEFAULTS)
    if not cfg or cfg == BLOCK_MATCHING_DEFAULTS:
        gpu_cfg = load_section("BlockMatchingGPU", {})
        if gpu_cfg:
            cfg.update(gpu_cfg)
    return cfg


def save_block_matching_config(config):
    save_section("BlockMatching", config)
    save_section("BlockMatchingGPU", config)


def save_block_matching_config_for_active_batch(config):
    save_alignment_config_for_active_batch(
        "Block Matching",
        "block_matching_params",
        config,
    )
    save_alignment_config_for_active_batch(
        "Block Matching GPU",
        "block_matching_gpu_params",
        config,
    )


# Backward compatibility aliases
load_block_matching_gpu_config = load_block_matching_config
save_block_matching_gpu_config = save_block_matching_config
save_block_matching_gpu_config_for_active_batch = save_block_matching_config_for_active_batch
