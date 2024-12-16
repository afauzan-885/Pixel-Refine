import cv2, sys, os
import numpy as np
import sqlite3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from logic.database_manager import DatabaseManager  # Import setelah menambahkan path

# Fungsi untuk menghitung kesalahan L2
def calculate_L2_error(image1, image2, shift_x, shift_y):
    shifted_image2 = np.roll(image2, shift=(int(shift_y), int(shift_x)), axis=(0, 1))
    return np.linalg.norm(image1 - shifted_image2)

# Fungsi untuk mencari subpixel alignment
def subpixel_alignment(image1, image2):
    # Menyelarakan dua gambar pada tingkat piksel pertama
    result = cv2.matchTemplate(image1, image2, method=cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # Lokasi terbaik dalam piksel
    best_match = max_loc
    shift_x = best_match[0]
    shift_y = best_match[1]
    
    # Menyesuaikan untuk subpixel alignment dengan interpolasi
    subpixel_shift_x, subpixel_shift_y = optimize_subpixel_shift(image1, image2, shift_x, shift_y)
    
    return subpixel_shift_x, subpixel_shift_y

# Fungsi untuk optimasi subpixel dengan gradient descent
def optimize_subpixel_shift(image1, image2, initial_shift_x, initial_shift_y, learning_rate=0.1, max_iter=100):
    shift_x, shift_y = initial_shift_x, initial_shift_y
    for _ in range(max_iter):
        # Menghitung kesalahan L2 untuk posisi shift saat ini
        error = calculate_L2_error(image1, image2, shift_x, shift_y)
        
        # Menggunakan gradient descent untuk mengoptimalkan shift
        grad_x = (calculate_L2_error(image1, image2, shift_x + 1e-4, shift_y) - error) / 1e-4
        grad_y = (calculate_L2_error(image1, image2, shift_x, shift_y + 1e-4) - error) / 1e-4
        
        shift_x -= learning_rate * grad_x
        shift_y -= learning_rate * grad_y
        
        # Jika kesalahan cukup kecil, hentikan
        if abs(grad_x) < 1e-6 and abs(grad_y) < 1e-6:
            break
    
    return shift_x, shift_y

# Inisialisasi DatabaseManager dan path database
db_path = 'pixel_refine_database.db'  # Ganti dengan path database Anda
db_manager = DatabaseManager(db_path)

# Ambil semua path gambar dari database
image_paths = db_manager.get_all_image_paths()

# Simpan gambar yang diambil dari path ke dalam database
for image_id, image_path in enumerate(image_paths):
    db_manager.save_image_data(image_id, image_path)

# Pastikan ada cukup gambar dalam database
if len(image_paths) >= 2:
    # Iterasi melalui semua pasangan gambar
    for i in range(len(image_paths)):
        for j in range(i + 1, len(image_paths)):
            # Mengambil data gambar dari database
            image1_data = db_manager.get_image_data(i)
            image2_data = db_manager.get_image_data(j)
            
            if image1_data and image2_data:
                # Mengonversi BLOB ke array numpy untuk diproses dengan OpenCV
                image1 = cv2.imdecode(np.frombuffer(image1_data, np.uint8), cv2.IMREAD_GRAYSCALE)
                image2 = cv2.imdecode(np.frombuffer(image2_data, np.uint8), cv2.IMREAD_GRAYSCALE)
                
                # Melakukan subpixel alignment
                shift_x, shift_y = subpixel_alignment(image1, image2)
                
                print(f"Subpixel shift between image {i} and image {j}: X = {shift_x}, Y = {shift_y}")

    # Menghapus semua gambar setelah proses alignment selesai
    for image_id in range(len(image_paths)):
        db_manager.delete_image_data(image_id)
else:
    print("Tidak ada cukup gambar dalam database untuk melakukan alignment.")
