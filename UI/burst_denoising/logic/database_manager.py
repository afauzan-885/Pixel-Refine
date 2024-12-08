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
        Creates the 'images' table in the database if it doesn't exist.
        Handles messages for checking and creating the database.
        """
        if not os.path.exists(self.db_path):
            print("Checking database...")
            print("Database not found. Creating database...")
        else:
            print("Using existing database.")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='images'
            """)
            table_exists = cursor.fetchone()

            if table_exists:
                print("Using existing table 'images'.")
            else:
                print("Creating table 'images'...")
                cursor.execute("""
                    CREATE TABLE images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        path TEXT NOT NULL
                    )
                """)
                conn.commit()
                print("Table 'images' has been created.")

        self.is_table_checked = True

    def save_image(self, image_path):
        """
        Saves an image path to the database.

        Args:
            image_path: The path to the image file.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO images (path) VALUES (?)", (image_path,))
            conn.commit()  # Explicitly commit the transaction
            print(f"Image path saved: {image_path}")

    def delete_images(self, image_paths):
        """
        Deletes multiple image paths from the database.

        Args:
            image_paths: A list of image paths to delete.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany("DELETE FROM images WHERE path = ?", [(path,) for path in image_paths])
            conn.commit()
            print(f"Deleted images: {image_paths}")

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
