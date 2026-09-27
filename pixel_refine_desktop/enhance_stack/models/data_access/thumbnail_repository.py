import os
import hashlib
from PySide6.QtGui import QImage
from .base_repository import BaseRepository


class ThumbnailRepository(BaseRepository):
    """
    Repository for storing and retrieving thumbnails as physical files.
    Uses SHA-1 hashing of the image path for unique, file-system safe names.
    """

    def __init__(self, cache_dir="database/cache/thumbnails"):
        # Kita tidak panggil BaseRepository.__init__ (karena tidak butuh DB)
        # Tapi tetap simpan db_path untuk kompatibilitas jika dibutuhkan kueri lain
        self.db_path = None
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_hash_path(self, image_path: str) -> str:
        """Konversi path gambar menjadi path cache unik via SHA-1."""
        path_hash = hashlib.sha1(image_path.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{path_hash}.jpg")

    def get_thumbnail(self, image_path: str) -> QImage:
        """Load thumbnail dari file sistem."""
        target_path = self._get_hash_path(image_path)
        if os.path.exists(target_path):
            return QImage(target_path)
        return QImage()

    def get_thumbnails_bulk(self, image_paths: list) -> dict:
        """
        Muat banyak thumbnail sekaligus dari disk.
        Returns a dict of {path: QImage}
        """
        thumbnails = {}
        for path in image_paths:
            img = self.get_thumbnail(path)
            if not img.isNull():
                thumbnails[path] = img
        return thumbnails

    def save_thumbnail(self, image_path: str, q_image: QImage):
        """Simpan satu thumbnail ke disk sebagai JPG."""
        if q_image.isNull():
            return

        target_path = self._get_hash_path(image_path)
        try:
            # Gunakan JPG dengan kualitas 80 agar seimbang antara size dan kualitas
            q_image.save(target_path, "JPG", 80)
        except Exception as e:
            print(f"[ThumbnailRepo] Errror saving file {target_path}: {e}")

    def save_thumbnails_bulk(self, thumbnail_data: list):
        """
        Simpan banyak thumbnail sekaligus.
        thumbnail_data: list of (image_path, q_image)
        """
        for path, q_img in thumbnail_data:
            self.save_thumbnail(path, q_img)

    def delete_thumbnails(self, image_paths: list):
        """Hapus file cache untuk gambar yang dihapus."""
        for path in image_paths:
            target_path = self._get_hash_path(path)
            if os.path.exists(target_path):
                try:
                    os.remove(target_path)
                except Exception as e:
                    print(f"[ThumbnailRepo] Error deleting {target_path}: {e}")

    # --- Cache maintenance ---
    SHA1_NAME_LENGTH = 40

    @classmethod
    def _is_hashed_name(cls, name: str) -> bool:
        """True when *name* follows the current SHA-1 cache naming scheme."""
        if not name.endswith(".jpg"):
            return False
        stem = name[: -len(".jpg")]
        return len(stem) == cls.SHA1_NAME_LENGTH and all(
            c in "0123456789abcdef" for c in stem
        )

    def prune_cache(self, max_files: int = 5000, max_bytes: int = 256 * 1024 * 1024):
        """Drop leftover thumbnails and cap the cache by age.

        The SHA-1 naming scheme is the single source of truth for what is
        current, so any other name in this directory is a leftover from an older
        naming scheme and is removed.  The remaining files are then capped by
        count and total size, oldest first.  Only this repository's own cache
        directory is touched.

        Returns the number of files removed.
        """
        removed = 0
        try:
            entries = []
            for name in os.listdir(self.cache_dir):
                full = os.path.join(self.cache_dir, name)
                if not os.path.isfile(full):
                    continue
                if not self._is_hashed_name(name):
                    try:
                        os.remove(full)
                        removed += 1
                    except OSError:
                        pass
                    continue
                try:
                    stat = os.stat(full)
                except OSError:
                    continue
                entries.append((stat.st_mtime, stat.st_size, full))

            entries.sort()  # oldest first
            total_bytes = sum(size for _mtime, size, _path in entries)
            remaining = len(entries)
            for _mtime, size, full in entries:
                if remaining <= max_files and total_bytes <= max_bytes:
                    break
                try:
                    os.remove(full)
                    remaining -= 1
                    total_bytes -= size
                    removed += 1
                except OSError:
                    pass
        except Exception as exc:
            print(f"[ThumbnailRepo] Cache prune warning: {exc}")

        if removed:
            print(f"[ThumbnailRepo] Pruned {removed} thumbnail cache file(s)")
        return removed

    # --- Methods for compatibility or future use ---
    def execute_query(self, *args, **kwargs):
        return []

    def execute_update(self, *args, **kwargs):
        return 0

    def execute_many(self, *args, **kwargs):
        return 0
