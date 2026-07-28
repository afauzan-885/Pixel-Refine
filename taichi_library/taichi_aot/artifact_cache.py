"""Small persistent cache for backend artifact validation status."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import tempfile
import threading
import time


def _cache_path():
    root = os.environ.get("PIXEL_REFINE_AOT_CACHE") or os.path.join(
        tempfile.gettempdir(), "pixel_refine_aot_cache"
    )
    os.makedirs(root, exist_ok=True)
    return os.path.join(root, "artifact_status.json")


def artifact_key(path, backend, device_id=0, device_name="unknown"):
    path = os.path.abspath(path)
    st = os.stat(path) if os.path.isfile(path) else None
    token = "|".join((path, backend.lower(), str(device_id), device_name,
                      platform.platform(), str(getattr(st, "st_size", 0)),
                      str(getattr(st, "st_mtime_ns", 0))))
    return hashlib.sha256(token.encode("utf-8", "replace")).hexdigest()


def get_status(key):
    try:
        with open(_cache_path(), "r", encoding="utf-8") as f:
            return json.load(f).get(key)
    except (OSError, ValueError, TypeError):
        return None


def set_status(key, status, **extra):
    path = _cache_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError, TypeError):
        data = {}
    data[key] = {"status": status, **extra}
    # Child-process validators update the same cache concurrently. A shared
    # fixed ``.tmp`` name causes WinError 32 during os.replace; use a unique
    # staging file and retry briefly while another writer rotates the cache.
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
