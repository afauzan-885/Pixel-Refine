import cv2
import numpy as np
import traceback

def align_hdr(ref_img, target_img, mode='simple', max_levels=6):
    """
    Menyelaraskan (align) gambar HDR menggunakan algoritma Median Threshold Bitmap (MTB).
    Sangat tahan terhadap perbedaan pencahayaan yang ekstrem.
    
    Args:
        ref_img: Gambar referensi (numpy array).
        target_img: Gambar target yang akan digeser (numpy array).
        mode: 'simple' (Translasi saja via MTB murni) atau 'complex' (Affine via ORB Feature di atas MTB).
        max_levels: Kedalaman piramida untuk MTB.
        
    Returns:
        (aligned_image, transformasi_matriks_M)
    """
    # Pastikan taichi_algorithm tersedia
    try:
        import taichi_library.taichi_algorithm as ta
    except ImportError:
        print("Warning: taichi_algorithm tidak ditemukan. Gunakan fallback jika ada.")
        return target_img, np.eye(3)

    if mode == 'simple':
        # --- Mode Simple: Murni Translasi (Sangat Cepat & Aman) ---
        dx, dy = ta.align_mtb(ref_img, target_img, max_levels=max_levels)
        
        h, w = target_img.shape[:2]
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        
        # Warp target image
        aligned = cv2.warpAffine(target_img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        return aligned, M

    elif mode == 'complex':
        # --- Mode Complex: Affine (Translasi, Skala, Rotasi, Shear) ---
        # 1. Dapatkan Median Threshold Bitmap untuk menyamakan pencahayaan ekstrem
        def get_bitmap(img):
            import taichi_library.taichi_algorithm.mtb as mtb
            gray = ta.cvtColor(img, ta.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            # Kita numpakan ke GPU untuk hitung median
            img_gpu, _ = ta.common.ensure_taichi_field(gray, dtype=ta.ti.f32)
            med = mtb.get_median(img_gpu)
            
            # Buat biner (0 dan 255 agar bisa dideteksi ORB)
            bitmap_np = np.where(gray > med, 255, 0).astype(np.uint8)
            return bitmap_np

        ref_bitmap = get_bitmap(ref_img)
        tgt_bitmap = get_bitmap(target_img)

        # 2. Ekstraksi Fitur (ORB) pada gambar Bitmap yang pencahayaannya kini sudah identik!
        orb = cv2.ORB_create(nfeatures=1000)
        
        kp1, des1 = orb.detectAndCompute(ref_bitmap, None)
        kp2, des2 = orb.detectAndCompute(tgt_bitmap, None)
        
        if des1 is None or des2 is None or len(kp1) < 10 or len(kp2) < 10:
            print("Peringatan: Tidak cukup fitur ditemukan pada Bitmap. Jatuh kembali ke 'simple'.")
            return align_hdr(ref_img, target_img, mode='simple', max_levels=max_levels)

        # 3. Pencocokan Fitur (Matcher)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        
        # Urutkan berdasarkan jarak
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Ambil 15% fitur terbaik
        good_matches = matches[:int(len(matches) * 0.15)]
        
        if len(good_matches) < 4:
            print("Peringatan: Tidak cukup pasangan fitur yang bagus. Jatuh kembali ke 'simple'.")
            return align_hdr(ref_img, target_img, mode='simple', max_levels=max_levels)

        # 4. Hitung Transformasi Affine
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Perhatikan: estimateAffinePartial2D menangani Translasi, Rotasi, dan Skala seragam
        # Jika Anda ingin menyertakan Shear, gunakan cv2.estimateAffine2D
        M, inliers = cv2.estimateAffinePartial2D(dst_pts, src_pts, method=cv2.RANSAC, ransacReprojThreshold=5.0)
        
        if M is None:
            print("Peringatan: Gagal menghitung Matriks Affine. Jatuh kembali ke 'simple'.")
            return align_hdr(ref_img, target_img, mode='simple', max_levels=max_levels)
            
        h, w = target_img.shape[:2]
        aligned = cv2.warpAffine(target_img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        
        return aligned, M
    
    else:
        raise ValueError("Mode harus 'simple' atau 'complex'.")

