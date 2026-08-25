"""Native AOT RAW normalization/weight/fusion stress harness.

This is deliberately separate from ``stress_raw_pipeline.py``: that script
is a dependency-free semantic oracle, while this harness requires a selected
runtime and target-qualified ``compression_raw`` artifact.  It streams
memmap-backed Bayer frames through fixed-size tiles and reports accuracy,
throughput, RSS, and native dispatch counts.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from taichi_vision.taichi_algorithm.compression.raw_frame import RawMosaicFrame
from taichi_vision.taichi_algorithm.compression.raw_pipeline import (
    fuse_raw_pair_native,
    raw_normalize_headroom_native,
    raw_weight_map_native,
)


PRESETS = {
    "12": (3000, 4000),
    "24": (4000, 6000),
    "50": (5000, 10000),
    "100": (10000, 10000),
}


def _rss_bytes() -> int:
    try:
        import psutil

        return int(psutil.Process().memory_info().rss)
    except Exception:
        return 0


def _fill_sensor(path: Path, shape: tuple[int, int], seed: int) -> np.memmap:
    array = np.memmap(path, mode="w+", dtype=np.uint16, shape=shape)
    height, width = shape
    yy = np.arange(height, dtype=np.uint32)[:, None]
    xx = np.arange(width, dtype=np.uint32)[None, :]
    # A deterministic 14-bit sensor pattern with a mild exposure offset.
    array[:] = ((yy * 37 + xx * 19 + seed * 101) & 0x3FFF).astype(np.uint16)
    array.flush()
    return array


def run_case(label: str, shape: tuple[int, int], block_size: int) -> dict:
    started = time.perf_counter()
    rss_before = _rss_bytes()
    with tempfile.TemporaryDirectory(prefix=f"raw_native_{label}_") as temp:
        root = Path(temp)
        first = _fill_sensor(root / "first.u16", shape, 1)
        second = _fill_sensor(root / "second.u16", shape, 7)
        frame_a = RawMosaicFrame.from_samples(
            first,
            bits_per_sample=14,
            black_level=(128, 128, 128, 128),
            white_level=(16384, 16384, 16384, 16384),
            cfa_pattern=(1, 0, 0, 1),
            source_id=f"native-{label}-a",
            source_version="stress-v1",
        )
        frame_b = RawMosaicFrame.from_samples(
            second,
            bits_per_sample=14,
            black_level=(128, 128, 128, 128),
            white_level=(16384, 16384, 16384, 16384),
            cfa_pattern=(1, 0, 0, 1),
            source_id=f"native-{label}-b",
            source_version="stress-v1",
        )
        output_path = root / "fused.f32"
        output = np.memmap(output_path, mode="w+", dtype=np.float32, shape=shape)
        blocks = 0
        max_error = 0.0
        max_normalize_error = 0.0
        max_weight_error = 0.0
        max_fuse_error = 0.0
        height, width = shape
        for y0 in range(0, height, block_size):
            y1 = min(height, y0 + block_size)
            for x0 in range(0, width, block_size):
                x1 = min(width, x0 + block_size)
                normalized_a = raw_normalize_headroom_native(
                    frame_a, y0=y0, y1=y1, x0=x0, x1=x1
                )
                normalized_b = raw_normalize_headroom_native(
                    frame_b, y0=y0, y1=y1, x0=x0, x1=x1
                )
                # Compare every native stage with an independent oracle that
                # starts from the original uint16 sensor codes.  Do not call
                # RawMosaicFrame.normalized_headroom_region() here: reusing
                # the semantic implementation could hide a shared bug.
                raw_a = np.asarray(first[y0:y1, x0:x1], dtype=np.float32)
                raw_b = np.asarray(second[y0:y1, x0:x1], dtype=np.float32)
                reference_a = np.maximum(raw_a - np.float32(128.0), 0.0) / np.float32(
                    16384.0 - 128.0
                )
                reference_b = np.maximum(raw_b - np.float32(128.0), 0.0) / np.float32(
                    16384.0 - 128.0
                )
                max_normalize_error = max(
                    max_normalize_error,
                    float(np.max(np.abs(normalized_a - reference_a))),
                    float(np.max(np.abs(normalized_b - reference_b))),
                )
                local_weight = raw_weight_map_native(normalized_a, normalized_b)
                reference_weight = 1.0 / (1.0 + np.abs(reference_b - reference_a))
                max_weight_error = max(
                    max_weight_error,
                    float(np.max(np.abs(local_weight - reference_weight))),
                )
                fused = fuse_raw_pair_native(
                    normalized_a,
                    normalized_b,
                    local_weight,
                    reference_weight=1.0,
                    current_weight=1.0,
                )
                # The independent known-value oracle uses the reference
                # stages, not the native intermediates.
                expected = (reference_a + reference_b * reference_weight) / (
                    1.0 + reference_weight
                )
                tile_error = float(np.max(np.abs(fused - expected)))
                max_fuse_error = max(max_fuse_error, tile_error)
                max_error = max(max_error, tile_error)
                output[y0:y1, x0:x1] = fused
                blocks += 1
        output.flush()
        output_min = float(np.min(output))
        output_max = float(np.max(output))
        output_nbytes = int(output.nbytes)
        del output
        del first, second, frame_a, frame_b
        gc.collect()
    elapsed = time.perf_counter() - started
    rss_after = _rss_bytes()
    megapixels = (shape[0] * shape[1]) / 1_000_000.0
    return {
        "label": label,
        "shape": shape,
        "megapixels": megapixels,
        "block_size": block_size,
        "blocks": blocks,
        "elapsed_seconds": elapsed,
        "megapixels_per_second": megapixels / max(elapsed, 1e-12),
        "rss_before_bytes": rss_before,
        "rss_after_bytes": rss_after,
        "rss_delta_bytes": rss_after - rss_before,
        "output_bytes": output_nbytes,
        "output_min": output_min,
        "output_max": output_max,
        "max_error": max_error,
        "max_normalize_error": max_normalize_error,
        "max_weight_error": max_weight_error,
        "max_fuse_error": max_fuse_error,
        "passed": bool(
            max_normalize_error <= 2.0e-5
            and max_weight_error <= 2.0e-5
            and max_fuse_error <= 2.0e-5
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", default="12,24,50,100")
    parser.add_argument("--block-size", type=int, default=2048)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    if args.block_size <= 0:
        raise SystemExit("--block-size must be positive")
    results = [
        run_case(label, PRESETS[label], args.block_size)
        for label in (item.strip() for item in args.sizes.split(","))
        if label in PRESETS
    ]
    payload = {"backend": os.environ.get("BACKEND", "auto"), "results": results}
    print(json.dumps(payload, indent=2))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
