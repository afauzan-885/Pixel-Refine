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

            # Create single_process_image table
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='single_process_image';
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS single_process_image (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_id INTEGER NOT NULL,
                        FOREIGN KEY (image_id) REFERENCES images (id)
                    )
                """)
                print("Table 'single_process_image' has been created with 'image_id' column.")
            else:
                cursor.execute("SELECT COUNT(*) FROM single_process_image")

            # Create batch_process table (untuk menyimpan info batch)
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='batch_process';
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE batch_process (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        batch_name TEXT NOT NULL
                    );
                """)
                print("Table 'batch_process' has been created.")
            
            # Create batch_process_image table (menghubungkan batch dengan image)
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='batch_process_image';
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE batch_process_image (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        batch_id INTEGER NOT NULL,
                        image_id INTEGER NOT NULL,
                        FOREIGN KEY (batch_id) REFERENCES batch_process(id),
                        FOREIGN KEY (image_id) REFERENCES images(id)
                    );
                """)
                print("Table 'batch_process_image' has been created.")
            else:
                cursor.execute("SELECT COUNT(*) FROM batch_process_image")
                
        self.is_table_checked = True

    def single_process_save_image_path(self, image_path):
        """
        Saves an image path to the database and links it to single_process_image.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO images (path) VALUES (?)", (image_path,))
            image_id = cursor.lastrowid  # Ambil ID gambar yang baru disimpan
            cursor.execute("INSERT INTO single_process_image (image_id) VALUES (?)", (image_id,))
            conn.commit()
            print(f"Image path saved and linked to single_process_image: {image_path}")

    def single_process_delete_path_images(self, image_paths):
        """
        Deletes multiple image paths from the database, including related data in single_process_image.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM images WHERE path IN ({seq})".format(
                seq=",".join(["?"] * len(image_paths))), image_paths)
            image_ids = [row[0] for row in cursor.fetchall()]
            if image_ids:
                cursor.executemany("DELETE FROM single_process_image WHERE image_id = ?", 
                                   ((image_id,) for image_id in image_ids))
                cursor.executemany("DELETE FROM images WHERE id = ?", 
                                   ((image_id,) for image_id in image_ids))
                conn.commit()
                print(f"Deleted images and related data: {image_paths}")

    # Fungsi untuk membuat batch baru
    def create_new_batch(self, batch_name):
        """
        Creates a new batch in the batch_process table.

        Args:
            batch_name: The name of the batch (e.g., "batch1").
        
        Returns:
            The batch_id of the newly created batch.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO batch_process (batch_name) VALUES (?)", (batch_name,))
            batch_id = cursor.lastrowid
            conn.commit()
            print(f"Batch '{batch_name}' created with ID: {batch_id}")
            return batch_id
        
    def get_images_by_batch(self, batch_id):
        """
        Returns a list of image paths associated with the given batch_id.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT images.path 
                FROM images 
                JOIN batch_process_image ON images.id = batch_process_image.image_id 
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
        Saves multiple image paths into a specified batch.
        For each image, it inserts into the images table and then creates a mapping in batch_process_image.

        Args:
            batch_id: The ID of the batch where images will be added.
            image_paths: A list of image paths to add to the batch.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for image_path in image_paths:
                cursor.execute("INSERT INTO images (path) VALUES (?)", (image_path,))
                image_id = cursor.lastrowid
                cursor.execute("INSERT INTO batch_process_image (batch_id, image_id) VALUES (?, ?)", 
                               (batch_id, image_id))
            conn.commit()
            print(f"Added {len(image_paths)} images to batch with ID {batch_id}")

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
            cursor.execute("DELETE FROM batch_process_image WHERE batch_id = ? AND image_id = ?", 
                           (batch_id, image_id))
            conn.commit()
            print(f"Deleted image ID {image_id} from batch ID {batch_id}")

    # Fungsi untuk menghapus seluruh batch
    def batch_process_delete_batch(self, batch_id):
        """
        Deletes an entire batch along with all associated image mappings.

        Args:
            batch_id: The ID of the batch to delete.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Hapus mapping gambar dari batch
            cursor.execute("DELETE FROM batch_process_image WHERE batch_id = ?", (batch_id,))
            # Hapus batch itu sendiri
            cursor.execute("DELETE FROM batch_process WHERE id = ?", (batch_id,))
            conn.commit()
            print(f"Deleted batch ID {batch_id} and all its associated image mappings")


    def get_all_image_paths(self):
        """
        Retrieves all image paths stored in the database.

        Returns:
            List of image paths.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM images")
            return [row[0] for row in cursor.fetchall()]    