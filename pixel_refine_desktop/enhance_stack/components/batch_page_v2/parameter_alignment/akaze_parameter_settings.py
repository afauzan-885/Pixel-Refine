from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_alignment.alignment_config_provider import (
    load_section,
    save_alignment_config_for_active_batch,
    save_section,
)


AKAZE_DEFAULTS = {
    "akaze_threshold": 0.001,
    "akaze_nOctaves": 4,
    "akaze_nOctaveLayers": 4,
    "ratio_threshold": 0.75,
    "ransacThreshold": 5.0,
    "transformation": "homography",
    "keep_edges": False,
    "enable_cropping": False,
    "save_align": False,
    "command_save_to_hd5f": True,
    "align_folder": "",
    "use_multi_core": True,
    "min_matches_for_transform": 10,
    "max_keypoints_used": 500,
}


PARAMETER_SCHEMA = [
    {"key": "akaze_threshold", "label": "Threshold", "type": "slider", "min": 1, "max": 100, "scale": 0.0001, "decimals": 4, "value_type": "float", "default": 0.001, "tooltip_key": "AKAZE_THRESHOLD_TOOLTIP"},
    {"key": "akaze_nOctaves", "label": "Octaves", "type": "slider", "min": 1, "max": 8, "scale": 1, "value_type": "int", "default": 4, "tooltip_key": "AKAZE_OCTAVES_TOOLTIP"},
    {"key": "akaze_nOctaveLayers", "label": "Octave Layers", "type": "slider", "min": 1, "max": 10, "scale": 1, "value_type": "int", "default": 4, "tooltip_key": "AKAZE_OCTAVE_LAYERS_TOOLTIP"},
    {"key": "ratio_threshold", "label": "Ratio Threshold", "type": "slider", "min": 50, "max": 95, "scale": 0.01, "decimals": 2, "value_type": "float", "default": 0.75, "tooltip_key": "FEATURE_RATIO_THRESHOLD_TOOLTIP"},
    {"key": "min_matches_for_transform", "label": "Min Matches", "type": "slider", "min": 4, "max": 80, "scale": 1, "value_type": "int", "default": 10, "tooltip_key": "FEATURE_MIN_MATCHES_TOOLTIP"},
    {"key": "max_keypoints_used", "label": "Max Keypoints", "type": "slider", "min": 100, "max": 5000, "scale": 1, "value_type": "int", "default": 500, "tooltip_key": "FEATURE_MAX_KEYPOINTS_TOOLTIP"},
    {"key": "ransacThreshold", "label": "RANSAC Threshold", "type": "slider", "min": 5, "max": 200, "scale": 0.1, "decimals": 1, "value_type": "float", "default": 5.0, "tooltip_key": "FEATURE_RANSAC_THRESHOLD_TOOLTIP"},
    {"key": "transformation", "label": "Transformation", "type": "dropdown", "options": ["homography", "affine"], "value_type": "str", "default": "homography", "tooltip_key": "FEATURE_TRANSFORMATION_TOOLTIP"},
    {"key": "keep_edges", "label": "Keep Edges", "type": "toggle", "value_type": "bool", "default": False, "tooltip_key": "FEATURE_KEEP_EDGES_TOOLTIP"},
    {"key": "enable_cropping", "label": "Enable Cropping", "type": "toggle", "value_type": "bool", "default": False, "tooltip_key": "FEATURE_ENABLE_CROPPING_TOOLTIP"},
    {"key": "use_multi_core", "label": "Use Multi Core", "type": "toggle", "value_type": "bool", "default": True, "tooltip_key": "PARAMETER_USE_MULTI_CORE_TOOLTIP"},
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
