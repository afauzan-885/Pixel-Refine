import concurrent.futures 
import os
import concurrent
import cv2
import h5py
import numpy as np

# ------------------ Load and Saving Process ------------------- #
def load_images_from_paths(image_paths, stop_requested=None):
    """
    Memuat gambar dari daftar path gambar menggunakan multithreading untuk mempercepat proses I/O.
    """
    
    def load_image(image_path):
        if stop_requested and stop_requested():
            return None
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        return image if image is not None else None
    
    images = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(load_image, path): path for path in image_paths}
        
        for future in concurrent.futures.as_completed(futures):
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


# ------------------ Compensate Motion Process ------------------- #
def estimate_transformation(transformation_type, base_points, target_points, corners):
        """
        Estimate the transformation matrix and transform the image corners based on the given type.
        """
        if transformation_type == 'affine':
            matrix, _ = cv2.estimateAffine2D(target_points, base_points, method=cv2.RANSAC, ransacReprojThreshold=5.0)
            if matrix is None:
                raise ValueError("Affine transformation estimation failed.")
            transformed_corners = cv2.transform(np.array([corners]), matrix)[0]
            return matrix, transformed_corners

        elif transformation_type in ['similarity', 'euclidean']:
            matrix, _ = cv2.estimateAffinePartial2D(target_points, base_points, method=cv2.RANSAC, ransacReprojThreshold=5.0)
            if matrix is None:
                raise ValueError("Similarity/Euclidean transformation estimation failed.")
            if transformation_type == 'euclidean' and not np.isclose(np.linalg.norm(matrix[:2, 0]), np.linalg.norm(matrix[:2, 1])):
                raise ValueError("Transformation is not Euclidean (scaling detected).")
            transformed_corners = cv2.transform(np.array([corners]), matrix)[0]
            return matrix, transformed_corners

        elif transformation_type == 'homography':
            H, _ = cv2.findHomography(target_points, base_points, cv2.RANSAC, 5.0)
            if H is None:
                raise ValueError("Homography estimation failed.")
            transformed_corners = cv2.perspectiveTransform(np.array([corners]), H)[0]
            return H, transformed_corners

        else:
            raise ValueError("Unknown transformation type.")

def transform_corners(transformation_matrix, corners, transformation_type):
        """
        Transform the given corners using the provided transformation matrix.
        """
        if transformation_type in ['affine', 'similarity', 'euclidean']:
            return cv2.transform(np.array([corners]), transformation_matrix)[0]
        elif transformation_type == 'homography':
            return cv2.perspectiveTransform(np.array([corners]), transformation_matrix)[0]
        else:
            raise ValueError("Unknown transformation type.")

def compute_padding(transformed_corners, h, w):
        """
        Compute the padding required so that the transformed image is not clipped.
        """
        min_x, min_y = np.min(transformed_corners, axis=0).astype(int)
        max_x, max_y = np.max(transformed_corners, axis=0).astype(int)

        pad_top = max(0, -min_y)
        pad_left = max(0, -min_x)
        pad_bottom = max(0, max_y - h)
        pad_right = max(0, max_x - w)
        return pad_top, pad_left, pad_bottom, pad_right

# ------------------ Compensate Motion Process ------------------- #
    
# --------------- Main Process -------------- #
def process_with_cropping(processor, base_image, remaining_paths, batch_count, batch_size,
                          h, w, transformation_dir, update_progress, total_images, stop_requested):
    # Phase 1: Estimate transformations and compute cropping offsets
    aligned_offsets = [(0, 0)]  # Offset for base_image is (0,0)
    all_pad_tops = [0]
    all_pad_lefts = [0]
    image_index = 1

    total_steps = total_images * 2  # Total langkah (kalkulasi + penyimpanan)
    current_step = 0  # Inisialisasi progress

    for batch_idx in range(batch_count):
        if stop_requested and stop_requested():
            break

        start_idx = batch_idx * batch_size
        end_idx = min((batch_idx + 1) * batch_size, len(remaining_paths))
        batch_paths = remaining_paths[start_idx:end_idx]
        batch_images = load_images_from_paths(batch_paths, stop_requested)
        if not batch_images:
            continue

        for target_image in batch_images:
            if stop_requested and stop_requested():
                print("Proses dihentikan oleh pengguna.")
                break

            base_pts, target_pts = processor.calculate_global_motion(base_image, target_image)
            if base_pts is None or target_pts is None:
                print(f"Global motion tidak dapat dihitung untuk gambar ke-{image_index}")
                image_index += 1
                continue

            _, (pad_top, pad_left, _, _) = processor.compensate_motion(
                base_image, base_pts, target_pts, transformation_type='homography'
            )

            transformation_matrix, _ = estimate_transformation(
                'homography', base_pts, target_pts, np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32)
            )

            if transformation_matrix is None:
                print(f"Estimasi homografi gagal untuk gambar ke-{image_index}")
                image_index += 1
                continue

            # Simpan matriks transformasi
            transformation_path = os.path.join(transformation_dir, f"transformation_image_{image_index}.npy")
            np.save(transformation_path, transformation_matrix)

            aligned_offsets.append((pad_top, pad_left))
            all_pad_tops.append(pad_top)
            all_pad_lefts.append(pad_left)

            # Update progress saat menyelaraskan dan cropping
            current_step += 1
            if update_progress:
                update_progress(current_step, total_steps, f"Menyelaraskan dan cropping gambar {image_index}/{total_images}")

            image_index += 1

    # Calculate global crop region
    global_crop_top = max(all_pad_tops)
    global_crop_left = max(all_pad_lefts)
    global_crop_bottom = min(offset[0] + h for offset in aligned_offsets)
    global_crop_right = min(offset[1] + w for offset in aligned_offsets)

    if global_crop_bottom <= global_crop_top or global_crop_right <= global_crop_left:
        print("Crop region global tidak valid. Tidak ada overlap yang cukup.")
        return

    # Phase 2: Alignment and saving cropped images
    with h5py.File(processor.hdf5_path, "w", libver="latest") as h5f:
        cropped_base = base_image[global_crop_top:global_crop_bottom, global_crop_left:global_crop_right]
        h5f.create_dataset("image_0", data=cropped_base, compression="lzf")
        print("Gambar 0 disimpan ke dataset image_0.")

        image_index = 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for batch_idx in range(batch_count):
                if stop_requested and stop_requested():
                    break

                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, len(remaining_paths))
                batch_paths = remaining_paths[start_idx:end_idx]
                batch_images = load_images_from_paths(batch_paths, stop_requested)
                if not batch_images:
                    continue

                for target_image in batch_images:
                    if stop_requested and stop_requested():
                        print("Proses dihentikan oleh pengguna.")
                        break

                    transformation_path = os.path.join(transformation_dir, f"transformation_image_{image_index}.npy")
                    if not os.path.exists(transformation_path):
                        print(f"File transformation matrix tidak ditemukan untuk gambar ke-{image_index}")
                        image_index += 1
                        continue

                    H = np.load(transformation_path)
                    compensated, _ = processor.compensate_motion(target_image, None, None, transformation_matrix=H)
                    cropped = compensated[global_crop_top:global_crop_bottom, global_crop_left:global_crop_right]
                    dataset_name = f"image_{image_index}"
                    futures.append(executor.submit(save_to_hdf5, h5f, dataset_name, cropped))

                    current_step += 1
                    if update_progress:
                        update_progress(current_step, total_steps, f"Menyimpan gambar {image_index}/{total_images}")

                    image_index += 1
            
            for future in futures:
                future.result()

    if update_progress:
        update_progress(total_steps, total_steps, "Penyimpanan gambar yang telah di-align selesai.")
    print("Pemrosesan selesai dan semua gambar telah disimpan ke HDF5.")

def process_without_cropping(processor, base_image, remaining_paths, batch_count, batch_size,
                               transformation_dir, update_progress, total_images, stop_requested):
    # Phase 1: Estimate transformations
    image_index = 1
    total_steps = total_images * 2  # Total langkah (kalkulasi + penyimpanan)
    current_step = 0  # Inisialisasi progress

    for batch_idx in range(batch_count):
        if stop_requested and stop_requested():
            break

        start_idx = batch_idx * batch_size
        end_idx = min((batch_idx + 1) * batch_size, len(remaining_paths))
        batch_paths = remaining_paths[start_idx:end_idx]
        batch_images = load_images_from_paths(batch_paths, stop_requested)
        if not batch_images:
            continue

        for target_image in batch_images:
            if stop_requested and stop_requested():
                print("Proses dihentikan oleh pengguna.")
                break

            base_pts, target_pts = processor.calculate_global_motion(base_image, target_image)
            if base_pts is None or target_pts is None:
                print(f"Global motion tidak dapat dihitung untuk gambar ke-{image_index}")
                image_index += 1
                continue

            # Definisikan corners sebagai array float32 dengan bentuk (4,2)
            corners = np.array([[0, 0],
                                [base_image.shape[1] - 1, 0],
                                [base_image.shape[1] - 1, base_image.shape[0] - 1],
                                [0, base_image.shape[0] - 1]], dtype=np.float32)

            transformation_matrix, _ = estimate_transformation(
                'homography', base_pts, target_pts, corners
            )

            if transformation_matrix is None:
                print(f"Estimasi homografi gagal untuk gambar ke-{image_index}")
                image_index += 1
                continue

            # Simpan matriks transformasi
            transformation_path = os.path.join(transformation_dir, f"transformation_image_{image_index}.npy")
            np.save(transformation_path, transformation_matrix)

            # Update progress
            current_step += 1
            if update_progress:
                update_progress(current_step, total_steps, f"Menyelaraskan gambar {image_index}/{total_images}")

            image_index += 1

    # Phase 2: Apply transformation and save images without cropping
    with h5py.File(processor.hdf5_path, "w", libver="latest") as h5f:
        h5f.create_dataset("image_0", data=base_image, compression="lzf")
        print("Gambar 0 disimpan ke dataset image_0.")

        image_index = 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for batch_idx in range(batch_count):
                if stop_requested and stop_requested():
                    break

                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, len(remaining_paths))
                batch_paths = remaining_paths[start_idx:end_idx]
                batch_images = load_images_from_paths(batch_paths, stop_requested)
                if not batch_images:
                    continue

                for target_image in batch_images:
                    if stop_requested and stop_requested():
                        print("Proses dihentikan oleh pengguna.")
                        break

                    transformation_path = os.path.join(transformation_dir, f"transformation_image_{image_index}.npy")
                    if not os.path.exists(transformation_path):
                        print(f"File transformation matrix tidak ditemukan untuk gambar ke-{image_index}")
                        image_index += 1
                        continue

                    H = np.load(transformation_path)
                    # Langsung terapkan warping tanpa padding
                    compensated = cv2.warpPerspective(target_image, H, 
                                                      (target_image.shape[1], target_image.shape[0]))

                    dataset_name = f"image_{image_index}"
                    futures.append(executor.submit(save_to_hdf5, h5f, dataset_name, compensated))

                    current_step += 1
                    if update_progress:
                        update_progress(current_step, total_steps, f"Menyimpan gambar {image_index}/{total_images}")

                    image_index += 1
            
            for future in futures:
                future.result()

    if update_progress:
        update_progress(total_steps, total_steps, "Penyimpanan gambar yang telah di-align selesai.")
    print("Pemrosesan selesai dan semua gambar telah disimpan ke HDF5.")
    
# ------------------------------ Main Process ---------------------------------- #
## ----------------  Feature-based Alignment ---------------- ##

