"""Lightweight performance and memory probe for the batch workflow.

The probe is inert unless ``PIXEL_REFINE_PERF_PROBE=1`` is present in the
environment, so normal runs pay only a single ``os.environ`` lookup per call
site that uses it.  Every helper here is best-effort: a probe must never raise
into application code, therefore all measurements are individually guarded and
degrade to sentinel values.

It reuses the telemetry that already exists in the codebase instead of adding a
second measurement stack:

* ``psutil`` for the GUI process RSS,
* ``BackendWorkerManager.get_worker_memory_mb`` for the isolated worker RSS,
* ``taichi_aot.get_memory_status`` / ``get_block_cache_stats`` for engine
  counters.
"""

from __future__ import annotations

import os
import time

ENV_FLAG = "PIXEL_REFINE_PERF_PROBE"

_MB = 1024.0 * 1024.0


def probe_enabled() -> bool:
    """Return True when the probe was explicitly requested via the environment."""

    try:
        # ``strip`` because a shell can hand over a trailing space (``set VAR=1 &&``
        # does exactly that in cmd), which would otherwise silently disable the
        # probe instead of failing loudly.
        return os.environ.get(ENV_FLAG, "0").strip() == "1"
    except Exception:
        return False


def gui_rss_mb() -> float:
    """Resident memory of the current (GUI) process in MB, or -1.0 if unknown."""

    try:
        import psutil

        return psutil.Process(os.getpid()).memory_info().rss / _MB
    except Exception:
        return -1.0


def worker_rss_mb() -> float:
    """Resident memory of the isolated backend worker in MB, or -1.0 if unknown."""

    try:
        from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import (
            BackendWorkerManager,
        )

        return float(BackendWorkerManager.instance().get_worker_memory_mb())
    except Exception:
        return -1.0


def engine_memory() -> dict:
    """Return the engine host-memory counters, or an empty dict when unavailable.

    Deliberately skipped while the silent TCM warm-up is running:
    ``get_memory_status`` takes the engine lifecycle lock, which the warm-up
    holds for its whole module-loading session, so sampling it there blocks the
    caller.  Since the probe runs inside the operation it measures, that stall
    would show up as the operation's own duration.
    """

    try:
        from pixel_refine_desktop.app_core.aot_warmup import (
            is_silent_aot_warmup_running,
        )

        if is_silent_aot_warmup_running():
            return {}
    except Exception:
        pass

    try:
        from taichi_vision import taichi_aot

        status = taichi_aot.get_memory_status(force=False)
        if not isinstance(status, dict):
            return {}
        return {
            "live_bytes": int(status.get("live_bytes", 0) or 0),
            "pooled_bytes": int(status.get("pooled_bytes", 0) or 0),
            "retired_bytes": int(status.get("retired_bytes", 0) or 0),
            "resident_limit": int(status.get("resident_limit", 0) or 0),
        }
    except Exception:
        return {}


def snapshot() -> dict:
    """Collect process and engine memory counters in one call."""

    data = {
        "gui_rss_mb": gui_rss_mb(),
        "worker_rss_mb": worker_rss_mb(),
    }
    data.update(engine_memory())
    return data


def _format_value(value) -> str:
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)


def format_metrics(label: str, metrics: dict) -> str:
    """Render one ``[PerfProbe]`` log line from a flat metric mapping."""

    body = " ".join(f"{key}={_format_value(val)}" for key, val in metrics.items())
    return f"[PerfProbe] label={label} {body}"


class Mark:
    """A single timed section.

    Works both as a context manager and as an explicit ``begin``/``end`` pair so
    a probe can be added to a long method without re-indenting its body::

        mark = perf_mark("load_batch", batch_id=batch_id)
        ...
        mark.end(images=len(visual_images))

    When the probe is disabled every method is a no-op.
    """

    __slots__ = ("label", "_enabled", "_started", "_fields", "_reported")

    def __init__(self, label: str, enabled: bool, fields: dict | None = None):
        self.label = label
        self._enabled = enabled
        self._started = time.perf_counter() if enabled else 0.0
        self._fields = dict(fields or {})
        self._reported = False

    def add(self, **fields) -> "Mark":
        """Attach extra fields; only the latest value of a key is kept."""

        if self._enabled:
            self._fields.update(fields)
        return self

    def end(self, **fields) -> None:
        """Emit the log line once.  Safe to call more than once."""

        if not self._enabled or self._reported:
            return
        self._reported = True
        metrics = {"ms": (time.perf_counter() - self._started) * 1000.0}
        metrics.update(snapshot())
        metrics.update(fields)
        metrics.update(self._fields)
        try:
            print(format_metrics(self.label, metrics), flush=True)
        except Exception:
            pass

    def __enter__(self) -> "Mark":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.end()
        return False


def perf_mark(label: str, **fields) -> Mark:
    """Begin a timed section.  No measurement happens unless the probe is on."""

    return Mark(label, probe_enabled(), fields)


def diagnose_panel(panel) -> dict:
    """Count the live objects a batch switch can leak or accumulate."""

    data = {}
    try:
        from PySide6.QtCore import QTimer

        data["qtimers"] = len(panel.findChildren(QTimer))
    except Exception:
        data["qtimers"] = -1

    try:
        from resources.GenericUILibrary import ImageCard

        data["image_cards"] = len(panel.findChildren(ImageCard))
    except Exception:
        data["image_cards"] = -1

    try:
        data["all_cards"] = len(getattr(panel, "all_cards", {}) or {})
    except Exception:
        data["all_cards"] = -1

    try:
        data["grid_cache"] = len(getattr(panel, "_grid_cache", {}) or {})
    except Exception:
        data["grid_cache"] = -1

    try:
        data["playback_cache"] = len(getattr(panel, "_batch_playback_cache", {}) or {})
    except Exception:
        data["playback_cache"] = -1

    try:
        processor = panel.logic.get_thumbnail_processor()
        data["ram_cache"] = len(getattr(processor, "ram_cache", {}) or {})
    except Exception:
        data["ram_cache"] = -1

    try:
        from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_processor import (
            get_global_cache,
        )

        data["global_thumb_cache"] = len(get_global_cache())
    except Exception:
        data["global_thumb_cache"] = -1

    return data


def report_panel(panel, label: str = "panel") -> dict:
    """Measure and log :func:`diagnose_panel` plus memory counters."""

    data = diagnose_panel(panel)
    if probe_enabled():
        metrics = dict(data)
        metrics.update(snapshot())
        try:
            print(format_metrics(label, metrics), flush=True)
        except Exception:
            pass
    return data
