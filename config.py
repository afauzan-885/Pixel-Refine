import os

APP_VERSION = "0.6.0"
MODEL_CONFIG = {
    "refiner": "database/Learning_Model/mobilenet_refiner.pth",
    "backbone": "database/Learning_Model/mobilenet_v2_weights.pth",
}
PYTHON_INTERPRETER = "venv/Scripts/python.exe"
CACHE_DIR = "database/cache/thumbnails"
COMPARISON_CACHE_DIR = "database/cache/comparison"
CONFIG_DIR = os.path.join("database", "setting")

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
