"""
Taichi Automated Thread Management (ti_thread)
==============================================
Fully automated persistent thread for Taichi operations.
Solves CUDA context issues and minimizes overhead.
"""

import threading
import queue
import functools
import os
import traceback
import sys
import concurrent.futures
import time
import ctypes
import numpy as np

from taichi_vision.config import AOT_MODE

# Check if we are running in AOT mode (default: yes)
_IS_AOT_MODE = any("aot" in arg.lower() or "compiler" in arg.lower() for arg in sys.argv) or AOT_MODE == "1"

if not _IS_AOT_MODE:
    # Force stable CUDA context settings globally before any Taichi import
    os.environ["TI_ENABLE_CUDA_MALLOC_ASYNC"] = "0"

TAICHI_AVAILABLE = False
ti = None
if AOT_MODE == "0":
    try:
        import importlib
        ti = importlib.import_module("taichi")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass


# --- Cache Strategy ---
# Store Taichi kernels in the project root to prevent auto-deletion and speed up JIT.
def _get_project_cache_path():
    """Determine the project root and return the absolute path for the cache."""
    try:
        # e:\...\pixel_refine_desktop\enhance_stack\core\algorithm\taichi_algorithm\taichi_worker.py
        current_file_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
        
        # Go up 5 levels to reach project root
        project_root = current_file_dir
        for _ in range(5):
            project_root = os.path.dirname(project_root)
            
        cache_path = f"{project_root}/taichi_cache"
        
        # Ensure directory exists and is writable
        if not os.path.exists(cache_path):
            os.makedirs(cache_path, exist_ok=True)
            
        if not _IS_AOT_MODE:
            print(f"[TaichiWorker] Using project-level cache at: {cache_path}")
        return cache_path
    except Exception as e:
        print(f"[TaichiWorker] Could not resolve project root for cache: {e}")
        return None

# --- CRITICAL: Set environment variables IMMEDIATELY upon import ---
# This ensures Taichi picks up the project-level cache even if initialized elsewhere.
_global_cache_path = _get_project_cache_path()

if _IS_AOT_MODE:
    pass  # AOT mode: JIT worker and cache envs disabled silently
elif _global_cache_path:
    os.environ["TI_OFFLINE_CACHE_FILE_PATH"] = _global_cache_path
    os.environ["TI_OFFLINE_CACHE_DIR"] = _global_cache_path
    os.environ["TI_OFFLINE_CACHE"] = "1"
    # Optional: Disable async malloc if causing issues on some GPUs
    os.environ["TI_ENABLE_CUDA_MALLOC_ASYNC"] = "0"

# Windows Thread Priority Constants
THREAD_PRIORITY_BELOW_NORMAL = -1


class _TaichiWorker(threading.Thread):
    """Hidden persistent thread for Taichi execution."""

    def __init__(self):
        super().__init__(name="AutomatedTaichiWorker", daemon=True)
        self.task_queue = queue.Queue()
        self.running = True
        self.initialized = False
        self.init_error = None
        self.start()

    def _set_low_priority(self):
        """Reduces thread priority on Windows to keep UI responsive."""
        if sys.platform == "win32":
            try:
                # Set thread priority to Below Normal
                handle = ctypes.windll.kernel32.GetCurrentThread()
                ctypes.windll.kernel32.SetThreadPriority(
                    handle, THREAD_PRIORITY_BELOW_NORMAL
                )
            except Exception as e:
                print(f"[TaichiWorker] Could not set thread priority: {e}")

    def run(self):
        # 1. Reduce priority to leave room for UI thread
        self._set_low_priority()

        if _IS_AOT_MODE:
            # In AOT mode, the background worker does nothing to avoid Context Crashes
            # All calls are executed synchronously in the main thread
            self.initialized = True
            return

        # 2. Initialize Taichi exactly once in this persistent thread
        if not TAICHI_AVAILABLE:
            self.init_error = "Taichi not installed"
            return

        try:
            # Optimization: Pre-calculate CPU thread limit to avoid UI starvation
            import multiprocessing

            num_cores = multiprocessing.cpu_count()
            # Leave at least 2 cores for OS/UI if possible, minimum 1 thread
            reserved_cores = 2 if num_cores > 4 else 1
            ti_cpu_threads = max(1, num_cores - reserved_cores)

            # Allow manual override via environment variable
            from taichi_vision.backend_config import normalize_backend

            raw_arch = (
                os.environ.get("TAICHI_ARCH")
                or os.environ.get("PIXEL_REFINE_TAICHI_ARCH")
                or os.environ.get("PIXEL_REFINE_AOT_ARCH")
                or os.environ.get("PIXEL_REFINE_BACKEND")
            )
            forced_arch = normalize_backend(raw_arch, allow_auto=True)
            if forced_arch == "auto":
                # Legacy JIT's generic GPU means Vulkan on desktop.  AOT
                # callers never reach this branch because _IS_AOT_MODE keeps
                # the worker inert.
                forced_arch = "vulkan"
            cache_path = _global_cache_path

            if forced_arch == "cpu":
                ti.init(arch=ti.cpu, cpu_max_num_threads=ti_cpu_threads, offline_cache=True, offline_cache_file_path=cache_path)
            elif forced_arch == "vulkan":
                ti.init(arch=ti.vulkan, offline_cache=True, device_memory_GB=1.8, offline_cache_file_path=cache_path)
            elif forced_arch == "cuda":
                ti.init(arch=ti.cuda, offline_cache=True, device_memory_GB=1.8, offline_cache_file_path=cache_path)
            elif forced_arch == "opengl":
                opengl_arch = getattr(ti, "opengl", None)
                if opengl_arch is None:
                    raise RuntimeError("This Taichi build does not expose the OpenGL JIT arch")
                ti.init(arch=opengl_arch, offline_cache=True, device_memory_GB=1.8, offline_cache_file_path=cache_path)
            elif forced_arch == "gles":
                gles_arch = getattr(ti, "gles", None)
                if gles_arch is None:
                    raise RuntimeError("This Taichi build does not expose the GLES JIT arch")
                ti.init(arch=gles_arch, offline_cache=True, device_memory_GB=1.8, offline_cache_file_path=cache_path)
            else:
                # Fallback chain: Vulkan -> GPU -> CPU
                try:
                    ti.init(arch=ti.vulkan, offline_cache=True, device_memory_GB=1.8, offline_cache_file_path=cache_path)
                except Exception:
                    try:
                        # Use ti.gpu (CUDA/Vulkan/Metal)
                        ti.init(arch=ti.gpu, offline_cache=True, device_memory_GB=1.8, offline_cache_file_path=cache_path)
                    except Exception as e:
                        try:
                            # Limit CPU threads to keep UI responsive on fallback
                            ti.init(arch=ti.cpu, cpu_max_num_threads=ti_cpu_threads, offline_cache=True, offline_cache_file_path=cache_path)
                        except Exception as e2:
                            self.init_error = str(e2)
                            return

            # Verify configuration
            try:
                print(f"[TaichiWorker] Confirmed Offline Cache Path: {ti.cfg.offline_cache_file_path}")
                print(f"[TaichiWorker] Offline Cache Enabled: {ti.cfg.offline_cache}")
            except:
                pass

            self.initialized = True
        except Exception as e:
            self.init_error = str(e)
            print(f"[TaichiWorker] Initialization failed: {e}")

        # 3. Infinite job loop
        while self.running:
            try:
                task = self.task_queue.get()
                if task is None:
                    break

                func, args, kwargs, future = task
                try:
                    result = func(*args, **kwargs)
                    future.set_result(result)
                except Exception as e:
                    traceback.print_exc()
                    future.set_exception(e)
                finally:
                    self.task_queue.task_done()

                # Yield to OS is implicitly handled by blocking task_queue.get()
                # and when the worker thread finishes a task and waits for the next one.
                # Removing explicit sleep to maximize task throughput.
                pass

            except Exception as e:
                print(f"[TaichiWorker] Critical Loop Error: {e}")

    def submit(self, func, *args, **kwargs):
        """Submit a job and wait for results (Thread-safe, non-blocking for UI)."""
        future = self.submit_async(func, *args, **kwargs)

        # If we are in the Main Thread, we must YIELD to avoid Windows "Not Responding"
        is_main = threading.current_thread() is threading.main_thread()

        if is_main:
            # Polling wait with small sleeps allows the GIL to switch and UI to breathe
            while not future.done():
                time.sleep(0.001)
            return future.result()
        else:
            # Worker or side threads can block normally
            return future.result()

    def submit_and_wait(self, func, *args, **kwargs):
        """Alias for submit() for backward compatibility."""
        return self.submit(func, *args, **kwargs)

    def submit_async(self, func, *args, **kwargs):
        """Submit a job and return a Future (Thread-safe, non-blocking)."""
        if not self.initialized and self.init_error:
            raise RuntimeError(f"Taichi Worker failed to initialize: {self.init_error}")

        # If we are already in the worker thread, we must execute directly to avoid deadlock
        if threading.get_ident() == self.ident:
            f = concurrent.futures.Future()
            try:
                res = func(*args, **kwargs)
                f.set_result(res)
            except Exception as e:
                f.set_exception(e)
            return f

        future = concurrent.futures.Future()
        self.task_queue.put((func, args, kwargs, future))
        return future


# --- Singleton Instance ---
_GLOBAL_TI_WORKER = None
_INIT_LOCK = threading.Lock()
_CACHED_COMMON = None


def _get_common_module():
    """Lazily import and cache the common module."""
    global _CACHED_COMMON
    if _CACHED_COMMON is None:
        try:
            from . import common

            _CACHED_COMMON = common
        except ImportError:
            pass
    return _CACHED_COMMON


def _get_worker():
    global _GLOBAL_TI_WORKER
    if _GLOBAL_TI_WORKER is None:
        with _INIT_LOCK:
            if _GLOBAL_TI_WORKER is None:
                _GLOBAL_TI_WORKER = _TaichiWorker()
    return _GLOBAL_TI_WORKER


def get_taichi_worker():
    """Public API to get the persistent worker."""
    return _get_worker()


def ti_thread(func):
    """
    Decorator: Automatically routes function execution to the persistent Taichi thread.
    Prevents CUDA_ERROR_INVALID_CONTEXT and minimizes startup overhead.
    
    SPECIAL CASE: If 'g' (GraphBuilder) is passed in kwargs, we bypass the worker thread
    to ensure graph recording happens correctly in the caller's thread/arch.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # If we are globally in AOT mode, we bypass the worker thread completely
        # and execute directly to prevent any context collision.
        if _IS_AOT_MODE:
            return func(*args, **kwargs)

        # Bypass worker during AOT recording or if explicitly requested
        if kwargs.get("g") is not None:
            return func(*args, **kwargs)

        worker = _get_worker()
        return worker.submit(func, *args, **kwargs)

    return wrapper


def cleanup_taichi(mode="cache"):
    """
    Declarative API for Taichi cleanup operations.

    Args:
        mode (str): Cleanup mode
            - "cache": Clear buffer cache only (fast, keeps context alive)
            - "memory": Clear cache + force GC (moderate)
            - "full": Full reset including Taichi context (slow, use sparingly)

    Returns:
        bool: True if cleanup succeeded
    """

    def _cleanup_impl():
        try:
            common_mod = _get_common_module()
            if not common_mod:
                return False

            if mode == "cache":
                # Fast: Only clear buffer pool
                common_mod.cleanup_cache()
                return True

            elif mode == "memory":
                # Moderate: Clear cache + GC
                common_mod.cleanup_cache()
                import gc

                gc.collect()
                return True

            elif mode == "full":
                # Slow: Full reset (use only when necessary)
                common_mod.cleanup_cache()
                import gc

                gc.collect()
                if TAICHI_AVAILABLE:
                    try:
                        ti.reset()
                    except:
                        pass
                return True
            else:
                print(f"[TaichiWorker] Unknown cleanup mode: {mode}")
                return False

        except Exception as e:
            print(f"[TaichiWorker] Cleanup failed: {e}")
            return False

    return _get_worker().submit(_cleanup_impl)


def clear_vram():
    """Submit a cache cleanup task to the worker thread (legacy API)."""
    return cleanup_taichi(mode="cache")


@ti_thread
def create_taichi_ndarray(arr, dtype=None, use_pool=False):
    """
    Helper to create a ti.ndarray from numpy in the worker thread.
    Optionally uses the global buffer pool.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Map numpy dtype to ti if not provided
    ti_dtype = dtype
    if ti_dtype is None:
        if arr.dtype == np.uint16:
            ti_dtype = ti.u16
        elif arr.dtype == np.uint8:
            ti_dtype = ti.u8
        elif arr.dtype == np.int32:
            ti_dtype = ti.i32
        elif arr.dtype == np.int64:
            ti_dtype = ti.i64
        else:
            ti_dtype = ti.f32

    # Use pool if requested, else allocate new
    if use_pool:
        common_mod = _get_common_module()
        if common_mod:
            field = common_mod.get_temp_buffer(
                arr.shape, ti_dtype, buffer_provider="pool"
            )
        else:
            field = ti.ndarray(dtype=ti_dtype, shape=arr.shape)
    else:
        field = ti.ndarray(dtype=ti_dtype, shape=arr.shape)

    # Upload data
    field.from_numpy(np.ascontiguousarray(arr))
    return field


@ti_thread
def download_taichi_ndarray(field, out=None):
    """Helper to download a ti.ndarray to numpy in the worker thread."""
    if out is not None:
        out[:] = field.to_numpy()
        return out
    return field.to_numpy()


@ti_thread
def release_taichi_ndarray(field):
    """
    Release a Taichi ndarray back to the pool.
    This should be called for buffers created with use_pool=True.
    """
    if field is None:
        return
    try:
        common_mod = _get_common_module()
        if common_mod:
            common_mod.release_temp_buffer(field)
    except:
        pass
