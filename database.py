# import os
# import sqlite3

# def create_db(db_path="pixel_refine_database.db"):
#     if not os.path.exists(db_path):
#         print("Database not found. Creating a new database...")
#     else:
#         print(f"Database found at {db_path}.")

#     # Gunakan 'with' untuk manajemen koneksi yang lebih aman
#     with sqlite3.connect(db_path) as conn:
#         cursor = conn.cursor()

#         # Membuat tabel 'images' untuk menyimpan file gambar
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS images (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 path TEXT NOT NULL
#             )
#         ''')
#         print("Table 'images' has been created or already exists.")

#         # Membuat tabel 'path_gambar' untuk menyimpan path gambar secara terpisah
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS path_gambar (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 image_id INTEGER NOT NULL,
#                 file_name TEXT NOT NULL,
#                 FOREIGN KEY (image_id) REFERENCES images (id) ON DELETE CASCADE
#             )
#         ''')
#         print("Table 'path_gambar' has been created or already exists.")

# if __name__ == "__main__":
#     create_db()
