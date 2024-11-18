from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from .TopBar import TopBar
from .ImagePanel import ImagePanel
import sqlite3
import db

class ImportImagesPage(QWidget):
    """Halaman untuk mengimpor dan mengelola gambar."""

    # Konstanta untuk filter file
    IMAGE_FILE_FILTER = "Image Files (*.dng *.png *.jpg *.tiff);;All Files (*)"

    def __init__(self):
        super().__init__()
        
        # Panggil create_db untuk memastikan tabel sudah ada
        db.create_db()

        # Layout utama
        layout = QVBoxLayout()

        # Komponen Top Bar
        self.top_bar = TopBar(self.import_images, self.delete_images)
        layout.addLayout(self.top_bar)

        # Komponen Image Panel
        self.image_panel = ImagePanel()
        layout.addLayout(self.image_panel)

        self.setLayout(layout)
        
         # Muat gambar dari database
        self.load_images_from_db()

        # State tracking (bisa digunakan untuk fitur tambahan di masa depan)
        self.shift_pressed = False
        self.ctrl_pressed = False
        self.last_selected_item = None

        # Set untuk menyimpan path gambar yang sudah diimpor
        self.imported_images = set()

    def import_images(self):
        """Handle 'Import Image' button click."""
        file_paths = self.open_file_dialog()

        if not file_paths:
            return  # Tidak ada file yang dipilih

        duplicate_files = self.get_duplicate_images(file_paths)
        if duplicate_files:
            # Tampilkan pesan error jika ada gambar yang sama
            self.show_duplicate_message(duplicate_files)
            # Hanya tambahkan gambar yang tidak duplikat
            file_paths = [path for path in file_paths if path not in duplicate_files]

        if not file_paths:
            return  # Tidak ada gambar baru untuk diimpor

        self.reset_progress_bar()

        total_files = len(file_paths)
        for index, file_path in enumerate(file_paths):
            if self.validate_file(file_path):  # Validasi file
                self.image_panel.add_image(file_path)
                self.imported_images.add(file_path)  # Tambahkan ke set imported_images
            self.update_progress_bar(index + 1, total_files)

    def save_image_path_to_db(self, image_path):
        """Simpan path gambar ke database SQLite."""
        conn = sqlite3.connect("image_paths.db")  # Nama file database
        cursor = conn.cursor()

        # Menyimpan path gambar ke dalam database
        cursor.execute("INSERT INTO images (path) VALUES (?)", (image_path,))
        conn.commit()
        conn.close()
    
    def load_images_from_db(self):
        """Muat gambar yang sudah ada dari database SQLite ke dalam panel."""
        conn = sqlite3.connect("image_paths.db")  # Nama file database
        cursor = conn.cursor()

        # Ambil semua path gambar dari database
        cursor.execute("SELECT path FROM images")
        rows = cursor.fetchall()

        # Menambahkan gambar yang ada di database ke panel
        for row in rows:
            self.image_panel.add_image(row[0])  # row[0] adalah path gambar

        conn.close()
    
        
    def delete_images(self):
        """Handle 'Delete' button click."""
        deleted_files = self.image_panel.delete_selected_images()

        if not deleted_files:
            return  # Tidak ada gambar yang dipilih untuk dihapus

        # Hapus gambar dari database
        conn = sqlite3.connect("image_paths.db")
        cursor = conn.cursor()

        for file_path in deleted_files:
            # Hapus path gambar dari database
            cursor.execute("DELETE FROM images WHERE path = ?", (file_path,))
        
        conn.commit()
        conn.close()

        # Hapus file yang dihapus dari daftar imported_images
        self.imported_images.difference_update(deleted_files)




    def open_file_dialog(self):
        """Buka dialog file untuk memilih gambar."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", self.IMAGE_FILE_FILTER
        )
        return file_paths

    def reset_progress_bar(self):
        """Reset nilai progress bar."""
        self.image_panel.progress_bar.setValue(0)

    def update_progress_bar(self, current, total):
        """Perbarui nilai progress bar."""
        progress = int((current / total) * 100)
        self.image_panel.progress_bar.setValue(progress)

    def validate_file(self, file_path):
        """Validasi apakah file dapat diakses."""
        # Tambahkan logika untuk validasi (misalnya, periksa apakah file ada)
        # Contoh sederhana:
        return bool(file_path)

    def get_duplicate_images(self, file_paths):
        """Cek apakah ada gambar yang sudah diimpor."""
        return [path for path in file_paths if path in self.imported_images]

    def show_duplicate_message(self, duplicate_files):
        """Tampilkan pesan error untuk gambar yang duplikat."""
        duplicate_list = "\n".join(duplicate_files)
        message = f"The same image has existed:\n{duplicate_list}"
        QMessageBox.warning(self, "Duplicate Image", message)
