import multiprocessing
import time
import cv2, os
import numpy as np
from scipy.linalg import sqrtm, inv
from concurrent.futures import ThreadPoolExecutor


class HybridContentAwareStitcher:
    def __init__(self, settings, progress_callback):
        self.settings = settings
        self.progress_callback = progress_callback

    def _manual_load_images(self, image_paths):
        images = [cv2.imread(p) for p in image_paths if cv2.imread(p) is not None]
        return images

    def _manual_detect_features(self, image, algorithm="sift", num_features=4000):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if algorithm.lower() == "sift":
            detector = cv2.SIFT_create(nfeatures=num_features)
        else:
            detector = cv2.ORB_create(nfeatures=num_features)
        return detector.detectAndCompute(gray, None)
    
    def _manual_match_features(self, des1, des2):
        if des1 is None or des2 is None: return []
        if des1.dtype != np.float32: des1 = des1.astype(np.float32)
        if des2.dtype != np.float32: des2 = des2.astype(np.float32)
        matcher = cv2.BFMatcher()
        raw_matches = matcher.knnMatch(des1, des2, k=2)
        return [m for m, n in raw_matches if m.distance < 0.75 * n.distance]

    def _manual_crop(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours: return image
        cnt = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(cnt)
        return image[y : y + h, x : x + w]

    def _create_feather_mask(self, mask):
        dist_transform = cv2.distanceTransform(mask, cv2.DIST_L2, cv2.DIST_MASK_5)
        max_val = np.max(dist_transform)
        if max_val == 0: return mask.astype(np.float32)
        return dist_transform / max_val
    
    def _apply_anms(self, kps, descs, num_points_to_keep):
        """
        Menerapkan Adaptive Non-Maximal Suppression (ANMS) secara PARALEL
        untuk mendapatkan distribusi keypoint yang lebih baik dengan cepat.
        """
        num_initial_points = len(kps)
        if num_initial_points <= num_points_to_keep:
            return kps, descs

        # Urutkan keypoints berdasarkan respons (kekuatan) dari yang terkuat ke terlemah
        indices = np.argsort([kp.response for kp in kps])[::-1]
        kps_sorted = np.array(kps)[indices]
        descs_sorted = descs[indices]
        
        # Ekstrak hanya koordinat (x,y) untuk perhitungan jarak yang cepat
        pts_sorted = np.array([kp.pt for kp in kps_sorted], dtype=np.float32)

        # Definisikan fungsi helper yang akan dijalankan oleh setiap thread
        # Fungsi ini menghitung radius supresi untuk satu titik.
        def calculate_radius_for_point(i):
            # Titik saat ini
            pt_i = pts_sorted[i]
            # Semua titik yang lebih kuat (sudah diproses sebelumnya)
            stronger_pts = pts_sorted[:i]
            
            # Hitung jarak dari titik saat ini ke SEMUA titik yang lebih kuat sekaligus
            distances = np.linalg.norm(stronger_pts - pt_i, axis=1)
            
            # Radius adalah jarak minimum
            return np.min(distances)

        # Tentukan jumlah thread
        num_threads = multiprocessing.cpu_count()
        print(f"    - Menghitung radius ANMS dengan {num_threads} thread...")

        # Jalankan perhitungan radius secara paralel menggunakan ThreadPoolExecutor
        # Kita mulai dari i=1 karena titik terkuat (i=0) selalu memiliki radius tak terhingga
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            radii_list = list(executor.map(calculate_radius_for_point, range(1, num_initial_points)))
        
        # Gabungkan hasilnya. Ingat, titik pertama (i=0) memiliki radius tak terhingga.
        radii = np.array([np.inf] + radii_list)
        
        # Urutkan berdasarkan radius supresi (semakin besar semakin baik untuk distribusi)
        final_indices = np.argsort(radii)[::-1]
        
        # Pilih N titik teratas
        anms_kps = kps_sorted[final_indices[:num_points_to_keep]]
        anms_descs = descs_sorted[final_indices[:num_points_to_keep]]
        
        return list(anms_kps), anms_descs
   
    def _calculate_iterative_flow(self, img1_gray, img2_gray, num_levels=4):
        """
        Menghitung dense optical flow menggunakan pendekatan piramida iteratif
        untuk meningkatkan akurasi secara signifikan (Coarse-to-Fine).
        """
        # Buat piramida gambar untuk kedua gambar
        pyramid1 = [img1_gray]
        pyramid2 = [img2_gray]
        for _ in range(num_levels - 1):
            pyramid1.append(cv2.pyrDown(pyramid1[-1]))
            pyramid2.append(cv2.pyrDown(pyramid2[-1]))

        # Balik urutan agar dimulai dari yang paling kasar (terkecil)
        pyramid1 = list(reversed(pyramid1))
        pyramid2 = list(reversed(pyramid2))
        
        # Inisialisasi flow di level terkecil
        h, w = pyramid1[0].shape
        flow = np.zeros((h, w, 2), dtype=np.float32)

        # Iterasi dari kasar ke halus (coarse to fine)
        for i in range(num_levels):
            # Upscale flow dari level sebelumnya
            if i > 0:
                h, w = pyramid1[i].shape
                flow = cv2.pyrUp(flow)
                # Penting: Sesuaikan magnitudo flow karena resolusi berlipat ganda
                flow *= 2 
            
            # Warp gambar 2 menggunakan flow yang sudah di-upscale
            # untuk membuatnya lebih dekat dengan gambar 1
            h, w = pyramid1[i].shape
            yy, xx = np.indices((h, w), dtype=np.float32)
            map_x = xx + flow[:, :, 0]
            map_y = yy + flow[:, :, 1]
            
            warped_img2 = cv2.remap(pyramid2[i], map_x, map_y, cv2.INTER_LINEAR)

            # Hitung flow sisa (residual) pada level ini
            residual_flow = cv2.calcOpticalFlowFarneback(pyramid1[i], warped_img2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            
            # Tambahkan flow sisa ke flow saat ini untuk menyempurnakannya
            flow += residual_flow
            
        return flow
    
    def _manual_warp_image(self, img, H, size, translation=(0, 0)):
        """
        Melakukan warp pada sebuah gambar menggunakan matriks homografi (H) 
        dan sebuah translasi.

        Args:
            img: Gambar sumber yang akan di-warp.
            H: Matriks homografi 3x3 yang mendefinisikan transformasi perspektif.
            size: Tuple (lebar, tinggi) untuk ukuran kanvas output.
            translation: Tuple (tx, ty) untuk menggeser hasil warp agar pas di kanvas.

        Returns:
            Gambar yang sudah di-warp.
        """
        # 1. Buat matriks translasi (T)
        # Translasi ini digunakan untuk memastikan seluruh panorama (yang mungkin memiliki
        # koordinat negatif setelah di-warp) dapat ditampilkan di kanvas output.
        T = np.array(
            [[1, 0, translation[0]], 
             [0, 1, translation[1]], 
             [0, 0, 1]],
            dtype=np.float32,
        )

        # 2. Gabungkan matriks homografi (H) dengan matriks translasi (T)
        # Transformasi akhir adalah melakukan H terlebih dahulu, baru kemudian T.
        # Dalam perkalian matriks, urutannya adalah T @ H.
        H_final = T @ H

        # 3. Gunakan fungsi warpPerspective dari OpenCV untuk menerapkan transformasi akhir
        # 'size' harus dalam format (lebar, tinggi) yang diharapkan oleh OpenCV.
        return cv2.warpPerspective(img, H_final, size)

    def stitch(self, image_paths, feature_algorithm, num_features=10000):
            print("--- MEMULAI PROSES STITCHING ULTIMATE (ANMS + FLOW SMOOTHING) ---")
            HARDCODE_BASE_PATH = "D:/database"
            os.makedirs(HARDCODE_BASE_PATH, exist_ok=True)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_dir = os.path.join(HARDCODE_BASE_PATH, f"stitch_debug_{timestamp}")
            os.makedirs(output_dir, exist_ok=True)
            images = self._manual_load_images(image_paths)
            if len(images) != 2: raise ValueError("Hanya untuk 2 gambar.")
            img_anchor, img_src = images[0], images[1]

            # Deteksi fitur dalam jumlah besar
            (kp_anchor_raw, des_anchor_raw) = self._manual_detect_features(img_anchor, feature_algorithm, num_features)
            (kp_src_raw, des_src_raw) = self._manual_detect_features(img_src, feature_algorithm, num_features)

            # --- PENYEMPURNAAN 1: GUNAKAN ANMS UNTUK DISTRIBUSI FITUR YANG LEBIH BAIK ---
            print("  > Menerapkan ANMS untuk distribusi fitur yang lebih baik...")
            num_anms_points = 2000 # Jumlah fitur yang lebih sedikit tapi lebih berkualitas
            (kp_anchor, des_anchor) = self._apply_anms(kp_anchor_raw, des_anchor_raw, num_anms_points)
            (kp_src, des_src) = self._apply_anms(kp_src_raw, des_src_raw, num_anms_points)
            print(f"    - Fitur dikurangi menjadi {len(kp_src)} (src) dan {len(kp_anchor)} (anchor) titik.")

            # Lanjutkan dengan fitur yang sudah di-filter ANMS
            global_matches = self._manual_match_features(des_src, des_anchor)
            if len(global_matches) < 4: return {"stitched_image": None, "error": "Tidak cukup pencocokan global."}
            
            H_global_src_to_anchor, _ = cv2.findHomography(
                np.float32([kp_src[m.queryIdx].pt for m in global_matches]).reshape(-1, 1, 2),
                np.float32([kp_anchor[m.trainIdx].pt for m in global_matches]).reshape(-1, 1, 2),
                cv2.RANSAC, 5.0
            )
            if H_global_src_to_anchor is None: return {"stitched_image": None, "error": "Gagal menghitung H global."}

            print("  > Coarse Registration: Menghitung warp 'bertemu di tengah'...")
            try:
                H_sqrt_complex = sqrtm(H_global_src_to_anchor)
                H_inv_sqrt_complex = inv(H_sqrt_complex)
                H_center_src = H_sqrt_complex.real.astype(np.float32)
                H_center_anchor = H_inv_sqrt_complex.real.astype(np.float32)
            except Exception as e:
                print(f"PERINGATAN: Gagal menghitung akar matriks. Error: {e}")
                H_center_src = H_global_src_to_anchor.astype(np.float32)
                H_center_anchor = np.eye(3, dtype=np.float32)

            h_src, w_src = img_src.shape[:2]
            h_anchor, w_anchor = img_anchor.shape[:2]
            corners_src = np.float32([[0, 0], [0, h_src], [w_src, h_src], [w_src, 0]]).reshape(-1, 1, 2)
            corners_anchor = np.float32([[0, 0], [0, h_anchor], [w_anchor, h_anchor], [w_anchor, 0]]).reshape(-1, 1, 2)
            warped_corners_src = cv2.perspectiveTransform(corners_src, H_center_src)
            warped_corners_anchor = cv2.perspectiveTransform(corners_anchor, H_center_anchor)
            all_corners = np.concatenate((warped_corners_anchor, warped_corners_src), axis=0)
            x_min, y_min = np.int32(all_corners.min(axis=0).ravel() - 0.5)
            x_max, y_max = np.int32(all_corners.max(axis=0).ravel() + 0.5)
            translation = [-x_min, -y_min]
            output_size = (x_max - x_min, y_max - y_min)

            warped_src = self._manual_warp_image(img_src, H_center_src, output_size, translation)
            warped_anchor = self._manual_warp_image(img_anchor, H_center_anchor, output_size, translation)
            
            print("  > Optical Flow Stage: Menghitung deformasi sampling warna...")
            gray_src = cv2.cvtColor(warped_src, cv2.COLOR_BGR2GRAY)
            gray_anchor = cv2.cvtColor(warped_anchor, cv2.COLOR_BGR2GRAY)
            mask_src = (gray_src > 0).astype(np.uint8) * 255
            mask_anchor = (gray_anchor > 0).astype(np.uint8) * 255
            mask_overlap = cv2.bitwise_and(mask_src, mask_anchor)

            print("    - Menghitung Bidirectional Optical Flow...")
            flow_AtoS = cv2.calcOpticalFlowFarneback(gray_anchor, gray_src, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            flow_StoA = cv2.calcOpticalFlowFarneback(gray_src, gray_anchor, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            
            # --- PENYEMPURNAAN 2: HALUSKAN FLOW FIELD UNTUK MENGURANGI "PENYOK" ---
            print("    - Menghaluskan flow field untuk menjaga struktur...")
            # Kernel size yang lebih besar akan menghasilkan deformasi yang lebih mulus.
            # Harus ganjil. (31, 31) adalah awal yang baik.
            kernel_size = (31, 31) 
            flow_AtoS = cv2.GaussianBlur(flow_AtoS, kernel_size, 0)
            flow_StoA = cv2.GaussianBlur(flow_StoA, kernel_size, 0)

            # Nol-kan kembali flow di luar overlap setelah dihaluskan
            flow_AtoS[mask_overlap == 0] = 0
            flow_StoA[mask_overlap == 0] = 0
            
            print("  > Blending Stage: Menggabungkan gambar dengan deformasi flow...")
            blend_map_src = self._create_feather_mask(mask_src)
            blend_map_anchor = self._create_feather_mask(mask_anchor)
            total_blend = blend_map_src + blend_map_anchor
            total_blend[total_blend == 0] = 1.0
            blend_R = blend_map_anchor / total_blend
            blend_L = 1.0 - blend_R

            pano_h, pano_w = output_size[1], output_size[0]
            pano_yy, pano_xx = np.indices((pano_h, pano_w), dtype=np.float32)
            
            map_x_L = pano_xx + flow_AtoS[:,:,0] * blend_R
            map_y_L = pano_yy + flow_AtoS[:,:,1] * blend_R
            map_x_R = pano_xx + flow_StoA[:,:,0] * blend_L
            map_y_R = pano_yy + flow_StoA[:,:,1] * blend_L

            print("    - Melakukan sampling warna terdeformasi...")
            color_L = cv2.remap(warped_src, map_x_L, map_y_L, cv2.INTER_LINEAR)
            color_R = cv2.remap(warped_anchor, map_x_R, map_y_R, cv2.INTER_LINEAR)

            panorama = color_L.astype(np.float32) * blend_L[:, :, np.newaxis] + \
                    color_R.astype(np.float32) * blend_R[:, :, np.newaxis]

            panorama = np.clip(panorama, 0, 255).astype(np.uint8)
            panorama_final = self._manual_crop(panorama)
            final_pano_fname = os.path.join(output_dir, "panorama_ULTIMATE_V2.png")
            cv2.imwrite(final_pano_fname, panorama_final)
            
            return {"stitched_image": panorama_final, "error": None}

def run_local_homography(image_paths, settings, progress_callback):
    # Wrapper function
    try:
        stitcher = HybridContentAwareStitcher(settings, progress_callback)
        result = stitcher.stitch(
            image_paths=image_paths,
            feature_algorithm=settings.get("feature_detector", "sift"),
            num_features=settings.get("num_features", 10000),
        )
        print("INFO: Proses Hybrid Stitching selesai.")
        return result
    except Exception as e:
        import traceback

        print(f"FATAL ERROR: {e}")
        traceback.print_exc()
        return {"stitched_image": None, "error": str(e)}
