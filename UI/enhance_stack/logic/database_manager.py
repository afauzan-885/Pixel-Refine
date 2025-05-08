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
        """Establishes a database connection and enables foreign keys."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON;") # Ensure foreign keys are enabled
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error to {self.db_path}: {e}")
            raise # Re-raise the exception for calling code to handle

    def _add_column_if_not_exists(self, cursor, table_name, column_name, column_def):
        """Helper to add a column if it doesn't exist."""
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [info[1] for info in cursor.fetchall()]
        if column_name not in columns:
            print(f"Adding column '{column_name}' to table '{table_name}'...")
            try:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
                print(f"Column '{column_name}' added successfully.")
            except sqlite3.Error as e:
                print(f"Error adding column {column_name} to {table_name}: {e}")
                # Decide if this is critical - maybe raise? For now, just print.


    def create_database(self):
        """
        Creates the necessary tables and ensures the 'is_reference' column exists
        in 'single_process_image'.
        """
        db_dir_exists = True
        if not os.path.exists(self.db_path):
            print("Database not found. Creating database...")
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            db_dir_exists = False # Database is newly created
        # else:
            # print("Database exists. Checking tables...") # Optional: reduce verbosity

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Create images table (if not exists)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images';")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE images (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            path TEXT NOT NULL UNIQUE
                        )
                    """)
                    print("Table 'images' created.")

                # Create single_process_image table (if not exists)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='single_process_image';")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE single_process_image (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            image_id_single INTEGER NOT NULL UNIQUE,
                            is_reference INTEGER NOT NULL DEFAULT 0, -- TAMBAHKAN KOLOM INI
                            FOREIGN KEY (image_id_single) REFERENCES images (id) ON DELETE CASCADE
                        )
                    """)
                    print("Table 'single_process_image' created with 'is_reference' column.")
                else:
                     # Jika tabel sudah ada, pastikan kolom is_reference ada
                     self._add_column_if_not_exists(cursor, 'single_process_image', 'is_reference', 'INTEGER NOT NULL DEFAULT 0')


                # --- Create batch tables (unchanged) ---
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batch_process';")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE batch_process (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            batch_name TEXT NOT NULL UNIQUE
                        );
                    """)
                    print("Table 'batch_process' created.")

                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batch_process_image';")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE batch_process_image (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            batch_id INTEGER NOT NULL,
                            image_id_batch INTEGER NOT NULL,
                            FOREIGN KEY (batch_id) REFERENCES batch_process(id) ON DELETE CASCADE,
                            FOREIGN KEY (image_id_batch) REFERENCES images(id) ON DELETE CASCADE,
                            UNIQUE(batch_id, image_id_batch)
                        );
                    """)
                    print("Table 'batch_process_image' created.")

                conn.commit() # Commit changes after all table checks/creations
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
            return result[0]  # Return existing image_id
        else:
            try:
                cursor.execute("INSERT INTO images (path) VALUES (?)", (image_path,))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                print(f"Race condition or error: Image path '{image_path}' likely already inserted.")
                cursor.execute("SELECT id FROM images WHERE path = ?", (image_path,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    # This case indicates a more serious issue
                    raise Exception(f"Could not get or create image ID for {image_path} after integrity error.")


    # --- 3. Batch Operations (Unchanged from your original code) ---
    # ... (Keep all batch methods: create_new_batch, batch_process_save_image_path, etc.) ...
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
                except sqlite3.IntegrityError: # Handles UNIQUE constraint violation
                    print(f"Batch name '{batch_name}' already exists. Fetching existing ID.")
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

        Args:
            batch_id: The ID of the target batch.
            image_paths: A list of image file paths to add.

        Returns:
            The number of images successfully added (new links created).
        """
        added_count = 0
        sql_check = "SELECT 1 FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ?"
        sql_insert = "INSERT INTO batch_process_image (batch_id, image_id_batch) VALUES (?, ?)"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for image_path in image_paths:
                    try:
                        image_id = self._get_or_create_image_id(cursor, image_path)

                        cursor.execute(sql_check, (batch_id, image_id))
                        if cursor.fetchone():
                            continue

                        # Insert the link
                        cursor.execute(sql_insert, (batch_id, image_id))
                        added_count += 1

                    except sqlite3.IntegrityError as e:
                        print(f"Skipping duplicate link or integrity error for image {image_path} in batch {batch_id}: {e}")
                    except Exception as e:
                        print(f"An unexpected error occurred for image {image_path} in batch {batch_id}: {e}")

                conn.commit() # Commit all successful insertions at the end
                if added_count > 0:
                    print(f"Added {added_count} new image links to batch with ID {batch_id}")
                else:
                    pass

        except sqlite3.Error as e:
                 print(f"Database error during batch image save for batch {batch_id}: {e}")
                 return 0 # Indicate failure

        return added_count

    def batch_process_delete_image(self, batch_id, image_id):
        """
        Deletes a specific image link from a given batch (removes the mapping
        in 'batch_process_image'). Does not delete from 'images' table.

        Args:
            batch_id: The batch ID from which the image link should be removed.
            image_id: The ID of the image whose link should be removed.
        """
        sql = "DELETE FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (batch_id, image_id))
                conn.commit()
                if cursor.rowcount > 0:
                    pass                
        except sqlite3.Error as e:
            print(f"Error deleting image link (Image ID: {image_id}, Batch ID: {batch_id}): {e}")

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
                print(f"Deleted {cursor.rowcount} batches. Associated links should be removed by CASCADE.")
        except sqlite3.Error as e:
            print(f"Error deleting all batches: {e}")


    def get_all_batch_names(self):
        """
        Returns a list of all batch names from the 'batch_process' table.
        """
        sql = "SELECT batch_name FROM batch_process ORDER BY batch_name" # Optional ordering
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
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
            return []

    def get_images_by_batch(self, batch_id):
        """
        Returns a list of image paths associated with a given batch_id.
        """
        sql = """
            SELECT i.path
            FROM images i
            JOIN batch_process_image bpi ON i.id = bpi.image_id_batch
            WHERE bpi.batch_id = ?
            ORDER BY i.id -- Or i.path, or keep order from insertion
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (batch_id,))
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            return []

    def get_batch_process_image_paths(self, batch_id=None):
        """
        Retrieves image paths currently linked in batch_process_image.
        If batch_id is provided, retrieves paths only for that specific batch.
        Otherwise, retrieves distinct paths from ALL batches.

        Args:
            batch_id (int, optional): The specific batch ID. Defaults to None (all batches).

        Returns:
            A list of image paths.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if batch_id:
                    sql = """
                        SELECT i.path
                        FROM images i
                        JOIN batch_process_image bpi ON i.id = bpi.image_id_batch
                        WHERE bpi.batch_id = ?
                        ORDER BY i.id -- Or i.path
                    """
                    cursor.execute(sql, (batch_id,))
                else:
                    sql = """
                        SELECT DISTINCT i.path
                        FROM images i
                        JOIN batch_process_image bpi ON i.id = bpi.image_id_batch
                        ORDER BY i.path -- Optional
                    """
                    cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            return []

    # --- 4. Single Process Operations ---

    # --- 4.a Single Process Modification ---

    def single_process_save_image_path(self, image_path):
        """
        Saves an image path for single processing. Ensures the image exists in
        'images' table and links it uniquely in 'single_process_image'.
        If this is the *first* image added, it becomes the reference by default.

        Args:
            image_path: The path of the image to save.

        Returns:
            True if the link was newly created, False if it already existed or an error occurred.
        """
        sql_check_link = "SELECT 1 FROM single_process_image WHERE image_id_single = ?"
        sql_insert_link = "INSERT INTO single_process_image (image_id_single, is_reference) VALUES (?, ?)"
        sql_count_single = "SELECT COUNT(*) FROM single_process_image"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                try:
                    image_id = self._get_or_create_image_id(cursor, image_path)
                    if not image_id: # Handle case where image ID couldn't be obtained
                        raise Exception(f"Failed to get or create image ID for {image_path}")

                    # Check if already linked
                    cursor.execute(sql_check_link, (image_id,))
                    if cursor.fetchone():
                        conn.commit() # Commit image creation if it happened
                        return False

                    # Check if this will be the first image in single process
                    cursor.execute(sql_count_single)
                    count = cursor.fetchone()[0]
                    is_first = (count == 0)
                    reference_flag = 1 if is_first else 0

                    # Insert the link
                    cursor.execute(sql_insert_link, (image_id, reference_flag))
                    conn.commit()
                    if reference_flag:
                        pass
                    else:
                        pass
                    return True

                except sqlite3.IntegrityError as e: # Handles UNIQUE constraint on image_id_single
                    conn.rollback()
                    return False
                except Exception as e: # Catch other errors like failing _get_or_create_image_id
                    conn.rollback()
                    return False
        except sqlite3.Error as e:
            return False

    # --- BARU: Fungsi untuk set gambar referensi ---
    def set_single_process_reference(self, image_path):
        """
        Sets the specified image as the single reference image.
        Sets 'is_reference = 0' for all others in single_process_image.

        Args:
            image_path: The path of the image to set as reference.

        Returns:
            True if successful, False otherwise.
        """
        sql_get_id = "SELECT id FROM images WHERE path = ?"
        sql_reset_all = "UPDATE single_process_image SET is_reference = 0"
        sql_set_one = "UPDATE single_process_image SET is_reference = 1 WHERE image_id_single = ?"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                try:
                    # 1. Dapatkan ID gambar dari path
                    cursor.execute(sql_get_id, (image_path,))
                    result = cursor.fetchone()
                    if not result:
                        return False
                    image_id = result[0]

                    # 2. Reset semua referensi (dalam transaksi)
                    cursor.execute(sql_reset_all)

                    # 3. Set referensi yang baru
                    cursor.execute(sql_set_one, (image_id,))

                    # Pastikan link untuk image_id ini ada di single_process_image
                    if cursor.rowcount == 0:
                        conn.rollback()
                        return False

                    conn.commit() # Commit jika semua berhasil
                    return True

                except sqlite3.Error as e:
                    conn.rollback()
                    return False
        except sqlite3.Error as e:
            return False


    def single_process_delete_path_images(self, image_paths):
        """
        Deletes links from 'single_process_image' for the given image paths.
        Does not delete the images from the main 'images' table.
        Checks if the deleted image was the reference and potentially sets a new one.

        Args:
            image_paths: A list of image file paths whose links should be removed.

        Returns:
            The number of links successfully deleted. Returns -1 on major error.
        """
        deleted_count = 0
        if not image_paths:
            return 0

        # Dapatkan ID dan status referensi dari path yang akan dihapus
        placeholders = ','.join('?' for _ in image_paths)
        sql_get_ids_to_delete = f"""
            SELECT spi.image_id_single, spi.is_reference
            FROM single_process_image spi
            JOIN images i ON spi.image_id_single = i.id
            WHERE i.path IN ({placeholders})
        """

        sql_delete_link = "DELETE FROM single_process_image WHERE image_id_single = ?"
        sql_find_new_ref = "SELECT image_id_single FROM single_process_image ORDER BY id LIMIT 1" # Ambil ID terlama sebagai ref baru
        sql_set_ref = "UPDATE single_process_image SET is_reference = 1 WHERE image_id_single = ?"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                try:
                    # Dapatkan ID dan status referensi item yang akan dihapus
                    cursor.execute(sql_get_ids_to_delete, image_paths)
                    items_to_delete = cursor.fetchall() # List of (image_id, is_reference)

                    if not items_to_delete:
                        return 0

                    was_ref_deleted = False
                    ids_to_delete = []
                    for img_id, is_ref in items_to_delete:
                        ids_to_delete.append(img_id)
                        if is_ref == 1:
                            was_ref_deleted = True

                    # Hapus link dari single_process_image
                    for img_id in ids_to_delete:
                        cursor.execute(sql_delete_link, (img_id,))
                        deleted_count += cursor.rowcount

                    # Jika referensi dihapus dan masih ada item lain, set referensi baru
                    if was_ref_deleted:
                        cursor.execute("SELECT COUNT(*) FROM single_process_image")
                        remaining_count = cursor.fetchone()[0]
                        if remaining_count > 0:
                            cursor.execute(sql_find_new_ref)
                            new_ref_result = cursor.fetchone()
                            if new_ref_result:
                                new_ref_id = new_ref_result[0]
                                cursor.execute(sql_set_ref, (new_ref_id,))
                                print(f"Previous reference deleted. Set new reference to image ID: {new_ref_id}")

                    conn.commit()
                    print(f"Successfully deleted {deleted_count} links from single_process_image.")
                    return deleted_count

                except sqlite3.Error as e:
                    print(f"Database error during single process delete: {e}")
                    conn.rollback()
                    return -1 # Indicate error
        except sqlite3.Error as e:
            print(f"Database connection error during single process delete: {e}")
            return -1 # Indicate error


    # --- 4.b Single Process Retrieval ---
    def get_single_process_image_paths(self):
        """
        Retrieves all image paths from 'single_process_image', ordered by
        reference status first, then alphabetically by image path for non-references.
        """
        # --- PERUBAHAN DI SINI ---
        sql = """
            SELECT i.path
            FROM images i
            JOIN single_process_image spi ON i.id = spi.image_id_single
            ORDER BY
                spi.is_reference DESC, -- Referensi (is_reference=1) selalu di atas
                i.path ASC             -- Urutkan sisanya (is_reference=0) berdasarkan nama file
        """
        # -------------------------
        try:
            with self._get_connection() as conn:
                # Tidak perlu row_factory di sini karena kita hanya ambil satu kolom (path)
                cursor = conn.cursor()
                cursor.execute(sql)
                # Mengembalikan list of strings (paths)
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving single process image paths: {e}")
            return []

    def get_single_process_reference_image(self):
        """
        Retrieves the path of the current reference image, if any.
        Returns: Path string or None.
        """
        sql = """
            SELECT i.path
            FROM images i
            JOIN single_process_image spi ON i.id = spi.image_id_single
            WHERE spi.is_reference = 1
            LIMIT 1
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


    # --- 5. General Image Operations ---

    def delete_image_path_from_all(self, image_path):
        """
        Deletes an image entry from the main 'images' table.
        Due to CASCADE, this should remove links from 'single_process_image'
        and 'batch_process_image' as well.

        USE WITH CAUTION: This removes the image record completely.

        Args:
            image_path: The path of the image to delete entirely.

        Returns:
            True if deletion successful, False otherwise.
        """
        sql = "DELETE FROM images WHERE path = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (image_path,))
                conn.commit()
                if cursor.rowcount > 0:
                    print(f"Successfully deleted image '{image_path}' and its associations (via CASCADE).")
                    return True
                else:
                    print(f"Image path '{image_path}' not found in 'images' table for deletion.")
                    return False
        except sqlite3.Error as e:
            print(f"Error deleting image '{image_path}' from database: {e}")
            return False