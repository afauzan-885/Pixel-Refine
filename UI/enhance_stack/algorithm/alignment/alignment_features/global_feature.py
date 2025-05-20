import concurrent.futures 
from functools import lru_cache
import json
import os
import concurrent
import shutil
import sqlite3
import subprocess
import time
import cv2
import exifread
import numpy as np
import rawpy
import tifffile
from PIL import Image
try:
    import rawpy
    RAWPY_AVAILABLE = True
except ImportError:
    RAWPY_AVAILABLE = False
from UI.settings.General.Language import language_config

# ====================== Preprocessing ====================== #
@lru_cache(maxsize=None)
def gaussian_window(size, sigma_scale=1/6): 
        """Menghasilkan jendela Gaussian 2D [0, 1] float32 C-contiguous."""
        rows, cols = size
        if rows <= 0 or cols <= 0:
            return np.zeros((0, 0), dtype=np.float32)
        sigma_y = max(rows * sigma_scale, 1e-6)
        sigma_x = max(cols * sigma_scale, 1e-6)
        y = np.arange(0, rows, 1, float) - (rows - 1) / 2
        x = np.arange(0, cols, 1, float) - (cols - 1) / 2
        gaussian_y = np.exp(-y**2 / (2 * sigma_y**2 + 1e-12))
        gaussian_x = np.exp(-x**2 / (2 * sigma_x**2 + 1e-12))
        window = np.outer(gaussian_y, gaussian_x)
        max_val = window.max()
        if max_val > 1e-6:
             window = window / max_val
        else:
             window = np.zeros_like(window)
        return np.ascontiguousarray(window.astype(np.float32))

    
def normalize_image(image, dtype): 
        """
        Normalisasi gambar ke range [0, 1] float32 berdasarkan tipe data asli.
        Mempertahankan kecerahan relatif antar frame. Menghasilkan C-contiguous array.
        """
        try:
            scale = np.float32(np.iinfo(dtype).max)
        except ValueError:
            if np.issubdtype(dtype, np.floating):
                scale = 1.0
            else:
                msg = language_config.DATA_TYPE_NOT_SUPPORTED.format(dtype) if hasattr(language_config, 'DATA_TYPE_NOT_SUPPORTED') else f"Data type not supported for normalization: {dtype}"
                raise TypeError(msg)


        image_float = np.ascontiguousarray(image.astype(np.float32))

        if scale > 1e-6: 
            norm_image = image_float / scale
        else:
             norm_image = image_float 

        if image.ndim == 2: 
            norm_image = np.stack((norm_image,) * 3, axis=-1)
       
        return np.ascontiguousarray(norm_image.astype(np.float32)) 

# ====================== End Preprocessing ====================== #

# ====================== Load and Saving Process ====================== #
def get_all_image_paths_for_single_process(db_path: str)-> list:
        """
    Retrieves all image paths for single process from the specified database,
    ORDERED by reference status first, then alphabetically by image path.

    Args:
        db_path: The full path to the SQLite database file.

    Returns:
        A list of image paths in the correct order, or an empty list on error.
    """
        try:
            if not os.path.isfile(db_path):
                return []

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                sql_query = """
                    SELECT i.path
                    FROM images i
                    JOIN single_process_image spi ON i.id = spi.image_id_single
                    ORDER BY
                        spi.is_reference DESC, -- Referensi (is_reference=1) selalu di atas
                        i.path ASC             -- Urutkan sisanya (is_reference=0) berdasarkan nama file
                """
                cursor.execute(sql_query)
                image_paths = [row[0] for row in cursor.fetchall()]

                if not image_paths:
                    pass
                return image_paths

        except sqlite3.Error as e:
            return [] 
        except Exception as e:
            return []
        
def _prepare_image_path(original_path, temp_dir):
    """
    Memeriksa path gambar. Jika DNG/RAW dan rawpy tersedia, proses,
    simpan sebagai TIFF sementara, dan kembalikan path sementara.
    Jika tidak, kembalikan path asli.
    Mengembalikan None jika terjadi error atau file RAW dilewati.
    """
    try:
        _, ext = os.path.splitext(original_path)
        ext = ext.lower()

        raw_extensions = {'.dng', '.cr2', '.nef', '.arw', '.orf', '.rw2', '.pef', '.srw'}

        if ext in raw_extensions:
            if not RAWPY_AVAILABLE:
                return None 

            try:
                with rawpy.imread(original_path) as raw:
                    gamma_setting = (2.5, 15.92) # Natural Gamma
                    rgb = raw.postprocess(use_camera_wb=True, gamma=gamma_setting, output_bps=16,
                                          bad_pixels_path=None,output_color=rawpy.ColorSpace.sRGB,
                                          chromatic_aberration=None, highlight_mode=rawpy.HighlightMode.Blend)

                base_name = os.path.basename(original_path)
                temp_filename = f"{os.path.splitext(base_name)[0]}_{int(time.time_ns())}.tiff"
                temp_path = os.path.join(temp_dir, temp_filename)
    
                bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                success = cv2.imwrite(temp_path, bgr)

                if success:
                    return temp_path 
                else:
                    return None

            except rawpy.LibRawError as e:
                return None
            except Exception as e:
                return None

        else:
            if os.path.exists(original_path):
                return original_path
            else:
                return None

    except Exception as e:
        return None 
    
def load_images_from_paths(image_paths, stop_requested=None):
    session_id = f"imgproc_{os.getpid()}_{int(time.time_ns())}"
    temp_dir = os.path.join("database", "align", session_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    processed_paths_futures = []
    non_raw_paths = []
    raw_extensions = {'.dng', '.cr2', '.nef', '.arw', '.orf', '.rw2', '.pef', '.srw'}
    num_threads = os.cpu_count() or 4 

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor_prepare:
            for path in image_paths:
                if stop_requested and stop_requested():
                    break

                _, ext = os.path.splitext(path)
                ext = ext.lower()

                if ext in raw_extensions:
                    future = executor_prepare.submit(_prepare_image_path, path, temp_dir)
                    processed_paths_futures.append(future)
                else:
                    if os.path.exists(path):
                        non_raw_paths.append(path) 
                    else:
                        pass

            temp_processed_raw_paths = []
            for future in concurrent.futures.as_completed(processed_paths_futures):
                if stop_requested and stop_requested():
                    break
                try:
                    result_path = future.result() # Bisa None jika gagal
                    if result_path:
                        temp_processed_raw_paths.append(result_path)
                except Exception as e:
                    print(f"Error saat mengambil hasil future _prepare_image_path: {e}")
            
            if stop_requested and stop_requested(): # Cek lagi sebelum lanjut
                return []


        all_paths_to_load = temp_processed_raw_paths + non_raw_paths
       

        images = []
        if not all_paths_to_load:
            return images

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor_load:
            future_to_path = {executor_load.submit(cv2.imread, p, cv2.IMREAD_UNCHANGED): p for p in all_paths_to_load}

            for future in concurrent.futures.as_completed(future_to_path):
                if stop_requested and stop_requested():
                    break
                
                original_input_path = future_to_path[future]
                try:
                    img = future.result()
                    if img is not None:
                        images.append(img)
                    else:
                      pass
                except Exception as e:
                    print(f"Error saat memuat gambar {original_input_path}: {e}")
        
        return images

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
                
def save_special_jpg_and_png(
    src_path: str,
    dst_path: str,
    reference_image_path: str = None,
    quality: int = 95,
    optimize: bool = True
    ) -> str:
    img_np = tifffile.imread(src_path)
    
    if img_np.dtype == 'uint16':
        img_np = (img_np / 256).astype('uint8')
    
    img = Image.fromarray(img_np)

    save_kwargs = {
        'quality': quality,
        'optimize': optimize,
        'subsampling': 0
    }

    ext = os.path.splitext(dst_path)[1].lower()
    img.save(dst_path, **save_kwargs)

    if reference_image_path and os.path.exists(reference_image_path):
        try:
            subprocess.run(
                [
                    "exiftool",
                    "-overwrite_original",
                    "-TagsFromFile", reference_image_path,
                    dst_path
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError as e:
            pass
    
    return dst_path
        
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

    # Simpan gambar dengan OpenCV tanpa kompresi
    cv2.imwrite(file_path, image)
    
    # multithreading untuk menjalankan exiftool
    try:
        num_threads = os.cpu_count() or 4  # Default to 4 if os.cpu_count() returns None
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
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