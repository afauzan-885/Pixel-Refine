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

    def terminate_all(self) -> bool:
        """Kill every process in the job, not just the one we tracked.

        The worker is launched through the interpreter launcher, so the process
        we hold may only be the launcher while the real worker is its child.
        Killing just the tracked process would leave the real worker (with its
        AOT engine, driver DLLs and RAM) alive after a "sleep" - which both
        defeats the RAM saving and can block the next worker's engine start-up.
        """
        if not self.handle or os.name != "nt":
            return False
        try:
            return bool(ctypes.windll.kernel32.TerminateJobObject(self.handle, 0))
        except Exception as e:
            print(f"[BackendWorkerManager] Failed to terminate job object: {e}")
            return False


class BackendWorkerManager:
    """Manages the isolated backend worker process."""

    _instance: Optional["BackendWorkerManager"] = None
    _lock = threading.Lock()

    # Cold spawn budget.  The worker only signals ready after engine init and
    # the algorithm pre-imports (MFDenoiser / Median / SplatSR), which on a CPU
    # backend is routinely slower than the old 45 s budget.
    COLD_BOOT_TIMEOUT_S: float = 45.0
    # Budget for a start that the user is waiting on.  A timeout here must not
    # be reported as "failed": the worker is usually still loading.
    START_READY_TIMEOUT_S: float = 180.0
    # A dispatched task that neither reports progress nor consumes any CPU for
    # this long is treated as lost: the worker is restarted and the caller gets a
    # clear error instead of an indefinitely frozen progress bar.  A worker that
    # is merely quiet but still computing is never touched.
    TASK_WATCHDOG_TIMEOUT_S: float = 300.0

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
        # Last time the worker said anything (monotonic seconds).  Used by the
        # task watchdog to tell "quiet but working" from "wedged".
        self._last_worker_activity: float = 0.0
        self._reader_thread: Optional[threading.Thread] = None
        self._stderr_thread: Optional[threading.Thread] = None
        self._is_terminating = False
        self._is_task_active = False
        self._idle_sleep_timer: Optional[threading.Timer] = None
        self._idle_sleep_lock = threading.Lock()
        # Idle policy: the worker is only put to sleep once the application
        # window is no longer in use.  It used to sleep 30 s after *every* task,
        # which cost a full worker respawn plus TCM/ONNX reload before the next
        # batch could start.  Override for diagnostics with
        # PIXEL_REFINE_WORKER_IDLE_SLEEP_SECONDS.
        try:
            self._idle_timeout: float = float(
                os.environ.get("PIXEL_REFINE_WORKER_IDLE_SLEEP_SECONDS", "120") or 120
            )
        except (TypeError, ValueError):
            self._idle_timeout = 120.0
        self._window_active: bool = True

        atexit.register(self.shutdown)

    def get_current_backend_config(self) -> Dict[str, Any]:
        """Return the active backend configuration."""
        with self._proc_lock:
            return dict(self._active_backend_config)

    def is_worker_alive(self) -> bool:
        """Check if worker process is currently running."""
        with self._proc_lock:
            return self._proc is not None and self._proc.poll() is None

    def is_task_active(self) -> bool:
        """Whether a task is currently executing in the worker.

        Read-only view of the dispatch state so background callers (for example
        the GPU availability watcher) can defer a backend switch instead of
        terminating the user's running batch.
        """
        return bool(self._is_task_active)

    def get_worker_memory_mb(self) -> float:
        """Return the resident memory (RSS) of the worker process tree, in MB.

        The whole tree is summed because the worker is launched through an
        interpreter stub: the tracked process alone reports only a few MB, which
        made the reported worker memory meaningless.
        """
        try:
            import psutil

            with self._proc_lock:
                proc = self._proc
                if proc is None or proc.poll() is not None:
                    return 0.0
                pid = proc.pid

            total = 0
            try:
                root = psutil.Process(pid)
                processes = [root]
                try:
                    processes.extend(root.children(recursive=True))
                except Exception:
                    pass
                for candidate in processes:
                    try:
                        total += candidate.memory_info().rss
                    except Exception:
                        continue
            except Exception:
                return 0.0
            return total / (1024 * 1024)
        except Exception:
            return 0.0

    def set_window_active(self, active: bool) -> None:
        """Tell the manager whether the application window is in use.

        While the window is active the worker is kept warm so the next batch
        starts immediately; once the window is out of use (minimised), the
        worker is allowed to sleep and give its memory back to the OS.
        """
        self._window_active = bool(active)
        if self._window_active:
            self._cancel_idle_sleep()
        else:
            self._maybe_schedule_idle_sleep()

    def _maybe_schedule_idle_sleep(self) -> None:
        """Arm the idle sleep only when the window is not in use."""
        if getattr(self, "_window_active", True) or self._is_task_active:
            self._cancel_idle_sleep()
            return
        self._schedule_idle_sleep()

    def _cancel_idle_sleep(self):
        """Cancel any pending auto-sleep timer."""
        with self._idle_sleep_lock:
            if self._idle_sleep_timer is not None:
                try:
                    self._idle_sleep_timer.cancel()
                except Exception:
                    pass
                self._idle_sleep_timer = None

    def _schedule_idle_sleep(self, timeout: Optional[float] = None):
        """Schedule an auto-sleep timer after inactivity (default 30 seconds)."""
        self._cancel_idle_sleep()
        delay = timeout if timeout is not None else self._idle_timeout
        with self._idle_sleep_lock:
            self._idle_sleep_timer = threading.Timer(delay, self._on_idle_sleep_timeout)
            self._idle_sleep_timer.daemon = True
            self._idle_sleep_timer.name = "WorkerIdleSleepTimer"
            self._idle_sleep_timer.start()
            print(f"[BackendWorkerManager] Scheduled auto-sleep in {delay:.1f}s of inactivity.")

    def _on_idle_sleep_timeout(self):
        """Callback invoked when idle sleep timer fires."""
        with self._idle_sleep_lock:
            self._idle_sleep_timer = None

        if self._is_task_active or self._is_terminating:
            return

        if getattr(self, "_window_active", True):
            # The window came back before the timer fired; keep the worker warm.
            return

        print(
            f"[BackendWorkerManager] Inactivity timeout ({self._idle_timeout}s) reached; "
            "putting worker to sleep to achieve maximum RAM savings."
        )
        self.sleep_worker()

    def sleep_worker(self) -> bool:
        """
        Cleanly put worker to sleep (terminates subprocess to release 100% GPU VRAM and driver DLLs).
        The worker will seamlessly re-spawn whenever the next task is dispatched.
        """
        self._cancel_idle_sleep()
        with self._proc_lock:
            if self._proc is None or self._proc.poll() is not None:
                return True
            print("[BackendWorkerManager] Putting worker subprocess to sleep.")
            self._terminate_worker_locked()

        # Trim main GUI process memory too
        import gc
        gc.collect()
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.kernel32.SetProcessWorkingSetSize(
                    ctypes.windll.kernel32.GetCurrentProcess(), -1, -1
                )
            except Exception:
                pass
        return True

    def recycle_worker(self) -> bool:
        """Cleanly restart the worker subprocess to release 100% native driver RAM."""
        self._cancel_idle_sleep()
        with self._proc_lock:
            print(
                "[BackendWorkerManager] Recycling worker subprocess to return native memory to OS.",
                flush=True,
            )
            self._terminate_worker_locked()
            if not self._spawn_worker_locked():
                return False
            proc = self._proc

        return self._await_ready(proc, self.START_READY_TIMEOUT_S)

    def switch_backend(
        self,
        backend_config: Optional[Dict[str, Any]] = None,
        force_restart: bool = False,
    ) -> bool:
        """
        Switch backend to a new configuration.
        Terminates the previous worker subprocess (releasing 100% VRAM and driver DLLs)
        and spawns a clean worker process with the new configuration.
        """
        self._cancel_idle_sleep()
        if backend_config is None:
            backend_config = self._active_backend_config or {}

        with self._proc_lock:
            # Check if configuration actually changed
            if not force_restart and self._proc is not None and self._proc.poll() is None:
                if self._is_config_equal(self._active_backend_config, backend_config):
                    print("[BackendWorkerManager] Backend configuration unchanged; worker kept running.")
                    return True

            print(
                f"[BackendWorkerManager] Switching backend -> "
                f"{backend_config.get('backend_text', 'unknown')}",
                flush=True,
            )
            self._terminate_worker_locked()
            self._active_backend_config = dict(backend_config)
            if not self._spawn_worker_locked():
                return False
            proc = self._proc

        return self._await_ready(proc, self.START_READY_TIMEOUT_S)

    def _is_config_equal(self, a: Dict[str, Any], b: Dict[str, Any]) -> bool:
        keys_to_compare = ("arch", "device_id", "vendor", "auto_fallback", "onnx_runtime")
        return all(a.get(k) == b.get(k) for k in keys_to_compare)

    def ensure_worker_ready(self, timeout: Optional[float] = None) -> bool:
        """Ensure a worker process exists **and has signalled ready**.

        A live process is not enough.  The worker announces readiness only after
        it has initialised the engine and pre-imported the algorithm modules
        (MFDenoiser / Median / SplatSR), which on a CPU backend routinely takes
        longer than the old 45 s budget.  Reporting a still-booting process as
        ready meant the first Start wrote a task into a worker that could not
        answer yet, and the parent then waited for a result with no progress and
        no timeout - which is exactly the "the app looks hung and never
        processes anything" report.

        A timeout keeps the process alive: its boot is in progress and valuable,
        and the next call will pick it up once the handshake arrives.
        """
        if timeout is None:
            timeout = self.START_READY_TIMEOUT_S

        self._cancel_idle_sleep()

        with self._proc_lock:
            proc = self._proc
            if proc is None or proc.poll() is not None:
                if not self._spawn_worker_locked():
                    return False
                proc = self._proc

        if proc is None:
            return False

        # Wait outside ``_proc_lock``: a cold boot can take minutes and every
        # other caller of the lock (cancel, liveness, memory report) would block
        # behind it, which is how a slow start turned into an unresponsive
        # Cancel button.
        return self._await_ready(proc, timeout)

    def _await_ready(self, proc, timeout: float, announce: bool = True) -> bool:
        """Wait for the ready handshake of *proc* outside ``_proc_lock``."""
        if self._wait_ready(timeout, proc):
            if announce:
                config = self._active_backend_config or {}
                print(
                    f"[BackendWorkerManager] Worker online (PID {proc.pid}, "
                    f"arch={config.get('arch', '?')}, "
                    f"device={config.get('device_id', '?')}, "
                    f"vendor={config.get('vendor', '')})",
                    flush=True,
                )
            return True

        print(
            f"[BackendWorkerManager] Worker PID {proc.pid} is still loading after "
            f"{timeout:.0f}s; keeping it (boot in progress).",
            flush=True,
        )
        return False

    def _wait_ready(self, timeout: float, proc=None) -> bool:
        """Wait for the worker's ready handshake.

        Polls in short slices so a worker that dies, or that another caller
        recycled, does not force the caller to sit out the whole timeout.
        """
        deadline = time.monotonic() + timeout
        while True:
            if self._ready_event.is_set():
                return True
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            if proc is not None:
                try:
                    if proc.poll() is not None:
                        return False
                except Exception:
                    return False
                with self._proc_lock:
                    if self._proc is not proc:
                        # Another caller recycled the worker while we waited.
                        return False
            self._ready_event.wait(timeout=min(0.25, remaining))

    def _spawn_worker_locked(self) -> bool:
        """Start the worker process and its reader threads (no ready wait).

        Callers must release ``_proc_lock`` before waiting for the handshake;
        ``_await_ready`` does exactly that.
        """
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
        env["PYTHONIOENCODING"] = "utf-8"

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
                encoding="utf-8",
                errors="replace",
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

            # Ready is awaited by the caller, outside ``_proc_lock``.
            return True

        except Exception as e:
            print(f"[BackendWorkerManager] Failed to spawn worker: {e}", flush=True)
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

            print(
                f"[BackendWorkerManager] Worker PID {proc.pid} terminated cleanly.",
                flush=True,
            )
        except Exception as e:
            print(f"[BackendWorkerManager] Error terminating worker: {e}", flush=True)

        # The launcher chain (interpreter stub -> real worker) can leave the real
        # worker, its AOT engine and driver DLLs alive.  Kill whatever is still in
        # the job so a "sleep" really frees the memory and cannot block the next
        # worker's engine start-up.
        self._job_object.terminate_all()

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

                # Any output at all counts as liveness for the task watchdog.
                self._last_worker_activity = time.monotonic()

                try:
                    data = json.loads(line)
                except Exception:
                    # Non-JSON output (e.g. print statements from C library)
                    print(f"[WorkerRaw] {line}", flush=True)
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
                    print(f"[WorkerLog] {data.get('message', '')}", flush=True)

            except Exception:
                if stdout_pipe.closed or self._is_terminating:
                    break
                continue

    def _stderr_reader_loop(self, stderr_pipe):
        """Monitor worker stderr for diagnostic information."""
        while not self._is_terminating:
            try:
                line = stderr_pipe.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    print(f"[WorkerErr] {line}", flush=True)
            except Exception:
                if stderr_pipe.closed or self._is_terminating:
                    break
                continue

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

        self._cancel_idle_sleep()

        if not self.ensure_worker_ready():
            return {
                "success": False,
                "error": (
                    "Backend worker masih memuat mesin proses (belum mengirim ready). "
                    "Tunggu sebentar lalu jalankan lagi."
                ),
            }

        if stop_requested_cb and stop_requested_cb():
            return {
                "success": False,
                "type": "cancelled",
                "message": "Task was cancelled before dispatch.",
            }

        self._is_task_active = True
        try:
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

            # The worker can disappear between the ready handshake and the write
            # (the idle policy may have just put it to sleep, or it crashed).
            # Restart it and retry once instead of failing the user's batch.
            send_error = None
            for attempt in range(2):
                send_error = self._write_task(cmd_payload)
                if send_error is None:
                    break
                if attempt == 0:
                    print(
                        f"[BackendWorkerManager] {send_error} Restarting worker and retrying.",
                        flush=True,
                    )
                    with self._proc_lock:
                        self._terminate_worker_locked()
                    if not self.ensure_worker_ready():
                        return {"success": False, "error": send_error}

            if send_error is not None:
                return {"success": False, "error": send_error}

            # Monitor loop with responsive cancel, a stall watchdog, and the
            # existing force-stop escape hatch.
            start_time = time.monotonic()
            last_activity = max(self._last_worker_activity, start_time)
            cpu_sample_time = start_time
            cpu_sample_value = self._worker_cpu_seconds()
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

                now = time.monotonic()
                if self._last_worker_activity > last_activity:
                    last_activity = self._last_worker_activity

                # A quiet worker that is still burning CPU is working, not wedged.
                if now - cpu_sample_time >= 5.0:
                    cpu_now = self._worker_cpu_seconds()
                    if (
                        cpu_now is not None
                        and cpu_sample_value is not None
                        and cpu_now - cpu_sample_value > 0.05
                    ):
                        last_activity = now
                    cpu_sample_time = now
                    cpu_sample_value = cpu_now

                if now - last_activity >= self.TASK_WATCHDOG_TIMEOUT_S:
                    return self._on_task_stalled()

                self._current_task_event.wait(timeout=0.05)

            result = dict(self._current_task_result)
            return result
        finally:
            self._is_task_active = False
            self._progress_cb = None

            # Fase 1: Warm Trim (Instan) - release GUI process working set
            import gc

            gc.collect()
            if sys.platform == "win32":
                try:
                    import ctypes

                    ctypes.windll.kernel32.SetProcessWorkingSetSize(
                        ctypes.windll.kernel32.GetCurrentProcess(), -1, -1
                    )
                except Exception:
                    pass

            # Fase 2: allow the worker to sleep only once the window is idle
            self._maybe_schedule_idle_sleep()

    def _write_task(self, cmd_payload: Dict[str, Any]) -> Optional[str]:
        """Send one task command to the worker.  Returns an error string or None."""
        with self._proc_lock:
            if not self._proc or self._proc.poll() is not None:
                return "Worker died before task dispatch."
            try:
                self._proc.stdin.write(json.dumps(cmd_payload) + "\n")
                self._proc.stdin.flush()
                return None
            except Exception as e:
                return f"Failed to send task to worker: {e}"

    def _worker_cpu_seconds(self) -> Optional[float]:
        """Total CPU seconds of the worker process tree (None when unknown).

        The whole tree is measured, not just the tracked process: the worker is
        launched through an interpreter stub, so the tracked process can sit idle
        while the real worker computes.
        """
        try:
            import psutil

            with self._proc_lock:
                proc = self._proc
                if proc is None or proc.poll() is not None:
                    return None
                pid = proc.pid

            root = psutil.Process(pid)
            processes = [root]
            try:
                processes.extend(root.children(recursive=True))
            except Exception:
                pass

            total = 0.0
            for candidate in processes:
                try:
                    times = candidate.cpu_times()
                    total += float(times.user) + float(times.system)
                except Exception:
                    continue
            return total
        except Exception:
            return None

    def _on_task_stalled(self) -> Dict[str, Any]:
        """Restart a wedged worker and report it instead of hanging forever."""
        timeout = self.TASK_WATCHDOG_TIMEOUT_S
        print(
            f"[BackendWorkerManager] Worker produced no progress and no CPU for "
            f"{timeout:.0f}s; restarting it.",
            flush=True,
        )
        with self._proc_lock:
            self._terminate_worker_locked()
        threading.Thread(
            target=self.ensure_worker_ready,
            daemon=True,
            name="RespawnAfterStall",
        ).start()
        return {
            "success": False,
            "error": (
                f"Mesin proses berhenti merespons lebih dari {timeout:.0f} detik. "
                "Worker sudah dijalankan ulang, silakan jalankan batch lagi."
            ),
        }

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
        self._cancel_idle_sleep()
        self._is_terminating = True
        with self._proc_lock:
            self._terminate_worker_locked()

