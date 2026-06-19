"""
home_page.py
------------
Home Page — Tool selection hub for Pixel Refine Mobile.
"""

from resources.GenericUILibrary.containers import Container, Spacer
from resources.GenericUILibrary.cards import Card
from resources.GenericUILibrary.buttons import Button


def build_home_page(bridge) -> Container:
    """Build the Home Page layout."""
    layout = Container(padding=10)

    layout.add_widget(Card(title="Pixel Refine"))
    layout.add_widget(Spacer(height=8))

    tools = [
        ("MFDenoiser", "primary"),
        ("MFResolution", "success"),
        ("HDR", "info"),
        ("Panorama", "secondary"),
    ]

    for name, variant in tools:
        card = Card(title=name)
        btn = Button(f"Open {name}", variant=variant)
        btn.clicked.connect(lambda checked=False, n=name: bridge.openTool(n))
        card.add_body_widget(btn)
        layout.add_widget(card)

    return layout
