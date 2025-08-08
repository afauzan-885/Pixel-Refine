from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import cv2
import numpy as np
from typing import List, Union, Tuple, Any
from cv2 import KeyPoint
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

def detect_features(img, feature_algorithm, use_multicore=True, num_features=500):
    """
    Mendeteksi fitur pada satu gambar dengan strategi per-blok yang canggih dan pra-pemrosesan adaptif.
    """
    if img is None: return [], None
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img.astype(np.uint8)
    
    # 1. Pra-pemrosesan dengan CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_gray_img = clahe.apply(gray_img)
    
    # 2. Pra-pemrosesan dengan Bilateral Filter jika noise tinggi
    noise_level = estimate_noise_variance(enhanced_gray_img)
    if noise_level > 600.0:
        d, sigma, _ = get_adaptive_bilateral(noise_level, 300, 800, 5, 9, 20, 75)
        print(f"Noise tinggi ({noise_level:.2f}), menerapkan Bilateral Filter (d={d}, sigma={sigma})...")
        enhanced_gray_img = cv2.bilateralFilter(enhanced_gray_img, d, sigma, sigma)

    h, w = enhanced_gray_img.shape
    num_blocks, overlap, max_kps_per_block = (3, 3), 30, 600

    # 3. Inisialisasi Detektor
    algo = feature_algorithm.upper()
    if algo == "SIFT": detector = cv2.SIFT_create(nfeatures=max_kps_per_block)
    elif algo == "ORB": detector = cv2.ORB_create(nfeatures=max_kps_per_block)
    elif algo == "BRISK": detector = cv2.BRISK_create()
    else: detector = cv2.AKAZE_create(descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB)

    def process_block(i, j):
        roi_x, roi_y = i * (w // num_blocks[0]), j * (h // num_blocks[1])
        roi_w, roi_h = w // num_blocks[0], h // num_blocks[1]
        x_start, y_start = max(0, roi_x - overlap), max(0, roi_y - overlap)
        x_end, y_end = min(w, roi_x + roi_w + overlap), min(h, roi_y + roi_h + overlap)
        block_gray = enhanced_gray_img[y_start:y_end, x_start:x_end]
        kps, des = detector.detectAndCompute(block_gray, None)
        if kps is None or len(kps) == 0: return [], None
        
        # Seleksi Top-K per-blok
        if len(kps) > max_kps_per_block:
            indices = np.argsort([-kp.response for kp in kps])[:max_kps_per_block]
            kps = [kps[i] for i in indices]
            if des is not None: des = des[indices]

        for kp in kps: kp.pt = (kp.pt[0] + x_start, kp.pt[1] + y_start)
        return kps, des
    
    keypoints, descriptor_list = [], []
    if use_multicore:
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
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

