from concurrent.futures import ThreadPoolExecutor, as_completed
import ctypes
import gc
import os
import queue
import threading
import cv2
from joblib import Parallel, delayed
from cachetools import LRUCache
import numpy as np
from typing import Any, Callable, Dict, List, Optional
from scipy.linalg import expm, logm
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

from pixel_refine_desktop.core.algorithm.alignment.alignment_features.global_feature import estimate_noise_variance, get_adaptive_bilateral
from pixel_refine_desktop.ui.views.panorama.Algorithm.Blend import get_blender
from pixel_refine_desktop.ui.views.panorama.Algorithm.Blend.base_blender import BaseBlender
from pixel_refine_desktop.ui.views.panorama.Algorithm.Projection_and_Crop.image_warping import get_warper
from pixel_refine_desktop.ui.views.panorama.Algorithm.Projection_and_Crop.image_warping.base_warper import BaseWarper
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
        with ThreadPoolExecutor(max_workers=3) as executor:
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

def center_FOV(transformations: list, warp_method: str = "planar"):
    """
    Versi generik dan canggih untuk memusatkan transformasi.
    Dapat menangani baik homografi maupun matriks rotasi.
    
    Args:
        transformations (list): Daftar matriks 3x3 (homografi atau rotasi).
        warp_method (str): Tipe warp ("planar" atau lainnya) untuk menerapkan
                             normalisasi yang benar. Default ke "planar".
    """
    print(f"  > Menghitung transformasi terpusat untuk model '{warp_method}'...")
    
    log_transforms = []
    for T in transformations:
        T_processed = T.copy()
        
        # Lakukan normalisasi H[2,2] hanya untuk homografi planar
        if warp_method == "planar":
            if T_processed[2, 2] != 0:
                T_processed = T_processed / T_processed[2, 2]
        
        try:
            log_T = logm(T_processed)
            log_transforms.append(log_T)
        except Exception as e:
            print(f"    - Peringatan saat menghitung logm: {e}")
            continue
            
    if not log_transforms:
        print("Peringatan: Gagal menghitung pusat. Tidak ada koreksi.")
        return transformations

    avg_log_T = np.mean(log_transforms, axis=0)
    
    # Pastikan output selalu riil untuk mencegah bilangan kompleks
    T_avg = expm(avg_log_T).real
    
    try:
        T_correction = np.linalg.inv(T_avg)
    except np.linalg.LinAlgError:
        print("Peringatan: Gagal menginversi T_avg. Tidak ada koreksi.")
        return transformations

    # Pastikan hasil akhir juga riil
    centered_transforms = [(T_correction @ T).real for T in transformations]
    
    print("    - Transformasi berhasil dipusatkan.")
    return centered_transforms

# ==============================================================================
# WARPER
# ==============================================================================
def prewarp_to_cylindrical(image, focal_length):
    """
    Melakukan pra-warping pada sebuah gambar ke proyeksi silinder.
    Ini adalah langkah pertama dalam alur kerja hibrida.
    """
    h, w, _ = image.shape
    K = np.array([[focal_length, 0, w/2], [0, focal_length, h/2], [0, 0, 1]])

    # Buat kanvas tujuan (output) untuk gambar yang sudah di-warp
    cylinder_img = np.zeros_like(image)
    
    # Buat grid koordinat di kanvas tujuan
    y_out, x_out = np.indices((h, w))
    
    # Hitung koordinat sumber yang sesuai untuk setiap piksel tujuan
    # Ini adalah Backward Warping
    theta = (x_out - K[0, 2]) / K[0, 0] # Sudut
    h_in = (y_out - K[1, 2]) / K[1, 1] # Tinggi
    
    # Proyeksi balik ke bidang gambar 2D
    x_in = np.tan(theta)
    y_in = h_in * np.sqrt(1 + x_in**2)
    
    # Ubah kembali ke koordinat piksel
    map_x = (focal_length * x_in + K[0, 2]).astype(np.float32)
    map_y = (focal_length * y_in + K[1, 2]).astype(np.float32)

    # Lakukan remap untuk membuat gambar silinder
    warped_image = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    
    return warped_image

def prewarp_to_spherical(image, focal_length):
    """
    Melakukan pra-warping pada sebuah gambar ke proyeksi bola (equirectangular) sejati.
    """
    h, w, _ = image.shape
    
    # Buat grid koordinat di kanvas tujuan (output)
    y_out, x_out = np.indices((h, w))

    # Ubah koordinat piksel output menjadi sudut 3D (longitude dan latitude)
    lon = (x_out - w/2) / focal_length
    lat = (y_out - h/2) / focal_length

    # Proyeksi balik dari bola 3D ke bidang gambar 2D sumber
    # x_source = f * tan(lon)
    # y_source = f * tan(lat) / cos(lon)
    x_in = np.tan(lon)
    y_in = np.tan(lat) / np.cos(lon)

    # Ubah kembali ke koordinat piksel sumber
    map_x = (focal_length * x_in + w/2).astype(np.float32)
    map_y = (focal_length * y_in + h/2).astype(np.float32)

    # Lakukan remap
    return cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

# ==============================================================================
# WORKER PARALEL WARPING DAN BLENDING (GENERIC)
# ==============================================================================
def _render_single_tile(args: tuple) -> tuple:
    if len(args) == 5:
        task_info, warper, blender, save_as_uint8, save_as_float16 = args
    else:
        raise ValueError(f"_render_single_tile menerima 5 argumen, dapat {len(args)}")

    # langsung proses float16 jika diminta
    dtype_tile = np.float16 if save_as_float16 else np.float32

    warped_layers_float = []
    mask_layers = []

    for image_index in task_info["relevant_indices"]:
        img_uint8 = cv2.imread(warper.image_paths[image_index])
        if img_uint8 is None:
            continue
        img_float = img_uint8.astype(np.float32) / 255.0
        del img_uint8

        warped_tile, mask = warper.warp_and_mask_layer(img_float, task_info, image_index)
        del img_float

        warped_layers_float.append(warped_tile)
        mask_layers.append(mask)

    if not warped_layers_float:
        return (task_info["y_start"], task_info["x_start"], np.zeros(task_info["tile_shape"], dtype=dtype_tile))

    final_tile_float = blender.blend(warped_layers_float, mask_layers)
    del warped_layers_float, mask_layers

    final_tile_float = np.clip(final_tile_float, 0.0, 1.0)

    if save_as_uint8:
        final_tile = (final_tile_float * 255.0).round().astype(np.uint8)
    elif save_as_float16:
        final_tile = final_tile_float.astype(np.float16)
    else:
        final_tile = final_tile_float.astype(np.float32)

    return (task_info["y_start"], task_info["x_start"], final_tile)


def render_panorama_tiles(
    image_paths: list,
    image_shapes: list,
    warp_params: dict,
    output_shape: tuple,
    warp_method: str = "planar",
    blending_method: str = "multiband",
    progress_callback: callable = None,
    progress_range: tuple = (95, 99),
    save_as_uint8: bool = False,
    save_as_float16: bool = True,
    flush_every_n_tiles: int = 4,
    output_memmap: np.memmap = None,
    max_in_flight_tiles: int = 4
) -> np.memmap:

    try:
        warper = get_warper(name=warp_method, image_paths=image_paths, image_shapes=image_shapes, **warp_params)
        blender = get_blender(blending_method)
    except (ValueError, NotImplementedError) as e:
        print(f"ERROR: Gagal inisialisasi warper/blender: {e}")
        return None

    TILE_SIZE = (2048, 2048)
    dtype_out = np.uint8 if save_as_uint8 else (np.float16 if save_as_float16 else np.float32)

    # buat memmap
    if output_memmap is None:
        memmap_dir = os.path.join("database", "cache", "render_tiles")
        os.makedirs(memmap_dir, exist_ok=True)
        memmap_path = os.path.join(memmap_dir, "panorama_temp.mmap")
        if os.path.exists(memmap_path):
            os.remove(memmap_path)
        output_memmap = np.memmap(memmap_path, dtype=dtype_out, mode="w+", shape=output_shape)

    all_tasks_info = warper.build_task_list(output_shape, TILE_SIZE)
    total_tiles = len(all_tasks_info)
    if total_tiles == 0:
        return np.zeros(output_shape, dtype=dtype_out)

    all_tasks_args = [(task, warper, blender, save_as_uint8, save_as_float16) for task in all_tasks_info]

    # ------------------- Queue & Writer Thread -------------------
    tile_queue = queue.Queue(maxsize=max_in_flight_tiles)
    stop_writer = threading.Event()
    progress_counter = 0
    progress_lock = threading.Lock()

    def writer_thread_func():
        nonlocal progress_counter
        tile_buffer = []
        while not stop_writer.is_set() or not tile_queue.empty():
            try:
                item = tile_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if item is not None:
                tile_buffer.append(item)

            if len(tile_buffer) >= flush_every_n_tiles:
                for y_start, x_start, tile_float in tile_buffer:
                    y_end = y_start + tile_float.shape[0]
                    x_end = x_start + tile_float.shape[1]
                    output_memmap[y_start:y_end, x_start:x_end] = tile_float
                    del tile_float
                    if progress_callback:
                        with progress_lock:
                            progress_counter += 1
                            p_start, p_end = progress_range
                            progress = p_start + (progress_counter / total_tiles) * (p_end - p_start)
                            progress_callback(progress, f"Memproses Tile {progress_counter}/{total_tiles}")
                output_memmap.flush()
                tile_buffer.clear()

        # flush terakhir
        if tile_buffer:
            for y_start, x_start, tile_float in tile_buffer:
                y_end = y_start + tile_float.shape[0]
                x_end = x_start + tile_float.shape[1]
                output_memmap[y_start:y_end, x_start:x_end] = tile_float
                del tile_float
                if progress_callback:
                    with progress_lock:
                        progress_counter += 1
                        p_start, p_end = progress_range
                        progress = p_start + (progress_counter / total_tiles) * (p_end - p_start)
                        progress_callback(progress, f"Memproses Tile {progress_counter}/{total_tiles}")
            output_memmap.flush()
            tile_buffer.clear()

    writer_thread = threading.Thread(target=writer_thread_func, daemon=True)
    writer_thread.start()

    # ------------------- Worker Tiles Paralel dengan ThreadPool -------------------
    def worker_func(task_args):
        return _render_single_tile(task_args)  # kembalikan (y_start, x_start, tile_float)

    with ThreadPoolExecutor(max_workers=min(max_in_flight_tiles, os.cpu_count())) as executor:
        futures = [executor.submit(worker_func, args) for args in all_tasks_args]

        for future in as_completed(futures):
            y_start, x_start, tile_float = future.result()
            tile_queue.put((y_start, x_start, tile_float))  # kirim ke writer thread

    stop_writer.set()
    writer_thread.join()
    return output_memmap
