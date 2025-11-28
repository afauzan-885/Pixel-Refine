from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QMouseEvent

# --- 1. Generic Grid Item (Dulu ThumbnailWidget) ---
class GridItemWidget(QWidget):
    """
    Widget kotak sederhana untuk grid.
    Bisa merepresentasikan Gambar, File, Dokumen, dll.
    """
    clicked = Signal(str)        # Mengirim ID item
    double_clicked = Signal(str) # Mengirim ID item

    def __init__(self, item_id, label_text, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self._is_selected = False

        self.setFixedSize(110, 110)
        
        # Layout Sederhana
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Placeholder Visual (Kotak abu-abu)
        self.visual_box = QLabel(label_text)
        self.visual_box.setAlignment(Qt.AlignCenter)
        self.visual_box.setStyleSheet("background-color: #ddd; border: 1px solid #bbb; color: #333;")
        self.visual_box.setWordWrap(True)
        
        layout.addWidget(self.visual_box)

    def set_selected(self, selected: bool):
        if self._is_selected != selected:
            self._is_selected = selected
            self.update() # Memicu paintEvent

    def paintEvent(self, event):
        """Menggambar border biru saat dipilih."""
        super().paintEvent(event)
        if self._is_selected:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Warna Highlight Biru
            border_pen = QPen(QColor(0, 120, 215)) 
            border_pen.setWidth(3)
            
            painter.setPen(border_pen)
            painter.setBrush(Qt.NoBrush)
            
            rect = self.rect().adjusted(2, 2, -2, -2)
            painter.drawRoundedRect(rect, 4, 4)

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit(self.item_id)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.double_clicked.emit(self.item_id)

# --- 2. Simple Loading View (Dulu ProcessingView) ---
class LoadingOverlay(QWidget):
    """Tampilan Loading Generik."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.lbl_text = QLabel("Processing...")
        self.lbl_text.setStyleSheet("font-size: 18px; color: #555;")
        
        # Anda bisa mengganti ini dengan Progress Bar favorit Anda
        self.progress_indicator = QLabel("[ Progress Bar Here ]")
        self.progress_indicator.setStyleSheet("color: #888;")
        
        layout.addWidget(self.lbl_text)
        layout.addWidget(self.progress_indicator)

    def set_status(self, text, percentage=0):
        self.lbl_text.setText(f"{text} ({percentage}%)")