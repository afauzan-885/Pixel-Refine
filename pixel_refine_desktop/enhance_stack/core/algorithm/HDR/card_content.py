"""Display metadata for the HDR algorithm option and featured card."""

CARD_NAME = "Weighted HDR"
LEGACY_CARD_NAME = "Weighted HDR (Foundation)"
SPDE_MR_NAME = "SPDE-MR HDR Fusion"
LEGACY_SPDE_MR_NAME = "SPDE-MR (Patch-Based)"
FEATURE_CARD_NAME = "HDR Fusion"
CARD_CONTENT = {
    "name": CARD_NAME,
    "description": (
        "Gabungkan frame dengan bobot eksposur, estimasi SNR Taichi, dan "
        "penyelarasan MTB."
    ),
}


def get_card_content(translations):
    """Return localized descriptive text for the HDR featured card."""
    return {
        "name": FEATURE_CARD_NAME,
        "description": translations.DESC_HDR_CARD,
    }


def get_process_command(settings):
    """Supply the HDR stage selected for the common batch Start button."""
    import config
    from pixel_refine_desktop.enhance_stack.core.logic.card_process_command import (
        create_card_command,
    )

    return create_card_command(
        settings, category=config.KEY_HDR, stored_key=config.KEY_HDR_ALGO,
        enabled_key=config.KEY_CHECKBOX_HDR, title=FEATURE_CARD_NAME,
        none_value="No HDR",
        aliases={LEGACY_CARD_NAME: CARD_NAME, LEGACY_SPDE_MR_NAME: SPDE_MR_NAME},
        supported_algorithms=(CARD_NAME, SPDE_MR_NAME),
    )
