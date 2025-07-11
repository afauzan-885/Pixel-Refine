from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QLabel, QScrollArea, 
    QGridLayout, QTabWidget, QComboBox, QSlider, QHBoxLayout,
    QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Slot, Signal, QEvent
from PySide6.QtGui import QPixmap

class WorkingLeftPanel(QWidget):
    """
    Panel kiri yang dinamis, menampilkan detail proyek,
    menerima drag-n-drop, dan meminta perubahan nama.
    """
    # Sinyal baru untuk meminta penggantian nama
    rename_project_requested = Signal(int, str)

    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        # === PERUBAHAN: Terima dan simpan database manager ===
        self.database_manager = database_manager
        
        left_panel_layout = QVBoxLayout(self)
        left_panel_layout.setContentsMargins(0, 0, 0, 0)
        left_panel_layout.setSpacing(10)

        display_area = self._create_display_area()
        workflow_panel = self.workflow_panel()
        workflow_panel.setMaximumHeight(270)
        
        left_panel_layout.addWidget(display_area, 3)
        left_panel_layout.addWidget(workflow_panel, 1)
        
        self.current_project_id = None
        
        # === PERUBAHAN: Aktifkan Drag and Drop untuk seluruh panel ===
        self.setAcceptDrops(True)

    def _create_display_area(self):
        """Membuat area grid untuk menampilkan thumbnail gambar."""
        display_container = QFrame()
        display_container.setObjectName("displayContainer")
        container_layout = QVBoxLayout(display_container)
        
        self.title_label = QLabel("No Project Selected")
        self.title_label.setObjectName("sectionTitle")
        # === PERUBAHAN: Install event filter untuk mendeteksi double-click ===
        self.title_label.installEventFilter(self)
        
        self.import_button = QPushButton("Import Images")
        self.import_button.setObjectName("importButton") # Beri nama untuk styling jika perlu
        self.import_button.setEnabled(False)
        self.import_button.clicked.connect(self.import_images)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.import_button)

        container_layout.addLayout(header_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scrollArea")
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            
        scroll_area.setWidget(self.grid_widget)
        container_layout.addWidget(scroll_area)
        
        return display_container

    # === PERUBAHAN: Implementasi Event Filter untuk rename ===
    def eventFilter(self, watched_object, event):
        # Cek jika objek yang di-double-click adalah title_label
        if watched_object == self.title_label and event.type() == QEvent.MouseButtonDblClick:
            if self.current_project_id:
                print(f"Double-click detected on title. Emitting rename request for project ID {self.current_project_id}.")
                # Pancarkan sinyal bahwa ada permintaan rename
                self.rename_project_requested.emit(self.current_project_id, self.title_label.text())
                return True # Event sudah ditangani
        
        # Kembalikan ke handler default untuk event lain
        return super().eventFilter(watched_object, event)
        
    # === PERUBAHAN: Implementasi Drag and Drop Events ===
    def dragEnterEvent(self, event):
        # Cek jika data yang di-drag berisi URL (file)
        if event.mimeData().hasUrls():
            event.acceptProposedAction() # Terima event ini
        else:
            event.ignore()

    def dropEvent(self, event):
        # Ambil daftar URL dari file yang di-drop
        urls = event.mimeData().urls()
        image_paths = []
        for url in urls:
            if url.isLocalFile():
                # Filter hanya untuk file gambar yang valid
                path = url.toLocalFile()
                if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif')):
                    image_paths.append(path)
        
        if image_paths:
            print(f"Dropped {len(image_paths)} valid image files.")
            # Panggil fungsi yang sama dengan tombol import
            self.process_imported_images(image_paths)
        else:
            print("No valid image files were dropped.")

    def clear_grid(self):
        """Membersihkan semua gambar dari grid."""
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def import_images(self):
        """Membuka file dialog untuk memilih gambar."""
        if not self.current_project_id:
            QMessageBox.warning(self, "No Project", "Please select a project before importing images.")
            return

        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images for Panorama", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tif)")

        if file_paths:
            self.process_imported_images(file_paths)

    def process_imported_images(self, file_paths):
        """Memproses path gambar yang diimpor, menyimpannya ke DB, dan memuat ulang UI."""
        print(f"Processing {len(file_paths)} images for project ID {self.current_project_id}")
        
        # Panggil fungsi database untuk menyimpan path ini
        success = self.database_manager.add_images_to_project(self.current_project_id, file_paths)
        
        if success:
            # Muat ulang grid untuk menampilkan gambar baru
            self.load_images_for_project(self.current_project_id)
        else:
            QMessageBox.critical(self, "Database Error", "Failed to save images to the project.")

    def load_images_for_project(self, project_id):
        """Memuat dan menampilkan gambar untuk proyek yang diberikan (dari DB)."""
        self.clear_grid()
        image_paths = self.database_manager.get_images_for_project(project_id)

        if not image_paths:
            placeholder = QLabel("No images in this project. Drag & drop files here or use the 'Import Images' button.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setWordWrap(True)
            self.grid_layout.addWidget(placeholder, 0, 0, 1, 4) # Span 1 baris, 4 kolom
        else:
            for i, path in enumerate(image_paths):
                row = i // 8 # Tampilkan 8 gambar per baris
                col = i % 8
                
                thumbnail_label = QLabel()
                thumbnail_label.setToolTip(path) # Tampilkan path saat hover
                # Muat gambar dan buat thumbnail
                pixmap = QPixmap(path)
                scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                thumbnail_label.setPixmap(scaled_pixmap)
                thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                thumbnail_label.setFixedSize(110, 110)
                thumbnail_label.setObjectName("imageThumbnail") # Gunakan style yang sama

                self.grid_layout.addWidget(thumbnail_label, row, col)

    @Slot(int, str)
    def update_display_for_project(self, project_id, project_name):
        """Slot yang dipanggil saat proyek baru dipilih."""
        print(f"Slot activated in Left Panel. Updating for: {project_name}")
        self.title_label.setText(project_name)
        self.current_project_id = project_id
        self.import_button.setEnabled(True)
        self.load_images_for_project(project_id)

    @Slot()
    def clear_display(self):
        """Slot yang dipanggil saat tidak ada proyek yang dipilih."""
        print("Slot activated in Left Panel. Clearing display.")
        self.title_label.setText("No Project Selected")
        self.current_project_id = None
        self.import_button.setEnabled(False)
        self.clear_grid()
    
    # ... (fungsi workflow_panel dan tab lainnya tidak berubah)
    def workflow_panel(self):
        """Membuat panel bawah dengan tab untuk setiap langkah proses."""
        tab_widget = QTabWidget()
        tab_widget.addTab(self.alignment_tab(), "Align gambar")
        tab_widget.addTab(self.projection_tab(), "Projection dan Crop")
        tab_widget.addTab(self.blending_tab(), "Blending")
        return tab_widget

    def alignment_tab(self):
        tab_content = QWidget()
        main_layout = QVBoxLayout(tab_content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        main_layout.addWidget(QLabel("Alignment Algorithm:"))
        combo_layout = QHBoxLayout()
        combo_align = QComboBox()
        combo_align.addItems(["AKAZE", "ORB", "SIFT", "BRISK"])
        combo_layout.addWidget(combo_align)
        combo_layout.addStretch()
        main_layout.addLayout(combo_layout)

        main_layout.addSpacing(10)
        main_layout.addWidget(QLabel("Parameter 1:"))
        main_layout.addWidget(QSlider(Qt.Orientation.Horizontal))
        main_layout.addSpacing(5)
        main_layout.addWidget(QLabel("Parameter 2:"))
        main_layout.addWidget(QSlider(Qt.Orientation.Horizontal))
        main_layout.addStretch()
        return tab_content

    def projection_tab(self):
        tab_content = QWidget()
        main_layout = QVBoxLayout(tab_content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(QLabel("Projection Type:"))
        combo_layout = QHBoxLayout()
        combo_proj = QComboBox()
        combo_proj.addItems(["Planar", "Cylindrical", "Spherical", "Fisheye"])
        combo_layout.addWidget(combo_proj)
        combo_layout.addStretch()
        main_layout.addLayout(combo_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(QLabel("Set Region:"))
        button_layout = QHBoxLayout()
        btn_auto = QPushButton("Auto")
        btn_manual = QPushButton("Manual")
        button_layout.addWidget(btn_auto)
        button_layout.addWidget(btn_manual)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        return tab_content
        
    def blending_tab(self):
        tab_content = QWidget()
        main_layout = QVBoxLayout(tab_content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(QLabel("Blending Method:"))
        combo_layout_1 = QHBoxLayout()
        combo_blend = QComboBox()
        combo_blend.addItems(["Multi-band", "Feathering", "No Blending"])
        combo_layout_1.addWidget(combo_blend)
        combo_layout_1.addStretch()
        main_layout.addLayout(combo_layout_1)
        main_layout.addSpacing(10)
        main_layout.addWidget(QLabel("Anti-ghosting:"))
        combo_layout_2 = QHBoxLayout()
        combo_ghost = QComboBox()
        combo_ghost.addItems(["None", "Simple", "Dynamic"])
        combo_layout_2.addWidget(combo_ghost)
        combo_layout_2.addStretch()
        main_layout.addLayout(combo_layout_2)
        main_layout.addStretch()
        return tab_content