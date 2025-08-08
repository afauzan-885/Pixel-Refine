from scipy.optimize import least_squares
import cv2
import numpy as np
from UI.panorama.Algorithm.stitching import stitching_utils


class MultiRowStandartHomography:
    def __init__(self, settings, progress_callback):
        self.settings = settings
        self.progress_callback = progress_callback

    def estimate_homography(self, kp1, kp2, matches):
        """Mengestimasi homografi dan mengembalikan mask inlier."""
        if len(matches) < 4: return None, None
        pts1 = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        pts2 = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        H, mask = cv2.findHomography(pts2, pts1, cv2.USAC_MAGSAC, 5.0)
        return H, mask

    def _bundle_adjust_homographies(self, initial_homographies, all_pairwise_matches, all_kps, n_images, anchor_idx):
        """Menyempurnakan semua homografi secara global."""
        def pack_params(homographies):
            params = []
            for i, H in enumerate(homographies):
                if i == anchor_idx: continue
                params.extend(H.flatten())
            return np.array(params)

        def unpack_params(params):
            homographies = [None] * n_images
            homographies[anchor_idx] = np.eye(3)
            param_idx = 0
            for i in range(n_images):
                if i == anchor_idx: continue
                homographies[i] = params[param_idx : param_idx + 9].reshape((3, 3))
                param_idx += 9
            return homographies

        def objective_function(params):
            homographies = unpack_params(params)
            residuals = []
            for match_info in all_pairwise_matches:
                src_idx, dst_idx = match_info['src_idx'], match_info['dst_idx']
                H_src, H_dst = homographies[src_idx], homographies[dst_idx]
                if H_src is None or H_dst is None: continue
                
                matches = match_info['matches']
                if not matches: continue

                kp1, kp2 = all_kps[src_idx], all_kps[dst_idx]
                pts1 = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                pts2 = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                
                weight = np.sqrt(match_info.get('confidence', 1))
                try: H_rel = np.linalg.inv(H_dst) @ H_src
                except np.linalg.LinAlgError: continue
                
                pts1_reproj = cv2.perspectiveTransform(pts1, H_rel)
                if pts1_reproj is None: continue

                error = (pts2 - pts1_reproj).flatten()
                residuals.extend(error * weight)
            return np.array(residuals)

        print("Memulai Bundle Adjustment untuk penyempurnaan global...")
        initial_params = pack_params(initial_homographies)
        res = least_squares(objective_function, initial_params, loss='huber', verbose=1, ftol=1e-4)
        print("Bundle Adjustment selesai.")
        return unpack_params(res.x)

    def stitch(self, image_paths, feature_algorithm, num_features=2000, use_bundle_adjustment=True):
        n_images = len(image_paths)
        if n_images < 2: return {"stitched_image": None, "error": "Butuh setidaknya 2 gambar."}
        
        self.progress_callback(0, "Membaca gambar...")
        try:
            images = stitching_utils.load_images(image_paths)
        except IOError as e:
            return {"stitched_image": None, "error": str(e)}

        self.progress_callback(5, "Mendeteksi fitur...")
        all_kps, all_des = [None] * n_images, [None] * n_images
        for i in range(n_images):
            self.progress_callback(5 + i * (40 / n_images), f"Mendeteksi fitur di gambar {i+1}...")
            all_kps[i], all_des[i] = stitching_utils.detect_features(
                images[i], feature_algorithm, num_features=num_features
            )
        
        self.progress_callback(45, "Mencocokkan fitur...")
        pairwise_matches = []
        for i in range(n_images):
            for j in range(i + 1, n_images):
                matches = stitching_utils.match_features(all_des[i], all_des[j])
                if len(matches) < 20: continue
                
                H, mask = self.estimate_homography(all_kps[i], all_kps[j], matches)
                if H is None: continue
                
                confidence = np.sum(mask)
                if confidence < 20: continue
                
                inlier_matches = [m for k, m in enumerate(matches) if mask[k] == 1]
                if not inlier_matches: continue

                pairwise_matches.append({
                    "src_idx": i, "dst_idx": j, "T": H, "confidence": confidence, "matches": inlier_matches
                })

        del all_des # Hemat memori

        if not pairwise_matches: return {"stitched_image": None, "error": "Tidak bisa menemukan pencocokan berkualitas."}

        self.progress_callback(80, "Menyusun transformasi awal...")
        centrality_scores = [0] * n_images
        for match in pairwise_matches:
            centrality_scores[match['src_idx']] += match['confidence']
            centrality_scores[match['dst_idx']] += match['confidence']
        anchor_idx = np.argmax(centrality_scores)
        
        initial_homographies = stitching_utils.compose_transformations_from_graph(pairwise_matches, n_images, anchor_idx)
        if initial_homographies is None: return {"stitched_image": None, "error": "Gagal membuat grafik terhubung."}

        if use_bundle_adjustment:
            homographies = self._bundle_adjust_homographies(initial_homographies, pairwise_matches, all_kps, n_images, anchor_idx)
            progress_start_warping = 90
        else:
            homographies = initial_homographies
            progress_start_warping = 85
        
        self.progress_callback(progress_start_warping, "Menghitung kanvas akhir...")
        
        all_corners = []
        for i, H in enumerate(homographies):
            h, w = images[i].shape[:2]
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

        progress_warp_step = (98 - progress_start_warping) / n_images
        
        for idx, (img, H) in enumerate(zip(images, homographies)):
            self.progress_callback(progress_start_warping + idx * progress_warp_step, f"Warping image {idx+1}...")
            
            warped_img, mask = stitching_utils.warp_image(img, H, output_size, translation)
            panorama_sum += warped_img
            image_count_map += mask

        self.progress_callback(98, "Finalizing panorama...")
        image_count_map[image_count_map == 0] = 1.0 
        panorama = (panorama_sum / image_count_map[..., np.newaxis]).astype(np.uint8)
        
        return {"stitched_image": panorama}
    
def run_standart_homography(image_paths, settings, progress_callback):
    """
    Menjalankan workflow stitching standar dengan konfigurasi dari 'settings'.
    """
    try:
        # Ekstrak konfigurasi
        feature_detector_name = settings.get('feature_detector', 'AKAZE')
        # --- PERUBAHAN DI SINI: Gunakan 'num_features' sebagai nama setting ---
        num_features = settings.get('num_features', 2000)
        enable_ba = settings.get('use_bundle_adjustment', True) 
        
        print(f"--- KONFIGURASI STITCHING ---")
        print(f"  > Algoritma Deteksi Fitur: {feature_detector_name.upper()}")
        print(f"  > Jumlah Fitur per Gambar: {num_features}")
        print(f"  > Bundle Adjustment: {'AKTIF' if enable_ba else 'NON-AKTIF'}")
        print(f"-----------------------------")

        stitcher = MultiRowStandartHomography(settings, progress_callback)
        
        # Teruskan parameter ke fungsi stitch
        result = stitcher.stitch(
            image_paths=image_paths,
            feature_algorithm=feature_detector_name,
            # --- PERUBAHAN DI SINI: Teruskan `num_features` ---
            num_features=num_features, 
            use_bundle_adjustment=enable_ba
        )
        
        return result
        
    except Exception as e:
        import traceback
        print(f"FATAL ERROR in stitching: {e}")
        traceback.print_exc()
        return {"stitched_image": None, "error": str(e)}