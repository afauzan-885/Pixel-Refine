from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget
from PyQt6.QtGui import QPixmap
import sqlite3

class RightPanel(QWidget):
    """Right panel containing a list of images."""
    def __init__(self):
        super().__init__()
        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.image_list.setStyleSheet("""
            QListWidget {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                font-size: 14px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_list)

        # Panggil load_image_paths untuk menampilkan daftar gambar yang tersimpan
        self.load_image_paths()

        # Emit signal when the selection changes
        self.image_list.itemSelectionChanged.connect(self.on_selection_changed)

    def load_image_paths(self):
        # Fetch image paths from the database and populate the list widget
        conn = sqlite3.connect("image_paths.db")
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM images")
        image_paths = cursor.fetchall()
        conn.close()

        # Clear the existing items in the list
        self.image_list.clear()

        # Add the image paths to the list widget
        for path in image_paths:
            self.image_list.addItem(path[0])

    def get_selected_image_paths(self):
        selected_items = self.image_list.selectedItems()
        return [item.text() for item in selected_items]

    def remove_selected_images(self):
        selected_items = self.image_list.selectedItems()

        if selected_items:
            if self.parent():
                self.parent().pause_preview_update()

            # Putuskan sementara sinyal
            self.image_list.itemSelectionChanged.disconnect(self.on_selection_changed)

            for item in selected_items:
                self.image_list.takeItem(self.image_list.row(item))

            # Hubungkan kembali sinyal setelah selesai
            self.image_list.itemSelectionChanged.connect(self.on_selection_changed)

            if self.parent():
                self.parent().resume_preview_update()


    def on_selection_changed(self):
        """Signal to notify selection change to BurstDenoisingPage."""
        selected_paths = self.get_selected_image_paths()
        if self.parent():
            self.parent().update_preview_panel(selected_paths)