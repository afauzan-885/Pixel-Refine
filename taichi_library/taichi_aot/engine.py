import ctypes
import os
import sys
import atexit
import signal
import weakref
import numpy as np
import typing
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future

# -------------------------------------------------------------------------
# CUDA Pinned Memory Allocator (Host Page-Locked)
# -------------------------------------------------------------------------
class PinnedMemoryAllocator:
    _nvcuda = None
    _ctx = None
    _dev = None

    @classmethod
    def init(cls):
        if cls._nvcuda is not None:
            return True
        try:
            # Only try to load if CUDA is active/intended
            cls._nvcuda = ctypes.CDLL("nvcuda.dll")
            res = cls._nvcuda.cuInit(0)
            if res != 0:
                cls._nvcuda = None
                return False
                
            dev = ctypes.c_int(0)
            res = cls._nvcuda.cuDeviceGet(ctypes.byref(dev), 0)
            if res != 0:
                cls._nvcuda = None
                return False
            cls._dev = dev.value
            
            ctx = ctypes.c_void_p()
            res = cls._nvcuda.cuCtxCreate(ctypes.byref(ctx), 0, dev)
            if res != 0:
                cls._nvcuda = None
                return False
            cls._ctx = ctx.value
            
            # Setup APIs
            cls._nvcuda.cuMemAllocHost.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_size_t]
            cls._nvcuda.cuMemAllocHost.restype = ctypes.c_int
            cls._nvcuda.cuMemFreeHost.argtypes = [ctypes.c_void_p]
            cls._nvcuda.cuMemFreeHost.restype = ctypes.c_int
            cls._nvcuda.cuCtxSetCurrent.argtypes = [ctypes.c_void_p]
            cls._nvcuda.cuCtxSetCurrent.restype = ctypes.c_int
            cls._nvcuda.cuCtxDestroy.argtypes = [ctypes.c_void_p]
            cls._nvcuda.cuCtxDestroy.restype = ctypes.c_int
            
            print("[PinnedMemoryAllocator] CUDA Pinned Memory Allocator initialized successfully.")
            return True
        except Exception:
            cls._nvcuda = None
            return False

    @classmethod
    def allocate(cls, size_bytes):
        if not cls.init():
            return None
        try:
            ptr = ctypes.c_void_p()
            cls._nvcuda.cuCtxSetCurrent(cls._ctx)
            res = cls._nvcuda.cuMemAllocHost(ctypes.byref(ptr), size_bytes)
            if res != 0:
                return None
            return ptr
        except Exception:
            return None

    @classmethod
    def free(cls, ptr):
        if cls._nvcuda is None or ptr is None:
            return
        try:
            cls._nvcuda.cuCtxSetCurrent(cls._ctx)
            cls._nvcuda.cuMemFreeHost(ptr)
        except Exception:
            pass

    @classmethod
    def cleanup(cls):
        if cls._nvcuda is not None and cls._ctx is not None:
            try:
                cls._nvcuda.cuCtxDestroy(cls._ctx)
            except Exception:
                pass
            cls._ctx = None
            cls._nvcuda = None

_ctypes_map = {
    np.float32: ctypes.c_float,
    np.int32: ctypes.c_int32,
    np.uint8: ctypes.c_uint8,
    np.uint16: ctypes.c_uint16,
    np.float64: ctypes.c_double,
}

def allocate_pinned_numpy(shape, dtype) -> np.ndarray:
    """Allocates a numpy array mapped to CUDA pinned (page-locked) host memory.
    Falls back to normal np.zeros if CUDA is not available.
    Memory is automatically freed when the array is garbage collected.
    """
    dtype_np = np.dtype(dtype)
    try:
        if PinnedMemoryAllocator.init():
            size_bytes = int(np.prod(shape) * dtype_np.itemsize)
            ptr = PinnedMemoryAllocator.allocate(size_bytes)
            if ptr is not None:
                ctype_type = _ctypes_map.get(dtype_np.type, ctypes.c_ubyte)
                ptr_cast = ctypes.cast(ptr, ctypes.POINTER(ctype_type))
                arr = np.ctypeslib.as_array(ptr_cast, shape=shape)
                weakref.finalize(arr, PinnedMemoryAllocator.free, ptr)
                return arr
    except Exception:
        pass
    return np.zeros(shape, dtype=dtype_np)

# -------------------------------------------------------------------------
# Auto-Destruction & Job Object Configuration
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
_CLEAN_ZOMBIES = os.environ.get("PIXEL_REFINE_CLEAN_ZOMBIES", "1") != "0"

_win32_job_handle = None

def _setup_windows_job_object():
    """Binds the current process and all future child processes (like vulkaninfo.exe)
    to a Win32 Job Object configured to kill them automatically on termination.
    Prevents zombie processes from leaking VRAM.
    """
    global _win32_job_handle
    if os.name != "nt":
        return
    try:
        import ctypes
        from ctypes import wintypes
        
        kernel32 = ctypes.windll.kernel32
        job_handle = kernel32.CreateJobObjectW(None, None)
        if job_handle:
            # Set job limits: kill on job close
            # Structure size is 144 bytes on 64-bit Windows. LimitFlags is at offset 16.
            # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
            info = bytearray(144)
            info[16:20] = b"\x00\x20\x00\x00"
            success = kernel32.SetInformationJobObject(
                job_handle,
                9,  # JobObjectExtendedLimitInformation
                bytes(info),
                len(info),
            )
            if success:
                current_process = kernel32.GetCurrentProcess()
                kernel32.AssignProcessToJobObject(job_handle, current_process)
                _win32_job_handle = job_handle
                sys.stderr.write("[AOTEngine] Win32 Job Object initialized successfully (Anti-Zombie PID enabled).\n")
                sys.stderr.flush()
    except Exception as e:
        sys.stderr.write(f"[AOTEngine] Failed to setup Win32 Job Object: {e}\n")
        sys.stderr.flush()


def configure_auto_destroy(
    heartbeat_timeout=None,
    op_timeout=None,
    lock_timeout=None,
    error_threshold=None,
    error_window=None,
    enabled=None,
):
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
_last_activity_time = time.monotonic()
_op_start_time = 0.0
_op_name = ""
_lock_wait_start = 0.0
_lock_wait_name = ""
_error_timestamps = []
_vram_reclaimed = False


def _heartbeat():
    global _last_activity_time, _vram_reclaimed
    if not _AUTO_DESTROY_ENABLED:
        return
    with _heartbeat_lock:
        _last_activity_time = time.monotonic()
        _vram_reclaimed = False


def _op_begin(name: str):
    global _op_start_time, _op_name, _last_activity_time, _vram_reclaimed
    if not _AUTO_DESTROY_ENABLED:
        return
    with _heartbeat_lock:
        _op_start_time = time.monotonic()
        _op_name = name
        _last_activity_time = _op_start_time
        _vram_reclaimed = False


def _op_end():
    global _op_start_time, _op_name, _last_activity_time, _vram_reclaimed
    if not _AUTO_DESTROY_ENABLED:
        return
    with _heartbeat_lock:
        _op_start_time = 0.0
        _op_name = ""
        _last_activity_time = time.monotonic()
        _vram_reclaimed = False


def _lock_wait_begin(name: str):
    global _lock_wait_start, _lock_wait_name
    if not _AUTO_DESTROY_ENABLED:
        return
    with _heartbeat_lock:
        _lock_wait_start = time.monotonic()
        _lock_wait_name = name


def _lock_wait_end():
    global _lock_wait_start, _lock_wait_name
    if not _AUTO_DESTROY_ENABLED:
        return
    with _heartbeat_lock:
        _lock_wait_start = 0.0
        _lock_wait_name = ""


def _record_error():
    if not _AUTO_DESTROY_ENABLED:
        return
    now = time.monotonic()
    with _heartbeat_lock:
        _error_timestamps.append(now)
        cutoff = now - _ERROR_WINDOW_S
        while _error_timestamps and _error_timestamps[0] < cutoff:
            _error_timestamps.pop(0)


# -------------------------------------------------------------------------
# Watchdog Thread: GIL-safe and deadlock-safe
# -------------------------------------------------------------------------
_WATCHDOG_INTERVAL_S = 2.0


def _watchdog_run():
    global _last_activity_time, _vram_reclaimed
    main_thread = threading.main_thread()
    while True:
        time.sleep(_WATCHDOG_INTERVAL_S)
        if not _AUTO_DESTROY_ENABLED:
            if not main_thread.is_alive():
                _global_cleanup("watchdog-main-thread-dead")
                os._exit(1)
                break
            continue

        now = time.monotonic()

        # Try-acquire heartbeat lock to avoid GIL-deadlocks
        has_lock = _heartbeat_lock.acquire(blocking=True, timeout=0.1)
        if not has_lock:
            continue
        try:
            activity_age = now - _last_activity_time
            op_elapsed = (now - _op_start_time) if _op_start_time > 0 else 0.0
            current_op = _op_name
            lock_wait_elapsed = (
                (now - _lock_wait_start) if _lock_wait_start > 0 else 0.0
            )
            lock_wait_op = _lock_wait_name
            recent_errors = len(_error_timestamps)
        finally:
            _heartbeat_lock.release()

        # 1. Main thread dead
        if not main_thread.is_alive():
            try:
                sys.stderr.write("[AOTEngine Watchdog] Main thread dead. Cleaning VRAM.\n")
                sys.stderr.flush()
            except Exception:
                pass
            _force_global_cleanup("watchdog-main-thread-dead")
            os._exit(1)
            break

        # 2. Single operation hung
        if op_elapsed > _OP_TIMEOUT_S:
            try:
                sys.stderr.write(
                    f"[AOTEngine Watchdog] Operation '{current_op}' hung for {op_elapsed:.1f}s. Cleaning VRAM.\n"
                )
                sys.stderr.flush()
            except Exception:
                pass
            _force_global_cleanup(f"op-timeout:{current_op}:{op_elapsed:.0f}s")
            os._exit(1)
            break

        # 3. Lock contention
        if lock_wait_elapsed > _LOCK_CONTENTION_S:
            try:
                sys.stderr.write(
                    f"[AOTEngine Watchdog] Lock contention in '{lock_wait_op}' for {lock_wait_elapsed:.1f}s. Cleaning VRAM.\n"
                )
                sys.stderr.flush()
            except Exception:
                pass
            _force_global_cleanup(f"lock-contention:{lock_wait_op}:{lock_wait_elapsed:.0f}s")
            os._exit(1)
            break

        # 4. Heartbeat stale (Idle -> Reclaim VRAM)
        if activity_age > _HEARTBEAT_TIMEOUT_S and op_elapsed == 0.0:
            if not _vram_reclaimed:
                try:
                    sys.stderr.write(
                        f"[AOTEngine Watchdog] Idle for {activity_age:.1f}s. Reclaiming VRAM.\n"
                    )
                    sys.stderr.flush()
                except Exception:
                    pass
                
                try:
                    instances = list(AOTEngine._instances.items())
                    for key, inst in instances:
                        locked = inst._lock.acquire(blocking=True, timeout=0.1)
                        if locked:
                            try:
                                # Clear cached staging buffers
                                for entries in list(getattr(inst, '_staging_pool', {}).values()):
                                    for entry in entries:
                                        buf = entry.get('buffer')
                                        if buf and buf.handle is not None and buf.is_owner:
                                            try:
                                                inst.backend.free_buffer(inst.runtime, buf.handle)
                                                buf.handle = None
                                                buf.is_owner = False
                                            except Exception:
                                                pass
                                inst._staging_pool = {}
                                inst.buffer_pool.clear()
                            finally:
                                inst._lock.release()
                    import gc as _gc
                    _gc.collect()
                except Exception as e:
                    try:
                        sys.stderr.write(f"[AOTEngine Watchdog] Reclamation error: {e}\n")
                        sys.stderr.flush()
                    except Exception:
                        pass
                
                with _heartbeat_lock:
                    _vram_reclaimed = True
            
            with _heartbeat_lock:
                _last_activity_time = now
            continue

        # 5. Error circuit breaker
        if recent_errors >= _ERROR_THRESHOLD:
            try:
                sys.stderr.write(
                    f"[AOTEngine Watchdog] {recent_errors} errors inside {_ERROR_WINDOW_S}s window. Terminating.\n"
                )
                sys.stderr.flush()
            except Exception:
                pass
            _force_global_cleanup(f"error-breaker:{recent_errors}-errors")
            os._exit(1)
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
# Types mapping and argument helpers
# -------------------------------------------------------------------------
from .backends import DynamicArg

dtype_map = {
    np.float32: 0,
    np.int32: 1,
    np.uint8: 2,
    np.uint16: 3,
    np.float64: 0,
}


def _populate_dynamic_arg(arg: DynamicArg, name_bytes, value, context_name="Unknown"):
    arg.name = name_bytes

    if isinstance(value, (int, np.integer)):
        arg.arg_type = 1
        arg.dtype = 1  # i32
        arg.val_u64 = int(value)
    elif isinstance(value, (float, np.floating)):
        arg.arg_type = 1
        arg.dtype = 0  # f32
        arg.val_u64 = ctypes.cast(
            ctypes.pointer(ctypes.c_float(float(value))),
            ctypes.POINTER(ctypes.c_uint64),
        ).contents.value
    elif isinstance(value, (TaichiGPUBuffer, TaichiPlaceholder)):
        arg.arg_type = 0

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
            if dim_count >= 2 and shape[-1] == v_dim:
                arg.dim_count = dim_count - 1
                for d in range(dim_count - 1):
                    arg.shape[d] = shape[d]
                arg.elem_dim_count = 1
                arg.elem_shape[0] = v_dim
            else:
                arg.dim_count = dim_count
                for d in range(dim_count):
                    arg.shape[d] = shape[d]
                arg.elem_dim_count = 1
                arg.elem_shape[0] = v_dim
        else:
            arg.dim_count = dim_count
            for d in range(dim_count):
                arg.shape[d] = shape[d]
            arg.elem_dim_count = 0

        arg.val_u64 = ctypes.c_uint64(value.handle)
    else:
        if hasattr(value, "ptr"):
            arg.arg_type = 0
            arg.val_u64 = value.ptr
            arg.dtype = 0
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
# Fallback Monolith Bridge (Legacy)
# -------------------------------------------------------------------------
_LIB_fallback = None
_RUNTIME = None


def _init_aot_bridge():
    global _LIB_fallback
    if _LIB_fallback is not None:
        return

    os.environ["VK_LOADER_DEBUG"] = "error"
    if os.name == "nt":
        try:
            ctypes.CDLL("msvcrt.dll")._putenv(b"VK_LOADER_DEBUG=error")
        except Exception:
            pass

    script_dir = os.path.dirname(os.path.abspath(__file__))
    aot_dll_dir = os.path.abspath(
        os.path.join(script_dir, "../taichi_algorithm/aot_py/aot_dll")
    )
    engine_dll_path = os.path.join(aot_dll_dir, "taichi_aot_engine.dll")

    if os.name == "nt" and os.path.exists(aot_dll_dir):
        try:
            os.add_dll_directory(aot_dll_dir)
        except Exception:
            pass

        try:
            import importlib.util
            spec = importlib.util.find_spec("taichi")
            if spec is not None and spec.origin is not None:
                ti_root = os.path.dirname(spec.origin)
                ti_bin = os.path.join(ti_root, "_lib", "c_api", "bin")
                if os.path.exists(ti_bin):
                    os.add_dll_directory(ti_bin)
                ti_runtime = os.path.join(ti_root, "_lib", "runtime")
                if os.path.exists(ti_runtime):
                    os.environ["TI_LIB_DIR"] = ti_runtime
            _setup_windows_job_object()
        except Exception:
            pass

    try:
        from .backends import BaseAOTBackend
        # BaseAOTBackend with fallback DLL
        _LIB_fallback = BaseAOTBackend("taichi_aot_engine.dll")
    except Exception as e:
        raise RuntimeError(
            f"Failed to load Generic Fallback AOT Engine DLL at {engine_dll_path}\nError: {e}"
        )


def configure_taichi_backend(prefer: str = None, device_memory_GB: float = None):
    try:
        import taichi as ti
    except Exception:
        raise RuntimeError("Taichi is not installed or cannot be imported.")

    env_pref = os.environ.get("PIXEL_REFINE_TAICHI_ARCH")
    arch_choice = prefer or env_pref or "vulkan"
    arch_choice = arch_choice.lower()

    arch_map = {
        "vulkan": getattr(ti, "vulkan", getattr(ti, "gpu", None)),
        "cuda": getattr(ti, "cuda", None),
        "gpu": getattr(ti, "gpu", None),
        "cpu": getattr(ti, "cpu", None),
    }

    arch = arch_map.get(arch_choice, None)
    if arch is None:
        arch = getattr(ti, "vulkan", getattr(ti, "gpu", ti.cpu))

    init_kwargs = {"default_fp": ti.f32}
    if device_memory_GB is not None:
        init_kwargs["device_memory_GB"] = device_memory_GB

    if arch_choice == "cpu":
        import multiprocessing
        init_kwargs["cpu_max_num_threads"] = multiprocessing.cpu_count()
        init_kwargs["fast_math"] = True
        init_kwargs["advanced_optimization"] = True
        init_kwargs["cpu_optimization_level"] = 3
        os.environ["TI_CPU_MAX_NUM_THREADS"] = str(init_kwargs["cpu_max_num_threads"])

    print(f"[engine.configure_taichi_backend] Initializing Taichi with arch={arch_choice}")
    ti.init(arch=arch, **init_kwargs)


# -------------------------------------------------------------------------
# GPU Buffer Manager: Two-Tier Pooling
# -------------------------------------------------------------------------
class BufferPool:
    """Two-Tier Pool: Tracks handles by exact size or block-aligned size (256x256 tiles)."""

    def __init__(self, engine=None):
        self.engine = engine
        self.free_buffers = {}  # size_bytes -> list of handles
        self._lock = threading.Lock()

    def acquire(self, size, aligned_size):
        with self._lock:
            # Tier 1: Exact match
            if size in self.free_buffers and self.free_buffers[size]:
                return self.free_buffers[size].pop()
            # Tier 2: Rounded-block match
            if aligned_size in self.free_buffers and self.free_buffers[aligned_size]:
                return self.free_buffers[aligned_size].pop()
            return None

    def store(self, size, handle):
        with self._lock:
            if size not in self.free_buffers:
                self.free_buffers[size] = []
            self.free_buffers[size].append(handle)

    def clear(self):
        with self._lock:
            runtime = self.engine.runtime if self.engine else _RUNTIME
            backend = self.engine.backend if self.engine else _LIB_fallback
            if backend and runtime:
                for size, handles in self.free_buffers.items():
                    for h in handles:
                        try:
                            backend.free_buffer(runtime, h)
                            if self.engine:
                                self.engine.total_physical_vram_allocated_bytes -= size
                        except Exception:
                            pass
            self.free_buffers = {}


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
        allocated_size=None,
    ):
        self.size_bytes = size_bytes
        self.allocated_size = allocated_size if allocated_size is not None else size_bytes
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
        if self.handle is not None and self.is_owner:
            if self.engine and self.engine.current_pipeline:
                if getattr(self, "is_pipeline_intermediate", False) or (
                    self.engine.current_pipeline in self.associated_pipelines
                ):
                    return

            if self.engine and not self.host_accessible:
                self.engine.buffer_pool.store(self.allocated_size, self.handle)
                self.handle = None
                self.is_owner = False
            else:
                self.destroy()

    def destroy(self):
        _heartbeat()
        if self.handle is not None and self.is_owner:
            if self.engine and self.engine.current_pipeline:
                if getattr(self, "is_pipeline_intermediate", False) or (
                    self.engine.current_pipeline in self.associated_pipelines
                ):
                    return

            if self.associated_pipelines:
                pipelines_to_clear = list(self.associated_pipelines)
                self.associated_pipelines.clear()
                if self.engine:
                    for pipe_name in pipelines_to_clear:
                        self.engine.clear_pipeline_by_name(pipe_name)

            runtime = self.engine.runtime if self.engine else _RUNTIME
            backend = self.engine.backend if self.engine else _LIB_fallback
            if backend and runtime:
                if self.engine and hasattr(self.engine, "_lock"):
                    with self.engine._lock:
                        backend.free_buffer(runtime, self.handle)
                        if hasattr(self, "allocated_size"):
                            self.engine.total_physical_vram_allocated_bytes -= self.allocated_size
                else:
                    backend.free_buffer(runtime, self.handle)
            self.handle = None
            self.is_owner = False

    def _force_destroy(self):
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

    def to_numpy(self):
        _heartbeat()
        out = np.zeros(self.shape, dtype=self.dtype)
        runtime = self.engine.runtime if self.engine else _RUNTIME
        engine = self.engine
        backend = engine.backend if engine else _LIB_fallback
        if engine and hasattr(engine, "_lock"):
            _lock_wait_begin("to_numpy")
            with engine._lock:
                _lock_wait_end()
                if self.host_accessible:
                    _op_begin("read_from_gpu_buffer")
                    try:
                        backend.read_buffer(
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
                            backend.copy_buffer(
                                runtime, self.handle, staging.handle, self.size_bytes
                            )
                            backend.read_buffer(
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
            if self.host_accessible and backend:
                _op_begin("read_from_gpu_buffer")
                try:
                    backend.read_buffer(
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
        backend = self.engine.backend if self.engine else _LIB_fallback
        if self.engine and hasattr(self.engine, "_lock"):
            with self.engine._lock:
                return backend.map_buffer(runtime, self.handle)
        return backend.map_buffer(runtime, self.handle)

    def unmap(self):
        runtime = self.engine.runtime if self.engine else _RUNTIME
        backend = self.engine.backend if self.engine else _LIB_fallback
        if self.engine and hasattr(self.engine, "_lock"):
            with self.engine._lock:
                backend.unmap_buffer(runtime, self.handle)
        else:
            backend.unmap_buffer(runtime, self.handle)

    def cast(self, target_dtype, host_accessible=False):
        self_dtype_type = np.dtype(self.dtype).type
        target_dtype_type = np.dtype(target_dtype).type
        if self_dtype_type == target_dtype_type:
            return self
        dtype_map_val = {np.float32: 0, np.int32: 1, np.uint8: 2, np.uint16: 3}
        if (
            self_dtype_type not in dtype_map_val
            or target_dtype_type not in dtype_map_val
            or not self.host_accessible
            or not host_accessible
        ):
            return self.engine.upload(self.to_numpy().astype(target_dtype))

        engine = self.engine if self.engine is not None else AOTEngine()
        backend = engine.backend
        with engine._lock:
            dst = engine.allocate(
                self.shape, dtype=target_dtype, host_accessible=host_accessible
            )
            src_ptr = self.map()
            dst_ptr = dst.map()
            try:
                num_elements = np.prod(self.shape)
                backend.cast_buffer(
                    ctypes.c_void_p(src_ptr),
                    ctypes.c_void_p(dst_ptr),
                    int(num_elements),
                    dtype_map_val[self_dtype_type],
                    dtype_map_val[target_dtype_type],
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
            allocated_size=self.allocated_size,
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

    def __del__(self):
        if self.module_ptr and self.engine:
            self.engine.backend.destroy_module(self.module_ptr)

    def run(self, graph_name, **kwargs):
        num_args = len(kwargs)
        args_array = (DynamicArg * num_args)()
        arg_names = [k.encode("utf-8") for k in kwargs.keys()]

        for i, (k, v) in enumerate(kwargs.items()):
            try:
                _populate_dynamic_arg(
                    args_array[i], arg_names[i], v, context_name=graph_name
                )
            except Exception as e:
                raise ValueError(
                    f"Failed to prepare argument '{k}' for kernel '{graph_name}':\n{str(e)}"
                )

        engine = self.engine if self.engine is not None else AOTEngine()
        backend = engine.backend
        if engine.current_pipeline:
            _lock_wait_begin(f"run:{graph_name}:pipeline")
            with engine._lock:
                _lock_wait_end()
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

                _op_begin(f"add_to_pipeline:{graph_name}")
                try:
                    backend.add_to_pipeline(
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
            _lock_wait_begin(f"run:{graph_name}")
            try:
                with engine._lock:
                    _lock_wait_end()
                    _op_begin(f"run_aot_graph:{graph_name}")
                    try:
                        backend.run_graph(
                            engine.runtime,
                            self.module_ptr,
                            graph_name.encode("utf-8"),
                            args_array,
                            num_args,
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


class AOTEngine:
    _instances = {}
    _active_arch = "vulkan"
    _placeholder_id_counter = 0xFFFFFF00

    def __new__(cls, arch="vulkan", device_id=None):
        if arch.lower() == "cpu":
            import multiprocessing
            num_cores = multiprocessing.cpu_count()
            if "TI_CPU_MAX_NUM_THREADS" not in os.environ:
                os.environ["TI_CPU_MAX_NUM_THREADS"] = str(num_cores)
        
        _init_aot_bridge()

        if device_id is None:
            env_device = os.environ.get("PIXEL_REFINE_AOT_DEVICE")
            if env_device is not None:
                device_id = int(env_device)
            else:
                device_id = 0
                try:
                    devices_str = _LIB_fallback.scan_devices()
                    device_list = [d.strip().lower() for d in devices_str.split(";")]
                    for idx, dev_name in enumerate(device_list):
                        if "nvidia" in dev_name or "geforce" in dev_name:
                            device_id = idx
                            break
                except Exception:
                    pass

        key = (arch.lower(), device_id)
        if key not in cls._instances:
            instance = super(AOTEngine, cls).__new__(cls)
            instance.arch = arch
            instance.device_id = device_id

            arch_id = {"vulkan": 0, "cuda": 1, "cpu": 2}.get(arch.lower(), 0)

            # Choose and load modular backend driver
            dev_mode = os.environ.get("PIXEL_REFINE_DEV_MODE", "0") != "0"
            arch_lower = arch.lower()
            try:
                if arch_lower == "vulkan":
                    from .backends.vulkan import VulkanAOTBackend
                    instance.backend = VulkanAOTBackend()
                elif arch_lower == "cuda":
                    from .backends.cuda import CudaAOTBackend
                    instance.backend = CudaAOTBackend()
                elif arch_lower == "cpu":
                    from .backends.cpu import CpuAOTBackend
                    instance.backend = CpuAOTBackend()
                else:
                    raise ValueError(f"Unsupported arch: {arch}")
            except Exception as e:
                if dev_mode:
                    raise RuntimeError(f"Failed to load modular backend '{arch_lower}' in DEV mode: {e}")
                else:
                    sys.stderr.write(f"[AOTEngine] Warning: failed to load modular backend '{arch_lower}' ({e}). Falling back to monolith engine.\n")
                    sys.stderr.flush()
                    instance.backend = _LIB_fallback

            _op_begin("init_aot_engine")
            _init_result = [None]
            _init_error = [None]

            def _do_init():
                try:
                    _init_result[0] = instance.backend.init_engine(arch_id, device_id)
                except Exception as e:
                    _init_error[0] = e

            _init_thread = threading.Thread(target=_do_init, daemon=True)
            _init_thread.start()
            _init_thread.join(timeout=_INIT_TIMEOUT_S)
            _op_end()

            if _init_thread.is_alive():
                sys.stderr.write(
                    f"[AOTEngine] CRITICAL: init_engine() hung for >{_INIT_TIMEOUT_S}s.\n"
                )
                sys.stderr.flush()
                raise RuntimeError(
                    f"init_engine() timed out after {_INIT_TIMEOUT_S}s. GPU driver is likely hung."
                )

            if _init_error[0] is not None:
                raise RuntimeError(f"init_engine() failed: {_init_error[0]}")

            instance.runtime = _init_result[0]
            if not instance.runtime:
                raise RuntimeError(
                    f"Failed to initialize {arch.upper()} AOT Runtime on device {device_id}."
                )

            print(f"[AOTEngine] Runtime initialized on '{arch.upper()}' (Device {device_id})")

            instance.modules = {}
            instance.buffer_pool = BufferPool(instance)
            instance._local = threading.local()
            instance._staging_pool = {}
            instance._pipeline_intermediates = {}
            instance.total_physical_vram_allocated_bytes = 0
            instance.recorded_pipelines = set()
            instance._executor = None
            instance._lock = threading.RLock()

            cls._instances[key] = instance
        return cls._instances[key]

    def get_allocated_vram_bytes(self):
        return getattr(self, "total_physical_vram_allocated_bytes", 0)

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
        class Recorder:
            def __init__(self, engine, name):
                self.engine, self.name = engine, name

            def __enter__(self):
                module = (
                    next(iter(self.engine.modules.values()))
                    if self.engine.modules
                    else None
                )
                self.engine.backend.clear_pipeline(
                    module.module_ptr if module else None, self.name.encode("utf-8")
                )
                self.engine.current_pipeline = self.name
                self.engine.recorded_pipelines.add(self.name)

                if self.name in self.engine._pipeline_intermediates:
                    for buf in self.engine._pipeline_intermediates[self.name]:
                        buf._force_destroy()
                    del self.engine._pipeline_intermediates[self.name]
                return self

            def __exit__(self, *args):
                self.engine.current_pipeline = None

        return Recorder(self, name)

    def use_pipeline(self, name, overrides=None):
        _init_aot_bridge()
        if name not in self.recorded_pipelines:
            print(f"[AOTEngine WARNING] Pipeline '{name}' is not recorded. Skipping execution.")
            return

        ovr = overrides or {}
        n = len(ovr)
        handles = (ctypes.c_uint64 * n)()
        args = (DynamicArg * n)()
        arg_names = [b"override"] * n
        for i, (p, b) in enumerate(ovr.items()):
            handles[i] = ctypes.c_uint64(p.handle)
            _populate_dynamic_arg(args[i], arg_names[i], b)
        _lock_wait_begin(f"use_pipeline:{name}")
        with self._lock:
            _lock_wait_end()
            _op_begin(f"run_pipeline:{name}")
            try:
                self.backend.run_pipeline(self.runtime, name.encode("utf-8"), handles, args, n)
            except Exception:
                _record_error()
                raise
            finally:
                _op_end()

    def _get_block_aligned_size(self, shape, dtype):
        if len(shape) >= 2:
            h, w = shape[0], shape[1]
            h_aligned = ((h + 255) // 256) * 256
            w_aligned = ((w + 255) // 256) * 256
            num_elements = h_aligned * w_aligned
            for dim in shape[2:]:
                num_elements *= dim
            return int(num_elements * np.dtype(dtype).itemsize)
        return int(np.prod(shape) * np.dtype(dtype).itemsize)

    def allocate(
        self,
        shape,
        dtype=np.float32,
        is_vector=False,
        host_accessible=False,
        vector_dim=None,
    ):
        _lock_wait_begin("allocate")
        with self._lock:
            _lock_wait_end()
            size = int(np.prod(shape) * np.dtype(dtype).itemsize)
            aligned_size = size
            if not host_accessible:
                aligned_size = self._get_block_aligned_size(shape, dtype)

            v_dim = (
                vector_dim
                if vector_dim is not None
                else (shape[-1] if is_vector and len(shape) >= 2 else 1)
            )
            
            handle = None
            if not host_accessible:
                handle = self.buffer_pool.acquire(size, aligned_size)
                
            if not handle:
                _op_begin("allocate_gpu_buffer")
                try:
                    handle = self.backend.allocate_buffer(
                        self.runtime, aligned_size, 1 if host_accessible else 0
                    )
                    self.total_physical_vram_allocated_bytes += aligned_size
                except Exception:
                    _record_error()
                    raise
                finally:
                    _op_end()

            if handle is None or handle == 0:
                _record_error()
                raise RuntimeError(
                    f"\n[AOTEngine Memory Error] Failed to allocate {size/1024/1024:.2f} MB on GPU ({self.arch.upper()}, Device {self.device_id})."
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
                allocated_size=aligned_size,
            )
            if self.current_pipeline:
                buf.is_pipeline_intermediate = True
                buf.associated_pipelines.add(self.current_pipeline)
                if self.current_pipeline not in self._pipeline_intermediates:
                    self._pipeline_intermediates[self.current_pipeline] = []
                self._pipeline_intermediates[self.current_pipeline].append(buf)
            return buf

    def clear_pipeline_by_name(self, name):
        with self._lock:
            if name in self.recorded_pipelines:
                self.recorded_pipelines.remove(name)
            self.backend.clear_pipeline(None, name.encode("utf-8"))
            if name in self._pipeline_intermediates:
                bufs = self._pipeline_intermediates[name]
                for buf in bufs:
                    if name in buf.associated_pipelines:
                        buf.associated_pipelines.remove(name)
                    if not buf.associated_pipelines:
                        buf._force_destroy()
                del self._pipeline_intermediates[name]

    def clear_pipelines(self):
        with self._lock:
            for name in list(self._pipeline_intermediates.keys()):
                self.clear_pipeline_by_name(name)
            self.recorded_pipelines.clear()

    def get_staging_buffer(self, shape, dtype):
        return self.acquire_staging_buffer(shape, dtype)

    def acquire_staging_buffer(self, shape, dtype):
        size = int(np.prod(shape) * np.dtype(dtype).itemsize)
        key = (size, np.dtype(dtype).name)
        with self._lock:
            if key not in self._staging_pool:
                self._staging_pool[key] = []

            for entry in self._staging_pool[key]:
                if not entry["leased"]:
                    entry["leased"] = True
                    return entry["buffer"]

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
        obj_type = self._is_external_gpu_obj(data)
        shape = getattr(data, "shape", (1,))
        dtype = np.float32

        if obj_type == "pytorch":
            import torch
            dtype_map_pt = {
                torch.float32: np.float32,
                torch.uint8: np.uint8,
                torch.int32: np.int32,
            }
            dtype = dtype_map_pt.get(data.dtype, np.float32)
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
                self.backend.copy_buffer(
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

    def upload(self, data, is_vector=False, vector_dim=3, dst=None):
        _heartbeat()

        if isinstance(data, TaichiGPUBuffer):
            if dst is not None and dst is not data:
                # Copy from GPU buffer data to dst buffer
                from . import copy_field
                copy_field(data, dst)
                return dst
            return data

        ext_type = self._is_external_gpu_obj(data)

        if not is_vector and hasattr(data, "shape"):
            if len(data.shape) == 3:
                if data.shape[2] == 3:
                    is_vector = True
                    vector_dim = 3
                elif data.shape[2] == 2:
                    is_vector = True
                    vector_dim = 2

        if ext_type:
            # For GPU objects, if dst is provided we might need to handle it differently,
            # but _upload_fast_interop handles allocation. Let's redirect if no dst.
            if dst is None:
                return self._upload_fast_interop(
                    data, is_vector=is_vector, vector_dim=vector_dim
                )
            else:
                tmp = self._upload_fast_interop(
                    data, is_vector=is_vector, vector_dim=vector_dim
                )
                from . import copy_field
                copy_field(tmp, dst)
                tmp.release()
                return dst

        arr = np.ascontiguousarray(data)

        # Normalize data types to optimize memory and prevent C++ AOT crash
        if arr.dtype == np.float64:
            arr = arr.astype(np.float32)
        elif arr.dtype == bool:
            arr = arr.astype(np.int32)
        elif np.issubdtype(arr.dtype, np.integer):
            if arr.dtype not in (np.int32, np.uint8, np.uint16):
                arr = arr.astype(np.int32)

        if dst is not None:
            buf = dst
        else:
            buf = self.allocate(
                arr.shape,
                arr.dtype,
                is_vector=is_vector,
                host_accessible=True,
                vector_dim=vector_dim,
            )

        _op_begin("write_to_gpu_buffer")
        try:
            self.backend.write_buffer(
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
            if p in self.modules:
                return self.modules[p]
            ptr = self.backend.load_module(self.runtime, p.encode("utf-8"))
            if not ptr:
                raise RuntimeError(
                    f"\n[AOTEngine Load Error] Failed to load TCM module at: {p}"
                )
            print(f"[AOTEngine] Loaded TCM module: {os.path.basename(p)}")
            self.modules[p] = AOTModuleWrapper(ptr, self)
            return self.modules[p]

    def imread(self, path):
        _heartbeat()
        w, h, c, d = ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0)
        _lock_wait_begin("imread")
        with self._lock:
            _lock_wait_end()
            _op_begin(f"imread:{os.path.basename(path)}")
            try:
                handle = self.backend.imread(
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
        h, w = buf.shape[0], buf.shape[1]
        c = 1 if len(buf.shape) == 2 else buf.shape[2]
        d = 8 if buf.dtype == np.uint8 else 16
        _lock_wait_begin("imwrite")
        with self._lock:
            _lock_wait_end()
            _op_begin(f"imwrite:{os.path.basename(path)}")
            try:
                res = self.backend.imwrite(
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
                self.backend.sync(self.runtime)
            except Exception:
                _record_error()
                raise
            finally:
                _op_end()

    def reinit(self, device_id=0):
        with self._lock:
            self.runtime = self.backend.init_engine(
                {"vulkan": 0, "cuda": 1, "cpu": 2}.get(self.arch.lower(), 0), device_id
            )
            self.device_id = device_id
            self.modules = {}

    def destroy(self):
        with self._lock:
            if not getattr(self, "_destroyed", False):
                self._destroyed = True

                if self._executor is not None:
                    try:
                        self._executor.shutdown(wait=False, cancel_futures=True)
                    except TypeError:
                        self._executor.shutdown(wait=False)
                    self._executor = None

                for name in list(getattr(self, "_pipeline_intermediates", {}).keys()):
                    try:
                        bufs = self._pipeline_intermediates.pop(name, [])
                        for buf in bufs:
                            buf.is_pipeline_intermediate = False
                            buf.associated_pipelines.discard(name)
                            if buf.handle is not None and buf.is_owner:
                                self.backend.free_buffer(self.runtime, buf.handle)
                                buf.handle = None
                                buf.is_owner = False
                    except Exception:
                        pass
                self.recorded_pipelines.clear()

                for entries in list(getattr(self, "_staging_pool", {}).values()):
                    for entry in entries:
                        buf = entry.get("buffer")
                        if buf and buf.handle is not None and buf.is_owner:
                            try:
                                self.backend.free_buffer(self.runtime, buf.handle)
                                buf.handle = None
                                buf.is_owner = False
                            except Exception:
                                pass
                self._staging_pool = {}

                try:
                    self.buffer_pool.clear()
                except Exception:
                    pass

                for mod in list(self.modules.values()):
                    try:
                        if mod.module_ptr:
                            self.backend.destroy_module(mod.module_ptr)
                            mod.module_ptr = None
                    except Exception:
                        pass
                self.modules = {}

                try:
                    if self.runtime:
                        self.backend.sync(self.runtime)
                except Exception:
                    pass
                self.runtime = None
                _kill_tracked_children()


# =========================================================================
# Zombie GPU Process Cleanup
# =========================================================================
import subprocess as _subprocess
import gc as _gc

_child_pids = set()
_child_pids_lock = threading.Lock()


def _track_child_pid(pid):
    with _child_pids_lock:
        _child_pids.add(pid)


def _win32_force_terminate_process(pid: int) -> bool:
    """Direct Win32 process termination with multi-layer escalation (ctypes)."""
    if os.name != "nt":
        return False
    try:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.windll.kernel32
        ntdll = ctypes.windll.ntdll

        # PROCESS_TERMINATE (0x0001) | PROCESS_QUERY_INFORMATION (0x0400)
        handle = kernel32.OpenProcess(0x0001 | 0x0400, False, pid)
        if not handle:
            return False

        try:
            # Check exit code
            exit_code = wintypes.DWORD()
            if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                if exit_code.value != 259:  # STILL_ACTIVE
                    return True

            # Layer 1: Win32 TerminateProcess
            if kernel32.TerminateProcess(handle, 1):
                # Verify termination
                time.sleep(0.05)
                if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                    if exit_code.value != 259:
                        return True

            # Layer 2: NT API NtTerminateProcess (lower syscall level)
            if ntdll.NtTerminateProcess(handle, 1) == 0:
                time.sleep(0.05)
                if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                    if exit_code.value != 259:
                        return True
        finally:
            kernel32.CloseHandle(handle)
    except Exception:
        pass

    # Layer 5: Fallback subprocess taskkill
    try:
        res = _subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            capture_output=True,
            timeout=3
        )
        return res.returncode == 0
    except Exception:
        return False


def _reset_gpu_device() -> bool:
    """Layer 4: Best-effort DXGI GPU device reset to unblock driver locks."""
    if os.name != "nt":
        return False
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        h_module = kernel32.GetModuleHandleW("dxgi.dll")
        if not h_module:
            h_module = kernel32.LoadLibraryW("dxgi.dll")
        if h_module:
            return True
    except Exception:
        pass
    return False


def _enumerate_zombie_pids(target_names: list) -> list:
    """Enumerate running process IDs matching Target names using Toolhelp32 (no subprocess)."""
    pids = []
    if os.name != "nt":
        return pids
    try:
        import ctypes
        from ctypes import wintypes
        
        kernel32 = ctypes.windll.kernel32
        h_snap = kernel32.CreateToolhelp32Snapshot(0x00000002, 0) # TH32CS_SNAPPROCESS
        if h_snap == -1 or h_snap is None:
            return pids

        class PROCESSENTRY32W(ctypes.Structure):
            _fields_ = [
                ("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.c_void_p),
                ("th32ModuleID", wintypes.DWORD),
                ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", wintypes.LONG),
                ("dwFlags", wintypes.DWORD),
                ("szExeFile", ctypes.c_wchar * 260)
            ]

        pe = PROCESSENTRY32W()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)

        if kernel32.Process32FirstW(h_snap, ctypes.byref(pe)):
            while True:
                exe_name = pe.szExeFile.lower()
                if any(t in exe_name for t in target_names):
                    pids.append((pe.th32ProcessID, pe.szExeFile))
                if not kernel32.Process32NextW(h_snap, ctypes.byref(pe)):
                    break
        kernel32.CloseHandle(h_snap)
    except Exception:
        pass
    return pids


def _kill_tracked_children():
    with _child_pids_lock:
        pids = list(_child_pids)
        _child_pids.clear()
    for pid in pids:
        try:
            if os.name == "nt":
                _win32_force_terminate_process(pid)
            else:
                os.kill(pid, signal.SIGKILL)
        except Exception:
            pass


def _cleanup_zombie_gpu_processes():
    if not _CLEAN_ZOMBIES:
        return

    my_pid = os.getpid()
    killed = []

    try:
        if os.name == "nt":
            # Direct Toolhelp32 Scan (bypassing tasklist)
            zombies = _enumerate_zombie_pids(["vulkaninfo"])
            for pid, name in zombies:
                if pid == my_pid:
                    continue
                if _win32_force_terminate_process(pid):
                    killed.append((pid, name))
            
            if killed:
                _reset_gpu_device()
        else:
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
            f"[AOTEngine] Cleaned {len(killed)} zombie GPU process(es) using multi-layer Win32 escalation: "
            f"{', '.join(f'{name}(pid={pid})' for pid, name in killed)}\n"
        )
        sys.stderr.flush()


def emergency_cleanup():
    _force_global_cleanup("emergency")
    _cleanup_zombie_gpu_processes()
    _kill_tracked_children()
    _gc.collect()
    sys.stderr.write("[AOTEngine] Emergency cleanup complete.\n")
    sys.stderr.flush()


if _CLEAN_ZOMBIES:
    _cleanup_zombie_gpu_processes()

# Set up Win32 Job Object early
_setup_windows_job_object()

engine = AOTEngine()
_RUNTIME = engine.runtime
_LIB = engine.backend._lib if hasattr(engine.backend, "_lib") else engine.backend

# =========================================================================
# Global Resource Cleanup Guard
# =========================================================================
_CLEANUP_LOCK = threading.Lock()
_CLEANUP_DONE = False


def _global_cleanup(reason: str = "atexit", force: bool = False):
    global _CLEANUP_DONE
    with _CLEANUP_LOCK:
        if _CLEANUP_DONE and not force:
            return
        _CLEANUP_DONE = True

    try:
        PinnedMemoryAllocator.cleanup()
    except Exception:
        pass

    try:
        sys.stderr.write(f"[AOTEngine] GPU cleanup triggered (reason={reason})\n")
        sys.stderr.flush()
    except Exception:
        pass

    for key, inst in list(AOTEngine._instances.items()):
        try:
            inst.destroy()
        except Exception:
            pass
    AOTEngine._instances.clear()

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
    _global_cleanup(reason=reason, force=True)


atexit.register(_global_cleanup, "atexit")


def _signal_cleanup_handler(signum, frame):
    _global_cleanup(f"signal-{signum}")
    signal.signal(signum, signal.SIG_DFL)
    os.kill(os.getpid(), signum)


crash_signals = [signal.SIGTERM, signal.SIGINT]
for name in ("SIGSEGV", "SIGILL", "SIGABRT", "SIGFPE"):
    if hasattr(signal, name):
        crash_signals.append(getattr(signal, name))

for _sig in crash_signals:
    try:
        signal.signal(_sig, _signal_cleanup_handler)
    except (OSError, ValueError):
        pass

if hasattr(signal, "SIGBREAK"):
    try:
        signal.signal(signal.SIGBREAK, _signal_cleanup_handler)
    except (OSError, ValueError):
        pass


# -------------------------------------------------------------------------
# OpenCV-style Data Unification (InputArray / OutputArray)
# -------------------------------------------------------------------------
def InputArray(data, is_vector=False, vector_dim=None) -> TaichiGPUBuffer:
    if isinstance(data, (TaichiGPUBuffer, TaichiPlaceholder)):
        return data

    # Zero-Copy interop with PyTorch / CuPy CUDA pointers
    if hasattr(data, "__cuda_array_interface__"):
        try:
            device_ptr = data.__cuda_array_interface__["data"][0]
            if device_ptr:
                shape = data.shape
                dtype_name = str(data.dtype).split(".")[-1]
                dtype_map_str = {
                    "float32": np.float32,
                    "int32": np.int32,
                    "uint8": np.uint8,
                    "uint16": np.uint16,
                    "float64": np.float64,
                }
                dtype_np = dtype_map_str.get(dtype_name, np.float32)
                size_bytes = int(np.prod(shape) * np.dtype(dtype_np).itemsize)
                
                v_dim = (
                    vector_dim
                    if vector_dim is not None
                    else (shape[-1] if is_vector and len(shape) >= 2 else 1)
                )
                
                return TaichiGPUBuffer(
                    size_bytes=size_bytes,
                    handle=device_ptr,
                    shape=shape,
                    dtype=dtype_np,
                    is_vector=is_vector,
                    engine=engine,
                    is_owner=False, # Do not free external memory
                    host_accessible=False,
                    vector_dim=v_dim,
                )
        except Exception:
            pass

    if isinstance(data, (list, tuple, int, float)):
        data = np.array(data, dtype=np.float32)

    return engine.upload(data, is_vector=is_vector, vector_dim=vector_dim)


def OutputArray(
    shape, dtype=np.float32, is_vector=False, vector_dim=None, host_accessible=False
) -> TaichiGPUBuffer:
    return engine.allocate(
        shape,
        dtype=dtype,
        is_vector=is_vector,
        vector_dim=vector_dim,
        host_accessible=host_accessible,
    )
