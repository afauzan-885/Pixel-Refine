from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PyQt6.QtCore import Qt
import sqlite3

class RightPanel(QWidget):
    """Right panel containing a list of images."""
    def __init__(self):
        super().__init__()
        self.image_list = QListWidget()
        self.preview_active = True  # Default: Preview diizinkan
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
        self.image_list.itemSelectionChanged.connect(self.select_list_preview)

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

    def get_select_image_list(self):
        select_image_list = self.image_list.selectedItems()
        return [item.text() for item in select_image_list]

    def remove_selected_images(self):
        select_image_list = self.image_list.selectedItems()

        if select_image_list:
            if self.parent():
                self.parent().pause_preview_update()

            # Putuskan sementara sinyal
            self.image_list.itemSelectionChanged.disconnect(self.select_list_preview)

            for item in select_image_list:
                self.image_list.takeItem(self.image_list.row(item))

            # Hubungkan kembali sinyal setelah selesai
            self.image_list.itemSelectionChanged.connect(self.select_list_preview)

            if self.parent():
                self.parent().resume_preview_update()

    def select_list_preview(self):
        """Signal to notify selection change to BurstDenoisingPage."""
        selected_paths = self.get_select_image_list()

        # Jika lebih dari satu gambar dipilih, hentikan proses preview sebelumnya dan tampilkan pesan
        if len(selected_paths) > 1:
            if self.parent():
                if hasattr(self.parent(), "raw_thread") and self.parent().raw_thread.isRunning():
                    self.parent().raw_thread.stop()
                    self.parent().raw_thread.quit()

                self.parent().pause_preview_update()
                self.parent().preview_scene.clear()

                # Nonaktifkan update preview
                label = QLabel("Multiple images selected. Preview disabled.")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # Tambahkan pesan ke preview scene
                proxy = self.parent().preview_scene.addWidget(label)
                self.parent().image_status_info(proxy)

            return 
        # Jika hanya satu gambar yang dipilih, update preview panel
        if len(selected_paths) == 1:
            if self.parent():
                self.parent().update_preview_panel(selected_paths)

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
