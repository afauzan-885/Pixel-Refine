"""
ReconstructionLeftPanel - Left panel untuk 3D Reconstruction.
Subclass of WorkspaceLeftPanel.
"""

from pixel_refine_desktop.workplace.workspace_left_panel import WorkspaceLeftPanel
from .reconstruction_display_panel import ReconstructionDisplayPanel
from .reconstruction_parameter_panel import ReconstructionParameterPanel


class ReconstructionLeftPanel(WorkspaceLeftPanel):
    """
    Left panel spesifik untuk 3D Reconstruction.
    Display panel menampilkan input images / point clouds.
    Parameter panel menampilkan pengaturan rekonstruksi 3D.
    """

    def __init__(self, controller=None, store=None):
        super().__init__(controller, store)

    def _create_display_panel(self):
        return ReconstructionDisplayPanel(controller=self.controller)

    def _create_parameter_panel(self):
        return ReconstructionParameterPanel(
            controller=self.controller, store=self.store
        )
