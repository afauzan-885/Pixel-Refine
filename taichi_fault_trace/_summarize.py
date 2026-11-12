"""Bounded, exception-proof summaries of Python values.

Every helper in this module must never raise: the tracer runs inside
``except`` blocks where a secondary failure would hide the original fault.
"""

from __future__ import annotations

import inspect
import os
from pathlib import Path
from typing import Any

import numpy as np

_MAX_DEPTH = 3


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def _dtype_name(dtype: Any) -> str:
    try:
        return str(np.dtype(dtype).name)
    except Exception:
        return str(dtype)


def summarize_buffer(value: Any, *, limit: int = 220) -> str | None:
    """Describe bridge/graph buffers without touching device memory."""

    try:
        shape = getattr(value, "shape", None)
        dtype = getattr(value, "dtype", None)
        handle = getattr(value, "handle", None)
        if shape is None or dtype is None or handle is None:
            return None
        parts = [type(value).__name__]
        parts.append(f"dtype={_dtype_name(dtype)}")
        try:
            parts.append(f"shape={tuple(int(d) for d in shape)}")
        except Exception:
            parts.append(f"shape={shape!r}")
        nbytes = getattr(value, "nbytes", None)
        if nbytes is not None:
            parts.append(f"nbytes={int(nbytes)}")
        raw = getattr(handle, "value", handle)
        try:
            parts.append(f"handle=0x{int(raw or 0):X}")
        except Exception:
            parts.append(f"handle={raw!r}")
        if getattr(value, "_released", False):
            parts.append("released=True")
        if getattr(value, "is_vector", False):
            parts.append(f"vector_dim={getattr(value, 'vector_dim', '?')}")
        generation = getattr(value, "engine_generation", None)
        if generation is not None:
            parts.append(f"engine_generation={generation}")
        return _clip(" ".join(parts), limit)
    except Exception:
        return None


def summarize_ndarray(value: np.ndarray, *, limit: int = 220) -> str:
    parts = ["ndarray", f"dtype={value.dtype.name}", f"shape={tuple(value.shape)}"]
    try:
        parts.append("C_CONTIG" if value.flags.c_contiguous else "NON_CONTIG")
    except Exception:
        pass
    try:
        parts.append(f"nbytes={value.nbytes}")
    except Exception:
        pass
    if value.dtype.kind in "biufc" and value.size <= 4_000_000:
        try:
            if value.size:
                parts.append(f"min={float(np.nanmin(value)):.4g}")
                parts.append(f"max={float(np.nanmax(value)):.4g}")
                finite = bool(np.isfinite(value).all())
                if not finite:
                    parts.append("has_nonfinite=True")
        except Exception:
            pass
    return _clip(" ".join(parts), limit)


def summarize(value: Any, *, limit: int = 220, depth: int = 0, config=None) -> str:
    """Return a single-line, truncated description of ``value``."""

    try:
        if depth > _MAX_DEPTH:
            return "<nested>"

        if value is None or isinstance(value, (bool, int, float, complex)):
            return _clip(repr(value), limit)

        if isinstance(value, str):
            return _clip(repr(value), limit)

        if isinstance(value, (bytes, bytearray, memoryview)):
            return f"{type(value).__name__}(len={len(bytes(value))})"

        if isinstance(value, np.ndarray):
            return summarize_ndarray(value, limit=limit)

        buffer_summary = summarize_buffer(value)
        if buffer_summary is not None:
            return buffer_summary

        if isinstance(value, Path) or isinstance(value, os.PathLike):
            return _clip(f"Path({os.fspath(value)!r})", limit)

        if inspect.ismodule(value):
            return f"module({getattr(value, '__name__', '?')})"

        if inspect.isclass(value):
            return f"class({getattr(value, '__module__', '?')}.{getattr(value, '__qualname__', '?')})"

        if callable(value) and not isinstance(value, type):
            name = getattr(value, "__qualname__", None) or getattr(value, "__name__", None)
            if name:
                return f"callable({name})"

        if isinstance(value, dict):
            if not value:
                return "{}"
            items = list(value.items())[: getattr(config, "max_sequence_items", 6)]
            body = ", ".join(
                f"{summarize(k, limit=48, depth=depth + 1, config=config)}: "
                f"{summarize(v, limit=72, depth=depth + 1, config=config)}"
                for k, v in items
            )
            suffix = ", ..." if len(value) > len(items) else ""
            return _clip(f"{{{body}{suffix}}}", limit)

        if isinstance(value, (list, tuple, set, frozenset)):
            if not value:
                return repr(value)
            items = list(value)[: getattr(config, "max_sequence_items", 6)]
            body = ", ".join(summarize(v, limit=56, depth=depth + 1, config=config) for v in items)
            suffix = ", ..." if len(value) > len(items) else ""
            return _clip(f"{type(value).__name__}[{body}{suffix}]", limit)

        text = repr(value)
        return _clip(f"{type(value).__name__}({text})", limit)
    except Exception as exc:  # pragma: no cover - defensive
        return f"<unsummarizable {type(exc).__name__}>"


def summarize_mapping(mapping: dict, *, config=None, limit: int = 220) -> dict[str, str]:
    """Summarize a mapping while keeping the keys readable."""

    result: dict[str, str] = {}
    try:
        items = list(mapping.items())
    except Exception:
        return result
    for key, value in items:
        try:
            result[str(key)] = summarize(value, limit=limit, config=config)
        except Exception:
            result[str(key)] = "<error>"
    return result


def safe_len(value: Any) -> int | None:
    try:
        return len(value)
    except Exception:
        return None
