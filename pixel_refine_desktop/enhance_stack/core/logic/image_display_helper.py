"""
Image Display Helper untuk Zoomable Preview
============================================

Helper module untuk menampilkan gambar full resolution di Zoomable widget
dengan support untuk berbagai format dan ukuran gambar.
"""

import os
import numpy as np
import rawpy
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import QThread, Signal, Qt
from PIL import Image, ImageOps

from config import SUPPORTED_FORMATS, COMPARISON_CACHE_DIR


class ComparisonCache:
    """
    Manager specifically for caching the 'Original' (Reference) image
    used in Comparison Mode.
    Saves converted results (e.g. from RAW) to disk to avoid re-conversion.
    """

    _instance = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = ComparisonCache()
        return cls._instance

    def __init__(self):
        self.cache_dir = COMPARISON_CACHE_DIR
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    def _get_paths(self, batch_id):
        """Helper to get cache file and metadata file for a specific batch."""
        safe_batch_id = str(batch_id) if batch_id is not None else "default"
        ref_file = os.path.join(self.cache_dir, f"ref_batch_{safe_batch_id}.png")
        meta_file = os.path.join(self.cache_dir, f"ref_batch_{safe_batch_id}.txt")
        return ref_file, meta_file

    def get_cached_path(self, batch_id, original_path):
        """Returns the local cache path if it matches original_path for the batch, else None."""
        ref_file, meta_file = self._get_paths(batch_id)

        if not os.path.exists(meta_file):
            return None

        try:
            with open(meta_file, "r") as f:
                cached_path = f.read().strip()
                if os.path.normpath(cached_path) == os.path.normpath(original_path):
                    # Check if actual file exists
                    if os.path.exists(ref_file):
                        return ref_file
        except Exception:
            pass
        return None

    def save_to_cache(self, batch_id, original_path, image_array):
        """Saves converted image_array to cache for a specific batch and updates metadata."""
        ref_file, meta_file = self._get_paths(batch_id)

        # Save new image (RGB format)
        try:
            # Use PNG for lossless reference in comparison
            Image.fromarray(image_array).save(ref_file)

            # Update metadata
            with open(meta_file, "w") as f:
                f.write(original_path)
            return True
        except Exception as e:
            print(f"[ComparisonCache] Error saving cache for batch {batch_id}: {e}")
            return False

    def clear_cache(self):
        """Deletes cache files."""
        if os.path.exists(self.cache_dir):
            for f in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, f)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception:
                    pass


class ImageLoaderThread(QThread):
    """
    Thread untuk load gambar full resolution dari disk.
    Support untuk JPEG, PNG, TIFF, RAW formats.
    """

    image_loaded = Signal(QPixmap, str)  # (pixmap, image_path)
    error_occurred = Signal(str)  # error_message

    def __init__(
        self,
        image_path,
        max_width=None,
        max_height=None,
        is_reference=False,
        batch_id=None,
        half_res=False,
        parent=None,
    ):
        """
        Initialize image loader thread.

        Args:
            image_path: Path ke file gambar
            max_width: Max width untuk resize (optional)
            max_height: Max height untuk resize (optional)
            is_reference: Jika True, gunakan/update comparison cache
            batch_id: ID batch untuk caching referensi
            half_res: Jika True, load resolusi rendah (cepat) untuk preview burst
            parent: Parent widget
        """
        super().__init__(parent)
        self.image_path = image_path
        self.max_width = max_width
        self.max_height = max_height
        self.is_reference = is_reference
        self.batch_id = batch_id
        self.half_res = half_res

    def run(self):
        """Metode utama untuk loading gambar di background thread."""
        try:
            if not os.path.exists(self.image_path):
                self.error_occurred.emit(f"File not found: {self.image_path}")
                return

            # --- OPTIMIZATION: Check Cache if it's a reference ---
            if self.is_reference:
                cached_file = ComparisonCache.instance().get_cached_path(
                    self.batch_id, self.image_path
                )
                if cached_file:
                    print(
                        f"[ComparisonCache] Thread loading from cache (Batch {self.batch_id}): {self.image_path}"
                    )
                    pixmap = QPixmap(cached_file)
                    if not pixmap.isNull():
                        if self.max_width or self.max_height:
                            pixmap = self._resize_pixmap(pixmap)
                        self.image_loaded.emit(pixmap, self.image_path)
                        return

            # Load image sesuai format
            image_array = self._load_image()
            if image_array is None:
                self.error_occurred.emit(f"Failed to load image: {self.image_path}")
                return

            # --- OPTIMIZATION: Save to Cache if it's a reference ---
            if self.is_reference:
                print(
                    f"[ComparisonCache] Thread saving to cache (Batch {self.batch_id}): {self.image_path}"
                )
                ComparisonCache.instance().save_to_cache(
                    self.batch_id, self.image_path, image_array
                )

            # Convert to QPixmap
            pixmap = self._array_to_pixmap(image_array)

            if pixmap is None or pixmap.isNull():
                self.error_occurred.emit(f"Failed to convert image to pixmap")
                return

            # Resize jika diperlukan (untuk large images)
            if self.max_width or self.max_height:
                pixmap = self._resize_pixmap(pixmap)

            self.image_loaded.emit(pixmap, self.image_path)

        except Exception as e:
            self.error_occurred.emit(f"Error loading image: {str(e)}")

    def _load_image(self):
        """Load image file dan return numpy array."""
        ext = os.path.splitext(self.image_path)[1].lower()
        image_array = None

        try:
            # Handle non-RAW formats
            if ext in SUPPORTED_FORMATS.get("jpg", []) + SUPPORTED_FORMATS.get(
                "png", []
            ) + SUPPORTED_FORMATS.get("tiff", []):
                # Use PIL and correct orientation automatically for display
                with Image.open(self.image_path) as img:
                    img = ImageOps.exif_transpose(img)
                    # Convert ke RGB jika perlu
                    if img.mode in ("RGBA", "LA", "P"):
                        img = img.convert("RGB")
                    elif img.mode == "L":
                        img = img.convert("RGB")
                    # Convert PIL image to numpy array (RGB)
                    image_array = np.array(img)
                    
                    # If half_res requested, downsample for quick preview via fast slice
                    if getattr(self, "half_res", False):
                        image_array = np.ascontiguousarray(image_array[::2, ::2])

            # Handle RAW formats
            elif ext in SUPPORTED_FORMATS.get("raw", []):
                if getattr(self, "half_res", False):
                    from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import load_raw_as_8bit_rgb_half_res
                    image_array = load_raw_as_8bit_rgb_half_res(self.image_path)
                else:
                    from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import load_raw_as_8bit_rgb
                    image_array = load_raw_as_8bit_rgb(self.image_path)

        except Exception as e:
            print(f"Error loading image {self.image_path}: {e}")
            return None

        return image_array

    def _array_to_pixmap(self, image_array):
        """Convert numpy array ke QPixmap."""
        try:
            if image_array is None or image_array.size == 0:
                return None

            image_array = np.ascontiguousarray(image_array)
            height, width = image_array.shape[:2]

            # Handle different image formats
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                # RGB image
                bytes_per_line = 3 * width
                q_image = QImage(
                    image_array.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format.Format_RGB888,
                )
            elif len(image_array.shape) == 2:
                # Grayscale
                bytes_per_line = width
                q_image = QImage(
                    image_array.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format.Format_Grayscale8,
                )
            else:
                return None

            pixmap = QPixmap.fromImage(q_image)
            return pixmap

        except Exception as e:
            print(f"Error converting array to pixmap: {e}")
            return None

    def _resize_pixmap(self, pixmap):
        """Resize pixmap jika terlalu besar."""
        width = pixmap.width()
        height = pixmap.height()

        max_w = self.max_width or width
        max_h = self.max_height or height

        if width > max_w or height > max_h:
            # Maintain aspect ratio
            pixmap = pixmap.scaledToWidth(
                max_w, Qt.TransformationMode.SmoothTransformation
            )

        return pixmap


def setup_zoomable_preview(
    zoomable_widget, image_path, is_reference=False, batch_id=None, half_res=False, callback=None
):
    """
    Setup dan load gambar ke Zoomable widget menggunakan background thread.

    Args:
        zoomable_widget: Zoomable QGraphicsView instance
        image_path: Path ke file gambar
        is_reference: Jika True, gunakan/update comparison cache
        batch_id: ID batch untuk caching referensi
        half_res: Jika True, load resolusi rendah (cepat) untuk preview burst
        callback: Optional callback saat image loaded (pixmap, path) -> None
    """
    # Clear scene
    zoomable_widget.scene().clear()

    # Create loader thread
    def on_image_loaded(pixmap, path):
        if pixmap is None or pixmap.isNull():
            return

        # Add pixmap ke scene
        scene = zoomable_widget.scene()
        scene.clear()  # Clear any existing items

        # Create pixmap item
        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)

        # Add ke scene
        scene.addItem(pixmap_item)

        # Set scene rect
        scene.setSceneRect(pixmap_item.boundingRect())

        # Reset zoom
        zoomable_widget.reset_zoom()

        # Fit dalam view
        zoomable_widget.fitInView(
            scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio
        )

        if callback:
            try:
                callback(pixmap, path)
            except Exception as e_cb:
                print(f"[image_display_helper] Callback error: {e_cb}")

    def on_error(error_msg):
        print(f"Error loading image: {error_msg}")

    # Start loading thread with optimized bounds for half_res burst previews
    max_w = 1920 if half_res else 4000
    max_h = 1080 if half_res else 4000

    loader = ImageLoaderThread(
        image_path,
        max_width=max_w,
        max_height=max_h,
        is_reference=is_reference,
        batch_id=batch_id,
        half_res=half_res,
    )
    loader.image_loaded.connect(on_image_loaded)
    loader.error_occurred.connect(on_error)
    loader.start()

    return loader


def display_image_in_zoomable(
    zoomable_widget, image_path, callback=None, is_reference=False, batch_id=None, half_res=False
):
    """
    Display gambar di Zoomable widget dengan loading indicator.

    Args:
        zoomable_widget: Zoomable QGraphicsView instance
        image_path: Path ke file gambar
        callback: Optional callback saat image loaded (pixmap, path) -> None
        is_reference: Jika True, gunakan/update comparison cache
        batch_id: ID batch untuk caching referensi
        half_res: Jika True, load resolusi rendah (cepat) untuk preview burst
    """
    loader = setup_zoomable_preview(
        zoomable_widget,
        image_path,
        is_reference=is_reference,
        batch_id=batch_id,
        half_res=half_res,
        callback=callback,
    )
    return loader


def load_and_display_image(
    image_path, max_width=2000, max_height=2000, is_reference=False, batch_id=None
):
    """
    Load dan return QPixmap dari image path.
    Helper untuk synchronous image loading.
    Support caching untuk reference image.

    Args:
        image_path: Path ke file gambar
        max_width: Max width untuk resize
        max_height: Max height untuk resize
        is_reference: Jika True, gunakan/update comparison cache
        batch_id: ID batch untuk caching referensi
    """
    try:
        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            return None

        # --- OPTIMIZATION: Check Cache if it's a reference ---
        if is_reference:
            cached_file = ComparisonCache.instance().get_cached_path(
                batch_id, image_path
            )
            if cached_file:
                print(
                    f"[ComparisonCache] Loading from cache (Batch {batch_id}): {image_path}"
                )
                pixmap = QPixmap(cached_file)
                if not pixmap.isNull():
                    # Resize if needed
                    if pixmap.width() > max_width or pixmap.height() > max_height:
                        pixmap = pixmap.scaled(
                            max_width,
                            max_height,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                    return pixmap

        ext = os.path.splitext(image_path)[1].lower()
        image_array = None

        # Load image
        if ext in SUPPORTED_FORMATS.get("jpg", []) + SUPPORTED_FORMATS.get(
            "png", []
        ) + SUPPORTED_FORMATS.get("tiff", []):
            with Image.open(image_path) as img:
                img = ImageOps.exif_transpose(img)
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")
                image_array = np.array(img)

        elif ext in SUPPORTED_FORMATS.get("raw", []):
            from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import load_raw_as_8bit_rgb
            image_array = load_raw_as_8bit_rgb(image_path)

        else:
            print(f"Unsupported format: {ext}")
            return None

        if image_array is None:
            return None

        image_array = np.ascontiguousarray(image_array)

        # --- OPTIMIZATION: Save to Cache if it's a reference ---
        if is_reference:
            print(f"[ComparisonCache] Saving to cache (Batch {batch_id}): {image_path}")
            ComparisonCache.instance().save_to_cache(batch_id, image_path, image_array)

        # Convert to QPixmap
        height, width = image_array.shape[:2]
        bytes_per_line = 3 * width
        q_image = QImage(
            image_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
        )

        pixmap = QPixmap.fromImage(q_image)

        # Resize jika perlu
        if width > max_width or height > max_height:
            pixmap = pixmap.scaledToWidth(
                max_width, Qt.TransformationMode.SmoothTransformation
            )

        return pixmap

    except Exception as e:
        print(f"Error loading image: {e}")
        return None
