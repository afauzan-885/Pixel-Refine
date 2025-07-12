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

semaphore = QSemaphore(4)
try:
    os.makedirs(CACHE_DIR, exist_ok=True)
except OSError as e:
    print(f"Error creating cache directory {CACHE_DIR}: {e}")

class ThumbnailLoader(QThread):
    thumbnail_ready = Signal(QImage, str)

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
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
        cache_path = os.path.join(CACHE_DIR, os.path.basename(self.image_path) + ".jpg")

        self.mutex.lock()
        while self.paused:
            self.cond.wait(self.mutex)
        self.mutex.unlock()

        if QFile.exists(cache_path):
            image = QImage(cache_path)
            if not image.isNull():
                self.thumbnail_ready.emit(image, self.image_path)
                return

        ext = os.path.splitext(self.image_path)[1].lower()

        semaphore.acquire()
        try:
            # === PERUBAHAN UTAMA: Logika untuk JPG, PNG, TIFF menggunakan Pillow ===
            if ext in SUPPORTED_FORMATS["jpg"] + SUPPORTED_FORMATS["png"] + SUPPORTED_FORMATS["tiff"]:
                try:
                    # 1. Buka dengan Pillow dan terapkan orientasi EXIF
                    pil_img = Image.open(self.image_path)
                    pil_img = ImageOps.exif_transpose(pil_img)

                    # 2. Konversi dari Pillow (RGB) ke array NumPy untuk OpenCV (BGR)
                    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                    if img is None: return

                    # ... (sisa logika pemrosesan Anda sama)
                    if len(img.shape) == 2: img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                    if img.dtype == np.uint16: img = (img / 256).astype(np.uint8)

                    # 3. Buat QImage dari data yang sudah benar orientasinya
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    height, width, channel = img_rgb.shape
                    bytes_per_line = 3 * width
                    final_image = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).copy()
                
                except Exception as e:
                    print(f"Error processing standard image {self.image_path}: {e}")
                    return

            # Logika untuk RAW (sudah cukup baik, kita hanya menyatukan scaling)
            elif ext in SUPPORTED_FORMATS["raw"]:
                try:
                    with rawpy.imread(self.image_path) as raw:
                        img_array = raw.postprocess(output_bps=8, use_camera_wb=True, half_size=True)
                    
                    height, width, channel = img_array.shape
                    bytes_per_line = 3 * width
                    final_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).copy()
                except Exception as e:
                    print(f"Error processing RAW image {self.image_path}: {e}")
                    return
            
            else:
                return

            # === PERUBAHAN UTAMA 2: Penskalaan yang disatukan dan benar ===
            if final_image and not final_image.isNull():
                # Skalakan agar pas di dalam kotak 100x100 dengan mempertahankan rasio aspek
                # Ini akan menangani potret dan lanskap dengan benar.
                final_image = final_image.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                
                # Simpan thumbnail yang sudah diskalakan ke cache
                final_image.save(cache_path, "JPG", quality=85)
                
                # Kirim sinyal
                self.thumbnail_ready.emit(final_image, self.image_path)

        finally:
            semaphore.release()

        self.thumbnail_ready.emit(image, self.image_path)


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
                # Cek apakah sudah ada thumbnail yang valid (hindari duplikasi)
                for j in range(widget.count()):
                    w = widget.widget(j)
                    if isinstance(w, QLabel) and w.pixmap() is not None and not w.pixmap().isNull():
                        return  # Sudah ada thumbnail valid, tidak perlu fade lagi

                # === Buat thumbnail label baru
                thumb_label = QLabel()
                thumb_label.setPixmap(pixmap.scaledToHeight(80, Qt.TransformationMode.SmoothTransformation))
                thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                thumb_label.setScaledContents(False)
                thumb_label.setMaximumHeight(80)
                thumb_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")

                widget.addWidget(thumb_label)
                widget.setCurrentWidget(thumb_label)

                # === Tambahkan efek fade-in (jika animator tersedia)
                if animator:
                    thumb_label.setGraphicsEffect(None)  # Hapus efek sebelumnya jika ada
                    fade_in(animator, widget, thumb_label)

                return

    except RuntimeError:
        if retry_count < 3:
            QTimer.singleShot(100, lambda: show_thumbnail(ref_layout, image, image_path, animator, retry_count + 1))

def stop_process_thumbnails(threads):
    if not threads:
        return

    for thread in threads:
        if thread.isRunning():
            thread.thumbnail_ready.disconnect()
            thread.quit()

    QTimer.singleShot(100, lambda: threads.clear())
