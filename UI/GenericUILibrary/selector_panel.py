from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, 
    QListWidget, QListWidgetItem, QAbstractItemView, QInputDialog, QFrame
)
from PySide6.QtCore import Qt, Signal

class SelectorPanel(QWidget):
    item_selected = Signal(str, str)
    selection_cleared = Signal()
    add_requested = Signal(str)
    delete_requested = Signal(list)
    action_requested = Signal()

    def __init__(self, title="Items", action_btn_text="Process", parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # --- 1. Panel Frame (Container List) ---
        # Ini meniru struktur lama agar border/background sesuai style
        self.list_frame = QFrame()
        self.list_frame.setObjectName("projectPanel") # <--- ID PENTING
        
        frame_layout = QVBoxLayout(self.list_frame)

        # Tombol Add/Delete
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Pano")
        self.btn_add.setObjectName("addButton")       # <--- ID PENTING
        
        self.btn_del = QPushButton("Delete Pano")
        self.btn_del.setObjectName("deleteButton")    # <--- ID PENTING
        self.btn_del.setEnabled(False)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_del)
        frame_layout.addLayout(btn_layout)

        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # Style border list seringkali diatur di stylesheet global
        frame_layout.addWidget(self.list_widget)

        layout.addWidget(self.list_frame, 1)

        # --- 2. Main Action Button ---
        self.btn_action = QPushButton(action_btn_text)
        self.btn_action.setObjectName("processButton") # <--- ID PENTING (Tombol besar di bawah)
        self.btn_action.setFixedHeight(40)
        layout.addWidget(self.btn_action)

        # Connect
        self.btn_add.clicked.connect(self._handle_add)
        self.btn_del.clicked.connect(self._handle_delete)
        self.btn_action.clicked.connect(self.action_requested.emit)
        self.list_widget.itemSelectionChanged.connect(self._handle_selection)

    # ... (Method add_item, remove_item, _handle_* sama seperti sebelumnya) ...
    def add_item(self, item_id, label):
        item = QListWidgetItem(label)
        item.setData(Qt.UserRole, item_id)
        self.list_widget.addItem(item)

    def remove_item(self, item_id):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == item_id:
                self.list_widget.takeItem(i)
                break

    def _handle_add(self):
        text, ok = QInputDialog.getText(self, "New Item", "Name:")
        if ok and text: self.add_requested.emit(text)

    def _handle_delete(self):
        ids = [item.data(Qt.UserRole) for item in self.list_widget.selectedItems()]
        if ids: self.delete_requested.emit(ids)

    def _handle_selection(self):
        selected = self.list_widget.selectedItems()
        self.btn_del.setEnabled(len(selected) > 0)
        if len(selected) == 1:
            self.item_selected.emit(selected[0].data(Qt.UserRole), selected[0].text())
        else:
            self.selection_cleared.emit()