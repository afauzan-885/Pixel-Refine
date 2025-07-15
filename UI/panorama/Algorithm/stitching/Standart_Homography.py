import concurrent
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.sparse import csr_matrix
import os
import cv2
import numpy as np

from UI.panorama.Algorithm.stitching import stitching_utils

class MultiRowPlanarStitcher:
    def __init__(self, settings, progress_callback):
        self.settings = settings
        self.progress_callback = progress_callback

    def _warp_and_merge_image(self, panorama, img, H, translation, output_size):
        """
        Melakukan warp pada satu gambar dan menggabungkannya ke dalam kanvas panorama.

        Args:
            panorama (np.array): Kanvas panorama saat ini.
            img (np.array): Gambar yang akan di-warp.
            H (np.array): Matriks homografi untuk gambar ini.
            translation (list): Vektor translasi [tx, ty] untuk memastikan semua koordinat positif.
            output_size (tuple): Ukuran (lebar, tinggi) dari kanvas output.

        Returns:
            np.array: Kanvas panorama yang telah diperbarui.
        """
        # Gabungkan matriks homografi dengan matriks translasi
        H_translated = np.array([
            [1, 0, translation[0]],
            [0, 1, translation[1]],
            [0, 0, 1]
        ]) @ H

        # Lakukan warp perspektif pada gambar
        warped = cv2.warpPerspective(img, H_translated, output_size)

        # Buat mask untuk menempatkan gambar yang di-warp ke kanvas.
        # Hanya piksel yang tidak hitam (bukan bagian dari padding setelah warp) yang disalin.
        mask = (warped > 0)
        panorama[mask] = warped[mask]

        return panorama

    def _find_pairwise_matches(self, images, feature_algorithm='AKAZE'): # Tambahkan parameter di sini
        n_images = len(images)
        pairwise_matches = []
        for i in range(n_images):
            for j in range(i + 1, n_images):
                self.progress_callback(5 + (i * n_images + j) * (45 / (n_images*n_images)), f"Matching image {i+1} and {j+1}...")
                
                # Teruskan pilihan algoritma ke fungsi detect_and_match_features
                kp1, kp2, matches = self.detect_and_match_features(images[i], images[j], feature_algorithm=feature_algorithm)

                if len(matches) < 20:
                    continue

                H = self.estimate_homography(kp1, kp2, matches)
                if H is None:
                    continue

                confidence = len(matches)
                pairwise_matches.append({'src_idx': i, 'dst_idx': j, 'H': H, 'confidence': confidence})

        return pairwise_matches
    
    def _compose_homographies_from_graph(self, pairwise_matches, n_images, anchor_idx):
        """
        Membangun graf, menemukan MST, dan mengkomposisikan homografi ke anchor.
        """
        if not pairwise_matches:
            return None

        # Buat matriks kepercayaan (semakin tinggi confidence, semakin kecil 'jarak')
        # Kita menggunakan nilai negatif karena MST mencari bobot minimum.
        rows = [m['src_idx'] for m in pairwise_matches]
        cols = [m['dst_idx'] for m in pairwise_matches]
        weights = [-m['confidence'] for m in pairwise_matches]
        
        graph = csr_matrix((weights, (rows, cols)), shape=(n_images, n_images))
        
        # Temukan Pohon Rentang Minimum (yang sebenarnya maksimum karena bobot negatif)
        mst = minimum_spanning_tree(graph)
        mst_graph = mst.toarray()

        # Buat kamus homografi untuk akses mudah
        homography_map = {}
        for match in pairwise_matches:
            homography_map[(match['src_idx'], match['dst_idx'])] = match['H']
            # Juga simpan inversnya
            H_inv = np.linalg.inv(match['H'])
            homography_map[(match['dst_idx'], match['src_idx'])] = H_inv

        # Lakukan traversal (BFS/DFS) dari anchor untuk menghitung homografi final
        final_homographies = [None] * n_images
        final_homographies[anchor_idx] = np.eye(3) # Homografi anchor adalah identitas
        
        q = [anchor_idx]
        visited = {anchor_idx}

        while q:
            current_idx = q.pop(0)
            
            # Cari tetangga di MST
            neighbors = np.where(mst_graph[current_idx] != 0)[0]
            inv_neighbors = np.where(mst_graph[:, current_idx] != 0)[0]
            all_neighbors = set(list(neighbors) + list(inv_neighbors))

            for neighbor_idx in all_neighbors:
                if neighbor_idx not in visited:
                    visited.add(neighbor_idx)
                    # Temukan homografi yang menghubungkan current ke neighbor
                    H_to_neighbor = homography_map.get((current_idx, neighbor_idx))
                    if H_to_neighbor is not None:
                         # H_neighbor = H_current @ H_current_to_neighbor
                        final_homographies[neighbor_idx] = final_homographies[current_idx] @ H_to_neighbor
                        q.append(neighbor_idx)
                    else:
                        print(f"Warning: Missing homography for edge ({current_idx}, {neighbor_idx}) in MST")


        # Pastikan semua gambar terhubung
        if any(h is None for h in final_homographies):
            return None # Gagal menghubungkan semua gambar

        return final_homographies
    
    def detect_and_match_features(self, img1, img2, feature_algorithm='AKAZE', use_multicore=True):
        """
        Mendeteksi, mencocokkan, dan menyaring fitur menggunakan berbagai algoritma.
        Fungsi ini sekarang agnostik terhadap algoritma dan bertindak sebagai pengontrol.

        Args:
            img1 (np.array): Gambar pertama.
            img2 (np.array): Gambar kedua.
            feature_algorithm (str): Algoritma yang akan digunakan. Pilihan: 'AKAZE', 'SIFT', 'ORB'.
            use_multicore (bool): Apakah akan menggunakan pemrosesan paralel untuk blok.

        Returns:
            Tuple[List, List, List]: final_kp1, final_kp2, final_matches
        """
        # --- 1. Persiapan Gambar ---
        # Bagian ini tetap sama: konversi ke grayscale dan tingkatkan kontras.
        def prepare_gray(img):
            if img.ndim == 3:
                return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return img.astype(np.uint8)

        base_gray = prepare_gray(img1)
        target_gray = prepare_gray(img2)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_base_gray = clahe.apply(base_gray)
        enhanced_target_gray = clahe.apply(target_gray)

        h, w = base_gray.shape
        
        # Konfigurasi umum
        num_blocks = (4, 3) # Grid 4x3 untuk deteksi
        overlap = 30 # overlap dalam piksel
        min_matches_for_transform = 10
        ratio_thresh = 0.75

        # --- 2. Inisialisasi Detektor dan Matcher berdasarkan Algoritma ---
        # Kita membuat objek 'detector' dan 'matcher' yang sesuai berdasarkan input string.
        print(f"Menggunakan algoritma fitur: {feature_algorithm}")
        if feature_algorithm.upper() == 'SIFT':
            # SIFT adalah detektor berbasis float, cocok dengan FlannBasedMatcher
            detector = cv2.SIFT_create()
            matcher = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
        
        elif feature_algorithm.upper() == 'ORB':
            # ORB adalah detektor biner, HARUS menggunakan BFMatcher dengan NORM_HAMMING
            detector = cv2.ORB_create(nfeatures=2000)
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

        else: # Default ke AKAZE, yang juga berbasis float
            if feature_algorithm.upper() != 'AKAZE':
                print(f"Peringatan: '{feature_algorithm}' tidak dikenali. Menggunakan AKAZE sebagai default.")
            detector = cv2.AKAZE_create(descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB)
            matcher = cv2.FlannBasedMatcher(dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1), dict(checks=50))
        
        # --- 3. Deteksi Fitur Paralel Berbasis Blok ---
        # Bagian ini sekarang memanggil fungsi generik dari stitching_utils
        keypoints_base_all, descriptors_base_list = [], []
        keypoints_target_all, descriptors_target_list = [], []
        
        blocks_x, blocks_y = num_blocks
        block_w = max(1, w // blocks_x)
        block_h = max(1, h // blocks_y)

        def process_block(i, j):
            return stitching_utils.compute_features_for_block(
                detector=detector, 
                enhanced_gray_base=enhanced_base_gray,
                enhanced_gray_target=enhanced_target_gray,
                block_coords=(i * block_w, j * block_h, w - (i*block_w) if i == blocks_x - 1 else block_w, h - (j*block_h) if j == blocks_y - 1 else block_h),
                img_dims=(w, h),
                overlap_px=overlap
            )

        # Logika eksekusi paralel tetap sama
        if use_multicore:
            with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
                futures = [executor.submit(process_block, i, j) for i in range(blocks_x) for j in range(blocks_y)]
                for future in as_completed(futures):
                    kpb, db, kpt, dt = future.result()
                    if db is not None and db.size > 0: keypoints_base_all.extend(kpb); descriptors_base_list.append(db)
                    if dt is not None and dt.size > 0: keypoints_target_all.extend(kpt); descriptors_target_list.append(dt)
        else:
            for i in range(blocks_x):
                for j in range(blocks_y):
                    kpb, db, kpt, dt = process_block(i, j)
                    if db is not None and db.size > 0: keypoints_base_all.extend(kpb); descriptors_base_list.append(db)
                    if dt is not None and dt.size > 0: keypoints_target_all.extend(kpt); descriptors_target_list.append(dt)

        if not descriptors_base_list or not descriptors_target_list:
            return [], [], []

        descriptors_base_all = np.vstack(descriptors_base_list)
        descriptors_target_all = np.vstack(descriptors_target_list)

        # --- 4. Pencocokan Fitur (Matching) ---
        # Menggunakan 'matcher' yang sudah kita inisialisasi sebelumnya
        matches = matcher.knnMatch(descriptors_base_all, descriptors_target_all, k=2)
        
        # Filtering dengan Lowe's Ratio Test
        good_matches = []
        if matches:
            for m_n in matches:
                # Pastikan ada 2 match (k=2) sebelum di-unpack
                if len(m_n) == 2:
                    m, n = m_n
                    if m.distance < ratio_thresh * n.distance:
                        good_matches.append(m)

        if len(good_matches) < min_matches_for_transform:
            return [], [], []
        
        good_matches = sorted(good_matches, key=lambda m: m.distance)

        # --- 5. Menyesuaikan Format Output ---
        # Bagian ini tidak berubah
        final_kp1, final_kp2, final_matches = [], [], []
        kp1_map, kp2_map = {}, {}

        for m in good_matches:
            if m.queryIdx not in kp1_map:
                kp1_map[m.queryIdx] = len(final_kp1)
                final_kp1.append(keypoints_base_all[m.queryIdx])
            
            if m.trainIdx not in kp2_map:
                kp2_map[m.trainIdx] = len(final_kp2)
                final_kp2.append(keypoints_target_all[m.trainIdx])

            final_matches.append(cv2.DMatch(
                _queryIdx=kp1_map[m.queryIdx],
                _trainIdx=kp2_map[m.trainIdx],
                _distance=m.distance
            ))
            
        return final_kp1, final_kp2, final_matches
    
    def estimate_homography(self, kp1, kp2, matches):
        # Tidak perlu ada perubahan di sini
        pts1 = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
        pts2 = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
        H, _ = cv2.findHomography(pts2, pts1, cv2.USAC_MAGSAC, 4.0)
        return H

    def stitch(self, image_paths, feature_algorithm='AKAZE'):
        n_images = len(image_paths)
        if n_images < 2:
            return {"stitched_image": None, "error": "Butuh setidaknya 2 gambar."}

        self.progress_callback(0, "Membaca metadata gambar...")
        temp_images_for_matching = stitching_utils.load_images(image_paths)
        if isinstance(temp_images_for_matching, str):
            return {"stitched_image": None, "error": temp_images_for_matching}
        
        self.progress_callback(5, "Finding pairwise matches...")
        # Gunakan gambar yang dimuat sementara untuk pencocokan fitur
        pairwise_matches = self._find_pairwise_matches(temp_images_for_matching, feature_algorithm=feature_algorithm)
        # Setelah selesai, kita bisa melepaskan memori ini
        del temp_images_for_matching

        if not pairwise_matches:
            return {"stitched_image": None, "error": "Could not find enough confident matches..."}

        self.progress_callback(50, "Building connection graph and composing transformations...")
        anchor_idx = n_images // 2
        homographies = self._compose_homographies_from_graph(pairwise_matches, n_images, anchor_idx)
        
        if homographies is None:
            return {"stitched_image": None, "error": "Failed to create a connected graph..."}

        self.progress_callback(70, "Warping and merging images...")
        
        # Hitung batas kanvas (ini membutuhkan dimensi gambar, jadi kita muat satu per satu)
        all_corners = []
        for path, H in zip(image_paths, homographies):
            # Muat dimensi gambar sesuai kebutuhan
            img_shape = cv2.imread(path).shape
            h, w = img_shape[:2]
            corners = np.float32([[0,0], [0,h], [w,h], [w,0]]).reshape(-1,1,2)
            warped = cv2.perspectiveTransform(corners, H)
            all_corners.append(warped)

        all_corners = np.concatenate(all_corners, axis=0)
        [x_min, y_min] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(all_corners.max(axis=0).ravel() + 0.5)

        translation = [-x_min, -y_min]
        output_size = (x_max - x_min, y_max - y_min)
        
        # Masalah kanvas besar masih ada di sini
        panorama = np.zeros((output_size[1], output_size[0], 3), dtype=np.uint8)

        # <<< LOOPING DENGAN LAZY LOADING >>>
        for idx, (path, H) in enumerate(zip(image_paths, homographies)):
            self.progress_callback(70 + idx * (25 // n_images), f"Warping and merging image {idx+1}...")
            
            # Muat gambar dari disk HANYA saat dibutuhkan
            img = cv2.imread(path)
            if img is None:
                print(f"Peringatan: Gagal memuat ulang gambar {path}, dilewati.")
                continue
                
            # Gunakan fungsi warp yang sudah ada
            panorama = self._warp_and_merge_image(panorama, img, H, translation, output_size)
            # 'img' akan dilepaskan dari memori di iterasi berikutnya

        self.progress_callback(98, "Finalizing panorama...")
        return {"stitched_image": panorama}
    
def run_standart_homography(image_paths, settings, progress_callback):
    try:
        stitcher = MultiRowPlanarStitcher(settings, progress_callback)
        result = stitcher.stitch(image_paths)
        return result
    except Exception as e:
        import traceback
        print(f"FATAL ERROR in stitching: {e}")
        traceback.print_exc()
        return {"stitched_image": None, "error": str(e)}