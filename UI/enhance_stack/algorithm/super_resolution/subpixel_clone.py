import cv2
import numpy as np

def fast_subpixel_L2_alignment(fixed_image, moving_image):
    # Mengubah gambar menjadi grayscale
    fixed_gray = cv2.cvtColor(fixed_image, cv2.COLOR_BGR2GRAY)
    moving_gray = cv2.cvtColor(moving_image, cv2.COLOR_BGR2GRAY)

    # Estimasi pergeseran kasar (translasi) menggunakan metode cross-correlation
    result = cv2.matchTemplate(moving_gray, fixed_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # Pergeseran kasar dalam pixel
    shift_x = max_loc[0]
    shift_y = max_loc[1]

    # Tentukan ukuran window untuk pencarian subpixel
    window_size = 5
    best_shift = (shift_x, shift_y)
    min_error = float('inf')

    # Pencarian untuk pergeseran subpixel dengan interpolasi
    for dx in np.linspace(-0.5, 0.5, window_size):
        for dy in np.linspace(-0.5, 0.5, window_size):
            # Terapkan pergeseran dengan interpolasi bilinear
            shifted_image = np.roll(moving_gray, shift=(int(shift_y + dy), int(shift_x + dx)), axis=(0, 1))
            
            # Hitung kesalahan L2 (norma Euclidean)
            error = np.sqrt(np.sum((fixed_gray - shifted_image) ** 2))
            
            # Jika kesalahan L2 lebih kecil, simpan pergeseran baru
            if error < min_error:
                min_error = error
                best_shift = (shift_x + dx, shift_y + dy)

    return best_shift

# Muat gambar
fixed_image = cv2.imread('fixed_image.jpg')
moving_image = cv2.imread('moving_image.jpg')

# Terapkan algoritma fast subpixel alignment
shift = fast_subpixel_L2_alignment(fixed_image, moving_image)
print("Pergeseran subpixel terbaik:", shift)
