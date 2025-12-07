from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor
import os
import time
import concurrent
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap, QImage
import rawpy

from config import SUPPORTED_FORMATS


class BaseMultiThreading(QThread):
    """
    Base class for multithreading tasks. This class supports batch processing.
    """
    progress_signal = Signal(int, int)  # Mengirim progres (dalam persen) dan jumlah item tersisa
    completion_signal = Signal(int)    # Mengirim jumlah total item setelah selesai
    result_signal = Signal(object)     # Mengirim hasil dari setiap tugas
    error_signal = Signal(str)         # Mengirim pesan error jika ada

    def __init__(self, task_function, items, batch_size=3, delay_ms=50):
        super().__init__()
        self.task_function = task_function  # Fungsi tugas yang akan dijalankan
        self.items = items                  # Daftar item yang akan diproses
        self.batch_size = batch_size        # Ukuran batch
        self.delay_ms = delay_ms            # Waktu jeda antar batch
        self._is_running = True   

    def run(self):
        total_items = len(self.items)
        current_batch = 0

        while current_batch * self.batch_size < total_items:
            start_index = current_batch * self.batch_size
            end_index = min((current_batch + 1) * self.batch_size, total_items)
            batch = self.items[start_index:end_index]

            for i, item in enumerate(batch):
                if not self._is_running:
                    break
                try:
                    # Jalankan fungsi tugas dan ambil hasilnya
                    result = self.task_function(item)
                    self.result_signal.emit(result)  # Kirim hasil ke sinyal
                except Exception as e:
                    self.error_signal.emit(str(e))
                    continue

                global_index = start_index + i + 1
                progress = int(global_index / total_items * 100)
                items_left = total_items - global_index
                self.progress_signal.emit(progress, items_left)

            current_batch += 1
            self.msleep(self.delay_ms)

        self.completion_signal.emit(total_items)

    def stop(self):
        """Set the running flag to False to stop the thread."""
        self._is_running = False
    
    
        
def _process_image_part(img_part_data):
    """Memproses bagian gambar (NumPy array). Melakukan konversi warna/tipe jika perlu."""
    img_part = img_part_data.copy()

    try:
        if img_part.dtype == np.uint16:
            img_part = (img_part / 256).astype(np.uint8)
        elif img_part.dtype != np.uint8:
             raise ValueError(f"Tipe data kuadran tidak valid: {img_part.dtype}")

        processed_part = img_part # Default jika sudah RGB

        # Konversi warna jika perlu
        if len(img_part.shape) == 2: # Grayscale
            processed_part = cv2.cvtColor(img_part, cv2.COLOR_GRAY2RGB)
        elif img_part.shape[2] == 4: # RGBA
            processed_part = cv2.cvtColor(img_part, cv2.COLOR_RGBA2RGB)

        # Pastikan output adalah RGB uint8
        if len(processed_part.shape) != 3 or processed_part.shape[2] != 3 or processed_part.dtype != np.uint8:
            pass
            # raise RuntimeError(f"Pemrosesan kuadran gagal menghasilkan RGB uint8: shape={processed_part.shape}, dtype={processed_part.dtype}")

        return processed_part

    except Exception as e:
        pass
        raise RuntimeError(f"Failed to process quadrant: {e}")

class RawImageProcessingThread(BaseMultiThreading):
    """
    Thread untuk memproses gambar dari path file menjadi QPixmap atau QImage.
    
    Mendukung dua mode operasi:
    1.  Resolusi Penuh (default):
        Memuat gambar dengan kualitas penuh, menerapkan pemrosesan paralel
        untuk format tertentu, dan menghasilkan QPixmap.
        
    2.  Resolusi Rendah (diaktifkan dengan `low_res_target_size`):
        Mengambil jalur cepat untuk memuat, mengubah ukuran gambar ke target
        yang ditentukan, dan menghasilkan tuple (path, QImage). Mode ini
        dirancang untuk pra-pemuatan (pre-caching) yang cepat.
    """
    def __init__(self, image_paths, batch_size=1, delay_ms=100, low_res_target_size=None):
        """
        Inisialisasi thread pemrosesan.

        Args:
            image_paths (list): Daftar path gambar yang akan diproses.
            batch_size (int): Ukuran batch untuk pemrosesan.
            delay_ms (int): Jeda antar batch.
            low_res_target_size (int, optional): Jika diisi, mengaktifkan mode resolusi
                                                 rendah. Nilai ini adalah ukuran (dalam piksel)
                                                 untuk sisi terpanjang gambar thumbnail.
        """
        self.low_res_mode = low_res_target_size is not None
        self.target_size = low_res_target_size

        try:
             total_cores = os.cpu_count()
             self.num_part_workers = max(1, (total_cores // 2) if total_cores else 2)
        except NotImplementedError:
             self.num_part_workers = 2
        
        def process_image(image_path):
            try:
                # =======================================================
                # TAHAP 1: PEMBACAAN FILE DAN KONVERSI AWAL KE NP.ARRAY
                # =======================================================
                filename = os.path.basename(image_path)
                extension = os.path.splitext(image_path)[1].lower()
                img_array = None
                
                is_raw = any(extension in formats for key, formats in SUPPORTED_FORMATS.items() if key == "raw")
                if is_raw:
                    try:
                        with rawpy.imread(image_path) as raw:
                            # Pemrosesan dasar untuk mendapatkan array RGB 8-bit
                            gamma_setting = (2.222, 4.5)
                            # gamma_setting = (1,1)
                            img_array = raw.postprocess(
                                demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,
                                four_color_rgb=True,
                                use_camera_wb=True,
                                # no_auto_bright=True,
                                gamma=gamma_setting,
                                output_bps=8,
                                output_color=rawpy.ColorSpace.sRGB,
                                highlight_mode=rawpy.HighlightMode.Blend,
                            )
                            if img_array is None: raise RuntimeError(f"Rawpy postprocessing failed for {filename}")
                    except rawpy.LibRawError as e: raise RuntimeError(f"Rawpy Error for {filename}: {e}")
                    except Exception as e: raise RuntimeError(f"Unexpected DNG error for {filename}: {e}")

                else: # Untuk format non-RAW (JPG, PNG, TIFF, dll.)
                    img_cv = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                    if img_cv is None: raise RuntimeError(f"OpenCV failed to read image: {filename}")

                    # Normalisasi tipe data ke uint8
                    if img_cv.dtype == np.uint16:
                        img_array = (img_cv / 256).astype(np.uint8)
                    elif img_cv.dtype == np.uint8:
                        img_array = img_cv
                    else:
                        img_array = img_cv.astype(np.uint8)

                    # Konversi warna awal jika gambar berwarna (3 channel)
                    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                         img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

                if img_array is None:
                    raise RuntimeError(f"Image array could not be created for {filename}")

                # =================================================================
                # TAHAP 2: JALUR CEPAT UNTUK MODE RESOLUSI RENDAH (PRE-LOADING)
                # =================================================================
                if self.low_res_mode:
                    # Pastikan format warna konsisten (RGB) sebelum resize
                    if len(img_array.shape) == 2: # Grayscale
                        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
                    elif len(img_array.shape) == 3 and img_array.shape[2] == 4: # BGRA/RGBA
                        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGRA2RGB)

                    # Hitung dimensi baru dengan menjaga aspek rasio
                    h, w = img_array.shape[:2]
                    if max(h, w) <= self.target_size:
                        resized_img = img_array # Tidak perlu resize jika sudah kecil
                    else:
                        scale = self.target_size / max(h, w)
                        new_w, new_h = int(w * scale), int(h * scale)
                        resized_img = cv2.resize(img_array, (new_w, new_h), interpolation=cv2.INTER_AREA)

                    # Konversi array numpy hasil resize ke QImage
                    height, width, channel = resized_img.shape
                    bytes_per_line = channel * width
                    qimg_low = QImage(resized_img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).copy()
                    
                    # Kembalikan TUPLE untuk menandakan hasil pra-pemuatan
                    return (image_path, qimg_low)

                # =================================================================
                # TAHAP 3: PEMROSESAN RESOLUSI PENUH (PERILAKU ASLI)
                # =================================================================
                
                final_img = None
                # Tentukan apakah perlu pemrosesan paralel (untuk gambar Grayscale atau Alpha)
                processed_via_parts = len(img_array.shape) == 2 or img_array.shape[2] == 4

                if processed_via_parts:
                    h, w = img_array.shape[:2]
                    mid_h, mid_w = h // 2, w // 2
                    parts = [
                        img_array[0:mid_h, 0:mid_w], img_array[0:mid_h, mid_w:w],
                        img_array[mid_h:h, 0:mid_w], img_array[mid_h:h, mid_w:w]
                    ]
                    
                    with ThreadPoolExecutor(max_workers=self.num_part_workers) as executor:
                        futures = [executor.submit(_process_image_part, p) for p in parts]
                        processed_parts = [future.result() for future in as_completed(futures)]

                    # Gabungkan kembali bagian-bagian yang telah diproses
                    top_row = np.hstack((processed_parts[0], processed_parts[1]))
                    bottom_row = np.hstack((processed_parts[2], processed_parts[3]))
                    final_img = np.vstack((top_row, bottom_row))
                else:
                    # Jika gambar sudah RGB, tidak perlu pemrosesan paralel
                    final_img = img_array

                # =================================================================
                # TAHAP 4: KONVERSI FINAL KE QPIXMAP (UNTUK RESOLUSI PENUH)
                # =================================================================
                if final_img is not None:
                    if final_img.dtype != np.uint8:
                        final_img = final_img.astype(np.uint8)

                    height, width, channel = final_img.shape
                    bytes_per_line = channel * width
                    qimg = QImage(final_img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).copy()
                    
                    if qimg.isNull(): raise RuntimeError(f"Failed to copy QImage for {filename}")
                    
                    pixmap = QPixmap.fromImage(qimg)
                    if pixmap.isNull(): raise RuntimeError(f"Failed to create QPixmap for {filename}")
                    
                    # Kembalikan QPixmap untuk menandakan hasil resolusi penuh
                    return pixmap
                else:
                    raise RuntimeError(f"Final image is None after processing {filename}")

            except Exception as e:
                print(f"ERROR processing {image_path}: {e}")
                # Melempar kembali error agar dapat ditangkap oleh error_signal dari BaseMultiThreading
                raise e

        super().__init__(process_image, image_paths, batch_size, delay_ms)
        
class ImageImportThreading(BaseMultiThreading):
    """
    Specific multithreading implementation for importing images.
    """
    def __init__(self, database_manager, image_paths, batch_size, delay_ms):
        def import_task(image_path):
            database_manager.single_process_save_image_path(image_path)
        
        super().__init__(import_task, image_paths, batch_size, delay_ms)
        
class BatchImageImportThreading(BaseMultiThreading):
    """
    Specific multithreading implementation for importing images into a SPECIFIC batch.
    """
    def __init__(self, database_manager, image_paths, batch_id, batch_size, delay_ms):
        # Terima batch_id yang sudah ada
        self.batch_id = batch_id
        self.database_manager = database_manager # Simpan referensi

        # Definisikan tugas untuk setiap gambar
        def import_task(image_path):
            # Panggil fungsi save dengan batch_id yang sudah ditentukan
            # Fungsi ini sekarang menangani satu path dalam list
            self.database_manager.batch_process_save_image_path(self.batch_id, [image_path])

        super().__init__(import_task, image_paths, batch_size, delay_ms)

        
class ImageProcessingMultiThreading(QThread):
    progress_updated = Signal(int, str)
    finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, worker_function, db_path, single_process=True, batch_id=None, parent=None):
        super().__init__(parent)
        self.worker_function = worker_function
        self.db_path = db_path
        self.single_process = single_process
        self.batch_id = batch_id
        self.stop_requested = False

    def run(self):
        try:
            def update_progress(current, total, message):
                progress = int((current / total) * 100)
                self.progress_updated.emit(progress, message)

            def is_stop_requested():
                return self.stop_requested

            # Jalankan fungsi pekerja yang diberikan
            self.worker_function(
                self.db_path, 
                update_progress=update_progress, 
                stop_requested=is_stop_requested, 
                single_process=self.single_process, 
                batch_id=self.batch_id
            )
            self.finished.emit()
        except Exception as e:
            print(f"Error terjadi: {str(e)}")
            self.error_occurred.emit(str(e))

    def stop(self):
        self.stop_requested = True