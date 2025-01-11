from PyQt6.QtWidgets import QWidget, QHBoxLayout, QProgressBar, QPushButton, QFileDialog, QMessageBox, QInputDialog
from PyQt6.QtCore import pyqtSignal
import os
import cv2

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
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #B2F2A0, stop:1 #66D966
                );
                color: #3C3939;
                font-weight: bold;
                border-radius: 10px;
                font-size: 14px;
                padding: 4px 8px;
                border: 1px solid #66D966;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #C7F3B8, stop:1 #82E582
                );
            }
            QPushButton:pressed {
                background-color: #56B856;
            }
        """)

        self.save_as_button = QPushButton(language_config.PROGRESS_SECTION_SAVE_BUTTON_TEXT)
        self.save_as_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #D3D3D3, stop:1 #A9A9A9
                );
                color: #3C3939;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                padding: 4px 8px;
                border: 1px solid #A9A9A9;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #E0E0E0, stop:1 #B8B8B8
                );
            }
            QPushButton:pressed {
                background-color: #808080;
            }
        """)

     
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
            QMessageBox.warning(self, "No Images", "There are no processed images to save.")
            return

        # Sort by modification time (last modified) and pick the latest file
        image_files.sort(key=os.path.getmtime, reverse=True)
        latest_image_path = image_files[0]

        # Ask the user where to save the file
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image As",
            os.path.basename(latest_image_path),  # Use the original file name
            "JPEG (*.jpg *.jpeg);;TIFF (*.tif *.tiff);;PNG (*.png)"
        )

        if not file_path:
            return  # User canceled the save dialog

        # Determine the file format from the file extension
        file_extension = os.path.splitext(file_path)[-1].lower()
        if file_extension not in [".jpg", ".jpeg", ".tif", ".tiff", ".png"]:
            QMessageBox.warning(self, "Invalid Format", "Unsupported file format.")
            return

        try:
            # Load the image with original bit depth using OpenCV
            image = cv2.imread(latest_image_path, cv2.IMREAD_UNCHANGED)
            if image is None:
                QMessageBox.critical(self, "Error", "Failed to load the image.")
                return

            # Save the image using OpenCV
            if file_extension in [".jpg", ".jpeg"]:
                cv2.imwrite(file_path, image, [cv2.IMWRITE_JPEG_QUALITY, 100])
            elif file_extension in [".tif", ".tiff"]:
                cv2.imwrite(file_path, image)  # OpenCV saves TIFF with original bit depth by default
            elif file_extension == ".png":
                cv2.imwrite(file_path, image, [cv2.IMWRITE_PNG_COMPRESSION, 5])

            # Confirm successful save
            QMessageBox.information(self, "Success", f"Image saved successfully as {file_path}.")

            # Remove the original image file
            os.remove(latest_image_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save image: {e}")