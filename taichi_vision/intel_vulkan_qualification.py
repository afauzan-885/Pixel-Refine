"""Automatic, crash-isolated qualification for previously unseen Intel Vulkan.

Production never enables a new Intel driver/fingerprint optimistically.  When
an unvalidated native Intel ICD is selected, the application keeps using the
safe OpenGL route and schedules this worker.  The worker waits for the parent
application to exit before running the comprehensive Vulkan gate, avoiding
contention with the application's OpenGL context and shared-memory workload.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

# Direct worker execution places ``taichi_vision`` rather than its parent at
# sys.path[0]. Add the repository root without importing taichi_aot.
_IMPORT_ROOT = Path(__file__).resolve().parent.parent
if str(_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_IMPORT_ROOT))

from taichi_vision.device_selection import (
    device_fingerprint,
    is_translation_device,
    make_device_selector,
    scan_vulkan_device_records,
)


STATE_SCHEMA = 1
DEFAULT_FAILURE_COOLDOWN_S = 24 * 60 * 60
DEFAULT_SCHEDULE_TTL_S = 26 * 60 * 60
DEFAULT_PARENT_WAIT_S = 24 * 60 * 60


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _state_root() -> Path:
    configured = os.environ.get("PIXEL_REFINE_INTEL_VULKAN_STATE")
    if configured:
        return Path(configured).resolve()
    base = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir()))
    return base / "PixelRefine" / "intel_vulkan_qualification"


def _state_path() -> Path:
    return _state_root() / "state.json"


def _load_state() -> dict:
    try:
        payload = json.loads(_state_path().read_text(encoding="utf-8"))
        if isinstance(payload, dict) and payload.get("schema") == STATE_SCHEMA:
            return payload
    except (OSError, TypeError, ValueError):
        pass
    return {"schema": STATE_SCHEMA, "entries": {}}


def _write_state(payload: dict) -> None:
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    staging.write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    os.replace(staging, path)


def _native_intel_record(device_id: int, records=None):
    records = records if records is not None else scan_vulkan_device_records()
    return next(
        (
            record
            for record in records
            if int(record.get("ordinal", -1)) == int(device_id)
            and record.get("vendor") == "intel"
            and not is_translation_device(record)
        ),
        None,
    )


def _qualification_key(record, project_root=None) -> str:
    # Import lazily: vulkan_probe intentionally avoids constructing taichi_aot.
    from taichi_vision.vulkan_probe import vulkan_inventory_digest

    inventory = vulkan_inventory_digest(project_root)
    identity = {
        "fingerprint": device_fingerprint(record),
        "driver_uuid": record.get("driver_uuid", ""),
        "driver_version": record.get("driver_version", ""),
        "api_version": record.get("api_version", ""),
        "inventory": inventory["digest"],
    }
    token = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _lock_path(key: str) -> Path:
    # One worker qualifies every native Intel ICD sequentially. A global lock
    # prevents multiple adapters or application instances from launching
    # competing 24 MP qualification workloads.
    return _state_root() / "qualification.lock"


def _process_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        query_limited_information = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(
            query_limited_information, False, int(pid)
        )
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong()
            if not ctypes.windll.kernel32.GetExitCodeProcess(
                handle, ctypes.byref(exit_code)
            ):
                return False
            return exit_code.value == 259  # STILL_ACTIVE
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _write_lock_owner(key: str, pid: int) -> None:
    path = _lock_path(key)
    staging = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    staging.write_text(
        json.dumps({"pid": int(pid), "created_at": time.time()}),
        encoding="utf-8",
    )
    os.replace(staging, path)


def _claim_schedule(key: str, ttl_s: float) -> bool:
    path = _lock_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        age = time.time() - path.stat().st_mtime
        try:
            owner = json.loads(path.read_text(encoding="utf-8"))
            owner_alive = _process_is_alive(int(owner.get("pid", 0)))
        except (OSError, TypeError, ValueError):
            owner_alive = False
        if age <= float(ttl_s) and owner_alive:
            return False
        path.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        return False
    try:
        descriptor = os.open(
            str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY
        )
    except FileExistsError:
        return False
    try:
        os.write(
            descriptor,
            json.dumps({"pid": os.getpid(), "created_at": time.time()}).encode(
                "utf-8"
            ),
        )
    finally:
        os.close(descriptor)
    return True


def _release_schedule(key: str) -> None:
    try:
        _lock_path(key).unlink()
    except FileNotFoundError:
        pass


def _update_entry(key: str, **values) -> dict:
    state = _load_state()
    entries = state.setdefault("entries", {})
    entry = entries.setdefault(key, {})
    entry.update(values)
    entry["updated_at"] = time.time()
    _write_state(state)
    return dict(entry)


def qualification_status(device_id: int, project_root=None, records=None) -> dict:
    record = _native_intel_record(device_id, records=records)
    if record is None:
        return {
            "status": "ineligible",
            "reason": "selected adapter is not a native Intel Vulkan ICD",
        }
    from taichi_vision.vulkan_probe import intel_vulkan_is_validated

    if intel_vulkan_is_validated(
        device_id=int(device_id), project_root=project_root
    ):
        return {"status": "valid", "device": record}
    key = _qualification_key(record, project_root)
    entry = _load_state().get("entries", {}).get(key, {})
    return {
        "status": entry.get("status", "unseen"),
        "key": key,
        "device": record,
        **entry,
    }


def _spawn_worker(command, log_path: Path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handle = log_path.open("a", encoding="utf-8")
    flags = 0
    if os.name == "nt":
        flags = (
            getattr(subprocess, "CREATE_NO_WINDOW", 0)
            | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            | getattr(subprocess, "DETACHED_PROCESS", 0)
        )
    try:
        process = subprocess.Popen(
            command,
            cwd=str(_project_root()),
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            close_fds=True,
            creationflags=flags,
            start_new_session=os.name != "nt",
        )
    finally:
        log_handle.close()
    return process


def schedule_intel_vulkan_qualification(
    device_id: int,
    project_root=None,
    parent_pid=None,
    timeout=1200.0,
    repeat=3,
    records=None,
    launcher=None,
) -> dict:
    """Schedule comprehensive qualification after the current app exits."""
    if os.environ.get("PIXEL_REFINE_INTEL_VULKAN_AUTO_QUALIFY", "1") == "0":
        return {"status": "disabled", "scheduled": False}
    root = Path(project_root or _project_root()).resolve()
    status = qualification_status(
        int(device_id), project_root=root, records=records
    )
    if status.get("status") in ("valid", "ineligible"):
        return {**status, "scheduled": False}
    key = status["key"]
    previous = _load_state().get("entries", {}).get(key, {})
    cooldown = float(
        os.environ.get(
            "PIXEL_REFINE_INTEL_VULKAN_RETRY_COOLDOWN",
            DEFAULT_FAILURE_COOLDOWN_S,
        )
    )
    if (
        previous.get("status") == "quarantined"
        and time.time() - float(previous.get("updated_at", 0)) < cooldown
    ):
        return {
            **status,
            "status": "cooldown",
            "scheduled": False,
            "reason": previous.get("error", "previous qualification failed"),
        }
    ttl = float(
        os.environ.get(
            "PIXEL_REFINE_INTEL_VULKAN_SCHEDULE_TTL",
            DEFAULT_SCHEDULE_TTL_S,
        )
    )
    if not _claim_schedule(key, ttl):
        return {**status, "status": "scheduled", "scheduled": False}

    log_path = _state_root() / f"{key}.log"
    command = [
        sys.executable,
        "-u",
        str(Path(__file__).resolve()),
        "--worker",
        "--project-root",
        str(root),
        "--device",
        str(int(device_id)),
        "--parent-pid",
        str(int(parent_pid if parent_pid is not None else os.getpid())),
        "--timeout",
        str(float(timeout)),
        "--repeat",
        str(max(1, int(repeat))),
        "--key",
        key,
    ]
    try:
        process = (launcher or _spawn_worker)(command, log_path)
        worker_pid = int(getattr(process, "pid", 0) or 0)
        if worker_pid:
            _write_lock_owner(key, worker_pid)
        entry = _update_entry(
            key,
            status="scheduled",
            device=status["device"],
            selector=make_device_selector(status["device"]),
            worker_pid=worker_pid,
            parent_pid=int(parent_pid if parent_pid is not None else os.getpid()),
            log=str(log_path),
            error="",
        )
        return {**entry, "key": key, "scheduled": True}
    except Exception as exc:
        _release_schedule(key)
        entry = _update_entry(
            key,
            status="schedule_failed",
            device=status["device"],
            error=f"{type(exc).__name__}: {exc}",
        )
        return {**entry, "key": key, "scheduled": False}


def _wait_for_parent(parent_pid: int, timeout_s: float) -> bool:
    if parent_pid <= 0 or parent_pid == os.getpid():
        return True
    if os.name == "nt":
        synchronize = 0x00100000
        handle = ctypes.windll.kernel32.OpenProcess(
            synchronize, False, int(parent_pid)
        )
        if not handle:
            return True
        try:
            wait_ms = min(int(max(0.0, timeout_s) * 1000), 0xFFFFFFFE)
            result = ctypes.windll.kernel32.WaitForSingleObject(handle, wait_ms)
            return result == 0
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    deadline = time.monotonic() + max(0.0, timeout_s)
    while time.monotonic() < deadline:
        try:
            os.kill(parent_pid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            pass
        time.sleep(1.0)
    return False


def _run_worker(args) -> int:
    key = str(args.key)
    try:
        if not _wait_for_parent(int(args.parent_pid), DEFAULT_PARENT_WAIT_S):
            _update_entry(
                key,
                status="deferred",
                error="parent application did not exit before qualification timeout",
            )
            return 2
        _update_entry(key, status="running", worker_pid=os.getpid(), error="")
        from taichi_vision.vulkan_probe import (
            run_all_intel_vulkan_comprehensive,
        )

        aggregate = run_all_intel_vulkan_comprehensive(
            project_root=args.project_root,
            timeout=float(args.timeout),
            probe_repeats=max(1, int(args.repeat)),
            persist=True,
        )
        report = next(
            (
                item
                for item in aggregate.get("reports", [])
                if int(item.get("device", {}).get("ordinal", -1))
                == int(args.device)
            ),
            {
                "ok": False,
                "error": (
                    "selected Intel adapter disappeared before qualification"
                ),
            },
        )
        _update_entry(
            key,
            status="valid" if report.get("ok") else "quarantined",
            passed=int(report.get("passed", 0)),
            total=int(report.get("total", 0)),
            pipeline_passed=bool(report.get("pipeline_passed", False)),
            artifact_loaded=int(report.get("artifact_loaded", 0)),
            artifact_total=int(report.get("artifact_total", 0)),
            error=str(report.get("error") or ""),
        )
        return 0 if report.get("ok") else 1
    except Exception as exc:
        _update_entry(
            key,
            status="quarantined",
            error=f"{type(exc).__name__}: {exc}",
        )
        return 1
    finally:
        _release_schedule(key)


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--project-root", default=str(_project_root()))
    parser.add_argument("--device", type=int, required=True)
    parser.add_argument("--parent-pid", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=1200.0)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--key", default="")
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    if not args.worker:
        status = qualification_status(args.device, args.project_root)
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0 if status.get("status") == "valid" else 1
    if not args.key:
        raise SystemExit("--key is required in worker mode")
    return _run_worker(args)


if __name__ == "__main__":
    raise SystemExit(main())
