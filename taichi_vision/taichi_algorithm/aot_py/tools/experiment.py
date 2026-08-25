import argparse
import ctypes
import os
import subprocess
import sys
import time
from ctypes import wintypes


class WindowsJob:
    def __init__(self):
        self.handle = None
        self.active = False

    def __enter__(self):
        if os.name != "nt":
            return self
        try:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

            class BasicLimit(ctypes.Structure):
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

            class IoCounters(ctypes.Structure):
                _fields_ = [
                    ("ReadOperationCount", ctypes.c_ulonglong),
                    ("WriteOperationCount", ctypes.c_ulonglong),
                    ("OtherOperationCount", ctypes.c_ulonglong),
                    ("ReadTransferCount", ctypes.c_ulonglong),
                    ("WriteTransferCount", ctypes.c_ulonglong),
                    ("OtherTransferCount", ctypes.c_ulonglong),
                ]

            class ExtendedLimit(ctypes.Structure):
                _fields_ = [
                    ("BasicLimitInformation", BasicLimit),
                    ("IoInfo", IoCounters),
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
            kernel32.AssignProcessToJobObject.argtypes = [
                wintypes.HANDLE,
                wintypes.HANDLE,
            ]
            kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
            kernel32.OpenProcess.argtypes = [
                wintypes.DWORD,
                wintypes.BOOL,
                wintypes.DWORD,
            ]
            kernel32.OpenProcess.restype = wintypes.HANDLE
            kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
            kernel32.TerminateJobObject.restype = wintypes.BOOL
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel32.CloseHandle.restype = wintypes.BOOL
            self._kernel32 = kernel32

            job = kernel32.CreateJobObjectW(None, None)
            if not job:
                return self
            info = ExtendedLimit()
            info.BasicLimitInformation.LimitFlags = 0x00002000
            ok = kernel32.SetInformationJobObject(
                job, 9, ctypes.byref(info), ctypes.sizeof(info)
            )
            if not ok:
                kernel32.CloseHandle(job)
                return self
            self.handle = job
            self.active = True
        except Exception:
            self.handle = None
            self.active = False
        return self

    def assign(self, pid):
        if not self.active or os.name != "nt":
            return False
        process = None
        try:
            process = self._kernel32.OpenProcess(0x0001 | 0x0400, False, int(pid))
            if not process:
                return False
            return bool(self._kernel32.AssignProcessToJobObject(self.handle, process))
        except Exception:
            return False
        finally:
            if process:
                self._kernel32.CloseHandle(process)

    def terminate(self, code=124):
        if self.active and os.name == "nt":
            try:
                self._kernel32.TerminateJobObject(self.handle, code)
            except Exception:
                pass

    def __exit__(self, exc_type, exc, tb):
        if self.handle and os.name == "nt":
            try:
                self._kernel32.CloseHandle(self.handle)
            except Exception:
                pass
        self.handle = None
        self.active = False


def _kill_tree(pid):
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(int(pid))],
            capture_output=True,
            text=True,
            timeout=15,
        )
    else:
        try:
            os.kill(int(pid), 9)
        except OSError:
            pass


def run_experiment(command, timeout):
    env = os.environ.copy()
    env["AOT_EXPERIMENT"] = "1"
    env.setdefault("AOT_MODE", "1")
    env.setdefault("AOT_AUTOSCAN", "0")
    env.setdefault("CLEAN_ZOMBIES", "0")
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        repo_root
        if not existing_pythonpath
        else repo_root + os.pathsep + existing_pythonpath
    )

    with WindowsJob() as job:
        proc = subprocess.Popen(
            command,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        )
        assigned = job.assign(proc.pid)
        print(
            f"[AOT-EXPERIMENT] pid={proc.pid} job_active={job.active} assigned={assigned}",
            flush=True,
        )
        start = time.monotonic()
        timed_out = False
        try:
            while True:
                line = proc.stdout.readline() if proc.stdout else ""
                if line:
                    print(line.rstrip(), flush=True)
                if proc.poll() is not None:
                    break
                if timeout > 0 and time.monotonic() - start > timeout:
                    timed_out = True
                    print(
                        "[AOT-EXPERIMENT] timeout reached; terminating job", flush=True
                    )
                    job.terminate(124)
                    _kill_tree(proc.pid)
                    break
                if not line:
                    time.sleep(0.05)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _kill_tree(proc.pid)
                proc.wait(timeout=5)
        finally:
            if proc.stdout:
                rest = proc.stdout.read()
                if rest:
                    print(rest.rstrip(), flush=True)
    if timed_out:
        return 124
    return int(proc.returncode or 0)


def main():
    parser = argparse.ArgumentParser(
        description="Run unstable Taichi AOT experiments in an isolated process."
    )
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error(
            "missing command, example: python -m taichi_vision.taichi_algorithm.aot_py.tools.experiment -- python scratch/my_test.py"
        )
    raise SystemExit(run_experiment(command, args.timeout))


if __name__ == "__main__":
    main()
