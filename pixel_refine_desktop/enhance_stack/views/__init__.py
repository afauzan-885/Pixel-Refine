"""Enhance Stack views with lazy public exports."""

from pixel_refine_desktop._lazy_exports import public_names, resolve_lazy_attribute


_LAZY_IMPORTS = {
    "EnhanceStackView": (
        "pixel_refine_desktop.enhance_stack.views.enhance_stack_view",
        "EnhanceStackView",
    ),
    "SinglePageView": (
        "pixel_refine_desktop.enhance_stack.views.single_page_view",
        "SinglePageView",
    ),
    "BatchPageView": (
        "pixel_refine_desktop.enhance_stack.views.batch_page_view",
        "BatchPageView",
    ),
}

__all__ = list(_LAZY_IMPORTS)


def __getattr__(name):
    """Resolve view exports only when they are requested."""
    return resolve_lazy_attribute(name, _LAZY_IMPORTS, globals())


def __dir__():
    return public_names(globals(), __all__)
