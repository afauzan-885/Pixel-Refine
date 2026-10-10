"""Display metadata for the HDR algorithm option and featured card."""

from ..catalog import get_spec, get_names

CARD_NAME = get_spec("hdr", "weighted").name
LEGACY_CARD_NAME = get_spec("hdr", "weighted").aliases[0]
SPDE_MR_NAME = get_spec("hdr", "spde_mr").name
LEGACY_SPDE_MR_NAME = get_spec("hdr", "spde_mr").aliases[0]
FEATURE_CARD_NAME = "HDR Fusion"
CARD_CONTENT = {
    "name": CARD_NAME,
    "description": get_spec("hdr", "weighted").description,
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
        supported_algorithms=get_names("hdr", include_disabled=False),
    )
