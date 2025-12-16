from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor, QMouseEvent, QPen
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from .theme import get_theme


class ImageCard(QWidget):
    """
    A friendly card component for displaying images or thumbnails.
    Supports selection, loading state, and click interactions.

    Usage:
        card = ImageCard("unique_id_or_path")
        card.set_image(pixmap)
        card.clicked.connect(handle_click)
    """

    # Signals for interaction
    clicked = Signal(str, object)  # emits (id, mouse_event)
    double_clicked = Signal(str)  # emits (id)

    def __init__(self, card_id: str, size: int = 110, parent=None):
        super().__init__(parent)
        self.card_id = card_id
        self._image_path = None  # Initialize to None to avoid AttributeError
        self._is_selected = False
        self._is_loading = True

        # Configure layout
        self.setFixedSize(size, size)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 5, 5, 5)  # Left padding 10px

        # Image container
        theme = get_theme()
        self.image_label = QLabel("Loading...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(f"color: {theme.text_secondary};")
        self.main_layout.addWidget(self.image_label)

        # Style
        self.setStyleSheet(
            f"""
            ImageCard {{
                background-color: {theme.bg_primary};
                border-radius: {theme.radius_md}px;
            }}
        """
        )

    def set_image(self, pixmap: QPixmap, scale_to_fit: bool = True):
        """Display an image on the card."""
        self._is_loading = False
        if pixmap and not pixmap.isNull():
            if scale_to_fit:
                # Scale considering padding (10px total)
                target_size = self.size() - QSize(10, 10)
                scaled = pixmap.scaled(
                    target_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.image_label.setPixmap(scaled)
            else:
                self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("No Image")

    def set_loading(self, loading: bool = True):
        """Show or hide the loading state."""
        self._is_loading = loading
        if loading:
            self.image_label.clear()
            self.image_label.setText("Loading...")
        else:
            if not self.image_label.pixmap():
                self.image_label.setText("No Image")

    # --- Selection API ---

    def select(self):
        """Select this card."""
        if not self._is_selected:
            self._is_selected = True
            self.update()  # Trigger repaint for overlay

    def deselect(self):
        """Deselect this card."""
        if self._is_selected:
            self._is_selected = False
            self.update()

    def toggle_selection(self):
        """Toggle selection state."""
        if self._is_selected:
            self.deselect()
        else:
            self.select()

    def is_selected(self) -> bool:
        return self._is_selected

    # --- Internals ---

    def paintEvent(self, event):
        """Draw selection overlay if selected."""
        super().paintEvent(event)

        if self._is_selected:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Use theme colors
            theme = get_theme()
            overlay_color = QColor(theme.primary)
            overlay_color.setAlpha(40)  # Semi-transparent overlay

            border_color = QColor(theme.primary)

            border_pen = QPen(border_color)
            border_pen.setWidth(2)

            painter.setPen(border_pen)
            painter.setBrush(overlay_color)

            # Draw rounded rect adjusting for pen width
            rect = self.rect().adjusted(1, 1, -1, -1)
            painter.drawRoundedRect(rect, 4, 4)

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit(self.card_id, event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.double_clicked.emit(self.card_id)
