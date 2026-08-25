from PySide6.QtCore import Qt, Signal, QSize, QPoint, Property, QRect
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QMouseEvent, QPen, QBrush
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
        self._image = None
        self._is_selected = False
        self._is_loading = True
        self._is_fetching = False
        self._placeholder_text = ""
        self._opacity = 1.0  # Tingkat transparansi (0.0 - 1.0)

        # Configure geometry reinforcement
        self.setFixedSize(size, size)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Style hint
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # No internal components/layouts to avoid layout-engine overhead during scroll

    def set_image(self, q_image: QImage, scale_to_fit: bool = True):
        """Display an image on the card (Pixel-Perfect Image Drawing)."""
        self._is_loading = False
        self._is_fetching = False
        self._placeholder_text = ""
        if q_image and not q_image.isNull():
            self._image = q_image
        else:
            self._image = None
        self.update()

    def set_loading(self, loading: bool = True):
        """Show or hide the loading state."""
        if self._is_loading != loading:
            self._is_loading = loading
            if loading:
                self._image = None
                self._placeholder_text = ""
            self.update()

    def set_placeholder_text(self, text: str):
        """Display lightweight text in place of a thumbnail image."""
        self._image = None
        self._is_loading = False
        self._is_fetching = False
        self._placeholder_text = str(text or "")
        self.update()

    def unload_image(self):
        """Unload image to free memory (Reinforced)."""
        if not self._is_loading:
            self._is_loading = True
            self._is_fetching = False
            self._image = None
            self._placeholder_text = ""
            self.update()

    def has_image(self) -> bool:
        """Check if card currently holds image data."""
        return self._image is not None

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

        if self._image:
            # Gunakan drawImage langsung dengan SmoothTransformation
            # Ini mengatasi bug gambar terpotong saat lazy loading/scroll
            img_size = self._image.size()
            img_size.scale(content_rect.size(), Qt.AspectRatioMode.KeepAspectRatio)

            # Center it
            x = content_rect.left() + (content_rect.width() - img_size.width()) // 2
            y = content_rect.top() + (content_rect.height() - img_size.height()) // 2

            target_rect = QRect(x, y, img_size.width(), img_size.height())

            # Pixel-to-pixel drawing: Render image directly into target rect
            painter.drawImage(target_rect, self._image)
        elif self._placeholder_text:
            placeholder_rect = rect.adjusted(1, 1, -1, -1)
            painter.setPen(QColor("gray"))
            painter.setBrush(QColor("lightgray"))
            painter.drawRect(placeholder_rect)

            painter.setPen(QColor(theme.text_secondary))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawText(
                content_rect,
                Qt.AlignmentFlag.AlignCenter,
                self._placeholder_text,
            )
        elif self._is_loading:
            painter.setPen(QColor(theme.text_secondary))
            painter.drawText(content_rect, Qt.AlignmentFlag.AlignCenter, "Loading..")
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

    def to_qml(self, indent=0):
        tab = "    " * indent
        size = self.width()
        img_source = self._image_path or ""
        selected = str(self._is_selected).lower()
        qml = f"{tab}Rectangle {{\n"
        qml += f"{tab}    width: {size}\n"
        qml += f"{tab}    height: {size}\n"
        qml += f"{tab}    radius: 4\n"
        qml += f"{tab}    color: 'transparent'\n"
        qml += f"{tab}    border.color: {selected == 'true' and 'genericTheme.primary' or 'transparent'}\n"
        qml += f"{tab}    border.width: 2\n"
        qml += f"{tab}    Image {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        anchors.margins: 5\n"
        qml += f"{tab}        source: '{img_source}'\n"
        qml += f"{tab}        fillMode: Image.PreserveAspectFit\n"
        qml += f"{tab}    }}\n"
        if self._is_loading:
            qml += f"{tab}    Text {{ text: 'Loading..'; anchors.centerIn: parent; color: genericTheme.textSecondary }}\n"
        qml += f"{tab}    MouseArea {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        onClicked: appBridge.openTool('{self.card_id}')\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml
