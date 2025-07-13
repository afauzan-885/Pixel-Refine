from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PySide6.QtCore import Slot, Signal, QTimer

from UI.panorama.display_area.display_panel import DisplayPanel
from UI.panorama.workflow_area.workflow_panel import WorkflowPanel


class WorkingLeftPanel(QWidget):
    # Sinyal yang diteruskan ke luar (misal ke main window)
    rename_project_requested = Signal(int, str)

    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager

        # --- Variabel State Utama ---
        self.current_project_id = None
        self.projects_exist = False
        self.latest_successful_stage = "grid"

        # --- Setup UI dengan Komponen Baru ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        self.display_panel = DisplayPanel()
        self.workflow_panel = WorkflowPanel()

        main_layout.addWidget(self.display_panel, 3)  # Beri lebih banyak ruang
        main_layout.addWidget(self.workflow_panel, 1)

        self._connect_signals()

    def _connect_signals(self):
        """Menghubungkan sinyal dari anak ke slot di kontroler ini."""
        # Dari DisplayPanel
        self.display_panel.rename_project_requested.connect(self._on_rename_request)
        self.display_panel.images_to_import_selected.connect(self._on_images_imported)
        self.display_panel.images_to_delete_selected.connect(self._on_images_deleted)
        self.display_panel.back_to_grid_requested.connect(self._on_back_to_grid_request)

        # Dari WorkflowPanel
        self.workflow_panel.setting_changed.connect(self._on_workflow_setting_changed)
        self.workflow_panel.preview_requested.connect(self._on_preview_requested)

    @Slot(int, str)
    def update_display_for_project(self, project_id, project_name):
        self.current_project_id = project_id
        self.latest_successful_stage = "grid"

        # 1. Muat data
        image_paths = self.database_manager.get_images_for_project(project_id)
        settings = self.database_manager.get_project_workflow_settings(project_id)

        # 2. Perintahkan anak-anak untuk update
        self.display_panel.load_project(project_id, project_name, image_paths)
        self.workflow_panel.load_settings(settings)
        self.workflow_panel.update_workflow_stage("grid", has_images=bool(image_paths))
        self.workflow_panel.setVisible(True)
        self.workflow_panel.tab_widget.setCurrentIndex(0)

    @Slot()
    def clear_display(self):
        self.current_project_id = None
        self.display_panel.clear_display(no_projects_exist=(not self.projects_exist))
        self.workflow_panel.setVisible(False)

    @Slot(bool)
    def on_project_existence_changed(self, exists):
        self.projects_exist = exists
        if not self.current_project_id:
            self.clear_display()

    @Slot(str)
    def _on_rename_request(self, current_name):
        self.rename_project_requested.emit(self.current_project_id, current_name)

    @Slot(list)
    def _on_images_imported(self, file_paths):
        success = self.database_manager.add_images_to_project(
            self.current_project_id, file_paths
        )
        if success:
            # Muat ulang data untuk proyek saat ini
            project_name = self.display_panel.project_name
            self.update_display_for_project(self.current_project_id, project_name)
        else:
            QMessageBox.critical(self, "Database Error", "Failed to save images.")

    @Slot(list)
    def _on_images_deleted(self, paths_to_delete):
        success = self.database_manager.delete_images_from_project(
            self.current_project_id, paths_to_delete
        )
        if success:
            project_name = self.display_panel.project_name
            self.update_display_for_project(self.current_project_id, project_name)
        else:
            QMessageBox.critical(self, "Database Error", "Failed to delete images.")

    @Slot(str, str)
    def _on_workflow_setting_changed(self, key, value):
        if self.current_project_id:
            self.database_manager.save_project_workflow_setting(
                self.current_project_id, key, value
            )

    @Slot()
    def _on_back_to_grid_request(self):
        self.display_panel.show_grid_view()
        # Perbarui juga state di workflow panel
        image_paths = self.database_manager.get_images_for_project(
            self.current_project_id
        )
        self.workflow_panel.update_workflow_stage(
            self.latest_successful_stage, has_images=bool(image_paths)
        )

    @Slot(str)
    def _on_preview_requested(self, stage_name):
        """Menangani permintaan preview dan menjalankan simulasi."""
        simulations = {
            "alignment": {
                "message": "Processing Alignment...",
                "delay": 1500,
                "callback": self._on_alignment_finished,
            },
            "projection": {
                "message": "Updating Projection...",
                "delay": 1000,
                "callback": self._on_projection_finished,
            },
            "blending": {
                "message": "Updating Blending...",
                "delay": 1000,
                "callback": self._on_blending_finished,
            },
        }
        sim = simulations.get(stage_name)
        if sim:
            print(f"SIMULASI: Memulai {stage_name}...")
            self.display_panel.show_preview_message(sim["message"])
            QTimer.singleShot(sim["delay"], sim["callback"])

    # --- Simulasi Proses Workflow (sekarang berada di Kontroler) ---
    def _on_alignment_finished(self):
        print("SIMULASI: Alignment selesai.")
        self.display_panel.show_preview_message("DUMMY ALIGNMENT RESULT")
        self.latest_successful_stage = "aligned"
        image_paths = self.database_manager.get_images_for_project(
            self.current_project_id
        )
        self.workflow_panel.update_workflow_stage(
            "aligned", has_images=bool(image_paths)
        )
        self.workflow_panel.tab_widget.setCurrentIndex(1)

    def _on_projection_finished(self):
        print("SIMULASI: Proyeksi selesai.")
        self.display_panel.show_preview_message("DUMMY PROJECTION RESULT")
        self.latest_successful_stage = "projected"
        image_paths = self.database_manager.get_images_for_project(
            self.current_project_id
        )
        self.workflow_panel.update_workflow_stage(
            "projected", has_images=bool(image_paths)
        )
        self.workflow_panel.tab_widget.setCurrentIndex(2)

    def _on_blending_finished(self):
        print("SIMULASI: Blending selesai.")
        self.display_panel.show_preview_message("DUMMY FINAL PREVIEW")
        self.latest_successful_stage = "blended"
        image_paths = self.database_manager.get_images_for_project(
            self.current_project_id
        )
        self.workflow_panel.update_workflow_stage(
            "blended", has_images=bool(image_paths)
        )
