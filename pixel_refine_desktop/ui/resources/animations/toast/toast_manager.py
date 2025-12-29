# UI/resources/toast_manager.py  (atau lokasi lain yang sesuai)

import weakref
from PySide6.QtWidgets import QWidget, QLabel, QGraphicsOpacityEffect
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
from PySide6.QtGui import QFont
from enum import Enum, auto


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


class ToastManager(QObject):
    """
    Manages the display and animation of toast notifications within a parent widget.
    Offers configurable positions and animations (fade, slide).
    """

    def __init__(self, parent: QWidget):
        # Gunakan weakref untuk menghindari reference cycle jika parent
        # juga menyimpan referensi ke ToastManager
        super().__init__(parent)  # Parent QObject tetap diperlukan untuk timer/animasi
        parent_ref = weakref.ref(parent)
        self._parent_ref = parent_ref

        # --- State Internal ---
        self._toast_label: QLabel | None = None
        self._opacity_effect: QGraphicsOpacityEffect | None = None
        self._show_anim: QPropertyAnimation | None = None  # Generic show animation
        self._hide_anim: QPropertyAnimation | None = None  # Generic hide animation
        self._close_timer: QTimer | None = None
        self._current_animation_type: ToastAnimation = (
            ToastAnimation.FADE
        )  # Track active anim

    # --- Konfigurasi Default ---
    default_duration = 3000  # ms
    default_style_sheet = """
        background-color: rgba(40, 40, 40, 0.9);
        color: white;
        padding: 12px 20px;
        border-radius: 15px;
        font-size: 14px;
        font-weight: bold;
    """
    default_font = QFont("Arial", 10)
    default_fade_duration = 400
    default_slide_duration = 500  # Sedikit lebih lambat untuk slide
    default_show_easing_curve = (
        QEasingCurve.Type.OutCubic
    )  # Bagus untuk slide in/fade in
    default_hide_easing_curve = (
        QEasingCurve.Type.InCubic
    )  # Bagus untuk slide out/fade out
    default_vertical_margin = 25
    default_horizontal_margin = 25
    default_position = ToastPosition.BOTTOM_CENTER
    default_animation = ToastAnimation.FADE

    @property
    def parent_widget(self) -> QWidget | None:
        return self._parent_ref()

    # --- Metode Helper Publik (API yang Disederhanakan) ---

    @Slot(str)
    @Slot(str, object)  # Menerima None atau int untuk durasi
    @Slot(str, object, object)  # Menerima None atau ToastPosition
    @Slot(str, object, object, object)  # Menerima None atau ToastAnimation
    def show_message(
        self,
        message: str,
        duration: int | None = None,
        position: ToastPosition | None = None,
        animation: ToastAnimation | None = None,
    ):
        """
        Displays a standard informational toast that disappears after a duration.

        Args:
            message: The message to display.
            duration: Duration in ms. If None, uses default_duration.
            position: Position (optional, uses default).
            animation: Animation type (optional, uses default).
        """
        actual_duration = duration if duration is not None else self.default_duration
        # Panggil metode inti dengan is_progress_update=False
        self._show(message, actual_duration, position, animation, False)

    @Slot(str)
    @Slot(str, object)  # Menerima None atau ToastPosition
    @Slot(str, object, object)  # Menerima None atau ToastAnimation
    def show_progress(
        self,
        message: str,
        position: ToastPosition | None = None,
        animation: ToastAnimation | None = None,
    ):
        """
        Displays or updates a progress toast. Stays visible until hidden
        or replaced by a non-progress toast.

        Args:
            message: The progress message to display or update.
            position: Position (optional, uses default if creating new).
            animation: Animation type (optional, uses default if creating new).
        """
        # Panggil metode inti dengan duration=None dan is_progress_update=True
        self._show(message, None, position, animation, True)

    @Slot()
    def hide(self):
        """
        Starts the animation to hide the currently visible toast, if any.
        Also stops any pending close timer.
        """
        # Hentikan timer close jika ada (misal progress di-hide manual)
        if self._close_timer and self._close_timer.isActive():
            self._close_timer.stop()
        self._close_timer = None  # Hapus referensi timer

        # Mulai animasi hide (fade out atau slide out)
        self._start_hide_animation()

    # --- Metode Inti Internal (Implementasi Detail) ---

    # Ubah nama show menjadi _show untuk menandakan ini bukan API utama lagi
    # Signature asli dipertahankan untuk mengakomodasi parameter baru
    def _show(
        self,
        message: str,
        duration: int | None = None,  # Bisa None untuk progress
        position: ToastPosition | None = None,
        animation: ToastAnimation | None = None,
        is_progress_update: bool = False,
    ):  # Parameter internal
        """
        Internal method to display or update a toast. Handles logic for
        new toasts vs. progress updates.

        (Implementasi _show sebagian besar sama dengan 'show' Anda sebelumnya,
         pastikan logika is_progress_update di dalamnya sudah benar)
        """
        parent = self.parent_widget
        if not parent:
            print("ToastManager Error: Parent widget is no longer available.")
            return

        actual_position = position if position is not None else self.default_position
        actual_animation = (
            animation if animation is not None else self.default_animation
        )

        # --- Hentikan Timer/Animasi yang Sedang Berjalan ---
        # Penting: panggil ini SEBELUM cek is_progress_update
        # agar animasi hide sebelumnya (jika ada) berhenti
        self._clear_running_operations()

        # --- Logika Progress Update ---
        # Cek is_progress_update DAN apakah label toast sudah ada/terlihat
        if is_progress_update and self._toast_label and self._toast_label.isVisible():
            # Pastikan opacity 1.0
            if self._opacity_effect:
                self._opacity_effect.setOpacity(1.0)
            elif actual_animation == ToastAnimation.FADE:
                # Jika tidak ada efek (mungkin dari slide sebelumnya) tapi sekarang FADE
                self._opacity_effect = QGraphicsOpacityEffect(self._toast_label)
                self._toast_label.setGraphicsEffect(self._opacity_effect)
                self._opacity_effect.setOpacity(1.0)

            self._toast_label.setText(message)
            self._toast_label.adjustSize()
            # Hitung ulang posisi jika perlu (misal parent resize)
            final_pos, final_size = self._calculate_geometry(actual_position)
            if final_pos and final_size:
                self._toast_label.setGeometry(QRect(final_pos, final_size))
            self._toast_label.raise_()
            self._toast_label.show()  # Pastikan show dipanggil lagi

            # Progress update TIDAK memulai timer close atau animasi baru
            return  # Selesai untuk progress update

        # --- Logika Toast Baru atau Penggantian ---
        # Hapus toast lama jika ada
        self._cleanup_toast_widget()

        # --- Buat Elemen Toast Baru ---
        self._toast_label = QLabel(message, parent)
        # ... (Setup QLabel: stylesheet, alignment, font, adjustSize, WA_DeleteOnClose) ...
        self._toast_label.setStyleSheet(self.default_style_sheet)
        self._toast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._toast_label.setFont(self.default_font)
        self._toast_label.adjustSize()  # Hitung ukuran awal berdasarkan teks
        self._toast_label.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._current_animation_type = actual_animation

        # --- Persiapan Animasi ---
        final_pos, final_size = self._calculate_geometry(actual_position)
        if not final_pos or not final_size:
            print("ToastManager Warning: Could not determine final geometry.")
            self._cleanup_toast_widget()
            return

        initial_pos = final_pos
        initial_opacity = 1.0

        if actual_animation == ToastAnimation.FADE:
            self._opacity_effect = QGraphicsOpacityEffect(self._toast_label)
            self._toast_label.setGraphicsEffect(self._opacity_effect)
            initial_opacity = 0.0
            self._opacity_effect.setOpacity(initial_opacity)
        elif actual_animation in [
            ToastAnimation.SLIDE_FROM_BOTTOM,
            ToastAnimation.SLIDE_FROM_TOP,
            ToastAnimation.SLIDE_FROM_LEFT,
            ToastAnimation.SLIDE_FROM_RIGHT,
        ]:
            initial_pos = self._get_offscreen_start_pos(
                actual_animation, final_pos, final_size
            )
            if self._opacity_effect:
                self._toast_label.setGraphicsEffect(None)  # type: ignore
                self._opacity_effect = None

        self._toast_label.setGeometry(QRect(initial_pos, final_size))
        self._toast_label.raise_()
        self._toast_label.show()

        # --- Mulai Animasi Masuk ---
        if actual_animation == ToastAnimation.FADE:
            self._start_fade_in_animation()
        else:  # Slide
            self._start_slide_in_animation(final_pos)  # Target pos diperlukan

        # --- Timer HANYA jika durasi ditentukan (bukan None / progress) ---
        if duration is not None:
            self._close_timer = QTimer(self)
            self._close_timer.setSingleShot(True)
            # Gunakan metode 'hide' publik sebagai target timeout
            self._close_timer.timeout.connect(self.hide)
            self._close_timer.start(duration)

    def _clear_running_operations(self):
        """Menghentikan dan membersihkan timer dan animasi yang sedang berjalan."""
        if self._close_timer and self._close_timer.isActive():
            self._close_timer.stop()
        self._close_timer = None

        if (
            self._show_anim
            and self._show_anim.state() == QPropertyAnimation.State.Running
        ):
            self._show_anim.stop()
        self._show_anim = None

        if (
            self._hide_anim
            and self._hide_anim.state() == QPropertyAnimation.State.Running
        ):
            self._hide_anim.stop()
        self._hide_anim = None

    def _cleanup_toast_widget(self):
        """Menjadwalkan penghapusan widget toast dan mereset state terkait."""
        if self._toast_label:
            # Sembunyikan segera jika masih terlihat (meski jarang)
            self._toast_label.hide()
            # Hapus efek grafis jika ada sebelum menghapus label
            if self._toast_label.graphicsEffect():
                self._toast_label.setGraphicsEffect(None)  # type: ignore  # Hapus referensi
            self._toast_label.deleteLater()
        self._toast_label = None
        self._opacity_effect = None  # Pastikan efek juga dibersihkan

    # --- Metode Utama ---
    # Tipe parameter 'duration' diubah agar konsisten dengan ToastManager asli
    @Slot(str, object, bool)  # Pertahankan signature untuk kompatibilitas sinyal
    @Slot(str)
    @Slot(str, int)
    @Slot(str, int, bool)
    @Slot(str, int, ToastPosition, ToastAnimation, bool)
    def show(
        self,
        message: str,
        duration: int | None = None,  # Tetap pakai int | None
        position: ToastPosition | None = None,
        animation: ToastAnimation | None = None,
        is_progress_update: bool = False,
    ):
        """
        Displays a toast notification with configurable position and animation.

        Args:
            message: The text message to display.
            duration: How long the toast should be visible (in ms).
                      If None, uses default_duration unless is_progress_update.
                      If is_progress_update is True, duration is ignored.
            position: Where to place the toast (e.g., ToastPosition.BOTTOM_RIGHT).
                      Defaults to self.default_position.
            animation: How the toast appears/disappears (e.g., ToastAnimation.SLIDE_FROM_BOTTOM).
                       Defaults to self.default_animation.
            is_progress_update: If True and a toast is visible, only update
                                the text without fade/slide animations. If False,
                                create a new toast with animations.
        """
        parent = self.parent_widget
        if not parent:
            print("ToastManager Error: Parent widget is no longer available.")
            return

        # Tentukan nilai aktual atau default
        actual_duration = duration if duration is not None else self.default_duration
        actual_position = position if position is not None else self.default_position
        actual_animation = (
            animation if animation is not None else self.default_animation
        )

        # --- Hentikan Timer/Animasi yang Sedang Berjalan ---
        self._clear_running_operations()

        # --- Logika Progress Update ---
        if is_progress_update and self._toast_label and self._toast_label.isVisible():
            # Pastikan opacity 1.0 (jika sebelumnya fade out)
            if self._opacity_effect:
                self._opacity_effect.setOpacity(1.0)
            elif (
                actual_animation == ToastAnimation.FADE
            ):  # Jika animasi default FADE, perlu efek
                self._opacity_effect = QGraphicsOpacityEffect(self._toast_label)
                self._toast_label.setGraphicsEffect(self._opacity_effect)
                self._opacity_effect.setOpacity(1.0)

            # Update teks, ukuran, posisi
            self._toast_label.setText(message)
            self._toast_label.adjustSize()
            final_pos, final_size = self._calculate_geometry(actual_position)
            if final_pos and final_size:
                self._toast_label.setGeometry(QRect(final_pos, final_size))
            self._toast_label.raise_()
            self._toast_label.show()

            # Progress update TIDAK memulai timer close atau animasi baru
            return  # Selesai untuk progress update

        # --- Logika Toast Baru atau Penggantian ---
        # Hapus toast lama jika ada (setelah menghentikan operasinya)
        self._cleanup_toast_widget()

        # --- Buat Elemen Toast Baru ---
        self._toast_label = QLabel(message, parent)
        self._toast_label.setStyleSheet(self.default_style_sheet)
        self._toast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._toast_label.setFont(self.default_font)
        self._toast_label.adjustSize()  # Hitung ukuran awal berdasarkan teks
        self._toast_label.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Simpan tipe animasi yang digunakan untuk toast ini
        self._current_animation_type = actual_animation

        # --- Persiapan Animasi (Opacity/Posisi Awal) ---
        final_pos, final_size = self._calculate_geometry(actual_position)
        if not final_pos or not final_size:
            print(
                "ToastManager Warning: Could not determine final geometry. Toast might not show."
            )
            self._cleanup_toast_widget()  # Bersihkan label yang baru dibuat
            return

        initial_pos = final_pos
        initial_opacity = 1.0

        if actual_animation == ToastAnimation.FADE:
            self._opacity_effect = QGraphicsOpacityEffect(self._toast_label)
            self._toast_label.setGraphicsEffect(self._opacity_effect)
            initial_opacity = 0.0
            self._opacity_effect.setOpacity(initial_opacity)  # Mulai transparan
        elif actual_animation in [
            ToastAnimation.SLIDE_FROM_BOTTOM,
            ToastAnimation.SLIDE_FROM_TOP,
            ToastAnimation.SLIDE_FROM_LEFT,
            ToastAnimation.SLIDE_FROM_RIGHT,
        ]:
            # Tentukan posisi awal di luar layar
            initial_pos = self._get_offscreen_start_pos(
                actual_animation, final_pos, final_size
            )
            # Pastikan opacity 1 untuk slide
            if (
                self._opacity_effect
            ):  # Hapus efek opacity jika ada dari toast sebelumnya
                self._toast_label.setGraphicsEffect(None)  # type: ignore
                self._opacity_effect = None

        # Terapkan posisi awal dan ukuran
        self._toast_label.setGeometry(QRect(initial_pos, final_size))

        # Tampilkan (mungkin transparan atau di luar layar)
        self._toast_label.raise_()
        self._toast_label.show()

        # --- Mulai Animasi Masuk (Show) ---
        if actual_animation == ToastAnimation.FADE:
            self._start_fade_in_animation()
        else:
            self._start_slide_in_animation(final_pos)

        if duration is not None:
            self._close_timer = QTimer(self)
            self._close_timer.setSingleShot(True)
            # Hubungkan ke metode hide generik
            self._close_timer.timeout.connect(self._start_hide_animation)
            self._close_timer.start(actual_duration)

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
            padding_v = 12 * 2
            padding_h = 20 * 2
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

    # --- Metode Animasi ---

    def _start_fade_in_animation(self):
        """Memulai animasi fade-in."""
        if not self._toast_label or not self._opacity_effect:
            return

        self._show_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._show_anim.setDuration(self.default_fade_duration)
        self._show_anim.setStartValue(0.0)
        self._show_anim.setEndValue(1.0)
        self._show_anim.setEasingCurve(self.default_show_easing_curve)
        self._show_anim.finished.connect(self._on_show_animation_finished)
        self._show_anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _start_slide_in_animation(self, target_pos: QPoint):
        """Memulai animasi slide-in."""
        if not self._toast_label:
            return

        # Animasi pada properti 'pos'
        self._show_anim = QPropertyAnimation(self._toast_label, b"pos", self)
        self._show_anim.setDuration(self.default_slide_duration)
        self._show_anim.setEndValue(target_pos)
        self._show_anim.setEasingCurve(self.default_show_easing_curve)
        self._show_anim.finished.connect(self._on_show_animation_finished)
        self._show_anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _on_show_animation_finished(self):
        """Dipanggil setelah animasi show (fade/slide) selesai."""
        self._show_anim = None
        # Opcional: Reposisi ulang jika ukuran parent mungkin berubah drastis
        # Ini bisa menyebabkan sedikit lompatan jika ukuran berubah signifikan
        # final_pos, final_size = self._calculate_geometry(self.default_position) # Ganti dg posisi aktual
        # if final_pos and self._toast_label:
        #     self._toast_label.move(final_pos)

    def _start_hide_animation(self):
        """Memulai animasi hide (fade out atau slide out) berdasarkan _current_animation_type."""
        if not self._toast_label or (
            self._hide_anim
            and self._hide_anim.state() == QPropertyAnimation.State.Running
        ):
            return

        if (
            self._show_anim
            and self._show_anim.state() == QPropertyAnimation.State.Running
        ):
            self._show_anim.stop()
        self._show_anim = None

        if self._current_animation_type == ToastAnimation.FADE:
            self._start_fade_out_animation()
        elif self._current_animation_type in [
            ToastAnimation.SLIDE_FROM_BOTTOM,
            ToastAnimation.SLIDE_FROM_TOP,
            ToastAnimation.SLIDE_FROM_LEFT,
            ToastAnimation.SLIDE_FROM_RIGHT,
        ]:
            self._start_slide_out_animation()
        else:
            print(
                f"Warning: Unknown animation type '{self._current_animation_type}' for hiding."
            )
            self._on_hide_animation_finished()

    def _start_fade_out_animation(self):
        """Memulai animasi fade-out."""
        if not self._toast_label or not self._opacity_effect:
            self._on_hide_animation_finished()  # Langsung cleanup jika ada yg hilang
            return

        self._hide_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._hide_anim.setDuration(self.default_fade_duration)
        self._hide_anim.setStartValue(
            self._opacity_effect.opacity()
        )  # Mulai dari opacity saat ini
        self._hide_anim.setEndValue(0.0)
        self._hide_anim.setEasingCurve(self.default_hide_easing_curve)
        self._hide_anim.finished.connect(self._on_hide_animation_finished)
        self._hide_anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _start_slide_out_animation(self):
        """Memulai animasi slide-out kembali ke arah datangnya."""
        if not self._toast_label:
            self._on_hide_animation_finished()
            return

        current_pos = self._toast_label.pos()
        current_size = self._toast_label.size()

        target_pos = self._get_offscreen_start_pos(
            self._current_animation_type, current_pos, current_size
        )

        self._hide_anim = QPropertyAnimation(self._toast_label, b"pos", self)
        self._hide_anim.setDuration(self.default_slide_duration)
        self._hide_anim.setStartValue(current_pos)
        self._hide_anim.setEndValue(target_pos)
        self._hide_anim.setEasingCurve(self.default_hide_easing_curve)  # Kurva masuk
        self._hide_anim.finished.connect(self._on_hide_animation_finished)
        self._hide_anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _on_hide_animation_finished(self):
        """Dipanggil setelah animasi hide selesai. Membersihkan toast."""
        self._hide_anim = None
        self._cleanup_toast_widget()
        self._close_timer = None
