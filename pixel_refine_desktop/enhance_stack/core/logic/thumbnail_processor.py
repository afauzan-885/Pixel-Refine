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

from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import (
    load_raw_as_8bit_rgb_half_res,
)
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
from resources.animations.fade import fade_in
from pixel_refine_desktop.enhance_stack.core.logic.display_manager import (
    DisplayThreadManager,
)

from pixel_refine_desktop.enhance_stack.models.data_access.thumbnail_repository import (
    ThumbnailRepository,
)

# Max worker threads (standard 4 for balanced I/O and CPU)
MAX_THUMBNAIL_WORKERS = 4

# ---------------------------------------------------------------------------
# GLOBAL THUMBNAIL CACHE (L0) — RAM cache lintas batch, survive switch batch
# ---------------------------------------------------------------------------


class GlobalThumbnailCache:
    """
    Singleton RAM cache untuk thumbnail QImage.

    Cache bersifat global dan persist selama aplikasi berjalan — tidak
    di-reset saat user pindah batch. Ini memungkinkan navigasi instan
    antar batch tanpa decode ulang.

    Ukuran cache dibatasi (LRU-like eviction) untuk mengendalikan memori.
    Default: 500 gambar maks (~500 * 128x128 * 3 bytes ≈ 24 MB)
    """

    _instance = None
    MAX_SIZE = 500

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache: dict = {}  # path -> QImage
            cls._instance._order: list = []  # insertion order untuk LRU eviction
        return cls._instance

    def get(self, path: str):
        """Return cached QImage or None."""
        return self._cache.get(path)

    def put(self, path: str, q_image):
        """Store QImage in cache, evicting oldest if at capacity."""
        if path in self._cache:
            # Refresh order
            try:
                self._order.remove(path)
            except ValueError:
                pass
        elif len(self._cache) >= self.MAX_SIZE:
            # Evict least-recently-used entry
            oldest = self._order.pop(0)
            self._cache.pop(oldest, None)
        self._cache[path] = q_image
        self._order.append(path)

    def has(self, path: str) -> bool:
        return path in self._cache

    def clear(self):
        """Hapus seluruh cache (misalnya saat aplikasi shutdown)."""
        self._cache.clear()
        self._order.clear()

    def __len__(self):
        return len(self._cache)


# Module-level singleton accessor
def get_global_cache() -> GlobalThumbnailCache:
    return GlobalThumbnailCache()


# ---------------------------------------------------------------------------
# RAW DEMOSAIC THROTTLE — batasi maks 2 demosaic GPU paralel sekaligus
# ---------------------------------------------------------------------------
import threading


class RawDemosaicThrottle:
    """
    Singleton semaphore yang membatasi jumlah demosaic GPU/CPU yang berjalan
    paralel menjadi MAX_PARALLEL (default 2).

    Tanpa throttle, saat user membuat banyak batch cepat (batch 4-5-6
    dengan drag-drop), seluruh thread pool akan diisi job demosaic berat
    sehingga UI lag dan tidak responsif.
    """

    _instance = None
    MAX_PARALLEL = 2

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._sem = threading.Semaphore(cls.MAX_PARALLEL)
        return cls._instance

    def acquire(self):
        self._sem.acquire()

    def release(self):
        self._sem.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args):
        self.release()


def get_demosaic_throttle() -> RawDemosaicThrottle:
    return RawDemosaicThrottle()


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
    all_thumbnails_processed = Signal()  # Dipicu jika BulkWorker selesai (Fix GC)


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
            # 0. Cek GlobalThumbnailCache (L0 — paling cepat, persist lintas batch)
            global_cache = get_global_cache()
            cached_l0 = global_cache.get(self.image_path)
            if cached_l0 is not None and not cached_l0.isNull():
                result_image = cached_l0
                return  # langsung ke finally

            # 1. Cek Disk Cache (JPG di database/cache/thumbnails)
            repo = get_thumbnail_repo()
            cached_image = repo.get_thumbnail(self.image_path)
            if not cached_image.isNull():
                # Cache hit disk: simpan ke L0 agar batch switch berikutnya instan
                global_cache.put(self.image_path, cached_image)
                result_image = cached_image
                return

            if self._should_abort():
                return

            # 2. Decode gambar (demosaic untuk RAW, OpenCV/PIL untuk lainnya)
            pil_thumb = process_thumbnail_logic(self.image_path, self.thumbnail_size)

            if self._should_abort():
                return

            # 3. Simpan ke JPG -> muat kembali ke RAM -> emit ke UI
            if pil_thumb:
                temp_image = convert_pil_to_qimage(pil_thumb)
                if not temp_image.isNull():
                    repo.save_thumbnail(self.image_path, temp_image)
                    result_image = repo.get_thumbnail(self.image_path)
                    # Simpan ke L0 cache untuk akses instan ke depannya
                    if not result_image.isNull():
                        global_cache.put(self.image_path, result_image)

        except Exception as e:
            if not self._should_abort():
                print(f"[ThumbnailWorker] Error processing {self.image_path}: {e}")
        finally:
            # Selalu emit (cache hit maupun decode baru), agar UI selalu update
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
        global_cache = get_global_cache()
        for path in self.image_paths:
            if self._should_abort():
                return

            q_img_to_emit = QImage()
            try:
                # 0. Cek L0 RAM cache (GlobalThumbnailCache) — instan, lintas batch
                cached_l0 = global_cache.get(path)
                if cached_l0 is not None and not cached_l0.isNull():
                    q_img_to_emit = cached_l0
                    # Langsung lanjut ke emit, tidak perlu decode
                    if not self._should_abort():
                        self._safe_emit(q_img_to_emit, path)
                    continue

                # 1. Decode gambar (process_batch sudah filter cache miss sebelumnya)
                pil_thumb = process_thumbnail_logic(path, self.thumbnail_size)

                if self._should_abort():
                    return

                # 2. Simpan ke JPG di disk -> muat kembali -> emit ke UI (realtime)
                if pil_thumb:
                    temp_image = convert_pil_to_qimage(pil_thumb)
                    if not temp_image.isNull():
                        repo = get_thumbnail_repo()
                        repo.save_thumbnail(path, temp_image)
                        q_img_to_emit = repo.get_thumbnail(path)
                        # Simpan ke L0 untuk akses instan selanjutnya
                        if not q_img_to_emit.isNull():
                            global_cache.put(path, q_img_to_emit)
                else:
                    print(f"[ThumbnailBulkWorker] Failed to decode image: {path}")

            except Exception as e:
                # Jangan print error jika penyebabnya adalah shutdown
                if not self._should_abort():
                    print(
                        f"[ThumbnailBulkWorker] Critical error processing {path}: {e}"
                    )
            finally:
                # Always emit a signal for this path, even if it's an empty QImage
                # This ensures the UI can update its state (e.g., remove loading spinner)
                if not self._should_abort():
                    self._safe_emit(q_img_to_emit, path)

        # Emit final signal to help with GC cleanup
        if hasattr(self, "signals") and self.signals:
            try:
                self.signals.all_thumbnails_processed.emit()
            except (RuntimeError, AttributeError):
                pass

    def _safe_emit(self, q_image, path):
        """Emisi sinyal dengan perlindungan terhadap shutdown."""
        try:
            if hasattr(self, "signals") and self.signals:
                self.signals.thumbnail_ready.emit(q_image, path)
        except (RuntimeError, AttributeError):
            pass


def process_thumbnail_logic(image_path, thumbnail_size):
    """Core logic to process a single thumbnail, used by both workers.

    Untuk file RAW: menggunakan RawDemosaicThrottle agar maks 2 demosaic
    GPU/CPU berjalan paralel, mencegah overload saat pembuatan batch cepat.
    Hasil thumbnail langsung disimpan ke GlobalThumbnailCache (L0).
    """
    global_cache = get_global_cache()

    # L0 check — return immediately if already in global RAM cache
    cached = global_cache.get(image_path)
    if cached is not None:
        # Kembalikan PIL-compatible via convert dari QImage
        # Catatan: caller mengharap PIL Image, jadi kita skip L0 di sini
        # dan biarkan ThumbnailWorker/BulkWorker handle cache hit via
        # process_image/process_batch yang sudah cek global_cache lebih awal.
        pass

    try:
        # 1. Fast path for common formats using OpenCV
        if image_path.lower().endswith((".jpg", ".jpeg", ".png")):
            img = cv2.imread(image_path)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img)
                return ImageOps.fit(pil_img, thumbnail_size, Image.Resampling.BILINEAR)

        # 2. Fallback to PIL for TIFF, RAW, etc.
        ext = os.path.splitext(image_path)[1].lower()
        if ext in SUPPORTED_FORMATS.get("raw", []):
            throttle = get_demosaic_throttle()
            try:
                from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import (
                    taichi_lock,
                )

                # Gunakan throttle: maks 2 demosaic GPU paralel
                with throttle:
                    # Direct GPU demosaic half resolution (always consistent with full preview).
                    # load_raw_as_8bit_rgb_half_res already returns RGB uint8.
                    img_array = load_raw_as_8bit_rgb_half_res(image_path)

                if img_array is not None:
                    pil_img = Image.fromarray(img_array, "RGB")
                    return ImageOps.fit(
                        pil_img, thumbnail_size, Image.Resampling.BILINEAR
                    )
                else:
                    raise RuntimeError("Hamilton demosaic returned None")
            except Exception as e_raw:
                print(
                    f"[ThumbnailProcessor] Hamilton RAW decoding failed for {image_path}: {e_raw}. Falling back to full demosaic."
                )

            # Fallback 2: Full demosaic (Hamilton/Taichi) if fast method fails
            from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import (
                load_raw_as_8bit_rgb,
            )

            # Full demosaic juga dibatasi oleh throttle
            throttle = get_demosaic_throttle()
            with throttle:
                img_array = load_raw_as_8bit_rgb(image_path)
            pil_img = Image.fromarray(img_array, "RGB")
            return ImageOps.fit(pil_img, thumbnail_size, Image.Resampling.BILINEAR)

        with Image.open(image_path) as img:
            img_corrected = ImageOps.exif_transpose(img)
            return ImageOps.fit(
                img_corrected, thumbnail_size, Image.Resampling.BILINEAR
            )

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
    # Signal untuk melaporkan progres pemeriksaan awal (cek disk/cache)
    check_progress = Signal(str, int)

    def __init__(self, thumbnail_size=(128, 128), max_concurrent=None):
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
        self.path_to_batch = {}  # Tracking context
        self._active_workers = (
            set()
        )  # Proteksi agar worker tidak kena GC (Fix Loading Abadi)
        self._in_flight = set()  # Track items currently being processed/fetched
        self._processed_paths = (
            set()
        )  # Track paths already counted towards decoded_count
        self._persisted_paths = set()  # Track paths already counted towards saved_count

        # Performance tuning
        # Timer untuk melakukan bulk save ke disk saat idle
        self.flush_timer = QTimer()
        self.flush_timer.setSingleShot(True)
        self.flush_timer.timeout.connect(self.flush_to_disk)

        # Track last emitted progress to avoid redundancy
        self._last_emit_decode = -1
        self._last_emit_save = -1

        # Config QThreadPool (Dynamic scaling based on CPU count)
        if max_concurrent is None:
            import os

            # Set to CPU logical core count, min 4 and max 12 to balance I/O and CPU
            max_concurrent = max(4, min(12, os.cpu_count() or 4))
        QThreadPool.globalInstance().setMaxThreadCount(max_concurrent)

    def add_to_stats(self, count):
        """Tambah jumlah total gambar yang diproses secara dinamis (incremental)."""
        self.total_to_process += count
        self.total_to_save += count
        self._emit_progress()

    def process_image(self, image_path, callback=None):
        """
        Process single image thumbnail dengan sistem cache 3 level (L0 Global -> L1 RAM -> L2 Disk).
        """
        # Map path to current batch context for single process too
        self.path_to_batch[image_path] = self.current_batch_id

        # 0. CEK GLOBAL RAM CACHE (L0 - Persist lintas batch)
        global_cache = get_global_cache()
        cached_l0 = global_cache.get(image_path)
        if cached_l0 is not None and not cached_l0.isNull():
            # Sinkronisasikan ke L1 juga
            self.ram_cache[image_path] = cached_l0
            if callback:
                callback(cached_l0, image_path)
            return

        # 1. CEK RAM CACHE (L1 - Paling Cepat, session ini)
        if image_path in self.ram_cache:
            # Populasi ke L0 jika belum ada
            global_cache.put(image_path, self.ram_cache[image_path])
            if callback:
                callback(self.ram_cache[image_path], image_path)
            return

        # 2. CEK DISK CACHE (L2 - SQLite)
        if callback:
            repo = get_thumbnail_repo()
            cached_image = repo.get_thumbnail(image_path)

            if not cached_image.isNull():
                # Masukkan ke L1 dan L0 agar akses berikutnya instan
                self.ram_cache[image_path] = cached_image
                global_cache.put(image_path, cached_image)
                callback(cached_image, image_path)
                return

            # Cek apakah sudah sedang diproses (in-flight)
            if image_path in self._in_flight:
                self.callbacks[image_path] = callback
                return

            self.callbacks[image_path] = callback

        # Mark as in-flight
        self._in_flight.add(image_path)

        # 3. GENERATE (Spawn via QThreadPool to avoid handle leak)
        worker = ThumbnailWorker(
            image_path, self, self.current_batch_id, self.thumbnail_size
        )

        # Connect signals
        worker.signals.thumbnail_ready.connect(
            lambda img, path: self._on_thumbnail_ready(img, path)
        )

        # Proteksi GC: Simpan referensi worker
        self._active_workers.add(worker)
        # Hapus referensi setelah selesai (apapun hasilnya)
        worker.signals.thumbnail_ready.connect(
            lambda: self._active_workers.discard(worker)
        )

        # Start in global pool
        QThreadPool.globalInstance().start(worker)

    def reset_stats(self, batch_id, total_count):
        """Reset progress statistics for a new batch of work."""
        self.current_batch_id = str(batch_id)
        self.total_to_process = total_count
        self.decoded_count = 0
        self.saved_count = 0
        self.path_to_batch.clear()  # Clear tracking context for efficiency
        self._in_flight.clear()
        self._processed_paths.clear()
        self._persisted_paths.clear()
        self._last_emit_decode = -1
        self._last_emit_save = -1
        self._emit_progress()

    def process_batch(self, image_paths, callback=None):
        """
        Process multiple images dengan Bulk Load dari L0 Global -> L1 RAM -> L2 Disk.
        """
        if not image_paths:
            return

        remaining_paths = []
        global_cache = get_global_cache()

        # 0. BULK LOAD DARI GLOBAL RAM CACHE (L0 - Persist lintas batch)
        #    Ini adalah tier pertama dan tercepat — tidak ada I/O sama sekali.
        for path in image_paths:
            # Map path to current batch context
            self.path_to_batch[path] = self.current_batch_id

            cached_l0 = global_cache.get(path)
            if cached_l0 is not None and not cached_l0.isNull():
                # L0 hit: sinkronisasikan ke L1 juga
                self.ram_cache[path] = cached_l0
                if callback:
                    callback(cached_l0, path)

                # Update progress (Avoid double counting)
                if path not in self._processed_paths:
                    self._processed_paths.add(path)
                    self.decoded_count += 1

                if path not in self._persisted_paths:
                    self._persisted_paths.add(path)
                    self.saved_count += 1
            else:
                remaining_paths.append(path)

        if not remaining_paths:
            self._emit_progress()
            return

        # 1. BULK LOAD DARI RAM (L1)
        still_remaining = []
        for path in remaining_paths:
            if path in self.ram_cache:
                # L1 hit: populasikan ke L0
                global_cache.put(path, self.ram_cache[path])
                if callback:
                    callback(self.ram_cache[path], path)

                # Update progress even for cache hits (Avoid double counting)
                if path not in self._processed_paths:
                    self._processed_paths.add(path)
                    self.decoded_count += 1

                if path not in self._persisted_paths:
                    self._persisted_paths.add(path)
                    self.saved_count += 1
            else:
                still_remaining.append(path)

        remaining_paths = still_remaining

        if not remaining_paths:
            self._emit_progress()
            return

        # 2. BULK LOAD DARI Disk Cache (L2) - JPG di database/cache/thumbnails
        repo = get_thumbnail_repo()

        # Emit initial check progress (0%)
        self.check_progress.emit(self.current_batch_id, 0)

        # Split remaining into hits and misses with incremental progress emission
        batch_size = 50  # Process in small chunks for progress feedback
        cached_thumbnails = {}

        for i in range(0, len(remaining_paths), batch_size):
            chunk = remaining_paths[i : i + batch_size]
            hits = repo.get_thumbnails_bulk(chunk)
            cached_thumbnails.update(hits)

            # Emit progress percentage
            pct = int(((i + len(chunk)) / len(remaining_paths)) * 100)
            self.check_progress.emit(self.current_batch_id, pct)

        final_to_process = []
        for path in remaining_paths:
            if path in cached_thumbnails:
                img = cached_thumbnails[path]
                self.ram_cache[path] = img  # Simpan ke L1
                global_cache.put(path, img)  # Simpan ke L0 untuk instan lintas batch
                if callback:
                    callback(img, path)

                # Update progress for L2 hits (Avoid double counting)
                if path not in self._processed_paths:
                    self._processed_paths.add(path)
                    self.decoded_count += 1

                if path not in self._persisted_paths:
                    self._persisted_paths.add(path)
                    self.saved_count += 1

            else:
                # Cek apakah sedang dalam antrean (in-flight)
                if path not in self._in_flight:
                    final_to_process.append(path)
                    if callback:
                        self.callbacks[path] = callback
                else:
                    # Jika in-flight, cukup tambahkan callback jika ada
                    if callback:
                        self.callbacks[path] = callback

        # Final check progress (100%)
        self.check_progress.emit(self.current_batch_id, 100)

        # Emit progress after cache checks
        self._emit_progress()

        # 3. SPAWN BULK GENERATOR (Chunked processing for high performance)
        if final_to_process:
            chunk_size = 20
            # print(
            #     f"[ThumbnailProcessor] L1 hits, L2 hits: {len(image_paths)-len(final_to_process)}, "
            #     f"Decoding {len(final_to_process)} in chunks of {chunk_size}"
            # )

            for i in range(0, len(final_to_process), chunk_size):
                chunk = final_to_process[i : i + chunk_size]

                # Mark as in-flight
                for p in chunk:
                    self._in_flight.add(p)

                bulk_worker = ThumbnailBulkWorker(
                    chunk, self, self.current_batch_id, self.thumbnail_size
                )

                # Connect common signal
                bulk_worker.signals.thumbnail_ready.connect(
                    lambda img, path: self._on_thumbnail_ready(img, path)
                )

                # Proteksi GC: Simpan referensi worker (Fix "Loading 2%")
                self._active_workers.add(bulk_worker)

                # Gunakan wrapper untuk disconnect/discard saat batch ini selesai diproses oleh worker ini
                # Kita tidak bisa pakai satu sinyal untuk hapus, karena bulk emit banyak.
                # Namun QRunnable di pool akan hancur setelah run() selesai.
                # Idealnya ada sinyal 'finished'. Karena tidak ada, kita bisa buat di signals.
                bulk_worker.signals.all_thumbnails_processed.connect(
                    lambda: self._active_workers.discard(bulk_worker)
                )

                QThreadPool.globalInstance().start(bulk_worker)

    def _on_thumbnail_ready(self, q_image, image_path):
        """Internal callback saat dekoding gambar selesai."""
        is_success = not q_image.isNull()

        # Remove from in-flight tracker
        if image_path in self._in_flight:
            self._in_flight.discard(image_path)

        if is_success:
            # Simpan ke RAM Cache (L1)
            self.ram_cache[image_path] = q_image

        # Progress tracking: Selalu update agar progress mencapai 100%
        if self.path_to_batch.get(image_path) == self.current_batch_id:
            if image_path not in self._processed_paths:
                self._processed_paths.add(image_path)
                self.decoded_count += 1

            if image_path not in self._persisted_paths:
                self._persisted_paths.add(image_path)
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

        # Only emit if values changed
        if decode_pct != self._last_emit_decode or save_pct != self._last_emit_save:
            self._last_emit_decode = decode_pct
            self._last_emit_save = save_pct
            self.progress_updated.emit(self.current_batch_id, decode_pct, save_pct)

    def flush_to_disk(self):
        """
        Menyimpan semua thumbnail yang ada di pending queue ke disk (JPG) secara BULK.
        Dipanggil saat idle atau saat stop_all() untuk memastikan tidak ada yang terlewat.
        """
        if not self.pending_save_queue:
            return

        data_to_save = self.pending_save_queue[:]
        self.pending_save_queue.clear()

        total_count = len(data_to_save)

        # Dynamic chunk size berdasarkan volume
        chunk_size = 50
        if total_count >= 1499:
            chunk_size = 400
        elif total_count >= 999:
            chunk_size = 200
        elif total_count >= 500:
            chunk_size = 100

        repo = get_thumbnail_repo()
        for i in range(0, total_count, chunk_size):
            chunk = data_to_save[i : i + chunk_size]
            repo.save_thumbnails_bulk(chunk)

            # Update saved count (Avoid double counting)
            for path, img in chunk:
                if path not in self._persisted_paths:
                    self._persisted_paths.add(path)
                    self.saved_count += 1
            self._emit_progress()

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
