"""Small persistent cache for backend artifact validation status."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import tempfile
import threading
import time
from contextlib import contextmanager


_CACHE_PROCESS_LOCK = threading.RLock()
# The status cache records runtime load results, not only artifact identity.
# Bump this namespace when the loader/bridge contract changes so a previous
# native failure cannot permanently block a now-compatible artifact.
_CACHE_SCHEMA = "3"


def _cache_path():
    root = os.environ.get("PIXEL_REFINE_AOT_CACHE") or os.path.join(
        tempfile.gettempdir(), "pixel_refine_aot_cache"
    )
    os.makedirs(root, exist_ok=True)
    return os.path.join(root, "artifact_status.json")


def artifact_key(path, backend, device_id=0, device_name="unknown"):
    # Windows paths are case-insensitive, but ``Path.resolve()`` and a
    # subprocess launched through a differently-cased drive letter can yield
    # ``E:\\...`` versus ``e:\\...``.  Hash a canonical real path so a valid
    # artifact is not mistaken for a different (and quarantined) artifact.
    path = os.path.normcase(os.path.realpath(os.path.abspath(path)))
    st = os.stat(path) if os.path.isfile(path) else None
    compatibility = os.environ.get(
        "PIXEL_REFINE_GFX_COMPAT_MODE",
        os.environ.get("PIXEL_REFINE_INTEL_GFX_COMPAT", "auto"),
    )
    token = "|".join((_CACHE_SCHEMA, str(compatibility).lower(), path, backend.lower(), str(device_id), device_name,
                       platform.platform(), str(getattr(st, "st_size", 0)),
                       str(getattr(st, "st_mtime_ns", 0))))
    return hashlib.sha256(token.encode("utf-8", "replace")).hexdigest()


def get_status(key):
    if os.environ.get("PIXEL_REFINE_AOT_DISABLE_CACHE", "0") == "1":
        return None
    try:
        with open(_cache_path(), "r", encoding="utf-8") as f:
            return json.load(f).get(key)
    except (OSError, ValueError, TypeError):
        return None


@contextmanager
def _cache_write_lock(path):
    """Serialize status writers across threads and child processes.

    ``os.replace`` makes each individual write atomic, but without a lock two
    writers can still read the same old JSON and one update can erase the
    other.  A one-byte sidecar lock works on Windows (``msvcrt``) and POSIX
    (``fcntl``) without adding a runtime dependency.
    """
    lock_path = path + ".lock"
    with _CACHE_PROCESS_LOCK:
        with open(lock_path, "a+b") as lock:
            if os.path.getsize(lock_path) == 0:
                lock.write(b"\0")
                lock.flush()
            lock.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl

                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                if os.name == "nt":
                    import msvcrt

                    lock.seek(0)
                    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def set_status(key, status, **extra):
    if os.environ.get("PIXEL_REFINE_AOT_DISABLE_CACHE", "0") == "1":
        return
    path = _cache_path()
    with _cache_write_lock(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError, TypeError):
            data = {}
        data[key] = {"status": status, **extra}
        # Child-process validators update the same cache concurrently. A
        # shared fixed ``.tmp`` name causes WinError 32 during os.replace; use
        # a unique staging file and retry briefly while another writer rotates
        # the cache.
        tmp = os.path.join(
            os.path.dirname(path),
            f"artifact_status.{os.getpid()}.{threading.get_ident()}.tmp",
        )
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        try:
            for attempt in range(12):
                try:
                    os.replace(tmp, path)
                    break
                except PermissionError:
                    if attempt == 11:
                        raise
                    time.sleep(0.025 * (attempt + 1))
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass
