"""
ReconstructionRightPanel - Right panel untuk 3D Reconstruction.
Subclass of WorkspaceRightPanel.

Menggunakan workplace framework untuk list + settings sidebar yang identik
dengan enhance_stack tetapi konten spesifik 3D.
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Signal

from resources.GenericUILibrary import (
    ListGroup,
    Button,
    FormGroup,
    FeatureCard,
)

from pixel_refine_desktop.workplace.workspace_right_panel import WorkspaceRightPanel


class ReconstructionRightPanel(WorkspaceRightPanel):
    """
    Right panel spesifik untuk 3D Reconstruction.
    Sidebar berisi daftar project 3D dan pengaturan rekonstruksi.
    """

    # Override signals dengan nama yang lebih semantik
    project_selected = Signal(int)  # Emits project_id
    project_selection_cleared = Signal()

    def __init__(self, controller=None, left_panel=None, store=None):
        # FeatureCard references for 3D-specific settings
        self.densify_card = None
        self.meshing_card = None
        self.texturing_card = None

        super().__init__(controller, left_panel, store)

    def _load_items(self):
        """Load 3D projects dari controller/database ke ListGroup."""
        if not self.controller:
            return

        self.list_group.clear()
        # TODO: Load projects dari controller
        # projects = self.controller.get_all_projects()
        # for project in projects:
        #     self.list_group.add_item(project.name, value=project.id)

    def _create_settings_content(self):
        """Populate settings area dengan 3D reconstruction parameter cards."""

        # ============================
        # Densification Feature Card
        # ============================
        densify_options = [
            "Dense Stereo",
            "Patch Match MVS",
            "SGM Stereo",
        ]
        self.densify_card = FeatureCard(
            "DENSIFICATION",
            "Method untuk menghasilkan dense point cloud dari sparse reconstruction.",
            densify_options,
            "Dense Stereo",
            self,
        )
        self.densify_card.value_changed.connect(self._on_settings_changed)
        self.scroll_content_layout.addWidget(self.densify_card)

        # ============================
        # Meshing Feature Card
        # ============================
        meshing_options = [
            "Poisson Reconstruction",
            "Delaunay Triangulation",
            "Marching Cubes",
        ]
        self.meshing_card = FeatureCard(
            "MESHING",
            "Method untuk mengkonversi point cloud menjadi mesh 3D.",
            meshing_options,
            "Poisson Reconstruction",
            self,
        )
        self.meshing_card.value_changed.connect(self._on_settings_changed)
        self.scroll_content_layout.addWidget(self.meshing_card)

        # ============================
        # Texturing Feature Card
        # ============================
        texturing_options = [
            "UV Projection",
            "Multi-View Texturing",
            "No Texturing",
        ]
        self.texturing_card = FeatureCard(
            "TEXTURING",
            "Method untuk mengaplikasikan tekstur pada mesh 3D.",
            texturing_options,
            "UV Projection",
            self,
        )
        self.texturing_card.value_changed.connect(self._on_settings_changed)
        self.scroll_content_layout.addWidget(self.texturing_card)

    def _handle_selection(self, selected_values):
        """Handle project selection change."""
        if not selected_values:
            self.selection_cleared.emit()
            self.project_selection_cleared.emit()
            self.settings_container.setFixedHeight(0)
            self.settings_container.hide()
            return

        project_id = selected_values[0]
        self.current_item_id = project_id

        # Show settings container
        self.settings_container.show()
        target_h = self._calculate_settings_target_h()
        self.settings_container.setFixedHeight(target_h)

        # Emit selection
        self.item_selected.emit(project_id)
        self.project_selected.emit(project_id)

        # Load project-specific settings
        self._load_project_settings(project_id)

    def _load_project_settings(self, project_id):
        """Load settings untuk specific project dari store."""
        self.current_item_id = project_id

        if self.store:
            self.set_scope(str(project_id))
            self.on_store_changed(None, self.get_data())

    def _on_settings_changed(self):
        """Emit current settings dan save ke store."""
        settings = self.get_current_settings()
        self.settings_changed.emit(settings)

    def get_current_settings(self) -> dict:
        """Get current reconstruction settings."""
        return {
            "densification": self.densify_card.get_value() if self.densify_card else "Dense Stereo",
            "meshing": self.meshing_card.get_value() if self.meshing_card else "Poisson Reconstruction",
            "texturing": self.texturing_card.get_value() if self.texturing_card else "UV Projection",
        }

    # === Implementasi abstract/template methods ===

    def _create_item(self, name: str):
        """Create project baru."""
        if not self.controller:
            return None
        # TODO: Implementasi create 3D project
        # return self.controller.create_project(name)
        return None

    def _delete_item(self, item_id):
        """Delete project."""
        if not self.controller:
            return
        # TODO: Implementasi delete 3D project
        # self.controller.delete_project(item_id)

    def _get_all_items(self) -> list:
        """Get all 3D projects."""
        if not self.controller:
            return []
        # TODO: return self.controller.get_all_projects()
        return []

    def _get_item_name(self, item) -> str:
        """Get name dari project object."""
        return getattr(item, 'name', str(item))

    def _should_show_process_all(self) -> bool:
        """Show process all jika ada project dengan images."""
        if not self.controller:
            return False
        # TODO: Cek apakah ada project dengan images
        return False

    def _on_process_all_clicked(self):
        """Handle process all button click."""
        # TODO: Implementasi batch 3D reconstruction
        pass

    # === Theme & Language ===

    def retranslate_ui(self):
        """Update text saat language berubah."""
        if hasattr(self, "densify_card") and self.densify_card:
            self.densify_card.title_lbl.setText("DENSIFICATION")
        if hasattr(self, "meshing_card") and self.meshing_card:
            self.meshing_card.title_lbl.setText("MESHING")
        if hasattr(self, "texturing_card") and self.texturing_card:
            self.texturing_card.title_lbl.setText("TEXTURING")
        self.update_theme()

    def update_theme(self):
        """Update styles saat theme berubah."""
        super().update_theme()
        if hasattr(self, "densify_card") and self.densify_card and hasattr(self.densify_card, "update_theme"):
            self.densify_card.update_theme()
        if hasattr(self, "meshing_card") and self.meshing_card and hasattr(self.meshing_card, "update_theme"):
            self.meshing_card.update_theme()
        if hasattr(self, "texturing_card") and self.texturing_card and hasattr(self.texturing_card, "update_theme"):
            self.texturing_card.update_theme()
