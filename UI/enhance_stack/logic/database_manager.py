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
        # self.is_table_checked = False # Consider removing if create_database is always called early

    # --- 1. Initialization & Setup ---

    def _get_connection(self):
        """Establishes a database connection and enables foreign keys."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON;") # Ensure foreign keys are enabled
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error to {self.db_path}: {e}")
            # Consider raising the exception or returning None based on desired error handling
            raise # Re-raise the exception for calling code to handle

    def create_database(self):
        """
        Creates the necessary tables ('images', 'single_process_image',
        'batch_process', 'batch_process_image') in the database if they
        don't exist.
        """
        if not os.path.exists(self.db_path):
            print("Checking database...")
            print("Database not found. Creating database...")
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        else:
            print("Database already exists.")

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Create images table
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images';")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE images (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            path TEXT NOT NULL UNIQUE -- Ensure image paths are unique in this table
                        )
                    """)
                    print("Table 'images' has been created.")

                # Create single_process_image table
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='single_process_image';")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE single_process_image (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            image_id_single INTEGER NOT NULL UNIQUE,
                            FOREIGN KEY (image_id_single) REFERENCES images (id) ON DELETE CASCADE
                        )
                    """)
                    print("Table 'single_process_image' has been created.")

                # Create batch_process table
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batch_process';")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE batch_process (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            batch_name TEXT NOT NULL UNIQUE
                        );
                    """)
                    print("Table 'batch_process' has been created.")

                # Create batch_process_image table
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
                    print("Table 'batch_process_image' has been created.")
                conn.commit() # Commit changes after all table checks/creations
        except sqlite3.Error as e:
            print(f"Error during database/table creation: {e}")


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
            # Ensure path uniqueness is handled (added UNIQUE to images table)
            try:
                cursor.execute("INSERT INTO images (path) VALUES (?)", (image_path,))
                return cursor.lastrowid # Return new image_id
            except sqlite3.IntegrityError:
                 # Should not happen if check is done first, but handle race conditions
                 print(f"Race condition or error: Image path '{image_path}' likely already inserted.")
                 cursor.execute("SELECT id FROM images WHERE path = ?", (image_path,))
                 result = cursor.fetchone()
                 if result:
                    return result[0]
                 else:
                    # This case indicates a more serious issue
                    raise Exception(f"Could not get or create image ID for {image_path} after integrity error.")


    # --- 3. Batch Operations ---

    # --- 3.a Batch Creation & Modification ---

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

                        # Check if already linked to this batch
                        cursor.execute(sql_check, (batch_id, image_id))
                        if cursor.fetchone():
                            # print(f"Image {image_path} already linked to batch ID {batch_id}. Skipping.")
                            continue

                        # Insert the link
                        cursor.execute(sql_insert, (batch_id, image_id))
                        added_count += 1

                    except sqlite3.IntegrityError as e:
                        print(f"Skipping duplicate link or integrity error for image {image_path} in batch {batch_id}: {e}")
                        # No rollback needed here as each insert is separate attempt within loop
                    except Exception as e: # Catch other potential errors for a single image
                        print(f"An unexpected error occurred for image {image_path} in batch {batch_id}: {e}")
                        # Decide if you want to stop the whole batch or just skip the image

                conn.commit() # Commit all successful insertions at the end
                if added_count > 0:
                    print(f"Added {added_count} new image links to batch with ID {batch_id}")
                else:
                    print(f"No new image links added to batch {batch_id} (all might be duplicates).")

        except sqlite3.Error as e:
             print(f"Database error during batch image save for batch {batch_id}: {e}")
             return 0 # Indicate failure

        return added_count

    # --- 3.b Batch Deletion ---

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
                    print(f"Deleted link for image ID {image_id} from batch ID {batch_id}")
                else:
                    print(f"No link found to delete for image ID {image_id} in batch ID {batch_id}")
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
                    print(f"Deleted batch ID {batch_id}. Associated links should be removed by CASCADE.")
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


    # --- 3.c Batch Retrieval ---

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
            print(f"Error retrieving batch names: {e}")
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
            print(f"Error retrieving batch IDs: {e}")
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
            ORDER BY i.path -- Optional ordering
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (batch_id,))
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving images for batch ID {batch_id}: {e}")
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
                        ORDER BY i.path -- Optional
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
            print(f"Error retrieving batch process image paths (Batch ID: {batch_id}): {e}")
            return []


    # --- 4. Single Process Operations ---

    # --- 4.a Single Process Modification ---

    def single_process_save_image_path(self, image_path):
        """
        Saves an image path for single processing. Ensures the image exists in
        'images' table and links it uniquely in 'single_process_image'.

        Args:
            image_path: The path of the image to save.

        Returns:
            True if the link was newly created, False if it already existed or an error occurred.
        """
        sql_check = "SELECT 1 FROM single_process_image WHERE image_id_single = ?"
        sql_insert = "INSERT INTO single_process_image (image_id_single) VALUES (?)"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                try:
                    image_id = self._get_or_create_image_id(cursor, image_path)

                    # Check if already linked
                    cursor.execute(sql_check, (image_id,))
                    if cursor.fetchone():
                        # print(f"Image path already linked in single_process_image: {image_path}")
                        return False

                    # Insert the link
                    cursor.execute(sql_insert, (image_id,))
                    conn.commit()
                    print(f"Image path linked to single_process_image: {image_path}")
                    return True
                except sqlite3.IntegrityError as e: # Handles UNIQUE constraint
                    print(f"Error linking image {image_path} to single process (likely duplicate): {e}")
                    conn.rollback()
                    return False
        except sqlite3.Error as e:
            print(f"Database error during single process save for {image_path}: {e}")
            return False

    def single_process_delete_path_images(self, image_paths):
        """
        Deletes links from 'single_process_image' for the given image paths.
        Does not delete the images from the main 'images' table.

        Args:
            image_paths: A list of image file paths whose links should be removed.

        Returns:
            The number of links successfully deleted.
        """
        deleted_count = 0
        if not image_paths:
            return 0

        # Prepare placeholders for the IN clause
        placeholders = ",".join(["?"] * len(image_paths))
        sql_get_ids = f"SELECT id FROM images WHERE path IN ({placeholders})"
        sql_delete = "DELETE FROM single_process_image WHERE image_id_single = ?"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Get image IDs for the paths
                cursor.execute(sql_get_ids, image_paths)
                image_ids = [row[0] for row in cursor.fetchall()]

                if image_ids:
                    # Delete links one by one or use executemany
                    # executemany is generally more efficient
                    cursor.executemany(sql_delete, ((image_id,) for image_id in image_ids))
                    deleted_count = cursor.rowcount # executemany updates rowcount cumulatively
                    conn.commit()
                else:
                    pass
                    # print("No matching images found in 'images' table for deletion from single process.")

        except sqlite3.Error as e:
            print(f"Error deleting single process links: {e}")

        return deleted_count


    # --- 4.b Single Process Retrieval ---
    def get_single_process_image_paths(self):
        """
        Retrieves image paths currently linked in 'single_process_image'.
        """
        sql = """
            SELECT i.path
            FROM images i
            JOIN single_process_image spi ON i.id = spi.image_id_single
            ORDER BY i.path -- Optional
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving single process image paths: {e}")
            return []


    # --- 5. General Image Operations ---

    # --- 5.a General Retrieval ---
    def get_all_image_paths(self):
        """
        Retrieves ALL unique image paths stored in the 'images' table,
        regardless of whether they are linked to single or batch processing.
        """
        sql = "SELECT path FROM images ORDER BY path" # Optional ordering
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving all image paths: {e}")
            return []