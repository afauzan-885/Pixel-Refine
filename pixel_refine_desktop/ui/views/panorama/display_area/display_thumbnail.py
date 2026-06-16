from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QColor,
    QMouseEvent,
    QPen
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,

)
class ThumbnailWidget(QWidget):
    """Widget kustom untuk setiap thumbnail, menggunakan paintEvent untuk seleksi."""
    back_to_preview_requested = Signal() 
    clicked = Signal(str, QMouseEvent)
    double_clicked = Signal(str)

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self._is_selected = False

        self.setFixedSize(110, 110)
        self.setObjectName("thumbnailWidget")

        self.has_valid_preview = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5) 
        self.image_label = QLabel("Loading...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

    # Metode untuk menerima gambar dari thread
    def set_pixmap(self, pixmap: QPixmap):
        if not pixmap.isNull():
            self.pixmap = pixmap.scaled(
                100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(self.pixmap)
            
    def is_selected(self) -> bool:
        """Getter: Mengembalikan status terpilih."""
        return self._is_selected

    def set_selected(self, selected: bool):
        """
        Setter: Mengatur status terpilih dan memicu penggambaran ulang.
        """
        # Hanya proses jika status benar-benar berubah
        if self._is_selected != selected:
            self._is_selected = selected
            self.update() 
    
    def paintEvent(self, event):
        """
        Menggambar widget. Dipanggil secara otomatis oleh Qt saat 'update()' dipanggil.
        """
        super().paintEvent(event)

        if self._is_selected:
            painter = QPainter(self)
            try:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                overlay_color = QColor(173, 216, 230, 128)

                border_color = QColor(0, 84, 166)
                
                border_pen = QPen(border_color)
                border_pen.setWidth(2)

                painter.setPen(border_pen)
                painter.setBrush(overlay_color)

                pen_half_width = border_pen.width() / 2.0
                draw_rect = self.rect().adjusted(
                    pen_half_width, pen_half_width, 
                    -pen_half_width, -pen_half_width
                )
                
                painter.drawRoundedRect(draw_rect, 4.0, 4.0)
            finally:
                painter.end()


    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit(self.image_path, event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.double_clicked.emit(self.image_path)
