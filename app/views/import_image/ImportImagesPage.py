from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QMessageBox
from .TopBar import TopBar
from WorkerDatabase import SaveImagesWorker
from .ImagePanel import ImagePanel
import sqlite3
import db



class ImportImagesPage(QWidget):
    """Halaman untuk mengimpor dan mengelola gambar."""

    # Konstanta untuk filter file
    IMAGE_FILE_FILTER = "Image Files (*.dng *.png *.jpg *.tiff);;All Files (*)"

    def __init__(self):
        super().__init__()
        db.create_db()  # Pastikan database siap digunakan
        layout = QVBoxLayout()

        # Komponen UI lainnya
        self.top_bar = TopBar(self.import_images, self.delete_images)
        layout.addLayout(self.top_bar)

        self.image_panel = ImagePanel()
        layout.addLayout(self.image_panel)

        self.setLayout(layout)
        self.imported_images = set()
        self.load_images_from_db()

    def import_images(self):
        file_paths = self.open_file_dialog()
        if not file_paths:
            return

        duplicate_files = self.get_duplicate_images(file_paths)
        if duplicate_files:
            self.show_duplicate_message(duplicate_files)
            file_paths = [path for path in file_paths if path not in duplicate_files]

        if not file_paths:
            return

        self.reset_progress_bar()

        # Jalankan worker untuk menyimpan gambar dalam batch
        self.worker = SaveImagesWorker(file_paths)
        self.worker.progress.connect(self.update_progress_bar)
        self.worker.finished.connect(self.on_import_complete)
        self.worker.start()  # Start worker in a separate thread



        total_files = len(file_paths)
        for index, file_path in enumerate(file_paths):
            if self.validate_file(file_path):  # Validasi file
                self.image_panel.add_image(file_path)
                self.imported_images.add(file_path)  # Tambahkan ke set imported_images
                self.save_image_path_to_db(file_path)  # Simpan ke database
            # Hitung dan perbarui progress bar
            progress = int((index + 1) / total_files * 100)
            self.update_progress_bar(progress)

    def on_import_complete(self):
            """Handle import completion."""
            QMessageBox.information(self, "Import Complete", "Images have been imported.")
    
    def save_image_path_to_db(self, file_path):
        """Simpan satu path gambar ke database SQLite."""
        conn = sqlite3.connect("image_paths.db")
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO images (path) VALUES (?)", (file_path,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def sync_imported_images_with_db(self):
        """Sinkronkan imported_images dengan data di database."""
        conn = sqlite3.connect("image_paths.db")
        cursor = conn.cursor()

        cursor.execute("SELECT path FROM images")
        rows = cursor.fetchall()

        # Perbarui imported_images berdasarkan database
        self.imported_images = {row[0] for row in rows}

        conn.close()
        
    def save_image_paths_to_db(image_paths):
        """Simpan beberapa path gambar ke database SQLite sekaligus."""
        conn = sqlite3.connect("image_paths.db")
        cursor = conn.cursor()

        try:
            # Gunakan batch processing untuk menyimpan semua path dalam satu transaksi
            cursor.executemany("INSERT INTO images (path) VALUES (?)", [(path,) for path in image_paths])
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
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
        # Ambil gambar yang dipilih untuk dihapus
        selected_items = self.image_panel.image_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "No images selected to delete.")
            return

        deleted_files = [item.text() for item in selected_items]

        # Hapus gambar dari database
        conn = sqlite3.connect("image_paths.db")
        cursor = conn.cursor()

        for file_path in deleted_files:
            cursor.execute("DELETE FROM images WHERE path = ?", (file_path,))
        
        conn.commit()
        conn.close()

        # Hapus file yang dihapus dari daftar imported_images
        self.imported_images.difference_update(deleted_files)

        # Hapus dari GUI
        for item in selected_items:
            row = self.image_panel.image_list.row(item)
            self.image_panel.image_list.takeItem(row)


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
