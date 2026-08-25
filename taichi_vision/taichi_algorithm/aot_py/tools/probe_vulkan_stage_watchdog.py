"""Crash/timeout-isolated Vulkan stage watchdog.

This diagnostic deliberately starts a fresh Python process for every stage so
that the process-wide AOT singleton cannot blur an import/context failure with
an artifact or graph failure.  It is evidence-only: it never changes dispatch,
the native-evidence registry, or ``engine.py``.

Example (Intel Vulkan):

    python -m taichi_vision.taichi_algorithm.aot_py.tools.probe_vulkan_stage_watchdog \
        --backend vulkan --vendor intel --operation both --timeout 12

The child reports the backend/device and the stage at which it stopped.  A
timeout is intentionally a diagnostic result, not a successful native probe.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[4]


def _environment(backend: str, vendor: str, device: int) -> dict[str, str]:
    env = os.environ.copy()
    normalized = str(backend).strip().lower()
    env.update(
        {
            "PIXEL_REFINE_AOT_ARCH": normalized,
            "AOT_ARCH": normalized,
            "AOT_DEVICE": str(int(device)),
            "TARGET_VENDOR": str(vendor).strip().lower(),
            # Keep this tool diagnostic-only even when a caller has an old
            # migration flag in its shell environment.
            "PIXEL_REFINE_AOT_REGISTER_NATIVE_EVIDENCE": "0",
        }
    )
    return env


def _child_source(operation: str, stage: str) -> str:
    # Keep imports inside the child.  Importing aot_api in the parent would
    # initialize the singleton before the watchdog can classify the stage.
    return f'''\
import json, time, traceback\n
started = time.perf_counter()\n
try:\n
    import taichi_vision.taichi_aot as aot\n
    import taichi_vision.taichi_algorithm.aot_api as api\n
    imported_at = time.perf_counter()\n
    result = {{\n
        "backend": str(getattr(aot.engine, "arch", "")),\n
        "device": str(getattr(aot.engine, "gpu_name", "") or ""),\n
        "device_id": int(getattr(aot.engine, "device_id", 0)),\n
        "import_seconds": imported_at - started,\n
    }}\n
    if {stage!r} in ("load", "execute"):\n
        name = "akaze" if {operation!r} == "akaze" else "farneback_flow"\n
        module = api.load_tcm(name)\n
        result.update({{\n
            "artifact_stage": "loaded",\n
            "module": name,\n
            "module_ptr": bool(getattr(module, "module_ptr", None)),\n
        }})\n
    if {stage!r} == "execute":\n
        import numpy as np\n
        if {operation!r} == "akaze":\n
            # A bounded operation still exercises the first AKAZE graph while
            # keeping a watchdog useful on drivers that stall graph dispatch.
            image = np.linspace(0.0, 1.0, 32 * 32, dtype=np.float32).reshape(32, 32)\n
            value = api.akaze(image, image, max_keypoints=64, num_fed_steps=1)\n
            result["output_shape"] = [list(np.asarray(item).shape) for item in value]\n
        else:\n
            rows = np.linspace(0.0, 1.0, 32, dtype=np.float32)[:, None]\n
            cols = np.linspace(0.0, 1.0, 32, dtype=np.float32)[None, :]\n
            image = np.ascontiguousarray((rows + cols) * np.float32(100.0))\n
            value = api._farneback_flow_full(image, image, num_levels=1, num_iters=1, win_size=7, poly_n=5, poly_sigma=1.1)\n
            result["output_shape"] = list(np.asarray(value).shape)\n
        result["execution_stage"] = "completed"\n
    result["stage"] = {stage!r}\n
    result["seconds"] = time.perf_counter() - started\n
    print(json.dumps(result, sort_keys=True), flush=True)\n
except BaseException as exc:\n
    print(json.dumps({{\n
        "stage": {stage!r},\n
        "seconds": time.perf_counter() - started,\n
        "error_type": type(exc).__name__,\n
        "error": str(exc),\n
        "traceback_tail": traceback.format_exc().splitlines()[-8:],\n
    }}, sort_keys=True), flush=True)\n
    raise\n
'''


def run_stage(*, backend: str, vendor: str, device: int, operation: str, stage: str, timeout: float) -> dict[str, Any]:
    started = time.perf_counter()
    command = [sys.executable, "-X", "utf8", "-c", _child_source(operation, stage)]
    try:
        completed = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            env=_environment(backend, vendor, device),
            capture_output=True,
            text=True,
            timeout=float(timeout),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "backend_requested": backend,
            "vendor_requested": vendor,
            "device_requested": int(device),
            "operation": operation,
            "stage": stage,
            "status": "timeout",
            "timeout_seconds": float(timeout),
            "seconds": time.perf_counter() - started,
            "stdout_tail": (exc.stdout or "")[-2000:],
            "stderr_tail": (exc.stderr or "")[-2000:],
        }

    parsed: dict[str, Any] | None = None
    for line in reversed(completed.stdout.splitlines()):
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict):
            parsed = candidate
            break
    result = parsed or {}
    result.update(
        {
            "backend_requested": backend,
            "vendor_requested": vendor,
            "device_requested": int(device),
            "operation": operation,
            "stage": stage,
            "status": "ok" if completed.returncode == 0 else "error",
            "returncode": completed.returncode,
            "seconds": time.perf_counter() - started,
            "stdout_tail": completed.stdout[-2000:],
            "stderr_tail": completed.stderr[-2000:],
        }
    )
    return result


def run(*, backend: str, vendor: str, device: int, operation: str, timeout: float) -> dict[str, Any]:
    if operation not in {"akaze", "moving-flow"}:
        raise ValueError("operation must be 'akaze' or 'moving-flow'")
    stages = {
        "import": run_stage(backend=backend, vendor=vendor, device=device, operation=operation, stage="import", timeout=timeout),
        "load": run_stage(backend=backend, vendor=vendor, device=device, operation=operation, stage="load", timeout=timeout),
        "execute": run_stage(backend=backend, vendor=vendor, device=device, operation=operation, stage="execute", timeout=timeout),
    }
    return {"operation": operation, "stages": stages, "passed": all(item.get("status") == "ok" for item in stages.values())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="vulkan")
    parser.add_argument("--vendor", default="intel")
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--operation", choices=("akaze", "moving-flow"), default="moving-flow")
    parser.add_argument("--timeout", type=float, default=12.0)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    result = run(backend=args.backend, vendor=args.vendor, device=args.device, operation=args.operation, timeout=args.timeout)
    text = json.dumps(result, indent=2, sort_keys=True, default=str)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
