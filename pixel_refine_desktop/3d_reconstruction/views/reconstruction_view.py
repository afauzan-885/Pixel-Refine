"""
ReconstructionView - Main view untuk 3D Reconstruction module.
Subclass of WorkspaceView - implementasi spesifik 3D reconstruction.

Menggunakan workplace framework untuk layout yang identik dengan enhance_stack.
"""

from PySide6.QtCore import Signal
from pixel_refine_desktop.workplace.workspace_view import WorkspaceView
from pixel_refine_desktop.workplace.workspace_page_layout import WorkspacePageLayout

from .reconstruction_left_panel import ReconstructionLeftPanel
from .reconstruction_right_panel import ReconstructionRightPanel


class ReconstructionPageLayout(WorkspacePageLayout):
    """
    Page layout untuk 3D Reconstruction.
    Menggunakan workspace framework dengan panel spesifik 3D.
    """

    def __init__(self, controller=None, store=None):
        super().__init__(controller, store)

    def _create_left_panel(self):
        return ReconstructionLeftPanel(controller=self.controller, store=self.store)

    def _create_right_panel(self):
        return ReconstructionRightPanel(
            controller=self.controller,
            left_panel=self.workspace_panel,
            store=self.store,
        )

    def _connect_panel_signals(self):
        """Hubungkan sinyal antar panel 3D reconstruction."""
        # Saat project dipilih di sidebar -> load di workspace
        self.batch_panel.item_selected.connect(self._on_project_selected)
        self.batch_panel.selection_cleared.connect(self.workspace_panel.clear_display)

        # Connect process signal
        self.workspace_panel.process_requested.connect(
            lambda _: self._trigger_reconstruction()
        )

        # Connect page navigation
        self.workspace_panel.page_changed.connect(self.page_changed)

    def _on_project_selected(self, project_id):
        """Load project content ke workspace."""
        # TODO: Implementasi load 3D project content
        pass

    def _trigger_reconstruction(self):
        """Trigger proses rekonstruksi 3D."""
        # TODO: Implementasi 3D reconstruction pipeline
        pass

    def _should_show_right_panel(self) -> bool:
        """Kondisi awal: tampilkan right panel jika ada project."""
        # TODO: Cek apakah ada project di database
        return True


class ReconstructionView(WorkspaceView):
    """
    Main view untuk 3D Reconstruction.
    Menggunakan workspace framework untuk layout yang identik dengan enhance_stack.
    """

    page_changed = Signal(int)

    def __init__(self, db_path: str, parent=None):
        super().__init__(db_path, parent)

    def _create_pages(self):
        """Buat halaman 3D reconstruction."""
        # Single workspace page
        self.reconstruction_page = ReconstructionPageLayout(
            controller=None,  # TODO: Pass controller
            store=None,  # TODO: Pass store
        )
        self.stacked_widget.addWidget(self.reconstruction_page)

    def _set_initial_page(self):
        """Set halaman awal ke reconstruction page."""
        self.stacked_widget.setCurrentWidget(self.reconstruction_page)

    def _connect_page_signals(self):
        """Connect page signals."""
        self.reconstruction_page.page_changed.connect(self.page_changed)
