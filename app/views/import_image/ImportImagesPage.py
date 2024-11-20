from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QMessageBox
from .TopBar import TopBar
from WorkerDatabase import SaveImagesWorker
from .ImagePanel import ImagePanel
from app.controllers.ImportImages.ImportImagesDatabaseHandler import ImportImagesDatabaseHandler


class ImportImagesPage(QWidget):
    """Halaman untuk mengimpor dan mengelola gambar."""

    IMAGE_FILE_FILTER = "Image Files (*.dng *.png *.jpg *.tiff);;All Files (*)"

    def __init__(self):
        super().__init__()
        # Inisialisasi handler database untuk berinteraksi dengan SQLite
        self.db_handler = ImportImagesDatabaseHandler()
        layout = QVBoxLayout()

        # Membuat dan menambahkan top bar
        self.top_bar = TopBar(self.import_images, self.delete_images)
        layout.addLayout(self.top_bar)

        # Membuat panel untuk menampilkan gambar yang diimpor
        self.image_panel = ImagePanel()
        layout.addLayout(self.image_panel)

        self.setLayout(layout)
        self.db_handler.remove_duplicates()
        self.imported_images = set()  # Menyimpan set gambar yang sudah diimpor
        self.load_images_from_db()  # Memuat gambar yang sudah ada dari database

    def import_images(self):
        """Mengimpor gambar baru dan menyimpannya ke database serta menampilkannya."""
        file_paths = self.open_file_dialog()
        if not file_paths:
            return

        # Mengecek apakah ada gambar duplikat dan menampilkan pesan jika ada
        duplicate_files = self.get_duplicate_images(file_paths)
        if duplicate_files:
            self.show_duplicate_message(duplicate_files)
            file_paths = [path for path in file_paths if path not in duplicate_files]

        if not file_paths:
            return

        self.reset_progress_bar()  # Reset progress bar sebelum mulai

        total_imported_files = 0  # Inisialisasi penghitung file yang diimpor

        # Menjalankan worker untuk mengimpor gambar secara terpisah (multithreading)
        self.worker = SaveImagesWorker(file_paths)
        self.worker.progress.connect(self.update_progress_bar)
        self.worker.finished.connect(
            lambda: self.on_import_complete(total_imported_files)
        )
        self.worker.start()

        # Menyimpan file ke panel dan database
        for index, file_path in enumerate(file_paths):
            if self.validate_file(file_path):  # Validasi file
                self.image_panel.add_image(file_path)
                self.imported_images.add(file_path)  # Menambahkan path gambar ke set
                self.db_handler.save_image_path(
                    file_path
                )  # Simpan path gambar ke database
                total_imported_files += 1

            # Menghitung dan memperbarui progress bar
            progress = int((index + 1) / len(file_paths) * 100)
            self.update_progress_bar(progress)

    def on_import_complete(self, total_imported_files):
        """Menangani selesai impor dan menampilkan pesan konfirmasi."""
        message = f"Images have been imported: ({total_imported_files} images)"
        QMessageBox.information(self, "Import Complete", message)

    def load_images_from_db(self):
        """Memuat gambar yang sudah ada dari database SQLite ke dalam panel."""
        image_paths = self.db_handler.get_all_image_paths()
        for path in image_paths:
            if path not in self.imported_images:
                self.image_panel.add_image(path)
                self.imported_images.add(path)

    def delete_images(self):
        """Menangani klik tombol 'Delete' untuk menghapus gambar yang dipilih dengan konfirmasi dan progres bar."""
        selected_items = self.image_panel.image_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "No images selected to delete.")
            return

        # Tampilkan pesan konfirmasi sebelum menghapus
        num_selected = len(selected_items)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {num_selected} image(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            return  # Jika pengguna memilih No, batalkan penghapusan

        # Mulai proses penghapusan dengan progress
        deleted_files = [item.text() for item in selected_items]
        self.reset_progress_bar()  # Reset progress bar sebelum mulai

        # Menjalankan penghapusan gambar secara bertahap dengan memperbarui progress bar
        total_files = len(deleted_files)
        for index, file_path in enumerate(deleted_files):
            self.db_handler.delete_images([file_path])  # Hapus gambar dari database
            self.imported_images.discard(file_path)  # Hapus gambar dari set
            self.image_panel.delete_selected_images(file_path)  # Hapus gambar dari tampilan

            # Perbarui progress bar
            progress = int((index + 1) / total_files * 100)
            self.update_progress_bar(progress)

        QMessageBox.information(self, "Deletion Complete", f"Successfully deleted {num_selected} image(s).")

    def open_file_dialog(self):
        """Buka dialog file untuk memilih gambar."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", self.IMAGE_FILE_FILTER
        )
        return file_paths

    def reset_progress_bar(self):
        """Reset nilai progress bar."""
        self.image_panel.progress_bar.setValue(0)

    def update_progress_bar(self, progress):
        """Perbarui nilai progress bar."""
        self.image_panel.progress_bar.setValue(progress)

    def validate_file(self, file_path):
        """Validasi apakah file dapat diakses."""
        return bool(file_path)

    def get_duplicate_images(self, file_paths):
        """Cek apakah ada gambar yang sudah diimpor sebelumnya."""
        return [path for path in file_paths if path in self.imported_images]

    def show_duplicate_message(self, duplicate_files):
        """Menampilkan pesan jika ditemukan gambar yang duplikat."""
        duplicate_count = len(duplicate_files)
        duplicate_list = "\n".join(duplicate_files)
        message = f"The same image has existed: ({duplicate_count} duplicates)\n{duplicate_list}"
        QMessageBox.warning(self, "Duplicate Image", message)
