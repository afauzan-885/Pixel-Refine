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
# Cache entries are bound to artifact contents as well as runtime identity.
# Bump the schema if that status contract or the loader/bridge contract changes.
_CACHE_SCHEMA = 4
_CACHE_KEY_PREFIX = f"v{_CACHE_SCHEMA}"


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
    compatibility = os.environ.get(
        "PIXEL_REFINE_GFX_COMPAT_MODE",
        os.environ.get("PIXEL_REFINE_INTEL_GFX_COMPAT", "auto"),
    )
    identity = "|".join(
        (
            str(_CACHE_SCHEMA),
            str(compatibility).lower(),
            _stable_artifact_path(path),
            backend.lower(),
            str(device_id),
            device_name,
            platform.platform(),
        )
    )
    identity_digest = hashlib.sha256(identity.encode("utf-8", "replace")).hexdigest()
    content_digest = _content_fingerprint(path)
    return f"{_CACHE_KEY_PREFIX}:{identity_digest}:{content_digest}"


def _stable_artifact_path(path):
    """Normalize CPU extraction paths whose directory name is a TCM hash."""
    parent = os.path.dirname(path)
    artifact_digest = os.path.basename(path)
    if (
        os.path.basename(parent) == ".cpu_aot_cache"
        and len(artifact_digest) == 64
        and all(char in "0123456789abcdef" for char in artifact_digest.lower())
    ):
        marker = os.path.join(path, "__content__")
        try:
            with open(marker, "rb") as source:
                module_identity = hashlib.sha256(source.read()).hexdigest()
        except OSError:
            module_identity = "unknown-module"
        # CPU artifacts are extracted beneath a content-addressed directory.
        # Use the stable module marker for identity and the full directory hash
        # below for content, so replacing a TCM invalidates its old status.
        return os.path.join(parent, "<cpu-aot>", module_identity)
    return path


def _content_fingerprint(path):
    """Hash the bytes the runtime will load, independent of mtime/size."""
    digest = hashlib.sha256()
    if os.path.isfile(path):
        digest.update(b"file\0")
        _update_file_digest(digest, path)
        return digest.hexdigest()
    if os.path.isdir(path):
        digest.update(b"directory\0")
        for root, directories, filenames in os.walk(path, followlinks=False):
            directories.sort()
            filenames.sort()
            for directory in directories:
                directory_path = os.path.join(root, directory)
                if os.path.islink(directory_path):
                    relative_path = os.path.relpath(directory_path, path).replace(
                        os.sep, "/"
                    )
                    digest.update(relative_path.encode("utf-8", "replace"))
                    digest.update(b"\0link\0")
                    digest.update(os.readlink(directory_path).encode("utf-8", "replace"))
            for filename in filenames:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, path).replace(os.sep, "/")
                digest.update(relative_path.encode("utf-8", "replace"))
                digest.update(b"\0")
                if os.path.islink(file_path):
                    digest.update(b"link\0")
                    digest.update(os.readlink(file_path).encode("utf-8", "replace"))
                else:
                    digest.update(b"file\0")
                    _update_file_digest(digest, file_path)
        return digest.hexdigest()
    digest.update(b"missing\0")
    return digest.hexdigest()


def _update_file_digest(digest, path):
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)


def _key_identity(key):
    parts = str(key).split(":", 2)
    if len(parts) == 3 and parts[0] == _CACHE_KEY_PREFIX:
        return parts[1]
    return None


def _load_entries(path):
    """Read the current cache format; old status-only caches are untrusted."""
    try:
        with open(path, "r", encoding="utf-8") as source:
            data = json.load(source)
    except (OSError, ValueError, TypeError):
        return {}, True
    if (
        isinstance(data, dict)
        and data.get("_schema") == _CACHE_SCHEMA
        and isinstance(data.get("_entries"), dict)
    ):
        return data["_entries"], False
    # Previous schemas did not bind status to the artifact's content. Discard
    # those status records once rather than risk reusing a stale quarantine.
    return {}, True


def _prune_stale_identity(entries, key):
    identity = _key_identity(key)
    if identity is None:
        return False
    stale = [
        old_key
        for old_key in entries
        if old_key != key and _key_identity(old_key) == identity
    ]
    for old_key in stale:
        del entries[old_key]
    return bool(stale)


def _write_entries(path, entries):
    data = {"_schema": _CACHE_SCHEMA, "_entries": entries}
    # Child-process validators update the same cache concurrently. A shared
    # fixed ``.tmp`` name can collide during os.replace, so use a unique file.
    tmp = os.path.join(
        os.path.dirname(path),
        f"artifact_status.{os.getpid()}.{threading.get_ident()}.tmp",
    )
    with open(tmp, "w", encoding="utf-8") as target:
        json.dump(data, target, indent=2, sort_keys=True)
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


def get_status(key):
    if os.environ.get("PIXEL_REFINE_AOT_DISABLE_CACHE", "0") == "1":
        return None
    path = _cache_path()
    with _cache_write_lock(path):
        entries, migrated = _load_entries(path)
        pruned = _prune_stale_identity(entries, key)
        if migrated or pruned:
            _write_entries(path, entries)
        return entries.get(key)


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
        entries, _ = _load_entries(path)
        _prune_stale_identity(entries, key)
        entries[key] = {"status": status, **extra}
        _write_entries(path, entries)
