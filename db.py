import os
import sqlite3

def create_db():
    db_path = "image_paths.db"
    if not os.path.exists(db_path):
        print("Database not found. Creating a new database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
