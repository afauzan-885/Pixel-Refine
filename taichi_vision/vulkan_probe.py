"""Crash-isolated native Vulkan readiness probe.

The production dispatcher must never learn that a driver is safe merely
because runtime construction succeeded.  This module runs the native bridge
in a child process and records progress after every lifecycle gate so an
access violation or driver abort can be attributed to the last completed
stage.

This file intentionally lives outside ``taichi_vision.taichi_aot``. Importing
that package creates the process-wide AOT singleton, which would defeat probe
isolation and could route quarantined Intel Vulkan back to OpenGL.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import math
import re
import subprocess
import sys
import tempfile
import threading
import time

# Running this file directly makes ``taichi_vision`` (rather than its parent)
# sys.path[0]. Add the repository root before importing the shared helpers.
_IMPORT_ROOT = Path(__file__).resolve().parent.parent
if str(_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_IMPORT_ROOT))

from taichi_vision.device_selection import (
    device_fingerprint,
    is_translation_device,
    make_device_selector,
    normalize_device_name,
    query_vulkan_device_limits,
    query_vulkan_memory_budget,
    resolve_device_selector,
    scan_vulkan_device_records,
)
from taichi_vision.spirv_compatibility import (
    AUDIT_SCHEMA,
    audit_vulkan_inventory,
    evaluate_device_compatibility,
)


PROBE_SCHEMA = 2
VALIDATION_SCHEMA = 4
_INVENTORY_CACHE = {}
_INVENTORY_CACHE_LOCK = threading.RLock()
STAGES = (
    "enumerated",
    "runtime_initialized",
    "host_roundtrip",
    "device_copy_roundtrip",
    "module_loaded",
    "graph_dispatched",
    "graph_readback",
    "artifact_inventory_loaded",
    "module_destroyed",
    "buffers_destroyed",
    "runtime_destroyed",
)


class DynamicArg(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("arg_type", ctypes.c_int),
        ("dtype", ctypes.c_int),
        ("dim_count", ctypes.c_int),
        ("shape", ctypes.c_int32 * 8),
        ("elem_dim_count", ctypes.c_int),
        ("elem_shape", ctypes.c_int32 * 8),
        ("is_vector", ctypes.c_int),
        ("vector_dim", ctypes.c_int),
        ("val_u64", ctypes.c_uint64),
    ]


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _bridge_path(root: Path) -> Path:
    return (
        root
        / "taichi_vision"
        / "taichi_algorithm"
        / "aot_py"
        / "aot_dll"
        / "vulkan"
        / "taichi_aot_engine.dll"
    )


def _default_module(root: Path) -> Path:
    return (
        root
        / "taichi_vision"
        / "taichi_algorithm"
        / "aot_tcm"
        / "vulkan_x86_64_windows"
        / "common_vulkan_x86_64_windows.tcm"
    )


def _vulkan_artifacts(root: Path):
    """Return target-qualified Vulkan artifacts, excluding legacy root files."""

    artifact_root = root / "taichi_vision" / "taichi_algorithm" / "aot_tcm"
    target_root = artifact_root / "vulkan_x86_64_windows"
    return sorted(target_root.glob("*_vulkan_x86_64_windows.tcm"), key=lambda p: p.name)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def vulkan_inventory_digest(project_root=None):
    """Hash every shipped Vulkan artifact and the active bridge binary."""
    root = Path(project_root or _project_root()).resolve()
    artifact_root = (
        root / "taichi_vision" / "taichi_algorithm" / "aot_tcm"
    )
    paths = _vulkan_artifacts(root)
    artifact_count = len(paths)
    bridge = _bridge_path(root)
    if bridge.is_file():
        paths.append(bridge)
    runtime_sources = sorted(
        (root / "taichi_vision" / "taichi_aot").glob("*.py"),
        key=lambda path: path.name,
    )
    runtime_sources.extend(
        (
            root / "taichi_vision" / "device_selection.py",
            root / "taichi_vision" / "intel_vulkan_qualification.py",
            root / "taichi_vision" / "spirv_compatibility.py",
            root
            / "pixel_refine_desktop"
            / "ui"
            / "views"
            / "settings"
            / "Perfomance"
            / "test_comprehensif.py",
            Path(__file__).resolve(),
        )
    )
    for source in runtime_sources:
        if source.is_file():
            paths.append(source)
    cache_key = str(root)
    signature = tuple(
        (
            str(path.resolve()),
            int(path.stat().st_size),
            int(path.stat().st_mtime_ns),
        )
        for path in paths
    )
    with _INVENTORY_CACHE_LOCK:
        cached = _INVENTORY_CACHE.get(cache_key)
        if cached and cached["signature"] == signature:
            result = cached["result"]
            return {
                "digest": result["digest"],
                "artifact_count": result["artifact_count"],
                "components": dict(result["components"]),
            }
    digest = hashlib.sha256()
    components = {}
    for path in paths:
        try:
            identifier = path.resolve().relative_to(root).as_posix()
        except ValueError:
            identifier = path.name
        file_digest = _sha256_file(path)
        components[identifier] = file_digest
        digest.update(identifier.encode("utf-8"))
        digest.update(file_digest.encode("ascii"))
    result = {
        "digest": digest.hexdigest(),
        "artifact_count": artifact_count,
        "components": dict(sorted(components.items())),
    }
    with _INVENTORY_CACHE_LOCK:
        _INVENTORY_CACHE[cache_key] = {
            "signature": signature,
            "result": result,
        }
    return {
        "digest": result["digest"],
        "artifact_count": result["artifact_count"],
        "components": dict(result["components"]),
    }


def _validation_key(record, project_root=None):
    inventory = vulkan_inventory_digest(project_root)
    identity = {
        "schema": VALIDATION_SCHEMA,
        "fingerprint": device_fingerprint(record),
        "driver_uuid": record.get("driver_uuid", ""),
        "driver_version": record.get("driver_version", ""),
        "api_version": record.get("api_version", ""),
        "inventory": inventory["digest"],
    }
    token = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(token.encode("utf-8")).hexdigest(), inventory


def _validation_path():
    configured = os.environ.get("PIXEL_REFINE_INTEL_VULKAN_VALIDATION")
    if configured:
        return Path(configured).resolve()
    base = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir()))
    return base / "PixelRefine" / "intel_vulkan_validation.json"


def _load_validation_manifest():
    path = _validation_path()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except (OSError, TypeError, ValueError):
        return {}


def save_intel_vulkan_validation(report, project_root=None):
    """Persist a driver/artifact-specific validation result atomically."""
    record = report.get("device") or {}
    key, inventory = _validation_key(record, project_root)
    path = _validation_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = _load_validation_manifest()
    entries = manifest.setdefault("entries", {})
    entries[key] = {
        "status": "valid" if report.get("ok") else "quarantined",
        "validated_at": time.time(),
        "device": record,
        "selector": make_device_selector(record),
        "inventory": inventory,
        "passed": int(report.get("passed", 0)),
        "total": int(report.get("total", 0)),
        "pipeline_passed": bool(report.get("pipeline_passed", False)),
        "probe_attempts": int(report.get("probe_attempts", 0)),
        "artifact_loaded": int(report.get("artifact_loaded", 0)),
        "artifact_total": int(report.get("artifact_total", 0)),
        "static_compatibility": report.get("static_compatibility", {}),
        "spirv_audit": report.get("spirv_audit", {}),
        "error": str(report.get("error") or ""),
    }
    manifest["schema"] = VALIDATION_SCHEMA
    staging = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    staging.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    os.replace(staging, path)
    return str(path)


def get_intel_vulkan_validation(
    device_id=None, project_root=None, records=None
):
    """Return an exact current driver/artifact validation entry or ``None``."""
    records = records or scan_vulkan_device_records()
    native = [
        record
        for record in records
        if record.get("vendor") == "intel"
        and not is_translation_device(record)
    ]
    if device_id is None:
        record = native[0] if native else None
    else:
        record = next(
            (
                item
                for item in native
                if int(item.get("ordinal", -1)) == int(device_id)
            ),
            None,
        )
    if record is None:
        return None
    key, _inventory = _validation_key(record, project_root)
    entry = _load_validation_manifest().get("entries", {}).get(key)
    if not isinstance(entry, dict) or entry.get("status") != "valid":
        return None
    static = entry.get("static_compatibility")
    audit = entry.get("spirv_audit")
    if (
        not isinstance(static, dict)
        or not static.get("compatible")
        or not isinstance(audit, dict)
        or audit.get("schema") != AUDIT_SCHEMA
        or not audit.get("valid")
    ):
        return None
    return entry


def intel_vulkan_is_validated(device_id=None, project_root=None) -> bool:
    return get_intel_vulkan_validation(device_id, project_root) is not None


def _write_result(path: Path, state: dict) -> None:
    state["updated_at"] = time.time()
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(state, indent=2, sort_keys=True), encoding="utf-8"
    )
    os.replace(temporary, path)


def _configure_bridge(dll: Path):
    bridge = ctypes.CDLL(str(dll))
    bridge.init_aot_engine.argtypes = [ctypes.c_int, ctypes.c_int]
    bridge.init_aot_engine.restype = ctypes.c_void_p
    bridge.destroy_aot_engine.argtypes = [ctypes.c_void_p]
    bridge.destroy_aot_engine.restype = None
    bridge.allocate_gpu_buffer.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint64,
        ctypes.c_int,
    ]
    bridge.allocate_gpu_buffer.restype = ctypes.c_void_p
    bridge.free_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    bridge.free_gpu_buffer.restype = None
    bridge.write_to_gpu_buffer.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint64,
    ]
    bridge.write_to_gpu_buffer.restype = None
    bridge.read_from_gpu_buffer.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint64,
    ]
    bridge.read_from_gpu_buffer.restype = None
    bridge.copy_gpu_buffer.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint64,
    ]
    bridge.copy_gpu_buffer.restype = None
    bridge.sync_runtime.argtypes = [ctypes.c_void_p]
    bridge.sync_runtime.restype = None
    bridge.load_aot_module.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    bridge.load_aot_module.restype = ctypes.c_void_p
    bridge.destroy_aot_module.argtypes = [ctypes.c_void_p]
    bridge.destroy_aot_module.restype = None
    bridge.run_aot_graph.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.POINTER(DynamicArg),
        ctypes.c_int,
    ]
    bridge.run_aot_graph.restype = None
    try:
        bridge.get_last_engine_error.argtypes = [ctypes.c_void_p]
        bridge.get_last_engine_error.restype = ctypes.c_char_p
    except AttributeError:
        pass
    return bridge


def _ndarray_arg(name, memory, shape, dtype=0, element_shape=()):
    arg = DynamicArg()
    arg.name = str(name).encode("utf-8")
    arg.arg_type = 0
    arg.dtype = int(dtype)
    arg.dim_count = len(shape)
    for index, value in enumerate(shape):
        arg.shape[index] = int(value)
    arg.elem_dim_count = len(element_shape)
    for index, value in enumerate(element_shape):
        arg.elem_shape[index] = int(value)
    arg.is_vector = bool(element_shape)
    arg.vector_dim = int(element_shape[0]) if element_shape else 1
    arg.val_u64 = int(memory)
    return arg


def _scalar_i32_arg(name, value):
    arg = DynamicArg()
    arg.name = str(name).encode("utf-8")
    arg.arg_type = 1
    arg.dtype = 1
    arg.val_u64 = int(value) & 0xFFFFFFFFFFFFFFFF
    return arg


def _run_bicubic_graph(bridge, runtime, module, buffers):
    import cv2
    import numpy as np

    src_shape = (32, 32)
    dst_shape = (24, 24)
    source = (ctypes.c_float * (src_shape[0] * src_shape[1]))(
        *(
            ((row * src_shape[1] + column) % 97) / 96.0
            for row in range(src_shape[0])
            for column in range(src_shape[1])
        )
    )
    output = (ctypes.c_float * (dst_shape[0] * dst_shape[1]))()
    src_bytes = ctypes.sizeof(source)
    dst_bytes = ctypes.sizeof(output)
    src = bridge.allocate_gpu_buffer(runtime, src_bytes, 1)
    dst = bridge.allocate_gpu_buffer(runtime, dst_bytes, 0)
    readback = bridge.allocate_gpu_buffer(runtime, dst_bytes, 1)
    if not src or not dst or not readback:
        raise RuntimeError("bicubic probe buffer allocation failed")
    buffers.extend((src, dst, readback))
    bridge.write_to_gpu_buffer(runtime, src, source, src_bytes)
    args = (DynamicArg * 6)(
        _ndarray_arg("src", src, src_shape),
        _ndarray_arg("dst", dst, dst_shape),
        _scalar_i32_arg("h_src", src_shape[0]),
        _scalar_i32_arg("w_src", src_shape[1]),
        _scalar_i32_arg("h_dst", dst_shape[0]),
        _scalar_i32_arg("w_dst", dst_shape[1]),
    )
    bridge.run_aot_graph(
        runtime,
        module,
        b"bicubic_resize_f32_2d",
        args,
        len(args),
    )
    bridge.sync_runtime(runtime)
    try:
        error = bridge.get_last_engine_error(runtime)
    except AttributeError:
        error = None
    if error:
        detail = error.decode("utf-8", errors="replace")
        if detail:
            raise RuntimeError(f"bicubic graph dispatch failed: {detail}")
    bridge.copy_gpu_buffer(runtime, dst, readback, dst_bytes)
    bridge.read_from_gpu_buffer(runtime, readback, output, dst_bytes)
    values = list(output)
    if not all(math.isfinite(value) for value in values):
        raise RuntimeError("bicubic graph returned non-finite pixels")
    if max(values) - min(values) <= 1e-6:
        raise RuntimeError("bicubic graph returned a constant image")
    actual = np.ctypeslib.as_array(output).reshape(dst_shape).copy()
    source_np = np.ctypeslib.as_array(source).reshape(src_shape)
    expected = cv2.resize(
        source_np,
        (dst_shape[1], dst_shape[0]),
        interpolation=cv2.INTER_CUBIC,
    )
    delta = np.abs(actual - expected)
    return {
        "minimum": min(values),
        "maximum": max(values),
        "mean": sum(values) / len(values),
        "opencv_mae": float(delta.mean()),
        "opencv_max_error": float(delta.max()),
    }


def _child_probe(args) -> int:
    result_path = Path(args.result).resolve()
    root = Path(args.project_root).resolve()
    dll = Path(args.bridge).resolve()
    module_path = Path(args.module).resolve() if args.module else None
    state = {
        "schema": PROBE_SCHEMA,
        "ok": False,
        "device_ordinal": int(args.device),
        "last_stage": "starting",
        "completed_stages": [],
        "error": "",
    }
    _write_result(result_path, state)

    runtime = None
    module = None
    buffers = []

    def complete(stage):
        state["last_stage"] = stage
        state["completed_stages"].append(stage)
        _write_result(result_path, state)

    try:
        # These switches affect only this disposable child process. The Python
        # production quarantine remains untouched.
        os.environ["PIXEL_REFINE_AOT_ALLOW_CPU_FALLBACK"] = "0"
        os.environ["PIXEL_REFINE_VULKAN_SERIALIZE_SUBMIT"] = "1"
        os.environ["PIXEL_REFINE_AOT_INTEL_PROBE"] = "1"
        bridge = _configure_bridge(dll)

        complete("enumerated")
        runtime = bridge.init_aot_engine(0, int(args.device))
        if not runtime:
            raise RuntimeError("native bridge returned a null Vulkan runtime")
        complete("runtime_initialized")

        count = 1024
        size = count * ctypes.sizeof(ctypes.c_uint32)
        source = (ctypes.c_uint32 * count)(
            *((index * 2654435761) & 0xFFFFFFFF for index in range(count))
        )
        output = (ctypes.c_uint32 * count)()

        upload = bridge.allocate_gpu_buffer(runtime, size, 1)
        if not upload:
            raise RuntimeError("host-visible upload allocation failed")
        buffers.append(upload)
        bridge.write_to_gpu_buffer(runtime, upload, source, size)
        bridge.read_from_gpu_buffer(runtime, upload, output, size)
        if bytes(source) != bytes(output):
            raise RuntimeError("host-visible buffer roundtrip mismatch")
        complete("host_roundtrip")

        device = bridge.allocate_gpu_buffer(runtime, size, 0)
        readback = bridge.allocate_gpu_buffer(runtime, size, 1)
        if not device or not readback:
            raise RuntimeError("device/readback allocation failed")
        buffers.extend((device, readback))
        bridge.copy_gpu_buffer(runtime, upload, device, size)
        bridge.copy_gpu_buffer(runtime, device, readback, size)
        bridge.read_from_gpu_buffer(runtime, readback, output, size)
        if bytes(source) != bytes(output):
            raise RuntimeError("device-copy roundtrip mismatch")
        complete("device_copy_roundtrip")

        if module_path is not None:
            module = bridge.load_aot_module(
                runtime, str(module_path).encode("utf-8")
            )
            if not module:
                raise RuntimeError(
                    f"AOT module load failed: {module_path.name}"
                )
            complete("module_loaded")
            if args.graph == "bicubic_resize_f32_2d":
                state["graph"] = args.graph
                bridge.sync_runtime(runtime)
                state["graph_output"] = _run_bicubic_graph(
                    bridge, runtime, module, buffers
                )
                complete("graph_dispatched")
                complete("graph_readback")
            bridge.sync_runtime(runtime)
            bridge.destroy_aot_module(module)
            module = None
            complete("module_destroyed")

        if args.inventory:
            artifacts = sorted(
                (
                    root
                    / "taichi_vision"
                    / "taichi_algorithm"
                    / "aot_tcm"
                ).glob("vulkan_x86_64_windows/*_vulkan_x86_64_windows.tcm"),
                key=lambda path: path.name,
            )
            state["artifact_total"] = len(artifacts)
            state["artifact_loaded"] = 0
            state["artifact_names"] = []
            for artifact in artifacts:
                state["current_module"] = artifact.name
                _write_result(result_path, state)
                candidate = bridge.load_aot_module(
                    runtime, str(artifact).encode("utf-8")
                )
                if not candidate:
                    raise RuntimeError(
                        f"AOT inventory load failed: {artifact.name}"
                    )
                bridge.sync_runtime(runtime)
                bridge.destroy_aot_module(candidate)
                state["artifact_names"].append(artifact.name)
                state["artifact_loaded"] += 1
                _write_result(result_path, state)
            state["current_module"] = ""
            complete("artifact_inventory_loaded")

        bridge.sync_runtime(runtime)
        for memory in reversed(buffers):
            bridge.free_gpu_buffer(runtime, memory)
        buffers.clear()
        complete("buffers_destroyed")

        bridge.destroy_aot_engine(runtime)
        runtime = None
        complete("runtime_destroyed")
        state["ok"] = True
        state["error"] = ""
        _write_result(result_path, state)
        return 0
    except BaseException as exc:
        state["error"] = f"{type(exc).__name__}: {exc}"
        _write_result(result_path, state)
        return 1
    finally:
        # Best-effort cleanup is deliberately avoided after an exception.
        # A lifecycle failure must remain attributable to its exact stage, and
        # teardown itself is one of the operations under test.
        _ = (runtime, module, buffers, root)


def _native_intel_record(records, selector=None):
    candidates = [
        record
        for record in records
        if record.get("vendor") == "intel"
        and not is_translation_device(record)
    ]
    if selector:
        ordinal = resolve_device_selector(selector, candidates)
        for record in candidates:
            if record["ordinal"] == ordinal:
                return record
    return candidates[0] if candidates else None


def run_intel_vulkan_probe(
    project_root=None,
    selector=None,
    timeout=45.0,
    module_path=None,
    graph=None,
    inventory=False,
):
    """Run the native Intel lifecycle gate and return a JSON-safe report."""
    root = Path(project_root or _project_root()).resolve()
    records = scan_vulkan_device_records()
    record = _native_intel_record(records, selector=selector)
    if record is None:
        return {
            "schema": PROBE_SCHEMA,
            "ok": False,
            "last_stage": "enumeration_failed",
            "completed_stages": [],
            "error": "No native Intel Vulkan ICD was found (Dozen excluded)",
            "devices": records,
        }

    dll = _bridge_path(root)
    module = (
        None
        if inventory
        else (
            Path(module_path).resolve()
            if module_path
            else _default_module(root)
        )
    )
    if not dll.is_file():
        raise FileNotFoundError(f"Vulkan AOT bridge not found: {dll}")
    if module is not None and not module.is_file():
        raise FileNotFoundError(f"Vulkan probe artifact not found: {module}")

    with tempfile.TemporaryDirectory(prefix="pixel_refine_vk_probe_") as temp:
        result_path = Path(temp) / "result.json"
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--child",
            "--project-root",
            str(root),
            "--bridge",
            str(dll),
            "--device",
            str(record["ordinal"]),
            "--result",
            str(result_path),
        ]
        if module is not None:
            command.extend(["--module", str(module)])
        if graph:
            command.extend(["--graph", str(graph)])
        if inventory:
            command.append("--inventory")
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            process = subprocess.run(
                command,
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=float(timeout),
                creationflags=flags,
                check=False,
            )
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            process = exc
            timed_out = True

        if result_path.is_file():
            report = json.loads(result_path.read_text(encoding="utf-8"))
        else:
            report = {
                "schema": PROBE_SCHEMA,
                "ok": False,
                "last_stage": "child_start_failed",
                "completed_stages": [],
                "error": "Probe child exited before writing its first checkpoint",
            }

        report.update(
            {
                "device": record,
                "selector": make_device_selector(record),
                "fingerprint": device_fingerprint(record),
                "module": module.name if module is not None else "all_vulkan_artifacts",
                "timed_out": timed_out,
                "returncode": None if timed_out else process.returncode,
                "stdout": process.stdout or "",
                "stderr": process.stderr or "",
            }
        )
        if timed_out:
            report["ok"] = False
            report["error"] = (
                f"Probe timed out after {float(timeout):.1f}s; "
                f"last completed stage: {report.get('last_stage')}"
            )
        elif process.returncode != 0:
            report["ok"] = False
            if not report.get("error"):
                report["error"] = (
                    f"Probe child exited with code {process.returncode}"
                )
        return report

def run_intel_vulkan_comprehensive(
    project_root=None,
    timeout=900.0,
    probe_repeats=5,
    persist=False,
    device_id=None,
    artifact_audit=None,
):
    """Run lifecycle, parity, and 24 MP pipeline gates on native Intel Vulkan."""
    root = Path(project_root or _project_root()).resolve()
    records = scan_vulkan_device_records()
    if device_id is None:
        record = _native_intel_record(records)
    else:
        record = next(
            (
                item
                for item in records
                if int(item.get("ordinal", -1)) == int(device_id)
                and item.get("vendor") == "intel"
                and not is_translation_device(item)
            ),
            None,
        )
    if record is None:
        selected = (
            ""
            if device_id is None
            else f"Selected Vulkan ordinal {int(device_id)} is not a native Intel ICD; "
        )
        report = {
            "schema": VALIDATION_SCHEMA,
            "ok": False,
            "device": {},
            "passed": 0,
            "total": 0,
            "pipeline_passed": False,
            "probe_attempts": 0,
            "error": selected
            + "no qualifying native Intel Vulkan ICD was found (Dozen excluded)",
        }
        if persist:
            save_intel_vulkan_validation(report, root)
        return report

    try:
        static_audit = artifact_audit or audit_vulkan_inventory(
            project_root=root, target_env="vulkan1.1"
        )
        device_capabilities = query_vulkan_memory_budget(record["ordinal"])
        limits = query_vulkan_device_limits(
            record["ordinal"]
        )
        if normalize_device_name(limits.get("device_name")) != normalize_device_name(
            record.get("name")
        ):
            raise RuntimeError(
                "Vulkan limit ordinal changed during qualification: "
                f"expected {record.get('name')!r}, got "
                f"{limits.get('device_name')!r}"
            )
        device_capabilities["limits"] = limits
        static_compatibility = evaluate_device_compatibility(
            record, static_audit, device_capabilities
        )
    except Exception as exc:
        static_audit = {
            "schema": AUDIT_SCHEMA,
            "valid": False,
            "error": f"{type(exc).__name__}: {exc}",
        }
        static_compatibility = {
            "compatible": False,
            "reasons": ["Static Vulkan compatibility audit could not complete"],
        }

    static_summary = {
        key: value
        for key, value in static_audit.items()
        if key != "artifacts"
    }
    if not static_compatibility.get("compatible"):
        report = {
            "schema": VALIDATION_SCHEMA,
            "ok": False,
            "device": record,
            "passed": 0,
            "total": 0,
            "pipeline_passed": False,
            "probe_attempts": 0,
            "spirv_audit": static_summary,
            "static_compatibility": static_compatibility,
            "error": "Intel Vulkan rejected before dispatch: "
            + "; ".join(static_compatibility.get("reasons", [])),
        }
        if persist:
            report["manifest"] = save_intel_vulkan_validation(report, root)
        return report

    bicubic = (
        root
        / "taichi_vision"
        / "taichi_algorithm"
        / "aot_tcm"
        / "vulkan_x86_64_windows"
        / "bicubic_vulkan_x86_64_windows.tcm"
    )
    probes = [
        run_intel_vulkan_probe(
            project_root=root,
            selector=make_device_selector(record),
            timeout=min(float(timeout), 60.0),
            module_path=bicubic,
            graph="bicubic_resize_f32_2d",
        )
        for _ in range(max(1, int(probe_repeats)))
    ]
    if not all(item.get("ok") for item in probes):
        failed = next(item for item in probes if not item.get("ok"))
        report = {
            "schema": VALIDATION_SCHEMA,
            "ok": False,
            "device": record,
            "passed": 0,
            "total": 0,
            "pipeline_passed": False,
            "probe_attempts": len(probes),
            "error": (
                "Native lifecycle probe failed at "
                f"{failed.get('last_stage')}: {failed.get('error')}"
            ),
            "probe_reports": probes,
            "spirv_audit": static_summary,
            "static_compatibility": static_compatibility,
        }
        if persist:
            report["manifest"] = save_intel_vulkan_validation(report, root)
        return report

    inventory_report = run_intel_vulkan_probe(
        project_root=root,
        selector=make_device_selector(record),
        timeout=min(float(timeout), 180.0),
        inventory=True,
    )
    inventory_complete = bool(
        inventory_report.get("ok")
        and inventory_report.get("artifact_total", 0) > 0
        and inventory_report.get("artifact_loaded")
        == inventory_report.get("artifact_total")
    )
    if not inventory_complete:
        report = {
            "schema": VALIDATION_SCHEMA,
            "ok": False,
            "device": record,
            "passed": 0,
            "total": 0,
            "pipeline_passed": False,
            "probe_attempts": len(probes),
            "artifact_loaded": int(
                inventory_report.get("artifact_loaded", 0)
            ),
            "artifact_total": int(
                inventory_report.get("artifact_total", 0)
            ),
            "error": (
                "Vulkan artifact inventory failed at "
                f"{inventory_report.get('current_module')}: "
                f"{inventory_report.get('error')}"
            ),
            "inventory_report": inventory_report,
            "spirv_audit": static_summary,
            "static_compatibility": static_compatibility,
        }
        if persist:
            report["manifest"] = save_intel_vulkan_validation(report, root)
        return report

    test_script = (
        root
        / "pixel_refine_desktop"
        / "ui"
        / "views"
        / "settings"
        / "Perfomance"
        / "test_comprehensif.py"
    )
    environment = os.environ.copy()
    environment.update(
        {
            "PIXEL_REFINE_AOT_ARCH": "vulkan",
            "PIXEL_REFINE_AOT_DEVICE": str(record["ordinal"]),
            "PIXEL_REFINE_AOT_INTEL_PROBE": "1",
            "PIXEL_REFINE_AOT_ALLOW_UNSAFE_INTEL": "1",
            "PIXEL_REFINE_VULKAN_SERIALIZE_SUBMIT": "1",
            "PIXEL_REFINE_AOT_SAFE_TEARDOWN": "0",
            "PIXEL_REFINE_AOT_ALLOW_CPU_FALLBACK": "0",
            "VK_LOADER_DEBUG": "error",
        }
    )
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        process = subprocess.run(
            [sys.executable, "-u", str(test_script), "--run-logic"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=float(timeout),
            creationflags=flags,
            env=environment,
            check=False,
        )
        timed_out = False
        output = "\n".join(
            part for part in (process.stdout, process.stderr) if part
        )
        returncode = process.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        output = "\n".join(
            part.decode("utf-8", errors="replace")
            if isinstance(part, bytes)
            else (part or "")
            for part in (exc.stdout, exc.stderr)
            if part
        )
        returncode = None

    matches = re.findall(r"Results:\s*(\d+)\s*/\s*(\d+)", output)
    passed, total = (
        (int(matches[-1][0]), int(matches[-1][1]))
        if matches else (0, 0)
    )
    pipeline_passed = (
        "OBG Accuracy MAE (vs Standard):" in output
        and "Pipeline Test Failed" not in output
    )
    ok = bool(
        not timed_out
        and returncode == 0
        and total > 0
        and passed == total
        and pipeline_passed
        and "ALL TESTS PASSED" in output
    )
    report = {
        "schema": VALIDATION_SCHEMA,
        "ok": ok,
        "device": record,
        "passed": passed,
        "total": total,
        "pipeline_passed": pipeline_passed,
        "probe_attempts": len(probes),
        "artifact_loaded": int(inventory_report["artifact_loaded"]),
        "artifact_total": int(inventory_report["artifact_total"]),
        "probe_opencv_mae_max": max(
            item.get("graph_output", {}).get("opencv_mae", float("inf"))
            for item in probes
        ),
        "returncode": returncode,
        "timed_out": timed_out,
        "error": "" if ok else (
            "Comprehensive Intel Vulkan gate failed or produced incomplete evidence"
        ),
        "stdout": output,
        "spirv_audit": static_summary,
        "static_compatibility": static_compatibility,
    }
    if persist:
        report["manifest"] = save_intel_vulkan_validation(report, root)
    return report


def run_all_intel_vulkan_comprehensive(
    project_root=None,
    timeout=900.0,
    probe_repeats=5,
    persist=False,
):
    """Qualify every native Intel ICD and persist independent manifests."""
    records = scan_vulkan_device_records()
    devices = [
        record
        for record in records
        if record.get("vendor") == "intel"
        and not is_translation_device(record)
    ]
    if not devices:
        return {
            "schema": VALIDATION_SCHEMA,
            "ok": False,
            "device_count": 0,
            "passed_devices": 0,
            "reports": [],
            "error": "No native Intel Vulkan ICD was found (Dozen excluded)",
        }
    try:
        shared_audit = audit_vulkan_inventory(
            project_root=project_root, target_env="vulkan1.1"
        )
    except Exception:
        # The per-device runner will produce and persist the detailed
        # fail-closed diagnostic for the same audit failure.
        shared_audit = None
    reports = [
        run_intel_vulkan_comprehensive(
            project_root=project_root,
            timeout=timeout,
            probe_repeats=probe_repeats,
            persist=persist,
            device_id=record["ordinal"],
            artifact_audit=shared_audit,
        )
        for record in devices
    ]
    return {
        "schema": VALIDATION_SCHEMA,
        "ok": bool(reports) and all(report.get("ok") for report in reports),
        "device_count": len(devices),
        "passed_devices": sum(bool(report.get("ok")) for report in reports),
        "reports": reports,
        "error": "" if devices else "No native Intel Vulkan ICD was found",
    }


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=str(_project_root()))
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Run independent child-process lifecycle probes repeatedly",
    )
    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Run and verify the complete native Intel Vulkan suite",
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Persist an exact driver/artifact validation manifest",
    )
    parser.add_argument(
        "--all-intel",
        action="store_true",
        help="Qualify every native Intel Vulkan adapter (Dozen excluded)",
    )
    parser.add_argument("--module")
    parser.add_argument(
        "--graph",
        choices=("bicubic_resize_f32_2d",),
        help="Optionally dispatch a known graph after loading its module",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--inventory", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--bridge", help=argparse.SUPPRESS)
    parser.add_argument(
        "--device",
        type=int,
        help="Vulkan ordinal to qualify; must be a native Intel adapter",
    )
    parser.add_argument("--result", help=argparse.SUPPRESS)
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    if args.child:
        return _child_probe(args)
    if args.comprehensive:
        runner = (
            run_all_intel_vulkan_comprehensive
            if args.all_intel
            else run_intel_vulkan_comprehensive
        )
        kwargs = {
            "project_root": args.project_root,
            "timeout": args.timeout,
            "probe_repeats": max(1, int(args.repeat)),
            "persist": args.persist,
        }
        if not args.all_intel:
            kwargs["device_id"] = args.device
        payload = runner(**kwargs)
        printable = dict(payload)
        # Full suite output remains available to Python callers but would make
        # the command's JSON unnecessarily large.
        full_output = printable.pop("stdout", "")
        if args.all_intel:
            printable["reports"] = [
                {
                    key: value
                    for key, value in report.items()
                    if key != "stdout"
                }
                for report in payload.get("reports", [])
            ]
        if not payload.get("ok") and full_output:
            printable["stdout_tail"] = full_output[-12000:]
        print(json.dumps(printable, indent=2, sort_keys=True))
        return 0 if payload.get("ok") else 1
    reports = [
        run_intel_vulkan_probe(
            project_root=args.project_root,
            timeout=args.timeout,
            module_path=args.module,
            graph=args.graph,
            inventory=args.inventory,
        )
        for _ in range(max(1, int(args.repeat)))
    ]
    payload = reports[0] if len(reports) == 1 else {
        "schema": PROBE_SCHEMA,
        "ok": all(report.get("ok") for report in reports),
        "passed": sum(bool(report.get("ok")) for report in reports),
        "attempts": len(reports),
        "reports": reports,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
