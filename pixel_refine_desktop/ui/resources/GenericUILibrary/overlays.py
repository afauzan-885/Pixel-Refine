"""
Overlay Components for GenericUILibrary.
Improved Version: True Gaussian Blur & Ghosting Fix.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
    QGraphicsBlurEffect,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QApplication,
)
from PySide6.QtGui import QPainter, QColor, QPixmap, QMouseEvent
from PySide6.QtCore import Qt, QEvent, QPoint, QRect, QTimer


class OverlayPosition:
    """Enum definitions for overlay positioning."""

    TOP_LEFT = 1
    TOP_CENTER = 2
    TOP_RIGHT = 3
    BOTTOM_LEFT = 4
    BOTTOM_CENTER = 5
    BOTTOM_RIGHT = 6
    CENTER = 7
    LEFT_CENTER = 8
    RIGHT_CENTER = 9


class OverlayContainer(QWidget):
    def __init__(
        self,
        parent=None,
        position=OverlayPosition.BOTTOM_CENTER,
        margin=20,
        smart_positioning=True,
        close_on_click_outside=False,
        dim_background=False,
        dim_opacity=0.4,
        blur_background=False,
        blur_radius=15,  # Default radius ditingkatkan agar lebih soft
        shadow_enabled=False,
        shadow_blur_radius=20,
        shadow_color=QColor(0, 0, 0, 80),
        shadow_offset=QPoint(0, 4),
    ):
        super().__init__(parent)
        self.preferred_position = position
        self.margin = margin
        self.smart_positioning = smart_positioning
        self.close_on_click_outside = close_on_click_outside

        self.dim_background = dim_background
        self.dim_opacity = dim_opacity
        self.blur_background = blur_background
        self.blur_radius = blur_radius
        self.shadow_enabled = shadow_enabled
        self.shadow_blur_radius = shadow_blur_radius
        self.shadow_color = shadow_color
        self.shadow_offset = shadow_offset

        self.setObjectName("OverlayContainer")

        # Modal Logic
        self.is_modal = self.dim_background or self.blur_background

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.content_wrapper = QWidget(self)
        self.content_wrapper.setObjectName("OverlayContentWrapper")
        self.content_wrapper.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground, True
        )

        self.wrapper_layout = QVBoxLayout(self.content_wrapper)
        self.wrapper_layout.setContentsMargins(0, 0, 0, 0)
        self.wrapper_layout.setSpacing(0)

        if self.is_modal:
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.content_wrapper.setParent(self)
        else:
            self.main_layout.addWidget(self.content_wrapper)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        if self.shadow_enabled:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(self.shadow_blur_radius)
            shadow.setColor(self.shadow_color)
            shadow.setOffset(self.shadow_offset)
            self.content_wrapper.setGraphicsEffect(shadow)

        self._blurred_bg = None

        # Timer untuk menghandle resize agar tidak spam grab()
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(100)  # Delay 100ms setelah resize selesai
        self._resize_timer.timeout.connect(self._capture_blur)

        if parent:
            self.setParent(parent)
            parent.installEventFilter(self)
            self._update_position()

    def set_content(self, widget):
        while self.wrapper_layout.count():
            item = self.wrapper_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.wrapper_layout.addWidget(widget)
        self.content_wrapper.adjustSize()
        if not self.is_modal:
            self.adjustSize()
        self._update_position()

    def setParent(self, parent, mode=Qt.WindowType.Widget):
        super().setParent(parent)
        if parent:
            parent.installEventFilter(self)
            self.raise_()
            self._update_position()

    def showEvent(self, event):
        self._update_position()
        self.raise_()

        if self.is_modal:
            if self.parent():
                self.resize(self.parent().size())
                self.move(0, 0)

            if self.blur_background:
                # Capture blur slightly delayed to ensure UI is ready
                QTimer.singleShot(10, self._capture_blur)

        if self.close_on_click_outside and not self.is_modal:
            window = self.window()
            if window:
                window.installEventFilter(self)
        super().showEvent(event)

    def _capture_blur(self):
        """
        Capture parent screenshot and apply TRUE Gaussian Blur.
        Fixed: Prevents capturing self (ghosting).
        """
        parent = self.parent()
        if not parent:
            return

        # 1. HIDE SELF: Kunci untuk menghindari bug "Ghosting"
        # Kita sembunyikan overlay agar parent.grab() hanya mengambil background asli.
        was_visible = self.isVisible()
        self.setVisible(False)

        # Force process events agar hide() benar-benar terjadi sebelum grab()
        # (Opsional, tapi membantu di beberapa OS)
        # QApplication.processEvents()

        try:
            bg_pixmap = parent.grab()
        except Exception as e:
            print(f"Capture failed: {e}")
            if was_visible:
                self.setVisible(True)
            return

        # 2. RESTORE VISIBILITY
        if was_visible:
            self.setVisible(True)

        # 3. APPLY TRUE BLUR (Gaussian)
        if self.blur_radius > 0:
            self._blurred_bg = self._apply_gaussian_blur(bg_pixmap, self.blur_radius)
        else:
            self._blurred_bg = bg_pixmap

        self.update()

    def _apply_gaussian_blur(self, pixmap, radius):
        """
        Applies a high-quality Gaussian blur using QGraphicsBlurEffect.
        """
        if pixmap.isNull():
            return pixmap

        # Optimization: Downscale sedikit (misal bagi 2) untuk performa
        # jika gambarnya sangat besar (Full HD/4K).
        # Blur radius perlu disesuaikan jika di-downscale.
        scale_factor = 2
        scaled_size = pixmap.size() / scale_factor

        # Buat temporary graphics scene
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem()

        # Scale pixmap down untuk performa (optional, tapi sangat disarankan)
        src_img = pixmap.scaled(
            scaled_size,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        item.setPixmap(src_img)

        # Apply Blur Effect
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(
            radius
        )  # Radius tidak perlu dibagi scale karena kita ingin blur yang 'kuat'
        blur.setBlurHints(QGraphicsBlurEffect.BlurHint.PerformanceHint)
        item.setGraphicsEffect(blur)

        scene.addItem(item)

        # Render scene kembali ke pixmap
        res_pixmap = QPixmap(scaled_size)
        res_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(res_pixmap)
        scene.render(painter)
        painter.end()

        # Tidak perlu upscale kembali di sini.
        # Kita akan menggambarnya stretched di paintEvent (lebih efisien).
        return res_pixmap

    def hideEvent(self, event):
        if self.close_on_click_outside and not self.is_modal:
            window = self.window()
            if window:
                window.removeEventFilter(self)
        super().hideEvent(event)

    def paintEvent(self, event):
        if not self.is_modal:
            super().paintEvent(event)
            return

        painter = QPainter(self)

        # Draw Blurred BG
        if self.blur_background and self._blurred_bg:
            # Kita gambar blurred_bg memenuhi rect self.
            # Karena _apply_gaussian_blur mungkin menghasilkan gambar lebih kecil (downscaled),
            # kita biarkan drawPixmap melakukan stretching (smooth secara default).
            painter.drawPixmap(self.rect(), self._blurred_bg)

        # Draw Dim
        if self.dim_background:
            color = QColor(0, 0, 0)
            color.setAlphaF(self.dim_opacity)
            painter.fillRect(self.rect(), color)

    def mousePressEvent(self, event):
        if self.is_modal and self.close_on_click_outside:
            local_pos = event.position().toPoint()
            if not self.content_wrapper.geometry().contains(local_pos):
                self.hide()
                return
        super().mousePressEvent(event)

    def eventFilter(self, obj, event):
        # Resize Logic
        if obj == self.parent() and event.type() == QEvent.Type.Resize:
            if self.is_modal:
                self.resize(obj.size())
                self.move(0, 0)

                # Saat resize terjadi, hapus blur lama untuk mencegah
                # gambar yang terdistorsi/ghosting
                self._blurred_bg = None
                self.update()  # Akan menampilkan background dimming polos sementara

                # Trigger capture baru setelah resize selesai (debounce)
                self._resize_timer.start()

            self._update_position()
            return False

        # Global Click Logic (Non-Modal only)
        if not self.is_modal and self.close_on_click_outside and self.isVisible():
            if event.type() == QEvent.Type.MouseButtonPress:
                global_pos = (
                    event.globalPosition().toPoint()
                    if hasattr(event, "globalPosition")
                    else event.globalPos()
                )
                parent_widget = self.parent()
                if isinstance(parent_widget, QWidget):
                    local_pos = parent_widget.mapFromGlobal(global_pos)
                    if not self.geometry().contains(local_pos):
                        self.hide()
                        return False

        return super().eventFilter(obj, event)

    def _update_position(self):
        parent = self.parent()
        if not parent or not isinstance(parent, QWidget):
            return

        parent_rect = parent.rect()
        target = self.content_wrapper if self.is_modal else self

        width = target.width()
        height = target.height()

        pos = self._calculate_coordinates(
            self.preferred_position, parent_rect, width, height
        )

        if self.smart_positioning and not self.is_modal:
            pos = self._adjust_position_smartly(pos, width, height, parent_rect)

        target.move(pos)

        if not self.is_modal:
            self.raise_()

    def _calculate_coordinates(self, position_enum, p_rect, w, h):
        m = self.margin
        x, y = 0, 0
        if position_enum in [
            OverlayPosition.TOP_LEFT,
            OverlayPosition.BOTTOM_LEFT,
            OverlayPosition.LEFT_CENTER,
        ]:
            x = m
        elif position_enum in [
            OverlayPosition.TOP_RIGHT,
            OverlayPosition.BOTTOM_RIGHT,
            OverlayPosition.RIGHT_CENTER,
        ]:
            x = p_rect.width() - w - m
        else:
            x = (p_rect.width() - w) // 2

        if position_enum in [
            OverlayPosition.TOP_LEFT,
            OverlayPosition.TOP_CENTER,
            OverlayPosition.TOP_RIGHT,
        ]:
            y = m
        elif position_enum in [
            OverlayPosition.BOTTOM_LEFT,
            OverlayPosition.BOTTOM_CENTER,
            OverlayPosition.BOTTOM_RIGHT,
        ]:
            y = p_rect.height() - h - m
        else:
            y = (p_rect.height() - h) // 2
        return QPoint(x, y)

    def _adjust_position_smartly(self, natural_pos: QPoint, w, h, p_rect: QRect):
        final_x = max(0, min(natural_pos.x(), p_rect.width() - w))
        final_y = max(0, min(natural_pos.y(), p_rect.height() - h))
        return QPoint(final_x, final_y)
