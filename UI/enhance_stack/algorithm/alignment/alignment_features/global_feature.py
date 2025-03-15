import concurrent.futures 
import json
import os
import concurrent
import subprocess
import cv2
import exifread
import numpy as np

from UI.settings.General.Language import language_config


# ====================== Load and Saving Process ====================== #
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


def save_to_hdf5(h5f, dataset_name, cropped, metadata=None):
    """
    Save images (array) into HDF5 and embed metadata as attributes using multithreading.

    Parameters:
    - h5f: opened HDF5 file object
    - dataset_name: name of dataset to be created
    - cropped: array of images to be saved
    - metadata: dictionary containing metadata or EXIF of images
    """
    # Buat dataset dengan bentuk dan tipe yang sesuai
    dset = h5f.create_dataset(dataset_name, shape=cropped.shape, dtype=cropped.dtype)

    # Fungsi untuk menulis chunk pada dataset
    def write_chunk(start, end):
        dset[start:end] = cropped[start:end]

    num_threads = os.cpu_count() or 4
    total_items = cropped.shape[0]
    chunk_size = total_items // num_threads if total_items >= num_threads else total_items
    # Gunakan multithreading untuk menulis dataset secara paralel
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        start = 0
        while start < total_items:
            end = start + chunk_size
            if end > total_items:
                end = total_items
            futures.append(executor.submit(write_chunk, start, end))
            start = end
        concurrent.futures.wait(futures)

    if metadata is not None:
        # Simpan metadata sebagai atribut (dalam format JSON)
        dset.attrs['metadata'] = json.dumps(metadata)
        
        
def save_align_to_folder(image, index, original_path, align_folder=None, load_config_func=None):
    """
    Menyimpan gambar dalam format TIFF ke folder yang ditentukan,
    kemudian mengembalikan metadata dari file asli ke file output menggunakan exiftool
    """
    
    # Gunakan nilai default dari config jika align_folder tidak diberikan
    if align_folder is None:
        if load_config_func is None:
            raise ValueError("Fungsi konfigurasi harus diberikan jika align_folder tidak diatur.")
        config = load_config_func()
        align_folder = config.get("align_folder")

    os.makedirs(align_folder, exist_ok=True)
    
    # Ambil nama file tanpa ekstensi dari original_path
    base_name = os.path.splitext(os.path.basename(original_path))[0]
    file_path = os.path.join(align_folder, f"{base_name}_align.tiff")

    # Simpan gambar dengan OpenCV dengan kompresi TIFF minimal
    cv2.imwrite(file_path, image, [cv2.IMWRITE_TIFF_COMPRESSION, 1])
    
    # multithreading untuk menjalankan exiftool
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future = executor.submit(
                subprocess.run,
                ["exiftool", "-overwrite_original", "-TagsFromFile", original_path, file_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Tunggu hingga proses selesai
            future.result()
        # print(f"Metadata successfully restored to {file_path}")
    except Exception as e:
        print(f"Error restoring metadata to {file_path}: {e}")
    
    return file_path

def save_image(image, output_path, reference_image_path=None):
        """
        Menyimpan gambar ke output_path dengan cv2.imwrite, lalu 
        mengembalikan metadata dari gambar referensi (reference_image_path) ke file yang disimpan.
        
        Parameter:
        - image: array gambar yang akan disimpan
        - output_path: path file output (misalnya, TIFF)
        - reference_image_path: path gambar referensi untuk penyalinan metadata
        """
        # Simpan gambar menggunakan OpenCV
        cv2.imwrite(output_path, image)
        
        # Jika reference_image_path disediakan, gunakan exiftool untuk mengembalikan metadata
        if reference_image_path is not None and os.path.exists(reference_image_path):
            try:
                subprocess.run(
                    ["exiftool", "-overwrite_original", "-TagsFromFile", reference_image_path, output_path],
                    check=True
                )
                # print(f"Metadata successfully restored {reference_image_path} to {output_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error restoring metadata to {output_path}: {e}")
        return output_path
# ====================== Load and Saving Process ====================== #

# ================ Fungsi Ekstraksi Metadata ====================== #
def extract_exif(image_path):
    """
    Mengambil metadata EXIF dari file gambar menggunakan exifread.
    Mengembalikan dictionary dengan data EXIF dan path file.
    """
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)
    # Ubah setiap value ke string agar dapat di-serialisasi ke JSON
    exif_data = {tag: str(value) for tag, value in tags.items()}
    exif_data["file"] = image_path
    return exif_data

def extract_all_metadata(image_paths, metadata_file="metadata.json"):
    """
    Mengekstrak metadata dari seluruh image paths dan menyimpannya ke file JSON.
    Jika file metadata sudah ada, data baru akan ditambahkan (tidak overwrite).
    """
    metadata_list = []
    for path in image_paths:
        try:
            metadata = extract_exif(path)
            metadata_list.append(metadata)
        except Exception as e:
            print(f"Failed to extract metadata from {path}: {e}")
    
    # Jika file sudah ada, muat data yang sudah tersimpan
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, "r") as f:
                existing_data = json.load(f)
        except Exception as e:
            print(f"Failed to read metadata file: {e}")
            existing_data = []
    else:
        existing_data = []
    
    # Tambahkan metadata baru ke data yang sudah ada
    existing_data.extend(metadata_list)
    
    # Simpan kembali ke file JSON dengan penulisan indent agar mudah dibaca
    with open(metadata_file, "w") as f:
        json.dump(existing_data, f, indent=4)
    
    return existing_data
    
## ====================== Feature-based Alignment ====================== ##

# ---------------- Calculate Global Motion Process ---------------- #
# ---------------- Calculate Global Motion Process ---------------- #


## ---------------- Compensate Motion Process ---------------- ##
## ---------------- Compensate Motion Process ---------------- ##


## ---------------- Calculate Global Crop Process ---------------- ##
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
        print(language_config.FAIL_CROPPING_PROCESS)
        return None

    return crop_x, crop_y, crop_w, crop_h

def crop_image(image, crop_bounds):
    """Melakukan cropping pada gambar sesuai batas crop yang diberikan."""
    crop_x, crop_y, crop_w, crop_h = crop_bounds
    return image[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]

## ---------------- Calculate Global Crop Process ---------------- ##

# ====================== Main Process ====================== #
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