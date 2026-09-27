"""Measure peak resident memory of the demosaic full-frame versus block paths.

VRAM/RAM economy cannot be read off the source: the interesting number is the
peak working set during a call, which depends on the engine's live buffers, the
scratch planes a graph allocates, and the tiling overhead of the block path.
This tool samples the process RSS while the call runs and records the engine's
own telemetry, so the two paths can be compared on the same frame.

The output array is part of the RSS when the caller asks for host memory; that is
deliberate, because it is what an application actually holds.

Example:
    python bench_demosaic_memory.py --backend cpu --methods hamilton --size 12mp
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RESOLUTIONS = {
    "12mp": (3000, 4000),
    "24mp": (4000, 6000),
    "50mp": (6144, 8192),
}


class PeakRssSampler:
    """Sample process RSS while a call runs and keep the peak."""

    def __init__(self, interval_s: float = 0.01):
        self.interval = interval_s
        self.peak_mb = 0.0
        self._stop = threading.Event()
        self._thread = None

    def _rss_mb(self) -> float:
        import psutil

        return psutil.Process(os.getpid()).memory_info().rss / (1024.0 * 1024.0)

    def _run(self) -> None:
        import psutil  # noqa: F401  (keep the import error local to the thread)

        while not self._stop.is_set():
            self.peak_mb = max(self.peak_mb, self._rss_mb())
            time.sleep(self.interval)

    def __enter__(self):
        self.peak_mb = self._rss_mb()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self.peak_mb = max(self.peak_mb, self._rss_mb())
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        return False


def engine_status(api) -> dict:
    getter = getattr(api, "get_memory_status", None)
    if getter is None:
        return {}
    try:
        status = getter(force=True)
    except Exception as exc:  # pragma: no cover - platform dependent
        return {"engine_status_error": repr(exc)}
    if not isinstance(status, dict):
        return {}
    return {
        key: status[key]
        for key in ("resident_bytes", "lifecycle_bytes", "resident_limit", "resident_over_limit")
        if key in status
    }


def tile_working_set_mb(tile: int, halo: int) -> float:
    span = tile + 2 * halo
    return (span * span * 4 + span * span * 12) / (1024.0 * 1024.0)


def synthetic_bayer(height: int, width: int) -> np.ndarray:
    y = np.linspace(-10, 10, height, dtype=np.float32)[:, None]
    x = np.linspace(-10, 10, width, dtype=np.float32)[None, :]
    radius = x**2 + y**2
    bayer = np.zeros((height, width), dtype=np.float32)
    bayer[0::2, 0::2] = np.clip(0.5 + 0.5 * np.cos(radius * 0.1), 0, 1)[0::2, 0::2]
    bayer[0::2, 1::2] = np.clip(0.5 + 0.5 * np.sin(x * 2.0 + y * 2.0), 0, 1)[0::2, 1::2]
    bayer[1::2, 0::2] = np.clip(0.5 + 0.5 * np.sin(x * 2.0 + y * 2.0), 0, 1)[1::2, 0::2]
    bayer[1::2, 1::2] = np.clip(0.5 + 0.5 * np.cos(x * 1.5 - y * 1.5), 0, 1)[1::2, 1::2]
    return bayer


def run_case(api, bayer: np.ndarray, method: str, mode: str, tile: int, halo: int) -> dict:
    cmatrix = np.eye(3, dtype=np.float32)
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
        c10=3,
        c11=2,
        method=method,
        return_gpu=False,
    )

    before = engine_status(api)
    if mode == "full":
        call = lambda: api.demosaic(bayer, **kwargs)  # noqa: E731
    else:

        @api.compute_block(halo=halo, mode="force")
        def tiled(raw):
            return api.demosaic(raw, **kwargs)

        call = lambda: tiled(bayer)  # noqa: E731

    with PeakRssSampler() as sampler:
        started = time.perf_counter()
        output = call()
        elapsed_ms = (time.perf_counter() - started) * 1000.0
    after = engine_status(api)

    return {
        "mode": mode,
        "tile": tile if mode == "block" else None,
        "halo": halo if mode == "block" else None,
        "output_shape": list(np.shape(output)),
        "elapsed_ms": round(elapsed_ms, 3),
        "peak_rss_mb": round(sampler.peak_mb, 2),
        "tile_working_set_mb": round(tile_working_set_mb(tile, halo), 3) if mode == "block" else None,
        "engine_before": before,
        "engine_after": after,
        "engine_resident_delta_mb": round(
            (after.get("resident_bytes", 0) - before.get("resident_bytes", 0)) / (1024.0 * 1024.0), 2
        ),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--backend", default="cpu")
    parser.add_argument("--methods", nargs="+", default=["hamilton"])
    parser.add_argument("--size", choices=sorted(RESOLUTIONS), default="12mp")
    parser.add_argument("--tiles", nargs="+", type=int, default=[512, 1024])
    parser.add_argument("--halo", type=int, default=16)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)

    os.environ["PIXEL_REFINE_AOT_ARCH"] = args.backend
    os.environ["AOT_ARCH"] = args.backend
    import taichi_vision.taichi_aot as api

    height, width = RESOLUTIONS[args.size]
    print(f"generating {width}x{height} ({height * width / 1e6:.2f} MP) synthetic Bayer...")
    bayer = synthetic_bayer(height, width)
    print(f"  host input buffer: {bayer.nbytes / 1e6:.1f} MB")

    report = {"backend": args.backend, "size": args.size, "shape": [height, width], "cases": {}}
    for method in args.methods:
        cases = []
        cases.append(run_case(api, bayer, method, "full", 0, args.halo))
        for tile in args.tiles:
            cases.append(run_case(api, bayer, method, "block", tile, args.halo))
        report["cases"][method] = cases

        print(f"\n=== {method}")
        print(f"  {'mode':<6} {'tile':>6} {'peak RSS MB':>12} {'tile set MB':>12} "
              f"{'engine d MB':>12} {'ms':>10}")
        for case in cases:
            print(
                f"  {case['mode']:<6} {str(case['tile'] or '-'):>6} {case['peak_rss_mb']:>12.2f} "
                f"{str(case['tile_working_set_mb'] or '-'):>12} "
                f"{case['engine_resident_delta_mb']:>12.2f} {case['elapsed_ms']:>10.1f}"
            )

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
