"""Measure demosaic latency phases and engine memory per method and frame size.

This is the authoritative latency/memory measurement for the demosaic family:
it splits a call into upload, dispatch, and readback, and records the engine's
resident/lifecycle telemetry.  The quality runner reports quality plus coarse
timing; this tool reports the phase breakdown that optimisation decisions need.

Full-frame is used deliberately, matching the quality runner: it is the
correctness oracle, and the block path has its own parity probe.

Example:
    python bench_demosaic_latency.py --backend cpu --methods hamilton \\
        --sizes 256 512 1024 --runs 5 --report latency.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_HARNESS_PATH = Path(__file__).resolve().parent / "demosaic_quality_harness.py"
_SPEC = importlib.util.spec_from_file_location("pixel_refine_latency_harness", _HARNESS_PATH)
if _SPEC is None or _SPEC.loader is None:  # pragma: no cover - repository invariant
    raise ImportError(f"cannot load harness: {_HARNESS_PATH}")
harness = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = harness
_SPEC.loader.exec_module(harness)

# ``cmatrix`` is a constant 3x3 for the benchmark; the point is the cost of the
# call, not the colour of the result.
SCALARS = (1.4, 1.0, 1.6, 1.02, np.eye(3, dtype=np.float32), 0.0, 1.0, 0, 1, 3, 2)


def configure_backend(backend: str) -> None:
    os.environ["PIXEL_REFINE_AOT_ARCH"] = backend
    os.environ["AOT_ARCH"] = backend


def status_provider(api):
    getter = getattr(api, "get_memory_status", None)
    if getter is None:
        return None

    def provider():
        return getter(force=True)

    return provider


def memory_snapshot(provider) -> dict:
    snapshot = {}
    if provider is None:
        return snapshot
    try:
        status = provider()
    except Exception as exc:  # pragma: no cover - platform dependent
        return {"engine_status_error": repr(exc)}
    for key in (
        "resident_bytes",
        "resident_limit",
        "resident_over_limit",
        "lifecycle_bytes",
        "allocation_count",
        "release_count",
    ):
        if isinstance(status, dict) and key in status:
            snapshot[key] = status[key]
    return snapshot


def measure(api, method: str, shape: tuple[int, int], runs: int) -> dict:
    height, width = shape
    rng = np.random.default_rng(20260923 + height * width)
    bayer = rng.random((height, width), dtype=np.float32)
    function = getattr(api, method)

    upload_ms = []
    dispatch_ms = []
    readback_ms = []
    end_to_end_ms = []
    output = None
    input_buffer = None
    try:
        for run in range(max(1, runs)):
            started = time.perf_counter()
            input_buffer = api.upload(bayer)
            uploaded = time.perf_counter()

            candidate = function(input_buffer, *SCALARS, return_gpu=True)
            dispatched = time.perf_counter()

            output = (
                candidate.to_numpy() if hasattr(candidate, "to_numpy") else np.asarray(candidate)
            )
            finished = time.perf_counter()

            if hasattr(candidate, "release"):
                candidate.release()
            if hasattr(input_buffer, "release"):
                input_buffer.release()
            input_buffer = None

            if run > 0:  # the first call also loads the module
                upload_ms.append((uploaded - started) * 1000.0)
                dispatch_ms.append((dispatched - uploaded) * 1000.0)
                readback_ms.append((finished - dispatched) * 1000.0)
                end_to_end_ms.append((finished - started) * 1000.0)
    finally:
        if input_buffer is not None and hasattr(input_buffer, "release"):
            input_buffer.release()

    def med(values):
        return float(np.median(values)) if values else float("nan")

    return {
        "shape": [height, width],
        "megapixels": round(height * width / 1e6, 4),
        "runs": max(1, runs),
        "upload_median_ms": med(upload_ms),
        "dispatch_median_ms": med(dispatch_ms),
        "readback_median_ms": med(readback_ms),
        "end_to_end_median_ms": med(end_to_end_ms),
        "output_shape": list(np.shape(output)),
        "output_dtype": str(np.asarray(output).dtype),
    }


def parse_shapes(values) -> list[tuple[int, int]]:
    """Accept ``WxH`` strings such as ``3840x2160`` alongside square sizes."""

    shapes = []
    for item in values:
        text = str(item).lower().replace(" ", "")
        if "x" in text:
            width, height = (int(part) for part in text.split("x", 1))
            shapes.append((height, width))
        else:
            side = int(text)
            shapes.append((side, side))
    return shapes


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--backend", default="cpu")
    parser.add_argument("--methods", nargs="+", default=["hamilton"])
    parser.add_argument(
        "--sizes",
        nargs="+",
        default=["256", "512", "1024"],
        help="square sizes, or WxH shapes such as 3840x2160",
    )
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args(argv)

    configure_backend(args.backend)
    import taichi_vision.taichi_aot as taichi_aot

    provider = status_provider(taichi_aot)
    before = memory_snapshot(provider)

    report = {
        "schema_version": 1,
        "backend": args.backend,
        "methods": {},
        "memory_before": before,
    }

    shapes = parse_shapes(args.sizes)
    for method in args.methods:
        entries = {}
        for shape in shapes:
            entry = measure(taichi_aot, method, shape, args.runs)
            entry["memory"] = memory_snapshot(provider)
            entries[f"{shape[1]}x{shape[0]}"] = entry
        report["methods"][method] = entries

    report["memory_after"] = memory_snapshot(provider)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.summary_only:
        for method, entries in report["methods"].items():
            print(f"\n=== {method}")
            for size, entry in entries.items():
                print(
                    f"  {size:>5} px  upload {entry['upload_median_ms']:7.3f}  "
                    f"dispatch {entry['dispatch_median_ms']:8.3f}  "
                    f"readback {entry['readback_median_ms']:7.3f}  "
                    f"e2e {entry['end_to_end_median_ms']:8.3f} ms"
                )
        print(f"\nmemory before: {report['memory_before']}")
        print(f"memory after:  {report['memory_after']}")
        return 0

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
