from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFrame,
    QPushButton,
    QHBoxLayout,
    QListWidget,
    QInputDialog,
    QListWidgetItem,
    QAbstractItemView,
    
)
from PySide6.QtCore import Qt, Signal, Slot, QEvent
from PySide6.QtWidgets import QMessageBox

from UI.panorama.logic.BatchProcessPano import BatchProcessDialog

class WorkingRightPanel(QWidget):
    """
    Panel kanan yang mengelola daftar proyek panorama.
    Memancarkan sinyal saat ada perubahan pemilihan.
    """

    project_selection_changed = Signal(int, str)
    project_selection_cleared = Signal()
    project_list_updated = Signal(bool)

    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager

        right_panel_layout = QVBoxLayout(self)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(10)

        project_list_panel = self._create_project_list_panel()
        self.process_button = QPushButton("Process All Pano")
        self.process_button.setObjectName("processButton")
        self.process_button.clicked.connect(self._show_batch_process_dialog)

        right_panel_layout.addWidget(project_list_panel, 1)
        right_panel_layout.addWidget(self.process_button)

    def _create_project_list_panel(self):
        project_panel = QFrame()
        project_panel.setObjectName("projectPanel")
        panel_layout = QVBoxLayout(project_panel)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Pano")
        self.btn_add.setObjectName("addButton")
        # KEMBALIKAN KE NAMA SEMULA
        self.btn_delete = QPushButton("Delete Pano")
        self.btn_delete.setObjectName("deleteButton")
        self.btn_delete.setEnabled(False)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        panel_layout.addLayout(btn_layout)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        panel_layout.addWidget(self.list_widget)

        self.btn_add.clicked.connect(self.add_new_panorama)
        self.btn_delete.clicked.connect(self.delete_selected_panorama)
        self.list_widget.itemSelectionChanged.connect(self.on_project_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.rename_selected_project)
        self.list_widget.installEventFilter(self)
        
        return project_panel
    
    def _show_batch_process_dialog(self):
        # 1. Ambil semua proyek dari database
        all_projects = self.database_manager.get_all_panorama_projects()
        
        if not all_projects:
            QMessageBox.information(self, "No Projects", "There are no panorama projects to process.")
            return

        # 2. Buat dan tampilkan dialog, kirimkan daftar proyek dan db manager
        dialog = BatchProcessDialog(all_projects, self.database_manager, self)
        dialog.exec() # exec() akan menampilkan dialog sebagai modal

    def load_projects_from_db(self):
        """
        Mengambil proyek dari DB, mengisi list widget, dan memilih item pertama jika ada.
        """
        self.list_widget.clear()
        projects = self.database_manager.get_all_panorama_projects()
        for project_id, project_name in projects:
            item = QListWidgetItem(project_name)
            item.setData(Qt.UserRole, project_id)  
            self.list_widget.addItem(item)
        
        # Pancarkan sinyal untuk memberi tahu panel kiri apakah ada proyek atau tidak
        self.project_list_updated.emit(self.list_widget.count() > 0)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def add_new_panorama(self):
        """Handler untuk membuat proyek baru."""
        text, ok = QInputDialog.getText(
            self, "New Panorama Project", "Enter project name:"
        )
        if ok and text:
            new_project_id = self.database_manager.create_new_panorama_project(
                name=text
            )
            if new_project_id is not None:
                self.load_projects_from_db()
                for i in range(self.list_widget.count()):
                    if self.list_widget.item(i).data(Qt.UserRole) == new_project_id:
                        self.list_widget.setCurrentRow(i)
                        break

    def delete_selected_panorama(self):
        selected_items = self.list_widget.selectedItems()
        
        # Jika tidak ada yang terpilih, jangan lakukan apa-apa
        if not selected_items:
            return

        # Buat pesan konfirmasi yang dinamis
        item_count = len(selected_items)
        project_names = "\n - ".join([item.text() for item in selected_items])
        question = (f"Are you sure you want to delete these {item_count} projects?\n\n"
                    f" - {project_names}")

        reply = QMessageBox.question(
            self,
            "Confirm Delete Projects",
            question,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Loop melalui item-item yang terpilih untuk dihapus
            # Kita ambil datanya dulu sebelum mulai mengubah UI
            items_to_delete = [(item.data(Qt.UserRole), item) for item in selected_items]
            
            for project_id, item in items_to_delete:
                if self.database_manager.delete_panorama_project(project_id):
                    # Hapus item dari list widget jika berhasil dihapus dari DB
                    self.list_widget.takeItem(self.list_widget.row(item))
                else:
                    # Beri tahu pengguna jika ada yang gagal
                    QMessageBox.warning(self, "Deletion Failed", 
                                        f"Could not delete the project '{item.text()}' from the database.")
            
            # Pancarkan sinyal bahwa daftar proyek telah diperbarui
            self.project_list_updated.emit(self.list_widget.count() > 0)

    def initiate_rename_sequence(self, item_to_rename):
        """Memulai proses rename untuk item yang diberikan."""
        if not item_to_rename:
            return

        project_id = item_to_rename.data(Qt.UserRole)
        old_name = item_to_rename.text()

        new_name, ok = QInputDialog.getText(
            self, "Rename Project", "Enter new name:", text=old_name
        )

        if ok and new_name and new_name != old_name:
            if self.database_manager.rename_panorama_project(project_id, new_name):
                item_to_rename.setText(new_name)  
                self.project_selection_changed.emit(project_id, new_name)

    def rename_selected_project(self, item):
        """Slot untuk double-click pada item list."""
        self.initiate_rename_sequence(item)

    @Slot(int, str)
    def handle_rename_request(self, project_id, old_name):
        """Menangani permintaan rename yang datang dari panel kiri."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == project_id:
                self.initiate_rename_sequence(item)
                return
    def eventFilter(self, source, event):
        # Pastikan event berasal dari list widget dan merupakan penekanan tombol
        if source is self.list_widget and event.type() == QEvent.Type.KeyPress:
            # Jika tombol yang ditekan adalah DELETE
            if event.key() == Qt.Key.Key_Delete:
                # Panggil fungsi penghapusan kita (yang akan kita upgrade)
                self.delete_selected_panorama()
                # Tandai event sebagai sudah ditangani
                return True 
        
        # Untuk event lainnya, teruskan ke handler default
        return super().eventFilter(source, event)

    def on_project_selection_changed(self):
        """Memancarkan sinyal saat seleksi berubah, menangani 0, 1, atau banyak item."""
        selected_items = self.list_widget.selectedItems()
        
        # Aktifkan atau nonaktifkan tombol delete berdasarkan apakah ada seleksi
        self.btn_delete.setEnabled(len(selected_items) > 0)
        
        if len(selected_items) == 1:
            # Jika hanya satu yang terpilih, perlakukan seperti biasa
            current_item = selected_items[0]
            project_id = current_item.data(Qt.UserRole)
            project_name = current_item.text()
            self.project_selection_changed.emit(project_id, project_name)
        else:
            # Jika 0 atau lebih dari 1 yang terpilih, bersihkan panel kiri
            self.project_selection_cleared.emit()
