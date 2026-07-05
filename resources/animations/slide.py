from PySide6.QtWidgets import QStackedWidget
from PySide6.QtCore import QEasingCurve
from typing import Callable, Optional

# Import kelas Animator dan Enum dari lokasi yang benar
from .animation_manager import (
    StackedWidgetAnimator,
    AnimationType,
    SlideDirection,
)  # Sesuaikan '.animation_manager'


def slide(
    animator: StackedWidgetAnimator,
    stack_widget: QStackedWidget,
    target,
    direction: SlideDirection,
    duration: int = 400,
    curve: QEasingCurve.Type = QEasingCurve.Type.OutExpo,
    on_mid_transition: Optional[Callable] = None,
):  # Kurva bisa jadi parameter preset
    """Melakukan transisi SLIDE + FADE."""
    try:
        if stack_widget.currentWidget() is target:
            return
    except RuntimeError:
        return

    anim_type = AnimationType.FADE  # Default
    if direction == SlideDirection.LEFT:
        anim_type = AnimationType.SLIDE_LEFT
    elif direction == SlideDirection.RIGHT:
        anim_type = AnimationType.SLIDE_RIGHT
    elif direction == SlideDirection.UP:
        anim_type = AnimationType.SLIDE_UP
    elif direction == SlideDirection.DOWN:
        anim_type = AnimationType.SLIDE_DOWN

    duration_out = int(duration * 0.4)
    duration_in = int(duration * 0.6)
    curve_out_slide = curve  # Gunakan kurva yang sama agar konsisten halusnya (OutExpo)
    curve_in_slide = curve  # Kurva masuk sesuai parameter

    animator.transition_in(
        stack_widget,
        target,
        animation_type=anim_type,
        duration_out=duration_out,
        duration_in=duration_in,
        curve_out=curve_out_slide,
        curve_in=curve_in_slide,
        on_mid_transition=on_mid_transition,
    )
