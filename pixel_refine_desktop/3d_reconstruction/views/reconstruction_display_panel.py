"""
ReconstructionDisplayPanel - Display panel untuk 3D Reconstruction.
Subclass of WorkspaceDisplayPanel.

Menggunakan workplace framework untuk grid/preview yang identik
dengan enhance_stack tetapi konten spesifik 3D.
"""

from pixel_refine_desktop.workplace.workspace_display_panel import WorkspaceDisplayPanel


class ReconstructionDisplayPanel(WorkspaceDisplayPanel):
    """
    Display panel spesifik untuk 3D Reconstruction.
    Menampilkan input images untuk rekonstruksi 3D.
    """

    def __init__(self, controller=None):
        super().__init__(controller)

    def _get_import_filter(self) -> str:
        """File filter untuk import images yang akan di-rekonstruksi."""
        return (
            "All Supported Images (*.jpg *.jpeg *.png *.tif *.tiff *.bmp);;"
            "JPEG (*.jpg *.jpeg);;"
            "PNG (*.png);;"
            "TIFF (*.tif *.tiff);;"
            "All Files (*)"
        )

    def load_batch(self, batch_id, items, batch_name=None):
        """Load images ke grid untuk rekonstruksi 3D."""
        self.current_batch_id = batch_id
        self.current_batch_name = batch_name

        # TODO: Implementasi load images ke grid dengan ImageCard
        # Contoh:
        # 1. Clear grid
        # 2. Buat ImageCard untuk setiap item
        # 3. Tambahkan ke grid_container
        # 4. Update header title dengan count

        count = len(items) if items else 0
        self.set_header_title(f"Project: {batch_name or 'Untitled'} ({count} images)")

    def clear_display(self):
        """Clear semua item dari grid."""
        self.current_batch_id = None
        self.current_batch_name = None
        self.set_header_title("")

        # TODO: Clear grid_container items
        # TODO: Show placeholder state

    def _on_import_files(self, paths: list):
        """Handle imported files untuk rekonstruksi 3D."""
        # TODO: Implementasi import images ke 3D project
        # 1. Validasi file format
        # 2. Simpan ke database
        # 3. Load ke grid
        self.items_to_import_selected.emit(paths)
