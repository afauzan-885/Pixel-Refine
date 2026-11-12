"""Snapshots of the native runtime, environment, and TCM artifacts.

Everything here is best-effort: resolving a handle after the engine was torn
down is expected to fail, and the tracer must still produce a report.
"""

from __future__ import annotations

import hashlib
import os
import platform
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ENV_KEYS = (
    "AOT_ARCH",
    "AOT_DEVICE",
    "AOT_ENGINE_DLL",
    "TARGET_VENDOR",
    "TI_LIB_DIR",
    "CUDA_VISIBLE_DEVICES",
    "CUDA_DEVICE",
    "BACKEND",
    "TAICHI_FAULT",
    "TAICHI_FAULT_DIR",
    "TAICHI_FAULT_EXTRA",
    "DISABLE_AOT_WATCHDOG",
)


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def environment_snapshot() -> dict[str, Any]:
    env = {key: os.environ[key] for key in _ENV_KEYS if key in os.environ}
    version = None
    try:
        import taichi  # noqa: WPS433 - intentional lazy import

        version = getattr(taichi, "__version__", None)
    except Exception:
        pass
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pid": os.getpid(),
        "thread": threading.current_thread().name,
        "thread_id": threading.get_ident(),
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "platform": f"{platform.system()} {platform.release()} {platform.machine()}",
        "cwd": _safe(os.getcwd, ""),
        "taichi_version": version,
        "env": env,
    }


def _resolve_engine(engine: Any = None) -> Any:
    if engine is not None:
        try:
            return engine._live() if hasattr(engine, "_live") else engine
        except Exception:
            return engine
    try:
        import taichi.aot_engine as aot_engine

        return aot_engine.get_engine()
    except Exception:
        return None


def _resolve_handle(engine: Any) -> Any:
    if engine is None:
        return None
    for attribute in ("handle", "runtime"):
        try:
            value = getattr(engine, attribute)
        except Exception:
            continue
        if value is not None:
            return value
    return None


def native_snapshot(engine: Any = None) -> dict[str, Any]:
    """Describe the live bridge engine, including its error slots."""

    resolved = _resolve_engine(engine)
    snapshot: dict[str, Any] = {
        "engine_type": type(resolved).__name__ if resolved is not None else None,
        "arch": _safe(lambda: getattr(resolved, "arch", None)),
        "device_id": _safe(lambda: getattr(resolved, "device_id", None)),
        "generation": _safe(lambda: getattr(resolved, "generation", None)),
        "destroyed": _safe(lambda: bool(getattr(resolved, "destroyed", False))),
        "gpu_name": _safe(lambda: getattr(resolved, "gpu_name", None)),
        "handle": None,
        "library": None,
        "last_error": None,
        "last_init_error": None,
        "context_backend": None,
        "device_name": None,
    }
    handle = _resolve_handle(resolved)
    try:
        raw = getattr(handle, "value", handle)
        snapshot["handle"] = None if raw is None else f"0x{int(raw):X}"
    except Exception:
        snapshot["handle"] = repr(handle)

    if resolved is None:
        return snapshot

    try:
        from taichi import native_bridge

        snapshot["library"] = _safe(lambda: getattr(native_bridge, "_LIB_PATH", None))
        if handle is not None:
            snapshot["last_error"] = _safe(lambda: native_bridge.last_error(handle))
            snapshot["device_name"] = _safe(lambda: native_bridge.device_name(handle))
            snapshot["context_backend"] = _safe(
                lambda: native_bridge.context_backend(handle)
            )
        lib = _safe(native_bridge.library)
        if lib is not None:
            try:
                message = lib.get_last_init_error()
                snapshot["last_init_error"] = (
                    message.decode("utf-8", "replace") if message else ""
                )
            except Exception:
                snapshot["last_init_error"] = None
    except Exception as exc:
        snapshot["bridge_probe_error"] = f"{type(exc).__name__}: {exc}"
    return snapshot


def artifact_snapshot(path: Any) -> dict[str, Any]:
    """Hash and stat one artifact so two runs can be compared reliably."""

    result: dict[str, Any] = {"path": str(path)}
    try:
        file = Path(path)
        if not file.is_file():
            result["exists"] = False
            return result
        stat = file.stat()
        result.update(
            {
                "exists": True,
                "size_bytes": stat.st_size,
                "mtime": datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).isoformat(timespec="seconds"),
                "sha256": _sha256(file),
            }
        )
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


_ARTIFACT_SUFFIXES = (".tcm", ".bundle", ".onnx", ".dll", ".so", ".dylib")


def find_artifacts(values: list[Any], *, limit: int = 8) -> list[dict[str, Any]]:
    """Collect artifact-like paths from already summarized call arguments."""

    found: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _consider(candidate: Any) -> None:
        try:
            text = os.fspath(candidate)
        except Exception:
            return
        if not isinstance(text, str):
            return
        if not text.lower().endswith(_ARTIFACT_SUFFIXES):
            return
        resolved = os.path.abspath(text)
        if resolved in seen:
            return
        seen.add(resolved)
        if len(found) < limit:
            found.append(artifact_snapshot(resolved))

    def _walk(candidate: Any, depth: int) -> None:
        if depth > 2 or len(found) >= limit:
            return
        if isinstance(candidate, (str, os.PathLike)):
            _consider(candidate)
            return
        if isinstance(candidate, dict):
            for value in candidate.values():
                _walk(value, depth + 1)
            return
        if isinstance(candidate, (list, tuple, set, frozenset)):
            for value in candidate:
                _walk(value, depth + 1)
            return
        for attribute in ("path", "artifact", "source", "model_path"):
            try:
                value = getattr(candidate, attribute, None)
            except Exception:
                continue
            if value is not None:
                _walk(value, depth + 1)

    for value in values:
        if len(found) >= limit:
            break
        _walk(value, 0)
    return found


def diagnose() -> dict[str, Any]:
    """Produce the one-call snapshot used by ``python -m taichi_fault_trace``."""

    return {
        "environment": environment_snapshot(),
        "native": native_snapshot(),
    }
