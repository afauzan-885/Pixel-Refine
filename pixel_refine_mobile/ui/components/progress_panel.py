"""
pixel_refine_mobile/ui/components/progress_panel.py
---------------------------------------------------
Progress bar panel for processing status.
Desktop equivalent: AlgorithmPanel (progress bar).
Uses GenericUILibrary ProgressBar.
"""

from resources.GenericUILibrary.containers import Container, Row
from resources.GenericUILibrary.cards import Card
from resources.GenericUILibrary.progress_bars import ProgressBar


def build_progress_panel(bridge) -> Container:
    """
    Build the progress panel.

    Args:
        bridge: AppBridge instance

    Returns:
        Container with progress bar
    """
    section = Container(padding=8)

    progress_row = Row(spacing=8)

    # Info card
    info_card = Card(title="")
    info_card.set_body_content("(i)")
    progress_row.add_column(info_card, stretch=1)

    # Progress bar
    progress_bar = ProgressBar()
    progress_bar.setValue(0)
    progress_row.add_column(progress_bar, stretch=3)

    # Percentage card
    percent_card = Card(title="")
    percent_card.set_body_content("0%")
    progress_row.add_column(percent_card, stretch=1)

    section.add_widget(progress_row)

    return section
