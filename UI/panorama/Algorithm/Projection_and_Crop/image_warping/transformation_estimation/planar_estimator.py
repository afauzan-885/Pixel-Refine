import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from scipy.optimize import least_squares

from UI.panorama.Algorithm import panorama_utils
from .base_estimator import BaseEstimator

class PlanarEstimator(BaseEstimator):
    
    def estimate(self, image_shapes: List[tuple], pairwise_matches: List[Dict], all_kps: List[Any]) -> Tuple[Dict[str, Any], tuple, str]:
        n_images = len(image_shapes)
        
        # =================================================================
        # TAHAP 1: Estimasi Awal (Sama seperti sebelumnya)
        # =================================================================
        self.progress_callback(80, "Menyusun transformasi planar awal...")
        
        centrality_scores = [0] * n_images
        for match in pairwise_matches:
            centrality_scores[match['src_idx']] += match['confidence']
            centrality_scores[match['dst_idx']] += match['confidence']
        anchor_idx = np.argmax(centrality_scores)
        
        # Dapatkan homografi awal dari MST
        initial_homographies = panorama_utils.compose_transformations_from_graph(pairwise_matches, n_images, anchor_idx)
        if initial_homographies is None:
            return None, None, "Gagal membuat grafik terhubung."
            
        # =================================================================
        # TAHAP 2: Penyempurnaan Global dengan Bundle Adjustment (BARU)
        # =================================================================
        self.progress_callback(84, "Menyempurnakan transformasi dengan Bundle Adjustment...")
        
        # Panggil fungsi BA untuk menyempurnakan homografi
        refined_homographies = self._bundle_adjust_homographies(
            initial_homographies, 
            pairwise_matches,  # Gunakan SEMUA match, bukan hanya dari MST
            all_kps, 
            n_images, 
            anchor_idx
        )

        # =================================================================
        # TAHAP 3: Pemusatan dan Perhitungan Kanvas (Sama, tapi pakai hasil BA)
        # =================================================================
        centered_homographies = panorama_utils.center_FOV(refined_homographies, "planar")

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
        
        warp_params = {"homographies": homographies_final, "translation": translation_offset}
        return warp_params, output_size, None
    
    def _bundle_adjust_homographies(self, initial_homographies, all_pairwise_matches, all_kps, n_images, anchor_idx):
        """Menyempurnakan semua homografi secara global menggunakan Bundle Adjustment."""
        
        def pack_params(homographies):
            """Mengubah list matriks homografi menjadi satu vektor parameter."""
            params = []
            for i, H in enumerate(homographies):
                if i == anchor_idx: continue
                # Kita hanya mengoptimalkan 8 parameter, karena H[2,2] biasanya 1
                params.extend(H.flatten()[:-1])
            return np.array(params)

        def unpack_params(params):
            """Mengubah kembali vektor parameter menjadi list matriks homografi."""
            homographies = [None] * n_images
            homographies[anchor_idx] = np.eye(3)
            param_idx = 0
            for i in range(n_images):
                if i == anchor_idx: continue
                # Membentuk kembali 8 parameter menjadi matriks 3x3
                flat_H = np.append(params[param_idx : param_idx + 8], 1)
                homographies[i] = flat_H.reshape((3, 3))
                param_idx += 8
            return homographies

        def objective_function(params):
            """Fungsi error (reprojection error) yang akan diminimalkan."""
            homographies = unpack_params(params)
            residuals = []
            
            for match_info in all_pairwise_matches:
                src_idx, dst_idx = match_info['src_idx'], match_info['dst_idx']
                H_src, H_dst = homographies[src_idx], homographies[dst_idx]
                
                # Jika salah satu homografi belum terhitung (seharusnya tidak terjadi)
                if H_src is None or H_dst is None: continue
                
                matches = match_info['matches']
                if not matches: continue

                kp_src, kp_dst = all_kps[src_idx], all_kps[dst_idx]
                pts_src = np.float32([kp_src[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                pts_dst = np.float32([kp_dst[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                
                # Hitung homografi relatif
                try: 
                    H_rel = np.linalg.inv(H_dst) @ H_src
                except np.linalg.LinAlgError: 
                    continue # Lewati jika matriks tidak dapat diinversi
                
                # Proyeksikan titik dari gambar sumber ke gambar tujuan
                pts_src_reproj = cv2.perspectiveTransform(pts_src, H_rel)
                if pts_src_reproj is None: continue

                # Error adalah jarak antara titik yang diproyeksikan dan titik sebenarnya
                error = (pts_dst - pts_src_reproj).flatten()
                
                # Beri bobot berdasarkan confidence, agar kecocokan yang baik lebih berpengaruh
                weight = np.sqrt(match_info.get('confidence', 1.0))
                residuals.extend(error * weight)
                
            return np.array(residuals)

        print("Memulai Bundle Adjustment untuk penyempurnaan global...")
        # Ubah homografi awal menjadi vektor parameter
        initial_params = pack_params(initial_homographies)
        
        # Jalankan optimizer non-linear least squares
        res = least_squares(
            objective_function, 
            initial_params, 
            loss='huber',  # 'huber' loss lebih tahan terhadap outlier (kecocokan buruk)
            verbose=2,     # Tampilkan progress dari optimizer
            ftol=1e-4      # Toleransi untuk penghentian
        )
        
        print("Bundle Adjustment selesai.")
        # Ubah kembali parameter yang sudah dioptimalkan menjadi list homografi
        return unpack_params(res.x)