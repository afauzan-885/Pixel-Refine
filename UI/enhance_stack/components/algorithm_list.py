from UI.settings.General.Language import language_config

ALGORITHM_DATA = {
    "alignment": {
        "name": language_config.ALIGNMENT_NAME,
        "options": [
            ("No Alignment", language_config.NONE_ALIGNMENT_DESCRIPTION),
            ("Farneback Optical Flow", language_config.FARNEBACK_DESCRIPTION),
            ("AKAZE", language_config.AKAZE_DESCRIPTION),
            ("ORB", language_config.ORB_DESCRIPTION),
            ("Light Glue", language_config.LIGHT_GLUE_DESCRIPTION)
        ]
    },
    "super_resolution": {
        "name": language_config.SUPER_RESOLUTION_NAME,
        "options": [
            ("No Super Resolution", language_config.NONE_SUPER_RESOLUTION_DESCRIPTION),
            # ("Interpolation", language_config.INTERPOLATION_DESCRIPTION)
        ]
    },
    "denoising": {
        "name": language_config.DENOISING_NAME,
        "options": [
            ("No Denoising", language_config.NONE_DENOISING_DESCRIPTION),
            ("Average", language_config.AVERAGE_DESCRIPTION),
            ("Median", language_config.MEDIAN_DESCRIPTION),
            ("Similarity", language_config.SIMILARITY_DESCRIPTION),
            # ("Similarity V2", language_config.SIMILARITY_MOTION_V2_DESCRIPTION)
        ]
    }
}

# Fungsi helper opsional untuk mendapatkan nama atau deskripsi saja
def get_algorithm_names(category):
    """Mengembalikan daftar nama algoritma untuk kategori tertentu."""
    if category in ALGORITHM_DATA:
        return [name for name, _ in ALGORITHM_DATA[category]["options"]]
    return []

def get_algorithm_descriptions(category):
    """Mengembalikan daftar deskripsi algoritma untuk kategori tertentu."""
    if category in ALGORITHM_DATA:
        return [desc for _, desc in ALGORITHM_DATA[category]["options"]]
    return []

def get_algorithm_options(category):
    """Mengembalikan daftar tuple (nama, deskripsi) untuk kategori tertentu."""
    if category in ALGORITHM_DATA:
        return ALGORITHM_DATA[category]["options"]
    return []

def get_category_display_name(category):
    """Mengembalikan nama tampilan untuk kategori tertentu."""
    if category in ALGORITHM_DATA:
        return ALGORITHM_DATA[category]["name"]
    return category.capitalize() # Fallback