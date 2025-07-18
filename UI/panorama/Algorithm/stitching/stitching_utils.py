from concurrent.futures import ThreadPoolExecutor
import os
import cv2
import numpy as np
from typing import List, Union, Tuple, Any
from cv2 import KeyPoint

"""
Skrip ini berisi fungsi-fungsi utilitas statis untuk pemrosesan gambar,
dirancang untuk dapat digunakan kembali di berbagai bagian aplikasi.
"""

def load_images(paths: List[str]) -> Union[List[np.ndarray], str]:
    """
    Memuat satu atau lebih gambar dari path yang diberikan.

    Args:
        paths (List[str]): Daftar path file gambar.

    Returns:
        Union[List[np.ndarray], str]: Daftar gambar yang dimuat sebagai array NumPy,
                                      atau pesan error jika salah satu gambar gagal dimuat.
    """
    images = []
    for path in paths:
        img = cv2.imread(path)
        if img is None:
            return f"Gagal memuat gambar: {path}"
        # Pastikan gambar selalu 3 channel (BGR) untuk konsistensi
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        images.append(img)
    return images

def estimate_focal_length(img: np.ndarray, sensor_width_mm: float = 36.0, focal_length_mm: float = 26.0) -> float:
    """
    Memperkirakan panjang fokus dalam piksel berdasarkan parameter kamera umum.
    Fungsi dibuat lebih generik dengan parameter opsional.

    Args:
        img (np.ndarray): Gambar input untuk mendapatkan dimensi lebar.
        sensor_width_mm (float, optional): Lebar sensor fisik kamera dalam mm. Default ke 36.0 (full-frame).
        focal_length_mm (float, optional): Panjang fokus lensa dalam mm. Default ke 26.0.

    Returns:
        float: Panjang fokus yang diperkirakan dalam satuan piksel.
    """
    if img.ndim != 2:
        h, w, _ = img.shape
    else:
        h, w = img.shape
        
    f_px = (focal_length_mm / sensor_width_mm) * w
    return f_px

def get_image_dimensions(path):
    img = cv2.imread(path)
    return img.shape

def _process_anms_chunk(args):
    """
    Fungsi pembantu yang dijalankan oleh setiap worker thread.
    Menghitung suppression radii untuk sebagian (chunk) dari keypoints.
    """
    start_idx, end_idx, pts, responses = args
    chunk_radii = np.full(end_idx - start_idx, np.inf)

    # Lakukan perbandingan hanya dalam rentang yang diberikan (chunk)
    for i in range(start_idx, end_idx):
        # Temukan semua titik yang lebih kuat di seluruh set data
        stronger_pts_mask = responses > responses[i]
        
        if not np.any(stronger_pts_mask):
            continue
            
        stronger_pts = pts[stronger_pts_mask]
        
        # Hitung jarak kuadrat dan temukan minimumnya
        dist_sq = np.sum((stronger_pts - pts[i])**2, axis=1)
        chunk_radii[i - start_idx] = np.min(dist_sq)
        
    return chunk_radii

def apply_anms(keypoints, num_points_to_keep, use_multicore=True):
    """
    Menerapkan Adaptive Non-Maximal Suppression secara paralel untuk menyebarkan keypoint.
    """
    n_keypoints = len(keypoints)
    if n_keypoints <= num_points_to_keep:
        return keypoints, list(range(n_keypoints))

    # Ekstrak data sekali untuk efisiensi
    pts = np.array([kp.pt for kp in keypoints])
    responses = np.array([kp.response for kp in keypoints])
    
    radii = np.full(n_keypoints, np.inf)

    # <<< INI BAGIAN UTAMA OPTIMISASI >>>
    if use_multicore:
        num_workers = os.cpu_count() or 4
        chunk_size = (n_keypoints + num_workers - 1) // num_workers # Bagi pekerjaan secara merata
        
        tasks = []
        for i in range(num_workers):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, n_keypoints)
            if start_idx >= end_idx:
                continue
            # Siapkan argumen untuk setiap worker
            tasks.append((start_idx, end_idx, pts, responses))

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Jalankan semua tugas secara paralel
            results = list(executor.map(_process_anms_chunk, tasks))
        
        # Gabungkan hasil dari semua worker menjadi satu array radii
        current_pos = 0
        for chunk_result in results:
            radii[current_pos : current_pos + len(chunk_result)] = chunk_result
            current_pos += len(chunk_result)
            
    else: # Fallback ke metode serial jika tidak menggunakan multicore
        for i in range(n_keypoints):
            stronger_pts_mask = responses > responses[i]
            if not np.any(stronger_pts_mask):
                continue
            stronger_pts = pts[stronger_pts_mask]
            dist_sq = np.sum((stronger_pts - pts[i])**2, axis=1)
            radii[i] = np.min(dist_sq)

    # Bagian ini tetap sama dan sangat cepat
    sorted_indices = np.argsort(radii)[::-1]
    best_indices = sorted_indices[:num_points_to_keep]
    anms_keypoints = [keypoints[i] for i in best_indices]
    
    return anms_keypoints, best_indices    
def compute_features_for_block(
    detector: Any,  # <<< INI KUNCINYA: Menerima detektor apa pun
    enhanced_gray_base: np.ndarray, 
    enhanced_gray_target: np.ndarray, 
    block_coords: Tuple[int, int, int, int],
    img_dims: Tuple[int, int],
    overlap_px: int, 
    max_kps_per_block: int = 500
) -> Tuple[List[KeyPoint], np.ndarray, List[KeyPoint], np.ndarray]:
    """
    Mengekstrak fitur dalam satu blok gambar menggunakan detektor yang diberikan.
    Fungsi ini agnostik terhadap algoritma (bisa SIFT, ORB, AKAZE, dll.).

    Returns:
        Tuple: Keypoints dan deskriptor untuk gambar dasar dan target.
    """
    x, y, bw, bh = block_coords
    img_w, img_h = img_dims

    # Logika untuk ROI, cropping, dll. tetap sama persis
    roi_x_start = max(0, x - overlap_px)
    roi_y_start = max(0, y - overlap_px)
    roi_x_end = min(img_w, x + bw + overlap_px)
    roi_y_end = min(img_h, y + bh + overlap_px)

    if roi_y_end <= roi_y_start or roi_x_end <= roi_x_start:
        return [], np.array([]), [], np.array([]) # Selalu kembalikan tipe yang konsisten

    roi_base_enhanced = enhanced_gray_base[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
    roi_target_enhanced = enhanced_gray_target[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

    # >>> INI PERUBAHAN UTAMANYA <<<
    # Tidak lagi memanggil akaze_instance, tapi objek 'detector' yang generik
    kps_base, desc_base = detector.detectAndCompute(roi_base_enhanced, None)
    kps_target, desc_target = detector.detectAndCompute(roi_target_enhanced, None)

    def adjust_and_filter_kps(kps, descs, current_block_coords):
        adjusted_kps = []
        valid_desc_indices = []
        if kps and descs is not None:
            cx, cy, cbw, cbh = current_block_coords
            for idx, kp in enumerate(kps):
                orig_x = kp.pt[0] + roi_x_start
                orig_y = kp.pt[1] + roi_y_start
                if cx <= orig_x < cx + cbw and cy <= orig_y < cy + cbh:
                    if idx < len(descs):
                        kp.pt = (orig_x, orig_y)
                        adjusted_kps.append(kp)
                        valid_desc_indices.append(idx)
        if descs is not None and valid_desc_indices:
            filtered_descs = descs[np.array(valid_desc_indices)]
        else:
            filtered_descs = np.array([]) # Kembalikan array kosong, bukan None
        return adjusted_kps, filtered_descs

    kps_base_adj, final_desc_base = adjust_and_filter_kps(kps_base, desc_base, block_coords)
    kps_target_adj, final_desc_target = adjust_and_filter_kps(kps_target, desc_target, block_coords)
    
    def select_top_k(kps, descs, k):
        if descs is None or len(kps) == 0:
            return [], np.array([])
        if len(kps) <= k:
            return kps, descs
        sorted_idx = np.argsort([-kp.response for kp in kps])[:k]
        return [kps[i] for i in sorted_idx], descs[sorted_idx]

    kps_base_adj, final_desc_base = select_top_k(kps_base_adj, final_desc_base, max_kps_per_block)
    kps_target_adj, final_desc_target = select_top_k(kps_target_adj, final_desc_target, max_kps_per_block)

    return kps_base_adj, final_desc_base, kps_target_adj, final_desc_target