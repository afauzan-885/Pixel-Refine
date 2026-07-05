from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)


LIGHT_GLUE_DEFAULTS = {
    "transformation": "homography",
    "keep_edges": False,
    "enable_cropping": False,
    "save_align": False,
    "command_save_to_hd5f": True,
    "align_folder": "",
    "use_multi_core": True,
    "use_gpu": False,
    "model_input_size": 448,
    "match_confidence": 0.5,
    "min_matches_for_transform": 8,
}


PARAMETER_SCHEMA = [
    {"key": "match_confidence", "label": "Match Confidence", "type": "slider", "min": 0, "max": 100, "scale": 0.01, "decimals": 2, "value_type": "float", "default": 0.5, "tooltip_key": "LIGHT_GLUE_MATCH_CONFIDENCE_TOOLTIP"},
    {"key": "min_matches_for_transform", "label": "Min Matches", "type": "slider", "min": 4, "max": 80, "scale": 1, "value_type": "int", "default": 8, "tooltip_key": "FEATURE_MIN_MATCHES_TOOLTIP"},
    {"key": "transformation", "label": "Transformation", "type": "dropdown", "options": ["homography", "affine"], "value_type": "str", "default": "homography", "tooltip_key": "FEATURE_TRANSFORMATION_TOOLTIP"},
    {"key": "keep_edges", "label": "Keep Edges", "type": "toggle", "value_type": "bool", "default": False, "tooltip_key": "FEATURE_KEEP_EDGES_TOOLTIP"},
    {"key": "enable_cropping", "label": "Enable Cropping", "type": "toggle", "value_type": "bool", "default": False, "tooltip_key": "FEATURE_ENABLE_CROPPING_TOOLTIP"},
    {"key": "use_gpu", "label": "Use GPU", "type": "toggle", "value_type": "bool", "default": False, "tooltip_key": "LIGHT_GLUE_USE_GPU_TOOLTIP"},
    {"key": "use_multi_core", "label": "Use Multi Core", "type": "toggle", "value_type": "bool", "default": True, "tooltip_key": "PARAMETER_USE_MULTI_CORE_TOOLTIP"},
]


def load_light_glue_config(config_filename=None):
    return load_section("Light_Glue", LIGHT_GLUE_DEFAULTS)


def save_light_glue_config(config):
    save_section("Light_Glue", config)


def save_light_glue_config_for_active_batch(config):
    save_alignment_config_for_active_batch(
        "Light Glue",
        "light_glue_params",
        config,
    )
