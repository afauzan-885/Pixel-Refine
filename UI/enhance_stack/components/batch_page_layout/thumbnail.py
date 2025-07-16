import os
from PySide6.QtWidgets import QLabel, QStackedWidget
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import (Qt, QThread, Signal, QMutex, QWaitCondition,
                          QFile, QSemaphore, QTimer)
import cv2
import numpy as np
import rawpy
from UI.resources.animation.fade import fade_in
from config import CACHE_DIR, SUPPORTED_FORMATS
from PIL import Image, ImageOps
from UI.settings.General.Language import language_config

semaphore = QSemaphore(4) # Batasi 4 thread yang aktif memproses gambar secara bersamaan

try:
    os.makedirs(CACHE_DIR, exist_ok=True)
except OSError as e:
    print(f"Error creating cache directory {CACHE_DIR}: {e}")

class ThumbnailLoader(QThread):
    """
    Versi yang dioptimalkan: lebih cepat merespons permintaan berhenti.
    """
    thumbnail_ready = Signal(QImage, str)

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        # Pause/Resume logic tidak diubah, karena sudah benar.
        self.paused = False
        self.mutex = QMutex()
        self.cond = QWaitCondition()

    def pause(self):
        self.mutex.lock()
        self.paused = True
        self.mutex.unlock()

    def resume(self):
        self.mutex.lock()
        self.paused = False
        self.cond.wakeAll()
        self.mutex.unlock()

    def run(self):
        result_image = QImage()
        semaphore.acquire()
        try:
            # === OPTIMASI: Cek interupsi lebih awal ===
            # Jika thread sudah diminta berhenti bahkan sebelum mulai, keluar segera.
            if self.isInterruptionRequested():
                return # Langsung ke 'finally'

            self.mutex.lock()
            while self.paused:
                self.cond.wait(self.mutex)
            self.mutex.unlock()

            cache_path = os.path.join(CACHE_DIR, os.path.basename(self.image_path) + ".jpg")
            if QFile.exists(cache_path):
                cached_image = QImage(cache_path)
                if not cached_image.isNull():
                    result_image = cached_image
                    return 
            
            # === OPTIMASI: Cek interupsi sebelum proses berat ===
            # Jika cache tidak ada, cek lagi sebelum memulai pemrosesan file asli.
            if self.isInterruptionRequested():
                return # Langsung ke 'finally'

            processed_image = QImage() 
            ext = os.path.splitext(self.image_path)[1].lower()

            try:
                # Logika pemrosesan file Anda sudah bagus dan tidak perlu diubah.
                # (kode untuk JPG, PNG, RAW tetap sama)
                if ext in SUPPORTED_FORMATS["jpg"] + SUPPORTED_FORMATS["png"] + SUPPORTED_FORMATS["tiff"]:
                    pil_img = Image.open(self.image_path)
                    pil_img = ImageOps.exif_transpose(pil_img)
                    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

                    if img is not None:
                        if len(img.shape) == 2: img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                        if img.dtype == np.uint16: img = (img / 256).astype(np.uint8)
                        
                        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        height, width, channel = img_rgb.shape
                        bytes_per_line = 3 * width
                        processed_image = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).copy()

                elif ext in SUPPORTED_FORMATS["raw"]:
                    with rawpy.imread(self.image_path) as raw:
                        img_array = raw.postprocess(output_bps=8, use_camera_wb=True, half_size=True)
                    
                    height, width, channel = img_array.shape
                    bytes_per_line = 3 * width
                    processed_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).copy()

            except Exception as e:
                print(f"SELF-REPAIR: Gagal memproses {self.image_path}. Error: {e}")

            if not processed_image.isNull():
                scaled_image = processed_image.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                scaled_image.save(cache_path, "JPG", quality=85)
                result_image = scaled_image

        finally:
            semaphore.release()
            # Hanya emit sinyal jika thread tidak diminta untuk berhenti.
            # Ini mencegah widget yang sudah tidak relevan untuk mencoba update.
            if not self.isInterruptionRequested():
                self.thumbnail_ready.emit(result_image, self.image_path)


def thumbnail_placeholder(list_layout, image_path, placeholders, retry_count=0):
    try:
        if list_layout is None:
            raise RuntimeError("Layout is None")
        parent = list_layout.parent()
    except RuntimeError:
        if retry_count < 3:
            QTimer.singleShot(100,
                              lambda: thumbnail_placeholder(list_layout, image_path, placeholders, retry_count + 1))
        return None

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

    try:
        list_layout.addWidget(stacked)
    except RuntimeError:
        return None

    placeholders[image_path] = list_layout
    return stacked


def make_safe_callback(current_path, layout_ref):
    def safe_callback(image, image_path):
        layout = layout_ref() if layout_ref else None
        try:
            if layout is None or not hasattr(layout, "count") or layout.parent() is None:
                return
            show_thumbnail(layout, image, current_path, animator=None)
        except RuntimeError:
            pass
        except Exception:
            pass
    return safe_callback


def show_thumbnail(ref_layout, image, image_path, animator=None, retry_count=0):
    try:
        list_layout = ref_layout() if callable(ref_layout) else ref_layout
        if list_layout is None:
            raise RuntimeError("Layout is None")

        _ = list_layout.parent()
        count = list_layout.count()
        pixmap = QPixmap.fromImage(image)

        for i in range(count):
            item = list_layout.itemAt(i)
            widget = item.widget()

            if isinstance(widget, QStackedWidget) and getattr(widget, "image_path", None) == image_path:
                for j in range(widget.count()):
                    w = widget.widget(j)
                    if isinstance(w, QLabel) and w.pixmap() is not None and not w.pixmap().isNull():
                        return  
                    
                thumb_label = QLabel()
                thumb_label.setPixmap(pixmap.scaledToHeight(80, Qt.TransformationMode.SmoothTransformation))
                thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                thumb_label.setScaledContents(False)
                thumb_label.setMaximumHeight(80)
                thumb_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")

                widget.addWidget(thumb_label)
                widget.setCurrentWidget(thumb_label)

                if animator:
                    thumb_label.setGraphicsEffect(None)
                    fade_in(animator, widget, thumb_label)

                return

    except RuntimeError:
        if retry_count < 3:
            QTimer.singleShot(100, lambda: show_thumbnail(ref_layout, image, image_path, animator, retry_count + 1))

def stop_process_thumbnails(threads):
    """
    Menghentikan semua thread thumbnail dengan aman dan sinkron.
    Fungsi ini sekarang akan memblokir sampai semua thread benar-benar berhenti
    sebelum membersihkan daftar referensi.
    """
    if not threads:
        return

    # Fase 1: Minta semua thread untuk berhenti dan putuskan koneksi sinyal.
    # Ini dilakukan terlebih dahulu agar thread berhenti menerima permintaan baru
    # dan kita tidak lagi memproses sinyal dari thread yang akan dihentikan.
    for thread in threads:
        if thread.isRunning():
            try:
                # Mencegah slot dipanggil setelah kita tidak lagi menginginkannya.
                thread.thumbnail_ready.disconnect()
            except (TypeError, RuntimeError):
                # Abaikan error jika sinyal sudah terputus.
                pass
            
            # Meminta thread untuk berhenti. Ini akan mengatur flag internal
            # yang bisa kita periksa di dalam metode run().
            thread.requestInterruption()

    # Fase 2: Tunggu setiap thread untuk benar-benar selesai.
    # Ini adalah bagian yang memblokir dan merupakan kunci dari perbaikan.
    for thread in threads:
        if thread.isRunning():
            # .wait() akan menjeda eksekusi di sini sampai metode .run()
            # dari thread tersebut selesai sepenuhnya.
            thread.wait()

    # Fase 3: Sekarang 100% aman untuk membersihkan daftar.
    # Semua objek thread sudah tidak aktif, sehingga tidak akan ada lagi
    # 'destroyed while running' error.
    threads.clear()
