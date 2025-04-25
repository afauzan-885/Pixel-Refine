from PyQt6.QtWidgets import QStackedWidget
from PyQt6.QtCore import QEasingCurve
# Import kelas Animator dan Enum dari lokasi yang benar
from .animation_manager import StackedWidgetAnimator, AnimationType

def zoom(animator: StackedWidgetAnimator,
           stack_widget: QStackedWidget,
           target,
           duration: int = 400):
    """ Melakukan transisi ZOOM + FADE. """
    duration_out = int(duration * 0.4)
    duration_in = int(duration * 0.6)
    curve = QEasingCurve.Type.InOutCirc # Kurva zoom

    animator.transition_to(stack_widget, target,
                           animation_type=AnimationType.ZOOM,
                           duration_out=duration_out,
                           duration_in=duration_in,
                           curve_out=curve,
                           curve_in=curve)