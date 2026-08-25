"""Native full-frame versus block parity harness for low-risk AOT operations.

The process backend must be selected before importing the AOT facade.  This
script intentionally exercises the public wrappers twice: once with the
adaptive/block planner disabled (full-frame baseline), then with a small
explicit block and a one-byte threshold.  It reports backend/device, timing,
per-operation error, and an optional RSS delta.  A successful run qualifies
only the exact backend/device named in the output; it is not a universal
driver claim.

Examples
--------
    $env:BACKEND = "cpu"
    python stress_block_native_parity.py --sizes 0.1 --operations copy,otsu

    $env:BACKEND = "vulkan"
    $env:VULKAN_VENDOR = "nvidia"
    python stress_block_native_parity.py --sizes 12 --operations low_risk,otsu
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


LOW_RISK = (
    "copy",
    "absdiff",
    "rgb2gray",
    "split_3ch",
    "merge_3ch",
    "extract_channel",
    "insert_channel",
    "cvtColor",
)


def _shape_for_mp(value: float) -> tuple[int, int]:
    pixels = max(1, int(float(value) * 1_000_000.0))
    height = max(8, int((pixels * 3.0 / 4.0) ** 0.5))
    width = max(8, int(pixels / height))
    return height, width


def _rss_bytes() -> int | None:
    try:
        import psutil  # type: ignore

        return int(psutil.Process().memory_info().rss)
    except Exception:
        return None


def _max_error(left: Any, right: Any) -> float:
    if isinstance(left, (list, tuple)) or isinstance(right, (list, tuple)):
        if not isinstance(left, (list, tuple)) or not isinstance(right, (list, tuple)):
            return float("inf")
        if len(left) != len(right):
            return float("inf")
        return max(
            (_max_error(a, b) for a, b in zip(left, right)),
            default=0.0,
        )
    left_array = np.asarray(left)
    right_array = np.asarray(right)
    if left_array.shape != right_array.shape:
        return float("inf")
    if left_array.size == 0:
        return 0.0
    return float(
        np.max(
            np.abs(
                left_array.astype(np.float64, copy=False)
                - right_array.astype(np.float64, copy=False)
            )
        )
    )


def _call_operation(api, name: str, image: np.ndarray, second: np.ndarray):
    if name == "copy":
        return api.copy(image)
    if name == "absdiff":
        return api.absdiff(image, second)
    if name == "rgb2gray":
        return api.rgb2gray(image)
    if name == "split_3ch":
        return api.split_3ch(image)
    if name == "merge_3ch":
        return api.merge_3ch(image[..., 0], image[..., 1], image[..., 2])
    if name == "extract_channel":
        return api.extract_channel(image, 1)
    if name == "insert_channel":
        return api.insert_channel(image[..., 1], image, 1)
    if name == "cvtColor":
        return api.cvtColor(image, 7)
    if name == "otsu_threshold":
        return api.otsu_threshold_aot(image[..., 0] * 255.0, max_val=255.0)
    raise ValueError(f"unsupported parity operation: {name}")


def _normalize_operations(values: Iterable[str]) -> tuple[str, ...]:
    selected: list[str] = []
    for value in values:
        name = str(value).strip().lower()
        if name == "low_risk":
            selected.extend(LOW_RISK)
        elif name in {"otsu", "otsu_threshold_aot"}:
            selected.append("otsu_threshold")
        elif name:
            selected.append(name)
    return tuple(dict.fromkeys(selected))


def run_case(api, engine, size_mp: float, block_size: int, operations: tuple[str, ...]):
    shape = _shape_for_mp(size_mp)
    rng = np.random.default_rng(20260810 + int(round(size_mp * 100)))
    image = rng.random((*shape, 3), dtype=np.float32)
    second = np.roll(image, 1, axis=1)

    engine.configure_blocks(enabled=False, adaptive_memory=False)
    full: dict[str, Any] = {}
    full_seconds: dict[str, float] = {}
    for name in operations:
        started = time.perf_counter()
        full[name] = _call_operation(api, name, image, second)
        full_seconds[name] = time.perf_counter() - started

    try:
        engine.get_block_cache().clear()
        engine.clear_block_quarantine()
    except Exception:
        pass
    engine.configure_blocks(
        enabled=True,
        size=int(block_size),
        threshold_bytes=1,
        adaptive_memory=False,
        cache_entries=1,
        device_cache_enabled=False,
    )
    before_rss = _rss_bytes()
    block: dict[str, Any] = {}
    block_seconds: dict[str, float] = {}
    for name in operations:
        started = time.perf_counter()
        block[name] = _call_operation(api, name, image, second)
        block_seconds[name] = time.perf_counter() - started

    errors = {name: _max_error(full[name], block[name]) for name in operations}
    after_rss = _rss_bytes()
    return {
        "size_mp": float(size_mp),
        "shape": list(shape),
        "block_size": int(block_size),
        "operations": list(operations),
        "max_abs_error": errors,
        "full_frame_seconds": full_seconds,
        "block_seconds": block_seconds,
        "rss_delta_bytes": (
            None if before_rss is None or after_rss is None else after_rss - before_rss
        ),
        "passed": all(
            np.isfinite(value) and value <= 1.0e-5 for value in errors.values()
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sizes",
        default="0.1",
        help="comma-separated megapixel presets, e.g. 0.1,12,24,50,100",
    )
    parser.add_argument("--block-size", type=int, default=512)
    parser.add_argument(
        "--operations",
        default="low_risk,otsu",
        help="comma-separated names, `low_risk`, or `otsu`",
    )
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)

    # Import only after the caller has selected the backend environment.
    from taichi_vision.taichi_algorithm import aot_api as api
    from taichi_vision.taichi_aot import engine

    operations = _normalize_operations(args.operations.split(","))
    sizes = tuple(float(value) for value in args.sizes.split(",") if value.strip())
    results = [
        run_case(api, engine, size, args.block_size, operations) for size in sizes
    ]
    payload = {
        "backend": str(getattr(engine, "arch", "unknown")),
        "device": str(
            getattr(engine, "gpu_name", getattr(engine, "device_id", "unknown"))
        ),
        "vendor_hint": os.environ.get("VULKAN_VENDOR"),
        "results": results,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return 0 if all(item["passed"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
