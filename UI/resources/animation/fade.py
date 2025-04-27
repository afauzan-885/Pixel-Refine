from PyQt6.QtWidgets import QStackedWidget, QWidget
from PyQt6.QtCore import QEasingCurve
from .animation_manager import StackedWidgetAnimator, AnimationType

def fade_in(animator: StackedWidgetAnimator,
           stack_widget: QStackedWidget,
           target,
           duration: int = 300):
    """ Melakukan transisi FADE. """
    duration_out = int(duration * 0.4)
    duration_in = int(duration * 0.6)
    animator.transition_in(stack_widget, target,
                           animation_type=AnimationType.FADE,
                           duration_out=duration_out,
                           duration_in=duration_in,
                           curve_out=animator.DEFAULT_CURVE_OUT,
                           curve_in=animator.DEFAULT_CURVE_IN)
    
def fade_out(animator: StackedWidgetAnimator,
             widget: QWidget,
             duration: int = 300, # Gunakan durasi default atau sesuaikan
             curve: QEasingCurve.Type = QEasingCurve.Type.OutQuad, # Default curve
             on_finished_callback=None):
    """
    Memulai animasi fade-out (opacity 1.0 -> 0.0) pada sebuah widget
    menggunakan instance animator yang diberikan.

    Args:
        animator: Instance StackedWidgetAnimator yang akan menjalankan animasi.
        widget: Widget yang akan dianimasikan.
        duration: Durasi animasi dalam milidetik.
        curve: Kurva easing yang akan digunakan.
        on_finished_callback: Fungsi yang akan dipanggil setelah animasi selesai.
    """
    # Cukup panggil metode fade_out pada instance animator yang sebenarnya
    animator.transition_out(widget=widget,
                      duration=duration,
                      curve=curve,
                      on_finished_callback=on_finished_callback)