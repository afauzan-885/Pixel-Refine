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
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.left_panel import (
    LeftPanel,
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.right_panel import (
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

    # Set right_panel reference di display_panel untuk "New Batch" button handler
    layout_instance.workspace_panel.display_panel.right_panel = layout_instance.batch_panel

    # Connect Interactions
    # Saat batch dipilih di panel batch -> load di workspace
    layout_instance.batch_panel.batch_selected.connect(
        lambda batch_id: _load_batch_content(layout_instance, batch_id)
    )
    
    # Saat batch deselect -> clear workspace display
    layout_instance.batch_panel.batch_selection_cleared.connect(
        layout_instance.workspace_panel.clear_display
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

    # Connect Image Import Signal from DisplayPanel (Drag & Drop)
    layout_instance.workspace_panel.imagesDropped.connect(
        lambda paths: _handle_images_imported(layout_instance, paths)
    )


def _load_batch_content(layout_instance, batch_id):
    """Helper to load batch content into workspace panel."""
    batch = layout_instance.controller.get_batch(batch_id)
    if batch:
        layout_instance.workspace_panel.load_batch(batch_id, batch.images)


def _handle_images_imported(layout_instance, file_paths):
    """
    Handle imported images dari drag & drop.
    Add images ke current batch di database.
    
    Args:
        layout_instance: BatchPageV2Layout instance
        file_paths: List of image file paths dari drop
    """
    if not file_paths:
        return
    
    # Get current batch ID dari display panel
    current_batch_id = layout_instance.workspace_panel.display_panel.current_batch_id
    if not current_batch_id:
        QMessageBox.warning(
            layout_instance,
            "No Batch Selected",
            "Please select a batch first before adding images."
        )
        return
    
    try:
        # Add images ke batch di database
        count = layout_instance.controller.add_images_to_batch(current_batch_id, file_paths)
        if count > 0:
            # Reload batch untuk display updated images
            batch = layout_instance.controller.get_batch(current_batch_id)
            if batch:
                layout_instance.workspace_panel.load_batch(current_batch_id, batch.images)
            
            QMessageBox.information(
                layout_instance,
                "Images Added",
                f"Successfully added {count} image(s) to batch."
            )
        else:
            QMessageBox.warning(
                layout_instance,
                "No Images Added",
                "Could not add images. They may already exist in the batch."
            )
    except Exception as e:
        QMessageBox.critical(
            layout_instance,
            "Database Error",
            f"Failed to add images to batch: {str(e)}"
        )


def setup_signals(layout_instance):
    """Menghubungkan sinyal-sinyal tambahan jika diperlukan."""
    # Process Button dihandle via process_requested signal di setup_main_layout

    if hasattr(layout_instance, "save_as_button"):
        layout_instance.save_as_button.clicked.connect(layout_instance.save_image)
