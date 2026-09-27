"""Background GPU availability watch and recovery.

A startup enumeration can fail for transient reasons (``vulkaninfo`` needs
9-13 s on hybrid systems and times out when the machine is busy).  When that
happens the saved GPU preference is preserved instead of being rewritten to CPU,
but the session itself still has to run without the GPU.

This module closes that gap: it keeps re-probing in the background until the
saved device reappears, then lets the application recover.

What it can and cannot do:

* The isolated compute worker **can** be switched to the GPU while the
  application runs (``BackendWorkerManager.switch_backend`` is built for that:
  "0% RAM/VRAM residue", no restart).
* The main process AOT runtime **cannot**: ``AOTEngine`` loads exactly one
  backend bridge per process and keys the singleton by ``(arch, device_id)``.
  Moving preview/resident work to the GPU therefore needs an application
  restart, which is offered to the user rather than performed silently.
"""

from __future__ import annotations

import threading
import time

from PySide6.QtCore import QObject, QThread, QTimer, Signal

# Backoff between probes.  The first wait is deliberately short: the device is
# usually unavailable because the driver was still warming up during startup.
DEFAULT_BACKOFF_S = (10.0, 20.0, 40.0, 80.0, 80.0)
DEFAULT_WATCH_BUDGET_S = 300.0
DEFAULT_WORKER_SWITCH_TIMEOUT_S = 600.0

_GLOBAL_WATCH_WORKER = None
_GLOBAL_ONESHOT_WORKER = None
_GLOBAL_WATCH_LOCK = threading.Lock()


def _watch_log(message: str) -> None:
    print(f"[GPU Watch] {message}", flush=True)


class GpuAvailabilitySignals(QObject):
    """Signals for the GUI, so recovery never has to write transient state.

    Emitting a store key would persist it into ``app_setting.json``; these
    signals keep the settings file limited to real user preferences.
    """

    device_available = Signal(dict)
    watch_finished = Signal(dict)
    backend_switch_finished = Signal(bool, dict)


_GLOBAL_SIGNALS = None


def signals() -> GpuAvailabilitySignals:
    """Return the shared signals object (created on first use)."""
    global _GLOBAL_SIGNALS
    if _GLOBAL_SIGNALS is None:
        _GLOBAL_SIGNALS = GpuAvailabilitySignals()
    return _GLOBAL_SIGNALS


def _default_probe():
    """Re-enumerate from the driver (never from the short-lived cache)."""
    from taichi_vision.device_selection import scan_vulkan_device_records

    return scan_vulkan_device_records(fresh=True)


def saved_gpu_selector():
    """Return the saved GPU selector, or ``None`` when the preference is CPU.

    Read-only: this never writes to the store, so a watcher can never disturb
    the persisted preference it is trying to protect.
    """
    try:
        from pixel_refine_desktop.ui.views.settings.General.general_store import (
            get_general_store,
        )

        store = get_general_store()
    except Exception:
        return None

    arch = str(store.get("device_backend_arch") or "").strip().lower()
    vendor = str(store.get("device_vendor") or "").strip().lower()
    selector = store.get("device_selector")
    if arch in ("", "cpu") or vendor in ("", "cpu", "unknown"):
        return None
    if not isinstance(selector, dict) or not selector:
        return None
    return selector


def _resolve_saved_device(selector, records):
    """Return the record matching ``selector`` or ``None``."""
    from taichi_vision.device_selection import resolve_device_selector

    ordinal = resolve_device_selector(selector, records)
    if ordinal is None:
        return None
    for record in records:
        if int(record.get("ordinal", -1)) == int(ordinal):
            return record
    return None


class GpuWatchWorker(QThread):
    """Re-probe the driver until the saved GPU shows up again."""

    def __init__(
        self,
        selector,
        *,
        delays=None,
        budget_s=DEFAULT_WATCH_BUDGET_S,
        probe=None,
        signals_obj=None,
        parent=None,
    ):
        super().__init__(parent)
        self._selector = selector if isinstance(selector, dict) else {}
        self._delays = tuple(delays) if delays else DEFAULT_BACKOFF_S
        self._budget_s = float(budget_s)
        self._probe = probe or _default_probe
        # Injectable so a caller (or a test) can own the signal object instead
        # of attaching to the process-wide one.
        self._signals = signals_obj or signals()
        self._stop_requested = False
        self.attempts = 0

    def request_stop(self):
        self._stop_requested = True

    def _wait(self, seconds):
        """Sleep in slices so a stop request is honoured promptly."""
        deadline = time.monotonic() + max(0.0, float(seconds))
        while not self._stop_requested and time.monotonic() < deadline:
            self.msleep(50)

    def run(self):
        started = time.monotonic()
        last_error = ""
        result = {
            "found": False,
            "attempts": 0,
            "reason": "stopped",
            "device": None,
        }

        while not self._stop_requested:
            if self.attempts >= len(self._delays):
                result["reason"] = "exhausted"
                break
            if time.monotonic() - started > self._budget_s:
                result["reason"] = "budget"
                break

            self._wait(self._delays[self.attempts])
            if self._stop_requested:
                break

            self.attempts += 1
            try:
                records = self._probe()
            except Exception as exc:
                # A failed probe is not evidence of absence; keep watching.
                last_error = f"{type(exc).__name__}: {exc}"
                continue

            device = _resolve_saved_device(self._selector, records or ())
            if device is not None:
                result.update(
                    {"found": True, "reason": "available", "device": device}
                )
                self._signals.device_available.emit(dict(device))
                break

        result["attempts"] = self.attempts
        if last_error and not result["found"]:
            result["last_error"] = last_error
        _watch_log(
            f"Probe selesai: found={result['found']} attempts={result['attempts']} "
            f"reason={result['reason']}"
        )
        self._signals.watch_finished.emit(result)


def is_gpu_watch_running() -> bool:
    worker = _GLOBAL_WATCH_WORKER
    if worker is None:
        return False
    try:
        return bool(worker.isRunning())
    except RuntimeError:
        # The C++ object can already be gone during shutdown.
        return False


def start_gpu_watch(selector=None, delay_ms: int = 3000, parent=None) -> bool:
    """Start the background watch for the saved GPU.

    Returns ``False`` when there is nothing to watch (the preference is CPU) or
    a watch is already running.
    """
    global _GLOBAL_WATCH_WORKER

    target = selector if isinstance(selector, dict) else saved_gpu_selector()
    if not target:
        return False

    def _launch():
        global _GLOBAL_WATCH_WORKER
        with _GLOBAL_WATCH_LOCK:
            if _GLOBAL_WATCH_WORKER is not None and _GLOBAL_WATCH_WORKER.isRunning():
                return
            worker = GpuWatchWorker(target, parent=parent)
            _GLOBAL_WATCH_WORKER = worker
            _watch_log(
                "Memantau GPU tersimpan di latar belakang "
                f"(vendor={target.get('vendor', '?')})."
            )
            worker.start(QThread.Priority.LowPriority)

    if delay_ms > 0:
        QTimer.singleShot(delay_ms, _launch)
    else:
        _launch()
    return True


def stop_gpu_watch(timeout_ms: int = 1500) -> None:
    """Stop the watch so no thread outlives the application."""
    global _GLOBAL_WATCH_WORKER
    with _GLOBAL_WATCH_LOCK:
        worker = _GLOBAL_WATCH_WORKER
        _GLOBAL_WATCH_WORKER = None

    if worker is not None and worker.isRunning():
        worker.request_stop()
        worker.quit()
        worker.wait(timeout_ms)


def probe_saved_gpu_once(selector=None, parent=None, signals_obj=None) -> bool:
    """Run one immediate background probe (manual "retry detection").

    Results are delivered through the same signals as the automatic watch, so
    the UI has one code path for both and the GUI thread never blocks on a
    ``vulkaninfo`` spawn.
    """
    global _GLOBAL_ONESHOT_WORKER

    target = selector if isinstance(selector, dict) else saved_gpu_selector()
    if not target:
        return False
    running = _GLOBAL_ONESHOT_WORKER
    if running is not None and running.isRunning():
        return False

    worker = GpuWatchWorker(
        target, delays=(0.0,), signals_obj=signals_obj, parent=parent
    )
    _GLOBAL_ONESHOT_WORKER = worker
    worker.start(QThread.Priority.LowPriority)
    return True


def switch_worker_backend_when_idle(
    config,
    *,
    poll_s: float = 2.0,
    timeout_s: float = DEFAULT_WORKER_SWITCH_TIMEOUT_S,
    signals_obj=None,
) -> bool:
    """Switch the isolated worker to ``config`` once no task is running.

    ``switch_backend`` terminates the worker, so calling it while a batch is
    running would abort the user's job.  It also blocks until the new worker
    signals ready (up to 180 s), hence the wait happens off the GUI thread.
    """
    if not isinstance(config, dict) or not config:
        return False

    emitter = signals_obj or signals()

    def _run():
        from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import (
            BackendWorkerManager,
        )

        manager = BackendWorkerManager.instance()
        deadline = time.monotonic() + max(0.0, float(timeout_s))
        while manager.is_task_active():
            if time.monotonic() > deadline:
                _watch_log(
                    "Pemrosesan sedang berjalan; perpindahan GPU dilewati untuk "
                    "menghindari membatalkan batch."
                )
                emitter.backend_switch_finished.emit(False, dict(config))
                return
            time.sleep(min(poll_s, 1.0))
        try:
            switched = bool(manager.switch_backend(config, force_restart=True))
        except Exception as exc:
            _watch_log(f"Perpindahan worker ke GPU gagal: {exc}")
            switched = False
        emitter.backend_switch_finished.emit(switched, dict(config))

    threading.Thread(
        target=_run, daemon=True, name="GpuWatchWorkerSwitch"
    ).start()
    return True
