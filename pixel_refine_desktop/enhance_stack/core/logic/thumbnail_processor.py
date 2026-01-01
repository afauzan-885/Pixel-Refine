"""
Thumbnail Processor Utility
============================
Utility untuk memproses dan menampilkan thumbnail gambar dengan cara yang konsisten.
Diekstrak dari batch_page/thumbnail.py untuk digunakan kembali di berbagai modul.

Fitur:
- Memproses thumbnail secara asinkron menggunakan QThread
- Support untuk berbagai format gambar (JPEG, PNG, TIFF, RAW)
- Koreksi orientasi otomatis menggunakan EXIF
- Cache thumbnail untuk performa
- Thread-safe dengan semaphore untuk membatasi thread aktif
"""

import os
from PySide6.QtWidgets import QLabel, QStackedWidget
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    QMutex,
    QWaitCondition,
    QFile,
    QSemaphore,
    QTimer,
    QObject,
    QRunnable,
    QThreadPool,
    QCoreApplication,
)
import cv2
import numpy as np
import rawpy
from PIL import Image, ImageOps
import weakref

from config import CACHE_DIR, SUPPORTED_FORMATS
from pixel_refine_desktop.ui.resources.animations.fade import fade_in
from pixel_refine_desktop.enhance_stack.core.logic.display_manager import (
    DisplayThreadManager,
)

from pixel_refine_desktop.enhance_stack.models.data_access.thumbnail_repository import (
    ThumbnailRepository,
)

# Max worker threads (standard 4 for balanced I/O and CPU)
MAX_THUMBNAIL_WORKERS = 4

# Thumbnail repository initialization

# Lazy initialization untuk repository
_thumbnail_repo = None


def get_thumbnail_repo():
    global _thumbnail_repo
    if _thumbnail_repo is None:
        _thumbnail_repo = ThumbnailRepository()
    return _thumbnail_repo


class ThumbnailWorkerSignals(QObject):
    """Signals for the ThumbnailWorker because QRunnable is not a QObject."""

    thumbnail_ready = Signal(QImage, str)


class ThumbnailWorker(QRunnable):
    """
    Worker QRunnable untuk memproses thumbnail gambar guna menghindari handle leak (Window Manager objects).
    Menggunakan QThreadPool untuk eksekusi massal yang efisien.
    """

    def __init__(self, image_path, processor, batch_id, thumbnail_size=(128, 128)):
        """
        Initialize thumbnail worker.
        """
        super().__init__()
        self.image_path = image_path
        self.thumbnail_size = thumbnail_size
        self.processor_ref = weakref.ref(processor)
        self.target_batch_id = str(batch_id)
        self.signals = ThumbnailWorkerSignals()
        self._is_aborted = False

    def _should_abort(self):
        """Check if this worker should stop immediately."""
        if self._is_aborted:
            return True

        # Cek apakah aplikasi sedang menutup (paling kritikal untuk cegah RuntimeError)
        app = QCoreApplication.instance()
        if app is None or app.closingDown():
            return True

        processor = self.processor_ref()
        if processor is None or str(processor.current_batch_id) != self.target_batch_id:
            return True

        return False

    def abort(self):
        """Request worker to stop."""
        self._is_aborted = True

    def run(self):
        """Main execution logic."""
        if self._should_abort():
            return

        result_image = QImage()

        try:
            # 1. Check SQLite Cache First
            repo = get_thumbnail_repo()
            cached_image = repo.get_thumbnail(self.image_path)
            if not cached_image.isNull():
                if not self._should_abort():
                    result_image = cached_image
                    try:
                        self.signals.thumbnail_ready.emit(result_image, self.image_path)
                    except (RuntimeError, AttributeError):
                        pass
                return

            if self._should_abort():
                return

            # 2. Process image (Decoding)
            pil_thumb = process_thumbnail_logic(self.image_path, self.thumbnail_size)

            if self._should_abort():
                return

            # 3. Convert to QImage
            if pil_thumb:
                result_image = convert_pil_to_qimage(pil_thumb)

        except Exception as e:
            if not self._should_abort():
                print(f"[ThumbnailWorker] Error processing {self.image_path}: {e}")
        finally:
            if not self._should_abort():
                try:
                    self.signals.thumbnail_ready.emit(result_image, self.image_path)
                except (RuntimeError, AttributeError):
                    pass

    def _convert_to_qimage(self, pil_img):
        """Helper to convert PIL Image to QImage safely."""
        if pil_img is None:
            return QImage()
        return convert_pil_to_qimage(pil_img)

    def _process_image(self):
        """Image processing logic for single worker."""
        return process_thumbnail_logic(self.image_path, self.thumbnail_size)


class ThumbnailBulkWorker(QRunnable):
    """
    Worker QRunnable untuk memproses SEKELOMPOK (Chunk) thumbnail gambar.
    Mengurangi overhead pembuatan objek worker dan emisi sinyal massal.
    """

    def __init__(self, image_paths, processor, batch_id, thumbnail_size=(128, 128)):
        super().__init__()
        self.image_paths = image_paths
        self.thumbnail_size = thumbnail_size
        self.processor_ref = weakref.ref(processor)
        self.target_batch_id = str(batch_id)
        self.signals = ThumbnailWorkerSignals()
        self._is_aborted = False

    def _should_abort(self):
        if self._is_aborted:
            return True

        # Cek apakah aplikasi sedang menutup (paling kritikal untuk cegah RuntimeError)
        app = QCoreApplication.instance()
        if app is None or app.closingDown():
            return True

        processor = self.processor_ref()
        if processor is None or str(processor.current_batch_id) != self.target_batch_id:
            return True
        return False

    def run(self):
        for path in self.image_paths:
            if self._should_abort():
                return

            try:
                # 1. Process image (Decoding)
                # Kita tidak cek SQLite di sini karena process_batch sudah melakukan bulk check.
                pil_thumb = process_thumbnail_logic(path, self.thumbnail_size)

                if self._should_abort():
                    return

                # 2. Convert and Emit
                if pil_thumb:
                    q_img = convert_pil_to_qimage(pil_thumb)
                    if not self._should_abort():
                        # Selalu emit meskipun null agar progress terupdate
                        self._safe_emit(q_img, path)
                else:
                    print(f"[ThumbnailBulkWorker] Failed to decode image: {path}")
                    # Jika gagal, kirim sinyal null agar UI bisa berhenti loading
                    if not self._should_abort():
                        self._safe_emit(QImage(), path)

            except Exception as e:
                # Jangan print error jika penyebabnya adalah shutdown
                if not self._should_abort():
                    print(
                        f"[ThumbnailBulkWorker] Critical error processing {path}: {e}"
                    )
                    self._safe_emit(QImage(), path)

    def _safe_emit(self, q_image, path):
        """Emisi sinyal dengan perlindungan terhadap shutdown."""
        try:
            if hasattr(self, "signals") and self.signals:
                self.signals.thumbnail_ready.emit(q_image, path)
        except (RuntimeError, AttributeError):
            pass


def process_thumbnail_logic(image_path, thumbnail_size):
    """Core logic to process a single thumbnail, used by both workers."""
    try:
        # 1. Fast path for common formats using OpenCV
        if image_path.lower().endswith((".jpg", ".jpeg", ".png")):
            img = cv2.imread(image_path)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img)
                return ImageOps.fit(pil_img, thumbnail_size, Image.Resampling.LANCZOS)

        # 2. Fallback to PIL for TIFF, RAW, etc.
        ext = os.path.splitext(image_path)[1].lower()
        if ext in SUPPORTED_FORMATS.get("raw", []):
            with rawpy.imread(image_path) as raw:
                img_array = raw.postprocess(
                    output_bps=8, use_camera_wb=True, half_size=True
                )
                pil_img = Image.fromarray(img_array, "RGB")
                pil_img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                return pil_img

        with Image.open(image_path) as img:
            img_corrected = ImageOps.exif_transpose(img)
            return ImageOps.fit(img_corrected, thumbnail_size, Image.Resampling.LANCZOS)

    except Exception as e:
        print(f"[ThumbnailProcessor] Error processing {image_path}: {e}")
        return None


def convert_pil_to_qimage(pil_img):
    """Helper to convert PIL Image to QImage safely with data copy."""
    try:
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        q_img = QImage(
            pil_img.tobytes(),
            pil_img.width,
            pil_img.height,
            pil_img.width * 3,
            QImage.Format.Format_RGB888,
        )
        return q_img.copy()
    except Exception:
        return QImage()

    # Removed old _convert_to_qimage method to avoid duplication


def create_thumbnail_placeholder(thumbnail_size=(80, 80)):
    """
    Create a placeholder widget untuk menampilkan loading state.

    Args:
        thumbnail_size: Tuple (width, height) untuk ukuran placeholder

    Returns:
        QLabel widget dengan styling placeholder
    """
    placeholder = QLabel("Loading...")
    placeholder.setFixedSize(*thumbnail_size)
    placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
    placeholder.setStyleSheet(
        "background-color: lightgray; "
        "border: 1px solid gray; "
        "font-size: 10px; "
        "color: gray;"
    )
    return placeholder


def display_thumbnail_in_layout(
    layout, q_image, image_path, display_size=(80, 80), animator=None
):
    """
    Display thumbnail image dalam layout.

    Args:
        layout: QLayout yang akan menampung thumbnail
        q_image: QImage object untuk ditampilkan
        image_path: Path ke file gambar (untuk tracking)
        display_size: Tuple (width, height) untuk display
        animator: Optional animator untuk fade effect
    """
    if q_image.isNull():
        return

    # Create label dengan thumbnail
    thumb_label = QLabel()
    pixmap = QPixmap.fromImage(q_image)
    scaled_pixmap = pixmap.scaledToHeight(
        display_size[1], Qt.TransformationMode.SmoothTransformation
    )

    thumb_label.setPixmap(scaled_pixmap)
    thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    thumb_label.setScaledContents(False)
    thumb_label.setMaximumHeight(display_size[1])
    thumb_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")

    # Store image path for reference
    thumb_label.setProperty("image_path", image_path)

    # Add to layout
    try:
        if hasattr(layout, "addWidget"):
            layout.addWidget(thumb_label)
        elif hasattr(layout, "addItem"):
            layout.addItem(thumb_label)
    except Exception as e:
        print(f"Error adding thumbnail to layout: {e}")
        return

    # Apply fade animation if provided
    if animator:
        # fade_in expects (animator, target_widget, stack_widget=None)
        # We want standalone fade in for the label
        fade_in(animator, thumb_label)


def stop_thumbnail_threads(threads):
    """
    Stop semua thumbnail threads dengan aman dan sinkron.
    """
    if not threads:
        return

    for thread in threads:
        try:
            if thread is None:
                continue
            if thread.isRunning():
                try:
                    thread.thumbnail_ready.disconnect()
                except (TypeError, RuntimeError):
                    pass
                thread.requestInterruption()
        except Exception:
            pass

    for thread in threads:
        try:
            if thread and thread.isRunning():
                thread.wait(timeout=500)
        except Exception:
            pass

    threads.clear()


class ThumbnailBatchProcessor(QObject):
    """
    Utility class untuk memproses batch thumbnail images.
    Mengelola multiple thumbnail loader threads, RAM Cache, dan Deferred SQLite Save.
    """

    # Signal untuk melaporkan progress ke UI: (batch_id, persentase_decode, persentase_save)
    progress_updated = Signal(str, int, int)

    def __init__(self, thumbnail_size=(128, 128), max_concurrent=4):
        """
        Initialize batch processor.
        """
        super().__init__()
        self.thumbnail_size = thumbnail_size
        self.callbacks = {}  # image_path -> callback function

        # --- OPTIMASI HIGH-PERFORMANCE: CACHING & DEFERRED I/O ---
        self.ram_cache = {}  # L1 Cache: path -> QImage (Instan)
        self.pending_save_queue = []  # Queue untuk simpan ke Disk (Deferred)

        # --- PROGRESS TRACKING ---
        self.current_batch_id = None
        self.total_to_process = 0
        self.decoded_count = 0
        self.total_to_save = 0
        self.saved_count = 0
        self.path_to_batch = {}  # image_path -> batch_id

        # Timer untuk melakukan bulk save ke disk saat idle
        self.flush_timer = QTimer()
        self.flush_timer.setSingleShot(True)
        self.flush_timer.timeout.connect(self.flush_to_disk)

        # Config QThreadPool (Defaults to 4 for balance)
        QThreadPool.globalInstance().setMaxThreadCount(max_concurrent)

    def add_to_stats(self, count):
        """Tambah jumlah total gambar yang diproses secara dinamis (incremental)."""
        self.total_to_process += count
        self.total_to_save += count
        self._emit_progress()

    def process_image(self, image_path, callback=None):
        """
        Process single image thumbnail dengan sistem cache 2 level (RAM -> Disk).
        """
        # Map path to current batch context for single process too
        self.path_to_batch[image_path] = self.current_batch_id

        # 1. CEK RAM CACHE (L1 - Paling Cepat)
        if image_path in self.ram_cache:
            if callback:
                callback(self.ram_cache[image_path], image_path)
            return

        # 2. CEK DISK CACHE (L2 - SQLite)
        if callback:
            repo = get_thumbnail_repo()
            cached_image = repo.get_thumbnail(image_path)

            if not cached_image.isNull():
                # Masukkan ke RAM agar akses berikutnya instan
                self.ram_cache[image_path] = cached_image
                callback(cached_image, image_path)
                return

            self.callbacks[image_path] = callback

        # 3. GENERATE (Spawn via QThreadPool to avoid handle leak)
        worker = ThumbnailWorker(
            image_path, self, self.current_batch_id, self.thumbnail_size
        )

        # Connect signals
        worker.signals.thumbnail_ready.connect(
            lambda img, path: self._on_thumbnail_ready(img, path)
        )

        # Start in global pool
        QThreadPool.globalInstance().start(worker)

    def reset_stats(self, batch_id, total_count):
        """Reset progress statistics for a new batch of work."""
        self.current_batch_id = str(batch_id)
        self.total_to_process = total_count
        self.decoded_count = 0
        self.total_to_save = total_count
        self.saved_count = 0
        self.path_to_batch.clear()  # Clear tracking context for efficiency
        self._emit_progress()

    def process_batch(self, image_paths, callback=None):
        """
        Process multiple images dengan Bulk Load dari RAM & Disk.
        """
        if not image_paths:
            return

        remaining_paths = []

        # 1. BULK LOAD DARI RAM (L1)
        for path in image_paths:
            # Map path to current batch context
            self.path_to_batch[path] = self.current_batch_id

            if path in self.ram_cache:
                if callback:
                    callback(self.ram_cache[path], path)

                # Update progress even for cache hits
                self.decoded_count += 1
                self.saved_count += 1
            else:
                remaining_paths.append(path)

        if not remaining_paths:
            self._emit_progress()
            return

        # 2. BULK LOAD DARI SQLite (L2) - Menggunakan Bulk Read Dinamis
        repo = get_thumbnail_repo()
        cached_thumbnails = repo.get_thumbnails_bulk(remaining_paths)

        final_to_process = []
        for path in remaining_paths:
            if path in cached_thumbnails:
                img = cached_thumbnails[path]
                self.ram_cache[path] = img  # Simpan ke L1
                if callback:
                    callback(img, path)

                # Update progress for L2 hits
                self.decoded_count += 1
                self.saved_count += 1
            else:
                final_to_process.append(path)
                if callback:
                    self.callbacks[path] = callback

        # Emit progress after cache checks
        self._emit_progress()

        # 3. SPAWN BULK GENERATOR (Chunked processing for high performance)
        if final_to_process:
            chunk_size = 20
            print(
                f"[ThumbnailProcessor] L1 hits, L2 hits: {len(image_paths)-len(final_to_process)}, "
                f"Decoding {len(final_to_process)} in chunks of {chunk_size}"
            )

            for i in range(0, len(final_to_process), chunk_size):
                chunk = final_to_process[i : i + chunk_size]
                bulk_worker = ThumbnailBulkWorker(
                    chunk, self, self.current_batch_id, self.thumbnail_size
                )

                # Connect common signal
                bulk_worker.signals.thumbnail_ready.connect(
                    lambda img, path: self._on_thumbnail_ready(img, path)
                )

                QThreadPool.globalInstance().start(bulk_worker)

    def _on_thumbnail_ready(self, q_image, image_path):
        """Internal callback saat dekoding gambar selesai."""
        is_success = not q_image.isNull()

        if is_success:
            # Simpan ke RAM Cache (L1)
            self.ram_cache[image_path] = q_image

            # Masukkan ke Pending Save Queue
            self.pending_save_queue.append((image_path, q_image))

            # Reset timer flush (Deferred Save)
            if len(self.pending_save_queue) >= 100:
                self.flush_to_disk()
            else:
                self.flush_timer.start(2000)

        # Progress tracking: Selalu update agar progress mencapai 100%
        if self.path_to_batch.get(image_path) == self.current_batch_id:
            self.decoded_count += 1
            if not is_success:
                # Jika gagal, anggap "tersimpan" (tidak perlu simpan) agar progress save juga naik
                self.saved_count += 1
            self._emit_progress()

        # Selalu jalankan callback agar UI berhenti menunjukkan loading
        if image_path in self.callbacks:
            callback = self.callbacks.pop(image_path)
            callback(q_image, image_path)

    def _emit_progress(self):
        """Kirim signal progress ke UI."""
        if self.total_to_process <= 0 or not self.current_batch_id:
            return

        decode_pct = int((self.decoded_count / self.total_to_process) * 100)
        save_pct = int((self.saved_count / self.total_to_process) * 100)

        # Cap at 100
        decode_pct = min(100, decode_pct)
        save_pct = min(100, save_pct)

        self.progress_updated.emit(self.current_batch_id, decode_pct, save_pct)

    def flush_to_disk(self):
        """
        Menyimpan semua thumbnail yang ada di queue ke database SQLite secara BULK.
        Menggunakan DYNAMIC BULK SIZE untuk efisiensi transaksi.
        """
        if not self.pending_save_queue:
            return

        data_to_save = self.pending_save_queue[:]
        self.pending_save_queue.clear()

        total_count = len(data_to_save)

        # --- LOGIKA DYNAMIC BULK SIZE ---
        chunk_size = 50
        if total_count >= 1499:
            chunk_size = 400
        elif total_count >= 999:
            chunk_size = 200
        elif total_count >= 500:
            chunk_size = 100

        print(
            f"[ThumbnailProcessor] DEFERRED SAVE: Writing {total_count} thumbnails to SQLite using chunk_size: {chunk_size}"
        )

        repo = get_thumbnail_repo()
        for i in range(0, total_count, chunk_size):
            chunk = data_to_save[i : i + chunk_size]
            repo.save_thumbnails_bulk(chunk)
            # Update saved count per chunk
            self.saved_count += len(chunk)
            self._emit_progress()

        print(f"[ThumbnailProcessor] Deferred save complete.")

    def stop_all(self):
        """Stop semua background tasks dan pastikan data tersimpan."""
        # 1. Bersihkan antrean thread pool agar tidak ada task baru mulai
        try:
            QThreadPool.globalInstance().clear()
        except Exception:
            pass

        # 2. Simpan data tertunda (harus sebelum cleanup)
        self.flush_to_disk()

        # 3. Cleanup state
        try:
            self.callbacks.clear()
            self.path_to_batch.clear()
            self.current_batch_id = None
        except Exception:
            pass

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.stop_all()
        except Exception:
            pass
