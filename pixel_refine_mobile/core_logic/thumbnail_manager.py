"""
pixel_refine_mobile/core_logic/thumbnail_manager.py
----------------------------------------------------
Simplified thumbnail processor for mobile.
2-tier cache: RAM dict + Disk JPG files.
Desktop equivalent: ThumbnailBatchProcessor (964 lines).
"""

import os
from typing import Optional, Callable, List
from PySide6.QtCore import QThread, Signal


class ThumbnailManager:
    """
    Manages thumbnail generation and caching for mobile.
    2-tier cache: L1 (RAM dict) + L2 (Disk JPG).
    """

    thumbnail_ready = Signal(str, object)  # path, thumbnail_data
    batch_thumbnails_ready = Signal(int)   # batch_id

    def __init__(self, cache_dir: str, max_ram_entries: int = 200):
        self._cache_dir = cache_dir
        self._max_ram = max_ram_entries
        self._ram_cache = {}  # path -> thumbnail data
        os.makedirs(cache_dir, exist_ok=True)

    def get_thumbnail(self, image_path: str, size: tuple = (96, 96)):
        """
        Return cached thumbnail or None (caller shows skeleton).
        L1: RAM -> L2: Disk -> None (generate async)
        """
        # L1: RAM check
        if image_path in self._ram_cache:
            return self._ram_cache[image_path]

        # L2: Disk check
        disk_path = self._disk_path(image_path)
        if os.path.exists(disk_path):
            data = self._load_disk(disk_path)
            if data:
                self._promote_to_ram(image_path, data)
                return data

        # Miss: caller should show skeleton
        return None

    def process_batch(self, image_paths: List[str], on_ready_callback: Callable,
                      batch_id: int):
        """Process thumbnails in background thread."""
        worker = ThumbnailWorker(image_paths, self._cache_dir, on_ready_callback)
        worker.finished.connect(lambda: self.batch_thumbnails_ready.emit(batch_id))
        worker.start()

    def clear_cache(self):
        """Clear RAM cache."""
        self._ram_cache.clear()

    def _disk_path(self, image_path: str) -> str:
        """Get disk cache path for an image."""
        basename = os.path.basename(image_path)
        name, ext = os.path.splitext(basename)
        return os.path.join(self._cache_dir, f"{name}_thumb.jpg")

    def _load_disk(self, disk_path: str):
        """Load thumbnail from disk."""
        try:
            with open(disk_path, "rb") as f:
                return f.read()
        except Exception:
            return None

    def _promote_to_ram(self, path: str, data):
        """Promote to RAM cache with LRU eviction."""
        if len(self._ram_cache) >= self._max_ram:
            # Evict oldest entry
            oldest = next(iter(self._ram_cache))
            del self._ram_cache[oldest]
        self._ram_cache[path] = data


class ThumbnailWorker(QThread):
    """Background worker for generating thumbnails."""
    thumbnail_generated = Signal(str, object)

    def __init__(self, image_paths: List[str], cache_dir: str,
                 on_ready_callback: Callable = None):
        super().__init__()
        self._paths = image_paths
        self._cache_dir = cache_dir
        self._callback = on_ready_callback

    def run(self):
        """Generate thumbnails for all paths."""
        for path in self._paths:
            try:
                thumbnail = self._generate_thumbnail(path)
                if thumbnail:
                    # Save to disk
                    disk_path = os.path.join(
                        self._cache_dir,
                        os.path.splitext(os.path.basename(path))[0] + "_thumb.jpg"
                    )
                    with open(disk_path, "wb") as f:
                        f.write(thumbnail)
                    self.thumbnail_generated.emit(path, thumbnail)
                    if self._callback:
                        self._callback(path, thumbnail)
            except Exception as e:
                print(f"[ThumbnailWorker] Error processing {path}: {e}")

    def _generate_thumbnail(self, image_path: str) -> Optional[bytes]:
        """Generate thumbnail from image. Placeholder — returns None."""
        # Placeholder: in production, would use PIL/OpenCV to resize
        return None
