from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
import rawpy, io, numpy 
from PIL import Image

class BaseMultiThreading(QThread):
    """
    Base class for multithreading tasks. This class supports batch processing.
    """
    progress_signal = pyqtSignal(int, int)  # Mengirimkan progres (dalam persen) dan jumlah item tersisa
    completion_signal = pyqtSignal(int)    # Mengirimkan jumlah total item setelah selesai
    result_signal = pyqtSignal(object)     # Mengirimkan hasil dari setiap tugas
    error_signal = pyqtSignal(str)         # Mengirimkan pesan error jika ada

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

            if extension in {"nef", "cr2", "dng", "arw"}:  # Format RAW
                with rawpy.imread(image_path) as raw:
                    rgb = raw.postprocess()
            elif extension in {"jpg", "jpeg", "png", "tiff", "tif"}:  # Format non-RAW
                img = Image.open(image_path)

                # Konversi jika gambar 16-bit
                if img.mode == "I;16":
                    img = img.point(lambda x: x >> 8)  # Turunkan ke 8-bit untuk tampilan

                img = img.convert("RGB")  # Konversi ke RGB
                rgb = numpy.array(img)  # Konversi ke array untuk keseragaman
            else:
                raise RuntimeError(f"Unsupported image format: {image_path}")

            # Konversi RGB array ke QPixmap
            processed_img = Image.fromarray(rgb)
            data = io.BytesIO()
            processed_img.save(data, format="PNG")
            data.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(data.read(), "PNG")

            if pixmap.isNull():
                raise RuntimeError(f"Failed to load image '{image_path}'. Conversion failed.")

            return pixmap  # Hasil yang diproses akan dikirim melalui sinyal `result_signal`

        super().__init__(process_image, image_paths, batch_size, delay_ms)



class ImageImportThreading(BaseMultiThreading):
    """
    Specific multithreading implementation for importing images.
    """
    def __init__(self, database_manager, image_paths, batch_size, delay_ms):
        def import_task(image_path):
            database_manager.save_image_path(image_path)
        
        super().__init__(import_task, image_paths, batch_size, delay_ms)
        
class ImageSaveThreading(BaseMultiThreading):
    """
    Multithreading implementation for saving image data into the database.
    """
    def __init__(self, database_manager, image_data_list, batch_size=3, delay_ms=50):
        """
        Args:
            database_manager: Instance of the database manager with `save_image_data` method.
            image_data_list: List of tuples containing (image_id, image_file).
            batch_size: Number of images processed per batch.
            delay_ms: Delay between processing batches in milliseconds.
        """
        def save_task(image_data):
            image_id, image_file = image_data
            database_manager.save_image_data(image_id, image_file)
        
        super().__init__(save_task, image_data_list, batch_size, delay_ms)


class ImageAlignmentThreading(BaseMultiThreading):
    """
    Threading implementation for aligning image pairs using ECC algorithm.
    """
    def __init__(self, database_manager, image_pairs, batch_size=1, delay_ms=100):
        def align_task(image_pair):
            image_id, path1, path2 = image_pair
            aligned_data = database_manager.eccAlign(path1, path2)
            if aligned_data:
                database_manager.save_image_data(image_id, aligned_data)
                return (image_id, "Success")
            else:
                raise RuntimeError(f"Alignment failed for image pair: {path1}, {path2}")
        
        super().__init__(align_task, image_pairs, batch_size, delay_ms)

