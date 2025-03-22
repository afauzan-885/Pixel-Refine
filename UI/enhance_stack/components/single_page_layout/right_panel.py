from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
import sqlite3

class RightPanel(QWidget):
    """Right panel containing a list of images."""
    previewImageRequested = pyqtSignal(list)
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
        """Load image paths from the database based on the single_process_image table."""
        conn = sqlite3.connect("pixel_refine_database.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT images.path
            FROM images
            JOIN single_process_image ON single_process_image.image_id_single = images.id
        """)
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
            conn = sqlite3.connect("pixel_refine_database.db")
            cursor = conn.cursor()

            for item in select_image_list:
                image_path = item.text()
                # Ambil ID gambar dari tabel images
                cursor.execute("SELECT id FROM images WHERE path = ?", (image_path,))
                result = cursor.fetchone()
                if result:
                    image_id = result[0]
                    # Hapus entri terkait di single_process_image menggunakan image_id_single
                    cursor.execute("DELETE FROM single_process_image WHERE image_id_single = ?", (image_id,))
                # Hapus item dari QListWidget
                self.image_list.takeItem(self.image_list.row(item))

            conn.commit()
            conn.close()


    def select_list_preview(self):
            """Emit sinyal ketika hanya satu gambar yang dipilih."""
            if self.preview_pause:
                return  # Abaikan sinyal jika sedang dipause
            selected_paths = self.get_select_image_list()

            # Untuk multiple selection, kamu bisa mengatur logika lain atau mengirim sinyal berbeda
            if len(selected_paths) == 1:
                self.previewImageRequested.emit(selected_paths)
                
            # Jika multiple images, misalnya tidak perlu preview:
            elif len(selected_paths) > 1:
                # Kamu bisa mengirim sinyal kosong atau mengabaikannya
                pass

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

