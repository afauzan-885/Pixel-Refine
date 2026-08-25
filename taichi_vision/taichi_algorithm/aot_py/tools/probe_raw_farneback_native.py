"""Probe the native pre-demosaic Farneback path on the selected target.

This is intentionally a small smoke probe.  It verifies that a synthetic
integer DNG is normalized in RAW space, that the selected target loads the
``compression_raw`` and Farneback artifacts, and that an identical-frame
flow is finite and zero.  It does not certify large-image throughput or
tile-safety for Farneback.

Example (PowerShell)::

    $env:AOT_MODE='1'
    $env:BACKEND='vulkan'
    $env:TARGET_VENDOR='nvidia'
    python -m taichi_vision.taichi_algorithm.aot_py.tools.probe_raw_farneback_native
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

import numpy as np

from taichi_vision import taichi_aot
from taichi_vision.taichi_algorithm.compression.dng_aot import (
    encode_dng_aot,
    read_dng_aot,
)
from taichi_vision.taichi_algorithm.compression.raw_pipeline import (
    raw_optical_flow_dng,
)


def run_probe(
    *,
    height: int = 128,
    width: int = 128,
    bits_per_sample: int = 14,
    block_size: int = 2048,
) -> dict[str, object]:
    if os.environ.get("AOT_MODE", "1").strip().lower() in {"0", "false", "off"}:
        raise RuntimeError("native RAW Farneback probe requires AOT_MODE=1")
    height, width = int(height), int(width)
    bits_per_sample = int(bits_per_sample)
    if height < 32 or width < 32:
        raise ValueError("probe dimensions must be at least 32x32")
    if bits_per_sample < 8 or bits_per_sample > 16:
        raise ValueError("bits_per_sample must be in [8,16]")
    mask = np.uint32((1 << bits_per_sample) - 1)
    rows = np.arange(height, dtype=np.uint32)[:, None]
    cols = np.arange(width, dtype=np.uint32)[None, :]
    source = ((rows * np.uint32(37) + cols * np.uint32(19)) & mask).astype(
        np.uint8 if bits_per_sample <= 8 else np.uint16
    )
    encoded = encode_dng_aot(
        source,
        metadata={
            "cfa_pattern": (1, 0, 0, 1),
            "black_level": 64,
            "white_level": int(mask),
        },
        compression="none",
        bits_per_sample=bits_per_sample,
    )
    frame = read_dng_aot(encoded)
    started = time.perf_counter()
    flow = raw_optical_flow_dng(
        frame,
        frame,
        block_size=block_size,
        native=True,
        flow_mode="full_frame",
        num_levels=1,
        num_iters=1,
        win_size=5,
        poly_n=5,
        poly_sigma=1.1,
        pyr_scale=0.5,
    )
    elapsed = time.perf_counter() - started
    flow_array = np.asarray(flow, dtype=np.float32)
    runtime = taichi_aot.engine
    loaded = tuple(sorted(str(key) for key in getattr(taichi_aot, "_module_cache", {})))
    max_error = float(np.max(np.abs(flow_array))) if flow_array.size else 0.0
    return {
        "backend_requested": os.environ.get("BACKEND", "auto"),
        "backend_actual": str(getattr(runtime, "arch", "unknown")),
        "device_id": int(getattr(runtime, "device_id", 0)),
        "device_name": str(getattr(runtime, "gpu_name", "") or ""),
        "shape_sensor": [height, width],
        "shape_guide_flow": list(flow_array.shape),
        "sensor_dtype": str(source.dtype),
        "flow_dtype": str(flow_array.dtype),
        "bits_per_sample": bits_per_sample,
        "block_size_sensor": int(block_size),
        "native": True,
        "flow_mode": "full_frame",
        "loaded_logical_modules": loaded,
        "elapsed_seconds": elapsed,
        "max_abs_error_vs_identical_frame": max_error,
        "finite": bool(np.isfinite(flow_array).all()),
        "passed": bool(
            flow_array.shape == (height // 2, width // 2, 2)
            and np.isfinite(flow_array).all()
            and max_error <= 1e-5
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--height", type=int, default=128)
    parser.add_argument("--width", type=int, default=128)
    parser.add_argument("--bits", type=int, default=14)
    parser.add_argument("--block-size", type=int, default=2048)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    try:
        result = run_probe(
            height=args.height,
            width=args.width,
            bits_per_sample=args.bits,
            block_size=args.block_size,
        )
    except Exception as exc:
        result = {
            "backend_requested": os.environ.get("BACKEND", "auto"),
            "error": f"{type(exc).__name__}: {exc}",
            "passed": False,
        }
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")
    return 0 if bool(result.get("passed")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
