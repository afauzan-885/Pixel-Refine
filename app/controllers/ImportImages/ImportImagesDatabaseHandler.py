# database_handler.py
import sqlite3


class ImportImagesDatabaseHandler:
    """Kelas untuk menangani operasi database terkait gambar."""

    def __init__(self, db_name="image_paths.db"):
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        """Membuat tabel 'images' jika belum ada di database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE
            )
        """
        )
        conn.commit()
        conn.close()
        
    def remove_duplicates(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM images
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM images
                GROUP BY path
            )
        """)
        conn.commit()
        conn.close()


    def save_image_path(self, file_path):
        """Simpan satu path gambar ke database, jika belum ada."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            # Menyimpan gambar hanya jika path belum ada
            cursor.execute("INSERT INTO images (path) VALUES (?)", (file_path,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Jika path sudah ada, abaikan error tersebut
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def save_image_paths(self, image_paths):
        """Simpan beberapa path gambar sekaligus ke database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
             # Menyimpan semua path dalam satu transaksi
            existing_paths = set(self.get_all_image_paths())
            new_paths = [path for path in image_paths if path not in existing_paths]
            cursor.executemany("INSERT INTO images (path) VALUES (?)", [(path,) for path in new_paths])
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def get_all_image_paths(self):
        """Ambil semua path gambar yang tersimpan di database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT path FROM images")
        rows = cursor.fetchall()

        conn.close()
        return [row[0] for row in rows]

    def delete_images(self, image_paths):
        """Hapus gambar dari database berdasarkan path yang diberikan."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        for file_path in image_paths:
            cursor.execute("DELETE FROM images WHERE path = ?", (file_path,))

        conn.commit()
        conn.close()
