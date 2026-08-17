"""Enhance Stack components.

Exports are lazy to prevent importing the legacy bulk page while a V2 module
is still being initialized.
"""

from pixel_refine_desktop._lazy_exports import public_names, resolve_lazy_attribute


_LAZY_IMPORTS = {
    "BatchPageV2Layout": (
        "pixel_refine_desktop.enhance_stack.components.batch_page_v2.batch_page_v2_layout",
        "BatchPageV2Layout",
    ),
    "BulkPageLayout": (
        "pixel_refine_desktop.enhance_stack.components.bulk_page.bulk_page_layout",
        "BulkPageLayout",
    ),
    "CombinedPanel": (
        "pixel_refine_desktop.enhance_stack.components.bulk_page.widgets.bulk_combined_panel",
        "CombinedPanel",
    ),
    "ThumbnailLoader": (
        "pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_thumbnail_service",
        "ThumbnailLoader",
    ),
    "convert_tiff_to_uncompressed": (
        "pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_import_service",
        "convert_tiff_to_uncompressed",
    ),
}

__all__ = list(_LAZY_IMPORTS)


def __getattr__(name):
    """Resolve component exports only when they are requested."""
    return resolve_lazy_attribute(name, _LAZY_IMPORTS, globals())


def __dir__():
    return public_names(globals(), __all__)
