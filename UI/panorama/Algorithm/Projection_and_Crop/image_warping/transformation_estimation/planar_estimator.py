import cv2
import numpy as np
from scipy.optimize import least_squares
from typing import List, Dict, Any, Tuple
from .base_estimator import BaseEstimator
import panorama_utils # Asumsikan fungsi-fungsi helper Anda ada di sini

class PlanarEstimator(BaseEstimator):
    def _estimate_homography(self, kp1, kp2, matches):
        # ... (Kode _estimate_homography Anda di sini) ...
        if len(matches) < 4: return None, None
        pts1 = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        pts2 = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        H, mask = cv2.findHomography(pts2, pts1, cv2.USAC_MAGSAC, 5.0)
        return H, mask

    # Catatan: _bundle_adjust_homographies juga bisa dipindahkan ke sini jika Anda menggunakannya.

    def estimate(self, n_images: int, image_shapes: List[tuple], all_kps: List, all_des: List) -> Tuple[Dict[str, Any], tuple, str]:
        # --- Kode dari Tahap 2, 3, dan 4 Anda dipindahkan ke sini ---
        self.progress_callback(45, "Mencocokkan fitur untuk model Planar...")
        pairwise_matches = []
        for i in range(n_images):
            for j in range(i + 1, n_images):
                matches = panorama_utils.match_features(all_des[i], all_des[j])
                if len(matches) < 20: continue
                H, mask = self._estimate_homography(all_kps[i], all_kps[j], matches)
                if H is None: continue
                confidence = np.sum(mask)
                if confidence < 20: continue
                pairwise_matches.append({"src_idx": i, "dst_idx": j, "T": H, "confidence": confidence})
        if not pairwise_matches:
            return None, None, "Tidak bisa menemukan pencocokan berkualitas."

        self.progress_callback(80, "Menyusun transformasi...")
        homographies = panorama_utils.compose_transformations_from_graph(pairwise_matches, n_images)
        if homographies is None:
            return None, None, "Gagal membuat grafik terhubung."
        
        centered_homographies = panorama_utils.center_FOV(homographies)
        
        self.progress_callback(88, "Menghitung kanvas akhir...")
        all_corners = []
        for i, H in enumerate(centered_homographies):
            h, w, _ = image_shapes[i]
            corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            all_corners.append(cv2.perspectiveTransform(corners, H))

        all_corners = np.concatenate(all_corners, axis=0)
        x_min, y_min = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        x_max, y_max = np.int32(all_corners.max(axis=0).ravel() + 0.5)
        T_translate = np.array([[1, 0, -x_min], [0, 1, -y_min], [0, 0, 1]])
        
        homographies_final = [T_translate @ H for H in centered_homographies]
        output_size = (y_max - y_min, x_max - x_min)

        warp_params = {"homographies": homographies_final}
        return warp_params, output_size, None