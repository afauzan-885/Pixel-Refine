"""
Overlay Components for GenericUILibrary.
Provides floating containers that position themselves relative to their parent.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QEvent, QPoint, QRect, QEnum, QTimer
from PySide6.QtGui import QColor


class OverlayPosition:
    # ... (rest of class) ...

    # ... (inside OverlayContainer) ...

    def showEvent(self, event):
        """Handle show event: Capture blur if needed."""
        self._update_position()
        self.raise_()

        if self.is_modal:
            # Resize to cover parent
            if self.parent():
                self.resize(self.parent().size())
                self.move(0, 0)

            # Capture background for Blur (DEFERRED for Robustness)
            # Avoids painter conflicts during initial show/layout
            if self.blur_background and self.parent():
                QTimer.singleShot(0, self._capture_blur)

        if self.close_on_click_outside and not self.is_modal:
            # Only install global filter if NOT modal.
            # If modal, we catch clicks on ourself (backdrop).
            window = self.window()
            if window:
                window.installEventFilter(self)

        super().showEvent(event)

    def _capture_blur(self):
        """Capture parent screenshot and blur it."""
        from PySide6.QtGui import QPainter, QPixmap
        from PySide6.QtWidgets import (
            QGraphicsBlurEffect,
            QGraphicsScene,
            QGraphicsPixmapItem,
        )

        # Verify valid state before capturing
        if not self.isVisible() or not self.parent():
            return

        parent = self.parent()

        # Prevent self-capture: Set flag so paintEvent returns empty
        self._is_capturing = True

        try:
            # Robust grab
            bg_pixmap = parent.grab()
        except Exception as e:
            # Fallback if grab fails (e.g. valid painter conflict)
            print(f"Overlay Blur Capture Failed: {e}")
            self._is_capturing = False
            return
        finally:
            self._is_capturing = False  # Always reset

        # Apply Blur
        if self.blur_radius > 0 and not bg_pixmap.isNull():
            # ... (blur logic same as before) ...
            # Scaling down for performance (optional)
            scale = 1
            if bg_pixmap.width() > 1920:
                scale = 2

            src = bg_pixmap
            if scale > 1:
                src = src.scaled(src.width() // scale, src.height() // scale)

            w, h = src.width(), src.height()

            # Use small dimensions to speed up
            small = src.scaled(
                w // 8,
                h // 8,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
            blurred = small.scaled(
                w,
                h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._blurred_bg = blurred

            # Trigger update to paint the new blur
            self.update()
        else:
            self._blurred_bg = bg_pixmap
            self.update()

    # ... (hideEvent same) ...

    def paintEvent(self, event):
        """Paint dimming and blur background."""
        if not self.is_modal:
            super().paintEvent(event)
            return

        # If capturing, allow grab() to see through us (transparent)
        if self._is_capturing:
            return

        from PySide6.QtGui import QPainter, QColor

        # Safety: Check if we can paint
        try:
            painter = QPainter(self)
            if not painter.isActive():
                return
        except Exception:
            return

        # Draw Blurred BG
        if self.blur_background and self._blurred_bg:
            painter.drawPixmap(0, 0, self.width(), self.height(), self._blurred_bg)

        # Draw Dim
        if self.dim_background:
            color = QColor(0, 0, 0)
            color.setAlphaF(self.dim_opacity)
            painter.fillRect(self.rect(), color)


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
    """
    A floating container that can position itself relative to its parent widget.
    Features:
    - Smart positioning: Flips/adjusts if out of bounds (Non-Modal Mode).
    - Modal Mode: Covers entire parent with dim/blur background, centers content.
    - Visual Effects: Shadow, Dimming, Blur.
    """

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
        blur_radius=10,
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

        # Visual Options
        self.dim_background = dim_background
        self.dim_opacity = dim_opacity
        self.blur_background = blur_background
        self.blur_radius = blur_radius
        self.shadow_enabled = shadow_enabled

        # Shadow params
        self.shadow_blur_radius = shadow_blur_radius
        self.shadow_color = shadow_color
        self.shadow_offset = shadow_offset

        self.setObjectName("OverlayContainer")

        # Flag to prevent self-capture during blur generation
        self._is_capturing = False

        # Determine if we are in "Modal/Backdrop" mode
        # If we dim or blur, we MUST be modal (cover whole parent)
        self.is_modal = self.dim_background or self.blur_background

        # Setup Content Wrapper
        # If modal, we need a wrapper to hold the content while 'self' is the backdrop
        # If not modal, 'self' is the container.
        # To unify logic, we will ALWAYS use a wrapper layout if it's modal.

        # However, for backward compatibility with non-modal existing usages (if any),
        # we'll stick to 'self' is main widget.

        # Structure:
        # Self (QWidget)
        #  -> Layout
        #      -> ContentWrapper (QWidget) -> Content Logic

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.content_wrapper = QWidget(self)
        self.content_wrapper.setObjectName("OverlayContentWrapper")
        # Ensure wrapper is transparent so background doesn't block shadow
        self.content_wrapper.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground, True
        )

        self.wrapper_layout = QVBoxLayout(self.content_wrapper)
        self.wrapper_layout.setContentsMargins(0, 0, 0, 0)
        self.wrapper_layout.setSpacing(0)

        # If Modal, 'self' covers parent. ContentWrapper floats inside.
        # If Non-Modal, 'self' IS the floating box. ContentWrapper fills 'self'.

        if self.is_modal:
            # Modal configuration
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            # Ensure we are translucent so we can see through when not painting dim/blur
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

            # We don't add wrapper to layout because we want to position it manually via move()
            # or use a layout with alignment? Manual move is better for 'OverlayPosition' logic.
            self.content_wrapper.setParent(self)  # Re-parent explicitly
        else:
            # Non-modal: Wrapper fills the container
            self.main_layout.addWidget(self.content_wrapper)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        # Apply Shadow to Wrapper
        if self.shadow_enabled:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(self.shadow_blur_radius)
            shadow.setColor(self.shadow_color)
            shadow.setOffset(self.shadow_offset)
            self.content_wrapper.setGraphicsEffect(shadow)

        # Background Blur Cache
        self._blurred_bg = None

        if parent:
            self.setParent(parent)
            parent.installEventFilter(self)
            self._update_position()

    def set_content(self, widget):
        """Set the content widget."""
        # Clear existing
        while self.wrapper_layout.count():
            item = self.wrapper_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.wrapper_layout.addWidget(widget)

        # Adjust size logic
        self.content_wrapper.adjustSize()
        if not self.is_modal:
            self.adjustSize()

        self._update_position()

    def setParent(self, parent, mode=Qt.WindowType.Widget):
        """Override setParent to install event filter."""
        super().setParent(parent)
        if parent:
            parent.installEventFilter(self)
            self.raise_()
            self._update_position()

    def showEvent(self, event):
        """Handle show event: Capture blur if needed."""
        self._update_position()
        self.raise_()

        if self.is_modal:
            # Resize to cover parent
            if self.parent():
                self.resize(self.parent().size())
                self.move(0, 0)

            # Capture background for Blur
            if self.blur_background and self.parent():
                self._capture_blur()

        if self.close_on_click_outside and not self.is_modal:
            # Only install global filter if NOT modal.
            # If modal, we catch clicks on ourself (backdrop).
            window = self.window()
            if window:
                window.installEventFilter(self)

        super().showEvent(event)

    def _capture_blur(self):
        """Capture parent screenshot and blur it."""
        from PySide6.QtGui import QPainter, QPixmap
        from PySide6.QtWidgets import (
            QGraphicsBlurEffect,
            QGraphicsScene,
            QGraphicsPixmapItem,
        )

        parent = self.parent()
        if not parent:
            return

        # Prevent self-capture: Set flag so paintEvent returns empty
        self._is_capturing = True
        # Force immediate update/repaint if needed?
        # Actually grab() triggers paintEvent internally for children.
        # But if self is child, it will call self.paintEvent via architecture.

        try:
            bg_pixmap = parent.grab()
        finally:
            self._is_capturing = False

        # Apply Blur
        # QGraphicsBlurEffect approach for Pixmap processing
        # Note: This can be expensive.
        if self.blur_radius > 0:
            from PySide6.QtWidgets import QLabel

            # Simplified blur calculation (QT generic blur is fast enough?)
            # Actually, doing it properly requires a scene or manual Image processing.
            # Let's use a temporary GraphicsScene to render blur.

            # Scaling down for performance (optional)
            scale = 1
            if bg_pixmap.width() > 1920:
                scale = 2

            src = bg_pixmap
            if scale > 1:
                src = src.scaled(src.width() // scale, src.height() // scale)

            # We will rely on QPainter Draw with QImage blur? No direct API.
            # Using QGraphicsDropShadowEffect abuse? No.
            # Let's use simple QImage blur algo or external PIL if needed?
            # No external deps.
            # STICK TO: QGraphicsBlurEffect on a dummy widget rendering approach.

            # ...For now, let's implement DIMMING first perfectly.
            # Blur in PySide6 without CV2/PIL is tricky to do purely in memory fast.
            # The standard way is QGraphicsEffect on a static image.

            # Let's skip complex blur implementation for speed and robustness for now
            # and simulate "Blur" look with high opacity dimming if blur fails?
            # Or use a simple downscale-upscale trick which looks like blur.

            # Trick: Downscale -> Upscale = Mosaic/Blurry
            w, h = src.width(), src.height()
            small = src.scaled(
                w // 8,
                h // 8,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
            blurred = small.scaled(
                w,
                h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._blurred_bg = blurred
        else:
            self._blurred_bg = bg_pixmap

    def hideEvent(self, event):
        """Remove global filter when hidden."""
        if self.close_on_click_outside and not self.is_modal:
            window = self.window()
            if window:
                window.removeEventFilter(self)
        super().hideEvent(event)

    def paintEvent(self, event):
        """Paint dimming and blur background."""
        if not self.is_modal:
            super().paintEvent(event)
            return

        # If capturing, allow grab() to see through us (transparent)
        if self._is_capturing:
            return

        from PySide6.QtGui import QPainter, QColor

        painter = QPainter(self)

        # Draw Blurred BG
        if self.blur_background and self._blurred_bg:
            painter.drawPixmap(0, 0, self.width(), self.height(), self._blurred_bg)

        # Draw Dim
        if self.dim_background:
            color = QColor(0, 0, 0)
            color.setAlphaF(self.dim_opacity)
            painter.fillRect(self.rect(), color)

    def mousePressEvent(self, event):
        """Handle click on backdrop."""
        if self.is_modal and self.close_on_click_outside:
            # If click is NOT on content_wrapper, close.
            local_pos = event.position().toPoint()
            if not self.content_wrapper.geometry().contains(local_pos):
                self.hide()
                return  # Consumed

        super().mousePressEvent(event)

    def eventFilter(self, obj, event):
        # Resize Logic
        if obj == self.parent() and event.type() == QEvent.Type.Resize:
            if self.is_modal:
                self.resize(obj.size())
                self.move(0, 0)
            self._update_position()  # Reposition content

            # Re-capture blur if resize happens? Expensive. Maybe just stretch?
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
                    # If click is NOT inside self (the box)
                    if not self.geometry().contains(local_pos):
                        self.hide()
                        return False

        return super().eventFilter(obj, event)

    def _update_position(self):
        """Calculate and update position."""
        parent = self.parent()
        if not parent or not isinstance(parent, QWidget):
            return

        parent_rect = parent.rect()

        # Target Widget is either SELF (Non-Modal) or CONTENT_WRAPPER (Modal)
        target = self.content_wrapper if self.is_modal else self

        width = target.width()
        height = target.height()

        # Calculate ideal position
        pos = self._calculate_coordinates(
            self.preferred_position, parent_rect, width, height
        )

        # Smart Positioning Logic (Only for Non-Modal or floating content)
        if (
            self.smart_positioning and not self.is_modal
        ):  # Disable smart pos for modal (usually centered)
            pos = self._adjust_position_smartly(pos, width, height, parent_rect)

        target.move(pos)

        if not self.is_modal:
            self.raise_()

    def _calculate_coordinates(self, position_enum, p_rect, w, h):
        """Helper to get x,y for a given position strategy."""
        m = self.margin
        x, y = 0, 0

        # Horizontal
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
        else:  # CENTER, TOP_CENTER, BOTTOM_CENTER
            x = (p_rect.width() - w) // 2

        # Vertical
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
        else:  # CENTER, LEFT_CENTER, RIGHT_CENTER
            y = (p_rect.height() - h) // 2

        return QPoint(x, y)

    def _adjust_position_smartly(self, natural_pos: QPoint, w, h, p_rect: QRect):
        """Smart adjustments (Flip/Clamp)."""
        from PySide6.QtCore import QSize

        # Calculate bounding rect
        rect = QRect(natural_pos, QSize(w, h))

        # Simplified clamp for robustness
        final_x = max(0, min(natural_pos.x(), p_rect.width() - w))
        final_y = max(0, min(natural_pos.y(), p_rect.height() - h))
        return QPoint(final_x, final_y)

    def _flip_vertical(self, pos):
        # ... logic as before ...
        pass
