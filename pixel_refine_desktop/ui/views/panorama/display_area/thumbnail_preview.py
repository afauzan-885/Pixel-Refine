from PySide6.QtCore import (
    Qt,
)
from PySide6.QtGui import (
    QPixmap,
)
from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QDialog,
    QGraphicsScene,
    QApplication,
)

from PIL import Image, ImageOps
from PIL.ImageQt import ImageQt

from pixel_refine_desktop.enhance_stack.core.logic.Zoomable_Handler import Zoomable


class ImagePreviewDialog(QDialog):
    """Dialog yang menampilkan gambar dengan orientasi dan ukuran awal yang benar."""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Preview - {image_path}")

        self.set_adaptive_initial_size()

        layout = QVBoxLayout(self)
        self.scene = QGraphicsScene(self)
        self.view = Zoomable(self.scene, self)
        layout.addWidget(self.view)

        self.pixmap_item = None
        pixmap = self.load_pixmap_with_correct_orientation(image_path)

        if pixmap and not pixmap.isNull():
            self.pixmap_item = self.scene.addPixmap(pixmap)
        else:
            error_label = QLabel(f"Failed to load image:\n{image_path}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.removeWidget(self.view)
            self.view.deleteLater()
            layout.addWidget(error_label)

    def set_adaptive_initial_size(
        self, width_ratio: float = 0.3, height_ratio: float = 0.5
    ):
        """
        Mengatur ukuran dan posisi awal dialog agar relatif terhadap ukuran layar.
        """
        # 1. Dapatkan layar utama tempat aplikasi berjalan
        primary_screen = QApplication.primaryScreen()
        if not primary_screen:
            self.resize(800, 600)
            return

        # 2. Dapatkan geometri area yang tersedia di layar (tidak termasuk taskbar, dll.)
        available_geometry = primary_screen.availableGeometry()
        screen_width = available_geometry.width()
        screen_height = available_geometry.height()

        # 3. Hitung ukuran dialog berdasarkan rasio
        dialog_width = int(screen_width * width_ratio)
        dialog_height = int(screen_height * height_ratio)

        # 4. Atur ukuran dialog
        self.resize(dialog_width, dialog_height)

        # 5. Pusatkan dialog di tengah layar
        # Hitung posisi x dan y agar jendela berada di tengah
        x = available_geometry.x() + (screen_width - dialog_width) / 2
        y = available_geometry.y() + (screen_height - dialog_height) / 2
        self.move(int(x), int(y))

        # Atur ukuran minimum agar pengguna tidak bisa membuatnya terlalu kecil
        self.setMinimumSize(int(screen_width * 0.4), int(screen_height * 0.4))

    def load_pixmap_with_correct_orientation(self, image_path: str) -> QPixmap | None:
        """
        Membuka file gambar menggunakan Pillow, menerapkan orientasi EXIF,
        dan mengonversinya menjadi QPixmap.
        """
        try:
            pil_image = Image.open(image_path)
            oriented_pil_image = ImageOps.exif_transpose(pil_image)
            qimage = ImageQt(oriented_pil_image)
            return QPixmap.fromImage(qimage)
        except Exception as e:
            print(f"Error loading image with Pillow for preview: {e}")
            return None

    # <<< PERBAIKAN KUNCI ADA DI SINI >>>
    def showEvent(self, event):
        """
        Dipanggil secara otomatis oleh Qt setelah dialog ditampilkan.
        Ini adalah tempat yang tepat untuk melakukan 'fitInView'.
        """
        super().showEvent(event)

        if self.pixmap_item:
            self.view.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        """
        Opsional, tapi sangat disarankan: Lakukan fitInView lagi saat jendela di-resize.
        """
        super().resizeEvent(event)
        if self.pixmap_item:
            self.view.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
