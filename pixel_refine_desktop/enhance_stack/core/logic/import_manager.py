# --- START OF FILE import_manager.py ---

import os
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QFileDialog

from pixel_refine_desktop.ui.resources.animations.toast.toast_manager import (
    ToastPosition,
)
from pixel_refine_desktop.ui.resources.GenericUILibrary import ImageCard
from config import SUPPORTED_FORMATS


class ImportManager(QObject):
    """
    Manager untuk menangani semua logika import gambar.
    Mengikuti pola yang sama dengan DeletionManager.
    """

    # Signals
    import_started = Signal(int)  # batch_id
    import_finished = Signal(int)  # batch_id

    def __init__(self, display_panel):
        super().__init__()
        self.panel = display_panel
        self.active_import_batches = set()

    def _build_file_filter(self):
        """
        Build file filter string untuk QFileDialog dari config.SUPPORTED_FORMATS.

        Returns:
            str: File filter string (e.g., "Images (*.jpg *.jpeg *.png ...)")
        """
        all_extensions = []
        for format_name, ext_list in SUPPORTED_FORMATS.items():
            all_extensions.extend(ext_list)

        # Create filter string: "Images (*.jpg *.jpeg *.png ...)"
        ext_string = " ".join([f"*{ext}" for ext in all_extensions])
        return f"Images ({ext_string})"

    @Slot()
    def import_images(self):
        """
        Membuka dialog file untuk impor gambar dengan format dari config.SUPPORTED_FORMATS.
        Mirip dengan panorama page import_images method.
        """
        if not self.panel.current_batch_id:
            return

        # Build file filter string dari supported formats
        file_filter = self._build_file_filter()

        # Open file dialog untuk select multiple images
        paths, _ = QFileDialog.getOpenFileNames(
            self.panel, "Select Images", "", file_filter
        )

        if paths:
            # Emit signal dengan selected file paths
            self.panel.images_to_import_selected.emit(paths)

    @Slot(int, str, str)
    def add_single_image_to_grid(self, batch_id, batch_name, image_path):
        """
        Menambah satu thumbnail ke grid secara real-time.
        """
        # 1. Background Import Logic (Jika user pindah batch saat import berjalan)
        if batch_id != self.panel.current_batch_id:
            active_count = len(self.active_import_batches)
            if batch_id not in self.active_import_batches:
                self.active_import_batches.add(batch_id)
                active_count += 1

            # Update pesan progress tanpa menutup toast
            message = (
                f"Background Import: Menambahkan gambar ke {active_count} batch..."
                if active_count > 1
                else f"Background Import: Menambahkan ke {batch_name}..."
            )
            self.panel.toast.show_progress(message, position=ToastPosition.BOTTOM_RIGHT)
            return

        # 2. Logic Tambah ke Grid (Current Batch)
        # Buat dummy object agar kompatibel dengan logic
        class DummyImg:
            def __init__(self, path):
                self.path = path
                self.id = os.path.basename(path)

        img = DummyImg(image_path)

        # Cek jika sudah ada (safety)
        if str(img.id) in self.panel.all_cards:
            return

        card = ImageCard(card_id=str(img.id), size=110)
        card._image_path = img.path
        card.double_clicked.connect(self.panel._on_card_double_clicked)
        card.clicked.connect(
            lambda cid, event, c=card: self.panel._on_card_clicked(cid, event, c)
        )

        self.panel.grid_container.add_item(card)
        self.panel.all_cards[str(img.id)] = card
        self.panel.logic.register_grid_item(str(img.id), {"path": img.path})
        self.panel._load_thumbnail_async(img.path, card)

        # Increment total count
        self.panel.total_image_count += 1

        # Update header count
        self.panel._update_header_title()

        # Check for active deletions to resume
        self.panel.deletion_manager.resume_deletion_simulation(batch_id)

        # Pastikan grid container pindah dari placeholder jika sebelumnya kosong
        if self.panel.grid_content_stack.currentWidget() != self.panel.grid_container:
            self.panel._set_placeholder(None)

    @Slot(int)
    def on_batch_import_started(self, batch_id):
        """Slot to mark a batch as actively importing."""
        self.active_import_batches.add(batch_id)

        # MODIFIKASI: Gunakan show_progress (Persistent / Duration 0)
        # Toast ini TIDAK akan hilang sampai kita panggil show_message/hide nanti.
        self.panel.toast.show_progress(
            "Mengimpor...", position=ToastPosition.BOTTOM_RIGHT
        )

        # Emit signal
        self.import_started.emit(batch_id)

    @Slot(int)
    def on_batch_import_finished(self, batch_id):
        """Slot to mark a batch as finished importing."""
        if batch_id in self.active_import_batches:
            self.active_import_batches.remove(batch_id)

        # Jika tidak ada lagi import yang berjalan di batch manapun
        if not self.active_import_batches:
            # MODIFIKASI: Tampilkan pesan "Selesai" dengan durasi 3 detik
            # Ini akan menggantikan pesan "Sedang mengimport..." lalu fade out otomatis.
            self.panel.toast.show_message(
                "Proses import selesai.",
                duration=3000,
                position=ToastPosition.BOTTOM_RIGHT,
            )

        # Emit signal
        self.import_finished.emit(batch_id)
