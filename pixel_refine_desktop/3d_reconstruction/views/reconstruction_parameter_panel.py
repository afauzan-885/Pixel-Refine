"""
ReconstructionParameterPanel - Parameter panel untuk 3D Reconstruction.
Subclass of WorkspaceParameterPanel.

Menggunakan workplace framework untuk parameter layout yang identik
dengan enhance_stack tetapi dengan pengaturan 3D reconstruction.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

from resources.GenericUILibrary import (
    FormGroup,
    Button,
)

from pixel_refine_desktop.workplace.workspace_parameter_panel import WorkspaceParameterPanel


class ReconstructionParameterPanel(WorkspaceParameterPanel):
    """
    Parameter panel spesifik untuk 3D Reconstruction.
    Kolom kiri: Camera/Keypoint parameters
    Kolom kanan: Reconstruction pipeline parameters
    """

    def __init__(self, controller=None, store=None):
        # Track header labels for retranslate
        self.camera_headers = []
        self.reconstruction_headers = []

        super().__init__(controller, store)

    def _create_left_column(self) -> QWidget:
        """Buat widget kolom kiri: Camera & Keypoint parameters."""
        widget = QWidget()
        widget.setObjectName("paramCameraWidget")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        header = QLabel("CAMERA & KEYPOINTS")
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)
        self.camera_headers.append(header)

        # TODO: Tambahkan parameter spesifik 3D:
        # - Feature detection method (AKAZE, ORB, SIFT)
        # - Camera model (Pinhole, Fisheye)
        # - Intrinsic parameters
        # - Match threshold

        placeholder = QLabel("Configure camera parameters...")
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)

        layout.addStretch()
        return widget

    def _create_right_column(self) -> QWidget:
        """Buat widget kolom kanan: Reconstruction pipeline parameters."""
        widget = QWidget()
        widget.setObjectName("paramReconstructionWidget")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        header = QLabel("RECONSTRUCTION PIPELINE")
        header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(header)
        self.reconstruction_headers.append(header)

        # TODO: Tambahkan parameter spesifik 3D:
        # - Sparse/Dense reconstruction mode
        # - Point cloud density
        # - Mesh quality settings
        # - Texture resolution

        placeholder = QLabel("Configure reconstruction parameters...")
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)

        layout.addStretch()
        return widget

    def get_settings(self) -> dict:
        """Ambil pengaturan rekonstruksi 3D saat ini."""
        # TODO: Ambil dari actual parameter widgets
        return {
            "feature_method": "AKAZE",
            "camera_model": "Pinhole",
            "reconstruction_mode": "sparse",
            "mesh_quality": "medium",
        }

    # === Override template methods untuk 3D-specific behavior ===

    def _is_left_column_active(self, settings: dict, none_values: list) -> bool:
        """Camera column selalu aktif saat ada input."""
        feature_method = settings.get("feature_method", "")
        return feature_method not in none_values

    def _is_right_column_active(self, settings: dict, none_values: list) -> bool:
        """Reconstruction column aktif saat mode bukan none."""
        recon_mode = settings.get("reconstruction_mode", "")
        return recon_mode not in none_values

    def _get_process_button_text(self) -> str:
        return "Start Reconstruction"

    def _get_cancel_button_text(self) -> str:
        return "Cancel Reconstruction"

    def _on_process_clicked(self, settings: dict):
        """Trigger proses rekonstruksi 3D."""
        # TODO: Implementasi 3D reconstruction pipeline
        # 1. Sparse reconstruction (Structure from Motion)
        # 2. Dense reconstruction (Multi-View Stereo)
        # 3. Meshing
        # 4. Texturing
        #
        # Setelah selesai, panggil self.on_processing_finished()
        print(f"[3D Reconstruction] Starting with settings: {settings}")
        self.on_processing_finished()

    def _on_ui_ready(self):
        """Setup setelah UI siap."""
        pass

    def retranslate_ui(self):
        """Update semua teks saat bahasa berubah."""
        for header in self.camera_headers:
            try:
                header.setText("CAMERA & KEYPOINTS")
            except RuntimeError:
                pass
        for header in self.reconstruction_headers:
            try:
                header.setText("RECONSTRUCTION PIPELINE")
            except RuntimeError:
                pass
        super().retranslate_ui()
