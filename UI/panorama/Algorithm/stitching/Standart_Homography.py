import cv2
import numpy as np
from scipy.optimize import least_squares
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
        def create_error_response(message):
            return {
                "stitched_image": None, "warped_images": None, "warped_masks": None,
                "homographies": None, "canvas_size": None, "translation": None, "error": message
            }

        if n_images < 2:
            return create_error_response("Butuh setidaknya 2 gambar.")
        
        self.progress_callback(0, "Membaca gambar...")
        try:
            images = stitching_utils.load_images(image_paths)
        except IOError as e:
            return create_error_response(str(e))

        # Tahap 1: Deteksi dan Pencocokan Fitur (Tidak ada perubahan)
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

        del all_des, all_kps # Membersihkan memori
        if not pairwise_matches:
            return create_error_response("Tidak bisa menemukan pencocokan berkualitas.")

        # Tahap 2: Komposisi Graf dan Optimasi (Bundle Adjustment)
        self.progress_callback(80, "Menyusun transformasi awal...")
        centrality_scores = [0] * n_images
        for match in pairwise_matches:
            centrality_scores[match['src_idx']] += match['confidence']
            centrality_scores[match['dst_idx']] += match['confidence']
        anchor_idx = np.argmax(centrality_scores)
        
        initial_homographies = stitching_utils.compose_transformations_from_graph(pairwise_matches, n_images, anchor_idx)
        if initial_homographies is None:
            return create_error_response("Gagal membuat grafik terhubung.")

        homographies = initial_homographies
        progress_start_warping = 85
        if use_bundle_adjustment:
            self.progress_callback(85, "Menyempurnakan transformasi (Bundle Adjustment)...")
            # Menggunakan kembali `all_kps` tidak efisien, jadi kita hapus saja di atas. BA perlu penyesuaian jika ingin digunakan.
            # Untuk sementara, mari asumsikan BA tidak membutuhkan all_kps, atau jika butuh, jangan dihapus.
            # homographies = self._bundle_adjust_homographies(initial_homographies, pairwise_matches, all_kps, n_images, anchor_idx)
            # ^ Jika baris di atas aktif, jangan 'del all_kps' sebelumnya.
            progress_start_warping = 90
        
        # --- KOREKSI DAN PEMBERSIHAN DIMULAI DI SINI ---

        # Tahap 3: Pemusatan Global (Meet-in-the-Middle)
        # Seluruh logika `logm`, `expm`, `H_correction` sekarang ada di dalam `center_FOV`.
        # Kita cukup memanggilnya. Ini membuat `stitch` jauh lebih bersih.
        self.progress_callback(progress_start_warping, "Menghitung transformasi terpusat...")
        final_homographies = stitching_utils.center_FOV(homographies)

        # Tahap 4: Hitung Kanvas Akhir & Translasi
        # Kode ini diperlukan untuk menentukan ukuran dan pergeseran panorama akhir.
        all_corners = []
        for i, H in enumerate(final_homographies):
            h, w = images[i].shape[:2]
            corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            warped = cv2.perspectiveTransform(corners, H)
            all_corners.append(warped)
            
        all_corners = np.concatenate(all_corners, axis=0)
        x_min, y_min = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        x_max, y_max = np.int32(all_corners.max(axis=0).ravel() + 0.5)
        
        # Translasi ini penting untuk menggeser panorama (yang mungkin punya koordinat negatif)
        # agar pas di dalam kanvas berukuran `output_size`.
        translation_offset = [-x_min, -y_min]
        output_size = (x_max - x_min, y_max - y_min)
        
        T_translate = np.array([[1, 0, translation_offset[0]], 
                                [0, 1, translation_offset[1]], 
                                [0, 0, 1]])

        # "Panggang" translasi ke dalam setiap homografi. Ini adalah transformasi final
        # yang akan digunakan untuk warping dan dikembalikan.
        homographies_to_warp_and_return = [T_translate @ H for H in final_homographies]
        
        # --- KOREKSI SELESAI ---

        # Tahap 5: Warping dan Blending
        progress_warp_step = (98 - progress_start_warping) / n_images
        panorama_sum = np.zeros((output_size[1], output_size[0], 3), dtype=np.float32)
        image_count_map = np.zeros((output_size[1], output_size[0]), dtype=np.float32)
        final_warped_images = []
        final_warped_masks = []
        
        # Loop menggunakan homografi yang sudah final (terpusat DAN tertranslasi)
        for idx, (img, H_final) in enumerate(zip(images, homographies_to_warp_and_return)):
            self.progress_callback(progress_start_warping + idx * progress_warp_step, f"Warping image {idx+1}...")
            
            # Karena translasi sudah dipanggang, argumen translasi di warp_image adalah [0,0]
            # Ini menyederhanakan panggilan fungsi warp.
            warped_img, mask = stitching_utils.warp_image(img, H_final, output_size, [0, 0])
            
            final_warped_images.append(warped_img)
            final_warped_masks.append(mask)
            panorama_sum += warped_img
            image_count_map += mask

        self.progress_callback(98, "Finalizing panorama...")
        image_count_map[image_count_map == 0] = 1.0 
        panorama_preview = (panorama_sum / image_count_map[..., np.newaxis]).astype(np.uint8)
        
        # Tahap 6: Return Hasil
        return {
            "stitched_image": panorama_preview,
            "warped_images": final_warped_images,
            "warped_masks": final_warped_masks,
            "homographies": homographies_to_warp_and_return, # Kembalikan homografi yang sudah "siap pakai"
            "canvas_size": output_size,
            "translation": [0, 0], # Translasi sudah menjadi bagian dari homografi
            "error": None
        }
def run_standart_homography(image_paths, settings, progress_callback, return_full_data=False):
    try:
        # Ekstrak konfigurasi
        feature_detector_name = settings.get('feature_detector', 'AKAZE')
        num_features = settings.get('num_features', 2000)
        enable_ba = settings.get('use_bundle_adjustment', True) 
        
        print(f"--- KONFIGURASI STITCHING ---")
        print(f"  > Algoritma Deteksi Fitur: {feature_detector_name.upper()}")
        print(f"  > Jumlah Fitur per Gambar: {num_features}")
        print(f"  > Bundle Adjustment: {'AKTIF' if enable_ba else 'NON-AKTIF'}")
        print(f"  > Mode Return: {'FULL' if return_full_data else 'MINIMAL'}")
        print(f"-----------------------------")

        stitcher = MultiRowStandartHomography(settings, progress_callback)
        
        # stitcher.stitch sekarang selalu mengembalikan data lengkap
        full_result = stitcher.stitch(
            image_paths=image_paths,
            feature_algorithm=feature_detector_name,
            num_features=num_features, 
            use_bundle_adjustment=enable_ba
        )

        if full_result.get("error"):
            return full_result

        if return_full_data:
            return full_result
        else:
            minimal_cache_data = {
                "stitched_image":full_result ["stitched_image"],
                "homographies": full_result["homographies"],
                "canvas_size": full_result["canvas_size"],
                "translation": full_result["translation"],
                "error": None
            }
            return minimal_cache_data
        
    except Exception as e:
        import traceback
        print(f"FATAL ERROR in stitching: {e}")
        traceback.print_exc()
        # Menggunakan struktur error yang sama untuk konsistensi
        return {
            "stitched_image": None, "warped_images": None, "warped_masks": None,
            "homographies": None, "canvas_size": None, "translation": None, 
            "error": f"Fatal error: {e}"
        }