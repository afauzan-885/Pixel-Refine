import os

# AOT (Ahead-of-Time) Mode configuration
# Default: "1" (AOT/Production mode), set to "0" for compile/JIT mode.
AOT_MODE = os.environ.get("AOT_MODE", os.environ.get("AOT_MODE", "1"))
os.environ["AOT_MODE"] = AOT_MODE
os.environ["AOT_MODE"] = AOT_MODE

APP_VERSION = "1.0.0"
MODEL_CONFIG = {
    "refiner": "database/Learning_Model/mobilenet_refiner.pth",
    "backbone": "database/Learning_Model/mobilenet_v2_weights.pth",
}
# Canonical desktop interpreter for the LLVM20 cutover.  An explicit
# environment override remains available for packaging/CI without silently
# falling back to the legacy E: LLVM15 venv.
PYTHON_INTERPRETER = os.environ.get(
    "PIXEL_REFINE_PYTHON_INTERPRETER",
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe"
    ),
)
CACHE_DIR = "database/cache/thumbnails"
COMPARISON_CACHE_DIR = "database/cache/comparison"
CONFIG_DIR = os.path.join("database", "setting")

# Canonical resident compute-block size for large-image AOT processing.
# Keep this in the application config so demosaic, alignment and denoising
# share one bounded-memory policy instead of carrying per-module literals.
# Defaults are retained only for headless/legacy callers.  Desktop runtime
# values are read from Performance Settings through ``get_compute_block_settings``.
COMPUTE_BLOCK_SIZE = 1024
COMPUTE_BLOCK_MODE = (
    os.environ.get("PIXEL_REFINE_COMPUTE_BLOCK_MODE", "auto").strip().lower()
)


def get_compute_block_settings():
    """Read the persisted performance block policy without importing Qt."""
    import json

    def normalize_mode(value):
        value = str(value or "").strip().lower()
        if value in {"block", "always", "enabled", "enable", "on", "true", "1"}:
            return "block"
        if value in {"full", "disabled", "disable", "off", "false", "0"}:
            return "full"
        return "auto"

    result = {
        "enabled": True,
        "block_size": COMPUTE_BLOCK_SIZE,
        "threshold_mp": 12.0,
        "mode": normalize_mode(COMPUTE_BLOCK_MODE),
    }
    try:
        with open(GENERAL_SETTINGS_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            result["block_size"] = int(
                data.get("compute_block_size", result["block_size"])
            )
            result["threshold_mp"] = float(
                data.get("compute_block_threshold_mp", result["threshold_mp"])
            )
            if "compute_block_mode" in data:
                result["mode"] = normalize_mode(data.get("compute_block_mode"))
            else:
                # Migrate settings written before Block Processing became the
                # single source of truth for enabling/disabling block mode.
                legacy_enabled = bool(
                    data.get("compute_block_enabled", result["enabled"])
                )
                result["mode"] = "auto" if legacy_enabled else "full"
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass
    if result["block_size"] not in (512, 768, 1024, 2048):
        result["block_size"] = COMPUTE_BLOCK_SIZE
    result["threshold_mp"] = max(0.1, result["threshold_mp"])
    result["enabled"] = result["mode"] != "full"
    return result


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
