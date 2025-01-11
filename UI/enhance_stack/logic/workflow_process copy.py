import os
import sys
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QDialog, QVBoxLayout,QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPointF

from UI.settings.General.Language import language_config
from .multi_threading import RunningAlgorithmThreading

def process_algorithm(self, virtualenv_path=r"venv/Scripts/python.exe", base_path="UI/enhance_stack/algorithm"):
    """Handle algorithm processing when 'Process' button is clicked."""

    # Handle PyInstaller bundling
    if getattr(sys, 'frozen', False):  # Check if running from a bundled executable
        base_path = os.path.join(sys._MEIPASS, base_path)  # Adjust base_path to temporary extraction location

    # Get selected algorithms and stacking method
    alignment = self.left_panel.alignment_dropdown.currentText()
    multiFrame_super_resolution = self.left_panel.super_resolution_dropdown.currentText()
    multiFrame_noise_reduction = self.left_panel.denoising_dropdown.currentText()

    # Ensure mutual exclusivity between multiFrame_super_resolution and multiFrame_noise_reduction
    if multiFrame_super_resolution != "None":
        multiFrame_noise_reduction = "None"
    elif multiFrame_noise_reduction != "None":
        multiFrame_super_resolution = "None"

    # Validate dropdown selections
    if alignment == "None" and multiFrame_super_resolution == "None" and multiFrame_noise_reduction == "None":
        # Pesan pada konsol
        print(language_config.PROCESS_ALGORITHM_PROCESS_SKIPPED)
        
        # Menampilkan pesan pada message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("Process Skipped")
        msg_box.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint )
        msg_box.setText(language_config.PROCESS_ALGORITHM_PROCESS_SKIPPED)
        
        # Mengatur tombol default menjadi Close
        msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
        msg_box.exec()

        return



    # Dynamically define paths for algorithms
    algorithm_alignment = {self.left_panel.alignment_dropdown.itemText(i): os.path.join(base_path, "alignment", 
                           f"{self.left_panel.alignment_dropdown.itemText(i).replace(' ', '_').lower()}.py") 
                         for i in range(self.left_panel.alignment_dropdown.count())}

    algorithm_multiFrame_super_resolution = {self.left_panel.super_resolution_dropdown.itemText(i): os.path.join(base_path, "super_resolution", 
                          f"{self.left_panel.super_resolution_dropdown.itemText(i).replace(' ', '_').lower()}.py") 
                        for i in range(self.left_panel.super_resolution_dropdown.count())}

    algorithm_multiFrame_noise_reduction = {self.left_panel.denoising_dropdown.itemText(i): os.path.join(base_path, "denoising", 
                         f"{self.left_panel.denoising_dropdown.itemText(i).replace(' ', '_').lower()}.py") 
                        for i in range(self.left_panel.denoising_dropdown.count())}

    # Prepare tasks for threading
    algorithm_tasks = []

    if alignment != "None" and alignment in algorithm_alignment:
        algorithm_tasks.append((virtualenv_path, algorithm_alignment[alignment], f"Alignment: {alignment}"))

    if multiFrame_super_resolution != "None" and multiFrame_super_resolution in algorithm_multiFrame_super_resolution:
        algorithm_tasks.append((virtualenv_path, algorithm_multiFrame_super_resolution[multiFrame_super_resolution], f"Super Resolution: {multiFrame_super_resolution}"))

    if multiFrame_noise_reduction != "None" and multiFrame_noise_reduction in algorithm_multiFrame_noise_reduction:
        algorithm_tasks.append((virtualenv_path, algorithm_multiFrame_noise_reduction[multiFrame_noise_reduction], f"Denoising: {multiFrame_noise_reduction}"))

    # Run algorithms in a separate thread
    self.algorithm_thread = RunningAlgorithmThreading(algorithm_tasks)
    self.algorithm_thread.progress_signal.connect(self.update_progress_bar)

    # Callback for when the algorithm is finished
    def on_algorithm_complete():
        """Handle post-algorithm tasks: display result image with zoom and pan functionality."""

        # Periksa apakah ada algoritma denoising dalam tugas yang dijalankan
        if not any("Denoising" in task[2] for task in algorithm_tasks):
            print("No denoising algorithm was executed. Skipping image viewer setup.")
            return

        # Get the latest image from the stack folder
        stack_path = "database/stack"
        if not os.path.exists(stack_path):
            print(f"Stack folder {stack_path} does not exist.")
            return

        # Find the most recent file in the stack folder
        try:
            stack_files = [
                os.path.join(stack_path, f) for f in os.listdir(stack_path)
                if os.path.isfile(os.path.join(stack_path, f))
            ]
            if not stack_files:
                print("No files found in stack folder.")
                return
            latest_image_path = max(stack_files, key=os.path.getmtime)
        except Exception as e:
            print(f"Error finding stack images: {e}")
            return

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
                self.min_zoom = 0.25  # Minimum zoom (25% dari ukuran asli)
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
                delta = event.angleDelta().y() / 120  # Positif untuk scroll ke atas, negatif untuk ke bawah
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


        # Show the dialog
        dialog = ImageViewer(latest_image_path, self)
        dialog.exec()

    self.algorithm_thread.finished.connect(on_algorithm_complete)

    # Start the thread
    self.algorithm_thread.start()

