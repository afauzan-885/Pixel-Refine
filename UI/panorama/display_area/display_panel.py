from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QStackedWidget, QScrollArea, QFrame, QGridLayout, QFileDialog
)

from UI.panorama.display_area.display_thumbnail import ThumbnailWidget
from UI.panorama.logic.processing_view import ProcessingView

class DisplayPanel(QWidget):
    """
    Panel Tengah: Menampilkan Grid, Loading, atau Result.
    Thumbnail loader diganti dengan Placeholder.
    """
    back_to_grid_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.show_empty_state()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Header ---
        header = QHBoxLayout()
        self.title_label = QLabel("No Selection")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.btn_import = QPushButton("Import Mock Images")
        self.btn_back = QPushButton("Back to Grid")
        self.btn_back.setVisible(False)
        self.btn_back.clicked.connect(self.back_to_grid_requested.emit)
        self.btn_import.clicked.connect(self._mock_import_images)
        
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.btn_back)
        header.addWidget(self.btn_import)
        
        # --- Stacked Views ---
        self.stack = QStackedWidget()
        
        # View 1: Grid Area
        self.grid_area = QScrollArea()
        self.grid_area.setWidgetResizable(True)
        self.grid_content = QWidget()
        self.grid_layout = QGridLayout(self.grid_content)
        self.grid_area.setWidget(self.grid_content)
        
        # View 2: Processing
        self.process_view = ProcessingView()
        
        # View 3: Result Placeholder
        self.result_label = QLabel("Result Preview (Placeholder)")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("background-color: #222; color: #888; font-size: 20px;")

        self.stack.addWidget(self.grid_area)
        self.stack.addWidget(self.process_view)
        self.stack.addWidget(self.result_label)

        layout.addLayout(header)
        layout.addWidget(self.stack)

    # --- Public Slots ---

    def set_project_view(self, name):
        self.title_label.setText(name)
        self.btn_import.setVisible(True)
        self.show_grid_view()
        # Isi grid dengan dummy jika kosong
        if self.grid_layout.count() == 0:
            self._populate_dummy_grid()

    def show_empty_state(self):
        self.title_label.setText("Please Select an Item")
        self.btn_import.setVisible(False)
        self._clear_grid()
        self.show_grid_view()

    def show_grid_view(self):
        self.stack.setCurrentWidget(self.grid_area)
        self.btn_back.setVisible(False)
        self.btn_import.setVisible(True)

    def show_processing_view(self, text):
        self.process_view.update_progress(text, 50) # Visual statis
        self.stack.setCurrentWidget(self.process_view)
        self.btn_back.setVisible(False)
        self.btn_import.setVisible(False)

    def show_preview_result(self):
        self.stack.setCurrentWidget(self.result_label)
        self.btn_back.setVisible(True)
        self.btn_import.setVisible(False)

    # --- Helpers ---

    def _mock_import_images(self):
        """Simulasi menambah gambar ke grid."""
        for i in range(3):
            self._add_thumbnail(f"Mock Img {self.grid_layout.count()}")

    def _add_thumbnail(self, name):
        # Gunakan widget thumbnail yang sudah ada (UI only)
        # Pass path dummy
        thumb = ThumbnailWidget("dummy_path") 
        # Kita set text manual karena tidak ada image loader
        thumb.image_label.setText(name) 
        
        count = self.grid_layout.count()
        row, col = divmod(count, 4)
        self.grid_layout.addWidget(thumb, row, col)

    def _populate_dummy_grid(self):
        self._clear_grid()
        for i in range(5):
            self._add_thumbnail(f"Img {i+1}")

    def _clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()