"""Pixel Refine Desktop UI Package.

The public UI objects are loaded lazily.  Importing this package must remain
cheap because many backend modules import settings language/configuration
modules during their own initialization.
"""

from pixel_refine_desktop._lazy_exports import public_names, resolve_lazy_attribute


_LAZY_IMPORTS = {
    "EnhanceStackView": (
        "pixel_refine_desktop.enhance_stack.views.enhance_stack_view",
        "EnhanceStackView",
    ),
    "SettingsView": (
        "pixel_refine_desktop.ui.views.settings.views.settings_view",
        "SettingsView",
    ),
    "Sidebar": (
        "pixel_refine_desktop.ui.components.common.sidebar",
        "Sidebar",
    ),
    "SplashScreen": (
        "pixel_refine_desktop.ui.components.common.splash_screen",
        "SplashScreen",
    ),
}

__all__ = list(_LAZY_IMPORTS)


def __getattr__(name):
    """Resolve public UI objects only when they are actually requested."""
    return resolve_lazy_attribute(name, _LAZY_IMPORTS, globals())


def __dir__():
    return public_names(globals(), __all__)
