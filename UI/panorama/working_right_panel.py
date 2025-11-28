from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QPushButton, QHBoxLayout, 
    QListWidget, QInputDialog, QListWidgetItem, QAbstractItemView, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from UI.panorama.logic.BatchProcessPano import BatchProcessDialog

class WorkingRightPanel(QWidget):
    """
    Panel Kanan: Daftar item. 
    Menggunakan Mock Data (ListWidget) menggantikan Database.
    """
    project_selection_changed = Signal(str, str) # id (dummy), name
    project_selection_cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # --- List Panel ---
        self.list_panel = self._create_list_panel()
        
        # --- Process Button ---
        self.process_button = QPushButton("Batch Process UI")
        self.process_button.clicked.connect(self._show_batch_dialog)

        layout.addWidget(self.list_panel, 1)
        layout.addWidget(self.process_button)
        
        # Load Dummy Data
        self._load_dummy_data()

    def _create_list_panel(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Item")
        self.btn_delete = QPushButton("Delete Item")
        self.btn_delete.setEnabled(False)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        
        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.list_widget)
        
        # Signals
        self.btn_add.clicked.connect(self._add_item_ui)
        self.btn_delete.clicked.connect(self._delete_item_ui)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_change)
        
        return frame

    def _load_dummy_data(self):
        """Mengisi list dengan data dummy untuk preview UI."""
        for i in range(1, 6):
            item = QListWidgetItem(f"Project Demo {i}")
            item.setData(Qt.UserRole, str(i)) # Dummy ID
            self.list_widget.addItem(item)

    def _add_item_ui(self):
        text, ok = QInputDialog.getText(self, "New Item", "Enter name:")
        if ok and text:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, "new_id")
            self.list_widget.addItem(item)
            self.list_widget.setCurrentItem(item)

    def _delete_item_ui(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def _on_selection_change(self):
        selected = self.list_widget.selectedItems()
        self.btn_delete.setEnabled(len(selected) > 0)
        
        if len(selected) == 1:
            item = selected[0]
            self.project_selection_changed.emit(item.data(Qt.UserRole), item.text())
        else:
            self.project_selection_cleared.emit()

    def _show_batch_dialog(self):
        # Ambil nama project dari list saja
        projects = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            projects.append((item.data(Qt.UserRole), item.text()))
            
        dialog = BatchProcessDialog(projects, self)
        dialog.exec()