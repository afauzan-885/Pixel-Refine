import concurrent.futures 
import os
import concurrent
import cv2
import h5py
import numpy as np

from UI.settings.General.Language import language_config


# ------------------ Load and Saving Process ------------------- #
def load_images_from_paths(image_paths, stop_requested=None):
        """
        Loads images from a list of image paths using multithreading.
        """
        num_threads = os.cpu_count() or 4  # Default ke 4 jika os.cpu_count() mengembalikan None
        images = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {executor.submit(cv2.imread, path, cv2.IMREAD_UNCHANGED): path for path in image_paths}

            for future in futures:
                if stop_requested and stop_requested():
                    break
                image = future.result()
                if image is not None:
                    images.append(image)

        return images

def save_to_hdf5(h5f, dataset_name, cropped):
    h5f.create_dataset(dataset_name, data=cropped, compression="lzf")
# ------------------ Load and Saving Process ------------------- #
    
## ------------------ Feature-based Alignment ------------------- ##

## ---------------- Calculate Global Motion Process ---------------- ##
# ---------------- Calculate Global Motion Process ---------------- #
def compute_images_multithreaded(base_gray, target_gray, extractor_func, num_blocks=(2,2), overlap=20):
    """
    Membagi gambar menjadi blok-blok dan mengekstrak fitur secara paralel menggunakan fungsi extractor_func.
    
    Parameters:
      - base_gray: gambar grayscale untuk citra dasar.
      - target_gray: gambar grayscale untuk citra target.
      - extractor_func: fungsi yang menerima ROI gambar dan mengembalikan (keypoints, deskriptor).
      - num_blocks: tuple (blocks_x, blocks_y) untuk pembagian blok.
      - overlap: jumlah piksel overlap di sekitar tiap blok.
    
    Mengembalikan:
      (keypoints_base_all, descriptors_base_all, keypoints_target_all, descriptors_target_all)
    """
    h, w = base_gray.shape
    blocks_x, blocks_y = num_blocks
    block_w = w // blocks_x
    block_h = h // blocks_y

    keypoints_base_all = []
    descriptors_base_all = None
    keypoints_target_all = []
    descriptors_target_all = None

    def compute_features_block(x, y, bw, bh, overlap):
        roi_x_start = max(0, x - overlap)
        roi_y_start = max(0, y - overlap)
        roi_x_end = min(w, x + bw + overlap)
        roi_y_end = min(h, y + bh + overlap)

        roi_base = base_gray[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
        roi_target = target_gray[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

        kps_base, desc_base = extractor_func(roi_base)
        kps_target, desc_target = extractor_func(roi_target)

        # Sesuaikan koordinat keypoints agar sesuai dengan posisi asli di gambar penuh
        for kp in kps_base:
            kp.pt = (kp.pt[0] + roi_x_start, kp.pt[1] + roi_y_start)
        for kp in kps_target:
            kp.pt = (kp.pt[0] + roi_x_start, kp.pt[1] + roi_y_start)
        return kps_base, desc_base, kps_target, desc_target

    max_workers = blocks_x * blocks_y
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for i in range(blocks_x):
            for j in range(blocks_y):
                x = i * block_w
                y = j * block_h
                # Untuk blok terakhir, pastikan tidak ada pixel yang tertinggal
                bw = block_w if i < blocks_x - 1 else w - x
                bh = block_h if j < blocks_y - 1 else h - y
                futures.append(executor.submit(compute_features_block, x, y, bw, bh, overlap))
        for future in concurrent.futures.as_completed(futures):
            kps_base, desc_base, kps_target, desc_target = future.result()
            if desc_base is not None and len(kps_base) > 0:
                keypoints_base_all.extend(kps_base)
                if descriptors_base_all is None:
                    descriptors_base_all = desc_base
                else:
                    descriptors_base_all = np.vstack([descriptors_base_all, desc_base])
            if desc_target is not None and len(kps_target) > 0:
                keypoints_target_all.extend(kps_target)
                if descriptors_target_all is None:
                    descriptors_target_all = desc_target
                else:
                    descriptors_target_all = np.vstack([descriptors_target_all, desc_target])
    return keypoints_base_all, descriptors_base_all, keypoints_target_all, descriptors_target_all

# ---------------- Calculate Global Motion Process ---------------- #
def compute_global_crop(transform_folder, total_images, w, h, transformation_type='homography'):
    """
    Menghitung batas cropping global dengan menggunakan batas pergerakan
    dari setiap transformasi. Fungsi ini mengembalikan koordinat crop global:
    (crop_x, crop_y, crop_w, crop_h)
    """
    # Inisialisasi dengan nilai ekstrem
    global_min_x =  float('inf')
    global_min_y =  float('inf')
    global_max_x = -float('inf')
    global_max_y = -float('inf')

    # Koordinat sudut asli gambar referensi
    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(-1, 1, 2)
    
    for i in range(1, total_images):  # Mulai dari gambar ke-1 (index 0 adalah referensi)
        transform_file_path = os.path.join(transform_folder, f"transform_{i}.npy")
        if not os.path.exists(transform_file_path):
            continue
        
        base_points, target_points = np.load(transform_file_path, allow_pickle=True)
        
        # Perkirakan matriks transformasi
        if transformation_type == 'homography':
            matrix, _ = cv2.findHomography(np.array(base_points), np.array(target_points), 0)
        else:
            matrix = cv2.estimateAffine2D(np.array(base_points), np.array(target_points))[0]
        if matrix is None:
            continue
        
        # Transformasikan sudut gambar
        if transformation_type == 'homography':
            transformed_corners = cv2.perspectiveTransform(corners, matrix)
        else:
            transformed_corners = cv2.transform(corners, matrix)
        transformed_corners = transformed_corners.reshape(-1, 2)
        
        min_xy = transformed_corners.min(axis=0)
        max_xy = transformed_corners.max(axis=0)
        min_x, min_y = min_xy
        max_x, max_y = max_xy
        
        # Update batas global
        global_min_x = min(global_min_x, min_x)
        global_min_y = min(global_min_y, min_y)
        global_max_x = max(global_max_x, max_x)
        global_max_y = max(global_max_y, max_y)
    
    # Hitung crop region berdasarkan batas global dan gambar referensi
    crop_x = int(max(0, np.ceil(-global_min_x)))   # Offset kiri
    crop_y = int(max(0, np.ceil(-global_min_y)))   # Offset atas
    crop_w = w - int(np.ceil(global_max_x - w)) - crop_x  # Lebar area yang tersisa
    crop_h = h - int(np.ceil(global_max_y - h)) - crop_y  # Tinggi area yang tersisa

    if crop_w <= 0 or crop_h <= 0:
        print("Crop region global tidak valid. Tidak ada overlap yang cukup.")
        return None

    return crop_x, crop_y, crop_w, crop_h

def crop_image(image, crop_bounds):
    """Melakukan cropping pada gambar sesuai batas crop yang diberikan."""
    crop_x, crop_y, crop_w, crop_h = crop_bounds
    return image[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]

# ------------------------------ Main Process ---------------------------------- #
## ----------------  Feature-based Alignment ---------------- ##


## ---------------- Optical Flow-based Alignment ---------------- ##
def compute_optical_flow_images_multithreaded(base_gray, target_gray, process_func, num_blocks=(3, 3), overlap_ratio=0.3, use_gpu=False):
    """
    Membagi gambar menjadi blok-blok dan memprosesnya secara paralel menggunakan fungsi yang diberikan.
    
    Parameters:
      - base_gray: gambar grayscale untuk citra dasar.
      - target_gray: gambar grayscale untuk citra target.
      - process_func: fungsi yang menerima ROI gambar dan mengembalikan hasil komputasi.
      - num_blocks: tuple (blocks_x, blocks_y) untuk pembagian blok.
      - overlap_ratio: persentase overlap relatif terhadap ukuran blok.
      - use_gpu: apakah menggunakan UMat untuk OpenCV GPU processing.
    
    Mengembalikan:
      - Matriks hasil komputasi (misalnya optical flow)
    """
    h, w = base_gray.shape if not use_gpu else base_gray.get().shape
    blocks_x, blocks_y = num_blocks
    block_w = w // blocks_x
    block_h = h // blocks_y
    
    result_full = np.zeros((h, w, 2), dtype=np.float32)
    
    def process_block(x, y, bw, bh):
        overlap_x = int(bw * overlap_ratio)
        overlap_y = int(bh * overlap_ratio)
        
        roi_x_start = max(0, x - overlap_x)
        roi_y_start = max(0, y - overlap_y)
        roi_x_end = min(w, x + bw + overlap_x)
        roi_y_end = min(h, y + bh + overlap_y)
        
        if use_gpu:
            roi_base = base_gray.get()[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
            roi_target = target_gray.get()[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
        else:
            roi_base = base_gray[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
            roi_target = target_gray[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
        
        result_block = process_func(roi_base, roi_target)
        
        offset_x = x - roi_x_start
        offset_y = y - roi_y_start
        h_block, w_block, _ = result_block.shape
        result_full[y:y+h_block, x:x+w_block, :] = result_block
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=blocks_x * blocks_y) as executor:
        futures = []
        for i in range(blocks_x):
            for j in range(blocks_y):
                x = i * block_w
                y = j * block_h
                bw = block_w if i < blocks_x - 1 else w - x
                bh = block_h if j < blocks_y - 1 else h - y
                futures.append(executor.submit(process_block, x, y, bw, bh))
        
        concurrent.futures.wait(futures)
    
    return result_full