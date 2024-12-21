import sqlite3
import subprocess, os
import sys

from .multi_threading import RunningAlgorithmThreading


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# virtualenv_path = r"venv/Scripts/python.exe"
def save_image_data(self, image_id, image_file):
    """
    Saves image file data as BLOB in the 'data_images' table.

    Args:
        image_id: The ID of the image in the 'images' table.
        image_file: The path to the image file.
    """
    with open(image_file, 'rb') as file:
        image_data = file.read()

    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO data_images (image_id, image_data) VALUES (?, ?)",
            (image_id, image_data)
        )
        conn.commit()
        print(f"Image data saved for image_id: {image_id}")
        
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
        
def get_image_data(self, image_id):
    """
    Retrieves image data (BLOB) from the database.

    Args:
        image_id: The ID of the image in the 'images' table.

    Returns:
        Image data as BLOB.
    """
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT image_data FROM data_images WHERE image_id = ?", (image_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print(f"No image data found for image_id: {image_id}")
            return None


def delete_image_data(self, image_id):
    """
    Deletes image data (BLOB) from the 'data_images' table.
    
    Args:
        image_id: The ID of the image whose data should be deleted.
    """
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        
        # Menghapus data gambar berdasarkan image_id
        cursor.execute("DELETE FROM data_images WHERE image_id = ?", (image_id,))
        
        # Melakukan commit untuk memastikan perubahan disimpan
        conn.commit()
        
        # Menjalankan VACUUM untuk mengurangi ukuran file database
        cursor.execute("VACUUM")
        conn.commit()
        
        print(f"Deleted image data for image_id: {image_id} and performed VACUUM to reclaim space.")

def process_algorithm(self, virtualenv_path=r"venv/Scripts/python.exe", base_path="UI/burst_denoising/algorithm"):
    """Handle algorithm processing when 'Process' button is clicked."""

    # Get selected algorithms and stacking method
    global_algorithm = self.left_panel.global_dropdown.currentText()
    local_algorithm = self.left_panel.local_dropdown.currentText()
    stacking_method = self.left_panel.stacking_dropdown.currentText()

    # Validate dropdown selections
    if global_algorithm == "None" and local_algorithm == "None" and stacking_method == "None":
        print("All processes are skipped. Please select at least one algorithm..")
        return

    # Dynamically define paths for algorithms
    global_algorithms = {self.left_panel.global_dropdown.itemText(i): os.path.join(base_path, "global_alignment", 
                           f"{self.left_panel.global_dropdown.itemText(i).replace(' ', '_').lower()}.py") 
                         for i in range(self.left_panel.global_dropdown.count())}

    local_algorithms = {self.left_panel.local_dropdown.itemText(i): os.path.join(base_path, "local_alignment", 
                          f"{self.left_panel.local_dropdown.itemText(i).replace(' ', '_').lower()}.py") 
                        for i in range(self.left_panel.local_dropdown.count())}

    stacking_methods = {self.left_panel.stacking_dropdown.itemText(i): os.path.join(base_path, "stacking", 
                         f"{self.left_panel.stacking_dropdown.itemText(i).replace(' ', '_').lower()}.py") 
                        for i in range(self.left_panel.stacking_dropdown.count())}

    # Prepare tasks for threading
    algorithm_tasks = []

    if global_algorithm != "None" and global_algorithm in global_algorithms:
        algorithm_tasks.append((virtualenv_path, global_algorithms[global_algorithm], f"Global Alignment: {global_algorithm}"))

    if local_algorithm != "None" and local_algorithm in local_algorithms:
        algorithm_tasks.append((virtualenv_path, local_algorithms[local_algorithm], f"Local Alignment: {local_algorithm}"))

    if stacking_method != "None" and stacking_method in stacking_methods:
        algorithm_tasks.append((virtualenv_path, stacking_methods[stacking_method], f"Stacking: {stacking_method}"))

    # Run algorithms in a separate thread
    self.algorithm_thread = RunningAlgorithmThreading(algorithm_tasks)

    # Start the thread
    self.algorithm_thread.start()
