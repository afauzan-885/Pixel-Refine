"""Dynamic algorithm list backed by MFDenoiser registries."""

ALGORITHM_DATA = {}


def init_algorithm_data():
    global ALGORITHM_DATA
    ALGORITHM_DATA = {}

    from pixel_refine_desktop.ui.views.settings.General.Language import language_config
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
        get_algorithm_options as get_mfdenoiser_algorithm_options,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.HDR.card_content import (
        CARD_CONTENT as HDR_CARD_CONTENT,
        SPDE_MR_NAME,
    )

    ALGORITHM_DATA.update(
        {
            "alignment": {
                "name": language_config.ALIGNMENT_NAME,
                "options": get_mfdenoiser_algorithm_options("alignment"),
            },
            "super_resolution": {
                "name": language_config.SUPER_RESOLUTION_NAME,
                "options": [
                    (
                        "No Super Resolution",
                        language_config.NONE_SUPER_RESOLUTION_DESCRIPTION,
                    ),
                    (
                        "splattingSR",
                        "Confidence-guided subpixel splatting super-resolution",
                    ),
                ],
            },
            "hdr": {
                "name": language_config.PARAMETER_BATCH_HDR,
                "options": [
                    (HDR_CARD_CONTENT["name"], HDR_CARD_CONTENT["description"]),
                    (
                        SPDE_MR_NAME,
                        "Patch-based fusion using 8x8 blocks, stride 4, and "
                        "structure-aware single-frame priority.",
                    ),
                ],
            },
            "denoising": {
                "name": language_config.DENOISING_NAME,
                "options": get_mfdenoiser_algorithm_options("denoising"),
            },
        }
    )


def refresh_algorithm_data():
    ALGORITHM_DATA.clear()
    init_algorithm_data()


def get_algorithm_names(category):
    init_algorithm_data()
    if category in ALGORITHM_DATA:
        return [name for name, _ in ALGORITHM_DATA[category]["options"]]
    return []


def get_algorithm_descriptions(category):
    init_algorithm_data()
    if category in ALGORITHM_DATA:
        return [desc for _, desc in ALGORITHM_DATA[category]["options"]]
    return []


def get_algorithm_options(category):
    init_algorithm_data()
    if category in ALGORITHM_DATA:
        return ALGORITHM_DATA[category]["options"]
    return []


def get_category_display_name(category):
    init_algorithm_data()
    if category in ALGORITHM_DATA:
        return ALGORITHM_DATA[category]["name"]
    return category.capitalize()
