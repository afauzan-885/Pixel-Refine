from __future__ import annotations
import os
from PySide6.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from pixel_refine_desktop.ui.resources.GenericUILibrary.store import get_store
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Use Any for layout_instance to avoid circularity noise
    pass


from pixel_refine_desktop.enhance_stack.core.logic.database_manager import (
    DatabaseManager,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.left_panel import (
    LeftPanel,
)
from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import (
    BatchImageImportThreading,
)
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.right_panel import (
    RightPanel,
)
from pixel_refine_desktop.enhance_stack.controllers.batch_page_controller import (
    BatchPageController,
)
from pixel_refine_desktop.enhance_stack.core.logic.process_manager import ProcessManager


def setup_main_layout(layout_instance: Any, database_manager: DatabaseManager):
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
    layout_instance.workspace_panel = LeftPanel(
        layout_instance.controller, store=layout_instance.store
    )
    layout_instance.batch_panel = RightPanel(
        layout_instance.controller,
        left_panel=layout_instance.workspace_panel,
        store=layout_instance.store,
    )

    # Set right_panel reference di display_panel untuk "New Batch" button handler
    # We use Any type to avoid assignment errors
    layout_instance.workspace_panel.display_panel.right_panel = (
        layout_instance.batch_panel
    )

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

    layout_instance.main_layout.addLayout(layout_instance.single_page_layout)

    # Connect Process Signal from Workspace to Logic
    layout_instance.workspace_panel.process_requested.connect(
        lambda _: layout_instance.single_process_algorithm()
    )

    # Connect Image Import Signal from DisplayPanel (Drag & Drop)
    layout_instance.workspace_panel.imagesDropped.connect(
        lambda paths: _handle_images_imported(layout_instance, paths)
    )

    # Initial Sync: Pastikan AlgorithmPanel sesuai dengan pilihan default di RightPanel
    initial_settings = layout_instance.batch_panel.get_current_settings()
    layout_instance.workspace_panel.algorithm_panel.update_settings(initial_settings)

    # Connect Page Navigation (Sidebar -> Main Window)
    if hasattr(layout_instance, "page_changed"):
        layout_instance.workspace_panel.page_changed.connect(
            layout_instance.page_changed
        )


def _load_batch_content(layout_instance, batch_id):
    """Helper to load batch content into workspace panel."""
    # We no longer cancel batch_import here to allow background completion
    # ProcessManager.instance().cancel_context("batch_import")

    batch = layout_instance.controller.get_batch(batch_id)
    if batch:
        layout_instance.workspace_panel.load_batch(batch_id, batch.images, batch.name)


def _handle_images_imported(layout_instance, file_paths):
    """
    Delegates image import handling to ImportManager.
    """
    display_panel = layout_instance.workspace_panel.display_panel
    current_batch_id = display_panel.current_batch_id

    if not current_batch_id:
        QMessageBox.warning(
            layout_instance,
            "No Batch Selected",
            "Please select a batch first before adding images.",
        )
        return

    try:
        # Use ImportManager's logic instead of manual threading setup here
        layout_instance.import_worker = (
            display_panel.import_manager.handle_batch_import(
                controller=layout_instance.controller,
                database_manager=layout_instance.database_manager,
                file_paths=file_paths,
                batch_id=current_batch_id,
            )
        )

        # Connect specific UI elements if needed (e.g. algorithm panel progress bar)
        if hasattr(layout_instance.workspace_panel.algorithm_panel, "progress_bar"):
            prog_bar = layout_instance.workspace_panel.algorithm_panel.progress_bar
            prog_bar.setVisible(True)
            layout_instance.import_worker.progress_signal.connect(
                lambda val, left: prog_bar.setValue(val)
            )

            # Hide progress bar when done
            layout_instance.import_worker.completion_signal.connect(
                lambda _: prog_bar.setVisible(False)
            )

    except Exception as e:
        QMessageBox.critical(
            layout_instance,
            "Import Error",
            f"Failed to start background import: {str(e)}",
        )


def setup_signals(layout_instance):
    """Menghubungkan sinyal-sinyal tambahan jika diperlukan."""
    # Process Button dihandle via process_requested signal di setup_main_layout

    if hasattr(layout_instance, "save_as_button"):
        layout_instance.save_as_button.clicked.connect(layout_instance.save_image)


class BatchPageV2Layout(QWidget):
    """
    V2 Layout Wrapper for Batch Page.
    Uses setup_main_layout to build the UI.
    """

    page_changed = Signal(int)  # Forward global navigation

    def __init__(self, database_manager):
        super().__init__()
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Will be populated by setup_main_layout
        self.single_page_layout = None
        self.controller = None
        self.workspace_panel = None
        self.batch_panel = None

        # Initialize Centralized Data Store
        self.store = get_store()

        # Bind to settings file
        json_path = os.path.join("database", "align", "batch_parameter.json")
        self.store.bind_to_file(json_path)

        # Build UI
        setup_main_layout(self, database_manager)
        setup_signals(self)
