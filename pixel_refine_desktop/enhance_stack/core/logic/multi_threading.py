from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import time
import concurrent
import threading
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap, QImage
import rawpy

from config import SUPPORTED_FORMATS

taichi_lock = threading.Lock()


class BaseMultiThreading(QThread):
    """
    Base class for multithreading tasks. This class supports batch processing.
    """

    progress_signal = Signal(
        int, int
    )  # Mengirim progres (dalam persen) dan jumlah item tersisa
    completion_signal = Signal(int)  # Mengirim jumlah total item setelah selesai
    result_signal = Signal(object)  # Mengirim hasil dari setiap tugas
    error_signal = Signal(str)  # Mengirim pesan error jika ada

    def __init__(self, task_function, items, batch_size=3, delay_ms=50):
        super().__init__()
        self.task_function = task_function  # Fungsi tugas yang akan dijalankan
        self.items = items  # Daftar item yang akan diproses
        self.batch_size = batch_size  # Ukuran batch
        self.delay_ms = delay_ms  # Waktu jeda antar batch
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

        processed_part = img_part  # Default jika sudah RGB

        # Konversi warna jika perlu
        if len(img_part.shape) == 2:  # Grayscale
            processed_part = cv2.cvtColor(img_part, cv2.COLOR_GRAY2RGB)
        elif img_part.shape[2] == 4:  # RGBA
            processed_part = cv2.cvtColor(img_part, cv2.COLOR_RGBA2RGB)

        # Pastikan output adalah RGB uint8
        if (
            len(processed_part.shape) != 3
            or processed_part.shape[2] != 3
            or processed_part.dtype != np.uint8
        ):
            pass

        return processed_part

    except Exception as e:
        raise RuntimeError(f"Failed to process quadrant: {e}")


def load_raw_as_8bit_rgb(image_path: str) -> np.ndarray:
    """Loads a RAW/DNG image and returns it as an 8-bit RGB numpy array using Hamilton Demosaic with rawpy fallback."""
    filename = os.path.basename(image_path)
    try:
        from taichi_vision import taichi_aot

        with taichi_lock:
            rgb_f32 = taichi_aot.demosaic(image_path, method="hamilton")
        if rgb_f32 is not None:
            rgb_f32 = taichi_aot.naturalTonemapping(rgb_f32)
            return np.clip(rgb_f32 * 255.0, 0, 255).astype(np.uint8)
        else:
            raise RuntimeError("Hamilton demosaic returned None")
    except Exception as e_ta:
        print(
            f"[Fallback] Taichi Hamilton demosaic failed ({e_ta}), falling back to rawpy."
        )
        try:
            with rawpy.imread(image_path) as raw:
                gamma_setting = (2.222, 4.5)
                img_array = raw.postprocess(
                    demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,  # type: ignore
                    four_color_rgb=True,
                    use_camera_wb=True,
                    gamma=gamma_setting,
                    output_bps=8,
                    output_color=rawpy.ColorSpace.sRGB,  # type: ignore
                    highlight_mode=rawpy.HighlightMode.Blend,  # type: ignore
                )
                if img_array is None:
                    raise RuntimeError(f"Rawpy postprocessing failed for {filename}")
                return img_array
        except rawpy.LibRawError as e:
            raise RuntimeError(f"Rawpy Error for {filename}: {e}")  # type: ignore
    except Exception as e:
        raise RuntimeError(f"Unexpected DNG error for {filename}: {e}")


def load_raw_as_8bit_rgb_half_res(image_path: str) -> np.ndarray:
    """Loads a RAW/DNG image and returns it as an 8-bit half-resolution RGB numpy array using Hamilton Demosaic with rawpy fallback."""
    filename = os.path.basename(image_path)
    try:
        from taichi_vision import taichi_aot

        with taichi_lock:
            rgb_f32 = taichi_aot.demosaic(image_path, method="bilinear", half_res=True)
        if rgb_f32 is not None:
            rgb_f32 = taichi_aot.naturalTonemapping(rgb_f32)
            return np.clip(rgb_f32 * 255.0, 0, 255).astype(np.uint8)
        else:
            raise RuntimeError("Hamilton demosaic half res returned None")
    except Exception as e_ta:
        print(
            f"[Fallback] Taichi Hamilton half res demosaic failed ({e_ta}), falling back to rawpy half-res."
        )
        try:
            from taichi_vision import taichi_aot

            taichi_aot.engine.buffer_pool.clear()
        except Exception:
            pass
        try:
            with rawpy.imread(image_path) as raw:
                gamma_setting = (2.222, 4.5)
                img_array = raw.postprocess(
                    demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,  # type: ignore
                    half_size=True,  # Extracted at half size for speed!
                    use_camera_wb=True,
                    gamma=gamma_setting,
                    output_bps=8,
                    output_color=rawpy.ColorSpace.sRGB,  # type: ignore
                    highlight_mode=rawpy.HighlightMode.Blend,  # type: ignore
                )
                if img_array is None:
                    raise RuntimeError(f"Rawpy postprocessing failed for {filename}")
                return img_array
        except rawpy.LibRawError as e:
            raise RuntimeError(f"Rawpy Error for {filename}: {e}")  # type: ignore
        except Exception as e:
            raise RuntimeError(f"Unexpected DNG error for {filename}: {e}")


class RawImageProcessingThread(BaseMultiThreading):
    """
    Thread untuk memproses gambar dari path file menjadi QPixmap atau QImage.
    """

    def __init__(
        self, image_paths, batch_size=1, delay_ms=100, low_res_target_size=None
    ):
        self.low_res_mode = low_res_target_size is not None
        self.target_size = low_res_target_size

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

                is_raw = any(
                    extension in formats
                    for key, formats in SUPPORTED_FORMATS.items()
                    if key == "raw"
                )
                if is_raw:
                    img_array = load_raw_as_8bit_rgb(image_path)
                else:  # Untuk format non-RAW (JPG, PNG, TIFF, dll.)
                    img_cv = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                    if img_cv is None:
                        raise RuntimeError(f"OpenCV failed to read image: {filename}")

                    if img_cv.dtype == np.uint16:
                        img_array = (img_cv / 256).astype(np.uint8)
                    elif img_cv.dtype == np.uint8:
                        img_array = img_cv
                    else:
                        img_array = img_cv.astype(np.uint8)

                    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

                if img_array is None:
                    raise RuntimeError(
                        f"Image array could not be created for {filename}"
                    )

                if self.low_res_mode:
                    if len(img_array.shape) == 2:
                        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
                    elif len(img_array.shape) == 3 and img_array.shape[2] == 4:
                        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGRA2RGB)

                    h, w = img_array.shape[:2]
                    if self.target_size is not None and max(h, w) <= self.target_size:
                        resized_img = img_array
                    elif self.target_size is not None:
                        scale = self.target_size / max(h, w)
                        new_w, new_h = int(w * scale), int(h * scale)
                        resized_img = cv2.resize(
                            img_array, (new_w, new_h), interpolation=cv2.INTER_AREA
                        )
                    else:
                        resized_img = img_array

                    height, width, channel = resized_img.shape
                    bytes_per_line = channel * width
                    qimg_low = QImage(
                        resized_img.data,
                        width,
                        height,
                        bytes_per_line,
                        QImage.Format.Format_RGB888,
                    ).copy()

                    return (image_path, qimg_low)

                final_img = None
                processed_via_parts = (
                    len(img_array.shape) == 2 or img_array.shape[2] == 4
                )

                if processed_via_parts:
                    h, w = img_array.shape[:2]
                    mid_h, mid_w = h // 2, w // 2
                    parts = [
                        img_array[0:mid_h, 0:mid_w],
                        img_array[0:mid_h, mid_w:w],
                        img_array[mid_h:h, 0:mid_w],
                        img_array[mid_h:h, mid_w:w],
                    ]

                    with ThreadPoolExecutor(
                        max_workers=self.num_part_workers
                    ) as executor:
                        futures = [
                            executor.submit(_process_image_part, p) for p in parts
                        ]
                        processed_parts = [
                            future.result() for future in as_completed(futures)
                        ]

                    top_row = np.hstack((processed_parts[0], processed_parts[1]))
                    bottom_row = np.hstack((processed_parts[2], processed_parts[3]))
                    final_img = np.vstack((top_row, bottom_row))
                else:
                    final_img = img_array

                if final_img is not None:
                    if final_img.dtype != np.uint8:
                        final_img = final_img.astype(np.uint8)

                    height, width, channel = final_img.shape
                    bytes_per_line = channel * width
                    qimg = QImage(
                        final_img.data,
                        width,
                        height,
                        bytes_per_line,
                        QImage.Format.Format_RGB888,
                    ).copy()

                    if qimg.isNull():
                        raise RuntimeError(f"Failed to copy QImage for {filename}")

                    pixmap = QPixmap.fromImage(qimg)
                    if pixmap.isNull():
                        raise RuntimeError(f"Failed to create QPixmap for {filename}")

                    return pixmap
                else:
                    raise RuntimeError(
                        f"Final image is None after processing {filename}"
                    )

            except Exception as e:
                print(f"ERROR processing {image_path}: {e}")
                raise e

        super().__init__(process_image, image_paths, batch_size, delay_ms)


class ImageImportThreading(BaseMultiThreading):
    image_added_signal = Signal(int, str)

    def __init__(self, database_manager, image_paths, batch_size, delay_ms, batch_id=0):
        self.batch_id = batch_id

        def import_task(image_path):
            database_manager.single_process_save_image_path(image_path)
            self.image_added_signal.emit(self.batch_id, image_path)

        super().__init__(import_task, image_paths, batch_size, delay_ms)


class BatchImageImportThreading(BaseMultiThreading):
    # One stable signal contract for all batch import callers.
    image_added_signal = Signal(int, str)
    batch_imported_signal = Signal(int, list)

    def __init__(
        self,
        database_manager,
        image_paths=None,
        batch_dict=None,
        batch_id=0,
        batch_name="",
        batch_size=5,
        delay_ms=50,
        **kwargs,
    ):
        self.database_manager = database_manager
        self.batch_id = batch_id
        self.batch_name = batch_name

        if batch_dict is not None:
            items = list(batch_dict.items())

            def process_task(item):
                item_batch_id, paths = item
                saved_paths = []
                for path in paths:
                    saved = self.database_manager.batch_process_save_image_path(
                        item_batch_id, [path]
                    )
                    if saved:
                        saved_paths.append(path)
                        self.image_added_signal.emit(item_batch_id, path)
                self.batch_imported_signal.emit(item_batch_id, saved_paths)
                return (item_batch_id, saved_paths)

        else:
            items = image_paths if image_paths is not None else []

            def process_task(image_path):
                saved = self.database_manager.batch_process_save_image_path(
                    self.batch_id, [image_path]
                )
                if saved:
                    self.image_added_signal.emit(self.batch_id, image_path)
                return (self.batch_id, image_path, bool(saved))

        super().__init__(process_task, items, batch_size, delay_ms)
