"""Run in separate processes to compare reconstruction-only RSS and latency.

python -m pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.tests.probe_splat_sr_tiles --mode tiled
"""
from __future__ import annotations

import argparse
import json
import tempfile
import threading
import time
from pathlib import Path

import numpy as np
import psutil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("resident", "tiled", "disk"), required=True)
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--frames", type=int, default=3)
    parser.add_argument("--skip-save", action="store_true", help="Reconstruction memory probe without final output I/O")
    args = parser.parse_args()
    from taichi_vision import taichi_aot
    from taichi_vision.taichi_algorithm.buffer_session import BufferSession
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.spatial_splat_runtime import SessionHannAccumulator
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.tiled_accumulator import TiledHannAccumulator, _TileBacking
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.legacy import _save_mfd_compatible_result

    # Initialize the device before the measured baseline, identically in both modes.
    taichi_aot.engine.sync()
    process = psutil.Process()
    baseline_info = process.memory_info()
    baseline = baseline_info.rss
    private_baseline = getattr(baseline_info, "private", None)
    peak = [baseline]
    private_peak = [private_baseline or 0]
    stop = threading.Event()

    def sample():
        while not stop.wait(0.01):
            memory = process.memory_info()
            peak[0] = max(peak[0], memory.rss)
            private_peak[0] = max(private_peak[0], getattr(memory, "private", 0))

    sampler = threading.Thread(target=sample, daemon=True)
    sampler.start()
    started = time.perf_counter()
    output = None
    with tempfile.TemporaryDirectory(prefix="sr_probe_") as directory:
        try:
            shape = (args.height, args.width)
            rng = np.random.default_rng(81)
            reference = rng.uniform(0.1, 0.8, (*shape, 3)).astype(np.float32)
            with BufferSession() as session:
                if args.mode == "resident":
                    accumulator = SessionHannAccumulator(reference, session=session, block_size=512, overlap=0.5)
                else:
                    options = {"backing_factory": _TileBacking} if args.mode == "disk" else {}
                    accumulator = TiledHannAccumulator(reference, session=session, **options)
                confidence = session.own(taichi_aot.upload(np.ones(shape, np.float32)))
                accumulator.add_frame(reference, None, confidence)
                for _ in range(args.frames - 1):
                    support = rng.uniform(0.1, 0.8, (*shape, 3)).astype(np.float32)
                    flow = np.empty((*shape, 2), dtype=np.float32)
                    flow[..., 0], flow[..., 1] = 0.35, -0.23
                    accumulator.add_frame(support, flow, confidence)
                    del support, flow
                output = accumulator.finalize()
                reconstruction_s = time.perf_counter() - started
            save_start = time.perf_counter()
            if not args.skip_save:
                _save_mfd_compatible_result(output, str(Path(directory) / "output.tif"))
            save_s = None if args.skip_save else time.perf_counter() - save_start
        finally:
            if output is not None and hasattr(output, "close"):
                output.close()
            peak[0] = max(peak[0], process.memory_info().rss)
            stop.set()
            sampler.join()
    print(json.dumps({
        "mode": args.mode, "backend": taichi_aot.backend_info(),
        "input_shape": [args.height, args.width, 3], "dtype": "float32",
        "frames": args.frames, "scale": 2, "reconstruction_s": reconstruction_s,
        "save_s": save_s, "rss_baseline_mib": baseline / 1024**2,
        "rss_peak_mib": peak[0] / 1024**2,
        "rss_increase_mib": (peak[0] - baseline) / 1024**2,
        "private_baseline_mib": private_baseline / 1024**2 if private_baseline is not None else None,
        "private_peak_mib": private_peak[0] / 1024**2 if private_baseline is not None else None,
        "save_skipped": args.skip_save,
        "tile_readbacks": getattr(accumulator, "readbacks", None),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
