from PySide6.QtWidgets import (
    QHBoxLayout,
    QProgressBar,
    QPushButton,
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Qt

from pixel_refine_desktop.enhance_stack.core.logic.database_manager import (
    DatabaseManager,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from pixel_refine_desktop.enhance_stack.components.single_page.left_panel import (
    LeftPanel,
)
from pixel_refine_desktop.enhance_stack.components.single_page.right_panel import (
    RightPanel,
)
from pixel_refine_desktop.enhance_stack.controllers.batch_page_controller import (
    BatchPageController,
)


def setup_main_layout(layout_instance, database_manager: DatabaseManager):
    """
    Membuat layout utama dengan Workspace (Kiri) dan Batch List (Kanan).
    Menginisialisasi Controller dan menghubungkan sinyal antar panel.
    """
    layout_instance.single_page_layout = QHBoxLayout()

    # Init Controller (Backend Logic)
    layout_instance.controller = BatchPageController(database_manager.db_path)

    # Init UI Panels
    # LeftPanel class = Workspace logic (image grid + workflow settings)
    # RightPanel class = Batch List logic (batch management)
    layout_instance.workspace_panel = LeftPanel(layout_instance.controller)
    layout_instance.batch_panel = RightPanel(layout_instance.controller)

    # Connect Interactions
    # Saat batch dipilih di panel batch -> load di workspace
    layout_instance.batch_panel.batch_selected.connect(
        lambda batch_id: _load_batch_content(layout_instance, batch_id)
    )

    # Setup Layout
    # Workspace (LeftPanel logic) di KIRI (Stretch 4)
    layout_instance.single_page_layout.addWidget(layout_instance.workspace_panel, 4)

    # Batch Panel (RightPanel logic) di KANAN (Stretch 1)
    layout_instance.single_page_layout.addWidget(layout_instance.batch_panel, 1)

    layout_instance.layout.addLayout(layout_instance.single_page_layout)

    # Connect Process Signal from Workspace to Logic
    layout_instance.workspace_panel.process_requested.connect(
        lambda _: layout_instance.single_process_algorithm()
    )


def _load_batch_content(layout_instance, batch_id):
    """Helper to load batch content into workspace panel."""
    batch = layout_instance.controller.get_batch(batch_id)
    if batch:
        layout_instance.workspace_panel.load_batch(batch_id, batch.images)


def setup_signals(layout_instance):
    """Menghubungkan sinyal-sinyal tambahan jika diperlukan."""
    # Process Button dihandle via process_requested signal di setup_main_layout

    if hasattr(layout_instance, "save_as_button"):
        layout_instance.save_as_button.clicked.connect(layout_instance.save_image)
