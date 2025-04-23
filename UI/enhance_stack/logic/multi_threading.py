import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage


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
                    # Kirim pesan error jika ada kesalahan
                    self.error_signal.emit(str(e))

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


class RawImageProcessingThread(BaseMultiThreading):
    """
    A special multithreading class for processing images of various formats.
    """
    def __init__(self, image_paths, batch_size=1, delay_ms=100):
        def process_image(image_path):
            # Deteksi format berdasarkan ekstensi file
            extension = image_path.split('.')[-1].lower()

            if extension in {"nef", "cr2", "dng", "arw"}:  # Format RAW (Gunakan OpenCV atau library lain jika perlu)
                raise RuntimeError(f"RAW format not supported: {image_path}")
            
            elif extension in {"jpg", "jpeg", "png", "tiff", "tif"}:  # Format non-RAW
                img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

                # Konversi jika gambar 16-bit ke 8-bit
                if img.dtype == np.uint16:
                    img = (img / 256).astype(np.uint8)

                # Jika format gambar adalah grayscale, ubah ke RGB
                if len(img.shape) == 2:  # Gambar grayscale
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                elif img.shape[2] == 4:  # Gambar dengan Alpha (RGBA)
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
                elif img.shape[2] == 3:  # Sudah RGB tetapi dalam format OpenCV (BGR)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Konversi NumPy array ke format QPixmap
                height, width, channel = img.shape
                bytes_per_line = channel * width
                qimg = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)

                if pixmap.isNull():
                    raise RuntimeError(f"Failed to load image '{image_path}'. Conversion failed.")

                return pixmap  # Hasil yang diproses akan dikirim melalui sinyal `result_signal`

            else:
                raise RuntimeError(f"Unsupported image format: {image_path}")

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