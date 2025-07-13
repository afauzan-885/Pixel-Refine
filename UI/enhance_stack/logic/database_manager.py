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
            conn.execute("PRAGMA foreign_keys = ON;")  # Ensure foreign keys are enabled
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error to {self.db_path}: {e}")
            raise  # Re-raise the exception for calling code to handle

    def _add_column_if_not_exists(self, cursor, table_name, column_name, column_def):
        """Helper to add a column if it doesn't exist."""
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [info[1] for info in cursor.fetchall()]
        if column_name not in columns:
            print(f"Adding column '{column_name}' to table '{table_name}'...")
            try:
                cursor.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"
                )
                print(f"Column '{column_name}' added successfully.")
            except sqlite3.Error as e:
                print(f"Error adding column {column_name} to {table_name}: {e}")
                # Decide if this is critical - maybe raise? For now, just print.

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

                # 1. Buat tabel untuk menyimpan proyek panorama
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS panorama_projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        -- Kolom baru akan ditambahkan di bawah
                    )
                """
                )

                # === PERUBAHAN: Tambahkan kolom untuk setiap parameter workflow ===
                self._add_column_if_not_exists(
                    cursor,
                    "panorama_projects",
                    "align_algorithm",
                    'TEXT DEFAULT "AKAZE"',
                )
                self._add_column_if_not_exists(
                    cursor,
                    "panorama_projects",
                    "projection_type",
                    'TEXT DEFAULT "Cylindrical"',
                )
                self._add_column_if_not_exists(
                    cursor,
                    "panorama_projects",
                    "blending_method",
                    'TEXT DEFAULT "Multi-band"',
                )
                # Tambahkan kolom lain jika Anda punya parameter lain (misal: slider)

                # 2. Buat tabel penghubung antara proyek dan gambar
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS panorama_project_images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        image_id INTEGER NOT NULL,
                        image_order INTEGER, -- Penting untuk urutan gambar dalam panorama
                        FOREIGN KEY (project_id) REFERENCES panorama_projects(id) ON DELETE CASCADE,
                        FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
                        UNIQUE(project_id, image_id)
                    )
                """
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error during database/table creation or modification: {e}")

    # --- 2. Helper Methods (Internal) ---
    def create_new_panorama_project(self, name):
        """
        Membuat entri proyek panorama baru di database.

        Args:
            name (str): Nama untuk proyek panorama baru (misalnya, "Panorama 1").

        Returns:
            int: ID dari proyek yang baru dibuat, atau None jika gagal.
        """
        sql = "INSERT INTO panorama_projects (name) VALUES (?)"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (name,))
                conn.commit()
                print(
                    f"Successfully created panorama project '{name}' with ID: {cursor.lastrowid}"
                )
                return (
                    cursor.lastrowid
                )  # Mengembalikan ID dari baris yang baru dimasukkan
        except sqlite3.IntegrityError:
            print(f"Error: A panorama project with the name '{name}' already exists.")
            return None
        except sqlite3.Error as e:
            print(f"Database error while creating new panorama project: {e}")
            return None

    def get_all_panorama_projects(self):
        """
        Mengambil semua proyek panorama dari database, diurutkan berdasarkan nama.

        Returns:
            list: Daftar tuple, di mana setiap tuple berisi (id, name).
        """
        sql = "SELECT id, name FROM panorama_projects ORDER BY name"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error while fetching panorama projects: {e}")
            return []  # Kembalikan list kosong jika terjadi error

    def delete_panorama_project(self, project_id):
        """
        Menghapus proyek panorama berdasarkan ID-nya.
        Karena ON DELETE CASCADE, gambar terkait di panorama_project_images juga akan terhapus.

        Args:
            project_id (int): ID dari proyek yang akan dihapus.

        Returns:
            bool: True jika berhasil, False jika gagal.
        """
        sql = "DELETE FROM panorama_projects WHERE id = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (project_id,))
                conn.commit()
                print(f"Successfully deleted panorama project with ID: {project_id}")
                return True
        except sqlite3.Error as e:
            print(f"Database error while deleting panorama project {project_id}: {e}")
            return False

    def rename_panorama_project(self, project_id, new_name):
        """
        Mengubah nama proyek panorama di database.

        Args:
            project_id (int): ID dari proyek yang akan diubah namanya.
            new_name (str): Nama baru untuk proyek.

        Returns:
            bool: True jika berhasil, False jika gagal.
        """
        sql = "UPDATE panorama_projects SET name = ? WHERE id = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (new_name, project_id))
                conn.commit()
                print(f"Successfully renamed project {project_id} to '{new_name}'")
                return True
        except sqlite3.IntegrityError:
            print(f"Error: A project with the name '{new_name}' likely already exists.")
            return False
        except sqlite3.Error as e:
            print(f"Database error while renaming project {project_id}: {e}")
            return False

    def get_project_workflow_settings(self, project_id):
        """
        Mengambil pengaturan workflow untuk sebuah proyek panorama tertentu.

        Args:
            project_id (int): ID dari proyek.

        Returns:
            dict: Dictionary berisi pengaturan, atau None jika proyek tidak ditemukan.
        """
        sql = "SELECT align_algorithm, projection_type, blending_method FROM panorama_projects WHERE id = ?"
        try:
            with self._get_connection() as conn:
                conn.row_factory = (
                    sqlite3.Row
                )  # Ini memungkinkan kita mengakses kolom berdasarkan nama
                cursor = conn.cursor()
                cursor.execute(sql, (project_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)  # Ubah baris menjadi dictionary
                return None
        except sqlite3.Error as e:
            print(
                f"Database error while fetching workflow settings for project {project_id}: {e}"
            )
            return None

    def save_project_workflow_setting(self, project_id, setting_key, setting_value):
        """
        Menyimpan satu pengaturan workflow untuk sebuah proyek.

        Args:
            project_id (int): ID dari proyek.
            setting_key (str): Nama kolom di database (misal: 'align_algorithm').
            setting_value (str/int/float): Nilai baru untuk pengaturan.

        Returns:
            bool: True jika berhasil, False jika gagal.
        """
        # Validasi untuk mencegah SQL Injection, meskipun kita tidak menggunakan f-string di sini
        allowed_keys = ["align_algorithm", "projection_type", "blending_method"]
        if setting_key not in allowed_keys:
            print(f"Error: Invalid setting key '{setting_key}'")
            return False

        sql = f"UPDATE panorama_projects SET {setting_key} = ? WHERE id = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (setting_value, project_id))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(
                f"Database error while saving setting '{setting_key}' for project {project_id}: {e}"
            )
            return False

    # Tambahkan fungsi untuk menambahkan gambar ke proyek (akan kita gunakan nanti)
    def add_images_to_project(self, project_id, image_paths):
        """
        Menambahkan daftar path gambar ke sebuah proyek panorama.
        Ini adalah operasi transaksional.

        Args:
            project_id (int): ID dari proyek target.
            image_paths (list): Daftar string path gambar.

        Returns:
            bool: True jika semua gambar berhasil ditambahkan, False jika ada error.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                for path in image_paths:
                    # 1. Masukkan path ke tabel 'images' jika belum ada.
                    # 'OR IGNORE' akan mencegah error jika path sudah ada (UNIQUE constraint).
                    cursor.execute(
                        "INSERT OR IGNORE INTO images (path) VALUES (?)", (path,)
                    )

                    # 2. Ambil image_id dari path tersebut.
                    cursor.execute("SELECT id FROM images WHERE path = ?", (path,))
                    image_id_result = cursor.fetchone()
                    if image_id_result:
                        image_id = image_id_result[0]
                        # 3. Hubungkan image_id dengan project_id.
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO panorama_project_images (project_id, image_id)
                            VALUES (?, ?)
                        """,
                            (project_id, image_id),
                        )
                conn.commit()
                print(
                    f"Successfully added/updated {len(image_paths)} images for project ID {project_id}."
                )
                return True
        except sqlite3.Error as e:
            print(f"Database error while adding images to project {project_id}: {e}")
            conn.rollback()  # Batalkan semua perubahan jika terjadi error
            return False

    def get_images_for_project(self, project_id):
        """
        Mengambil semua path gambar untuk sebuah proyek panorama tertentu.

        Args:
            project_id (int): ID dari proyek yang gambarnya ingin diambil.

        Returns:
            list: Daftar string path gambar.
        """
        sql = """
            SELECT i.path 
            FROM images i
            JOIN panorama_project_images ppi ON i.id = ppi.image_id
            WHERE ppi.project_id = ?
            ORDER BY ppi.image_order, ppi.id -- Urutkan berdasarkan urutan, lalu ID
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (project_id,))
                # cursor.fetchall() akan mengembalikan list of tuples, misal [('path1',), ('path2',)]
                # Kita ubah menjadi list of strings: ['path1', 'path2']
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error while fetching images for project {project_id}: {e}")
            return []

    def delete_images_from_project(self, project_id, image_paths_to_delete):
        """
        Menghapus beberapa gambar dari sebuah proyek panorama tertentu.

        Args:
            project_id (int): ID dari proyek.
            image_paths_to_delete (list): Daftar path gambar yang akan dihapus dari proyek ini.

        Returns:
            bool: True jika berhasil, False jika ada error.
        """
        if not image_paths_to_delete:
            return True  # Tidak ada yang perlu dihapus

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Ambil semua ID gambar dari path-nya
                placeholders = ",".join("?" for _ in image_paths_to_delete)
                cursor.execute(
                    f"SELECT id FROM images WHERE path IN ({placeholders})",
                    image_paths_to_delete,
                )
                image_ids_to_delete = [row[0] for row in cursor.fetchall()]

                if not image_ids_to_delete:
                    return True  # Tidak ada ID gambar yang cocok untuk dihapus

                # Hapus hubungan antara proyek dan gambar
                id_placeholders = ",".join("?" for _ in image_ids_to_delete)
                sql = f"DELETE FROM panorama_project_images WHERE project_id = ? AND image_id IN ({id_placeholders})"

                params = [project_id] + image_ids_to_delete
                cursor.execute(sql, params)

                conn.commit()
                print(
                    f"Successfully deleted {cursor.rowcount} image links from project ID {project_id}."
                )
                return True
        except sqlite3.Error as e:
            print(
                f"Database error while deleting images from project {project_id}: {e}"
            )
            return False

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

    # --- FUNGSI BARU UNTUK SET REFERENSI BATCH ---
    def set_batch_process_reference(self, batch_id, image_path):
        """
        Sets the specified image as the reference image for a specific batch.
        Sets 'is_reference_batch = 0' for all other images in that batch.

        Args:
            batch_id: The ID of the batch.
            image_path: The path of the image to set as reference within this batch.

        Returns:
            True if successful, False otherwise (e.g., image not in batch, batch not found).
        """
        sql_get_image_id = "SELECT id FROM images WHERE path = ?"
        sql_check_image_in_batch = "SELECT 1 FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ?"
        sql_reset_batch_refs = (
            "UPDATE batch_process_image SET is_reference_batch = 0 WHERE batch_id = ?"
        )
        sql_set_one_batch_ref = "UPDATE batch_process_image SET is_reference_batch = 1 WHERE batch_id = ? AND image_id_batch = ?"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                try:
                    # 1. Dapatkan image_id dari path
                    cursor.execute(sql_get_image_id, (image_path,))
                    img_result = cursor.fetchone()
                    if not img_result:
                        print(
                            f"Error setting batch reference: Image path '{image_path}' not found in 'images' table."
                        )
                        return False
                    image_id = img_result[0]

                    # 2. Pastikan batch ada (implisit, karena foreign key) dan gambar ada di batch tersebut
                    cursor.execute(sql_check_image_in_batch, (batch_id, image_id))
                    if not cursor.fetchone():
                        print(
                            f"Error setting batch reference: Image ID {image_id} ('{image_path}') is not part of batch ID {batch_id}."
                        )
                        conn.rollback()  # Meskipun tidak ada perubahan, ini praktik yang baik
                        return False

                    # 3. Reset semua referensi untuk batch_id ini
                    cursor.execute(sql_reset_batch_refs, (batch_id,))

                    # 4. Set referensi yang baru untuk image_id di batch_id ini
                    cursor.execute(sql_set_one_batch_ref, (batch_id, image_id))

                    if cursor.rowcount == 0:
                        # Ini seharusnya tidak terjadi jika langkah 2 berhasil, tapi sebagai pengaman
                        print(
                            f"Error setting batch reference: Failed to update reference status for image ID {image_id} in batch ID {batch_id}."
                        )
                        conn.rollback()
                        return False

                    conn.commit()
                    print(
                        f"Image '{image_path}' (ID: {image_id}) is now the reference for batch ID {batch_id}."
                    )
                    return True

                except sqlite3.Error as e:
                    print(
                        f"Database error setting batch reference for batch {batch_id}, image '{image_path}': {e}"
                    )
                    conn.rollback()
                    return False
        except sqlite3.Error as e:
            print(f"Database connection error during set batch reference: {e}")
            return False

    # -----------------------------------------------

    def batch_process_delete_image(
        self, batch_id, image_id
    ):  # Perlu dipertimbangkan jika ref dihapus
        """
        Deletes a specific image link from a given batch.
        If the deleted image was the reference for this batch,
        a new reference might need to be set if other images exist.

        Args:
            batch_id: The batch ID.
            image_id: The ID of the image link to remove.
        """
        sql_get_ref_status = "SELECT is_reference_batch FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ?"
        sql_delete = (
            "DELETE FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ?"
        )
        sql_find_new_ref = "SELECT id FROM batch_process_image WHERE batch_id = ? ORDER BY id LIMIT 1"  # Ambil yg terlama sbg ref baru
        sql_set_ref = "UPDATE batch_process_image SET is_reference_batch = 1 WHERE id = ?"  # Update by bpi.id

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 1. Cek apakah gambar yang akan dihapus adalah referensi
                was_ref = False
                cursor.execute(sql_get_ref_status, (batch_id, image_id))
                ref_status_result = cursor.fetchone()
                if ref_status_result and ref_status_result[0] == 1:
                    was_ref = True

                # 2. Hapus gambar
                cursor.execute(sql_delete, (batch_id, image_id))
                deleted_row_count = cursor.rowcount

                if deleted_row_count > 0:
                    print(
                        f"Image link (Image ID: {image_id}) deleted from batch ID: {batch_id}."
                    )
                    # 3. Jika referensi dihapus dan masih ada gambar lain di batch ini, set referensi baru
                    if was_ref:
                        cursor.execute(
                            "SELECT COUNT(*) FROM batch_process_image WHERE batch_id = ?",
                            (batch_id,),
                        )
                        remaining_count = cursor.fetchone()[0]
                        if remaining_count > 0:
                            cursor.execute(sql_find_new_ref, (batch_id,))
                            new_ref_bpi_id_result = (
                                cursor.fetchone()
                            )  # ini adalah id dari batch_process_image, bukan image_id
                            if new_ref_bpi_id_result:
                                new_ref_bpi_id = new_ref_bpi_id_result[0]
                                cursor.execute(sql_set_ref, (new_ref_bpi_id,))
                                print(
                                    f"Previous reference in batch {batch_id} deleted. New reference set for bpi.id: {new_ref_bpi_id}."
                                )
                    conn.commit()
        except sqlite3.Error as e:
            print(
                f"Error deleting image link (Image ID: {image_id}, Batch ID: {batch_id}): {e}"
            )

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
        Deletes links for selected image paths from a specific batch.
        It removes the mapping in 'batch_process_image' for the given
        batch_id and image paths. If a reference image is deleted,
        it attempts to set a new reference for that batch.

        Args:
            batch_id: The ID of the batch from which images should be removed.
            image_paths_to_delete: A list of image file paths to remove from the batch.

        Returns:
            The number of image links successfully deleted from the batch.
            Returns -1 on a major database error.
        """
        if not image_paths_to_delete:
            return 0

        deleted_count = 0

        placeholders = ",".join("?" * len(image_paths_to_delete))
        sql_get_image_info = f"""
            SELECT i.id, bpi.is_reference_batch, bpi.id AS bpi_id
            FROM images i
            JOIN batch_process_image bpi ON i.id = bpi.image_id_batch
            WHERE bpi.batch_id = ? AND i.path IN ({placeholders})
        """
        sql_delete_link = "DELETE FROM batch_process_image WHERE id = ?"
        sql_find_new_ref = (
            "SELECT id FROM batch_process_image WHERE batch_id = ? ORDER BY id LIMIT 1"
        )
        sql_set_ref = (
            "UPDATE batch_process_image SET is_reference_batch = 1 WHERE id = ?"
        )

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                try:
                    params = [batch_id] + image_paths_to_delete
                    cursor.execute(sql_get_image_info, params)
                    images_info_to_delete = cursor.fetchall()

                    if not images_info_to_delete:
                        print(
                            f"No images from the provided list found in batch ID {batch_id}."
                        )
                        return 0

                    was_any_ref_deleted = False
                    for image_id, is_ref, bpi_id_to_delete in images_info_to_delete:
                        cursor.execute(sql_delete_link, (bpi_id_to_delete,))
                        if cursor.rowcount > 0:
                            deleted_count += 1
                            if is_ref == 1:
                                was_any_ref_deleted = True

                    if was_any_ref_deleted:
                        cursor.execute(
                            "SELECT COUNT(*) FROM batch_process_image WHERE batch_id = ?",
                            (batch_id,),
                        )
                        remaining_count = cursor.fetchone()[0]
                        if remaining_count > 0:
                            cursor.execute(
                                "UPDATE batch_process_image SET is_reference_batch = 0 WHERE batch_id = ?",
                                (batch_id,),
                            )
                            cursor.execute(sql_find_new_ref, (batch_id,))
                            new_ref_result = cursor.fetchone()
                            if new_ref_result:
                                new_ref_bpi_id = new_ref_result[0]
                                cursor.execute(sql_set_ref, (new_ref_bpi_id,))
                                print(
                                    f"A reference image was deleted from batch {batch_id}. New reference set for bpi.id: {new_ref_bpi_id}."
                                )

                    conn.commit()
                    if deleted_count > 0:
                        print(
                            f"Successfully removed {deleted_count} image(s) from batch ID {batch_id}."
                        )
                    else:
                        print(
                            f"No images were removed from batch ID {batch_id} (either not found in batch or already removed)."
                        )
                    return deleted_count

                except sqlite3.Error as e:
                    print(
                        f"Database error during selected image deletion from batch {batch_id}: {e}"
                    )
                    conn.rollback()
                    return -1
        except sqlite3.Error as e:
            print(f"Database connection error during selected image deletion: {e}")
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

    # --- FUNGSI BARU UNTUK MENDAPATKAN REFERENSI BATCH ---
    def get_batch_process_reference_image(self, batch_id):
        """
        Retrieves the path of the current reference image for a specific batch, if any.

        Args:
            batch_id: The ID of the batch.

        Returns:
            Path string of the reference image or None if no reference is set or batch not found.
        """
        sql = """
            SELECT i.path
            FROM images i
            JOIN batch_process_image bpi ON i.id = bpi.image_id_batch
            WHERE bpi.batch_id = ? AND bpi.is_reference_batch = 1
            LIMIT 1
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (batch_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error retrieving reference image for batch ID {batch_id}: {e}")
            return None

    def get_batch_process_image_paths(self, batch_id=None):
        """
        Retrieves image paths currently linked in batch_process_image.
        If batch_id is provided, retrieves paths only for that specific batch,
        with the reference image listed first.
        Otherwise, retrieves distinct paths from ALL batches (order might be less defined).

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
                        ORDER BY
                            bpi.is_reference_batch DESC,
                            i.path ASC
                    """
                    cursor.execute(sql, (batch_id,))
                else:
                    sql = """
                        SELECT DISTINCT i.path
                        FROM images i
                        JOIN batch_process_image bpi ON i.id = bpi.image_id_batch
                        ORDER BY i.path
                    """
                    cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting batch process image paths: {e}")
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

    def set_single_process_reference(self, image_path):
        sql_get_id = "SELECT id FROM images WHERE path = ?"
        sql_reset_all = "UPDATE single_process_image SET is_reference = 0"
        sql_set_one = (
            "UPDATE single_process_image SET is_reference = 1 WHERE image_id_single = ?"
        )
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(sql_get_id, (image_path,))
                    result = cursor.fetchone()
                    if not result:
                        return False
                    image_id = result[0]
                    cursor.execute(sql_reset_all)
                    cursor.execute(sql_set_one, (image_id,))
                    if cursor.rowcount == 0:
                        conn.rollback()
                        return False
                    conn.commit()
                    return True
                except sqlite3.Error:
                    conn.rollback()
                    return False
        except sqlite3.Error:
            return False

    def single_process_delete_path_images(self, image_paths):
        deleted_count = 0
        if not image_paths:
            return 0
        placeholders = ",".join("?" for _ in image_paths)
        sql_get_ids_to_delete = f"""
            SELECT spi.image_id_single, spi.is_reference
            FROM single_process_image spi
            JOIN images i ON spi.image_id_single = i.id
            WHERE i.path IN ({placeholders})
        """
        sql_delete_link = "DELETE FROM single_process_image WHERE image_id_single = ?"
        sql_find_new_ref = (
            "SELECT image_id_single FROM single_process_image ORDER BY id LIMIT 1"
        )
        sql_set_ref = (
            "UPDATE single_process_image SET is_reference = 1 WHERE image_id_single = ?"
        )
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(sql_get_ids_to_delete, image_paths)
                    items_to_delete = cursor.fetchall()
                    if not items_to_delete:
                        return 0
                    was_ref_deleted = False
                    ids_to_delete = []
                    for img_id, is_ref in items_to_delete:
                        ids_to_delete.append(img_id)
                        if is_ref == 1:
                            was_ref_deleted = True
                    for img_id in ids_to_delete:
                        cursor.execute(sql_delete_link, (img_id,))
                        deleted_count += cursor.rowcount
                    if was_ref_deleted:
                        cursor.execute("SELECT COUNT(*) FROM single_process_image")
                        if cursor.fetchone()[0] > 0:
                            cursor.execute(sql_find_new_ref)
                            new_ref_result = cursor.fetchone()
                            if new_ref_result:
                                cursor.execute(sql_set_ref, (new_ref_result[0],))

                    conn.commit()
                    return deleted_count
                except sqlite3.Error as e:
                    print(f"Database error during single process delete: {e}")
                    conn.rollback()
                    return -1
        except sqlite3.Error as e:
            print(f"Database connection error during single process delete: {e}")
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

    def delete_image_path_from_all(self, image_path):
        sql = "DELETE FROM images WHERE path = ?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (image_path,))
                conn.commit()
                if cursor.rowcount > 0:
                    return True
                return False
        except sqlite3.Error as e:
            print(f"Error deleting image '{image_path}' from database: {e}")
            return False
