import os

# AOT (Ahead-of-Time) Mode configuration
# Default: "1" (AOT/Production mode), set to "0" for compile/JIT mode.
AOT_MODE = os.environ.get("AOT_MODE", os.environ.get("PIXEL_REFINE_AOT_MODE", "1"))
os.environ["AOT_MODE"] = AOT_MODE
os.environ["PIXEL_REFINE_AOT_MODE"] = AOT_MODE

APP_VERSION = "0.6.0"
MODEL_CONFIG = {
    "refiner": "database/Learning_Model/mobilenet_refiner.pth",
    "backbone": "database/Learning_Model/mobilenet_v2_weights.pth",
}
PYTHON_INTERPRETER = "venv/Scripts/python.exe"
CACHE_DIR = "database/cache/thumbnails"
COMPARISON_CACHE_DIR = "database/cache/comparison"
CONFIG_DIR = os.path.join("database", "setting")

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
