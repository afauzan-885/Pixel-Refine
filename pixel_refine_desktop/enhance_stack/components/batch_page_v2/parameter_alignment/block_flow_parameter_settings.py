from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)

BLOCK_FLOW_DEFAULTS = {
    "smooth": True,
}

PARAMETER_SCHEMA = [
    {
        "key": "smooth",
        "label": "Smooth Blending",
        "type": "checkbox",
        "default": True,
    },
]


def load_block_flow_config():
    return load_section("BlockFlow", BLOCK_FLOW_DEFAULTS)


def save_block_flow_config(config):
    save_section("BlockFlow", config)


def save_block_flow_config_for_active_batch(config):
    save_alignment_config_for_active_batch(
        "Block Flow",
        "block_flow_params",
        config,
    )
