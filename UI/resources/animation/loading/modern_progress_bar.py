from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget

class ModernProgressBar(QWidget):
    """
    Widget progress bar kustom yang disederhanakan menjadi HANYA satu baris.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        
        # --- Hanya warna yang kita perlukan ---
        self.BG_COLOR = QColor("#5A5E6B") 
        self.FG_COLOR = QColor("#2ECEBA") 
        
       
    def setValue(self, value: int):
        """Mengatur nilai progres utama (0-100)."""
        self._value = max(0, min(value, 100))
        self.update()

    def value(self) -> int:
        return self._value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        radius = height / 2.0

        # --- Gambar satu bar saja ---

        # 1. Gambar background bar (track)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.BG_COLOR)
        painter.drawRoundedRect(0, 0, width, height, radius, radius)

        # 2. Gambar foreground (progress) di atasnya
        if self._value > 0:
            progress_width = (self._value / 100.0) * width
            painter.setBrush(self.FG_COLOR)
            painter.drawRoundedRect(0, 0, progress_width, height, radius, radius)