from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QAbstractItemView, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
import sqlite3

from UI.enhance_stack.logic.database_manager import DatabaseManager

class RightPanel(QWidget):
    """Right panel containing a list of images."""
    previewImageRequested = pyqtSignal(list)
    
    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.image_list = QListWidget()
        self.preview_active = True  # Default: Preview diizinkan
        self.preview_pause = False
        self.db_manager = database_manager
        self.load_image_paths()
        self.image_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection) 
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
        """Load image paths using DatabaseManager."""
        # Hapus koneksi manual
        image_paths = self.db_manager.get_single_process_image_paths() 
        self.image_list.clear()
        self.image_list.addItems(image_paths) # Gunakan addItems

            
    def set_to_image_reference(self, item):
        """Move the selected item to the top of the list."""
        row = self.image_list.row(item)
        if row > 0:
            # Ambil item, hapus dari posisi lama, masukkan di posisi 0
            current_item = self.image_list.takeItem(row)
            self.image_list.insertItem(0, current_item)
            # Set item yang baru dipindah sebagai item terpilih saat ini
            self.image_list.setCurrentItem(current_item)


    def contextMenuEvent(self, event):
        """Display a context menu on right-click."""
        # Dapatkan posisi relatif terhadap list widget
        list_pos = self.image_list.mapFrom(self, event.pos())
        item = self.image_list.itemAt(list_pos)
        if item:
            menu = QMenu(self)
            set_ref_action = menu.addAction("Set as Image Reference")
            # Tambahkan action lain jika perlu
            # delete_action = menu.addAction("Delete Selected")

            action = menu.exec(self.image_list.mapToGlobal(list_pos))

            if action == set_ref_action:
                self.set_to_image_reference(item)
            # elif action == delete_action:
            #     self.remove_selected_images() # Panggil fungsi hapus

    def get_select_image_list(self):
        """Return a list of paths for the selected items."""
        select_image_list = self.image_list.selectedItems()
        return [item.text() for item in select_image_list]

    def remove_selected_images(self):
        """Remove selected images using DatabaseManager."""
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            return

        image_paths_to_delete = [item.text() for item in selected_items]

        try:
            # Panggil metode DatabaseManager untuk menghapus dari DB
            deleted_count = self.db_manager.single_process_delete_path_images(image_paths_to_delete)

            # Periksa hasil (metode DB Anda mungkin perlu return True/False atau jumlah)
            if deleted_count >= 0:
                print(f"DatabaseManager reported deletion of {deleted_count} links.")
                # Hapus dari UI HANYA jika DB berhasil
                rows_to_delete = sorted([self.image_list.row(item) for item in selected_items], reverse=True)
                for row in rows_to_delete:
                    if row >= 0:
                        self.image_list.takeItem(row)
            else:
                 # Handle kasus jika metode DB mengindikasikan kegagalan
                 from PyQt6.QtWidgets import QMessageBox
                 QMessageBox.warning(self, "Deletion Failed", "Could not remove images from the database.")

        except Exception as e: # Tangkap error umum jika pemanggilan metode DB gagal
            print(f"Error calling DatabaseManager to delete images: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"An error occurred during deletion:\n{e}")

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
        """Filter events - primarily for the Delete key."""
        if source == self.image_list:
            if event.type() == event.Type.KeyPress:
                # Hanya tangani tombol Delete di sini
                if event.key() == Qt.Key.Key_Delete:
                    print("Delete key pressed, removing selected items")
                    self.remove_selected_images()
                    return True

        # Penting: teruskan event yang tidak ditangani ke parent
        return super().eventFilter(source, event)

