from concurrent.futures import ThreadPoolExecutor
import os
import time
import concurrent
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
import rawpy

from config import SUPPORTED_FORMATS


class BaseMultiThreading(QThread):
    """
    Base class for multithreading tasks. This class supports batch processing.
    """
    progress_signal = pyqtSignal(int, int)  # Mengirim progres (dalam persen) dan jumlah item tersisa
    completion_signal = pyqtSignal(int)    # Mengirim jumlah total item setelah selesai
    result_signal = pyqtSignal(object)     # Mengirim hasil dari setiap tugas
    error_signal = pyqtSignal(str)         # Mengirim pesan error jika ada

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
    def __init__(self, image_paths, batch_size=1, delay_ms=100):

        try:
             total_cores = os.cpu_count()
             self.num_part_workers = max(1, (total_cores // 2) if total_cores else 2)
        except NotImplementedError:
             self.num_part_workers = 2
        
        def process_image(image_path):
            try:
                filename = os.path.basename(image_path)
                extension = os.path.splitext(image_path)[1].lower()
                img_array = None
                processed_via_parts = False 
                
                is_raw = any(extension in formats for key, formats in SUPPORTED_FORMATS.items() if key == "raw")
                if is_raw:
                    try:
                        with rawpy.imread(image_path) as raw:
                            img_array = raw.postprocess(output_bps=8, use_camera_wb=True, no_auto_bright=False, gamma=(2.222, 4.5), 
                                                        highlight_mode=rawpy.HighlightMode.Blend)
                            if img_array is None: raise RuntimeError(f"Rawpy postprocessing failed for {filename}")
                          
                    except rawpy.LibRawError as e: raise RuntimeError(f"Rawpy Error processing {filename}: {e}")
                    except FileNotFoundError: raise RuntimeError(f"DNG file not found: {image_path}")
                    except Exception as e: raise RuntimeError(f"Unexpected DNG processing error {filename}: {e}")

                elif any(extension in formats for key, formats in SUPPORTED_FORMATS.items() if key != "dng"):
                    img_cv = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                    if img_cv is None: raise RuntimeError(f"OpenCV failed to read image: {filename}")

                    # Pra-proses tipe data SEBELUM memecah
                    if img_cv.dtype == np.uint16:
                        img_array = (img_cv / 256).astype(np.uint8)
                    elif img_cv.dtype == np.uint8:
                        img_array = img_cv # Sudah tipe yang benar
                    else:
                        raise RuntimeError(f"Unexpected OpenCV dtype ({img_cv.dtype}) for {filename}")

                    # Konversi BGR awal ke RGB jika perlu (dilakukan sebelum pemecahan jika memungkinkan)
                    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                         img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                        
                    # Jika inputnya Grayscale atau RGBA, pemecahan akan dilakukan
                    # karena konversi warna perlu dilakukan per bagian.
                    if len(img_array.shape) == 2 or img_array.shape[2] == 4:
                         processed_via_parts = True # Tandai untuk pemrosesan paralel
                         print(f"  Image {filename} needs per-part color conversion (Grayscale/RGBA). Will attempt parallel processing.")
                    # Jika sudah RGB 8-bit pada tahap ini, tidak ada gunanya memecah lebih lanjut.
                    elif len(img_array.shape) == 3 and img_array.shape[2] == 3:
                         print(f"  Image {filename} is already RGB uint8. Skipping experimental part splitting.")
                    else:
                         raise RuntimeError(f"Unhandled image shape after initial processing: {img_array.shape}")

                else:
                    raise RuntimeError(f"Unsupported image format: {filename} (ext: {extension})")


                # 2. Pemrosesan Paralel Bagian (JIKA diperlukan dan ditandai)
                # ============================================================
                final_img = None
                if processed_via_parts and img_array is not None:
                    print(f"  Starting parallel part processing for {filename}...")
                    h, w = img_array.shape[:2]
                    # Hindari pemecahan jika gambar terlalu kecil
                    if h < 10 or w < 10:
                         print(f"  Image {filename} too small, processing whole.")
                         # Proses keseluruhan jika terlalu kecil
                         final_img = _process_image_part(img_array)
                    else:
                        # Tentukan titik potong (4 kuadran)
                        mid_h = h // 2
                        mid_w = w // 2
                        parts = [
                            img_array[0:mid_h, 0:mid_w],      # Top-Left
                            img_array[0:mid_h, mid_w:w],      # Top-Right
                            img_array[mid_h:h, 0:mid_w],      # Bottom-Left
                            img_array[mid_h:h, mid_w:w]       # Bottom-Right
                        ]
                        part_indices = [(0, 0), (0, 1), (1, 0), (1, 1)] # Untuk menempatkan kembali

                        processed_parts = {} # Simpan hasil berdasarkan indeks

                        with ThreadPoolExecutor(max_workers=self.num_part_workers) as executor:
                            # Buat future untuk setiap bagian
                            future_to_index = {executor.submit(_process_image_part, parts[i]): part_indices[i] for i in range(4)}

                            for future in concurrent.futures.as_completed(future_to_index):
                                index = future_to_index[future]
                                try:
                                    processed_parts[index] = future.result()
                                except Exception as exc:
                                    print(f"  Quadrant {index} generated an exception: {exc}")
                                    # Handle error: bisa raise error utama, atau coba lanjutkan tanpa bagian ini
                                    raise RuntimeError(f"Error in parallel processing for {filename}, quadrant {index}: {exc}")

                        # Periksa apakah semua bagian berhasil diproses
                        if len(processed_parts) == 4:
                            # Tentukan shape output (harus RGB)
                            out_h = h
                            out_w = w
                            out_channels = 3 # Target selalu RGB
                            out_dtype = np.uint8

                            # Buat array kosong untuk menampung hasil gabungan
                            stitched_img = np.zeros((out_h, out_w, out_channels), dtype=out_dtype)

                            # Gabungkan kembali bagian-bagian yang sudah diproses
                            # Pastikan dimensi sesuai
                            p_tl = processed_parts[(0, 0)]
                            p_tr = processed_parts[(0, 1)]
                            p_bl = processed_parts[(1, 0)]
                            p_br = processed_parts[(1, 1)]

                            stitched_img[0:mid_h, 0:mid_w] = p_tl
                            stitched_img[0:mid_h, mid_w:w] = p_tr
                            stitched_img[mid_h:h, 0:mid_w] = p_bl
                            stitched_img[mid_h:h, mid_w:w] = p_br

                            final_img = stitched_img
                            print(f"  Parallel part processing finished and stitched for {filename}.")
                        else:
                             raise RuntimeError(f"Parallel processing failed for {filename}: not all parts completed successfully.")

                elif img_array is not None:
                     # Jika tidak diproses via parts, img_array adalah hasil akhir
                     final_img = img_array
                else:
                     # Jika img_array None (error saat baca)
                     raise RuntimeError(f"Image array is None before final conversion for {filename}")


                # 3. Konversi ke QPixmap (dari final_img)
                # =========================================
                if final_img is not None:
                    # Validasi akhir sebelum konversi QPixmap
                    if len(final_img.shape) != 3 or final_img.shape[2] != 3 or final_img.dtype != np.uint8:
                         raise RuntimeError(f"Final image data not RGB uint8 for {filename}: shape={final_img.shape}, dtype={final_img.dtype}")

                    height, width, channel = final_img.shape
                    bytes_per_line = channel * width
                    qimg = QImage(final_img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

                    qimg_copy = qimg.copy() # Penting!
                    if qimg_copy.isNull(): raise RuntimeError(f"Failed to copy QImage for {filename}")

                    pixmap = QPixmap.fromImage(qimg_copy)
                    if pixmap.isNull(): raise RuntimeError(f"Failed to create QPixmap for {filename}")

                    return pixmap
                else:
                    raise RuntimeError(f"Final image is None after processing {filename}")

            except RuntimeError as e:
                print(f"ERROR processing {image_path}: {e}")
                raise e
            except Exception as e:
                import traceback
                print(f"!!! CRITICAL UNEXPECTED ERROR processing {image_path}: {e}")
                traceback.print_exc()
                raise RuntimeError(f"Critical error processing {image_path}")

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
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

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