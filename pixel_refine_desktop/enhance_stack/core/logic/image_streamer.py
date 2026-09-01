import threading
import queue
import numpy as np
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    load_images_from_paths,
)


class ImageStreamer:
    """
    Kelas generik untuk Producer-Consumer Image Streaming.
    Membaca gambar dari HDF5 atau list path disk satu per satu
    di latar belakang (background thread),
    sehingga UI thread / Main thread hanya perlu mengiterasi `.stream()`.
    Penyelamat RAM untuk mencegah OOM (Out Of Memory).
    """

    def __init__(self, data_source, stop_requested=None, max_queue_size=3):
        self.data_source = data_source
        self.stop_requested = stop_requested
        self.max_queue_size = max_queue_size
        self.job_queue = queue.Queue(maxsize=self.max_queue_size)

        self.is_hdf5 = False
        self.keys = []
        self.total_images = 0

        # --- TAHAP 1: Hitung total foto ---
        if isinstance(self.data_source, list):
            self.total_images = len(self.data_source)

    def __len__(self):
        return self.total_images

    def __bool__(self):
        return self.total_images > 0

    def __getitem__(self, idx):
        if self.data_source:
            item = self.data_source[idx]
            if isinstance(item, np.ndarray):
                return item
            elif isinstance(item, str):
                loaded = load_images_from_paths([item], self.stop_requested)
                return loaded[0] if loaded else None
        raise IndexError("ImageStreamer index out of range")

    def _image_loader_worker(self):
        try:
            if self.data_source:
                for i, item in enumerate(self.data_source):
                    if self.stop_requested and self.stop_requested():
                        break

                    if isinstance(item, np.ndarray):
                        self.job_queue.put((i, item))
                    elif isinstance(item, str):
                        # Gunakan load tunggal untuk menghemat RAM
                        loaded = load_images_from_paths([item], self.stop_requested)
                        if loaded and loaded[0] is not None:
                            self.job_queue.put((i, loaded[0]))
                        else:
                            self.job_queue.put((i, None))
                    else:
                        self.job_queue.put((i, None))
        except Exception as e:
            print(f"Error in ImageStreamer worker: {e}")
        finally:
            self.job_queue.put(None)  # Sentinel value EOF

    def stream(self):
        """
        Generator yang dapat diiterasi oleh Main Thread secara kontinyu.
        Yields: (index: int, image_array: np.ndarray)
        """
        if self.total_images == 0:
            return

        loader_thread = threading.Thread(target=self._image_loader_worker, daemon=True)
        loader_thread.start()

        try:
            while True:
                if self.stop_requested and self.stop_requested():
                    break

                item = self.job_queue.get()
                if item is None:  # EOF
                    break

                idx, img = item
                yield idx, img
        finally:
            # Pastikan thread tergabung dan clean up
            if loader_thread.is_alive():
                # Kuras queue jika stop_requested, supaya thread bisa finish (karena queue mungkin penuh dan mem-block thread)
                while True:
                    try:
                        self.job_queue.get_nowait()
                    except queue.Empty:
                        break
            loader_thread.join(timeout=1.0)
