"""
pixel_refine_mobile/core_logic/database_manager.py
---------------------------------------------------
Simplified database manager for mobile.
Creates tables and provides basic DB operations.
"""

import os
from pixel_refine_mobile.models.data_access.base_repository import BaseRepository
from pixel_refine_mobile.models.data_access.batch_repository import BatchRepository
from pixel_refine_mobile.models.data_access.image_repository import ImageRepository
from pixel_refine_mobile.core.config import DATABASE_PATH, DATABASE_DIR


class DatabaseManager:
    """
    Manages database initialization and provides repository access.
    Simplified version of desktop's DatabaseManager.
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        os.makedirs(DATABASE_DIR, exist_ok=True)
        # Create tables first, then initialize repositories
        self._create_tables()
        self.batch_repo = BatchRepository(self.db_path)
        self.image_repo = ImageRepository(self.db_path)

    def _create_tables(self):
        """Create all required tables."""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            # Images table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL
                )
            """)

            # Batch process table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS batch_process (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_name TEXT UNIQUE NOT NULL,
                    order_index INTEGER DEFAULT 0
                )
            """)

            # Batch process image table (junction)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS batch_process_image (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id INTEGER NOT NULL,
                    image_id_batch INTEGER NOT NULL,
                    is_reference_batch INTEGER DEFAULT 0,
                    FOREIGN KEY (batch_id) REFERENCES batch_process(id) ON DELETE CASCADE,
                    FOREIGN KEY (image_id_batch) REFERENCES images(id) ON DELETE CASCADE,
                    UNIQUE(batch_id, image_id_batch)
                )
            """)

            print("[DatabaseManager] Tables created successfully")
        except Exception as e:
            print(f"[DatabaseManager] Error creating tables: {e}")
        finally:
            conn.close()

    def get_batch_repo(self) -> BatchRepository:
        return self.batch_repo

    def get_image_repo(self) -> ImageRepository:
        return self.image_repo
