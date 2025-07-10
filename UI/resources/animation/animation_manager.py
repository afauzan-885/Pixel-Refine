import weakref
from PySide6.QtWidgets import QStackedWidget, QGraphicsOpacityEffect, QWidget
from PySide6.QtCore import (QObject, QPropertyAnimation, QEasingCurve, Slot,
                          QParallelAnimationGroup, QPoint, QRect, QTimer)

from enum import Enum, auto

class AnimationType(Enum): FADE=auto(); SLIDE_LEFT=auto(); SLIDE_RIGHT=auto(); SLIDE_UP=auto(); SLIDE_DOWN=auto(); ZOOM=auto()
class SlideDirection(Enum): LEFT=auto(); RIGHT=auto(); UP=auto(); DOWN=auto()

class StackedWidgetAnimator(QObject):
    DEFAULT_DURATION_OUT = 150
    DEFAULT_DURATION_IN = 250
    DEFAULT_CURVE_OUT = QEasingCurve.Type.OutQuad
    DEFAULT_CURVE_IN = QEasingCurve.Type.InQuad

    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity_effects = weakref.WeakValueDictionary()
        self._active_transitions = {} 
        self._transition_data = {}   
        self._active_fade_outs = {}

    def transition_out(self, widget: QWidget, duration: int = 300,
                       curve: QEasingCurve.Type = QEasingCurve.Type.OutQuad, on_finished_callback=None):
        """
        Animator fade-out yang sangat robust dan self healing.
        Jika widget sudah dihapus atau invalid, langsung panggil callback tanpa error.
        """

        if widget is None:
            if on_finished_callback:
                QTimer.singleShot(0, on_finished_callback)
            return

        # Cek validitas widget dengan try-except akses properti
        try:
            _ = widget.isVisible()
        except RuntimeError:
            if on_finished_callback:
                QTimer.singleShot(0, on_finished_callback)
            return
        except Exception:
            if on_finished_callback:
                QTimer.singleShot(0, on_finished_callback)
            return

        # Hentikan animasi fade-out lama jika masih jalan
        try:
            if widget in self._active_fade_outs:
                old_anim = self._active_fade_outs.get(widget)
                if old_anim is not None and old_anim.state() == QPropertyAnimation.State.Running:
                    old_anim.stop()
        except Exception:
            pass

        # Siapkan efek opacity dengan aman
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
        except Exception:
            if on_finished_callback:
                QTimer.singleShot(0, on_finished_callback)
            return

        # Buat animasi fade out
        anim = QPropertyAnimation(opacity_effect, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(curve)

        widget_ref = weakref.ref(widget)
        effect_ref = weakref.ref(opacity_effect)

        def on_anim_finished():
            w = widget_ref()
            e = effect_ref()
            if w and e:
                try:
                    w.setGraphicsEffect(None)
                except Exception:
                    pass
            if w in self._active_fade_outs:
                self._active_fade_outs.pop(w, None)

        anim.finished.connect(on_anim_finished)
        if on_finished_callback:
            anim.finished.connect(on_finished_callback)

        try:
            self._active_fade_outs[widget] = anim
            anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        except RuntimeError:
            if on_finished_callback:
                QTimer.singleShot(0, on_finished_callback)
            return
        except Exception:
            if on_finished_callback:
                QTimer.singleShot(0, on_finished_callback)
            return

    # =====================================================
    # === Metode Inti (Lebih Fleksibel, bisa tetap ada) ===
    # =====================================================
    def transition_in(self, stack_widget: QStackedWidget, target,
                        animation_type: AnimationType = AnimationType.FADE,
                        duration_out: int = DEFAULT_DURATION_OUT,
                        duration_in: int = DEFAULT_DURATION_IN,
                        curve_out: QEasingCurve.Type = DEFAULT_CURVE_OUT,
                        curve_in: QEasingCurve.Type = DEFAULT_CURVE_IN):
        """ Memulai animasi transisi. """
        if not stack_widget:
            return

        current_widget = stack_widget.currentWidget()
        target_widget, target_index = self._validate_target(stack_widget, target)

        if not target_widget or target_index == -1 or target_widget == current_widget or \
           (stack_widget in self._active_transitions and self._active_transitions[stack_widget].state() == QPropertyAnimation.State.Running):
            return 
        # --- Hentikan transisi lama jika ada ---
        if stack_widget in self._active_transitions:
             anim = self._active_transitions.pop(stack_widget)
             if anim and anim.state() == QPropertyAnimation.State.Running:
                 anim.stop()
                 if stack_widget in self._transition_data: del self._transition_data[stack_widget]
                 current_effect = current_widget.graphicsEffect()
                 if isinstance(current_effect, QGraphicsOpacityEffect): current_effect.setOpacity(1.0)


        # Simpan data transisi (termasuk widget lama)
        self._transition_data[stack_widget] = {
            'target': target, 'in_duration': duration_in, 'in_curve': curve_in,
            'type': animation_type, 'old_widget': current_widget 
        }

        # --- Mulai Fase Out ---
        current_effect = current_widget.graphicsEffect()
        if not isinstance(current_effect, QGraphicsOpacityEffect):
            current_effect = QGraphicsOpacityEffect(current_widget)
            current_widget.setGraphicsEffect(current_effect)
        current_effect.setOpacity(1.0) 

        # 2. Buat Grup Animasi Out
        out_group = QParallelAnimationGroup(self)
        fade_out_anim = QPropertyAnimation(current_effect, b"opacity", out_group)
        fade_out_anim.setDuration(duration_out); fade_out_anim.setEasingCurve(curve_out)
        fade_out_anim.setStartValue(1.0); fade_out_anim.setEndValue(0.0)
        out_group.addAnimation(fade_out_anim)
        
        geom_anim_out = self._create_outgoing_geometry_animation(current_widget, animation_type, duration_out, curve_out, out_group)
        if geom_anim_out: out_group.addAnimation(geom_anim_out)

        # 3. Hubungkan Finished ke Slot Internal
        out_group.finished.connect(lambda sw=stack_widget: self._on_animation_out_finished(sw))

        # 4. Simpan & Mulai
        self._active_transitions[stack_widget] = out_group
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
        target_widget = None; target_index = -1
        if isinstance(target, QWidget):
            target_widget = target; target_index = stack_widget.indexOf(target_widget)
            if target_index == -1: 
                print(f"Animator Error: Target widget {target_widget} not in stack {stack_widget.objectName()}.")
        elif isinstance(target, int):
            target_index = target; target_widget = stack_widget.widget(target_index)
            if not target_widget:
                print(f"Animator Error: No widget at index {target_index} in stack {stack_widget.objectName()}.")
        else:
            print(f"Animator Error: Invalid target type: {type(target)}")
        return target_widget, target_index

    def _create_outgoing_geometry_animation(self, widget, anim_type, duration, curve, parent_group):
        """Membuat animasi geometri/posisi untuk widget yang keluar."""
        geom_anim = None; w = widget.width(); h = widget.height(); current_pos = widget.pos()
        end_value = None; prop_name = None
        if anim_type == AnimationType.SLIDE_LEFT: prop_name, end_value = b"pos", QPoint(-w, current_pos.y())
        elif anim_type == AnimationType.SLIDE_RIGHT: prop_name, end_value = b"pos", QPoint(w, current_pos.y())
        elif anim_type == AnimationType.SLIDE_UP: prop_name, end_value = b"pos", QPoint(current_pos.x(), -h)
        elif anim_type == AnimationType.SLIDE_DOWN: prop_name, end_value = b"pos", QPoint(current_pos.x(), h)
        elif anim_type == AnimationType.ZOOM: prop_name, end_value = b"geometry", QRect(w // 2, h // 2, 0, 0)
        if prop_name and end_value is not None:
            start_value = widget.geometry() if prop_name == b"geometry" else current_pos
            geom_anim = QPropertyAnimation(widget, prop_name, parent_group); geom_anim.setDuration(duration); geom_anim.setEasingCurve(curve); geom_anim.setStartValue(start_value); geom_anim.setEndValue(end_value)
        return geom_anim

    def _create_incoming_geometry_animation(self, widget, anim_type, duration, curve, parent_group):
        """Membuat animasi geometri/posisi untuk widget yang masuk."""
        geom_anim = None; parent_stack = widget.parentWidget()
        if not isinstance(parent_stack, QStackedWidget): return None
        w = parent_stack.width(); h = parent_stack.height(); final_pos = QPoint(0, 0); final_geom = parent_stack.rect()
        start_value = None; end_value = None; prop_name = None
        if anim_type == AnimationType.SLIDE_LEFT: start_value, end_value, prop_name = QPoint(w, final_pos.y()), final_pos, b"pos"
        elif anim_type == AnimationType.SLIDE_RIGHT: start_value, end_value, prop_name = QPoint(-w, final_pos.y()), final_pos, b"pos"
        elif anim_type == AnimationType.SLIDE_UP: start_value, end_value, prop_name = QPoint(final_pos.x(), h), final_pos, b"pos"
        elif anim_type == AnimationType.SLIDE_DOWN: start_value, end_value, prop_name = QPoint(final_pos.x(), -h), final_pos, b"pos"
        elif anim_type == AnimationType.ZOOM: start_value, end_value, prop_name = QRect(w // 2, h // 2, 0, 0), final_geom, b"geometry"
        if prop_name and start_value is not None and end_value is not None:
            if prop_name == b"geometry": widget.setGeometry(start_value)
            else: widget.move(start_value)
            widget.setVisible(True)
            geom_anim = QPropertyAnimation(widget, prop_name, parent_group); geom_anim.setDuration(duration); geom_anim.setEasingCurve(curve); geom_anim.setStartValue(start_value); geom_anim.setEndValue(end_value)
        return geom_anim


    @Slot(QStackedWidget)
    def _on_animation_out_finished(self, stack_widget: QStackedWidget):
        """Slot internal: Dipanggil setelah animasi 'out' selesai."""
        transition_data = self._transition_data.get(stack_widget)
        if not transition_data: print(f"Animator Error: Data lost {stack_widget}"); return

        old_widget = transition_data.get('old_widget')
        target = transition_data['target']
        animation_type = transition_data['type']

        # --- Reset Widget Lama ---
        if old_widget:
            old_effect = old_widget.graphicsEffect()
            if isinstance(old_effect, QGraphicsOpacityEffect): old_effect.setOpacity(1.0)
            if animation_type != AnimationType.FADE: old_widget.setVisible(False); old_widget.move(0, 0); old_widget.setGeometry(stack_widget.rect()); old_widget.setVisible(True)
        
        # --- Lakukan Switch Widget SEKARANG ---
        new_widget, new_index = self._validate_target(stack_widget, target)
        if new_index != -1:
            stack_widget.setCurrentIndex(new_index)
            new_widget = stack_widget.widget(new_index)
        else:
             if stack_widget in self._active_transitions: del self._active_transitions[stack_widget];
             if stack_widget in self._transition_data: del self._transition_data[stack_widget]; return
        if not new_widget: 
            return

        # --- TUNDA FASE IN SEDIKIT ---
        QTimer.singleShot(0, lambda sw=stack_widget, nw=new_widget, td=transition_data:
                              self._start_incoming_animation(sw, nw, td))
        
    def _start_incoming_animation(self, stack_widget: QStackedWidget, new_widget: QWidget, transition_data: dict):
        # Validasi widget new_widget
        try:
            if new_widget is None:
                return
            _ = new_widget.isVisible()
        except RuntimeError:
            return
        except Exception as e:
            return

        # Terapkan efek opacity dengan aman
        try:
            new_effect = new_widget.graphicsEffect()
            if not isinstance(new_effect, QGraphicsOpacityEffect):
                new_effect = QGraphicsOpacityEffect(new_widget)
                new_widget.setGraphicsEffect(new_effect)
            new_effect.setOpacity(0.0) 
        except RuntimeError:
            return
        except Exception as e:
            return

        # Buat animasi grup masuk
        in_group = QParallelAnimationGroup(self)
        fade_in_anim = QPropertyAnimation(new_effect, b"opacity", in_group)
        fade_in_anim.setDuration(transition_data['in_duration'])
        fade_in_anim.setEasingCurve(transition_data['in_curve'])
        fade_in_anim.setStartValue(0.0)
        fade_in_anim.setEndValue(1.0)
        in_group.addAnimation(fade_in_anim)

        geom_anim_in = self._create_incoming_geometry_animation(
            new_widget, transition_data['type'], transition_data['in_duration'], transition_data['in_curve'], in_group)
        if geom_anim_in:
            in_group.addAnimation(geom_anim_in)

        # Hubungkan selesai & mulai animasi
        in_group.finished.connect(lambda sw=stack_widget: self._on_animation_in_finished(sw))
        self._active_transitions[stack_widget] = in_group
        in_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


    @Slot(QStackedWidget)
    def _on_animation_in_finished(self, stack_widget: QStackedWidget):
        """Slot internal: Dipanggil setelah animasi 'in' selesai."""
        current_widget = stack_widget.currentWidget()

        if current_widget:
            if current_widget.pos() != QPoint(0,0): current_widget.move(0,0)
            current_effect = current_widget.graphicsEffect()
            if isinstance(current_effect, QGraphicsOpacityEffect):
                 current_widget.setGraphicsEffect(None) 
                 if current_widget in self._opacity_effects:
                      del self._opacity_effects[current_widget]

        # Bersihkan state transisi
        if stack_widget in self._active_transitions: del self._active_transitions[stack_widget]
        if stack_widget in self._transition_data: del self._transition_data[stack_widget]

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

    def animate_width(self,
                      target_widget: QWidget,
                      end_width: int,
                      duration: int = DEFAULT_DURATION,
                      curve: QEasingCurve.Type = DEFAULT_CURVE):
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
            if existing_anim and existing_anim.state() == QPropertyAnimation.State.Running:
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
        animation_group.finished.connect(lambda w=target_widget: self._on_width_animation_finished(w))

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