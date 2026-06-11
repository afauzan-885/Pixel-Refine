# =========================================================================
# === 1. IMPORTS & KONFIGURASI GLOBAL
# =========================================================================
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from functools import lru_cache
import gc
import math
import threading
import traceback
import cv2
import json
import os
import sqlite3
import subprocess
import exifread
import numpy as np
import tifffile
from PIL import Image

try:
    import rawpy

    RAWPY_AVAILABLE = True
except ImportError:
    RAWPY_AVAILABLE = False

from pixel_refine_desktop.ui.views.settings.General.Language import language_config


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
                print(
                    f"Deleting {len(ids_to_delete)} invalid entries from the database..."
                )
                # Buat placeholder string, misal: (?, ?, ?)
                placeholders = ", ".join(["?"] * len(ids_to_delete))

                # Hapus dari tabel relasi terlebih dahulu
                cursor.execute(
                    f"DELETE FROM single_process_image WHERE image_id_single IN ({placeholders})",
                    ids_to_delete,
                )

                # Kemudian hapus dari tabel utama 'images'
                cursor.execute(
                    f"DELETE FROM images WHERE id IN ({placeholders})", ids_to_delete
                )

                conn.commit()  # Simpan perubahan

            return valid_image_paths

    except sqlite3.Error as e:
        print(f"Database error in get_all_image_paths_for_single_process: {e}")
        return []
    except Exception as e:
        print(
            f"An unexpected error occurred in get_all_image_paths_for_single_process: {e}"
        )
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
            cursor.execute(
                """
                SELECT images.id, images.path 
                FROM batch_process_image
                JOIN images ON batch_process_image.image_id_batch = images.id
                WHERE batch_process_image.batch_id = ?
                ORDER BY batch_process_image.is_reference_batch DESC, images.path ASC
            """,
                (batch_id,),
            )

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
                print(
                    f"Deleting {len(ids_to_delete)} invalid entries from the database..."
                )
                placeholders = ", ".join(["?"] * len(ids_to_delete))

                # Hapus dari tabel relasi `batch_process_image`
                # Kita perlu memastikan kita hanya menghapus untuk batch_id yang relevan
                # dan image_id yang tidak valid
                for image_id in ids_to_delete:
                    cursor.execute(
                        "DELETE FROM batch_process_image WHERE batch_id = ? AND image_id_batch = ?",
                        (batch_id, image_id),
                    )

                # Hapus dari tabel `images`
                cursor.execute(
                    f"DELETE FROM images WHERE id IN ({placeholders})", ids_to_delete
                )

                conn.commit()

            return valid_image_paths

    except sqlite3.Error as e:
        print(f"Database error in get_all_image_paths_for_batch_process: {e}")
        return []
    except Exception as e:
        print(
            f"An unexpected error occurred in get_all_image_paths_for_batch_process: {e}"
        )
        return []


def _prepare_image_array_from_raw(
    original_path, linear_mode=False, generate_ref_proxy=False
):
    # Fungsi ini tidak berubah
    try:
        if not RAWPY_AVAILABLE:
            return None
        with rawpy.imread(original_path) as raw:
            if linear_mode:
                # LINEAR DNG MODE (Gamma 1.0, 16-bit, No Auto Brightness)
                # output_color=rawpy.ColorSpace.sRGB means it applies the ColorMatrix to convert CameraRGB -> sRGB Primaries
                # but with gamma=(1,1) it keeps the tone curve LINEAR.
                rgb = raw.postprocess(
                    demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,
                    use_camera_wb=True,
                    no_auto_bright=True,  # Important for Linear
                    gamma=(1, 1),  # Linear Gamma
                    output_bps=16,
                    # [REVERTED] Use sRGB for Linear DNG (Demosaiced)
                    output_color=rawpy.ColorSpace.sRGB,
                    highlight_mode=rawpy.HighlightMode.Blend,
                    user_flip=0,
                )

                # [DUAL CONVERSION] Jika requested, generate GT Proxy (Standard Look)
                # Hanya untuk Reference Analysis
                gt_proxy = None
                if generate_ref_proxy:
                    gamma_setting = (2.222, 4.5)
                    proxy_raw = raw.postprocess(
                        demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,
                        use_camera_wb=True,
                        no_auto_bright=False,  # Default False (Auto Brightness ON)
                        gamma=gamma_setting,  # [GT PROXY] Needs sRGB Gamma (2.22, 4.5)
                        output_bps=8,  # User requested 16 bit GT
                        # [GT PROXY] Needs sRGB Color Space for valid brightness fitting
                        output_color=rawpy.ColorSpace.sRGB,
                        highlight_mode=rawpy.HighlightMode.Blend,  # Corrected
                        user_flip=0,
                    )
                    # Convert to BGR
                    if proxy_raw.flags["WRITEABLE"]:
                        bgr_proxy = proxy_raw
                        b_channel_p = bgr_proxy[:, :, 0].copy()
                        bgr_proxy[:, :, 0] = bgr_proxy[:, :, 2]
                        bgr_proxy[:, :, 2] = b_channel_p
                        gt_proxy = bgr_proxy

            else:
                # STANDARD MODE (Gamma 2.222, Auto Brightness optional but usually on by default if not specified)
                gamma_setting = (2.222, 4.5)
                rgb = raw.postprocess(
                    demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,  # pyright: ignore[reportAttributeAccessIssue]
                    use_camera_wb=True,
                    # no_auto_bright=True,
                    gamma=gamma_setting,
                    output_bps=16,
                    output_color=rawpy.ColorSpace.sRGB,  # pyright: ignore[reportAttributeAccessIssue]
                    highlight_mode=rawpy.HighlightMode.Blend,  # pyright: ignore[reportAttributeAccessIssue]
                    user_flip=0,  # [FIX] Disable auto-rotation for processing consistency
                )

        if rgb.flags["WRITEABLE"]:
            bgr = rgb
            b_channel = bgr[:, :, 0].copy()
            bgr[:, :, 0] = bgr[:, :, 2]
            bgr[:, :, 2] = b_channel

            if generate_ref_proxy and "gt_proxy" in locals() and gt_proxy is not None:
                return (bgr, gt_proxy)

            return bgr
    except Exception as e:
        print(f"Error membaca RAW file {original_path}: {e}")
        return None


def load_images_from_paths(
    image_paths, stop_requested=None, linear_mode=False, capture_ref_proxy=False
):
    images = []
    raw_extensions = {".dng", ".cr2", ".nef", ".arw", ".orf", ".rw2", ".pef", ".srw"}
    num_threads = 3

    raw_futures = []
    standard_futures = []

    gt_proxy_result = None

    def _load_standard_with_orientation(path):
        try:
            from PIL import Image, ImageOps

            with Image.open(path) as img:
                img = ImageOps.exif_transpose(img)
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")
                img_np = np.array(img)
                return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Error loading standard image {path} with PIL: {e}")
            return cv2.imread(path, cv2.IMREAD_UNCHANGED)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for idx_path, path in enumerate(image_paths):
            if stop_requested and stop_requested():
                break

            _, ext = os.path.splitext(path)
            ext = ext.lower()

            # Check if this is the first image and we want proxy
            generate_proxy = capture_ref_proxy and (idx_path == 0)

            if ext in raw_extensions:
                if os.path.exists(path):
                    future = executor.submit(
                        _prepare_image_array_from_raw,
                        path,
                        linear_mode,
                        generate_ref_proxy=generate_proxy,  # Kwargs passed if function accepts it
                        # Note: _prepare_image_array_from_raw accepts *args or specific arg
                        # We updated it to accept generate_ref_proxy name
                    )
                    raw_futures.append(future)
            else:
                if os.path.exists(path):
                    future = executor.submit(cv2.imread, path, cv2.IMREAD_UNCHANGED)
                    standard_futures.append(future)

        # Ambil hasil dari gambar RAW
        for future in as_completed(raw_futures):
            if stop_requested and stop_requested():
                executor.shutdown(wait=False, cancel_futures=True)
                # Return partial or empty
                if capture_ref_proxy:
                    return images, None
                return images

            try:
                res = future.result()
                if res is not None:
                    # Check if tuple (dual return)
                    if isinstance(res, tuple):
                        img, proxy = res
                        images.append(img)
                        # We assume only one proxy is generated (from first image)
                        if gt_proxy_result is None:
                            gt_proxy_result = proxy
                    else:
                        images.append(res)
            except Exception as e:
                print(f"Error loading RAW image: {e}")

        # Ambil hasil dari gambar Standard
        for future in as_completed(standard_futures):
            if stop_requested and stop_requested():
                executor.shutdown(wait=False, cancel_futures=True)
                if capture_ref_proxy:
                    return images, None
                return images

            try:
                img = future.result()
                if img is not None:
                    images.append(img)
            except Exception as e:
                print(f"Error loading standard image: {e}")

    if capture_ref_proxy:
        return images, gt_proxy_result

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
    chunk_size = (
        total_items // num_threads if total_items >= num_threads else total_items
    )
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
        dset.attrs["metadata"] = json.dumps(metadata)


def save_align_to_folder(
    image, index, original_path, align_folder=None, load_config_func=None
):
    """
    Menyimpan gambar dalam format TIFF ke folder yang ditentukan,
    kemudian mengembalikan metadata dari file asli ke file output menggunakan exiftool.
    [MODIFIED] Menggunakan logika penyimpanan yang lebih robust dengan kontrol kompresi.
    """

    # Gunakan nilai default dari config jika align_folder tidak diberikan
    if align_folder is None:
        if load_config_func is None:
            raise ValueError(
                "Fungsi konfigurasi harus diberikan jika align_folder tidak diatur."
            )
        config = load_config_func()
        align_folder = config.get("align_folder")

    os.makedirs(align_folder, exist_ok=True)

    # Ambil nama file tanpa ekstensi dari original_path
    base_name = os.path.splitext(os.path.basename(original_path))[0]
    file_path = os.path.join(align_folder, f"{base_name}_align.tiff")

    try:

        save_params = [cv2.IMWRITE_TIFF_COMPRESSION, 1]

        # Simpan gambar dengan parameter
        success = cv2.imwrite(file_path, image, save_params)

        if not success:
            print(
                f"Peringatan: OpenCV gagal menyimpan TIFF dengan parameter ke '{file_path}'. Mencoba lagi tanpa parameter."
            )
            # Coba lagi tanpa parameter sebagai fallback
            success_fallback = cv2.imwrite(file_path, image)
            if not success_fallback:
                print(f"FATAL: Gagal total menyimpan gambar ke '{file_path}'")
                return None  # Hentikan proses jika penyimpanan gagal total
    except Exception as e:
        print(f"FATAL: Terjadi error saat menyimpan gambar ke '{file_path}': {e}")
        return None
    # =====================================================================

    # Logika multithreading untuk exiftool tidak berubah, karena sudah benar
    try:
        num_threads = os.cpu_count() or 4
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            future = executor.submit(
                subprocess.run,
                [
                    "exiftool",
                    "-overwrite_original",
                    "-TagsFromFile",
                    original_path,
                    file_path,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            future.result()  # Tunggu hingga proses selesai
    except Exception as e:
        print(
            f"Peringatan: Gagal menyalin metadata ke {file_path}. ExifTool mungkin tidak terpasang. Error: {e}"
        )

    return file_path


def save_image(image, output_path, reference_image_path=None):
    """
    Menyimpan gambar dengan kontrol kompresi untuk file TIFF demi kompatibilitas.
    Menyalin metadata orientasi dari gambar referensi menggunakan exiftool.
    """
    try:
        image_to_save = image
        ext = os.path.splitext(output_path)[1].lower()
        success = False

        if ext in [".tif", ".tiff"]:
            try:
                # 1. Konversi BGR (format dari cv2.rotate) kembali ke RGB jika perlu
                # Kita asumsikan gambar yang masuk ke save_image adalah BGR jika berwarna 3-channel
                if len(image_to_save.shape) == 3 and image_to_save.shape[2] >= 3:
                    # Pastikan konversi kembali ke RGB untuk tifffile
                    image_to_write_tifffile = cv2.cvtColor(
                        image_to_save, cv2.COLOR_BGR2RGB
                    )
                else:
                    image_to_write_tifffile = image_to_save

                # 2. Gunakan tifffile untuk menyimpan tanpa kompresi
                tifffile.imwrite(output_path, image_to_write_tifffile, compression=None)
                success = True
            except Exception as e:
                print(f"Error: Failed to save TIFF to '{output_path}': {e}")
                success = False

        else:
            # Jika bukan TIFF, gunakan cv2.imwrite seperti biasa
            save_params = []  # Tidak ada parameter kompresi khusus untuk non-TIFF
            success = cv2.imwrite(output_path, image_to_save, save_params)

        if not success:
            return None

        # --- Bagian ExifTool tidak berubah ---
        if reference_image_path and os.path.exists(reference_image_path):
            try:
                # Salin metadata dari referensi
                subprocess.run(
                    [
                        "exiftool",
                        "-q",
                        "-overwrite_original",
                        "-TagsFromFile",
                        reference_image_path,
                        output_path,
                    ],
                    check=True,
                    capture_output=True,
                )
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                # Ini bukan error fatal, hanya peringatan
                print(
                    f" Warning: Failed to copy metadata to '{output_path}'. ExifTool may not be installed. Error: {e}"
                )

        return output_path

    except Exception as e:
        print(f"Error fatal saat menyimpan gambar ke '{output_path}': {e}")
        traceback.print_exc()
        return None


def calculate_scale_from_gt_proxy(linear_img, gt_proxy, ref_dtype=np.uint16):
    """
    Menghitung faktor skala optimal untuk `to_gamma_proxy` dengan membandingkan
    Green Channel dari Linear Image (RAW Space) dengan Green Channel dari GT Proxy (sRGB).

    Args:
        linear_img: Gambar Linear (Main Image), BGR.
        gt_proxy: Gambar Ground Truth dari rawpy (sRGB), BGR.
        ref_dtype: Tipe data referensi (uint16/uint8).

    Returns:
        float: Faktor skala (scale) yang optimal.
    """
    # 1. Pastikan input float32 [0, 1]
    if linear_img.dtype == np.uint16:
        l_img = linear_img.astype(np.float32) / 65535.0
    elif linear_img.dtype == np.uint8:
        l_img = linear_img.astype(np.float32) / 255.0
    else:
        l_img = linear_img

    if gt_proxy.dtype == np.uint16:
        g_img = gt_proxy.astype(np.float32) / 65535.0
    elif gt_proxy.dtype == np.uint8:
        g_img = gt_proxy.astype(np.float32) / 255.0
    else:
        g_img = gt_proxy

    # 2. Ambil Green Channel (Index 1) untuk perbandingan brightness
    # Mengurangi dampak perbedaan Color Matrix pada R/B
    if l_img.ndim == 3:
        l_green = l_img[:, :, 1]
    else:
        l_green = l_img

    if g_img.ndim == 3:
        g_green = g_img[:, :, 1]
    else:
        g_green = g_img

    target_mean = np.mean(g_green)

    # 3. Binary Search untuk mencari Scale
    # Range pencarian: 0.1x sampai 20.0x exposure
    min_scale = 0.1
    max_scale = 50.0
    best_scale = 1.0
    min_diff = float("inf")

    # Gamma params default
    gamma_pow = 2.22
    slope = 4.5
    cutoff = 0.018

    # Fungsi bantu hitung mean setelah gamma
    def get_mean_after_gamma(s):
        # Apply scale + gamma curve (vectorized)
        scaled = l_green * s
        # Clip
        scaled = np.clip(scaled, 0.0, 1.0)
        # Gamma
        res = np.where(
            scaled < cutoff,
            scaled * slope,
            1.099 * np.power(scaled, 1.0 / gamma_pow) - 0.099,
        )
        return np.mean(res)

    # Iterasi (misal 15 iterasi binary search cukup presisi)
    for _ in range(15):
        mid = (min_scale + max_scale) / 2
        curr_mean = get_mean_after_gamma(mid)

        if curr_mean < target_mean:
            min_scale = mid
        else:
            max_scale = mid

    best_scale = (min_scale + max_scale) / 2
    print(
        f" [Smart Proxy] Fitted Scale: {best_scale:.4f} (Target Mean: {target_mean:.4f})"
    )
    return best_scale


def save_linear_dng(image, output_path, reference_image_path):
    """
    Menyimpan gambar sebagai Linear DNG (RGB) dengan kompresi Deflate.
    """
    if image.dtype != np.uint16:
        # Konversi ke 16-bit uint
        image_uint16 = (image * 65535).astype(np.uint16)
    else:
        image_uint16 = image

    # Pastikan RGB (tifffile expects RGB)
    if image_uint16.ndim == 3 and image_uint16.shape[2] == 3:
        # Convert BGR (OpenCV) -> RGB
        image_to_save = cv2.cvtColor(image_uint16, cv2.COLOR_BGR2RGB)
    else:
        image_to_save = image_uint16

    # 1. Simpan sebagai TIFF Kompresi (Deflate/Zlib)
    # compression='zlib' biasanya kompatibel dengan DNG deflate
    tifffile.imwrite(output_path, image_to_save, compression="zlib")

    # 2. Inject DNG Tags dengan ExifTool
    # Kita menggunakan tag dari Reference Image, tapi override beberapa hal penting
    if reference_image_path and os.path.exists(reference_image_path):
        subprocess.run(
            [
                "exiftool",
                "-q",
                "-overwrite_original",
                "-TagsFromFile",
                reference_image_path,
                "-all:all",  # Copy all tags
                "-SubfileType=0",  # Full resolution image
                "-PhotometricInterpretation=LinearRaw",  # 34892
                "-Orientation=1",  # Reset orientation
                "-Compression=Deflate",  # [CRITICAL] Set metadata Compression=8 (Deflate)
                "-DefaultScale=1.0",
                "-BlackLevel=0",  # Data sudah bersih
                "-WhiteLevel=65535",  # Full range
                output_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    return output_path


def save_special_jpg_and_png(
    img_np: np.ndarray,
    dst_path: str,
    reference_image_path: str = None,
    # --- Parameter Kompresi Baru ---
    quality: int = 98,
    optimize: bool = True,
    png_compress_level: int = 8,
) -> str:
    """
    Mengkonversi array NumPy, menerapkan rotasi, dan menyimpannya ke JPG/PNG
    dengan opsi kompresi yang lebih agresif dan cerdas.
    """
    if img_np is None:
        raise ValueError("Data gambar input (img_np) tidak boleh None.")

    # Logika untuk menangani orientasi (tetap sama)
    if reference_image_path and os.path.exists(reference_image_path):
        try:
            h, w = img_np.shape[:2]
            if h > w:
                img_np = cv2.rotate(img_np, cv2.ROTATE_180)
            else:
                with Image.open(reference_image_path) as ref_img:
                    orientation = ref_img.getexif().get(274, 1)

                if orientation == 3:
                    img_np = cv2.rotate(img_np, cv2.ROTATE_180)
                elif orientation == 6:
                    img_np = cv2.rotate(img_np, cv2.ROTATE_90_CLOCKWISE)
                elif orientation == 8:
                    img_np = cv2.rotate(img_np, cv2.ROTATE_90_COUNTERCLOCKWISE)
        except Exception:
            pass

    # Konversi tipe data jika perlu (tetap sama)
    image_to_save = img_np
    if image_to_save.dtype == "uint16":
        image_to_save = (image_to_save / 256).astype("uint8")

    img = Image.fromarray(image_to_save)

    file_ext = os.path.splitext(dst_path)[1].lower()

    # --- Logika Penyimpanan yang Ditingkatkan ---
    if file_ext in [".jpg", ".jpeg"]:
        save_kwargs = {
            "quality": quality,
            "optimize": True,
            "progressive": True,  # Membuat JPG dimuat secara bertahap, kadang bisa sedikit lebih kecil
        }
        # Mengaktifkan Chroma Subsampling untuk ukuran file yang jauh lebih kecil
        if optimize:
            # '4:2:0' adalah standar untuk web dan sangat efisien.
            # Kode asli Anda menggunakan `subsampling=0` ('4:4:4') yang menjaga semua info warna.
            save_kwargs["subsampling"] = "4:2:0"
        else:
            # Jika tidak mau subsampling, samakan seperti kode asli Anda
            save_kwargs["subsampling"] = 0

        img.save(dst_path, **save_kwargs)

    elif file_ext == ".png":
        img.save(
            dst_path,
            optimize=True,
            compress_level=png_compress_level,  # Level 0 (tanpa kompresi) hingga 9 (maksimal)
        )
    else:
        # Fallback untuk format lain
        img.save(dst_path)

    # Logika menyalin metadata (tetap sama)
    if reference_image_path and os.path.exists(reference_image_path):
        try:
            subprocess.run(
                [
                    "exiftool",
                    "-overwrite_original",
                    "-TagsFromFile",
                    reference_image_path,
                    dst_path,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.run(
                ["exiftool", "-overwrite_original", "-Orientation=1", dst_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    return dst_path


def extract_exif(image_path):
    """
    Mengambil metadata EXIF dari file gambar menggunakan exifread.
    Mengembalikan dictionary dengan data EXIF dan path file.
    """
    with open(image_path, "rb") as f:
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
    if img is None:
        raise ValueError("Input image is None.")
    if img.ndim == 3 and img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif img.ndim == 3 and img.shape[2] == 4:
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)  # Tambahkan handle BGRA
    elif img.ndim == 2:
        gray = img
    else:
        raise ValueError(f"Invalid image dimensions/channels: {img.shape}")

    if gray.dtype != np.uint8:
        max_val = np.max(gray)
        if gray.dtype == np.float32 or gray.dtype == np.float64:
            if max_val <= 1.0 and np.min(gray) >= 0:
                gray_norm = (gray * 255.0).astype(np.uint8)
            else:
                if gray.dtype == np.uint16:
                    gray_norm = (gray / 256.0).astype(
                        np.uint8
                    )  # Asumsi 16-bit ke 8-bit
                elif gray.dtype == np.int16:
                    gray_norm = ((gray / 256.0) + 128).astype(
                        np.uint8
                    )  # Perkiraan kasar
                else:
                    gray_norm = cv2.normalize(
                        gray, None, 0, 255, cv2.NORM_MINMAX
                    ).astype(np.uint8)
        elif gray.dtype == np.uint16:
            gray_norm = (gray / 256.0).astype(np.uint8)
        else:
            gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(
                np.uint8
            )
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
                clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(3, 3))
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
                processed_image = cv2.normalize(
                    image, None, 0, 255, cv2.NORM_MINMAX
                ).astype(np.uint8)
        else:
            processed_image = cv2.normalize(
                image, None, 0, 255, cv2.NORM_MINMAX
            ).astype(np.uint8)

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

    padded = cv2.copyMakeBorder(
        resized,
        top,
        bottom,
        left,
        right,
        borderType=cv2.BORDER_CONSTANT,
        value=pad_color,
    )
    return padded


def resize_all_with_padding(
    images,
    method="preserve",
    verbose=False,
    pad_color=(0, 0, 0),
    return_original_sizes=False,
    stop_requested=None,
    force_even=False,
):
    """
    Resize + pad all images to the same size using letterbox strategy.

    Args:
        images (list): Daftar array gambar (NumPy).
        method (str): Strategi penentuan ukuran target. Pilihan:
            - "min"      : gunakan tinggi & lebar minimum dari semua gambar.
            - "max"      : gunakan tinggi & lebar maksimum dari semua gambar.
            - "median"   : gunakan median tinggi & lebar dari semua gambar.
            - "preserve" : gunakan ukuran gambar pertama sebagai referensi.
        verbose (bool): Jika True, cetak informasi proses.
        pad_color (tuple): Warna padding (B, G, R).
        return_original_sizes (bool): Jika True, juga kembalikan ukuran asli.
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
    elif method == "preserve":
        # Ambil ukuran gambar pertama sebagai referensi
        target_h, target_w = original_sizes[0]
    else:
        raise ValueError(
            "Unsupported resize method. Use 'min', 'max', 'median', or 'preserve'."
        )

    # Force even dimensions if requested
    if force_even:
        target_h = (target_h // 2) * 2
        target_w = (target_w // 2) * 2
        if verbose:
            print(
                f"[Padding] Force Even: ({original_sizes[0][0]}x{original_sizes[0][1]}) -> ({target_h}x{target_w})"
            )

    if verbose:
        print(f"Resizing all images to {target_w}x{target_h} using method: {method}")

    # --- di sini lanjutkan proses resize + padding sesuai target_h, target_w ---

    resized_images = []
    for img, (h, w) in zip(images, original_sizes):
        if stop_requested and stop_requested():
            if return_original_sizes:
                return [], None, []
            return [], None

        if h == target_h and w == target_w:
            resized_images.append(img)
        else:
            resized_images.append(
                resize_with_padding(img, (target_h, target_w), pad_color=pad_color)
            )

    result = (resized_images, (target_h, target_w))
    return result if not return_original_sizes else (*result, original_sizes)


@lru_cache(maxsize=3200)
def gaussian_window(size, sigma_scale=1 / 6):
    """Menghasilkan jendela Gaussian 2D [0, 1] float32 C-contiguous."""
    rows, cols = size
    if rows <= 0 or cols <= 0:
        return np.zeros((0, 0), dtype=np.float32)
    sigma_y = max(rows * sigma_scale, 1e-6)
    sigma_x = max(cols * sigma_scale, 1e-6)
    y = np.arange(0, rows, 1, float) - (rows - 1) / 2
    x = np.arange(0, cols, 1, float) - (cols - 1) / 2
    gaussian_y = np.exp(-(y**2) / (2 * sigma_y**2 + 1e-12))
    gaussian_x = np.exp(-(x**2) / (2 * sigma_x**2 + 1e-12))
    window = np.outer(gaussian_y, gaussian_x)
    max_val = window.max()
    if max_val > 1e-6:
        window = window / max_val
    else:
        window = np.zeros_like(window)
    return np.ascontiguousarray(window.astype(np.float32))


# ================= Replikasi Fungsi C++ untuk Estimasi Noise & Pra-pemrosesan Gambar Referensi =================
_CLAHE_CACHE = {}
_SIGMOID_LUT_CACHE = {}


def estimate_noise_in_python(ref_image_gray_float):
    if ref_image_gray_float is None or ref_image_gray_float.size == 0:
        return 0.015
    H, W = ref_image_gray_float.shape
    block_size = 8
    min_blocks = 4
    if H < block_size * 2 or W < block_size * 2:
        native_img = ref_image_gray_float.copy()
        lap = cv2.Laplacian(native_img, cv2.CV_32F, ksize=3)
        return float(np.median(np.abs(lap - np.median(lap))) * 1.4826)
    img_lap = cv2.Laplacian(ref_image_gray_float, cv2.CV_32F, ksize=3)
    h_cut = (H // block_size) * block_size
    w_cut = (W // block_size) * block_size
    img_cut = img_lap[:h_cut, :w_cut]
    blocks = (
        img_cut.reshape(
            h_cut // block_size, block_size, w_cut // block_size, block_size
        )
        .transpose(0, 2, 1, 3)
        .reshape(-1, block_size * block_size)
    )
    block_medians = np.median(blocks, axis=1, keepdims=True)
    block_mads = np.median(np.abs(blocks - block_medians), axis=1)
    keep_ratio = 0.2
    num_keep = max(min_blocks, int(len(block_mads) * keep_ratio))
    estimated_sigma = np.median(np.partition(block_mads, num_keep)[:num_keep]) * 1.4826
    return float(np.clip(estimated_sigma, 0.00001, 0.99999))


def apply_s_curve_float32(img: np.ndarray, strength: float = 4.0, pivot: float = 0.5):
    """
    S-Curve float32 dengan pivot.
    Input: 0..255 float32
    Output: float32 0..255
    """
    x = img / 255.0  # tetap float32

    # sigmoid dengan pivot
    y = 1.0 / (1.0 + np.exp(-strength * (x - pivot)))

    return (y * 255.0).astype(np.float32)


# preprocess_in_python has been moved to:
# taichi_library.taichi_algorithm.preprocess
# Use: preprocess.preprocess_in_python_gpu() instead
# This provides automatic GPU/CPU fallback with identical API


def preprocess_in_python(ref_image_float: np.ndarray, s_curve_contrast: float = 4.0):
    """
    Melakukan semua pra-pemrosesan gambar referensi di Python.
    [MODIFIED] Hanya melakukan konversi ke grayscale sesuai permintaan user.
    Mengembalikan gambar grayscale dan nilai noise-nya (estimasi cepat).
    """
    if ref_image_float.ndim == 3 and ref_image_float.shape[2] > 1:
        ref_gray = cv2.cvtColor(ref_image_float, cv2.COLOR_BGR2GRAY)
    else:
        ref_gray = ref_image_float.copy()

    # Perkirakan noise (diperlukan untuk kompatibilitas signature return)
    noise_sigma = estimate_noise_in_python(ref_gray)

    return ref_gray, noise_sigma


def estimate_noise_variance(
    gray_image, edge_threshold_low=70, dilate_kernel_size=4, min_flat_pixels_ratio=0.1
):
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
        return 0.0  # Atau nilai default yang sesuai

    # 1. Deteksi tepi untuk mengidentifikasi area non-datar
    edges = cv2.Canny(gray_image, edge_threshold_low, edge_threshold_low * 2)

    # 2. Dilatasi tepi untuk sedikit memperluas area non-datar
    kernel = np.ones((dilate_kernel_size, dilate_kernel_size), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)

    # 3. Buat mask untuk area "datar" (piksel yang bukan bagian dari tepi yang diperluas)
    flat_mask = (dilated_edges == 0).astype(np.bool_)

    # Periksa apakah ada cukup piksel "datar"
    num_flat_pixels = np.sum(flat_mask)
    if num_flat_pixels < (gray_image.size * min_flat_pixels_ratio):
        laplacian_full = cv2.Laplacian(gray_image, cv2.CV_64F)
        return laplacian_full.var()

    # 4. Hitung Laplacian dari gambar asli
    laplacian_output = cv2.Laplacian(gray_image, cv2.CV_64F)

    # 5. Hitung varians hanya pada piksel yang dianggap "datar"
    variance = laplacian_output[flat_mask].var()

    return variance


def get_adaptive_bilateral(
    noise_level, min_noise, max_noise, min_d, max_d, min_sigma, max_sigma
):
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


def normalize_image(image, dtype, out=None):
    """
    Normalisasi gambar ke range [0, 1] float32.
    - Jika `out` disediakan, hasil akan disalin ke buffer tersebut (otomatis disesuaikan ukuran & dimensi).
    - Jika `out` tidak ada, fungsi akan membuat array baru.
    - Menangani RGB dan grayscale secara otomatis.

    Args:
        image: np.ndarray (grayscale 2D atau RGB 3D)
        dtype: tipe data asli dari gambar (mis. np.uint8, np.uint16)
        out: buffer opsional (np.ndarray dengan dtype=float32 dan dimensi sama)

    Returns:
        np.ndarray (float32, 3 channel)
    """

    # --- 1. Tentukan skala berdasarkan dtype ---
    if np.issubdtype(dtype, np.integer):
        scale = np.float32(np.iinfo(dtype).max)
    elif np.issubdtype(dtype, np.floating):
        scale = 1.0
    else:
        raise TypeError(f"Unsupported dtype for normalization: {dtype}")

    # --- 2. Pastikan gambar dalam float32 ---
    img_float = image.astype(np.float32, copy=False)

    # --- 3. Normalisasi in-place jika memungkinkan ---
    if scale > 1e-6:
        img_float = img_float / scale

    # --- 4. Pastikan output memiliki 3 channel ---
    if img_float.ndim == 2:
        # Grayscale → ubah jadi RGB 3-channel
        img_float = np.stack((img_float, img_float, img_float), axis=-1)

    # --- 5. Sesuaikan buffer 'out' jika diberikan ---
    if out is not None:
        # Pastikan ukuran & tipe sesuai
        if out.shape != img_float.shape or out.dtype != np.float32:
            out.resize(img_float.shape, refcheck=False)
            out[:] = np.zeros_like(img_float, dtype=np.float32)
        np.copyto(out, img_float, casting="unsafe")
        return out

    return img_float


def calculate_auto_scale(linear_img_float, target_mean=0.25):
    """
    Menghitung scale factor agar rata-rata brightness mendekati target_mean.
    Digunakan untuk normalisasi brightness referensi sebelum estimasi gamma proxy.
    linear_img_float: HxWx3 (Linear RGB) atau HxW (Gray), range 0.0-1.0
    """
    if linear_img_float.ndim == 3:
        # Gunakan Green channel sebagai representasi luminance paling akurat untuk RAW
        vals = linear_img_float[:, :, 1]
    else:
        vals = linear_img_float

    # Gunakan mean (cepat & cukup akurat untuk auto-exposure sederhana)
    avg_val = np.mean(vals)

    if avg_val <= 1e-6:
        return 1.0

    scale = target_mean / avg_val

    # Batasi scale agar tidak meledakkan noise ekstrem
    scale = np.clip(scale, 1.0, 100.0)

    return float(scale)


def to_gamma_proxy(linear_img, scale=1.0, gamma_pow=2.22, slope=4.5, cutoff=0.018):
    """
    Konversi Linear [0,1] ke Gamma Proxy [0,1] untuk Alignment.
    Menggunakan parameter tuning manual: Scale, Gamma, Slope, Cutoff.
    """
    # 1. Exposure Scaling (Manual / Auto-calculated passed as scale)
    # Gunakan in-place multiplication jika memungkinkan untuk hemat RAM, tapi hati-hati reference changes.
    # np.clip returns new array, safe.
    img = np.clip(linear_img * scale, 0.0, 1.0)

    # 2. Gamma Curve (BT.709 Style with custom params)
    # y = s * x               if x < cutoff
    # y = (1+a) * x^(1/g) - a if x >= cutoff
    # Dimana 'a' (offset) implisit menjadi 0.099 seperti Rec.709 standar atau sebaiknya dihitung agar continue?
    # User function: 1.099 * pow(...) - 0.099 implies a=0.099.

    res = np.where(
        img < cutoff, img * slope, 1.099 * np.power(img, 1.0 / gamma_pow) - 0.099
    )

    # Pastikan output float32 valid
    return np.clip(res, 0.0, 1.0).astype(np.float32)


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
            raise ValueError(
                f"Input mkptsL harus berbentuk (N, 2), tetapi ditemukan {mkptsL.shape}"
            )

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
                    if (
                        np.linalg.norm(pt - grid[cell_key]) < distance_thresh
                    ):  # SEKARANG: Menghitung jarak Euclidean yang benar
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
        if transformation_type == "homography":
            compensated_padded = cv2.warpPerspective(
                padded_image,
                matrix,
                (target_w_padded, target_h_padded),
                flags=interpolation_flag,
                borderMode=cv2.BORDER_REFLECT,
            )
        else:
            compensated_padded = cv2.warpAffine(
                padded_image,
                matrix,
                (target_w_padded, target_h_padded),
                flags=interpolation_flag,
                borderMode=cv2.BORDER_REFLECT,
            )

        # Lakukan cropping untuk kembali ke ukuran gambar asli
        # Pemeriksaan keamanan jika hasil warp lebih kecil dari yang diharapkan
        if (
            pad + h > compensated_padded.shape[0]
            or pad + w > compensated_padded.shape[1]
        ):
            # Fallback: warp langsung tanpa menjaga tepi jika cropping tidak memungkinkan
            if transformation_type == "homography":
                return cv2.warpPerspective(
                    image,
                    matrix,
                    (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_CONSTANT,
                )
            else:
                return cv2.warpAffine(
                    image,
                    matrix,
                    (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_CONSTANT,
                )
        else:
            return compensated_padded[pad : pad + h, pad : pad + w]

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
    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(
        -1, 1, 2
    )
    try:
        if transformation_type == "homography":
            if matrix.shape != (3, 3):
                return None
            transformed_corners = cv2.perspectiveTransform(corners, matrix)
        else:  # affine, similarity, euclidean
            if matrix.shape != (2, 3):
                return None
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
    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(
        -1, 1, 2
    )

    if transformation_type == "homography":
        matrix, mask = cv2.findHomography(
            np.array(base_points), np.array(target_points), cv2.RANSAC
        )
    else:
        matrix, mask = cv2.estimateAffine2D(
            np.array(base_points), np.array(target_points), method=cv2.RANSAC
        )

    # Debugging jumlah keypoint dan inlier
    if matrix is None or mask is None:
        # print(f"[DEBUG] Transform #{i}: transform matrix is None. Total points: {len(base_points)}")
        return None
    else:
        inlier_count = int(mask.sum())
        total_points = len(base_points)
        # print(f"[DEBUG] Transform #{i}: total points = {total_points}, inliers = {inlier_count}")

    # Transform corners
    if transformation_type == "homography":
        transformed_corners = cv2.perspectiveTransform(corners, matrix)
    else:
        transformed_corners = cv2.transform(corners, matrix)

    transformed_corners = transformed_corners.reshape(-1, 2)
    min_xy = transformed_corners.min(axis=0)
    max_xy = transformed_corners.max(axis=0)

    return min_xy, max_xy


def compute_global_crop(
    all_transforms, total_images, w, h, transformation_type="homography"
):
    global_min_x = float("inf")
    global_min_y = float("inf")
    global_max_x = -float("inf")
    global_max_y = -float("inf")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(
                compute_transform_bounds, transform, w, h, transformation_type
            )
            for transform in all_transforms
        ]

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
    return image[crop_y : crop_y + crop_h, crop_x : crop_x + crop_w]


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
        return []  # Kembalikan list kosong jika tidak ada gambar

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


def run_pipeline_non_crop(
    processor,
    image_paths,
    base_image,
    target_dims,
    update_progress,
    stop_requested,
    save_align,
    align_folder,
    h5_file_handle,
    num_workers,
):
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
        update_progress(
            1,
            total_images_in_stack,
            language_config.IMAGE_PROCESS_IN_PROGRESS.format(1, total_images_in_stack),
        )

    if save_align:
        save_align_to_folder(base_image, 0, image_paths[0], align_folder)
    if h5_file_handle:
        with h5_lock:
            save_to_hdf5(
                h5_file_handle, "image_0", base_image, extract_exif(image_paths[0])
            )

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
                compensated = processor.compensate_motion(
                    target_image, base_pts, target_pts
                )
                if compensated is not None:
                    if save_align:
                        save_align_to_folder(compensated, i, path, align_folder)
                    if h5_file_handle:
                        with h5_lock:
                            save_to_hdf5(
                                h5_file_handle,
                                f"image_{i}",
                                compensated,
                                extract_exif(path),
                            )
        except Exception as e:
            # Penting untuk menangkap exception di sini agar bisa di-raise di thread utama
            print(f"⚠️ Error processing image {i} ({os.path.basename(path)}): {e}")
            raise  # Melempar kembali exception agar future.result() bisa menangkapnya
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
                break  # Keluar dari loop jika diminta berhenti

            path = future_to_path[future]
            try:
                # Panggil .result() untuk memeriksa apakah ada exception di dalam thread
                future.result()
            except Exception as exc:
                print(
                    f"Task for {os.path.basename(path)} generated an exception: {exc}"
                )

            # Update progress di sini, di thread utama!
            completed_count += 1
            if update_progress:
                update_progress(
                    completed_count,
                    total_images_in_stack,
                    language_config.IMAGE_PROCESS_IN_PROGRESS.format(
                        completed_count, total_images_in_stack
                    ),
                )


def run_pipeline_global_crop(
    processor,
    image_paths,
    base_image,
    target_dims,
    update_progress,
    stop_requested,
    transformation_type,
    save_align,
    align_folder,
    h5_file_handle,
    num_workers,
):
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
        processor,
        images_to_process_for_transforms,
        base_image,
        target_dims,
        update_progress,
        stop_requested,
        num_workers=num_workers,
    )
    if not all_transforms:
        print("Transform calculation failed for all images. Aborting global crop.")
        return

    if len(all_transforms) < len(images_to_process_for_transforms):
        failed_count = len(images_to_process_for_transforms) - len(all_transforms)
        print(
            f"Warning: Could not calculate transforms for {failed_count} image(s). Continuing with the successful ones."
        )

    if update_progress:
        update_progress(50, 100, "Computing global crop bounds...")

    crop_bounds = compute_global_crop(
        [(item[0], item[2], item[3]) for item in all_transforms],
        total_images_in_stack,
        base_image.shape[1],
        base_image.shape[0],
        transformation_type=transformation_type,
    )
    if crop_bounds is None:
        return

    # --- TAHAP 3: Apply & Save (50% -> 100%) ---
    _run_apply_and_save_stage(
        processor,
        all_transforms,
        crop_bounds,
        target_dims,
        update_progress,
        stop_requested,
        save_align,
        align_folder,
        h5_file_handle,
        base_image,
        image_paths[0],
        num_workers=num_workers,
    )


def _run_transform_calculation_stage(
    processor,
    image_paths,
    base_image,
    target_dims,
    update_progress,
    stop_requested,
    num_workers,
):
    """Tahap 1 yang disederhanakan: Menghitung transformasi secara paralel."""
    import os

    all_transforms = []
    num_to_process = len(image_paths)
    if num_to_process == 0:
        return all_transforms

    # --- Fungsi Worker Tunggal ---
    def calculate_transform_task(i, path):
        if stop_requested and stop_requested():
            return None
        try:
            img_list = load_images_from_paths([path], stop_requested=stop_requested)
            if not img_list or img_list[0] is None:
                return None

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
        future_to_task = {
            executor.submit(calculate_transform_task, i, path): i
            for i, path in enumerate(image_paths, start=1)
        }

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
                status = language_config.RUN_PROCESS_TRANSFORMATION.format(
                    results_received, num_to_process
                )
                update_progress(int(percent), 100, status)

    all_transforms.sort(key=lambda x: x[0])
    return all_transforms


def _run_apply_and_save_stage(
    processor,
    temp_transforms,
    crop_bounds,
    target_dims,
    update_progress,
    stop_requested,
    save_align,
    align_folder,
    h5_file_handle,
    base_image,
    base_image_path,
    num_workers,
):
    """Tahap 3 yang disederhanakan: Menerapkan transformasi dan menyimpan secara paralel."""

    h5_lock = threading.Lock()
    progress_lock = threading.Lock()

    tasks = [(0, base_image_path, None, None, base_image)] + [
        (i, path, base_pts, target_pts, None)
        for i, path, base_pts, target_pts in temp_transforms
    ]

    num_to_save = len(tasks)
    completed_counter = {"count": 0}

    # --- Fungsi Worker Tunggal ---
    def apply_and_save_task(task_data):
        i, path, base_pts, target_pts, image_data = task_data
        if stop_requested and stop_requested():
            return

        try:
            # 1. Muat gambar jika diperlukan
            if image_data is None:
                img_list = load_images_from_paths([path], stop_requested=stop_requested)
                if not img_list or img_list[0] is None:
                    return
                image_data = resize_with_padding(img_list[0], target_dims)

            # 2. Proses: Kompensasi & Crop
            processed_image = None
            if i > 0:  # Target image
                if base_pts is not None and target_pts is not None:
                    compensated = processor.compensate_motion(
                        image_data, base_pts, target_pts
                    )
                    if compensated is not None:
                        processed_image = crop_image(compensated, crop_bounds)
            else:  # Base image
                processed_image = crop_image(image_data, crop_bounds)

            # 3. Simpan
            if processed_image is not None:
                if save_align:
                    save_align_to_folder(processed_image, i, path, align_folder)
                if h5_file_handle:
                    with h5_lock:
                        save_to_hdf5(
                            h5_file_handle,
                            f"image_{i}",
                            processed_image,
                            extract_exif(path),
                        )
        except Exception as e:
            print(f"⚠️ Apply/Save error {i} ({os.path.basename(path)}): {e}")
        finally:
            # 4. Update Progress & Cleanup
            with progress_lock:
                completed_counter["count"] += 1
                count = completed_counter["count"]
                if update_progress:
                    percent = 50 + (count / num_to_save) * 50
                    status = language_config.RUN_SAVING_TRANSFORMATION.format(
                        count, num_to_save
                    )
                    update_progress(int(percent), 100, status)

            del image_data
            if "processed_image" in locals():
                del processed_image
            if "compensated" in locals():
                del compensated
            gc.collect()

    # --- Eksekusi Menggunakan ThreadPoolExecutor ---
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for task in tasks:
            if stop_requested and stop_requested():
                break
            executor.submit(apply_and_save_task, task)
