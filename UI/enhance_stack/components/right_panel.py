from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QMenu
from PyQt6.QtCore import Qt
import sqlite3

class RightPanel(QWidget):
    """Right panel containing a list of images."""
    def __init__(self):
        super().__init__()
        self.image_list = QListWidget()
        self.preview_active = True  # Default: Preview diizinkan
        self.preview_pause = False
        
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
        
        self.image_list.itemDoubleClicked.connect(self.set_to_image_reference)

        # Install event filter to capture key presses
        self.image_list.installEventFilter(self)

    def load_image_paths(self):
        """Load image paths from the database and populate the image list."""
        conn = sqlite3.connect("pixel_refine_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM images")
        image_paths = cursor.fetchall()
        conn.close()

        # Clear the existing items in the list
        self.image_list.clear()

        # Add the image paths to the list widget
        for path in image_paths:
            self.image_list.addItem(path[0])
            
    def set_to_image_reference(self, item):
        """Move the selected item to the top of the list."""
        row = self.image_list.row(item)
        if row > 0:
            self.image_list.takeItem(row)
            self.image_list.insertItem(0, item)
            self.image_list.setCurrentItem(item)

    def contextMenuEvent(self, event):
        """Display a context menu on right-click."""
        item = self.image_list.itemAt(event.pos())
        if item:
            menu = QMenu(self)
            set_ref_action = menu.addAction("Set as Image Reference")
            action = menu.exec(self.image_list.mapToGlobal(event.pos()))
            if action == set_ref_action:
                self.set_to_image_reference(item)

    def get_select_image_list(self):
        select_image_list = self.image_list.selectedItems()
        return [item.text() for item in select_image_list]

    def remove_selected_images(self):
        select_image_list = self.image_list.selectedItems()

        if select_image_list:
            if self.parent():
                if hasattr(self.parent(), 'single_page_layout'):
                    self.parent().single_page_layout.pause_preview_update()

            # Set pause untuk mengabaikan sinyal
            self.preview_pause = True

            # Hapus entri dari database
            conn = sqlite3.connect("pixel_refine_database.db")
            cursor = conn.cursor()

            for item in select_image_list:
                image_path = item.text()

                # Hapus dari database
                cursor.execute("DELETE FROM images WHERE path = ?", (image_path,))
                self.image_list.takeItem(self.image_list.row(item))

            conn.commit()
            conn.close()

            # Kembalikan status pause
            self.preview_pause = False

            if self.parent():
                if hasattr(self.parent(), 'single_page_layout'):
                    # Update preview panel setelah penghapusan
                    self.parent().single_page_layout.update_preview_panel(self.get_select_image_list())
                    self.parent().single_page_layout.resume_preview_update()


    def select_list_preview(self):
        """Signal to notify selection change to EnhanceStackPage."""
        if self.preview_pause:
            return  # Abaikan sinyal jika sedang dipause
        selected_paths = self.get_select_image_list()


        # Jika lebih dari satu gambar dipilih, hentikan proses preview sebelumnya dan tampilkan pesan
        if len(selected_paths) > 1:
            if self.parent():
                if hasattr(self.parent(), 'single_page_layout'):
                    self.parent().single_page_layout.pause_preview_update()
                    self.parent().single_page_layout.preview_scene.clear()

                # Nonaktifkan update preview
                label = QLabel("Multiple images selected. Preview disabled.")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # Tambahkan pesan ke preview scene
                proxy = self.parent().single_page_layout.preview_scene.addWidget(label)
                self.parent().single_page_layout.image_status_info(proxy)
            return

        # Jika hanya satu gambar yang dipilih, update preview panel
        if len(selected_paths) == 1:
            if self.parent() and hasattr(self.parent(), 'single_page_layout'):
                self.parent().single_page_layout.update_preview_panel(selected_paths)


    def eventFilter(self, source, event):
        """Filter events for specific widgets."""
        if source == self.image_list:
            if event.type() == event.Type.KeyPress:
                # Jika CTRL ditekan, ubah ke mode MultiSelection
                if event.key() == Qt.Key.Key_Control:
                    print("CTRL key pressed, enabling MultiSelection")
                    self.image_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
                    return True  # Event handled
                # Jika tombol Delete ditekan, hapus item yang dipilih
                elif event.key() == Qt.Key.Key_Delete:
                    print("Delete key pressed, removing selected items")
                    self.remove_selected_images()
                    return True  # Event handled
            elif event.type() == event.Type.KeyRelease:
                # Jika CTRL dilepaskan, ubah kembali ke mode SingleSelection
                if event.key() == Qt.Key.Key_Control:
                    print("CTRL key released, reverting to SingleSelection")
                    self.image_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
                    return True  # Event handled
        return super().eventFilter(source, event)

