"""Large-frame bilateral-grid full versus compute-block parity probe."""

from __future__ import annotations

import argparse
import gc
import json
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
    parser.add_argument("--sizes", default="12,24")
    parser.add_argument("--block-size", type=int, default=512)
    parser.add_argument("--preset", default="medium")
    parser.add_argument("--channels", type=int, choices=(1, 3), default=1)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)

    from taichi_vision.taichi_algorithm import aot_api as api
    from taichi_vision.taichi_aot import engine

    results = []
    for size in (float(item) for item in args.sizes.split(",") if item.strip()):
        height, width = _shape_for_mp(size)
        rng = np.random.default_rng(20260815 + int(round(size * 100)))
        y = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None]
        x = np.linspace(0.0, 1.0, width, dtype=np.float32)[None, :]
        base = np.clip(
            0.5 * x + 0.35 * y + 0.15 * rng.random((height, width), dtype=np.float32),
            0.0,
            1.0,
        )
        if args.channels == 3:
            image = np.stack(
                (base, np.clip(base * 0.9 + 0.03, 0.0, 1.0), np.clip(base * 1.05, 0.0, 1.0)),
                axis=-1,
            ).astype(np.float32, copy=False)
        else:
            image = base

        engine.configure_blocks(
            enabled=False,
            size=int(args.block_size),
            threshold_bytes=1 << 60,
            adaptive_memory=True,
            cache_entries=1,
            device_cache_enabled=False,
        )
        started = time.perf_counter()
        full = np.asarray(api.bilateral_grid_filter(image, preset=args.preset, return_gpu=False))
        full_seconds = time.perf_counter() - started
        full_status = engine.get_memory_status(force=True)

        @api.compute_block(
            operation="bilateral_grid_filter",
            halo=0,
            mode="force",
            fallback="full_frame",
        )
        def run_block(raw):
            return api.bilateral_grid_filter(raw, preset=args.preset, return_gpu=False)

        started = time.perf_counter()
        blocked = np.asarray(run_block(image))
        block_seconds = time.perf_counter() - started
        block_status = engine.get_memory_status(force=True)
        finite = bool(np.isfinite(full).all() and np.isfinite(blocked).all())
        max_abs = float("inf")
        mean_abs = float("inf")
        if full.shape == blocked.shape and full.size:
            diff = np.abs(full.astype(np.float64) - blocked.astype(np.float64))
            max_abs = float(np.max(diff))
            mean_abs = float(np.mean(diff))

        results.append({
            "size_mp": size,
            "shape": [height, width],
            "full_seconds": full_seconds,
            "block_seconds": block_seconds,
            "full_shape": list(full.shape),
            "block_shape": list(blocked.shape),
            "finite": finite,
            "max_abs_error": max_abs,
            "mean_abs_error": mean_abs,
            "full_memory": {
                "resident_bytes": int(full_status.get("resident_bytes", 0)),
                "resident_limit": int(full_status.get("resident_limit", 0)),
                "resident_over_limit": bool(full_status.get("resident_over_limit", False)),
            },
            "block_memory": {
                "resident_bytes": int(block_status.get("resident_bytes", 0)),
                "resident_limit": int(block_status.get("resident_limit", 0)),
                "resident_over_limit": bool(block_status.get("resident_over_limit", False)),
            },
        })
        del full, blocked, image
        gc.collect()
        try:
            engine.buffer_pool.clear()
            engine.trim_staging_pool()
        except Exception:
            pass

    payload = {
        "backend": str(getattr(engine, "arch", "unknown")),
        "device": str(getattr(engine, "gpu_name", getattr(engine, "device_id", "unknown"))),
        "operation": "bilateral_grid_filter",
        "preset": str(args.preset),
        "channels": int(args.channels),
        "block_size": int(args.block_size),
        "results": results,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # This is an evidence probe, not a universal quality assertion.  A strict
    # parity threshold is intentionally not applied because bilateral-grid
    # normalization is global and tile boundaries may be semantically visible.
    return 0 if all(item["finite"] and item["full_shape"] == item["block_shape"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
