# UI/enhance_stack/components/single_page_layout/page_layout.py
from PyQt6.QtWidgets import QHBoxLayout, QProgressBar, QPushButton, QGraphicsScene, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
# --- Hapus import update_preview_panel ---
# from UI.enhance_stack.components.single_page_layout.image_preview_handler import update_preview_panel
# --- Import Zoomable dan komponen lain yang diperlukan ---
from UI.enhance_stack.logic.Zoomable_Handler import Zoomable
from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.resources.stylesheet import stylesheet
from UI.settings.General.Language import language_config
from UI.enhance_stack.components.single_page_layout.left_panel import LeftPanel
from UI.enhance_stack.components.single_page_layout.right_panel import RightPanel

def setup_main_layout(layout_instance, database_manager: DatabaseManager):
    """Membuat layout utama dengan LeftPanel dan RightPanel."""
    layout_instance.single_page_layout = QHBoxLayout()

    # --- Asumsi LeftPanel dan RightPanel ada ---
    layout_instance.left_panel = LeftPanel()
    layout_instance.right_panel = RightPanel(database_manager)
    # -----------------------------------------

    # --- Pindahkan koneksi sinyal previewImageRequested ke SinglePageLayout.__init__ ---
    # layout_instance.right_panel.previewImageRequested.connect(lambda paths: update_preview_panel(layout_instance, paths))
    # --------------------------------------------------------------------------------

    layout_instance.single_page_layout.addWidget(layout_instance.left_panel, 3)
    layout_instance.single_page_layout.addWidget(layout_instance.right_panel, 2)
    layout_instance.layout.addLayout(layout_instance.single_page_layout)

def setup_progress_section(layout_instance):
    """Membuat layout untuk progress bar dan tombol."""
    layout_instance.progress_bar = QProgressBar()
    layout_instance.progress_bar.setRange(0, 100)
    layout_instance.progress_bar.setValue(0)
    layout_instance.progress_bar.setStyleSheet(stylesheet.PROGRESS_BAR)

    layout_instance.process_button = QPushButton(language_config.PROGRESS_SECTION_PROCESS_BUTTON_TEXT)
    layout_instance.process_button.setStyleSheet(stylesheet.PROCESS_BUTTON)

    layout_instance.save_as_button = QPushButton(language_config.PROGRESS_SECTION_SAVE_BUTTON_TEXT)
    layout_instance.save_as_button.setStyleSheet(stylesheet.SAVE_AS_BUTTON)

    layout_instance.progress_layout = QHBoxLayout()
    layout_instance.progress_layout.setContentsMargins(0, 0, 0, 0)
    layout_instance.progress_layout.addWidget(layout_instance.progress_bar, 3)
    layout_instance.progress_layout.addWidget(layout_instance.process_button, 1)
    layout_instance.progress_layout.addWidget(layout_instance.save_as_button, 1)

    layout_instance.layout.addLayout(layout_instance.progress_layout)

def setup_preview_panel(layout_instance):
    """
    Membuat panel pratinjau (scene dan view), lalu menambahkannya ke layout
    di dalam LeftPanel.
    """
    layout_instance.preview_scene = QGraphicsScene(layout_instance) # Set parent
    layout_instance.preview_view = Zoomable(layout_instance.preview_scene, layout_instance) # Set parent

    # Style dasar view (bisa juga diatur di dalam Zoomable.__init__)
    layout_instance.preview_view.setStyleSheet("background-color: #f0f0f0; margin-left: 5px; border: none")

    # Tambahkan view ke layout di LeftPanel
    # --- Pastikan left_panel dan preview_panel_widget ada dan punya layout ---
    if hasattr(layout_instance, 'left_panel') and hasattr(layout_instance.left_panel, 'preview_panel_widget'):
        preview_panel = layout_instance.left_panel.preview_panel_widget
        # Cek apakah layout sudah ada, jika belum, buat
        preview_layout = preview_panel.layout()
        if not preview_layout:
            preview_layout = QVBoxLayout(preview_panel) # Atau QHBoxLayout sesuai kebutuhan
            preview_layout.setContentsMargins(0,0,0,0) # Hapus margin jika perlu
            preview_panel.setLayout(preview_layout)

        # Hapus widget lama di layout preview sebelum menambah baru
        while preview_layout.count():
            item = preview_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater() # Hapus widget lama

        # Tambahkan view baru
        preview_layout.addWidget(layout_instance.preview_view)
        
    else:
        pass

def setup_signals(layout_instance):
    """Menghubungkan tombol proses dan simpan."""
    # Koneksi sinyal preview dipindah ke SinglePageLayout.__init__
    if hasattr(layout_instance, 'process_button'):
        layout_instance.process_button.clicked.connect(layout_instance.process_clicked)
        layout_instance.process_clicked.connect(layout_instance.single_process_algorithm)
    else:
        pass
    
    if hasattr(layout_instance, 'save_as_button'):
        layout_instance.save_as_button.clicked.connect(layout_instance.save_image)
    else:
        pass