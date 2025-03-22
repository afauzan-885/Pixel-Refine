import os
from PyQt6.QtWidgets import QLabel, QHBoxLayout
from PyQt6.QtGui import QPixmap, QImage, QImageReader, QPixmapCache
from PyQt6.QtCore import (Qt, QThread, pyqtSignal, QMutex, QWaitCondition,
                          QFile, QSemaphore, QTimer)
import weakref
from config import CACHE_DIR
from UI.settings.General.Language import language_config

# Semaphore untuk menghindari banyak thread mengakses disk secara bersamaan
semaphore = QSemaphore(1)

class ThumbnailLoader(QThread):
    # Mengirimkan QImage dan path gambar
    thumbnail_ready = pyqtSignal(QImage, str)

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
        # Tentukan lokasi cache file
        cache_path = os.path.join(CACHE_DIR, os.path.basename(self.image_path) + ".jpg")

        # Periksa apakah proses dijeda sebelum memulai
        self.mutex.lock()
        while self.paused:
            self.cond.wait(self.mutex)
        self.mutex.unlock()

        # Cek apakah thumbnail sudah ada di hard disk (disimpan sebagai QImage)
        if QFile.exists(cache_path):
            image = QImage(cache_path)
            if not image.isNull():
                self.thumbnail_ready.emit(image, self.image_path)
                return

        # Gunakan semaphore agar tidak ada banyak thread mengakses disk bersamaan
        semaphore.acquire()
        try:
            reader = QImageReader(self.image_path)
            reader.setAutoTransform(True)
            # Mengatur ukuran thumbnail (80x80) dengan menjaga aspek rasio
            reader.setScaledSize(reader.size().scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
            image = reader.read()
            if image.isNull():
                return

            # Simpan hasil ke cache disk sebagai JPG
            image.save(cache_path, "JPG", quality=75)
        finally:
            semaphore.release()

        self.thumbnail_ready.emit(image, self.image_path)


def create_thumbnail_placeholder(list_layout, image_path, placeholders):
    """
    Menampilkan placeholder loading sebelum thumbnail selesai diproses.
    Placeholder akan menggunakan teks yang sama dengan yang dicek di update_thumbnail.
    """
    placeholder = QLabel(language_config.LOADING_THUMBNAIL)  # Contoh: "Memuat..."
    placeholder.setFixedSize(80, 80)
    placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
    placeholder.setStyleSheet(
        "background-color: lightgray; "
        "border: 1px solid gray; "
        "font-size: 12px; "
        "color: gray;"
    )
    list_layout.addWidget(placeholder)
    # Simpan referensi layout agar tidak menyebabkan crash jika dihapus
    placeholders[image_path] = list_layout  
    return placeholder


def update_thumbnail(ref_layout, image, image_path):
    """
    Mengganti placeholder dengan thumbnail saat sudah tersedia.
    Proses konversi dari QImage ke QPixmap dilakukan di GUI thread.
    """
    list_layout = ref_layout() if callable(ref_layout) else ref_layout

    if list_layout is None:
        return 
    
    # Konversi QImage menjadi QPixmap di thread utama
    pixmap = QPixmap.fromImage(image)

    thumb_label = None
    # Cari widget placeholder berdasarkan teks loading
    for i in range(list_layout.count()):
        item = list_layout.itemAt(i)
        widget = item.widget()
        if isinstance(widget, QLabel) and widget.text() == language_config.LOADING_THUMBNAIL:
            thumb_label = widget
            break

    if not thumb_label:
        thumb_label = QLabel()
        list_layout.addWidget(thumb_label)

    thumb_label.setPixmap(pixmap)
    thumb_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    thumb_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
    thumb_label.setFixedSize(80, 80)


def stop_all_thumbnails(threads):
    """Menghentikan semua thread ThumbnailLoader yang sedang berjalan dan membersihkan daftar thread."""
    if not threads:
        return

    for thread in threads:
        if thread.isRunning():
            thread.thumbnail_ready.disconnect()
            thread.quit()

    QTimer.singleShot(100, lambda: threads.clear())
