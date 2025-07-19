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

    # <<< MODIFIKASI BARU: Fungsi helper untuk menggambar dan menyimpan match yang bersih >>>
    def _draw_and_save_clean_matches(self, img1, img2, kp1, kp2, matches, mask, filename):
        """
        Menggambar hanya inlier matches (keypoint bersih) dan menyimpannya ke file.
        """
        if mask is not None:
            # Mask dari findHomography perlu diratakan untuk drawMatches
            matches_mask = mask.ravel().tolist()
        else:
            matches_mask = None

        # Gambar match dengan warna hijau untuk inliers
        match_img = cv2.drawMatches(
            img1, kp1, img2, kp2, matches, None,
            matchColor=(0, 255, 0),  # Warna hijau untuk match yang baik
            singlePointColor=None,
            matchesMask=matches_mask,
            flags=2
        )
        
        cv2.imwrite(filename, match_img)
        print(f"Menyimpan visualisasi keypoint bersih ke: {filename}")

    def _calculate_local_homography_for_cell(self, cell_center, kp1, kp2, matches, gamma=100):
        """
        Menghitung homografi lokal untuk satu sel berdasarkan matches terdekat.
        Ini adalah inti dari metode Moving DLT (Direct Linear Transform).
        """
        pts1 = np.float32([kp1[m.queryIdx].pt for m in matches])
        pts2 = np.float32([kp2[m.trainIdx].pt for m in matches])
        
        weights = np.exp(-np.linalg.norm(pts2 - cell_center, axis=1) / gamma)
        
        # Selesaikan sistem linear terbobot untuk homografi (Weighted DLT)
        # Kita perlu membangun matriks A untuk sistem Ax=0
        num_matches = len(matches)
        A = np.zeros((2 * num_matches, 9))
        
        for i in range(num_matches):
            x, y = pts2[i]
            u, v = pts1[i]
            w = weights[i]
            
            A[2*i]   = [-x*w, -y*w, -w, 0, 0, 0, u*x*w, u*y*w, u*w]
            A[2*i+1] = [0, 0, 0, -x*w, -y*w, -w, v*x*w, v*y*w, v*w]
            
        # Selesaikan menggunakan SVD
        _, _, Vt = np.linalg.svd(A)
        H_local = Vt[-1].reshape(3, 3)
        H_local /= H_local[2, 2] # Normalisasi
        return H_local
    
    def _warp_image_in_grids_simple(self, img, H, translation, output_size, grid_size=(10, 10)):
        """
        Melakukan warp pada gambar dengan membaginya menjadi grid dan me-warp setiap
        sel secara individual menggunakan homografi global yang sama.
        Ini adalah untuk visualisasi dan debugging.
        """
        src_h, src_w = img.shape[:2]
        grid_x, grid_y = grid_size
        cell_w = src_w // grid_x
        cell_h = src_h // grid_y

        # Buat kanvas tujuan untuk gambar ini saja
        warped_canvas = np.zeros((output_size[1], output_size[0], 3), dtype=np.uint8)
        
        # Matriks translasi untuk kanvas global
        H_translation = np.array([[1, 0, translation[0]], [0, 1, translation[1]], [0, 0, 1]])
        
        # Loop untuk setiap sel dalam grid
        for i in range(grid_x):
            for j in range(grid_y):
                # 1. Tentukan 4 sudut dari sel sumber (persegi)
                src_corners = np.float32([
                    [i * cell_w, j * cell_h],
                    [(i + 1) * cell_w, j * cell_h],
                    [(i + 1) * cell_w, (j + 1) * cell_h],
                    [i * cell_w, (j + 1) * cell_h]
                ])

                # Ambil potongan (tile) dari gambar sumber
                tile = img[j * cell_h:(j + 1) * cell_h, i * cell_w:(i + 1) * cell_w]
                if tile.size == 0:
                    continue

                # 2. Transformasikan 4 sudut tersebut menggunakan Homografi GLOBAL
                #    Ini akan menghasilkan segiempat (quadrilateral)
                warped_corners = cv2.perspectiveTransform(src_corners.reshape(-1, 1, 2), H)
                
                # 3. Tambahkan translasi global
                dst_corners = cv2.perspectiveTransform(warped_corners, H_translation)

                # 4. Buat matriks transformasi khusus untuk tile ini
                #    yang memetakan dari persegi asli tile ke segiempat tujuan
                tile_transform = cv2.getPerspectiveTransform(src_corners, dst_corners.reshape(4, 2))
                
                # 5. Warp tile ini ke kanvas tujuan
                cv2.warpPerspective(
                    img,  # Warp dari gambar asli (bukan tile) untuk menghindari artifak tepi
                    tile_transform,
                    output_size,
                    dst=warped_canvas,
                    borderMode=cv2.BORDER_TRANSPARENT, # Tulis di atas kanvas yang ada
                    flags=cv2.INTER_LINEAR
                )

        return warped_canvas
    
    def _draw_grid_on_image(self, image, color=(0, 0, 255), grid_size=50):
        """Menggambar grid 10x10 pada salinan gambar."""
        img_with_grid = image.copy()
        h, w, _ = img_with_grid.shape
        step_x = w // grid_size
        step_y = h // grid_size
        thickness = max(1, int(min(w, h) / 500))

        for i in range(1, grid_size):
            cv2.line(img_with_grid, (i * step_x, 0), (i * step_x, h), color, thickness)
            cv2.line(img_with_grid, (0, i * step_y), (w, i * step_y), color, thickness)
        return img_with_grid
    
    def _warp_and_overlay_image(
        self, panorama_sum, image_count_map, img, H, translation, output_size
    ):
        """
        Melakukan warp pada gambar dan mengakumulasikannya untuk blending rata-rata (overlay).
        """
        H_translated = (
            np.array([[1, 0, translation[0]], [0, 1, translation[1]], [0, 0, 1]]) @ H
        )
        warped_img = cv2.warpPerspective(
            img,
            H_translated,
            output_size,
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
        )
        panorama_sum += warped_img.astype(np.float32)
        mask = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY) > 0
        image_count_map[mask] += 1
        return panorama_sum, image_count_map

    def _find_pairwise_matches(
        self, images, feature_algorithm="AKAZE", num_anms_points=1000
    ):
        n_images = len(images)
        pairwise_matches = []
        for i in range(n_images):
            for j in range(i + 1, n_images):
                self.progress_callback(
                    5 + (i * n_images + j) * (45 / (n_images * n_images)),
                    f"Matching image {i+1} and {j+1}...",
                )

                kp1, kp2, matches = self.detect_and_match_features(
                    images[i],
                    images[j],
                    feature_algorithm=feature_algorithm,
                    num_anms_points=num_anms_points,
                )

                if len(matches) < 20:
                    continue

                # <<< MODIFIKASI: Tangkap mask inlier dari estimate_homography >>>
                H, inlier_mask = self.estimate_homography(kp1, kp2, matches)
                if H is None:
                    continue

                # <<< MODIFIKASI BARU: Panggil fungsi untuk menyimpan visualisasi match >>>
                self._draw_and_save_clean_matches(
                    images[i], images[j], kp1, kp2, matches, inlier_mask, 
                    f"debug/clean_matches_{i}_vs_{j}.png"
                )

                confidence = len(matches)
                pairwise_matches.append(
                    {"src_idx": i, "dst_idx": j, "H": H, "confidence": confidence}
                )

        return pairwise_matches

    def _compose_homographies_from_graph(self, pairwise_matches, n_images, anchor_idx):
        if not pairwise_matches:
            return None

        rows = [m["src_idx"] for m in pairwise_matches]
        cols = [m["dst_idx"] for m in pairwise_matches]
        weights = [-m["confidence"] for m in pairwise_matches]

        graph = csr_matrix((weights, (rows, cols)), shape=(n_images, n_images))
        mst = minimum_spanning_tree(graph)
        mst_graph = mst.toarray()

        homography_map = {}
        for match in pairwise_matches:
            homography_map[(match["src_idx"], match["dst_idx"])] = match["H"]
            H_inv = np.linalg.inv(match["H"])
            homography_map[(match["dst_idx"], match["src_idx"])] = H_inv

        final_homographies = [None] * n_images
        final_homographies[anchor_idx] = np.eye(3)

        q = [anchor_idx]
        visited = {anchor_idx}

        while q:
            current_idx = q.pop(0)

            neighbors = np.where(mst_graph[current_idx] != 0)[0]
            inv_neighbors = np.where(mst_graph[:, current_idx] != 0)[0]
            all_neighbors = set(list(neighbors) + list(inv_neighbors))

            for neighbor_idx in all_neighbors:
                if neighbor_idx not in visited:
                    visited.add(neighbor_idx)
                    H_to_neighbor = homography_map.get((current_idx, neighbor_idx))
                    if H_to_neighbor is not None:
                        final_homographies[neighbor_idx] = (
                            final_homographies[current_idx] @ H_to_neighbor
                        )
                        q.append(neighbor_idx)
                    else:
                        print(
                            f"Warning: Missing homography for edge ({current_idx}, {neighbor_idx}) in MST"
                        )

        if any(h is None for h in final_homographies):
            return None

        return final_homographies

    def detect_and_match_features(
        self,
        img1,
        img2,
        feature_algorithm="AKAZE",
        use_multicore=True,
        num_anms_points=5000,
    ):
        def prepare_gray(img):
            if img.ndim == 3:
                return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return img.astype(np.uint8)

        base_gray = prepare_gray(img1)
        target_gray = prepare_gray(img2)
        h, w = base_gray.shape
        num_blocks = (4, 3)
        overlap = 30
        min_matches_for_transform = 10
        ratio_thresh = 0.70

        print(f"Menggunakan algoritma fitur: {feature_algorithm}")
        if feature_algorithm.upper() == "SIFT":
            detector = cv2.SIFT_create()
            matcher = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
        elif feature_algorithm.upper() == "ORB":
            detector = cv2.ORB_create(nfeatures=2000)
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        else:
            if feature_algorithm.upper() != "AKAZE":
                print(
                    f"Peringatan: '{feature_algorithm}' tidak dikenali. Menggunakan AKAZE."
                )
            detector = cv2.AKAZE_create(descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB)
            matcher = cv2.FlannBasedMatcher(
                dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1),
                dict(checks=50),
            )

        keypoints_base_all, descriptors_base_list = [], []
        keypoints_target_all, descriptors_target_list = [], []
        blocks_x, blocks_y = num_blocks
        block_w = max(1, w // blocks_x)
        block_h = max(1, h // blocks_y)

        def process_block(i, j):
            return stitching_utils.compute_features_for_block(
                detector=detector,
                enhanced_gray_base=base_gray,
                enhanced_gray_target=target_gray,
                block_coords=(
                    i * block_w,
                    j * block_h,
                    w - (i * block_w) if i == blocks_x - 1 else block_w,
                    h - (j * block_h) if j == blocks_y - 1 else block_h,
                ),
                img_dims=(w, h),
                overlap_px=overlap,
            )

        if use_multicore:
            with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
                futures = [
                    executor.submit(process_block, i, j)
                    for i in range(blocks_x)
                    for j in range(blocks_y)
                ]
                for future in as_completed(futures):
                    kpb, db, kpt, dt = future.result()
                    if db is not None and db.size > 0:
                        keypoints_base_all.extend(kpb)
                        descriptors_base_list.append(db)
                    if dt is not None and dt.size > 0:
                        keypoints_target_all.extend(kpt)
                        descriptors_target_list.append(dt)
        else:
            for i in range(blocks_x):
                for j in range(blocks_y):
                    kpb, db, kpt, dt = process_block(i, j)
                    if db is not None and db.size > 0:
                        keypoints_base_all.extend(kpb)
                        descriptors_base_list.append(db)
                    if dt is not None and dt.size > 0:
                        keypoints_target_all.extend(kpt)
                        descriptors_target_list.append(dt)

        if not descriptors_base_list or not descriptors_target_list:
            return [], [], []

        descriptors_base_all = np.vstack(descriptors_base_list)
        descriptors_target_all = np.vstack(descriptors_target_list)

        if num_anms_points > 0 and len(keypoints_base_all) > num_anms_points:
            print(
                f"Menerapkan ANMS paralel untuk mempertahankan {num_anms_points} keypoints terbaik..."
            )

            keypoints_base_all, best_indices_base = stitching_utils.apply_anms(
                keypoints_base_all, num_anms_points, use_multicore=use_multicore
            )
            descriptors_base_all = descriptors_base_all[best_indices_base, :]

            keypoints_target_all, best_indices_target = stitching_utils.apply_anms(
                keypoints_target_all, num_anms_points, use_multicore=use_multicore
            )
            descriptors_target_all = descriptors_target_all[best_indices_target, :]
        
        matches = matcher.knnMatch(descriptors_base_all, descriptors_target_all, k=2)
        good_matches = [
            m
            for m_n in matches
            if len(m_n) == 2 and (m := m_n[0]).distance < ratio_thresh * m_n[1].distance
        ]
        if len(good_matches) < min_matches_for_transform:
            return [], [], []

        final_kp1, final_kp2, final_matches = [], [], []
        kp1_map, kp2_map = {}, {}
        for m in good_matches:
            if m.queryIdx not in kp1_map:
                kp1_map[m.queryIdx] = len(final_kp1)
                final_kp1.append(keypoints_base_all[m.queryIdx])
            if m.trainIdx not in kp2_map:
                kp2_map[m.trainIdx] = len(final_kp2)
                final_kp2.append(keypoints_target_all[m.trainIdx])
            final_matches.append(
                cv2.DMatch(
                    _queryIdx=kp1_map[m.queryIdx],
                    _trainIdx=kp2_map[m.trainIdx],
                    _distance=m.distance,
                )
            )

        return final_kp1, final_kp2, final_matches

    
    def estimate_homography(self, kp1, kp2, matches):
        pts1 = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        pts2 = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        H, mask = cv2.findHomography(pts2, pts1, cv2.USAC_MAGSAC, 5.0)
        return H, mask # Kembalikan H dan mask

    def _warp_image_apap(self, img, all_matches_data, homographies, img_idx,
                         translation, output_size, grid_size=(10, 10)):
        """
        Melakukan warp pada gambar menggunakan homografi lokal per-vertex
        dan interpolasi bilinear untuk hasil yang mulus (gaya APAP).
        """
        src_h, src_w = img.shape[:2]
        grid_x, grid_y = grid_size
        
        # Buat mesh (kumpulan vertex)
        vertices_x = np.linspace(0, src_w, grid_x + 1)
        vertices_y = np.linspace(0, src_h, grid_y + 1)
        
        # 1. Hitung homografi lokal untuk setiap VERTEX di mesh
        local_homographies = {}
        for i, vx in enumerate(vertices_x):
            for j, vy in enumerate(vertices_y):
                # Temukan match yang relevan untuk gambar ini
                # Untuk penyederhanaan, kita gunakan homografi global sebagai "panduan"
                # atau rata-rata dari semua match. Implementasi yang lebih baik
                # akan menggunakan match antar pasangan gambar yang relevan.
                # Di sini, kita akan gunakan homografi global saja sebagai basis.
                # Untuk implementasi APAP sejati, kita perlu match asli (kp1, kp2, matches).
                # Karena struktur kode saat ini tidak langsung menyediakan match per warp,
                # kita akan tetap menggunakan homografi global tapi pada mesh,
                # ini adalah langkah menengah yang baik.
                
                # Langkah menengah: Daripada menghitung ulang H lokal, kita gunakan H global.
                # Ini akan mendemonstrasikan proses meshing dan remap.
                # Untuk APAP sejati, baris di bawah ini akan diganti dengan
                # _calculate_local_homography_for_cell.
                local_homographies[(i, j)] = homographies[img_idx]

        # 2. Buat peta dari koordinat sumber ke tujuan (mapping)
        # Buat grid koordinat di gambar SUMBER
        src_coords_x, src_coords_y = np.meshgrid(np.arange(src_w), np.arange(src_h))
        src_coords = np.stack([src_coords_x.ravel(), src_coords_y.ravel(), np.ones(src_w * src_h)]).T

        # Siapkan array tujuan
        dst_coords = np.zeros((src_h * src_w, 2), dtype=np.float32)

        # Matriks translasi untuk kanvas global
        H_translation = np.array([[1, 0, translation[0]], [0, 1, translation[1]], [0, 0, 1]])

        # 3. Loop untuk setiap piksel sumber dan hitung posisi tujuannya
        for p_idx, p_src in enumerate(src_coords):
            x, y, _ = p_src
            
            # Temukan di sel grid mana piksel ini berada
            i = np.searchsorted(vertices_x, x) - 1
            j = np.searchsorted(vertices_y, y) - 1
            i = max(0, i)
            j = max(0, j)

            # Hitung bobot interpolasi bilinear
            vx0, vx1 = vertices_x[i], vertices_x[i+1]
            vy0, vy1 = vertices_y[j], vertices_y[j+1]
            
            alpha = (x - vx0) / (vx1 - vx0)
            beta = (y - vy0) / (vy1 - vy0)

            # Dapatkan 4 homografi lokal dari sudut-sudut sel
            H00 = local_homographies[(i, j)]
            H10 = local_homographies[(i + 1, j)]
            H01 = local_homographies[(i, j + 1)]
            H11 = local_homographies[(i + 1, j + 1)]
            
            # Terapkan 4 homografi ke piksel sumber
            p_dst_00 = H00 @ p_src
            p_dst_10 = H10 @ p_src
            p_dst_01 = H01 @ p_src
            p_dst_11 = H11 @ p_src

            # Normalisasi
            p_dst_00 /= p_dst_00[2]
            p_dst_10 /= p_dst_10[2]
            p_dst_01 /= p_dst_01[2]
            p_dst_11 /= p_dst_11[2]
            
            # Lakukan interpolasi bilinear pada KOORDINAT TUJUAN
            p_dst_top = (1 - alpha) * p_dst_00 + alpha * p_dst_10
            p_dst_bottom = (1 - alpha) * p_dst_01 + alpha * p_dst_11
            p_dst = (1 - beta) * p_dst_top + beta * p_dst_bottom
            
            # Tambahkan translasi global
            p_final = H_translation @ p_dst
            p_final /= p_final[2]

            dst_coords[p_idx] = p_final[:2]
            
        # 4. Gunakan cv2.remap untuk melakukan warping non-linear
        map_x = dst_coords[:, 0].reshape(src_h, src_w)
        map_y = dst_coords[:, 1].reshape(src_h, src_w)
        
        warped_img = cv2.remap(
            img, map_x, map_y, 
            interpolation=cv2.INTER_LINEAR, 
            borderMode=cv2.BORDER_CONSTANT, 
            borderValue=(0,0,0)
        )

        # Untuk blending, kita perlu mask
        final_canvas = np.zeros((output_size[1], output_size[0], 3), dtype=np.uint8)
        mask = np.ones((src_h, src_w), dtype=np.uint8) * 255
        warped_mask = cv2.remap(
            mask, map_x, map_y, 
            interpolation=cv2.INTER_NEAREST, 
            borderMode=cv2.BORDER_CONSTANT, 
            borderValue=0
        )
        
        # Tempelkan gambar yang sudah di-warp ke kanvas final
        # Ini adalah cara sederhana, blending yang lebih baik akan memerlukan alpha blending
        # di perbatasan.
        final_canvas[warped_mask > 0] = warped_img[warped_mask > 0]

        return final_canvas
    
    def stitch(self, image_paths, feature_algorithm="AKAZE", num_anms_points=1000):
        os.makedirs("debug", exist_ok=True)
        
        n_images = len(image_paths)
        if n_images < 2: return {"stitched_image": None, "error": "Butuh setidaknya 2 gambar."}

        try:
            images_to_stitch = stitching_utils.load_images(image_paths)
            if isinstance(images_to_stitch, str): return {"stitched_image": None, "error": images_to_stitch}
        except Exception as e:
             return {"stitched_image": None, "error": f"Gagal memuat gambar: {e}"}

        pairwise_matches = self._find_pairwise_matches(images_to_stitch, feature_algorithm=feature_algorithm, num_anms_points=num_anms_points)
        if not pairwise_matches: return {"stitched_image": None, "error": "Could not find enough confident matches..."}

        centrality_scores = [0] * n_images
        for match in pairwise_matches:
            centrality_scores[match['src_idx']] += match['confidence']
            centrality_scores[match['dst_idx']] += match['confidence']
        anchor_idx = np.argmax(centrality_scores)
        homographies = self._compose_homographies_from_graph(pairwise_matches, n_images, anchor_idx)
        if homographies is None: return {"stitched_image": None, "error": "Failed to create a connected graph..."}

        all_corners = []
        for img, H in zip(images_to_stitch, homographies):
            h, w = img.shape[:2]
            corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            warped = cv2.perspectiveTransform(corners, H)
            all_corners.append(warped)

        all_corners = np.concatenate(all_corners, axis=0)
        [x_min, y_min] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(all_corners.max(axis=0).ravel() + 0.5)
        translation = [-x_min, -y_min]
        output_size = (x_max - x_min, y_max - y_min)


        # --- PEMBUATAN PANORAMA UTAMA (BLENDING RATA-RATA) ---
        panorama_sum = np.zeros((output_size[1], output_size[0], 3), dtype=np.float32)
        image_count_map = np.zeros((output_size[1], output_size[0]), dtype=np.float32)

        # Kanvas untuk debug APAP
        debug_apap_canvas = np.zeros((output_size[1], output_size[0], 3), dtype=np.uint8)

        self.progress_callback(75, "Warping and overlaying images...")
        for idx, (img, H) in enumerate(zip(images_to_stitch, homographies)):
            self.progress_callback(
                75 + idx * (20 / n_images), f"Warping image {idx+1}..."
            )
            
            # Metode 1: Blending rata-rata (cepat dan stabil)
            panorama_sum, image_count_map = self._warp_and_overlay_image(
                panorama_sum, image_count_map, img, H, translation, output_size
            )

            # Metode 2: Warping gaya APAP (lambat, untuk debug kualitas)
            # Catatan: Kita meneruskan 'homographies' dan 'idx' sebagai pengganti data match asli
            # untuk implementasi menengah ini.
            print(f"Memulai warp gaya APAP untuk gambar {idx+1}. Ini mungkin lambat...")
            warped_apap_img = self._warp_image_apap(
                img, None, homographies, idx, translation, output_size
            )
            mask = cv2.cvtColor(warped_apap_img, cv2.COLOR_BGR2GRAY) > 0
            debug_apap_canvas[mask] = warped_apap_img[mask]


        self.progress_callback(98, "Finalizing panorama and saving debug files...")
        
        image_count_map[image_count_map == 0] = 1.0
        panorama_final = (panorama_sum / image_count_map[..., np.newaxis]).astype(np.uint8)

        debug_filename = "debug/panorama_apap_style_preview.png"
        cv2.imwrite(debug_filename, debug_apap_canvas)
        print(f"Hasil debug warp gaya APAP disimpan di: {debug_filename}")

        return {"stitched_image": panorama_final}

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