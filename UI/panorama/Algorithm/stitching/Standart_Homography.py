import os
import shutil
import tempfile
from typing import List
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

    def stitch(self, image_paths: List[str], feature_algorithm: str, num_features: int = 2000, 
               blending_method: str = "simple_average", warp_method: str = "planar"):
        """
        Melakukan proses stitching panorama lengkap dengan alur kerja yang sangat hemat memori.
        Gambar hanya dimuat saat diperlukan dan segera dilepaskan.
        """
        n_images = len(image_paths)

        def create_error_response(message):
            return {
                "stitched_image": None, "warped_images": None, "warped_masks": None, 
                "homographies": None, "canvas_size": None, "translation": None, "error": message
            }

        if n_images < 2:
            return create_error_response("Butuh setidaknya 2 gambar.")

        # ==================== Tahap 1: Persiapan Awal ====================
        self.progress_callback(5, "Menginisialisasi detektor fitur...")
        
        algo = feature_algorithm.upper()
        if algo == "SIFT":
            detector = cv2.SIFT_create(nfeatures=num_features)
        elif algo == "ORB":
            detector = cv2.ORB_create(nfeatures=num_features)
        elif algo == "AKAZE":
            detector = cv2.AKAZE_create()
        elif algo == "BRISK":
            detector = cv2.BRISK_create()
        else:
            print(f"Peringatan: Detektor '{feature_algorithm}' tidak didukung. Menggunakan AKAZE sebagai default.")
            detector = cv2.AKAZE_create()

        # Dapatkan bentuk gambar tanpa memuat gambar penuh, ini sangat hemat memori.
        def get_image_shape_from_path(path):
            img = cv2.imread(path)
            if img is None: return (0, 0, 0)
            shape = img.shape
            del img
            return shape
            
        print("Membaca dimensi gambar awal...")
        original_image_shapes = [get_image_shape_from_path(path) for path in image_paths]
        
        temp_dir = None

        try:
            # ==================== Tahap 2: Pra-Warping (Jika Diperlukan) & Persiapan Path ====================
            
            paths_for_alignment = image_paths
            shapes_for_alignment = original_image_shapes

            if warp_method in ["cylindrical", "mercator"]:
                self.progress_callback(10, f"Mode Hibrida: Estimasi focal length (hemat memori)...")
                
                # --- Estimasi Focal Length (Hemat Memori) ---
                all_kps_focal, all_des_focal = [], []
                for path in image_paths:
                    img = cv2.imread(path)
                    if img is None:
                        all_kps_focal.append([]); all_des_focal.append(None)
                        continue
                    k, d = panorama_utils.detect_features(img, detector, num_features)
                    all_kps_focal.append(k)
                    all_des_focal.append(d)
                    del img  # Hapus referensi agar memori dilepaskan
                
                pairwise_matches_for_focal = []
                for i in range(n_images):
                    for j in range(i + 1, n_images):
                        if all_des_focal[i] is None or all_des_focal[j] is None: continue
                        matches = panorama_utils.match_features(all_des_focal[i], all_des_focal[j])
                        if len(matches) < 20: continue
                        H, mask = self.estimate_homography(all_kps_focal[i], all_kps_focal[j], matches)
                        if H is not None:
                            pairwise_matches_for_focal.append({'T': H})
                
                del all_kps_focal, all_des_focal

                focals = []
                for match in pairwise_matches_for_focal:
                    H = match['T']
                    h11, h12, _, h21, h22, _, h31, h32, _ = H.flatten()
                    if abs(h31 * h32) > 1e-7: focals.append(np.sqrt(abs((h11 * h12 + h21 * h22) / (h31 * h32))))
                    if abs(h31**2 - h32**2) > 1e-7: focals.append(np.sqrt(abs(((h11**2 + h21**2) - (h12**2 + h22**2)) / (h31**2 - h32**2))))
                
                focal_length = np.median(focals) if focals else np.mean([max(s) for s in original_image_shapes])
                print(f"  > Estimasi Focal Length: {focal_length:.2f} piksel")

                # --- Lakukan Pra-Warping dan Simpan ke File Sementara ---
                self.progress_callback(20, f"Melakukan pra-warping ke {warp_method.capitalize()}...")
                temp_dir = tempfile.mkdtemp()
                prewarped_paths, prewarped_shapes = [], []

                for i, path in enumerate(image_paths):
                    self.progress_callback(20 + i * (20 / n_images), f"Pra-warping gambar {i+1}...")
                    original_image = cv2.imread(path)
                    if original_image is None: continue

                    if warp_method == "cylindrical":
                        warped_img = panorama_utils.prewarp_to_cylindrical(original_image, focal_length)
                    else:  # mercator
                        warped_img = panorama_utils.prewarp_to_spherical(original_image, focal_length)
                    
                    del original_image

                    temp_path = os.path.join(temp_dir, f"prewarped_{i}.png")
                    cv2.imwrite(temp_path, warped_img)
                    prewarped_paths.append(temp_path)
                    prewarped_shapes.append(warped_img.shape)
                    del warped_img
                
                paths_for_alignment = prewarped_paths
                shapes_for_alignment = prewarped_shapes

            # ==================== Tahap 3: Deteksi, Pencocokan, dan Estimasi (Inti) ====================

            self.progress_callback(40, "Mendeteksi fitur pada gambar (satu per satu)...")
            all_kps, all_des = [], []
            for i, path in enumerate(paths_for_alignment):
                self.progress_callback(40 + i * (20 / n_images), f"Mendeteksi fitur di gambar {i+1}...")
                img = cv2.imread(path)
                if img is None:
                    all_kps.append([]); all_des.append(None)
                    continue
                k, d = panorama_utils.detect_features(img, detector, num_features)
                all_kps.append(k)
                all_des.append(d)
                del img

            # Hitung total pasangan gambar (nC2)
            total_pairs = n_images * (n_images - 1) // 2
            pair_index = 0

            self.progress_callback(60, "Mencocokkan fitur antar gambar...")

            pairwise_matches = []
            for i in range(n_images):
                for j in range(i + 1, n_images):
                    pair_index += 1
                    progress_val = 60 + (20 * pair_index / total_pairs)

                    # Update progress callback detail: pasangan ke-i dan ke-j
                    self.progress_callback(progress_val, f"Mencocokkan fitur antara gambar {i+1} dan {j+1}...")

                    if all_des[i] is None or all_des[j] is None:
                        continue

                    matches = panorama_utils.match_features(all_des[i], all_des[j])
                    if len(matches) < 20:
                        continue

                    H, mask = self.estimate_homography(all_kps[i], all_kps[j], matches)
                    if H is None:
                        continue

                    confidence = np.sum(mask)
                    if confidence < 20:
                        continue

                    # Simpan hanya inlier
                    inlier_matches = [m for k, m in enumerate(matches) if mask[k, 0]]
                    pairwise_matches.append({
                        "src_idx": i, "dst_idx": j, "T": H,
                        "confidence": confidence, "matches": inlier_matches
                    })

            if not pairwise_matches:
                return create_error_response("Tidak bisa menemukan pencocokan berkualitas.")

            self.progress_callback(80, "Menyusun dan menyempurnakan transformasi...")
            
            centrality_scores = [0] * n_images
            for m in pairwise_matches:
                centrality_scores[m['src_idx']] += m['confidence']
                centrality_scores[m['dst_idx']] += m['confidence']
            anchor_idx = np.argmax(centrality_scores)

            initial_homographies = panorama_utils.compose_transformations_from_graph(pairwise_matches, n_images, anchor_idx)
            if initial_homographies is None:
                return create_error_response("Gagal membuat grafik terhubung.")
            
            refined_homographies = [H.copy() if H is not None else None for H in initial_homographies]
            
            # Hapus data fitur secepatnya
            del all_kps, all_des, pairwise_matches

            centered_homographies = self.center_transformations(refined_homographies, warp_method="planar")

            self.progress_callback(88, "Menghitung kanvas akhir...")
            all_corners = []
            for i, H in enumerate(centered_homographies):
                h, w, _ = shapes_for_alignment[i]
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

            # ==================== Tahap 4: Rendering ====================
            self.progress_callback(90, "Memulai rendering panorama akhir...")

            # render tiles langsung ke memmap (.mmap sudah dibuat di folder database/cache/render_tiles)
            final_image_memmap = panorama_utils.render_panorama_tiles(
                image_paths=paths_for_alignment,
                image_shapes=shapes_for_alignment,
                warp_params=warp_params,
                output_shape=(output_size[1], output_size[0], 3),
                warp_method="planar",
                blending_method=blending_method, 
                progress_callback=self.progress_callback,
                progress_range=(90, 99.5),
            )

            if final_image_memmap is None:
                return create_error_response("Gagal merender panorama.")

            # path file .mmap yang dibuat di render_panorama_tiles
            memmap_path = final_image_memmap.filename

            # konversi ke uint8 untuk preview kecil
            final_image_uint8 = (np.clip(final_image_memmap[:], 0, 1) * 255).astype(np.uint8)

            # buat preview kecil agar hemat RAM saat ditampilkan
            preview_max_size = 2048
            h, w = final_image_uint8.shape[:2]
            if max(h, w) > preview_max_size:
                scale = preview_max_size / max(h, w)
                preview = cv2.resize(
                    final_image_uint8,
                    (int(w * scale), int(h * scale)),
                    interpolation=cv2.INTER_AREA
                )
            else:
                preview = final_image_uint8

            # lepas array besar dari RAM
            del final_image_uint8

            self.progress_callback(100, "Selesai.")

            return {
                "stitched_image": preview,          # hanya preview kecil untuk display
                "memmap_path": memmap_path,         # path ke panorama penuh (.mmap)
                "dtype": np.float32,                # dtype panorama penuh
                "shape": output_size[::-1] + (3,),  # (h, w, c) full panorama
                "homographies": homographies_final,
                "canvas_size": output_size,
                "image_shapes": shapes_for_alignment,
                "translation": translation_offset,
                "error": None
            }



        finally:
            # Pastikan direktori sementara selalu dibersihkan, bahkan jika terjadi error
            if temp_dir and os.path.exists(temp_dir):
                print(f"Membersihkan file sementara di '{temp_dir}'...")
                shutil.rmtree(temp_dir)
        
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