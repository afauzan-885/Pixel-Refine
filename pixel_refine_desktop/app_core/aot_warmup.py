"""
Pixel Refine - AOT & TCM Silent Background Warm-Up
===================================================
Manages background GPU runtime wake-up and pre-loading/pre-compiling of
Taichi AOT TCM modules into Host RAM.

Focused Pack Architecture:
- Pack 1 (preview catalog): the 3 preview/demosaic modules remain registered
  ("bilinear_demosaice", "hamilton", "common").
- Startup hot set: only the two modules needed for the first preview/RAW
  interaction are loaded on the critical warm-up path. ``common`` remains
  lazy and is loaded through the normal AOT API when a caller needs it.
- Pack 2 (On-Demand): Heavy multi-frame alignment and fusion modules
  ("auto_enhance", "spatial_fusion", etc.) loaded when processing begins.
- Zero VRAM Bloat: Host RAM holds module definitions and bytecode. No heavy image
  buffers (TaichiGPUBuffer) are allocated during warm-up.
"""

import os
import time
import threading
from PySide6.QtCore import QThread, QTimer, Signal, QObject

# Global worker reference to prevent GC and ensure clean shutdown
_GLOBAL_WARMUP_WORKER = None
_GLOBAL_LOCK = threading.Lock()


def _warmup_log(message: str, *, detail: bool = False) -> None:
    """Keep normal startup output useful while preserving opt-in diagnostics."""
    if detail and os.environ.get("PIXEL_REFINE_AOT_VERBOSE_LOGS", "0") != "1":
        return
    prefix = "[Taichi Vision - Detail]" if detail else "[Taichi Vision]"
    print(f"{prefix} {message}", flush=True)


def _startup_warmup_allowed() -> bool:
    """Return whether the optional startup TCM warm-up is safe to run.

    Intel OpenGL contexts are thread-affine, so creating one in this worker
    would bind the production runtime to the wrong thread. Intel Vulkan can
    warm safely when the conservative compatibility policy is active.
    """

    if os.environ.get("PIXEL_REFINE_ALLOW_INTEL_GFX_WARMUP", "0") == "1":
        return True

    backend = str(
        os.environ.get("AOT_ARCH")
        or os.environ.get("PIXEL_REFINE_AOT_ARCH")
        or ""
    ).strip().lower()
    vendor = str(
        os.environ.get("TARGET_VENDOR")
        or os.environ.get("PIXEL_REFINE_TARGET_VENDOR")
        or ""
    ).strip().lower()
    if backend == "opengl" and "intel" in vendor:
        return False
    if backend == "vulkan" and "intel" in vendor:
        try:
            from taichi_vision.vulkan_probe import intel_vulkan_is_validated

            raw_device = os.environ.get("AOT_DEVICE", "").strip()
            device_id = int(raw_device) if raw_device else None
            if intel_vulkan_is_validated(device_id):
                return True
            # Vulkan ordinals can change after a driver update.  The runtime
            # resolver will repair a stale ordinal by vendor, so accept an
            # exact current Intel manifest even when the saved ordinal moved.
            if device_id is not None and intel_vulkan_is_validated(None):
                return True
        except (ImportError, TypeError, ValueError):
            pass
        from taichi_vision.graphics_compatibility import (
            graphics_compatibility_enabled,
        )

        return graphics_compatibility_enabled(backend, vendor)
    return True

# Pack 1: Immediate interactive preview, demosaic, canvas transform, and playback
PACK_1_PREVIEW_MODULES = (
    "bilinear_demosaice",
    "hamilton",
    "common",
)

# Keep ``PACK_1_PREVIEW_MODULES``/``TIER_1_MODULES`` as the complete public
# catalog, but keep the first startup pass bounded to the two hot paths. The
# normal ``_mod`` loader remains the source of truth for deferred modules.
PACK_1_STARTUP_MODULES = (
    "bilinear_demosaice",
    "hamilton",
)

# Pack 2: Heavy multi-frame burst alignment, enhancement, and spatial fusion (on-demand)
PACK_2_ENHANCE_MODULES = (
    "auto_enhance",
    "estimate_noise",
    "spatial_fusion",
    "dcb",
    "median_filter",
    "color_convert",
    "lucas_kanade",
    "farneback_flow",
    "block_matching",
)

# Backwards compatibility aliases
TIER_1_MODULES = PACK_1_PREVIEW_MODULES
TIER_2_MODULES = PACK_2_ENHANCE_MODULES


def _get_taichi_lock():
    """Retrieve the global taichi lock safely."""
    try:
        from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import taichi_lock
        return taichi_lock
    except Exception:
        return threading.Lock()


def _resolve_tcm_directory():
    """Locate active TCM directory."""
    explicit = os.environ.get("PIXEL_REFINE_AOT_TCM_ROOT", "").strip()
    if explicit and os.path.isdir(explicit):
        return explicit

    here = os.path.dirname(os.path.abspath(__file__))
    base = os.path.abspath(os.path.join(here, "..", "..", "taichi_vision", "taichi_algorithm", "aot_tcm"))
    backend = os.environ.get("AOT_DEVICE", "vulkan").strip().lower() or "vulkan"
    sub = os.path.join(base, f"{backend}_x86_64_windows")
    if os.path.isdir(sub):
        return sub
    return base


class AOTSilentWarmupWorker(QThread):
    """Background worker that silently wakes GPU and warms up Pack 1 TCM modules into Host RAM."""

    warmup_finished = Signal(dict)

    def __init__(self, modules=None, parent=None):
        super().__init__(parent)
        self._modules = modules or PACK_1_STARTUP_MODULES
        self._stop_requested = False

    def request_stop(self):
        """Signal the thread to abort warm-up gracefully."""
        self._stop_requested = True

    def run(self):
        t0 = time.perf_counter()
        stats = {"loaded_modules": 0, "total_modules": len(self._modules), "elapsed_s": 0.0}
        taichi_lock = _get_taichi_lock()

        if self._stop_requested:
            return

        try:
            # Wake the runtime and load the preview pack in one serialized
            # session. The batch helper resolves target/root once and keeps
            # native module loading serial, while avoiding one lock round-trip
            # and one target-resolution pass per module.
            with taichi_lock:
                if self._stop_requested:
                    return
                taichi_engine = None
                try:
                    import taichi_vision.taichi_aot as taichi_aot
                    if hasattr(taichi_aot, "get_engine"):
                        taichi_engine = taichi_aot.get_engine()
                    elif hasattr(taichi_aot, "engine"):
                        taichi_engine = taichi_aot.engine
                except Exception as exc:
                    _warmup_log(
                        "Komponen awal akan dimuat saat diperlukan.",
                    )
                    _warmup_log(
                        f"Warmup engine check: {type(exc).__name__}: {exc}",
                        detail=True,
                    )

                if self._stop_requested:
                    return

                if taichi_engine is None:
                    from taichi_vision.taichi_aot import get_engine

                    taichi_engine = get_engine()
                from taichi_vision.taichi_aot.aot_module_loader import (
                    AOTModuleLoader,
                )

                batch_stats = AOTModuleLoader(taichi_engine).warmup(self._modules)
                stats["loaded_modules"] = batch_stats["loaded_modules"]
                for mod_name, exc in batch_stats.get("deferred_modules", ()):
                    _warmup_log(
                        f"Warmup module deferred: {mod_name}: {type(exc).__name__}: {exc}",
                        detail=True,
                    )

        except Exception as exc:
            _warmup_log("Komponen awal akan dimuat saat diperlukan.")
            _warmup_log(
                f"Warmup notification: {type(exc).__name__}: {exc}", detail=True
            )

        stats["elapsed_s"] = round(time.perf_counter() - t0, 3)
        if not self._stop_requested:
            if stats["loaded_modules"] == stats["total_modules"]:
                _warmup_log(
                    f"Komponen awal siap dalam {stats['elapsed_s']} dtk."
                )
            else:
                _warmup_log("Sebagian komponen akan dimuat saat diperlukan.")
            _warmup_log(
                f"Warmup: {stats['loaded_modules']}/{stats['total_modules']} modules "
                f"ready in {stats['elapsed_s']}s ({', '.join(self._modules)})",
                detail=True,
            )
            self.warmup_finished.emit(stats)


def is_silent_aot_warmup_running() -> bool:
    """True while the silent Pack 1 warm-up is still loading TCM modules.

    The warm-up holds the Taichi lock for its whole module-loading session, so
    any engine operation issued meanwhile (``sync``, pool drain) blocks until it
    finishes.  Callers that would otherwise stall the GUI thread should check
    this first and postpone their work.
    """
    worker = _GLOBAL_WARMUP_WORKER
    if worker is None:
        return False
    try:
        return bool(worker.isRunning())
    except RuntimeError:
        # The underlying C++ object can already be gone during shutdown.
        return False


def start_silent_aot_warmup(delay_ms: int = 200, parent: QObject | None = None) -> None:
    """Schedule the silent Pack 1 AOT warmup after the GUI is shown."""
    global _GLOBAL_WARMUP_WORKER

    if not _startup_warmup_allowed():
        backend = str(
            os.environ.get("AOT_ARCH")
            or os.environ.get("PIXEL_REFINE_AOT_ARCH")
            or ""
        ).strip().lower()
        vendor = str(
            os.environ.get("TARGET_VENDOR")
            or os.environ.get("PIXEL_REFINE_TARGET_VENDOR")
            or ""
        ).strip().lower()
        if backend == "opengl" and "intel" in vendor:
            message = (
                "Persiapan grafis akan dilakukan saat diperlukan untuk menjaga stabilitas Intel."
            )
        else:
            message = (
                "Persiapan grafis akan dilakukan saat diperlukan untuk menjaga stabilitas perangkat."
            )
        _warmup_log(message)
        return

    def _launch():
        global _GLOBAL_WARMUP_WORKER
        with _GLOBAL_LOCK:
            if _GLOBAL_WARMUP_WORKER is not None and _GLOBAL_WARMUP_WORKER.isRunning():
                return
            worker = AOTSilentWarmupWorker(
                modules=PACK_1_STARTUP_MODULES,
                parent=parent,
            )
            _GLOBAL_WARMUP_WORKER = worker
            # Keep warm-up below normal UI work, but avoid starving native
            # module loading indefinitely on busy systems.  The old
            # LowestPriority behavior remains an opt-in compatibility mode.
            priority = (
                QThread.Priority.LowestPriority
                if os.environ.get("PIXEL_REFINE_AOT_WARMUP_LOWEST", "0") == "1"
                else QThread.Priority.LowPriority
            )
            worker.start(priority)

    if delay_ms > 0:
        QTimer.singleShot(delay_ms, _launch)
    else:
        _launch()


def stop_silent_aot_warmup(timeout_ms: int = 1000) -> None:
    """Safely abort and wait for the warmup worker before app shutdown."""
    global _GLOBAL_WARMUP_WORKER
    with _GLOBAL_LOCK:
        worker = _GLOBAL_WARMUP_WORKER
        _GLOBAL_WARMUP_WORKER = None

    if worker is not None and worker.isRunning():
        worker.request_stop()
        worker.quit()
        worker.wait(timeout_ms)
