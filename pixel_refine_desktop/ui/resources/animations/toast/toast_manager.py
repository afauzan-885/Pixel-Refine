# UI/resources/toast_manager.py  (atau lokasi lain yang sesuai)

import weakref
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QGraphicsOpacityEffect,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)
from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
    Slot,
    QObject,
    QPoint,
    QRect,
    QSize,
)
from PySide6.QtGui import QFont, QColor
from enum import Enum, auto

from pixel_refine_desktop.ui.resources.animations.fade import fade_in, fade_out
from pixel_refine_desktop.ui.resources.animations.animation_manager import (
    StackedWidgetAnimator,
    AnimationType,
)


class ToastPosition(Enum):
    BOTTOM_CENTER = auto()
    TOP_CENTER = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    CENTER = auto()
    # Tambahkan posisi lain jika perlu


class ToastAnimation(Enum):
    FADE = auto()
    SLIDE_FROM_BOTTOM = auto()
    SLIDE_FROM_TOP = auto()
    SLIDE_FROM_LEFT = auto()
    SLIDE_FROM_RIGHT = auto()
    # Tambahkan animasi lain jika perlu (misal FADE_AND_SLIDE)


class ToastWidget(QFrame):
    def __init__(self, message: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("ToastWidgetWrapper")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Layout Wrapper
        wrapper_layout = QVBoxLayout(self)
        # Margin 20px sudah cukup aman agar shadow tidak terpotong saat nempel
        wrapper_layout.setContentsMargins(20, 20, 20, 20)
        wrapper_layout.setSpacing(0)

        # --- CONTAINER DALAM ---
        self.content_frame = QFrame()
        self.content_frame.setObjectName("ToastContent")
        self.content_frame.setStyleSheet(
            """
            #ToastContent {
                background-color: #FCFEFF; 
                border: 1px solid #ECEDED;
                border-radius: 4px; 
            }
        """
        )

        # --- SHADOW SETUP (Disesuaikan agar menempel) ---
        shadow = QGraphicsDropShadowEffect(self.content_frame)

        # Blur radius 25-30 membuat shadow terlihat lembut tapi tidak "terbang"
        shadow.setBlurRadius(25)

        # Offset Y kecil (4-6) membuat shadow terlihat menempel di bawah toast
        shadow.setXOffset(0)
        shadow.setYOffset(4)

        # Hitam 70% (179)
        shadow.setColor(QColor(0, 0, 0, 179))
        self.content_frame.setGraphicsEffect(shadow)

        # --- ISI KONTEN ---
        content_layout = QHBoxLayout(self.content_frame)
        content_layout.setContentsMargins(0, 0, int(20 * 1.3), 0)
        content_layout.setSpacing(int(15 * 1.3))

        self.accent_line = QFrame()
        self.accent_line.setFixedWidth(4)
        self.accent_line.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        self.accent_line.setStyleSheet(
            "background-color: #7DDA58; border-top-left-radius: 2px; border-bottom-left-radius: 2px;"
        )

        self.label = QLabel(message)
        self.label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.label.setStyleSheet(
            "background: transparent; color: #212529; border: none; font-weight: 600;"
        )

        content_layout.addWidget(self.accent_line)
        content_layout.addWidget(self.label, 1)
        wrapper_layout.addWidget(self.content_frame)

        self.animator = StackedWidgetAnimator(self)
        self._is_blinking = False

    def setText(self, text: str):
        self.label.setText(text)

    def text(self) -> str:
        return self.label.text()

    def set_blinking(self, active: bool):
        if active:
            if not self._is_blinking:
                self._is_blinking = True
                self._run_blink_cycle()
        else:
            self._is_blinking = False
            # Reset opacity accent line jika perlu
            effect = self.accent_line.graphicsEffect()
            if isinstance(effect, QGraphicsOpacityEffect):
                effect.setOpacity(1.0)
            self.accent_line.show()

    def _run_blink_cycle(self):
        if not self._is_blinking:
            return
        # Gunakan fade_out pada komponen internal (accent_line), bukan seluruh toast
        fade_out(
            self.animator,
            self.accent_line,
            duration=100,
            curve=QEasingCurve.Type.InOutSine,
            hide_on_finish=False,
            on_finished_callback=self._on_blink_fade_out_complete,
        )

    def _on_blink_fade_out_complete(self):
        if not self._is_blinking:
            return
        fade_in(self.animator, self.accent_line, duration=800)
        QTimer.singleShot(800, self._run_blink_cycle)


class ToastManager(QObject):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._parent_ref = weakref.ref(parent)
        self._toast_label: ToastWidget | None = None
        self._show_anim: QPropertyAnimation | None = None
        self._hide_anim: QPropertyAnimation | None = None
        self._close_timer: QTimer | None = None
        self._current_animation_type: ToastAnimation = ToastAnimation.FADE

    # --- Konfigurasi Default ---
    default_duration = 3000
    default_font = QFont("Inter", 13)
    default_fade_duration = 200
    default_slide_duration = 400
    default_show_easing_curve = QEasingCurve.Type.OutCubic
    default_hide_easing_curve = QEasingCurve.Type.InCubic
    default_vertical_margin = 25
    default_horizontal_margin = 25
    default_animation = ToastAnimation.FADE

    @property
    def parent_widget(self) -> QWidget | None:
        return self._parent_ref()

    # --- API Publik ---
    @Slot(str)
    def show_message(self, message: str, duration=None, position=None, animation=None):
        actual_duration = duration if duration is not None else self.default_duration
        self._show(message, actual_duration, position, animation, False)

    @Slot(str)
    def show_progress(self, message: str, position=None, animation=None):
        self._show(message, None, position, animation, True)

    @Slot()
    def hide(self):
        if self._close_timer and self._close_timer.isActive():
            self._close_timer.stop()
        self._start_hide_animation()

    # --- Logika Inti ---
    def _show(self, message, duration, position, animation, is_progress_update):
        parent = self.parent_widget
        if not parent:
            return

        actual_position = (
            ToastPosition.BOTTOM_RIGHT
        )  # Sesuai permintaan Anda sebelumnya
        actual_animation = (
            animation if animation is not None else self.default_animation
        )
        self._current_animation_type = actual_animation

        self._clear_running_operations()

        # Update jika sedang Progress
        if is_progress_update and self._toast_label and self._toast_label.isVisible():
            self._toast_label.setText(message)
            self._toast_label.set_blinking(True)
            self._toast_label.adjustSize()

            final_pos, final_size = self._calculate_geometry(actual_position)
            if final_pos:
                self._toast_label.setGeometry(QRect(final_pos, final_size))
            return

        # Buat Toast Baru
        self._cleanup_toast_widget()
        self._toast_label = ToastWidget(message, parent)
        self._toast_label.label.setFont(self.default_font)
        self._toast_label.set_blinking(is_progress_update)
        self._toast_label.adjustSize()

        final_pos, final_size = self._calculate_geometry(actual_position)
        if not final_pos:
            return

        # Set Posisi Awal
        initial_pos = final_pos
        if actual_animation != ToastAnimation.FADE:
            initial_pos = self._get_offscreen_start_pos(
                actual_animation, final_pos, final_size
            )

        self._toast_label.setGeometry(QRect(initial_pos, final_size))
        self._toast_label.show()

        # Jalankan Animasi Masuk
        if actual_animation == ToastAnimation.FADE:
            self._start_fade_in_animation()
        else:
            self._start_slide_in_animation(final_pos)

        # Setup Auto Close Timer
        if duration is not None:
            self._close_timer = QTimer(self)
            self._close_timer.setSingleShot(True)
            self._close_timer.timeout.connect(self.hide)
            self._close_timer.start(duration)

    def _start_fade_in_animation(self):
        if self._toast_label:
            fade_in(
                self._toast_label.animator,
                self._toast_label,
                duration=self.default_fade_duration,
            )

    def _start_fade_out_animation(self):
        """Menggunakan fade.py untuk animasi keluar."""
        # CEK HANYA _toast_label, jangan cek _opacity_effect lagi
        if not self._toast_label:
            self._on_hide_animation_finished()
            return

        # Panggil fungsi fade_out dari script fade.py
        # Fungsi ini akan secara otomatis mencari/membuat QGraphicsOpacityEffect
        # pada ToastWidgetWrapper Anda tanpa perlu Anda simpan di Manager.
        fade_out(
            animator=self._toast_label.animator,
            widget=self._toast_label,
            duration=self.default_fade_duration,
            curve=self.default_hide_easing_curve,
            hide_on_finish=False,
            on_finished_callback=self._on_hide_animation_finished,
        )

    def _start_slide_in_animation(self, target_pos):
        if not self._toast_label:
            return
        self._show_anim = QPropertyAnimation(self._toast_label, b"pos", self)
        self._show_anim.setDuration(self.default_slide_duration)
        self._show_anim.setEndValue(target_pos)
        self._show_anim.setEasingCurve(self.default_show_easing_curve)
        self._show_anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _start_slide_out_animation(self):
        if not self._toast_label:
            return
        target_pos = self._get_offscreen_start_pos(
            self._current_animation_type,
            self._toast_label.pos(),
            self._toast_label.size(),
        )
        self._hide_anim = QPropertyAnimation(self._toast_label, b"pos", self)
        self._hide_anim.setDuration(self.default_slide_duration)
        self._hide_anim.setEndValue(target_pos)
        self._hide_anim.setEasingCurve(self.default_hide_easing_curve)
        self._hide_anim.finished.connect(self._on_hide_animation_finished)
        self._hide_anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _start_hide_animation(self):
        """Memutuskan jenis animasi hide yang digunakan."""
        if not self._toast_label:
            return

        # Hentikan animasi show yang mungkin sedang berjalan
        if (
            self._show_anim
            and self._show_anim.state() == QPropertyAnimation.State.Running
        ):
            self._show_anim.stop()
        self._show_anim = None

        if self._current_animation_type == ToastAnimation.FADE:
            self._start_fade_out_animation()
        else:
            self._start_slide_out_animation()

    def _on_hide_animation_finished(self):
        self._cleanup_toast_widget()

    def _clear_running_operations(self):
        if self._close_timer:
            self._close_timer.stop()
        if self._show_anim:
            self._show_anim.stop()
        if self._hide_anim:
            self._hide_anim.stop()
        self._show_anim = None
        self._hide_anim = None

    def _cleanup_toast_widget(self):
        if self._toast_label:
            self._toast_label.hide()
            self._toast_label.deleteLater()
            self._toast_label = None

    def _calculate_geometry(
        self, position: ToastPosition
    ) -> tuple[QPoint | None, QSize | None]:
        """Menghitung posisi akhir (top-left) dan ukuran toast."""
        parent = self.parent_widget
        if not self._toast_label or not parent:
            return None, None

        parent_width = parent.width()
        parent_height = parent.height()

        # Fallback jika parent belum di-layout
        if parent_width <= 0 or parent_height <= 0:
            parent_size_hint = parent.sizeHint()
            parent_width = max(parent_width, parent_size_hint.width())
            parent_height = max(parent_height, parent_size_hint.height())
            if parent_width <= 0 or parent_height <= 0:
                print("Warning: Could not determine parent size for toast positioning.")
                return None, None

        # Dapatkan ukuran toast (adjustSize sudah dipanggil)
        toast_size = self._toast_label.sizeHint()
        toast_width = toast_size.width()
        toast_height = toast_size.height()
        if toast_width <= 0 or toast_height <= 0:
            margins = self._toast_label.contentsMargins()
            fm = self._toast_label.fontMetrics()
            text_width = fm.horizontalAdvance(self._toast_label.text())
            text_height = fm.height()
            text_width = fm.horizontalAdvance(self._toast_label.text())
            text_height = fm.height()
            # Scaled up padding (+30%)
            padding_v = int(15 * 2 * 1.3)
            # Left (0) + Right (26) + Spacing (19.5) + AccentWidth (4)
            padding_h = int(20 * 1.3) + int(15 * 1.3) + 4
            toast_width = text_width + padding_h + margins.left() + margins.right()
            toast_height = text_height + padding_v + margins.top() + margins.bottom()
            if toast_width <= 0 or toast_height <= 0:
                print("Warning: Could not determine toast size.")
                return None, None

        h_margin = self.default_horizontal_margin
        v_margin = self.default_vertical_margin

        match position:
            case ToastPosition.BOTTOM_CENTER:
                x = (parent_width - toast_width) // 2
                y = parent_height - toast_height - v_margin
            case ToastPosition.TOP_CENTER:
                x = (parent_width - toast_width) // 2
                y = v_margin
            case ToastPosition.BOTTOM_LEFT:
                x = h_margin
                y = parent_height - toast_height - v_margin
            case ToastPosition.BOTTOM_RIGHT:
                x = parent_width - toast_width - h_margin
                y = parent_height - toast_height - v_margin
            case ToastPosition.TOP_LEFT:
                x = h_margin
                y = v_margin
            case ToastPosition.TOP_RIGHT:
                x = parent_width - toast_width - h_margin
                y = v_margin
            case ToastPosition.CENTER:
                x = (parent_width - toast_width) // 2
                y = (parent_height - toast_height) // 2
            case _:
                print(
                    f"Warning: Invalid ToastPosition '{position}'. Defaulting to BOTTOM_CENTER."
                )
                x = (parent_width - toast_width) // 2
                y = parent_height - toast_height - v_margin

        x = max(0, x)
        y = max(0, y)

        return QPoint(x, y), QSize(toast_width, toast_height)

    def _get_offscreen_start_pos(
        self, animation_type: ToastAnimation, final_pos: QPoint, toast_size: QSize
    ) -> QPoint:
        """Menentukan posisi awal di luar layar untuk animasi slide."""
        parent = self.parent_widget
        if not parent:
            return final_pos  # Fallback

        parent_height = parent.height()
        parent_width = parent.width()
        toast_height = toast_size.height()
        toast_width = toast_size.width()

        match animation_type:
            case ToastAnimation.SLIDE_FROM_BOTTOM:
                return QPoint(final_pos.x(), parent_height)
            case ToastAnimation.SLIDE_FROM_TOP:
                return QPoint(final_pos.x(), -toast_height)
            case ToastAnimation.SLIDE_FROM_LEFT:
                return QPoint(-toast_width, final_pos.y())
            case ToastAnimation.SLIDE_FROM_RIGHT:
                return QPoint(parent_width, final_pos.y())
            case _:
                return final_pos
