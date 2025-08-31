# =========================================================================
# === 1. IMPORTS & KONFIGURASI GLOBAL
# =========================================================================
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from functools import lru_cache
import gc
import math
import queue
import threading
import concurrent
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

def get_all_image_paths_for_single_process(db_path: str) -> list:
    """
    Mengambil semua path gambar, memvalidasi keberadaannya di disk,
    dan menghapus entri yang tidak valid dari database.
    """
    try:
        if not os.path.isfile(db_path):
            return []

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Ambil semua data yang relevan: path dan ID
            sql_query = """
                SELECT i.id, i.path
                FROM images i
                JOIN single_process_image spi ON i.id = spi.image_id_single
                ORDER BY
                    spi.is_reference DESC,
                    i.path ASC
            """
            cursor.execute(sql_query)
            
            all_rows = cursor.fetchall()
            
            valid_image_paths = []
            ids_to_delete = []

            # --- Validasi dan Pemisahan ---
            for image_id, image_path in all_rows:
                if os.path.exists(image_path):
                    # Jika file ada, simpan path-nya
                    valid_image_paths.append(image_path)
                else:
                    # Jika file tidak ada, tandai ID-nya untuk dihapus
                    print(f"Path not found, marking for deletion from DB: {image_path}")
                    ids_to_delete.append(image_id)
            
            # --- Pembersihan Database (jika ada yang perlu dihapus) ---
            if ids_to_delete:
                print(f"Deleting {len(ids_to_delete)} invalid entries from the database...")
                # Buat placeholder string, misal: (?, ?, ?)
                placeholders = ', '.join(['?'] * len(ids_to_delete))
                
                # Hapus dari tabel relasi terlebih dahulu
                cursor.execute(
                    f"DELETE FROM single_process_image WHERE image_id_single IN ({placeholders})",
                    ids_to_delete
                )
                
                # Kemudian hapus dari tabel utama 'images'
                cursor.execute(
                    f"DELETE FROM images WHERE id IN ({placeholders})",
                    ids_to_delete
                )
                
                conn.commit() # Simpan perubahan
            
            return valid_image_paths

    except sqlite3.Error as e:
        print(f"Database error in get_all_image_paths_for_single_process: {e}")
        return [] 
    except Exception as e:
        print(f"An unexpected error occurred in get_all_image_paths_for_single_process: {e}")
        return []
        
def get_all_image_paths_for_batch_process(db_path, batch_id):
    """
    Mengambil semua path gambar untuk batch ID tertentu, memvalidasi,
    dan menghapus entri yang tidak valid dari database.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Ambil path dan ID
            cursor.execute("""
                SELECT images.id, images.path 
                FROM batch_process_image
                JOIN images ON batch_process_image.image_id_batch = images.id
                WHERE batch_process_image.batch_id = ?
                ORDER BY images.path ASC
            """, (batch_id,))
            
            all_rows = cursor.fetchall()
            
            valid_image_paths = []
            ids_to_delete = []

            # --- Validasi dan Pemisahan ---
            for image_id, image_path in all_rows:
                if os.path.exists(image_path):
                    valid_image_paths.append(image_path)
                else:
                    print(f"Path not found, marking for deletion from DB: {image_path}")
                    ids_to_delete.append(image_id)

            # --- Pembersihan Database ---
            if ids_to_delete:
                print(f"Deleting {len(ids_to_delete)} invalid entries from the database...")
                placeholders = ', '.join(['?'] * len(ids_to_delete))
                
                # Hapus dari tabel relasi `batch_process_image`
                # Kita perlu memastikan kita hanya menghapus untuk batch_id yang relevan
                # dan image_id yang tidak valid
                for image_id in ids_to_delete:
                    cursor.execute(
                        "DELETE FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ?",
                        (batch_id, image_id)
                    )

                # Hapus dari tabel `images`
                cursor.execute(
                    f"DELETE FROM images WHERE id IN ({placeholders})",
                    ids_to_delete
                )
                
                conn.commit()

            return valid_image_paths
            
    except sqlite3.Error as e:
        print(f"Database error in get_all_image_paths_for_batch_process: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred in get_all_image_paths_for_batch_process: {e}")
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
            # gamma_setting = (2.5, 15.92)  # Natural Gamma
            gamma_setting = (2.222, 4.5)
            rgb = raw.postprocess(
                demosaic_algorithm= rawpy.DemosaicAlgorithm.DCB,
                use_camera_wb=True,
                gamma=gamma_setting,
                output_bps=16,
                bad_pixels_path=None,
                output_color=rawpy.ColorSpace.sRGB,
                chromatic_aberration=None,
                highlight_mode=rawpy.HighlightMode.Blend,
            )

        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        return bgr
    except Exception as e:
        print(f"Error membaca RAW file {original_path}: {e}")
        return None
 
def load_images_from_paths(image_paths, stop_requested=None):
    images = []
    raw_extensions = {'.dng', '.cr2', '.nef', '.arw', '.orf', '.rw2', '.pef', '.srw'}
    num_threads = os.cpu_count() or 4

    raw_futures = []
    standard_futures = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
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
        for future in as_completed(raw_futures):
            if stop_requested and stop_requested():
                break
            try:
                img = future.result()
                if img is not None:
                    images.append(img)
            except Exception as e:
                print(f"Error loading RAW image: {e}")

        # Ambil hasil dari gambar biasa
        for future in as_completed(standard_futures):
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
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        start = 0
        while start < total_items:
            end = start + chunk_size
            if end > total_items:
                end = total_items
            futures.append(executor.submit(write_chunk, start, end))
            start = end
        wait(futures)

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
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
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
    Menyimpan gambar tanpa rotasi/flip fisik, 
    tapi tetap menyalin metadata orientasi dari gambar referensi 
    menggunakan exiftool agar metadata akurat.
    """
    try:
        image_to_save = image.copy()
        if reference_image_path is None or not os.path.exists(reference_image_path):
            cv2.imwrite(output_path, image_to_save)
            return output_path

        # Langsung simpan gambar apa adanya (tidak diputar/flip)
        success = cv2.imwrite(output_path, image_to_save)
        if not success:
            print(f"Error: OpenCV gagal menyimpan gambar ke '{output_path}'")
            return None

        # Salin metadata dari referensi (termasuk Orientation)
        try:
            subprocess.run([
                "exiftool",
                "-q",
                "-overwrite_original",
                "-TagsFromFile", reference_image_path,
                output_path
            ], check=True, capture_output=True)
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

def prepare_gray(img):
        if img is None: raise ValueError("Input image is None.")
        if img.ndim == 3 and img.shape[2] == 3: gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif img.ndim == 3 and img.shape[2] == 4: gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY) # Tambahkan handle BGRA
        elif img.ndim == 2: gray = img
        else:
            raise ValueError(f"Invalid image dimensions/channels: {img.shape}")

        if gray.dtype != np.uint8:
            max_val = np.max(gray)
            if gray.dtype == np.float32 or gray.dtype == np.float64:
                 if max_val <= 1.0 and np.min(gray) >= 0:
                     gray_norm = (gray * 255.0).astype(np.uint8)
                 else:
                     if gray.dtype == np.uint16:
                         gray_norm = (gray / 256.0).astype(np.uint8) # Asumsi 16-bit ke 8-bit
                     elif gray.dtype == np.int16:
                          gray_norm = ((gray / 256.0) + 128).astype(np.uint8) # Perkiraan kasar
                     else:
                         gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            elif gray.dtype == np.uint16:
                 gray_norm = (gray / 256.0).astype(np.uint8)
            else:
                 gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            return gray_norm
        return gray

def prepare_image(image, grayscale=False, use_clahe=True):
    """
    Fungsi Hibrida Cerdas.
    - Untuk Grayscale (AKAZE): Mendelegasikan tugas ke `prepare_gray_akaze` untuk hasil yang 100% identik.
    - Untuk Berwarna (LightGlue): Menggunakan logika internalnya sendiri yang kuat.

    Args:
        image: Gambar input.
        grayscale (bool): Jika True, akan memanggil pipeline khusus grayscale.
        use_clahe (bool): Jika True, akan menerapkan CLAHE.

    Returns:
        Gambar uint8 yang telah diproses.
    """
    if image is None:
        return None

    if grayscale:
        processed_image = prepare_gray(image)
        
        if use_clahe:
            try:
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                processed_image = clahe.apply(processed_image)
            except Exception:
                pass 

    else:
        if image.dtype == np.uint8:
            processed_image = image.copy()
        elif image.dtype == np.uint16:
            processed_image = (image / 256).astype(np.uint8)
        elif image.dtype in [np.float32, np.float64]:
            max_val, min_val = np.max(image), np.min(image)
            if max_val <= 1.0 and min_val >= 0.0:
                processed_image = (image * 255).astype(np.uint8)
            else:
                processed_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        else:
            processed_image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        if processed_image.ndim == 2:
            final_image = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)
        elif processed_image.shape[2] == 4:
            final_image = cv2.cvtColor(processed_image, cv2.COLOR_BGRA2BGR)
        else:
            final_image = processed_image
            
        if use_clahe:
            try:
                lab = cv2.cvtColor(final_image, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                cl = clahe.apply(l)
                merged_channels = cv2.merge((cl, a, b))
                processed_image = cv2.cvtColor(merged_channels, cv2.COLOR_LAB2BGR)
            except Exception:
                pass
        else:
            processed_image = final_image 
    
    return processed_image

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

def estimate_noise_variance(gray_image, edge_threshold_low=70, dilate_kernel_size=4, min_flat_pixels_ratio=0.1):
    """
    Memperkirakan tingkat noise dalam gambar dengan menghitung varians Laplacian
    hanya pada area gambar yang dianggap "datar" (tidak ada tepi atau tekstur yang kuat).

    Args:
        gray_image (np.array): Gambar grayscale.
        edge_threshold_low (int): Ambang batas rendah untuk detektor tepi Canny.
        dilate_kernel_size (int): Ukuran kernel untuk operasi dilasi pada tepi.
        min_flat_pixels_ratio (float): Rasio minimum piksel datar yang dibutuhkan.
                                       Jika terlalu sedikit, estimasi bisa tidak andal.
    Returns:
        float: Varians noise yang diestimasi.
    """
    if gray_image is None or gray_image.size == 0:
        return 0.0 # Atau nilai default yang sesuai

    # 1. Deteksi tepi untuk mengidentifikasi area non-datar
    # Gunakan Canny. Threshold tinggi x 2 untuk high threshold adalah standar.
    edges = cv2.Canny(gray_image, edge_threshold_low, edge_threshold_low * 2)
    
    # 2. Dilatasi tepi untuk sedikit memperluas area non-datar
    kernel = np.ones((dilate_kernel_size, dilate_kernel_size), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)
    
    # 3. Buat mask untuk area "datar" (piksel yang bukan bagian dari tepi yang diperluas)
    flat_mask = (dilated_edges == 0).astype(np.bool_) # Ubah ke boolean mask
    
    # Periksa apakah ada cukup piksel "datar"
    num_flat_pixels = np.sum(flat_mask)
    if num_flat_pixels < (gray_image.size * min_flat_pixels_ratio):
        # print(f"Peringatan: Tidak ditemukan cukup piksel datar ({num_flat_pixels}/{gray_image.size * min_flat_pixels_ratio:.0f}). Estimasi noise mungkin kurang akurat.")
        laplacian_full = cv2.Laplacian(gray_image, cv2.CV_64F)
        return laplacian_full.var()

    # 4. Hitung Laplacian dari gambar asli
    laplacian_output = cv2.Laplacian(gray_image, cv2.CV_64F)
    
    # 5. Hitung varians hanya pada piksel yang dianggap "datar"
    variance = laplacian_output[flat_mask].var()
    
    return variance

def get_adaptive_bilateral(noise_level, min_noise, max_noise, min_d, max_d, min_sigma, max_sigma):
    """
    Menghitung parameter untuk filter bilateral secara dinamis berdasarkan tingkat noise.
    """
    # Jika noise di atas atau sama dengan maksimum, gunakan parameter maksimum.
    if noise_level >= max_noise:
        return max_d, max_sigma, max_sigma

    # Hitung rasio/progres noise antara rentang min dan max (nilai antara 0.0 dan 1.0)
    # Ditambah epsilon (1e-6) untuk menghindari pembagian dengan nol jika min_noise == max_noise
    ratio = (noise_level - min_noise) / (max_noise - min_noise + 1e-6)

    # Lakukan interpolasi linear untuk menghitung parameter
    calculated_d = min_d + ratio * (max_d - min_d)
    calculated_sigma = min_sigma + ratio * (max_sigma - min_sigma)

    # Parameter 'd' harus berupa integer ganjil.
    # Bulatkan ke integer terdekat, lalu pastikan ganjil.
    d = int(round(calculated_d))
    if d % 2 == 0:
        d += 1
    
    # Sigma bisa dibulatkan ke integer terdekat
    sigma = int(round(calculated_sigma))
    
    return d, sigma, sigma

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
                                    max_boost=2.0, min_boost=0.5,
                                    num_iterations=10, # Parameter baru untuk iterasi
                                    ksize=5): # Parameter untuk filter
    """
    Menyempurnakan peta bobot total secara iteratif berdasarkan stabilitas temporal.
    Menggunakan pendekatan relaxation labeling untuk menghasilkan area stabil/tidak stabil yang koheren.
    """
    if len(weight_maps_all) <= 1 or num_iterations == 0:
        return # Tidak melakukan apa-apa jika tidak ada cukup data

    # --- LANGKAH 1: Analisis Statistik (Dilakukan Sekali) ---
    print("Menganalisis stabilitas temporal...")
    weight_stack = np.stack(weight_maps_all, axis=0)
    temporal_std = np.std(weight_stack, axis=0)
    temporal_mean = np.mean(weight_stack, axis=0)

    # Metrik stabilitas: rasio mean terhadap standar deviasi
    stability_score = temporal_mean / (temporal_std + 1e-6)
    
    # Gunakan persentil untuk ketahanan terhadap outlier, bukan median/std
    p50_stability = np.percentile(stability_score, 50) # Median
    p84_stability = np.percentile(stability_score, 84)
    std_equivalent = p84_stability - p50_stability # Estimasi std yang lebih kuat
    if std_equivalent < 1e-6: std_equivalent = 1.0 # Hindari pembagian dengan nol

    # --- LANGKAH 2: Hitung Faktor Penskalaan Awal ---
    delta = stability_score - p50_stability
    scaling_factors = 1.0 + np.tanh(delta / std_equivalent)
    scaling_factors = np.clip(scaling_factors, min_boost, max_boost).astype(np.float32)

    # --- LANGKAH 3: Refinement Iteratif (Cepat & Hemat Memori) ---
    refined_scaling_factors = scaling_factors
    
    for i in range(num_iterations):
        refined_scaling_factors = cv2.medianBlur(
            refined_scaling_factors.astype(np.float32),
            ksize=ksize
        )

    # --- LANGKAH 4: Terapkan Faktor Penskalaan Akhir ---
    # Modifikasi weight_map_sum secara in-place
    weight_map_sum *= refined_scaling_factors

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
    smoothed_current_weight = cv2.medianBlur(
        current_weight_map.astype(np.float32), 
        ksize=5
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
    
    with ThreadPoolExecutor(max_workers=blocks_x * blocks_y) as executor:
        futures = []
        for i in range(blocks_x):
            for j in range(blocks_y):
                x = i * block_w
                y = j * block_h
                bw = block_w if i < blocks_x - 1 else w - x
                bh = block_h if j < blocks_y - 1 else h - y
                futures.append(executor.submit(process_block, x, y, bw, bh))
        
        wait(futures)
    
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

def setup_balanced_batching(total_images, language_config, max_batch_size=8):
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

def run_pipeline_non_crop(processor, image_paths, base_image, target_dims, 
                           update_progress, stop_requested, save_align, align_folder, h5_file_handle,
                           num_workers):
    """
    Pipeline sederhana dan tangguh menggunakan Thread Pool dengan progress bar real-time.
    Setiap thread memproses satu gambar, dan thread utama mengupdate progress saat masing-masing selesai.
    """

    total_images_in_stack = len(image_paths)
    if total_images_in_stack <= 1:
        return

    # Kunci untuk operasi yang tidak thread-safe (HANYA HDF5)
    # progress_lock tidak lagi diperlukan karena progress di-handle oleh thread utama.
    h5_lock = threading.Lock()
    
    # --- Simpan base image dulu ---
    # Progress dimulai dari 1 karena base image sudah ada
    if update_progress:
        update_progress(1, total_images_in_stack, language_config.IMAGE_PROCESS_IN_PROGRESS.format(1, total_images_in_stack))
        
    if save_align:
        save_align_to_folder(base_image, 0, image_paths[0], align_folder)
    if h5_file_handle:
        with h5_lock:
            save_to_hdf5(h5_file_handle, "image_0", base_image, extract_exif(image_paths[0]))

    # --- Fungsi Worker Tunggal (LOGIKA PROGRESS DIHAPUS) ---
    def process_image_task(i, path):
        # Pemeriksaan stop_requested tetap penting
        if stop_requested and stop_requested():
            return
        
        try:
            # 1. Muat & Resize
            img_list = load_images_from_paths([path], stop_requested=stop_requested)
            if not img_list or img_list[0] is None:
                return
            target_image = resize_with_padding(img_list[0], target_dims)
            
            # 2. Hitung Motion
            base_pts, target_pts = processor.calculate_global_motion(
                base_image, target_image, stop_requested=stop_requested
            )
            
            # 3. Kompensasi & Simpan
            if base_pts is not None and target_pts is not None:
                compensated = processor.compensate_motion(target_image, base_pts, target_pts)
                if compensated is not None:
                    if save_align:
                        save_align_to_folder(compensated, i, path, align_folder)
                    if h5_file_handle:
                        with h5_lock:
                            save_to_hdf5(h5_file_handle, f"image_{i}", compensated, extract_exif(path))
        except Exception as e:
            # Penting untuk menangkap exception di sini agar bisa di-raise di thread utama
            print(f"⚠️ Error processing image {i} ({os.path.basename(path)}): {e}")
            raise # Melempar kembali exception agar future.result() bisa menangkapnya
        finally:
            # Cleanup RAM tetap di sini
            gc.collect()

    # --- Eksekusi Menggunakan Pola "as_completed" ---
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        
        tasks_to_process = image_paths[1:]
        
        # Buat dictionary untuk melacak future
        future_to_path = {
            executor.submit(process_image_task, i, path): path
            for i, path in enumerate(tasks_to_process, start=1)
        }
        
        # Inisialisasi progress. 1 untuk base image.
        completed_count = 1

        # Loop ini akan berjalan setiap kali sebuah tugas selesai
        for future in as_completed(future_to_path):
            if stop_requested and stop_requested():
                break # Keluar dari loop jika diminta berhenti

            path = future_to_path[future]
            try:
                # Panggil .result() untuk memeriksa apakah ada exception di dalam thread
                future.result()
            except Exception as exc:
                print(f"Task for {os.path.basename(path)} generated an exception: {exc}")

            # Update progress di sini, di thread utama!
            completed_count += 1
            if update_progress:
                update_progress(
                    completed_count,
                    total_images_in_stack,
                    language_config.IMAGE_PROCESS_IN_PROGRESS.format(completed_count, total_images_in_stack)
                )         
def run_pipeline_global_crop(processor, image_paths, base_image, target_dims, 
                             update_progress, stop_requested, transformation_type,
                             save_align, align_folder, h5_file_handle,
                             num_workers):
    """
    Alur global crop:
      Stage 1 (paralel & hemat RAM) -> hitung transform
      Stage 2 -> hitung global crop
      Stage 3 -> apply & save (pakai versi yang sudah kamu miliki)
    """
    total_images_in_stack = len(image_paths)
    images_to_process_for_transforms = image_paths[1:]

    # --- TAHAP 1: Hitung transform (0% -> 50%) ---
    all_transforms = _run_transform_calculation_stage(
        processor, images_to_process_for_transforms, base_image, target_dims,
        update_progress, stop_requested,
        num_workers=num_workers
    )
    if not all_transforms:
        print("Transform calculation failed for all images. Aborting global crop.")
        return

    if len(all_transforms) < len(images_to_process_for_transforms):
        failed_count = len(images_to_process_for_transforms) - len(all_transforms)
        print(f"Warning: Could not calculate transforms for {failed_count} image(s). Continuing with the successful ones.")

    if update_progress:
        update_progress(50, 100, "Computing global crop bounds...")

    crop_bounds = compute_global_crop(
        [(item[0], item[2], item[3]) for item in all_transforms],
        total_images_in_stack, base_image.shape[1], base_image.shape[0],
        transformation_type=transformation_type,
    )
    if crop_bounds is None:
        return

    # --- TAHAP 3: Apply & Save (50% -> 100%) ---
    _run_apply_and_save_stage(
        processor, all_transforms, crop_bounds, target_dims,
        update_progress, stop_requested,
        save_align, align_folder,
        h5_file_handle,
        base_image, image_paths[0],
        num_workers=num_workers
    )
    
def _run_transform_calculation_stage(processor, image_paths, base_image, target_dims, 
                                     update_progress, stop_requested,
                                     num_workers):
    """Tahap 1 yang disederhanakan: Menghitung transformasi secara paralel."""
    import os

    all_transforms = []
    num_to_process = len(image_paths)
    if num_to_process == 0:
        return all_transforms

    # --- Fungsi Worker Tunggal ---
    def calculate_transform_task(i, path):
        if stop_requested and stop_requested(): return None
        try:
            img_list = load_images_from_paths([path], stop_requested=stop_requested)
            if not img_list or img_list[0] is None: return None
            
            target_image = resize_with_padding(img_list[0], target_dims)
            base_pts, target_pts = processor.calculate_global_motion(
                base_image, target_image, stop_requested=stop_requested
            )
            
            if base_pts is not None and target_pts is not None:
                return (i, path, base_pts, target_pts)
        except Exception as e:
            print(f"⚠️ Transform calc error {i} ({os.path.basename(path)}): {e}")
        return None

    # --- Eksekusi dan Kumpulkan Hasil ---
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_task = {executor.submit(calculate_transform_task, i, path): i 
                          for i, path in enumerate(image_paths, start=1)}

        results_received = 0
        for future in as_completed(future_to_task):
            if stop_requested and stop_requested():
                break

            result = future.result()
            results_received += 1
            if result:
                all_transforms.append(result)
            
            if update_progress:
                percent = (results_received / num_to_process) * 50
                status = language_config.RUN_PROCESS_TRANSFORMATION.format(results_received, num_to_process)
                update_progress(int(percent), 100, status)

    all_transforms.sort(key=lambda x: x[0])
    return all_transforms

def _run_apply_and_save_stage(processor, temp_transforms, crop_bounds, target_dims,
                              update_progress, stop_requested,
                              save_align, align_folder,
                              h5_file_handle,
                              base_image, base_image_path,
                              num_workers):
    """Tahap 3 yang disederhanakan: Menerapkan transformasi dan menyimpan secara paralel."""

    h5_lock = threading.Lock()
    progress_lock = threading.Lock()

    tasks = [(0, base_image_path, None, None, base_image)] + \
            [(i, path, base_pts, target_pts, None) for i, path, base_pts, target_pts in temp_transforms]
    
    num_to_save = len(tasks)
    completed_counter = {"count": 0}
    
    # --- Fungsi Worker Tunggal ---
    def apply_and_save_task(task_data):
        i, path, base_pts, target_pts, image_data = task_data
        if stop_requested and stop_requested(): return

        try:
            # 1. Muat gambar jika diperlukan
            if image_data is None:
                img_list = load_images_from_paths([path], stop_requested=stop_requested)
                if not img_list or img_list[0] is None: return
                image_data = resize_with_padding(img_list[0], target_dims)

            # 2. Proses: Kompensasi & Crop
            processed_image = None
            if i > 0: # Target image
                if base_pts is not None and target_pts is not None:
                    compensated = processor.compensate_motion(image_data, base_pts, target_pts)
                    if compensated is not None:
                        processed_image = crop_image(compensated, crop_bounds)
            else: # Base image
                processed_image = crop_image(image_data, crop_bounds)
            
            # 3. Simpan
            if processed_image is not None:
                if save_align:
                    save_align_to_folder(processed_image, i, path, align_folder)
                if h5_file_handle:
                    with h5_lock:
                        save_to_hdf5(h5_file_handle, f"image_{i}", processed_image, extract_exif(path))
        except Exception as e:
            print(f"⚠️ Apply/Save error {i} ({os.path.basename(path)}): {e}")
        finally:
            # 4. Update Progress & Cleanup
            with progress_lock:
                completed_counter["count"] += 1
                count = completed_counter["count"]
                if update_progress:
                    percent = 50 + (count / num_to_save) * 50
                    status = language_config.RUN_SAVING_TRANSFORMATION.format(count, num_to_save)
                    update_progress(int(percent), 100, status)
            
            del image_data
            if 'processed_image' in locals(): del processed_image
            if 'compensated' in locals(): del compensated
            gc.collect()

    # --- Eksekusi Menggunakan ThreadPoolExecutor ---
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for task in tasks:
            if stop_requested and stop_requested():
                break
            executor.submit(apply_and_save_task, task)     
               