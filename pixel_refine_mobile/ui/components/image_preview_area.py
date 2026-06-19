"""
pixel_refine_mobile/ui/components/image_preview_area.py
-------------------------------------------------------
Image preview area with dot pagination.
Desktop equivalent: DisplayPanel (preview mode).
Uses GenericUILibrary Card + DotIndicator.
"""

from resources.GenericUILibrary.containers import Container, Row, Spacer
from resources.GenericUILibrary.cards import Card
from resources.GenericUILibrary.dot_indicator import DotIndicator


def build_image_preview_area(bridge) -> Container:
    """
    Build the image preview area.

    Args:
        bridge: AppBridge instance

    Returns:
        Container with image preview and dot pagination
    """
    section = Container(padding=8)

    # Image info header
    info_row = Row(spacing=8)

    img_name_card = Card(title="")
    img_name_card.set_body_content("IMG-001")
    info_row.add_column(img_name_card, stretch=1)

    img_count_card = Card(title="")
    img_count_card.set_body_content("0 Images")
    info_row.add_column(img_count_card, stretch=1)

    section.add_widget(info_row)

    # Image preview placeholder
    preview_card = Card(title="")
    preview_card.set_body_content("Image Preview Area")
    section.add_widget(preview_card)

    # Reference label
    ref_card = Card(title="")
    ref_card.set_body_content("Image (Reference)")
    section.add_widget(ref_card)

    # Dot pagination
    dot_indicator = DotIndicator(count=6, active_index=0)
    section.add_widget(dot_indicator)

    return section
