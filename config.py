import os

# AOT (Ahead-of-Time) Mode configuration
# Default: "1" (AOT/Production mode), set to "0" for compile/JIT mode.
AOT_MODE = os.environ.get("AOT_MODE", os.environ.get("AOT_MODE", "1"))
os.environ["AOT_MODE"] = AOT_MODE
os.environ["AOT_MODE"] = AOT_MODE

APP_VERSION = "0.6.0"
MODEL_CONFIG = {
    "refiner": "database/Learning_Model/mobilenet_refiner.pth",
    "backbone": "database/Learning_Model/mobilenet_v2_weights.pth",
}
# Canonical desktop interpreter for the LLVM20 cutover.  An explicit
# environment override remains available for packaging/CI without silently
# falling back to the legacy E: LLVM15 venv.
PYTHON_INTERPRETER = os.environ.get(
    "PIXEL_REFINE_PYTHON_INTERPRETER",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe"),
)
CACHE_DIR = "database/cache/thumbnails"
COMPARISON_CACHE_DIR = "database/cache/comparison"
CONFIG_DIR = os.path.join("database", "setting")

# ==============================================================================
# CENTRALIZED NATURAL TONE MAPPING PARAMETERS (SINGLE SOURCE OF TRUTH)
# ==============================================================================
DEFAULT_TONE_MAPPING_PARAMS = {
    "exposure": 1.43,
    "shoulder": 2.99,
    "gamma": 1.50,
    "shadow_offset": 0.01,
    "saturation": 1.00,
    "texture_amount": 0.0,
    "texture_radius": 10,
}

CALCULATION_TONE_MAPPING_PARAMS = {
    "exposure": 1.43,
    "shoulder": 2.99,
    "gamma": 1.50,
    "shadow_offset": 0.01,
    "saturation": 1.00,
    "texture_amount": 0.42,
    "texture_radius": 10,
}

# ==============================================================================
# BATCH PARAMETER & ALGORITHM KEYS (SINGLE SOURCE OF TRUTH)
# ==============================================================================
KEY_ALIGNMENT_ALGO = "alignment_algo"
KEY_DENOISING_ALGO = "denoising_algo"
KEY_SUPER_RESOLUTION_ALGO = "super_resolution_algo"

KEY_ALIGNMENT = "alignment"
KEY_DENOISING = "denoising"
KEY_SUPER_RESOLUTION = "super_resolution"

KEY_CHECKBOX_ALIGN = "checkbox_align_images"
KEY_CHECKBOX_SAVE_ALIGN_FOLDER = "checkbox_save_alignment_to_folder"
KEY_CHECKBOX_DENOISING = "checkbox_denoising"
KEY_CHECKBOX_SUPER_RES = "checkbox_super_resolution"
KEY_CHECKBOX_CROP_EDGES = "checkbox_crop_edges"
KEY_CHECKBOX_KEEP_EDGES = "checkbox_keep_edges"

ALGORITHM_PARAMETER_SETTINGS_FILE = os.path.join(
    CONFIG_DIR, "Parameter_Stack_Enhance.json"
)
GENERAL_SETTINGS_FILE = os.path.join(CONFIG_DIR, "app_setting.json")
SUPPORTED_FORMATS = {
    "jpg": [".jpg", ".jpeg", ".jiff", ".jli"],
    "tiff": [".tif", ".tiff"],
    "png": [".png"],
    "raw": [
        ".dng",
        ".cr2",
        ".cr3",
        ".nef",
        ".nrw",
        ".arw",
        ".srf",
        ".sr2",
        ".orf",
        ".rw2",
        ".pef",
        ".raf",
        ".erf",
        ".mrw",
        ".kdc",
        ".3fr",
        ".fff",
        ".rwl",
        ".srw",
        ".x3f",
        ".mef",
        ".iiq",
    ],
}

WINDOW_CONFIG = {
    "app_aspect_ratio": 1200 / 600,
    "min_screen_ratio": 0.76,
    "abs_min_width": 800,
    "abs_min_height": 400,
}
