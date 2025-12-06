import os
from PySide6.QtWidgets import (
    QVBoxLayout,
    QGraphicsView,
    QGraphicsScene,
    QVBoxLayout,
    QGraphicsPixmapItem,
    QDialog
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

def get_last_image(path):
        """Mengambil file gambar terakhir dari folder berdasarkan waktu modifikasi"""
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if not files:
            return None

        # Ambil file dengan waktu modifikasi terakhir
        last_file = max(files, key=lambda f: os.path.getmtime(os.path.join(path, f)))
        return os.path.join(path, last_file)
    

# Create a dialog for the viewer
class ImageViewer(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Viewer")
        self.setFixedSize(600, 500)  # Set a minimum size for the dialog

        # Set the dialog as modal
        self.setModal(True)

        # Create a zoomable graphics view for the result image
        self.image_view = ZoomableGraphicsView(image_path)

        # Layout setup
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_view)

    def update_zoom(self, value):
        """Update zoom level for the image."""
        scale_factor = value / 100.0
        self.image_view.set_zoom(scale_factor)


# Custom zoomable graphics view
class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.zoom_level = 0  # Awal zoom level
        self.zoom_step = 0.1  # Besaran perubahan zoom
        self.max_zoom = 4.0  # Maksimum zoom (4x ukuran asli)
        self.min_zoom = 0.1  # Minimum zoom (10% dari ukuran asli)
        self.init_ui()

    def init_ui(self):
        """Initialize the graphics view."""
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Load and display the image
        pixmap = QPixmap(self.image_path)
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)

        # Enable dragging and zooming
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Fit the image to the view initially
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event):
        """Handle mouse wheel event for zooming."""
        delta = (
            event.angleDelta().y() / 120
        )  # Positif untuk scroll ke atas, negatif untuk ke bawah
        if delta > 0:
            # Zoom in
            new_zoom = min(self.zoom_level + self.zoom_step, self.max_zoom)
        else:
            # Zoom out
            new_zoom = max(self.zoom_level - self.zoom_step, self.min_zoom)

        # Jika zoom level berubah, terapkan zoom
        if new_zoom != self.zoom_level:
            self.zoom_level = new_zoom
            self.set_zoom(self.zoom_level)

    def set_zoom(self, scale_factor):
        """Set zoom level by scaling the view."""
        self.resetTransform()
        self.scale(scale_factor, scale_factor)
