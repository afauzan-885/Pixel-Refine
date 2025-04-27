from PyQt6.QtWidgets import QStackedWidget
from PyQt6.QtCore import QEasingCurve
# Import kelas Animator dan Enum dari lokasi yang benar
from .animation_manager import StackedWidgetAnimator, AnimationType, SlideDirection # Sesuaikan '.animation_manager'

def slide(animator: StackedWidgetAnimator,
            stack_widget: QStackedWidget,
            target,
            direction: SlideDirection,
            duration: int = 400,
            curve: QEasingCurve.Type = QEasingCurve.Type.OutExpo): # Kurva bisa jadi parameter preset
    """ Melakukan transisi SLIDE + FADE. """
    anim_type = AnimationType.FADE # Default
    if direction == SlideDirection.LEFT: anim_type = AnimationType.SLIDE_LEFT
    elif direction == SlideDirection.RIGHT: anim_type = AnimationType.SLIDE_RIGHT
    elif direction == SlideDirection.UP: anim_type = AnimationType.SLIDE_UP
    elif direction == SlideDirection.DOWN: anim_type = AnimationType.SLIDE_DOWN

    duration_out = int(duration * 0.4)
    duration_in = int(duration * 0.6)
    curve_out_slide = QEasingCurve.Type.Linear # Kurva keluar untuk slide
    curve_in_slide = curve                  # Kurva masuk sesuai parameter

    animator.transition_in(stack_widget, target,
                           animation_type=anim_type,
                           duration_out=duration_out,
                           duration_in=duration_in,
                           curve_out=curve_out_slide,
                           curve_in=curve_in_slide)