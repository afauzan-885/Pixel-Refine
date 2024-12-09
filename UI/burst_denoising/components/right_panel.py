from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PyQt6.QtCore import Qt
import sqlite3
import sys

class RightPanel(QWidget):
    """Right panel containing a list of images."""
    def __init__(self):
        super().__init__()
        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
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

        # Install event filter to capture key presses
        self.image_list.installEventFilter(self)

    def load_image_paths(self):
        """Load image paths from the database and populate the image list."""
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

        if len(selected_paths) == 1:
            if self.parent():
                # Hentikan pemrosesan gambar jika masih berjalan
                if hasattr(self.parent(), 'raw_thread') and self.parent().raw_thread.isRunning():
                    self.parent().raw_thread.terminate()
                    self.parent().raw_thread.wait()

                # Tampilkan gambar yang dipilih
                self.parent().update_preview_panel(selected_paths)
        else:
            if self.parent():
                # Hentikan pemrosesan gambar jika masih berjalan
                if hasattr(self.parent(), 'raw_thread') and self.parent().raw_thread.isRunning():
                    self.parent().raw_thread.terminate()
                    self.parent().raw_thread.wait()

                # Nonaktifkan preview
                label = QLabel("Multiple images selected. Preview disabled.")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                proxy = self.parent().preview_scene.addWidget(label)
                self.parent().image_status_info(proxy)  # Pusatkan pesan


    def eventFilter(self, source, event):
        """Filter events for specific widgets."""
        if source == self.image_list:
            if event.type() == event.Type.KeyPress:
                # If CTRL is pressed, enable MultiSelection mode
                if event.key() == Qt.Key.Key_Control:
                    print("CTRL key pressed, enabling MultiSelection")
                    self.image_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
                    return True  # Event handled
            elif event.type() == event.Type.KeyRelease:
                # If CTRL is released, revert to SingleSelection mode
                if event.key() == Qt.Key.Key_Control:
                    print("CTRL key released, reverting to SingleSelection")
                    self.image_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
                    return True  # Event handled
        return super().eventFilter(source, event)

