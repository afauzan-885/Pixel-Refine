import weakref
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional
import time

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
    Property,
    QParallelAnimationGroup,
    QEvent,
)
from PySide6.QtGui import QFont, QColor
from resources.animations.animation_manager import (
    WidgetLifecycleAnimator,
)


class ToastPosition(Enum):
    BOTTOM_CENTER = auto()
    TOP_CENTER = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    CENTER = auto()


class ToastAnimation(Enum):
    FADE = auto()
    SLIDE_FROM_BOTTOM = auto()
    SLIDE_FROM_TOP = auto()
    SLIDE_FROM_LEFT = auto()
    SLIDE_FROM_RIGHT = auto()


class ToastPriority(Enum):
    URGENT = 3
    HIGH = 2
    NORMAL = 1
    LOW = 0


class ToastWidget(QFrame):
    def __init__(
        self,
        message: str,
        priority: ToastPriority,
        category: str | None = None,
        parent: QWidget | None = None,
        position=ToastPosition.BOTTOM_RIGHT,
    ):
        super().__init__(parent)
        self.priority = priority
        self.category = category
        self.position = position
        self.timestamp = time.time()
        self.setObjectName("ToastWidgetWrapper")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(
            "background: transparent;"
        )  # Pastikan wrapper benar-benar transparan

        # Layout Wrapper
        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.setContentsMargins(
            20, 10, 20, 10
        )  # Reduced vertical margin for stacking
        wrapper_layout.setSpacing(0)

        # --- CONTAINER DALAM ---
        self.content_frame = QFrame()
        self.content_frame.setObjectName("ToastContent")

        # Setup theme-aware backgrounds
        from resources.GenericUILibrary.theme import get_theme
        theme = get_theme()

        # Color based on priority
        accent_color = "#7DDA58"  # NORMAL (Green)

        if priority == ToastPriority.URGENT:
            accent_color = "#FF4B4B"  # Red
        elif priority == ToastPriority.HIGH:
            accent_color = "#FFA500"  # Orange
        elif priority == ToastPriority.LOW:
            accent_color = "#A0A0A0"  # Grey

        # Convert hex background to rgba for translucent effect
        def hex_to_rgba(hex_str, alpha=235):
            hex_str = hex_str.lstrip('#')
            if len(hex_str) == 3:
                hex_str = ''.join(c*2 for c in hex_str)
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return f"rgba({r}, {g}, {b}, {alpha})"

        bg_rgba = hex_to_rgba(theme.bg_card, 235)
        border_color = theme.border_color

        self.content_frame.setStyleSheet(
            f"""
            #ToastContent {{
                background-color: {bg_rgba}; 
                border: 1px solid {border_color};
                border-radius: 4px; 
            }}
            """
        )

        # --- SHADOW SETUP ---
        shadow = QGraphicsDropShadowEffect(self.content_frame)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 179))
        self.content_frame.setGraphicsEffect(shadow)

        # --- ISI KONTEN ---
        content_layout = QHBoxLayout(self.content_frame)
        # Compact margins
        content_layout.setContentsMargins(0, 0, 10, 0)
        content_layout.setSpacing(15)

        self.accent_line = QFrame()
        self.accent_line.setFixedWidth(4)
        self.accent_line.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        self.accent_line.setStyleSheet(
            f"background-color: {accent_color}; border-top-left-radius: 2px; border-bottom-left-radius: 2px;"
        )

        self.label = QLabel(message)
        self.label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.label.setStyleSheet(
            f"background: transparent; color: {theme.text_primary}; border: none; font-weight: 600;"
        )

        content_layout.addWidget(self.accent_line)
        content_layout.addWidget(self.label, 1)
        wrapper_layout.addWidget(self.content_frame)

        # self.setFixedSize(self.sizeHint()) # Initial size

    def text(self) -> str:
        return self.label.text()

    def setText(self, text: str):
        self.label.setText(text)
        self.adjustSize()

    # Blinking support (simplified)
    def set_blinking(self, active: bool):
        pass  # Optional impl


class ToastManager(QObject):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._parent_ref = weakref.ref(parent)
        self._active_toasts: List[ToastWidget] = []
        self._timers = {}  # widget -> QTimer
        self._last_update_time = {}  # category -> time (For throttling)
        self.max_toasts = 5
        self.spacing = 5
        self.lifecycle_animator = WidgetLifecycleAnimator(self)
        if parent:
            parent.installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched == self.parent_widget and event.type() == QEvent.Type.Resize:
            self._reposition_toasts(animate=False)
        return super().eventFilter(watched, event)

    @property
    def parent_widget(self) -> QWidget | None:
        return self._parent_ref()

    # --- API Publik ---
    @Slot(str)
    def show_message(
        self,
        message: str,
        duration=3000,
        position=ToastPosition.BOTTOM_RIGHT,
        animation=ToastAnimation.SLIDE_FROM_BOTTOM,
        priority: str = "NORMAL",
        category: str | None = None,
        single_mode: bool = False,
    ):
        """
        Menampilkan pesan toast baru.
        Allowed priorities: "URGENT", "HIGH", "NORMAL", "LOW"
        Args:
            category: ID unik (string) untuk identifikasi toast ini agar bisa di-update (reusable).
                      Jika None, dianggap toast transient (sekali lewat).
        """
        # Convert string priority to Enum
        try:
            prio_enum = ToastPriority[priority.upper()]
        except KeyError:
            prio_enum = ToastPriority.NORMAL

        self._add_toast(
            message, duration, position, animation, prio_enum, category, single_mode
        )

    @Slot(str)
    def show_progress(
        self,
        message: str,
        category: str,  # REQUIRED NOW
        position=ToastPosition.BOTTOM_RIGHT,
        animation=None,
        priority: str = "HIGH",
        single_mode: bool = False,
        bypass_throttle: bool = False,
    ):
        target_toast = None
        current_time = time.time()

        if category:
            # THROTTLING (Peredam Spawning)
            # Batasi update visual maksimal 20fps (setiap 0.05 detik)
            last_time = self._last_update_time.get(category, 0)

            # General Logic: Use explicit bypass argument instead of hardcoded strings
            if not bypass_throttle and (current_time - last_time) < 0.15:
                # Skip update ini untuk menghemat resource
                return

            self._last_update_time[category] = current_time

            for t in self._active_toasts:
                if t.category == category:
                    target_toast = t
                    break

        # EXCLUSIVE/SINGLE MODE LOGIC:
        if single_mode:
            # Drop everyone else except target (if exists)
            to_remove = []
            for t in self._active_toasts:
                if t != target_toast:
                    to_remove.append(t)
            for t in to_remove:
                self._remove_toast(t)

        if target_toast:
            # 1. CLEANUP (Aggressive)
            # Remove any lingering overlays immediately
            for child in target_toast.children():
                if (
                    isinstance(child, QLabel)
                    and child.objectName() == "SnapshotOverlay"
                ):
                    child.hide()
                    child.deleteLater()

            # 2. CAPTURE GEOMETRY (For Smooth Resize)
            old_geo = target_toast.geometry()

            # NOTE: User requested to DISABLE visible snapshot overlay to prevent ghosting.
            # "overlaynya tidak terlihat agar tidak menimbulkan ghosting"
            # We skip creating the SnapshotOverlay but keep the geometry freeze-and-animate
            # so the box still resizes smoothly (just updated text appears instantly).

            # 3. Update Content & Recalculate SizeHint
            target_toast.setText(message)
            target_toast.adjustSize()

            # 4. Freeze Visual State (paksakan tetap di ukuran lama utk awal animasi)
            target_toast.setGeometry(old_geo)

            # 5. Trigger Global Reposition (animates resize/move)
            self._reposition_toasts()

            # No fade animation needed since overlay is gone.
        else:
            self.show_message(
                message,
                duration=0,
                position=position,
                priority=priority,
                category=category,
                single_mode=single_mode,
            )

    @Slot()
    def hide(self):
        """Hide all or specific? Default implementation hides all for compatibility."""
        # For multi-stack, typically we don't 'hide all' frequently.
        # But if called without args, maybe remove the oldest? or all?
        # Let's remove ALL for safety/reset.
        while self._active_toasts:
            self._remove_toast(self._active_toasts[0])

    @Slot(str)
    def hide_specific(self, message_substring: str):
        """Hide toast containing specific text."""
        to_remove = []
        for t in self._active_toasts:
            if message_substring in t.text():
                to_remove.append(t)
        for t in to_remove:
            self._remove_toast(t)

    @Slot(str)
    def hide_category(self, category: str):
        """Hide all toasts with specific category."""
        to_remove = []
        for t in self._active_toasts:
            if t.category == category:
                to_remove.append(t)
        for t in to_remove:
            self._remove_toast(t)

    # --- Core Logic ---
    def _add_toast(
        self,
        message,
        duration,
        position,
        animation,
        priority: ToastPriority,
        category: str | None = None,
        single_mode: bool = False,
    ):
        parent = self.parent_widget
        if not parent:
            return

        # EXCLUSIVE MODE (Create New): Remove all others first
        if single_mode:
            while self._active_toasts:
                # Check if we accidentally found same category inside list?
                # Logic above handles update, so here means we are creating NEW.
                # So wipe everything.
                self._remove_toast(self._active_toasts[0])

        # PERFORMANCE GUARD:
        # Jika category diberikan, cek apakah sudah ada toast dengan category sama.
        # Jika ada, update teksnya & reset timer, jangan buat baru (duplicate).
        if category:
            for t in self._active_toasts:
                if t.category == category:
                    t.setText(message)
                    # Reset timer to extend duration? Or keep as is?
                    # Generally new message = reset duration.
                    if t in self._timers:
                        self._timers[t].start(duration)
                    return

        # 1. Create Widget
        toast = ToastWidget(message, priority, category, parent, position)
        toast.adjustSize()
        toast.show()

        # 2. Add to list
        self._active_toasts.append(toast)

        # 3. Sort List (Priority DESC, Timestamp DESC (Newest First for Tie-Break))
        # Logic: Highest priority first. If same priority, newest (biggest timestamp) first.
        # Tapi tunggu, untuk visual stack Bottom-Up:
        # Posisi paling bawah (y terbesar) biasanya adalah Slot 0 (Prime).
        # Jadi kita ingin item Paling Penting & Paling Baru ada di index 0 list ini
        # (jika index 0 dipetakan ke posisi paling bawah).

        self._active_toasts.sort(
            key=lambda t: (t.priority.value, t.timestamp), reverse=True
        )

        # 4. Enforce Limit (Remove lowest priority / oldest if > max)
        if len(self._active_toasts) > self.max_toasts:
            # Remove last item (Lowest priority/Oldest)
            removed = self._active_toasts.pop()
            removed.hide()
            removed.deleteLater()

        # 5. Animate Entry (Slide In to calculated position)
        # Kita hitung target posisi nanti di _reposition, tapi untuk animasi masuk
        # kita butuh posisi awal offscreen.

        # Trigger reposition for ALL toasts (shifting existing ones, placing new one)
        self._reposition_toasts()

        # 6. Setup Auto-Close Timer
        if duration and duration > 0:
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._remove_toast(toast))
            timer.start(duration)
            self._timers[toast] = timer

    def _remove_toast(self, toast: ToastWidget):
        if toast not in self._active_toasts:
            return

        # Remove timer
        if toast in self._timers:
            self._timers[toast].stop()
            del self._timers[toast]

        # Animasi Keluar (Delegated to WidgetLifecycleAnimator)
        self._active_toasts.remove(toast)

        # Uses the shared animation logic for consistent Slide Down + Fade
        self.lifecycle_animator.animate_delete(
            widget=toast, duration=300, use_drop_effect=True, drop_distance=30
        )

        # Shift sisanya
        self._reposition_toasts()

    def _reposition_toasts(self, animate: bool = True):
        """Mengatur ulang posisi semua toast berdasarkan urutan di list."""
        parent = self.parent_widget
        if not parent:
            return

        parent_rect = parent.rect()
        margin_x = 25
        margin_y = 25

        # Track bottom offset for each position to stack them correctly
        bottom_y_right = parent_rect.height() - margin_y
        right_x = parent_rect.width() - margin_x
        
        bottom_y_left = parent_rect.height() - margin_y
        left_x = margin_x

        # Iterate sorted list (Index 0 = Bottom-most / Prime)
        for i, toast in enumerate(self._active_toasts):
            # FIX TRUNCATION: Use sizeHint() because actual width() might be
            # frozen to old size by geometry animation logic in show_progress.
            hint = toast.sizeHint()
            t_width = hint.width()
            t_height = hint.height()

            pos_enum = getattr(toast, "position", ToastPosition.BOTTOM_RIGHT)
            if pos_enum == ToastPosition.BOTTOM_LEFT:
                target_x = left_x
                target_y = bottom_y_left - t_height
                bottom_y_left = target_y - self.spacing
            else:
                target_x = right_x - t_width
                target_y = bottom_y_right - t_height
                bottom_y_right = target_y - self.spacing

            # Target geometry
            target_geo = QRect(int(target_x), int(target_y), t_width, t_height)

            if not animate:
                # Stop any existing geometry animations to avoid conflicts
                for attr_name in list(toast.__dict__.keys()):
                    if attr_name.startswith("_pos_anim_"):
                        anim = getattr(toast, attr_name)
                        if anim:
                            try:
                                anim.stop()
                            except Exception:
                                pass
                        try:
                            delattr(toast, attr_name)
                        except AttributeError:
                            pass
                toast.setGeometry(target_geo)
                continue

            if toast.pos().isNull():
                # First show: start slightly below (Slide Up effect)
                toast.setGeometry(int(target_x), int(target_y) + 50, t_width, t_height)
                toast.setWindowOpacity(0)

            # Create animation for smooth stack shift & resize
            anim = QPropertyAnimation(toast, b"geometry", self)
            anim.setDuration(400)
            anim.setStartValue(toast.geometry())
            anim.setEndValue(target_geo)
            # Menggunakan Curve OutExpo seperti di slide.py
            anim.setEasingCurve(QEasingCurve.Type.OutExpo)

            # Animasi Opacity untuk entry
            if toast.windowOpacity() == 0:
                anim_op = QPropertyAnimation(toast, b"windowOpacity", self)
                anim_op.setDuration(300)
                anim_op.setStartValue(0.0)
                anim_op.setEndValue(1.0)
                anim_op.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

            anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

            # Keep ref to prevent GC if needed, though parent ownership helps
            setattr(toast, f"_pos_anim_{time.time()}", anim)
