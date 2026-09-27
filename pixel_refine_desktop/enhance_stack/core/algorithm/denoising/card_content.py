"""Localized display content for the multi-frame denoising card."""


CARD_NAME = "MF-Denoising"
DESCRIPTION_TRANSLATION_KEY = "DESC_DENOISING_CARD"


def get_card_content(translations):
    """Return card text using the active language module."""
    return {
        "name": CARD_NAME,
        "description": getattr(translations, DESCRIPTION_TRANSLATION_KEY),
    }


def get_process_command(settings):
    """Supply a denoising stage using the existing parameter-panel policy."""
    import config
    from pixel_refine_desktop.enhance_stack.core.logic.card_process_command import (
        create_card_command,
    )

    algorithm = str(
        settings.get(config.KEY_DENOISING)
        or settings.get(config.KEY_DENOISING_ALGO)
        or ""
    ).strip()
    return create_card_command(
        settings, category=config.KEY_DENOISING,
        stored_key=config.KEY_DENOISING_ALGO,
        enabled_key=config.KEY_CHECKBOX_DENOISING, title=CARD_NAME,
        none_value="No Denoising",
        direct_start=algorithm in {
            "Average", "Median", "Similarity", "Spatial AI", "FusionNet",
        },
    )
