import os
from PySide6.QtGui import QImage
from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition, QFile, QSemaphore
from PIL import Image, ImageOps
import rawpy
from config import CACHE_DIR, SUPPORTED_FORMATS

semaphore = QSemaphore(4) # Limit to 4 concurrent thumbnail processing threads

try:
    os.makedirs(CACHE_DIR, exist_ok=True)
except OSError as e:
    print(f"Error creating cache directory {CACHE_DIR}: {e}")

class ThumbnailLoader(QThread):
    """
    QThread for generating image thumbnails asynchronously using Pillow.
    """
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
        result_image = QImage()
        semaphore.acquire()
        try:
            if self.isInterruptionRequested():
                return

            self.mutex.lock()
            while self.paused:
                self.cond.wait(self.mutex)
            self.mutex.unlock()

            THUMBNAIL_SIZE = (128, 128)
            cache_path = os.path.join(CACHE_DIR, os.path.basename(self.image_path) + ".jpg")

            if QFile.exists(cache_path):
                cached_image = QImage(cache_path)
                if not cached_image.isNull():
                    result_image = cached_image
                    return

            if self.isInterruptionRequested():
                return

            pil_thumb = None
            ext = os.path.splitext(self.image_path)[1].lower()

            try:
                # JPG, TIFF, PNG, etc.
                if ext in SUPPORTED_FORMATS["jpg"] + SUPPORTED_FORMATS["png"] + SUPPORTED_FORMATS["tiff"]:
                    with Image.open(self.image_path) as img:
                        img_corrected = ImageOps.exif_transpose(img)
                        img_corrected.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                        pil_thumb = img_corrected

                # RAW Formats
                elif ext in SUPPORTED_FORMATS["raw"]:
                    with rawpy.imread(self.image_path) as raw:
                        img_array = raw.postprocess(
                            output_bps=8,
                            use_camera_wb=True,
                            half_size=True,
                            demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD
                        )
                    
                    pil_img = Image.fromarray(img_array, 'RGB')
                    pil_img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                    pil_thumb = pil_img

            except Exception as e:
                print(f"[BulkThumbnailService] Fail to process {self.image_path}: {e}")

            if pil_thumb:
                if pil_thumb.mode == "RGB":
                    q_image = QImage(pil_thumb.tobytes(), pil_thumb.width, pil_thumb.height, pil_thumb.width * 3, QImage.Format.Format_RGB888)
                elif pil_thumb.mode == "RGBA":
                    q_image = QImage(pil_thumb.tobytes(), pil_thumb.width, pil_thumb.height, pil_thumb.width * 4, QImage.Format.Format_RGBA8888)
                elif pil_thumb.mode == "L":
                    q_image = QImage(pil_thumb.tobytes(), pil_thumb.width, pil_thumb.height, pil_thumb.width, QImage.Format.Format_Grayscale8)
                else:
                    pil_thumb = pil_thumb.convert("RGB")
                    q_image = QImage(pil_thumb.tobytes(), pil_thumb.width, pil_thumb.height, pil_thumb.width * 3, QImage.Format.Format_RGB888)

                q_image.save(cache_path, "JPG", 85)
                result_image = q_image.copy()

        finally:
            semaphore.release()
            if not self.isInterruptionRequested():
                self.thumbnail_ready.emit(result_image, self.image_path)


def stop_process_thumbnails(threads):
    """
    Stops all thumbnail threads safely and synchronously.
    """
    if not threads:
        return

    for thread in threads:
        if thread.isRunning():
            try:
                thread.thumbnail_ready.disconnect()
            except (TypeError, RuntimeError):
                pass
            thread.requestInterruption()

    for thread in threads:
        if thread.isRunning():
            thread.wait()

    threads.clear()
