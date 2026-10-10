"""Small cached previews and a bounded, cancellable queue for the bulk viewport."""

import hashlib
import io
import os
import tempfile
import weakref
from collections import OrderedDict

import rawpy
from PIL import Image, ImageOps
from PySide6.QtGui import QImage
from PySide6.QtCore import (
    QObject, QRunnable, QThreadPool, QTimer, QThread, Signal, Slot,
    QMutex, QWaitCondition, QSemaphore, Qt,
)
from config import CACHE_DIR, SUPPORTED_FORMATS
from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_policy import thumbnail_creation_enabled

semaphore = QSemaphore(2)
_retired_loaders = set()
THUMBNAIL_SIZE = (80, 80)


def _cache_path(image_path):
    stat = os.stat(image_path)
    identity = f"bulk80-v2|{os.path.normcase(os.path.abspath(image_path))}|{stat.st_size}|{stat.st_mtime_ns}"
    return os.path.join(CACHE_DIR, hashlib.sha1(identity.encode("utf-8")).hexdigest() + ".jpg")


def _small_preview(image):
    # JPEG draft avoids decoding the full image before downsizing.
    image.draft("RGB", THUMBNAIL_SIZE)
    image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.BILINEAR, reducing_gap=3.0)
    return ImageOps.exif_transpose(image).convert("RGB")


def load_bulk_thumbnail(image_path):
    """Run only in a worker; reuse disk cache before opening the source decoder."""
    cache_path = _cache_path(image_path)
    source_mtime = os.path.getmtime(image_path)
    shared_cache = os.path.join(CACHE_DIR, hashlib.sha1(image_path.encode("utf-8")).hexdigest() + ".jpg")
    for candidate in (cache_path, shared_cache):
        if os.path.isfile(candidate) and os.path.getmtime(candidate) >= source_mtime:
            cached = QImage(candidate)
            if not cached.isNull():
                return cached.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    if os.path.splitext(image_path)[1].lower() in SUPPORTED_FORMATS["raw"]:
        # open_file + extract_thumb reads the embedded preview without unpacking CFA.
        with rawpy.RawPy() as raw:
            raw.open_file(image_path)
            try:
                thumb = raw.extract_thumb()
                if thumb.format == rawpy.ThumbFormat.JPEG:
                    with Image.open(io.BytesIO(thumb.data)) as image:
                        preview = _small_preview(image)
                else:
                    preview = _small_preview(Image.fromarray(thumb.data))
            except (rawpy.LibRawNoThumbnailError, rawpy.LibRawUnsupportedThumbnailError):
                raw.unpack()
                image = Image.fromarray(raw.postprocess(
                    output_bps=8, use_camera_wb=True, half_size=True,
                    demosaic_algorithm=rawpy.DemosaicAlgorithm.LINEAR,
                ))
                preview = _small_preview(image)
    else:
        with Image.open(image_path) as image:
            preview = _small_preview(image)

    pixels = preview.tobytes()
    result = QImage(pixels, preview.width, preview.height, preview.width * 3, QImage.Format_RGB888).copy()
    # Atomic publication prevents a cache reader from seeing a partial JPEG.
    temporary = None
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(dir=CACHE_DIR, suffix=".partial")
        os.close(descriptor)
        if result.save(temporary, "JPG", 85):
            os.replace(temporary, cache_path)
    except OSError:
        pass  # A read-only cache must not prevent showing the decoded thumbnail.
    finally:
        if temporary is not None:
            try:
                os.remove(temporary)
            except OSError:
                pass
    return result


class _ThumbnailTask(QRunnable):
    def __init__(self, path, ready):
        super().__init__()
        self.path = path
        self.ready = ready

    def run(self):
        image = QImage()
        semaphore.acquire()
        try:
            image = load_bulk_thumbnail(self.path)
        except Exception as error:
            print(f"[BulkThumbnailService] {self.path}: {error}")
        finally:
            semaphore.release()
            self.ready.emit(self.path, image)


class ThumbnailScheduler(QObject):
    """Only submit jobs when a pool slot is free; discard obsolete viewport requests."""
    ready = Signal(str, QImage)

    def __init__(self, parent=None, max_workers=2):
        super().__init__(parent)
        self.max_workers = max_workers
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(max_workers)
        self.pending = OrderedDict()
        self.active = {}
        self.ready.connect(self._on_ready, Qt.QueuedConnection)
        self._pump_timer = QTimer(self)
        self._pump_timer.setSingleShot(True)
        self._pump_timer.timeout.connect(self._pump)

    def request(self, owner, path, callback):
        listeners = self.active.get(path)
        if listeners is None:
            listeners = self.pending.setdefault(path, {})
        listeners[id(owner)] = (weakref.ref(owner), callback)
        self._pump_timer.start(0)

    def cancel(self, owner):
        for requests in (self.pending, self.active):
            for path in list(requests):
                requests[path].pop(id(owner), None)
                if not requests[path] and requests is self.pending:
                    del requests[path]

    def cancel_all(self):
        self.pending.clear()
        for listeners in self.active.values():
            listeners.clear()
        self._pump_timer.stop()

    @Slot()
    def _pump(self):
        while self.pending and len(self.active) < self.max_workers:
            path, listeners = self.pending.popitem(last=False)
            self.active[path] = listeners
            self.pool.start(_ThumbnailTask(path, self.ready))

    @Slot(str, QImage)
    def _on_ready(self, path, image):
        listeners = self.active.pop(path, {})
        for owner_ref, callback in list(listeners.values()):
            owner = owner_ref()
            if owner is not None:
                try:
                    callback(image, path)
                except RuntimeError:
                    pass  # The panel may have been destroyed since its request.
        self._pump_timer.start(0)


class ThumbnailLoader(QThread):
    """
    QThread for generating image thumbnails asynchronously using Pillow.
    """
    thumbnail_ready = Signal(QImage, str)

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.paused = False
        self.mutex = QMutex()
        self.cond = QWaitCondition()

    def pause(self):
        self.mutex.lock()
        self.paused = True
        self.mutex.unlock()

    def resume(self):
        self.mutex.lock()
        self.paused = False
        self.cond.wakeAll()
        self.mutex.unlock()

    def run(self):
        result = QImage()
        while not semaphore.tryAcquire(1, 100):
            if self.isInterruptionRequested():
                return
        try:
            if self.isInterruptionRequested() or not thumbnail_creation_enabled():
                return
            self.mutex.lock()
            while self.paused and not self.isInterruptionRequested():
                self.cond.wait(self.mutex, 100)
            self.mutex.unlock()
            if not self.isInterruptionRequested():
                result = load_bulk_thumbnail(self.image_path)
        except Exception as error:
            print(f"[BulkThumbnailService] {self.image_path}: {error}")
        finally:
            semaphore.release()
            if not self.isInterruptionRequested() and thumbnail_creation_enabled():
                self.thumbnail_ready.emit(result, self.image_path)


def stop_process_thumbnails(threads):
    """Request cancellation without waiting in the GUI; retain running QThreads."""
    for thread in list(threads):
        try:
            thread.thumbnail_ready.disconnect()
        except (TypeError, RuntimeError):
            pass
        if thread.isRunning():
            _retired_loaders.add(thread)
            thread.finished.connect(lambda thread=thread: _release_loader(thread))
            thread.requestInterruption()
        else:
            thread.deleteLater()
    threads.clear()


def _release_loader(thread):
    _retired_loaders.discard(thread)
    thread.deleteLater()
