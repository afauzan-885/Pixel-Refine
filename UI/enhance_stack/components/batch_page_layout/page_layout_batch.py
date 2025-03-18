from PyQt6.QtWidgets import QHBoxLayout, QProgressBar, QPushButton, QGraphicsScene, QGraphicsView
from PyQt6.QtCore import Qt
from UI.enhance_stack.components.single_page_layout.image_preview_handler import update_preview_panel
from UI.resources.stylesheet import stylesheet
from UI.settings.General.Language import language_config 
from UI.enhance_stack.components.single_page_layout.left_panel import LeftPanel
from UI.enhance_stack.components.single_page_layout.right_panel import RightPanel


def setup_main_layout(layout_instance):
    """Membuat layout utama dengan LeftPanel dan RightPanel."""
    layout_instance.single_page_layout = QHBoxLayout()

    layout_instance.left_panel = LeftPanel()
    layout_instance.right_panel = RightPanel()

    layout_instance.right_panel.previewImageRequested.connect(lambda paths: update_preview_panel(layout_instance, paths))

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
    """Membuat panel pratinjau untuk gambar yang di-load."""
    layout_instance.preview_scene = QGraphicsScene()
    layout_instance.preview_view = QGraphicsView(layout_instance.preview_scene)
    layout_instance.preview_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout_instance.preview_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    layout_instance.preview_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    layout_instance.preview_view.setStyleSheet("background-color: #f0f0f0; margin-left: 5px; border: none")
    layout_instance.preview_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    layout_instance.left_panel.preview_panel_widget.layout().addWidget(layout_instance.preview_view)

def setup_signals(layout_instance):
    """Menghubungkan tombol dengan fungsinya."""
    layout_instance.process_button.clicked.connect(layout_instance.process_clicked)
    layout_instance.process_clicked.connect(layout_instance.process_algorithm)
    layout_instance.save_as_button.clicked.connect(layout_instance.save_image)
