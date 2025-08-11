# File: UI/panorama/logic/projection.py

import cv2
import numpy as np

from UI.panorama.Algorithm.stitching import stitching_utils

# =========================================================================
# === 1. Logika Cropping ===
# =========================================================================

def _find_safe_cropping_rect(masks):
    """
    Menemukan persegi panjang terbesar yang bisa memuat semua area valid
    dari semua mask. Ini adalah implementasi auto-crop sederhana.
    """
    if not masks:
        return None

    # Gabungkan semua mask menjadi satu untuk menemukan area valid total
    # Kita mulai dengan mask pertama
    combined_mask = masks[0].copy()
    for i in range(1, len(masks)):
        # Gunakan bitwise_and untuk menemukan area di mana SEMUA gambar ada.
        # Ini adalah crop yang sangat aman tapi mungkin terlalu kecil.
        # cv2.bitwise_or(combined_mask, masks[i], combined_mask)
        # Atau gunakan bitwise_or untuk area di mana SETIDAKNYA SATU gambar ada.
        # Ini lebih umum untuk auto-crop.
        combined_mask = cv2.bitwise_or(combined_mask, masks[i])

    # Temukan kontur dari area valid
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
        
    # Temukan bounding box dari kontur terbesar
    all_points = np.concatenate(contours, axis=0)
    x, y, w, h = cv2.boundingRect(all_points)
    
    # Untuk keamanan, kita bisa sedikit menyusutkan hasilnya (opsional)
    # x += int(w * 0.01); w = int(w * 0.98)
    # y += int(h * 0.01); h = int(h * 0.98)

    return (x, y, w, h)

def perform_crop(images_to_crop, masks_to_crop, crop_mode="Auto", manual_rect=None):
    """
    Memotong daftar gambar dan mask berdasarkan mode yang dipilih.
    """
    if crop_mode == "Manual" and manual_rect:
        x, y, w, h = manual_rect
    elif crop_mode == "Auto":
        rect = _find_safe_cropping_rect(masks_to_crop)
        if rect is None:
            return images_to_crop, masks_to_crop # Gagal auto-crop, kembalikan apa adanya
        x, y, w, h = rect
    else: # Jika mode tidak dikenali atau Auto gagal
        return images_to_crop, masks_to_crop

    cropped_images = []
    cropped_masks = []
    
    for img, mask in zip(images_to_crop, masks_to_crop):
        cropped_img = img[y:y+h, x:x+w]
        cropped_mask = mask[y:y+h, x:x+w]
        cropped_images.append(cropped_img)
        cropped_masks.append(cropped_mask)
        
    return cropped_images, cropped_masks

# =========================================================================
# === 2. Logika Proyeksi ===
# =========================================================================

def _cylindrical_warp_remap(img, K):
    """
    Proyeksi silinder menggunakan cv2.remap. Lebih cepat dan lebih akurat.
    """
    foc_len = (K[0, 0] + K[1, 1]) / 2
    height, width = img.shape[:2]
    
    cylinder = np.zeros_like(img)
    
    # Buat grid koordinat output
    x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))
    
    # Konversi ke koordinat yang dinormalisasi
    theta = (x_coords - K[0, 2]) / foc_len
    h = (y_coords - K[1, 2]) / foc_len
    
    # Proyeksikan ke koordinat 3D silinder
    x_3d = np.sin(theta)
    y_3d = h
    z_3d = np.cos(theta)
    
    p = np.stack([x_3d, y_3d, z_3d], axis=-1)
    
    # Proyeksikan kembali ke bidang gambar sumber
    # p @ K.T akan lebih efisien untuk array besar
    p_flat = p.reshape(-1, 3)
    image_points_flat = p_flat @ K.T
    
    # Normalisasi (membagi dengan z)
    points_flat = image_points_flat[:, :2] / image_points_flat[:, 2, np.newaxis]
    
    # Bentuk kembali ke ukuran gambar asli untuk peta remap
    map_x = points_flat[:, 0].reshape(height, width).astype(np.float32)
    map_y = points_flat[:, 1].reshape(height, width).astype(np.float32)

    # Lakukan warping menggunakan peta remap
    cylinder = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR)
    return cylinder

def project_cylindrical(original_images, alignment_data, settings):
    print("INFO: Memulai proyeksi Cylindrical (Implementasi Remap)...")
    homographies = alignment_data["homographies"]
    
    warped_images = []
    
    for i, img in enumerate(original_images):
        h, w = img.shape[:2]
        # Estimasi matriks kamera K yang sederhana
        focal_length = (w + h) / 2
        K = np.array([[focal_length, 0, w/2],
                      [0, focal_length, h/2],
                      [0, 0, 1]], dtype=np.float32)

        # Warp gambar ke silinder
        cyl_img = _cylindrical_warp_remap(img, K)
        
        # Warp lagi menggunakan homografi planar (ini tetap aproksimasi)
        final_warped, _ = stitching_utils.warp_image(
            image=cyl_img,
            homography=homographies[i],
            output_size=alignment_data["canvas_size"],
            translation=alignment_data["translation"]
        )
        warped_images.append(final_warped)
        
    # Buat mask gabungan setelah semua di-warp
    warped_masks = [(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) > 0).astype(np.uint8) for img in warped_images]
    
    return warped_images, warped_masks


def project_planar(alignment_data, settings):
    """
    Proyeksi planar hanya menggunakan gambar yang sudah di-warp dari tahap alignment.
    """
    print("INFO: Menggunakan proyeksi Planar (data dari tahap alignment).")
    return alignment_data["warped_images"], alignment_data["warped_masks"]


# =========================================================================
# === 3. Fungsi Dispatcher Utama ===
# =========================================================================
PROJECTION_DISPATCHER = {
    "Cylindrical": project_cylindrical,
    "Planar": project_planar,
    # Tambahkan "Spherical" dan "Fisheye" di sini nanti
}

def run_projection_and_crop(alignment_data, original_images, settings):
    """
    Fungsi utama untuk menjalankan proyeksi dan cropping.
    """
    projection_type = settings.get("projection_type", "Planar")
    crop_mode = "Auto" 

    projection_function = PROJECTION_DISPATCHER.get(projection_type)
    if not projection_function:
        raise NotImplementedError(f"Proyeksi '{projection_type}' belum diimplementasikan.")

    # Jalankan proyeksi dengan argumen yang benar
    if projection_type == "Planar":
        warped_images, warped_masks = projection_function(alignment_data, settings)
    else:
        # Proyeksi lain (seperti Cylindrical) butuh gambar asli DAN data alignment
        warped_images, warped_masks = projection_function(
            original_images, alignment_data, settings
        )

    # Jalankan cropping
    cropped_images, cropped_masks = perform_crop(warped_images, warped_masks, crop_mode)
    
    # Buat gambar pratinjau dari hasil crop
    preview_image = stitching_utils.create_simple_preview(cropped_images, cropped_masks)

    return {
        "stitched_image": preview_image,
        "warped_images": cropped_images,
        "warped_masks": cropped_masks,
        "error": None
    }