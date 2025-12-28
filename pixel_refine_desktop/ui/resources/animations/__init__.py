"""UI Animations"""

from .fade import fade_in, fade_out
from .slide import slide
from .zoom import zoom
from .delete import delete
from .animation_manager import (
    StackedWidgetAnimator,
    WidgetLifecycleAnimator,  # <--- Tambahkan ini
    AnimationType,
    SlideDirection,
)

__all__ = [
    "fade_in",
    "fade_out",
    "slide",
    "zoom",
    "delete",
    "StackedWidgetAnimator",
    "WidgetLifecycleAnimator",
    "AnimationType",
    "SlideDirection",
]
