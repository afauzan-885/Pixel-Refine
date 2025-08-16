from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import threading
import cv2
from joblib import Parallel, delayed
import numpy as np
from typing import Any, Callable, Dict, List, Optional
from scipy.linalg import expm, logm
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import estimate_noise_variance, get_adaptive_bilateral
from UI.panorama.Algorithm.Blend import get_blender
from UI.panorama.Algorithm.Blend.base_blender import BaseBlender
from UI.panorama.Algorithm.Projection_and_Crop.image_warping import get_warper
from UI.panorama.Algorithm.Projection_and_Crop.image_warping.base_warper import BaseWarper
"""
Skrip ini berisi fungsi-fungsi utilitas statis untuk pemrosesan gambar,
dirancang untuk dapat digunakan kembali di berbagai bagian aplikasi.
"""

# ==============================================================================
# 1. IO DAN PRA-PEMROSESAN
# ==============================================================================
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

# ==============================================================================
# 2. DETEKSI DAN PENCOCOKAN FITUR
# ==============================================================================
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
    
    noise_level = estimate_noise_variance(enhanced_gray_img)
    if noise_level > 600.0:
        d, sigma, _ = get_adaptive_bilateral(noise_level, 300, 800, 5, 9, 20, 75)
        print(f"Noise tinggi ({noise_level:.2f}), menerapkan Bilateral Filter (d={d}, sigma={sigma})...")
        enhanced_gray_img = cv2.bilateralFilter(enhanced_gray_img, d, sigma, sigma)

    h, w = enhanced_gray_img.shape
    # Kita bisa membuat max_kps_per_block lebih dinamis, tapi untuk sekarang ini sudah cukup.
    num_blocks, overlap, max_kps_per_block = (3, 3), 30, 600


    def process_block(i, j):
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
# 3. KOMPOSISI TRANSFORMASI DAN GEOMETRI
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

# ==============================================================================
# WORKER PARALEL WARPING DAN BLENDING (GENERIC)
# ==============================================================================
def _render_single_tile(args: tuple) -> tuple:
    """
    Worker paralel yang sepenuhnya generik dan bertugas memproses satu ubin.

    Fungsi ini tidak memiliki pengetahuan spesifik tentang metode warping atau blending.
    Ia hanya bertindak sebagai orkestrator yang mengikuti instruksi dari objek
    'warper' dan 'blender' yang diterimanya.

    Args:
        args (tuple): Sebuah tuple berisi (task_info, warper_instance, blender_instance).
                      - task_info (dict): Informasi spesifik untuk ubin ini (misal, koordinat, gambar relevan).
                      - warper_instance (BaseWarper): Objek yang tahu cara melakukan warping.
                      - blender_instance (BaseBlender): Objek yang tahu cara melakukan blending.

    Returns:
        tuple: Berisi (y_start, x_start, final_tile_float) untuk ubin yang telah diproses.
    """
    task_info: Dict[str, Any]
    warper: BaseWarper
    blender: BaseBlender
    task_info, warper, blender = args
    
    warped_layers_float = []
    mask_layers = []

    # 1. Loop melalui gambar-gambar yang sudah ditentukan relevan oleh warper
    for image_index in task_info['relevant_indices']:
        image_path = warper.image_paths[image_index]
        
        img_uint8 = cv2.imread(image_path)
        if img_uint8 is None:
            print(f"Peringatan: Gagal membaca gambar di worker: {image_path}")
            continue
        
        img_float = img_uint8.astype(np.float32) / 255.0

        # 2. Minta objek 'warper' untuk melakukan pekerjaan warping & masking
        warped_tile, mask = warper.warp_and_mask_layer(img_float, task_info, image_index)
        
        warped_layers_float.append(warped_tile)
        mask_layers.append(mask)

    # Jika tidak ada layer yang berhasil di-warp untuk ubin ini
    if not warped_layers_float:
        return (task_info['y_start'], task_info['x_start'], np.zeros(task_info['tile_shape'], dtype=np.float32))

    # 3. Minta objek 'blender' untuk melakukan pekerjaan blending
    #    Worker ini tidak perlu tahu apakah ini multiband, feather, dll.
    final_tile_float = blender.blend(warped_layers_float, mask_layers)
    
    # 4. Pastikan output berada dalam rentang yang valid sebelum dikembalikan
    final_tile_float = np.clip(final_tile_float, 0.0, 1.0)
    
    return (task_info['y_start'], task_info['x_start'], final_tile_float)


# ==============================================================================
# FUNGSI ORKESTRATOR UTAMA
# ==============================================================================
def render_panorama_tiles(
    image_paths: List[str], 
    image_shapes: List[tuple], 
    warp_params: Dict[str, Any],
    output_shape: tuple, 
    warp_method: str = "planar",
    blending_method: str = "multiband",
    progress_callback: Optional[Callable] = None, 
    progress_range: tuple = (95, 99)
) -> Optional[np.ndarray]:
    """
    Fungsi rendering panorama berbasis ubin yang sepenuhnya generik dan modular.

    Fungsi ini bertindak sebagai "otak" utama:
    1. Membuat instance 'warper' dan 'blender' yang sesuai berdasarkan nama.
    2. Meminta 'warper' untuk merencanakan semua pekerjaan (pra-komputasi relevansi ubin).
    3. Menyiapkan dan menjalankan pemrosesan paralel.
    4. Menyusun hasil dari para worker menjadi gambar panorama akhir.

    Args:
        image_paths: Daftar path ke gambar sumber.
        image_shapes: Daftar shape (H, W, C) dari setiap gambar sumber.
        warp_params: Dictionary berisi parameter yang spesifik untuk metode warp
                     (misalnya: {"homographies": [...]}).
        output_shape: Shape dari kanvas panorama akhir (H, W, C).
        warp_method: Nama metode warp yang akan digunakan (misal, "planar").
        blending_method: Nama metode blend yang akan digunakan (misal, "multiband").
        progress_callback: Fungsi callback untuk melaporkan progres.
        progress_range: Rentang progres (min, max) yang akan digunakan callback.

    Returns:
        np.ndarray: Gambar panorama akhir sebagai array float32 [0, 1], atau None jika gagal.
    """
    print(f"\n--- Memulai Rendering Panorama ---")
    print(f"Metode Warp: '{warp_method}', Metode Blend: '{blending_method}'")
    
    # Langkah 1: Buat instance spesialis yang dibutuhkan menggunakan factory
    try:
        warper = get_warper(
            name=warp_method, 
            image_paths=image_paths, 
            image_shapes=image_shapes,
            **warp_params  # Teruskan parameter spesifik seperti homographies
        )
        blender = get_blender(blending_method)
    except (ValueError, NotImplementedError) as e:
        print(f"ERROR: Gagal menginisialisasi warper atau blender: {e}")
        return None

    temp_pano_path = ""
    panorama_full_float = None
    try:
        if progress_callback:
            progress_callback(progress_range[0], f"Mempersiapkan rendering dengan {warp_method}/{blending_method}...")

        TILE_SIZE = (1024, 1024)
        
        # Setup temporary memory-mapped file untuk output
        cache_dir = os.path.join("database", "cache", "render_tiles")
        os.makedirs(cache_dir, exist_ok=True)
        temp_pano_path = os.path.join(cache_dir, "panorama_temp.mmap")
        if os.path.exists(temp_pano_path):
            os.remove(temp_pano_path)
        panorama_full_float = np.memmap(temp_pano_path, dtype=np.float32, mode='w+', shape=output_shape)
        
        # Langkah 2: Minta 'warper' untuk merencanakan semua pekerjaan (tahap pra-komputasi)
        print("Merencanakan tugas rendering untuk setiap ubin...")
        all_tasks_info = warper.build_task_list(output_shape, TILE_SIZE)
        
        total_tiles = len(all_tasks_info)
        if total_tiles == 0:
            print("Peringatan: Tidak ada ubin yang perlu diproses berdasarkan analisis warper.")
            return np.zeros(output_shape, dtype=np.float32)
        
        print(f"Ditemukan {total_tiles} ubin yang relevan untuk diproses.")
        if progress_callback:
            progress_callback(progress_range[0] + 1, f"Memulai pemrosesan {total_tiles} ubin...")

        # Langkah 3: Siapkan argumen lengkap untuk setiap worker paralel
        all_tasks_args = [(task_info, warper, blender) for task_info in all_tasks_info]

        # Langkah 4: Jalankan eksekusi paralel
        progress_counter = 0
        progress_lock = threading.Lock()

        def process_and_update_progress(task_args):
            nonlocal progress_counter
            result = _render_single_tile(task_args)
            if progress_callback:
                with progress_lock:
                    progress_counter += 1
                    p_start, p_end = progress_range
                    progress = p_start + (progress_counter / total_tiles) * (p_end - p_start)
                    progress_callback(progress, f"Memproses ubin... ({progress_counter}/{total_tiles})")
            return result

        results = Parallel(n_jobs=-1, backend="threading")(
            delayed(process_and_update_progress)(args) for args in all_tasks_args
        )

        # Langkah 5: Susun hasil dari para worker menjadi gambar akhir
        if progress_callback:
            progress_callback(progress_range[1], "Menyusun ubin menjadi gambar akhir...")
            
        for y_start, x_start, final_tile_float in results:
            if final_tile_float is not None:
                y_end = y_start + final_tile_float.shape[0]
                x_end = x_start + final_tile_float.shape[1]
                panorama_full_float[y_start:y_end, x_start:x_end] = final_tile_float

        # Konversi hasil dari memmap ke array numpy di memori
        final_image_in_memory = np.array(panorama_full_float)
        
        return final_image_in_memory
    
    finally:
        # Pastikan file temporary selalu dibersihkan
        if panorama_full_float is not None:
            # Menutup file memmap
            if hasattr(panorama_full_float, '_mmap'):
                panorama_full_float._mmap.close()
            del panorama_full_float
        
        if os.path.exists(temp_pano_path):
            try:
                os.remove(temp_pano_path)
                print(f"File temporary '{temp_pano_path}' berhasil dihapus.")
            except OSError as e:
                print(f"Peringatan: Gagal menghapus file temporary: {e}")