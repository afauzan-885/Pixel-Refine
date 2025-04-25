import sys
import weakref
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QStackedWidget,
                             QGraphicsOpacityEffect, QLabel, ) 
from PyQt6.QtCore import (QEasingCurve, QPropertyAnimation, Qt,
                        QTimer, pyqtSlot) 
from PyQt6.QtGui import QFont 

# Import Halaman dan Komponen Anda
from UI.enhance_stack.batch_page_layout import BatchPageLayout
from UI.enhance_stack.single_page_layout import SinglePageLayout
from UI.resources.animation.animation_manager import AnimationType, SlideDirection, StackedWidgetAnimator
from UI.resources.animation.fade import fade
from UI.resources.animation.slide import slide
from .components.top_bar import TopBar
from .logic.database_manager import DatabaseManager

class EnhanceStackPage(QWidget):
    """Halaman utama dengan efek transisi fade antar sub-halaman dan TopBar."""

    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.database_manager = database_manager
        self.layout = QVBoxLayout(self)
        
        # --- Atribut untuk Toast (PINDAH KE SINI) ---
        self.toast_label = None
        self.toast_opacity_effect = None
        self.toast_fade_in_anim = None
        self.toast_fade_out_anim = None
        self.toast_close_timer = None
        # -----------------------------------------
        self.animator = StackedWidgetAnimator(self) # Beri parent jika perlu

        self.top_bar = TopBar()
        self.layout.addWidget(self.top_bar)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget, 1)

        self.single_page_layout = SinglePageLayout(self.database_manager)
        self.batch_page_layout = BatchPageLayout()

        self.stacked_widget.addWidget(self.single_page_layout)
        self.stacked_widget.addWidget(self.batch_page_layout)
        self.stacked_widget.setCurrentWidget(self.single_page_layout)

        # --- Koneksi Sinyal ---
        self.top_bar.single_button.toggled.connect(self._handle_switch_request)
        self.top_bar.batch_button.toggled.connect(self._handle_switch_request)
        self.batch_page_layout.show_toast_requested.connect(self.show_toast) # Koneksi toast tetap
        
        self.top_bar.single_page_import_button.clicked.connect(self.single_page_layout.handle_import_button)
        self.top_bar.single_page_delete_button.clicked.connect(self.single_page_layout.handle_delete_button)
        self.top_bar.batch_page_import_button.clicked.connect(self.batch_page_layout.handle_batch_import_button)
        self.top_bar.batch_page_delete_button.clicked.connect(self.batch_page_layout.handle_delete_all_batches)
        self.top_bar.start_process_batch.clicked.connect(self.batch_page_layout.process_all_batches)
        # ----------------------

        # Atur UI Awal TopBar
        self.top_bar.left_stack.setCurrentIndex(0)
        self.top_bar.right_stack.setCurrentIndex(0)
        
    # --- METODE TOAST (PINDAH KE SINI) ---
    @pyqtSlot(str, object, bool) # Tentukan tipe argumen slot
    def show_toast(self, message, duration=None, is_progress_update=False):
        """Menampilkan toast. Jika is_progress_update=True dan toast sudah ada, hanya update teks."""
        # Hentikan timer lama (selalu aman dilakukan)
        if self.toast_close_timer and self.toast_close_timer.isActive():
            self.toast_close_timer.stop()
            self.toast_close_timer = None

        # Hentikan animasi fade-out lama jika berjalan
        if self.toast_fade_out_anim and self.toast_fade_out_anim.state() == QPropertyAnimation.State.Running:
            self.toast_fade_out_anim.stop()

        # --- Logika Pembaruan atau Pembuatan Baru ---
        if is_progress_update and self.toast_label:
            # --- UPDATE TOAST YANG ADA ---
            if self.toast_fade_in_anim and self.toast_fade_in_anim.state() == QPropertyAnimation.State.Running:
                self.toast_fade_in_anim.stop(); self.toast_fade_in_anim = None
            if self.toast_opacity_effect: self.toast_opacity_effect.setOpacity(1.0)
            else:
                 self.toast_opacity_effect = QGraphicsOpacityEffect(self.toast_label); self.toast_opacity_effect.setOpacity(1.0); self.toast_label.setGraphicsEffect(self.toast_opacity_effect)

            self.toast_label.setText(message); self.toast_label.adjustSize()
            toast_width = self.toast_label.width() + 40; toast_height = self.toast_label.height()
            # --- GUNAKAN UKURAN EnhanceStackPage ('self') ---
            parent_width = self.width(); parent_height = self.height()
            self.toast_label.setGeometry( (parent_width - toast_width) // 2, parent_height - toast_height - 20, toast_width, toast_height )
            # --------------------------------------------
            self.toast_label.raise_(); self.toast_label.show()
        else:
            # --- BUAT TOAST BARU ---
            if self.toast_label:
                if self.toast_fade_in_anim and self.toast_fade_in_anim.state() == QPropertyAnimation.State.Running: self.toast_fade_in_anim.stop()
                self.toast_label.deleteLater()
                self.toast_label = None; self.toast_opacity_effect = None; self.toast_fade_in_anim = None

            # --- Parent adalah 'self' (EnhanceStackPage) ---
            self.toast_label = QLabel(message, self)
            # ---------------------------------------------
            self.toast_label.setStyleSheet(""" background-color: rgba(40, 40, 40, 0.85); color: white; padding: 12px 20px; border-radius: 15px; font-size: 14px; font-weight: bold; """)
            self.toast_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.toast_label.setFont(QFont("Arial", 10)); self.toast_label.adjustSize()

            self.toast_opacity_effect = QGraphicsOpacityEffect(self.toast_label); self.toast_opacity_effect.setOpacity(0.0); self.toast_label.setGraphicsEffect(self.toast_opacity_effect)

            toast_width = self.toast_label.width() + 40; toast_height = self.toast_label.height()
            # --- GUNAKAN UKURAN EnhanceStackPage ('self') ---
            parent_width = self.width(); parent_height = self.height()
            self.toast_label.setGeometry( (parent_width - toast_width) // 2, parent_height - toast_height - 20, toast_width, toast_height )
            # --------------------------------------------

            self.toast_label.raise_(); self.toast_label.show()

            fade_in_anim = QPropertyAnimation(self.toast_opacity_effect, b"opacity", self) # Parent self
            fade_in_anim.setDuration(400); fade_in_anim.setStartValue(0.0); fade_in_anim.setEndValue(1.0); fade_in_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            fade_in_anim.finished.connect(self._on_toast_fade_in_finished)
            fade_in_anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            self.toast_fade_in_anim = fade_in_anim

            if duration:
                self.toast_close_timer = QTimer(self); self.toast_close_timer.setSingleShot(True); self.toast_close_timer.timeout.connect(self._start_toast_fade_out); self.toast_close_timer.start(duration)

    def _on_toast_fade_in_finished(self):
        """Dipanggil setelah animasi fade-in toast selesai."""
        self.toast_fade_in_anim = None

    def _start_toast_fade_out(self):
        """Memulai animasi fade-out untuk toast."""
        if not self.toast_label or not self.toast_opacity_effect: return
        if self.toast_fade_in_anim and self.toast_fade_in_anim.state() == QPropertyAnimation.State.Running: self.toast_fade_in_anim.stop(); self.toast_fade_in_anim = None
        if self.toast_fade_out_anim and self.toast_fade_out_anim.state() == QPropertyAnimation.State.Running: return

        fade_out_anim = QPropertyAnimation(self.toast_opacity_effect, b"opacity", self) # Parent self
        fade_out_anim.setDuration(500); fade_out_anim.setStartValue(self.toast_opacity_effect.opacity()); fade_out_anim.setEndValue(0.0); fade_out_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        fade_out_anim.finished.connect(self._on_toast_fade_out_finished)
        fade_out_anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self.toast_fade_out_anim = fade_out_anim

    def _on_toast_fade_out_finished(self):
        """Dipanggil setelah animasi fade-out toast selesai."""
        if self.toast_label: self.toast_label.hide(); self.toast_label.deleteLater(); self.toast_label = None
        self.toast_opacity_effect = None; self.toast_fade_in_anim = None; self.toast_fade_out_anim = None
        if self.toast_close_timer and self.toast_close_timer.isActive(): self.toast_close_timer.stop()
        self.toast_close_timer = None

    def _handle_switch_request(self):
        """Dipanggil ketika tombol Single/Batch ditekan."""
        if self.top_bar.single_button.isChecked():
            target_main_widget = self.single_page_layout
            target_topbar_index = 0
            main_slide_direction = SlideDirection.RIGHT
        elif self.top_bar.batch_button.isChecked():
            target_main_widget = self.batch_page_layout
            target_topbar_index = 1
            main_slide_direction = SlideDirection.LEFT
        else:
            return

        slide(self.animator, self.stacked_widget, target_main_widget, main_slide_direction, duration=400)
        self.top_bar.left_stack.setCurrentIndex(target_topbar_index)
        self.top_bar.right_stack.setCurrentIndex(target_topbar_index)
