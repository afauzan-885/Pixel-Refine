"""
Camera Preview Widget - KISS Display
====================================
Widget sederhana untuk menampilkan frame kamera dari Taichi Pipeline.

KISS Principle:
  - QLabel-based (paling ringan di PySide6)
  - Update via update_frame(ndarray)
  - Auto-scale ke ukuran widget
  - FPS overlay optional
"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt


class CameraPreviewWidget(QWidget):
    """
    Widget untuk menampilkan frame kamera secara real-time.

    Usage:
        widget = CameraPreviewWidget()
        widget.show()

        # Dari bridge atau timer:
        widget.update_frame(numpy_array_uint8)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Image display
        self._image_label = QLabel(self)
        self._image_label.setAlignment(Qt.AlignCenter)
        self._image_label.setMinimumSize(320, 240)
        self._image_label.setText("Camera Preview")
        self._image_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #666666;
                font-size: 14px;
                border: 1px solid #333333;
            }
        """)
        layout.addWidget(self._image_label)

        # FPS overlay
        self._show_fps = True
        self._fps_text = ""
        self._last_frame = None

    def update_frame(self, frame_uint8):
        """
        Update display dengan frame baru.

        Args:
            frame_uint8: NumPy array (H, W, 3) uint8 RGB
        """
        if frame_uint8 is None:
            return

        self._last_frame = frame_uint8

        h, w, ch = frame_uint8.shape
        bytes_per_line = ch * w

        # Create QImage from numpy array
        q_image = QImage(
            frame_uint8.data,
            w, h,
            bytes_per_line,
            QImage.Format_RGB888
        )

        # Convert to QPixmap and scale
        pixmap = QPixmap.fromImage(q_image)
        scaled = pixmap.scaled(
            self._image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Draw FPS overlay if enabled
        if self._show_fps and self._fps_text:
            painter = QPainter(scaled)
            painter.setPen(QColor(0, 255, 0))
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(10, 20, self._fps_text)
            painter.end()

        self._image_label.setPixmap(scaled)

    def set_fps(self, fps):
        """Set FPS text untuk overlay."""
        self._fps_text = f"FPS: {fps:.1f}"

    def set_show_fps(self, show):
        """Toggle FPS overlay."""
        self._show_fps = show

    def clear(self):
        """Clear display."""
        self._image_label.clear()
        self._image_label.setText("Camera Preview")
        self._last_frame = None
