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

from pixel_refine_desktop.enhance_stack.core.logic.process_manager import (
    is_widget_alive,
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
    PLUS: Anti-QPainter Error dengan throttling dan safe grab.
    """

    DEFAULT_DURATION_OUT = 150
    DEFAULT_DURATION_IN = 250
    DEFAULT_CURVE_OUT = QEasingCurve.Type.OutQuad
    DEFAULT_CURVE_IN = QEasingCurve.Type.InQuad

    DEFAULT_CURVE_IN = QEasingCurve.Type.InQuad
    MAX_CONCURRENT_ANIMATIONS = 50

    def __init__(self, parent=None):
        super().__init__(parent)
        self._animation_state = weakref.WeakKeyDictionary()
        self._standalone_anims = weakref.WeakKeyDictionary()  # Tracking per-widget
        self._active_widgets = (
            weakref.WeakKeyDictionary()
        )  # Track widgets currently animating
        self._all_ghosts = []  # Strong refs for final cleanup
        self._animation_queue = []  # Queue untuk animasi yang ditunda
        self._concurrent_count = 0  # Counter animasi aktif

        self.destroyed.connect(self._on_animator_destroyed)

    def _on_animator_destroyed(self):
        """Final cleanup of all ghosts when animator is destroyed."""
        for ghost in self._all_ghosts:
            try:
                if is_widget_alive(ghost):
                    ghost.hide()
                    ghost.deleteLater()
            except:
                pass
        self._all_ghosts.clear()

    def stop_for_widget(self, widget: QWidget):
        """Public method to stop animations for a specific widget and delete its ghost."""
        if not widget or widget not in self._active_widgets:
            return

        old_data = self._active_widgets[widget]
        try:
            if isinstance(old_data, tuple):
                old_anim, old_ghost = old_data
                if old_anim and old_anim.state() == QPropertyAnimation.State.Running:
                    old_anim.stop()
                if is_widget_alive(old_ghost):
                    old_ghost.hide()
                    old_ghost.deleteLater()
                    if old_ghost in self._all_ghosts:
                        self._all_ghosts.remove(old_ghost)
        except:
            pass
        self._active_widgets.pop(widget, None)

    def _safe_grab(self, widget: QWidget, max_retries: int = 3):
        """
        Safely grab widget pixmap dengan retry mechanism.
        Returns (pixmap, geometry) tuple atau (None, None) jika gagal.
        """
        for attempt in range(max_retries):
            try:
                # Pastikan widget visible dan punya ukuran
                if (
                    not widget.isVisible()
                    or widget.width() <= 0
                    or widget.height() <= 0
                ):
                    return None, None

                # Tunggu sebentar jika bukan attempt pertama
                if attempt > 0:
                    QTimer.singleShot(attempt * 5, lambda: None)
                    QApplication.processEvents()

                pixmap = widget.grab()
                geom = widget.geometry()

                if not pixmap.isNull():
                    return pixmap, geom

            except (RuntimeError, Exception) as e:
                if attempt == max_retries - 1:
                    # Last attempt failed
                    return None, None
                continue

        return None, None

    def _direct_fade_out(
        self,
        widget: QWidget,
        duration: int,
        curve: QEasingCurve.Type,
        on_finished_callback=None,
    ):
        """
        Fallback animasi fade-out TANPA grab (direct opacity).
        Digunakan ketika grab() gagal atau untuk mencegah QPainter error.
        """
        if not is_widget_alive(widget):
            if on_finished_callback:
                QTimer.singleShot(0, on_finished_callback)
            return

        try:
            # Setup opacity effect
            effect = widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)
            effect.setOpacity(1.0)

            # Animasi langsung pada widget asli
            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(duration)
            anim.setStartValue(1.0)
            anim.setEndValue(0.0)
            anim.setEasingCurve(curve)

            def on_anim_finished():
                try:
                    if is_widget_alive(widget):
                        widget.hide()
                except RuntimeError:
                    pass

                if on_finished_callback and callable(on_finished_callback):
                    try:
                        if hasattr(on_finished_callback, "__self__"):
                            cb_obj = on_finished_callback.__self__
                            if isinstance(cb_obj, QWidget) and not is_widget_alive(
                                cb_obj
                            ):
                                return
                        on_finished_callback()
                    except RuntimeError:
                        pass

                # Decrement counter
                self._concurrent_count = max(0, self._concurrent_count - 1)
                self._process_animation_queue()

            anim.finished.connect(on_anim_finished)
            anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

        except (RuntimeError, Exception):
            # Jika semua gagal, langsung hide
            try:
                widget.hide()
            except:
                pass
            if on_finished_callback:
                QTimer.singleShot(0, on_finished_callback)

    def _can_start_animation(self) -> bool:
        """Check apakah masih bisa start animasi baru (throttle check)."""
        return self._concurrent_count < self.MAX_CONCURRENT_ANIMATIONS

    def _process_animation_queue(self):
        """Process queued animations jika ada slot tersedia."""
        while self._animation_queue and self._can_start_animation():
            queued_item = self._animation_queue.pop(0)
            # Unpack dan jalankan
            widget, duration, curve, callback = queued_item
            if is_widget_alive(widget):
                self._execute_transition_out(widget, duration, curve, callback)

    def transition_out(
        self,
        widget: QWidget,
        duration: int = 300,
        curve: QEasingCurve.Type = QEasingCurve.Type.OutQuad,
        on_finished_callback=None,
    ):
        """
        Animator fade-out mandiri yang aman dengan throttling dan queue.
        """
        if not widget:
            return

        # Check throttle - jika penuh, masukkan ke queue
        if not self._can_start_animation():
            self._animation_queue.append(
                (widget, duration, curve, on_finished_callback)
            )
            return

        # Eksekusi langsung
        self._execute_transition_out(widget, duration, curve, on_finished_callback)

    def _execute_transition_out(
        self,
        widget: QWidget,
        duration: int,
        curve: QEasingCurve.Type,
        on_finished_callback=None,
    ):
        """
        Internal executor untuk transition_out dengan safe grab dan fallback.
        """
        if not widget:
            return

        # Increment counter
        self._concurrent_count += 1

        # Batalkan animasi sebelumnya jika ada pada widget yang sama
        if widget in self._active_widgets:
            old_data = self._active_widgets[widget]
            try:
                if isinstance(old_data, tuple):
                    old_anim, old_ghost = old_data
                    if (
                        old_anim
                        and old_anim.state() == QPropertyAnimation.State.Running
                    ):
                        old_anim.stop()
                    if is_widget_alive(old_ghost):
                        old_ghost.hide()
                        old_ghost.deleteLater()
            except:
                pass
            del self._active_widgets[widget]

        widget_ref = weakref.ref(widget)

        if not widget_ref or not widget_ref():
            if on_finished_callback and callable(on_finished_callback):
                QTimer.singleShot(0, on_finished_callback)
            self._concurrent_count = max(0, self._concurrent_count - 1)
            self._process_animation_queue()
            return

        target_widget = widget_ref()
        if target_widget is None:
            if on_finished_callback and callable(on_finished_callback):
                on_finished_callback()
            self._concurrent_count = max(0, self._concurrent_count - 1)
            self._process_animation_queue()
            return

        parent = target_widget.parentWidget()
        if not parent:
            if on_finished_callback and callable(on_finished_callback):
                on_finished_callback()
            self._concurrent_count = max(0, self._concurrent_count - 1)
            self._process_animation_queue()
            return

        # --- STRATEGI SAFE GRAB dengan FALLBACK ---
        # Coba grab dengan retry, jika gagal gunakan direct fade
        pixmap, geom = self._safe_grab(target_widget)

        if pixmap is None or geom is None:
            # FALLBACK: Gunakan direct fade tanpa ghost
            self._direct_fade_out(target_widget, duration, curve, on_finished_callback)
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
        self._all_ghosts.append(ghost)

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
            # Cleanup entry from tracking
            if target_widget in self._active_widgets:
                del self._active_widgets[target_widget]

            try:
                if is_widget_alive(ghost):
                    if ghost in self._all_ghosts:
                        self._all_ghosts.remove(ghost)
                    ghost.deleteLater()
            except RuntimeError:
                pass

            # Check if callback is still valid to run
            if on_finished_callback and callable(on_finished_callback):
                try:
                    # If the callback is a method of a widget, check if widget is alive
                    if hasattr(on_finished_callback, "__self__"):
                        cb_obj = on_finished_callback.__self__
                        if isinstance(cb_obj, QWidget) and not is_widget_alive(cb_obj):
                            return
                    on_finished_callback()
                except RuntimeError:
                    pass

            # Decrement counter dan process queue
            self._concurrent_count = max(0, self._concurrent_count - 1)
            self._process_animation_queue()

        anim.finished.connect(on_anim_finished)
        self._active_widgets[target_widget] = (anim, ghost)
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

    def stop_all(self):
        """Hentikan semua animasi transisi di semua stacked widget."""
        # 1. Hentikan transisi QStackedWidget (in-progress)
        for stack_widget in list(self._animation_state.keys()):
            self._interrupt_transition(stack_widget)

        # 2. Hentikan semua animasi Ghost (out-progress)
        for widget in list(self._active_widgets.keys()):
            self.stop_for_widget(widget)

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
        self._ghosts = []  # Keep ghosts alive

    def _safe_grab(self, widget: QWidget, max_retries: int = 3):
        """Safely grab widget pixmap."""
        for attempt in range(max_retries):
            try:
                if (
                    not widget.isVisible()
                    or widget.width() <= 0
                    or widget.height() <= 0
                ):
                    return None, None
                if attempt > 0:
                    QApplication.processEvents()

                # Check for existing painters
                # Note: We can't easily check internal painter state, but try/except handles it.

                pixmap = widget.grab()
                geom = widget.geometry()

                if not pixmap.isNull():
                    return pixmap, geom
            except:
                continue
        return None, None

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

        # STRATEGI BARU: GHOST / SNAPSHOT MODE
        # Alih-alih menganimasikan widget asli (yang kompleks dan mungkin sedang repainting),
        # kita ambil screenshot (grab), buat label palsu (Ghost), sembunyikan widget asli,
        # lalu animasikan Ghost tersebut. Ini MENGHILANGKAN QPainter error.

        parent = widget.parentWidget()
        pixmap, geom = self._safe_grab(widget)

        if not pixmap or not geom or not parent:
            # Fallback jika gagal grab: Hide langsung
            widget.hide()
            widget.deleteLater()
            if on_finished_callback:
                on_finished_callback()
            return

        # 1. HIDE Widget Asli SEGERA (Stop QPainter Errors)
        widget.hide()
        # Kita trigger deleteLater nanti setelah animasi ghost selesai,
        # atau sekarang? Jika sekarang, mungkin aman, tapi callback butuh ref?
        # Lebih aman delete di akhir.

        # 2. Buat Ghost
        ghost = QLabel(parent)
        ghost.setPixmap(pixmap)
        ghost.setGeometry(geom)
        # FIX: Pastikan Ghost Label transparan agar tidak ada border/background putih di balik pixmap
        ghost.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        ghost.setStyleSheet("background: transparent;")
        ghost.show()
        ghost.raise_()
        self._ghosts.append(ghost)

        # 3. Setup Animasi pada Ghost
        # Setup Effect pada Ghost (bukan widget asli)
        effect = QGraphicsOpacityEffect(ghost)
        ghost.setGraphicsEffect(effect)
        effect.setOpacity(1.0)

        group = QParallelAnimationGroup()

        # A. Fade Out
        anim_fade = QPropertyAnimation(effect, b"opacity")
        anim_fade.setDuration(duration)
        anim_fade.setStartValue(1.0)
        anim_fade.setEndValue(0.0)
        anim_fade.setEasingCurve(QEasingCurve.Type.InQuad)
        group.addAnimation(anim_fade)

        # B. Drop Down
        if use_drop_effect:
            target_geo = QRect(
                geom.x(), geom.y() + drop_distance, geom.width(), geom.height()
            )
            anim_geo = QPropertyAnimation(ghost, b"geometry")
            anim_geo.setDuration(duration)
            anim_geo.setStartValue(geom)
            anim_geo.setEndValue(target_geo)
            anim_geo.setEasingCurve(QEasingCurve.Type.InBack)
            group.addAnimation(anim_geo)

        # C. Cleanup
        def cleanup():
            if ghost in self._ghosts:
                self._ghosts.remove(ghost)
            try:
                ghost.deleteLater()
                widget.deleteLater()  # Delete widget asli di sini
            except RuntimeError:
                pass

            if on_finished_callback:
                on_finished_callback()

            # Remove anim ref
            if group in self._active_animations:
                self._active_animations.remove(group)

        group.finished.connect(cleanup)
        self._active_animations.append(group)
        group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def stop_all(self):
        """Hentikan paksa semua animasi yang sedang berjalan."""
        for seq in list(self._active_animations):
            try:
                seq.stop()
            except RuntimeError:
                pass
        self._active_animations.clear()


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
