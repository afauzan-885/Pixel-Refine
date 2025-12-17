import weakref
from PySide6.QtWidgets import QStackedWidget, QGraphicsOpacityEffect, QWidget
from PySide6.QtCore import (
    QObject,
    QPropertyAnimation,
    QEasingCurve,
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
        # --- Hanya SATU dictionary untuk melacak semua state transisi ---
        self._active_transitions = {}
        # Metode transition_out yang baru tidak perlu state tracking di sini.

    def transition_out(
        self,
        widget: QWidget,
        duration: int = 300,
        curve: QEasingCurve.Type = QEasingCurve.Type.OutQuad,
        on_finished_callback=None,
    ):
        """
        Animator fade-out mandiri yang aman.
        Jika widget tidak valid, callback akan tetap dipanggil dengan aman.
        """
        widget_ref = weakref.ref(widget) if widget else None

        # Self-Healing: Jika widget sudah tidak ada, panggil callback dan selesai.
        if not widget_ref or not widget_ref():
            if on_finished_callback:
                QTimer.singleShot(0, on_finished_callback)
            return

        # Siapkan efek opacity. Jika widget dihapus saat ini, tangkap errornya.
        try:
            opacity_effect = widget.graphicsEffect()
            if not isinstance(opacity_effect, QGraphicsOpacityEffect):
                opacity_effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(opacity_effect)
            opacity_effect.setOpacity(1.0)
        except RuntimeError:
            if on_finished_callback:
                QTimer.singleShot(0, on_finished_callback)
            return

        anim = QPropertyAnimation(opacity_effect, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(curve)

        # Gunakan weakref untuk callback agar tidak menahan objek
        def on_anim_finished():
            w = widget_ref()
            if w:
                try:
                    # Cukup hapus efeknya, tidak perlu memeriksa apakah efeknya sama.
                    w.setGraphicsEffect(None)
                except RuntimeError:
                    pass  # Abaikan jika widget dihapus saat callback berjalan

            # Panggil callback eksternal jika ada
            if on_finished_callback:
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

        # --- Pengecekan Awal yang Ketat ---
        # Interupsi animasi yang sedang berjalan jika ada
        if stack_widget in self._active_transitions:
            self._interrupt_transition(stack_widget)

        # Pastikan tidak ada transisi aktif sebelum lanjut
        if stack_widget in self._active_transitions:
            return

        old_widget = stack_widget.currentWidget()
        new_widget, new_index = self._validate_target(stack_widget, target)

        # Hentikan jika tidak ada target baru atau jika target sama dengan yang lama
        if not new_widget or old_widget == new_widget:
            return

        # --- Simpan State Transisi ---
        self._active_transitions[stack_widget] = {
            "old_widget_ref": weakref.ref(old_widget) if old_widget else None,
            "new_widget_ref": weakref.ref(new_widget),
            "new_index": new_index,
            "animation_type": animation_type,
            "duration_in": duration_in,
            "curve_in": curve_in,
        }

        # --- FASE OUT ---
        if not old_widget:
            # Jika tidak ada widget lama, langsung ke fase IN
            self._on_animation_out_finished(weakref.ref(stack_widget))
            return

        # Self-Healing: Cek apakah widget lama masih valid SEBELUM membuat animasi
        try:
            effect = old_widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(old_widget)
                old_widget.setGraphicsEffect(effect)
            effect.setOpacity(1.0)
        except RuntimeError:
            # Jika old_widget sudah hilang, batalkan transisi dengan bersih
            del self._active_transitions[stack_widget]
            return

        # --- Pembuatan Animasi yang Aman ---
        out_group = QParallelAnimationGroup(self)

        # PERBAIKAN: Jangan berikan parent pada animasi individual.
        # Biarkan QParallelAnimationGroup yang menjadi parent-nya.
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

        # Hubungkan sinyal menggunakan weakref
        out_group.finished.connect(
            lambda sw_ref=weakref.ref(stack_widget): self._on_animation_out_finished(
                sw_ref
            )
        )

        # --- PENGECEKAN FINAL SEBELUM START ---
        # Self-Healing: Cek sekali lagi apakah old_widget masih ada tepat sebelum 'start'.
        # Ini adalah pertahanan terakhir melawan race condition ekstrem.
        if (
            not (data := self._active_transitions.get(stack_widget))
            or not data["old_widget_ref"]()
        ):
            # Widget lama sudah hilang, jangan mulai animasi yatim piatu.
            del self._active_transitions[stack_widget]
            return

        self._active_transitions[stack_widget]["out_group"] = out_group
        out_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    # =====================================================
    # === Metode Internal (Helper dan Slot) ===
    # =====================================================

    @Slot(weakref.ref, weakref.ref)
    def _on_standalone_fade_out_finished(self, widget_ref, effect_ref):
        """Slot internal: Membersihkan setelah animasi fade-out mandiri selesai."""
        widget = widget_ref() if widget_ref else None
        effect = effect_ref() if effect_ref else None

        if widget:
            if effect and widget.graphicsEffect() == effect:
                widget.setGraphicsEffect(None)
            if widget in self._active_fade_outs:
                del self._active_fade_outs[widget]
        else:
            pass

    def _validate_target(self, stack_widget, target):
        """Validasi target dan kembalikan widget serta indeksnya."""
        target_widget = None
        target_index = -1
        if isinstance(target, QWidget):
            target_widget = target
            target_index = stack_widget.indexOf(target_widget)
            if target_index == -1:
                print(
                    f"Animator Error: Target widget {target_widget} not in stack {stack_widget.objectName()}."
                )
        elif isinstance(target, int):
            target_index = target
            target_widget = stack_widget.widget(target_index)
            if not target_widget:
                print(
                    f"Animator Error: No widget at index {target_index} in stack {stack_widget.objectName()}."
                )
        else:
            print(f"Animator Error: Invalid target type: {type(target)}")
        return target_widget, target_index

    def _create_outgoing_geometry_animation(self, widget, anim_type, duration, curve):
        """Membuat animasi geometri/posisi untuk widget yang keluar."""
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
            # Jangan set parent di sini
            geom_anim = QPropertyAnimation(widget, prop_name)
            geom_anim.setDuration(duration)
            geom_anim.setEasingCurve(curve)
            geom_anim.setStartValue(start_value)
            geom_anim.setEndValue(end_value)
        return geom_anim

    # <<< PERBAIKAN KUNCI: Hapus `parent_group` dari definisi fungsi >>>
    def _create_incoming_geometry_animation(self, widget, anim_type, duration, curve):
        """Membuat animasi geometri/posisi untuk widget yang masuk."""
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
            # Jangan set parent di sini
            geom_anim = QPropertyAnimation(widget, prop_name)
            geom_anim.setDuration(duration)
            geom_anim.setEasingCurve(curve)
            geom_anim.setStartValue(start_value)
            geom_anim.setEndValue(end_value)
        return geom_anim

    @Slot(weakref.ref)
    def _on_animation_out_finished(self, stack_widget_ref: weakref.ref):
        stack_widget = stack_widget_ref()
        if not stack_widget or not (data := self._active_transitions.get(stack_widget)):
            return

        old_widget = data["old_widget_ref"]() if data["old_widget_ref"] else None
        new_widget = data["new_widget_ref"]()
        new_index = data["new_index"]

        if old_widget:
            try:
                old_widget.setGraphicsEffect(None)
                old_widget.hide()
            except RuntimeError:
                pass

        if new_widget:
            try:
                stack_widget.setCurrentIndex(new_index)
                self._start_incoming_animation(stack_widget, new_widget, data)
            except RuntimeError:
                del self._active_transitions[stack_widget]
        else:
            del self._active_transitions[stack_widget]

    def _start_incoming_animation(
        self, stack_widget: QStackedWidget, new_widget: QWidget, data: dict
    ):
        try:
            effect = new_widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(new_widget)
                new_widget.setGraphicsEffect(effect)
            effect.setOpacity(0.0)
            new_widget.show()
        except RuntimeError:
            del self._active_transitions[stack_widget]
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

        if (
            not (active_data := self._active_transitions.get(stack_widget))
            or not active_data["new_widget_ref"]()
        ):
            del self._active_transitions[stack_widget]
            return

        self._active_transitions[stack_widget]["in_group"] = in_group
        in_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    @Slot(weakref.ref)
    def _on_animation_in_finished(self, stack_widget_ref: weakref.ref):
        stack_widget = stack_widget_ref()
        if not stack_widget:
            return

        current_widget = stack_widget.currentWidget()
        if current_widget:
            try:
                current_widget.setGraphicsEffect(None)
                if current_widget.pos() != QPoint(0, 0):
                    current_widget.move(0, 0)
            except RuntimeError:
                pass

        self._active_transitions.pop(stack_widget, None)

    @Slot(weakref.ref)
    def _on_animation_in_finished(self, stack_widget_ref: weakref.ref):
        stack_widget = stack_widget_ref()
        if not stack_widget:
            return

        current_widget = stack_widget.currentWidget()
        if current_widget:
            try:
                current_widget.setGraphicsEffect(None)
                if current_widget.pos() != QPoint(0, 0):
                    current_widget.move(0, 0)
            except RuntimeError:
                pass

        self._active_transitions.pop(stack_widget, None)

    def _interrupt_transition(self, stack_widget):
        """Force stop any active transition on the stack widget and cleanup."""
        if stack_widget not in self._active_transitions:
            return

        data = self._active_transitions[stack_widget]

        # Stop outgoing group
        if "out_group" in data and data["out_group"]:
            try:
                if data["out_group"].state() == QParallelAnimationGroup.State.Running:
                    data["out_group"].stop()
            except RuntimeError:
                pass  # Animation group already deleted

        # Stop incoming group
        if "in_group" in data and data["in_group"]:
            try:
                if data["in_group"].state() == QParallelAnimationGroup.State.Running:
                    data["in_group"].stop()
            except RuntimeError:
                pass  # Animation group already deleted

        # Cleanup active widgets manually since animations are stopped
        old_widget = data["old_widget_ref"]() if data["old_widget_ref"] else None
        new_widget = data["new_widget_ref"]()

        if old_widget:
            try:
                old_widget.setGraphicsEffect(None)
                old_widget.hide()
            except RuntimeError:
                pass

        if new_widget:
            try:
                new_widget.setGraphicsEffect(None)
                if new_widget.pos() != QPoint(0, 0):
                    new_widget.move(0, 0)
                new_widget.show()
                # Ensure opacity is 1
                opacity = new_widget.graphicsEffect()
                if isinstance(opacity, QGraphicsOpacityEffect):
                    opacity.setOpacity(1.0)
            except RuntimeError:
                pass

        # Ensure stack is at new index
        try:
            stack_widget.setCurrentIndex(data["new_index"])
        except RuntimeError:
            pass

        del self._active_transitions[stack_widget]

    # Metode validasi
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


import weakref
from PySide6.QtWidgets import QStackedWidget, QGraphicsOpacityEffect, QWidget
from PySide6.QtCore import (
    QObject,
    QPropertyAnimation,
    QEasingCurve,
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
        # --- Hanya SATU dictionary untuk melacak semua state transisi ---
        self._active_transitions = {}
        # Metode transition_out yang baru tidak perlu state tracking di sini.

    def transition_out(
        self,
        widget: QWidget,
        duration: int = 300,
        curve: QEasingCurve.Type = QEasingCurve.Type.OutQuad,
        on_finished_callback=None,
    ):
        """
        Animator fade-out mandiri yang aman.
        Jika widget tidak valid, callback akan tetap dipanggil dengan aman.
        """
        widget_ref = weakref.ref(widget) if widget else None

        # Self-Healing: Jika widget sudah tidak ada, panggil callback dan selesai.
        if not widget_ref or not widget_ref():
            if on_finished_callback:
                QTimer.singleShot(0, on_finished_callback)
            return

        # Siapkan efek opacity. Jika widget dihapus saat ini, tangkap errornya.
        try:
            opacity_effect = widget.graphicsEffect()
            if not isinstance(opacity_effect, QGraphicsOpacityEffect):
                opacity_effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(opacity_effect)
            opacity_effect.setOpacity(1.0)
        except RuntimeError:
            if on_finished_callback:
                QTimer.singleShot(0, on_finished_callback)
            return

        anim = QPropertyAnimation(opacity_effect, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(curve)

        # Gunakan weakref untuk callback agar tidak menahan objek
        def on_anim_finished():
            w = widget_ref()
            if w:
                try:
                    # Cukup hapus efeknya, tidak perlu memeriksa apakah efeknya sama.
                    w.setGraphicsEffect(None)
                except RuntimeError:
                    pass  # Abaikan jika widget dihapus saat callback berjalan

            # Panggil callback eksternal jika ada
            if on_finished_callback:
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

        # --- Pengecekan Awal yang Ketat ---
        # Interupsi animasi yang sedang berjalan jika ada
        if stack_widget in self._active_transitions:
            self._interrupt_transition(stack_widget)

        # Pastikan tidak ada transisi aktif sebelum lanjut
        if stack_widget in self._active_transitions:
            return

        old_widget = stack_widget.currentWidget()
        new_widget, new_index = self._validate_target(stack_widget, target)

        # Hentikan jika tidak ada target baru atau jika target sama dengan yang lama
        if not new_widget or old_widget == new_widget:
            return

        # --- Simpan State Transisi ---
        self._active_transitions[stack_widget] = {
            "old_widget_ref": weakref.ref(old_widget) if old_widget else None,
            "new_widget_ref": weakref.ref(new_widget),
            "new_index": new_index,
            "animation_type": animation_type,
            "duration_in": duration_in,
            "curve_in": curve_in,
        }

        # --- FASE OUT ---
        if not old_widget:
            # Jika tidak ada widget lama, langsung ke fase IN
            self._on_animation_out_finished(weakref.ref(stack_widget))
            return

        # Self-Healing: Cek apakah widget lama masih valid SEBELUM membuat animasi
        try:
            effect = old_widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(old_widget)
                old_widget.setGraphicsEffect(effect)
            effect.setOpacity(1.0)
        except RuntimeError:
            # Jika old_widget sudah hilang, batalkan transisi dengan bersih
            del self._active_transitions[stack_widget]
            return

        # --- Pembuatan Animasi yang Aman ---
        out_group = QParallelAnimationGroup(self)

        # PERBAIKAN: Jangan berikan parent pada animasi individual.
        # Biarkan QParallelAnimationGroup yang menjadi parent-nya.
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

        # Hubungkan sinyal menggunakan weakref
        out_group.finished.connect(
            lambda sw_ref=weakref.ref(stack_widget): self._on_animation_out_finished(
                sw_ref
            )
        )

        # --- PENGECEKAN FINAL SEBELUM START ---
        # Self-Healing: Cek sekali lagi apakah old_widget masih ada tepat sebelum 'start'.
        # Ini adalah pertahanan terakhir melawan race condition ekstrem.
        if (
            not (data := self._active_transitions.get(stack_widget))
            or not data["old_widget_ref"]()
        ):
            # Widget lama sudah hilang, jangan mulai animasi yatim piatu.
            del self._active_transitions[stack_widget]
            return

        self._active_transitions[stack_widget]["out_group"] = out_group
        out_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    # =====================================================
    # === Metode Internal (Helper dan Slot) ===
    # =====================================================

    @Slot(weakref.ref, weakref.ref)
    def _on_standalone_fade_out_finished(self, widget_ref, effect_ref):
        """Slot internal: Membersihkan setelah animasi fade-out mandiri selesai."""
        widget = widget_ref() if widget_ref else None
        effect = effect_ref() if effect_ref else None

        if widget:
            if effect and widget.graphicsEffect() == effect:
                widget.setGraphicsEffect(None)
            if widget in self._active_fade_outs:
                del self._active_fade_outs[widget]
        else:
            pass

    def _validate_target(self, stack_widget, target):
        """Validasi target dan kembalikan widget serta indeksnya."""
        target_widget = None
        target_index = -1
        if isinstance(target, QWidget):
            target_widget = target
            target_index = stack_widget.indexOf(target_widget)
            if target_index == -1:
                print(
                    f"Animator Error: Target widget {target_widget} not in stack {stack_widget.objectName()}."
                )
        elif isinstance(target, int):
            target_index = target
            target_widget = stack_widget.widget(target_index)
            if not target_widget:
                print(
                    f"Animator Error: No widget at index {target_index} in stack {stack_widget.objectName()}."
                )
        else:
            print(f"Animator Error: Invalid target type: {type(target)}")
        return target_widget, target_index

    def _create_outgoing_geometry_animation(self, widget, anim_type, duration, curve):
        """Membuat animasi geometri/posisi untuk widget yang keluar."""
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
            # Jangan set parent di sini
            geom_anim = QPropertyAnimation(widget, prop_name)
            geom_anim.setDuration(duration)
            geom_anim.setEasingCurve(curve)
            geom_anim.setStartValue(start_value)
            geom_anim.setEndValue(end_value)
        return geom_anim

    # <<< PERBAIKAN KUNCI: Hapus `parent_group` dari definisi fungsi >>>
    def _create_incoming_geometry_animation(self, widget, anim_type, duration, curve):
        """Membuat animasi geometri/posisi untuk widget yang masuk."""
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
            # Jangan set parent di sini
            geom_anim = QPropertyAnimation(widget, prop_name)
            geom_anim.setDuration(duration)
            geom_anim.setEasingCurve(curve)
            geom_anim.setStartValue(start_value)
            geom_anim.setEndValue(end_value)
        return geom_anim

    @Slot(weakref.ref)
    def _on_animation_out_finished(self, stack_widget_ref: weakref.ref):
        stack_widget = stack_widget_ref()
        if not stack_widget or not (data := self._active_transitions.get(stack_widget)):
            return

        old_widget = data["old_widget_ref"]() if data["old_widget_ref"] else None
        new_widget = data["new_widget_ref"]()
        new_index = data["new_index"]

        if old_widget:
            try:
                old_widget.setGraphicsEffect(None)
                old_widget.hide()
            except RuntimeError:
                pass

        if new_widget:
            try:
                stack_widget.setCurrentIndex(new_index)
                self._start_incoming_animation(stack_widget, new_widget, data)
            except RuntimeError:
                del self._active_transitions[stack_widget]
        else:
            del self._active_transitions[stack_widget]

    def _start_incoming_animation(
        self, stack_widget: QStackedWidget, new_widget: QWidget, data: dict
    ):
        try:
            effect = new_widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(new_widget)
                new_widget.setGraphicsEffect(effect)
            effect.setOpacity(0.0)
            new_widget.show()
        except RuntimeError:
            del self._active_transitions[stack_widget]
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

        if (
            not (active_data := self._active_transitions.get(stack_widget))
            or not active_data["new_widget_ref"]()
        ):
            del self._active_transitions[stack_widget]
            return

        self._active_transitions[stack_widget]["in_group"] = in_group
        in_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    @Slot(weakref.ref)
    def _on_animation_in_finished(self, stack_widget_ref: weakref.ref):
        stack_widget = stack_widget_ref()
        if not stack_widget:
            return

        current_widget = stack_widget.currentWidget()
        if current_widget:
            try:
                current_widget.setGraphicsEffect(None)
                if current_widget.pos() != QPoint(0, 0):
                    current_widget.move(0, 0)
            except RuntimeError:
                pass

        self._active_transitions.pop(stack_widget, None)

    @Slot(weakref.ref)
    def _on_animation_in_finished(self, stack_widget_ref: weakref.ref):
        stack_widget = stack_widget_ref()
        if not stack_widget:
            return

        current_widget = stack_widget.currentWidget()
        if current_widget:
            try:
                current_widget.setGraphicsEffect(None)
                if current_widget.pos() != QPoint(0, 0):
                    current_widget.move(0, 0)
            except RuntimeError:
                pass

        self._active_transitions.pop(stack_widget, None)

    def _interrupt_transition(self, stack_widget):
        """Force stop any active transition on the stack widget and cleanup."""
        if stack_widget not in self._active_transitions:
            return

        data = self._active_transitions[stack_widget]

        # Stop outgoing group
        if "out_group" in data and data["out_group"]:
            try:
                if data["out_group"].state() == QParallelAnimationGroup.State.Running:
                    data["out_group"].stop()
            except RuntimeError:
                pass  # Animation group already deleted

        # Stop incoming group
        if "in_group" in data and data["in_group"]:
            try:
                if data["in_group"].state() == QParallelAnimationGroup.State.Running:
                    data["in_group"].stop()
            except RuntimeError:
                pass  # Animation group already deleted

        # Cleanup active widgets manually since animations are stopped
        old_widget = data["old_widget_ref"]() if data["old_widget_ref"] else None
        new_widget = data["new_widget_ref"]()

        if old_widget:
            try:
                old_widget.setGraphicsEffect(None)
                old_widget.hide()
            except RuntimeError:
                pass

        if new_widget:
            try:
                new_widget.setGraphicsEffect(None)
                if new_widget.pos() != QPoint(0, 0):
                    new_widget.move(0, 0)
                new_widget.show()
                # Ensure opacity is 1
                opacity = new_widget.graphicsEffect()
                if isinstance(opacity, QGraphicsOpacityEffect):
                    opacity.setOpacity(1.0)
            except RuntimeError:
                pass

        # Ensure stack is at new index
        try:
            stack_widget.setCurrentIndex(data["new_index"])
        except RuntimeError:
            pass

        del self._active_transitions[stack_widget]

    # Metode validasi
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


class WidgetAnimator(QObject):
    """
    Animator universal untuk QWidget apa pun (kecuali QStackedWidget).
    Menangani animasi Show (Masuk) dan Hide (Keluar) dengan aman.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Menyimpan animasi aktif agar tidak di-garbage collect
        self._active_animations = weakref.WeakKeyDictionary()

    def show_widget(
        self,
        widget: QWidget,
        animation_type: AnimationType = AnimationType.FADE,
        duration: int = 250,
        curve: QEasingCurve.Type = QEasingCurve.Type.OutQuad,
        offset: int = 30,  # Jarak geser
    ):
        """
        Menampilkan widget dengan animasi.
        """
        if not widget:
            return

        # 1. Siapkan Opacity Effect (Mulai dari 0)
        self._setup_opacity_effect(widget, 0.0)

        # 2. Tampilkan widget agar geometri dan posisi terhitung oleh Qt/Layout
        widget.show()
        widget.raise_()
        QApplication.processEvents()  # Pastikan layout manager selesai menata posisi

        # 3. Hitung Posisi Akhir (Goal) dan Awal (Start)
        end_pos = widget.pos()
        end_geometry = widget.geometry()

        start_pos = self._calculate_offset_pos(end_pos, animation_type, offset)
        start_geometry = self._calculate_zoom_geometry(end_geometry, animation_type)

        # 4. Hentikan animasi sebelumnya jika ada
        self._stop_running_animation(widget)

        # 5. Setup Animasi
        anim_group = QParallelAnimationGroup(self)

        # A. Animasi Opacity (0 -> 1)
        opacity_anim = QPropertyAnimation(widget.graphicsEffect(), b"opacity")
        opacity_anim.setDuration(duration)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(curve)
        anim_group.addAnimation(opacity_anim)

        # B. Animasi Geometri/Posisi
        if animation_type == AnimationType.ZOOM:
            # Khusus Zoom: Mainkan Geometry
            widget.setGeometry(start_geometry)  # Set ke kecil dulu
            geom_anim = QPropertyAnimation(widget, b"geometry")
            geom_anim.setDuration(duration)
            geom_anim.setStartValue(start_geometry)
            geom_anim.setEndValue(end_geometry)
            geom_anim.setEasingCurve(curve)
            anim_group.addAnimation(geom_anim)

        elif animation_type != AnimationType.FADE:
            # Slide Animations: Mainkan Posisi
            widget.move(start_pos)  # Pindahkan ke posisi start (offset)
            pos_anim = QPropertyAnimation(widget, b"pos")
            pos_anim.setDuration(duration)
            pos_anim.setStartValue(start_pos)
            pos_anim.setEndValue(end_pos)
            pos_anim.setEasingCurve(curve)
            anim_group.addAnimation(pos_anim)

        # Cleanup saat selesai
        anim_group.finished.connect(lambda: self._on_show_finished(weakref.ref(widget)))

        self._active_animations[widget] = anim_group
        anim_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def hide_widget(
        self,
        widget: QWidget,
        animation_type: AnimationType = AnimationType.FADE,
        duration: int = 200,
        curve: QEasingCurve.Type = QEasingCurve.Type.InQuad,
        offset: int = 30,
    ):
        """
        Menyembunyikan widget dengan animasi, lalu memanggil hide().
        """
        if not widget or not widget.isVisible():
            return

        # Pastikan effect ada
        self._setup_opacity_effect(widget, 1.0)

        # Capture kondisi saat ini (Awal animasi keluar)
        start_pos = widget.pos()
        start_geometry = widget.geometry()

        # Hitung target (Akhir animasi keluar)
        # Note: Untuk keluar, offset logikanya sama (geser ke arah tertentu)
        end_pos = self._calculate_offset_pos(start_pos, animation_type, offset)
        end_geometry = self._calculate_zoom_geometry(start_geometry, animation_type)

        self._stop_running_animation(widget)

        anim_group = QParallelAnimationGroup(self)

        # A. Opacity (1 -> 0)
        opacity_anim = QPropertyAnimation(widget.graphicsEffect(), b"opacity")
        opacity_anim.setDuration(duration)
        opacity_anim.setStartValue(1.0)
        opacity_anim.setEndValue(0.0)
        opacity_anim.setEasingCurve(curve)
        anim_group.addAnimation(opacity_anim)

        # B. Geometri/Posisi
        if animation_type == AnimationType.ZOOM:
            geom_anim = QPropertyAnimation(widget, b"geometry")
            geom_anim.setDuration(duration)
            geom_anim.setStartValue(start_geometry)
            geom_anim.setEndValue(end_geometry)  # Mengecil
            geom_anim.setEasingCurve(curve)
            anim_group.addAnimation(geom_anim)

        elif animation_type != AnimationType.FADE:
            pos_anim = QPropertyAnimation(widget, b"pos")
            pos_anim.setDuration(duration)
            pos_anim.setStartValue(start_pos)
            pos_anim.setEndValue(end_pos)
            pos_anim.setEasingCurve(curve)
            anim_group.addAnimation(pos_anim)

        # Simpan posisi asli untuk dikembalikan setelah hide
        # Agar saat nanti di-show() lagi tanpa animasi, posisinya benar.
        original_pos = start_pos
        original_geom = (
            start_geometry  # Sebenarnya start_geometry untuk hide adalah full size
        )

        anim_group.finished.connect(
            lambda: self._on_hide_finished(
                weakref.ref(widget), original_pos, original_geom, animation_type
            )
        )

        self._active_animations[widget] = anim_group
        anim_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    # --- Helper Methods ---

    def _setup_opacity_effect(self, widget, initial_opacity):
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
        effect.setOpacity(initial_opacity)

    def _stop_running_animation(self, widget):
        if widget in self._active_animations:
            group = self._active_animations[widget]
            if group.state() == QParallelAnimationGroup.State.Running:
                group.stop()
            del self._active_animations[widget]

    def _calculate_offset_pos(self, base_pos: QPoint, anim_type, offset: int) -> QPoint:
        """Menghitung posisi offset berdasarkan arah animasi."""
        x, y = base_pos.x(), base_pos.y()

        if anim_type == AnimationType.SLIDE_UP:
            return QPoint(x, y + offset)  # Datang dari bawah / Pergi ke bawah
        elif anim_type == AnimationType.SLIDE_DOWN:
            return QPoint(x, y - offset)  # Datang dari atas / Pergi ke atas
        elif anim_type == AnimationType.SLIDE_LEFT:
            return QPoint(x + offset, y)  # Datang dari kanan / Pergi ke kanan
        elif anim_type == AnimationType.SLIDE_RIGHT:
            return QPoint(x - offset, y)  # Datang dari kiri / Pergi ke kiri

        return base_pos

    def _calculate_zoom_geometry(self, base_rect: QRect, anim_type) -> QRect:
        """Menghitung geometry mengecil (tengah) untuk efek Zoom."""
        if anim_type == AnimationType.ZOOM:
            # Hitung rect yang lebih kecil di tengah-tengah
            center = base_rect.center()
            # Mulai dari ukuran 0 atau sangat kecil
            new_w, new_h = 0, 0
            return QRect(center.x(), center.y(), new_w, new_h)
        return base_rect

    def _on_show_finished(self, widget_ref):
        """Cleanup setelah show selesai."""
        # Kita tidak perlu menghapus referensi animasi di sini secara manual
        # karena DeleteWhenStopped akan menanganinya, tapi referensi di dictionary akan tertimpa nanti.
        pass

    def _on_hide_finished(self, widget_ref, original_pos, original_geom, anim_type):
        """Cleanup setelah hide selesai: Hide widget dan Reset posisi."""
        widget = widget_ref()
        if not widget:
            return

        try:
            widget.hide()

            # Kembalikan properti agar siap dipakai lagi (Reset State)
            effect = widget.graphicsEffect()
            if isinstance(effect, QGraphicsOpacityEffect):
                effect.setOpacity(1.0)

            # Reset posisi/geometri ke posisi asli sebelum animasi dimulai
            # Ini PENTING agar layout manager tidak bingung atau posisi tidak 'drift'
            if anim_type == AnimationType.ZOOM:
                # Untuk Zoom, original_geom yang dikirim saat hide adalah ukuran Penuh (start_geometry)
                widget.setGeometry(original_geom)
            else:
                widget.move(original_pos)

        except RuntimeError:
            pass  # Widget mungkin sudah deleted


# ============================================
# === KELAS BARU: WidthAnimator ===
# ============================================
class WidthAnimator(QObject):
    """
    Mengelola animasi perubahan lebar (minimumWidth, maximumWidth) untuk sebuah QWidget.
    """

    # --- Nilai Default ---
    DEFAULT_DURATION = 250
    DEFAULT_CURVE = QEasingCurve.Type.InOutQuad

    def __init__(self, parent=None):
        """Inisialisasi WidthAnimator."""
        super().__init__(parent)
        self._active_width_animations = weakref.WeakKeyDictionary()

    def animate_width(
        self,
        target_widget: QWidget,
        end_width: int,
        duration: int = DEFAULT_DURATION,
        curve: QEasingCurve.Type = DEFAULT_CURVE,
    ):
        """
        Memulai animasi untuk mengubah lebar widget target.

        Args:
            target_widget: Widget yang lebarnya akan dianimasikan.
            end_width: Lebar target akhir.
            duration: Durasi animasi dalam milidetik.
            curve: Kurva easing yang akan digunakan.
        """
        if not target_widget:
            print("WidthAnimator Error: target_widget cannot be None.")
            return

        # Hentikan animasi sebelumnya untuk widget ini jika sedang berjalan
        if target_widget in self._active_width_animations:
            existing_anim = self._active_width_animations.get(target_widget)
            if (
                existing_anim
                and existing_anim.state() == QPropertyAnimation.State.Running
            ):
                existing_anim.stop()
            if target_widget in self._active_width_animations:
                del self._active_width_animations[target_widget]

        start_width = target_widget.width()

        # Jangan animasi jika sudah di lebar target
        if start_width == end_width:
            target_widget.setMinimumWidth(end_width)
            target_widget.setMaximumWidth(end_width)
            return

        # Buat grup animasi paralel
        animation_group = QParallelAnimationGroup(self)

        # Animasi properti minimumWidth
        min_anim = QPropertyAnimation(target_widget, b"minimumWidth", animation_group)
        min_anim.setDuration(duration)
        min_anim.setEasingCurve(curve)
        min_anim.setStartValue(start_width)
        min_anim.setEndValue(end_width)
        animation_group.addAnimation(min_anim)

        # Animasi properti maximumWidth
        max_anim = QPropertyAnimation(target_widget, b"maximumWidth", animation_group)
        max_anim.setDuration(duration)
        max_anim.setEasingCurve(curve)
        max_anim.setStartValue(start_width)
        max_anim.setEndValue(end_width)
        animation_group.addAnimation(max_anim)

        # Hubungkan sinyal finished dari GRUP ke slot cleanup internal
        animation_group.finished.connect(
            lambda w=target_widget: self._on_width_animation_finished(w)
        )

        # Simpan referensi animasi aktif dan mulai
        self._active_width_animations[target_widget] = animation_group
        animation_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    @Slot(QWidget)
    def _on_width_animation_finished(self, target_widget: QWidget):
        """Slot internal: Dipanggil setelah animasi lebar selesai."""
        if target_widget in self._active_width_animations:
            del self._active_width_animations[target_widget]

        final_width = target_widget.minimumWidth()
        target_widget.setFixedWidth(final_width)


QWIDGETSIZE_MAX = 16777215


class HeightAnimator(QObject):
    """
    Mengelola animasi perubahan tinggi yang fleksibel untuk sebuah QWidget.
    Setelah animasi selesai, widget dapat menyesuaikan ukurannya secara dinamis.
    """

    DEFAULT_DURATION = 250
    DEFAULT_CURVE = QEasingCurve.Type.InOutQuad

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_height_animations = weakref.WeakKeyDictionary()

    def animate_height(
        self,
        target_widget: QWidget,
        end_height: int,
        duration: int = DEFAULT_DURATION,
        curve: QEasingCurve.Type = DEFAULT_CURVE,
    ):
        """Memulai animasi untuk mengubah tinggi widget target."""
        if not target_widget:
            return

        if target_widget in self._active_height_animations:
            try:
                existing_anim = self._active_height_animations.get(target_widget)
                if (
                    existing_anim
                    and existing_anim.state() == QPropertyAnimation.State.Running
                ):
                    existing_anim.stop()
            except RuntimeError:
                if target_widget in self._active_height_animations:
                    del self._active_height_animations[target_widget]

        target_widget.setMinimumHeight(target_widget.height())
        target_widget.setMaximumHeight(QWIDGETSIZE_MAX)

        start_height = target_widget.height()
        if start_height == end_height:
            self._set_flexible_height(target_widget, end_height)
            return

        animation_group = QParallelAnimationGroup(self)

        min_anim = QPropertyAnimation(target_widget, b"minimumHeight", animation_group)
        min_anim.setDuration(duration)
        min_anim.setEasingCurve(curve)
        min_anim.setStartValue(start_height)
        min_anim.setEndValue(end_height)
        animation_group.addAnimation(min_anim)

        max_anim = QPropertyAnimation(target_widget, b"maximumHeight", animation_group)
        max_anim.setDuration(duration)
        max_anim.setEasingCurve(curve)
        max_anim.setStartValue(start_height)
        max_anim.setEndValue(end_height)
        animation_group.addAnimation(max_anim)

        animation_group.finished.connect(
            lambda w_ref=weakref.ref(target_widget): self._on_height_animation_finished(
                w_ref
            )
        )
        self._active_height_animations[target_widget] = animation_group
        animation_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def toggle_height(
        self,
        target_widget: QWidget,
        duration: int = DEFAULT_DURATION,
        curve: QEasingCurve.Type = DEFAULT_CURVE,
    ):
        """
        Membuka atau menutup widget secara otomatis.
        - Jika tertutup (tinggi ~0), akan terbuka ke ukuran kontennya (sizeHint).
        - Jika terbuka, akan tertutup (tinggi 0).
        """
        if not target_widget:
            return

        content_height = target_widget.sizeHint().height()
        current_height = target_widget.height()

        if current_height < content_height / 2:
            self.animate_height(target_widget, content_height, duration, curve)
        else:
            self.animate_height(target_widget, 0, duration, curve)

    @Slot(weakref.ref)
    def _on_height_animation_finished(self, target_widget_ref):
        """Slot yang dipanggil setelah animasi selesai untuk mengatur state fleksibel."""
        target_widget = target_widget_ref()
        if not target_widget:
            return

        self._active_height_animations.pop(target_widget, None)

        if target_widget not in self._active_height_animations:
            try:
                final_height = target_widget.minimumHeight()
                self._set_flexible_height(target_widget, final_height)
            except RuntimeError:
                pass

    def _set_flexible_height(self, widget: QWidget, height: int):
        """
        *** KUNCI PERUBAHAN ADA DI SINI ***
        Mengatur state tinggi widget setelah animasi selesai.
        """
        if height > 0:
            widget.setMinimumHeight(height)
            widget.setMaximumHeight(QWIDGETSIZE_MAX)
        else:
            widget.setFixedHeight(0)


# ============================================
# === KELAS BARU: WidthAnimator ===
# ============================================
class WidthAnimator(QObject):
    """
    Mengelola animasi perubahan lebar (minimumWidth, maximumWidth) untuk sebuah QWidget.
    """

    # --- Nilai Default ---
    DEFAULT_DURATION = 250
    DEFAULT_CURVE = QEasingCurve.Type.InOutQuad

    def __init__(self, parent=None):
        """Inisialisasi WidthAnimator."""
        super().__init__(parent)
        self._active_width_animations = weakref.WeakKeyDictionary()

    def animate_width(
        self,
        target_widget: QWidget,
        end_width: int,
        duration: int = DEFAULT_DURATION,
        curve: QEasingCurve.Type = DEFAULT_CURVE,
    ):
        """
        Memulai animasi untuk mengubah lebar widget target.

        Args:
            target_widget: Widget yang lebarnya akan dianimasikan.
            end_width: Lebar target akhir.
            duration: Durasi animasi dalam milidetik.
            curve: Kurva easing yang akan digunakan.
        """
        if not target_widget:
            print("WidthAnimator Error: target_widget cannot be None.")
            return

        # Hentikan animasi sebelumnya untuk widget ini jika sedang berjalan
        if target_widget in self._active_width_animations:
            existing_anim = self._active_width_animations.get(target_widget)
            if (
                existing_anim
                and existing_anim.state() == QPropertyAnimation.State.Running
            ):
                existing_anim.stop()
            if target_widget in self._active_width_animations:
                del self._active_width_animations[target_widget]

        start_width = target_widget.width()

        # Jangan animasi jika sudah di lebar target
        if start_width == end_width:
            target_widget.setMinimumWidth(end_width)
            target_widget.setMaximumWidth(end_width)
            return

        # Buat grup animasi paralel
        animation_group = QParallelAnimationGroup(self)

        # Animasi properti minimumWidth
        min_anim = QPropertyAnimation(target_widget, b"minimumWidth", animation_group)
        min_anim.setDuration(duration)
        min_anim.setEasingCurve(curve)
        min_anim.setStartValue(start_width)
        min_anim.setEndValue(end_width)
        animation_group.addAnimation(min_anim)

        # Animasi properti maximumWidth
        max_anim = QPropertyAnimation(target_widget, b"maximumWidth", animation_group)
        max_anim.setDuration(duration)
        max_anim.setEasingCurve(curve)
        max_anim.setStartValue(start_width)
        max_anim.setEndValue(end_width)
        animation_group.addAnimation(max_anim)

        # Hubungkan sinyal finished dari GRUP ke slot cleanup internal
        animation_group.finished.connect(
            lambda w=target_widget: self._on_width_animation_finished(w)
        )

        # Simpan referensi animasi aktif dan mulai
        self._active_width_animations[target_widget] = animation_group
        animation_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    @Slot(QWidget)
    def _on_width_animation_finished(self, target_widget: QWidget):
        """Slot internal: Dipanggil setelah animasi lebar selesai."""
        if target_widget in self._active_width_animations:
            del self._active_width_animations[target_widget]

        final_width = target_widget.minimumWidth()
        target_widget.setFixedWidth(final_width)


QWIDGETSIZE_MAX = 16777215


class HeightAnimator(QObject):
    """
    Mengelola animasi perubahan tinggi yang fleksibel untuk sebuah QWidget.
    Setelah animasi selesai, widget dapat menyesuaikan ukurannya secara dinamis.
    """

    DEFAULT_DURATION = 250
    DEFAULT_CURVE = QEasingCurve.Type.InOutQuad

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_height_animations = weakref.WeakKeyDictionary()

    def animate_height(
        self,
        target_widget: QWidget,
        end_height: int,
        duration: int = DEFAULT_DURATION,
        curve: QEasingCurve.Type = DEFAULT_CURVE,
    ):
        """Memulai animasi untuk mengubah tinggi widget target."""
        if not target_widget:
            return

        if target_widget in self._active_height_animations:
            try:
                existing_anim = self._active_height_animations.get(target_widget)
                if (
                    existing_anim
                    and existing_anim.state() == QPropertyAnimation.State.Running
                ):
                    existing_anim.stop()
            except RuntimeError:
                if target_widget in self._active_height_animations:
                    del self._active_height_animations[target_widget]

        target_widget.setMinimumHeight(target_widget.height())
        target_widget.setMaximumHeight(QWIDGETSIZE_MAX)

        start_height = target_widget.height()
        if start_height == end_height:
            self._set_flexible_height(target_widget, end_height)
            return

        animation_group = QParallelAnimationGroup(self)

        min_anim = QPropertyAnimation(target_widget, b"minimumHeight", animation_group)
        min_anim.setDuration(duration)
        min_anim.setEasingCurve(curve)
        min_anim.setStartValue(start_height)
        min_anim.setEndValue(end_height)
        animation_group.addAnimation(min_anim)

        max_anim = QPropertyAnimation(target_widget, b"maximumHeight", animation_group)
        max_anim.setDuration(duration)
        max_anim.setEasingCurve(curve)
        max_anim.setStartValue(start_height)
        max_anim.setEndValue(end_height)
        animation_group.addAnimation(max_anim)

        animation_group.finished.connect(
            lambda w_ref=weakref.ref(target_widget): self._on_height_animation_finished(
                w_ref
            )
        )
        self._active_height_animations[target_widget] = animation_group
        animation_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def toggle_height(
        self,
        target_widget: QWidget,
        duration: int = DEFAULT_DURATION,
        curve: QEasingCurve.Type = DEFAULT_CURVE,
    ):
        """
        Membuka atau menutup widget secara otomatis.
        - Jika tertutup (tinggi ~0), akan terbuka ke ukuran kontennya (sizeHint).
        - Jika terbuka, akan tertutup (tinggi 0).
        """
        if not target_widget:
            return

        content_height = target_widget.sizeHint().height()
        current_height = target_widget.height()

        if current_height < content_height / 2:
            self.animate_height(target_widget, content_height, duration, curve)
        else:
            self.animate_height(target_widget, 0, duration, curve)

    @Slot(weakref.ref)
    def _on_height_animation_finished(self, target_widget_ref):
        """Slot yang dipanggil setelah animasi selesai untuk mengatur state fleksibel."""
        target_widget = target_widget_ref()
        if not target_widget:
            return

        self._active_height_animations.pop(target_widget, None)

        if target_widget not in self._active_height_animations:
            try:
                final_height = target_widget.minimumHeight()
                self._set_flexible_height(target_widget, final_height)
            except RuntimeError:
                pass

    def _set_flexible_height(self, widget: QWidget, height: int):
        """
        *** KUNCI PERUBAHAN ADA DI SINI ***
        Mengatur state tinggi widget setelah animasi selesai.
        """
        if height > 0:
            widget.setMinimumHeight(height)
            widget.setMaximumHeight(QWIDGETSIZE_MAX)
        else:
            widget.setFixedHeight(0)
