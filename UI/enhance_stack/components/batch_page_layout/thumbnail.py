import os
from PyQt6.QtWidgets import QLabel, QStackedWidget
from PyQt6.QtGui import QPixmap, QImage, QImageReader 
from PyQt6.QtCore import (Qt, QThread, pyqtSignal, QMutex, QWaitCondition,
                          QFile, QSemaphore, QTimer)
import weakref

import rawpy
from UI.resources.animation.fade import fade_in
from config import CACHE_DIR, SUPPORTED_FORMATS
from UI.settings.General.Language import language_config

semaphore = QSemaphore(1)

class ThumbnailLoader(QThread):
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
        cache_path = os.path.join(CACHE_DIR, os.path.basename(self.image_path) + ".jpg")

        self.mutex.lock()
        while self.paused:
            self.cond.wait(self.mutex)
        self.mutex.unlock()

        # Cek cache
        if QFile.exists(cache_path):
            image = QImage(cache_path)
            if not image.isNull():
                self.thumbnail_ready.emit(image, self.image_path)
                return

        ext = os.path.splitext(self.image_path)[1].lower()

        semaphore.acquire()
        try:
            if ext in SUPPORTED_FORMATS["jpg"] + SUPPORTED_FORMATS["png"] + SUPPORTED_FORMATS["tiff"]:
                reader = QImageReader(self.image_path)
                reader.setAutoTransform(True)
                reader.setScaledSize(reader.size().scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
                image = reader.read()
                if image.isNull():
                    return
            elif ext in SUPPORTED_FORMATS["raw"]:
                try:
                    with rawpy.imread(self.image_path) as raw:
                        img_array = raw.postprocess(
                            output_bps=8,
                            use_camera_wb=True,
                            no_auto_bright=False,
                            gamma=(2.5, 15.92),
                            highlight_mode=rawpy.HighlightMode.Blend,
                            half_size=True
                        )
                    # Konversi numpy array (HWC, uint8) ke QImage
                    height, width, channel = img_array.shape
                    bytes_per_line = 3 * width
                    image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                    image = image.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)
                except rawpy.LibRawError as e:
                    print(f"Rawpy Error: {e}")
                    return
                except Exception as e:
                    print(f"Unexpected error processing RAW file: {e}")
                    return
            else:
                # Format tidak didukung
                print(f"Format file tidak didukung: {ext}")
                return

            # Simpan thumbnail ke cache
            image.save(cache_path, "JPG", quality=75)

        finally:
            semaphore.release()

        self.thumbnail_ready.emit(image, self.image_path)



def create_thumbnail_placeholder(list_layout, image_path, placeholders):
    """
    Membuat placeholder dalam QStackedWidget untuk bisa dianimasikan nanti.
    """
    placeholder_label = QLabel(language_config.LOADING_THUMBNAIL)
    placeholder_label.setFixedSize(80, 80)
    placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    placeholder_label.setStyleSheet(
        "background-color: lightgray; "
        "border: 1px solid gray; "
        "font-size: 12px; "
        "color: gray;"
    )

    stacked = QStackedWidget()
    stacked.setFixedSize(80, 80)
    stacked.addWidget(placeholder_label)
    stacked.image_path = image_path

    list_layout.addWidget(stacked)
    placeholders[image_path] = list_layout
    return stacked


def show_thumbnail(ref_layout, image, image_path, animator):
    """
    Mengganti placeholder dengan thumbnail + efek animasi fade-in.
    """
    list_layout = ref_layout() if callable(ref_layout) else ref_layout
    if list_layout is None:
        return

    pixmap = QPixmap.fromImage(image)

    for i in range(list_layout.count()):
        item = list_layout.itemAt(i)
        widget = item.widget()

        if isinstance(widget, QStackedWidget) and getattr(widget, "image_path", None) == image_path:
            thumb_label = QLabel()
            thumb_label.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            thumb_label.setScaledContents(True)  
            thumb_label.setMaximumSize(80, 80)
            thumb_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")

            widget.addWidget(thumb_label)
            fade_in(animator, widget, thumb_label)
            break


def stop_process_thumbnails(threads):
    """Menghentikan semua thread ThumbnailLoader yang sedang berjalan dan membersihkan daftar thread."""
    if not threads:
        return

    for thread in threads:
        if thread.isRunning():
            thread.thumbnail_ready.disconnect()
            thread.quit()

    QTimer.singleShot(100, lambda: threads.clear())
