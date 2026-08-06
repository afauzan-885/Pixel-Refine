import ctypes
import hashlib
import json
import os
import sys
import atexit
import signal
import shutil
import struct
import tempfile
import weakref
import zipfile
import numpy as np
import typing
import threading
import time
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, Future

from .block import (
    BlockCache, BlockConfig, BlockGrid, BlockRecord, BlockState, checksum,
    is_auto_block_safe, should_use_blocks,
)
from .memory import CacheTelemetry, MemoryGovernor
from .residency import DeviceResidencyCache
from .auto_pipeline import AutoPipelinePlanner
from .capabilities import classify_device
from .artifact_cache import artifact_key, get_status, set_status
from .backend_manager import BackendManager
from taichi_library.backend_config import (
    BackendConfig,
    backend_env,
    normalize_backend,
    normalize_vendor,
    parse_device_id,
    requested_backend,
)
from taichi_library.device_selection import (
    make_device_selector,
    query_vulkan_memory_budget,
    resolve_device_selector,
    scan_vulkan_device_records,
)

_UNSET = object()
_CPU_AOT_EXTRACTION_LOCK = threading.RLock()


def _materialize_cpu_aot_directory(artifact_path):
    """Return a safe directory form of a packed CPU AOT artifact.

    Taichi 1.7.4's LLVM C runtime loads CPU AOT from a directory, while the
    graphics C runtime accepts the packed ``.tcm`` form.  Keep the package
    format uniform for callers and materialize the CPU-only directory in a
    private cache keyed by the artifact content.
    """
    artifact_path = os.path.abspath(artifact_path)
    digest = hashlib.sha256()
    with open(artifact_path, "rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)

    cache_root = os.path.join(os.path.dirname(artifact_path), ".cpu_aot_cache")
    target = os.path.join(cache_root, digest.hexdigest())
    ready_marker = os.path.join(target, "__content__")
    with _CPU_AOT_EXTRACTION_LOCK:
        if os.path.isfile(ready_marker):
            return target

        os.makedirs(cache_root, exist_ok=True)
        staging = tempfile.mkdtemp(prefix="extract-", dir=cache_root)
        try:
            staging_root = os.path.abspath(staging)
            with zipfile.ZipFile(artifact_path) as archive:
                for member in archive.infolist():
                    destination = os.path.abspath(
                        os.path.join(staging_root, member.filename)
                    )
                    if os.path.commonpath((staging_root, destination)) != staging_root:
                        raise RuntimeError(
                            f"Unsafe member in CPU AOT artifact: {member.filename!r}"
                        )
                    if member.is_dir():
                        os.makedirs(destination, exist_ok=True)
                        continue
                    os.makedirs(os.path.dirname(destination), exist_ok=True)
                    with archive.open(member) as source, open(destination, "wb") as output:
                        shutil.copyfileobj(source, output)

            if not os.path.isfile(os.path.join(staging_root, "__content__")):
                raise RuntimeError("CPU AOT artifact does not contain __content__")
            if not os.path.exists(target):
                os.rename(staging_root, target)
                staging = None
            return target
        finally:
            if staging and os.path.isdir(staging):
                shutil.rmtree(staging, ignore_errors=True)

def get_vulkan_device_name(device_id):
    # The AOT bridge and the runtime must use the same enumeration source.
    # Otherwise a UI ordinal can refer to NVIDIA in one list and Intel in a
    # separate Vulkan-loader list after a driver update.
    try:
        index = int(device_id)
        record = next(
            (
                item
                for item in scan_vulkan_device_records()
                if int(item.get("ordinal", -1)) == index
            ),
            None,
        )
        if record and record.get("name"):
            return str(record["name"])
    except Exception:
        pass
    try:
        import ctypes
        vk = ctypes.CDLL("vulkan-1.dll")
        
        class VkApplicationInfo(ctypes.Structure):
            _fields_ = [
                ("sType", ctypes.c_int),
                ("pNext", ctypes.c_void_p),
                ("pApplicationName", ctypes.c_char_p),
                ("applicationVersion", ctypes.c_uint32),
                ("pEngineName", ctypes.c_char_p),
                ("engineVersion", ctypes.c_uint32),
                ("apiVersion", ctypes.c_uint32),
            ]

        class VkInstanceCreateInfo(ctypes.Structure):
            _fields_ = [
                ("sType", ctypes.c_int),
                ("pNext", ctypes.c_void_p),
                ("flags", ctypes.c_uint32),
                ("pApplicationInfo", ctypes.POINTER(VkApplicationInfo)),
                ("enabledLayerCount", ctypes.c_uint32),
                ("ppEnabledLayerNames", ctypes.c_void_p),
                ("enabledExtensionCount", ctypes.c_uint32),
                ("ppEnabledExtensionNames", ctypes.c_void_p),
            ]

        vk.vkCreateInstance.argtypes = [ctypes.POINTER(VkInstanceCreateInfo), ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        vk.vkCreateInstance.restype = ctypes.c_int
        
        vk.vkDestroyInstance.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        vk.vkDestroyInstance.restype = None
        
        vk.vkEnumeratePhysicalDevices.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_void_p)]
        vk.vkEnumeratePhysicalDevices.restype = ctypes.c_int
        
        vk.vkGetPhysicalDeviceProperties.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        vk.vkGetPhysicalDeviceProperties.restype = None

        app_info = VkApplicationInfo(
            sType=9,
            pNext=None,
            pApplicationName=b"Query",
            applicationVersion=1,
            pEngineName=b"Query",
            engineVersion=1,
            apiVersion=0x00400000,
        )
        create_info = VkInstanceCreateInfo(
            sType=10,
            pNext=None,
            flags=0,
            pApplicationInfo=ctypes.pointer(app_info),
            enabledLayerCount=0,
            ppEnabledLayerNames=None,
            enabledExtensionCount=0,
            ppEnabledExtensionNames=None,
        )
        
        instance = ctypes.c_void_p()
        res = vk.vkCreateInstance(ctypes.pointer(create_info), None, ctypes.pointer(instance))
        if res != 0:
            return None

        count = ctypes.c_uint32(0)
        vk.vkEnumeratePhysicalDevices(instance, ctypes.pointer(count), None)
        if count.value == 0 or device_id >= count.value:
            vk.vkDestroyInstance(instance, None)
            return None

        devices = (ctypes.c_void_p * count.value)()
        vk.vkEnumeratePhysicalDevices(instance, ctypes.pointer(count), devices)

        dev = devices[device_id]
        buf = (ctypes.c_byte * 1024)()
        vk.vkGetPhysicalDeviceProperties(dev, buf)
        
        name_bytes = bytes(buf[20:276])
        null_idx = name_bytes.find(b'\x00')
        if null_idx != -1:
            name_bytes = name_bytes[:null_idx]
        name = name_bytes.decode("utf-8", errors="ignore")

        vk.vkDestroyInstance(instance, None)
        return name
    except Exception:
        return None



# -------------------------------------------------------------------------
# Auto-Destruction Configuration
# -------------------------------------------------------------------------
def _env_float(name, default):
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


_HEARTBEAT_TIMEOUT_S = _env_float("PIXEL_REFINE_HEARTBEAT_TIMEOUT", 10.0)
_OP_TIMEOUT_S = _env_float("PIXEL_REFINE_OP_TIMEOUT", 120.0)
_LOCK_CONTENTION_S = _env_float("PIXEL_REFINE_LOCK_TIMEOUT", 30.0)
_ERROR_WINDOW_S = _env_float("PIXEL_REFINE_ERROR_WINDOW", 30.0)
_ERROR_THRESHOLD = _env_int("PIXEL_REFINE_ERROR_THRESHOLD", 5)
_AUTO_DESTROY_ENABLED = os.environ.get("PIXEL_REFINE_AUTO_DESTROY", "1") != "0"
_INIT_TIMEOUT_S = _env_float("PIXEL_REFINE_INIT_TIMEOUT", 30.0)
_CLEAN_ZOMBIES = os.environ.get("PIXEL_REFINE_CLEAN_ZOMBIES", "0") == "1"
_EXPERIMENT_MODE = os.environ.get("PIXEL_REFINE_AOT_EXPERIMENT", "0") == "1"
_SUPPRESS_VULKAN_LOADER_WARNINGS = (
    os.environ.get("PIXEL_REFINE_SUPPRESS_VULKAN_LOADER_WARNINGS", "1") != "0"
)
_DEVICE_CACHE_PATH = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
    "PixelRefine",
    "aot_device_cache.txt",
)
_STDERR_REDIRECT_LOCK = threading.Lock()
_PROCESS_JOB_HANDLE = None
_PROCESS_JOB_ACTIVE = False
_QUALIFICATION_NOTICES = set()


def _intel_vulkan_probe_override():
    """Permit Intel Vulkan only inside an explicitly isolated probe process."""
    return (
        os.environ.get("PIXEL_REFINE_AOT_INTEL_PROBE") == "1"
        and os.environ.get("PIXEL_REFINE_AOT_ALLOW_UNSAFE_INTEL") == "1"
    )


def _intel_vulkan_allowed(device_id):
    """Return true only for an isolated probe or exact validated build."""
    if _intel_vulkan_probe_override():
        return True
    try:
        from taichi_library.vulkan_probe import intel_vulkan_is_validated

        return intel_vulkan_is_validated(device_id=int(device_id))
    except Exception:
        return False


def _schedule_intel_vulkan_qualification(device_id):
    """Queue full qualification after shutdown without delaying startup."""
    if _intel_vulkan_probe_override():
        return None
    try:
        from taichi_library.intel_vulkan_qualification import (
            schedule_intel_vulkan_qualification,
        )

        report = schedule_intel_vulkan_qualification(
            int(device_id), parent_pid=os.getpid()
        )
        notice_key = (
            int(device_id),
            str(report.get("key", "")),
            str(report.get("status", "")),
        )
        if notice_key not in _QUALIFICATION_NOTICES:
            _QUALIFICATION_NOTICES.add(notice_key)
            if report.get("scheduled"):
                print(
                    "[AOTEngine] Intel Vulkan qualification scheduled after "
                    "application shutdown; OpenGL remains active for this run."
                )
            elif report.get("status") == "cooldown":
                print(
                    "[AOTEngine] Intel Vulkan qualification is in retry "
                    f"cooldown: {report.get('reason', 'previous gate failed')}"
                )
        return report
    except Exception as exc:
        print(
            "[AOTEngine] Intel Vulkan auto-qualification could not be "
            f"scheduled: {type(exc).__name__}: {exc}"
        )
        return None


def _opengl_renderer_matches_vendor(renderer, expected_vendor):
    renderer = str(renderer or "").lower()
    vendor = str(expected_vendor or "").strip().lower()
    if not vendor or vendor == "unknown":
        return True
    aliases = {
        "intel": ("intel",),
        "nvidia": ("nvidia", "geforce", "quadro"),
        "amd": ("amd", "radeon", "ati"),
    }
    return any(token in renderer for token in aliases.get(vendor, (vendor,)))


def _read_cached_device_id():
    try:
        with open(_DEVICE_CACHE_PATH, "r", encoding="utf-8") as fh:
            raw = fh.read().strip()
        if not raw:
            return None
        try:
            payload = json.loads(raw)
        except (TypeError, ValueError):
            # A legacy ordinal cannot be trusted after a driver update.
            return None
        selector = payload.get("selector") if isinstance(payload, dict) else None
        if not isinstance(selector, dict):
            return None
        devices = scan_vulkan_device_records()
        return resolve_device_selector(
            selector,
            devices,
            cached_id=payload.get("cached_ordinal"),
        )
    except Exception:
        return None


def _write_cached_device_id(device_id):
    try:
        ordinal = int(device_id)
        devices = scan_vulkan_device_records()
        record = next(
            (
                item
                for item in devices
                if int(item.get("ordinal", -1)) == ordinal
            ),
            None,
        )
        if record is None:
            return
        payload = {
            "schema": 2,
            "cached_ordinal": ordinal,
            "selector": make_device_selector(record),
            "driver_version": record.get("driver_version", "unknown"),
            "driver_uuid": record.get("driver_uuid", ""),
        }
        os.makedirs(os.path.dirname(_DEVICE_CACHE_PATH), exist_ok=True)
        staging = _DEVICE_CACHE_PATH + ".tmp"
        with open(staging, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
        os.replace(staging, _DEVICE_CACHE_PATH)
    except Exception:
        pass


def enable_experiment_mode(enabled=True):
    """Enable fail-fast native-error handling for isolated AOT experiments."""
    global _EXPERIMENT_MODE
    _EXPERIMENT_MODE = bool(enabled)
    os.environ["PIXEL_REFINE_AOT_EXPERIMENT"] = "1" if enabled else "0"


def is_experiment_mode():
    return bool(_EXPERIMENT_MODE)


def _install_process_job_guard():
    """Attach this Python process to a Windows Job Object.

    Child processes spawned after this point inherit the job. If this Python
    process is killed or its console is closed, Windows closes the last job
    handle and terminates the whole process tree. This is intentionally
    best-effort and silent: some IDEs already run Python inside a job.
    """
    global _PROCESS_JOB_HANDLE, _PROCESS_JOB_ACTIVE
    if os.name != "nt" or _PROCESS_JOB_ACTIVE or _PROCESS_JOB_HANDLE:
        return

    try:
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_longlong),
                ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            ]

        class IO_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("ReadOperationCount", ctypes.c_ulonglong),
                ("WriteOperationCount", ctypes.c_ulonglong),
                ("OtherOperationCount", ctypes.c_ulonglong),
                ("ReadTransferCount", ctypes.c_ulonglong),
                ("WriteTransferCount", ctypes.c_ulonglong),
                ("OtherTransferCount", ctypes.c_ulonglong),
            ]

        class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
                ("IoInfo", IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t),
            ]

        kernel32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.SetInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            wintypes.LPVOID,
            wintypes.DWORD,
        ]
        kernel32.SetInformationJobObject.restype = wintypes.BOOL
        kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel32.GetCurrentProcess.argtypes = []
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL

        job = kernel32.CreateJobObjectW(None, None)
        if not job:
            return

        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = 0x00002000  # KILL_ON_JOB_CLOSE
        ok = kernel32.SetInformationJobObject(
            job,
            9,  # JobObjectExtendedLimitInformation
            ctypes.byref(info),
            ctypes.sizeof(info),
        )
        if not ok:
            kernel32.CloseHandle(job)
            return

        ok = kernel32.AssignProcessToJobObject(job, kernel32.GetCurrentProcess())
        if not ok:
            kernel32.CloseHandle(job)
            return

        _PROCESS_JOB_HANDLE = job
        _PROCESS_JOB_ACTIVE = True
    except Exception:
        _PROCESS_JOB_HANDLE = None
        _PROCESS_JOB_ACTIVE = False


_install_process_job_guard()


class _suppress_native_stderr:
    """Temporarily silence native stderr spam from Vulkan loader on Windows."""

    def __init__(self, enabled=True):
        self.enabled = bool(
            enabled and _SUPPRESS_VULKAN_LOADER_WARNINGS and os.name == "nt"
        )
        self._saved_fd = None
        self._null_fd = None

    def __enter__(self):
        if not self.enabled:
            return self
        _STDERR_REDIRECT_LOCK.acquire()
        try:
            sys.stderr.flush()
        except Exception:
            pass
        self._saved_fd = os.dup(2)
        self._null_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self._null_fd, 2)
        return self

    def __exit__(self, exc_type, exc, tb):
        if not self.enabled:
            return False
        try:
            try:
                sys.stderr.flush()
            except Exception:
                pass
            if self._saved_fd is not None:
                os.dup2(self._saved_fd, 2)
        finally:
            if self._null_fd is not None:
                os.close(self._null_fd)
            if self._saved_fd is not None:
                os.close(self._saved_fd)
            _STDERR_REDIRECT_LOCK.release()
        return False


def configure_auto_destroy(
    heartbeat_timeout=None,
    op_timeout=None,
    lock_timeout=None,
    error_threshold=None,
    error_window=None,
    enabled=None,
):
    """Runtime configuration override for auto-destruction system.

    Call before any GPU operations to adjust timeouts.

    Args:
        heartbeat_timeout: Max idle seconds before auto-destruction (default 60)
        op_timeout: Max seconds for a single DLL operation (default 120)
        lock_timeout: Max seconds waiting on lock before deadlock detection (default 30)
        error_threshold: Error count within error_window to trigger cleanup (default 5)
        error_window: Rolling window in seconds for error counting (default 30)
        enabled: Set False to disable all auto-destruction
    """
    global _HEARTBEAT_TIMEOUT_S, _OP_TIMEOUT_S, _LOCK_CONTENTION_S
    global _ERROR_THRESHOLD, _ERROR_WINDOW_S, _AUTO_DESTROY_ENABLED
    global _INIT_TIMEOUT_S, _CLEAN_ZOMBIES
    if heartbeat_timeout is not None:
        _HEARTBEAT_TIMEOUT_S = float(heartbeat_timeout)
    if op_timeout is not None:
        _OP_TIMEOUT_S = float(op_timeout)
    if lock_timeout is not None:
        _LOCK_CONTENTION_S = float(lock_timeout)
    if error_threshold is not None:
        _ERROR_THRESHOLD = int(error_threshold)
    if error_window is not None:
        _ERROR_WINDOW_S = float(error_window)
    if enabled is not None:
        _AUTO_DESTROY_ENABLED = bool(enabled)


# -------------------------------------------------------------------------
# Heartbeat & Operation Tracking State
# -------------------------------------------------------------------------
_heartbeat_lock = threading.Lock()
_last_activity_time = time.monotonic()  # updated on every GPU op entry/exit
_op_start_time = 0.0  # 0.0 = no operation in progress
_op_name = ""  # human-readable label for logging
_lock_wait_start = 0.0  # when a thread started waiting for _lock
_lock_wait_name = ""  # what operation is waiting for lock
_error_timestamps = []  # rolling list of time.monotonic() for circuit breaker
_vram_reclaimed = (
    False  # Track if VRAM was already cleared during the current idle session
)


def _heartbeat():
    """Record activity. Call at entry and exit of every GPU operation."""
    global _last_activity_time, _vram_reclaimed
    if not _AUTO_DESTROY_ENABLED:
        return
    with _heartbeat_lock:
        _last_activity_time = time.monotonic()
        _vram_reclaimed = False


def _op_begin(name: str):
    """Mark the start of a blocking GPU/DLL operation."""
    global _op_start_time, _op_name, _last_activity_time, _vram_reclaimed
    if not _AUTO_DESTROY_ENABLED:
        return
    with _heartbeat_lock:
        _op_start_time = time.monotonic()
        _op_name = name
        _last_activity_time = _op_start_time
        _vram_reclaimed = False


def _op_end():
    """Mark the end of a blocking GPU/DLL operation."""
    global _op_start_time, _op_name, _last_activity_time, _vram_reclaimed
    if not _AUTO_DESTROY_ENABLED:
        return
    with _heartbeat_lock:
        _op_start_time = 0.0
        _op_name = ""
        _last_activity_time = time.monotonic()
        _vram_reclaimed = False


def _lock_wait_begin(name: str):
    """Track when a thread starts blocking on engine._lock."""
    global _lock_wait_start, _lock_wait_name
    if not _AUTO_DESTROY_ENABLED:
        return
    with _heartbeat_lock:
        _lock_wait_start = time.monotonic()
        _lock_wait_name = name


def _lock_wait_end():
    """Clear lock wait tracking (called immediately after lock acquired)."""
    global _lock_wait_start, _lock_wait_name
    if not _AUTO_DESTROY_ENABLED:
        return
    with _heartbeat_lock:
        _lock_wait_start = 0.0
        _lock_wait_name = ""


def _record_error():
    """Register an error occurrence for the circuit breaker."""
    if not _AUTO_DESTROY_ENABLED:
        return
    now = time.monotonic()
    with _heartbeat_lock:
        _error_timestamps.append(now)
        # Prune old entries outside the window
        cutoff = now - _ERROR_WINDOW_S
        while _error_timestamps and _error_timestamps[0] < cutoff:
            _error_timestamps.pop(0)


# -------------------------------------------------------------------------
# Early Watchdog: started BEFORE any DLL/GPU initialization so it can
# detect and recover from hangs during AOTEngine() Vulkan init.
# -------------------------------------------------------------------------
_WATCHDOG_INTERVAL_S = 2.0  # check every 2 seconds


def _watchdog_run():
    global _last_activity_time, _vram_reclaimed
    main_thread = threading.main_thread()
    while True:
        time.sleep(_WATCHDOG_INTERVAL_S)
        if not _AUTO_DESTROY_ENABLED:
            # If auto-destroy is disabled, only check main thread liveness
            if not main_thread.is_alive():
                _global_cleanup("watchdog-main-thread-dead")
                os._exit(1)  # Hard kill when auto-destroy disabled
                break
            continue

        now = time.monotonic()

        # Snapshot all monitored state atomically under the heartbeat lock
        with _heartbeat_lock:
            activity_age = now - _last_activity_time
            op_elapsed = (now - _op_start_time) if _op_start_time > 0 else 0.0
            current_op = _op_name
            lock_wait_elapsed = (
                (now - _lock_wait_start) if _lock_wait_start > 0 else 0.0
            )
            lock_wait_op = _lock_wait_name
            recent_errors = len(_error_timestamps)

        # --- Condition 1: Main thread dead (original behavior) ---
        if not main_thread.is_alive():
            try:
                sys.stderr.write(
                    f"[AOTEngine Watchdog] Main thread is dead. "
                    f"Triggering VRAM destruction.\n"
                )
                sys.stderr.flush()
            except Exception:
                pass
            _force_global_cleanup("watchdog-main-thread-dead")
            os._exit(
                1
            )  # Hard kill: os._exit bypasses signal delivery (main thread may be dead)
            break

        # --- Condition 2: Single operation hung beyond timeout ---
        if op_elapsed > _OP_TIMEOUT_S:
            try:
                sys.stderr.write(
                    f"[AOTEngine Watchdog] Operation '{current_op}' hung for "
                    f"{op_elapsed:.1f}s (limit {_OP_TIMEOUT_S}s). "
                    f"Triggering auto-destruction.\n"
                )
                sys.stderr.flush()
            except Exception:
                pass
            _force_global_cleanup(f"op-timeout:{current_op}:{op_elapsed:.0f}s")
            os._exit(
                1
            )  # Hard kill: os._exit bypasses signal delivery (main thread may be blocked)
            break

        # --- Condition 3: Lock contention beyond timeout (deadlock detection) ---
        if lock_wait_elapsed > _LOCK_CONTENTION_S:
            try:
                sys.stderr.write(
                    f"[AOTEngine Watchdog] Lock contention in '{lock_wait_op}' for "
                    f"{lock_wait_elapsed:.1f}s (limit {_LOCK_CONTENTION_S}s). "
                    f"Triggering auto-destruction.\n"
                )
                sys.stderr.flush()
            except Exception:
                pass
            _force_global_cleanup(
                f"lock-contention:{lock_wait_op}:{lock_wait_elapsed:.0f}s"
            )
            os._exit(
                1
            )  # Hard kill: os._exit is REQUIRED here (main thread is blocked on RLock)
            break

        # --- Condition 4: Heartbeat stale (no GPU activity at all -> Idle) ---
        # When the application is idle, we don't want to shut down the application.
        # Instead, we perform a smart VRAM cleanup (clear buffer pools, collect GC) to
        # minimize VRAM footprint, while keeping the application fully alive and functional.
        # Note: We only run reclamation once per idle session (guarded by _vram_reclaimed).
        if activity_age > _HEARTBEAT_TIMEOUT_S and op_elapsed == 0.0:
            if not _vram_reclaimed:
                try:
                    sys.stderr.write(
                        f"[AOTEngine Watchdog] No GPU activity for {activity_age:.1f}s "
                        f"(limit {_HEARTBEAT_TIMEOUT_S}s). Triggering smart VRAM reclamation.\n"
                    )
                    sys.stderr.flush()
                except Exception:
                    pass

                # Smart VRAM reclamation logic:
                try:
                    # Obtain the global engine instance if it exists and clear its pools
                    for key, inst in list(AOTEngine._instances.items()):
                        with inst._lock:
                            # 1. Clear cached staging buffers
                            for entries in list(
                                getattr(inst, "_staging_pool", {}).values()
                            ):
                                for entry in entries:
                                    buf = entry.get("buffer")
                                    if buf and buf.handle is not None and buf.is_owner:
                                        try:
                                            _LIB.free_gpu_buffer(
                                                inst.runtime, buf.handle
                                            )
                                            buf.handle = None
                                            buf.is_owner = False
                                        except Exception:
                                            pass
                            inst._staging_pool = {}

                            # 2. Clear buffer pool
                            inst.buffer_pool.clear()

                    # 3. Trigger Python garbage collection to free unreferenced wrappers
                    import gc as _gc

                    _gc.collect()
                except Exception as e:
                    try:
                        sys.stderr.write(
                            f"[AOTEngine Watchdog] Smart VRAM reclamation error: {e}\n"
                        )
                        sys.stderr.flush()
                    except Exception:
                        pass

                # Mark VRAM as reclaimed for the current idle session
                with _heartbeat_lock:
                    _vram_reclaimed = True

            # Reset heartbeat timer so we don't spin-poll the check
            with _heartbeat_lock:
                _last_activity_time = now
            continue

        # --- Condition 5: Error circuit breaker ---
        if recent_errors >= _ERROR_THRESHOLD:
            try:
                sys.stderr.write(
                    f"[AOTEngine Watchdog] {recent_errors} errors within "
                    f"{_ERROR_WINDOW_S}s window (threshold {_ERROR_THRESHOLD}). "
                    f"Triggering auto-destruction.\n"
                )
                sys.stderr.flush()
            except Exception:
                pass
            _force_global_cleanup(f"error-breaker:{recent_errors}-errors")
            os._exit(1)  # Hard kill: os._exit bypasses signal delivery
            break


_watchdog = threading.Thread(
    target=_watchdog_run, name="AOTEngine-GPU-Watchdog", daemon=True
)
_watchdog.start()

# -------------------------------------------------------------------------
# OpenCV-style Constants for Standardization
# -------------------------------------------------------------------------
INTER_NEAREST = 0
INTER_LINEAR = 1
INTER_CUBIC = 2
INTER_AREA = 3

COLOR_BGR2GRAY = 6
COLOR_RGB2GRAY = 7
COLOR_GRAY2BGR = 8


# -------------------------------------------------------------------------
# Dynamic Argument Structure for C++ Engine
# -------------------------------------------------------------------------
class DynamicArg(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("arg_type", ctypes.c_int),  # 0: ndarray, 1: scalar
        ("dtype", ctypes.c_int),  # 0: f32, 1: i32, 2: u8, 3: u16
        ("dim_count", ctypes.c_int),
        ("shape", ctypes.c_int * 8),
        ("elem_dim_count", ctypes.c_int),
        ("elem_shape", ctypes.c_int * 8),
        ("is_vector", ctypes.c_int),
        ("vector_dim", ctypes.c_int),
        ("val_u64", ctypes.c_uint64),
    ]


dtype_map = {
    np.float32: 0,
    np.int32: 1,
    np.uint8: 2,
    np.uint16: 3,
    np.float64: 0,  # Fallback
}


# -------------------------------------------------------------------------
# Dynamic Argument Population Helper
# -------------------------------------------------------------------------
def _populate_dynamic_arg(arg: DynamicArg, name_bytes, value, context_name="Unknown"):
    """Internal helper to fill DynamicArg metadata consistently."""
    arg.name = name_bytes

    if isinstance(value, (int, np.integer)):
        arg.arg_type = 1
        arg.dtype = 1  # i32
        arg.val_u64 = int(value)
    elif isinstance(value, (float, np.floating)):
        arg.arg_type = 1
        arg.dtype = 0  # f32
        # DynamicArg stores scalars in a 64-bit transport slot, while the C++
        # bridge consumes the low 32 bits for TI_ARGUMENT_TYPE_F32. Reading a
        # uint64 through a pointer to c_float used to overread four bytes of
        # unrelated memory, causing nondeterministic scalar AOT dispatches.
        arg.val_u64 = struct.unpack("<I", struct.pack("<f", float(value)))[0]
    elif isinstance(value, (TaichiGPUBuffer, TaichiPlaceholder)):
        arg.arg_type = 0

        # Strict Metadata Alignment for AOT
        is_vec = getattr(value, "is_vector", False)
        v_dim = getattr(value, "vector_dim", 1)

        val_dtype = value.dtype if hasattr(value, "dtype") else np.float32
        if hasattr(val_dtype, "type"):
            val_dtype = val_dtype.type
        arg.dtype = dtype_map.get(val_dtype, 0)
        arg.is_vector = 1 if is_vec else 0
        arg.vector_dim = v_dim

        shape = value.shape
        dim_count = len(shape)

        if is_vec:
            # Vector field: Distinguish between spatial and vector components
            if dim_count >= 2 and shape[-1] == v_dim:
                # Shape explicitly includes vector dim (e.g. H, W, 3) -> Strip it for Taichi
                arg.dim_count = dim_count - 1
                for d in range(dim_count - 1):
                    arg.shape[d] = shape[d]
                arg.elem_dim_count = 1
                arg.elem_shape[0] = v_dim
            else:
                # Shape is implicitly a grid of vectors (e.g. gn, gm, gl containing vec2)
                arg.dim_count = dim_count
                for d in range(dim_count):
                    arg.shape[d] = shape[d]
                arg.elem_dim_count = 1
                arg.elem_shape[0] = v_dim
        else:
            # Scalar field
            arg.dim_count = dim_count
            for d in range(dim_count):
                arg.shape[d] = shape[d]
            arg.elem_dim_count = 0

        arg.val_u64 = ctypes.c_uint64(value.handle)
    else:
        # Backward compatibility for direct Taichi NDArrays (if any)
        if hasattr(value, "ptr"):
            arg.arg_type = 0
            arg.val_u64 = value.ptr
            arg.dtype = 0  # Assume f32
            arg.dim_count = len(value.shape)
            for d, s in enumerate(value.shape):
                arg.shape[d] = s
            arg.elem_dim_count = 0
        else:
            name_str = (
                name_bytes.decode("utf-8")
                if isinstance(name_bytes, bytes)
                else str(name_bytes)
            )
            raise TypeError(
                f"\n[AOTEngine Error] {context_name}: Unsupported object type for argument '{name_str}'.\n"
                f"  EXPECTED: TaichiGPUBuffer, TaichiPlaceholder, int, or float.\n"
                f"  ACTUAL  : {type(value)}\n"
                f"  HINT    : If using NumPy, ensure you upload it via 'InputArray(data)' first."
            )


# -------------------------------------------------------------------------
# Global State
# -------------------------------------------------------------------------
_LIB = None
_RUNTIME = None


def _init_aot_bridge(backend=None):
    global _LIB, _RUNTIME
    if _LIB is not None:
        return

    # Suppress loader registry warnings on Windows before Vulkan DLL gets loaded
    os.environ["VK_LOADER_DEBUG"] = "error"
    if os.name == "nt":
        try:
            # Force setting the environment variable directly into the Windows CRT process environment block
            # This ensures that compiled C++ modules loaded via ctypes/LoadLibrary also inherit it.
            ctypes.CDLL("msvcrt.dll")._putenv(b"VK_LOADER_DEBUG=error")
        except Exception:
            pass

    script_dir = os.path.dirname(os.path.abspath(__file__))
    aot_dll_dir = os.path.abspath(
        os.path.join(script_dir, "../taichi_algorithm/aot_py/aot_dll")
    )
    # The bridge is only loaded after AOTEngine has resolved a concrete
    # backend.  Keep this guard as a final safety net for legacy callers that
    # still invoke the private helper directly.
    backend = normalize_backend(
        backend if backend is not None else os.environ.get("PIXEL_REFINE_AOT_ARCH", "vulkan"),
        allow_auto=True,
        strict=True,
    )
    if backend == "auto":
        backend = select_backend()
    backend_dir = os.path.join(aot_dll_dir, backend)
    renderer_bridge = os.path.join(backend_dir, "taichi_aot_engine_renderer.dll")
    default_bridge = (
        renderer_bridge
        if backend == "opengl" and os.path.exists(renderer_bridge)
        else os.path.join(backend_dir, "taichi_aot_engine.dll")
    )
    engine_dll_path = os.environ.get(
        "PIXEL_REFINE_AOT_ENGINE_DLL",
        default_bridge
        if os.path.exists(default_bridge)
        else os.path.join(aot_dll_dir, "taichi_aot_engine.dll"),
    )
    engine_dll_path = os.path.abspath(engine_dll_path)

    if os.name == "nt" and os.path.exists(aot_dll_dir):
        if os.path.exists(backend_dir):
            # Backend-specific runtime must precede the shared directory:
            # Vulkan bridge builds are ABI-coupled to their matching
            # taichi_c_api.dll (a stale global DLL can corrupt the stack).
            os.add_dll_directory(backend_dir)
        os.add_dll_directory(aot_dll_dir)

        # Add Taichi runtime bin for DLL resolution without importing it (avoid printing banner/startup JIT check)
        try:
            import importlib.util

            spec = importlib.util.find_spec("taichi")
            if spec is not None and spec.origin is not None:
                ti_root = os.path.dirname(spec.origin)
                ti_bin = os.path.join(ti_root, "_lib", "c_api", "bin")
                if os.path.exists(ti_bin):
                    os.add_dll_directory(ti_bin)

                # CRITICAL: Set TI_LIB_DIR for the C++ Engine to find SPIR-V/CUDA runtimes
                ti_runtime = os.path.join(ti_root, "_lib", "runtime")
                if os.path.exists(ti_runtime):
                    os.environ["TI_LIB_DIR"] = ti_runtime
        except:
            pass

    try:
        _LIB = ctypes.CDLL(engine_dll_path)
        print(
            f"[AOTEngine] Successfully loaded backend bridge: {engine_dll_path}"
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to load Generic AOT Engine DLL at {engine_dll_path}\nError: {e}"
        )

    # Setup C-API Function Prototypes
    _LIB.init_aot_engine.argtypes = [ctypes.c_int, ctypes.c_int]
    _LIB.init_aot_engine.restype = ctypes.c_void_p

    try:
        _LIB.destroy_aot_engine.argtypes = [ctypes.c_void_p]
        _LIB.destroy_aot_engine.restype = None
    except AttributeError:
        pass

    try:
        _LIB.get_last_engine_error.argtypes = [ctypes.c_void_p]
        _LIB.get_last_engine_error.restype = ctypes.c_char_p
        _LIB.clear_last_engine_error.argtypes = [ctypes.c_void_p]
        _LIB.clear_last_engine_error.restype = None
    except AttributeError:
        pass

    try:
        _LIB.get_runtime_device_name.argtypes = [ctypes.c_void_p]
        _LIB.get_runtime_device_name.restype = ctypes.c_char_p
    except AttributeError:
        pass

    try:
        _LIB.get_runtime_context_backend.argtypes = [ctypes.c_void_p]
        _LIB.get_runtime_context_backend.restype = ctypes.c_char_p
    except AttributeError:
        pass

    try:
        _LIB.get_last_init_error.argtypes = []
        _LIB.get_last_init_error.restype = ctypes.c_char_p
    except AttributeError:
        pass

    _LIB.scan_vulkan_devices.argtypes = []
    _LIB.scan_vulkan_devices.restype = ctypes.c_char_p

    _LIB.load_aot_module.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    _LIB.load_aot_module.restype = ctypes.c_void_p

    _LIB.destroy_aot_module.argtypes = [ctypes.c_void_p]
    _LIB.destroy_aot_module.restype = None

    _LIB.allocate_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_int]
    _LIB.allocate_gpu_buffer.restype = ctypes.c_void_p

    _LIB.free_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _LIB.free_gpu_buffer.restype = None

    _LIB.write_to_gpu_buffer.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint64,
    ]
    _LIB.write_to_gpu_buffer.restype = None

    _LIB.read_from_gpu_buffer.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint64,
    ]
    _LIB.read_from_gpu_buffer.restype = None

    _LIB.map_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _LIB.map_gpu_buffer.restype = ctypes.c_void_p

    _LIB.unmap_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _LIB.unmap_gpu_buffer.restype = None

    _LIB.copy_gpu_buffer.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint64,
    ]
    _LIB.copy_gpu_buffer.restype = None

    _LIB.run_aot_graph.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.POINTER(DynamicArg),
        ctypes.c_int,
    ]
    _LIB.run_aot_graph.restype = None

    _LIB.sync_runtime.argtypes = [ctypes.c_void_p]
    _LIB.sync_runtime.restype = None

    _LIB.clear_pipeline.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    _LIB.clear_pipeline.restype = None

    _LIB.add_to_pipeline.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.POINTER(DynamicArg),
        ctypes.c_int,
    ]
    _LIB.add_to_pipeline.restype = None

    _LIB.run_pipeline.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(DynamicArg),
        ctypes.c_int,
    ]
    _LIB.run_pipeline.restype = None

    _LIB.ti_imread_to_gpu.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    _LIB.ti_imread_to_gpu.restype = ctypes.c_void_p

    _LIB.ti_imwrite_from_gpu.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
    ]
    _LIB.ti_imwrite_from_gpu.restype = ctypes.c_bool

    _LIB.ti_cast_buffer.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
    ]
    _LIB.ti_cast_buffer.restype = ctypes.c_bool


def _scan_native_vulkan_device(preferred_vendor=None):
    """Return a native Vulkan ordinal, preferring the requested vendor."""

    try:
        records = scan_vulkan_device_records()
    except Exception:
        return None

    preferred = normalize_vendor(preferred_vendor)
    fallback = None
    skip_translation = os.environ.get("PIXEL_REFINE_AOT_SKIP_DOZEN", "1") == "1"
    for record in records:
        name = str(record.get("name", ""))
        if skip_translation and (
            record.get("translation")
            or "dozen" in name.lower()
            or "direct3d12" in name.lower()
        ):
            continue
        if not record.get("native", not record.get("translation", False)):
            continue
        ordinal = parse_device_id(record.get("ordinal"))
        if ordinal is None:
            continue
        vendor = normalize_vendor(record.get("vendor") or name)
        if preferred != "unknown" and vendor == preferred:
            return ordinal
        if fallback is None and vendor in {"nvidia", "intel", "amd"}:
            fallback = ordinal
    return fallback


def select_backend(prefer=None, device_id=None):
    """Select one canonical backend for automatic mode.

    Explicit AOT settings remain strict and are never silently rerouted.  In
    automatic mode the existing capability manager decides the preference,
    while translation (Dozen/D3D12) adapters are excluded from the probe.
    """

    requested, explicit, _source = requested_backend(prefer=prefer)
    if requested != "auto":
        return requested

    probe_id = parse_device_id(
        device_id,
        parse_device_id(os.environ.get("PIXEL_REFINE_AOT_DEFAULT_DEVICE"), 0),
    )
    if probe_id is None:
        probe_id = 0
    name = get_vulkan_device_name(probe_id) or "unknown"
    selected = BackendManager(name).decide("auto").selected
    if (
        "intel" in name.lower()
        and selected != "vulkan"
        and not _intel_vulkan_allowed(probe_id)
    ):
        _schedule_intel_vulkan_qualification(probe_id)
    return normalize_backend(selected, allow_auto=False, strict=True)


def resolve_backend_config(arch=None, device_id=None, *, prefer=None, strict=None):
    """Resolve the complete backend/device contract before native init.

    Device ordinals have different namespaces: Vulkan ordinals come from the
    Vulkan loader, CUDA ordinals come from CUDA, and OpenGL is selected by the
    Windows native ICD/context.  This function keeps those namespaces
    separate, preventing a driver reorder from mapping NVIDIA to Intel (or a
    Vulkan ordinal from being accidentally passed to CUDA).
    """

    requested, explicit, source = requested_backend(prefer=prefer, arch=arch)
    if strict is None:
        strict = explicit
    if requested == "auto":
        backend = select_backend(device_id=device_id)
        source = "automatic"
    else:
        backend = requested

    backend = normalize_backend(backend, allow_auto=False, strict=True)
    requested_id = parse_device_id(device_id)
    env_id = parse_device_id(os.environ.get("PIXEL_REFINE_AOT_DEVICE"))

    if backend == "cpu":
        ordinal = 0
        name = "CPU (x86_64 Windows)"
        vendor = "cpu"
    elif backend == "opengl":
        # OpenGL's native ICD chooses the adapter through the process/context;
        # the bridge exposes one logical device.  Keep vendor/name expectations
        # for the post-init renderer check instead of treating this as a
        # Vulkan ordinal.
        ordinal = 0
        name = os.environ.get("PIXEL_REFINE_OPENGL_EXPECTED_NAME", "")
        vendor = normalize_vendor(
            os.environ.get("PIXEL_REFINE_OPENGL_EXPECTED_VENDOR", "")
            or name
        )
    elif backend == "cuda":
        # CUDA ordinals are independent of Vulkan ordinals.  Prefer the
        # dedicated CUDA setting, then the generic setting for compatibility,
        # and finally CUDA device 0.
        ordinal = requested_id
        if ordinal is None:
            ordinal = parse_device_id(os.environ.get("PIXEL_REFINE_CUDA_DEVICE"))
        if ordinal is None:
            ordinal = env_id if env_id is not None else 0
        name = os.environ.get("PIXEL_REFINE_CUDA_EXPECTED_NAME", "")
        vendor = "nvidia"
    else:  # Vulkan
        ordinal = requested_id if requested_id is not None else env_id
        if ordinal is None:
            ordinal = _read_cached_device_id()
        if ordinal is None:
            ordinal = parse_device_id(
                os.environ.get("PIXEL_REFINE_AOT_DEFAULT_DEVICE"), 0
            ) or 0
            # Automatic/default Vulkan selection prefers a native NVIDIA
            # adapter, then native Intel/AMD, never Dozen.
            if (
                os.environ.get("PIXEL_REFINE_AOT_AUTOSCAN", "1") == "1"
                and (not explicit or requested_id is None)
            ):
                scanned = _scan_native_vulkan_device()
                if scanned is not None:
                    ordinal = scanned
        name = get_vulkan_device_name(ordinal) or ""
        vendor = normalize_vendor(name)

    config = BackendConfig(
        backend=backend,
        device_id=ordinal,
        vendor=vendor,
        device_name=name,
        explicit=explicit,
        source=source,
        strict=bool(strict),
    )
    # Keep child processes and old callers in sync with the canonical values.
    os.environ.update(backend_env(config))
    return config


def configure_taichi_backend(prefer: str = None, device_memory_GB: float = None):
    """
    Helper to initialize Taichi runtime consistently across the project.
    - prefer: 'vulkan', 'cuda', 'gpu', or 'cpu'. If None, reads
      PIXEL_REFINE_TAICHI_ARCH env var, otherwise auto-selects.
    - device_memory_GB: optional device memory hint forwarded to `ti.init`.

    This function imports Taichi lazily and calls `ti.init(...)`.
    Use this from scripts before invoking any Taichi kernels.
    """
    try:
        import taichi as ti
    except Exception:
        raise RuntimeError("Taichi is not installed or cannot be imported.")

    env_pref = os.environ.get("PIXEL_REFINE_TAICHI_ARCH")
    raw_choice = prefer or env_pref or os.environ.get("PIXEL_REFINE_AOT_ARCH")
    arch_choice = normalize_backend(raw_choice, allow_auto=True, strict=raw_choice not in (None, "", "auto"))
    if arch_choice == "auto":
        arch_choice = select_backend()
    # TEMPORARILY DISABLED: Intel Vulkan automatic reroute/quarantine.
    # The General Settings compatibility matrix must expose and exercise the
    # native Intel Vulkan path explicitly. Retain this policy as comments for
    # a quick rollback if a driver regression is confirmed.
    # if arch_choice == "vulkan":
    #     _device_name = get_vulkan_device_name(
    #         int(os.environ.get("PIXEL_REFINE_AOT_DEVICE", 0))
    #     ) or ""
    #     if (
    #         "intel" in _device_name.lower()
    #         and not _intel_vulkan_allowed(
    #             int(os.environ.get("PIXEL_REFINE_AOT_DEVICE", 0))
    #         )
    #         and not explicit_backend
    #     ):
    #         _schedule_intel_vulkan_qualification(
    #             int(os.environ.get("PIXEL_REFINE_AOT_DEVICE", 0))
    #         )
    #         print("[engine.configure_taichi_backend] Intel Vulkan quarantined; using opengl")
    #         arch_choice = "opengl"

    # Map string to taichi arch constant
    arch_map = {
        "vulkan": getattr(ti, "vulkan", getattr(ti, "gpu", None)),
        "opengl": getattr(ti, "opengl", None),
        "cuda": getattr(ti, "cuda", None),
        "cpu": getattr(ti, "cpu", None),
    }

    arch = arch_map.get(arch_choice, None)
    if arch is None:
        arch = getattr(ti, "vulkan", getattr(ti, "gpu", ti.cpu))

    init_kwargs = {"default_fp": ti.f32}
    if device_memory_GB is not None:
        init_kwargs["device_memory_GB"] = device_memory_GB

    # Provide a friendly log
    print(
        f"[engine.configure_taichi_backend] Initializing Taichi with arch={arch_choice}"
    )
    ti.init(arch=arch, **init_kwargs)


def _get_native_engine_error(runtime):
    if not _LIB or not runtime:
        return ""
    try:
        getter = getattr(_LIB, "get_last_engine_error")
    except AttributeError:
        return ""
    try:
        raw = getter(runtime)
        if not raw:
            return ""
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="replace")
        return str(raw)
    except Exception:
        return ""


def _get_runtime_device_name(runtime):
    if not _LIB or not runtime:
        return ""
    try:
        getter = _LIB.get_runtime_device_name
        raw = getter(runtime)
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="replace").strip()
        return str(raw or "").strip()
    except (AttributeError, OSError, TypeError):
        return ""


def _get_runtime_context_backend(runtime):
    if not _LIB or not runtime:
        return ""
    try:
        raw = _LIB.get_runtime_context_backend(runtime)
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="replace").strip()
        return str(raw or "").strip()
    except (AttributeError, OSError, TypeError):
        return ""


def _get_last_init_error():
    if not _LIB:
        return ""
    try:
        raw = _LIB.get_last_init_error()
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="replace").strip()
        return str(raw or "").strip()
    except (AttributeError, OSError, TypeError):
        return ""


def _clear_native_engine_error(runtime):
    if not _LIB or not runtime:
        return
    try:
        clearer = getattr(_LIB, "clear_last_engine_error")
    except AttributeError:
        return
    try:
        clearer(runtime)
    except Exception:
        pass


def _raise_native_engine_error(runtime, context):
    message = _get_native_engine_error(runtime)
    if message:
        _clear_native_engine_error(runtime)
        _record_error()
        if _EXPERIMENT_MODE:
            try:
                sys.stderr.write(
                    f"[AOTEngine Experiment] Fatal native error in {context}: {message}\n"
                )
                sys.stderr.flush()
            except Exception:
                pass
            try:
                _global_cleanup("experiment-native-error", force=True)
            except Exception:
                pass
            os._exit(86)
        raise RuntimeError(f"[AOTEngine Native Error] {context}: {message}")


# -------------------------------------------------------------------------
# GPU Buffer Manager
# -------------------------------------------------------------------------
class BufferPool:
    """Lightweight pool: tracks handles for potential reuse by exact size match."""

    def __init__(self, engine=None):
        self.engine = engine
        self.free_buffers = {}  # size -> list of handles
        self.max_bytes = 0
        self.pooled_bytes = 0
        import threading

        self._lock = threading.Lock()

    def acquire(self, size):
        with self._lock:
            if size in self.free_buffers and self.free_buffers[size]:
                handle = self.free_buffers[size].pop()
                self.pooled_bytes = max(0, self.pooled_bytes - int(size))
                if not self.free_buffers[size]:
                    self.free_buffers.pop(size, None)
                return handle
            return None

    def store(self, size, handle):
        """Store a handle for reuse (caller decides if reuse or free)."""
        with self._lock:
            size = int(size)
            if self.max_bytes <= 0 or self.pooled_bytes + size > self.max_bytes:
                runtime = self.engine.runtime if self.engine else _RUNTIME
                if _LIB and runtime:
                    _LIB.free_gpu_buffer(runtime, handle)
                return
            if size not in self.free_buffers:
                self.free_buffers[size] = []
            self.free_buffers[size].append(handle)
            self.pooled_bytes += size

    def set_budget(self, max_bytes):
        """Apply an adaptive cap and evict largest idle buffers first."""
        with self._lock:
            self.max_bytes = max(0, int(max_bytes))
            runtime = self.engine.runtime if self.engine else _RUNTIME
            for size in sorted(tuple(self.free_buffers), reverse=True):
                handles = self.free_buffers.get(size, [])
                while handles and self.pooled_bytes > self.max_bytes:
                    handle = handles.pop()
                    if _LIB and runtime:
                        _LIB.free_gpu_buffer(runtime, handle)
                    self.pooled_bytes = max(0, self.pooled_bytes - int(size))
                if not handles:
                    self.free_buffers.pop(size, None)

    def clear(self):
        """Force-free all pooled handles from VRAM."""
        global _LIB, _RUNTIME
        with self._lock:
            runtime = self.engine.runtime if self.engine else _RUNTIME
            if _LIB and runtime:
                for handles in self.free_buffers.values():
                    for h in handles:
                        _LIB.free_gpu_buffer(runtime, h)
            self.free_buffers = {}
            self.pooled_bytes = 0


class TaichiGPUBuffer:
    def __init__(
        self,
        size_bytes,
        handle,
        shape,
        dtype=np.float32,
        is_vector=False,
        engine=None,
        is_owner=True,
        host_accessible=False,
        vector_dim=3,
    ):
        self.size_bytes = size_bytes
        self.handle = handle
        self.shape = shape
        self.dtype = dtype
        self.is_vector = is_vector
        self.vector_dim = vector_dim
        self.engine = engine
        self.is_owner = is_owner
        self.host_accessible = host_accessible
        self.associated_pipelines = set()

    def release(self):
        """Release the buffer back to the engine's buffer pool for reuse."""
        if self.handle is not None and self.is_owner:
            if self.engine and self.engine.current_pipeline:
                # Bypass/protect buffers during recording to prevent use-after-free
                if getattr(self, "is_pipeline_intermediate", False) or (
                    self.engine.current_pipeline in self.associated_pipelines
                ):
                    return

            if self.engine and not self.host_accessible:
                self.engine.buffer_pool.store(self.size_bytes, self.handle)
                self.handle = None
                self.is_owner = False
            else:
                self.destroy()

    def destroy(self):
        """Immediately release GPU VRAM. Does NOT use buffer pool reuse."""
        _heartbeat()
        if self.handle is not None and self.is_owner:
            # Bypass/protect buffers during recording to prevent use-after-free
            if self.engine and self.engine.current_pipeline:
                if getattr(self, "is_pipeline_intermediate", False) or (
                    self.engine.current_pipeline in self.associated_pipelines
                ):
                    return

            # Auto-clear associated pipelines: if buffer is destroyed outside of recording,
            # automatically clear the pipeline to prevent memory accesses to freed handles.
            if self.associated_pipelines:
                pipelines_to_clear = list(self.associated_pipelines)
                self.associated_pipelines.clear()
                if self.engine:
                    for pipe_name in pipelines_to_clear:
                        self.engine.clear_pipeline_by_name(pipe_name)

            global _LIB, _RUNTIME
            runtime = self.engine.runtime if self.engine else _RUNTIME
            if _LIB and runtime:
                if self.engine and hasattr(self.engine, "_lock"):
                    with self.engine._lock:
                        _LIB.free_gpu_buffer(runtime, self.handle)
                else:
                    _LIB.free_gpu_buffer(runtime, self.handle)
            self.handle = None
            self.is_owner = False

    def _force_destroy(self):
        """Force release GPU VRAM regardless of pipeline intermediate status."""
        self.is_pipeline_intermediate = False
        self.associated_pipelines.clear()
        self.destroy()

    def __del__(self):
        self.destroy()

    @property
    def ndim(self):
        return len(self.shape)

    @property
    def nbytes(self):
        return self.size_bytes

    def to_numpy(self, out=None):
        """Read GPU data. Automatically handles staging for VRAM-only buffers."""
        _heartbeat()
        if out is None:
            out = np.empty(self.shape, dtype=self.dtype)
        elif out.shape != self.shape or out.dtype != self.dtype:
            raise ValueError(
                f"Output array must have shape={self.shape} dtype={self.dtype}, "
                f"got shape={out.shape} dtype={out.dtype}"
            )
        runtime = self.engine.runtime if self.engine else _RUNTIME
        engine = self.engine
        if engine and hasattr(engine, "_lock"):
            _lock_wait_begin("to_numpy")
            with engine._lock:
                _lock_wait_end()
                if self.host_accessible:
                    _op_begin("read_from_gpu_buffer")
                    try:
                        _LIB.read_from_gpu_buffer(
                            runtime, self.handle, out.ctypes.data, self.size_bytes
                        )
                    except Exception:
                        _record_error()
                        raise
                    finally:
                        _op_end()
                else:
                    staging = engine.acquire_staging_buffer(self.shape, self.dtype)
                    try:
                        _op_begin("copy+read_gpu_buffer")
                        try:
                            _LIB.copy_gpu_buffer(
                                runtime, self.handle, staging.handle, self.size_bytes
                            )
                            _LIB.read_from_gpu_buffer(
                                runtime,
                                staging.handle,
                                out.ctypes.data,
                                self.size_bytes,
                            )
                        except Exception:
                            _record_error()
                            raise
                        finally:
                            _op_end()
                    finally:
                        engine.release_staging_buffer(staging)
        else:
            if self.host_accessible:
                _op_begin("read_from_gpu_buffer")
                try:
                    _LIB.read_from_gpu_buffer(
                        runtime, self.handle, out.ctypes.data, self.size_bytes
                    )
                except Exception:
                    _record_error()
                    raise
                finally:
                    _op_end()
            else:
                raise RuntimeError("VRAM-only read requires engine for staging.")
        return out

    def map(self):
        runtime = self.engine.runtime if self.engine else _RUNTIME
        if self.engine and hasattr(self.engine, "_lock"):
            with self.engine._lock:
                return _LIB.map_gpu_buffer(runtime, self.handle)
        return _LIB.map_gpu_buffer(runtime, self.handle)

    def unmap(self):
        runtime = self.engine.runtime if self.engine else _RUNTIME
        if self.engine and hasattr(self.engine, "_lock"):
            with self.engine._lock:
                _LIB.unmap_gpu_buffer(runtime, self.handle)
        else:
            _LIB.unmap_gpu_buffer(runtime, self.handle)

    def cast(self, target_dtype, host_accessible=False):
        self_dtype_type = np.dtype(self.dtype).type
        target_dtype_type = np.dtype(target_dtype).type
        if self_dtype_type == target_dtype_type:
            return self
        dtype_map = {np.float32: 0, np.int32: 1, np.uint8: 2, np.uint16: 3}
        if (
            self_dtype_type not in dtype_map
            or target_dtype_type not in dtype_map
            or not self.host_accessible
            or not host_accessible
        ):
            return self.engine.upload(self.to_numpy().astype(target_dtype))

        engine = self.engine if self.engine is not None else AOTEngine()
        with engine._lock:
            dst = engine.allocate(
                self.shape, dtype=target_dtype, host_accessible=host_accessible
            )
            src_ptr = self.map()
            dst_ptr = dst.map()
            try:
                num_elements = np.prod(self.shape)
                _LIB.ti_cast_buffer(
                    ctypes.c_void_p(src_ptr),
                    ctypes.c_void_p(dst_ptr),
                    int(num_elements),
                    dtype_map[self_dtype_type],
                    dtype_map[target_dtype_type],
                )
            finally:
                self.unmap()
                dst.unmap()
            return dst

    def view_as_vector(self, is_vector=True, vector_dim=3):
        buf = TaichiGPUBuffer(
            self.size_bytes,
            self.handle,
            self.shape,
            self.dtype,
            is_vector,
            self.engine,
            False,
            self.host_accessible,
            vector_dim,
        )
        buf._parent_ref = self
        return buf


class TaichiPlaceholder(TaichiGPUBuffer):
    def __init__(self, placeholder_id, shape, dtype, is_vector=False, vector_dim=3):
        super().__init__(
            0, placeholder_id, shape, dtype, is_vector, None, False, False, vector_dim
        )


# -------------------------------------------------------------------------
# AOT Engine and Wrappers
# -------------------------------------------------------------------------
class AOTModuleWrapper:
    def __init__(self, module_ptr, engine=None):
        self.module_ptr = module_ptr
        self.engine = engine
        self.engine_generation = getattr(engine, "_generation", 0)

    def __del__(self):
        module_ptr = getattr(self, "module_ptr", None)
        if not module_ptr:
            return

        try:
            engine = getattr(self, "engine", None)
            runtime = getattr(engine, "runtime", None) if engine is not None else _RUNTIME
            if _LIB is not None and runtime and not getattr(engine, "_destroyed", False):
                _LIB.destroy_aot_module(module_ptr)
        except Exception:
            pass
        finally:
            self.module_ptr = None

    def run(self, graph_name, **kwargs):
        """Menjalankan grafik Taichi AOT dengan validasi argumen yang informatif."""
        num_args = len(kwargs)
        args_array = (DynamicArg * num_args)()
        # CRITICAL: Keep names alive during the C++ call to prevent dangling pointers
        arg_names = [k.encode("utf-8") for k in kwargs.keys()]

        for i, (k, v) in enumerate(kwargs.items()):
            try:
                _populate_dynamic_arg(
                    args_array[i], arg_names[i], v, context_name=graph_name
                )
            except Exception as e:
                # Wrap error with clearer context
                raise ValueError(
                    f"Failed to prepare argument '{k}' for kernel '{graph_name}':\n{str(e)}"
                )

        engine = self.engine if self.engine is not None else AOTEngine()
        engine._refresh_memory_policy()
        engine._auto_pipeline_before_run(graph_name)
        if engine.current_pipeline:
            _lock_wait_begin(f"run:{graph_name}:pipeline")
            with engine._lock:
                _lock_wait_end()
                # Associate and track any TaichiGPUBuffer arguments with the current pipeline during recording
                for arg_val in kwargs.values():
                    if isinstance(arg_val, TaichiGPUBuffer):
                        arg_val.associated_pipelines.add(engine.current_pipeline)
                        if (
                            engine.current_pipeline
                            not in engine._pipeline_intermediates
                        ):
                            engine._pipeline_intermediates[engine.current_pipeline] = []
                        if (
                            arg_val
                            not in engine._pipeline_intermediates[
                                engine.current_pipeline
                            ]
                        ):
                            engine._pipeline_intermediates[
                                engine.current_pipeline
                            ].append(arg_val)

                # Every backend uses the same resident-memory admission rule.
                # If an automatic recording grows beyond the current budget,
                # abandon recording while preserving buffers and continue via
                # direct dispatch. Explicit legacy recordings still fail
                # clearly instead of silently overcommitting device memory.
                decision = engine._refresh_memory_policy()
                limit = (
                    int(decision.pipeline_resident_limit)
                    if decision is not None else 512 * 1024 * 1024
                )
                resident = sum(
                    int(getattr(buf, "size_bytes", getattr(buf, "nbytes", 0)) or 0)
                    for buf in engine._pipeline_intermediates.get(
                        engine.current_pipeline, []))
                if limit > 0 and resident > limit:
                    state = getattr(engine._local, "auto_pipeline_context", None)
                    if state and state.get("mode") == "recorded":
                        engine._abort_auto_pipeline(
                            f"resident budget exceeded ({resident} > {limit} bytes)"
                        )
                    else:
                        raise RuntimeError(
                            "AOT pipeline exceeds the adaptive resident-memory "
                            f"limit ({resident} > {limit} bytes); "
                            f"recommended block size is "
                            f"{getattr(decision, 'recommended_block_size', 512)}.")

                if engine.current_pipeline:
                    _op_begin(f"add_to_pipeline:{graph_name}")
                    try:
                        _LIB.add_to_pipeline(
                            self.module_ptr,
                            engine.current_pipeline.encode("utf-8"),
                            graph_name.encode("utf-8"),
                            args_array,
                            num_args,
                        )
                    except Exception:
                        _record_error()
                        raise
                    finally:
                        _op_end()
                else:
                    _op_begin(f"run_aot_graph:{graph_name}")
                    try:
                        _LIB.run_aot_graph(
                            engine.runtime,
                            self.module_ptr,
                            graph_name.encode("utf-8"),
                            args_array,
                            num_args,
                        )
                        _raise_native_engine_error(
                            engine.runtime, f"Kernel '{graph_name}'"
                        )
                    finally:
                        _op_end()
        else:
            _lock_wait_begin(f"run:{graph_name}")
            try:
                with engine._lock:
                    _lock_wait_end()
                    # TEMPORARILY DISABLED: per-graph Intel Vulkan quarantine.
                    # Explicit selection in General Settings now runs the native
                    # path so that real workloads can be validated.
                    # if (
                    #     engine.arch.lower() == "vulkan"
                    #     and "intel" in getattr(engine, "gpu_name", "").lower()
                    #     and "microsoft" not in getattr(engine, "gpu_name", "").lower()
                    #     and os.environ.get("PIXEL_REFINE_AOT_INTEL_UNSAFE") == "1"
                    #     and not _intel_vulkan_allowed(engine.device_id)
                    # ):
                    #     msg = (
                    #         f"Intel native Vulkan AOT graph '{graph_name}' quarantined: "
                    #         "Taichi 1.7.4 ABI triggers STATUS_STACK_BUFFER_OVERRUN."
                    #     )
                    #     _record_error()
                    #     raise RuntimeError(msg)
                    _op_begin(f"run_aot_graph:{graph_name}")
                    try:
                        _LIB.run_aot_graph(
                            engine.runtime,
                            self.module_ptr,
                            graph_name.encode("utf-8"),
                            args_array,
                            num_args,
                        )
                        _raise_native_engine_error(
                            engine.runtime, f"Kernel '{graph_name}'"
                        )
                    except Exception as e:
                        _record_error()
                        raise RuntimeError(
                            f"\n[AOTEngine Execution Error] Kernel '{graph_name}' gagal dijalankan!\n"
                            f"  ERROR: {str(e)}\n"
                            f"  HINT : Periksa apakah ukuran (shape) dan tipe data input sudah sesuai dengan definisi kernel di C++."
                        )
                    finally:
                        _op_end()
            except RuntimeError:
                raise
            except Exception as e:
                _record_error()
                raise RuntimeError(
                    f"\n[AOTEngine Execution Error] Kernel '{graph_name}' gagal dijalankan!\n"
                    f"  ERROR: {str(e)}\n"
                    f"  HINT : Periksa apakah ukuran (shape) dan tipe data input sudah sesuai dengan definisi kernel di C++."
                )

    def async_run(self, graph_name, **kwargs):
        """Menjalankan grafik Taichi AOT secara asinkron menggunakan ThreadPoolExecutor."""
        _heartbeat()
        engine = self.engine if self.engine is not None else AOTEngine()
        if getattr(engine, "_executor", None) is None:
            with engine._lock:
                if getattr(engine, "_executor", None) is None:
                    engine._executor = ThreadPoolExecutor(max_workers=8)

        def _run_and_sync():
            with engine._lock:
                self.run(graph_name, **kwargs)
                engine.sync()

        return engine._executor.submit(_run_and_sync)

    def _dummy_run(self):
        pass  # For keeping refs if needed


class AOTEngine:
    _instances = {}
    _active_arch = "vulkan"
    _placeholder_id_counter = 0xFFFFFF00

    def __new__(cls, arch=None, device_id=None):
        config = resolve_backend_config(arch=arch, device_id=device_id)
        arch = config.backend
        device_id = config.device_id
        explicit_backend = config.explicit

        # TEMPORARILY DISABLED: engine-boundary Intel Vulkan quarantine.
        # Do not silently replace a saved/selected Intel Vulkan backend with
        # OpenGL while compatibility testing is active.
        # if arch.lower() == "vulkan":
        #     _intel_name = get_vulkan_device_name(int(device_id)) or ""
        #     if (
        #         "intel" in _intel_name.lower()
        #         and not _intel_vulkan_allowed(device_id)
        #         and not explicit_backend
        #     ):
        #         _schedule_intel_vulkan_qualification(device_id)
        #         print("[AOTEngine] Intel Vulkan quarantined; selecting OPENGL")
        #         arch = "opengl"
        #         device_id = 0

        # CPU and OpenGL expose one logical device through this bridge.
        # Normalize before the singleton key is formed so instances cannot
        # alias the same native runtime under arbitrary Vulkan device IDs.
        if arch.lower() in ("cpu", "opengl"):
            device_id = 0
            os.environ["PIXEL_REFINE_AOT_DEVICE"] = "0"

        # Load exactly one backend bridge only after the final backend and
        # device policy has been resolved. Loading Vulkan before an Intel
        # quarantine decision would permanently contaminate an OpenGL process.
        _init_aot_bridge(arch)

        key = (arch.lower(), device_id)
        existing = cls._instances.get(key)
        if existing is not None and (
            getattr(existing, "_destroyed", False)
            or getattr(existing, "runtime", None) is None
        ):
            cls._instances.pop(key, None)
            existing = None

        if existing is None:
            instance = super(AOTEngine, cls).__new__(cls)
            instance.arch = arch
            instance.device_id = device_id
            instance._backend_config = config

            # Map arch to arch_id
            arch_id = {
                "vulkan": 0,
                "cuda": 1,
                "cpu": 2,
                "opengl": 3,
            }.get(arch.lower(), 0)
            native_device_id = int(device_id)
            if arch.lower() in ("cpu", "opengl") and native_device_id != 0:
                native_device_id = 0

            # Wrap init_aot_engine in a thread with timeout to detect hung Vulkan driver.
            # ctypes releases the GIL during C calls, so this timeout mechanism works
            # even if the C function hangs. The early watchdog is a secondary safety net.
            _op_begin("init_aot_engine")
            _init_result = [None]
            _init_error = [None]

            def _do_init():
                try:
                    with _suppress_native_stderr(arch.lower() == "vulkan"):
                        _init_result[0] = _LIB.init_aot_engine(
                            arch_id,
                            native_device_id,
                        )
                except Exception as e:
                    _init_error[0] = e

            _init_thread = None
            if arch.lower() in ("opengl", "cuda"):
                # OpenGL contexts are thread-affine. CUDA's Taichi runtime
                # likewise binds its primary context to the initializing
                # thread; creating it in a short-lived timeout worker leaves
                # the Python/main thread with CUDA_ERROR_INVALID_CONTEXT at
                # module teardown. Both bridges therefore initialize on the
                # caller thread. Vulkan keeps the timeout worker because its
                # ICD initialization can hang on a broken driver.
                _do_init()
            else:
                _init_thread = threading.Thread(target=_do_init, daemon=True)
                _init_thread.start()
                _init_thread.join(timeout=_INIT_TIMEOUT_S)
            _op_end()

            if _init_thread is not None and _init_thread.is_alive():
                # init_aot_engine hung beyond timeout — Vulkan driver is likely broken
                sys.stderr.write(
                    f"[AOTEngine] CRITICAL: init_aot_engine() hung for >{_INIT_TIMEOUT_S}s. "
                    f"Vulkan driver may be in a bad state (zombie GPU processes?).\n"
                    f"  HINT: Kill zombie processes or set PIXEL_REFINE_INIT_TIMEOUT to increase limit.\n"
                )
                sys.stderr.flush()
                raise RuntimeError(
                    f"init_aot_engine() timed out after {_INIT_TIMEOUT_S}s. "
                    f"GPU driver is likely hung. Run emergency_cleanup() or restart."
                )

            if _init_error[0] is not None:
                raise RuntimeError(f"init_aot_engine() failed: {_init_error[0]}")

            instance.runtime = _init_result[0]
            if not instance.runtime:
                init_error = _get_last_init_error()
                raise RuntimeError(
                    f"Failed to initialize {arch.upper()} AOT Runtime on device {device_id}."
                    + (f" {init_error}" if init_error else "")
                )

            gpu_name = (
                get_vulkan_device_name(device_id)
                if arch.lower() == "vulkan"
                else _get_runtime_device_name(instance.runtime)
            )
            if arch.lower() == "opengl":
                expected_vendor = os.environ.get(
                    "PIXEL_REFINE_OPENGL_EXPECTED_VENDOR", ""
                )
                expected_name = os.environ.get(
                    "PIXEL_REFINE_OPENGL_EXPECTED_NAME", ""
                )
                if not _opengl_renderer_matches_vendor(
                    gpu_name, expected_vendor
                ):
                    context_backend = _get_runtime_context_backend(instance.runtime)
                    try:
                        _LIB.destroy_aot_engine(instance.runtime)
                    finally:
                        instance.runtime = None
                    raise RuntimeError(
                        "OpenGL renderer mismatch: selected "
                        f"{expected_name or expected_vendor!r}, but the active "
                        f"{context_backend or 'context provider'} selected "
                        f"{gpu_name or 'an unknown renderer'!r}. "
                        "Native ICD selection is used automatically when the "
                        "vendor driver is discoverable; otherwise provide a "
                        "vendor libEGL.dll. WGL is not supported."
                    )
            if gpu_name:
                print(
                    f"[AOTEngine] Runtime initialized on '{arch.upper()}' ({gpu_name})"
                )
                if arch.lower() == "opengl":
                    context_backend = _get_runtime_context_backend(instance.runtime)
                    if context_backend:
                        print(
                            f"[AOTEngine] OpenGL context provider: {context_backend}"
                        )
                # Intel's legacy native Vulkan allocator (not Dozen) can assert
                # during Taichi context teardown when AOT memory blocks are
                # still tracked internally.  Keep the process alive by letting
                # the OS reclaim the context instead of calling the faulty
                # destructor; this is scoped to Intel and never affects NVIDIA.
                if arch.lower() == "vulkan" and "intel" in gpu_name.lower() and "microsoft" not in gpu_name.lower():
                    # Keep teardown conservative even while the execution
                    # quarantine is disabled: it affects only resource release,
                    # not backend selection or graph dispatch.
                    os.environ.setdefault("PIXEL_REFINE_AOT_SAFE_TEARDOWN", "1")
                    # TEMPORARILY DISABLED: setting this flag previously made
                    # every unqualified Intel Vulkan graph fail before dispatch.
                    # os.environ.setdefault("PIXEL_REFINE_AOT_INTEL_UNSAFE", "1")
                    os.environ.setdefault("PIXEL_REFINE_VULKAN_SERIALIZE_SUBMIT", "1")
            else:
                print(
                    f"[AOTEngine] Runtime initialized on '{arch.upper()}' (Device {device_id})"
                )

            instance.gpu_name = gpu_name or ""
            # The bridge is the source of truth for the actual OpenGL ICD and
            # Vulkan physical-device name.  Refresh the immutable selection
            # record so diagnostics and downstream callers never rely on an
            # ordinal alone.
            instance._backend_config = config.with_device(
                device_id=device_id,
                vendor=normalize_vendor(gpu_name or config.vendor),
                device_name=gpu_name or config.device_name,
            )
            instance.modules = {}
            instance.buffer_pool = BufferPool(instance)
            instance._local = threading.local()
            instance._staging_pool = {}
            instance._pipeline_intermediates = {}
            instance.recorded_pipelines = set()
            # Automatic pipeline metadata is kept per thread at dispatch time;
            # this engine-level slot makes lifecycle/reset behavior explicit.
            instance._auto_pipeline_context = None
            instance._live_buffers = weakref.WeakSet()
            instance._executor = None
            instance._lock = threading.RLock()
            instance._destroyed = False
            instance._generation = 0
            instance._block_config = BlockConfig()
            instance._cache_telemetry = CacheTelemetry()
            instance._device_memory_provider = (
                (lambda selected_id=int(device_id): query_vulkan_memory_budget(selected_id))
                if arch.lower() == "vulkan"
                else None
            )
            instance._memory_governor = MemoryGovernor(
                configured_max_bytes=instance._block_config.cache_bytes,
                device_provider=instance._device_memory_provider,
            )
            instance._auto_pipeline_planner = AutoPipelinePlanner(
                backend=str(arch).lower(),
                memory_provider=lambda: instance.get_memory_status(),
            )
            initial_memory = instance._memory_governor.refresh(force=True)
            instance.buffer_pool.set_budget(initial_memory.device_pool_budget)
            print(
                "[AOTEngine Memory] "
                f"pressure={initial_memory.pressure.name.lower()} "
                f"shared_budget={initial_memory.shared_device_budget // (1024 ** 2)}MB "
                f"device_available={initial_memory.device_heap_available // (1024 ** 2)}MB "
                f"source={initial_memory.device_budget_source} "
                f"pipeline_limit={initial_memory.pipeline_resident_limit // (1024 ** 2)}MB "
                f"block={initial_memory.recommended_block_size}"
            )
            instance._block_cache = BlockCache(
                instance._block_config.cache_entries,
                max_bytes=initial_memory.host_cache_budget,
                telemetry=instance._cache_telemetry,
            )
            instance._device_block_cache = DeviceResidencyCache(0)

            cls._instances[key] = instance
        return cls._instances[key]

    @property
    def current_pipeline(self):
        if not hasattr(self._local, "current_pipeline"):
            self._local.current_pipeline = None
        return self._local.current_pipeline

    @current_pipeline.setter
    def current_pipeline(self, val):
        self._local.current_pipeline = val

    def placeholder(self, shape, dtype=np.float32, is_vector=False, vector_dim=3):
        p = TaichiPlaceholder(
            self._placeholder_id_counter, shape, dtype, is_vector, vector_dim
        )
        self._placeholder_id_counter += 1
        return p

    def rec_pipeline(self, name):
        # Pipeline selection is automatic.  OpenGL recording is allowed by
        # default; per-stage capability checks and the resident-memory guard
        # below decide whether a graph can remain native.  The historical
        # PIXEL_REFINE_AOT_NATIVE_PIPELINE switch remains a compatibility
        # override, but is no longer required for normal developer usage.
        auto_pipeline = self.arch.lower() == "opengl" and os.environ.get(
            "PIXEL_REFINE_AOT_NATIVE_PIPELINE") != "1"

        class Recorder:
            def __init__(self, engine, name):
                self.engine, self.name = engine, name

            def __enter__(self):
                module = (
                    next(iter(self.engine.modules.values()))
                    if self.engine.modules
                    else None
                )
                _LIB.clear_pipeline(
                    module.module_ptr if module else None, self.name.encode("utf-8")
                )
                self.engine.current_pipeline = self.name
                self.engine.recorded_pipelines.add(self.name)
                self.engine._auto_pipeline_active = auto_pipeline

                # Clear previous intermediates for this pipeline
                if self.name in self.engine._pipeline_intermediates:
                    for buf in self.engine._pipeline_intermediates[self.name]:
                        buf._force_destroy()
                    del self.engine._pipeline_intermediates[self.name]
                return self

            def __exit__(self, *args):
                self.engine.current_pipeline = None

        return Recorder(self, name)

    def _auto_pipeline_before_run(self, graph_name):
        """Advance an active automatic scope before a graph dispatch.

        Segmented plans remain graph-order preserving while synchronization is
        inserted at each planned boundary. An unexpected graph degrades to
        direct dispatch instead of leaving a partially recorded pipeline.
        """
        state = getattr(self._local, "auto_pipeline_context", None)
        if not state or state.get("aborted"):
            return
        expected = state.get("graph_names", ())
        cursor = int(state.get("cursor", 0))
        if cursor >= len(expected) or str(graph_name) != expected[cursor]:
            self._abort_auto_pipeline(
                f"unexpected graph order at {graph_name!r}"
            )
            try:
                self.sync()
            except Exception:
                pass
            return
        boundaries = state.get("boundaries", ())
        segment_index = boundaries[cursor] if cursor < len(boundaries) else 0
        if state.get("segment_index") is not None and segment_index != state["segment_index"]:
            self.sync()
        state["segment_index"] = segment_index
        state["cursor"] = cursor + 1

    def _drop_pipeline_recording(self, name, *, destroy_intermediates=False):
        """Cancel recording while preserving caller-owned GPU buffers."""
        if not name:
            return
        try:
            _LIB.clear_pipeline(None, str(name).encode("utf-8"))
        except Exception:
            pass
        key = str(name)
        self.recorded_pipelines.discard(key)
        for buf in self._pipeline_intermediates.pop(key, []):
            buf.associated_pipelines.discard(key)
            if destroy_intermediates and getattr(buf, "is_pipeline_intermediate", False):
                buf._force_destroy()
            else:
                buf.is_pipeline_intermediate = False

    def _abort_auto_pipeline(self, reason):
        state = getattr(self._local, "auto_pipeline_context", None)
        if not state or state.get("aborted"):
            return
        state["aborted"] = True
        name = state.get("name")
        if self.current_pipeline:
            # Flush the already-recorded prefix before abandoning the
            # recording. Dropping it silently would lose earlier graph
            # results when a later allocation crosses the adaptive limit.
            active_name = name or self.current_pipeline
            self.current_pipeline = None
            try:
                if active_name in self.recorded_pipelines:
                    self.use_pipeline(active_name)
            finally:
                self._drop_pipeline_recording(active_name)
        print(f"[AOTEngine Pipeline] automatic recording disabled: {reason}")

    def use_pipeline(self, name, overrides=None):
        _init_aot_bridge()
        if name not in self.recorded_pipelines:
            print(
                f"[AOTEngine WARNING] Pipeline '{name}' is not recorded or has been invalidated (one of its buffers was destroyed). Skipping execution."
            )
            return

        ovr = overrides or {}
        n = len(ovr)
        handles = (ctypes.c_uint64 * n)()
        args = (DynamicArg * n)()
        # Keep names alive
        arg_names = [b"override"] * n
        for i, (p, b) in enumerate(ovr.items()):
            handles[i] = ctypes.c_uint64(p.handle)
            _populate_dynamic_arg(args[i], arg_names[i], b)
        _lock_wait_begin(f"use_pipeline:{name}")
        with self._lock:
            _lock_wait_end()
            _op_begin(f"run_pipeline:{name}")
            try:
                _LIB.run_pipeline(self.runtime, name.encode("utf-8"), handles, args, n)
                _raise_native_engine_error(self.runtime, f"Pipeline '{name}'")
            except Exception:
                _record_error()
                raise
            finally:
                _op_end()

    def allocate(
        self,
        shape,
        dtype=np.float32,
        is_vector=False,
        host_accessible=False,
        vector_dim=None,
    ):
        if not host_accessible and hasattr(self, "_memory_governor"):
            self._refresh_memory_policy()
        _lock_wait_begin("allocate")
        with self._lock:
            _lock_wait_end()
            size = int(np.prod(shape) * np.dtype(dtype).itemsize)
            v_dim = (
                vector_dim
                if vector_dim is not None
                else (shape[-1] if is_vector and len(shape) >= 2 else 1)
            )
            handle = self.buffer_pool.acquire(size) if not host_accessible else None
            if not handle:
                _op_begin("allocate_gpu_buffer")
                try:
                    handle = _LIB.allocate_gpu_buffer(
                        self.runtime, size, 1 if host_accessible else 0
                    )
                except Exception:
                    _record_error()
                    raise
                finally:
                    _op_end()

            if handle is None or handle == 0:
                _record_error()
                raise RuntimeError(
                    f"\n[AOTEngine Memory Error] Failed to allocate {size/1024/1024:.2f} MB on GPU ({self.arch.upper()}, Device {self.device_id}).\n"
                    f"  HINT: VRAM might be exhausted. Try calling 'engine.buffer_pool.clear()' or 'gc.collect()' to free idle buffers."
                )

            buf = TaichiGPUBuffer(
                size,
                handle,
                shape,
                dtype,
                is_vector,
                self,
                host_accessible=host_accessible,
                vector_dim=v_dim,
            )
            self._live_buffers.add(buf)
            if self.current_pipeline:
                buf.is_pipeline_intermediate = True
                buf.associated_pipelines.add(self.current_pipeline)
                if self.current_pipeline not in self._pipeline_intermediates:
                    self._pipeline_intermediates[self.current_pipeline] = []
                self._pipeline_intermediates[self.current_pipeline].append(buf)
            return buf

    def clear_pipeline_by_name(self, name):
        """Safely erases a pipeline from C++ and forces destruction of its intermediate buffers."""
        with self._lock:
            if name in self.recorded_pipelines:
                self.recorded_pipelines.remove(name)
            _LIB.clear_pipeline(None, name.encode("utf-8"))
            if name in self._pipeline_intermediates:
                bufs = self._pipeline_intermediates[name]
                for buf in bufs:
                    if name in buf.associated_pipelines:
                        buf.associated_pipelines.remove(name)
                    if not buf.associated_pipelines:
                        buf._force_destroy()
                del self._pipeline_intermediates[name]

    def clear_pipelines(self):
        """Clear all registered pipelines and destroy their intermediate buffers."""
        with self._lock:
            for name in list(self._pipeline_intermediates.keys()):
                self.clear_pipeline_by_name(name)
            self.recorded_pipelines.clear()

    def configure_blocks(
        self,
        enabled=None,
        size=None,
        threshold_bytes=None,
        cache_entries=None,
        cache_bytes=_UNSET,
        adaptive_memory=None,
        device_cache_enabled=None,
        device_cache_bytes=None,
    ):
        """Update the opt-in block execution policy for this engine."""
        with self._lock:
            self._ensure_memory_cache_runtime()
            current = self._block_config
            config = BlockConfig(
                enabled=current.enabled if enabled is None else bool(enabled),
                size=current.size if size is None else size,
                threshold_bytes=(
                    current.threshold_bytes
                    if threshold_bytes is None
                    else int(threshold_bytes)
                ),
                cache_entries=(
                    current.cache_entries if cache_entries is None else int(cache_entries)
                ),
                cache_bytes=(
                    current.cache_bytes
                    if cache_bytes is _UNSET
                    else (None if cache_bytes is None else int(cache_bytes))
                ),
                adaptive_memory=(
                    current.adaptive_memory if adaptive_memory is None else bool(adaptive_memory)
                ),
                device_cache_enabled=(
                    current.device_cache_enabled
                    if device_cache_enabled is None else bool(device_cache_enabled)
                ),
                device_cache_bytes=(
                    current.device_cache_bytes
                    if device_cache_bytes is None else int(device_cache_bytes)
                ),
            )
            self._block_config = config
            self._memory_governor.configure(config.cache_bytes)
            self._refresh_memory_policy(force=True)
            return config

    def _ensure_memory_cache_runtime(self):
        """Lazily initialize policy components for lightweight/test engine instances."""
        if not hasattr(self, "_cache_telemetry"):
            self._cache_telemetry = CacheTelemetry()
        if not hasattr(self, "_memory_governor"):
            self._memory_governor = MemoryGovernor(
                configured_max_bytes=self._block_config.cache_bytes,
                device_provider=getattr(self, "_device_memory_provider", None),
            )
        if not hasattr(self, "_block_cache"):
            self._block_cache = BlockCache(
                self._block_config.cache_entries,
                telemetry=self._cache_telemetry,
            )
        elif self._block_cache._telemetry is None:
            self._block_cache._telemetry = self._cache_telemetry
        if not hasattr(self, "_device_block_cache"):
            self._device_block_cache = DeviceResidencyCache(0)

    def get_block_config(self):
        """Return the active block execution policy."""
        return self._block_config

    def get_block_cache(self):
        """Return the engine-owned block cache for block-aware algorithms."""
        self._refresh_memory_policy()
        return self._block_cache

    def _refresh_memory_policy(self, force=False):
        self._ensure_memory_cache_runtime()
        if not self._block_config.adaptive_memory:
            self._block_cache.set_limits(
                self._block_config.cache_entries,
                self._block_config.cache_bytes,
            )
            device_budget = (
                self._block_config.device_cache_bytes
                if self._block_config.device_cache_enabled else 0
            )
            self.buffer_pool.set_budget(device_budget)
            self._device_block_cache.set_budget(device_budget)
            return None
        decision = self._memory_governor.refresh(force=force)
        if decision.device_pool_budget < self.buffer_pool.pooled_bytes:
            # Idle handles may still be referenced by queued OpenGL commands.
            # Synchronize before adaptive eviction to avoid SSBO use-after-free.
            self.sync()
        self.buffer_pool.set_budget(decision.device_pool_budget)
        self._block_cache.set_limits(
            self._block_config.cache_entries,
            decision.host_cache_budget,
        )
        device_budget = (
            min(
                self._block_config.device_cache_bytes,
                decision.device_pool_budget,
            )
            if self._block_config.device_cache_enabled and decision.allow_cache else 0
        )
        self._device_block_cache.set_budget(device_budget)
        return decision

    def put_block_record(self, record):
        """Admit a block result only while the realtime memory policy allows it."""
        self._refresh_memory_policy()
        admitted = self._block_cache.put(record)
        if self._block_config.device_cache_enabled:
            self._promote_block_record(record)
        return admitted

    @staticmethod
    def _resident_buffers_nbytes(buffers):
        if isinstance(buffers, tuple):
            return sum(AOTEngine._resident_buffers_nbytes(item) for item in buffers)
        return int(buffers.size_bytes)

    @staticmethod
    def _destroy_resident_buffers(buffers):
        items = buffers if isinstance(buffers, tuple) else (buffers,)
        for item in items:
            item.destroy()

    def _upload_resident_data(self, data):
        if isinstance(data, tuple):
            uploaded = []
            try:
                for item in data:
                    uploaded.append(self.upload(np.ascontiguousarray(item), is_vector=item.ndim == 3))
                return tuple(uploaded)
            except Exception:
                self._destroy_resident_buffers(tuple(uploaded))
                raise
        array = np.ascontiguousarray(data)
        return self.upload(array, is_vector=array.ndim == 3)

    @staticmethod
    def _download_resident_data(buffers):
        if isinstance(buffers, tuple):
            return tuple(np.ascontiguousarray(item.to_numpy()) for item in buffers)
        return np.ascontiguousarray(buffers.to_numpy())

    def _promote_block_record(self, record):
        """Keep a native copy of a validated host tile under the VRAM budget."""
        cache = self._device_block_cache
        if cache.max_bytes <= 0 or record.data is None:
            return None
        existing = cache.peek(record.block_id)
        if (
            existing is not None
            and existing.checksum == record.checksum
            and existing.source_checksum == record.source_checksum
        ):
            return existing
        try:
            buffers = self._upload_resident_data(record.data)
        except Exception:
            return None
        entry = cache.put(
            record.block_id,
            record.owner,
            buffers,
            self._resident_buffers_nbytes(buffers),
            dispose=self._destroy_resident_buffers,
            checksum=record.checksum,
            source_checksum=record.source_checksum,
        )
        if entry is None:
            self._destroy_resident_buffers(buffers)
        return entry

    def restore_resident_block(self, block_id, source_checksum):
        """Download a leased native tile, rejecting stale or corrupted data."""
        self._refresh_memory_policy()
        with self._device_block_cache.lease(block_id) as entry:
            if entry is None or entry.source_checksum != source_checksum:
                return None
            try:
                data = self._download_resident_data(entry.buffer)
                actual = (
                    tuple(checksum(item) for item in data)
                    if isinstance(data, tuple) else checksum(data)
                )
                if actual != entry.checksum:
                    raise RuntimeError("resident block checksum mismatch")
                return BlockRecord(
                    str(block_id), state=BlockState.READY, data=data,
                    checksum=entry.checksum, source_checksum=entry.source_checksum,
                    owner=entry.owner,
                )
            except Exception:
                pass
        self._device_block_cache.invalidate(block_id)
        return None

    def get_memory_status(self, force=False):
        """Return the current adaptive host-memory decision as plain data."""
        self._refresh_memory_policy(force=force)
        status = self._memory_governor.snapshot()
        resident = 0
        for buf in tuple(getattr(self, "_live_buffers", ())):
            if getattr(buf, "handle", None) is not None and getattr(buf, "is_owner", False):
                resident += int(getattr(buf, "size_bytes", 0) or 0)
        pooled = int(getattr(self.buffer_pool, "pooled_bytes", 0) or 0)
        status["resident_bytes"] = resident + pooled
        status["live_bytes"] = resident
        status["pooled_bytes"] = pooled
        status["resident_limit"] = int(status.get("pipeline_resident_limit", 0) or 0)
        status["resident_over_limit"] = bool(
            status["resident_limit"] > 0 and resident > status["resident_limit"]
        )
        status["resident_headroom_bytes"] = max(0, status["resident_limit"] - resident)
        return status

    def plan_pipeline(self, graphs):
        """Plan graph grouping automatically from current memory telemetry.

        Public algorithms may call this helper when they have a multi-graph
        operation.  Callers do not need to name or manage a recorded pipeline;
        the returned plan selects direct, recorded, or segmented execution.
        The legacy ``rec_pipeline``/``use_pipeline`` primitives remain below
        as compatibility mechanisms for existing stress tests.
        """
        self._refresh_memory_policy()
        return self._auto_pipeline_planner.plan(graphs)

    @contextmanager
    def auto_pipeline(self, graphs, *, name=None):
        """Execute a multi-graph scope using the safest automatic mode.

        This is the migration path away from hand-written ``rec_pipeline`` /
        ``use_pipeline`` pairs.  A scope with enough resident-memory budget is
        recorded and submitted once; direct/segmented plans leave recording
        disabled so every graph dispatch remains bounded by the governor.  In
        both cases callers retain the returned :class:`PipelinePlan` for
        diagnostics and can keep their existing ``module.run`` calls unchanged.

        The legacy primitives remain available for compatibility, but new
        algorithms should prefer this context manager.
        """
        specs = tuple(graphs)
        plan = self.plan_pipeline(specs)
        graph_names = tuple(
            str(item.name) for segment in plan.segments for item in segment
        )
        boundaries = tuple(
            index for index, segment in enumerate(plan.segments) for _ in segment
        )
        state = {
            "name": None,
            "graph_names": graph_names,
            "boundaries": boundaries,
            "cursor": 0,
            "segment_index": None,
            "aborted": False,
            "mode": plan.mode,
        }
        self._local.auto_pipeline_context = state
        if plan.mode != "recorded":
            try:
                yield plan
            finally:
                try:
                    self.sync()
                finally:
                    self._local.auto_pipeline_context = None
            return

        if name is None:
            digest = hashlib.sha1(
                "|".join(str(item.name) for item in plan.segments[0]).encode("utf-8")
            ).hexdigest()[:12]
            name = f"__auto_pipeline_{digest}"

        state["name"] = str(name)
        completed = False
        try:
            with self.rec_pipeline(str(name)):
                try:
                    yield plan
                    completed = True
                finally:
                    # ``rec_pipeline`` always clears the thread-local
                    # recording state. Submission is skipped after an
                    # adaptive fallback or an exception.
                    pass
            if completed and not state["aborted"]:
                self.use_pipeline(str(name))
            elif state["aborted"]:
                self.sync()
        except BaseException:
            if not state["aborted"]:
                self._drop_pipeline_recording(
                    str(name), destroy_intermediates=True
                )
            raise
        finally:
            self._local.auto_pipeline_context = None

    def get_block_cache_stats(self):
        self._ensure_memory_cache_runtime()
        stats = self._cache_telemetry.snapshot()
        stats.update({
            "entries": len(self._block_cache),
            "size_bytes": self._block_cache.size_bytes,
            "max_entries": self._block_cache.max_entries,
            "max_bytes": self._block_cache.max_bytes,
            "owner_bytes": self._block_cache.owner_bytes,
            "owner_targets": self._block_cache.owner_targets(),
            "device": self._device_block_cache.stats(),
            "buffer_pool": {
                "pooled_bytes": self.buffer_pool.pooled_bytes,
                "max_bytes": self.buffer_pool.max_bytes,
                "size_classes": len(self.buffer_pool.free_buffers),
            },
        })
        return stats

    def configure_block_reservation(self, operation, soft_bytes=0, hard_bytes=None, weight=1.0):
        """Configure an elastic owner quota for the feature-gated VRAM cache."""
        self._ensure_memory_cache_runtime()
        self._device_block_cache.configure_owner(operation, soft_bytes, hard_bytes, weight)

    def get_device_block_cache(self):
        self._refresh_memory_policy()
        return self._device_block_cache

    def clear_block_cache(self):
        """Drop cached block results without changing the active policy."""
        with self._lock:
            self._block_cache.clear()
            self._device_block_cache.clear()

    def plan_blocks(self, operation, shape, nbytes, halo=0):
        """Plan explicit or pressure-triggered blocks for parity-safe operations."""
        decision = (
            self._refresh_memory_policy()
            if self._block_config.adaptive_memory else None
        )
        explicit = should_use_blocks(operation, nbytes, self._block_config)
        automatic = bool(
            decision is not None
            and is_auto_block_safe(operation)
            and int(nbytes) >= max(
                1,
                min(
                    int(self._block_config.threshold_bytes),
                    int(decision.target_chunk_bytes),
                ),
            )
        )
        if not explicit and not automatic:
            return None
        size = self._block_config.normalized_size()
        if decision is not None:
            recommended = int(decision.recommended_block_size)
            if automatic and not self._block_config.enabled:
                size = (recommended, recommended)
            else:
                size = (min(size[0], recommended), min(size[1], recommended))
        return BlockGrid(shape, size=size, halo=halo)

    def get_staging_buffer(self, shape, dtype):
        """Deprecated: use acquire_staging_buffer instead for thread safety."""
        return self.acquire_staging_buffer(shape, dtype)

    def acquire_staging_buffer(self, shape, dtype):
        size = int(np.prod(shape) * np.dtype(dtype).itemsize)
        key = (size, np.dtype(dtype).name)
        with self._lock:
            if key not in self._staging_pool:
                self._staging_pool[key] = []

            # Find an unleased buffer
            for entry in self._staging_pool[key]:
                if not entry["leased"]:
                    entry["leased"] = True
                    return entry["buffer"]

            # None found, allocate a new one
            buf = self.allocate(shape, dtype, host_accessible=True)
            self._staging_pool[key].append({"leased": True, "buffer": buf})
            return buf

    def release_staging_buffer(self, staging_buf):
        size = staging_buf.size_bytes
        dtype_name = np.dtype(staging_buf.dtype).name
        key = (size, dtype_name)
        with self._lock:
            if key in self._staging_pool:
                for entry in self._staging_pool[key]:
                    if entry["buffer"] is staging_buf:
                        entry["leased"] = False
                        break

    def _is_external_gpu_obj(self, data):
        if hasattr(data, "is_cuda") and data.is_cuda:
            return "pytorch"
        if type(data).__name__ == "UMat":
            return "opencv"
        if type(data).__name__ == "OrtValue":
            return "onnx"
        if hasattr(data, "__cuda_array_interface__"):
            return "cuda"
        return None

    def _upload_fast_interop(
        self, data, is_vector=False, vector_dim=3
    ) -> TaichiGPUBuffer:
        """Universal Fast-Copy bridge using Pinned Memory DMA."""
        obj_type = self._is_external_gpu_obj(data)
        shape = getattr(data, "shape", (1,))
        dtype = np.float32

        if obj_type == "pytorch":
            import torch

            dtype_map = {
                torch.float32: np.float32,
                torch.uint8: np.uint8,
                torch.int32: np.int32,
            }
            dtype = dtype_map.get(data.dtype, np.float32)
        elif hasattr(data, "dtype"):
            dtype = data.dtype

        staging = self.acquire_staging_buffer(shape, dtype)
        try:
            ptr = staging.map()

            if obj_type == "pytorch":
                import torch

                target_view = torch.from_blob(
                    ptr, shape, dtype=data.dtype, device="cpu"
                )
                target_view.copy_(data.detach(), non_blocking=False)
            elif hasattr(data, "__cuda_array_interface__"):
                src_ptr = data.__cuda_array_interface__["data"][0]
                ctypes.memmove(ptr, src_ptr, staging.nbytes)
            else:
                temp = np.ascontiguousarray(data)
                ctypes.memmove(ptr, temp.ctypes.data, temp.nbytes)

            staging.unmap()
            vram_target = self.allocate(
                shape, dtype, is_vector=is_vector, vector_dim=vector_dim
            )
            _op_begin("copy_gpu_buffer:fast_interop")
            try:
                _LIB.copy_gpu_buffer(
                    self.runtime, staging.handle, vram_target.handle, staging.nbytes
                )
            except Exception:
                _record_error()
                raise
            finally:
                _op_end()
        finally:
            self.release_staging_buffer(staging)
        return vram_target

    def upload(self, data, is_vector=False, vector_dim=3):
        _heartbeat()
        _init_aot_bridge()

        # Short-circuit: if already a TaichiGPUBuffer, return as-is (zero-copy passthrough)
        if isinstance(data, TaichiGPUBuffer):
            return data

        ext_type = self._is_external_gpu_obj(data)

        # Auto-detect Vector Fields (RGB=3, Flow=2)
        if not is_vector and hasattr(data, "shape"):
            if len(data.shape) == 3:
                if data.shape[2] == 3:
                    is_vector = True
                    vector_dim = 3
                elif data.shape[2] == 2:
                    is_vector = True
                    vector_dim = 2

        if ext_type:
            return self._upload_fast_interop(
                data, is_vector=is_vector, vector_dim=vector_dim
            )

        arr = np.ascontiguousarray(data)
        buf = self.allocate(
            arr.shape,
            arr.dtype,
            is_vector=is_vector,
            host_accessible=True,
            vector_dim=vector_dim,
        )
        _op_begin("write_to_gpu_buffer")
        try:
            _LIB.write_to_gpu_buffer(
                self.runtime, buf.handle, arr.ctypes.data, buf.nbytes
            )
        except Exception:
            _record_error()
            raise
        finally:
            _op_end()
        return buf

    def load(self, path):
        with self._lock:
            base, ext = os.path.splitext(path)
            p = (
                f"{base}_{self.arch.lower()}{ext}"
                if os.path.exists(f"{base}_{self.arch.lower()}{ext}")
                else path
            )
            # LLVM/CPU AOT in Taichi 1.7.4 consumes the unpacked module
            # directory. Graphics runtimes consume .tcm directly. Prefer a
            # checked-in CPU directory when present, otherwise safely
            # materialize a content-addressed cache from the packed artifact.
            if self.arch.lower() == "cpu" and p.lower().endswith(".tcm"):
                cpu_directory = os.path.splitext(p)[0]
                p = (
                    cpu_directory
                    if os.path.isdir(cpu_directory)
                    else _materialize_cpu_aot_directory(p)
                )
            if p in self.modules:
                return self.modules[p]
            if self.arch.lower() == "vulkan":
                device_name = get_vulkan_device_name(self.device_id)
            elif self.arch.lower() == "opengl":
                # Hybrid systems can run this same logical OpenGL backend on
                # physically different renderers. Keep artifact quarantine and
                # validation records isolated per actual adapter.
                device_name = (
                    _get_runtime_device_name(self.runtime)
                    or "opengl-unknown-renderer"
                )
            else:
                device_name = "logical-device"
            cache_key = artifact_key(p, self.arch, self.device_id, device_name)
            cached = get_status(cache_key)
            if cached and cached.get("status") == "quarantined":
                raise RuntimeError(
                    f"AOT artifact quarantined for {self.arch.upper()} device {device_name}: {os.path.basename(p)}"
                )
            try:
                with _suppress_native_stderr(self.arch.lower() == "vulkan"):
                    ptr = _LIB.load_aot_module(self.runtime, p.encode("utf-8"))
            except Exception as exc:
                set_status(cache_key, "quarantined", error=str(exc))
                raise
            if not ptr:
                native_error = _get_native_engine_error(self.runtime)
                detail = f"\n  NATIVE: {native_error}" if native_error else ""
                try:
                    self.reinit(self.device_id)
                except Exception:
                    pass
                set_status(cache_key, "quarantined", error=native_error or "load returned null")
                raise RuntimeError(
                    f"\n[AOTEngine Load Error] Failed to load TCM module at: {p}\n"
                    f"  HINT: Ensure the .tcm file exists and is compatible with the active GPU backend ({self.arch.upper()})."
                    f"{detail}"
                )
            print(f"[AOTEngine] Loaded TCM module: {os.path.basename(p)}")
            set_status(cache_key, "valid", backend=self.arch, device=device_name)
            self.modules[p] = AOTModuleWrapper(ptr, self)
            return self.modules[p]

    def imread(self, path):
        _heartbeat()
        _init_aot_bridge()
        w, h, c, d = ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0)
        _lock_wait_begin("imread")
        with self._lock:
            _lock_wait_end()
            _op_begin(f"imread:{os.path.basename(path)}")
            try:
                handle = _LIB.ti_imread_to_gpu(
                    self.runtime,
                    path.encode("utf-8"),
                    ctypes.byref(w),
                    ctypes.byref(h),
                    ctypes.byref(c),
                    ctypes.byref(d),
                )
            except Exception:
                _record_error()
                raise
            finally:
                _op_end()
        if not handle:
            raise RuntimeError(f"Failed to load image: {path}")
        dtype = np.uint8 if d.value == 8 else np.uint16
        shape = (h.value, w.value) if c.value == 1 else (h.value, w.value, c.value)
        return TaichiGPUBuffer(
            w.value * h.value * c.value * (d.value // 8),
            handle,
            shape,
            dtype,
            engine=self,
            host_accessible=False,
        )

    def imwrite(self, path, buf):
        _heartbeat()
        _init_aot_bridge()
        h, w = buf.shape[0], buf.shape[1]
        c = 1 if len(buf.shape) == 2 else buf.shape[2]
        d = 8 if buf.dtype == np.uint8 else 16
        _lock_wait_begin("imwrite")
        with self._lock:
            _lock_wait_end()
            _op_begin(f"imwrite:{os.path.basename(path)}")
            try:
                res = _LIB.ti_imwrite_from_gpu(
                    self.runtime, path.encode("utf-8"), buf.handle, w, h, c, d
                )
            except Exception:
                _record_error()
                raise
            finally:
                _op_end()
        if not res:
            raise RuntimeError(f"Failed to save image: {path}")

    def sync(self):
        _lock_wait_begin("sync")
        with self._lock:
            _lock_wait_end()
            _op_begin("sync_runtime")
            try:
                _LIB.sync_runtime(self.runtime)
            except Exception:
                _record_error()
                raise
            finally:
                _op_end()

    @contextmanager
    def reserve_device_execution(self, owner="operation"):
        """Lease the Vulkan queue across a dependent multi-graph operation."""
        name = str(owner)
        _lock_wait_begin(f"device-reservation:{name}")
        with self._lock:
            _lock_wait_end()
            self.sync()
            try:
                yield self
            finally:
                self.sync()

    def last_error(self):
        return _get_native_engine_error(self.runtime)

    def clear_last_error(self):
        _clear_native_engine_error(self.runtime)

    def reinit(self, device_id=0):
        with self._lock:
            active_arch = self.arch.lower()
            # Taichi's x64 C runtime only accepts device index 0. Keep the
            # public reinit API uniform while preventing a CPU recovery from
            # accidentally requesting a GPU device index.
            requested_device = (
                0 if active_arch in ("cpu", "opengl") else int(device_id)
            )
            old_runtime = self.runtime
            for mod in list(self.modules.values()):
                mod.module_ptr = None
            self.modules = {}
            self.recorded_pipelines.clear()
            self._pipeline_intermediates = {}
            if hasattr(self, "_local"):
                self._local.auto_pipeline_context = None
            self._staging_pool = {}
            try:
                self.buffer_pool.clear()
            except Exception:
                pass
            try:
                destroy_engine = getattr(_LIB, "destroy_aot_engine")
            except AttributeError:
                destroy_engine = None
            if old_runtime and destroy_engine is not None:
                try:
                    destroy_engine(old_runtime)
                except Exception:
                    pass
            with _suppress_native_stderr(self.arch.lower() == "vulkan"):
                self.runtime = _LIB.init_aot_engine(
                    {
                        "vulkan": 0,
                        "cuda": 1,
                        "cpu": 2,
                        "opengl": 3,
                    }.get(active_arch, 0),
                    requested_device,
                )
            if not self.runtime:
                raise RuntimeError(
                    f"Failed to reinitialize Taichi AOT runtime for {active_arch}"
                )
            # Keep legacy buffer helpers that rely on the module-level runtime
            # synchronized with an explicit reinit().
            global _RUNTIME
            _RUNTIME = self.runtime
            self.device_id = requested_device
            self._device_memory_provider = (
                (
                    lambda selected_id=requested_device: query_vulkan_memory_budget(
                        selected_id
                    )
                )
                if active_arch == "vulkan"
                else None
            )
            if hasattr(self, "_memory_governor"):
                self._memory_governor.device_provider = (
                    self._device_memory_provider
                )
                self._memory_governor._device_sample = None
                self._memory_governor._decision = None
            self._destroyed = False
            self._generation = getattr(self, "_generation", 0) + 1

    def destroy(self):
        """Full GPU context teardown: free all buffers, clear pipelines, shutdown executor.

        Safe to call multiple times. After this call the engine instance is invalidated.
        This is called automatically by the global atexit / signal cleanup handler.
        """
        with self._lock:
            if not getattr(self, "_destroyed", False):
                self._destroyed = True

                # 1. Shutdown async executor gracefully (no new jobs)
                if self._executor is not None:
                    try:
                        self._executor.shutdown(wait=False, cancel_futures=True)
                    except TypeError:
                        # Python < 3.9 does not support cancel_futures
                        self._executor.shutdown(wait=False)
                    self._executor = None

                # 2. Clear all pipelines and their intermediate GPU buffers
                for name in list(getattr(self, "_pipeline_intermediates", {}).keys()):
                    try:
                        bufs = self._pipeline_intermediates.pop(name, [])
                        for buf in bufs:
                            buf.is_pipeline_intermediate = False
                            buf.associated_pipelines.discard(name)
                            if buf.handle is not None and buf.is_owner:
                                _LIB.free_gpu_buffer(self.runtime, buf.handle)
                                buf.handle = None
                                buf.is_owner = False
                    except Exception:
                        pass
                self.recorded_pipelines.clear()

                # 3. Free all staging pool buffers
                for entries in list(getattr(self, "_staging_pool", {}).values()):
                    for entry in entries:
                        buf = entry.get("buffer")
                        if buf and buf.handle is not None and buf.is_owner:
                            try:
                                _LIB.free_gpu_buffer(self.runtime, buf.handle)
                                buf.handle = None
                                buf.is_owner = False
                            except Exception:
                                pass
                self._staging_pool = {}

                # 4. Drain buffer pool free list
                try:
                    self.buffer_pool.clear()
                except Exception:
                    pass

                # 5. Unload all AOT modules
                for mod in list(self.modules.values()):
                    try:
                        if mod.module_ptr:
                            _LIB.destroy_aot_module(mod.module_ptr)
                            mod.module_ptr = None
                    except Exception:
                        pass
                self.modules = {}

                # 6. Sync and destroy the native runtime context
                runtime_to_destroy = self.runtime
                try:
                    if runtime_to_destroy:
                        _LIB.sync_runtime(runtime_to_destroy)
                except Exception:
                    pass
                try:
                    destroy_engine = getattr(_LIB, "destroy_aot_engine")
                except AttributeError:
                    destroy_engine = None
                skip_native_destroy = (
                    os.environ.get("PIXEL_REFINE_AOT_SAFE_TEARDOWN", "0") == "1"
                    and self.arch.lower() == "vulkan"
                )
                if runtime_to_destroy and destroy_engine is not None and not skip_native_destroy:
                    try:
                        destroy_engine(runtime_to_destroy)
                    except Exception:
                        pass
                elif skip_native_destroy:
                    print("[AOTEngine] Intel native Vulkan safe teardown: native context destructor skipped")
                self.runtime = None
                global _RUNTIME
                if _RUNTIME is runtime_to_destroy:
                    _RUNTIME = None
                for key, inst in list(AOTEngine._instances.items()):
                    if inst is self:
                        AOTEngine._instances.pop(key, None)

                # 7. Kill tracked child processes (vulkaninfo, etc.)
                _kill_tracked_children()


# =========================================================================
# Zombie GPU Process Cleanup
# =========================================================================
# Prevents zombie processes (vulkaninfo.exe, orphaned python.exe) from
# accumulating and corrupting the GPU driver state.

import subprocess as _subprocess
import gc as _gc

_child_pids = set()  # PIDs spawned by this process (tracked for cleanup)
_child_pids_lock = threading.Lock()


def _track_child_pid(pid):
    """Register a child process PID for later cleanup."""
    with _child_pids_lock:
        _child_pids.add(pid)


def _kill_tracked_children():
    """Kill all tracked child processes to prevent zombies."""
    with _child_pids_lock:
        pids = list(_child_pids)
        _child_pids.clear()
    for pid in pids:
        try:
            if os.name == "nt":
                _subprocess.run(
                    ["taskkill", "/F", "/PID", str(pid)], capture_output=True, timeout=5
                )
            else:
                os.kill(pid, signal.SIGKILL)
        except Exception:
            pass


def _cleanup_zombie_gpu_processes():
    """Kill zombie GPU processes (vulkaninfo.exe, orphaned python.exe) that
    are holding VRAM but are no longer responsive.

    This prevents the NVIDIA WDDM driver from accumulating ghost GPU context
    entries that block future Vulkan init and consume VRAM reservations.
    """
    if not _CLEAN_ZOMBIES:
        return

    my_pid = os.getpid()
    killed = []

    try:
        if os.name == "nt":
            # Windows: use tasklist to find GPU-holding zombie processes
            result = _subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.strip().split("\n"):
                parts = line.strip().strip('"').split('","')
                if len(parts) < 2:
                    continue
                proc_name = parts[0].lower()
                try:
                    pid = int(parts[1])
                except (ValueError, IndexError):
                    continue

                # Skip our own process
                if pid == my_pid:
                    continue

                # Kill vulkaninfo.exe zombies (spawned by Vulkan device scanning)
                if "vulkaninfo" in proc_name:
                    try:
                        _subprocess.run(
                            ["taskkill", "/F", "/PID", str(pid)],
                            capture_output=True,
                            timeout=5,
                        )
                        killed.append((pid, proc_name))
                    except Exception:
                        pass
        else:
            # Linux: use ps to find zombie GPU processes
            result = _subprocess.run(
                ["ps", "-eo", "pid,comm,state", "--no-headers"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.strip().split("\n"):
                parts = line.split()
                if len(parts) < 3:
                    continue
                try:
                    pid = int(parts[0])
                except ValueError:
                    continue
                comm = parts[1].lower()
                state = parts[2]

                if pid == my_pid:
                    continue

                # Kill zombie state processes related to GPU
                if state == "Z" and ("vulkan" in comm or "python" in comm):
                    try:
                        os.kill(pid, signal.SIGKILL)
                        killed.append((pid, comm))
                    except Exception:
                        pass
    except Exception as e:
        sys.stderr.write(f"[AOTEngine] Zombie cleanup scan failed: {e}\n")
        sys.stderr.flush()

    if killed:
        sys.stderr.write(
            f"[AOTEngine] Cleaned {len(killed)} zombie GPU process(es): "
            f"{', '.join(f'{name}(pid={pid})' for pid, name in killed)}\n"
        )
        sys.stderr.flush()


def emergency_cleanup():
    """Full emergency cleanup: free all VRAM + kill zombie processes + GC.

    Call this when the GPU is in a bad state to recover without a reboot.
    Safe to call multiple times.
    """
    # 1. Force-free all GPU resources
    _force_global_cleanup("emergency")

    # 2. Kill zombie GPU processes
    _cleanup_zombie_gpu_processes()

    # 3. Kill any tracked child processes
    _kill_tracked_children()

    # 4. Force Python garbage collection
    _gc.collect()

    sys.stderr.write("[AOTEngine] Emergency cleanup complete.\n")
    sys.stderr.flush()


# Pre-init zombie cleanup: clear any pre-existing zombies that could block Vulkan init
if _CLEAN_ZOMBIES:
    _cleanup_zombie_gpu_processes()

_initial_engine = AOTEngine()


class _EngineHandle:
    """Stable module-level engine reference with lifecycle recovery.

    ``InputArray``/``OutputArray`` and older callers use this global directly.
    If an application explicitly destroys the singleton and starts another
    processing job, retaining the old object would route allocations through a
    null native runtime.  Reacquire the same backend/device lazily while
    keeping the historical attribute-based API intact.
    """

    __slots__ = ("_target",)

    def __init__(self, target):
        object.__setattr__(self, "_target", target)

    def _live(self):
        global _RUNTIME
        target = object.__getattribute__(self, "_target")
        if getattr(target, "_destroyed", False) or getattr(target, "runtime", None) is None:
            target = AOTEngine(
                arch=getattr(target, "arch", None),
                device_id=getattr(target, "device_id", 0),
            )
            object.__setattr__(self, "_target", target)
            _RUNTIME = target.runtime
        return target

    def __getattr__(self, name):
        return getattr(self._live(), name)

    def __setattr__(self, name, value):
        if name == "_target":
            object.__setattr__(self, name, value)
        else:
            setattr(self._live(), name, value)

    def __repr__(self):
        return repr(self._live())

    @property
    def __class__(self):
        # Preserve the concrete type exposed by the legacy module-global.
        return self._live().__class__


engine = _EngineHandle(_initial_engine)
_RUNTIME = _initial_engine.runtime


def get_backend_config() -> BackendConfig:
    """Return the live canonical backend/device contract."""

    target = engine._live()
    config = getattr(target, "_backend_config", None)
    if config is not None:
        return config
    return BackendConfig(
        backend=getattr(target, "arch", "cpu"),
        device_id=getattr(target, "device_id", 0),
        device_name=getattr(target, "gpu_name", ""),
    )


def get_backend_name() -> str:
    """Return the concrete active backend (never an alias or ``auto``)."""

    return get_backend_config().backend


def backend_info() -> dict:
    """Return JSON-safe backend diagnostics for UI/logging and child jobs."""

    return get_backend_config().as_dict()

# =========================================================================
# Global Resource Cleanup Guard
# =========================================================================
# This multi-layer guard ensures VRAM is freed even when the host process
# is killed unexpectedly (Task Manager, OS shutdown, Python crash).
# Without this, Windows holds the Vulkan/CUDA memory reservation until
# a full reboot, blocking shutdown/restart on systems with discrete GPUs.

_CLEANUP_LOCK = threading.Lock()
_CLEANUP_DONE = False


def _global_cleanup(reason: str = "atexit", force: bool = False):
    """Release all GPU resources for every live AOTEngine instance.

    Idempotent — safe to call from multiple signal handlers.

    Args:
        reason: Human-readable label for diagnostic logging.
        force: If True, bypass the one-shot _CLEANUP_DONE guard.
               Used by the watchdog to trigger cleanup while the
               interpreter is still alive (e.g. hung GPU operation).
    """
    global _CLEANUP_DONE
    with _CLEANUP_LOCK:
        if _CLEANUP_DONE and not force:
            return
        _CLEANUP_DONE = True

    try:
        sys.stderr.write(f"[AOTEngine] GPU cleanup triggered (reason={reason})\n")
        sys.stderr.flush()
    except Exception:
        pass

    # Destroy every engine instance registered in the class-level dict
    for key, inst in list(AOTEngine._instances.items()):
        try:
            inst.destroy()
        except Exception:
            pass
    AOTEngine._instances.clear()

    # Kill zombie GPU processes and tracked children to prevent VRAM leaks
    try:
        _kill_tracked_children()
    except Exception:
        pass
    try:
        _cleanup_zombie_gpu_processes()
    except Exception:
        pass
    try:
        _gc.collect()
    except Exception:
        pass


def _force_global_cleanup(reason: str):
    """Watchdog entry point: always runs, bypasses one-shot guard.

    Called by the enhanced watchdog when a fatal condition is detected
    (operation timeout, lock contention, heartbeat stale, error storm).
    """
    _global_cleanup(reason=reason, force=True)


# --- atexit: runs on normal exit AND uncaught exceptions ---
atexit.register(_global_cleanup, "atexit")


# --- Signal handlers: SIGTERM / SIGBREAK (Windows) / SIGINT / Hardware Crash Signals ---
def _signal_cleanup_handler(signum, frame):
    _global_cleanup(f"signal-{signum}")
    # Re-raise default behaviour so the OS knows the process ended
    signal.signal(signum, signal.SIG_DFL)
    os.kill(os.getpid(), signum)


# Register normal exit signals and critical crash signals (like Access Violation / Segfault)
# to catch C++ DLL crashes and cleanly free VRAM before Windows freezes the process context.
crash_signals = [signal.SIGTERM, signal.SIGINT]
for name in ("SIGSEGV", "SIGILL", "SIGABRT", "SIGFPE"):
    if hasattr(signal, name):
        crash_signals.append(getattr(signal, name))

for _sig in crash_signals:
    try:
        signal.signal(_sig, _signal_cleanup_handler)
    except (OSError, ValueError):
        pass  # Cannot set handlers on non-main threads; skip gracefully

# SIGBREAK is Windows-specific (Ctrl+Break / console close)
if hasattr(signal, "SIGBREAK"):
    try:
        signal.signal(signal.SIGBREAK, _signal_cleanup_handler)
    except (OSError, ValueError):
        pass


# --- Watchdog is started EARLY (before DLL/GPU init) — see top of file ---


# -------------------------------------------------------------------------
# OpenCV-style Data Unification (InputArray / OutputArray)
# -------------------------------------------------------------------------
def InputArray(data, is_vector=False, vector_dim=None) -> TaichiGPUBuffer:
    """
    OpenCV-style Data Input Unification.
    Automatically handles NumPy arrays, PyTorch tensors, OpenCV UMats,
    native Python lists, or existing TaichiGPUBuffer instances.
    """
    if isinstance(data, (TaichiGPUBuffer, TaichiPlaceholder)):
        return data

    # Auto-convert native Python structures
    if isinstance(data, (list, tuple, int, float)):
        data = np.array(data, dtype=np.float32)

    # Delegate to universal fast-interop bridge
    return engine.upload(data, is_vector=is_vector, vector_dim=vector_dim)


def OutputArray(
    shape, dtype=np.float32, is_vector=False, vector_dim=None,
    host_accessible=False,
) -> TaichiGPUBuffer:
    """
    OpenCV-style Data Output Allocation.
    Creates an empty GPU VRAM buffer ready for writing.
    """
    return engine.allocate(
        shape, dtype=dtype, is_vector=is_vector,
        vector_dim=vector_dim, host_accessible=host_accessible,
    )
