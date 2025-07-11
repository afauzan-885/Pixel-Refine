from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QListWidget, QGridLayout, QTabWidget,
    QComboBox, QSlider, QFrame, QScrollArea, QSizePolicy 
)
from PySide6.QtCore import Qt
from UI.enhance_stack.logic.database_manager import DatabaseManager

class PanoramaPage(QMainWindow):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.database_manager = database_manager
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_content = self._create_main_content()
        main_layout.addWidget(main_content)
        
        self.setStyleSheet(self._get_stylesheet())

    def _create_main_content(self):
        """Membuat area konten utama dengan struktur Kiri-Kanan."""
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)

        left_panel = QWidget()
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(0, 0, 0, 0)
        left_panel_layout.setSpacing(10)
        
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(10)

        # --- Mengisi PANEL KIRI ---
        image_display_area = self._create_image_display_area()
        workflow_panel = self._create_workflow_panel()
        workflow_panel.setMaximumHeight(270)
        
        left_panel_layout.addWidget(image_display_area, 3)
        left_panel_layout.addWidget(workflow_panel, 1)
        
        # --- Mengisi PANEL KANAN ---
        project_list_panel = self._create_project_list_panel()
        btn_process = QPushButton("Process All Pano")
        btn_process.setObjectName("processButton")
        
        # === PERUBAHAN: Beri stretch factor agar panel list lebih tinggi ===
        right_panel_layout.addWidget(project_list_panel, 1) # Stretch factor 1
        right_panel_layout.addWidget(btn_process) # Stretch factor 0 (default)

        main_layout.addWidget(left_panel, 3)
        main_layout.addWidget(right_panel, 1)

        return content_widget

    def _create_image_display_area(self):
        """Membuat area grid untuk menampilkan thumbnail gambar."""
        display_container = QFrame()
        display_container.setObjectName("displayContainer")
        container_layout = QVBoxLayout(display_container)
        
        title = QLabel("Project Panorama 1")
        title.setObjectName("sectionTitle")
        container_layout.addWidget(title)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scrollArea")
        
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(10)

        for i in range(36):
            row = i // 9
            col = i % 9
            image_label = QLabel(f"{i + 1}")
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setObjectName("imageThumbnail")
            image_label.setMinimumSize(80, 80)
            grid_layout.addWidget(image_label, row, col)
            
        scroll_area.setWidget(grid_widget)
        container_layout.addWidget(scroll_area)
        
        return display_container

    def _create_project_list_panel(self):
        """Membuat panel di sisi kanan untuk mengelola proyek panorama."""
        project_panel = QFrame()
        project_panel.setObjectName("projectPanel")
        panel_layout = QVBoxLayout(project_panel)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Pano")
        btn_add.setObjectName("addButton")
        btn_delete = QPushButton("Delete Pano")
        btn_delete.setObjectName("deleteButton")
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_delete)
        panel_layout.addLayout(btn_layout)
        
        list_widget = QListWidget()
        for i in range(1, 11):
            list_widget.addItem(f"Panorama {i}")
        panel_layout.addWidget(list_widget)

        return project_panel

    def _create_workflow_panel(self):
        """Membuat panel bawah dengan tab untuk setiap langkah proses."""
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_alignment_tab(), "Align gambar")
        tab_widget.addTab(self._create_projection_tab(), "Projection dan Crop")
        tab_widget.addTab(self._create_blending_tab(), "Blending")
        return tab_widget

    def _create_alignment_tab(self):
        """Membuat konten tab 'Align gambar' yang lebih rapi."""
        tab_content = QWidget()
        main_layout = QVBoxLayout(tab_content)
        # === PERUBAHAN: Padding dikurangi ===
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

    def _create_projection_tab(self):
        """Membuat konten tab 'Projection dan Crop' yang lebih rapi."""
        tab_content = QWidget()
        main_layout = QVBoxLayout(tab_content)
        # === PERUBAHAN: Padding dikurangi ===
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
        
    def _create_blending_tab(self):
        """Membuat konten tab 'Blending' yang lebih rapi."""
        tab_content = QWidget()
        main_layout = QVBoxLayout(tab_content)
        # === PERUBAHAN: Padding dikurangi ===
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
        
    def _get_stylesheet(self):
        """Mengembalikan QSS untuk styling aplikasi."""
        return """
            /* === PERUBAHAN: Latar belakang utama sedikit lebih lembut === */
            QMainWindow, QWidget {
                background-color: #F5F8FA;
            }
            * {
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 10pt;
                border: none; /* Menghilangkan border default */
            }
            #sectionTitle {
                font-size: 14pt;
                font-weight: bold;
                color: #333;
                margin-bottom: 5px;
            }
            /* === PERUBAHAN: Desain Card Modern dengan Shadow === */
            #displayContainer, #projectPanel, QTabWidget::pane {
                background-color: #FFFFFF;
                border-radius: 8px;
                /* Menghapus border dan menggantinya dengan shadow halus */
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            }
            QTabWidget::pane {
                 border-top-left-radius: 0;
            }
            #scrollArea {
                background-color: transparent;
            }
            #imageThumbnail {
                border: 1px solid #E8EDF2;
                background-color: #F8F9FA;
                border-radius: 4px;
                font-size: 14pt;
                font-weight: bold;
                color: #B0B0B0;
            }
            /* === PERUBAHAN: Padding pada project panel dikurangi === */
            #projectPanel {
                padding: 5px;
            }
            QListWidget {
                border: 1px solid #E8EDF2;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #E7F5FE;
                color: #005A82;
                border-radius: 3px;
                border: 1px solid #BCE3F9;
            }
            QPushButton {
                padding: 8px 12px;
                border: 1px solid #DCDCDC;
                border-radius: 5px;
                background-color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #F8F9FA;
                border-color: #CCCCCC;
            }
            QPushButton:pressed {
                background-color: #F0F2F5;
            }
            QPushButton#addButton, QPushButton#processButton {
                background-color: #2ECC71;
                color: white;
                font-weight: bold;
            }
            QPushButton#addButton:hover, QPushButton#processButton:hover {
                background-color: #28B463;
            }
            QPushButton#deleteButton {
                background-color: #E74C3C;
                color: white;
                font-weight: bold;
            }
            QPushButton#deleteButton:hover {
                background-color: #C0392B;
            }
            QTabBar::tab {
                background: transparent;
                border-bottom: 3px solid transparent; 
                padding: 6px 10px;
                margin-right: 5px;
                color: #555;
            }
            QTabBar::tab:selected {
                font-weight: bold;
                color: #005A82;
                border-bottom: 3px solid #0078D4;
            }
            QTabBar::tab:!selected:hover {
                color: #222;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #DCDCDC;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #0078D4;
            }
            QComboBox::drop-down {
                border: none;
            }
            QSlider::groove:horizontal {
                border: 1px solid #E0E0E0;
                background: #F0F2F5;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #0078D4;
                border: 2px solid white;
                width: 16px;
                margin: -8px 0; 
                border-radius: 10px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.2);
            }
        """