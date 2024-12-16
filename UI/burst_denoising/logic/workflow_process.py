import sqlite3
import subprocess, os

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

def process_algorithm(self):
    """Handle algorithm processing when 'Process' button is clicked."""
    
    # Get selected algorithms and stacking method
    global_algorithm = self.left_panel.global_dropdown.currentText()
    local_algorithm = self.left_panel.local_dropdown.currentText()
    stacking_method = self.left_panel.stacking_dropdown.currentText()

    # Get the stacking method label text
    stacking_label_text = self.left_panel.stacking_dropdown.currentText()

    # Define the base path to the algorithms
    base_path = os.path.join("UI", "burst_denoising", "algorithm")

    # Dynamically define global, local, and stacking algorithms from dropdown items
    global_algorithms = {self.left_panel.global_dropdown.itemText(i): os.path.join(base_path, "global_alignment", f"{self.left_panel.global_dropdown.itemText(i).replace(' ', '_').lower()}.py") 
                         for i in range(self.left_panel.global_dropdown.count())}

    local_algorithms = {self.left_panel.local_dropdown.itemText(i): os.path.join(base_path, "local_alignment", f"local_alignment_{self.left_panel.local_dropdown.itemText(i).replace(' ', '_').lower()}.py") 
                        for i in range(self.left_panel.local_dropdown.count())}

    stacking_methods = {self.left_panel.stacking_dropdown.itemText(i): os.path.join(base_path, "stacking", f"stacking_{self.left_panel.stacking_dropdown.itemText(i).replace(' ', '_').lower()}.py") 
                        for i in range(self.left_panel.stacking_dropdown.count())}

    # Process Global Alignment based on dropdown selection
    if global_algorithm in global_algorithms:
        print(f"Processing Global Alignment: using {global_algorithm}...")
        subprocess.run(["python", global_algorithms[global_algorithm]])

    # Process Local Alignment based on dropdown selection, only if global alignment was successful
    if local_algorithm in local_algorithms:
        print(f"Processing Local Alignment: using {local_algorithm}...")
        subprocess.run(["python", local_algorithms[local_algorithm]])

    # Process Stacking based on dropdown selection, only if local alignment was successful
    if stacking_method in stacking_methods:
        formatted_method = stacking_label_text.replace(" ", "_")  # Format method name, replace spaces with underscores
        print(f"Processing Stacking: using {formatted_method}...")
        subprocess.run(["python", stacking_methods[stacking_method]])
