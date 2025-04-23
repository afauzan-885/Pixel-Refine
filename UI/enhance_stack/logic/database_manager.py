import os
import sqlite3

class DatabaseManager:
    def __init__(self, db_path):
        """
        Initializes the DatabaseManager.

        Args:
            db_path: The path to the database file.
        """
        self.db_path = db_path
        self.is_table_checked = False

    def create_database(self):
        """
        Creates the 'images', 'single_process_image', 'batch_process', and 'batch_process_image' tables
        in the database if they don't exist.
        """
        if not os.path.exists(self.db_path):
            print("Checking database...")
            print("Database not found. Creating database...")
        else:
            print("Database already exists.")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create images table
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='images';
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        path TEXT NOT NULL
                    )
                """)
            else:
                cursor.execute("SELECT COUNT(*) FROM images")

            # Create single_process_image table with explicit column name image_id_single
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='single_process_image';")
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS single_process_image (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_id_single INTEGER NOT NULL UNIQUE, -- Tambahkan UNIQUE jika satu gambar hanya boleh 1 kali di single
                        FOREIGN KEY (image_id_single) REFERENCES images (id) ON DELETE CASCADE -- Tambahkan ON DELETE CASCADE
                    )
                """)
                print("Table 'single_process_image' has been created.")
            else:
                cursor.execute("SELECT COUNT(*) FROM single_process_image")

            # Create batch_process table (untuk menyimpan info batch)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batch_process';")
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE batch_process (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        batch_name TEXT NOT NULL UNIQUE -- Tambahkan UNIQUE jika nama batch harus unik
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
                        FOREIGN KEY (batch_id) REFERENCES batch_process(id) ON DELETE CASCADE, -- Tambahkan ON DELETE CASCADE
                        FOREIGN KEY (image_id_batch) REFERENCES images(id) ON DELETE CASCADE, -- Tambahkan ON DELETE CASCADE
                        UNIQUE(batch_id, image_id_batch) -- Pastikan kombinasi batch dan image unik
                    );
                """)
                print("Table 'batch_process_image' has been created.")
            else:
                cursor.execute("SELECT COUNT(*) FROM batch_process_image")
                
        self.is_table_checked = True
        
    def _get_or_create_image_id(self, cursor, image_path):
        """Helper function to get existing image_id or create a new one."""
        cursor.execute("SELECT id FROM images WHERE path = ?", (image_path,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return existing image_id
        else:
            cursor.execute("INSERT INTO images (path) VALUES (?)", (image_path,))
            return cursor.lastrowid # Return new image_id

    def single_process_save_image_path(self, image_path):
        """
        Saves an image path ensuring uniqueness in images table and links it
        to single_process_image if not already linked.
        Returns True if successfully added, False otherwise (e.g., duplicate link).
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                image_id = self._get_or_create_image_id(cursor, image_path)

                # Check if this image_id is already in single_process_image
                cursor.execute("SELECT 1 FROM single_process_image WHERE image_id_single = ?", (image_id,))
                if cursor.fetchone():
                    print(f"Image path already linked in single_process_image: {image_path}")
                    return False # Indicate it was already there

                # Insert the link
                cursor.execute("INSERT INTO single_process_image (image_id_single) VALUES (?)", (image_id,))
                conn.commit()
                print(f"Image path linked to single_process_image: {image_path}")
                return True # Indicate successful addition
            except sqlite3.IntegrityError as e:
                # Handle potential race conditions or other integrity issues if UNIQUE constraint fails
                print(f"Error linking image {image_path} to single process: {e}")
                conn.rollback() # Rollback on error
                return False

    def single_process_delete_path_images(self, image_paths):
        """
        Deletes links from single_process_image for the given paths.
        Optionally, could add logic later to delete from 'images' if not used elsewhere.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Get image IDs for the paths
            cursor.execute("SELECT id FROM images WHERE path IN ({seq})".format(
                seq=",".join(["?"] * len(image_paths))), image_paths)
            image_ids = [row[0] for row in cursor.fetchall()]

            if image_ids:
                # Delete only the links from single_process_image
                cursor.executemany("DELETE FROM single_process_image WHERE image_id_single = ?",
                                   ((image_id,) for image_id in image_ids))
                conn.commit()
                print(f"Deleted single process links for: {image_paths}")
                # Note: We are NOT deleting from the main 'images' table here
                # to allow the image to potentially exist in batches.

    # Fungsi untuk membuat batch baru
    def create_new_batch(self, batch_name):
        """Creates a new batch, ensuring the name is unique."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO batch_process (batch_name) VALUES (?)", (batch_name,))
                batch_id = cursor.lastrowid
                conn.commit()
                print(f"Batch '{batch_name}' created with ID: {batch_id}")
                return batch_id
            except sqlite3.IntegrityError:
                print(f"Batch name '{batch_name}' already exists. Fetching existing ID.")
                cursor.execute("SELECT id FROM batch_process WHERE batch_name = ?", (batch_name,))
                result = cursor.fetchone()
                return result[0] if result else None # Return existing ID or None if 
        
    def get_images_by_batch(self, batch_id):
        """
        Returns a list of image paths associated with the given batch_id.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT images.path 
                FROM images 
                JOIN batch_process_image ON images.id = batch_process_image.image_id_batch 
                WHERE batch_process_image.batch_id = ?
            """, (batch_id,))
            return [row[0] for row in cursor.fetchall()]
        
    def get_all_batch_ids(self):
        """
        Returns a list of all batch IDs from the batch_process table.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM batch_process")
            return [row[0] for row in cursor.fetchall()]

    # Fungsi untuk menambahkan gambar ke batch tertentu
    def batch_process_save_image_path(self, batch_id, image_paths):
        """
        Saves multiple image paths into a specified batch, ensuring uniqueness
        in the images table and within the batch-image link.
        Returns the number of images successfully added to the batch link.
        """
        added_count = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for image_path in image_paths:
                try:
                    image_id = self._get_or_create_image_id(cursor, image_path)

                    # Check if this image_id is already linked to this batch_id
                    cursor.execute("SELECT 1 FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ?",
                                   (batch_id, image_id))
                    if cursor.fetchone():
                        print(f"Image {image_path} already linked to batch ID {batch_id}. Skipping.")
                        continue # Skip to the next image path

                    # Insert the link
                    cursor.execute("INSERT INTO batch_process_image (batch_id, image_id_batch) VALUES (?, ?)",
                                   (batch_id, image_id))
                    added_count += 1

                except sqlite3.IntegrityError as e:
                     # Handles UNIQUE(batch_id, image_id_batch) constraint violation gracefully
                    print(f"Skipping duplicate link or error for image {image_path} in batch {batch_id}: {e}")
                    conn.rollback() # Rollback the single failed insert attempt for this image
                    # We need to start a new transaction context for the next image or commit
                    # Since we are in a 'with' block, commit/rollback happens at the end.
                    # A manual commit here might be needed if not for the loop structure.
                    # But since we `continue`, the final commit outside the loop should work for successful ones.
                except Exception as e:
                    print(f"An unexpected error occurred for image {image_path} in batch {batch_id}: {e}")
                    conn.rollback() # Rollback on unexpected error

            conn.commit() # Commit all successful insertions at the end
            print(f"Added {added_count} new image links to batch with ID {batch_id}")
        return added_count

    # Fungsi untuk menghapus gambar tertentu dari batch
    def batch_process_delete_image(self, batch_id, image_id):
        """
        Deletes a specific image from a given batch (removes the mapping in batch_process_image).
        
        Args:
            batch_id: The batch ID from which the image should be removed.
            image_id: The ID of the image to remove.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ?", 
                           (batch_id, image_id))
            conn.commit()
            print(f"Deleted image ID {image_id} from batch ID {batch_id}")

    # Fungsi untuk menghapus seluruh batch
    def batch_process_delete_batch(self, batch_id):
        """Deletes a batch and its associated image links."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Hapus mapping gambar dari batch (ON DELETE CASCADE handle this if set)
            # cursor.execute("DELETE FROM batch_process_image WHERE batch_id = ?", (batch_id,))

            # Hapus batch itu sendiri
            cursor.execute("DELETE FROM batch_process WHERE id = ?", (batch_id,))
            conn.commit()
            print(f"Deleted batch ID {batch_id} and its associated image links (via CASCADE or explicit delete).")
            # Note: Images in 'images' table are not deleted here.

    def delete_all_batches(self):
        """Deletes all batches and their links."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Hapus seluruh mapping gambar dari batch_process_image (ON DELETE CASCADE handle this)
            # cursor.execute("DELETE FROM batch_process_image")

            # Hapus seluruh batch dari batch_process
            cursor.execute("DELETE FROM batch_process")
            conn.commit()
            print("Deleted all batches and their associated image links.")
            # Note: Images in 'images' table are not deleted here.

    # --- METODE BARU UNTUK PEMERIKSAAN DUPLIKAT SPESIFIK ---

    def get_single_process_image_paths(self):
        """Retrieves image paths currently linked in single_process_image."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT i.path
                FROM images i
                JOIN single_process_image spi ON i.id = spi.image_id_single
            """)
            return [row[0] for row in cursor.fetchall()]

    def get_batch_process_image_paths(self, batch_id=None):
        """
        Retrieves image paths currently linked in batch_process_image.
        If batch_id is provided, retrieves paths only for that specific batch.
        Otherwise, retrieves paths from ALL batches.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if batch_id:
                cursor.execute("""
                    SELECT i.path
                    FROM images i
                    JOIN batch_process_image bpi ON i.id = bpi.image_id_batch
                    WHERE bpi.batch_id = ?
                """, (batch_id,))
            else:
                 # Ambil path unik dari semua batch
                cursor.execute("""
                    SELECT DISTINCT i.path
                    FROM images i
                    JOIN batch_process_image bpi ON i.id = bpi.image_id_batch
                """)
            return [row[0] for row in cursor.fetchall()]

    def get_all_image_paths(self):
        """
        Retrieves ALL unique image paths stored in the 'images' table.
        Use context-specific methods (get_single_process_image_paths, get_batch_process_image_paths)
        for duplicate checking during import.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]