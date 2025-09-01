import os
APP_VERSION = "0.5.1"
MODEL_CONFIG = {
    "refiner": "database/Learning_Model/mobilenet_refiner.pth",
    "backbone": "database/Learning_Model/mobilenet_v2_weights.pth"
}
PYTHON_INTERPRETER = "venv/Scripts/python.exe"
CACHE_DIR = "database/cache/thumbnails"
CONFIG_DIR = os.path.join("database", "setting")

ALGORITHM_PARAMETER_SETTINGS_FILE = os.path.join(CONFIG_DIR, "Parameter_Stack_Enhance.json")
GENERAL_SETTINGS_FILE = os.path.join(CONFIG_DIR, "app_setting.json")
SUPPORTED_FORMATS = {
    "jpg": [".jpg", ".jpeg", ".jiff", ".jli"],
    "tiff": [".tif", ".tiff"],
    "png": [".png"],
    "raw": [
        ".dng", ".cr2", ".cr3", ".nef", ".nrw", ".arw", ".srf", ".sr2", ".orf", ".rw2", ".pef", ".raf", ".erf",
        ".mrw", ".kdc", ".3fr", ".fff", ".rwl", ".srw", ".x3f", ".mef", ".iiq"
    ]
}

