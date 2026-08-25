"""Native block-only residency probe for large images.

Unlike ``stress_block_native_parity.py`` this probe deliberately does not
allocate a full-frame reference.  It is used to qualify the bounded path on
small-VRAM devices where a full-frame staging allocation would be an invalid
comparison rather than a useful parity result.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _shape_for_mp(value: float) -> tuple[int, int]:
    pixels = max(1, int(float(value) * 1_000_000.0))
    height = max(8, int((pixels * 3.0 / 4.0) ** 0.5))
    width = max(8, int(pixels / height))
    return height, width


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", default="12,24,50")
    parser.add_argument("--block-size", type=int, default=512)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)

    from taichi_vision.taichi_algorithm import aot_api as api
    from taichi_vision.taichi_aot import engine

    engine.configure_blocks(
        enabled=True,
        size=int(args.block_size),
        threshold_bytes=1,
        adaptive_memory=True,
        cache_entries=1,
        device_cache_enabled=False,
    )
    results = []
    for value in (float(item) for item in args.sizes.split(",") if item.strip()):
        shape = _shape_for_mp(value)
        rng = np.random.default_rng(20260815 + int(round(value * 100)))
        image = rng.random((*shape, 3), dtype=np.float32)
        iteration_reports = []
        for iteration in range(max(1, int(args.iterations))):
            started = time.perf_counter()
            copied = np.asarray(api.copy(image))
            gray = np.asarray(api.rgb2gray(image))
            elapsed = time.perf_counter() - started
            status = engine.get_memory_status(force=True)
            finite = bool(np.isfinite(copied).all() and np.isfinite(gray).all())
            iteration_reports.append({
                "iteration": iteration + 1,
                "seconds": elapsed,
                "finite": finite,
                "resident_bytes": int(status.get("resident_bytes", 0)),
                "resident_limit": int(status.get("resident_limit", 0)),
                "resident_over_limit": bool(status.get("resident_over_limit", False)),
                "lifecycle_bytes": int(status.get("lifecycle_bytes", 0)),
            })
            del copied, gray
            gc.collect()
            try:
                engine.buffer_pool.clear()
                engine.trim_staging_pool()
            except Exception:
                pass
        final_status = engine.get_memory_status(force=True)
        results.append({
            "size_mp": value,
            "shape": list(shape),
            "block_size": int(args.block_size),
            "iterations": iteration_reports,
            "copy_shape": [shape[0], shape[1], 3],
            "gray_shape": list(shape),
            "finite": all(item["finite"] for item in iteration_reports),
            "memory_status_after_trim": final_status,
        })
        del image
        gc.collect()
        try:
            engine.buffer_pool.clear()
            engine.trim_staging_pool()
        except Exception:
            pass

    payload = {
        "backend": str(getattr(engine, "arch", "unknown")),
        "device": str(getattr(engine, "gpu_name", getattr(engine, "device_id", "unknown"))),
        "block_only": True,
        "results": results,
        "result": "All block-only outputs were finite; no full-frame reference was allocated.",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if all(item["finite"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
