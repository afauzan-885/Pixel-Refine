"""
pixel_refine_mobile/ui/components/bottom_nav.py
-----------------------------------------------
Bottom navigation bar.
Mobile-specific component (no desktop equivalent).
Uses GenericUILibrary BottomActionBar.
"""

from resources.GenericUILibrary.bottom_action_bar import BottomActionBar


def build_bottom_nav(bridge, tool_type: str = "MFDenoiser") -> BottomActionBar:
    """
    Build the bottom navigation bar.

    Args:
        bridge: AppBridge instance
        tool_type: Current tool type

    Returns:
        BottomActionBar widget
    """
    action_bar = BottomActionBar()
    action_bar.add_nav_item("Home")
    action_bar.add_nav_item("Denoiser")
    action_bar.add_nav_item("MFResolution")
    action_bar.add_nav_item("Search")
    action_bar.set_primary_action("Start")

    return action_bar
