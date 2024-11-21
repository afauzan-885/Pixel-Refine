from PyQt6.QtWidgets import QVBoxLayout, QListWidget, QProgressBar, QListWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class ImagePanel(QVBoxLayout):
    def __init__(self):
        super().__init__()

        # Panel List Gambar
        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)  # Enable multi-selection
        self.image_list.setStyleSheet(""" 
            QListWidget {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                font-size: 14px;
                padding: 10px;
            }
        """)
        self.addWidget(self.image_list)

        # Progress Bar
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
                background-color: #3498db;
                width: 20px;
            }
        """)
        self.addWidget(self.progress_bar)

    def add_image(self, image_path):
        """Add an image file path to the list."""
        item = QListWidgetItem(image_path)  # Display file path in the list
        item.setIcon(QIcon("resources/icon/drag-handle.svg"))  # Optional: Set an icon for drag handle
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)  # Enable dragging for the item
        self.image_list.addItem(item)

    def delete_selected_images(self):
        """Delete selected images from the list."""
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            return  # No items selected

        for item in selected_items:
            row = self.image_list.row(item)
            self.image_list.takeItem(row)  # Remove the item
            
    def delete_selected_images(self, file_path=None):
        """Hapus gambar dari tampilan."""
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            return  # Tidak ada gambar yang dipilih
        
        if file_path:
            # Jika file_path diberikan, hapus gambar spesifik
            for item in self.image_list.findItems(file_path, Qt.MatchFlag.MatchExactly):
                row = self.image_list.row(item)
                self.image_list.takeItem(row)
        else:
            # Hapus semua gambar yang dipilih
            for item in selected_items:
                row = self.image_list.row(item)
                self.image_list.takeItem(row)
