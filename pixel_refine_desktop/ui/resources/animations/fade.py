from typing import Optional
from PySide6.QtWidgets import QStackedWidget, QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QTimer
from .animation_manager import StackedWidgetAnimator, AnimationType


def fade_in(
    animator: StackedWidgetAnimator,
    target_widget: QWidget,
    stack_widget: Optional[QStackedWidget] = None,  # Opsional
    duration: int = 300,
):
    """
    Melakukan transisi FADE.
    - Jika 'stack_widget' diisi: Melakukan transisi halaman stack.
    - Jika 'stack_widget' None: Melakukan fade-in pada 'target_widget' biasa.
    """

    # === SKENARIO 1: Stacked Widget Transition ===
    if stack_widget is not None:
        duration_out = int(duration * 0.4)
        duration_in = int(duration * 0.6)
        animator.transition_in(
            stack_widget,
            target_widget,
            animation_type=AnimationType.FADE,
            duration_out=duration_out,
            duration_in=duration_in,
            curve_out=animator.DEFAULT_CURVE_OUT,
            curve_in=animator.DEFAULT_CURVE_IN,
        )
        return

    # === SKENARIO 2: Standalone Widget Fade In ===
    if not target_widget:
        return

    # 1. Siapkan Opacity Effect
    try:
        effect = target_widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(target_widget)
            target_widget.setGraphicsEffect(effect)
    except RuntimeError:
        return  # Widget sudah dihapus dari C++ side

    # 2. Mulai dari transparan (0.0) lalu tampilkan widget
    effect.setOpacity(0.0)
    target_widget.show()
    target_widget.raise_()  # Opsional: angkat ke atas agar terlihat

    # 3. Buat animasi manual (karena transition_in animator khusus stack)
    anim = QPropertyAnimation(effect, b"opacity", target_widget)
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(animator.DEFAULT_CURVE_IN)

    # Cleanup referensi animasi setelah selesai agar tidak garbage collected terlalu dini
    # Kita bisa simpan di animator._active_transitions sementara atau biarkan parent widget mengurusnya
    # Di sini kita set parent anim ke target_widget agar aman.
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


def fade_out(
    animator: StackedWidgetAnimator,
    widget: QWidget,
    duration: int = 300,
    curve: QEasingCurve.Type = QEasingCurve.Type.OutQuad,
    on_finished_callback=None,
    hide_on_finish: bool = True,
):  # Tambahan parameter
    """
    Memulai animasi fade-out.

    Args:
        hide_on_finish (bool): Jika True, widget akan di-hide() setelah animasi selesai.
                               Sangat penting untuk widget biasa agar tidak memblokir mouse.
    """
    if not widget or not widget.isVisible() or not widget.isEnabled():
        if on_finished_callback:
            on_finished_callback()
        return

    # Kita bungkus callback agar bisa melakukan hide() otomatis
    def internal_callback():
        if hide_on_finish and widget:
            try:
                widget.hide()
            except RuntimeError:
                pass  # Widget mungkin sudah dihapus

        if on_finished_callback:
            try:
                on_finished_callback()
            except RuntimeError:
                pass

    animator.transition_out(
        widget=widget,
        duration=duration,
        curve=curve,
        on_finished_callback=internal_callback,
    )
