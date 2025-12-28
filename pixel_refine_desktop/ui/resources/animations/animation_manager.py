import weakref
from PySide6.QtWidgets import (
    QStackedWidget,
    QGraphicsOpacityEffect,
    QWidget,
    QApplication,
    QLabel,
)
from PySide6.QtCore import (
    QObject,
    QPropertyAnimation,
    QEasingCurve,
    QSequentialAnimationGroup,
    Qt,
    Slot,
    QParallelAnimationGroup,
    QPoint,
    QRect,
    QTimer,
)

from enum import Enum, auto


class AnimationType(Enum):
    FADE = auto()
    SLIDE_LEFT = auto()
    SLIDE_RIGHT = auto()
    SLIDE_UP = auto()
    SLIDE_DOWN = auto()
    ZOOM = auto()


class SlideDirection(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()


class StackedWidgetAnimator(QObject):
    """
    Animator yang TAHAN BANTING dan SELF-HEALING untuk QStackedWidget.
    Dirancang untuk menangani penghapusan widget di tengah animasi dengan aman.
    """

    DEFAULT_DURATION_OUT = 150
    DEFAULT_DURATION_IN = 250
    DEFAULT_CURVE_OUT = QEasingCurve.Type.OutQuad
    DEFAULT_CURVE_IN = QEasingCurve.Type.InQuad

    def __init__(self, parent=None):
        super().__init__(parent)
        self._animation_state = weakref.WeakKeyDictionary()
        self._standalone_anims = weakref.WeakKeyDictionary()  # Tracking per-widget

    def transition_out(
        self,
        widget: QWidget,
        duration: int = 300,
        curve: QEasingCurve.Type = QEasingCurve.Type.OutQuad,
        on_finished_callback=None,
    ):
        """
        Animator fade-out mandiri yang aman.
        """
        widget_ref = weakref.ref(widget) if widget else None

        if not widget_ref or not widget_ref():
            if on_finished_callback and callable(on_finished_callback):
                QTimer.singleShot(0, on_finished_callback)
            return

        target_widget = widget_ref()
        if target_widget is None:
            if on_finished_callback and callable(on_finished_callback):
                on_finished_callback()
            return

        parent = target_widget.parentWidget()
        if not parent:
            if on_finished_callback and callable(on_finished_callback):
                on_finished_callback()
            return

        # --- STRATEGI GHOSTING PIXMAP ---
        # 1. Ambil snapshot widget asli
        try:
            pixmap = target_widget.grab()
            geom = target_widget.geometry()
        except RuntimeError:
            if on_finished_callback and callable(on_finished_callback):
                on_finished_callback()
            return

        # 2. Buat widget "Hantu" (Ghost) di parent yang sama
        ghost = QLabel(parent)
        ghost.setPixmap(pixmap)
        ghost.setGeometry(geom)
        ghost.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # 3. Siapkan effect pada Ghost
        opacity_effect = QGraphicsOpacityEffect(ghost)
        ghost.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(1.0)
        ghost.show()
        ghost.raise_()

        # 4. Sembunyikan widget asli SEGERA untuk menghindari konflik QPainter
        try:
            target_widget.hide()
        except RuntimeError:
            pass

        # 5. Jalankan animasi pada Ghost
        anim = QPropertyAnimation(opacity_effect, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(curve)

        def on_anim_finished():
            try:
                ghost.deleteLater()
            except RuntimeError:
                pass
            if on_finished_callback and callable(on_finished_callback):
                on_finished_callback()

        anim.finished.connect(on_anim_finished)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def transition_in(
        self,
        stack_widget: QStackedWidget,
        target,
        animation_type: AnimationType = AnimationType.FADE,
        duration_out: int = DEFAULT_DURATION_OUT,
        duration_in: int = DEFAULT_DURATION_IN,
        curve_out: QEasingCurve.Type = DEFAULT_CURVE_OUT,
        curve_in: QEasingCurve.Type = DEFAULT_CURVE_IN,
    ):
        if self._is_animating(stack_widget):
            self._interrupt_transition(stack_widget)

        old_widget = stack_widget.currentWidget()
        new_widget, new_index = self._validate_target(stack_widget, target)

        if not new_widget or old_widget == new_widget:
            return

        # Skip animation if not visible (startup)
        if not stack_widget.isVisible():
            stack_widget.setCurrentIndex(new_index)
            return

        # --- Kunci diperoleh di sini ---
        self._animation_state[stack_widget] = {
            "old_widget_ref": weakref.ref(old_widget) if old_widget else None,
            "new_widget_ref": weakref.ref(new_widget),
            "new_index": new_index,
            "animation_type": animation_type,
            "duration_in": duration_in,
            "curve_in": curve_in,
        }

        if not old_widget:
            # Langsung ke animasi masuk jika tidak ada widget lama
            self._on_animation_out_finished(weakref.ref(stack_widget))
            return

        try:
            # Siapkan widget lama untuk transisi keluar
            effect = old_widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(old_widget)
                old_widget.setGraphicsEffect(effect)
            effect.setOpacity(1.0)
        except RuntimeError:
            self._clear_animation_state(stack_widget)  # Gunakan helper baru
            return

        out_group = QParallelAnimationGroup(self)
        fade_out = QPropertyAnimation(effect, b"opacity")
        fade_out.setDuration(duration_out)
        fade_out.setEasingCurve(curve_out)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        out_group.addAnimation(fade_out)

        geom_anim = self._create_outgoing_geometry_animation(
            old_widget, animation_type, duration_out, curve_out
        )
        if geom_anim:
            out_group.addAnimation(geom_anim)

        out_group.finished.connect(
            lambda sw_ref=weakref.ref(stack_widget): self._on_animation_out_finished(
                sw_ref
            )
        )

        state = self._animation_state.get(stack_widget)
        if not state or not state["old_widget_ref"]():
            self._clear_animation_state(stack_widget)
            return

        state["out_group"] = out_group
        out_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _is_animating(self, stack_widget: QStackedWidget) -> bool:
        """Periksa apakah ada animasi yang sedang berlangsung di QStackedWidget."""
        return stack_widget in self._animation_state

    def _clear_animation_state(self, stack_widget: QStackedWidget):
        """Hapus state animasi untuk QStackedWidget tertentu (melepas kunci)."""
        self._animation_state.pop(stack_widget, None)

    def _reset_widget_state(self, widget: QWidget, visible: bool = False):
        """Atur ulang properti visual widget dengan aman."""
        if not widget:
            return
        try:
            if widget.graphicsEffect():
                self._safe_remove_effect(widget)
            widget.move(0, 0)
            if visible:
                widget.show()
            else:
                widget.hide()
        except RuntimeError:
            # Widget mungkin sudah tidak ada lagi
            pass

    def _validate_target(self, stack_widget, target):
        target_widget = None
        target_index = -1
        if isinstance(target, QWidget):
            target_widget = target
            target_index = stack_widget.indexOf(target_widget)
        elif isinstance(target, int):
            target_index = target
            target_widget = stack_widget.widget(target_index)
        return target_widget, target_index

    def _create_outgoing_geometry_animation(self, widget, anim_type, duration, curve):
        geom_anim = None
        w = widget.width()
        h = widget.height()
        current_pos = widget.pos()
        end_value = None
        prop_name = None
        if anim_type == AnimationType.SLIDE_LEFT:
            prop_name, end_value = b"pos", QPoint(-w, current_pos.y())
        elif anim_type == AnimationType.SLIDE_RIGHT:
            prop_name, end_value = b"pos", QPoint(w, current_pos.y())
        elif anim_type == AnimationType.SLIDE_UP:
            prop_name, end_value = b"pos", QPoint(current_pos.x(), -h)
        elif anim_type == AnimationType.SLIDE_DOWN:
            prop_name, end_value = b"pos", QPoint(current_pos.x(), h)
        elif anim_type == AnimationType.ZOOM:
            prop_name, end_value = b"geometry", QRect(w // 2, h // 2, 0, 0)

        if prop_name:
            start_value = widget.geometry() if prop_name == b"geometry" else current_pos
            geom_anim = QPropertyAnimation(widget, prop_name)
            geom_anim.setDuration(duration)
            geom_anim.setEasingCurve(curve)
            geom_anim.setStartValue(start_value)
            geom_anim.setEndValue(end_value)
        return geom_anim

    def _create_incoming_geometry_animation(self, widget, anim_type, duration, curve):
        geom_anim = None
        parent_stack = widget.parentWidget()
        if not isinstance(parent_stack, QStackedWidget):
            return None
        w = parent_stack.width()
        h = parent_stack.height()
        final_pos = QPoint(0, 0)
        final_geom = parent_stack.rect()
        start_value = None
        end_value = None
        prop_name = None
        if anim_type == AnimationType.SLIDE_LEFT:
            start_value, end_value, prop_name = (
                QPoint(w, final_pos.y()),
                final_pos,
                b"pos",
            )
        elif anim_type == AnimationType.SLIDE_RIGHT:
            start_value, end_value, prop_name = (
                QPoint(-w, final_pos.y()),
                final_pos,
                b"pos",
            )
        elif anim_type == AnimationType.SLIDE_UP:
            start_value, end_value, prop_name = (
                QPoint(final_pos.x(), h),
                final_pos,
                b"pos",
            )
        elif anim_type == AnimationType.SLIDE_DOWN:
            start_value, end_value, prop_name = (
                QPoint(final_pos.x(), -h),
                final_pos,
                b"pos",
            )
        elif anim_type == AnimationType.ZOOM:
            start_value, end_value, prop_name = (
                QRect(w // 2, h // 2, 0, 0),
                final_geom,
                b"geometry",
            )

        if prop_name:
            if prop_name == b"geometry":
                widget.setGeometry(start_value)
            else:
                widget.move(start_value)
            geom_anim = QPropertyAnimation(widget, prop_name)
            geom_anim.setDuration(duration)
            geom_anim.setEasingCurve(curve)
            geom_anim.setStartValue(start_value)
            geom_anim.setEndValue(end_value)
        return geom_anim

    @Slot(weakref.ref)
    def _on_animation_out_finished(self, stack_widget_ref: weakref.ref):
        stack_widget = stack_widget_ref()
        if not stack_widget:
            return

        state = self._animation_state.get(stack_widget)
        if not state:
            return

        old_widget = state["old_widget_ref"]() if state["old_widget_ref"] else None
        new_widget = state["new_widget_ref"]()
        new_index = state["new_index"]

        if old_widget:
            try:
                old_widget.setGraphicsEffect(None)
                old_widget.hide()
            except RuntimeError:
                pass

        if new_widget:
            try:
                stack_widget.setCurrentIndex(new_index)
                self._start_incoming_animation(stack_widget, new_widget, state)
            except RuntimeError:
                self._clear_animation_state(stack_widget)
        else:
            self._clear_animation_state(
                stack_widget
            )  # Kunci dilepas jika widget baru tidak ada

    def _start_incoming_animation(self, stack_widget, new_widget, data):
        try:
            effect = new_widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(new_widget)
                new_widget.setGraphicsEffect(effect)
            effect.setOpacity(0.0)
            new_widget.show()
        except RuntimeError:
            self._clear_animation_state(stack_widget)
            return

        in_group = QParallelAnimationGroup(self)
        fade_in = QPropertyAnimation(effect, b"opacity")
        fade_in.setDuration(data["duration_in"])
        fade_in.setEasingCurve(data["curve_in"])
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        in_group.addAnimation(fade_in)

        geom_anim = self._create_incoming_geometry_animation(
            new_widget, data["animation_type"], data["duration_in"], data["curve_in"]
        )
        if geom_anim:
            in_group.addAnimation(geom_anim)

        in_group.finished.connect(
            lambda sw_ref=weakref.ref(stack_widget): self._on_animation_in_finished(
                sw_ref
            )
        )

        state = self._animation_state.get(stack_widget)
        if not state:
            return  # Animasi diinterupsi
        state["in_group"] = in_group
        in_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    @Slot(weakref.ref)
    def _on_animation_in_finished(self, stack_widget_ref: weakref.ref):
        stack_widget = stack_widget_ref()
        if not stack_widget or not self._is_animating(stack_widget):
            return

        current_widget = stack_widget.currentWidget()
        if current_widget:
            try:
                # Atur ulang properti dengan aman
                if current_widget.graphicsEffect():
                    QTimer.singleShot(
                        0, lambda w=current_widget: self._safe_remove_effect(w)
                    )
                if current_widget.pos() != QPoint(0, 0):
                    current_widget.move(0, 0)  # Pastikan posisi akhir benar
            except RuntimeError:
                pass  # Widget mungkin sudah dihapus

        self._clear_animation_state(stack_widget)

    def _interrupt_transition(self, stack_widget):
        state = self._animation_state.get(stack_widget)
        if not state:
            return

        # Hentikan semua animasi yang berjalan
        for group_name in ["out_group", "in_group"]:
            if group := state.get(group_name):
                try:
                    group.stop()
                except RuntimeError:
                    pass

        # Atur ulang state widget lama dan baru dengan aman
        old_widget = state["old_widget_ref"]() if state["old_widget_ref"] else None
        if old_widget:
            QTimer.singleShot(0, lambda w=old_widget: self._reset_widget_state(w))

        new_widget = state["new_widget_ref"]()
        if new_widget:
            QTimer.singleShot(
                0, lambda w=new_widget: self._reset_widget_state(w, visible=True)
            )
            try:
                # Pastikan widget baru berada di atas setelah interupsi
                stack_widget.setCurrentIndex(state["new_index"])
            except RuntimeError:
                pass

        self._clear_animation_state(stack_widget)

    def show_widget(
        self,
        widget,
        animation_type=AnimationType.FADE,
        duration=250,
        curve=QEasingCurve.Type.OutQuad,
        offset=30,
    ):
        if not widget:
            return
        self._setup_opacity_effect(widget, 0.0)
        widget.show()
        widget.raise_()
        QApplication.processEvents()

        end_pos = widget.pos()
        start_pos = self._calculate_offset_pos(end_pos, animation_type, offset)

        anim_group = QParallelAnimationGroup(self)
        opacity_anim = QPropertyAnimation(widget.graphicsEffect(), b"opacity")
        opacity_anim.setDuration(duration)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(curve)
        anim_group.addAnimation(opacity_anim)

        if animation_type != AnimationType.FADE:
            widget.move(start_pos)
            pos_anim = QPropertyAnimation(widget, b"pos")
            pos_anim.setDuration(duration)
            pos_anim.setStartValue(start_pos)
            pos_anim.setEndValue(end_pos)
            pos_anim.setEasingCurve(curve)
            anim_group.addAnimation(pos_anim)

        anim_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _setup_opacity_effect(self, widget, initial_opacity):
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
        effect.setOpacity(initial_opacity)

    def _calculate_offset_pos(self, base_pos, anim_type, offset):
        x, y = base_pos.x(), base_pos.y()
        if anim_type == AnimationType.SLIDE_UP:
            return QPoint(x, y + offset)
        if anim_type == AnimationType.SLIDE_DOWN:
            return QPoint(x, y - offset)
        if anim_type == AnimationType.SLIDE_LEFT:
            return QPoint(x + offset, y)
        if anim_type == AnimationType.SLIDE_RIGHT:
            return QPoint(x - offset, y)
        return base_pos

    def _safe_remove_effect(self, widget: QWidget):
        """Safely remove graphics effect on the next event loop cycle."""
        if not widget:
            return
        try:
            widget.setGraphicsEffect(None)  # type: ignore
        except (RuntimeError, AttributeError):
            pass


class WidgetLifecycleAnimator(QObject):
    """
    Animator khusus untuk siklus hidup widget (Delete/Remove).
    Memisahkan logika 'penghancuran' dari logika navigasi StackedWidget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_animations = []  # Menyimpan referensi agar tidak di-GC

    def animate_delete(
        self,
        widget: QWidget,
        duration: int = 400,
        use_drop_effect: bool = True,
        drop_distance: int = 50,
        on_finished_callback=None,
    ):
        if not widget:
            return

        # 1. Setup Opacity
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
        effect.setOpacity(1.0)

        # 2. Setup Geometry Sequence
        # Kunci tinggi widget agar saat animasi drop, layout tidak langsung snap
        current_h = widget.height()
        widget.setMinimumHeight(current_h)
        widget.setMaximumHeight(current_h)

        # Durasi dibagi: Fase Visual (Jatuh & Fade) -> Fase Struktural (Collapse)
        dur_visual = int(duration * 0.7)
        dur_collapse = int(duration * 0.3)

        # --- FASE 1: VISUAL (Parallel) ---
        visual_group = QParallelAnimationGroup()

        # A. Fade Out
        anim_fade = QPropertyAnimation(effect, b"opacity")
        anim_fade.setDuration(dur_visual)
        anim_fade.setStartValue(1.0)
        anim_fade.setEndValue(0.0)
        anim_fade.setEasingCurve(QEasingCurve.Type.InQuad)  # Fade makin cepat di akhir
        visual_group.addAnimation(anim_fade)

        # B. Drop Down (Efek Jatuh)
        if use_drop_effect:
            start_pos = widget.pos()
            end_pos = QPoint(start_pos.x(), start_pos.y() + drop_distance)

            anim_pos = QPropertyAnimation(widget, b"pos")
            anim_pos.setDuration(dur_visual)
            anim_pos.setStartValue(start_pos)
            anim_pos.setEndValue(end_pos)

            # QEasingCurve.InBack memberikan efek "ancang-ancang" ke atas sedikit
            # sebelum jatuh ke bawah, memberikan kesan berat/gravitasi.
            anim_pos.setEasingCurve(QEasingCurve.Type.InBack)
            visual_group.addAnimation(anim_pos)

        # --- FASE 2: STRUKTURAL (Collapse) ---
        # Menyusutkan tinggi ke 0 agar layout menutup
        collapse_group = QParallelAnimationGroup()

        anim_min = QPropertyAnimation(widget, b"minimumHeight")
        anim_min.setDuration(dur_collapse)
        anim_min.setStartValue(current_h)
        anim_min.setEndValue(0)
        anim_min.setEasingCurve(QEasingCurve.Type.OutQuad)

        anim_max = QPropertyAnimation(widget, b"maximumHeight")
        anim_max.setDuration(dur_collapse)
        anim_max.setStartValue(current_h)
        anim_max.setEndValue(0)
        anim_max.setEasingCurve(QEasingCurve.Type.OutQuad)

        collapse_group.addAnimation(anim_min)
        collapse_group.addAnimation(anim_max)

        # --- GABUNGKAN DALAM URUTAN ---
        sequence = QSequentialAnimationGroup(self)
        sequence.addAnimation(visual_group)
        sequence.addAnimation(collapse_group)

        # --- CLEANUP ---
        def on_done():
            if on_finished_callback:
                on_finished_callback()
            if widget:
                widget.deleteLater()
            # Hapus referensi animasi dari list internal
            if sequence in self._active_animations:
                self._active_animations.remove(sequence)

        sequence.finished.connect(on_done)

        # Simpan referensi dan jalankan
        self._active_animations.append(sequence)


class WidthAnimator(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_anims = weakref.WeakKeyDictionary()

    def animate_width(
        self, target, end_width, duration=250, curve=QEasingCurve.Type.InOutQuad
    ):
        if not target:
            return
        if target.width() == end_width:
            target.setFixedWidth(end_width)
            return

        group = QParallelAnimationGroup(self)
        for prop in [b"minimumWidth", b"maximumWidth"]:
            anim = QPropertyAnimation(target, prop, group)
            anim.setDuration(duration)
            anim.setEasingCurve(curve)
            anim.setStartValue(target.width())
            anim.setEndValue(end_width)
            group.addAnimation(anim)

        group.finished.connect(lambda: target.setFixedWidth(end_width))
        group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


class HeightAnimator(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    def animate_height(
        self, target, end_height, duration=250, curve=QEasingCurve.Type.InOutQuad
    ):
        if not target:
            return

        # Prepare for expansion if currently hidden or height 0
        if end_height > 0 and (not target.isVisible() or target.height() <= 1):
            target.show()
            target.setMinimumHeight(0)
            target.setMaximumHeight(0)

        start_height = target.height()
        if start_height == end_height:
            self._set_flex_height(target, end_height)
            return

        group = QParallelAnimationGroup(self)
        for prop in [b"minimumHeight", b"maximumHeight"]:
            anim = QPropertyAnimation(target, prop, group)
            anim.setDuration(duration)
            anim.setEasingCurve(curve)
            anim.setStartValue(start_height)
            anim.setEndValue(end_height)
            group.addAnimation(anim)

        group.finished.connect(lambda: self._set_flex_height(target, end_height))
        group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _set_flex_height(self, widget, height):
        if height > 0:
            widget.setMinimumHeight(height)
            widget.setMaximumHeight(16777215)
        else:
            widget.setFixedHeight(0)

    def _safe_remove_effect(self, widget: QWidget):
        """Safely remove graphics effect on the next event loop cycle."""
        if not widget:
            return
        try:
            # Using casting to any if possible or just ignoring lint
            # In PySide6, None is explicitly accepted to remove effect.
            widget.setGraphicsEffect(None)  # type: ignore
        except (RuntimeError, AttributeError):
            pass
