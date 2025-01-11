import os
import subprocess
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

class RunningAlgorithmThreading(BaseMultiThreading):
    def __init__(self, algorithm_tasks, virtualenv_path, base_path, batch_size=1, delay_ms=100):
        self.virtualenv_path = virtualenv_path
        self.base_path = base_path

        def run_algorithm(task):
            virtualenv_path, script_path, algorithm_name = task  # Pastikan unpacking sesuai dengan format tuple
            try:
                print(f"Running {algorithm_name}...")
                subprocess.run([self.virtualenv_path, script_path], check=True)
                return f"{algorithm_name} completed successfully."
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error running {algorithm_name}: {e}")
            except FileNotFoundError as e:
                raise RuntimeError(f"File not found for {algorithm_name}: {e}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error for {algorithm_name}: {e}")

        # Perbaiki list comprehension di sini untuk menangani tuple tiga elemen
        tasks = [(virtualenv_path, os.path.join(base_path, p), n) for p, n in algorithm_tasks]
        super().__init__(run_algorithm, tasks, batch_size, delay_ms)
