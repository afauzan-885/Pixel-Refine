"""
pixel_refine_mobile/ui/screens/__init__.py
-------------------------------------------
Screen builders for Pixel Refine Mobile.
All screens are built exclusively with GenericUILibrary (Python-only composition).
"""

from .home_page import build_home_page
from .workspace_page import build_workspace_page
from .settings_page import build_settings_page

__all__ = [
    "build_home_page",
    "build_workspace_page",
    "build_settings_page",
]
