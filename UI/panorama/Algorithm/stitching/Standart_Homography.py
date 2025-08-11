import gc
import math
import os
import shutil
import cv2
from joblib import Parallel, delayed
import numpy as np
import zarr
# Tambahkan import ini di bagian atas file Anda
import dask
import dask.array as da
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

    def stitch(self, image_paths, feature_algorithm, num_features=2000,preview_scale=0.1):
        n_images = len(image_paths)

        def create_error_response(message):
            return {
                "stitched_image": None, "warped_images": None,
                "warped_masks": None, "homographies": None, "canvas_size": None,
                "translation": None, "error": message
            }

        if n_images < 2:
            return create_error_response("Butuh setidaknya 2 gambar.")

        # ==================== Tahap 1: Deteksi fitur ====================
        self.progress_callback(5, "Mendeteksi fitur...")
        all_kps, all_des = [None] * n_images, [None] * n_images
        image_shapes = [None] * n_images

        for i, path in enumerate(image_paths):
            self.progress_callback(5 + i * (40 / n_images), f"Mendeteksi fitur di gambar {i+1}...")
            img_to_process = cv2.imread(path)
            if img_to_process is None:
                return create_error_response(f"Gagal membaca gambar: {path}")

            image_shapes[i] = img_to_process.shape
            all_kps[i], all_des[i] = stitching_utils.detect_features(
                img_to_process, feature_algorithm, num_features=num_features
            )

        # ==================== Tahap 2: Pencocokan & Homografi ====================
        self.progress_callback(45, "Mencocokkan fitur...")
        pairwise_matches = []
        for i in range(n_images):
            for j in range(i + 1, n_images):
                matches = stitching_utils.match_features(all_des[i], all_des[j])
                if len(matches) < 20:
                    continue

                H, mask = self.estimate_homography(all_kps[i], all_kps[j], matches)
                if H is None:
                    continue

                confidence = np.sum(mask)
                if confidence < 20:
                    continue

                inlier_matches = [m for k, m in enumerate(matches) if mask[k] == 1]
                if not inlier_matches:
                    continue

                pairwise_matches.append({
                    "src_idx": i, "dst_idx": j, "T": H, "confidence": confidence, "matches": inlier_matches
                })

        del all_des, all_kps
        if not pairwise_matches:
            return create_error_response("Tidak bisa menemukan pencocokan berkualitas.")

        # ==================== Tahap 3: Komposisi graf ====================
        self.progress_callback(80, "Menyusun transformasi...")
        centrality_scores = [0] * n_images
        for match in pairwise_matches:
            centrality_scores[match['src_idx']] += match['confidence']
            centrality_scores[match['dst_idx']] += match['confidence']
        anchor_idx = np.argmax(centrality_scores)

        homographies = stitching_utils.compose_transformations_from_graph(pairwise_matches, n_images, anchor_idx)
        if homographies is None:
            return create_error_response("Gagal membuat grafik terhubung.")

        self.progress_callback(85, "Menghitung transformasi terpusat...")
        centered_homographies = stitching_utils.center_FOV(homographies)

        # ==================== Tahap 4: Perhitungan kanvas ====================
        self.progress_callback(88, "Menghitung kanvas akhir...")
        all_corners = []
        for i, H in enumerate(centered_homographies):
            h, w, _ = image_shapes[i]
            corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            warped = cv2.perspectiveTransform(corners, H)
            all_corners.append(warped)

        all_corners = np.concatenate(all_corners, axis=0)
        x_min, y_min = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        x_max, y_max = np.int32(all_corners.max(axis=0).ravel() + 0.5)

        translation_offset = [-x_min, -y_min]
        output_size = (x_max - x_min, y_max - y_min)

        T_translate = np.array([[1, 0, translation_offset[0]], [0, 1, translation_offset[1]], [0, 0, 1]])
        homographies_final = [T_translate @ H for H in centered_homographies]

        # ==================== Tahap 5: Rendering (Preview + Tile-Based Full-Res) ====================
        
        # 1) Preview (kecil) — lazy stack + compute (TETAP SAMA)
        # Bagian ini sudah sangat cepat dan hemat memori, jadi kita pertahankan.
        self.progress_callback(90, "Memulai rendering dengan Dask (preview)...")
        preview_output_size = (int(output_size[0] * preview_scale), int(output_size[1] * preview_scale))
        preview_output_shape = (preview_output_size[1], preview_output_size[0], 3)
        S = np.array([[preview_scale, 0, 0], [0, preview_scale, 0], [0, 0, 1]])
        preview_homographies = [S @ H for H in homographies_final]

        lazy_preview_warps = []
        lazy_preview_masks = []
        for i in range(n_images):
            lazy_result = dask.delayed(stitching_utils._warp_to_dask_array)(
                image_paths[i], preview_homographies[i], preview_output_shape, chunks='auto'
            )
            preview_warp_da = da.from_delayed(lazy_result[0], shape=preview_output_shape, dtype=np.float32)
            preview_mask_da = da.from_delayed(lazy_result[1], shape=(preview_output_shape[0], preview_output_shape[1]), dtype=np.float32)
            lazy_preview_warps.append(preview_warp_da)
            lazy_preview_masks.append(preview_mask_da)

        preview_sum = da.stack(lazy_preview_warps).sum(axis=0)
        preview_count = da.maximum(da.stack(lazy_preview_masks).sum(axis=0), 1.0)
        panorama_preview = (preview_sum / preview_count[..., np.newaxis]).astype(np.uint8).compute()

        # ==============================================================================
        # 2) Full-resolution TILE-BASED PARALLEL rendering dengan Custom Progress
        # ==============================================================================
        self.progress_callback(95, "Mempersiapkan rendering paralel berbasis ubin...")
        full_output_shape = (output_size[1], output_size[0], 3)
        TILE_SIZE = (1024, 1024)

        cache_dir = os.path.join("database", "cache", "align_stitch")
        os.makedirs(cache_dir, exist_ok=True)
        temp_pano_path = os.path.join(cache_dir, "panorama_temp.mmap")
        
        if os.path.exists(temp_pano_path):
            os.remove(temp_pano_path)

        panorama_full = np.memmap(temp_pano_path, dtype=np.uint8, mode='w+', shape=full_output_shape)
        
        # Buat daftar semua tugas (ubin) yang akan diproses
        all_tasks = []
        for y_start in range(0, full_output_shape[0], TILE_SIZE[0]):
            for x_start in range(0, full_output_shape[1], TILE_SIZE[1]):
                y_end = min(y_start + TILE_SIZE[0], full_output_shape[0])
                x_end = min(x_start + TILE_SIZE[1], full_output_shape[1])
                tile_shape = (y_end - y_start, x_end - x_start, 3)
                
                args = (
                    y_start, x_start, tile_shape, full_output_shape, 
                    homographies_final, image_paths, image_shapes
                )
                all_tasks.append(args)

        total_tiles = len(all_tasks)
        self.progress_callback(96, f"Memulai pemrosesan {total_tiles} ubin...")

        # --- LOGIKA BATCHING UNTUK PROGRESS REPORTING ---
        
        # Tentukan ukuran batch. Ukuran yang sama dengan jumlah core adalah pilihan yang baik.
        n_cores = os.cpu_count() or 4
        batch_size = n_cores 
        
        num_batches = int(math.ceil(total_tiles / batch_size))
        tasks_completed = 0

        # Proses tugas dalam beberapa batch
        for i in range(num_batches):
            # Ambil batch tugas saat ini
            start_index = i * batch_size
            end_index = start_index + batch_size
            current_batch_tasks = all_tasks[start_index:end_index]
            
            if not current_batch_tasks:
                continue

            # Jalankan joblib hanya untuk batch ini
            batch_results = Parallel(n_jobs=n_cores, backend="loky")(
                delayed(stitching_utils._process_single_tile)(task) for task in current_batch_tasks
            )
            
            # Tulis hasil dari batch yang sudah selesai ke disk
            for y_start, x_start, final_tile in batch_results:
                y_end = y_start + final_tile.shape[0]
                x_end = x_start + final_tile.shape[1]
                panorama_full[y_start:y_end, x_start:x_end] = final_tile
            
            # Perbarui progress setelah setiap batch selesai
            tasks_completed += len(batch_results)
            progress = 96 + (tasks_completed / total_tiles) * 3 # Progress dari 96% ke 99%
            self.progress_callback(progress, f"Memproses ubin... ({tasks_completed}/{total_tiles})")

        # --- AKHIR LOGIKA BATCHING ---

        self.progress_callback(99.5, "Menyelesaikan gambar akhir...")
        final_image_in_memory = np.array(panorama_full)

        panorama_full.flush()
        del panorama_full
        try:
            os.remove(temp_pano_path)
        except OSError as e:
            print(f"Peringatan: Tidak bisa menghapus file temp: {e}")

        self.progress_callback(100, "Selesai.")

        return {
            "stitched_image": final_image_in_memory,  # Resolusi penuh, sekarang dimuat dari hasil di disk
            "stitched_preview": panorama_preview,  
            "warped_images": None,
            "warped_masks": None,
            "homographies": homographies_final,
            "canvas_size": output_size,
            "translation": [0, 0],
            "error": None
        }
        
def run_standart_homography(image_paths, settings, progress_callback, return_full_data=False):
    try:
        # Ekstrak konfigurasi
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