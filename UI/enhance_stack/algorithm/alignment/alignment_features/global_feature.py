# =========================================================================
# === 1. IMPORTS & KONFIGURASI GLOBAL
# =========================================================================
import concurrent.futures 
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import gc
import math
import queue
import threading
import cv2
import json
import os
import sqlite3
import subprocess
import exifread
import h5py
import numpy as np
import tifffile
from PIL import Image

try:
    import rawpy
    RAWPY_AVAILABLE = True
except ImportError:
    RAWPY_AVAILABLE = False
    
# from UI.enhance_stack.algorithm.model_trainer.mobile_net_v2 import AlphaGenerator
from UI.settings.General.Language import language_config


# =========================================================================
# === 2. MANAJEMEN DATA & I/O (Database, File, Metadata)
# =========================================================================

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

def _prepare_image_array_from_raw(original_path):
    """
    Membaca gambar RAW dan mengembalikan array NumPy BGR.
    Jika gagal atau bukan RAW, mengembalikan None.
    """
    try:
        if not RAWPY_AVAILABLE:
            return None

        with rawpy.imread(original_path) as raw:
            gamma_setting = (2.5, 15.92)  # Natural Gamma
            rgb = raw.postprocess(
                use_camera_wb=True,
                gamma=gamma_setting,
                output_bps=16,
                bad_pixels_path=None,
                output_color=rawpy.ColorSpace.sRGB,
                chromatic_aberration=None,
                highlight_mode=rawpy.HighlightMode.Blend
            )

        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        return bgr  # langsung return array, bukan path
    except Exception as e:
        print(f"Error membaca RAW file {original_path}: {e}")
        return None
 
def load_images_from_paths(image_paths, stop_requested=None):
    images = []
    raw_extensions = {'.dng', '.cr2', '.nef', '.arw', '.orf', '.rw2', '.pef', '.srw'}
    num_threads = os.cpu_count() or 4

    raw_futures = []
    standard_futures = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for path in image_paths:
            if stop_requested and stop_requested():
                break

            _, ext = os.path.splitext(path)
            ext = ext.lower()

            if ext in raw_extensions:
                if os.path.exists(path):
                    future = executor.submit(_prepare_image_array_from_raw, path)
                    raw_futures.append(future)
            else:
                if os.path.exists(path):
                    future = executor.submit(cv2.imread, path, cv2.IMREAD_UNCHANGED)
                    standard_futures.append(future)

        # Ambil hasil dari gambar RAW
        for future in concurrent.futures.as_completed(raw_futures):
            if stop_requested and stop_requested():
                break
            try:
                img = future.result()
                if img is not None:
                    images.append(img)
            except Exception as e:
                print(f"Error loading RAW image: {e}")

        # Ambil hasil dari gambar biasa
        for future in concurrent.futures.as_completed(standard_futures):
            if stop_requested and stop_requested():
                break
            try:
                img = future.result()
                if img is not None:
                    images.append(img)
            except Exception as e:
                print(f"Error loading standard image: {e}")

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
    Menyimpan gambar dengan menyinkronkan data pikselnya dengan metadata orientasi
    dari gambar referensi, lalu menyalin semua metadata menggunakan exiftool.
    Akurasi metadata adalah prioritas utama.
    """
    try:
        image_to_save = image.copy()
        if reference_image_path is None or not os.path.exists(reference_image_path):
            cv2.imwrite(output_path, image_to_save)
            return output_path

        target_orientation = 1
        try:
            result = subprocess.run(["exiftool", "-n", "-Orientation", reference_image_path], capture_output=True, text=True, check=True)
            output_str = result.stdout.strip()
            if output_str:
                target_orientation = int(output_str.split(':')[-1].strip())
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            print(f"  Peringatan: Tidak dapat membaca orientasi dari '{reference_image_path}'.")

        if target_orientation == 3: image_to_save = cv2.rotate(image, cv2.ROTATE_180)
        elif target_orientation == 6: image_to_save = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif target_orientation == 8: image_to_save = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif target_orientation == 2: image_to_save = cv2.flip(image, 1)
        elif target_orientation == 4: image_to_save = cv2.flip(image, 0)
        
        success = cv2.imwrite(output_path, image_to_save)
        if not success:
            print(f"Error: OpenCV gagal menyimpan gambar ke '{output_path}'")
            return None

        try:
            subprocess.run(["exiftool", "-q", "-overwrite_original", "-TagsFromFile", reference_image_path, output_path], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"  Peringatan: Gagal menyalin metadata ke '{output_path}'. Error: {e}")

        return output_path
    except Exception as e:
        print(f"Error fatal saat menyimpan gambar ke '{output_path}': {e}")
        return None

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


# =========================================================================
# === 3. PRA-PEMROSESAN & UTILITAS GAMBAR
# =========================================================================

def convert_to_uint8(image):
    """
    Mengonversi gambar dari tipe data apa pun ke uint8 dengan cara yang kuat,
    memastikan kontras global dimaksimalkan menggunakan normalisasi min-max.
    Ini adalah langkah krusial untuk data dengan kedalaman bit tinggi seperti uint16.

    Args:
        image: Gambar input (berwarna atau grayscale).

    Returns:
        Gambar uint8 dengan kontras yang telah diregangkan.
    """
    # Jika sudah 8-bit, tidak perlu melakukan apa-apa.
    if image.dtype == np.uint8:
        return image

    # Untuk SEMUA tipe data lain (uint16, float32, dll.), gunakan
    # cv2.normalize dengan NORM_MINMAX. Ini akan meregangkan rentang dinamis
    # yang ada (misalnya, nilai piksel dari 1000 hingga 5000) ke rentang
    # penuh 0-255. Inilah yang membuat hasilnya kuat.
    
    # Periksa apakah gambar memiliki rentang yang valid untuk dinormalisasi
    min_val, max_val = np.min(image), np.max(image)
    if max_val - min_val < 1e-6: # Jika gambar hampir datar (misal, semua hitam)
        # Hindari pembagian dengan nol, kembalikan gambar dengan nilai rata-rata
        return np.full(image.shape, int(np.mean(image)), dtype=np.uint8)

    normalized_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    
    return normalized_image.astype(np.uint8)
    
def enhance_contrast_and_convert_8bit(image):
    """
    Meningkatkan kontras pada gambar berwarna dengan cara yang kuat dan andal.
    
    Pertama, ia memastikan gambar dikonversi ke 8-bit dengan kontras global
    yang optimal. Kemudian, ia menerapkan CLAHE pada channel Luminance (L) 
    di ruang warna LAB untuk menyempurnakan kontras lokal tanpa merusak warna.

    Args:
        image: Gambar input berwarna (kedalaman bit apa pun).

    Returns:
        Gambar BGR 8-bit dengan kontras yang telah ditingkatkan.
    """
    # Langkah 1: Gunakan fungsi konversi 8-bit kita yang baru dan kuat.
    # Ini memastikan kita memulai dengan gambar berkualitas tinggi.
    image_8bit = convert_to_uint8(image)

    # Pastikan input adalah gambar berwarna untuk konversi LAB
    if image_8bit.ndim == 2:
        image_8bit = cv2.cvtColor(image_8bit, cv2.COLOR_GRAY2BGR)

    # Langkah 2: Terapkan CLAHE di ruang warna LAB (logika ini sudah bagus)
    lab = cv2.cvtColor(image_8bit, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)) # Gunakan grid 8x8 seperti di AKAZE Anda
    cl = clahe.apply(l_channel)

    merged_channels = cv2.merge((cl, a_channel, b_channel))
    enhanced_image = cv2.cvtColor(merged_channels, cv2.COLOR_LAB2BGR)
    
    return enhanced_image

def resize_with_padding(img, target_size, pad_color=(0, 0, 0)):
    h, w = img.shape[:2]
    target_h, target_w = target_size

    if (h, w) == (target_h, target_w):
        return img.copy()

    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)

    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    delta_w = target_w - new_w
    delta_h = target_h - new_h
    top, bottom = delta_h // 2, delta_h - delta_h // 2
    left, right = delta_w // 2, delta_w - delta_w // 2

    padded = cv2.copyMakeBorder(resized, top, bottom, left, right,
                                 borderType=cv2.BORDER_CONSTANT, value=pad_color)
    return padded

def resize_all_with_padding(images, method="median", verbose=False,
                            pad_color=(0, 0, 0), return_original_sizes=False):
    """
    Resize + pad all images to the same size using letterbox strategy.

    Returns:
        By default: resized_images, (h, w)
        If return_original_sizes=True: resized_images, (h, w), original_sizes
    """
    if not images:
        raise ValueError("Image list is empty")

    original_sizes = []
    h_list, w_list = [], []
    for img in images:
        if img is not None:
            h, w = img.shape[:2]
            original_sizes.append((h, w))
            h_list.append(h)
            w_list.append(w)
        else:
            raise ValueError("One of the images is None")

    if all(size == original_sizes[0] for size in original_sizes):
        if verbose:
            print("All images already have same dimensions. Skipping resize.")
        result = (images, original_sizes[0])
        return result if not return_original_sizes else (*result, original_sizes)

    # Determine target size
    if method == "min":
        target_h, target_w = min(h_list), min(w_list)
    elif method == "max":
        target_h, target_w = max(h_list), max(w_list)
    elif method == "median":
        target_h = sorted(h_list)[len(h_list) // 2]
        target_w = sorted(w_list)[len(w_list) // 2]
    else:
        raise ValueError("Unsupported resize method. Use 'min', 'max', or 'median'.")

    if verbose:
        print(f"Resizing all images to {target_w}x{target_h} using method: {method}")

    resized_images = []
    for img, (h, w) in zip(images, original_sizes):
        if h == target_h and w == target_w:
            resized_images.append(img)
        else:
            resized_images.append(
                resize_with_padding(img, (target_h, target_w), pad_color=pad_color)
            )

    result = (resized_images, (target_h, target_w))
    return result if not return_original_sizes else (*result, original_sizes)

@lru_cache(maxsize=3200)
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

# =========================================================================
# === 4. LOGIKA INTI ALIGNMENT & FITUR
# =========================================================================

# Di sinilah Anda akan menempatkan fungsi-fungsi seperti:
# - calculate_global_motion_AKAZE(...)
# - calculate_global_motion_ORB(...)
# - calculate_global_motion_LightGlue(...)
# - compensate_motion(...)

def filter_keypoints_spatially(keypoints, descriptors, image_shape, grid_size=(5, 5), max_kps_per_cell=80):
        """
        Menyaring keypoints untuk memastikan distribusi spasial yang merata.
        
        Metode ini membagi gambar menjadi sebuah grid, lalu mengambil N keypoint
        terbaik (berdasarkan 'response') dari setiap sel grid. Ini mencegah
        penumpukan keypoint di satu area dan memastikan fitur representatif
        dari seluruh gambar.

        Args:
            keypoints: Daftar keypoint mentah dari detektor.
            descriptors: Deskriptor yang sesuai dengan keypoint.
            image_shape: Bentuk gambar (h, w) untuk menentukan batas grid.
            grid_size: Tuple (cols, rows) untuk grid.
            max_kps_per_cell: Jumlah maksimum keypoint yang diambil dari setiap sel.

        Returns:
            Tuple (filtered_keypoints, filtered_descriptors)
        """
        if not keypoints or descriptors is None:
            return [], None
            
        h, w = image_shape
        rows, cols = grid_size
        
        # Hindari pembagian dengan nol jika grid tidak valid
        if cols == 0 or rows == 0:
            return keypoints, descriptors

        cell_w = w // cols
        cell_h = h // rows
        
        # Buat grid untuk menampung keypoint per sel
        grid_cells = [[] for _ in range(rows * cols)]
        
        # Masukkan setiap keypoint ke dalam sel grid yang sesuai
        for i, kp in enumerate(keypoints):
            # Hindari error jika koordinat di luar gambar
            if not (0 <= kp.pt[0] < w and 0 <= kp.pt[1] < h):
                continue

            col_idx = int(kp.pt[0] // cell_w)
            row_idx = int(kp.pt[1] // cell_h)
            
            # Pastikan tidak keluar dari batas karena pembulatan
            col_idx = min(col_idx, cols - 1)
            row_idx = min(row_idx, rows - 1)
            
            grid_idx = row_idx * cols + col_idx
            grid_cells[grid_idx].append((kp, i)) # Simpan keypoint dan indeks aslinya

        # Ambil keypoint terbaik dari setiap sel
        final_keypoints = []
        final_desc_indices = []

        for cell in grid_cells:
            if not cell:
                continue
            
            # Urutkan keypoint di dalam sel berdasarkan response (terbaik di atas)
            cell.sort(key=lambda item: item[0].response, reverse=True)
            
            # Ambil N teratas (atau semua jika lebih sedikit)
            for kp, original_idx in cell[:max_kps_per_cell]:
                final_keypoints.append(kp)
                final_desc_indices.append(original_idx)

        if not final_desc_indices:
            return [], None

        # Ambil deskriptor yang sesuai menggunakan indeks yang telah difilter
        final_descriptors = descriptors[final_desc_indices]
        
        return final_keypoints, final_descriptors
    
def deduplicate_keypoints(mkptsL, mkptsR, scores, image_shape, distance_thresh=10):
    """
    Menghilangkan duplikat keypoint yang mungkin muncul dari area tumpang tindih.
    
    Hanya keypoint dengan skor kepercayaan tertinggi dalam radius tertentu yang dipertahankan.
    
    Args:
        mkptsL, mkptsR: Array keypoint yang cocok.
        scores: Skor kepercayaan untuk setiap pasangan match.
        image_shape: Bentuk gambar penuh untuk membuat grid spasial.
        distance_thresh: Jarak piksel untuk dianggap sebagai duplikat.

    Returns:
        Tuple (dedup_mkptsL, dedup_mkptsR, dedup_scores)
    """
    if len(mkptsL) == 0:
        return np.array([]), np.array([]), np.array([])

    # Pastikan input adalah array (N, 2)
    if len(mkptsL.shape) != 2 or mkptsL.shape[1] != 2:
        # Jika bentuknya (N, 1, 2), ubah menjadi (N, 2) untuk diproses
        if len(mkptsL.shape) == 3 and mkptsL.shape[1] == 1 and mkptsL.shape[2] == 2:
            mkptsL = mkptsL.reshape(-1, 2)
            mkptsR = mkptsR.reshape(-1, 2)
        else:
            raise ValueError(f"Input mkptsL harus berbentuk (N, 2), tetapi ditemukan {mkptsL.shape}")
            
    h, w = image_shape[:2]
    cols = int(w / distance_thresh)
    rows = int(h / distance_thresh)
    
    grid = {}
    
    sorted_indices = np.argsort(scores)[::-1]

    kept_indices = []
    
    for idx in sorted_indices:
        pt = mkptsL[idx]  
        
        grid_col = int(pt[0] / distance_thresh)
        grid_row = int(pt[1] / distance_thresh)
        
        is_duplicate = False
        for r_offset in range(-1, 2):
            for c_offset in range(-1, 2):
                cell_key = (grid_row + r_offset, grid_col + c_offset)
                if cell_key in grid:
                    if np.linalg.norm(pt - grid[cell_key]) < distance_thresh: # SEKARANG: Menghitung jarak Euclidean yang benar
                        is_duplicate = True
                        break
            if is_duplicate:
                break
        
        if not is_duplicate:
            kept_indices.append(idx)
            grid[(grid_row, grid_col)] = pt

    dedup_mkptsL = mkptsL[kept_indices]
    dedup_mkptsR = mkptsR[kept_indices]
    dedup_scores = scores[kept_indices]
    
    return dedup_mkptsL, dedup_mkptsR, dedup_scores

def do_warp_and_crop(image, matrix, pad, w, h, transformation_type):
        """
        Menerapkan padding, warping, dan cropping untuk menjaga tepi gambar.
        """
        try:
            # Terapkan padding ke gambar asli
            padded_image = cv2.copyMakeBorder(image, pad, pad, pad, pad, cv2.BORDER_REFLECT)
            
            target_w_padded = padded_image.shape[1]
            target_h_padded = padded_image.shape[0]
            
            interpolation_flag = cv2.INTER_LANCZOS4

            # Lakukan warping pada gambar yang sudah di-padding
            if transformation_type == 'homography':
                compensated_padded = cv2.warpPerspective(padded_image, matrix, (target_w_padded, target_h_padded), flags=interpolation_flag, borderMode=cv2.BORDER_REFLECT)
            else:
                compensated_padded = cv2.warpAffine(padded_image, matrix, (target_w_padded, target_h_padded), flags=interpolation_flag, borderMode=cv2.BORDER_REFLECT)

            # Lakukan cropping untuk kembali ke ukuran gambar asli
            # Pemeriksaan keamanan jika hasil warp lebih kecil dari yang diharapkan
            if pad + h > compensated_padded.shape[0] or pad + w > compensated_padded.shape[1]:
                 # Fallback: warp langsung tanpa menjaga tepi jika cropping tidak memungkinkan
                 if transformation_type == 'homography':
                     return cv2.warpPerspective(image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
                 else:
                     return cv2.warpAffine(image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
            else:
                 return compensated_padded[pad:pad+h, pad:pad+w]

        except (cv2.error, Exception):
            return None

def calculate_crop_parameters(matrix, w, h, transformation_type):
        """
        Fungsi statis untuk menghitung parameter padding yang diperlukan.
        
        Args:
            matrix (np.ndarray): Matriks transformasi (2x3 untuk affine, 3x3 untuk homography).
            w (int): Lebar gambar asli.
            h (int): Tinggi gambar asli.
            transformation_type (str): Tipe transformasi ('affine', 'homography', dll.).

        Returns:
            int: Nilai padding seragam yang diperlukan, atau None jika terjadi kesalahan.
        """
        corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(-1, 1, 2)
        try:
            if transformation_type == 'homography':
                if matrix.shape != (3, 3): return None
                transformed_corners = cv2.perspectiveTransform(corners, matrix)
            else: # affine, similarity, euclidean
                if matrix.shape != (2, 3): return None
                transformed_corners = cv2.transform(corners, matrix)

            if transformed_corners is None:
                return None

            transformed_corners = transformed_corners.reshape(-1, 2)
            min_x, min_y = transformed_corners.min(axis=0)
            max_x, max_y = transformed_corners.max(axis=0)
            
            # Hitung padding yang diperlukan untuk setiap sisi
            pad_x = max(0, int(np.ceil(max_x - w)))
            pad_y = max(0, int(np.ceil(max_y - h)))
            pad_left = max(0, int(np.ceil(-min_x)))
            pad_top = max(0, int(np.ceil(-min_y)))

            # Gunakan nilai padding terbesar untuk memastikan semua tepi masuk
            pad = max(pad_x, pad_y, pad_left, pad_top)
            return pad

        except Exception:
            return None
    

# =========================================================================
# === 5. LOGIKA CROPPING GLOBAL
# =========================================================================

def compute_transform_bounds(transform, w, h, transformation_type):
    i, base_points, target_points = transform
    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(-1, 1, 2)

    if transformation_type == 'homography':
        matrix, mask = cv2.findHomography(np.array(base_points), np.array(target_points), cv2.RANSAC)
    else:
        matrix, mask = cv2.estimateAffine2D(np.array(base_points), np.array(target_points), method=cv2.RANSAC)

    # Debugging jumlah keypoint dan inlier
    if matrix is None or mask is None:
        # print(f"[DEBUG] Transform #{i}: transform matrix is None. Total points: {len(base_points)}")
        return None
    else:
        inlier_count = int(mask.sum())
        total_points = len(base_points)
        # print(f"[DEBUG] Transform #{i}: total points = {total_points}, inliers = {inlier_count}")

    # Transform corners
    if transformation_type == 'homography':
        transformed_corners = cv2.perspectiveTransform(corners, matrix)
    else:
        transformed_corners = cv2.transform(corners, matrix)

    transformed_corners = transformed_corners.reshape(-1, 2)
    min_xy = transformed_corners.min(axis=0)
    max_xy = transformed_corners.max(axis=0)

    return min_xy, max_xy

def compute_global_crop(all_transforms, total_images, w, h, transformation_type='homography'):
    global_min_x = float('inf')
    global_min_y = float('inf')
    global_max_x = -float('inf')
    global_max_y = -float('inf')

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(compute_transform_bounds, transform, w, h, transformation_type)
                   for transform in all_transforms]

        for future in futures:
            result = future.result()
            if result is None:
                continue
            min_xy, max_xy = result
            min_x, min_y = min_xy
            max_x, max_y = max_xy

            global_min_x = min(global_min_x, min_x)
            global_min_y = min(global_min_y, min_y)
            global_max_x = max(global_max_x, max_x)
            global_max_y = max(global_max_y, max_y)

    crop_x = int(max(0, np.ceil(-global_min_x)))
    crop_y = int(max(0, np.ceil(-global_min_y)))
    crop_w = w - int(np.ceil(global_max_x - w)) - crop_x
    crop_h = h - int(np.ceil(global_max_y - h)) - crop_y

    if crop_w <= 0 or crop_h <= 0:
        print(language_config.FAIL_CROPPING_PROCESS)
        return None

    return crop_x, crop_y, crop_w, crop_h

def crop_image(image, crop_bounds):
    """Melakukan cropping pada gambar sesuai batas crop yang diberikan."""
    crop_x, crop_y, crop_w, crop_h = crop_bounds
    return image[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]


# =========================================================================
# === 6. PENYEMPURNAAN & PASCA-PEMROSESAN (Opsional)
# =========================================================================

def add_legend_heatmap(img, norm_values, labels=("Static (High Weight)", "Moving (Low Weight)"),
                       font_scale_info=1.7, thickness_info=2,
                       font_scale_label=1.2, thickness_label=2):
    h, w = img.shape[:2]
    legend_width = 1000
    legend_height = 500
    margin = 10
    bar_height = 20
    bar_padding = 50  # Jarak antara color bar dan label
    label_info_spacing = 100  # Jarak antara labels dan info_lines

    # Posisi pojok kiri bawah
    x0 = margin
    y1 = h - margin
    y0 = y1 - legend_height

    # Buat panel transparan
    overlay = img.copy()
    cv2.rectangle(overlay, (x0, y0), (x0 + legend_width, y1), (0, 0, 0), -1)
    alpha = 0.6
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

    # Buat color bar dengan step warna (diskrit)
    legend_bar = np.zeros((bar_height, legend_width, 3), dtype=np.uint8)
    num_steps = 15
    step_width = legend_width // num_steps
    for i in range(num_steps):
        val = int((i / (num_steps - 1)) * 255)
        color = cv2.applyColorMap(np.array([[val]], dtype=np.uint8), cv2.COLORMAP_JET)[0, 0]
        x_start = i * step_width
        x_end = (i + 1) * step_width if i < num_steps - 1 else legend_width
        legend_bar[:, x_start:x_end] = color
    img[y0 + 5: y0 + 5 + bar_height, x0: x0 + legend_width] = legend_bar

    # Font dan warna
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_color = (255, 255, 255)

    # Label kiri dan kanan di bawah color bar, dengan padding 50px
    label_y = y0 + 5 + bar_height + bar_padding
    cv2.putText(img, labels[0], (x0, label_y),
                font, font_scale_label, text_color, thickness_label, cv2.LINE_AA)
    text_size = cv2.getTextSize(labels[1], font, font_scale_label, thickness_label)[0]
    cv2.putText(img, labels[1], (x0 + legend_width - text_size[0], label_y),
                font, font_scale_label, text_color, thickness_label, cv2.LINE_AA)

    # Statistik
    high_thresh = 0.7
    low_thresh = 0.3
    percent_high = (norm_values > high_thresh).sum() / norm_values.size * 100
    percent_low = (norm_values < low_thresh).sum() / norm_values.size * 100
    mean_val = np.mean(norm_values)

    info_lines = [
        f"High: {percent_high:.1f}%",
        f"Low: {percent_low:.1f}%",
        f"Avg: {mean_val:.3f}"
    ]

    # Hitung tinggi font untuk spacing otomatis (berdasarkan font info)
    _, text_height = cv2.getTextSize("Ag", font, font_scale_info, thickness_info)[0]
    line_spacing = int(text_height * 1.4)

    # Tampilkan statistik di bawah label dengan tambahan jarak
    for i, line in enumerate(info_lines):
        y_text = label_y + label_info_spacing + line_spacing * (i + 1)
        cv2.putText(img, line, (x0, y_text),
                    font, font_scale_info, text_color, thickness_info, cv2.LINE_AA)

    return img

def temporal_consistency_refinement(weight_maps_all, weight_map_sum, save_temporal_std_path=None,
                                    max_boost=2.0, min_boost=0.5):
    if len(weight_maps_all) <= 1:
        return

    weight_stack = np.stack(weight_maps_all, axis=0)
    temporal_std = np.std(weight_stack, axis=0)
    temporal_mean = np.mean(weight_stack, axis=0)

    stability_score = temporal_mean / (temporal_std + 1e-6)
    median_stability = np.median(stability_score)
    std_stability = np.std(stability_score)

    # ✅ Vektorized sigmoid-style scaling
    delta = stability_score - median_stability
    scaling_factors = 1 + np.tanh(delta / (std_stability + 1e-6))
    scaling_factors = np.clip(scaling_factors, min_boost, max_boost)

    weight_map_sum *= scaling_factors

    if save_temporal_std_path:
        norm_std = (temporal_std - np.min(temporal_std)) / (np.max(temporal_std) - np.min(temporal_std) + 1e-8)
        heatmap_color = cv2.applyColorMap((norm_std * 255).astype(np.uint8), cv2.COLORMAP_JET)
        heatmap_with_legend = add_legend_heatmap(
            heatmap_color,
            norm_values=norm_std,
            labels=("Static (High Weight)", "Moving (Low Weight)")
        )
        os.makedirs(os.path.dirname(save_temporal_std_path), exist_ok=True)
        cv2.imwrite(save_temporal_std_path, heatmap_with_legend)

def optical_flow_refinement(
    current_weight_map, 
    prev_weight_map_ema, 
    optical_flow, 
    flow_confidence_map=None,
    alpha_base=0.1, 
    alpha_no_confidence=0.9,
    bilateral_d=9, 
    bilateral_sigma_color=0.05, 
    bilateral_sigma_space=75):
    """
    Menyempurnakan peta bobot menggunakan optical flow dengan cara yang lebih kuat dan robust.
    Fungsi ini menggabungkan Bilateral Filtering untuk menjaga tepi, dan menggunakan peta 
    kepercayaan optical flow untuk menangani oklusi dan area tidak akurat secara cerdas.

    Args:
        current_weight_map (np.ndarray): Peta bobot untuk frame saat ini (mentah atau dari AI).
        prev_weight_map_ema (np.ndarray): Peta bobot yang sudah disempurnakan dari frame sebelumnya (hasil EMA).
        optical_flow (np.ndarray): Vektor pergerakan dari frame sebelumnya ke frame saat ini.
        flow_confidence_map (np.ndarray, optional): Peta [0,1] yang menunjukkan kepercayaan pada
                                                    setiap vektor optical flow. Nilai 1 sangat percaya,
                                                    nilai 0 tidak percaya. Defaults to None.
        alpha_base (float): Faktor pencampuran dasar. Bobot untuk prev_weight_map_ema ketika 
                            kepercayaan tinggi. Nilai rendah berarti lebih stabil.
        alpha_no_confidence (float): Faktor pencampuran untuk current_weight_map ketika kepercayaan
                                     sangat rendah. Nilai tinggi (mendekati 1.0) akan lebih
                                     mengandalkan frame saat ini.
        bilateral_d, bilateral_sigma_color, bilateral_sigma_space: Parameter untuk Bilateral Filter.

    Returns:
        np.ndarray: Peta bobot yang telah disempurnakan.
    """
    if prev_weight_map_ema is None or optical_flow is None:
        return current_weight_map

    h, w = current_weight_map.shape
    
    # --- UPGRADE 1: Deteksi Area Tidak Valid Setelah Warping ---
    # Warp peta bobot dari frame sebelumnya ke posisi saat ini
    grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
    map_x = (grid_x - optical_flow[..., 0]).astype(np.float32)
    map_y = (grid_y - optical_flow[..., 1]).astype(np.float32)
    
    # Warp peta bobot historis
    warped_prev_ema = cv2.remap(
        prev_weight_map_ema, map_x, map_y, 
        interpolation=cv2.INTER_LINEAR, 
        borderMode=cv2.BORDER_REPLICATE
    )
    
    # Deteksi area disoklusi (piksel yang baru muncul dan tidak memiliki sumber di frame lama)
    warped_ones = cv2.remap(np.ones_like(prev_weight_map_ema), map_x, map_y, interpolation=cv2.INTER_LINEAR)
    disocclusion_mask = warped_ones < 0.95 

    # --- UPGRADE 2: Gunakan Bilateral Filter untuk Menjaga Tepi ---
    smoothed_current_weight = cv2.bilateralFilter(
        current_weight_map.astype(np.float32), 
        d=bilateral_d, 
        sigmaColor=bilateral_sigma_color, 
        sigmaSpace=bilateral_sigma_space
    )
    
    # --- UPGRADE 3: Kalkulasi Kepercayaan Gabungan yang Cerdas ---
    # Kepercayaan dasar: seberapa mirip prediksi histori dengan data saat ini.
    temporal_diff = np.abs(smoothed_current_weight - warped_prev_ema)
    temporal_confidence = np.clip(1.0 - temporal_diff * 5.0, 0.0, 1.0) # Skala bisa disesuaikan
    
    # Gabungkan dengan kepercayaan dari optical flow jika tersedia
    if flow_confidence_map is not None:
        # Kepercayaan final hanya tinggi jika KEDUA sumber (temporal & flow) percaya diri.
        final_confidence = temporal_confidence * flow_confidence_map
    else:
        # Jika tidak ada info flow, andalkan kepercayaan temporal saja.
        final_confidence = temporal_confidence
        
    # Di area disoklusi, kita tidak bisa percaya pada histori sama sekali.
    final_confidence[disocclusion_mask] = 0.0

    # --- UPGRADE 4: Pencampuran Adaptif Berbasis Kepercayaan ---
    alpha_for_current = alpha_no_confidence - (alpha_no_confidence - alpha_base) * final_confidence
    alpha_for_current = np.clip(alpha_for_current, alpha_base, alpha_no_confidence)
    
    # Perluas dimensi alpha agar bisa di-broadcast dengan gambar berwarna
    alpha_for_current = alpha_for_current[..., np.newaxis] if current_weight_map.ndim > smoothed_current_weight.ndim else alpha_for_current

    # Lakukan pencampuran akhir
    weight_map_refined = (alpha_for_current * smoothed_current_weight) + ((1.0 - alpha_for_current) * warped_prev_ema)

    return weight_map_refined

# def ml_driven_refinement(
#     current_weight_map, 
#     prev_weight_map_ema, 
#     optical_flow, 
#     alpha_generator: AlphaGenerator,
#     flow_confidence_map=None,
#     bilateral_d=9, 
#     bilateral_sigma_color=0.05, 
#     bilateral_sigma_space=75):
#     """
#     Versi refinement yang digerakkan oleh Machine Learning untuk menghasilkan alpha map.
#     """
#     if prev_weight_map_ema is None or optical_flow is None or alpha_generator is None:
#         return current_weight_map

#     h, w = current_weight_map.shape
    
#     # --- LANGKAH 1: PERSIAPAN INPUT (Sama seperti sebelumnya) ---
#     grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
#     map_x = (grid_x - optical_flow[..., 0]).astype(np.float32)
#     map_y = (grid_y - optical_flow[..., 1]).astype(np.float32)
    
#     warped_prev_ema = cv2.remap(
#         prev_weight_map_ema, map_x, map_y, 
#         interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
#     )
    
#     warped_ones = cv2.remap(np.ones_like(prev_weight_map_ema), map_x, map_y, interpolation=cv2.INTER_LINEAR)
#     disocclusion_mask = warped_ones < 0.95 

#     smoothed_current_weight = cv2.bilateralFilter(
#         current_weight_map.astype(np.float32), 
#         d=bilateral_d, sigmaColor=bilateral_sigma_color, sigmaSpace=bilateral_sigma_space
#     )
    
#     ### DIHAPUS ###
#     # Bagian UPGRADE 3 dan 4 (kalkulasi confidence dan alpha heuristik) dihapus.
#     # Model ML akan menggantikan logika ini sepenuhnya.

#     # --- LANGKAH 2: PERUBAHAN UTAMA - INFERENSI MODEL ML ---
#     # Gunakan alpha_generator untuk membuat peta alpha yang cerdas.
#     alpha_for_current = alpha_generator.generate(
#         smoothed_current_weight=smoothed_current_weight,
#         warped_prev_ema=warped_prev_ema,
#         optical_flow=optical_flow,
#         flow_confidence_map=flow_confidence_map,
#         disocclusion_mask=disocclusion_mask
#     )

#     # --- LANGKAH 3: PENCAMPURAN AKHIR (Sama seperti sebelumnya) ---
#     # Logika blending tetap sama, tetapi sekarang menggunakan alpha map dari ML.
#     alpha_for_current_reshaped = alpha_for_current[..., np.newaxis] if current_weight_map.ndim > smoothed_current_weight.ndim else alpha_for_current

#     weight_map_refined = (alpha_for_current_reshaped * smoothed_current_weight) + ((1.0 - alpha_for_current_reshaped) * warped_prev_ema)

#     return weight_map_refined

def standard_refinement(
    weight_map: np.ndarray,
    prev_weight_map: np.ndarray,
    reference_image: np.ndarray,
    texture_threshold: float = 10.0,
    alpha: float = 0.7,
    bilateral_d: int = 9,
    bilateral_sigma_color: float = 0.1,
    bilateral_sigma_space: float = 10.0
) -> np.ndarray:
    """
    Refinement standar + temporal smoothing antar frame (tanpa optical flow).
    Lebih halus dan stabil dibanding standard_refinement biasa.

    Args:
        weight_map: peta bobot saat ini
        prev_weight_map: peta bobot dari frame sebelumnya
        reference_image: citra referensi untuk mendeteksi area flat
        texture_threshold: batasan untuk menentukan area flat
        alpha: blending factor antar bobot sekarang dan sebelumnya
        bilateral_d: diameter filter bilateral
        bilateral_sigma_color: sigma warna bilateral
        bilateral_sigma_space: sigma spasial bilateral

    Returns:
        weight_map_refined: peta bobot hasil refinement
    """

    # 1. Deteksi area low-texture seperti sebelumnya
    if reference_image.ndim == 3 and reference_image.shape[2] == 3:
        gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = reference_image

    laplacian = cv2.Laplacian(gray, cv2.CV_32F)
    texture_map = cv2.convertScaleAbs(laplacian)
    mask_low_texture = texture_map < texture_threshold

    # 2. Bilateral filter untuk spatial denoising
    spatial_smoothed = cv2.bilateralFilter(weight_map, bilateral_d, bilateral_sigma_color, bilateral_sigma_space)

    # 3. Kurangi bobot di area flat
    spatial_smoothed[mask_low_texture] *= 0.7

    # 4. Temporal blending tanpa optical flow
    if prev_weight_map is not None:
        refined = alpha * spatial_smoothed + (1 - alpha) * prev_weight_map
    else:
        refined = spatial_smoothed

    return refined

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

# =========================================================================
# === 7. LOGIKA PIPELINE & EKSEKUSI
# =========================================================================

def generate_balanced_batches(total_images, max_batch_size=10):
    """Sebuah generator yang menghasilkan indeks (awal, akhir) untuk setiap batch."""
    if total_images <= 0:
        return
    if total_images <= max_batch_size:
        yield (0, total_images)
        return
    num_batches = math.ceil(total_images / max_batch_size)
    base_size = total_images // num_batches
    remainder = total_images % num_batches
    current_index = 0
    for i in range(num_batches):
        batch_size = base_size + 1 if i < remainder else base_size
        start_index = current_index
        end_index = current_index + batch_size
        yield (start_index, end_index)
        current_index = end_index

def setup_balanced_batching(total_images, language_config, max_batch_size=10):
    """
    Menyiapkan seluruh logika batching, termasuk mencetak info ke konsol.
    
    Fungsi ini menyembunyikan semua kompleksitas dan mengembalikan rencana batching
    yang siap digunakan oleh perulangan di fungsi `main`.

    Args:
        total_images (int): Jumlah total gambar.
        language_config: Objek konfigurasi bahasa untuk pesan.
        max_batch_size (int): Ukuran maksimum per batch.

    Returns:
        list: Sebuah daftar tuple [(start1, end1), (start2, end2), ...] 
              yang merupakan rencana eksekusi batch. Mengembalikan list kosong jika
              tidak ada gambar.
    """
    if total_images <= 0:
        return [] # Kembalikan list kosong jika tidak ada gambar

    # 1. Panggil generator untuk membuat rencana batch
    batch_plan = list(generate_balanced_batches(total_images, max_batch_size))
    total_batches = len(batch_plan)

    # 2. Lakukan semua printing di sini untuk menjaga `main` tetap bersih
    print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))
    print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))
    
    # Buat string distribusi yang mudah dibaca
    distribusi_str = ", ".join([f"{end-start}" for start, end in batch_plan])
    # print(f"  -> Rencana distribusi gambar per batch: [{distribusi_str}]")

    # 3. Kembalikan rencana yang sudah jadi
    return batch_plan        

def run_pipeline_streaming(processor, image_paths, base_image, target_dims, 
                           update_progress, stop_requested, save_align, align_folder, command_save_to_hd5f):
    """
    Menjalankan pipeline tiga tahap penuh untuk alignment streaming sederhana.
    Loader -> Feature Extractor (GPU/CPU) -> Compensator & Saver.
    """
    total_images = len(image_paths) + 1
    progress_counter = {"count": 1}
    progress_lock = threading.Lock()
    lock = threading.Lock()

    queue_images = queue.Queue(maxsize=2)
    queue_points = queue.Queue(maxsize=2)

    # --- Stasiun 1: Loader ---
    def loader_worker():
        for i, path in enumerate(image_paths, start=1):
            if stop_requested and stop_requested(): break
            img_list = load_images_from_paths([path], stop_requested=stop_requested)
            if not img_list or img_list[0] is None: continue
            target_image = resize_with_padding(img_list[0], target_dims)
            queue_images.put((i, path, target_image))
        queue_images.put(None)

    # --- Stasiun 2: Feature Extractor ---
    def feature_extractor_worker():
        while True:
            item = queue_images.get()
            if item is None: break
            i, path, target_image = item
            base_pts, target_pts = processor.calculate_global_motion(base_image, target_image)
            if base_pts is not None and target_pts is not None:
                queue_points.put((i, path, target_image, base_pts, target_pts))
            else:
                with progress_lock: progress_counter["count"] += 1
        queue_points.put(None)

    # Mulai thread worker
    loader_thread = threading.Thread(target=loader_worker)
    extractor_thread = threading.Thread(target=feature_extractor_worker)
    loader_thread.start()
    extractor_thread.start()

    # --- Stasiun 3: Compensator & Saver (di Thread Utama) ---
    while True:
        item = queue_points.get()
        if item is None: break
        i, path, target_image, base_pts, target_pts = item
        
        compensated = processor.compensate_motion(target_image, base_pts, target_pts)
        if compensated is not None:
            if save_align: save_align_to_folder(compensated, i, path, align_folder)
            if command_save_to_hd5f:
                with lock:
                    with h5py.File(processor.hdf5_path, "a") as h5f:
                        save_to_hdf5(h5f, f"image_{i}", compensated, extract_exif(path))
        
        with progress_lock:
            progress_counter["count"] += 1
            if update_progress:
                update_progress(
                    progress_counter["count"], total_images,
                    f"Processing image {progress_counter['count']}/{total_images}"
                )

    loader_thread.join()
    extractor_thread.join()

def _run_transform_calculation_stage(processor, image_paths, base_image, target_dims, 
                                     update_progress, stop_requested, total_images):
    """Helper untuk Tahap 1 dari Global Crop: Menghitung semua transformasi."""
    all_transforms = []
    progress_counter = {"count": 0}
    progress_lock = threading.Lock()
    
    queue_images_s1 = queue.Queue(maxsize=2)
    queue_transforms_s1 = queue.Queue(maxsize=2)

    def loader_s1_worker():
        for i, path in enumerate(image_paths, start=1):
            if stop_requested and stop_requested(): break
            img_list = load_images_from_paths([path], stop_requested=stop_requested)
            if not img_list or img_list[0] is None: continue
            target_image = resize_with_padding(img_list[0], target_dims)
            queue_images_s1.put((i, path, target_image))
        queue_images_s1.put(None)

    def extractor_s1_worker():
        while True:
            item = queue_images_s1.get()
            if item is None: break
            i, path, target_image = item
            base_pts, target_pts = processor.calculate_global_motion(base_image, target_image)
            if base_pts is not None and target_pts is not None:
                queue_transforms_s1.put((i, path, base_pts, target_pts))
        queue_transforms_s1.put(None)

    loader_s1_thread = threading.Thread(target=loader_s1_worker)
    extractor_s1_thread = threading.Thread(target=extractor_s1_worker)
    loader_s1_thread.start()
    extractor_s1_thread.start()

    while True:
        item = queue_transforms_s1.get()
        if item is None: break
        all_transforms.append(item)
        with progress_lock:
            progress_counter["count"] += 1
            if update_progress:
                update_progress(
                    progress_counter["count"], 2 * total_images,
                    f"Calculating transform {progress_counter['count']}/{total_images}"
                )
    loader_s1_thread.join()
    extractor_s1_thread.join()
    return all_transforms

def _run_apply_and_save_stage(processor, temp_transforms, crop_bounds, target_dims,
                               update_progress, stop_requested, total_images,
                               save_align, align_folder, command_save_to_hd5f):
    """Helper untuk Tahap 3 dari Global Crop: Menerapkan transformasi dan menyimpan."""
    stage3_counter = {"count": 0}
    progress_lock = threading.Lock()
    lock = threading.Lock()
    
    queue_images_s3 = queue.Queue(maxsize=2)
    queue_to_save_s3 = queue.Queue(maxsize=2)

    def loader_s3_worker():
        for i, path, base_pts, target_pts in temp_transforms:
            if stop_requested and stop_requested(): break
            img_list = load_images_from_paths([path], stop_requested=stop_requested)
            if not img_list or img_list[0] is None: continue
            target_image = resize_with_padding(img_list[0], target_dims)
            queue_images_s3.put((i, path, base_pts, target_pts, target_image))
        queue_images_s3.put(None)

    def compensator_s3_worker():
        while True:
            item = queue_images_s3.get()
            if item is None: break
            i, path, base_pts, target_pts, target_image = item
            compensated = processor.compensate_motion(target_image, base_pts, target_pts)
            if compensated is None: continue
            cropped = crop_image(compensated, crop_bounds)
            queue_to_save_s3.put((i, path, cropped))
        queue_to_save_s3.put(None)
    
    loader_s3_thread = threading.Thread(target=loader_s3_worker)
    compensator_s3_thread = threading.Thread(target=compensator_s3_worker)
    loader_s3_thread.start()
    compensator_s3_thread.start()

    while True:
        item = queue_to_save_s3.get()
        if item is None: break
        i, path, cropped = item
        if save_align: save_align_to_folder(cropped, i, path, align_folder)
        if command_save_to_hd5f:
            with lock:
                with h5py.File(processor.hdf5_path, "a") as h5f:
                    save_to_hdf5(h5f, f"image_{i}", cropped, extract_exif(path))
        del cropped
        gc.collect()
        with progress_lock:
            stage3_counter["count"] += 1
            if update_progress:
                update_progress(
                    total_images + stage3_counter["count"], 2 * total_images,
                    f"Applying transform {stage3_counter['count']}/{len(temp_transforms)}"
                )
    loader_s3_thread.join()
    compensator_s3_thread.join()

def run_pipeline_global_crop(processor, image_paths, base_image, target_dims, 
                             update_progress, stop_requested, transformation_type,
                             save_align, align_folder, command_save_to_hd5f):
    """Menjalankan pipeline tiga tahap penuh untuk alignment dengan global cropping."""
    total_images_to_process = len(image_paths)

    # --- Tahap 1 ---
    all_transforms = _run_transform_calculation_stage(
        processor, image_paths, base_image, target_dims,
        update_progress, stop_requested, total_images_to_process
    )
    if not all_transforms: return

    # --- Tahap 2 (Sinkron) ---
    crop_bounds = compute_global_crop(
        [(i, b, t) for i, _, b, t in all_transforms],
        total_images_to_process + 1, base_image.shape[1], base_image.shape[0],
        transformation_type=transformation_type,
    )
    if crop_bounds is None: return

    base_image_cropped = crop_image(base_image, crop_bounds)
    with h5py.File(processor.hdf5_path, "a") as h5f:
        del h5f["image_0"]
        h5f.create_dataset("image_0", data=base_image_cropped)
    if save_align: save_align_to_folder(base_image_cropped, 0, image_paths[0], align_folder)
    del base_image_cropped, base_image
    gc.collect()

    # --- Tahap 3 ---
    _run_apply_and_save_stage(
        processor, all_transforms, crop_bounds, target_dims,
        update_progress, stop_requested, total_images_to_process,
        save_align, align_folder, command_save_to_hd5f
    )

# def main(db_path, update_progress=None, ...):
#     """Fungsi utama yang mengoordinasikan seluruh alur kerja."""
    
#     # --- 1. Inisialisasi dan Konfigurasi ---
#     # Pilih prosesor yang sesuai (AKAZE, LightGlue, dll.)
#     # processor = AKAZEAlgorithm(db_path) 
#     # config = processor.load_akaze_config(config_filename)
    
#     # ... (sisa logika inisialisasi dari jawaban sebelumnya) ...

#     # --- 2. Penyiapan Path dan Metadata ---
#     # ... (sisa logika penyiapan path dari jawaban sebelumnya) ...
    
#     # --- 3. Pemuatan dan Penyiapan Base Image ---
#     # ... (sisa logika pemuatan base image dari jawaban sebelumnya) ...

#     # --- 4. Delegasi ke Pipeline yang Sesuai ---
#     if not enable_cropping or keep_edges:
#         run_pipeline_streaming(...)
#     else:
#         run_pipeline_global_crop(...)