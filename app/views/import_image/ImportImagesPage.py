from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from .TopBar import TopBar
from .ImagePanel import ImagePanel
from PyQt6.QtCore import Qt

class ImportImagesPage(QWidget):
    def __init__(self):
        super().__init__()

        # Layout utama
        layout = QVBoxLayout()

        # Komponen Top Bar
        self.top_bar = TopBar(self.import_images, self.delete_images)
        layout.addLayout(self.top_bar)

        # Komponen Image Panel
        self.image_panel = ImagePanel()
        layout.addLayout(self.image_panel)

        self.setLayout(layout)

        # State tracking
        self.shift_pressed = False
        self.ctrl_pressed = False
        self.last_selected_item = None

    def import_images(self):
        """Handle 'Import Image' button click."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select Images", 
            "", 
            "Image Files (*.dng *.png *.jpg *.tiff);;All Files (*)"
        )

        if file_paths:
            self.image_panel.progress_bar.setValue(0)  # Reset progress bar
            total_files = len(file_paths)

            for index, file_path in enumerate(file_paths):
                self.image_panel.add_image(file_path)
                progress = int((index + 1) / total_files * 100)
                self.image_panel.progress_bar.setValue(progress)

    def delete_images(self):
        """Handle 'Delete' button click."""
        self.image_panel.delete_selected_images()
