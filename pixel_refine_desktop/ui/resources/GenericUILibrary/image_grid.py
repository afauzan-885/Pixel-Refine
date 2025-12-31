from PySide6.QtCore import Qt, Signal, QSize, QPoint, Property
from PySide6.QtGui import QPixmap, QPainter, QColor, QMouseEvent, QPen, QBrush
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy

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
        self._image_path = None
        self._pixmap = None
        self._scaled_pixmap = None
        self._is_selected = False
        self._is_loading = True
        self._is_fetching = False
        self._opacity = 1.0  # Tingkat transparansi (0.0 - 1.0)

        # Configure geometry reinforcement
        self.setFixedSize(size, size)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Style hint
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # No internal components/layouts to avoid layout-engine overhead during scroll

    def set_image(self, pixmap: QPixmap, scale_to_fit: bool = True):
        """Display an image on the card (Reinforced)."""
        self._is_loading = False
        self._is_fetching = False
        if pixmap and not pixmap.isNull():
            self._pixmap = pixmap
            self._scaled_pixmap = None  # Clear cache
        else:
            self._pixmap = None
            self._scaled_pixmap = None
        self.update()

    def set_loading(self, loading: bool = True):
        """Show or hide the loading state."""
        if self._is_loading != loading:
            self._is_loading = loading
            if loading:
                self._pixmap = None
                self._scaled_pixmap = None
            self.update()

    def unload_image(self):
        """Unload image to free memory (Reinforced)."""
        if not self._is_loading:
            self._is_loading = True
            self._is_fetching = False
            self._pixmap = None
            self._scaled_pixmap = None
            self.update()

    def has_image(self) -> bool:
        """Check if card currently holds image data."""
        return self._pixmap is not None or self._scaled_pixmap is not None

    # --- Animation Properties ---

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):
        self._opacity = float(value)
        self.update()

    # Qt Property for animation
    opacity = Property(float, get_opacity, set_opacity)

    # --- Selection API ---

    def select(self):
        """Select this card."""
        if not self._is_selected:
            self._is_selected = True
            try:
                self.update()  # Trigger repaint for overlay
            except RuntimeError:
                pass

    def deselect(self):
        """Deselect this card."""
        if self._is_selected:
            self._is_selected = False
            try:
                self.update()
            except RuntimeError:
                pass

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
        """Render the card and its content manually for ultimate stability."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Apply internal opacity for reinforced fade-in
        painter.setOpacity(self._opacity)

        theme = get_theme()
        rect = self.rect()

        # 1. Background (Transparent - No brush/pen applied to fill)
        # Background is inherited or empty as per user request.

        # 2. Content (Image / Loading / Placeholder)
        content_rect = rect.adjusted(5, 5, -5, -5)  # Internal padding

        if self._is_loading:
            painter.setPen(QColor(theme.text_secondary))
            painter.drawText(content_rect, Qt.AlignmentFlag.AlignCenter, "Loading...")
        elif self._pixmap:
            # Cache scaling for performance
            if not self._scaled_pixmap:
                self._scaled_pixmap = self._pixmap.scaled(
                    content_rect.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

            # Center the scaled pixmap
            x = (
                content_rect.left()
                + (content_rect.width() - self._scaled_pixmap.width()) // 2
            )
            y = (
                content_rect.top()
                + (content_rect.height() - self._scaled_pixmap.height()) // 2
            )
            painter.drawPixmap(x, y, self._scaled_pixmap)
        else:
            painter.setPen(QColor(theme.text_secondary))
            painter.drawText(content_rect, Qt.AlignmentFlag.AlignCenter, "!")

        # 3. Selection Overlay
        if self._is_selected:
            overlay_color = QColor(theme.primary)
            overlay_color.setAlpha(40)

            border_pen = QPen(QColor(theme.primary))
            border_pen.setWidth(2)

            painter.setPen(border_pen)
            painter.setBrush(overlay_color)

            # Adjusted rect for border alignment
            selection_rect = rect.adjusted(1, 1, -1, -1)
            painter.drawRoundedRect(selection_rect, 4, 4)

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit(self.card_id, event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.double_clicked.emit(self.card_id)
