from functools import partial
import os
import weakref
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy,
                             QSpacerItem, QPushButton, QScrollArea, QMessageBox,
                             QFileDialog, QLabel)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from UI.enhance_stack.components.batch_page_layout.thumbnail import ThumbnailLoader, update_thumbnail
from UI.enhance_stack.logic import database_manager
from UI.settings.General.Language import language_config

class BatchDeleteProcess(QThread):
    batch_deleted = pyqtSignal()

    def __init__(self, database_manager, batch_id, cache_dir, thumbnail_threads, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.batch_id = batch_id
        self.cache_dir = cache_dir
        self.thumbnail_threads = thumbnail_threads

    def run(self):
        # **Jeda semua proses pembuatan thumbnail**
        for thread in self.thumbnail_threads:
            thread.pause()

        # **Hapus cache dari disk**
        image_paths = self.database_manager.get_images_by_batch(self.batch_id)
        for path in image_paths:
            cache_path = os.path.join(self.cache_dir, os.path.basename(path) + ".jpg")
            if os.path.exists(cache_path):
                os.remove(cache_path)

        # **Hapus batch dari database**
        self.database_manager.batch_process_delete_batch(self.batch_id)

        # **Emit sinyal untuk memperbarui UI setelah penghapusan selesai**
        self.batch_deleted.emit()

        # **Lanjutkan kembali proses pembuatan thumbnail**
        for thread in self.thumbnail_threads:
            thread.resume()

def handle_add_image_to_batch(batch_page_layout, database_manager, thumbnail_threads, batch_id, list_layout):
    if batch_id is None:
        print("Batch ID tidak valid.")
        return

    existing_image_paths = database_manager.get_images_by_batch(batch_id)

    file_dialog = QFileDialog()
    file_paths, _ = file_dialog.getOpenFileNames(
        None,
        language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH,
        "",
        language_config.HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION
    )

    if not file_paths:
        return  

    existing_set = set(existing_image_paths)
    unique_files = [path for path in file_paths if path not in existing_set]
    duplicates = list(existing_set.intersection(file_paths))

    if duplicates:
        message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE.format(count=len(duplicates))
        QMessageBox.warning(None, language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE, message)

    if unique_files:
        database_manager.batch_process_save_image_path(batch_id, unique_files)

        ref_layout = weakref.ref(list_layout)

        for path in unique_files:
            loader = ThumbnailLoader(path)
            loader.thumbnail_ready.connect(
                lambda pixmap, p=path, ref_layout=ref_layout: update_thumbnail(ref_layout, pixmap, p) if ref_layout() else None
            )
            loader.start()
            thumbnail_threads.append(loader)  # Simpan referensi agar tidak dihapus GC

        print(f"Added {len(unique_files)} new images to batch {batch_id}")

        # Emit sinyal data_changed dari BatchPageLayout
        batch_page_layout.data_changed.emit()
