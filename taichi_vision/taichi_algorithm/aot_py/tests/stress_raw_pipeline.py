"""Synthetic pre-demosaic RAW stress test.

The script deliberately uses a deterministic Bayer code oracle and a streamed
block fusion path.  It does not claim native GPU support; use it to qualify
the semantic RAW contract and memory behavior before attaching AOT kernels.
"""

from __future__ import annotations

import argparse
import json
import math
import tempfile
import time
from pathlib import Path

import numpy as np


def _load_modules():
    # Importing taichi_vision.taichi_algorithm normally constructs the AOT
    # engine.  This benchmark is intentionally a pure semantic oracle, so it
    # loads only the compression modules and their relative dependencies.
    import importlib.util
    import sys
    import types

    root = Path(__file__).resolve().parents[2] / "compression"
    base = "_pixel_refine_raw_stress"
    package = types.ModuleType(base)
    package.__path__ = [str(root.resolve())]
    sys.modules[base] = package
    subpackage = types.ModuleType(f"{base}.compression")
    subpackage.__path__ = [str(root.resolve())]
    sys.modules[f"{base}.compression"] = subpackage
    loaded = {}
    for name in ("bitstream", "png_aot", "raw_frame", "raw_pipeline"):
        qualified = f"{base}.compression.{name}"
        spec = importlib.util.spec_from_file_location(qualified, root / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[qualified] = module
        spec.loader.exec_module(module)
        loaded[name] = module
    return loaded["raw_frame"].RawMosaicFrame, loaded["raw_pipeline"]


RawMosaicFrame, raw_pipeline = _load_modules()


SHAPES = {
    12: (3000, 4000),
    24: (4000, 6000),
    50: (5000, 10000),
    100: (10000, 10000),
}


def _shape_for_mp(mp: int) -> tuple[int, int]:
    if mp in SHAPES:
        return SHAPES[mp]
    width = int(math.ceil(math.sqrt(float(mp) * 1_000_000.0 * 4.0 / 3.0)))
    height = int(math.ceil(float(mp) * 1_000_000.0 / width))
    return height, width


def _fill_sensor(path: Path, shape: tuple[int, int], *, offset: int) -> np.memmap:
    height, width = shape
    array = np.memmap(path, mode="w+", dtype=np.uint16, shape=shape)
    columns = np.arange(width, dtype=np.uint32)[None, :]
    for y0 in range(0, height, 256):
        y1 = min(height, y0 + 256)
        rows = np.arange(y0, y1, dtype=np.uint32)[:, None]
        values = (rows * 17 + columns * 29 + np.uint32(offset)) % np.uint32(14000)
        array[y0:y1] = (values + 128).astype(np.uint16)
    array.flush()
    return array


def _rss_bytes() -> int:
    try:
        import psutil

        return int(psutil.Process().memory_info().rss)
    except Exception:
        return 0


def _oracle_error(output: np.ndarray, first: np.ndarray, second: np.ndarray, block_size: int) -> float:
    height, width = first.shape
    maximum = 0.0
    for y0 in range(0, height, block_size):
        y1 = min(height, y0 + block_size)
        for x0 in range(0, width, block_size):
            x1 = min(width, x0 + block_size)
            expected = ((first[y0:y1, x0:x1].astype(np.float32) - 128.0) +
                        (second[y0:y1, x0:x1].astype(np.float32) - 128.0)) / (2.0 * (16384.0 - 128.0))
            maximum = max(maximum, float(np.max(np.abs(output[y0:y1, x0:x1] - expected))))
    return maximum


def run_case(mp: int, *, block_size: int = 512) -> dict:
    shape = _shape_for_mp(mp)
    with tempfile.TemporaryDirectory(prefix=f"raw_stress_{mp}mp_") as temporary:
        root = Path(temporary)
        first_samples = _fill_sensor(root / "first.raw", shape, offset=0)
        second_samples = _fill_sensor(root / "second.raw", shape, offset=400)
        first = RawMosaicFrame.from_samples(
            first_samples,
            bits_per_sample=14,
            cfa_pattern=(1, 0, 0, 1),
            black_level=128,
            white_level=16384,
            source_id=f"synthetic-{mp}-a",
        )
        second = RawMosaicFrame.from_samples(
            second_samples,
            bits_per_sample=14,
            cfa_pattern=(1, 0, 0, 1),
            black_level=128,
            white_level=16384,
            source_id=f"synthetic-{mp}-b",
        )
        rss_before = _rss_bytes()
        started = time.perf_counter()
        output, report = raw_pipeline.fuse_raw_frames_blockwise(
            (first, second), block_size=block_size
        )
        elapsed = time.perf_counter() - started
        rss_after = _rss_bytes()
        error = _oracle_error(output, first_samples, second_samples, block_size)
        result = {
            "megapixels": mp,
            "shape": list(shape),
            "pixels": int(shape[0] * shape[1]),
            "block_size": block_size,
            "elapsed_seconds": elapsed,
            "megapixels_per_second": (shape[0] * shape[1] / 1_000_000.0) / max(elapsed, 1e-9),
            "max_abs_error": error,
            "output_min": report.output_min,
            "output_max": report.output_max,
            "headroom_pixels": report.headroom_pixels,
            "blocks": report.block_count,
            "rss_before_bytes": rss_before,
            "rss_after_bytes": rss_after,
            "resident_output_bytes": int(output.nbytes),
        }
        first_samples.flush()
        second_samples.flush()
        # Windows keeps a memory-mapped file locked until every view is gone.
        del output, first, second, first_samples, second_samples
        return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", default="12,24,50,100")
    parser.add_argument("--block-size", type=int, default=512)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    sizes = [int(item.strip()) for item in str(args.sizes).split(",") if item.strip()]
    results = [run_case(mp, block_size=args.block_size) for mp in sizes]
    payload = {
        "kind": "synthetic_raw_pre_demosaic_stress",
        "backend": "numpy_reference_oracle",
        "results": results,
    }
    text = json.dumps(payload, indent=2)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
