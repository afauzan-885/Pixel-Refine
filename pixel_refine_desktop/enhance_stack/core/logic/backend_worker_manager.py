"""
Backend Worker Manager
======================
Singleton manager governing the lifecycle of the isolated Taichi Vision compute worker process.
Guarantees:
1. 0% RAM/VRAM residue and clean driver DLL unload when switching hardware backends.
2. Synchronized backend dropdown and actual execution device (zero desync).
3. Windows Job Object binding: anti-zombie protection guaranteeing child termination on exit/crash.
4. Seamless real-time backend switching without requiring application restart.
"""

import os
import sys
import json
import time
import atexit
import ctypes
import threading
import subprocess
from typing import Optional, Dict, Any, Callable


class WindowsJobObject:
    """Binds child processes to a Windows Job Object with KILL_ON_JOB_CLOSE."""

    def __init__(self):
        self.handle = None
        if os.name == "nt":
            try:
                class IO_COUNTERS(ctypes.Structure):
                    _fields_ = [
                        ("ReadOperationCount", ctypes.c_uint64),
                        ("WriteOperationCount", ctypes.c_uint64),
                        ("OtherOperationCount", ctypes.c_uint64),
                        ("ReadTransferCount", ctypes.c_uint64),
                        ("WriteTransferCount", ctypes.c_uint64),
                        ("OtherTransferCount", ctypes.c_uint64),
                    ]

                class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
                    _fields_ = [
                        ("PerProcessUserTimeLimit", ctypes.c_int64),
                        ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", ctypes.c_uint32),
                        ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t),
                        ("ActiveProcessLimit", ctypes.c_uint32),
                        ("Affinity", ctypes.c_size_t),
                        ("PriorityClass", ctypes.c_uint32),
                        ("SchedulingClass", ctypes.c_uint32),
                    ]

                class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
                    _fields_ = [
                        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
                        ("IoInfo", IO_COUNTERS),
                        ("ProcessMemoryLimit", ctypes.c_size_t),
                        ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryLimit", ctypes.c_size_t),
                        ("PeakJobMemoryLimit", ctypes.c_size_t),
                    ]

                self.handle = ctypes.windll.kernel32.CreateJobObjectW(None, None)
                if self.handle:
                    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
                    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
                    info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
                    JobObjectExtendedLimitInformation = 9
                    ctypes.windll.kernel32.SetInformationJobObject(
                        self.handle,
                        JobObjectExtendedLimitInformation,
                        ctypes.byref(info),
                        ctypes.sizeof(info),
                    )
            except Exception as e:
                print(f"[BackendWorkerManager] Warning: Job object setup failed: {e}")
                self.handle = None

    def assign_process(self, pid: int) -> bool:
        if not self.handle or os.name != "nt":
            return False
        try:
            PROCESS_SET_QUOTA = 0x0100
            PROCESS_TERMINATE = 0x0001
            h_proc = ctypes.windll.kernel32.OpenProcess(
                PROCESS_SET_QUOTA | PROCESS_TERMINATE, False, pid
            )
            if h_proc:
                res = ctypes.windll.kernel32.AssignProcessToJobObject(self.handle, h_proc)
                ctypes.windll.kernel32.CloseHandle(h_proc)
                return bool(res)
        except Exception as e:
            print(f"[BackendWorkerManager] Failed to assign PID {pid} to Job Object: {e}")
        return False


class BackendWorkerManager:
    """Manages the isolated backend worker process."""

    _instance: Optional["BackendWorkerManager"] = None
    _lock = threading.Lock()

    @classmethod
    def instance(cls) -> "BackendWorkerManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        self._proc: Optional[subprocess.Popen] = None
        self._job_object = WindowsJobObject()
        self._active_backend_config: Dict[str, Any] = {}
        self._proc_lock = threading.Lock()
        self._ready_event = threading.Event()
        self._current_task_event = threading.Event()
        self._current_task_result: Dict[str, Any] = {}
        self._progress_cb: Optional[Callable] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._stderr_thread: Optional[threading.Thread] = None
        self._is_terminating = False

        atexit.register(self.shutdown)

    def get_current_backend_config(self) -> Dict[str, Any]:
        """Return the active backend configuration."""
        with self._proc_lock:
            return dict(self._active_backend_config)

    def is_worker_alive(self) -> bool:
        """Check if worker process is currently running."""
        with self._proc_lock:
            return self._proc is not None and self._proc.poll() is None

    def switch_backend(self, backend_config: Dict[str, Any], force_restart: bool = False) -> bool:
        """
        Switch backend to a new configuration.
        Terminates the previous worker subprocess (releasing 100% VRAM and driver DLLs)
        and spawns a clean worker process with the new configuration.
        """
        with self._proc_lock:
            # Check if configuration actually changed
            if not force_restart and self._proc is not None and self._proc.poll() is None:
                if self._is_config_equal(self._active_backend_config, backend_config):
                    print("[BackendWorkerManager] Backend configuration unchanged; worker kept running.")
                    return True

            print(f"[BackendWorkerManager] Switching backend -> {backend_config.get('backend_text', 'unknown')}")
            self._terminate_worker_locked()
            self._active_backend_config = dict(backend_config)
            return self._spawn_worker_locked()

    def _is_config_equal(self, a: Dict[str, Any], b: Dict[str, Any]) -> bool:
        keys_to_compare = ("arch", "device_id", "vendor", "auto_fallback", "onnx_runtime")
        return all(a.get(k) == b.get(k) for k in keys_to_compare)

    def ensure_worker_ready(self) -> bool:
        """Ensure a worker process is spawned and ready."""
        with self._proc_lock:
            if self._proc is not None and self._proc.poll() is None:
                return True
            return self._spawn_worker_locked()

    def _spawn_worker_locked(self) -> bool:
        """Spawn the worker process with backend environment variables."""
        self._ready_event.clear()

        # If active config is empty, pull from persisted general store
        if not self._active_backend_config:
            try:
                from pixel_refine_desktop.ui.views.settings.General.general_store import (
                    get_general_store,
                )
                store = get_general_store()
                self._active_backend_config = {
                    "arch": store.get("device_backend_arch", os.environ.get("AOT_ARCH", "cpu")),
                    "device_id": store.get("device_backend_id", os.environ.get("AOT_DEVICE", "0")),
                    "vendor": store.get("device_vendor", os.environ.get("TARGET_VENDOR", "")),
                    "backend_text": store.get("device_backend", "CPU (Universal)"),
                    "auto_fallback": bool(store.get("auto_fallback", True)),
                    "onnx_runtime": store.get("onnx_runtime", "auto"),
                }
            except Exception:
                pass

        # Build clean environment
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        # Apply backend settings to env
        arch = self._active_backend_config.get("arch") or os.environ.get("AOT_ARCH", "cpu")
        device_id = str(self._active_backend_config.get("device_id", "0"))
        vendor = self._active_backend_config.get("vendor") or os.environ.get("TARGET_VENDOR", "")
        auto_fallback = self._active_backend_config.get("auto_fallback")
        onnx_runtime = self._active_backend_config.get("onnx_runtime")

        env["AOT_ARCH"] = arch
        env["AOT_DEVICE"] = device_id
        if vendor:
            env["TARGET_VENDOR"] = vendor

        if auto_fallback is not None:
            env["PIXEL_REFINE_AOT_AUTO_FALLBACK"] = "1" if auto_fallback else "0"
            env["PIXEL_REFINE_AOT_ALLOW_CPU_FALLBACK"] = "1" if auto_fallback else "0"
            if not auto_fallback:
                env["AOT_STRICT_BACKEND"] = "1"
            else:
                env.pop("AOT_STRICT_BACKEND", None)

        if onnx_runtime:
            env["ONNX_RUNTIME"] = onnx_runtime

        # Workspace root
        workspace_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        env["PYTHONPATH"] = workspace_root + os.pathsep + env.get("PYTHONPATH", "")

        worker_script = os.path.join(
            os.path.dirname(__file__), "backend_worker_process.py"
        )

        creationflags = 0
        if os.name == "nt":
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

        try:
            cmd = [sys.executable, "-u", worker_script]
            self._proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env,
                cwd=workspace_root,
                creationflags=creationflags,
            )

            # Assign to Windows Job Object
            if self._proc.pid:
                self._job_object.assign_process(self._proc.pid)

            # Start background stdout reader
            self._reader_thread = threading.Thread(
                target=self._stdout_reader_loop,
                args=(self._proc.stdout,),
                daemon=True,
                name=f"WorkerStdoutReader-{self._proc.pid}",
            )
            self._reader_thread.start()

            # Start background stderr monitor
            self._stderr_thread = threading.Thread(
                target=self._stderr_reader_loop,
                args=(self._proc.stderr,),
                daemon=True,
                name=f"WorkerStderrReader-{self._proc.pid}",
            )
            self._stderr_thread.start()

            # Wait for ready signal
            ready = self._ready_event.wait(timeout=25.0)
            if not ready:
                print(f"[BackendWorkerManager] Warning: Worker PID {self._proc.pid} did not send ready in time.")
                return False

            print(
                f"[BackendWorkerManager] Worker online (PID {self._proc.pid}, "
                f"arch={arch}, device={device_id}, vendor={vendor})"
            )
            return True

        except Exception as e:
            print(f"[BackendWorkerManager] Failed to spawn worker: {e}")
            self._proc = None
            return False

    def _terminate_worker_locked(self):
        """Terminate the running worker subprocess cleanly."""
        if self._proc is None:
            return

        proc = self._proc
        self._proc = None
        self._ready_event.clear()
        self._current_task_event.set()

        try:
            if proc.poll() is None:
                # Try graceful shutdown command
                try:
                    if proc.stdin and not proc.stdin.closed:
                        proc.stdin.write(json.dumps({"cmd": "shutdown"}) + "\n")
                        proc.stdin.flush()
                except Exception:
                    pass

                # Wait up to 1.0s for exit
                try:
                    proc.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    # Force kill if not exited
                    proc.terminate()
                    try:
                        proc.wait(timeout=1.0)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait(timeout=0.5)

            print(f"[BackendWorkerManager] Worker PID {proc.pid} terminated cleanly.")
        except Exception as e:
            print(f"[BackendWorkerManager] Error terminating worker: {e}")

    def _stdout_reader_loop(self, stdout_pipe):
        """Read JSON messages from worker stdout."""
        while not self._is_terminating:
            try:
                line = stdout_pipe.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except Exception:
                    # Non-JSON output (e.g. print statements from C library)
                    print(f"[WorkerRaw] {line}")
                    continue

                msg_type = data.get("type")
                if msg_type == "ready":
                    self._ready_event.set()
                elif msg_type == "progress":
                    if self._progress_cb:
                        percent = data.get("percent", 0)
                        raw_msg = data.get("raw_msg", "")
                        self._progress_cb(percent, raw_msg)
                elif msg_type in ("finished", "cancelled", "error"):
                    self._current_task_result = data
                    self._current_task_event.set()
                elif msg_type == "log":
                    print(f"[WorkerLog] {data.get('message', '')}")

            except Exception:
                break

    def _stderr_reader_loop(self, stderr_pipe):
        """Monitor worker stderr for diagnostic information."""
        while not self._is_terminating:
            try:
                line = stderr_pipe.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    print(f"[WorkerErr] {line}")
            except Exception:
                break

    def dispatch_task(
        self,
        task_payload: Dict[str, Any],
        progress_cb: Optional[Callable] = None,
        stop_requested_cb: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Execute an image processing task in the isolated worker.
        Routes progress updates to progress_cb and monitors stop_requested_cb.
        """
        if stop_requested_cb and stop_requested_cb():
            return {
                "success": False,
                "type": "cancelled",
                "message": "Task was cancelled before start.",
            }

        if not self.ensure_worker_ready():
            return {"success": False, "error": "Backend worker failed to start."}

        if stop_requested_cb and stop_requested_cb():
            return {
                "success": False,
                "type": "cancelled",
                "message": "Task was cancelled before dispatch.",
            }

        self._current_task_event.clear()
        self._current_task_result = {}
        self._progress_cb = progress_cb

        task_id = f"task_{int(time.time() * 1000)}"
        cmd_payload = {
            "cmd": "execute",
            "task_id": task_id,
            "batch_id": task_payload.get("batch_id"),
            "single_process": task_payload.get("single_process", False),
            "db_path": task_payload.get("db_path"),
            "settings": task_payload.get("settings", {}),
        }

        with self._proc_lock:
            if not self._proc or self._proc.poll() is not None:
                return {"success": False, "error": "Worker died before task dispatch."}
            try:
                self._proc.stdin.write(json.dumps(cmd_payload) + "\n")
                self._proc.stdin.flush()
            except Exception as e:
                return {"success": False, "error": f"Failed to send task to worker: {e}"}

        # Monitor loop with responsive cancel & watchdog force-stop
        stop_sent = False
        stop_sent_time = 0.0
        while not self._current_task_event.is_set():
            if stop_requested_cb and stop_requested_cb():
                if not stop_sent:
                    self.stop_current_task()
                    stop_sent = True
                    stop_sent_time = time.time()
                elif time.time() - stop_sent_time > 6.0:
                    # Worker is stuck in uncooperative kernel/inference loop.
                    # Terminate worker process immediately to release 100% GPU VRAM.
                    print(
                        "[BackendWorkerManager] Worker uncooperative on stop; "
                        "force terminating worker subprocess to reclaim GPU memory immediately."
                    )
                    with self._proc_lock:
                        self._terminate_worker_locked()
                    # Spawn fresh replacement worker in background
                    threading.Thread(
                        target=self.ensure_worker_ready,
                        daemon=True,
                        name="RespawnReplacementWorker",
                    ).start()
                    return {
                        "success": False,
                        "type": "cancelled",
                        "message": "Task cancelled by user (worker force-stopped).",
                    }

            with self._proc_lock:
                if self._proc is not None and self._proc.poll() is not None:
                    # Worker exited unexpectedly
                    return {
                        "success": False,
                        "error": f"Worker crashed unexpectedly (exit code {self._proc.poll()}).",
                    }

            self._current_task_event.wait(timeout=0.05)

        result = dict(self._current_task_result)
        self._progress_cb = None
        return result

    def stop_current_task(self):
        """Send stop command to current running task."""
        with self._proc_lock:
            if self._proc and self._proc.poll() is None:
                try:
                    self._proc.stdin.write(json.dumps({"cmd": "stop"}) + "\n")
                    self._proc.stdin.flush()
                except Exception:
                    pass

    def shutdown(self):
        """Shutdown worker on exit."""
        self._is_terminating = True
        with self._proc_lock:
            self._terminate_worker_locked()
