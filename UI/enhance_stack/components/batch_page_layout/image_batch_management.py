from functools import partial
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy,
                             QSpacerItem, QPushButton, QScrollArea, QMessageBox,
                             QFileDialog, QLabel)

from UI.enhance_stack.components.batch_page_layout.thumbnail import ThumbnailLoader, add_thumbnail
from UI.enhance_stack.logic import database_manager
from UI.settings.General.Language import language_config

@classmethod
def handle_add_image_to_batch(cls, batch_id, list_layout):
        """
        Menambahkan gambar ke batch yang sudah ada, dengan pengecekan duplikat dalam batch tersebut.

        Args:
            batch_id (int): ID batch tempat gambar akan ditambahkan.
            list_layout (QHBoxLayout): Layout yang menampilkan daftar gambar.
        """
        if batch_id is None:
            print("Batch ID tidak valid.")
            return

        # Ambil daftar image_id yang sudah ada dalam batch ini
        existing_image_paths = database_manager.get_images_by_batch(batch_id)

        # Buka dialog pemilihan file
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(None, language_config.HANDLE_IMPORT_BUTTON_IMAGE_PATH, "", language_config.HANDLE_IMPORT_BUTTON_IMAGE_EXTENSION)

        if not file_paths:
            return  # Jika user tidak memilih gambar, keluar dari fungsi

        # Cek duplikat dalam batch ini
        existing_set = set(existing_image_paths)
        unique_files = [path for path in file_paths if path not in existing_set]
        duplicates = list(existing_set.intersection(file_paths))
        unique_files = [path for path in file_paths if path not in existing_image_paths]

        # Jika ada duplikat, beri peringatan ke user
        if duplicates:
            message = language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE_MESSAGE.format(count=len(duplicates))
            QMessageBox.warning(None, language_config.HANDLE_IMPORT_BUTTON_IMAGE_DUPLICATE, message)

        # Simpan hanya gambar yang unik ke database
        if unique_files:
            cls.database_manager.batch_process_save_image_path(batch_id, unique_files)

            # List untuk menyimpan thread agar tetap hidup
            cls.thumbnail_threads = getattr(cls, 'thumbnail_threads', [])

            # Tambahkan thumbnail dengan threading
            for path in unique_files:
                loader = ThumbnailLoader(path)
                loader.thumbnail_ready.connect(partial(add_thumbnail, list_layout=list_layout))  # Perbaiki lambda capturing
                loader.start()
                cls.thumbnail_threads.append(loader)  # Simpan referensi agar tidak dihapus GC

            print(f"Added {len(unique_files)} new images to batch {batch_id}")
            
            