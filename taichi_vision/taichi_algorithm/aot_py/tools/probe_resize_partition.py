"""Parity probe for the specialized coordinate-domain resize executor.

The resize implementation is not a generic local adapter: every output tile
is mapped back into one global source frame through the offset AOT graph.  This
probe therefore compares the exact same backend's full-frame graph with the
specialized offset/batched tile path at deliberately non-multiple shapes.  A
successful result qualifies only the backend/device printed in the JSON; it
does not promote the generic automatic-block registry.

Examples (repository root)::

    $env:BACKEND = "cpu"
    python -m taichi_vision.taichi_algorithm.aot_py.tools.probe_resize_partition --backend cpu

    $env:BACKEND = "vulkan"
    $env:VULKAN_VENDOR = "nvidia"
    python -m taichi_vision.taichi_algorithm.aot_py.tools.probe_resize_partition --backend vulkan --device 0
    python -m taichi_vision.taichi_algorithm.aot_py.tools.probe_resize_partition --backend opengl --device 0 --expected-vendor NVIDIA
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Iterable, Mapping

import numpy as np


# Keep direct-file invocation equivalent to ``python -m`` invocation.
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Source and destination dimensions are intentionally not divisible by the
# default probe tile (7).  RGB and grayscale cover both offset graph variants.
DEFAULT_CASES: tuple[tuple[tuple[int, ...], tuple[int, int]], ...] = (
    ((23, 31), (17, 19)),
    ((29, 37, 3), (13, 22)),
    ((17, 25), (31, 11)),
    ((31, 27, 3), (15, 19)),
)

INTERPOLATIONS = {
    "linear": "INTER_LINEAR",
    "cubic": "INTER_CUBIC",
    "area": "INTER_AREA",
}


def _cuda_device_name(device: int) -> str:
    """Resolve CUDA ordinal through the installed NVIDIA driver.

    The native bridge may not expose a CUDA model string.  A resize
    qualification must not accept an empty name or infer a vendor from an
    ordinal, so use the driver identity and fail closed when unavailable.
    """

    try:
        ordinal = int(device)
    except (TypeError, ValueError):
        return ""
    if ordinal < 0:
        return ""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                f"--id={ordinal}",
                "--query-gpu=name",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    return next(
        (line.strip() for line in result.stdout.splitlines() if line.strip()),
        "",
    )


def _max_abs_error(left: Any, right: Any) -> float:
    first = np.asarray(left)
    second = np.asarray(right)
    if first.shape != second.shape:
        return float("inf")
    if first.size == 0:
        return 0.0
    return float(
        np.max(
            np.abs(
                first.astype(np.float64, copy=False)
                - second.astype(np.float64, copy=False)
            )
        )
    )


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def _parse_interpolations(value: str | Iterable[str] | None) -> tuple[str, ...]:
    if value is None:
        return tuple(INTERPOLATIONS)
    if isinstance(value, str):
        values = [part.strip().lower() for part in value.split(",") if part.strip()]
    else:
        values = [str(part).strip().lower() for part in value if str(part).strip()]
    if not values:
        return tuple(INTERPOLATIONS)
    unknown = [name for name in values if name not in INTERPOLATIONS]
    if unknown:
        raise ValueError(
            "unknown interpolation(s): "
            + ", ".join(sorted(set(unknown)))
            + "; choose from "
            + ", ".join(INTERPOLATIONS)
        )
    return tuple(dict.fromkeys(values))


def _validate_device_identity(
    device_name: str,
    *,
    expected_vendor: str | None = None,
    expected_device: str | None = None,
) -> None:
    """Fail closed when a qualification target is not the requested device.

    Backend selection variables are advisory on multi-GPU Windows systems;
    the runtime-reported identity is authoritative.  Qualification commands
    can therefore pass both an expected vendor and exact device name so a
    context accidentally created on another adapter cannot become evidence.
    """

    actual = str(device_name or "").strip()
    if expected_vendor:
        vendor = str(expected_vendor).strip().casefold()
        if not vendor or vendor not in actual.casefold():
            raise RuntimeError(
                "resize probe device vendor mismatch: expected "
                f"'{expected_vendor}', runtime reported '{actual or '<unknown>'}'"
            )
    if expected_device:
        expected = str(expected_device).strip()
        if not expected or actual != expected:
            raise RuntimeError(
                "resize probe device mismatch: expected "
                f"'{expected_device}', runtime reported '{actual or '<unknown>'}'"
            )


def _telemetry(engine: Any) -> dict[str, Any]:
    getter = getattr(engine, "get_last_block_execution", None)
    if not callable(getter):
        return {}
    try:
        value = getter()
    except Exception:
        return {}
    return dict(value) if isinstance(value, Mapping) else {}


def _reset_telemetry(engine: Any) -> None:
    setter = getattr(engine, "set_last_block_execution", None)
    if callable(setter):
        try:
            setter({})
        except Exception:
            pass


def _plan(engine: Any) -> dict[str, Any]:
    local = getattr(engine, "_local", None)
    value = getattr(local, "last_block_plan", None)
    return dict(value) if isinstance(value, Mapping) else {}


def _set_full(aot: Any, engine: Any) -> None:
    # Disable both explicit and adaptive selection.  This is the full-frame
    # oracle on the selected backend, not an OpenCV or CPU substitute.
    aot.set_block_mode(
        enabled=False,
        threshold_bytes=1,
        adaptive_memory=False,
        cache_entries=1,
        device_cache_enabled=False,
    )
    engine.clear_block_quarantine("resize")
    _reset_telemetry(engine)


def _set_block(aot: Any, engine: Any, block_size: int) -> None:
    aot.set_block_mode(
        enabled=True,
        size=int(block_size),
        threshold_bytes=1,
        cache_entries=8,
        cache_bytes=16 * 1024 * 1024,
        adaptive_memory=False,
        device_cache_enabled=False,
    )
    engine.clear_block_quarantine("resize")
    _reset_telemetry(engine)


def _run_case(
    aot: Any,
    engine: Any,
    source: np.ndarray,
    dsize: tuple[int, int],
    interpolation_name: str,
    block_size: int,
) -> dict[str, Any]:
    interpolation = getattr(aot, INTERPOLATIONS[interpolation_name])
    _set_full(aot, engine)
    started = time.perf_counter()
    full = np.ascontiguousarray(aot.resize(source, dsize, interpolation=interpolation))
    full_seconds = time.perf_counter() - started
    full_plan = _plan(engine)
    full_telemetry = _telemetry(engine)

    _set_block(aot, engine, block_size)
    started = time.perf_counter()
    cold = np.ascontiguousarray(aot.resize(source, dsize, interpolation=interpolation))
    cold_seconds = time.perf_counter() - started
    cold_plan = _plan(engine)
    cold_telemetry = _telemetry(engine)
    cold_error = _max_abs_error(full, cold)

    # A second call exercises the existing exact output-tile cache.  It is
    # reported separately and is not allowed to hide a cold-path mismatch.
    started = time.perf_counter()
    warm = np.ascontiguousarray(aot.resize(source, dsize, interpolation=interpolation))
    warm_seconds = time.perf_counter() - started
    warm_plan = _plan(engine)
    warm_telemetry = _telemetry(engine)
    warm_error = _max_abs_error(full, warm)

    # The specialized path must own the dispatch.  Exact parity produced by a
    # full-frame fallback is useful diagnostic data but is not support evidence.
    cold_selected = bool(cold_plan.get("selected"))
    warm_selected = bool(warm_plan.get("selected"))
    cold_supported = bool(
        cold_selected
        and str(cold_telemetry.get("operation", "")) == "resize"
        and int(cold_telemetry.get("block_count", 0) or 0) > 1
    )
    warm_supported = bool(
        warm_selected
        and str(warm_telemetry.get("operation", "")) == "resize"
        and int(warm_telemetry.get("block_count", 0) or 0) > 1
    )
    return {
        "source_shape": list(source.shape),
        "target_dsize": [int(dsize[0]), int(dsize[1])],
        "target_shape": list(full.shape),
        "interpolation": interpolation_name,
        "block_size": int(block_size),
        "full_frame_seconds": float(full_seconds),
        "cold_block_seconds": float(cold_seconds),
        "warm_block_seconds": float(warm_seconds),
        "cold_max_abs_error": float(cold_error),
        "warm_max_abs_error": float(warm_error),
        "cold_block_selected": cold_selected,
        "warm_block_selected": warm_selected,
        "cold_native_supported": cold_supported,
        "warm_native_supported": warm_supported,
        "cold_passed": bool(cold_supported and cold_error <= 2.0e-5),
        "warm_passed": bool(warm_supported and warm_error <= 2.0e-5),
        "full_plan": _json_safe(full_plan),
        "cold_plan": _json_safe(cold_plan),
        "warm_plan": _json_safe(warm_plan),
        "full_telemetry": _json_safe(full_telemetry),
        "cold_telemetry": _json_safe(cold_telemetry),
        "warm_telemetry": _json_safe(warm_telemetry),
    }


def run(
    backend: str,
    device: int = 0,
    block_size: int = 7,
    interpolations: str | Iterable[str] | None = None,
    expected_vendor: str | None = None,
    expected_device: str | None = None,
) -> dict[str, Any]:
    selected = _parse_interpolations(interpolations)
    os.environ["BACKEND"] = str(backend)
    os.environ["AOT_ARCH"] = str(backend)
    os.environ["AOT_DEVICE"] = str(int(device))
    if str(backend).lower() == "vulkan":
        os.environ.setdefault("TARGET_VENDOR", "nvidia")

    # Import only after backend selection variables are set.
    from taichi_vision.taichi_algorithm import aot_api as aot
    from taichi_vision.taichi_aot import engine

    runtime_backend = str(getattr(engine, "arch", backend) or backend).strip().lower()
    if runtime_backend != str(backend).strip().lower():
        raise RuntimeError(
            "resize probe backend mismatch: requested "
            f"'{backend}', runtime reported '{runtime_backend or '<unknown>'}'"
        )
    runtime_device_name = str(
        getattr(engine, "gpu_name", "") or getattr(engine, "device_name", "")
    )
    if not runtime_device_name and runtime_backend == "cuda":
        runtime_device_name = _cuda_device_name(device)
    _validate_device_identity(
        runtime_device_name,
        expected_vendor=expected_vendor,
        expected_device=expected_device,
    )

    rng = np.random.default_rng(20260810)
    cases: list[dict[str, Any]] = []
    for source_shape, dsize in DEFAULT_CASES:
        source = rng.random(source_shape, dtype=np.float32)
        for interpolation in selected:
            try:
                cases.append(
                    _run_case(
                        aot,
                        engine,
                        source,
                        dsize,
                        interpolation,
                        int(block_size),
                    )
                )
            except Exception as exc:
                cases.append(
                    {
                        "source_shape": list(source_shape),
                        "target_dsize": list(dsize),
                        "interpolation": interpolation,
                        "block_size": int(block_size),
                        "cold_passed": False,
                        "warm_passed": False,
                        "error": str(exc)[:512],
                    }
                )

    return {
        "backend": runtime_backend,
        "device_id": int(getattr(engine, "device_id", device) or device),
        "device_name": runtime_device_name,
        "block_size": int(block_size),
        "interpolations": list(selected),
        "cases": cases,
        "all_cold_passed": bool(
            cases and all(item.get("cold_passed") for item in cases)
        ),
        "all_warm_passed": bool(
            cases and all(item.get("warm_passed") for item in cases)
        ),
        "native_case_count": int(
            sum(bool(item.get("cold_native_supported")) for item in cases)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    # OpenGL uses the process-wide Windows ICD context, just like the native
    # partition probe.  It is therefore a valid exact-backend diagnostic even
    # though its ordinal is not comparable with Vulkan/CUDA ordinals.
    parser.add_argument(
        "--backend", choices=("cpu", "vulkan", "opengl", "cuda"), required=True
    )
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--block-size", type=int, default=7)
    parser.add_argument(
        "--interpolations",
        default="linear,cubic,area",
        help="comma-separated subset of linear,cubic,area",
    )
    parser.add_argument(
        "--expected-vendor",
        default=None,
        help="fail closed unless runtime device name contains this vendor",
    )
    parser.add_argument(
        "--expected-device",
        default=None,
        help="fail closed unless runtime device name exactly matches this value",
    )
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()
    try:
        payload = run(
            args.backend,
            args.device,
            args.block_size,
            args.interpolations,
            args.expected_vendor,
            args.expected_device,
        )
    except ValueError as exc:
        parser.error(str(exc))
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    print(encoded)
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
