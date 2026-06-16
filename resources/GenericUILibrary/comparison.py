from typing import Optional
from PySide6.QtWidgets import (
    QGraphicsObject,
    QStyleOptionGraphicsItem,
    QWidget,
)
from PySide6.QtCore import Qt, QRectF, QPointF, QRect
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen, QBrush


class ImageCompareItem(QGraphicsObject):
    """
    Graphics Item untuk membandingkan dua gambar dengan slider.
    Dapat dimasukkan ke dalam QGraphicsScene sehingga mendukung Zoomable View.
    """

    def __init__(
        self,
        left_pixmap,
        right_pixmap,
        left_label="Original",
        right_label="Processed",
        parent=None,
    ):
        super().__init__(parent)
        self.left_pixmap = left_pixmap
        self.right_pixmap = right_pixmap
        self.left_label = left_label
        self.right_label = right_label

        # Slider position (0.0 - 1.0)
        self.slider_pos = 0.5
        self.is_dragging = False

        # Cache rect
        self.width = max(self.left_pixmap.width(), self.right_pixmap.width())
        self.height = max(self.left_pixmap.height(), self.right_pixmap.height())

        self.setAcceptHoverEvents(True)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        # 0. Calculate Scale Factors
        transform = painter.worldTransform()
        lod = option.levelOfDetailFromTransform(transform)
        if lod <= 0:
            lod = 1.0
        adaptive_scale = 1.0 / lod

        # 1. Background Layer (Visible on Right side)
        painter.drawPixmap(0, 0, self.right_pixmap)

        # 2. Foreground Layer (Clipped to Left side)
        split_x = int(self.width * self.slider_pos)

        if split_x > 0:
            painter.drawPixmap(0, 0, self.left_pixmap, 0, 0, split_x, self.height)

        # 3. Draw Slider Line
        pen = QPen(QColor(255, 255, 255, 200))
        pen.setWidthF(2.0 * adaptive_scale)
        painter.setPen(pen)
        painter.drawLine(split_x, 0, split_x, self.height)

        # 4. Draw Handler Circle
        radius = 6.0 * adaptive_scale
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(split_x, self.height / 2), radius, radius)

        # 5. Draw Labels (Sticky / Floating)
        visible_rect = self.boundingRect()

        if widget:
            viewport = widget.parent() if widget.parent() else widget
            inv_transform, invertable = transform.inverted()
            if invertable:
                viewport_rect = widget.rect()
                scene_viewport_rect = inv_transform.mapRect(QRectF(viewport_rect))
                visible_rect = scene_viewport_rect.intersected(self.boundingRect())

        font = painter.font()
        # Initial target size
        target_point_size = 14 * adaptive_scale

        # --- ADAPTIVE SIZING FIX ---
        # Ensure labels don't overwhelm the visible area (or image scaling)
        # We calculate limits in item space
        max_h = visible_rect.height() * 0.10  # Max 15% of visible height
        max_w = visible_rect.width() * 0.20  # Max 35% of visible width per label

        # Estimate heights
        # 1 point ~= 1.333 pixels (approx, depends on DPI but good enough for relative limit)
        # Using simple heuristic: line height ~ 1.5 * point_size
        estimated_line_height = target_point_size * 1.5

        scale_factor = 1.0
        if estimated_line_height > max_h:
            scale_factor = max_h / estimated_line_height

        final_point_size = target_point_size * scale_factor

        # Check width roughly (assuming average char width is 0.6 * point size)
        # "Processed" is roughly 9 chars.
        estimated_width = 9 * (final_point_size * 0.6)
        if estimated_width > max_w:
            width_scale = max_w / estimated_width
            final_point_size *= width_scale

        # Minimum readability clamp relative to adaptive scale won't help if we specifically want to shrink
        # But let's prevent it from disappearing completely?
        # User asked for it to shrink, so we let it shrink.

        font.setPointSizeF(final_point_size)
        font.setBold(True)
        painter.setFont(font)

        # Helper to draw text with background
        def draw_label(text, x, y, align_right=False):
            metrics = painter.fontMetrics()
            padding = 10 * adaptive_scale * scale_factor  # Scale padding too
            if padding < 2:
                padding = 2  # Min padding

            text_w = metrics.horizontalAdvance(text)
            text_h = metrics.height()

            w = text_w + (padding * 2)
            h = text_h + (padding)

            if align_right:
                rect_x = x - w
            else:
                rect_x = x

            rect = QRectF(rect_x, y, w, h)

            # Background
            painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
            painter.setPen(Qt.PenStyle.NoPen)
            border_radius = 4 * adaptive_scale * scale_factor
            painter.drawRoundedRect(rect, border_radius, border_radius)

            # Text
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

        # Margin from viewport edges
        margin = 20 * adaptive_scale * scale_factor  # Scale margin too
        if margin < 5:
            margin = 5

        top_y = visible_rect.top() + margin
        top_y = max(top_y, 0 + margin)

        # Left Side Label
        left_label_x = visible_rect.left() + margin
        if left_label_x < (split_x - 10 * adaptive_scale * scale_factor):
            draw_label(self.left_label, left_label_x, top_y)

        # Right Side Label
        right_label_x = visible_rect.right() - margin
        if right_label_x > (split_x + 10 * adaptive_scale * scale_factor):
            draw_label(self.right_label, right_label_x, top_y, align_right=True)

    def mousePressEvent(self, event):
        pos = event.pos()
        split_x = self.width * self.slider_pos

        if abs(pos.x() - split_x) < 30:  # Tolerance 30px
            self.is_dragging = True
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            pos = event.pos()
            new_pos = pos.x() / self.width
            self.slider_pos = max(0.0, min(1.0, new_pos))
            self.update()
            event.accept()
        else:
            pos = event.pos()
            split_x = self.width * self.slider_pos
            if abs(pos.x() - split_x) < 30:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            event.ignore()

    def mouseReleaseEvent(self, event):
        if self.is_dragging:
            self.is_dragging = False
            event.accept()
        else:
            event.ignore()

    def to_qml(self, indent=0):
        tab = "    " * indent
        # left_pixmap, right_pixmap:
        _ = getattr(self, "left_pixmap", None)
        _ = getattr(self, "right_pixmap", None)
        qml = f"{tab}Item {{\n"
        qml += f"{tab}    width: {self.width}\n"
        qml += f"{tab}    height: {self.height}\n"
        qml += f"{tab}    property real sliderPos: {self.slider_pos}\n"
        qml += f"{tab}    Image {{ source: ''; anchors.fill: parent; fillMode: Image.PreserveAspectFit }}\n"
        qml += f"{tab}    Item {{\n"
        qml += f"{tab}        clip: true\n"
        qml += f"{tab}        width: parent.width * sliderPos\n"
        qml += f"{tab}        height: parent.height\n"
        qml += f"{tab}        Image {{ source: ''; width: parent.parent.width; height: parent.parent.height; fillMode: Image.PreserveAspectFit }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}    Rectangle {{ x: parent.width * sliderPos - 1; width: 2; height: parent.height; color: 'white' }}\n"
        qml += f"{tab}    Text {{ text: '{self.left_label}'; x: 15; y: 15; color: 'white'; font.bold: true }}\n"
        qml += f"{tab}    Text {{ text: '{self.right_label}'; x: parent.width - width - 15; y: 15; color: 'white'; font.bold: true }}\n"
        qml += f"{tab}    MouseArea {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        onPositionChanged: parent.sliderPos = Math.max(0, Math.min(1, mouseX / parent.width))\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml


class ImageCompareWidget(QWidget):
    """
    Widget mandiri (stand-alone) untuk membandingkan dua gambar dengan slider.
    Gunakan ini jika Anda ingin meletakkannya langsung di layout (bukan di QGraphicsView).
    """

    def __init__(
        self,
        left_pixmap: Optional[QPixmap] = None,
        right_pixmap: Optional[QPixmap] = None,
        left_label="Original",
        right_label="Processed",
        parent=None,
    ):
        super().__init__(parent)
        self.left_pixmap = left_pixmap
        self.right_pixmap = right_pixmap
        self.left_label = left_label
        self.right_label = right_label

        self.slider_pos = 0.5
        self.is_dragging = False
        self.setMouseTracking(True)

    def set_images(self, left_pixmap: QPixmap, right_pixmap: QPixmap):
        """Update gambar secara dinamis."""
        self.left_pixmap = left_pixmap
        self.right_pixmap = right_pixmap
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.left_pixmap or not self.right_pixmap:
            painter.fillRect(self.rect(), QColor("#1A1A1A"))
            painter.setPen(QColor("#888888"))
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter, "No images loaded"
            )
            return

        # 1. Calculate aspect ratio fit
        rect = self.rect()
        w, h = rect.width(), rect.height()
        img_w, img_h = self.left_pixmap.width(), self.left_pixmap.height()

        scale = min(w / img_w, h / img_h)
        draw_w = int(img_w * scale)
        draw_h = int(img_h * scale)
        draw_x = (w - draw_w) // 2
        draw_y = (h - draw_h) // 2

        draw_rect = QRect(draw_x, draw_y, draw_w, draw_h)
        split_x = int(draw_x + (draw_w * self.slider_pos))

        # 2. Draw Layers
        # Right Side (Background)
        painter.drawPixmap(draw_rect, self.right_pixmap)

        # Left Side (Clipped Foreground)
        clip_w = int(img_w * self.slider_pos)
        if clip_w > 0:
            src_rect = QRect(0, 0, clip_w, img_h)
            dst_rect = QRect(draw_x, draw_y, int(draw_w * self.slider_pos), draw_h)
            painter.drawPixmap(dst_rect, self.left_pixmap, src_rect)

        # 3. Draw UI (Slider Line & Handler)
        pen = QPen(QColor(255, 255, 255, 200))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(split_x, draw_y, split_x, draw_y + draw_h)

        handler_r = 6
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(split_x, draw_y + draw_h / 2), handler_r, handler_r)

        # 4. Draw Labels
        font = painter.font()
        font.setPointSizeF(12)
        font.setBold(True)
        painter.setFont(font)

        def draw_label(text, x, y, align_right=False):
            metrics = painter.fontMetrics()
            padding = 8
            text_w = metrics.horizontalAdvance(text)
            text_h = metrics.height()
            w_total = text_w + (padding * 2)
            h_total = text_h + padding

            rx = x - w_total if align_right else x
            l_rect = QRectF(rx, y, w_total, h_total)

            painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(l_rect, 4, 4)

            painter.setPen(QColor(255, 255, 255))
            painter.drawText(l_rect, Qt.AlignmentFlag.AlignCenter, text)

        margin = 15
        label_y = draw_y + margin

        # Left Label
        if split_x > draw_x + margin + 40:
            draw_label(self.left_label, draw_x + margin, label_y)

        # Right Label
        if split_x < draw_x + draw_w - margin - 40:
            draw_label(
                self.right_label, draw_x + draw_w - margin, label_y, align_right=True
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self._update_slider(event.position().x())

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self._update_slider(event.position().x())
        else:
            # Update cursor if near slider
            # (Need to calculate width again or store it)
            pass

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    def _update_slider(self, mouse_x):
        if not self.left_pixmap:
            return

        rect = self.rect()
        img_w, img_h = self.left_pixmap.width(), self.left_pixmap.height()
        scale = min(rect.width() / img_w, rect.height() / img_h)
        draw_w = int(img_w * scale)
        draw_x = (rect.width() - draw_w) // 2

        local_x = mouse_x - draw_x
        pos = local_x / draw_w
        self.slider_pos = max(0.0, min(1.0, pos))
        self.update()

    def to_qml(self, indent=0):
        tab = "    " * indent
        # left_pixmap, right_pixmap:
        _ = getattr(self, "left_pixmap", None)
        _ = getattr(self, "right_pixmap", None)
        qml = f"{tab}Item {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    height: parent.height\n"
        qml += f"{tab}    property real sliderPos: {self.slider_pos}\n"
        qml += f"{tab}    Image {{ source: ''; anchors.fill: parent; fillMode: Image.PreserveAspectFit }}\n"
        qml += f"{tab}    Item {{\n"
        qml += f"{tab}        clip: true\n"
        qml += f"{tab}        width: parent.width * sliderPos\n"
        qml += f"{tab}        height: parent.height\n"
        qml += f"{tab}        Image {{ source: ''; width: parent.parent.width; height: parent.parent.height; fillMode: Image.PreserveAspectFit }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}    Rectangle {{ x: parent.width * sliderPos - 1; width: 2; height: parent.height; color: 'white' }}\n"
        qml += f"{tab}    Text {{ text: '{self.left_label}'; x: 15; y: 15; color: 'white'; font.bold: true }}\n"
        qml += f"{tab}    Text {{ text: '{self.right_label}'; x: parent.width - width - 15; y: 15; color: 'white'; font.bold: true }}\n"
        qml += f"{tab}    MouseArea {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        onPositionChanged: parent.sliderPos = Math.max(0, Math.min(1, mouseX / parent.width))\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml
