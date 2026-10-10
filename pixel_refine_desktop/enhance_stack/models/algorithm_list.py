"""Localized UI facade for the shared algorithm catalogue."""

ALGORITHM_DATA = {}


def init_algorithm_data():
    global ALGORITHM_DATA
    ALGORITHM_DATA = {}

    from pixel_refine_desktop.ui.views.settings.General.Language import language_config
    from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import get_options

    category_names = {
        "alignment": language_config.ALIGNMENT_NAME,
        "super_resolution": language_config.SUPER_RESOLUTION_NAME,
        "hdr": language_config.PARAMETER_BATCH_HDR,
        "denoising": language_config.DENOISING_NAME,
    }
    for category, display_name in category_names.items():
        options = get_options(category)
        if category == "super_resolution":
            options = [
                (name, language_config.NONE_SUPER_RESOLUTION_DESCRIPTION
                 if name == "No Super Resolution" else description)
                for name, description in options
            ]
        ALGORITHM_DATA[category] = {"name": display_name, "options": options}


def refresh_algorithm_data():
    ALGORITHM_DATA.clear()
    init_algorithm_data()


def get_algorithm_names(category, *, context="batch", process=None):
    return [name for name, _ in get_algorithm_options(category, context=context, process=process)]


def get_algorithm_descriptions(category):
    init_algorithm_data()
    if category in ALGORITHM_DATA:
        return [desc for _, desc in ALGORITHM_DATA[category]["options"]]
    return []


def get_algorithm_options(category, *, context="batch", process=None):
    init_algorithm_data()
    if category in ALGORITHM_DATA:
        if context == "batch" and process is None:
            return ALGORITHM_DATA[category]["options"]
        from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import get_options
        return get_options(category, context=context, process=process)
    return []


def get_category_display_name(category):
    init_algorithm_data()
    if category in ALGORITHM_DATA:
        return ALGORITHM_DATA[category]["name"]
    return category.capitalize()
