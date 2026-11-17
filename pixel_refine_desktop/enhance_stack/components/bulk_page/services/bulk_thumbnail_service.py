"""Small cached previews and a bounded, cancellable queue for the bulk viewport."""

import hashlib
import io
import os
import tempfile
import weakref
from collections import OrderedDict

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError
from PySide6.QtGui import QImage
from PySide6.QtCore import (
    QObject, QRunnable, QThreadPool, QTimer, QThread, Signal, Slot,
    QMutex, QWaitCondition, QSemaphore, Qt,
)
from config import CACHE_DIR, SUPPORTED_FORMATS
from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_policy import (
    thumbnail_creation_enabled,
    thumbnail_generation_suspended,
)

semaphore = QSemaphore(2)
_retired_loaders = set()
THUMBNAIL_SIZE = (80, 80)


def _cache_path(image_path):
    stat = os.stat(image_path)
    identity = f"bulk80-v2|{os.path.normcase(os.path.abspath(image_path))}|{stat.st_size}|{stat.st_mtime_ns}"
    return os.path.join(CACHE_DIR, hashlib.sha1(identity.encode("utf-8")).hexdigest() + ".jpg")


def _small_preview(image, apply_exif=True):
    # JPEG draft avoids decoding the full image before downsizing.
    image.draft("RGB", THUMBNAIL_SIZE)
    image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.BILINEAR, reducing_gap=3.0)
    if apply_exif:
        image = ImageOps.exif_transpose(image)
    return image.convert("RGB")


def _apply_tiff_orientation(image, orientation):
    operations = {
        2: Image.Transpose.FLIP_LEFT_RIGHT,
        3: Image.Transpose.ROTATE_180,
        4: Image.Transpose.FLIP_TOP_BOTTOM,
        5: Image.Transpose.TRANSPOSE,
        6: Image.Transpose.ROTATE_270,
        7: Image.Transpose.TRANSVERSE,
        8: Image.Transpose.ROTATE_90,
    }
    operation = operations.get(int(orientation or 1))
    return image.transpose(operation) if operation is not None else image


def _decode_embedded_preview(preview_bytes, payload):
    """Open an embedded preview when its bytes are an image container or raw RGB."""
    if not preview_bytes:
        return None
    signatures = (
        b"\xff\xd8",  # JPEG
        b"\x89PNG\r\n\x1a\n",  # PNG
        b"II*\x00",  # TIFF little-endian
        b"MM\x00*",  # TIFF big-endian
    )
    if preview_bytes.startswith(signatures):
        try:
            return Image.open(io.BytesIO(preview_bytes))
        except (UnidentifiedImageError, OSError, ValueError):
            return None
    if not isinstance(payload, dict):
        return None
    width = int(payload.get("width") or 0)
    height = int(payload.get("height") or 0)
    if width <= 0 or height <= 0 or int(payload.get("compression") or 0) != 1:
        return None
    photometric = int(payload.get("photometric") or 0)
    if len(preview_bytes) != width * height * 3:
        return None
    if photometric == 2:
        return Image.frombytes("RGB", (width, height), preview_bytes)
    if photometric == 6:
        return Image.frombytes("YCbCr", (width, height), preview_bytes)
    return None


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
        import taichi

        try:
            payload = taichi.imread(image_path, mode="preview")
            preview_bytes = payload.get("preview") if isinstance(payload, dict) else None
            orientation = int(payload.get("orientation", 1) or 1) if isinstance(payload, dict) else 1
            preview = None
            embedded = _decode_embedded_preview(preview_bytes, payload)
            if embedded is not None:
                try:
                    with embedded as image:
                        preview = _apply_tiff_orientation(
                            _small_preview(image, apply_exif=False), orientation
                        )
                except (OSError, ValueError):
                    preview = None
            if preview is None:
                from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import (
                    load_raw_as_8bit_rgb_half_res,
                )

                array = load_raw_as_8bit_rgb_half_res(image_path)
                preview = _small_preview(Image.fromarray(np.asarray(array)))
        except Exception as exc:
            raise RuntimeError(
                f"Native RAW thumbnail failed for {image_path}: {exc}"
            ) from exc
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
        self.pool.setThreadPriority(QThread.Priority.LowPriority)
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

    def cancel_except(self, owner, keep_paths):
        """Drop this owner's obsolete viewport listeners but retain visible work."""
        keep_paths = set(keep_paths)
        owner_id = id(owner)
        for requests in (self.pending, self.active):
            for path in list(requests):
                if path in keep_paths:
                    continue
                requests[path].pop(owner_id, None)
                if not requests[path] and requests is self.pending:
                    del requests[path]

    def cancel_all(self):
        self.pending.clear()
        for listeners in self.active.values():
            listeners.clear()
        self._pump_timer.stop()

    def resume(self):
        """Restart queued thumbnail work after compute released the backend."""
        self._pump_timer.start(0)

    @Slot()
    def _pump(self):
        if thumbnail_generation_suspended():
            # Keep every request queued; resume() re-arms the pump later.
            return
        while self.pending and len(self.active) < self.max_workers:
            path, listeners = self.pending.popitem(last=False)
            self.active[path] = listeners
            # The pool itself carries the low-priority setting. Passing Qt's
            # Priority enum as the overload's int argument fails in PySide6.
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
            while (self.paused or thumbnail_generation_suspended()) and not self.isInterruptionRequested():
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
