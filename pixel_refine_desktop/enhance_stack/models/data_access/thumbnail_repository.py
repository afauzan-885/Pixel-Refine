import sqlite3
import os
import io
from PySide6.QtGui import QImage
from PySide6.QtCore import QBuffer, QIODevice
from .base_repository import BaseRepository


class ThumbnailRepository(BaseRepository):
    """
    Repository for storing and retrieving thumbnails from SQLite.
    Optimized for bulk operations to reduce I/O wait.
    """

    def __init__(self, db_path="database/cache/thumbnails.db"):
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        super().__init__(db_path)
        self._create_table()

    def _create_table(self):
        """Create thumbnail cache table if not exists."""
        query = """
        CREATE TABLE IF NOT EXISTS thumbnail_cache (
            image_path TEXT PRIMARY KEY,
            image_blob BLOB,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_update(query)

        # Optimasi performa database khusus untuk blob
        try:
            with self.get_connection() as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                conn.execute("PRAGMA cache_size=-32000;")  # 32MB cache
        except Exception:
            pass

    def get_thumbnail(self, image_path: str) -> QImage:
        """Get a single thumbnail from cache."""
        query = "SELECT image_blob FROM thumbnail_cache WHERE image_path = ?"
        result = self.execute_query(query, (image_path,), fetch_one=True)

        if result and result[0]:
            return self._blob_to_qimage(result[0])
        return QImage()

    def get_thumbnails_bulk(self, image_paths: list) -> dict:
        """
        Get multiple thumbnails in a single query using DYNAMIC BULK reading.
        Returns a dict of {path: QImage}
        """
        if not image_paths:
            return {}

        total_count = len(image_paths)
        thumbnails = {}

        # --- LOGIKA DYNAMIC BULK SIZE (Konsisten dengan Deletion/Write) ---
        chunk_size = 50
        if total_count >= 1499:
            chunk_size = 400
        elif total_count >= 999:
            chunk_size = 200
        elif total_count >= 500:
            chunk_size = 100

        # Pecah pencarian menjadi bagian-bagian (borongan)
        for i in range(0, total_count, chunk_size):
            chunk = image_paths[i : i + chunk_size]
            placeholders = ",".join("?" for _ in chunk)
            query = f"SELECT image_path, image_blob FROM thumbnail_cache WHERE image_path IN ({placeholders})"

            try:
                results = self.execute_query(query, tuple(chunk))
                for path, blob in results:
                    thumbnails[path] = self._blob_to_qimage(blob)
            except Exception as e:
                print(f"[ThumbnailRepo] Bulk Read Error: {e}")

        return thumbnails

    def save_thumbnail(self, image_path: str, q_image: QImage):
        """Save a single thumbnail to cache."""
        if q_image.isNull():
            return

        blob = self._qimage_to_blob(q_image)
        query = "INSERT OR REPLACE INTO thumbnail_cache (image_path, image_blob) VALUES (?, ?)"
        self.execute_update(query, (image_path, blob))

    def save_thumbnails_bulk(self, thumbnail_data: list):
        """
        Save multiple thumbnails in a single transaction.
        thumbnail_data: list of (image_path, q_image)
        """
        if not thumbnail_data:
            return

        processed_data = []
        for path, q_img in thumbnail_data:
            if not q_img.isNull():
                blob = self._qimage_to_blob(q_img)
                processed_data.append((path, blob))

        if not processed_data:
            return

        query = "INSERT OR REPLACE INTO thumbnail_cache (image_path, image_blob) VALUES (?, ?)"
        # execute_many handles transaction
        self.execute_many(query, processed_data)

    def delete_thumbnails(self, image_paths: list):
        """Clean up cache for deleted images."""
        if not image_paths:
            return
        placeholders = ",".join("?" for _ in image_paths)
        query = f"DELETE FROM thumbnail_cache WHERE image_path IN ({placeholders})"
        self.execute_update(query, tuple(image_paths))

    def _qimage_to_blob(self, q_image: QImage) -> bytes:
        """Convert QImage to PNG/JPG blob bytes."""
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        # We use JPG for smaller size in DB
        q_image.save(buffer, "JPG", 80)
        return buffer.data().data()

    def _blob_to_qimage(self, blob: bytes) -> QImage:
        """Convert blob bytes back to QImage."""
        q_image = QImage()
        q_image.loadFromData(blob)
        return q_image
