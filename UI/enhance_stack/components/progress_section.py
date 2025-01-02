from PyQt6.QtWidgets import QWidget, QHBoxLayout, QProgressBar, QPushButton, QFileDialog, QMessageBox, QInputDialog
from PyQt6.QtCore import pyqtSignal
import os
from PIL import Image

from UI.settings.General.Language import language_config

class ProgressSection(QWidget):
    process_clicked  = pyqtSignal()
    save_as_clicked = pyqtSignal()
    
    """Progress bar and control buttons."""
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 5px;
                background-color: #f0f0f0;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #80C4E9;
                width: 20px;
            }
        """)

        # self.next_button = QPushButton("Next")
        self.process_button = QPushButton(language_config.PROGRESS_SECTION_PROCESS_BUTTON_TEXT)
        self.save_as_button = QPushButton(language_config.PROGRESS_SECTION_SAVE_BUTTON_TEXT)
     
        self.layout.addWidget(self.progress_bar, 2)
        # self.layout.addWidget(self.next_button, 1)
        self.layout.addWidget(self.process_button, 1)
        self.layout.addWidget(self.save_as_button, 1)
        
        self.process_button.clicked.connect(self.process_clicked)
        self.save_as_button.clicked.connect(self.save_image)
        
    def save_image(self):
        folder_path = "database/stack"  # Path to the folder containing images
        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "Error", "The folder 'database/stack' does not exist.")
            return

        # Get all image files in the folder and sort them by modification time
        image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if not image_files:
            QMessageBox.warning(self, "No Images", "No images available in the folder.")
            return

        # Sort by modification time (last modified) and pick the latest file
        image_files.sort(key=os.path.getmtime, reverse=True)
        latest_image_path = image_files[0]

        # Ask the user where to save the file
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image As",
            "",
            "JPEG (*.jpg *.jpeg);;TIFF (*.tif *.tiff);;PNG (*.png)"
        )

        if not file_path:
            return  # User canceled the save dialog

        # Determine the file format from the file extension
        file_extension = os.path.splitext(file_path)[-1].lower()
        if file_extension in [".jpg", ".jpeg"]:
            format = "JPEG"
        elif file_extension in [".tif", ".tiff"]:
            format = "TIFF"
        elif file_extension == ".png":
            format = "PNG"
        else:
            QMessageBox.warning(self, "Invalid Format", "Unsupported file format.")
            return

        try:
            # Load the image from the latest path and save it in the chosen format
            image = Image.open(latest_image_path)
            image.save(file_path, format)

            # Confirm successful save
            QMessageBox.information(self, "Success", f"Image saved successfully as {file_path}.")

            # Remove the original image file
            os.remove(latest_image_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save image: {e}")
            # Ask the user for the bit depth if the format is TIFF
            if format == "TIFF":
                bit_depth, ok = QInputDialog.getItem(
                    self,
                    "Select Bit Depth",
                    "Choose the bit depth for TIFF:",
                    ["8-bit", "16-bit"],
                    0,
                    False
                )
                if not ok:
                    return  # User canceled the bit depth selection

            # Load the image from the latest path and save it in the chosen format
            image = Image.open(latest_image_path)
            if format == "TIFF" and bit_depth == "16-bit":
                image = image.convert("I;16")  # Convert to 16-bit grayscale

            # Use the original file name for saving
            original_file_name = os.path.basename(latest_image_path)
            file_path = os.path.join(os.path.dirname(file_path), original_file_name)

            image.save(file_path, format)

            # Confirm successful save
            QMessageBox.information(self, "Success", f"Image saved successfully as {file_path}.")

            # Remove the original image file
            os.remove(latest_image_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save image: {e}")