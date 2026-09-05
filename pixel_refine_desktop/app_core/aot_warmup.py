"""
Pixel Refine - AOT & TCM Silent Background Warm-Up
===================================================
Manages background GPU runtime wake-up and pre-loading/pre-compiling of
Taichi AOT TCM modules into Host RAM.

Focused Pack Architecture:
- Pack 1 (Startup Background): Only the 3 essential preview and playback modules
  ("bilinear_demosaice", "hamilton", "common").
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
        self._modules = modules or PACK_1_PREVIEW_MODULES
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
            # 1. Wake up discrete GPU & Vulkan context under taichi_lock
            with taichi_lock:
                if self._stop_requested:
                    return
                try:
                    import taichi_vision.taichi_aot as taichi_aot
                    if hasattr(taichi_aot, "get_engine"):
                        _ = taichi_aot.get_engine()
                    elif hasattr(taichi_aot, "engine"):
                        _ = taichi_aot.engine
                except Exception as exc:
                    print(f"[AOT Warmup] GPU/Vulkan engine check: {exc}", flush=True)

            if self._stop_requested:
                return

            # 2. Warm up Pack 1 modules (Demosaic, preview, canvas)
            from taichi_vision.taichi_algorithm.aot_api import _mod

            for mod_name in self._modules:
                if self._stop_requested:
                    return
                with taichi_lock:
                    try:
                        _mod(mod_name)
                        stats["loaded_modules"] += 1
                    except Exception as exc:
                        print(f"[AOT Warmup] Module {mod_name} deferred: {exc}", flush=True)

        except Exception as exc:
            print(f"[AOT Warmup] Non-critical warmup notification: {exc}", flush=True)

        stats["elapsed_s"] = round(time.perf_counter() - t0, 3)
        if not self._stop_requested:
            print(
                f"[AOT Warmup] Pack 1 (Preview & Playback) ready in {stats['elapsed_s']}s "
                f"({stats['loaded_modules']} core modules: {', '.join(self._modules)}, VRAM load: 0MB)",
                flush=True,
            )
            self.warmup_finished.emit(stats)


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
                "[AOT Warmup] Intel OpenGL compatibility mode active; "
                "background preloading is deferred because the native context "
                "is thread-affine. Modules load on demand."
            )
        else:
            message = (
                "[AOT Warmup] Intel graphics warmup deferred by strict policy; "
                "runtime remains lazy."
            )
        print(
            message,
            flush=True,
        )
        return

    def _launch():
        global _GLOBAL_WARMUP_WORKER
        with _GLOBAL_LOCK:
            if _GLOBAL_WARMUP_WORKER is not None and _GLOBAL_WARMUP_WORKER.isRunning():
                return
            worker = AOTSilentWarmupWorker(modules=PACK_1_PREVIEW_MODULES, parent=parent)
            _GLOBAL_WARMUP_WORKER = worker
            worker.start(QThread.Priority.LowestPriority)

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
