"""Large-frame DCB full-frame versus compute-block parity probe."""

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


def _status(engine):
    try:
        value = engine.get_memory_status(force=True)
    except Exception as exc:  # pragma: no cover - diagnostic only
        return {"status_error": repr(exc)}
    return {
        "resident_bytes": int(value.get("resident_bytes", 0)),
        "resident_limit": int(value.get("resident_limit", 0)),
        "resident_over_limit": bool(value.get("resident_over_limit", False)),
        "lifecycle_bytes": int(value.get("lifecycle_bytes", 0)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", default="12,24")
    parser.add_argument("--block-size", type=int, default=512)
    parser.add_argument("--method", default="dcb")
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)

    from taichi_vision.taichi_algorithm import aot_api as api
    from taichi_vision.taichi_aot import engine

    method = str(args.method).strip().lower()
    if method not in {"dcb", "hamilton", "bilinear"}:
        raise SystemExit("Supported methods: dcb, hamilton, bilinear")

    cmatrix = np.eye(3, dtype=np.float32)
    results = []
    for size in (float(item) for item in args.sizes.split(",") if item.strip()):
        height, width = _shape_for_mp(size)
        rng = np.random.default_rng(20260815 + int(round(size * 100)))
        bayer = rng.random((height, width), dtype=np.float32)
        kwargs = dict(
            wb_r=1.0,
            wb_g1=1.0,
            wb_b=1.0,
            wb_g2=1.0,
            cmatrix=cmatrix,
            black_level=0.0,
            white_level=1.0,
            c00=0,
            c01=1,
            c10=1,
            c11=2,
            method=method,
            return_gpu=False,
        )

        engine.configure_blocks(
            enabled=False,
            size=int(args.block_size),
            threshold_bytes=1 << 60,
            adaptive_memory=True,
            cache_entries=1,
            device_cache_enabled=False,
        )
        full_started = time.perf_counter()
        full = np.asarray(api.demosaic(bayer, **kwargs))
        full_seconds = time.perf_counter() - full_started
        full_status = _status(engine)
        full_finite = bool(np.isfinite(full).all())

        @api.compute_block(halo=16, mode="force")
        def run_block(raw):
            return api.demosaic(raw, **kwargs)

        block_started = time.perf_counter()
        blocked = np.asarray(run_block(bayer))
        block_seconds = time.perf_counter() - block_started
        block_status = _status(engine)
        block_finite = bool(np.isfinite(blocked).all())
        max_abs = float("inf")
        if full.shape == blocked.shape and full.size:
            max_abs = float(np.max(np.abs(full.astype(np.float64) - blocked.astype(np.float64))))

        results.append({
            "size_mp": size,
            "shape": [height, width],
            "full_seconds": full_seconds,
            "block_seconds": block_seconds,
            "full_shape": list(full.shape),
            "block_shape": list(blocked.shape),
            "full_finite": full_finite,
            "block_finite": block_finite,
            "max_abs_error": max_abs,
            "full_memory": full_status,
            "block_memory": block_status,
        })
        del full, blocked, bayer
        gc.collect()
        try:
            engine.buffer_pool.clear()
            engine.trim_staging_pool()
        except Exception:
            pass

    payload = {
        "backend": str(getattr(engine, "arch", "unknown")),
        "device": str(getattr(engine, "gpu_name", getattr(engine, "device_id", "unknown"))),
        "method": method,
        "block_size": int(args.block_size),
        "results": results,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    passed = all(
        item["full_finite"]
        and item["block_finite"]
        and item["full_shape"] == item["block_shape"]
        and item["max_abs_error"] <= 1e-5
        and not item["block_memory"].get("resident_over_limit", False)
        for item in results
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
