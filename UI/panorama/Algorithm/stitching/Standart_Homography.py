import cv2
import numpy as np
from scipy.optimize import least_squares
from scipy.linalg import logm, expm
from UI.panorama.Algorithm import panorama_utils

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
    
    def center_transformations(self, transformations: list, warp_method: str):
        """
        Versi generik dari center_FOV yang sekarang secara eksplisit memastikan
        outputnya adalah matriks riil untuk mencegah bilangan kompleks.
        """
        print(f"  > Menghitung transformasi terpusat untuk model '{warp_method}'...")
        
        log_transforms = []
        for T in transformations:
            T_processed = T.copy()
            
            if warp_method == "planar":
                if T_processed[2, 2] != 0:
                    T_processed = T_processed / T_processed[2, 2]
            
            try:
                log_T = logm(T_processed)
                log_transforms.append(log_T)
            except Exception as e:
                # Peringatan RuntimeWarning dari logm tidak fatal, jadi kita bisa lanjutkan
                print(f"    - Peringatan saat menghitung logm: {e}")
                continue
                
        if not log_transforms:
            print("Peringatan: Gagal menghitung pusat. Tidak ada koreksi.")
            return transformations

        avg_log_T = np.mean(log_transforms, axis=0)
        T_avg = expm(avg_log_T)
        
        try:
            T_correction = np.linalg.inv(T_avg)
        except np.linalg.LinAlgError:
            print("Peringatan: Gagal menginversi T_avg. Tidak ada koreksi.")
            return transformations

        # ==============================================================================
        # ### PERBAIKAN KUNCI DI SINI ###
        # ==============================================================================
        # Pastikan SETIAP matriks di hasil akhir adalah riil.
        # Ini membersihkan kontaminasi kompleks dari seluruh rantai perhitungan.
        centered_transforms = [(T_correction @ T).real for T in transformations]
        
        print("    - Transformasi berhasil dipusatkan.")
        return centered_transforms

    def stitch(self, image_paths, feature_algorithm, num_features=2000, 
            blending_method: str = "multiband", warp_method: str="mercator"):
        n_images = len(image_paths)

        def create_error_response(message):
            return {
                "stitched_image": None, "warped_images": None, "warped_masks": None,
                "homographies": None, "canvas_size": None, "translation": None, "error": message
            }

        if n_images < 2:
            return create_error_response("Butuh setidaknya 2 gambar.")

        # ==================== Tahap 1: Deteksi Fitur ====================
        self.progress_callback(5, "Menginisialisasi detektor fitur...")
        
        algo = feature_algorithm.upper()
        max_kps_per_block = 600 
        if algo == "SIFT":
            detector = cv2.SIFT_create(nfeatures=max_kps_per_block)
        elif algo == "ORB":
            detector = cv2.ORB_create(nfeatures=max_kps_per_block)
        elif algo == "BRISK":
            detector = cv2.BRISK_create()
        else:
            detector = cv2.AKAZE_create(descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB)

        self.progress_callback(6, "Mendeteksi fitur...")
        all_kps, all_des, image_shapes = [None] * n_images, [None] * n_images, [None] * n_images
        for i, path in enumerate(image_paths):
            self.progress_callback(6 + i * (39 / n_images), f"Mendeteksi fitur di gambar {i+1}...")
            img_to_process = cv2.imread(path)
            if img_to_process is None:
                return create_error_response(f"Gagal membaca gambar: {path}")
            image_shapes[i] = img_to_process.shape
            all_kps[i], all_des[i] = panorama_utils.detect_features(img_to_process, detector, num_features)

        # ==================== Tahap 2: Pencocokan Fitur (Langkah Umum) ====================
        self.progress_callback(45, "Mencocokkan fitur antar gambar...")
        pairwise_matches = []
        for i in range(n_images):
            for j in range(i + 1, n_images):
                matches = panorama_utils.match_features(all_des[i], all_des[j])
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
        if not pairwise_matches:
            return create_error_response("Tidak bisa menemukan pencocokan berkualitas.")

        # Inisialisasi variabel hasil
        warp_params = {}
        output_size = (0, 0)
        homographies_final = [np.eye(3)] * n_images
        translation_offset = [0, 0]

        # ==================== Tahap 3 & 4: Estimasi Transformasi (Dinamis) ====================
        if warp_method == "planar":
            self.progress_callback(80, "Menyusun transformasi planar...")
            
            centrality_scores = [0] * n_images
            for match in pairwise_matches:
                centrality_scores[match['src_idx']] += match['confidence']
                centrality_scores[match['dst_idx']] += match['confidence']
            anchor_idx = np.argmax(centrality_scores)
            
            homographies = panorama_utils.compose_transformations_from_graph(pairwise_matches, n_images, anchor_idx)
            if homographies is None:
                return create_error_response("Gagal membuat grafik terhubung.")
            
            self.progress_callback(85, "Menghitung transformasi terpusat...")
            centered_homographies = self.center_transformations(homographies, warp_method="planar")

            self.progress_callback(88, "Menghitung kanvas akhir...")
            all_corners = []
            for i, H in enumerate(centered_homographies):
                h, w, _ = image_shapes[i]
                corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
                all_corners.append(cv2.perspectiveTransform(corners, H))
            all_corners = np.concatenate(all_corners, axis=0)
            x_min, y_min = np.int32(all_corners.min(axis=0).ravel())
            x_max, y_max = np.int32(all_corners.max(axis=0).ravel())

            translation_offset = [-x_min, -y_min]
            output_size = (x_max - x_min, y_max - y_min)
            T_translate = np.array([[1, 0, translation_offset[0]], [0, 1, translation_offset[1]], [0, 0, 1]])
            homographies_final = [T_translate @ H for H in centered_homographies]
            
            warp_params = {"homographies": homographies_final}

        elif warp_method in ["cylindrical", "mercator"]:
            # --- BLOK BARU DENGAN ESTIMASI DAN PERHITUNGAN KANVAS YANG DIPERBAIKI ---
            self.progress_callback(45, f"Mengestimasi transformasi untuk model {warp_method.capitalize()}...")
            
            # ==============================================================================
            # ### PERBAIKAN: Tambahkan kembali pemuatan gambar ###
            # ==============================================================================
            # OpenCV Stitcher membutuhkan daftar gambar mentah, bukan hanya fitur.
            images_for_estimator = []
            for path in image_paths:
                img = cv2.imread(path)
                if img is None:
                    return create_error_response(f"Gagal membaca ulang gambar untuk estimator: {path}")
                images_for_estimator.append(img)
            # ==============================================================================
            
            # Gunakan OpenCV Stitcher hanya untuk estimasi
            stitcher_estimator = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)
            
            # Di Python, estimateTransform HANYA mengembalikan status.
            status = stitcher_estimator.estimateTransform(images_for_estimator)
            
            if status != cv2.Stitcher_OK:
                error_map = {1: "ERR_NEED_MORE_IMGS", 2: "ERR_HOMOGRAPHY_EST_FAIL", 3: "ERR_CAMERA_PARAMS_ADJUST_FAIL"}
                return create_error_response(f"Gagal mengestimasi transformasi: {error_map.get(status, 'Error tidak diketahui')}")
            
            # Dapatkan `cameras` setelah estimasi berhasil
            cameras = stitcher_estimator.cameras()

            rotations = [cam.R for cam in cameras]
            focal_lengths = [cam.focal for cam in cameras if cam.focal > 0]
            
            if not focal_lengths:
                return create_error_response("Tidak dapat mengestimasi focal length kamera dari estimator.")
            
            focal_length = np.median(focal_lengths)
            
            # Gunakan fungsi centering yang sudah diperbaiki
            centered_rotations = self.center_transformations(rotations, warp_method=warp_method)

            # PERHITUNGAN KANVAS YANG LEBIH SEDERHANA DAN ROBUST
            canvas_width = int(focal_length * 2 * np.pi)
            max_image_height = max(s[0] for s in image_shapes)
            canvas_height = int(max_image_height * 1.2) # Beri padding 20%
            
            canvas_center_x = canvas_width / 2
            canvas_center_y = canvas_height / 2

            output_size = (canvas_width, canvas_height)
            
            warp_params = {
                "rotations": centered_rotations, 
                "focal_length": focal_length,
                "canvas_center_x": canvas_center_x,
                "canvas_center_y": canvas_center_y
            }
        else:
            return create_error_response(f"Metode warp '{warp_method}' tidak didukung.")
            
        del all_des, all_kps
            
        # ==================== Tahap 5: Rendering ====================
        final_image_float = panorama_utils.render_panorama_tiles(
            image_paths=image_paths,
            image_shapes=image_shapes,
            warp_params=warp_params,
            output_shape=(output_size[1], output_size[0], 3),
            warp_method=warp_method, 
            blending_method=blending_method, 
            progress_callback=self.progress_callback,
            progress_range=(95, 99.5)
        )
        
        self.progress_callback(99.5, "Mengonversi gambar akhir ke format 8-bit...")
        if final_image_float is None or final_image_float.size == 0:
            return create_error_response("Gagal merender panorama akhir.")
        final_image_uint8 = (np.clip(final_image_float, 0, 1) * 255).astype(np.uint8)
        
        self.progress_callback(100, "Selesai.")

        # ==================== Bagian Akhir (Return) ====================
        return {
            "stitched_image": final_image_uint8, 
            "warped_images": None,
            "warped_masks": None,
            "homographies": homographies_final,
            "canvas_size": output_size,
            "image_shapes": image_shapes,
            "translation": translation_offset,
            "error": None
        }   

def run_standart_homography(image_paths, settings, progress_callback, return_full_data=False):
    try:
        feature_detector_name = settings.get('feature_detector', 'AKAZE')
        num_features = settings.get('num_features', 2000)
        
        print(f"--- KONFIGURASI STITCHING ---")
        print(f"  > Algoritma Deteksi Fitur: {feature_detector_name.upper()}")
        print(f"  > Jumlah Fitur per Gambar: {num_features}")
        print(f"  > Mode Return: {'FULL' if return_full_data else 'MINIMAL'}")
        print(f"-----------------------------")

        stitcher = MultiRowStandartHomography(settings, progress_callback)
        
        # stitcher.stitch sekarang selalu mengembalikan data lengkap
        full_result = stitcher.stitch(
            image_paths=image_paths,
            feature_algorithm=feature_detector_name,
            num_features=num_features, 
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
                "image_shapes": full_result["image_shapes"],
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