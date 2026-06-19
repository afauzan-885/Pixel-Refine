"""
pixel_refine_mobile/ui/components/batch_strip.py
-------------------------------------------------
Horizontal batch selector strip.
Desktop equivalent: RightPanel (batch list section).
Uses GenericUILibrary HorizontalScrollRow + BatchCards.
"""

from resources.GenericUILibrary.containers import Container, Spacer
from resources.GenericUILibrary.horizontal_scroll import (
    HorizontalScrollRow, BatchCard, NewBatchCard,
)


def build_batch_strip(bridge, batches=None) -> Container:
    """
    Build the batch strip (horizontal scrollable batch cards).

    Args:
        bridge: AppBridge instance
        batches: List of (batch_id, batch_name) tuples

    Returns:
        Container with horizontal scroll row
    """
    section = Container(padding=8)

    scroll_row = HorizontalScrollRow(spacing=8)

    # New Batch card
    new_batch = NewBatchCard()
    scroll_row.add_widget(new_batch)

    # Existing batch cards
    if batches:
        for batch_id, batch_name in batches:
            batch_card = BatchCard(name=batch_name)
            scroll_row.add_widget(batch_card)

    scroll_row.add_stretch()
    section.add_widget(scroll_row)

    return section
