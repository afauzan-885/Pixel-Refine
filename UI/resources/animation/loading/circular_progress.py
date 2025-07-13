import math
from PySide6.QtWidgets import (QWidget)
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt, QRectF

class CircularProgress(QWidget):
    """
    Widget kustom untuk menampilkan progress bar berbentuk lingkaran.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self.setMinimumSize(80, 80)

    def setValue(self, value: int):
        if 0 <= value <= 100:
            self._value = value
            self.update()

    def value(self) -> int:
        return self._value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        side = min(rect.width(), rect.height())
        draw_rect = QRectF(
            (rect.width() - side) / 2,
            (rect.height() - side) / 2,
            side,
            side
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 0)) 
        painter.drawEllipse(draw_rect)
        
        num_dots = 12
        dot_radius = side * 0.04  
        circle_radius = side / 2 - dot_radius * 2

        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(num_dots):
            angle_rad = math.radians(i * (360 / num_dots) - 90)
            center_x = draw_rect.center().x()
            center_y = draw_rect.center().y()
            x = center_x + circle_radius * math.cos(angle_rad)
            y = center_y + circle_radius * math.sin(angle_rad)
            painter.setBrush(QColor(255, 255, 255, 60))
            painter.drawEllipse(x - dot_radius/2, y - dot_radius/2, dot_radius, dot_radius)

        # Gambar titik-titik progres
        num_active_dots = int(self._value / 100 * num_dots)
        painter.setBrush(QColor(255, 255, 255, 255))
        for i in range(num_active_dots):
            angle_rad = math.radians(i * (360 / num_dots) - 90)
            center_x = draw_rect.center().x()
            center_y = draw_rect.center().y()
            x = center_x + circle_radius * math.cos(angle_rad)
            y = center_y + circle_radius * math.sin(angle_rad)
            painter.drawEllipse(x - dot_radius/2, y - dot_radius/2, dot_radius, dot_radius)

        # Gambar teks persentase
        font = QFont("Segoe UI", int(side * 0.18), QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor("white"))
        painter.drawText(draw_rect, Qt.AlignmentFlag.AlignCenter, f"{self._value}%")