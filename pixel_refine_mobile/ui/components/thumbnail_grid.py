"""
pixel_refine_mobile/ui/components/thumbnail_grid.py
---------------------------------------------------
Thumbnail grid for batch image display.
Desktop equivalent: DisplayPanel (grid mode).
Uses GenericUILibrary GridContainer.
"""

from resources.GenericUILibrary.containers import Container
from resources.GenericUILibrary.cards import Card


def build_thumbnail_grid(bridge) -> Container:
    """
    Build the thumbnail grid.

    Args:
        bridge: AppBridge instance

    Returns:
        Container with thumbnail grid
    """
    section = Container(padding=8)

    # Placeholder grid
    placeholder = Card(title="")
    placeholder.set_body_content("Thumbnail Grid — No images loaded")
    section.add_widget(placeholder)

    return section
