# File: working_right_panel.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QPushButton, QHBoxLayout, QListWidget, QInputDialog,
    QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QMessageBox


class WorkingRightPanel(QWidget):
    """
    Panel kanan yang mengelola daftar proyek panorama.
    Memancarkan sinyal saat ada perubahan pemilihan.
    """
    # === PERUBAHAN: Definisikan sinyal kustom ===
    # Sinyal ini akan membawa (int: project_id, str: project_name)
    project_selection_changed = Signal(int, str)
    # Sinyal saat tidak ada proyek yang dipilih
    project_selection_cleared = Signal()

    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        
        right_panel_layout = QVBoxLayout(self)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(10)

        project_list_panel = self._create_project_list_panel()
        self.process_button = QPushButton("Process All Pano")
        self.process_button.setObjectName("processButton")
        
        right_panel_layout.addWidget(project_list_panel, 1)
        right_panel_layout.addWidget(self.process_button)

        # Muat proyek yang ada dari DB saat startup
        self.load_projects_from_db()

    def _create_project_list_panel(self):
        project_panel = QFrame()
        project_panel.setObjectName("projectPanel")
        panel_layout = QVBoxLayout(project_panel)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Pano")
        self.btn_add.setObjectName("addButton")
        self.btn_delete = QPushButton("Delete Pano")
        self.btn_delete.setObjectName("deleteButton")
        self.btn_delete.setEnabled(False) # Nonaktifkan tombol hapus di awal
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        panel_layout.addLayout(btn_layout)
        
        self.list_widget = QListWidget()
        panel_layout.addWidget(self.list_widget)

        # Hubungkan sinyal-sinyal
        self.btn_add.clicked.connect(self.add_new_panorama)
        self.btn_delete.clicked.connect(self.delete_selected_panorama)
        self.list_widget.currentItemChanged.connect(self.on_project_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.rename_selected_project)

        return project_panel

    def load_projects_from_db(self):
        """Mengambil proyek dari DB dan mengisi list widget."""
        self.list_widget.clear()
        projects = self.database_manager.get_all_panorama_projects()
        for project_id, project_name in projects:
            item = QListWidgetItem(project_name)
            # Simpan ID di dalam item untuk referensi nanti
            item.setData(Qt.UserRole, project_id)
            self.list_widget.addItem(item)
        print(f"Loaded {len(projects)} projects from database.")

    def add_new_panorama(self):
        """Handler untuk membuat proyek baru."""
        # Gunakan QInputDialog untuk nama yang lebih fleksibel
        text, ok = QInputDialog.getText(self, "New Panorama Project", "Enter project name:")
        if ok and text:
            new_project_id = self.database_manager.create_new_panorama_project(name=text)
            if new_project_id is not None:
                # Muat ulang semua proyek untuk menjaga konsistensi
                self.load_projects_from_db()
                # Pilih yang baru
                for i in range(self.list_widget.count()):
                    if self.list_widget.item(i).data(Qt.UserRole) == new_project_id:
                        self.list_widget.setCurrentRow(i)
                        break

    def delete_selected_panorama(self):
        """Menghapus proyek yang sedang dipilih."""
        current_item = self.list_widget.currentItem()
        if not current_item:
            return

        project_id = current_item.data(Qt.UserRole)
        project_name = current_item.text()

        reply = QMessageBox.question(self, "Confirm Delete", 
                                     f"Are you sure you want to delete '{project_name}'?\nThis action cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.database_manager.delete_panorama_project(project_id):
                # Hapus item dari UI
                self.list_widget.takeItem(self.list_widget.row(current_item))
                print(f"Project '{project_name}' deleted from UI.")

    def initiate_rename_sequence(self, item_to_rename):
        """Memulai proses rename untuk item yang diberikan."""
        if not item_to_rename:
            return

        project_id = item_to_rename.data(Qt.UserRole)
        old_name = item_to_rename.text()
        
        new_name, ok = QInputDialog.getText(self, "Rename Project", "Enter new name:", text=old_name)

        if ok and new_name and new_name != old_name:
            if self.database_manager.rename_panorama_project(project_id, new_name):
                item_to_rename.setText(new_name) # Perbarui nama di UI
                # Pancarkan sinyal lagi untuk memperbarui judul di panel kiri
                self.project_selection_changed.emit(project_id, new_name)

    def rename_selected_project(self, item):
        """Slot untuk double-click pada item list."""
        self.initiate_rename_sequence(item)

    # === PERUBAHAN BARU: Slot untuk menangani permintaan rename dari luar ===
    @Slot(int, str)
    def handle_rename_request(self, project_id, old_name):
        """Menangani permintaan rename yang datang dari panel kiri."""
        print(f"Right panel received rename request for ID {project_id}")
        # Cari item di list widget yang sesuai dengan ID
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == project_id:
                self.initiate_rename_sequence(item)
                return

    def on_project_selection_changed(self, current_item, previous_item):
        """Memancarkan sinyal saat pilihan proyek berubah."""
        if current_item:
            project_id = current_item.data(Qt.UserRole)
            project_name = current_item.text()
            self.btn_delete.setEnabled(True) # Aktifkan tombol hapus
            print(f"Selection changed. Emitting signal for project: {project_name} (ID: {project_id})")
            self.project_selection_changed.emit(project_id, project_name)
        else:
            self.btn_delete.setEnabled(False) # Nonaktifkan jika tidak ada pilihan
            print("Selection cleared. Emitting signal.")
            self.project_selection_cleared.emit()