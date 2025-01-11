import os
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QMessageBox,
    QGraphicsView,
    QGraphicsScene,
    QVBoxLayout,
    QGraphicsPixmapItem,
    QDialog
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from UI.enhance_stack.algorithm.alignment.AKAZE import running_akaze
from UI.enhance_stack.algorithm.alignment.Farneback_optical_flow import running_farneback_optical_flow
from UI.enhance_stack.algorithm.alignment.ORB import running_orb
from UI.enhance_stack.algorithm.denoising.Average import running_average

def get_last_image(path):
        """Mengambil file gambar terakhir dari folder berdasarkan waktu modifikasi"""
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if not files:
            return None

        # Ambil file dengan waktu modifikasi terakhir
        last_file = max(files, key=lambda f: os.path.getmtime(os.path.join(path, f)))
        return os.path.join(path, last_file)
    

def process_algorithm(self):
        """
        Fungsi untuk memproses algoritma berdasarkan pilihan dropdown.
        """
        try:
            alignment_choice = self.left_panel.alignment_dropdown.currentText()
            denoising_choice = self.left_panel.denoising_dropdown.currentText()  # Ambil pilihan denoising
            super_resolution_choice = self.left_panel.super_resolution_dropdown.currentText()  # Ambil pilihan super resolution

            # Jika tidak ada algoritma yang dipilih
            if alignment_choice == "None" and denoising_choice == "None" and super_resolution_choice == "None":
                QMessageBox.warning(self, "Peringatan", "Tidak ada algoritma yang dipilih untuk diproses.")
                return

            # Proses untuk Alignment
            if alignment_choice == "ORB":
                running_orb(self)
            elif alignment_choice == "Farneback Optical Flow":
                running_farneback_optical_flow(self)
            elif alignment_choice == "AKAZE":
                running_akaze(self)
            elif alignment_choice == "None":
                if denoising_choice != "None":  # Jika hanya denoising yang dipilih
                    reply = QMessageBox.question(self, "Konfirmasi", 
                                                "Yakin tidak ingin menyelaraskan terlebih dahulu?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                                QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No:
                        return  # Jika pengguna memilih 'No', berhenti proses
            else:
                QMessageBox.warning(self, "Peringatan", "Pilihan algoritma alignment tidak dikenali.")
                
            super_resolution_executed = False
            # Proses untuk Super Resolution
            if super_resolution_choice == "None":
                pass  # Tidak ada super resolution yang dipilih
            else:
                QMessageBox.information(self, "Info", "Modul Super Resolusi belum diimplementasikan.")
        
            
            if super_resolution_executed:
                latest_image_path = get_last_image("database/stack")
                if latest_image_path:
                    dialog = ImageViewer(latest_image_path, self)  # Menampilkan gambar di ImageViewer
                    dialog.exec()  # Menampilkan dialog secara modal
                else:
                    QMessageBox.warning(self, "Peringatan", "Tidak ada gambar yang tersedia di folder stack.")


            # Proses untuk Denoising
            denoising_executed = False  # Flag untuk melacak apakah denoising dilakukan
            if denoising_choice == "Average":
                print("Sebelum memanggil running_average")
                running_average(self)
                print("Setelah memanggil running_average")

                denoising_executed = True
            elif denoising_choice == "Median":
                QMessageBox.warning(self, "Peringatan", "Modul Median belum diimplementasikan.")
            elif denoising_choice == "Similarity":
                QMessageBox.warning(self, "Peringatan", "Modul Similarity belum diimplementasikan.")
            elif denoising_choice == "none":
                return 
           
            # Tampilkan hasil hanya jika denoising berhasil dijalankan
            if denoising_executed:
                latest_image_path = get_last_image("database/stack")
                if latest_image_path:
                    dialog = ImageViewer(latest_image_path, self)  # Menampilkan gambar di ImageViewer
                    dialog.exec()  # Menampilkan dialog secara modal
                else:
                    QMessageBox.warning(self, "Peringatan", "Tidak ada gambar yang tersedia di folder stack.")
        except Exception as e:
                    QMessageBox.critical(self, "Error", f"Terjadi kesalahan: {e}")

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
