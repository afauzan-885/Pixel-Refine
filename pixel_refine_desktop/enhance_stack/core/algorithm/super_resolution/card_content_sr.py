"""Localized display content for the multi-frame super-resolution card."""


CARD_NAME = "MF-Super Resolution"
DESCRIPTION_TRANSLATION_KEY = "DESC_SUPER_RESOLUTION_CARD"


def get_card_content(translations):
    """Return card text using the active language module."""
    return {
        "name": CARD_NAME,
        "description": getattr(translations, DESCRIPTION_TRANSLATION_KEY),
    }


def get_process_command(settings):
    """Supply the selected super-resolution stage to the common Start button."""
    import config
    from pixel_refine_desktop.enhance_stack.core.logic.card_process_command import (
        create_card_command,
    )

    return create_card_command(
        settings, category=config.KEY_SUPER_RESOLUTION,
        stored_key=config.KEY_SUPER_RESOLUTION_ALGO,
        enabled_key=config.KEY_CHECKBOX_SUPER_RES, title=CARD_NAME,
        none_value="No Super Resolution",
    )
