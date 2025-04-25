from PyQt6.QtWidgets import QStackedWidget, QWidget
from PyQt6.QtCore import QEasingCurve
# Import kelas Animator dan Enum dari lokasi yang benar
from .animation_manager import StackedWidgetAnimator, AnimationType

def fade(animator: StackedWidgetAnimator,
           stack_widget: QStackedWidget,
           target,
           duration: int = 300):
    """ Melakukan transisi FADE. """
    duration_out = int(duration * 0.4)
    duration_in = int(duration * 0.6)
    animator.transition_to(stack_widget, target,
                           animation_type=AnimationType.FADE,
                           duration_out=duration_out,
                           duration_in=duration_in,
                           curve_out=animator.DEFAULT_CURVE_OUT, # Akses default dari instance
                           curve_in=animator.DEFAULT_CURVE_IN)

