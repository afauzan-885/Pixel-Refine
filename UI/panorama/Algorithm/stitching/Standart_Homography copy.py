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

    # <<< MODIFIKASI: Tambahkan parameter num_anms_points >>>
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

                # <<< MODIFIKASI: Teruskan parameter ANMS >>>
                kp1, kp2, matches = self.detect_and_match_features(
                    images[i],
                    images[j],
                    feature_algorithm=feature_algorithm,
                    num_anms_points=num_anms_points,  # Teruskan parameter
                )

                if len(matches) < 20:
                    continue

                H = self.estimate_homography(kp1, kp2, matches)
                if H is None:
                    continue

                confidence = len(matches)
                pairwise_matches.append(
                    {"src_idx": i, "dst_idx": j, "H": H, "confidence": confidence}
                )

        return pairwise_matches

    def _compose_homographies_from_graph(self, pairwise_matches, n_images, anchor_idx):
        # ... (Tidak ada perubahan di fungsi ini)
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

    # <<< MODIFIKASI: Tambahkan parameter num_anms_points >>>
    def detect_and_match_features(
        self,
        img1,
        img2,
        feature_algorithm="AKAZE",
        use_multicore=True,
        num_anms_points=1000,
    ):
        # ... (Langkah 1 & 2: Persiapan dan inisialisasi, tidak ada perubahan) ...
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
        num_blocks = (4, 3)
        overlap = 30
        min_matches_for_transform = 10
        ratio_thresh = 0.75

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

        # --- 3. Deteksi Fitur Paralel Berbasis Blok ---
        # ... (Tidak ada perubahan pada logika deteksi blok) ...
        keypoints_base_all, descriptors_base_list = [], []
        keypoints_target_all, descriptors_target_list = [], []
        blocks_x, blocks_y = num_blocks
        block_w = max(1, w // blocks_x)
        block_h = max(1, h // blocks_y)

        # Anda perlu memastikan fungsi stitching_utils.compute_features_for_block ada
        def process_block(i, j):
            return stitching_utils.compute_features_for_block(
                detector=detector,
                enhanced_gray_base=enhanced_base_gray,
                enhanced_gray_target=enhanced_target_gray,
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

            # <<< MODIFIKASI: Teruskan parameter `use_multicore` >>>
            # Panggilan ini sekarang akan menjalankan ANMS secara paralel
            keypoints_base_all, best_indices_base = stitching_utils.apply_anms(
                keypoints_base_all, num_anms_points, use_multicore=use_multicore
            )
            descriptors_base_all = descriptors_base_all[best_indices_base, :]

            keypoints_target_all, best_indices_target = stitching_utils.apply_anms(
                keypoints_target_all, num_anms_points, use_multicore=use_multicore
            )
            descriptors_target_all = descriptors_target_all[best_indices_target, :]
        # ... (Sisa fungsi tetap sama) ...
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
        # ... (Tidak ada perubahan di fungsi ini)
        pts1 = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        pts2 = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        H, _ = cv2.findHomography(pts2, pts1, cv2.USAC_MAGSAC, 4.0)
        return H

    # <<< MODIFIKASI: Tambahkan parameter num_anms_points ke stitch() >>>
    def stitch(self, image_paths, feature_algorithm="AKAZE", num_anms_points=1000):
        n_images = len(image_paths)
        if n_images < 2:
            return {"stitched_image": None, "error": "Butuh setidaknya 2 gambar."}

        self.progress_callback(0, "Membaca metadata gambar...")
        temp_images_for_matching = stitching_utils.load_images(image_paths)
        if isinstance(temp_images_for_matching, str):
            return {"stitched_image": None, "error": temp_images_for_matching}

        self.progress_callback(5, "Finding pairwise matches...")
        # <<< MODIFIKASI: Teruskan parameter ANMS >>>
        pairwise_matches = self._find_pairwise_matches(
            temp_images_for_matching,
            feature_algorithm=feature_algorithm,
            num_anms_points=num_anms_points,
        )
        del temp_images_for_matching

        if not pairwise_matches:
            return {
                "stitched_image": None,
                "error": "Could not find enough confident matches...",
            }

        # ... (Sisa fungsi stitch tidak perlu diubah) ...
        self.progress_callback(
            50, "Building connection graph and composing transformations..."
        )
        anchor_idx = n_images // 2
        homographies = self._compose_homographies_from_graph(
            pairwise_matches, n_images, anchor_idx
        )

        if homographies is None:
            return {
                "stitched_image": None,
                "error": "Failed to create a connected graph...",
            }

        self.progress_callback(70, "Calculating final canvas size...")
        all_corners = []
        for path, H in zip(image_paths, homographies):
            img_shape = cv2.imread(path).shape
            h, w = img_shape[:2]
            corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            warped = cv2.perspectiveTransform(corners, H)
            all_corners.append(warped)

        all_corners = np.concatenate(all_corners, axis=0)
        [x_min, y_min] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(all_corners.max(axis=0).ravel() + 0.5)

        translation = [-x_min, -y_min]
        output_size = (x_max - x_min, y_max - y_min)

        panorama_sum = np.zeros((output_size[1], output_size[0], 3), dtype=np.float32)
        image_count_map = np.zeros((output_size[1], output_size[0]), dtype=np.float32)

        self.progress_callback(75, "Warping and overlaying images...")
        for idx, (path, H) in enumerate(zip(image_paths, homographies)):
            self.progress_callback(
                75 + idx * (20 / n_images), f"Warping and overlaying image {idx+1}..."
            )

            img = cv2.imread(path)
            if img is None:
                print(f"Peringatan: Gagal memuat ulang gambar {path}, dilewati.")
                continue

            panorama_sum, image_count_map = self._warp_and_overlay_image(
                panorama_sum, image_count_map, img, H, translation, output_size
            )

        self.progress_callback(98, "Finalizing panorama by averaging...")
        image_count_map = image_count_map[..., np.newaxis]
        image_count_map[image_count_map == 0] = 1.0
        panorama = (panorama_sum / image_count_map).astype(np.uint8)

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
