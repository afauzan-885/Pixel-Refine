"""
Thumbnail Processor Utility
============================
Utility untuk memproses dan menampilkan thumbnail gambar dengan cara yang konsisten.
Diekstrak dari batch_page/thumbnail.py untuk digunakan kembali di berbagai modul.

Fitur:
- Memproses thumbnail secara asinkron menggunakan QThread
- Support untuk berbagai format gambar (JPEG, PNG, TIFF, RAW)
- Koreksi orientasi otomatis menggunakan EXIF
- Cache thumbnail untuk performa
- Thread-safe dengan semaphore untuk membatasi thread aktif
"""

import os
from PySide6.QtWidgets import QLabel, QStackedWidget
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    QMutex,
    QWaitCondition,
    QFile,
    QSemaphore,
    QTimer,
)
import cv2
import numpy as np
import rawpy
from PIL import Image, ImageOps

from config import CACHE_DIR, SUPPORTED_FORMATS
from pixel_refine_desktop.ui.resources.animations.fade import fade_in
from pixel_refine_desktop.enhance_stack.core.logic.display_manager import (
    DisplayThreadManager,
)

# Batasi 4 thread yang aktif memproses gambar secara bersamaan
_thumbnail_semaphore = QSemaphore(4)

try:
    os.makedirs(CACHE_DIR, exist_ok=True)
except OSError as e:
    print(f"Error creating cache directory {CACHE_DIR}: {e}")


class ThumbnailLoaderThread(QThread):
    """
    Thread worker untuk memproses thumbnail gambar.

    Signals:
        thumbnail_ready: Emitted ketika thumbnail siap (QImage, str)
    """

    thumbnail_ready = Signal(QImage, str)

    def __init__(self, image_path, thumbnail_size=(128, 128), parent=None):
        """
        Initialize thumbnail loader thread.

        Args:
            image_path: Path ke file gambar
            thumbnail_size: Tuple (width, height) untuk ukuran thumbnail
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.image_path = image_path
        self.thumbnail_size = thumbnail_size
        self.paused = False
        self.mutex = QMutex()
        self.cond = QWaitCondition()

    def pause(self):
        """Pause thread execution."""
        self.mutex.lock()
        self.paused = True
        self.mutex.unlock()

    def resume(self):
        """Resume thread execution."""
        self.mutex.lock()
        self.paused = False
        self.cond.wakeAll()
        self.mutex.unlock()

    def run(self):
        """Main thread execution."""
        result_image = QImage()
        _thumbnail_semaphore.acquire()

        try:
            if self.isInterruptionRequested():
                return

            # Wait if paused
            self.mutex.lock()
            while self.paused:
                self.cond.wait(self.mutex)
            self.mutex.unlock()

            # Check cache first
            cache_path = self._get_cache_path()
            if QFile.exists(cache_path):
                cached_image = QImage(cache_path)
                if not cached_image.isNull():
                    result_image = cached_image
                    return

            if self.isInterruptionRequested():
                return

            # Process image
            pil_thumb = self._process_image()

            # Convert to QImage
            if pil_thumb:
                result_image = self._convert_to_qimage(pil_thumb)
                # Save to cache
                result_image.save(cache_path, None, 85)

        finally:
            _thumbnail_semaphore.release()
            if not self.isInterruptionRequested():
                self.thumbnail_ready.emit(result_image, self.image_path)

    def _get_cache_path(self):
        """Generate cache file path for this image."""
        filename = os.path.basename(self.image_path) + ".jpg"
        return os.path.join(CACHE_DIR, filename)

    def _process_image(self):
        """
        Process image file dan return PIL Image object atau None.
        Support untuk JPEG, PNG, TIFF, dan RAW formats.
        """
        ext = os.path.splitext(self.image_path)[1].lower()
        pil_thumb = None

        try:
            # Handle non-RAW formats
            if ext in SUPPORTED_FORMATS.get("jpg", []) + SUPPORTED_FORMATS.get(
                "png", []
            ) + SUPPORTED_FORMATS.get("tiff", []):
                with Image.open(self.image_path) as img:
                    # Auto-correct orientation based on EXIF
                    img_corrected = ImageOps.exif_transpose(img)
                    # Create thumbnail maintaining aspect ratio
                    img_corrected.thumbnail(
                        self.thumbnail_size, Image.Resampling.LANCZOS
                    )
                    pil_thumb = img_corrected

            # Handle RAW formats
            elif ext in SUPPORTED_FORMATS.get("raw", []):
                with rawpy.imread(self.image_path) as raw:
                    img_array = raw.postprocess(
                        output_bps=8, use_camera_wb=True, half_size=True
                    )
                pil_img = Image.fromarray(img_array, "RGB")
                pil_img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                pil_thumb = pil_img

        except Exception as e:
            print(f"Error processing thumbnail for {self.image_path}: {e}")

        return pil_thumb

    def _convert_to_qimage(self, pil_image):
        """Convert PIL Image to QImage."""
        if pil_image.mode == "RGB":
            q_image = QImage(
                pil_image.tobytes(),
                pil_image.width,
                pil_image.height,
                pil_image.width * 3,
                QImage.Format.Format_RGB888,
            )
        elif pil_image.mode == "RGBA":
            q_image = QImage(
                pil_image.tobytes(),
                pil_image.width,
                pil_image.height,
                pil_image.width * 4,
                QImage.Format.Format_RGBA8888,
            )
        elif pil_image.mode == "L":  # Grayscale
            q_image = QImage(
                pil_image.tobytes(),
                pil_image.width,
                pil_image.height,
                pil_image.width,
                QImage.Format.Format_Grayscale8,
            )
        else:
            # Fallback: convert to RGB
            pil_image = pil_image.convert("RGB")
            q_image = QImage(
                pil_image.tobytes(),
                pil_image.width,
                pil_image.height,
                pil_image.width * 3,
                QImage.Format.Format_RGB888,
            )

        return q_image


def create_thumbnail_placeholder(thumbnail_size=(80, 80)):
    """
    Create a placeholder widget untuk menampilkan loading state.

    Args:
        thumbnail_size: Tuple (width, height) untuk ukuran placeholder

    Returns:
        QLabel widget dengan styling placeholder
    """
    placeholder = QLabel("Loading...")
    placeholder.setFixedSize(*thumbnail_size)
    placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
    placeholder.setStyleSheet(
        "background-color: lightgray; "
        "border: 1px solid gray; "
        "font-size: 10px; "
        "color: gray;"
    )
    return placeholder


def display_thumbnail_in_layout(
    layout, q_image, image_path, display_size=(80, 80), animator=None
):
    """
    Display thumbnail image dalam layout.

    Args:
        layout: QLayout yang akan menampung thumbnail
        q_image: QImage object untuk ditampilkan
        image_path: Path ke file gambar (untuk tracking)
        display_size: Tuple (width, height) untuk display
        animator: Optional animator untuk fade effect
    """
    if q_image.isNull():
        return

    # Create label dengan thumbnail
    thumb_label = QLabel()
    pixmap = QPixmap.fromImage(q_image)
    scaled_pixmap = pixmap.scaledToHeight(
        display_size[1], Qt.TransformationMode.SmoothTransformation
    )

    thumb_label.setPixmap(scaled_pixmap)
    thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    thumb_label.setScaledContents(False)
    thumb_label.setMaximumHeight(display_size[1])
    thumb_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")

    # Store image path for reference
    thumb_label.setProperty("image_path", image_path)

    # Add to layout
    try:
        if hasattr(layout, "addWidget"):
            layout.addWidget(thumb_label)
        elif hasattr(layout, "addItem"):
            layout.addItem(thumb_label)
    except Exception as e:
        print(f"Error adding thumbnail to layout: {e}")
        return

    # Apply fade animation if provided
    if animator:
        # fade_in expects (animator, target_widget, stack_widget=None)
        # We want standalone fade in for the label
        fade_in(animator, thumb_label)


def stop_thumbnail_threads(threads):
    """
    Stop semua thumbnail threads dengan aman dan sinkron.
    Lebih robust untuk menangani edge cases (deleted objects, etc).
    Handles yang sudah dihapus dari C++ side silently untuk cleaner output.

    Args:
        threads: List of ThumbnailLoaderThread objects
    """
    if not threads:
        return

    # Phase 1: Request interruption dan disconnect signals
    for thread in threads:
        try:
            if thread is None:
                continue

            try:
                if thread.isRunning():
                    try:
                        thread.thumbnail_ready.disconnect()
                    except (TypeError, RuntimeError):
                        pass
                    thread.requestInterruption()
            except RuntimeError:
                # Silently handle deleted objects - they're already gone
                pass

        except Exception:
            # Silently ignore other errors
            pass

    # Phase 2: Wait untuk semua thread finish
    for thread in threads:
        try:
            if thread is None:
                continue

            try:
                if thread.isRunning():
                    thread.wait(timeout=500)  # Shorter timeout
            except RuntimeError:
                # Silently handle - object already deleted
                pass

        except Exception:
            # Silently ignore
            pass

    # Phase 3: Clear list
    threads.clear()


class ThumbnailBatchProcessor:
    """
    Utility class untuk memproses batch thumbnail images.
    Mengelola multiple thumbnail loader threads.
    """

    def __init__(self, thumbnail_size=(128, 128), max_concurrent=4):
        """
        Initialize batch processor.

        Args:
            thumbnail_size: Tuple (width, height) untuk ukuran thumbnail
            max_concurrent: Maximum concurrent threads
        """
        self.thumbnail_size = thumbnail_size
        self.threads = []
        self.callbacks = {}  # image_path -> callback function

        # Adjust semaphore if needed
        global _thumbnail_semaphore
        if max_concurrent != 4:
            _thumbnail_semaphore = QSemaphore(max_concurrent)

    def process_image(self, image_path, callback=None):
        """
        Process single image thumbnail.

        Args:
            image_path: Path ke file gambar
            callback: Optional callback function (image, path) -> None
        """
        thread = ThumbnailLoaderThread(image_path, self.thumbnail_size)

        if callback:
            self.callbacks[image_path] = callback
            thread.thumbnail_ready.connect(
                lambda img, path: self._on_thumbnail_ready(img, path)
            )

        self.threads.append(thread)

        # Register to Global DisplayThreadManager for safe lifecycle
        DisplayThreadManager.instance().register_thread(thread)

        thread.start()

    def process_batch(self, image_paths, callback=None):
        """
        Process multiple images.

        Args:
            image_paths: List of image paths
            callback: Optional callback function (image, path) -> None
        """
        for image_path in image_paths:
            self.process_image(image_path, callback)

    def _on_thumbnail_ready(self, q_image, image_path):
        """Internal callback when thumbnail is ready."""
        if image_path in self.callbacks:
            self.callbacks[image_path](q_image, image_path)

    def stop_all(self):
        """Stop semua threads dan clear."""
        try:
            if self.threads:
                # Use Global Manager to stop threads safely (Non-blocking)
                DisplayThreadManager.instance().stop_all_threads()
                # stop_thumbnail_threads(self.threads) # Legacy blocking wait removed
        except Exception:
            # Silently handle - stop_thumbnail_threads is robust
            pass

        try:
            self.callbacks.clear()
        except Exception:
            # Silently ignore
            pass

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.stop_all()
        except Exception as e:
            # Ignore errors di destructor untuk prevent exception spam
            pass
