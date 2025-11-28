from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QFileDialog
)
from PySide6.QtGui import QColor
from UI.resources.animation.loading.modern_progress_bar import ModernProgressBar

class BatchProcessDialog(QDialog):
    """
    Dialog Batch: Murni visual. Tidak ada logika thread di baliknya.
    """
    def __init__(self, projects_list, parent=None):
        super().__init__(parent)
        self.projects_list = projects_list
        self.setWindowTitle("Batch Process (UI Demo)")
        self.resize(600, 400)
        self._setup_ui()
        self._populate_table()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Folder Input
        h_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select output folder...")
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(lambda: self.path_edit.setText(QFileDialog.getExistingDirectory(self)))
        h_layout.addWidget(self.path_edit)
        h_layout.addWidget(btn_browse)
        layout.addLayout(h_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Project", "Status", "Details"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Progress
        self.progress = ModernProgressBar()
        layout.addWidget(self.progress)

        # Actions
        btn_layout = QHBoxLayout()
        btn_start = QPushButton("Start (Simulation)")
        btn_start.clicked.connect(self._simulate_process)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_start)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def _populate_table(self):
        self.table.setRowCount(len(self.projects_list))
        for row, (pid, name) in enumerate(self.projects_list):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem("Idle"))

    def _simulate_process(self):
        """Ubah status tabel secara visual saja."""
        self.progress.setValue(50)
        for row in range(self.table.rowCount()):
            self.table.item(row, 1).setText("Processing...")
            self.table.item(row, 1).setBackground(QColor("orange"))