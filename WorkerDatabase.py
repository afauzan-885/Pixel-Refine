from PyQt6.QtCore import QThread, pyqtSignal, QThreadPool
import sqlite3
from threading import Lock

db_lock = Lock()

class SaveImagesWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths

    def run(self):
        total_files = len(self.file_paths)

        with db_lock:  # Pastikan hanya satu thread yang mengakses database
            conn = sqlite3.connect("image_paths.db")
            cursor = conn.cursor()

            try:
                # Mulai transaksi
                cursor.execute('BEGIN TRANSACTION')

                for index, file_path in enumerate(self.file_paths):
                    cursor.execute("INSERT INTO images (path) VALUES (?)", (file_path,))
                    
                    # Update progress setiap batch
                    if (index + 1) % 10 == 0:  # Commit setiap 10 file
                        cursor.connection.commit()  # Commit batch untuk mencegah terlalu sering I/O

                    progress = int((index + 1) / total_files * 100)
                    self.progress.emit(progress)

                # Commit transaksi setelah selesai semua
                cursor.connection.commit()

            except sqlite3.Error as e:
                print(f"Database error: {e}")
                conn.rollback()  # Jika ada error, rollback transaksi

            finally:
                conn.close()

        self.finished.emit()


class ImageImportManager:
    def __init__(self):
        self.thread_pool = QThreadPool.globalInstance()  # Pool untuk thread
        self.thread_pool.setMaxThreadCount(3)  # Batasi maksimal 3 thread bersamaan

    def import_images_in_batches(self, all_file_paths):
        batch_size = 3  # Setiap batch akan memproses 3 file
        batches = [all_file_paths[i:i + batch_size] for i in range(0, len(all_file_paths), batch_size)]

        for batch in batches:
            worker = SaveImagesWorker(batch)
            worker.progress.connect(self.update_progress_bar)
            worker.finished.connect(self.on_import_finished)
            worker.start()  # Mulai memproses batch berikutnya