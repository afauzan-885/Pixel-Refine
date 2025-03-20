import os
from PyQt6.QtWidgets import QLabel, QHBoxLayout
from PyQt6.QtGui import QImage, QPixmap, QImageReader, QPixmapCache
from PyQt6.QtCore import (Qt, QThread, pyqtSignal, QMutex, QWaitCondition,
                          QFile, QSemaphore)

from config import CACHE_DIR
semaphore = QSemaphore(1)

class ThumbnailLoader(QThread):
    thumbnail_ready = pyqtSignal(QPixmap, str)

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.paused = False
        self.mutex = QMutex()
        self.cond = QWaitCondition()

    def pause(self):
        """Menjeda proses thumbnail."""
        self.mutex.lock()
        self.paused = True
        self.mutex.unlock()

    def resume(self):
        """Melanjutkan proses thumbnail setelah dijeda."""
        self.mutex.lock()
        self.paused = False
        self.cond.wakeAll()
        self.mutex.unlock()

    def run(self):
        cache_path = os.path.join(CACHE_DIR, os.path.basename(self.image_path) + ".jpg")

        # **Cek apakah harus dijeda sebelum memulai proses**
        self.mutex.lock()
        while self.paused:
            self.cond.wait(self.mutex)
        self.mutex.unlock()

        # **Gunakan QPixmapCache untuk menghindari akses disk berulang**
        cached_pixmap = QPixmapCache.find(cache_path)
        if cached_pixmap:
            self.thumbnail_ready.emit(cached_pixmap, self.image_path)
            return

        # **Cek apakah thumbnail sudah ada di hard disk**
        if QFile.exists(cache_path):
            pixmap = QPixmap(cache_path)
            QPixmapCache.insert(cache_path, pixmap)  # Cache ke RAM
            self.thumbnail_ready.emit(pixmap, self.image_path)
            return

        # **Gunakan semaphore agar tidak ada banyak thread mengakses disk secara bersamaan**
        semaphore.acquire()
        try:
            reader = QImageReader(self.image_path)
            reader.setAutoTransform(True)
            reader.setScaledSize(reader.size().scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))

            image = reader.read()
            if image.isNull():
                return

            pixmap = QPixmap.fromImage(image)

            # **Simpan hasil ke cache disk sebagai JPG (lebih kecil & cepat)**
            pixmap.save(cache_path, "JPG", quality=75)

            # **Masukkan ke cache RAM untuk menghindari akses disk ulang**
            QPixmapCache.insert(cache_path, pixmap)

        finally:
            semaphore.release()

        self.thumbnail_ready.emit(pixmap, self.image_path)

def clear_batch_cache(database_manager, batch_id, cache_dir):
    """
    Menghapus thumbnail yang terkait dengan batch yang dihapus.

    Args:
        database_manager: Instance database manager untuk mengambil data batch.
        batch_id (int): ID batch yang akan dihapus.
        cache_dir (str): Lokasi direktori cache.
    """
    image_paths = database_manager.get_images_by_batch(batch_id)
    for path in image_paths:
        cache_path = os.path.join(cache_dir, os.path.basename(path) + ".png")
        if os.path.exists(cache_path):
            os.remove(cache_path)

def stop_thumbnail(thumbnail_threads):
    """
    Menghentikan semua thread ThumbnailLoader yang sedang berjalan.

    Args:
        thumbnail_threads (list): List thread ThumbnailLoader.
    """
    for thread in thumbnail_threads:
        if thread.isRunning():
            thread.thumbnail_ready.disconnect() 
            thread.quit()  
            thread.wait()
    thumbnail_threads.clear()

def add_loading_placeholder(list_layout: QHBoxLayout, image_path: str):
    """
    Menampilkan placeholder loading sebelum thumbnail selesai diproses.

    Args:
        list_layout (QHBoxLayout): Layout tempat widget ditambahkan.
        image_path (str): Path gambar (bisa digunakan untuk logika tambahan jika diperlukan).

    Returns:
        QLabel: Widget placeholder yang telah dibuat.
    """
    placeholder = QLabel("Loading...")
    placeholder.setFixedSize(80, 80)
    placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
    placeholder.setStyleSheet(
        "background-color: lightgray; border: 1px solid gray; font-size: 12px; color: gray;"
    )
    list_layout.addWidget(placeholder)
    return placeholder

def add_thumbnail(list_layout: QHBoxLayout, image: QImage, image_path: str):
    """
    Mengganti placeholder dengan thumbnail saat sudah tersedia.

    Args:
        list_layout (QHBoxLayout): Layout tempat widget ditambahkan.
        image (QImage): Gambar thumbnail yang sudah diproses.
        image_path (str): Path gambar yang bersangkutan.
    """
    pixmap = QPixmap.fromImage(image)
    
    # Cari placeholder yang sesuai (dengan teks "Loading...")
    thumb_label = None
    for i in range(list_layout.count()):
        widget = list_layout.itemAt(i).widget()
        if isinstance(widget, QLabel) and widget.text() == "Loading...":
            thumb_label = widget
            break
    # Jika placeholder tidak ditemukan, buat widget baru
    if thumb_label is None:
        thumb_label = QLabel()
        list_layout.addWidget(thumb_label)
    
    thumb_label.setPixmap(pixmap)
    thumb_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    thumb_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
    thumb_label.setFixedSize(80, 80)
