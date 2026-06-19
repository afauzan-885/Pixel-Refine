"""
settings_page.py
----------------
Settings Page — App settings and preferences.
"""

from resources.GenericUILibrary.containers import Container, Spacer
from resources.GenericUILibrary.cards import Card
from resources.GenericUILibrary.buttons import Button


def build_settings_page(bridge) -> Container:
    """Build the Settings Page layout."""
    layout = Container(padding=10)

    layout.add_widget(Card(title="Settings"))
    layout.add_widget(Spacer(height=8))

    general = Card(title="General")
    general.add_body_widget(Button("Language", variant="secondary"))
    layout.add_widget(general)

    layout.add_widget(Spacer(height=8))

    perf = Card(title="Performance")
    perf.add_body_widget(Button("GPU Settings", variant="secondary"))
    layout.add_widget(perf)

    layout.add_widget(Spacer(height=8))

    about = Card(title="About")
    about.set_body_content("Pixel Refine Mobile v0.6.0")
    layout.add_widget(about)

    return layout
