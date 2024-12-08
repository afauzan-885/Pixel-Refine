import os
import sqlite3

def create_db(db_path="image_paths.db"):
    if not os.path.exists(db_path):
        print("Database not found. Creating a new database...")
    else:
        print(f"Database found at {db_path}.")

    # Gunakan 'with' untuk manajemen koneksi yang lebih aman
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL
            )
        ''')
        print("Table 'images' has been created or already exists.")
