"""Large synthetic block optical-flow benchmark with known ground truth."""

from __future__ import annotations

import argparse
import gc
import json
import subprocess
import threading
import time
from pathlib import Path

import numpy as np

from taichi_vision import taichi_aot as aot


class VramSampler:
    def __init__(self, interval=0.05):
        self.interval = interval
        self.samples = []
        self._stop = threading.Event()
        self._thread = None

    @staticmethod
    def _read():
        try:
            value = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                text=True,
                timeout=2,
            ).splitlines()[0]
            return int(value.strip())
        except Exception:
            return None

    def __enter__(self):
        self.baseline_mib = self._read()
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self._thread.start()
        return self

    def _sample(self):
        while not self._stop.is_set():
            value = self._read()
            if value is not None:
                self.samples.append(value)
            self._stop.wait(self.interval)

    def __exit__(self, *_args):
        self._stop.set()
        self._thread.join(timeout=3)
        value = self._read()
        if value is not None:
            self.samples.append(value)

    @property
    def peak_mib(self):
        return max(self.samples, default=self.baseline_mib or 0)

    @property
    def delta_mib(self):
        return max(0, self.peak_mib - (self.baseline_mib or 0))


def make_texture(height, width, seed=42):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[:height, :width]
    image = (
        112.0
        + 32.0 * np.sin(x * 0.071)
        + 27.0 * np.cos(y * 0.053)
        + 21.0 * np.sin((x + y) * 0.029)
        + 15.0 * np.cos((x - 2.0 * y) * 0.017)
        + rng.normal(0.0, 9.0, (height, width))
    )
    return np.clip(image, 0.0, 255.0).astype(np.float32)


def known_flow(height, width, scenario):
    y, x = np.mgrid[:height, :width]
    xn = x.astype(np.float32) / max(1, width - 1)
    yn = y.astype(np.float32) / max(1, height - 1)
    if scenario == "translation_small":
        dx = np.full((height, width), 4.0, np.float32)
        dy = np.full((height, width), -3.0, np.float32)
    elif scenario == "translation_large":
        dx = np.full((height, width), 18.0, np.float32)
        dy = np.full((height, width), 11.0, np.float32)
    elif scenario == "parallax":
        depth = 0.5 + 0.28 * np.sin(2.0 * np.pi * xn) * np.cos(2.0 * np.pi * yn)
        depth += 0.22 * (xn > 0.52).astype(np.float32)
        dx = 3.0 + 12.0 * depth + 3.0 * (yn - 0.5)
        dy = -2.0 - 6.0 * depth + 2.0 * (xn - 0.5)
    else:
        raise ValueError(f"unknown scenario: {scenario}")
    return np.ascontiguousarray(np.stack((dx, dy), axis=-1), dtype=np.float32)


def inverse_remap_flow(forward, iterations=8):
    """Solve q = p + F(p), returning D(q) = p - q for remap."""
    h, w = forward.shape[:2]
    qy, qx = np.mgrid[:h, :w]
    px = qx.astype(np.float32)
    py = qy.astype(np.float32)
    for _ in range(iterations):
        ix = np.clip(np.rint(px).astype(np.int32), 0, w - 1)
        iy = np.clip(np.rint(py).astype(np.int32), 0, h - 1)
        px = qx - forward[iy, ix, 0]
        py = qy - forward[iy, ix, 1]
    return np.ascontiguousarray(np.stack((px - qx, py - qy), axis=-1), dtype=np.float32)


def accuracy(flow, truth, margin):
    h, w = truth.shape[:2]
    crop = (slice(margin, h - margin), slice(margin, w - margin))
    delta = flow[crop] - truth[crop]
    epe = np.sqrt(np.sum(delta * delta, axis=2))
    magnitude = np.sqrt(np.sum(truth[crop] * truth[crop], axis=2))
    return {
        "mean_epe_px": float(np.mean(epe)),
        "median_epe_px": float(np.median(epe)),
        "p95_epe_px": float(np.percentile(epe, 95)),
        "bad_1px_pct": float(np.mean(epe > 1.0) * 100.0),
        "relative_epe_pct": float(np.mean(epe / np.maximum(magnitude, 1e-3)) * 100.0),
    }


def timed(label, function):
    with VramSampler() as memory:
        start = time.perf_counter()
        result = function()
        elapsed = time.perf_counter() - start
    return result, {
        "label": label,
        "seconds": elapsed,
        "vram_baseline_mib": memory.baseline_mib,
        "vram_peak_mib": memory.peak_mib,
        "vram_delta_mib": memory.delta_mib,
    }


def run(args):
    output = {
        "shape": [args.height, args.width],
        "megapixels": args.height * args.width / 1e6,
        "mode": "full_frame" if args.disable_blocks else "block",
        "block_size": args.block_size,
        "scenarios": {},
    }
    ref = make_texture(args.height, args.width)
    algorithms = {
        "farneback": lambda p, n: aot.farneback_flow(
            p, n, num_levels=3, num_iters=3, win_size=15, poly_n=5
        ),
        "lucas_kanade": lambda p, n: aot.lucasKanade(
            p, n, maxLevel=2, grid_step=16, winSize=(13, 13)
        ),
        "block_matching": lambda p, n: aot.blockMatching(
            p, n, maxLevel=2, grid_step=16, winSize=(13, 13)
        ),
    }
    aot.set_block_mode(
        not args.disable_blocks,
        size=args.block_size,
        threshold_bytes=0,
        cache_entries=args.cache_entries,
    )

    for scenario in args.scenarios:
        truth = known_flow(args.height, args.width, scenario)
        inverse = inverse_remap_flow(truth)
        comparison, remap_stats = timed(
            "remap_with_flow", lambda: aot.remap_with_flow(ref, inverse, args.height, args.width)
        )
        del inverse
        scenario_result = {"remap": remap_stats, "algorithms": {}}
        aot.engine.clear_block_cache()

        for name, algorithm in algorithms.items():
            flow, cold = timed(name + "_cold", lambda: algorithm(ref, comparison))
            _, warm = timed(name + "_warm", lambda: algorithm(ref, comparison))
            metrics = accuracy(flow, truth, args.margin)
            scenario_result["algorithms"][name] = {
                "accuracy": metrics,
                "cold": cold,
                "warm": warm,
                "cache_speedup": cold["seconds"] / max(warm["seconds"], 1e-9),
            }
            del flow
            gc.collect()
        output["scenarios"][scenario] = scenario_result
        del truth, comparison
        aot.engine.clear_block_cache()
        gc.collect()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="ascii")
    print(json.dumps(output, indent=2))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--height", type=int, default=4000)
    parser.add_argument("--width", type=int, default=5000)
    parser.add_argument("--block-size", type=int, default=512)
    parser.add_argument("--cache-entries", type=int, default=256)
    parser.add_argument("--disable-blocks", action="store_true")
    parser.add_argument("--margin", type=int, default=160)
    parser.add_argument(
        "--scenarios", nargs="+",
        default=["translation_small", "translation_large", "parallax"],
    )
    parser.add_argument(
        "--output", type=Path,
        default=Path("test_algorithm/block_visualization/optical_flow_20mp_benchmark.json"),
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
