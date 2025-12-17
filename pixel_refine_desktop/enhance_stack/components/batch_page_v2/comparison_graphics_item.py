from PySide6.QtWidgets import QGraphicsObject
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QImage, QPixmap, QColor, QPen, QBrush


class ComparisonGraphicsItem(QGraphicsObject):
    """
    Graphics Item untuk membandingkan dua gambar dengan slider.
    Dapat dimasukkan ke dalam QGraphicsScene sehingga mendukung Zoomable View.
    """

    def __init__(self, before_pixmap, after_pixmap, parent=None):
        super().__init__(parent)
        self.before_pixmap = before_pixmap  # Original (Full visibility on Right)
        self.after_pixmap = after_pixmap  # Processed (Clipped visibility on Left)

        # Slider position (0.0 - 1.0)
        self.slider_pos = 0.5
        self.is_dragging = False

        # Cache rect
        self.width = max(self.before_pixmap.width(), self.after_pixmap.width())
        self.height = max(self.before_pixmap.height(), self.after_pixmap.height())

        self.setAcceptHoverEvents(True)
        # Penting: Item harus selectable/movable jika ingin menangkap mouse event secara eksklusif,
        # tapi di sini kita handle mouse press manual.

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        # 0. Calculate Scale Factors
        # Transform maps Scene -> Viewport
        transform = painter.worldTransform()
        # Scale for UI elements (fixed size on screen)
        # levelOfDetail is approx scale factor (zoom level)
        lod = option.levelOfDetailFromTransform(transform)
        if lod <= 0:
            lod = 1.0
        adaptive_scale = 1.0 / lod

        # 1. Draw Processed (Background/Right side) - SWAPPED
        # Previously Original was background. Now Processed is background (visible on right).
        painter.drawPixmap(0, 0, self.after_pixmap)

        # 2. Draw Original (Foreground/Left side) - SWAPPED
        # We crop the Original to show on the left side
        split_x = int(self.width * self.slider_pos)

        if split_x > 0:
            painter.drawPixmap(0, 0, self.before_pixmap, 0, 0, split_x, self.height)

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
        # We need the visible rect in Scene Coordinates
        visible_rect = self.boundingRect()  # Default to full size

        if widget:
            # Calculate visible rect from viewport
            viewport = widget.parent() if widget.parent() else widget
            # Note: widget passed to paint is usually the viewport widget
            # We map viewport rect (0,0, w, h) to Scene coords

            # More robust: use the transform inverted
            inv_transform, invertable = transform.inverted()
            if invertable:
                viewport_rect = widget.rect()
                # Map viewport rect to scene
                scene_viewport_rect = inv_transform.mapRect(QRectF(viewport_rect))
                # Intersect with item bounds to clamp
                visible_rect = scene_viewport_rect.intersected(self.boundingRect())

        font = painter.font()
        font.setPointSizeF(14 * adaptive_scale)
        font.setBold(True)
        painter.setFont(font)

        # Helper to draw text with background
        def draw_label(text, x, y, align_right=False):
            metrics = painter.fontMetrics()

            padding = 10 * adaptive_scale

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
            border_radius = 4 * adaptive_scale
            painter.drawRoundedRect(rect, border_radius, border_radius)

            # Text
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

        # Margin from viewport edges
        margin = 20 * adaptive_scale
        top_y = visible_rect.top() + margin

        # Ensure y is within bounds (e.g. if scrolled way past, though visible_rect handles intersection)
        top_y = max(top_y, 0 + margin)

        # Draw Labels - SWAPPED

        # Left Side = "Asli" (Original)
        left_label_x = visible_rect.left() + margin

        # Constraint: Must be strictly inside the 'Processed' region (0 to split_x)
        # And allow some clearance for the label width?
        # Let's just say if the anchor point is left of split_x
        if left_label_x < (split_x - 10 * adaptive_scale):
            draw_label("Asli", left_label_x, top_y)

        # Right Side = "Diproses" (Processed)
        right_label_x = visible_rect.right() - margin

        if right_label_x > (split_x + 10 * adaptive_scale):
            draw_label("Diproses", right_label_x, top_y, align_right=True)

    def mousePressEvent(self, event):
        # Cek apakah klik dekat garis slider?
        # Karena kita ingin membedakan antara Pan (Geser Canvas) dan Slide (Geser Garis).
        # Logika: Jika kursor dekat garis (+- 20px), kita ambil alih event.
        # Jika tidak, kita ignore() supaya diteruskan ke View (untuk Panning).

        pos = event.pos()
        split_x = self.width * self.slider_pos

        if abs(pos.x() - split_x) < 30:  # Tolerance 30px
            self.is_dragging = True
            event.accept()  # Kita 'makan' event ini
        else:
            event.ignore()  # Biarkan View menangani (Panning)

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            pos = event.pos()
            # Normalize 0.0 - 1.0
            new_pos = pos.x() / self.width
            self.slider_pos = max(0.0, min(1.0, new_pos))
            self.update()  # Redraw
            event.accept()
        else:
            # Hover logic: Ubah kursor jika dekat garis
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
