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
from PySide6.QtCore import Qt, QEvent, QPoint, QRect, QTimer, QSize


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
        dim_opacity=0.5,
        blur_background=False,
        blur_radius=10,  # Default radius ditingkatkan agar lebih soft
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

        self._is_capturing = False  # Re-entrancy guard

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

        self._bg_pixmap = None

        # Timer untuk menghandle resize agar tidak spam grab()
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(100)  # Delay 100ms setelah resize selesai
        self._resize_timer.timeout.connect(self._capture_blur)

        if parent:
            self.setParent(parent)
            parent.installEventFilter(self)
            self.content_wrapper.installEventFilter(self)  # Listen to content resize
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

    def setVisible(self, visible):
        """
        Zero-flicker capture: Grab background BEFORE becoming visible.
        """
        if visible and not self.isVisible():
            self._update_position()
            if self.is_modal and self.blur_background:
                self._create_blurred_snapshot()

        super().setVisible(visible)

    def showEvent(self, event):
        self._update_position()
        self.raise_()

        if self.close_on_click_outside and not self.is_modal:
            window = self.window()
            if window:
                window.installEventFilter(self)

        super().showEvent(event)

    def _capture_blur(self):
        """
        Triggered primarily by parent resize events.
        """
        if self._is_capturing:
            return

        self._is_capturing = True
        was_visible = self.isVisible()

        # If already visible, hide to capture what's behind
        if was_visible:
            self.hide()
            QApplication.processEvents()

        try:
            self._create_blurred_snapshot()
        except Exception as e:
            print(f"Snapshot update failed: {e}")
        finally:
            if was_visible:
                self.show()
            self._is_capturing = False
            self.update()

    def _create_blurred_snapshot(self):
        """
        Sequence: Snapshot -> Downscale -> Gaussian Blur (Smoothing)
        """
        parent = self.parent()
        if not parent or not isinstance(parent, QWidget):
            return

        try:
            # 1. Snapshot
            full_pixmap = parent.grab()

            # 2. Downscale (Factor 4)
            # FastTransformation is used; Gaussian blur will smooth the results.
            scaled = full_pixmap.scaled(
                full_pixmap.width() // 4,
                full_pixmap.height() // 4,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )

            # 3. Gaussian Blur (Smoothing)
            if self.blur_radius > 0:
                self._bg_pixmap = self._apply_gaussian_blur(scaled, self.blur_radius)
            else:
                self._bg_pixmap = scaled
        except Exception as e:
            print(f"Failed to create blurred snapshot: {e}")

    def _apply_gaussian_blur(self, pixmap, radius):
        """
        Applies a high-quality Gaussian blur with padding to avoid edge artifacts.
        """
        if pixmap.isNull():
            return pixmap

        # Increase padding to allow the blur to "bleed" out, then crop it.
        # This prevents the "fade-to-transparent" effect at the edges.
        padding = int(radius * 1.5)

        # 1. Create expanded pixmap
        expanded_size = QSize(
            pixmap.width() + padding * 2, pixmap.height() + padding * 2
        )
        expanded_pixmap = QPixmap(expanded_size)
        expanded_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(expanded_pixmap)
        # Draw the original pixmap stretched slightly to fill the padding area.
        # This provides "fake" border pixels for the blur to work with.
        painter.drawPixmap(expanded_pixmap.rect(), pixmap)
        painter.end()

        # 2. Apply Blur Effect in a Scene
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(expanded_pixmap)

        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(radius)
        blur.setBlurHints(QGraphicsBlurEffect.BlurHint.PerformanceHint)
        item.setGraphicsEffect(blur)

        scene.addItem(item)

        # 3. Render back to pixmap
        blurred_expanded = QPixmap(expanded_size)
        blurred_expanded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(blurred_expanded)
        scene.render(painter)
        painter.end()

        # 4. Crop back to original size
        return blurred_expanded.copy(padding, padding, pixmap.width(), pixmap.height())

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
        try:
            # Draw Blurred BG
            if self.blur_background and self._bg_pixmap:
                painter.drawPixmap(self.rect(), self._bg_pixmap)

            # Draw Dim
            if self.dim_background:
                color = QColor(0, 0, 0)
                color.setAlphaF(self.dim_opacity)
                painter.fillRect(self.rect(), color)
        finally:
            painter.end()

    def mousePressEvent(self, event):
        if self.is_modal and self.close_on_click_outside:
            # Check what widget is under the mouse
            pos = event.position().toPoint()
            child = self.childAt(pos)

            # If we clicked on content_wrapper or any of its descendants, don't hide
            if child and (
                child == self.content_wrapper
                or self.content_wrapper.isAncestorOf(child)
            ):
                super().mousePressEvent(event)
                return

            # Otherwise, hide (clicked on background/dim area)
            self.hide()
            return
        super().mousePressEvent(event)

    def eventFilter(self, obj, event):
        # 1. Parent Resize Logic
        if obj == self.parent() and event.type() == QEvent.Type.Resize:
            if self.is_modal:
                self.resize(obj.size())
                self.move(0, 0)
                # DO NOT clear _bg_pixmap here to avoid flickering.
                # The old pixmap will be stretched in paintEvent until the new one is captured.
                self.update()
                self._resize_timer.start()

            self._update_position()
            return False

        # 2. Content Wrapper Resize Logic (Recentering)
        if obj == self.content_wrapper and event.type() == QEvent.Type.Resize:
            # If content size changed (e.g. Accordion expanded), we need to update our position
            # to remain centered or correctly aligned.
            QTimer.singleShot(0, self._update_position)
            return False

        # 3. Global Click Logic (Non-Modal only)
        if not self.is_modal and self.close_on_click_outside and self.isVisible():
            if event.type() == QEvent.Type.MouseButtonPress:
                # Use widgetAt for much more robust hit detection
                global_pos = (
                    event.globalPosition().toPoint()
                    if hasattr(event, "globalPosition")
                    else event.globalPos()
                )

                clicked_widget = QApplication.widgetAt(global_pos)

                # If we clicked outside the overlay entirely
                if (
                    clicked_widget
                    and not self.isAncestorOf(clicked_widget)
                    and clicked_widget != self
                ):
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

    def to_qml(self, indent=0):
        tab = "    " * indent
        # position, margin, smart_positioning, close_on_click_outside:
        # blur_background, blur_radius, shadow_enabled, shadow_blur_radius, shadow_color, shadow_offset:
        qml = f"{tab}Popup {{\n"
        qml += f"{tab}    modal: {str(self.is_modal).lower()}\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    height: parent.height\n"
        qml += f"{tab}    background: Rectangle {{\n"
        if self.dim_background:
            qml += f"{tab}        color: '#{int(self.dim_opacity * 255):02x}000000'\n"
        else:
            qml += f"{tab}        color: 'transparent'\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}    Rectangle {{\n"
        qml += f"{tab}        anchors.centerIn: parent\n"
        qml += f"{tab}        width: childrenRect.width\n"
        qml += f"{tab}        height: childrenRect.height\n"
        qml += f"{tab}        color: 'transparent'\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml
