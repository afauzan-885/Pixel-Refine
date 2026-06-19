"""
pixel_refine_mobile/core/config.py
-----------------------------------
Mobile-specific configuration for Pixel Refine Mobile.
Mirrors desktop config.py with mobile-appropriate paths.
"""

import os

APP_VERSION = "0.6.0"

# ── Database ────────────────────────────────────────────────────────────────
DATABASE_DIR = "database"
DATABASE_NAME = "pixel_refine_mobile.db"
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)

# ── Cache directories ───────────────────────────────────────────────────────
CACHE_DIR = os.path.join(DATABASE_DIR, "cache", "thumbnails")
COMPARISON_CACHE_DIR = os.path.join(DATABASE_DIR, "cache", "comparison")
ALIGN_DIR = os.path.join(DATABASE_DIR, "align")
STACK_DIR = os.path.join(DATABASE_DIR, "stack")
SETTING_DIR = os.path.join(DATABASE_DIR, "setting")

# ── Algorithm parameter settings ────────────────────────────────────────────
CONFIG_DIR = SETTING_DIR
ALGORITHM_PARAMETER_SETTINGS_FILE = os.path.join(
    CONFIG_DIR, "Parameter_Stack_Enhance.json"
)
GENERAL_SETTINGS_FILE = os.path.join(CONFIG_DIR, "app_setting.json")

# ── Supported image formats ─────────────────────────────────────────────────
SUPPORTED_FORMATS = {
    "jpg": [".jpg", ".jpeg", ".jiff", ".jli"],
    "tiff": [".tif", ".tiff"],
    "png": [".png"],
    "raw": [
        ".dng", ".cr2", ".cr3", ".nef", ".nrw", ".arw",
        ".srf", ".sr2", ".orf", ".rw2", ".pef", ".raf",
        ".erf", ".mrw", ".kdc", ".3fr", ".fff", ".rwl",
        ".srw", ".x3f", ".mef", ".iiq",
    ],
}

# ── Mobile-specific settings ────────────────────────────────────────────────
THUMBNAIL_SIZE = (96, 96)  # Smaller than desktop (128x128)
THUMBNAIL_MAX_RAM_ENTRIES = 200  # Fewer than desktop (500)
THUMBNAIL_WORKERS = 2  # Fewer threads than desktop (4-12)

# ── Tool-specific default algorithm settings ────────────────────────────────
TOOL_DEFAULTS = {
    "MFDenoiser": {
        "alignment": "No Alignment",
        "super_resolution": "No Super Resolution",
        "denoising": "Similarity",
    },
    "MFResolution": {
        "alignment": "AKAZE",
        "super_resolution": "WSR",
        "denoising": "No Denoising",
    },
    "HDR": {
        "alignment": "No Alignment",
        "super_resolution": "No Super Resolution",
        "denoising": "Average",
    },
    "Panorama": {
        "alignment": "AKAZE",
        "super_resolution": "No Super Resolution",
        "denoising": "No Denoising",
    },
}


def ensure_directories():
    """Create all required directories if they don't exist."""
    for directory in [DATABASE_DIR, CACHE_DIR, COMPARISON_CACHE_DIR,
                      ALIGN_DIR, STACK_DIR, SETTING_DIR]:
        os.makedirs(directory, exist_ok=True)
