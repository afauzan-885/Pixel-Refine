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

    # --- Methods for compatibility or future use ---
    def execute_query(self, *args, **kwargs):
        return []

    def execute_update(self, *args, **kwargs):
        return 0

    def execute_many(self, *args, **kwargs):
        return 0
