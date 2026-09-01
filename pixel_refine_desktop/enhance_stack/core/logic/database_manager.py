# database_manager.py

import os
import sqlite3


class DatabaseManager:
    """
    Manages interactions with the SQLite database for storing and retrieving
    image paths for single and batch processing.
    """

    def __init__(self, db_path):
        """
        Initializes the DatabaseManager.

        Args:
            db_path: The path to the database file.
        """
        self.db_path = db_path
        # Pastikan database dan tabel dibuat saat inisialisasi
        self.create_database()

    # --- 1. Initialization & Setup ---

    def _get_connection(self):
        """Establishes a database connection with High-Performance settings."""
        try:
            conn = sqlite3.connect(self.db_path)

            # --- OPTIMASI HDD ---
            # WAL Mode: Write-Ahead Logging. Menulis jauh lebih cepat di HDD, concurrency lebih baik.
            conn.execute("PRAGMA journal_mode=WAL;")

            # Synchronous NORMAL: Mengurangi fsync(), trade-off keamanan vs kecepatan yang sangat worth it untuk desktop app.
            conn.execute("PRAGMA synchronous=NORMAL;")

            # Cache Size: Memperbesar cache in-memory (-64000 page = ~64MB)
            conn.execute("PRAGMA cache_size=-64000;")

            # Foreign Keys tetap ON
            conn.execute("PRAGMA foreign_keys = ON;")

            return conn
        except sqlite3.Error as e:
            print(f"Database connection error to {self.db_path}: {e}")
            raise

    def _add_column_if_not_exists(self, cursor, table_name, column_name, column_def):
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [info[1] for info in cursor.fetchall()]
        if column_name not in columns:
            try:
                cursor.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"
                )
            except sqlite3.Error:
                pass

    def create_database(self):
        """
        Creates the necessary tables and ensures the 'is_reference' column exists
        in 'single_process_image' and 'is_reference_batch' in 'batch_process_image'.
        """
        db_dir_exists = True
        if not os.path.exists(self.db_path):
            print("Database not found. Creating database...")
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            db_dir_exists = False  # Database is newly created

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Create images table (if not exists)
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='images';"
                )
                if not cursor.fetchone():
                    cursor.execute(
                        """
                        CREATE TABLE images (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            path TEXT NOT NULL UNIQUE
                        )
                    """
                    )
                    print("Table 'images' created.")

                # Create single_process_image table (if not exists)
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='single_process_image';"
                )
                if not cursor.fetchone():
                    cursor.execute(
                        """
                        CREATE TABLE single_process_image (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            image_id_single INTEGER NOT NULL UNIQUE,
                            is_reference INTEGER NOT NULL DEFAULT 0,
                            FOREIGN KEY (image_id_single) REFERENCES images (id) ON DELETE CASCADE
                        )
                    """
                    )
                    print(
                        "Table 'single_process_image' created with 'is_reference' column."
                    )
                else:
                    self._add_column_if_not_exists(
                        cursor,
                        "single_process_image",
                        "is_reference",
                        "INTEGER NOT NULL DEFAULT 0",
                    )

                # Create batch_process table
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='batch_process';"
                )
                if not cursor.fetchone():
                    cursor.execute(
                        """
                        CREATE TABLE batch_process (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            batch_name TEXT NOT NULL UNIQUE
                        );
                    """
                    )
                    print("Table 'batch_process' created.")

                # Create batch_process_image table
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='batch_process_image';"
                )
                if not cursor.fetchone():
                    cursor.execute(
                        """
                        CREATE TABLE batch_process_image (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            batch_id INTEGER NOT NULL,
                            image_id_batch INTEGER NOT NULL,
                            is_reference_batch INTEGER NOT NULL DEFAULT 0, -- KOLOM BARU
                            FOREIGN KEY (batch_id) REFERENCES batch_process(id) ON DELETE CASCADE,
                            FOREIGN KEY (image_id_batch) REFERENCES images(id) ON DELETE CASCADE,
                            UNIQUE(batch_id, image_id_batch)
                        );
                    """
                    )
                    print(
                        "Table 'batch_process_image' created with 'is_reference_batch' column."
                    )
                else:
                    # Jika tabel sudah ada, pastikan kolom is_reference_batch ada
                    self._add_column_if_not_exists(
                        cursor,
                        "batch_process_image",
                        "is_reference_batch",
                        "INTEGER NOT NULL DEFAULT 0",
                    )

                conn.commit()
        except sqlite3.Error as e:
            print(f"Error during database/table creation or modification: {e}")

    # --- 2. Helper Methods (Internal) ---
    def _get_or_create_image_id(self, cursor, image_path):
        """
        Helper function to get existing image_id or create a new one.
        Assumes cursor is already active within a transaction.
        """
        cursor.execute("SELECT id FROM images WHERE path = ?", (image_path,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            try:
                cursor.execute("INSERT INTO images (path) VALUES (?)", (image_path,))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                print(
                    f"Race condition or error: Image path '{image_path}' likely already inserted."
                )
                cursor.execute("SELECT id FROM images WHERE path = ?", (image_path,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    raise Exception(
                        f"Could not get or create image ID for {image_path} after integrity error."
                    )

    # --- 3. Batch Operations ---
    def create_new_batch(self, batch_name):
        """
        Creates a new batch entry in the 'batch_process' table.
        If the batch name already exists, returns the ID of the existing batch.

        Args:
            batch_name: The desired unique name for the batch.

        Returns:
            The integer ID of the created or existing batch, or None on error.
        """
        sql_insert = "INSERT INTO batch_process (batch_name) VALUES (?)"
        sql_select = "SELECT id FROM batch_process WHERE batch_name = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(sql_insert, (batch_name,))
                    batch_id = cursor.lastrowid
                    conn.commit()
                    print(f"Batch '{batch_name}' created with ID: {batch_id}")
                    return batch_id
                except sqlite3.IntegrityError:
                    print(
                        f"Batch name '{batch_name}' already exists. Fetching existing ID."
                    )
                    cursor.execute(sql_select, (batch_name,))
                    result = cursor.fetchone()
                    return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error creating/fetching batch '{batch_name}': {e}")
            return None

    def batch_process_save_image_path(self, batch_id, image_paths):
        """
        Saves multiple image paths into a specified batch by linking them
        in 'batch_process_image'. Creates entries in 'images' if needed.
        If adding the first image to a new batch context (or batch has no ref yet),
        it can be set as reference.

        Args:
            batch_id: The ID of the target batch.
            image_paths: A list of image file paths to add.

        Returns:
            The number of images successfully added (new links created).
        """
        added_count = 0
        # Kolom baru 'is_reference_batch' ditambahkan
        sql_check_link = "SELECT 1 FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ?"
        sql_insert_link = "INSERT INTO batch_process_image (batch_id, image_id_batch, is_reference_batch) VALUES (?, ?, ?)"
        sql_check_batch_ref = "SELECT 1 FROM batch_process_image WHERE batch_id = ? AND is_reference_batch = 1"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Periksa apakah batch ini sudah memiliki referensi
                cursor.execute(sql_check_batch_ref, (batch_id,))
                batch_has_reference = cursor.fetchone() is not None

                for image_path in image_paths:
                    try:
                        image_id = self._get_or_create_image_id(cursor, image_path)

                        cursor.execute(sql_check_link, (batch_id, image_id))
                        if cursor.fetchone():
                            # print(f"Image '{image_path}' (ID: {image_id}) already linked to batch ID {batch_id}.")
                            continue  # Sudah ada, lewati

                        # Tentukan status referensi untuk gambar baru ini
                        # Jika batch belum punya referensi, gambar pertama yang DITAMBAHKAN jadi referensi
                        # (Catatan: ini berarti jika batch sudah ada isinya TAPI belum ada yg jadi ref,
                        # gambar baru ini akan jadi ref. Jika ingin yang terlama jadi ref, logikanya beda)
                        current_is_reference = 0
                        if not batch_has_reference:
                            current_is_reference = 1
                            batch_has_reference = True  # Set agar gambar berikutnya di loop ini tidak jadi ref

                        cursor.execute(
                            sql_insert_link, (batch_id, image_id, current_is_reference)
                        )
                        added_count += 1
                        # if current_is_reference:
                        #     print(f"Image '{image_path}' (ID: {image_id}) added to batch ID {batch_id} and set as reference for this batch.")
                        # else:
                        #     print(f"Image '{image_path}' (ID: {image_id}) added to batch ID {batch_id}.")

                    except sqlite3.IntegrityError as e:
                        print(
                            f"Skipping duplicate link or integrity error for image {image_path} in batch {batch_id}: {e}"
                        )
                    except Exception as e:
                        print(
                            f"An unexpected error occurred for image {image_path} in batch {batch_id}: {e}"
                        )

                conn.commit()
                if added_count > 0:
                    print(
                        f"Added {added_count} new image links to batch with ID {batch_id}"
                    )
                # else:
                #     print(f"No new images were added to batch ID {batch_id}.")

        except sqlite3.Error as e:
            print(f"Database error during batch image save for batch {batch_id}: {e}")
            return 0  # Indicate failure
        return added_count

    def batch_process_delete_batch(self, batch_id):
        """
        Deletes a specific batch definition from 'batch_process'.
        Associated image links in 'batch_process_image' should be deleted
        automatically due to 'ON DELETE CASCADE'.

        Args:
            batch_id: The ID of the batch to delete.
        """
        sql = "DELETE FROM batch_process WHERE id = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (batch_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    pass
                else:
                    print(f"Batch ID {batch_id} not found for deletion.")
        except sqlite3.Error as e:
            print(f"Error deleting batch ID {batch_id}: {e}")

    def batch_process_delete_selected_images(self, batch_id, image_paths_to_delete):
        """
        ULTRA OPTIMIZED DELETE:
        1. Menggunakan 'Blind Bulk Delete' dengan sub-query untuk kecepatan maksimal.
        2. Memperbaiki Reference (Reference Repair) hanya SEKALI di akhir transaksi.
        3. Menangani limit variabel SQLite dengan chunking internal.
        """
        if not image_paths_to_delete:
            return 0

        # Limit aman variabel SQLite (biasanya 999). Kita pakai 500.
        CHUNK_SIZE = 500
        total_deleted = 0

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # --- TAHAP 1: DELETE (Tanpa Cek ID/Reference dulu) ---
                # Kita looping hanya untuk memecah limit variabel SQL,
                # bukan logic Python.

                for i in range(0, len(image_paths_to_delete), CHUNK_SIZE):
                    chunk_paths = image_paths_to_delete[i : i + CHUNK_SIZE]

                    # Buat placeholders (?, ?, ?)
                    placeholders = ",".join("?" * len(chunk_paths))

                    # Query Maut: Hapus link di batch_process_image
                    # dimana image_id cocok dengan path yang ada di tabel images.
                    # Ini menghilangkan kebutuhan 'SELECT id FROM images' terpisah.
                    sql_bulk_delete = f"""
                        DELETE FROM batch_process_image 
                        WHERE batch_id = ? 
                        AND image_id_batch IN (
                            SELECT id FROM images WHERE path IN ({placeholders})
                        )
                    """

                    # Params: batch_id + list path
                    params = [batch_id] + chunk_paths

                    cursor.execute(sql_bulk_delete, params)
                    total_deleted += cursor.rowcount

                # --- TAHAP 2: REPAIR REFERENCE (Hanya Sekali) ---
                # Cek apakah batch ini kehilangan referensinya?
                # (Lebih cepat cek count ref=1 daripada cek logic per gambar)

                if total_deleted > 0:
                    cursor.execute(
                        "SELECT 1 FROM batch_process_image WHERE batch_id = ? AND is_reference_batch = 1 LIMIT 1",
                        (batch_id,),
                    )
                    has_reference = cursor.fetchone()

                    if not has_reference:
                        # Jika tidak ada referensi (mungkin terhapus),
                        # tunjuk gambar terlama (ID terkecil) jadi referensi baru.
                        sql_fix_ref = """
                            UPDATE batch_process_image 
                            SET is_reference_batch = 1 
                            WHERE id = (
                                SELECT id FROM batch_process_image 
                                WHERE batch_id = ? 
                                ORDER BY id ASC 
                                LIMIT 1
                            )
                        """
                        cursor.execute(sql_fix_ref, (batch_id,))
                        # Jika rowcount > 0, berarti referensi baru berhasil diset.
                        # Jika 0, berarti batch kosong (semua gambar habis), tidak perlu ref.

                conn.commit()
                return total_deleted

        except sqlite3.Error as e:
            print(f"DB Ultra-Delete Error: {e}")
            return -1

    def delete_all_batches(self):
        """
        Deletes ALL batch definitions from 'batch_process'.
        Associated links in 'batch_process_image' should be deleted via CASCADE.
        Does not delete images from the main 'images' table.
        """
        sql = "DELETE FROM batch_process"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                conn.commit()
                print(
                    f"Deleted {cursor.rowcount} batches. Associated links should be removed by CASCADE."
                )
        except sqlite3.Error as e:
            print(f"Error deleting all batches: {e}")

    def get_all_batch_names(self):
        """
        Returns a list of all batch names from the 'batch_process' table.
        """
        sql = "SELECT batch_name FROM batch_process ORDER BY batch_name"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting all batch names: {e}")
            return []

    def get_all_batch_ids(self):
        """
        Returns a list of all batch IDs from the 'batch_process' table.
        """
        sql = "SELECT id FROM batch_process"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting all batch IDs: {e}")
            return []

    def get_images_by_batch(self, batch_id):
        """
        Returns a list of image paths associated with a given batch_id.
        The reference image for the batch is listed first.
        """
        # --- PERUBAHAN DI SINI UNTUK URUTAN ---
        sql = """
            SELECT i.path
            FROM images i
            JOIN batch_process_image bpi ON i.id = bpi.image_id_batch
            WHERE bpi.batch_id = ?
            ORDER BY
                bpi.is_reference_batch DESC, -- Referensi (is_reference_batch=1) selalu di atas
                i.path ASC                  -- Urutkan sisanya berdasarkan nama file
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (batch_id,))
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting images for batch ID {batch_id}: {e}")
            return []
    # --- 4. Single Process Operations --- (Tidak ada perubahan di bagian ini)

    # --- 4.a Single Process Modification ---
    def single_process_save_image_path(self, image_path):
        sql_check_link = "SELECT 1 FROM single_process_image WHERE image_id_single = ?"
        sql_insert_link = "INSERT INTO single_process_image (image_id_single, is_reference) VALUES (?, ?)"
        sql_count_single = "SELECT COUNT(*) FROM single_process_image"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                try:
                    image_id = self._get_or_create_image_id(cursor, image_path)
                    if not image_id:
                        raise Exception(
                            f"Failed to get or create image ID for {image_path}"
                        )
                    cursor.execute(sql_check_link, (image_id,))
                    if cursor.fetchone():
                        conn.commit()
                        return False
                    cursor.execute(sql_count_single)
                    count = cursor.fetchone()[0]
                    is_first = count == 0
                    reference_flag = 1 if is_first else 0
                    cursor.execute(sql_insert_link, (image_id, reference_flag))
                    conn.commit()
                    return True
                except sqlite3.IntegrityError:
                    conn.rollback()
                    return False
                except Exception:
                    conn.rollback()
                    return False
        except sqlite3.Error:
            return False

    def single_process_delete_path_images(self, image_paths):
        # Optimasi ringan: Bulk delete untuk single process juga
        if not image_paths:
            return 0
        placeholders = ",".join("?" * len(image_paths))
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                sql_get = f"SELECT spi.image_id_single, spi.is_reference FROM single_process_image spi JOIN images i ON spi.image_id_single = i.id WHERE i.path IN ({placeholders})"
                cursor.execute(sql_get, image_paths)
                rows = cursor.fetchall()
                if not rows:
                    return 0

                ids = [r[0] for r in rows]
                ref_del = any(r[1] == 1 for r in rows)

                pl_del = ",".join("?" * len(ids))
                cursor.execute(
                    f"DELETE FROM single_process_image WHERE image_id_single IN ({pl_del})",
                    ids,
                )
                cnt = cursor.rowcount

                if ref_del:
                    cursor.execute(
                        "UPDATE single_process_image SET is_reference = 1 WHERE id = (SELECT id FROM single_process_image ORDER BY id LIMIT 1)"
                    )

                conn.commit()
                return cnt
        except sqlite3.Error:
            return -1

    # --- 4.b Single Process Retrieval ---
    def get_single_process_image_paths(self):
        sql = """
            SELECT i.path
            FROM images i
            JOIN single_process_image spi ON i.id = spi.image_id_single
            ORDER BY spi.is_reference DESC, i.path ASC
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving single process image paths: {e}")
            return []

    def get_single_process_reference_image(self):
        sql = """
            SELECT i.path
            FROM images i
            JOIN single_process_image spi ON i.id = spi.image_id_single
            WHERE spi.is_reference = 1 LIMIT 1
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                result = cursor.fetchone()
                return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error retrieving single process reference image: {e}")
            return None
