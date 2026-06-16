from PySide6.QtWidgets import QWidget
from .animation_manager import WidgetLifecycleAnimator

_default_animator = WidgetLifecycleAnimator()


def delete(
    widget: QWidget,
    animator: WidgetLifecycleAnimator = None,
    duration: int = 500,
    drop_distance: int = 60,
    on_finished_callback=None,
):
    """
    Menghapus widget dengan efek 'Runtuh/Jatuh'.

    Logic didelegasikan sepenuhnya ke animation_manager.WidgetLifecycleAnimator.

    Args:
        widget: Widget target.
        animator: Instance WidgetLifecycleAnimator (opsional).
        duration: Durasi total animasi (ms).
        drop_distance: Seberapa jauh widget 'jatuh' ke bawah (px).
        on_finished_callback: Fungsi yang dipanggil sebelum widget dimusnahkan.
    """
    if not widget:
        return

    # Gunakan animator yang diberikan user, atau gunakan default
    manager = animator if animator else _default_animator

    manager.animate_delete(
        widget=widget,
        duration=duration,
        use_drop_effect=True,
        drop_distance=drop_distance,
        on_finished_callback=on_finished_callback,
    )
