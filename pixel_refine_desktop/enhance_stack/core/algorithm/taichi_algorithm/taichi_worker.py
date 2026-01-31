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

# Force stable CUDA context settings globally before any Taichi import
os.environ["TI_ENABLE_CUDA_MALLOC_ASYNC"] = "0"

try:
    import taichi as ti

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False

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

        # 2. Initialize Taichi exactly once in this persistent thread
        if not TAICHI_AVAILABLE:
            self.init_error = "Taichi not installed"
            return

        try:
            # Try Vulkan first as requested by the user
            try:
                ti.init(arch=ti.vulkan, offline_cache=True, device_memory_GB=2.0)
            except Exception:
                # Fallback to GPU (CUDA/Metal) -> CPU
                try:
                    ti.init(arch=ti.gpu, offline_cache=True, device_memory_GB=2.0)
                except Exception:
                    ti.init(arch=ti.cpu)

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

                # Yield to OS - prevents UI/GIL starvation
                time.sleep(0.001)

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
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
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
            from . import common

            if mode == "cache":
                # Fast: Only clear buffer pool
                common.cleanup_cache()
                return True

            elif mode == "memory":
                # Moderate: Clear cache + GC
                common.cleanup_cache()
                import gc

                gc.collect()
                return True

            elif mode == "full":
                # Slow: Full reset (use only when necessary)
                common.cleanup_cache()
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
        from . import common

        field = common.get_temp_buffer(arr.shape, ti_dtype, buffer_provider="pool")
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


def release_taichi_ndarray(field):
    """
    Release a Taichi ndarray back to the pool.
    This should be called for buffers created with use_pool=True.
    """
    if field is None:
        return
    try:
        from . import common

        common.release_temp_buffer(field)
    except:
        pass
