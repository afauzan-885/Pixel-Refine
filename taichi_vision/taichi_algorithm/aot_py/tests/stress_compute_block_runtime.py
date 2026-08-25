"""Synthetic compute-block benchmark and correctness gate.

This benchmark deliberately uses the backend-neutral generic executor instead
of a native bridge.  It is therefore safe to run on a build machine without a
GPU, while still exercising the same cache, tile reader, halo and merge
machinery used by AOT algorithms.  Native backend parity is a separate gate;
this script must never be interpreted as proof that a Vulkan/OpenGL/CUDA graph
loaded successfully.

Examples (PowerShell)::

    python stress_compute_block_runtime.py --sizes 12 --iterations 2
    python stress_compute_block_runtime.py --sizes 12,24,50,100 --iterations 4 --json report.json

The reported ``max_abs_error`` is measured against the full-frame NumPy
reference.  ``rss_delta_mb`` is process RSS (when psutil is available), not a
device-VRAM measurement.  Native runs should attach their own engine memory
telemetry to the resulting JSON.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[4]


def _load_runtime_modules():
    """Load block/generic modules without importing the native engine."""

    package_name = "pixel_refine_compute_block_benchmark"
    package = __import__("types").ModuleType(package_name)
    package.__path__ = [str(ROOT / "taichi_vision" / "taichi_aot")]
    sys.modules[package_name] = package

    def load(name: str, path: Path):
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    block = load(f"{package_name}.block", ROOT / "taichi_vision" / "taichi_aot" / "block.py")
    generic = load(
        f"{package_name}.generic_block",
        ROOT / "taichi_vision" / "taichi_aot" / "generic_block.py",
    )
    return block, generic


BLOCK, GENERIC = _load_runtime_modules()


class FakeRuntime:
    """Small deterministic runtime implementing the generic executor contract."""

    def __init__(self, block_size: int = 512):
        self.block_size = int(block_size)
        self.cache = BLOCK.BlockCache(max_entries=4096, max_bytes=512 * 1024 * 1024)
        self.quarantine: dict[str, str] = {}
        self.arch = "synthetic"
        self.target_id = "synthetic"
        self.gpu_name = "synthetic"
        self._generation = 0

    def get_block_cache(self):
        return self.cache

    def get_device_block_cache(self):
        return self.cache

    def restore_resident_block(self, *_args):
        return None

    def put_block_record(self, record):
        return self.cache.put(record)

    def quarantine_block_operation(self, operation, reason):
        self.quarantine[str(operation)] = str(reason)

    def plan_generic_blocks(self, operation, shape, nbytes, **kwargs):
        mode = str(kwargs.get("mode", "auto")).lower()
        if mode == "off":
            return None
        if mode == "auto" and int(nbytes) < int(kwargs.get("threshold_bytes") or 0):
            return None
        return BLOCK.BlockGrid(
            shape,
            size=kwargs.get("block_size") or self.block_size,
            halo=int(kwargs.get("halo", 0)),
        )


def _rss_mb() -> float | None:
    try:
        import psutil  # type: ignore

        return float(psutil.Process(os.getpid()).memory_info().rss) / (1024 * 1024)
    except Exception:
        return None


def _full_stencil(array: np.ndarray) -> np.ndarray:
    padded = np.pad(array, 1, mode="edge")
    return (
        padded[:-2, :-2]
        + padded[:-2, 1:-1]
        + padded[:-2, 2:]
        + padded[1:-1, :-2]
        + padded[1:-1, 1:-1]
        + padded[1:-1, 2:]
        + padded[2:, :-2]
        + padded[2:, 1:-1]
        + padded[2:, 2:]
    ) / np.float32(9.0)


def _block_stencil(ctx):
    return _full_stencil(ctx.inputs[0])


def _run_case(shape: tuple[int, int], iterations: int, block_size: int) -> dict[str, Any]:
    # A deterministic low-amplitude signal prevents the benchmark from
    # accidentally measuring an all-zero fast path while keeping the expected
    # result numerically stable for float32.
    height, width = shape
    source = (
        np.arange(height * width, dtype=np.float32).reshape(shape) % np.float32(251)
    ) / np.float32(251.0)
    runtime = FakeRuntime(block_size)
    executor = GENERIC.GenericBlockExecutor(runtime)

    operations = (
        ("copy_add", 0, lambda array: array * np.float32(1.25) + np.float32(0.5),
         lambda ctx: ctx.inputs[0] * np.float32(1.25) + np.float32(0.5)),
        ("stencil3x3", 1, _full_stencil, _block_stencil),
    )
    rows: list[dict[str, Any]] = []
    for name, halo, reference_fn, tile_fn in operations:
        reference = reference_fn(source)
        full_spec = GENERIC.BlockComputeSpec(
            name,
            tile_fn,
            output_shape=shape,
            output_dtype=np.float32,
            mode="off",
            cache=False,
            fallback="full_frame",
            full_frame=lambda arrays, fn=reference_fn: fn(arrays[0]),
        )
        block_spec = GENERIC.BlockComputeSpec(
            name,
            tile_fn,
            output_shape=shape,
            output_dtype=np.float32,
            block_size=block_size,
            halo=halo,
            mode="force",
            cache=True,
            fallback="error",
        )

        rss_before = _rss_mb()
        t0 = time.perf_counter()
        full = None
        for _ in range(max(1, iterations)):
            full = executor.run((source,), full_spec)
        full_seconds = time.perf_counter() - t0
        rss_after_full = _rss_mb()

        runtime.cache.clear()
        t0 = time.perf_counter()
        cold = None
        cold_report = None
        for iteration in range(max(1, iterations)):
            current = executor.run((source,), block_spec, return_report=True)
            if cold_report is None:
                cold_report = current
            cold = current.value
        block_seconds = time.perf_counter() - t0
        rss_after_block = _rss_mb()
        warm_t0 = time.perf_counter()
        warm = executor.run((source,), block_spec, return_report=True)
        warm_seconds = time.perf_counter() - warm_t0

        error = float(np.max(np.abs(np.asarray(cold) - np.asarray(reference))))
        full_error = float(np.max(np.abs(np.asarray(full) - np.asarray(reference))))
        rows.append({
            "operation": name,
            "shape": list(shape),
            "pixels": int(height * width),
            "block_size": int(block_size),
            "iterations": int(max(1, iterations)),
            "full_seconds": full_seconds,
            "block_seconds": block_seconds,
            "warm_block_seconds": warm_seconds,
            "full_throughput_mpix_s": (height * width * max(1, iterations) / 1e6) / max(full_seconds, 1e-12),
            "block_throughput_mpix_s": (height * width * max(1, iterations) / 1e6) / max(block_seconds, 1e-12),
            "warm_cache_hit_rate": float(warm.report.cache_hits / max(1, warm.report.block_count)),
            "block_count": int(warm.report.block_count),
            "computed_cold": int(getattr(cold_report.report, "computed", 0)),
            "bytes_copied": int(getattr(cold_report.report, "bytes_copied", 0) or 0),
            "cache_copy_bytes": int(getattr(cold_report.report, "cache_copy_bytes", 0) or 0),
            "checksum_seconds": float(getattr(cold_report.report, "checksum_seconds", 0.0) or 0.0),
            "reader_seconds": float(getattr(cold_report.report, "reader_seconds", 0.0) or 0.0),
            "dispatch_seconds": float(getattr(cold_report.report, "dispatch_seconds", 0.0) or 0.0),
            "merge_seconds": float(getattr(cold_report.report, "merge_seconds", 0.0) or 0.0),
            "output_bytes": int(getattr(cold_report.report, "output_bytes", 0) or 0),
            "max_abs_error": error,
            "full_reference_error": full_error,
            "rss_delta_mb": None if rss_before is None or rss_after_block is None else rss_after_block - rss_before,
            "rss_full_delta_mb": None if rss_before is None or rss_after_full is None else rss_after_full - rss_before,
        })
    return {"shape": list(shape), "operations": rows}


def _parse_sizes(value: str) -> list[tuple[int, int, str]]:
    presets = {
        "12": (3000, 4000, "12mp"),
        "24": (4000, 6000, "24mp"),
        "50": (5000, 10000, "50mp"),
        # A Hasselblad-class pressure case.  Keep the dimensions explicit so
        # the benchmark remains deterministic instead of silently rounding a
        # requested megapixel count.  The source is float32 (400 MB) and the
        # executor's resident/cache limits still provide the memory gate.
        "100": (8000, 12500, "100mp"),
    }
    result = []
    for item in str(value).split(","):
        item = item.strip().lower()
        if item in presets:
            result.append(presets[item])
            continue
        h, w = item.lower().split("x", 1)
        result.append((int(h), int(w), item))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", default="12", help="12,24,50,100 or explicit HxW values")
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--block-size", type=int, default=512)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()
    report = {
        "kind": "synthetic_compute_block_benchmark",
        "backend": "synthetic_cpu_reference",
        "sizes": [],
    }
    for height, width, label in _parse_sizes(args.sizes):
        print(f"[compute_block] {label}: {height}x{width}, block={args.block_size}")
        case = _run_case((height, width), max(1, args.iterations), args.block_size)
        case["label"] = label
        report["sizes"].append(case)
        for row in case["operations"]:
            print(
                f"  {row['operation']}: error={row['max_abs_error']:.3g}, "
                f"full={row['full_seconds']:.3f}s, block={row['block_seconds']:.3f}s, "
                f"warm-hit={row['warm_cache_hit_rate']:.1%}"
            )
    encoded = json.dumps(report, indent=2)
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")
        print(f"[compute_block] wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
