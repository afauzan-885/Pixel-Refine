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
from dataclasses import dataclass
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, Future

from .block import (
    BlockCache,
    BlockConfig,
    BlockGrid,
    BlockPath,
    BlockRecord,
    BlockState,
    checksum,
    can_auto_block,
    operation_capability,
    operation_contract,
    should_use_blocks,
)
from .memory import CacheTelemetry, MemoryGovernor
from .residency import DeviceResidencyCache
from .auto_pipeline import AutoPipelinePlanner
from .capabilities import classify_device
from .artifact_cache import artifact_key, get_status, set_status
from .backend_manager import BackendManager
from taichi_vision.backend_config import (
    BackendConfig,
    backend_env,
    normalize_backend,
    normalize_vendor,
    parse_device_id,
    requested_backend,
    is_android_runtime,
)
from taichi_vision.device_selection import (
    is_translation_device,
    make_device_selector,
    query_vulkan_memory_budget,
    resolve_device_selector,
    scan_vulkan_device_records,
)
from .artifact_targets import detect_target
from .tcm_preflight import preflight_tcm

_UNSET = object()
_CPU_AOT_EXTRACTION_LOCK = threading.RLock()
_OPENGL_VENDOR_INJECTED = None


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
                    with archive.open(member) as source, open(
                        destination, "wb"
                    ) as output:
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

        vk.vkCreateInstance.argtypes = [
            ctypes.POINTER(VkInstanceCreateInfo),
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        vk.vkCreateInstance.restype = ctypes.c_int

        vk.vkDestroyInstance.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        vk.vkDestroyInstance.restype = None

        vk.vkEnumeratePhysicalDevices.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_void_p),
        ]
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
        res = vk.vkCreateInstance(
            ctypes.pointer(create_info), None, ctypes.pointer(instance)
        )
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
        null_idx = name_bytes.find(b"\x00")
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


_HEARTBEAT_TIMEOUT_S = _env_float("HEARTBEAT_TIMEOUT", 10.0)
_OP_TIMEOUT_S = _env_float("OP_TIMEOUT", 120.0)
_LOCK_CONTENTION_S = _env_float("LOCK_TIMEOUT", 30.0)
_ERROR_WINDOW_S = _env_float("ERROR_WINDOW", 30.0)
_ERROR_THRESHOLD = _env_int("ERROR_THRESHOLD", 5)
_WATCHDOG_DISABLE_REQUESTED = any(
    os.environ.get(name, "0") == "1"
    for name in (
        "DISABLE_AOT_WATCHDOG",
        "PIXEL_REFINE_DISABLE_AOT_WATCHDOG",
    )
)
_AUTO_DESTROY_ENABLED = (
    os.environ.get("AUTO_DESTROY", "1") != "0"
    and not _WATCHDOG_DISABLE_REQUESTED
)
# Idle reclamation is deliberately disabled by default.  Native GPU buffer
# finalizers and Python GC must run at an owner-thread synchronization point,
# never from this daemon watchdog thread.  The resident pipeline already has
# explicit safe-point reclamation for the supported processing paths.
_WATCHDOG_IDLE_RECLAIM_ENABLED = (
    os.environ.get("AOT_WATCHDOG_IDLE_RECLAIM", "0") == "1"
)
_INIT_TIMEOUT_S = _env_float("INIT_TIMEOUT", 30.0)
_CLEAN_ZOMBIES = os.environ.get("CLEAN_ZOMBIES", "0") == "1"
_EXPERIMENT_MODE = os.environ.get("AOT_EXPERIMENT", "0") == "1"
_SUPPRESS_VULKAN_LOADER_WARNINGS = (
    os.environ.get("SUPPRESS_VULKAN_LOADER_WARNINGS", "1") != "0"
)
_PRESERVE_NATIVE_STDERR = any(
    os.environ.get(name, "0") == "1"
    for name in (
        "AOT_PRESERVE_NATIVE_STDERR",
        "AOT_VERBOSE_NATIVE_ERRORS",
    )
)
_DEVICE_CACHE_PATH = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
    "PixelRefine",
    "aot_device_cache.txt",
)
# Lifecycle pools are intentionally small and bounded.  The limits are
# process-level safety valves; the adaptive memory governor supplies the
# byte budgets for the active device/pressure state.
_MAX_STAGING_POOL_ENTRIES = max(1, _env_int("AOT_MAX_STAGING_ENTRIES", 4))
_MAX_RETIRED_BUFFERS = max(1, _env_int("AOT_MAX_RETIRED_BUFFERS", 16))
_DEFAULT_STAGING_POOL_BUDGET = max(0, _env_int("AOT_STAGING_BUDGET", 64 * 1024**2))
_DEFAULT_RETIRED_BUFFER_BUDGET = max(0, _env_int("AOT_RETIRED_BUDGET", 64 * 1024**2))
# ``ThreadPoolExecutor`` itself has an unbounded submission queue.  A native
# AOT call retains every Python argument (and often a GPU buffer handle) until
# its future starts, so an unbounded queue can defeat the memory governor even
# though native dispatch remains serialized.  Keep the public ``async_run``
# API, but make admission explicit and bounded.
_MAX_ASYNC_PENDING = max(1, _env_int("AOT_MAX_ASYNC_PENDING", 8))
_STDERR_REDIRECT_LOCK = threading.Lock()
_PROCESS_JOB_HANDLE = None
_PROCESS_JOB_ACTIVE = False
_QUALIFICATION_NOTICES = set()


def _intel_vulkan_probe_override():
    """Permit Intel Vulkan only inside an explicitly isolated probe process."""
    return (
        any(
            os.environ.get(name) == "1"
            for name in ("AOT_INTEL_PROBE", "PIXEL_REFINE_AOT_INTEL_PROBE")
        )
        and any(
            os.environ.get(name) == "1"
            for name in ("AOT_ALLOW_UNSAFE_INTEL", "PIXEL_REFINE_AOT_ALLOW_UNSAFE_INTEL")
        )
    )


def _intel_vulkan_allowed(device_id):
    """Return true only for an isolated probe or exact validated build."""
    if _intel_vulkan_probe_override():
        return True
    try:
        from taichi_vision.vulkan_probe import intel_vulkan_is_validated

        return intel_vulkan_is_validated(device_id=int(device_id))
    except Exception:
        return False


def _graphics_compatibility_enabled(backend, vendor):
    """Resolve the shared legacy-driver policy without importing the API facade."""
    try:
        from taichi_vision.graphics_compatibility import (
            graphics_compatibility_enabled,
        )

        return graphics_compatibility_enabled(backend, vendor)
    except Exception:
        return False


def _schedule_intel_vulkan_qualification(device_id):
    """Queue full qualification after shutdown without delaying startup."""
    if _intel_vulkan_probe_override():
        return None
    try:
        from taichi_vision.intel_vulkan_qualification import (
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
            (item for item in devices if int(item.get("ordinal", -1)) == ordinal),
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
    os.environ["AOT_EXPERIMENT"] = "1" if enabled else "0"


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
            enabled
            and _SUPPRESS_VULKAN_LOADER_WARNINGS
            and not _PRESERVE_NATIVE_STDERR
            and os.name == "nt"
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


# -------------------------------------------------------------------------
# CUDA Thread-Local Primary Context Auto-Binding Manager
# Ensures worker threads (QThread, ThreadPoolExecutor, BurstCacheWorker)
# automatically bind the active CUDA primary context before invoking C-API driver calls.
# -------------------------------------------------------------------------
_CUDA_DRIVER_LIB = None
_CUDA_PRIMARY_CTX_MAP = {}  # device_id (int) -> ctypes.c_void_p (primary context)
_CUDA_CTX_LOCK = threading.Lock()


def _get_cuda_primary_context(device_id: int = 0):
    global _CUDA_DRIVER_LIB, _CUDA_PRIMARY_CTX_MAP
    with _CUDA_CTX_LOCK:
        if device_id in _CUDA_PRIMARY_CTX_MAP:
            return _CUDA_PRIMARY_CTX_MAP[device_id]
        try:
            if _CUDA_DRIVER_LIB is None:
                if os.name == "nt":
                    _CUDA_DRIVER_LIB = ctypes.CDLL("nvcuda.dll")
                else:
                    _CUDA_DRIVER_LIB = ctypes.CDLL("libcuda.so")
                _CUDA_DRIVER_LIB.cuInit(0)

            dev = ctypes.c_int()
            res_dev = _CUDA_DRIVER_LIB.cuDeviceGet(ctypes.byref(dev), int(device_id))
            if res_dev != 0:
                return None

            ctx = ctypes.c_void_p()
            res_ctx = _CUDA_DRIVER_LIB.cuDevicePrimaryCtxRetain(ctypes.byref(ctx), dev)
            if res_ctx != 0 or not ctx.value:
                return None

            _CUDA_PRIMARY_CTX_MAP[device_id] = ctx
            return ctx
        except Exception:
            return None


def ensure_cuda_context(device_id: int = 0):
    """Bind CUDA primary context for the calling thread if using CUDA backend."""
    ctx = _get_cuda_primary_context(device_id)
    if ctx and _CUDA_DRIVER_LIB:
        try:
            _CUDA_DRIVER_LIB.cuCtxSetCurrent(ctx)
        except Exception:
            pass


def _op_begin(name: str):
    """Mark the start of a blocking GPU/DLL operation."""
    # Ensure CUDA thread-local primary context is bound for the calling thread
    for inst in list(AOTEngine._instances.values()):
        if getattr(inst, "arch", "").lower() == "cuda":
            ensure_cuda_context(getattr(inst, "device_id", 0))

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
        # Lazy engine creation is intentional.  Before the first runtime is
        # registered, there is no native resource that this thread can safely
        # inspect or reclaim.  Treating that startup interval as idle used to
        # invoke Python GC while Vulkan was about to initialize.
        instances = list(AOTEngine._instances.values())
        if not instances:
            if not main_thread.is_alive():
                break
            continue

        # Eksperimen: Untuk backend GPU (CUDA, Vulkan, OpenGL), nonaktifkan Watchdog idle reclamation
        # dan error circuit breaker agar Primary GPU Context tetap aktif 100% dan GC diatur murni
        # per-algoritma / di main thread, mencegah crash assertion taichi_c_api.dll (vulkan_device.cpp:2045)
        # akibat _gc.collect() di secondary watchdog thread.
        is_gpu = False
        for inst in instances:
            arch_name = getattr(inst, "arch", "").lower()
            if arch_name in ("cuda", "vulkan", "opengl"):
                is_gpu = True
                break

        if not _AUTO_DESTROY_ENABLED or is_gpu:
            # If auto-destroy is disabled or GPU backend is active, only check main thread liveness
            if not main_thread.is_alive():
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
        # Idle reclamation is not performed by this daemon thread.  Native
        # finalizers can execute when Python objects become unreachable, so
        # even clearing a staging dictionary here can destroy a GPU resource
        # from the wrong thread.  Resident callers reclaim at explicit,
        # synchronized safe points instead.
        if activity_age > _HEARTBEAT_TIMEOUT_S and op_elapsed == 0.0:
            if _WATCHDOG_IDLE_RECLAIM_ENABLED and not _vram_reclaimed:
                try:
                    sys.stderr.write(
                        f"[AOTEngine Watchdog] Idle reclamation requested after "
                        f"{activity_age:.1f}s, but it is deferred to an owner-thread "
                        f"safe point.\n"
                    )
                    sys.stderr.flush()
                except Exception:
                    pass

                # Mark the idle interval as observed so the watchdog does not
                # repeatedly emit the deferred notice.  No native resource is
                # touched here.
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
        # Keep the legacy values stable.  4/5 extend the private bridge
        # metadata for native CPU compact graphs; this is an internal enum,
        # not a public API/ABI change (the struct layout is unchanged).
        ("dtype", ctypes.c_int),  # 0: f32, 1: i32, 2: u8, 3: u16, 4: i16, 5: f16
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
    np.int16: 4,
    np.float16: 5,
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

        # A wrapper can outlive ``reinit()``/shutdown.  The runtime teardown
        # deliberately clears its handle; reject the stale object here rather
        # than passing a null pointer into the native ABI (which otherwise
        # manifests as an access violation or a driver-specific assertion).
        resolved_handle = (
            value._resolve_handle()
            if hasattr(value, "_resolve_handle")
            else getattr(value, "handle", None)
        )
        if resolved_handle is None:
            raise RuntimeError(
                f"{context_name}: GPU buffer is no longer valid; "
                "the AOT runtime was reinitialized or destroyed"
            )
        owner_engine = getattr(value, "engine", None)
        if owner_engine is not None and getattr(
            value, "engine_generation", 0
        ) != getattr(owner_engine, "_generation", 0):
            raise RuntimeError(
                f"{context_name}: GPU buffer belongs to an old AOT runtime "
                "generation"
            )

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

        raw_handle = getattr(resolved_handle, "value", resolved_handle)
        arg.val_u64 = ctypes.c_uint64(int(raw_handle or 0))
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


def _cpu_supports_avx2():
    """Return whether the host CPU can execute the bridge AVX2 fast path.

    The native bridge contains a small AVX2 conversion path for host buffers.
    It is deliberately kept separate from the AOT kernel target: loading an
    AVX2 bridge on an older x86-64 CPU would otherwise fail only when a cast
    operation is first exercised.  Windows exposes this capability through
    ``IsProcessorFeaturePresent``; Linux/other hosts use ``/proc/cpuinfo`` as
    a best-effort fallback.  ``AOT_CPU_ISA`` can force
    ``baseline`` or ``avx2`` for diagnostics and packaging tests.
    """
    forced = str(os.environ.get("AOT_CPU_ISA", "auto")).strip().lower()
    if forced in {"baseline", "sse2", "generic"}:
        return False
    if forced in {"avx2", "native"}:
        return True

    if os.name == "nt":
        try:
            # PF_AVX2_INSTRUCTIONS_AVAILABLE is 40 in the Windows API.
            probe = ctypes.windll.kernel32.IsProcessorFeaturePresent
            probe.argtypes = [ctypes.c_uint]
            probe.restype = ctypes.c_int
            return bool(probe(40))
        except Exception:
            pass

    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8", errors="ignore") as fh:
            flags = fh.read().lower()
        return "avx2" in flags
    except Exception:
        return False


def _select_cpu_bridge(default_bridge):
    """Select an ISA-compatible CPU bridge without changing its ABI."""
    if not default_bridge or not os.path.exists(default_bridge):
        return default_bridge
    if _cpu_supports_avx2():
        return default_bridge
    extension = os.path.splitext(default_bridge)[1] or (
        ".dll" if os.name == "nt" else ".so"
    )
    baseline = os.path.join(
        os.path.dirname(default_bridge),
        "taichi_aot_engine_baseline" + extension,
    )
    if os.path.exists(baseline):
        print("[AOTEngine] AVX2 unavailable; selecting baseline CPU bridge")
        return baseline
    # A legacy package may contain only the historical AVX2 bridge.  Keep the
    # existing error/diagnostic path rather than silently changing the public
    # backend selection contract.
    return default_bridge


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
    legacy_aot_dll_dir = os.path.abspath(
        os.path.join(script_dir, "../taichi_algorithm/aot_py/aot_dll")
    )
    # The bridge is only loaded after AOTEngine has resolved a concrete
    # backend.  Keep this guard as a final safety net for legacy callers that
    # still invoke the private helper directly.
    backend = normalize_backend(
        backend if backend is not None else os.environ.get("AOT_ARCH", "vulkan"),
        allow_auto=True,
        strict=True,
    )
    if backend == "auto":
        backend = select_backend()
    # Desktop keeps the historical backend directories.  ARM/Linux/Android
    # uses target-qualified directories so a Windows DLL or an Android/Linux
    # bridge can never be selected merely because the backend name matches.
    target = detect_target(
        backend=backend,
        device=os.environ.get("TARGET_VENDOR", ""),
    )
    # Prefer the isolated LLVM20 bundle when it is present.  The resolver is
    # target-qualified, so a CUDA bridge can never be selected for Vulkan or
    # OpenGL merely because a similarly named file exists.  The repository
    # tree remains a compatibility fallback for source-only/rollback runs.
    aot_dll_dir = legacy_aot_dll_dir
    staged_bundle = None
    try:
        from taichi_vision.llvm20_runtime_paths import bundle_root

        staged_bundle = bundle_root(target.target_id)
    except (ImportError, OSError, ValueError):
        staged_bundle = None
    if staged_bundle is not None:
        aot_dll_dir = str(staged_bundle)
        print(f"[AOTEngine] LLVM20 runtime bundle selected: {aot_dll_dir}")
    target_dir = os.path.join(aot_dll_dir, target.target_id)
    backend_dir = (
        aot_dll_dir
        if staged_bundle is not None
        else target_dir
        if os.name != "nt" and os.path.isdir(target_dir)
        else os.path.join(aot_dll_dir, backend)
    )
    library_ext = (
        ".dll" if os.name == "nt" else ".dylib" if sys.platform == "darwin" else ".so"
    )
    renderer_bridge = os.path.join(
        backend_dir, "taichi_aot_engine_renderer" + library_ext
    )
    default_bridge = (
        renderer_bridge
        if backend in {"opengl", "gles"} and os.path.exists(renderer_bridge)
        else os.path.join(backend_dir, "taichi_aot_engine" + library_ext)
    )
    if backend == "cpu":
        default_bridge = _select_cpu_bridge(default_bridge)
    explicit_bridge = os.environ.get("AOT_ENGINE_DLL")
    if explicit_bridge:
        engine_dll_path = explicit_bridge
    elif os.path.exists(default_bridge):
        engine_dll_path = default_bridge
    else:
        # Keep the failure deterministic.  Falling back to a global DLL/so
        # with a different target can corrupt the C ABI before initialization.
        raise RuntimeError(
            f"No native AOT bridge for target {target.target_id}: {default_bridge}"
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
        print(f"[AOTEngine] Successfully loaded backend bridge: {engine_dll_path}")
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
    skip_translation = os.environ.get("AOT_SKIP_DOZEN", "1") == "1"
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
        parse_device_id(os.environ.get("AOT_DEFAULT_DEVICE"), 0),
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
    # ``opengl`` is retained as a desktop compatibility alias, but Android
    # must never load a desktop GL bridge or artifact under that name. Resolve
    # the legacy setting to the explicit GLES architecture before singleton
    # identity, bridge selection, and arch-id mapping are computed.
    if backend == "opengl" and is_android_runtime():
        backend = "gles"
    requested_id = parse_device_id(device_id)
    env_id = parse_device_id(os.environ.get("AOT_DEVICE"))

    if backend == "cpu":
        ordinal = 0
        name = "CPU (x86_64 Windows)"
        vendor = "cpu"
    elif backend in {"opengl", "gles"}:
        # OpenGL's native ICD chooses the adapter through the process/context;
        # the bridge exposes one logical device.  Keep vendor/name expectations
        # for the post-init renderer check instead of treating this as a
        # Vulkan ordinal.
        ordinal = 0
        name = os.environ.get("OPENGL_EXPECTED_NAME", "")
        # ``TARGET_VENDOR`` is the stable selection identity used
        # by the artifact resolver.  Use it as the default renderer contract
        # too, while allowing the more explicit OpenGL-only variables to
        # override it for embedding applications.
        expected_vendor = os.environ.get("OPENGL_EXPECTED_VENDOR", "")
        vendor = normalize_vendor(
            expected_vendor or os.environ.get("TARGET_VENDOR", "") or name
        )
    elif backend == "cuda":
        # CUDA ordinals are independent of Vulkan ordinals.  Prefer the
        # dedicated CUDA setting, then the generic setting for compatibility,
        # and finally CUDA device 0.
        ordinal = requested_id
        if ordinal is None:
            ordinal = parse_device_id(os.environ.get("CUDA_DEVICE"))
        if ordinal is None:
            ordinal = env_id if env_id is not None else 0
        name = os.environ.get("CUDA_EXPECTED_NAME", "")
        vendor = "nvidia"
    else:  # Vulkan
        ordinal = requested_id if requested_id is not None else env_id
        preferred_vendor = normalize_vendor(os.environ.get("TARGET_VENDOR", ""))
        if ordinal is not None and preferred_vendor != "unknown":
            # ``AOT_DEVICE`` is often restored from an older
            # settings file (and test harnesses historically defaulted it to
            # zero).  Treat the saved vendor as the stable identity and
            # repair a conflicting ordinal before loading the runtime.
            selected_vendor = normalize_vendor(get_vulkan_device_name(ordinal))
            if selected_vendor != preferred_vendor:
                ordinal = None
        if ordinal is None:
            ordinal = _read_cached_device_id()
            # A selector cache is ordinal-independent, but a legacy or stale
            # cache can still resolve to an adapter from the wrong vendor when
            # the user changed the saved backend preference.  Never let that
            # silently turn an NVIDIA request into Intel (or the reverse).
            if ordinal is not None and preferred_vendor != "unknown":
                cached_vendor = normalize_vendor(get_vulkan_device_name(ordinal))
                if cached_vendor != preferred_vendor:
                    ordinal = None
        if ordinal is None:
            ordinal = parse_device_id(os.environ.get("AOT_DEFAULT_DEVICE"), 0) or 0
            # Automatic/default Vulkan selection prefers a native NVIDIA
            # adapter, then native Intel/AMD, never Dozen.
            if os.environ.get("AOT_AUTOSCAN", "1") == "1" and (
                not explicit
                or requested_id is None
                or preferred_vendor != "unknown"
            ):
                # A saved backend choice may carry a vendor identity while
                # Vulkan ordinals are free to change after a driver update.
                # Prefer that identity during a fresh scan so NVIDIA is not
                # accidentally remapped to Intel (or vice versa).  The
                # selector/fingerprint cache remains the stronger path when
                # it is available.
                scanned = _scan_native_vulkan_device(preferred_vendor=preferred_vendor)
                if scanned is not None:
                    ordinal = scanned

        # Dozen/D3D12 adapters are translation layers, not native Vulkan
        # devices.  They must not slip through merely because a saved or
        # explicit ordinal points at them.  Keep the user-facing backend
        # choice strict, but repair the ordinal to the same vendor's native
        # adapter when one is available.  Diagnostic experiments can opt in
        # with AOT_ALLOW_TRANSLATION=1.
        skip_translation = os.environ.get("AOT_SKIP_DOZEN", "1") == "1"
        allow_translation = os.environ.get("AOT_ALLOW_TRANSLATION", "0") == "1"
        if ordinal is not None and skip_translation and not allow_translation:
            selected_record = None
            try:
                selected_record = next(
                    (
                        item
                        for item in scan_vulkan_device_records()
                        if int(item.get("ordinal", -1)) == int(ordinal)
                    ),
                    None,
                )
            except Exception:
                selected_record = None
            if selected_record is not None and is_translation_device(selected_record):
                selected_vendor = normalize_vendor(
                    selected_record.get("vendor") or selected_record.get("name")
                )
                replacement = _scan_native_vulkan_device(
                    preferred_vendor=(
                        preferred_vendor
                        if preferred_vendor != "unknown"
                        else selected_vendor
                    )
                )
                if replacement is None or int(replacement) == int(ordinal):
                    raise RuntimeError(
                        "Selected Vulkan adapter is a Dozen/D3D12 translation "
                        "device and no native adapter for the requested vendor "
                        "is available. Install/use the native Vulkan ICD or set "
                        "AOT_ALLOW_TRANSLATION=1 only for diagnostics."
                    )
                print(
                    "[AOTEngine] Vulkan translation adapter quarantined; "
                    f"using native device {replacement} ({selected_vendor or 'requested vendor'})"
                )
                ordinal = int(replacement)
        name = get_vulkan_device_name(ordinal) or ""
        if (
            skip_translation
            and not allow_translation
            and is_translation_device({"name": name})
        ):
            raise RuntimeError(
                f"Vulkan device {ordinal} ({name}) is a Dozen/D3D12 translation "
                "adapter; native Vulkan is required by the current policy."
            )
        vendor = normalize_vendor(name)
        if vendor == "intel" and not _intel_vulkan_allowed(ordinal):
            _schedule_intel_vulkan_qualification(ordinal)
            if not _graphics_compatibility_enabled("vulkan", vendor):
                raise RuntimeError(
                    "Native Intel Vulkan is quarantined for this device/driver "
                    "until the isolated lifecycle, device-copy, artifact-load, "
                    "and graph-dispatch gates pass. Dozen/D3D12 translation is "
                    "not an accepted production fallback. Enable "
                    "PIXEL_REFINE_GFX_COMPAT_MODE=1 for conservative native-GPU "
                    "execution, use CPU/OpenGL, or run the isolated Intel "
                    "qualification probe."
                )
            print(
                "[AOTEngine] Native Intel Vulkan admitted in legacy graphics "
                "compatibility mode; qualification continues independently."
            )

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
      TAICHI_ARCH env var, otherwise auto-selects.
    - device_memory_GB: optional device memory hint forwarded to `ti.init`.

    This function imports Taichi lazily and calls `ti.init(...)`.
    Use this from scripts before invoking any Taichi kernels.
    """
    try:
        import taichi as ti
    except Exception:
        raise RuntimeError("Taichi is not installed or cannot be imported.")

    env_pref = os.environ.get("TAICHI_ARCH")
    raw_choice = prefer or env_pref or os.environ.get("AOT_ARCH")
    arch_choice = normalize_backend(
        raw_choice, allow_auto=True, strict=raw_choice not in (None, "", "auto")
    )
    if arch_choice == "auto":
        arch_choice = select_backend()
    if arch_choice == "opengl" and is_android_runtime():
        arch_choice = "gles"
    # TEMPORARILY DISABLED: Intel Vulkan automatic reroute/quarantine.
    # The General Settings compatibility matrix must expose and exercise the
    # native Intel Vulkan path explicitly. Retain this policy as comments for
    # a quick rollback if a driver regression is confirmed.
    # if arch_choice == "vulkan":
    #     _device_name = get_vulkan_device_name(
    #         int(os.environ.get("AOT_DEVICE", 0))
    #     ) or ""
    #     if (
    #         "intel" in _device_name.lower()
    #         and not _intel_vulkan_allowed(
    #             int(os.environ.get("AOT_DEVICE", 0))
    #         )
    #         and not explicit_backend
    #     ):
    #         _schedule_intel_vulkan_qualification(
    #             int(os.environ.get("AOT_DEVICE", 0))
    #         )
    #         print("[engine.configure_taichi_backend] Intel Vulkan quarantined; using opengl")
    #         arch_choice = "opengl"

    # Map string to taichi arch constant
    arch_map = {
        "vulkan": getattr(ti, "vulkan", getattr(ti, "gpu", None)),
        "opengl": getattr(ti, "opengl", None),
        "gles": getattr(ti, "gles", None),
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
@dataclass(frozen=True)
class BufferKey:
    """Physical allocation identity used by the reusable buffer pool.

    A GPU allocation is raw storage; shape and dtype are carried by the
    ``DynamicArg`` metadata at dispatch time.  The key therefore contains the
    memory domain and vector view information (which must not be mixed), while
    allowing different shapes with the same byte capacity to share storage.
    The engine generation is intentionally not part of the key: each
    ``BufferPool`` belongs to one runtime generation and is discarded on
    reinitialisation.
    """

    size_bytes: int
    host_accessible: bool = False
    dtype: str = "raw"
    is_vector: bool = False
    vector_dim: int = 1
    usage: str = "storage"

    def __post_init__(self):
        if int(self.size_bytes) <= 0:
            raise ValueError("buffer allocation size must be positive")
        object.__setattr__(self, "size_bytes", int(self.size_bytes))
        object.__setattr__(self, "host_accessible", bool(self.host_accessible))
        object.__setattr__(self, "dtype", str(self.dtype or "raw"))
        object.__setattr__(self, "is_vector", bool(self.is_vector))
        object.__setattr__(self, "vector_dim", max(1, int(self.vector_dim)))
        object.__setattr__(self, "usage", str(self.usage or "storage"))


class BufferPool:
    """Bounded pool for reusable raw allocations.

    The old pool only covered device-local allocations and keyed handles by
    byte size.  Full-frame NumPy uploads use host-visible allocations, so they
    never benefited from reuse.  This pool now accepts a domain-aware
    ``BufferKey`` while retaining the integer-size API for old callers.
    """

    def __init__(self, engine=None):
        self.engine = engine
        self.free_buffers = {}  # BufferKey -> list of handles
        self.max_bytes = 0
        self.pooled_bytes = 0
        self._stats = {
            "hits": 0,
            "misses": 0,
            "stores": 0,
            "evictions": 0,
        }
        import threading

        self._lock = threading.Lock()

    @staticmethod
    def _key(
        size_or_key,
        *,
        host_accessible=False,
        dtype="raw",
        is_vector=False,
        vector_dim=1,
        usage="storage",
    ):
        if isinstance(size_or_key, BufferKey):
            return size_or_key
        return BufferKey(
            int(size_or_key),
            host_accessible=host_accessible,
            dtype=dtype,
            is_vector=is_vector,
            vector_dim=vector_dim,
            usage=usage,
        )

    def acquire(self, size_or_key, **kwargs):
        key = self._key(size_or_key, **kwargs)
        with self._lock:
            handles = self.free_buffers.get(key)
            if handles:
                handle = handles.pop()
                self.pooled_bytes = max(0, self.pooled_bytes - key.size_bytes)
                self._stats["hits"] += 1
                if not handles:
                    self.free_buffers.pop(key, None)
                return handle
            self._stats["misses"] += 1
            return None

    def store(self, size_or_key, handle, **kwargs):
        """Store a handle for reuse (caller decides if reuse or free)."""
        key = self._key(size_or_key, **kwargs)
        with self._lock:
            size = key.size_bytes
            if self.max_bytes <= 0 or self.pooled_bytes + size > self.max_bytes:
                runtime = self.engine.runtime if self.engine else _RUNTIME
                if self.engine and getattr(self.engine, "arch", "").lower() == "cuda":
                    ensure_cuda_context(getattr(self.engine, "device_id", 0))
                if _LIB and runtime:
                    try:
                        _LIB.free_gpu_buffer(runtime, handle)
                    except Exception:
                        pass
                self._stats["evictions"] += 1
                return
            if key not in self.free_buffers:
                self.free_buffers[key] = []
            self.free_buffers[key].append(handle)
            self.pooled_bytes += size
            self._stats["stores"] += 1

    def set_budget(self, max_bytes):
        """Apply an adaptive cap and evict largest idle buffers first."""
        with self._lock:
            self.max_bytes = max(0, int(max_bytes))
            runtime = self.engine.runtime if self.engine else _RUNTIME
            if self.engine and getattr(self.engine, "arch", "").lower() == "cuda":
                ensure_cuda_context(getattr(self.engine, "device_id", 0))
            for key in sorted(
                tuple(self.free_buffers),
                key=lambda item: item.size_bytes,
                reverse=True,
            ):
                handles = self.free_buffers.get(key, [])
                while handles and self.pooled_bytes > self.max_bytes:
                    handle = handles.pop()
                    if _LIB and runtime:
                        try:
                            _LIB.free_gpu_buffer(runtime, handle)
                        except Exception:
                            pass
                    self.pooled_bytes = max(0, self.pooled_bytes - key.size_bytes)
                    self._stats["evictions"] += 1
                if not handles:
                    self.free_buffers.pop(key, None)

    def clear(self):
        """Force-free all pooled handles from VRAM."""
        global _LIB, _RUNTIME
        # ``destroy()``/``release()`` may have placed handles in the engine's
        # retired queue rather than directly in this free-list.  Preserve the
        # historical public meaning of ``buffer_pool.clear()`` by promoting
        # that queue first; the engine performs one synchronization only.
        if self.engine and hasattr(self.engine, "_drain_retired"):
            try:
                self.engine._drain_retired(wait=True)
            except Exception:
                pass
        with self._lock:
            runtime = self.engine.runtime if self.engine else _RUNTIME
            if self.engine and getattr(self.engine, "arch", "").lower() == "cuda":
                ensure_cuda_context(getattr(self.engine, "device_id", 0))
            if _LIB and runtime:
                for handles in self.free_buffers.values():
                    for h in handles:
                        try:
                            _LIB.free_gpu_buffer(runtime, h)
                        except Exception:
                            pass
            self.free_buffers = {}
            self.pooled_bytes = 0

    def stats(self):
        with self._lock:
            requests = self._stats["hits"] + self._stats["misses"]
            return {
                **self._stats,
                "enabled": bool(
                    self.engine is None
                    or getattr(self.engine, "_buffer_cache_enabled", True)
                ),
                "hit_rate": (self._stats["hits"] / requests if requests else 0.0),
                "pooled_bytes": self.pooled_bytes,
                "max_bytes": self.max_bytes,
                "size_classes": len(self.free_buffers),
            }


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
        self.engine_generation = getattr(engine, "_generation", 0)
        self.associated_pipelines = set()

    def _buffer_key(self):
        return BufferKey(
            self.size_bytes,
            host_accessible=self.host_accessible,
            dtype=np.dtype(self.dtype).str,
            is_vector=self.is_vector,
            vector_dim=self.vector_dim,
        )

    def release(self):
        """Release the buffer back to the engine's buffer pool for reuse."""
        if self.handle is not None and self.is_owner:
            if self.engine and self.engine.current_pipeline:
                # Bypass/protect buffers during recording to prevent use-after-free
                if getattr(self, "is_pipeline_intermediate", False) or (
                    self.engine.current_pipeline in self.associated_pipelines
                ):
                    return

            if self.engine:
                self.engine._retire_buffer(self)
            else:
                self.destroy(force=True)

    def destroy(self, force=False):
        """Release the allocation, retaining it for safe cache reuse by default.

        ``destroy()`` remains terminal from the caller's point of view: the
        wrapper loses ownership immediately.  The engine may retain the raw
        handle in a retired queue until the native runtime has completed all
        queued work.  Internal teardown uses ``force=True`` to bypass the pool.
        """
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

            if self.engine and not force:
                self.engine._retire_buffer(self)
                return

            global _LIB, _RUNTIME
            if self.engine and getattr(self.engine, "arch", "").lower() == "cuda":
                ensure_cuda_context(getattr(self.engine, "device_id", 0))
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
        self.destroy(force=True)

    def __del__(self):
        self.destroy()

    @property
    def ndim(self):
        return len(self.shape)

    @property
    def nbytes(self):
        return self.size_bytes

    def _resolve_handle(self):
        """Resolve a non-owning vector view through its owning parent."""
        parent = getattr(self, "_parent_ref", None)
        if parent is not None:
            return getattr(parent, "handle", None)
        return getattr(self, "handle", None)

    def _require_live(self, operation="GPU buffer access"):
        """Return the active runtime or reject a stale wrapper."""
        handle = self._resolve_handle()
        if handle is None:
            raise RuntimeError(
                f"{operation} failed: GPU buffer is no longer valid; "
                "the AOT runtime was reinitialized or destroyed"
            )
        runtime = self.engine.runtime if self.engine else _RUNTIME
        if runtime is None:
            raise RuntimeError(f"{operation} failed: AOT runtime is not initialized")
        if self.engine is not None and self.engine_generation != getattr(
            self.engine, "_generation", 0
        ):
            raise RuntimeError(
                f"{operation} failed: buffer belongs to an old AOT runtime "
                "generation"
            )
        return runtime, handle

    def to_numpy(self, out=None):
        """Read GPU data. Automatically handles staging for VRAM-only buffers."""
        _heartbeat()
        if self.engine is not None:
            self.engine._assert_native_context_owner("to_numpy")
        if out is None:
            out = np.empty(self.shape, dtype=self.dtype)
        elif out.shape != self.shape or out.dtype != self.dtype:
            raise ValueError(
                f"Output array must have shape={self.shape} dtype={self.dtype}, "
                f"got shape={out.shape} dtype={out.dtype}"
            )
        runtime, handle = self._require_live("GPU readback")
        engine = self.engine
        if engine and hasattr(engine, "_lock"):
            _lock_wait_begin("to_numpy")
            with engine._lock:
                _lock_wait_end()
                if self.host_accessible:
                    _op_begin("read_from_gpu_buffer")
                    try:
                        _LIB.read_from_gpu_buffer(
                            runtime, handle, out.ctypes.data, self.size_bytes
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
                                runtime, handle, staging.handle, self.size_bytes
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
                        runtime, handle, out.ctypes.data, self.size_bytes
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
        if self.engine is not None:
            self.engine._assert_native_context_owner("map")
        runtime, handle = self._require_live("GPU buffer map")
        if self.engine and hasattr(self.engine, "_lock"):
            with self.engine._lock:
                return _LIB.map_gpu_buffer(runtime, handle)
        return _LIB.map_gpu_buffer(runtime, handle)

    def unmap(self):
        if self.engine is not None:
            self.engine._assert_native_context_owner("unmap")
        runtime, handle = self._require_live("GPU buffer unmap")
        if self.engine and hasattr(self.engine, "_lock"):
            with self.engine._lock:
                _LIB.unmap_gpu_buffer(runtime, handle)
        else:
            _LIB.unmap_gpu_buffer(runtime, handle)

    def cast(self, target_dtype, host_accessible=False):
        self_dtype_type = np.dtype(self.dtype).type
        target_dtype_type = np.dtype(target_dtype).type
        if self_dtype_type == target_dtype_type:
            return self
        # Keep i16 on the native bridge path as well.  f16 intentionally
        # remains on the NumPy route until a portable half-conversion contract
        # is available for every desktop and ARM toolchain.
        dtype_map = {
            np.float32: 0,
            np.int32: 1,
            np.uint8: 2,
            np.uint16: 3,
            np.int16: 4,
        }
        native_cast_pairs = {
            (0, 2),  # f32 -> u8
            (2, 0),  # u8 -> f32
            (0, 3),  # f32 -> u16
            (3, 0),  # u16 -> f32
            (1, 2),  # i32 -> u8
            (1, 3),  # i32 -> u16
            (0, 4),  # f32 -> i16
            (4, 0),  # i16 -> f32
            (4, 4),  # i16 -> i16 (copy)
        }
        # Native OpenGL buffer mapping is driver-dependent: several Windows
        # ICDs expose a non-coherent pointer for host-visible storage, so a
        # direct bridge cast can observe stale/undefined bytes.  Preserve
        # correctness by taking the synchronized NumPy path on OpenGL; CPU,
        # Vulkan, and CUDA host-visible allocations keep the native path.
        native_host_cast = str(getattr(self.engine, "arch", "")).lower() not in {
            "opengl",
            "gles",
        }
        cast_pair = (
            dtype_map.get(self_dtype_type),
            dtype_map.get(target_dtype_type),
        )
        if (
            self_dtype_type not in dtype_map
            or target_dtype_type not in dtype_map
            or cast_pair not in native_cast_pairs
            or not native_host_cast
            or not self.host_accessible
            or not host_accessible
        ):
            source = self.to_numpy()
            # Match the defined native f32->i16 bridge contract even when
            # OpenGL must use a synchronized host conversion.  NumPy's direct
            # cast wraps out-of-range values and maps NaN differently, which
            # would make backend switching alter compact intermediate data.
            if cast_pair == (0, 4):
                source = np.nan_to_num(
                    source,
                    nan=-32768.0,
                    posinf=32767.0,
                    neginf=-32768.0,
                )
                converted = np.clip(source, -32768.0, 32767.0).astype(np.int16)
            else:
                converted = source.astype(target_dtype)
            return self.engine.upload(converted)

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
            runtime = (
                getattr(engine, "runtime", None) if engine is not None else _RUNTIME
            )
            if (
                _LIB is not None
                and runtime
                and not getattr(engine, "_destroyed", False)
            ):
                _LIB.destroy_aot_module(module_ptr)
        except Exception:
            pass
        finally:
            self.module_ptr = None

    def run(self, graph_name, **kwargs):
        """Menjalankan grafik Taichi AOT dengan validasi argumen yang informatif."""
        engine = self.engine if self.engine is not None else AOTEngine()
        engine._assert_native_context_owner(f"run:{graph_name}")
        if getattr(engine, "_destroyed", False) or not getattr(engine, "runtime", None):
            raise RuntimeError(
                f"AOT runtime for graph '{graph_name}' is no longer active; "
                "reacquire the engine/module after lifecycle reset"
            )
        if not self.module_ptr:
            raise RuntimeError(
                f"AOT module for graph '{graph_name}' is no longer valid"
            )
        if getattr(self, "engine_generation", None) != getattr(
            engine, "_generation", 0
        ):
            raise RuntimeError(
                f"AOT module for graph '{graph_name}' belongs to an old runtime "
                "generation; reload the module after reinitialization"
            )
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

        # Refresh once per graph dispatch.  The pipeline admission branch
        # below used to refresh the governor a second time after acquiring
        # the engine lock; ``MemoryGovernor`` already rate-limits device/RAM
        # sampling, so the duplicate call only added lock/bookkeeping work
        # without changing the decision.  Reuse this snapshot for the same
        # dispatch.  A later graph gets a fresh call, preserving adaptive
        # pressure updates for long-running scopes.
        memory_decision = engine._refresh_memory_policy()
        start_wait = time.perf_counter()
        while True:
            with engine._lock:
                active_recording = next(
                    (
                        item
                        for item in tuple(
                            getattr(engine, "_pipeline_recordings", {}).values()
                        )
                        if item.get("active", False)
                    ),
                    None,
                )
                current_pipeline = engine.current_pipeline
            if (
                active_recording is None
                or current_pipeline is not None
                or active_recording.get("owner_thread") == threading.get_ident()
            ):
                break
            if time.perf_counter() - start_wait > 5.0:
                raise RuntimeError(
                    "AOT graph dispatch cannot overlap a pipeline recording owned "
                    "by another thread (timed out waiting for recording to complete)"
                )
            time.sleep(0.005)
        engine._auto_pipeline_before_run(graph_name, kwargs)
        if engine.current_pipeline:
            pipeline_name = engine.current_pipeline
            recording = getattr(engine, "_pipeline_recordings", {}).get(pipeline_name)
            if (
                recording is None
                or not recording.get("active", False)
                or recording.get("owner_thread") != threading.get_ident()
                or recording.get("generation") != getattr(engine, "_generation", 0)
            ):
                # A stale thread-local marker must never append work to a
                # native graph from another owner or runtime generation.
                engine.current_pipeline = None
                raise RuntimeError(
                    f"AOT pipeline '{pipeline_name}' is no longer owned by "
                    "the current recording scope"
                )
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
                decision = memory_decision
                limit = (
                    int(decision.pipeline_resident_limit)
                    if decision is not None
                    else 512 * 1024 * 1024
                )
                resident = sum(
                    int(getattr(buf, "size_bytes", getattr(buf, "nbytes", 0)) or 0)
                    for buf in engine._pipeline_intermediates.get(
                        engine.current_pipeline, []
                    )
                )
                if limit > 0 and resident > limit:
                    state = getattr(engine._local, "auto_pipeline_context", None)
                    if state and state.get("mode") in {"recorded", "segmented"}:
                        engine._abort_auto_pipeline(
                            f"resident budget exceeded ({resident} > {limit} bytes)"
                        )
                    else:
                        raise RuntimeError(
                            "AOT pipeline exceeds the adaptive resident-memory "
                            f"limit ({resident} > {limit} bytes); "
                            f"recommended block size is "
                            f"{getattr(decision, 'recommended_block_size', 512)}."
                        )

                if engine.current_pipeline:
                    engine._auto_pipeline_capture_call(self, graph_name, kwargs)
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
                    #     and os.environ.get("AOT_INTEL_UNSAFE") == "1"
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
        """Submit a serialized-safe async job.

        The executor avoids blocking the caller, but the native bridge still
        holds the engine lock through ``run`` and ``sync``.  Therefore this is
        not advertised as overlapping GPU dispatch; true overlap requires a
        backend queue/fence proof and remains a future capability.
        """
        _heartbeat()
        engine = self.engine if self.engine is not None else AOTEngine()

        def _rejected(exc):
            # ``async_run`` historically returned a Future even when the
            # native job later failed.  Preserve that contract for lifecycle
            # and queue admission errors while still surfacing the cause via
            # ``Future.result()``.
            rejected = Future()
            rejected.set_exception(exc)
            return rejected

        with engine._lock:
            if getattr(engine, "_destroyed", False) or not getattr(
                engine, "runtime", None
            ):
                return _rejected(
                    RuntimeError(
                        "Cannot submit async AOT work after the runtime has been "
                        "destroyed or reinitialized"
                    )
                )
            if getattr(engine, "_executor", None) is None:
                engine._executor = ThreadPoolExecutor(max_workers=8)
            pending = getattr(engine, "_async_futures", None)
            if pending is None:
                pending = set()
                engine._async_futures = pending
            # Completed futures may still be waiting for their callback when
            # a caller submits the next job.  Prune them before applying the
            # admission limit; the callback remains the authoritative cleanup
            # path for futures that complete concurrently.
            pending.difference_update(
                {future for future in tuple(pending) if future.done()}
            )
            limit = max(
                1,
                int(
                    getattr(
                        engine,
                        "_async_pending_limit",
                        _MAX_ASYNC_PENDING,
                    )
                    or _MAX_ASYNC_PENDING
                ),
            )
            reservations = int(getattr(engine, "_async_reservations", 0) or 0)
            if len(pending) + reservations >= limit:
                rejected = Future()
                rejected.set_exception(
                    RuntimeError(
                        "AOT async submission queue is full "
                        f"({len(pending) + reservations}/{limit}); wait for an earlier future "
                        "before submitting more work"
                    )
                )
                return rejected
            # Reserve a slot before releasing the lock to build the closure.
            # Without this token two caller threads can both pass admission
            # before either one has inserted its Future into ``pending``.
            engine._async_reservations = reservations + 1
            generation = getattr(engine, "_generation", 0)

        def _run_and_sync(submission_generation=generation):
            with engine._lock:
                if (
                    getattr(engine, "_destroyed", False)
                    or getattr(engine, "_generation", 0) != submission_generation
                ):
                    raise RuntimeError(
                        "Async AOT submission belongs to an invalidated runtime "
                        "generation"
                    )
                planner = getattr(engine, "_auto_pipeline_planner", None)
                if planner is not None:
                    try:
                        planner.observe(
                            {
                                "async_serialized": 1,
                                "overlap_verified": False,
                            }
                        )
                    except Exception:
                        pass
                self.run(graph_name, **kwargs)
                engine.sync()

        with engine._lock:
            # Recheck the lifecycle immediately before submission.  Keeping
            # submit() under the same lock as admission prevents destroy() or
            # reinit() from racing between executor admission and future
            # registration, which would otherwise leave an untracked task.
            try:
                if (
                    getattr(engine, "_destroyed", False)
                    or getattr(engine, "_generation", 0) != generation
                ):
                    return _rejected(
                        RuntimeError(
                            "AOT runtime changed while an async submission was being "
                            "admitted"
                        )
                    )
                future = engine._executor.submit(_run_and_sync)
                # The engine may be destroyed after this point; retaining the
                # future here lets destroy() cancel queued work deterministically.
                getattr(engine, "_async_futures", set()).add(future)
            finally:
                engine._async_reservations = max(
                    0, int(getattr(engine, "_async_reservations", 0) or 0) - 1
                )

            def _release(done):
                try:
                    with engine._lock:
                        futures = getattr(engine, "_async_futures", None)
                        if futures is not None:
                            futures.discard(done)
                except Exception:
                    # Interpreter teardown may already have released locks;
                    # the Future itself remains valid for the caller.
                    pass

            future.add_done_callback(_release)
        return future

    def _dummy_run(self):
        pass  # For keeping refs if needed


class AOTEngine:
    _instances = {}
    _active_arch = "vulkan"
    _placeholder_id_counter = 0xFFFFFF00

    def __new__(cls, arch=None, device_id=None):
        global _OPENGL_VENDOR_INJECTED
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
        if arch.lower() in ("cpu", "opengl", "gles"):
            device_id = 0
            os.environ["AOT_DEVICE"] = "0"

        if arch.lower() == "opengl":
            # The native ICD bridge reads its vendor filter during context
            # creation (before the Python post-init renderer check).  Prop-
            # agate the stable target selection into that filter so an Intel
            # request does not accidentally win NVIDIA merely because the
            # driver enumeration order puts NVIDIA first.
            requested_vendor = os.environ.get("TARGET_VENDOR", "")
            current_vendor = os.environ.get("OPENGL_EXPECTED_VENDOR", "")
            # If the value was injected by a previous backend selection, it is
            # safe to replace it when the user changes vendor in-process.  A
            # value supplied explicitly by an embedding application remains
            # authoritative.
            if requested_vendor and (
                not current_vendor or current_vendor == _OPENGL_VENDOR_INJECTED
            ):
                os.environ["OPENGL_EXPECTED_VENDOR"] = requested_vendor
                _OPENGL_VENDOR_INJECTED = requested_vendor

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
                "gles": 4,
            }.get(arch.lower(), 0)
            native_device_id = int(device_id)
            if arch.lower() in ("cpu", "opengl", "gles") and native_device_id != 0:
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
            if arch.lower() in ("opengl", "gles", "cuda"):
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
                    f"  HINT: Kill zombie processes or set INIT_TIMEOUT to increase limit.\n"
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
                    "OPENGL_EXPECTED_VENDOR",
                    os.environ.get("TARGET_VENDOR", ""),
                )
                expected_name = os.environ.get("OPENGL_EXPECTED_NAME", "")
                if not _opengl_renderer_matches_vendor(gpu_name, expected_vendor):
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
                        print(f"[AOTEngine] OpenGL context provider: {context_backend}")
                # Intel's legacy native Vulkan allocator (not Dozen) can assert
                # during Taichi context teardown when AOT memory blocks are
                # still tracked internally.  Keep the process alive by letting
                # the OS reclaim the context instead of calling the faulty
                # destructor; this is scoped to Intel and never affects NVIDIA.
                if (
                    arch.lower() in ("vulkan", "opengl")
                    and "intel" in gpu_name.lower()
                    and "microsoft" not in gpu_name.lower()
                ):
                    os.environ.setdefault("AOT_SAFE_TEARDOWN", "1")
                    # TEMPORARILY DISABLED: setting this flag previously made
                    # every unqualified Intel Vulkan graph fail before dispatch.
                    # os.environ.setdefault("AOT_INTEL_UNSAFE", "1")
                    os.environ.setdefault("VULKAN_SERIALIZE_SUBMIT", "1")
            else:
                print(
                    f"[AOTEngine] Runtime initialized on '{arch.upper()}' (Device {device_id})"
                )

            instance.gpu_name = gpu_name or ""
            instance._graphics_compatibility_mode = _graphics_compatibility_enabled(
                arch, normalize_vendor(gpu_name or config.vendor)
            )
            if instance._graphics_compatibility_mode:
                # Legacy integrated Vulkan drivers require host-visible storage
                # for buffers that cross the Python/C-API boundary.  Keeping
                # every allocation in that domain also avoids the invalid
                # device-local ti_map_memory path without changing algorithms
                # or silently moving execution to CPU.
                instance._force_host_accessible = True
                print(
                    "[AOTEngine] Legacy graphics compatibility active: "
                    "host-visible buffers, serialized direct graph dispatch."
                )
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
            # Buffers released while a native queue may still reference them
            # remain here until the next runtime synchronization.  This keeps
            # host-visible upload allocations reusable without permitting a
            # GPU command to observe a handle that has already been recycled.
            instance._retired_buffers = []
            instance._retired_bytes = 0
            instance._retired_buffer_budget = _DEFAULT_RETIRED_BUFFER_BUDGET
            instance._staging_pool_budget = _DEFAULT_STAGING_POOL_BUDGET
            instance._staging_pool_max_entries = _MAX_STAGING_POOL_ENTRIES
            instance._buffer_cache_enabled = (
                os.environ.get("AOT_BUFFER_CACHE", "1") != "0"
            )
            instance._pipeline_intermediates = {}
            instance.recorded_pipelines = set()
            # A pipeline name is a native global resource, while
            # ``current_pipeline`` is thread-local for backward compatibility.
            # Keep an engine-level ownership table so two recording scopes
            # cannot clear/overwrite the same native graph concurrently.
            instance._pipeline_recordings = {}
            # Automatic pipeline metadata is kept per thread at dispatch time;
            # this engine-level slot makes lifecycle/reset behavior explicit.
            instance._auto_pipeline_context = None
            instance._live_buffers = weakref.WeakSet()
            instance._executor = None
            instance._async_futures = set()
            instance._async_reservations = 0
            instance._async_pending_limit = _MAX_ASYNC_PENDING
            instance._lock = threading.RLock()
            # Windows OpenGL/GLES ICD contexts are thread-affine.  The native
            # bridge does not provide a context migration/dispatch queue, so
            # retain the creating thread and fail closed before a worker can
            # turn a context error into a misleading allocation failure.
            instance._native_context_owner_thread_id = (
                threading.get_ident()
                if arch.lower() in {"opengl", "gles"}
                else None
            )
            instance._destroyed = False
            instance._generation = 0
            instance._block_config = BlockConfig()
            instance._block_plan_stats = {
                "automatic": 0,
                "explicit": 0,
                "full_frame": 0,
                "full_frame_threshold": 0,
                "full_frame_dependency": 0,
                "full_frame_halo": 0,
                "full_frame_quarantine": 0,
            }
            instance._block_plan_stats_lock = threading.Lock()
            instance._block_quarantine = {}
            instance._cache_telemetry = CacheTelemetry()
            instance._device_memory_provider = (
                (
                    lambda selected_id=int(device_id): query_vulkan_memory_budget(
                        selected_id
                    )
                )
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
                unsafe_backends=(
                    {str(arch).lower()}
                    if instance._graphics_compatibility_mode
                    else ()
                ),
            )
            initial_memory = instance._memory_governor.refresh(force=True)
            instance.buffer_pool.set_budget(initial_memory.device_pool_budget)
            instance._apply_lifecycle_limits(initial_memory, trim=False)
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

    def _free_buffer_handle(self, handle):
        """Free one native handle while the engine lock is already held."""
        if handle is None:
            return
        if getattr(self, "arch", "").lower() == "cuda":
            ensure_cuda_context(getattr(self, "device_id", 0))
        runtime = getattr(self, "runtime", None)
        if _LIB and runtime:
            try:
                _LIB.free_gpu_buffer(runtime, handle)
            except Exception:
                pass

    def _invalidate_live_buffers(self, runtime=None):
        """Invalidate every wrapper before its native runtime is replaced.

        ``reinit()`` and ``destroy()`` used to clear the staging/pipeline
        dictionaries but leave ordinary user-owned wrappers in
        ``_live_buffers``.  Their Python objects could then call ``destroy``
        against a new runtime generation, where the old numeric handle was
        no longer valid.  A single synchronized sweep keeps the ownership
        contract explicit for all buffer classes (full-frame, block,
        staging, and pipeline intermediates).

        The caller owns the engine lock.  ``runtime`` is deliberately
        explicit so a teardown can release handles against the old context
        before replacing ``self.runtime``.
        """
        runtime = runtime if runtime is not None else getattr(self, "runtime", None)
        if not (_LIB and runtime):
            for buffer in list(getattr(self, "_live_buffers", ())):
                buffer.handle = None
                buffer.is_owner = False
                buffer.associated_pipelines.clear()
            return

        freed = set()
        for buffer in list(getattr(self, "_live_buffers", ())):
            handle = getattr(buffer, "handle", None)
            if handle is not None and getattr(buffer, "is_owner", False):
                # A handle should have one owner, but guarding against a
                # duplicate prevents a double-free if a caller retained an
                # alias while a pipeline was being torn down.
                raw_token = getattr(handle, "value", handle)
                token = int(raw_token or 0)
                if token not in freed:
                    try:
                        _LIB.free_gpu_buffer(runtime, handle)
                    except Exception:
                        # Context teardown is best-effort; the wrapper is
                        # still invalidated below so it cannot touch a stale
                        # handle later.
                        pass
                    freed.add(token)
            buffer.handle = None
            buffer.is_owner = False
            buffer.associated_pipelines.clear()
            buffer.is_pipeline_intermediate = False

    def _apply_lifecycle_limits(self, decision=None, *, trim=True):
        """Apply governor limits to staging and queue-retired allocations.

        These limits are bookkeeping only: a leased staging buffer or a
        handle still referenced by the native queue is never freed early.
        Idle staging entries are trimmed immediately; retired entries are
        drained (with one safe-point wait) only when their bounded queue is
        over budget.
        """
        if decision is None:
            staging_budget = getattr(
                self, "_staging_pool_budget", _DEFAULT_STAGING_POOL_BUDGET
            )
            retired_budget = getattr(
                self, "_retired_buffer_budget", _DEFAULT_RETIRED_BUFFER_BUDGET
            )
        else:
            staging_budget = getattr(
                decision, "staging_pool_budget", _DEFAULT_STAGING_POOL_BUDGET
            )
            retired_budget = getattr(
                decision, "retired_buffer_budget", _DEFAULT_RETIRED_BUFFER_BUDGET
            )
        self._staging_pool_budget = max(0, int(staging_budget or 0))
        self._retired_buffer_budget = max(0, int(retired_budget or 0))
        self._staging_pool_max_entries = max(
            1,
            int(getattr(self, "_staging_pool_max_entries", _MAX_STAGING_POOL_ENTRIES)),
        )
        if not trim:
            return
        # Callers that explicitly opt into ``trim`` must already be at a
        # native synchronization safe point. The hot refresh path passes
        # ``trim=False`` so it never frees an asynchronously referenced host
        # buffer.
        self._trim_staging_pool()
        if (
            int(getattr(self, "_retired_bytes", 0) or 0) > self._retired_buffer_budget
            or len(getattr(self, "_retired_buffers", ())) > _MAX_RETIRED_BUFFERS
        ):
            # This is a safe frame/batch boundary.  A single native wait lets
            # the queue release every retired handle; ``BufferPool`` still
            # enforces its own byte budget while promoting them.
            self._drain_retired(wait=True)

    def _trim_staging_pool(self):
        """Evict oldest idle staging entries until count/bytes are bounded."""
        pool = getattr(self, "_staging_pool", None)
        if not pool:
            return 0
        removed = 0
        with self._lock:

            def entries():
                for key, bucket in tuple(pool.items()):
                    for entry in tuple(bucket):
                        yield key, bucket, entry

            def totals():
                all_entries = list(entries())
                return len(all_entries), sum(
                    int(getattr(item.get("buffer"), "size_bytes", 0) or 0)
                    for _, _, item in all_entries
                )

            while True:
                count, resident = totals()
                if count <= int(
                    getattr(
                        self, "_staging_pool_max_entries", _MAX_STAGING_POOL_ENTRIES
                    )
                ) and resident <= int(
                    getattr(self, "_staging_pool_budget", _DEFAULT_STAGING_POOL_BUDGET)
                ):
                    break
                candidates = [
                    (float(item.get("last_used", 0.0) or 0.0), key, bucket, item)
                    for key, bucket, item in entries()
                    if not item.get("leased", False)
                ]
                if not candidates:
                    # All entries are in use; defer eviction until release.
                    break
                _, key, bucket, entry = min(candidates, key=lambda item: item[0])
                try:
                    bucket.remove(entry)
                except ValueError:
                    continue
                if not bucket:
                    pool.pop(key, None)
                buf = entry.get("buffer")
                if buf is not None:
                    try:
                        buf._force_destroy()
                    except Exception:
                        # Teardown is best effort; dropping the pool reference
                        # still prevents unbounded Python-side growth.
                        try:
                            buf.handle = None
                            buf.is_owner = False
                        except Exception:
                            pass
                removed += 1
        return removed

    def _retire_buffer(self, buffer):
        """Retire a wrapper without reusing its handle before queue completion."""
        handle = getattr(buffer, "handle", None)
        if handle is None or not getattr(buffer, "is_owner", False):
            return
        with self._lock:
            handle = getattr(buffer, "handle", None)
            if handle is None or not getattr(buffer, "is_owner", False):
                return
            buffer.handle = None
            buffer.is_owner = False
            key = buffer._buffer_key()
            # During teardown or when explicitly disabled, release directly.
            if getattr(self, "_destroyed", False) or not getattr(
                self, "_buffer_cache_enabled", True
            ):
                self._free_buffer_handle(handle)
                return
            self._retired_buffers.append((key, handle))
            self._retired_bytes += key.size_bytes
            if (
                self._retired_bytes
                > int(
                    getattr(
                        self, "_retired_buffer_budget", _DEFAULT_RETIRED_BUFFER_BUDGET
                    )
                )
                or len(self._retired_buffers) > _MAX_RETIRED_BUFFERS
            ):
                # Never leave an over-budget queue alive indefinitely.  This
                # wait is only reached on an explicit lifecycle trim/safe
                # point, not for unrelated allocation keys.
                self._drain_retired(wait=True)

    def _drain_retired(self, *, wait=False, already_synchronized=False, key=None):
        """Move retired handles to the pool after native work is complete.

        When ``key`` is supplied, only that allocation class is promoted.  A
        missing key does not trigger a global queue wait, which keeps a fresh
        allocation from synchronizing behind an unrelated retired buffer.
        """
        if not getattr(self, "_retired_buffers", None):
            return
        with self._lock:
            if not self._retired_buffers:
                return
            if key is None:
                selected = list(self._retired_buffers)
                remaining = []
            else:
                selected = [item for item in self._retired_buffers if item[0] == key]
                if not selected:
                    return
                remaining = [item for item in self._retired_buffers if item[0] != key]
            backend = str(getattr(self, "arch", "")).lower()
            owner = getattr(self, "_native_context_owner_thread_id", None)
            is_non_owner_opengl = backend in {"opengl", "gles"} and owner is not None and threading.get_ident() != owner

            sync_failed = False
            if wait and not already_synchronized and not is_non_owner_opengl:
                _op_begin("sync_runtime:retired_buffers")
                try:
                    if _LIB is not None and getattr(self, "runtime", None):
                        _LIB.sync_runtime(self.runtime)
                except (OSError, RuntimeError, ctypes.ArgumentError) as exc:
                    # A backend can invalidate its native context while Python
                    # still owns retired wrapper objects (most often during
                    # driver reset/atexit).  Do not let cleanup turn that
                    # recoverable lifecycle race into an access-violation
                    # traceback.  Handles from a failed sync are deliberately
                    # discarded: returning them to the pool could reuse a
                    # buffer owned by a dead context.
                    sync_failed = True
                    if os.environ.get("AOT_VERBOSE_CLEANUP") == "1":
                        print(
                            "[AOTEngine] Retired-buffer sync failed; "
                            f"discarding {len(selected)} stale handle(s): {exc}"
                        )
                finally:
                    _op_end()
            self._retired_buffers = remaining
            self._retired_bytes = sum(item[0].size_bytes for item in remaining)
            if not sync_failed:
                for retired_key, handle in selected:
                    self.buffer_pool.store(retired_key, handle)

    def _buffer_pool_key(self, size, dtype, *, host_accessible, is_vector, vector_dim):
        return BufferKey(
            size,
            host_accessible=host_accessible,
            dtype=np.dtype(dtype).str,
            is_vector=is_vector,
            vector_dim=vector_dim,
        )

    def placeholder(self, shape, dtype=np.float32, is_vector=False, vector_dim=3):
        p = TaichiPlaceholder(
            self._placeholder_id_counter, shape, dtype, is_vector, vector_dim
        )
        self._placeholder_id_counter += 1
        return p

    def _resolve_pipeline_module(self, module_key=None):
        """Resolve a loaded AOT module for an automatic segment key.

        ``GraphSpec.module_key`` uses stable family names (``canny``,
        ``pyramid``, ...), while ``self.modules`` is keyed by the concrete
        artifact path.  Keep this lookup best-effort: a missing key falls back
        to the historical first-loaded module and never changes public module
        loading semantics.
        """
        modules = getattr(self, "modules", {}) or {}
        if module_key is not None:
            key = str(module_key).strip().lower().replace("-", "_")
            aliases = {key}
            if key.endswith("_batch"):
                aliases.add(key[: -len("_batch")])
            for path, module in modules.items():
                logical_key = (
                    str(getattr(module, "logical_key", "") or "").strip().lower()
                )
                logical_key = logical_key.replace("-", "_")
                if logical_key in aliases:
                    return module
                stem = os.path.splitext(os.path.basename(str(path)))[0].lower()
                stem = stem.replace("-", "_")
                if any(
                    stem == alias or stem.startswith(alias + "_") for alias in aliases
                ):
                    return module
            # A requested family key that cannot be mapped must not silently
            # bind its recording to another loaded module.  The caller can
            # safely keep the segment on direct same-backend dispatch.
            return None
        return next(iter(modules.values()), None) if modules else None

    def rec_pipeline(self, name, *, module_key=None):
        # Pipeline selection is automatic.  OpenGL recording is allowed by
        # default; per-stage capability checks and the resident-memory guard
        # below decide whether a graph can remain native.  The historical
        # AOT_NATIVE_PIPELINE switch remains a compatibility
        # override, but is no longer required for normal developer usage.
        auto_pipeline = (
            self.arch.lower() in ("opengl", "gles")
            and os.environ.get("AOT_NATIVE_PIPELINE") != "1"
        )
        name = str(name)
        if not name:
            raise ValueError("Pipeline name must not be empty")

        class Recorder:
            def __init__(self, engine, name, module_key=None):
                self.engine, self.name = engine, name
                self.module_key = module_key
                self._owner_thread = None
                self._generation = None
                self._token = object()
                self._entered = False

            def __enter__(self):
                owner = threading.get_ident()
                with self.engine._lock:
                    if getattr(self.engine, "_destroyed", False) or not getattr(
                        self.engine, "runtime", None
                    ):
                        raise RuntimeError(
                            "Cannot record a pipeline on an inactive AOT runtime"
                        )
                    if self.engine.current_pipeline is not None:
                        raise RuntimeError(
                            "Nested AOT pipeline recordings are not supported; "
                            f"finish '{self.engine.current_pipeline}' first"
                        )
                    recordings = getattr(self.engine, "_pipeline_recordings", None)
                    if recordings is None:
                        recordings = {}
                        self.engine._pipeline_recordings = recordings
                    active = next(
                        (
                            item
                            for item in recordings.values()
                            if item.get("active", False)
                        ),
                        None,
                    )
                    if active is not None:
                        raise RuntimeError(
                            "Another AOT pipeline is currently being recorded "
                            f"('{active.get('name', '<unknown>')}'); "
                            "recording scopes must not overlap"
                        )
                    previous = recordings.get(self.name)
                    if previous is not None and previous.get("active", False):
                        raise RuntimeError(
                            f"Pipeline '{self.name}' is already being recorded"
                        )
                    module = self.engine._resolve_pipeline_module(self.module_key)
                    if self.module_key is not None and module is None:
                        raise RuntimeError(
                            f"AOT module key '{self.module_key}' is not loaded; "
                            "segmented recording remains direct"
                        )
                    _LIB.clear_pipeline(
                        module.module_ptr if module else None,
                        self.name.encode("utf-8"),
                    )
                    # Clear previous intermediates for this pipeline only after
                    # the native graph has been invalidated.  Handles associated
                    # with a prior generation are never allowed into a fresh
                    # recording.
                    if self.name in self.engine._pipeline_intermediates:
                        for buf in self.engine._pipeline_intermediates[self.name]:
                            buf._force_destroy()
                        del self.engine._pipeline_intermediates[self.name]
                    self.engine.current_pipeline = self.name
                    self.engine.recorded_pipelines.add(self.name)
                    self.engine._auto_pipeline_active = auto_pipeline
                    self._owner_thread = owner
                    self._generation = getattr(self.engine, "_generation", 0)
                    recordings[self.name] = {
                        "name": self.name,
                        "owner_thread": owner,
                        "generation": self._generation,
                        "active": True,
                        "token": self._token,
                    }
                    self._entered = True
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                owner = threading.get_ident()
                with self.engine._lock:
                    recordings = getattr(self.engine, "_pipeline_recordings", {})
                    record = recordings.get(self.name)
                    owns_record = bool(
                        self._entered
                        and record is not None
                        and record.get("token") is self._token
                        and record.get("owner_thread") == owner
                        and record.get("generation")
                        == getattr(self.engine, "_generation", 0)
                    )
                    if owns_record:
                        record["active"] = False
                        record["closed"] = True
                        if self.engine.current_pipeline == self.name:
                            self.engine.current_pipeline = None
                        # A failed recording must never remain executable as an
                        # apparently complete native graph.  Clear the
                        # compatibility slot and its intermediate leases at
                        # the scope boundary; successful recordings retain
                        # the historical ``use_pipeline(name)`` behavior.
                        if exc_type is not None:
                            self.engine._drop_pipeline_recording(self.name)
                    elif self.engine.current_pipeline == self.name:
                        # Do not leave a thread-local recording marker behind
                        # after a generation reset or an exceptional teardown.
                        self.engine.current_pipeline = None
                self._entered = False
                return False

        return Recorder(self, name, module_key=module_key)

    @staticmethod
    def _auto_pipeline_segment_recordable(segment):
        """Return whether a planned segment is safe to record as one graph.

        The planner already rejects incomplete graph metadata, but this guard
        is intentionally repeated at the runtime boundary: callers can hold a
        stale ``PipelinePlan`` or mutate a mapping before it reaches
        ``auto_pipeline``.  A one-graph segment is always direct because the
        recorder has no amortization benefit.
        """
        if segment is None or len(segment) < 2:
            return False
        for spec in segment:
            metadata = getattr(spec, "metadata", {}) or {}
            if metadata.get("_implicit_graph_name"):
                return False
            if int(getattr(spec, "resident_bytes", 0) or 0) <= 0:
                return False
            if not bool(getattr(spec, "backend_safe", True)):
                return False
        return True

    def _auto_pipeline_capture_call(self, module, graph_name, values):
        """Capture a replayable call while a segmented recorder is active.

        Recording is an optimization and can fail at ``use_pipeline`` after
        the Python caller has already issued all graph calls.  Keeping the
        module wrapper, graph name, and argument objects lets the engine replay
        that segment through direct same-backend dispatch without changing a
        public algorithm signature.  Only segmented scopes capture calls;
        existing one-big-graph scopes retain their established caller-owned
        fallback behavior.
        """
        state = getattr(self._local, "auto_pipeline_context", None)
        if not state or state.get("mode") != "segmented":
            return
        if state.get("replaying") or not state.get("recording_active"):
            return
        calls = state.setdefault("replay_calls", [])
        calls.append((module, str(graph_name), dict(values or {})))

    def _auto_pipeline_replay_segment(self, state, calls):
        """Replay one failed segment directly on the selected backend."""
        if not calls:
            return
        state["replaying"] = True
        try:
            for module, graph_name, values in tuple(calls):
                module.run(graph_name, **dict(values))
        finally:
            state["replaying"] = False

    @staticmethod
    def _auto_pipeline_replay_allowed(error) -> bool:
        """Return whether an exception should trigger same-backend replay.

        A recorder/submit failure must replay its already-issued calls to keep
        correctness.  User cancellation is different: replaying a cancelled
        segment would silently undo the caller's request and can re-run a
        costly full-frame operation.  Treat the standard cancellation/control
        flow exceptions as terminal cleanup while preserving replay for
        ordinary algorithm errors and native recording failures.
        """
        if isinstance(error, (KeyboardInterrupt, SystemExit, GeneratorExit)):
            return False
        name = type(error).__name__.strip().lower().lstrip("_")
        if (
            name in {"cancellederror", "cancellationerror", "cancelederror"}
            or "cancel" in name
        ):
            return False
        message = str(error).strip().lower()
        if any(
            token in message
            for token in (
                "old runtime generation",
                "stale runtime generation",
                "runtime generation",
                "was invalidated",
            )
        ):
            # Handles from an old runtime cannot be replayed on the selected
            # backend.  Cleanup is still mandatory, but retrying would merely
            # raise the same stale-generation error (or target a stale handle).
            return False
        return not bool(getattr(error, "cancelled", False))

    def _auto_pipeline_begin_segment(self, state, segment_index):
        """Start recording a qualified segment or leave it direct."""
        segments = tuple(state.get("segments", ()))
        if segment_index < 0 or segment_index >= len(segments):
            state["active_segment"] = segment_index
            state["recording_active"] = False
            state["active_recorder"] = None
            state["replay_calls"] = []
            return
        segment = segments[segment_index]
        state["active_segment"] = segment_index
        state["recording_active"] = False
        state["active_recorder"] = None
        state["active_pipeline_name"] = None
        state["replay_calls"] = []
        if not self._auto_pipeline_segment_recordable(segment):
            return

        name = state.get("segment_names", ())[segment_index]
        segment_module_key = getattr(segment[0], "module_key", None)
        if segment_module_key is None:
            metadata = getattr(segment[0], "metadata", {}) or {}
            segment_module_key = metadata.get("module_key", metadata.get("module"))
        recorder = (
            self.rec_pipeline(str(name), module_key=segment_module_key)
            if segment_module_key
            else self.rec_pipeline(str(name))
        )
        try:
            recorder.__enter__()
        except Exception as exc:
            # A recorder admission failure is recoverable before the first
            # graph of the segment: leave the segment on direct dispatch.
            self.current_pipeline = None
            state["segment_recording_error"] = str(exc)
            print(
                f"[AOTEngine Pipeline] segmented recording disabled for "
                f"{name}; using direct same-backend dispatch: {exc}"
            )
            return
        state["active_recorder"] = recorder
        state["active_pipeline_name"] = str(name)
        state["recording_active"] = True

    def _auto_pipeline_finish_segment(self, state, *, error=None, replay=True):
        """Finish, submit, synchronize, and clear one segmented recorder."""
        if not state or state.get("mode") != "segmented":
            return
        recorder = state.get("active_recorder")
        name = state.get("active_pipeline_name")
        calls = tuple(state.get("replay_calls", ()))
        state["active_recorder"] = None
        state["recording_active"] = False
        state["active_pipeline_name"] = None
        state["replay_calls"] = []
        if recorder is None or not name:
            return

        preserve_for_replay = bool(
            error is not None
            and replay
            and calls
            and self._auto_pipeline_replay_allowed(error)
        )
        submit_error = None
        try:
            if error is None or preserve_for_replay:
                # A normal close leaves pipeline intermediates available for
                # the direct same-backend replay below.  Passing the caller's
                # exception to ``Recorder.__exit__`` would eagerly destroy
                # those buffers as part of legacy failed-recording cleanup.
                recorder.__exit__(None, None, None)
            else:
                exc_type = (
                    type(error) if isinstance(error, BaseException) else RuntimeError
                )
                recorder.__exit__(exc_type, error, None)
        except BaseException as exc:
            submit_error = exc

        if error is not None:
            try:
                self._drop_pipeline_recording(
                    name, destroy_intermediates=not preserve_for_replay
                )
            except Exception:
                pass
            if preserve_for_replay:
                self._auto_pipeline_replay_segment(state, calls)
            return

        if error is None and submit_error is None:
            try:
                if name in self.recorded_pipelines:
                    self.use_pipeline(name)
                    # ``use_pipeline`` intentionally warns and returns when a
                    # runtime generation invalidated the recording.  Treat
                    # that as a failed submission here so the captured calls
                    # take the same-backend direct path instead of being lost.
                    if name not in self.recorded_pipelines:
                        raise RuntimeError(
                            f"segmented pipeline '{name}' was invalidated"
                        )
                # Segment boundaries are explicit queue safe points.  This
                # does not establish concurrent queue execution.
                self.sync()
            except BaseException as exc:
                submit_error = exc

        if submit_error is not None:
            try:
                self._drop_pipeline_recording(name, destroy_intermediates=False)
            except Exception:
                pass
            try:
                self.sync()
            except Exception:
                pass
            if replay and calls and self._auto_pipeline_replay_allowed(submit_error):
                print(
                    f"[AOTEngine Pipeline] segmented recording '{name}' "
                    "failed; replaying direct same-backend calls: "
                    f"{submit_error}"
                )
                self._auto_pipeline_replay_segment(state, calls)
            elif error is None:
                raise submit_error
            return

        # A one-shot segment must not remain in ``recorded_pipelines`` after
        # its submission.  Drop only the recording associations; caller-owned
        # buffers stay alive for the next segment.
        try:
            self._drop_pipeline_recording(name, destroy_intermediates=False)
        except Exception:
            pass

    def _auto_pipeline_before_run(self, graph_name, values=None):
        """Advance an active automatic scope before a graph dispatch.

        Segmented plans remain graph-order preserving while synchronization is
        inserted at each planned boundary.  A segment with at least two
        qualified graphs is recorded as a one-shot native pipeline; unknown
        and one-graph segments stay on direct dispatch. An unexpected graph
        degrades to direct dispatch instead of leaving a partially recorded
        pipeline.
        """
        # A small number of Intel desktop OpenGL ICDs can execute the same
        # graphs successfully with direct dispatch but hang when a very wide
        # 16+ MP frame is captured into one recorded pipeline. Detect that
        # shape at the first dispatch and keep the computation full-frame while
        # disabling only the risky recording layer. This is intentionally
        # vendor/shape scoped; NVIDIA and ordinary Intel resolutions retain the
        # faster one-big-graph path. An explicit diagnostic override is
        # available for driver experiments.
        if (
            self.current_pipeline
            and values
            and not any(
                isinstance(value, TaichiPlaceholder) for value in values.values()
            )
            and getattr(self._local, "auto_pipeline_context", None)
            and self._should_bypass_large_intel_pipeline(values)
        ):
            reason = (
                "large/wide Intel OpenGL frame uses direct full-frame dispatch "
                "to avoid driver pipeline hang"
            )
            state = getattr(self._local, "auto_pipeline_context", None)
            if state and not state.get("aborted"):
                self._abort_auto_pipeline(reason)
            else:
                name = self.current_pipeline
                self.current_pipeline = None
                self._drop_pipeline_recording(name)
            self._auto_pipeline_active = False
            try:
                self.sync()
            except Exception:
                pass
            self._pipeline_bypass_reason = reason
            print(f"[AOTEngine Pipeline] {reason}")
            return

        state = getattr(self._local, "auto_pipeline_context", None)
        if not state or state.get("aborted"):
            return
        # Replay is the same-backend recovery path after a segmented pipeline
        # submit failure.  Do not advance the original graph cursor or start a
        # second recorder while replaying its captured calls directly.
        if state.get("replaying"):
            return
        expected = state.get("graph_names", ())
        cursor = int(state.get("cursor", 0))
        if cursor >= len(expected) or str(graph_name) != expected[cursor]:
            self._abort_auto_pipeline(f"unexpected graph order at {graph_name!r}")
            try:
                self.sync()
            except Exception:
                pass
            return
        boundaries = state.get("boundaries", ())
        segment_index = boundaries[cursor] if cursor < len(boundaries) else 0

        if state.get("mode") == "segmented":
            # Finish the preceding segment before starting the next one.  The
            # safe point submits the prior one-shot graph and synchronizes the
            # backend queue; this is sequencing, not overlap proof.
            if state.get("active_segment") != segment_index:
                self._auto_pipeline_finish_segment(state)
                self._auto_pipeline_begin_segment(state, segment_index)
            state["segment_index"] = segment_index
            state["cursor"] = cursor + 1
            return

        if (
            state.get("segment_index") is not None
            and segment_index != state["segment_index"]
        ):
            self.sync()
        state["segment_index"] = segment_index
        state["cursor"] = cursor + 1

    def _should_bypass_large_intel_pipeline(self, values):
        """Return whether a frame shape is unsafe for Intel OpenGL recording.

        The direct path remains full-frame and therefore does not alter image
        semantics.  The guard only avoids a known driver failure mode for
        ultrawide high-resolution dispatches.  It can be disabled for a
        controlled experiment with ``AOT_FORCE_RECORDED_PIPELINE``.
        """
        if os.environ.get("AOT_FORCE_RECORDED_PIPELINE") == "1":
            return False
        for value in values.values():
            shape = getattr(value, "shape", None)
            if self._shape_requires_large_intel_bypass(shape):
                return True
        return False

    def _shape_requires_large_intel_bypass(self, shape):
        """Return whether ``shape`` hits the tested Intel OpenGL hazard."""
        if os.environ.get("AOT_FORCE_RECORDED_PIPELINE") == "1":
            return False
        if str(getattr(self, "arch", "")).lower() != "opengl":
            return False
        identity = " ".join(
            str(item)
            for item in (
                getattr(self, "gpu_name", ""),
                getattr(getattr(self, "_backend_config", None), "vendor", ""),
            )
        ).lower()
        if "intel" not in identity or shape is None:
            return False
        try:
            if len(shape) < 2:
                return False
            height, width = int(shape[0]), int(shape[1])
        except (TypeError, ValueError):
            return False
        pixels = height * width
        short_side = max(1, min(height, width))
        long_side = max(height, width)
        return pixels >= 16_000_000 and (
            long_side >= 6144 or long_side / short_side >= 2.5
        )

    def _drop_pipeline_recording(self, name, *, destroy_intermediates=False):
        """Cancel recording while preserving caller-owned GPU buffers."""
        if not name:
            return
        key = str(name)
        encoded_name = key.encode("utf-8")
        # A recorded graph is owned by the module that first dispatched it;
        # clearing only the legacy global slot can leave backend-local state
        # alive on graphics drivers. Clear both the compatibility slot and
        # every loaded module before switching to direct dispatch.
        try:
            _LIB.clear_pipeline(None, encoded_name)
        except Exception:
            pass
        for module in tuple(getattr(self, "modules", {}).values()):
            module_ptr = getattr(module, "module_ptr", None)
            if not module_ptr:
                continue
            try:
                _LIB.clear_pipeline(module_ptr, encoded_name)
            except Exception:
                pass
        self.recorded_pipelines.discard(key)
        recordings = getattr(self, "_pipeline_recordings", None)
        if recordings is not None:
            recordings.pop(key, None)
        for buf in self._pipeline_intermediates.pop(key, []):
            buf.associated_pipelines.discard(key)
            if destroy_intermediates and getattr(
                buf, "is_pipeline_intermediate", False
            ):
                buf._force_destroy()
            else:
                buf.is_pipeline_intermediate = False

    def _abort_auto_pipeline(self, reason):
        state = getattr(self._local, "auto_pipeline_context", None)
        if not state or state.get("aborted"):
            return
        state["aborted"] = True
        if state.get("mode") == "segmented":
            # Recover any already-captured prefix before abandoning the
            # segmented scope.  The current graph is dispatched directly by
            # the caller after this method returns; no CPU substitution or
            # overlap claim is introduced here.
            try:
                self._auto_pipeline_finish_segment(
                    state,
                    error=RuntimeError(str(reason)),
                    replay=True,
                )
            finally:
                try:
                    self.sync()
                except Exception:
                    pass
            print(f"[AOTEngine Pipeline] automatic recording disabled: {reason}")
            return
        name = state.get("name")
        if self.current_pipeline:
            # Flush the already-recorded prefix before abandoning the
            # recording. Dropping it silently would lose earlier graph
            # results when a later allocation crosses the adaptive limit.
            active_name = name or self.current_pipeline
            self.current_pipeline = None
            recording = getattr(self, "_pipeline_recordings", {}).get(active_name)
            if recording is not None:
                # The prefix is submitted as a completed graph before its
                # native entry is dropped.  Mark it closed first so
                # ``use_pipeline`` cannot mistake this controlled transition
                # for an overlapping recording scope.
                recording["active"] = False
                recording["aborted"] = True
            try:
                if active_name in self.recorded_pipelines:
                    self.use_pipeline(active_name)
            finally:
                self._drop_pipeline_recording(active_name)
        print(f"[AOTEngine Pipeline] automatic recording disabled: {reason}")

    def use_pipeline(self, name, overrides=None):
        _init_aot_bridge()
        name = str(name)
        if getattr(self, "_destroyed", False) or not getattr(self, "runtime", None):
            raise RuntimeError(
                f"Cannot execute pipeline '{name}' on an inactive AOT runtime"
            )
        recording = getattr(self, "_pipeline_recordings", {}).get(name)
        if recording is not None and recording.get("generation") != getattr(
            self, "_generation", 0
        ):
            # A reinit invalidates every native graph, even if a Python caller
            # still holds the old string name.  Drop the bookkeeping entry so
            # a later call cannot accidentally target stale native state.
            self._drop_pipeline_recording(name)
            recording = None
        if recording is not None and recording.get("active", False):
            raise RuntimeError(
                f"Pipeline '{name}' is still being recorded; leave the "
                "recording scope before executing it"
            )
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
        # Phase 4 D4: refuse pixel counts above the configured cap.
        self._check_max_pixel_count(shape)
        # Phase 4 D1: caller passed the default sentinel; let the
        # engine pick device-local vs host-accessible based on
        # current pressure.  An explicit True/False is honored.
        if host_accessible is False:
            try:
                _size = int(np.prod(shape) * np.dtype(dtype).itemsize)
            except Exception:  # noqa: BLE001
                _size = 0
            if _size > 0 and self._decide_memory_domain(_size):
                host_accessible = True
        self._assert_native_context_owner("allocate")
        if not host_accessible and hasattr(self, "_memory_governor"):
            self._refresh_memory_policy()
        _lock_wait_begin("allocate")
        with self._lock:
            _lock_wait_end()
            size = int(np.prod(shape) * np.dtype(dtype).itemsize)

            # Admit a pipeline allocation before entering the native driver.
            # OpenGL ICDs commonly report GL_INVALID_OPERATION from glGenBuffers
            # after an over-committed SSBO sequence instead of returning a
            # recoverable out-of-memory result.  The resident estimate is kept
            # in Python so the automatic planner can abandon recording (or an
            # explicit legacy recording can fail clearly) before the driver is
            # asked to create the next buffer.  Upload/staging allocations are
            # intentionally excluded because they are not pipeline residents.
            if self.current_pipeline and not host_accessible:
                decision = self._refresh_memory_policy()
                limit = int(getattr(decision, "pipeline_resident_limit", 0) or 0)
                if limit > 0:
                    resident = sum(
                        int(getattr(buf, "size_bytes", getattr(buf, "nbytes", 0)) or 0)
                        for buf in self._pipeline_intermediates.get(
                            self.current_pipeline, ()
                        )
                    )
                    projected = resident + size
                    if projected > limit:
                        state = getattr(self._local, "auto_pipeline_context", None)
                        if state and state.get("mode") in {"recorded", "segmented"}:
                            self._abort_auto_pipeline(
                                "resident budget exceeded before allocation "
                                f"({projected} > {limit} bytes)"
                            )
                        else:
                            raise RuntimeError(
                                "AOT pipeline allocation exceeds the adaptive "
                                "resident-memory limit "
                                f"({projected} > {limit} bytes); "
                                "reduce the graph footprint or use automatic "
                                "pipeline planning."
                            )

            v_dim = (
                vector_dim
                if vector_dim is not None
                else (shape[-1] if is_vector and len(shape) >= 2 else 1)
            )
            pool_key = self._buffer_pool_key(
                size,
                dtype,
                host_accessible=host_accessible,
                is_vector=is_vector,
                vector_dim=v_dim,
            )
            # A free warm slot is returned without synchronization.  If the
            # matching slot was just retired by the preceding frame, perform
            # one bounded queue wait and promote only that allocation class;
            # unrelated retired keys must not impose a global wait here.
            handle = self.buffer_pool.acquire(pool_key)
            if handle is None and self._retired_buffers:
                self._drain_retired(wait=True, key=pool_key)
                handle = self.buffer_pool.acquire(pool_key)
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
                # Automatic emergency memory reclamation and retry
                self._drain_retired(wait=True)
                self.buffer_pool.clear()
                import gc
                gc.collect()
                _op_begin("allocate_gpu_buffer_retry")
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

    def _assert_native_context_owner(self, operation: str) -> None:
        """Reject unsupported cross-thread OpenGL/GLES native dispatch.

        CPU/CUDA/Vulkan remain lock-serialized as before.  OpenGL/GLES needs
        the actual ICD context owner thread, not merely a Python mutex; a
        mutex cannot make a context current on a different Windows thread.
        """

        backend = str(getattr(self, "arch", "")).lower()
        owner = getattr(self, "_native_context_owner_thread_id", None)
        if backend in {"opengl", "gles"} and owner is not None:
            current = threading.get_ident()
            if current != owner:
                raise RuntimeError(
                    "OpenGL/GLES native operation is thread-affine: "
                    f"{operation} must run on context-owner thread {owner}, "
                    f"not worker thread {current}. The bridge has no safe "
                    "context migration queue; dispatch this operation through "
                    "the owner thread or use a backend with thread-safe native "
                    "submission."
                )

    def clear_pipeline_by_name(self, name):
        """Safely erases a pipeline from C++ and forces destruction of its intermediate buffers."""
        name = str(name)
        with self._lock:
            if name in self.recorded_pipelines:
                self.recorded_pipelines.remove(name)
            _LIB.clear_pipeline(None, name.encode("utf-8"))
            recordings = getattr(self, "_pipeline_recordings", None)
            if recordings is not None:
                recordings.pop(name, None)
            if getattr(self, "current_pipeline", None) == name:
                self.current_pipeline = None
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
            names = set(self._pipeline_intermediates.keys())
            names.update(self.recorded_pipelines)
            names.update(getattr(self, "_pipeline_recordings", {}).keys())
            for name in list(names):
                self.clear_pipeline_by_name(name)
            self.recorded_pipelines.clear()
            getattr(self, "_pipeline_recordings", {}).clear()

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
                    current.cache_entries
                    if cache_entries is None
                    else int(cache_entries)
                ),
                cache_bytes=(
                    current.cache_bytes
                    if cache_bytes is _UNSET
                    else (None if cache_bytes is None else int(cache_bytes))
                ),
                adaptive_memory=(
                    current.adaptive_memory
                    if adaptive_memory is None
                    else bool(adaptive_memory)
                ),
                device_cache_enabled=(
                    current.device_cache_enabled
                    if device_cache_enabled is None
                    else bool(device_cache_enabled)
                ),
                device_cache_bytes=(
                    current.device_cache_bytes
                    if device_cache_bytes is None
                    else int(device_cache_bytes)
                ),
            )
            self._block_config = config
            self._memory_governor.configure(config.cache_bytes)
            self._refresh_memory_policy(force=True)
            return config

    def _ensure_memory_cache_runtime(self):
        """Lazily initialize policy components for lightweight/test engine instances."""
        if not hasattr(self, "_block_plan_stats"):
            self._block_plan_stats = {
                "automatic": 0,
                "explicit": 0,
                "full_frame": 0,
                "full_frame_threshold": 0,
                "full_frame_dependency": 0,
                "full_frame_halo": 0,
                "full_frame_quarantine": 0,
            }
        if not hasattr(self, "_block_plan_stats_lock"):
            self._block_plan_stats_lock = threading.Lock()
        if not hasattr(self, "_block_quarantine"):
            self._block_quarantine = {}
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
                if self._block_config.device_cache_enabled
                else 0
            )
            self.buffer_pool.set_budget(device_budget)
            self._device_block_cache.set_budget(device_budget)
            self._apply_lifecycle_limits(None, trim=False)
            return None
        decision = self._memory_governor.refresh(force=force)
        # BufferPool only receives handles after the retired queue has reached
        # a synchronization safe point. Evicting an idle pooled handle
        # therefore needs no second queue barrier here; deferring lifecycle
        # trims avoids turning every graph refresh into a full device wait.
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
            if self._block_config.device_cache_enabled and decision.allow_cache
            else 0
        )
        self._device_block_cache.set_budget(device_budget)
        self._apply_lifecycle_limits(decision, trim=False)
        return decision

    def put_block_record(self, record):
        """Admit a block result only while the realtime memory policy allows it."""
        self._refresh_memory_policy()
        # ``BlockCache.put`` deliberately preserves its historical return
        # value (the record itself) even when byte admission is rejected.  Do
        # the same admission check here before uploading a second copy to the
        # device cache; otherwise a host-rejected tile could still consume
        # VRAM and bypass the governor's bounded-memory policy.
        host_cache = self._block_cache
        entry_bytes = BlockCache.data_nbytes(getattr(record, "data", None))
        host_limit = getattr(host_cache, "max_bytes", None)
        host_admission_possible = not (
            host_limit is not None
            and (int(host_limit) <= 0 or entry_bytes > int(host_limit))
        )
        admitted = self._block_cache.put(record)
        # ``collect()`` may evict the just-inserted record when entry/owner
        # quotas are pinned.  Confirm that the exact record remains resident
        # before uploading a second copy to the device cache.
        host_admitted = host_admission_possible and (
            self._block_cache.peek(getattr(record, "block_id", "")) is record
        )
        if self._block_config.device_cache_enabled and host_admitted:
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
                    uploaded.append(
                        self.upload(
                            np.ascontiguousarray(item), is_vector=item.ndim == 3
                        )
                    )
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
            and not getattr(existing, "invalidated", False)
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
            fence_ready=getattr(record, "fence_ready", None),
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
                    if isinstance(data, tuple)
                    else checksum(data)
                )
                if actual != entry.checksum:
                    raise RuntimeError("resident block checksum mismatch")
                return BlockRecord(
                    str(block_id),
                    state=BlockState.READY,
                    data=data,
                    checksum=entry.checksum,
                    source_checksum=entry.source_checksum,
                    owner=entry.owner,
                )
            except Exception:
                pass
        self._device_block_cache.invalidate(block_id)
        return None

    @contextmanager
    def lease_resident_block(self, block_id, source_checksum=None):
        """Lease a device-resident tile without forcing a host readback.

        Native graph callers can consume ``entry.buffer`` while the context is
        active and release it deterministically afterwards.  This is the
        zero-copy P2 path; :meth:`restore_resident_block` remains the legacy
        CPU/NumPy compatibility path and still validates a downloaded payload.
        ``None`` is yielded for a missing or stale entry, never a buffer from a
        different source generation.
        """

        self._refresh_memory_policy()
        with self._device_block_cache.lease(block_id) as entry:
            valid = bool(
                entry is not None
                and not getattr(entry, "invalidated", False)
                and (
                    source_checksum is None
                    or getattr(entry, "source_checksum", None) == source_checksum
                )
            )
            yield entry if valid else None

    def consume_resident_block(self, block_id, source_checksum, consumer):
        """Invoke ``consumer`` on a leased resident entry, without readback."""

        if not callable(consumer):
            raise TypeError("consumer must be callable")
        with self.lease_resident_block(block_id, source_checksum) as entry:
            if entry is None:
                return None
            return consumer(entry)

    def _log_warning(self, message):
        """Phase 4 D2 telemetry sink.  Default falls back to ``print`` so
        warnings are visible without wiring a logger.
        """
        try:
            print(f"[AOTEngine][warn] {message}")
        except Exception:  # noqa: BLE001
            pass

    def get_memory_status(self, force=False):
        """Return the current adaptive host-memory decision as plain data."""
        self._refresh_memory_policy(force=force)
        status = self._memory_governor.snapshot()
        resident = 0
        for buf in tuple(getattr(self, "_live_buffers", ())):
            if getattr(buf, "handle", None) is not None and getattr(
                buf, "is_owner", False
            ):
                resident += int(getattr(buf, "size_bytes", 0) or 0)
        pooled = int(getattr(self.buffer_pool, "pooled_bytes", 0) or 0)
        retired = int(getattr(self, "_retired_bytes", 0) or 0)
        staging_entries = []
        for bucket in getattr(self, "_staging_pool", {}).values():
            staging_entries.extend(bucket)
        staging_bytes = sum(
            int(getattr(entry.get("buffer"), "size_bytes", 0) or 0)
            for entry in staging_entries
        )
        staging_leased_bytes = sum(
            int(getattr(entry.get("buffer"), "size_bytes", 0) or 0)
            for entry in staging_entries
            if entry.get("leased", False)
        )
        status["resident_bytes"] = resident + pooled + retired
        status["live_bytes"] = resident
        status["pooled_bytes"] = pooled
        status["retired_bytes"] = retired
        status["retired_count"] = len(getattr(self, "_retired_buffers", ()))
        status["retired_budget"] = int(
            getattr(
                self, "_retired_buffer_budget", status.get("retired_buffer_budget", 0)
            )
            or 0
        )
        status["staging_entries"] = len(staging_entries)
        status["staging_bytes"] = staging_bytes
        status["staging_leased_bytes"] = staging_leased_bytes
        status["staging_pool_budget"] = int(
            getattr(self, "_staging_pool_budget", status.get("staging_pool_budget", 0))
            or 0
        )
        status["lifecycle_bytes"] = staging_bytes + retired
        status["retired_buffer_budget"] = int(
            getattr(
                self, "_retired_buffer_budget", status.get("retired_buffer_budget", 0)
            )
            or 0
        )
        # This is a resident/preload depth hint only. Native queue overlap is
        # intentionally reported false until a backend fence proof exists.
        status["residency_depth"] = int(status.get("max_concurrency", 1) or 1)
        status["concurrency_verified"] = False
        status["resident_limit"] = int(status.get("pipeline_resident_limit", 0) or 0)
        status["resident_over_limit"] = bool(
            status["resident_limit"] > 0
            and resident + pooled + retired > status["resident_limit"]
        )
        status["resident_headroom_bytes"] = max(
            0, status["resident_limit"] - (resident + pooled + retired)
        )
        lifecycle_lock = getattr(self, "_lock", None)
        if lifecycle_lock is not None:
            with lifecycle_lock:
                recordings_snapshot = tuple(
                    getattr(self, "_pipeline_recordings", {}).values()
                )
                pending_snapshot = tuple(getattr(self, "_async_futures", ()))
                reservations_snapshot = int(
                    getattr(self, "_async_reservations", 0) or 0
                )
        else:
            recordings_snapshot = tuple(
                getattr(self, "_pipeline_recordings", {}).values()
            )
            pending_snapshot = tuple(getattr(self, "_async_futures", ()))
            reservations_snapshot = int(
                getattr(self, "_async_reservations", 0) or 0
            )
        status["recording_active"] = sum(
            1 for item in recordings_snapshot if item.get("active", False)
        )
        status["recording_count"] = len(recordings_snapshot)
        status["async_pending"] = sum(
            1 for future in pending_snapshot if not future.done()
        )
        status["async_reservations"] = int(reservations_snapshot)
        status["async_pending_limit"] = int(
            getattr(self, "_async_pending_limit", _MAX_ASYNC_PENDING)
            or _MAX_ASYNC_PENDING
        )

        # Phase 4 D5: surface pressure indicators so callers (MFDenoiser,
        # stress tests) can observe the engine's pressure model without
        # reading private state.  Read-only, no allocation.
        try:
            _shared_budget = int(
                getattr(
                    status,
                    "shared_device_budget",
                    status.get("shared_device_budget", 0) or 0,
                )
                or 0
            )
            _dev_heap_budget = int(
                getattr(
                    status,
                    "device_heap_budget",
                    status.get("device_heap_budget", 0) or 0,
                )
                or 0
            )
            _dev_heap_avail = int(
                getattr(
                    status,
                    "device_heap_available",
                    status.get("device_heap_available", 0) or 0,
                )
                or 0
            )
            status["device_heap_pressure_ratio"] = (
                round(_dev_heap_avail / max(1, _dev_heap_budget), 4)
                if _dev_heap_budget > 0
                else 0.0
            )
            status["shared_budget_consumed_ratio"] = (
                round(1.0 - (_dev_heap_avail / max(1, _shared_budget)), 4)
                if _shared_budget > 0
                else 0.0
            )
            # What the auto-promotion policy would do for a 1 MiB probe.
            status["auto_promote_next_allocation"] = bool(
                self._decide_memory_domain(1 * 1024 * 1024)
            )
        except Exception:  # noqa: BLE001
            pass

        return status

    def _decide_memory_domain(self, size_bytes):
        """Phase 4 D1: return True if the next ``size_bytes`` allocation
        should use host-accessible (shared) memory.

        Policy:
          1. Caller is allowed to opt in/out via ``set_force_host_accessible``
             or per-call ``host_accessible=``; this helper only decides
             when the caller passed the sentinel default.
          2. CPU backend (no device heap) -> True.
          3. Device backend:
             - If ``shared_device_budget`` is 0 -> True (no budget info).
             - If size > 0.5 * device_heap_available -> True.
             - If shared_device_budget < 1.5 * size -> True (prefer host
               over risking OOM).
             - Otherwise -> False (device-local).
        """
        try:
            # Caller override takes precedence.
            force = getattr(self, "_force_host_accessible", None)
            if force is True:
                return True
            if force is False:
                return False
            _arch = str(getattr(self, "arch", "")).lower()
            if _arch in {"", "cpu"}:
                return True
            try:
                _status = self.get_memory_status(force=True)
            except Exception:  # noqa: BLE001
                _status = {}
            _shared = int(_status.get("shared_device_budget", 0) or 0)
            _dev_budget = int(_status.get("device_heap_budget", 0) or 0)
            _dev_avail = int(_status.get("device_heap_available", 0) or 0)
            if _dev_budget <= 0:
                # Backend did not report a device heap; treat as shared.
                return True
            if _dev_avail <= 0:
                return True
            if int(size_bytes) > int(0.5 * _dev_avail):
                return True
            if _shared > 0 and int(size_bytes) > int(_shared / 1.5):
                return True
            return False
        except Exception:  # noqa: BLE001
            return False

    def set_force_host_accessible(self, value):
        """Phase 4 D1: force every subsequent allocation to use
        host-accessible memory (value=True) or device-local (value=False).
        Pass None to clear the override and let ``_decide_memory_domain``
        apply the default policy.
        """
        if value is None:
            if hasattr(self, "_force_host_accessible"):
                try:
                    delattr(self, "_force_host_accessible")
                except Exception:  # noqa: BLE001
                    pass
        else:
            self._force_host_accessible = bool(value)
        return getattr(self, "_force_host_accessible", None)

    def set_max_pixel_count(self, max_pixels):
        """Phase 4 D4: cap the per-call pixel count.  Pass ``0`` to clear
        the limit.  Returns the new effective cap.
        """
        if max_pixels is None or int(max_pixels) <= 0:
            if hasattr(self, "_max_pixel_count"):
                try:
                    delattr(self, "_max_pixel_count")
                except Exception:  # noqa: BLE001
                    pass
            return getattr(self, "_max_pixel_count", 0)
        self._max_pixel_count = int(max_pixels)
        return self._max_pixel_count

    def _check_max_pixel_count(self, shape):
        """Phase 4 D4: raise ``RuntimeError`` when the requested shape
        exceeds the configured pixel cap.
        """
        cap = getattr(self, "_max_pixel_count", 0)
        if not cap:
            return
        try:
            _n = int(np.prod(shape))
        except Exception:  # noqa: BLE001
            return
        if _n > cap:
            raise RuntimeError(
                f"\n[AOTEngine Pixel Cap] Requested shape {tuple(shape)!r} "
                f"has {_n:,} pixels, exceeding the configured cap of "
                f"{cap:,} pixels.\n"
                "  HINT: enable block mode via "
                "`taichi_aot.set_block_mode(enabled=True, size=512)` "
                "or raise the cap with "
                "`engine.set_max_pixel_count(0)` (0 = unlimited)."
            )

    def recommend_block_batch_size(self, tile_bytes=0, *, extra_bytes=0, cap=4):
        """Choose a bounded number of resident tiles for batched block work.

        Block execution historically synchronized after every tile.  Callers
        that can defer readback use this helper to keep a small number of
        output slots resident without bypassing the memory governor.  The
        recommendation is deliberately conservative: it is limited by the
        governor's concurrency hint, current resident headroom, and ``cap``.
        A result of one is always safe and preserves the old execution shape.
        """
        try:
            status = self.get_memory_status()
        except Exception:
            return 1

        limit = max(1, int(cap))
        decision = getattr(self, "_memory_governor", None)
        decision = decision.snapshot() if decision is not None else {}
        pressure = str(decision.get("pressure", "healthy")).lower()
        if pressure in {"critical", "emergency"}:
            return 1

        hinted = int(
            decision.get("residency_depth", decision.get("max_concurrency", 1)) or 1
        )
        count = max(1, min(limit, hinted))
        per_slot = max(0, int(tile_bytes)) + max(0, int(extra_bytes))
        headroom = int(status.get("resident_headroom_bytes", 0) or 0)
        resident_limit = int(status.get("resident_limit", 0) or 0)
        if per_slot > 0:
            if resident_limit > 0 and headroom < per_slot:
                return 1
            if headroom > 0:
                count = min(count, max(1, headroom // per_slot))
        return max(1, int(count))

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
            "segments": tuple(plan.segments),
            "cursor": 0,
            "segment_index": None,
            "aborted": False,
            "mode": plan.mode,
            "active_segment": None,
            "active_recorder": None,
            "active_pipeline_name": None,
            "recording_active": False,
            "replay_calls": [],
            "replaying": False,
        }
        self._local.auto_pipeline_context = state

        if plan.mode == "segmented":
            # Segmented execution is still automatic: each qualified segment
            # (two or more graphs with valid resident metadata) gets its own
            # one-shot recorder. Unknown or one-graph segments remain direct.
            # Boundaries are finalized in ``_auto_pipeline_before_run`` when
            # the next graph is about to dispatch, then once more on scope
            # exit for the final segment.
            if name is None:
                digest = hashlib.sha1(
                    "|".join(
                        f"{getattr(item, 'module_key', None)}:{item.name}"
                        for segment in plan.segments
                        for item in segment
                    ).encode("utf-8")
                ).hexdigest()[:12]
                name = f"__auto_pipeline_{digest}"
            state["name"] = str(name)
            state["segment_names"] = tuple(
                f"{name}__segment_{index}"
                for index, _segment in enumerate(plan.segments)
            )
            try:
                yield plan
            except BaseException as exc:
                state["aborted"] = True
                try:
                    self._auto_pipeline_finish_segment(
                        state,
                        error=exc,
                        replay=self._auto_pipeline_replay_allowed(exc),
                    )
                finally:
                    try:
                        self.sync()
                    except Exception:
                        pass
                raise
            else:
                self._auto_pipeline_finish_segment(state)
                self.sync()
            finally:
                self._local.auto_pipeline_context = None
            return

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
                self._drop_pipeline_recording(str(name), destroy_intermediates=True)
            raise
        finally:
            self._local.auto_pipeline_context = None

    def get_block_cache_stats(self):
        self._ensure_memory_cache_runtime()
        stats = self._cache_telemetry.snapshot()
        with self._block_plan_stats_lock:
            planner_stats = dict(self._block_plan_stats)
            quarantine = dict(self._block_quarantine)
        stats.update(
            {
                "entries": len(self._block_cache),
                "size_bytes": self._block_cache.size_bytes,
                "max_entries": self._block_cache.max_entries,
                "max_bytes": self._block_cache.max_bytes,
                "owner_bytes": self._block_cache.owner_bytes,
                "owner_targets": self._block_cache.owner_targets(),
                "device": self._device_block_cache.stats(),
                "buffer_pool": {
                    **self.buffer_pool.stats(),
                    "retired_bytes": int(getattr(self, "_retired_bytes", 0) or 0),
                },
                "planner": planner_stats,
                "quarantine": quarantine,
                "last_execution": self.get_last_block_execution(),
            }
        )
        planner = getattr(self, "_auto_pipeline_planner", None)
        if planner is not None:
            try:
                stats["autotune"] = planner.autotuner.snapshot()
            except Exception:
                stats["autotune"] = {}
            try:
                stats["plan_cache"] = planner.plan_cache_stats()
            except Exception:
                stats["plan_cache"] = {}
        return stats

    def set_last_block_execution(self, payload):
        """Store the most recent block orchestration telemetry per thread."""
        data = dict(payload or {})
        self._local.last_block_execution = data
        planner = getattr(self, "_auto_pipeline_planner", None)
        if planner is not None and data:
            try:
                planner_metrics = dict(data)
                if "elapsed_seconds" in data:
                    planner_metrics["latency_ms"] = (
                        float(data["elapsed_seconds"] or 0.0) * 1000.0
                    )
                if "bytes_copied" in data or "cache_copy_bytes" in data:
                    planner_metrics["transfer_bytes"] = int(
                        data.get("bytes_copied", 0) or 0
                    ) + int(data.get("cache_copy_bytes", 0) or 0)
                if "cache_hits" in data or "computed" in data:
                    planner_metrics["cache_misses"] = int(data.get("computed", 0) or 0)
                planner.observe(
                    planner_metrics,
                    operation=data.get("operation"),
                )
            except Exception:
                # Telemetry must never change the execution result or turn a
                # successful algorithm into a failure.
                pass

    def get_last_block_execution(self):
        """Return host-side block telemetry without exposing native handles."""
        return dict(getattr(self._local, "last_block_execution", {}) or {})

    def configure_block_reservation(
        self, operation, soft_bytes=0, hard_bytes=None, weight=1.0
    ):
        """Configure an elastic owner quota for the feature-gated VRAM cache."""
        self._ensure_memory_cache_runtime()
        self._device_block_cache.configure_owner(
            operation, soft_bytes, hard_bytes, weight
        )

    def get_device_block_cache(self):
        self._refresh_memory_policy()
        return self._device_block_cache

    def clear_block_cache(self):
        """Drop cached block results without changing the active policy."""
        with self._lock:
            self._block_cache.clear()
            self._device_block_cache.clear()

    def reclaim_resident_buffers(self, reason: str = "manual"):
        """Drain the warm pool and retired queue, returning reclaimed counters.

        Additive public API introduced in Phase 4.  Safe to call from any
        thread that does not already hold ``self._lock`` for another
        purpose (the engine uses an RLock so the same thread can re-enter).
        The caller is expected to invoke ``engine.sync()`` first if GPU
        work is in flight, otherwise in-flight kernels may reuse the
        retired handle.

        Returns a counter dict with before/after ``get_memory_status()``
        snapshots and the delta in live / pooled / staging bytes.
        """
        with self._lock:
            before = self.get_memory_status()
            try:
                self._drain_retired(wait=True)
            except Exception:  # noqa: BLE001
                pass
            try:
                self.buffer_pool.clear()
            except Exception:  # noqa: BLE001
                pass
            try:
                self._trim_staging_pool()
            except Exception:  # noqa: BLE001
                pass
            try:
                import gc as _gc

                _gc.collect()
            except Exception:  # noqa: BLE001
                pass
            after = self.get_memory_status()
        return {
            "reason": str(reason),
            "before": dict(before),
            "after": dict(after),
            "reclaimed_live_bytes": int(
                (before.get("live_bytes", 0) or 0)
                - (after.get("live_bytes", 0) or 0)
            ),
            "reclaimed_pooled_bytes": int(
                (before.get("pooled_bytes", 0) or 0)
                - (after.get("pooled_bytes", 0) or 0)
            ),
            "reclaimed_staging_bytes": int(
                (before.get("staging_bytes", 0) or 0)
                - (after.get("staging_bytes", 0) or 0)
            ),
            "reclaimed_retired_bytes": int(
                (before.get("retired_bytes", 0) or 0)
                - (after.get("retired_bytes", 0) or 0)
            ),
        }

    def _record_block_plan(self, bucket):
        self._ensure_memory_cache_runtime()
        with self._block_plan_stats_lock:
            self._block_plan_stats[bucket] = self._block_plan_stats.get(bucket, 0) + 1

    def quarantine_block_operation(self, operation, reason):
        """Disable block planning for one operation in this runtime generation.

        A failed tile must not poison later frames.  The same-backend
        full-frame path remains available, while cached partial tiles are
        invalidated before the next request.
        """
        self._ensure_memory_cache_runtime()
        name = str(operation)
        with self._block_plan_stats_lock:
            self._block_quarantine[name] = str(reason)[:512]
        try:
            self._block_cache.invalidate_owner(name)
        except Exception:
            pass
        try:
            self._device_block_cache.invalidate_owner(name)
        except Exception:
            pass

    def clear_block_quarantine(self, operation=None):
        """Clear one or all block failure quarantines for controlled retesting."""
        self._ensure_memory_cache_runtime()
        with self._block_plan_stats_lock:
            if operation is None:
                self._block_quarantine.clear()
            else:
                self._block_quarantine.pop(str(operation), None)

    def plan_blocks(self, operation, shape, nbytes, halo=0):
        """Plan explicit or pressure-triggered blocks for parity-safe operations."""
        capability = operation_capability(operation)
        contract = operation_contract(operation)
        if str(operation) in getattr(self, "_block_quarantine", {}):
            self._local.last_block_plan = {
                "operation": str(operation),
                "selected": False,
            }
            self._record_block_plan("full_frame")
            self._record_block_plan("full_frame_quarantine")
            return None
        decision = (
            self._refresh_memory_policy()
            if self._block_config.adaptive_memory
            else None
        )
        explicit = should_use_blocks(operation, nbytes, self._block_config)
        automatic = bool(
            decision is not None
            and capability.automatic_safe
            and can_auto_block(operation, getattr(self, "arch", "cpu"))
            and int(halo) >= int(capability.min_halo)
            and int(nbytes)
            >= max(
                1,
                min(
                    int(self._block_config.threshold_bytes),
                    int(decision.target_chunk_bytes),
                ),
            )
        )
        if not explicit and not automatic:
            self._local.last_block_plan = {
                "operation": str(operation),
                "selected": False,
                "contract": contract.as_dict(),
            }
            self._record_block_plan("full_frame")
            if int(nbytes) < max(
                1,
                min(
                    int(self._block_config.threshold_bytes),
                    (
                        int(decision.target_chunk_bytes)
                        if decision is not None
                        else int(self._block_config.threshold_bytes)
                    ),
                ),
            ):
                self._record_block_plan("full_frame_threshold")
            elif capability.path == BlockPath.GLOBAL or not capability.automatic_safe:
                self._record_block_plan("full_frame_dependency")
            elif int(halo) < int(capability.min_halo):
                self._record_block_plan("full_frame_halo")
            return None
        self._record_block_plan("explicit" if explicit else "automatic")
        tuning = None
        if automatic:
            planner = getattr(self, "_auto_pipeline_planner", None)
            if planner is not None:
                try:
                    tuning = planner.recommend(
                        str(operation),
                        contract=contract,
                        current_block_size=self._block_config.normalized_size()[0],
                    ).as_dict()
                except Exception:
                    tuning = None
        self._local.last_block_plan = {
            "operation": str(operation),
            "selected": True,
            "contract": contract.as_dict(),
            "tuning": tuning,
        }
        size = self._block_config.normalized_size()
        if decision is not None:
            # Refine the generic governor estimate using the operation's
            # channel count.  The resident policy remains conservative
            # f32-based, but grayscale/flow operations no longer inherit the
            # full RGB footprint unnecessarily.
            shape_tuple = tuple(int(item) for item in shape)
            channels = 1
            if len(shape_tuple) >= 3 and 1 <= shape_tuple[-1] <= 4:
                channels = shape_tuple[-1]
            recommended = int(
                self._memory_governor.recommend_block_size(
                    channels=channels,
                    sample_bytes=4,
                    live_buffers=4,
                )
            )
            if automatic and not self._block_config.enabled:
                size = (recommended, recommended)
            else:
                size = (min(size[0], recommended), min(size[1], recommended))
            if automatic and tuning:
                tuned = int(tuning.get("block_size", recommended) or recommended)
                tuned = max(1, min(recommended, tuned))
                size = (min(size[0], tuned), min(size[1], tuned))
        return BlockGrid(shape, size=size, halo=halo)

    def plan_generic_blocks(
        self,
        operation,
        shape,
        nbytes,
        *,
        halo=0,
        mode="auto",
        automatic=True,
        min_halo=0,
        block_size=None,
        threshold_bytes=None,
    ):
        """Plan an explicitly described custom block operation.

        Unlike :meth:`plan_blocks`, this method intentionally does not consult
        ``OPERATION_CAPABILITIES``.  A caller-owned ``BlockComputeSpec`` is the
        authority for custom tile semantics.  Memory sizing, lifecycle, and
        quarantine remain engine-owned so a custom optical-flow or feature
        matcher cannot bypass the shared safety mechanisms.

        ``mode='force'`` means force the *custom grid*, not force an unsafe
        allocation: the selected size is still clamped by the adaptive memory
        recommendation when telemetry is available.
        """
        mode = str(mode).lower().strip()
        if mode not in {"auto", "force", "off"}:
            raise ValueError("generic block mode must be 'auto', 'force', or 'off'")
        name = str(operation)
        if name in getattr(self, "_block_quarantine", {}):
            self._local.last_block_plan = {
                "operation": name,
                "selected": False,
                "generic": True,
                "reason": "quarantined",
            }
            self._record_block_plan("generic_full_frame_quarantine")
            return None

        halo = int(halo)
        min_halo = int(min_halo)
        if halo < min_halo:
            self._local.last_block_plan = {
                "operation": name,
                "selected": False,
                "generic": True,
                "reason": "insufficient_halo",
            }
            self._record_block_plan("generic_full_frame_halo")
            return None

        decision = (
            self._refresh_memory_policy()
            if self._block_config.adaptive_memory
            else None
        )
        configured_threshold = int(self._block_config.threshold_bytes)
        threshold = (
            configured_threshold
            if threshold_bytes is None
            else max(0, int(threshold_bytes))
        )
        target_chunk = (
            int(decision.target_chunk_bytes) if decision is not None else threshold
        )
        # Keep the same non-zero lower bound used by the native planner.  A
        # zero budget must not make every positive-sized custom input appear
        # below a zero threshold and accidentally select an unbounded grid.
        effective_threshold = max(1, min(threshold, target_chunk))
        size_bytes = int(nbytes)
        selected = False
        reason = ""
        if mode == "force":
            selected = True
            reason = "custom force mode"
        elif mode == "auto" and bool(automatic):
            selected = size_bytes >= effective_threshold
            reason = (
                "adaptive budget threshold reached"
                if selected
                else "below adaptive budget threshold"
            )
        else:
            reason = "custom block mode disabled"

        if not selected:
            self._local.last_block_plan = {
                "operation": name,
                "selected": False,
                "generic": True,
                "reason": reason,
            }
            self._record_block_plan("generic_full_frame")
            if mode == "off":
                self._record_block_plan("generic_full_frame_disabled")
            elif size_bytes < effective_threshold:
                self._record_block_plan("generic_full_frame_threshold")
            return None

        self._record_block_plan(
            "generic_forced" if mode == "force" else "generic_automatic"
        )
        self._local.last_block_plan = {
            "operation": name,
            "selected": True,
            "generic": True,
            "reason": reason,
        }

        size = block_size or self._block_config.normalized_size()
        if decision is not None:
            shape_tuple = tuple(int(item) for item in shape)
            channels = 1
            if len(shape_tuple) >= 3 and 1 <= shape_tuple[-1] <= 4:
                channels = shape_tuple[-1]
            recommended = int(
                self._memory_governor.recommend_block_size(
                    channels=channels,
                    sample_bytes=4,
                    live_buffers=4,
                )
            )
            normalized = BlockConfig(size=size).normalized_size()
            size = (min(normalized[0], recommended), min(normalized[1], recommended))
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
                    entry["last_used"] = time.monotonic()
                    return entry["buffer"]

            # None found, allocate a new one.  If the bounded pool would
            # exceed its cap, synchronize once before reclaiming an idle
            # staging handle.  This avoids freeing a buffer still referenced
            # by an asynchronous upload/readback while keeping the common
            # reuse path non-blocking.
            all_entries = [
                entry for bucket in self._staging_pool.values() for entry in bucket
            ]
            total_bytes = sum(
                int(getattr(entry.get("buffer"), "size_bytes", 0) or 0)
                for entry in all_entries
            )
            max_entries = int(
                getattr(self, "_staging_pool_max_entries", _MAX_STAGING_POOL_ENTRIES)
            )
            max_bytes = int(
                getattr(self, "_staging_pool_budget", _DEFAULT_STAGING_POOL_BUDGET)
            )
            if all_entries and (
                len(all_entries) >= max_entries
                or (max_bytes > 0 and total_bytes + size > max_bytes)
                or (max_bytes == 0 and total_bytes > 0)
            ):
                self.sync()
                self._trim_staging_pool()
            buf = self.allocate(shape, dtype, host_accessible=True)
            self._staging_pool[key].append(
                {"leased": True, "buffer": buf, "last_used": time.monotonic()}
            )
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
                        entry["last_used"] = time.monotonic()
                        break
        # Returning a slot is a safe lifecycle point.  Trim only idle entries;
        # an in-flight readback/upload can never be reclaimed here.
        # Idle staging entries are reclaimed by ``sync()`` after the native
        # queue has completed.  Marking the entry free here is intentionally
        # non-blocking and preserves upload throughput.

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
        shape = getattr(data, "shape", None)
        dtype = np.float32
        # Host-export based interop objects (OpenCV UMat and ONNX OrtValue in
        # particular) do not reliably expose shape/dtype metadata themselves.
        # Materialize them once, before allocating the staging buffer, so the
        # exported host array—not the placeholder ``(1,)`` shape—is the ABI
        # source of truth.  This remains a staged transfer; it deliberately
        # does not turn a foreign allocation into a borrowed GPU handle.
        materialized = None

        if obj_type == "pytorch":
            import torch

            dtype_map = {
                torch.float32: np.float32,
                torch.float16: np.float16,
                torch.uint8: np.uint8,
                torch.uint16: np.uint16,
                torch.int16: np.int16,
                torch.int32: np.int32,
            }
            dtype = dtype_map.get(data.dtype)
            if dtype is None:
                raise TypeError(
                    f"unsupported PyTorch interop dtype {data.dtype}; "
                    "convert explicitly to float16/float32/int16/int32/uint8/uint16"
                )
        elif obj_type == "opencv" and hasattr(data, "get"):
            materialized = data.get()
        elif obj_type == "onnx":
            if hasattr(data, "numpy"):
                materialized = data.numpy()
            elif hasattr(data, "cpu"):
                materialized = data.cpu().numpy()
            else:
                raise TypeError(
                    "ONNX OrtValue does not expose a safe host export"
                )
        elif hasattr(data, "__cuda_array_interface__"):
            if hasattr(data, "get"):
                materialized = data.get()
            elif hasattr(data, "cpu"):
                materialized = data.cpu().numpy()
            elif hasattr(data, "copy_to_host"):
                materialized = data.copy_to_host()
            elif hasattr(data, "numpy"):
                materialized = data.numpy()
            else:
                materialized = np.asarray(data)

        if materialized is not None:
            materialized = np.ascontiguousarray(materialized)
            if materialized.ndim == 0:
                materialized = materialized.reshape((1,))
            shape = tuple(int(dimension) for dimension in materialized.shape)
            dtype = materialized.dtype
        else:
            if shape is None:
                shape = (1,)
            else:
                shape = tuple(int(dimension) for dimension in shape)
            if hasattr(data, "dtype") and obj_type != "pytorch":
                dtype = data.dtype

        # Apply the same RGB/flow vector convention after host export.  This
        # is necessary for UMat/OrtValue, whose public ``shape`` attribute is
        # absent or callable and therefore cannot be inspected by upload().
        if not is_vector and len(shape) == 3:
            if shape[2] == 3:
                is_vector = True
                vector_dim = 3
            elif shape[2] == 2:
                is_vector = True
                vector_dim = 2

        staging = self.acquire_staging_buffer(shape, dtype)
        try:
            ptr = staging.map()
            try:
                if obj_type == "pytorch":
                    import torch

                    target_view = torch.from_blob(
                        ptr, shape, dtype=data.dtype, device="cpu"
                    )
                    target_view.copy_(data.detach(), non_blocking=False)
                else:
                    # A CUDA array-interface ``data`` field is a device
                    # address, never a host pointer.  The old direct
                    # ctypes.memmove path could dereference it and corrupt
                    # memory.  Prefer an object's synchronized host getter;
                    # otherwise use CuPy's CUDA-aware device-to-host copy.
                    if materialized is not None:
                        temp = materialized
                    else:
                        temp = data
                    temp = np.ascontiguousarray(temp)
                    if temp.nbytes != staging.nbytes:
                        raise ValueError(
                            "external interop byte size does not match its declared "
                            f"shape/dtype ({temp.nbytes} != {staging.nbytes})"
                        )
                    ctypes.memmove(ptr, temp.ctypes.data, staging.nbytes)
            finally:
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

        if ext_type:
            return self._upload_fast_interop(
                data, is_vector=is_vector, vector_dim=vector_dim
            )

        # Auto-detect Vector Fields (RGB=3, Flow=2) for ordinary array-like
        # inputs. External objects are handled above because their shape may
        # be a method (OrtValue) or unavailable until host export (UMat).
        if not is_vector and hasattr(data, "shape"):
            raw_shape = getattr(data, "shape", None)
            if raw_shape is not None and not callable(raw_shape) and len(raw_shape) == 3:
                if raw_shape[2] == 3:
                    is_vector = True
                    vector_dim = 3
                elif raw_shape[2] == 2:
                    is_vector = True
                    vector_dim = 2

        arr = np.ascontiguousarray(data)
        # Phase 4 D4: refuse pixel counts above the configured cap.
        self._check_max_pixel_count(arr.shape)
        # Phase 4 D2: surface a soft warning when an upload would push
        # ``live + pooled + retired`` past the adaptive
        # ``pipeline_resident_limit``.  We do not raise here because
        # legacy callers (notably MFDenoiser / resident_pipeline.py)
        # intentionally commit full-res accumulators that exceed the
        # 1 GiB default; raising here would break them.  Callers that
        # want strict enforcement can use ``engine.allocate`` instead.
        try:
            _sz = int(arr.nbytes)
            _status = self.get_memory_status(force=True)
            _live = int(_status.get("live_bytes", 0) or 0)
            _pooled = int(_status.get("pooled_bytes", 0) or 0)
            _retired = int(_status.get("retired_bytes", 0) or 0)
            _limit = int(_status.get("resident_limit", 0) or 0)
            if _limit > 0 and (_live + _pooled + _retired + _sz) > _limit:
                _print_fn = getattr(self, "_log_warning", None)
                if callable(_print_fn):
                    _print_fn(
                        f"upload({tuple(arr.shape)!r}, {arr.dtype}) requests "
                        f"{_sz / (1024 * 1024):.1f} MiB but live+pooled+retired "
                        f"({(_live + _pooled + _retired) / (1024 * 1024):.1f} MiB) "
                        f"plus this upload ({_sz / (1024 * 1024):.1f} MiB) "
                        f"exceeds pipeline_resident_limit "
                        f"({_limit / (1024 * 1024):.1f} MiB). "
                        "Consider engine.reclaim_resident_buffers() or "
                        "engine.allocate(host_accessible=True) for this size."
                    )
        except Exception:  # noqa: BLE001
            pass

        # Phase 4 D1: pass the sentinel default; let ``allocate`` apply
        # the auto-promote policy.  The historical ``host_accessible=True``
        # hard-code is preserved when the caller passes it explicitly.
        buf = self.allocate(
            arr.shape,
            arr.dtype,
            is_vector=is_vector,
            vector_dim=vector_dim,
        )
        if buf.host_accessible:
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
        else:
            # A device-local Vulkan allocation is not mappable on many Intel
            # and NVIDIA drivers.  Upload through the host-visible staging
            # pool, then issue an explicit same-device copy.  The old direct
            # ti_map_memory call happened to work on permissive heaps but
            # asserted on standards-conforming legacy drivers.
            staging = self.acquire_staging_buffer(arr.shape, arr.dtype)
            try:
                _op_begin("write+copy_gpu_buffer")
                try:
                    _LIB.write_to_gpu_buffer(
                        self.runtime,
                        staging.handle,
                        arr.ctypes.data,
                        staging.nbytes,
                    )
                    _LIB.copy_gpu_buffer(
                        self.runtime, staging.handle, buf.handle, staging.nbytes
                    )
                except Exception:
                    _record_error()
                    raise
                finally:
                    _op_end()
            finally:
                self.release_staging_buffer(staging)
        return buf

    def load(self, path):
        with self._lock:
            base, ext = os.path.splitext(path)
            p = (
                f"{base}_{self.arch.lower()}{ext}"
                if os.path.exists(f"{base}_{self.arch.lower()}{ext}")
                else path
            )
            # TCM ABI validation is deliberately opt-in during migration.  A
            # packed archive is checked before CPU extraction or native bridge
            # loading; unpacked legacy CPU directories retain the historical
            # path.  This keeps current applications compatible while making
            # manifest failures fail-closed when the gate is enabled.
            tcm_manifest_path = p if str(p).lower().endswith(".tcm") else None
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
            elif self.arch.lower() in ("opengl", "gles"):
                # Hybrid systems can run this same logical OpenGL backend on
                # physically different renderers. Keep artifact quarantine and
                # validation records isolated per actual adapter.
                device_name = (
                    _get_runtime_device_name(self.runtime) or "opengl-unknown-renderer"
                )
            else:
                device_name = "logical-device"
            if tcm_manifest_path and os.environ.get("AOT_TCM_ABI_PREFLIGHT", "0") == "1":
                target_device_name = device_name
                if self.arch.lower() == "cuda":
                    # CUDA's load diagnostics use a logical device label, but
                    # the TCM target contract still needs the NVIDIA vendor.
                    # Preserve the resolved backend config instead of asking
                    # the contract to infer a vendor from "logical-device".
                    target_device_name = (
                        getattr(getattr(self, "_backend_config", None), "vendor", "")
                        or os.environ.get("TARGET_VENDOR", "nvidia")
                    )
                elif self.arch.lower() == "cpu":
                    target_device_name = ""
                requested_target = detect_target(
                    backend=self.arch,
                    device=target_device_name,
                )
                feature_text = os.environ.get("AOT_TCM_RUNTIME_FEATURES", "")
                if feature_text.strip():
                    runtime_features = {
                        item.strip().upper()
                        for item in feature_text.split(",")
                        if item.strip()
                    }
                elif self.arch.lower() in {"vulkan", "opengl", "gles"}:
                    # The graphics AOT profile is compute/SSBO based.  A
                    # future native capability probe can replace this default
                    # through AOT_TCM_RUNTIME_FEATURES without changing the
                    # manifest or public algorithm API.
                    runtime_features = {"COMPUTE", "SSBO"}
                else:
                    runtime_features = set()
                try:
                    runtime_abi = int(os.environ.get("AOT_TCM_RUNTIME_ABI", "1"))
                except ValueError as exc:
                    raise RuntimeError("AOT_TCM_RUNTIME_ABI must be an integer") from exc
                preflight = preflight_tcm(
                    tcm_manifest_path,
                    requested_target=requested_target,
                    runtime_abi=runtime_abi,
                    runtime_features=runtime_features,
                    allow_legacy=os.environ.get("AOT_TCM_ABI_ALLOW_LEGACY", "1") != "0",
                )
                if not preflight.allowed:
                    set_status(
                        artifact_key(
                            tcm_manifest_path,
                            self.arch,
                            self.device_id,
                            device_name,
                        ),
                        "quarantined",
                        backend=self.arch,
                        device=device_name,
                        artifact=os.path.basename(tcm_manifest_path),
                        error=preflight.reason,
                    )
                    raise RuntimeError(
                        f"[AOTEngine TCM ABI] {preflight.status}: "
                        f"{os.path.basename(tcm_manifest_path)}: {preflight.reason}"
                    )
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
                set_status(
                    cache_key,
                    "quarantined",
                    backend=self.arch,
                    device=device_name,
                    artifact=os.path.basename(p),
                    error=str(exc),
                )
                raise
            if not ptr:
                native_error = _get_native_engine_error(self.runtime)
                detail = f"\n  NATIVE: {native_error}" if native_error else ""
                try:
                    self.reinit(self.device_id)
                except Exception:
                    pass
                set_status(
                    cache_key,
                    "quarantined",
                    backend=self.arch,
                    device=device_name,
                    artifact=os.path.basename(p),
                    error=native_error or "load returned null",
                )
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
        backend = str(getattr(self, "arch", "")).lower()
        owner = getattr(self, "_native_context_owner_thread_id", None)
        if backend in {"opengl", "gles"} and owner is not None and threading.get_ident() != owner:
            return
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
            # Native work is complete now; recycled host/device allocations
            # can safely become available to the next full-frame or block
            # dispatch without another synchronization round trip.
            self._drain_retired(already_synchronized=True)
            self._trim_staging_pool()

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
            # Queued Python jobs retain their argument buffers until they
            # start.  Cancel those that have not acquired the native queue;
            # an already-running job holds ``self._lock`` and therefore
            # completes before this lifecycle transition proceeds.
            for future in tuple(getattr(self, "_async_futures", ())):
                try:
                    future.cancel()
                except Exception:
                    pass
            active_arch = self.arch.lower()

            # A Windows OpenGL ICD context is not safely restartable in the
            # same process on several Intel drivers: destroying the imported
            # runtime and immediately creating a second raw ICD context leaves
            # the driver's thread-local dispatch table invalid, and the next
            # glGenBuffers reports GL_INVALID_OPERATION.  Android GLES has the
            # same ownership rule: the application owns the current EGL
            # context. Reinitialize graph/module/buffer state while retaining
            # the validated native context for both graphics paths. This gives
            # callers the same public lifecycle contract without forcing a
            # fragile context teardown.
            if active_arch in ("opengl", "gles"):
                try:
                    self.sync()
                except Exception:
                    pass
                try:
                    self._drain_retired(already_synchronized=True)
                except Exception:
                    pass
                try:
                    self.clear_pipelines()
                except Exception:
                    self.recorded_pipelines.clear()
                    self._pipeline_intermediates = {}
                for mod in list(getattr(self, "modules", {}).values()):
                    try:
                        if mod.module_ptr:
                            _LIB.destroy_aot_module(mod.module_ptr)
                            mod.module_ptr = None
                    except Exception:
                        pass
                self.modules = {}
                for buf in list(getattr(self, "_live_buffers", ())):
                    try:
                        buf._force_destroy()
                    except Exception:
                        pass
                self._staging_pool = {}
                try:
                    self.buffer_pool.clear()
                except Exception:
                    pass
                self.recorded_pipelines.clear()
                self._pipeline_intermediates = {}
                getattr(self, "_pipeline_recordings", {}).clear()
                if hasattr(self, "_local"):
                    self._local.current_pipeline = None
                    self._local.auto_pipeline_context = None
                self._destroyed = False
                self._generation = getattr(self, "_generation", 0) + 1
                return

            # Taichi's x64 C runtime only accepts device index 0. Keep the
            # public reinit API uniform while preventing a CPU recovery from
            # accidentally requesting a GPU device index.
            requested_device = (
                0 if active_arch in ("cpu", "opengl", "gles") else int(device_id)
            )
            old_runtime = self.runtime
            # Complete queued work before invalidating wrappers.  This is
            # essential for the same-size allocation cache: a retired handle
            # may be reusable only in its original runtime generation.
            try:
                if old_runtime:
                    _LIB.sync_runtime(old_runtime)
            except Exception:
                pass
            for mod in list(self.modules.values()):
                try:
                    if mod.module_ptr:
                        _LIB.destroy_aot_module(mod.module_ptr)
                except Exception:
                    pass
                mod.module_ptr = None
            self.modules = {}
            self.recorded_pipelines.clear()
            getattr(self, "_pipeline_recordings", {}).clear()
            if hasattr(self, "_local"):
                self._local.auto_pipeline_context = None
            try:
                self._drain_retired(already_synchronized=True)
            except Exception:
                pass
            self._invalidate_live_buffers(old_runtime)
            self._pipeline_intermediates = {}
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
                        "gles": 4,
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
                self._memory_governor.device_provider = self._device_memory_provider
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
            if getattr(self, "arch", "").lower() == "cuda":
                ensure_cuda_context(getattr(self, "device_id", 0))
            if not getattr(self, "_destroyed", False):
                self._destroyed = True

                # 1. Shutdown async executor gracefully (no new jobs)
                for future in tuple(getattr(self, "_async_futures", ())):
                    try:
                        future.cancel()
                    except Exception:
                        pass
                if self._executor is not None:
                    try:
                        self._executor.shutdown(wait=False, cancel_futures=True)
                    except TypeError:
                        # Python < 3.9 does not support cancel_futures
                        self._executor.shutdown(wait=False)
                    self._executor = None
                getattr(self, "_async_futures", set()).clear()
                self._async_reservations = 0

                # Stop queued work before releasing pipeline/staging/live
                # handles.  Some drivers tolerate freeing during teardown,
                # while others report a device error or keep the stale handle
                # alive until the context is gone.
                try:
                    if getattr(self, "runtime", None):
                        _LIB.sync_runtime(self.runtime)
                except Exception:
                    pass

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
                getattr(self, "_pipeline_recordings", {}).clear()

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

                # Retired handles are not in the free pool yet.  Synchronize
                # once, promote them, then let the normal pool drain release
                # every native allocation before the runtime is destroyed.
                try:
                    self._drain_retired(wait=True)
                except Exception:
                    pass

                # Ordinary user-owned buffers are not registered in a
                # pipeline/staging dictionary.  Invalidate them explicitly
                # so Python wrappers cannot later free their numeric handles
                # against a destroyed runtime.
                self._invalidate_live_buffers(self.runtime)

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
                    os.environ.get("AOT_SAFE_TEARDOWN", "0") == "1"
                    and self.arch.lower() in ("vulkan", "opengl")
                )
                if (
                    runtime_to_destroy
                    and destroy_engine is not None
                    and not skip_native_destroy
                ):
                    try:
                        destroy_engine(runtime_to_destroy)
                    except Exception:
                        pass
                elif skip_native_destroy:
                    print(
                        f"[AOTEngine] Intel native {self.arch.upper()} safe teardown: native context destructor skipped"
                    )
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

_initial_engine = None


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
        global _RUNTIME, _initial_engine
        target = object.__getattribute__(self, "_target")
        if (
            target is None
            or getattr(target, "_destroyed", False)
            or getattr(target, "runtime", None) is None
        ):
            target = AOTEngine(
                arch=getattr(target, "arch", None) if target is not None else None,
                device_id=getattr(target, "device_id", 0) if target is not None else 0,
            )
            object.__setattr__(self, "_target", target)
            _initial_engine = target
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


engine = _EngineHandle(None)
_RUNTIME = None


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
    shape,
    dtype=np.float32,
    is_vector=False,
    vector_dim=None,
    host_accessible=False,
) -> TaichiGPUBuffer:
    """
    OpenCV-style Data Output Allocation.
    Creates an empty GPU VRAM buffer ready for writing.
    """
    return engine.allocate(
        shape,
        dtype=dtype,
        is_vector=is_vector,
        vector_dim=vector_dim,
        host_accessible=host_accessible,
    )
