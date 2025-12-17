from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QImage, QPixmap, QColor, QPen


class CompareWidget(QWidget):
    """
    Widget untuk membandingkan dua gambar dengan slider geser (Before/After).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.before_pixmap = None
        self.after_pixmap = None

        self.slider_pos = 0.5  # Posisi 0.0 sampai 1.0
        self.is_dragging = False
        self.setMouseTracking(True)

    def set_images(self, before_path, after_path):
        """Load images untuk comparison."""
        self.before_pixmap = QPixmap(before_path)
        self.after_pixmap = QPixmap(after_path)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        if not self.before_pixmap or not self.after_pixmap:
            painter.fillRect(self.rect(), QColor("#333333"))
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter, "No images loaded"
            )
            return

        rect = self.rect()
        width = rect.width()
        height = rect.height()

        # Calculate scaled dimensions to fit aspect ratio (Fit Center)
        img_w = self.before_pixmap.width()
        img_h = self.before_pixmap.height()

        # Scale logic
        scale = min(width / img_w, height / img_h)
        draw_w = int(img_w * scale)
        draw_h = int(img_h * scale)

        draw_x = (width - draw_w) // 2
        draw_y = (height - draw_h) // 2

        draw_rect = QRect(draw_x, draw_y, draw_w, draw_h)

        # Split point (x coordinate)
        split_x = int(draw_x + (draw_w * self.slider_pos))

        # Draw "After" (Processed) Image - FULL (Background)
        # Actually standard practice: Left is Before, Right is After OR vice versa.
        # User requested: "gambar asli akan tertumpuk di bawah gambar proses"
        # -> So Original is Background, Process is Foreground (clipped)?
        # Let's do: Left Side = Original, Right Side = Processed (or standard slider)
        # Let's implement standard "Reveal" slider.
        # Left of slider = Processed (New), Right of slider = Original (Old) ?
        # Usually "After" is the one being revealed.

        # Draw Original (Background) everywhere first? No, that's inefficient.

        # CLIP REGIONS
        # Region 1: Left (0 to split_x) -> show Original ? or Processed?
        # Let's say Slider moves from Left to Right.
        # Left side = Processed (The Result). Right side = Original.

        # 1. Draw Original (Before) on the RIGHT side of split
        # Crop source rect
        # We draw the FULL image but perform clipping via painter logic or manual rect calculation

        # Efficient way: Draw full Original, then draw Processed clipped?
        # Draw Original
        painter.drawPixmap(draw_rect, self.before_pixmap)

        # Draw Processed (After) clipped to LEFT side
        # Source Rect for crop
        # We want the LEFT part of the image, from 0 to (img_w * slider_pos)
        src_w_crop = int(img_w * self.slider_pos)
        if src_w_crop > 0:
            source_rect = QRect(0, 0, src_w_crop, img_h)
            # Dest Rect
            dest_w_crop = int(draw_w * self.slider_pos)
            dest_rect = QRect(draw_x, draw_y, dest_w_crop, draw_h)

            painter.drawPixmap(dest_rect, self.after_pixmap, source_rect)

        # Draw Slider Line
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawLine(split_x, draw_y, split_x, draw_y + draw_h)

        # Draw Header Labels (Optional)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        # Left Label (Processed)
        if self.slider_pos > 0.1:
            painter.drawText(draw_x + 10, draw_y + 20, "Processed")
        # Right Label (Original)
        if self.slider_pos < 0.9:
            painter.drawText(draw_x + draw_w - 60, draw_y + 20, "Original")

    def mouseMoveEvent(self, event):
        if self.before_pixmap:
            rect = self.rect()
            width = rect.width()

            # Calculate image rect to constrain slider
            img_w = self.before_pixmap.width()
            img_h = self.before_pixmap.height()
            scale = min(width / img_w, rect.height() / img_h)
            draw_w = int(img_w * scale)
            draw_x = (width - draw_w) // 2

            # Local X relative to image
            local_x = event.position().x() - draw_x

            # Normalized 0.0 - 1.0
            pos = local_x / draw_w
            self.slider_pos = max(0.0, min(1.0, pos))

            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
