from concurrent.futures import ThreadPoolExecutor, as_completed
import gc
import os
import cv2
import numpy as np
import dask
import dask.array as da
from typing import List
from scipy.linalg import expm, logm
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import estimate_noise_variance, get_adaptive_bilateral
"""
Skrip ini berisi fungsi-fungsi utilitas statis untuk pemrosesan gambar,
dirancang untuk dapat digunakan kembali di berbagai bagian aplikasi.
"""
def load_images(paths: List[str]) -> List[np.ndarray]:
    """
    Memuat satu atau lebih gambar dari path yang diberikan.
    Memastikan semua gambar dikembalikan dalam format BGR 3-channel.

    Args:
        paths (List[str]): Daftar path file gambar.

    Returns:
        List[np.ndarray]: Daftar gambar yang dimuat sebagai array NumPy.

    Raises:
        IOError: Jika salah satu file gambar tidak dapat ditemukan atau dibaca.
    """
    images = []
    for path in paths:
        if not os.path.exists(path):
            raise IOError(f"File tidak ditemukan: {path}")
        img = cv2.imread(path)
        if img is None:
            raise IOError(f"Gagal membaca atau format tidak didukung untuk gambar: {path}")
        
        # Untuk konsistensi, konversi gambar grayscale menjadi BGR
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        images.append(img)
    return images

def detect_features(img, detector, use_multicore=True, num_features=5000):
    """
    Mendeteksi fitur pada satu gambar dengan strategi per-blok yang canggih.
    VERSI OPTIMAL: Menerima objek detektor yang sudah dibuat.
    """
    if img is None: return [], None
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img.astype(np.uint8)
    
    # 1. Pra-pemrosesan dengan CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_gray_img = clahe.apply(gray_img)
    
    # 2. Pra-pemrosesan dengan Bilateral Filter (INI MASIH PER GAMBAR, DAN ITU BENAR)
    #    Keputusan untuk menerapkan filter ini bergantung pada noise gambar individual, jadi
    #    logika ini harus tetap di sini. Kita tidak bisa menghindarinya.
    noise_level = estimate_noise_variance(enhanced_gray_img)
    if noise_level > 600.0:
        d, sigma, _ = get_adaptive_bilateral(noise_level, 300, 800, 5, 9, 20, 75)
        print(f"Noise tinggi ({noise_level:.2f}), menerapkan Bilateral Filter (d={d}, sigma={sigma})...")
        enhanced_gray_img = cv2.bilateralFilter(enhanced_gray_img, d, sigma, sigma)

    h, w = enhanced_gray_img.shape
    # Kita bisa membuat max_kps_per_block lebih dinamis, tapi untuk sekarang ini sudah cukup.
    num_blocks, overlap, max_kps_per_block = (3, 3), 30, 600

    # 3. Inisialisasi Detektor DIHAPUS DARI SINI
    #    'detector' sekarang adalah argumen yang masuk.

    def process_block(i, j):
        # ... (logika process_block tidak berubah) ...
        roi_x, roi_y = i * (w // num_blocks[0]), j * (h // num_blocks[1])
        roi_w, roi_h = w // num_blocks[0], h // num_blocks[1]
        x_start, y_start = max(0, roi_x - overlap), max(0, roi_y - overlap)
        x_end, y_end = min(w, roi_x + roi_w + overlap), min(h, y_start + roi_h + overlap) # Koreksi bug kecil
        block_gray = enhanced_gray_img[y_start:y_end, x_start:x_end]
        kps, des = detector.detectAndCompute(block_gray, None)
        if kps is None or len(kps) == 0: return [], None
        
        if len(kps) > max_kps_per_block:
            indices = np.argsort([-kp.response for kp in kps])[:max_kps_per_block]
            kps = [kps[i] for i in indices]
            if des is not None: des = des[indices]

        for kp in kps: kp.pt = (kp.pt[0] + x_start, kp.pt[1] + y_start)
        return kps, des
    
    keypoints, descriptor_list = [], []
    if use_multicore:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(process_block, i, j) for i in range(num_blocks[0]) for j in range(num_blocks[1])]
            for future in as_completed(futures):
                kps, des = future.result()
                if des is not None and des.shape[0] > 0:
                    keypoints.extend(kps)
                    descriptor_list.append(des)
    else:
        for i in range(num_blocks[0]):
            for j in range(num_blocks[1]):
                kps, des = process_block(i, j)
                if des is not None and des.shape[0] > 0:
                    keypoints.extend(kps)
                    descriptor_list.append(des)

    if not descriptor_list: return [], None
    descriptors = np.vstack(descriptor_list)
    
    # Hapus duplikat
    unique_kps, unique_des_indices = [], []
    seen_coords = set()
    for i, kp in enumerate(keypoints):
        coord = tuple(map(int, kp.pt))
        if coord not in seen_coords:
            seen_coords.add(coord)
            unique_kps.append(kp)
            unique_des_indices.append(i)
    keypoints, descriptors = unique_kps, descriptors[unique_des_indices]
    
    # Seleksi Top-K Final
    if num_features > 0 and len(keypoints) > num_features:
        indices = np.argsort([-kp.response for kp in keypoints])[:num_features]
        keypoints = [keypoints[i] for i in indices]
        descriptors = descriptors[indices]
    
    return keypoints, descriptors

def match_features(des1: np.ndarray, des2: np.ndarray, ratio_thresh: float = 0.75) -> List[cv2.DMatch]:
    """
    Mencocokkan dua set deskriptor menggunakan Lowe's Ratio Test.
    Secara otomatis memilih matcher yang sesuai (BFMatcher atau FlannBasedMatcher).

    Args:
        des1 (np.ndarray): Deskriptor dari gambar pertama.
        des2 (np.ndarray): Deskriptor dari gambar kedua.
        ratio_thresh (float): Ambang batas untuk Lowe's Ratio Test.

    Returns:
        List[cv2.DMatch]: Daftar pencocokan yang baik.
    """
    if des1 is None or des2 is None or len(des1) < 2 or len(des2) < 2:
        return []

    # Pilih matcher berdasarkan tipe data deskriptor
    if des1.dtype == np.uint8:  # Biasanya untuk ORB, BRISK (binary)
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    else:  # Biasanya untuk SIFT, AKAZE (float)
        des1 = np.float32(des1)
        des2 = np.float32(des2)
        matcher = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
    
    # Lakukan pencocokan k-NN
    matches_knn = matcher.knnMatch(des1, des2, k=2)
    
    # Terapkan Lowe's Ratio Test
    good_matches = []
    for m_n in matches_knn:
        if len(m_n) == 2 and m_n[0].distance < ratio_thresh * m_n[1].distance:
            good_matches.append(m_n[0])
            
    return good_matches

# ==============================================================================
# Fungsi untuk Komposisi Graf dan Warping
# ==============================================================================

def compose_transformations_from_graph(pairwise_matches, n_images, anchor_idx):
    if not pairwise_matches: return None
    rows = [m["src_idx"] for m in pairwise_matches]
    cols = [m["dst_idx"] for m in pairwise_matches]
    weights = [-float(m["confidence"]) for m in pairwise_matches]
    graph = csr_matrix((weights, (rows, cols)), shape=(n_images, n_images), dtype=np.float64)
    
    mst = minimum_spanning_tree(graph)
    mst_graph = mst.toarray()
    
    transform_map = {}
    for match in pairwise_matches:
        transform_map[(match['src_idx'], match['dst_idx'])] = match['T']
        try:
            transform_map[(match['dst_idx'], match['src_idx'])] = np.linalg.inv(match['T'])
        except np.linalg.LinAlgError: continue
    
    final_transforms = [None] * n_images
    final_transforms[anchor_idx] = np.eye(3)
    q = [anchor_idx]
    visited = {anchor_idx}
    while q:
        current_idx = q.pop(0)
        neighbors_fwd = np.where(mst_graph[current_idx, :] != 0)[0]
        neighbors_bwd = np.where(mst_graph[:, current_idx] != 0)[0]
        for neighbor_idx in list(neighbors_fwd) + list(neighbors_bwd):
            if neighbor_idx not in visited:
                visited.add(neighbor_idx)
                T_to_neighbor = transform_map.get((current_idx, neighbor_idx))
                if T_to_neighbor is not None:
                    final_transforms[neighbor_idx] = final_transforms[current_idx] @ T_to_neighbor
                    q.append(neighbor_idx)
    
    if any(t is None for t in final_transforms): return None
    return final_transforms

def center_FOV(homographies: list):
    """
    Mengambil daftar homografi yang relatif terhadap satu anchor, dan memusatkannya
    sehingga semua gambar di-warp menuju "bidang tengah" virtual.
    Ini mengimplementasikan prinsip "Meet in the Middle" untuk N-gambar.

    Args:
        homographies (list): Daftar matriks homografi 3x3 (np.ndarray).
                             Salah satunya diasumsikan sebagai matriks identitas (anchor).

    Returns:
        list: Daftar homografi 3x3 baru yang semuanya telah dikoreksi.
    """
    print("  > Menghitung transformasi terpusat (centering transformations)...")
    
    # Langkah 1: Hitung "rata-rata" dari semua homografi di ruang logaritmik.
    log_homographies = []
    for H in homographies:
        # Normalisasi untuk stabilitas numerik, penting untuk logm
        H_normalized = H / H[2, 2]
        try:
            # logm mengubah transformasi proyektif menjadi ruang linear di mana kita bisa merata-ratakannya
            log_H = logm(H_normalized)
            log_homographies.append(log_H)
        except Exception as e:
            print(f"Peringatan: logm gagal untuk homografi, dilewati. Error: {e}")
            continue
            
    if not log_homographies:
        print("Peringatan: Tidak bisa menghitung pusat virtual. Tidak ada koreksi yang diterapkan.")
        return homographies # Kembalikan homografi asli jika gagal

    # Rata-ratakan semua log-homografi untuk menemukan "orientasi tengah"
    avg_log_H = np.mean(log_homographies, axis=0)
    
    # Kembalikan ke ruang homografi normal dengan expm
    H_avg = expm(avg_log_H)
    
    # Langkah 2: Buat "transformasi koreksi" yang merupakan kebalikan dari orientasi rata-rata.
    try:
        H_correction = np.linalg.inv(H_avg)
    except np.linalg.LinAlgError:
        print("Peringatan: Gagal menginversi H_avg. Tidak ada koreksi yang diterapkan.")
        return homographies

    # Langkah 3: Terapkan koreksi ke SEMUA homografi.
    # Ini memastikan bahkan gambar anchor pun ikut di-warp.
    centered_homographies = [H_correction @ H for H in homographies]
    
    print("    - Transformasi berhasil dipusatkan.")
    return centered_homographies

def _warp_to_dask_array(image_path, homography, output_shape, *args, **kwargs):
    img = cv2.imread(image_path)
    if img is None:
        return (
            np.zeros(output_shape, dtype=np.float32), 
            np.zeros((output_shape[0], output_shape[1]), dtype=np.float32)
        )

    warped_np = cv2.warpPerspective(img, homography, (output_shape[1], output_shape[0]))
    mask_np = (cv2.cvtColor(warped_np, cv2.COLOR_BGR2GRAY) > 0).astype(np.float32)

    del img
    return warped_np.astype(np.float32), mask_np

def _process_single_tile(args):
    """
    Fungsi helper yang memproses satu ubin. Dirancang untuk dijalankan secara paralel oleh joblib.
    """
    # Unpack argumen
    y_start, x_start, tile_shape, full_output_shape, homographies, image_paths, image_shapes = args
    
    # KUNCI: Akumulator hanya seukuran satu ubin!
    tile_sum = np.zeros(tile_shape, dtype=np.float32)
    count_map = np.zeros((tile_shape[0], tile_shape[1]), dtype=np.float32)

    # Iterasi melalui setiap gambar sumber untuk melihat apakah ia berkontribusi pada ubin ini
    for i in range(len(image_paths)):
        try:
            H_inv = np.linalg.inv(homographies[i])
        except np.linalg.LinAlgError:
            continue

        y_end, x_end = y_start + tile_shape[0], x_start + tile_shape[1]
        tile_corners = np.float32([[x_start, y_start], [x_end, y_start], [x_end, y_end], [x_start, y_end]]).reshape(-1, 1, 2)
        orig_corners = cv2.perspectiveTransform(tile_corners, H_inv)
        
        min_x_orig, min_y_orig = np.min(orig_corners, axis=0).ravel()
        max_x_orig, max_y_orig = np.max(orig_corners, axis=0).ravel()
        
        h_orig, w_orig, _ = image_shapes[i]
        if max_x_orig < 0 or min_x_orig > w_orig or max_y_orig < 0 or min_y_orig > h_orig:
            continue

        T_tile = np.array([[1, 0, -x_start], [0, 1, -y_start], [0, 0, 1]])
        H_tile = T_tile @ homographies[i]

        img_to_process = cv2.imread(image_paths[i])
        if img_to_process is None: continue

        warped_tile = cv2.warpPerspective(img_to_process, H_tile, (tile_shape[1], tile_shape[0]))
        
        mask = (cv2.cvtColor(warped_tile, cv2.COLOR_BGR2GRAY) > 0).astype(np.float32)
        tile_sum += warped_tile
        count_map += mask
        
        del img_to_process, warped_tile, mask

    count_map[count_map == 0] = 1.0
    final_tile = (tile_sum / count_map[..., np.newaxis]).astype(np.uint8)
    
    # Kembalikan posisi ubin dan datanya
    return (y_start, x_start, final_tile)

def warp_image(image: np.ndarray, homography: np.ndarray, output_size: tuple, translation: list = [0, 0]) -> tuple:
    """
    Melakukan warp perspektif pada sebuah gambar dan membuat mask-nya.

    Args:
        image (np.ndarray): Gambar yang akan di-warp.
        homography (np.ndarray): Matriks homografi 3x3.
        output_size (tuple): Ukuran kanvas output (lebar, tinggi).
        translation (list): Ofset translasi [tx, ty] untuk diterapkan pada homografi.

    Returns:
        tuple: (warped_image, mask)
               - warped_image: Gambar yang telah di-warp.
               - mask: Mask biner dari area non-hitam pada gambar yang di-warp.
    """
    # Gabungkan matriks translasi dengan homografi
    translation_matrix = np.array([[1, 0, translation[0]], 
                                   [0, 1, translation[1]], 
                                   [0, 0, 1]])
    final_homography = translation_matrix @ homography

    # Lakukan warp pada gambar
    warped_image = cv2.warpPerspective(image, final_homography, output_size,
                                       flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
    
    # Buat mask dari hasil warp (area yang tidak hitam)
    gray_warped = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
    mask = (gray_warped > 0).astype(np.uint8)
    
    return warped_image, mask

def rewarp_from_homography(original_images, minimal_cache_data, settings, progress_callback):
    """
    Merekontruksi paket data panorama lengkap hanya dari gambar asli dan data homografi.
    Fungsi ini menjalankan bagian akhir dari proses stitching.
    """
    print("INFO: Memulai proses re-warping dari data cache minimal...")
    try:
        # 1. Ekstrak data yang dibutuhkan dari cache
        homographies = minimal_cache_data.get("homographies")
        output_size = minimal_cache_data.get("canvas_size")
        translation = minimal_cache_data.get("translation")
        
        if not all([homographies, output_size, translation]):
            return {"error": "Data cache minimal tidak lengkap."}

        # 2. Loop melalui setiap gambar dan lakukan warp
        n_images = len(original_images)
        final_warped_images = []
        final_warped_masks = []
        
        # Siapkan untuk membuat gambar pratinjau
        panorama_sum = np.zeros((output_size[1], output_size[0], 3), dtype=np.float32)
        image_count_map = np.zeros((output_size[1], output_size[0]), dtype=np.float32)

        progress_step = 1.0 / n_images
        
        for idx, (img, H) in enumerate(zip(original_images, homographies)):
            # Beri laporan progres
            progress_callback(idx * progress_step, f"Re-warping gambar {idx+1}...")
            
            # Gunakan utilitas warp_image di sini, dengan argumen yang benar!
            warped_img, mask = warp_image(
                image=img, 
                homography=H, 
                output_size=output_size, 
                translation=translation
            )
            
            # Kumpulkan hasil individual
            final_warped_images.append(warped_img)
            final_warped_masks.append(mask)
            
            # Hitung panorama kasar untuk preview
            panorama_sum += warped_img
            image_count_map += mask

        progress_callback(0.98, "Menyelesaikan pratinjau...")
        image_count_map[image_count_map == 0] = 1.0 
        panorama_preview = (panorama_sum / image_count_map[..., np.newaxis]).astype(np.uint8)
        
        # 3. Kembalikan paket data lengkap, sama seperti hasil dari proses penuh
        return {
            "stitched_image": panorama_preview,
            "warped_images": final_warped_images,
            "warped_masks": final_warped_masks,
            "homographies": homographies,
            "canvas_size": output_size,
            "translation": translation,
            "error": None
        }
        
    except Exception as e:
        import traceback
        error_msg = f"Error selama re-warping: {e}\n{traceback.format_exc()}"
        print(error_msg)
        return {"error": error_msg}
    
def create_simple_preview(warped_images: list, warped_masks: list) -> np.ndarray:
    """
    Membuat gambar pratinjau panorama sederhana dengan merata-ratakan
    gambar-gambar yang tumpang tindih.

    Args:
        warped_images (list): Daftar gambar (np.ndarray) yang sudah di-warp
                              dan berukuran sama (kanvas panorama).
        warped_masks (list): Daftar mask biner yang sesuai dengan warped_images.

    Returns:
        np.ndarray: Gambar panorama pratinjau, atau None jika input kosong.
    """
    if not warped_images or not warped_masks:
        return None

    # Asumsikan semua gambar memiliki ukuran yang sama
    h, w = warped_images[0].shape[:2]
    
    # Siapkan kanvas untuk penjumlahan
    # Gunakan float32 untuk presisi saat menjumlah dan membagi
    panorama_sum = np.zeros((h, w, 3), dtype=np.float32)
    image_count_map = np.zeros((h, w), dtype=np.float32)
    
    for img, mask in zip(warped_images, warped_masks):
        # Pastikan gambar dalam format float untuk dijumlahkan
        # Jika gambar dalam format uint8, ubah ke float
        if img.dtype != np.float32:
            img = img.astype(np.float32)
            
        panorama_sum += img
        
        # Tambahkan mask ke peta hitungan
        # (Ubah mask menjadi float jika perlu)
        if mask.dtype != np.float32:
            image_count_map += mask.astype(np.float32)
        else:
            image_count_map += mask

    # Hindari pembagian dengan nol
    # Di mana pun image_count_map adalah 0, ubah menjadi 1
    # Ini berarti area hitam akan tetap hitam (0 / 1 = 0)
    image_count_map[image_count_map == 0] = 1.0
    
    # Lakukan pembagian elemen-demi-elemen untuk mendapatkan rata-rata
    # Gunakan broadcasting (..., np.newaxis) untuk membuat image_count_map menjadi 3D
    # agar cocok dengan dimensi panorama_sum.
    panorama_preview = (panorama_sum / image_count_map[..., np.newaxis]).astype(np.uint8)
    
    return panorama_preview